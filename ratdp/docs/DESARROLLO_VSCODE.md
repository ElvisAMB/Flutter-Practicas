# Ejecutar el proyecto en Visual Studio Code

Guía para levantar, depurar y probar el Sistema RAT desde VS Code, en Windows,
macOS o Linux.

---

## 1. Preparación (una sola vez)

### 1.1 Descomprimir y abrir

Descomprima `sistema-rat-django.tar.gz` y abra **la carpeta `ratdp`** con
`Archivo → Abrir carpeta`.

> Abra la carpeta del proyecto, no la carpeta que la contiene. Si abre el nivel
> superior, `manage.py` no queda en la raíz del workspace y todas las rutas de
> `launch.json` fallan.

### 1.2 Instalar las extensiones recomendadas

Al abrir el proyecto, VS Code ofrecerá instalar las extensiones de
`.vscode/extensions.json`. Acepte, o abra la vista de Extensiones y filtre por
`@recommended`.

Las dos imprescindibles son **Python** (Microsoft) y **Django** (Baptiste
Darthenay). Sin la segunda, el editor marca como error cada etiqueta
`{% ... %}` de las plantillas.

### 1.3 Crear el entorno virtual

Abra el terminal integrado (`Ctrl+Ñ` o `Ctrl+` `` ` ``) y ejecute:

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea el script de activación:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 1.4 Seleccionar el intérprete

`Ctrl+Shift+P` → **Python: Select Interpreter** → elija el que muestra
`.venv` y la ruta del proyecto.

Este paso es el que más problemas causa cuando se omite: sin él, VS Code usa el
Python del sistema, no encuentra Django y marca en rojo todos los imports aunque
el proyecto funcione en el terminal.

Verifique en la barra de estado inferior que aparece `Python 3.12 ('.venv')`.

### 1.5 Instalar dependencias y configurar

`Ctrl+Shift+P` → **Tasks: Run Task** → **RAT: instalar dependencias**

Luego cree el archivo de configuración:

```powershell
Copy-Item .env.example .env      # Windows
# cp .env.example .env           # macOS / Linux
```

Genere las llaves de cifrado con la tarea **RAT: generar llaves de cifrado** y
pegue las tres líneas resultantes en `.env`:

```
DP_ENC_KEYS={"1": "..."}
DP_ENC_ACTIVE_KEY=1
DP_INDEX_KEY=...
```

Añada también, para desarrollo local:
```
DJANGO_SETTINGS_MODULE=config.settings.dev
```

> En desarrollo, si omite las llaves el sistema genera unas nuevas en cada
> arranque — cómodo para una prueba rápida, pero los datos cifrados de la
> sesión anterior quedan ilegibles. Fíjelas en `.env` si va a trabajar varios
> días sobre los mismos datos.

### 1.6 Base de datos y datos iniciales

`Ctrl+Shift+P` → **Tasks: Run Task** → **RAT: puesta a punto completa**

Esa tarea encadena: instalar dependencias → migrar → cargar catálogos y
plantillas → ejecutar las 36 pruebas. Si termina en `OK`, el entorno está listo.

Cree su usuario administrador:

```powershell
python manage.py inicializar --admin admin --password "Local.2026#Dev"
```

---

## 2. Ejecutar

Pulse **F5** o abra el panel *Ejecutar y depurar* (`Ctrl+Shift+D`). Hay siete
configuraciones:

| Configuración | Cuándo usarla |
|---|---|
| **Django: runserver** | Uso normal. Recarga al guardar. |
| **Django: runserver (sin recarga)** | Al depurar señales o el arranque: el recargador reinicia el proceso y pierde los puntos de interrupción. |
| **Django: pruebas (todas)** | Las 36 pruebas con depurador. |
| **Django: pruebas (archivo actual)** | Solo las del archivo abierto. |
| **Django: shell** | Consola interactiva con el ORM cargado. |
| **Django: comando de gestión…** | Pide el nombre del comando (`verificar_bitacora`, `rotar_llaves`, `purgar_bitacora`…). |
| **Waitress: simular producción** | Reproduce problemas que solo aparecen con `DEBUG=False`. Requiere las variables de producción en `.env`. |

Abra `http://127.0.0.1:8000/`. Ingrese con el administrador; el sistema le
exigirá cambiar la contraseña.

Para detener: `Shift+F5` o el cuadrado rojo de la barra de depuración.

---

## 3. Depurar

Los puntos de interrupción (clic en el margen izquierdo, o `F9`) funcionan en
vistas, modelos, formularios, señales y comandos de gestión.

`justMyCode` está en `false` en todas las configuraciones, de modo que también
puede entrar en el código de Django. Es lo que necesita para entender, por
ejemplo, por qué un `QuerySet` genera el SQL que genera.

Lugares útiles donde poner un punto de interrupción la primera vez:

| Archivo | Línea de interés | Qué observa |
|---|---|---|
| `apps/core/fields.py` | `get_prep_value` | El momento exacto del cifrado, antes de llegar a la base |
| `apps/core/fields.py` | `from_db_value` | El descifrado al leer |
| `apps/auditoria/signals.py` | `auditar_guardado` | El diff antes/después que se registra |
| `apps/auditoria/models.py` | `_encadenar` | Cómo se calcula el hash de cada evento |
| `apps/rat/models.py` | `clean` | Las reglas normativas rechazando datos inconsistentes |

### Consola de depuración

Con la ejecución detenida en un punto de interrupción, la pestaña *Consola de
depuración* evalúa expresiones en ese contexto:

```python
self.actividad.alertas
Evento.verificar_cadena()
str(ActividadTratamiento.objects.filter(estado="VIGENTE").query)
```

---

## 4. Inspeccionar la base de datos

Con la extensión **SQLTools** puede abrir `db.sqlite3` y consultar las tablas
directamente. Es la forma más clara de comprobar que el cifrado funciona:

```sql
SELECT username, first_name, email, email_bidx FROM accounts_usuario;
```

`username` aparece legible (es la clave de autenticación, debe ser indexable);
`first_name` y `email` aparecen como `v1$...`. El sufijo `_bidx` muestra el
índice ciego determinista.

```sql
SELECT id, username, accion, modelo, hash_actual FROM auditoria_evento ORDER BY id DESC LIMIT 20;
```

Si modifica cualquier fila de esa tabla con un `UPDATE` y luego ejecuta la tarea
**RAT: verificar integridad de bitácora**, obtendrá el número del evento
comprometido. Vale la pena probarlo una vez para entender qué garantiza el
mecanismo y qué no.

---

## 5. Trabajar con plantillas

`settings.json` asocia `templates/**/*.html` al lenguaje `django-html`. Con eso:

- Las etiquetas `{% %}` y `{{ }}` se resaltan correctamente.
- Emmet funciona dentro de las plantillas.
- **djLint** valida y formatea al guardar.

Si abre una plantilla y ve todo marcado en rojo, revise en la barra de estado
inferior derecha que el lenguaje diga `Django HTML` y no `HTML`.

---

## 6. Atajos frecuentes

| Acción | Atajo |
|---|---|
| Ejecutar / depurar | `F5` |
| Detener | `Shift+F5` |
| Ejecutar tarea | `Ctrl+Shift+P` → *Tasks: Run Task* |
| Terminal integrado | `` Ctrl+` `` |
| Buscar en todo el proyecto | `Ctrl+Shift+F` |
| Ir a definición | `F12` |
| Ir a símbolo del workspace | `Ctrl+T` |
| Paleta de comandos | `Ctrl+Shift+P` |

---

## 7. Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `Import "django" could not be resolved` | Intérprete no seleccionado | §1.4 |
| Imports de `apps.*` en rojo | Falta la raíz en el path de análisis | Ya está en `settings.json`; recargue la ventana (`Ctrl+Shift+P` → *Reload Window*) |
| `.venv\Scripts\Activate.ps1 no se puede cargar` | Política de ejecución de PowerShell | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `RuntimeError: Falta la variable DJANGO_SECRET_KEY` | Está usando `config.settings.prod` sin configurar | Fije `DJANGO_SETTINGS_MODULE=config.settings.dev` en `.env` |
| `DP_ENC_KEYS y DP_INDEX_KEY son obligatorios` | Igual que el anterior, o `.env` no encontrado | Verifique que `.env` esté en la raíz y en UTF-8 sin BOM |
| `CryptoError: la llave '1' no está en el keyring` | Las llaves cambiaron entre ejecuciones | Fije las llaves en `.env` (§1.5) o borre `db.sqlite3` y vuelva a migrar |
| Los puntos de interrupción no se detienen | El recargador reinició el proceso | Use *Django: runserver (sin recarga)* |
| `Port 8000 is already in use` | Quedó un proceso anterior | Windows: `netstat -ano \| findstr :8000` y `taskkill /PID <pid> /F` |
| La página se ve sin estilos | Bootstrap no descargado | Ejecute `deploy/descargar_assets.ps1` (ver README §7) |
| Al modificar un modelo, error de columna inexistente | Falta migrar | Tareas: *crear migraciones* → *aplicar migraciones* |

---

## 8. Advertencia sobre el archivo `.env`

Contiene las llaves de cifrado. Está en `.gitignore`, pero eso cubre solo el
control de versiones. En un entorno de desarrollo compartido conviene además:

- No abrirlo durante demostraciones con pantalla compartida.
- No pegar su contenido en incidencias, canales de chat o herramientas de IA.
- Usar llaves **distintas** en desarrollo y producción. Si comparte llaves entre
  entornos, un respaldo de desarrollo permite descifrar datos de producción.

---

## 9. Sobre el uso de `runserver`

El servidor de desarrollo de Django es monohilo, no valida cabeceras y su propia
documentación advierte que no ha pasado auditorías de seguridad. Es adecuado
para desarrollar y no lo es para nada más: no lo exponga en la red ni lo use
para una demostración a terceros fuera de su equipo.

Para una prueba realista use la configuración *Waitress: simular producción*, o
el despliegue completo descrito en `docs/INSTALACION_WINDOWS.md`.
