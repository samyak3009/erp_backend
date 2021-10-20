'''LEFT TO ADD CREATE DUE RECIEPT AND REFUND RECIEPT FOR CHANGE IN SEAT'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
import json
import urllib
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum, F
from django.http import HttpResponse, JsonResponse
import time
from PyPDF2 import PdfFileMerger, PdfFileReader
from PIL import ImageDraw
import qrcode
import io
from threading import Thread
import requests
from random import randint
import time
from PIL import Image, ImageChops, ImageOps
from PIL import ImageFont
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum, Count, Max
# from datetime import datetime
import datetime
from datetime import date
import pytz
from datetime import datetime
import calendar
from operator import itemgetter
from StudentMMS.constants_functions import requestType

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

from login.models import EmployeeDropdown, EmployeePrimdetail, AuthUser,Daksmsstatus
from attendance.models import Attendance2
from Registrar.models import *
from StudentHostel.models import *
from .models import *
from login.models import EmployeePrimdetail, Daksmsstatus 

from StudentHostel.views import *
from StudentPortal.views import get_stu_data as get_stu_data
from login.views import checkpermission, generate_session_table_name,Sms_Api
from StudentPortal.views import AcademicFeeLetter as AcademicFeeLetter
from StudentHostel.views.hostel_function import acc_get_student_eligible_seater, get_student_eligible_seater, get_student_eligible_seater_acc, get_uniq_id_alloted_seater, get_hostel_occupied_un_capacity
from StudentMMS.constants_functions import requestType

# Create your views here.


def Student_Accounts_dropdown(request):
    data = {}
    qry1 = ""

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'general':
                        qry1 = StudentAccountsDropdown.objects.filter(value=None).extra(select={'fd': 'field', 'id': 'sno', 'parent': 'pid'}).values('fd', 'id', 'parent').exclude(status="DELETE").distinct()
                        for field1 in qry1:
                            if field1['parent'] != 0:
                                pid = field1['parent']
                                qry2 = StudentAccountsDropdown.objects.filter(sno=pid).exclude(status="DELETE").values('field')
                                field1['fd'] = field1['fd'] + '(' + qry2[0]['field'] + ')'
                        msg = "Success"
                        error = False
                        if not qry1:
                            msg = "No Data Found!!"
                        status = 200
                        data = {'msg': msg, 'data': list(qry1)}

                    elif request.GET['request_type'] == 'subcategory':
                        sno = request.GET['Sno']
                        names = StudentAccountsDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('field', 'pid')
                        name = names[0]['field']
                        p_id = names[0]['pid']

                        qry1 = StudentAccountsDropdown.objects.filter(field=name, pid=p_id).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'valueid': 'sno', 'parentId': 'pid', 'cat': 'field', 'text1': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('valueid', 'parentId', 'cat', 'text1', 'edit', 'delete')
                        for x in range(0, len(qry1)):
                            test = StudentAccountsDropdown.objects.filter(pid=qry1[x]['valueid']).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'subid': 'sno', 'subvalue': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('subid', 'subvalue', 'edit', 'delete')
                            qry1[x]['subcategory'] = list(test)
                        msg = "Success"
                        data = {'msg': msg, 'data': list(qry1)}
                        status = 200

                elif request.method == 'DELETE':
                    data = json.loads(request.body)
                    qry = StudentAccountsDropdown.objects.filter(sno=data['del_id']).exclude(status="DELETE").values('field')
                    if(qry.exists()):

                        sno = data['del_id']
                        fd = qry[0]['field']
                        deletec(sno)
                        q2 = StudentAccountsDropdown.objects.filter(field=fd).exclude(status="DELETE").exclude(value__isnull=True).values().count()
                        if q2 == 0:
                            q3 = StudentAccountsDropdown.objects.filter(field=fd).exclude(status="DELETE").update(status="DELETE")
                        msg = "Data Successfully Deleted..."
                        status = 200
                    else:
                        msg = "Data Not Found!"
                        status = 404
                    data = {'msg': msg}
                    status = 200
                elif request.method == 'POST':
                    body1 = json.loads(request.body)

                    for body in body1:
                        pid = body['parentid']
                        value = body['val'].upper()
                        field_id = body['cat']
                        field_qry = StudentAccountsDropdown.objects.filter(sno=field_id).exclude(status="DELETE").values('field')
                        field = field_qry[0]['field']
                        if pid != 0:
                            field_qry = StudentAccountsDropdown.objects.filter(sno=pid).exclude(status="DELETE").exclude(value__isnull=True).values('value')
                            field = field_qry[0]['value']
                            cnt = StudentAccountsDropdown.objects.filter(field=field).exclude(status="DELETE").values('sno')
                            if len(cnt) == 0:
                                add = StudentAccountsDropdown.objects.create(pid=pid, field=field)

                        qry_ch = StudentAccountsDropdown.objects.filter(Q(field=field) & Q(value=value)).filter(pid=pid).exclude(status="DELETE")
                        if(len(qry_ch) > 0):
                            status = 409

                        else:
                            created = StudentAccountsDropdown.objects.create(pid=pid, field=field, value=value)
                            msg = "Successfully Inserted"
                            data = {'msg': msg}
                            status = 200

                elif request.method == 'PUT':
                    body = json.loads(request.body)
                    sno = body['sno1']
                    val = body['val'].upper()
                    field_qry = StudentAccountsDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('pid', 'value')
                    pid = field_qry[0]['pid']
                    value = field_qry[0]['value']
                    add = StudentAccountsDropdown.objects.filter(pid=pid, field=value).exclude(status="DELETE").update(field=val)
                    add = StudentAccountsDropdown.objects.filter(sno=sno).exclude(status="DELETE").update(value=val, status="UPDATE")
                    add = StudentAccountsDropdown.objects.filter(pid=sno).exclude(status="DELETE").update(field=val, status="UPDATE")
                    msg = "Successfully Updated"
                    data = {'msg': msg}
                    status = 200

            else:
                status = 403
        else:
            status = 401
    else:
        status = 400
    return JsonResponse(status=status, data=data)


def deletec(pid):
    qry = StudentAccountsDropdown.objects.filter(pid=pid).exclude(status="DELETE").values('sno')
    if len(qry) > 0:
        for x in qry:
            deletec(x['sno'])
    qry = StudentAccountsDropdown.objects.filter(sno=pid).exclude(status="DELETE").update(status="DELETE")


########################################################-START- Divyanshu - made changes for 1st year students ##########################################################

def is_direct_seat_allotment(check_data, seater, session_name, session,hostel_id):
    if ((check_data['year'] == 2 and 'LATERAL' in check_data['admission_type__value']) or (check_data['year'] == 1)):
        seater_value = HostelDropdown.objects.filter(sno=seater).values_list('value', flat=True)[0]
        flag = 0
        un_occupied_capacity = get_hostel_occupied_un_capacity(hostel_id, session_name, session)
        if seater_value in un_occupied_capacity:
            if un_occupied_capacity[seater_value] <= 0:
                return [True, -1]
            else:
                return [True, hostel_id]
        else:
            return [True, -1]   
    return [False, -1]



def acc_get_hostel_component(uniq_id, session):
    fee_comp_details = []
    fee_comp_details = SubmitFeeComponentDetails.objects.filter(fee_id__uniq_id=uniq_id, fee_id__session=session).exclude(fee_id__status="DELETE").values('fee_component__value', 'fee_sub_component__value', 'sub_component_value', 'fee_component', 'fee_sub_component', 'fee_id__fee_rec_no')
    data = {}
    data['is_ac'] = "NO"
    data['is_bedding'] = "NO"
    data['is_laundary'] = "NO"
    for x in fee_comp_details:
        if 'H' in x['fee_id__fee_rec_no']:
            data['reciept_no'] = x['fee_id__fee_rec_no']
        if "AIR CONDITIONER" in x['fee_sub_component__value']:
            data['is_ac'] = "YES"

        if "LAUNDRY" in x['fee_sub_component__value']:
            data['is_laundary'] = "YES"

        if "BEDDING" in x['fee_sub_component__value']:
            data['is_bedding'] = "YES"
    return data


def get_next_fee_receipt_no(fee_initial):
    q_find = StudentAccountsDropdown.objects.filter(field="FEE INITIAL", value=fee_initial).exclude(status="DELETE").values('sno')
    q_find2 = StudentAccountsDropdown.objects.filter(pid=q_find[0]['sno']).exclude(status="DELETE").exclude(value__isnull=True).values('value')
    # q_find = SubmitFee.objects.filter(fee_rec_no__contains=fee_initial).exclude(session__in=exc_sess).values('fee_rec_no').order_by('-id')[:1]
    # if len(q_find)==0:
    #   return fee_initial+str(1)
    # else:
    #   fee_rec_no=int(q_find[0]['fee_rec_no'].split(fee_initial)[1])
    #   return fee_initial+str(fee_rec_no+1)
    return fee_initial + str(q_find2[0]['value'])


def update_fee_rec_no(fee_initial, fee_rec_no):
    q_find = StudentAccountsDropdown.objects.filter(field="FEE INITIAL", value=fee_initial).exclude(status="DELETE").values('sno')
    q_find2 = StudentAccountsDropdown.objects.filter(pid=q_find[0]['sno']).exclude(status="DELETE").exclude(value__isnull=True).values('sno', 'value')
    fee_rec = int(q_find2[0]['value']) + 1
    q_update = StudentAccountsDropdown.objects.filter(sno=q_find2[0]['sno']).update(value=str(fee_rec))


def getJoinYear():
    join_year = []
    curr_year = date.today().year
    while curr_year > 2009:
        join_year.append(curr_year)
        curr_year -= 1
    return join_year


def get_course_all():
    data = []
    data.append({"sno": "ALL", 'value': "ALL"})
    qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    data.extend(list(qry))
    return data


def get_seater(session):
    if session < 8:
        qry = HostelDropdown.objects.filter(field="SEATER TYPE", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    else:
        qry = HostelDropdown.objects.filter(field="BED CAPACITY", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    return list(qry)

# ##################### CHANGE KARNA HAI ################################
# def get_student_eligible_seater(uniq_id, session):
#   qry=HostelDropdown.objects.filter(field="SEATER TYPE", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
#   return list(qry)
# ######### END ###### CHANGE KARNA HAI #################################


def get_course():
    qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    return list(qry)


def get_admission_status():
    qry = StudentDropdown.objects.filter(field="ADMISSION STATUS").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    return list(qry)


def get_fee_initial():
    qry = StudentAccountsDropdown.objects.filter(field="FEE INITIAL").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    return list(qry)


def get_caste():
    qry = StudentDropdown.objects.filter(field="CASTE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    return list(qry)


def get_mode_of_payment():
    data = {}
    qry = StudentAccountsDropdown.objects.filter(field="MODE OF PAYMENT").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    for q in qry:
        data2 = {}
        qr = StudentAccountsDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
        for r in qr:
            data2[r['sno']] = r['value']
        data[q['value']] = data2

    return data


def getPenalty():
    qry = StudentAccountsDropdown.objects.filter(field="PENALTY/FINE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    return list(qry)


def get_fee_component():
    data = []
    qry = StudentAccountsDropdown.objects.filter(field="FEE COMPONENTS").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    for q in qry:
        qr = StudentAccountsDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
        data.append({'id': q['sno'], 'component_name': q['value'], 'data': list(qr)})

    return data


def get_fee_component_filtered(uniq_id, session):
    data = []

    qry = StudentAccountsDropdown.objects.filter(field="FEE COMPONENTS").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    for q in qry:

        # q_fee_comp = SubmitFeeComponentDetails.objects.filter(fee_id__session=Semtiming.objects.get(uid=session),fee_id__uniq_id=uniq_id,fee_component=q['sno']).values('fee_id__status','fee_id__cancelled_status').order_by('-id')[:1]

        # if len(q_fee_comp)>0:
        #   if q_fee_comp[0]['fee_id__status']=='DELETE' or q_fee_comp[0]['fee_id__cancelled_status'] == 'Y':
        #       qr=StudentAccountsDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
        #       data.append({'id':q['sno'],'component_name':q['value'],'data':list(qr)})
        # else:
        qr = StudentAccountsDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
        data.append({'id': q['sno'], 'component_name': q['value'], 'data': list(qr)})

    return data


def get_custom_field_stu_acc(field_name):
    data = []
    data = list(StudentAccountsDropdown.objects.filter(field=field_name.split("(")[0]).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value"))
    return data


def get_branch(course):
    qry = CourseDetail.objects.filter(course_id__in=course).exclude(dept_id__value='AS').values("uid", "dept_id", "dept_id__value", 'course__value', "course_duration")
    return list(qry)


def get_years(branch):
    if branch == 'ALL':
        qry = CourseDetail.objects.all().aggregate(Max('course_duration'))
        year_li = list(range(1, qry['course_duration__max'] + 1))
        return year_li
    else:
        qry = CourseDetail.objects.filter(uid__in=branch.split(',')).values_list("course_duration", flat=True)
        year_li = list(range(1, max(qry) + 1))
        return year_li


def get_gender():
    qry = StudentDropdown.objects.filter(field="GENDER").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    return list(qry)


def get_transport():
    qry = StudentAccountsDropdown.objects.filter(field="TRANSPORTATION").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    return list(qry)


def get_students(branch, year, gender, session_name):

    student_session = generate_session_table_name("studentSession_", session_name)
    qry_select_stu = student_session.objects.filter(uniq_id__dept_detail__in=branch, year__in=year, uniq_id__gender__in=gender).exclude(uniq_id__in=student_session.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no', 'year', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value').order_by('uniq_id__name')
    for q in qry_select_stu:
        q['sem__dept__dept__value'] = q['uniq_id__dept_detail__dept__value']

        aadhar_num = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('aadhar_num', 'fname', 'image_path')
        if q['uniq_id__uni_roll_no'] is None or q['uniq_id__uni_roll_no'] == '':
            q['bracket_val'] = aadhar_num[0]['aadhar_num']
            
        else:
            q['bracket_val'] = q['uniq_id__uni_roll_no']
        q['fname'] = aadhar_num[0]['fname']
        if aadhar_num[0]['image_path'] is not None:
            q['image_path'] = settings.BASE_URL2 + "StudentMusterroll/Student_images/" + aadhar_num[0]['image_path']
        else:
            q['image_path'] = settings.BASE_URL2 + "StudentMusterroll/Student_images/default.jpg"

    return list(qry_select_stu)


def get_batch_dropdown(dept):
    qry = SubmitFee.objects.filter(uniq_id__dept_detail=dept).values('uniq_id__batch_from').distinct().order_by('uniq_id__batch_from')
    return list(qry)


def get_filtered_students(branch, batch_from, gender):
    qry_select_stu = StudentPrimDetail.objects.filter(dept_detail__in=branch, batch_from__in=batch_from, gender__in=gender).values('name', 'uniq_id', 'uni_roll_no', 'dept_detail__dept__value', 'dept_detail__course__value').order_by('name')
    for q in qry_select_stu:
        aadhar_num = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('aadhar_num', 'fname', 'image_path')
        if q['uni_roll_no'] is None or q['uni_roll_no'] == '':
            q['bracket_val'] = aadhar_num[0]['aadhar_num']
        else:
            q['bracket_val'] = q['uni_roll_no']

        q['fname'] = aadhar_num[0]['fname']
        if aadhar_num[0]['image_path'] is not None:
            q['image_path'] = settings.BASE_URL2 + "StudentMusterroll/Student_images/" + aadhar_num[0]['image_path']
        else:
            q['image_path'] = settings.BASE_URL2 + "StudentMusterroll/Student_images/default.jpg"
    return list(qry_select_stu)


# def generate_lib_id(uniq_id):
#   q_stu_det = StudentPrimDetail.objects.filter(uniq_id=uniq_id, lib__isnull=True).values('dept_detail__dept__value', 'dept_detail__course__value', 'batch_from', 'batch_to')
#   if len(q_stu_det) > 0:
#       bfrom = q_stu_det[0]['batch_from'] % 2000
#       bto = q_stu_det[0]['batch_to'] % 2000

#       lib_id = str(bfrom) + str(bto)
#       lib_char = ""
#       if q_stu_det[0]['dept_detail__dept__value'] == 'CSE':
#           lib_char = "CS"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'IT':
#           lib_char = "IT"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'EN':
#           lib_char = "EN"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'ECE':
#           lib_char = "EC"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'EIE':
#           lib_char = "EI"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'ME':
#           lib_char = "ME"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'CE':
#           lib_char = "CE"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'CSI':
#           lib_char = "CSI"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'CO':
#           lib_char = "CO"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'MBA':
#           lib_char = "MBA"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'MCA':
#           lib_char = "MCA"
#       elif q_stu_det[0]['dept_detail__dept__value'] == 'KSOP':
#           lib_char = "PH"
#       else:
#           return

#       if q_stu_det[0]['dept_detail__course__value'] == "M.TECH":
#           lib_char = "M" + lib_char
#       elif q_stu_det[0]['dept_detail__course__value'] == "B.PHARMA":
#           lib_char = "B" + lib_char
#       elif q_stu_det[0]['dept_detail__course__value'] == "M.PHARMA (PHARMACEUTICS)":
#           lib_char = "PHT"
#       elif q_stu_det[0]['dept_detail__course__value'] == "M.PHARMA (PHARMACOLOGY)":
#           lib_char = "PHL"

#       lib_id = lib_id + lib_char
#       q_lib = AuthUser.objects.filter(username__contains=lib_id).values('username').order_by('-username')[:1]
#       exclude = []
#       if len(q_lib) > 0:
#           last4 = int(q_lib[0]['username'][-4:]) + 1
#           lib_check = lib_id + str(last4)
#           q_check = StudentPrimDetail.objects.filter(lib=lib_check).values()
#           while len(q_check) > 0:
#               last4 += 1
#               lib_check = lib_id + str(last4)
#               q_check = StudentPrimDetail.objects.filter(lib=lib_check).values()
#           lib_id = lib_check

#           q_user = User.objects.create_user(username=lib_id, password="KIET123")
#           q_upd = StudentPrimDetail.objects.filter(uniq_id=uniq_id).update(lib=AuthUser.objects.get(username=lib_id))
#           q_upd2 = AuthUser.objects.filter(username=lib_id).update(user_type='Student')
#       else:
#           lib_id = lib_id + "1001"
#           q_user = User.objects.create_user(username=lib_id, password="KIET123")
#           q_upd = StudentPrimDetail.objects.filter(uniq_id=uniq_id).update(lib=AuthUser.objects.get(username=lib_id))
#           q_upd2 = AuthUser.objects.filter(username=lib_id).update(user_type='Student')
#   return




def generate_lib_id(uniq_id):
    q_stu_det = StudentPrimDetail.objects.filter(uniq_id=uniq_id, lib__isnull=True).values('dept_detail__dept__value', 'dept_detail__course__value', 'batch_from', 'batch_to')
    if len(q_stu_det) > 0:
        bfrom = q_stu_det[0]['batch_from'] % 2000
        bto = q_stu_det[0]['batch_to'] % 2000

        lib_id = str(bfrom) + str(bto)
        lib_char = ""
        if q_stu_det[0]['dept_detail__dept__value'] == 'CSE':
            lib_char = "CSE"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'IT':
            lib_char = "IT"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'EN':
            lib_char = "EN"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'ECE':
            lib_char = "EC"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'EIE':
            lib_char = "EI"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'ME':
            lib_char = "ME"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'CE':
            lib_char = "CE"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'CSIT':
            lib_char = "CSIT"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'CS':
            lib_char = "CS"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'MBA':
            lib_char = "MBA"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'MCA':
            lib_char = "MCA"
        elif q_stu_det[0]['dept_detail__dept__value'] == 'KSOP':
            lib_char = "PH"
        else:
            return

        if q_stu_det[0]['dept_detail__course__value'] == "M.TECH":
            lib_char = "M" + lib_char
        elif q_stu_det[0]['dept_detail__course__value'] == "B.PHARMA":
            lib_char = "B" + lib_char
        elif q_stu_det[0]['dept_detail__course__value'] == "M.PHARMA (PHARMACEUTICS)":
            lib_char = "PHT"
        elif q_stu_det[0]['dept_detail__course__value'] == "M.PHARMA (PHARMACOLOGY)":
            lib_char = "PHL"

        lib_id = lib_id + lib_char
        if lib_char=='CS':
            q_lib = AuthUser.objects.filter(username__startswith=lib_id).filter(username__length__lt=11).values('username').order_by('-username')[:1]
        else:
            q_lib = AuthUser.objects.filter(username__startswith=lib_id).values('username').order_by('-username')[:1]
        exclude = []
        if len(q_lib) > 0:
            print(q_lib[0])
            last4 = int(q_lib[0]['username'][-4:]) + 1
            lib_check = lib_id + str(last4)
            q_check = StudentPrimDetail.objects.filter(lib=lib_check).values()
            while len(q_check) > 0:
                last4 += 1
                lib_check = lib_id + str(last4)
                q_check = StudentPrimDetail.objects.filter(lib=lib_check).values()
            lib_id = lib_check

            q_user = User.objects.create_user(username=lib_id, password="KIET123")
            q_upd = StudentPrimDetail.objects.filter(uniq_id=uniq_id).update(lib=AuthUser.objects.get(username=lib_id))
            q_upd2 = AuthUser.objects.filter(username=lib_id).update(user_type='Student')
        else:
            lib_id = lib_id + "1001"
            q_user = User.objects.create_user(username=lib_id, password="KIET123")
            q_upd = StudentPrimDetail.objects.filter(uniq_id=uniq_id).update(lib=AuthUser.objects.get(username=lib_id))
            q_upd2 = AuthUser.objects.filter(username=lib_id).update(user_type='Student')
    return





##########################################CODE TO GENERATE LIB ID BY FOR CS/CSIT YASH ###################################
# def get_stu_for_lib(request):
#   qry = StudentPrimDetail.objects.filter(batch_from=2020,batch_to=2024,dept_detail__in=[48,49],lib__isnull=True).values_list('uniq_id',flat=True)
#   print(len(qry),qry,'yash')
#   c=0
#   for q in qry:
#       if (SubmitFee.objects.filter(uniq_id=q,session=10).exclude(status="DELETE").exists()):
#           c=c+1
#           generate_lib_id(q)
#   print(c,'yc')
#   return JsonResponse({'msg':'suc'})
#####################################################################################################################
    


def getComponents(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session = request.session['Session_id']
                session_name = request.session['Session_name']
                if(request.method == 'GET'):
                    if request.GET['request_type'] == 'course':
                        query = get_course()
                    elif request.GET['request_type'] == 'branch':
                        query = get_branch(request.GET['course'].split(","))
                    elif request.GET['request_type'] == 'year':
                        query = get_years(request.GET['branch'])
                    elif request.GET['request_type'] == 'gender':
                        query = get_gender()
                    elif request.GET['request_type'] == 'fee_initial':
                        query = get_fee_initial()
                    elif request.GET['request_type'] == 'mode_of_payment':
                        query = get_mode_of_payment()
                    elif request.GET['request_type'] == 'transportation':
                        query = get_transport()
                    elif request.GET['request_type'] == 'get_batch_dropdown':
                        query = get_batch_dropdown(request.GET['dept'])
                    elif request.GET['request_type'] == 'students':
                        gender = request.GET['gender'].split(',')
                        query = get_students(request.GET['branch'].split(","), request.GET['year'].split(","), gender, session_name)
                    elif request.GET['request_type'] == 'filtered_students':
                        gender = request.GET['gender'].split(',')
                        query = get_filtered_students(request.GET['branch'].split(","), request.GET['batch_from'].split(","), gender)

########################################################-START- Divyanshu - made changes for 1st year students ##########################################################
                    elif request.GET['request_type'] == 'get_hostel_dropdown':
                        year = request.GET['year']
                        if request.GET['gender'] == 'B':
                            gender = ['BOYS','GIRLS']
                        else:    
                            genders=list(StudentDropdown.objects.filter(sno__in=request.GET['gender'].split(',')).values('value'))
                            gender= [ "BOYS" if g['value']=='MALE' else "GIRLS" for g in genders]
                        print(gender)
                        query = list(HostelSetting.objects.filter(year=year,branch=request.GET['course_id'].split(",")[0],hostel_id__hostel_id__field__in=gender, hostel_id__hostel_id__session=session).exclude(status="DELETE").values('hostel_id__hostel_id','hostel_id__hostel_id__value').distinct())
                        print(query,"asasasasasasssssssssssssssssssssssssssssssss")
                    elif request.GET['request_type'] == 'get_stu_hostel':
                        uniq_id = request.GET['uniq_id']
                        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
                        query = list(HostelSeatAlloted.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('hostel_part__sno','seat_part__sno')) 
######################################################## END- Divyanshu - made changes for 1st year students ############################################################
                    elif request.GET['request_type'] == 'refund_filter_students':
                        gender = request.GET['gender'].split(',')
                        refund_type = request.GET['refund_type']
                        branch = request.GET['branch'].split(",")
                        year = request.GET['year'].split(",")
                        if refund_type == 'W':
                            student_session = generate_session_table_name("studentSession_", session_name)
                            query = student_session.objects.filter(uniq_id__dept_detail__in=branch, year__in=year, uniq_id__gender__in=gender, uniq_id__admission_status__value="WITHDRAWAL").values('uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no').order_by('uniq_id__name')
                            for q in query:
                                if q['uniq_id__uni_roll_no'] is None or q['uniq_id__uni_roll_no'] == '':
                                    q['bracket_val'] = q['uniq_id']
                                else:
                                    q['bracket_val'] = q['uniq_id__uni_roll_no']
                        elif refund_type == 'E':
                            student_session = generate_session_table_name("studentSession_", session_name)
                            qry_select_stu = student_session.objects.filter(uniq_id__dept_detail__in=branch, year__in=year, uniq_id__gender__in=gender).exclude(uniq_id__in=student_session.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED"))).values_list('uniq_id__uniq_id', flat=True)
                            query = SubmitFee.objects.filter(refund_value__gt=0, uniq_id__in=(qry_select_stu), session=session).values('uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no').order_by('uniq_id__name')
                            for q in query:
                                if q['uniq_id__uni_roll_no'] is None or q['uniq_id__uni_roll_no'] == '':
                                    q['bracket_val'] = q['uniq_id']
                                else:
                                    q['bracket_val'] = q['uniq_id__uni_roll_no']
                    status = 200
                    data_values = {'data': (query)}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def fee_settings(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session = request.session['Session_id']
                if request.method == 'GET':
                    if request.GET['request_type'] == 'form_data':
                        course = get_course_all()
                        fee_component = get_fee_component()
                        admission_status = get_admission_status()
                        join_year = getJoinYear()
                        caste = get_caste()
                        seater = get_seater(session)

                        msg = "Success"
                        status = 200
                        data_values = {'msg': msg, 'data': {'join_year': join_year, 'course': course, 'fee_component': fee_component,
                                                            'admission_status': admission_status, 'caste': get_caste(), 'seater_type': get_seater(session)}}

                    elif request.GET['request_type'] == 'view_previous':
                        qry = StuAccFeeSettings.objects.extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y %%H:%%i:%%s')"}).filter(session=session).exclude(status="DELETE").values('course_id__value', 'course_id', 'fee_component', 'fee_component__value', 'admission_status', 'admission_status__value', 'join_year', 'fee_component_cat', 'fee_component_cat__value', 'session__session', 'time_stamp', 'caste', 'caste__value', 'value', 'fee_waiver', 'gender__value', 'seater_type__value', 'id')

                        for q in qry:
                            if q['seater_type__value'] is not None:
                                q['seater_type__value'] = q['seater_type__value']

                            if q['gender__value'] == 'MALE':
                                q['gender__value'] = 'BOY'
                            elif q['gender__value'] == 'FEMALE':
                                q['gender__value'] = 'GIRL'
                        status = 200
                        data_values = {'data': list(qry)}
                elif request.method == 'POST':
                    data = json.loads(request.body)
                    msg = "Fee Component Successfully Inserted"
                    emp_id = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                    course = data['course']
                    c_id = []
                    if course == "ALL":
                        c_id = get_course()
                    else:
                        c_id.append({"sno": course, 'value': "course"})
                    caste = list(data['caste'])
                    fee_component = data['fee_component']
                    admission_status = list(data['admission_status'])
                    join_year = list(data['join_year'])
                    fee_waiver = list(data['fee_waiver'])
                    gender = list(data['gender'])

                    if 'seater_type' in data:
                        if data['seater_type'] == '':
                            seater_type = None
                        else:
                            seater_type = data['seater_type']
                    else:
                        seater_type = None
                    fee_component_cat = list(data['fee_component_cat'])
                    for cid in c_id:
                        for jy in join_year:
                            for a in admission_status:
                                for ca in caste:
                                    for c in fee_component_cat:
                                        for g in gender:
                                            for fw in fee_waiver:

                                                qry_check = StuAccFeeSettings.objects.filter(course_id=StudentDropdown.objects.get(sno=cid['sno']), join_year=jy, admission_status=StudentDropdown.objects.get(sno=a), session=Semtiming.objects.get(uid=session), fee_component_cat=StudentAccountsDropdown.objects.get(sno=c['sno']), fee_component=StudentAccountsDropdown.objects.get(sno=fee_component), fee_waiver=fw, caste=StudentDropdown.objects.get(sno=ca), gender=StudentDropdown.objects.get(sno=g), seater_type=seater_type).exclude(status="DELETE").values('id')
                                                if len(qry_check) > 0:
                                                    msg = "Fee Component Successfully Updated"
                                                    qry_up = StuAccFeeSettings.objects.filter(id=qry_check[0]['id']).update(status="DELETE")

                                                if seater_type is None:
                                                    qry_ins = StuAccFeeSettings.objects.create(course_id=StudentDropdown.objects.get(sno=cid['sno']), join_year=jy, admission_status=StudentDropdown.objects.get(sno=a), session=Semtiming.objects.get(uid=session), fee_component_cat=StudentAccountsDropdown.objects.get(sno=c['sno']), fee_component=StudentAccountsDropdown.objects.get(sno=fee_component), gender=StudentDropdown.objects.get(sno=g), fee_waiver=fw, value=c['value'], added_by=emp_id, caste=StudentDropdown.objects.get(sno=ca))
                                                else:
                                                    qry_ins = StuAccFeeSettings.objects.create(course_id=StudentDropdown.objects.get(sno=cid['sno']), join_year=jy, admission_status=StudentDropdown.objects.get(sno=a), session=Semtiming.objects.get(uid=session), fee_component_cat=StudentAccountsDropdown.objects.get(sno=c['sno']), fee_component=StudentAccountsDropdown.objects.get(sno=fee_component), gender=StudentDropdown.objects.get(sno=g), fee_waiver=fw, value=c['value'], added_by=emp_id, caste=StudentDropdown.objects.get(sno=ca), seater_type=HostelDropdown.objects.get(sno=seater_type))

                    data_values = {'msg': msg}
                    status = 200
                elif request.method == 'PUT':
                    data = json.loads(request.body)
                    id = data['id']
                    emp_id = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                    value = data['value']

                    q_get_det = StuAccFeeSettings.objects.filter(id=id).values('course_id', 'join_year', 'admission_status', 'session', 'fee_component', 'fee_component_cat', 'gender', 'fee_waiver', 'value', 'caste', 'seater_type')
                    q_update = StuAccFeeSettings.objects.filter(id=id).update(status="DELETE")

                    if q_get_det[0]['seater_type'] is None:
                        qry_ins = StuAccFeeSettings.objects.create(course_id=StudentDropdown.objects.get(sno=q_get_det[0]['course_id']), join_year=q_get_det[0]['join_year'], admission_status=StudentDropdown.objects.get(sno=q_get_det[0]['admission_status']), session=Semtiming.objects.get(uid=q_get_det[0]['session']), fee_component_cat=StudentAccountsDropdown.objects.get(sno=q_get_det[0]['fee_component_cat']), fee_component=StudentAccountsDropdown.objects.get(sno=q_get_det[0]['fee_component']), gender=StudentDropdown.objects.get(sno=q_get_det[0]['gender']), fee_waiver=q_get_det[0]['fee_waiver'], value=value, added_by=emp_id, caste=StudentDropdown.objects.get(sno=q_get_det[0]['caste']))
                    else:
                        qry_ins = StuAccFeeSettings.objects.create(course_id=StudentDropdown.objects.get(sno=q_get_det[0]['course_id']), join_year=q_get_det[0]['join_year'], admission_status=StudentDropdown.objects.get(sno=q_get_det[0]['admission_status']), session=Semtiming.objects.get(uid=q_get_det[0]['session']), fee_component_cat=StudentAccountsDropdown.objects.get(sno=q_get_det[0]['fee_component_cat']), fee_component=StudentAccountsDropdown.objects.get(sno=q_get_det[0]['fee_component']), gender=StudentDropdown.objects.get(sno=q_get_det[0]['gender']), fee_waiver=q_get_det[0]['fee_waiver'], value=value, added_by=emp_id, caste=StudentDropdown.objects.get(sno=q_get_det[0]['caste']), seater_type=HostelDropdown.objects.get(sno=q_get_det[0]['seater_type']))

                    msg = "Fee component Successfully Updated"
                    status = 200
                    data_values = {'msg': msg}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)

# def fee_initial_settings(request):
#   data_values={}
#   if 'HTTP_COOKIE' in request.META:
#       if request.user.is_authenticated:
#           check=checkpermission(request,[1353])
#           if check==200:
#               if request.method == 'GET':
#                   if request.GET['request_type'] == 'form_data':
#                       fee_initial=get_fee_initial()
#                       fee_component=get_fee_component()

#                       msg="Success"
#                       status=200
#                       data_values={'msg':msg,'data':{'fee_component':fee_component,'fee_initial':fee_initial}}
#                   elif request.GET['request_type'] == 'view_previous':
#                       qry = FeeInitialSettings.objects.extra(select={'time_stamp':"DATE_FORMAT(time_stamp,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('fee_initial__value','fee_initial','fee_component','fee_component__value','time_stamp')
#                       status=200
#                       data_values={'data':list(qry)}
#               elif request.method == 'POST':
#                   data=json.loads(request.body)

#                   msg="Fee Initial Successfully Inserted"
#                   emp_id = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
#                   fee_initial=data['fee_initial']
#                   fee_component=list(data['fee_component'])

#                   for fc in fee_component:
#                       qry_check = FeeInitialSettings.objects.filter(fee_initial=StudentAccountsDropdown.objects.get(sno=fee_initial),fee_component=StudentAccountsDropdown.objects.get(sno=fc)).exclude(status="DELETE").values('id')
#                       if len(qry_check)>0:
#                           msg="Fee Initial Successfully Updated"
#                           qry_up = FeeInitialSettings.objects.filter(id=qry_check[0]['id']).update(status="DELETE")

#                       qry_ins = FeeInitialSettings.objects.create(fee_initial=StudentAccountsDropdown.objects.get(sno=fee_initial),fee_component=StudentAccountsDropdown.objects.get(sno=fc),added_by=emp_id)

#                   data_values={'msg':msg}
#                   status=200
#               else:
#                   status=502
#           else:
#               status=403
#       else:
#           status=401
#   else:
#       status=500
#   return JsonResponse(data=data_values,status=status)


def penalty_settings(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'form_data':
                        penalty = getPenalty()

                        msg = "Success"
                        status = 200
                        data_values = {'msg': msg, 'data': {'penalty': penalty}}
                    elif request.GET['request_type'] == 'view_previous':
                        qry = PenaltySettings.objects.extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('penalty__value', 'penalty', 'value', 'time_stamp')

                        status = 200
                        data_values = {'data': list(qry)}
                elif request.method == 'POST':
                    data = json.loads(request.body)

                    msg = "Penalty Successfully Inserted"
                    emp_id = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                    penalty = data['penalty']
                    value = data['value']

                    qry_check = PenaltySettings.objects.filter(penalty=StudentAccountsDropdown.objects.get(sno=penalty)).exclude(status="DELETE").values('id')
                    if len(qry_check) > 0:
                        msg = "Penalty Component Successfully Updated"
                        qry_up = PenaltySettings.objects.filter(id=qry_check[0]['id']).update(status="DELETE")

                    qry_ins = PenaltySettings.objects.create(penalty=StudentAccountsDropdown.objects.get(sno=penalty), value=value, added_by=emp_id)

                    data_values = {'msg': msg}
                    status = 200

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def fee_receipt_details(filter_data):
    qry_fee_details = SubmitFee.objects.filter(**filter_data).exclude(status="DELETE").values('fee_rec_no', 'uniq_id__name', 'cancelled_status', 'actual_fee', 'paid_fee', 'refund_value', 'due_value', 'session__session', 'receipt_type', 'id', 'uniq_id', 'due_date', 'seater_type', 'seater_type__value').order_by('id')
    data = []
    for q in qry_fee_details:
        if q['receipt_type'] == 'N':
            q['receipt_type'] = 'NORMAL'
        elif q['receipt_type'] == 'D':
            q['receipt_type'] = 'DUE'
        mop = {}

        q_mop_details = ModeOfPaymentDetails.objects.filter(fee_id=q['id']).values('MOPcomponent__value', 'MOPcomponent', 'value', 'MOPcomponent__pid')
        i = 0
        pid_li = []
        for qm in q_mop_details:
            pid_li.append(qm['MOPcomponent__pid'])

            q_id = StudentAccountsDropdown.objects.filter(sno=qm['MOPcomponent']).values('pid', 'value')
            q_val = StudentAccountsDropdown.objects.filter(sno=q_id[0]['pid']).values('value')

            if 'AMOUNT' in q_id[0]['value']:
                qm['value'] = float(qm['value'])

            if 'DROPDOWN' in q_id[0]['value']:
                qm['value'] = int(qm['value'])

            if q_val[0]['value'] not in mop:
                i = 0
                mop[q_val[0]['value']] = []
                mop[q_val[0]['value']].append({qm['MOPcomponent']: qm['value']})
            else:
                if qm['MOPcomponent'] in mop[q_val[0]['value']][i]:
                    i += 1
                    mop[q_val[0]['value']].append({qm['MOPcomponent']: qm['value']})
                else:

                    mop[q_val[0]['value']][i][qm['MOPcomponent']] = qm['value']

        fee_comp_details = SubmitFeeComponentDetails.objects.filter(fee_id=q['id']).values('fee_component__value', 'fee_sub_component__value', 'sub_component_value', 'fee_component', 'fee_sub_component')

        q_other_mode_of_payment = StudentAccountsDropdown.objects.filter(field='MODE OF PAYMENT').exclude(sno__in=pid_li).exclude(value__isnull=True).values('value')
        for other_mode in q_other_mode_of_payment:
            mop[other_mode['value']] = []

        print(mop)
        data.append({'fee_details': q, 'mode_of_payment_details': list(q_mop_details), 'fee_component_details': list(fee_comp_details), 'frontend_mop': mop})

    return data


def get_stu_fee_receipts(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                if request.method == 'GET':
                    fee_initial = request.GET['fee_initial']
                    uniq_id = request.GET['uniq_id']
                    filter_data = {}
                    filter_data['session'] = Semtiming.objects.get(uid=session_id)
                    filter_data['fee_rec_no__contains'] = fee_initial
                    filter_data['uniq_id'] = StudentPrimDetail.objects.get(uniq_id=uniq_id)

                    if request.GET['request_type'] == "due":
                        filter_data['due_value__gt'] = 0

                    if request.GET['request_type'] == 'fee_receipt_details':
                        filter_data['fee_rec_no'] = request.GET['fee_receipt']
                    data_values['data'] = fee_receipt_details(filter_data)

                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


# def due_paid_report(request):
#   data_values = {}
#   status = 403
#   if 'HTTP_COOKIE' in request.META:
#       if request.user.is_authenticated:
#           check = checkpermission(request, [1353])
#           if check == 200:
#               session_name = request.session['Session_name']
#               session_id = request.session['Session_id']
#               if request.method == 'POST':
#                   student_session = generate_session_table_name("studentSession_", session_name)

#                   data = json.loads(request.body)
#                   if data['request_type'] != 'ALL':
#                       filter_data = {}
#                       if data['request_type'] == 'due':
#                           filter_data['due_value__gt'] = 0
#                           filter_data['cancelled_status__in'] = ['N']
#                       elif data['request_type'] == 'paid':
#                           filter_data['cancelled_status__in'] = data['receipt_status']

#                       course = data['course']
#                       branch = data['branch']
#                       year = data['year']
#                       gender = data['gender']
#                       fee_initial = data['fee_initial']
#                       # receipt_status=data['receipt_status']

#                       if course == 'ALL':
#                           course = qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno', flat=True)

#                       if branch[0] == 'ALL':
#                           branch = CourseDetail.objects.values_list('uid', flat=True)

#                       if year[0] == 'ALL':
#                           qry = CourseDetail.objects.all().aggregate(Max('course_duration'))
#                           year_li = list(range(1, qry['course_duration__max'] + 1))

#                       # branch=[1]
#                       # year=[1]
#                       # gender=[58]
#                       # fee_initial=[5]
#                       # receipt_status=['N']
#                       data2 = []

#                       qry_stu_uniq = student_session.objects.filter(year__in=year, uniq_id__dept_detail__in=branch, uniq_id__gender__in=gender).values_list('uniq_id', flat=True)

#                       status = 200
#                       i = 0
#                       for fi in fee_initial:
#                           q_fiv = StudentAccountsDropdown.objects.filter(sno=fi).values('value')
#                           fiv = q_fiv[0]['value']

#                           if data['request_type'] == 'due':
#                               qu = SubmitFee.objects.filter(fee_rec_no__contains=fiv, uniq_id__in=qry_stu_uniq, session=session_id).filter(cancelled_status='N').exclude(status="DELETE").exclude(fee_rec_no__in=SubmitFee.objects.filter(cancelled_status='N').exclude(status='DELETE').exclude(prev_fee_rec_no='').exclude(prev_fee_rec_no__isnull=True).values_list('prev_fee_rec_no', flat=True)).values('uniq_id', 'id')

#                               id_li = [q['id'] for q in qu]
#                               qry_due_details = SubmitFee.objects.filter(id__in=id_li, due_value__gt=0).values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'uniq_id__admission_status__value', 'actual_fee', 'paid_fee', 'time_stamp', 'uniq_id__admission_through__value')
#                           else:
#                               qry_due_details = SubmitFee.objects.filter(fee_rec_no__contains=fiv, uniq_id__in=qry_stu_uniq, session=session_id).filter(**filter_data).exclude(status="DELETE").values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'uniq_id__admission_status__value', 'actual_fee', 'paid_fee', 'time_stamp', 'uniq_id__admission_through__value')

#                           for qd in qry_due_details:
#                               q_date = SubmitFee.objects.filter(fee_rec_no=qd['fee_rec_no']).extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('time_stamp').order_by('id')[:1]
#                               qd['date_re'] = q_date[0]['time_stamp']

#                               data2.append(qd)
#                               q_details2 = student_session.objects.filter(uniq_id=qd['uniq_id']).values('mob', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'year', 'sem__dept', 'uniq_id__gender', 'sem__dept__course')
#                               for k, v in q_details2[0].items():
#                                   if k == 'uniq_id__dept_detail__dept__value':
#                                       data2[i]['sem__dept__dept__value'] = v
#                                   else:
#                                       data2[i][k] = v
#                               q_det3 = StudentPerDetail.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=qd['uniq_id'])).values('fname')
#                               if len(q_det3) > 0:
#                                   data2[i]['fname'] = q_det3[0]['fname']
#                               else:
#                                   data2[i]['fname'] = "----"
#                               i += 1
#                       data_values = {'data': data2}
#                   else:
#                       fee_rec_no = data['reciept'].upper()
#                       qry_due_details = SubmitFee.objects.filter(fee_rec_no__contains=fee_rec_no, session=session_id).exclude(status="DELETE").values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'uniq_id__admission_status__value', 'actual_fee', 'paid_fee', 'time_stamp', 'uniq_id__admission_through__value')

#                       data2 = []
#                       i = 0
#                       for qd in qry_due_details:
#                           q_date = SubmitFee.objects.filter(fee_rec_no=qd['fee_rec_no']).extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('time_stamp').order_by('id')[:1]
#                           qd['date_re'] = q_date[0]['time_stamp']

#                           # qd['date_re']=datetime.strptime(str(qd['time_stamp']).split(' ')[0],"%Y-%m-%d").strftime("%d-%m-%Y")
#                           data2.append(qd)
#                           q_details2 = student_session.objects.filter(uniq_id=qd['uniq_id']).values('mob', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'year', 'sem__dept', 'uniq_id__gender', 'sem__dept__course')
#                           for k, v in q_details2[0].items():
#                               if k == 'uniq_id__dept_detail__dept__value':
#                                   data2[i]['sem__dept__dept__value'] = v
#                               else:
#                                   data2[i][k] = v
#                           q_det3 = StudentPerDetail.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=qd['uniq_id'])).values('fname')
#                           if len(q_det3) > 0:
#                               data2[i]['fname'] = q_det3[0]['fname']
#                           else:
#                               data2[i]['fname'] = "----"
#                           i += 1
#                       status = 200
#                       data_values = {'data': data2}

#               elif request.method == "PUT":
#                   data = json.loads(request.body)
#                   fee_id = data['fee_id']
#                   due_date = datetime.strptime(str(data['due_date']).split('T')[0], "%Y-%m-%d").date()
#                   added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])

#                   q_old_d = SubmitFee.objects.filter(id=fee_id).values('due_date')
#                   q_log = DueDateLog.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), due_date=q_old_d[0]['due_date'], added_by=added_by)
#                   status = 200
#                   q_update = SubmitFee.objects.filter(id=fee_id).update(due_date=due_date)
#               else:
#                   status = 502
#           else:
#               status = 403
#       else:
#           status = 401
#   else:
#       status = 500
#   return JsonResponse(data=data_values, status=status)
def due_paid_report(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                if request.method == 'POST':
                    student_session = generate_session_table_name("studentSession_", session_name)
                    HostelStudentAppliction = generate_session_table_name("HostelStudentAppliction_", session_name)
                    

                    data = json.loads(request.body)
                    if data['request_type'] != 'ALL':
                        filter_data = {}
                        if data['request_type'] == 'due':
                            filter_data['due_value__gt'] = 0
                            filter_data['cancelled_status__in'] = ['N']
                        elif data['request_type'] == 'paid':
                            filter_data['cancelled_status__in'] = data['receipt_status']

                        course = data['course']
                        branch = data['branch']
                        year = data['year']
                        gender = data['gender']
                        fee_initial = data['fee_initial']
                        # receipt_status=data['receipt_status']

                        if course == 'ALL':
                            course = qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno', flat=True)

                        if branch[0] == 'ALL':
                            branch = CourseDetail.objects.values_list('uid', flat=True)

                        if year[0] == 'ALL':
                            qry = CourseDetail.objects.all().aggregate(Max('course_duration'))
                            year_li = list(range(1, qry['course_duration__max'] + 1))

                        # branch=[1]
                        # year=[1]
                        # gender=[58]
                        # fee_initial=[5]
                        # receipt_status=['N']
                        data2 = []

                        qry_stu_uniq = student_session.objects.filter(year__in=year, uniq_id__dept_detail__in=branch, uniq_id__gender__in=gender).values_list('uniq_id', flat=True)

                        status = 200
                        i = 0
                        for fi in fee_initial:
                            q_fiv = StudentAccountsDropdown.objects.filter(sno=fi).values('value')
                            fiv = q_fiv[0]['value']

                            if data['request_type'] == 'due':
                                ### WITHDRAWAL CHECK FOR HOSTEL ###
                                withdrawal_stu = []
                                if 'H' in fiv:
                                    withdrawal_stu = HostelStudentAppliction.objects.filter(current_status="WITHDRAWAL").exclude(status="DELETE").values_list('uniq_id', flat=True)
                                elif 'A' in fiv:
                                    withdrawal_stu = student_session.objects.filter(uniq_id__in=qry_stu_uniq,uniq_id__admission_status__value="WITHDRAWAL").values_list('uniq_id', flat=True)
                                qu = SubmitFee.objects.filter(fee_rec_no__contains=fiv, uniq_id__in=qry_stu_uniq, session=session_id).filter(cancelled_status='N').exclude(uniq_id__in=withdrawal_stu).exclude(status="DELETE").exclude(fee_rec_no__in=SubmitFee.objects.filter(cancelled_status='N').exclude(status='DELETE').exclude(prev_fee_rec_no='').exclude(prev_fee_rec_no__isnull=True).values_list('prev_fee_rec_no', flat=True)).values('uniq_id', 'id')

                                # qu = SubmitFee.objects.filter(fee_rec_no__contains=fiv, uniq_id__in=qry_stu_uniq, session=session_id).filter(cancelled_status='N').exclude(status="DELETE").exclude(fee_rec_no__in=SubmitFee.objects.filter(cancelled_status='N').exclude(status='DELETE').exclude(prev_fee_rec_no='').exclude(prev_fee_rec_no__isnull=True).values_list('prev_fee_rec_no', flat=True)).values('uniq_id', 'id')
                                ###################################

                                id_li = [q['id'] for q in qu]
                                qry_due_details = SubmitFee.objects.filter(id__in=id_li, due_value__gt=0).values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'uniq_id__admission_status__value', 'actual_fee', 'paid_fee', 'time_stamp', 'uniq_id__admission_through__value')
                            else:
                                qry_due_details = SubmitFee.objects.filter(fee_rec_no__contains=fiv, uniq_id__in=qry_stu_uniq, session=session_id).filter(**filter_data).exclude(status="DELETE").values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'uniq_id__admission_status__value', 'actual_fee', 'paid_fee', 'time_stamp', 'uniq_id__admission_through__value')

                            for qd in qry_due_details:
                                q_date = SubmitFee.objects.filter(fee_rec_no=qd['fee_rec_no']).extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('time_stamp').order_by('id')[:1]
                                qd['date_re'] = q_date[0]['time_stamp']

                                data2.append(qd)
                                q_details2 = student_session.objects.filter(uniq_id=qd['uniq_id']).values('uniq_id__lib','mob', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'year', 'sem__dept', 'uniq_id__gender', 'sem__dept__course')


                                for k, v in q_details2[0].items():
                                    if k == 'uniq_id__dept_detail__dept__value':
                                        data2[i]['sem__dept__dept__value'] = v
                                    else:
                                        data2[i][k] = v
                                q_det3 = StudentPerDetail.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=qd['uniq_id'])).values('fname')
                                if len(q_det3) > 0:
                                    data2[i]['fname'] = q_det3[0]['fname']
                                else:
                                    data2[i]['fname'] = "----"

                                q_Fmob=StudentFamilyDetails.objects.filter(uniq_id=qd['uniq_id']).values('father_mob','father_email')
                                if len(q_Fmob)>0:
                                    data2[i]['father_mob'] = q_Fmob[0]['father_mob']
                                    data2[i]['father_email'] = q_Fmob[0]['father_email']
                                else:
                                    data2[i]['father_mob'] = "----"
                                i += 1
                        data_values = {'data': data2}
                    else:
                        fee_rec_no = data['reciept'].upper()
                        qry_due_details = SubmitFee.objects.filter(fee_rec_no__contains=fee_rec_no, session=session_id).exclude(status="DELETE").values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'uniq_id__admission_status__value', 'actual_fee', 'paid_fee', 'time_stamp', 'uniq_id__admission_through__value')

                        data2 = []
                        i = 0
                        for qd in qry_due_details:
                            q_date = SubmitFee.objects.filter(fee_rec_no=qd['fee_rec_no']).extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('time_stamp').order_by('id')[:1]
                            qd['date_re'] = q_date[0]['time_stamp']

                            # qd['date_re']=datetime.strptime(str(qd['time_stamp']).split(' ')[0],"%Y-%m-%d").strftime("%d-%m-%Y")
                            data2.append(qd)
                            q_details2 = student_session.objects.filter(uniq_id=qd['uniq_id']).values('uniq_id__lib','mob', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'year', 'sem__dept', 'uniq_id__gender', 'sem__dept__course')
                            for k, v in q_details2[0].items():
                                if k == 'uniq_id__dept_detail__dept__value':
                                    data2[i]['sem__dept__dept__value'] = v
                                else:
                                    data2[i][k] = v
                            q_det3 = StudentPerDetail.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=qd['uniq_id'])).values('fname')
                            if len(q_det3) > 0:
                                data2[i]['fname'] = q_det3[0]['fname']
                            else:
                                data2[i]['fname'] = "----"

                            q_Fmob=StudentFamilyDetails.objects.filter(uniq_id=qd['uniq_id']).values('father_mob','father_email')
                            if len(q_Fmob)>0:
                                data2[i]['father_mob'] = q_Fmob[0]['father_mob']
                                data2[i]['father_email'] = q_Fmob[0]['father_email']
                            else:
                                data2[i]['father_mob'] = "----"
                            i += 1
                        status = 200
                        data_values = {'data': data2}

                elif request.method == "PUT":
                    data = json.loads(request.body)
                    fee_id = data['fee_id']
                    due_date = datetime.strptime(str(data['due_date']).split('T')[0], "%Y-%m-%d").date()
                    added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])

                    q_old_d = SubmitFee.objects.filter(id=fee_id).values('due_date')
                    q_log = DueDateLog.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), due_date=q_old_d[0]['due_date'], added_by=added_by)
                    status = 200
                    q_update = SubmitFee.objects.filter(id=fee_id).update(due_date=due_date)
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def check_update_due_receipts(fee_rec_no, actual_fee, added_by):
    q_check_due_rec = SubmitFee.objects.filter(prev_fee_rec_no=fee_rec_no).exclude(status='DELETE').values('refund_value', 'due_value', 'actual_fee', 'paid_fee', 'id', 'uniq_id', 'session', 'fee_rec_no', 'prev_fee_rec_no', 'cancelled_status', 'receipt_type', 'due_date', 'seater_type')
    if len(q_check_due_rec) > 0:
        q_del = SubmitFee.objects.filter(id=q_check_due_rec[0]['id']).update(status='DELETE')

        ref_val = None
        du_val = None

        if actual_fee is None:
            actual_fee = 0
        if q_check_due_rec[0]['paid_fee'] is None:
            q_check_due_rec[0]['paid_fee'] = 0

        if q_check_due_rec[0]['paid_fee'] > actual_fee:
            ref_val = q_check_due_rec[0]['paid_fee'] - actual_fee
        elif actual_fee > q_check_due_rec[0]['paid_fee']:
            du_val = actual_fee - q_check_due_rec[0]['paid_fee']

        if q_check_due_rec[0]['seater_type'] is not None:
            q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=q_check_due_rec[0]['session']), uniq_id=StudentPrimDetail.objects.get(uniq_id=q_check_due_rec[0]['uniq_id']), receipt_type=q_check_due_rec[0]['receipt_type'], added_by=added_by, actual_fee=actual_fee, seater_type=HostelDropdown.objects.get(sno=q_check_due_rec[0]['seater_type']), prev_fee_rec_no=q_check_due_rec[0]['prev_fee_rec_no'], fee_rec_no=q_check_due_rec[0]['fee_rec_no'], due_date=q_check_due_rec[0]['due_date'], paid_fee=q_check_due_rec[0]['paid_fee'], refund_value=ref_val, due_value=du_val)
        else:
            q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=q_check_due_rec[0]['session']), uniq_id=StudentPrimDetail.objects.get(uniq_id=q_check_due_rec[0]['uniq_id']), receipt_type=q_check_due_rec[0]['receipt_type'], added_by=added_by, actual_fee=actual_fee, prev_fee_rec_no=q_check_due_rec[0]['prev_fee_rec_no'], fee_rec_no=q_check_due_rec[0]['fee_rec_no'], due_date=q_check_due_rec[0]['due_date'], paid_fee=q_check_due_rec[0]['paid_fee'], refund_value=ref_val, due_value=du_val)
            print(q_ins)
            mod_data = list(ModeOfPaymentDetails.objects.filter(fee_id=q_check_due_rec[0]['id']).values('id','value','MOPcomponent','fee_id'))
            qr_object = (ModeOfPaymentDetails(fee_id=SubmitFee.objects.get(id=q_ins.id),MOPcomponent=StudentAccountsDropdown.objects.get(sno=k['MOPcomponent']),value=k['value'])for k in mod_data)
            qr_create = ModeOfPaymentDetails.objects.bulk_create(qr_object)
            print(mod_data)

        q_check = SubmitFee.objects.filter(prev_fee_rec_no=q_check_due_rec[0]['fee_rec_no']).exclude(status='DELETE').count()
        if q_check > 0:
            check_update_due_receipts(q_check_due_rec[0]['fee_rec_no'], du_val, added_by)

# def hostel_refund_paid_fee(uniq_id,session,seater_type,emp_id,hostel_id,session_name,operation,type_of_refund):
#   normal_fee_reciept = list(SubmitFee.objects.filter(session=session, uniq_id=uniq_id, fee_rec_no__contains="H", receipt_type="N").values().order_by('-id'))
#   due_fee_reciept = list(SubmitFee.objects.filter(session=session, uniq_id=uniq_id, fee_rec_no__contains="H", receipt_type="D").values().order_by('-id'))
#   if operation=="REFUND" and len(normal_fee_reciept)>0:
#       fee_id=""
#       remark="DUE TO HOSTEL CHANGE"
#       if len(due_fee_reciept)>0:
#           amount=normal_fee_reciept[0]['actual_fee'] - due_fee_reciept[0]['due_value']
#           fee_id = due_fee_reciept[0]['id']
#       else:
#           amount=normal_fee_reciept[0]['actual_fee']
#           fee_id = normal_fee_reciept[0]['id']
#       refund_type=type_of_refund

#       SubmitFee.objects.filter(id=fee_id).update(cancelled_status = "Y")
#       print(uniq_id,session,seater_type,emp_id,hostel_id,session_name,operation,type_of_refund)
#       q_ins = RefundFee.objects.create(fee_id=SubmitFee.objects.get(id=fee_id),remark=remark,amount=amount,refund_type=refund_type,added_by=EmployeePrimdetail.objects.get(emp_id = emp_id))
#       ref_id=q_ins.id

#       q_bank = StudentBankDetails.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('id')
#       if len(q_bank)>0:
#           q_upd = RefundFee.objects.filter(id=ref_id).update(bank_details_id=StudentBankDetails.objects.get(id=q_bank[0]['id']))

#   elif operation=="UPDATE" and len(normal_fee_reciept)>0:
#       if len(due_fee_reciept)>0:
#           f_id = due_fee_reciept[0]['id']
#       else:
#           f_id = normal_fee_reciept[0]['id']

#       q_fee = SubmitFee.objects.filter(id = f_id).values('fee_rec_no','uniq_id','receipt_type','prev_fee_rec_no')
#       data = SubmitFeeComponentDetails.objects.filter(fee_id = f_id).values('fee_component','fee_component__value','fee_sub_component','fee_sub_component__value','sub_component_value')

#       rec_type = q_fee[0]['receipt_type']
#       prev_fee_rec_no=q_fee[0]['prev_fee_rec_no']
#       fee_rec_no = q_fee[0]['fee_rec_no']

#       q_upd = SubmitFee.objects.filter(id=f_id).update(status="DELETE")
#       fee_initial=fee_rec_no[0]

#       print(data)

#       # if 'transportation_sub' in data:
#       #   transportation_sub=data['transportation_sub']
#       # else:
#       #   transportation_sub=None


def submit_fee(request):
    print(request)
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session = request.session['Session_id']
                session_name = request.session['Session_name']
                added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                operation = None
                if request.method == 'GET':
                    if not 'request_type' in request.GET:
                        operation = "fetch"
                        uniq_id = request.GET['uniq_id']
                        mode_of_payment = get_mode_of_payment()
                        fee_component = get_fee_component_filtered(uniq_id, session)
                        print(fee_component,'fee_component')
                        fee_initial = get_fee_initial()

                        stu_details = {}
                        student_session = generate_session_table_name("studentSession_", session_name)
                        qry_stu_details = student_session.objects.filter(uniq_id=uniq_id).values('year', 'sem__dept', 'uniq_id__fee_waiver', 'uniq_id__caste', 'uniq_id__admission_status', 'uniq_id__join_year', 'sem__dept__course_id', 'uniq_id__gender', 'uniq_id__admission_type__value', 'uniq_id__admission_through__value', 'uniq_id__name')
                        qry_stu_details[0]['uniq_id__fee_waiver'] = str(qry_stu_details[0]['uniq_id__fee_waiver'])
                        if str(qry_stu_details[0]['uniq_id__fee_waiver']) == '0':
                            qry_stu_details[0]['uniq_id__fee_waiver'] = 'N'
                        else:
                            qry_stu_details[0]['uniq_id__fee_waiver'] = 'Y'

                        if qry_stu_details[0]['uniq_id__admission_status'] is None or qry_stu_details[0]['uniq_id__caste'] is None or qry_stu_details[0]['uniq_id__gender'] is None:
                            msg = "Please contact registrar office for updation of details"
                            status = 202
                            data_values = {'msg': msg}
                        else:
                            n = len(fee_component)
                            total_amt = 0
                            flag_upsee = 0
                            upsee_amt = 0
                            for i in range(n):
                                fee_component[i]['already_paid'] = False
                                # q_check_paid = SubmitFeeComponentDetails.objects.filter(fee_component=fee_component[i]['id'],fee_id__cancelled_status='N',fee_id__session=session,fee_id__uniq_id=uniq_id).exclude(fee_id__fee_rec_no__isnull=True).exclude(fee_id__status="DELETE").values('fee_id')
                                # if len(q_check_paid)==0:
                                total_amt = 0
                                if 'TRANSPORTATION' in fee_component[i]['component_name'] or 'HOSTEL' in fee_component[i]['component_name']:
                                    fee_component[i]['data'] = []
                                else:
                                    n2 = len(fee_component[i]['data'])
                                    for j in range(n2):
                                        qry_details = StuAccFeeSettings.objects.filter(join_year=qry_stu_details[0]['uniq_id__join_year'], caste=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__caste']), admission_status=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__admission_status']), fee_waiver=qry_stu_details[0]['uniq_id__fee_waiver'], fee_component=StudentAccountsDropdown.objects.get(sno=fee_component[i]['id']), fee_component_cat=StudentAccountsDropdown.objects.get(sno=fee_component[i]['data'][j]['sno']), course_id=StudentDropdown.objects.get(sno=qry_stu_details[0]['sem__dept__course_id']), gender=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__gender']), session=Semtiming.objects.get(uid=session)).exclude(status="DELETE").values('value')
                                        if len(qry_details) > 0:
                                            if 'UPSEE' in fee_component[i]['data'][j]['value']:
                                                # if ((qry_stu_details[0]['year'] == 2 and 'LATERAL' in qry_stu_details[0]['uniq_id__admission_type__value']) or (qry_stu_details[0]['year'] == 1)) and (qry_stu_details[0]['uniq_id__admission_through__value'] in ['COUNSELLING', 'EWS']) and (qry_stu_details[0]['uniq_id__join_year'] == date.today().year):
                                                # changed on 18 jan and to be reverted after session 2021o
                                                if ((qry_stu_details[0]['year'] == 2 and 'LATERAL' in qry_stu_details[0]['uniq_id__admission_type__value']) or (qry_stu_details[0]['year'] == 1)) and (qry_stu_details[0]['uniq_id__admission_through__value'] in ['COUNSELLING', 'EWS']):
                                                    flag_upsee = 1
                                                    fee_component[i]['data'][j]['value'] = qry_details[0]['value']
                                                    total_amt += qry_details[0]['value']
                                                    upsee_amt = qry_details[0]['value']
                                                else:
                                                    fee_component[i]['data'][j]['value'] = qry_details[0]['value']
                                                    total_amt += qry_details[0]['value']

                                            elif 'ONE TIME' in fee_component[i]['data'][j]['value']:
                                                ####################
                                                # change on 6 jan 2021
                                                ####################
                                                # if ((qry_stu_details[0]['year'] == 2 and 'LATERAL' in qry_stu_details[0]['uniq_id__admission_type__value']) or (qry_stu_details[0]['year'] == 1)) and (qry_stu_details[0]['uniq_id__join_year'] == date.today().year):
                                                if ((qry_stu_details[0]['year'] == 2 and 'LATERAL' in qry_stu_details[0]['uniq_id__admission_type__value']) or (qry_stu_details[0]['year'] == 1)):
                                                    fee_component[i]['data'][j]['value'] = qry_details[0]['value']
                                                    total_amt += qry_details[0]['value']
                                                else:
                                                    fee_component[i]['data'][j]['value'] = 0
                                            else:
                                                fee_component[i]['data'][j]['value'] = qry_details[0]['value']
                                                total_amt += qry_details[0]['value']

                                        else:
                                            fee_component[i]['data'][j]['value'] = 0

                                q_check_paid = SubmitFeeComponentDetails.objects.filter(fee_component=fee_component[i]['id'], fee_id__cancelled_status='N', fee_id__session=session, fee_id__uniq_id=uniq_id, fee_id__receipt_type='N').exclude(fee_id__fee_rec_no__isnull=True).exclude(fee_id__status="DELETE").values('fee_id__fee_rec_no')
                                fee_component[i]['already_paid'] = ""
                                if len(q_check_paid) > 0:
                                    total_amt = 0
                                    fee_component[i]['already_paid'] = True
                                    fee_component[i]['already_paid'] = q_check_paid[0]['fee_id__fee_rec_no']
                                fee_component[i]['total_amt'] = total_amt
                                # else:
                                #   fee_component[i]['already_paid']=True
                                #   n2=len(fee_component[i]['data'])
                                #   for j in range(n2):
                                #       fee_component[i]['data'][j]['value'] = 0

                            if flag_upsee == 1:
                                # while upsee_amt>0 and not fee_component[0]['already_paid']:
                                    # if fee_component[0]['data'][i]['value']>0:
                                    #   if fee_component[0]['data'][i]['value']>upsee_amt:
                                    #       fee_component[0]['data'][i]['value']=fee_component[0]['data'][i]['value']-upsee_amt
                                    #       upsee_amt=0

                                    #   else:
                                    #       diff=upsee_amt-fee_component[0]['data'][i]['value']
                                    #       upsee_amt=diff
                                    #       fee_component[0]['data'][i]['value']=0
                                    #       #fee_component[0]['data'][i]['value']-=diff
                                    #       i+=1
                                    # else:
                                    #   i+=1
                                if upsee_amt > 0 and not fee_component[0]['already_paid']:
                                    fee_component[0]['total_amt'] = fee_component[0]['total_amt'] - upsee_amt

                            msg = "Success"
                            status = 200
                            data_values = {'msg': msg, 'data': {'mode_of_payment': mode_of_payment, 'fee_component': fee_component, 'fee_initial': fee_initial}}

                    elif request.GET['request_type'] == 'hostel_seater':
                        try:
                            req_tp = request.GET['operation']
                        except:
                            req_tp = "----"
                        operation = "fetch"
                        uniq_id = request.GET['uniq_id']

                        ##################### SEATER CHANGE ################
                        # hostel_seater = get_student_eligible_seater(uniq_id, session)

                        ##################### SEATER CHANGE ################
                        hostel_seater = get_student_eligible_seater_acc(uniq_id, session_name, {}, session)
                        seater_type = []
                        if len(hostel_seater) > 0:
                            seater_type = hostel_seater
                        else:
                            seater_type = get_seater(session)
                        ####### END ######### SEATER CHANGE ################

                        fee_component = []
                        qry = StudentAccountsDropdown.objects.filter(field="FEE COMPONENTS", value__contains="HOSTEL").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
                        for q in qry:
                            qr = StudentAccountsDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
                            fee_component.append({'id': q['sno'], 'component_name': q['value'], 'data': list(qr)})
                        print(fee_component,'ggggggggg')

                        student_session = generate_session_table_name("studentSession_", session_name)
                        qry_stu_details = student_session.objects.filter(uniq_id=uniq_id).values('uniq_id', 'year', 'sem__dept', 'uniq_id__fee_waiver', 'uniq_id__caste', 'uniq_id__admission_status', 'uniq_id__join_year', 'sem__dept__course_id', 'uniq_id__gender', 'uniq_id__old_uniq_id')

                        if qry_stu_details[0]['uniq_id__old_uniq_id'] is not None:
                            q_room = HostelEligible.objects.filter(uni_id=qry_stu_details[0]['uniq_id__old_uniq_id'], status="INSERT").values('room_alloted')
                            # if len(q_room)>0:
                            #   room_alloted=q_room[0]['room_alloted']
                            if len(qry_stu_details) > 0 and session > 7:
                                q_room = get_uniq_id_alloted_seater(qry_stu_details[0]['uniq_id'], session_name)
                            # ABHI CHANGE KARNA HAI
                            if len(q_room) > 0 and session <= 7:
                                room_alloted = q_room[0]['room_alloted']
                            elif len(q_room) > 0 and session > 7:
                                room_alloted = q_room[0]['seat_part__value']
                            else:
                                room_alloted = "---"
                        else:
                            room_alloted = "---"
                        if qry_stu_details[0]['uniq_id__fee_waiver'] == 0:
                            qry_stu_details[0]['uniq_id__fee_waiver'] = 'N'
                        else:
                            qry_stu_details[0]['uniq_id__fee_waiver'] = 'Y'

                        n = len(seater_type)
                        for i in range(n):
                            q_check_paid1 = SubmitFeeComponentDetails.objects.filter(fee_component=fee_component[0]['id'], fee_id__cancelled_status='N', fee_id__session=session, fee_id__uniq_id=uniq_id, fee_id__receipt_type='N').exclude(fee_id__fee_rec_no__isnull=True).exclude(fee_id__status="DELETE").values('fee_id')
                            print(q_check_paid1,'q_check_paid')
                            total_amt = 0
                            q_check_paid = []
                            if len(q_check_paid1)>0:
                                for q in q_check_paid1:
                                    qry_check_paid2 = RefundFee.objects.filter(fee_id__uniq_id=uniq_id,fee_id=q['fee_id'],refund_type='W').values('fee_id')
                                    print(qry_check_paid2,'qry_check_paid1')
                                    if len(qry_check_paid2)==0:
                                        # q_check_paid.pop(q)
                                        q_check_paid.append(q)
                            if len(q_check_paid) == 0 or req_tp == "update":
                                n2 = len(fee_component[0]['data'])
                                print(n2,'n2')
                                for j in range(n2):
                                    print(seater_type[i]['sno'],'kkkk')
                                    if 'ONE TIME' in fee_component[0]['data'][j]['value']:
                                        q_check = SubmitFeeComponentDetails.objects.filter(fee_sub_component=fee_component[0]['data'][j]['sno'], fee_id__uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), fee_id__cancelled_status='N').exclude(fee_id__fee_rec_no__isnull=True).exclude(fee_id__status="DELETE").values()
                                        if len(q_check) == 0:
                                            qry_details = StuAccFeeSettings.objects.filter(join_year=qry_stu_details[0]['uniq_id__join_year'], caste=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__caste']), admission_status=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__admission_status']), fee_waiver=qry_stu_details[0]['uniq_id__fee_waiver'], fee_component=StudentAccountsDropdown.objects.get(sno=fee_component[0]['id']), fee_component_cat=StudentAccountsDropdown.objects.get(sno=fee_component[0]['data'][j]['sno']), course_id=StudentDropdown.objects.get(sno=qry_stu_details[0]['sem__dept__course_id']), gender=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__gender']), session=Semtiming.objects.get(uid=session), seater_type=HostelDropdown.objects.get(sno=seater_type[i]['sno'])).exclude(status="DELETE").values('value')
                                            print(qry_details,'qrybmm')
                                            if len(qry_details) > 0:
                                                total_amt += qry_details[0]['value']
                                    else:
                                        print(qry_stu_details, "fee_component", fee_component, seater_type[i])
                                        qry_details = StuAccFeeSettings.objects.filter(join_year=qry_stu_details[0]['uniq_id__join_year'], caste=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__caste']), admission_status=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__admission_status']), fee_waiver=qry_stu_details[0]['uniq_id__fee_waiver'], fee_component=StudentAccountsDropdown.objects.get(sno=fee_component[0]['id']), fee_component_cat=StudentAccountsDropdown.objects.get(sno=fee_component[0]['data'][j]['sno']), course_id=StudentDropdown.objects.get(sno=qry_stu_details[0]['sem__dept__course_id']), gender=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__gender']), session=Semtiming.objects.get(uid=session), seater_type=HostelDropdown.objects.get(sno=seater_type[i]['sno'])).exclude(status="DELETE").values('value')
                                        print(qry_details)
                                        if len(qry_details) > 0:
                                            total_amt += qry_details[0]['value']
                            else:
                                total_amt += 0

                            seater_type[i]['amount'] = total_amt
                        msg = "Success"
                        status = 200
                        data_values = {'msg': msg, 'data': {'seater_amt': seater_type, 'room_alloted': room_alloted}}

                    elif request.GET['request_type'] == 'dropdown':
                        operation = "fetch"
                        msg = "Success"
                        status = 200
                        data_values = {'msg': msg, 'data': get_custom_field_stu_acc(request.GET['field'])}

                    elif request.GET['request_type'] == 'transportation':
                        try:
                            req_tp = request.GET['operation']
                        except:
                            req_tp = "----"
                        operation = "fetch"
                        uniq_id = request.GET['uniq_id']

                        student_session = generate_session_table_name("studentSession_", session_name)
                        qry_stu_details = student_session.objects.filter(uniq_id=uniq_id).values('year', 'sem__dept', 'uniq_id__fee_waiver', 'uniq_id__caste', 'uniq_id__admission_status', 'uniq_id__join_year', 'sem__dept__course_id', 'uniq_id__gender')

                        fee_component = []
                        qry = StudentAccountsDropdown.objects.filter(field="FEE COMPONENTS", value__contains="TRANSPORTATION").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
                        for q in qry:
                            q_check_paid = SubmitFeeComponentDetails.objects.filter(fee_component=q['sno'], fee_id__cancelled_status='N', fee_id__session=session, fee_id__uniq_id=uniq_id, fee_id__receipt_type='N').exclude(fee_id__fee_rec_no__isnull=True).exclude(fee_id__status="DELETE").values('fee_id')
                            if len(q_check_paid) == 0 or req_tp == "update":
                                qr = StudentAccountsDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
                                for qi in qr:
                                    qry_details = StuAccFeeSettings.objects.filter(join_year=qry_stu_details[0]['uniq_id__join_year'], caste=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__caste']), admission_status=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__admission_status']), fee_waiver=qry_stu_details[0]['uniq_id__fee_waiver'], fee_component=StudentAccountsDropdown.objects.get(sno=q['sno']), fee_component_cat=StudentAccountsDropdown.objects.get(sno=qi['sno']), course_id=StudentDropdown.objects.get(sno=qry_stu_details[0]['sem__dept__course_id']), gender=StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__gender']), session=Semtiming.objects.get(uid=session)).exclude(status="DELETE").values('value')
                                    if len(qry_details) > 0:
                                        fee_component.append({'sno': qi['sno'], 'value': qi['value'], 'amount': qry_details[0]['value']})
                            else:
                                qr = StudentAccountsDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
                                for qi in qr:
                                    fee_component.append({'sno': qi['sno'], 'value': qi['value'], 'amount': 0})

                        msg = "Success"
                        status = 200
                        data_values = {'msg': msg, 'data': {'transportation_amt': fee_component}}

                ################# update fee receipt #####################
                elif request.method == 'PUT':
                    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
                    student_session = generate_session_table_name("studentSession_", session_name)
                    HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
                    HostelSeaterPriority = generate_session_table_name('HostelSeaterPriority_', session_name)

                    operation = "update"
                    
                    data = json.loads(request.body)
                    f_id = data['fee_id']

                    q_fee = SubmitFee.objects.filter(id=f_id).values('fee_rec_no', 'uniq_id', 'receipt_type', 'prev_fee_rec_no')

                    rec_type = q_fee[0]['receipt_type']
                    prev_fee_rec_no = q_fee[0]['prev_fee_rec_no']
                    fee_rec_no = q_fee[0]['fee_rec_no']

                    uniq_id = q_fee[0]['uniq_id']
                    fee_initial = fee_rec_no[0]

                    
                    if 'seater_type' in data:
                        seater_type = data['seater_type']

                        ####################### ADD SEAT ALLOTEMENT DETAILS FOR 1st Year and CHANGE PAID_STATUS in ALLOTMENT TABLE ##########################
                        if session > 7 and seater_type is not None:
                            check_data = student_session.objects.filter(uniq_id=uniq_id).annotate(admission_type__value=F('uniq_id__admission_type__value')).annotate(course__value=F('sem__dept__course_id__value')).values('uniq_id', 'year', 'course__value', 'sem__dept__course_id__value', 'admission_type__value', 'uniq_id__admission_type__value', 'uniq_id__join_year')
                            if len(check_data) > 0:
                                check_direct = is_direct_seat_allotment(check_data[0], seater_type, session_name, session)
                                print(check_direct, 'check_direct')
                                if check_direct[0]:
                                    
                                    previous_seat_data = HostelSeatAlloted.objects.filter(uniq_id=uniq_id, seat_part=seater_type).exclude(status="DELETE").values()

                                    if check_direct[1] == -1 and len(previous_seat_data) == 0:
                                        data = statusMessages.CUSTOM_MESSAGE('SELECTED SEAT IS NOT ALLOTED AVAILABLE')
                                        return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                                    
                                    if len(previous_seat_data) == 0:
                                        previous_seat_data = HostelSeatAlloted.objects.filter(uniq_id=uniq_id).update(status="DELETE")
                                        HostelStudentAppliction.objects.filter(uniq_id=uniq_id).update(status="DELETE")

                                        HostelSeatAlloted.objects.create(hostel_part=HostelDropdown.objects.get(sno=check_direct[1]), seat_part=HostelDropdown.objects.get(sno=seater_type), uniq_id=student_session.objects.get(uniq_id=uniq_id), paid_status="ALREADY PAID")
                                        StudentAcademic_data = StudentAcademic.objects.filter(uniq_id=uniq_id).values('max_10', 'total_10')
                                        gene = ""
                                        if len(StudentAcademic_data) > 0:
                                            gene = HostelStudentAppliction.objects.create(uniq_id=student_session.objects.get(uniq_id=uniq_id), uni_marks_obt=StudentAcademic_data[0]['total_10'], uni_max_marks=StudentAcademic_data[0]['max_10'], current_status="SEAT ALLOTED", agree=1)
                                        else:
                                            gene = HostelStudentAppliction.objects.create(uniq_id=student_session.objects.get(uniq_id=uniq_id), current_status="SEAT ALLOTED", agree=1)
                                        HostelSeaterPriority.objects.create(application_id=HostelStudentAppliction.objects.get(id=gene.id), seater=HostelDropdown.objects.get(sno=seater_type), priority=1)

                        ########## END ######## ADD SEAT ALLOTEMENT DETAILS FOR 1st Year and CHANGE PAID_STATUS in ALLOTMENT TABLE ##########################

                        ################### CHECK WHEATHER THE SELECTED SEAT IS ALLOTED TO STUDENT OR NOT ##########################
                        if session > 7 and seater_type is not None:
                            checking_seat_alloted = HostelSeatAlloted.objects.filter(seat_part=seater_type, uniq_id=uniq_id).values()
                            print(checking_seat_alloted, 'checking_seat_alloted')
                            if len(checking_seat_alloted) == 0:
                                data = statusMessages.CUSTOM_MESSAGE('SELECTED SEAT IS NOT ALLOTED TO THIS STUDENT')
                                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                            else:
                                HostelSeatAlloted.objects.filter(seat_part=seater_type, uniq_id=uniq_id).exclude(status="DELETE").exclude(paid_status="ALREADY PAID").update(paid_status="ALREADY PAID")

                        ######## END ###### CHECK WHEATHER THE SELECTED SEAT IS ALLOTED TO STUDENT OR NOT ##########################

                    else:
                        seater_type = None

                    if 'transportation_sub' in data:
                        transportation_sub = data['transportation_sub']
                    else:
                        transportation_sub = None

                    q_upd = SubmitFee.objects.filter(id=f_id).update(status="DELETE")

                    print("update")
                ################# generate new fee receipt ###############
                elif request.method == 'POST':
                    student_session = generate_session_table_name("studentSession_", session_name)
                    studentSession = generate_session_table_name("studentSession_", session_name)
                    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
                    HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
                    HostelSeaterPriority = generate_session_table_name('HostelSeaterPriority_', session_name)

                    data = json.loads(request.body)
                    operation = "insert"

                    rec_type = 'N'
                    prev_fee_rec_no = None
                    uniq_id = data['uniq_id']
                    fee_initial = data['fee_initial']
                    q_fee_initial = StudentAccountsDropdown.objects.filter(sno=fee_initial).values('value')
                    fee_initial = q_fee_initial[0]['value']
                    if 'seater_type' in data:
                        seater_type = data['seater_type']
                        ######################## ADD SEAT ALLOTEMENT DETAILS FOR 1st Year and CHANGE PAID_STATUS in ALLOTMENT TABLE ##########################
                        if session > 7 and seater_type is not None:
                            check_data = student_session.objects.filter(uniq_id=uniq_id).annotate(admission_type__value=F('uniq_id__admission_type__value')).annotate(course__value=F('sem__dept__course_id__value')).values('uniq_id', 'year', 'course__value', 'sem__dept__course_id__value', 'admission_type__value', 'uniq_id__admission_type__value', 'uniq_id__join_year')
                            if len(check_data) > 0:
                                hostel_id = data['hostel_id']
                                previous_seat_data = HostelSeatAlloted.objects.filter(uniq_id=uniq_id, hostel_part=hostel_id ,seat_part=seater_type).exclude(status="DELETE").values()
                                check_direct = is_direct_seat_allotment(check_data[0], seater_type, session_name, session,hostel_id)
                                if check_direct[0]:
                                    if check_direct[1] == -1 and len(previous_seat_data)==0:
                                        data = statusMessages.CUSTOM_MESSAGE('SELECTED SEAT IS NOT ALLOTED AVAILABLE')
                                        return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                                    previous_seat_data = HostelSeatAlloted.objects.filter(uniq_id=uniq_id).update(status="DELETE")
                                    HostelStudentAppliction.objects.filter(uniq_id=uniq_id).update(status="DELETE")
                                    HostelSeatAlloted.objects.create(hostel_part=HostelDropdown.objects.get(sno=check_direct[1]), seat_part=HostelDropdown.objects.get(sno=seater_type), uniq_id=student_session.objects.get(uniq_id=uniq_id), paid_status="ALREADY PAID")
                                    StudentAcademic_data = StudentAcademic.objects.filter(uniq_id=uniq_id).values('max_10', 'total_10')
                                    gene = ""
                                    if len(StudentAcademic_data) > 0:
                                        gene = HostelStudentAppliction.objects.create(uniq_id=student_session.objects.get(uniq_id=uniq_id), uni_marks_obt=StudentAcademic_data[0]['total_10'], uni_max_marks=StudentAcademic_data[0]['max_10'], current_status="SEAT ALLOTED", agree=1)
                                    else:
                                        gene = HostelStudentAppliction.objects.create(uniq_id=student_session.objects.get(uniq_id=uniq_id), current_status="SEAT ALLOTED", agree=1)
                                    HostelSeaterPriority.objects.create(application_id=HostelStudentAppliction.objects.get(id=gene.id), seater=HostelDropdown.objects.get(sno=seater_type), priority=1)
                        ########### END ######## ADD SEAT ALLOTEMENT DETAILS FOR 1st Year and CHANGE PAID_STATUS in ALLOTMENT TABLE ##########################

                        ################### CHECK WHEATHER THE SELECTED SEAT IS ALLOTED TO STUDENT OR NOT ##########################
                        if session > 7 and seater_type is not None:
                            checking_seat_alloted = HostelSeatAlloted.objects.filter(seat_part=seater_type,uniq_id=uniq_id).values()
                            if len(checking_seat_alloted) == 0:
                                data = statusMessages.CUSTOM_MESSAGE('SELECTED SEAT IS NOT ALLOTED TO THIS STUDENT')
                                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                            else:
                                HostelSeatAlloted.objects.filter(seat_part=seater_type,hostel_part=hostel_id,uniq_id=uniq_id).exclude(status="DELETE").exclude(paid_status="ALREADY PAID").update(paid_status="ALREADY PAID")

                        ######## END ###### CHECK WHEATHER THE SELECTED SEAT IS ALLOTED TO STUDENT OR NOT ##########################

                    else:
                        seater_type = None

                    if 'transportation_sub' in data:
                        transportation_sub = data['transportation_sub']
                    else:
                        transportation_sub = None

                if operation is not None and operation != "fetch":
                    print(operation, 'nnnnn')
                    sec = randint(0, 3)
                    time.sleep(sec)
                    session = request.session['Session_id']
                    student_session = generate_session_table_name("studentSession_", session_name)
                    qry_stu_details = student_session.objects.filter(uniq_id=uniq_id).values('year', 'sem__dept', 'uniq_id__fee_waiver', 'uniq_id__caste', 'uniq_id__admission_status', 'uniq_id__join_year', 'sem__dept__course_id', 'uniq_id__gender', 'uniq_id__admission_type__value', 'mob', 'uniq_id__name', 'uniq_id__admission_through__value')
                    flag_upsee = 0
                    fee_components = data['fee_components']

                    ################# 8 in below line should be checked ########## DONE ###### IT IS COMPONENT ID###################
                    if ((qry_stu_details[0]['year'] == 2 and 'LATERAL' in qry_stu_details[0]['uniq_id__admission_type__value']) or (qry_stu_details[0]['year'] == 1)) and (qry_stu_details[0]['uniq_id__admission_through__value'] in ['COUNSELLING', 'EWS']) and (8 in fee_components):
                        flag_upsee = 1

                    mob = qry_stu_details[0]['mob']
                    name = qry_stu_details[0]['uniq_id__name']
                    q_det2 = StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values('father_mob')
                    mob1 = q_det2[0]['father_mob']

                    if qry_stu_details[0]['uniq_id__fee_waiver'] == 0:
                        qry_stu_details[0]['uniq_id__fee_waiver'] = 'N'
                    else:
                        qry_stu_details[0]['uniq_id__fee_waiver'] = 'Y'

                    emp_id = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                    payment_values = data['payment_values']
                    fee_sub_comp = []
                    actual_fee = 0
                    upsee_amt = 0
                    print('nkkkk', operation)
                    if operation == 'insert' or rec_type == 'N':
                        print('iiiii')
                        for j in fee_components:
                            q_value = StudentAccountsDropdown.objects.filter(sno=j).values('value')
                            filter_data = {}
                            filter_data['join_year'] = qry_stu_details[0]['uniq_id__join_year']
                            filter_data['caste'] = StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__caste'])
                            filter_data['admission_status'] = StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__admission_status'])
                            filter_data['fee_waiver'] = qry_stu_details[0]['uniq_id__fee_waiver']
                            filter_data['fee_component'] = StudentAccountsDropdown.objects.get(sno=j)
                            filter_data['course_id'] = StudentDropdown.objects.get(sno=qry_stu_details[0]['sem__dept__course_id'])
                            filter_data['session'] = Semtiming.objects.get(uid=session)
                            filter_data['gender'] = StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__gender'])

                            if 'TRANSPORTATION' in q_value[0]['value']:
                                filter_data['fee_component_cat'] = StudentAccountsDropdown.objects.get(sno=transportation_sub)

                            elif 'HOSTEL' in q_value[0]['value']:
                                filter_data['seater_type'] = HostelDropdown.objects.get(sno=seater_type)

                            qry_details = StuAccFeeSettings.objects.filter(**filter_data).exclude(status="DELETE").values('value', 'fee_component_cat', 'fee_component_cat__value')
                            print(qry_details,'qry_details')
                            li = []
                            if rec_type == 'N':
                                # q_check_paid = SubmitFeeComponentDetails.objects.filter(fee_component=j, fee_id__cancelled_status='N', fee_id__session=session, fee_id__uniq_id=uniq_id, fee_id__receipt_type='N').exclude(fee_id__fee_rec_no__isnull=True).exclude(fee_id__status="DELETE").values('fee_id')
                                ########################## BY VRINDA #######################
                                q_check_paid1 = SubmitFeeComponentDetails.objects.filter(fee_component=j, fee_id__cancelled_status='N', fee_id__session=session, fee_id__uniq_id=uniq_id, fee_id__receipt_type='N').exclude(fee_id__fee_rec_no__isnull=True).exclude(fee_id__status="DELETE").values('fee_id')
                                print(q_check_paid1,'q_check_paid')
                                total_amt = 0
                                q_check_paid = []
                                if len(q_check_paid1)>0:
                                    for q in q_check_paid1:
                                        qry_check_paid2 = RefundFee.objects.filter(fee_id__uniq_id=uniq_id,fee_id=q['fee_id'],refund_type='W').values('fee_id')
                                        print(qry_check_paid2,'qry_check_paid1')
                                        if len(qry_check_paid2)==0:
                                            # q_check_paid.pop(q)
                                            q_check_paid.append(q)
                                ###########################################################
                            else:
                                q_check_paid = []
                            for qd in qry_details:
                                if len(q_check_paid) == 0:
                                    print(qd,q_value[0]['value'])
                                    if 'ONE TIME' in qd['fee_component_cat__value'] and 'HOSTEL' not in q_value[0]['value']:

                                        ####################
                                        # change on 6 jan 2021
                                        ####################
                                        # if (qry_stu_details[0]['year'] == 2 and 'LATERAL' in qry_stu_details[0]['uniq_id__admission_type__value']) or (qry_stu_details[0]['year'] == 1) and (qry_stu_details[0]['uniq_id__join_year'] == date.today().year):
                                        if (qry_stu_details[0]['year'] == 2 and 'LATERAL' in qry_stu_details[0]['uniq_id__admission_type__value']) or (qry_stu_details[0]['year'] == 1):
                                            actual_fee += qd['value']
                                            li.append({'id': qd['fee_component_cat'], 'value': qd['value']})
                                        else:
                                            actual_fee += 0
                                            li.append({'id': qd['fee_component_cat'], 'value': 0})
                                    elif 'ONE TIME' in qd['fee_component_cat__value'] and 'HOSTEL' in q_value[0]['value']:
                                        q_check = SubmitFeeComponentDetails.objects.filter(fee_sub_component=qd['fee_component_cat'], fee_id__uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id)).exclude(fee_id__cancelled_status='Y').exclude(fee_id__status="DELETE").values()
                                        if len(q_check) == 0:
                                            actual_fee += qd['value']
                                            li.append({'id': qd['fee_component_cat'], 'value': qd['value']})
                                    else:
                                        actual_fee += qd['value']
                                        li.append({'id': qd['fee_component_cat'], 'value': qd['value']})
                                else:
                                    actual_fee += 0
                                    li.append({'id': qd['fee_component_cat'], 'value': 0})

                            if flag_upsee == 1 and len(q_check_paid) == 0 and j == 8:
                                filter_data2 = {}
                                filter_data2['join_year'] = qry_stu_details[0]['uniq_id__join_year']
                                filter_data2['caste'] = StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__caste'])
                                filter_data2['admission_status'] = StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__admission_status'])
                                filter_data2['fee_waiver'] = qry_stu_details[0]['uniq_id__fee_waiver']
                                filter_data2['course_id'] = StudentDropdown.objects.get(sno=qry_stu_details[0]['sem__dept__course_id'])
                                filter_data2['session'] = Semtiming.objects.get(uid=session)
                                filter_data2['gender'] = StudentDropdown.objects.get(sno=qry_stu_details[0]['uniq_id__gender'])

                                qry_details2 = StuAccFeeSettings.objects.filter(**filter_data2).filter(fee_component_cat__value="UPSEE").exclude(status="DELETE").values('value', 'fee_component_cat', 'fee_component_cat__value')
                                if len(qry_details2) > 0:
                                    li.append({'id': qry_details2[0]['fee_component_cat'], 'value': qry_details2[0]['value']})
                                    upsee_amt = qry_details2[0]['value']

                            fee_sub_comp.append({'comp': j, 'data': li})

                        status = 200

                        if operation == "insert":
                            fee_rec_no = get_next_fee_receipt_no(fee_initial)

                        if seater_type is None:
                            q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=session), uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), receipt_type=rec_type, added_by=emp_id, actual_fee=actual_fee, prev_fee_rec_no=prev_fee_rec_no)
                        else:
                            q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=session), uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), receipt_type=rec_type, added_by=emp_id, actual_fee=actual_fee, seater_type=HostelDropdown.objects.get(sno=seater_type), prev_fee_rec_no=prev_fee_rec_no)

                        q_fee_id = SubmitFee.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), session=Semtiming.objects.get(uid=session)).exclude(status="DELETE").values('id').order_by('-id')[:1]
                        if len(q_fee_id) == 0:
                            if seater_type is None:
                                q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=session), uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), receipt_type=rec_type, added_by=emp_id, actual_fee=actual_fee, prev_fee_rec_no=prev_fee_rec_no)
                            else:
                                q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=session), uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), receipt_type=rec_type, added_by=emp_id, actual_fee=actual_fee, seater_type=HostelDropdown.objects.get(sno=seater_type), prev_fee_rec_no=prev_fee_rec_no)

                            q_fee_id = [{'id': q_ins.id}]
                        fee_id = q_fee_id[0]['id']
                        fee_paid = 0
                        for pv in payment_values:
                            mode_of_payment = payment_values[pv]
                            for mp in mode_of_payment:
                                try:
                                    for m, v in mp.items():
                                        qry_check_date = StudentAccountsDropdown.objects.filter(sno=int(m)).values('value')
                                        # if 'DATE' in qry_check_date[0]['value']:
                                        #   v=str(datetime.strptime(str(v).split('T')[0],"%Y-%m-%d").date().strftime('%d-%m-%Y'))

                                        if 'AMOUNT' in qry_check_date[0]['value']:
                                            fee_paid += float(v)

                                        qry_insert = ModeOfPaymentDetails.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), MOPcomponent=StudentAccountsDropdown.objects.get(sno=int(m)), value=str(v))
                                except:
                                    print(mode_of_payment, mp)
                                    for m, v in mp.items():
                                        qry_check_date = StudentAccountsDropdown.objects.filter(sno=int(m)).values('value')
                                        # if 'DATE' in qry_check_date[0]['value']:
                                        #   v=str(datetime.strptime(str(v).split('T')[0],"%Y-%m-%d").date().strftime('%d-%m-%Y'))

                                        if 'AMOUNT' in qry_check_date[0]['value']:
                                            fee_paid += float(v)

                                        qry_insert = ModeOfPaymentDetails.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), MOPcomponent=StudentAccountsDropdown.objects.get(sno=int(m)), value=str(v))
                        for sub in fee_sub_comp:
                            for s in sub['data']:
                                q_ins = SubmitFeeComponentDetails.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), fee_component=StudentAccountsDropdown.objects.get(sno=sub['comp']), fee_sub_component=StudentAccountsDropdown.objects.get(sno=s['id']), sub_component_value=s['value'])
                        due_value = None
                        refund_value = None
                        due_date = None
                        if (fee_paid + upsee_amt) > actual_fee:
                            refund_value = (fee_paid + upsee_amt) - actual_fee
                        elif (fee_paid + upsee_amt) < actual_fee:
                            due_value = actual_fee - (fee_paid + upsee_amt)
                            try:
                                due_date = datetime.strptime(str(data['due_date']).split('T')[0], "%Y-%m-%d").date() + relativedelta(days=+1)
                            except:
                                due_date = None
                        q_update = SubmitFee.objects.filter(id=fee_id).update(paid_fee=fee_paid, due_value=due_value, refund_value=refund_value, due_date=due_date)

                        if fee_rec_no[0] == 'A':
                            q_update_fee_status = student_session.objects.filter(uniq_id=uniq_id).update(fee_status="PAID")

                        q_update_rec = SubmitFee.objects.filter(id=fee_id).update(fee_rec_no=fee_rec_no)

                        if operation == "insert":
                            generate_lib_id(uniq_id)
                            update_fee_rec_no(fee_initial, fee_rec_no)
                            fee_type = ""
                            if fee_rec_no[0] == 'H':
                                fee_type = "Hostel"
                            elif fee_rec_no == "P":
                                fee_type = "Penalty"
                            elif fee_rec_no[0] == 'A':
                                fee_type = "Academic"
                            msg = "Dear , " + name + " , your " + fee_type + " Fee has been submitted by Accounts Office. Thanks KIET"
                            if mob != '' and mob is not None:
                                q_in = Daksmsstatus.objects.create(phonenos=mob, updatestatus='N', msg=msg, type='Accounts', counttry=0)
                            if mob1 != '' and mob1 is not None:
                                q_in2 = Daksmsstatus.objects.create(phonenos=mob1, updatestatus='N', msg=msg, type='Accounts', counttry=0)
                        print(fee_rec_no, due_value, added_by,'fee_rec_no, due_value, added_by')
                        check_update_due_receipts(fee_rec_no, due_value, added_by)

                    else:
                        print("update2")
                        qry_fee_details = SubmitFee.objects.filter(id=f_id).values('fee_rec_no', 'uniq_id', 'receipt_type', 'prev_fee_rec_no', 'uniq_id', 'session', 'actual_fee', 'seater_type')

                        print(qry_fee_details.query, 'qry_fee_details')
                        if seater_type is not None:
                            # q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=qry_fee_details[0]['session']),uniq_id=StudentPrimDetail.objects.get(uniq_id=qry_fee_details[0]['uniq_id']),receipt_type=qry_fee_details[0]['receipt_type'],added_by=added_by,actual_fee=qry_fee_details[0]['actual_fee'],seater_type=HostelDropdown.objects.get(sno=qry_fee_details[0]['seater_type']),prev_fee_rec_no=qry_fee_details[0]['prev_fee_rec_no'],fee_rec_no=qry_fee_details[0]['fee_rec_no'])
                            q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=qry_fee_details[0]['session']), uniq_id=StudentPrimDetail.objects.get(uniq_id=qry_fee_details[0]['uniq_id']), receipt_type=qry_fee_details[0]['receipt_type'], added_by=added_by, actual_fee=qry_fee_details[0]['actual_fee'], seater_type=HostelDropdown.objects.get(sno=seater_type), prev_fee_rec_no=qry_fee_details[0]['prev_fee_rec_no'], fee_rec_no=qry_fee_details[0]['fee_rec_no'])
                        else:
                            q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=qry_fee_details[0]['session']), uniq_id=StudentPrimDetail.objects.get(uniq_id=qry_fee_details[0]['uniq_id']), receipt_type=qry_fee_details[0]['receipt_type'], added_by=added_by, actual_fee=qry_fee_details[0]['actual_fee'], prev_fee_rec_no=qry_fee_details[0]['prev_fee_rec_no'], fee_rec_no=qry_fee_details[0]['fee_rec_no'])

                        fee_paid = 0
                        fee_id = q_ins.id
                        for pv in payment_values:
                            mode_of_payment = payment_values[pv]
                            for mp in mode_of_payment:
                                try:
                                    for m, v in mp.items():
                                        qry_check_date = StudentAccountsDropdown.objects.filter(sno=int(m)).values('value')

                                        if 'AMOUNT' in qry_check_date[0]['value']:
                                            fee_paid += int(v)

                                        qry_insert = ModeOfPaymentDetails.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), MOPcomponent=StudentAccountsDropdown.objects.get(sno=int(m)), value=str(v))
                                except:
                                    for m, v in (mode_of_payment[mp]).items():
                                        qry_check_date = StudentAccountsDropdown.objects.filter(sno=int(m)).values('value')

                                        if 'AMOUNT' in qry_check_date[0]['value']:
                                            fee_paid += int(v)

                                        qry_insert = ModeOfPaymentDetails.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), MOPcomponent=StudentAccountsDropdown.objects.get(sno=int(m)), value=str(v))
                        due_value = None
                        refund_value = None
                        due_date = None
                        actual_fee = qry_fee_details[0]['actual_fee']

                        if (fee_paid) > actual_fee:
                            refund_value = (fee_paid) - actual_fee
                        elif (fee_paid) < actual_fee:
                            due_value = actual_fee - (fee_paid)
                            try:
                                due_date = datetime.strptime(str(data['due_date']).split('T')[0], "%Y-%m-%d").date() + relativedelta(days=+1)
                            except:
                                due_date = None

                        print(due_date)
                        q_update = SubmitFee.objects.filter(id=fee_id).update(paid_fee=fee_paid, due_value=due_value, refund_value=refund_value, due_date=due_date)

                        print("hello")
                        check_update_due_receipts(fee_rec_no, due_value, added_by)

                        status = 200

                    data_values = {'msg': "Success", 'fee_rec_no': fee_rec_no}
                elif operation == "fetch":
                    a = 10
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def due_fee_pay(request):
    data2 = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session = request.session['Session_id']
                session_name = request.session['Session_name']

                if request.method == 'POST':
                    data = json.loads(request.body)
                    fee_id = data['fee_id']
                    filter_data = {}
                    filter_data['id'] = fee_id
                    added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                    data_values = fee_receipt_details(filter_data)
                    prev_due_date = data_values[0]['fee_details']['due_date']
                    q_log = DueDateLog.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), due_date=prev_due_date, added_by=added_by)

                    actual_fee = data_values[0]['fee_details']['due_value']
                    prev_fee_rec_no = data_values[0]['fee_details']['fee_rec_no']

                    session = request.session['Session_id']
                    uniq_id = data_values[0]['fee_details']['uniq_id']

                    student_session = generate_session_table_name("studentSession_", session_name)

                    emp_id = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                    payment_values = data['payment_values']

                    fee_initial = data_values[0]['fee_details']['fee_rec_no'][0]
                    status = 200

                    fee_rec_no = get_next_fee_receipt_no(fee_initial)

                    q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=session), uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), receipt_type="D", added_by=emp_id, actual_fee=actual_fee, prev_fee_rec_no=prev_fee_rec_no)

                    q_fee_id = SubmitFee.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), session=Semtiming.objects.get(uid=session)).exclude(status="DELETE").values('id').order_by('-id')[:1]
                    if len(q_fee_id) == 0:
                        q_ins = SubmitFee.objects.create(session=Semtiming.objects.get(uid=session), uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), receipt_type="D", added_by=emp_id, actual_fee=actual_fee, prev_fee_rec_no=prev_fee_rec_no)

                        q_fee_id = SubmitFee.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), session=Semtiming.objects.get(uid=session)).exclude(status="DELETE").values('id').order_by('-id')[:1]
                    fee_id = q_fee_id[0]['id']
                    fee_paid = 0
                    print(payment_values)
                    for pv in payment_values:
                        mode_of_payment = payment_values[pv]
                        print(pv,mode_of_payment)
                        for mp in mode_of_payment:
                            for m, v in mp.items():
                                print(mp.items())
                                qry_check_date = StudentAccountsDropdown.objects.filter(sno=int(m)).values('value')
                                if 'DATE' in qry_check_date[0]['value']:
                                    v = str(datetime.strptime(str(v).split('T')[0], "%Y-%m-%d").date().strftime('%d-%m-%Y'))

                                if 'AMOUNT' in qry_check_date[0]['value']:
                                    fee_paid += float(v)

                                qry_insert = ModeOfPaymentDetails.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), MOPcomponent=StudentAccountsDropdown.objects.get(sno=int(m)), value=str(v))

                    for sub in data_values[0]['fee_component_details']:
                        q_ins = SubmitFeeComponentDetails.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), fee_component=StudentAccountsDropdown.objects.get(sno=sub['fee_component']), fee_sub_component=StudentAccountsDropdown.objects.get(sno=sub['fee_sub_component']), sub_component_value=sub['sub_component_value'])
                    due_value = None
                    refund_value = None
                    due_date = None
                    print(actual_fee,fee_paid)
                    if fee_paid > actual_fee:
                        refund_value = fee_paid - actual_fee
                    elif fee_paid < actual_fee:
                        due_value = actual_fee - fee_paid
                        due_date = datetime.strptime(str(data['due_date']).split('T')[0], "%Y-%m-%d").date() + relativedelta(days=+1)
                    q_update = SubmitFee.objects.filter(id=fee_id).update(paid_fee=fee_paid, due_value=due_value, refund_value=refund_value, due_date=due_date)

                    q_update_rec = SubmitFee.objects.filter(id=fee_id).update(fee_rec_no=fee_rec_no)
                    update_fee_rec_no(fee_initial, fee_rec_no)
                    data2 = {'msg': "Success", 'fee_rec': fee_rec_no}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data2, status=status)


def cancel_fee_receipt(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session = request.session['Session_id']
                session_name = request.session['Session_name']
                if(request.method == 'PUT'):
                    data = json.loads(request.body)
                    fee_id = data['fee_id']
                    q_det = SubmitFee.objects.filter(id=fee_id).values('uniq_id', 'fee_rec_no', 'session')
                    q_ch = SubmitFee.objects.filter(prev_fee_rec_no=q_det[0]['fee_rec_no'], cancelled_status='N').exclude(status="DELETE").values('id')
                    if len(q_ch) == 0:
                        q_update = SubmitFee.objects.filter(id=fee_id).update(cancelled_status='Y')

                        q_check = SubmitFee.objects.filter(uniq_id=q_det[0]['uniq_id'], fee_rec_no__contains='A', session=Semtiming.objects.get(uid=session), cancelled_status='N').exclude(status="DELETE").values()

                        q_check_hostel = SubmitFee.objects.filter(id=fee_id, fee_rec_no__contains='H', session=Semtiming.objects.get(uid=session), cancelled_status='N').exclude(status="DELETE").values()

                        if len(q_check) == 0:
                            student_session = generate_session_table_name("studentSession_", session_name)
                            q_upd2 = student_session.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=q_det[0]['uniq_id'])).update(fee_status="UNPAID")

                        if len(q_check_hostel) == 0:
                            HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
                            q_upd2 = HostelSeatAlloted.objects.filter(uniq_id=q_det[0]['uniq_id']).update(paid_status="NOT PAID")

                        status = 200
                        data_values = {'msg': 'Fee Receipt Cancelled Successfully'}
                    else:
                        status = 202
                        data_values = {'msg': 'Fee Receipt Cannot be cancelled'}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def refund_pay(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                emp_id = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                if request.method == 'POST':
                    student_session = generate_session_table_name("studentSession_", session_name)
                    HostelSeatAlloted = generate_session_table_name("HostelSeatAlloted_", session_name)
                    HostelStudentAppliction = generate_session_table_name("HostelStudentAppliction_", session_name)

                    data = json.loads(request.body)
                    if data['request_type'] == 'form_data':
                        course = data['course']
                        c = course[0]

                        branch = data['branch']
                        # if c!='ALL':
                        #   branch=branch[0]
                        year = data['year']
                        gender = data['gender']
                        refund_type = data['refund_type']
                        fee_initial = get_fee_initial()
                        if course[0] == 'ALL':
                            course = qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno', flat=True)

                        if branch[0] == 'ALL':
                            branch = CourseDetail.objects.values_list('uid', flat=True)

                        if year[0] == 'ALL':
                            qry = CourseDetail.objects.all().aggregate(Max('course_duration'))
                            year = list(range(1, qry['course_duration__max'] + 1))

                        if refund_type == 'W':
                            qry_stu_uniq = student_session.objects.filter(year__in=year, uniq_id__dept_detail__in=branch, uniq_id__gender__in=gender, uniq_id__admission_status__value="WITHDRAWAL").values_list('uniq_id', flat=True)

                        else:
                            qry_stu_uniq = student_session.objects.filter(year__in=year, uniq_id__dept_detail__in=branch, uniq_id__gender__in=gender).values_list('uniq_id', flat=True)

                        filter_data = {}
                        if refund_type == 'E':
                            filter_data['refund_value__gt'] = 0
                        filter_data['session'] = session_id
                        filter_data['cancelled_status__in'] = ['N']

                        data2 = []
                        i = 0
                        for fi in fee_initial:
                            fiv = fi['value']

                            if refund_type == 'E':
                                qu = SubmitFee.objects.filter(fee_rec_no__contains=fiv, uniq_id__in=qry_stu_uniq, refund_value__isnull=False).filter(**filter_data).exclude(status="DELETE").values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'refund_value', 'paid_fee')
                                for qd in qu:
                                    q_ch = RefundFee.objects.filter(fee_id=SubmitFee.objects.get(id=qd['id'])).values()
                                    if len(q_ch) == 0:
                                        data2.append(qd)
                                        q_details2 = student_session.objects.filter(uniq_id=qd['uniq_id']).values('mob', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'year', 'sem__dept', 'uniq_id__gender', 'sem__dept__course')
                                        for k, v in q_details2[0].items():
                                            if k == 'uniq_id__dept_detail__dept__value':
                                                data2[i]['sem__dept__dept__value'] = v
                                            else:
                                                data2[i][k] = v
                                        q_det3 = StudentPerDetail.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=qd['uniq_id'])).values('fname')
                                        if len(q_det3) > 0:
                                            data2[i]['fname'] = q_det3[0]['fname']
                                        else:
                                            data2[i]['fname'] = "----"

                                        bank_details = StudentBankDetails.objects.filter(uniq_id=qd['uniq_id']).exclude(status="DELETE").values().order_by('-id')[:1]
                                        if len(bank_details) > 0:
                                            data2[i]['bank_details'] = list(bank_details)
                                        else:
                                            data2[i]['bank_details'] = []
                                        i += 1

                            elif refund_type == 'W':
                                u_id = []
                                is_withdrawl = list(HostelStudentAppliction.objects.filter(current_status="WITHDRAWAL").exclude(status="DELETE").values_list('uniq_id', flat=True).distinct())
                                # print(is_withdrawl,'is_withdrawl')
                                if len(is_withdrawl) > 0:
                                    for q in is_withdrawl:
                                        is_not_paid = list(HostelSeatAlloted.objects.filter(paid_status="ALREADY PAID", uniq_id=q).values())
                                        # print(is_not_paid,'is_not_paid')
                                        if len(is_not_paid) > 0:
                                            u_id.append(q)
                                else:
                                    is_not_paid = []
                                if len(u_id) > 0 and fiv == "H":
                                    # print(uid,'vrinda')
                                    # q_ins = RefundFee.objects.create(fee_id=SubmitFee.objects.get(id=fee_id),remark=remark,amount=amount,refund_type=refund_type,added_by=emp_id)
                                    query1 = SubmitFee.objects.filter(fee_rec_no__contains=fiv, uniq_id__in=u_id).filter(**filter_data).exclude(status="DELETE").values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'id', 'refund_value', 'paid_fee').distinct()
                                    print(query1, 'query1')
                                else:
                                    query1 = []
                                query2 = SubmitFee.objects.filter(fee_rec_no__contains=fiv, uniq_id__in=qry_stu_uniq).filter(**filter_data).exclude(status="DELETE").values('uniq_id', 'fee_rec_no', 'due_value', 'uniq_id__name', 'uniq_id', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__uni_roll_no', 'uniq_id__email_id', 'uniq_id__join_year', 'uniq_id__gender__value', 'session__session', 'due_date', 'id', 'cancelled_status', 'id', 'refund_value', 'paid_fee')
                                if len(query1) > 0:
                                    qu = query1
                                else:
                                    qu = query2
                                for qd in qu:
                                    print(qd['id'], qd['uniq_id__name'], 'singhal')
                                    q_ch = RefundFee.objects.filter(fee_id=SubmitFee.objects.get(id=qd['id'])).values()
                                    if len(q_ch) == 0:
                                        qd['refund_value'] = qd['paid_fee']
                                        data2.append(qd)
                                        q_details2 = student_session.objects.filter(uniq_id=qd['uniq_id']).values('mob', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'year', 'sem__dept', 'uniq_id__gender', 'sem__dept__course')
                                        for k, v in q_details2[0].items():
                                            if k == 'uniq_id__dept_detail__dept__value':
                                                data2[i]['sem__dept__dept__value'] = v
                                            else:
                                                data2[i][k] = v
                                        q_det3 = StudentPerDetail.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=qd['uniq_id'])).values('fname')
                                        if len(q_det3) > 0:
                                            data2[i]['fname'] = q_det3[0]['fname']
                                        else:
                                            data2[i]['fname'] = "----"
                                        i += 1
                            elif refund_type == 'S':
                                q_sec_id = StudentAccountsDropdown.objects.filter(value__contains="TUITION").values_list('sno', flat=True)
                                q_li = RefundFee.objects.values_list('fee_id', flat=True)

                                q_sec_val = SubmitFeeComponentDetails.objects.filter(fee_sub_component__in=q_sec_id, fee_id__fee_rec_no__contains=fiv, fee_id__uniq_id__in=qry_stu_uniq, fee_id__cancelled_status="N").exclude(fee_id__status="DELETE").exclude(fee_id__in=q_li).values('fee_id').annotate(sum=Sum('sub_component_value'))

                                for qs in q_sec_val:
                                    q_det = SubmitFee.objects.filter(id=qs['fee_id']).values('uniq_id', 'uniq_id__name', 'fee_rec_no', 'session__session')
                                    data2.append({'fee_id': qs['fee_id'], 'refund_amount': qs['sum']})
                                    for k, v in q_det[0].items():
                                        data2[i][k] = v
                                    i += 1

                        status = 200
                        data_values = {'data': data2}
                    elif data['request_type'] == 'submit':
                        fee_id = data['fee_id']
                        remark = data['remark']
                        amount = data['amount']
                        refund_type = data['refund_type']

                        # if refund_type=='W':
                        #   is_withdrawl = list(HostelStudentAppliction.objects.filter(current_status="WITHDRAWL").exclude(status="DELETE").values())
                        #   is_not_paid = list(HostelSeatAlloted.objects.filter(paid_status="UNPAID").exclude(status="DELETE").values())
                        #   if len(is_withdrawl)>0 and len(is_not_paid)>0:
                        #       q_ins = RefundFee.objects.create(fee_id=SubmitFee.objects.get(id=fee_id),remark=remark,amount=amount,refund_type=refund_type,added_by=emp_id)
                        q_ins = RefundFee.objects.create(fee_id=SubmitFee.objects.get(id=fee_id), remark=remark, amount=amount, refund_type=refund_type, added_by=emp_id)
                        q_get = RefundFee.objects.filter(fee_id=fee_id).values('id', 'fee_id__uniq_id').order_by('-id')[:1]
                        ref_id = q_get[0]['id']

                        q_bank = StudentBankDetails.objects.filter(uniq_id=q_get[0]['fee_id__uniq_id']).exclude(status="DELETE").values('id')
                        if len(q_bank) > 0:
                            q_upd = RefundFee.objects.filter(id=ref_id).update(bank_details_id=StudentBankDetails.objects.get(id=q_bank[0]['id']))
                        status = 200
                        data_values = {'msg': 'ok'}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def refund_report(request):
    print("vrinda")
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                if request.method == 'POST':
                    data = json.loads(request.body)
                    student_session = generate_session_table_name("studentSession_", session_name)

                    course = data['course']
                    branch = data['branch']
                    year = data['year']
                    gender = list(data['gender'])

                    if course[0] == 'ALL':
                        course = qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno', flat=True)

                    if branch[0] == 'ALL':
                        branch = CourseDetail.objects.values_list('uid', flat=True)

                    if year[0] == 'ALL':
                        qry = CourseDetail.objects.all().aggregate(Max('course_duration'))
                        year = list(range(1, qry['course_duration__max'] + 1))

                    qry_stu_uniq = student_session.objects.filter(year__in=year, uniq_id__dept_detail__in=branch, uniq_id__gender__in=gender).values_list('uniq_id', flat=True)

                    q_refund_report = RefundFee.objects.filter(fee_id__session=session_id, fee_id__uniq_id__in=qry_stu_uniq).values('fee_id__uniq_id', 'refund_type', 'amount', 'remark', 'fee_id', 'fee_id__uniq_id__name', 'fee_id__fee_rec_no', 'fee_id__uniq_id__batch_from', 'fee_id__uniq_id__batch_to', 'fee_id__uniq_id__uni_roll_no', 'fee_id__uniq_id__join_year', 'fee_id__uniq_id__gender__value', 'fee_id__session__session')
                    for q in q_refund_report:
                        q_details2 = student_session.objects.filter(uniq_id=q['fee_id__uniq_id']).values('mob', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'year', 'sem__dept', 'uniq_id__gender__value', 'sem__dept__course')
                        q['course'] = q_details2[0]['sem__dept__course__value']
                        q['year'] = q_details2[0]['year']
                        q['dept'] = q_details2[0]['uniq_id__dept_detail__dept__value']
                        q['mob'] = q_details2[0]['mob']
                        q['gender'] = q_details2[0]['uniq_id__gender__value']
                        if q['refund_type'] == 'E':
                            q['refund_type'] = 'Excess Amount'
                        elif q['refund_type'] == 'W':
                            q['refund_type'] = 'Withdrawal'
                        elif q['refund_type'] == 'S':
                            q['refund_type'] = 'Security'

                    status = 200
                    data_values = {'data': list(q_refund_report)}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def generate_receipt_file(receipt_name, filename, fee_id, bool_white, student_session):
    q_check = SubmitFee.objects.filter(id=fee_id).values('fee_rec_no', 'uniq_id__name', 'cancelled_status', 'actual_fee', 'paid_fee', 'refund_value', 'due_value','due_date', 'session__session', 'receipt_type', 'id', 'time_stamp', 'uniq_id', 'receipt_type', 'prev_fee_rec_no', 'uniq_id__gender__value')
    fee_rec_no = q_check[0]['fee_rec_no']
    uniq_id = q_check[0]['uniq_id']

    q_date = SubmitFee.objects.filter(fee_rec_no=fee_rec_no).extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('time_stamp').order_by('id')[:1]
    date = q_date[0]['time_stamp']

    stu_per = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname')
    if len(stu_per) > 0 and stu_per[0]['fname'] is not None :
        fname = stu_per[0]['fname']
    else:
        fname = "----"
    stu_det = student_session.objects.filter(uniq_id=uniq_id).values('year', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__exam_roll_no')

    q_mop_details = ModeOfPaymentDetails.objects.filter(fee_id=fee_id).values('MOPcomponent__value', 'value')

    fee_comp_details = SubmitFeeComponentDetails.objects.filter(fee_id=fee_id).values('fee_component__value', 'fee_sub_component__value', 'sub_component_value').order_by('fee_component', 'fee_sub_component')

    if not bool_white:
        img = Image.open(settings.FILE_PATH + "KIET_Fee_Receipt.jpg")
    else:
        img = Image.new(mode='RGB', size=(1478, 2100), color=(255, 255, 255, 0))

    # size = 1480, 2100
    size = 1490, 2006
    img.thumbnail(size, Image.ANTIALIAS)
    flag_upsee = 0
    upsee_amt = 0

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

    draw.text((1130, 340), receipt_name, (0, 0, 0), font=font)
    draw.text((115, 430), "Receipt No.:", (0, 0, 0), font=font)
    draw.text((115, 480), "Name:", (0, 0, 0), font=font)
    draw.text((115, 530), "Father's Name:", (0, 0, 0), font=font)
    if len(stu_det) > 0:
        if stu_det[0]['uniq_id__uni_roll_no'] is not None:
            draw.text((115, 580), "Roll No.:", (0, 0, 0), font=font)
        elif stu_det[0]['uniq_id__exam_roll_no'] is not None:
            draw.text((115, 580), "Exam Roll No.:", (0, 0, 0), font=font)
        else:
            draw.text((115, 580), "Roll No.:", (0, 0, 0), font=font)
    else:
        draw.text((400, 585), "----", (0, 0, 0), font=font2)

    draw.text((115, 630), "Course:", (0, 0, 0), font=font)

    draw.text((400, 435), fee_rec_no, (0, 0, 0), font=font2)
    draw.text((400, 485), q_check[0]['uniq_id__name'] + " (" + q_check[0]['uniq_id__gender__value'][0] + ")", (0, 0, 0), font=font2)
    draw.text((400, 535), fname, (0, 0, 0), font=font2)

    if len(stu_det) > 0:
        if stu_det[0]['uniq_id__uni_roll_no'] is not None:
            draw.text((400, 585), str(stu_det[0]['uniq_id__uni_roll_no']), (0, 0, 0), font=font2)
        elif stu_det[0]['uniq_id__exam_roll_no'] is not None:
            draw.text((400, 585), str(stu_det[0]['uniq_id__exam_roll_no']), (0, 0, 0), font=font2)
        else:
            draw.text((400, 585), "----", (0, 0, 0), font=font2)
    else:
        draw.text((400, 585), "----", (0, 0, 0), font=font2)

    if len(stu_det) > 0:
        draw.text((400, 635), stu_det[0]['sem__dept__course__value'], (0, 0, 0), font=font2)
    else:
        draw.text((400, 585), "----", (0, 0, 0), font=font2)

    draw.text((650, 430), "Session:", (0, 0, 0), font=font)
    draw.text((800, 435), q_check[0]['session__session'], (0, 0, 0), font=font2)

    draw.text((1050, 430), "Date:", (0, 0, 0), font=font)
    draw.text((1150, 435), str(date), (0, 0, 0), font=font2)

    img.paste(qr, (1175, 485))
    draw.text((650, 580), "Batch:", (0, 0, 0), font=font)

    if len(stu_det) > 0:
        draw.text((800, 585), str(stu_det[0]['uniq_id__batch_from']) + "-" + str(stu_det[0]['uniq_id__batch_to']), (0, 0, 0), font=font2)
    else:
        draw.text((400, 585), "----", (0, 0, 0), font=font2)

    draw.text((650, 630), "Branch:", (0, 0, 0), font=font)
    if len(stu_det) > 0:
        draw.text((800, 635), stu_det[0]['uniq_id__dept_detail__dept__value'], (0, 0, 0), font=font2)
    else:
        draw.text((400, 585), "----", (0, 0, 0), font=font2)

    draw.text((1050, 630), "Year:", (0, 0, 0), font=font)
    if len(stu_det) > 0:
        draw.text((1150, 635), str(stu_det[0]['year']), (0, 0, 0), font=font2)
    else:
        draw.text((400, 585), "----", (0, 0, 0), font=font2)

    draw.text((115, 780), "Particulars", (0, 0, 0), font=font)
    draw.text((1130, 780), "Amount (Rs.)", (0, 0, 0), font=font)

    y = 870
    if q_check[0]['receipt_type'] == 'N':
        for comp in fee_comp_details:
            if comp['sub_component_value'] > 0:
                if comp['fee_sub_component__value'] == 'UPSEE' and comp['fee_component__value'] == 'ACADEMIC':
                    flag_upsee = 1
                    upsee_amt = comp['sub_component_value']
                else:
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

    if flag_upsee == 1:
        y += 50
        draw.text((115, y), "UPSEE", (0, 0, 0), font=font4)
        draw.text((1170, y), str(upsee_amt) + "0", (0, 0, 0), font=font3)

    y += 50
    draw.text((115, y), "Amount Paid", (0, 0, 0), font=font4)
    draw.text((1170, y), str(q_check[0]['paid_fee']) + "0", (0, 0, 0), font=font3)

    y += 50
    if q_check[0]['due_value'] is not None and q_check[0]['due_value'] > 0:
        draw.text((115, y), "Due Amount"+str(q_check[0]['due_date']), (0, 0, 0), font=font4)
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

    tmp_image.save(settings.FILE_PATH + filename, "PDF", resolution=300.0)

def generate_receipt_file_coloured(receipt_name, filename, fee_id, bool_white, student_session):
    q_check = SubmitFee.objects.filter(id=fee_id).values('fee_rec_no', 'uniq_id__name', 'cancelled_status', 'actual_fee', 'paid_fee', 'refund_value', 'due_value','due_date', 'session__session', 'receipt_type', 'id', 'time_stamp', 'uniq_id', 'receipt_type', 'prev_fee_rec_no', 'uniq_id__gender__value')
    fee_rec_no = q_check[0]['fee_rec_no']
    uniq_id = q_check[0]['uniq_id']

    q_date = SubmitFee.objects.filter(fee_rec_no=fee_rec_no).extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('time_stamp').order_by('id')[:1]
    date = q_date[0]['time_stamp']

    stu_per = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname')
    if len(stu_per) > 0 and stu_per[0]['fname'] is not None :
        fname = stu_per[0]['fname']
    else:
        fname = "----"
    stu_det = student_session.objects.filter(uniq_id=uniq_id).values('year', 'uniq_id__dept_detail__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__exam_roll_no')

    q_mop_details = ModeOfPaymentDetails.objects.filter(fee_id=fee_id).values('MOPcomponent__value', 'value')

    fee_comp_details = SubmitFeeComponentDetails.objects.filter(fee_id=fee_id).values('fee_component__value', 'fee_sub_component__value', 'sub_component_value').order_by('fee_component', 'fee_sub_component')

    if not bool_white:
        img = Image.open(settings.FILE_PATH + "KIET_Fee_Receipt.jpg")
    else:
        img = Image.new(mode='RGB', size=(1478, 2100), color=(255, 255, 255, 0))

    # size = 1480, 2100
    size = 1490, 2006
    img.thumbnail(size, Image.ANTIALIAS)
    flag_upsee = 0
    upsee_amt = 0

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

        img.paste(ImageOps.colorize(w, (0, 0, 0), (196, 196, 196)), (200, 800),  w)

    draw.text((1130, 400), receipt_name, (0, 0, 0), font=font)
    draw.text((115, 480), "Receipt No.:", (0, 0, 0), font=font)
    draw.text((115, 530), "Name:", (0, 0, 0), font=font)
    draw.text((115, 580), "Father's Name:", (0, 0, 0), font=font)
    if len(stu_det) > 0:
        if stu_det[0]['uniq_id__uni_roll_no'] is not None:
            draw.text((115, 630), "Roll No.:", (0, 0, 0), font=font)
        elif stu_det[0]['uniq_id__exam_roll_no'] is not None:
            draw.text((115, 630), "Exam Roll No.:", (0, 0, 0), font=font)
        else:
            draw.text((115, 630), "Roll No.:", (0, 0, 0), font=font)
    else:
        draw.text((115, 635), "----", (0, 0, 0), font=font2)

    draw.text((115, 672), "Course:", (0, 0, 0), font=font)

    draw.text((400, 485), fee_rec_no, (0, 0, 0), font=font2)
    draw.text((400, 535), q_check[0]['uniq_id__name'] + " (" + q_check[0]['uniq_id__gender__value'][0] + ")", (0, 0, 0), font=font2)
    draw.text((400, 585), fname, (0, 0, 0), font=font2)

    if len(stu_det) > 0:
        if stu_det[0]['uniq_id__uni_roll_no'] is not None:
            draw.text((270, 635), str(stu_det[0]['uniq_id__uni_roll_no']), (0, 0, 0), font=font2)
        elif stu_det[0]['uniq_id__exam_roll_no'] is not None:
            draw.text((270, 635), str(stu_det[0]['uniq_id__exam_roll_no']), (0, 0, 0), font=font2)
        else:
            draw.text((270, 635), "----", (0, 0, 0), font=font2)
    else:
        draw.text((270, 635), "----", (0, 0, 0), font=font2)

    if len(stu_det) > 0:
        draw.text((270, 680), stu_det[0]['sem__dept__course__value'], (0, 0, 0), font=font2)
    else:
        draw.text((270, 680), "----", (0, 0, 0), font=font2)

    draw.text((650, 480), "Session:", (0, 0, 0), font=font)
    draw.text((800, 485), q_check[0]['session__session'], (0, 0, 0), font=font2)

    draw.text((1025, 480), "Date:", (0, 0, 0), font=font)
    draw.text((1125, 485), str(date), (0, 0, 0), font=font2)

    img.paste(qr, (1175, 535))
    draw.text((650, 630), "Batch:", (0, 0, 0), font=font)

    if len(stu_det) > 0:
        draw.text((800, 635), str(stu_det[0]['uniq_id__batch_from']) + "-" + str(stu_det[0]['uniq_id__batch_to']), (0, 0, 0), font=font2)
    else:
        draw.text((800, 635), "----", (0, 0, 0), font=font2)

    draw.text((1025, 672), "Branch:", (0, 0, 0), font=font)
    if len(stu_det) > 0:
        draw.text((1175, 680), stu_det[0]['uniq_id__dept_detail__dept__value'], (0, 0, 0), font=font2)
    else:
        draw.text((1175, 680), "----", (0, 0, 0), font=font2)

    draw.text((1025, 630), "Year:", (0, 0, 0), font=font)
    if len(stu_det) > 0:
        draw.text((1125, 635), str(stu_det[0]['year']), (0, 0, 0), font=font2)
    else:
        draw.text((1125, 635), "----", (0, 0, 0), font=font2)

    draw.text((115, 830), "Particulars", (0, 0, 0), font=font)
    draw.text((1080, 830), "Amount (Rs.)", (0, 0, 0), font=font)

    y = 920
    if q_check[0]['receipt_type'] == 'N':
        for comp in fee_comp_details:
            if comp['sub_component_value'] > 0:
                if comp['fee_sub_component__value'] == 'UPSEE' and comp['fee_component__value'] == 'ACADEMIC':
                    flag_upsee = 1
                    upsee_amt = comp['sub_component_value']
                else:
                    draw.text((115, y), comp['fee_sub_component__value'].replace("(ONE TIME)", "").title(), (0, 0, 0), font=font3)
                    draw.text((1130, y), str(float(comp['sub_component_value'])) + "0", (0, 0, 0), font=font3)
                    y += 50
    elif q_check[0]['receipt_type'] == 'D':
        draw.text((115, y), q_check[0]['prev_fee_rec_no'], (0, 0, 0), font=font3)
        draw.text((1130, y), str(q_check[0]['actual_fee']) + "0", (0, 0, 0), font=font3)
        y += 50

    y += 20
    draw.line((110, y, 1300, y), fill=(0, 0, 0), width=5)

    y += 20
    draw.text((115, y), "Total Fee", (0, 0, 0), font=font4)
    draw.text((1130, y), str(q_check[0]['actual_fee']) + "0", (0, 0, 0), font=font3)

    if flag_upsee == 1:
        y += 50
        draw.text((115, y), "UPSEE", (0, 0, 0), font=font4)
        draw.text((1130, y), str(upsee_amt) + "0", (0, 0, 0), font=font3)

    y += 50
    draw.text((115, y), "Amount Paid", (0, 0, 0), font=font4)
    draw.text((1130, y), str(q_check[0]['paid_fee']) + "0", (0, 0, 0), font=font3)

    y += 50
    if q_check[0]['due_value'] is not None and q_check[0]['due_value'] > 0:
        draw.text((115, y), "Due Amount"+"("+str(q_check[0]['due_date'])+")", (0, 0, 0), font=font4)
        draw.text((1130, y), str(q_check[0]['due_value']) + "0", (0, 0, 0), font=font3)
        y += 50
    elif q_check[0]['refund_value'] is not None and q_check[0]['refund_value'] > 0:
        draw.text((115, y), "Refund Amount", (0, 0, 0), font=font4)
        draw.text((1130, y), str(q_check[0]['refund_value']) + "0", (0, 0, 0), font=font3)
        y += 50

    y += 10
    draw.line((110, y, 1300, y), fill=(0, 0, 0), width=5)

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
            x2 = 1130
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

    tmp_image.save(settings.FILE_PATH + filename, "PDF", resolution=300.0)


def print_fee_receipt(request):

    msg = ""
    status = 401
    if request.META:
        if True:
            check = checkpermission(request, [1353])
            if 200 == 200:
                if request.method == 'GET':

                    session_name = request.session['Session_name']
                    session_id = request.session['Session_id']
                    student_session = generate_session_table_name("studentSession_", session_name)

                    fee_rec_no = request.GET['fee_rec_no']
                    q_check = SubmitFee.objects.filter(fee_rec_no=fee_rec_no).exclude(status="DELETE").values('fee_rec_no', 'uniq_id__name', 'cancelled_status', 'actual_fee', 'paid_fee', 'refund_value', 'due_value', 'session__session', 'receipt_type', 'id', 'time_stamp', 'uniq_id', 'receipt_type', 'prev_fee_rec_no')
                    if len(q_check) > 0:
                        fee_id = q_check[0]['id']
                        generate_receipt_file("Student's Copy", "student.pdf", fee_id, True, student_session)
                        generate_receipt_file("Account's Copy", "accounts.pdf", fee_id, True, student_session)

                        merger = PdfFileMerger()

                        pdfs = [settings.FILE_PATH + "student.pdf", settings.FILE_PATH + "accounts.pdf"]
                        for pdf in pdfs:
                            merger.append(open(pdf, 'rb'))

                        with open(settings.FILE_PATH + 'result.pdf', 'wb') as fout:
                            merger.write(fout)

                        with open(settings.FILE_PATH + "result.pdf", 'rb') as pdf:
                            response = HttpResponse(pdf, content_type='application/pdf')
                            response['Content-Disposition'] = 'inline;filename=some_file.pdf'

                            return response
                            pdf.closed

                        # pdf = open(settings.FILE_PATH+"result.pdf")
                        # pdf.seek(0)
                        # response = HttpResponse(pdf.read(), content_type="application/pdf")

                        status = 200
                        msg = "Success"
                        return response
                    else:
                        status = 404
                        msg = "Fee Receipt Not found"
                else:
                    status = 502
                    msg = 'Bad Gateway'
            else:
                status = 403
                msg = "Not Authorized"

        else:
            status = 401
            msg = "Session Expired"
    else:
        status = 500
        msg = "Error"
    return JsonResponse(data={'msg': msg}, status=status)

def print_fee_receipt_coloured(request):

    msg = ""
    status = 401
    if request.META:
        if True:
            check = checkpermission(request, [1353])
            if 200 == 200:
                if request.method == 'GET':

                    session_name = request.session['Session_name']
                    session_id = request.session['Session_id']
                    student_session = generate_session_table_name("studentSession_", session_name)

                    fee_rec_no = request.GET['fee_rec_no']
                    q_check = SubmitFee.objects.filter(fee_rec_no=fee_rec_no).exclude(status="DELETE").values('fee_rec_no', 'uniq_id__name', 'cancelled_status', 'actual_fee', 'paid_fee', 'refund_value', 'due_value', 'session__session', 'receipt_type', 'id', 'time_stamp', 'uniq_id', 'receipt_type', 'prev_fee_rec_no')
                    if len(q_check) > 0:
                        fee_id = q_check[0]['id']
                        generate_receipt_file_coloured("Student's Copy", "student.pdf", fee_id, False, student_session)
                        generate_receipt_file_coloured("Account's Copy", "accounts.pdf", fee_id, False, student_session)

                        merger = PdfFileMerger()

                        pdfs = [settings.FILE_PATH + "student.pdf", settings.FILE_PATH + "accounts.pdf"]
                        for pdf in pdfs:
                            merger.append(open(pdf, 'rb'))

                        with open(settings.FILE_PATH + 'result.pdf', 'wb') as fout:
                            merger.write(fout)

                        with open(settings.FILE_PATH + "result.pdf", 'rb') as pdf:
                            response = HttpResponse(pdf, content_type='application/pdf')
                            response['Content-Disposition'] = 'inline;filename=some_file.pdf'

                            return response
                            pdf.closed

                        # pdf = open(settings.FILE_PATH+"result.pdf")
                        # pdf.seek(0)
                        # response = HttpResponse(pdf.read(), content_type="application/pdf")

                        status = 200
                        msg = "Success"
                        return response
                    else:
                        status = 404
                        msg = "Fee Receipt Not found"
                else:
                    status = 502
                    msg = 'Bad Gateway'
            else:
                status = 403
                msg = "Not Authorized"

        else:
            status = 401
            msg = "Session Expired"
    else:
        status = 500
        msg = "Error"
    return JsonResponse(data={'msg': msg}, status=status)


def qr_img(request):
    img = qrcode.make('A2251')

    img = trim(img)
    img = img.resize((136, 136), Image.NEAREST)

    response = HttpResponse(content_type="image/png")
    img.save(response, 'png')
    return response


def StudentBankDetails_account(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                if request.method == 'GET':
                    if request.GET['request_type'] == 'send_ifsc':
                        ifsc = request.GET['ifsc']
                        url = "https://ifsc.razorpay.com/" + ifsc
                        response = urllib.request.urlopen(url)
                        data = json.loads(response.read())
                        if(data != 'Not Found'):
                            address = data['ADDRESS'] + ',' + data['STATE']
                            data['ADDRESS'] = address
                        else:
                            data = None
                        data_values = data
                        status = 200

                elif request.method == 'POST':
                    data = json.loads(request.body)
                    filters = {}
                    course = data['course']
                    branch = data['branch']
                    year = data['year']
                    if "toDate" in data and data['toDate'] is not None:
                        fromDate = datetime.strptime(str(data['fromDate']).split('T')[0], "%Y-%m-%d").date()
                        toDate = datetime.strptime(str(data['toDate']).split('T')[0], "%Y-%m-%d").date()
                        filters['time_stamp__range'] = [fromDate, toDate]
                    student_session = generate_session_table_name("studentSession_", session_name)
                    # include_them_only=list(StudentBankDetails.objects.filter(**filters).filter(status="INSERT").values_list('uniq_id',flat=True))
                    qr1 = list(student_session.objects.filter(year__in=year, uniq_id__dept_detail__in=branch, sem__dept__course_id__in=course).values('uniq_id__uni_roll_no', 'uniq_id__name', 'uniq_id__uniq_id'))
                    final_data = []
                    for q in qr1:
                        qry2 = StudentBankDetails.objects.filter(uniq_id=q['uniq_id__uniq_id']).filter(**filters).extra(select={'time_stamp': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y %%H:%%i:%%s')"}).exclude(status='DELETE').values('acc_name', 'acc_num', 'ifsc_code', 'branch', 'address', 'bank_name', 'edit_by__first_name', 'edit_by', 'time_stamp')
                        qry3 = StudentPrimDetail.objects.filter(uniq_id=q['uniq_id__uniq_id']).values('dept_detail__dept__value', 'dept_detail__course__value', 'lib', 'email_id')
                        qry4 = StudentPerDetail.objects.filter(uniq_id=q['uniq_id__uniq_id']).values('fname', 'mname')
                        qry5 = student_session.objects.filter(uniq_id=q['uniq_id__uniq_id']).values('mob', 'year')
                        qry6 = StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id__uniq_id']).values('father_mob')
                        if len(qry2) > 0:
                            q['bank_name'] = qry2[0]['bank_name']
                            q['branch'] = qry2[0]['branch']
                            q['address'] = qry2[0]['address']
                            q['ifsc_code'] = qry2[0]['ifsc_code']
                            q['acc_name'] = qry2[0]['acc_name']
                            q['time_stamp'] = qry2[0]['time_stamp']

                            if '&' not in str(qry2[0]['acc_num']):
                                q['acc_num'] = "&" + str(qry2[0]['acc_num'])
                            else:
                                q['acc_num'] = str(qry2[0]['acc_num'])
                            
                            q['edit_by__first_name'] = str(qry2[0]['edit_by__first_name']) + '(' + str(qry2[0]['edit_by']) + ')'
                            q['dept_detail__course__value'] = qry3[0]['dept_detail__course__value']
                            q['lib'] = qry3[0]['lib']
                            q['email_id'] = qry3[0]['email_id']
                            q['fname'] = qry4[0]['fname']
                            q['mname'] = qry4[0]['mname']
                            q['mob'] = qry5[0]['mob']
                            q['year'] = qry5[0]['year']
                            q['father_mob'] = qry6[0]['father_mob']
                            q['dept'] = qry3[0]['dept_detail__dept__value']

                            final_data.append(q)
                        elif "toDate" not in data or data['toDate'] is None:
                            q['bank_name'] = ''
                            q['branch'] = ''
                            q['address'] = ''
                            q['ifsc_code'] = ''
                            q['acc_name'] = ''
                            q['acc_num'] = ''
                            q['edit_by__first_name'] = ''
                            q['time_stamp'] = ''
                            q['dept_detail__course__value'] = qry3[0]['dept_detail__course__value']
                            q['lib'] = qry3[0]['lib']
                            q['email_id'] = qry3[0]['email_id']
                            q['fname'] = qry4[0]['fname']
                            q['mname'] = qry4[0]['mname']
                            q['mob'] = qry5[0]['mob']
                            q['year'] = qry5[0]['year']
                            q['father_mob'] = qry6[0]['father_mob']
                            q['dept'] = qry3[0]['dept_detail__dept__value']

                            final_data.append(q)

                    data_values = {'data': final_data}
                    status = 200
                elif request.method == 'PUT':
                    data = json.loads(request.body)
                    uniq_id = data['uniq_id']
                    acc_name = data['acc_name']
                    acc_num = data['acc_num']
                    if '&' in str(acc_num):
                        acc_num = acc_num.split('&')[1]
                    ifsc_code = data['ifsc_code']
                    bank_name = data['bank_name']
                    branch = data['branch']
                    address = data['address']
                    qry = StudentBankDetails.objects.filter(uniq_id=uniq_id).update(status='DELETE')
                    qry1 = StudentBankDetails.objects.create(acc_name=acc_name, acc_num=acc_num, bank_name=bank_name, ifsc_code=ifsc_code, branch=branch, address=address, uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id), status='INSERT', edit_by=AuthUser.objects.get(username=request.session['hash1']))
                    status = 200
                    data_values = {'msg': "Data Added Succesfully"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        data_values = {"message": "Could Not Display"}
        status = 500
    return JsonResponse(data=data_values, status=status, safe=False)


# /////////////////////////REPORT MADE AFTER 22ND DEC - DHRUV AGARWAL ////////////////////////////
def getFeeReceipts(extra):

    q_fee_receipts = SubmitFee.objects.filter(**extra).exclude(cancelled_status='Y').exclude(status='DELETE').extra(select={'receipt_date': "DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('fee_rec_no', 'id', 'receipt_type', 'receipt_date', 'session__session').order_by('receipt_date').distinct()
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


def get_stu_fee_receipts_report(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                if request.method == 'GET':
                    filter_data = {}
                    request_type = request.GET['request_type']
                    filter_data['session'] = Semtiming.objects.get(uid=session_id)
                    data = request.GET['data']
                    flag = 0
                    if request.GET['type'] == "STU_NAME":
                        uniq_id = data
                        flag = 1
                    if request.GET['type'] == 'ROLL_NO':
                        temp_roll = StudentPrimDetail.objects.filter(uni_roll_no=data).values('uniq_id')
                        temp_lib = StudentPrimDetail.objects.filter(lib=data).values('uniq_id')
                        temp_reciept = SubmitFee.objects.filter(fee_rec_no=data).values('fee_rec_no')
                        temp_dd_ka_no = ModeOfPaymentDetails.objects.filter(value=data).values('fee_id__fee_rec_no')
                        if len(temp_roll) > 0 and request_type == "FEE REPORT":
                            uniq_id = temp_roll[0]['uniq_id']
                            flag = 1
                        elif len(temp_lib) > 0 and request_type == "FEE REPORT":
                            uniq_id = temp_lib[0]['uniq_id']
                            flag = 1
                        elif len(temp_reciept) > 0 and request_type == "RECEIPT REPORT":
                            receipt_no = temp_reciept[0]['fee_rec_no']
                            flag = 2
                        elif len(temp_dd_ka_no) > 0 and request_type == "RECEIPT REPORT":
                            receipt_no = temp_dd_ka_no[0]['fee_id__fee_rec_no']
                            flag = 2
                    if flag == 1:
                        query = getFeeReceipts({"uniq_id": uniq_id})
                        data_values['data'] = query
                        data_values['msg'] = "SUCCESS"
                        status = 200
                    elif flag == 2:
                        query = getFeeReceipts({"fee_rec_no": receipt_no})
                        data_values['data'] = query
                        data_values['msg'] = "SUCCESS"
                        status = 200
                    else:
                        data_values['msg'] = "NO DATA"
                        status = 202
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def unpaid_report(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                if request.method == 'POST':
                    data = json.loads(request.body)
                    student_session = generate_session_table_name("studentSession_", session_name)
                    course = data['course']
                    branch = data['branch']
                    year = data['year']
                    gender = data['gender']
                    fee_initial = data['fee_initial']

                    if course == 'ALL':
                        course = qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno', flat=True)

                    if branch[0] == 'ALL':
                        branch = CourseDetail.objects.values_list('uid', flat=True)

                    if year[0] == 'ALL':
                        qry = CourseDetail.objects.all().aggregate(Max('course_duration'))
                        year_li = list(range(1, qry['course_duration__max'] + 1))
                    data2 = []

                    exclude_them = SubmitFee.objects.filter(uniq_id__gender__in=gender, status="INSERT", cancelled_status="N", session=session_id, fee_rec_no__contains="A").values_list('uniq_id', flat=True).distinct()

                    qry_stu_uniq = list(student_session.objects.filter(year__in=year, uniq_id__dept_detail__in=branch, uniq_id__gender__in=gender).exclude(uniq_id__in=exclude_them).exclude(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED")).values('uniq_id', 'year', 'session__session', 'uniq_id__join_year', 'uniq_id__gender__value', 'uniq_id__admission_status__value', 'uniq_id__admission_through__value', 'sem__dept__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__exam_roll_no', 'uniq_id__name', 'uniq_id__exam_roll_no', 'uniq_id__email_id'))
                    for student in qry_stu_uniq:
                        per_detail = StudentPerDetail.objects.filter(uniq_id=student['uniq_id']).values('fname')
                        family_detail = StudentFamilyDetails.objects.filter(uniq_id=student['uniq_id']).values('father_mob')
                        student['fname'] = per_detail[0]['fname']
                        student['mob'] = family_detail[0]['father_mob']

                    status = 200
                    data_values = {'data': qry_stu_uniq}
                else:
                    status = 400
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def transport_report(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                if request.method == 'POST':
                    data = json.loads(request.body)
                    print(data)
                    student_session = generate_session_table_name("studentSession_", session_name)
                    filters = {}
                    filtering = {}
                    if "branch" in data:
                        filters['fee_id__uniq_id__dept_detail__in'] = data['branch']

                    if "year" in data:
                        filtering['year__in'] = data['year']

                    if "gender" in data:
                        filters['fee_id__uniq_id__gender__in'] = data['gender']

                    if "transport" in data:
                        filters['fee_sub_component__in'] = data['transport']
                    include_only = list(student_session.objects.filter(**filtering).values_list('uniq_id', flat=True))
                    data2 = []

                    consolidate = list(SubmitFeeComponentDetails.objects.filter(fee_id__uniq_id__in=include_only, fee_id__status="INSERT", fee_id__cancelled_status="N", fee_id__session=session_id, fee_id__receipt_type="N").exclude(Q(fee_id__uniq_id__admission_status__value="WITHDRAWAL") | Q(fee_id__uniq_id__admission_status__value="FAILED") | Q(fee_id__uniq_id__admission_status__value="PASSED")).filter(**filters).values('fee_sub_component__value').annotate(sumer=Count('id')).distinct())

                    detailed = SubmitFeeComponentDetails.objects.filter(fee_id__uniq_id__in=include_only, fee_id__status="INSERT", fee_id__cancelled_status="N", fee_id__session=session_id, fee_id__receipt_type="N").exclude(Q(fee_id__uniq_id__admission_status__value="WITHDRAWAL") | Q(fee_id__uniq_id__admission_status__value="FAILED") | Q(fee_id__uniq_id__admission_status__value="PASSED")).filter(**filters).values('fee_sub_component__value', 'fee_id__uniq_id', 'fee_id__fee_rec_no').distinct()

                    for per in detailed:
                        qry_stu_uniq = list(student_session.objects.filter(uniq_id=per['fee_id__uniq_id']).values('uniq_id', 'year', 'session__session', 'uniq_id__join_year', 'uniq_id__gender__value', 'uniq_id__admission_status__value', 'uniq_id__admission_through__value', 'sem__dept__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__exam_roll_no', 'uniq_id__name', 'uniq_id__exam_roll_no', 'uniq_id__email_id'))
                        per_detail = StudentPerDetail.objects.filter(uniq_id=per['fee_id__uniq_id']).values('fname')
                        family_detail = StudentFamilyDetails.objects.filter(uniq_id=per['fee_id__uniq_id']).values('father_mob')
                        data2.append(qry_stu_uniq[0])
                        data2[-1]['fname'] = per_detail[0]['fname']
                        data2[-1]['mob'] = family_detail[0]['father_mob']
                        data2[-1]['transport'] = per['fee_sub_component__value']
                        data2[-1]['uniq_id__fee_rec_no'] = per['fee_id__fee_rec_no']

                    status = 200
                    data_values = {'data': {'consolidate': consolidate, 'detailed': data2}}
                else:
                    status = 400
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


# ////////////////////////////////////////////////////////////////////////////

def gen_payment_component_format(list_data, reciept_details):
    temp_mode_of_pay_list = []

    for detail_per in list_data:
        field_name = detail_per['fee_sub_component__value'].upper()
        field_value = detail_per['sub_component_value']

        if "(" in reciept_details['uniq_id__dept_detail__course__value']:
            reciept_details['uniq_id__dept_detail__course__value'] = reciept_details['uniq_id__dept_detail__course__value'].split("(")[0]

        if detail_per['fee_component__value'] == "ACADEMIC" or detail_per['fee_component__value'] == "J&K":
            if "TUITION FEE" in field_name:
                if reciept_details['uniq_id__admission_type__value'] is not None and reciept_details['year'] is not None:
                    if ("LATERAL" not in reciept_details['uniq_id__admission_type__value'] and reciept_details['year'] == 1) or ("LATERAL" in reciept_details['uniq_id__admission_type__value'] and reciept_details['year'] == 2):
                        field_name = "ADMISSION FEE " + reciept_details['uniq_id__dept_detail__course__value']
                    else:
                        field_name = "Annual Fee " + reciept_details['uniq_id__dept_detail__course__value']

                if reciept_details['uniq_id__admission_type__value'] is not None:
                    if "LATERAL" in reciept_details['uniq_id__admission_type__value'] or "Annual" in field_name:
                        field_name = field_name + " " + str(reciept_details['year'])

            elif "SECURITY" in field_name:
                field_name = "SECURITY " + reciept_details['uniq_id__dept_detail__course__value'] + " " + str(reciept_details['uniq_id__batch_from'])

            elif "EXAM" in field_name:
                field_name = "UNIVERSITY FEE " + str(reciept_details['session__session'])

            elif "ALUMNI" in field_name:
                field_name = "Alumina meet"

            elif "EXTRA-C" in field_name:
                field_name = "Personality Development (Income)"

            elif "UPSEE" in field_name:
                field_name = "UPSEE " + str(reciept_details['uniq_id__join_year'])
                temp_mode_of_pay_list.append({'ledger_name': field_name, 'value_dr': field_value})
                continue

            elif "ENGLISH" in field_name:
                field_name = "English Comm. & Soft Skill"

            elif "BOOK BANK" in field_name:
                field_name = "BOOK BANK"

            temp_mode_of_pay_list.append({'ledger_name': field_name, 'value_cr': field_value})
            continue

        elif detail_per['fee_component__value'] == "HOSTEL":
            if "HOSTEL FEE" in field_name:
                temp_mode_of_pay_list.append({'ledger_name': "HOSTEL FEES", 'value_cr': int(field_value) - 46000})
                field_name = "MESS FEES"
                field_value = 46000

            elif "SECURITY" in field_name:
                field_name = "HOSTEL SECURITY " + reciept_details['uniq_id__dept_detail__course__value'] + " " + str(reciept_details['uniq_id__batch_from'])

            temp_mode_of_pay_list.append({'ledger_name': field_name, 'value_cr': field_value})
            continue
        else:
            if "AIR" in field_name or "AC" in field_name:
                field_name = "AC FACILITY"
            temp_mode_of_pay_list.append({'ledger_name': field_name, 'value_cr': field_value})
            continue
    return temp_mode_of_pay_list


def change_date_format(field_value):
    try:
        field_value = (datetime.strptime(str(field_value).split('T')[0], "%Y-%m-%d").date() + relativedelta(days=+1)).strftime("%d-%m-%Y")
    except:
        try:
            field_value = (datetime.strptime(str(field_value).split(' ')[0], "%Y-%m-%d").date() + relativedelta(days=+1)).strftime("%d-%m-%Y")
        except:
            try:
                field_value = (datetime.strptime(str(field_value).split(' ')[0], "%d-%m-%Y").date() + relativedelta(days=+1)).strftime("%d-%m-%Y")
            except:
                try:
                    field_value = (datetime.strptime(str(field_value).split(' ')[0], "%d-%m-%Y").date() + relativedelta(days=+1)).strftime("%d-%m-%Y")
                except:
                    field_value = str(field_value)
    return field_value


def gen_payment_mode_format(list_data, leger_details):
    temp_mode_of_pay_list = {}

    for detail_per in list_data:
        # print(detail_per)

        field_name = detail_per['MOPcomponent__value'].upper()
        field_value = detail_per['value']

        if "RECIEVER'S BANK" in field_name:
            field_name = "ledger_name"
            field_value = leger_details[field_value]

        elif " ID" in field_name or " NO" in field_name:
            field_name = "cheque_dd_no"

        elif " DATE" in field_name:
            field_name = "cheque_date"
            field_value = change_date_format(field_value)

        elif "AMOUNT" in field_name:
            field_name = "value_dr"

        elif "BANK" in field_name:
            field_name = "bank"

        temp_mode_of_pay_list[field_name] = field_value

    return temp_mode_of_pay_list


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


def get_leger_details():
    temp_leger_details = list(StudentAccountsDropdown.objects.filter(field__contains="RECIEVER'S BANK").exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'value'))
    leger_details = {}
    for x in temp_leger_details:
        leger_details[str(x['sno'])] = x['value']
    return leger_details


def gen_mode_of_payment(list_data):
    mode_of_pay_list = []
    count_mode_no = {}
    counter_skip = 0

    leger_details = get_leger_details()

    for per_index, per_payment in enumerate(list_data):

        if counter_skip > 0:
            counter_skip = counter_skip - 1
            continue

        if per_payment['MOPcomponent__pid'] not in count_mode_no:
            count_mode_no[per_payment['MOPcomponent__pid']] = len(StudentAccountsDropdown.objects.filter(pid=per_payment['MOPcomponent__pid']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'value'))
        temp_mode_of_pay_list = gen_payment_mode_format(list_data[per_index: per_index + count_mode_no[per_payment['MOPcomponent__pid']]], leger_details)

        counter_skip = count_mode_no[per_payment['MOPcomponent__pid']] - 1
        if per_payment['MOPcomponent__field'] == "CASH":
            temp_mode_of_pay_list['ledger_name'] = 'CASH'
        mode_of_pay_list.append(temp_mode_of_pay_list)

    return mode_of_pay_list

def gen_reciept_format(fee_rec_no, voucher_no, session_name):
    student_session = generate_session_table_name("studentSession_", session_name)

    reciept_details = list(SubmitFee.objects.filter(fee_rec_no=fee_rec_no).exclude(status="DELETE").values('session', 'session__session', 'cancelled_status', 'fee_rec_no', 'time_stamp', 'prev_fee_rec_no', 'actual_fee', 'paid_fee', 'uniq_id', 'uniq_id__name', 'uniq_id__batch_from', 'uniq_id__join_year', 'uniq_id__admission_status__value', 'uniq_id__admission_type__value', 'session__session', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__course__value', 'refund_value', 'due_value', 'receipt_type'))[0]

    qry_stu_uniq = list(student_session.objects.filter(uniq_id=reciept_details['uniq_id']).values('year'))
    if len(qry_stu_uniq) > 0:
        reciept_details['year'] = qry_stu_uniq[0]['year']
    else:
        reciept_details['year'] = 0

    data = list(SubmitFeeComponentDetails.objects.filter(fee_id__fee_rec_no=fee_rec_no).exclude(fee_id__status="DELETE").exclude(sub_component_value=0).values('fee_component', 'fee_component__value', 'fee_sub_component', 'fee_sub_component__value', 'sub_component_value').order_by('fee_component', 'fee_sub_component', 'id'))
    comp_of_pay_list = gen_payment_component_format(data, reciept_details)

    payment_detail = list(ModeOfPaymentDetails.objects.filter(fee_id__fee_rec_no=fee_rec_no).exclude(fee_id__status="DELETE").values('MOPcomponent', 'MOPcomponent__value', 'MOPcomponent__pid', 'MOPcomponent__field', 'value').distinct().order_by('id'))
    mode_of_pay_list = gen_mode_of_payment(payment_detail)

    if reciept_details['receipt_type'] is not "D":
        comp_of_pay_list.extend(mode_of_pay_list)
    else:
        comp_of_pay_list = mode_of_pay_list

    final_data = []

    narration_string = fee_rec_no + " " + reciept_details['uniq_id__name'] + " " + reciept_details['uniq_id__dept_detail__dept__value'] + " " + get_suffix(reciept_details['year'])
    try:
        date_data = datetime.strptime(str(reciept_details['time_stamp']).split('T')[0], "%Y-%m-%d").strftime("%d-%m-%Y")
    except:
        date_data = datetime.strptime(str(reciept_details['time_stamp']).split(' ')[0], "%Y-%m-%d").strftime("%d-%m-%Y")
    ledger_narration = ""
    ledger_name = ""

    if reciept_details['receipt_type'] == "D" or reciept_details['due_value'] is not None or reciept_details['refund_value'] is not None:
        ledger_narration = " ".join(narration_string.split(" ")[1:])
        if reciept_details['uniq_id__admission_type__value'] is not None and reciept_details['year'] is not None:
            if ("LATERAL" not in reciept_details['uniq_id__admission_type__value'] and reciept_details['year'] == 1) or ("LATERAL" in reciept_details['uniq_id__admission_type__value'] and reciept_details['year'] == 2):
                ledger_name = "ADM FEE RECEIVABLE " + reciept_details['uniq_id__dept_detail__course__value']
            else:
                ledger_name = "ANN FEE RECEIVABLE " + reciept_details['uniq_id__dept_detail__course__value']

    if reciept_details['receipt_type'] == "D":
        final_data.append({'voucher_no': voucher_no, 'voucher_type': "Receipt", 'date': date_data, 'ledger_name': ledger_name, 'value_cr': reciept_details['actual_fee'], 'value_dr': "", 'ledger_narration': ledger_narration, 'cheque_dd_no': "", 'cheque_date': "", 'bank': "", 'branch': "", 'narration': narration_string})

    for x in comp_of_pay_list:
        if 'voucher_no' not in x:
            x['voucher_no'] = voucher_no
        if 'voucher_type' not in x:
            x['voucher_type'] = "Receipt"
        if 'date' not in x:
            x['date'] = date_data
        if 'ledger_name' not in x:
            x['ledger_name'] = ""
        if 'value_cr' not in x:
            x['value_cr'] = ""
        if 'value_dr' not in x:
            x['value_dr'] = ""
        if 'ledger_narration' not in x:
            x['ledger_narration'] = ""
        if 'cheque_dd_no' not in x:
            x['cheque_dd_no'] = ""
        if 'cheque_date' not in x:
            x['cheque_date'] = ""
        if 'bank' not in x:
            x['bank'] = ""
        if 'branch' not in x:
            x['branch'] = ""
        if 'narration' not in x:
            x['narration'] = narration_string
        final_data.append(x)

    if reciept_details['due_value'] is not None:
        if reciept_details['due_value'] > 0:
            final_data.append({'voucher_no': voucher_no, 'voucher_type': "Receipt", 'date': date_data, 'ledger_name': ledger_name, 'value_cr': "", 'value_dr': reciept_details['due_value'], 'ledger_narration': ledger_narration, 'cheque_dd_no': "", 'cheque_date': "", 'bank': "", 'branch': "", 'narration': narration_string})

    if reciept_details['refund_value'] is not None:
        if reciept_details['refund_value'] > 0:
            final_data.append({'voucher_no': voucher_no, 'voucher_type': "Receipt", 'date': date_data, 'ledger_name': ledger_name, 'value_cr': reciept_details['refund_value'], 'value_dr': "", 'ledger_narration': ledger_narration, 'cheque_dd_no': "", 'cheque_date': "", 'bank': "", 'branch': "", 'narration': narration_string})

    return final_data


# def gen_reciept_format(fee_rec_no, voucher_no, session_name,cancelled_status):
#   student_session = generate_session_table_name("studentSession_", session_name)

#   reciept_details = list(SubmitFee.objects.filter(fee_rec_no=fee_rec_no,cancelled_status=cancelled_status).exclude(status="DELETE").values('session', 'session__session', 'cancelled_status', 'fee_rec_no', 'time_stamp', 'prev_fee_rec_no', 'actual_fee', 'paid_fee', 'uniq_id', 'uniq_id__name', 'uniq_id__batch_from', 'uniq_id__join_year', 'uniq_id__admission_status__value', 'uniq_id__admission_type__value', 'session__session', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__course__value', 'refund_value', 'due_value', 'receipt_type'))[0]###added cancelled status filter

#   qry_stu_uniq = list(student_session.objects.filter(uniq_id=reciept_details['uniq_id']).values('year'))
#   if len(qry_stu_uniq) > 0:
#       reciept_details['year'] = qry_stu_uniq[0]['year']
#   else:
#       reciept_details['year'] = 0

#   data = list(SubmitFeeComponentDetails.objects.filter(fee_id__fee_rec_no=fee_rec_no).exclude(fee_id__status="DELETE").exclude(sub_component_value=0).values('fee_component', 'fee_component__value', 'fee_sub_component', 'fee_sub_component__value', 'sub_component_value').order_by('fee_component', 'fee_sub_component', 'id'))
#   comp_of_pay_list = gen_payment_component_format(data, reciept_details)
#   payment_detail = list(ModeOfPaymentDetails.objects.filter(fee_id__fee_rec_no=fee_rec_no).exclude(fee_id__status="DELETE").values('MOPcomponent', 'MOPcomponent__value', 'MOPcomponent__pid', 'MOPcomponent__field', 'value').distinct().order_by('id'))
#   mode_of_pay_list = gen_mode_of_payment(payment_detail)

#   if reciept_details['receipt_type'] is not "D":
#       comp_of_pay_list.extend(mode_of_pay_list)
#   else:
#       comp_of_pay_list = mode_of_pay_list

#   final_data = []

#   narration_string = fee_rec_no + " " + reciept_details['uniq_id__name'] + " " + reciept_details['uniq_id__dept_detail__dept__value'] + " " + get_suffix(reciept_details['year'])
#   try:
#       date_data = datetime.strptime(str(reciept_details['time_stamp']).split('T')[0], "%Y-%m-%d").strftime("%d-%m-%Y")
#   except:
#       date_data = datetime.strptime(str(reciept_details['time_stamp']).split(' ')[0], "%Y-%m-%d").strftime("%d-%m-%Y")
#   ledger_narration = ""
#   ledger_name = ""

#   if reciept_details['receipt_type'] == "D" or reciept_details['due_value'] is not None or reciept_details['refund_value'] is not None:
#       ledger_narration = " ".join(narration_string.split(" ")[1:])
#       if reciept_details['uniq_id__admission_type__value'] is not None and reciept_details['year'] is not None:
#           if ("LATERAL" not in reciept_details['uniq_id__admission_type__value'] and reciept_details['year'] == 1) or ("LATERAL" in reciept_details['uniq_id__admission_type__value'] and reciept_details['year'] == 2):
#               ledger_name = "ADM FEE RECEIVABLE " + reciept_details['uniq_id__dept_detail__course__value']
#           else:
#               ledger_name = "ANN FEE RECEIVABLE " + reciept_details['uniq_id__dept_detail__course__value']

#   if reciept_details['receipt_type'] == "D":
#       final_data.append({'voucher_no': voucher_no, 'voucher_type': "Receipt", 'date': date_data, 'ledger_name': ledger_name, 'value_cr': reciept_details['actual_fee'], 'value_dr': "", 'ledger_narration': ledger_narration, 'cheque_dd_no': "", 'cheque_date': "", 'bank': "", 'branch': "", 'narration': narration_string})

#   for x in comp_of_pay_list:
#       if 'voucher_no' not in x:
#           x['voucher_no'] = voucher_no
#       if 'voucher_type' not in x:
#           x['voucher_type'] = "Receipt"
#       if 'date' not in x:
#           x['date'] = date_data
#       if 'ledger_name' not in x:
#           x['ledger_name'] = ""
#       if 'value_cr' not in x:
#           x['value_cr'] = ""
#       if 'value_dr' not in x:
#           x['value_dr'] = ""
#       if 'ledger_narration' not in x:
#           x['ledger_narration'] = ""
#       if 'cheque_dd_no' not in x:
#           x['cheque_dd_no'] = ""
#       if 'cheque_date' not in x:
#           x['cheque_date'] = ""
#       if 'bank' not in x:
#           x['bank'] = ""
#       if 'branch' not in x:
#           x['branch'] = ""
#       if 'narration' not in x:
#           x['narration'] = narration_string
#       final_data.append(x)

#   if reciept_details['due_value'] is not None:
#       if reciept_details['due_value'] > 0:
#           final_data.append({'voucher_no': voucher_no, 'voucher_type': "Receipt", 'date': date_data, 'ledger_name': ledger_name, 'value_cr': "", 'value_dr': reciept_details['due_value'], 'ledger_narration': ledger_narration, 'cheque_dd_no': "", 'cheque_date': "", 'bank': "", 'branch': "", 'narration': narration_string})

#   if reciept_details['refund_value'] is not None:
#       if reciept_details['refund_value'] > 0:
#           final_data.append({'voucher_no': voucher_no, 'voucher_type': "Receipt", 'date': date_data, 'ledger_name': ledger_name, 'value_cr': reciept_details['refund_value'], 'value_dr': "", 'ledger_narration': ledger_narration, 'cheque_dd_no': "", 'cheque_date': "", 'bank': "", 'branch': "", 'narration': narration_string})
#   return final_data

# print(gen_reciept_format("A26541", 1, "1920o"))

from datetime import datetime
def format_report(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = 200
            # check=checkpermission(request,[1353, ])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                if request.method == 'POST':
                    data = json.loads(request.body)
                    student_session = generate_session_table_name("studentSession_", session_name)
                    course = data['course']
                    branch = data['branch']
                    year = data['year']
                    receipt_status = data['receipt_status']
                    gender = data['gender']
                    fee_initial = list(StudentAccountsDropdown.objects.filter(sno=x).values_list('value', flat=True)[0] for x in data['fee_initial'])

                    from_date = datetime.strptime(str(data['from_date']), "%Y-%m-%d").date()
                    to_date = datetime.strptime(str(data['to_date']), "%Y-%m-%d").date()+timedelta(days=1)
                    print(type(from_date),type(to_date))
                    if course == 'ALL':
                        course = qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno', flat=True)

                    if 'ALL' in branch:
                        branch = CourseDetail.objects.values_list('uid', flat=True)

                    if 'ALL' in year:
                        qry = CourseDetail.objects.all().aggregate(Max('course_duration'))
                        year_li = list(range(1, qry['course_duration__max'] + 1))

                    final_data = []

                    qry_stu_uniq = list(student_session.objects.filter(year__in=year, uniq_id__dept_detail__in=branch, uniq_id__gender__in=gender).exclude(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED")).values_list('uniq_id', flat=True))
                    fee_reciept_list = []
                    for x in fee_initial:
                        qry=(list(SubmitFee.objects.raw('SELECT DISTINCT fee_rec_no,id FROM StuAccSubmitFee WHERE time_stamp>=%s AND time_stamp<=%s AND session=%s AND Uniq_id IN %s AND fee_rec_no REGEXP %s AND status  NOT LIKE "DELETE"',[from_date,to_date,session_id,qry_stu_uniq,x])))
                        for q in qry:
                            fee_reciept_list.append(q.fee_rec_no)
                        # fee_reciept_list.extend(list(SubmitFee.objects.filter(time_stamp__date__range=(from_date, to_date), uniq_id__in=qry_stu_uniq, status="INSERT", cancelled_status__in=receipt_status, session=session_id, fee_rec_no__contains=x).exclude(status="DELETE").values_list('fee_rec_no', flat=True).distinct()))

                    ##########################REMOVED EQUAL CHECK FROM TIMESTAMP BY YASH###########
                    check_first_reciept = set(SubmitFee.objects.filter(fee_rec_no__in=fee_reciept_list, time_stamp__date__lt=from_date).values_list('fee_rec_no', flat=True).distinct())
                    ################################################################################
                    fee_reciept_list = list(set(fee_reciept_list).difference(check_first_reciept))

                    for voucher_no, reciept in enumerate(fee_reciept_list):
                        final_data.extend(gen_reciept_format(reciept, voucher_no + 1, session_name))

                    status = 200

                    data_values = {'data': final_data}
                else:
                    status = 400
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)



def AccAcademicFeeLetter(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = 200
            # check=checkpermission(request,[1353, ])
            if check == 200:
                session_name = request.session['Session_name']
                sem_type = request.session['sem_type']
                session_id = request.session['Session_id']
                session = request.session['Session']
                if request.method == 'GET':
                    if int(session_name[:2]) < 19:
                        return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    data = request.GET['data']
                    temp_roll = StudentPrimDetail.objects.filter(uni_roll_no=data).values('uniq_id')
                    temp_lib = StudentPrimDetail.objects.filter(lib=data).values('uniq_id')
                    stu_data = []
                    if len(temp_roll) > 0:
                        uniq_id = temp_roll[0]['uniq_id']
                        stu_data = get_stu_data(temp_roll[0]['uniq_id'], session_name)
                    elif len(temp_lib) > 0:
                        uniq_id = temp_lib[0]['uniq_id']
                        stu_data = get_stu_data(temp_lib[0]['uniq_id'], session_name)
                    else:
                        msg = "Wrong Lib. ID or University Roll No."
                        status = 202

                    if len(stu_data) > 0:
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
                        status = 202
                        msg = "No data is found"
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


def student_insurance_report(request):
    data_values = {}
    data = []
    new_data = []
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1353])
            if check == 200:
                session_name = request.session['Session_name']
                session_id = request.session['Session_id']
                if int(session_name[:2]) < 19:
                    return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                if request.method == 'POST':

                    data = json.loads(request.body)

                    StudentFillInsurance = generate_session_table_name("StudentFillInsurance_", session_name)
                    student_session = generate_session_table_name("studentSession_", session_name)

                    year = data['year']
                    branch = data['branch']

                    if year[0] == 'ALL':
                        qry = CourseDetail.objects.all().aggregate(Max('course_duration'))
                        year = list(range(1, qry['course_duration__max'] + 1))

                    if branch[0] == 'ALL':
                        branch = CourseDetail.objects.values_list('uid', flat=True)

                    qry = list(StudentFillInsurance.objects.filter(uniq_id__year__in=year, uniq_id__uniq_id__dept_detail__in=branch).exclude(status="DELETE").values('uniq_id__uniq_id__dept_detail__dept__value', 'uniq_id__sem_id__dept__dept__value', 'uniq_id__mob', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__uniq_id', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__uniq_id__lib', 'uniq_id__year', 'uniq_id__section__section', 'uniq_id__sem__sem', 'nominee_name', 'nominee_relation', 'insurer_name', 'insurer_dob', 'insurer_aadhar_num', 'insurer_occupation', 'insurer_nominee_name', 'insurer_relation','uniq_id__uniq_id__gender__value').order_by('uniq_id__uniq_id__name'))

                    for q in qry:
                        dob = list(StudentPerDetail.objects.filter(uniq_id=q['uniq_id__uniq_id__uniq_id']).values('dob'))

                        q['Student_phone'] = q['uniq_id__mob']

                        for x in q.keys():
                            if type(q[x]) == str:
                                q[x] = q[x].upper()

                        if dob[0]['dob'] != None:
                            dob_date = datetime.strptime(str(dob[0]['dob']), "%Y-%m-%d").strftime("%d-%m-%Y")
                        else:
                            dob_date = '---'

                        if q['insurer_dob'] != None:
                            q['insurer_dob'] = datetime.strptime(str(q['insurer_dob']), "%Y-%m-%d").strftime("%d-%m-%Y")
                        else:
                            q['insurer_dob'] = '---'

                        q['Student_dob'] = dob_date
                        data_values = dob

                        if(q['uniq_id__year'] == 1 or q['uniq_id__year'] == "1"):
                            q['branch'] = q['uniq_id__uniq_id__dept_detail__dept__value']
                        else:
                            q['branch'] = q['uniq_id__sem_id__dept__dept__value']

                        if(q['insurer_relation'] == "FATHER"):
                            fmob = list(StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id__uniq_id__uniq_id']).values('father_mob'))
                            q['insurer_phone'] = fmob[0]['father_mob']
                        elif (q['insurer_relation'] == "MOTHER"):
                            Mmob = list(StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id__uniq_id__uniq_id']).values('mother_mob'))
                            q['insurer_phone'] = Mmob[0]['mother_mob']
                        else:
                            q['insurer_phone'] = "--"

                        new_data.append(q)

                    status = 200
                    data_values = {'data': new_data}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def remider_due_date():  
    session_name = request.session['Session_name']
    session_id=request.session['Session_id']
    student_session = generate_session_table_name("studentSession_", session_name)
    date1 =  date.today() + timedelta(days=2)
    data1 = list(SubmitFee.objects.filter(due_date=date1,session=session_id).exclude(due_value__isnull=True).exclude(cancelled_status='Y').exclude(uniq_id__isnull=True).exclude(status='DELETE').values('uniq_id','uniq_id__name','due_date','due_value','fee_rec_no'))
    now = datetime.now()
    for x in data1:
        print(len(data1))
        qry1 = list(SubmitFee.objects.filter(prev_fee_rec_no =x['fee_rec_no'], uniq_id =x['uniq_id']).exclude(cancelled_status='Y').exclude(status='DELETE').values('uniq_id','uniq_id__name','due_date','due_value','fee_rec_no'))
        if len(qry1)==0:
            qry = list(student_session.objects.filter(uniq_id=x['uniq_id']).values_list('mob',flat=True))
            x['mob'] = qry[0]
            due_date = datetime.strptime(str(x['due_date']),'%Y-%m-%d')
            new_due_date = datetime.strftime(due_date,'%d-%m-%Y')
            if 'H' in str(x['fee_rec_no']):
                mssg = "Dear "+str(x['uniq_id__name'])+" ,\n Due date of your balance fees i.e Rs "+str(x['due_value'])+" is "+str(new_due_date)+" .Submit your balance fees before the due date , failing which you will be debar from hostel.\nThanks Account Office (KIET)"
            else:
                mssg = "Dear "+str(x['uniq_id__name'])+" ,\n Due date of your balance fees i.e Rs "+str(x['due_value'])+" is  "+str(new_due_date)+" .Submit your balance fees before the due date , failing which you will be debar from your classes.\nThanks Account Office (KIET)"

            Daksmsstatus.objects.create(phonenos=qry[0], counttry=0,  rectimestamp=now, updatestatus='N', msg=mssg)
            list1 = Daksmsstatus.objects.filter(phonenos=qry[0],msg=mssg, rectimestamp=now).values("mainid").exclude(updatestatus="U")
            Sms_Api(list1[0]['mainid'], qry[0],mssg)
    data = {'msg':'Successfully messages transferred.'}
    return JsonResponse(data=data1 ,safe = False)



