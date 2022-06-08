import json
from datetime import datetime
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from payments import models as payment_models
from payments.api import serializers as payment_serializers
from payments.utils import mpesa

gateway = mpesa.MpesaGateway()


class UnitAmountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = payment_models.UnitAmount.objects.all()
    serializer_class = payment_serializers.UnitAmountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        form = self.request.query_params.get("form", False)
        subject = self.request.query_params.get("subject", False)

        if not form or not subject:
            return super().get_queryset()
        else:
            qs = payment_models.UnitAmount.objects.filter(unit__form__id=form, unit__subject__id=subject)
            return qs

    def create(self, request):
        serializer = payment_serializers.CreateUnitAmountSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        with transaction.atomic():
            payment_models.UnitAmount.objects.create(**validated_data)
            return Response({"details": "Unit amount updated successfully"}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def update_amount(self, request):
        serializer = payment_serializers.UpdateAmountSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        inst = validated_data['request_id']
        inst.amount = validated_data['amount']
        inst.save()
        return Response({"details": "Unit amount updated successfully"}, status=status.HTTP_200_OK)


class InvoiceViewSet(viewsets.ViewSet):

    def create(self, request):
        pass


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = payment_models.Subscription.objects.all()
    serializer_class = payment_serializers.ListSubscription
    permission_classes = [IsAuthenticated]

    @action(methods=['GET'], detail=False, url_name="check-status", url_path="check-status")
    def check_status(self, request):
        # active subscriptions
        qs = payment_models.Subscription.objects.filter(user=request.user, status="ACTIVE")
        if not qs.exists():
            return Response({"details": "Not subscribed"}, status=status.HTTP_400_BAD_REQUEST)

        # revoke if subscription has expired
        expired_subscriptions = qs.filter(expiry_date__lt=datetime.now())
        if expired_subscriptions.exists():
            expired_subscriptions.update(status="EXPIRED")
            expired_ids = [i.id for i in expired_subscriptions]
            qs = qs.exclude(id__in=expired_ids)

            if not qs.exists():
                return Response({"details": "Not subscribed"}, status=status.HTTP_400_BAD_REQUEST)

        # check if user has subscribed to unit
        serializer = payment_serializers.BaseSerializer(data=request.query_params.dict(), many=False)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        is_valid = payment_models.InvoiceUnit.objects.filter(unit__id=validated_data['request_id'],
                                                             subscription__in=qs).exists()

        if not is_valid:
            return Response({"details": "Not subscribed"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"details": "Subscribed"}, status=status.HTTP_200_OK)


class MpesaCheckout(APIView):

    def post(self, request):
        serializer = payment_serializers.MpesaCheckoutSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        amount = validated_data['amount']
        phone_number = validated_data['phone_number']
        res = gateway.stk_push_request(amount, phone_number)
        return Response(res, status=status.HTTP_200_OK)


class MpesaCallBack(APIView):

    def post(self, request):
        print(request.body)
        return Response(True)
