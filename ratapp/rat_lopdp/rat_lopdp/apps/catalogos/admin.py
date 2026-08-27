from django.contrib import admin

from .models import (Area, BaseLicitud, CategoriaDato, CategoriaInteresado,
                     CriterioEIPD, DestinatarioExterno, EstadoRegistro,
                     HabilitanteEspecial, MecanismoTransferencia, MedidaSeguridad,
                     Pais, ProcesoInterno, Tercero)

for modelo in (Area, BaseLicitud, CategoriaDato, CategoriaInteresado, CriterioEIPD,
               DestinatarioExterno, EstadoRegistro, HabilitanteEspecial,
               MecanismoTransferencia, MedidaSeguridad, Pais, ProcesoInterno):
    admin.site.register(modelo)


@admin.register(Tercero)
class TerceroAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "rol", "contrato_suscrito", "clausulas_art41", "activo")
    list_filter = ("rol", "activo", "contrato_suscrito")
    search_fields = ("razon_social", "identificacion")
