from __future__ import unicode_literals
from django.db import models
from rest_framework import serializers
from django.dispatch import receiver
from .constant_variables.constant_variables import PRIORITY,SCHEDULING
# from erp_notification.constants import PRIORITY,SCHEDULING
from django_mysql.models import JSONField
from django_celery_results.models import TaskResult

class DataStructure(models.Model):
    data_id = models.AutoField(db_column='data_id', primary_key=True)  # Field name made lowercase.
    data_fields = JSONField(db_column = 'data_fields')  # Field name made lowercase.
    # {
    #     {
    #         'field_name':'name'
    #         'type':'VC'         # DEFAULT:VC  #VC : VARCHAR, I : INTEGER, F : FLOAT, DB : DOUBLE, DT : DATETIME, T : TIME, D : DATE, L : LONGTEXT
    #         'is_email':1 or 0   # DEFAULT:0   #1 for YES ,0 for NO
    #         'is_phone':1 or 0   # DEFAULT:0   #1 for YES ,0 for NO
    #         'is_unique':1 or 0  # DEFAULT:0   #1 for YES ,0 for NO
    #         'is_filter':1 or 0  # DEFAULT:0   #1 for YES ,0 for NO ,

    #     },
    #     {
    #         'field_name':'id'
    #         'type':'I'         # DEFAULT:VC  #VC : VARCHAR, I : INTEGER, F : FLOAT, DB : DOUBLE, DT : DATETIME, T : TIME, D : DATE, L : LONGTEXT
    #         'is_email':1 or 0   #1 for YES ,0 for NO
    #         'is_phone':1 or 0   #1 for YES ,0 for NO
    #         'is_unique':1 or 0  #1 for YES ,0 for NO
    #         'is_filter':1 or 0  #1 for YES ,0 for NO
    #     }

    # }
    name = models.CharField(max_length=50,default=None)
    # access = models.IntegerField(default=1)
    # DEFAULT:1  #1 : PUBLIC, 2 : PRIVATE
    accessible_by = JSONField(db_column='accessible_by')
    # store the emp_id in array e.g: [12066,4448]
    status = models.IntegerField(db_column='status', default=1)
    # 0 = DELETE, 1 = INSERT, 2 = UPDATE
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = 'NotifyDataStructure'

class DataSet(models.Model):
    prim_key = models.CharField(db_column='prim_key', max_length=50, blank=False, null=False)
    data_id = models.ForeignKey(DataStructure, related_name='Notify_DataSet_DataStructure', db_column='data_id', null=True, on_delete=models.SET_NULL)
    data_json = JSONField(default='NULL')
    # {'field_name':field_value} eg: {'name':'VRINDA SINGHAL','uniq_id':954,-----,'group_id':[1,2.3]}
    status = models.IntegerField(db_column='status', default=1)
    # 0 = DELETE, 1 = INSERT, 2 = UPDATE
    
    class Meta:
        db_table = 'NotifyDataSet'

class Group(models.Model):
    group_name = models.CharField(db_column='group_name', max_length=40, blank=True, null=True)
    data_id = models.ForeignKey(DataStructure, related_name='Notify_Group_DataStructure', db_column='data_id', null=True, on_delete=models.SET_NULL)
    # access = models.IntegerField(default=1)
    # DEFAULT:1  #1 : PUBLIC, 2 : PRIVATE
    accessible_by = JSONField(db_column='accessible_by')
    # store the emp_id in array e.g: [12066,4448]
    status = models.IntegerField(db_column='status', default=1)
    # 0 = DELETE, 1 = INSERT, 2 = UPDATE
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
    class Meta:
        db_table = 'NotifyGroup'

class SubGroup(models.Model):
    subgroup_name = models.CharField(db_column='group_name', max_length=40, blank=True, null=True)
    group_id = models.ForeignKey(Group, related_name='Notify_SubGroup_Group', db_column='group_id', null=True, on_delete=models.SET_NULL)
    # access = models.IntegerField(default=1)
    # DEFAULT:1  #1 : PUBLIC, 2 : PRIVATE
    accessible_by = JSONField(db_column='accessible_by')
    # store the emp_id in array e.g: [12066,4448]
    status = models.IntegerField(db_column='status', default=1)
    # 0 = DELETE, 1 = INSERT, 2 = UPDATE
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
    class Meta:
        db_table = 'NotifySubGroup'

class Template(models.Model):
    template_name = models.CharField(db_column='template_name', max_length=40, blank=True, null=True)
    body = models.TextField(db_column='body')
    # store variable values in << >> eg: Dear <<1.data_set>>,\t Your metting is schedule on <<2.date>> at <<3.time>> in <<4.string>>.
    formation = JSONField(db_column="formation")
    # store all varible values eg:   in correct order
    # access = models.IntegerField(default=1)
    # DEFAULT:1  #1 : PUBLIC, 2 : PRIVATE
    accessible_by = JSONField(db_column='accessible_by')
    # store the emp_id in array e.g: [12066,4448]
    description = JSONField(db_column='description')
    #description of formation
    status = models.IntegerField(db_column='status', default=1)
    # 0 = DELETE, 1 = INSERT, 2 = UPDATE
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
    class Meta:
        db_table = 'NotifyTemplate'

