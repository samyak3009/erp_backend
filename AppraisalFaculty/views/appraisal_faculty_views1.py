
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

# from Accounts.views import getCurrentSession
# from aar.dept_achievement import get_all_emp
# from StudentAcademics.views import get_organization, get_emp_category, get_department

# from .appraisal_faculty_functions import *
# from .appraisal_faculty_checks import *

# #'''import functions'''
# # Create your views here.


# def form_emp_end(request):
#     data = {}
#     session = getCurrentSession(None)
#     emp_id = request.session['hash1']
#     level = 0

#     if check_if_faculty(emp_id) == True:
#         session_name = request.session['Session_name']
#         sem_type = request.session['sem_type']
#         unlock_type = "INC"
        # if int(session_name[:2]) < 20:
        #     return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        # ########################################### CHECKS ####################################################
        # experience_check = check_eligibility_of_employee_faculty(emp_id, session)
        # check_is_locked = check_if_submit_unlocked(unlock_type, emp_id, session, {})
        # if experience_check == "NOT ELIGIBLE":
        #     data['msg'] = "You are not eligible to fill this form."
        #     data['already_filled'] = "NOT FILLED"
        #     return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        # if check_is_locked == True:
        #     already_filled_check = check_if_already_filled_final(emp_id, session, level)
        #     if already_filled_check != False:
        #         already_filled_check = "FILLED"
        #     else:
        #         already_filled_check = "NOT FILLED"
        #     data['msg'] = 'Appraisal Form is Locked.'
        #     data['already_filled'] = already_filled_check
        #     # return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        # else:
        #     already_filled_check = check_if_already_filled_final(emp_id, session, level)
        #     if already_filled_check != False:
        #         already_filled_check = "FILLED"
        #         data['msg'] = 'You have already filled your Appraisal Form.'
        #     else:
        #         data['already_filled'] = already_filled_check
#         ########################################### CHECKS END ####################################################

#         if requestMethod.GET_REQUEST(request):
#             if requestType.custom_request_type(request.GET, 'get_employee_data'):
#                 if create_incial_pending_request(emp_id, session, session_name) == True:
#                     level = request.GET['level']
#                     data['personal'] = get_emp_part_data(emp_id, session, {})
#                     data['data'] = {}
#                     data['data']['cat1'] = get_cat1_form_data(emp_id, level, session, session_name)
#                     # data['data']['cat2'] = get_cat2_form_data(emp_id, level, session, session_name)
#                     # data['data']['cat3'] = get_cat3_form_data(emp_id, level, session, session_name)
#                     # data['data']['cat4'] = get_cat4_form_data(emp_id, level, session, session_name)
#                     # data['next_level_status'] = get_next_level_status(emp_id, level, session)
#                     # data['status'] = get_submission_status_of_emp(emp_id, session)

#                     roles = [319, 1371]
#                     if check_is_hod_dean(emp_id, session, roles) == True:
#                         data['is_hod_dean'] = True
#                     else:
#                         data['is_hod_dean'] = False
#                 else:
#                     data = {'msg': 'Something went wrong'}
#             return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#         elif requestMethod.POST_REQUEST(request):
#             body = json.loads(request.body)
#             print(body, 'body')
#             personal_data = body['personal']
#             category_data = body['data']
#             action = body['action']
#             is_hod_dean = body['is_hod_dean']
#             level = 0
#             today_date = date.today()
#             #####################################
#             if action == 'SAVE':
#                 status = "SAVED"
#                 form_filled_status = 'N'
#                 data = {'msg': 'Appraisal Form Is Saved Sucessfully.'}
#             elif action == 'SUBMIT':
#                 status = "SUBMITTED"
#                 form_filled_status = 'Y'
#                 data = {'msg': 'Appraisal Form Is Submitted Sucessfully.'}
#             #####################################
#             if status == "SUBMITTED":
#                 if check_for_final_submit(category_data, is_hod_dean, level) == False:
#                     return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Fields cannot be empty.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#             #### UPDATE ####
#             check_for_filled = check_if_already_filled(emp_id, session)
#             if check_for_filled[0] == True:
#                 last_id = check_for_filled[1]
#                 FacultyAppraisal.objects.filter(emp_id=emp_id, id=last_id).exclude(status="DELETE").exclude(status="PENDING").update(status="DELETE")
#                 if delete_row_from_all_tables([last_id], session, level, None) != True:
#                     return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Something went wrong.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#             ################
#             ############### FOR PART-1 DATA ###############
#             #### GET CAT3 A3 & A4 & A5 DATA ####
#             if 'cat4' in category_data:
#                 if 'A3' in category_data['cat4']:                    print(schedule)

