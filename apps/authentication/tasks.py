from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_welcome_email_task(self,username, email, password):
    """
    Celery task to send welcome email to new users
    """
    try:
        subject = 'Welcome to Our Resort'
        message = f"""
        Thank you for registering with us!
        
        Here are your login details:
        Username: {username}
        Email: {email}
        Password: {password}
        
        Please keep your credentials safe and do not share them with anyone.
        
        Best regards,
        The Resort Team
        """

        send_mail(
            subject=subject, 
            message=message, 
            from_email=settings.DEFAULT_FROM_EMAIL, 
            recipient_list=[email],
            fail_silently=False
        )
        
        logger.info(f"Welcome email sent successfully to {email}")
        return f"Email sent to {email}"
        
    except Exception as exc:
        logger.error(f"Failed to send email to {email}: {str(exc)}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))