# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-04 20:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0013_auto_20190304_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='_custom_demographics',
            field=models.CharField(max_length=2048, null=True),
        ),
    ]