#                     if 'achievement' in category_data['cat4']['A3']['data'][0]:
#                         achievement_recognition = category_data['cat4']['A3']['data'][0]['achievement']
#                     else:
#                         achievement_recognition = None
#                 else:
#                     achievement_recognition = None
#                 if 'A4' in category_data['cat4']:
#                     if 'training_needs' in category_data['cat4']['A4']['data'][0]:
#                         training_needs = category_data['cat4']['A4']['data'][0]['training_needs']
#                     else:
#                         training_needs = None
#                 else:
#                     training_needs = None
#                 if 'A5' in category_data['cat4']:
#                     if 'suggestions' in category_data['cat4']['A5']['data'][0]:
#                         suggestions = category_data['cat4']['A5']['data'][0]['suggestions']
#                     else:
#                         suggestions = None
#                 else:
#                     suggestions = None
#             ####################################

#             FacultyAppraisal.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=personal_data['emp_id']), dept=EmployeeDropdown.objects.get(sno=personal_data['dept']), desg=EmployeeDropdown.objects.get(sno=personal_data['desg']), highest_qualification=personal_data['h_qual'], salary_type=AccountsDropdown.objects.get(sno=personal_data['salary_type_id']), current_gross_salary=personal_data['current_gross_salary'], agp=personal_data['agp'], total_experience=personal_data['total_experience'], form_filled_status=form_filled_status, status=status, achievement_recognition=achievement_recognition, training_needs=training_needs, suggestions=suggestions, level=level, emp_date=today_date, session=AccountsSession.objects.get(id=session))
#             app_id = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session).exclude(status="DELETE").exclude(status="PENDING").values_list('id', flat=True).order_by('-id')
#             # PART -1 END ##################################
#             if len(app_id) == 0:
#                 return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Something went wrong.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#             fac_app_id = FacultyAppraisal.objects.get(id=app_id[0])

#             #### FOR CAT-1 ####
#             if 'cat1' in category_data:
#                 if 'A1' in category_data['cat1']:
#                     category_data['cat1']['A1']['data'] = score_calculation_of_cat1('A1', category_data['cat1']['A1']['data'])
#                     for catA1 in category_data['cat1']['A1']['data']:
#                         if catA1['course_paper'] != None and catA1['lec_per_academic'] != None:
#                             FacAppCat1A1.objects.create(fac_app_id=fac_app_id, course_paper=catA1['course_paper'], lectues_calendar=catA1['lec_per_academic'], lectues_portal=catA1['lec_per_taken'], score_claimed=catA1['score_claimed'])

#                 if 'A2' in category_data['cat1']:
#                     category_data['cat1']['A2']['data'] = score_calculation_of_cat1('A2', category_data['cat1']['A2']['data'])
#                     for catA2 in category_data['cat1']['A2']['data']:
#                         # if catA2['consulted'] != None:
#                         if 'consulted' in catA2:
#                             consulted = catA2['consulted']
#                         else:
#                             consulted = None
#                         if 'prescribed' in catA2:
#                             prescribed = catA2['prescribed']
#                         else:
#                             prescribed = None
#                         if 'additional_resource' in catA2:
#                             additional_resource = catA2['additional_resource']
#                         else:
#                             additional_resource = None
#                         FacAppCat1A2.objects.create(fac_app_id=fac_app_id, course_paper=catA2['course_paper'], consulted=consulted, prescribed=prescribed, additional_resource=additional_resource, score_claimed=catA2['score_claimed'])

#                 if 'A3' in category_data['cat1']:
#                     category_data['cat1']['A3']['data'] = score_calculation_of_cat1('A3', category_data['cat1']['A3']['data'])
#                     for catA3 in category_data['cat1']['A3']['data']:
#                         # if catA3['short_descriptn'] != None:
#                         if 'short_descriptn' in catA3:
#                             short_descriptn = catA3['short_descriptn']
#                         else:
#                             short_descriptn = None
#                         if short_descriptn != None:
#                             FacAppCat1A3.objects.create(fac_app_id=fac_app_id, short_descriptn=short_descriptn, score_claimed=catA3['score_claimed'])
#                 if is_hod_dean == False:
#                     if 'A4' in category_data['cat1']:
#                         category_data['cat1']['A4']['data'] = score_calculation_of_cat1('A4', category_data['cat1']['A4']['data'])
#                         for i, catA4 in enumerate(category_data['cat1']['A4']['data']):
#                             # if catA4['duties_assign'] != None and catA4['executed'] != None and catA4['extent_to_carried'] != None:
#                             FacAppCat1A4.objects.create(fac_app_id=fac_app_id, sno=int(i), executed=catA4['executed'], extent_to_carried=catA4['extent_to_carried'], duties_assign=catA4['duties_assign'], score_claimed=catA4['score_claimed'])
#             # END #############

