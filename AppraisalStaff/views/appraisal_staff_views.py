
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
import json
import datetime
import operator


# '''import constants'''
from StudentMMS.constants_functions import requestType
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from AppraisalStaff.constants_functions.functions import *
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

# '''import models'''
from musterroll.models import EmployeePerdetail, Roles
from login.models import EmployeePrimdetail
from login.models import AarDropdown, EmployeeDropdown
from AppraisalStaff.models import *

from AppraisalStaff.views.appraisal_staff_function import *
from AppraisalStaff.views.appraisal_staff_checks_function import *
from Accounts.views import getCurrentSession
from aar.dept_achievement import get_all_emp
from StudentAcademics.views import get_organization, get_emp_category, get_department
from login.views import checkpermission, generate_session_table_name

# Create your views here.
# '''import views'''

def locking_unlocking_appraisal(request):
    if checkpermission(request, [211,1364]) == statusCodes.STATUS_SUCCESS:
        session = getCurrentSession(None)
        session_name = request.session['Session_name']
        sem_type = request.session['sem_type']
        Emp_id = request.session['hash1']
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                unlock_type = []
                data_values = {}
                unlock_type.append({'sno': 'INC', 'value': 'INCREMENT'})
                organization = get_organization()
                employeecategory = get_emp_category()
                data_values = {'organization': organization, 'unlock_type': unlock_type, 'employeecategory': employeecategory}
                return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

            elif requestType.custom_request_type(request.GET, 'view_previous'):
                query_view_previous = AppraisalStaffLockingUnlockingStatus.objects.filter(locking_details__session = session).exclude(status='DELETE').values('emp_id', 'emp_id__name', 'emp_id__emp_category__value', 'locking_details__lock_type', 'locking_details__unlock_from',
                                                                                                   'locking_details__unlock_to', 'locking_details__status', 'locking_details__unlocked_by__name', 'locking_details__lock_type').order_by('-locking_details__time_stamp')
                return functions.RESPONSE(list(query_view_previous), statusCodes.STATUS_SUCCESS)
            else:
                return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            print(data)
            emp_id = data['del_id']
            unlock_type = data['unlock_type']
            AppraisalStaffLockingUnlockingStatus.objects.filter(emp_id__in=emp_id, locking_details__lock_type=unlock_type,locking_details__session=session).exclude(status='DELETE').update(status='DELETE')
            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            unlock_type = data['unlock_type']
            unlock_to = datetime.strptime(
                str(data['unlock_to']), "%Y-%m-%d %H:%M:%S")
            unlock_from = datetime.strptime(
                str(data['unlock_from']), "%Y-%m-%d %H:%M:%S")
            emp_id = data['emp_id']
            length_emp_id = len(emp_id)

            AppraisalStaffLockingUnlockingStatus.objects.filter(emp_id__in=emp_id, locking_details__lock_type=unlock_type,locking_details__session=session).exclude(status='DELETE').update(status='DELETE')

            qry1 = AppraisalStaffLockingUnlocking.objects.create(session=AccountsSession.objects.get(
                Fdate__lte=unlock_from, Tdate__gte=unlock_from), lock_type=unlock_type, unlock_from=unlock_from, unlock_to=unlock_to, status='INSERT', unlocked_by=EmployeePrimdetail.objects.get(emp_id=Emp_id))

            objs = (AppraisalStaffLockingUnlockingStatus(locking_details=AppraisalStaffLockingUnlocking.objects.get(
                id=qry1.id), emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id[x]))for x in range(0, length_emp_id))
            qry2 = AppraisalStaffLockingUnlockingStatus.objects.bulk_create(
                objs)

            return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def get_components(request):
    if request.user.is_authenticated:
        data = []
        session = getCurrentSession(None)
        emp_id = request.session['hash1']
        if checkpermission(request, [rolesCheck.ROLE_HR, rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
            if requestMethod.GET_REQUEST(request):
                if requestType.custom_request_type(request.GET, 'department'):
                    org = request.GET['org']
                    department = get_department(org)
                    data = department

                elif requestType.custom_request_type(request.GET, 'employee'):
                    employee = get_employees(request.GET['dept'].split(','), request.GET['emp_category'].split(','))
                    data = list(employee)

                elif requestType.custom_request_type(request.GET, 'get_rating'):
                    rating = 5
                    data = get_rating(
                        rating)

                elif requestType.custom_request_type(request.GET, 'get_all_desg'):
                    emp_id = request.GET['emp_id']
                    data = get_emp_desg(emp_id)

                elif requestType.custom_request_type(request.GET, 'get_emp_inicial_data'):
                    data = get_emp_part_data(emp_id, session, {})

                elif requestType.custom_request_type(request.GET, 'get_employee_form_data'):
                    form_type = request.GET['form_type']
                    level = None
                    data = get_questions_in_format(
                        form_type, emp_id, session, level, {})

                elif requestType.custom_request_type(request.GET, 'get_employee_form_data_under_reporting'):
                    form_type = request.GET['form_type']
                    e_id = request.GET['e_id']
                    level = request.GET['level']
                    data = get_questions_in_format(
                        form_type, e_id, session, level, {})

                elif requestType.custom_request_type(request.GET, 'get_employee_under_reporting'):
                    form_type = request.GET['form_type']
                    data = get_employee_under_reporting(
                        emp_id, session, form_type)

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
            else:
                return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def emg_employee_end(request):
    data = {}
    session = getCurrentSession(None)
    emp_id = request.session['hash1']
    if check_for_emg_band_emp(emp_id, session) == True:

        session_name = request.session['Session_name']
        sem_type = request.session['sem_type']

        unlock_type = "INC"
        form_type = "EMG-BAND"

        ########### CHECKS ###############
        check_is_locked = check_if_submit_unlocked(unlock_type, emp_id, session, {})
        # total_exp = get_total_experience(emp_id, {})
        experience_check = check_eligibility_of_employee(emp_id, session)
        if experience_check == "NOT ELIGIBLE":
            data['msg'] = "You are not eligible to fill this form."
            data['already_filled'] = "NOT FILLED"
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        if check_is_locked == True:
            already_filled_check = check_if_already_filled(emp_id, form_type, session, {'status': "SUBMITTED"})
            if already_filled_check != False:
                already_filled_check = "FILLED"
            else:
                already_filled_check = "NOT FILLED"
            data['msg'] = 'Appraisal Form is Locked.'
            data['already_filled'] = already_filled_check
        else:
            already_filled_check = check_if_already_filled(emp_id, form_type, session, {'status': "SUBMITTED"})
            if already_filled_check != False:
                already_filled_check = "FILLED"
                data['msg'] = 'You have already filled your Appraisal Form.'
        ####### CHECKS END ###################

        if requestMethod.GET_REQUEST(request):
            if requestType.custom_request_type(request.GET, 'get_employee_form_data'):
                level = 0
                if insert_first_pending_request(emp_id, form_type, session) == True:
                    data['personal'] = get_emp_part_data(emp_id, session, {})
                    data['question_data'] = get_questions_in_format(form_type, emp_id, session, level, {})
                    # data.update({"status": get_employee_status_for_form(emp_id, form_type, session)})
                    data.update({"status": get_submission_status_of_emp_form(emp_id, form_type, session, {})})
                    if check_if_pending_at_next_level(level, form_type, session, emp_id) == False:
                        data.update({"next_level_status": 'PENDING'})
                    else:
                        data.update({"next_level_status": get_next_level_status(form_type, emp_id, level, session)})
                else:
                    data = {'msg': 'Something went wrong'}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            body = json.loads(request.body)
            form_type = "EMG-BAND"

            ###### FOR UPDATE #####################
            already_filled = check_if_already_filled(emp_id, form_type, session, {})
            if already_filled != False:
                already_filled_id = list(already_filled)
            else:
                already_filled_id = None
            if already_filled_id != None:
                # for ids in already_filled_id:
                #     AppraisalStaffApplication.objects.filter(id=ids).exclude(status="DELETE").exclude(status="PENDING").update(status="DELETE")
                #     AppraisalStaffAnswer.objects.filter(application=ids).exclude(status="DELETE").update(status="DELETE")
                AppraisalStaffApplication.objects.filter(id__in=already_filled_id,session=session).exclude(status="DELETE").exclude(status="PENDING").update(status="DELETE")
                AppraisalStaffAnswer.objects.filter(application__in=already_filled_id,ques_id__session=session).exclude(status="DELETE").update(status="DELETE")

            ############ END......#################
            question = []
            for part in body['question']:
                if part == "PART-2":
                    for activity in body['question'][part]['type_of_act']:
                        question.append({'ques_id': body['question'][part]['ques_id'], 'answer': activity, 'marks_obtained': None})
                    continue
                for sub_part in body['question'][part]:
                    if len(sub_part['sub_category']) == 0:
                        if sub_part['answer'] != None:
                            if len(sub_part['answer']) == 0:
                                sub_part['answer'] = None
                            else:
                                sub_part['answer'] = sub_part['answer'][0]
                        if sub_part['marks_obtained'] != None:
                            if len(sub_part['marks_obtained']) == 0:
                                sub_part['marks_obtained'] = None
                            else:
                                sub_part['marks_obtained'] = sub_part['marks_obtained'][0]
                        question.append({'ques_id': sub_part['ques_id'], 'answer': sub_part['answer'], 'marks_obtained': sub_part['marks_obtained']})
                    else:
                        for sub_category in sub_part['sub_category']:
                            if sub_category['answer'] != None:
                                if len(sub_category['answer']) == 0:
                                    sub_category['answer'] = None
                                else:
                                    sub_category['answer'] = sub_category['answer'][0]
                            if sub_category['marks_obtained'] != None:
                                if len(sub_category['marks_obtained']) == 0:
                                    sub_category['marks_obtained'] = None
                                else:
                                    sub_category['marks_obtained'] = sub_category['marks_obtained'][0]
                            question.append({'ques_id': sub_category['ques_id'], 'answer': sub_category['answer'], 'marks_obtained': sub_category['marks_obtained']})
            #######################################
            if body['action'] == 'SAVE':
                status = "SAVED"
                data = {'msg': 'Appraisal Form Is Saved Sucessfully.'}
            elif body['action'] == 'SUBMIT':
                status = "SUBMITTED"
                data = {'msg': 'Appraisal Form Is Submitted Sucessfully.'}
            AppraisalStaffApplication.objects.create(form_type=form_type, emp_id=EmployeePrimdetail.objects.get(
                emp_id=emp_id), session=AccountsSession.objects.get(id=session))
            application_id = list(AppraisalStaffApplication.objects.filter(
                emp_id=emp_id, form_type=form_type,session=session).exclude(status="DELETE").values_list('id', flat=True).order_by('-id'))
            if len(application_id) > 0:
                if status == "SUBMITTED":
                    if check_for_final_submit(question, {}) != True:
                        return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Fields cannot be left empty.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                for q in question:
                    print(q)
                objs = (AppraisalStaffAnswer(application=AppraisalStaffApplication.objects.get(id=application_id[0]), ques_id=AppraisalStaffQuestion.objects.get(ques_id=q['ques_id']), marks_obtained=q['marks_obtained'], answer=q['answer'], status=status, level=0) for q in question)
                AppraisalStaffAnswer.objects.bulk_create(objs)
            else:
                data = {'msg': 'Something went wrong'}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def reporting_form_all_band(request):
    data = []
    form_type = 'S-BAND'
    session = getCurrentSession(None)
    added_by_id = request.session['hash1']
    ##########################CHANGED####################################
    if ((check_if_any_reporting_level(form_type, session, added_by_id) == True) or checkpermission(request, [rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS):
        ##########################CHANGED####################################
        session_name = request.session['Session_name']
        sem_type = request.session['sem_type']

        unlock_type = "INC"
        ########### CHECKS ###############
        check_is_locked = check_if_submit_unlocked(unlock_type, added_by_id, session, {})
        if check_is_locked == True:
            return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Appraisal Form is Locked.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        ####### CHECKS END ###################
        if requestMethod.GET_REQUEST(request):
            if requestType.custom_request_type(request.GET, 'get_employee_under_reporting'):
                form_type = request.GET['form_type']
                function_data = get_employee_under_reporting(
                    added_by_id, session, form_type)
                emp_list = function_data[0]
                consolidate_data = function_data[1]
                data = {'data': emp_list, 'max_reporting': get_maximum_reporting(emp_list), 'consolidate_data': consolidate_data}

            elif requestType.custom_request_type(request.GET, 'get_employee_form_data_under_reporting'):
                e_id = request.GET['e_id']
                if e_id == '':
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Kindly go back to previous page.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                level = request.GET['level']
                form_type = request.GET['form_type']
                question_data = get_questions_in_format(
                    form_type, e_id, session, level, {})
                if form_type == "S-BAND":
                    ################ LOCKING/UNLOCKING CHECK FOR S-BAND ###############
                    check_is_locked = check_if_submit_unlocked(unlock_type, e_id, session, {})
                    if check_is_locked == True:
                        return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Appraisal Form is Locked.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    experience_check = check_eligibility_of_employee(e_id, session)
                    if experience_check == "NOT ELIGIBLE":
                        return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Employee is not eligible for this form.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                        # data['msg'] = "Employee is not eligible to fill thia form."
                        # data['already_filled'] = "NOT FILLED"
                        # return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
                    ###################################################################
                    if insert_first_pending_request(e_id, form_type, session) == True:
                        is_already_filled = check_if_already_filled(e_id, form_type, session, {})
                        if is_already_filled != False:
                            is_already_filled = True
                        data = {'personal': get_emp_part_data(e_id, session, {}), 'question_data': question_data, 'recomended_data': get_recomended_data(e_id, level, form_type, session, {}), 'remark': get_remark(form_type, level, e_id, session), 'is_already_filled': is_already_filled}

                    else:
                        data = {'msg': 'Something went wrong'}
                else:
                    data = {'personal': get_emp_part_data(e_id, session, {}), 'question_data': question_data, 'recomended_data': get_recomended_data(e_id, level, form_type, session, {}), 'remark': get_remark(form_type, level, e_id, session)}

            elif requestType.custom_request_type(request.GET, 'get_increment'):
                increment_type = request.GET['increment_type']
                emp_id = request.GET['emp_id']
                salary_type = request.GET['salary_type']
                if 'amount' in request.GET:
                    amount = request.GET['amount']
                    if amount == None:
                        amount = 0
                else:
                    amount = 0
                data = get_increment_in_salary(increment_type, emp_id, session, salary_type, amount)

            elif requestType.custom_request_type(request.GET, 'review_request'):
                level = request.GET['level']
                form_type = request.GET['form_type']
                e_id = request.GET['e_id']
                if int(level) <= 1:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Review request are not been requested at this level.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                if check_for_review_request(e_id, added_by_id, session, level) == False:
                    return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Review request can be made only once. Please contact registrar for the same.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                else:
                    AppraisalStaffRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=e_id), level=level, remark="Review", approval_status="REVIEW", added_by=EmployeePrimdetail.objects.get(emp_id=added_by_id), session=AccountsSession.objects.get(id=session))
                    get_earlier_reporting_id = AppraisalStaffRecommendationApproval.objects.filter(emp_id=e_id, level=1,session=session).values('added_by').order_by('-id')
                    if len(get_earlier_reporting_id) > 0:
                        AppraisalStaffRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=e_id), level=int(level) - 1, remark="Request for review", approval_status="REVIEW", added_by=EmployeePrimdetail.objects.get(emp_id=get_earlier_reporting_id[0]['added_by']), session=AccountsSession.objects.get(id=session))
                        data = {"msg": "Reviewed request is submitted successfully."}
                    else:
                        data = {"msg": "Something went wrong."}

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = {}
            body = json.loads(request.body)
            ###################### CHECKS FOR 60% ELIGIBILITY AND MAX MARKS NOT LESS THAN OBT MARKS ################
            if 'request_type' in body:  # get_increment_type #############
                question = body['question']
                form_type = body['form_type']
                index = body['index']
                emp_id = body['emp_id']
                max_marks = {}
                for part in list(question.keys()):
                    max_marks[part] = get_max_marks_of_form_part(form_type, part,session)
                if check_for_obt_marks_less_than_max_marks(form_type, question, index) == False:
                    data = {'msg': 'Obtained marks cannot be greater than maximum marks.', 'data': ({"increment_type": get_increment_type(), 'increment_dropdown': get_increment_dropdown(), 'promotion': get_promotion_dropdown(), 'employee_current_salary': get_employee_current_salary(emp_id, session)})}
                if check_eligibility_at_sixty_per_marks(form_type, question, max_marks, index) == False:
                    data = {'msg': 'Marks for this part are less than the eligibility criteria for increment.', 'data': ({"increment_type": get_increment_type(), 'increment_dropdown': get_increment_dropdown(), 'promotion': get_promotion_dropdown(), 'before': get_employee_current_salary(emp_id, session)})}

                else:
                    data['data'] = ({"increment_type": get_increment_type(), 'increment_dropdown': get_increment_dropdown(), 'promotion': get_promotion_dropdown(), 'before': get_employee_current_salary(emp_id, session), 'current_gross': get_gross_salary(emp_id, session, {})['total_gross']})
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            #########################################################################################################
            else:
                emp_id = body['emp_id']
                level = body['level']
                index = body['index']
                if 'remark' in body:
                    remark = body['remark']['data'][-1]
                else:
                    remark = None
                form_type = body['form_type']
                data_question = body['question']
                ########### FOR APPROVAL STATUS ##################
                approval_status = get_approval_status_for_repoprting_level(level, emp_id, session)
                ##################################################

                ###### FOR UPDATE #####################
                already_filled = check_if_already_filled(emp_id, form_type, session, {})
                if already_filled != False:
                    already_filled_id = list(already_filled)
                else:
                    already_filled_id = None
                if already_filled_id != None:
                    # for ids in already_filled_id:
                        # AppraisalStaffApplication.objects.filter(id=already_filled_id).exclude(status="DELETE").update(status="DELETE")
                    AppraisalStaffAnswer.objects.filter(application__in=already_filled_id, level=level, status=approval_status,ques_id__session=session).exclude(status="DELETE").update(status="DELETE")
                    AppraisalStaffRecommendationApproval.objects.filter(emp_id=emp_id, added_by=added_by_id, session=session, approval_status=approval_status).exclude(status="DELETE").update(status="DELETE")

                ############ END......#################
                question = []
                check_parts = check_form_part_for_first_reporting(form_type, level)
                for part in data_question:
                    if part in check_parts:
                        if part == "PART-5" and form_type == "EMG-BAND":
                            for category in data_question[part]['data']:
                                if category['answer'] != None and len(category['answer']) > int(index):
                                    for activity in category['answer'][index]:
                                        question.append({'ques_id': category['ques_id'], 'answer': activity, 'marks_obtained': None})
                            continue
                        if form_type == "S-BAND" and part == "PART-2" or form_type == "A-BAND" and part == "PART-3":
                            for category in data_question[part]['data']:
                                if category['marks_obtained'] != None and len(category['marks_obtained']) > int(index):
                                    question.append({'ques_id': category['ques_id'], 'answer': None, 'marks_obtained': category['marks_obtained'][index]})
                            continue
                        for sub_part in data_question[part]['data']:
                            if len(sub_part['sub_category']) == 0:
                                if sub_part['answer'] != None:
                                    if len(sub_part['answer']) == 0:
                                        answer = None
                                    else:
                                        answer = sub_part['answer'][index]
                                if sub_part['marks_obtained'] != None:
                                    if len(sub_part['marks_obtained']) == 0:
                                        marks_obtained = None
                                    else:
                                        marks_obtained = sub_part['marks_obtained'][index]
                                question.append({'ques_id': sub_part['ques_id'], 'answer': answer, 'marks_obtained': marks_obtained})
                            else:
                                for sub_category in sub_part['sub_category']:
                                    if sub_category['answer'] != None:
                                        if len(sub_category['answer']) == 0:
                                            answer = None
                                        else:
                                            answer = sub_category['answer'][index]
                                    if sub_category['marks_obtained'] != None:
                                        if len(sub_category['marks_obtained']) == 0:
                                            marks_obtained = None
                                        else:
                                            marks_obtained = sub_category['marks_obtained'][index]
                                    question.append({'ques_id': sub_category['ques_id'], 'answer': answer, 'marks_obtained': marks_obtained})

                #######################################
                ########## FOR RECOMMENTATION ###############################
                increment_type = body['increment_type']
                if 'increment_amount' in body:
                    if body['increment_amount'] != None:
                        increment_amount = body['increment_amount']
                    else:
                        increment_amount = body['increment_amount']
                # if increment_type == 'SPECIAL' or increment_type == 'PROMOTION WITH SPECIAL INCREAMENT':
                #     increment_amount = body['increment_amount']
                # else:
                #     increment_amount = 0
                if increment_type == 'PROMOTION WITH SPECIAL INCREAMENT' or increment_type == 'PROMOTION WITHOUT INCREAMENT':
                    promoted_to = EmployeeDropdown.objects.get(sno=body['promoted_to'])
                else:
                    promoted_to = None
                #############################################################

                if check_if_already_filled(emp_id, form_type, session, {}) == False:
                    AppraisalStaffApplication.objects.create(form_type=form_type, emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), session=AccountsSession.objects.get(id=session))
                application_id = list(AppraisalStaffApplication.objects.filter(emp_id=emp_id, form_type=form_type,session=session).exclude(status="DELETE").values_list('id', flat=True).order_by('-id'))

                if len(application_id) > 0:
                    if increment_type != "NO INCREMENT":
                        ########## CHECK FOR 60% ELIGIBILITY ##########################
                        max_marks = {}
                        for part in list(data_question.keys()):
                            if form_type == "EMG-BAND" and part == "PART-4" or form_type == "S-BAND" and part == "PART-2" or form_type == "A-BAND" and part == "PART-3":
                                max_marks[part] = get_max_marks_of_form_part(form_type, part,session)
                        if check_for_obt_marks_less_than_max_marks(form_type, body['question'], index) == False:
                            data = {"msg": "Obtained marks cannot be greater than maximum marks."}
                            return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                        if check_eligibility_at_sixty_per_marks(form_type, body['question'], max_marks, index) == False:
                            data = {"msg": "Marks for this part are less than the eligibility criteria for increment."}
                            return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                        ###############################################################
                    if check_for_final_submit(question, {}) != True:
                        return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Fields cannot be left empty.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                    if check_for_next_level_approval_exist(level, emp_id, session) == False:
                        return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Since next reporting level approved this form so you cannot edit.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    objs = (AppraisalStaffAnswer(application=AppraisalStaffApplication.objects.get(id=application_id[0]), ques_id=AppraisalStaffQuestion.objects.get(ques_id=q['ques_id']), marks_obtained=q['marks_obtained'], answer=q['answer'], level=level, status=approval_status) for q in question)
                    AppraisalStaffAnswer.objects.bulk_create(objs)
                    AppraisalStaffRecommendationApproval.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), increment_type=increment_type, increment_amount=increment_amount, promoted_to=promoted_to, level=level, remark=remark, approval_status=approval_status, added_by=EmployeePrimdetail.objects.get(emp_id=added_by_id), session=AccountsSession.objects.get(id=session))
                    data = {'msg': 'Appraisal Form Is Submitted Sucessfully.'}
                else:
                    data = {'msg': 'Something went wrong'}
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def a_employee_end(request):
    data = {}
    session = getCurrentSession(None)
    emp_id = request.session['hash1']
    form_type = "A-BAND"
    if check_for_a_band_emp(emp_id, session) == True:

        session_name = request.session['Session_name']
        sem_type = request.session['sem_type']

        unlock_type = "INC"
        ########### CHECKS ###############
        check_is_locked = check_if_submit_unlocked(unlock_type, emp_id, session, {})
        # total_exp = get_total_experience(emp_id, {})
        experience_check = check_eligibility_of_employee(emp_id, session)
        if experience_check == "NOT ELIGIBLE":
            data['msg'] = "You are not eligible to fill this form."
            data['already_filled'] = "NOT FILLED"
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        if check_is_locked == True:
            already_filled_check = check_if_already_filled(emp_id, form_type, session, {'status': "SUBMITTED"})
            if already_filled_check != False:
                already_filled_check = "FILLED"
            else:
                already_filled_check = "NOT FILLED"
            data['msg'] = 'Appraisal Form is Locked.'
            data['already_filled'] = already_filled_check
        else:
            already_filled_check = check_if_already_filled(emp_id, form_type, session, {'status': "SUBMITTED"})
            if already_filled_check != False:
                already_filled_check = "FILLED"
                data['msg'] = 'You have already filled your Appraisal Form.'
        ####### CHECKS END ###################

        if requestMethod.GET_REQUEST(request):
            if requestType.custom_request_type(request.GET, 'get_employee_form_data'):
                form_type = "A-BAND"
                level = 0
                if insert_first_pending_request(emp_id, form_type, session) == True:
                    data['personal'] = get_emp_part_data(emp_id, session, {})
                    data['question_data'] = get_questions_in_format(
                        form_type, emp_id, session, level, {})
                    # data.update({"status": get_employee_status_for_form(emp_id, form_type, session)})
                    data.update({"status": get_submission_status_of_emp_form(emp_id, form_type, session, {})})
                    if check_if_pending_at_next_level(level, form_type, session, emp_id) == False:
                        data.update({"next_level_status": 'PENDING'})
                    else:
                        data.update({"next_level_status": get_next_level_status(form_type, emp_id, level, session)})
                else:
                    data = {'msg': 'Something went wrong'}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            body = json.loads(request.body)
            form_type = "A-BAND"

            ###### FOR UPDATE #####################
            already_filled = check_if_already_filled(emp_id, form_type, session, {})
            if already_filled != False:
                already_filled_id = list(already_filled)
            else:
                already_filled_id = None
            if already_filled_id != None:
                # for ids in already_filled_id:
                #     AppraisalStaffApplication.objects.filter(id=ids).exclude(status="DELETE").exclude(status="PENDING").update(status="DELETE")
                #     AppraisalStaffAnswer.objects.filter(application=ids).exclude(status="DELETE").update(status="DELETE")
                AppraisalStaffApplication.objects.filter(id__in=already_filled_id,session=session).exclude(status="DELETE").exclude(status="PENDING").update(status="DELETE")
                AppraisalStaffAnswer.objects.filter(application__in=already_filled_id,ques_id__session=session).exclude(status="DELETE").update(status="DELETE")

            ############ END......#################
            question = []
            for part in body['question']:
                for sub_part in body['question'][part]:
                    if len(sub_part['sub_category']) == 0:
                        if sub_part['answer'] != None:
                            if len(sub_part['answer']) == 0:
                                answer = None
                            else:
                                answer = sub_part['answer'][0]
                        if sub_part['marks_obtained'] != None:
                            if len(sub_part['marks_obtained']) == 0:
                                marks_obtained = None
                            else:
                                marks_obtained = sub_part['marks_obtained'][0]
                        question.append({'ques_id': sub_part['ques_id'], 'answer': answer, 'marks_obtained': marks_obtained})
                    else:
                        for sub_category in sub_part['sub_category']:
                            if sub_category['answer'] != None:
                                if len(sub_category['answer']) == 0:
                                    answer = None
                                else:
                                    answer = sub_category['answer'][0]
                            if sub_category['marks_obtained'] != None:
                                if len(sub_category['marks_obtained']) == 0:
                                    marks_obtained = None
                                else:
                                    marks_obtained = sub_category['marks_obtained'][0]
                            question.append({'ques_id': sub_category['ques_id'], 'answer': answer, 'marks_obtained': marks_obtained})

            #######################################
            if body['action'] == 'SAVE':
                status = "SAVED"
                data = {'msg': 'Appraisal Form Is Saved Sucessfully.'}
            elif body['action'] == 'SUBMIT':
                status = "SUBMITTED"
                data = {'msg': 'Appraisal Form Is Submitted Sucessfully.'}
            AppraisalStaffApplication.objects.create(form_type=form_type, emp_id=EmployeePrimdetail.objects.get(
                emp_id=emp_id), session=AccountsSession.objects.get(id=session))
            application_id = list(AppraisalStaffApplication.objects.filter(
                emp_id=emp_id, form_type=form_type,session=session).exclude(status="DELETE").values_list('id', flat=True).order_by('-id'))
            if len(application_id) > 0:
                if status == "SUBMITTED":
                    if check_for_final_submit(question, {}) != True:
                        return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Fields cannot be left empty.'), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                objs = (AppraisalStaffAnswer(application=AppraisalStaffApplication.objects.get(id=application_id[0]), ques_id=AppraisalStaffQuestion.objects.get(ques_id=q['ques_id']), marks_obtained=q['marks_obtained'], answer=q['answer'], status=status, level=0) for q in question)
                AppraisalStaffAnswer.objects.bulk_create(objs)
            else:
                data = {'msg': 'Something went wrong'}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def appraisal_consolidate_report(request):
    data = []
    if request.user.is_authenticated:
        session = getCurrentSession(None)
        emp_id = request.session['hash1']
        if checkpermission(request, [rolesCheck.ROLE_HR_REPORTS, rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS:
            if requestMethod.GET_REQUEST(request):
                if requestType.custom_request_type(request.GET, 'form_data'):
                    all_band = ['A-BAND', 'EMG-BAND', 'S-BAND']
                    heading = ['NOT FILLED', 'FILLED', 'TOTAL APPROVED', 'TOTAL EMPLOYEE', 'NOT FILLED', 'FILLED', 'TOTAL APPROVED', 'TOTAL EMPLOYEE', 'NOT FILLED', 'FILLED', 'TOTAL APPROVED', 'TOTAL EMPLOYEE']
                    department = list(EmployeePrimdetail.objects.exclude(dept__isnull=True).values('dept', 'dept__value').order_by('dept__value').distinct())
                    dept_data = {}
                    band = {}
                    band['dept_data'] = {}
                    band['band_data'] = []
                    band['band_data'].append({'data': {}})
                    for b in all_band:

                        ######### FOR LADDRE-CADRE ###########
                        cadre = []
                        cadre__value = str(str(b).split('-')[0])
                        for c in cadre__value:
                            cadre.append(c)
                        ladder = []
                        new_list = []
                        for c in cadre:
                            new_list = get_ladder_acc_to_cadre(c)
                            ladder.extend(new_list)
                        ######################################
                        band_employee = EmployeePrimdetail.objects.filter(ladder__value__in=ladder).exclude(emp_id='00007').exclude(emp_status="SEPARATE").values('emp_id', 'dept', 'dept__value', 'desg', 'desg__value').distinct()
                        function_data = get_detpwise_consolidate_data(department, ladder, session, b, dept_data)
                        dept_data = function_data[0]  # dept data
                        band_data = function_data[1]  # band data
                        band['band_data'][0]['data'].update(band_data)
                    final_data = []
                    for d in dept_data:
                        dept = {}
                        dept['data'] = dept_data[d]
                        dept['name'] = d
                        final_data.append(dept)
                    band['dept_data'] = final_data
                    data.append(band)
                    data = {'heading': heading, 'data': data}

                elif requestType.custom_request_type(request.GET, 'get_employee_data'):
                    band = request.GET['band']
                    ######### FOR LADDRE-CADRE ###########
                    cadre = []
                    cadre__value = str(str(band).split('-')[0])
                    for c in cadre__value:
                        cadre.append(c)
                    ladder = []
                    new_list = []
                    for c in cadre:
                        new_list = get_ladder_acc_to_cadre(c)
                        ladder.extend(new_list)
                    ######################################
                    band_employee = EmployeePrimdetail.objects.filter(ladder__value__in=ladder).exclude(emp_id='00007').exclude(emp_category__value="FACULTY").exclude(emp_status="SEPARATE").values('emp_id', 'dept', 'dept__value', 'desg', 'desg__value').distinct()
                    emp_data = []
                    max_reporting = get_max_reporting_of_all_employee(band_employee)
                    for emp in band_employee:
                        data1 = {}
                        data1 = get_emp_part_data(emp['emp_id'], session, {})

                        get_training_sugg_data = get_training_suggestion_of_emp_form(emp['emp_id'], band, session)
                        for k, v in get_training_sugg_data.items():
                            data1[k] = v
                        # increment_data = get_level_wise_propose_increment(emp_id, max_reporting, session)

                        # for k, v in increment_data.items():
                        #     data1[k] = v
                        level_status = get_statuses_at_reporting_level_of_emp(emp['emp_id'], session)

                        level_1_status = "PENDING"
                        for i in range(1, len(level_status) + 1):
                            data1['level_' + str(i) + 'status'] = level_status[i - 1]['status']
                            if i == 1:
                                level_1_status = level_status[i - 1]['status']
                            proposed_data = get_proposed_increment(emp['emp_id'], i, session)
                            data1['level_' + str(i) + 'increment_type'] = proposed_data['increment_type']
                            data1['level_' + str(i) + 'increment_amount'] = proposed_data['increment_amount']
                            data1['level_' + str(i) + 'promoted_to'] = proposed_data['promoted_to']
                            data1['level_' + str(i) + 'estimated_gross_salary'] = proposed_data['estimated_gross_salary']

                        data1['HOD MARKS'] = get_first_reporting_total_marks(emp['emp_id'], band, level_1_status, 1, session, {})
                        data1['emp_status'] = get_submission_status_of_emp_form(emp['emp_id'], band, session, {})
                        level_status = get_statuses_at_reporting_level_of_emp(emp['emp_id'], session)
                        last_level = len(level_status)
                        data1['reporting_level'] = last_level
                        remarks = get_remark(band, last_level, emp['emp_id'], session)
                        if len(remarks) != 0:
                            for x in range(0, len(remarks['data'])):
                                remark_key = "level_" + str(x + 1) + '_remark'
                                data1[remark_key] = remarks['data'][x]
                        recommend_data = get_recomended_data_without_review(emp['emp_id'], last_level, band, session)
                        # for x in range(0, len(recommend_data['data'])):
                        #     data1["level_" + str(x + 1) + '_recommend'] = recommend_data['data'][x]
                        if data1['emp_status']=='FILLED':
                            data1['show_print_button'] = True
                        else:
                            data1['show_print_button'] = False
                        emp_data.append(data1)
                    data = {'band': band, 'band_data': emp_data, 'max_reporting': '3'}  # STATIC
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
            else:
                return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
