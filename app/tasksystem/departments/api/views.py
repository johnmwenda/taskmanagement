from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from tasksystem.departments.models import Department, Category
from tasksystem.departments.api.serializers import (
    DepartmentSerializer,
    CategorySerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    '''
    API Endpoint for department operations
    '''
    queryset = Department.objects.all().prefetch_related('category_set')
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=["GET"])
    def categories(self, request, pk=None):
        department = self.get_object()
        categories = department.category_set.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=200)

    @action(detail=True, methods=["POST"])
    def category(self, request, pk=None):
        department = self.get_object()
        data = request.data
        data["department"] = department.id
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
