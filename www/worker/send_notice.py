# -*- coding: utf-8 -*-

import os
import sys
import redis
import datetime

file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)

sys.path.insert(0, '../../www')
from settings import REDIS_NOTICE

pf = open('/var/log/jianhu/send_notice.log', 'a')

last_write = datetime.datetime.now()
def write_log(content):
    now = datetime.datetime.now()
    log_str = "%s %s\n" % (now, content)
    pf.write(log_str)
    
    global last_write
    if (now - last_write).seconds > 1:
        last_write = now
        pf.flush()

def write_log_with_pf(content, f):
    log_str = "%s %s\n" % (datetime.datetime.now(), content)
    f.write(log_str)

gNoticeRedisClt = None
def init_notice_redis():
    write_log("init_notice_redis in send_notice")

    global gNoticeRedisClt
    if not gNoticeRedisClt:
        gNoticeRedisClt = redis.StrictRedis(host=REDIS_NOTICE[0], port=REDIS_NOTICE[1], db=REDIS_NOTICE[2])

def get_key(openid):
    return "%s_notice" % openid

#1. 只有私聊消息才会通知
#2. 第一条私聊会通知，后续如果不进入消息中心，则24小时内不再通知; 24小时后如果有新的私信消息到达，则通知 －－ 因为可能是用户不太关心
#3. 用户进入后消息中心或者消息会话页面都表示用户有活动，则3分钟内不通知，因为可能有很多私信消息达到，如果通知很频繁，则会有骚扰嫌疑；3分钟结束时检查是否有消息，有消息则通知
def main():
    while True:
        #从redis中监听队列，如果有数据，则发送
        popRet = gNoticeRedisClt.blpop("notice_queue")
        if popRet:
            openid = popRet[1]
            write_log("pop openid: %s" % openid)
            value = gNoticeRedisClt.exists(get_key(openid))
            if not value:
                #没有记录，则发送，key消失的时候会再次发送
                ret = send_notice(openid, pf)
                if ret:
                    gNoticeRedisClt.set(get_key(openid), 1, ex=24*60*60)
            else:
                write_log("not send to %s for too quick" % openid)

def send_notice(openid, f):
    #取私信消息数
    #取。。。。
    #发送模版消息
    write_log_with_pf("send notice to %s succ" % openid, f)
    return True

if __name__ == '__main__':
    init_notice_redis()
    main()

