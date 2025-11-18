from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View, DetailView  # ← Agrega DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from .models import *
from .utils import enviar_notificacion_email



# Mixin para verificar si es profesor - DEBE IR PRIMERO
class EsProfesorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.rol == 'Profesor_Admin'

# Vistas principales
class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if self.request.user.rol == 'Alumno_Usuario':
                context['en_espera'] = EnEspera.objects.filter(id_usuario=self.request.user)
            elif self.request.user.rol == 'Profesor_Admin':
                context['clases_pendientes'] = Clase.objects.filter(confirmado=False)
        return context

class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'perfil.html'

class EditarPerfilView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'editar_perfil.html'
    fields = ['nombre', 'apellido', 'nacimiento', 'jugador_de', 'mano_habil', 'celular', 'mail', 'direccion', 'localidad', 'provincia', 'pais']
    success_url = reverse_lazy('perfil')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)

# Vistas para Lista de Espera (Alumnos)
class ListaEsperaListView(LoginRequiredMixin, ListView):
    model = EnEspera
    template_name = 'lista_espera.html'
    context_object_name = 'en_espera'
    
    def get_queryset(self):
        return EnEspera.objects.filter(id_usuario=self.request.user).order_by('-fecha', '-hora')

class AgregarEsperaView(LoginRequiredMixin, CreateView):
    model = EnEspera
    template_name = 'agregar_espera.html'
    fields = ['id_club', 'fecha', 'hora', 'descripcion']
    success_url = reverse_lazy('lista_espera')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubes'] = Club.objects.all()
        return context
    
    def form_valid(self, form):
        form.instance.id_usuario = self.request.user
        messages.success(self.request, 'Te has agregado a la lista de espera correctamente.')
        return super().form_valid(form)

