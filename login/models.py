from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.conf import settings
from django.db.models import CharField
from django.db.models.functions import Length
CharField.register_lookup(Length, 'length')


class EmployeeDropdown(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='Pid', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=500, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=500, blank=True, null=True)  # Field name made lowercase.
    is_edit = models.IntegerField(db_column='Is_Edit',default='1')  # Field name made lowercase.
    is_delete = models.IntegerField(db_column='Is_Delete',default='1')  # Field name made lowercase.
    status = models.CharField(db_column='status', max_length=50, blank=True, null=True,default='INSERT')  # Field name made lowercase.
    
    

    class Meta:
        db_table = 'employee_dropdown'


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    user_type = models.CharField(max_length=255)

    class Meta:
        managed=True
        db_table = 'auth_user'


class EmployeePrimdetail(models.Model):
    title = models.ForeignKey(EmployeeDropdown, related_name='title',db_column='Title', blank=True, null=True, limit_choices_to={'field':'TITLE'},on_delete=models.SET_NULL)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    dept = models.ForeignKey(EmployeeDropdown,db_column='Dept', related_name='department', blank=True, null=True, limit_choices_to={'field':'DEPARTMENT'},on_delete=models.SET_NULL)  # Field name made lowercase.
    doj = models.DateField(db_column='DOJ', blank=True, null=True)  # Field name made lowercase.
    current_pos = models.ForeignKey(EmployeeDropdown, related_name='Current_Position',db_column='Current_Pos', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    emp_type = models.ForeignKey(EmployeeDropdown, related_name='Emp_Type', blank=True,db_column='Emp_Type', null=True, limit_choices_to={'Field':'TYPE OF EMPLOYEMENT'},on_delete=models.SET_NULL)  # Field name made lowercase.
    emp_category = models.ForeignKey(EmployeeDropdown, related_name='Emp_Category', blank=True, null=True,db_column='emp_category', limit_choices_to={'Field':'CATEGORY OF EMPLOYEE'},on_delete=models.SET_NULL)  # Field name made lowercase.
    desg = models.ForeignKey(EmployeeDropdown, related_name='designation',db_column='Desg', blank=True, null=True, limit_choices_to={'Field':'DESIGNATION'},on_delete=models.SET_NULL)  # Field name made lowercase.
    cadre = models.ForeignKey(EmployeeDropdown, related_name='cadre',db_column='Cadre', blank=True, null=True, limit_choices_to={'Field':'CADRE'},on_delete=models.SET_NULL)  # Field name made lowercase.
    ladder = models.ForeignKey(EmployeeDropdown, related_name='ladder',db_column='Ladder', blank=True, null=True, limit_choices_to={'Field':'LADDER'},on_delete=models.SET_NULL)  # Field name made lowercase.
    shift = models.ForeignKey(EmployeeDropdown, related_name='shift',db_column='Shift', blank=True, null=True, limit_choices_to={'Field':'SHIFT'},on_delete=models.SET_NULL)  # Field name made lowercase.
    mob = models.CharField(db_column='Mob', max_length=12, blank=True, null=True)  # Field name made lowercase.
    mob1 = models.CharField(db_column='Mob1', max_length=12, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)  # Field name made lowercase.
    emp_id = models.OneToOneField(AuthUser,to_field='username',db_column='Emp_Id', primary_key=True,unique=True,on_delete=models.CASCADE)  # Field name made lowercase.
    lib_card_no = models.CharField(db_column='Lib_Card_No', max_length=15, blank=True, null=True)  # Field name made lowercase.
    organization = models.ForeignKey(EmployeeDropdown, related_name='organization', blank=True, null=True, limit_choices_to={'Field':'SHIFT'},on_delete=models.SET_NULL,db_column='Organization')  # Field name made lowercase.
    emp_status = models.CharField(db_column='Emp_Status', max_length=255, blank=True, null=True, default='ACTIVE')  # Field name made lowercase.
    join_pos = models.ForeignKey('EmployeeDropdown',related_name='Join_Position',db_column='Join_Pos', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.

    class Meta:
        db_table = 'employee_primdetail'


class CCellSeries(models.Model):
    description = models.TextField()
    title=models.CharField(max_length=1000,default=None,null=True)
    date = models.DateField()
    banner=models.CharField(max_length=1000)
    
    class Meta:
        managed=True
        db_table = 'CCellSeries'

class CCellSeriesDetails(models.Model):
    series_id=models.ForeignKey(CCellSeries,null=True,db_column='series_id',on_delete=models.SET_NULL)
    title=models.CharField(max_length=1000,default=None,null=True)
    description = models.TextField()
    date_of_launch = models.DateField()
    image=models.TextField(max_length=1000)
    is_file=models.CharField(max_length=2,default='N')
    url = models.CharField(max_length=200)
    
    class Meta:
        managed=True
        db_table = 'CCellSeriesDetails'

class Daksmsstatus(models.Model):
    phonenos = models.CharField(db_column='PhoneNos', max_length=100) 
    updatestatus = models.CharField(db_column='UpdateStatus', max_length=10) 
    rectimestamp = models.DateTimeField(db_column='RecTimeStamp')
    counttry = models.IntegerField(db_column='CountTry')
    msg = models.TextField(db_column='Msg') 
    otp = models.CharField(db_column='Otp',max_length=100, blank=True, null=True)
    senderid = models.IntegerField(db_column='SenderID', blank=True, null=True)
    sendby = models.CharField(db_column='Sendby', max_length=50, blank=True, null=True)
    mainid = models.AutoField(db_column='MainId', primary_key=True) 
    type = models.CharField(db_column='Type', max_length=50,default=None,null=True) 

    class Meta:
        db_table = 'daksmsstatus'

class AarDropdown(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='Pid', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=500, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=500, blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=100, blank=True, null=True)
    is_delete = models.IntegerField(db_column='Is_Delete',default=1)  # Field name made lowercase.
    is_edit = models.IntegerField(db_column='Is_Edit',default=1)  # Field name made lowercase.
    status = models.CharField(db_column='status', max_length=50, blank=True, null=True,default='INSERT')  # Field name made lowercase.

    class Meta:
        db_table = 'aar_dropdown'


class Notification(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)
    notification_json=models.CharField(db_column="notification_json",null=True,blank=True,max_length=10000)
    send_date=models.DateTimeField(blank=True, null=True)
    send_to_group=models.IntegerField(db_column="send_to_group",null=True,blank=True,default=-1)

    class Meta:
        db_table = 'Notification'

class Notification_status(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)
    emp_id = models.ForeignKey(AuthUser,to_field='username',db_column='Emp_Id',null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    notification_id=models.ForeignKey(Notification,to_field='sno',db_column='notification_id',null=True,on_delete=models.SET_NULL) 
    read_status=models.IntegerField(db_column="read_status",null=True,blank=True,default=0)

    class Meta:
        db_table = 'Notification_status'


class LogRecord(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)
    emp_id = models.ForeignKey(AuthUser,to_field='username',db_column='Emp_Id',null=True,on_delete=models.SET_NULL,blank=True)  # Field name made lowercase.
    db_table=models.CharField(db_column="db_table",max_length=250,null=True,blank=True)
    operation=models.CharField(db_column="operation",max_length=10,null=True,blank=True)
    previous_values=models.TextField(db_column="previous_values",null=True,blank=True)
    new_or_inserted_values=models.TextField(db_column="new_or_inserted_values",null=True,blank=True)
    timestamp=models.DateTimeField(db_column="timestamp",auto_now_add=True)

    class Meta:
        db_table = 'LogRecord'

class MailService(models.Model):
    send_to=models.CharField(db_column='send_to',null=True,max_length=100)
    subject=models.TextField(db_column='subject',null=True)
    message=models.TextField(db_column='message',null=True)
    status=models.CharField(db_column='status',default='N',max_length=2)
    timestamp=models.DateTimeField(db_column="timestamp",auto_now_add=True)

    class Meta:
        db_table = 'MailService'

class fcm(models.Model):
    username = models.ForeignKey(AuthUser, to_field='username',db_column='username',null=True,on_delete=models.SET_NULL)
    fcm_token = models.CharField(max_length=1000, null=True, default=None)
    device_id = models.CharField(max_length=40, null=True, default=None)
    application = models.CharField(max_length=40, null=True, default=None)

    class Meta:
        db_table = 'fcm'

class external_login(models.Model):
    username = models.CharField(db_column='username',max_length=20)
    device_ip = models.CharField(db_column='device_ip',max_length=20)
    timestamp = models.DateTimeField(db_column='timestamp',auto_now_add=True)

    class Meta:
        db_table = 'external_login'