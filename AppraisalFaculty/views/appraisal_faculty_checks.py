
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


def check_if_faculty_new(emp_id):
    qry = EmployeePrimdetail.objects.filter(emp_id=emp_id, emp_category__value="FACULTY").exclude(emp_status="SEPARATE").exclude(emp_id="00007").values_list('emp_id', flat=True)
    print(qry)
    if len(qry) > 0:
        return True
    else:
        return False


def check_if_already_filled_final_new(emp_id, session, level):
    qry = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, level=level, form_filled_status="Y").exclude(status="PENDING").exclude(status="DELETE").values('id')
    if len(qry) > 0:
        return True
    else:
        return False


def check_if_already_filled_new(emp_id, session):
    qry = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session).exclude(status="PENDING").exclude(status="DELETE").values('id').order_by('-id')
    if len(qry) > 0:
        return [True, qry[0]['id']]
    return [False, -1]


def check_if_already_filled_reporting_new(emp_id, session, level, approval_status):
    qry = list(FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, form_filled_status='Y').exclude(status="DELETE").exclude(status="PENDING").exclude(status="SAVED").values_list('id', flat=True).order_by('-id'))
    if len(qry) > 0:
        approved_id = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=level+1, session=session, approval_status=approval_status).exclude(status="DELETE").exclude(approval_status="REVIEW").values('id').order_by('-id')
        if len(approved_id) > 0:
            return [True, qry]
    return [False, -1]


def check_if_emp_details_same_or_not_new(emp_id, details, session, session_name):
    today_date = date.today()
    qry = FacultyAppraisal.objects.filter(emp_id=details['emp_id'], dept=details['dept'], desg=details['desg'], highest_qualification=details['h_qual'], salary_type=details['salary_type_id'], current_gross_salary=details['current_gross_salary'], agp=details['agp'], total_experience=details['total_experience'], session=session).exclude(status="DELETE").values('id').order_by('-id')
    if len(qry) > 0:
        return True
    else:
        return False


def check_is_pass_or_fail_new(student):
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



def check_for_final_submit_new(category_data, is_hod_dean, level):
    flag = 0
    cat = None
    for category,data_cat in category_data.items():
        if 'main_heading' in data_cat:
            remove_main_heading = data_cat.pop("main_heading")
        if int (level)==1 and 'cat3' in category:
            if 'confidential_awarded' in data_cat.keys():
                confidential_awarded = data_cat.pop("confidential_awarded")
        for part,data_prt in data_cat.items():
            if 'heading' in data_prt:
                remove_heading = data_prt.pop("heading")
            if flag == 1:
                cat = category
                break
###########################################################OVERALL SCORE CHECK########################################
            if "overall_score" not in data_prt:
                cat = category
                flag = 1
                break
            if "overall_score" in data_prt and data_prt['overall_score'] == None or data_prt['overall_score'] == 'NaN':
                cat = category
                flag = 1
                break
            if int(level)==1:
                if "overall_score_awarded" not in data_prt:
                    cat = category
                    flag = 1
                    break
                if ("overall_score_awarded" in data_prt and data_prt['overall_score_awarded'] == None) or data_prt['overall_score_awarded'] == 'NaN':
                    cat = category
                    flag = 1
                    break
###########################################################OVERALL SCORE CHECK END########################################
            if 'data' not in data_prt:
                cat = category
                flag = 1
                break
            else:
                if 'cat1' in category and 'A5' in part:
                    for d in data_prt['last_xyrs_data']:
                        if 'score_claimed' not in d:
                            cat = category
                            flag = 1
                            break
                        if ("score_claimed" in d and d['score_claimed'] == None) or d['score_claimed'] == 'NaN':
                            cat = category
                            flag = 1
                            break
                        for k,v in d.items():#NO KEY VALUE MUST BE  None
                            if v==None:
                                flag=1
                                break
                        if int(level)==1:
                            if "score_awarded" not in d:
                                cat = category
                                flag = 1
                                break
                            if "score_awarded" in d and d['score_awarded'] == None or d['score_awarded'] == 'NaN':
                                cat = category
                                flag = 1
                                break
#####################################################MAX-MIN SCORE CHECKS############################################
                

                if 'cat1' in category and 'A5' not in part:
                    if check_cat1_max_score_claimed(category,part,data_prt['data'],level)[0]==True: 
                        flag=1
                        break
                if 'cat2' in category and flag !=1:        
                    if check_cat2_max_score_claimed(category,part,data_prt['data'],level)[0]==True:
                        flag =1
                        break
                if 'cat3' in category and flag!=1:
                    if check_cat3_max_score_claimed(category,part,data_prt['data'],level)[0]==True:
                        flag = 1
                        break
#####################################################MAX-MIN SCORE CHECKS END############################################
    if flag == 1:
        return False

    return True



