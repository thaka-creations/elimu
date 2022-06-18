from django.db import models


# Create your models here.
class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class RegistrationCodes(BaseModel):
    id_no = models.CharField(max_length=255, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, null=True, unique=True)
    users = models.BigIntegerField(default=0)

    def __str__(self):
        return self.code
