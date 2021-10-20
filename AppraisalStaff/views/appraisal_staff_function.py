
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# '''essentials'''
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
from datetime import date
import json
import datetime
import operator


# '''import constants'''
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

# '''import models'''
from musterroll.models import EmployeePerdetail, Roles, EmployeeResearch, EmployeeAcademic, AarReporting
from Accounts.models import EmployeeGross_detail, EmployeePayableDays, SalaryIngredient, AccountsSession, ConstantDeduction
from login.models import AarDropdown, EmployeeDropdown
from login.models import EmployeePrimdetail
from AppraisalStaff.models import AppraisalStaffQuestion, AppraisalStaffAnswer, AppraisalStaffApplication, AppraisalStaffRecommendationApproval
from AppraisalStaff.views.appraisal_staff_checks_function import *
from Accounts.views import gross_payable_salary_components, stored_gross_payable_salary_components, modified_category_sheet
from AppraisalStaff.constants_functions.functions import *
# '''import views'''
from login.views import checkpermission, generate_session_table_name
from musterroll.views import get_net_experience
from dateutil.relativedelta import relativedelta

# Create your views here.

# STEPS :-
'''
    1. Create function for fetching data for specific part of question
    2. Create function for "FORMATTING" data for fetched data according to exact need of frontend
'''

# RECCOMEND :-
'''
    1. Create function name that clearly defines what question of part of which form it is checking the value
    2. Don't use abbreviations
'''


def get_increment_dropdown():
    data = []
    data.append({'sno': 1, 'value': "NORMAL"})
    data.append({'sno': 2, 'value': "SPECIAL"})
    return data


def get_promotion_dropdown():
    data = []
    data.append({'sno': 1, 'value': "PROMOTION WITH SPECIAL INCREAMENT"})
    data.append({'sno': 1, 'value': "PROMOTION WITHOUT INCREAMENT"})
    return data

# constant


def get_increment_type():
    data = []
    data.append({'sno': 1, 'value': 'NO INCREMENT'})
    data.append({'sno': 2, 'value': 'NORMAL'})
    data.append({'sno': 3, 'value': 'SPECIAL'})
    data.append({'sno': 4, 'value': 'PROMOTION WITH SPECIAL INCREAMENT'})
    data.append({'sno': 5, 'value': 'PROMOTION WITHOUT INCREAMENT'})
    return data


def get_employees(dept, category):
    query = EmployeePrimdetail.objects.filter(emp_category__in=category, dept__in=dept, emp_status='ACTIVE').values('emp_id', 'name').order_by('name')
    return query


def get_rating(rating):
    data = []
    for i in range(0, rating):
        data.append({"rating": i + 1})
    return data


def get_ladder_acc_to_cadre(cadre):
    ladder = []
    if cadre == 'S':
        ladder = ['S1', 'S2', 'S3']
    elif cadre == 'E':
        ladder = ['E1', 'E2', 'E3', 'E4', 'E5']
    elif cadre == 'M':
        ladder = ['M1', 'M2', 'M3']
    elif cadre == 'A':
        ladder = ['A1', 'A2', 'A3']
    elif cadre == 'G':
        ladder = ['G']
    return ladder


def get_maximum_reporting(list_emp):  # LIST OF EMPLOYEE LIST AT DIFFERENT LEVELS ###########
    max_reporting = 0
    for emp in list_emp:
        if int(max_reporting) < int(emp['reporting_level']):
            max_reporting = int(emp['reporting_level'])
    return max_reporting


def get_all_desg(extra_filter):
    data = []
    qry = list(EmployeeDropdown.objects.filter(**extra_filter).filter(value="DESIGNATION").exclude(status="DELETE").exclude(value__isnull=True).values_list('sno', flat=True))
    if len(qry) > 0:
        data = list(EmployeeDropdown.objects.filter(field="DESIGNATION", pid__in=qry).exclude(value__isnull=True).values('sno', 'pid', 'field', 'value'))
    return data


def get_emp_desg(emp_id):
    data = []
    category_of_emp = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status="SEPARATE").values('emp_category', 'emp_category__value'))
    if len(category_of_emp) > 0:
        qry = list(EmployeeDropdown.objects.filter(field=category_of_emp[0]['emp_category__value'], value="DESIGNATION").exclude(status="DELETE").exclude(value__isnull=True).values_list('sno', flat=True))
        if len(qry) > 0:
            data = list(EmployeeDropdown.objects.filter(field="DESIGNATION", pid__in=qry).exclude(value__isnull=True).values('sno', 'pid', 'field', 'value'))
    return data


def get_percentage_increase(salary_type, increment_type):
    per = 0
    if increment_type == "NORMAL":
        if salary_type == "GRADE":
            per = 3
        elif salary_type == "CONSOLIDATE":
            per = 8
    return per


def get_emp_details(emp_id, extra_filter):
    data = []
    qry = EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status="SEPARATE").values(
        'emp_id', 'name', 'dept', 'dept__value', 'desg', 'desg__value', 'doj', 'ladder', 'ladder__value', 'cadre', 'cadre__value','current_pos','current_pos__value','title__value')
    if qry:
        qry[0]['doj'] = qry[0]['doj'].strftime("%d-%m-%Y")
        qry[0]['name'] = qry[0]['title__value'] + ". "+ qry[0]['name']
        data = qry[0]
    return data


def get_salary_type(emp_id, session, extra_filter):
    salary_type = {}
    # for salary type session = 2
    session = 2
    qry = EmployeeGross_detail.objects.filter(Emp_Id=emp_id, session=session).filter().exclude(Status="DELETE").extra(
        select={'sno': 'salary_type', 'value': 'salary_type__value'}).values('sno', 'salary_type__value')
    if len(qry) > 0:
        salary_type = qry[0]
    return salary_type

# function


def get_gross_salary(emp_id, session, extra_filter):
    data = {}
    payable = {}
    total_gross = 0
    agp = 0
    month = 3  # JUNE STATIC #########
    # for salary session = 2 static
    session = 2
    get_emp_cat = EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status="SEAPARATE").values_list('emp_category__value', flat=True)
    if len(get_emp_cat) > 0:
        if 'STAFF' in get_emp_cat[0]:
            month = 5
        else:
            month = 5
    #####
    emps = EmployeePayableDays.objects.filter(emp_id=emp_id, session=session, month=month).values(
        'working_days', 'leave', 'holidays', 'total_days', 'emp_id__name', 'emp_id', 'emp_id__dept__value', 'emp_id__desg__value')
    if emps:
        leave = emps[0]['leave']
        holidays = emps[0]['holidays']
        total_days = emps[0]['total_days']
        working_days = emps[0]['working_days'] + leave + holidays
        taxstatus_li = [0, 1]
        payable = stored_gross_payable_salary_components(emp_id, session, month)
        # payable = gross_payable_salary_components(emp_id, working_days, total_days, session, taxstatus_li, month)
        if len(payable) > 0:
            for pay in payable:
                total_gross = total_gross + pay['gross_value']
                if "AGP" in pay['value']:
                    agp = pay['gross_value']
    total_gross = float(round(total_gross, 2))
    data = {'payable': payable, 'total_gross': total_gross, 'agp': agp}
    return data

