"""
apps/accounts/models.py
=======================
Gestión de identidades, perfiles (roles) y permisos.

Modelo de autorización
----------------------
Se reutiliza el sistema de permisos de Django (``auth.Permission``) en lugar de
inventar uno nuevo. Un ``Perfil`` es un ``auth.Group`` enriquecido con
metadatos (descripción, si es de sistema, alcance de datos). Ventajas:

*  ``@permission_required`` y ``user.has_perm()`` funcionan sin adaptadores.
*  El admin de Django y los tests de terceros siguen siendo válidos.
*  Los permisos por modelo (add/change/delete/view) se crean solos en cada
   migración.

Perfiles de sistema (no eliminables, no renombrables):
  ADMINISTRADOR  -> superusuario funcional; único que gestiona accesos.
  AUDITOR        -> solo lectura sobre todo, incluida la bitácora.
  USUARIO        -> plantilla base editable en datos y en accesos.

Perfiles personalizados: se crean libremente desde la interfaz y se les asignan
permisos individuales.
"""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.fields import (
    BlindIndexField,
    EncryptedCharField,
    EncryptedEmailField,
)
from apps.core.models import BlindIndexMixin, UUIDModel


class PerfilSistema(models.TextChoices):
    ADMINISTRADOR = "ADMINISTRADOR", _("Administrador")
    AUDITOR = "AUDITOR", _("Auditor (solo lectura)")
    USUARIO = "USUARIO", _("Usuario común")


class Perfil(models.Model):
    """
    Rol de acceso. Envuelve un ``auth.Group`` en relación 1-1.
    """

    grupo = models.OneToOneField(
        Group, on_delete=models.CASCADE, related_name="perfil", verbose_name=_("Grupo"),
    )
    codigo = models.SlugField(_("Código"), max_length=64, unique=True)
    descripcion = models.TextField(_("Descripción"), blank=True)
    es_sistema = models.BooleanField(
        _("Perfil de sistema"), default=False,
        help_text=_("Los perfiles de sistema no pueden eliminarse ni renombrarse."),
    )
    permite_edicion_permisos = models.BooleanField(
        _("Permite editar sus permisos"), default=True,
        help_text=_("ADMINISTRADOR y AUDITOR tienen permisos fijos por diseño."),
    )
    activo = models.BooleanField(_("Activo"), default=True)
    creado_en = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = _("Perfil")
        verbose_name_plural = _("Perfiles")
        ordering = ("codigo",)

    def __str__(self) -> str:
        return self.grupo.name

    @property
    def nombre(self) -> str:
        return self.grupo.name

    @property
    def es_solo_lectura(self) -> bool:
        return self.codigo == PerfilSistema.AUDITOR

    def permisos(self):
        return self.grupo.permissions.select_related("content_type")

    def asignar_permisos(self, permisos: list[Permission]) -> None:
        if not self.permite_edicion_permisos:
            raise ValueError(
                f"El perfil '{self.codigo}' tiene permisos fijos y no admite edición."
            )
        self.grupo.permissions.set(permisos)


class UsuarioManager(UserManager):
    """Manager que resuelve el login por índice ciego del correo."""

    def get_by_natural_key(self, username):
        return self.get(username=username)

    def por_email(self, email: str):
        from apps.core.crypto import blind_index

        return self.get(email_bidx=blind_index(email, scope="usuario.email"))


