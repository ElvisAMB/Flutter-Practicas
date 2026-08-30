from django.contrib import admin
from .models import TipoGasto, Gasto

# Register your models here.

@admin.register(TipoGasto)
class TipoGastoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre",
        "activo",
    )

    search_fields = ("nombre",)

    list_filter = ("activo",)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "usuario",
        "tipo_gasto",
        "descripcion",
        "costo_previsto",
        "costo_real",
        "fecha",
    )

    search_fields = ("descripcion",)

    list_filter = (
        "tipo_gasto",
        "fecha",
    )
