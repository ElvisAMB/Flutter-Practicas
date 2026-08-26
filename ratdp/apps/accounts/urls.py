from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("ingreso/", views.IngresoView.as_view(), name="login"),
    path("salir/", views.SalidaView.as_view(), name="logout"),
    path("cambiar-clave/", views.CambiarPasswordView.as_view(), name="cambiar_password"),
]