# def get_gross_salary(emp_id, session, extra_filter):
#     data = {}
#     payable = {}
#     total_gross = 0
#     agp = 0
#     month = 6  # JUNE STATIC #########
#     get_emp_cat = EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status="SEAPARATE").values_list('emp_category__value',flat=True)
#     if len(get_emp_cat)>0:
#         if 'STAFF' in get_emp_cat[0]:
#             month = 6
#         else:
#             month = 7

#     qry_salary_comp = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values('Ingredients__value', 'id')
#     qry_salary_comp_ids = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values_list('id', flat=True)
#     q_const_ded = ConstantDeduction.objects.filter(session=session).exclude(status="DELETE").values('DeductionName__value', 'id')
#     q_var_ded = AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("value", 'sno')

#     q_emps = EmployeePayableDays.objects.filter(emp_id=emp_id, month=month, session=session).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'), emp_id__dept__value=F('dept__value'), bank_Acc_no=F('bank_acc_no'), emp_id__title__value=F('title__value')).values('emp_id__name', 'emp_id', 'emp_id__desg__value', 'emp_id__dept__value', 'emp_id__title__value', 'bank_Acc_no', 'pan_no', 'uan_no')

#     final_data = modified_category_sheet(qry_salary_comp, q_emps, q_const_ded, q_var_ded, session, month, qry_salary_comp_ids)

#     print(final_data)

#     data = {'payable': payable, 'total_gross': total_gross, 'agp': agp}

#     return data


def get_total_experience(emp_id, extra_filter):
    query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
    exp = relativedelta(date.today(), query2[0]['doj'])  # 30.0.2019 STATIC
    years = exp.years
    months = exp.months
    days = exp.days

    total_year = 0
    total_month = 0
    query_research = EmployeeResearch.objects.filter(emp_id=emp_id).values(
        'research_years', 'research_months', 'industry_years', 'industry_months', 'teaching_years', 'teaching_months')
    total_exp2 = int()
    total_year = 0
    total_month = 0
    if(len(query_research) > 0):
        if query_research[0]['research_years'] != None and query_research[0]['research_months'] != None:
            total_year = total_year + query_research[0]['research_years']
            total_month = total_month + query_research[0]['research_months']

        if query_research[0]['industry_years'] != None and query_research[0]['industry_months'] != None:
            total_year = total_year + query_research[0]['industry_years']
            total_month = total_month + query_research[0]['industry_months']

        if query_research[0]['teaching_years'] != None and query_research[0]['teaching_months'] != None:
            total_year = total_year + query_research[0]['teaching_years']
            total_month = total_month + query_research[0]['teaching_months']
    else:
        total_year = 0
        total_month = 0
    total_year1 = int(years) + int(total_year)
    total_month1 = int(months) + int(total_month)
    if(total_month1 % 12 == 0):
        c = total_month1 / 12
        total_year1 = total_year1 + int(c)
        total_month1 = 0
    else:
        p = total_month1 % 12
        y = total_month1 / 12
        total_year1 = total_year1 + int(y)
        total_month1 = p
    if total_month1 == 0:
        total_exp = str(total_year1) + " Years "
    else:
        total_exp = str(total_year1) + " Years " + str(total_month1) + " Months "
    return total_exp


def get_qualifications(emp_id,extra_filter):
    qual = []
    qr = list(EmployeeAcademic.objects.filter(emp_id=emp_id).values('univ_ug__value', 'degree_ug__value', 'univ_pg__value', 'degree_pg__value', 'univ_doctrate__value', 'stage_doctrate__value', 'degree_other__value', 'univ_other__value',))
    if len(qr)>0:
        if qr[0]['degree_ug__value'] is not None:
            qual.append(qr[0]['degree_ug__value'])
        if qr[0]['degree_pg__value'] is not None:
            qual.append(qr[0]['degree_pg__value'])
        if qr[0]['degree_other__value'] is not None:
            qual.append(qr[0]['degree_other__value'])
    return qual



def get_highest_qualification(emp_id, extra_filter):
    qr = EmployeeAcademic.objects.filter(emp_id=emp_id).values('pass_year_10', 'board_10', 'cgpa_per_10', 'pass_year_12', 'board_12', 'cgpa_per_12', 'pass_year_dip', 'univ_dip', 'cgpa_per_dip', 'pass_year_ug', 'univ_ug', 'degree_ug', 'cgpa_per_ug', 'pass_year_pg', 'univ_pg', 'degree_pg', 'cgpa_per_pg', 'area_spl_pg', 'doctrate', 'univ_doctrate', 'date_doctrate', 'stage_doctrate',
                                                               'research_topic_doctrate', 'degree_other', 'pass_year_other', 'univ_other', 'cgpa_per_other', 'area_spl_other', 'emp_id', 'area_spl_ug', 'dip_area', 'board_10__value', 'board_12__value', 'univ_dip__value', 'univ_ug__value', 'degree_ug__value', 'univ_pg__value', 'degree_pg__value', 'univ_doctrate__value', 'stage_doctrate__value', 'degree_other__value', 'univ_other__value',)
    highest_qualification = "---"
    if qr is not None and len(qr) > 0:
        r = qr[0]
        if r['doctrate'] == 'PD':
            try:
                highest_qualification = "PHD "
            except:
                highest_qualification = "PHD "

        else:
            if r['cgpa_per_pg'] != None:
                try:
                    if r['area_spl_pg'] != None:
                        highest_qualification = r['degree_pg__value']
                    else:
                        highest_qualification = r['degree_pg__value']
                except:
                    highest_qualification = "Post Graduation"
            elif r['cgpa_per_pg'] == None:
                if r['cgpa_per_ug'] != None:
                    if r['area_spl_ug'] != None:
                        if r['degree_ug__value'] != None:
                            highest_qualification = r['degree_ug__value']
                        else:
                            highest_qualification = "Graduation"
                    else:
                        highest_qualification = r['degree_ug__value']

                elif r['cgpa_per_ug'] == None:
                    if r['cgpa_per_dip'] != None:
                        if r['dip_area'] != None:
                            highest_qualification = "Diploma"
                        else:
                            highest_qualification = "Diploma"
                    elif r['cgpa_per_dip'] == None:
                        if(r['degree_other'] != None):
                            highest_qualification = r['degree_other__value']
                        else:
                            if r['cgpa_per_12'] != None:
                                highest_qualification = "12th"
                            elif r['cgpa_per_12'] == None:
                                if r['cgpa_per_10'] != None:
                                    highest_qualification = "10th"
                                elif r['cgpa_per_10'] == None:
                                    highest_qualification = '----'
    return highest_qualification


