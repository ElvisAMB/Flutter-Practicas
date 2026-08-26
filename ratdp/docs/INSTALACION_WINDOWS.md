# Guía de instalación y publicación — Windows y Windows Server

**Sistema RAT** — Registro de Actividades de Tratamiento de Datos Personales

| | |
|---|---|
| Documento | INS-RAT-001 |
| Versión | 1.0 |
| Dirigido a | Administradores de TI, Seguridad de la Información |
| Alcance | Windows 10/11 (desarrollo y pruebas) · Windows Server 2019/2022 (producción) |

---

## 1. Arquitectura de despliegue

```
   Internet / Red corporativa
             │  HTTPS 443
             ▼
   ┌───────────────────────┐
   │  IIS 10  (proxy)      │   TLS, cabeceras de seguridad, filtrado
   │  + ARR + URL Rewrite  │   (opcional: WAF corporativo delante)
   └──────────┬────────────┘
              │  HTTP 127.0.0.1:8000   ← nunca expuesto a la red
   ┌──────────▼────────────┐
   │  Waitress (WSGI)      │   Servicio de Windows (NSSM)
   │  Django 5.2           │   Cuenta gMSA o cuenta de servicio dedicada
   └──────────┬────────────┘
              │  TCP cifrado
   ┌──────────▼────────────┐
   │  Motor de BD          │   PostgreSQL / SQL Server / MySQL / Oracle
   │  + TDE + respaldos    │
   └───────────────────────┘
```

**Por qué IIS delante y no Waitress directo.** Waitress es un servidor WSGI sólido, pero no gestiona TLS, no aplica cabeceras de seguridad ni limita tamaños de petición de forma granular. IIS actúa como terminador TLS y punto de aplicación de política. Waitress escucha **solo en loopback**: no debe ser alcanzable desde la red.

**Por qué no `runserver`.** El servidor de desarrollo de Django es monohilo, no valida cabeceras y su propia documentación advierte que no ha pasado auditorías de seguridad. Usarlo en producción es una no conformidad.

---

## 2. Requisitos previos

| Componente | Versión | Nota |
|---|---|---|
| Windows Server | 2019 o 2022 | 2016 funciona pero su soporte extendido termina antes |
| Python | 3.11 o 3.12 | Instalar **para todos los usuarios**, marcar «Add to PATH» |
| IIS | 10 | Con ARR 3.0 y URL Rewrite 2.1 |
| NSSM | 2.24+ | Para ejecutar Waitress como servicio |
| Motor de BD | Según elección | Ver §4 |
| Certificado TLS | — | De CA pública o CA interna de la organización |

**Dimensionamiento orientativo.** El RAT es un inventario: incluso una compañía grande registra cientos de filas, no millones. Lo que crece es la bitácora. Para 50 usuarios concurrentes y 5 años de bitácora: 4 vCPU, 8 GB RAM, 100 GB de disco en el servidor de aplicación; el motor de base de datos según estándar corporativo.

---

## 3. Instalación de la aplicación

### 3.1 Estructura de directorios

```powershell
New-Item -ItemType Directory -Force -Path C:\ratdp, C:\ratdp\logs, C:\ratdp\media, C:\ratdp\archivo, C:\ratdp\respaldos
```

Copie el código fuente en `C:\ratdp\app`.

### 3.2 Entorno virtual y dependencias

```powershell
cd C:\ratdp\app
python -m venv C:\ratdp\venv
C:\ratdp\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

# Controlador del motor elegido (descomente uno):
# pip install "psycopg[binary]"     # PostgreSQL
# pip install mssql-django          # SQL Server (requiere ODBC Driver 18)
# pip install mysqlclient           # MySQL / MariaDB
# pip install oracledb              # Oracle

pip install waitress
```

### 3.3 Recursos estáticos

La aplicación **no enlaza a ningún CDN externo**. Cargar recursos desde un tercero implicaría que ese tercero observa la IP y el user-agent de cada usuario en cada carga de página — una comunicación de datos no declarada en el RAT, y una dependencia de internet innecesaria en una red interna.

```powershell
powershell -ExecutionPolicy Bypass -File C:\ratdp\app\deploy\descargar_assets.ps1
```

