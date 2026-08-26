"""
deploy/servidor.py
==================
Arranque de Waitress para producción en Windows / Windows Server.

Escucha SOLO en loopback: IIS (o el proxy corporativo) es el único cliente
legítimo. Exponer este puerto a la red equivale a publicar la aplicación sin
TLS y sin cabeceras de seguridad.

Uso como servicio con NSSM: ver docs/INSTALACION_WINDOWS.md §6.
"""

import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

env_file = BASE / ".env"
if env_file.exists():
    for linea in env_file.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

import sys  # noqa: E402

sys.path.insert(0, str(BASE))

from waitress import serve  # noqa: E402

from config.wsgi import application  # noqa: E402

if __name__ == "__main__":
    serve(
        application,
        host=os.environ.get("WAITRESS_HOST", "127.0.0.1"),
        port=int(os.environ.get("WAITRESS_PORT", "8000")),
        threads=int(os.environ.get("WAITRESS_THREADS", "12")),
        connection_limit=200,
        channel_timeout=120,
        ident="",            # no anunciar el servidor en las respuestas
        url_scheme="https",  # coherente con SECURE_PROXY_SSL_HEADER
    )