class Usuario(UUIDModel, BlindIndexMixin, AbstractUser):
    """
    Usuario del sistema.

    Los datos personales del propio usuario (nombre, apellido, correo,
    documento, teléfono) **sí** son datos personales bajo la LOPDP y por eso se
    cifran. El ``username`` no se cifra: es la clave natural de autenticación y
    debe ser indexable con costo O(log n) en cada login. Es un identificador
    asignado por la organización, no un dato del titular.
    """

    first_name = EncryptedCharField(
        _("Nombres"), max_length=512, blank=True, aad_scope="usuario.first_name",
    )
    last_name = EncryptedCharField(
        _("Apellidos"), max_length=512, blank=True, aad_scope="usuario.last_name",
    )
    email = EncryptedEmailField(
        _("Correo electrónico"), max_length=512, blank=True, aad_scope="usuario.email",
    )
    email_bidx = BlindIndexField(source="email", scope="usuario.email", db_index=True)

    documento = EncryptedCharField(
        _("Documento de identidad"), max_length=512, blank=True, aad_scope="usuario.documento",
    )
    documento_bidx = BlindIndexField(source="documento", scope="usuario.documento")
    telefono = EncryptedCharField(
        _("Teléfono"), max_length=512, blank=True, aad_scope="usuario.telefono",
    )

    cargo = models.CharField(_("Cargo"), max_length=150, blank=True)
    area = models.ForeignKey(
        "catalogos.Area", verbose_name=_("Área"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="usuarios",
    )
    perfil = models.ForeignKey(
        Perfil, verbose_name=_("Perfil"), null=True, blank=True,
        on_delete=models.PROTECT, related_name="usuarios",
    )

    mfa_habilitado = models.BooleanField(_("MFA habilitado"), default=False)
    debe_cambiar_password = models.BooleanField(_("Debe cambiar la contraseña"), default=True)
    ultimo_cambio_password = models.DateTimeField(_("Último cambio de contraseña"), null=True, blank=True)
    intentos_fallidos = models.PositiveSmallIntegerField(default=0, editable=False)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True, editable=False)

    objects = UsuarioManager()

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ("username",)
        permissions = [
            ("gestionar_accesos", _("Puede gestionar perfiles, permisos y accesos")),
            ("ver_bitacora", _("Puede consultar la bitácora de auditoría")),
            ("exportar_datos", _("Puede exportar información del sistema")),
        ]

    def __str__(self) -> str:
        return f"{self.username}"

    # -- helpers de rol ----------------------------------------------------
    @property
    def es_administrador(self) -> bool:
        return self.is_superuser or (self.perfil_id and self.perfil.codigo == PerfilSistema.ADMINISTRADOR)

    @property
    def es_auditor(self) -> bool:
        return bool(self.perfil_id) and self.perfil.codigo == PerfilSistema.AUDITOR

    @property
    def nombre_completo(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def esta_bloqueado(self) -> bool:
        return bool(self.bloqueado_hasta and self.bloqueado_hasta > timezone.now())

    def sincronizar_grupo(self) -> None:
        """Mantiene ``user.groups`` alineado con el perfil asignado."""
        self.groups.clear()
        if self.perfil_id:
            self.groups.add(self.perfil.grupo)

    def save(self, *args, **kwargs):
        nuevo = self._state.adding
        super().save(*args, **kwargs)
        if not nuevo or self.perfil_id:
            self.sincronizar_grupo()

    def has_perm(self, perm, obj=None):
        """
        El AUDITOR nunca obtiene permisos de escritura, aunque un
        administrador se los asigne por error a su grupo.
        """
        if self.es_auditor and not perm.split(".")[-1].startswith(("view_", "ver_")):
            return False
        return super().has_perm(perm, obj)


class SesionAcceso(models.Model):
    """
    Registro de sesiones. Complementa la bitácora: permite responder
    "¿quién estuvo conectado y desde dónde?" sin recorrer millones de eventos.
    """

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="sesiones")
    session_key = models.CharField(max_length=64, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, blank=True)
    inicio = models.DateTimeField(default=timezone.now, db_index=True)
    fin = models.DateTimeField(null=True, blank=True)
    exitosa = models.BooleanField(default=True)
    motivo_fallo = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = _("Sesión de acceso")
        verbose_name_plural = _("Sesiones de acceso")
        ordering = ("-inicio",)
        indexes = [models.Index(fields=["usuario", "-inicio"])]
