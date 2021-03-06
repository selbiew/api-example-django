# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-03 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0009_auto_20190302_2250'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='checkin_time',
            new_name='checkin_datetime',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='checkout_time',
        ),
        migrations.AddField(
            model_name='appointment',
            name='start_datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[(b'UNK', b''), (b'ARR', b'Arrived'), (b'CHK', b'Checked In'), (b'CNC', b'Canceled'), (b'CMP', b'Complete'), (b'CNF', b'Confirmed'), (b'INS', b'In Session'), (b'NSH', b'No Show'), (b'NCF', b'Not Confirmed'), (b'RSC', b'Rescheduled')], max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='office',
            name='_exam_rooms',
            field=models.CharField(max_length=2048),
        ),
    ]
