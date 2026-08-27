"""Expone el usuario de la petición para poder sellar creado_por/actualizado_por."""
import threading

_local = threading.local()


def usuario_actual():
    return getattr(_local, "usuario", None)


class UsuarioActualMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.usuario = getattr(request, "user", None)
        try:
            return self.get_response(request)
        finally:
            _local.usuario = None
