# Generated by Django 4.0.4 on 2022-06-10 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0005_remove_videomodel_url_videomodel_videoid'),
    ]

    operations = [
        migrations.AddField(
            model_name='videomodel',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
