# -*- coding: utf-8 -*-
from django.contrib import admin

from logic.models import Job,Share
# Register your models here.


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    date_hierarchy = "create_time"

    # actions_selection_counter = True

    # actions_on_buttom = True
    # actions_on_top = False
    empty_value_display = '无'

    ordering = ['-update_time']

    list_display = ('id', 'user_id', 'company_name', 'job_title', 'city', 'is_valid', 'format_create_time', 'format_update_time')
    search_fields = ('id', 'user_id', 'company_name', 'job_title', 'city')
    readonly_fields = Job._meta.get_all_field_names()

    def format_create_time(self, obj):
        return obj.create_time.strftime('%Y-%m-%d %H:%M')
    format_create_time.short_description = "创建时间"

    def format_update_time(self, obj):
        return obj.update_time.strftime('%Y-%m-%d %H:%M')
    format_update_time.short_description = "更新时间"

@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    date_hierarchy = "create_time"

    # actions_selection_counter = True

    # actions_on_buttom = True
    # actions_on_top = False
    empty_value_display = '无'

    ordering = ['-update_time']

    list_display = ('id', 'user_id', 'recommend_id', 'job_id', 'last_share_id', 'format_create_time', 'format_update_time')
    search_fields = ('id', 'user_id','last_share_id',)
    readonly_fields = Share._meta.get_all_field_names()

    def format_create_time(self, obj):
        return obj.create_time.strftime('%Y-%m-%d %H:%M')
    format_create_time.short_description = "创建时间"

    def format_update_time(self, obj):
        return obj.update_time.strftime('%Y-%m-%d %H:%M')
    format_update_time.short_description = "更新时间"
