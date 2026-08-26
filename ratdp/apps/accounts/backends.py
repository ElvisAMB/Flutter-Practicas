"""Backend de autenticación con bloqueo temporal por intentos fallidos."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.utils import timezone


class BackendConBloqueo(ModelBackend):
    """
    Añade dos controles al backend estándar:

    1. Bloqueo temporal tras N intentos fallidos (mitiga fuerza bruta sin
       depender de un WAF externo).
    2. Verificación de contraseña incluso cuando el usuario no existe, para
       evitar la enumeración de usuarios por diferencia de tiempo de respuesta.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        Usuario = get_user_model()
        username = username or kwargs.get(Usuario.USERNAME_FIELD)
        if username is None or password is None:
            return None
        try:
            user = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            Usuario().set_password(password)  # iguala el tiempo de respuesta
            return None

        if user.esta_bloqueado:
            raise PermissionDenied(
                f"Cuenta bloqueada temporalmente hasta "
                f"{timezone.localtime(user.bloqueado_hasta):%H:%M}."
            )
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
