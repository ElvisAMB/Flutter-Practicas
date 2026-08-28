from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.catalogos.models import (
    Area,
    BaseLicitud,
    CategoriaDato,
    CategoriaInteresado,
    CriterioEIPD,
    DestinatarioExterno,
    EstadoRegistro,
    HabilitanteEspecial,
    MecanismoTransferencia,
    MedidaSeguridad,
    Pais,
    ProcesoInterno,
    Tercero,
)
from apps.core.models import ModeloAuditado

validador_codigo = RegexValidator(
    r"^[A-Z0-9][A-Z0-9\-\.]{2,29}$",
    "Use mayúsculas, números, guiones y puntos. Ej.: RAT-SUS-01",
)


class ActividadTratamiento(ModeloAuditado):
    """
    Una fila = una finalidad. No un soporte, no una base de datos, no un sistema.

    Si dos finalidades comparten la misma tabla de clientes, siguen siendo dos
    filas: el plazo de conservación, la base de licitud y los destinatarios
    cambian con la finalidad, no con el soporte.
    """

    TRES_ESTADOS = [
        ("SI", "Sí"),
        ("NO", "No / No aplica"),
        ("PEND", "Pendiente de evaluar"),
    ]
    DESTINO_ELIMINACION = "ELIM"
    DESTINO_BLOQUEO = "BLOQ"
    DESTINO_ANONIMIZACION = "ANON"
    DESTINOS_FINALES = [
        (DESTINO_ELIMINACION, "Eliminación segura"),
        (DESTINO_BLOQUEO, "Bloqueo"),
        (DESTINO_ANONIMIZACION, "Anonimización"),
    ]

    # ---------------------------------------------------------- 3.1
    codigo = models.CharField(
        "3.1 Código único",
        max_length=30,
        unique=True,
        validators=[validador_codigo],
        help_text="Ej.: RAT-SUS-01",
    )
    nombre_corto = models.CharField(
        "3.1 Nombre corto de la actividad",
        max_length=180,
        help_text="Ej.: Evaluación de riesgo y capacidad de pago para suscripción de fianzas.",
    )
    finalidad = models.TextField(
        "3.1 Finalidad (una frase)",
        help_text="Para qué se tratan los datos. Una fila por finalidad. "
        "'Base de clientes' no es una finalidad, es un soporte.",
    )

    # ---------------------------------------------------------- 3.2 / 3.3
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        verbose_name="3.2 Área dueña del proceso",
        related_name="actividades",
        help_text="Si intervienen varias, registre la que decide la finalidad; "
        "las demás van en destinatarios internos (3.12).",
    )
    responsable_cargo = models.CharField(
        "3.3 Responsable del área (cargo)",
        max_length=180,
        help_text="Cargo, no nombre propio. El responsable del tratamiento ante la ley es la compañía.",
    )

    # ---------------------------------------------------------- 3.4
    corresponsable_situacion = models.CharField(
        "3.4 ¿Existe corresponsable?",
        max_length=4,
        choices=TRES_ESTADOS,
        default="NO",
        help_text="Solo si otra entidad decide CONJUNTAMENTE fines y medios (Art. 37 RLOPDP). "
        "Un corredor de seguros normalmente NO es corresponsable.",
    )
    corresponsables = models.CharField(
        "3.4 Corresponsables",
        max_length=500,
        blank=True,
        help_text="Razón social de cada entidad que decide conjuntamente fines y medios. "
        "Separe con punto y coma si hay varias.",
    )
    corresponsable_detalle = models.TextField(
        "3.4 Detalle del reparto de tareas",
        blank=True,
        help_text="Contrato que reparte tareas; la responsabilidad es solidaria.",
    )

    # ---------------------------------------------------------- 3.5
    encargados = models.TextField(
        "3.5 Encargados del tratamiento",
        blank=True,
        help_text="Razón social de cada encargado; separe con punto y coma. Tratan datos POR CUENTA "
        "de la compañía y bajo sus instrucciones (Art. 34 LOPDP). Si el tercero decide "
        "para qué usa los datos, es destinatario (3.13), no encargado.",
    )
    encargados_contrato_art41 = models.BooleanField(
        "Contratos de encargo verificados",
        default=False,
        help_text="Todos los encargados listados tienen contrato con las cláusulas del Art. 41 "
        "RLOPDP y acuerdo de confidencialidad (Art. 47 núm. 10 LOPDP).",
    )

    # ---------------------------------------------------------- 3.6
    bases_licitud = models.ManyToManyField(
        BaseLicitud,
        through="BaseLicitudActividad",
        related_name="actividades",
        verbose_name="3.6 Bases de licitud (Art. 7 LOPDP)",
    )
    aplica_art28 = models.BooleanField(
        "3.6 Datos crediticios — Art. 28 LOPDP",
        default=False,
        help_text="Licitud presunta para fines de solvencia patrimonial cuando los datos vienen "
        "de fuentes públicas o del acreedor. Restringido a esa única finalidad.",
    )

    # ---------------------------------------------------------- 3.8 / 3.9
    categorias_datos = models.ManyToManyField(
        CategoriaDato,
        related_name="actividades",
        verbose_name="3.8 Categorías de datos personales",
    )
    datos_especiales = models.BooleanField(
        "3.9 ¿Datos especiales? (Art. 25 LOPDP)",
        default=False,
        help_text="Sensibles, de niñas/niños/adolescentes, de salud o de discapacidad. "
        "El pasado judicial pedido en debida diligencia cuenta.",
    )

    # ---------------------------------------------------------- 3.7
    habilitantes_especiales = models.ManyToManyField(
        HabilitanteEspecial,
        blank=True,
        related_name="actividades",
        verbose_name="3.7 Habilitante para categorías especiales (Art. 26)",
    )
    habilitante_justificacion = models.TextField(
        "3.7 Justificación del habilitante",
        blank=True,
    )

    # ---------------------------------------------------------- 3.10 / 3.11
    categorias_interesados = models.ManyToManyField(
        CategoriaInteresado,
        related_name="actividades",
        verbose_name="3.10 Categorías de interesados (titulares)",
    )
    menores = models.BooleanField(
        "3.11 ¿Datos de menores?",
        default=False,
        help_text="Cargas familiares, beneficiarios de desgravamen, hijos en encuestas o eventos.",
    )
    menores_consentimiento_representante = models.BooleanField(
        "Consentimiento del representante legal verificado",
        default=False,
        help_text="Art. 19 RLOPDP: menores de 15 años. Desde los 15, el adolescente puede consentir.",
    )
    menores_interes_superior = models.BooleanField(
        "Interés superior del niño evaluado (Art. 20 RLOPDP)",
        default=False,
    )
    menores_informacion_representante = models.BooleanField(
        "Información dirigida al representante (Art. 12 LOPDP)",
        default=False,
    )
    menores_sin_decisiones_automatizadas = models.BooleanField(
        "Sin decisiones automatizadas sobre menores (Art. 21 LOPDP)",
        default=False,
    )

    # ---------------------------------------------------------- 3.12
    proceso_interno = models.ForeignKey(
        ProcesoInterno,
        on_delete=models.PROTECT,
        related_name="actividades",
        verbose_name="3.12 Proceso interno",
    )
    destinatarios_internos = models.TextField(
        "3.12 Destinatarios internos (áreas / cargos con acceso)",
        help_text="Criterio de necesidad de conocer. Insumo de la matriz de control de accesos. "
        "Ej.: Suscripción, Comité de Riesgos, Cobranzas, Auditoría Interna.",
    )

    # ---------------------------------------------------------- 3.13
    destinatarios_externos = models.ManyToManyField(
        DestinatarioExterno,
        through="DestinatarioExternoActividad",
        related_name="actividades",
        verbose_name="3.13 Destinatarios externos",
    )

    # ---------------------------------------------------------- 3.14
    transferencia_internacional = models.BooleanField(
        "3.14 ¿Transferencia internacional?",
        default=False,
        help_text="Sí también cuando los datos son ACCESIBLES desde el exterior: nube con "
        "servidores fuera del país, casa matriz, soporte remoto, reaseguro internacional.",
    )

    # ---------------------------------------------------------- 3.16 / 3.17
    plazo_conservacion = models.CharField(
        "3.16 Plazo de conservación",
        max_length=255,
        help_text="Plazo concreto. Ej.: vigencia de la póliza + 10 años de prescripción.",
    )
    criterio_plazo = models.TextField(
        "3.17 Criterio de determinación del plazo",
        help_text="Norma legal expresa (cítela), plazo de prescripción, duración del contrato + "
        "defensa de reclamaciones (Art. 11 núm. 2 RLOPDP) o decisión interna motivada.",
    )
    destino_final = models.CharField(
        "3.17 Destino final de los datos",
        max_length=4,
        choices=DESTINOS_FINALES,
        default=DESTINO_ELIMINACION,
        help_text="Art. 9 RLOPDP.",
    )

    # ---------------------------------------------------------- 3.18
    medidas_seguridad = models.ManyToManyField(
        MedidaSeguridad,
        blank=True,
        related_name="actividades",
        verbose_name="3.18 Medidas técnicas y organizativas",
    )
    medidas_adicionales = models.TextField(
        "3.18 Medidas adicionales",
        blank=True,
        help_text="Describa por referencia a controles. No incluya detalle confidencial "
        "(claves, rutas, configuraciones).",
    )

    # ---------------------------------------------------------- 3.19
    eipd_requerida = models.BooleanField(
        "3.19 ¿EIPD requerida?",
        default=False,
        help_text="Obligatoria y PREVIA al tratamiento (Art. 42 LOPDP, Arts. 29-32 RLOPDP).",
    )
    criterios_eipd = models.ManyToManyField(
        CriterioEIPD,
        blank=True,
        related_name="actividades",
        verbose_name="3.19 Criterios que activan la EIPD",
    )
    eipd_codigo = models.CharField("3.19 Código de la EIPD", max_length=60, blank=True)
    eipd_fecha = models.DateField("3.19 Fecha de la EIPD", null=True, blank=True)
    consulta_spdp = models.BooleanField(
        "Consulta previa a la SPDP",
        default=False,
        help_text="En caso de duda, la Autoridad responde en término de 5 días (Art. 31 RLOPDP).",
    )

    # ---------------------------------------------------------- 3.20
    estado = models.ForeignKey(
        EstadoRegistro,
        on_delete=models.PROTECT,
        related_name="actividades",
        verbose_name="3.20 Estado del registro",
    )
    version = models.PositiveIntegerField("3.20 Versión", default=1)
    fecha_cese = models.DateField(
        "3.20 Fecha de cese",
        null=True,
        blank=True,
        help_text="Obligatoria en estado Histórico/Cesado, para conservar la trazabilidad.",
    )
    fecha_validacion = models.DateField("Fecha de validación", null=True, blank=True)
    validado_por_cargo = models.CharField(
        "Validado por (cargo)",
        max_length=180,
        blank=True,
        help_text="Dueño del proceso y DPD.",
    )
    reportado_registro_nacional = models.BooleanField(
        "Reportado al Registro Nacional",
        default=False,
    )
    observaciones = models.TextField("Observaciones", blank=True)

    class Meta:
        ordering = ("codigo",)
        verbose_name = "Actividad de tratamiento"
        verbose_name_plural = "Actividades de tratamiento"
        permissions = [
            ("validar_actividad", "Puede validar y cambiar el estado de una actividad"),
            ("exportar_rat", "Puede exportar el RAT completo"),
        ]

    def __str__(self):
        return f"{self.codigo} — {self.nombre_corto}"

    def get_absolute_url(self):
        return reverse("rat:actividad_detail", args=[self.pk])

    # ---------------------------------------------------------- validación
    def clean(self):
        errores = {}

        # if (self.corresponsable_situacion == "SI" and not self.corresponsable_detalle.strip()):
        #     errores["corresponsable_detalle"] = ("Si hay corresponsable, describa el reparto de tareas del contrato (Art. 37 RLOPDP).")

        if self.corresponsable_situacion == "SI":
            if not self.corresponsables.strip():
                errores["corresponsables"] = (
                    "Indique la razón social del corresponsable."
                )
            if not self.corresponsable_detalle.strip():
                errores["corresponsable_detalle"] = (
                    "Si hay corresponsable, describa el reparto de tareas del contrato "
                    "(Art. 37 RLOPDP)."
                )

        if self.menores and not self.datos_especiales:
            errores["datos_especiales"] = (
                "Los datos de niñas, niños y adolescentes son categoría especial (Art. 25 LOPDP): "
                "marque 3.9."
            )

        if self.eipd_requerida:
            if not self.eipd_codigo.strip():
                errores["eipd_codigo"] = "Registre el código de la EIPD."
            if not self.eipd_fecha:
                errores["eipd_fecha"] = "Registre la fecha de la EIPD."
            if self.eipd_fecha and self.eipd_fecha > timezone.localdate():
                errores["eipd_fecha"] = (
                    "La EIPD debe ser previa al tratamiento, no futura."
                )

        if self.estado_id:
            if self.estado.es_final and not self.fecha_cese:
                errores["fecha_cese"] = (
                    "Un registro histórico/cesado exige fecha de cese."
                )
            if not self.estado.es_final and self.fecha_cese:
                errores["fecha_cese"] = (
                    "Solo los registros cesados llevan fecha de cese."
                )

        if errores:
            raise ValidationError(errores)

    # ---------------------------------------------------------- utilidades
    @property
    def alertas(self):
        """Señales de calidad del registro. No bloquean; obligan a mirar."""
        avisos = []
        if self.corresponsable_situacion == "PEND":
            avisos.append("Corresponsabilidad pendiente de evaluar (3.4).")
        if self.datos_especiales and not self.habilitantes_especiales.exists():
            avisos.append("Datos especiales sin habilitante del Art. 26 (3.7).")
        if self.transferencia_internacional and not self.transferencias.exists():
            avisos.append(
                "Transferencia internacional marcada sin país ni mecanismo (3.15)."
            )
        if (
            self.transferencia_internacional
            and self.transferencias.filter(registrada_registro_nacional=False).exists()
        ):
            avisos.append(
                "Transferencia no reportada al Registro Nacional (Art. 78 RLOPDP)."
            )
        if self.menores and not all(
            [
                self.menores_consentimiento_representante,
                self.menores_interes_superior,
                self.menores_informacion_representante,
            ]
        ):
            avisos.append("Verificaciones de menores incompletas (3.11).")
        if self.bases_licitud.filter(exige_ponderacion=True).exists():
            if (
                not self.baselicitudactividad_set.filter(base__exige_ponderacion=True)
                .exclude(test_ponderacion="")
                .exists()
            ):
                avisos.append(
                    "Interés legítimo sin test de ponderación documentado (3.6)."
                )
        if not self.medidas_seguridad.exists() and not self.medidas_adicionales.strip():
            avisos.append("Sin medidas de seguridad registradas (3.18).")
        if self.encargados.strip() and not self.encargados_contrato_art41:
            avisos.append("Encargados registrados sin confirmar contrato del Art. 41 RLOPDP (3.5).")
        return avisos

    def registrar_version(self, usuario, estado_anterior=None, nota=""):
        HistorialActividad.objects.create(
            actividad=self,
            version=self.version,
            usuario=usuario,
            estado_anterior=estado_anterior,
            estado_nuevo=self.estado,
            nota=nota,
        )


