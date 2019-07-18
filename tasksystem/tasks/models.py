from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from tasksystem.utils.models import CreatedModified
from tasksystem.departments.models import Category, Department

class SupervisorTaskManager(models.Manager):
    # custom queries related to supervisor role tasks
    def get_private_tasks(self):
        pass

class JuniorTaskManager(models.Manager):
    # custom queries related to junior role tasks
    def get_private_tasks(self):
        pass

def get_default_category():
    return Category.objects.filter(name='DEFAULT')
    

class Task(CreatedModified):
    '''
    Most important model for this application. Allows users to create and list their tasks
    '''
    
    objects = models.Manager()
    junior_object = JuniorTaskManager()
    supervisor_object = SupervisorTaskManager()

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, help_text='Enter a brief description of the task', null=True, blank=True)
    due_date = models.DateTimeField(blank=True, null=True)
    complete_time = models.DateTimeField(blank=True, null=True)
    reporter = models.ForeignKey(get_user_model(), verbose_name='Reporter', editable=True)
    assignees = models.ManyToManyField(
        get_user_model(), 
        related_name='assigned_tasks', 
        verbose_name='Assignees', 
        blank=True)
    
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
        ('pub', 'public'),
        ('prv', 'private'),
        
    )
    access_level = models.CharField(max_length=3, choices=ACCESS_LEVEL, default='pub', help_text='Access level')

    PRIORITY = (
        ('l', 'Low'),
        ('m', 'Medium'),
        ('h', 'High'),
    )
    priority = models.CharField(max_length=1, choices=PRIORITY, default='m')
    category = models.ForeignKey(Category, default=get_default_category)
    user_subscribers = models.ManyToManyField(
        get_user_model(),
        through='TaskSubscription',
        through_fields=('task','user'),
        related_name='subscribed_tasks',
        verbose_name='Subsribe Users',
        blank=True)
    department_subscribers = models.ManyToManyField(
        Department,
        through='TaskSubscription',
        through_fields=('task','department'),
        related_name='subscribed_tasks',
        verbose_name='Subsribe Department',
        blank=True)
    
    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self

    def __str__(self):
        return self.name
    
class TaskProgress(CreatedModified):
    task = models.ForeignKey(Task, verbose_name='Task Progress')
    progress_comment = models.TextField(max_length=1000, help_text='Add a progress message')

    progress_percentage = models.IntegerField(verbose_name='percentage done',
                    help_text='What percentage of the task is done?',
                    default=0,
                    validators=[MinValueValidator(10), MaxValueValidator(400)])

class TaskAttachment(CreatedModified):
    '''
    A task might have one or more supporting documents/images
    '''
    name = models.CharField(max_length=100)
    task = models.ForeignKey(Task, verbose_name='Attachments')
    file_name = models.FileField(upload_to='tasks/%Y/%m/%d/', max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('-created_date',)

class TaskSubscription(CreatedModified):
    '''
    A user can subscribe to a task, or be added as part of a task user group by another user
    '''
    task = models.ForeignKey(Task)
    user = models.ForeignKey(get_user_model(), null=True, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    created_by = models.ForeignKey(get_user_model(), related_name='created_by')

    def __str__(self):
        return f'task subscribed by {self.user} or {self.department}'