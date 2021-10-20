from django.shortcuts import render

import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from login.views import generate_session_table_name
from django.http import HttpResponse, JsonResponse
from itertools import groupby
import math
from datetime import datetime
from Registrar.models import *
from django.db.models import Count, Avg
from django.db.models import Sum, F

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from erp.constants_functions.functions import *

from musterroll.models import EmployeePrimdetail
from StudentAccounts.models import SubmitFee, RefundFee
from StudentFeedback.models import *
from StudentAcademics.models import *
from Registrar.models import StudentSemester, StudentDropdown, Sections, CourseDetail

from StudentAcademics.views import get_course, get_subject_type, get_gender, check_islocked, get_att_group_section_students, get_sub_attendance_type, get_student_subjects, get_attendance_type, get_student_attendance, get_semester, get_section, get_section_students


''' #CHECK IF PORTAL IS LOCKED# '''


def check_is_portal_locked(section_id, session_name):
    LockingUnlocking = generate_session_table_name("LockingUnlocking_", session_name)

    now = datetime.now()

    qry_check = LockingUnlocking.objects.filter(section=section_id, unlock_to__gte=now, unlock_from__lte=now, lock_type='F').values('time_stamp').order_by('-id')[:1]

    if len(qry_check) > 0:
        return {'locked': False, 'time_stamp': qry_check[0]['time_stamp']}
    else:
        ########## if portal is locked, get largest unlock to date ###########################
        qry_check = LockingUnlocking.objects.filter(section=section_id, lock_type='F').values('time_stamp').order_by('-unlock_to')[:1]
        if len(qry_check) > 0:
            return {'locked': True, 'time_stamp': qry_check[0]['time_stamp']}
        else:
            return {'locked': True, 'time_stamp': now}

''' #GET ALL ATTRIBUTE of SINGLE SUBJECT TYPE AND SEMESTER AND PERCENTAGE# '''


def get_attribute(sub_type, sem, session_name):
    StuFeedbackAttributes = generate_session_table_name("StuFeedbackAttributes_", session_name)
    none_flag = False
    if sub_type == "ALL":
        sub_type = list(types['sno'] for types in get_subject_type())
        none_flag = True
    if None in sub_type:
        sub_type.remove(None)
        none_flag = True
    result = list(StuFeedbackAttributes.objects.filter(eligible_settings_id__sem=sem, subject_type__in=sub_type).values('id', 'name', 'residential_status', 'gender', 'gender__value', 'min_marks', 'max_marks').distinct())
    if none_flag:
        none_list = list(StuFeedbackAttributes.objects.filter(eligible_settings_id__sem=sem, subject_type__isnull=True).values('id', 'name', 'residential_status', 'gender', 'gender__value', 'min_marks', 'max_marks').distinct())
        for x in none_list:
            result.append(x)
    return result


def for_feedback_get_student_attendance(request, uniq_id, to_date, session_name, session_id):
    result = {}
    studentSession = generate_session_table_name("studentSession_", session_name)
    StuFeedbackEligibility = generate_session_table_name("StuFeedbackEligibility_", session_name)

    result['q_att_date'] = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
    result['att_type'] = get_attendance_type(session_id)
    result['att_sub_type'] = get_sub_attendance_type(session_id)
    att_type_li = [t['id'] for t in result['att_type']]
    att_sub_type_li = [t['sno'] for t in result['att_sub_type']]
    get_Sem_timing = Semtiming.objects.filter(uid=request.session['Session_id']).values()
    from_date = get_Sem_timing[0]['sem_start']
    result['sem_id'] = result['q_att_date'][0]['section__sem_id']
    result['subjects'] = get_student_subjects(result['q_att_date'][0]['section__sem_id'], session_name)
    result['att_data'] = get_student_attendance(uniq_id, max(from_date, result['q_att_date'][0]['att_start_date']), to_date, request.session['Session_id'], att_sub_type_li, result['subjects'], 1, [], session_name)
    result['eligible_percent'] = list(StuFeedbackEligibility.objects.filter(sem=result['sem_id']).exclude(status__contains="DELETE").values('eligible_att_per'))
    if len(result['eligible_percent']) == 0:
        result['eligible_percent'].append({'eligible_att_per': 0})

    result['total_present'] = result['att_data']['present_count']
    result['total_total'] = result['att_data']['total']

    if result['total_total'] > 0:
        result['current_percent'] = round(float(result['total_present']) * 100 / int(result['total_total']))
    else:
        result['current_percent'] = 0
    if len(result['eligible_percent']) > 0:
        result['eligible_percentage'] = result['eligible_percent'][0]['eligible_att_per']
    else:
        result['eligible_percentage'] = "--"
    return result

