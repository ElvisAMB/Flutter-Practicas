from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="rat:actividad_list", permanent=False)),
    path("rat/", include("apps.rat.urls")),
    path("catalogos/", include("apps.catalogos.urls")),
    path("cuentas/", include("apps.cuentas.urls")),
    path("admin/", admin.site.urls),
]

#Configuración para depuración y recarga en tiempo real de la aplicación web en ejecución
if settings.DEBUG:
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]