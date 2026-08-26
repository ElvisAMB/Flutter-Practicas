# Sistema RAT — Registro de Actividades de Tratamiento

Aplicación web en Django 5.2 para gestionar la matriz RAT exigida por los
**Arts. 38–39 del Reglamento General a la LOPDP** (Ecuador), conforme al
procedimiento interno **PR-PDP-001 v1.0** de una compañía de seguros de fianzas
y crédito.

---

## Inicio rápido

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python manage.py generar_llave        # pegue el resultado en .env
python manage.py migrate
python manage.py inicializar --admin admin --password "Cambiar.2026#Ya"
python manage.py runserver
```

Abra `http://127.0.0.1:8000/`. El administrador deberá cambiar su contraseña en
el primer ingreso.

Para desarrollar en **Visual Studio Code**, ver `docs/DESARROLLO_VSCODE.md`:
el proyecto incluye `.vscode/` con siete configuraciones de depuración y diez
tareas preconfiguradas.

Para Windows Server con IIS, ver `docs/INSTALACION_WINDOWS.md`.

---

## Documentación

| Documento | Contenido |
|---|---|
| `docs/MANUAL_OPERATIVO.md` | Uso del sistema: perfiles, carga del RAT, ciclo de vida, indicadores, bitácora, rutinas periódicas |
| `docs/INSTALACION_WINDOWS.md` | Instalación en Windows / Windows Server, IIS, TLS, endurecimiento, respaldos, tareas programadas |
| `docs/DESARROLLO_VSCODE.md` | Ejecutar, depurar y probar el proyecto desde Visual Studio Code |
| `.env.example` | Todas las variables de configuración, comentadas |

---

## Estructura

```
config/settings/   base.py · dev.py · prod.py
apps/
  core/            cifrado, campos, modelos base, mixins de acceso, comandos
  accounts/        usuarios, perfiles, permisos, backend con bloqueo
  auditoria/       bitácora encadenada, middleware, señales
  catalogos/       11 catálogos maestros con CRUD parametrizado
  rat/             matriz RAT (campos 3.1–3.20), estados, brechas, entrevistas
  indicadores/     tablero de gestión (Art. 36 RLOPDP)
  plantillas/      plantillas reutilizables y extensibles
templates/  static/  deploy/  docs/
```

---

## Decisiones de diseño que conviene conocer antes de modificar el código

### 1. El cifrado es selectivo, y eso es deliberado

Se cifra con **AES-256-GCM** lo que es dato personal: nombres, correos,
documentos, teléfonos, observaciones, respuestas de entrevistas, detalle de la
bitácora, contenido de documentos generados.

**No** se cifran los metadatos de tratamiento: código y nombre de la actividad,
área, estado, fechas, tipo de acción de bitácora.

El motivo es que el cifrado seguro usa nonce aleatorio: el mismo texto produce
un resultado distinto en cada fila, de modo que sobre un campo cifrado el motor
**no puede** filtrar por igualdad, buscar por coincidencia parcial, ordenar ni
agrupar. Cifrarlo todo convertiría cada consulta en un recorrido completo de la
tabla con descifrado en Python. Una fila del RAT, además, no identifica a
ninguna persona: describe un tratamiento.

Para búsquedas de igualdad sobre campos cifrados existen **índices ciegos**
(HMAC-SHA256 determinista en columna hermana indexada). Permiten `=` a
velocidad de índice; no permiten `LIKE` ni rangos. Los campos cifrados
**rechazan** los lookups imposibles con un `FieldError` explicativo en lugar de
devolver cero resultados en silencio.

### 2. La bitácora es append-only y encadenada

`Evento.save()` sobre un registro existente lanza `PermissionError`;
`Evento.delete()` también. Cada fila guarda
`SHA-256(hash_anterior || contenido canónico)`. Alterar o borrar una fila
directamente en la base rompe la cadena y `manage.py verificar_bitacora` lo
detecta.

Esto **detecta** manipulación, no la impide: quien tenga privilegios sobre el
motor puede borrar la tabla entera. Lo que no puede hacer es alterar un registro
y que la verificación siga dando correcta. Por eso la verificación debe
ejecutarse periódicamente y por alguien distinto de quien administra el servidor.

La tabla usa `BigAutoField` en lugar de UUID como PK, porque es la única que
crece a millones de filas y un índice B-Tree sobre entero es sustancialmente más
compacto.

### 3. El borrado es lógico

