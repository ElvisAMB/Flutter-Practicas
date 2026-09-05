from django import forms
from .models import Gasto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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

    def clean(self):
        cleaned_data = super().clean()
        previsto = cleaned_data.get("costo_previsto")
        real = cleaned_data.get("costo_real")
        if previsto is not None and real is not None:
            if previsto < 0 or real < 0:
                raise forms.ValidationError("Los costos no pueden ser negativos.")
        return cleaned_data

class RegistroUsuarioForm(UserCreationForm):

    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]
