
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# '''essentials'''
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
from datetime import datetime
import json
import operator


# '''import constants'''
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

# '''import models'''
from musterroll.models import EmployeePerdetail, Roles, AarReporting, EmployeeSeparation
from login.models import EmployeePrimdetail
from AppraisalStaff.models import *
from Accounts.models import EmployeeGross_detail, EmployeePayableDays, SalaryIngredient
from leave.models import Leaves

# '''import views'''
from login.views import checkpermission, generate_session_table_name

# Create your views here.

# RECCOMEND :-
'''
    1. Create function name that clearly defines what question of part of which form it is checking the value
    2. Don't use abbreviations
'''


def check_form_part_for_first_reporting(form_type, level):
    check_parts = []
    if int(level) == 1:
        if form_type == "EMG-BAND":
            check_parts = ['PART-4', 'PART-5']
        if form_type == "A-BAND":
            check_parts = ['PART-3']
        if form_type == "S-BAND":
            check_parts = ['PART-2']
    return check_parts


def check_form_part_for_submission_of_appraisal(form_type, data, level):
    showable_form_parts = []
    if int(level) < 1:
        if form_type == 'A-BAND':
            showable_form_parts = ['PART-2']
        if form_type == 'S-BAND':
            showable_form_parts = []
        if form_type == 'EMG-BAND':
            showable_form_parts = ['PART-1', 'PART-2', 'PART-3', 'PART-4']
    else:
        if form_type == 'A-BAND':
            showable_form_parts = ['PART-2', 'PART-3']
        if form_type == 'S-BAND':
            showable_form_parts = ['PART-2']
        if form_type == 'EMG-BAND':
            showable_form_parts = ['PART-1', 'PART-2', 'PART-3', 'PART-4', 'PART-5']
    keys = list(data.keys())
    if 'personal' in keys:
        keys.pop(keys.index('personal'))
    for i in range(0, len(keys)):
        if keys[i] not in showable_form_parts:
            del data[keys[i]]
    keys = list(data.keys())
    if len(keys) == len(showable_form_parts):

        return data
    else:
        return False


# def check_form_part_at_reporting_level(form_type, data, level):
#     showable_form_parts = ['PART-5']
#     return showable_form_parts


def check_if_submit_unlocked(type, emp_id, session, extra_filter):
    today = datetime.now()
    qry_check = AppraisalStaffLockingUnlockingStatus.objects.filter(emp_id=emp_id, locking_details__lock_type=type, locking_details__session=session).exclude(status="DELETE").exclude(locking_details__status="DELETE").values('locking_details__unlock_from', 'locking_details__unlock_to', 'locking_details__id').order_by('-locking_details__id')
    if len(qry_check) > 0:
        if qry_check[0]['locking_details__unlock_to'] > today and qry_check[0]['locking_details__unlock_from'] < today:
            return False
        else:
            return True
    else:
        return True

# correction


def check_is_exp_less_than_6_month(emp_id, session, total_exp, extra_filter):
    total_experience = total_exp
    get_year = int(str(total_experience).split(' ')[0])
    if get_year <= 0:
        get_month = int(str(total_experience).split(',')[2])
        if get_month <= 6:
            return False
        else:
            return True
    else:
        return True


def check_if_already_filled(emp_id, form_type, session, extra_filter):
    qry = AppraisalStaffApplication.objects.filter(form_type=form_type, emp_id=emp_id, session=session).exclude(status="PENDING").exclude(status="DELETE").values_list('id', flat=True)
    if len(qry) == 0:
        for q in qry:
            check = AppraisalStaffAnswer.objects.filter(application=q,application__session=session).filter(**extra_filter).exclude(status="DELETE").values()
            if len(check) > 0:
                return qry
        return False
    else:
        return qry


def check_for_emg_band_emp(emp_id, session):
    cadre = ['M', 'E', 'G']
    qry = EmployeePrimdetail.objects.filter(emp_id=emp_id).filter(Q(emp_category__value="TECHNICAL STAFF") | Q(emp_category__value='STAFF')).exclude(emp_status="SEPARATE").values_list('cadre__value', flat=True)
    if len(qry) > 0:
        if qry[0] in cadre:
            return True
        else:
            return False
    else:
        return False


