# RAT — Registro de Actividades de Tratamiento (LOPDP Ecuador)

Aplicación Django + Bootstrap 5 para levantar y mantener el registro de actividades
de tratamiento de una compañía de fianzas y seguro de crédito.

## Puesta en marcha

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                     # descomente el driver de su motor
cp .env.example .env                                # y edítelo
python manage.py migrate
python manage.py seed_catalogos                     # catálogos + perfiles base
python manage.py createsuperuser
python manage.py runserver
```

Entre en `http://127.0.0.1:8000/`.

## Motores de base de datos

`DB_ENGINE` acepta `postgres`, `mysql`, `mssql` o `sqlite`. Las mismas migraciones
corren en los cuatro: el modelo evita tipos propietarios (nada de `JSONField`,
`ArrayField` ni `TextField` indexados), y las selecciones múltiples se resuelven con
tablas de relación en lugar de listas serializadas. Eso hace la matriz consultable
por SQL directo, que es lo que va a necesitar cuando la Autoridad pida un extracto.

| Motor | Driver | Nota |
|---|---|---|
| PostgreSQL | `psycopg[binary]` | Recomendado |
| MySQL / MariaDB | `mysqlclient` | Use `utf8mb4` |
| SQL Server | `mssql-django` + `pyodbc` | Requiere ODBC Driver 17/18 en el SO |
| SQLite | incluido | Solo desarrollo y pruebas |

## Estructura

```
config/            settings, urls, wsgi
apps/core/         modelos abstractos, mixins Bootstrap, vistas CRUD genéricas
apps/catalogos/    catálogos parametrizables + CRUD genérico + carga inicial
apps/rat/          actividad de tratamiento (3.1 a 3.20), formsets, export, tablero
apps/cuentas/      login, usuarios, perfiles y permisos
templates/         Bootstrap 5, un parcial de campo reutilizable
```

## Cómo agregar un catálogo nuevo

1. Cree el modelo heredando de `apps.core.models.CatalogoBase`.
2. Añada una entrada en `apps/catalogos/views.py::REGISTRO`.
3. `makemigrations` y `migrate`.

No hace falta escribir vistas, formularios ni plantillas: el CRUD genérico y el
menú de catálogos los toman del registro.

## Permisos

`seed_catalogos` crea tres perfiles de arranque: **DPD** (todo), **Dueño de proceso**
(ver, crear y editar actividades) y **Consulta** (solo lectura). Además del CRUD
estándar, el modelo define dos permisos propios: `validar_actividad` (cambiar de
estado) y `exportar_rat`. Revise los perfiles en *Administración → Perfiles* antes de
salir a producción.

## Decisiones de diseño que conviene conocer

- **Una fila = una finalidad.** No hay campo "sistema" ni "base de datos" como eje
  principal, a propósito. Si dos finalidades comparten la misma tabla, siguen siendo
  dos filas: cambian el plazo, la base de licitud y los destinatarios.
- **El blanco no significa nada.** 3.4 usa tres valores (Sí / No aplica / Pendiente de
  evaluar) y 3.13 obliga a elegir explícitamente «Ninguno» cuando no hay
  comunicaciones externas. Un campo vacío no distingue «no aplica» de «no lo revisé».
- **Cada base de licitud lleva su justificación** y el interés legítimo exige el test
  de ponderación en el mismo formulario, no en un anexo aparte.
- **Cada comunicación externa lleva su fundamento** (Art. 33 o excepción del Art. 36),
  porque el fundamento cambia por destinatario, no por actividad.
- **Los catálogos se desactivan, no se borran.** Las claves foráneas son `PROTECT`: si
  una actividad histórica referencia una opción, borrarla destruiría la trazabilidad.
- **Las alertas no bloquean.** La ficha muestra observaciones (encargado sin contrato,
  transferencia sin reportar, menores sin verificar) para que el DPD las mire antes de
  validar, pero no impiden guardar un borrador incompleto.

## Pruebas

```bash
python manage.py test apps.rat
```

## Antes de producción

- `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY` real, `ALLOWED_HOSTS` explícito.
- HTTPS y `COOKIE_SECURE=True`.
- Servir estáticos con WhiteNoise o el servidor web (`collectstatic`).
- Usuario de base de datos sin privilegios de DDL en runtime.
- Respaldos y bitácoras: el propio RAT es un registro que la Autoridad puede requerir.

## Alcance

Esta herramienta ordena y documenta el RAT. No sustituye el criterio del DPD ni una
asesoría legal: las referencias normativas incluidas en los catálogos son un punto de
partida que debe validarse contra el texto vigente de la LOPDP, su reglamento y las
resoluciones de la SPDP.
