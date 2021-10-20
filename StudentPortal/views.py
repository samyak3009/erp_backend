# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
import json
import datetime
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import time
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum, Count, Max
from datetime import date
from datetime import datetime
import math
import calendar
import io
from threading import Thread
import requests
from PIL import Image, ImageChops, ImageOps
from PIL import ImageFont
from PyPDF2 import PdfFileMerger, PdfFileReader
from PIL import ImageDraw
import textwrap
import qrcode
import urllib
from operator import itemgetter

from StudentMMS.constants_functions import requestType
from StudentMMS.views.mms_function_views import *

from .models import *
from StudentAcademics.models import *
from Registrar.models import *
from LessonPlan.models import *
from StudentMMS.models import *
from StudentHostel.models import *
from StudentSMM.models import *
from StudentAccounts.models import SubmitFee, ModeOfPaymentDetails, SubmitFeeComponentDetails, StuAccFeeSettings, StudentAccountsDropdown, RefundFee
from login.models import EmployeePrimdetail, Daksmsstatus, EmployeeDropdown, EmployeePrimdetail, AuthUser
from attendance.models import Attendance2

from login.views import checkpermission, generate_session_table_name
from dashboard.views import academic_calendar
from StudentAcademics.views import *
from login.views import send_mail

import StudentHostel as studenthostel
import StudentSMM as smm
# Create your views here.


def isadmin(request):
    if requestMethod.GET_REQUEST(request):
        unique_id = request.session['uniq_id']
        admin_list = [4348, 4245, 233]
        if unique_id in admin_list:
            data = {"isAdmin": True}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            data = {"isAdmin": False}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def getFeeReceipts(uniq_id, session_id):
    session_ids = []
    session_details = Semtiming.objects.filter(uid=session_id).values('session')
    new_session_id = (Semtiming.objects.filter(session=session_details[0]['session'], sem_type='odd').values('uid'))[0]['uid']
    get_session_ids = SubmitFee.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").exclude(cancelled_status='Y').values('session__session_name', 'session')
    for ses in get_session_ids:
        if int(ses['session__session_name'][:2]) >= 18:
            session_ids.append(ses['session'])
    q_fee_receipts = SubmitFee.objects.filter(session__in=session_ids, uniq_id=uniq_id).exclude(cancelled_status='Y').exclude(fee_rec_no=None).exclude(status='DELETE').extra(select={'receipt_date': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('fee_rec_no', 'id', 'receipt_type', 'receipt_date', 'session__session')
    for q in q_fee_receipts:
        if q['receipt_type'] == 'N':
            q['receipt_type'] = 'Normal'
        elif q['receipt_type'] == 'D':
            q['receipt_type'] = 'Due'

        if q['fee_rec_no'][0] == 'A':
            q['fee_type'] = 'Academic Fee'
        elif q['fee_rec_no'][0] == 'H':
            q['fee_type'] = 'Hostel Fee'
        elif q['fee_rec_no'][0] == 'P':
            q['fee_type'] = 'Penalty Fee'

    return list(q_fee_receipts)


def get_sub_type():
    query = StudentDropdown.objects.filter(field="SUBJECT TYPE").exclude(value__isnull=True).exclude(status="DELETE").values('value', 'sno')
    return list(query)


def get_header_profile(uniq_id):
    data = []
    q_profile = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('image_path', 'uniq_id__name', 'uniq_id__uni_roll_no')
    data = list(q_profile)
    if data[0]['uniq_id__uni_roll_no'] is None or data[0]['uniq_id__uni_roll_no'] == '':
        data[0]['uniq_id__uni_roll_no'] = "-----"

    if data[0]['image_path'] is not None:
        imagepath = settings.BASE_URL2 + "StudentMusterroll/Student_images/" + data[0]['image_path']
    else:
        imagepath = settings.BASE_URL2 + "StudentMusterroll/Student_images/default.jpg"
    data[0]['imagepath'] = imagepath
    del data[0]['image_path']
    return data


def get_profile(uniq_id, session_name):
    data = {}
    print(session_name)
    studentSession = generate_session_table_name("studentSession_", session_name)
    q_prim_per_det = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('image_path', 'uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__date_of_add', 'uniq_id__lib', 'uniq_id__gender__value', 'uniq_id__caste__value', 'fname', 'dob', 'aadhar_num', 'bg__value', 'mname', 'uniq_id__email_id', 'uniq_id__dept_detail__dept__value', 'uniq_id__admission_status__value', 'uniq_id__dept_detail__course__value', 'religion__value', 'physically_disabled', 'nationality__value')
    q_sess_det = studentSession.objects.filter(uniq_id=uniq_id).values('mob', 'session__session', 'year', 'section__section', 'sem__sem', 'section', 'sem', 'reg_form_status', 'registration_status', 'class_roll_no')
    print(q_sess_det)
    q_father_mob = StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values('father_mob', 'mother_mob', 'father_email')

    q_address_details = StudentAddress.objects.filter(uniq_id=uniq_id).values('c_add1', 'c_add2', 'p_add1', 'p_add2', 'c_city', 'p_city', 'c_district', 'p_district', 'p_pincode', 'c_pincode', 'c_state__value', 'c_state', 'p_state__value')
    q_primdetail = StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('admission_type__value')

    for k, v in q_prim_per_det[0].items():
        data[k] = v
        if data[k] is None or data[k] == "":
            data[k] = "----"

    for k, v in q_sess_det[0].items():
        data[k] = v
        if data[k] is None or data[k] == "":
            data[k] = "----"

    for k, v in q_father_mob[0].items():
        data[k] = v
        if data[k] is None or data[k] == "":
            data[k] = "----"

    for k, v in q_address_details[0].items():
        data[k] = v
        if data[k] is None or data[k] == "":
            data[k] = "----"
    for k, v in q_primdetail[0].items():
        data[k] = v
        if data[k] is None or data[k] == "":
            data[k] = "----"

    if data['uniq_id__gender__value'] == 'BOY':
        data['uniq_id__gender__value'] = 'MALE'
    elif data['uniq_id__gender__value'] == 'GIRL':
        data['uniq_id__gender__value'] = 'FEMALE'

    if data['mother_mob'] == 0:
        data['mother_mob'] = "----"

    if data['father_mob'] == 0:
        data['father_mob'] = "----"

    if data['mob'] == 0:
        data['mob'] = "----"

    if data['section'] != '----':
        AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)
        q_coord = AcadCoordinator.objects.filter(section=data['section'], coord_type='C').exclude(status="DELETE").values('emp_id__name')
        q_section_sem_coord=AcadCoordinator.objects.filter(section=q_sess_det[0]['section'],coord_type='R').exclude(status='DELETE').values('emp_id__name')

        if len(q_coord) > 0:
            data['coord_name'] = q_coord[0]['emp_id__name']
        else:
            data['coord_name'] = "----"
        if len(q_section_sem_coord)>0:
            data['sem_coord_name']=q_section_sem_coord[0]['emp_id__name']
        else:
            data['sem_coord_name']="----" 

    imagepath = settings.BASE_URL2 + "StudentMusterroll/Student_images/" + data['image_path']
    data['imagepath'] = imagepath
    del data['image_path']
    return data


def get_bank_details(uniq_id):
    data = StudentBankDetails.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').extra(select={'ac_name': 'acc_name', 'ac_num': 'acc_num', 'ifsc': 'ifsc_code'}).values('ac_name', 'ac_num', 'ifsc', 'branch', 'address', 'bank_name')
    if len(data) > 0:
        return data[0]
    else:
        data = {}
        data['ac_name'] = "----"
        data['ac_num'] = "----"
        data['ifsc'] = "----"
        data['branch'] = "----"
        data['address'] = "----"
        data['bank_name'] = "----"

        return data


def get_subjects(sem_id, session_name, sub_type):
    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
    query_sub = SubjectInfo.objects.filter(sem=sem_id, subject_type=sub_type).exclude(status='DELETE').values('subject_type__value', 'subject_unit__value', 'sub_alpha_code', 'sub_num_code', 'sub_name', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'no_of_units', 'id')
    return list(query_sub)


def get_sem_subjects(request, studentSession, SubjectInfo):
    uniq_id = request.session['uniq_id']
    sessionquery = list(studentSession.objects.filter(uniq_id=uniq_id).exclude(fee_status='UNPAID').values('sem', 'sem__dept'))
    temp = list(SubjectInfo.objects.filter(sem=sessionquery[0]['sem'], sem__dept=sessionquery[0]['sem__dept'], subject_type__in=map(int, request.GET['subject_type'].split(',')[:-1])).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'id', 'sem__sem', 'sem__dept__dept__value'))

    for x in temp:
        try:
            x['info'] = '(' + str(x['sem__dept__dept__value']) + "-" + str(x['sem__sem']) + ') ' + str(x['sub_name']) + ' ( ' + str(x['sub_alpha_code']) + str(x['sub_num_code']) + ' )'
        except:
            x['info'] = x['sub_name']
    return list(temp)


def get_activity_type(session):
    qry = list(StudentAcademicsDropdown.objects.filter(field='ACTIVITY TYPE', session=session).exclude(value__isnull=True).values('sno', 'value'))
    return qry


