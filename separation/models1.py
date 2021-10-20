# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from login.models import EmployeeDropdown,EmployeePrimdetail
from musterroll.models import EmployeeSeparation,NoDuesHead,NoDuesEmp
#Create your models here.

class SeparationLog(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    relieving_date = models.DateTimeField(db_column='Relieving_date',auto_now_add=True)  # Field name made lowercase.
    rejoin_date = models.DateTimeField(db_column='Rejoin_date',auto_now_add=True)  # Field name made lowercase.
    separation = models.ForeignKey(EmployeeSeparation,db_column='Separation_id', related_name='separation_log_id',null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    
    class Meta:
        managed = True
        db_table = 'separation_log'

class SeparationApproval(models.Model):

    approved_by = models.CharField(db_column='Approved_by', max_length=150, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=100, blank=True, null=True,default='PENDING')  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=100, blank=True, null=True,default=None)  # Field name made lowercase.
    approvaldate = models.DateTimeField(db_column='ApprovalDate', blank=True, null=True,default=None)  # Field name made lowercase.
    reportinglevel = models.IntegerField(db_column='ReportingLevel', blank=True, null=True)  # Field name made lowercase.
    separation_id = models.ForeignKey(EmployeeSeparation,db_column='Separation_id', related_name='separation_approval_id',on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    dept = models.ForeignKey(EmployeeDropdown, db_column='Dept', related_name='separation_dept',blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    desg = models.ForeignKey(EmployeeDropdown, db_column='Desg', related_name='separation_desg',blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.

    class Meta:
    	db_table = 'SeparationApproval'
