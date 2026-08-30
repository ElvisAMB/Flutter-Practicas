from django.urls import path
from . import views

from .views import (
    dashboard,
    GastoListView,
    GastoCreateView,
    GastoUpdateView,
    GastoDeleteView,
)

# urlpatterns = [
#     path("", views.dashboard, name="dashboard"),
# ]

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("gastos/", GastoListView.as_view(), name="gasto_lista"),
    path("gastos/nuevo/", GastoCreateView.as_view(), name="gasto_crear"),
    path("gastos/<int:pk>/editar/", GastoUpdateView.as_view(), name="gasto_editar"),
    path("gastos/<int:pk>/eliminar/", GastoDeleteView.as_view(), name="gasto_eliminar"),
]
