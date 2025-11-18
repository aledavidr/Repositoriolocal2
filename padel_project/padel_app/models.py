from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.mail import send_mail  # ← AGREGAR ESTE IMPORT

# Custom User Model (EXISTENTE)
class CustomUser(AbstractUser):
    ROL_CHOICES = [
        ('Profesor_Admin', 'Profesor/Administrador'),
        ('Alumno_Usuario', 'Alumno/Usuario'),
    ]
    
    HAND_CHOICES = [
        ('Z', 'Zurdo'),
        ('D', 'Diestro'),
    ]
    
    PLAYER_SIDE_CHOICES = [
        ('Drive', 'Drive'),
        ('Revés', 'Revés'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='Alumno_Usuario')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    nacimiento = models.DateField(null=True, blank=True)
    jugador_de = models.CharField(max_length=10, choices=PLAYER_SIDE_CHOICES, default='Drive')
    mano_habil = models.CharField(max_length=1, choices=HAND_CHOICES, default='D')
    celular = models.CharField(max_length=20)
    mail = models.EmailField()
    nivel_categoria = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        default=1
    )
    direccion = models.CharField(max_length=200, blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, blank=True)
    
    # MÉTODOS PARA PASSWORD RESET - AGREGAR ESTOS
    def get_email(self):
        """Retorna el email para password reset"""
        return self.mail
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Envía email al usuario - requerido por Django"""
        send_mail(subject, message, from_email, [self.mail], **kwargs)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Club Model (EXISTENTE)
class Club(models.Model):
    SURFACE_CHOICES = [
        ('Vidrio/Sintetico', 'Vidrio/Sintético'),
        ('Pared/Sintetico', 'Pared/Sintético'),
        ('Pared/Piso Cemento', 'Pared/Piso Cemento'),
    ]
    
    nombre_club = models.CharField(max_length=200)
    canchas_techo = models.IntegerField(default=0)
    canchas_sin_techo = models.IntegerField(default=0)
    es_techado = models.BooleanField(default=False)
    tipo_superficie = models.CharField(max_length=20, choices=SURFACE_CHOICES)
    cant_profesores = models.IntegerField(default=0)
    direccion = models.CharField(max_length=200, blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    celular = models.CharField(max_length=20, blank=True)
    mail = models.EmailField(blank=True)
    valor_hora_ar = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.es_techado = self.canchas_techo > 0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre_club

# NUEVO: Modelo Entrenamiento (AGREGAR ESTO)
class Entrenamiento(models.Model):
    TIPO_ENTRENO_CHOICES = [
        ('Tecnica', 'Técnica'),
        ('Tactica', 'Táctica'),
        ('Fisico', 'Físico'),
        ('Estrategia', 'Estrategia'),
        ('Mixto', 'Mixto'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_entreno = models.CharField(max_length=20, choices=TIPO_ENTRENO_CHOICES, default='Mixto')
    duracion_minutos = models.IntegerField(default=60)
    nivel_minimo = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)], default=1)
    nivel_maximo = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)], default=9)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_entreno_display()})"

# Class Model (MODIFICAR el existente - NO redefinir)
class Clase(models.Model):
    descripcion = models.CharField(max_length=200, blank=True)
    id_profesor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'rol': 'Profesor_Admin'})
    fecha = models.DateField()
    hora = models.TimeField()
    confirmado = models.BooleanField(default=False)
    notificado = models.BooleanField(default=False)
    valor_ar = models.DecimalField(max_digits=10, decimal_places=2)
    entrenamiento = models.ForeignKey(Entrenamiento, on_delete=models.SET_NULL, null=True, blank=True)  # ← NUEVO CAMPO
    
    def __str__(self):
        entrenamiento_str = f" - {self.entrenamiento.nombre}" if self.entrenamiento else ""
        return f"Clase {self.fecha} {self.hora} - {self.id_profesor}{entrenamiento_str}"

# Pairing Model (EXISTENTE)
class Emparejamiento(models.Model):
    descripcion = models.CharField(max_length=200, blank=True)
    id_clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    jugadores = models.ManyToManyField(CustomUser, limit_choices_to={'rol': 'Alumno_Usuario'})
    
    def __str__(self):
        return f"Emparejamiento {self.id_clase}"

# Waiting List Model (EXISTENTE)
class EnEspera(models.Model):
    descripcion = models.CharField(max_length=200, blank=True)
    id_club = models.ForeignKey(Club, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'rol': 'Alumno_Usuario'})
    fecha = models.DateField()
    hora = models.TimeField()
    id_clase = models.ForeignKey(Clase, on_delete=models.SET_NULL, null=True, blank=True)
    id_emparejamiento = models.ForeignKey(Emparejamiento, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Espera: {self.id_usuario} - {self.fecha} {self.hora}"

# Notification Model (MODIFICAR el existente - NO redefinir)
class Notificacion(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('Confirmacion', 'Confirmación'),
        ('Cancelacion', 'Cancelación'),
        ('Recordatorio', 'Recordatorio'),
    ]
    
    id_usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    id_clase = models.ForeignKey(Clase, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    enviada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notificación {self.tipo_evento} - {self.id_usuario}"
    
    def marcar_como_enviada(self):
        """Marca la notificación como enviada con timestamp"""
        self.enviada = True
        self.fecha_envio = timezone.now()
        self.save()