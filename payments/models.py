import uuid
from django.db import models
from users.models import User
from school.models import UnitModel
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
ALLOWED_STATUS = [
    ("PENDING", "PENDING"),
    ("APPROVED", "APPROVED"),
    ("REVOKED", "REVOKED"),
    ("CANCELLED", "CANCELLED")
]

ALLOWED_PERIOD = [
    ("1 MONTH", 30),
    ("3 MONTHS", 90),
    ("6 MONTHS", 180),
    ("1 YEAR", 365)
]

SUBSCRIPTION_STATUS = [
    ("ACTIVE", "ACTIVE"),
    ("EXPIRED", "EXPIRED"),
    ("REVOKED", "REVOKED")
]

STATUS = [
    ("PENDING", "PENDING"),
    ("COMPLETE", "COMPLETE")
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
    period = models.IntegerField(choices=ALLOWED_PERIOD, default=30)
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


class Subscription(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_subcriptions")
    status = models.CharField(max_length=255, choices=SUBSCRIPTION_STATUS)
    period = models.IntegerField(blank=True, null=True, choices=ALLOWED_PERIOD)
    expiry_date = models.DateTimeField(blank=True, null=True)


class InvoiceUnit(BaseModel):
    unit = models.ForeignKey(UnitModel, on_delete=models.DO_NOTHING, related_name="invoice_units")
    invoice = models.ForeignKey(Invoice, on_delete=models.DO_NOTHING, related_name="invoice_unit_set")
    subscription = models.ForeignKey(Subscription, on_delete=models.DO_NOTHING, related_name="invoiceunits",
                                     blank=True, null=True)


class Transaction(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = PhoneNumberField(blank=False, null=False)
    checkout_id = models.CharField(max_length=255)
    receipt_no = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=100, choices=STATUS, default="PENDING")
    invoices = models.ManyToManyField(Invoice, related_name="transactions")

    def __str__(self):
        return self.reference
