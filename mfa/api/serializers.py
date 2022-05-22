from rest_framework import serializers
from mfa import models as mfa_models


class CreateOtpSerializer(serializers.Serializer):
    send_to = serializers.CharField(required=True)
    expiry_time = serializers.CharField(required=True)


class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = mfa_models.OtpCode
        fields = ['id', 'send_to', 'code', 'date_created', 'expiry_date']


class VerifyOtpSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    send_to = serializers.CharField(required=True)