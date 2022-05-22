from django.core.validators import RegexValidator
from rest_framework import serializers
from users import models


class NameSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, trim_whitespace=True)
    middle_name = serializers.CharField(allow_blank=True, allow_null=True, trim_whitespace=True)
    last_name = serializers.CharField(required=True, trim_whitespace=True)


class PhoneNumberSerializer(serializers.Serializer):
    country_code = serializers.CharField(required=True)
    phone_number = serializers.CharField(
        required=True, max_length=10, min_length=10,
        validators=[RegexValidator(r'^\d{0,10}$', 'Kindly add valid number')],
        error_messages={
            "invalid": "Kindly add valid number",
            "min_length": "Should be at least 10 numbers",
            "max_length": "Should be at most 10 numbers",
        }
    )


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class RegisterByEmailSerializer(NameSerializer, EmailSerializer):
    email_otp = serializers.CharField(required=True)

    def validate(self, obj):
        # validate otp if valid
        email = obj['email']
        otp = obj['email_otp']

        user_exists = models.PublicUser.objects.filter(
            email=email, profile_status__iexact='ACTIVE', email_verified=True
        ).exists()

        if user_exists:
            raise serializers.ValidationError("User with email record exists")

        otp_status, message = services_responses.verify_otp_code({'otp': otp, 'send_to': email})

        if not otp_status:
            raise serializers.ValidationError(message)

        return obj


class RegisterByPhoneNumberSerializer(NameSerializer, PhoneNumberSerializer):
    phone_otp = serializers.CharField(required=True)

    def validate(self, obj):
        # validate otp if valid
        otp = obj['phone_otp']
        phone_number = obj['phone_number']
        country_code = obj['country_code']

        phone = phone_functions.phone_number_format(country_code, phone_number)

        if not phone:
            raise serializers.ValidationError("Invalid phone number")

        user_exists = models.PublicUser.objects.filter(
            phone_number=phone_number, country_code=country_code, profile_status__iexact='ACTIVE',
            phone_verified=True
        ).exists()

        if user_exists:
            raise serializers.ValidationError("User with phone record exists")

        otp_status, message = services_responses.verify_otp_code({'otp': otp, 'send_to': phone})

        if not otp_status:
            raise serializers.ValidationError(message)

        return obj


class PasswordSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, obj):
        # user exists
        user_id = obj['user_id']
        password = obj['password']
        confirm_password = obj['confirm_password']

        try:
            user = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords don't match")

        obj.update({"user_id": user})
        return obj
