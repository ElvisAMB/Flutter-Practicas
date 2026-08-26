from django.urls import path

from . import views

app_name = "plantillas"

urlpatterns = [
    path("", views.PlantillaListView.as_view(), name="lista"),
    path("nueva/", views.PlantillaCreateView.as_view(), name="crear"),
    path("<uuid:uuid>/", views.PlantillaPreviewView.as_view(), name="preview"),
    path("<uuid:uuid>/editar/", views.PlantillaUpdateView.as_view(), name="editar"),
    path("<uuid:uuid>/clonar/", views.PlantillaClonarView.as_view(), name="clonar"),
]
