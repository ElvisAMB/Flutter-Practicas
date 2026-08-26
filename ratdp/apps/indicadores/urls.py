from django.urls import path

from . import views

app_name = "indicadores"

urlpatterns = [
    path("", views.TableroView.as_view(), name="tablero"),
    path("exportar/", views.ExportarIndicadoresView.as_view(), name="exportar"),
]
