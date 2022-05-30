from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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