Ejecútelo desde una máquina con internet y copie los archivos resultantes si el servidor está aislado. Verifique los hashes SHA-256 contra los publicados por el proyecto Bootstrap.

---

## 4. Base de datos

La aplicación usa exclusivamente el ORM de Django y **no contiene SQL específico de motor**. Cambiar de motor requiere ajustar variables de entorno, instalar el controlador y migrar. No hay dependencias de `pgcrypto`, `Always Encrypted` ni funciones propietarias.

### 4.1 PostgreSQL (recomendado)

```sql
CREATE DATABASE ratdp ENCODING 'UTF8' LC_COLLATE 'es_EC.UTF-8' LC_CTYPE 'es_EC.UTF-8' TEMPLATE template0;
CREATE USER ratdp_app WITH PASSWORD '<contraseña larga y aleatoria>';
GRANT CONNECT ON DATABASE ratdp TO ratdp_app;
\c ratdp
GRANT USAGE, CREATE ON SCHEMA public TO ratdp_app;
```

En `pg_hba.conf` exija `scram-sha-256` y `hostssl`. **No** conceda `SUPERUSER` a `ratdp_app`.

### 4.2 SQL Server

```sql
CREATE DATABASE ratdp COLLATE Latin1_General_CI_AI;
GO
CREATE LOGIN ratdp_app WITH PASSWORD = '<contraseña larga y aleatoria>';
GO
USE ratdp;
CREATE USER ratdp_app FOR LOGIN ratdp_app;
ALTER ROLE db_owner ADD MEMBER ratdp_app;   -- reducir a db_datareader/db_datawriter tras migrar
GO
```

Variables correspondientes en `.env`:

```
DB_ENGINE=mssql
DB_PORT=1433
DB_OPTIONS={"driver":"ODBC Driver 18 for SQL Server","extra_params":"Encrypt=yes;TrustServerCertificate=no"}
```

> Tras aplicar las migraciones, **reduzca los privilegios** de la cuenta de aplicación a lectura y escritura de datos. La cuenta que ejecuta el servicio no necesita poder alterar el esquema en operación normal, y con privilegios reducidos una inyección exitosa no puede modificar la estructura ni eliminar la tabla de bitácora.

### 4.3 Cifrado a nivel de motor (TDE) — complementario, no alternativo

Active TDE (SQL Server Enterprise) o cifrado de volumen con BitLocker donde no haya TDE. **TDE y el cifrado de aplicación resuelven amenazas distintas**:

| Amenaza | TDE / BitLocker | Cifrado de aplicación |
|---|---|---|
| Robo del disco o del archivo de respaldo | Protege | Protege |
| Copia del `.bak` a otro servidor | Protege | Protege |
| Consulta directa con credenciales válidas de BD | **No protege** | Protege |
| DBA curioso leyendo tablas | **No protege** | Protege |

Con TDE, cualquiera que se conecte legítimamente ve los datos en claro: el descifrado es transparente. Por eso la aplicación cifra los campos con datos personales en su propia capa. Use ambos.

### 4.4 Migraciones

```powershell
cd C:\ratdp\app
C:\ratdp\venv\Scripts\python.exe manage.py migrate
C:\ratdp\venv\Scripts\python.exe manage.py inicializar --admin dpd.admin --password "<contraseña temporal>"
C:\ratdp\venv\Scripts\python.exe manage.py collectstatic --noinput
```

El administrador creado deberá cambiar su contraseña en el primer ingreso (control forzado por la aplicación).

---

## 5. Configuración: archivo `.env`

```powershell
Copy-Item C:\ratdp\app\.env.example C:\ratdp\app\.env
notepad C:\ratdp\app\.env
```

Genere los secretos:

```powershell
C:\ratdp\venv\Scripts\python.exe -c "import secrets;print(secrets.token_urlsafe(64))"   # DJANGO_SECRET_KEY
C:\ratdp\venv\Scripts\python.exe manage.py generar_llave                                # DP_ENC_KEYS y DP_INDEX_KEY
```

Restrinja el acceso al archivo — es el punto más sensible de toda la instalación:

