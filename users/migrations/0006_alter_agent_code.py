# Generated by Django 4.0.4 on 2022-07-08 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_status_agent_profile_status_remove_user_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]