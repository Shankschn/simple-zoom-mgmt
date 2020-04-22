from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

from .mail import *
from .zoom import *
from .models import *
from .simpletime import *


@csrf_exempt
def sqhys(request):
    bs = BasicSetting.objects.first()
    d = {}
    print('申请会议', type(request), request)
    if request.method == 'POST':
        print('request.POST.dict()', request.POST.dict())
        t_roomid = request.POST.get('invented_meet_pid', None)

        # meeting = Meeting.objects.create(
        #     topic=request.POST.get('topic', None),
        #     requester=request.POST.get('requester', None),
        #     requester_email=request.POST.get('email', None),
        #     request_time=request.POST.get('request_time', None),
        #     start_time=request.POST.get('start_time', None),
        #     end_time=request.POST.get('end_time', None),
        #     people=request.POST.get('max_people', None),
        #     people_emails=request.POST.get('emails', None)
        # )

        # - datetime.timedelta(hours=bs.early_time)

        meeting = Meeting()
        meeting.requester = request.POST.get('requester', None)
        meeting.requester_email = request.POST.get('email', None)
        # temp = UTC_to_CST(strToTime(str(request.POST.get('request_time', None))))
        meeting.request_time = strToTime(str(request.POST.get('request_time', None)))
        meeting.topic = request.POST.get('topic', None)
        # temp = UTC_to_CST(strToTime(str(request.POST.get('start_time', None))))
        meeting.start_time = strToTime(str(request.POST.get('start_time', None)))
        # temp = UTC_to_CST(strToTime(str(request.POST.get('end_time', None))))
        meeting.end_time = strToTime(str(request.POST.get('end_time', None)))
        meeting.people = request.POST.get('max_people', None)
        meeting.people_emails = request.POST.get('emails', None)
        temp = request.POST.get('is_mail_all', None)
        if (temp == '1') or (temp == 1):
            meeting.is_mail_all = 1
            print('--------------', meeting.is_mail_all)
        # print(meeting.__dict__)
        # print('type{}'.format(type(meeting.start_time)))
        meeting.real_start_time = meeting.start_time - datetime.timedelta(hours=bs.early_time)
        meeting.real_end_time = meeting.end_time + datetime.timedelta(hours=bs.early_time)
        meeting.level = 0
        meeting.request_status = 0
        meeting.status = 0
        meeting.save()
        # print(meeting.__dict__)
        msg = '申请会议，已接收到的会议信息：{}'.format(meeting)
        print(msg)
        # 如果接收到会议号，先作废，再申请。
        if t_roomid:
            t_meeting = room_id_get_meeting(t_roomid)
            zfhys_public(t_meeting)
        meeting = get_host(meeting)
        if meeting.request_status == 1:
            meeting = create_room(meeting)
            d['status'] = '1'
            d['msg'] = '申请会议成功，请查看申请人公司邮箱。'
            d['data'] = {
                'room_id': meeting.room_id,
                'password': meeting.room_password,
                'host_limit': meeting.host.capacity,
            }
            send_mail(meeting)
        elif meeting.request_status == 0:
            d['status'] = '0'
            d['msg'] = '会议室已满，申请会议失败，请查看申请人公司邮箱。'
            send_mail(meeting)
        elif meeting.request_status == 2:
            d['status'] = '1'
            d['msg'] = '申请会议失败，请查看申请人公司邮箱。'
            send_mail(meeting)
    if request.method == 'GET':
        d['tips'] = '请使用POST'
    temp_d = json.dumps(d)
    print(temp_d)
    return HttpResponse(temp_d, content_type="application/json,charset=utf-8")


@csrf_exempt
def zfhys(request):
    d = {}
    if request.method == 'POST':
        room_id = request.POST.get('room_id', None)
        print('作废申请---------Room id：{}'.format(room_id))
        meeting = room_id_get_meeting(room_id)
        ok = zfhys_public(meeting)
        if ok == 1:
            d['status'] = 1
            d['msg'] = '作废会议室，成功。'
    if request.method == 'GET':
        d['tips'] = '请使用POST'
    temp_d = json.dumps(d)
    print(temp_d)
    return HttpResponse(temp_d, content_type="application/json,charset=utf-8")


def zfhys_public(meeting):
    ok = 0
    if meeting:
        ok, meeting = del_room(meeting, 0)
    if ok == 1:
        msg = '作废会议室 会议室：{}，已作废，正在发送作废邮件...'.format(meeting)
        send_mail(meeting)
    else:
        msg = '作废会议室 会议室：{}，出错，请排查...'.format(meeting)
    print(msg)
    return ok

