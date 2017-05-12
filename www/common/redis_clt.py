#coding=utf8

import redis
from settings import REDIS_USER

USER_REDIS_CLT = None

def get_user_redis():
    global USER_REDIS_CLT
    if not USER_REDIS_CLT:
        USER_REDIS_CLT = redis.StrictRedis(host=REDIS_USER[0], port=REDIS_USER[1], db=REDIS_USER[2])

    return USER_REDIS_CLT