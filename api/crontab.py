from api.zoom import del_room
from api.models import Meeting
from datetime import datetime


def del_room_crontab():
    now_time = datetime.now()
    meetings = Meeting.objects.filter(request_status=1, status=1, room_is_delete=0)
    msg = '{}删除会议室报错，原因未知，请排查。'.format(now_time)
    if meetings.exists():
        for meeting in meetings:
            if now_time > meeting.real_end_time:
                ok, meeting = del_room(meeting, 1)
                if ok == 1:
                    msg = '{2}正常结束会议，会议主题：{0}，会议号：{1}'.format(meeting.topic, meeting.room_id, now_time)
                else:
                    msg = '{2}无法结束会议，会议主题：{0}，会议号：{1}'.format(meeting.topic, meeting.room_id, now_time)
    print(msg)
