# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from user.models import Profile, ProfileExt, Bind, WxSubscribe
from django.utils.translation import ugettext_lazy as _


class IsEditListFilter(admin.SimpleListFilter):
    title = _(u"是否编辑了个人信息")
    parameter_name = 'decade'

    def lookups(self, request, model_admin):
        return (
            ('yes', _(u'是')), ("no", _(u'否')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(real_name="")
        if self.value() == 'no':
            return queryset.filter(real_name="")


class IsBindWxFilter(admin.SimpleListFilter):
    title = _(u"是否关注公众号")
    parameter_name = 'is_bind'

    def lookups(self, request, model_admin):
        return (
            ('1', _(u'是')), ("0", _(u'否')),
        )

    def queryset(self, request, queryset):
        # print self.value()
        if self.value() == '1':
            user_ids = []
            for profile in queryset:
                binds = Bind.objects.filter(user_id=profile.id)[:1]
                if binds:
                    bind_wxs = WxSubscribe.objects.filter(wx_openid=binds[0].wx_openid)[:1]
                    if bind_wxs:
                        user_ids.append(binds[0].user_id)
            return queryset.filter(id__in=user_ids)
        if self.value() == '0':
            user_ids = []
            for profile in queryset:
                binds = Bind.objects.filter(user_id=profile.id)[:1]
                if binds:
                    bind_wxs = WxSubscribe.objects.filter(wx_openid=binds[0].wx_openid)[:1]
                    if bind_wxs:
                        user_ids.append(binds[0].user_id)
            return queryset.exclude(id__in=user_ids)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_filter = ('vip', IsEditListFilter, IsBindWxFilter,)
    empty_value_display = '无'

    date_hierarchy = "create_time"
    # ordering = ['-update_time']

    list_display = (
        'id', 'nick', 'real_name', 'get_phone', 'get_bind_wx', 'company_name', 'title', 'vip', 'pub_valid_job_cnt',
        'format_create_time', 'format_update_time')

    search_fields = ('id', 'nick', 'real_name', 'vip', 'company_name')
    readonly_fields = (
        'nick', 'pub_valid_job_cnt', 'real_name', 'company_name', 'title', 'desc', 'sex', 'nation', 'province', 'city',
        'district', 'pub_valid_job_cnt', 'create_time', 'update_time')

    fieldsets = (
        ['用户基本信息',
         {'fields': ('vip', ('nick', 'real_name',), ('company_name', 'title',), 'desc', 'pub_valid_job_cnt'), }],
        ['用户其他信息', {  # 'classes': ('wide',), # CSS
                      'fields': ('sex', ('nation', 'province', 'city', 'district'), 'pub_valid_job_cnt',
                                 ('create_time', 'update_time'),), }]
    )

    def format_create_time(self, obj):
        return obj.create_time.strftime('%Y-%m-%d %H:%M')

    format_create_time.short_description = "创建时间"

    def format_update_time(self, obj):
        return obj.update_time.strftime('%Y-%m-%d %H:%M')

    format_update_time.short_description = "更新时间"

    def get_phone(self, obj):
        binds = Bind.objects.filter(user_id=obj.id)[:1]
        if binds:
            return binds[0].phone_number
        else:
            return ""

    get_phone.short_description = "手机"

    def get_bind_wx(self, obj):
        binds = Bind.objects.filter(user_id=obj.id)[:1]
        if binds:
            bind_wxs = WxSubscribe.objects.filter(wx_openid=binds[0].wx_openid)[:1]
            if bind_wxs:
                return True
        return False

    get_bind_wx.short_description = "关注公众号"
    get_bind_wx.boolean = True


