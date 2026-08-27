from django.conf import settings
from django.db import models


class ModeloAuditado(models.Model):
    """Trazabilidad mínima exigible a un RAT: quién y cuándo tocó la fila."""

    creado_en = models.DateTimeField("Creado en", auto_now_add=True)
    actualizado_en = models.DateTimeField("Última actualización", auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_creados", verbose_name="Creado por",
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_actualizados", verbose_name="Actualizado por",
    )

    class Meta:
        abstract = True


class CatalogoBase(ModeloAuditado):
    """
    Base de todos los catálogos parametrizables.

    `codigo` es el identificador estable que se referencia desde la lógica de
    negocio (p. ej. "3.6.8" para interés legítimo). `clave` es un slug interno
    opcional para reglas de validación que no deben depender del texto visible.
    """

    codigo = models.CharField("Código", max_length=30, unique=True)
    nombre = models.CharField("Nombre", max_length=255)
    descripcion = models.TextField("Descripción / ejemplos", blank=True)
    referencia_legal = models.CharField(
        "Referencia legal", max_length=255, blank=True,
        help_text="Artículo de la LOPDP o del RLOPDP que sustenta la opción.",
    )
    clave = models.SlugField(
        "Clave interna", max_length=60, blank=True,
        help_text="Uso técnico. No la modifique si ya hay reglas que dependen de ella.",
    )
    orden = models.PositiveIntegerField("Orden", default=100)
    activo = models.BooleanField(
        "Activo", default=True,
        help_text="Desactive en lugar de borrar: las filas históricas del RAT conservan la referencia.",
    )

    class Meta:
        abstract = True
        ordering = ("orden", "codigo")

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"

    @property
    def etiqueta_corta(self):
        return self.nombre
