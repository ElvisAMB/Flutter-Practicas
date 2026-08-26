"""Filtros de plantilla de uso general."""
from django import template

register = template.Library()


@register.filter
def attr(obj, nombre):
    """Acceso dinámico a atributos: {{ objeto|attr:"campo" }}."""
    valor = getattr(obj, nombre, "")
    if hasattr(valor, "all"):
        return ", ".join(str(x) for x in valor.all())
    if callable(valor):
        try:
            return valor()
        except TypeError:
            return ""
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    return valor if valor is not None else ""


@register.filter
def etiqueta_campo(modelo, nombre):
    try:
        return modelo._meta.get_field(nombre).verbose_name
    except Exception:
        return nombre.replace("_", " ").capitalize()
