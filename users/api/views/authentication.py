from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.models import get_application_model
from users.api import serializers
from users.utils import services, oauth_utils

klass = oauth_utils.ApplicationUser()


class AuthenticationViewSet(viewsets.ViewSet):

    @action(
        methods=["POST"],
        detail=False,
        url_name="login",
        url_path="login"
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

        dt = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": instance.client_id,
            "client_secret": instance.client_secret
        }

        resp = services.get_client_details(dt)

        if not resp:
            return Response({"details": "Invalid client details"}, status=status.HTTP_400_BAD_REQUEST)

        userinfo = {
            "access_token": resp["access_token"],
            "expires_in": resp["expires_in"],
            "token_type": resp["token_type"],
            "refresh_token": resp["refresh_token"],
            "jwt_token": klass.generate_jwt_token(user)
        }

        return Response({"details": userinfo}, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        url_name="reset-password",
        url_path="reset-password"
    )
    def reset_password(self, request):
        pass