```powershell
$acl = Get-Acl C:\ratdp\app\.env
$acl.SetAccessRuleProtection($true, $false)   # romper herencia
$acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) | Out-Null }
$acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule("BUILTIN\Administrators","FullControl","Allow")))
$acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule("$env:COMPUTERNAME\svc_ratdp","Read","Allow")))
Set-Acl C:\ratdp\app\.env $acl
```

### 5.1 Custodia de las llaves de cifrado — leer completo

Esto merece más atención que cualquier otro paso.

1. **Sin las llaves, los datos cifrados son irrecuperables.** No existe recuperación; es exactamente el objetivo del cifrado. Un respaldo de base de datos sin las llaves es papel.
2. **Respalde las llaves en un lugar distinto al de los respaldos de base de datos.** Si el mismo atacante obtiene ambos, el cifrado no aportó nada. Custodia recomendada: sobre sellado en caja fuerte, o Azure Key Vault / HSM corporativo.
3. **`DP_INDEX_KEY` no puede rotarse** sin recalcular todos los índices ciegos. Cambiarla deja sin resultados la búsqueda de usuarios por correo y documento.
4. **`DP_ENC_KEYS` sí puede rotarse** sin downtime: agregue una llave nueva al conjunto, suba `DP_ENC_ACTIVE_KEY`, ejecute `manage.py rotar_llaves` y **solo entonces** retire la llave antigua. Retirarla antes vuelve ilegibles los registros aún no re-cifrados.
5. Registre en el propio RAT quién tiene acceso a las llaves. Es una medida de seguridad del campo 3.18.

Alternativa a texto plano en Windows Server: cifrar el `.env` con DPAPI a nivel de máquina y descifrarlo en el arranque del servicio. Reduce la exposición ante copia del disco, no ante compromiso del servidor en ejecución.

---

## 6. Servicio de aplicación (Waitress + NSSM)

### 6.1 Cuenta de servicio

Cree una cuenta dedicada (`svc_ratdp`) o, preferentemente, una **gMSA** en dominio. Requisitos:

- **Sin** derecho de inicio de sesión interactivo (`Deny log on locally`).
- **Sin** pertenencia a Administradores locales.
- Contraseña que no expire, o gMSA con rotación automática.
- Permisos de escritura únicamente en `C:\ratdp\logs`, `C:\ratdp\media` y `C:\ratdp\archivo`.

Ejecutar la aplicación como `LocalSystem` es cómodo y elimina la mayor parte de la contención de un compromiso: no lo haga.

### 6.2 Script de arranque

`C:\ratdp\app\deploy\servidor.py`:

```python
import os
from pathlib import Path
from waitress import serve

BASE = Path(__file__).resolve().parent.parent
for linea in (BASE / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in linea and not linea.lstrip().startswith("#"):
        k, v = linea.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

from config.wsgi import application

serve(
    application,
    host="127.0.0.1",          # solo loopback: IIS es el único cliente
    port=8000,
    threads=int(os.environ.get("WAITRESS_THREADS", "12")),
    connection_limit=200,
    channel_timeout=120,
    ident="",                  # no anunciar el servidor en las respuestas
    url_scheme="https",        # coherente con SECURE_PROXY_SSL_HEADER
)
```

### 6.3 Registro del servicio

```powershell
nssm install RATDP "C:\ratdp\venv\Scripts\python.exe" "C:\ratdp\app\deploy\servidor.py"
nssm set RATDP AppDirectory C:\ratdp\app
nssm set RATDP DisplayName "Sistema RAT - Protección de Datos"
nssm set RATDP Start SERVICE_AUTO_START
nssm set RATDP AppStdout C:\ratdp\logs\servicio.out.log
nssm set RATDP AppStderr C:\ratdp\logs\servicio.err.log
nssm set RATDP AppRotateFiles 1
nssm set RATDP AppRotateBytes 20971520
nssm set RATDP ObjectName ".\svc_ratdp" "<contraseña>"
nssm set RATDP AppExit Default Restart
nssm start RATDP
```

Verificación: `Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing` debe responder con una redirección al inicio de sesión.

---

## 7. Publicación con IIS

### 7.1 Roles y módulos

```powershell
Install-WindowsFeature Web-Server, Web-Http-Redirect, Web-Filtering, Web-Windows-Auth -IncludeManagementTools
```

