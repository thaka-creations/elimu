# Generated by Django 4.0.4 on 2022-06-04 12:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0002_unitamount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceunit',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='invoice_unit_set', to='payments.invoice'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('EXPIRED', 'EXPIRED'), ('REVOKED', 'REVOKED')], max_length=255)),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_subcriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='invoiceunit',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='invoiceunits', to='payments.subscription'),
        ),
    ]