def get_emp_part_data(emp_id, session, extra_filter):
    data = {}
    emp_data = get_emp_details(emp_id, {})
    emp_salary_type = get_salary_type(emp_id, session, {})
    emp_gross_salary = get_gross_salary(emp_id, session, {})
    highest_qualification = get_highest_qualification(emp_id, {})
    total_experience = " "
    total_experience = total_experience.join(get_net_experience(emp_id))

    ############# SET FORMAT FOR PART-1 ###############
    if len(emp_data) > 0:
        for k, v in emp_data.items():
            data[k] = v
    data['h_qual'] = highest_qualification
    if len(emp_salary_type) > 0:
        data['salary_type_id'] = emp_salary_type['sno']
        data['salary_type'] = emp_salary_type['salary_type__value']
    data['current_gross_salary'] = emp_gross_salary['total_gross']
    data['agp'] = emp_gross_salary['agp']
    if len(total_experience) > 0:
        data['total_experience'] = total_experience
    ###################################################
    return data



def get_emp_part_data_new(emp_id, session, extra_filter):
    data = {}
    emp_data = get_emp_details(emp_id, {})
    emp_salary_type = get_salary_type(emp_id, session, {})
    emp_gross_salary = get_gross_salary(emp_id, session, {})
    highest_qualification = get_highest_qualification(emp_id, {})
    qualification = get_qualifications(emp_id,{})
    total_experience = " "
    total_experience = total_experience.join(get_net_experience(emp_id))

    ############# SET FORMAT FOR PART-1 ###############
    if len(emp_data) > 0:
        for k, v in emp_data.items():
            data[k] = v
    data['h_qual'] = highest_qualification
    if len(emp_salary_type) > 0:
        data['salary_type_id'] = emp_salary_type['sno']
        data['salary_type'] = emp_salary_type['salary_type__value']
    data['current_gross_salary'] = emp_gross_salary['total_gross']
    data['agp'] = emp_gross_salary['agp']
    if len(total_experience) > 0:
        data['total_experience'] = total_experience
    data['qualification'] = "---"
    if (len(qualification)>0):
        data['qualification'] = " , ".join(qualification)

        

    ###################################################
    return data


def get_heading_ques_data(heading, form_type, form_part, index, level):
    heading = []
    heading1 = []
    heading2 = []
    heading3 = []
    if form_type == "EMG-BAND":
        if form_part == "PART-4":
            heading1 = ['CLAIMED SCORE', 'AWARDED HOD/FH', 'REVIEWED HOD/FH']
            if len(heading1) >= int(index) + 1:
                heading = heading1[int(index)]
            else:
                heading = None
        elif form_part == "PART-5":
            heading2 = ['', 'STRENGTH/WEAKNESS', 'REVIEWED STRENGTH/WEAKNESS']
            if len(heading2) >= int(index) + 1:
                heading = heading2[int(index)]
            else:
                heading = None
        else:
            heading = None
    elif form_type == "A-BAND":
        if form_part == "PART-3" and int(level) == 1:
            heading3 = ['AWARDED HOD/FH', 'REVIEWED HOD/FH']
            if len(heading3) >= int(index) + 1:
                heading = heading3[int(index)]
            else:
                heading = None
        else:
            heading = None
    elif form_type == "S-BAND":
        if form_part == "PART-2" and int(level) == 1:
            heading3 = ['AWARDED HOD/FH', 'REVIEWED HOD/FH']
            if len(heading3) >= int(index) + 1:
                heading = heading3[int(index)]
            else:
                heading = None
        else:
            heading = None
    else:
        heading = None
    return heading


def get_answers_of_application_id(emp_id, session, level, extra_filter):
    data = {}
    app_id = AppraisalStaffAnswer.objects.filter(application__emp_id=emp_id, level=level, ques_id__session=session).exclude(status="DELETE").values_list('application', flat=True).order_by('-application').distinct()

    if len(app_id) > 0:
        qry = AppraisalStaffAnswer.objects.filter(application=app_id[0], level=level,ques_id__session=session).filter(**extra_filter).exclude(status="DELETE").values('ques_id', 'marks_obtained', 'answer')
    else:
        qry = []
    if len(qry) > 0:
        flag = 0
        for q in qry:
            if q['ques_id'] in data:
                if type(data[q['ques_id']]['answer']) == str:
                    previous_ans = data[q['ques_id']]['answer']
                    data[q['ques_id']]['answer'] = []
                    data[q['ques_id']]['answer'].append(previous_ans)
                    flag = 1
                data[q['ques_id']]['answer'].append(q['answer'])
            else:
                data[q['ques_id']] = {'answer': q['answer'], 'marks_obtained': q['marks_obtained']}
    return data


def get_part_wise_data(question, data):
    for q in question:
        if q['form_part'] in data:
            if q['parent_ques'] != 0 and q['parent_ques'] != None:
                ques_id = AppraisalStaffQuestion.objects.filter(ques_id=q['parent_ques']).exclude(
                    status="DELETE").values_list('ques_id', flat=True)
                sub_category_ques_ids = list(AppraisalStaffQuestion.objects.filter(parent_ques=q['parent_ques']).exclude(status="DELETE").exclude(statement__isnull=True).values_list('ques_id', flat=True))
                for d in data[q['form_part']]['data']:
                    if d['ques_id'] == ques_id[0]:
                        d['sub_category'].append({'ques_id': q['ques_id'], 'max_marks': q[
                            'max_marks'], 'question': q['statement'], 'answer': [], 'marks_obtained': [], 'is_editable': []})
            else:
                if 'RATE' in str(q['statement'])[:5] or 'Rate' in str(q['statement']):
                    type_ques = 'Rating'
                else:
                    type_ques = 'Question'
                question_no = int(data[q['form_part']]['data'][-1]['ques_no'])
                data[q['form_part']]['data'].append({'type': type_ques, 'type_name': q['field'], 'ques_no': question_no + 1, 'question': q[
                    'statement'], 'sub_category': [], 'ques_id': q['ques_id'], 'max_marks': q['max_marks'], 'answer': [], 'marks_obtained': [], 'is_editable': []})

        else:
            if 'RATE' in str(q['statement'])[:5] or 'Rate' in str(q['statement']):
                type_ques = 'Rating'
            else:
                type_ques = 'Question'
            question_no = 1
            data[q['form_part']] = {}
            data[q['form_part']]['data'] = []
            data[q['form_part']]['data'].append({'type': type_ques, 'type_name': q['field'], 'ques_no': question_no, 'question': q[
                'statement'], 'sub_category': [], 'ques_id': q['ques_id'], 'max_marks': q['max_marks'], 'answer': [], 'marks_obtained': [], 'is_editable': []})
            data[q['form_part']]['heading'] = []
    return data


