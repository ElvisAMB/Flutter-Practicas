"""
Carga los perfiles fijos, catálogos base y plantillas del procedimiento
PR-PDP-001. Idempotente: puede ejecutarse varias veces.
"""

from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Perfil, PerfilSistema, Usuario
from apps.catalogos.models import (
    Area, BaseLicitud, CategoriaDato, CategoriaTitular, CriterioConservacion,
    HabilitanteEspecial, Macroproceso, MecanismoTransferencia, MedidaSeguridad,
    Pais, TipoDatoEspecial,
)
from apps.plantillas.models import Plantilla, TipoPlantilla

MACROPROCESOS = [
    ("COM", "Comercial / Intermediación", 10),
    ("SUS", "Suscripción / Riesgos", 20),
    ("EMI", "Emisión / Operaciones", 30),
    ("CUM", "Cumplimiento (PLA/FT)", 40),
    ("COB", "Cobranzas / Finanzas", 50),
    ("SIN", "Reclamos / Siniestros", 60),
    ("LEG", "Legal / Recuperación", 70),
    ("REA", "Reaseguro", 80),
    ("TH", "Talento Humano", 90),
    ("TI", "Tecnología de la Información", 100),
    ("ADM", "Administración", 110),
    ("MKT", "Marketing / Comunicación", 120),
]

BASES_LICITUD = [
    (1, "Consentimiento del titular", "Marketing, encuestas, finalidades no necesarias para el contrato", False, True),
    (2, "Cumplimiento de obligación legal", "Reportes UAFE, SRI, IESS, organismo de control de seguros", False, False),
    (3, "Orden judicial", "Entrega de información en procesos judiciales", False, False),
    (4, "Misión de interés público / poderes públicos", "Raro en el sector privado", False, False),
    (5, "Medidas precontractuales o ejecución de contrato", "Cotización, suscripción, emisión, cobranza, reclamos", False, False),
    (6, "Intereses vitales", "Emergencias médicas de empleados o visitantes", False, False),
    (7, "Bases de datos de acceso público", "Consulta de registros públicos con límite de finalidad", False, False),
    (8, "Interés legítimo", "Prevención de fraude, seguridad, recuperación y subrogación", True, False),
]

HABILITANTES = [
    ("a", "Consentimiento explícito con fines claros"),
    ("b", "Obligaciones en derecho laboral y seguridad social"),
    ("c", "Intereses vitales del titular"),
    ("d", "Datos hechos manifiestamente públicos por el titular"),
    ("e", "Orden judicial"),
    ("f", "Archivo, investigación o estadística con salvaguardas"),
    ("g", "Datos de salud conforme a los Arts. 30–32 LOPDP"),
]

CATEGORIAS_DATOS = [
    ("IDENT", "Identificación", TipoDatoEspecial.NO_APLICA, "Nombres, cédula, RUC de persona natural, firma"),
    ("CONTACT", "Contacto", TipoDatoEspecial.NO_APLICA, "Dirección, teléfono, correo"),
    ("SOCIOEC", "Socioeconómicos y patrimoniales", TipoDatoEspecial.NO_APLICA, "Ingresos, bienes, referencias"),
    ("CREDIT", "Financieros y crediticios", TipoDatoEspecial.CREDITICIO, "Historial, score, endeudamiento"),
    ("LABOR", "Laborales", TipoDatoEspecial.NO_APLICA, "Cargo, remuneración, evaluaciones"),
    ("ACADEM", "Académicos", TipoDatoEspecial.NO_APLICA, "Títulos, certificaciones"),
    ("TRANSAC", "Transaccionales", TipoDatoEspecial.NO_APLICA, "Primas, pagos, siniestralidad"),
    ("JUDIC", "Judiciales / pasado judicial", TipoDatoEspecial.JUDICIAL, "Antecedentes penales, procesos"),
    ("SALUD", "Salud", TipoDatoEspecial.SALUD, "Certificados médicos, exámenes ocupacionales"),
    ("DISCAP", "Discapacidad", TipoDatoEspecial.DISCAPACIDAD, "Carné de discapacidad"),
    ("BIOMET", "Biométricos", TipoDatoEspecial.BIOMETRICO, "Huella, reconocimiento facial"),
    ("IMAGEN", "Imagen y voz", TipoDatoEspecial.NO_APLICA, "Videovigilancia, grabación de llamadas"),
    ("NAVEG", "Datos de navegación", TipoDatoEspecial.NO_APLICA, "Cookies, IP, analítica web"),
    ("CONTRAG", "Contragarantías", TipoDatoEspecial.NO_APLICA, "Pagarés, hipotecas, prendas, avalúos"),
]

