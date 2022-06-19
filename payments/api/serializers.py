from rest_framework import serializers
from phonenumbers.phonenumberutil import is_possible_number
from phonenumber_field.phonenumber import to_python
from school.models import UnitModel
from users.models import User
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
    period = serializers.SerializerMethodField()

    class Meta:
        model = models.UnitAmount
        fields = "__all__"

    @staticmethod
    def get_period(obj):
        return str(obj.period) + " " + obj.period_type


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
    unit = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    subject = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user = serializers.UUIDField(required=True)

    def validate(self, obj):
        phone = obj['phone_number']
        amount = obj['amount']
        user = obj['user']

        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        try:
            if "unit" in obj.keys():
                instance = models.UnitAmount.objects.get(unit__id=obj['unit'], amount=amount)
                obj.update({"unit": instance.unit})
            elif "subject" in obj.keys() and "form" in obj.keys():
                instance = models.SubjectAmount.objects.get(subject__id=obj['subject'], form__id=obj['form'],
                                                            amount=amount)
            else:
                instance = models.FormAmount.objects.get(form__id=obj['form'], amount=amount)
        except Exception as e:
            print(e)
            raise serializers.ValidationError("An error occurred. Try again later")

        period = str(instance.period) + ' ' + instance.period_type

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

        _period_list = period.split(" ")

        if len(_period_list) < 2 or len(_period_list) > 2:
            raise serializers.ValidationError("Invalid period")

        if _period_list[1] in ["MONTH", "MONTHS"]:
            period = int(_period_list[0]) * 30
        elif _period_list[1] in ["YEAR", "YEARS"]:
            period = int(_period_list[0]) * 365
        else:
            period = int(_period_list[0])

        obj.update({"period": period, "user": user, "phone_number": str(phone_number)[1:]})
        return obj


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = "__all__"


class CheckSubjectSubscriptionSerializer(serializers.Serializer):
    form = serializers.UUIDField(required=True)
    subject = serializers.UUIDField(required=True)


class CheckFormSubscriptionSerializer(serializers.Serializer):
    form = serializers.UUIDField(required=True)
