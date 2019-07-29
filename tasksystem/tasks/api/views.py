from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from tasksystem.tasks.models import Task
from tasksystem.tasks.api.serializers import (
        TaskViewSerializer,
        TaskCreatingSerializer,
    )

from rest_framework import permissions


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskViewSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return TaskCreatingSerializer
        return TaskViewSerializer

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