''' #GET COMPLETE STATUS OF STUDENT# '''


def studentDetailNstatus(request, uniq_id, att_to_date, session_name, session_id):
    data = {}
    StuFeedbackMarks = generate_session_table_name("StuFeedbackMarks_", session_name)
    studentSession = generate_session_table_name("studentSession_", session_name)
    StuFeedback = generate_session_table_name("StuFeedback_", session_name)

    # #######################LOCKING STARTS######################
    # section_li=list(studentSession.objects.filter(uniq_id=uniq_id).values_list('section'))
    # if check_islocked("F",section_li,session_name):
    #   return RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
    #   #######################LOCKING ENDS######################

    check_given = StuFeedbackMarks.objects.filter(feedback_id__feedback_id__uniq_id=uniq_id, feedback_id__feedback_id__status='INSERT', attribute__eligible_settings_id__status="INSERT", feedback_id__feedback_id__locked="Y").values()

    if len(check_given) > 0:
        data['status'] = "ALREADY_FILLED"
    else:
        ####################### GET STUDENT ATTENDANCE ###############
        temp_attendence_detail = for_feedback_get_student_attendance(request, uniq_id, att_to_date, session_name, session_id)
        for key in temp_attendence_detail:
            data[key] = temp_attendence_detail[key]
        ################## CHECK IF NOT ELIGIBLE #######################

        if data['current_percent'] < data['eligible_percent'][0]['eligible_att_per']:
            log_record = StuFeedback.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), status='DELETE', attendance_per=data['current_percent'], locked="N")
            data['status'] = "NOT_ELIGIBLE"

        else:
            data['status'] = "NOT_FILLED"
    return data

''' #CHECK RESIDENCY OF STUDENT# '''


def student_residency(request, uniq_id):
    # CHANGE SESSION
    session = Semtiming.objects.filter(uid=request.session['Session_id']).values_list("session", flat=True)
    session_id = Semtiming.objects.filter(session=session[0], sem_type="odd").values_list("uid", flat=True)

    check_resident = SubmitFee.objects.filter(cancelled_status='N', uniq_id=uniq_id, status="INSERT", fee_rec_no__contains='H', session=session_id[0]).exclude(id__in=RefundFee.objects.values_list('fee_id', flat=True)).exclude(status__contains="DELETE").values('due_fee_id')
    if len(check_resident) > 0:
        res_status = 'H'
    else:
        res_status = 'D'
    return res_status

''' #GET SECTION FOR MULTI DEPARTMENT SEMESTER SECTION SELECTED# '''


def getSection(branch, sem, sec):
    result = list(Sections.objects.filter(section__in=sec, sem_id__sem__in=sem, dept__in=branch))
    return result