def getComponents(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        # print(request.session['uniq_id'])

        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                session = request.session['Session_id']
                session_name = request.session['Session_name']
                if(request.method == 'GET'):
                    if request.GET['request_type'] == 'fee_receipts':
                        query = getFeeReceipts(request.session['uniq_id'], session)
                        data_values = {'data': query}
                    elif request.GET['request_type'] == 'header_profile':
                        query = get_header_profile(request.session['uniq_id'])
                        query[0]['session'] = list(Semtiming.objects.filter(sem_start__gte="2018-06-01").values('uid', 'session', 'session_name'))
                        query[0]['current_session'] = request.session['Session_id']
                        data_values = {'data': query}
                    elif request.GET['request_type'] == 'exam_name':
                        query = get_exam_name()
                        data_values = {'data': query}
                    elif request.GET['request_type'] == 'attendance_type':
                        data_values = get_sub_attendance_type(session)
                    elif request.GET['request_type'] == 'get_sub_type':
                        data_values = get_sub_type()
                    elif request.GET['request_type'] == 'get_sem_subjects':
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
                        # sessionquery = list(studentSession.objects.filter(uniq_id=uniq_id).exclude(fee_status='UNPAID').values('sem'))
                        data_values = get_sem_subjects(request, studentSession, SubjectInfo)

                    elif request.GET['request_type'] == 'sem_commencement':
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        data = list(studentSession.objects.filter(uniq_id=request.session['uniq_id'], session=session).values('year', 'uniq_id__dept_detail__course', 'session__sem_end'))
                        if data:
                            d = data[0]['uniq_id__dept_detail__course']
                            dt = data[0]['session__sem_end']
                            year = data[0]['year']
                        else:
                            d = None
                            dt = None
                            year = None
                        data1 = list(SemesterCommencement.objects.filter(session=session, course=d, year=year).exclude(status='DELETE').values('commencement_date', 'session__sem_end'))
                        if not data1:
                            att_start = list(Semtiming.objects.filter(uid=session).values('sem_start'))
                            data_values = ({'commencement_date': date.today(), 'session__sem_end': dt,'sem_start':att_start[0]['sem_start']})
                        else:
                            com = data1[0]['commencement_date']
                            end = data1[0]['session__sem_end']
                            data_values = ({'commencement_date': com, 'session__sem_end': end})

                    elif request.GET['request_type'] == 'att_category_from_type':
                        data_values = get_att_category_from_type(request.GET['att_type'].split(','), session)

                    elif request.GET['request_type'] == 'stu_att':
                        from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
                        to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
                        if request.GET['att_category'] == ' ':
                            att_category = []
                        else:
                            att_category = request.GET['att_category'].split(',')
                        att_type = request.GET['att_type'].split(',')
                        uniq_id = request.session['uniq_id']

                        # att_type = get_sub_attendance_type()
                        # att_type_li = [t['sno'] for t in att_type]
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
                        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
                        query = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type, subjects, 1, att_category, session_name)
                        data_values = {'data': query}

                    elif request.GET['request_type'] == 'mobikiet_sem_data':
                        uniq_id = request.session['uniq_id']
                        sem_data = Semtiming.objects.filter(uid=request.session['Session_id']).values('sem_start', 'sem_end', 'session')
                        studentSession = generate_session_table_name("studentSession_", session_name)

                        q_section = studentSession.objects.filter(uniq_id=uniq_id).values('section__section', 'section__sem_id__sem')

                        data_values = {'data': {"Current_session": sem_data[0]['session'], 'Exam_Des': [], 'Till_Schedule': [], 'sem_start': sem_data[0]['sem_start'], 'sem_end': sem_data[0]['sem_end'], 'section': q_section[0]['section__section'], 'sem': q_section[0]['section__sem_id__sem']}, 'error': False, 'message': "", 'is_flexible_update': True}

                    # elif request.GET['request_type'] == 'mobikiet_att':
                    #     SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
                    #     final_data = {}
                    #     from_date = datetime.strptime(str(request.GET['date_from']).split('T')[0], "%Y-%m-%d").date()
                    #     to_date = datetime.strptime(str(request.GET['date_to']).split('T')[0], "%Y-%m-%d").date()
                    #     uniq_id = request.session['uniq_id']
                    #     StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
                    #     studentSession = generate_session_table_name("studentSession_", session_name)
                    #     q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
                    #     if 'att_category' not in request.GET and 'att_type' not in request.GET:
                    #         att_type_li = get_sub_attendance_type(session)
                    #         att_type = [t['sno'] for t in att_type_li]
                    #         att_category_query = get_att_category_from_type(att_type, session)
                    #         att_category = [t['attendance_category'] for t in att_category_query]
                    #     else:
                    #         att_category = request.GET['att_category'].split(',')
                    #         att_type_li = []
                    #         if att_category[0] == '':
                    #             att_category = []
                    #         att_type = request.GET['att_type'].split(',')
                    #     # session_name = '1819e'

                    #     # subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
                    #         # query_sub = list(SubjectInfo.objects.filter(id=request.GET['subject']).exclude(status='DELETE').values('subject_type__value', 'subject_unit__value', 'sub_alpha_code', 'sub_num_code', 'sub_name', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'no_of_units', 'id'))
                    #     # print(q_att_date)
                    #     subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
                    #     att_data = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type, subjects, 1, att_category, session_name)
                    #     print("2")
                    #     final_data['total_present'] = att_data['present_count']
                    #     final_data['total_total'] = att_data['total']
                    #     final_data['error'] = False
                    #     final_data['message'] = ""
                    #     final_data['update'] = False
                    #     final_data['data'] = []
                    #     final_data['attendance_type'] = []
                    #     ############# ATTENDANCE TYPE ATTENDANCE #########################
                    #     normal_attendance = 0
                    #     for att in att_type_li:
                    #         if 'NORMAL' in att['value']:
                    #             normal_id = att['sno']
                    #         final_att_data = {}
                    #         type_att = []
                    #         type_att.append(att['sno'])
                    #         get_cat = get_att_category_from_type(type_att, session)
                    #         category = [t['attendance_category'] for t in get_cat]
                    #         ##### FOR TOTAL #######
                    #         qry = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type__in=type_att, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
                    #         if len(qry) > 0:
                    #             total = len(qry)
                    #         else:
                    #             total = 0
                    #         #######################
                    #         q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
                    #         q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')
                    #         year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
                    #         course = q_year[0]['dept__course']

                    #         query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
                    #         if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
                    #             # if float(query_att[0]['criteria_per']) > 0.0:
                    #             type_att.append(normal_id)
                    #             new_att_data = get_student_attendance(uniq_id, min(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, type_att, subjects, 1, category, session_name)
                    #             print(new_att_data,'check')
                    #             if int(total) > 0 and int(new_att_data['present_count']) != 0:
                    #                 if int(normal_attendance) > 0:
                    #                     new_att_data['present_count'] = new_att_data['present_count'] - normal_attendance
                    #                     final_att_data = {'total': total, 'present_count': new_att_data['present_count'], 'value': att['value'], 'color': get_color_attendance_type(att['value'])}
                    #                     final_data['attendance_type'].append(final_att_data)

                    #         else:
                    #             new_att_data = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(),
                    #                 datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, type_att, subjects, 1, category, session_name)
                    #             if int(new_att_data['present_count']) != 0:
                    #                 if 'NORMAL' in att['value']:
                    #                     normal_attendance = new_att_data['present_count']
                    #                 final_att_data = {'total': total, 'present_count': new_att_data['present_count'], 'value': att['value'], 'color': get_color_attendance_type(att['value'])}
                    #                 final_data['attendance_type'].append(final_att_data)
                    #     #################################################################
                    #     for att in att_data['sub_data']:
                    #         if '-' in str(att['id']):
                    #             stu_sub_data = []
                    #         else:
                    #             stu_sub_data = get_student_subject_att_status(uniq_id, att['id'], max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, att_type, session_name)
                    #         date_li = []
                    #         lec_li = []
                    #         attendance_type_li = []
                    #         status_li = []

                    #         for sub in stu_sub_data:
                    #             date_li.append(sub['att_id__date'])
                    #             lec_li.append(sub['att_id__lecture'])
                    #             status_li.append(sub['present_status'])
                    #             if sub['att_type__value'] in ['SUBSTITUTE']:
                    #                 attendance_type_li.append('S')
                    #             elif sub['att_type__value'] not in ['REMEDIAL', 'NORMAL', 'TUTORIAL']:
                    #                 attendance_type_li.append('E')
                    #             elif sub['att_id__group_id'] is not None:
                    #                 if 'REMEDIAL' in sub['att_type__value']:
                    #                     attendance_type_li.append('R')
                    #                 else:
                    #                     attendance_type_li.append('G')
                    #             else:
                    #                 if 'REMEDIAL' in sub['att_type__value']:
                    #                     attendance_type_li.append('R')
                    #                 else:
                    #                     attendance_type_li.append('N')
                    #         final_data['data'].append({'date': date_li, 'lecture': lec_li, 'status': status_li, 'attedance_type': attendance_type_li, 'subject_name': att['sub_name'], 'sub_code': att['sub_alpha_code'] + "-" + str(att['sub_num_code']), 'lecture_present': att['present_count'], 'lecture_total': att['total'], 'att_type_color': get_color_app()})

                    #     data_values = final_data

                    elif request.GET['request_type'] == 'mobikiet_att':
                        session_name = '1920o'
                        session = 8
                        StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
                        final_data = {}
                        from_date = datetime.strptime(str(request.GET['date_from']).split('T')[0], "%Y-%m-%d").date()
                        to_date = datetime.strptime(str(request.GET['date_to']).split('T')[0], "%Y-%m-%d").date()
                        uniq_id = request.session['uniq_id']
                        normal_id = []
                        if 'att_category' not in request.GET and 'att_type' not in request.GET:
                            att_type_li = get_sub_attendance_type(session)
                            att_type = [t['sno'] for t in att_type_li]
                            e_att = []
                            for t in att_type_li:
                                if 'NORMAL' in t['value'] or 'REMEDIAL' in t['value'] or 'TUTORIAL' in t['value']:
                                    normal_id.append(t['sno'])
                                else:
                                    e_att.append(t['sno'])
                            # normal_id.append(t['sno'] for t in att_type_li)
                            att_category_query = get_att_category_from_type(att_type, session)
                            att_category = [t['attendance_category'] for t in att_category_query]
                        else:
                            att_type_li = []
                            att_category = request.GET['att_category'].split(',')
                            if att_category[0] == '':
                                att_category = []
                            att_type = request.GET['att_type'].split(',')
                        # session_name = '1819e'
                        StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
                        subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
                        att_data = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type, subjects, 1, att_category, session_name)
                        final_data['total_present'] = att_data['present_count']
                        final_data['total_total'] = att_data['total']
                        final_data['error'] = False
                        final_data['message'] = ""
                        final_data['update'] = False
                        final_data['data'] = []
                        final_data['attendance_type'] = []
                        ############# ATTENDANCE TYPE ATTENDANCE #########################
                        normal_attendance = 0
                        # print(att_type_li)
                        get_cat = get_att_category_from_type(normal_id, session)
                        category = [t['attendance_category'] for t in get_cat]
                        e_att_adta = get_student_attendance(uniq_id, min(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, normal_id, subjects, 1, category, session_name)
                        for att in att_type_li:

                            # if 'NORMAL' in att['value'] or 'REMIDIAL' in att['value'] or 'TUTORIAL' in att['value']:
                            #   normal_id.append(att['sno'])
                            final_att_data = {}
                            type_att = []
                            type_att.append(att['sno'])
                            get_cat = get_att_category_from_type(type_att, session)
                            category = [t['attendance_category'] for t in get_cat]
                            ##### FOR TOTAL #######
                            qry = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type__in=type_att, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
                            if len(qry) > 0:
                                total = len(qry)
                            else:
                                total = 0
                            #######################
                            q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
                            q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')
                            year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
                            course = q_year[0]['dept__course']

                            query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
                            if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
                                type_att.extend(normal_id)
                                new_att_data = get_student_attendance(uniq_id, min(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, type_att, subjects, 1, category, session_name)

                                # if att['sno']==652:
                                # print(new_att_data,'vrinda')
                                if int(total) > 0 and int(new_att_data['present_count']) != 0:
                                    if int(normal_attendance) > 0:
                                        # print( new_att_data['present_count'],new_att_data['total'],normal_attendance,att['value'])
                                        new_att_data['present_count'] = new_att_data['present_count'] - e_att_adta['present_count']
                                        final_att_data = {'total': total, 'present_count': new_att_data['present_count'], 'value': att['value'], 'color': get_color_attendance_type(att['value'])}
                                        # print(final_att_data,'final_att_data')

                                        final_data['attendance_type'].append(final_att_data)

                            else:
                                new_att_data = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, type_att, subjects, 1, category, session_name)
                                if int(new_att_data['present_count']) != 0:
                                    # if 'NORMAL' in att['value']:
                                    if att['sno'] in normal_id:
                                        normal_attendance += int(new_att_data['present_count'])
                                    final_att_data = {'total': total, 'present_count': new_att_data['present_count'], 'value': att['value'], 'color': get_color_attendance_type(att['value'])}
                                    final_data['attendance_type'].append(final_att_data)
                        #################################################################
                        for att in att_data['sub_data']:
                            if '-' in str(att['id']):
                                stu_sub_data = []
                            else:
                                stu_sub_data = get_student_subject_att_status(uniq_id, att['id'], max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, att_type, session_name)
                            date_li = []
                            lec_li = []
                            attendance_type_li = []
                            status_li = []

                            for sub in stu_sub_data:
                                date_li.append(sub['att_id__date'])
                                lec_li.append(sub['att_id__lecture'])
                                status_li.append(sub['present_status'])
                                if sub['att_type__value'] in ['SUBSTITUTE']:
                                    attendance_type_li.append('S')
                                elif sub['att_type__value'] not in ['REMEDIAL', 'NORMAL', 'TUTORIAL']:
                                    attendance_type_li.append('E')
                                elif sub['att_id__group_id'] is not None:
                                    if 'REMEDIAL' in sub['att_type__value']:
                                        attendance_type_li.append('R')
                                    else:
                                        attendance_type_li.append('G')
                                else:
                                    if 'REMEDIAL' in sub['att_type__value']:
                                        attendance_type_li.append('R')
                                    else:
                                        attendance_type_li.append('N')
                            final_data['data'].append({'date': date_li, 'lecture': lec_li, 'status': status_li, 'attedance_type': attendance_type_li, 'subject_name': att['sub_name'], 'sub_code': att['sub_alpha_code'] + "-" + str(att['sub_num_code']), 'lecture_present': att['present_count'], 'lecture_total': att['total'], 'att_type_color': get_color_app()})
                        data_values = final_data

                    elif request.GET['request_type'] == 'mobikiet_att_sub_wise':
                        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
                        final_data = {}
                        from_date = datetime.strptime(str(request.GET['date_from']).split('T')[0], "%Y-%m-%d").date()
                        to_date = datetime.strptime(str(request.GET['date_to']).split('T')[0], "%Y-%m-%d").date()
                        uniq_id = request.session['uniq_id']
                        StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
                        if 'att_category' not in request.GET and 'att_type' not in request.GET:
                            att_type_li = get_sub_attendance_type(session)
                            att_type = [t['sno'] for t in att_type_li]
                            att_category_query = get_att_category_from_type(att_type, session)
                            att_category = [t['attendance_category'] for t in att_category_query]
                            subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
                        else:
                            att_category = request.GET['att_category'].split(',')
                            att_type_li = []
                            if att_category[0] == '':
                                att_category = []
                            att_type = request.GET['att_type'].split(',')
                            subjects = list(SubjectInfo.objects.filter(id__in=map(int, request.GET['subject'].split(',')[:-1])).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name').order_by('id'))

                        # session_name = '1819e'

                        # subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
                            # query_sub = list(SubjectInfo.objects.filter(id=request.GET['subject']).exclude(status='DELETE').values('subject_type__value', 'subject_unit__value', 'sub_alpha_code', 'sub_num_code', 'sub_name', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'no_of_units', 'id'))
                        # print(q_att_date)
                        att_data = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type, subjects, 1, att_category, session_name)
                        print("2")
                        final_data['total_present'] = att_data['present_count']
                        final_data['total_total'] = att_data['total']
                        final_data['error'] = False
                        final_data['message'] = ""
                        final_data['update'] = False
                        final_data['data'] = []
                        final_data['attendance_type'] = []
                        ############# ATTENDANCE TYPE ATTENDANCE #########################
                        for att in att_type_li:
                            if 'NORMAL' in att['value']:
                                normal_id = att['sno']
                            final_att_data = {}
                            type_att = []
                            type_att.append(att['sno'])
                            get_cat = get_att_category_from_type(type_att, session)
                            category = [t['attendance_category'] for t in get_cat]
                            ##### FOR TOTAL #######
                            qry = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type__in=type_att, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
                            if len(qry) > 0:
                                total = len(qry)
                            else:
                                total = 0
                            #######################
                            q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
                            q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')
                            year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
                            course = q_year[0]['dept__course']

                            query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
                            if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
                                # if float(query_att[0]['criteria_per']) > 0.0:
                                type_att.append(normal_id)
                                new_att_data = get_student_attendance(uniq_id, min(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, type_att, subjects, 1, category, session_name)
                                if int(total) > 0 and int(new_att_data['present_count']) != 0:
                                    if int(normal_attendance) > 0:
                                        new_att_data['present_count'] = new_att_data['present_count'] - normal_attendance
                                        final_att_data = {'total': total, 'present_count': new_att_data['present_count'], 'value': att['value'], 'color': get_color_attendance_type(att['value'])}
                                        final_data['attendance_type'].append(final_att_data)

                            else:
                                new_att_data = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, type_att, subjects, 1, category, session_name)
                                if int(new_att_data['present_count']) != 0:
                                    if 'NORMAL' in att['value']:
                                        normal_attendance = new_att_data['present_count']
                                    final_att_data = {'total': total, 'present_count': new_att_data['present_count'], 'value': att['value'], 'color': get_color_attendance_type(att['value'])}
                                    final_data['attendance_type'].append(final_att_data)
                        #################################################################
                        for att in att_data['sub_data']:
                            if '-' in str(att['id']):
                                stu_sub_data = []
                            else:
                                stu_sub_data = get_student_subject_att_status(uniq_id, att['id'], max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, att_type, session_name)
                            date_li = []
                            lec_li = []
                            attendance_type_li = []
                            status_li = []

                            for sub in stu_sub_data:
                                date_li.append(sub['att_id__date'])
                                lec_li.append(sub['att_id__lecture'])
                                status_li.append(sub['present_status'])
                                if sub['att_type__value'] in ['SUBSTITUTE']:
                                    attendance_type_li.append('S')
                                elif sub['att_type__value'] not in ['REMEDIAL', 'NORMAL', 'TUTORIAL']:
                                    attendance_type_li.append('E')
                                elif sub['att_id__group_id'] is not None:
                                    if 'REMEDIAL' in sub['att_type__value']:
                                        attendance_type_li.append('R')
                                    else:
                                        attendance_type_li.append('G')
                                else:
                                    if 'REMEDIAL' in sub['att_type__value']:
                                        attendance_type_li.append('R')
                                    else:
                                        attendance_type_li.append('N')
                            final_data['data'].append({'date': date_li, 'lecture': lec_li, 'status': status_li, 'attedance_type': attendance_type_li, 'subject_name': att['sub_name'], 'sub_code': att['sub_alpha_code'] + "-" + str(att['sub_num_code']), 'lecture_present': att['present_count'], 'lecture_total': att['total'], 'att_type_color': get_color_app()})

                        data_values = final_data

                    elif request.GET['request_type'] == 'sub_att_data':
                        from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
                        to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
                        uniq_id = request.session['uniq_id']
                        sub_id = request.GET['subject_id']
                        att_type = get_sub_attendance_type(session)
                        att_type_li = [t['sno'] for t in att_type]
                        studentSession = generate_session_table_name("studentSession_", session_name)

                        q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date')
                        if '-' in sub_id:
                            data_values = {'data': []}
                        else:
                            query = get_student_subject_att_status(uniq_id, sub_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, att_type_li, session_name)
                            data_values = {'data': query, 'att_type_color': get_color()}
                    elif request.GET['request_type'] == 'profile':
                        query = get_profile(request.session['uniq_id'], session_name)
                        data_values = {'data': query}
                    elif request.GET['request_type'] == 'app_profile':
                        query = get_profile(request.session['uniq_id'], session_name)
                        data = {}
                        data['name'] = query['uniq_id__name']
                        data['FName'] = query['fname']
                        data['MOB'] = query['mob']
                        data['email'] = query['uniq_id__email_id']
                        data['M_Name'] = query['mname']
                        data['Religion'] = query['religion__value']
                        data['Category'] = query['uniq_id__name']
                        data['Nationality'] = query['nationality__value']
                        data['DOB'] = query['dob']
                        data['P_Add1'] = query['p_add1']
                        data['P_Add2'] = query['p_add2']
                        data['P_City'] = query['p_city']
                        data['P_Dist'] = query['p_district']
                        data['P_State'] = query['p_state__value']
                        data['P_Pincode'] = query['p_pincode']
                        data['C_Add1'] = query['c_add1']
                        data['C_Add2'] = query['c_add2']
                        data['C_City'] = query['c_city']
                        data['C_Dist'] = query['c_district']
                        data['C_State'] = query['c_state__value']
                        data['C_Pincode'] = query['c_pincode']
                        data['gender'] = query['uniq_id__gender__value']
                        data['image'] = query['imagepath']
                        data['year'] = query['year']
                        data['department'] = query['uniq_id__dept_detail__dept__value']
                        data['uni_roll_no'] = query['uniq_id__uni_roll_no']
                        data['course'] = query['uniq_id__dept_detail__course__value']
                        data['lib_id'] = query['uniq_id__lib']
                        data['bank'] = {}
                        data['bank'] = get_bank_details(request.session['uniq_id'])
                        data['bank']['update'] = False
                        data['bank']['mobileNo'] = query['mob']
                        data['bank']['emailid'] = query['uniq_id__email_id']
                        data['error'] = False
                        data_values = data

                    elif request.GET['request_type'] == 'time_table':
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        q_sec = studentSession.objects.filter(uniq_id=request.session['uniq_id']).values('section')
                        if q_sec[0]['section'] is not None:
                            data = get_section_time_table(q_sec[0]['section'], session_name)
                        else:
                            data = []
                        query = {'error': False, 'message': "", 'data': data}
                        data_values = query
                    elif request.GET['request_type'] == 'time_table_dash':
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        session = Semtiming.objects.get(uid=request.session['Session_id'])
                        q_sec = studentSession.objects.filter(uniq_id=request.session['uniq_id']).values('section__section', 'sem__sem', 'sem', 'sem__dept__dept__value', 'section')
                        if q_sec[0]['section'] is not None and q_sec[0]['section'] is not None:
                            data = create_matrix_tt(session, q_sec[0]['sem'], q_sec[0]['section'], session_name)
                            data.append(q_sec[0]['section__section'])
                            data.append(q_sec[0]['sem__sem'])
                            data.append(q_sec[0]['sem__dept__dept__value'])
                        else:
                            data = []
                        data_values = data

                    elif request.GET['request_type'] == 'academic_calendar':
                        data_values = academic_calendar(session_name)

                    elif request.GET['request_type'] == 'get_activity_type':
                        data_values = get_activity_type(session)

                    status = 200

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 401

    return JsonResponse(data=data_values, status=status, safe=False)


def left_panel(request):
    data = [{}]
    msg = ""
    i = 0
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if(request.method == 'GET'):
                uniq_id = request.session['uniq_id']
                # print(uniq_id)

                links = list(StudentLeftPanel.objects.filter(parent_id='0').values().order_by('priority'))
                for link in links:
                    sub_tabs = list(sublinks(link['menu_id']))
                    link['sub_tabs'] = sub_tabs
                    data[i]["role"] = 'Student'

                data[i]["tabs"] = list(links)
                i += 1
                msg = "success"
                status = 200
            else:
                status = 502
        else:
            status = 401
    else:
        status = 500
    result = {'msg': msg, 'data': data}

    return JsonResponse(data=result, status=status)


def sublinks(parent_id):
    if StudentLeftPanel.objects.filter(parent_id=parent_id).all().count() == 0:
        return []
    else:
        links = StudentLeftPanel.objects.filter(parent_id=parent_id).values().order_by('priority')
        for link in links:
            sub_tabs = list(sublinks(link['menu_id']))
            link['sub_tabs'] = sub_tabs
        return links


def printFeeReceipts(request):
    data_values = {}
    msg = ""
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                session = Semtiming.objects.get(uid=request.session['Session_id'])
                session_name = request.session['Session_name']
                if(request.method == 'GET'):
                    # data=json.loads(request.body)
                    fee_rec_no = request.GET['fee_rec_no']
                    # print(data)
                    # fee_id=data['fee_id']

                    get_session = SubmitFee.objects.filter(fee_rec_no=fee_rec_no).values('session__session', 'session__session_name')
                    if len(get_session) > 0 and int(get_session[0]['session__session_name'][:2]) < 18:
                        return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    studentSession = generate_session_table_name("studentSession_", get_session[0]['session__session_name'])

                    q_check = SubmitFee.objects.filter(fee_rec_no=fee_rec_no).exclude(status="DELETE").values('fee_rec_no', 'uniq_id__name', 'cancelled_status', 'actual_fee', 'paid_fee', 'refund_value', 'due_value', 'session__session', 'receipt_type', 'id', 'time_stamp', 'uniq_id', 'receipt_type', 'prev_fee_rec_no', 'uniq_id__gender__value')
                    if len(q_check) == 0:
                        status = 403
                        msg = "Fee Receipt not Found"
                    else:
                        if q_check[0]['uniq_id'] == request.session['uniq_id']:
                            fee_rec_no = q_check[0]['fee_rec_no']
                            uniq_id = q_check[0]['uniq_id']
                            fee_id = q_check[0]['id']
                            receipt_name = "Student's Copy"
                            filename = "stu_port.pdf"
                            bool_white = False

                            date = datetime.strptime(str(q_check[0]['time_stamp']).split(' ')[0], "%Y-%m-%d").strftime("%d-%m-%Y")

                            stu_per = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname')
                            if len(stu_per) > 0:
                                fname = stu_per[0]['fname']
                            else:
                                fname = "----"
                            stu_det = studentSession.objects.filter(uniq_id=uniq_id).values('year', 'uniq_id__dept_detail__dept__value', 'sem__dept__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__exam_roll_no')

                            q_mop_details = ModeOfPaymentDetails.objects.filter(fee_id=fee_id).values('MOPcomponent__value', 'value')

                            fee_comp_details = SubmitFeeComponentDetails.objects.filter(fee_id=fee_id).values('fee_component__value', 'fee_sub_component__value', 'sub_component_value').order_by('fee_sub_component')

                            if not bool_white:
                                img = Image.open(settings.FILE_PATH + "KIET_Fee_Receipt.jpg")
                            else:
                                img = Image.new(mode='RGB', size=(1478, 2100), color=(255, 255, 255, 0))

                            size = 1480, 2100
                            img.thumbnail(size, Image.ANTIALIAS)

                            qr = qrcode.make(fee_rec_no)
                            qr = trim(qr)
                            qr = qr.resize((136, 136), Image.NEAREST)

                            draw = ImageDraw.Draw(img)
                            font = ImageFont.truetype(settings.FILE_PATH + "OpenSans-Bold.ttf", 36)
                            font2 = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 36)

                            font7 = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 170)

                            font3 = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 36)
                            font4 = ImageFont.truetype(settings.FILE_PATH + "OpenSans-Bold.ttf", 36)

                            font5 = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 32)
                            font6 = ImageFont.truetype(settings.FILE_PATH + "OpenSans-Bold.ttf", 32)

                            if q_check[0]['cancelled_status'] == 'Y':
                                txt = Image.new('L', (1050, 170))
                                d = ImageDraw.Draw(txt)
                                d.text((0, 0), "CANCELLED",  font=font7, fill=255)
                                w = txt.rotate(36,  expand=1)

                                img.paste(ImageOps.colorize(w, (0, 0, 0), (196, 196, 196)), (270, 640),  w)

                            draw.text((1130, 410), receipt_name, (0, 0, 0), font=font)
                            draw.text((115, 510), "Receipt No.:", (0, 0, 0), font=font)
                            draw.text((115, 560), "Name:", (0, 0, 0), font=font)
                            draw.text((115, 610), "Father's Name:", (0, 0, 0), font=font)
                            draw.text((115, 660), "Roll No.:", (0, 0, 0), font=font)
                            draw.text((115, 710), "Course:", (0, 0, 0), font=font)

                            draw.text((400, 515), fee_rec_no, (0, 0, 0), font=font2)
                            draw.text((400, 565), q_check[0]['uniq_id__name'] + " (" + q_check[0]['uniq_id__gender__value'][0] + ")", (0, 0, 0), font=font2)
                            draw.text((400, 615), fname, (0, 0, 0), font=font2)
                            if stu_det[0]['uniq_id__uni_roll_no'] is not None:
                                draw.text((275, 665), str(stu_det[0]['uniq_id__uni_roll_no']), (0, 0, 0), font=font2)
                            else:
                                draw.text((275, 665), str(stu_det[0]['uniq_id__exam_roll_no']), (0, 0, 0), font=font2)

                            draw.text((275, 715), stu_det[0]['sem__dept__course__value'], (0, 0, 0), font=font2)

                            draw.text((650, 510), "Session:", (0, 0, 0), font=font)
                            draw.text((800, 515), q_check[0]['session__session'].split('-')[0] + '-' + q_check[0]['session__session'].split('-')[1][-2:], (0, 0, 0), font=font2)

                            draw.text((1050, 510), "Date:", (0, 0, 0), font=font)
                            draw.text((1150, 515), str(date), (0, 0, 0), font=font2)

                            img.paste(qr, (1175, 565))
                            draw.text((650, 660), "Batch:", (0, 0, 0), font=font)
                            draw.text((770, 665), str(stu_det[0]['uniq_id__batch_from']) + "-" + str(stu_det[0]['uniq_id__batch_to'])[-2:], (0, 0, 0), font=font2)

                            draw.text((1000, 710), "Branch:", (0, 0, 0), font=font)
                            draw.text((1150, 715), stu_det[0]['uniq_id__dept_detail__dept__value'], (0, 0, 0), font=font2)

                            draw.text((1000, 660), "Year:", (0, 0, 0), font=font)
                            draw.text((1100, 665), str(stu_det[0]['year']), (0, 0, 0), font=font2)

                            draw.text((115, 860), "Particulars", (0, 0, 0), font=font)
                            draw.text((1130, 860), "Amount (Rs.)", (0, 0, 0), font=font)

                            y = 950
                            if q_check[0]['receipt_type'] == 'N':
                                for comp in fee_comp_details:
                                    if comp['sub_component_value'] > 0:
                                        draw.text((115, y), comp['fee_sub_component__value'].replace("(ONE TIME)", "").title(), (0, 0, 0), font=font3)
                                        draw.text((1170, y), str(float(comp['sub_component_value'])) + "0", (0, 0, 0), font=font3)
                                        y += 50
                            elif q_check[0]['receipt_type'] == 'D':
                                draw.text((115, y), q_check[0]['prev_fee_rec_no'], (0, 0, 0), font=font3)
                                draw.text((1170, y), str(q_check[0]['actual_fee']) + "0", (0, 0, 0), font=font3)
                                y += 50

                            y += 20
                            draw.line((110, y, 1350, y), fill=(0, 0, 0), width=5)

                            y += 20
                            draw.text((115, y), "Total Fee", (0, 0, 0), font=font4)
                            draw.text((1170, y), str(q_check[0]['actual_fee']) + "0", (0, 0, 0), font=font3)

                            y += 50
                            draw.text((115, y), "Amount Paid", (0, 0, 0), font=font4)
                            draw.text((1170, y), str(q_check[0]['paid_fee']) + "0", (0, 0, 0), font=font3)

                            y += 50
                            if q_check[0]['due_value'] is not None and q_check[0]['due_value'] > 0:
                                draw.text((115, y), "Due Amount", (0, 0, 0), font=font4)
                                draw.text((1170, y), str(q_check[0]['due_value']) + "0", (0, 0, 0), font=font3)
                                y += 50

                            elif q_check[0]['refund_value'] is not None and q_check[0]['refund_value'] > 0:
                                draw.text((115, y), "Refund Amount", (0, 0, 0), font=font4)
                                draw.text((1170, y), str(q_check[0]['refund_value']) + "0", (0, 0, 0), font=font3)
                                y += 50

                            y += 10
                            draw.line((110, y, 1350, y), fill=(0, 0, 0), width=5)

                            y += 20
                            y -= 50
                            i = 0
                            x1 = 115
                            x2 = 400
                            for mop in q_mop_details:
                                if i % 2 == 0:
                                    x1 = 115
                                    x2 = 400
                                    y += 50
                                else:
                                    x1 = 885
                                    x2 = 1170
                                i += 1

                                if 'DATE' in mop['MOPcomponent__value']:
                                    try:
                                        mop['value'] = ((datetime.strptime(str(mop['value']).split('T')[0], "%Y-%m-%d")) + relativedelta(days=+1)).strftime("%d-%m-%Y")
                                    except:
                                        try:
                                            mop['value'] = ((datetime.strptime(str(mop['value']), "%Y-%m-%d")) + relativedelta(days=+1)).strftime("%d-%m-%Y")
                                        except:
                                            try:
                                                mop['value'] = ((datetime.strptime(str(mop['value']), "%d-%m-%Y")) + relativedelta(days=+1)).strftime("%d-%m-%Y")
                                            except:
                                                mop['value'] = '---'
                                if 'DROPDOWN' in mop['MOPcomponent__value']:
                                    draw.text((x1, y), str(mop['MOPcomponent__value']).replace("(DROPDOWN)", "").title(), (0, 0, 0), font=font6)
                                else:
                                    draw.text((x1, y), str(mop['MOPcomponent__value']).title(), (0, 0, 0), font=font6)

                                # draw.text((x1, y), str(mop['MOPcomponent__value']).title(), (0, 0, 0), font=font6)
                                if 'AMOUNT' in mop['MOPcomponent__value']:
                                    if "." not in str(mop['value']):
                                        mop['value'] = str(mop['value']) + ".00"
                                    draw.text((x2, y + 5), str(mop['value']), (0, 0, 0), font=font5)
                                elif 'DROPDOWN' in mop['MOPcomponent__value']:
                                    mop['value'] = list(StudentAccountsDropdown.objects.filter(sno=mop['value']).values())
                                    if len(mop['value']) > 0:
                                        draw.text((x2, y + 5), str(mop['value'][-1]['value']), (0, 0, 0), font=font5)
                                else:
                                    draw.text((x2, y + 5), str(mop['value']), (0, 0, 0), font=font5)

                            final_img_width = min(img.size[0], 1478)
                            final_img_height = min(img.size[1], 2100)
                            tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")

                            index = 0
                            margin_left = 0
                            margin_top = 0

                            x = index // 2 * (tmp_image.size[0] // 2)
                            y = index % 2 * (tmp_image.size[1] // 2)
                            w, h = img.size
                            tmp_image.paste(img, (x, y, x + w, y + h))

                            tmp_image.save(settings.FILE_PATH + filename, "PDF", resolution=250.0)

                            with open(settings.FILE_PATH + filename, 'rb') as pdf:
                                response = HttpResponse(pdf, content_type='application/pdf')
                                response['Content-Disposition'] = 'inline;filename=some_file.pdf'

                                return response
                                pdf.closed

                            status = 200
                            return response

                        else:
                            status = 403
                            msg = "Fee Receipt Not Found"
                else:
                    status = 502
                    msg = "Bad Request"
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Not Authorized"
    else:
        status = 500
        msg = "Error"

    data_values = {'msg': msg}
    return JsonResponse(data=data_values, status=status)


def student_registration(request):
    data_values = {}
    msg = ""
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                session = Semtiming.objects.get(uid=request.session['Session_id'])
                session_name = request.session['Session_name']
                uniq_id = request.session['uniq_id']
                if int(session_name[:2]) < 20:
                    return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                if(request.method == 'GET'):
                    studentSession = generate_session_table_name("studentSession_", session_name)
                    StudentFillInsurance = generate_session_table_name("StudentFillInsurance_", session_name)
                    StudentHobbyClubs = generate_session_table_name("StudentHobbyClubs_", session_name)
                    if(request.GET['request_type'] == 'initial_data'):
                        q_check_lock_status = studentSession.objects.filter(uniq_id=uniq_id).values('reg_form_status')
                        if q_check_lock_status[0]['reg_form_status'] == 'LOCK':
                            status = 202
                            msg = 'Please contact your class coordinator to be able to fill your Registration Form.'
                            data_values = {'msg': msg}
                        else:

                            query_sub_types = StudentDropdown.objects.filter(field="SUBJECT TYPE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno', flat=True)
                            sub_data = []
                            for sub in query_sub_types:
                                sub_data.extend(get_subjects(stu_data['sem'], session_name, sub))

                            q_state = EmployeeDropdown.objects.filter(field="STATE").exclude(value__isnull=True).values("sno", "value")
                            data_values = {'subjects': sub_data, 'states': list(q_state)}
                            status = 200
                            msg = 'success'
                    elif(request.GET['request_type'] == 'form_data'):
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        q_check_lock_status = studentSession.objects.filter(uniq_id=uniq_id).values('reg_form_status')
                        if q_check_lock_status[0]['reg_form_status'] == 'LOCK':
                            status = 202
                            msg = 'Please contact your class coordinator to be able to fill your Registration Form.'
                            data_values = {'msg': msg}
                        else:
                            stu_data = get_profile(uniq_id, session_name)
                            internsip_data=get_Internship_details(uniq_id,session_name)
                            # insurance_data=get_insurance_data(uniq_id,session_name)
                            query_sub_types = StudentDropdown.objects.filter(field="SUBJECT TYPE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno', flat=True)
                            sub_data = []
                            for sub in query_sub_types:
                                sub_data.extend(get_subjects(stu_data['sem'], session_name, sub))

                            q_state = EmployeeDropdown.objects.filter(field="STATE").exclude(value__isnull=True).values("sno", "value")

                            qry = StudentAcademicsDropdown.objects.filter(field="HOBBY CLUBS").values('sno')
                            qry1 = StudentAcademicsDropdown.objects.filter(pid=qry[0]['sno']).values('sno', 'field')
                            qry4 = []
                            for i in qry1:
                                qry2 = list(StudentAcademicsDropdown.objects.filter(pid=i['sno']).values('field', 'value', 'sno'))
                                qry4.append({'category': i['field'], 'clubs_list': qry2})
                            data_values = {'profile_data': stu_data, 'subjects': sub_data, 'states': list(q_state), 'stu_det': qry4,'intern_data':internsip_data}
                            status = 200
                            msg = 'success'
                    elif(request.GET['request_type'] == 'after_submit_form'):
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

                        q_check_lock_status = studentSession.objects.filter(uniq_id=uniq_id).values('registration_status')
                        if q_check_lock_status[0]['registration_status'] == 0:
                            status = 202
                            msg = 'Please fill sem registration form'
                            data_values = {'msg': msg}
                        else:
                            q_sec = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id')

                            sub_selected = []
                            sub = SubjectInfo.objects.filter(sem=q_sec[0]['section__sem_id'], subject_type__value='THEORY').exclude(status='DELETE').values('subject_type__value', 'subject_unit__value', 'sub_alpha_code', 'sub_num_code', 'sub_name', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'no_of_units', 'id')

                            for s in sub:
                                sub_selected.append({'subject_id__sub_alpha_code': s['sub_alpha_code'], 'subject_id__sub_num_code': s['sub_num_code'], 'subject_id__sub_name': s['sub_name']})
                            data_values = {'subjects': list(sub_selected)}
                            status = 200
                            msg = 'success'
                    elif(request.GET['request_type'] == 'print_data'):
                        stu_det = studentSession.objects.filter(uniq_id=uniq_id).values('reg_date_time', 'year', 'uniq_id__name', 'uniq_id__stu_type__value', 'sem__dept__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__email_id', 'sem__sem', 'section', 'mob', 'uniq_id__admission_category__value', 'uniq_id__caste__value', 'section__section')
                        personal_details = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('religion__value', 'fname', 'mob_sec', 'dob', 'image_path', 'aadhar_num', 'bank_acc_no', 'pan_no', 'uan_no', 'physically_disabled', 'bg', 'marital_status', 'nationality', 'religion', 'mname', 'caste_name', 'nation_other')
                        insurance_details = StudentFillInsurance.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('nominee_name', 'nominee_relation', 'insurer_name', 'insurer_dob', 'insurer_aadhar_num', 'insurer_occupation', 'insurer_nominee_name', 'insurer_relation')
                        bank_details = StudentBankDetails.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('acc_name', 'acc_num', 'bank_name', 'ifsc_code', 'branch', 'address')
                        family_details = StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values('father_mob', 'mother_mob', 'father_occupation', 'mother_occupation', 'mother_uan_no', 'mother_uan_no', 'father_uan_no')
                        hobby_club = list(StudentHobbyClubs.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('hobby_club__value', 'hobby_club__field'))
                        internship_data=list(StudentInternshipsTaken.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('taken','internship'))
                        data_values = {'stu_det': list(stu_det), 'personal_details': list(personal_details), 'insurance_details': list(insurance_details), 'bank_details': list(bank_details), 'family_details': list(family_details), 'hobby_club': hobby_club,'internship_data':internship_data}
                        status = 200
                    # elif(request.GET['request_type'] == 'hobby_club_dropdown'):
                    #     qry=StudentAcademicsDropdown.objects.filter(field="HOBBY CLUBS").values('sno')
                    #     qry1=StudentAcademicsDropdown.objects.filter(pid=qry[0]['sno']).values('sno')
                    #     qry2=StudentAcademicsDropdown.objects.filter(pid=qry1[0]['sno']).values('field','value','sno')
                    #     data_values = {'stu_det': list(qry2)}
                    #     status = 200
                elif(request.method == 'POST'):
                    studentSession = generate_session_table_name("studentSession_", session_name)
                    # StudentFillSubjects = generate_session_table_name("StudentFillSubjects_", session_name)
                    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
                    StudentHobbyClubs = generate_session_table_name("StudentHobbyClubs_", session_name)
                    #######################LOCKING STARTS######################
                    section_li = list(studentSession.objects.filter(uniq_id=uniq_id).values_list('section', flat=True))
                    if check_islocked("REG", section_li, session_name):
                        return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                        ####################LOCKING ENDS##############################
                    q_check_lock_status = studentSession.objects.filter(uniq_id=uniq_id).values('reg_form_status')
                    if q_check_lock_status[0]['reg_form_status'] == 'LOCK':
                        status = 202
                        msg = 'Registration form is Locked. Please contact your class coordinator.'
                        data_values = {'msg': msg}
                    else:

                        data = json.loads(request.body)
                        c_city = data['c_city']
                        c_district = data['c_district']
                        nominee_name = data['nominee_name']
                        nominee_relation = data['nominee_relation']
                        insurer_name = data['insurer_name']
                        insurer_relation = data['insurer_relation']
                        insurer_dob = data['insurer_dob']
                        insurer_occuptation = data['insurer_occuptation']
                        insurer_aadhar_num = data['insurer_aadhar_num']
                        insurer_nominee_name = data['insurer_nominee_name']
                        hobby_club = data['hobby_club1']
                        # intern_data=data['internship']
                        # data_check=insert_intern_taken(uniq_id,intern_data,session_name)

                        if all(k in data for k in ("nominee_name", "nominee_relation", "insurer_name", "insurer_relation", "insurer_dob", "insurer_occuptation", "insurer_aadhar_num", "insurer_nominee_name", "hobby_club1")):
                            StudentFillInsurance = generate_session_table_name("StudentFillInsurance_", session_name)
                            if data["c_state_id"] is None:
                                c_state_id = None
                            else:
                                c_state_id = EmployeeDropdown.objects.get(sno=data['c_state_id'])
                            c_pincode = data['c_pincode']
                            c_add2 = data['c_add2']
                            c_add1 = data['c_add1']

                            mob = data['mob']
                            email = data['email']
                            if len(hobby_club) > 0:
                                # objs = (StudentFillSubjects(uniq_id=studentSession.objects.get(uniq_id=uniq_id),subject_id=SubjectInfo.objects.get(id=sub)) for sub in subjects)
                                # q_ins = StudentFillSubjects.objects.bulk_create(objs)
                                q_upd_em = StudentPrimDetail.objects.filter(uniq_id=uniq_id).update(email_id=email)
                                q_address_update = StudentAddress.objects.filter(uniq_id=uniq_id).update(c_city=c_city, c_district=c_district, c_state=c_state_id, c_pincode=c_pincode, c_add2=c_add2, c_add1=c_add1)
                                q_insert_insurance = StudentFillInsurance.objects.update_or_create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), status="INSERT", defaults={'nominee_name': nominee_name, 'nominee_relation': nominee_relation, 'insurer_name': insurer_name, 'insurer_relation': insurer_relation, 'insurer_dob': insurer_dob, 'insurer_occupation': insurer_occuptation, 'insurer_aadhar_num': insurer_aadhar_num, 'insurer_nominee_name': insurer_nominee_name})
                                q_delete_old_hobby_club = StudentHobbyClubs.objects.filter(uniq_id=uniq_id).update(status="DELETE")
                                q_insert_hobbyclub_objs = (StudentHobbyClubs(uniq_id=studentSession.objects.get(uniq_id=uniq_id), hobby_club=StudentAcademicsDropdown.objects.get(sno=x)) for x in hobby_club)
                                print(hobby_club)
                                bulk_create = StudentHobbyClubs.objects.bulk_create(q_insert_hobbyclub_objs)
                                if q_insert_insurance:
                                    q_update_mob = studentSession.objects.filter(uniq_id=uniq_id).update(mob=mob, registration_status=1, reg_form_status='LOCK', reg_date_time=datetime.now())
                                    if q_update_mob:
                                        status = 200
                                        data_values = {'msg': 'Registration Form Successfully Submitted'}
                                    else:
                                        status = 202
                                        data_values = {'msg': 'Registration Form Could not be Submitted'}
                                else:
                                    status = 202
                                    data_values = {'msg': 'Registration Form Could not be Submitted'}

                            else:
                                status = 202
                                data_values = {'msg': 'Please fill hobby club details'}
                        else:
                            status = 202
                            data_values = {'msg': 'Please fill all details'}

                else:
                    status = 502
                    msg = "Bad Request"
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Not Authorized"
    else:
        status = 500
        msg = "Error"
    return JsonResponse(data=data_values, status=status)


def printDeclaration(request):
    data_values = {}
    msg = ""
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                session = Semtiming.objects.get(uid=request.session['Session_id'])
                session_name = request.session['Session_name']
                if(request.method == 'GET'):
                    uniq_id = request.session['uniq_id']
                    return Declarationpdf(uniq_id, session_name)
                    # pdf = open(settings.FILE_PATH+filename)
                    # pdf.seek(0)
                    # response = HttpResponse(pdf.read(), content_type="application/pdf")
                    status = 200
                    return response
                else:
                    status = 502
                    msg = "Bad Request"
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Not Authorized"
    else:
        status = 500
        msg = "Error"

    data_values = {'msg': msg}
    return JsonResponse(data=data_values, status=status)

    # /////////////////////////// DHRUV START ////////////////////////////


def small_change(request):
    data_values = {}
    msg = ""
    status = 403
    # print(request.GET)

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                if(request.method == 'GET'):
                    uniq_id = request.session['uniq_id']
                    if request.GET['request_type'] == 'DOB':
                        dob = datetime.strptime(str(request.GET['DATE']).split('T')[0], "%Y-%m-%d").date()
                        qry = StudentPerDetail.objects.filter(uniq_id=uniq_id).update(dob=dob)
                        qry = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('dob')
                        data_values['data'] = qry[0]['dob']
                        status = 200
                        msg = "Success"
                else:
                    status = 502
                    msg = "Bad Request"
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Not Authorized"
    else:
        status = 500
        msg = "Error"
    data_values['msg'] = msg
    return JsonResponse(data=data_values, status=status)

    # /////////////////////////// DHRUV END ////////////////////////////


def StudentBankDetailsChange(request):
    qry = []
    data = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                if request.method == 'GET':
                    if (request.GET['request_type'] == 'get_data'):
                        uniq_id = request.session['uniq_id']
                        data = list(StudentBankDetails.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('acc_name', 'acc_num', 'bank_name', 'ifsc_code', 'branch', 'address'))
                        status = 200

                    if(request.GET['request_type'] == 'send_ifsc'):
                        ifsc = request.GET['ifsc']
                        url = "https://ifsc.razorpay.com/" + ifsc
                        try:
                            response = urllib.request.urlopen(url)
                            data = json.loads(response.read())
                            if(data != 'Not Found'):
                                address = data['ADDRESS'] + ',' + data['STATE']
                                data['ADDRESS'] = address
                            else:
                                data = None
                        except Exception as e:
                            data = None
                        status = 200
                    return JsonResponse(data=data, status=status, safe=False)

                if request.method == 'POST':
                    data = json.loads(request.body)
                    uniq_id = request.session['uniq_id']
                    acc_num = data['acc_num']
                    acc_name = data['acc_name']
                    bank_name = data['bank_name']
                    ifsc_code = data['ifsc_code']
                    branch = data['branch']
                    address = data['address']
                    qry = StudentBankDetails.objects.filter(uniq_id=uniq_id).update(status='DELETE')
                    qry1 = StudentBankDetails.objects.create(acc_name=acc_name, acc_num=acc_num, bank_name=bank_name, ifsc_code=ifsc_code, branch=branch, address=address, uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), status='INSERT')
                    status = 200
                    data_values = {'msg': "Data Added Succesfully"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values)


