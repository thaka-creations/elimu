import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager

# Create your models here.
ACCEPTED_STATUS = [
    ("ACTIVE", "ACTIVE"),
    ("SUSPENDED", "SUSPENDED"),
    ("DEACTIVATED", "DEACTIVATED"),
    ("REGISTRATION", "REGISTRATION")
]


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class ProfileMixin(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    postal_address = models.CharField(max_length=255, blank=True, null=True)
    physical_address = models.CharField(max_length=255, blank=True, null=True)
    profile_status = models.CharField(max_length=255, choices=ACCEPTED_STATUS, default="REGISTRATION")

    def __str__(self):
        middle_name = self.middle_name
        return "%s %s %s" % (self.first_name, middle_name if middle_name else "", self.last_name)

    class Meta:
        abstract = True


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    account_status = models.CharField(max_length=255, choices=ACCEPTED_STATUS, default="REGISTRATION")

    objects = UserManager()
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Staff(ProfileMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_user")
    employee_num = models.CharField(max_length=255, blank=True, null=True)


class PublicUser(ProfileMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="public_user")
