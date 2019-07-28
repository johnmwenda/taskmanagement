from django.shortcuts import render
from django.contrib.auth import login as django_login, logout as django_logout

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from rest_framework.authtoken.models import Token

from .serializers import UserSignInSerializer, UserSerializer, UserSignupSerializer

# Create your views here.
class UserSignInView(APIView):
    serializer_class = UserSignInSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        django_login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key,
                        'user': UserSerializer(user, context={'request': request}).data},
                        status=status.HTTP_200_OK)

class UserSignUpView(APIView):
    serializer_class = UserSignupSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
        return Response(
            data={"message": "User successfully registered."}, 
            status=status.HTTP_201_CREATED
            )

    def perform_create(self, serializer):
        serializer.save()


class UserSignoutView(APIView):
    authentication_classes = (TokenAuthentication, )

    def get(self, request):
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)