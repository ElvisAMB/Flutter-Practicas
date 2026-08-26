"""
apps/core/mixins.py
===================
Control de acceso reutilizable para las vistas.

Principio: **denegar por defecto**. Toda vista hereda de ``VistaBase``, que
exige autenticación. El permiso concreto se declara por vista con
``permiso_requerido``; una vista sin permiso declarado solo es accesible para
usuarios autenticados y queda registrada en el log como configuración
incompleta.
"""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class PermisoRequeridoMixin(AccessMixin):
    """Verifica ``permiso_requerido`` (str o lista) antes de despachar."""

    permiso_requerido: str | list[str] | None = None
    requiere_todos_los_permisos = True

    def obtener_permisos(self) -> list[str]:
        if self.permiso_requerido is None:
            logger.warning("Vista %s sin permiso_requerido declarado.", self.__class__.__name__)
            return []
        if isinstance(self.permiso_requerido, str):
            return [self.permiso_requerido]
        return list(self.permiso_requerido)

    def tiene_permiso(self) -> bool:
        permisos = self.obtener_permisos()
        if not permisos:
            return True
        comprobar = all if self.requiere_todos_los_permisos else any
        return comprobar(self.request.user.has_perm(p) for p in permisos)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.tiene_permiso():
            raise PermissionDenied("No cuenta con el permiso necesario para esta operación.")
        return super().dispatch(request, *args, **kwargs)


class VistaBase(LoginRequiredMixin, PermisoRequeridoMixin):
    """Base de toda vista de la aplicación."""

    titulo = ""
    subtitulo = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("titulo", self.titulo)
        ctx.setdefault("subtitulo", self.subtitulo)
        ctx.setdefault("solo_lectura", getattr(self.request.user, "es_auditor", False))
        return ctx


class SoloAdministradorMixin(VistaBase):
    """Restringe la vista al perfil ADMINISTRADOR (gestión de accesos)."""

    def tiene_permiso(self) -> bool:
        return bool(getattr(self.request.user, "es_administrador", False))


class BloquearAuditorMixin:
    """
    Corta cualquier método de escritura para el perfil AUDITOR.

    Defensa en profundidad: aunque ``Usuario.has_perm`` ya niega permisos de
    escritura al auditor, esta comprobación evita que una vista mal declarada
    (sin ``permiso_requerido``) abra un hueco.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.method not in ("GET", "HEAD", "OPTIONS") and getattr(
            request.user, "es_auditor", False
        ):
            messages.error(request, "El perfil Auditor es de solo lectura.")
            raise PermissionDenied("Perfil de solo lectura.")
        return super().dispatch(request, *args, **kwargs)


class AsignarUsuarioMixin:
    """Rellena ``creado_por`` / ``actualizado_por`` al guardar un formulario."""

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)


class MensajeExitoMixin:
    mensaje_exito = "Operación realizada correctamente."

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, self.mensaje_exito)
        return respuesta


class BorradoLogicoMixin:
    """Convierte el DELETE de una vista en borrado lógico auditado."""

    def form_valid(self, form):
        objeto = self.get_object()
        objeto.delete(usuario=self.request.user)
        messages.warning(
            self.request,
            f"«{objeto}» fue dado de baja. El registro se conserva para trazabilidad "
            f"y puede restaurarse desde la papelera.",
        )
        return redirect(self.get_success_url())
