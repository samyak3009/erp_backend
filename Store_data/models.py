from django.db import models
import datetime
from datetime import date, timedelta
# Create your models here.
from Registrar.models import *
from login.models import EmployeePrimdetail
from StudentMMS.models import *
from StudentAcademics.models import *


##########################################################################################################################################################
########################################################################## 1819o #########################################################################
##########################################################################################################################################################
# class Store_Attendance_Ctwise_1819o(models.Model):
#     uniq_id = models.ForeignKey(studentSession_1819o, related_name="uniq_id_store_att_ctwise_1819o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
#     exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_store_att_ctwise_1819o', null=True, on_delete=models.SET_NULL)
#     subject = models.ForeignKey(SubjectInfo_1819o, related_name="subject_store_att_ctwise_1819o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
#     att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_ctwise_1819o', null=True, on_delete=models.SET_NULL)
#     attendance_total = models.CharField(max_length=50, blank=True, null=True)
#     attendance_present = models.CharField(max_length=50, blank=True, null=True)
#     status = models.CharField(max_length=20, default='INSERT')
#     timestamp = models.DateTimeField(auto_now=True)

#     class Meta:
#         managed = True
#         db_table = 'Store_Attendance_Ctwise_1819o'


# class Store_Attendance_Total_Attwise_1819o(models.Model):
#     uniq_id = models.ForeignKey(studentSession_1819o, related_name="uniq_id_store_att_total_attwise_1819o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
#     subject = models.ForeignKey(SubjectInfo_1819o, related_name="subject_store_att_total_attwise_1819o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
#     att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_attwise_1819o', null=True, on_delete=models.SET_NULL)
#     attendance_total = models.CharField(max_length=50, blank=True, null=True)
#     attendance_present = models.CharField(max_length=50, blank=True, null=True)
#     status = models.CharField(max_length=20, default='INSERT')
#     timestamp = models.DateTimeField(auto_now=True)

#     class Meta:
#         managed = True
#         db_table = 'Store_Attendance_Total_Attwise_1819o'


class Store_Attendance_Total_1819o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819o, related_name="uniq_id_store_att_total_1819o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1819o, related_name="subject_store_att_total_1819o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    # att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_1920e', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Total_1819o'


class Store_Attendance_1819o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819o, related_name="uniq_id_store_att_1819o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_1819o'

##########################################################################################################################################################
########################################################################## 1819e #########################################################################
##########################################################################################################################################################
# class Store_Attendance_Ctwise_1819e(models.Model):
#     uniq_id = models.ForeignKey(studentSession_1819e, related_name="uniq_id_store_att_ctwise_1819e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
#     exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_store_att_ctwise_1819e', null=True, on_delete=models.SET_NULL)
#     subject = models.ForeignKey(SubjectInfo_1819e, related_name="subject_store_att_ctwise_1819e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
#     att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_ctwise_1819e', null=True, on_delete=models.SET_NULL)
#     attendance_total = models.CharField(max_length=50, blank=True, null=True)
#     attendance_present = models.CharField(max_length=50, blank=True, null=True)
#     status = models.CharField(max_length=20, default='INSERT')
#     timestamp = models.DateTimeField(auto_now=True)

#     class Meta:
#         managed = True
#         db_table = 'Store_Attendance_Ctwise_1819e'


# class Store_Attendance_Total_Attwise_1819e(models.Model):
#     uniq_id = models.ForeignKey(studentSession_1819e, related_name="uniq_id_store_att_total_attwise_1819e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
#     subject = models.ForeignKey(SubjectInfo_1819e, related_name="subject_store_att_total_attwise_1819e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
#     att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_attwise_1819e', null=True, on_delete=models.SET_NULL)
#     attendance_total = models.CharField(max_length=50, blank=True, null=True)
#     attendance_present = models.CharField(max_length=50, blank=True, null=True)
#     status = models.CharField(max_length=20, default='INSERT')
#     timestamp = models.DateTimeField(auto_now=True)

#     class Meta:
#         managed = True
#         db_table = 'Store_Attendance_Total_Attwise_1819e'


class Store_Attendance_Total_1819e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819e, related_name="uniq_id_store_att_total_1819e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1819e, related_name="subject_store_att_total_1819e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    # att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_1920e', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Total_1819e'


class Store_Attendance_1819e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819e, related_name="uniq_id_store_att_1819e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_1819e'

##########################################################################################################################################################
########################################################################## 1920o #########################################################################
##########################################################################################################################################################

