
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# '''essentials'''
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
from datetime import datetime, date
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
from AppraisalStaff.models import *
from AppraisalFaculty.models import *

# '''import views'''
from login.views import checkpermission, generate_session_table_name

# Create your views here.

# RECCOMEND :-
'''
    1. Create function name that clearly defines what question of part of which form it is checking the value
    2. Don't use abbreviations
'''


def check_if_faculty(emp_id):
    qry = EmployeePrimdetail.objects.filter(emp_id=emp_id, emp_category__value="FACULTY").exclude(emp_status="SEPARATE").exclude(emp_id="00007").values_list('emp_id', flat=True)
    print(qry)
    if len(qry) > 0:
        return True
    else:
        return False


def check_if_already_filled_final(emp_id, session, level):
    qry = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, level=level, form_filled_status="Y").exclude(status="PENDING").exclude(status="DELETE").values('id')
    if len(qry) > 0:
        return True
    else:
        return False


def check_if_already_filled(emp_id, session):
    qry = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session).exclude(status="PENDING").exclude(status="DELETE").values('id').order_by('-id')
    if len(qry) > 0:
        return [True, qry[0]['id']]
    return [False, -1]


def check_if_already_filled_reporting(emp_id, session, level, approval_status):
    qry = list(FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, form_filled_status='Y').exclude(status="DELETE").exclude(status="PENDING").exclude(status="SAVED").values_list('id', flat=True).order_by('-id'))
    if len(qry) > 0:
        approved_id = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=level, session=session, approval_status=approval_status).exclude(status="DELETE").exclude(approval_status="REVIEW").values('id').order_by('-id')
        if len(approved_id) > 0:
            return [True, qry]
    return [False, -1]


def check_if_emp_details_same_or_not(emp_id, details, session, session_name):
    today_date = date.today()
    qry = FacultyAppraisal.objects.filter(emp_id=details['emp_id'], dept=details['dept'], desg=details['desg'], highest_qualification=details['h_qual'], salary_type=details['salary_type_id'], current_gross_salary=details['current_gross_salary'], agp=details['agp'], total_experience=details['total_experience'], session=session).exclude(status="DELETE").values('id').order_by('-id')
    if len(qry) > 0:
        return True
    else:
        return False


def check_is_pass_or_fail(student):
    max_internal = 0
    max_external = 0
    max_marks = 0
    marks_obt = 0
    if len(student) > 0:
        # for student in univ_marks:
        # total_students = total_students + 1
        if student['subject_id__max_ct_marks'] != None:
            max_internal = max_internal + int(student['subject_id__max_ct_marks'])
        if student['subject_id__max_ta_marks'] != None:
            max_internal = max_internal + int(student['subject_id__max_ta_marks'])
        if student['subject_id__max_att_marks'] != None:
            max_internal = max_internal + int(student['subject_id__max_att_marks'])
        if student['subject_id__max_university_marks'] != None:
            max_external = max_external + int(student['subject_id__max_university_marks'])
        max_marks = max_external + max_internal

        try:
            student['external_marks'] = float(student['external_marks'])
        except:
            student['external_marks'] = 0

        try:
            student['internal_marks'] = float(student['internal_marks'])
        except:
            student['internal_marks'] = 0

        try:
            student['back_marks'] = float(student['back_marks'])
        except:
            student['back_marks'] = 0

        if student['back_marks'] == None or student['back_marks'] == 0:
            marks_obt = float(student['external_marks']) + float(student['internal_marks'])
            # print(marks_obt, 'obtain')
        else:
            marks_obt = int(student['back_marks']) + int(student['internal_marks'])

        if int(marks_obt) >= (0.4 * max_marks) and int(student['external_marks']) >= (0.3 * max_internal):
            # print(max_marks, marks_obt)
            return [True, max_marks, marks_obt]
    return [False, -1, -1]


