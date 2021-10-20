# from __future__ import unicode_literals
# from django.db import models
# from rest_framework import serializers
# from django.dispatch import receiver
# from erp_notification.constants import PRIORITY,SCHEDULING


# class DataStructure(models.Model):
#     data_id = models.AutoField(db_column='data_id', primary_key=True)  # Field name made lowercase.
#     data_fields = models.JsonField(db_column = 'data_fields')  # Field name made lowercase.
#     # {
#     #     {
#     #         'field_name':'name'
#     #         'type':'VC'         # DEFAULT:VC  #VC : VARCHAR, I : INTEGER, F : FLOAT, DB : DOUBLE, DT : DATETIME, T : TIME, D : DATE, L : LONGTEXT
#     #         'is_email':1 or 0   # DEFAULT:0   #1 for YES ,0 for NO
#     #         'is_phone':1 or 0   # DEFAULT:0   #1 for YES ,0 for NO
#     #         'is_unique':1 or 0  # DEFAULT:0   #1 for YES ,0 for NO
#     #         'is_filter':1 or 0  # DEFAULT:0   #1 for YES ,0 for NO ,

#     #     },
#     #     {
#     #         'field_name':'id'
#     #         'type':'I'         # DEFAULT:VC  #VC : VARCHAR, I : INTEGER, F : FLOAT, DB : DOUBLE, DT : DATETIME, T : TIME, D : DATE, L : LONGTEXT
#     #         'is_email':1 or 0   #1 for YES ,0 for NO
#     #         'is_phone':1 or 0   #1 for YES ,0 for NO
#     #         'is_unique':1 or 0  #1 for YES ,0 for NO
#     #         'is_filter':1 or 0  #1 for YES ,0 for NO
#     #     }

#     # }
#     access = models.IntegerField(default=1)
#     # DEFAULT:1  #1 : PUBLIC, 2 : PRIVATE
#     accessible_by = models.JsonField(db_column='accessible_by')
#     # store the emp_id in array e.g: [12066,4448]
#     status = models.IntegerField(db_column='status', default=1)
#     # 0 = DELETE, 1 = INSERT, 2 = UPDATE
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'NotifyDataStructure'

# class DataSet(models.Model):
#     prim_key = models.CharField(db_column='prim_key', max_length=11, blank=False, null=False)
#     data_id = models.ForeignKey(DataStructure, related_name='Notify_DataSet_DataStructure', db_column='data_id', null=True, on_delete=models.SET_NULL)
#     data_json = models.JsonField(default='NULL')
#     # {'field_name':field_value} eg: {'name':'VRINDA SINGHAL','uniq_id':954,-----,'group_id':[1,2.3]}
#     status = models.IntegerField(db_column='status', default=1)
#     # 0 = DELETE, 1 = INSERT, 2 = UPDATE
    
#     class Meta:
#         db_table = 'NotifyDataSet'

# class Group(models.Model):
#     group_name = models.CharField(db_column='group_name', max_length=40, blank=True, null=True)
#     data_id = models.ForeignKey(DataStructure, related_name='Notify_Group_DataStructure', db_column='data_id', null=True, on_delete=models.SET_NULL)
#     access = models.IntegerField(default=1)
#     # DEFAULT:1  #1 : PUBLIC, 2 : PRIVATE
#     accessible_by = models.JsonField(db_column='accessible_by')
#     # store the emp_id in array e.g: [12066,4448]
#     status = models.IntegerField(db_column='status', default=1)
#     # 0 = DELETE, 1 = INSERT, 2 = UPDATE
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
#     class Meta:
#         db_table = 'NotifyGroup'

# class SubGroup(models.Model):
#     subgroup_name = models.CharField(db_column='group_name', max_length=40, blank=True, null=True)
#     group_id = models.ForeignKey(Group, related_name='Notify_SubGroup_Group', db_column='group_id', null=True, on_delete=models.SET_NULL)
#     access = models.IntegerField(default=1)
#     # DEFAULT:1  #1 : PUBLIC, 2 : PRIVATE
#     accessible_by = models.JsonField(db_column='accessible_by')
#     # store the emp_id in array e.g: [12066,4448]
#     status = models.IntegerField(db_column='status', default=1)
#     # 0 = DELETE, 1 = INSERT, 2 = UPDATE
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
#     class Meta:
#         db_table = 'NotifySubGroup'