#             #### FOR CAT-2 ####
#             if 'cat2' in category_data:
#                 if 'A1' in category_data['cat2']:
#                     for cat2A1 in category_data['cat2']['A1']['data']:
#                         if 'type_of_activity' in cat2A1:
#                             type_of_activity = cat2A1['type_of_activity']
#                         else:
#                             type_of_activity = None
#                         if 'average_hours' in cat2A1:
#                             average_hours = cat2A1['average_hours']
#                         else:
#                             average_hours = None
#                         if 'score_claimed' in cat2A1:
#                             score_claimed = cat2A1['score_claimed']
#                         else:
#                             score_claimed = None
#                         # if cat2A1['type_of_activity'] != None and cat2A1['average_hours'] != None and cat2A1['score_claimed'] != None:
#                         FacAppCat2A1.objects.create(fac_app_id=fac_app_id, type_of_activity=type_of_activity, average_hours=average_hours, score_claimed=score_claimed)
#             # END #############

#             #### FOR CAT-3 ####
#             if 'cat3' in category_data:
#                 is_entery_in_achievement = check_for_achievement_data(category_data['cat3'], fac_app_id, level)
#                 if is_entery_in_achievement[0] == True:
#                     for ach in is_entery_in_achievement[1]:
#                         FacAppCat3Achievement.objects.create(fac_app_id=fac_app_id, type=ach['type'], achievement_id=ach['id'], score_claimed=ach['score_claimed'])
#             # END #############

#             #### FOR CAT-4 ####
#             if 'cat4' in category_data:
#                 if 'A1' in category_data['cat4']:
#                     for cat4A1 in category_data['cat4']['A1']['data']:
#                         FacAppCat4A1.objects.create(fac_app_id=fac_app_id, branch_details=cat4A1['branch'], subject=cat4A1['subject'], result_clear_pass=cat4A1['pass_per'], result_external=cat4A1['average_external'], stu_below_40=cat4A1['below_40'], stu_40_49=cat4A1['in_40_49'], stu_50_59=cat4A1['in_50_59'], stu_above_60=cat4A1['above_60'], score_claimed=cat4A1['score_claimed'])
#                     for cat4A1 in category_data['cat4']['A1']['data2']:
#                         if cat4A1['institute1'] != None and cat4A1['institute2'] != None and cat4A1['ext_exam_average1'] != None and cat4A1['ext_exam_average2'] != None:
#                             institute1 = str(cat4A1['institute1']) + '-INST(1)'
#                             # else:
#                             #     institute1 = None
#                             FacAppCat4A1.objects.create(fac_app_id=fac_app_id, branch_details=institute1, subject=cat4A1['subject'], result_external=cat4A1['ext_exam_average1'], score_claimed=cat4A1['score_claimed'])
#                             institute2 = str(cat4A1['institute2']) + '-INST(2)'
#                             # else:
#                             #     institute2 = None
#                             FacAppCat4A1.objects.create(fac_app_id=fac_app_id, branch_details=institute2, subject=cat4A1['subject'], result_external=cat4A1['ext_exam_average2'], score_claimed=cat4A1['score_claimed'])
#                 if 'A2' in category_data['cat4']:
#                     for cat4A2 in category_data['cat4']['A2']['data']:
#                         FacAppCat4A2.objects.create(fac_app_id=fac_app_id, branch=cat4A2['branch'], semester=cat4A2['semester'], section=cat4A2['section'], subject=cat4A2['branch'], overall_avg=cat4A2['overall_avg'], student_feedback=cat4A2['student_feedback'], score_claimed=cat4A2['score_claimed'])
#             # END #############

#             return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#         return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
#     else:
#         return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


# def reporting_level_form(request):
#     data = {}
#     session = getCurrentSession(None)
#     added_by_id = request.session['hash1']

#     if check_if_any_reporting_level(None, session, added_by_id) == True or checkpermission(request, [rolesCheck.ROLE_HR_REPORTS, rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS:
#         session_name = request.session['Session_name']
#         sem_type = request.session['sem_type']
#         unlock_type = "INC"

