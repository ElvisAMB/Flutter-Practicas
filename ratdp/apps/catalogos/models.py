"""
apps/catalogos/models.py
========================
Catálogos maestros. Todo lo que el procedimiento PR-PDP-001 pide "elegir de una
lista" vive aquí, para que el cambio normativo se resuelva parametrizando y no
recompilando.

Nota de clasificación: **ninguno de estos modelos contiene datos personales**.
Son metadatos de tratamiento (nombres de áreas, artículos de ley, países,
razones sociales de proveedores). Cifrarlos degradaría búsqueda y orden sin
aportar protección a ningún titular. Ver docs/MANUAL_OPERATIVO.md §9.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.fields import EncryptedCharField
from apps.core.models import ModeloBase


class CatalogoBase(ModeloBase):
    """Estructura común: código, nombre, descripción, activo, orden."""

    codigo = models.SlugField(_("Código"), max_length=32, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=250)
    descripcion = models.TextField(_("Descripción"), blank=True)
    activo = models.BooleanField(_("Activo"), default=True, db_index=True)
    orden = models.PositiveSmallIntegerField(_("Orden"), default=100)

    class Meta:
        abstract = True
        ordering = ("orden", "nombre")

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nombre}"


class Macroproceso(CatalogoBase):
    """Comercial, Suscripción, Cumplimiento, Talento Humano, TI, etc. (§6.2)."""

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Macroproceso")
        verbose_name_plural = _("Macroprocesos")


class Area(CatalogoBase):
    """Unidad organizativa dueña del proceso (campo 3.2)."""

    macroproceso = models.ForeignKey(
        Macroproceso, verbose_name=_("Macroproceso"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="areas",
    )
    cargo_responsable = models.CharField(
        _("Cargo del responsable"), max_length=200, blank=True,
        help_text=_("Se registra el cargo, no el nombre, para que la matriz no caduque "
                    "con la rotación de personal (campo 3.3 del procedimiento)."),
    )
    padre = models.ForeignKey(
        "self", verbose_name=_("Área superior"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="dependientes",
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Área / Unidad organizativa")
        verbose_name_plural = _("Áreas / Unidades organizativas")


class BaseLicitud(CatalogoBase):
    """Numerales del Art. 7 LOPDP (campo 3.6)."""

    numeral = models.PositiveSmallIntegerField(_("Numeral Art. 7 LOPDP"))
    articulo = models.CharField(_("Artículo"), max_length=60, default="Art. 7 LOPDP")
    requiere_test_ponderacion = models.BooleanField(
        _("Exige test de ponderación"), default=False,
        help_text=_("Verdadero para interés legítimo (Art. 7 núm. 8 LOPDP y "
                    "Art. 7 núm. 3 RLOPDP)."),
    )
    requiere_consentimiento = models.BooleanField(_("Exige consentimiento"), default=False)
    equivalencia_rgpd = models.CharField(
        _("Equivalencia RGPD (informativa)"), max_length=120, blank=True,
        help_text=_("Solo informativa para cesiones a matrices o reaseguradores "
                    "europeos. El fundamento registrable es siempre el ecuatoriano."),
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Base de licitud (Art. 7 LOPDP)")
        verbose_name_plural = _("Bases de licitud (Art. 7 LOPDP)")
        ordering = ("numeral",)


class HabilitanteEspecial(CatalogoBase):
    """Literales del Art. 26 LOPDP y regímenes especiales (campo 3.7)."""

    literal = models.CharField(_("Literal"), max_length=8, blank=True)
    articulo = models.CharField(_("Artículo"), max_length=80, default="Art. 26 LOPDP")

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Habilitante para categorías especiales")
        verbose_name_plural = _("Habilitantes para categorías especiales")


class TipoDatoEspecial(models.TextChoices):
    NO_APLICA = "NA", _("No aplica")
    SENSIBLE = "SENSIBLE", _("Dato sensible (Art. 4 / 25 LOPDP)")
    SALUD = "SALUD", _("Datos de salud (Arts. 30–32 LOPDP)")
    BIOMETRICO = "BIOMETRICO", _("Datos biométricos")
    JUDICIAL = "JUDICIAL", _("Pasado judicial")
    CREDITICIO = "CREDITICIO", _("Datos crediticios (Arts. 28–29 LOPDP)")
    MENORES = "MENORES", _("Datos de niñas, niños y adolescentes")
    DISCAPACIDAD = "DISCAPACIDAD", _("Datos de discapacidad")


class CategoriaDato(CatalogoBase):
    """
    Catálogo **cerrado** de categorías de datos (campo 3.8).

    El procedimiento lo pide expresamente: "mantener un catálogo cerrado de
    categorías para que la matriz sea agregable y comparable". Por eso es un
    modelo y no un campo de texto libre.
    """

    tipo_especial = models.CharField(
        _("Tipo de categoría especial"), max_length=16,
        choices=TipoDatoEspecial.choices, default=TipoDatoEspecial.NO_APLICA, db_index=True,
    )
    ejemplos = models.TextField(_("Ejemplos"), blank=True)

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Categoría de datos personales")
        verbose_name_plural = _("Categorías de datos personales")

    @property
    def es_especial(self) -> bool:
        return self.tipo_especial != TipoDatoEspecial.NO_APLICA


class CategoriaTitular(CatalogoBase):
    """Categorías de interesados (campo 3.10)."""

    puede_incluir_menores = models.BooleanField(_("Puede incluir menores"), default=False)

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Categoría de titulares")
        verbose_name_plural = _("Categorías de titulares")


class Pais(models.Model):
    """Países para transferencias internacionales (campo 3.15)."""

    iso2 = models.CharField(_("ISO 3166-1 alfa-2"), max_length=2, primary_key=True)
    nombre = models.CharField(_("Nombre"), max_length=120)
    nivel_adecuado = models.BooleanField(
        _("Nivel adecuado reconocido por la SPDP"), default=False,
        help_text=_("Art. 56 LOPDP / Art. 71 RLOPDP. Verificar resoluciones vigentes."),
    )
    observaciones = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = _("País")
        verbose_name_plural = _("Países")
        ordering = ("nombre",)

    def __str__(self) -> str:
        return self.nombre


class MecanismoTransferencia(CatalogoBase):
    """Mecanismos habilitantes de transferencia internacional (campo 3.15)."""

    articulo = models.CharField(_("Fundamento"), max_length=120, blank=True)
    requiere_autorizacion_spdp = models.BooleanField(default=False)

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Mecanismo de transferencia internacional")
        verbose_name_plural = _("Mecanismos de transferencia internacional")


class RolTercero(models.TextChoices):
    ENCARGADO = "ENCARGADO", _("Encargado (trata por cuenta de la compañía)")
    DESTINATARIO = "DESTINATARIO", _("Destinatario / responsable independiente")
    CORRESPONSABLE = "CORRESPONSABLE", _("Corresponsable (decide conjuntamente)")


class Tercero(ModeloBase):
    """
    Terceros: encargados (3.5), corresponsables (3.4) y destinatarios (3.13).

    Se unifican en un solo modelo porque la distinción es *funcional* y depende
    de quién decide la finalidad; el mismo proveedor puede ser encargado en una
    actividad y destinatario en otra. El rol se fija en la relación, no aquí.
    """

    razon_social = models.CharField(_("Razón social"), max_length=250, db_index=True)
    identificacion = models.CharField(_("RUC / identificación"), max_length=32, blank=True)
    rol_habitual = models.CharField(
        _("Rol habitual"), max_length=16, choices=RolTercero.choices,
        default=RolTercero.ENCARGADO, db_index=True,
    )
    pais = models.ForeignKey(
        Pais, verbose_name=_("País"), null=True, blank=True, on_delete=models.SET_NULL,
    )
    # -- contrato de encargo (Art. 41 RLOPDP) ------------------------------
    tiene_contrato = models.BooleanField(_("Tiene contrato firmado"), default=False)
    codigo_contrato = models.CharField(_("Código de contrato"), max_length=64, blank=True)
    fecha_contrato = models.DateField(_("Fecha de contrato"), null=True, blank=True)
    fecha_vencimiento = models.DateField(_("Vence"), null=True, blank=True)
    clausula_confidencialidad = models.BooleanField(
        _("Cláusula de confidencialidad"), default=False,
        help_text=_("Art. 47 núm. 10 LOPDP."),
    )
    clausulas_art41_completas = models.BooleanField(
        _("Cláusulas completas Art. 41 RLOPDP"), default=False,
        help_text=_("Objeto, duración, naturaleza, finalidad, categorías de datos, "
                    "titulares y obligaciones."),
    )
    subencargados = models.TextField(_("Subencargados declarados"), blank=True)
    # -- contacto (dato personal -> cifrado) -------------------------------
    contacto_nombre = EncryptedCharField(
        _("Contacto"), max_length=512, blank=True, aad_scope="tercero.contacto")
    contacto_email = EncryptedCharField(
        _("Correo de contacto"), max_length=512, blank=True, aad_scope="tercero.email")
    activo = models.BooleanField(_("Activo"), default=True, db_index=True)

    class Meta:
        verbose_name = _("Tercero (encargado / destinatario)")
        verbose_name_plural = _("Terceros (encargados / destinatarios)")
        ordering = ("razon_social",)

    def __str__(self) -> str:
        return self.razon_social

    @property
    def contrato_conforme(self) -> bool:
        """Insumo del indicador '% de encargados con contrato conforme'."""
        return all([
            self.tiene_contrato,
            self.clausula_confidencialidad,
            self.clausulas_art41_completas,
        ])

    @property
    def es_extranjero(self) -> bool:
        return bool(self.pais_id) and self.pais_id != "EC"


class MedidaSeguridad(CatalogoBase):
    """Controles técnicos y organizativos (campo 3.18)."""

    class Tipo(models.TextChoices):
        TECNICA = "TECNICA", _("Técnica")
        ORGANIZATIVA = "ORGANIZATIVA", _("Organizativa")
        FISICA = "FISICA", _("Física")

    tipo = models.CharField(max_length=16, choices=Tipo.choices, default=Tipo.TECNICA, db_index=True)

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Medida de seguridad")
        verbose_name_plural = _("Medidas de seguridad")


class CriterioConservacion(CatalogoBase):
    """Criterios de determinación del plazo (campo 3.17)."""

    norma_referencia = models.CharField(_("Norma de referencia"), max_length=250, blank=True)
    plazo_sugerido_meses = models.PositiveIntegerField(_("Plazo sugerido (meses)"), null=True, blank=True)
    es_limite_imperativo = models.BooleanField(
        _("Límite imperativo"), default=False,
        help_text=_("P. ej. Art. 28 LOPDP: 5 años para comunicación de datos crediticios."),
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Criterio de conservación")
        verbose_name_plural = _("Criterios de conservación")


class SistemaInformacion(CatalogoBase):
    """Inventario de sistemas/repositorios (Fase 1, Paso 2)."""

    class Alojamiento(models.TextChoices):
        ON_PREMISE = "ON_PREMISE", _("On-premise")
        NUBE_EC = "NUBE_EC", _("Nube en Ecuador")
        NUBE_EXT = "NUBE_EXT", _("Nube en el exterior")
        FISICO = "FISICO", _("Archivo físico")

    alojamiento = models.CharField(max_length=16, choices=Alojamiento.choices, default=Alojamiento.ON_PREMISE)
    pais = models.ForeignKey(Pais, null=True, blank=True, on_delete=models.SET_NULL)
    proveedor = models.ForeignKey(Tercero, null=True, blank=True, on_delete=models.SET_NULL, related_name="sistemas")
    contiene_datos_personales = models.BooleanField(default=True)
    ambiente_pruebas_con_datos_reales = models.BooleanField(
        _("Ambiente de pruebas con datos reales"), default=False,
        help_text=_("Mala práctica señalada en el procedimiento (§7.2, TI): exigir disociación."),
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = _("Sistema de información")
        verbose_name_plural = _("Sistemas de información")

    @property
    def implica_transferencia(self) -> bool:
        return self.alojamiento == self.Alojamiento.NUBE_EXT or (
            self.pais_id is not None and self.pais_id != "EC"
        )
