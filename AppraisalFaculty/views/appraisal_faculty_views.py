
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# '''essentials'''

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
import json
# from datetime import datetime
import datetime
import operator
from datetime import date
from StudentMMS.constants_functions import requestType
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

from musterroll.models import EmployeePerdetail, Roles
from login.models import EmployeePrimdetail
from login.models import AarDropdown, EmployeeDropdown
from login.views import checkpermission, generate_session_table_name

from AppraisalStaff.models import *
from AppraisalStaff.constants_functions.functions import *
from AppraisalStaff.views.appraisal_staff_function import *
from AppraisalStaff.views.appraisal_staff_checks_function import *

from Accounts.views import getCurrentSession,getCurrentSession_BySessionName
from aar.dept_achievement import get_all_emp
from StudentAcademics.views import get_organization, get_emp_category, get_department

from .appraisal_faculty_functions import *
from .appraisal_faculty_checks import *

#'''import functions'''
# Create your views here.


def form_emp_end(request):
    data = {}
    session = getCurrentSession(None)
    emp_id = request.session['hash1']
    level = 0
    is_editable = 0
    if check_if_faculty_new(emp_id) == True:
        session_name = request.session['Session_name']
        sem_type = request.session['sem_type']
        unlock_type = "INC"
        if int(session_name[:2]) < 20:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        ########################################### CHECKS ####################################################
        experience_check = check_eligibility_of_employee_faculty(emp_id, session)
        check_is_locked = check_if_submit_unlocked(unlock_type, emp_id, session, {})
        if experience_check == "NOT ELIGIBLE":
            data['msg'] = "You are not eligible to fill this form."
            data['already_filled'] = "NOT FILLED"
            data['is_editable'] = False
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        check_is_locked =  False
        if check_is_locked == True:
            already_filled_check = check_if_already_filled_final_new(emp_id, session, level)
            if already_filled_check != False:
                already_filled_check = "FILLED"
                data['msg'] = 'You have already filled your Appraisal Form.'
            else:
                already_filled_check = "NOT FILLED"
                data['msg'] = 'Appraisal Form is Locked.'
            data['already_filled'] = already_filled_check
            data['is_editable'] = False
            is_editable = 1
        else:
            already_filled_check = check_if_already_filled_final_new(emp_id, session, level)
            print(already_filled_check)
            if already_filled_check != False:
                already_filled_check = "FILLED"
                data['msg'] = 'You have already filled your Appraisal Form.'
                approval_status = "APPROVED"
                data['is_editable'] = True
                already_filled_status = check_if_already_filled_reporting_new(emp_id,  session, level, approval_status)
                print(already_filled_status,'status')
                if already_filled_status[0]==True:
                    data['is_editable'] = False
                    is_editable = 1
            else:
                data['already_filled'] = already_filled_check
                data['is_editable'] = True
        ########################################### CHECKS END ####################################################

        if requestMethod.GET_REQUEST(request):
            if requestType.custom_request_type(request.GET, 'get_employee_data'):
                if create_intial_pending_request_new(emp_id, session, session_name) == True:
                    level = request.GET['level']
                    data['personal'] = get_emp_part_data_new(emp_id, session, {})
                    data['data'] = {}
                    data['data']['cat1'] = get_cat1_form_data_new(emp_id, level, session, session_name)
                    data['data']['cat2'] = get_cat2_form_data_new(emp_id, level, session, session_name)
                    data['data']['cat3'] = get_cat3_form_data_new(emp_id, level, session, session_name)
                    data['next_level_status'] = get_next_level_status_new(emp_id, level, session)
                    data['status'] = get_submission_status_of_emp_new(emp_id, session)
                    qry = list(FacultyAppraisal.objects.filter(emp_id=emp_id, session=session).exclude(status="DELETE").exclude(status="PENDING").values('achievement_recognition','training_needs','suggestions').order_by('-id'))
                    if len(qry)>0:    
                        data['D1'] = qry[0]['achievement_recognition']
                        data['D2'] = qry[0]['training_needs']
                        data['D3'] = qry[0]['suggestions']
                    else:
                        data['D1'] = None
                        data['D2'] = None
                        data['D3'] = None

                    roles = [319, 1371]
                    if check_is_hod_dean_new(emp_id, session, roles) == True:
                        data['is_hod_dean'] = True
                    else:
                        data['is_hod_dean'] = False
                else:
                    data = {'msg': 'Something went wrong'}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            body = json.loads(request.body)
            personal_data = body['personal']
            category_data = body['data']
            action = body['action']
            is_hod_dean = body['is_hod_dean']
            achievement_recognition = None
            training_needs = None
            suggestions = None
            if 'D1' in body:
                achievement_recognition = body['D1']
            if 'D2' in body:
                training_needs = body['D2']
            if 'D3' in body:
                suggestions = body['D3']
            level = 0
            today_date = date.today()

            #####################################
            if action == 'SAVE':
                status = "SAVED"
                form_filled_status = 'N'
                data = {'msg': 'Appraisal Form Is Saved Sucessfully.'}
            elif action == 'SUBMIT':
                status = "SUBMITTED"
                form_filled_status = 'Y'
                data = {'msg': 'Appraisal Form Is Submitted Sucessfully.'}
            #####################################
            if status == "SUBMITTED":
                if check_for_final_submit_new(category_data, is_hod_dean, level) == False:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Fields cannot be empty.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            #### UPDATE ####
            # print(category_data)
            check_for_filled = check_if_already_filled_new(emp_id, session)
            if check_for_filled[0] == True:
                last_id = check_for_filled[1]
                FacultyAppraisal.objects.filter(emp_id=emp_id, id=last_id).exclude(status="DELETE").exclude(status="PENDING").update(status="DELETE")
                if delete_row_from_tables_new(last_id, session, level, None) != True:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Something went wrong.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            ################
            ############### FOR PART-1 DATA ###############
          
            FacultyAppraisal.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=personal_data['emp_id']), dept=EmployeeDropdown.objects.get(sno=personal_data['dept']), desg=EmployeeDropdown.objects.get(sno=personal_data['desg']), highest_qualification=personal_data['h_qual'], salary_type=AccountsDropdown.objects.get(sno=personal_data['salary_type_id']), current_gross_salary=personal_data['current_gross_salary'], agp=personal_data['agp'], total_experience=personal_data['total_experience'], form_filled_status=form_filled_status, status=status, achievement_recognition=achievement_recognition, training_needs=training_needs, suggestions=suggestions, level=level, emp_date=today_date, session=AccountsSession.objects.get(id=session))
            app_id = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session).exclude(status="DELETE").exclude(status="PENDING").values_list('id', flat=True).order_by('-id')
            # PART -1 END ##################################
            if len(app_id) == 0:
                return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Something went wrong.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            fac_app_id = FacultyAppraisal.objects.get(id=app_id[0])
            data_li =[]
            for category,data_cat in category_data.items():
                print(data_cat.keys())
                if 'main_heading' in data_cat:
                    remove_main_heading = data_cat.pop("main_heading")
                for part,data_prt in data_cat.items():
                    if 'heading' in data_prt:
                        remove_heading = data_prt.pop("heading")
                    if 'cat1' in category and 'A5' in part:
                        qry5 = FacAppAcadData.objects.create(fac_app_id=fac_app_id,external_data=data_prt,score_claimed=data_prt['overall_score'])
                    else:
                        data={
                        "category":category,
                        "sub_category":part,
                        "data_sub_category":data_prt,
                        "is_editable":is_editable,
                        "score_claimed":data_prt['overall_score'],
                        }
                        data_li.append(data)
            objs =(FacAppCatWiseData(fac_app_id=fac_app_id,category=x['category'],sub_category=x['sub_category'],data_sub_category=x['data_sub_category'],score_claimed=x['score_claimed']) for x in data_li )
            qry = FacAppCatWiseData.objects.bulk_create(objs)
            if qry and qry5:
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS) 
        return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def reporting_level_form(request):
    data = {}
    session = getCurrentSession_BySessionName(request.session['Session'])
    added_by_id = request.session['hash1']
    if check_if_any_reporting_level(None, session, added_by_id) == True or checkpermission(request, [rolesCheck.ROLE_HR_REPORTS, rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        sem_type = request.session['sem_type']
        unlock_type = "INC"

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        ######## CHEKS ############
        check_is_locked = check_if_submit_unlocked(unlock_type, added_by_id, session, {})
        check_is_locked = False
        if check_is_locked == True:
            return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Appraisal Form is Locked.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        ###### CHECKS END ###################
        if requestMethod.GET_REQUEST(request):
            if requestType.custom_request_type(request.GET, 'get_employee_under_reporting'):
                emp_list,consolidated_data = get_faculty_under_reporting_new(added_by_id, session,session_name)
                data = {'data': emp_list,'consolidated_data':consolidated_data, 'max_reporting': get_maximum_reporting(emp_list)}

            elif requestType.custom_request_type(request.GET, 'get_all_desg'):
                emp_id = request.GET['emp_id']
                data = get_emp_desg(emp_id)

            elif requestType.custom_request_type(request.GET, 'get_employee_form_data_under_reporting'):
                category_data = {}
                emp_id = request.GET['e_id']
                level = request.GET['level']
                print(level,'kjhgfx')
                if emp_id == '':
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Kindly go back to previous page.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                category_data = {}
                category_data['cat1'] = get_cat1_form_data_new(emp_id, level, session, session_name)
                category_data['cat2'] = get_cat2_form_data_new(emp_id, level, session, session_name)
                category_data['cat3'] = get_cat3_form_data_new(emp_id, level, session, session_name)
                qry = list(FacultyAppraisal.objects.filter(emp_id=emp_id, session=session).exclude(status="DELETE").exclude(status="PENDING").values('achievement_recognition','training_needs','suggestions').order_by('-id'))
                if len(qry)>0:    
                    category_data['D1'] = qry[0]['achievement_recognition']
                    category_data['D2'] = qry[0]['training_needs']
                    category_data['D3'] = qry[0]['suggestions']
                else:
                    category_data['D1'] = None
                    category_data['D2'] = None
                    category_data['D3'] = None
                category_data['level'] = level
                roles = [319, 1371]
                if check_is_hod_dean_new(emp_id, session, roles) == True:
                    is_hod_dean = True
                else:
                    is_hod_dean = False
                session_date = '1-August 2019 to 31-August 2020'
                data = {'personal': get_emp_part_data_new(emp_id, session, {}), 'data': category_data, 'is_hod_dean': is_hod_dean,'recomended_data': get_recomended_data_faculty_new(emp_id, level,  session), 'remark': get_remark_faculty_new(level, emp_id, session),'session_date':session_date}
                print(data['remark'])
            elif requestType.custom_request_type(request.GET, 'review_request'):
                level = request.GET['level']
                e_id = request.GET['e_id']
                remark = None
                if 'remark' in request.GET:
                    remark = request.GET['remark']
                if int(level) <= 1:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Review request are not been requested at this level.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                if check_for_review_request_faculty_new(e_id, added_by_id, session, level) == False:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Review request can be made only once. Please contact registrar for the same.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                else:
                    FacAppRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=e_id), level=level, remark=remark, approval_status="REVIEW", added_by=EmployeePrimdetail.objects.get(emp_id=added_by_id), session=AccountsSession.objects.get(id=session))
                    get_earlier_reporting_id = FacAppRecommendationApproval.objects.filter(emp_id=e_id, level=int(level) - 1).exclude(status="DELETE").values('added_by').order_by('-id')
                    if len(get_earlier_reporting_id) > 0:
                        FacAppRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=e_id), level=int(level) - 1, remark="REQUEST FOR REVIEW", approval_status="REVIEW", added_by=EmployeePrimdetail.objects.get(emp_id=get_earlier_reporting_id[0]['added_by']), session=AccountsSession.objects.get(id=session))
                        data = {"msg": "Reviewed request is submitted successfully."}
                    else:
                        data = {"msg": "Something went wrong."}

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = {}
            body = json.loads(request.body)
            ###################### CHECKS FOR 60% ELIGIBILITY AND MAX MARKS NOT LESS THAN OBT MARKS ################
            if 'request_type' in body:  # get_increment_type #############
                emp_id = body['emp_id']
                max_marks = body['max_marks']
                marks_obt = body['marks_obt']
                if check_eligibility_at_sixty_per_marks_faculty_new(marks_obt, max_marks) == False:
                    data = {'msg': 'Marks awarded are less than the eligibility criteria for increment.', 'data': ({"increment_type": get_increment_type(), 'increment_dropdown': get_increment_dropdown(), 'promotion': get_promotion_dropdown(), 'before': get_employee_current_salary(emp_id, session)})}

                else:
                    data['data'] = ({"increment_type": get_increment_type(), 'increment_dropdown': get_increment_dropdown(), 'promotion': get_promotion_dropdown(), 'before': get_employee_current_salary(emp_id, session), 'current_gross': get_gross_salary(emp_id, session, {})['total_gross']})
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            else:
                category_data = body['data']
                personal_data = body['personal']
                remark = body['remark']
                emp_id = body['emp_id']
                level = body['level']
                # max_marks = body['max_marks']
                # marks_obt = body['marks_obt']
                is_hod_dean = body['is_hod_dean']
                print(body['remark'],'remark')
                #### FOR REMARK ####
                if 'remark' in body:
                    remark = body['remark']['data'][-1]
                else:
                    remark = None
                ####################
                ###################################

                ########### FOR APPROVAL STATUS ##################
                approval_status = get_approval_status_for_repoprting_level_faculty_new(level, emp_id, session)
                ##################################################
                if check_for_final_submit_new(category_data, is_hod_dean, level) == False:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Fields cannot be empty.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                if check_for_next_level_approval_exist_faculty_new(level, emp_id, session) == False:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Since next reporting level approved this form so you cannot edit.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                ###### FOR UPDATE #####################
                ##############################FILLED CHECK#####################################
                qry = list(FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, form_filled_status='Y').exclude(status="DELETE").exclude(status="PENDING").exclude(status="SAVED").values_list('id', flat=True).order_by('-id'))
                if len(qry) > 0:
                    if int(level) == 1:
                        if delete_row_from_tables_new(qry[0], session, level, approval_status) != True:
                            return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Something went wrong.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    FacAppRecommendationApproval.objects.filter(emp_id=emp_id, added_by=added_by_id, session=session, level=level, approval_status=approval_status).exclude(status="DELETE").update(status="DELETE")

                ############ END......#################
                last_id = list(FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, status="SUBMITTED", form_filled_status="Y").exclude(status="DELETE").values_list('id', flat=True))
                if len(last_id) > 0:
                    ######## ENTER AWARDED MARKS ########
                    if int(level) == 1:
                        fac_app_id = FacultyAppraisal.objects.get(id=last_id[-1])
                        data_li =[]
                        for category,data_cat in category_data.items():
                            if 'main_heading' in data_cat:
                                remove_main_heading = data_cat.pop("main_heading")
                            for part,data_prt in data_cat.items():
                                if 'heading' in data_prt:
                                    remove_heading = data_prt.pop("heading")
                                if 'cat1' in category and 'A5' in part:
                                    qry5 = FacAppAcadData.objects.create(fac_app_id=fac_app_id,external_data=data_prt,score_claimed=data_prt['overall_score'],score_awarded=data_prt['overall_score_awarded'])
                                else:
                                    data={
                                    "category":category,
                                    "sub_category":part,
                                    "data_sub_category":data_prt,
                                    "score_claimed":data_prt['overall_score'],
                                    "score_awarded":data_prt['overall_score_awarded']
                                    }
                                    data_li.append(data)
                        objs =(FacAppCatWiseData(fac_app_id=fac_app_id,category=x['category'],sub_category=x['sub_category'],data_sub_category=x['data_sub_category'],score_claimed=x['score_claimed'],score_awarded=x['score_awarded']) for x in data_li )
                        qry = FacAppCatWiseData.objects.bulk_create(objs)
                        
                    #####################################

                    #### ENTER RECOMMENDATION ####
                    FacAppRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), increment_type="NO INCREMENT", increment_amount=0, promoted_to=None, level=level, remark=remark, approval_status=approval_status, added_by=EmployeePrimdetail.objects.get(emp_id=added_by_id), session=AccountsSession.objects.get(id=session))
                    ##############################
                    data = {'msg': 'Appraisal Form Is Submitted Sucessfully.'}
                else:
                    data = {'msg': 'Something went wrong.'}
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
