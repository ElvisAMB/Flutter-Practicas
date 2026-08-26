"""Enrutado raíz del proyecto."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="indicadores:tablero"), name="inicio"),
    path("cuenta/", include("apps.accounts.urls")),
    path("usuarios/", include("apps.accounts.urls_gestion")),
    path("rat/", include("apps.rat.urls")),
    path("catalogos/", include("apps.catalogos.urls")),
    path("indicadores/", include("apps.indicadores.urls")),
    path("plantillas/", include("apps.plantillas.urls")),
    path("auditoria/", include("apps.auditoria.urls")),
    # El admin de Django se publica en una ruta no evidente y puede
    # deshabilitarse por completo en producción (ver documento de instalación).
    path(settings.ADMIN_URL if hasattr(settings, "ADMIN_URL") else "gestion-django/",
         admin.site.urls),
]

handler403 = "apps.core.views.error_403"
handler404 = "apps.core.views.error_404"
handler500 = "apps.core.views.error_500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