CATEGORIAS_TITULARES = [
    ("AFIANZ", "Afianzados / asegurados persona natural", False),
    ("REPLEG", "Representantes legales, socios y accionistas de clientes PJ", False),
    ("CONTRAG", "Contragarantes y codeudores", False),
    ("CONYUG", "Cónyuges de garantes", False),
    ("BENEF", "Beneficiarios de la fianza (contactos persona natural)", True),
    ("CORRED", "Corredores e intermediarios persona natural", False),
    ("EMPLE", "Empleados y candidatos", False),
    ("CARGAS", "Cargas familiares de empleados", True),
    ("PROVEE", "Contactos de proveedores", False),
    ("VISIT", "Visitantes", False),
    ("WEB", "Usuarios de canales digitales", True),
]

MEDIDAS = [
    ("ACCROL", "Control de acceso por roles", "TECNICA"),
    ("MFA", "Autenticación multifactor", "TECNICA"),
    ("CIFTRA", "Cifrado en tránsito (TLS)", "TECNICA"),
    ("CIFREP", "Cifrado en reposo", "TECNICA"),
    ("SEUDO", "Seudonimización / disociación", "TECNICA"),
    ("RESPAL", "Respaldos y pruebas de restauración", "TECNICA"),
    ("BITAC", "Bitácoras de auditoría", "TECNICA"),
    ("SEGAMB", "Segregación de ambientes", "TECNICA"),
    ("ACUCONF", "Acuerdos de confidencialidad", "ORGANIZATIVA"),
    ("CAPAC", "Capacitación al personal", "ORGANIZATIVA"),
    ("POLIT", "Políticas y procedimientos", "ORGANIZATIVA"),
    ("ARCHLL", "Archivo físico bajo llave", "FISICA"),
    ("CTRLFIS", "Control de acceso físico", "FISICA"),
]

CRITERIOS = [
    ("LEYSEG", "Obligación legal — Ley General de Seguros", "Conservación contable ≥ 6 años", 72, False),
    ("POLIZA", "Duplicados de pólizas y anexos", "Al menos 3 años tras el vencimiento", 36, False),
    ("TRIBUT", "Normativa tributaria", "Plazos de prescripción del Código Tributario", 84, False),
    ("PLAFT", "Normativa PLA/FT (UAFE)", "Plazo de la normativa de prevención vigente", None, False),
    ("PRESCR", "Prescripción de acciones", "Defensa de reclamaciones — Art. 11 núm. 2 RLOPDP", None, False),
    ("CREDIT5", "Límite imperativo de datos crediticios", "Art. 28 LOPDP: 5 años desde la exigibilidad", 60, True),
    ("CONSENT", "Hasta revocatoria del consentimiento", "Marketing y comunicaciones comerciales", None, False),
    ("INTERNA", "Decisión interna motivada", "Política interna documentada", None, False),
]

MECANISMOS = [
    ("ADECUADO", "País con nivel adecuado declarado por la SPDP", "Art. 56 LOPDP / Art. 71 RLOPDP", False),
    ("CLAUSULAS", "Cláusulas tipo avaladas por la Autoridad", "Art. 58 LOPDP / Art. 75 RLOPDP", False),
    ("BCR", "Normas corporativas vinculantes aprobadas", "Art. 58 LOPDP / Art. 76 RLOPDP", False),
    ("CODIGO", "Códigos de conducta o certificaciones vinculantes", "Art. 74 RLOPDP", False),
    ("AUTORIZ", "Autorización previa de la Autoridad", "Art. 59 LOPDP / Art. 77 RLOPDP", True),
    ("EXC_CONS", "Excepción: consentimiento explícito informado de riesgos", "Art. 60 núm. 2 LOPDP", False),
    ("EXC_CONTR", "Excepción: ejecución de contrato", "Art. 60 núm. 4 LOPDP", False),
    ("EXC_BANC", "Excepción: operaciones bancarias y bursátiles", "Art. 60 núm. 9 LOPDP", False),
    ("EXC_RECL", "Excepción: defensa de reclamaciones", "Art. 60 núm. 10 LOPDP", False),
]

PAISES = [
    ("EC", "Ecuador", False), ("US", "Estados Unidos", False), ("ES", "España", False),
    ("DE", "Alemania", False), ("GB", "Reino Unido", False), ("CO", "Colombia", False),
    ("PE", "Perú", False), ("MX", "México", False), ("CH", "Suiza", False),
    ("BR", "Brasil", False), ("CL", "Chile", False), ("PA", "Panamá", False),
]

