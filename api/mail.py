import time
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr

import smtplib

from django.utils import timezone

from .models import *


# from api.models import BasicSetting
# bs = BasicSetting.objects.first()
# BS = {
#     'zh': bs.zh,
#     'mm': bs.mm,
#     'name': bs.name,
#     'smtp_server': bs.smtp_server,
#     'early_time': bs.early_time,
#     'delay_time': bs.delay_time,
#     'it': bs.it,
#     'api_create_url': bs.api_create_url,
#     'api_delete_url': bs.api_delete_url,
#     'api_end_url': bs.api_end_url
# }


from .simpletime import *


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def get_body_end():
    end = '''
安装Zoom：
  苹果手机，安卓手机，Windows电脑，Mac电脑：
    请前往：https://www.zoomus.cn/download ，根据提示下载并安装。
  注意：安卓手机在安装过程中请选择“继续安装”，请勿选择”在应用市场中安装“。
    所有设备在安装过程中有提示网络和权限问题，请一律点击允许Zoom使用权限。

加入会议步骤：
  1.打开软件后，无需登陆，直接选择加入会议；
  2.第一行输入会议号，第二行输入姓名后，加入会议；
  3.如提示验证手机，请验证手机；
  4.输入会议密码；
  5.如果无法加入会议，请查看“安装Zoom”，下载最新客户端后重新加入会议。
加入后必须操作：
  1.激活扬声器（听见声音）：点击左下角的音频（麦克风/语音），会弹出选项,
    点击弹出选项中的“通过设备语音/互联网进行呼入/呼叫”；
  2.请根据情况打开/关闭，麦克风/视频（摄像头）：左下角有音频（语音），视频等开关。
    '''
    return end


# 数据，是否发送全部信息(申请人及管理员，发送主持人密码。)
def get_body_cg(meeting, is_special_email, bs):
    body = '''
会议主题：{0}
申请人：{1}
开始时间：{2}
结束时间：{3}
会议号：{4}
会议密码：{5}
人数上限：{6}
占用：{7}
最终可用时间：{10} 至 {11} 
注意：请勿在“最终可用时间”外加入会议，请勿超时！
  如需在时间段外测试，请联系信息技术部获取测试会议室使用！
    '''.format(meeting.topic, meeting.requester, meeting.start_time,
               meeting.end_time,
               meeting.room_id, meeting.room_password, meeting.host.capacity, meeting.host.name,
               bs.early_time, bs.delay_time,
               meeting.real_start_time, meeting.real_end_time)
    if is_special_email:
        special_body = '''
        
若在申请会议时，未勾选“发送邮件通知参会人”，请申请人将会议号及会议密码下发至需要参会的人员。        

----------请勿将以下信息发送给其他人员----------
主持人密码：{}
  201601：电脑获取权限，202002：手机获取权限
----------请勿将以上信息发送给其他人员----------

主持人权限：录制会议，全体静音，共享屏幕，设置联席主持人等。

获取权限：
  手机：右下角——更多——获取主持人权限
  电脑：下方导航栏——参会者——右侧参会者框的右下角——获取主持人权限   

注意：如果对方无法共享屏幕，请设置对方为联席主持人。

        '''.format(meeting.host.host_password)
        body = body + special_body
    body = body + get_body_end()
    return body


def get_ct_meetings_html(ct_meetings):
    temp_host = None
    html = '\n\t'
    for ct in ct_meetings:
        if ct.host != temp_host:
            html1 = '{} 已被占用时间：\n\t'.format(ct.host.name)
        else:
            html1 = ''
        html2 = '{0}————{1} 至 {2}————{3}\n\t' \
            .format(ct.topic, ct.real_start_time, ct.real_end_time, ct.requester)
        html = html + html1 + html2 + '\n\t'
        temp_host = ct.host
    return html


def get_body_sb0(meetings):
    ct_meetings_html = get_ct_meetings_html(meetings.ct_meetings)
    body = '''
{0}<{1}>：
您好，很抱歉的通知您，您申请的Zoom会议的时间段与其他人冲突。

申请信息如下：
  会议主题：{2}
  申请会议时间：{3} 至 {4}
  请求会议时间：{5} 至 {6}
  参会人数：{7}
  
一、如果必须在此时间段开会，请联系信息技术部查看备用会议室使用情况
二、否则可在下方查看符合申请人数的 Zoom 会议室 已被占用的时间段，选择未被占用的时间段，再重新申请会议
三、联系已申请会议的申请人，沟通更换会议时间

系统判断冲突方式：以申请会议时间的开始时间提前 1 小时，结束时间延后 1 小时，再去判断会议是否冲突。

{8}
    '''.format(meetings.requester, meetings.requester_email, meetings.topic,
               meetings.start_time, meetings.end_time,
               meetings.real_start_time, meetings.real_end_time,
               meetings.people, ct_meetings_html)
    return body


