# coding=utf8
"""www URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.contrib import admin

import views
import wx_views
from user import views as user_views
from logic import views as logic_views

urlpatterns = [

    url(r'^get_job$', logic_views.get_job, name='get_job'),  #职位详情
    url(r'^get_job_luyin$', logic_views.get_job_luyin, name='get_job_luyin'),  #带录音的职位详情

    url(r'^post_res_for_job$', logic_views.post_res_for_job, name='post_res_for_job'),  #发布职位前上传图片
    url(r'^post_job$', logic_views.post_job, name='post_job'),  #提交表单，发布职位
    url(r'^fabu_job$', logic_views.fabu_job, name='fabu_job'),  #发布职位
    url(r'^recommand_job$', logic_views.recommand_job, name='recommand_job'),  #推荐职位
    url(r'^post_recommand_job$', logic_views.post_recommand_job, name='post_recommand_job'),  #提交推荐表单
    url(r'^post_recommand_job_success$', logic_views.post_recommand_job_success, name='post_recommand_job_success'),  #成功推荐

    url(r'^get_chat_list$', logic_views.get_chat_list, name='get_chat_list'),  #首页消息
    url(r'^chat_detail$', logic_views.chat_detail, name='chat_detail'),  #消息内容
    url(r'^interest_job$', logic_views.interest_job, name='interest_job'),  #我感兴趣
    url(r'^ajax_send_words$', logic_views.ajax_send_words, name='ajax_send_words'),  #发送聊天消息

    url(r'^ajax_collection$', logic_views.ajax_collection, name='ajax_collection'),  #收藏的ajax操作
    url(r'^ajax_share$', logic_views.ajax_share, name='ajax_share'),  #分享的ajax操作
     ]
