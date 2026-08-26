"""Validadores de contraseña adicionales."""
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplejidadValidator:
    """Exige mayúscula, minúscula, dígito y símbolo."""

    def validate(self, password, user=None):
        faltantes = []
        if not re.search(r"[A-ZÁÉÍÓÚÑ]", password):
            faltantes.append(_("una letra mayúscula"))
        if not re.search(r"[a-záéíóúñ]", password):
            faltantes.append(_("una letra minúscula"))
        if not re.search(r"\d", password):
            faltantes.append(_("un dígito"))
        if not re.search(r"[^\w\s]", password):
            faltantes.append(_("un carácter especial"))
        if faltantes:
            raise ValidationError(
                _("La contraseña debe contener al menos %(f)s.") % {"f": ", ".join(faltantes)},
                code="password_sin_complejidad",
            )

    def get_help_text(self):
        return _("Debe incluir mayúscula, minúscula, dígito y carácter especial.")
