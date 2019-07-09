from django.db import models

from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from tasksystem.utils.models import CreatedModified
from tasksystem.departments.models import Category

class SupervisorTaskManager(models.Manager):
    # custom queries related to supervisor role tasks
    def get_private_tasks(self):
        pass

class JuniorTaskManager(models.Manager):
    # custom queries related to junior role tasks
    def get_private_tasks(self):
        pass


class Task(CreatedModified):
    '''
    Most important model for this application. Allows users to create and list their tasks
    '''
    
    junior_objects = JuniorTaskManager()
    supervisor_objects = SupervisorTaskManager()

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, help_text='Enter a brief description of the task', null=True, blank=True)
    due_date = models.DateTimeField(blank=True, null=True)
    complete_time = models.DateTimeField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_tasks', verbose_name='Reporter', editable=False)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_tasks', verbose_name='Assignees')
    
    TASK_STATUS = (
        ('n', 'Not Started'),
        ('p', 'On Progress'),
        ('c', 'Complete'),
    )
    status = models.CharField(
        max_length=1,
        choices=TASK_STATUS,
        blank=True,
        default='n',
        help_text='Status of Task')

    ACCESS_LEVEL = (
        ('prv', 'private'),
        ('pub', 'public')
    )
    access_level = models.CharField(max_length=3, choices=ACCESS_LEVEL, default='pub', help_text='Access level')
    category = models.ForeignKey(Category, default=lambda: Category.objects.filter(name='DEFAULT'))
    task_user_group = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_taskgroups', verbose_name='Notify Users' )

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self

    def get_manager_object(self):
        '''
        Gets the supervisor object of the reporter/owner of this task
        '''
        pass
    

class TaskProgress(CreatedModified):
    task = models.ForeignKey(Task, verbose_name='Task Progress')
    progress_comment = models.TextField(max_length=1000, help_text='Add a progress message')

    progress_percentage = models.IntegerField(verbose_name='What percentage of the task is done?',
                    help_text='What percentage of the task is done?',
                    default=0,
                    validators=[MinValueValidator(10), MaxValueValidator(400)])


class TaskAttachment(CreatedModified):
    name = models.CharField(max_length=100)
    task = models.ForeignKey(Task, verbose_name='Attachments')
    fileName = models.FileField(upload_to='tasks/%Y/%m/%d/', max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('-created_date',)