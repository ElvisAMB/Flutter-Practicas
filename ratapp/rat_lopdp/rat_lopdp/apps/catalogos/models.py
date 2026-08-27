from django.db import models

from apps.core.models import CatalogoBase, ModeloAuditado


# ---------------------------------------------------------------- 3.2 / 3.3
class Area(CatalogoBase):
    """Área o unidad organizativa dueña del proceso (organigrama vigente)."""

    responsable_cargo = models.CharField(
        "Cargo del responsable del área", max_length=180, blank=True,
        help_text="Cargo, no nombre propio. Se usa como valor sugerido en el campo 3.3.",
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = "Área / unidad organizativa"
        verbose_name_plural = "Áreas / unidades organizativas"


# ---------------------------------------------------------------- 3.6
class BaseLicitud(CatalogoBase):
    """Bases de licitud del Art. 7 LOPDP."""

    exige_ponderacion = models.BooleanField(
        "Exige test de ponderación", default=False,
        help_text="Interés legítimo: Art. 7 núm. 3 RLOPDP.",
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = "Base de licitud (Art. 7 LOPDP)"
        verbose_name_plural = "Bases de licitud (Art. 7 LOPDP)"


# ---------------------------------------------------------------- 3.7
class HabilitanteEspecial(CatalogoBase):
    """Literales del Art. 26 LOPDP para categorías especiales."""

    class Meta(CatalogoBase.Meta):
        verbose_name = "Habilitante categorías especiales (Art. 26)"
        verbose_name_plural = "Habilitantes categorías especiales (Art. 26)"


# ---------------------------------------------------------------- 3.8
class CategoriaDato(CatalogoBase):
    """Catálogo cerrado de categorías de datos, para que la matriz sea agregable."""

    es_sensible = models.BooleanField(
        "Categoría especial (Art. 25)", default=False,
        help_text="Marcar si la categoría activa por sí sola el campo 3.9.",
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = "Categoría de datos personales"
        verbose_name_plural = "Categorías de datos personales"


# ---------------------------------------------------------------- 3.10
class CategoriaInteresado(CatalogoBase):
    """Categorías de titulares."""

    implica_menores = models.BooleanField(
        "Puede implicar menores", default=False,
        help_text="Sugiere marcar el campo 3.11 cuando se selecciona.",
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = "Categoría de interesados (titulares)"
        verbose_name_plural = "Categorías de interesados (titulares)"


# ---------------------------------------------------------------- 3.12
class ProcesoInterno(CatalogoBase):
    """Proceso interno al que pertenece la actividad (selección única)."""

    class Meta(CatalogoBase.Meta):
        verbose_name = "Proceso interno"
        verbose_name_plural = "Procesos internos"


# ---------------------------------------------------------------- 3.13
class DestinatarioExterno(CatalogoBase):
    """Terceros que reciben datos y deciden su propio uso."""

    es_ninguno = models.BooleanField(
        "Opción 'ninguno'", default=False,
        help_text="Marca la opción que representa ausencia de comunicaciones externas. "
                  "Permite exigir una respuesta explícita sin forzar datos falsos.",
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = "Destinatario externo"
        verbose_name_plural = "Destinatarios externos"


# ---------------------------------------------------------------- 3.15
class Pais(CatalogoBase):
    """País destino de transferencias internacionales."""

    nivel_adecuado = models.BooleanField(
        "Nivel adecuado declarado por la SPDP", default=False,
        help_text="Art. 56 LOPDP / Art. 71 RLOPDP. Verifique la lista vigente de la Autoridad.",
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = "País"
        verbose_name_plural = "Países"


class MecanismoTransferencia(CatalogoBase):
    """Mecanismos habilitantes de transferencia internacional (Arts. 56-60 LOPDP)."""

    requiere_autorizacion_previa = models.BooleanField(
        "Requiere autorización previa de la Autoridad", default=False,
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = "Mecanismo de transferencia internacional"
        verbose_name_plural = "Mecanismos de transferencia internacional"


# ---------------------------------------------------------------- 3.18
class MedidaSeguridad(CatalogoBase):
    """Controles técnicos y organizativos, por referencia (Arts. 37-41 LOPDP)."""

    TIPO_TECNICA = "TEC"
    TIPO_ORGANIZATIVA = "ORG"
    TIPOS = [(TIPO_TECNICA, "Técnica"), (TIPO_ORGANIZATIVA, "Organizativa")]

    tipo = models.CharField("Tipo", max_length=3, choices=TIPOS, default=TIPO_TECNICA)

    class Meta(CatalogoBase.Meta):
        verbose_name = "Medida de seguridad"
        verbose_name_plural = "Medidas de seguridad"


# ---------------------------------------------------------------- 3.19
class CriterioEIPD(CatalogoBase):
    """Supuestos del Art. 42 LOPDP que obligan a una EIPD previa."""

    class Meta(CatalogoBase.Meta):
        verbose_name = "Criterio de EIPD (Art. 42)"
        verbose_name_plural = "Criterios de EIPD (Art. 42)"


# ---------------------------------------------------------------- 3.20
class EstadoRegistro(CatalogoBase):
    """Ciclo de vida de la fila del RAT."""

    es_final = models.BooleanField(
        "Estado final", default=False,
        help_text="Histórico/Cesado: exige fecha de cese y bloquea edición de contenido.",
    )
    es_vigente = models.BooleanField("Cuenta como vigente", default=False)
    color = models.CharField(
        "Color del distintivo", max_length=20, default="secondary",
        help_text="Clase de color de Bootstrap: primary, success, warning, danger, secondary, info.",
    )

    class Meta(CatalogoBase.Meta):
        verbose_name = "Estado del registro"
        verbose_name_plural = "Estados del registro"


# ---------------------------------------------------------------- 3.4 / 3.5
class Tercero(ModeloAuditado):
    """
    Terceros con los que se comparte tratamiento.

    La distinción encargado / corresponsable no es una etiqueta administrativa:
    determina el contrato exigible (Art. 41 RLOPDP vs. Art. 37 RLOPDP) y el
    régimen de responsabilidad. Por eso vive en un modelo propio y no en texto libre.
    """

    ROL_ENCARGADO = "ENC"
    ROL_CORRESPONSABLE = "COR"
    ROLES = [
        (ROL_ENCARGADO, "Encargado del tratamiento (Art. 34 LOPDP)"),
        (ROL_CORRESPONSABLE, "Corresponsable / responsable conjunto (Art. 37 RLOPDP)"),
    ]

    razon_social = models.CharField("Razón social", max_length=255)
    identificacion = models.CharField("RUC / identificación", max_length=30, blank=True)
    rol = models.CharField("Rol", max_length=3, choices=ROLES, default=ROL_ENCARGADO)
    pais = models.ForeignKey(
        Pais, null=True, blank=True, on_delete=models.PROTECT,
        verbose_name="País de establecimiento", related_name="terceros",
    )
    servicio = models.CharField(
        "Servicio prestado", max_length=255, blank=True,
        help_text="Ej.: infraestructura en la nube, cobranza, nómina, SaaS de suscripción.",
    )
    contrato_suscrito = models.BooleanField("Contrato suscrito", default=False)
    contrato_referencia = models.CharField("Referencia del contrato", max_length=120, blank=True)
    contrato_fecha = models.DateField("Fecha del contrato", null=True, blank=True)
    clausulas_art41 = models.BooleanField(
        "Cláusulas del Art. 41 RLOPDP verificadas", default=False,
        help_text="Objeto, duración, naturaleza, finalidad, categorías de datos, titulares y obligaciones.",
    )
    confidencialidad = models.BooleanField(
        "Acuerdo de confidencialidad", default=False,
        help_text="Art. 47 núm. 10 LOPDP.",
    )
    reparto_responsabilidades = models.TextField(
        "Reparto de tareas (solo corresponsables)", blank=True,
        help_text="Art. 37 RLOPDP: el contrato debe repartir tareas; la responsabilidad es solidaria.",
    )
    activo = models.BooleanField("Activo", default=True)
    notas = models.TextField("Notas", blank=True)

    class Meta:
        ordering = ("razon_social",)
        verbose_name = "Tercero (encargado / corresponsable)"
        verbose_name_plural = "Terceros (encargados / corresponsables)"

    def __str__(self):
        return f"{self.razon_social} ({self.get_rol_display().split('(')[0].strip()})"

    @property
    def contrato_completo(self):
        return self.contrato_suscrito and self.clausulas_art41 and self.confidencialidad
