# padel_app/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend personalizado que permite autenticar tanto por username como por email
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        
        try:
            # Buscar por username O por email (campo 'mail')
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(mail__iexact=username)
            )
        except UserModel.DoesNotExist:
            # Ejecutar el set_password para reducir el timing difference
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            # Si hay múltiples usuarios, tomar el primero
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(mail__iexact=username)
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None