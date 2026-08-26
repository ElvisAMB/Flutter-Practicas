"""Verifica la integridad de la cadena hash de la bitácora."""
from django.core.management.base import BaseCommand

from apps.auditoria.models import Evento


class Command(BaseCommand):
    help = "Recorre la bitácora y verifica el encadenamiento SHA-256 de cada evento."

    def add_arguments(self, parser):
        parser.add_argument("--desde", type=int, default=0)
        parser.add_argument("--hasta", type=int, default=None)

    def handle(self, *args, **opciones):
        resultado = Evento.verificar_cadena(opciones["desde"], opciones["hasta"])
        if resultado["ok"]:
            self.stdout.write(self.style.SUCCESS(
                f"Integridad correcta: {resultado['revisados']} eventos verificados."))
            return
        self.stderr.write(self.style.ERROR(
            f"RUPTURA DE INTEGRIDAD en el evento #{resultado['evento_id']}: "
            f"{resultado['motivo']}."))
        raise SystemExit(1)