class Store_Ctmarks_RuleWise_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="uniq_id_store_int_ctwise_1920o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_store_int_ctwise_1920o', null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920o, related_name="subject_store_int_ctwise_1920o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    ct_marks_obtained = models.CharField(max_length=50, blank=True, null=True)
    ct_marks_total = models.CharField(max_length=50, blank=True, null=True)
    rule_id = models.ForeignKey(CTMarksRules_1920o, related_name="rule_store_int_ctwise_1920o", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Ctmarks_RuleWise_1920o'


class Store_Internal_Total_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="uniq_id_store_int_total_1920o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920o, related_name="subject_store_int_total_1920o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    total_ct_marks = models.CharField(max_length=50, blank=True, null=True)
    total_ta_marks = models.CharField(max_length=50, blank=True, null=True)
    total_att_marks = models.CharField(max_length=50, blank=True, null=True)
    total_bonus_marks = models.CharField(max_length=50, blank=True, null=True)
    total_extra_bonus = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Internal_Total_1920o'


class Store_Attendance_Ctwise_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="uniq_id_store_att_ctwise_1920o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_store_att_ctwise_1920o', null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920o, related_name="subject_store_att_ctwise_1920o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_ctwise_1920o', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Ctwise_1920o'


class Store_Attendance_Total_Attwise_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="uniq_id_store_att_total_attwise_1920o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920o, related_name="subject_store_att_total_attwise_1920o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_attwise_1920o', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Total_Attwise_1920o'


class Store_Attendance_Total_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="uniq_id_store_att_total_1920o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920o, related_name="subject_store_att_total_1920o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    # att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_1920o', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Total_1920o'


class Store_Attendance_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="uniq_id_store_att_1920o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_1920o'

##########################################################################################################################################################
########################################################################## 1920e #########################################################################
##########################################################################################################################################################


class Store_Ctmarks_RuleWise_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name="uniq_id_store_int_ctwise_1920e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_store_int_ctwise_1920e', null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920e, related_name="subject_store_int_ctwise_1920e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    ct_marks_obtained = models.CharField(max_length=50, blank=True, null=True)
    ct_marks_total = models.CharField(max_length=50, blank=True, null=True)
    rule_id = models.ForeignKey(CTMarksRules_1920e, related_name="rule_store_int_ctwise_1920e", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Ctmarks_RuleWise_1920e'


class Store_Internal_Total_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name="uniq_id_store_int_total_1920e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920e, related_name="subject_store_int_total_1920e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    total_ct_marks = models.CharField(max_length=50, blank=True, null=True)
    total_ta_marks = models.CharField(max_length=50, blank=True, null=True)
    total_att_marks = models.CharField(max_length=50, blank=True, null=True)
    total_bonus_marks = models.CharField(max_length=50, blank=True, null=True)
    total_extra_bonus = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Internal_Total_1920e'


class Store_Attendance_Ctwise_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name="uniq_id_store_att_ctwise_1920e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_store_att_ctwise_1920e', null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920e, related_name="subject_store_att_ctwise_1920e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_ctwise_1920e', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Ctwise_1920e'


class Store_Attendance_Total_Attwise_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name="uniq_id_store_att_total_attwise_1920e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920e, related_name="subject_store_att_total_attwise_1920e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_attwise_1920e', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Total_Attwise_1920e'


class Store_Attendance_Total_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name="uniq_id_store_att_total_1920e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920e, related_name="subject_store_att_total_1920e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    # att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_1920e', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Total_1920e'


class Store_Attendance_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name="uniq_id_store_att_1920e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_1920e'


################################################################################################################################################################################################################################################################################################################################################################################################
##################################################################################2021o#########################################################################################################################################################################################################################################################################################################
##############################################################################################################################################################################




class Store_Ctmarks_RuleWise_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="uniq_id_store_int_ctwise_2021o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_store_int_ctwise_2021o', null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_2021o, related_name="subject_store_int_ctwise_2021o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    ct_marks_obtained = models.CharField(max_length=50, blank=True, null=True)
    ct_marks_total = models.CharField(max_length=50, blank=True, null=True)
    rule_id = models.ForeignKey(CTMarksRules_2021o, related_name="rule_store_int_ctwise_2021o", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Ctmarks_RuleWise_2021o'


class Store_Internal_Total_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="uniq_id_store_int_total_2021o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_2021o, related_name="subject_store_int_total_2021o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    total_ct_marks = models.CharField(max_length=50, blank=True, null=True)
    total_ta_marks = models.CharField(max_length=50, blank=True, null=True)
    total_att_marks = models.CharField(max_length=50, blank=True, null=True)
    total_bonus_marks = models.CharField(max_length=50, blank=True, null=True)
    total_extra_bonus = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Internal_Total_2021o'


class Store_Attendance_Ctwise_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="uniq_id_store_att_ctwise_2021o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_store_att_ctwise_2021o', null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_2021o, related_name="subject_store_att_ctwise_2021o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_ctwise_2021o', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Ctwise_2021o'


class Store_Attendance_Total_Attwise_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="uniq_id_store_att_total_attwise_2021o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_2021o, related_name="subject_store_att_total_attwise_2021o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_attwise_2021o', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Total_Attwise_2021o'


class Store_Attendance_Total_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="uniq_id_store_att_total_2021o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_2021o, related_name="subject_store_att_total_2021o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    # att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_store_att_total_1920e', null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_Total_2021o'


class Store_Attendance_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="uniq_id_store_att_2021o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    attendance_total = models.CharField(max_length=50, blank=True, null=True)
    attendance_present = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Store_Attendance_2021o'