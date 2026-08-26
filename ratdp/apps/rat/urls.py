from django.urls import path

from . import views

app_name = "rat"

urlpatterns = [
    path("", views.ActividadListView.as_view(), name="lista"),
    path("nueva/", views.ActividadCreateView.as_view(), name="crear"),
    path("exportar/", views.ExportarRATView.as_view(), name="exportar"),
    path("<uuid:uuid>/", views.ActividadDetailView.as_view(), name="detalle"),
    path("<uuid:uuid>/editar/", views.ActividadUpdateView.as_view(), name="editar"),
    path("<uuid:uuid>/baja/", views.ActividadDeleteView.as_view(), name="baja"),
    path("<uuid:uuid>/estado/", views.CambiarEstadoView.as_view(), name="cambiar_estado"),
    path("<uuid:uuid>/brecha/", views.BrechaCreateView.as_view(), name="crear_brecha"),
]
