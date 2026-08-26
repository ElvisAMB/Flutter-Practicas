"""apps/rat/forms.py — formularios de la matriz RAT."""

from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.catalogos.models import TipoDatoEspecial
from .models import ActividadTratamiento, Brecha, Entrevista, SiNo

CLASE_INPUT = "form-control"
CLASE_SELECT = "form-select"
CLASE_CHECK = "form-check-input"


class BootstrapMixin:
    """Aplica clases CSS sin ensuciar cada declaración de campo."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", CLASE_CHECK)
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", CLASE_SELECT)
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs.setdefault("class", "")
            else:
                widget.attrs.setdefault("class", CLASE_INPUT)
            if isinstance(widget, forms.DateInput):
                widget.input_type = "date"


class ActividadForm(BootstrapMixin, forms.ModelForm):
    tipos_dato_especial = forms.MultipleChoiceField(
        label=_("Tipos de categoría especial"),
        choices=[(c.value, c.label) for c in TipoDatoEspecial if c != TipoDatoEspecial.NO_APLICA],
        required=False, widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = ActividadTratamiento
        exclude = (
            "uuid", "creado_en", "actualizado_en", "creado_por", "actualizado_por",
            "eliminado_en", "eliminado_por", "estado", "validado_por", "fecha_validacion",
        )
        widgets = {
            "finalidad": forms.Textarea(attrs={"rows": 2}),
            "justificacion_base_licitud": forms.Textarea(attrs={"rows": 3}),
            "fundamento_comunicacion": forms.Textarea(attrs={"rows": 2}),
            "garantias_detalle": forms.Textarea(attrs={"rows": 2}),
            "criterio_detalle": forms.Textarea(attrs={"rows": 2}),
            "medidas_detalle": forms.Textarea(attrs={"rows": 3}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
            "fecha_inicio_tratamiento": forms.DateInput(),
            "fecha_cese": forms.DateInput(),
            "fecha_ultima_revision": forms.DateInput(),
            "eipd_fecha": forms.DateInput(),
            "fecha_reporte_registro_nacional": forms.DateInput(),
            "categorias_datos": forms.CheckboxSelectMultiple,
            "categorias_titulares": forms.CheckboxSelectMultiple,
            "medidas_seguridad": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["tipos_dato_especial"].initial = self.instance.tipos_dato_especial or []
        for nombre in ("corresponsables", "encargados", "destinatarios_externos"):
            if nombre in self.fields:
                self.fields[nombre].queryset = self.fields[nombre].queryset.filter(activo=True)

    def clean(self):
        datos = super().clean()
        tipos = datos.get("tipos_dato_especial") or []
        if datos.get("datos_especiales") == SiNo.SI and not tipos:
            self.add_error(
                "tipos_dato_especial",
                _("Si marca SÍ en 3.9, indique el tipo para no perder trazabilidad "
                  "(SÍ – crediticios, SÍ – salud, etc.)."),
            )
        if tipos and datos.get("datos_especiales") != SiNo.SI:
            self.add_error("datos_especiales",
                           _("Declaró tipos especiales; el campo 3.9 debe ser SÍ."))
        if datos.get("menores") == SiNo.SI and TipoDatoEspecial.MENORES not in tipos:
            tipos = list(tipos) + [TipoDatoEspecial.MENORES]
            datos["tipos_dato_especial"] = tipos
        return datos

    def save(self, commit=True):
        self.instance.tipos_dato_especial = list(self.cleaned_data.get("tipos_dato_especial") or [])
        return super().save(commit)


class FiltroActividadForm(BootstrapMixin, forms.Form):
    """Filtros del listado. Todos operan sobre columnas indexadas."""

    q = forms.CharField(label=_("Buscar"), required=False,
                        widget=forms.TextInput(attrs={"placeholder": "Código o nombre…"}))
    area = forms.ChoiceField(label=_("Área"), required=False, choices=[])
    estado = forms.ChoiceField(label=_("Estado"), required=False, choices=[])
    datos_especiales = forms.ChoiceField(label=_("Datos especiales"), required=False, choices=[])
    transferencia = forms.ChoiceField(label=_("Transf. internacional"), required=False, choices=[])
    solo_alertas = forms.BooleanField(label=_("Solo con alertas"), required=False)

    def __init__(self, *args, **kwargs):
        from apps.catalogos.models import Area
        from .models import EstadoRegistro

        super().__init__(*args, **kwargs)
        vacio = [("", "Todos")]
        self.fields["area"].choices = vacio + [
            (str(a.pk), a.nombre) for a in Area.objects.filter(activo=True)
        ]
        self.fields["estado"].choices = vacio + list(EstadoRegistro.choices)
        self.fields["datos_especiales"].choices = vacio + list(SiNo.choices)
        self.fields["transferencia"].choices = vacio + list(SiNo.choices)


class CambioEstadoForm(BootstrapMixin, forms.Form):
    nuevo_estado = forms.ChoiceField(label=_("Nuevo estado"), choices=[])
    motivo = forms.CharField(label=_("Motivo"), widget=forms.Textarea(attrs={"rows": 3}),
                             required=False)

    def __init__(self, *args, actividad=None, **kwargs):
        from .models import EstadoRegistro, TRANSICIONES

        super().__init__(*args, **kwargs)
        permitidos = TRANSICIONES.get(EstadoRegistro(actividad.estado), set()) if actividad else set()
        self.fields["nuevo_estado"].choices = [
            (e.value, e.label) for e in EstadoRegistro if e in permitidos
        ]


class BrechaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Brecha
        fields = ("tipo", "descripcion", "accion", "responsable", "fecha_compromiso",
                  "estado", "fecha_cierre")
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 2}),
            "accion": forms.Textarea(attrs={"rows": 2}),
            "fecha_compromiso": forms.DateInput(),
            "fecha_cierre": forms.DateInput(),
        }


class EntrevistaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Entrevista
        fields = ("area", "fecha", "plantilla", "entrevistados", "respuestas",
                  "confirmada_por_area", "actividades")
        widgets = {
            "fecha": forms.DateInput(),
            "entrevistados": forms.Textarea(attrs={"rows": 2}),
            "respuestas": forms.Textarea(attrs={"rows": 10}),
        }