PLANTILLAS_BASE = [
    ("CUEST-GEN", "Cuestionario general de levantamiento", TipoPlantilla.CUESTIONARIO,
     "Bloque común del §7.1 del procedimiento, aplicable a todas las áreas."),
    ("CUEST-SUS", "Cuestionario específico — Suscripción y Riesgos", TipoPlantilla.CUESTIONARIO,
     "Preguntas del §7.2 para análisis de riesgo, burós y scoring."),
    ("CUEST-TH", "Cuestionario específico — Talento Humano", TipoPlantilla.CUESTIONARIO,
     "Datos sensibles, cargas familiares y antecedentes de candidatos."),
    ("CUEST-TI", "Cuestionario específico — TI y Seguridad", TipoPlantilla.CUESTIONARIO,
     "Inventario de sistemas, jurisdicción de la nube y controles."),
    ("EIPD-001", "Evaluación de impacto (EIPD)", TipoPlantilla.EIPD,
     "Estructura base conforme a los Arts. 29–32 RLOPDP."),
    ("TP-001", "Test de ponderación de interés legítimo", TipoPlantilla.TEST_PONDERACION,
     "Necesidad, proporcionalidad y expectativa razonable del titular."),
    ("ACTA-ENT", "Acta de entrevista de levantamiento", TipoPlantilla.ACTA,
     "Evidencia de responsabilidad proactiva (Art. 10 lit. k LOPDP)."),
    ("CONTR-ENC", "Cláusulas de contrato de encargo", TipoPlantilla.CONTRATO_ENCARGO,
     "Contenido mínimo del Art. 41 RLOPDP."),
    ("VULN-001", "Notificación de vulneración de seguridad", TipoPlantilla.NOTIF_VULNERACION,
     "Términos: 5 días a la Autoridad; 3 días al titular; 2 días del encargado."),
    ("AVISO-001", "Aviso de privacidad", TipoPlantilla.AVISO_PRIVACIDAD,
     "Derecho a la información — Art. 12 LOPDP."),
    ("FICHA-RAT", "Ficha de actividad para el Registro Nacional", TipoPlantilla.INFORME,
     "Insumo del reporte del Art. 51 LOPDP (nueve numerales)."),
]

CUERPO_GENERICO = """PLANTILLA: {{ titulo|default:"(sin título)" }}
Organización: {{ organizacion.razon_social }}
Fecha: {{ fecha }}
Elaborado por: {{ usuario }}

ACTIVIDAD RELACIONADA
Código: {{ actividad.codigo|default:"N/A" }}
Nombre: {{ actividad.nombre|default:"N/A" }}
Área: {{ area|default:"N/A" }}

CONTENIDO
[Edite esta plantilla desde el módulo Plantillas. Puede usar cualquier variable
del contexto y las etiquetas estándar de Django Template Language.]
"""


