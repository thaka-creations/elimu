from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from users import models as user_models


def validate_password(value):
    pass


def validate_county(value):
    try:
        user_models.County.objects.get(id=value)
    except user_models.County.DoesNotExist:
        raise ValidationError(_("%(value)s does not exists"), params={"value": value}, )
