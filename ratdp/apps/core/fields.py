"""
apps/core/fields.py
===================
Campos de modelo que cifran de forma transparente al ORM.

El cifrado ocurre en ``get_prep_value`` (Python -> BD) y el descifrado en
``from_db_value`` (BD -> Python). Esto significa:

*  Funciona con **cualquier backend** soportado por Django, porque en la BD
   solo se almacena texto.
*  ``.filter(campo="x")`` **no funciona** sobre un campo cifrado: el valor en
   BD es distinto en cada fila aunque el plaintext sea igual. Si necesita
   filtrar, declare además un ``BlindIndexField`` y filtre por él.
*  ``.order_by(campo)`` ordena por ciphertext, es decir, aleatoriamente. Si
   necesita ordenar, el campo no debe cifrarse (revise la clasificación).

Estas restricciones son inherentes al cifrado seguro, no a la implementación.
"""

from __future__ import annotations

from django.core.exceptions import FieldError
from django.db import models

from .crypto import blind_index, decrypt, encrypt


class _EncryptedMixin:
    """Lógica común de cifrado transparente."""

    def __init__(self, *args, aad_scope: str | None = None, **kwargs):
        self.aad_scope = aad_scope
        # El ciphertext en base64 crece ~35 % + prefijo + nonce/tag.
        kwargs.setdefault("max_length", 1024)
        super().__init__(*args, **kwargs)

    # -- serialización de migraciones -------------------------------------
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.aad_scope:
            kwargs["aad_scope"] = self.aad_scope
        return name, path, args, kwargs

    # -- ida y vuelta ------------------------------------------------------
    @property
    def _aad(self) -> bytes | None:
        return self.aad_scope.encode() if self.aad_scope else None

    def get_internal_type(self) -> str:
        return "TextField"

    def get_prep_value(self, value):
        if value in (None, ""):
            return value
        return encrypt(str(value), aad=self._aad)

    def from_db_value(self, value, expression, connection):
        if value in (None, ""):
            return value
        return decrypt(value, aad=self._aad)

    def to_python(self, value):
        return value

    # -- bloqueo explícito de lookups imposibles ---------------------------
    def get_lookup(self, lookup_name):
        if lookup_name in {
            "contains", "icontains", "startswith", "istartswith",
            "endswith", "iendswith", "gt", "gte", "lt", "lte", "range",
            "regex", "iregex",
        }:
            raise FieldError(
                f"El lookup '{lookup_name}' no puede aplicarse sobre "
                f"'{self.name}' porque el campo está cifrado con nonce "
                f"aleatorio. Use un BlindIndexField para igualdad exacta, o "
                f"reclasifique el campo si necesita búsqueda parcial."
            )
        return super().get_lookup(lookup_name)


class EncryptedCharField(_EncryptedMixin, models.CharField):
    """Texto corto cifrado (nombres, documentos, teléfonos, correos)."""


class EncryptedTextField(_EncryptedMixin, models.TextField):
    """Texto largo cifrado (observaciones, justificaciones, evidencias)."""

    def __init__(self, *args, **kwargs):
        kwargs.pop("max_length", None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop("max_length", None)
        return name, path, args, kwargs


class EncryptedEmailField(EncryptedCharField):
    """Correo cifrado. Recuerde declarar su índice ciego para el login."""


class BlindIndexField(models.CharField):
    """
    Columna hermana, determinista e indexada, que habilita búsquedas de
    igualdad sobre un campo cifrado.

    Uso::

        email      = EncryptedEmailField(aad_scope="usuario.email")
        email_bidx = BlindIndexField(source="email", scope="usuario.email",
                                     unique=True)

    El valor se recalcula automáticamente en ``save()`` a través de
    :class:`apps.core.models.BlindIndexMixin`.
    """

    def __init__(self, *args, source: str = "", scope: str = "", **kwargs):
        self.source = source
        self.scope = scope
        kwargs.setdefault("max_length", 32)
        kwargs.setdefault("db_index", True)
        kwargs.setdefault("editable", False)
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["source"] = self.source
        kwargs["scope"] = self.scope
        return name, path, args, kwargs

    def calcular(self, instancia) -> str:
        valor = getattr(instancia, self.source, None)
        return blind_index(valor, scope=self.scope) if valor else ""