def check_cat1_max_score_claimed(category,part,data,level):
    part = str(part)
    flag = 0
    cat = None
    p = None
    for d in data:
        if 'score_claimed' not in d:
            cat = category
            flag = 1
            break
        if int(level)==1:
            if 'score_awarded' not in d:
                cat = category
                flag = 1
                break
        if 'A1' in part:
            if  d['score_claimed']!='---':
                if int(d['score_claimed']) not in range(0,11):
                    cat = category
                    flag = 1
                    p = part
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,11):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A2' in part:
            if  d['score_claimed']!='---':
                if int(d['score_claimed'])<0 or int(d['score_claimed'])>5 :
                    cat = category
                    flag =1
                    p=part
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,6):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A3' in part:
            if  d['score_claimed']!='---':
                if int(d['score_claimed'])<0 or int(d['score_claimed'])>5 :
                    cat = category
                    flag =1
                    p=part
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,6):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A4' in part:
            if  d['score_claimed']!='---':
                if int(d['score_claimed'])<0 or int(d['score_claimed'])>10 :
                    cat=category
                    flag = 1
                    p=part
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,11):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A6' in part:
            if  d['score_claimed']!='---':
                if int(d['score_claimed'])<0 or int(d['score_claimed'])>5 :
                    cat= category
                    flag = 1
                    p=part
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,6):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A7' in part:
            if  d['score_claimed']!='---':
                if int(d['score_claimed'])<0 or int(d['score_claimed'])>5 :
                    cat = category
                    p=part
                    flag =1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,6):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A8' in part:
            if  d['score_claimed']!='---':
                if int(d['score_claimed'])<0 or int(d['score_claimed'])>30 :
                    cat = category
                    p=part
                    flag =1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,31):
                            cat = category
                            flag = 1
                            p = part
                            break
    if flag ==1:
        return [True]
    else:
        return [False]


def check_cat2_max_score_claimed(category,part,data,level):
    part = str(part)
    flag = 0
    cat = None
    for d in data:
        if 'score_claimed' not in d:
            cat = category
            flag = 1
            break
        if int(level)==1:
            if 'score_awarded' not in d:
                cat = category
                flag = 1
                break
        if 'A1' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0:
                    cat = category
                    flag = 1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) <0:
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A2' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 :
                    cat = category
                    flag =1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) <0:
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A3' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0:
                    cat = category
                    flag =1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) <0:
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A4' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 :
                    cat=category
                    flag = 1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded'])<0:
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A5' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 :
                    cat = category
                    flag =1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) <0:
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A6' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 :
                    cat= category
                    flag = 1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) <0:
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A7' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 :
                    cat = category
                    flag =1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) <0:
                            cat = category
                            flag = 1
                            p = part
                            break
    if flag ==1:
        print(cat,part)
        return [True]
    else:
        return [False]


def check_cat3_max_score_claimed(category,part,data,level):
    part = str(part)
    flag = 0
    cat = None
    for d in data:
        print(d)
        if 'score_claimed' not in d:
            cat = category
            flag = 1
            break
        if int(level)==1:
            if 'score_awarded' not in d:
                cat = category
                flag = 1
                break
        if 'A1' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 and d['score_claimed']>20 :
                    cat = category
                    flag = 1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,21):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A2' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 and d['score_claimed']>3 :
                    cat = category
                    flag =1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,4):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A3' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 and d['score_claimed']>2 :
                    cat = category
                    flag =1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,3):
                            cat = category
                            flag = 1
                            p = part
                            break
        elif 'A4' in part:
            if  d['score_claimed']!='---':
                if d['score_claimed']<0 and d['score_claimed']>15 :
                    cat=category
                    flag = 1
                    break
                if int(level)==1:
                    if  d['score_awarded']!='---':
                        if int(d['score_awarded']) not in range(0,16):
                            cat = category
                            flag = 1
                            p = part
                            break
    if flag ==1:
        print(cat)
        return [True]
    else:
        return [False]


def check_is_hod_dean_new(emp_id, session, roles):
    qry = list(Roles.objects.filter(emp_id=emp_id).values_list('roles', flat=True))
    if len(qry) > 0:
        for r in roles:
            if r in qry:
                return True
    return False


def check_for_review_request_faculty_new(emp_id, added_by_id, session, level):
    qry = FacAppRecommendationApproval.objects.filter(level=level, emp_id=emp_id, added_by=added_by_id, session=session).exclude(status="DELETE").values_list('approval_status', flat=True)
    if len(qry) > 0:
        if ('APPROVED' in qry and 'REVIEW' in qry) or 'REVIEW' in qry:
            return False
        # elif 'REVIEW' in qry:
        #     return True
    else:
        return True




def check_eligibility_at_sixty_per_marks_faculty_new(marks_obt, max_marks):
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


def check_if_form_editable_or_not_faculty_new(emp_id, level, session, reporting_end, status):
    if int(reporting_end) != int(level) and int(reporting_end) > int(level):  # FOR BELOW LEVEL
        return False
    if status != None:
        if status == "PENDING":  # IF NOT SUBMITTED AT ANY LEVEL
            return True
        if status == "APPROVED":
            level_last_status = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=level,session=session).exclude(status="DELETE").exclude(approval_status="DELETE").values("approval_status").order_by('-approval_status')
            if len(level_last_status) > 0:
                if level_last_status[0]['approval_status'] == "REVIEWED":
                    return False
    qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=level + 1,session=session).exclude(status="DELETE").exclude(approval_status="DELETE").values("approval_status", 'id').order_by('-id')
    if len(qry) > 0:
        if qry[0]['approval_status'] == "APPROVED" or qry[0]['approval_status'] == "REVIEWED":
            return False
        elif qry[0]['approval_status'] == "REVIEW":
            return True
    else:
        return True

# def check_for_cat2_values(data,session):


# def check_if_locked(emp_id,session):
def check_for_next_level_approval_exist_faculty_new(level, emp_id, session):
    ########## TRUE FOR SUBMIT IF NEXT LEVEL IS NOT APPROVED ######################
    qry = FacAppRecommendationApproval.objects.filter(level=int(level) + 1, emp_id=emp_id, session=session).exclude(status="DELETE").values('approval_status').order_by('-approval_status')
    if len(qry) > 0:
        if qry[0]['approval_status'] == "APPROVED" or qry[0]['approval_status'] == ['REVIEWED']:
            return False
        else:
            return True
    else:
        return True
