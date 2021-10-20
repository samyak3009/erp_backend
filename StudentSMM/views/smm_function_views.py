from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
import json
from itertools import groupby
import datetime
from datetime import date
import time
import math

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

from Registrar.models import *
from musterroll.models import EmployeePrimdetail, Roles
from StudentMMS.models import *
from StudentSMM.models import *
from StudentAccounts.models import SubmitFee, RefundFee
from StudentPortal.models import StudentInternshipsTaken

from StudentMMS.constants_functions import requestType
from StudentAcademics.models import *
from login.views import generate_session_table_name, checkpermission
from StudentAcademics.views import *
from StudentPortal.views import get_profile
from StudentMMS.views.mms_function_views import get_student_marks, single_student_ct_marks, get_student_subject_ta_marks, get_student_subject_att_marks, get_student_subject_ct_marks, get_student_per_ct_marks, get_student_total_ct_marks


####################################DROPDOWNS CREATOR##################################


def get_mentor_course(emp_id, session_name):
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    GroupSection = generate_session_table_name("GroupSection_", session_name)
    SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
    emp = []
    emp.append(emp_id)
    q_employee = EmpGroupAssign.objects.filter(emp_id=emp_id, group_id__type_of_group='MENTOR').exclude(group_id__status='DELETE').exclude(status='DELETE').values_list('group_id')
    q_course = GroupSection.objects.filter(group_id__in=q_employee).values('section_id__dept__course__value', 'section_id__dept__course').distinct()
    return list(q_course)


def get_mentor_branch(emp_id, course, session_name):
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    GroupSection = generate_session_table_name("GroupSection_", session_name)
    SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
    emp = []
    emp.append(emp_id)
    q_employee = EmpGroupAssign.objects.filter(emp_id=emp_id, group_id__type_of_group='MENTOR').exclude(group_id__status='DELETE').exclude(status='DELETE').values_list('group_id')
    q_branch = GroupSection.objects.filter(group_id__in=q_employee, section_id__dept__course=course).values('section_id__dept__dept__value', 'section_id__dept__dept').distinct()
    return list(q_branch)


def get_mentor_semester(emp_id, dept, session_name):
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    GroupSection = generate_session_table_name("GroupSection_", session_name)
    SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
    emp = []
    emp.append(emp_id)
    q_employee = EmpGroupAssign.objects.filter(emp_id=emp_id, group_id__type_of_group='MENTOR').exclude(group_id__status='DELETE').exclude(status='DELETE').values_list('group_id')
    q_semester = GroupSection.objects.filter(group_id__in=q_employee, section_id__dept__dept=dept).values('section_id__sem_id__sem', 'section_id__sem_id').order_by('section_id__sem_id__sem').distinct()
    return list(q_semester)


def get_mentor_section(emp_id, sem, session_name):
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    GroupSection = generate_session_table_name("GroupSection_", session_name)
    SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
    emp = []
    emp.append(emp_id)
    q_employee = EmpGroupAssign.objects.filter(emp_id__in=emp, group_id__type_of_group='MENTOR').exclude(group_id__status='DELETE').exclude(status='DELETE').values_list('group_id', flat=True)
    q_section = GroupSection.objects.filter(group_id__in=q_employee, section_id__sem_id=sem).values('section_id__section', 'section_id').distinct()
    return list(q_section)
####################################END DROPDOWN CREATOR################################

#################################GROUP DATA#############################################


