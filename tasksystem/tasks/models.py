from django.db import models

from django.conf import settings

class SupervisorTaskManager(models.Manager):
    # custom filters related to supervisor tasks
    def get_private_tasks(self):
        pass

class JuniorTaskManager(models.Manager):
    # custom filters related to junior tasks
    def get_private_tasks(self):
        pass


# Create your models here.
class Task(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_tasks', verbose_name='Reporter', editable=False)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_tasks', verbose_name='Assignees')
    is_private = models.BooleanField(default=False)

    junior_objects = JuniorTaskManager()
    supervisor_objects = SupervisorTaskManager()

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self

    def get_manager_object(self):
        '''
        Gets the manager object of the reporter(owner) of this task
        '''
        pass
    
