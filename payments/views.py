from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from payments import serializers as payment_serializers, models as payment_models


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