def student_marks(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            data = []
            data_values = {}
            session_name = request.session['Session_name']
            QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
            QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)
            StudentMarks = generate_session_table_name("StudentMarks_", session_name)
            Marks = generate_session_table_name("Marks_", session_name)
            SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
            studentSession = generate_session_table_name("studentSession_", session_name)
            if request.session['hash3'] == 'Student':
                if request.method == 'GET':
                    if (request.GET['request_type'] == 'get_marks'):
                        uniq_id = request.session['uniq_id']
                        sem_type = request.session['sem_type']
                        exam_id = request.GET['exam_id']
                        # print(exam_id)
                        if(exam_id != "-1"):
                            qry = list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('dept_detail', 'join_year'))
                            query = list(studentSession.objects.filter(uniq_id=uniq_id).values('sem'))
                            format_id = list(QuesPaperApplicableOn.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id__exam_id=exam_id, sem=query[0]['sem']).values_list('ques_paper_id', flat=True))
                            max_marks = {}
                            if len(format_id) == 0:
                                maximum = 60
                                max_marks['total_marks'] = 60
                            else:
                                max_marks = QuesPaperSectionDetails.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id=format_id[0]).aggregate(total_marks=Sum('max_marks'))

                            subject = list(SubjectInfo.objects.exclude(subject_type__value='LAB').exclude(subject_type__value='VALUE ADDED COURSE').exclude(status="DELETE").filter(sem=query[0]['sem']).values('id', 'sub_name', 'sub_alpha_code', 'sub_num_code').annotate(ids=F('id')))
                            avg_marks_obt = 0.0
                            avg_total_marks = 0.0
                            for s in subject:
                                subject_name = s['sub_name'] + ' (' + s['sub_alpha_code'] + '-' + s['sub_num_code'] + ')'
                                qry = StudentMarks.objects.exclude(status='DELETE').filter(uniq_id=uniq_id, marks_id__exam_id=exam_id, marks_id__subject_id=s['id']).aggregate(marks_obtained=Sum('marks'))
                                qry1 = StudentMarks.objects.exclude(status="DELETE").filter(uniq_id=uniq_id, marks_id__exam_id=exam_id, marks_id__subject_id=s['id']).values('present_status', 'ques_id__section_id__ques_paper_id')
                                if qry['marks_obtained'] == None:
                                    if len(qry1) != 0:
                                        qry['marks_obtained'] = 'P'
                                # if len(qry1) == 0:
                                    # print("vrinda")
                                else:
                                    # ########################################################
                                    format_id = list(QuesPaperApplicableOn.objects.filter(ques_paper_id__exam_id=exam_id, sem=query[0]['sem'], ques_paper_id=qry1[0]['ques_id__section_id__ques_paper_id']).values_list('ques_paper_id', flat=True))
                                    max_marks = {}
                                    if len(format_id) == 0:
                                        maximum = 60
                                        max_marks['total_marks'] = 60
                                    else:
                                        max_marks = QuesPaperSectionDetails.objects.filter(ques_paper_id=format_id[0]).aggregate(total_marks=Sum('max_marks'))
                                    # #########################################################

                                    if qry1[0]['present_status'] == 'A':
                                        qry['marks_obtained'] = qry1[0]['present_status']
                                        avg_total_marks = avg_total_marks + max_marks['total_marks']
                                    elif qry1[0]['present_status'] == 'D':
                                        qry['marks_obtained'] = qry1[0]['present_status']
                                        avg_total_marks = avg_total_marks + max_marks['total_marks']
                                    elif qry1[0]['present_status'] == 'P':
                                        # print(subject_name)
                                        if type(qry['marks_obtained']) == type(avg_marks_obt) and max_marks is not None:
                                            avg_marks_obt = avg_marks_obt + qry['marks_obtained']
                                            avg_total_marks = avg_total_marks + max_marks['total_marks']
                                        elif max_marks is not None:
                                            avg_marks_obt = avg_marks_obt
                                            avg_total_marks = avg_total_marks + max_marks['total_marks']

                                if len(format_id) == 0:
                                    data.append({'subject_name': subject_name, 'marks_obtained': qry.get('marks_obtained', 0), 'total_marks': maximum})
                                else:
                                    query = list(studentSession.objects.filter(uniq_id=uniq_id).values('sem'))
                                    data.append({'subject_name': subject_name, 'marks_obtained': qry.get('marks_obtained', 0), 'total_marks': max_marks['total_marks']})
                            data_values = {'data': data, 'avg_marks_obt': avg_marks_obt, 'avg_total_marks': avg_total_marks}
                            status = 200
                        # else:
                        #   query = studentSession.objects.filter(uniq_id=uniq_id).values('sem')
                        #   subject_details = list(SubjectInfo.objects.exclude(status="DELETE").filter(sem=query[0]['sem']).values('max_ct_marks', 'max_ta_marks', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'id', 'max_att_marks', 'subject_type', 'sem').annotate(ids=F('id')))
                        #   temp_data = single_student_ct_marks(session_name, uniq_id, subject_details, {})
                        #   print(temp_data)
                        #   data_values = temp_data
                        #   status = 200
                        else:
                            query = studentSession.objects.filter(uniq_id=uniq_id).values('sem')
                            subject_details = list(SubjectInfo.objects.exclude(status="DELETE").filter(sem=query[0]['sem']).values('max_ct_marks', 'max_ta_marks', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'id', 'max_att_marks', 'subject_type', 'subject_type__value', 'sem').annotate(ids=F('id')))
                            # temp_data = single_student_ct_marks(session_name, uniq_id, subject_details, {})
                            temp_data = get_single_student_internal_marks(uniq_id, query[0]['sem'], subject_details, session_name)
                            data_values = temp_data
                            status = 200
                    elif (request.GET['request_type'] == 'get_exams'):
                        uniq_id = request.session['uniq_id']
                        qry_section_id = studentSession.objects.filter(uniq_id=uniq_id).values('section')
                        qry_exam_name = list(Marks.objects.filter(section=qry_section_id[0]['section']).exclude(status='DELETE').annotate(sno=F('exam_id'), value=F('exam_id__value')).values('sno', 'value').distinct().order_by('sno'))
                        # qry_exam_name.append({'sno': int(-1), 'value': 'INTERNAL MARKS'})
                        data_values = list(qry_exam_name)

                        status = 200
                    return JsonResponse(data=data_values, status=status, safe=False)

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values)


