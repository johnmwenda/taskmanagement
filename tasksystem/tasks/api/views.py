from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreatingSerializer
        return TaskViewSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # retrieve the old data before update
        old_data = {}
        for key in request.data.keys():
            old_data[key] = getattr(instance, key)

        # save new data
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
