import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# @shared_task(bind=True, max_retries=3)
def send_email_message(subject, template_name, context, recipient_list, from_email=None):
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
        email_msg.send()

        logger.info(f"HTML email sent successfully to {recipient_list}")
        return True

    except Exception as e:
        logger.error(f"Failed to send HTML email: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))