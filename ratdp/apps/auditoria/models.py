"""
apps/auditoria/models.py
========================
Bitácora de auditoría: quién accede, consulta, crea, modifica, elimina o
cambia permisos.

Decisiones de rendimiento (esta es la tabla que llega a millones de filas):

*  **PK entero autoincremental (BigAutoField)**, no UUID. Un índice B-Tree
   sobre bigint ocupa ~40 % menos que sobre UUID v4 y no fragmenta la hoja del
   índice por inserción aleatoria.
*  **Sin borrado lógico ni ``updated_at``**: la tabla es *append-only*. Nadie,
   ni el administrador, puede editar un evento desde la aplicación.
*  Los campos por los que se filtra (fecha, usuario, acción, modelo,
   objeto_id) están **en claro e indexados**. Cifrarlos obligaría a traer la
   tabla completa a memoria para filtrar. Ninguno de ellos es dato personal de
   un titular: son metadatos de operación del sistema.
*  El **detalle** (valores anteriores/nuevos) **sí se cifra**, porque puede
   contener datos personales copiados de los campos modificados.
*  **Integridad verificable**: cada fila almacena ``hash_actual =
   SHA-256(hash_anterior || contenido canónico)``. Alterar o borrar una fila
   rompe la cadena y ``manage.py verificar_bitacora`` lo detecta. Esto
   convierte la bitácora en evidencia razonablemente defendible ante la SPDP.
*  **Retención**: ``manage.py purgar_bitacora --dias N`` archiva a fichero
   firmado antes de eliminar; la purga misma queda registrada.
"""

from __future__ import annotations

import hashlib
import json

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.fields import EncryptedTextField

GENESIS_HASH = "0" * 64


class Accion(models.TextChoices):
    LOGIN = "LOGIN", _("Inicio de sesión")
    LOGIN_FALLIDO = "LOGIN_FAIL", _("Intento de acceso fallido")
    LOGOUT = "LOGOUT", _("Cierre de sesión")
    CONSULTA = "CONSULTA", _("Consulta / lectura")
    CREACION = "CREACION", _("Creación")
    MODIFICACION = "MODIFICACION", _("Modificación")
    ELIMINACION = "ELIMINACION", _("Eliminación")
    RESTAURACION = "RESTAURACION", _("Restauración")
    EXPORTACION = "EXPORTACION", _("Exportación de datos")
    CAMBIO_ESTADO = "CAMBIO_ESTADO", _("Cambio de estado")
    CAMBIO_PERMISO = "CAMBIO_PERMISO", _("Cambio de permisos o perfil")
    CAMBIO_PASSWORD = "CAMBIO_PWD", _("Cambio de contraseña")
    ACCESO_DENEGADO = "DENEGADO", _("Acceso denegado")
    ADMIN = "ADMIN", _("Operación administrativa")


class EventoQuerySet(models.QuerySet):
    def de_usuario(self, usuario):
        return self.filter(usuario=usuario)

    def escrituras(self):
        return self.exclude(accion__in=[Accion.CONSULTA, Accion.LOGIN, Accion.LOGOUT])

    def en_rango(self, desde, hasta):
        return self.filter(fecha__gte=desde, fecha__lte=hasta)


