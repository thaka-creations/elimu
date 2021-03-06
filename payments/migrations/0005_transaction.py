# Generated by Django 4.0.4 on 2022-06-08 17:38

from django.db import migrations, models
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_subscription_period_alter_unitamount_period'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('checkout_id', models.CharField(max_length=255)),
                ('reference', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('COMPLETE', 'COMPLETE')], default='PENDING', max_length=100)),
                ('invoices', models.ManyToManyField(related_name='transactions', to='payments.invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