Instale además **Application Request Routing 3.0** y **URL Rewrite 2.1**. En la consola de IIS, nivel servidor → *Application Request Routing Cache* → *Server Proxy Settings* → habilitar proxy y **desactivar** «Reverse rewrite host in response headers».

### 7.2 Sitio y `web.config`

Cree un sitio apuntando a `C:\ratdp\site` (carpeta vacía, solo contiene el `web.config`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="ForzarHTTPS" stopProcessing="true">
          <match url="(.*)" />
          <conditions><add input="{HTTPS}" pattern="off" /></conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
        <rule name="ProxyDjango" stopProcessing="true">
          <match url="(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:8000/{R:1}" />
          <serverVariables>
            <set name="HTTP_X_FORWARDED_PROTO" value="https" />
            <set name="HTTP_X_FORWARDED_FOR"   value="{REMOTE_ADDR}" />
          </serverVariables>
        </rule>
      </rules>
    </rewrite>

    <httpProtocol>
      <customHeaders>
        <remove name="X-Powered-By" />
        <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains; preload" />
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="DENY" />
        <add name="Referrer-Policy" value="same-origin" />
        <add name="Permissions-Policy" value="geolocation=(), camera=(), microphone=(), payment=()" />
        <add name="Content-Security-Policy"
             value="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'" />
      </customHeaders>
    </httpProtocol>

    <security>
      <requestFiltering removeServerHeader="true">
        <requestLimits maxAllowedContentLength="10485760" />   <!-- 10 MB -->
        <verbs allowUnlisted="false">
          <add verb="GET" allowed="true" /><add verb="POST" allowed="true" />
          <add verb="HEAD" allowed="true" />
        </verbs>
      </requestFiltering>
    </security>

    <httpErrors errorMode="Custom" existingResponse="PassThrough" />
  </system.webServer>
</configuration>
```

La CSP anterior es estricta y funciona porque la aplicación no usa scripts en línea ni CDNs. Si en el futuro agrega analítica o recursos externos, **revise antes si esa incorporación no constituye una comunicación de datos que deba declararse en el RAT**.

Debe permitirse la reescritura de variables de servidor: IIS → *Configuration Editor* → `system.webServer/rewrite/allowedServerVariables` → agregar `HTTP_X_FORWARDED_PROTO` y `HTTP_X_FORWARDED_FOR`.

### 7.3 TLS

- Certificado de CA pública (si es accesible desde internet) o CA interna (si es intranet).
- **Solo TLS 1.2 y 1.3.** Deshabilite SSL 3.0, TLS 1.0 y 1.1 en `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols`. La herramienta *IIS Crypto* de Nartac automatiza esto de forma fiable.
- Suites con *forward secrecy* (ECDHE) únicamente.
- Programe la renovación con alerta a 30 días. Un certificado vencido es la causa más común de indisponibilidad no planificada.

### 7.4 Ruta del panel de administración de Django

El panel `/gestion-django/` de Django no es necesario para operar el sistema: toda la gestión se hace desde la interfaz propia. Recomendación: **deshabilitarlo en producción** comentando su línea en `config/urls.py`, o restringirlo por IP:

```xml
<rule name="BloquearAdminExterno" stopProcessing="true">
  <match url="^gestion-django" />
  <conditions logicalGrouping="MatchAll">
    <add input="{REMOTE_ADDR}" pattern="^10\.0\.1\." negate="true" />
  </conditions>
  <action type="CustomResponse" statusCode="404" />
</rule>
```

Si lo conserva, cambie la ruta a un valor no adivinable mediante `ADMIN_URL` en settings.

---

## 8. Endurecimiento del servidor

### 8.1 Firewall

```powershell
New-NetFirewallRule -DisplayName "RATDP HTTPS entrante" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "RATDP bloquear 8000 externo" -Direction Inbound -Protocol TCP -LocalPort 8000 -RemoteAddress Any -Action Block
```

Waitress ya escucha solo en loopback; la regla es defensa en profundidad ante un cambio de configuración accidental.

### 8.2 Controles de sistema

- Desinstale roles y características no usados. Un servidor de aplicación no necesita SMB expuesto ni servicios de impresión.
- Windows Update automático con ventana de mantenimiento definida.
- Antimalware con **exclusión de rendimiento** para `C:\ratdp\logs` y el directorio de datos del motor de base de datos (no exclusión de escaneo bajo demanda).
- Auditoría de Windows habilitada para inicios de sesión y cambios de directiva; reenvío de eventos al SIEM corporativo.
- Deshabilite la enumeración anónima y NTLMv1.

### 8.3 Separación de responsabilidades

Quien administra el servidor **no debería** ser simultáneamente Administrador del sistema RAT. Si la misma persona controla el servidor y la aplicación, puede alterar la base de datos y también la bitácora que lo evidenciaría. La cadena hash detecta esa alteración precisamente porque asume que puede ocurrir — pero la detección solo sirve si quien verifica es alguien distinto. Asigne la verificación mensual a Auditoría Interna.

---

## 9. Respaldos y continuidad

| Elemento | Frecuencia | Retención | Nota |
|---|---|---|---|
| Base de datos completa | Diaria | 30 días | Cifrada en reposo |
| Registro de transacciones | Cada 15 min | 7 días | Permite recuperación puntual |
| `C:\ratdp\media` | Diaria | 30 días | |
| `C:\ratdp\archivo` (bitácora purgada) | Al generarse | 7 años | Evidencia normativa |
| **Llaves de cifrado** | Al rotar | Permanente | **Custodia separada de todo lo anterior** |
| `.env` (sin llaves) | Al cambiar | 1 año | |

**Pruebe la restauración trimestralmente.** Un respaldo no verificado es una hipótesis. La prueba debe incluir descifrar al menos un registro cifrado, porque es donde falla la restauración cuando las llaves no se respaldaron correctamente.

---

## 10. Tareas programadas

### 10.1 Verificación mensual de la bitácora

```powershell
$accion = New-ScheduledTaskAction `
  -Execute "C:\ratdp\venv\Scripts\python.exe" `
  -Argument "manage.py verificar_bitacora" `
  -WorkingDirectory "C:\ratdp\app"

$disparador = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 3am

Register-ScheduledTask -TaskName "RATDP-VerificarBitacora" `
  -Action $accion -Trigger $disparador -User "svc_ratdp" -Password "<contraseña>" `
  -Description "Verifica la integridad de la cadena hash de la bitácora del sistema RAT."
```

Configure una alerta si la tarea termina con código distinto de cero: significa ruptura de la cadena y debe escalarse de inmediato al DPD y a Seguridad de la Información.

### 10.2 Purga anual conforme a retención

```powershell
C:\ratdp\venv\Scripts\python.exe manage.py purgar_bitacora --dias 2555             # simulación
C:\ratdp\venv\Scripts\python.exe manage.py purgar_bitacora --dias 2555 --confirmar # ejecución
```

Sin `--confirmar` solo informa. Genera un CSV con hash SHA-256 antes de eliminar.

### 10.3 Rotación de llaves (anual o ante incidente)

```powershell
# 1. Generar la llave nueva y agregarla al conjunto existente en .env, p. ej.:
#    DP_ENC_KEYS={"1":"<antigua>","2":"<nueva>"}
#    DP_ENC_ACTIVE_KEY=2
# 2. Reiniciar el servicio
Restart-Service RATDP
# 3. Re-cifrar (simular primero)
C:\ratdp\venv\Scripts\python.exe manage.py rotar_llaves --simular
C:\ratdp\venv\Scripts\python.exe manage.py rotar_llaves
# 4. Solo tras finalizar sin errores, retirar la llave "1" de DP_ENC_KEYS
```

---

## 11. Verificación posterior a la instalación

Recorra esta lista antes de declarar el sistema en producción:

- [ ] `https://rat.empresa.com` responde y redirige `http://` a `https://`.
- [ ] El puerto 8000 **no** es alcanzable desde otra máquina de la red.
- [ ] Ingreso con el administrador inicial fuerza el cambio de contraseña.
- [ ] Cinco intentos fallidos bloquean la cuenta 15 minutos.
- [ ] Un usuario con perfil Auditor no ve botones de edición y recibe 403 al forzar una URL de edición.
- [ ] `manage.py check --deploy` no reporta advertencias críticas.
- [ ] Las cabeceras de seguridad aparecen en la respuesta (verifique con las herramientas de desarrollo del navegador o SSL Labs).
- [ ] El tablero de indicadores carga y muestra las actividades cargadas.
- [ ] `manage.py verificar_bitacora` responde «integridad correcta».
- [ ] Se generó y **guardó fuera del servidor** una copia de las llaves de cifrado.
- [ ] Se realizó y **verificó** una restauración de respaldo completa.
- [ ] Los eventos de Windows se reenvían al SIEM.
- [ ] Existe registro de quién tiene acceso a las llaves y al `.env`.

```powershell
C:\ratdp\venv\Scripts\python.exe manage.py check --deploy --settings=config.settings.prod
```

---

## 12. Diagnóstico de problemas frecuentes

| Síntoma | Causa probable | Acción |
|---|---|---|
| Error 502 en IIS | Servicio RATDP detenido | `Get-Service RATDP`; revisar `C:\ratdp\logs\servicio.err.log` |
| «DP_ENC_KEYS y DP_INDEX_KEY son obligatorios» | `.env` no leído o vacío | Verificar ruta, codificación (UTF-8 sin BOM) y permisos de `svc_ratdp` |
| CSRF verification failed | `CSRF_TRUSTED_ORIGINS` incompleto | Agregar el origen `https://…` exacto |
| Redirección infinita | Falta `HTTP_X_FORWARDED_PROTO` en IIS | Habilitar la variable en `allowedServerVariables` |
| Estilos sin aplicar | `collectstatic` no ejecutado o Bootstrap no descargado | Reejecutar §3.3 y `collectstatic` |
| `CryptoError: llave no está en el keyring` | Se retiró una llave antes de completar la rotación | Restaurar la llave al conjunto y reejecutar `rotar_llaves` |
| Búsqueda de usuario por correo sin resultados | Búsqueda parcial sobre campo cifrado | La búsqueda por correo es exacta; ver Manual Operativo §9 |
| Indicadores inconsistentes entre recargas | Varias instancias con caché local | Configurar Redis como caché compartida |
| Lentitud creciente en la bitácora | Tabla sin purgar | Ejecutar §10.2 y verificar índices del motor |

---

## 13. Consideraciones para publicación en internet

Si el sistema se expone fuera de la red corporativa, además de todo lo anterior:

1. **WAF delante de IIS** (Azure Front Door, Cloudflare o appliance corporativo) con reglas OWASP.
2. **MFA obligatorio.** El modelo de usuario ya contempla el campo; integre con el proveedor de identidad corporativo (Entra ID vía SAML/OIDC) en lugar de gestionar un segundo factor propio.
3. **Restricción geográfica y de rango de IP** si el acceso legítimo proviene solo de Ecuador y de sedes conocidas.
4. **Alerta ante patrones anómalos**: exportaciones fuera de horario, múltiples accesos denegados, ingresos desde ubicaciones nuevas. La bitácora ya registra estos eventos; falta conectarla al SIEM.
5. **Evalúe si es necesario.** El RAT es un instrumento interno cuyo destinatario natural son el DPD, los dueños de proceso y la SPDP cuando lo requiera. Publicarlo en internet amplía la superficie de ataque a cambio de una conveniencia que una VPN corporativa suele resolver igual de bien. La decisión debería documentarse con su propio análisis de riesgo (Art. 40 LOPDP).

---

## 14. Instalación en Windows 10/11 para desarrollo

```powershell
git clone <repositorio> C:\dev\ratdp
cd C:\dev\ratdp
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py generar_llave    # pegar el resultado en .env
python manage.py migrate
python manage.py inicializar --admin admin --password "Local.2026#Dev"
python manage.py runserver
```

Con `DJANGO_SETTINGS_MODULE=config.settings.dev`, si no define llaves se generan al vuelo en cada arranque — cómodo para probar, pero **los datos cifrados de la ejecución anterior quedan ilegibles**. Para desarrollo continuado, fije las llaves en `.env`.

**No use la configuración de desarrollo en un servidor accesible por terceros.** `DEBUG=True` expone trazas con fragmentos de configuración y consultas.

---

*Documento de referencia interna. Las citas normativas corresponden a la LOPDP (2021) y su Reglamento General (Decreto 904, 2023).*
