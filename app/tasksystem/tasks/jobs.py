# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from tasksystem.tasks.emails import send_task_progress_email


@shared_task
def delay_task_progress_notifications(notifications, progress_instance):
    print("sending progress update email to subscribers")
    send_task_progress_email(notifications, progress_instance)
    print("completed sending progress update emails")
