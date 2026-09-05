from django.apps import AppConfig


class GastosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gastos'

    class Meta:

        permissions = [
            (
                'view_dashboard',
                'Puede visualizar el dashboard'
            ),
            (
                'manage_catalog',
                'Puede administrar tipos de gasto'
            ),
        ]


