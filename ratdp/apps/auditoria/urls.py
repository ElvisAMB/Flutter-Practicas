from django.urls import path

from . import views

app_name = "auditoria"

urlpatterns = [
    path("", views.BitacoraListView.as_view(), name="bitacora"),
    path("verificar/", views.VerificarCadenaView.as_view(), name="verificar"),
    path("exportar/", views.ExportarBitacoraView.as_view(), name="exportar"),
]
