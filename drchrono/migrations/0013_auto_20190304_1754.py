# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-04 17:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0012_auto_20190304_1751'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customdemographic',
            old_name='allowed_values',
            new_name='_allowed_values',
        ),
    ]