def faculty_feedback_details(faculty_id_list, session_name, subject_type):
    data_value = []
    StuFeedbackMarks = generate_session_table_name("StuFeedbackMarks_", session_name)
    StuFeedbackAttributes = generate_session_table_name("StuFeedbackAttributes_", session_name)
    GroupSection = generate_session_table_name("GroupSection_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
    data_set = []
    data_set = list(StuFeedbackMarks.objects.filter(feedback_id__emp_id__in=faculty_id_list, attribute__subject_type__in=subject_type, feedback_id__feedback_id__status="INSERT", attribute__eligible_settings_id__status="INSERT")
                    .exclude(attribute__subject_type__isnull=True).exclude(attribute__eligible_settings_id__status="DELETE")
                    .values(
                    "feedback_id__feedback_id__uniq_id",
                    "feedback_id__feedback_id__uniq_id__section__dept__course__value",
                    "feedback_id__feedback_id__uniq_id__section__dept__dept__value",
                    "feedback_id__feedback_id__uniq_id__section__sem_id__sem",
                    "feedback_id__feedback_id__uniq_id__section__section",
                    "feedback_id__feedback_id__uniq_id__section",
                    "feedback_id__feedback_id__attendance_per",
                    "feedback_id__subject",
                    "feedback_id__subject__sub_alpha_code",
                    "feedback_id__subject__sub_num_code",
                    "feedback_id__subject__sub_name",
                    "feedback_id__emp_id__name",
                    "feedback_id__emp_id__desg__value",
                    "feedback_id__emp_id__dept__value",
                    "feedback_id__emp_id__email",
                    "feedback_id__emp_id__mob",
                    "feedback_id__emp_id__current_pos__value",
                    "feedback_id__emp_id",
                    "attribute__name",
                    "attribute__eligible_settings_id__sem",
                    "attribute__eligible_settings_id__sem__sem",
                    "attribute__min_marks",
                    "attribute__max_marks",
                    "attribute__gender__value",
                    "attribute__subject_type__value",
                    "marks"
                    )
                    .annotate(cal_marks=(F("marks")) * 10 / (F("attribute__max_marks"))
                              )
                    .order_by(
                    "feedback_id__feedback_id__uniq_id__section__dept__course__value",
                    "feedback_id__feedback_id__uniq_id__section__dept__dept__value",
                    "feedback_id__feedback_id__uniq_id__section__sem_id__sem",
                    "feedback_id__feedback_id__uniq_id__section__section",
                    "feedback_id__subject",
                    "feedback_id__emp_id",
                    "attribute__name",
                    # "feedback_id__feedback_id__uniq_id",
                    )
                    )

    per_sem_attributes = list(StuFeedbackAttributes.objects.filter(subject_type__in=subject_type).exclude(eligible_settings_id__status="DELETE").exclude(subject_type__isnull=True).values('name').distinct())
    # '''ATTRIBUTE DATA GATHERING'''
    per_sem_attribute_ids = {}
    for attribute in per_sem_attributes:
        per_sem_attribute_ids[attribute['name']] = attribute
    student_counter = -1
    # '''COURSE LOOP'''
    for course_sno, (course_name, course_group) in enumerate(groupby(data_set, key=lambda group_course: group_course['feedback_id__feedback_id__uniq_id__section__dept__course__value'])):
        temp_course = list(course_group)

        # '''DEPARTMENT LOOP'''
        for dept_sno, (dept_name, dept_group) in enumerate(groupby(temp_course, key=lambda group_dept: group_dept['feedback_id__feedback_id__uniq_id__section__dept__dept__value'])):
            temp_dept = list(dept_group)

            # '''SEMESTER LOOP'''
            for sem_sno, (sem_name, sem_group) in enumerate(groupby(temp_dept, key=lambda group_sem: group_sem['attribute__eligible_settings_id__sem'])):
                temp_sem = list(sem_group)

            # '''ATTRIBUTE DATA GATHERING'''
                per_sem_attribute_ids = {}
                for attribute in per_sem_attributes:
                    per_sem_attribute_ids[attribute['name']] = attribute

                # '''SECTION LOOP'''
                for section_sno, (section_name, section_group) in enumerate(groupby(temp_sem, key=lambda group_section: group_section['feedback_id__feedback_id__uniq_id__section__section'])):
                    temp_section = list(section_group)
                    if len(temp_section) > 0:
                        section_for_group_detail = temp_section[0]['feedback_id__feedback_id__uniq_id__section']

                    # '''SECTION SUBJECT LOOP'''
                    section_students = get_section_students([temp_section[0]["feedback_id__feedback_id__uniq_id__section"]], {}, session_name)

                    for subject_id, subject_group in groupby(temp_section, key=lambda subject_attribute: subject_attribute['feedback_id__subject']):
                        temp_subject = list(subject_group)

                        # '''SECTION EMPLOYEE LOOP'''
                        for emp_id_id, emp_id_group in groupby(temp_subject, key=lambda emp_id_attribute: emp_id_attribute['feedback_id__emp_id']):
                            temp_emp_id = list(emp_id_group)
                            data_value.append({})

                            attri_keys = set(per_sem_attribute_ids.keys())

                            data_value[-1]["course_sem_section"] = course_name
                            data_value[-1]["branch"] = dept_name
                            data_value[-1]["sem"] = temp_sem[0]['feedback_id__feedback_id__uniq_id__section__sem_id__sem']
                            data_value[-1]["section"] = section_name
                            data_value[-1]["subject"] = temp_emp_id[0]['feedback_id__subject__sub_name'] + "(" + temp_emp_id[0]['feedback_id__subject__sub_alpha_code'] + "-" + temp_subject[0]['feedback_id__subject__sub_num_code'] + ")"
                            student_distinct_list = []
                            for uniq_id, uniq_group in groupby(temp_emp_id, key=lambda uniq_ids: uniq_ids['feedback_id__feedback_id__uniq_id']):
                                student_distinct_list.append(uniq_id)

                            '''#TO GET STUDENT IN GROUP'''

                            q_group_id = GroupSection.objects.filter(section_id=section_for_group_detail).values('group_id').distinct()
                            group_id = list(StudentAttStatus.objects.filter(att_id__emp_id=temp_emp_id[0]["feedback_id__emp_id"], att_id__section_id=section_for_group_detail, uniq_id__in=student_distinct_list, att_id__group_id__in=q_group_id, att_id__subject_id=subject_id, att_id__isgroup="Y").exclude(status="DELETE").exclude(att_id__status="DELETE").values('att_id__group_id', 'att_id__group_id__group_type').distinct())
                            non_group_id = list(StudentAttStatus.objects.filter(att_id__emp_id=temp_emp_id[0]["feedback_id__emp_id"], att_id__section_id=section_for_group_detail, uniq_id__in=student_distinct_list, att_id__subject_id=subject_id, att_id__isgroup="N").exclude(status="DELETE").exclude(att_id__status="DELETE").values('att_id').distinct())
                            if len(non_group_id) == 0 and len(group_id) == 1:
                                temp_student_distinct_list = get_att_group_section_students(group_id[0]['att_id__group_id'], section_for_group_detail, session_name)
                                if(len(temp_student_distinct_list) <= len(section_students[0])):
                                    total_student_distinct_list = list(x['uniq_id'] for x in temp_student_distinct_list)
                                else:
                                    total_student_distinct_list = section_students[0]
                            else:
                                total_student_distinct_list = section_students[0]

                            '''#TO GET STUDENT IN GROUP ENDS'''

                            data_value[-1]["no_given_feedback"] = len(list(set(student_distinct_list)))
                            data_value[-1]["no_total_student"] = len(total_student_distinct_list)
                            data_value[-1]["faculty"] = str(temp_emp_id[0]["feedback_id__emp_id__name"]) + "(" + str(temp_emp_id[0]["feedback_id__emp_id"]) + ")"
                            data_value[-1]["desg"] = str(temp_emp_id[0]["feedback_id__emp_id__desg__value"])
                            data_value[-1]["current_pos"] = str(temp_emp_id[0]["feedback_id__emp_id__current_pos__value"])
                            data_value[-1]["emp_dept"] = str(temp_emp_id[0]["feedback_id__emp_id__dept__value"])
                            data_value[-1]["emp_id__email"] = str(temp_emp_id[0]["feedback_id__emp_id__email"])
                            data_value[-1]["emp_id__mob"] = str(temp_emp_id[0]["feedback_id__emp_id__mob"])

                        # '''ATTRIBUTE CHEKING'''
                            temp_addition = 0
                            temp_addition_attri = 0
                            temp_attri_used = 0

                            temp_addition_att = {}
                            temp_sum = {}

                            for atttibute_id, atttibute_group in groupby(temp_emp_id, key=lambda group_attribute: group_attribute['attribute__name']):
                                temp_attri = list(atttibute_group)
                                temp_key = atttibute_id

                                if atttibute_id not in temp_sum.keys():
                                    # '''ATTRIBUTE ADDITION'''
                                    temp_sum[temp_key] = (sum(list(x['cal_marks'] for x in list(temp_attri) if x['cal_marks']!=None)))
                                    temp_addition_att[temp_key] = len(temp_attri)

                                else:
                                    temp_key = atttibute_id
                                    # '''ATTRIBUTE ADDITION'''
                                    temp_sum[temp_key] = temp_sum[temp_key] + (sum(list(x['cal_marks'] for x in list(temp_attri) if x['cal_marks']!=None )))
                                    temp_addition_att[temp_key] = temp_addition_att[temp_key] + len(temp_attri)

                                # '''OVERALL SECTION ADDITION'''
                                temp_attri_used = temp_attri_used + 1

                            for x in attri_keys:
                                data_value[-1][x] = "--"

                            for x in temp_sum.keys():
                                temp_addition = temp_addition + temp_sum[x]
                                temp_addition_attri = temp_addition_attri + temp_addition_att[x]
                                data_value[-1][x] = round((temp_sum[x] / temp_addition_att[x]), 2)

                            if(temp_attri_used > 0):
                                data_value[-1]['TOTAL'] = round(temp_addition / (temp_addition_attri), 2)
                            else:
                                data_value[-1]['TOTAL'] = 0
    return data_value


def individual_faculty_consolidate(data_value, session_name, subject_type):  # takes list of dictionary with {'emp_id':example}
    data_values = []
    StuFeedbackMarks = generate_session_table_name("StuFeedbackMarks_", session_name)
    StuFeedbackAttributes = generate_session_table_name("StuFeedbackAttributes_", session_name)

    per_attributes = list(StuFeedbackAttributes.objects.filter(subject_type__in=subject_type).exclude(eligible_settings_id__status="DELETE").exclude(subject_type__isnull=True).values('name').distinct())
    per_sem_attribute_ids = {}
    for attribute in per_attributes:
        per_sem_attribute_ids[attribute['name']] = attribute
    for faculty in data_value:
        data_values.append({'emp_id': faculty})
        detail = list(EmployeePrimdetail.objects.filter(emp_id=faculty).values("desg__value", "dept__value", "current_pos__value", "name"))[0]
        for key in detail:
            data_values[-1][key] = detail[key]

        added_avg = 0
        added_avg_count = 0
        for attribute in per_attributes:
            data_set = StuFeedbackMarks.objects.filter(feedback_id__emp_id=faculty, attribute__name=attribute['name'], feedback_id__feedback_id__status="INSERT", attribute__eligible_settings_id__status="INSERT", attribute__subject_type__in=subject_type).annotate(cal_marks=(F("marks")) * 10 / (F("attribute__max_marks"))).aggregate(Avg('cal_marks'))
            if data_set['cal_marks__avg'] is not None:
                data_values[-1][attribute['name']] = round(data_set['cal_marks__avg'], 2)
                added_avg = added_avg + data_set['cal_marks__avg']
                added_avg_count = added_avg_count + 1
            else:
                data_values[-1][attribute['name']] = "--"
        if(added_avg_count > 0):
            data_values[-1]["TOTAL"] = round(added_avg / added_avg_count, 2)

        else:
            data_values[-1]["TOTAL"] = 0

        data_set = list(StuFeedbackMarks.objects.filter(feedback_id__emp_id=faculty, attribute__subject_type__in=subject_type, feedback_id__feedback_id__status="INSERT", attribute__eligible_settings_id__status="INSERT").exclude(attribute__subject_type__isnull=True).values('feedback_id__feedback_id__uniq_id').distinct())
        if len(data_set) is not None:
            data_values[-1]['count'] = len(data_set)
        else:
            data_values[-1]['count'] = "--"
    return data_values

def check_islocked(lock_type, emp_id_li, session_name):
    if lock_type not in ['FF']:
        return False

    today = datetime.now()
    LockingUnlocking = generate_session_table_name("LockingUnlocking_", session_name)

    qry_check = LockingUnlocking.objects.filter(lock_type=lock_type, emp_id__in=emp_id_li).values('unlock_to', 'unlock_from').order_by('-id')
    print(qry_check, "astha")
    if len(qry_check) > 0:
        if qry_check[0]['unlock_to'] > today and qry_check[0]['unlock_from'] <= today:
            return False
        else:
            return True
    else:
        return True

def check_islocked_faculty(lock_type, emp_id_li, session_name):
    if lock_type not in ['FF','FS']:
        return False

    today = datetime.now()
    LockingUnlocking = generate_session_table_name("LockingUnlocking_", session_name)

    qry_check = LockingUnlocking.objects.filter(lock_type=lock_type, emp_id__in=emp_id_li).values('unlock_to', 'unlock_from').order_by('-id')
    if len(qry_check) > 0:
        if qry_check[0]['unlock_to'] > today and qry_check[0]['unlock_from'] <= today:
            return False
        else:
            return True
    else:
        return True
