import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.catalogos.models import Area, EstadoRegistro
from .forms import (
    ActividadTratamientoForm, BaseLicitudFormSet, DestinatarioExternoFormSet,
    FiltroActividadForm, TransferenciaFormSet,
)
from .models import ActividadTratamiento


class ActividadListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ActividadTratamiento
    permission_required = "rat.view_actividadtratamiento"
    template_name = "rat/actividad_list.html"
    context_object_name = "actividades"
    paginate_by = 15

    def get_queryset(self):
        qs = (ActividadTratamiento.objects
              .select_related("area", "estado", "proceso_interno")
              .prefetch_related("categorias_datos"))
        f = FiltroActividadForm(self.request.GET or None)
        if f.is_valid():
            d = f.cleaned_data
            if d.get("q"):
                qs = qs.filter(
                    Q(codigo__icontains=d["q"]) | Q(nombre_corto__icontains=d["q"])
                    | Q(finalidad__icontains=d["q"]))
            if d.get("area"):
                qs = qs.filter(area=d["area"])
            if d.get("estado"):
                qs = qs.filter(estado=d["estado"])
            if d.get("datos_especiales") in ("0", "1"):
                qs = qs.filter(datos_especiales=d["datos_especiales"] == "1")
            if d.get("transferencia") in ("0", "1"):
                qs = qs.filter(transferencia_internacional=d["transferencia"] == "1")
            if d.get("eipd") in ("0", "1"):
                qs = qs.filter(eipd_requerida=d["eipd"] == "1")
        self.filtro = f
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filtro"] = self.filtro
        parametros = self.request.GET.copy()
        parametros.pop("page", None)
        ctx["querystring"] = parametros.urlencode()
        ctx["total"] = self.get_queryset().count()
        return ctx


class ActividadDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ActividadTratamiento
    permission_required = "rat.view_actividadtratamiento"
    template_name = "rat/actividad_detail.html"
    context_object_name = "actividad"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["estados"] = EstadoRegistro.objects.filter(activo=True)
        return ctx


class ActividadFormMixin:
    """Coordina el formulario principal con los tres formsets dependientes."""

    model = ActividadTratamiento
    form_class = ActividadTratamientoForm
    template_name = "rat/actividad_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        datos = self.request.POST if self.request.method == "POST" else None
        instancia = self.object
        ctx["fs_bases"] = BaseLicitudFormSet(datos, instance=instancia, prefix="bases")
        ctx["fs_destinatarios"] = DestinatarioExternoFormSet(
            datos, instance=instancia, prefix="dest")
        fs_transf = TransferenciaFormSet(datos, instance=instancia, prefix="transf")
        fs_transf.instance_transferencia_marcada = bool(
            self.request.POST.get("transferencia_internacional")
        ) if self.request.method == "POST" else False
        ctx["fs_transferencias"] = fs_transf
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        fs_bases = ctx["fs_bases"]
        fs_dest = ctx["fs_destinatarios"]
        fs_transf = ctx["fs_transferencias"]

        if not (fs_bases.is_valid() and fs_dest.is_valid() and fs_transf.is_valid()):
            messages.error(self.request, "Revise los errores marcados en rojo.")
            return self.form_invalid(form)

        with transaction.atomic():
            es_nuevo = form.instance.pk is None
            estado_anterior = None
            if not es_nuevo:
                estado_anterior = ActividadTratamiento.objects.get(pk=form.instance.pk).estado
                form.instance.version = form.instance.version + 1
            if es_nuevo:
                form.instance.creado_por = self.request.user
            form.instance.actualizado_por = self.request.user
            self.object = form.save()

            for fs in (fs_bases, fs_dest, fs_transf):
                fs.instance = self.object
                fs.save()

            self.object.registrar_version(
                usuario=self.request.user,
                estado_anterior=estado_anterior,
                nota="Alta del registro" if es_nuevo else "Actualización del registro",
            )

        messages.success(
            self.request,
            f"Actividad {self.object.codigo} guardada (versión {self.object.version}).")
        return redirect(self.object.get_absolute_url())


class ActividadCreateView(LoginRequiredMixin, PermissionRequiredMixin,
                          ActividadFormMixin, CreateView):
    permission_required = "rat.add_actividadtratamiento"


class ActividadUpdateView(LoginRequiredMixin, PermissionRequiredMixin,
                          ActividadFormMixin, UpdateView):
    permission_required = "rat.change_actividadtratamiento"


class ActividadDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ActividadTratamiento
    permission_required = "rat.delete_actividadtratamiento"
    template_name = "rat/actividad_confirm_delete.html"
    success_url = reverse_lazy("rat:actividad_list")

    def form_valid(self, form):
        messages.warning(
            self.request,
            f"Actividad {self.object.codigo} eliminada. Para trazabilidad, lo recomendable "
            f"es cesarla, no borrarla.")
        return super().form_valid(form)


