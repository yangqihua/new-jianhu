# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-01 22:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_auto_20160901_2226'),
    ]

    operations = [
        migrations.AddField(
            model_name='myrecommendmerg',
            name='update_time',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 9, 1, 22, 37, 30, 144122)),
            preserve_default=False,
        ),
    ]