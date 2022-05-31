from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import Group
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users import models as user_models
from users.utils import oauth_utils
from mfa.utils import two_factor
from users.api import serializers

oauth2_user = oauth_utils.ApplicationUser()


class RegistrationViewSet(viewsets.ViewSet):

    @action(
        methods=['POST'],
        detail=False,
        url_name='validate-email',
        url_path='validate-email'
    )
    def validate_email(self, request):
        serializer = serializers.EmailSerializer(data=request.data, many=False)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        klass = two_factor.MultiFactorAuthentication()
        message = klass.generate_otp_code(
            send_to=validated_data['email'], expiry_time=settings.REGISTRATION_OTP_EXPIRY_TIME)

        return Response({"details": message}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_name='registration-by-email',
        url_path='registration-by-email'
    )
    def registration_by_email(self, request):
        payload = request.data
        payload_serializer = serializers.RegisterByEmailSerializer(
            data=payload, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data

        first_name = validated_data['first_name'].upper()
        last_name = validated_data['last_name'].upper()
        middle_name = validated_data['middle_name']
        other_name = middle_name.upper() if middle_name else None
        email = validated_data['email']

        with transaction.atomic():
            user = user_models.User.objects.create(
                username=email
            )

            user_models.PublicUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=other_name,
                email=email,
                is_email_verified=True,
                user=user
            )

        return Response({"details": {"User created.Proceed to set password"}}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_name='set-password',
        url_path='set-password'
    )
    def set_password(self, request):
        payload = request.data
        payload_serializer = serializers.PasswordSerializer(
            data=payload, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        password = validated_data['password']
        user = validated_data['user']

        if not user.is_password_verified:

            with transaction.atomic():
                user.set_password(password)  # hash password
                user.is_password_verified = True
                # user.password_update = timezone.now()

                # user role
                # public_group = Group.objects.get(name='PUBLIC')
                # user.groups.add(public_group)
                user.account_status = "ACTIVE"
                user.public_user.profile_status = "ACTIVE"
                user.save()

                # create application user
                oauth2_user.create_application_user(user)

        return Response({"details": "Proceed to login"}, status=status.HTTP_200_OK)