"""apps/rat/views.py — CRUD, flujo de estados y exportación de la matriz."""

from __future__ import annotations

import csv

from django.conf import settings
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView, View,
)

from apps.auditoria.models import Accion, Evento
from apps.core.mixins import (
    AsignarUsuarioMixin, BloquearAuditorMixin, BorradoLogicoMixin,
    MensajeExitoMixin, VistaBase,
)
from .forms import ActividadForm, BrechaForm, CambioEstadoForm, FiltroActividadForm
from .models import ActividadTratamiento, Brecha, EstadoRegistro, SiNo


class ActividadListView(VistaBase, ListView):
    """
    Listado con filtros. Nota de rendimiento: la búsqueda ``q`` opera sobre
    ``codigo`` y ``nombre``, que **no** están cifrados precisamente para
    permitir ``icontains`` con índice. Buscar dentro de ``observaciones``
    (cifrado) es imposible por diseño.
    """

    model = ActividadTratamiento
    template_name = "rat/lista.html"
    context_object_name = "actividades"
    permiso_requerido = "rat.view_actividadtratamiento"
    titulo = "Matriz RAT"
    subtitulo = "Registro de Actividades de Tratamiento (Arts. 38–39 RLOPDP)"

    def get_paginate_by(self, queryset):
        return getattr(settings, "PAGINACION", 25)

    def get_queryset(self):
        qs = (
            ActividadTratamiento.objects.select_related("area", "criterio_conservacion")
            .prefetch_related("categorias_datos", "bases_licitud", "encargados")
        )
        f = FiltroActividadForm(self.request.GET or None)
        if f.is_valid():
            d = f.cleaned_data
            if d.get("q"):
                qs = qs.filter(Q(codigo__icontains=d["q"]) | Q(nombre__icontains=d["q"]))
            if d.get("area"):
                qs = qs.filter(area_id=d["area"])
            if d.get("estado"):
                qs = qs.filter(estado=d["estado"])
            if d.get("datos_especiales"):
                qs = qs.filter(datos_especiales=d["datos_especiales"])
            if d.get("transferencia"):
                qs = qs.filter(transferencia_internacional=d["transferencia"])
            if d.get("solo_alertas"):
                qs = qs.filter(
                    Q(datos_especiales=SiNo.NO_EVALUADO)
                    | Q(transferencia_internacional=SiNo.NO_EVALUADO)
                    | Q(eipd_requerida=SiNo.SI, eipd_codigo="")
                    | Q(fecha_ultima_revision__isnull=True)
                )
        self.filtro = f
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filtro"] = self.filtro
        ctx["total"] = self.get_queryset().count()
        return ctx


