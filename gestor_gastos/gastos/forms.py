from django import forms
from .models import Gasto


class GastoForm(forms.ModelForm):

    class Meta:

        model = Gasto

        fields = [
            "tipo_gasto",
            "descripcion",
            "costo_previsto",
            "costo_real",
            "fecha",
            "observacion",
        ]

        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "observacion": forms.Textarea(attrs={"rows": 3}),
        }
