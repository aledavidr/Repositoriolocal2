# padel_app/forms.py
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from .models import CustomUser

class CustomPasswordResetForm(PasswordResetForm):
    """
    Form personalizado para password reset que usa el campo 'mail'
    en lugar del campo 'email' por defecto de Django
    """
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm dark:bg-gray-700',
            'placeholder': 'tu@email.com'
        })
    )
    
    def get_users(self, email):
        """Busca usuarios por el campo 'mail' en lugar de 'email'"""
        active_users = CustomUser.objects.filter(
            mail__iexact=email, 
            is_active=True
        )
        return active_users