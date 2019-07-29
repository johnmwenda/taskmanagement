
from rest_framework import serializers

from tasksystem.departments.models import Category, Department 

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id')

class CategorySlimSerializer(serializers.ModelSerializer):
    ''' Serializer used for read only drop downs '''
    class Meta:
        model = Category
        exclude = ('department')
        read_only_fields = ('id', 'department', 'name')


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ('id')

class DepartmentSlimSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id', 'name')
        read_only_fields = ('id', 'name')