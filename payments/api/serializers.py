from rest_framework import serializers
from phonenumbers.phonenumberutil import is_possible_number
from phonenumber_field.phonenumber import to_python
from school.models import UnitModel
from payments import models
from school.api.serializers import ListRetrieveUnitSerializer

ALLOWED_PERIOD_TYPE = [
    ("DAY", "DAY"),
    ("MONTH", "MONTH"),
    ("DAYS", "DAYS"),
    ("YEAR", "YEAR"),
    ("YEARS", "YEARS"),
    ("MONTHS", "MONTHS")
]


class BaseSerializer(serializers.Serializer):
    request_id = serializers.UUIDField(required=True)


class UnitAmountSerializer(serializers.ModelSerializer):
    unit = ListRetrieveUnitSerializer(many=False)

    class Meta:
        model = models.UnitAmount
        fields = "__all__"


class CreateUnitAmountSerializer(serializers.Serializer):
    unit = serializers.UUIDField(required=True)
    amount = serializers.FloatField(required=True)
    period = serializers.IntegerField(required=True)
    period_type = serializers.ChoiceField(required=True, choices=ALLOWED_PERIOD_TYPE)

    def validate(self, obj):
        try:
            unit = UnitModel.objects.get(id=obj['unit'])
        except UnitModel.DoesNotExist:
            raise serializers.ValidationError("Unit does not exist")

        obj.update({"unit": unit})

        instance = models.UnitAmount.objects.filter(unit=unit, period=obj['period'])
        if instance.exists():
            raise serializers.ValidationError("Unit amount for selected period exists. "
                                              "Use update unit amount to update details")
        return obj


class UpdateAmountSerializer(serializers.Serializer):
    request_id = serializers.UUIDField(required=True)
    amount = serializers.FloatField(required=True)

    def validate(self, obj):
        try:
            inst = models.UnitAmount.objects.get(id=obj['request_id'])
        except models.UnitAmount.DoesNotExist:
            raise serializers.ValidationError("Invalid unit amount")

        obj['request_id'] = inst
        return obj


class ListSubscription(serializers.ModelSerializer):
    class Meta:
        model = models.Subscription
        fields = "__all__"


class MpesaCheckoutSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)
    reference = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    def validate(self, obj):
        phone = obj['phone_number']
        amount = obj['amount']

        if phone == "+":
            phone = phone[1:]
        if phone[0] == "0":
            phone = "254" + phone[1:]

        try:
            phone_number = to_python(phone, "KE")

            if phone_number and not is_possible_number(phone_number) or not phone_number.is_valid():
                raise serializers.ValidationError("Invalid phone number")
        except Exception:
            raise serializers.ValidationError("Invalid phone number")

        if amount <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")

        return obj


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = "__all__"
