# Generated by Django 4.0.4 on 2022-07-15 08:19

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0009_remove_unitmodel_form_remove_unitmodel_subject_and_more'),
        ('payments', '0015_alter_commission_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicAmount',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('period', models.IntegerField(default=1)),
                ('period_type', models.CharField(choices=[('DAY', 'DAY'), ('MONTH', 'MONTH'), ('DAYS', 'DAYS'), ('YEAR', 'YEAR'), ('YEARS', 'YEARS'), ('MONTHS', 'MONTHS')], default='MONTH', max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=19)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topic_amounts', to='school.topicmodel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]