def get_questions_in_format(form_type, emp_id, session, level, extra_filter):
    data = {}
    question = AppraisalStaffQuestion.objects.filter(form_type=form_type, session=session).exclude(status="DELETE").exclude(statement__isnull=True).values('ques_id', 'parent_ques', 'field', 'max_marks', 'statement', 'form_part', 'form_type').order_by('parent_ques', 'form_part', 'ques_id')
    data = get_part_wise_data(question, data)
    ########## PART WISE CHECK FOR LEVEL #####################################
    if check_form_part_for_submission_of_appraisal(form_type, data, level) == False:
        return False
    else:
        data = check_form_part_for_submission_of_appraisal(form_type, data, level)
    ##########################################################################
    for d in list(data.keys()):
        ################### HEADING CHECK ############################
        i = 0

        if form_type == "EMG-BAND" and d == "PART-4":
            data[d]['heading'] = ['SNO', 'PARAMETERS', 'NATURE OF ACTIVITY', 'MAX. SCORE']
        if form_type == "A-BAND" and d == "PART-3":
            data[d]['heading'] = ['SNO', 'CATEGORY', 'EVALUATION CRITERIA', 'MAX. SCORE']
        if d == "S-BAND" and d == "PART-2":
            data[d]['heading'] = ['SNO', 'EVALUATION CRITERIA', 'MAX. SCORE']

        ##############################################################
        for l in range(0, int(level) + 1):
            get_no_of_statuses = []
            if l == 0:
                status = AppraisalStaffAnswer.objects.filter(level=l, application__emp_id=emp_id,application__session = session).exclude(status="DELETE").values('status').distinct()
                if len(status) > 0:
                    get_no_of_statuses = []
                    get_no_of_statuses.append(status[0])
            elif l <= 1:
                status = list(AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, level=l,session = session).exclude(status="DELETE").values('approval_status').distinct())
                if len(status) > 0:
                    if status[-1]['approval_status'] == "REVIEWED":
                        get_no_of_statuses = []
                        get_no_of_statuses.append({'status': "APPROVED"})
                        get_no_of_statuses.append({'status': "REVIEWED"})
                    elif status[-1]['approval_status'] == "REVIEW":
                        get_no_of_statuses = []
                        get_no_of_statuses.append({'status': "APPROVED"})
                        get_no_of_statuses.append({'status': "APPROVED", 'real': "REVIEW"})
                    else:
                        get_no_of_statuses = []
                        get_no_of_statuses.append({'status': "APPROVED"})

            # IF NO DATA IS FOUND FOR EMPLOYEE AND 1ST REPORTING END THEN NULL IS APPEND IN ANSWERS
            if len(get_no_of_statuses) == 0 and int(l) <= 1:
                get_no_of_statuses = []
                get_no_of_statuses.append({'status': "PENDING"})
            ###############################################################################################
            for status in get_no_of_statuses:
                ans_data = get_answers_of_application_id(emp_id, session, l, {"status": status['status']})
                if len(ans_data) == 0 and status['status'] == "REVIEWED":
                    ans_data = get_answers_of_application_id(emp_id, session, l, {"status": "APPROVED"})

                # FOR HEADING.............
                if get_heading_ques_data(data[d]['heading'], form_type, d, i, l) != None:
                    data[d]['heading'].append(get_heading_ques_data(data[d]['heading'], form_type, d, i, l))

                    i = i + 1
                # END .................
                ############ FOR A-BAND AND S-BAND == DIFFERENT FORMAT OF QUES/ANS#######################
                if form_type == "S-BAND" and d == "PART-2" or form_type == "A-BAND" and d == "PART-3":
                    for category in data[d]['data']:
                        ############ FOR EDITABLE KEY ######################
                        if 'real' in status:
                            category['is_editable'].append(check_if_form_editable_or_not(emp_id, l, form_type, session, level, status['real']))
                        else:
                            category['is_editable'].append(check_if_form_editable_or_not(emp_id, l, form_type, session, level, status['status']))
                        ###################################################
                        if category['ques_id'] in ans_data:
                            category['answer'].append(ans_data[category['ques_id']]['answer'])
                            category['marks_obtained'].append(ans_data[category['ques_id']]['marks_obtained'])
                        else:
                            category['answer'].append(None)
                            category['marks_obtained'].append(None)
                    continue
                #########################################################################################
                for category in data[d]['data']:
                    if len(category['sub_category']) == 0:
                        ############ FOR EDITABLE KEY ######################
                        if 'real' in status:
                            category['is_editable'].append(check_if_form_editable_or_not(emp_id, l, form_type, session, level, status['real']))
                        else:
                            category['is_editable'].append(check_if_form_editable_or_not(emp_id, l, form_type, session, level, status['status']))
                        ###################################################
                        if category['ques_id'] in ans_data:
                            category['answer'].append(ans_data[category['ques_id']]['answer'])
                            category['marks_obtained'].append(ans_data[category['ques_id']]['marks_obtained'])
                        else:
                            category['answer'].append(None)
                            category['marks_obtained'].append(None)
                    else:
                        for sub_category in category['sub_category']:
                            ############ FOR EDITABLE KEY ######################
                            if 'real' in status:
                                sub_category['is_editable'].append(check_if_form_editable_or_not(emp_id, l, form_type, session, level, status['real']))
                            else:
                                sub_category['is_editable'].append(check_if_form_editable_or_not(emp_id, l, form_type, session, level, status['status']))
                            ###################################################

                            if sub_category['ques_id'] in ans_data:
                                sub_category['answer'].append(ans_data[sub_category['ques_id']]['answer'])
                                sub_category['marks_obtained'].append(ans_data[sub_category['ques_id']]['marks_obtained'])
                            else:
                                sub_category['answer'].append(None)
                                sub_category['marks_obtained'].append(None)
    return data


def get_reporting_of_emp_of_corresponding_band(dept, desg, emp_id, extra_filter):
    data = None
    qry = AarReporting.objects.filter(reporting_to=desg, department=dept, emp_id=emp_id).exclude(emp_id__emp_status="SEPARATE").values_list('reporting_no', flat=True)
    print(qry)
    if len(qry) > 0:
        data = qry[0]
    return data


def get_statuses_at_reporting_level_of_emp(emp_id, session):
    data = []
    qry = AarReporting.objects.filter(emp_id=emp_id).values('reporting_to', 'reporting_to__value', 'department', 'reporting_no').order_by('reporting_no')
    if len(qry) > 0:
        for q in qry:
            get_reporting_id = EmployeePrimdetail.objects.filter(dept=q['department'], desg=q['reporting_to']).exclude(emp_status="SEPARATE").exclude(emp_id="00007").values('emp_id')
            if len(get_reporting_id) > 0:
                get_status = list(AppraisalStaffRecommendationApproval.objects.filter(added_by=get_reporting_id[0]['emp_id'], level=q['reporting_no'], session=session, emp_id=emp_id).exclude(status="DELETE").values('approval_status', 'id').order_by('-id'))
                if len(get_status) > 0:
                    data.append({'status': get_status[0]['approval_status'], 'desgination': q['reporting_to__value']})
                else:
                    data.append({'status': 'PENDING', 'desgination': q['reporting_to__value']})
    return data


