# -*- coding: utf-8 -*-
import datetime
from common.sys_config import log
from common.str_tools import gen_uuid
from common.redis_clt import get_user_redis
from user.models import Bind, WxSubscribe, Profile, ProfileExt, MyRecommend


# 从腾讯获取用户数据的回调, 存储到数据库中, 因为有多表，需要增加事物控制
# todo @transaction.commit_on_success
def fetch_user_info_callback(openid, userinfo, request):
    sex = 'O'
    if 'sex' in userinfo:
        if userinfo['sex'] == 1:
            sex = 'M'
        else:
            sex = 'F'

    wx_subscribed = False
    if 'subscribe' in userinfo:
        if userinfo['subscribe'] == 1:
            wx_subscribed = True

        wxsubscribes = WxSubscribe.objects.filter(wx_openid=openid)[:1]
        if wxsubscribes:
            wxsubscribes[0].wx_subscribed = wx_subscribed
            wxsubscribes[0].save()
        elif wx_subscribed:
            wxsubscribe = WxSubscribe(wx_openid=openid, wx_subscribed=True)
            wxsubscribe.save()

    wx_subscribed = 0
    wxsubscribes = WxSubscribe.objects.filter(wx_openid=openid)[:1]
    if wxsubscribes:
        wx_subscribed = wxsubscribes[0].wx_subscribed

    setattr(request, "bind_wx", wx_subscribed)

    log.info("[WXCALLBACK]userinfo: %s" % userinfo)

    exist = Bind.objects.filter(wx_openid=openid)
    if not exist:
        log.info("[WXCALLBACK]new user. openid: %s" % (openid, ))

        profile = Profile(uuid=gen_uuid(), nick=userinfo['nickname'], sex=sex, portrait=userinfo['headimgurl'],
            real_name='', company_name='', title='', vip=False, desc='', nation=userinfo['country'],
            province=userinfo['province'], city=userinfo['city'], district='')
        profile.save()

        bind = Bind(user_id=profile.id, phone_number='', phone_number_verify_time='1972-01-01', wx_openid=openid,
            wx_openid_verify_time=datetime.datetime.now(), qq_openid='', qq_openid_verify_time='1972-01-01',
            weibo_openid='', weibo_openid_verify_time='1972-01-01', email='', email_verify_time='1972-01-01')
        bind.save()

        profileext = ProfileExt(user_id=profile.id, education='', blood_type='', birthday='1972-01-01',
            certificate_no='')
        profileext.save()

        setattr(request, "user_id", profile.id)
    else:
        log.debug('[WXCALLBACK]exist user。user_id: %s' % exist[0].user_id)

        setattr(request, "user_id", exist[0].user_id)

        profiles = Profile.objects.filter(id=exist[0].user_id)[:1]
        if profiles:
            profiles[0].nick = userinfo['nickname']
            profiles[0].sex = sex
            profiles[0].portrait = userinfo['headimgurl']
            profiles[0].nation = userinfo['country']
            profiles[0].province = userinfo['province']
            profiles[0].city = userinfo['city']
            profiles[0].save()
        else:
            profile = Profile(uuid=gen_uuid(), nick=userinfo['nickname'], sex=sex, portrait=userinfo['headimgurl'],
                real_name='', company_name='', title='', vip=False, desc='', nation=userinfo['country'],
                province=userinfo['province'], city=userinfo['city'], district='')
            profile.save()


from wx_base.backends.dj import sns_userinfo_callback

sns_userinfo_with_userinfo = sns_userinfo_callback(fetch_user_info_callback)


def get_user_profile_by_user_id(user_id, need_default):
    profiles = Profile.objects.filter(id=user_id)[:1]
    if profiles:
        return profiles[0]

    if need_default:
        return Profile(id=user_id, uuid='', nick='', sex='O', real_name='', portrait='', company_name='', title='',
            vip=False, desc='', nation='', province='', city='', district='', pub_valid_job_cnt=0)
    else:
        return None


def is_vip(user_id):
    profiles = Profile.objects.filter(id=user_id)[:1]
    if profiles and profiles[0].vip:
        return True

    return False


def get_recommend_id(user_id, job_id):
    objects = MyRecommend.objects.filter(user_id=user_id, job_id=job_id).only('id')[:1]
    if objects:
        return objects[0].id
    else:
        return 0


def get_userinfomap(profile):
    userinfo = {}
    userinfo['nick'] = get_user_name(profile)
    userinfo['portrait'] = profile.portrait
    userinfo['user_company'] = profile.company_name
    userinfo['user_title'] = profile.title
    userinfo['user_desc'] = profile.desc
    userinfo['user_city'] = profile.city
    userinfo['user_province'] = profile.province
    userinfo['user_district'] = profile.district
    userinfo['vip'] = profile.vip
    return userinfo


def get_user_name(profile):
    if profile.real_name == "":
        return profile.nick
    else:
        return profile.real_name


def get_isbind_and_isedit(profile, request, page_data):
    page_data['bind_wx'] = '1' if (request.bind_wx is True or request.bind_wx == '1') else '0'
    if not profile:
        user_id = request.user_id
        profile = get_user_profile_by_user_id(user_id, True)

    page_data['is_edit'] = "0" if profile.real_name == "" else "1"
    return page_data

def get_openid(user_id):
    objects = Bind.objects.filter(user_id=user_id)[:1]
    if objects:
        return objects[0].wx_openid

    return None
