from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from mfa.api import serializers as mfa_serializers
from mfa import models as mfa_models


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
