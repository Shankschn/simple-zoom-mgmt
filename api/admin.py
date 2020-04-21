import datetime

from django.contrib import admin, messages
from django.utils.html import format_html

from import_export.admin import ImportExportActionModelAdmin, ImportExportModelAdmin
# Register your models here.
from api.mail import send_mail
from api.models import *
from api.zoom import *
from api.simpletime import *

admin.site.site_title = 'Zoom 会议室管理'
admin.site.site_header = 'Zoom 会议室管理'
admin.site.index_title = 'Zoom 会议室管理'


@admin.register(BasicSetting)
class BasicSettingAdmin(ImportExportModelAdmin):
    list_display = ['zh', 'mm', 'name', 'smtp_server']


@admin.register(Host)
class HostAdmin(ImportExportModelAdmin):
    list_display = ['account', 'name', 'password', 'host_type',
                    'url', 'capacity', 'level', 'host_password', 'remark']
    save_as = True


def colour_is_or_no(status, zfc):
    if status == 1:
        return format_html('<span style="color:green">{}</span>', zfc)
    else:
        return format_html('<span style="color:red">{}</span>', zfc)


@admin.register(Meeting)
class MeetingAdmin(ImportExportModelAdmin):
    list_display = ['id', 'color_topic', 'host', 'room_id', 'room_password', 'color_request_status',
                    'color_status', 'color_level', 'real_start_time', 'real_end_time', 'requester',
                    'people', 'color_is_mail_all', 'color_is_mail_success', 'color_room_is_delete',
                    'start_time', 'end_time'
                    ]
    exclude = ['real_start_time', 'real_end_time']
    actions = ['meeting_get_host', 'meeting_create', 'zf_room', 'send_mails']
    ordering = ['-real_start_time']
    list_per_page = 15

    def color_request_status(self, obj):
        # print(type(obj), obj)
        if obj.request_status == 1:
            return format_html('<span style="color:green">{}</span>', obj.get_request_status_display())
        else:
            return format_html('<span style="color:red">{}</span>', obj.get_request_status_display())
    color_request_status.short_description = "会议请求状态"
    color_request_status.admin_order_field = 'request_status'

    def color_status(self, obj):
        # print(type(obj), obj)
        if obj.status == 1:
            return format_html('<span style="color:green">{}</span>', obj.get_status_display())
        else:
            return format_html('<span style="color:red">{}</span>', obj.get_status_display())
    color_status.short_description = "Room 会议状态"
    color_status.admin_order_field = 'status'

    def color_level(self, obj):
        # print(type(obj), obj)
        if obj.level == 0:
            return format_html('<span style="color:black">{}</span>', obj.get_level_display())
        if obj.level == 1:
            return format_html('<span style="color:green">{}</span>', obj.get_level_display())
        elif obj.level == 2:
            return format_html('<span style="color:orange">{}</span>', obj.get_level_display())
        elif obj.level == 3:
            return format_html('<span style="color:red">{}</span>', obj.get_level_display())
    color_level.short_description = "会议级别"
    color_level.admin_order_field = 'level'

    def color_topic(self, obj):
        # print(type(obj), obj)
        x = is_in_today(obj.real_end_time)
        if x == 0:
            return format_html('<span style="color:gray">{}</span>', obj.topic)
        elif x == 1:
            return format_html('<span style="color:green">{}</span>', obj.topic)
        elif x == 2:
            return format_html('<span style="color:orange">{}</span>', obj.topic)
        else:
            return format_html('<span style="color:red">{}</span>', obj.topic)
    color_topic.short_description = "会议主题"
    color_topic.admin_order_field = 'topic'

    def color_is_mail_all(self, obj):
        # print(type(obj), obj)
        return colour_is_or_no(obj.is_mail_all, obj.get_is_mail_all_display())
    color_is_mail_all.short_description = "是否发送会议信息至参会人"
    color_is_mail_all.admin_order_field = 'is_mail_all'

    def color_is_mail_success(self, obj):
        # print(type(obj), obj)
        return colour_is_or_no(obj.is_mail_success, obj.get_is_mail_success_display())
    color_is_mail_success.short_description = "是否发送会议信息至参会人"
    color_is_mail_success.admin_order_field = 'is_mail_success'

    def color_room_is_delete(self, obj):
        # print(type(obj), obj)
        return colour_is_or_no(obj.room_is_delete, obj.get_room_is_delete_display())
    color_room_is_delete.short_description = "是否发送会议信息至参会人"
    color_room_is_delete.admin_order_field = 'room_is_delete'

    def meeting_get_host(self, request, queryset):
        for meeting in queryset:
            meeting = get_host(meeting)
            print(meeting)
            if meeting.request_status == 1:
                messages.success(request, '会议：{}，获取主持人成功.'.format(meeting.topic))
            else:
                messages.error(request, '会议：{}，获取主持人失败.'.format(meeting.topic))
    meeting_get_host.short_description = '获取主持人'



    def save_model(self, request, obj, form, change):
        bs = BasicSetting.objects.first()
        if obj.enable_early_time == 1:
            # print(type(obj.start_time))
            # return
            print(bs.early_time)
            obj.real_start_time = obj.start_time - datetime.timedelta(hours=bs.early_time)
        if obj.enable_delay_time == 1:
            obj.real_end_time = obj.end_time + datetime.timedelta(hours=bs.delay_time)
        obj.save()

    def meeting_create(self, request, queryset):
        for meeting in queryset:
            meeting = create_room(meeting)
            print(meeting.request_status, meeting)
            if meeting.request_status == 1:
                messages.success(request, '会议：{}，创建 Zoom 会议室成功.'.format(meeting.topic))
            else:
                messages.error(request, '会议：{}，获取 Zoom 会议室失败.'.format(meeting.topic))
    meeting_create.short_description = '创建 Zoom'

    def send_mails(self, request, queryset):
        for meeting in queryset:
            meeting = send_mail(meeting)
            print(meeting.request_status, meeting)
            if meeting.is_mail_success == 1:
                messages.success(request, '会议：{}，发送通知邮件：成功.'.format(meeting.topic))
            else:
                messages.error(request, '会议：{}，发送通知邮件：失败.'.format(meeting.topic))
    send_mails.short_description = '发送邮件'

    def zf_room(self, request, queryset):
        for meeting in queryset:
            ok, meeting = del_room(meeting, 1)
            print(meeting.request_status, meeting)
            if ok == 1:
                messages.success(request, '作废 Zoom 会议室：{}：成功.'.format(meeting.room_id))
            else:
                messages.error(request, '作废 Zoom 会议室：{}：失败.'.format(meeting.room_id))
    zf_room.short_description = '作废 Room'


# @admin.register(ZoomMeeting)
# class ZoomMeetingAdmin(admin.ModelAdmin):
#     list_display = ['meeting.topic', 'meeting__start_time', 'meeting__end_time'
#                     'host__account', 'status', 'room_id', 'password', 'host__host_passowrd'
#                     'is_delete']