def Activities_Student_Portal(request):
    data_values = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                session_name = request.session['Session_name']
                StudentActivities = generate_session_table_name("StudentActivities_", session_name)
                studentSession = generate_session_table_name("studentSession_", session_name)
                ActivitiesApproval = generate_session_table_name("ActivitiesApproval_", session_name)
                if request.method == 'POST':
                    data = json.loads(request.body)
                    uniq_id = request.session['uniq_id']
                    activity_type = data['activity_type']
                    Date_of_event = datetime.strptime(str(data['Date_of_event']).split('T')[0], "%Y-%m-%d").date()
                    Organized_by = data['Organized_by']
                    venue_address = data['venue_address']
                    venue_city = data['venue_city']
                    venue_state = data['venue_state']
                    venue_country = data['venue_country']
                    Description = data['Description']
                    Document = data['Document']

                    if Document == "":
                        qry = StudentActivities.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), activity_type=StudentAcademicsDropdown.objects.get(sno=activity_type), date_of_event=Date_of_event, organised_by=Organized_by, venue_address=venue_address, venue_city=venue_city, description=Description, venue_state=venue_state, venue_country=venue_country)
                    else:
                        qry = StudentActivities.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), activity_type=StudentAcademicsDropdown.objects.get(sno=activity_type), date_of_event=Date_of_event, organised_by=Organized_by, venue_address=venue_address, venue_city=venue_city, description=Description, venue_state=venue_state, venue_country=venue_country, student_document=Document)

                    qry1 = ActivitiesApproval.objects.create(Activities_detail=StudentActivities.objects.get(id=qry.id))
                    if qry:
                        data_values = {'msg': 'Data Succesfully Inserted'}
                    else:
                        data_values = {'msg': 'Data Could not be Inserted'}
                    status = 200

                elif request.method == 'GET':
                    uniq_id = request.session['uniq_id']
                    qry = list(ActivitiesApproval.objects.filter(Activities_detail__uniq_id=uniq_id).exclude(status='DELETE').exclude(Activities_detail__status='DELETE').values('Activities_detail__id', 'Activities_detail__date_of_event', 'Activities_detail__organised_by', 'Activities_detail__venue_address', 'Activities_detail__venue_city', 'Activities_detail__description', 'Activities_detail__student_document', 'Activities_detail__time_stamp', 'Activities_detail__venue_state', 'Activities_detail__venue_country', 'Activities_detail__activity_type', 'Activities_detail__activity_type__value', 'appoval_status'))
                    for q in qry:
                        if(q['Activities_detail__student_document'] == None):
                            q['Activities_detail__student_document'] = ""
                    data_values = qry
                    status = 200

                elif request.method == 'PUT':
                    uniq_id = request.session['uniq_id']
                    data = json.loads(request.body)
                    id = data['id']
                    activity_type = data['activity_type']
                    Date_of_event = datetime.strptime(str(data['Date_of_event']).split('T')[0], "%Y-%m-%d").date()
                    Organized_by = data['Organized_by']
                    venue_address = data['venue_address']
                    venue_city = data['venue_city']
                    venue_state = data['venue_state']
                    venue_country = data['venue_country']
                    Description = data['Description']
                    Document = data['Document']
                    qry1 = ActivitiesApproval.objects.filter(Activities_detail__id=id, appoval_status='PENDING').values('appoval_status')
                    if qry1[0]['appoval_status'] == 'PENDING':
                        qry = StudentActivities.objects.filter(id=id).update(status='DELETE')
                        qry4 = ActivitiesApproval.objects.filter(Activities_detail__id=id).update(status='DELETE')
                        qry2 = StudentActivities.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), activity_type=StudentAcademicsDropdown.objects.get(sno=activity_type), date_of_event=Date_of_event, organised_by=Organized_by, venue_address=venue_address, venue_city=venue_city, description=Description, student_document=Document, venue_state=venue_state, venue_country=venue_country)
                        qry3 = ActivitiesApproval.objects.create(Activities_detail=StudentActivities.objects.get(id=qry2.id))
                        data_values = {'msg': 'Data Succesfully Updated'}
                    else:
                        data_values = {'msg': 'Data Could not be Updated'}
                    status = 200

                elif request.method == 'DELETE':
                    ActivitiesApproval = generate_session_table_name("ActivitiesApproval_", session_name)
                    data = json.loads(request.body)
                    id = data['id']
                    qry = ActivitiesApproval.objects.filter(Activities_detail__id=id, appoval_status='PENDING').values('appoval_status')
                    if qry[0]['appoval_status'] == 'PENDING':
                        qry1 = StudentActivities.objects.filter(id=id).update(status='DELETE')
                        qry4 = ActivitiesApproval.objects.filter(Activities_detail__id=id).update(status='DELETE')
                        data_values = {'msg': 'Data Succesfully Deleted'}
                    else:
                        data_values = {'msg': 'Data Could not be Deleted'}
                    status = 200

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)


def MentorCardOnPortal(request):
    qry = []
    data_values = []
    Sessions = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                if request.method == 'GET':
                    if (request.GET['request_type'] == 'get_data'):
                        cur_year=session_name[:-1]
                        cur_year=datetime.strptime(cur_year,'%Y')
                        if(cur_year<datetime.strptime("1819",'%Y')):
                            return
                        studentSession = generate_session_table_name("studentSession_", session_name)
                        IncidentApproval = generate_session_table_name('IncidentApproval_', session_name)
                        uniq_id = request.session['uniq_id']
                        personal_data = get_profile(uniq_id, session_name)
                        academic_data = smm.views.smm_settings_views.student_academic_details(uniq_id, session_name)
                        stu_reg_date = list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('date_of_add', 'batch_from'))
                        all_ses = list(Semtiming.objects.values('sem_end', 'session', 'session_name', 'uid', 'sem_start'))
                        i = 0
                        date = list(Semtiming.objects.filter(session_name="1819o").values('sem_start', 'session'))
                        for s in all_ses:
                            session_year = int(s['session'].split('-')[0])
                            # if s['sem_start'] > stu_reg_date[0]['date_of_add'] and s['sem_start'] >= date[0]['sem_start']:
                            if session_year >= int(stu_reg_date[0]['batch_from']) and s['sem_start'] >= date[0]['sem_start'] :
                                Sessions.append({})
                                Sessions[i]['uid'] = s['uid']
                                Sessions[i]['session_name'] = s['session_name']
                                i = i + 1
                        data = {}
                        data1 = {}
                        print(Sessions, 'Sessions')
                        for ses in Sessions:
                            studentSession = generate_session_table_name("studentSession_", ses['session_name'])
                            details = list(studentSession.objects.filter(uniq_id=uniq_id).values('uniq_id'))
                            if len(details) == 0:
                                continue
                            else:
                                UniversityWise = smm.views.smm_settings_views.UnivMarksInfo(uniq_id, ses['session_name'])
                                semester_wise = smm.views.smm_settings_views.SemesterWisePerformance(uniq_id, ses['session_name'], ses['uid'])
                                data[ses['session_name']] = semester_wise
                                data1[ses['session_name']] = UniversityWise
                            if ses['session_name']==session_name:
                                break

                        q_activity = smm.views.smm_settings_views.get_student_activities(uniq_id, session_name)

                        if sem_type == 'even':
                            qry = list(Semtiming.objects.filter(uid=session_id).values_list('session', flat=True))
                            sem_odd = list(Semtiming.objects.filter(session=qry[0], sem_type='odd').values('uid'))
                            session_id = sem_odd[0]['uid']
                        residential_status = SubmitFee.objects.filter(cancelled_status='N', uniq_id=uniq_id, status='INSERT', fee_rec_no__contains='H', session=session_id).exclude(id__in=RefundFee.objects.values_list('fee_id', flat=True)).exclude(status__contains='DELETE').values()
                        if(len(residential_status) > 0):
                            res_status = 'HOSTELLER'
                        else:
                            res_status = 'DAY SCHOLAR'
                        personal_data['res_status'] = res_status
                        indisciplinary = list(IncidentApproval.objects.filter(incident_detail__uniq_id=uniq_id).exclude(status='DELETE').exclude(incident_detail__incident__status='DELETE').exclude(incident_detail__status='DELETE').values('incident_detail__incident__date_of_incident', 'incident_detail__incident__description', 'incident_detail__incident__incident_document', 'incident_detail__incident__added_by', 'incident_detail__uniq_id', 'incident_detail__action', 'incident_detail__comm_to_parent', 'incident_detail__student_document', 'remark', 'appoval_status', 'approved_by', 'incident_detail__uniq_id__session__session', 'incident_detail__uniq_id__sem__sem', 'incident_detail__uniq_id__session__sem_type'))

                        data_values.append({'Personal': personal_data, 'Academic': academic_data, 'UniversityWise': data1, 'SemesterWise': data, 'Activities': list(q_activity), 'Indisciplinary': indisciplinary})

                        status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)


def HostelAppForm(request):
    Sessions = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                uniq_id = request.session['uniq_id']
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                session = request.session['Session']
                if int(session_name[:2]) < 19 or 'even' in str(sem_type):
                    return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
                HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
                HostelSeaterPriority = generate_session_table_name('HostelSeaterPriority_', session_name)
                HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
                HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)
                HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)
                studentSession = generate_session_table_name("studentSession_", session_name)
                
                if request.method == 'GET':
                    if (request.GET['request_type'] == 'form_data'):
                        
                        qry_check = studentSession.objects.filter(uniq_id=uniq_id).values()
                        if len(qry_check) == 0:
                            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                        qry_check = HostelSeatAlloted.objects.filter(uniq_id=uniq_id, status="INSERT").values()
                        if len(qry_check) > 0:
                            return functions.RESPONSE({'msg': 'You cannot fill this form since you have already been alloted seat'}, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                        locking_status = studenthostel.views.hostel_function.check_isLocked('S', uniq_id, session_name)
                        details = studenthostel.views.hostel_function.get_student_details(uniq_id, session_name, {}, sem_type, session_id)
                        course_dur = list(CourseDetail.objects.filter(course=details[0]['sem__dept__course']).values_list('course_duration', flat=True).distinct())
                        if locking_status == True:
                            details[0]['is_locked'] = False
                        else:
                            details[0]['is_locked'] = True
                            details[0]['msg'] = 'Portal is locked'

                        details[0]['is_eligible'] = "Y"
                        app_check = list(HostelStudentAppliction.objects.filter(uniq_id=uniq_id, current_status="PENDING").exclude(status='DELETE').values_list('id', flat=True))
                        if len(app_check) > 0:
                            details[0]['already_filled'] = True
                            details[0]['app_id'] = app_check[0]
                        else:
                            details[0]['already_filled'] = False
                            details[0]['app_id'] = None

                        new_session = session.split('-')
                        new_session1 = str(int(new_session[0])-1) + '-' + str(int(new_session[1])-1) # FOR PREVIOUS SESSION ATTENDANCE AND MARKS
                        qry = list(Semtiming.objects.filter(session=new_session1).values('uid', 'session_name', 'sem_start', 'sem_end', 'sem_type'))
                        att_per = 0.0
                        total_marks = 0.0
                        total_marks_obt = 0.0
                        count = 0
                        details[0]['att'] = {}
                        for q in qry:
                            i = 0
                            sub_id = []
                            max_marks = 0.0
                            total_internal = 0.0
                            total_external = 0.0
                            attendance = 0.0
                            att_category = []
                            att_type = get_sub_attendance_type(q['uid'])
                            att_type_li = [t['sno'] for t in att_type]
                            studentSession = generate_session_table_name("studentSession_", q['session_name'])
                            if 'even' in q['sem_type']:
                                end_date = datetime.strptime(str('2020-03-06'), "%Y-%m-%d").date()
                            else:
                                end_date = q['sem_end']
                            q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
                            subjects = get_student_subjects(q_att_date[0]['section__sem_id'], q['session_name'])
                            query = get_student_attendance(uniq_id, max(datetime.strptime(str(q['sem_start']), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), end_date, q['uid'], att_type_li, subjects, 1, att_category, q['session_name'])
                            if (query['total'] > 0):
                                attendance = round((query['present_count'] / query['total']) * 100, 2)
                                att_per = att_per + (query['present_count'] / query['total']) * 100
                            else:
                                attendance = 0.0
                            details[0]['att'][q['session_name']] = attendance
                            if q['sem_type'] == 'odd':
                                subjects = get_student_subjects(q_att_date[0]['section__sem_id'], q['session_name'])
                                StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", q['session_name'])
                                for s in subjects:
                                    sub_id.append(s['id'])
                                    if(sub_id[i] == "" or sub_id[i] == "----" or sub_id[i] == None):
                                        sub_id.pop(i)
                                        i = i - 1
                                    i = i + 1
                                marks = StudentUniversityMarks.objects.filter(uniq_id=uniq_id, subject_id__in=sub_id).values('external_marks', 'internal_marks', 'subject_id__max_university_marks', 'subject_id__max_ct_marks', 'subject_id__max_att_marks', 'subject_id__max_ta_marks', 'back_marks')
                                for m in marks:
                                    max_marks = max_marks + float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks'])
                                    try:
                                        if (m['internal_marks'] == '' or m['internal_marks'] == None):
                                            m['internal_marks'] = 0.0
                                            
                                            max_marks = max_marks-(float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks']))
                                        if (m['external_marks'] == '' or m['external_marks'] == None):
                                            m['external_marks'] = 0.0
                                            
                                            max_marks = max_marks - float(m['subject_id__max_university_marks'])
                                        if (m['back_marks'] != None):
                                            m['external_marks'] = float(m['back_marks'])
                                        

                                        case1 = (float(m['internal_marks']) + float(m['external_marks'])) / (float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks'])) * 100
                                        if float(m['subject_id__max_university_marks'])>0:
                                            case2 = float(m['external_marks']) / float(m['subject_id__max_university_marks']) * 100
                                        else:
                                            case2 = 100
                                        
                                        if (case1<40 or case2<30) or m['back_marks'] != None:
                                            count = count + 1
                                            if m['back_marks']!=None:
                                                m['external_marks'] = float(m['back_marks'])
                                        total_internal = total_internal + float(m['internal_marks'])
                                        total_external = total_external + float(m['external_marks'])
                                    except ValueError:
                                        total_internal = total_internal
                                        total_external = total_external
                                    total_marks = max_marks
                                    total_marks_obt = total_external + total_internal
                                details[0]['univ_marks'] = {'Marks': {'Obtained_Marks': total_marks_obt, 'Max_Marks': total_marks}, 'Carry_Over': count}
                        if att_per != 0:
                            average_att = round(att_per, 2) / 2
                        else:
                            average_att = 0.00
                        details[0]['avg_att'] = average_att
                        
                        if details[0]['gender__value'] == 'MALE':
                            hostel_id = studenthostel.views.hostel_function.get_hostel('BOYS', {}, session_id)
                        elif details[0]['gender__value'] == 'FEMALE':
                            hostel_id = studenthostel.views.hostel_function.get_hostel('GIRLS', {}, session_id)
                        

                        h_id = []
                        for h in hostel_id:
                            h_id.append(h['sno'])
                        
                        q1 = list(HostelSetting.objects.filter(branch=details[0]['sem__dept'], year=details[0]['year'], hostel_id__hostel_id__in=h_id).exclude(status="DELETE").values('hostel_id__bed_capacity', 'hostel_id__bed_capacity__value').distinct().order_by("hostel_id__bed_capacity__value"))
                        if len(q1) > 0:
                            details[0]['room_preference'] = q1
                        else:
                            details[0]['room_preference'] = []
                        details[0]['medical_cases'] = studenthostel.views.hostel_function.get_medical_cases({}, session_id)
                        data_values = details[0]
                        status = 200

                    elif (request.GET['request_type'] == 'edit_form'):
                        app_id = request.GET['app_id']
                        seater = list(HostelSeaterPriority.objects.filter(application_id=app_id).exclude(status="DELETE").values('seater', 'seater__value', 'priority').order_by('priority'))
                        medical = list(HostelMedicalCases.objects.filter(student_medical__uniq_id=uniq_id, student_medical__session=session_id).exclude(status="DELETE").values("student_medical__medical_category", "student_medical__medical_category__value", "student_medical__document", "cases", "cases__value").distinct())
                        if len(medical) == 0:
                            medical = None
                            Category = None
                        else:
                            for m in medical:
                                Category = m['student_medical__medical_category__value']
                        if len(seater) == 0:
                            seater = None
                        data_values = ({"Room_preference": seater, "Medical": medical, "Category": Category})
                        status = 200

                elif request.method == "POST":
                    data = json.loads(request.body)
                    agree = data['agree']
                    medical_data = data['medical_data']
                    medical_cases = []
                    medical_doc = []
                    if medical_data != None:
                        for m in medical_data:
                            if m is None:
                                continue
                            medical_cases.append(m['cases'])
                            medical_doc.append(m['document'])
                    room_preference = data['room_preference']
                    attendance = data['attendance']
                    uni_marks = data['univ_marks']
                    marks_obt = uni_marks['Marks']['Obtained_Marks']
                    carry_over = uni_marks['Carry_Over']
                    if marks_obt == 0:
                        marks_obt = None
                    max_marks = uni_marks['Marks']['Max_Marks']
                    if max_marks == 0:
                        max_marks = None

                    if agree == True:
                        locking_status = studenthostel.views.hostel_function.check_isLocked('S', uniq_id, session_name)
                        if locking_status == True:
                            qry = list(HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values_list('id', flat=True))
                            if len(qry) > 0:
                                HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").update(status="DELETE")
                                HostelSeaterPriority.objects.filter(application_id=qry[0]).update(status="DELETE")
                                HostelStudentMedical.objects.filter(uniq_id=uniq_id).update(status="DELETE")
                                q1 = list(HostelStudentMedical.objects.filter(uniq_id=uniq_id, status="DELETE").values_list('id', flat=True).order_by('-id'))
                                if len(q1) > 0:
                                    HostelMedicalCases.objects.filter(student_medical__in=q1).update(status="DELETE")
                                    HostelMedicalApproval.objects.filter(student_medical__in=q1).update(status="DELETE")

                            HostelStudentAppliction.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), current_status="PENDING", attendance_avg=attendance, agree=1, uni_marks_obt=marks_obt, uni_max_marks=max_marks, carry=carry_over)
                            app_id = list(HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values_list('id', flat=True))
                            objs = (HostelSeaterPriority(application_id=HostelStudentAppliction.objects.get(id=app_id[0]), seater=HostelDropdown.objects.get(sno=r), priority=i + 1)for i, r in enumerate(room_preference))
                            create = HostelSeaterPriority.objects.bulk_create(objs)

                            ########## FOR CATEGORY ################
                            query = studenthostel.views.hostel_function.get_medical_category({}, session_id)
                            ########################################
                            if medical_data != None and medical_doc != None and medical_cases != None and None not in medical_data and None not in medical_doc and None not in medical_cases:
                                q2 = (HostelStudentMedical(uniq_id=studentSession.objects.get(uniq_id=uniq_id), medical_category=HostelDropdown.objects.get(sno=query[0]['sno']), document=m, session=Semtiming.objects.get(uid=session_id))for m in medical_doc)
                                if len(medical_doc) > 0:
                                    HostelStudentMedical.objects.bulk_create(q2)
                                medical_id = list(HostelStudentMedical.objects.filter(uniq_id=uniq_id, document__in=medical_doc).exclude(status="DELETE").values_list('id', flat=True))
                                if len(medical_id) > 0:
                                    q3 = (HostelMedicalCases(student_medical=HostelStudentMedical.objects.get(id=medical_id[0]), cases=HostelDropdown.objects.get(sno=m))for m in medical_cases)
                                    if len(medical_cases) > 0:
                                        HostelMedicalCases.objects.bulk_create(q3)
                                    HostelMedicalApproval.objects.create(student_medical=HostelStudentMedical.objects.get(id=medical_id[0]), level=1, approval_status="PENDING")
                            data_values = {'msg': 'Your Hostel Application Form Is Succesfully Filled'}
                            status = 200
                        else:
                            data_values = {'msg': 'Portal is locked'}
                            status = 202
                    else:
                        data_values = {'msg': 'Please agree our terms and conditions'}
                        status = 202
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)


def SurveyFillFeedback(request):
    data_values = []
    Sessions = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                qry = []
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                uniq_id = request.session['uniq_id']
                SurveyAddQuestions = generate_session_table_name("SurveyAddQuestions_", session_name)
                SurveyFillFeedback = generate_session_table_name("SurveyFillFeedback_", session_name)
                studentSession = generate_session_table_name("studentSession_", session_name)
                # StudentSemester=generate_session_table_name("StudentSemester_",session_name)
                if request.method == 'GET':
                    if (request.GET['request_type'] == 'get_data'):

                        sem_id = studentSession.objects.filter(uniq_id=uniq_id).values('sem')
                        qry1 = SurveyFillFeedback.objects.filter(uniq_id=uniq_id, ques_id__survey_id=request.GET['survey_id']).exclude(status__contains='DELETE').values('feedback')
                        qry2 = list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('dept_detail'))
                        po_list = get_po(qry2[0]['dept_detail'], session_name)
                        qry = SurveyAddQuestions.objects.filter(survey_id=StudentAcademicsDropdown.objects.get(sno=request.GET['survey_id']), sem_id=sem_id[0]['sem']).exclude(status__contains='DELETE').values('description', 'question_img', 'survey_id', 'survey_id__value').distinct()

                        for d in qry:
                            data = list(SurveyAddQuestions.objects.filter(sem_id=sem_id[0]['sem'], survey_id=request.GET['survey_id'], description=d['description']).exclude(status='DELETE').values('po_id__description', 'po_id', 'id'))
                            d['po_id__description'] = data

                            for t in d['po_id__description']:
                                d['unique_key'] = t['id']
                                for po in po_list:
                                    if po['description'] == t['po_id__description']:
                                        t['po'] = po['po_level_abbr']
                                        break

                        # for d in qry:
                        #   for po in po_list:
                        #       if po['description'] == d['po_id__description']:
                        #           d['po'] = po['po_level_abbr']
                        #           break
                        if qry1:
                            msg = True
                        else:
                            msg = False

                        data_values = {'data': list(qry), 'msg': msg, 'po_list': po_list}
                        status = 200

                    elif(request.GET['request_type'] == 'get_survey'):
                        #######################LOCKING STARTS######################
                        section_li = studentSession.objects.filter(uniq_id=uniq_id).values_list('section', flat=True)
                        if check_islocked("SUR", section_li, session_name):
                            return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                        #######################LOCKING ENDS######################
                        qry = studentSession.objects.filter(uniq_id=uniq_id).values('sem')
                        survey_list = get_survey_dropdown_by_sem(qry[0]['sem'], session_id, session_name)
                        # survey_list=get_survey_dropdown(session_id)

                        data_values = {'survey_list': survey_list}
                        status = 200

                elif request.method == 'POST':
                    data1 = json.loads(request.body)
                    data1 = data1['data']

                    for x in data1:
                        ques_id = x['ques_id'].split(",")
                        objs = (SurveyFillFeedback(uniq_id=studentSession.objects.get(uniq_id=uniq_id), ques_id=SurveyAddQuestions.objects.get(id=q), feedback=x['feedback']) for q in ques_id)
                        qry = SurveyFillFeedback.objects.bulk_create(objs)
                        if objs:
                            data_values = {'msg': 'Successfully Submitted'}
                            status = 200

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)


