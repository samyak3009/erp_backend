# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django_mysql.models import JSONField
from login.models import EmployeeDropdown,EmployeePrimdetail
from musterroll.models import EmployeeSeparation,NoDuesHead,NoDuesEmp


class SeparationReporting(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='SeparationReporting_emp_id', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    reporting_to = models.ForeignKey(EmployeeDropdown,db_column='Reporting_To', related_name='SeparationReporting_Designation', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    department = models.ForeignKey(EmployeeDropdown,db_column='Department', related_name='SeparationReporting_Department', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    reporting_no = models.IntegerField(db_column='Reporting_No', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'SeparationReporting'


class SeparationApplication(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='emp_id',related_name='SeparationApplication_emp_id', on_delete=models.SET_NULL,null=True)
    separation_type = models.ForeignKey(EmployeeDropdown,db_column='separation_type',related_name='SeparationApplication_separation_type',on_delete=models.SET_NULL,null=True)
    relieving_date = models.DateTimeField(db_column='relieving_date')
    rejoin_date = models.DateTimeField(db_column='rejoin_date',null=True)
    remark = models.TextField(db_column='remark',blank=True,null=True)
    resignation_doc = models.CharField(db_column='resignation_doc',null=True,max_length=1000)
    document = models.CharField(db_column='document',null=True,max_length=1000)
    current_level = models.IntegerField(db_column='current_level',default=0,null=True)#form at reporting level
    approval_status = models.CharField(db_column='approval_status',null=True,blank=True,max_length=25)#PENDING
    status = models.CharField(db_column='status',default="INSERT",null=True,blank=True,max_length=25)

    class Meta:
        db_table = 'Employee_SeparationApplication'
        managed = True


class SeparationLevelApproval(models.Model):
    form_id = models.ForeignKey(EmployeeSeparation,db_column='form_id',related_name='SeparationApplication_form_id',on_delete=models.SET_NULL,null=True)
    approved_by = models.ForeignKey(EmployeePrimdetail,db_column='approved_by',related_name='SeparationLevelApproval_approved_by',on_delete=models.SET_NULL,null=True)
    approval_status = models.CharField(db_column='approval_status',default='PENDING',max_length=20)#APPROVED HOLD CANCELED PENDING
    remark = models.TextField(db_column='remark',null=True)
    level = models.IntegerField(db_column='level',null=True)
    status = models.CharField(db_column='status',default='INSERT',max_length=20)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = 'Employee_SeparationLevelApproval'
        managed = True


class SeparationExitQuestionPaper(models.Model):
    emp_category  = models.ForeignKey(EmployeeDropdown,db_column='emp_category',related_name='SeparationExitQuestionPaper_emp_category',on_delete=models.SET_NULL,null=True)
    title = models.CharField(db_column='title',null=True,max_length=2000)
    expiry_date = models.CharField(db_column='expiry_date',null=True,max_length=50)
    added_by = models.ForeignKey(EmployeePrimdetail,db_column='added_by', related_name='SeparationExitQuestionPaper_added_by', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='time_stamp',auto_now=True)
    class Meta:
        db_table='Employee_SeparationExitQuestionPaper'
        managed = True

class SeparationQuestions(models.Model):
    paper_id = models.ForeignKey(SeparationExitQuestionPaper,db_column='paper_id',related_name='SeparationQuestions_paper_id',on_delete=models.SET_NULL,null=True)
    p_ques_id  = models.IntegerField(db_column='p_ques_id',null=True)
    ques_no = models.IntegerField(db_column='ques_no',null=True)
    description = models.TextField(db_column='description',null=True)
    answer_type = JSONField()

    class Meta:
        db_table = 'Employee_SeprationQuestions'
        managed = True

class SeparationResponse(models.Model):
    paper_id = models.ForeignKey(SeparationExitQuestionPaper,db_column='paper_id',related_name='SeparationResponse_paper_id',on_delete=models.SET_NULL,null=True)
    form_id = models.ForeignKey(SeparationApplication,db_column='form_id',related_name='SeparationResponse_form_id',on_delete=models.SET_NULL,null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='SeparationResponse_emp_id', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='time_stamp',auto_now=True)
    status = models.CharField(db_column='status',default='INSERT',max_length=20)

    class Meta:
        db_table = 'Employee_SeprationResponse'
        managed = True

class SeparationAnswers(models.Model):
    resp_id = models.ForeignKey(SeparationResponse,db_column='resp_id',related_name='SeparationAnswers_resp_id',on_delete=models.SET_NULL,null=True)
    ques_id = models.ForeignKey(SeparationQuestions,db_column='ques_id',related_name='SeparationAnswers_ques_id',on_delete=models.SET_NULL,null=True)
    answer = JSONField()

    class Meta:
        db_table = 'Employee_SeprationAnswers'
        managed = True


class SeparationExitPaper(models.Model):
    paper_attr=JSONField()

    class Meta:
        db_table = 'Employee_SeparationExitPaper'
        managed = True
