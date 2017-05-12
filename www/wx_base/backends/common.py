#coding=utf8
import hmac
import redis

from settings import REDIS_WEIXIN
from .. import WeixinHelper, class_property

#经过测试，redis连接在网络断开，redisserver重启等情况下可以等待，在对方恢复后可以恢复工作
WEIXIN_REDIS_CLT = None

class CommonHelper(object):

    @classmethod
    def get_redis(cls):
        global WEIXIN_REDIS_CLT
        if not WEIXIN_REDIS_CLT:
            WEIXIN_REDIS_CLT = redis.StrictRedis(host=REDIS_WEIXIN[0], port=REDIS_WEIXIN[1], db=REDIS_WEIXIN[2])
            return WEIXIN_REDIS_CLT

        return WEIXIN_REDIS_CLT


    @class_property
    def expire(cls):
        """比真实过期减少时间2分钟"""
        return 120


    @class_property
    def access_token_key(cls):
        return "WEIXIN_ACCESS_TOKEN"


    @class_property
    def jsapi_ticket_key(cls):
        return "WEIXIN_JSAPI_TICKET"


    @class_property
    def clear_access_token(cls):
        cache = cls.get_redis()
        key = cls.access_token_key
        cache.delete(key)


    @class_property
    def access_token(cls):
        cache = cls.get_redis()
        key = cls.access_token_key
        token = cache.get(key)
        if not token:
            data = WeixinHelper.getAccessToken()
            token, expire = data["access_token"], data["expires_in"]
            if token and expire:
                cache.set(key, token, expire-cls.expire)
        return token


    @class_property
    def jsapi_ticket(cls):
        cache = cls.get_redis()
        key = cls.jsapi_ticket_key
        ticket = cache.get(key)
        if not ticket:
            data = WeixinHelper.getJsapiTicket(cls.access_token)
            ticket, expire = data["ticket"], data["expires_in"]
            cache.set(key, ticket, expire-cls.expire)
        return ticket


    @classmethod
    def send_text_message(cls, openid, message):
        """客服主动推送消息"""
        return WeixinHelper.sendTextMessage(openid, message, cls.access_token)


    @classmethod
    def jsapi_sign(cls, url):
        """jsapi_ticket 签名"""
        return WeixinHelper.jsapiSign(cls.jsapi_ticket, url)


    @classmethod
    def hmac_sign(cls, key):
        return hmac.new(cls.secret_key, key).hexdigest()


    @classmethod
    def sign_cookie(cls, key):
        """cookie签名"""
        return "{0}|{1}".format(key, cls.hmac_sign(key))


    @classmethod
    def check_cookie(cls, value):
        """验证cookie
        成功返回True, key
        """
        code = value.split("|", 1)
        if len(code) != 2:
            return False, None
        key, signature = code
        if cls.hmac_sign(key) != signature:
            return False, None
        return True, key





