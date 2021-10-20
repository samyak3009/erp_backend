
# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals

# # '''essentials'''

# from django.http import HttpResponse, JsonResponse
# from django.shortcuts import render
# from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
# import json
# # from datetime import datetime
# import datetime
# import operator
# from datetime import date
# from StudentMMS.constants_functions import requestType
# from erp.constants_variables import statusCodes, statusMessages, rolesCheck
# from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

# from musterroll.models import EmployeePerdetail, Roles
# from login.models import EmployeePrimdetail
# from login.models import AarDropdown, EmployeeDropdown
# from login.views import checkpermission, generate_session_table_name

# from AppraisalStaff.models import *
# from AppraisalStaff.constants_functions.functions import *
# from AppraisalStaff.views.appraisal_staff_function import *
# from AppraisalStaff.views.appraisal_staff_checks_function import *

# from Accounts.views import getCurrentSession,getCurrentSession_BySessionName
# from aar.dept_achievement import get_all_emp
# from StudentAcademics.views import get_organization, get_emp_category, get_department

# from .appraisal_faculty_functions import *
# from .appraisal_faculty_checks import *

# #'''import functions'''
# # Create your views here.


# def cv_raman_report(request):
#     data = []
#     if request.user.is_authenticated:
#         session = getCurrentSession(None)
#         emp_id = request.session['hash1']
#         if checkpermission(request, [rolesCheck.ROLE_HR_REPORTS, rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS:
#             if requestMethod.GET_REQUEST(request):
#                 if requestType.custom_request_type(request.GET, 'form_data'):
#                     emps = EmployeePrimdetail.objects.filter(emp_category__value="FACULTY").exclude(emp_id="00007").exclude(emp_status="SEPARATE").values('emp_id', 'name', 'desg', 'desg__value', 'dept', 'dept__value').order_by('dept__value', 'name')
#                     for emp in emps:
#                         emp['total'] = 0
#                         qry = FacultyAppraisal.objects.filter(emp_id=emp['emp_id'], form_filled_status='Y', status="SUBMITTED").exclude(status="DELETE").values_list('id', flat=True).order_by('-id')
#                         if len(qry) > 0:
#                             type_list = ['RESEARCH PAPER IN JOURNAL', 'RESEARCH PAPER IN CONFERENCE', 'BOOKS', 'PROJECTS/CONSULTANCY', 'PATENT', 'RESEARCH GUIDANCE / PROJECT GUIDANCE', 'TRAINING AND DEVELOPMENT PROGRAM', 'LECTURES AND TALKS']
#                             for ach in type_list:
#                                 total = 0
#                                 achievement = [{'total': 0}]

#                                 ach_data = GetAllAchievementEmployee(emp['emp_id'], ach, session)
#                                 achievement_data = score_calculation_of_cat3_per_report(ach, ach_data, session)
#                                 achievement = achievement_data[1]
#                                 if achievement['total'] == 0 or achievement['total'] == None:
#                                     achieve = {"type": ach, 'total': '---'}
#                                 else:
#                                     total = achievement['total']
#                                     achieve = {"type": ach, 'total': total}

#                                 if 'JOURNAL' in ach:
#                                     ach = 'journal'
#                                 elif 'CONFERENCE' in ach:
#                                     ach = 'conference'
#                                 elif 'BOOKS' in ach:
#                                     ach = 'books'
#                                 elif 'PROJECTS' in ach:
#                                     ach = 'projects'
#                                 elif 'PATENT' in ach:
#                                     ach = 'patent'
#                                 elif 'GUIDANCE' in ach:
#                                     ach = 'guidance'
#                                 elif 'TRAINING' in ach:
#                                     ach = 'training'
#                                 elif 'LECTURES' in ach:
#                                     ach = 'lectures'
#                                 emp[ach] = achieve
#                                 emp['total'] = emp['total'] + total
#                             data.append(emp)
#                 return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
#             else:
#                 return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
#         else:
#             return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
#     else:
#         return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


