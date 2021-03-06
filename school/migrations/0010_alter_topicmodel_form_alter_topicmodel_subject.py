# Generated by Django 4.0.4 on 2022-07-15 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0009_remove_unitmodel_form_remove_unitmodel_subject_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicmodel',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_topics', to='school.formmodel'),
        ),
        migrations.AlterField(
            model_name='topicmodel',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_topics', to='school.subjectmodel'),
        ),
    ]