def RoomPartnerChoice(request):
    Sessions = []
    data_values = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                uniq_id = request.session['uniq_id']
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                session = request.session['Session']

                if int(session_name[:2]) < 19 or 'even' in str(sem_type):
                    return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                HostelSeatAlloted = generate_session_table_name("HostelSeatAlloted_", session_name)
                studentSession = generate_session_table_name("studentSession_", session_name)
                HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
                HostelRoommatePriority = generate_session_table_name("HostelRoommatePriority_", session_name)

                if request.method == 'GET':
                    if (request.GET['request_type'] == 'form_data'):
                        locking_status = studenthostel.views.hostel_function.check_isLocked('R', uniq_id, session_name)
                        details = studenthostel.views.hostel_function.get_student_details(uniq_id, session_name, {}, sem_type, session_id)
                        course_dur = list(CourseDetail.objects.filter(course=details[0]['sem__dept__course']).values_list('course_duration', flat=True).distinct())
                        qry = HostelSeatAlloted.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('paid_status', 'hostel_part', 'seat_part__value', 'status', 'seat_part')
                        year = studentSession.objects.filter(uniq_id=uniq_id).values_list('year', flat=True)
                        app_id = HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values_list('id', flat=True)
                        if len(course_dur) == 0 or len(app_id) == 0:
                            status = 200
                            data_values = {'msg': 'You are not eligible to fill this form.'}

                        else:
                            # details[0]['msg']='Portal is locked'
                            if len(qry) == 0:
                                data_values = {'msg': 'Seat is not alloted.'}
                                status = 200
                            else:

                                if locking_status == False:
                                    status = 200
                                    data_values = {'msg': 'Portal Is Locked'}

                                else:
                                    stu_whose_priority = list(HostelRoommatePriority.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('application_id__uniq_id__uniq_id__name', 'application_id__uniq_id__uniq_id__uni_roll_no', 'application_id__uniq_id__uniq_id__dept_detail__dept__value', 'application_id__uniq_id__uniq_id__dept_detail__dept'))
                                    print(stu_whose_priority, 'stu_whose_priority')
                                    qry1 = HostelRoommatePriority.objects.filter(application_id=app_id[0]).exclude(status="DELETE").values('uniq_id')
                                    query = HostelSeatAlloted.objects.filter(hostel_part=qry[0]['hostel_part'], seat_part=qry[0]['seat_part'], uniq_id__year__in=year).exclude(status="DELETE").exclude(paid_status="WITHDRAWAL").exclude(paid_status="NOT PAID").exclude(uniq_id=uniq_id).values('uniq_id__uniq_id__name', 'uniq_id', 'uniq_id__uniq_id__uni_roll_no').distinct()
                                    if len(qry1) != 0:
                                        already_filled_data = list(HostelRoommatePriority.objects.filter(application_id=app_id[0]).exclude(status="DELETE").values('uniq_id', 'uniq_id__uniq_id__name', 'priority'))
                                        data_values = {'msg': 'You have already filled your roommate choice form', 'app_id': app_id[0], 'allready_filled_data': already_filled_data, 'data': list(query), 'students': stu_whose_priority}
                                        print(data_values, 'data_values')
                                        status = 200
                                    else:
                                        if qry[0]['status'] == 'WITHDRAWAL':
                                            data_values = {'msg': 'You are not eligible to fill this form.'}
                                            status = 200
                                        # elif qry[0]['status']!='SEAT ALLOTED':
                                        #   data_values = {'msg':'Seat is not alloted.'}
                                        #   status = 200
                                        elif qry[0]['seat_part__value'] == 1:
                                            data_values = {'msg': 'There is no roommate choice for your seater type.'}
                                            status = 200
                                        else:
                                            if qry[0]['paid_status'] != 'ALREADY PAID':
                                                data_values = {'msg': 'Your hostel fees is due.'}
                                                status = 200
                                            else:

                                                data_values = {'data': list(query), 'seater': qry[0]['seat_part__value'], 'students': stu_whose_priority}
                                                status = 200
                    # elif (request.GET['request_type']== 'edit_form'):
                    #   app_id = request.GET['app_id']
                    #   HostelRoommatePriority.objects.filter(application_id=app_id).exclude(status="DELETE").update(status="DELETE")

                elif request.method == "POST":
                    data = json.loads(request.body)
                    if 'app_id' in data:
                        HostelRoommatePriority.objects.filter(application_id=data['app_id']).exclude(status="DELETE").update(status="DELETE")
                    roommate = data['roommate']
                    app_id = HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values_list('id', flat=True)
                    if len(app_id) > 0:
                        objs = (HostelRoommatePriority(application_id=HostelStudentAppliction.objects.get(id=app_id[0]), uniq_id=studentSession.objects.get(uniq_id=v), priority=int(k) + 1)for k, v in enumerate(roommate))
                        qry = HostelRoommatePriority.objects.bulk_create(objs)
                        data_values = {'msg': 'Roommate choice form is successfully submitted.'}
                    else:
                        data_values = {'msg': 'You have not fill your Hostel Application Form'}
                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)


def HostelFeeLetter(stu_data, filename):
    receipt_name = "HOSTEL FEE LETTER"
    # filename="HostelFeeLetter.pdf"

    img = Image.new(mode='RGB', size=(1478, 2100), color=(255, 255, 255, 0))
    kiet = Image.open(settings.FILE_PATH + "KIET_Header.png")
    kiet = kiet.convert('RGB')
    kiet = kiet.resize((900, 170))
    img.paste(kiet, (300, 30))

    size = 2480, 3508
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 25)
    font_bold = ImageFont.truetype(settings.FILE_PATH + "arialbd.ttf", 25)
    final_img_width = min(img.size[0], 1478)
    final_img_height = min(img.size[1], 2100)
    tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")

    draw.text((50, 220), str('Ref No. : KIET/ ADMN./ FEE/2019-20'), (0, 0, 0), font=font_bold)
    draw.text((50, 250), str('05/May/2019,'), (0, 0, 0), font=font_bold)  # gap=15
    draw.text((50, 290), str('TO,'), (0, 0, 0), font=font)
    draw.text((50, 320), str(stu_data['f_name']), (0, 0, 0), font=font_bold)
    draw.text((50, 350), str(stu_data['address']), (0, 0, 0), font=font_bold)
    draw.text((50, 390), str(stu_data['city_state']), (0, 0, 0), font=font_bold)
    draw.text((50, 420), str('Pin Code - ' + str(stu_data['pincode'])), (0, 0, 0), font=font_bold)
    draw.text((50, 450), str('Contact No. - ' + str(stu_data['father_mob'])), (0, 0, 0), font=font_bold)
    draw.text((50, 490), str('Dear Parent,'), (0, 0, 0), font=font)
    text = 'Hostel Fee of your ward ' + stu_data['uniq_id__name'] + ' (Roll No. -' + stu_data['uniq_id__uni_roll_no'] + ') student of ' + stu_data['uniq_id__dept_detail__course__value'] + ' of our institute is due for the academic year 2019-20 as mentioned below:'
    text = textwrap.wrap(text, width=100)
    margin = 500
    for line in text:
        margin = margin + 30
        draw.text((50, margin), line, font=font, fill="#000000")
    # draw.text((50,495),str('institute is due for the academic year 2019-20 as mentioned below:'),(0,0,0),font=font)
    draw.text((50, 600), str('Hostel Charges (Including Mess):'), (0, 0, 0), font=font_bold)
    draw.point([(40, 630), (0, 0)], fill="#aa0000")
    draw.text((60, 630), str('-For ' + stu_data['seat_alloted'] + ' Seat Room                  :  ' + str(stu_data['fee_value']) + '/-'), (0, 0, 0), font=font_bold)
    draw.text((60, 660), str('-Hostel Security(Refundable)         :  5,000/-'), (0, 0, 0), font=font_bold)
    draw.text((50, 690), str('(In case of opting first time)'), (0, 0, 0), font=font_bold)
    draw.text((50, 720), str('Other Hostel Fees*:'), (0, 0, 0), font=font_bold)
    draw.text((60, 750), str('-Bedding Charges (Mattress, Pillow with cover & Bed sheet)(One Time)    :  2,000/-*'), (0, 0, 0), font=font_bold)
    draw.text((60, 780), str('-Laundary Charges (Detail Attached)                                                                           :  6,250/-*'), (0, 0, 0), font=font_bold)
    draw.text((60, 810), str('-Air Conditioning (Bedding Includes):'), (0, 0, 0), font=font_bold)
    draw.text((260, 840), str('-For Double Seat Room                                                       :  37,500/-*'), (0, 0, 0), font=font_bold)
    draw.text((260, 870), str('-For Triple Seat Room                                                         :  25,000/-*'), (0, 0, 0), font=font_bold)
    draw.text((50, 900), str('(*Optional Services)'), (0, 0, 0), font=font_bold)
    text2 = 'If your ward is interested to avail Hostel facility for the academic year 2019-20, please send a demand  draft of Rs.' + str(stu_data['fee_value']) + ' for ' + stu_data['seat_alloted'] + ' seat room. (Kindly add security amount in case of opting first time) as the case may be in favour of "KIET Group Of Institutions" payable at Ghaziabad / Delhi on or before 25/05/2019.'
    text2 = textwrap.wrap(text2, width=100)
    margin2 = 900
    for line in text2:
        margin2 = margin2 + 30
        draw.text((50, margin2), line, font=font, fill="#000000")
    draw.text((50, 1050), str('Separate DD required for optional Hostel Fees.'), (0, 0, 0), font=font_bold)
    draw.text((50, 1080), str('No fee will be accepted in cash.'), (0, 0, 0), font=font_bold)
    text3 = 'In this regard you are further informed that hostel will be alloted to those students who satisfy following conditions at the time of allotment and during the stay in the hostel:'
    text3 = textwrap.wrap(text3, width=100)
    margin3 = 1090
    for line in text3:
        margin3 = margin3 + 30
        draw.text((50, margin3), line, font=font, fill="#000000")
    draw.text((50, 1190), str('1.   Full Hostel charges as mentioned above are paid before due date i.e. 25/05/2019.'), (0, 0, 0), font=font)
    draw.text((50, 1220), str('2.   They are not involved in any kind of indiscipline activities in the past.'), (0, 0, 0), font=font)
    draw.text((50, 1250), str('3.'), (0, 0, 0), font=font)
    draw.text((50, 1250), str('3.   Hostel allotment will stand automatically cancelled, in case any time during the session, the attendance of the '), (0, 0, 0), font=font)
    draw.text((100, 1280), str('alloted falls below 75%. In case of explusion due to indiscipline activity, no fee will be refundable.'), font=font, fill="#000000")
    draw.text((50, 1350), str('You can also deposit fees through NEFT (Bank Transfer) in our Account (A/C detail as under):- '), (0, 0, 0), font=font)

    neft = Image.open(settings.FILE_PATH + "NEFT.jpg")
    neft = neft.convert('RGB')
    neft = neft.resize((1000, 200))
    img.paste(neft, (50, 1380))

    bank_acc_draw = ImageDraw.Draw(img)
    draw.text((530, 1470), str('KIET' + str(stu_data['uniq_id__uni_roll_no'])), font=font, fill="#000000")

    text5 = 'If you fail to deposit hostel fees on or before 25/05/2019, hostel allotment shall stand cancelled.'
    text5 = textwrap.wrap(text5, width=100)
    margin5 = 1550
    for line in text5:
        margin5 = margin5 + 30
    draw.text((50, margin5), line, font=font, fill="#000000")
    draw.text((50, 1630), str('Thanking You,'), font=font, fill="#000000")
    draw.text((50, 1660), str("For KIET Group of Institutions"), font=font, fill="#000000")

    sign = Image.open(settings.FILE_PATH + "Arunji_Sign.jpg")
    sign = sign.convert('RGB')
    sign = sign.resize((200, 140))
    img.paste(sign, (50, 1730))
    draw.text((50, 1870), str('(Arun Agarwal)'), font=font, fill="#000000")
    draw.text((50, 1900), str("Accounts Officer"), font=font, fill="#000000")
    draw.text((50, 1950), str("NOTE : This is a computer generated document."), font=font_bold, fill="#000000")
    index = 0
    x = index // 2 * (tmp_image.size[0] // 2)
    y = index % 2 * (tmp_image.size[1] // 2)
    w, h = img.size
    tmp_image.paste(img, (x, y, x + w, y + h))

    tmp_image.save(settings.FILE_PATH + 'HostelFeeLetter/fee_let.pdf', "PDF", resolution=250.0)

    merger = PdfFileMerger()

    pdfs = [settings.FILE_PATH + 'HostelFeeLetter/fee_let.pdf', settings.FILE_PATH + "laundromat.pdf"]
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))

    with open(settings.FILE_PATH + 'HostelFeeLetter/' + filename, 'wb') as fout:
        merger.write(fout)
    # with open(settings.FILE_PATH+filename, 'rb') as pdf:
    #   response = HttpResponse(pdf, content_type='application/pdf')
    #   response['Content-Disposition'] = 'inline;filename=some_file.pdf'
    #   return response
    #   pdf.closed


def get_stu_data(uniq_id, session_name):
    studentSession = generate_session_table_name('studentSession_', session_name)
    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
    data = list(studentSession.objects.filter(uniq_id=uniq_id).values('uniq_id__name', 'uniq_id__join_year', 'uniq_id__uni_roll_no', 'uniq_id__dept_detail__course__value', 'uniq_id__dept_detail__course', 'uniq_id__batch_from', 'uniq_id__caste', 'uniq_id__gender', 'uniq_id__fee_waiver', 'uniq_id__admission_status', 'uniq_id__dept_detail__dept__value', 'year', 'uniq_id__exam_roll_no'))
    session_data = list(Semtiming.objects.filter())
    if len(data) > 0:
        for d in data:
            if d['uniq_id__uni_roll_no'] == None:
                d['uniq_id__uni_roll_no'] = d['uniq_id__exam_roll_no']
            qry = list(StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values('father_mob', 'father_add', 'father_city'))
            d['father_mob'] = qry[0]['father_mob']
            qry2 = list(StudentAddress.objects.filter(uniq_id=uniq_id).values('p_add1', 'p_add2', 'p_city', 'p_pincode', 'p_state__value'))
            if qry2[0]['p_add1'] == None:
                qry2[0]['p_add1'] = ''
            if qry2[0]['p_add2'] == None:
                qry2[0]['p_add2'] = ''
            d['address'] = str(qry2[0]['p_add1']) + " " + str(qry2[0]['p_add2'])
            if qry2[0]['p_pincode'] == None:
                d['pincode'] = ''
            d['pincode'] = qry2[0]['p_pincode']
            if qry2[0]['p_city'] == None:
                qry2[0]['p_city'] = ''
            if qry2[0]['p_state__value'] == None:
                qry2[0]['p_state__value'] = ''
            d['city_state'] = str(qry2[0]['p_city']) + " " + str(qry2[0]['p_state__value'])
            qry3 = list(StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname'))
            if len(qry3) > 0:
                d['f_name'] = qry3[0]['fname']
            else:
                d['f_name'] = ''
            seat_all = list(HostelSeatAlloted.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").exclude(status="WITHDRAWAL").values('seat_part__value', 'seat_part', 'hostel_part'))
            if len(seat_all) > 0:
                if seat_all[0]['seat_part__value'] == '1':
                    d['seat_alloted'] = 'Single'
                elif seat_all[0]['seat_part__value'] == '2':
                    d['seat_alloted'] = 'Double'
                elif seat_all[0]['seat_part__value'] == '3':
                    d['seat_alloted'] = 'Triple'
                elif seat_all[0]['seat_part__value'] == '4':
                    d['seat_alloted'] = 'Four'
                else:
                    d['seat_alloted'] = None
                fee_data = StuAccFeeSettings.objects.filter(course_id=data[0]['uniq_id__dept_detail__course'], gender=data[0]['uniq_id__gender'], join_year=data[0]['uniq_id__batch_from'], admission_status=data[0]['uniq_id__admission_status'], caste=data[0]['uniq_id__caste'], fee_waiver=data[0]['uniq_id__fee_waiver'], session=8, seater_type=seat_all[0]['seat_part'], fee_component__value='HOSTEL', fee_component_cat__value='HOSTEL FEE (INCLUDING MESS)').exclude(status="DELETE").values_list('value', flat=True)
                if len(fee_data) > 0:
                    d['fee_value'] = fee_data[0]
                else:
                    d['fee_value'] = None
            else:
                d['seat_alloted'] = '---'
                d['fee_value'] = '---'
            academic_fee_data = StuAccFeeSettings.objects.filter(
                join_year=data[0]['uniq_id__join_year'],
                caste=data[0]['uniq_id__caste'],
                admission_status=data[0]['uniq_id__admission_status'],
                fee_waiver=data[0]['uniq_id__fee_waiver'],
                fee_component__value='ACADEMIC',
                fee_component_cat__field='ACADEMIC',
                course_id=data[0]['uniq_id__dept_detail__course'],
                gender=data[0]['uniq_id__gender'],
                session=8,
            ).exclude(status="DELETE").values('value', 'fee_component_cat__value')
            print(academic_fee_data, 'academic_fee_data')
            z = {}
            total_amt = 0
            upsee_amt = 0
            print(academic_fee_data)
            for acad in academic_fee_data:
                if 'UPSEE' in acad:
                    if ((data[0]['year'] == 2 and 'LATERAL' in data[0]['uniq_id__admission_type__value']) or (data[0]['year'] == 1)) and (data[0]['uniq_id__admission_through__value'] in ['COUNSELLING', 'EWS']) and (data[0]['uniq_id__join_year'] == date.today().year):
                        flag_upsee = 1
                        z[acad['fee_component_cat__value']] = acad['value']
                        total_amt += acad['value']
                        upsee_amt = acad['value']
                    else:
                        z[acad['fee_component_cat__value']] = acad['value']
                        total_amt += acad['value']

                elif 'ONE TIME' in acad:
                    if ((data[0]['year'] == 2 and 'LATERAL' in data[0]['uniq_id__admission_type__value']) or (data[0]['year'] == 1)) and (data[0]['uniq_id__join_year'] == date.today().year):
                        z[acad['fee_component_cat__value']] = acad['value']
                        total_amt += acad['value']
                    else:
                        z[acad['fee_component_cat__value']] = 0
                else:
                    z[acad['fee_component_cat__value']] = acad['value']
                    total_amt += acad['value']

            z['total'] = str(total_amt)

            d['component_data'] = z

            trans_data = StuAccFeeSettings.objects.filter(course_id=data[0]['uniq_id__dept_detail__course'], gender=data[0]['uniq_id__gender'], join_year=data[0]['uniq_id__batch_from'], admission_status=data[0]['uniq_id__admission_status'], caste=data[0]['uniq_id__caste'], fee_waiver=data[0]['uniq_id__fee_waiver'], fee_component__value='TRANSPORTATION').exclude(status="DELETE").values('value', 'fee_component_cat__value')

            # print(trans_data)
            if len(trans_data) == 0:
                d['ghaz'] = 0
                d['mohan'] = 0
                d['anand'] = 0
            else:
                for bus in trans_data:
                    if "GHAZIABAD" in bus['fee_component_cat__value']:
                        d['ghaz'] = bus['value']
                    if bus['fee_component_cat__value'] == 'FROM MOHAN NAGAR':
                        d['mohan'] = bus['value']
                    if bus['fee_component_cat__value'] == 'FROM ANAND VIHAR':
                        d['anand'] = bus['value']
            if 'ghaz' not in d:
                d['ghaz'] = 0
            if 'mohan' not in d:
                d['mohan'] = 0
            if 'anand' not in d:
                d['anand'] = 0

        return data[0]
    else:
        return data


def PrintHostelFeeLetter(request):
    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', '1920o')
    Seat_alloted_ids = list(HostelSeatAlloted.objects.exclude(status="DELETE").exclude(status="WITHDRAWAL").values_list('uniq_id', flat=True))
    uniq_id = Seat_alloted_ids
    pdfs = []
    for stu in uniq_id:
        stu_data = get_stu_data(stu, '1920o')
        filename = str('HostelFeeLetter_' + str(stu) + '.pdf')
        HostelFeeLetter(stu_data, filename)
        pdfs.append(settings.FILE_PATH + filename)
    merger = PdfFileMerger()
    for p in pdfs:
        merger.append(open(p, 'rb'))
    with open(settings.FILE_PATH + 'result.pdf', 'wb') as fout:
        merger.write(fout)
    with open(settings.FILE_PATH + "result.pdf", 'rb') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'

        return response
        pdf.closed


def HostelFeeLetter_Portal(request):
    Sessions = []
    data_values = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                uniq_id = request.session['uniq_id']
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                session = request.session['Session']
                if request.method == 'GET':
                    if int(session_name[:2]) < 19:
                        return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    stu_data = get_stu_data(uniq_id, session_name)
                    if stu_data['seat_alloted'] != '---':
                        # filename = str('HostelFeeLetter_' + str(uniq_id) + '.pdf')
                        # HostelFeeLetter(stu_data, filename)
                        # with open(settings.FILE_PATH + 'HostelFeeLetter/' + filename, 'rb') as pdf:
                        #     response = HttpResponse(pdf, content_type='application/pdf')
                        #     response['Content-Disposition'] = 'inline;filename=some_file.pdf'
                        #     msg = "Success"
                        #     return response
                        #     pdf.closed
                        if stu_data['uniq_id__uni_roll_no'] != None:
                            filename = str('HostelFeeLetter_' + str(uniq_id) + '.pdf')
                            HostelFeeLetter(stu_data, filename)
                            with open(settings.FILE_PATH + 'HostelFeeLetter/' + filename, 'rb') as pdf:
                                response = HttpResponse(pdf, content_type='application/pdf')
                                response['Content-Disposition'] = 'inline;filename=some_file.pdf'
                                msg = "Success"
                                return response
                                pdf.closed
                        else:
                            status = 202
                            msg = "You are not eligible to see Hostel Fee Letter."
                    else:
                        status = 202
                        msg = "Hostel is not alloted"
                else:
                    status = 502
                    msg = "Bad Request"
            else:
                status = 401
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Not Authorized"
    else:
        status = 500
        msg = "Error"
    data_values = {'msg': msg}
    return JsonResponse(data=data_values, status=status, safe=False)


def PlacementPolicy_Form(request):
    Sessions = []
    data_values = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                uniq_id = request.session['uniq_id']
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                session = request.session['Session']
                studentSession = generate_session_table_name('studentSession_', session_name)

                if request.method == 'GET':

                    if (request.GET['request_type'] == 'print_form'):
                        form_type = PlacementPolicyNew.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values_list('form_type', flat=True)
                        if form_type[0] == 'FORM_A':
                            return printPlacementForm(uniq_id, 'FORM_A', session_name)
                        else:
                            return printPlacementForm(uniq_id, 'FORM_B', session_name)

                    elif (request.GET['request_type'] == 'get_data'):
                        current_year = session.split('-')[0]
                        date = datetime.today().strftime('%Y-%m-%d')
                        course_duration = list(studentSession_2021e.objects.filter(uniq_id=uniq_id).values('sem__dept__course_duration', 'sem'))
                        if course_duration:
                            year = course_duration[0]['sem__dept__course_duration']
                            second_last = list(studentSession.objects.filter(year=year, uniq_id=uniq_id, uniq_id__dept_detail__course__in=[12,17]).values('uniq_id'))
                        else:
                            second_last = []

                        if second_last:
                            if date < '2021-08-30' and date > '2020-05-25':
                                Placement_id = PlacementPolicyNew.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values_list('id', flat=True)
                                if len(Placement_id) == 0:
                                    link = 'https://localhost/upload_images/placement_policy/Placement_Policy_2021_B.Tech_MCA.pdf'
                                    details = studenthostel.views.hostel_function.get_student_details(uniq_id, session_name, {}, sem_type, session_id)
                                    data_values = {'data': details, 'link': link, 'already_filled': False}
                                    status = 200

                                else:
                                    form_type = PlacementPolicyNew.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('form_type', 'time_stamp')
                                    if len(form_type) > 0:
                                        data_values = {'msg': 'You have already filled your placement policy form.', 'time_stamp': form_type[0]['time_stamp'], 'already_filled': True}
                                    else:
                                        data_values = {'msg': 'You have not filled your placement policy form.', 'already_filled': False}

                                    status = 200
                            else:
                                form_type = PlacementPolicyNew.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('form_type', 'time_stamp')
                                if len(form_type) > 0:
                                    data_values = {'msg': 'You have filled your placement policy form.', 'time_stamp': form_type[0]['time_stamp'], 'already_filled': True}
                                else:
                                    data_values = {'msg': 'Portal is locked.', 'already_filled': False}
                                status = 200
                        else:
                            data_values = {'msg': 'You are not eligible for this form.'}
                            status = 200

                elif request.method == 'POST':
                    data = json.loads(request.body)
                    form_type = data['form_type']
                    type = (form_type.split("_"))[1]
                    student_email = list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('email_id', 'name'))
                    msg = "Dear " + str(student_email[0]['name']) + ",\n\n You have opted FORM-" + str(type) + " for your placement policy and therefore you are requested to download and submit the PDF of your form with your and your parent's signature before 22nd July."

                    msg += "<br><br><hr><br>Thanks and Regards,<br><br>CRPC Dept.<br><br><a href='https://tech.kiet.edu/StudentPortal/' target='_blank' style='color:#137aa9;'>View On Web</a><br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this erp@kiet.edu"
                    qry4  = studentSession_1819e.objects.get(uniq_id=uniq_id)
                    print(qry4)
                    print('samyak')
                    PlacementPolicyNew.objects.create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), form_type=form_type , session=Semtiming.objects.get(session=session))
                    send_mail(student_email[0]['email_id'], 'Regarding submission of placement policy', [msg], [])

                    data_values = {'msg': 'Placement Policy Form Is Successfully Filled.'}
                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)


