import datetime

from django.utils import timezone


def strToTime(tempstr):
    return datetime.datetime.strptime(tempstr, "%Y-%m-%d %H:%M:%S")


def UTC_to_CST(t_time):
    cst_time = timezone.localtime(t_time).strftime("%Y-%m-%d %H:%M:%S")
    return cst_time


def is_in_today(end_time):
    now = datetime.datetime.now()
    today_start = datetime.datetime.strptime(str(now.date()) + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    today_end = datetime.datetime.strptime(str(now.date()) + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    cha = now - end_time
    # one_day = datetime.timedelta(days=1)
    if end_time < today_start:
        return 0
    elif today_start < end_time < today_end:
        return 1
    elif end_time > today_end:
        return 2
    else:
        return 99
