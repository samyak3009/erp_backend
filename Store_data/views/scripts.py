from django.shortcuts import render
from django.db.models import F
from django.db.models import Min, Count
from django.http import HttpResponse, JsonResponse
import math
from datetime import date, datetime
import json

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, requestMethod, functions
from StudentMMS.constants_functions import requestType

from login.models import EmployeeDropdown
from Registrar.models import *
from StudentAcademics.models import *
from StudentMMS.models import *
from Store_data.models import *

from login.views import checkpermission, generate_session_table_name
from StudentAcademics.views import get_sub_attendance_type, get_student_subjects, get_student_attendance, get_att_category_from_type
from .functions import *
from StudentMMS.views.mms_function_views import get_ctrule_wise_student_marks, bonus_marks_rule_wise, check_if_ctrule_created

session_name = '1920o'
session = 8
sem_type = 'odd'
msg = ''
status = 200


def getComponents(request):
    data = []
    emp_id = request.session['hash1']
    session_name = request.session['Session_name']
    session = request.session['Session_id']
    if checkpermission(request, [rolesCheck.ROLE_DEAN, rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_course')):
                course = list(StudentDropdown.objects.filter(field="COURSE").exclude(status="DELETE").values('sno', 'value'))
                data = course
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def StoredAttendance():
    studentSession = generate_session_table_name("studentSession_", session_name)
    Store_Attendance_Total_Attwise = generate_session_table_name("Store_Attendance_Total_Attwise_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    att_type_li = get_sub_attendance_type(session)
    att_type = []
    nor_rem_tut = []
    for t in att_type_li:
        att_type.append(t['sno'])
        if 'NORMAL' in t['value'] or "REMEDIAL" in t['value'] or "TUTORIAL" in t['value']:
            nor_rem_tut.append(t['sno'])

    att_category_query = get_att_category_from_type(att_type, session)
    uniq_id_stude = get_all_students(sem_type, session_name, session)
    att_category = [t['attendance_category'] for t in att_category_query]

    bulk_data = []
    for uniq in uniq_id_stude:
        Store_Attendance_Total_Attwise.objects.filter(uniq_id=uniq).delete()
        q_att_date = studentSession.objects.filter(uniq_id=uniq).values('att_start_date', 'section__sem_id')
        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
        present_normal = []
        sub_id = []
        for att in att_type_li:

            type_att = []
            type_att.append(att['sno'])

            normal_and_extra_att = []

            get_cat = get_att_category_from_type(type_att, session)
            category = [t['attendance_category'] for t in get_cat]

            q_stu_details = studentSession.objects.filter(uniq_id=uniq).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
            year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
            course = q_stu_details[0]['uniq_id__dept_detail__course']

            query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
            if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
                type_att.extend(nor_rem_tut)
                student_sub_att = get_student_attendance(uniq, q_att_date[0]['att_start_date'], date.today(), session, type_att, subjects, 1, att_category, session_name)

                for present in student_sub_att['sub_data']:
                    if present['id'] != '----':
                        if present['total'] > 0 and present['present_count'] != 0:
                            normal_and_extra_att.append(present['present_count'])
                mapped = zip(sub_id, normal_and_extra_att, present_normal)
                mapped = set(mapped)

                for map1 in mapped:
                    if map1[1] > map1[2] and map1[1] - map1[2] != 0:
                        qry = {
                            "subject_id": map1[0],
                            "att_total": map1[1] - map1[2],
                            "att_present": map1[1] - map1[2],
                            "att_type": att['sno'],
                            "uniq_id": uniq,
                        }
                        bulk_data.append(qry)
            else:
                student_sub_att = get_student_attendance(uniq, q_att_date[0]['att_start_date'], date.today(), session, type_att, subjects, 1, att_category, session_name)

                for sub in student_sub_att['sub_data']:
                    if sub['id'] != '----':
                        if sub['total'] > 0 and sub['present_count'] != 0:
                            total_att = get_attendance_type_total_new(uniq, [att], [sub['id']], session_name, session)
                            present_normal.append(sub['present_count'])
                            sub_id.append(sub['id'])
                            qry = {
                                "subject_id": sub['id'],
                                "att_total": total_att['total_att_type'],
                                "att_present": sub['present_count'],
                                "att_type": att['sno'],
                                "uniq_id": uniq,
                            }
                            bulk_data.append(qry)
    objs = (Store_Attendance_Total_Attwise(uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']), subject=SubjectInfo.objects.get(id=data['subject_id']), att_type=StudentAcademicsDropdown.objects.get(sno=data['att_type']), attendance_total=data['att_total'], attendance_present=data['att_present'])for data in bulk_data)
    query = Store_Attendance_Total_Attwise.objects.bulk_create(objs)
    if query:
        msg = 'Successfully Stored'
        status = 200
    else:
        msg = "Something went wrong."
        status = 409
    return JsonResponse(msg, status=status, safe=False)


def store_total_subject_attendance():
    studentSession = generate_session_table_name("studentSession_", session_name)
    Store_Attendance_Total = generate_session_table_name("Store_Attendance_Total_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    att_type_li = get_sub_attendance_type(session)
    att_type = [t['sno'] for t in att_type_li]
    att_category_query = get_att_category_from_type(att_type, session)
    uniq_id_stude = get_all_students(sem_type, session_name, session)
    att_category = [t['attendance_category'] for t in att_category_query]
    bulk_data = []
    for uniq in uniq_id_stude:
        Store_Attendance_Total.objects.filter(uniq_id=uniq).delete()
        q_att_date = studentSession.objects.filter(uniq_id=uniq).values('att_start_date', 'section__sem_id')
        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
        student_sub_att = get_student_attendance(uniq, q_att_date[0]['att_start_date'], date.today(), session, att_type, subjects, 1, att_category, session_name)
        for sub in student_sub_att['sub_data']:
            if sub['id'] != '----':
                if sub['total'] > 0 and sub['present_count'] != 0:
                    qry = {
                        "subject_id": sub['id'],
                        "att_total": sub['total'],
                        "att_present": sub['present_count'],
                        "uniq_id": uniq,
                    }
                    bulk_data.append(qry)
    objs = (Store_Attendance_Total(uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']), subject=SubjectInfo.objects.get(id=data['subject_id']), attendance_total=data['att_total'], attendance_present=data['att_present'])for data in bulk_data)
    query = Store_Attendance_Total.objects.bulk_create(objs)
    if query:
        msg = 'Successfully Stored'
    else:
        msg = "Something went wrong."
    return JsonResponse(msg, status=status, safe=False)


###################################################################################YASH VIEWS END ####################################################################################################################################################################################


def StoreCtWiseAttendance():
    studentSession = generate_session_table_name("studentSession_", session_name)
    Store_Attendance_Ct_wise = generate_session_table_name("Store_Attendance_Ctwise_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

    att_type_li = get_sub_attendance_type(session)
    # att_type = [t['sno'] for t in att_type_li]
    att_type = []
    nor_rem_tut = []
    for t in att_type_li:
        att_type.append(t['sno'])
        if 'NORMAL' in t['value'] or "REMEDIAL" in t['value'] or "TUTORIAL" in t['value']:
            nor_rem_tut.append(t['sno'])
    att_category_query = get_att_category_from_type(att_type, session)
    att_category = [t['attendance_category'] for t in att_category_query]
    exam_type = get_exam_id(session)
    to_date = date.today()
    uniq_id_stude = get_all_students(sem_type, session_name, session)
    bulk_data = []
    for uniq in uniq_id_stude:
        bulk_data = []

        q_stu_details = studentSession.objects.filter(uniq_id=uniq).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
        year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
        course = q_stu_details[0]['uniq_id__dept_detail__course']
        q_att_date = studentSession.objects.filter(uniq_id=uniq).values('att_start_date', 'section__sem_id')

        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
        present_normal = []
        sub_id = []
        flag = 0
        for exam in exam_type:
            ct_dates = get_ct_dates(session, session_name, exam['sno'], q_stu_details[0]['section__sem_id'])
            if len(ct_dates) > 0:
                flag = flag + 1
                if flag == 1:
                    new_from_date = q_att_date[0]['att_start_date']
                    to_date = ct_dates[0]['from_date']
                else:
                    to_date = ct_dates[0]['from_date']

                for att in att_type_li:

                    type_att = []
                    normal_and_extra_att = []
                    type_att.append(att['sno'])
                    get_cat = get_att_category_from_type(type_att, session)
                    category = [t['attendance_category'] for t in get_cat]

                    query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
                    if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
                        type_att.extend(nor_rem_tut)
                        student_sub_att = get_student_attendance(uniq, new_from_date, to_date, session, type_att, subjects, 1, att_category, session_name)
                        for present in student_sub_att['sub_data']:
                            if present['id'] != '----':
                                if present['total'] > 0 and present['present_count'] != 0:
                                    normal_and_extra_att.append(present['present_count'])
                        mapped = zip(sub_id, normal_and_extra_att, present_normal)
                        mapped = set(mapped)
                        for map1 in mapped:
                            if map1[1] > map1[2] and map1[1] - map1[2] != 0:
                                qry = {
                                    "subject_id": map1[0],
                                    "att_total": map1[1] - map1[2],
                                    "att_present": map1[1] - map1[2],
                                    "att_type": att['sno'],
                                    "exam_id": exam['sno'],
                                    "uniq_id": uniq,
                                }
                                bulk_data.append(qry)
                    else:
                        student_sub_att = get_student_attendance(uniq, new_from_date, to_date, session, type_att, subjects, 1, att_category, session_name)
                        for sub in student_sub_att['sub_data']:
                            if sub['id'] != '----':
                                if sub['total'] > 0 and sub['present_count'] != 0:
                                    present_normal.append(sub['present_count'])
                                    sub_id.append(sub['id'])
                                    qry = {
                                        "subject_id": sub['id'],
                                        "att_total": sub['total'],
                                        "att_present": sub['present_count'],
                                        "att_type": att['sno'],
                                        "exam_id": exam['sno'],
                                        "uniq_id": uniq,
                                    }
                                    bulk_data.append(qry)
            new_from_date = to_date

    objs = (Store_Attendance_Ct_wise(uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']), exam_id=StudentAcademicsDropdown.objects.get(sno=data['exam_id']), subject=SubjectInfo.objects.get(id=data['subject_id']), att_type=StudentAcademicsDropdown.objects.get(sno=data['att_type']), attendance_total=data['att_total'], attendance_present=data['att_present'])for data in bulk_data)
    query = Store_Attendance_Ct_wise.objects.bulk_create(objs)
    if query:
        msg = 'Successfully Stored'
    else:
        msg = "Something went wrong."
    return JsonResponse(msg, status=status, safe=False)

    # return JsonResponse({"attendance": "Stored"})


###################################################### MARKS #########################################################

def store_ctwise_marks(request):
    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        data = {}
        get_subject_type = []
        session_name = request.session['Session_name']
        session = request.session['Session_id']
        sem_type = request.session['sem_type']

        ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        studentSession = generate_session_table_name("studentSession_", session_name)
        CTMarksRules = generate_session_table_name("CTMarksRules_", session_name)
        Store_Ctmarks_RuleWise = generate_session_table_name("Store_Ctmarks_RuleWise_", session_name)

        ### FOR DEPT-SEM-SECTION-SUB_TYPE WISE script ###

        get_dept_ids = request.GET['dept'].split(',')

        if 'ALL' not in request.GET['sem']:
            sem = request.GET['sem'].split(',')
            get_sem_ids = list(StudentSemester.objects.filter(dept__in=get_dept_ids).filter(Q(sem__in=sem) | Q(sem_id__in=sem)).order_by('sem').values_list('sem_id', flat=True).order_by('sem'))
        else:
            if 'odd' in str(sem_type):
                get_sem_ids = list(StudentSemester.objects.filter(dept__in=get_dept_ids).annotate(odd=F('sem') % 2).filter(odd=True).order_by('sem').values_list('sem_id', flat=True).order_by('sem'))
            else:
                get_sem_ids = list(StudentSemester.objects.filter(dept__in=get_dept_ids).annotate(odd=F('sem') % 2).filter(odd=False).order_by('sem').values_list('sem_id', flat=True).order_by('sem'))

        subject_type = set(SubjectInfo.objects.exclude(status="DELETE").exclude(subject_type__value='VALUE ADDED COURSE').exclude(subject_type__value='MENTORING/LIBRARY').exclude(subject_type__value='VALUE ADDED COURSE BY OUTSIDE').exclude(subject_type__value='LAB').distinct().values_list('subject_type', flat=True))

        if 'subject_type' in request.GET:
            get_subject_type = set(map(int, request.GET['subject_type'].split(',')))
            get_subject_type = list(subject_type.intersection(get_subject_type))
        else:
            get_subject_type = subject_type

        ### CHECK IF RULE CREATED ###
        if check_if_ctrule_created(get_dept_ids, get_sem_ids, get_subject_type, session, session_name) == False:
            data = statusMessages.CUSTOM_MESSAGE('Rules are not yet created for selected DEPARTMENT, SEMESTER or SUBJECT TYPE.')
            return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        #############################
        if 'section' in request.GET:
            section_id=request.GET['section']
            get_students=list(studentSession.objects.filter(sem__in=set(get_sem_ids),section_id=section_id).exclude(section__isnull=True).values('uniq_id', 'sem').distinct())
        else:
            get_students=list(studentSession.objects.filter(sem__in=set(get_sem_ids)).exclude(section__isnull=True).values('uniq_id', 'sem').distinct())
        # print(get_students)
        if 'subject' in request.GET: #included due to call of celery function. Per subject entry of marks in store.
            subject_id_list=[]
            subject=request.GET['subject']
            subject_id_list.append(subject)
        else:
            subject_id=list(SubjectInfo.objects.filter(sem__in=get_sem_ids,subject_type__in=subject_type).values('id'))
            subject_id_list=[]
            for sub in subject_id:
                subject_id_list.append(sub['id'])   
        i=1
        for each_id in get_students:
            Store_Ctmarks_RuleWise.objects.filter(uniq_id=each_id['uniq_id'],subject__in=subject_id_list).delete() #added check of subject_id
            marks = get_ctrule_wise_student_marks(each_id['uniq_id'], each_id['sem'], get_subject_type, session_name,subject_id_list) #included a parameter of subject_id to find per subject marks
            print(each_id['uniq_id'],i,marks)
            i=i+1
            for sub in marks['subject_data']:
                for rule_no, rule_data in sub['rule_data'].items():
                    rule_id = rule_data['rule_id']

                    ct_marks = {}
                    ct_list = []
                    for k, v in rule_data['total_ct_converted'].items():
                        Store_Ctmarks_RuleWise.objects.update_or_create(uniq_id=studentSession.objects.get(uniq_id=each_id['uniq_id']), exam_id=StudentAcademicsDropdown.objects.get(sno=k), subject=SubjectInfo.objects.get(id=sub['subject_id']), defaults={'rule_id': CTMarksRules.objects.get(id=rule_id), "ct_marks_obtained": v, "ct_marks_total": rule_data['max_ct_marks'][k]})

        # msg = "Successfully Inserted"
        data = statusMessages.MESSAGE_INSERT

        # return JsonResponse(msg, status=200, safe=False)
        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
######################################################################################################################################################
############################################################ STORE BONUS MARKS-RULE WISE #############################################################


def store_bonus_rule_wise(request):
    session_name = request.session['Session_name']
    session = request.session['Session_id']
    sem_type = request.session['sem_type']
    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        emp_id = request.session['hash1']
        if requestMethod.GET_REQUEST(request):

            BonusMarks_Students = generate_session_table_name('BonusMarks_Students_', session_name)
            BonusMarks_Rule = generate_session_table_name('BonusMarks_Rule_', session_name)
            BonusMarks = generate_session_table_name('BonusMarks_', session_name)
            studentSession = generate_session_table_name('studentSession_', session_name)

            sem_id = request.GET['sem_id'].split(',')
            get_bonus_rule_wise = bonus_marks_rule_wise(sem_id, session_name, session)
            print(get_bonus_rule_wise, 'get_bonus_rule_wise')
            i = 0
            for stu, data in get_bonus_rule_wise.items():
                BonusMarks.objects.filter(uniq_id=stu).delete()
                print(stu, i)
                i += 1
                for rule_no, rule_data in data.items():

                    objs = (BonusMarks(uniq_id=studentSession.objects.get(uniq_id=stu), rule_id=BonusMarks_Rule.objects.get(id=r_id), total_bonus_marks=sub_data['bonus_marks']) for sub, sub_data in rule_data.items() for r_id in sub_data['ids'])
                    qry = BonusMarks.objects.bulk_create(objs)

            data = {'msg': 'Successfully Inserted'}
        else:
            data = statusMessages.MESSAGE_BAD_REQUEST
        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def store_attendance_total():
    studentSession = generate_session_table_name("studentSession_", session_name)
    Store_Attendance = generate_session_table_name("Store_Attendance_", session_name)

    att_type_li = get_sub_attendance_type(session)
    att_type = []
    nor_rem_tut = []
    for t in att_type_li:
        att_type.append(t['sno'])
        if 'NORMAL' in t['value'] or "REMEDIAL" in t['value'] or "TUTORIAL" in t['value']:
            nor_rem_tut.append(t['sno'])
    att_category_query = get_att_category_from_type(att_type, session)
    att_category = [t['attendance_category'] for t in att_category_query]
    to_date = date.today()
    uniq_id_stude = get_all_students(sem_type, session_name, session)
    bulk_data = []
    for uniq in uniq_id_stude:
        Store_Attendance.objects.filter(uniq_id=uniq).delete()
        q_att_date = studentSession.objects.filter(uniq_id=uniq).values('att_start_date', 'section__sem_id')
        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
        student_sub_att = get_student_attendance(uniq, q_att_date[0]['att_start_date'], date.today(), session, att_type, subjects, 1, att_category, session_name)
        if(student_sub_att['present_count'] > 0):
            qry = {
                "present": student_sub_att['present_count'],
                "total": student_sub_att['total'],
                "uniq_id": uniq
            }
            bulk_data.append(qry)
    objs = (Store_Attendance(uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']),  attendance_total=data['total'], attendance_present=data['present'])for data in bulk_data)
    querry = Store_Attendance.objects.bulk_create(objs)

    if query:
        msg = 'Successfully Stored'
    else:
        msg = "Something went wrong."
    return JsonResponse(msg, status=status, safe=False)