def check_for_a_band_emp(emp_id, session):
    cadre = ['A']
    qry = EmployeePrimdetail.objects.filter(emp_id=emp_id).filter(Q(emp_category__value="TECHNICAL STAFF") | Q(emp_category__value='STAFF')).exclude(emp_status="SEPARATE").values_list('cadre__value', flat=True)
    if len(qry) > 0:
        if qry[0] in cadre:
            return True
        else:
            return False
    else:
        return False


def check_for_s_band_emp(emp_id, session):
    cadre = ['S']
    qry = EmployeePrimdetail.objects.filter(emp_id=emp_id).filter(Q(emp_category__value="TECHNICAL STAFF") | Q(emp_category__value='STAFF')).exclude(emp_status="SEPARATE").values_list('cadre__value', flat=True)
    if len(qry) > 0:
        if qry[0] in cadre:
            return True
        else:
            return False
    else:
        return False


def check_for_final_submit(ques_answer, extra_filter):
    data = ques_answer
    flag = 0
    if len(data) > 0:
        for ques in data:
            if ques['answer'] == None and ques['marks_obtained'] == None:
                return False
            else:
                flag = 1
        if flag == 1:
            return True
    else:
        return True


def check_if_any_reporting_level(form_type, session, emp_id):
    emp_details = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status="SEPARATE").values('desg', 'desg__value', 'dept', 'dept__value', 'name'))
    if len(emp_details) > 0:

        qry = AarReporting.objects.filter(reporting_to=emp_details[0]['desg'], department=emp_details[0]['dept']).exclude(reporting_no__isnull=True).values_list('emp_id', flat=True)
        if len(qry) > 0:
            return True
        else:
            return False
    else:
        return False


def check_for_obt_marks_less_than_max_marks(form_type, ques_answer, index):  # ques_answer in dict format
    for k, part in ques_answer.items():
        for sub_part in part['data']:
            if form_type == 'S-BAND' or form_type == "A-BAND":
                if sub_part['marks_obtained'] != None and len(sub_part['marks_obtained']) > 0:
                    if sub_part['marks_obtained'][index] != None:
                        if sub_part['marks_obtained'][index] > sub_part['max_marks']:
                            return False
                continue
            if len(sub_part['sub_category']) != 0:
                for v in sub_part['sub_category']:
                    if v['marks_obtained'] != None and len(v['marks_obtained']) > 0:
                        if v['marks_obtained'][index] != None:
                            if v['marks_obtained'][index] > v['max_marks']:
                                return False
    return True


def check_eligibility_at_sixty_per_marks(form_type, ques_answer, max_marks_total, index):
    if form_type == "A-BAND":
        check_part = 'PART-3'
    elif form_type == "EMG-BAND":
        check_part = 'PART-4'
    elif form_type == "S-BAND":
        check_part = 'PART-2'
    else:
        check_part = ""
    status = []
    max_obtained = 0
    marks_obtained = 0.0
    if str(check_part) in set(ques_answer.keys()):
        for sub_part in ques_answer[check_part]['data']:
            if form_type == 'S-BAND' or form_type == "A-BAND":
                if sub_part['marks_obtained'] == None:
                    return False
                if len(sub_part['marks_obtained']) == 0:
                    return False
                elif len(sub_part['marks_obtained']) >= int(index) and sub_part['marks_obtained'][index] != None:
                    marks_obtained = marks_obtained + float(sub_part['marks_obtained'][index])
                continue
            if len(sub_part['sub_category']) != 0:
                for v in sub_part['sub_category']:
                    if v['marks_obtained'] == None:
                        return False
                    if len(v['marks_obtained']) == 0:
                        return False
                    elif len(v['marks_obtained']) >= int(index) and v['marks_obtained'][index] != None:
                        marks_obtained = marks_obtained + float(v['marks_obtained'][index])
        max_marks = max_marks_total[check_part]
        sixty_per_max_marks = float((max_marks * 60) / 100)
        if marks_obtained < sixty_per_max_marks:
            return False
    else:
        return False
    return True


def check_if_depend_on_salary_components(salary_comp_ids, session, current_salary, check_comp_id):
    qry = list(SalaryIngredient.objects.filter(Ingredients=check_comp_id, session=session, calcType='F').exclude(status="DELETE").exclude(Formula__isnull=True).values('Formula', 'percent'))
    if len(qry) > 0:
        ids = str(qry[0]['Formula']).split(',')
        ids = set(ids)
        salary_comp_ids = set(salary_comp_ids)
        if len(salary_comp_ids.intersection(ids)) == 0:
            return qry[0]['percent']
        else:
            return False
    else:
        return False


