# -*- coding: utf-8 -*-

import logging

log = logging.getLogger('www')

def get_sys_config(key):
    config = DBConfig.objects.filter(key=key)[0]
    if config:
        return config.value
    
    return None

def set_sys_config(key, value):
    config = DBConfig.objects.filter(key=key)
    if config:
        config.value = value
    else:
        config = DBConfig(key=key, value=value)
        config.save()

