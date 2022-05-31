from rest_framework import serializers
from users import models as user_models


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, trim_whitespace=True)
    password = serializers.CharField(required=True, trim_whitespace=True)
    confirm_password = serializers.CharField(required=True, trim_whitespace=True)

    def validate(self, obj):
        password = obj['password']
        password2 = obj['confirm_password']
        name = obj['name'].split(" ")
        email = obj['email']

        # validate email
        qs = user_models.User.objects.filter(username=email)

        if qs.exists():
            raise serializers.ValidationError("User with email already exists")

        # validate name
        if len(name) == 1:
            raise serializers.ValidationError("Enter fullname")

        # validate password
        if password != password2:
            raise serializers.ValidationError("Password do not match")

        return obj


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, trim_whitespace=True)



