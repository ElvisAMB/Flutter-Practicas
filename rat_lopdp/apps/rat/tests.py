from django.contrib.auth.models import Permission, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.catalogos.models import (
    Area, BaseLicitud, CategoriaDato, CategoriaInteresado, DestinatarioExterno,
    EstadoRegistro, HabilitanteEspecial, MecanismoTransferencia, Pais, ProcesoInterno,
)
from apps.rat.models import ActividadTratamiento


class FlujoRATTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_catalogos", verbosity=0)
        cls.usuario = User.objects.create_user("dpd", password="Clave-Segura-2026")
        cls.usuario.user_permissions.set(Permission.objects.filter(
            content_type__app_label__in=["rat", "catalogos"]))

    def setUp(self):
        self.client.force_login(self.usuario)

    def _datos_base(self, **extra):
        datos = {
            "codigo": "RAT-SUS-01",
            "nombre_corto": "Evaluación de riesgo y capacidad de pago para suscripción de fianzas",
            "finalidad": "Evaluar el riesgo del solicitante antes de emitir la fianza.",
            "area": Area.objects.get(codigo="AR-01").pk,
            "responsable_cargo": "Jefe de Suscripción",
            "corresponsable_situacion": "NO",
            "categorias_datos": [CategoriaDato.objects.get(codigo="3.8.1").pk,
                                 CategoriaDato.objects.get(codigo="3.8.4").pk],
            "datos_especiales": "",
            "categorias_interesados": [CategoriaInteresado.objects.get(codigo="3.10.1").pk],
            "proceso_interno": ProcesoInterno.objects.get(codigo="3.12.1").pk,
            "destinatarios_internos": "Suscripción, Comité de Riesgos",
            "plazo_conservacion": "Vigencia de la fianza + 10 años",
            "criterio_plazo": "Prescripción de acciones contractuales.",
            "destino_final": "ELIM",
            "estado": EstadoRegistro.objects.get(codigo="3.20.1").pk,
            "aplica_art28": "on",
            # formset bases
            "bases-TOTAL_FORMS": "1", "bases-INITIAL_FORMS": "0",
            "bases-MIN_NUM_FORMS": "0", "bases-MAX_NUM_FORMS": "1000",
            "bases-0-base": BaseLicitud.objects.get(codigo="3.6.5").pk,
            "bases-0-justificacion": "Necesario para las medidas precontractuales de suscripción.",
            "bases-0-test_ponderacion": "",
            # formset destinatarios
            "dest-TOTAL_FORMS": "1", "dest-INITIAL_FORMS": "0",
            "dest-MIN_NUM_FORMS": "0", "dest-MAX_NUM_FORMS": "1000",
            "dest-0-destinatario": DestinatarioExterno.objects.get(codigo="3.13.5").pk,
            "dest-0-fundamento": "Art. 28 LOPDP: consulta de solvencia patrimonial.",
            # formset transferencias
            "transf-TOTAL_FORMS": "0", "transf-INITIAL_FORMS": "0",
            "transf-MIN_NUM_FORMS": "0", "transf-MAX_NUM_FORMS": "1000",
        }
        datos.update(extra)
        return datos

    def test_crea_actividad_completa(self):
        respuesta = self.client.post(reverse("rat:actividad_create"), self._datos_base())
        self.assertEqual(respuesta.status_code, 302, getattr(respuesta, "context", None))
        actividad = ActividadTratamiento.objects.get(codigo="RAT-SUS-01")
        self.assertEqual(actividad.version, 1)
        self.assertEqual(actividad.baselicitudactividad_set.count(), 1)
        self.assertEqual(actividad.historial.count(), 1)

    def test_datos_especiales_exige_habilitante(self):
        datos = self._datos_base(datos_especiales="on")
        respuesta = self.client.post(reverse("rat:actividad_create"), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("habilitantes_especiales", respuesta.context["form"].errors)

    def test_categoria_sensible_obliga_marcar_39(self):
        datos = self._datos_base()
        datos["categorias_datos"] = [CategoriaDato.objects.get(codigo="3.8.9").pk]
        respuesta = self.client.post(reverse("rat:actividad_create"), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("datos_especiales", respuesta.context["form"].errors)

    def test_destinatarios_externos_no_puede_quedar_vacio(self):
        datos = self._datos_base()
        datos["dest-TOTAL_FORMS"] = "0"
        datos.pop("dest-0-destinatario")
        datos.pop("dest-0-fundamento")
        respuesta = self.client.post(reverse("rat:actividad_create"), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["fs_destinatarios"].non_form_errors())

    def test_interes_legitimo_exige_ponderacion(self):
        datos = self._datos_base()
        datos["bases-0-base"] = BaseLicitud.objects.get(codigo="3.6.8").pk
        datos["bases-0-test_ponderacion"] = ""
        respuesta = self.client.post(reverse("rat:actividad_create"), datos)
        self.assertEqual(respuesta.status_code, 200)

    def test_transferencia_marcada_exige_pais(self):
        datos = self._datos_base(transferencia_internacional="on")
        respuesta = self.client.post(reverse("rat:actividad_create"), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["fs_transferencias"].non_form_errors())

    def test_transferencia_completa(self):
        datos = self._datos_base(
            transferencia_internacional="on",
            **{"transf-TOTAL_FORMS": "1",
               "transf-0-pais": Pais.objects.get(codigo="US").pk,
               "transf-0-mecanismo": MecanismoTransferencia.objects.get(codigo="3.15.2").pk,
               "transf-0-detalle": "Cláusulas tipo avaladas por la Autoridad.",
               "transf-0-destinatario_exterior": "Proveedor cloud",
               "transf-0-registrada_registro_nacional": "on"})
        respuesta = self.client.post(reverse("rat:actividad_create"), datos)
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(ActividadTratamiento.objects.get(codigo="RAT-SUS-01")
                         .transferencias.count(), 1)

    def test_edicion_incrementa_version(self):
        self.client.post(reverse("rat:actividad_create"), self._datos_base())
        actividad = ActividadTratamiento.objects.get(codigo="RAT-SUS-01")
        datos = self._datos_base(
            **{"bases-INITIAL_FORMS": "1", "dest-INITIAL_FORMS": "1",
               "bases-0-id": actividad.baselicitudactividad_set.first().pk,
               "bases-0-actividad": actividad.pk,
               "dest-0-id": actividad.destinatarioexternoactividad_set.first().pk,
               "dest-0-actividad": actividad.pk})
        datos["finalidad"] = "Finalidad corregida."
        respuesta = self.client.post(
            reverse("rat:actividad_update", args=[actividad.pk]), datos)
        self.assertEqual(respuesta.status_code, 302)
        actividad.refresh_from_db()
        self.assertEqual(actividad.version, 2)
        self.assertEqual(actividad.historial.count(), 2)

    def test_listado_detalle_tablero_y_export(self):
        self.client.post(reverse("rat:actividad_create"), self._datos_base())
        actividad = ActividadTratamiento.objects.get(codigo="RAT-SUS-01")
        self.assertEqual(self.client.get(reverse("rat:actividad_list")).status_code, 200)
        self.assertEqual(self.client.get(actividad.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(reverse("rat:tablero")).status_code, 200)
        csv = self.client.get(reverse("rat:exportar_csv"))
        self.assertEqual(csv.status_code, 200)
        self.assertIn("RAT-SUS-01", csv.content.decode("utf-8-sig"))

    def test_catalogos_crud(self):
        self.assertEqual(self.client.get(reverse("catalogos:indice")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("catalogos:lista", args=["bases-licitud"])).status_code, 200)
        respuesta = self.client.post(
            reverse("catalogos:crear", args=["procesos"]),
            {"codigo": "3.12.10", "nombre": "Siniestros", "descripcion": "",
             "orden": "100", "activo": "on"})
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(ProcesoInterno.objects.filter(codigo="3.12.10").exists())

    def test_sin_permisos_no_entra(self):
        self.client.logout()
        respuesta = self.client.get(reverse("rat:actividad_list"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/cuentas/ingresar/", respuesta["Location"])