class EditarEsperaView(LoginRequiredMixin, UpdateView):
    model = EnEspera
    template_name = 'editar_espera.html'
    fields = ['id_club', 'fecha', 'hora', 'descripcion']
    success_url = reverse_lazy('lista_espera')
    
    def get_queryset(self):
        return EnEspera.objects.filter(id_usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Solicitud de espera actualizada correctamente.')
        return super().form_valid(form)

class EliminarEsperaView(LoginRequiredMixin, DeleteView):
    model = EnEspera
    template_name = 'eliminar_espera.html'
    success_url = reverse_lazy('lista_espera')
    
    def get_queryset(self):
        return EnEspera.objects.filter(id_usuario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Solicitud de espera eliminada correctamente.')
        return super().delete(request, *args, **kwargs)

# Vistas para Emparejamiento (Profesores)
class EmparejamientoView(EsProfesorMixin, ListView):
    model = EnEspera
    template_name = 'emparejamiento.html'
    context_object_name = 'lista_espera'
    
    def get_queryset(self):
        # Agrupar por fecha, hora y club
        return EnEspera.objects.filter(
            id_clase__isnull=True,
            id_emparejamiento__isnull=True
        ).order_by('fecha', 'hora', 'id_club')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agrupar por fecha, hora y club para facilitar el emparejamiento
        espera_agrupada = {}
        for item in context['lista_espera']:
            key = f"{item.fecha}_{item.hora}_{item.id_club.id}"
            if key not in espera_agrupada:
                espera_agrupada[key] = []
            espera_agrupada[key].append(item)
        context['espera_agrupada'] = espera_agrupada
        return context

class CrearEmparejamientoView(EsProfesorMixin, View):
    def post(self, request):
        jugadores_ids = request.POST.getlist('jugadores')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        club_id = request.POST.get('club_id')
        descripcion = request.POST.get('descripcion', '')
        valor_ar = request.POST.get('valor_ar')
        
        if len(jugadores_ids) < 2 or len(jugadores_ids) > 4:
            messages.error(request, 'Debes seleccionar entre 2 y 4 jugadores.')
            return redirect('emparejamiento')
        
        try:
            # Crear la clase
            clase = Clase.objects.create(
                descripcion=descripcion,
                id_profesor=request.user,
                fecha=fecha,
                hora=hora,
                valor_ar=valor_ar,
                confirmado=True
            )
            
            # Crear el emparejamiento
            emparejamiento = Emparejamiento.objects.create(
                descripcion=descripcion,
                id_clase=clase
            )
            emparejamiento.jugadores.set(jugadores_ids)
            
            # Actualizar las entradas en espera
            EnEspera.objects.filter(
                id_usuario__in=jugadores_ids,
                fecha=fecha,
                hora=hora,
                id_club_id=club_id
            ).update(id_clase=clase, id_emparejamiento=emparejamiento)
            
emails_exitosos = 0
emails_fallidos = 0

for jugador_id in jugadores_ids:
    notificacion = Notificacion.objects.create(
        id_usuario_id=jugador_id,
        tipo_evento='Confirmacion',
        id_clase=clase
    )
    
    # ENVÍO CON VERIFICACIÓN
    jugador = CustomUser.objects.get(id=jugador_id)
    email_enviado = enviar_notificacion_email(jugador, 'Confirmacion', clase, notificacion)
    
    if email_enviado:
        emails_exitosos += 1
        # No necesitas marcar manualmente como enviada porque 
        # enviar_notificacion_email ya lo hace si se pasa notificacion_obj
    else:
        emails_fallidos += 1
        messages.warning(request, f'Error enviando email a {jugador.nombre}')

# Mensaje final consolidado
if emails_fallidos == 0:
    messages.success(request, f'✅ Emparejamiento creado exitosamente para {len(jugadores_ids)} jugadores. Todas las notificaciones enviadas.')
else:
    messages.success(request, f'⚠️ Emparejamiento creado para {len(jugadores_ids)} jugadores. {emails_exitosos} notificaciones enviadas, {emails_fallidos} fallaron.')

# NUEVAS VISTAS PARA GESTIÓN DEL PROFESOR
class GestionAlumnosView(EsProfesorMixin, ListView):
    model = CustomUser
    template_name = 'gestion_alumnos.html'
    context_object_name = 'alumnos'
    
    def get_queryset(self):
        return CustomUser.objects.filter(rol='Alumno_Usuario').order_by('nombre')

class EditarAlumnoView(EsProfesorMixin, UpdateView):
    model = CustomUser
    template_name = 'editar_alumno.html'
    fields = ['nombre', 'apellido', 'nacimiento', 'jugador_de', 'mano_habil', 'celular', 'mail', 'nivel_categoria', 'direccion', 'localidad', 'provincia', 'pais']
    success_url = reverse_lazy('gestion_alumnos')
    
    def get_queryset(self):
        return CustomUser.objects.filter(rol='Alumno_Usuario')
    
    def form_valid(self, form):
        messages.success(self.request, 'Alumno actualizado correctamente.')
        return super().form_valid(form)

class GestionEsperaView(EsProfesorMixin, ListView):
    model = EnEspera
    template_name = 'gestion_espera.html'
    context_object_name = 'lista_espera'
    
    def get_queryset(self):
        return EnEspera.objects.select_related(
            'id_usuario', 
            'id_club', 
            'id_clase',
            'id_clase__id_profesor'
        ).prefetch_related(
            'id_clase__notificacion_set'
        ).all().order_by('-fecha', '-hora')

class CancelarEsperaView(EsProfesorMixin, DeleteView):
    model = EnEspera
    template_name = 'cancelar_espera.html'
    success_url = reverse_lazy('gestion_espera')
    
    def delete(self, request, *args, **kwargs):
        espera = self.get_object()
        # Crear notificación de cancelación
        notificacion = Notificacion.objects.create(
            id_usuario=espera.id_usuario,
            tipo_evento='Cancelacion',
            fecha=timezone.now(),
            hora=timezone.now()
        )
        # Enviar email real
        enviar_notificacion_email(espera.id_usuario, 'Cancelacion')
        notificacion.enviada = True
        notificacion.save()
        
        messages.success(request, 'Solicitud cancelada y notificación enviada.')
        return super().delete(request, *args, **kwargs)

class ConfirmarClaseView(EsProfesorMixin, View):
    def post(self, request, pk):
        clase = get_object_or_404(Clase, pk=pk)
        clase.confirmado = True
        clase.save()
        
        # Notificar a todos los jugadores
        emparejamiento = clase.emparejamiento_set.first()
        if emparejamiento:
            for jugador in emparejamiento.jugadores.all():
                notificacion = Notificacion.objects.create(
                    id_usuario=jugador,
                    tipo_evento='Confirmacion',
                    id_clase=clase
                )
                # Enviar email real
                enviar_notificacion_email(jugador, 'Confirmacion', clase)
                notificacion.enviada = True
                notificacion.save()
        
        messages.success(request, 'Clase confirmada y notificaciones enviadas.')
        return redirect('gestion_espera')
class RegistroView(CreateView):
    model = CustomUser
    template_name = 'registration/register.html'
    fields = ['username', 'password', 'nombre', 'apellido', 'mail', 'celular', 'jugador_de', 'mano_habil', 'direccion', 'localidad', 'provincia']
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # Configurar valores por defecto para alumnos
        form.instance.rol = 'Alumno_Usuario'
        form.instance.nivel_categoria = 1  # Nivel inicial por defecto
        
        # Guardar el usuario con password hasheado
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        messages.success(self.request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
        return redirect(self.success_url)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Hacer el campo password visible en el form
        form.fields['password'].widget.attrs.update({'class': 'form-control'})
        return form


class DetalleNotificacionView(EsProfesorMixin, DetailView):
    model = Notificacion
    template_name = 'detalle_notificacion.html'
    context_object_name = 'notificacion'
    
    def get_queryset(self):
        return Notificacion.objects.select_related('id_usuario', 'id_clase')

class DetalleClaseView(EsProfesorMixin, DetailView):
    model = Clase
    template_name = 'detalle_clase.html'
    context_object_name = 'clase'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información adicional
        context['emparejamiento'] = self.object.emparejamiento_set.first()
        context['notificaciones'] = self.object.notificacion_set.all()
        context['alumnos_en_espera'] = EnEspera.objects.filter(id_clase=self.object)
        return context
 # CRUD de Clases
class ListaClasesView(EsProfesorMixin, ListView):
    model = Clase
    template_name = 'clases/lista_clases.html'
    context_object_name = 'clases'
    
    def get_queryset(self):
        return Clase.objects.select_related('id_profesor', 'entrenamiento').prefetch_related('emparejamiento_set__jugadores').all().order_by('-fecha', '-hora')

class CrearClaseView(EsProfesorMixin, CreateView):
    model = Clase
    template_name = 'clases/crear_clase.html'
    fields = ['fecha', 'hora', 'valor_ar', 'entrenamiento', 'descripcion']
    success_url = reverse_lazy('lista_clases')
    
    def form_valid(self, form):
        form.instance.id_profesor = self.request.user
        form.instance.confirmado = False
        messages.success(self.request, 'Clase creada exitosamente. Ahora puedes agregar alumnos.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entrenamientos'] = Entrenamiento.objects.all()
        return context

class EditarClaseView(EsProfesorMixin, UpdateView):
    model = Clase
    template_name = 'clases/editar_clase.html'
    fields = ['fecha', 'hora', 'valor_ar', 'entrenamiento', 'descripcion', 'confirmado']
    success_url = reverse_lazy('lista_clases')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entrenamientos'] = Entrenamiento.objects.all()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Clase actualizada exitosamente.')
        return super().form_valid(form)

class EliminarClaseView(EsProfesorMixin, DeleteView):
    model = Clase
    template_name = 'clases/eliminar_clase.html'
    success_url = reverse_lazy('lista_clases')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Clase eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

# Vista para gestionar alumnos en una clase
class GestionarAlumnosClaseView(EsProfesorMixin, DetailView):
    model = Clase
    template_name = 'clases/gestionar_alumnos.html'
    context_object_name = 'clase'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clase = self.object
        
        # Obtener emparejamiento existente
        emparejamiento = clase.emparejamiento_set.first()
        alumnos_actuales = emparejamiento.jugadores.all() if emparejamiento else []
        
        # Obtener alumnos en espera que coincidan con la fecha y hora de la clase
        alumnos_en_espera = EnEspera.objects.filter(
            fecha=clase.fecha,
            hora=clase.hora,
            id_clase__isnull=True  # Solo los que no tienen clase asignada
        ).select_related('id_usuario')
        
        context['alumnos_actuales'] = alumnos_actuales
        context['alumnos_en_espera'] = alumnos_en_espera
        context['emparejamiento'] = emparejamiento
        return context

class AgregarAlumnoClaseView(EsProfesorMixin, View):
    def post(self, request, clase_id):
        clase = get_object_or_404(Clase, id=clase_id)
        alumno_id = request.POST.get('alumno_id')
        
        try:
            alumno = CustomUser.objects.get(id=alumno_id, rol='Alumno_Usuario')
            
            # Obtener o crear el emparejamiento
            emparejamiento, created = Emparejamiento.objects.get_or_create(
                id_clase=clase,
                defaults={'descripcion': f'Emparejamiento para clase del {clase.fecha}'}
            )
            
            # Agregar alumno al emparejamiento
            if alumno not in emparejamiento.jugadores.all():
                emparejamiento.jugadores.add(alumno)
                
                # Actualizar la entrada en espera del alumno
                EnEspera.objects.filter(
                    id_usuario=alumno,
                    fecha=clase.fecha,
                    hora=clase.hora
                ).update(id_clase=clase, id_emparejamiento=emparejamiento)
                
                messages.success(request, f'Alumno {alumno.nombre} agregado a la clase.')
            else:
                messages.warning(request, f'El alumno {alumno.nombre} ya está en esta clase.')
                
        except CustomUser.DoesNotExist:
            messages.error(request, 'Alumno no encontrado.')
        
        return redirect('gestionar_alumnos_clase', pk=clase_id)

class QuitarAlumnoClaseView(EsProfesorMixin, View):
    def post(self, request, clase_id):
        clase = get_object_or_404(Clase, id=clase_id)
        alumno_id = request.POST.get('alumno_id')
        
        try:
            alumno = CustomUser.objects.get(id=alumno_id)
            emparejamiento = clase.emparejamiento_set.first()
            
            if emparejamiento and alumno in emparejamiento.jugadores.all():
                emparejamiento.jugadores.remove(alumno)
                
                # Liberar la entrada en espera del alumno
                EnEspera.objects.filter(
                    id_usuario=alumno,
                    id_clase=clase
                ).update(id_clase=None, id_emparejamiento=None)
                
                messages.success(request, f'Alumno {alumno.nombre} removido de la clase.')
            else:
                messages.warning(request, 'El alumno no está en esta clase.')
                
        except CustomUser.DoesNotExist:
            messages.error(request, 'Alumno no encontrado.')
        
        return redirect('gestionar_alumnos_clase', pk=clase_id)  
      