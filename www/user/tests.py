# -*- coding: utf-8 -*-

from django.test import TestCase

import time
import redis

WEIXIN_REDIS_CLT = None

#经过测试，redis连接在网络断开，redisserver重启等情况下可以等待，在对方恢复后可以恢复工作
class TestRedis(object):

    def get_redis(self):
        global WEIXIN_REDIS_CLT
        if not WEIXIN_REDIS_CLT:
            WEIXIN_REDIS_CLT = redis.StrictRedis(host='139.196.140.181', port=6379, db=0)
            return WEIXIN_REDIS_CLT
        
        return WEIXIN_REDIS_CLT

if __name__ == '__main__':
    for i in range(100):
        print TestRedis().get_redis().ping()
        time.sleep(1)
