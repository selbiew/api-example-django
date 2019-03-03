# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-03 02:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('duration', models.IntegerField()),
                ('reason', models.CharField(max_length=1024)),
                ('scheduled_time', models.DateTimeField()),
                ('status', models.CharField(max_length=64)),
                ('is_walk_in', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentProfile',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('duration', models.IntegerField()),
                ('name', models.CharField(max_length=64)),
                ('reason', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Doctor')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('gender', models.CharField(choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')], max_length=6)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Doctor')),
            ],
        ),
        migrations.AddField(
            model_name='appointmentprofile',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Doctor'),
        ),
        migrations.AddField(
            model_name='appointmentprofile',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Office'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Doctor'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Office'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drchrono.Patient'),
        ),
    ]