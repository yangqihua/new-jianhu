# coding=utf8
'''
Created on 2014-5-14
django 帮助函数

@author: skycrab

@sns_userinfo
def oauth(request):
    openid = request.openid

'''
import json
from functools import wraps
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect

from .common import CommonHelper
from .. import class_property, WeixinHelper


class Helper(CommonHelper):
    """微信具体逻辑帮组类"""

    @class_property
    def cache(cls):
        """返回cache对象"""
        return cache

    @class_property
    def secret_key(cls):
        """返回cookie加密秘钥"""
        return settings.SECRET_KEY


def sns_userinfo_callback(callback=None):
    """网页授权获取用户信息装饰器
    callback(openid, userinfo, request):
        return user
    """
    """return wrap,向wrap()中传递func的引用"""

    def wrap(func):
        # 原始函数的__name__等属性复制到inner()函数中，不需要编写inner.__name__ = func.__name__这样的代码
        @wraps(func)
        def inner(*args, **kwargs):  # 可以接受任意参数的调用，但views.py里面的函数都只有一个参数request
            request = args[0]  # django第一个参数request
            openid = request.COOKIES.get('openid')
            userinfo = None
            if not openid:  # 客户端cookies失效
                code = request.GET.get("code")
                if not code:
                    # 没有授权记录，进入授权环节，这里的默认都是使用获取用户资料的方式
                    current = "http://" + request.get_host() + request.get_full_path()
                    return redirect(WeixinHelper.oauth2(current))
                else:
                    data = WeixinHelper.getAccessTokenByCode(code)
                    print "[AccessToken]getAccessTokenByCode: %s" % data
                    user_access_token, openid, refresh_token = data["access_token"], data["openid"], data["refresh_token"]
                    userinfo = WeixinHelper.getSnsapiUserInfo(user_access_token, openid)
                    print "[AccessToken]Get(%s) SnsapiUserInfo: %s user_access_token: %s" % (openid, userinfo, user_access_token)

                    if 'errcode' not in userinfo:
                        new_userinfo = WeixinHelper.getUserInfo(CommonHelper.access_token, openid)
                        print "[AccessToken]Get(%s) UserInfo: %s access_token: %s" % (openid, userinfo, CommonHelper.access_token)

                    if 'subscribe' in new_userinfo and new_userinfo['subscribe'] == 1:
                        userinfo = new_userinfo
                    else:
                        userinfo['subscribe'] = 0
            else:
                # 通过opendid来判断，是否有不安全的因素？
                ok, openid = Helper.check_cookie(openid)
                if not ok:
                    return redirect("/")

            request.openid = openid
            if callable(callback) and userinfo:
                request.user = callback(openid, userinfo, request)
            
            response = func(request)
            if userinfo:
                response.set_cookie("openid", Helper.sign_cookie(request.openid), max_age=30*24*3600)

            return response

        return inner

    return wrap


sns_userinfo = sns_userinfo_callback()









