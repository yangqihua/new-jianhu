# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class SYSConfig(models.Model):
    #####################################
    key = models.CharField(max_length=36, db_index=True)
    value = models.CharField(max_length=256)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sys_config"

