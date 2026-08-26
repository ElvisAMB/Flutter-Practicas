"""
apps/rat/models.py
==================
Matriz de Registro de Actividades de Tratamiento (Arts. 38–39 RLOPDP).

Correspondencia con el procedimiento PR-PDP-001 §8: cada campo del modelo
lleva en su ``help_text`` la referencia al numeral 3.x correspondiente, de modo
que la interfaz se autodocumenta y el manual no se desactualiza respecto al
código.

Regla estructural: **una finalidad = una fila**. La restricción se apoya en el
campo ``finalidad`` (obligatorio) y en la unicidad del ``codigo``.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.catalogos.models import TipoDatoEspecial
from apps.core.fields import EncryptedTextField
from apps.core.models import ModeloBase, SoftDeleteManager, SoftDeleteQuerySet


class EstadoRegistro(models.TextChoices):
    """Campo 3.20 — ciclo de vida de la fila."""

    BORRADOR = "BORRADOR", _("Borrador")
    EN_VALIDACION = "EN_VALIDACION", _("En validación")
    VALIDADO = "VALIDADO", _("Validado")
    VIGENTE = "VIGENTE", _("Vigente / Publicado")
    CON_BRECHAS = "CON_BRECHAS", _("Con brechas")
    EN_REVISION = "EN_REVISION", _("En revisión")
    HISTORICO = "HISTORICO", _("Histórico / Cesado")


#: Transiciones permitidas del flujo de estados. Cualquier otra se rechaza en
#: ``ActividadTratamiento.cambiar_estado``.
TRANSICIONES = {
    EstadoRegistro.BORRADOR: {EstadoRegistro.EN_VALIDACION, EstadoRegistro.HISTORICO},
    EstadoRegistro.EN_VALIDACION: {EstadoRegistro.VALIDADO, EstadoRegistro.CON_BRECHAS, EstadoRegistro.BORRADOR},
    EstadoRegistro.CON_BRECHAS: {EstadoRegistro.EN_VALIDACION, EstadoRegistro.HISTORICO},
    EstadoRegistro.VALIDADO: {EstadoRegistro.VIGENTE, EstadoRegistro.EN_REVISION, EstadoRegistro.CON_BRECHAS},
    EstadoRegistro.VIGENTE: {EstadoRegistro.EN_REVISION, EstadoRegistro.HISTORICO},
    EstadoRegistro.EN_REVISION: {EstadoRegistro.VALIDADO, EstadoRegistro.VIGENTE, EstadoRegistro.CON_BRECHAS},
    EstadoRegistro.HISTORICO: set(),
}


class SiNo(models.TextChoices):
    SI = "SI", _("Sí")
    NO = "NO", _("No")
    NA = "NA", _("No aplica")
    NO_EVALUADO = "NE", _("No evaluado")


class ActividadQuerySet(SoftDeleteQuerySet):
    # Hereda de SoftDeleteQuerySet a proposito: sobrescribir el manager sin
    # heredarlo dejaria visibles en los listados las filas dadas de baja.
    def vigentes(self):
        return self.filter(estado=EstadoRegistro.VIGENTE)

    def con_datos_especiales(self):
        return self.filter(datos_especiales=SiNo.SI)

    def con_transferencia_internacional(self):
        return self.filter(transferencia_internacional=SiNo.SI)

    def eipd_pendiente(self):
        return self.filter(eipd_requerida=SiNo.SI, eipd_codigo="")

    def desactualizadas(self, dias: int = 365):
        limite = timezone.now() - timezone.timedelta(days=dias)
        return self.filter(fecha_ultima_revision__lt=limite.date())


class ActividadTratamiento(ModeloBase):
    """Una fila de la matriz RAT."""

    objects = SoftDeleteManager.from_queryset(ActividadQuerySet)()
    todos = ActividadQuerySet.as_manager()

    # ---------------- 3.1 Identificación --------------------------------
    codigo = models.CharField(
        _("3.1 Código"), max_length=32, unique=True, db_index=True,
        help_text=_("Formato sugerido RAT-<ÁREA>-<NN>. Ej.: RAT-SUS-01."),
    )
    nombre = models.CharField(
        _("3.1 Actividad / Proceso de tratamiento"), max_length=300, db_index=True,
        help_text=_("Acción + finalidad. Correcto: «Evaluación de riesgo y capacidad de "
                    "pago para suscripción». Incorrecto: «Base de clientes» (eso es un soporte)."),
    )
    finalidad = models.TextField(
        _("Finalidad concreta"),
        help_text=_("Una sola finalidad por fila, con verbos concretos: evaluar, emitir, "
                    "cobrar, reportar. Si necesita tres bases legales distintas, "
                    "probablemente son tres actividades."),
    )

    # ---------------- 3.2 / 3.3 Área y responsable ----------------------
    area = models.ForeignKey(
        "catalogos.Area", verbose_name=_("3.2 Área / Unidad organizativa"),
        on_delete=models.PROTECT, related_name="actividades",
        help_text=_("Área que decide la finalidad. Las demás van en 3.12."),
    )
    cargo_responsable = models.CharField(
        _("3.3 Responsable del área (cargo)"), max_length=200,
        help_text=_("Cargo, no nombre propio, para que la matriz no caduque con la rotación."),
    )

    # ---------------- 3.4 / 3.5 Terceros --------------------------------
    corresponsables = models.ManyToManyField(
        "catalogos.Tercero", verbose_name=_("3.4 Corresponsables"), blank=True,
        related_name="actividades_corresponsable",
        help_text=_("Solo si otra entidad decide CONJUNTAMENTE fines y medios "
                    "(Art. 37 RLOPDP). Un corredor normalmente NO es corresponsable."),
    )
    encargados = models.ManyToManyField(
        "catalogos.Tercero", verbose_name=_("3.5 Encargados de tratamiento"), blank=True,
        related_name="actividades_encargado",
        help_text=_("Terceros que tratan datos POR CUENTA de la compañía (Art. 34 LOPDP). "
                    "Si el tercero decide para qué usa los datos, va en 3.13."),
    )

    # ---------------- 3.6 Base de licitud -------------------------------
    bases_licitud = models.ManyToManyField(
        "catalogos.BaseLicitud", verbose_name=_("3.6 Base de licitud (Art. 7 LOPDP)"),
        related_name="actividades",
    )
    justificacion_base_licitud = models.TextField(
        _("Justificación de la base de licitud"),
        help_text=_("Una línea por numeral invocado. Para datos crediticios añada la "
                    "referencia al Art. 28 LOPDP."),
    )
    test_ponderacion_codigo = models.CharField(
        _("Código del test de ponderación"), max_length=64, blank=True,
        help_text=_("Obligatorio si invoca interés legítimo (Art. 7 núm. 3 RLOPDP). "
                    "Ej.: TP-2026-01."),
    )

    # ---------------- 3.7 / 3.9 Categorías especiales -------------------
    datos_especiales = models.CharField(
        _("3.9 ¿Datos especiales?"), max_length=2, choices=SiNo.choices,
        default=SiNo.NO_EVALUADO, db_index=True,
    )
    tipos_dato_especial = models.JSONField(
        _("Tipos de dato especial"), default=list, blank=True,
        help_text=_("Trazabilidad fina: SENSIBLE, SALUD, BIOMETRICO, JUDICIAL, "
                    "CREDITICIO, MENORES, DISCAPACIDAD."),
    )
    habilitantes_especiales = models.ManyToManyField(
        "catalogos.HabilitanteEspecial", verbose_name=_("3.7 Habilitante (Art. 26 LOPDP)"),
        blank=True, related_name="actividades",
    )

    # ---------------- 3.8 Categorías de datos ---------------------------
    categorias_datos = models.ManyToManyField(
        "catalogos.CategoriaDato", verbose_name=_("3.8 Categorías de datos personales"),
        related_name="actividades",
    )

    # ---------------- 3.10 / 3.11 Titulares -----------------------------
    categorias_titulares = models.ManyToManyField(
        "catalogos.CategoriaTitular", verbose_name=_("3.10 Categorías de interesados"),
        related_name="actividades",
    )
    menores = models.CharField(
        _("3.11 ¿Datos de menores?"), max_length=2, choices=SiNo.choices,
        default=SiNo.NO_EVALUADO, db_index=True,
    )
    menores_detalle = models.CharField(
        _("Detalle de menores"), max_length=300, blank=True,
        help_text=_("Si SÍ: verificar consentimiento del representante legal "
                    "(Art. 19 RLOPDP) y prohibición reforzada de decisiones "
                    "automatizadas (Art. 21 LOPDP)."),
    )

    # ---------------- 3.12 / 3.13 Destinatarios -------------------------
    destinatarios_internos = models.ManyToManyField(
        "catalogos.Area", verbose_name=_("3.12 Destinatarios internos"), blank=True,
        related_name="actividades_receptoras",
        help_text=_("Insumo directo de la matriz de control de accesos."),
    )
    destinatarios_externos = models.ManyToManyField(
        "catalogos.Tercero", verbose_name=_("3.13 Destinatarios externos"), blank=True,
        related_name="actividades_destinatario",
    )
    fundamento_comunicacion = models.TextField(
        _("Fundamento de la comunicación a terceros"), blank=True,
        help_text=_("Art. 33 LOPDP (causal + consentimiento) o excepciones del Art. 36."),
    )

    # ---------------- 3.14 / 3.15 Transferencia internacional -----------
    transferencia_internacional = models.CharField(
        _("3.14 ¿Transferencia internacional?"), max_length=2, choices=SiNo.choices,
        default=SiNo.NO_EVALUADO, db_index=True,
        help_text=_("SÍ si los datos salen del Ecuador O son accesibles desde el "
                    "exterior. La nube extranjera cuenta aunque «solo almacene»."),
    )
    paises_destino = models.ManyToManyField(
        "catalogos.Pais", verbose_name=_("3.15 Países destino"), blank=True,
        related_name="actividades",
    )
    mecanismos_transferencia = models.ManyToManyField(
        "catalogos.MecanismoTransferencia", verbose_name=_("3.15 Mecanismos habilitantes"),
        blank=True, related_name="actividades",
    )
    garantias_detalle = models.TextField(
        _("Detalle de garantías"), blank=True,
        help_text=_("Ej.: «Alemania — contrato de reaseguro con anexo DP-2025». "
                    "No cite solo «SCC/BCR»: son figuras del RGPD."),
    )
    reportada_registro_nacional = models.BooleanField(
        _("Reportada al Registro Nacional"), default=False,
        help_text=_("Art. 51 LOPDP y Art. 86 RLOPDP: término de 10 días desde el "
                    "inicio del tratamiento."),
    )
    fecha_reporte_registro_nacional = models.DateField(null=True, blank=True)

    # ---------------- 3.16 / 3.17 Conservación --------------------------
    plazo_conservacion = models.CharField(
        _("3.16 Plazo de conservación"), max_length=300,
        help_text=_("Plazo concreto desde un hito verificable. Evite «indefinido»."),
    )
    plazo_meses = models.PositiveIntegerField(
        _("Plazo en meses (normalizado)"), null=True, blank=True,
        help_text=_("Permite calcular indicadores y alertas de depuración."),
    )
    criterio_conservacion = models.ForeignKey(
        "catalogos.CriterioConservacion", verbose_name=_("3.17 Criterio de determinación"),
        null=True, blank=True, on_delete=models.SET_NULL, related_name="actividades",
    )
    criterio_detalle = models.TextField(_("Detalle del criterio"), blank=True)

    class DestinoFinal(models.TextChoices):
        ELIMINACION = "ELIMINACION", _("Eliminación segura")
        BLOQUEO = "BLOQUEO", _("Bloqueo")
        ANONIMIZACION = "ANONIMIZACION", _("Anonimización")

    destino_final = models.CharField(
        _("Destino final del dato"), max_length=16, choices=DestinoFinal.choices,
        blank=True, help_text=_("Art. 9 RLOPDP."),
    )

    # ---------------- 3.18 Seguridad ------------------------------------
    medidas_seguridad = models.ManyToManyField(
        "catalogos.MedidaSeguridad", verbose_name=_("3.18 Medidas de seguridad"),
        blank=True, related_name="actividades",
    )
    medidas_detalle = EncryptedTextField(
        _("Detalle de medidas (confidencial)"), blank=True,
        aad_scope="rat.medidas_detalle",
        help_text=_("Cifrado: el detalle de controles es información de seguridad "
                    "cuya divulgación facilitaría un ataque. El procedimiento §3.18 "
                    "pide describir «por referencia a controles, no en detalle confidencial»."),
    )
    sistemas = models.ManyToManyField(
        "catalogos.SistemaInformacion", verbose_name=_("Sistemas/soportes"), blank=True,
        related_name="actividades",
    )

    # ---------------- 3.19 EIPD -----------------------------------------
    eipd_requerida = models.CharField(
        _("3.19 ¿EIPD requerida?"), max_length=2, choices=SiNo.choices,
        default=SiNo.NO_EVALUADO, db_index=True,
    )
    eipd_codigo = models.CharField(_("Código de la EIPD"), max_length=64, blank=True)
    eipd_fecha = models.DateField(_("Fecha de la EIPD"), null=True, blank=True)

    decision_automatizada = models.BooleanField(
        _("¿Decisión automatizada / scoring?"), default=False, db_index=True,
        help_text=_("Si es SÍ con efectos jurídicos, la EIPD es obligatoria y PREVIA "
                    "(Art. 42 lit. a LOPDP) e informa el derecho del Art. 20."),
    )
    intervencion_humana = models.BooleanField(_("Existe intervención humana en la decisión"), default=True)
    gran_escala = models.BooleanField(
        _("¿Tratamiento a gran escala?"), default=False,
        help_text=_("Criterios del Art. 4 núm. 7 RLOPDP y MTGE de la SPDP."),
    )

    # ---------------- 3.20 Estado ---------------------------------------
    estado = models.CharField(
        _("3.20 Estado del registro"), max_length=16, choices=EstadoRegistro.choices,
        default=EstadoRegistro.BORRADOR, db_index=True,
    )
    version = models.CharField(_("Versión"), max_length=16, default="1.0")
    fecha_inicio_tratamiento = models.DateField(_("Inicio del tratamiento"), null=True, blank=True)
    fecha_cese = models.DateField(_("Fecha de cese"), null=True, blank=True)
    fecha_ultima_revision = models.DateField(_("Última revisión"), null=True, blank=True, db_index=True)
    validado_por = models.ForeignKey(
        "accounts.Usuario", verbose_name=_("Validado por"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="actividades_validadas",
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    observaciones = EncryptedTextField(
        _("Observaciones"), blank=True, aad_scope="rat.observaciones",
        help_text=_("Campo libre: puede contener nombres de personas mencionadas en "
                    "entrevistas, por lo que se cifra por precaución."),
    )

    class Meta:
        verbose_name = _("Actividad de tratamiento")
        verbose_name_plural = _("Actividades de tratamiento (RAT)")
        ordering = ("codigo",)
        indexes = [
            models.Index(fields=["estado", "area"]),
            models.Index(fields=["datos_especiales", "estado"]),
            models.Index(fields=["transferencia_internacional"]),
            models.Index(fields=["-actualizado_en"]),
        ]
        permissions = [
            ("validar_actividad", _("Puede validar actividades de tratamiento")),
            ("publicar_actividad", _("Puede publicar (poner vigente) actividades")),
            ("exportar_rat", _("Puede exportar la matriz RAT")),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nombre}"

    def get_absolute_url(self) -> str:
        return reverse("rat:detalle", args=[self.uuid])

    # ---------------- reglas de negocio ---------------------------------
    def clean(self):
        errores = {}

        if self.datos_especiales == SiNo.SI and self.pk and not self.habilitantes_especiales.exists():
            errores["habilitantes_especiales"] = _(
                "Si 3.9 = SÍ, el campo 3.7 (habilitante Art. 26 LOPDP) es obligatorio."
            )

        if self.transferencia_internacional == SiNo.SI and self.pk:
            if not self.paises_destino.exists():
                errores["paises_destino"] = _("Indique al menos un país destino (3.15).")
            if not self.mecanismos_transferencia.exists():
                errores["mecanismos_transferencia"] = _(
                    "Indique el mecanismo habilitante conforme a los Arts. 56–60 LOPDP."
                )

        if self.decision_automatizada and self.eipd_requerida == SiNo.NO:
            errores["eipd_requerida"] = _(
                "El perfilamiento con efectos jurídicos exige EIPD previa "
                "(Art. 42 lit. a LOPDP). No puede marcarse NO."
            )

        if self.eipd_requerida == SiNo.SI and self.estado == EstadoRegistro.VIGENTE and not self.eipd_codigo:
            errores["eipd_codigo"] = _(
                "No puede publicarse una actividad con EIPD requerida sin el código "
                "del informe: la evaluación es PREVIA al tratamiento."
            )

        if self.estado == EstadoRegistro.HISTORICO and not self.fecha_cese:
            errores["fecha_cese"] = _("Toda actividad histórica requiere fecha de cese.")

        if errores:
            raise ValidationError(errores)

    def cambiar_estado(self, nuevo: str, usuario=None, motivo: str = "") -> None:
        actual = EstadoRegistro(self.estado)
        if nuevo == actual:
            return
        if nuevo not in TRANSICIONES[actual]:
            raise ValidationError(
                _("Transición no permitida: %(a)s → %(b)s.") % {"a": actual.label, "b": EstadoRegistro(nuevo).label}
            )
        anterior = self.estado
        self.estado = nuevo
        if nuevo == EstadoRegistro.VALIDADO:
            self.validado_por = usuario
            self.fecha_validacion = timezone.now()
        if nuevo in (EstadoRegistro.VIGENTE, EstadoRegistro.VALIDADO):
            self.fecha_ultima_revision = timezone.localdate()
        self.full_clean(exclude=["creado_por", "actualizado_por"])
        self.save()
        HistorialEstado.objects.create(
            actividad=self, estado_anterior=anterior, estado_nuevo=nuevo,
            usuario=usuario, motivo=motivo,
        )

    # ---------------- señales de alerta (§6.3) ---------------------------
    @property
    def alertas(self) -> list[str]:
        """Semáforo de cumplimiento mostrado en el detalle y en indicadores."""
        avisos = []
        if self.datos_especiales == SiNo.NO_EVALUADO:
            avisos.append("Campo 3.9 sin evaluar: el blanco no distingue «no aplica» de «no evaluado».")
        if self.transferencia_internacional == SiNo.NO_EVALUADO:
            avisos.append("Campo 3.14 sin evaluar: consulte a TI la región de alojamiento de la nube.")
        if self.eipd_requerida == SiNo.SI and not self.eipd_codigo:
            avisos.append("EIPD requerida sin informe registrado (Art. 42 LOPDP: es previa).")
        if self.decision_automatizada and not self.intervencion_humana:
            avisos.append("Decisión totalmente automatizada: verifique el derecho del Art. 20 LOPDP.")
        if TipoDatoEspecial.CREDITICIO in (self.tipos_dato_especial or []):
            avisos.append("Datos crediticios: no comunicar obligaciones con más de 5 años "
                          "de exigibilidad (Art. 28 LOPDP, límite imperativo).")
        if self.pk:
            sin_contrato = self.encargados.filter(tiene_contrato=False)
            if sin_contrato.exists():
                avisos.append(f"{sin_contrato.count()} encargado(s) sin contrato conforme "
                              f"al Art. 41 RLOPDP.")
        if not self.plazo_conservacion or "indefinid" in self.plazo_conservacion.lower():
            avisos.append("Plazo de conservación indefinido: incompatible con el Art. 10 lit. i LOPDP.")
        if self.fecha_ultima_revision:
            dias = (timezone.localdate() - self.fecha_ultima_revision).days
            if dias > 365:
                avisos.append(f"Sin revisión desde hace {dias} días (revisión mínima anual).")
        else:
            avisos.append("Nunca revisada formalmente.")
        if (self.estado == EstadoRegistro.VIGENTE and self.fecha_inicio_tratamiento
                and not self.reportada_registro_nacional):
            avisos.append("Vigente y no reportada al Registro Nacional (término de 10 días, Art. 86 RLOPDP).")
        return avisos

    @property
    def nivel_riesgo(self) -> str:
        puntos = 0
        puntos += 2 if self.datos_especiales == SiNo.SI else 0
        puntos += 2 if self.decision_automatizada else 0
        puntos += 1 if self.transferencia_internacional == SiNo.SI else 0
        puntos += 1 if self.menores == SiNo.SI else 0
        puntos += 2 if self.gran_escala else 0
        if puntos >= 5:
            return "ALTO"
        if puntos >= 2:
            return "MEDIO"
        return "BAJO"


class HistorialEstado(models.Model):
    """Trazabilidad del flujo del campo 3.20."""

    actividad = models.ForeignKey(
        ActividadTratamiento, on_delete=models.CASCADE, related_name="historial_estados",
    )
    estado_anterior = models.CharField(max_length=16, choices=EstadoRegistro.choices)
    estado_nuevo = models.CharField(max_length=16, choices=EstadoRegistro.choices)
    usuario = models.ForeignKey("accounts.Usuario", null=True, blank=True, on_delete=models.SET_NULL)
    motivo = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = _("Cambio de estado")
        verbose_name_plural = _("Historial de estados")
        ordering = ("-fecha",)


class Brecha(ModeloBase):
    """
    Plan de acción para filas «Con brechas» (§9 del procedimiento).
    """

    class Tipo(models.TextChoices):
        CONTRATO_ENCARGADO = "CONTRATO", _("Falta contrato de encargado")
        BASE_LEGAL = "BASE_LEGAL", _("Base de licitud débil o ausente")
        PLAZO = "PLAZO", _("Plazo de conservación indefinido")
        EIPD = "EIPD", _("EIPD pendiente")
        TRANSFERENCIA = "TRANSFERENCIA", _("Transferencia sin mecanismo habilitante")
        CONSENTIMIENTO = "CONSENTIMIENTO", _("Consentimiento no evidenciado")
        SEGURIDAD = "SEGURIDAD", _("Medida de seguridad faltante")
        OTRO = "OTRO", _("Otro")

    class Estado(models.TextChoices):
        ABIERTA = "ABIERTA", _("Abierta")
        EN_PROCESO = "EN_PROCESO", _("En proceso")
        CERRADA = "CERRADA", _("Cerrada")
        ACEPTADA = "ACEPTADA", _("Riesgo aceptado")

    actividad = models.ForeignKey(
        ActividadTratamiento, on_delete=models.CASCADE, related_name="brechas",
    )
    tipo = models.CharField(max_length=16, choices=Tipo.choices, db_index=True)
    descripcion = models.TextField()
    accion = models.TextField(_("Acción correctiva"))
    responsable = models.ForeignKey(
        "accounts.Usuario", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="brechas_asignadas",
    )
    fecha_compromiso = models.DateField(null=True, blank=True, db_index=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.ABIERTA, db_index=True)

    class Meta:
        verbose_name = _("Brecha")
        verbose_name_plural = _("Brechas y planes de acción")
        ordering = ("fecha_compromiso", "-creado_en")

    def __str__(self) -> str:
        return f"{self.actividad.codigo} — {self.get_tipo_display()}"

    @property
    def vencida(self) -> bool:
        return bool(
            self.fecha_compromiso
            and self.estado in (self.Estado.ABIERTA, self.Estado.EN_PROCESO)
            and self.fecha_compromiso < timezone.localdate()
        )


class Entrevista(ModeloBase):
    """
    Evidencia de la Fase 2. El procedimiento §10 exige conservar actas y
    cuestionarios como prueba de responsabilidad proactiva (Art. 10 lit. k).
    """

    area = models.ForeignKey("catalogos.Area", on_delete=models.PROTECT, related_name="entrevistas")
    fecha = models.DateField(default=timezone.localdate, db_index=True)
    entrevistados = EncryptedTextField(
        _("Entrevistados (cargo y nombre)"), blank=True, aad_scope="rat.entrevistados",
    )
    respuestas = EncryptedTextField(
        _("Respuestas al cuestionario"), blank=True, aad_scope="rat.entrevista_respuestas",
    )
    plantilla = models.ForeignKey(
        "plantillas.Plantilla", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="entrevistas",
    )
    confirmada_por_area = models.BooleanField(
        _("Confirmada por el área"), default=False,
        help_text=_("Regla de cierre: repetir la lista de actividades identificadas y "
                    "pedir confirmación expresa."),
    )
    actividades = models.ManyToManyField(
        ActividadTratamiento, blank=True, related_name="entrevistas",
    )

    class Meta:
        verbose_name = _("Entrevista de levantamiento")
        verbose_name_plural = _("Entrevistas de levantamiento")
        ordering = ("-fecha",)

    def __str__(self) -> str:
        return f"{self.area} — {self.fecha:%Y-%m-%d}"