def printPlacementForm(uniq_id, form_type, session_name):

    receipt_name = "PLACEMENT FORM"
    studentSession = generate_session_table_name('studentSession_', session_name)
    date1 = date.today()

    filename = str("PlacementForm_" + str(uniq_id) + ".pdf")
    student_det = list(studentSession.objects.filter(uniq_id=uniq_id).values('uniq_id__dept_detail__dept__value', 'uniq_id__uni_roll_no', 'uniq_id__name', 'uniq_id__dept_detail__course__value'))
    sno = list(PlacementPolicyNew.objects.filter(uniq_id=uniq_id).values('id'))
    father_det = list(StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname'))

    if form_type == 'FORM_A':

        img = Image.open(settings.FILE_PATH + "Form A_B_Tech.jpg")
        img2 = Image.open(settings.FILE_PATH + "Form A_B_Tech2.jpg")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 30)
        font_bold = ImageFont.truetype(settings.FILE_PATH + "arialbd.ttf", 26)
        final_img_width = img.size[0]
        final_img_height = img.size[1]
        final_img_width2 = img2.size[0]
        final_img_height2 = img2.size[1]

        tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")
        tmp_image2 = Image.new("RGB", (final_img_width, final_img_height), "white")
        draw.text((170, 300), 'Serial No.' + str(sno[0]['id']), font=font)
        draw.text((350, 590), str(date1), font=font_bold)
        draw.text((1100, 590), str(student_det[0]['uniq_id__dept_detail__dept__value']), font=font_bold)
        draw.text((495, 665), str(student_det[0]['uniq_id__name']), font=font_bold)
        draw.text((1250, 665), str(student_det[0]['uniq_id__uni_roll_no']), font=font_bold)
        draw.text((300, 800), str(student_det[0]['uniq_id__name']), font=font_bold)
        draw.text((950, 800), str(father_det[0]['fname']), font=font_bold)
        draw.text((290, 860), str(student_det[0]['uniq_id__dept_detail__course__value'] + ' ' + '(' + student_det[0]['uniq_id__dept_detail__dept__value'] + ')'), font=font_bold)

        index = 0
        x = index // 2 * (tmp_image.size[0] // 2)
        y = index % 2 * (tmp_image.size[1] // 2)
        w, h = img.size
        tmp_image.paste(img, (x, y, x + w, y + h))
        tmp_image2.paste(img2, (x, y, x + w, y + h))

        tmp_image.save(settings.FILE_PATH + '/placement_form.pdf', "PDF", resolution=250.0)
        tmp_image2.save(settings.FILE_PATH + '/placement_form1.pdf', "PDF", resolution=250.0)
        merger = PdfFileMerger()
        pdfs = [settings.FILE_PATH + '/placement_form.pdf', settings.FILE_PATH + "placement_form1.pdf"]
        for pdf in pdfs:
            merger.append(open(pdf, 'rb'))

    else:
        img = Image.open(settings.FILE_PATH + "Form B_B_Tech.jpg")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 25)
        font_bold = ImageFont.truetype(settings.FILE_PATH + "arialbd.ttf", 25)
        final_img_width = img.size[0]
        final_img_height = img.size[1]

        tmp_image = Image.new("RGB", (final_img_width, final_img_height), "black")

        draw.text((350, 560), str(date1), font=font)
        draw.text((1100, 560), str(student_det[0]['uniq_id__dept_detail__dept__value']), font=font_bold)
        draw.text((495, 630), str(student_det[0]['uniq_id__name']), font=font_bold)
        draw.text((1250, 630), str(student_det[0]['uniq_id__uni_roll_no']), font=font_bold)
        draw.text((300, 770), str(student_det[0]['uniq_id__name']), font=font_bold)
        draw.text((1050, 770), str(father_det[0]['fname']), font=font_bold)
        draw.text((390, 865), str(student_det[0]['uniq_id__dept_detail__course__value'] + ' ' + '(' + student_det[0]['uniq_id__dept_detail__dept__value'] + ')'), font=font_bold)

        index = 0
        x = index // 2 * (tmp_image.size[0] // 2)
        y = index % 2 * (tmp_image.size[1] // 2)
        w, h = img.size
        tmp_image.paste(img, (x, y, x + w, y + h))

        tmp_image.save(settings.FILE_PATH + '/placement_form3.pdf', "PDF", resolution=250.0)

        merger = PdfFileMerger()
        merger.append(open(settings.FILE_PATH + '/placement_form3.pdf', 'rb'))

    with open(settings.FILE_PATH + 'Placement_Form/' + filename, 'wb') as fout:
        merger.write(fout)

    with open(settings.FILE_PATH + 'Placement_Form/' + filename, 'rb') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        msg = "Success"
        return response


def Script_HostelAppForm_correction():
    Sessions = []
    session_name = '1920o'
    sem_type = 'odd'
    session_id = '8'
    session = '2019-2020'

    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
    HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
    HostelSeaterPriority = generate_session_table_name('HostelSeaterPriority_', session_name)
    HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
    HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)
    HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)

    studentSession = generate_session_table_name("studentSession_", session_name)
    new_session = session.split('-')
    new_session1 = str(int(new_session[0]) - 1) + '-' + str(int(new_session[1]) - 1)

    qry = list(Semtiming.objects.filter(session=new_session1).values('uid', 'session_name', 'sem_start', 'sem_end', 'sem_type'))

    not_having_uni_marks = list(HostelStudentAppliction.objects.filter(uniq_id__lte=5900).exclude(status='DELETE').values_list('uniq_id', flat=True))

    for uniq_id in not_having_uni_marks:
        uni_max_marks = 0.0
        uni_marks_obt = 0.0
        carry_over = 0

        for q in qry:
            i = 0
            sub_id = []
            max_marks = 0.0
            total_internal = 0.0
            total_external = 0.0

            att_type = get_sub_attendance_type(q['uid'])
            att_type_li = [t['sno'] for t in att_type]

            studentSession = generate_session_table_name("studentSession_", q['session_name'])

            q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
            print(q_att_date, q['sem_type'])
            if q['sem_type'] == 'odd':

                StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", q['session_name'])

                subjects = get_student_subjects(q_att_date[0]['section__sem_id'], q['session_name'])
                for s in subjects:
                    sub_id.append(s['id'])
                    if(sub_id[i] == "" or sub_id[i] == "----" or sub_id[i] == None):
                        sub_id.pop(i)
                        i = i - 1
                    i = i + 1

                marks = StudentUniversityMarks.objects.filter(uniq_id=uniq_id, subject_id__in=sub_id).values('external_marks', 'internal_marks', 'subject_id__max_university_marks', 'subject_id__max_ct_marks', 'subject_id__max_att_marks', 'subject_id__max_ta_marks', 'back_marks')
                for m in marks:
                    max_marks = max_marks + float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks'])
                    try:
                        if (m['internal_marks'] == '' or m['internal_marks'] == None):
                            m['internal_marks'] = 0.0
                        if (m['external_marks'] == '' or m['external_marks'] == None):
                            m['external_marks'] = 0.0
                        if (m['back_marks'] != None):
                            m['external_marks'] = float(m['back_marks'])
                        if m['subject_id__max_university_marks'] == 0:
                            continue
                        if ((float(m['internal_marks']) + float(m['external_marks'])) / (float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks'])) * 100 < 40 or(float(m['external_marks']) / float(m['subject_id__max_university_marks']) * 100) < 30):
                            carry_over = carry_over + 1

                        total_internal = total_internal + float(m['internal_marks'])
                        total_external = total_external + float(m['external_marks'])

                    except ValueError:
                        total_internal = total_internal
                        total_external = total_external

                uni_max_marks = uni_max_marks + max_marks
                uni_marks_obt = uni_marks_obt + total_external + total_internal

        # HostelStudentAppliction.objects.filter(uniq_id = uniq_id).update(carry=carry_over)
        # HostelStudentAppliction.objects.filter(uniq_id = uniq_id).update(uni_marks_obt=uni_marks_obt, uni_max_marks=uni_max_marks, carry=carry_over)
        print("carry", carry_over)

    not_having_att = list(HostelStudentAppliction.objects.filter(attendance_avg=None, uniq_id__lte=5900).exclude(status='DELETE').values_list('uniq_id', flat=True))

    qry = list(Semtiming.objects.filter(session=new_session1).values('uid', 'session_name', 'sem_start', 'sem_end', 'sem_type'))

    for uniq_id in not_having_uni_marks:
        att_per = 0.0
        count = 0
        for q in qry:
            attendance = 0.0
            att_category = []

            att_type = get_sub_attendance_type(q['uid'])
            att_type_li = [t['sno'] for t in att_type]

            studentSession = generate_session_table_name("studentSession_", q['session_name'])

            q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')

            subjects = get_student_subjects(q_att_date[0]['section__sem_id'], q['session_name'])

            query = get_student_attendance(uniq_id, max(datetime.strptime(str(q['sem_start']), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), q['sem_end'], q['uid'], att_type_li, subjects, 1, att_category, q['session_name'])

            if (query['total'] > 0):
                attendance = round((query['present_count'] / query['total']) * 100, 2)
                count = count + 1
            else:
                attendance = 0.0

            att_per = att_per + (query['present_count'] / query['total']) * 100

        HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').update(attendance_avg=round((att_per / count), 2))
        print(att_per / count)
    return 200

def Script_HostelAppForm_correction_2021o():
    session_name = '2021o'
    HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
    get_all_students = HostelStudentAppliction.objects.exclude(status="DELETE").values_list('uniq_id',flat=True)
    print(get_all_students)
    qry = list(Semtiming.objects.filter(session='2019-2020').values('uid', 'session_name', 'sem_start', 'sem_end', 'sem_type'))

    data = []
    for uniq_id in get_all_students:
        att_per = 0.0
        total_marks = 0.0
        total_marks_obt = 0.0
        count = 0
        temp_data = {'uniq_id':uniq_id,'avg_att':att_per,'Obtained_Marks': total_marks_obt, 'Max_Marks': total_marks, 'Carry_Over': count}
        for q in qry:
            i = 0
            sub_id = []
            max_marks = 0.0
            total_internal = 0.0
            total_external = 0.0
            attendance = 0.0
            att_category = []
            att_type = get_sub_attendance_type(q['uid'])
            att_type_li = [t['sno'] for t in att_type]
            studentSession = generate_session_table_name("studentSession_", q['session_name'])

            q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
            subjects = get_student_subjects(q_att_date[0]['section__sem_id'], q['session_name'])

            if 'even' in q['sem_type']:
                end_date = datetime.strptime(str('2020-03-06'), "%Y-%m-%d").date()
            else:
                end_date = q['sem_end']
            print(datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date(), end_date)
            query = get_student_attendance(uniq_id, max(datetime.strptime(str(q['sem_start']), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), end_date, q['uid'], att_type_li, subjects, 1, att_category, q['session_name'])
            if (query['total'] > 0):
                attendance = round((query['present_count'] / query['total']) * 100, 2)
                att_per = att_per + (query['present_count'] / query['total']) * 100
            else:
                attendance = 0.0
            # details[0]['att'][q['session_name']] = attendance
            # if q['sem_type'] == 'odd':
            subjects = get_student_subjects(q_att_date[0]['section__sem_id'], q['session_name'])
            StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", q['session_name'])
            for s in subjects:
                sub_id.append(s['id'])
                if(sub_id[i] == "" or sub_id[i] == "----" or sub_id[i] == None):
                    sub_id.pop(i)
                    i = i - 1
                i = i + 1
            marks = StudentUniversityMarks.objects.filter(uniq_id=uniq_id, subject_id__in=sub_id).values('external_marks', 'internal_marks', 'subject_id__max_university_marks', 'subject_id__max_ct_marks', 'subject_id__max_att_marks', 'subject_id__max_ta_marks', 'back_marks')
            for m in marks:
                max_marks = max_marks + float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks'])
                try:
                    if (m['internal_marks'] == '' or m['internal_marks'] == None):
                        m['internal_marks'] = 0.0
                        
                        max_marks = max_marks-(float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks']))
                    if (m['external_marks'] == '' or m['external_marks'] == None):
                        m['external_marks'] = 0.0
                        
                        max_marks = max_marks - float(m['subject_id__max_university_marks'])
                    if (m['back_marks'] != None):
                        m['external_marks'] = float(m['back_marks'])
                    # if m['subject_id__max_university_marks'] == 0:
                    #   continue
                    case1 = (float(m['internal_marks']) + float(m['external_marks'])) / (float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks']) + float(m['subject_id__max_att_marks']) + float(m['subject_id__max_ta_marks'])) * 100
                    if float(m['subject_id__max_university_marks'])>0:
                        case2 = float(m['external_marks']) / float(m['subject_id__max_university_marks']) * 100
                    else:
                        case2 = 100
                    if (case1<40 or case2<30) or m['back_marks'] != None:
                        count = count + 1
                        if m['back_marks']!=None:
                            m['external_marks'] = float(m['back_marks'])
                    total_internal = total_internal + float(m['internal_marks'])
                    total_external = total_external + float(m['external_marks'])
                except ValueError:
                    total_internal = total_internal
                    total_external = total_external
                total_marks = max_marks
                total_marks_obt = total_external + total_internal
            temp_data['Obtained_Marks'] = total_marks_obt
            temp_data['Max_Marks'] = total_marks
            temp_data['Carry_Over'] = count

            # {'Obtained_Marks': total_marks_obt, 'Max_Marks': total_marks}, 'Carry_Over': count}
        if att_per != 0:
            average_att = round(att_per, 2) / 2
        else:
            average_att = 0.00
        temp_data['avg_att'] = average_att
        data.append(temp_data)

    for d in data:
        HostelStudentAppliction.objects.filter(uniq_id=d['uniq_id']).exclude(status="DELETE").update(attendance_avg=d['avg_att'],uni_marks_obt=d['Obtained_Marks'],uni_max_marks=d['Max_Marks'],carry=d['Carry_Over'])
        print(d['avg_att'] ,'      '  , d['Carry_Over'])
    return 200
# Script_HostelAppForm_correction_2021o()

def AcademicFeeLetter(stu_data, filename):
    # print(stu_data,stu_data)
    receipt_name = "ACADEMIC FEE LETTER"
    # filename="HostelFeeLetter.pdf"
    print(stu_data)
    img = Image.new(mode='RGB', size=(1478, 2100), color=(255, 255, 255, 0))
    kiet = Image.open(settings.FILE_PATH + "KIET_Header.png")
    kiet = kiet.convert('RGB')
    kiet = kiet.resize((900, 170))
    img.paste(kiet, (300, 30))
    size = 2480, 3508
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 25)
    font_bold = ImageFont.truetype(settings.FILE_PATH + "arialbd.ttf", 25)
    final_img_width = min(img.size[0], 1478)
    final_img_height = min(img.size[1], 2100)
    tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")

    draw.text((50, 230), str('Ref : KIET/ADM/FEES/19-20/1067'), (0, 0, 0), font=font)
    draw.text((1300, 220), str('05/06/2019'), (0, 0, 0), font=font)  # gap=15
    draw.text((50, 290), str('TO,'), (0, 0, 0), font=font)
    draw.text((50, 320), str('' + stu_data['f_name']), (0, 0, 0), font=font_bold)
    draw.text((50, 350), str(stu_data['address']), (0, 0, 0), font=font_bold)
    draw.text((50, 390), str(stu_data['city_state']), (0, 0, 0), font=font_bold)
    draw.text((50, 420), str('Pin Code - ' + str(stu_data['pincode'])), (0, 0, 0), font=font_bold)
    draw.text((50, 450), str('Contact No. - ' + str(stu_data['father_mob'])), (0, 0, 0), font=font_bold)
    draw.text((50, 490), str('Dear Parent,'), (0, 0, 0), font=font)
    draw.text((50, 520), str('Heartiest Congratulation for the completion of another academic session of your ward.'), (0, 0, 0), font=font)
    text1 = 'Academic fees of your ward, Mr./Ms.' + stu_data['uniq_id__name'] + ' (Roll No  ' + stu_data['uniq_id__uni_roll_no'] + ' student of ' + stu_data['uniq_id__dept_detail__course__value'] + '  ' + stu_data['uniq_id__dept_detail__dept__value'] + '  ' + get_suffix(int(stu_data['year'])) + ' Year for the session 2019-2020 is due for payment as per details given below:'
    text1 = textwrap.wrap(text1, width=100)
    margin = 520
    for line in text1:
        margin = margin + 30
        draw.text((50, margin), line, font=font, fill="#000000")
    w = 30
    for x in stu_data['component_data']:
        # print(x, stu_data[x])
        if 'total' in x:
            stu_data['total'] = stu_data['component_data'][x]
            continue
        if stu_data['component_data'][x] == 0:
            continue
        draw.text((200, 630 + w), str(x), (0, 0, 0), font=font_bold)
        draw.text((860, 630 + w), str(': ' + Comma_function(str(stu_data['component_data'][x])) + '/-'), (0, 0, 0), font=font_bold)
        w = w + 30

    # draw.text((200,660),str('Re-registration Fees'),(0,0,0),font=font_bold)
    # draw.text((700,660),str(': '+Comma_function(str(stu_data['regs_fee']))+'/-'),(0,0,0),font=font_bold)

    # draw.text((200,690),str('Examination Fees (2018-2019'),(0,0,0),font=font_bold)
    # draw.text((700,690),str(': '+Comma_function(str(stu_data['univ_fee']))+'/-'),(0,0,0),font=font_bold)

    # draw.text((200,720),str('Extra-curricular and co-curriculra Fees'),(0,0,0),font=font_bold)
    # draw.text((200,750),str('(Cultural/Tech.Fest/Seminars/'),(0,0,0),font=font_bold)
    # draw.text((200,780),str('Aptitude Training etc.)'),(0,0,0),font=font_bold)
    # draw.text((700,720),str(': '+Comma_function(str(stu_data['extra_fee']))+'/-'),(0,0,0),font=font_bold)

    # draw.text((200,810),str('English Communication,Soft Skill,'),(0,0,0),font=font_bold)
    # draw.text((200,840),str('Technical Skiill enhancement etc.'),(0,0,0),font=font_bold)
    # draw.text((700,810),str(' : '+Comma_function(str(stu_data['comm_fee']))+'/-'),(0,0,0),font=font_bold)

    # draw.text((200,870),str('Medical & Accidental Insurance'),(0,0,0),font=font_bold)
    # draw.text((700,870),str(': '+Comma_function(str(stu_data['medical_fee']))+'/-'),(0,0,0),font=font_bold)

    draw.text((150, 940), str('------------------------------------------------------------------------------------------------------------'), (0, 0, 0), font=font_bold)
    draw.text((250, 960), str('Total'), (0, 0, 0), font=font_bold)
    draw.text((860, 960), str(': ' + Comma_function(str(stu_data['total'])) + '/-'), (0, 0, 0), font=font_bold)
    draw.text((150, 980), str('------------------------------------------------------------------------------------------------------------'), (0, 0, 0), font=font_bold)
    amount = convert_amount_to_words(int(stu_data['total']))
    draw.text((50, 1020), str('Rs. ' + str(amount) + ' Only.'), (0, 0, 0), font=font_bold)
    draw.text((50, 1060), str('Bus Fees (for Day Scholar only)'), (0, 0, 0), font=font_bold)
    draw.text((50, 1090), str('(Ghaziabad / Mohan Nagar / Anand Vihar)'), (0, 0, 0), font=font_bold)
    draw.text((700, 1060), str(' : ' + Comma_function(str(stu_data['ghaz'])) + '.00/ ' + Comma_function(str(stu_data['mohan'])) + '.00/ ' + Comma_function(str(stu_data['anand'])) + '.00'), (0, 0, 0), font=font_bold)

    draw.text((50, 1140), str('Kindly send a Demand Draft of Rs,' + Comma_function(str(stu_data['total'])) + '/- (plus bus fees as mentioned above if opted) in favour of "KIET Group'), (0, 0, 0), font=font)
    draw.text((50, 1170), str('Institutions" payable at Ghaziabad / Delhi on or before 5th July 2019.'), (0, 0, 0), font=font)

    draw.text((50, 1240), str('No fees shall be accepted in cash under an circumstance.'), (0, 0, 0), font=font_bold)

    draw.text((50, 1300), str('You can also deposit fees through NEFT (Bank Transfer) in our Account (A/C detail as under):- '), (0, 0, 0), font=font)

    neft = Image.open(settings.FILE_PATH + "NEFT.jpg")
    neft = neft.convert('RGB')
    neft = neft.resize((1000, 200))
    img.paste(neft, (50, 1340))

    bank_acc_draw = ImageDraw.Draw(img)
    draw.text((530, 1430), str('KIET' + str(stu_data['uniq_id__uni_roll_no'])), font=font, fill="#000000")

    draw.text((50, 1580), str('No fresh registration of a student for forth coming session will be undertaken without deposit of full fees.'), font=font, fill="#000000")

    draw.text((50, 1630), str('Thanking You'), font=font, fill="#000000")
    draw.text((50, 1660), str("Yours Truely,"), font=font, fill="#000000")

    sign = Image.open(settings.FILE_PATH + "Arunji_Sign.jpg")
    sign = sign.convert('RGB')
    sign = sign.resize((200, 140))
    img.paste(sign, (50, 1730))
    draw.text((50, 1870), str('Accounts Officer'), font=font_bold, fill="#000000")
    draw.text((50, 1900), str("KIET Group of Institutions,"), font=font_bold, fill="#000000")
    draw.text((50, 1930), str("Ghaziabad"), font=font_bold, fill="#000000")
    draw.text((50, 2040), str("NOTE : This is a computer generated document."), font=font_bold, fill="#000000")
    index = 0
    x = index // 2 * (tmp_image.size[0] // 2)
    y = index % 2 * (tmp_image.size[1] // 2)
    w, h = img.size
    tmp_image.paste(img, (x, y, x + w, y + h))

    tmp_image.save(settings.FILE_PATH + 'AcademicFeeLetter/fee_let.pdf', "PDF", resolution=250.0)

    merger = PdfFileMerger()

    pdfs = [settings.FILE_PATH + 'AcademicFeeLetter/fee_let.pdf']
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))

    with open(settings.FILE_PATH + 'AcademicFeeLetter/' + filename, 'wb') as fout:
        merger.write(fout)


def updateInsuranceDetails(request):
    data_values = []
    print("hello")
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                uniq_id = request.session['uniq_id']
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                session = request.session['Session']
                if int(session_name[:2]) < 19:
                    return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                StudentFillInsurance = generate_session_table_name('StudentFillInsurance_', session_name)
                if request.method == 'GET':
                    insurance_details = list(StudentFillInsurance.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('nominee_name', 'nominee_relation', 'insurer_name', 'insurer_dob', 'insurer_aadhar_num', 'insurer_occupation', 'insurer_nominee_name', 'insurer_relation'))
                    print(insurance_details)
                    if len(insurance_details) != 0:
                        data_values = {'data': insurance_details[0]}
                        status = 200
                    else:
                        data_values = {'msg': 'No details for existing user'}
                        status = 200
                elif request.method == 'PUT':
                    data = json.loads(request.body.decode("utf-8"))
                    nominee_name = data['nominee_name']
                    nominee_relation = data['nominee_relation']
                    insurer_name = data['insurer_name']
                    insurer_dob = data['insurer_dob']
                    insurer_aadhar_num = data['insurer_aadhar_num']
                    insurer_occupation = data['insurer_occupation']
                    insurer_nominee_name = data['insurer_nominee_name']
                    insurer_relation = data['insurer_relation']
                    uniq_id = request.session['uniq_id']
                    session = request.session['Session']
                    session_name = request.session['Session_name']
                    StudentFillInsurance = generate_session_table_name('StudentFillInsurance_', session_name)
                    # sessionTable =  generate_session_table_name('studentSession_',session_name)
                    studentSession = generate_session_table_name("studentSession_", session_name)
                    # try:
                    # student = list(studentSession.objects.filter(uniq_id=uniq_id))
                    # print(student)
                    # q_insert_insurance = StudentFillInsurance.objects.update_or_create(uniq_id=student[0],defaults={ 'nominee_name':nominee_name, 'nominee_relation':nominee_relation, 'insurer_name':insurer_name, 'insurer_relation':insurer_relation, 'insurer_dob':insurer_dob, 'insurer_occupation':insurer_occupation, 'insurer_aadhar_num':insurer_aadhar_num, 'insurer_nominee_name':insurer_nominee_name})
                    insurance_details = list(StudentFillInsurance.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('nominee_name', 'nominee_relation', 'insurer_name', 'insurer_dob', 'insurer_aadhar_num', 'insurer_occupation', 'insurer_nominee_name', 'insurer_relation'))
                    if(len(insurance_details) == 0):
                        create_detail = StudentFillInsurance.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), nominee_name=nominee_name, nominee_relation=nominee_relation, insurer_name=insurer_name, insurer_dob=insurer_dob, insurer_aadhar_num=insurer_aadhar_num, insurer_occupation=insurer_occupation, insurer_nominee_name=insurer_nominee_name, insurer_relation=insurer_relation)
                    else:
                        update_detail = StudentFillInsurance.objects.filter(uniq_id=uniq_id).update(nominee_name=nominee_name, nominee_relation=nominee_relation, insurer_name=insurer_name, insurer_dob=insurer_dob, insurer_aadhar_num=insurer_aadhar_num, insurer_occupation=insurer_occupation, insurer_nominee_name=insurer_nominee_name, insurer_relation=insurer_relation)

                    # except Exception as e:

                        # print(update_detail)
                    insurance_details = list(StudentFillInsurance.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('nominee_name', 'nominee_relation', 'insurer_name', 'insurer_dob', 'insurer_aadhar_num', 'insurer_occupation', 'insurer_nominee_name', 'insurer_relation'))
                    status = 200
                    data_values = {'data': insurance_details[0], 'msg': 'Successfully Updated'}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)


def PrintAcademicFeeLetter(request):
    studentSession = generate_session_table_name('studentSession_', '1920o')
    prim_details = list(studentSession.objects.values_list('uniq_id', flat=True))
    pdfs = []
    for stu in prim_details:
        stu_data = get_stu_data(stu, '1920o')
        filename = str('AcademicFeeLetter_' + str(stu) + '.pdf')
        AcademicFeeLetter(stu_data, filename)
        pdfs.append(settings.FILE_PATH + filename)
    merger = PdfFileMerger()
    for p in pdfs:
        merger.append(open(p, 'rb'))
    with open(settings.FILE_PATH + 'result_acad.pdf', 'wb') as fout:
        merger.write(fout)
    with open(settings.FILE_PATH + "result_acad.pdf", 'rb') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'

        return response
        pdf.closed


def AcademicFeeLetter_Portal(request):
    Sessions = []
    data_values = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                uniq_id = request.session['uniq_id']
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                session = request.session['Session']
                if request.method == 'GET':
                    if int(session_name[:2]) < 19:
                        return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    stu_data = get_stu_data(uniq_id, session_name)
                    print(stu_data)
                    if len(stu_data) == 0:
                        msg = "Academic fee letter is not available for your session."
                        status = 202
                    else:
                        filename = str('AcademicFeeLetter_' + str(uniq_id) + '.pdf')
                        AcademicFeeLetter(stu_data, filename)
                        with open(settings.FILE_PATH + 'AcademicFeeLetter/' + filename, 'rb') as pdf:
                            response = HttpResponse(pdf, content_type='application/pdf')
                            response['Content-Disposition'] = 'inline;filename=some_file.pdf'
                            msg = "Success"
                            status = 200
                            return response
                            pdf.closed
                else:
                    status = 502
                    msg = "Bad Request"
            else:
                status = 401
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Not Authorized"
    else:
        status = 500
        msg = "Error"
    data_values = {'msg': msg}
    return JsonResponse(data=data_values, status=status, safe=False)


def convert_amount_to_words(num):
    ones = ["", "One ", "Two ", "Three ", "Four ", "Five ", "Six ", "Seven ", "Eight ", "Nine ", "Ten ", "Eleven ", "Twelve ", "Thirteen ", "Fourteen ", "Fifteen ", "Sixteen ", "Seventeen ", "Eighteen ", "Nineteen "]

    twenties = ["", "", "Twenty ", "Thirty ", "Forty ", "Fifty ", "Sixty ", "Seventy ", "Eighty ", "Ninety "]

    thousands = ["", "Thousand ", "Lac ", "billion ", "trillion ", "quadrillion ", "quintillion ", "sextillion ", "septillion ", "octillion ", "nonillion ", "decillion ", "undecillion ", "duodecillion ", "tredecillion ", "quattuordecillion ", "quindecillion", "sexdecillion ", "septendecillion ", "octodecillion ", "novemdecillion ", "vigintillion "]

    def num99(n):
        c = int(n % 10)  # singles digit
        b = int(((n % 100) - c) / 10)  # tens digit

        t = ""
        h = ""
        if b <= 1:
            h = ones[n % 100]
        elif b > 1:
            h = twenties[b] + ones[c]
        st = t + h
        return st

    def num999(n):
        c = int(n % 10)  # singles digit
        b = int(((n % 100) - c) / 10)  # tens digit
        a = int(((n % 1000) - (b * 10) - c) / 100)  # hundreds digit
        t = ""
        h = ""
        if a != 0 and b == 0 and c == 0:
            t = ones[a] + "Hundred "
        elif a != 0:
            t = ones[a] + "Hundred and "
        if b <= 1:
            h = ones[n % 100]
        elif b > 1:
            h = twenties[b] + ones[c]
        st = t + h
        return st

    def num2word(num):
        if num == 0:
            return 'zero'
        if num <= 99:
            return num99(num)
        if num <= 999:
            return num999(num)
        else:
            n = str(num)
            word = num999(int(n[-3:]))
            n = n[:-3]
            i = 1
            while(len(n) > 0):
                word = num99(int(n[-2:])) + thousands[i] + word
                i = i + 1
                n = n[:-2]

        return word[:-1]

    return num2word(num)


def Comma_function(number):
    number = str(number)
    number_len = len(number)
    if len(number) > 3:
        number = number[:number_len - 3] + "," + number[-3:]

    if len(number) > 6:
        temp_data = ""
        for index, x in enumerate(number[:-4][::-1]):
            temp_data = temp_data + x
            if index % 2 == 1:
                temp_data = temp_data + ","

        number = temp_data[::-1] + number[-4:]
    if number[0] is ",":
        number = number[1:]
    return number


def get_suffix(i):
    j = i % 10
    k = i % 100
    if (j == 1 and k != 11):
        return str(i) + "ST"
    if (j == 2 and k != 12):
        return str(i) + "ND"
    if (j == 3 and k != 13):
        return str(i) + "RD"

    return str(i) + "TH"


def LessonPlanOnPortal(request):
    qry = []
    data_values = []
    Sessions = []
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                # print(request.session['sem'])
                session_name = request.session['Session_name']
                if int(session_name[:2]) < 19:
                    return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                uniq_id = request.session['uniq_id']

                StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
                LessonCompletedTopic = generate_session_table_name("LessonCompletedTopic_", session_name)
                studentSession = generate_session_table_name("studentSession_", session_name)
                LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                if request.method == 'GET':

                    if (request.GET['request_type'] == 'get_dashboard_lesson_plan_data'):
                        date1 = request.GET['date']
                        data_values = []
                        qry_sem = list(studentSession.objects.filter(uniq_id=uniq_id).values('sem'))
                        if len(qry_sem) > 0:
                            subject = get_student_subjects(qry_sem[0]['sem'], session_name)
                            qry = list(StudentAttStatus.objects.filter(att_id__date=date1, uniq_id=uniq_id).exclude(status="DELETE").exclude(att_id__status="DELETE").values('att_id', 'att_id__lecture', 'att_id__normal_remedial', 'att_id__subject_id__sub_name', 'att_id__subject_id__sub_alpha_code', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__subject_type__value', 'att_id__date', 'att_id__emp_id', 'att_id__subject_id').exclude(att_id__subject_id__subject_type__value="LAB").exclude(att_id__subject_id__subject_type__value="VALUE ADDED COURSE").order_by('-att_id__lecture').distinct())

                            if len(qry) > 0:
                                for q in qry:
                                    # print(type(q['att_id__date']))
                                    dictionary = {}
                                    dictionary['subject'] = q['att_id__subject_id__sub_name']
                                    dictionary['data'] = []
                                    dictionary['lecture'] = q['att_id__lecture']
                                    qry1 = list(LessonCompletedTopic.objects.filter(completed_detail__lecture_details=q['att_id']).exclude(status="DELETE").exclude(completed_detail__status="DELETE").values_list('completed_topic__topic_name', flat=True))

                                    if len(qry1) > 0:
                                        qry_unit = list(LessonTopicDetail.objects.filter(subject=q['att_id__subject_id']).exclude(status="DELETE").values_list('unit', flat=True).distinct())
                                        print(qry_unit)
                                        for q1 in qry_unit:
                                            qry_topic = list(LessonTopicDetail.objects.filter(subject=q['att_id__subject_id'], unit=q1, topic_name__in=qry1).exclude(status="DELETE").values_list('topic_name', flat=True).distinct())
                                            if len(qry_topic) > 0:
                                                dictionary['data'].append({'unit': q1, 'topic': qry_topic})
                                    if len(dictionary['data']) > 0:
                                        data_values.append(dictionary)
                        status = 200

                    elif (request.GET['request_type'] == 'get_student_subjects'):
                        qry_sem = list(studentSession.objects.filter(uniq_id=uniq_id).values('sem'))
                        if len(qry_sem) > 0:
                            subject = get_student_subjects(qry_sem[0]['sem'], session_name)
                            data_values.extend(subject)
                        status = 200

                    elif (request.GET['request_type'] == 'get_lesson_plan_data'):
                        try:
                            subject_id = request.GET['subject']
                            lecture_tutorial = request.GET['lecture_tutorial']
                            # qry=LessonCompletedTopic.objects.filter(completed_detail__lecture_details__att_id__subject_id=subject_id)
                            qry = list(StudentAttStatus.objects.filter(att_id__subject_id=subject_id, uniq_id=uniq_id).exclude(status="DELETE").exclude(att_id__status="DELETE").values('att_id', 'att_id__lecture', 'att_id__date').exclude(att_id__subject_id__subject_type__value="LAB").exclude(att_id__subject_id__subject_type__value="VALUE ADDED COURSE").order_by('-att_id__date').distinct())
                            date_list = []
                            for q in qry:
                                print(q['att_id'])
                                print(q['att_id__date'])
                                if str(q['att_id__date']) not in date_list:
                                    date_list.append(str(q['att_id__date']))
                            data = []
                            print(date_list)

                            for x in date_list:
                                dictionary = {}
                                dictionary['date'] = x
                                dictionary['data'] = []
                                # dictionary['lecture']
                                for q in qry:
                                    qry1 = list(LessonCompletedTopic.objects.filter(completed_detail__lecture_details__date=x, completed_detail__lecture_details__id=q['att_id'], completed_detail__lecture_tutorial=lecture_tutorial).exclude(status="DELETE").exclude(completed_detail__status="DELETE").values_list('completed_topic__topic_name', flat=True))
                                    print(qry1)
                                    if len(qry1) > 0:
                                        qry_unit = list(LessonTopicDetail.objects.filter(subject=subject_id).exclude(status="DELETE").values_list('unit', flat=True).distinct())
                                        for q1 in qry_unit:
                                            qry_topic = LessonTopicDetail.objects.filter(subject=subject_id, unit=q1, topic_name__in=qry1).exclude(status="DELETE").values_list('topic_name', flat=True).distinct()
                                            if len(qry_topic) > 0:
                                                dictionary['data'].append({'unit': q1, 'topic': list(qry_topic), 'lecture': q['att_id__lecture']})
                                if len(dictionary['data']) > 0:
                                    data_values.append(dictionary)
                            status = 200
                        except:
                            status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)


def RequiredFormat(unique_id):

    distinct_date = list(MessageList_1920o.objects.filter(sent_by_to__uniq_id=unique_id).extra(select={'date1': 'DATE(time_stamp)'}).values('date1').extra(select={'date1': 'DATE(time_stamp)'}).order_by('date1').distinct())

    final_list = []

    for y in distinct_date:

        data = {
            "date": y['date1'],
            "msg_data": []
        }

        message_list = list(MessageList_1920o.objects.filter(time_stamp__date=y['date1'], sent_by_to__uniq_id=unique_id).values('message', 'user_type', 'time_stamp', 'id', 'status').order_by('time_stamp'))

        data['msg_data'].extend(message_list)

        final_list.append(data)

    return final_list

########################################## MAIN FUNCTION ########################################


def Message(request):

    unique_id = request.session['uniq_id']

    admin_list = [4348, 4245, 233, 319]
    if unique_id in admin_list:
        user_type = "Admin"

    else:
        user_type = "Student"

####################################### INSERT MESSAGE ###########################################

    if requestMethod.POST_REQUEST(request):

        data = json.loads(request.body)

        if 'message' in data:

            if user_type == "Admin":

                user_unique_id = data['user_id']

                new_message = MessageList_1920o.objects.create(message=data['message'], user_type=user_type, sent_by_to=studentSession_1920o.objects.get(uniq_id=user_unique_id))

            else:

                new_message = MessageList_1920o.objects.create(message=data['message'], user_type=user_type, sent_by_to=studentSession_1920o.objects.get(uniq_id=unique_id))

            response = [{"insert": "True", "date": datetime.date(new_message.time_stamp), "time": new_message.time_stamp, "id": new_message.id}]

            return functions.RESPONSE(response, statusCodes.STATUS_SUCCESS)

############################################ REFRESH ###########################################

    elif requestMethod.GET_REQUEST(request):

        if(requestType.custom_request_type(request.GET, 'refresh')):

            if user_type == "Admin":

                send_data = []

                unread = list(MessageList_1920o.objects.filter(read_status="UNREAD", user_type="Student").values('sent_by_to__mob', 'sent_by_to__uniq_id__name', 'sent_by_to__uniq_id__lib', 'sent_by_to__sem__sem', 'sent_by_to__section__section', 'sent_by_to__uniq_id', 'sent_by_to__uniq_id__dept_detail__dept__value').annotate(unread=Count('read_status')))

                unread_user = {}

                for x in unread:
                    unread_user[x['sent_by_to__uniq_id']] = x['unread']

                full_list = list(MessageList_1920o.objects.filter().exclude(user_type="Admin").values('sent_by_to__mob', 'sent_by_to__uniq_id__name', 'sent_by_to__uniq_id__lib', 'sent_by_to__sem__sem', 'sent_by_to__section__section', 'sent_by_to__uniq_id', 'sent_by_to__uniq_id__dept_detail__dept__value').order_by('-time_stamp'))

                unread_user_keys = unread_user.keys()

                parsed_array = []

                for x in full_list:

                    if x['sent_by_to__uniq_id'] not in parsed_array:
                        parsed_array.append(x['sent_by_to__uniq_id'])
                        x["unread"] = 0

                        if x['sent_by_to__uniq_id'] in unread_user_keys:
                            x["unread"] = unread_user[x['sent_by_to__uniq_id']]

                        send_data.append(x)

                return functions.RESPONSE(send_data, statusCodes.STATUS_SUCCESS)

            elif user_type == "Student":

                final_list = RequiredFormat(unique_id)

                if len(final_list) == 0:

                    final_list = [{"date": "", "msg_data": []}]

                return functions.RESPONSE(final_list, statusCodes.STATUS_SUCCESS)

################################## MAIN ACTIVITY #################################################

        elif(requestType.custom_request_type(request.GET, 'main_activity')):

            if user_type == "Admin":

                send_data = []

                unread = list(MessageList_1920o.objects.filter(read_status="UNREAD", user_type="Student").values('sent_by_to__mob', 'sent_by_to__uniq_id__name', 'sent_by_to__uniq_id__lib', 'sent_by_to__sem__sem', 'sent_by_to__section__section', 'sent_by_to__uniq_id', 'sent_by_to__uniq_id__dept_detail__dept__value').annotate(unread=Count('read_status')))

                unread_user = {}

                for x in unread:
                    unread_user[x['sent_by_to__uniq_id']] = x['unread']

                full_list = list(MessageList_1920o.objects.filter().exclude(user_type="Admin").values('sent_by_to__mob', 'sent_by_to__uniq_id__name', 'sent_by_to__uniq_id__lib', 'sent_by_to__sem__sem', 'sent_by_to__section__section', 'sent_by_to__uniq_id', 'sent_by_to__uniq_id__dept_detail__dept__value').order_by('-read_status'))

                unread_user_keys = unread_user.keys()

                parsed_array = []

                for x in full_list:

                    if x['sent_by_to__uniq_id'] not in parsed_array:
                        parsed_array.append(x['sent_by_to__uniq_id'])
                        x["unread"] = 0

                        if x['sent_by_to__uniq_id'] in unread_user_keys:
                            x["unread"] = unread_user[x['sent_by_to__uniq_id']]

                        send_data.append(x)

                return functions.RESPONSE(send_data, statusCodes.STATUS_SUCCESS)

            elif user_type == "Student":

                final_list = RequiredFormat(unique_id)

                if len(final_list) == 0:

                    final_list = [{"date": "", "msg_data": []}]

                return functions.RESPONSE(final_list, statusCodes.STATUS_SUCCESS)

############################## ADMIN CARD CLICK ##################################################

        elif(requestType.custom_request_type(request.GET, 'card_click')):

            unique_id = request.GET['unique_id']

            update = MessageList_1920o.objects.filter(sent_by_to__uniq_id=unique_id).update(read_status="READ")

            response = RequiredFormat(unique_id)

            return functions.RESPONSE(response, statusCodes.STATUS_SUCCESS)

################################## DELETE ####################################################

    elif requestMethod.DELETE_REQUEST(request):

        data = json.loads(request.body)

        if user_type == "Student":

            msg_delete = MessageList_1920o.objects.filter(sent_by_to__uniq_id=unique_id, id=data['id']).update(status="DELETE")

            final_list = RequiredFormat(unique_id)

            return functions.RESPONSE(final_list, statusCodes.STATUS_SUCCESS)

        elif user_type == "Admin":

            user_id = MessageList_1920o.objects.filter(id=data['id']).values('sent_by_to__uniq_id')

            unique_id = user_id[0]['sent_by_to__uniq_id']

            msg_delete = MessageList_1920o.objects.filter(id=data['id']).delete()

            final_list = RequiredFormat(unique_id)

            return functions.RESPONSE(final_list, statusCodes.STATUS_SUCCESS)

######################################################## STUDENT DIGITAL DIRECTORY ######################################################################


def Student_Directory(request):
    unique_id = request.session['uniq_id']
    session_name = request.session['Session_name']
    admin_list=[4307,4730,1835,71,319,1522,2874,348,190,233,1087,954,471,4245,4634,4348]
    if (requestMethod.POST_REQUEST(request)):
        if unique_id in admin_list:
            q = StudentDropdown.objects.filter(field="COURSE").exclude(sno=1).values('value', 'sno')
            d1 = {"Status": "True", "data": list(q)}
            return JsonResponse(d1)
        else:
            d2 = {"Status": "False", "data": {}}
            return JsonResponse(d2)
    elif (requestMethod.GET_REQUEST(request)):
        if (requestType.custom_request_type(request.GET, 'get_branch')):
            Cou = request.GET['course'].split(",")
            drop1 = get_branch(Cou)
            return JsonResponse(list(drop1), safe=False)

        elif (requestType.custom_request_type(request.GET, 'get_sem')):
            Bran = request.GET['branch'].split(",")
            drop2 = get_sem(Bran)
            return JsonResponse(drop2)

        elif (requestType.custom_request_type(request.GET, 'get_sec')):
            Bran = request.GET['branch'].split(",")
            Sem = request.GET['sem'].split(",")
            drop3 = get_sec(Bran, Sem)
            return JsonResponse(drop3)

        elif (requestType.custom_request_type(request.GET, 'get_data')):
            Bran = request.GET['branch'].split(",")
            Sem = request.GET['sem'].split(",")
            Sec = request.GET['sec'].split(",")
            data = get_Detail(Bran, Sem, Sec, session_name)
            return JsonResponse(data, safe=False)


def get_branch(course):
    # course=12,13,14
    q2 = list(CourseDetail.objects.filter(course__in=course).values('uid', 'dept__value', 'course__value'))
    return(q2)


def get_sem(dept):

    # dept=41,42,
    t = datetime.today().date()
    q2 = list(Semtiming.objects.filter(sem_start__lte=t, sem_end__gte=t).values('sem_type'))
    q3 = StudentSemester.objects.none()
    sem = []
    if q2[0]['sem_type'] == "odd":
        q3 = StudentSemester.objects.filter(dept__in=dept).annotate(odd=F('sem') % 2).filter(odd=True).order_by('sem').distinct().values('sem').order_by('sem')
    elif q2[0]['sem_type'] == "even":
        q3 = StudentSemester.objects.filter(dept__in=dept).annotate(odd=F('sem') % 2).filter(odd=False).order_by('sem').distinct().values('sem').order_by('sem')

    t1 = len(q3)
    for x in range(0, t1):
        sem.append(q3[x]['sem'])
    d1 = {'sem': list(sem)}
    return(d1)


def get_sec(dept, sem):
        # dept=41,42.sem=1,3,5,7
    q4 = list(StudentSemester.objects.filter(dept__in=dept, sem__in=sem).values_list('sem_id', flat=True))
    q5 = list(Sections.objects.filter(sem_id__in=q4).annotate(max1=Count('section')).values_list('section', flat=True))
    section = set()
    for q in q5:
        if q not in section:
            section.add(q)

    d1 = {'sec': sorted(section)}
    return(d1)


def get_Detail(dept, sem, sec, session_name):
    # section=A,B...dept=41,41...sem=1,3,4
    data = []
    q4 = list(StudentSemester.objects.filter(dept__in=dept, sem__in=sem).values_list('sem_id', flat=True))
    q5 = list(Sections.objects.filter(dept__in=dept, sem_id__in=q4, section__in=sec).values_list('section_id', flat=True))
    studentSession = generate_session_table_name('studentSession_', session_name)
    print("Current Session", studentSession)
    for x in q5:
        q2 = list(studentSession.objects.filter(section_id=x).values('uniq_id', 'mob', 'class_roll_no', 'sem__sem', 'section__section').order_by('uniq_id__name'))
        for i in q2:
            q3 = list(StudentPrimDetail.objects.filter(uniq_id=i['uniq_id']).values('name', 'dept_detail__dept__value', 'lib_id', 'uni_roll_no', 'email_id', 'uniq_id'))
            i.update(q3[0])
            q4 = list(StudentPerDetail.objects.filter(uniq_id=i['uniq_id']).values('dob'))
            i.update(q4[0])

        data.extend(q2)
    return(data)
########################################################################################################################################################################################################

def get_Internship_details(uniq_id,session_name):
    data = {}
    studentSession = generate_session_table_name("studentSession_", session_name)
    q_prim_per_det = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('uniq_id__dept_detail__course__sno','uniq_id__dept_detail__dept__value')
    q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('year')

    if len(q_prim_per_det)>0:
        if((q_stu_details[0]['year']==2 and q_prim_per_det[0]['uniq_id__dept_detail__course__sno']==17) or (q_stu_details[0]['year']==3 and q_prim_per_det[0]['uniq_id__dept_detail__course__sno']==12)):
            data['eligible']= True
            data['erp']=False
        elif ((q_stu_details[0]['year']==1 and ( 'CSE' in str(q_prim_per_det[0]['uniq_id__dept_detail__dept__value']) or 'IT' in str(q_prim_per_det[0]['uniq_id__dept_detail__dept__value']) or 'CO' in str(q_prim_per_det[0]['uniq_id__dept_detail__dept__value']) or 'CSI' in str(q_prim_per_det[0]['uniq_id__dept_detail__dept__value'])))):
            data['erp']=True
            data['eligible']= False  
        else:
            data['eligible']= False
            data['erp']= False
        intern_qry=list(StudentInternshipPrograms.objects.filter(year=q_stu_details[0]['year'],course_id=q_prim_per_det[0]['uniq_id__dept_detail__course__sno']).exclude(status='DELETE').values('duration','field','to_select'))
        if(len(intern_qry)>0):
            area_intern=intern_qry[0]['field'].split(";")
            data['to_select']=intern_qry[0]['to_select']
            data['duration']=intern_qry[0]['duration']
            data['fields']=area_intern
        else:
            data['to_select']=0
            data['duration']="NOT APPLICABLE"
            data['fields']=[]    
    return (data)


def insert_intern_taken(uniq_id,intern_obj,session_name):
    msg={}
    print(intern_obj)
    if (int(session_name[:2]) < 20):
        studentSession = generate_session_table_name("studentSession_", session_name)
        InternshipsTaken = generate_session_table_name("StudentInternshipsTaken","")
    else:
        InternshipsTaken = generate_session_table_name("StudentInternshipsTakenNew","")
        studentSession = generate_session_table_name("StudentPrimDetail","")

    if(len(intern_obj)>0):
        InternshipsTaken.objects.filter(uniq_id=uniq_id).delete()
        if(len(intern_obj['field'])>0):
            for internship in intern_obj['field']:
                if(intern_obj['erp'] != None ):
                    qry=InternshipsTaken.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),internship=internship,taken=intern_obj['taken'],erp_interest=intern_obj['erp'])                
                else:
                    qry=InternshipsTaken.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),internship=internship,taken=intern_obj['taken'])

            msg['intern']="INSERTED"
        else:
            qry=InternshipsTaken.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),taken=intern_obj['taken'])

    return (msg)



