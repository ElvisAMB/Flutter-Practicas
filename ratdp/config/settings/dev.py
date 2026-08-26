"""Configuración de desarrollo. NO usar en producción."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env

DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-inseguro-no-usar-en-produccion")

# Llaves de desarrollo: se generan al vuelo si no existen, para que
# `runserver` funcione sin configuración previa. En producción esto falla
# a propósito (ver prod.py).
if not DP_ENC_KEYS:  # noqa: F405
    from apps.core.crypto import generar_llave  # noqa: E402
    DP_ENC_KEYS = {"1": generar_llave()}
    DP_ENC_ACTIVE_KEY = "1"
if not DP_INDEX_KEY:  # noqa: F405
    from apps.core.crypto import generar_llave  # noqa: E402
    DP_INDEX_KEY = generar_llave()

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
