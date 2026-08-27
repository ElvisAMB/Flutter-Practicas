from django.urls import path

from . import views

app_name = "rat"

urlpatterns = [
    path("", views.ActividadListView.as_view(), name="actividad_list"),
    path("tablero/", views.tablero, name="tablero"),
    path("nueva/", views.ActividadCreateView.as_view(), name="actividad_create"),
    path("<int:pk>/", views.ActividadDetailView.as_view(), name="actividad_detail"),
    path("<int:pk>/editar/", views.ActividadUpdateView.as_view(), name="actividad_update"),
    path("<int:pk>/eliminar/", views.ActividadDeleteView.as_view(), name="actividad_delete"),
    path("<int:pk>/estado/", views.cambiar_estado, name="actividad_estado"),
    path("exportar/", views.exportar_csv, name="exportar_csv"),
]
