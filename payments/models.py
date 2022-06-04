import uuid
from django.db import models
from users.models import User
from school.models import UnitModel

# Create your models here.
ALLOWED_STATUS = [
    ("PENDING", "PENDING"),
    ("APPROVED", "APPROVED"),
    ("REVOKED", "REVOKED"),
    ("CANCELLED", "CANCELLED")
]

ALLOWED_PERIOD = [
    ("1 MONTH", "1 MONTH"),
    ("3 MONTHS", "3 MONTHS"),
    ("6 MONTHS", "6 MONTHS"),
    ("1 YEAR", "1 YEAR")
]


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class UnitAmount(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey(UnitModel, on_delete=models.CASCADE, related_name="unit_amounts")
    period = models.CharField(max_length=255, choices=ALLOWED_PERIOD, default="1 MONTH")
    amount = models.DecimalField(max_digits=19, decimal_places=2)


class Invoice(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="invoices")
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    mpesa_ref = models.CharField(max_length=255, blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=255, choices=ALLOWED_STATUS, default="PENDING")


class InvoiceUnit(BaseModel):
    unit = models.ForeignKey(UnitModel, on_delete=models.DO_NOTHING, related_name="invoice_units")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoice_unit_set")
