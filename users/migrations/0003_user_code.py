# Generated by Django 4.0.4 on 2022-06-18 07:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_alter_registrationcodes_users'),
        ('users', '0002_county_user_school_user_county'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='code_users', to='staff.registrationcodes'),
        ),
    ]
