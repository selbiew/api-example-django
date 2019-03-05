# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-05 02:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0014_patient__custom_demographics'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentMeta',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('arrival_time', models.DateTimeField(null=True)),
                ('start_time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='office',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='patient',
        ),
        migrations.RemoveField(
            model_name='appointmentprofile',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='customdemographic',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='office',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='doctor',
        ),
        migrations.DeleteModel(
            name='Appointment',
        ),
        migrations.DeleteModel(
            name='AppointmentProfile',
        ),
        migrations.DeleteModel(
            name='CustomDemographic',
        ),
        migrations.DeleteModel(
            name='Doctor',
        ),
        migrations.DeleteModel(
            name='Office',
        ),
        migrations.DeleteModel(
            name='Patient',
        ),
    ]
