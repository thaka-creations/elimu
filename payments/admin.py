from django.contrib import admin
from payments.models import Transaction, Subscription, InvoiceUnit, Invoice
# Register your models here.

admin.site.register(Transaction)
admin.site.register(Subscription)
admin.site.register(InvoiceUnit)
admin.site.register(Invoice)
