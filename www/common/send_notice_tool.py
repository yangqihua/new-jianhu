# -*- coding: utf-8 -*-

import redis
from common.sys_config import log

from settings import REDIS_NOTICE
gNoticeRedisClt = redis.StrictRedis(host=REDIS_NOTICE[0], port=REDIS_NOTICE[1], db=REDIS_NOTICE[2])

def get_key(openid):
    return "%s_notice" % openid

def touch(openid):
    log.info("touch %s" % openid)
    if openid and len(openid) > 3:
        #自己操作了界面，说明自己还是比较关心消息，设置下次有新消息就通知. 在点击消息列表界面和私信界面时触发该操作
        gNoticeRedisClt.delete(get_key(openid))

def send_notice(openid):
    if openid and len(openid) > 3:
        log.info("send_notice %s" % openid)
        gNoticeRedisClt.rpush("notice_queue", openid)
