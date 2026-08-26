"""apps/auditoria/views.py — consulta y verificación de la bitácora."""
import csv

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.dateparse import parse_date
from django.views.generic import ListView, View

from apps.core.mixins import VistaBase
from .models import Accion, Evento


class BitacoraListView(VistaBase, ListView):
    """
    Consulta de la bitácora.

    Todos los filtros usan columnas indexadas y no cifradas. El campo
    ``detalle`` se descifra solo en la fila que el usuario expande, no en el
    listado: descifrar 25 detalles por página es barato; descifrar un millón
    para filtrar no lo sería.
    """

    model = Evento
    template_name = "auditoria/bitacora.html"
    context_object_name = "eventos"
    paginate_by = 50
    permiso_requerido = "accounts.ver_bitacora"
    titulo = "Bitácora de auditoría"
    subtitulo = "Registro inmutable y encadenado de accesos y cambios"

    def get_queryset(self):
        qs = Evento.objects.select_related("usuario").all()
        g = self.request.GET
        if g.get("usuario"):
            qs = qs.filter(username__icontains=g["usuario"])
        if g.get("accion"):
            qs = qs.filter(accion=g["accion"])
        if g.get("modelo"):
            qs = qs.filter(modelo__icontains=g["modelo"])
        if g.get("objeto_id"):
            qs = qs.filter(objeto_id=g["objeto_id"])
        if g.get("ip"):
            qs = qs.filter(ip=g["ip"])
        if g.get("desde") and parse_date(g["desde"]):
            qs = qs.filter(fecha__date__gte=parse_date(g["desde"]))
        if g.get("hasta") and parse_date(g["hasta"]):
            qs = qs.filter(fecha__date__lte=parse_date(g["hasta"]))
        if g.get("solo_fallidos"):
            qs = qs.filter(exitoso=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["acciones"] = Accion.choices
        ctx["filtros"] = self.request.GET
        return ctx


class VerificarCadenaView(VistaBase, View):
    """Verifica la integridad de la cadena hash de la bitácora."""

    permiso_requerido = "accounts.ver_bitacora"

    def post(self, request):
        resultado = Evento.verificar_cadena()
        if resultado["ok"]:
            messages.success(
                request,
                f"Integridad verificada: {resultado['revisados']} eventos encadenados "
                f"correctamente.")
        else:
            messages.error(
                request,
                f"¡ALERTA! Ruptura de la cadena en el evento #{resultado['evento_id']}: "
                f"{resultado['motivo']}. Notifique al DPD y a Seguridad de la Información.")
        return redirect("auditoria:bitacora")


class ExportarBitacoraView(VistaBase, View):
    permiso_requerido = ["accounts.ver_bitacora", "accounts.exportar_datos"]

    def get(self, request):
        qs = Evento.objects.all()[:100000]
        respuesta = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        respuesta["Content-Disposition"] = 'attachment; filename="bitacora.csv"'
        respuesta.write("\ufeff")
        w = csv.writer(respuesta, delimiter=";")
        w.writerow(["Id", "Fecha", "Usuario", "Perfil", "Acción", "Entidad", "Objeto",
                    "Descripción", "Éxito", "IP", "Ruta", "Hash"])
        filas = 0
        for e in qs.iterator(chunk_size=1000):
            w.writerow([e.id, e.fecha.isoformat(), e.username, e.perfil, e.accion,
                        e.modelo, e.objeto_id, e.objeto_repr, e.exitoso, e.ip, e.ruta,
                        e.hash_actual])
            filas += 1
        Evento.registrar(
            usuario=request.user, username=request.user.username,
            accion=Accion.EXPORTACION, modelo="auditoria.Evento",
            objeto_repr="Exportación de bitácora", ip=request.META.get("REMOTE_ADDR"),
            detalle={"filas": filas},
        )
        return respuesta
