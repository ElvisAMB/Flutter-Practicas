"""apps/indicadores/views.py — tablero de indicadores de gestión."""
import csv

from django.http import HttpResponse
from django.views.generic import TemplateView, View

from apps.core.mixins import VistaBase
from apps.rat.models import ActividadTratamiento, Brecha
from . import services


class TableroView(VistaBase, TemplateView):
    template_name = "indicadores/tablero.html"
    permiso_requerido = "rat.view_actividadtratamiento"
    titulo = "Tablero de indicadores"
    subtitulo = "Prueba de medidas — Art. 36 RLOPDP"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tablero"] = services.calcular(usar_cache=not self.request.GET.get("refrescar"))
        ctx["ultimas"] = ActividadTratamiento.objects.select_related("area").order_by(
            "-actualizado_en")[:8]
        ctx["brechas"] = Brecha.objects.select_related("actividad", "responsable").filter(
            estado__in=[Brecha.Estado.ABIERTA, Brecha.Estado.EN_PROCESO]
        ).order_by("fecha_compromiso")[:8]
        return ctx


class ExportarIndicadoresView(VistaBase, View):
    permiso_requerido = "rat.exportar_rat"

    def get(self, request):
        tablero = services.calcular(usar_cache=False)
        respuesta = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        respuesta["Content-Disposition"] = 'attachment; filename="indicadores_rat.csv"'
        respuesta.write("\ufeff")
        w = csv.writer(respuesta, delimiter=";")
        w.writerow(["Código", "Indicador", "Valor", "Unidad", "Meta", "Detalle"])
        for i in tablero.indicadores:
            w.writerow([i.codigo, i.nombre, i.valor, i.unidad, i.meta or "", i.detalle])
        return respuesta
