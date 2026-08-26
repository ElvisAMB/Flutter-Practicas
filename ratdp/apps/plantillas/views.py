"""apps/plantillas/views.py — gestión y renderizado de plantillas."""
from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.core.mixins import AsignarUsuarioMixin, BloquearAuditorMixin, VistaBase
from apps.rat.forms import BootstrapMixin
from apps.rat.models import ActividadTratamiento
from .models import DocumentoGenerado, Plantilla


class PlantillaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Plantilla
        fields = ("codigo", "nombre", "tipo", "descripcion", "cuerpo",
                  "esquema_campos", "version", "activa")
        widgets = {
            "cuerpo": forms.Textarea(attrs={"rows": 18, "class": "form-control font-monospace"}),
            "esquema_campos": forms.Textarea(attrs={"rows": 6, "class": "form-control font-monospace"}),
            "descripcion": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_cuerpo(self):
        cuerpo = self.cleaned_data["cuerpo"]
        temporal = Plantilla(cuerpo=cuerpo)
        try:
            temporal.validar()
        except ValueError as exc:
            raise forms.ValidationError(str(exc))
        return cuerpo


class PlantillaListView(VistaBase, ListView):
    model = Plantilla
    template_name = "plantillas/lista.html"
    context_object_name = "plantillas"
    permiso_requerido = "plantillas.view_plantilla"
    titulo = "Plantillas"
    subtitulo = "Formularios e informes reutilizables y extensibles"


class PlantillaCreateView(BloquearAuditorMixin, AsignarUsuarioMixin, VistaBase, CreateView):
    model = Plantilla
    form_class = PlantillaForm
    template_name = "plantillas/formulario.html"
    permiso_requerido = "plantillas.add_plantilla"
    success_url = reverse_lazy("plantillas:lista")
    titulo = "Nueva plantilla"


class PlantillaUpdateView(BloquearAuditorMixin, AsignarUsuarioMixin, VistaBase, UpdateView):
    model = Plantilla
    form_class = PlantillaForm
    template_name = "plantillas/formulario.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    permiso_requerido = "plantillas.change_plantilla"
    success_url = reverse_lazy("plantillas:lista")
    titulo = "Editar plantilla"


class PlantillaPreviewView(VistaBase, DetailView):
    model = Plantilla
    template_name = "plantillas/preview.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    context_object_name = "plantilla"
    permiso_requerido = "plantillas.view_plantilla"
    titulo = "Vista previa"

    def get_context_data(self, **kwargs):
        from django.conf import settings
        from django.utils import timezone

        ctx = super().get_context_data(**kwargs)
        actividad = ActividadTratamiento.objects.select_related("area").first()
        try:
            ctx["render"] = self.object.renderizar({
                "actividad": actividad,
                "area": getattr(actividad, "area", None),
                "usuario": self.request.user,
                "fecha": timezone.localdate(),
                "organizacion": settings.ORGANIZACION,
            })
        except Exception as exc:
            ctx["error"] = str(exc)
        return ctx


class PlantillaClonarView(BloquearAuditorMixin, VistaBase, View):
    permiso_requerido = "plantillas.add_plantilla"

    def post(self, request, uuid):
        original = get_object_or_404(Plantilla, uuid=uuid)
        nuevo_codigo = f"{original.codigo}-copia"
        sufijo = 1
        while Plantilla.objects.filter(codigo=nuevo_codigo).exists():
            sufijo += 1
            nuevo_codigo = f"{original.codigo}-copia{sufijo}"
        copia = original.clonar(nuevo_codigo, usuario=request.user)
        messages.success(request, f"Plantilla clonada como «{copia.codigo}».")
        return redirect("plantillas:editar", uuid=copia.uuid)
