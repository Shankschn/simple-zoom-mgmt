import datetime
import json
import random

import numpy as np

from .models import *

import requests


def strToTime(str_time):
    return datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")


def timeToStr(time):
    return time.strftime("%Y-%m-%d %H:%M:%S")


def addHours(str_time, hours=1):
    return strToTime(str_time) + datetime.timedelta(hours=hours)


def subHours(str_time, hours=1):
    return strToTime(str_time) - datetime.timedelta(hours=hours)


# 删除 room status: 0 为取消/作废 1 为正常结束会议
def del_room(meeting, status):
    bs = BasicSetting.objects.first()
    url = bs.api_delete_url
    host = meeting.host
    data = {
        'api_key': host.api_key,
        'api_secret': host.api_secret,
        'host_id': host.host_id,
        'data_type': 'JSON',
        'id': meeting.room_id
    }
    try:
        rp = requests.post(url, data=data)
    except Exception as e:
        ok = 0
        meeting.room_is_delete = False
        msg = '删除 room 时，Post 请求时，报错：{}'.format(e)
        print(msg)
        pass
    else:
        temp = json.loads(rp.text)
        msg = '删除 room 时，Post 请求后，返回的 Json：{}'.format(temp)
        print(msg)
        try:
            if (temp['id'] == meeting.room_id) and temp['deleted_at']:
                ok = 1
                meeting.room_is_delete = True
                if status == 0:  # 作废/取消会议
                    meeting.status = 2
                else:  # 会议正常结束
                    meeting.status = 3
            else:
                ok = 0
                meeting.room_is_delete = False
                meeting.status = 1
        except Exception as e:
            msg = '删除 room 时，返回的Json，报错：{}'.format(e)
            print(msg)
            ok = 1
            meeting.status = 2
            meeting.room_is_delete = True
    finally:
        meeting.save()
    return ok, meeting


# 为会议室请求主持人
def get_host(meeting):
    hosts = Host.objects.filter(level__range=[1, meeting.level + 1], host_type=1)  # __lte 小于等于
    print('meeting', meeting)
    ct_meetings = []
    # 申请人数 在范围外
    # print(type(meeting.people))
    print('meeting_people', meeting.people)
    if int(str(meeting.people)) > 100:
        meeting.request_status = 2
        return meeting
    for host in hosts:
        # 申请人数 在范围内
        if int(meeting.people) <= int(host.capacity):
            meetings = Meeting.objects.filter(host=host, request_status=1)
            print('=========== 查询到{0}拥有的会议{1}'.format(host.name, meetings ))
            if meetings.exists():  # 主持人目前有主持的会议
                # 遍历 主持人目前主持的会议 是否与 申请的会议 时间是否冲突
                has_time = []
                for m in meetings:
                    if m == meeting and meetings.count() == 1:
                        print('主持人当前没有会议, 返回主持人可主持会议。')
                        meeting.host = host
                        meeting.request_status = 1
                        meeting.save()
                        return meeting
                    # print(m.real_end_time, meeting.real_end_time, m.real_start_time, meeting.start_time)
                    if min(m.real_end_time, meeting.real_end_time) > max(m.real_start_time, meeting.start_time):
                        print('主持人：{}无空闲时间主持会议。'.format(host.name))
                        # print('没时间')
                        has_time.append(0)
                        ct_meetings.append(m)
                    else:
                        has_time.append(1)
                arr = np.array(has_time)
                if (arr == 1).all():
                    print('主持人：{}有空闲时间主持会议。'.format(host.name))
                    # print('有时间')
                    meeting.host = host
                    meeting.request_status = 1
                    meeting.save()
                    return meeting
            else:  # 主持人目前没有主持会议
                print('主持人：{}没有会议。'.format(host.name))
                meeting.host = host
                meeting.request_status = 1
                meeting.save()
                return meeting
    meeting.ct_meetings = ct_meetings
    meeting.request_status = 0
    meeting.save()
    return meeting


# 创建 room
def create_room(meeting):
    # print('创建会议室', dict)
    bs = BasicSetting.objects.first()
    url = bs.api_create_url
    password1 = ''.join(random.sample(['a', 'b', 'c', 'd'], 1))
    password2 = ''.join(random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
    password = password1 + password2
    data = {
        'api_key': meeting.host.api_key,
        'api_secret': meeting.host.api_secret,
        'data_type': 'JSON',
        'host_id': meeting.host.host_id,
        'topic': meeting.topic,
        'type': 3,
        "timezone": "Asia/Shanghai",
        'password': password,
        "option_jbh": 'true',
        "option_start_type": "video",
        "option_host_video": 'true',
        "option_participants_video": 'true',
        "option_cn_meeting": 'false',
        "option_enforce_login": 'false',
    }
    try:
        rp = requests.post(url, data=data)
    except Exception as e:
        msg = '创建 room 时，Post 请求时，报错：{}'.format(e)
        print(msg)
        pass
    else:
        temp = json.loads(rp.text)
        msg = '创建 room 时，Post 请求后，返回的 Json：{}'.format(temp)
        print(msg)
        if temp['id'] and temp['password']:
            meeting.request_status = 1
            meeting.status = 1
            meeting.room_id = temp['id']
            meeting.room_password = temp['password']
            meeting.save()
    return meeting
