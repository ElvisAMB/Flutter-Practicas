"""
apps/auditoria/middleware.py
============================
Captura del contexto de la petición y registro automático de accesos.

Por qué middleware y no solo señales: las señales ``post_save`` no conocen al
usuario ni la IP. Se guardan en un ``ContextVar`` (seguro con ASGI y con hilos)
y las señales lo leen.

Nota de rendimiento: registrar **cada** GET en la bitácora multiplica el
volumen por 10–50. Por eso solo se auditan como CONSULTA las rutas declaradas
en ``AUDITORIA_RUTAS_CONSULTA`` (por defecto, vistas de detalle y de
exportación), no cada carga de listado o de estático. La lectura masiva se
audita a nivel de exportación, que es donde existe riesgo real de fuga.
"""

from __future__ import annotations

import contextvars
import re
import time

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from .models import Accion, Evento

_contexto = contextvars.ContextVar("auditoria_ctx", default=None)


def contexto_actual() -> dict:
    return _contexto.get() or {}


def usuario_actual():
    return contexto_actual().get("usuario")


def obtener_ip(request) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff and getattr(settings, "USE_X_FORWARDED_FOR", False):
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditoriaMiddleware(MiddlewareMixin):
    """Publica el contexto de la petición y audita consultas relevantes."""

    def process_request(self, request):
        usuario = getattr(request, "user", None)
        if usuario is not None and not usuario.is_authenticated:
            usuario = None
        _contexto.set({
            "usuario": usuario,
            "username": getattr(usuario, "username", "") or "anónimo",
            "perfil": getattr(getattr(usuario, "perfil", None), "codigo", ""),
            "ip": obtener_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:400],
            "ruta": request.path[:300],
            "metodo": request.method,
            "session_key": getattr(getattr(request, "session", None), "session_key", "") or "",
            "inicio": time.monotonic(),
        })

    def process_response(self, request, response):
        ctx = contexto_actual()
        if not ctx or not ctx.get("usuario"):
            _contexto.set(None)
            return response

        patrones = getattr(settings, "AUDITORIA_RUTAS_CONSULTA", [])
        if request.method == "GET" and any(re.search(p, request.path) for p in patrones):
            Evento.registrar(
                usuario=ctx["usuario"], username=ctx["username"], perfil=ctx["perfil"],
                accion=Accion.CONSULTA, ip=ctx["ip"], user_agent=ctx["user_agent"],
                ruta=ctx["ruta"], metodo=ctx["metodo"], session_key=ctx["session_key"],
                exitoso=response.status_code < 400,
            )
        elif response.status_code == 403:
            Evento.registrar(
                usuario=ctx["usuario"], username=ctx["username"], perfil=ctx["perfil"],
                accion=Accion.ACCESO_DENEGADO, ip=ctx["ip"], user_agent=ctx["user_agent"],
                ruta=ctx["ruta"], metodo=ctx["metodo"], exitoso=False,
            )
        _contexto.set(None)
        return response

    def process_exception(self, request, exception):
        _contexto.set(None)
        return None
