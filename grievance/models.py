# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from login.models import EmployeeDropdown,EmployeePrimdetail
from datetime import datetime

# Create your models here.
class GrievanceData(models.Model):
    gri_id = models.AutoField(primary_key=True)
    gri_date = models.DateTimeField(blank=True, null=True)
    gri_message = models.TextField()
    remark_hod = models.TextField(db_column='remark_HOD', blank=True, null=True,default='PENDING')  # Field name made lowercase.
    status_hod = models.TextField(db_column='status_HOD', blank=True, null=True,default='PENDING')  # Field name made lowercase.
    hod_responsedate = models.DateTimeField(blank=True, null=True)
    remark_hr = models.TextField(db_column='remark_HR', blank=True, null=True,default='PENDING')  # Field name made lowercase.
    status_hr = models.TextField(db_column='status_HR', blank=True, null=True,default='PENDING')  # Field name made lowercase.
    hr_responsedate = models.DateTimeField(blank=True, null=True)
    #code = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True,default='PENDING')
    document = models.CharField(max_length=100, blank=True, null=True)
    empid = models.ForeignKey(EmployeePrimdetail,db_column='emp_id',related_name='emp',on_delete=models.SET_NULL,blank=True, null=True)
    type = models.ForeignKey(EmployeeDropdown,db_column='type',related_name='gr_type',on_delete=models.SET_NULL,blank=True, null=True)
    designation = models.ForeignKey(EmployeeDropdown,db_column='desg',related_name='desg',on_delete=models.SET_NULL,blank=True, null=True)
    department = models.ForeignKey(EmployeeDropdown,db_column='dept',related_name='dept',on_delete=models.SET_NULL,blank=True, null=True)
    class Meta:
        db_table = 'grievance'
        managed= True

'''class grievance_info(models.Model):
    gri_id = models.AutoField(db_column='Gri_Id', primary_key=True)  # Field name made lowercase.
    gri_date = models.DateField(db_column='Gri_Date')  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=35)  # Field name made lowercase.
    message = models.TextField(db_column='Message')  # Field name made lowercase.
    emp_id = models.CharField(db_column='Emp_Id', max_length=20)  # Field name made lowercase.
    document = models.CharField(db_column='Document', max_length=100)  # Field name made lowercase.
    feedback = models.TextField(db_column='Feedback')  # Field name made lowercase.

    class Meta:
        db_table = 'grievance_info'

class grievance_status(models.Model):
    r_id = models.AutoField(db_column='R_Id', primary_key=True)  # Field name made lowercase.
    gid = models.IntegerField(db_column='Gid', null=True, blank=True)  # Field name made lowercase.
    repto = models.IntegerField(db_column='Repto', blank=True, null=True)  # Field name made lowercase.
    department = models.IntegerField(db_column='Department', blank=True, null=True)  # Field name made lowercase.
    reporting_level = models.IntegerField(db_column='Reporting_Level', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    solve_date = models.DateField(db_column='Solve_Date', blank=True, null=True)  # Field name made lowercase.
    remark = models.TextField(db_column='Remark', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'grievance_status'''
