from django.urls import path

from . import views

app_name = "gestion"

urlpatterns = [
    path("", views.UsuarioListView.as_view(), name="usuarios"),
    path("nuevo/", views.UsuarioCreateView.as_view(), name="usuario_crear"),
    path("<uuid:uuid>/", views.UsuarioDetailView.as_view(), name="usuario_detalle"),
    path("<uuid:uuid>/editar/", views.UsuarioUpdateView.as_view(), name="usuario_editar"),
    path("<uuid:uuid>/toggle/", views.ToggleUsuarioView.as_view(), name="usuario_toggle"),
    path("<uuid:uuid>/desbloquear/", views.DesbloquearUsuarioView.as_view(), name="usuario_desbloquear"),
    path("perfiles/", views.PerfilListView.as_view(), name="perfiles"),
    path("perfiles/nuevo/", views.PerfilCreateView.as_view(), name="perfil_crear"),
    path("perfiles/<int:pk>/editar/", views.PerfilUpdateView.as_view(), name="perfil_editar"),
    path("perfiles/<int:pk>/permisos/", views.PerfilPermisosView.as_view(), name="perfil_permisos"),
    path("matriz-accesos/", views.MatrizAccesosView.as_view(), name="matriz_accesos"),
]
