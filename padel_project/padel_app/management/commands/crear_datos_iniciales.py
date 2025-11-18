from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from padel_app.models import Club, CustomUser

class Command(BaseCommand):
    help = 'Crea datos iniciales para la PoC'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Crear club de ejemplo
        club, created = Club.objects.get_or_create(
            nombre_club="Club Padel Ejemplo",
            defaults={
                'canchas_techo': 2,
                'canchas_sin_techo': 4,
                'tipo_superficie': 'Vidrio/Sintetico',
                'cant_profesores': 3,
                'direccion': 'Av. Ejemplo 123',
                'localidad': 'CABA',
                'provincia': 'Buenos Aires',
                'celular': '+5491112345678',
                'mail': 'info@clubpadelejemplo.com',
                'valor_hora_ar': 15000.00
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Club creado exitosamente'))
        
        # Crear profesor admin
        profesor, created = User.objects.get_or_create(
            username='profesor',
            defaults={
                'rol': 'Profesor_Admin',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'jugador_de': 'Drive',
                'mano_habil': 'D',
                'celular': '+5491122334455',
                'mail': 'profesor@ejemplo.com',
                'nivel_categoria': 9,
                'direccion': 'Av. Profesor 456',
                'localidad': 'CABA',
                'provincia': 'Buenos Aires',
                'pais': 'Argentina'
            }
        )
        if created:
            profesor.set_password('pass123')
            profesor.save()
            self.stdout.write(self.style.SUCCESS('Profesor creado exitosamente'))
        
        # Crear alumno
        alumno, created = User.objects.get_or_create(
            username='alumno',
            defaults={
                'rol': 'Alumno_Usuario',
                'nombre': 'María',
                'apellido': 'González',
                'jugador_de': 'Revés',
                'mano_habil': 'D',
                'celular': '+5491166778899',
                'mail': 'alumno@ejemplo.com',
                'nivel_categoria': 5,
                'direccion': 'Calle Alumno 789',
                'localidad': 'CABA',
                'provincia': 'Buenos Aires',
                'pais': 'Argentina'
            }
        )
        if created:
            alumno.set_password('pass123')
            alumno.save()
            self.stdout.write(self.style.SUCCESS('Alumno creado exitosamente'))
        
        self.stdout.write(self.style.SUCCESS('Datos iniciales creados exitosamente'))