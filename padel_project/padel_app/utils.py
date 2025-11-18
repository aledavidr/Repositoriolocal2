# utils.py - VERSIÓN MEJORADA
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def enviar_notificacion_email(usuario, tipo_evento, clase=None, notificacion_obj=None):
    """
    Función para enviar notificaciones por email CON MEJOR LOGGING
    """
    if tipo_evento == 'Confirmacion':
        asunto = '🎾 Clase de Pádel Confirmada'
        entrenamiento_info = f"\n🏸 Entrenamiento: {clase.entrenamiento.nombre}" if clase and clase.entrenamiento else ""
        mensaje = f"""
        Hola {usuario.nombre},
        
        Tu clase de pádel ha sido confirmada.
        
        📅 Fecha: {clase.fecha if clase else 'N/A'}
        ⏰ Hora: {clase.hora if clase else 'N/A'}
        💰 Valor: ${clase.valor_ar if clase else 'N/A'}
        👨‍🏫 Profesor: {clase.id_profesor.nombre if clase and clase.id_profesor else 'N/A'}
        {entrenamiento_info}
        
        ¡Nos vemos en la cancha!
        
        Saludos,
        Equipo Padel App
        """
    elif tipo_evento == 'Cancelacion':
        asunto = '❌ Clase de Pádel Cancelada'
        mensaje = f"""
        Hola {usuario.nombre},
        
        Lamentamos informarte que tu clase de pádel ha sido cancelada.
        
        📅 Fecha: {clase.fecha if clase else 'N/A'}
        ⏰ Hora: {clase.hora if clase else 'N/A'}
        
        Te contactaremos pronto para reagendar.
        
        Saludos,
        Equipo Padel App
        """
    else:
        asunto = '🔔 Recordatorio - Clase de Pádel'
        mensaje = f"""
        Hola {usuario.nombre},
        
        Recordatorio: Tienes una clase de pádel pronto.
        
        📅 Fecha: {clase.fecha if clase else 'N/A'}
        ⏰ Hora: {clase.hora if clase else 'N/A'}
        
        ¡No faltes!
        
        Saludos,
        Equipo Padel App
        """
    
    try:
        logger.info(f"🔧 Intentando enviar email a {usuario.mail} - Tipo: {tipo_evento}")
        
        # ENVÍO REAL DE EMAIL
        resultado = send_mail(
            asunto,
            mensaje,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'aromero@fpimpresora.com.ar'),
            [usuario.mail],
            fail_silently=False,
        )
        
        logger.info(f"✅ Email enviado exitosamente a: {usuario.mail} - Resultado: {resultado}")
        
        # Marcar como enviada en la base de datos
        if notificacion_obj:
            notificacion_obj.marcar_como_enviada()
            logger.info(f"📝 Notificación marcada como enviada en BD")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR enviando email a {usuario.mail}: {str(e)}")
        return False