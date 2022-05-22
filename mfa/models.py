import uuid
from django.db import models

# Create your models here.
OTP_STATUS = [("PENDING", "PENDING"), ("REVOKED", "REVOKED")]


class OtpCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    send_to = models.CharField(max_length=500)
    code = models.CharField(max_length=500, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=255, choices=OTP_STATUS, default="PENDING")

    def __str__(self):
        return self.code