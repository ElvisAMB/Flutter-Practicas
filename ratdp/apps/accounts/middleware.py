"""Fuerza el cambio de contraseña inicial o vencida."""
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

EXENTAS = ("accounts:cambiar_password", "accounts:logout", "accounts:login")


class CambioPasswordMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        if request.path.startswith(("/static/", "/media/")):
            return None
        actual = getattr(request.resolver_match, "view_name", "") if request.resolver_match else ""
        if actual in EXENTAS:
            return None

        vencida = False
        dias = getattr(settings, "DIAS_VIGENCIA_PASSWORD", 0)
        if dias and user.ultimo_cambio_password:
            vencida = (timezone.now() - user.ultimo_cambio_password).days > dias

        if user.debe_cambiar_password or vencida:
            destino = reverse("accounts:cambiar_password")
            if request.path != destino:
                return redirect(destino)
        return None
