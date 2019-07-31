from django.utils import timezone
from django.db import transaction

from rest_framework import serializers

from tasksystem.tasks.models import Task, TaskAttachment, TaskSubscription, TaskProgress
from tasksystem.departments.models import Category, Department
from tasksystem.accounts.models import User

from tasksystem.accounts.api.serializers import BasicUserSerializer


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = '__all__'


class TaskSubscriptionSerializer(serializers.ModelSerializer):
    created_by = serializers.HyperlinkedIdentityField(view_name='tasks-detail')

    class Meta:
        model = TaskSubscription
        exclude = ('created_date', 'deleted_at', 'modified_date')
        read_only_fields = ('id',)


class TaskProgressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        allow_null=True, required=False)

    class Meta:
        model = TaskProgress
        fields = ('id', 'progress_comment', 'progress_percentage')

    @transaction.atomic
    def create(self, validated_data):
        instance = validated_data.pop('instance', None)
        return TaskProgress.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance = validated_data.pop('instance', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TaskCreatingSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all())
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all())
    assignees = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), allow_null=True, required=False)
    user_subscribers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), allow_null=True, required=False)
    department_subscribers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Department.objects.all(), allow_null=True, required=False)
    taskprogress_set = TaskProgressSerializer(many=True)
    is_complete = serializers.BooleanField(required=False)

    class Meta:
        model = Task
        fields = ('name', 'description', 'due_date', 'status', 'access_level', 'priority',
                  'category', 'department', 'user_subscribers', 'department_subscribers',
                  'assignees', 'taskprogress_set', 'is_complete', 'complete_time')

    def validate_user_subscribers(self, value):
        # validate reporter cannot subscribe to their own task
        user = self.context.get('request').user
        if user in value:
            raise serializers.ValidationError(
                [f'User with ID {user.pk} is the reporter, they dont need to be subscribed to this task'])
        return value

    def validate_assignees(self, value):
        # validate junior cannot assign tasks to their supervisor
        user = self.context.get('request').user
        if(user.is_member):
            for assignee in value:
                if assignee.is_manager:
                    raise serializers.ValidationError(
                        [f'A junior cannot assign a task to a supervisor. ID {assignee.pk} - {assignee.email} is a supervisor'])
        return value

    def validate(self, attrs):
        # if is_complete field is passed, pop, and set complete_time
        is_complete = attrs.pop('is_complete', None)
        if is_complete and is_complete is True:
            attrs['complete_time'] = timezone.now()
        return attrs

    def save_taskprogress_set(self, task, taskprogress_set):
        '''
        Save taskprogress nested serializer 
        '''
        for progress_data in taskprogress_set:
            # remove passed id from data
            id = progress_data.pop('id', None)
            # use id to fetch TaskProgressInstance, in case its an update on TaskProgress
            try:
                progress_instance = TaskProgress.objects.get(
                    pk=id)
            except TaskProgress.DoesNotExist:
                progress_instance = None
            # instantiate serializer using TaskProgressInstance or None
            serializer = TaskProgressSerializer(
                data=progress_data, instance=progress_instance)

            serializer.is_valid(raise_exception=True)
            # saving serializer will either create or update TaskProgress depending on whether we found
            # an existing instance
            serializer.save(instance=progress_instance,
                            task=task)

    @transaction.atomic
    def update(self, instance, validated_data):
        # pop and save nested taskprogress serializer
        taskprogress_set = validated_data.pop("taskprogress_set", [])
        if taskprogress_set:
            self.save_taskprogress_set(instance, taskprogress_set)

        return super().update(instance, validated_data)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        department_subscribers = validated_data.pop(
            'department_subscribers', [])
        user_subscribers = validated_data.pop('user_subscribers', [])
        assignees = validated_data.pop('assignees', [])
        taskprogress_set = validated_data.pop('taskprogress_set', [])

        # create task
        task = Task.objects.create(**validated_data)

        # create user_subscribers
        user_sub_list = []
        for user_sub in user_subscribers:
            subscription = TaskSubscription(
                task=task,
                user=user_sub,
                created_by=user,
                subscriber_type='USER'
            )
            user_sub_list.append(subscription)
        TaskSubscription.objects.bulk_create(user_sub_list)

        # create department_subscribers
        department_sub_list = []
        for dept_sub in department_subscribers:
            subscription = TaskSubscription(
                task=task,
                department=dept_sub,
                created_by=user,
                subscriber_type='DEPARTMENT'
            )
            department_sub_list.append(subscription)
        TaskSubscription.objects.bulk_create(department_sub_list)

        # create task assignees
        task.assignees = [assignee.pk for assignee in assignees]

        # create initial task progress for this task
        self.save_taskprogress_set(task, taskprogress_set)

        return task


class TaskViewSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=False, slug_field='name', read_only=False)
    department = serializers.SlugRelatedField(
        queryset=Department.objects.all(),
        many=False, slug_field='name', read_only=False)
    reporter = BasicUserSerializer(read_only=True)
    assignees = BasicUserSerializer(read_only=True, many=True)
    subscribers = TaskSubscriptionSerializer(many=True)
    attachments = TaskAttachmentSerializer(many=True)
    status = serializers.SerializerMethodField()
    access_level = serializers.SerializerMethodField()
    priority = serializers.SerializerMethodField()
    is_complete = serializers.BooleanField(read_only=True)
    taskprogress_set = TaskProgressSerializer(many=True)

    class Meta:
        model = Task
        fields = ('id', 'name', 'reporter', 'assignees', 'subscribers', 'attachments',
                  'category', 'department',  'description', 'due_date', 'complete_time',
                  'status', 'access_level', 'priority', 'created_date',
                  'modified_date', 'is_complete', 'taskprogress_set')
        read_only_fields = ('id', 'created_date',
                            'modified_date', 'complete_time')

    # def create(self, validated_data):
    #     print(validated_data)
    #     return

    def get_status(self, obj):
        return obj.get_status_display()

    def get_access_level(self, obj):
        return obj.get_access_level_display()

    def get_priority(self, obj):
        return obj.get_priority_display()
