from django.test import TestCase

# Create your tests here.
import requests


# Post to sqhys create zoom
def post_sqhys():
    url = 'http://127.0.0.1:8000/zoom_api/sqhys/'
    data = {
        'topic': '测试会议53',
        'requester': '李东宇',
        'email': 'lidy@creditpharma.cn',
        'request_time': '2020-4-18 12:00:00',
        'start_time': '2020-4-18 12:00:00',
        'end_time': '2020-4-18 15:00:00',
        'max_people': 200,
        'emails': 'lidy@creditpharma.cn,zoom17@creditpharma.cn',
        'is_mail_all': 1
    }
    r = requests.post(url, data=data)
    print(r.text)



post_sqhys()