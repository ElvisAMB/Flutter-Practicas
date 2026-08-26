"""apps/accounts/forms.py"""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, Permission
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.rat.forms import BootstrapMixin
from .models import Perfil, PerfilSistema, Usuario


class LoginForm(BootstrapMixin, AuthenticationForm):
    error_messages = {
        # Mensaje genérico deliberado: no revela si el usuario existe.
        "invalid_login": _("Usuario o contraseña incorrectos."),
        "inactive": _("Esta cuenta está desactivada."),
    }


class UsuarioBaseForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = (
            "username", "first_name", "last_name", "email", "documento", "telefono",
            "cargo", "area", "perfil", "is_active", "mfa_habilitado",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["perfil"].queryset = Perfil.objects.filter(activo=True).select_related("grupo")
        self.fields["username"].help_text = _(
            "Identificador de acceso. No se cifra: es la clave de autenticación y "
            "debe permanecer indexable."
        )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            return email
        from apps.core.crypto import blind_index

        bidx = blind_index(email, scope="usuario.email")
        qs = Usuario.objects.filter(email_bidx=bidx)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("Ya existe un usuario con ese correo."))
        return email


class UsuarioCreateForm(UsuarioBaseForm):
    password1 = forms.CharField(label=_("Contraseña"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirmar contraseña"), widget=forms.PasswordInput)

    def clean(self):
        datos = super().clean()
        if datos.get("password1") != datos.get("password2"):
            self.add_error("password2", _("Las contraseñas no coinciden."))
        from django.contrib.auth.password_validation import validate_password

        if datos.get("password1"):
            validate_password(datos["password1"], self.instance)
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password1"])
        usuario.debe_cambiar_password = True
        if commit:
            usuario.save()
        return usuario


class UsuarioUpdateForm(UsuarioBaseForm):
    """
    Edición sin contraseña. El requisito «el usuario común debe poder
    modificarse tanto en datos como en accesos» se satisface aquí (datos) y en
    la asignación de perfil/permisos (accesos).
    """


class PerfilForm(BootstrapMixin, forms.ModelForm):
    nombre = forms.CharField(label=_("Nombre del perfil"), max_length=150)

    class Meta:
        model = Perfil
        fields = ("descripcion", "activo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["nombre"].initial = self.instance.grupo.name
            if self.instance.es_sistema:
                self.fields["nombre"].disabled = True
                self.fields["nombre"].help_text = _(
                    "Los perfiles de sistema no pueden renombrarse.")

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        qs = Group.objects.filter(name__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.grupo_id)
        if qs.exists():
            raise forms.ValidationError(_("Ya existe un perfil con ese nombre."))
        return nombre

    def save(self, commit=True):
        nombre = self.cleaned_data["nombre"]
        if self.instance.pk:
            grupo = self.instance.grupo
            if not self.instance.es_sistema:
                grupo.name = nombre
                grupo.save()
        else:
            grupo = Group.objects.create(name=nombre)
            self.instance.grupo = grupo
            self.instance.codigo = slugify(nombre)[:64]
            self.instance.es_sistema = False
            self.instance.permite_edicion_permisos = True
        return super().save(commit)


class AsignarPermisosForm(forms.Form):
    """Selector de permisos agrupado por aplicación."""

    permisos = forms.ModelMultipleChoiceField(
        label=_("Permisos"), queryset=Permission.objects.none(),
        widget=forms.CheckboxSelectMultiple, required=False,
    )

    APPS_GESTIONABLES = ["rat", "catalogos", "accounts", "plantillas", "auditoria"]

    def __init__(self, *args, perfil: Perfil | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = (
            Permission.objects.select_related("content_type")
            .filter(content_type__app_label__in=self.APPS_GESTIONABLES)
            .order_by("content_type__app_label", "content_type__model", "codename")
        )
        self.fields["permisos"].queryset = qs
        if perfil and perfil.pk:
            self.fields["permisos"].initial = perfil.grupo.permissions.all()
        if perfil and perfil.codigo == PerfilSistema.AUDITOR:
            # Coherencia visual con la regla de negocio: el auditor solo lee.
            self.fields["permisos"].queryset = qs.filter(codename__startswith="view_")

    def permisos_agrupados(self):
        grupos: dict[str, list] = {}
        for bound in self["permisos"]:
            permiso = bound.choice_label
            app = str(permiso).split(" | ")[0] if " | " in str(permiso) else "otros"
            grupos.setdefault(app, []).append(bound)
        return grupos
