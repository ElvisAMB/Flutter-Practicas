from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="rat:actividad_list", permanent=False)),
    path("rat/", include("apps.rat.urls")),
    path("catalogos/", include("apps.catalogos.urls")),
    path("cuentas/", include("apps.cuentas.urls")),
    path("admin/", admin.site.urls),
]
