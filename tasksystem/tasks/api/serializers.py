from django.utils import timezone
from django.db import transaction

from rest_framework import serializers

from tasksystem.tasks.models import Task, TaskAttachment, TaskSubscription
from tasksystem.departments.models import Category, Department
from tasksystem.accounts.models import User
from tasksystem.departments.api.serializers import (
    CategorySlimSerializer,
    DepartmentSlimSerializer
)
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


class TaskCreatingSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    assignees = serializers.PrimaryKeyRelatedField( 
                many=True, queryset=User.objects.all(), allow_null=True, required=False)
    user_subscribers = serializers.PrimaryKeyRelatedField( 
                        many=True, queryset=User.objects.all(), allow_null=True, required=False)
    department_subscribers = serializers.PrimaryKeyRelatedField( 
                        many=True, queryset=Department.objects.all(), allow_null=True, required=False)
    
    class Meta:
        model = Task
        fields = ('name', 'description', 'due_date', 'status', 'access_level', 'priority',
                'category', 'department', 'user_subscribers', 'department_subscribers', 'assignees' )

    def validate(self, attrs): 

        # validate user_subscribers
        user_subscribers = attrs.get('user_subscribers', [])
        assignees = attrs.get('assignees', [])
        user = self.context.get('request').user
        if user in user_subscribers:
            raise serializers.ValidationError(
                    {"user_subscribers":[f'User with ID {user.pk} is the reporter, they dont need to be subscribed to this task']})

        # validate junior cannot assign tasks to their supervisor
        if(user.is_member):
            for assignee in assignees:
                if assignee.is_manager:
                    raise serializers.ValidationError(
                        {"assignees": [f'A junior cannot assign a task to a supervisor. ID {assignee.pk} is a supervisor']})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # sid = transaction.savepoint()
        user = self.context.get('request').user
        department_subscribers = validated_data.pop('department_subscribers')
        user_subscribers = validated_data.pop('user_subscribers')
        assignees = validated_data.pop('assignees')

        # create task
        task = Task.objects.create(**validated_data)
        
        # create user_subscribers
        user_sub_list = []
        for user_sub in user_subscribers:
            subscription = TaskSubscription(
                task = task,
                user = user_sub,
                created_by = user,
                subscriber_type = 'USER'
            )
            user_sub_list.append(subscription)
        TaskSubscription.objects.bulk_create(user_sub_list)
        
        # create department_subscribers
        department_sub_list = []
        for dept_sub in department_subscribers:
            subscription = TaskSubscription(
                task = task,
                department = dept_sub,
                created_by = user,
                subscriber_type = 'DEPARTMENT'
            )
            department_sub_list.append(subscription)
        TaskSubscription.objects.bulk_create(department_sub_list)
        
        # create task assignees
        task.assignees = [assignee.pk for assignee in assignees]
        # transaction.savepoint_rollback(sid)

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


    class Meta:
        model = Task
        fields = ('id','name', 'reporter', 'assignees', 'subscribers', 'attachments',
                 'category', 'department',  'description', 'due_date', 'complete_time', 
                 'status', 'access_level', 'priority', 'created_date', 
                 'modified_date', 'is_complete')
        read_only_fields = ('id', 'created_date', 'modified_date', 'complete_time')

    # def create(self, validated_data):
    #     print(validated_data)
    #     return

    def get_status(self,obj):
        return obj.get_status_display()

    def get_access_level(self, obj):
        return obj.get_access_level_display()
    
    def get_priority(self, obj):
        return obj.get_priority_display()