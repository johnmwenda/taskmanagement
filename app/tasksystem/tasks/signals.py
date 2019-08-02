import django.dispatch

# define partial_update_done signal
task_progress_update = django.dispatch.Signal(providing_args=["progress_instance"])

