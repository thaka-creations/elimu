from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.models import get_application_model
from users.api import serializers


class AuthenticationViewSet(viewsets.ViewSet):

    @action(
        methods=["POST"],
        detail=False,
        url_name="system-login",
        url_path="system-login"
    )
    def login(self, request):
        serializer = serializers.SystemLoginSerializer(
            data=request.data, many=False
        )

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        username = validated_data['username']
        password = validated_data['password']

        user = authenticate(username=username, password=password)

        if not user:
            return Response({"details": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = get_application_model().objects.get(user=user)
        except Exception as e:
            print(e)
            return Response({"details": "Failed to login. Try again later"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": instance.client_id,
            "client_secret": instance.client_secret
        }






