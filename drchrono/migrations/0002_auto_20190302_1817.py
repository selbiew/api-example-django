# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-03 02:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='office',
        ),
        migrations.RemoveField(
            model_name='appointmentprofile',
            name='office',
        ),
    ]
