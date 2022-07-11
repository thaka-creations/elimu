from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from mfa.api import serializers as mfa_serializers
from mfa.utils import two_factor
from mfa import models as mfa_models
from staff import util

service_manager = util.ServiceManager()
klass = two_factor.MultiFactorAuthentication()


class OtpViewSet(viewsets.ViewSet):

    @action(
        methods=['POST'],
        detail=False,
        url_name='generate',
        url_path='generate'
    )
    def generate_otp_code(self, request):
        payload_serializer = mfa_serializers.CreateOtpSerializer(
            data=request.data, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        send_to = validated_data['send_to']
        expiry_time = int(validated_data['expiry_time'])
        generation_time = timezone.now()
        expiry_date = generation_time + timedelta(seconds=expiry_time)
        otp_code = klass.generate_otp_code(send_to, expiry_time)

        with transaction.atomic():
            otp_instance = mfa_models.OtpCode.objects.create(
                code=otp_code,
                send_to=send_to,
                expiry_date=expiry_date
            )
            service_manager.send_email(
                subject="TAFA OTP CODE",
                message="Your otp code is %s" % otp_code['code'],
                recipient=send_to
            )
            # serializer = mfa_serializers.OtpSerializer(otp_instance, many=False)
            return Response({"otp": otp_code['code']}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_name='verify',
        url_path='verify'
    )
    def verify_otp_code(self, request):
        payload_serializer = mfa_serializers.VerifyOtpSerializer(
            data=request.data, many=False
        )

        if not payload_serializer.is_valid():
            return Response({"details": payload_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = payload_serializer.validated_data
        otp = validated_data['otp']
        send_to = validated_data['send_to']
        valid, message = klass.verify_otp_code(otp, send_to)

        if not valid:
            return Response({"details": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"details": message}, status=status.HTTP_200_OK)
