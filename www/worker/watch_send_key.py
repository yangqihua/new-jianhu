# -*- coding: utf-8 -*-

import os
import sys
import redis
import datetime

file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)

sys.path.insert(0, '../../www')
from settings import REDIS_NOTICE
from worker import send_notice

pf = open('/var/log/jianhu/watch_send_key.log', 'a')

last_write = datetime.datetime.now()
def write_log(content):
    now = datetime.datetime.now()
    log_str = "%s %s\n" % (now, content)
    pf.write(log_str)

    global last_write
    if (now - last_write).seconds > 1:
        last_write = now
        pf.flush()

gNoticeRedisClt = None
def init_notice_redis():
    write_log("init_notice_redis in watch_send_key")

    global gNoticeRedisClt
    if not gNoticeRedisClt:
        gNoticeRedisClt = redis.StrictRedis(host=REDIS_NOTICE[0], port=REDIS_NOTICE[1], db=REDIS_NOTICE[2])

def call_back(item):
    write_log("del %s call back" % item)
    send_notice.send_notice(item['data'], pf)

def subscribe():
    gNoticeRedisClt.config_set("notify-keyspace-events", "Ex");

    db = REDIS_NOTICE[2]
    ps = gNoticeRedisClt.pubsub()

    event = '__keyevent@%s__:expired' % db
    write_log(event)

    ps.subscribe(event)

    for item in ps.listen():
        call_back(item)

if __name__ == '__main__':
    init_notice_redis()
    subscribe()