#         if int(session_name[:2]) < 19:
#             return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#         ######### CHEKS ############
#         check_is_locked = check_if_submit_unlocked(unlock_type, added_by_id, session, {})
#         if check_is_locked == True:
#             return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Appraisal Form is Locked.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#         ####### CHECKS END ###################
#         if requestMethod.GET_REQUEST(request):
#             if requestType.custom_request_type(request.GET, 'get_employee_under_reporting'):
#                 emp_list = get_faculty_under_reporting(added_by_id, session)[0]
#                 data = {'data': emp_list, 'max_reporting': get_maximum_reporting(emp_list)}

#             elif requestType.custom_request_type(request.GET, 'get_all_desg'):
#                 emp_id = request.GET['emp_id']
#                 data = get_emp_desg(emp_id)

#             elif requestType.custom_request_type(request.GET, 'get_employee_form_data_under_reporting'):
#                 category_data = {}
#                 emp_id = request.GET['e_id']
#                 level = request.GET['level']
#                 if emp_id == '':
#                     return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Kindly go back to previous page.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

#                 category_data['cat1'] = get_cat1_form_data(emp_id, level, session, session_name)
#                 category_data['cat2'] = get_cat2_form_data(emp_id, level, session, session_name)
#                 category_data['cat3'] = get_cat3_form_data(emp_id, level, session, session_name)
#                 category_data['cat4'] = get_cat4_form_data(emp_id, level, session, session_name)

#                 roles = [319, 1371]
#                 if check_is_hod_dean(emp_id, session, roles) == True:
#                     is_hod_dean = True
#                 else:
#                     is_hod_dean = False
#                 session_date = '1-August 2018 to 31=August 2019'
#                 data = {'personal': get_emp_part_data(emp_id, session, {}), 'data': category_data, 'is_hod_dean': is_hod_dean, 'part_III': score_sheet_data(emp_id, level), 'recomended_data': get_recomended_data_faculty(emp_id, level,  session), 'remark': get_remark_faculty(level, emp_id, session),'session_date':session_date}

#             elif requestType.custom_request_type(request.GET, 'review_request'):
#                 level = request.GET['level']
#                 e_id = request.GET['e_id']
#                 remark = request.GET['remark']
#                 if int(level) <= 1:
#                     return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Review request are not been requested at this level.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

#                 if check_for_review_request_faculty(e_id, added_by_id, session, level) == False:
#                     return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Review request can be made only once. Please contact registrar for the same.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#                 else:
#                     FacAppRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=e_id), level=level, remark=remark, approval_status="REVIEW", added_by=EmployeePrimdetail.objects.get(emp_id=added_by_id), session=AccountsSession.objects.get(id=session))
#                     get_earlier_reporting_id = FacAppRecommendationApproval.objects.filter(emp_id=e_id, level=int(level) - 1).exclude(status="DELETE").values('added_by').order_by('-id')
#                     if len(get_earlier_reporting_id) > 0:
#                         FacAppRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=e_id), level=int(level) - 1, remark=remark, approval_status="REVIEW", added_by=EmployeePrimdetail.objects.get(emp_id=get_earlier_reporting_id[0]['added_by']), session=AccountsSession.objects.get(id=session))
#                         data = {"msg": "Reviewed request is submitted successfully."}
#                     else:
#                         data = {"msg": "Something went wrong."}

#             elif requestType.custom_request_type(request.GET, 'get_increment'):
#                 increment_type = request.GET['increment_type']
#                 emp_id = request.GET['emp_id']
#                 salary_type = request.GET['salary_type']
#                 if 'amount' in request.GET:
#                     amount = request.GET['amount']
#                     if amount == None:
#                         amount = 0
#                 else:
#                     amount = 0
#                 data = get_increment_in_salary(increment_type, emp_id, session, salary_type, amount)

#             return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#         elif requestMethod.POST_REQUEST(request):
#             data = {}
#             body = json.loads(request.body)
#             print(body)
#             ###################### CHECKS FOR 60% ELIGIBILITY AND MAX MARKS NOT LESS THAN OBT MARKS ################
#             if 'request_type' in body:  # get_increment_type #############
#                 emp_id = body['emp_id']
#                 max_marks = body['max_marks']
#                 marks_obt = body['marks_obt']
#                 if check_eligibility_at_sixty_per_marks_faculty(marks_obt, max_marks) == False:
#                     data = {'msg': 'Marks awarded are less than the eligibility criteria for increment.', 'data': ({"increment_type": get_increment_type(), 'increment_dropdown': get_increment_dropdown(), 'promotion': get_promotion_dropdown(), 'before': get_employee_current_salary(emp_id, session)})}