def get_submission_status_of_emp_form(emp_id, form_type, session, extra_filter):
    status = "NOT FILLED"
    qry = AppraisalStaffApplication.objects.filter(form_type=form_type, emp_id=emp_id, session=session).exclude(status="DELETE").exclude(status="PENDING").values('id').order_by('-id')
    if len(qry) > 0:
        if form_type == "S-BAND":
            extra_filter = {'level': 0}
        else:
            extra_filter = {'level': 1}
        answer_status = AppraisalStaffAnswer.objects.filter(application=qry[0]['id']).exclude(**extra_filter).exclude(status="DELETE").exclude(status="SAVED").values('status').distinct()
        if len(answer_status) > 0:
            if answer_status[0]['status'] == "SUBMITTED":
                return "FILLED"
            elif answer_status[0]['status'] == "APPROVED":
                return "FILLED"
    return status


def get_employee_under_reporting(emp_id, session, form_type):
    list_emp = []
    consolidate_data = {}
    ########## LADDER-CADRE ###########
    cadre = []
    cadre__value = str(str(form_type).split('-')[0])
    for c in cadre__value:
        cadre.append(c)
    ladder = []
    new_list = []
    for c in cadre:
        new_list = get_ladder_acc_to_cadre(c)
        ladder.extend(new_list)
    ############# END #####################
    qry = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status="SEPARATE").exclude(emp_id='00007').values('emp_category__value', 'cadre__value', 'ladder__value', 'desg', 'desg__value', 'dept', 'dept__value'))
    if len(qry) > 0:
        list_emp = list(AarReporting.objects.filter(reporting_to=qry[0]['desg'], department=qry[0]['dept'], emp_id__ladder__value__in=ladder).exclude(emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id='00007').values('emp_id', 'emp_id__name', 'emp_id__cadre__value', 'emp_id__ladder__value'))
        for emp in list_emp:
            other_details = get_emp_part_data(emp['emp_id'], session, {})
            for k, v in other_details.items():
                emp[k] = v
            query = AppraisalStaffApplication.objects.filter(form_type=form_type, emp_id=emp['emp_id'], session=session).exclude(status="DELETE").exclude(status="PENDING").values()

            ############ REPORTING DETAILS ##################################
            reporting = get_reporting_of_emp_of_corresponding_band(qry[0]['dept'], qry[0]['desg'], emp['emp_id'], {})
            emp['reporting_level'] = reporting

            # REVIEW CHECK .................
            emp['is_review'] = check_if_review_is_eligible(reporting)
            ####################################

            emp['status'] = get_statuses_at_reporting_level_of_emp(emp['emp_id'], session)
            status_len = len(emp['status'])

            # REMARK CHECK ................
            if form_type == "EMG-BAND":
                if status_len - int(reporting) > 1:
                    emp['remark'] = False
                else:
                    emp['remark'] = True
            ###################################

            is_eligible_check = check_eligibility_of_employee(emp['emp_id'], session)
            if is_eligible_check == "NOT ELIGIBLE":
                emp['emp_status'] = "NOT ELIGIBLE"
            else:
                emp['emp_status'] = get_submission_status_of_emp_form(emp['emp_id'], form_type, session, {})
            emp['desgination'] = qry[0]['desg__value']
            if len(query) > 0:
                emp['reporting'] = []
                if reporting != None:
                    for i in range(1, int(reporting + 1)):
                        status = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp['emp_id'], level=i,session=session).exclude(status="DELETE").values('approval_status', 'added_by', 'added_by__name', 'id').order_by('-id')
                        if len(status) > 0:
                            emp['reporting'].append({'status': status[0]['approval_status'], 'added_by': status[0]['added_by'], 'added_by__name': status[0]['added_by__name']})
                        else:
                            emp['reporting'].append({'status': 'PENDING', 'added_by': None, 'added_by__name': None})
            else:
                emp['reporting'] = []
                if reporting != None:
                    for i in range(1, int(reporting + 1)):
                        emp['reporting'].append({'status': 'PENDING', 'added_by': None, 'added_by__name': None})

            #################### END.......###########################################
        ############# FOR CONSOLIDATE DATA ####################
        flag = 0
        not_filled = 0
        filled = 0
        max_reporting = get_maximum_reporting(list_emp)
        if form_type != "S-BAND":
            consolidate_data['emp'] = {}
            consolidate_data['emp']['not_filled'] = 0
            consolidate_data['emp']['filled'] = 0
            consolidate_data['emp']['total'] = 0
        for emp in list_emp:
            level_reporting = 0
            if form_type != "S-BAND":
                consolidate_data['emp']['total'] = consolidate_data['emp']['total'] + 1
                if emp['emp_status'] == "NOT FILLED":
                    consolidate_data['emp']['not_filled'] = consolidate_data['emp']['not_filled'] + 1
            if emp['emp_status'] == "FILLED":
                flag = 1
                if form_type != "S-BAND":
                    consolidate_data['emp']['filled'] = consolidate_data['emp']['filled'] + 1
                for level, status in enumerate(emp['status']):
                    if status['desgination'] == qry[0]['desg__value'] and int(level) + 1 <= int(max_reporting) and level_reporting == 0:
                        level = int(max_reporting) - 1
                    if level_reporting == 0:
                        if "level_" + str(int(level) + 1) in consolidate_data:
                            if status['status'] == "PENDING" or status['status'] == "REVIEW":
                                consolidate_data["level_" + str(int(level) + 1)]['not_filled'] = consolidate_data["level_" + str(int(level) + 1)]['not_filled'] + 1
                            if status['status'] == "APPROVED" or status['status'] == "REVIEWED":
                                consolidate_data["level_" + str(int(level) + 1)]['filled'] = consolidate_data["level_" + str(int(level) + 1)]['filled'] + 1
                            consolidate_data["level_" + str(int(level) + 1)]['total'] = consolidate_data["level_" + str(int(level) + 1)]['total'] + 1

                        else:
                            consolidate_data["level_" + str(int(level) + 1)] = {}
                            consolidate_data["level_" + str(int(level) + 1)].update({'not_filled': 0, 'filled': 0, 'total': 1})
                            if status['status'] == "PENDING" or status['status'] == "REVIEW":
                                consolidate_data["level_" + str(int(level) + 1)]['not_filled'] = 1
                            if status['status'] == "APPROVED" or status['status'] == "REVIEWED":
                                consolidate_data["level_" + str(int(level) + 1)]['filled'] = 1
                    if status['desgination'] == qry[0]['desg__value'] and int(level) + 1 <= int(max_reporting) and level_reporting == 0:
                        level_reporting = 1
        if flag == 0:
            for i in range(1, int(max_reporting) + 1):
                consolidate_data["level_" + str(i)] = {}
                consolidate_data["level_" + str(i)]['not_filled'] = 0
                consolidate_data["level_" + str(i)]['filled'] = 0
                consolidate_data["level_" + str(i)]['total'] = 0
        ################### END #################################
    return list_emp, consolidate_data

