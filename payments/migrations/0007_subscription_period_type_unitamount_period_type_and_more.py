# Generated by Django 4.0.4 on 2022-06-09 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_transaction_receipt_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='period_type',
            field=models.CharField(blank=True, choices=[('DAY', 'DAY'), ('MONTH', 'MONTH'), ('DAYS', 'DAYS'), ('YEAR', 'YEAR'), ('YEARS', 'YEARS'), ('MONTHS', 'MONTHS')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='unitamount',
            name='period_type',
            field=models.CharField(choices=[('DAY', 'DAY'), ('MONTH', 'MONTH'), ('DAYS', 'DAYS'), ('YEAR', 'YEAR'), ('YEARS', 'YEARS'), ('MONTHS', 'MONTHS')], default='MONTH', max_length=100),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='period',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='unitamount',
            name='period',
            field=models.IntegerField(default=1),
        ),
    ]
