"""
CRUD genérico de catálogos.

Un solo juego de vistas y plantillas atiende a todos los catálogos. Para agregar
uno nuevo basta con crear el modelo y añadir una entrada en REGISTRO: no hace
falta escribir vistas, formularios ni templates. Esta es la "plantilla para
gestión de catálogos" del punto 3.21.
"""
from django import forms
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.forms import MixinBootstrap

# slug -> (app_label, modelo, título, campos del formulario, campos buscables)
REGISTRO = {
    "areas": ("catalogos", "Area", "Áreas / unidades organizativas",
              ["codigo", "nombre", "responsable_cargo", "descripcion", "orden", "activo"],
              ["codigo", "nombre", "responsable_cargo"]),
    "bases-licitud": ("catalogos", "BaseLicitud", "Bases de licitud (Art. 7 LOPDP)",
                      ["codigo", "nombre", "descripcion", "referencia_legal",
                       "exige_ponderacion", "orden", "activo"],
                      ["codigo", "nombre"]),
    "habilitantes": ("catalogos", "HabilitanteEspecial",
                     "Habilitantes de categorías especiales (Art. 26 LOPDP)",
                     ["codigo", "nombre", "descripcion", "referencia_legal", "orden", "activo"],
                     ["codigo", "nombre"]),
    "categorias-datos": ("catalogos", "CategoriaDato", "Categorías de datos personales",
                         ["codigo", "nombre", "descripcion", "es_sensible", "referencia_legal",
                          "orden", "activo"],
                         ["codigo", "nombre"]),
    "categorias-interesados": ("catalogos", "CategoriaInteresado",
                               "Categorías de interesados (titulares)",
                               ["codigo", "nombre", "descripcion", "implica_menores",
                                "orden", "activo"],
                               ["codigo", "nombre"]),
    "procesos": ("catalogos", "ProcesoInterno", "Procesos internos",
                 ["codigo", "nombre", "descripcion", "orden", "activo"],
                 ["codigo", "nombre"]),
    "destinatarios-externos": ("catalogos", "DestinatarioExterno", "Destinatarios externos",
                               ["codigo", "nombre", "descripcion", "referencia_legal",
                                "es_ninguno", "orden", "activo"],
                               ["codigo", "nombre"]),
    "paises": ("catalogos", "Pais", "Países",
               ["codigo", "nombre", "nivel_adecuado", "referencia_legal", "orden", "activo"],
               ["codigo", "nombre"]),
    "mecanismos": ("catalogos", "MecanismoTransferencia",
                   "Mecanismos de transferencia internacional",
                   ["codigo", "nombre", "descripcion", "referencia_legal",
                    "requiere_autorizacion_previa", "orden", "activo"],
                   ["codigo", "nombre"]),
    "medidas": ("catalogos", "MedidaSeguridad", "Medidas de seguridad",
                ["codigo", "nombre", "tipo", "descripcion", "referencia_legal",
                 "orden", "activo"],
                ["codigo", "nombre"]),
    "criterios-eipd": ("catalogos", "CriterioEIPD", "Criterios de EIPD (Art. 42 LOPDP)",
                       ["codigo", "nombre", "descripcion", "referencia_legal",
                        "orden", "activo"],
                       ["codigo", "nombre"]),
    "estados": ("catalogos", "EstadoRegistro", "Estados del registro",
                ["codigo", "nombre", "descripcion", "es_vigente", "es_final", "color",
                 "orden", "activo"],
                ["codigo", "nombre"]),
    "terceros": ("catalogos", "Tercero", "Terceros (encargados y corresponsables)",
                 ["razon_social", "identificacion", "rol", "servicio", "pais",
                  "contrato_suscrito", "contrato_referencia", "contrato_fecha",
                  "clausulas_art41", "confidencialidad", "reparto_responsabilidades",
                  "activo", "notas"],
                 ["razon_social", "identificacion", "servicio"]),
}


def _config(slug):
    if slug not in REGISTRO:
        raise PermissionDenied("Catálogo no registrado.")
    app_label, modelo, titulo, campos, buscables = REGISTRO[slug]
    return apps.get_model(app_label, modelo), titulo, campos, buscables