# in check


def get_increment_in_salary(increment_type, emp_id, session, salary_type, amount):
    print("samyak")
    data = {}
    if increment_type == '---' or salary_type == '---':
        data['increment'] = 0
        data['estimated_salary'] = 0
        data['current_gross'] = 0
        return data
    print(increment_type)
    if amount != None:
        amount = float(amount)
    current_data = get_gross_salary(emp_id, session, {})
    salary = current_data['payable']  # correction
    current_gross = current_data['total_gross']
    print(current_gross)
    new_salary = []
    b_a = 0
    new_gross = 0
    increment = 0
    if "GRADE" in salary_type:
        print("in GRADE")
        main_ids = []
        for pay in salary:
            if pay['value'] == "BASIC" or pay['value'] == "AGP":
                main_ids.append(pay['sal_dropdown_id'])
                b_a = b_a + pay['gross_value']
        del_ids = []

        if increment_type == "NORMAL":
            per_increase = get_percentage_increase(salary_type, increment_type)

            inc_in_b_a = float((b_a * per_increase) / 100)
            new_b_a = inc_in_b_a + float(b_a)
            for i, pay in enumerate(salary):
                if pay['value'] == "BASIC":
                    salary[i]['gross_value'] = float(round(float(salary[i]['gross_value'] + inc_in_b_a), 2))
                    new_gross = new_gross + pay['gross_value']
                    continue
                if pay['value'] == "AGP":
                    new_gross = new_gross + pay['gross_value']
                    continue
                else:
                    per_component = check_if_depend_on_salary_components(main_ids, session, salary, pay['sal_dropdown_id'])
                    if per_component == False:
                        new_gross = new_gross + salary[i]['gross_value']
                        del_ids.append(i)
                    else:
                        salary[i]['gross_value'] = float(round(float((new_b_a * int(per_component)) / 100), 2))
                        new_gross = new_gross + salary[i]['gross_value']
                if "HRA" in str(pay['value']):
                    pay['value'] = "HRA"
            current_salary = get_gross_salary(emp_id, session, {})['payable']
            for pay in current_salary:
                if "HRA" in str(pay['value']):
                    pay['value'] = "HRA"
            del_ids.sort(reverse=True)
            for ids in del_ids:
                del salary[int(ids)]
                del current_salary[int(ids)]
            increment = new_gross - current_gross
            data['before'] = current_salary
            data['after'] = salary
        elif increment_type == "SPECIAL" or increment_type == "PROMOTION WITH SPECIAL INCREAMENT":
            if amount != None:
                for i, pay in enumerate(salary):
                    if pay['value'] == "BASIC" or pay['value'] == "AGP":
                        continue
                    else:
                        per_component = check_if_depend_on_salary_components(main_ids, session, salary, pay['sal_dropdown_id'])
                        if per_component == False:
                            del_ids.append(i)
                    if "HRA" in str(pay['value']):
                        pay['value'] = "HRA"
                del_ids.sort(reverse=True)
                for ids in del_ids:
                    del salary[int(ids)]
                data['before'] = salary
                data['after'] = salary
                new_gross = int(current_gross) + int(amount)
        elif increment_type == "NO INCREMENT" or increment_type == "PROMOTION WITHOUT INCREAMENT":
            for i, pay in enumerate(salary):
                if pay['value'] == "BASIC" or pay['value'] == "AGP":
                    continue
                else:
                    per_component = check_if_depend_on_salary_components(main_ids, session, salary, pay['sal_dropdown_id'])
                    if per_component == False:
                        del_ids.append(i)
                if "HRA" in str(pay['value']):
                    pay['value'] = "HRA"

            del_ids.sort(reverse=True)
            for ids in del_ids:
                del salary[int(ids)]
            data['before'] = salary
            data['after'] = salary
            increment = 0
            new_gross = float(current_gross)
    if (salary_type == "CONSOLIDATE" and increment_type == "NORMAL"):
        print("inconsolidate")
        per_increase = get_percentage_increase(salary_type, increment_type)
        increment = float((current_gross * per_increase) / 100)
        new_gross = current_gross + increment
    if increment_type == "SPECIAL" or increment_type == "PROMOTION WITH SPECIAL INCREAMENT":
        increment = float(amount)
        new_gross = current_gross + increment
    if increment_type == "NO INCREMENT" or increment_type == "PROMOTION WITHOUT INCREAMENT":
        print("none increment")
        increment = 0
        new_gross = float(current_gross)
    if increment < 0:
        increment = 0
    if amount != 0 and amount != None:
        increment = amount
    data['increment'] = str(round(increment, 2))
    data['estimated_salary'] = str(round(new_gross, 2))
    data['current_gross'] = str(round(current_gross, 2))
    return data


def get_max_marks_of_form_part(form_type, form_part,session):
    max_marks = 0
    marks = AppraisalStaffQuestion.objects.filter(Q(parent_ques=0) | Q(parent_ques__isnull=True)).filter(form_type=form_type, form_part=form_part,session=session).exclude(statement__isnull=True).values_list('max_marks', flat=True)
    for m in marks:
        if m != None:
            max_marks = max_marks + int(m)
    return max_marks


def get_recomended_data(e_id, level, form_type, session, extra_exclude):
    data = {}
    data['data'] = []
    data['key'] = []
    data['heading'] = []
    heading = {1: ['Approved by 1st Reporting', 'Review request by 2nd Reporting', 'Reviewed by 1st Reporting'], 2: ['Approved by 2nd Reporting', 'Send a review request at 1st reporting', 'Approve the reviewed request by 1st Reporting'], 2: ['Approved by 3rd Reporting', 'Send a review request at 2nd Reporting', 'Approve the reviewed request by 2nd Reporting']}
    if level != 0:
        for l in range(1, int(level) + 1):
            i = 0
            qry = AppraisalStaffRecommendationApproval.objects.filter(emp_id=e_id, level=l,session=session).exclude(status="DELETE").exclude(approval_status="REVIEW").values('id', 'emp_id', 'increment_type', 'increment_amount', 'promoted_to', 'level', 'approval_status', 'added_by', 'added_by__name', 'added_by__desg__value', 'session', 'session__session', 'status', 'promoted_to__value').order_by('id')
            if len(qry) > 0:

                for q in qry:
                    q['editable'] = check_if_form_editable_or_not(e_id, l, form_type, session, level, None)
                    q['table_data'] = get_increment_in_salary(q['increment_type'], e_id, q['session'], get_salary_type(e_id, q['session'], {})['salary_type__value'], q['increment_amount'])
                    data['data'].append(q)
                    data['key'].append(q['approval_status'])
                    data['heading'].append(str(q['approval_status']) + ' by ' + str(q['added_by__desg__value']))
                    i = i + 1

        return data
    return data