class Command(BaseCommand):
    help = "Crea perfiles fijos, catálogos base y plantillas del procedimiento PR-PDP-001."

    def add_arguments(self, parser):
        parser.add_argument("--admin", default="", help="Crea un superusuario con este nombre.")
        parser.add_argument("--password", default="")

    @transaction.atomic
    def handle(self, *args, **o):
        self.verbosidad = o.get("verbosity", 1)
        self._perfiles()
        self._catalogos()
        self._plantillas()
        if o["admin"]:
            self._admin(o["admin"], o["password"])
        self._log("Inicialización completada.", self.style.SUCCESS)

    def _log(self, mensaje, estilo=None):
        if self.verbosidad:
            self.stdout.write(estilo(mensaje) if estilo else mensaje)

    # ------------------------------------------------------------------
    def _perfiles(self):
        definiciones = [
            (PerfilSistema.ADMINISTRADOR, "Administrador",
             "Superusuario funcional. Único perfil que gestiona usuarios, perfiles y "
             "permisos. Acceso total a la aplicación.", False),
            (PerfilSistema.AUDITOR, "Auditor",
             "Solo lectura sobre toda la información, incluida la bitácora. No puede "
             "crear, modificar ni eliminar nada.", False),
            (PerfilSistema.USUARIO, "Usuario común",
             "Perfil base editable. Por defecto puede consultar y registrar actividades "
             "de su área; sus permisos los ajusta el administrador.", True),
        ]
        for codigo, nombre, descripcion, editable in definiciones:
            grupo, _ = Group.objects.get_or_create(name=nombre)
            perfil, creado = Perfil.objects.get_or_create(
                codigo=codigo,
                defaults={"grupo": grupo, "descripcion": descripcion, "es_sistema": True,
                          "permite_edicion_permisos": editable},
            )
            if not creado:
                perfil.descripcion = descripcion
                perfil.es_sistema = True
                perfil.permite_edicion_permisos = editable
                perfil.save()

            if codigo == PerfilSistema.ADMINISTRADOR:
                grupo.permissions.set(Permission.objects.filter(
                    content_type__app_label__in=["rat", "catalogos", "accounts",
                                                 "plantillas", "auditoria"]))
            elif codigo == PerfilSistema.AUDITOR:
                grupo.permissions.set(Permission.objects.filter(
                    content_type__app_label__in=["rat", "catalogos", "accounts",
                                                 "plantillas", "auditoria"],
                ).filter(codename__startswith="view_"))
                grupo.permissions.add(
                    *Permission.objects.filter(codename__in=["ver_bitacora", "exportar_rat"]))
            else:
                grupo.permissions.set(Permission.objects.filter(
                    content_type__app_label__in=["rat", "catalogos", "plantillas"],
                    codename__regex=r"^(view|add|change)_",
                ))
            self._log(f"  perfil {codigo}: {grupo.permissions.count()} permisos")

    def _catalogos(self):
        for codigo, nombre, orden in MACROPROCESOS:
            Macroproceso.objects.get_or_create(
                codigo=codigo, defaults={"nombre": nombre, "orden": orden})
            Area.objects.get_or_create(
                codigo=f"A-{codigo}",
                defaults={"nombre": nombre, "orden": orden,
                          "macroproceso": Macroproceso.objects.get(codigo=codigo)})

        for numeral, nombre, uso, test, consent in BASES_LICITUD:
            BaseLicitud.objects.get_or_create(
                codigo=f"ART7-{numeral}",
                defaults={"numeral": numeral, "nombre": nombre, "descripcion": uso,
                          "requiere_test_ponderacion": test,
                          "requiere_consentimiento": consent, "orden": numeral})

        for literal, nombre in HABILITANTES:
            HabilitanteEspecial.objects.get_or_create(
                codigo=f"ART26-{literal.upper()}",
                defaults={"literal": literal, "nombre": nombre})

        for codigo, nombre, tipo, ejemplos in CATEGORIAS_DATOS:
            CategoriaDato.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "tipo_especial": tipo, "ejemplos": ejemplos})

        for codigo, nombre, menores in CATEGORIAS_TITULARES:
            CategoriaTitular.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "puede_incluir_menores": menores})

        for codigo, nombre, tipo in MEDIDAS:
            MedidaSeguridad.objects.get_or_create(
                codigo=codigo, defaults={"nombre": nombre, "tipo": tipo})

        for codigo, nombre, norma, meses, imperativo in CRITERIOS:
            CriterioConservacion.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "norma_referencia": norma,
                          "plazo_sugerido_meses": meses, "es_limite_imperativo": imperativo})

        for codigo, nombre, articulo, autoriza in MECANISMOS:
            MecanismoTransferencia.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "articulo": articulo,
                          "requiere_autorizacion_spdp": autoriza})

        for iso2, nombre, adecuado in PAISES:
            Pais.objects.get_or_create(
                iso2=iso2, defaults={"nombre": nombre, "nivel_adecuado": adecuado})

        self._log("  catálogos base cargados")

    def _plantillas(self):
        for codigo, nombre, tipo, descripcion in PLANTILLAS_BASE:
            Plantilla.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "tipo": tipo, "descripcion": descripcion,
                          "cuerpo": CUERPO_GENERICO.replace("{{ titulo", "{{ titulo"),
                          "es_sistema": True},
            )
        self._log(f"  {len(PLANTILLAS_BASE)} plantillas base disponibles")

    def _admin(self, username: str, password: str):
        if Usuario.objects.filter(username=username).exists():
            self._log(f"  el usuario {username} ya existe", self.style.WARNING)
            return
        if not password:
            self.stderr.write("Debe indicar --password para crear el administrador.")
            return
        usuario = Usuario.objects.create_superuser(username=username, password=password)
        usuario.perfil = Perfil.objects.get(codigo=PerfilSistema.ADMINISTRADOR)
        usuario.debe_cambiar_password = True
        usuario.save()
        self._log(f"  administrador «{username}» creado (deberá cambiar su contraseña).",
                  self.style.SUCCESS)
