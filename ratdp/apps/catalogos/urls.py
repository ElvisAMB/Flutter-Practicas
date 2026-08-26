from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "catalogos"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="catalogos:lista_default"), name="indice"),
    path("areas/", views.CatalogoListView.as_view(), {"slug": "areas"}, name="lista_default"),
    path("<slug:slug>/", views.CatalogoListView.as_view(), name="lista"),
    path("<slug:slug>/nuevo/", views.CatalogoCreateView.as_view(), name="crear"),
    path("<slug:slug>/<uuid:uuid>/editar/", views.CatalogoUpdateView.as_view(), name="editar"),
    path("<slug:slug>/<uuid:uuid>/baja/", views.CatalogoDeleteView.as_view(), name="baja"),
]