def is_alloted(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                uniq_id = request.session['uniq_id']
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                session = request.session['Session']
                session_name='2021o'
                sem_type='odd'
                if int(session_name[:2]) < 19 or 'even' in str(sem_type):
                    return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
                HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
                HostelRoomAlloted=generate_session_table_name('HostelRoomAlloted_', session_name)
                app_hostel=list(HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values())
                if len(app_hostel)==0:
                    data_values['msg']="You have not opted for hostel"
                    status=200
                else:
                    qry=list(HostelSeatAlloted.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('hostel_part__value','seat_part__value'))
                    if len(qry)>0:
                        data_values['hostel']=qry[0]['hostel_part__value']
                        data_values['seater']=qry[0]['seat_part__value']
                        room_allot=list(HostelRoomAlloted.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('room_part__room_no','room_part__hostel_id__floor__value'))
                        if len(room_allot)==0:
                            data_values['room_details']="Room has not been alloted yet.\n(Kindly submit your hostel fees as per the Hostel Fee Letter first then only room will be alloted.)"
                        else:
                            room={}
                            room['floor']=room_allot[0]['room_part__hostel_id__floor__value']
                            room['room_no']=room_allot[0]['room_part__room_no']
                            data_values['room_details']=room

                        status=200
                        # data['msg']=f"You have been alloted {qry[0]['seat_part__value']} seater in {qry[0]['hostel_part__value']}"
                    elif len(qry)==0:
                        data_values['msg']="No seat is alloted"
                        status=200
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data_values, safe=False)





