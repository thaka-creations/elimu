from django.db import transaction
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from users.api import serializers
from users import models as user_models
from mfa.utils import two_factor


class RegistrationViewSet(viewsets.ViewSet):

    @action(
        methods=["POST"],
        detail=False,
        url_name="validate-email",
        url_path="validate-email"
    )
    def validate_email(self, request):
        serializer = serializers.EmailSerializer(data=request.data, many=False)

        if not serializer.validated_data:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        klass = two_factor.MultiFactorAuthentication()
        message = klass.generate_otp_code(
            send_to=validated_data['email'], expiry_time=settings.REGISTRATION_OTP_EXPIRY_TIME)

        return Response({"details": message}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_name="registration",
        url_path="registration"
    )
    def registration_by_email(self, request):
        serializer = serializers.RegisterByEmailSerializer(
            data=request.data, many=False
        )

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        first_name = validated_data['first_name'].upper()
        middle_name = validated_data['middle_name']
        middle_name = middle_name.upper() if middle_name else ""
        last_name = validated_data['last_name'].upper()
        email = validated_data['email']

        with transaction.atomic():
            instance = user_models.User.objects.create(
                username=email
            )

            # create user profile
            user_models.PublicUser.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                email=email,
                user=instance,
                is_email_verified=True
            )

            return Response({"details": "User created successfully"},
                            status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_name='set-password',
        url_path='set-password'
    )
    def set_password(self, request):
        serializer = serializers.PasswordSerializer(data=request.data, many=False)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        user = validated_data['user_id']
        password = validated_data['password']

        user.set_password(password)
        user.is_password_verified = True
        user.account_status = "ACTIVE"
        user.save()

        public_profile = user.public_user
        public_profile.profile_status = "ACTIVE"
        public_profile.is_password_verified = True
        public_profile.save()

        return Response({"details": "Password set successfully"}, status=status.HTTP_200_OK)
