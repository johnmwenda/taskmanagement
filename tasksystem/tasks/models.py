from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)

from django.utils import timezone

from tasksystem.utils.models import SoftDeleteModel, SoftDeleteManager
from tasksystem.accounts.models import User
from tasksystem.departments.models import Category, Department
from .validators import validate_date_not_in_past


def get_default_category(self):
    return Category.objects.filter(name='DEFAULT')


class SupervisorManager(SoftDeleteManager):
    '''
    custom queries related to supervisor role tasks
    initial queryset will be all the tasks that this user has authorization
    this includes:
    1. all my department tasks, whether private or public because i am the boss
    2. all public tasks from other department
    3. all private interdepartmental tasks involving my department whether public or private
    '''

    def __init__(self, *args, **kwargs):
        super(SupervisorManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        # this queryset inherits SoftDeleteManager methods eg delete, hard_delete etc
        return super(SupervisorManager, self).get_queryset()

    def tasks(self, user):
        qs = Task.objects.filter(
            Q(department=user.department_id) |
            (~Q(department=user.department_id) & Q(access_level='pub')) |
            (
                ~Q(department=user.department_id) &
                Q(assignees__department=user.department_id) &
                Q(access_level='prv')
            )
        ).select_related('department','category', 'reporter').prefetch_related(
            'taskprogress_set', 'subscribers', 'assignees', 'attachments')
        return qs.distinct()


class JuniorManager(SoftDeleteManager):
    '''
    custom queries related to junior role tasks
    initial queryset will be all the tasks that this user has authorization
    this includes:
    1. all my tasks whether private or public (reporter)
    3. all assigned tasks (private or public)
    4. all subscribed tasks
    5. all other public tasks
    '''

    def __init__(self, *args, **kwargs):
        super(JuniorManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        # this queryset inherits SoftDeleteManager methods eg delete, hard_delete etc
        return super(JuniorManager, self).get_queryset()

    def tasks(self, user):
        qs = Task.objects.filter(
                Q(assignees=user) |
                Q(reporter=user) |
                Q(user_subscribers=user) |
                Q(access_level='pub')
            ).select_related('department','category','reporter').prefetch_related(
                'assignees', 'user_subscribers', 'taskprogress_set', 'subscribers', 'attachments')
        return qs.distinct()


        subscribed_tasks = user.subscribed_tasks.all()
        public_tasks = Task.objects.filter(access_level='pub')
        qs = public_tasks | reporter_tasks | assigned_tasks | subscribed_tasks
        qs.select_related('department','category', 'reporter').prefetch_related(
            'taskprogress_set', 'subscribers', 'assignees', 'attachments')
        return qs.distinct()


class Task(SoftDeleteModel):
    '''
    Most important model for this application. Allows users to create and list their tasks
    '''

    junior_objects = JuniorManager()
    junior_objects_with_deleted = JuniorManager(with_deleted=True)

    supervisor_objects = SupervisorManager()
    supervisor_objects_with_deleted = SupervisorManager(with_deleted=True)

    name = models.CharField(max_length=200)
    description = models.TextField(
        max_length=1000, help_text='Enter a brief description of the task', null=True, blank=True)
    due_date = models.DateTimeField(help_text='Enter due date', validators=[
                                    validate_date_not_in_past])
    complete_time = models.DateTimeField(blank=True, null=True)
    reporter = models.ForeignKey(
        get_user_model(), verbose_name='Reporter', editable=True)
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
    access_level = models.CharField(
        max_length=3, choices=ACCESS_LEVEL, default='pub', help_text='Access level')

    PRIORITY = (
        ('l', 'Low'),
        ('m', 'Medium'),
        ('h', 'High'),
    )
    priority = models.CharField(max_length=1, choices=PRIORITY, default='m')
    category = models.ForeignKey(Category, default=get_default_category)
    department = models.ForeignKey(Department)
    user_subscribers = models.ManyToManyField(
        get_user_model(),
        through='TaskSubscription',
        through_fields=('task', 'user'),
        related_name='subscribed_tasks',
        verbose_name='Subsribe Users',
        blank=True)
    department_subscribers = models.ManyToManyField(
        Department,
        through='TaskSubscription',
        through_fields=('task', 'department'),
        related_name='subscribed_tasks',
        verbose_name='Subsribe Department',
        blank=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.name

    @property
    def is_complete(self):
        return bool(self.complete_time and self.complete_time < timezone.now())


class TaskProgress(SoftDeleteModel):
    task = models.ForeignKey(Task, verbose_name='Task Progress', null=False)
    progress_comment = models.TextField(
        max_length=1000, help_text='Add a progress message', null=False)

    progress_percentage = models.IntegerField(verbose_name='percentage done',
                                              help_text='What percentage of the task is done?',
                                              default=0,
                                              validators=[MinValueValidator(0), MaxValueValidator(100)])


class TaskAttachment(SoftDeleteModel):
    '''
    A task might have one or more supporting documents/images
    '''
    name = models.CharField(max_length=100)
    task = models.ForeignKey(
        Task, related_name='attachments', verbose_name='Task')
    file_name = models.FileField(
        upload_to='tasks/%Y/%m/%d/', max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('-created_date',)

    def delete(self, *args, **kwargs):
        self.file_name.delete()
        super().delete(*args, **kwargs)


class TaskSubscription(SoftDeleteModel):
    '''
    A user can subscribe to a task, or be added as part of a task user group by another user
    '''
    task = models.ForeignKey(Task, related_name='subscribers')
    user = models.ForeignKey(get_user_model(), null=True, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    created_by = models.ForeignKey(get_user_model(), related_name='created_by')
    TASK_STATUS = (
        ('DEPARTMENT', 'DEPARMENT'),
        ('USER', 'USER'),
    )
    subscriber_type = models.CharField(max_length=20, choices=TASK_STATUS)

    def __str__(self):
        return f'task subscribed by {self.user} or {self.department}'
