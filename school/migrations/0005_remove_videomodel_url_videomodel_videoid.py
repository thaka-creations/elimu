# Generated by Django 4.0.4 on 2022-06-07 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0004_alter_unitmodel_form'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videomodel',
            name='url',
        ),
        migrations.AddField(
            model_name='videomodel',
            name='videoid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
