"""
Configuración del proyecto RAT (Registro de Actividades de Tratamiento) - LOPDP Ecuador.

El motor de base de datos se elige por variable de entorno (DB_ENGINE):
    postgres | mysql | mssql | sqlite
Todo el modelo de datos evita tipos propietarios (JSONField, ArrayField, etc.)
para que las mismas migraciones corran en los tres motores.
"""
from pathlib import Path
import os

try:  # carga .env si python-dotenv está instalado (opcional)
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def env(clave, defecto=None):
    return os.environ.get(clave, defecto)


def env_bool(clave, defecto=False):
    valor = os.environ.get(clave)
    if valor is None:
        return defecto
    return valor.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


SECRET_KEY = env("DJANGO_SECRET_KEY", "cambie-esta-clave-en-produccion")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in env("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
    "apps.catalogos",
    "apps.rat",
    "apps.cuentas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.UsuarioActualMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.datos_aplicacion",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --------------------------------------------------------------------------
# Base de datos: un solo bloque, cuatro motores.
# --------------------------------------------------------------------------
MOTORES = {
    "postgres": "django.db.backends.postgresql",
    "postgresql": "django.db.backends.postgresql",
    "mysql": "django.db.backends.mysql",
    "mariadb": "django.db.backends.mysql",
    "mssql": "mssql",  # requiere el paquete mssql-django
    "sqlserver": "mssql",
    "sqlite": "django.db.backends.sqlite3",
}

DB_ENGINE = env("DB_ENGINE", "sqlite").strip().lower()
if DB_ENGINE not in MOTORES:
    raise ValueError(
        f"DB_ENGINE '{DB_ENGINE}' no reconocido. Use uno de: {', '.join(sorted(MOTORES))}"
    )

if DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": MOTORES["sqlite"],
            "NAME": env("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        }
    }
else:
    PUERTOS = {"postgres": "5432", "postgresql": "5432", "mysql": "3306",
               "mariadb": "3306", "mssql": "1433", "sqlserver": "1433"}
    DATABASES = {
        "default": {
            "ENGINE": MOTORES[DB_ENGINE],
            "NAME": env("DB_NAME", "rat"),
            "USER": env("DB_USER", ""),
            "PASSWORD": env("DB_PASSWORD", ""),
            "HOST": env("DB_HOST", "localhost"),
            "PORT": env("DB_PORT", PUERTOS[DB_ENGINE]),
            "OPTIONS": {},
        }
    }
    if MOTORES[DB_ENGINE] == "mssql":
        DATABASES["default"]["OPTIONS"] = {
            "driver": env("DB_MSSQL_DRIVER", "ODBC Driver 18 for SQL Server"),
            "extra_params": env("DB_MSSQL_EXTRA", "TrustServerCertificate=yes"),
        }
    if MOTORES[DB_ENGINE] == "django.db.backends.mysql":
        DATABASES["default"]["OPTIONS"] = {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-ec"
TIME_ZONE = env("TIME_ZONE", "America/Guayaquil")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

LOGIN_URL = "cuentas:login"
LOGIN_REDIRECT_URL = "rat:actividad_list"
LOGOUT_REDIRECT_URL = "cuentas:login"

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# Datos de marca usados en las plantillas
ORGANIZACION = env("ORGANIZACION", "Nombre de la Compañía")
APP_NOMBRE = "Registro de Actividades de Tratamiento"

# Endurecimiento básico cuando DEBUG=False
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = env_bool("COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = env_bool("COOKIE_SECURE", True)
    X_FRAME_OPTIONS = "DENY"
    SESSION_COOKIE_AGE = int(env("SESSION_COOKIE_AGE", "3600"))
