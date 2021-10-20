# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from login.models import AarDropdown, EmployeeDropdown, EmployeePrimdetail
from Accounts.models import AccountsDropdown, AccountsSession
from Registrar.models import StudentDropdown

# INCREAMEN
# TABLE 1: BASIC DETAILS FOR THE INCREAMENT SETTINGS


# class AppraisalStaffIncrementSettings(models.Model):
#     salary_type = models.ForeignKey(AccountsDropdown, db_column='salary_type',
#                                     related_name='AppraisalStaffIncrementSettings_AccountsDropdown_salary_type', null=True, on_delete=models.SET_NULL)  # GRADE AND CONSOLIDATED
#     increment_type = models.CharField(
#         db_column='increment_type', max_length=50, blank=True)
#     # NO INCREMENT, NORMAL, SPECIAL, PROMOTION WITH NORMAL INCREAMENT,
#     # PROMOTION WITH SPECIAL INCREAMENT, PROMOTION WITHOUT INCREAMENT
#     value_type = models.CharField(
#         db_column='value_type', max_length=50, blank=True)  # PERCENTAGE OR AMOUNT
#     value = models.FloatField()  # PERCENTAGE OR AMOUNT
#     edit_by = models.ForeignKey(EmployeePrimdetail, related_name='AppraisalStaffIncrementSettings_EmployeePrimdetail_edit_by',
#                                 db_column='edit_by', null=True, on_delete=models.SET_NULL)
#     session = models.ForeignKey(AccountsSession, related_name='AppraisalStaffIncrementSettings_Semtiming',
#                                 db_column='session', null=True, on_delete=models.SET_NULL, default=1)
#     status = models.CharField(
#         db_column='Status', max_length=50, blank=True, default='INSERT')
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         managed = True
#         db_table = 'AppraisalStaff_IncrementSettings'

# TABLE 2: INCREAMENT SETTINGS APPLICABLE ON TYPE OF EMPLOYEES


# class AppraisalStaffIncrementApplicable(models.Model):
#     increment_setting = models.ForeignKey(AppraisalStaffIncrementSettings, db_column='increment_setting',
#                                           related_name='AppraisalStaffIncrementApplicable_StaffAppraisalStaffIncrementSettings_increment_setting', null=True, on_delete=models.SET_NULL)  # GRADE AND CONSOLIDATED
#     emp_category = models.ForeignKey(EmployeeDropdown, related_name='AppraisalStaffIncrementApplicable_EmployeeDropdown_emp_category',
#                                      blank=True, null=True, db_column='emp_category', on_delete=models.SET_NULL)
#     desg = models.ForeignKey(EmployeeDropdown, related_name='AppraisalStaffIncrementApplicable_EmployeeDropdown_desg',
#                              db_column='desg', blank=True, null=True, on_delete=models.SET_NULL)
#     cadre = models.ForeignKey(EmployeeDropdown, related_name='AppraisalStaffIncrementApplicable_EmployeeDropdown_cadre',
#                               db_column='cadre', blank=True, null=True, on_delete=models.SET_NULL)
#     ladder = models.ForeignKey(EmployeeDropdown, related_name='AppraisalStaffIncrementApplicable_EmployeeDropdown_ladder',
#                                db_column='ladder', blank=True, null=True, on_delete=models.SET_NULL)

#     class Meta:
#         managed = True
#         db_table = 'AppraisalStaff_IncrementApplicable'

# TABLE 3: INCREAMENT SETTINGS APPLICABLE ON COMPONENT OF INCOME


# class AppraisalStaffIncrementComponents(models.Model):
#     increment_setting = models.ForeignKey(AppraisalStaffIncrementSettings, db_column='increment_setting',
#                                           related_name='AppraisalStaffIncrementComponents_StaffAppraisalStaffIncrementSettings_increment_setting', null=True, on_delete=models.SET_NULL)  # GRADE AND CONSOLIDATED
#     increment_component = models.ForeignKey(AccountsDropdown, db_column='increment_component',
#                                             related_name='AppraisalStaffIncrementComponents_AccountsDropdown_increment_component', null=True, on_delete=models.SET_NULL)  # GRADE AND CONSOLIDATED

#     class Meta:
#         managed = True
#         db_table = 'AppraisalStaff_IncrementComponents'
# ############################# END ############################## INCREAM


