from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import GrupoForm, UsuarioCrearForm, UsuarioEditarForm


class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    permission_required = "auth.view_user"
    template_name = "cuentas/usuario_list.html"
    context_object_name = "usuarios"
    paginate_by = 25

    def get_queryset(self):
        qs = User.objects.prefetch_related("groups").order_by("username")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(username__icontains=q)
        return qs


@login_required
@permission_required("auth.add_user", raise_exception=True)
def usuario_crear(request):
    form = UsuarioCrearForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Usuario creado.")
        return redirect("cuentas:usuario_list")
    return render(request, "cuentas/usuario_form.html", {"form": form, "objeto": None})


@login_required
@permission_required("auth.change_user", raise_exception=True)
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    form = UsuarioEditarForm(request.POST or None, instance=usuario)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Usuario actualizado.")
        return redirect("cuentas:usuario_list")
    return render(request, "cuentas/usuario_form.html", {"form": form, "objeto": usuario})


class GrupoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Group
    permission_required = "auth.view_group"
    template_name = "cuentas/grupo_list.html"
    context_object_name = "grupos"


@login_required
@permission_required("auth.change_group", raise_exception=True)
def grupo_editar(request, pk=None):
    grupo = get_object_or_404(Group, pk=pk) if pk else None
    form = GrupoForm(request.POST or None, instance=grupo)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil guardado.")
        return redirect("cuentas:grupo_list")
    return render(request, "cuentas/grupo_form.html", {"form": form, "objeto": grupo})