# class Template(models.Model):
#     template_name = models.CharField(db_column='template_name', max_length=40, blank=True, null=True)
#     body = models.TextField(db_column='body')
#     # store variable values in << >> eg: Dear <<1.data_set>>,\t Your metting is schedule on <<2.date>> at <<3.time>> in <<4.string>>.
#     formation = models.JsonField(db_column="formation")
#     # store all varible values eg: [data_set,date,time,string] in correct order
#     access = models.IntegerField(default=1)
#     # DEFAULT:1  #1 : PUBLIC, 2 : PRIVATE
#     accessible_by = models.JsonField(db_column='accessible_by')
#     # store the emp_id in array e.g: [12066,4448]
#     status = models.IntegerField(db_column='status', default=1)
#     # 0 = DELETE, 1 = INSERT, 2 = UPDATE
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
#     class Meta:
#         db_table = 'NotifyTemplate'

# class SendNotification(models.Model):
#     data_id = models.ForeignKey(DataStructure, related_name='Notify_SendNotification_DataStructure', db_column='data_id', null=True, on_delete=models.SET_NULL)
#     group_id = models.JsonField(db_column='group_id')
#     # store the array of primary key of table Group eg: [1,2] #must to belong to same dataset
#     prim_keys = models.JsonField(db_column='prim_keys')
#     # store array of those ids to whom notification is send eg: [954,348]
#     email = models.JsonField(db_column='email')
#     # store the array of email field name from dataset eg: ['Email','FatherEmail']
#     phone = models.JsonField(db_column='phone')
#     # store the array of phone field name from dataset eg: ['MobileNo','FatherMobile']
#     portal = models.CharField(db_column='portal',max_length=1,blank=True,null=True,default='N')
#     # Y: YES, N: NO
#     subject = models.CharField(db_column='subject', max_length=78, blank=True, null=True)
#     signature = models.TextField(db_column='signature')
#     template_id = models.ForeignKey(Template, related_name='Notify_SendNotification_Template', db_column='template_id', null=True, on_delete=models.SET_NULL)
#     # NULL in case if template is not selected from existing
#     template_body = models.TextField(db_column='body')
#     # store value of data_set_keys in << >> eg: Dear <<1.data_set.name>>,\t Your metting is schedule on 12-04-2020 at 03:00am in A-BLOCK.
#     temp_data_key = models.JsonField(db_column='temp_data_key')
#     # DEFALUT: {1: data_set.name}
#     priority = models.CharField(choices=PRIORITY, default='L', max_length=10, blank=True, null=True)
#     scheduling = models.CharField(choices=SCHEDULING, default='O', max_length=20, blank=True, null=True)
#     scheduling_other = models.IntegerField()
#     start_date = models.DateTimeField(blank=True, null=True)
#     expiry_date = models.DateTimeField(blank=True, null=True)
#     send_by = models.IntegerField() #12066 : prim_key
#     status = models.IntegerField(db_column='status', default=1)
#     # 0 = DELETE, 1 = INSERT, 2 = UPDATE
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
#     class Meta:
#         db_table = 'NotifySendNotification'

# class NotificationLog(models.Model):
#     msg = models.TextField() #actual text eg: Dear VRINDA SINGHAL,\t Your metting is schedule on 12-04-2020 at 03:00am in A-BLOCK.
#     prim_key = models.IntegerField() # 954
#     email = models.CharField(db_column='email', max_length=100, blank=True, null=True)
#     phone = models.IntegerField(db_column='phone')
#     portal = models.CharField(db_column='portal',max_length=1,blank=True,null=True,default='N')
#     # Y: YES, N: NO
#     notify_id = models.ForeignKey(SendNotification, related_name='Notify_NotificationLog_SendNotification', db_column='notify_id', null=True, on_delete=models.CASCADE)
#     date = models.DateTimeField(blank=True, null=True)
#     status = models.IntegerField(db_column='status', default=1)
#     # 0 = DELETE, 1 = INSERT, 2 = UPDATE
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
#     class Meta:
#         db_table = 'NotifyNotificationLog'