def _formulario(modelo, campos):
    class _Form(MixinBootstrap, forms.ModelForm):
        class Meta:
            model_ = modelo
            model = modelo
            fields = campos
            widgets = {"contrato_fecha": forms.DateInput(attrs={"type": "date"})}
    return _Form


def _exigir(request, modelo, accion):
    codigo = f"{modelo._meta.app_label}.{accion}_{modelo._meta.model_name}"
    if not request.user.has_perm(codigo):
        raise PermissionDenied(f"Le falta el permiso {codigo}.")


@login_required
def indice(request):
    fichas = []
    for slug, (app_label, modelo, titulo, _c, _b) in REGISTRO.items():
        Modelo = apps.get_model(app_label, modelo)
        if request.user.has_perm(f"{app_label}.view_{Modelo._meta.model_name}"):
            fichas.append({"slug": slug, "titulo": titulo, "total": Modelo.objects.count()})
    return render(request, "catalogos/indice.html", {"fichas": fichas})


@login_required
def lista(request, slug):
    Modelo, titulo, campos, buscables = _config(slug)
    _exigir(request, Modelo, "view")
    qs = Modelo.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        filtro = Q()
        for campo in buscables:
            filtro |= Q(**{f"{campo}__icontains": q})
        qs = qs.filter(filtro)
    pagina = Paginator(qs, 25).get_page(request.GET.get("page"))
    columnas = [c for c in campos if c not in ("descripcion", "notas",
                                               "reparto_responsabilidades")][:6]
    filas = [
        {"obj": obj,
         "valores": [_render(obj, c) for c in columnas]}
        for obj in pagina.object_list
    ]
    contexto = {
        "slug": slug, "titulo": titulo, "page_obj": pagina, "filas": filas, "q": q,
        "encabezados": [Modelo._meta.get_field(c).verbose_name for c in columnas],
        "puede_editar": request.user.has_perm(
            f"{Modelo._meta.app_label}.change_{Modelo._meta.model_name}"),
        "puede_crear": request.user.has_perm(
            f"{Modelo._meta.app_label}.add_{Modelo._meta.model_name}"),
        "puede_borrar": request.user.has_perm(
            f"{Modelo._meta.app_label}.delete_{Modelo._meta.model_name}"),
    }
    return render(request, "catalogos/lista.html", contexto)


def _render(obj, campo):
    valor = getattr(obj, campo)
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if hasattr(obj, f"get_{campo}_display"):
        return getattr(obj, f"get_{campo}_display")()
    return valor if valor not in (None, "") else "—"


@login_required
def editar(request, slug, pk=None):
    Modelo, titulo, campos, _b = _config(slug)
    _exigir(request, Modelo, "change" if pk else "add")
    instancia = get_object_or_404(Modelo, pk=pk) if pk else None
    Form = _formulario(Modelo, campos)
    if request.method == "POST":
        form = Form(request.POST, instance=instancia)
        if form.is_valid():
            objeto = form.save(commit=False)
            if hasattr(objeto, "actualizado_por"):
                if not objeto.pk:
                    objeto.creado_por = request.user
                objeto.actualizado_por = request.user
            objeto.save()
            form.save_m2m()
            messages.success(request, "Registro guardado.")
            return redirect("catalogos:lista", slug=slug)
        messages.error(request, "Revise los campos marcados.")
    else:
        form = Form(instance=instancia)
    return render(request, "catalogos/form.html",
                  {"form": form, "titulo": titulo, "slug": slug, "objeto": instancia})


@login_required
def eliminar(request, slug, pk):
    Modelo, titulo, _c, _b = _config(slug)
    _exigir(request, Modelo, "delete")
    objeto = get_object_or_404(Modelo, pk=pk)
    if request.method == "POST":
        try:
            objeto.delete()
            messages.success(request, "Registro eliminado.")
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar: hay actividades del RAT que lo referencian. "
                "Desactívelo en su lugar para conservar la trazabilidad histórica.")
        return redirect("catalogos:lista", slug=slug)
    return render(request, "catalogos/confirmar_eliminar.html",
                  {"objeto": objeto, "titulo": titulo, "slug": slug})
