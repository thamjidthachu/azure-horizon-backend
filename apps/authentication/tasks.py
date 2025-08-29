from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_welcome_email_task(self, username, email, password):
    """
    Celery task to send welcome HTML email to new users
    """
    try:
        subject = 'Welcome to Azure Horizon Resort! 🌊'
        
        # Context for the template
        context = {
            'username': username,
            'email': email,
            'password': password,
            'login_url': f'{settings.NEXT_FRONTEND_BASE_URL}/login',
            'company_name': 'Azure Horizon',
            'current_year': '2025'
        }
        
        # Render HTML email template
        html_content = render_to_string('welcome.html', context)
        
        # Create plain text version by stripping HTML tags
        text_content = strip_tags(html_content)
        
        # Create EmailMultiAlternatives object
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        
        # Attach HTML version
        email_msg.attach_alternative(html_content, "text/html")
        
        # Send the email
        email_msg.send(fail_silently=False)
        
        logger.info(f"Welcome HTML email sent successfully to {email}")
        return f"HTML email sent to {email}"
        
    except Exception as exc:
        logger.error(f"Failed to send email to {email}: {str(exc)}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


def send_html_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Utility function to send HTML emails with template
    
    Args:
        subject (str): Email subject
        template_name (str): Template file name (e.g., 'welcome.html')
        context (dict): Template context variables
        recipient_list (list): List of recipient emails
        from_email (str): Sender email (optional)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL
            
        # Render HTML email template
        html_content = render_to_string(template_name, context)
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create EmailMultiAlternatives object
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list
        )
        
        # Attach HTML version
        email_msg.attach_alternative(html_content, "text/html")
        
        # Send the email
        email_msg.send(fail_silently=False)
        
        logger.info(f"HTML email sent successfully to {recipient_list}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send HTML email: {str(e)}")
        return False