# def faculty_hr_report(request):
#     data = []
#     if request.user.is_authenticated:
#         # session = getCurrentSession(None)
#         session = getCurrentSession_BySessionName(request.session['Session'])
#         session_name = request.session['Session_name']
#         emp_id = request.session['hash1']
#         if checkpermission(request, [rolesCheck.ROLE_HR_REPORTS, rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS:
#             if requestMethod.GET_REQUEST(request):
#                 if requestType.custom_request_type(request.GET, 'form_data'):
#                     consolidate_data = []
#                     table_data = []
#                     heading = ['NOT FILLED', 'FILLED', 'NOT ELIGIBLE', 'TOTAL APPROVED', 'TOTAL EMPLOYEE']
#                     department = list(EmployeePrimdetail.objects.filter(emp_category__value="FACULTY").exclude(dept__isnull=True).values('dept', 'dept__value').order_by('dept__value').distinct())
#                     consolidate_data = get_detpwise_consolidate_data(department, session)

#                     emps = EmployeePrimdetail.objects.filter(emp_category__value="FACULTY").exclude(emp_id="00007").exclude(emp_status="SEPARATE").values('emp_id', 'name', 'dept__value', 'dept', 'desg', 'desg__value').order_by('dept__value', 'name')
#                     for emp in emps:
#                         data1 = {}
#                         data1 = get_emp_part_data(emp['emp_id'], session, {})
#                         level_status = get_statuses_at_reporting_level_of_faculty(emp['emp_id'], session)

#                         level_1_status = "PENDING"
#                         for i in range(1, len(level_status) + 1):
#                             data1['level_' + str(i) + 'status'] = level_status[i - 1]['status']
#                             if i == 1:
#                                 level_1_status = level_status[i - 1]['status']
#                             proposed_data = get_proposed_increment_faculty(emp['emp_id'], i, session)
#                             increment_amount = {}
#                             increment_amount['increment'] = '---'
#                             data1['level_' + str(i) + 'increment_type'] = proposed_data['increment_type']
#                             if 'NORMAL' in str(proposed_data['increment_type']):
#                                 increment_amount = get_increment_in_salary(proposed_data['increment_type'], emp['emp_id'], session, data1['salary_type'], 0)
#                                 # print(increment_amount, 'increment_amount')
#                             else:
#                                 increment_amount['increment'] = proposed_data['increment_amount']
#                             data1['level_' + str(i) + 'increment_amount'] = increment_amount['increment']
#                             data1['level_' + str(i) + 'promoted_to'] = proposed_data['promoted_to']
#                             data1['level_' + str(i) + 'estimated_gross_salary'] = proposed_data['estimated_gross_salary']

#                         is_eligible_check = check_eligibility_of_employee_faculty(emp['emp_id'], session)
#                         if is_eligible_check == "NOT ELIGIBLE":
#                             data1['emp_status'] = "NOT ELIGIBLE"
#                         else:
#                             data1['emp_status'] = get_submission_status_of_emp(emp['emp_id'],  session)

#                         #### FOR IS_REVIEW_MARKS ####
#                         data1['is_review_marks'] = False
#                         if len(level_status) > 0:
#                             if level_status[-1]['status'] == "APPROVED":
#                                 review_check = FacAppRecommendationApproval.objects.filter(emp_id=emp['emp_id'], approval_status="REVIEW").exclude(status="DELETE").values()
#                                 if len(review_check) > 0:
#                                     data1['is_review_marks'] = True
#                         #############################
#                         level_status = get_statuses_at_reporting_level_of_faculty(emp['emp_id'], session)

#                         last_level = len(level_status)

#                         data1['reporting_level'] = last_level
#                         remarks = get_remark_faculty(last_level, emp['emp_id'], session)
#                         if len(remarks) != 0:
#                             for x in range(0, len(remarks['data'])):
#                                 remark_key = "level_" + str(x + 1) + '_remark'
#                                 data1[remark_key] = remarks['data'][x]

#                         data1['is_view'] = True
#                         data1['is_print'] = False
#                         if len(level_status) > 0:
#                             if level_status[-1]['status'] == "APPROVED":
#                                 data1['is_print'] = True
#                         marks_data = get_total_hod_awarded_marks(emp['emp_id'], session, session_name, 1)
#                         data1['hod_marks'] = marks_data[0]
#                         cat_marks = marks_data[1]
#                         training_sugg_data = get_training_sugg(emp['emp_id'], session)
#                         for k, v in training_sugg_data.items():
#                             data1[k] = v
#                         for k, v in cat_marks.items():
#                             data1[k] = round(v, 2)
#                         table_data.append(data1)

#                     data = {'heading': heading, 'consolidate_data': consolidate_data, 'table_data': table_data}

#                 return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
#             else:
#                 return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
#         else:
#             return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
#     else:
#         return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
