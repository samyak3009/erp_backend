# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from Registrar.models import StudentPrimDetail
from login.models import EmployeePrimdetail

class RedressalDropdown(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='Pid', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=500, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=500, blank=True, null=True)  # Field name made lowercase.
    is_edit = models.IntegerField(db_column='Is_Edit',default='1')  # Field name made lowercase.
    is_delete = models.IntegerField(db_column='Is_Delete',default='1')  # Field name made lowercase.
    status=models.CharField(db_column='status',null=True,max_length=10,default="INSERT")## Formulatype, Valuebased

    class Meta:
        db_table = 'RedressalDropdown'
        managed = True

class RedressalPriority(models.Model):
    priority = models.ForeignKey(RedressalDropdown,related_name='RedreCoord_pri', db_column='Priority',on_delete=models.SET_NULL, null=True)
    hours = models.IntegerField(db_column="hours",null=True,default=None)
    status=models.CharField(db_column='status',null=True,max_length=10,default="INSERT")## Formulatype, Valuebased
    added_by = models.ForeignKey(EmployeePrimdetail,related_name="RedrePri_added_by", db_column='Added_by', null=True, blank=True,on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'RedressalPriority'
        managed = True

class RedressalCoordinator(models.Model):
    category = models.ForeignKey(RedressalDropdown,related_name='RedreCoord_category', db_column='Category',on_delete=models.SET_NULL, null=True)
    subCategory = models.ForeignKey(RedressalDropdown,related_name='RedreCoord_subCategory', db_column='Sub_category',on_delete=models.SET_NULL, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail,related_name="RedreCoord_emp_id",null=True,on_delete=models.SET_NULL)
    added_by = models.ForeignKey(EmployeePrimdetail,related_name="RedreCoord_added_by", db_column='Added_by', null=True, blank=True,on_delete=models.SET_NULL)
    status = models.CharField(max_length=20,default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'RedressalCoordinator'


class RedressalInsert(models.Model):
    grievance_ticket_num = models.CharField(max_length=100,db_column='grievance_ticket_num',default=None,null=True)
    category = models.ForeignKey(RedressalDropdown,related_name='RedreIns_category', db_column='Category',on_delete=models.SET_NULL, null=True)
    subCategory = models.ForeignKey(RedressalDropdown,related_name='RedreIns_subCategory', db_column='Sub_category',on_delete=models.SET_NULL, null=True)
    priority = models.ForeignKey(RedressalPriority,related_name='RedreIns_priority', db_column='Priority',on_delete=models.SET_NULL, null=True)
    #title = models.TextField(null=True,default=None,db_column='title')
    description = models.TextField(db_column='description',null=True,default=None)
    attachment = models.CharField(db_column='attachment', max_length=500, blank=True, null=True)  # Field name made lowercase.
    final_status = models.CharField(max_length=20,db_column='final_status',default='PENDING') ####### 'PENDING'/'CLOSED'
    griev_sugg = models.CharField(max_length=20,db_column='griev_sugg',default='G') ##### 'G' for GRIEVACE and 'S' for suggestion 
    grievance_type = models.CharField(max_length=20,db_column='grievance_type',default='N') ##### 'N' for normal grievance and 'R' for reopened grievance ###########
    uniq_id = models.ForeignKey(StudentPrimDetail,db_column='uniq_id',null=True,default=None,on_delete=models.SET_NULL)
    feedback = models.CharField(max_length=20,db_column='feedback',default='PENDING')  ### 'S' for Satisfied / 'NS' for Not-Satisfied
    status = models.CharField(max_length=20,db_column='status',default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'RedressalInsert'
        
        
class RedressalApproval(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,related_name="RedreApp_emp_id",null=True,on_delete=models.SET_NULL) ### coordinator/forwarded to emp_id
    redressal_id = models.ForeignKey(RedressalInsert,related_name="RedressalApp_Insert_id",null=True,on_delete=models.SET_NULL)
    remark = models.TextField(null=True,default=None)
    coord_status=models.CharField(max_length=50,default='PENDING') ###### 'CLOSED'/'PENDING'/'FORWARDED'
    action_time = models.DateTimeField(null=True,default=None)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'RedressalApproval'