def GroupName(grouptype, extra_filter, session_name, sem, emp_id, type):
    data = []
    GroupSection = generate_session_table_name("GroupSection_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    group_id = list(GroupSection.objects.filter(group_id__group_type=grouptype, group_id__type_of_group='MENTOR', section_id__sem_id=sem).filter(**extra_filter).exclude(group_id__status='DELETE').values('group_id__id', 'group_id__group_name').distinct())
    for id in group_id:
        if type == 'M':
            group_name = list(EmpGroupAssign.objects.filter(emp_id=emp_id, group_id=id['group_id__id']).exclude(status='DELETE').values('group_id', 'group_id__group_name').distinct())
            if len(group_name) > 0:
                data.append({'group_id__group_name': group_name[0]['group_id__group_name'], 'group_id__id': group_name[0]['group_id']})
        elif type == 'H' or 'D':
            data.append({'group_id__group_name': id['group_id__group_name'], 'group_id__id': id['group_id__id']})
    return data


# def GroupStudents(groupid, session_name):
#     data = []
#     group_students = group_student_data(groupid, session_name)
#     session = list(Semtiming.objects.filter(session_name=session_name).values('uid'))
#     for grp in group_students:
#         incident = incident_count(grp['uniq_id'], session_name)
#         counselling = counselling_count(grp['uniq_id'], session_name)
#         profile = get_profile(grp['uniq_id'], session_name)
#         data.append({'incident': incident, 'counselling': counselling, 'class_roll_no': grp['uniq_id__class_roll_no'], 'profile': profile})

#     return data
# def GroupStudents(groupid, session_name):
#     data = []
#     group_students = group_student_data(groupid, session_name)
#     print(group_students, 'group_students')
#     session = list(Semtiming.objects.filter(session_name=session_name).values('uid'))
#     for grp in group_students:
#         print(grp['uniq_id'], 'uniq_id')
#         incident_data = incident_count(grp['uniq_id'], session_name)
#         counselling_data = counselling_count(grp['uniq_id'], session_name)
#         profile = get_profile(grp['uniq_id'], session_name)
#         data.append({'incident': {'incident_approved': incident_data[0], 'incident_pending': incident_data[1]}, 'counselling': {"counselling_approved": counselling_data[0], "counselling_pending": counselling_data[1]}, 'class_roll_no': grp['uniq_id__class_roll_no'], 'profile': profile})
#
#     return data
def GroupStudents(groupid, session_name):
    data = []
    attendance_percentage = 0
    studentSession = generate_session_table_name('studentSession_', session_name)
    group_students = group_student_data(groupid, session_name)
    session = list(Semtiming.objects.filter(session_name=session_name).values('uid'))
    to_date = date.today()
    att_type = get_sub_attendance_type(session[0]['uid'])
    att_type_list = []
    for x in att_type:
        print(x['sno'], 'sno')
        att_type_list.append(x['sno'])

    for grp in group_students:
        incident_data = incident_count(grp['uniq_id'], session_name)
        counselling_data = counselling_count(grp['uniq_id'], session_name)
        from_date = list(studentSession.objects.filter(uniq_id=grp['uniq_id']).values('att_start_date', 'section__sem_id'))

        get_internship_data = list(StudentInternshipsTaken.objects.filter(session__session_name=session_name, uniq_id=grp['uniq_id']).exclude(status="DELETE").values_list('internship', flat=True))
        internship_data = []
        if len(get_internship_data) > 0:
            internship_data = get_internship_data
        q_att_date = list(studentSession.objects.filter(uniq_id=grp['uniq_id']).values('att_start_date', 'section__sem_id'))
        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)

        profile = get_profile(grp['uniq_id'], session_name)

        attendance = get_student_attendance(grp['uniq_id'], from_date[0]['att_start_date'], to_date, session[0]['uid'], att_type_list, subjects, 1, [], session_name)
        if int(attendance['total'])>0:
            attendance_percentage = round((attendance['present_count'] / attendance['total']) * 100, 2)
        data.append({'incident': {'incident_approved': incident_data[0], 'incident_pending': incident_data[1]}, 'counselling': {"counselling_approved": counselling_data[0], "counselling_pending": counselling_data[1]}, 'class_roll_no': grp['uniq_id__class_roll_no'], 'profile': profile, 'attendance': attendance_percentage, 'internship_data': internship_data})

    return data


