from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

# Create your models here.


# Clase TipoGasto que representa un modelo Django
class TipoGasto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Tipo de gasto"
        verbose_name_plural = "Tipos de gasto"

    def _str_(self):
        return self.nombre


class Gasto(models.Model):
    codigo = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gastos"
    )
    tipo_gasto = models.ForeignKey(
        TipoGasto, on_delete=models.PROTECT, related_name="gastos"
    )
    descripcion = models.CharField(max_length=250)
    costo_previsto = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    costo_real = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    fecha = models.DateField()
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha", "-codigo"]

    def _str_(self):
        return f"{self.codigo} - {self.descripcion}"

    @property
    def diferencia(self):
        return self.costo_real - self.costo_previsto
