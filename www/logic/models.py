# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from user.models import Profile
from django.utils import timezone

# Create your models here.

class Job(models.Model):
    uuid = models.CharField(max_length=36, db_index=True)
    user_id = models.IntegerField(db_index=True)
    company_name = models.CharField(max_length=30)
    job_title = models.CharField(max_length=30)
    work_experience = models.CharField(max_length=10)
    salary = models.CharField(max_length=10)
    education = models.CharField(max_length=10)
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    district = models.CharField(max_length=20, default='')
    skill = models.CharField(max_length=120)
    piclist = models.CharField(max_length=256)
    is_valid = models.BooleanField(default=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "job"

    def __unicode__(self):
        return self.job_title


# 请确定已有的会更新时间
class VipJobList(models.Model):
    job_id = models.IntegerField()
    user_id = models.IntegerField(primary_key=True)
    pub_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        db_table = "job_for_vip_list"


# 1. 职位详情页面的分享回调; 2. 发送录用成功后的页面的分享回调；3. 我的推荐记录里的详情分享回调（忽略对主公的分享）；
class Share(models.Model):
    uuid = models.CharField(max_length=36, db_index=True)
    user_id = models.IntegerField(db_index=True)
    job_id = models.IntegerField(db_index=True, default=0)
    last_share_id = models.IntegerField(default=0)
    recommend_id = models.IntegerField(db_index=True, default=0)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "job_share"


class BeInterested(models.Model):
    uuid = models.CharField(max_length=36, db_index=True,default='00000000000000000000000000000000')
    last_share_uuid = models.CharField(max_length=36, db_index=True, default='00000000000000000000000000000000')
    job_id = models.IntegerField(db_index=True)
    qlm_user_id = models.IntegerField(db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "be_interested"


class Conversation(models.Model):
    be_interested_id = models.IntegerField(db_index=True)
    user_id = models.IntegerField()
    words = models.CharField(max_length=120)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conversation"


class MergeMsg(models.Model):
    uuid = models.CharField(max_length=36, db_index=True,default='00000000000000000000000000000000')
    zg_user_id = models.IntegerField()
    bl_user_id = models.IntegerField(default=0)
    qlm_user_id = models.IntegerField(db_index=True, default=0)
    recommend_id = models.IntegerField(default=0)
    be_interested_id = models.IntegerField(default=0)
    last_words = models.CharField(max_length=120, default='')
    zg_have_read = models.BooleanField(default=False)
    qlm_have_read = models.BooleanField(default=False)
    update_time = models.DateTimeField()
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        index_together = ("zg_user_id", "bl_user_id", "recommend_id")
        index_together = ("zg_user_id", "qlm_user_id", "be_interested_id")
        db_table = "merge_msg"