def get_body_sb2(meeting):
    body = '''
{0}<{1}>：
会议主题：{2}
会议时间：{3} 至 {4}
参会人数：{5}
您好，很抱歉的通知您，您申请的 Zoom 会议的参会人数超过限制，请等待信息技术部与服务商沟通后的结果。
    '''.format(meeting.requester, meeting.requester_email, meeting.topic,
               meeting.start_time, meeting.end_time,
               meeting.people)
    return body


def get_body_qx(meeting):
    body = '''
{2}<{3}}>:
  Zoom 会议被作废，概要：
    会议主题：{0}
    会 议 号：{1}
    状    态：已作废
    '''.format(meeting.topic, meeting.room_id, meeting.requester, meeting.requester_email)
    return body


# 发送邮件
def send_mail(meeting):
    bs = BasicSetting.objects.first()
    meeting.is_mail_success = 0
    super_special_emails = bs.it.split(',')
    special_emails = super_special_emails
    special_emails.append(meeting.requester_email)
    print(special_emails)

    emails = special_emails

    if meeting.is_mail_all == 1:
        people_emails = meeting.people_emails.split(',')
        emails = emails + people_emails

    emails = set(emails)
    emails = list(emails)
    print('如果申请成功，邮件将被发送给：{}'.format(emails))

    special_emails = set(special_emails)
    special_emails = list(special_emails)
    print(special_emails)
    print('特殊人员：{}'.format(special_emails))

    msg_from = _format_addr('%s <%s>' % (bs.name, bs.zh))
    msg_subject = Header('Zoom 会议通知：{0}——{1}'.format(meeting.topic, meeting.requester), 'utf-8').encode()
    smtp = smtplib.SMTP_SSL(bs.smtp_server, 465)
    smtp.login(bs.zh, bs.mm)
    # smtp.set_debuglevel(1)
    try:
        if meeting.request_status == 1:
            go = 1
            if meeting.status == 2:
                go = 0
                msg = MIMEMultipart()
                msg['From'] = msg_from
                msg['Subject'] = Header('Zoom 会议通知：作废——{0}——{1}'.format(meeting.topic, meeting.requester),
                                        'utf-8').encode()
                msg['To'] = _format_addr('<%s>' % meeting.requester_email)
                body = get_body_qx(meeting)
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                smtp.sendmail(bs.zh, special_emails, msg.as_string())
            if go == 1:
                for email in emails:
                    msg = MIMEMultipart()
                    msg['From'] = msg_from
                    msg['Subject'] = msg_subject
                    msg['To'] = _format_addr('<%s>' % email)
                    if email in special_emails:
                        body = get_body_cg(meeting, True, bs)
                    else:
                        body = get_body_cg(meeting, False, bs)
                    msg.attach(MIMEText(body, 'plain', 'utf-8'))
                    # print(msg)
                    # smtp.set_debuglevel(1)
                    smtp.sendmail(bs.zh, [email], msg.as_string())
        else:
            msg = MIMEMultipart()
            msg['From'] = msg_from
            msg['Subject'] = Header('Zoom 会议通知：失败——{0}——{1}'.format(meeting.topic, meeting.requester), 'utf-8').encode()
            msg['To'] = _format_addr('<%s>' % meeting.requester_email)
            if meeting.request_status == 0:
                body = get_body_sb0(meeting)
            else:
                body = get_body_sb2(meeting)
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            # smtp.set_debuglevel(1)
            # print('special_emails-------------', special_emails, type(special_emails))
            smtp.sendmail(bs.zh, special_emails, msg.as_string())
    except Exception as e:
        msg = '发送邮件，未发送完成，报错：{}, 错误文件：{}, 错误行：{}'.format(e,
                                                         e.__traceback__.tb_frame.f_globals["__file__"],
                                                         e.__traceback__.tb_lineno)
        meeting.is_mail_success = False
        print(msg)
    else:
        msg = '发送邮件，发送完成。'
        meeting.is_mail_success = True
        print(msg)
    finally:
        meeting.save()
    smtp.quit()
    return meeting
