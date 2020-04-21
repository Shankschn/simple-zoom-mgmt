from django.db import models

# Create your models here.


class BasicSetting(models.Model):
    zh = models.CharField(max_length=50, null=True, verbose_name='邮箱')
    mm = models.CharField(max_length=50, null=True, verbose_name='密码')
    name = models.CharField(max_length=50, null=True, verbose_name='发件人身份')
    smtp_server = models.CharField(max_length=50, null=True, verbose_name='SMTP 发件服务器')
    early_time = models.IntegerField(null=True, verbose_name='可提前时间（时）')
    delay_time = models.IntegerField(null=True, verbose_name='可延迟时间（时）')
    it = models.TextField(null=True, verbose_name='管理员邮箱',
                          help_text='多个邮箱以英文逗号","进行分隔。所有会议通知都会通过邮件发送至管理人员邮箱。')
    api_create_url = models.CharField(max_length=100, null=True, verbose_name='API 创建会议室地址')
    api_delete_url = models.CharField(max_length=100, null=True, verbose_name='API 删除会议室地址',
                                      help_text='删除Zoom后台的会议室，如果会议正在进行，无法删除会议。')
    api_end_url = models.CharField(max_length=100, null=True, verbose_name='API 结束会议室地址',
                                   help_text='强制结束正在开的会议！谨慎调用。如果不知道有什么用，请勿填写。')
    models.DateTimeField()

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = 'BasicSetting'
        # Django Admin 中显示名名称
        verbose_name = '基础信息配置'  # 单数
        verbose_name_plural = '0 基础信息配置'  # 复数


class Host(models.Model):
    # 自定义字段
    account = models.CharField(max_length=50, null=True, unique=True, verbose_name='账号')
    password = models.CharField(max_length=50, null=True, verbose_name='账号密码')
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name='简称')
    types = (
        (0, '临时账号'),
        (1, '正式账号'),
        (2, '过期账号')
    )
    host_type = models.IntegerField(default=1, choices=types, verbose_name='账号类型')
    url = models.CharField(max_length=50, null=True, verbose_name='登陆地址')
    capacity = models.IntegerField(null=True, verbose_name='人数上限')
    level = models.IntegerField(default=1, verbose_name='主持人级别',
                                help_text='默认：1。0:不可申请；1：一般会议可申请；2：重要会议申请；3：特殊会议可申请。')

    # api 相关字段
    api_key = models.CharField(max_length=50, null=True, blank=True, verbose_name='api_key')
    api_secret = models.CharField(max_length=50, null=True, blank=True, verbose_name='api_secret')
    host_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='host_id')
    host_password = models.CharField(max_length=10, null=True, verbose_name='主持人密码')

    remark = models.CharField(max_length=100, null=True, blank=True, verbose_name='备注')

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = 'Host'
        # Django Admin 中显示名名称
        verbose_name = '主持人账户'  # 单数
        verbose_name_plural = '1 主持人账户'  # 复数

    def __str__(self):
        return self.name


class Meeting(models.Model):
    topic = models.CharField(max_length=100, null=True, verbose_name='主题')
    request_statuss = {
        (0, '失败 - 无可用会议室'),
        (1, '成功'),
        (2, '失败 - 人数超出限制'),
    }
    request_status = models.IntegerField(choices=request_statuss, null=True, default=0, verbose_name='申请状态')
    statuss = (
        (0, '待定/未获取'),
        (1, '正常'),
        (2, '作废/取消'),
        (3, '结束'),
    )
    status = models.IntegerField(choices=statuss, null=True, default=0, verbose_name='会议状态')
    levels = (
        (0, '一般会议'),
        (1, '重要会议'),
        (2, '特殊会议'),
        (3, '紧急会议')
    )
    level = models.IntegerField(choices=levels, default=0, verbose_name='会议级别',
                                help_text=(
                                        '默认：一般会议。<br />' +
                                        '一般会议：向主持人级别：0，发起会议申请；<br />' +
                                        '重要会议：向主持人级别：0，1，发起会议申请；<br />' +
                                        '特殊会议：向主持人级别：0，1，2，发起会议申请；<br />' +
                                        '紧急会议：向主持人级别：0，1，2，3，发起会议申请；<br />'
                                    )
                                )
    start_time = models.DateTimeField(null=True, verbose_name='开始时间')
    real_start_time = models.DateTimeField(null=True, verbose_name='实际开始时间')
    end_time = models.DateTimeField( null=True, verbose_name='结束时间')
    real_end_time = models.DateTimeField(null=True, verbose_name='实际结束时间')
    is_no = (
        (0, '否'),
        (1, '是')
    )
    enable_early_time = models.IntegerField(default=1, choices=is_no, verbose_name='是否启用提前时间')
    enable_delay_time = models.IntegerField(default=1, choices=is_no, verbose_name='是否启用延迟时间')
    requester = models.CharField(max_length=50, null=True, verbose_name='申请人')
    requester_email = models.CharField(max_length=50, null=True, verbose_name='申请人邮箱')
    request_time = models.DateTimeField(null=True, verbose_name='申请时间')
    people = models.IntegerField(null=True, verbose_name='参会人数')
    people_emails = models.TextField(null=True, verbose_name='参会人邮箱')
    is_mail_all = models.IntegerField(default=0, choices=is_no, verbose_name='是否发送会议信息至参会人')
    is_mail_success = models.IntegerField(default=0, choices=is_no, verbose_name='是否成功发送邮件')
    host = models.ForeignKey(Host, to_field='account', on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name='主持人')
    room_id = models.CharField(max_length=10, null=True, blank=True, verbose_name='会议号')
    room_password = models.CharField(max_length=20, null=True, blank=True, verbose_name='会议密码')
    room_is_delete = models.IntegerField(default=0, choices=is_no, verbose_name='是否已删除 Room ')
    ct_meetings = models.TextField(null=True, blank=True, verbose_name='冲突会议室列表')

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = 'MeetingInfo'
        # Django Admin 中显示名名称
        verbose_name = '会议信息'  # 单数
        verbose_name_plural = '2 会议信息'  # 复数
