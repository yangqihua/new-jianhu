# -*- coding: utf-8 -*-

import json, time
import requests
import datetime
from django.db.models import Q
from common.sys_config import log
from wx_base.wx_tools import jsapi_sign
from django.utils import html
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from common.oss_tools import OSSTools
from common import convert, str_tools
from wx_base.backends.common import CommonHelper
from user import user_tools
from logic import logic_tools
from models import Job, VipJobList, BeInterested, Conversation, MergeMsg, Share
from user.models import Bind, Profile, ProfileExt, MyCollection, MyRecommend, MyRecommendMerg, MyInterview
from common import send_notice_tool

def pc_index(request):
    template = get_template('pc_index.html')
    return HttpResponse(template.render({}, request))


@user_tools.sns_userinfo_with_userinfo
def index(request):
    user_id = request.user_id
    own_profile = user_tools.get_user_profile_by_user_id(user_id=user_id, need_default=False)
    if not own_profile:
        log.error('Cant find user profile by user_id: %s when index' % user_id)
        return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")

    vip_job_from_point = convert.str_to_int(request.GET.get('from', '0'), 0)  # 有from时，则为翻页，无时，则为首页
    number_limit = convert.str_to_int(request.GET.get('limit', '10'), 10)  # 异常情况下，或者不传的情况下，默认为10
    own_job_list = []
    user_info_map = {}

    # 取本人发布过的，并且有效的简历
    if vip_job_from_point == 0:  # 不是首页的话，翻页不需要继续找own_jobs了
        own_jobs = Job.objects.filter(user_id=user_id, is_valid=True).order_by('-id')[:1]
        if len(own_jobs) == 1:  # 自己发过职位
            my_job = own_jobs[0]
            own_job = {'job_city': my_job.city, 'job_addr': my_job.city + " " + my_job.district,
                       'company_name': my_job.company_name, 'job_title': my_job.job_title,
                       'education': my_job.education, 'work_experience': my_job.work_experience,
                       'salary': my_job.salary, 'create_time': convert.format_time(my_job.create_time),
                       'username': user_tools.get_user_name(own_profile), 'portrait': own_profile.portrait,
                       'job_uuid': my_job.uuid, 'user_company': own_profile.company_name, 'vip_display': 'none'}
            own_job_list.append(own_job)

            user_info_map[my_job.uuid] = user_tools.get_userinfomap(own_profile)

    # 按发布时间去取VIP发布简历
    vip_job_records = VipJobList.objects.all().order_by('-pub_time')[
                      vip_job_from_point:number_limit + vip_job_from_point]
    vip_jobs = Job.objects.filter(id__in=list(set([vip_job_record.job_id for vip_job_record in vip_job_records])))
    vip_job_id_to_vip_job = {}
    for vip_job in vip_jobs:
        vip_job_id_to_vip_job[vip_job.id] = vip_job

    profiles = Profile.objects.filter(id__in=list(set([vip_job.user_id for vip_job in vip_jobs])))
    user_id_to_profile = {}
    for profile in profiles:
        user_id_to_profile[profile.id] = profile

    vip_job_list = []
    for vip_job_record in vip_job_records:
        vip_job = vip_job_id_to_vip_job[vip_job_record.job_id]
        profile = user_id_to_profile[vip_job.user_id]
        job = {'job_city': vip_job.city, 'job_addr': vip_job.city + " " + vip_job.district,
               'company_name': vip_job.company_name, 'job_title': vip_job.job_title, 'education': vip_job.education,
               'work_experience': vip_job.work_experience, 'salary': vip_job.salary,
               'create_time': convert.format_time(vip_job.create_time), 'username': user_tools.get_user_name(profile),
               'portrait': profile.portrait, 'job_uuid': vip_job.uuid, 'user_company': profile.company_name}
        vip_job_list.append(job)

        user_info_map[vip_job.uuid] = user_tools.get_userinfomap(profile)

    page_data = {'own_job_list': json.dumps(own_job_list), 'vip_job_list': json.dumps(vip_job_list),
                 'user_info_map': json.dumps(user_info_map)}
    page_data = user_tools.get_isbind_and_isedit(own_profile, request, page_data)

    if vip_job_from_point == 0:  # 首页，需要返回页面
        page_data['jsapi'] = jsapi_sign(request)
        template = get_template('index.html')
        return HttpResponse(template.render(page_data, request))
    else:  # 加载下一页，ajax请求
        page_data = {'own_job_list': own_job_list, 'vip_job_list': vip_job_list, 'user_info_map': user_info_map}
        return HttpResponse(json.dumps(page_data), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def get_chat_list(request):
    user_id = request.user_id
    chat_from_point = convert.str_to_int(request.GET.get('from', '0'), 0)  # 有from时，则为翻页，无时，则为首页
    number_limit = convert.str_to_int(request.GET.get('limit', '10'), 10)  # 异常情况下，或者不传的情况下，默认为10
    chat_list = []
    chats = MergeMsg.objects.filter(Q(qlm_user_id=user_id) | Q(zg_user_id=user_id)).order_by("-update_time")[
            chat_from_point:chat_from_point + number_limit]

    user_id_list = []
    be_interested_id_list = []
    recommend_id_list = []
    job_id_list = []
    for merge_msg in chats:
        if merge_msg.qlm_user_id == user_id:  # 本人是千里马，发消息来的为主公
            user_id_list.append(merge_msg.zg_user_id)
            be_interested_id_list.append(merge_msg.be_interested_id)
        else:  # 本人是主公，发消息来的有可能是千里马或是伯乐
            if merge_msg.recommend_id != 0:  # 说明是伯乐发消息
                user_id_list.append(merge_msg.bl_user_id)
                recommend_id_list.append(merge_msg.recommend_id)
            else:  # 本人是主公，对方是千里马
                user_id_list.append(merge_msg.qlm_user_id)
                be_interested_id_list.append(merge_msg.be_interested_id)

    id_to_profile = {}
    profiles = Profile.objects.filter(id__in=list(set(user_id_list)))
    for profile in profiles:
        id_to_profile[profile.id] = profile

    id_to_be_interested = {}
    be_interesteds = BeInterested.objects.filter(id__in=list(set(be_interested_id_list)))
    for be_interested in be_interesteds:
        job_id_list.append(be_interested.job_id)
        id_to_be_interested[be_interested.id] = be_interested

    id_to_be_recommend = {}
    recommends = MyRecommend.objects.filter(id__in=list(set(recommend_id_list)))
    for recommend in recommends:
        job_id_list.append(recommend.job_id)
        id_to_be_recommend[recommend.id] = recommend

    id_to_job = {}
    jobs = Job.objects.filter(id__in=list(set(job_id_list)))
    for job in jobs:
        id_to_job[job.id] = job

    for merge_msg in chats:
        if merge_msg.qlm_user_id == user_id:  # 本人是千里马，发消息来的为主公
            zg_profile = id_to_profile[merge_msg.zg_user_id]
            be_interested = id_to_be_interested[merge_msg.be_interested_id]
            if not zg_profile or not be_interested:
                continue
            zg_job = id_to_job[be_interested.job_id]
            if not zg_job:
                continue
            display_css = "none" if merge_msg.qlm_have_read else "block"  # 已读和未读判断
            chat_info = {'user_tag': "主公", 'portrait': zg_profile.portrait,
                         'nick': user_tools.get_user_name(zg_profile), 'last_words': merge_msg.last_words,
                         'update_time': convert.format_time(merge_msg.update_time), 'display_css': display_css,
                         'background_color': "#c773ff", 'job_title': zg_job.company_name + zg_job.job_title,
                         'go_url': "/chat/chat_detail?be_interested_uuid=" + be_interested.uuid, 'hint': '招聘职位：'}
        else:  # 本人是主公，发消息来的有可能是千里马或是伯乐
            if merge_msg.recommend_id != 0:  # 说明是伯乐发消息
                bl_profile = id_to_profile[merge_msg.bl_user_id]
                recommend = id_to_be_recommend[merge_msg.recommend_id]
                if not bl_profile or not recommend:
                    continue
                zg_job = id_to_job[recommend.job_id]
                if not zg_job:
                    continue
                display_css = "none" if merge_msg.zg_have_read else "block"
                chat_info = {'user_tag': "伯乐", 'portrait': bl_profile.portrait,
                             'nick': user_tools.get_user_name(bl_profile), 'last_words': merge_msg.last_words,
                             'update_time': convert.format_time(merge_msg.update_time), 'display_css': display_css,
                             'background_color': "#ff9600", 'job_title': zg_job.company_name + zg_job.job_title,
                             'go_url': "/job/post_recommand_job_success?is_chat=1&share_to_zg=1&recommend_uuid=" + recommend.uuid + "&merge_msg_uuid=" + merge_msg.uuid,
                             'hint': '推荐职位：'}
            else:  # 本人是主公，对方是千里马
                qlm_profile = id_to_profile[merge_msg.qlm_user_id]
                be_interested = id_to_be_interested[merge_msg.be_interested_id]
                if not qlm_profile or not be_interested:
                    continue
                zg_job = id_to_job[be_interested.job_id]
                if not zg_job:
                    continue
                display_css = "none" if merge_msg.zg_have_read else "block"
                chat_info = {'user_tag': "千里马", 'portrait': qlm_profile.portrait,
                             'nick': user_tools.get_user_name(qlm_profile), 'last_words': merge_msg.last_words,
                             'update_time': convert.format_time(merge_msg.update_time), 'display_css': display_css,
                             'background_color': "#00a8ff", 'job_title': zg_job.company_name + zg_job.job_title,
                             'go_url': "/chat/chat_detail?be_interested_uuid=" + be_interested.uuid, 'hint': '应聘职位：'}
        chat_list.append(chat_info)

    page_data = {'chat_list': json.dumps(chat_list)}

    send_notice_tool.touch(request.openid)

    if chat_from_point == 0:  # 首页，需要返回页面
        page_data['jsapi'] = jsapi_sign(request)
        template = get_template('chat/mesg.html')
        return HttpResponse(template.render(page_data, request))
    else:  # 加载下一页，ajax请求
        return HttpResponse(json.dumps({'chat_list': chat_list}), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def get_job(request):
    user_id = request.user_id
    job_uuid = request.GET.get('job_uuid', '')
    last_share_uuid = request.GET.get('last_share_uuid', '')
    job_details = Job.objects.filter(uuid=job_uuid)[:1]
    if job_details:

        if user_id == job_details[0].user_id:
            return HttpResponseRedirect("/user/fabu_detail?job_uuid=" + job_uuid)

        page_data = model_to_dict(job_details[0], exclude=['id', 'user_id', 'create_time', 'update_time', ])
        page_data['job_addr'] = job_details[0].city + " " + job_details[0].district
        page_data['job_city'] = job_details[0].city

        profile = user_tools.get_user_profile_by_user_id(user_id=job_details[0].user_id, need_default=True)
        page_data['username'] = user_tools.get_user_name(profile)
        page_data['portrait'] = profile.portrait
        page_data['user_company'] = profile.company_name
        page_data['user_uuid'] = profile.uuid
        page_data['user_title_count'] = profile.pub_valid_job_cnt
        page_data['last_share_uuid'] = last_share_uuid

        page_data['vip_display'] = "block" if profile.vip else 'none'

        # 收藏按钮的控制
        if user_id != job_details[0].user_id:  # 这个职位不是该userid发布的
            my_collection = MyCollection.objects.filter(user_id=user_id, job_id=job_details[0].id)
            if my_collection:  # 我已经收藏过该职位
                page_data['collection'] = "取消收藏"
            else:
                page_data['collection'] = "收藏职位"

        page_data['user_info_map'] = json.dumps({job_uuid: user_tools.get_userinfomap(profile)})
    else:
        log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
        return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    page_data['jsapi'] = jsapi_sign(request)
    page_data = user_tools.get_isbind_and_isedit(None, request, page_data)

    template = get_template('job/job_detail.html')
    return HttpResponse(template.render(page_data, request))


@user_tools.sns_userinfo_with_userinfo
def post_res_for_job(request):
    media_id = request.GET.get('media_id')
    if not media_id:
        return HttpResponse("")

    access_token = CommonHelper.access_token
    url = "http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" % (access_token, media_id)
    log.debug("Res Url: %s" % url)
    ret = requests.get(url)
    if ((ret.status_code == 200) and ("image" in ret.headers["Content-Type"]) and (
                "filename" in ret.headers["Content-disposition"]) and (ret.headers["Content-Length"] > 500)):
        OSSUgcRes = OSSTools('ugcres')
        picname = str_tools.gen_short_uuid()
        OSSUgcRes.upload_from_url(picname, ret.content)

        log.info("[UploadToOSS] Succ, url: %s      picname: %s " % (url, picname))
        return HttpResponse(picname)
    else:
        resp = json.loads(ret.text)
        if "errcode" in resp and (resp["errcode"] == 40001 or resp["errcode"] == 42001):
            log.error("Wrong Ret, going to clear access token, err: %s" % ret.text)
            CommonHelper.clear_access_token

        log.error(
            "[UploadToOSS] Fail, Check Url: %s      Header: %s       Resp: %s" % (url, str(ret.headers), ret.text))
        return HttpResponse("")


@user_tools.sns_userinfo_with_userinfo
def post_job(request):
    user_id = request.user_id

    profile = user_tools.get_user_profile_by_user_id(user_id=user_id, need_default=False)
    if not profile:
        log.error('Cant find user profile by user_id: %s when post_job' % user_id)
        return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")

    company_name = html.escape(request.POST.get('company_name'))[:30]
    job_title = html.escape(request.POST.get('job_title'))[:30]
    work_experience = html.escape(request.POST.get('work_experience'))[:10]
    salary = html.escape(request.POST.get('salary'))[:10]
    education = html.escape(request.POST.get('education'))[:10]

    job_addr = html.escape(request.POST.get('job_addr')).split(' ')
    if len(job_addr) < 2:
        return HttpResponse("地理位置参数错误")

    province = job_addr[0][:20]
    city = job_addr[1][:20]
    district = ''
    if len(job_addr) == 3:  # 防止有些地方没有区，数组越界异常
        district = job_addr[2][:20]

    if not (company_name and job_title and work_experience and salary and education and job_addr and province and city):
        return HttpResponse("十分抱歉，你输入的参数缺失，请检查确认后重试。重试失败请联系客服人员")

    skills = ""
    for i in range(1, 7):
        skill = html.escape(request.POST.get('skill%s' % i))
        if skill != "":
            skills += skill + ","
    skills = skills[:-1][:120]

    piclist = ''
    for i in range(1, 7):
        picname = html.escape(request.POST.get('img_url%s' % i))
        if picname:
            if piclist:
                piclist = '%s,%s' % (piclist, picname)
            else:
                piclist = picname
    piclist = piclist[:256]

    job_uuid = request.POST.get('job_uuid', '')
    if job_uuid:  # 有job_uuid, 更新职位信息
        job_details = Job.objects.filter(uuid=job_uuid)[:1]
        if job_details:
            job_id = job_details[0].id
            job = Job(id=job_id, uuid=job_uuid, user_id=user_id, company_name=company_name, job_title=job_title,
                work_experience=work_experience, salary=salary, education=education, province=province, city=city,
                district=district, skill=skills, piclist=piclist, create_time=job_details[0].create_time)
        else:
            log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
            return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    else:  # 插入一条新的职位
        job = Job(uuid=str_tools.gen_uuid(), user_id=user_id, company_name=company_name, job_title=job_title,
            work_experience=work_experience, salary=salary, education=education, province=province, city=city,
            district=district, skill=skills, piclist=piclist)
        profile.pub_valid_job_cnt += 1
        profile.save()
    job.save()

    try:
        if profile.vip:
            vip_job = VipJobList(job_id=job.id, user_id=user_id, pub_time=datetime.datetime.now())
            vip_job.save()
    except Exception, e:
        log.error("VipJobList Exception: %s" % e)

    page_data = logic_tools.get_job_detail(job.id)
    page_data['post_success'] = 1
    page_data['jsapi'] = jsapi_sign(request)

    template = get_template('user/fabu_detail.html')
    return HttpResponse(template.render(page_data, request))


# 编辑或者进入发布职位页面
@user_tools.sns_userinfo_with_userinfo
def fabu_job(request):
    user_id = request.user_id
    job_uuid = request.GET.get('job_uuid', '')

    own_job = {}
    page_data = {}
    if job_uuid:  # 如果有传job_uuid，说明是编辑职位信息
        job_details = Job.objects.filter(uuid=job_uuid)[:1]
        if job_details:
            own_job['job_company'] = job_details[0].company_name
            own_job['job_title'] = job_details[0].job_title
            own_job['job_experience'] = job_details[0].work_experience
            own_job['job_salary'] = job_details[0].salary
            own_job['job_education'] = job_details[0].education
            own_job['job_addr'] = job_details[0].province + " " + job_details[0].city + " " + job_details[0].district
            own_job['job_skill'] = job_details[0].skill
            own_job['job_img'] = job_details[0].piclist
            page_data['job_uuid'] = job_details[0].uuid
            page_data['is_new'] = '0'  # 标记是修改职位
            page_data['own_job'] = json.dumps(own_job)
        else:
            log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
            return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")
    else:  # 取最近发布的一条职位信息
        job_details = Job.objects.filter(user_id=user_id).order_by('-id')[:1]
        page_data['is_new'] = '1'  # 标记是新发布的一条职位
        if job_details:  # 有发布过职位
            own_job['job_company'] = job_details[0].company_name
            own_job['job_title'] = job_details[0].job_title
            own_job['job_experience'] = job_details[0].work_experience
            own_job['job_salary'] = job_details[0].salary
            own_job['job_education'] = job_details[0].education
            own_job['job_addr'] = job_details[0].province + " " + job_details[0].city + " " + job_details[0].district
            own_job['job_skill'] = job_details[0].skill
            own_job['job_img'] = job_details[0].piclist
            page_data['own_job'] = json.dumps(own_job)

    page_data['jsapi'] = jsapi_sign(request)
    template = get_template('job/job_fabu.html')
    return HttpResponse(template.render(page_data, request))


@user_tools.sns_userinfo_with_userinfo
def recommand_job(request):
    user_id = request.user_id
    job_uuid = request.GET.get('job_uuid', '')
    last_share_uuid = request.GET.get('last_share_uuid', '00000000000000000000000000000000')
    job_details = Job.objects.filter(uuid=job_uuid)[:1]
    if job_details:
        page_data = model_to_dict(job_details[0], exclude=['id', 'user_id', 'is_valid', 'create_time', 'update_time', ])
        page_data['job_addr'] = job_details[0].city + " " + job_details[0].district
        page_data['job_city'] = job_details[0].city

        profile = user_tools.get_user_profile_by_user_id(user_id=job_details[0].user_id, need_default=True)
        page_data['username'] = user_tools.get_user_name(profile)
        page_data['portrait'] = profile.portrait
        page_data['user_company'] = profile.company_name
        page_data['user_info_map'] = json.dumps(user_tools.get_userinfomap(profile))
        page_data['last_share_uuid'] = last_share_uuid

        page_data['vip_display'] = "block" if profile.vip else "none"
    else:
        log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
        return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    page_data['jsapi'] = jsapi_sign(request)
    template = get_template('job/job_recommand.html')
    return HttpResponse(template.render(page_data, request))


@user_tools.sns_userinfo_with_userinfo
def post_recommand_job(request):
    user_id = request.user_id
    audio_for_zg = html.escape(request.POST.get('audio_for_zg', '')) + "," + request.POST.get('audio_for_zg_length', '')
    audio_for_qlm = html.escape(request.POST.get('audio_for_qlm', '')) + "," + request.POST.get('audio_for_qlm_length',
        '')

    if user_id == 0:
        return HttpResponse("十分抱歉，参数错误，请联系客服人员")

    job_uuid = request.GET.get('job_uuid', '')

    last_share_uuid = request.GET.get('last_share_uuid', '00000000000000000000000000000000')

    job_details = Job.objects.filter(uuid=job_uuid)[:1]
    if job_details:
        my_recommend = MyRecommend(uuid=str_tools.gen_uuid(), user_id=user_id, job_id=job_details[0].id,
            audio_for_zg=audio_for_zg, audio_for_qlm=audio_for_qlm, last_share_uuid=last_share_uuid)
        my_recommend.save()

        merge_msg = MergeMsg(update_time=datetime.datetime.now(), uuid=str_tools.gen_uuid(), bl_user_id=user_id,
            zg_user_id=job_details[0].user_id, recommend_id=my_recommend.id, zg_have_read=False,
            last_words="给您推荐了千里马！快听听吧！")
        merge_msg.save()

        my_recommend_merge = MyRecommendMerg.objects.filter(user_id=user_id, job_id=job_details[0].id)
        if my_recommend_merge:
            my_recommend_merge[0].recommend_num = my_recommend_merge[0].recommend_num + 1
            my_recommend_merge[0].save()
        else:
            my_recommend_merge = MyRecommendMerg(user_id=user_id, job_id=job_details[0].id, recommend_num=1)
            my_recommend_merge.save()
    else:
        log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
        return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    return HttpResponseRedirect(
        "/job/post_recommand_job_success?last_share_uuid=" + last_share_uuid + "&recommend_uuid=" + str(
            my_recommend.uuid) + "&post_success=1&share_to_zg=0")


# 调用该函数的地方有：
# 1.伯乐推荐录音成功后返回传post_success来标识
# 2.伯乐录完音分享出去（可以分享给主公或千里马），用户点击进来，传share_to_zg来区分是千里马还是主公
# 3.消息页面：点击消息页面，返回给伯乐的录音界面，传share_to_zg=1和is_chat=1
@user_tools.sns_userinfo_with_userinfo
def post_recommand_job_success(request):
    recommend_uuid = request.GET.get('recommend_uuid', '')
    last_share_uuid = request.GET.get('last_share_uuid', '')
    my_recommend = MyRecommend.objects.filter(uuid=recommend_uuid)[:1]

    if not my_recommend:
        log.error('Cant find recommend by recommend_uuid: %s' % recommend_uuid)
        return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")

    is_chat = request.GET.get('is_chat', '')
    if is_chat == '1':  # 说明是查看消息，更新merge_msg表，设置消息已读
        merge_msg_uuid = request.GET.get('merge_msg_uuid', '')
        merge_msg = MergeMsg.objects.filter(uuid=merge_msg_uuid)[:1]
        if not merge_msg:
            log.error('Cant find merge_msg by merge_msg_uuid: %s' % merge_msg_uuid)
            return HttpResponse("十分抱歉，获取推荐消息失败，请重试。重试失败请联系客服人员")
        merge_msg[0].zg_have_read = True
        merge_msg[0].save()

    post_success = request.GET.get('post_success', '')
    share_to_zg = request.GET.get('share_to_zg', '')

    page_data = logic_tools.get_job_detail(my_recommend[0].job_id)
    logic_tools.fullfill_recommend_detail(page_data, my_recommend[0], share_to_zg == '1', share_to_zg == '0')

    page_data['post_success'] = post_success

    # if share_to_zg == '0':  # 如果是分享给千里马的，则带上last_share_uuid
    page_data['last_share_uuid'] = last_share_uuid

    page_data['jsapi'] = jsapi_sign(request)
    page_data = user_tools.get_isbind_and_isedit(None, request, page_data)
    template = get_template('job/job_recommend_success.html')
    return HttpResponse(template.render(page_data, request))


@user_tools.sns_userinfo_with_userinfo
def chat_detail(request):
    
    send_notice_tool.touch(request.openid)

    user_id = request.user_id
    be_interested_uuid = request.GET.get('be_interested_uuid', '')

    chat_from_point = convert.str_to_int(request.GET.get('from', '0'), 0)  # 有from时，则为翻页，无时，则为首页
    number_limit = convert.str_to_int(request.GET.get('limit', '10'), 10)  # 异常情况下，或者不传的情况下，默认为10

    chat_user_info_map = {}
    be_interesteds = BeInterested.objects.filter(uuid=be_interested_uuid)[:1]
    if not be_interesteds:
        log.error('Cant find be_interesteds by be_interested_uuid: %s ' % be_interested_uuid)
        return HttpResponse("十分抱歉，获取留言信息失败，请重试。重试失败请联系客服人员")

    be_interested = be_interesteds[0]

    job_details = Job.objects.filter(id=be_interested.job_id)[:1]
    if not job_details:
        log.error("uid(%s) try to get not exsit job, maybe attack" % user_id)
        return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    conversations = Conversation.objects.filter(be_interested_id=be_interested.id).order_by("-id")[
                    chat_from_point:chat_from_point + number_limit]
    conversation_list = []
    qlm_profile = user_tools.get_user_profile_by_user_id(be_interested.qlm_user_id, need_default=True)
    bl_profile = user_tools.get_user_profile_by_user_id(job_details[0].user_id, need_default=True)
    for conversation in conversations:
        if be_interested.qlm_user_id == conversation.user_id:  # 说明是qlm
            profile = qlm_profile
        else:
            profile = bl_profile

        conversation_data = {'user_portrait': profile.portrait, 'user_nick': user_tools.get_user_name(profile),
                             'user_uuid': profile.uuid, 'words': conversation.words,
                             'create_time': conversation.create_time.strftime('%Y-%m-%d %H:%M'),
                             'vip_display': 'block' if profile.vip else 'none'}

        chat_user_info_map[profile.uuid] = user_tools.get_userinfomap(profile)
        conversation_list.append(conversation_data)

    if chat_from_point == 0:  # 首页，需要返回页面
        page_data = logic_tools.get_job_detail(job_details[0].id)
        page_data['conversation_list'] = json.dumps(conversation_list)
        page_data['be_interested_uuid'] = str(be_interested.uuid)
        page_data['chat_user_info_map'] = json.dumps(chat_user_info_map)
        page_data['jsapi'] = jsapi_sign(request)

        merge_msg = MergeMsg.objects.filter(be_interested_id=be_interested.id)[:1]
        if not merge_msg:
            log.error('Cant find merge_msg by be_interested_id: %s' % be_interested.id)
            return HttpResponse("十分抱歉，获取推荐消息失败，请重试。重试失败请联系客服人员")
        if user_id == job_details[0].user_id:  # 我是主公，返回千里马的姓名
            merge_msg[0].zg_have_read = True
            merge_msg[0].save()
            page_data['des_nick'] = user_tools.get_user_name(qlm_profile)
        else:
            merge_msg[0].qlm_have_read = True
            merge_msg[0].save()
            page_data['des_nick'] = user_tools.get_user_name(bl_profile)
        template = get_template('chat/chat.html')
        return HttpResponse(template.render(page_data, request))
    else:  # 加载下一页，ajax请求
        page_data = {"conversation_list": conversation_list, "chat_user_info_map": chat_user_info_map}
        return HttpResponse(json.dumps(page_data), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def interest_job(request):
    user_id = request.user_id

    # 1.从vip职位列表那里直接点击感兴趣进来传进来-------job_uuid->job
    # 2.通过别人分享链接(分享的职位详情)进来------------share_uuid获取job_id->job
    # 3.通过别人分享链接(分享的带推荐录音的职位详情)进来 share_uuid获取recommend_id->job

    recommend_uuid = request.GET.get('recommend_uuid', '')
    last_share_uuid = request.GET.get('last_share_uuid', '')

    job_uuid = request.GET.get('job_uuid', '')

    job_details = []
    if last_share_uuid:  # 通过别人的分享链接进来的1.职位详情2.带录音的职位详情，只要有share_uuid就可以拿到job
        if recommend_uuid:  # 传recommend_uuid，为带录音的职位详情
            recommends = MyRecommend.objects.filter(uuid=recommend_uuid)[:1]
            if not recommends:
                return HttpResponse("十分抱歉，获取推荐信息失败，请重试。重试失败请联系客服人员")

            job_details = Job.objects.filter(id=recommends[0].job_id)[:1]
        elif job_uuid:
            job_details = Job.objects.filter(uuid=job_uuid)[:1]

        if not job_details:
            log.error("uid(%s) try to get not exsit job, maybe attack" % user_id)
            return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    elif job_uuid:  # 说明直接点我感兴趣进来的，没有通过分享
        job_details = Job.objects.filter(uuid=job_uuid)[:1]
        last_share_uuid = "00000000000000000000000000000000"

        if not job_details:
            log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
            return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    be_interested = BeInterested.objects.filter(job_id=job_details[0].id, qlm_user_id=user_id)[:1]
    if not be_interested:  # 当前user以前没有对这个职位点击过我感兴趣,则插入数据

        be_interested = BeInterested(last_share_uuid=last_share_uuid, job_id=job_details[0].id, qlm_user_id=user_id,
            uuid=str_tools.gen_uuid())
        be_interested.save()

        conversation = Conversation(be_interested_id=be_interested.id, user_id=user_id,
            words="主公，我揭了您的“招贤令”！<span style='color:#8e8e8e;'>(系统代发消息)</span>")
        conversation.save()
        conversation = Conversation(create_time=datetime.datetime.fromtimestamp(time.time() + 2),
            be_interested_id=be_interested.id, user_id=job_details[0].user_id,
            words="管家！快给英雄赐座。容我先批完折子。<span style='color:#8e8e8e;'>(系统代发消息)</span>")
        conversation.save()

        merge_msg = MergeMsg(update_time=datetime.datetime.now(), uuid=str_tools.gen_uuid(),
            zg_user_id=job_details[0].user_id, be_interested_id=be_interested.id, qlm_user_id=user_id,
            last_words="管家！快给英雄赐座。容我先批完折子。<span style='color:#8e8e8e;'>(系统代发消息)</span>", qlm_have_read=True,
            zg_have_read=False)
        merge_msg.save()

        # 更新my_interview表
        my_interview = MyInterview(user_id=user_id, job_id=job_details[0].id, last_share_uuid=last_share_uuid)
        my_interview.save()

    else:
        be_interested = be_interested[0]

    be_interested_uuid = be_interested.uuid
    return HttpResponseRedirect("/chat/chat_detail?be_interested_uuid=" + str(be_interested_uuid))


@csrf_exempt
@user_tools.sns_userinfo_with_userinfo
def ajax_send_words(request):
    user_id = request.user_id
    be_interested_uuid = request.POST.get('be_interested_uuid')
    words = request.POST.get('words', '')

    profile = user_tools.get_user_profile_by_user_id(user_id, need_default=False)
    data = ""
    if be_interested_uuid and words:
        be_interesteds = BeInterested.objects.filter(uuid=be_interested_uuid)[:1]
        if be_interesteds:
            conversation = Conversation(be_interested_id=be_interesteds[0].id, user_id=user_id, words=words)
            conversation.save()

            openid = None
            if be_interesteds[0].qlm_user_id != user_id:
                openid = user_tools.get_openid(be_interesteds[0].qlm_user_id)
            else:
                job_details = Job.objects.filter(id=be_interesteds[0].job_id).only('user_id')
                if job_details:
                    openid = user_tools.get_openid(job_details[0].user_id)

            send_notice_tool.send_notice(openid)

            merge_msg = MergeMsg.objects.filter(be_interested_id=be_interesteds[0].id)[0]  # 既然都可以发送了，肯定有这条记录了
            merge_msg.last_words = words
            if be_interesteds[0].qlm_user_id == user_id:  # 说明发送的这个人是千里马
                merge_msg.qlm_have_read = True
                merge_msg.zg_have_read = False
                merge_msg.update_time = datetime.datetime.now()
            else:
                merge_msg.qlm_have_read = False
                merge_msg.zg_have_read = True
                merge_msg.update_time = datetime.datetime.now()
            merge_msg.save()

            data = {'user_portrait': profile.portrait, 'user_nick': user_tools.get_user_name(profile),
                    'words': conversation.words, 'user_uuid': profile.uuid,
                    'vip_display': "block" if profile.vip else "none",
                    'create_time': conversation.create_time.strftime('%Y-%m-%d %H:%M')}
    else:
        log.error("uid(%s) try to get not exsit be_interested_uuid(%s), maybe attack" % (user_id, be_interested_uuid))

    return HttpResponse(json.dumps(data), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def chat(request):
    page_data = {}
    page_data['jsapi'] = jsapi_sign(request)
    template = get_template('chat/chat.html')
    return HttpResponse(template.render(page_data, request))


@user_tools.sns_userinfo_with_userinfo
def get_job_luyin(request):
    template = get_template('job/job_recommend_success.html')
    return HttpResponse(template.render({}, request))


@csrf_exempt
@user_tools.sns_userinfo_with_userinfo
def ajax_collection(request):
    user_id = request.user_id
    is_collected = request.POST.get('is_collected')
    job_uuid = request.POST.get('job_uuid', '')
    last_share_uuid = request.POST.get('last_share_uuid', '000000000000000000000')

    job_details = Job.objects.filter(uuid=job_uuid).only('id')
    data = {'info': "收藏职位"}
    if job_details:
        job_detail = job_details[0]
        data['status'] = "ok"
        if is_collected == '0':  # 收藏
            my_collections = MyCollection.objects.filter(user_id=user_id, job_id=job_detail.id)[:1]
            if not my_collections:
                my_collection = MyCollection(user_id=user_id, job_id=job_detail.id, last_share_uuid=last_share_uuid)
                my_collection.save()
            data['info'] = "取消收藏"
        else:  # 取消收藏
            MyCollection.objects.filter(user_id=user_id, job_id=job_detail.id).delete()
    else:
        data['status'] = "error"
        log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
@user_tools.sns_userinfo_with_userinfo
def ajax_share(request):
    user_id = request.user_id
    share_uuid = request.POST.get('share_uuid', '')
    last_share_uuid = request.POST.get('last_share_uuid', '')
    job_uuid = request.POST.get('job_uuid', '')
    recommend_uuid = request.POST.get('recommend_uuid', '')
    data = ""
    if job_uuid:  # 分享职位详情
        job_details = Job.objects.filter(uuid=job_uuid)[:1]
        if job_details:
            if last_share_uuid:
                shares = Share.objects.filter(uuid=last_share_uuid)[:1]
                if not shares:
                    return HttpResponse("十分抱歉，获取上个人推荐信息失败，请重试。重试失败请联系客服人员")
                last_share_id = shares[0].id
            else:
                last_share_id = 0

            job_share = Share(user_id=user_id, uuid=share_uuid, job_id=job_details[0].id, last_share_id=last_share_id)
            job_share.save()
            data = "ok"
        else:
            log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
            return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    if recommend_uuid:  # 分享带录音的职位详情
        recommends = MyRecommend.objects.filter(uuid=recommend_uuid)[:1]
        if recommends:
            if last_share_uuid:
                shares = Share.objects.filter(uuid=last_share_uuid)[:1]
                if not shares:
                    return HttpResponse("十分抱歉，获取上个人推荐信息失败，请重试。重试失败请联系客服人员")
                last_share_id = shares[0].id
            else:
                last_share_id = 0

            job_share = Share(user_id=user_id, uuid=share_uuid, recommend_id=recommends[0].id,
                last_share_id=last_share_id)
            job_share.save()
            data = "ok"
        else:
            log.error("uid(%s) try to get not exsit recommend(%s), maybe attack" % (user_id, recommend_uuid))
            return HttpResponse("十分抱歉，获取推荐信息失败，请重试。重试失败请联系客服人员")
    return HttpResponse(data, content_type='application/json')

