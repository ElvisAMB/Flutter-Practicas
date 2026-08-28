from django import forms
from django.forms import inlineformset_factory

from apps.catalogos.models import (
    Area,
    BaseLicitud,
    CategoriaDato,
    CategoriaInteresado,
    CriterioEIPD,
    DestinatarioExterno,
    EstadoRegistro,
    HabilitanteEspecial,
    MedidaSeguridad,
    ProcesoInterno,
    Tercero,
)
from apps.core.forms import MixinBootstrap
from .models import (
    ActividadTratamiento,
    BaseLicitudActividad,
    DestinatarioExternoActividad,
    TransferenciaInternacional,
)


class ActividadTratamientoForm(MixinBootstrap, forms.ModelForm):
    class Meta:
        model = ActividadTratamiento
        exclude = (
            "creado_en",
            "actualizado_en",
            "creado_por",
            "actualizado_por",
            "bases_licitud",
            "destinatarios_externos",
            "version",
        )
        widgets = {
            "finalidad": forms.Textarea(attrs={"rows": 2}),
            "destinatarios_internos": forms.Textarea(attrs={"rows": 3}),
            "criterio_plazo": forms.Textarea(attrs={"rows": 3}),
            "corresponsable_detalle": forms.Textarea(attrs={"rows": 3}),
            "habilitante_justificacion": forms.Textarea(attrs={"rows": 2}),
            "medidas_adicionales": forms.Textarea(attrs={"rows": 3}),
            "observaciones": forms.Textarea(attrs={"rows": 2}),
            "categorias_datos": forms.CheckboxSelectMultiple(
                attrs={"class": "lista-alta"}
            ),
            "categorias_interesados": forms.CheckboxSelectMultiple(
                attrs={"class": "lista-alta"}
            ),
            "habilitantes_especiales": forms.CheckboxSelectMultiple,
            "medidas_seguridad": forms.CheckboxSelectMultiple(
                attrs={"class": "lista-alta"}
            ),
            "criterios_eipd": forms.CheckboxSelectMultiple,
            "corresponsables": forms.Textarea(attrs={"rows": 2}),
            "encargados": forms.Textarea(attrs={"rows": 2}),
            "eipd_fecha": forms.DateInput(attrs={"type": "date"}),
            "fecha_cese": forms.DateInput(attrs={"type": "date"}),
            "fecha_validacion": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo opciones activas de cada catálogo.
        self.fields["area"].queryset = Area.objects.filter(activo=True)
        self.fields["proceso_interno"].queryset = ProcesoInterno.objects.filter(
            activo=True
        )
        self.fields["estado"].queryset = EstadoRegistro.objects.filter(activo=True)
        self.fields["categorias_datos"].queryset = CategoriaDato.objects.filter(
            activo=True
        )
        self.fields["categorias_interesados"].queryset = (
            CategoriaInteresado.objects.filter(activo=True)
        )
        self.fields["habilitantes_especiales"].queryset = (
            HabilitanteEspecial.objects.filter(activo=True)
        )
        self.fields["medidas_seguridad"].queryset = MedidaSeguridad.objects.filter(
            activo=True
        )
        self.fields["criterios_eipd"].queryset = CriterioEIPD.objects.filter(
            activo=True
        )
        self.fields["corresponsables"].queryset = Tercero.objects.filter(
            rol=Tercero.ROL_CORRESPONSABLE, activo=True
        )
        self.fields["encargados"].queryset = Tercero.objects.filter(
            rol=Tercero.ROL_ENCARGADO, activo=True
        )
        self.fields["codigo"].widget.attrs["placeholder"] = "RAT-SUS-01"
        self.fields["nombre_corto"].widget.attrs[
            "placeholder"
        ] = "Evaluación de riesgo y capacidad de pago para suscripción de fianzas"

    def clean(self):
        datos = super().clean()
        errores = {}

        if not datos.get("categorias_datos"):
            errores["categorias_datos"] = (
                "Seleccione al menos una categoría de datos (3.8)."
            )

        if not datos.get("categorias_interesados"):
            errores["categorias_interesados"] = (
                "Seleccione al menos una categoría de titulares (3.10)."
            )

        # 3.9 -> 3.7 obligatorio
        if datos.get("datos_especiales") and not datos.get("habilitantes_especiales"):
            errores["habilitantes_especiales"] = (
                "Con datos especiales debe indicar el habilitante del Art. 26 LOPDP (3.7)."
            )
        if (
            datos.get("datos_especiales")
            and not (datos.get("habilitante_justificacion") or "").strip()
        ):
            errores["habilitante_justificacion"] = (
                "Justifique el habilitante seleccionado."
            )
        if not datos.get("datos_especiales") and datos.get("habilitantes_especiales"):
            errores["habilitantes_especiales"] = (
                "El habilitante del Art. 26 solo se llena si 3.9 = Sí."
            )

        # 3.8 con categoría sensible obliga a 3.9
        seleccionadas = datos.get("categorias_datos")
        if seleccionadas and not datos.get("datos_especiales"):
            sensibles = [c.nombre for c in seleccionadas if c.es_sensible]
            if sensibles:
                errores["datos_especiales"] = (
                    "Estas categorías son especiales según el Art. 25 LOPDP: "
                    + ", ".join(sensibles)
                    + ". Marque 3.9."
                )

        # 3.4
        if datos.get("corresponsable_situacion") == "SI" and not datos.get(
            "corresponsables"
        ):
            errores["corresponsables"] = (
                "Seleccione al menos un corresponsable o cambie 3.4."
            )

        if errores:
            raise forms.ValidationError(errores)
        return datos


class BaseLicitudActividadForm(MixinBootstrap, forms.ModelForm):
    class Meta:
        model = BaseLicitudActividad
        fields = ("base", "justificacion", "test_ponderacion")
        widgets = {
            "justificacion": forms.TextInput(),
            "test_ponderacion": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["base"].queryset = BaseLicitud.objects.filter(activo=True)


class BaseLicitudActividadFormSetBase(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        vivos = [
            f for f in self.forms if f.cleaned_data and not f.cleaned_data.get("DELETE")
        ]
        if not vivos:
            raise forms.ValidationError(
                "Registre al menos una base de licitud con su justificación (3.6)."
            )


BaseLicitudFormSet = inlineformset_factory(
    ActividadTratamiento,
    BaseLicitudActividad,
    form=BaseLicitudActividadForm,
    formset=BaseLicitudActividadFormSetBase,
    extra=1,
    can_delete=True,
)


class DestinatarioExternoActividadForm(MixinBootstrap, forms.ModelForm):
    class Meta:
        model = DestinatarioExternoActividad
        fields = ("destinatario", "fundamento")
        widgets = {"fundamento": forms.TextInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["destinatario"].queryset = DestinatarioExterno.objects.filter(
            activo=True
        )


class DestinatarioExternoFormSetBase(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        vivos = [
            f for f in self.forms if f.cleaned_data and not f.cleaned_data.get("DELETE")
        ]
        if not vivos:
            raise forms.ValidationError(
                "3.13 no puede quedar vacío. Si no hay comunicaciones externas, seleccione "
                "explícitamente la opción «Ninguno»: el blanco no distingue «no aplica» de "
                "«no evaluado»."
            )
        # "Ninguno" es excluyente.
        marcados = [f.cleaned_data["destinatario"] for f in vivos]
        if any(d.es_ninguno for d in marcados) and len(marcados) > 1:
            raise forms.ValidationError(
                "«Ninguno» no puede combinarse con otros destinatarios externos."
            )


DestinatarioExternoFormSet = inlineformset_factory(
    ActividadTratamiento,
    DestinatarioExternoActividad,
    form=DestinatarioExternoActividadForm,
    formset=DestinatarioExternoFormSetBase,
    extra=1,
    can_delete=True,
)


class TransferenciaForm(MixinBootstrap, forms.ModelForm):
    class Meta:
        model = TransferenciaInternacional
        fields = (
            "pais",
            "mecanismo",
            "destinatario_exterior",
            "detalle",
            "registrada_registro_nacional",
            "fecha_registro",
        )
        widgets = {
            "detalle": forms.TextInput(),
            "fecha_registro": forms.DateInput(attrs={"type": "date"}),
        }


class TransferenciaFormSetBase(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        vivos = [
            f for f in self.forms if f.cleaned_data and not f.cleaned_data.get("DELETE")
        ]
        marca = self.instance_transferencia_marcada
        if marca and not vivos:
            raise forms.ValidationError(
                "Marcó transferencia internacional (3.14): registre país y mecanismo (3.15)."
            )
        if not marca and vivos:
            raise forms.ValidationError(
                "Hay transferencias registradas pero 3.14 dice «No». Corrija una de las dos."
            )

    instance_transferencia_marcada = False


TransferenciaFormSet = inlineformset_factory(
    ActividadTratamiento,
    TransferenciaInternacional,
    form=TransferenciaForm,
    formset=TransferenciaFormSetBase,
    extra=1,
    can_delete=True,
)


class FiltroActividadForm(MixinBootstrap, forms.Form):
    q = forms.CharField(
        label="Buscar",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Código, nombre o finalidad"}),
    )
    area = forms.ModelChoiceField(
        label="Área",
        queryset=Area.objects.filter(activo=True),
        required=False,
        empty_label="Todas las áreas",
    )
    estado = forms.ModelChoiceField(
        label="Estado",
        queryset=EstadoRegistro.objects.filter(activo=True),
        required=False,
        empty_label="Todos los estados",
    )
    datos_especiales = forms.ChoiceField(
        label="Datos especiales",
        required=False,
        choices=[
            ("", "Todos"),
            ("1", "Solo con datos especiales"),
            ("0", "Sin datos especiales"),
        ],
    )
    transferencia = forms.ChoiceField(
        label="Transferencia internacional",
        required=False,
        choices=[("", "Todas"), ("1", "Con transferencia"), ("0", "Sin transferencia")],
    )
    eipd = forms.ChoiceField(
        label="EIPD",
        required=False,
        choices=[("", "Todas"), ("1", "EIPD requerida"), ("0", "Sin EIPD")],
    )
