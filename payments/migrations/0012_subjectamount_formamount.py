# Generated by Django 4.0.4 on 2022-06-18 14:16

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0006_videomodel_description'),
        ('payments', '0011_alter_invoiceunit_invoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectAmount',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('period', models.IntegerField(default=1)),
                ('period_type', models.CharField(choices=[('DAY', 'DAY'), ('MONTH', 'MONTH'), ('DAYS', 'DAYS'), ('YEAR', 'YEAR'), ('YEARS', 'YEARS'), ('MONTHS', 'MONTHS')], default='MONTH', max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=19)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_subject_amounts', to='school.formmodel')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_amounts', to='school.subjectmodel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormAmount',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('period', models.IntegerField(default=1)),
                ('period_type', models.CharField(choices=[('DAY', 'DAY'), ('MONTH', 'MONTH'), ('DAYS', 'DAYS'), ('YEAR', 'YEAR'), ('YEARS', 'YEARS'), ('MONTHS', 'MONTHS')], default='MONTH', max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=19)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_amounts', to='school.formmodel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
