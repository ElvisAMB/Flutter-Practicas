"""Archiva y purga eventos antiguos conforme a la política de retención."""
import csv
import hashlib
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.auditoria.models import Evento, PurgaBitacora


class Command(BaseCommand):
    help = (
        "Exporta a CSV firmado y elimina los eventos anteriores al plazo de retención. "
        "La purga se registra en PurgaBitacora y en la propia bitácora."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dias", type=int,
                            default=getattr(settings, "RETENCION_BITACORA_DIAS", 2555))
        parser.add_argument("--destino", default=str(settings.BASE_DIR / "archivo"))
        parser.add_argument("--confirmar", action="store_true",
                            help="Sin este indicador solo se simula.")

    def handle(self, *args, **o):
        corte = timezone.now() - timezone.timedelta(days=o["dias"])
        qs = Evento.objects.filter(fecha__lt=corte).order_by("id")
        n = qs.count()
        if not n:
            self.stdout.write("No hay eventos que purgar.")
            return
        primero, ultimo = qs.first(), qs.last()
        self.stdout.write(f"{n} eventos anteriores a {corte:%Y-%m-%d} "
                          f"(#{primero.id} a #{ultimo.id}).")
        if not o["confirmar"]:
            self.stdout.write(self.style.WARNING("Simulación. Use --confirmar para ejecutar."))
            return

        destino = Path(o["destino"])
        destino.mkdir(parents=True, exist_ok=True)
        archivo = destino / f"bitacora_{primero.id}_{ultimo.id}.csv"
        with archivo.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(["id", "fecha", "username", "accion", "modelo", "objeto_id",
                        "objeto_repr", "exitoso", "ip", "ruta", "hash_anterior", "hash_actual"])
            for e in qs.iterator(chunk_size=2000):
                w.writerow([e.id, e.fecha.isoformat(), e.username, e.accion, e.modelo,
                            e.objeto_id, e.objeto_repr, e.exitoso, e.ip, e.ruta,
                            e.hash_anterior, e.hash_actual])
        digest = hashlib.sha256(archivo.read_bytes()).hexdigest()

        # Borrado directo en SQL: Evento.delete() está bloqueado a propósito.
        with connection.cursor() as cur:
            cur.execute(
                f"DELETE FROM {Evento._meta.db_table} WHERE id <= %s", [ultimo.id])

        PurgaBitacora.objects.create(
            ejecutada_por="management-command", desde=primero.fecha, hasta=ultimo.fecha,
            eventos_archivados=n, archivo=str(archivo), hash_archivo=digest,
        )
        self.stdout.write(self.style.SUCCESS(
            f"{n} eventos archivados en {archivo} (SHA-256 {digest[:16]}…) y purgados.\n"
            f"IMPORTANTE: la cadena hash se reinicia tras la purga; conserve el archivo "
            f"como evidencia del tramo eliminado."))