class BaseLicitudActividad(models.Model):
    """3.6 — cada base seleccionada exige su justificación de una línea."""

    actividad = models.ForeignKey(ActividadTratamiento, on_delete=models.CASCADE)
    base = models.ForeignKey(BaseLicitud, on_delete=models.PROTECT)
    justificacion = models.CharField(
        "Justificación (una línea)",
        max_length=500,
        help_text="Por qué esta base cubre esta finalidad concreta.",
    )
    test_ponderacion = models.TextField(
        "Test de ponderación",
        blank=True,
        help_text="Obligatorio para interés legítimo (Art. 7 núm. 3 RLOPDP): interés perseguido, "
        "necesidad, y por qué no prevalecen los derechos del titular.",
    )

    class Meta:
        unique_together = ("actividad", "base")
        verbose_name = "Base de licitud aplicada"
        verbose_name_plural = "Bases de licitud aplicadas"
        ordering = ("base__orden",)

    def __str__(self):
        return f"{self.actividad.codigo} · {self.base.codigo}"

    def clean(self):
        if (
            self.base_id
            and self.base.exige_ponderacion
            and not self.test_ponderacion.strip()
        ):
            raise ValidationError(
                {
                    "test_ponderacion": "El interés legítimo exige test de ponderación documentado."
                }
            )


