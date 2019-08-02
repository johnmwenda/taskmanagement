from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

print(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)


def send_task_progress_email(notifications, progress):
    """Sends an email to user about a progress update."""
    for notify in notifications:
        context = {
            "name": notify["name"],
            "task": progress["task"],
            "due_date": progress["due_date"],
            "progress_percentage": progress["progress_percentage"],
            "progress_comment": progress["progress_comment"],
            "created_by": progress["created_by"],
            "extra": progress.get('extra', None)
        }
        msg_html = render_to_string('email/progress_update.html', context)
        msg = EmailMessage(
            subject='Task Progress Update',
            body=msg_html,
            from_email=settings.EMAIL_HOST_USER,
            to=[notify["email"]])
        msg.content_subtype = "html"  # Main content is now text/html
        return msg.send()
