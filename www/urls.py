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

from django.conf.urls import url, include
from django.contrib import admin

import views
import wx_views
from logic import views as logic_views

urlpatterns = [url(r'^admin/', admin.site.urls), url(r'^ping$', views.ping),  # 测试
               url(r'^$', logic_views.pc_index),  # PC首页
               url(r'^index$', logic_views.index),  # 微信首页
               url(r'^wx_io$', wx_views.wx_io),  # 微信消息、事件接口
               url(r'^openid$', wx_views.oauth),  # 获取用户的openid
               url(r'^job/', include('logic.urls')),  # 工作相关
               url(r'^chat/', include('logic.urls')),  # 留言
               url(r'^user/', include('user.urls')),  # 用户相关
               ]
