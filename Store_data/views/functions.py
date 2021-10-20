from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F, Q

from Registrar.models import *
from Store_data.models import Store_Attendance_Total_1920o
from StudentAcademics.views import *
from StudentAcademics.models import *

from login.views import generate_session_table_name
from login.views import generate_session_table_name

def get_all_students(sem_type, session_name, session):
    get_students = []
    studentSession = generate_session_table_name('studentSession_', session_name)

    get_course = list(StudentDropdown.objects.filter(field="COURSE").exclude(status="DELETE").values_list('sno', flat=True))
    get_dept_ids = list(CourseDetail.objects.filter(course__in=get_course).values_list('uid', flat=True))
    if 'odd' in str(sem_type):
        get_sem_ids = list(StudentSemester.objects.filter(dept__in=get_dept_ids).annotate(odd=F('sem') % 2).filter(odd=True).order_by('sem').values_list('sem_id', flat=True).order_by('sem'))
    else:
        get_sem_ids = list(StudentSemester.objects.filter(dept__in=get_dept_ids).annotate(odd=F('sem') % 2).filter(odd=False).order_by('sem').values_list('sem_id', flat=True).order_by('sem'))
    # get_sem_ids = [125,133,141,207,215,223,231,239,247,255]
    get_section_ids = Sections.objects.filter(sem_id__in=get_sem_ids, dept__in=get_dept_ids).exclude(status="DELETE").values_list('section_id', flat=True)

    get_students = studentSession.objects.filter(section__in=get_section_ids, sem__in=get_sem_ids, session=session).values_list('uniq_id', flat=True)

    return get_students


def get_student_attendance_subjectwise(uniq_id, att_id, subjects, session_name, session):
    ### attendance for given subjects ###
    # stu_data = [{'uniq_id':value1,'att_type_li':[1,2,3]}]
    attendance_data_li = []

    Store_Attendance_Total_Attwise = generate_session_table_name("Store_Attendance_Total_Attwise_", session_name)

    att_type_li = get_sub_attendance_type(session)

    for uid in uniq_id:
        attendance_data = {'uniq_id': uid, 'total': 0, 'present': 0, 'percent': 0}
        att_percent = 0

        uniq_id_total_att = get_attendance_type_total(uid, att_type_li, session_name, session)
        total_att = list(Store_Attendance_Total_Attwise.objects.filter(uniq_id=uid, att_type__in=att_id, subject__in=subjects).values('uniq_id').annotate(total=Sum('attendance_total') - uniq_id_total_att['total_att_type'], present=Sum('attendance_present')))

        if len(total_att) > 0:
            att_percent = round((total_att[0]['present'] / total_att[0]['total']) * 100, 2)

            attendance_data['total'] = total_att[0]['total']
            attendance_data['present'] = total_att[0]['present']
            attendance_data['percent'] = att_percent

        attendance_data_li.append(attendance_data)
    return (attendance_data_li)


