# -*- coding: utf-8 -*-

import json
from common import convert
from common.sys_config import log
from logic.models import Share, Job
from user.models import Profile
from user import user_tools
from django.forms.models import model_to_dict


def fullfill_recommend_detail(page_data, my_recommend, need_audio_4_zg, need_audio_4_qlm):
    if not my_recommend:
        return

    profile = Profile.objects.filter(id=my_recommend.user_id)[:1]
    if not profile:
        log.error("no profile id by my_recommend user_id: %s" % my_recommend.user_id)
        return

    page_data['recommend_audio_4_qlm'] = ''
    page_data['recommend_audio_length_4_qlm'] = ''

    page_data['recommend_audio_4_zg'] = ''
    page_data['recommend_audio_length_4_zg'] = ''
    # 推荐的相关信息start
    if need_audio_4_zg:
        recommend_audio = my_recommend.audio_for_zg.split(",")
        page_data['recommend_audio_4_zg'] = recommend_audio[0]
        page_data['recommend_audio_length_4_zg'] = recommend_audio[1]
        page_data['share_to'] = 'zg'

    if need_audio_4_qlm:
        recommend_audio = my_recommend.audio_for_qlm.split(",")
        page_data['recommend_audio_4_qlm'] = recommend_audio[0]
        page_data['recommend_audio_length_4_qlm'] = recommend_audio[1]
        page_data['share_to'] = 'qlm'

    page_data['bole_name'] = user_tools.get_user_name(profile[0])
    page_data['bole_portrait'] = profile[0].portrait
    page_data['bole_user_info_map'] = json.dumps(user_tools.get_userinfomap(profile[0]))
    page_data['recommend_expire_time'] = convert.format_expire_time(my_recommend.create_time)
    page_data['recommend_uuid'] = my_recommend.uuid

    page_data['bl_vip_display'] = "block" if profile[0].vip else "none"


def get_job_detail(job_id):
    job_details = Job.objects.filter(id=job_id)[:1]

    if not job_details:
        log.error("no job_details id by job_id: %s" % job_id)
        return None

    page_data = model_to_dict(job_details[0], exclude=['id', 'user_id', 'is_valid', 'create_time', 'update_time', ])

    page_data['job_addr'] = job_details[0].city + " " + job_details[0].district
    page_data['job_city'] = job_details[0].city

    profile = user_tools.get_user_profile_by_user_id(user_id=job_details[0].user_id, need_default=True)
    page_data['username'] = user_tools.get_user_name(profile)
    page_data['portrait'] = profile.portrait
    page_data['user_company'] = profile.company_name
    page_data['user_uuid'] = profile.uuid
    page_data['user_title_count'] = len(Job.objects.filter(user_id=profile.id))
    page_data['user_info_map'] = json.dumps({job_details[0].uuid: user_tools.get_userinfomap(profile)})
    page_data['vip_display'] = "block" if profile.vip else "none"
    return page_data


