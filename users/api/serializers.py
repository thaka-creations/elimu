from rest_framework import serializers
from users import models as user_models
from staff.models import RegistrationCodes


class BaseSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, trim_whitespace=True)
    password = serializers.CharField(required=True, trim_whitespace=True)
    confirm_password = serializers.CharField(required=True, trim_whitespace=True)
    code = serializers.CharField(required=True, trim_whitespace=True)
    school = serializers.CharField(required=True, trim_whitespace=True)
    county = serializers.UUIDField(required=True)

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

        try:
            code = user_models.Agent.objects.get(code=obj['code'])
        except user_models.Agent.DoesNotExist:
            raise serializers.ValidationError("Invalid code")

        try:
            county = user_models.County.objects.get(id=obj['county'])
        except user_models.County.DoesNotExist:
            raise serializers.ValidationError("County does not exist")

        obj.update({"code": code, "county": county})

        return obj


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, trim_whitespace=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = ["id", "username", "name", "account_status"]


class ListCodes(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()

    class Meta:
        model = user_models.Agent
        fields = ['id', 'code', 'name', 'users']

    @staticmethod
    def get_name(obj):
        return obj.user.name

    @staticmethod
    def get_users(obj):
        return obj.subscribers.count()


class ListCounties(serializers.ModelSerializer):
    class Meta:
        model = user_models.County
        fields = ["id", "name"]
