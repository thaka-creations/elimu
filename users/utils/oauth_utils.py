import jwt
import pytz
from datetime import timedelta, datetime
from django.db import transaction
from django.conf import settings
from oauth2_provider.generators import generate_client_id, generate_client_secret
from oauth2_provider.models import get_application_model
from rest_framework.exceptions import APIException


class ApplicationUser:

    @staticmethod
    def create_application_user(user):
        with transaction.atomic():
            username = user.username
            try:
                data = {
                    "client_id": generate_client_id(),
                    "client_secret": generate_client_secret(),
                    "client_type": "confidential",
                    "name": username,
                    "user": user,
                    "redirect_uris": "",
                    "authorization_grant_type": "password"
                }

                get_application_model().objects.create(**data)
            except Exception as e:
                raise APIException(e)

    @staticmethod
    def get_roles(user):
        user_roles = [role.name for role in user.groups.all()]
        return user_roles

    def generate_jwt_token(self, user):
        timezone = pytz.timezone(settings.TIME_ZONE)
        time = datetime.now(tz=timezone)
        access_token_expiry = time + timedelta(seconds=int(settings.ACCESS_TOKEN_EXPIRY))

        payload = {
            "user": str(user.id),
            "roles": self.get_roles(user),
            "exp": access_token_expiry,
            "iat": time,
            "aud": "urn:jst"
        }

        encoded = jwt.encode(payload, settings.TOKEN_SECRET_KEY, algorithm="HS512")
        return encoded


