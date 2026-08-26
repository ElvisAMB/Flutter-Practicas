"""
apps/plantillas/models.py
=========================
Plantillas reutilizables y extensibles.

Objetivo del requisito «agregar plantillas para usos futuros»: que la
organización pueda incorporar nuevos formularios e informes (EIPD, test de
ponderación, aviso de privacidad, contrato de encargo, notificación de
vulneración, cuestionarios por área) **sin tocar el código**.

Mecanismo: una plantilla es (a) un cuerpo en Django Template Language que se
renderiza con contexto controlado, y (b) opcionalmente un ``esquema_campos``
JSON que la interfaz convierte en formulario dinámico.

Seguridad: el renderizado usa un ``Engine`` aislado con autoescape activo y
**sin acceso a builtins ni a etiquetas de carga arbitraria**. Una plantilla es
contenido editable por usuarios privilegiados; tratarla como código de
confianza sería una vía de escalamiento.
"""

from __future__ import annotations

from django.db import models
from django.template import Context, Engine, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _

from apps.core.fields import EncryptedTextField
from apps.core.models import ModeloBase

_ENGINE = Engine(debug=False, autoescape=True, libraries={}, builtins=[])


class TipoPlantilla(models.TextChoices):
    CUESTIONARIO = "CUESTIONARIO", _("Cuestionario de levantamiento")
    EIPD = "EIPD", _("Evaluación de impacto (EIPD)")
    TEST_PONDERACION = "TEST_POND", _("Test de ponderación de interés legítimo")
    AVISO_PRIVACIDAD = "AVISO", _("Aviso / política de privacidad")
    CONTRATO_ENCARGO = "CONTRATO", _("Contrato de encargo (Art. 41 RLOPDP)")
    NOTIF_VULNERACION = "VULNERACION", _("Notificación de vulneración (Arts. 43–46)")
    ACTA = "ACTA", _("Acta de entrevista")
    INFORME = "INFORME", _("Informe / reporte")
    CORREO = "CORREO", _("Correo o notificación")
    OTRO = "OTRO", _("Otro")


class Plantilla(ModeloBase):
    codigo = models.SlugField(_("Código"), max_length=64, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=200)
    tipo = models.CharField(
        _("Tipo"), max_length=16, choices=TipoPlantilla.choices,
        default=TipoPlantilla.OTRO, db_index=True,
    )
    descripcion = models.TextField(_("Descripción"), blank=True)
    cuerpo = models.TextField(
        _("Cuerpo (Django Template Language)"),
        help_text=_("Variables disponibles: {{ actividad }}, {{ area }}, {{ usuario }}, "
                    "{{ fecha }}, {{ organizacion }} y las claves de esquema_campos."),
    )
    esquema_campos = models.JSONField(
        _("Esquema de campos"), default=list, blank=True,
        help_text=_('Lista de objetos: [{"nombre":"riesgo","etiqueta":"Riesgo identificado",'
                    '"tipo":"texto","requerido":true}]. Tipos: texto, area, numero, fecha, '
                    'booleano, seleccion.'),
    )
    version = models.CharField(_("Versión"), max_length=16, default="1.0")
    activa = models.BooleanField(_("Activa"), default=True, db_index=True)
    es_sistema = models.BooleanField(
        _("Plantilla base del sistema"), default=False,
        help_text=_("Las plantillas base no se eliminan; se clonan para adaptarlas."),
    )

    class Meta:
        verbose_name = _("Plantilla")
        verbose_name_plural = _("Plantillas")
        ordering = ("tipo", "codigo")

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nombre} (v{self.version})"

    def validar(self) -> None:
        try:
            _ENGINE.from_string(self.cuerpo)
        except TemplateSyntaxError as exc:
            raise ValueError(f"Error de sintaxis en la plantilla: {exc}") from exc

    def renderizar(self, contexto: dict | None = None) -> str:
        self.validar()
        return _ENGINE.from_string(self.cuerpo).render(Context(contexto or {}))

    def clonar(self, nuevo_codigo: str, usuario=None) -> "Plantilla":
        return Plantilla.objects.create(
            codigo=nuevo_codigo, nombre=f"{self.nombre} (copia)", tipo=self.tipo,
            descripcion=self.descripcion, cuerpo=self.cuerpo,
            esquema_campos=self.esquema_campos, version="1.0",
            es_sistema=False, creado_por=usuario,
        )


class DocumentoGenerado(ModeloBase):
    """Instancia rellenada de una plantilla, ligada opcionalmente a una fila RAT."""

    plantilla = models.ForeignKey(Plantilla, on_delete=models.PROTECT, related_name="documentos")
    actividad = models.ForeignKey(
        "rat.ActividadTratamiento", null=True, blank=True, on_delete=models.CASCADE,
        related_name="documentos",
    )
    codigo = models.CharField(_("Código del documento"), max_length=64, unique=True)
    titulo = models.CharField(_("Título"), max_length=250)
    datos = models.JSONField(_("Datos del formulario"), default=dict, blank=True)
    contenido = EncryptedTextField(_("Contenido renderizado"), blank=True, aad_scope="plantillas.documento")
    aprobado = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Documento generado")
        verbose_name_plural = _("Documentos generados")
        ordering = ("-creado_en",)

    def __str__(self) -> str:
        return f"{self.codigo} — {self.titulo}"
