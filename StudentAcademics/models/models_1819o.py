# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from Registrar.models import *
from django.utils import timezone
from login.models import EmployeePrimdetail
from StudentAcademics.models import *
# Create your models here.

# Create your models here.

######################################################## 1819o models ##########################################################################
################################################################################################################################################
class TimeTableSlots_1819o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='TT1819Session', db_column='session', null=True, on_delete=models.SET_NULL)
    sem = models.ForeignKey(StudentSemester, related_name='TimeTableSlots_1819o_sem', db_column='Sem_id', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    day = models.IntegerField()  # 0 for monday,1 for tuesday etc. use calendar.day_name[1]='Tuesday'
    num_lecture_slots = models.IntegerField()
    dean_approval_status = models.CharField(max_length=20, default="PENDING")
    remark = models.CharField(max_length=200, default=None, null=True)
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="TT1819_emp", db_column='Added_By', null=True, blank=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuAcadTTSlots_1819o'


class SectionGroupDetails_1819o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='SecDet1819Session', db_column='session', null=True, on_delete=models.SET_NULL)
    group_type = models.CharField(max_length=20, default="INTER")  # INTER OR INTRA FOR  intersection and intrasection respectively
    group_name = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="Group1819_emp", db_column='Added_By', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)
    type_of_group = models.CharField(max_length=20, default="ACADEMICS")  # type_of_group=ACADEMICS OR MENTOR

    class Meta:
        managed = True
        db_table = 'StuAcadGroupDetails_1819o'


