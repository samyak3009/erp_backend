# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from Registrar.models import studentSession_1819o, studentSession_1920o,studentSession_2021o, StudentDropdown, Semtiming, CourseDetail
from Accounts.models import AccountsDropdown
from login.models import EmployeePrimdetail
from StudentAcademics.models import *
from django.db import models

# Create your models here.


class LessonTopicDetail_2021o(models.Model):
    unit = models.CharField(db_column='unit', blank=True, null=True, max_length=20)
    subject = models.ForeignKey(SubjectInfo_2021o, related_name="LessonPlan_LessonTopicDetail_2021o_subject", blank=True, on_delete=models.SET_NULL, null=True)
    topic_name = models.TextField()
    status = models.CharField(max_length=20, default="INSERT")

    class Meta:
        managed = True
        db_table = 'LessonPlanTopicDetails_2021o'


class LessonPropose_2021o(models.Model):
    subject = models.ForeignKey(SubjectInfo_2021o, related_name="LessonPlan_LessonPropose_2021o_subject", on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Sections, related_name="LessonPlan_LessonPropose_2021o_section", blank=True, null=True, on_delete=models.SET_NULL)
    lecture_tutorial = models.CharField(max_length=5, default='N')  # 'L' for lecture, 'T' for tutorial
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="LessonPlan_LessonPropose_2021odd_added_by", blank=True, null=True, on_delete=models.SET_NULL)
    session = models.ForeignKey(Semtiming, related_name='LessonPlan_LessonPropose_2021o_session', db_column='session', null=True, on_delete=models.SET_NULL, default=1)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(default=timezone.now)
    isgroup=models.CharField(max_length=5,default='N')
    group_id=models.ForeignKey(SectionGroupDetails_2021o,related_name="LessonPlan_Gid",null=True,on_delete=models.SET_NULL)
    class Meta:
        managed = True
        db_table = 'LessonPlanPropose_2021o'


class LessonProposeRemark_2021o(models.Model):
    propose_detail = models.ForeignKey(LessonPropose_2021o, related_name='LessonPlan_LessonProposeRemark_2021o_propose_detail', blank=True, null=True, on_delete=models.SET_NULL)
    remark = models.TextField()
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'LessonPlanProposeRemark_2021o'
        managed = True


class LessonProposeDetail_2021o(models.Model):
    lesson_propose = models.ForeignKey(LessonPropose_2021o, related_name='LessonPlan_LessonProposeDetail_2021_lesson_propose', blank=True, null=True, on_delete=models.SET_NULL)
    lno = models.IntegerField(db_column='lno')
    schedule_date = models.DateField(db_column='schedule_date', max_length=500, blank=True, null=True)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="LessonPlan_LessonProposeDetail_odd_added_by", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', null=True, max_length=10, default="INSERT")  # Formulatype, Valuebased
    time_stamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'LessonPlanProposeDetail_2021o'
        managed = True


class LessonProposeTopics_2021o(models.Model):
    propose_detail = models.ForeignKey(LessonProposeDetail_2021o, related_name='LessonPlan_LessonProposeTopics_2021o_propose_detail', null=True, on_delete=models.SET_NULL)
    propose_topic = models.ForeignKey(LessonTopicDetail_2021o, related_name='LessonPlan_LessonProposeTopics_2021o_propose_topic', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'LessonPlanTopics_2021o'


class LessonProposeBTLevel_2021o(models.Model):
    propose_detail = models.ForeignKey(LessonProposeDetail_2021o, related_name='LessonPlan_LessonProposeBTLevel_2021o_propose_detail', blank=True, null=True, on_delete=models.SET_NULL)
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='LessonPlan_LessonProposeBTLevel_2021o_bt_level', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'LessonPlanBTLevel_2021o'


class LessonProposeApproval_2021o(models.Model):
    propose_detail = models.ForeignKey(LessonProposeDetail_2021o, related_name='LessonPlan_LessonProposeApproval_2021o_propose_detail', blank=True, null=True, on_delete=models.SET_NULL)
    remark = models.TextField()
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name='LessonPlan_LessonProposeApproval_2021o_approved_by', blank=True, null=True, on_delete=models.SET_NULL)
    approval_date = models.DateTimeField(db_column='approval_date', blank=True, null=True)
    approval_status = models.CharField(db_column='approval_status', null=True, max_length=10, default="PENDING")
    status = models.CharField(db_column='status', null=True, max_length=10, default="INSERT")

    class Meta:
        db_table = 'LessonPlanApproval_2021o'
        managed = True

class LessonCompletedDetail_2021o(models.Model):
    lno = models.IntegerField(db_column='lno')
    lecture_details=models.ForeignKey(Attendance_2021o,related_name ="LessonPlan_LessonCompletedDetail_2021o_lecture_details", blank=True,null=True,on_delete=models.SET_NULL)
    status=models.CharField(db_column='status',null=True,max_length = 10,default="INSERT")
    approval_status = models.CharField(db_column='approval_status', default="PENDING", max_length=20)
    approved_by = models.ForeignKey(EmployeePrimdetail,related_name='LessonPlan_LessonCompletedDetail_2021o_approved_by',blank=True,null=True,on_delete=models.SET_NULL)
    session=models.ForeignKey(Semtiming,related_name='LessonPlan_LessonCompletedDetail_2021o_session',db_column='session',null=True,on_delete=models.SET_NULL,default=1)
    lecture_tutorial = models.CharField(max_length=5, default='N')  # 'L' for lecture,'T' for tutorial

    class Meta:
        db_table = 'LessonPlanCompletedDetail_2021o'
        managed = True

class LessonCompletedTopic_2021o(models.Model):
    completed_topic = models.ForeignKey(LessonTopicDetail_2021o ,related_name='LessonPlan_LessonCompletedTopic_2021o_completed_topic',blank=True,null=True,on_delete=models.SET_NULL)
    completed_detail = models.ForeignKey(LessonCompletedDetail_2021o,related_name='LessonPlan_LessonCompletedTopic_2021o_completed_detail',blank=True,null=True,on_delete=models.SET_NULL)
    time_stamp=models.DateTimeField(default=timezone.now)
    status=models.CharField(max_length=20,default="INSERT")

    class Meta:
        managed=True
        db_table='LessonCompletedTopic_2021o'

class LessonCompletedRemark_2021o(models.Model):
    propose_detail = models.ForeignKey(LessonPropose_2021o,related_name='LessonPlan_LessonCompletedRemark_2021o_propose_detail',blank=True,null=True,on_delete=models.SET_NULL)
    remark = models.TextField()
    status=models.CharField(max_length=20,default="INSERT")

    class Meta:
        db_table = 'LessonPlanCompletedRemark_2021o'
        managed = True

class LessonCompletedApproval_2021o(models.Model):
    completed_detail = models.ForeignKey(LessonCompletedDetail_2021o,related_name='LessonPlan_LessonCompletedApproval_2021o_completed_detail',blank=True,null=True,on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(EmployeePrimdetail,related_name='LessonPlan_LessonCompletedApproval_2021o_approved_by',blank=True,null=True,on_delete=models.SET_NULL)
    remark = models.TextField()
    status=models.CharField(db_column='status',null=True,max_length=10,default="INSERT")
    approval_date = models.DateTimeField(db_column='ApprovalDate', blank=True, null=True)

    class Meta:
        db_table = 'LessonPlanCompletedApproval_2021o'
        managed = True
