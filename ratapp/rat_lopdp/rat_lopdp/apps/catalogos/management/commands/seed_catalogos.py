"""
Carga inicial idempotente de los catálogos parametrizables del RAT.

Ejecutar: python manage.py seed_catalogos
Vuelve a correrse sin duplicar: usa update_or_create sobre `codigo`.
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalogos.models import (
    Area, BaseLicitud, CategoriaDato, CategoriaInteresado, CriterioEIPD,
    DestinatarioExterno, EstadoRegistro, HabilitanteEspecial, MecanismoTransferencia,
    MedidaSeguridad, Pais, ProcesoInterno,
)

BASES_LICITUD = [
    ("3.6.1", "Consentimiento", "Marketing, encuestas, finalidades no necesarias para el contrato.",
     "Art. 7 núm. 1 LOPDP", False),
    ("3.6.2", "Obligación legal",
     "Reportes UAFE, retenciones tributarias, reportes al organismo de control de seguros, IESS.",
     "Art. 7 núm. 2 LOPDP", False),
    ("3.6.3", "Orden judicial", "Entrega de información en procesos judiciales.",
     "Art. 7 núm. 3 LOPDP", False),
    ("3.6.4", "Misión de interés público / poderes públicos",
     "Raro en el sector privado; normalmente N/A.", "Art. 7 núm. 4 LOPDP", False),
    ("3.6.5", "Medidas precontractuales / ejecución de contrato",
     "Cotización, suscripción, emisión, cobranza, reclamos, ejecución de la fianza.",
     "Art. 7 núm. 5 LOPDP", False),
    ("3.6.6", "Intereses vitales", "Emergencias médicas de empleados o visitantes.",
     "Art. 7 núm. 6 LOPDP", False),
    ("3.6.7", "Bases de datos de acceso público",
     "Consulta de registros públicos, con límite de finalidad.",
     "Art. 7 núm. 7 LOPDP / Art. 7 núm. 4 RLOPDP", False),
    ("3.6.8", "Interés legítimo",
     "Prevención de fraude, seguridad de instalaciones, recuperación y subrogación. "
     "Exige test de ponderación documentado y transparencia.",
     "Art. 7 núm. 8 LOPDP / Art. 7 núm. 3 RLOPDP / Art. 9 LOPDP", True),
]

HABILITANTES = [
    ("3.7.1", "a) Consentimiento explícito con fines claros", "", "Art. 26 lit. a LOPDP"),
    ("3.7.2", "b) Obligaciones en derecho laboral y seguridad social",
     "Típico en Talento Humano: salud ocupacional.", "Art. 26 lit. b LOPDP"),
    ("3.7.3", "c) Intereses vitales", "", "Art. 26 lit. c LOPDP"),
    ("3.7.4", "d) Datos hechos manifiestamente públicos por el titular", "", "Art. 26 lit. d LOPDP"),
    ("3.7.5", "e) Orden judicial", "", "Art. 26 lit. e LOPDP"),
    ("3.7.6", "f) Archivo, investigación o estadística con salvaguardas", "", "Art. 26 lit. f LOPDP"),
    ("3.7.7", "g) Datos de salud conforme la propia ley", "Arts. 30-32 LOPDP.",
     "Art. 26 lit. g LOPDP"),
    ("3.7.8", "Menores de edad — consentimiento del representante legal",
     "Menores de 15 años: consiente el representante. Desde los 15, el adolescente consiente por sí mismo.",
     "Art. 21 LOPDP / Art. 19 RLOPDP"),
]

CATEGORIAS_DATOS = [
    ("3.8.1", "Identificación", "Nombres, cédula o RUC de persona natural, firma.", False),
    ("3.8.2", "Contacto", "Dirección, teléfono, correo electrónico.", False),
    ("3.8.3", "Socioeconómicos y patrimoniales", "Ingresos, bienes, referencias.", False),
    ("3.8.4", "Financieros y crediticios", "Historial, score, endeudamiento.", False),
    ("3.8.5", "Laborales", "Cargo, remuneración, evaluaciones.", False),
    ("3.8.6", "Académicos", "Títulos, certificaciones.", False),
    ("3.8.7", "Transaccionales", "Primas, pagos, siniestralidad.", False),
    ("3.8.8", "Judiciales / pasado judicial",
     "Antecedentes penales en debida diligencia o suscripción. Categoría especial.", True),
    ("3.8.9", "Salud", "Categoría especial (Arts. 4 y 25 LOPDP).", True),
    ("3.8.10", "Biométricos", "Huella, reconocimiento facial. Categoría especial.", True),
    ("3.8.11", "Imagen (videovigilancia)", "Captación en instalaciones.", False),
    ("3.8.12", "Datos de navegación", "IP, cookies, registros de uso del sitio web.", False),
]

CATEGORIAS_INTERESADOS = [
    ("3.10.1", "Afianzados, asegurados y compradores personas naturales", False),
    ("3.10.2", "Representantes legales, socios y accionistas de clientes personas jurídicas", False),
    ("3.10.3", "Contragarantes y codeudores", False),
    ("3.10.4", "Cónyuges de garantes", False),
    ("3.10.5", "Beneficiarios de la fianza (contactos persona natural)", True),
    ("3.10.6", "Corredores e intermediarios", False),
    ("3.10.7", "Empleados y candidatos", True),
    ("3.10.8", "Contactos de proveedores", False),
    ("3.10.9", "Visitantes", False),
    ("3.10.10", "Usuarios web", True),
]

PROCESOS = [
    ("3.12.1", "Seguro de Fianzas"),
    ("3.12.2", "Seguro de Crédito"),
    ("3.12.3", "Cobranzas"),
    ("3.12.4", "Comercial"),
    ("3.12.5", "Marketing"),
    ("3.12.6", "Comunicaciones"),
    ("3.12.7", "Atención al cliente"),
    ("3.12.8", "Talento Humano"),
    ("3.12.9", "Finanzas"),
]

DESTINATARIOS = [
    ("3.13.0", "Ninguno — sin comunicaciones a terceros",
     "Marque esta opción cuando la actividad no comunica datos fuera de la compañía.", True),
    ("3.13.1", "Organismo de control de seguros", "", False),
    ("3.13.2", "SRI", "", False),
    ("3.13.3", "IESS", "", False),
    ("3.13.4", "UAFE", "", False),
    ("3.13.5", "Burós de crédito", "Deciden su propio uso: son destinatarios, no encargados.", False),
    ("3.13.6", "Bancos (débitos)", "", False),
    ("3.13.7", "Reaseguradores", "", False),
    ("3.13.8", "Juzgados", "", False),
    ("3.13.9", "Peritos independientes", "", False),
]

MECANISMOS = [
    ("3.15.1", "(a) País con nivel adecuado declarado por la SPDP",
     "", "Art. 56 LOPDP / Art. 71 RLOPDP", False),
    ("3.15.2", "(b) Garantías adecuadas mediante instrumento jurídico vinculante",
     "Cláusulas tipo avaladas por la Autoridad, normas corporativas vinculantes aprobadas, "
     "códigos de conducta o certificaciones con compromisos vinculantes.",
     "Art. 58 LOPDP / Arts. 74-76 RLOPDP", False),
    ("3.15.3", "(c) Autorización previa de la Autoridad", "",
     "Art. 59 LOPDP / Art. 77 RLOPDP", True),
    ("3.15.4", "(d) Caso excepcional del Art. 60 LOPDP",
     "Especialmente: núm. 2 consentimiento explícito informado de riesgos; núm. 4 ejecución de "
     "contrato; núm. 9 operaciones bancarias y bursátiles; núm. 10 defensa de reclamaciones.",
     "Art. 60 LOPDP", False),
]

CRITERIOS_EIPD = [
    ("3.19.1", "(a) Evaluación sistemática basada en tratamiento automatizado con efectos jurídicos",
     "Incluye elaboración de perfiles. El scoring de suscripción o crédito encaja aquí.",
     "Art. 42 LOPDP"),
    ("3.19.2", "(b) Tratamiento a gran escala de categorías especiales o de datos penales",
     "Aplique los criterios del Art. 4 núm. 7 RLOPDP y el Método Técnico de Gran Escala (MTGE).",
     "Art. 42 LOPDP / Art. 4 núm. 7 RLOPDP"),
    ("3.19.3", "(c) Observación sistemática a gran escala de zona de acceso público",
     "Videovigilancia extensiva.", "Art. 42 LOPDP"),
]

ESTADOS = [
    ("3.20.1", "Borrador", "Levantado, sin validar.", "secondary", False, False, 10),
    ("3.20.2", "Validado", "Aprobado por el dueño del proceso y el DPD.", "info", False, False, 20),
    ("3.20.3", "Vigente", "Operando y reportado al Registro Nacional cuando corresponda.",
     "success", True, False, 30),
    ("3.20.4", "En revisión", "Cambio en curso.", "warning", True, False, 40),
    ("3.20.5", "Histórico / Cesado",
     "Tratamiento finalizado. Se conserva la fila con fecha de cese para trazabilidad.",
     "dark", False, True, 50),
]

MEDIDAS = [
    ("SEG-01", "Control de acceso por roles", "TEC"),
    ("SEG-02", "Autenticación multifactor (MFA)", "TEC"),
    ("SEG-03", "Cifrado en tránsito", "TEC"),
    ("SEG-04", "Cifrado en reposo", "TEC"),
    ("SEG-05", "Seudonimización / disociación", "TEC"),
    ("SEG-06", "Respaldos y pruebas de restauración", "TEC"),
    ("SEG-07", "Bitácoras de auditoría", "TEC"),
    ("SEG-08", "Segregación de ambientes", "TEC"),
    ("SEG-09", "Acuerdos de confidencialidad", "ORG"),
    ("SEG-10", "Políticas y procedimientos aprobados", "ORG"),
    ("SEG-11", "Capacitación al personal", "ORG"),
    ("SEG-12", "Archivo físico bajo llave", "ORG"),
    ("SEG-13", "Gestión de incidentes y notificación de brechas", "ORG"),
]

PAISES = [
    ("EC", "Ecuador", False), ("US", "Estados Unidos", False), ("ES", "España", False),
    ("CO", "Colombia", False), ("PE", "Perú", False), ("MX", "México", False),
    ("CL", "Chile", False), ("BR", "Brasil", False), ("PA", "Panamá", False),
    ("GB", "Reino Unido", False), ("DE", "Alemania", False), ("IE", "Irlanda", False),
    ("CH", "Suiza", False), ("AR", "Argentina", False),
]

AREAS = [
    ("AR-01", "Suscripción", "Jefe de Suscripción"),
    ("AR-02", "Comercial", "Gerente Comercial"),
    ("AR-03", "Cobranzas", "Jefe de Cobranzas"),
    ("AR-04", "Talento Humano", "Jefe de Talento Humano"),
    ("AR-05", "Finanzas", "Gerente Financiero"),
    ("AR-06", "Tecnología de la Información", "Jefe de TI"),
    ("AR-07", "Cumplimiento / PLAFT", "Oficial de Cumplimiento"),
    ("AR-08", "Legal", "Gerente Legal"),
    ("AR-09", "Auditoría Interna", "Auditor Interno"),
    ("AR-10", "Atención al Cliente", "Jefe de Servicio al Cliente"),
]

PERFILES = {
    "DPD": "todos",
    "Dueño de proceso": [
        "view_actividadtratamiento", "add_actividadtratamiento", "change_actividadtratamiento",
    ],
    "Consulta": ["view_actividadtratamiento"],
}


class Command(BaseCommand):
    help = "Carga los catálogos parametrizables del RAT y los perfiles de permisos."

    def add_arguments(self, parser):
        parser.add_argument("--sin-perfiles", action="store_true",
                            help="No crear los grupos de permisos.")

    @transaction.atomic
    def handle(self, *args, **opciones):
        def cargar(modelo, codigo, orden, **campos):
            modelo.objects.update_or_create(
                codigo=codigo, defaults={"orden": orden, "activo": True, **campos})

        for i, (c, n, d) in enumerate(AREAS, 1):
            cargar(Area, c, i * 10, nombre=n, responsable_cargo=d)
        for i, (c, n, d, ref, pond) in enumerate(BASES_LICITUD, 1):
            cargar(BaseLicitud, c, i * 10, nombre=n, descripcion=d,
                   referencia_legal=ref, exige_ponderacion=pond)
        for i, (c, n, d, ref) in enumerate(HABILITANTES, 1):
            cargar(HabilitanteEspecial, c, i * 10, nombre=n, descripcion=d, referencia_legal=ref)
        for i, (c, n, d, sens) in enumerate(CATEGORIAS_DATOS, 1):
            cargar(CategoriaDato, c, i * 10, nombre=n, descripcion=d, es_sensible=sens)
        for i, (c, n, men) in enumerate(CATEGORIAS_INTERESADOS, 1):
            cargar(CategoriaInteresado, c, i * 10, nombre=n, implica_menores=men)
        for i, (c, n) in enumerate(PROCESOS, 1):
            cargar(ProcesoInterno, c, i * 10, nombre=n)
        for i, (c, n, d, ning) in enumerate(DESTINATARIOS, 1):
            cargar(DestinatarioExterno, c, i * 10, nombre=n, descripcion=d, es_ninguno=ning)
        for i, (c, n, d, ref, aut) in enumerate(MECANISMOS, 1):
            cargar(MecanismoTransferencia, c, i * 10, nombre=n, descripcion=d,
                   referencia_legal=ref, requiere_autorizacion_previa=aut)
        for i, (c, n, d, ref) in enumerate(CRITERIOS_EIPD, 1):
            cargar(CriterioEIPD, c, i * 10, nombre=n, descripcion=d, referencia_legal=ref)
        for c, n, d, color, vig, fin, orden in ESTADOS:
            cargar(EstadoRegistro, c, orden, nombre=n, descripcion=d, color=color,
                   es_vigente=vig, es_final=fin)
        for i, (c, n, t) in enumerate(MEDIDAS, 1):
            cargar(MedidaSeguridad, c, i * 10, nombre=n, tipo=t,
                   referencia_legal="Arts. 37-41 LOPDP")
        for i, (c, n, adecuado) in enumerate(PAISES, 1):
            cargar(Pais, c, i * 10, nombre=n, nivel_adecuado=adecuado)

        self.stdout.write(self.style.SUCCESS("Catálogos cargados."))

        if not opciones["sin_perfiles"]:
            self._perfiles()

    def _perfiles(self):
        permisos_rat = Permission.objects.filter(
            content_type__app_label__in=["rat", "catalogos"])
        for nombre, codigos in PERFILES.items():
            grupo, _ = Group.objects.get_or_create(name=nombre)
            if codigos == "todos":
                grupo.permissions.set(permisos_rat)
            else:
                grupo.permissions.set(permisos_rat.filter(codename__in=codigos))
        self.stdout.write(self.style.SUCCESS(
            "Perfiles creados: " + ", ".join(PERFILES) +
            ". Revise y ajuste los permisos antes de producción."))
