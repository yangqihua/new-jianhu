# -*- coding: utf-8 -*-

from common.sys_config import log
from user.models import Bind, WxSubscribe
from common.redis_clt import get_user_redis


def get_user_id_and_subscribed_from_db(openid):
    binds = Bind.objects.filter(wx_openid=openid).only('user_id')[:1]
    if binds:
        user_id = binds[0].user_id
    else:
        return []

    wx_subscribed = False
    if openid:
        objects = WxSubscribe.objects.filter(wx_openid=openid)[:1]
        if objects:
            wx_subscribed = objects[0].wx_subscribed

    if wx_subscribed:
        return [user_id, 1]
    else:
        return [user_id, 0]


def get_user_id_and_subscribed(openid):
    if not openid:
        return [0,0]

    str = get_user_redis().get(openid)
    if str:
        user_id_and_subscribed = str.split("|")
        if len(user_id_and_subscribed) == 2:
            return user_id_and_subscribed
        else:
            get_user_redis().delete(openid)

    user_id_and_subscribed = get_user_id_and_subscribed_from_db(openid)
    if not user_id_and_subscribed:
        return [0,0]

    get_user_redis().set(openid, "%s|%s" % (user_id_and_subscribed[0], user_id_and_subscribed[1]), 30 * 24 * 3600)
    return user_id_and_subscribed


class CheckWXBindMiddleware(object):
    def process_request(self, request):
        if 'openid' in request.COOKIES:
            raw_openid = request.COOKIES['openid'].split('|')
            if len(raw_openid) == 2:
                openid = raw_openid[0]
                user_id_and_subscribed = get_user_id_and_subscribed(openid)
                setattr(request, "bind_wx", user_id_and_subscribed[1])
                try:
                    user_id = long(user_id_and_subscribed[0])
                except Exception, e:
                    get_user_redis().delete(openid)
                    setattr(request, "user_id", 0L)
                    log.error("Cant get Userid by: %s  e: %s" % (raw_openid, e))
                else:
                    setattr(request, "user_id", user_id)

                setattr(request, "openid", openid)
            else:
                setattr(request, "openid", '')
                log.error("Cant Get Userid By: %s" % raw_openid) 


    def process_response(self, request, response):
        return response