def check_for_achievement_data(data, fac_app_id, level):
    ach_data = []
    row_data = {}
    return_data = []
    if 'A1' in data:
        if 'I' in data['A1']:
            for A1I in data['A1']['I']['data']:
                if A1I['id'] != None:
                    row_data = {'id': A1I['id'], 'type': 'RESEARCH PAPER IN JOURNAL', 'score_claimed': A1I['score_claimed']}
                    if int(level) > 0:
                        if 'score_reviewed' in A1I:
                            if A1I['score_reviewed'] != None:
                                row_data['score_awarded'] = A1I['score_reviewed']
                            else:
                                row_data['score_awarded'] = 0
                        else:
                            row_data['score_awarded'] = A1I['score_awarded']
                    ach_data.append(row_data)
        if 'II' in data['A1']:
            for A1II in data['A1']['II']['data']:
                if A1II['id'] != None:
                    row_data = {'id': A1II['id'], 'type': 'RESEARCH PAPER IN CONFERENCE', 'score_claimed': A1II['score_claimed']}
                    if int(level) > 0:
                        if 'score_reviewed' in A1II:
                            if A1II['score_reviewed'] != None:
                                row_data['score_awarded'] = A1II['score_reviewed']
                            else:
                                row_data['score_awarded'] = 0
                        else:
                            row_data['score_awarded'] = A1II['score_awarded']
                    ach_data.append(row_data)

    if 'A2' in data:
        if 'I' in data['A2']:
            for A2I in data['A2']['I']['data']:
                if A2I['id'] != None:
                    row_data = {'id': A2I['id'], 'type': 'BOOKS', 'score_claimed': A2I['score_claimed']}
                    if int(level) > 0:
                        if 'score_reviewed' in A2I:
                            if A2I['score_reviewed'] != None:
                                row_data['score_awarded'] = A2I['score_reviewed']
                            else:
                                row_data['score_awarded'] = 0
                        else:
                            row_data['score_awarded'] = A2I['score_awarded']
                    ach_data.append(row_data)

    if 'A3' in data:
        if 'I' in data['A3']:
            for A3I in data['A3']['I']['data']:
                if A3I['id'] != None:
                    row_data = {'id': A3I['id'], 'type': 'PROJECTS/CONSULTANCY', 'score_claimed': A3I['score_claimed']}
                    if int(level) > 0:
                        if 'score_reviewed' in A3I:
                            if A3I['score_reviewed'] != None:
                                row_data['score_awarded'] = A3I['score_reviewed']
                            else:
                                row_data['score_awarded'] = 0
                        else:
                            row_data['score_awarded'] = A3I['score_awarded']
                    ach_data.append(row_data)
        if 'II' in data['A3']:
            for A3II in data['A3']['II']['data']:
                if A3II['id'] != None:
                    row_data = {'id': A3II['id'], 'type': 'PATENT', 'score_claimed': A3II['score_claimed']}
                    if int(level) > 0:
                        if 'score_reviewed' in A3II:
                            if A1I['score_reviewed'] != None:
                                row_data['score_awarded'] = A3II['score_reviewed']
                            else:
                                row_data['score_awarded'] = 0
                        else:
                            row_data['score_awarded'] = A3II['score_awarded']
                    ach_data.append(row_data)

    if 'A4' in data:
        if 'I' in data['A4']:
            for A4I in data['A4']['I']['data']:
                if A4I['id'] != None:
                    row_data = {'id': A4I['id'], 'type': 'RESEARCH GUIDANCE / PROJECT GUIDANCE', 'score_claimed': A4I['score_claimed']}
                    if int(level) > 0:
                        if 'score_reviewed' in A4I:
                            if A4I['score_reviewed'] != None:
                                row_data['score_awarded'] = A4I['score_reviewed']
                            else:
                                row_data['score_awarded'] = 0
                        else:
                            row_data['score_awarded'] = A4I['score_awarded']
                    ach_data.append(row_data)

    if 'A5' in data:
        if 'I' in data['A5']:
            for A5I in data['A5']['I']['data']:
                if A5I['id'] != None:
                    row_data = {'id': A5I['id'], 'type': 'TRAINING AND DEVELOPMENT PROGRAM', 'score_claimed': A5I['score_claimed']}
                    if int(level) > 0:
                        if 'score_reviewed' in A5I:
                            if A5I['score_reviewed'] != None:
                                row_data['score_awarded'] = A5I['score_reviewed']
                            else:
                                row_data['score_awarded'] = 0
                        else:
                            row_data['score_awarded'] = A5I['score_awarded']
                    ach_data.append(row_data)
        if 'II' in data['A5']:
            for A5II in data['A5']['II']['data']:
                if A5II['id'] != None:
                    row_data = {'id': A5II['id'], 'type': 'LECTURES AND TALKS', 'score_claimed': A5II['score_claimed']}
                    if int(level) > 0:
                        if 'score_reviewed' in A5II:
                            if A5II['score_reviewed'] != None:
                                row_data['score_awarded'] = A5II['score_reviewed']
                            else:
                                row_data['score_awarded'] = 0
                        else:
                            row_data['score_awarded'] = A5II['score_awarded']
                    ach_data.append(row_data)
    # if int(level) < 1:
    #     flag = 0
    #     for ach in ach_data:
    #         qry = FacAppCat3Achievement.objects.filter(fac_app_id=fac_app_id, type=ach['type'], achievement_id=ach['id'], score_claimed=ach['score_claimed']).exclude(status="DELETE").values()
    #         if len(qry) == 0:
    #             flag = 1
    #             row_data = {'id': ach['id'], 'type': ach['type'], 'score_claimed': ach['score_claimed']}
    #             return_data.append(row_data)
    #     if flag == 1:
    #         return [True, return_data]
    #     else:
    #         return [False, -1]
    # else:
    #     return [ach_data,-1]
    # if int(level) < 1:
    flag = 0
    for ach in ach_data:
        if int(level) < 1:
            qry = FacAppCat3Achievement.objects.filter(fac_app_id=fac_app_id, type=ach['type'], achievement_id=ach['id'], score_claimed=ach['score_claimed']).exclude(status="DELETE").values()
        else:
            qry = FacAppCat3Achievement.objects.filter(fac_app_id=fac_app_id, type=ach['type'], achievement_id=ach['id'], score_claimed=ach['score_claimed'], score_awarded=ach['score_awarded']).exclude(status="DELETE").values()
        if len(qry) == 0:
            flag = 1
            if int(level) > 0:
                row_data = {'id': ach['id'], 'type': ach['type'], 'score_claimed': ach['score_claimed'], 'score_awarded': ach['score_awarded']}
            else:
                row_data = {'id': ach['id'], 'type': ach['type'], 'score_claimed': ach['score_claimed']}
            return_data.append(row_data)
    if flag == 1:
        return [True, return_data]
    else:
        return [False, -1]
    # else:
    #     return [ach_data,-1]


