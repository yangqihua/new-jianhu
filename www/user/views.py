# -*- coding: utf-8 -*-
import json
import user_tools
from logic import logic_tools
from common.sys_config import log
from django.utils import html
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from user.models import Profile, MyCollection, MyRecommend, MyRecommendMerg, MyInterview, Bind
from logic.models import Job, VipJobList
from common import convert, str_tools
from django.forms.models import model_to_dict
from wx_base.wx_tools import jsapi_sign


@user_tools.sns_userinfo_with_userinfo
def recommand_list(request):
    user_id = request.user_id
    recommend_job_from_point = convert.str_to_int(request.GET.get('from', '0'), 0)  # 有from时，则为翻页，无时，则为首页
    number_limit = convert.str_to_int(request.GET.get('limit', '10'), 10)  # 异常情况下，或者不传的情况下，默认为10

    recommend_job_list = []
    user_info_map = {}

    my_recommend_merges = MyRecommendMerg.objects.filter(user_id=user_id).order_by('update_time')[
                          recommend_job_from_point:number_limit + recommend_job_from_point]

    job_id_list = [job.job_id for job in my_recommend_merges]
    recommend_jobs = Job.objects.filter(id__in=list(set(job_id_list)))
    user_id_list = [job.user_id for job in recommend_jobs]
    profiles = Profile.objects.filter(id__in=list(set(user_id_list)))
    user_id_to_profile = {}
    for profile in profiles:
        user_id_to_profile[profile.id] = profile

    for recommend_job in recommend_jobs:
        profile = user_id_to_profile[recommend_job.user_id]
        my_recommend_merge = [my_recommend_merge for my_recommend_merge in my_recommend_merges if
                              my_recommend_merge.job_id == recommend_job.id]
        job_addr = recommend_job.city + " " + recommend_job.district
        job = {'job_city': recommend_job.city, 'job_addr': job_addr, 'company_name': recommend_job.company_name,
               'job_title': recommend_job.job_title, 'education': recommend_job.education,
               'work_experience': recommend_job.work_experience, 'salary': recommend_job.salary,
               'create_time': convert.format_time(recommend_job.create_time),
               'username': user_tools.get_user_name(profile), 'portrait': profile.portrait,
               'job_uuid': recommend_job.uuid, 'user_company': profile.company_name,
               'recommend_num': my_recommend_merge[0].recommend_num, 'vip_display': 'block' if profile.vip else 'none'}
        user_info_map[recommend_job.uuid] = user_tools.get_userinfomap(profile)
        recommend_job_list.insert(0, job)

    if recommend_job_from_point == 0:  # 首页，需要返回页面
        page_data = {'recommend_job_list': json.dumps(recommend_job_list), 'user_info_map': json.dumps(user_info_map),
                     'jsapi': jsapi_sign(request)}
        template = get_template('user/recommand_list.html')
        return HttpResponse(template.render(page_data, request))
    else:  # 加载下一页，ajax请求
        page_data = {'recommend_job_list': recommend_job_list, 'user_info_map': user_info_map}
        return HttpResponse(json.dumps(page_data), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def ajax_recommend_record_list(request):
    user_id = request.user_id
    job_uuid = request.GET.get('job_uuid', '')
    job_detail = Job.objects.filter(uuid=job_uuid)[:1]
    if not job_detail:
        log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
        return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    my_recommend_list = MyRecommend.objects.filter(user_id=user_id, job_id=job_detail[0].id).order_by('-id')[:20]
    if not my_recommend_list:
        return HttpResponse("十分抱歉，您还没有推荐该职位，请重试。重试失败请联系客服人员")

    recommand_list = []
    for my_recommend in my_recommend_list:
        recommend = {'uuid': my_recommend.uuid, 'last_share_uuid': my_recommend.last_share_uuid,
                     'create_time': my_recommend.create_time.strftime('%Y-%m-%d %H:%M')}
        recommand_list.append(recommend)

    my_recommend_info = {'job_title': job_detail[0].job_title, 'recommend_num': len(my_recommend_list),
                         "my_recommend_list": recommand_list}
    return HttpResponse(json.dumps(my_recommend_info), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def collection_list(request):
    user_id = request.user_id
    job_from_point = convert.str_to_int(request.GET.get('from', '0'), 0)  # 有from时，则为翻页，无时，则为首页
    number_limit = convert.str_to_int(request.GET.get('limit', '10'), 10)  # 异常情况下，或者不传的情况下，默认为10

    collections = MyCollection.objects.filter(user_id=user_id).order_by('-id')[
                  job_from_point:number_limit + job_from_point]

    job_id_to_last_share_uuid = {}
    for collection in collections:
        job_id_to_last_share_uuid[collection.job_id] = collection.last_share_uuid

    job_id_list = [collection.job_id for collection in collections]
    collection_jobs = Job.objects.filter(id__in=list(set(job_id_list)))

    user_id_list = [job.user_id for job in collection_jobs]
    profiles = Profile.objects.filter(id__in=list(set(user_id_list)))
    user_id_to_profile = {}
    for profile in profiles:
        user_id_to_profile[profile.id] = profile

    collection_job_list = []
    user_info_map = {}
    for collection_job in collection_jobs:
        profile = user_id_to_profile[collection_job.user_id]
        job_addr = collection_job.city + " " + collection_job.district
        job = {'job_city': collection_job.city, 'job_addr': job_addr, 'company_name': collection_job.company_name,
               'job_title': collection_job.job_title, 'education': collection_job.education,
               'work_experience': collection_job.work_experience, 'salary': collection_job.salary,
               'create_time': convert.format_time(collection_job.create_time),
               'username': user_tools.get_user_name(profile), 'portrait': profile.portrait,
               'job_uuid': collection_job.uuid, 'user_company': profile.company_name,
               'last_share_uuid': job_id_to_last_share_uuid[collection_job.id],
               'vip_display': 'block' if profile.vip else 'none'}

        user_info_map[collection_job.uuid] = user_tools.get_userinfomap(profile)
        collection_job_list.append(job)

    collection_job_list.reverse()
    if job_from_point == 0:  # 首页，需要返回页面
        page_data = {'collection_job_list': json.dumps(collection_job_list), 'user_info_map': json.dumps(user_info_map),
                     'jsapi': jsapi_sign(request)}
        template = get_template('user/collection_list.html')
        return HttpResponse(template.render(page_data, request))
    else:  # 加载下一页，ajax请求
        page_data = {'collection_job_list': collection_job_list, 'user_info_map': user_info_map}
        return HttpResponse(json.dumps(page_data), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def fabu_list(request):
    user_id = request.user_id
    user_uuid = request.GET.get('user_uuid', '')
    if user_uuid:  # 查某人的所有职位
        profile = Profile.objects.filter(uuid=user_uuid)[:1]
        if profile:
            profile = profile[0]
            if profile.id == user_id:
                page_title = "我的发布"
            else:
                page_title = "他的发布"
            user_id = profile.id
        else:
            log.error('Cant find user profile by user_id: %s when fabu_list' % user_id)
            return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")
    else:  # 查自己发过的所有职位
        profile = user_tools.get_user_profile_by_user_id(user_id=user_id, need_default=False)
        page_title = "我的发布"
        if not profile:
            log.error('Cant find user profile by user_id: %s when fabu_list' % user_id)
            return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")

    job_from_point = convert.str_to_int(request.GET.get('from', '0'), 0)  # 有from时，则为翻页，无时，则为首页
    number_limit = convert.str_to_int(request.GET.get('limit', '10'), 10)  # 异常情况下，或者不传的情况下，默认为10

    jobs = Job.objects.filter(user_id=user_id).order_by('-id')[job_from_point:number_limit + job_from_point]
    own_job_list = []
    user_info_map = {}
    for my_job in jobs:
        job_addr = my_job.city + " " + my_job.district
        job = {'job_uuid': my_job.uuid, 'job_city': my_job.city, 'job_addr': job_addr,
               'company_name': my_job.company_name, 'job_title': my_job.job_title, 'education': my_job.education,
               'work_experience': my_job.work_experience, 'salary': my_job.salary,
               'create_time': convert.format_time(my_job.create_time), 'username': user_tools.get_user_name(profile),
               'portrait': profile.portrait, 'user_company': profile.company_name}
        own_job_list.append(job)
        user_info_map[my_job.uuid] = user_tools.get_userinfomap(profile)

    vip_display = 'block' if user_tools.get_userinfomap(profile)['vip'] else 'none'
    if job_from_point == 0:  # 首页，需要返回页面
        page_data = {'vip_display': vip_display, 'own_job_list': json.dumps(own_job_list),
                     'vip_job_list': json.dumps([]), 'user_info_map': json.dumps(user_info_map),
                     'jsapi': jsapi_sign(request), 'page_title': page_title, "user_uuid": user_uuid}
        page_data = user_tools.get_isbind_and_isedit(None, request, page_data)
        template = get_template('user/fabu_list.html')
        return HttpResponse(template.render(page_data, request))
    else:  # 加载下一页，ajax请求
        page_data = {'own_job_list': own_job_list, 'vip_job_list': json.dumps([]), 'user_info_map': user_info_map}
        return HttpResponse(json.dumps(page_data), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def recommand_detail(request):
    recommend_uuid = request.GET.get('recommend_uuid', '')
    my_recommend = MyRecommend.objects.filter(uuid=recommend_uuid)[:1]

    if not my_recommend:
        log.error('Cant find recommend by recommend_uuid: %s' % recommend_uuid)
        return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")

    page_data = logic_tools.get_job_detail(my_recommend[0].job_id)
    logic_tools.fullfill_recommend_detail(page_data, my_recommend[0], True, True)

    page_data['last_share_uuid'] = my_recommend[0].last_share_uuid

    page_data['jsapi'] = jsapi_sign(request)

    page_data = user_tools.get_isbind_and_isedit(None, request, page_data)
    template = get_template('user/recommand_detail.html')
    return HttpResponse(template.render(page_data, request))


@user_tools.sns_userinfo_with_userinfo
def fabu_detail(request):
    user_id = request.user_id

    user_info_map = {}
    job_uuid = request.GET.get('job_uuid', '')
    job_detail = Job.objects.filter(uuid=job_uuid)[0]

    if job_detail:
        if user_id != job_detail.user_id:
            return HttpResponseRedirect("/job/get_job?job_uuid=" + job_uuid)

        profile = user_tools.get_user_profile_by_user_id(user_id=user_id, need_default=True)

        page_data = model_to_dict(job_detail, exclude=['id', 'user_id', 'create_time', 'update_time', ])
        page_data['job_addr'] = job_detail.city + " " + job_detail.district
        page_data['job_city'] = job_detail.city
        page_data['portrait'] = profile.portrait
        page_data['username'] = user_tools.get_user_name(profile)
        page_data['user_company'] = profile.company_name
        page_data['user_uuid'] = profile.uuid
        page_data['user_title_count'] = profile.pub_valid_job_cnt
        user_info_map[page_data['uuid']] = user_tools.get_userinfomap(profile)

    else:
        log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))
        return HttpResponse("十分抱歉，获取职位信息失败，请重试。重试失败请联系客服人员")

    page_data['vip_display'] = 'block' if profile.vip else 'none'
    page_data['user_info_map'] = json.dumps(user_info_map)
    page_data['jsapi'] = jsapi_sign(request)


    page_data['post_success'] = 0
    page_data['last_share_uuid'] = '00000000000000000000000000000000'
    page_data = user_tools.get_isbind_and_isedit(None, request, page_data)


    template = get_template('user/fabu_detail.html')
    return HttpResponse(template.render(page_data, request))


@user_tools.sns_userinfo_with_userinfo
def interview_list(request):
    user_id = request.user_id
    interview_job_from_point = convert.str_to_int(request.GET.get('from', '0'), 0)  # 有from时，则为翻页，无时，则为首页
    number_limit = convert.str_to_int(request.GET.get('limit', '10'), 10)  # 异常情况下，或者不传的情况下，默认为10

    interview_job_list = []
    user_info_map = {}

    my_interviews = MyInterview.objects.filter(user_id=user_id).order_by('-id')[
                    interview_job_from_point:number_limit + interview_job_from_point]

    job_id_list = [job.job_id for job in my_interviews]
    interview_jobs = Job.objects.filter(id__in=list(set(job_id_list)))

    user_id_list = [job.user_id for job in interview_jobs]
    profiles = Profile.objects.filter(id__in=list(set(user_id_list)))
    user_id_to_profile = {}
    for profile in profiles:
        user_id_to_profile[profile.id] = profile

    for interview_job in interview_jobs:
        profile = user_id_to_profile[interview_job.user_id]
        job_addr = interview_job.city + " " + interview_job.district
        job = {'job_city': interview_job.city, 'job_addr': job_addr, 'company_name': interview_job.company_name,
               'job_title': interview_job.job_title, 'education': interview_job.education,
               'work_experience': interview_job.work_experience, 'salary': interview_job.salary,
               'create_time': convert.format_time(interview_job.create_time),
               'username': user_tools.get_user_name(profile), 'portrait': profile.portrait,
               'job_uuid': interview_job.uuid, 'user_company': profile.company_name,
               'vip_display': 'block' if profile.vip else 'none'}
        user_info_map[interview_job.uuid] = user_tools.get_userinfomap(profile)
        interview_job_list.append(job)

    interview_job_list.reverse()
    if interview_job_from_point == 0:  # 首页，需要返回页面
        page_data = {'interview_job_list': json.dumps(interview_job_list), 'user_info_map': json.dumps(user_info_map),
                     'jsapi': jsapi_sign(request)}

        template = get_template('user/yinping_list.html')
        return HttpResponse(template.render(page_data, request))
    else:  # 加载下一页，ajax请求
        page_data = {'interview_job_list': interview_job_list, 'user_info_map': user_info_map}
        return HttpResponse(json.dumps(page_data), content_type='application/json')


@user_tools.sns_userinfo_with_userinfo
def edit_userinfo(request):
    user_id = request.user_id
    profile = user_tools.get_user_profile_by_user_id(user_id=user_id, need_default=False)
    if not profile:
        log.error('Cant find user profile by user_id: %s when edit_userinfo' % user_id)
        return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")

    info = {'title': '编辑信息'}

    user_bind = Bind.objects.filter(user_id=user_id)[:1]
    if not user_bind:
        return HttpResponse("十分抱歉，您还没有任何绑定方式")

    page_data = {'phone_number': user_bind[0].phone_number,
                 'user_info_map': json.dumps(user_tools.get_userinfomap(profile)), 'jsapi': jsapi_sign(request),
                 'info': json.dumps(info)}

    template = get_template('user/edit_userinfo.html')
    return HttpResponse(template.render(page_data, request))


@user_tools.sns_userinfo_with_userinfo
def post_userinfo(request):
    user_id = request.user_id
    profile = user_tools.get_user_profile_by_user_id(user_id=user_id, need_default=False)
    if not profile:
        return HttpResponse("十分抱歉，获取用户信息失败，请联系客服人员")

    user_bind = Bind.objects.filter(user_id=user_id)[:1]
    if not user_bind:
        return HttpResponse("十分抱歉，您还没有任何绑定方式")

    profile.real_name = html.escape(request.POST.get('real_name'))[:20]
    profile.company_name = html.escape(request.POST.get('company_name'))[:30]
    profile.title = html.escape(request.POST.get('title'))[:30]
    profile.desc = html.escape(request.POST.get('jianli'))[:150]
    user_addr = html.escape(request.POST.get('user_addr')).split(' ')
    if len(user_addr) > 1:
        profile.province = user_addr[0][:20]
        profile.city = user_addr[1][:20]
        if len(user_addr) == 3:
            profile.district = user_addr[2][:20]

    profile.save()

    user_bind[0].phone_number = html.escape(request.POST.get('phone'))[:20]
    user_bind[0].save()
    return HttpResponseRedirect('/user/me')


@user_tools.sns_userinfo_with_userinfo
def me(request):
    user_id = request.user_id
    profile = user_tools.get_user_profile_by_user_id(user_id=user_id, need_default=False)
    if not profile:
        log.error('Cant find user profile by user_id: %s when me' % user_id)
        return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")

    user_info_map = user_tools.get_userinfomap(profile)
    if profile.real_name == '':
        page_data = {'user_info_map': json.dumps(user_info_map), 'jsapi': jsapi_sign(request),
                     'info': json.dumps({'title': '完善资料'})}
        template = get_template('user/edit_userinfo.html')
        return HttpResponse(template.render(page_data, request))

    vip_display = 'block' if user_info_map['vip'] else 'none'
    page_data = {'vip_display': vip_display, 'user_info_map': json.dumps(user_info_map), 'jsapi': jsapi_sign(request)}
    template = get_template('user/me.html')
    return HttpResponse(template.render(page_data, request))


@csrf_exempt
@user_tools.sns_userinfo_with_userinfo
def ajax_toggle_job(request):
    user_id = request.user_id
    is_valid = request.POST.get('is_valid')
    job_uuid = request.POST.get('job_uuid', '')

    profile = user_tools.get_user_profile_by_user_id(user_id=user_id, need_default=False)
    if not profile:
        log.error('Cant find user profile by user_id: %s when ajax_toggle_job' % user_id)
        return HttpResponse("十分抱歉，获取用户信息失败，请重试。重试失败请联系客服人员")

    job_details = Job.objects.filter(uuid=job_uuid)
    data = {'status': "error"}
    if job_details:
        job_detail = job_details[0]
        if is_valid == '1':  # 有效改为无效
            data['status'] = "ok"
            data['valid'] = '0'
            job_detail.is_valid = False
            job_detail.save()

            vip_jobs = VipJobList.objects.filter(job_id=job_detail.id)[:1]
            if vip_jobs:  # 如果关闭的这个job是vip_job
                # 取最近一条有效的job插到vip_job里面去
                recent_jobs = Job.objects.filter(user_id=user_id, is_valid=True).order_by("-id")[:1]
                if recent_jobs:
                    vip_jobs[0].job_id = recent_jobs[0].id
                    vip_jobs[0].save()
                else:  # 没有最近发布的有效的job了，删vip_job
                    vip_jobs[0].delete()

        else:  # 无效改为有效
            data['status'] = "ok"
            data['valid'] = '1'
            job_detail.is_valid = True
            job_detail.save()

            vip_jobs = VipJobList.objects.filter(user_id=user_id)[:1]
            if vip_jobs:  # 如果存在vip_job，则修改job_id
                # 取最近一条有效的job插到vip_job里面去
                recent_jobs = Job.objects.filter(user_id=user_id, is_valid=True).order_by("-id")[:1]
                vip_jobs[0].job_id = recent_jobs[0].id  # 这里肯定可以取到recent_jobs
                vip_jobs[0].save()
            elif profile.vip:  # 没有则插入
                vip_job = VipJobList(job_id=job_detail.id, user_id=user_id)
                vip_job.save()

    else:
        log.error("uid(%s) try to get not exsit job(%s), maybe attack" % (user_id, job_uuid))

    return HttpResponse(json.dumps(data), content_type='application/json')

