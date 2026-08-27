from django import forms
from django.template import Library

register = Library()


@register.filter
def es_grupo_casillas(campo):
    """True si el campo se dibuja como lista de casillas o radios."""
    return isinstance(campo.field.widget,
                      (forms.CheckboxSelectMultiple, forms.RadioSelect))


@register.filter
def es_casilla(campo):
    return isinstance(campo.field.widget, forms.CheckboxInput)
