# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Profile(models.Model):
    #####################################
    uuid = models.CharField(max_length=36, db_index=True)
    nick = models.CharField(max_length=20)
    sex = models.CharField(choices=(('F', 'Female'), ('M', 'Male'), ('O', 'Other')), max_length=1)
    portrait = models.CharField(max_length=256)
    real_name = models.CharField(max_length=20)
    company_name = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    vip = models.BooleanField(default=False)
    desc = models.CharField(max_length=150, default='')
    nation = models.CharField(max_length=20, default='')
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    district = models.CharField(max_length=20, default='')
    pub_valid_job_cnt = models.IntegerField(default=0)
    ################# 以上是概要信息部分 #####
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_profile"

    def __unicode__(self):
        return self.nick


class ProfileExt(models.Model):
    user_id = models.IntegerField(db_index=True)
    education = models.CharField(max_length=40)
    blood_type = models.CharField(max_length=3)
    birthday = models.DateField()
    certificate_no = models.CharField(max_length=40)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_profile_ext"


class Bind(models.Model):
    user_id = models.IntegerField(db_index=True)
    phone_number = models.CharField(max_length=20, db_index=True)
    phone_number_verify_time = models.DateTimeField()
    wx_openid = models.CharField(max_length=36, db_index=True)
    wx_openid_verify_time = models.DateTimeField()
    qq_openid = models.CharField(max_length=20, db_index=True)
    qq_openid_verify_time = models.DateTimeField()
    weibo_openid = models.CharField(max_length=20, db_index=True)
    weibo_openid_verify_time = models.DateTimeField()
    email = models.CharField(max_length=40, db_index=True)
    email_verify_time = models.DateTimeField()
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_bind"


class WxSubscribe(models.Model):
    wx_openid = models.CharField(max_length=36, db_index=True)
    wx_subscribed = models.BooleanField(default=False)

    class Meta:
        db_table = "wx_subscribe"


class MyCollection(models.Model):
    user_id = models.IntegerField(db_index=True)
    last_share_uuid = models.CharField(max_length=36, db_index=True, default='00000000000000000000000000000000')
    job_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "my_collection"


class MyRecommend(models.Model):
    uuid = models.CharField(max_length=36, db_index=True, default='')
    last_share_uuid = models.CharField(max_length=36, db_index=True, default='00000000000000000000000000000000')
    user_id = models.IntegerField()
    job_id = models.IntegerField()
    audio_for_zg = models.CharField(max_length=80, default='')
    audio_for_qlm = models.CharField(max_length=80, default='')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = ("user_id", "job_id")
        db_table = "my_recommend"


class MyRecommendMerg(models.Model):
    user_id = models.IntegerField()
    job_id = models.IntegerField()
    recommend_num = models.IntegerField()
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user_id", "job_id")
        db_table = "my_recommend_merg"


class MyInterview(models.Model):
    user_id = models.IntegerField(db_index=True)
    last_share_uuid = models.CharField(max_length=36, db_index=True, default='00000000000000000000000000000000')
    job_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "my_interview"
