from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.api import serializers
from users import models as user_models
from users.utils import system_utils
from oauth2_provider.models import get_application_model

oauth2_user = system_utils.ApplicationUser()


class Registration(viewsets.ViewSet):

    @staticmethod
    def create(request):
        serializer = serializers.RegistrationSerializer(
            data=request.data, many=False
        )

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            validated_data = serializer.validated_data
            name = validated_data['name'].upper()
            email = validated_data['email']
            password = validated_data['password']

            user = user_models.User.objects.create(
                username=email,
                name=name
            )

            user.set_password(password)
            user.save()
            oauth2_user.create_application_user(user)

            return Response({"details": "Successfully registered"}, status=status.HTTP_200_OK)


class Authentication(viewsets.ViewSet):

    @action(
        methods=["POST"],
        detail=False,
        url_name="login",
        url_path="login"
    )
    def login(self, request):
        serializer = serializers.LoginSerializer(data=request.data, many=False)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        username = validated_data['email']
        password = validated_data['password']

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"details": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = get_application_model().objects.get(user=user)
        except get_application_model().DoesNotExist:
            return Response({"details": "Invalid client"}, status=status.HTTP_400_BAD_REQUEST)

        dt = {
            "grant_type": "password",
            "username": user.username,
            "password": password,
            "client_id": instance.client_id,
            "client_secret": instance.client_secret
        }

        print(dt)

        resp = oauth2_user.get_client_details(dt)

        if not resp:
            return Response({"details": "Invalid client"}, status=status.HTTP_400_BAD_REQUEST)

        userinfo = {
            "access_token": resp['access_token'],
            "expires_in": resp['expires_in'],
            "token_type": resp['token_type'],
            "refresh_token": resp['refresh_token'],
            "jwt_token": oauth2_user.generate_jwt_token(user)
        }

        return Response({"details": userinfo}, status=status.HTTP_200_OK)
