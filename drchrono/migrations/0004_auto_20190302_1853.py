# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-02 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0003_auto_20190302_1840'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='scheduled_time',
            new_name='scheduled_start_time',
        ),
        migrations.AddField(
            model_name='appointment',
            name='checkin_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='checkout_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='scheduled_end_time',
            field=models.DateTimeField(null=True),
        ),
    ]