def get_attendance_type_total_new(uniq_id, type_att_li, subjects, session_name, session):
    data = {}
    studentSession = generate_session_table_name("studentSession_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

    total_type_attendance = 0

    for att in type_att_li:

        type_att = []
        type_att.append(att['sno'])

        get_cat = get_att_category_from_type(type_att, session)
        category = [t['attendance_category'] for t in get_cat]

        q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
        qry = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type__in=type_att, att_id__subject_id__in=subjects, approval_status__contains="APPROVED", att_id__date__range=[q_att_date[0]['att_start_date'], date.today()]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
        if len(qry) > 0:
            total = len(qry)
        else:
            total = 0

        total_type_attendance += total

    data = {'uniq_id': uniq_id, 'total_att_type': total_type_attendance}
    return data


def get_overall_attendance(uniq_id_li, session_name, session):
    att_percent_li = []
    data_li = []
    studentSession = generate_session_table_name("studentSession_", session_name)
    Store_Attendance_Total_Attwise = generate_session_table_name("Store_Attendance_Total_Attwise_", session_name)

    att_type_li = get_sub_attendance_type(session)
    att_type = [t['sno'] for t in att_type_li]

    for uniq_id in uniq_id_li:
        data = {}
        att_percent = 0
        total_present = 0
        total_absent = 0
        total = 0
        type_wise = {}
        subject_wise = {}

        for att in att_type_li:
            type_wise_data = {}
            qry = list(Store_Attendance_Total_Attwise.objects.filter(uniq_id=uniq_id, att_type=att['sno']).values('uniq_id').annotate(present=Sum('attendance_present'), total=Sum('attendance_total')))
            if len(qry) > 0:
                type_wise_data[att['sno']] = {}
                type_wise_data[att['sno']] = {'present_count': qry[0]['present'], 'total_att': qry[0]['total']}
                type_wise.update(type_wise_data)

        q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id')
        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
        for sub in subjects:
            sub_wise_data = {}
            qry = list(Store_Attendance_Total_Attwise.objects.filter(uniq_id=uniq_id, subject=sub['id']).values('uniq_id').annotate(present=Sum('attendance_present'), total=Sum('attendance_total')))
            if len(qry) > 0:
                sub_wise_data[sub['id']] = {'present_count': qry[0]['present'], 'total_att': qry[0]['total']}
                subject_wise.update(sub_wise_data)

        uniq_id_total_att = get_attendance_type_total(uniq_id, att_type_li, session_name, session)
        total_att = list(Store_Attendance_Total_Attwise.objects.filter(uniq_id=uniq_id).values('uniq_id').annotate(total=Sum('attendance_total') - uniq_id_total_att['total_att_type'], present=Sum('attendance_present')))
        if len(total_att) > 0:
            att_percent = round((total_att[0]['present'] / total_att[0]['total']) * 100)
            total += total_att[0]['total']
            total_present += total_att[0]['present']
            total_absent = int(total) - int(total_present)

        data = {'uniq_id': uniq_id, 'att_per': att_percent, 'total_attendance': total, 'total_present': total_present, 'total_absent': total_absent, 'type_wise_att': type_wise, 'sub_wise_att': subject_wise}

        data_li.append(data)

    return (data_li)


def get_attendance_type_total(uniq_id, type_att_li, session_name, session):
    data = {}
    studentSession = generate_session_table_name("studentSession_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

    total_type_attendance = 0

    for att in type_att_li:

        type_att = []
        type_att.append(att['sno'])

        get_cat = get_att_category_from_type(type_att, session)
        category = [t['attendance_category'] for t in get_cat]

        q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
        qry = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type__in=type_att, approval_status__contains="APPROVED", att_id__date__range=[q_att_date[0]['att_start_date'], date.today()]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
        if len(qry) > 0:
            total = len(qry)
        else:
            total = 0

        q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')

        course = None
        year = None
        if len(q_stu_details) > 0:
            year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
            course = q_stu_details[0]['uniq_id__dept_detail__course']

        query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field__in=["DAY-WISE ATTENDANCE", 'EXTRA ATTENDANCE'], att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
        if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
            total_type_attendance += total

    data = {'uniq_id': uniq_id, 'total_att_type': total_type_attendance}
    return data


def get_student_attendance_subjectwise(uniq_id, att_id, subjects, session_name, session):
    attendance_data_li = []

    Store_Attendance_Total_Attwise = generate_session_table_name("Store_Attendance_Total_Attwise_", session_name)

    att_type_li = get_sub_attendance_type(session)

    for uid in uniq_id:
        attendance_data = {'uniq_id': uid, 'total': 0, 'present': 0, 'percent': 0}
        att_percent = 0
        uniq_id_total_att = get_attendance_type_total(uid, att_type_li, session_name, session)
        total_att = list(Store_Attendance_Total_Attwise.objects.filter(uniq_id=uid, att_type__in=att_id, subject__in=subjects).values('uniq_id').annotate(total=Sum('attendance_total') - uniq_id_total_att['total_att_type'], present=Sum('attendance_present')))
        if len(total_att) > 0:
            att_percent = round((total_att[0]['present'] / total_att[0]['total']) * 100, 2)

            attendance_data['total'] = total_att[0]['total']
            attendance_data['present'] = total_att[0]['present']
            attendance_data['percent'] = att_percent

        attendance_data_li.append(attendance_data)
    return (attendance_data_li)


def get_exam_id(session):
    data = []
    qry = StudentAcademicsDropdown.objects.filter(field="EXAM NAME", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    for q in qry:
        data.append({'sno': q['sno'], 'value': q['value']})

    return data


def get_ct_dates(session, session_name, exam_id, sem_id):
    data = []
    ExamSchedule = generate_session_table_name('ExamSchedule_', session_name)
    qry = list(ExamSchedule.objects.filter(exam_id=exam_id, sem=sem_id).distinct().exclude(status="DELETE").values("from_date", "to_date"))
    for q in qry:
        data.append(q)
    return data


def get_sub_type_att(uniq_id_li, session_name, session):
    studentSession = generate_session_table_name("studentSession_", session_name)
    Store_Attendance_Total_Attwise = generate_session_table_name("Store_Attendance_Total_Attwise_", session_name)
    data_li = []
    att_type_li = get_sub_attendance_type(session)
    att_type = [t['sno'] for t in att_type_li]

    for uniq_id in uniq_id_li:
        data = {}
        subject = {}
        q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id')
        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
        for sub in subjects:

            sub_wise_att = {}

            subject[sub['id']] = {}
            for att in att_type_li:

                qry = list(Store_Attendance_Total_Attwise.objects.filter(uniq_id=uniq_id, subject=sub['id'], att_type=att['sno']).values('uniq_id').annotate(present=Sum('attendance_present'), total=Sum('attendance_total')))
                if len(qry) > 0:
                    sub_wise_att[att['sno']] = {}
                    sub_wise_att[att['sno']] = {'present_count': qry[0]['present'], 'total': qry[0]['total']}
                    subject[sub['id']].update(sub_wise_att)

        data = {'uniq_id': uniq_id, 'sub_wise_att': subject}
        data_li.append(data)

    return (data_li)


def get_ct_wise_att(uniq_id_li, ct_li, session_name, session):
    studentSession = generate_session_table_name("studentSession_", session_name)
    Store_Attendance_Ct_wise = generate_session_table_name("Store_Attendance_Ctwise_", session_name)
    data_li = []
    att_type_li = get_sub_attendance_type(session)
    att_type = [t['sno'] for t in att_type_li]

    for uniq_id in uniq_id_li:
        data = {}
        for ct in ct_li:
            data_ct = {}
            uniq_id_total_att = get_attendance_type_total(uniq_id, att_type_li, session_name, session)
            qry = list(Store_Attendance_Ct_wise.objects.filter(uniq_id=uniq_id, exam_id=ct).values('uniq_id').annotate(present=Sum('attendance_present'), total=Sum('attendance_total') - uniq_id_total_att['total_att_type']))
            if len(qry) > 0:
                data_ct[ct] = {}
                data_ct[ct] = {'total': qry[0]['total'], 'present': qry[0]['present']}
                data.update(data_ct)

        data = {'uniq_id': uniq_id, 'exam_data': data}
        data_li.append(data)

    return (data_li)
