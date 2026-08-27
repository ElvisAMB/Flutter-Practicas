from django import forms


class MixinBootstrap:
    """Aplica clases de Bootstrap 5 a todos los widgets del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", "form-control")
                widget.attrs.setdefault("rows", 3)
            elif isinstance(widget, forms.DateInput):
                widget.attrs.setdefault("class", "form-control")
                widget.input_type = "date"
            else:
                widget.attrs.setdefault("class", "form-control")


class FormularioBootstrap(MixinBootstrap, forms.ModelForm):
    pass
