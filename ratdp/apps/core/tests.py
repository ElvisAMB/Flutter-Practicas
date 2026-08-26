"""
Pruebas del núcleo: cifrado, índices ciegos y bitácora encadenada.

Ejecutar con:  python manage.py test apps
"""

from django.core.exceptions import FieldError, ValidationError
from django.db import connection
from django.test import TestCase, override_settings

from apps.accounts.models import Usuario
from apps.auditoria.models import Accion, Evento
from apps.core.crypto import CryptoError, blind_index, decrypt, encrypt, generar_llave

LLAVES = {"1": generar_llave(), "2": generar_llave()}
INDEX = generar_llave()


@override_settings(DP_ENC_KEYS=LLAVES, DP_ENC_ACTIVE_KEY="1", DP_INDEX_KEY=INDEX)
class CifradoTest(TestCase):
    def setUp(self):
        from apps.core import crypto

        crypto.reset_cache()

    def test_ida_y_vuelta(self):
        texto = "Juan Carlos Pérez Andrade"
        self.assertEqual(decrypt(encrypt(texto)), texto)

    def test_no_determinista(self):
        """Dos cifrados del mismo texto deben diferir (nonce aleatorio)."""
        self.assertNotEqual(encrypt("1712345678"), encrypt("1712345678"))

    def test_aad_impide_mover_ciphertext(self):
        """Un valor cifrado para una columna no debe descifrarse en otra."""
        token = encrypt("dato", aad=b"tabla.columna_a")
        with self.assertRaises(CryptoError):
            decrypt(token, aad=b"tabla.columna_b")

    def test_deteccion_de_manipulacion(self):
        token = encrypt("valor original")
        alterado = token[:-6] + "AAAAAA"
        with self.assertRaises(CryptoError):
            decrypt(alterado)

    def test_llave_ausente(self):
        token = encrypt("dato")
        with override_settings(DP_ENC_KEYS={"9": LLAVES["2"]}, DP_ENC_ACTIVE_KEY="9"):
            from apps.core import crypto

            crypto.reset_cache()
            with self.assertRaises(CryptoError):
                decrypt(token)
        from apps.core import crypto

        crypto.reset_cache()

    def test_indice_ciego_determinista_e_insensible_a_mayusculas(self):
        a = blind_index("JPerez@Empresa.com ", scope="usuario.email")
        b = blind_index("jperez@empresa.com", scope="usuario.email")
        self.assertEqual(a, b)

    def test_indice_ciego_separado_por_scope(self):
        """El mismo valor en dominios distintos no debe correlacionarse."""
        self.assertNotEqual(
            blind_index("1712345678", scope="usuario.documento"),
            blind_index("1712345678", scope="tercero.documento"),
        )


@override_settings(DP_ENC_KEYS=LLAVES, DP_ENC_ACTIVE_KEY="1", DP_INDEX_KEY=INDEX)
class CampoCifradoTest(TestCase):
    def setUp(self):
        from apps.core import crypto

        crypto.reset_cache()
        self.u = Usuario.objects.create_user(
            username="jperez", password="Prueba.2026#Larga",
            first_name="Juan", email="jperez@empresa.com", documento="1712345678",
        )

    def test_valor_en_base_de_datos_esta_cifrado(self):
        with connection.cursor() as cur:
            cur.execute(
                "SELECT first_name, email FROM accounts_usuario WHERE username = %s",
                ["jperez"],
            )
            first_name, email = cur.fetchone()
        self.assertTrue(first_name.startswith("v1$"))
        self.assertNotIn("Juan", first_name)
        self.assertNotIn("jperez@empresa.com", email)

    def test_orm_devuelve_el_valor_en_claro(self):
        u = Usuario.objects.get(username="jperez")
        self.assertEqual(u.first_name, "Juan")
        self.assertEqual(u.email, "jperez@empresa.com")

    def test_busqueda_por_indice_ciego(self):
        u = Usuario.objects.get(
            email_bidx=blind_index("JPEREZ@EMPRESA.COM", scope="usuario.email"))
        self.assertEqual(u.pk, self.u.pk)

    def test_lookup_parcial_bloqueado_con_mensaje_util(self):
        """Debe fallar ruidosamente, no devolver cero resultados en silencio."""
        with self.assertRaises(FieldError) as ctx:
            list(Usuario.objects.filter(email__icontains="empresa"))
        self.assertIn("cifrado", str(ctx.exception))

    def test_indice_ciego_se_actualiza_al_cambiar_el_origen(self):
        self.u.email = "nuevo@empresa.com"
        self.u.save()
        self.assertEqual(
            Usuario.objects.get(pk=self.u.pk).email_bidx,
            blind_index("nuevo@empresa.com", scope="usuario.email"),
        )


@override_settings(DP_ENC_KEYS=LLAVES, DP_ENC_ACTIVE_KEY="1", DP_INDEX_KEY=INDEX)
class BitacoraTest(TestCase):
    def setUp(self):
        from apps.core import crypto

        crypto.reset_cache()
        for i in range(5):
            Evento.registrar(username=f"u{i}", accion=Accion.CONSULTA, modelo="prueba",
                             objeto_id=str(i), detalle={"n": i})

    def test_cadena_valida(self):
        self.assertTrue(Evento.verificar_cadena()["ok"])

    def test_evento_no_puede_modificarse(self):
        ev = Evento.objects.first()
        ev.objeto_repr = "otra cosa"
        with self.assertRaises(PermissionError):
            ev.save()

    def test_evento_no_puede_eliminarse(self):
        with self.assertRaises(PermissionError):
            Evento.objects.first().delete()

    def test_alteracion_directa_en_sql_rompe_la_cadena(self):
        objetivo = Evento.objects.order_by("id")[2]
        with connection.cursor() as cur:
            cur.execute("UPDATE auditoria_evento SET objeto_repr = %s WHERE id = %s",
                        ["ALTERADO", objetivo.id])
        resultado = Evento.verificar_cadena()
        self.assertFalse(resultado["ok"])
        self.assertEqual(resultado["evento_id"], objetivo.id)
        self.assertEqual(resultado["motivo"], "contenido alterado")

    def test_borrado_directo_en_sql_rompe_la_cadena(self):
        objetivo = Evento.objects.order_by("id")[2]
        with connection.cursor() as cur:
            cur.execute("DELETE FROM auditoria_evento WHERE id = %s", [objetivo.id])
        self.assertFalse(Evento.verificar_cadena()["ok"])

    def test_detalle_cifrado_en_base_de_datos(self):
        with connection.cursor() as cur:
            cur.execute("SELECT detalle FROM auditoria_evento ORDER BY id LIMIT 1")
            detalle = cur.fetchone()[0]
        self.assertTrue(detalle.startswith("v1$"))
