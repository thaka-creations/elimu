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
    country_code = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    postal_address = models.CharField(max_length=255, blank=True, null=True)
    physical_address = models.CharField(max_length=255, blank=True, null=True)
    profile_status = models.CharField(max_length=255, choices=ACCEPTED_STATUS, default="REGISTRATION")
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_password_verified = models.BooleanField(default=False)

    def __str__(self):
        middle_name = self.middle_name
        return "%s %s %s" % (self.first_name, middle_name if middle_name else "", self.last_name)

    class Meta:
        abstract = True


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True, db_index=True)
    account_status = models.CharField(max_length=255, choices=ACCEPTED_STATUS, default="REGISTRATION")
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

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

    class Meta:
        unique_together = ['country_code', 'phone_number']
        verbose_name_plural = 'staff'


class PublicUser(ProfileMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="public_user")

    class Meta:
        unique_together = ['country_code', 'phone_number']
        verbose_name_plural = 'publicuser'