def group_student_data(groupid, session_name):
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    group_students = list(StuGroupAssign.objects.filter(group_id=groupid).exclude(status='DELETE').values('uniq_id', 'uniq_id__class_roll_no', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__uniq_id__lib', 'uniq_id__section__section', 'uniq_id__sem__sem').order_by('uniq_id__class_roll_no'))
    print(group_students)
    return group_students
#################################END GROUP DATA#########################################

#################################COUNCELING DATA#########################################


def get_counselling_type(session):
    counselling_type = StudentAcademicsDropdown.objects.filter(field='TYPE OF COUNSELLING', session=session).exclude(value__isnull=True).values('sno', 'value')
    return list(counselling_type)


# def counselling_count(uniq_id, session_name):
#     CouncellingApproval = generate_session_table_name("CouncellingApproval_", session_name)
#     counselling = CouncellingApproval.objects.filter(councelling_detail__uniq_id=uniq_id, appoval_status='APPROVED').exclude(status='DELETE').count()
#     return counselling
def counselling_count(uniq_id, session_name):
    CouncellingApproval = generate_session_table_name("CouncellingApproval_", session_name)
    counselling_app = CouncellingApproval.objects.filter(councelling_detail__uniq_id=uniq_id, appoval_status='APPROVED').exclude(status='DELETE').exclude(councelling_detail__status="DELETE").count()
    counselling_pen = CouncellingApproval.objects.filter(councelling_detail__uniq_id=uniq_id, appoval_status="PENDING").exclude(status="DELETE").exclude(councelling_detail__status="DELETE").count()
    return [counselling_app, counselling_pen]


def get_student_counselling(uniq_id, session_name):
    CouncellingApproval = generate_session_table_name("CouncellingApproval_", session_name)
    q_counselling = CouncellingApproval.objects.filter(councelling_detail__uniq_id=uniq_id).exclude(status='DELETE').exclude(councelling_detail__status='DELETE').values('remark', 'councelling_detail__date_of_councelling', 'councelling_detail__student_document', 'councelling_detail__type_of_councelling', 'councelling_detail__type_of_councelling__value', 'councelling_detail__remark', 'time_stamp', 'councelling_detail__time_stamp', 'councelling_detail__added_by', 'approved_by', 'councelling_detail__uniq_id__sem__sem', 'councelling_detail__uniq_id__session__session', 'councelling_detail__uniq_id__session__sem_type', 'councelling_detail__uniq_id__uniq_id__name', 'appoval_status', 'approved_by__name', 'approved_by__dept__value', 'approved_by')
    return q_counselling
#############################END COUNCELING DATA#########################################

###################################INCIDENT DATA#########################################


# def incident_count(uniq_id, session_name):
#     IncidentApproval = generate_session_table_name("IncidentApproval_", session_name)
#     incident = IncidentApproval.objects.filter(incident_detail__uniq_id=uniq_id, appoval_status='APPROVED').exclude(status='DELETE').count()
#     return incident
def incident_count(uniq_id, session_name):
    IncidentApproval = generate_session_table_name("IncidentApproval_", session_name)
    incident_app = IncidentApproval.objects.filter(incident_detail__uniq_id=uniq_id, appoval_status='APPROVED').exclude(status='DELETE').exclude(incident_detail__status="DELETE").count()
    incident_pen = IncidentApproval.objects.filter(incident_detail__uniq_id=uniq_id, appoval_status="PENDING").exclude(status="DELETE").exclude(incident_detail__status="DELETE").count()
    return [incident_app, incident_pen]


def get_student_indisciplinary(uniq_id, session_name):
    IncidentApproval = generate_session_table_name("IncidentApproval_", session_name)
    q_indisciplinary = IncidentApproval.objects.filter(incident_detail__uniq_id=uniq_id).exclude(status='DELETE').exclude(incident_detail__status='DELETE').exclude(incident_detail__incident__status='DELETE').values('incident_detail__incident__date_of_incident', 'incident_detail__incident__description', 'incident_detail__incident__incident_document', 'incident_detail__incident__added_by', 'incident_detail__incident__added_by__name', 'incident_detail__incident__added_by__dept__value', 'incident_detail__uniq_id', 'incident_detail__action', 'incident_detail__comm_to_parent', 'incident_detail__uniq_id__sem__sem', 'incident_detail__uniq_id__session__session', 'incident_detail__uniq_id__session__sem_type', 'incident_detail__student_document', 'remark', 'appoval_status', 'approved_by__name', 'approved_by__dept__value', 'approved_by')
    return q_indisciplinary
#############################END INCIDENT DATA##########################################

###################################ACTIVITY DATA#########################################


def get_student_activities(uniq_id, session_name):
    ActivitiesApproval = generate_session_table_name("ActivitiesApproval_", session_name)
    q_activity = ActivitiesApproval.objects.filter(Activities_detail__uniq_id=uniq_id).exclude(status__contains='DELETE').exclude(Activities_detail__status__contains='DELETE').values('Activities_detail__id', 'Activities_detail__date_of_event', 'Activities_detail__organised_by', 'Activities_detail__venue_address', 'Activities_detail__venue_city', 'Activities_detail__venue_state', 'Activities_detail__description', 'Activities_detail__student_document', 'remark', 'approved_by', 'Activities_detail__uniq_id__uniq_id__name', 'Activities_detail__uniq_id', 'Activities_detail__uniq_id__sem__sem', 'Activities_detail__uniq_id__session__session', 'Activities_detail__uniq_id__session__sem_type', 'appoval_status', 'approved_by__name', 'approved_by__dept__value', 'approved_by', 'Activities_detail__activity_type', 'Activities_detail__activity_type__value', 'Activities_detail__venue_country')

    return q_activity
#############################END ACTIVITY DATA##########################################


def get_sem_start_date(session):
    data = Semtiming.objects.filter(uid=session).values('sem_start')
    return list(data)


def checkNotNone(data):
    if data is None or data is "" or data == 0:
        return False
    return True

#############################STUDENT DATA##############################################


def GetStudentDetails(uniq_id, session_name):
    studentSession = generate_session_table_name("studentSession_", session_name)
    data = studentSession.objects.filter(uniq_id=uniq_id).values('uniq_id', 'uniq_id__name', 'section', 'sem', 'section__section', 'sem__sem', 'uniq_id__uni_roll_no', 'uniq_id__lib', 'uniq_id__dept_detail', 'uniq_id__dept_detail__dept', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__course', 'uniq_id__dept_detail__course__value')
    return list(data)


def check_residential_status(uniq_id, session_id, sem_type):
    if sem_type == 'even':
        qry = list(Semtiming.objects.filter(uid=session_id).values_list('session', flat=True))
        sem_odd = list(Semtiming.objects.filter(session=qry[0], sem_type='odd').values('uid'))
        session_id = sem_odd[0]['uid']
    residential_status = SubmitFee.objects.filter(cancelled_status='N', uniq_id=uniq_id, fee_rec_no__contains='H', session=session_id).exclude(id__in=RefundFee.objects.values_list('fee_id', flat=True)).exclude(status__contains='DELETE').values()
    if(len(residential_status) > 0):
        return 'HOSTELLER'
    else:
        return 'DAY SCHOLAR'


def student_academic_details(uniq_id, session_name):
    academic = {}
    q_academic_details = StudentAcademic.objects.filter(uniq_id=uniq_id).values('year_10', 'per_10', 'max_10', 'total_12', 'year_12', 'per_12', 'max_12', 'total_12', 'phy_12', 'phy_max', 'chem_12', 'chem_max', 'math_12', 'math_max', 'eng_12', 'eng_max', 'bio_12', 'bio_max', 'pcm_total', 'is_dip', 'per_dip', 'max_dip', 'total_dip', 'ug_year1', 'ug_year1_max', 'ug_year1_back', 'ug_year2', 'ug_year2_max', 'ug_year2_back', 'ug_year3', 'ug_year3_max', 'ug_year3_back', 'ug_year4', 'ug_year4_max', 'ug_year4_back', 'year_ug', 'per_ug', 'max_ug', 'total_ug', 'sem1_ug', 'sem1_ug_max', 'sem1_ug_back', 'sem2_ug', 'sem2_ug_max', 'sem2_ug_back', 'sem3_ug', 'sem3_ug_max', 'sem3_ug_back', 'sem4_ug', 'sem4_ug_max', 'sem4_ug_back', 'sem5_ug', 'sem5_ug_max', 'sem5_ug_back', 'sem6_ug', 'sem6_ug_max', 'sem6_ug_back', 'sem7_ug', 'sem7_ug_max', 'sem7_ug_back', 'sem8_ug', 'sem8_ug_max', 'sem8_ug_back', 'pg_year1', 'pg_year1_max', 'pg_year1_back', 'pg_year2', 'pg_year2_max', 'pg_year2_back', 'pg_year3', 'pg_year3_max', 'pg_year3_back', 'year_pg', 'per_ug', 'sem1_pg', 'sem1_pg_max', 'sem1_pg_back', 'sem2_pg', 'sem2_pg_max', 'sem2_pg_back', 'sem3_pg', 'sem3_pg_max', 'sem3_pg_back', 'sem4_pg', 'sem4_pg_max', 'sem4_pg_back', 'sem5_pg', 'sem5_pg_max', 'sem5_pg_back', 'sem6_pg', 'sem6_pg_max', 'sem6_pg_back', 'area_dip', 'ug_degree', 'ug_area', 'pg_degree', 'pg_area', 'board_10__value', 'board_12__value', 'uni_dip__value', 'uni_pg__value', 'uni_ug__value', 'year_dip')

    for k, v in q_academic_details[0].items():
        academic[k] = v
    #########Academic Information###################
    academic['Academic'] = {}
    if checkNotNone(academic['per_10']):
        academic['Academic']['tenth'] = {}
        academic['Academic']['tenth']['course'] = '10TH'
        academic['Academic']['tenth']['year'] = academic['year_10']
        academic['Academic']['tenth']['percentage'] = academic['per_10']
        if academic['board_10__value'] is None:
            academic['board_10__value'] = '----'
        academic['Academic']['tenth']['board/univ'] = academic['board_10__value']
    if checkNotNone(academic['per_12']):
        academic['Academic']['twelfth'] = {}
        academic['Academic']['twelfth']['course'] = '12TH'
        academic['Academic']['twelfth']['year'] = academic['year_12']
        academic['Academic']['twelfth']['percentage'] = academic['per_12']
        if academic['board_12__value'] is None:
            academic['board_12__value'] = '----'
        academic['Academic']['twelfth']['board/univ'] = academic['board_12__value']
    if checkNotNone(academic['per_dip']):
        academic['Academic']['diploma'] = {}
        academic['Academic']['diploma']['course'] = 'DIPLOMA'
        academic['Academic']['diploma']['year'] = academic['year_dip']
        academic['Academic']['diploma']['percentage'] = academic['per_dip']
        if academic['uni_dip__value'] is None:
            academic['uni_dip__value'] = '----'
        academic['Academic']['diploma']['board/univ'] = academic['uni_dip__value']
    ##############Academic information ends here###########
    return academic


def checkMenteeDetails(uniq_id, emp_id, session_name):
    studentSession = generate_session_table_name("studentSession_", session_name)
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    student = studentSession.objects.filter(uniq_id=uniq_id).values_list('sem__dept__dept', flat=True)
    students = StuGroupAssign.objects.filter(uniq_id=uniq_id, group_id__type_of_group="MENTOR").exclude(status='DELETE').values_list('group_id', flat=True)
    checker_1 = EmpGroupAssign.objects.filter(emp_id=emp_id, group_id__in=students).exclude(status='DELETE').values_list('group_id', flat=True)
    checker_2 = Roles.objects.filter(emp_id=emp_id, emp_id__dept__in=student, roles=rolesCheck.ROLE_HOD).values_list('emp_id', flat=True)
    checker_3 = Roles.objects.filter(emp_id=emp_id, roles=rolesCheck.ROLE_DEAN).values_list('emp_id', flat=True)
    checking = len(checker_3) > 0 or len(checker_2) > 0 or len(checker_1) > 0
    if(checking):
        data = True
    else:
        data = False
    return data
#############################END STUDENT DATA###########################################


def GetMenteeData(group_id, sub, session, session_name):
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
    DeptExamSchedule = generate_session_table_name("DeptExamSchedule_", session_name)
    ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

    ct_group = int(list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP').values('value', 'sno'))[0]['value'])
    f_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
    students = list(StuGroupAssign.objects.filter(group_id=group_id).exclude(status='DELETE').values('uniq_id'))

    data = {}
    for stu in students:

        details = GetStudentDetails(stu['uniq_id'], session_name)

        sem_id = details[0]['sem']
        dept = details[0]['uniq_id__dept_detail']
        exam_conducted = list(SubjectQuestionPaper.objects.exclude(status='DELETE').filter(subject_id__sem=sem_id).values('exam_id', 'exam_id__value').distinct().order_by('exam_id'))

        att_type = get_sub_attendance_type(session)
        att_type_li = [t['sno'] for t in att_type]

        data[details[0]['uniq_id__name']] = {}
        subject = list(SubjectInfo.objects.filter(subject_type__value='THEORY', id=sub).exclude(status="DELETE").values('id', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'max_ct_marks', 'subject_type__value', 'subject_type', 'max_ta_marks', 'sem', 'max_att_marks'))

        if not subject:
            subject = []
        Att_status = StudentAttStatus.objects.filter(uniq_id=stu['uniq_id'], approval_status='APPROVED').exclude(status='DELETE').values('present_status')
        p = 0
        i = 0
        for s in subject:
            data[details[0]['uniq_id__name']][i] = {}
            data[details[0]['uniq_id__name']][i]['subject_name'] = s['sub_name']
            for exam in exam_conducted:
                exam_name = exam['exam_id__value']
                marks_obtained = 0.0
                total_marks = 0.0
                marks = get_student_marks(stu['uniq_id'], session_name, s['id'], exam['exam_id'], int(s['max_ct_marks']), ct_group, sem_id)
                marks_obtained = marks['converted_marks']
                total_marks = s['max_ct_marks'] / ct_group
                ################################################### FOR ATTENDANCE ###################################################
                if len(Att_status) == 0:
                    att_per = 0.0
                else:
                    if p == 0:
                        from_date = f_date[0]['sem_start']
                        exam_date = 0
                        p = p + 1
                    else:
                        if p == 0:
                            from_date = f_date[0]['sem_start']
                            exam_date = 0
                            p = p + 1
                        else:
                            if exam_date != 0:
                                from_date = exam_date
                            else:
                                att_per = 0.0
                            p = p + 1
                date = list(ExamSchedule.objects.filter(subject_type=s['subject_type'], exam_id=exam['exam_id']).exclude(status='DELETE').values('from_date', 'id'))
                if len(date) > 0:
                    if isinstance(date[0]['from_date'], datetime.date):
                        exam_date = "{}-{}-{}".format(date[0]['from_date'].year, date[0]['from_date'].month, date[0]['from_date'].day)
                    to_date = exam_date
                    query = get_student_attendance(stu['uniq_id'], from_date, to_date, session, att_type_li, [s], 1, [], session_name)
                    if query['total'] == 0:
                        att_per = 'N/A'
                    else:
                        att = (query['present_count'] / query['total']) * 100
                        att_per = round(att, 0)
                else:
                    att_per = 0.0
            ###################################################### END #############################################################
                data[details[0]['uniq_id__name']][i][exam_name + ' Marks_obt'] = marks_obtained
                data[details[0]['uniq_id__name']][i][exam_name + ' Total'] = total_marks
                data[details[0]['uniq_id__name']][i][exam_name + ' Attendance'] = att_per

            # from_data=f_date[0]['sem_start']
            # # to_date=datetime.now()
            # to_date=f_date[0]['sem_end']

            # query=get_student_attendance(stu['uniq_id'],from_date,to_date,session,att_type_li,[s],1,[],session_name)
            # att = (query['present_count']/query['total'])*100
            # att_per = round(att,0)

            # data[details[0]['uniq_id__name']]['Total_Attendance']=att_per

        i = i + 1

    return data


def UnivMarksInfo(uniq_id, session_name):
    print(session_name)
    data = []
    studentSession = generate_session_table_name("studentSession_", session_name)
    StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", session_name)
    q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id', 'section__sem_id__sem')
    if len(q_att_date) == 0:
        return data
    subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
    marks = []
    total_marks = 0.0
    total_marks_obt = 0.0
    count = 0
    max_marks = 0.0
    max_int_marks = 0.0
    total_internal = 0.0
    total_external = 0.0
    Aggregate = 0.00
    for s in subjects:
        marks = list(StudentUniversityMarks.objects.filter(uniq_id=uniq_id, subject_id=s['id']).values('external_marks', 'internal_marks', 'subject_id__max_university_marks', 'subject_id__max_ct_marks', 'subject_id__max_att_marks', 'subject_id__max_ta_marks', 'back_marks'))
        for m in marks:
            try:
                internal = float(m['internal_marks'])
            except:
                internal = 0
            if internal != 0:
                max_marks = float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks'])
            else:
                max_marks = 0
            max_int_marks = max_int_marks + float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks'])

            if (m['back_marks'] != None):
                # count = count+1
                try:
                    m['external_marks'] = float(m['back_marks'])
                except:
                    m['external_marks'] = 'NA'

            try:
                total_internal = float(m['internal_marks'])
                total_marks_obt = total_marks_obt + total_internal
            except:
                total_internal = "NA"
            try:
                total_external = float(m['external_marks'])
                total_marks_obt = total_marks_obt + total_external
            except:
                total_external = "NA"
            total_marks = total_marks + max_marks
            # total_marks_obt = total_marks_obt + total_external + total_internal
            if max_marks > 0:
                if type(total_external) == float and type(total_internal) == float:
                    if(round((total_internal + total_external) / max_marks, 2) * 100 < 40) or (round(total_external / float(m['subject_id__max_university_marks']), 2) * 100 < 30):
                        count = count + 1
            #       Status = 'Semester Back'
            #   else:
            #       Status = 'Pass'
    if total_marks > 0.0:
        Aggregate = round((total_marks_obt / total_marks) * 100, 4)
    data = {'Semester': q_att_date[0]['section__sem_id__sem'], 'Marks': {'Obtained_Marks': total_marks_obt, 'Max_Marks': total_marks}, 'Carry_Over': count, 'Aggregate': Aggregate}
    return data


def SemesterWisePerformance(uniq_id, session_name, session):
    studentSession = generate_session_table_name("studentSession_", session_name)
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
    GroupSection = generate_session_table_name("GroupSection_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    CouncellingApproval = generate_session_table_name("CouncellingApproval_", session_name)
    SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
    ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
    DeptExamSchedule = generate_session_table_name("DeptExamSchedule_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

    session_num = int(session_name[:2])
    data = []
    details = list(studentSession.objects.filter(uniq_id=uniq_id).values('uniq_id', 'uniq_id__name', 'section', 'sem', 'section__section', 'sem__sem', 'uniq_id__uni_roll_no', 'uniq_id__lib', 'uniq_id__dept_detail', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__course', 'uniq_id__dept_detail__course__value'))
    if len(details) == 0:
        return data
    sem = details[0]['sem__sem']

    group_id = list(StuGroupAssign.objects.filter(uniq_id=uniq_id, group_id__type_of_group='MENTOR').exclude(status='DELETE').values_list('group_id'))
    sem_group = list(GroupSection.objects.filter(section_id__sem_id__sem=sem, group_id__in=group_id).values_list('group_id'))
    mentor_name = EmpGroupAssign.objects.filter(group_id__in=sem_group).exclude(status='DELETE').values('emp_id__name', 'emp_id')
    if mentor_name:
        Mentor_Name = mentor_name[0]
    else:
        Mentor_Name = {}

    Att_status = StudentAttStatus.objects.filter(uniq_id=uniq_id, approval_status='APPROVED').exclude(status='DELETE').values('present_status')

    ct_group = int(list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP').values('value', 'sno'))[0]['value'])
    sem_id = details[0]['sem']
    dept = details[0]['uniq_id__dept_detail']
    exam_conducted = (SubjectQuestionPaper.objects.exclude(status='DELETE').filter(subject_id__sem=sem_id).values('exam_id', 'exam_id__value').distinct().order_by('exam_id'))
    f_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
    subject = list(SubjectInfo.objects.filter(Q(subject_type__value='THEORY') | Q(subject_type__value='ELECTIVE/SPECIALIZATION') | Q(subject_type__value='VALUE ADDED COURSE')).exclude(status="DELETE").filter(sem=details[0]['sem']).values('id', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'max_ct_marks', 'subject_type__value', 'subject_type', 'max_ta_marks', 'sem', 'max_att_marks'))

    att_type = list(get_sub_attendance_type(session))
    att_type = [t['sno'] for t in att_type]
    subjects = {}
    keys = []

    j = 0
    for s in subject:
        sub = s['sub_name']
        subjects[sub] = {}
        t = 0
        overall_marks = 0.0
        for exam in exam_conducted:
            exam_name = exam['exam_id__value']
            subjects[sub][exam_name] = {}
            if session_num < 19:
                marks = get_student_marks(uniq_id, session_name, s['id'], exam['exam_id'], int(s['max_ct_marks']), ct_group, details[0]['sem'])
            else:
                data = get_student_per_ct_marks([uniq_id], [exam['exam_id']], [s['id']], session_name)
                marks = {}
                if len(data) > 0:
                    if len(data[0]['sub_details']) > 0:
                        if len(data[0]['sub_details'][0]['marks_info']) > 0:
                            marks['converted_marks'] = data[0]['sub_details'][0]['marks_info'][0]['marks_obtained']
                            marks['total_marks'] = data[0]['sub_details'][0]['marks_info'][0]['out_of']

                        else:
                            marks['converted_marks'] = 0
                            marks['total_marks'] = 0

            ########################################### FOR ATTENDANCE ######################################################
            if len(Att_status) == 0:
                from_date = f_date[0]['sem_start']
                att_per = 0.0
            else:
                if t == 0:

                    from_date = f_date[0]['sem_start']
                    exam_date = 0

                    t = t + 1
                else:
                    if exam_date != 0:
                        from_date = exam_date
                    else:
                        att_per = 0.0
                    t = t + 1
            date = list(ExamSchedule.objects.filter(subject_type=s['subject_type'], exam_id=exam['exam_id'], sem=sem_id).exclude(status='DELETE').values('to_date', 'id'))
            if len(date) > 0:
                if 'datetime.date' in str(type(date[0]['to_date'])):
                    exam_date = "{}-{}-{}".format(date[0]['to_date'].year, date[0]['to_date'].month, date[0]['to_date'].day)
                to_date = exam_date

                query = get_student_attendance(uniq_id, from_date, to_date, session, att_type, [s], 1, [], session_name)
                if query['total'] == 0:
                    att_per = 'N/A/'
                else:
                    att = (query['present_count'] / query['total']) * 100
                    att_per = round(att, 0)
            else:
                att_per = 0.0
            ############################################ END #################################################################
            if j != -1:
                if session_num < 19:
                    keys.append({exam_name: s['max_ct_marks'] / ct_group})
                else:
                    keys.append({exam_name: marks['total_marks']})
                # keys.append(exam_name+' Total_marks')
                # keys.append(exam_name+' Attendance')
            subjects[sub][exam_name]['Marks_obt'] = marks['converted_marks']
            subjects[sub][exam_name]['Total_marks'] = s['max_ct_marks'] / ct_group
            subjects[sub][exam_name]['Attendance'] = att_per
            if type(marks['converted_marks']) == int:
                overall_marks = overall_marks + marks['converted_marks']
        if len(Att_status) == 0:
            att_per1 = 0.0
            subjects[sub]['Overall_Marks_Obt'] = 'N/A'
            subjects[sub]['Overall_Total_Marks'] = 'N/A'
            subjects[sub]['Overall_CT Marks_Obt'] = 'N/A'
            subjects[sub]['Overall_CT_Total_Marks'] = 'N/A'
        else:
            # temp_data = single_student_ct_marks(session_name,uniq_id,[s],{})
            if session_num < 19:
                temp_data = get_student_subject_ct_marks(uniq_id, session_name, s['id'], s['subject_type'], s['max_ct_marks'], sem_id)

            else:
                data = get_student_total_ct_marks([uniq_id], sem_id, [s['id']], session_name)
                if len(data) > 0:
                    if len(data[0]['sub_details']) > 0:
                        temp_data = data[0]['sub_details'][0]['selected_internal']['marks_obtained']

            ############## INTERNAL #####################
            ta = get_student_subject_ta_marks(uniq_id, session_name, s['id'])
            if(type(ta) != float):
                ta = 0
            att = get_student_subject_att_marks(uniq_id, session_name, s['id'], s['subject_type'], sem_id, s['max_att_marks'])
            if(type(att['att_marks']) != float):
                att['att_marks'] = 0
            ############### END ########################

            query1 = get_student_attendance(uniq_id, f_date[0]['sem_start'], f_date[0]['sem_end'], session, att_type, [s], 1, [], session_name)
            if query1['total'] == 0:
                att_per1 = 'N/A'
            else:
                att1 = (query1['present_count'] / query1['total']) * 100
                att_per1 = round(att1, 0)
            subjects[sub]['Overall_Marks_Obt'] = temp_data
            subjects[sub]['Overall_CT_Marks_Obt'] = temp_data
            subjects[sub]['Overall_Total_Marks'] = s['max_ct_marks']
            subjects[sub]['Overall_CT_Total_Marks'] = s['max_ct_marks']
            subjects[sub]['Overall_Internal_Marks_Obt'] = temp_data + att['att_marks'] + ta
            subjects[sub]['Overall_Total_Internal_Marks'] = s['max_ta_marks'] + s['max_ct_marks'] + s['max_att_marks']
        subjects[sub]['Overall_Attendance'] = att_per1
        j = -1

    # overall_ct={}
    # p=0
    # for exam in exam_conducted:
    #   exam_name=exam['exam_id__value']
    #   marks_obtained=0.0
    #   total_marks=0.0
    #   for s in subject:
    #       marks1 = get_student_marks(uniq_id,session_name,s['id'],exam['exam_id'],int(s['max_ct_marks']),ct_group,details[0]['sem'])
    #       if type(marks_obtained)==type(marks1['marks_obtained']):
    #           marks_obtained=marks_obtained+marks1['converted_marks']
    #       total_marks=total_marks+s['max_ct_marks']/ct_group
    #   ################################################### FOR ATTENDANCE #######################################################
    #   if len(Att_status)==0:
    #       att_per2 = 0.0
    #   else:
    #       if p==0:
    #           from_date1=f_date[0]['sem_start']
    #           exam_date1=0

    #           p=p+1
    #       else:

    #           if exam_date1!=0:
    #               from_date1=exam_date1
    #           else:
    #               att_per2=0.0
    #           p=p+1
    #       date1 = list(DeptExamSchedule.objects.filter(subject_id=s['id'],exam_id=exam['exam_id']).exclude(status='DELETE').values('exam_date','id'))
    #       if len(date1)>0:
    #           if isinstance(date1[0]['exam_date'], datetime.date):
    #               exam_date1= "{}-{}-{}".format(date1[0]['exam_date'].year, date1[0]['exam_date'].month, date1[0]['exam_date'].day)
    #           to_date1=exam_date1

    #           query2=get_student_attendance(uniq_id,from_date1,to_date1,session,att_type,subjects,1,[],session_name)
    #           if query2['total']==0:
    #               att_per2='N/A'
    #           else:
    #               att_per2 = (query2['present_count']/query2['total'])*100
    #       else:
    #           att_per2=0.0
    #   ###################################################### END ###############################################################
    #   overall_ct[exam_name+' Marks_obt']=marks_obtained
    #   overall_ct[exam_name+' Total']=total_marks
    #   overall_ct[exam_name+' Attendance']=att_per2
    data = {}
    q_counselling = get_student_counselling(uniq_id, session_name)
    counselling_type = get_counselling_type(session)
    data['KEYS'] = keys
    data['SUBJECTS'] = subjects
    data['MENTOR_NAME'] = Mentor_Name
    data['COUNSELLING'] = list(q_counselling)
    data['COUNSELLING_TYPE'] = list(counselling_type)
    return data

######## CHECK FUNCTIONS ###############


def check_if_mentor_of_student(uniq_id, emp_id, session_name):
    studentSession = generate_session_table_name("studentSession_", session_name)
    StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
    EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)

    student = studentSession.objects.filter(uniq_id=uniq_id).values_list('sem__dept__dept', flat=True)
    group_ids = StuGroupAssign.objects.filter(uniq_id=uniq_id, group_id__type_of_group="MENTOR").exclude(status='DELETE').values_list('group_id', flat=True)
    checker_1 = EmpGroupAssign.objects.filter(emp_id=emp_id, group_id__in=group_ids).exclude(status='DELETE').values_list('group_id', flat=True)
    if len(checker_1) > 0:
        return True
    else:
        return False
