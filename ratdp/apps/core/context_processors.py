"""Datos de organización disponibles en todas las plantillas."""
from django.conf import settings


def organizacion(request):
    return {
        "ORGANIZACION": getattr(settings, "ORGANIZACION", {}),
        "APP_VERSION": "1.0.0",
    }
