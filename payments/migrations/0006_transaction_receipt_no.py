# Generated by Django 4.0.4 on 2022-06-08 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='receipt_no',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]