@login_required
@permission_required("rat.view_actividadtratamiento", raise_exception=True)
def tablero(request):
    qs = ActividadTratamiento.objects.all()
    estados = (EstadoRegistro.objects.filter(activo=True)
               .annotate(total=Count("actividades")).order_by("orden"))
    areas = (Area.objects.filter(activo=True)
             .annotate(total=Count("actividades")).filter(total__gt=0).order_by("-total"))
    contexto = {
        "total": qs.count(),
        "con_especiales": qs.filter(datos_especiales=True).count(),
        "con_menores": qs.filter(menores=True).count(),
        "con_transferencia": qs.filter(transferencia_internacional=True).count(),
        "con_eipd": qs.filter(eipd_requerida=True).count(),
        "estados": estados,
        "areas": areas,
        "pendientes": [a for a in qs.select_related("estado", "area") if a.alertas][:15],
    }
    return render(request, "rat/tablero.html", contexto)


@login_required
@permission_required("rat.exportar_rat", raise_exception=True)
def exportar_csv(request):
    respuesta = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    marca = timezone.localdate().isoformat()
    respuesta["Content-Disposition"] = f'attachment; filename="RAT_{marca}.csv"'
    escritor = csv.writer(respuesta, delimiter=";")
    escritor.writerow([
        "3.1 Código", "3.1 Nombre", "3.1 Finalidad", "3.2 Área", "3.3 Responsable (cargo)",
        "3.4 Corresponsable", "3.5 Encargados", "3.6 Bases de licitud", "3.7 Habilitante Art. 26",
        "3.8 Categorías de datos", "3.9 Datos especiales", "3.10 Titulares", "3.11 Menores",
        "3.12 Proceso interno", "3.12 Destinatarios internos", "3.13 Destinatarios externos",
        "3.14 Transferencia internacional", "3.15 País / mecanismo", "3.16 Plazo",
        "3.17 Criterio y destino final", "3.18 Medidas", "3.19 EIPD", "3.20 Estado",
        "Versión", "Última actualización",
    ])
    consulta = (ActividadTratamiento.objects
                .select_related("area", "estado", "proceso_interno")
                .prefetch_related("categorias_datos", 
                                   "categorias_interesados", 
                                  #"encargados",
                                  #"corresponsables", 
                                  "habilitantes_especiales",
                                  "medidas_seguridad", 
                                  "transferencias__pais",
                                  "transferencias__mecanismo",
                                  "baselicitudactividad_set__base",
                                  "destinatarioexternoactividad_set__destinatario"
                                  )
                )
    for a in consulta:
        escritor.writerow([
            a.codigo, a.nombre_corto, a.finalidad, a.area.nombre, a.responsable_cargo,
            "; ".join(a.corresponsables or a.get_corresponsable_situacion_display()),
            "; ".join(a.encargados or "N/A"),
            " | ".join(f"{b.base.codigo} {b.base.nombre}: {b.justificacion}"
                       for b in a.baselicitudactividad_set.all()),
            "; ".join(h.codigo for h in a.habilitantes_especiales.all()) or "N/A",
            "; ".join(c.nombre for c in a.categorias_datos.all()),
            "SÍ" if a.datos_especiales else "NO",
            "; ".join(c.nombre for c in a.categorias_interesados.all()),
            "SÍ" if a.menores else "NO",
            a.proceso_interno.nombre, a.destinatarios_internos,
            " | ".join(f"{d.destinatario.nombre}: {d.fundamento}"
                       for d in a.destinatarioexternoactividad_set.all()),
            "SÍ" if a.transferencia_internacional else "NO",
            " | ".join(f"{t.pais.nombre} — {t.mecanismo.codigo} {t.mecanismo.nombre}"
                       for t in a.transferencias.all()) or "N/A",
            a.plazo_conservacion,
            f"{a.criterio_plazo} — Destino: {a.get_destino_final_display()}",
            "; ".join(m.nombre for m in a.medidas_seguridad.all()) + (
                f" | {a.medidas_adicionales}" if a.medidas_adicionales else ""),
            (f"SÍ ({a.eipd_codigo}, {a.eipd_fecha})" if a.eipd_requerida else "NO"),
            a.estado.nombre, a.version, a.actualizado_en.strftime("%Y-%m-%d %H:%M"),
        ])
    return respuesta


@login_required
@permission_required("rat.validar_actividad", raise_exception=True)
def cambiar_estado(request, pk):
    actividad = get_object_or_404(ActividadTratamiento, pk=pk)
    if request.method != "POST":
        return redirect(actividad.get_absolute_url())
    nuevo = get_object_or_404(EstadoRegistro, pk=request.POST.get("estado"))
    anterior = actividad.estado
    if nuevo.es_final and not actividad.fecha_cese:
        messages.error(request, "Registre primero la fecha de cese antes de pasar a histórico.")
        return redirect(actividad.get_absolute_url())
    actividad.estado = nuevo
    actividad.version += 1
    actividad.actualizado_por = request.user
    actividad.save()
    actividad.registrar_version(
        usuario=request.user, estado_anterior=anterior,
        nota=request.POST.get("nota", "")[:500] or f"Cambio de estado a {nuevo.nombre}")
    messages.success(request, f"Estado actualizado a «{nuevo.nombre}».")
    return redirect(actividad.get_absolute_url())
