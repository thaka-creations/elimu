import json
from datetime import datetime
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from school import models as school_models
from payments import models as payment_models
from payments.api import serializers as payment_serializers
from payments.utils import mpesa

gateway = mpesa.MpesaGateway()


class UnitAmountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = payment_models.UnitAmount.objects.all()
    serializer_class = payment_serializers.UnitAmountSerializer

    def get_queryset(self):
        form = self.request.query_params.get("form", False)
        subject = self.request.query_params.get("subject", False)
        unit = self.request.query_params.get("unit", False)

        if unit:
            qs = payment_models.UnitAmount.objects.filter(unit__id=unit)
        elif not form or not subject:
            return payment_models.UnitAmount.objects.none()
        else:
            qs = payment_models.UnitAmount.objects.filter(unit__form__id=form, unit__subject__id=subject)
        return qs

    def create(self, request):
        serializer = payment_serializers.CreateUnitAmountSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        with transaction.atomic():
            print(validated_data["period"])
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

    @action(
        methods=["GET"],
        detail=False,
        url_path="check-subject-subscription"
    )
    def check_subject_subscription(self, request):
        serializer = payment_serializers.CheckSubjectSubscriptionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        try:
            subject = school_models.SubjectModel.objects.get(id=validated_data['subject'])
        except school_models.SubjectModel.DoesNotExist:
            return Response({"details": "Subject does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            form = school_models.FormModel.objects.get(id=validated_data['form'])
        except school_models.FormModel.DoesNotExist:
            return Response({"details": "Form does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        units = school_models.UnitModel.objects.filter(subject=subject, form=form).values_list("id", flat=True)

        if not units:
            return Response({"details": "Subject does not have units"}, status=status.HTTP_400_BAD_REQUEST)

        qs = payment_models.Subscription.objects.filter(
            user=request.user, status="ACTIVE", invoiceunits__unit_id__in=units
        )
        if not qs.exists():
            return Response({"details": "Not subscribed for subject"}, status=status.HTTP_400_BAD_REQUEST)

        if qs.count() != len(units):
            return Response({"details": "Not subscribed for subject"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"details": "Subscribed to view subject"}, status=status.HTTP_200_OK)


class MpesaCheckout(APIView):

    def post(self, request):
        serializer = payment_serializers.MpesaCheckoutSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        amount = validated_data['amount']
        phone_number = validated_data['phone_number']
        period = validated_data['period']
        unit = validated_data['unit']
        user = validated_data['user']
        form = validated_data['form']
        subject = validated_data['subject']

        if not unit or not form or not subject:
            return Response({"details": "Unit or form or subject required"}, status=status.HTTP_400_BAD_REQUEST)
        resp = gateway.stk_push_request(amount, phone_number, unit, form, subject, period, user)

        if not resp:
            return Response({"details": "An error occurred. Try again later"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"details": "Payment process initiated successfully"}, status=status.HTTP_200_OK)


class MpesaCallBack(APIView):

    def get(self, request):
        return Response({"status": "OK"}, status=200)

    def post(self, request):
        data = request.data
        res = gateway.callback(data)

        if res:
            return Response({"details": "Success"}, status=status.HTTP_200_OK)

        return Response({"details": "Failed"}, status=status.HTTP_400_BAD_REQUEST)
