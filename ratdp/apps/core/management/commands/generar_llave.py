"""Genera llaves criptográficas para .env."""
from django.core.management.base import BaseCommand

from apps.core.crypto import generar_llave


class Command(BaseCommand):
    help = "Genera llaves AES-256 y de índice ciego listas para el archivo .env."

    def add_arguments(self, parser):
        parser.add_argument("--cantidad", type=int, default=1)

    def handle(self, *args, **opciones):
        llaves = {str(i + 1): generar_llave() for i in range(opciones["cantidad"])}
        import json

        self.stdout.write(self.style.SUCCESS("Copie estas líneas en su archivo .env:\n"))
        self.stdout.write(f"DP_ENC_KEYS={json.dumps(llaves)}")
        self.stdout.write(f"DP_ENC_ACTIVE_KEY={max(llaves)}")
        self.stdout.write(f"DP_INDEX_KEY={generar_llave()}")
        self.stdout.write(self.style.WARNING(
            "\nGuarde estas llaves fuera del repositorio y respáldelas: sin ellas los "
            "datos cifrados son irrecuperables. La llave de índice NO debe rotarse sin "
            "recalcular todos los índices ciegos."
        ))
