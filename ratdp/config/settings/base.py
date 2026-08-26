"""
config/settings/base.py
=======================
Configuración común. Nada específico de entorno vive aquí.

Estructura: base.py -> dev.py / prod.py. Los secretos se leen de variables de
entorno (archivo .env en desarrollo; variables de sistema o DPAPI en Windows
Server). Ningún secreto se versiona.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env(clave: str, defecto=None, requerido: bool = False):
    valor = os.environ.get(clave, defecto)
    if requerido and valor in (None, ""):
        raise RuntimeError(f"Falta la variable de entorno obligatoria: {clave}")
    return valor


def env_bool(clave: str, defecto: bool = False) -> bool:
    return str(os.environ.get(clave, defecto)).lower() in {"1", "true", "yes", "si", "sí", "on"}


def env_list(clave: str, defecto: str = "") -> list[str]:
    return [x.strip() for x in os.environ.get(clave, defecto).split(",") if x.strip()]


# --------------------------------------------------------------- seguridad
SECRET_KEY = env("DJANGO_SECRET_KEY", "cambieme-solo-en-desarrollo")
DEBUG = False
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

# Llaves criptográficas de la aplicación (ver apps/core/crypto.py)
DP_ENC_KEYS = json.loads(env("DP_ENC_KEYS", "{}") or "{}")
DP_ENC_ACTIVE_KEY = env("DP_ENC_ACTIVE_KEY", "1")
DP_INDEX_KEY = env("DP_INDEX_KEY", "")

# ------------------------------------------------------------ aplicaciones
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.auditoria",
    "apps.catalogos",
    "apps.rat",
    "apps.indicadores",
    "apps.plantillas",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.auditoria.middleware.AuditoriaMiddleware",
    "apps.accounts.middleware.CambioPasswordMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

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
                "apps.core.context_processors.organizacion",
            ],
        },
    },
]

# ------------------------------------------------------------ base de datos
# Portabilidad: el motor se define por variables de entorno. El código de la
# aplicación no contiene SQL específico de motor ni extensiones (pgcrypto,
# Always Encrypted, etc.). Cambiar de motor = cambiar DB_ENGINE y migrar.
_MOTORES = {
    "postgresql": "django.db.backends.postgresql",
    "mysql": "django.db.backends.mysql",
    "mariadb": "django.db.backends.mysql",
    "oracle": "django.db.backends.oracle",
    "sqlite": "django.db.backends.sqlite3",
    "mssql": "mssql",  # requiere el paquete mssql-django
}

_motor = env("DB_ENGINE", "sqlite").lower()

if _motor == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": _MOTORES["sqlite"],
            "NAME": env("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": _MOTORES.get(_motor, _motor),
            "NAME": env("DB_NAME", "ratdp", requerido=True),
            "USER": env("DB_USER", ""),
            "PASSWORD": env("DB_PASSWORD", ""),
            "HOST": env("DB_HOST", "localhost"),
            "PORT": env("DB_PORT", ""),
            "CONN_MAX_AGE": int(env("DB_CONN_MAX_AGE", "60")),
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": json.loads(env("DB_OPTIONS", "{}") or "{}"),
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------ autenticación
AUTH_USER_MODEL = "accounts.Usuario"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "indicadores:tablero"
LOGOUT_REDIRECT_URL = "accounts:login"

AUTHENTICATION_BACKENDS = ["apps.accounts.backends.BackendConBloqueo"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "apps.accounts.validators.ComplejidadValidator"},
]

# Argon2 primero: resistente a GPU/ASIC. Requiere `argon2-cffi`.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

MAX_INTENTOS_FALLIDOS = int(env("MAX_INTENTOS_FALLIDOS", "5"))
MINUTOS_BLOQUEO = int(env("MINUTOS_BLOQUEO", "15"))
DIAS_VIGENCIA_PASSWORD = int(env("DIAS_VIGENCIA_PASSWORD", "90"))

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = int(env("SESSION_COOKIE_AGE", "1800"))  # 30 min
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# ------------------------------------------------------------- auditoría
AUDITORIA_MODELOS = [
    "accounts.Usuario", "accounts.Perfil",
    "rat.ActividadTratamiento", "rat.Brecha", "rat.Entrevista",
    "catalogos.Area", "catalogos.Tercero", "catalogos.CategoriaDato",
    "catalogos.BaseLicitud", "catalogos.HabilitanteEspecial",
    "catalogos.CategoriaTitular", "catalogos.MedidaSeguridad",
    "catalogos.CriterioConservacion", "catalogos.SistemaInformacion",
    "catalogos.Macroproceso", "catalogos.MecanismoTransferencia",
    "plantillas.Plantilla", "plantillas.DocumentoGenerado",
]

# Rutas cuyo GET se audita como CONSULTA (ver middleware para el porqué).
AUDITORIA_RUTAS_CONSULTA = [
    r"^/rat/[0-9a-f\-]{36}/$",
    r"^/rat/exportar",
    r"^/usuarios/[0-9a-f\-]{36}/$",
    r"^/auditoria/",
    r"^/plantillas/[0-9a-f\-]{36}/",
]

RETENCION_BITACORA_DIAS = int(env("RETENCION_BITACORA_DIAS", "2555"))  # ~7 años

# ---------------------------------------------------- internacionalización
LANGUAGE_CODE = "es-ec"
TIME_ZONE = env("TIME_ZONE", "America/Guayaquil")
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

# ------------------------------------------------------------- estáticos
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / "media")))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # El manifiesto comprimido exige que collectstatic se haya ejecutado y que
    # todo archivo referenciado exista. Se activa solo en prod.py, para que las
    # pruebas y el desarrollo no dependan de ese paso.
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# ----------------------------------------------------------------- caché
CACHES = {
    "default": {
        "BACKEND": env("CACHE_BACKEND", "django.core.cache.backends.locmem.LocMemCache"),
        "LOCATION": env("CACHE_LOCATION", "ratdp"),
    }
}

# ------------------------------------------------------------- parámetros
ORGANIZACION = {
    "razon_social": env("ORG_RAZON_SOCIAL", "[Razón social]"),
    "ruc": env("ORG_RUC", ""),
    "dpd_contacto": env("ORG_DPD_CONTACTO", "dpd@empresa.com"),
    "codigo_procedimiento": "PR-PDP-001",
    "version_procedimiento": "1.0",
}

PAGINACION = int(env("PAGINACION", "25"))

# ------------------------------------------------------------------- logs
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{asctime} {levelname} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "archivo": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(BASE_DIR / "logs" / "aplicacion.log"),
            "maxBytes": 20 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "seguridad": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(BASE_DIR / "logs" / "seguridad.log"),
            "maxBytes": 20 * 1024 * 1024,
            "backupCount": 20,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "archivo"], "level": "INFO"},
        "django.security": {"handlers": ["seguridad"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console", "archivo"], "level": "INFO"},
    },
}
