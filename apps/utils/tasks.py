from celery import shared_task
from django.contrib.auth import get_user_model
User = get_user_model()

@shared_task
def test_celery_task(x, y):
    """Simple test task to verify Celery is working"""
    from apps.utils.logger import get_logger
    celery_logger = get_logger('celery')
    result = x + y
    celery_logger.info(f"Celery task executed: {x} + {y} = {result}")
    return result

@shared_task
def send_welcome_email_task(user_id, password):
    """
    Alternative task to send welcome email - more modular approach
    """
    from apps.utils.logger import get_logger
    celery_logger = get_logger('celery')
    try:
        user = User.objects.get(id=user_id)
        from utils.email import send_email_message
        send_email_message.delay(
            subject="Welcome to Azure Horizon | Login Details",
            template_name="welcome.html",
            context={
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "password": password
            },
            recipient_list=[user.email]
        )
        celery_logger.info(f"Welcome email queued for user: {user.username}")
        return True
    except User.DoesNotExist:
        celery_logger.error(f"User with ID {user_id} not found")
        return False
    except Exception as e:
        celery_logger.error(f"Error sending welcome email: {str(e)}")
        return False