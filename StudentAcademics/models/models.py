# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from Registrar.models import *
from django.utils import timezone
from login.models import EmployeePrimdetail
# Create your models here.

# Create your models here.


class StudentAcademicsDropdown(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='Pid', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=500, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=500, blank=True, null=True)  # Field name made lowercase.
    is_edit = models.IntegerField(db_column='Is_Edit', default=1)  # Field name made lowercase.
    is_delete = models.IntegerField(db_column='Is_Delete', default=0)  # Field name made lowercase.
    status = models.CharField(db_column='status', null=True, max_length=10, default="INSERT")  # Formulatype, Valuebased
    session = models.ForeignKey(Semtiming, related_name='AcademicDropdownSession', db_column='session', null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'StuAcadDropdown'
        managed = True


class SemesterCommencement(models.Model):
    session = models.ForeignKey(Semtiming, related_name='CommencementSession', db_column='session', null=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(StudentDropdown, related_name='SemesterComm_Course_id', db_column='Course_id', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    year = models.IntegerField(default=-1)  # Field name made lowercase.
    commencement_date = models.DateField()
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="SemesterComm_emp", db_column='Added_By', null=True, blank=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuAcadSemCommencement'
        managed = True


class AttendanceSettings(models.Model):
    session = models.ForeignKey(Semtiming, related_name='AttSettSession', db_column='session', null=True, on_delete=models.SET_NULL)
    # attendance_type=models.ForeignKey(StudentAcademicsDropdown,related_name="att_type",null=True,on_delete=models.SET_NULL)
    att_sub_cat = models.ForeignKey(StudentAcademicsDropdown, related_name="att_sub_category", null=True, on_delete=models.SET_NULL)
    attendance_category = models.ForeignKey(StudentAcademicsDropdown, related_name="att_category", null=True, on_delete=models.SET_NULL)
    admission_type = models.ForeignKey(StudentDropdown, related_name='AttSett_Admission_type', db_column='Admission_type', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    course = models.ForeignKey(StudentDropdown, related_name='AttSett_Course_id', db_column='Course_id', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    year = models.IntegerField(default=-1)  # Field name made lowercase.
    att_per = models.FloatField()
    criteria_per = models.FloatField()  # Field name made lowercase.
    lock_type = models.CharField(max_length=2, default="N")
    days_lock = models.IntegerField()
    att_to_be_approved = models.CharField(max_length=2, default="N")
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="AttSett_emp", db_column='Added_By', null=True, blank=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuAcadAttSettings'
        managed = True


class StudentRemarks(models.Model):
    session = models.ForeignKey(Semtiming, related_name='StudentRemarks_session', db_column='session', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(StudentPrimDetail, related_name='StudentRemarks_uniq_id', db_column='uniq_id', on_delete=models.SET_NULL, null=True)
    remark = models.TextField(db_column='remark')
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="StudentRemarks_added_by", db_column='added_by', null=True, blank=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuAcadStudentRemarks'
        managed = True
