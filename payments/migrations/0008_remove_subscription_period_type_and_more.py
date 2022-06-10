# Generated by Django 4.0.4 on 2022-06-10 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_subscription_period_type_unitamount_period_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='period_type',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='invoices',
        ),
        migrations.AddField(
            model_name='invoice',
            name='paid_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='invoice',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='transaction', to='payments.invoice'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('PAID', 'PAID'), ('REVOKED', 'REVOKED'), ('CANCELLED', 'CANCELLED'), ('OVERPAYMENT', 'OVERPAYMENT'), ('PARTIAL_PAYMENT', 'PARTIAL_PAYMENT')], default='PENDING', max_length=255),
        ),
    ]