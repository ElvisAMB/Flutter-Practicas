"""
apps/core/models.py
===================
Piezas reutilizables por todas las aplicaciones del proyecto.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .fields import BlindIndexField


class BlindIndexMixin(models.Model):
    """Recalcula todos los ``BlindIndexField`` del modelo antes de guardar."""

    class Meta:
        abstract = True

    def _refrescar_indices_ciegos(self) -> None:
        for field in self._meta.get_fields():
            if isinstance(field, BlindIndexField):
                setattr(self, field.attname, field.calcular(self))

    def save(self, *args, **kwargs):
        self._refrescar_indices_ciegos()
        if "update_fields" in kwargs and kwargs["update_fields"]:
            campos = set(kwargs["update_fields"])
            for field in self._meta.get_fields():
                if isinstance(field, BlindIndexField) and field.source in campos:
                    campos.add(field.attname)
            kwargs["update_fields"] = list(campos)
        return super().save(*args, **kwargs)


class TimeStampedModel(models.Model):
    """Marcas de tiempo y trazabilidad de autoría en toda entidad."""

    creado_en = models.DateTimeField("Creado en", default=timezone.now, editable=False, db_index=True)
    actualizado_en = models.DateTimeField("Actualizado en", auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Creado por", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+", editable=False,
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Actualizado por", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+", editable=False,
    )

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def vivos(self):
        return self.filter(eliminado_en__isnull=True)

    def eliminados(self):
        return self.filter(eliminado_en__isnull=False)

    def delete(self):  # borrado lógico masivo
        return self.update(eliminado_en=timezone.now())


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(eliminado_en__isnull=True)


class SoftDeleteModel(models.Model):
    """
    Borrado lógico. Requisito normativo implícito: el procedimiento exige
    conservar la fila del RAT con fecha de cese para trazabilidad
    (campo 3.20, estado 'Histórico/Cesado'). Un DELETE físico destruiría la
    evidencia de responsabilidad proactiva (Art. 10 lit. k LOPDP).
    """

    eliminado_en = models.DateTimeField("Eliminado en", null=True, blank=True, editable=False, db_index=True)
    eliminado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Eliminado por", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+", editable=False,
    )

    objects = SoftDeleteManager()
    todos = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def esta_eliminado(self) -> bool:
        return self.eliminado_en is not None

    def delete(self, using=None, keep_parents=False, usuario=None):
        self.eliminado_en = timezone.now()
        self.eliminado_por = usuario
        self.save(update_fields=["eliminado_en", "eliminado_por", "actualizado_en"])

    def restaurar(self):
        self.eliminado_en = None
        self.eliminado_por = None
        self.save(update_fields=["eliminado_en", "eliminado_por", "actualizado_en"])

    def borrar_definitivo(self, using=None):
        return super().delete(using=using)


class UUIDModel(models.Model):
    """
    Identificador público UUID además del PK entero.

    El PK entero se conserva porque los índices B-Tree sobre enteros son
    sustancialmente más compactos que sobre UUID v4 (relevante en la tabla de
    auditoría, que es la que llega a millones de filas). El UUID se usa solo
    en URLs para evitar enumeración.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    class Meta:
        abstract = True


class ModeloBase(UUIDModel, TimeStampedModel, SoftDeleteModel, BlindIndexMixin):
    """Modelo base recomendado para toda entidad de negocio."""

    class Meta:
        abstract = True
