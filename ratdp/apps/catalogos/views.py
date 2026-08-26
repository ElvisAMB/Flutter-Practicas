"""
apps/catalogos/views.py
=======================
CRUD genérico para todos los catálogos.

En lugar de escribir ocho listados y ocho formularios casi idénticos, se define
un registro (``CATALOGOS``) y tres vistas parametrizadas por ``slug``. Añadir un
catálogo nuevo = una entrada en el diccionario. Esto es lo que hace el
mantenimiento barato.
"""

from __future__ import annotations

from django import forms
from django.apps import apps
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.core.mixins import (
    AsignarUsuarioMixin, BloquearAuditorMixin, BorradoLogicoMixin, VistaBase,
)
from apps.rat.forms import BootstrapMixin

#: slug -> (modelo, campos del formulario, etiqueta)
CATALOGOS = {
    "macroprocesos": ("catalogos.Macroproceso",
                      ["codigo", "nombre", "descripcion", "orden", "activo"],
                      "Macroprocesos"),
    "areas": ("catalogos.Area",
              ["codigo", "nombre", "macroproceso", "cargo_responsable", "padre",
               "descripcion", "orden", "activo"],
              "Áreas / Unidades organizativas"),
    "bases-licitud": ("catalogos.BaseLicitud",
                      ["codigo", "numeral", "nombre", "articulo", "descripcion",
                       "requiere_test_ponderacion", "requiere_consentimiento",
                       "equivalencia_rgpd", "activo"],
                      "Bases de licitud (Art. 7 LOPDP)"),
    "habilitantes": ("catalogos.HabilitanteEspecial",
                     ["codigo", "literal", "nombre", "articulo", "descripcion", "activo"],
                     "Habilitantes de categorías especiales (Art. 26 LOPDP)"),
    "categorias-datos": ("catalogos.CategoriaDato",
                         ["codigo", "nombre", "tipo_especial", "ejemplos",
                          "descripcion", "orden", "activo"],
                         "Categorías de datos personales"),
    "categorias-titulares": ("catalogos.CategoriaTitular",
                             ["codigo", "nombre", "puede_incluir_menores",
                              "descripcion", "orden", "activo"],
                             "Categorías de titulares"),
    "terceros": ("catalogos.Tercero",
                 ["razon_social", "identificacion", "rol_habitual", "pais",
                  "tiene_contrato", "codigo_contrato", "fecha_contrato",
                  "fecha_vencimiento", "clausula_confidencialidad",
                  "clausulas_art41_completas", "subencargados",
                  "contacto_nombre", "contacto_email", "activo"],
                 "Terceros (encargados y destinatarios)"),
    "mecanismos": ("catalogos.MecanismoTransferencia",
                   ["codigo", "nombre", "articulo", "requiere_autorizacion_spdp",
                    "descripcion", "activo"],
                   "Mecanismos de transferencia internacional"),
    "medidas": ("catalogos.MedidaSeguridad",
                ["codigo", "nombre", "tipo", "descripcion", "orden", "activo"],
                "Medidas de seguridad"),
    "criterios": ("catalogos.CriterioConservacion",
                  ["codigo", "nombre", "norma_referencia", "plazo_sugerido_meses",
                   "es_limite_imperativo", "descripcion", "activo"],
                  "Criterios de conservación"),
    "sistemas": ("catalogos.SistemaInformacion",
                 ["codigo", "nombre", "alojamiento", "pais", "proveedor",
                  "contiene_datos_personales", "ambiente_pruebas_con_datos_reales",
                  "descripcion", "activo"],
                 "Sistemas de información"),
}


def _config(slug: str):
    if slug not in CATALOGOS:
        raise Http404("Catálogo no registrado.")
    ruta, campos, etiqueta = CATALOGOS[slug]
    app_label, modelo = ruta.split(".")
    return apps.get_model(app_label, modelo), campos, etiqueta


def _form_class(modelo, campos):
    return forms.modelform_factory(modelo, form=type("F", (BootstrapMixin, forms.ModelForm), {}),
                                   fields=campos)


class CatalogoMixin(VistaBase):
    def dispatch(self, request, *args, **kwargs):
        self.modelo, self.campos, self.etiqueta = _config(kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    @property
    def permiso_requerido(self):
        accion = {"crear": "add", "editar": "change", "baja": "delete"}.get(
            self.request.resolver_match.url_name, "view")
        return f"{self.modelo._meta.app_label}.{accion}_{self.modelo._meta.model_name}"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = self.etiqueta
        ctx["slug"] = self.kwargs["slug"]
        ctx["catalogos"] = [(s, v[2]) for s, v in CATALOGOS.items()]
        return ctx


class CatalogoListView(CatalogoMixin, ListView):
    template_name = "catalogos/lista.html"
    context_object_name = "objetos"
    paginate_by = 30

    def get_queryset(self):
        qs = self.modelo.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            campo = "razon_social" if hasattr(self.modelo, "razon_social") else "nombre"
            qs = qs.filter(**{f"{campo}__icontains": q})
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["columnas"] = self.campos[:5]
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class CatalogoCreateView(BloquearAuditorMixin, AsignarUsuarioMixin, CatalogoMixin, CreateView):
    template_name = "catalogos/formulario.html"

    def get_form_class(self):
        return _form_class(self.modelo, self.campos)

    def get_success_url(self):
        messages.success(self.request, "Registro creado.")
        return reverse("catalogos:lista", args=[self.kwargs["slug"]])


class CatalogoUpdateView(BloquearAuditorMixin, AsignarUsuarioMixin, CatalogoMixin, UpdateView):
    template_name = "catalogos/formulario.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_form_class(self):
        return _form_class(self.modelo, self.campos)

    def get_object(self, queryset=None):
        return self.modelo.objects.get(uuid=self.kwargs["uuid"])

    def get_success_url(self):
        messages.success(self.request, "Registro actualizado.")
        return reverse("catalogos:lista", args=[self.kwargs["slug"]])


class CatalogoDeleteView(BloquearAuditorMixin, CatalogoMixin, DeleteView):
    template_name = "catalogos/confirmar_baja.html"

    def get_object(self, queryset=None):
        return self.modelo.objects.get(uuid=self.kwargs["uuid"])

    def form_valid(self, form):
        objeto = self.get_object()
        objeto.delete(usuario=self.request.user)
        messages.warning(self.request, f"«{objeto}» dado de baja (borrado lógico).")
        return redirect("catalogos:lista", slug=self.kwargs["slug"])