def check_if_pending_at_next_level(level, form_type, session, emp_id):
    level = int(level) + 1
    qry = AppraisalStaffApplication.objects.filter(form_type=form_type, emp_id=emp_id, session=session).exclude(status="PENDING").values('id').order_by('-id')
    if len(qry) > 0:
        check = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, level=level, session=session).exclude(status="DELETE").values('approval_status', 'id').order_by('-id')
        if len(check) > 0:
            return True
    return False


def check_for_review_request(emp_id, added_by_id, session, level):
    qry = AppraisalStaffRecommendationApproval.objects.filter(level=level, emp_id=emp_id, added_by=added_by_id, session=session).exclude(status="DELETE").values_list('approval_status', flat=True)
    if len(qry) > 0:
        if 'APPROVED' in qry and 'REVIEW' in qry or 'REVIEW' in qry:
            return False
        # elif 'REVIEW' in qry:
        #     return True
    else:
        return True


def check_for_approved_request(emp_id, added_by_id, session, level):
    qry = AppraisalStaffRecommendationApproval.objects.filter(level=level, emp_id=emp_id, added_by=added_by_id, session=session).exclude(status="DELETE").values_list('approval_status', flat=True)
    if len(qry) > 0:
        if 'APPROVED' in qry:
            return False
        # elif 'REVIEW' in qry:
        #     return True
    else:
        return True

# def check_if_reviewed_answers(emp_id, session, level):
#     qry = AppraisalStaffAnswer.objects.filter(level=level, application__emp_id=emp_id, application__session=session, status="REVIEWED").exclude(status="DELETE").exclude(status="APPROVED").values('id')
#     if len(qry) > 0:
#         return True
#     else:
#         return False


# def check_if_approved_answers(emp_id, session, level):
#     qry = AppraisalStaffAnswer.objects.filter(level=level, application__emp_id=emp_id, application__session=session, status="APPROVED").exclude(status="DELETE").exclude(status="REVIEWED").values('id')
#     if len(qry) > 0:
#         return True
#     else:
#         return False


def check_if_form_editable_or_not(emp_id, level, form_type, session, reporting_end, status):
    if int(reporting_end) != int(level) and int(reporting_end) > int(level):  # FOR BELOW LEVEL
        return False
    if status != None:
        if status == "PENDING":  # IF NOT SUBMITTED AT ANY LEVEL
            return True
        if status == "APPROVED":
            level_last_status = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, level=level,session=session).exclude(status="DELETE").exclude(approval_status="DELETE").values("approval_status").order_by('-approval_status')
            if len(level_last_status) > 0:
                if level_last_status[0]['approval_status'] == "REVIEWED" or level_last_status[0]['approval_status'] == "REVIEW":
                    return False
    qry = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, level=level + 1,session=session).exclude(status="DELETE").exclude(approval_status="DELETE").values("approval_status", 'id').order_by('-id')
    if len(qry) > 0:
        if qry[0]['approval_status'] == "APPROVED" or qry[0]['approval_status'] == "REVIEWED":
            return False
        elif qry[0]['approval_status'] == "REVIEW":
            return True
    else:
        return True


def check_if_review_is_eligible(reporting_level):
    if int(reporting_level) <= 1:
        return False
    else:
        return True


# def check_is_employee_eligible_or_not(list_emp):
#     status = "ELIGIBLE"
#     data = []
#     # qry = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
#     for li in list_emp:
#         qry = Leaves.objects.filter(emp_id=li['emp_id'], finalstatus="APPROVED",).exclude(leavecode__accumulate_max__isnull=True).exclude(leavecode__status__isnull=True).values('emp_id', 'fromdate', 'todate', 'leaveid').order_by('-leaveid')
#         if len(qry) > 0:
#             data.append(qry)

#     return data

def check_for_next_level_approval_exist(level, emp_id, session):
    ########## TRUE FOR SUBMIT IF NEXT LEVEL IS NOT APPROVED ######################
    qry = AppraisalStaffRecommendationApproval.objects.filter(level=int(level) + 1, emp_id=emp_id, session=session).exclude(status="DELETE").values('approval_status').order_by('-approval_status')
    if len(qry) > 0:
        if qry[0]['approval_status'] == "APPROVED" or qry[0]['approval_status'] == ['REVIEWED']:
            return False
        else:
            return True
    else:
        return True
