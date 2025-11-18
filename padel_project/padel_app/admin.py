
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.contrib import admin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'nombre', 'apellido', 'rol', 'nivel_categoria']
    list_filter = ['rol', 'nivel_categoria']
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal', {
            'fields': ('rol', 'nombre', 'apellido', 'nacimiento', 'jugador_de', 'mano_habil', 'celular', 'mail', 'nivel_categoria')
        }),
        ('Dirección', {
            'fields': ('direccion', 'localidad', 'provincia', 'pais')
        }),
    )

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['nombre_club', 'es_techado', 'tipo_superficie', 'valor_hora_ar']

@admin.register(Entrenamiento)  # ← NUEVO
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_entreno', 'duracion_minutos', 'nivel_minimo', 'nivel_maximo']
    list_filter = ['tipo_entreno']
    search_fields = ['nombre', 'descripcion']

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'hora', 'id_profesor', 'entrenamiento', 'confirmado']  # ← Actualizado
    list_filter = ['confirmado', 'fecha']

@admin.register(Emparejamiento)
class EmparejamientoAdmin(admin.ModelAdmin):
    list_display = ['id_clase', 'get_jugadores_count']
    
    def get_jugadores_count(self, obj):
        return obj.jugadores.count()
    get_jugadores_count.short_description = 'Jugadores'

@admin.register(EnEspera)
class EnEsperaAdmin(admin.ModelAdmin):
    list_display = ['id_usuario', 'fecha', 'hora', 'id_club']

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['id_usuario', 'tipo_evento', 'fecha_creacion', 'fecha_envio', 'enviada']  # ← Corregido
    list_filter = ['tipo_evento', 'enviada']