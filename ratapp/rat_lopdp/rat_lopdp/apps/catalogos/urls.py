from django.urls import path

from . import views

app_name = "catalogos"

urlpatterns = [
    path("", views.indice, name="indice"),
    path("<slug:slug>/", views.lista, name="lista"),
    path("<slug:slug>/nuevo/", views.editar, name="crear"),
    path("<slug:slug>/<int:pk>/editar/", views.editar, name="editar"),
    path("<slug:slug>/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
