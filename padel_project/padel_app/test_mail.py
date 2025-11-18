import os
import django
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'padel_project.settings')
django.setup()

try:
    send_mail(
        'Test Email from Padel App',
        'Este es un email de prueba.',
        'aromero@fpimpresora.com.ar',
        ['aromero@fpimpresora.com.ar'],  # Envíate a ti mismo
        fail_silently=False,
    )
    print("✅ Email enviado exitosamente!")
except Exception as e:
    print(f"❌ Error enviando email: {e}")