class Evento(models.Model):
    """Un registro inmutable de la bitácora."""

    id = models.BigAutoField(primary_key=True)
    fecha = models.DateTimeField(_("Fecha y hora"), default=timezone.now, db_index=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("Usuario"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="eventos_auditoria",
    )
    username = models.CharField(
        _("Usuario (texto)"), max_length=150, blank=True, db_index=True,
        help_text=_("Se conserva aunque el usuario se elimine: la evidencia no puede "
                    "depender de una FK que puede quedar nula."),
    )
    perfil = models.CharField(_("Perfil vigente"), max_length=64, blank=True)

    accion = models.CharField(_("Acción"), max_length=16, choices=Accion.choices, db_index=True)
    modelo = models.CharField(_("Entidad"), max_length=100, blank=True, db_index=True)
    objeto_id = models.CharField(_("Id del objeto"), max_length=64, blank=True, db_index=True)
    objeto_repr = models.CharField(_("Descripción del objeto"), max_length=300, blank=True)

    exitoso = models.BooleanField(_("Exitoso"), default=True, db_index=True)
    ip = models.GenericIPAddressField(_("Dirección IP"), null=True, blank=True, db_index=True)
    user_agent = models.CharField(_("Agente de usuario"), max_length=400, blank=True)
    ruta = models.CharField(_("Ruta"), max_length=300, blank=True)
    metodo = models.CharField(_("Método HTTP"), max_length=8, blank=True)
    session_key = models.CharField(max_length=64, blank=True)

    detalle = EncryptedTextField(
        _("Detalle (cifrado)"), blank=True, aad_scope="auditoria.detalle",
        help_text=_("JSON con los valores anteriores y nuevos. Cifrado porque puede "
                    "contener datos personales."),
    )

    hash_anterior = models.CharField(max_length=64, editable=False, default=GENESIS_HASH)
    hash_actual = models.CharField(max_length=64, editable=False, unique=True, db_index=True)

    objects = EventoQuerySet.as_manager()

    class Meta:
        verbose_name = _("Evento de auditoría")
        verbose_name_plural = _("Bitácora de auditoría")
        ordering = ("-id",)
        indexes = [
            models.Index(fields=["-fecha", "accion"], name="aud_fecha_accion_idx"),
            models.Index(fields=["modelo", "objeto_id", "-fecha"], name="aud_objeto_idx"),
            models.Index(fields=["username", "-fecha"], name="aud_usuario_idx"),
        ]

    def __str__(self) -> str:
        return f"[{self.fecha:%Y-%m-%d %H:%M:%S}] {self.username} {self.accion} {self.modelo}"

    # -- inmutabilidad ----------------------------------------------------
    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise PermissionError(
                "La bitácora es append-only: un evento no puede modificarse."
            )
        if not self.hash_actual:
            self._encadenar()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError(
            "La bitácora es append-only. Use `manage.py purgar_bitacora` para la "
            "retención documentada."
        )

    # -- cadena de integridad ---------------------------------------------
    def _contenido_canonico(self) -> str:
        return json.dumps(
            {
                "fecha": self.fecha.isoformat(),
                "username": self.username,
                "accion": self.accion,
                "modelo": self.modelo,
                "objeto_id": self.objeto_id,
                "objeto_repr": self.objeto_repr,
                "exitoso": self.exitoso,
                "ip": self.ip,
                "ruta": self.ruta,
                "metodo": self.metodo,
            },
            sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        )

    def calcular_hash(self) -> str:
        base = f"{self.hash_anterior}|{self._contenido_canonico()}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def _encadenar(self) -> None:
        ultimo = Evento.objects.order_by("-id").values("hash_actual").first()
        self.hash_anterior = ultimo["hash_actual"] if ultimo else GENESIS_HASH
        self.hash_actual = self.calcular_hash()

    @classmethod
    @transaction.atomic
    def registrar(cls, **kwargs) -> "Evento":
        """
        Punto único de escritura de la bitácora.

        Se serializa con ``select_for_update`` sobre el último evento para
        evitar que dos peticiones concurrentes calculen el mismo
        ``hash_anterior`` y rompan la cadena.
        """
        detalle = kwargs.pop("detalle", None)
        if detalle is not None and not isinstance(detalle, str):
            detalle = json.dumps(detalle, ensure_ascii=False, default=str)
        list(cls.objects.select_for_update().order_by("-id").values_list("id", flat=True)[:1])
        return cls.objects.create(detalle=detalle or "", **kwargs)

    @classmethod
    def verificar_cadena(cls, desde_id: int = 0, hasta_id: int | None = None) -> dict:
        """Recorre la cadena y devuelve el primer punto de ruptura, si existe."""
        qs = cls.objects.filter(id__gt=desde_id).order_by("id")
        if hasta_id:
            qs = qs.filter(id__lte=hasta_id)
        anterior = None
        revisados = 0
        for ev in qs.iterator(chunk_size=2000):
            esperado = GENESIS_HASH if anterior is None else anterior.hash_actual
            if anterior is not None and ev.hash_anterior != esperado:
                return {"ok": False, "evento_id": ev.id, "motivo": "eslabón roto (posible borrado)"}
            if ev.calcular_hash() != ev.hash_actual:
                return {"ok": False, "evento_id": ev.id, "motivo": "contenido alterado"}
            anterior = ev
            revisados += 1
        return {"ok": True, "revisados": revisados}


class PurgaBitacora(models.Model):
    """Registro de las purgas de retención (la purga también se audita)."""

    ejecutada_en = models.DateTimeField(default=timezone.now)
    ejecutada_por = models.CharField(max_length=150)
    desde = models.DateTimeField()
    hasta = models.DateTimeField()
    eventos_archivados = models.BigIntegerField(default=0)
    archivo = models.CharField(max_length=500, blank=True)
    hash_archivo = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = _("Purga de bitácora")
        verbose_name_plural = _("Purgas de bitácora")
        ordering = ("-ejecutada_en",)
