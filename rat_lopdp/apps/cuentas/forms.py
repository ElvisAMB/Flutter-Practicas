from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User

from apps.core.forms import MixinBootstrap


class UsuarioCrearForm(MixinBootstrap, UserCreationForm):
    grupos = forms.ModelMultipleChoiceField(
        label="Perfiles", queryset=Group.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")

    def save(self, commit=True):
        usuario = super().save(commit)
        if commit:
            usuario.groups.set(self.cleaned_data["grupos"])
        return usuario


class UsuarioEditarForm(MixinBootstrap, forms.ModelForm):
    grupos = forms.ModelMultipleChoiceField(
        label="Perfiles", queryset=Group.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["grupos"].initial = self.instance.groups.all()

    def save(self, commit=True):
        usuario = super().save(commit)
        if commit:
            usuario.groups.set(self.cleaned_data["grupos"])
        return usuario


class GrupoForm(MixinBootstrap, forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name", "permissions")
        labels = {"name": "Nombre del perfil", "permissions": "Permisos"}
        widgets = {"permissions": forms.SelectMultiple(attrs={"size": 18})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permissions"].queryset = Permission.objects.filter(
            content_type__app_label__in=["rat", "catalogos", "auth"]
        ).select_related("content_type").order_by("content_type__app_label", "codename")