def check_for_final_submit(category_data, is_hod_dean, level):
    flag = 0
    if 'cat1' in category_data:
        if 'A1' in category_data['cat1']:
            for catA1 in category_data['cat1']['A1']['lec']:
                if catA1['avg'] == None:
                    flag = 1
                    if 'score_awarded' in catA1:
                        if catA1['score_awarded'] == None:
                            flag = 1

        if 'A2' in category_data['cat1']:
            for catA2 in category_data['cat1']['A2']['lec']:
                if catA2['avg'] == None and catA2['avg_per'] == None:
                    flag = 1
                    if 'score_awarded' in catA2:
                        if catA2['score_awarded'] == None:
                            flag = 1

        if 'A3' in category_data['cat1']:
            for catA3 in category_data['cat1']['A3']['data']:
                if 'score_awarded' in catA3:
                    if catA3['score_awarded'] == None:
                        flag = 1
        if is_hod_dean == False:
            if 'A4' in category_data['cat1']:
                for i, catA4 in enumerate(category_data['cat1']['A4']['data']):
                    if int(level) < 1:
                        if catA4['duties_assign'] == None or catA4['executed'] == None:
                            flag = 1
                        if 'score_awarded' in catA4:
                            if catA4['score_awarded'] == None:
                                flag = 1
    if 'cat2' in category_data:
        if 'A1' in category_data['cat2']:
            for cat2A1 in category_data['cat2']['A1']['data']:
                if cat2A1['type_of_activity'] == None or cat2A1['average_hours'] == None or cat2A1['score_claimed'] == None:
                    flag = 1
                if 'score_awarded' in cat2A1:
                    if cat2A1['score_awarded'] == None:
                        flag = 1

    if 'cat4' in category_data:
        if 'A1' in category_data['cat4']:
            for cat4A1 in category_data['cat4']['A1']['data2']:
                if cat4A1['institute1'] == None or cat4A1['institute2'] == None or cat4A1['ext_exam_average1'] == None or cat4A1['ext_exam_average2'] == None:
                    flag = 1
                if 'score_awarded' in cat4A1:
                    if cat4A1['score_awarded'] == None:
                        flag = 1

    if flag == 1:
        return False
    return True