Ninguna entidad de negocio se elimina físicamente. El procedimiento exige
conservar las filas cesadas con fecha de cese (campo 3.20, estado *Histórico*),
y el Art. 10 lit. k LOPDP exige poder demostrar la gestión pasada.

Consecuencia práctica: si sobrescribe el manager `objects` de un modelo que
hereda de `ModeloBase`, herede de `SoftDeleteQuerySet` y use
`SoftDeleteManager.from_queryset(...)`. En caso contrario las filas dadas de baja
volverán a aparecer en los listados.

### 4. Autorización sobre `auth.Permission`, no sobre un sistema propio

Un `Perfil` envuelve un `auth.Group`. Así `user.has_perm()`,
`@permission_required` y el admin de Django siguen funcionando sin adaptadores.

El perfil **AUDITOR** tiene doble candado: `Usuario.has_perm()` niega todo
permiso que no comience en `view_`/`ver_`, y `BloquearAuditorMixin` rechaza
cualquier método HTTP que no sea de lectura. Es redundante a propósito: una
vista mal declarada no debe abrir un hueco.

### 5. Las reglas normativas viven en el modelo, no en el formulario

`ActividadTratamiento.clean()` impide guardar combinaciones jurídicamente
inconsistentes (scoring con efectos jurídicos declarando que no requiere EIPD;
publicar como vigente con EIPD requerida sin informe; transferencia
internacional sin mecanismo habilitante). Estar en el modelo significa que
también aplican desde el shell, desde un script de carga o desde el admin.

### 6. CRUD de catálogos parametrizado

`apps/catalogos/views.py` define un diccionario `CATALOGOS` y tres vistas
genéricas. Agregar un catálogo nuevo son cuatro líneas, no un módulo.

### 7. Sin CDNs externos

La aplicación sirve todos sus estáticos localmente. Cargar recursos desde un
tercero implicaría que ese tercero observa la IP y el user-agent de cada usuario
en cada carga de página: una comunicación de datos que habría que declarar en el
propio RAT. Ejecute `deploy/descargar_assets.ps1` (o `.sh`) una vez.

---

## Comandos de gestión

| Comando | Uso |
|---|---|
| `generar_llave` | Genera llaves AES-256 y de índice ciego para `.env` |
| `rotar_llaves [--simular]` | Re-cifra todo con la llave activa (rotación sin downtime) |
| `inicializar [--admin U --password P]` | Perfiles fijos, catálogos base y 11 plantillas |
| `verificar_bitacora` | Verifica la cadena hash; sale con código 1 si hay ruptura |
| `purgar_bitacora --dias N [--confirmar]` | Archiva a CSV con hash y purga según retención |

---

## Pruebas

```bash
python manage.py test apps
```

36 pruebas cubren: cifrado y detección de manipulación, aislamiento por AAD,
índices ciegos, bloqueo de lookups imposibles, inmutabilidad y encadenamiento de
la bitácora, reglas normativas del RAT, transiciones de estado, borrado lógico y
control de acceso por perfil.

---

## Portabilidad de base de datos

Solo se usa el ORM; no hay SQL específico de motor ni dependencia de `pgcrypto`,
*Always Encrypted* u otras extensiones. Cambiar de motor requiere ajustar
`DB_ENGINE` y variables asociadas, instalar el controlador y migrar.

Probado con SQLite (desarrollo). Para producción se recomienda PostgreSQL o SQL
Server; ver `docs/INSTALACION_WINDOWS.md` §4.

---

## Limitaciones conocidas

- **MFA**: el modelo contempla el campo `mfa_habilitado`, pero la verificación
  del segundo factor no está implementada. Se recomienda integrar con el
  proveedor de identidad corporativo (Entra ID vía SAML/OIDC) antes de exponer
  el sistema fuera de la red interna.
- **Reporte al Registro Nacional**: el sistema marca el pendiente y recuerda el
  término de 10 días, pero el envío a la SPDP es manual.
- **Exportación**: CSV. No hay generación de Excel ni PDF con formato oficial.
- **Caché**: `LocMemCache` por defecto no se comparte entre procesos. Con más de
  una instancia, configure Redis o los indicadores serán inconsistentes entre
  recargas.
- Los indicadores miden **completitud documental**, no corrección jurídica.

---

*Las citas normativas corresponden a la LOPDP (R.O. Supl. 459, 2021) y su
Reglamento General (Decreto 904, 2023). La SPDP emite normativa complementaria
de forma continua: verifique resoluciones vigentes antes de cada revisión anual.*
