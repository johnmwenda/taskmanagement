from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = 'tasksystem.tasks'

    def ready(self):
        import tasksystem.tasks.receivers
