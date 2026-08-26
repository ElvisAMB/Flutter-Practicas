"""apps/accounts/views.py — autenticación y gestión de usuarios, perfiles y accesos."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.auditoria.models import Accion, Evento
from apps.core.mixins import SoloAdministradorMixin, VistaBase
from .forms import (
    AsignarPermisosForm, LoginForm, PerfilForm, UsuarioCreateForm, UsuarioUpdateForm,
)
from .models import Perfil, PerfilSistema, SesionAcceso, Usuario


# ------------------------------------------------------------ autenticación
class IngresoView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True


class SalidaView(LogoutView):
    pass


class CambiarPasswordView(VistaBase, PasswordChangeView):
    template_name = "accounts/cambiar_password.html"
    success_url = reverse_lazy("indicadores:tablero")
    titulo = "Cambiar contraseña"

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        usuario = self.request.user
        usuario.debe_cambiar_password = False
        usuario.ultimo_cambio_password = timezone.now()
        usuario.save(update_fields=["debe_cambiar_password", "ultimo_cambio_password"])
        update_session_auth_hash(self.request, usuario)
        Evento.registrar(
            usuario=usuario, username=usuario.username, accion=Accion.CAMBIO_PASSWORD,
            objeto_repr=str(usuario), ip=self.request.META.get("REMOTE_ADDR"),
        )
        messages.success(self.request, "Contraseña actualizada.")
        return respuesta


# --------------------------------------------------------- gestión usuarios
class UsuarioListView(SoloAdministradorMixin, ListView):
    """
    Solo el administrador ve y gestiona usuarios.

    Nota sobre la búsqueda: el nombre y el correo están cifrados, de modo que
    ``icontains`` es imposible. Se busca por ``username`` (en claro) y por
    correo exacto vía índice ciego. Es la contrapartida deliberada del cifrado.
    """

    model = Usuario
    template_name = "accounts/lista_usuarios.html"
    context_object_name = "usuarios"
    paginate_by = 25
    titulo = "Usuarios"
    subtitulo = "Altas, bajas y asignación de perfiles"

    def get_queryset(self):
        from apps.core.crypto import blind_index

        qs = Usuario.objects.select_related("perfil__grupo", "area").order_by("username")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(username__icontains=q)
                | Q(email_bidx=blind_index(q, scope="usuario.email"))
                | Q(documento_bidx=blind_index(q, scope="usuario.documento"))
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["ayuda_busqueda"] = (
            "El nombre y el correo están cifrados: la búsqueda por correo o "
            "documento debe ser exacta; por usuario admite coincidencia parcial."
        )
        return ctx


class UsuarioCreateView(SoloAdministradorMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = "accounts/formulario_usuario.html"
    success_url = reverse_lazy("gestion:usuarios")
    titulo = "Nuevo usuario"

    def form_valid(self, form):
        form.instance.creado_por = self.request.user if hasattr(Usuario, "creado_por") else None
        respuesta = super().form_valid(form)
        messages.success(
            self.request,
            f"Usuario «{self.object.username}» creado. Debe cambiar su contraseña "
            f"en el primer ingreso.",
        )
        return respuesta


class UsuarioUpdateView(SoloAdministradorMixin, UpdateView):
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = "accounts/formulario_usuario.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    success_url = reverse_lazy("gestion:usuarios")
    titulo = "Editar usuario"

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado.")
        return super().form_valid(form)


class UsuarioDetailView(SoloAdministradorMixin, DetailView):
    model = Usuario
    template_name = "accounts/detalle_usuario.html"
    context_object_name = "usuario_obj"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    titulo = "Detalle de usuario"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["sesiones"] = SesionAcceso.objects.filter(usuario=self.object)[:20]
        ctx["eventos"] = Evento.objects.filter(usuario=self.object)[:50]
        return ctx


class ToggleUsuarioView(SoloAdministradorMixin, View):
    """Activa o desactiva un usuario. No se eliminan usuarios: se desactivan."""

    def post(self, request, uuid):
        usuario = get_object_or_404(Usuario, uuid=uuid)
        if usuario == request.user:
            messages.error(request, "No puede desactivar su propia cuenta.")
            return redirect("gestion:usuarios")
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=["is_active"])
        messages.warning(
            request, f"Usuario «{usuario.username}» "
                     f"{'activado' if usuario.is_active else 'desactivado'}.")
        return redirect("gestion:usuarios")


class DesbloquearUsuarioView(SoloAdministradorMixin, View):
    def post(self, request, uuid):
        usuario = get_object_or_404(Usuario, uuid=uuid)
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
        messages.success(request, f"Usuario «{usuario.username}» desbloqueado.")
        return redirect("gestion:usuario_detalle", uuid=uuid)


# ---------------------------------------------------------- gestión perfiles
class PerfilListView(SoloAdministradorMixin, ListView):
    model = Perfil
    template_name = "accounts/lista_perfiles.html"
    context_object_name = "perfiles"
    titulo = "Perfiles de acceso"
    subtitulo = "Perfiles fijos del sistema y perfiles personalizados"

    def get_queryset(self):
        return Perfil.objects.select_related("grupo").prefetch_related("grupo__permissions")


class PerfilCreateView(SoloAdministradorMixin, CreateView):
    model = Perfil
    form_class = PerfilForm
    template_name = "accounts/formulario_perfil.html"
    success_url = reverse_lazy("gestion:perfiles")
    titulo = "Nuevo perfil personalizado"

    def form_valid(self, form):
        messages.success(self.request, "Perfil creado. Asigne ahora sus permisos.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("gestion:perfil_permisos", args=[self.object.pk])


class PerfilUpdateView(SoloAdministradorMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = "accounts/formulario_perfil.html"
    success_url = reverse_lazy("gestion:perfiles")
    titulo = "Editar perfil"

    def get_object(self, queryset=None):
        perfil = super().get_object(queryset)
        if perfil.es_sistema and perfil.codigo in (
            PerfilSistema.ADMINISTRADOR, PerfilSistema.AUDITOR
        ):
            messages.warning(
                self.request,
                "Los perfiles ADMINISTRADOR y AUDITOR tienen permisos fijos por diseño: "
                "solo puede editar su descripción.",
            )
        return perfil


class PerfilPermisosView(SoloAdministradorMixin, View):
    """
    Asignación granular de permisos. Es la única puerta de cambio de accesos y
    cada modificación se audita como CAMBIO_PERMISO.
    """

    template_name = "accounts/permisos_perfil.html"

    def get(self, request, pk):
        from django.shortcuts import render

        perfil = get_object_or_404(Perfil, pk=pk)
        form = AsignarPermisosForm(perfil=perfil)
        return render(request, self.template_name, {
            "perfil": perfil, "form": form,
            "titulo": f"Permisos de «{perfil.nombre}»",
            "bloqueado": not perfil.permite_edicion_permisos,
        })

    def post(self, request, pk):
        perfil = get_object_or_404(Perfil, pk=pk)
        if not perfil.permite_edicion_permisos:
            messages.error(request, "Este perfil tiene permisos fijos y no admite edición.")
            return redirect("gestion:perfiles")
        form = AsignarPermisosForm(request.POST, perfil=perfil)
        if form.is_valid():
            antes = set(perfil.grupo.permissions.values_list("codename", flat=True))
            perfil.grupo.permissions.set(form.cleaned_data["permisos"])
            despues = set(perfil.grupo.permissions.values_list("codename", flat=True))
            Evento.registrar(
                usuario=request.user, username=request.user.username,
                perfil=getattr(request.user.perfil, "codigo", ""),
                accion=Accion.CAMBIO_PERMISO, modelo="accounts.Perfil",
                objeto_id=str(perfil.pk), objeto_repr=perfil.nombre,
                ip=request.META.get("REMOTE_ADDR"), ruta=request.path, metodo="POST",
                detalle={"agregados": sorted(despues - antes),
                         "removidos": sorted(antes - despues)},
            )
            messages.success(request, "Permisos actualizados.")
            return redirect("gestion:perfiles")
        messages.error(request, "Revise los datos del formulario.")
        return redirect("gestion:perfil_permisos", pk=pk)


class MatrizAccesosView(SoloAdministradorMixin, ListView):
    """Vista consolidada perfil × permiso, útil como evidencia ante la SPDP."""

    template_name = "accounts/matriz_accesos.html"
    context_object_name = "perfiles"
    titulo = "Matriz de control de accesos"
    subtitulo = "Insumo del campo 3.12 del RAT (destinatarios internos)"

    def get_queryset(self):
        return Perfil.objects.select_related("grupo").prefetch_related(
            "grupo__permissions__content_type")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["permisos"] = Permission.objects.select_related("content_type").filter(
            content_type__app_label__in=["rat", "catalogos", "accounts", "plantillas", "auditoria"]
        ).order_by("content_type__app_label", "codename")
        return ctx
