"""
apps/auditoria/signals.py
=========================
Auditoría automática de escrituras.

Solo se auditan los modelos declarados en ``settings.AUDITORIA_MODELOS``
(lista de "app_label.ModelName"). Auditar todo, incluidas las sesiones de
Django, duplicaría el volumen sin aportar evidencia útil.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import (
    user_logged_in, user_logged_out, user_login_failed,
)
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .middleware import contexto_actual
from .models import Accion, Evento

MAX_VALOR = 500


def _auditable(instancia) -> bool:
    etiqueta = f"{instancia._meta.app_label}.{instancia._meta.object_name}"
    return etiqueta in set(getattr(settings, "AUDITORIA_MODELOS", []))


def _serializable(instancia) -> dict:
    """Instantánea de campos concretos (excluye M2M y relaciones inversas)."""
    datos = {}
    for f in instancia._meta.concrete_fields:
        if f.name in {"password", "hash_actual", "hash_anterior"}:
            datos[f.name] = "***"
            continue
        valor = getattr(instancia, f.attname, None)
        datos[f.name] = str(valor)[:MAX_VALOR] if valor is not None else None
    return datos


def _base_evento(instancia, accion, **extra) -> dict:
    ctx = contexto_actual()
    return dict(
        usuario=ctx.get("usuario"),
        username=ctx.get("username", "sistema"),
        perfil=ctx.get("perfil", ""),
        accion=accion,
        modelo=f"{instancia._meta.app_label}.{instancia._meta.object_name}",
        objeto_id=str(getattr(instancia, "pk", "")),
        objeto_repr=str(instancia)[:300],
        ip=ctx.get("ip"),
        user_agent=ctx.get("user_agent", ""),
        ruta=ctx.get("ruta", ""),
        metodo=ctx.get("metodo", ""),
        session_key=ctx.get("session_key", ""),
        **extra,
    )


@receiver(pre_save)
def capturar_estado_previo(sender, instance, **kwargs):
    if not _auditable(instance) or instance.pk is None:
        return
    try:
        previo = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    instance._auditoria_previo = _serializable(previo)


@receiver(post_save)
def auditar_guardado(sender, instance, created, **kwargs):
    if not _auditable(instance):
        return

    if created:
        Evento.registrar(**_base_evento(instance, Accion.CREACION),
                         detalle={"nuevo": _serializable(instance)})
        return

    previo = getattr(instance, "_auditoria_previo", None)
    actual = _serializable(instance)
    cambios = {}
    if previo:
        for campo, valor in actual.items():
            if previo.get(campo) != valor:
                cambios[campo] = {"antes": previo.get(campo), "despues": valor}
    else:
        cambios = {"__sin_snapshot__": actual}

    # Borrado lógico -> se audita como eliminación, no como modificación.
    if "eliminado_en" in cambios and cambios["eliminado_en"]["despues"] not in (None, "None"):
        accion = Accion.ELIMINACION
    elif "eliminado_en" in cambios and cambios["eliminado_en"]["antes"] not in (None, "None"):
        accion = Accion.RESTAURACION
    elif "estado" in cambios:
        accion = Accion.CAMBIO_ESTADO
    else:
        accion = Accion.MODIFICACION

    if not cambios:
        return
    Evento.registrar(**_base_evento(instance, accion), detalle={"cambios": cambios})


@receiver(post_delete)
def auditar_borrado_fisico(sender, instance, **kwargs):
    if not _auditable(instance):
        return
    Evento.registrar(**_base_evento(instance, Accion.ELIMINACION),
                     detalle={"borrado_fisico": _serializable(instance)})


@receiver(m2m_changed)
def auditar_permisos(sender, instance, action, pk_set, **kwargs):
    """Cambios de permisos y de pertenencia a grupos: siempre auditables."""
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    nombre = sender.__name__
    if not any(x in nombre for x in ("permissions", "groups", "user_permissions")):
        return
    Evento.registrar(**_base_evento(instance, Accion.CAMBIO_PERMISO),
                     detalle={"accion_m2m": action, "relacion": nombre,
                              "ids": sorted(str(p) for p in (pk_set or []))})


# ---------------------------------------------------------------- sesiones
@receiver(user_logged_in)
def auditar_login(sender, request, user, **kwargs):
    from apps.accounts.models import SesionAcceso

    ctx = contexto_actual()
    Evento.registrar(
        usuario=user, username=user.username,
        perfil=getattr(getattr(user, "perfil", None), "codigo", ""),
        accion=Accion.LOGIN, ip=ctx.get("ip"), user_agent=ctx.get("user_agent", ""),
        ruta=ctx.get("ruta", ""), metodo=ctx.get("metodo", ""),
        session_key=getattr(request.session, "session_key", "") or "",
    )
    SesionAcceso.objects.create(
        usuario=user, session_key=getattr(request.session, "session_key", "") or "",
        ip=ctx.get("ip"), user_agent=ctx.get("user_agent", "")[:400],
    )
    if user.intentos_fallidos:
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        user.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])


@receiver(user_logged_out)
def auditar_logout(sender, request, user, **kwargs):
    from apps.accounts.models import SesionAcceso

    if user is None:
        return
    ctx = contexto_actual()
    Evento.registrar(
        usuario=user, username=user.username, accion=Accion.LOGOUT,
        ip=ctx.get("ip"), ruta=ctx.get("ruta", ""),
    )
    SesionAcceso.objects.filter(
        usuario=user, session_key=getattr(request.session, "session_key", "") or "", fin__isnull=True,
    ).update(fin=timezone.now())


@receiver(user_login_failed)
def auditar_login_fallido(sender, credentials, request=None, **kwargs):
    from apps.accounts.models import SesionAcceso

    ctx = contexto_actual()
    username = (credentials or {}).get("username", "")[:150]
    Evento.registrar(
        username=username or "desconocido", accion=Accion.LOGIN_FALLIDO, exitoso=False,
        ip=ctx.get("ip"), user_agent=ctx.get("user_agent", ""), ruta=ctx.get("ruta", ""),
    )
    Usuario = get_user_model()
    limite = getattr(settings, "MAX_INTENTOS_FALLIDOS", 5)
    minutos = getattr(settings, "MINUTOS_BLOQUEO", 15)
    try:
        user = Usuario.objects.get(username=username)
    except Usuario.DoesNotExist:
        return
    user.intentos_fallidos = (user.intentos_fallidos or 0) + 1
    if user.intentos_fallidos >= limite:
        user.bloqueado_hasta = timezone.now() + timezone.timedelta(minutes=minutos)
    user.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
    SesionAcceso.objects.create(
        usuario=user, session_key="", ip=ctx.get("ip"), exitosa=False,
        motivo_fallo="credenciales inválidas",
    )
