# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from Registrar.models import StudentPrimDetail, StudentDropdown, Semtiming, StudentSemester, Sections, CourseDetail, studentSession_2021o
from login.models import EmployeePrimdetail
from StudentAcademics.models import *
# #Create your models here.


class StuFeedbackEligibility_2021o(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='FeedElig_sem_2021o', db_column='sem', on_delete=models.SET_NULL, null=True)
    eligible_att_per = models.FloatField()
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="FeedElig_emp_2021o", db_column='added_by', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuFeedbackEligibility_2021o'
        app_label = 'StudentFeedback'
        managed = True


class StuFeedbackAttributes_2021o(models.Model):
    subject_type = models.ForeignKey(StudentDropdown, related_name='FeedElig_category_type_2021o', db_column='subject_type', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, null=True)
    eligible_settings_id = models.ForeignKey(StuFeedbackEligibility_2021o, related_name='FeedSett_category_type_2021o', db_column='settings_id', on_delete=models.SET_NULL, null=True)
    residential_status = models.CharField(max_length=20, db_column='residential_status', null=True)  # 'D' for day scholar and 'H' for hosteller ###############
    gender = models.ForeignKey(StudentDropdown, related_name='FeedSett_gender_2021o', db_column='gender', on_delete=models.SET_NULL, null=True)
    min_marks = models.FloatField()
    max_marks = models.FloatField()

    class Meta:
        db_table = 'StuFeedbackAttributes_2021o'
        app_label = 'StudentFeedback'
        managed = True


class StuFeedback_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="FeedStu_uniq_id_2021o", db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    attendance_per = models.FloatField()
    locked = models.CharField(max_length=20, default="N")
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        app_label = 'StudentFeedback'
        db_table = 'StuFeedback_2021o'


class StuFeedbackRemark_2021o(models.Model):
    feedback_id = models.ForeignKey(StuFeedback_2021o, related_name="feedback_id_2021o", db_column='feedback_id', null=True, on_delete=models.SET_NULL)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="FeedFacStu_emp_id_2021o", db_column='emp_id', null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_2021o, related_name="FeedFacStu_subject_2021o", db_column='subject', null=True, on_delete=models.SET_NULL)
    total_lectures = models.IntegerField(default=0)  # Total lecture Faculty has completed
    remark = models.TextField(null=True, default=None)

    class Meta:
        managed = True
        app_label = 'StudentFeedback'
        db_table = 'StuFeedbackRemark_2021o'


class StuFeedbackMarks_2021o(models.Model):
    feedback_id = models.ForeignKey(StuFeedbackRemark_2021o, related_name="feedback_id_s_2021o", db_column='feedback_id', null=True, on_delete=models.SET_NULL)
    attribute = models.ForeignKey(StuFeedbackAttributes_2021o, related_name="FeedAttMark_attribute_2021o", db_column='attribute', null=True, on_delete=models.SET_NULL)
    marks = models.FloatField()

    class Meta:
        managed = True
        app_label = 'StudentFeedback'
        db_table = 'StuFeedbackMarks_2021o'