##########################CHANGED####################################


def get_recomended_data_without_review(e_id, level, form_type, session):
    data = {}
    data['data'] = []
    data['key'] = []
    data['heading'] = []
    heading = {1: ['Approved by 1st Reporting', 'Review request by 2nd Reporting', 'Reviewed by 1st Reporting'], 2: ['Approved by 2nd Reporting', 'Send a review request at 1st reporting', 'Approve the reviewed request by 1st Reporting'], 2: ['Approved by 3rd Reporting', 'Send a review request at 2nd Reporting', 'Approve the reviewed request by 2nd Reporting']}
    if level != 0:
        for l in range(1, int(level) + 1):
            i = 0
            qry = AppraisalStaffRecommendationApproval.objects.filter(emp_id=e_id, level=l,session=session).exclude(status="DELETE").exclude(approval_status="REVIEW").exclude(approval_status="REVIEWED").values('id', 'emp_id', 'increment_type', 'increment_amount', 'promoted_to', 'level', 'approval_status', 'added_by', 'added_by__name', 'added_by__desg__value', 'session', 'session__session', 'status', 'promoted_to__value').order_by('id')
            if len(qry) > 0:

                for q in qry:
                    q['editable'] = check_if_form_editable_or_not(e_id, l, form_type, session, level, None)
                    q['table_data'] = get_increment_in_salary(q['increment_type'], e_id, q['session'], get_salary_type(e_id, q['session'], {})['salary_type__value'], q['increment_amount'])
                    data['data'].append(q)
                    data['key'].append(q['approval_status'])
                    data['heading'].append(str(q['approval_status']) + ' by ' + str(q['added_by__desg__value']))
                    i = i + 1

        return data
    return data
##########################CHANGED####################################


def get_employee_status_for_form(emp_id, form_type, session):
    data = []
    qry = AppraisalStaffApplication.objects.filter(emp_id=emp_id, form_type=form_type, session=session).exclude(status="DELETE").values('status', 'id').order_by('-id').distinct()
    if len(qry) > 0:
        data = qry[0]['status']
    return data


def insert_first_pending_request(emp_id, form_type, session):
    check_pending = AppraisalStaffApplication.objects.filter(form_type=form_type, emp_id=emp_id, session=session).exclude(status="DELETE").values_list('status', flat=True)
    if len(check_pending) > 0:
        if "PENDING" in check_pending:
            return True
    AppraisalStaffApplication.objects.create(form_type=form_type, emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), status="PENDING", session=AccountsSession.objects.get(id=session))
    return True


def get_next_level_status(form_type, emp_id, level, session):
    level = int(level) + 1
    qry = AppraisalStaffApplication.objects.filter(form_type=form_type, emp_id=emp_id, session=session).exclude(status="PENDING").values('id').order_by('-id')
    if len(qry) > 0:
        check = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, level=level, session=session).exclude(status="DELETE").values('approval_status', 'id').order_by('-id')
        if len(check) > 0:
            return check[0]['approval_status']
    return False


def get_remark_function(pre_level, level, emp_id, session, form_type):
    remark = {}
    remark['data'] = []
    remark['heading'] = []
    remark['is_editable'] = []
    for l in range(int(pre_level), int(level) + 1):
        qry = AppraisalStaffRecommendationApproval.objects.filter(level=l, emp_id=emp_id, session=session).exclude(status="DELETE").exclude(approval_status="REVIEW").values('remark', 'id', 'approval_status', 'added_by__desg__value').order_by('-id')
        if len(qry) > 0:
            remark['data'].append(qry[0]['remark'])
            remark['heading'].append(str(qry[0]['added_by__desg__value']))
            remark['is_editable'].append(check_if_form_editable_or_not(emp_id, l, form_type, session, level, qry[0]['approval_status']))
        else:
            get_reporting_desg = AarReporting.objects.filter(emp_id=emp_id, reporting_no=l).values('reporting_to', 'reporting_to__value')
            if len(get_reporting_desg) > 0:
                remark['heading'].append(str(get_reporting_desg[0]['reporting_to__value']))
            else:
                remark['heading'].append(None)
            remark['data'].append(None)
            remark['is_editable'].append(check_if_form_editable_or_not(emp_id, l, form_type, session, level, 'PENDING'))
    return remark


def get_remark(form_type, level, emp_id, session):
    remark = {}
    if int(level) != 0:
        pre_level = 1
        remark = get_remark_function(pre_level, level, emp_id, session, form_type)
    return remark


def get_employee_current_salary(emp_id, session):
    del_ids = []
    current_salary = []
    current_data = get_gross_salary(emp_id, session, {})
    if len(current_data) > 0:
        current_salary = current_data['payable']
    main_ids = []
    for pay in current_salary:
        if pay['value'] == "BASIC" or pay['value'] == "AGP":
            main_ids.append(pay['sal_dropdown_id'])
    for i, pay in enumerate(current_salary):
        if pay['value'] == "BASIC" or pay['value'] == "AGP":
            continue
        else:
            per_component = check_if_depend_on_salary_components(main_ids, session, current_salary, pay['sal_dropdown_id'])
            if per_component == False:
                del_ids.append(i)
        if "HRA" in str(pay['value']):
            pay['value'] = "HRA"
    del_ids.sort(reverse=True)
    for ids in del_ids:
        del current_salary[int(ids)]
    return current_salary


