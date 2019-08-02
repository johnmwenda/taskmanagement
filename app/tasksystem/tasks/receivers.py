from django.dispatch import receiver
from .signals import task_progress_update

from tasksystem.tasks.jobs import delay_task_progress_notifications


@receiver(task_progress_update)
def task_progress_notifications(sender, **kwargs):
    '''
    This receiver will notify all interested parties of a progress updates to a task
    '''
    task = sender
    progress_instance = kwargs['instance']

    progress = dict()
    progress["task"] = progress_instance.task.name
    progress["due_date"] = progress_instance.task.due_date
    progress["progress_percentage"] = progress_instance.progress_percentage
    progress["progress_comment"] = progress_instance.progress_comment
    progress["created_by"] = progress_instance.created_by.get_full_name() + ' ' + progress_instance.created_by.email

    notifications = []
    user_subscribers = task.user_subscribers.all()
    department_subscribers = task.department_subscribers.all()
    reporter = task.reporter
    assignees = task.assignees.all()
    created_by = progress_instance.created_by

    for user in user_subscribers:
        notifications.append({
            "name": user.get_full_name(),
            "email": user.email
        })

    for department in department_subscribers:
        notifications.append({
            "name": f'{department.name} members',
            "email": department.email,
            "extra": "You are receiving this email because your department has been subscribed to receive progress updates on this task"
        })

    for assignee in assignees:
        if assignee == created_by:
            # probably an assignee created a progress update, dont send them mail
            continue
        
        notifications.append({
            "name": user.get_full_name(),
            "email": user.email
        })

    if reporter != created_by:
        # probably the reporter created a progress update, dont send them mail
        notifications.append({
            "name": reporter.get_full_name(),
            "email": reporter.email
        })

    delay_task_progress_notifications.delay(notifications, progress)