class ActividadDetailView(VistaBase, DetailView):
    model = ActividadTratamiento
    template_name = "rat/detalle.html"
    context_object_name = "actividad"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    permiso_requerido = "rat.view_actividadtratamiento"

    def get_queryset(self):
        return ActividadTratamiento.objects.select_related(
            "area", "criterio_conservacion", "validado_por"
        ).prefetch_related(
            "bases_licitud", "habilitantes_especiales", "categorias_datos",
            "categorias_titulares", "encargados", "corresponsables",
            "destinatarios_internos", "destinatarios_externos", "paises_destino",
            "mecanismos_transferencia", "medidas_seguridad", "sistemas",
            Prefetch("brechas", queryset=Brecha.objects.select_related("responsable")),
            "historial_estados",
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = self.object.codigo
        ctx["subtitulo"] = self.object.nombre
        ctx["form_estado"] = CambioEstadoForm(actividad=self.object)
        ctx["form_brecha"] = BrechaForm()
        return ctx


class ActividadCreateView(BloquearAuditorMixin, AsignarUsuarioMixin, MensajeExitoMixin,
                          VistaBase, CreateView):
    model = ActividadTratamiento
    form_class = ActividadForm
    template_name = "rat/formulario.html"
    permiso_requerido = "rat.add_actividadtratamiento"
    titulo = "Nueva actividad de tratamiento"
    subtitulo = "Recuerde: una finalidad = una fila"
    mensaje_exito = "Actividad registrada en estado Borrador."


class ActividadUpdateView(BloquearAuditorMixin, AsignarUsuarioMixin, MensajeExitoMixin,
                          VistaBase, UpdateView):
    model = ActividadTratamiento
    form_class = ActividadForm
    template_name = "rat/formulario.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    permiso_requerido = "rat.change_actividadtratamiento"
    titulo = "Editar actividad"
    mensaje_exito = "Actividad actualizada. El cambio quedó en la bitácora."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.estado == EstadoRegistro.HISTORICO:
            for campo in form.fields.values():
                campo.disabled = True
        return form


class ActividadDeleteView(BloquearAuditorMixin, BorradoLogicoMixin, VistaBase, DeleteView):
    model = ActividadTratamiento
    template_name = "rat/confirmar_baja.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    permiso_requerido = "rat.delete_actividadtratamiento"
    success_url = reverse_lazy("rat:lista")
    titulo = "Dar de baja actividad"


class CambiarEstadoView(BloquearAuditorMixin, VistaBase, View):
    permiso_requerido = "rat.validar_actividad"

    def post(self, request, uuid):
        actividad = get_object_or_404(ActividadTratamiento, uuid=uuid)
        form = CambioEstadoForm(request.POST, actividad=actividad)
        if form.is_valid():
            try:
                actividad.cambiar_estado(
                    form.cleaned_data["nuevo_estado"], usuario=request.user,
                    motivo=form.cleaned_data.get("motivo", ""),
                )
                messages.success(request, "Estado actualizado.")
            except Exception as exc:  # ValidationError de las reglas de negocio
                messages.error(request, f"No fue posible cambiar el estado: {exc}")
        else:
            messages.error(request, "Transición no válida.")
        return redirect(actividad.get_absolute_url())


class BrechaCreateView(BloquearAuditorMixin, AsignarUsuarioMixin, VistaBase, CreateView):
    model = Brecha
    form_class = BrechaForm
    template_name = "rat/formulario.html"
    permiso_requerido = "rat.change_actividadtratamiento"
    titulo = "Registrar brecha"

    def form_valid(self, form):
        form.instance.actividad = get_object_or_404(
            ActividadTratamiento, uuid=self.kwargs["uuid"])
        messages.success(self.request, "Brecha registrada con plan de acción.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.actividad.get_absolute_url()


class ExportarRATView(VistaBase, View):
    """
    Exportación CSV de la matriz.

    Toda exportación se audita explícitamente con el número de filas: es el
    punto de mayor riesgo de fuga masiva y el evento que un auditor buscará
    primero.
    """

    permiso_requerido = "rat.exportar_rat"

    COLUMNAS = [
        ("codigo", "3.1 Código"), ("nombre", "3.1 Actividad"), ("finalidad", "Finalidad"),
        ("area", "3.2 Área"), ("cargo_responsable", "3.3 Responsable"),
        ("corresponsables", "3.4 Corresponsables"), ("encargados", "3.5 Encargados"),
        ("bases_licitud", "3.6 Base de licitud (Art. 7 LOPDP)"),
        ("justificacion_base_licitud", "3.6 Justificación"),
        ("habilitantes_especiales", "3.7 Habilitante (Art. 26 LOPDP)"),
        ("categorias_datos", "3.8 Categorías de datos"),
        ("datos_especiales", "3.9 ¿Datos especiales?"),
        ("tipos_dato_especial", "3.9 Tipos"),
        ("categorias_titulares", "3.10 Interesados"), ("menores", "3.11 ¿Menores?"),
        ("destinatarios_internos", "3.12 Destinatarios internos"),
        ("destinatarios_externos", "3.13 Destinatarios externos"),
        ("transferencia_internacional", "3.14 ¿Transf. int.?"),
        ("paises_destino", "3.15 Países"), ("mecanismos_transferencia", "3.15 Mecanismos"),
        ("garantias_detalle", "3.15 Garantías"),
        ("plazo_conservacion", "3.16 Plazo"), ("criterio_conservacion", "3.17 Criterio"),
        ("medidas_seguridad", "3.18 Medidas"), ("eipd_requerida", "3.19 ¿EIPD?"),
        ("eipd_codigo", "3.19 Código EIPD"), ("estado", "3.20 Estado"),
        ("version", "Versión"), ("fecha_ultima_revision", "Última revisión"),
        ("nivel_riesgo", "Nivel de riesgo"),
    ]

    def get(self, request):
        qs = (
            ActividadTratamiento.objects.select_related("area", "criterio_conservacion")
            .prefetch_related(
                "bases_licitud", "habilitantes_especiales", "categorias_datos",
                "categorias_titulares", "encargados", "corresponsables",
                "destinatarios_internos", "destinatarios_externos", "paises_destino",
                "mecanismos_transferencia", "medidas_seguridad",
            )
        )
        respuesta = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        respuesta["Content-Disposition"] = 'attachment; filename="matriz_rat.csv"'
        respuesta.write("\ufeff")  # BOM para que Excel respete los acentos
        escritor = csv.writer(respuesta, delimiter=";")
        escritor.writerow([e for _, e in self.COLUMNAS])

        filas = 0
        for a in qs.iterator(chunk_size=500):
            fila = []
            for campo, _e in self.COLUMNAS:
                valor = getattr(a, campo, "")
                if hasattr(valor, "all"):
                    valor = " | ".join(str(x) for x in valor.all())
                elif callable(valor):
                    valor = valor()
                elif isinstance(valor, list):
                    valor = ", ".join(valor)
                fila.append(str(valor) if valor is not None else "")
            escritor.writerow(fila)
            filas += 1

        Evento.registrar(
            usuario=request.user, username=request.user.username,
            perfil=getattr(getattr(request.user, "perfil", None), "codigo", ""),
            accion=Accion.EXPORTACION, modelo="rat.ActividadTratamiento",
            objeto_repr=f"Exportación CSV de la matriz RAT",
            ip=request.META.get("REMOTE_ADDR"), ruta=request.path, metodo="GET",
            detalle={"filas_exportadas": filas, "formato": "csv"},
        )
        return respuesta