def get_detpwise_consolidate_data(department, ladder, session, band, dept):
    bandwise = {}
    bandwise[band] = {}
    bandwise[band] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0}

    for d in department:
        employee = list(EmployeePrimdetail.objects.filter(ladder__value__in=ladder, dept__value=d['dept__value']).exclude(emp_category__value="FACULTY").exclude(emp_id='00007').exclude(emp_status="SEPARATE").values('emp_id', 'dept', 'dept__value', 'desg', 'desg__value').distinct())
        if len(employee) == 0:
            if d['dept__value'] in dept:
                dept[d['dept__value']][band] = {}
                dept[d['dept__value']][band] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0}
            else:
                dept[d['dept__value']] = {}
                dept[d['dept__value']][band] = {}
                dept[d['dept__value']][band] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0}
        for emp in employee:
            emp_status = get_submission_status_of_emp_form(emp['emp_id'], band, session, {})
            level_status = get_statuses_at_reporting_level_of_emp(emp['emp_id'], session)
            if emp_status == 'NOT FILLED':
                bandwise[band]['not_filled'] = bandwise[band]['not_filled'] + 1
                bandwise[band]['total_employee'] = bandwise[band]['total_employee'] + 1
                if emp['dept__value'] in dept:
                    if band not in dept[emp['dept__value']]:
                        dept[emp['dept__value']][band] = {}
                        dept[emp['dept__value']][band] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0}
                    dept[emp['dept__value']][band]['not_filled'] = dept[emp['dept__value']][band]['not_filled'] + 1
                    dept[emp['dept__value']][band]['total_employee'] = dept[emp['dept__value']][band]['total_employee'] + 1
                else:
                    dept[emp['dept__value']] = {}
                    dept[emp['dept__value']][band] = {}
                    dept[emp['dept__value']][band] = {'not_filled': 1, 'filled': 0, 'total_approved': 0, 'total_employee': 1}

            elif emp_status == "FILLED":
                bandwise[band]['filled'] = bandwise[band]['filled'] + 1
                bandwise[band]['total_employee'] = bandwise[band]['total_employee'] + 1
                if emp['dept__value'] in dept:
                    if band not in dept[emp['dept__value']]:
                        dept[emp['dept__value']][band] = {}
                        dept[emp['dept__value']][band] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0}
                    dept[emp['dept__value']][band]['filled'] = dept[emp['dept__value']][band]['filled'] + 1
                    dept[emp['dept__value']][band]['total_employee'] = dept[emp['dept__value']][band]['total_employee'] + 1
                    if len(level_status) > 0:
                        if level_status[-1]['status'] == "APPROVED":
                            dept[emp['dept__value']][band]['total_approved'] = dept[emp['dept__value']][band]['total_approved'] + 1
                else:
                    dept[emp['dept__value']] = {}
                    dept[emp['dept__value']][band] = {}
                    dept[emp['dept__value']][band] = {'not_filled': 0, 'filled': 1, 'total_approved': 0, 'total_employee': 1}
                    if len(level_status) > 0:
                        if level_status[-1]['status'] == "APPROVED":
                            bandwise[band]['total_approved'] = bandwise[band]['total_approved'] + 1
                            dept[emp['dept__value']][band]['total_approved'] = dept[emp['dept__value']][band]['total_approved'] + 1
    return dept, bandwise


def get_approval_status_for_repoprting_level(level, emp_id, session):
    status = "APPROVED"
    qry = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level) + 1, session=session).exclude(status="DELETE").values('approval_status').order_by('-approval_status')
    if len(qry) > 0:
        if qry[0]['approval_status'] == "REVIEW":
            status = "REVIEWED"
    return status


def get_first_reporting_total_marks(emp_id, form_type, status, level, session, extra_filter):
    total_marks = 0
    ###### PART FOR EACH FORM TYPE IN FIRST LEVEL IS ONLY ONE IN THIS CASE ###########
    # status = str(status)
    qry = AppraisalStaffAnswer.objects.filter(application__emp_id=emp_id, application__form_type=form_type, application__session=session, level=level, status=status).exclude(status="DELETE").values_list('marks_obtained', flat=True)
    for q in qry:
        if q != None:
            total_marks = total_marks + int(q)
    return total_marks


def get_max_reporting_of_all_employee(employee):
    max_reporting = 0
    for emp in employee:
        qry = AarReporting.objects.filter(emp_id=emp['emp_id']).exclude(emp_id__emp_status="SEPARATE").values_list('reporting_no', flat=True)
        if int(len(qry)) > int(max_reporting):
            max_reporting = int(len(qry))
    return max_reporting


def get_level_wise_propose_increment(emp_id, max_reporting, session):
    data = {}
    ######## STATIC PRPOSED SALARY HEADING FOR LEVEL WISE ########
    heading = ['HOD PROPOSED SALARY', 'JOINT DIRECTOR PROPOSED SALARY', 'DIRECTOR PROPOSED SALARY']
    i = len(heading)
    ##############################################################
    if int(max_reporting) != 0:
        qry = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, session=session).exclude(approval_status="REVIEW").exclude(status="DELETE").values('level').distinct()
        for l in range(len(qry), 0, -1):
            get_increment = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, level=l,session=session).exclude(approval_status="REVIEW").exclude(status="DELETE").values('increment_amount').order_by('-increment_amount')
            if len(get_increment) > 0:
                if get_increment[0]['increment_amount'] != None and len(heading) >= i:
                    data.upadte({heading[i - 1]: get_increment[0]['increment_amount']})
                    max_reporting = int(max_reporting) - 1
                    i = i - 1
        if int(max_reporting) != 0 and len(heading) >= i:
            for r in range(int(max_reporting), 0, -1):
                data.update({heading[i - 1]: 0})
                i = i - 1
    return data


def get_proposed_increment(emp_id, level, session):
    data = {'increment_amount': 0, 'increment_type': '---', 'promoted_to': '---', 'estimated_gross_salary': 0}
    qry = AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level),session=session).exclude(status="DELETE").values('increment_type', 'id', 'increment_amount', 'promoted_to__value').order_by('-id')
    if len(qry) > 0:
        data['increment_type'] = qry[0]['increment_type']
        data['increment_amount'] = qry[0]['increment_amount']
        data['promoted_to'] = qry[0]['promoted_to__value']
        emp_salary_type = get_salary_type(emp_id, session, {})
        if len(emp_salary_type) > 0:
            salary_type = emp_salary_type['salary_type__value']
        else:
            salary_type = '---'
        salary = get_increment_in_salary(data['increment_type'], emp_id, session, salary_type, data['increment_amount'])
        data['estimated_gross_salary'] = salary['estimated_salary']
    return data


def get_training_suggestion_of_emp_form(emp_id, form_type, session):
    data = {'Training': '---', 'Suggestions': '---'}
    if "EMG-BAND" in str(form_type):
        form_part = "PART-3"
        qry = list(AppraisalStaffQuestion.objects.filter(parent_ques=0, session=session, form_type=form_type, form_part=form_part).exclude(status="DELETE").exclude(statement__isnull=True).values('ques_id', 'statement'))
        for q in qry:
            if 'Training' in str(q['statement']) or 'suggestions' in q['statement']:
                get_data = list(AppraisalStaffAnswer.objects.filter(application__emp_id=emp_id, status="SUBMITTED", level=0, ques_id=q['ques_id']).exclude(application__status="DELETE").exclude(status="DELETE").values_list('answer', flat=True))
                if len(get_data) > 0:
                    if 'Training' in q['statement']:
                        data['Training'] = get_data[0]
                    else:
                        data['Suggestions'] = get_data[0]

    elif 'A-BAND' in str(form_type):
        form_part = 'PART-2'
        qry = list(AppraisalStaffQuestion.objects.filter(parent_ques=0, session=session, form_type=form_type, form_part=form_part).exclude(status="DELETE").exclude(statement__isnull=True).values('ques_id', 'statement'))
        for q in qry:
            if 'training' in q['statement'] or 'Suggestions' in q['statement']:
                get_data = list(AppraisalStaffAnswer.objects.filter(application__emp_id=emp_id, status="SUBMITTED", level=0, ques_id=q['ques_id']).exclude(application__status="DELETE").exclude(status="DELETE").values_list('answer', flat=True))
                if len(get_data) > 0:
                    if 'training' in q['statement']:
                        data['Training'] = get_data[0]
                    else:
                        data['Suggestions'] = get_data[0]

    return data
