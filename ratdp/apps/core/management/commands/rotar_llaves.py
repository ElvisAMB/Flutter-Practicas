"""Re-cifra los campos cifrados con la llave activa."""
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.fields import _EncryptedMixin


class Command(BaseCommand):
    help = (
        "Re-cifra todos los campos cifrados con la llave activa (DP_ENC_ACTIVE_KEY). "
        "Ejecutar tras agregar una llave nueva al keyring. No elimine llaves antiguas "
        "hasta que este comando finalice sin errores."
    )

    def add_arguments(self, parser):
        parser.add_argument("--lote", type=int, default=500)
        parser.add_argument("--simular", action="store_true")

    def handle(self, *args, **opciones):
        total = 0
        for modelo in apps.get_models():
            campos = [f.name for f in modelo._meta.concrete_fields
                      if isinstance(f, _EncryptedMixin)]
            if not campos:
                continue
            qs = modelo._base_manager.all().only("pk", *campos)
            n = qs.count()
            if not n:
                continue
            self.stdout.write(f"{modelo._meta.label}: {n} filas, campos {campos}")
            if opciones["simular"]:
                continue
            procesadas = 0
            for inicio in range(0, n, opciones["lote"]):
                with transaction.atomic():
                    for obj in qs[inicio:inicio + opciones["lote"]]:
                        # Leer descifra con la llave antigua; guardar cifra con la activa.
                        obj.save(update_fields=campos)
                        procesadas += 1
                self.stdout.write(f"  {procesadas}/{n}", ending="\r")
            total += procesadas
            self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Rotación completada: {total} registros."))