def generate_tution_certificate(stu_data,fee_data ,fname,filename,fee_id,session_session):
    # print(stu_data,stu_data)
    receipt_name = "CERTIFICATE OF TUITION FEE"
    # filename="HostelFeeLetter.pdf"
    q_mop_details = ModeOfPaymentDetails.objects.filter(fee_id=fee_id).values('MOPcomponent__value', 'value')
    fee_rec_no =""
    for i,n in enumerate(list(fee_data)):
        if (i<len(list(fee_data))-1):
            fee_rec_no = fee_rec_no + n['fee_rec_no'] + ","
        else:
            fee_rec_no = fee_rec_no + n['fee_rec_no']
    fee_comp_details = SubmitFeeComponentDetails.objects.filter(fee_id=fee_id).values('fee_component__value', 'fee_sub_component__value', 'sub_component_value').order_by('fee_component', 'fee_sub_component')
    print(fee_comp_details)
    tution_fee = "----"
    for comp in fee_comp_details:
        if comp['fee_component__value'] == 'ACADEMIC' and comp['fee_sub_component__value'] == 'TUITION FEE':
            if comp['sub_component_value'] > 0:
                tution_fee = str(int(comp['sub_component_value']))
    img = Image.new(mode='RGB', size=(1478, 2100), color=(255, 255, 255, 0))
    kiet = Image.open(settings.FILE_PATH + "KIET_Header.png")
    kiet = kiet.convert('RGB')
    kiet = kiet.resize((900, 170))
    img.paste(kiet, (300, 30))
    size = 2480, 3508
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 40)
    fb = ImageFont.truetype(settings.FILE_PATH + "arialbd.ttf", 40)
    font_bold = ImageFont.truetype(settings.FILE_PATH + "OpenSans-Bold.ttf", 35)
    font_bold_large = ImageFont.truetype(settings.FILE_PATH + "arialbd.ttf", 50)
    final_img_width = min(img.size[0], 1478)
    final_img_height = min(img.size[1], 2100)
    tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")
    draw.text((100,190),str('__________________________________________________________________________________________'), (0, 0, 0), font=font_bold)
    draw.text((100,200),str('__________________________________________________________________________________________'), (0, 0, 0), font=font_bold)
    try:
        date_data = datetime.strptime(str(fee_data[0]['time_stamp']).split('T')[0], "%Y-%m-%d").strftime("%d-%m-%Y")
    except:
        date_data = datetime.strptime(str(fee_data[0]['time_stamp']).split(' ')[0], "%Y-%m-%d").strftime("%d-%m-%Y")
    draw.text((130, 250), "An ISO - 90012008 Certified & 'A' Grade accredited Institution by NAAC " , (0, 0, 0), font=font_bold)
    draw.text((1100, 350), "Dated: "+str(date_data), (0, 0, 0), font=font_bold)  # gap=15

    draw.text((350, 500), "TO WHOM IT MAY CONCERN", (0, 0, 0), font=font_bold_large)  # gap=15

    draw.text((70, 650), "This is to certify that", (0, 0, 0), font=font)  # gap=15
    draw.text((440,650), "Mr/Ms. "+ str(fee_data[0]['uniq_id__name'].title()) +" S/D/O Mr. " + str(fname.title()),(0, 0, 0), font=fb)
    draw.text((70, 720), "is studying in our Institute in ", (0, 0, 0), font=font)
    draw.text((570,720),str(stu_data[0]['sem__dept__course__value'].title()),(0, 0, 0), font=fb)
    draw.text((700,720)," Degree course in " ,(0, 0, 0), font=font)
    draw.text((1022,720),str(stu_data[0]['uniq_id__dept_detail__dept__value']),(0, 0, 0), font=fb )
    draw.text((1052,720), " Branch in " + str(stu_data[0]['year']) +" year .",(0, 0, 0), font=font)
    draw.text((70, 900), "Further certify that he/she has paid  " + "Rs"+tution_fee+"/- " + "as Tution fee for " + str(session_session), (0, 0, 0), font=font)
    draw.text((70,970), "session wise receipt no. " , (0, 0, 0), font=font)
    draw.text((500,970),  str(fee_rec_no) + ".",(0, 0, 0), font=fb)
    draw.text((70,1170), "For KIET GROUP OF INSTITUTIONS ", (0, 0, 0), font=font_bold)
    sign = Image.open(settings.FILE_PATH + "Arunji_Sign.jpg")
    sign = sign.convert('RGB')
    sign = sign.resize((200, 140))
    img.paste(sign, (50, 1330))
    draw.text((50, 1500), str('(Accounts Officer)'), font=font_bold, fill="#000000")
    draw.text((50, 1570), str("KIET Group of Institutions,"), font=font_bold, fill="#000000")
    draw.text((50, 1640), str("Ghaziabad"), font=font_bold, fill="#000000")
    draw.text((50, 1840), str("NOTE : This is a computer generated document."), font=font_bold, fill="#000000")
    index = 0
    x = index // 2 * (tmp_image.size[0] // 2)
    y = index % 2 * (tmp_image.size[1] // 2)
    w, h = img.size
    tmp_image.paste(img, (x, y, x + w, y + h))

    tmp_image.save(settings.FILE_PATH + 'Tution_certificate/fee_let.pdf', "PDF", resolution=250.0)

    merger = PdfFileMerger()

    pdfs = [settings.FILE_PATH + 'Tution_certificate/fee_let.pdf']
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))

    with open(settings.FILE_PATH + 'Tution_certificate/' + filename, 'wb') as fout:
        merger.write(fout)


def print_tution_certificate(request):
    msg = ""
    status = 401
    if request.META:
        if request.method == 'GET':
            studentSession = generate_session_table_name('studentSession_', '2021o')
            session_name = request.session['Session_name']
            session_id = request.session['Session_id']
            session_session = request.session['Session'] 
            student_session = generate_session_table_name("studentSession_", session_name)
            uniq_id = request.GET['uniq_id']
            q_check = SubmitFee.objects.filter(uniq_id=uniq_id,session__session="2020-2021").exclude(status="DELETE").values('fee_rec_no', 'uniq_id__name', 'cancelled_status', 'actual_fee', 'paid_fee', 'refund_value', 'due_value', 'session__session', 'receipt_type', 'id', 'time_stamp', 'uniq_id', 'receipt_type', 'prev_fee_rec_no').order_by('-id')
            if len(q_check)>0:
                if q_check[0]['due_value']==0 or q_check[0]['due_value'] is None :
                    fee_id = q_check[0]['id']
                    stu_per = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname')
                    if len(stu_per) > 0 and stu_per[0]['fname'] is not None :
                        fname = stu_per[0]['fname']
                    else:
                        fname = "----"
                    stu_data = student_session.objects.filter(uniq_id=uniq_id).values('year', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__exam_roll_no')
                    filename = str('Tution_certificate_' + str(q_check[0]['uniq_id__name']) + '.pdf')
                    generate_tution_certificate(stu_data,q_check,fname,filename,fee_id,session_session)
                    with open(settings.FILE_PATH + 'Tution_certificate/' + filename, 'rb') as pdf:
                        response = HttpResponse(pdf, content_type='application/pdf')
                        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
                        msg = "Success"
                        status = 200
                        return response
                        pdf.closed
                else:
                    status = 202
                    msg = "Sorry , you are not eligible as your academic fees is due."
            else:
                status = 404
                msg = "Fee Receipt Not found for this session"
        else:
          status = 502
          msg = 'Bad Gateway'
    else:
        status = 500
        msg = "Error"
    return JsonResponse(data={'msg':msg},status=status)