class GroupSection_1819o(models.Model):
    group_id = models.ForeignKey(SectionGroupDetails_1819o, related_name="GS1819", null=True, on_delete=models.SET_NULL)
    section_id = models.ForeignKey(Sections, related_name="GS1819", null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'StuAcadGroupSection_1819o'


class StuGroupAssign_1819o(models.Model):
    group_id = models.ForeignKey(SectionGroupDetails_1819o, related_name="GAS1819", null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819o, related_name='stu_grp_fee_uniq', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="StuGroup1_emp", db_column='Added_By', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuGroupAssign_1819o'


class EmpGroupAssign_1819o(models.Model):
    group_id = models.ForeignKey(SectionGroupDetails_1819o, related_name="GAS18192", null=True, on_delete=models.SET_NULL)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name='stu_grp_fee_emp', db_column='Emp_Id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="StuGroup2_emp", db_column='Added_By', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'EmpGroupAssign_1819o'


class SubjectInfo_1819o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='SubInfo1819Session', db_column='session', null=True, on_delete=models.SET_NULL)
    sem = models.ForeignKey(StudentSemester, related_name='SubInfo_1819o_sem', db_column='Sem_id', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    subject_type = models.ForeignKey(StudentDropdown, related_name='SubInfoSubType', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    subject_unit = models.ForeignKey(StudentDropdown, related_name='SubInfoSubUnit', db_column='Subject_Unit', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    sub_alpha_code = models.CharField(max_length=50, null=True, default=None)
    sub_num_code = models.CharField(null=True, default=None, max_length=50)
    sub_name = models.CharField(max_length=500, null=True, default=None)
    max_ct_marks = models.FloatField()
    max_ta_marks = models.FloatField()
    max_att_marks = models.FloatField()
    max_university_marks = models.FloatField()
    no_of_units = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="SubInfo1819_emp", db_column='Added_By', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuAcadSubjectInfo_1819o'


class AcadCoordinator_1819o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='TTCoord1819Session', db_column='session', null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey(Sections, related_name='TimeTableCoord_1819o_section', db_column='section', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    subject_id = models.ForeignKey(SubjectInfo_1819o, related_name="AcadCoordinator_1819o_sub", on_delete=models.SET_NULL, null=True)
    coord_type = models.CharField(max_length=5, default=None)
    # 'T' for time table, 'C' for class, 'S' for subject, 'M' for mentor ###################3
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="TTCoord", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="TTCord1819_emp", db_column='Added_By', null=True, blank=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuAcadCoord_1819o'


class AcademicsCalendar_1819o(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)
    title = models.CharField(max_length=100, db_column='title',)
    start = models.DateField()
    end = models.DateField()
    type = models.ForeignKey(StudentAcademicsDropdown, db_column='type', related_name='type_academicsCalendar_1819o', max_length=11, on_delete=models.SET_NULL, null=True)
    color = models.CharField(max_length=20, db_column='color',)
    description = models.TextField(db_column='description', null=True, default=None)
    status = models.CharField(max_length=20, db_column='status', default='INSERT')

    class Meta:
        managed = True
        db_table = 'academicsCalendar_1819o'


class FacultyTime_1819o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='FacTime1819Session', db_column='session', null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey(Sections, related_name='FacSec_1819o', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="FacTime", null=True, on_delete=models.SET_NULL)
    subject_id = models.ForeignKey(SubjectInfo_1819o, related_name="FacTimeSub_id", on_delete=models.SET_NULL, null=True)
    lec_num = models.IntegerField()
    day = models.IntegerField()  # 0 for monday,1 for tuesday etc. use calendar.day_name[1]='Tuesday'
    status = models.CharField(max_length=20, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="FacT1819_emp", db_column='Added_By', null=True, blank=True, on_delete=models.SET_NULL)
    start_time = models.TimeField(default=None)
    end_time = models.TimeField(default=None)
    # from_date = models.DateField(default=None,null=True)
    # to_date = models.DateField(default=None,null=True)
    remark = models.CharField(max_length=20, default=None, null=True)
    hod_remark = models.CharField(max_length=20, default=None, null=True)
    hod_approval_time = models.DateTimeField(default=None, null=True)
    hod_status = models.CharField(max_length=20, default="PENDING")
    dean_remark = models.CharField(max_length=20, default=None, null=True)
    dean_status = models.CharField(max_length=20, default="PENDING")
    dean_approval_time = models.DateTimeField(default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuAcadFacTime_1819o'


class LockingUnlocking_1819o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='Lock1819Session', db_column='session', null=True, on_delete=models.SET_NULL)
    lock_type = models.CharField(default='A', max_length=5)
    section = models.ForeignKey(Sections, related_name='Lock_1819o', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="LockEmp", null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name="LockAttType", on_delete=models.SET_NULL, null=True)
    att_date_from = models.DateField(default=None, null=True)
    att_date_to = models.DateField(default=None, null=True)
    unlock_from = models.DateTimeField(default=None, null=True)
    unlock_to = models.DateTimeField(default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuAcadLockingUnlocking_1819o'


class Attendance_1819o(models.Model):
    date = models.DateField(default=None, null=True)
    lecture = models.IntegerField(default=1)
    section = models.ForeignKey(Sections, related_name='Att_1819o', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_1819o, related_name="AttSub_id", on_delete=models.SET_NULL, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="AttEmp", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_1819o, related_name="AttGid", null=True, on_delete=models.SET_NULL)
    normal_remedial = models.CharField(max_length=5, default='N')  # 'N' for normal, 'R' for remedial
    isgroup = models.CharField(max_length=5, default='N')
    ########### 'Y' if attendance is marked group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(default=timezone.now)
    app = models.CharField(max_length=2, default='N')
    constrain_key = models.CharField(max_length=100, default=0, db_column='constrain_key', null=True)

    class Meta:
        managed = True
        db_table = 'StuAcadAttendance_1819o'


class StudentAttStatus_1819o(models.Model):
    att_id = models.ForeignKey(Attendance_1819o, related_name='Att_id', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819o, related_name='Att_fee_uniq', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    present_status = models.CharField(max_length=2, default='A')
    ############# 'P' for present, 'A' for absent ###################################
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name="MarkAttType", on_delete=models.SET_NULL, null=True)
    att_category = models.ForeignKey(StudentAcademicsDropdown, related_name="MarkAttCateg", on_delete=models.SET_NULL, null=True)
    approval_status = models.CharField(max_length=20, default=None, null=True)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    marked_by = models.ForeignKey(EmployeePrimdetail, related_name="marked_by", null=True, on_delete=models.SET_NULL)
    recommended_by = models.ForeignKey(EmployeePrimdetail, related_name="att_recommended_by", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name="att_approved_by", null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)
    remark = models.TextField(default=None, null=True)

    class Meta:
        managed = True
        db_table = 'StuAcadAttStatus_1819o'
