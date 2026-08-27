from django.conf import settings


def datos_aplicacion(request):
    return {
        "APP_NOMBRE": settings.APP_NOMBRE,
        "ORGANIZACION": settings.ORGANIZACION,
    }