class DestinatarioExternoActividad(models.Model):
    """3.13 — cada comunicación externa lleva su fundamento (Art. 33 / Art. 36 LOPDP)."""

    actividad = models.ForeignKey(ActividadTratamiento, on_delete=models.CASCADE)
    destinatario = models.ForeignKey(DestinatarioExterno, on_delete=models.PROTECT)
    fundamento = models.CharField(
        "Fundamento de la comunicación",
        max_length=500,
        help_text="Causal de legitimidad + consentimiento, o excepción del Art. 36 "
        "(obligación legal, requerimiento de autoridad, fuentes públicas, relación "
        "jurídica, urgencia vital, estudios epidemiológicos).",
    )

    class Meta:
        unique_together = ("actividad", "destinatario")
        verbose_name = "Destinatario externo de la actividad"
        verbose_name_plural = "Destinatarios externos de la actividad"
        ordering = ("destinatario__orden",)

    def __str__(self):
        return f"{self.actividad.codigo} · {self.destinatario.codigo}"


class TransferenciaInternacional(models.Model):
    """3.15 — una fila por país destino con su mecanismo habilitante."""

    actividad = models.ForeignKey(
        ActividadTratamiento,
        on_delete=models.CASCADE,
        related_name="transferencias",
    )
    pais = models.ForeignKey(
        Pais, on_delete=models.PROTECT, verbose_name="País destino"
    )
    mecanismo = models.ForeignKey(
        MecanismoTransferencia,
        on_delete=models.PROTECT,
        verbose_name="Mecanismo habilitante",
    )
    detalle = models.CharField(
        "Detalle / instrumento",
        max_length=500,
        blank=True,
        help_text="Ej.: cláusulas tipo avaladas por la Autoridad, contrato de reaseguro, "
        "región de alojamiento del proveedor cloud.",
    )
    destinatario_exterior = models.CharField(
        "Destinatario en el exterior",
        max_length=255,
        blank=True,
    )
    registrada_registro_nacional = models.BooleanField(
        "Registrada en el Registro Nacional",
        default=False,
        help_text="Art. 59 LOPDP / Art. 78 RLOPDP: país, categorías, finalidad, destinatario, mecanismo.",
    )
    fecha_registro = models.DateField("Fecha de registro", null=True, blank=True)

    class Meta:
        verbose_name = "Transferencia internacional"
        verbose_name_plural = "Transferencias internacionales"
        ordering = ("pais__nombre",)

    def __str__(self):
        return f"{self.pais} · {self.mecanismo.codigo}"


class HistorialActividad(models.Model):
    """Bitácora de versiones y cambios de estado."""

    actividad = models.ForeignKey(
        ActividadTratamiento,
        on_delete=models.CASCADE,
        related_name="historial",
    )
    version = models.PositiveIntegerField("Versión")
    fecha = models.DateTimeField("Fecha", auto_now_add=True)
    usuario = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Usuario",
    )
    estado_anterior = models.ForeignKey(
        EstadoRegistro,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Estado anterior",
    )
    estado_nuevo = models.ForeignKey(
        EstadoRegistro,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Estado nuevo",
    )
    nota = models.CharField("Nota del cambio", max_length=500, blank=True)

    class Meta:
        ordering = ("-fecha",)
        verbose_name = "Registro de historial"
        verbose_name_plural = "Historial"

    def __str__(self):
        return f"{self.actividad.codigo} v{self.version}"
