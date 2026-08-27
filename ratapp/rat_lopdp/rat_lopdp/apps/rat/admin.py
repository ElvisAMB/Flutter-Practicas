from django.contrib import admin

from .models import (ActividadTratamiento, BaseLicitudActividad,
                     DestinatarioExternoActividad, HistorialActividad,
                     TransferenciaInternacional)


class BaseLicitudInline(admin.TabularInline):
    model = BaseLicitudActividad
    extra = 1


class DestinatarioInline(admin.TabularInline):
    model = DestinatarioExternoActividad
    extra = 1


class TransferenciaInline(admin.TabularInline):
    model = TransferenciaInternacional
    extra = 0


@admin.register(ActividadTratamiento)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre_corto", "area", "estado", "datos_especiales",
                    "transferencia_internacional", "eipd_requerida", "version")
    list_filter = ("estado", "area", "datos_especiales", "menores",
                   "transferencia_internacional", "eipd_requerida")
    search_fields = ("codigo", "nombre_corto", "finalidad")
    inlines = [BaseLicitudInline, DestinatarioInline, TransferenciaInline]
    filter_horizontal = ("categorias_datos", "categorias_interesados",
                         "habilitantes_especiales", "medidas_seguridad",
                         "criterios_eipd", "encargados", "corresponsables")


admin.site.register(HistorialActividad)
admin.site.site_header = "Administración del RAT"
admin.site.site_title = "RAT"
