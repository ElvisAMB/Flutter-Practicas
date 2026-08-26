"""Pruebas de las reglas de negocio del RAT y del control de acceso por perfil."""

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Perfil, PerfilSistema, Usuario
from apps.catalogos.models import Area, CriterioConservacion, HabilitanteEspecial
from apps.rat.models import ActividadTratamiento, EstadoRegistro, SiNo


class BaseRAT(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("inicializar", verbosity=0)
        cls.area = Area.objects.get(codigo="A-SUS")
        cls.actividad = ActividadTratamiento.objects.create(
            codigo="RAT-SUS-01",
            nombre="Evaluación de riesgo para suscripción",
            finalidad="Analizar la capacidad de pago del solicitante y sus garantes.",
            area=cls.area, cargo_responsable="Gerente de Suscripción",
            justificacion_base_licitud="Art. 7 núm. 5 LOPDP",
            datos_especiales=SiNo.SI, tipos_dato_especial=["CREDITICIO"],
            transferencia_internacional=SiNo.NO, menores=SiNo.NO,
            plazo_conservacion="Vigencia + 6 años",
            criterio_conservacion=CriterioConservacion.objects.get(codigo="LEYSEG"),
        )
        # 3.9 = SI obliga a completar 3.7 (Art. 26 LOPDP); el modelo lo valida.
        cls.actividad.habilitantes_especiales.add(
            HabilitanteEspecial.objects.get(literal="a"))


class ReglasNegocioTest(BaseRAT):
    def test_scoring_no_puede_declarar_eipd_no_requerida(self):
        """Art. 42 lit. a LOPDP: el perfilamiento con efectos jurídicos exige EIPD."""
        self.actividad.decision_automatizada = True
        self.actividad.eipd_requerida = SiNo.NO
        with self.assertRaises(ValidationError) as ctx:
            self.actividad.full_clean(exclude=["creado_por", "actualizado_por"])
        self.assertIn("eipd_requerida", ctx.exception.message_dict)

    def test_no_se_publica_con_eipd_requerida_sin_informe(self):
        """La EIPD es previa al tratamiento, no posterior."""
        self.actividad.eipd_requerida = SiNo.SI
        self.actividad.eipd_codigo = ""
        self.actividad.estado = EstadoRegistro.VIGENTE
        with self.assertRaises(ValidationError) as ctx:
            self.actividad.full_clean(exclude=["creado_por", "actualizado_por"])
        self.assertIn("eipd_codigo", ctx.exception.message_dict)

    def test_historico_exige_fecha_de_cese(self):
        self.actividad.estado = EstadoRegistro.HISTORICO
        with self.assertRaises(ValidationError) as ctx:
            self.actividad.full_clean(exclude=["creado_por", "actualizado_por"])
        self.assertIn("fecha_cese", ctx.exception.message_dict)

    def test_transicion_invalida_rechazada(self):
        with self.assertRaises(ValidationError):
            self.actividad.cambiar_estado(EstadoRegistro.VIGENTE)

    def test_flujo_valido_y_registro_en_historial(self):
        self.actividad.cambiar_estado(EstadoRegistro.EN_VALIDACION, motivo="cierre")
        self.actividad.cambiar_estado(EstadoRegistro.VALIDADO)
        self.assertEqual(self.actividad.estado, EstadoRegistro.VALIDADO)
        self.assertEqual(self.actividad.historial_estados.count(), 2)
        self.assertIsNotNone(self.actividad.fecha_validacion)

    def test_alertas_detectan_incumplimientos(self):
        alertas = " ".join(self.actividad.alertas)
        self.assertIn("5 años", alertas)          # límite Art. 28 por datos crediticios
        self.assertIn("Nunca revisada", alertas)

    def test_plazo_indefinido_genera_alerta(self):
        self.actividad.plazo_conservacion = "Indefinido"
        self.assertTrue(any("indefinido" in a.lower() for a in self.actividad.alertas))

    def test_nivel_riesgo(self):
        self.assertEqual(self.actividad.nivel_riesgo, "MEDIO")
        self.actividad.decision_automatizada = True
        self.actividad.gran_escala = True
        self.assertEqual(self.actividad.nivel_riesgo, "ALTO")

    def test_borrado_es_logico(self):
        pk = self.actividad.pk
        self.actividad.delete()
        self.assertFalse(ActividadTratamiento.objects.filter(pk=pk).exists())
        self.assertTrue(ActividadTratamiento.todos.filter(pk=pk).exists())


class ControlAccesoTest(BaseRAT):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        def crear(username, codigo):
            u = Usuario.objects.create_user(username=username, password="Prueba.2026#Larga")
            u.perfil = Perfil.objects.get(codigo=codigo)
            u.debe_cambiar_password = False
            u.save()
            return u
        cls.admin = crear("admin_t", PerfilSistema.ADMINISTRADOR)
        cls.auditor = crear("auditor_t", PerfilSistema.AUDITOR)
        cls.comun = crear("usuario_t", PerfilSistema.USUARIO)

    def test_anonimo_es_redirigido_al_login(self):
        r = self.client.get(reverse("rat:lista"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("ingreso", r.url)

    def test_auditor_lee_pero_no_escribe(self):
        self.client.force_login(self.auditor)
        self.assertEqual(self.client.get(reverse("rat:lista")).status_code, 200)
        self.assertEqual(self.client.get(reverse("rat:crear")).status_code, 403)

    def test_auditor_nunca_obtiene_permiso_de_escritura(self):
        """Aunque se le asigne por error al grupo, has_perm debe negarlo."""
        from django.contrib.auth.models import Permission

        perfil = Perfil.objects.get(codigo=PerfilSistema.AUDITOR)
        perfil.grupo.permissions.add(
            Permission.objects.get(codename="add_actividadtratamiento"))
        usuario = Usuario.objects.get(pk=self.auditor.pk)  # recarga la caché de permisos
        self.assertFalse(usuario.has_perm("rat.add_actividadtratamiento"))

    def test_usuario_comun_no_gestiona_accesos(self):
        self.client.force_login(self.comun)
        self.assertEqual(self.client.get(reverse("gestion:usuarios")).status_code, 403)

    def test_administrador_gestiona_accesos(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("gestion:usuarios")).status_code, 200)
        self.assertEqual(self.client.get(reverse("gestion:perfiles")).status_code, 200)

    def test_perfiles_de_sistema_no_admiten_edicion_de_permisos(self):
        for codigo in (PerfilSistema.ADMINISTRADOR, PerfilSistema.AUDITOR):
            perfil = Perfil.objects.get(codigo=codigo)
            self.assertFalse(perfil.permite_edicion_permisos)
            with self.assertRaises(ValueError):
                perfil.asignar_permisos([])

    def test_perfil_usuario_si_admite_edicion(self):
        self.assertTrue(
            Perfil.objects.get(codigo=PerfilSistema.USUARIO).permite_edicion_permisos)

    def test_exportacion_queda_auditada_con_numero_de_filas(self):
        from apps.auditoria.models import Accion, Evento

        self.client.force_login(self.admin)
        self.client.get(reverse("rat:exportar"))
        evento = Evento.objects.filter(accion=Accion.EXPORTACION).first()
        self.assertIsNotNone(evento)
        self.assertIn("filas_exportadas", evento.detalle)


class IndicadoresTest(BaseRAT):
    def test_tablero_se_calcula(self):
        from apps.indicadores import services

        tablero = services.calcular(usar_cache=False)
        self.assertEqual(tablero.total_actividades, 1)
        self.assertEqual(len(tablero.indicadores), 10)
        codigos = {i.codigo for i in tablero.indicadores}
        self.assertIn("IND-03", codigos)
