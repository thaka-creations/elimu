import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from users.utils.managers import UserManager
from staff.models import RegistrationCodes
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
ACCOUNT_STATUS = [
    ("ACTIVE", "ACTIVE"),
    ("DEACTIVATED", "DEACTIVATED"),
    ("SUSPENDED", "SUSPENDED"),
]


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class County(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.EmailField(unique=True)
    name = models.CharField(max_length=1000)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    account_status = models.CharField(max_length=255, choices=ACCOUNT_STATUS, default="ACTIVE")

    USERNAME_FIELD = "username"

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Agent(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agent_user")
    code = models.CharField(max_length=255, blank=True, null=True)
    profile_status = models.CharField(max_length=255, choices=ACCOUNT_STATUS, default="ACTIVE")
    subscribers = models.ManyToManyField(User, related_name="agent_subscribers", blank=True, null=True)

    def __str__(self):
        return self.code


class Staff(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_user")
    phone = PhoneNumberField(blank=False, null=False)
    employee_num = models.CharField(max_length=255, blank=True, null=True)
    profile_status = models.CharField(max_length=255, choices=ACCOUNT_STATUS, default="ACTIVE")


class PublicUser(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="public_user")
    school = models.CharField(max_length=1000, blank=True, null=True)
    county = models.ForeignKey(County, on_delete=models.DO_NOTHING, related_name="county_users", blank=True, null=True)
    profile_status = models.CharField(max_length=255, choices=ACCOUNT_STATUS, default="ACTIVE")