# def check_is_hod_dean(request, session):
#     if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
#         return True
#     return False
def check_is_hod_dean(emp_id, session, roles):
    qry = list(Roles.objects.filter(emp_id=emp_id).values_list('roles', flat=True))
    if len(qry) > 0:
        for r in roles:
            if r in qry:
                return True
    return False


def check_for_review_request_faculty(emp_id, added_by_id, session, level):
    qry = FacAppRecommendationApproval.objects.filter(level=level, emp_id=emp_id, added_by=added_by_id, session=session).exclude(status="DELETE").values_list('approval_status', flat=True)
    if len(qry) > 0:
        if ('APPROVED' in qry and 'REVIEW' in qry) or 'REVIEW' in qry:
            return False
        # elif 'REVIEW' in qry:
        #     return True
    else:
        return True


def check_eligibility_at_sixty_per_marks_faculty(marks_obt, max_marks):
    try:
        marks_obt = float(marks_obt)
    except:
        marks_obt = 0
    try:
        max_marks = float(max_marks)
    except:
        max_marks = 0
    if max_marks > 0:
        if marks_obt > (0.6 * max_marks):
            return True
    return False


def check_if_form_editable_or_not_faculty(emp_id, level, session, reporting_end, status):
    if int(reporting_end) != int(level) and int(reporting_end) > int(level):  # FOR BELOW LEVEL
        return False
    if status != None:
        if status == "PENDING":  # IF NOT SUBMITTED AT ANY LEVEL
            return True
        if status == "APPROVED":
            level_last_status = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=level).exclude(status="DELETE").exclude(approval_status="DELETE").values("approval_status").order_by('-approval_status')
            if len(level_last_status) > 0:
                if level_last_status[0]['approval_status'] == "REVIEWED" or level_last_status[0]['approval_status'] == "REVIEW":
                    return False
    qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=level + 1).exclude(status="DELETE").exclude(approval_status="DELETE").values("approval_status", 'id').order_by('-id')
    if len(qry) > 0:
        if qry[0]['approval_status'] == "APPROVED" or qry[0]['approval_status'] == "REVIEWED":
            return False
        elif qry[0]['approval_status'] == "REVIEW":
            return True
    else:
        return True

# def check_for_cat2_values(data,session):


# def check_if_locked(emp_id,session):
def check_for_next_level_approval_exist_faculty(level, emp_id, session):
    ########## TRUE FOR SUBMIT IF NEXT LEVEL IS NOT APPROVED ######################
    qry = FacAppRecommendationApproval.objects.filter(level=int(level) + 1, emp_id=emp_id, session=session).exclude(status="DELETE").values('approval_status').order_by('-approval_status')
    if len(qry) > 0:
        if qry[0]['approval_status'] == "APPROVED" or qry[0]['approval_status'] == ['REVIEWED']:
            return False
        else:
            return True
    else:
        return True
