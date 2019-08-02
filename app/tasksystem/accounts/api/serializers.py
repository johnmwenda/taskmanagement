from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.core import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth import password_validation

from tasksystem.departments.api.serializers import DepartmentSlimSerializer

User = get_user_model()
from tasksystem.tasks.models import Department

class BasicUserSerializer(serializers.ModelSerializer):
    """User serializer to be used in model relations."""
    url = serializers.HyperlinkedIdentityField(view_name='tasks-detail')
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=False, required=True)
    last_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=False, required=True)

    class Meta:
        fields = ('id','url','email','first_name', 'last_name')
        model = User


class UserSignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not registered. Please sign up first")

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            if not user:
                raise serializers.ValidationError("Invalid email/password combination")
        else:
            raise serializers.ValidationError('Make sure you include "username" and "password".')
        
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            validators=[UniqueValidator(queryset=User.objects.all(),
            message='A user with this email address exists')])
    first_name = serializers.CharField(
                    max_length=30, allow_null=False, allow_blank=False, required=True)
    last_name = serializers.CharField(
                    max_length=30, allow_null=False, allow_blank=False, required=True)
    department = DepartmentSlimSerializer(read_only=True)
    
    class Meta:
        model=User
        fields=('pk', 'email', 'first_name', 'last_name', 'is_active', 'is_member', 
                    'is_manager', 'is_staff', 'is_superuser', 'department')


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='A user with this email address exists')] )
    first_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=True, required=True)
    last_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=True, required=True)
    password = serializers.CharField(required=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), 
                 allow_null=True, required=False)
    is_member = serializers.BooleanField()
    is_manager = serializers.BooleanField()
    is_staff = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'department', 'is_member', 'is_manager', 'is_staff')

    def validate(self, attrs):
        # valid/strong password checks
        errors = {}
        try:
            password_validation.validate_password(password=attrs.get('password'), user=User)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data.pop('email'),
            password=validated_data.pop('password'),
            **validated_data)
        return user