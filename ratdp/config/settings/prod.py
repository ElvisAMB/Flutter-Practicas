"""
Configuración de producción.

Falla al arrancar si falta cualquier secreto: es preferible un despliegue que
no levanta a uno que levanta con llaves de desarrollo.
"""
from .base import *  # noqa: F401,F403
from .base import env, env_bool, env_list

DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY", requerido=True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise RuntimeError("DJANGO_ALLOWED_HOSTS es obligatorio en producción.")
if not DP_ENC_KEYS or not DP_INDEX_KEY:  # noqa: F405
    raise RuntimeError(
        "DP_ENC_KEYS y DP_INDEX_KEY son obligatorios. Genérelos con "
        "`python manage.py generar_llave`."
    )

# --------------------------------------------------------------- HTTPS
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_FOR = env_bool("USE_X_FORWARDED_FOR", True)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_NAME = "__Host-ratdp-session"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", "")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@empresa.com")

STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}

ADMINS = [("DPD", env("ORG_DPD_CONTACTO", "dpd@empresa.com"))]
LOGGING["handlers"]["mail_admins"] = {  # noqa: F405
    "class": "django.utils.log.AdminEmailHandler", "level": "ERROR",
}
LOGGING["loggers"]["django"]["handlers"].append("mail_admins")  # noqa: F405
