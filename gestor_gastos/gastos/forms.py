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


class RegistroUsuarioForm(UserCreationForm):

    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]