class SendNotification(models.Model):
    data_id = models.ForeignKey(DataStructure, related_name='Notify_SendNotification_DataStructure', db_column='data_id', null=True, on_delete=models.SET_NULL)
    group_id = JSONField(db_column='group_id',null=True)
    # store the array of primary key of table Group eg: [1,2] #must to belong to same dataset
    subgroup_id = JSONField(db_column='subgroup_id',null=True)
    # store the array of primary key of table Sub_group eg: [1,2] #must to belong to same dataset
    prim_keys = JSONField(db_column='prim_keys')
    # store array of those ids to whom notification is send eg: [954,348]
    email = JSONField(db_column='email')
    # store the array of email field name from dataset eg: ['Email','FatherEmail']
    phone = JSONField(db_column='phone')
    # store the array of phone field name from dataset eg: ['MobileNo','FatherMobile']
    portal = models.CharField(db_column='portal',max_length=1,blank=True,null=True,default='N')
    # Y: YES, N: NO
    subject = models.CharField(db_column='subject', max_length=78, blank=True, null=True)
    signature = models.TextField(db_column='signature')
    template_id = models.ForeignKey(Template, related_name='Notify_SendNotification_Template', db_column='template_id', null=True, on_delete=models.SET_NULL)
    # NULL in case if template is not selected from existing
    template_body = models.TextField(db_column='body')
    # store value of data_set_keys in << >> eg: Dear <<1.data_set.name>>,\t Your metting is schedule on 12-04-2020 at 03:00am in A-BLOCK.
    temp_data_key = JSONField(db_column='temp_data_key')
    # DEFALUT: {1: data_set.name}
    priority = models.CharField(choices=PRIORITY, default='L', max_length=10, blank=True, null=True)
    scheduling = models.CharField(choices=SCHEDULING, default='O', max_length=20, blank=True, null=True)
    scheduling_other = models.IntegerField()
    start_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    send_by = models.CharField(db_column='send_by', max_length=50, blank=False, null=False) #12066 : prim_key
    status = models.IntegerField(db_column='status', default=1)
    # 0 = DELETE, 1 = INSERT, 2 = UPDATE
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    task_name = models.CharField(max_length=255,null=True)
    
    class Meta:
        db_table = 'NotifySendNotification'

class NotificationLog(models.Model):
    msg = models.TextField() #actual text eg: Dear VRINDA SINGHAL,\t Your metting is schedule on 12-04-2020 at 03:00am in A-BLOCK.
    prim_key = models.CharField(db_column='prim_key', max_length=20, blank=False, null=False) # 954
    email = JSONField(db_column='email', max_length=100, blank=True, null=True)
    phone = JSONField(db_column='phone')
    portal = models.CharField(db_column='portal',max_length=1,blank=True,null=True,default='N')
    # Y: YES, N: NO
    notify_id = models.ForeignKey(SendNotification, related_name='Notify_NotificationLog_SendNotification', db_column='notify_id', null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(db_column='status', default=1)
    # 0 = DELETE, 1 = INSERT, 2 = UPDATE
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    # task_result = models.ForeignKey(TaskResult,related_name='Notify_send_via_result',null=True, on_delete=models.CASCADE)
    # email_task_result = models.CharField(max_length=255,null=True)
    email_task_result = JSONField(default=dict)
    portal_task_result = models.CharField(max_length=255,null=True)
    # phone_task_result = models.CharField(max_length=255,null=True)
    phone_task_result = JSONField(default=dict)
    class Meta:
        db_table = 'NotifyNotificationLog'

class Job(models.Model):
    notify_id = models.ForeignKey(SendNotification, related_name='Notify_Job_SendNotification', db_column='notify_id', null=True, on_delete=models.CASCADE)
    start_date=models.DateField(blank=True, null=True)#start date given by the user . When to start the notification
    next_execution_date=models.DateField(blank=True, null=True)# this field is compared with current date . If both same ,notication is sent and it gets updated with adding interval.
    end_date=models.DateField(blank=True, null=True)#expiry date for the job or notification task
    interval = models.IntegerField(blank=True, default=1)#To store the time interval for sending notification. eg 1 day(daily), 7 days(weekly), 28 days(Monthly)
    args=models.TextField(null=True)#to store the arguments of sendNotification
    job_result = JSONField(default=dict)#to store datewise job result .
    task_name=JSONField(default=dict) #to store the celery task ids 
    task_priority=models.IntegerField(default=0)#to store the task priority . 9 is for high priority and 0 is for low priority. priority with 9 will executed first than task with priority 0 for same date.
    scheduling = models.CharField(choices=SCHEDULING, default='O', max_length=20, blank=True, null=True)#to store which type of scheduling is scheduled
    status = models.IntegerField(db_column='status', default=1) #to store the status of the Job . 1 if job is currently active and 0 if job is completed i.e. all mail/phone notification has been sent. It becomes 0 when it meets the expiry date
    flag = models.IntegerField(db_column='flag', default=1)# To store whether the Job is active or paused. This field updated in Pausing and Resuming the job .by pause_resume_job_task api. it becomes 0 when user stops the job task.
    class Meta:
        db_table = 'NotifyJob'