# LOCKING A
class AppraisalStaffLockingUnlocking(models.Model):
    lock_type = models.CharField(
        default='INC', max_length=5)  # INC: INCREAMENT
    att_date_from = models.DateField(default=None, null=True)
    att_date_to = models.DateField(default=None, null=True)
    unlock_from = models.DateTimeField(default=None, null=True)
    unlock_to = models.DateTimeField(default=None, null=True)
    status = models.CharField(
        db_column='status', default='INSERT', max_length=20)
    unlocked_by = models.ForeignKey(EmployeePrimdetail, db_column='unlocked_by',
                                    related_name='unlocked_by', on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey(AccountsSession, related_name='AppraisalStaffLockingUnlocking_Semtiming_session',
                                db_column='session', null=True, on_delete=models.SET_NULL, default=1)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = 'AppraisalStaff_lockingunlocking'
        managed = True


class AppraisalStaffLockingUnlockingStatus(models.Model):
    locking_details = models.ForeignKey(AppraisalStaffLockingUnlocking, db_column='locking_details',
                                        related_name='AppraisalStaffLockingUnlockingStatus_StaffAppraisalStaffLockingUnlocking_locking_details', on_delete=models.SET_NULL, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id',
                               related_name='AppraisalStaffLockingUnlockingStatus_EmployeePrimdetail_emp_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(
        db_column='status', max_length=40, blank=True, null=True, default='INSERT')
    # MIND 'SESSION(FROM PARENT TABLE)' CHECK DURING FETCHING

    class Meta:
        db_table = 'AppraisalStaff_LockingUnlockingStatus'
        managed = True
# END ############################## LOCKING A

# QUES MAX M

    ################# NEED TO IMPLEMENT LIKE DROPDOWNS ########################


class AppraisalStaffQuestion(models.Model):
    # FORM S-BAND/ A-BAND/ EMG-BAND {Make static on frontend}
    form_type = models.CharField(
        db_column='form_type', max_length=500, blank=True, null=True)
    # FORM PART1/ PART2/ PART3 {Make static on frontend}
    form_part = models.CharField(
        db_column='form_part', max_length=500, blank=True, null=True)
    ques_id = models.AutoField(
        db_column='ques_id', primary_key=True)  # {ref: Sno}
    parent_ques = models.IntegerField(
        db_column='parent_ques', blank=True, null=True)  # {ref: pid}
    field = models.TextField(
        db_column='field', blank=True, null=True)  # {ref: field}
    # Similar to statement take input along with statement
    max_marks = models.IntegerField(db_column='max_marks', null=True)
    statement = models.TextField(
        db_column='statement', blank=True, null=True)  # {ref: Value}
    status = models.CharField(
        db_column='status', null=True, max_length=10, default='INSERT')
    session = models.ForeignKey(AccountsSession, related_name='AppraisalStaffQuestion_AccountsSession_session',
                                db_column='session', null=True, on_delete=models.SET_NULL, default=1)

    class Meta:
        db_table = 'AppraisalStaff_Question'
        managed = True
        '''
        Field except form_type, form_part are just need to work like dropdown
        '''
# END ############################## QUES MAX

# ENTRY POIN


class AppraisalStaffApplication(models.Model):
    # FORM S-BAND/ A-BAND/ EMG-BAND {Make static on frontend}
    form_type = models.CharField(
        db_column='form_type', max_length=500, blank=True, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='ques_emp_id',
                               related_name='AppraisalStaffApplication_EmployeePrimdetail_emp_id', on_delete=models.SET_NULL, null=True)
    status = models.CharField(db_column='status', null=True,
                              max_length=10, default='INSERT')  # SAVED/ SUBMITTED
    session = models.ForeignKey(AccountsSession, related_name='AppraisalStaffApplication_AccountsSession_session',
                                db_column='session', null=True, on_delete=models.SET_NULL, default=1)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = 'AppraisalStaff_Application'
        managed = True
# END ########################## ENTRY POINT

# ALL QUES


class AppraisalStaffAnswer(models.Model):
    application = models.ForeignKey(AppraisalStaffApplication, db_column='application',
                                    related_name='AppraisalStaffAnswer_StaffAppraisalStaffApplication_application', on_delete=models.SET_NULL, null=True)
    ques_id = models.ForeignKey(AppraisalStaffQuestion, db_column='ques_id', null=True,
                                related_name='AppraisalStaffAnswer_StaffAppraisalStaffQuestion_ques_id', on_delete=models.SET_NULL)
    level = models.IntegerField(db_column='level', null=True)
    marks_obtained = models.FloatField(db_column='marks_obtained', null=True)
    answer = models.TextField(db_column='answer', null=True)
    status = models.CharField(
        db_column='status', default='INSERT', max_length=20)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = 'AppraisalStaff_Answer'
        managed = True
# END ############################## ALL QUES

# APPROVAL S


class AppraisalStaffRecommendationApproval(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id',
                               related_name='AppraisalStaffRecommendationApproval_EmployeePrimdetail_emp_id', on_delete=models.SET_NULL, null=True)
    increment_type = models.CharField(
        db_column='increment_type', max_length=50, blank=True)
    # NO INCREMENT, NORMAL, SPECIAL, PROMOTION WITH SPECIAL INCREAMENT,
    # PROMOTION WITHOUT INCREAMENT
    increment_amount = models.FloatField(
        db_column='increment_amount', null=True)
    promoted_to = models.ForeignKey(EmployeeDropdown, db_column='promoted_to', max_length=200,
                                    related_name='AppraisalStaffRecommendationApproval_EmployeeDropdown_promoted_to', on_delete=models.SET_NULL, null=True)
    level = models.IntegerField(db_column='level', null=True)
    remark = models.TextField(db_column='remark', null=True)
    approval_status = models.CharField(
        db_column='approval_status', default='INSERT', max_length=20)
    # APPROVED, REJECTED, REVIEW, PENDING
    added_by = models.ForeignKey(EmployeePrimdetail, db_column='added_by',
                                 related_name='AppraisalStaffRecommendationApproval_EmployeePrimdetail_added_by', null=True, on_delete=models.SET_NULL)
    session = models.ForeignKey(AccountsSession, related_name='AppraisalStaffRecommendationApproval_AccountsSession_session',
                                db_column='session', null=True, on_delete=models.SET_NULL, default=1)
    status = models.CharField(
        db_column='status', default='INSERT', max_length=20)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = 'AppraisalStaff_RecommendationApproval'
        managed = True
# END ############################## APPROVAL
