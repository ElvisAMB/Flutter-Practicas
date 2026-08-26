"""
apps/core/crypto.py
===================
Motor criptográfico de la aplicación.

Decisiones de diseño (leer antes de modificar):

1.  Cifrado **a nivel de aplicación** (no pgcrypto, no TDE del motor) porque el
    requisito funcional exige portabilidad entre motores (PostgreSQL, MySQL,
    SQL Server, Oracle, SQLite). Todo lo específico del motor rompería esa
    portabilidad.

2.  Algoritmo: **AES-256-GCM** (AEAD). Autenticado -> detecta manipulación del
    ciphertext en base de datos. Nonce aleatorio de 96 bits por operación.

3.  **Rotación de llaves sin downtime**: cada valor cifrado lleva un prefijo
    ``v<key_id>$``. Se descifra con la llave indicada; se cifra siempre con la
    llave activa. Para rotar: agregar llave nueva a DP_ENC_KEYS, subir
    DP_ENC_ACTIVE_KEY y ejecutar ``manage.py rotar_llaves``.

4.  **Determinismo NO** en el cifrado (nonce aleatorio) -> es imposible buscar,
    ordenar o indexar por el campo cifrado. Para búsquedas de igualdad se usa
    un **índice ciego** (blind index): HMAC-SHA256 truncado, determinista,
    almacenado en una columna hermana indexada. Ver ``blind_index()``.
    Un índice ciego permite ``WHERE campo_bidx = ?`` con velocidad de índice
    B-Tree, pero NO permite LIKE, ORDER BY ni rangos: eso es una limitación
    matemática, no de esta implementación.

5.  Rendimiento: AES-GCM con AES-NI cuesta del orden de 1-3 microsegundos por
    campo corto. El cuello de botella real en tablas grandes no es el cifrado
    sino la **imposibilidad de filtrar en el motor**. Por eso la política de
    clasificación (ver apps/core/classification.py) cifra solo lo que debe
    cifrarse.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from functools import lru_cache
from typing import Dict

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

NONCE_BYTES = 12
PREFIX_SEP = "$"
BLIND_INDEX_BYTES = 16  # 128 bits -> colisión despreciable


class CryptoError(Exception):
    """Error irrecuperable de cifrado/descifrado."""


@lru_cache(maxsize=1)
def _keyring() -> Dict[str, bytes]:
    """
    Devuelve {key_id: clave_32_bytes}.

    DP_ENC_KEYS se define como dict {'1': '<base64 32 bytes>', '2': '...'}
    normalmente cargado desde variables de entorno o desde un KMS/DPAPI.
    """
    raw = getattr(settings, "DP_ENC_KEYS", None)
    if not raw:
        raise ImproperlyConfigured(
            "DP_ENC_KEYS no está configurado. Genere llaves con "
            "`python manage.py generar_llave`."
        )
    ring: Dict[str, bytes] = {}
    for kid, b64 in raw.items():
        key = base64.urlsafe_b64decode(b64)
        if len(key) != 32:
            raise ImproperlyConfigured(f"La llave '{kid}' no mide 32 bytes.")
        ring[str(kid)] = key
    return ring


@lru_cache(maxsize=1)
def _active_key_id() -> str:
    kid = str(getattr(settings, "DP_ENC_ACTIVE_KEY", "1"))
    if kid not in _keyring():
        raise ImproperlyConfigured(f"DP_ENC_ACTIVE_KEY='{kid}' no existe en DP_ENC_KEYS.")
    return kid


@lru_cache(maxsize=1)
def _index_key() -> bytes:
    raw = getattr(settings, "DP_INDEX_KEY", None)
    if not raw:
        raise ImproperlyConfigured("DP_INDEX_KEY no está configurado.")
    key = base64.urlsafe_b64decode(raw)
    if len(key) < 32:
        raise ImproperlyConfigured("DP_INDEX_KEY debe medir al menos 32 bytes.")
    return key


def generar_llave() -> str:
    """Genera una llave AES-256 lista para pegar en el archivo .env."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()


def encrypt(plaintext: str, *, aad: bytes | None = None) -> str:
    """
    Cifra un texto y devuelve ``v<kid>$<base64(nonce||ct||tag)>``.

    ``aad`` (Additional Authenticated Data) permite ligar el ciphertext a un
    contexto (p. ej. b"rat.actividad.observaciones"), de modo que un atacante
    con acceso de escritura a la BD no pueda mover un valor cifrado de una
    columna a otra.
    """
    if plaintext is None:
        return None
    kid = _active_key_id()
    aead = AESGCM(_keyring()[kid])
    nonce = os.urandom(NONCE_BYTES)
    ct = aead.encrypt(nonce, plaintext.encode("utf-8"), aad)
    payload = base64.urlsafe_b64encode(nonce + ct).decode()
    return f"v{kid}{PREFIX_SEP}{payload}"


def decrypt(token: str, *, aad: bytes | None = None) -> str:
    """Descifra un token producido por :func:`encrypt`."""
    if token is None:
        return None
    if PREFIX_SEP not in token or not token.startswith("v"):
        # Dato heredado en claro (migración progresiva): se devuelve tal cual.
        return token
    prefix, payload = token.split(PREFIX_SEP, 1)
    kid = prefix[1:]
    ring = _keyring()
    if kid not in ring:
        raise CryptoError(
            f"El registro fue cifrado con la llave '{kid}', que no está en el "
            f"keyring actual. No elimine llaves antiguas antes de rotar."
        )
    raw = base64.urlsafe_b64decode(payload.encode())
    nonce, ct = raw[:NONCE_BYTES], raw[NONCE_BYTES:]
    try:
        return AESGCM(ring[kid]).decrypt(nonce, ct, aad).decode("utf-8")
    except InvalidTag as exc:  # pragma: no cover
        raise CryptoError(
            "Fallo de autenticación GCM: el dato fue alterado en la base de "
            "datos o el AAD no corresponde."
        ) from exc


def blind_index(value: str, *, scope: str = "") -> str:
    """
    HMAC-SHA256 truncado y determinista para búsquedas de igualdad exacta.

    Normaliza a minúsculas y sin espacios extremos para que la búsqueda sea
    case-insensitive. ``scope`` separa dominios (p. ej. 'usuario.email') e
    impide correlacionar el mismo valor entre tablas distintas.
    """
    if value is None:
        return ""
    norm = " ".join(str(value).strip().lower().split())
    mac = hmac.new(_index_key(), f"{scope}|{norm}".encode("utf-8"), hashlib.sha256)
    return base64.urlsafe_b64encode(mac.digest()[:BLIND_INDEX_BYTES]).decode()


def reset_cache() -> None:
    """Limpia las cachés de llaves (usar tras rotación en caliente)."""
    _keyring.cache_clear()
    _active_key_id.cache_clear()
    _index_key.cache_clear()
