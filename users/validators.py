from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from users import models as user_models


def validate_password(value):
    pass


def validate_email(value):
    qs = user_models.User.objects.filter(username=value)

    if qs.exists():
        raise ValidationError(_("%(value)s exists"), params={"value": value},)
