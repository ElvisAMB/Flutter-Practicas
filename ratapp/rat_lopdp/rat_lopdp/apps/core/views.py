"""Vistas CRUD genéricas reutilizables (base para catálogos y futuros módulos)."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView


class MixinAuditoria:
    """Sella creado_por / actualizado_por al guardar."""

    def form_valid(self, form):
        if hasattr(form.instance, "actualizado_por"):
            if not form.instance.pk and hasattr(form.instance, "creado_por"):
                form.instance.creado_por = self.request.user
            form.instance.actualizado_por = self.request.user
        return super().form_valid(form)


class MixinMensaje:
    mensaje_exito = "Cambios guardados."

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, self.mensaje_exito)
        return respuesta


class ListaBuscableView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Listado con búsqueda por texto libre sobre `campos_busqueda`."""

    paginate_by = 20
    campos_busqueda = ()

    def get_queryset(self):
        qs = super().get_queryset()
        texto = self.request.GET.get("q", "").strip()
        if texto and self.campos_busqueda:
            filtro = Q()
            for campo in self.campos_busqueda:
                filtro |= Q(**{f"{campo}__icontains": texto})
            qs = qs.filter(filtro)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class CrearView(LoginRequiredMixin, PermissionRequiredMixin, MixinMensaje, MixinAuditoria, CreateView):
    mensaje_exito = "Registro creado."


class EditarView(LoginRequiredMixin, PermissionRequiredMixin, MixinMensaje, MixinAuditoria, UpdateView):
    mensaje_exito = "Registro actualizado."


class DetalleView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    pass


class EliminarView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    def form_valid(self, form):
        messages.success(self.request, "Registro eliminado.")
        return super().form_valid(form)
