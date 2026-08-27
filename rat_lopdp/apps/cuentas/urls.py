from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    path("ingresar/", auth_views.LoginView.as_view(
        template_name="registration/login.html", redirect_authenticated_user=True),
        name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("clave/", auth_views.PasswordChangeView.as_view(
        template_name="registration/password_change_form.html",
        success_url="/cuentas/clave/listo/"), name="password_change"),
    path("clave/listo/", auth_views.PasswordChangeDoneView.as_view(
        template_name="registration/password_change_done.html"), name="password_change_done"),
    path("usuarios/", views.UsuarioListView.as_view(), name="usuario_list"),
    path("usuarios/nuevo/", views.usuario_crear, name="usuario_create"),
    path("usuarios/<int:pk>/editar/", views.usuario_editar, name="usuario_update"),
    path("grupos/", views.GrupoListView.as_view(), name="grupo_list"),
    path("grupos/nuevo/", views.grupo_editar, name="grupo_create"),
    path("grupos/<int:pk>/editar/", views.grupo_editar, name="grupo_update"),
]