#                 else:
#                     data['data'] = ({"increment_type": get_increment_type(), 'increment_dropdown': get_increment_dropdown(), 'promotion': get_promotion_dropdown(), 'before': get_employee_current_salary(emp_id, session), 'current_gross': get_gross_salary(emp_id, session, {})['total_gross']})
#                 return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#             else:
#                 category_data = body['data']
#                 personal_data = body['personal']
#                 remark = body['remark']
#                 emp_id = body['emp_id']
#                 level = body['level']
#                 max_marks = body['max_marks']
#                 marks_obt = body['marks_obt']
#                 is_hod_dean = body['is_hod_dean']

#                 #### FOR REMARK ####
#                 if 'remark' in body:
#                     remark = body['remark']['data'][-1]
#                 else:
#                     remark = None
#                 ####################
#                 ### FOR FACULTY CREATE OR EDIT ROW TO ENTER ONLY AWARDED MARKS ###
#                 create = False
#                 ###################################

#                 ########### FOR APPROVAL STATUS ##################
#                 approval_status = get_approval_status_for_repoprting_level_faculty(level, emp_id, session)
#                 if approval_status == "REVIEWED":
#                     create = True
#                 ##################################################
#                 if check_for_final_submit(category_data, is_hod_dean, level) == False:
#                     return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Fields cannot be empty.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#                 ###### FOR UPDATE #####################
#                 already_filled_status = check_if_already_filled_reporting(emp_id,  session, level, approval_status)
#                 already_filled = already_filled_status[0]
#                 already_filled_id = already_filled_status[1]
#                 if already_filled == False:
#                     already_filled_id = None
#                 if already_filled_id != None:
#                     if int(level) == 1:
#                         if delete_row_from_all_tables(already_filled_id, session, level, approval_status) != True:
#                             return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Something went wrong.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#                     FacAppRecommendationApproval.objects.filter(emp_id=emp_id, added_by=added_by_id, session=session, level=level, approval_status=approval_status).exclude(status="DELETE").update(status="DELETE")
#                     create = True

#                 ############ END......#################
#                 last_id = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, status="SUBMITTED", form_filled_status="Y").exclude(status="DELETE").values_list('id', flat=True)
#                 if len(last_id) > 0:
#                     ########## FOR RECOMMENTATION ###############################
#                     increment_type = body['increment_type']
#                     if 'increment_amount' in body:
#                         if body['increment_amount'] != None:
#                             increment_amount = body['increment_amount']
#                         else:
#                             increment_amount = body['increment_amount']
#                     if increment_type == 'PROMOTION WITH SPECIAL INCREAMENT' or increment_type == 'PROMOTION WITHOUT INCREAMENT':
#                         promoted_to = EmployeeDropdown.objects.get(sno=body['promoted_to'])
#                     else:
#                         promoted_to = None
#                     #############################################################
#                     if increment_type != "NO INCREMENT":
#                         ########## CHECK FOR 60% ELIGIBILITY ##########################
#                         if check_eligibility_at_sixty_per_marks_faculty(marks_obt, max_marks) == False:
#                             data = {"msg": "Marks for this part are less than the eligibility criteria for increment."}
#                             return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

#                     if check_for_next_level_approval_exist_faculty(level, emp_id, session) == False:
#                         return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Since next reporting level approved this form so you cannot edit.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
#                     ######## ENTER AWARDED MARKS ########
#                     if int(level) == 1:
#                         if create == False:
#                             if enter_awarded_marks_hod_first_time(category_data, last_id[0], is_hod_dean, level) != True:
#                                 return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Something went wrong.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

#                         elif create == True:
#                             if create_another_rows_for_hod_marks(category_data, last_id[0], is_hod_dean, level, approval_status) != True:
#                                 return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Something went wrong.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

#                     #####################################

#                     #### ENTER RECOMMENDATION ####
#                     FacAppRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), increment_type=increment_type, increment_amount=increment_amount, promoted_to=promoted_to, level=level, remark=remark, approval_status=approval_status, added_by=EmployeePrimdetail.objects.get(emp_id=added_by_id), session=AccountsSession.objects.get(id=session))
#                     ##############################
#                     data = {'msg': 'Appraisal Form Is Submitted Sucessfully.'}
#                 else:
#                     data = {'msg': 'Something went wrong.'}
#                 return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

#         else:
#             return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
#     else:
#         return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
