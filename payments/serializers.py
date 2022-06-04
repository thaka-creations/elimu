from rest_framework import serializers
from school.models import UnitModel
from payments import models
from school.api.serializers import ListRetrieveUnitSerializer

ALLOWED_PERIOD = [
    ("1 MONTH", "1 MONTH"),
    ("3 MONTHS", "3 MONTHS"),
    ("6 MONTHS", "6 MONTHS"),
    ("1 YEAR", "1 YEAR")
]


class UnitAmountSerializer(serializers.ModelSerializer):
    unit = ListRetrieveUnitSerializer(many=False)

    class Meta:
        model = models.UnitAmount
        fields = "__all__"


class CreateUnitAmountSerializer(serializers.Serializer):
    unit = serializers.UUIDField(required=True)
    amount = serializers.FloatField(required=True)
    period = serializers.ChoiceField(required=True, choices=ALLOWED_PERIOD)

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


