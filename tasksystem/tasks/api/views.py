from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from tasksystem.tasks.models import Task
from tasksystem.tasks.api.serializers import (
    TaskViewSerializer,
    TaskCreatingSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    '''
    API Endpoint for task objects
    '''
    serializer_class = TaskViewSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        '''
        Determine queryset by checking type of user logged in (Supervisor or Junior)  
        '''
        user = self.request.user
        queryset = []
        if self.request.user.is_manager:
            queryset = Task.supervisor_objects.tasks(user)
        elif user.is_member:
            queryset = Task.junior_objects.tasks(user)
        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return TaskCreatingSerializer
        return TaskViewSerializer

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
