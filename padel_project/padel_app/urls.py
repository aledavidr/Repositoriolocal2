from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm  # ← IMPORTAR EL FORM PERSONALIZADO

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    
    # URLs para reset de contraseña CON FORM PERSONALIZADO
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             form_class=CustomPasswordResetForm  # ← AGREGAR FORM PERSONALIZADO AQUÍ
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Perfil y usuarios
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('perfil/editar/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    
    # Lista de espera - Alumnos
    path('espera/', views.ListaEsperaListView.as_view(), name='lista_espera'),
    path('espera/agregar/', views.AgregarEsperaView.as_view(), name='agregar_espera'),
    path('espera/editar/<int:pk>/', views.EditarEsperaView.as_view(), name='editar_espera'),
    path('espera/eliminar/<int:pk>/', views.EliminarEsperaView.as_view(), name='eliminar_espera'),
    
    # Emparejamiento (solo profesores)
    path('emparejamiento/', views.EmparejamientoView.as_view(), name='emparejamiento'),
    path('emparejamiento/crear/', views.CrearEmparejamientoView.as_view(), name='crear_emparejamiento'),
    
    # Gestión de Alumnos
    path('gestion-alumnos/', views.GestionAlumnosView.as_view(), name='gestion_alumnos'),
    path('gestion-alumnos/editar/<int:pk>/', views.EditarAlumnoView.as_view(), name='editar_alumno'),
    
    # Gestión de Lista de Espera
    path('gestion-espera/', views.GestionEsperaView.as_view(), name='gestion_espera'),
    path('gestion-espera/cancelar/<int:pk>/', views.CancelarEsperaView.as_view(), name='cancelar_espera'),
    path('gestion-espera/confirmar/<int:pk>/', views.ConfirmarClaseView.as_view(), name='confirmar_clase'),
    path('gestion-espera/notificacion/<int:pk>/', views.DetalleNotificacionView.as_view(), name='detalle_notificacion'),
    path('gestion-espera/clase/<int:pk>/', views.DetalleClaseView.as_view(), name='detalle_clase'),

    path('clases/', views.ListaClasesView.as_view(), name='lista_clases'),
    path('clases/crear/', views.CrearClaseView.as_view(), name='crear_clase'),
    path('clases/editar/<int:pk>/', views.EditarClaseView.as_view(), name='editar_clase'),
    path('clases/eliminar/<int:pk>/', views.EliminarClaseView.as_view(), name='eliminar_clase'),
    path('clases/<int:pk>/gestionar-alumnos/', views.GestionarAlumnosClaseView.as_view(), name='gestionar_alumnos_clase'),
    path('clases/<int:clase_id>/agregar-alumno/', views.AgregarAlumnoClaseView.as_view(), name='agregar_alumno_clase'),
    path('clases/<int:clase_id>/quitar-alumno/', views.QuitarAlumnoClaseView.as_view(), name='quitar_alumno_clase'),
]