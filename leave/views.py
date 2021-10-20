from __future__ import print_function
from django.shortcuts import render
# Create your views here.
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
import json
from itertools import chain, groupby
from django.http import HttpResponse, JsonResponse
from musterroll.models import EmployeePerdetail, Shifts
import time
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Count
from django.utils import timezone
from dashboard.views import CountLeave
from datetime import date
from datetime import datetime
import calendar
import datetime
from django.utils.dateparse import parse_date
from dateutil import parser
from django.db.models import F
from operator import itemgetter
import Accounts as acc
import yagmail
from threading import Thread
from StudentMMS.constants_functions import requestType
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
import pytz

from .models import *
from Accounts.models import AccountsSession, EmployeePayableDays, DaysGenerateLog, Days_Arrear_Leaves, Sign_In_Out_Arrear
from login.models import EmployeeDropdown, EmployeePrimdetail, AuthUser, MailService
from musterroll.models import Reporting, EmployeePerdetail
from attendance.models import Attendance2
from separation.models import SeparationReporting
from django.utils import timezone
from login.views import checkpermission


# Create your views here.


# VIEWS FOR HOLIDAY #######################3

def Add_Holiday_Type(request):
    data = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    Holi_Type = data['sv']
                    if EmployeeDropdown.objects.filter(field="HOLIDAY", value=Holi_Type).count() > 0:
                        msg = "Entry Already Exists!!"
                        status = 409
                    else:
                        qry = EmployeeDropdown.objects.create(pid=int(0), field='HOLIDAY', value=Holi_Type)
                        msg = "Data Successfully Added..."
                        status = 200
                    data = {'msg': msg}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data, status=status)


def ExtractDepartment(request):
    data_values = ''
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'GET'):
                    qry1 = EmployeeDropdown.objects.filter(field='Department').exclude(pid__isnull=True).exclude(value__isnull=True).extra(select={'dept_id': 'sno', 'val': 'value'}).values('dept_id', 'val')
                    data_values = {'dept': list(qry1)}
                    status = 200
                    msg = "Success"
                    data_values = {'data': data_values, 'msg': msg}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def ExtractHolidays(request):
    data_values = ''
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'GET'):
                    qry = EmployeeDropdown.objects.filter(field='HOLIDAY').exclude(value__isnull=True).extra(select={'number': 'sno', 'val': 'value'}).values('number', 'val')
                    data_values = {'h_name': list(qry)}
                    status = 200
                    msg = "Success"
                    data_values = {'data': data_values, 'msg': msg}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data_values, safe=False)


def View_Table(request):
    msg = ''
    data_values = ""

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'GET'):
                    qrya = Holiday.objects.extra(select={'f_date': "DATE_FORMAT(f_date,'%%d-%%m-%%Y')", 't_date': "DATE_FORMAT(t_date,'%%d-%%m-%%Y')"}).values('id', 'h_type', 'h_des', 'dept', 'dept__value', 'f_date', 't_date', 'status').exclude(status="DELETE").order_by('-f_date').order_by('-t_date')
                    if qrya:
                        length = len(qrya)
                        for i in range(0, length):
                            qry_b = EmployeeDropdown.objects.filter(sno=qrya[i]['h_type']).exclude(value__isnull=True).extra(select={'holiday_type': 'value', 'holiday_id': 'sno'}).values('holiday_type')
                            qry_b = list(qry_b)
                            qrya[i]['holiday_type'] = qry_b[0]['holiday_type']
                    date_server = json.dumps(str(datetime.datetime.now().date()), default=str)
                    data_values = {'date': date_server, 'table_info': list(qrya)}
                    status = 200
                    msg = "Success"
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    data_values = {'data': data_values, 'msg': msg}

    return JsonResponse(data=data_values, status=status)


def Add_Holiday(request):
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    H_Type = data['h_type']
                    Dept = data['dept'].split(",")
                    F_Date = str(data['f_date'])
                    T_Date = str(data['t_date'])
                    H_Desc = data['h_des']
                    Restricted_status = data['restricted']

                    F_Date = datetime.datetime.strptime(F_Date, '%Y-%m-%d').date()
                    T_Date = datetime.datetime.strptime(T_Date, '%Y-%m-%d').date()

                    flag_duplicate = False

                    if(F_Date > T_Date):
                        status = 400

                    else:
                        duplicate_holidays = list(Holiday.objects.filter(Q(f_date__lte=F_Date) & Q(t_date__gte=F_Date) | Q(f_date__lte=T_Date) & Q(t_date__gte=T_Date) | Q(f_date__range=(F_Date, T_Date)) | Q(t_date__range=(F_Date, T_Date)), status='INSERT', dept__in=Dept).values_list('dept__value', flat=True))
                        print(duplicate_holidays)
                        if(len(duplicate_holidays) != 0):
                            flag_duplicate = True

                        if flag_duplicate:
                            msg = "Entry Already Exists in Dept: " + ", ".join(duplicate_holidays)
                            status = 409

                        else:
                            F_Date = F_Date.strftime('%Y-%m-%d')
                            T_Date = T_Date.strftime('%Y-%m-%d')

                            qry2 = (Holiday(h_type=H_Type, h_des=H_Desc, dept=EmployeeDropdown.objects.get(sno=i), f_date=F_Date, t_date=T_Date, status="INSERT", restricted=Restricted_status) for i in Dept)
                            Holiday.objects.bulk_create(qry2)

                            msg = "Holiday successfully added!!"
                            status = 200

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    sent_data = {'msg': msg}
    return JsonResponse(data=sent_data, status=status)


def Delete_Holiday(request):
    data = ""

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'DELETE'):

                    data = json.loads(request.body)
                    if(len(data['leave_object_array']) != 0):
                        for i in data['leave_object_array']:
                            qry2 = Holiday.objects.filter(h_type=i['h_type'], h_des=i['h_des'], f_date=datetime.datetime.strptime(str(i['f_date']), "%d-%m-%Y").strftime("%Y-%m-%d"), t_date=datetime.datetime.strptime(str(i['t_date']), "%d-%m-%Y").strftime("%Y-%m-%d"), dept=i['dept']).delete()
                            msg = "Holiday Successfully Deleted..."
                            status = 200
                            data = {'msg': msg}
                    else:
                        msg = "Sorry No data to delete..."
                        status = 204
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data, status=status)


def assign_no_dues(request):
    if(request.body):
        data = json.loads(request.body)
        Category = data['category']
        Employee = data['employee']
        qry2 = NoDuesHead.objects.filter(emp_id=Category, due_head=Employee).count()
        if qry2 > 0:
            msg = "msg already exist"
        else:
            qry2 = NoDuesHead.objects.create(emp_id=Category, due_head=Employee)
            msg = "Data Sucessfully Added"

    else:

        msg = "invalid request"

    res = {'msg': msg}

    return JsonResponse(res, safe=False)


def delete_club_type(request):
    error = True
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Employee' and 'HR' in request.session['roles']:
                if request.body:
                    inp = json.loads(request.body.decode('utf-8'))
                    lid1 = inp['Lid1']
                    lid2 = inp['Lid2']
                    qry = LeaveClub.objects.filter(leave_id1=lid1, leave_id2=lid2).update(status='DELETE')
                    msg = "Leave Deleted Successfully..!!"
                    error = False
                else:
                    msg = "Invalid Input"
            else:
                msg = "not permitted"
        else:
            msg = "not logged in"
    else:
        msg = "Technical Error:wrong parameters"
    values = {'error': error, 'msg': msg}
    return JsonResponse(values, safe=False)


####################################PREVIOUS LEAVE QUOTA######################################
def quota_leave_detail(request):
    error = True
    msg = ''
    status = 500
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 1345])
            if(request.method == 'GET'):
                if 'request_type' in request.GET:
                    if request.GET['request_type'] == 'hod':
                        check = checkpermission(request, [425])
            if(check == 200):
                qry1 = EmployeeDropdown.objects.filter(field="TYPE OF EMPLOYMENT").exclude(value__isnull=True).extra(select={'v': 'value', 's': 'sno'}).values('v', 's')
                qry2 = EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).extra(select={'ev': 'value', 'es': 'sno'}).values('ev', 'es')
                qry3 = EmployeeDropdown.objects.filter(value="DESIGNATION").exclude(value__isnull=True).extra(select={'id': 'sno', 'field': 'field'}).values('id', 'field')
                qry_len = len(qry3)
                for x in range(0, qry_len):
                    qry3_a = EmployeeDropdown.objects.filter(pid=qry3[x]['id']).exclude(value__isnull=True).extra(select={'desg_id': 'sno', 'desg_name': 'value'}).values('desg_id', 'desg_name')
                    qry3[x]['designation'] = list(qry3_a)
                qry4 = LeaveType.objects.exclude(status='DELETE').extra(select={'emp_id': 'id', 'l_name': 'leave_name', 'l_abbr': 'leave_abbr'}).values('emp_id', 'l_name', 'l_abbr')

                data_values = {'toe': (list(qry1)), 'coe': (list(qry2)), 'leave': (list(qry4)), 'desg': (list(qry3))}
                error = False
                msg = "Success"
                status = 200
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"
    else:
        msg = "Technical Error : Wrong Parameters"

    data_to_be_sent = {'data_d': data_values, 'error': error, 'msg': msg}
    return JsonResponse(data_to_be_sent, status=status)


def delete_quota_type(request):
    status = 401
    if 'HTTP_COOKIE' in request.META:
        check = checkpermission(request, [211, 337])
        if(check == 200):
            if request.method == 'DELETE':

                inp = json.loads(request.body)
                lid = list(map(str, inp['quota_id']))

                qry = LeaveQuota.objects.filter(id__in=lid).update(status='DELETE')
                msg = "Leave Deleted Successfully..!!"

                for li in lid:
                    empids = []
                    qry_li = LeaveQuota.objects.filter(id=li).values('category_emp', 'designation', 'type_of_emp', 'leave_id')
                    qry_emp = EmployeePrimdetail.objects.filter(emp_category=qry_li[0]['category_emp'], desg=qry_li[0]['designation'], emp_type=qry_li[0]['type_of_emp']).values('emp_id')
                    for e in qry_emp:
                        empids.append(e['emp_id'])

                    qry_up = Leaveremaning.objects.filter(leaveid=qry_li[0]['leave_id'], empid__in=empids).update(remaining=0)
                status = 200
            else:
                status = 502
        else:
            status = 403
    else:
        status = 401

    values = {'status': status}
    return JsonResponse(data=values, status=status)


def leave_days(request):
    msg = ''
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'GET'):

                    no_of_days = request.GET['day_limit']
                    obj = LeaveType.objects.filter(status='INSERT').exclude(leave_abbr__contains="SHL").update(apply_days=no_of_days)
                    msg = "Days Limit Updated Successfully..!!"
                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    values = {'msg': msg}
    return JsonResponse(data=values, status=status)


def show_leavetype(request):
    msg = ""
    data = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'GET'):
                    qry_lapse = list(LeaveType.objects.filter(status='INSERT', leave_status='L').extra(select={'Lid': 'id', 'LeaveName': 'leave_name', 'abbr': 'leave_abbr', 'creditDay': 'credit_day', 'lapseStart': 'lapse_start', 'dayLimit': 'apply_days', 'monthsNo': 'lapse_month', 'CountBasis': 'hours_leave', 'hoursNo': 'hours', 'LeaveCountStatus': 'leaveCountStatus', 'LeaveFor': 'leaveforgender', 'creditType': 'credittype'}).values('Lid', 'LeaveName', 'abbr', 'creditDay', 'lapseStart', 'monthsNo', 'CountBasis', 'hoursNo', 'dayLimit', 'LeaveCountStatus', 'creditType', 'LeaveFor'))
                    qry_acc = list(LeaveType.objects.filter(status='INSERT', leave_status='A').extra(select={'Lid': 'id', 'LeaveName': 'leave_name', 'abbr': 'leave_abbr', 'creditDay': 'credit_day', 'lapseStart': 'lapse_start', 'dayLimit': 'apply_days', 'maxAcc': 'accumulate_max', 'CountBasis': 'hours_leave', 'hoursNo': 'hours', 'LeaveCountStatus': 'leaveCountStatus', 'LeaveFor': 'leaveforgender', 'creditType': 'credittype'}).values('Lid', 'LeaveName', 'abbr', 'creditDay', 'maxAcc', 'CountBasis', 'hoursNo', 'dayLimit', 'LeaveCountStatus', 'creditType', 'LeaveFor'))

                    data['lapse'] = list(qry_lapse)
                    data['Accumulate'] = list(qry_acc)
                    msg = "success"
                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    values = {'msg': msg, 'data': data}
    return JsonResponse(data=values, status=status)
######################################################### ADD LEAVE ###############################################


def add_leave(request):
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'POST'):
                    inp = json.loads(request.body.decode('utf-8'))
                    leave_name = inp['leave_name']
                    abb = inp['leave_abb'].upper()
                    credit = inp['credit']
                    status = inp['status']
                    LeaveFor = inp['LeaveFor']
                    creditType = inp['creditType']
                    leaveCountStatus = inp['LeaveCountStatus']
                    list_add = {'leave_name': leave_name, 'leave_abbr': abb, 'leave_status': status, 'credit_day': credit, 'leaveCountStatus': leaveCountStatus, 'credittype': creditType, 'leaveforgender': LeaveFor}
                    if status == 'A':
                        list_add['accumulate_max'] = inp['accumulate']
                    else:
                        lapse_date = inp['lapse_date']
                        months = inp['lap_mon']
                        list_add['lapse_start'] = lapse_date
                        list_add['lapse_month'] = months
                    if inp['hourly'] == "Y":
                        hours = inp['hours']
                        list_add['hours_leave'] = 'Y'
                        list_add['hours'] = hours
                    else:
                        list_add['hours_leave'] = 'N'
                    list_add['inserted_by'] = request.session["hash1"]
                    list_add['status'] = 'INSERT'
                    list_add['time_stamp'] = str(datetime.datetime.now())
                    testqry = LeaveType.objects.filter(leave_abbr=abb, status='INSERT').all().count()
                    if testqry > 0:
                        msg = "Leave Already Exists..!!"
                        status = 409
                    else:
                        qry = LeaveType.objects.create(**list_add)
                        msg = "Leave Added Successfully..!!"
                        status = 200

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    values = {'msg': msg}

    return JsonResponse(data=values, status=status)


def update_type(request):
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'PUT'):
                    inp = json.loads(request.body.decode('utf-8'))
                    lid = inp['id']

                    qry_leave = list(LeaveType.objects.filter(id=lid).values('leave_name', 'leave_abbr', 'leave_status', 'lapse_start', 'lapse_month', 'accumulate_max', 'hours_leave', 'hours', 'credit_day', 'apply_days', 'inserted_by', 'time_stamp', 'leaveCountStatus', 'credittype', 'leaveforgender'))
                    qry_leave[0]['status'] = 'DELETE'
                    qry = LeaveType.objects.create(**qry_leave[0])
                    leave_name = inp['leave_name']
                    abb = inp['leave_abb'].upper()

                    credit = inp['credit']
                    status1 = inp['status']
                    LeaveFor = inp['LeaveFor']
                    creditType = inp['creditType']
                    leaveCountStatus = inp['LeaveCountStatus']
                    list_add = {'leave_name': leave_name, 'leave_abbr': abb, 'leave_status': status1, 'credit_day': credit, 'leaveCountStatus': leaveCountStatus, 'credittype': creditType, 'leaveforgender': LeaveFor}
                    if status1 == 'A':
                        list_add['accumulate_max'] = inp['accumulate']
                    else:
                        lapse_date = inp['lapse_date']
                        months = inp['lap_mon']
                        list_add['lapse_start'] = lapse_date
                        list_add['lapse_month'] = months
                    if inp['hourly'] == "Y":
                        hours = inp['hours']
                        list_add['hours_leave'] = 'Y'
                        list_add['hours'] = hours
                    else:
                        list_add['hours_leave'] = 'N'
                    list_add['inserted_by'] = request.session["hash1"]
                    list_add['status'] = 'INSERT'
                    list_add['time_stamp'] = str(datetime.datetime.now())
                    qry = LeaveType.objects.filter(id=lid).update(**list_add)
                    msg = "Leave Updated Successfully..!!"
                    status = 200

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    values = {'msg': msg}
    return JsonResponse(data=values, status=status)


def delete_type(request):
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'DELETE'):
                    inp = json.loads(request.body.decode('utf-8'))
                    lid = inp['Lid']
                    qry = LeaveType.objects.filter(id=lid).update(status='DELETE')
                    msg = "Leave Deleted Successfully..!!"
                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    values = {'msg': msg}
    return JsonResponse(data=values, status=status)


def Club_Get_Leave(request):
    values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211])
            if(check == 200):

                if(request.method == 'GET'):

                    if(request.GET['request_type'] == 'onload'):
                        s = LeaveType.objects.exclude(status='DELETE').extra(select={'name': 'leave_name', 'abbr': 'leave_abbr', 'leave_id': 'id'}).values('leave_name', 'leave_abbr', 'id').all()
                        msg = "Success"
                        status = 200
                        values = {'msg': msg, 'data': list(s)}
                    elif(request.GET['request_type'] == 'previous'):
                        qry1 = LeaveClub.objects.exclude(status="DELETE").values('id', 'leave_id1', 'day_count1', 'leave_id2', 'day_count2', 'status', 'leave_id1__leave_name', 'leave_id2__leave_name').order_by('-id')
                        status = 200
                        values = {'data_d': list(qry1)}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=values, status=status)


def Club_Leave(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body.decode('utf-8'))
                    if data['leave_type1'] != 'ALL':
                        Type1 = LeaveType.objects.get(id=data['leave_type1'])
                    if data['leave_type2'] != 'ALL':
                        Type2 = LeaveType.objects.get(id=data['leave_type2'])
                    c1 = data['leavecount1']
                    c2 = data['leavecount2']
                    emp = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                    time = str(timezone.now() + timedelta(hours=5, minutes=30))

                    if(data['leave_type1'] == "ALL"):
                        qry_a = LeaveType.objects.exclude(status='DELETE').extra(select={'l_id': 'id'}).values('l_id')
                        for i in qry_a:
                            Type3 = LeaveType.objects.get(id=i['l_id'])
                            list_add = {'leave_id1': Type3, 'leave_id2': Type2, 'day_count1': c1, 'inserted_by': emp, 'day_count2': c2, 'status': 'INSERT', 'time_stamp': time}
                            cnt = LeaveClub.objects.filter(leave_id1=Type3).filter(leave_id2=Type2).filter(status='INSERT').count()
                            cnt1 = LeaveClub.objects.filter(leave_id1=Type3, leave_id2=Type2, status='INSERT', inserted_by=emp, day_count1=c1, day_count2=c2).count()
                            if cnt1 > 0:
                                msg = "Club Rules Already Defined..."
                                status = 409
                            elif cnt > 0:
                                cnt = LeaveClub.objects.filter(leave_id1=Type3).filter(leave_id2=Type2).filter(status='INSERT').update(status='DELETE')
                                qry = LeaveClub.objects.create(**list_add)
                                msg = "Club Rule Successfully Updated..."
                                status = 200
                            else:
                                qry = LeaveClub.objects.create(**list_add)
                                msg = "Club Rule Successfully Added..."
                                status = 200

                    elif(data['leave_type2'] == "ALL"):
                        qry_a = LeaveType.objects.exclude(status='DELETE').extra(select={'l_id': 'id'}).values('l_id')
                        for i in qry_a:
                            Type3 = LeaveType.objects.get(id=i['l_id'])
                            list_add = {'leave_id1': Type1, 'leave_id2': Type3, 'day_count1': c1, 'inserted_by': emp, 'day_count2': c2, 'status': 'INSERT', 'time_stamp': time}
                            cnt = LeaveClub.objects.filter(leave_id1=Type1).filter(leave_id2=Type3).filter(status='INSERT').count()
                            cnt1 = LeaveClub.objects.filter(leave_id1=Type1, leave_id2=Type3, status='INSERT', inserted_by=emp, day_count1=c1, day_count2=c2).count()
                            if cnt1 > 0:
                                msg = "Club Rules Already Defined..."
                                status = 409
                            elif cnt > 0:
                                cnt = LeaveClub.objects.filter(leave_id1=Type1).filter(leave_id2=Type3).filter(status='INSERT').update(status='DELETE')
                                qry = LeaveClub.objects.create(**list_add)
                                msg = "Club Rule Successfully Updated..."
                                status = 200
                            else:
                                qry = LeaveClub.objects.create(**list_add)
                                msg = "Club Rule Successfully Added..."
                                status = 200
                    else:
                        Type3 = LeaveType.objects.get(id=data['leave_type2'])
                        list_add = {'leave_id1': Type1, 'leave_id2': Type3, 'day_count1': c1, 'inserted_by': emp, 'day_count2': c2, 'status': 'INSERT', 'time_stamp': time}
                        cnt = LeaveClub.objects.filter(leave_id1=Type1).filter(leave_id2=Type3).filter(status='INSERT').count()
                        cnt1 = LeaveClub.objects.filter(leave_id1=Type1, leave_id2=Type3, status='INSERT', inserted_by=emp, day_count1=c1, day_count2=c2).count()
                        if cnt1 > 0:
                            msg = "Club Rules Already Defined..."
                            status = 409
                        elif cnt > 0:
                            cnt = LeaveClub.objects.filter(leave_id1=Type1).filter(leave_id2=Type3).filter(status='INSERT').update(status='DELETE')
                            qry = LeaveClub.objects.create(**list_add)
                            msg = "Club Rule Successfully Updated..."
                            status = 200
                        else:
                            qry = LeaveClub.objects.create(**list_add)
                            msg = "Club Rule Successfully Added..."
                            status = 200
                    values = {'msg': msg}

                elif(request.method == 'DELETE'):

                    inp = json.loads(request.body.decode('utf-8'))
                    lid1 = inp['Lid1']
                    lid2 = inp['Lid2']
                    qry = LeaveClub.objects.filter(leave_id1=lid1, leave_id2=lid2).update(status='DELETE')
                    msg = "Leave Deleted Successfully..!!"
                    status = 200
                    values = {'msg': msg}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=values, status=status)


def Leave_Quota_Table(request):
    msg = ""
    data_values = {}

    status = 401
    if request.META:
        if 'HTTP_COOKIE' in request.META:
            if request.user.is_authenticated:
                check = checkpermission(request, [211, 337])
                if(check == 200):

                    qry_leave_quota = LeaveQuota.objects.filter(Q(status="INSERT") | Q(status="UPDATE")).extra(select={'leave_quota_id': 'Id', 'num_of_leaves': 'No_Of_Leaves', 'categ_emp': 'Category_Emp', 'designation': 'designation', 'type_emp': 'type_of_emp', 'leave_id': 'Leave_Id'}).values('leave_quota_id', 'num_of_leaves', 'categ_emp', 'designation', 'type_emp', 'leave_id')

                    prev_quota_data = []
                    i = 0
                    for res in qry_leave_quota:
                        qry_coe = EmployeeDropdown.objects.filter(sno=res['categ_emp']).extra(select={'coe': 'Value'}).values('coe')
                        qry_toe = EmployeeDropdown.objects.filter(sno=res['type_emp']).extra(select={'toe': 'Value'}).values('toe')
                        qry_desig = EmployeeDropdown.objects.filter(sno=res['designation']).extra(select={'desig': 'Value'}).values('desig')
                        qry_leave_type = LeaveType.objects.filter(id=res['leave_id']).extra(select={'leave_name': 'Leave_Name'}).values('leave_name')

                        prev_quota_data.append({'leave_name': qry_leave_type[0]['leave_name'], 'categ_emp': qry_coe[0]['coe'], 'type_of_emp': qry_toe[0]['toe'], 'designation': qry_desig[0]['desig'], 'leave_quota_id': res['leave_quota_id'], 'num_of_leaves': res['num_of_leaves']})

                    msg = "Success"
                    status = 200
                else:
                    status = 403
                    msg = "Not Authorized"
            else:
                status = 401
                msg = "Authentication failed"
        else:
            status = 500
            msg = "Technical Error : Wrong Parameters"

    data = {'data_d': prev_quota_data, 'status': status, 'msg': msg}

    return JsonResponse(data, safe=False)


def Leave_Insert(request):
    status = 401
    msg = ""
    if request.META:
        if 'HTTP_COOKIE' in request.META:

            if request.user.is_authenticated:
                check = checkpermission(request, [211, 337])
                if(check == 200):

                    if request.method == 'POST':
                        data = json.loads(request.body)
                        if data['typeofemp'] == "0001":  # in case of all type of emp
                            leave_quota_values_insert = {'no_of_leaves': data['noofleaves'], 'leave_id': LeaveType.objects.get(id=data['ltype']), 'inserted_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])}

                            qry_toe = EmployeeDropdown.objects.filter(field='TYPE OF EMPLOYMENT').values('sno').exclude(value__isnull=True)
                            for k in qry_toe:
                                leave_quota_values_insert['type_of_emp'] = EmployeeDropdown.objects.get(sno=k['sno'])
                                qry_coe = EmployeeDropdown.objects.filter(field='CATEGORY OF EMPLOYEE').values('sno').exclude(value__isnull=True)
                                for i in qry_coe:
                                    leave_quota_values_insert['category_emp'] = EmployeeDropdown.objects.get(sno=i['sno'])
                                    qr = EmployeeDropdown.objects.filter(pid=i['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                    qry1 = EmployeeDropdown.objects.filter(pid__in=qr, value="DESIGNATION").exclude(value__isnull=True).values('sno')
                                    for j in qry1:
                                        qrya = EmployeeDropdown.objects.filter(pid=j['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                        qryc = EmployeeDropdown.objects.filter(pid__in=qrya).exclude(value__isnull=True).values('sno')

                                        flag = 0
                                        for u in qryc:

                                            qry_check_duplicate = LeaveQuota.objects.filter(designation=u['sno'], category_emp=i['sno'], type_of_emp=k['sno'], leave_id=data['ltype'], status='INSERT').values('id')
                                            if len(qry_check_duplicate) > 0:
                                                flag = 1
                                                break

                                        if flag == 1:
                                            break

                                    if flag == 1:
                                        break

                                if flag == 1:
                                    break

                            if flag == 0:
                                leave_quota_values_insert = {'no_of_leaves': data['noofleaves'], 'leave_id': LeaveType.objects.get(id=data['ltype']), 'inserted_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])}
                                for k in qry_toe:
                                    leave_quota_values_insert['type_of_emp'] = EmployeeDropdown.objects.get(sno=k['sno'])
                                    qry_coe = EmployeeDropdown.objects.filter(field='CATEGORY OF EMPLOYEE').values('sno').exclude(value__isnull=True)
                                    for i in qry_coe:
                                        leave_quota_values_insert['category_emp'] = EmployeeDropdown.objects.get(sno=i['sno'])
                                        qr = EmployeeDropdown.objects.filter(pid=i['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)
                                        qry1 = EmployeeDropdown.objects.filter(pid__in=qr, value="DESIGNATION").exclude(value__isnull=True).values('sno')
                                        for j in qry1:
                                            qrya = EmployeeDropdown.objects.filter(pid=j['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                            qryc = EmployeeDropdown.objects.filter(pid__in=qrya).exclude(value__isnull=True).values('sno')

                                            flag = 0
                                            for u in qryc:
                                                leave_quota_values_insert['designation'] = EmployeeDropdown.objects.get(sno=u['sno'])
                                                qry5 = LeaveQuota.objects.create(**leave_quota_values_insert)

                                msg = "LEAVE QUOTA SUCCESFULLY ADDED!!"
                                status = 200
                            else:
                                msg = "Duplicate Entries!!"
                                status = 409

                        else:

                            if data['coemp'] == "0001":  # in case of all categ of emp

                                leave_quota_values_insert = {'no_of_leaves': data['noofleaves'], 'leave_id': LeaveType.objects.get(id=data['ltype']), 'inserted_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])}

                                leave_quota_values_insert['type_of_emp'] = EmployeeDropdown.objects.get(sno=data['typeofemp'])
                                qry_coe = EmployeeDropdown.objects.filter(field='CATEGORY OF EMPLOYEE').values('sno').exclude(value__isnull=True)

                                for i in qry_coe:

                                    leave_quota_values_insert['category_emp'] = EmployeeDropdown.objects.get(sno=i['sno'])
                                    qr = EmployeeDropdown.objects.filter(pid=i['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                    qry1 = EmployeeDropdown.objects.filter(pid__in=qr, value="DESIGNATION").exclude(value__isnull=True).values('sno')

                                    for j in qry1:

                                        qrya = EmployeeDropdown.objects.filter(pid=j['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                        qryc = EmployeeDropdown.objects.filter(pid__in=qrya).exclude(value__isnull=True).values('sno')

                                        flag = 0
                                        for u in qryc:

                                            qry_check_duplicate = LeaveQuota.objects.filter(designation=u['sno'], category_emp=i['sno'], type_of_emp=data['typeofemp'], leave_id=data['ltype'], status='INSERT').values('id')
                                            if len(qry_check_duplicate) > 0:
                                                flag = 1
                                                break

                                        if flag == 1:
                                            break

                                    if flag == 1:
                                        break

                                if flag == 0:
                                    leave_quota_values_insert = {'no_of_leaves': data['noofleaves'], 'leave_id': LeaveType.objects.get(id=data['ltype']), 'inserted_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])}
                                    leave_quota_values_insert['type_of_emp'] = EmployeeDropdown.objects.get(sno=data['typeofemp'])

                                    for i in qry_coe:

                                        leave_quota_values_insert['category_emp'] = EmployeeDropdown.objects.get(sno=i['sno'])
                                        qr = EmployeeDropdown.objects.filter(pid=i['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                        qry1 = EmployeeDropdown.objects.filter(pid__in=qr, value="DESIGNATION").exclude(value__isnull=True).values('sno')

                                        for j in qry1:

                                            qrya = EmployeeDropdown.objects.filter(pid=j['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                            qryc = EmployeeDropdown.objects.filter(pid__in=qrya).exclude(value__isnull=True).values('sno')

                                            flag = 0
                                            for u in qryc:
                                                leave_quota_values_insert['designation'] = EmployeeDropdown.objects.get(sno=u['sno'])
                                                qry5 = LeaveQuota.objects.create(**leave_quota_values_insert)

                                    msg = "LEAVE QUOTA SUCCESFULLY ADDED!!"
                                    status = 200
                                else:
                                    msg = "Duplicate Entries!!"
                                    status = 409

                            else:
                                if data['desg'][0] == "0001":  # in case of all designation

                                    leave_quota_values_insert = {'no_of_leaves': data['noofleaves'], 'leave_id': LeaveType.objects.get(id=data['ltype']), 'inserted_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])}
                                    # leave_quota_values_insert['type_of_emp']=data['typeofemp']
                                    # leave_quota_values_insert['category_emp']=data['coemp']

                                    leave_quota_values_insert['type_of_emp'] = EmployeeDropdown.objects.get(sno=data['typeofemp'])
                                    leave_quota_values_insert['category_emp'] = EmployeeDropdown.objects.get(sno=data['coemp'])

                                    qry = EmployeeDropdown.objects.filter(pid=data['coemp']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                    qry1 = EmployeeDropdown.objects.filter(pid__in=qry, value="DESIGNATION").exclude(value__isnull=True).values('sno')

                                    for j in qry1:

                                        qrya = EmployeeDropdown.objects.filter(pid=j['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                        qryc = EmployeeDropdown.objects.filter(pid__in=qrya).exclude(value__isnull=True).values('sno')

                                        flag = 0
                                        for u in qryc:

                                            qry_check_duplicate = LeaveQuota.objects.filter(designation=u['sno'], category_emp=data['coemp'], type_of_emp=data['typeofemp'], leave_id=data['ltype'], status='INSERT').values('id')
                                            if len(qry_check_duplicate) > 0:
                                                flag = 1
                                                break

                                        if flag == 1:
                                            break

                                    if flag == 0:
                                        for j in qry1:

                                            qrya = EmployeeDropdown.objects.filter(pid=j['sno']).extra(select={'sno': 'pid'}).values('pid').exclude(value__isnull=True)

                                            qryc = EmployeeDropdown.objects.filter(pid__in=qrya).exclude(value__isnull=True).values('sno')

                                            flag = 0
                                            for u in qryc:
                                                leave_quota_values_insert['designation'] = EmployeeDropdown.objects.get(sno=u['sno'])
                                                qry5 = LeaveQuota.objects.create(**leave_quota_values_insert)

                                        msg = "LEAVE QUOTA SUCCESFULLY ADDED!!"
                                        status = 200
                                    else:
                                        msg = "Duplicate Entries!!"
                                        status = 409

                                else:

                                    L_Type = LeaveType.objects.get(id=data['ltype'])
                                    Ty_Of_Emp = EmployeeDropdown.objects.get(sno=data['typeofemp'])
                                    Coe_Emp = EmployeeDropdown.objects.get(sno=data['coemp'])
                                    Desg = data['desg']
                                    Noof_Leaves = data['noofleaves']

                                    flag = 0
                                    for i in Desg:

                                        qry_check_duplicate = LeaveQuota.objects.filter(designation=i, category_emp=data['coemp'], type_of_emp=data['typeofemp'], leave_id=data['ltype'], status='INSERT').values('id')
                                        if len(qry_check_duplicate) > 0:
                                            flag = 1
                                            break

                                    if flag == 0:
                                        for i in Desg:
                                            qry5 = LeaveQuota.objects.create(leave_id=L_Type, type_of_emp=Ty_Of_Emp, category_emp=Coe_Emp, inserted_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), designation=EmployeeDropdown.objects.get(sno=i), no_of_leaves=Noof_Leaves)
                                        msg = "LEAVE QUOTA SUCCESFULLY ADDED!!"
                                        status = 200
                                    else:
                                        msg = "Duplicate Entries!!"
                                        status = 409
                    else:
                        status = 502
                        msg = "INVALID METHOD"

                else:
                    status = 403
                    msg = "Not Authorized"
            else:
                status = 401
                msg = "Authentication failed"
        else:
            status = 500
            msg = "Technical Error : Wrong Parameters"
    else:
        msg = "Invalid Request.."

    data = {'msg': msg}
    return JsonResponse(data=data, status=status)


def on_load(request):
    error = True
    info = ""
    qry = ""
    qry_b = ""
    if request.META:
        if 'HTTP_COOKIE' in request.META:

            if request.user.is_authenticated:
                if request.session['hash3'] == 'Employee' and 'HR' in request.session['roles']:

                    qry = NoDuesEmp.objects.extra(select={'idEmp': 'emp_id', 'Status': 'status'}).values('idEmp', 'Status')
                    qry_a = NoDuesEmp.objects.extra(select={'idEmp': 'emp_id'}).values('idEmp')
                    qry_b = EmployeePrimdetail.objects.filter(emp_id__in=qry_a.values('idEmp')).extra(select={'name': 'name', 'id': 'emp_id'}).values('name', 'id')
                    error = False
                    msg = "Status successfully updated!"
                else:
                    msg = "Not Logged In!!"
            else:
                msg = "Authentification Failed!"
        else:
            msg = "Wrong Parameters!!"
    else:
        msg = "Invalid Request.."
    info = {'info': list(qry), 'name': list(qry_b), 'error': error, 'msg': msg}
    return JsonResponse(info, safe=False)


def change_status(request):
    error = True
    data = ""
    msg = ""

    if(request.body):
        data = json.loads(request.body)
        emp_id = data['emp_id']
        status = data['status']
        update = {'status': status}
        qry = NoDuesEmp.objects.filter(emp_id=emp_id).update(status=status)

    return JsonResponse("updated", safe=False)


def Seperation_Table_View(request):
    error = True
    msg = ""
    if request.META:
        if 'HTTP_COOKIE' in request.META:

            if request.user.is_authenticated:

                if request.session['hash3'] == 'Employee' and 'HOD' in request.session['roles']:

                    qry1 = EmployeeSeparation.objects.filter(hod_status='PENDING', hr_status='PENDING').extra(select={'id': 'id', 'empid': 'emp_id', 'status': 'status', 'type': 'type', 'rejoindate': 'rejoin_date', 'empremark': 'emp_remark'}).values('id', 'emp_id', 'status', 'type', 'rejoindate', 'empremark')

                    Data = {'toe': list(qry1)}
                    msg = "Data Sent HOD panel...!!"
                    error = False

                elif request.session['hash3'] == 'Employee' and 'HR' in request.session['roles']:

                    qry1 = EmployeeSeparation.objects.filter(hod_status='APPROVED', hr_status='PENDING').exclude(emp_id__isnull=True).extra(select={'id': 'id', 'empid': 'emp_id', 'status': 'status', 'type': 'type', 'rejoindate': 'rejoin_date', 'empremark': 'emp_remark'}).values('id', 'emp_id', 'status', 'type', 'rejoindate', 'empremark')

                    data = {'toe': list(qry1)}
                    msg = "Data Sent to HR panel..!!"
                    error = False

                else:
                    msg = "Not Logged In!!"
            else:
                msg = "Authentification Failed!"
        else:
            msg = "Wrong Parameters!!"
    else:
        msg = "Invalid Request.."
    data = {'data': data, 'msg': msg, 'error': error}
    return JsonResponse(data, safe=False)


def Seperation_Change_status(request):
    error = True
    msg = ""
    if request.META:
        if 'HTTP_COOKIE' in request.META:

            if request.user.is_authenticated:
                if request.session['hash3'] == 'Employee' and 'HOD' in request.session['roles']:
                    data = json.loads(request.body.decode('utf-8'))
                    Status = data['stat']
                    Id = int(data['row_id'])
                    Hod_Remark = data['hodremark']
                    upd_list = {'hod_status': status, 'hr_status': 'PENDING', 'hod_remark': Hod_Remark}
                    sav = EmployeeSeparation.objects.filter(id=Id, hod_status='PENDING', hr_status='PENDING').update(**upd_list)
                    if sav:
                        data = {'msg': 'Update Successful'}
                    else:
                        data = {'msg': 'Update Failed'}
                    error = False
                elif request.session['hash3'] == 'Employee' and 'HR' in request.session['roles']:
                    data = json.loads(request.body.decode('utf-8'))
                    Status = data['stat']
                    Id = int(data['row_id'])
                    Hr_Remark = data['hodremark']
                    upd_list = {'hr_status': Status, 'hr_remark': Hr_Remark}
                    sav = EmployeeSeparation.objects.filter(id=Id, hod_status='APPROVED', hr_status='PENDING').update(**upd_list)
                    if sav:
                        data = {'msg': 'Update Successful'}
                    else:
                        data = {'msg': 'Update Failed'}
                    error = False

                else:
                    msg = "Not Logged In!!"

            else:
                msg = "Authentification Failed!"
        else:
            msg = "Wrong Parameters!!"
    else:
        msg = "Invalid Request.."
    data = {'msg': msg, 'error': error}
    return JsonResponse(data, safe=False)


def od_leave(request):
    error = True
    msg = ""
    status = ""
    data = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'OdValues':
                        qry_a = EmployeeDropdown.objects.filter(field="OD CATEGORY").exclude(value__isnull=True).extra(select={'val': 'value', 'id': 'sno'}).values('val', 'id')
                        error = False
                        msg = "Success"
                        status = 200
                        data = {'display_values': list(qry_a), 'error': error, 'msg': msg}

                    if request.GET['request_type'] == 'GetSubCatFromCat':
                        cat = request.GET['Cat']
                        QryA = EmployeeDropdown.objects.filter(pid=cat).exclude(value__isnull=True).extra(select={'val': 'value', 'id': 'sno'}).values('val', 'id')
                        data_send = []
                        for i in QryA:
                            qry_upload_check = OdCategoryUpload.objects.filter(category=cat, sub_category=i['id']).values()
                            if len(qry_upload_check) > 0:
                                co = "NO"
                                up = "NO"
                                if qry_upload_check[0]['is_compoff'] == 1:
                                    co = "YES"
                                if qry_upload_check[0]['is_upload'] == 1:
                                    up = "YES"

                                data_send.append({'val': i['val'], 'id': i['id'], 'upload': up, 'compoff': co, 'num_of_days': qry_upload_check[0]['num_of_days']})
                            else:
                                data_send.append({'val': i['val'], 'id': i['id'], 'upload': 'NO', 'compoff': 'NO', 'num_of_days': 0})

                        error = False
                        msg = "Success"
                        status = 200
                        data = {'display_values': data_send, 'error': error, 'msg': msg}

                    if request.GET['request_type'] == 'OdLeaveCheckForUpload':
                        data = {}
                        SubCat = request.GET['SubCat']
                        Cat = request.GET['Cat']
                        QryCheck = OdCategoryUpload.objects.filter(category=Cat, sub_category=SubCat).values('upload')
                        if QryCheck.count() > 0:
                            data['flag'] = QryCheck[0]['upload']
                            msg = "Success"
                            error = False
                        else:
                            msg = "No record of this category"
                            error = False
                        status = 200

                if request.method == "POST":
                    if request.GET['request_type'] == "OdLeaveInsert":
                        data = ''
                        fields_to_be_inserted = json.loads(request.body)
                        FromDate = parse_date(fields_to_be_inserted['f_date'])
                        ToDate = parse_date(fields_to_be_inserted['t_date'])
                        RequestDate = datetime.now()  # fields_to_be_inserted['RequestDate']
                        Category = fields_to_be_inserted['cat']
                        SubType = fields_to_be_inserted['sub_cat']
                        Emp_Id = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
                        FHalf = fields_to_be_inserted['half1']
                        THalf = fields_to_be_inserted['half2']
                        Days = fields_to_be_inserted['Days']
                        Reason = fields_to_be_inserted['Reason']

                        QryGetLEaveId = Leaves.objects.filter(requestdate=RequestDate, leavecode=2, category=Category, subtype=SubType, fromdate=FromDate, todate=ToDate, days=Days, emp_id=Emp_Id, fhalf=FHalf, thalf=THalf, finalstatus="PENDING")
                        if QryGetLEaveId.count() > 0:
                            msg = "Leave already applied"
                        else:
                            qry3 = Attendance2.objects.filter(Emp_Id=Emp_Id).filter(date__range=[FromDate, ToDate]).values('date')
                            if(qry3.count() > 0):
                                msg = 'Your Attendence has been marked for the dates you are applying leave for.. '
                                error = False
                            else:
                                qry1 = Leaves.objects.create(requestdate=RequestDate, leavecode=LeaveType.objects.get(id=2), fromdate=FromDate, todate=ToDate, days=Days, reason=Reason, emp_id=Emp_Id, fhalf=FHalf, thalf=THalf, finalstatus="PENDING")
                                QryGetLEaveId = Leaves.objects.filter(requestdate=RequestDate, leavecode=2, fromdate=FromDate, todate=ToDate, days=Days, reason=Reason, emp_id=Emp_Id, fhalf=FHalf, thalf=THalf, finalstatus="PENDING").values('leaveid')
                                LeaveId = QryGetLEaveId[0]['leaveid']
                                qry2 = Reporting.objects.filter(emp_id=request.session['hash1']).values('reporting_to', 'reporting_no', 'department')
                                qryRep = Reporting.objects.filter(emp_id=Emp_Id).values('reporting_to', 'reporting_no', 'department_id')
                                min_num = 1
                                MinRepObj = {}
                                for a in qryRep:
                                    if a['reporting_no'] <= min_num:
                                        MinRepObj = a

                                QryInsertApproval = Leaveapproval.objects.create(leaveid=Leaves.objects.get(leaveid=LeaveId), approved_by=request.session['hash1'], status="PENDING", reportinglevel=MinRepObj['reporting_no'], dept=EmployeeDropdown.objects.get(sno=MinRepObj['department_id']), desg=EmployeeDropdown.objects.get(sno=MinRepObj['reporting_to']))
                                msg = 'Your leave has been applied.'
                        error = False
                        status = 200
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"
    else:
        msg = "Technical error : wrong parameters"

    return JsonResponse(data={'msg': msg, 'data': data}, status=status)


def leaves(request):
    error = True

    qry_a = EmployeeDropdown.objects.filter(field="DAY TYPE").extra(select={'v': 'value', 's': 'sno'}).values('v', 's')
    qry_b = Attendance2.objects.extra(select={'e': 'extra'}).values('e')
    qry_c = Leaves.objects.extra(select={'e': 'extrahours'}).values('e')
    qry_d = Leaves.objects.extra(select={'e': 'extraworkdate'}).values('e')
    qry_e = Leaves.objects.extra(select={'e': 'fromdate'}).values('e')
    qry_f = Leaveapproval.objects.extra(select={'e': 'remark'}).values('e')
    qry_g = Leaves.objects.extra(select={'e': 'finalstatus'}).values('e')
    qry_h = Leaves.objects.extra(select={'e': 'finalapprovaldate'}).values('e')
    qry_i = Leaves.objects.extra(select={'e': 'cancelrequest'}).values('e')
    qry_j = Leaves.objects.extra(select={'e': 'days'}).values('e')
    qry_k = Attendance2.objects.extra(select={'e': 'date'}).values('e')

    error = False
    msg = ""

    data_to_be_sent = {'data_d': {'DayType': list(qry_a), 'Extra': list(qry_b), 'NumberExtraHours': list(qry_c), 'DateExtraHours': list(qry_d), 'FromDate': list(qry_e), 'remark': list(qry_f), 'finalstatus': list(qry_g), 'FinalApproval': list(qry_h), 'CancelRequest': list(qry_i), 'days': list(qry_j), 'Date': list(qry_k)}, 'error': error, 'msg': msg}
    return JsonResponse(data_to_be_sent, safe=False)


def checkhourlyvalid(emp_id, leave_id, date, status):
    # qry3=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('shift','dept') #get shift of employee

    qry_att = Attendance2.objects.filter(Emp_Id=emp_id, date=date).values('intime', 'outtime', 'shift_id')
    qry4 = Shifts.objects.filter(id=qry_att[0]['shift_id']).values()

    qry_leave = LeaveType.objects.filter(id=leave_id).values('hours')
    sec_hourleave = qry_leave[0]['hours'].hour * 3600 + qry_leave[0]['hours'].minute * 60 + qry_leave[0]['hours'].second
    delta_hourleave = datetime.timedelta(seconds=sec_hourleave)

    sec2 = qry4[0]['halfdaytime'].hour * 3600 + qry4[0]['halfdaytime'].minute * 60 + qry4[0]['halfdaytime'].second
    delta = datetime.timedelta(seconds=sec2)
    shifthaltime = (datetime.datetime.combine(datetime.date(1, 1, 1), qry4[0]['intime']) + delta).time()  # calculate half day time according to shifts

    date_check = datetime.datetime.strptime(str("2018-06-30"), "%Y-%m-%d").date()
    response = [0, ]
    if(status == 'P/II'):
        ###do not change this ,in case of any confusion contact salil#######
        date_check2 = datetime.datetime.strptime(str("2019-05-29"), "%Y-%m-%d").date()
        if date <= date_check2:
            diffsec = ((datetime.datetime.combine(datetime.date.today(), qry_att[0]['outtime']) - datetime.datetime.combine(datetime.date.today(), qry_att[0]['intime'])).total_seconds())
        else:
            diffsec = ((min(datetime.datetime.combine(datetime.date.today(), qry_att[0]['outtime']), (datetime.datetime.combine(datetime.date.today(), qry4[0]['outtime']))) - max(datetime.datetime.combine(datetime.date.today(), qry_att[0]['intime']), (datetime.datetime.combine(datetime.date.today(), qry4[0]['intime'])))).total_seconds())

        difftime = datetime.timedelta(seconds=diffsec)
        work_hour = (datetime.datetime.min + difftime).time()
        totalworkhour = (datetime.datetime.combine(datetime.date(1, 1, 1), work_hour) + delta_hourleave).time()
        if(totalworkhour >= qry4[0]['fulldaytime']):
            response = 2
        else:
            response = 3

    elif(status == 'P/I'):
        ###do not change this ,in case of any confusion contact salil#######

        date_check2 = datetime.datetime.strptime(str("2019-05-29"), "%Y-%m-%d").date()
        if date <= date_check2:
            diffsec = ((datetime.datetime.combine(datetime.date.today(), qry_att[0]['outtime']) - datetime.datetime.combine(datetime.date.today(), qry_att[0]['intime'])).total_seconds())
        else:
            ###### BUG SOLVED ######01/07/2019 : added this if condition in case of flexible shift or any shift with 0,0,0 outtime#####
            if qry4[0]['outtime'] != datetime.datetime(1, 1, 1, 0, 0).time():
                diffsec = ((min(datetime.datetime.combine(datetime.date.today(), qry_att[0]['outtime']), (datetime.datetime.combine(datetime.date.today(), qry4[0]['outtime']))) - max(datetime.datetime.combine(datetime.date.today(), qry_att[0]['intime']), (datetime.datetime.combine(datetime.date.today(), qry4[0]['intime'])))).total_seconds())

            else:
                diffsec = ((datetime.datetime.combine(datetime.date.today(), qry_att[0]['outtime'])) - max(datetime.datetime.combine(datetime.date.today(), qry_att[0]['intime']), (datetime.datetime.combine(datetime.date.today(), qry4[0]['intime'])))).total_seconds()
            ########End##############
        difftime = datetime.timedelta(seconds=diffsec)
        # print("datetime.datetime.min",datetime.datetime.min,"difftime",difftime,"date_check2",date_check2,"qry_att[0]",qry_att[0],"diffsec",diffsec,"emp_id",emp_id)
        work_hour = (datetime.datetime.min + difftime).time()
        totalworkhour = (datetime.datetime.combine(datetime.date(1, 1, 1), work_hour) + delta_hourleave).time()

        if(totalworkhour >= qry4[0]['fulldaytime']):

            response = 2
        else:
            response = 3

    elif(status == 'A' or status == 'P/A' or status == 'H'):
        if(qry_leave[0]['hours'] >= qry4[0]['halfdaytime']):
            response = 2
        else:
            response = 3

    elif(status == 'P' and date > date_check):
        response = 2
    # print(response)
    return response


def date_format(date):
    return datetime.datetime.strptime(str(date), "%Y-%m-%d").strftime("%d-%m-%Y")


def dayssummay(pmail, fdate, tdate, typ):

    p = 0
    a = 0
    l = 0
    l_nc = 0

    present_data = []
    absent_data = []
    leave_data = []
    leave_nc_data = []

    fdate = datetime.datetime.strptime(str(fdate), '%Y-%m-%d').date()
    tdate = datetime.datetime.strptime(str(tdate), '%Y-%m-%d').date()

    day = datetime.timedelta(days=1)
    date = fdate

    dept = EmployeePrimdetail.objects.filter(emp_id=pmail).values('dept')
    while date <= tdate:

        ####### get attendance status of employees on working days (i.e except holidays) ######

        qry = Attendance2.objects.filter(Emp_Id=pmail, date=date).exclude(status='H').values()
        if len(qry) > 0:
            if (qry[0]['status'] == 'P'):

                ######### if status is 'P' i.e. employee is present, simply append to present data and increase present count ####
                p = p + 1
                present_data.append({'date': date_format(date), 'status': qry[0]['status'], 'count': '1', 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

            elif(qry[0]['status'] == 'A'):
                response = check_leave_status(pmail, date, qry[0]['status'])
                ######### if status is 'A' i.e. employee is absent, check for leave applied on that particular date ######

                if(response[0] == 2):

                    ###### if response[0]=2, it means leave is applied for half day. Append the remaining half to absent data and increase absent count  ###############

                    a = a + 0.5
                    absent_data.append({'date': date_format(date), 'count': '0.5', 'status': qry[0]['status'], 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

                    if response[2] == 'Y':

                        ########### response[2]='Y' means leave is countable i.e it is payable. Add to leave data and increase leave count #########

                        l = l + 0.5
                        leave_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                    else:

                        ########### response[2]='N' means leave is non-countable i.e it is not payable (leave without pay). Add to leave non-countable data and increase leave non-countable count #########

                        l_nc += 0.5
                        leave_nc_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1]})

                elif(response[0] == 1):

                    ###### if response[0]=1, it means leave is applied for full day ###############

                    if response[2] == 'Y':

                        ########### response[2]='Y' means leave is countable i.e it is payable. Add to leave data and increase leave count #########

                        l = l + 1
                        leave_data.append({'date': date_format(date), 'count': '1', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                    elif response[2] == 'N':

                        ########### response[2]='N' means leave is non-countable i.e it is not payable (leave without pay). Add to leave non-countable data and increase leave non-countable count #########

                        l_nc += 1
                        leave_nc_data.append({'date': date_format(date), 'count': '1', 'leave': response[1]})
                    else:
                        l = l + 0.5
                        l_nc += 0.5
                        leave_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                        leave_nc_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1]})

                elif(response[0] == 3):

                    ###### if response[0]=1, it means no leave is applied. Append to absent data and increase absebt count ###############

                    a = a + 1
                    absent_data.append({'date': date_format(date), 'count': '1', 'status': qry[0]['status'], 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

            elif (qry[0]['status'] == 'P/I'):

                ######### if status is 'P/I' i.e. employee is present in first half and absent in second half, append Ist half present data and increase present count by 0.5 and check for leave in second half ####

                response = check_leave_status(pmail, date, 'P/I')
                if(response[0] != 0 and response[0] != 3):
                    p = p + 0.5
                    present_data.append({'date': date_format(date), 'status': qry[0]['status'], 'count': '0.5', 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

                    if response[2] == 'Y':
                        l = l + 0.5
                        leave_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                    else:
                        l_nc += 0.5
                        leave_nc_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1]})

                else:
                    a = a + 0.5
                    p = p + 0.5

                    absent_data.append({'date': date_format(date), 'count': '0.5', 'status': qry[0]['status'], 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})
                    present_data.append({'date': date_format(date), 'status': qry[0]['status'], 'count': '0.5', 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

            elif (qry[0]['status'] == 'P/II'):

                ######### if status is 'P/II' i.e. employee is present in second half and absent in first half, append IInd half present data and increase present count by 0.5 and check for leave in first half ####

                response = check_leave_status(pmail, date, 'P/II')
                if(response[0] != 0 and response[0] != 3):
                    p = p + 0.5
                    present_data.append({'date': date_format(date), 'status': qry[0]['status'], 'count': '0.5', 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

                    if response[2] == 'Y':
                        l = l + 0.5
                        leave_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                    else:
                        l_nc += 0.5
                        leave_nc_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1]})
                else:
                    a = a + 0.5
                    p = p + 0.5

                    absent_data.append({'date': date_format(date), 'count': '0.5', 'status': qry[0]['status'], 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})
                    present_data.append({'date': date_format(date), 'status': qry[0]['status'], 'count': '0.5', 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

            elif(qry[0]['status'] == 'P/A'):

                ######### if status is 'P/A' i.e. only 1st punch is recorded (employee exits without making punch). 'P/A' is considered equivalent to 'A' ####

                response = check_leave_status(pmail, date, 'A')
                if(response[0] == 2):
                    a = a + 0.5
                    absent_data.append({'date': date_format(date), 'count': '0.5', 'status': qry[0]['status'], 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

                    if response[2] == 'Y':
                        l = l + 0.5

                        leave_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                    elif response[2] == 'N':
                        l_nc += 0.5
                        leave_nc_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1]})

                elif(response[0] == 1):
                    if response[2] == 'Y':
                        l = l + 1
                        leave_data.append({'date': date_format(date), 'count': '1', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                    elif response[2] == 'N':
                        l_nc += 1
                        leave_nc_data.append({'date': date_format(date), 'count': '1', 'leave': response[1]})
                    else:
                        l = l + 0.5
                        l_nc += 0.5
                        leave_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                        leave_nc_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1]})
                elif(response[0] == 3):
                    a = a + 1
                    absent_data.append({'date': date_format(date), 'count': '1', 'status': qry[0]['status'], 'intime': qry[0]['intime'], 'outtime': qry[0]['outtime']})

        else:

            ############ case when leave is applied of date greater than today date & holiday is not there ##############

            qry_check_holi = Holiday.objects.filter(f_date__lte=date, t_date__gte=date, dept=dept[0]['dept'], status="INSERT").values('restricted')
            if len(qry_check_holi) == 0:
                response = check_leave_status(pmail, date, 'A')
                if response[0] == 1:
                    if response[2] == 'Y':
                        l += 1
                        leave_data.append({'date': date_format(date), 'count': '1', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                    elif response[2] == 'N':
                        l_nc += 1
                        leave_nc_data.append({'date': date_format(date), 'count': '1', 'leave': response[1]})
                    else:
                        l = l + 0.5
                        l_nc += response[5]
                        leave_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                        leave_nc_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1]})

                elif response[0] == 2:
                    if response[2] == 'Y':
                        l = l + 0.5

                        leave_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1], 'category':response[6]['category'], 'subtype':response[6]['subtype']})
                    elif response[2] == 'N':
                        l_nc += 0.5
                        leave_nc_data.append({'date': date_format(date), 'count': '0.5', 'leave': response[1]})

        date += day

    data = {'present': p, 'absent': a, 'leave': l, 'leave_nc': l_nc, 'absent_data': absent_data, 'leave_data': leave_data, 'present_data': present_data, 'leave_nc_data': leave_nc_data}
    return data


def check_leave_status(pmail, date, status):
    response = [0, '', 'Y', '{}', '{}', 0, '{}']

    # response[0] =1 (full leave),2(half leave),3(absent)
    # response[1] gives leave abbreviation
    # response[2] gives whether leave is countable or not
    # response[3] gives leave data
    # response[4] gives non count leave data
    # response[5] gives count of non count leave
    # response[6] gives category__value & subtype__value

    qry = Leaves.objects.filter(emp_id=pmail, fromdate__lte=date, todate__gte=date, finalstatus__contains="APPROVED").values('category__value','subtype__value','leaveid', 'leavecode__leave_abbr', 'fhalf', 'thalf', 'fromdate', 'todate', 'leavecode', 'leavecode__leaveCountStatus')   
    ############ check for leave on given date #####################

    if(qry.count() > 0):
        response[6] =  {'category':qry[0]['category__value'],'subtype':qry[0]['subtype__value']}
    
        if len(qry) == 2:

            ########### case when 2 leaves are applied for same day (i.e leave of 2 halves one of first half and other of second half) #####################

            response[0] = 1

            if qry[0]['leavecode__leaveCountStatus'] == 'Y' and qry[1]['leavecode__leaveCountStatus'] == 'Y':
                response[1] = qry[0]['leavecode__leave_abbr'] + "/" + qry[1]['leavecode__leave_abbr']
                response[2] = 'Y'
                response[3] = {'date': date, 'leave': response[1], 'count': '1'}

            elif qry[0]['leavecode__leaveCountStatus'] != 'Y' and qry[1]['leavecode__leaveCountStatus'] != 'Y':
                response[0] = 3
            elif qry[0]['leavecode__leaveCountStatus'] == 'Y' and qyr[1]['leavecode__leaveCountStatus'] != 'Y':
                response[1] = qry[0]['leavecode__leave_abbr']
                response[2] = 'Y/N'
                response[3] = {'date': date, 'leave': response[1], 'count': '0.5'}
                response[4] = {'date': date, 'leave': qry[1]['leavecode__leave_abbr'], 'count': '0.5'}
                response[5] = 0.5
            else:
                response[1] = qry[1]['leavecode__leave_abbr']
                response[2] = 'N/Y'
                response[3] = {'date': date, 'leave': response[1], 'count': '0.5'}
                response[4] = {'date': date, 'leave': qry[0]['leavecode__leave_abbr'], 'count': '0.5'}
                response[5] = 0.5

        else:

            # case when only one leave is applied for given date. It could be for full day or of either 2 halves

            ################ if date to be check is the fromdate of leave applied (separate case coz it could be full day or half) ######

            if str(date) == qry[0]['fromdate'].strftime('%Y-%m-%d'):

                # check whether the leave applied is hourly type or not ##########3

                if not fun_leave_hourly(qry[0]['leavecode'], qry[0]['fromdate'], qry[0]['todate'], qry[0]['fhalf'], qry[0]['thalf']):
                    if qry[0]['fhalf'] == '0':
                        response[0] = 1
                        response[1] = qry[0]['leavecode__leave_abbr']

                        if qry[0]['leavecode__leaveCountStatus'] == 'Y':
                            response[2] = 'Y'
                            response[3] = {'date': date, 'leave': response[1], 'count': '1'}
                        else:
                            response[2] = 'N'
                            response[4] = {'date': date, 'leave': response[1], 'count': '1'}
                            response[5] = 1
                    else:
                        response[0] = 2
                        response[1] = qry[0]['leavecode__leave_abbr']

                        if qry[0]['leavecode__leaveCountStatus'] == 'Y':
                            response[2] = 'Y'
                            response[3] = {'date': date, 'leave': response[1], 'count': '0.5'}
                        else:
                            response[2] = 'N'
                            response[4] = {'date': date, 'leave': response[1], 'count': '0.5'}
                            response[5] = 0.5

                else:
                    response[1] = qry[0]['leavecode__leave_abbr']
                    res_func = checkhourlyvalid(pmail, qry[0]['leavecode'], date, status)

                    # if hourly, check its validity (e.g SHL is hourly leave which adds 1:30 hours to the working time. If adding 1:30 hrs, working time gets greater than or equal to required full day wokring time, leave is counted i.e response[0]=2 else it will be ignored i.e response[0]=3) #####################3

                    response[0] = res_func
                    if response[0] == 2:
                        if qry[0]['leavecode__leaveCountStatus'] == 'Y':
                            response[2] = 'Y'
                            response[3] = {'date': date, 'leave': response[1], 'count': '0.5'}
                        else:
                            response[2] = 'N'
                            response[4] = {'date': date, 'leave': response[1], 'count': '0.5'}
                            response[5] = 0.5

            ################ if date to be check is the todate of leave applied (separate case coz it could be full day or half) ######

            elif str(date) == qry[0]['todate'].strftime('%Y-%m-%d'):

                # check whether the leave applied is hourly type or not ##########3

                if not fun_leave_hourly(qry[0]['leavecode'], qry[0]['fromdate'], qry[0]['todate'], qry[0]['fhalf'], qry[0]['thalf']):
                    if qry[0]['thalf'] == '0':
                        response[0] = 1
                        response[1] = qry[0]['leavecode__leave_abbr']

                        if qry[0]['leavecode__leaveCountStatus'] == 'Y':
                            response[2] = 'Y'
                            response[3] = {'date': date, 'leave': response[1], 'count': '1'}
                        else:
                            response[2] = 'N'
                            response[4] = {'date': date, 'leave': response[1], 'count': '1'}
                            response[5] = 1
                    else:
                        response[0] = 2
                        response[1] = qry[0]['leavecode__leave_abbr']

                        if qry[0]['leavecode__leaveCountStatus'] == 'Y':
                            response[2] = 'Y'
                            response[3] = {'date': date, 'leave': response[1], 'count': '0.5'}
                        else:
                            response[2] = 'N'
                            response[4] = {'date': date, 'leave': response[1], 'count': '0.5'}
                            response[5] = 0.5

                else:
                    response[1] = qry[0]['leavecode__leave_abbr']

                    # if hourly, check its validity (e.g SHL is hourly leave which adds 1:30 hours to the working time. If adding 1:30 hrs, working time gets greater than or equal to required full day wokring time, leave is counted i.e response[0]=2 else it will be ignored i.e response[0]=3) #####################3

                    res_func = checkhourlyvalid(pmail, qry[0]['leavecode'], date, status)
                    response[0] = res_func
                    if response[0] == 2:

                        if qry[0]['leavecode__leaveCountStatus'] == 'Y':
                            response[2] = 'Y'
                            response[3] = {'date': date, 'leave': response[1], 'count': '0.5'}
                        else:
                            response[2] = 'N'
                            response[4] = {'date': date, 'leave': response[1], 'count': '0.5'}
                            response[5] = 0.5

            ################ if date is neither fromdate or todate i.e it is between fromdate and todate so its count will be always 1 ######

            else:
                response[0] = 1
                response[1] = qry[0]['leavecode__leave_abbr']
                if qry[0]['leavecode__leaveCountStatus'] == 'Y':
                    response[2] = 'Y'
                    response[3] = {'date': date, 'leave': response[1], 'count': '1'}
                else:
                    response[2] = 'N'
                    response[4] = {'date': date, 'leave': response[1], 'count': '1'}
                    response[5] = 1

    ######## no leave is applied ########################

    else:
        response[0] = 3

    return response


def check_for_sandwich(fromdate, todate, pmail):

    qry_dept = EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=pmail)).values('dept')
    day = datetime.timedelta(days=1)
    date1 = fromdate
    date2 = todate
    while True:
        date1 = date1 - day
        qry_check_holi = Holiday.objects.filter(f_date__lte=date1, t_date__gte=date1, status="INSERT", dept=EmployeeDropdown.objects.get(sno=qry_dept[0]['dept']))

        if len(qry_check_holi) == 0:
            break

    while True:
        date2 = date2 + day

        qry_check_holi = Holiday.objects.filter(f_date__lte=date2, t_date__gte=date2, status="INSERT", dept=EmployeeDropdown.objects.get(sno=qry_dept[0]['dept']))
        if len(qry_check_holi) == 0:
            break

    flag_before = False
    flag_after = False

    ###################### before holiday ###########################
    qry1 = Leaves.objects.filter(emp_id=pmail, fromdate__lte=date1, todate__gte=date1, leavecode__leaveCountStatus="Y", finalstatus__contains="APPROVED").values('leaveid', 'leavecode__leave_abbr', 'fhalf', 'thalf', 'fromdate', 'todate', 'leavecode', 'leavecode__hours_leave')

    qry3 = Attendance2.objects.filter(Emp_Id=pmail, date=date1).exclude(status='H').values()

    if len(qry3) > 0:
        status3 = qry3[0]['status']
    else:
        status3 = 'P'

    for l1 in qry1:
        l1['fromdate'] = datetime.datetime.strptime(str(l1['fromdate']).split(' ')[0], "%Y-%m-%d").date()
        l1['todate'] = datetime.datetime.strptime(str(l1['todate']).split(' ')[0], "%Y-%m-%d").date()
        date1 = datetime.datetime.strptime(str(date1), "%Y-%m-%d").date()

        if l1['fromdate'] < date1 and l1['todate'] > date1 and l1['leavecode__leave_abbr'] != 'OD':
            flag_before = True
            break
        elif l1['fromdate'] < date1:
            if (l1['thalf'] == '2' or l1['thalf'] == '0') and (status3 != 'P' and status3 != 'P/II') and l1['leavecode__leave_abbr'] != 'OD':
                flag_before = True
                break
            elif (l1['thalf'] == '1') and (status3 == 'P/I' or status3 == 'A' or status3 == 'P/A'):
                flag_before = True
                break
        else:
            if l1['leavecode__hours_leave'] == 'Y':
                res_func = checkhourlyvalid(pmail, l1['leavecode'], date1, status3)
                if res_func != 2:
                    flag_before = True
                    break
            else:
                if (l1['thalf'] == '2' or l1['thalf'] == '0') and (status3 != 'P' and status3 != 'P/II') and l1['leavecode__leave_abbr'] != 'OD':
                    flag_before = True
                    break
                elif (l1['thalf'] == '1') and (status3 == 'P/I' or status3 == 'A' or status3 == 'P/A'):
                    flag_before = True
                    break

    if status3 != 'P' and status3 != 'P/II' and len(qry1) == 0:
        flag_before = True

    ###################### after holiday ###########################

    qry2 = Leaves.objects.filter(emp_id=pmail, fromdate__lte=date2, todate__gte=date2, leavecode__leaveCountStatus="Y", finalstatus__contains="APPROVED").values('leaveid', 'leavecode__leave_abbr', 'fhalf', 'thalf', 'fromdate', 'todate', 'leavecode', 'leavecode__hours_leave')

    qry4 = Attendance2.objects.filter(Emp_Id=pmail, date=date2).exclude(status='H').values()

    if len(qry4) > 0:
        status4 = qry4[0]['status']
    else:
        status4 = 'P'

    for l2 in qry2:
        l2['fromdate'] = datetime.datetime.strptime(str(l2['fromdate']).split(' ')[0], "%Y-%m-%d").date()
        l2['todate'] = datetime.datetime.strptime(str(l2['todate']).split(' ')[0], "%Y-%m-%d").date()
        date2 = datetime.datetime.strptime(str(date2), "%Y-%m-%d").date()

        if l2['fromdate'] < date2 and l2['todate'] > date2 and l2['leavecode__leave_abbr'] != 'OD':
            flag_after = True
            break

        elif l2['fromdate'] < date2:
            if (l2['thalf'] == '1' or l2['thalf'] == '0') and (status4 != 'P' and status4 != 'P/I') and l2['leavecode__leave_abbr'] != 'OD':
                flag_after = True
                break
            elif (l2['thalf'] == '2') and (status4 == 'P/II' or status4 == 'A' or status4 == 'P/A'):
                flag_after = True
                break

        else:
            if l2['leavecode__hours_leave'] == 'Y':
                res_func = checkhourlyvalid(pmail, l2['leavecode'], date2, status4)
                if res_func != 2:
                    flag_after = True
                    break
            else:
                if (l2['fhalf'] == '1' or l2['fhalf'] == '0') and (status4 != 'P' and status4 != 'P/I') and l2['leavecode__leave_abbr'] != 'OD':
                    flag_after = True
                    break
                elif (l2['fhalf'] == '2') and (status4 == 'P/II' or status4 == 'A' or status4 == 'P/A'):
                    flag_after = True
                    break

    if status4 != 'P' and status4 != 'P/I' and len(qry2) == 0:
        flag_after = True

    flag = 0

    # print(qry1)
    # print(qry2)
    # print(qry3)
    # print(qry4)
    # print(status3,status4)

    # qry1=Leaves.objects.filter(emp_id=pmail,fromdate__lte=date1,todate__gte=date1,leavecode__leaveCountStatus="Y",finalstatus__contains="APPROVED").values('leaveid','leavecode__leave_abbr','fhalf','thalf','fromdate','todate','leavecode','leavecode__hours_leave')

    # qry2=Leaves.objects.filter(emp_id=pmail,fromdate__lte=date2,todate__gte=date2,leavecode__leaveCountStatus="Y",finalstatus__contains="APPROVED").values('leaveid','leavecode__leave_abbr','fhalf','thalf','fromdate','todate','leavecode','leavecode__hours_leave')

    # qry3=Attendance2.objects.filter(Emp_Id=pmail,date=date1).exclude(status='H').values()

    # if len(qry3)>0:
    #   status3=qry3[0]['status']
    # else:
    #   status3='P'

    # qry4=Attendance2.objects.filter(Emp_Id=pmail,date=date2).exclude(status='H').values()

    # if len(qry4)>0:
    #   status4=qry4[0]['status']
    # else:
    #   status4='P'

    # flag=0

    # if len(qry1)>0 and len(qry2)>0:

    #   if not ((str(date1) == qry1[0]['todate'].strftime( '%Y-%m-%d') and qry1[0]['thalf'] == '1'and (status3 != 'P' or status3 != 'P/II')) or (str(date1) == qry1[0]['fromdate'].strftime( '%Y-%m-%d') and qry1[0]['fhalf'] == '1' and (status3 != 'P' or status3 != 'P/II')) or (str(date2) ==  qry2[0]['fromdate'].strftime( '%Y-%m-%d') and qry2[0]['fhalf'] == '2' and (status4 != 'P' or status4 != 'P/I'))):

    #       if qry1[0]['leavecode__leave_abbr'] == 'OD':
    #           if qry1[0]['thalf'] == '2' or qry1[0]['fhalf'] == '0':
    #               return 0

    #       if qry2[0]['leavecode__leave_abbr'] == 'OD':
    #           if qry2[0]['thalf'] == '1' or qry2[0]['fhalf'] == '0':
    #               return 0

    #       if qry1[0]['leavecode__hours_leave'] != 'Y' and qry2[0]['leavecode__hours_leave'] != 'Y':
    #           return 1

    #       elif qry1[0]['leavecode__hours_leave'] == 'Y' and qry2[0]['leavecode__hours_leave'] == 'Y':
    #           res_func=checkhourlyvalid(pmail,qry1[0]['leavecode'],date1,status3)
    #           res_func2=checkhourlyvalid(pmail,qry2[0]['leavecode'],date2,status4)
    #           if res_func != 2 and res_func2 != 2:
    #               return 1

    #       elif qry1[0]['leavecode__hours_leave'] == 'Y' :
    #           res_func=checkhourlyvalid(pmail,qry1[0]['leavecode'],date1,status3)
    #           if res_func != 2 :
    #               return 1

    #       elif qry2[0]['leavecode__hours_leave'] == 'Y' :
    #           res_func=checkhourlyvalid(pmail,qry2[0]['leavecode'],date2,status4)
    #           if res_func != 2 :
    #               return 1

    # elif len(qry1)>0 and len(qry4)>0:
    #   if not ((str(date1) == qry1[0]['todate'].strftime( '%Y-%m-%d') and qry1[0]['thalf'] == '1'and (status3 != 'P' or status3 != 'P/II')) or (str(date1) == qry1[0]['fromdate'].strftime( '%Y-%m-%d') and qry1[0]['fhalf'] == '1'and (status3 != 'P' or status3 != 'P/II')) or (qry4[0]['status'] == 'P' or qry4[0]['status'] == 'P/I')):

    #       if qry1[0]['leavecode__leave_abbr'] == 'OD':
    #           if qry1[0]['thalf'] == '2' or qry1[0]['fhalf'] == '0':
    #               return 0

    #       if  qry1[0]['leavecode__hours_leave'] == 'Y':
    #           res_func=checkhourlyvalid(pmail,qry1[0]['leavecode'],date1,qry3[0]['status'])
    #           if res_func != 2:
    #               return 1
    #       else:
    #           return 1

    # elif len(qry2)>0 and len(qry3)>0:

    #   if not ((qry3[0]['status'] == 'P' or qry3[0]['status'] == 'P/II') or (str(date2) ==  qry2[0]['fromdate'].strftime( '%Y-%m-%d') and qry2[0]['fhalf'] == '2'  and (status4 != 'P' or status4 != 'P/I'))):

    #       if qry2[0]['leavecode__leave_abbr'] == 'OD':
    #           if qry2[0]['thalf'] == '1' or qry2[0]['fhalf'] == '0':
    #               return 0

    #       if qry2[0]['leavecode__hours_leave'] == 'Y':
    #           res_func=checkhourlyvalid(pmail,qry2[0]['leavecode'],date2,qry4[0]['status'])
    #           if res_func != 2:
    #               return 1
    #       else:
    #           return 1

    # elif len(qry3)>0 and len(qry4)>0:
    #   if not ((qry3[0]['status'] == 'P' or qry3[0]['status'] == 'P/II') or (qry4[0]['status'] == 'P' or qry4[0]['status'] == 'P/I')):
    #       return 1

    if flag_before and flag_after:
        return 1
    else:
        return 0


def monthholiday(pmail, startdate, enddate):

    startdate = datetime.datetime.strptime(str(startdate), "%Y-%m-%d").date()
    enddate = datetime.datetime.strptime(str(enddate), "%Y-%m-%d").date()

    qry0 = EmployeePrimdetail.objects.filter(emp_id=pmail).values('dept', 'doj')

    ################## get all the  holidays of the requested month ####################

    qry = Holiday.objects.filter(Q(f_date__range=(startdate, enddate)) | Q(t_date__range=(startdate, enddate)) | Q(f_date__lte=startdate, t_date__gte=enddate)).filter(dept=qry0[0]['dept']).values('f_date', 't_date', 'h_type')

    holiday = 0
    leave = 0
    leave_nc = 0
    present = 0
    absent = 0

    holiday_data = []
    present_data = []
    leave_data = []
    leave_nc_data = []
    absent_data = []

    day = datetime.timedelta(days=1)

    for hol in qry:
        h_type = EmployeeDropdown.objects.filter(sno=hol['h_type']).values('value')
        if(hol['f_date'] < startdate and hol['t_date'] > enddate):
            f_date = startdate
            t_date = enddate

        elif(hol['f_date'] < startdate):
            f_date = startdate
            t_date = hol['t_date']

        elif(hol['t_date'] > enddate):
            f_date = hol['f_date']
            t_date = enddate

        else:
            f_date = hol['f_date']
            t_date = hol['t_date']

        while f_date < qry0[0]['doj'] and f_date <= t_date:
            absent += 1
            absent_data.append({'date': date_format(f_date), 'count': '1', 'status': 'A', 'intime': '00:00:00', 'outtime': '00:00:00'})
            f_date += day

        if f_date > t_date:
            continue
        ################ for a given holiday, check for sandwich #####################

        ############################## SANDWICH EXPLANATION ##########################
        # consider the following dates:- 8th march (working day) 9th & 10th march (holiday) and 11th march (working day)
        ########### if an employee is absent for fullday or absent for second half or applied leave for full day or  leave for second half or P/A status on 8th march ########################################################################

        ############################  AND ############################################################
        ########### if an employee is absent for fullday or absent for first half or applied leave for full day or  leave for first half or P/A status on 11th march ##########################################

        ########### then 9th and 10th march will be considered as absent for that employee unless he/she applied leave for 9th & 10th march ################################################################

        if check_for_sandwich(f_date, t_date, pmail) == 1:
            ############ if sandwich is there ####################################

            ############ check for leave applied on holidays ###############

            while f_date <= t_date:
                qry_att = Attendance2.objects.filter(Emp_Id=pmail, date=f_date).exclude(status='H').values()

                if len(qry_att) > 0:
                    f_date += day
                    continue
                res = check_leave_status(pmail, f_date, "A")
                if res[0] == 1:
                    if res[2] == 'Y':
                        leave += 1
                        leave_data.append({'date': date_format(f_date), 'count': '1', 'leave': res[1]})
                    elif res[2] == 'N':
                        leave_nc += 1
                        leave_nc_data.append({'date': date_format(f_date), 'count': '1', 'leave': res[1]})
                    else:
                        leave += 0.5
                        leave_nc += 0.5
                        leave_data.append({'date': date_format(f_date), 'count': '0.5', 'leave': res[1]})
                        leave_nc_data.append({'date': date_format(f_date), 'count': '0.5', 'leave': res[1]})

                elif res[0] == 2:
                    if res[2] == 'Y':
                        leave += 0.5
                        absent += 0.5
                        absent_data.append({'date': date_format(f_date), 'count': '0.5', 'status': 'A', 'intime': '00:00:00', 'outtime': '00:00:00'})
                        leave_data.append({'date': date_format(f_date), 'count': '0.5', 'leave': res[1]})
                    else:
                        leave_nc += 0.5
                        leave_nc_data.append({'date': date_format(f_date), 'count': '0.5', 'leave': res[1]})
                        absent += 0.5
                        absent_data.append({'date': date_format(f_date), 'count': '0.5', 'status': 'A', 'intime': '00:00:00', 'outtime': '00:00:00'})
                else:
                    absent += 1
                    absent_data.append({'date': date_format(f_date), 'count': '1', 'status': 'A', 'intime': '00:00:00', 'outtime': '00:00:00'})

                f_date += day
        else:

            ######### sandwich is not there ###################

            while f_date <= t_date:
                qry_att = Attendance2.objects.filter(Emp_Id=pmail, date=f_date).exclude(status='H').values()
                if len(qry_att) > 0:
                    f_date += day
                    continue
                ####### check for leave. Give priority to leave over holiday ################

                res = check_leave_status(pmail, f_date, "A")

                if res[0] == 1:
                    if res[2] == 'Y':
                        leave += 1
                        leave_data.append({'date': date_format(f_date), 'count': '1', 'leave': res[1]})
                    elif res[2] == 'N':
                        leave_nc += 1
                        leave_nc_data.append({'date': date_format(f_date), 'count': '1', 'leave': res[1]})
                    else:
                        leave += 0.5
                        leave_nc += 0.5
                        leave_data.append({'date': date_format(f_date), 'count': '0.5', 'leave': res[1]})
                        leave_nc_data.append({'date': date_format(f_date), 'count': '0.5', 'leave': res[1]})

                elif res[0] == 2:
                    if res[2] == 'Y':
                        leave += 0.5
                        holiday += 0.5
                        holiday_data.append({'date': date_format(f_date), 'count': '0.5', 'holiday': h_type[0]['value']})
                        leave_data.append({'date': date_format(f_date), 'count': '0.5', 'leave': res[1]})
                    else:
                        leave_nc += 0.5
                        leave_nc_data.append({'date': date_format(f_date), 'count': '0.5', 'leave': res[1]})
                        holiday += 0.5
                        holiday_data.append({'date': date_format(f_date), 'count': '0.5', 'holiday': h_type[0]['value']})
                else:
                    holiday += 1
                    holiday_data.append({'date': date_format(f_date), 'count': '1', 'holiday': h_type[0]['value']})

                f_date += day

    data_send = {'h': holiday, 'l': leave, 'a': absent, 'p': present, 'l_nc': leave_nc, 'holiday_data': holiday_data, 'present_data': present_data, 'leave_data': leave_data, 'absent_data': absent_data, 'leave_nc_data': leave_nc_data}

    return data_send


def calculate_working_days(emp_id, fdate, tdate, emp_name, emp_dept):

    summ = dayssummay(emp_id, fdate, tdate, "att")

    ####### get employee status on working status #########

    holiday = monthholiday(emp_id, fdate, tdate)

    ##### get employee status on holidays ##################

    a = {
        'pmail': emp_id,
        'name': emp_name,
        'dept': emp_dept,
        'present': summ['present'] + holiday['p'],
        'absent': summ['absent'] + holiday['a'],
        'leave': summ['leave'] + holiday['l'],
        'leave_nc': summ['leave_nc'] + holiday['l_nc'],
        'holiday': holiday['h'],
        'present_data': sorted(holiday['present_data'] + summ['present_data'], key=itemgetter('date')),
        'holiday_data': sorted(holiday['holiday_data'], key=itemgetter('date')),
        'leave_data': sorted(holiday['leave_data'] + summ['leave_data'], key=itemgetter('date')),
        'absent_data': sorted(summ['absent_data'] + holiday['absent_data'], key=itemgetter('date')),
        'payable_days': summ['present'] + holiday['p'] + summ['leave'] + holiday['l'] + holiday['h'],
        'total_days': summ['present'] + holiday['p'] + summ['leave'] + holiday['l'] + holiday['h'] + summ['leave_nc'] + holiday['l_nc'] + summ['absent'] + holiday['a'],
        'leave_nc_data': summ['leave_nc_data'] + holiday['leave_nc_data']
    }

    return a


def monthlydeptsummary(request):
    data1 = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            data = json.loads(request.body)
            if data['request_type'] == "admin":
                check = checkpermission(request, [211, 337, 1345])
            elif data['request_type'] == "employee":
                check = checkpermission(request, [337])
            elif data['request_type'] == "hod":
                check = checkpermission(request, [425, 337])
            else:
                check = 403
            if(check == 200):
                if(request.method == 'POST'):
                    year = int(data['year'])
                    month = int(data['month'])
                    date = datetime.date(year, month, 1)
                    session = acc.views.getCurrentSession(date)
                    fdate = datetime.date(year, month, 1).strftime('%Y-%m-%d')
                    range1 = calendar.monthrange(year, month)
                    tdate = datetime.date(year, month, range1[1]).strftime('%Y-%m-%d')
                    global_array = []
                    qry_arr = []
                    if data['request_type'] == "admin":
                        dept = []
                        coe = []
                        dept.append(data['dept'])
                        coe.append(data['etype'])

                        if dept[0] == 'ALL':
                            qry_dept = EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value__isnull=True).values('sno')
                            dept = [d['sno'] for d in qry_dept]
                        if coe[0] == 'ALL':
                            qry_coe = EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).values('sno')
                            coe = [c['sno'] for c in qry_coe]

                        qry_check = DaysGenerateLog.objects.filter(sessionid=session, month=month).values('id')
                        if len(qry_check) == 0:
                            qry = EmployeePrimdetail.objects.filter(dept__in=dept, emp_category__in=coe, emp_status='ACTIVE').values('emp_id', 'name', 'dept__value')
                        else:
                            qry = EmployeePayableDays.objects.filter(session=session, month=month, dept__in=dept, emp_category__in=coe).annotate(name=F('emp_id__name')).values('emp_id', 'name', 'dept__value').distinct()

                        if dept != 'ALL':
                            qry_dept = EmployeeDropdown.objects.filter(sno=dept[0]).values('value')
                            dept = qry_dept[0]['value']
                        else:
                            dept = "All"

                    elif data['request_type'] == "employee":
                        year = int(data['year'])
                        month = int(data['month'])
                        date = datetime.date(year, month, 1)
                        fdate = datetime.date(year, month, 1).strftime('%Y-%m-%d')
                        range1 = calendar.monthrange(year, month)
                        tdate = datetime.date(year, month, range1[1]).strftime('%Y-%m-%d')
                        global_array = []

                        qry = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('emp_id', 'name', 'dept', 'dept__value')
                        dept = qry[0]['dept']

                    elif data['request_type'] == "hod":
                        year = int(data['year'])
                        month = int(data['month'])
                        date = datetime.date(year, month, 1)
                        fdate = datetime.date(year, month, 1).strftime('%Y-%m-%d')
                        range1 = calendar.monthrange(year, month)
                        tdate = datetime.date(year, month, range1[1]).strftime('%Y-%m-%d')
                        global_array = []

                        qry_dept = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        dept = qry_dept[0]['dept']

                        coe = []
                        coe.append(data['etype'])
                        if coe[0] == 'ALL':
                            qry_coe = EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).values('sno')
                            coe = [c['sno'] for c in qry_coe]
                        qry_check = DaysGenerateLog.objects.filter(sessionid=session, month=month).values('id')
                        if len(qry_check) == 0:
                            qry = EmployeePrimdetail.objects.filter(dept=dept, emp_category__in=coe, emp_status='ACTIVE').values('emp_id', 'name', 'dept__value')
                        else:
                            qry = EmployeePayableDays.objects.filter(session=session, month=month, dept=dept, emp_category__in=coe).annotate(name=F('emp_id__name')).values('emp_id', 'name', 'dept__value').distinct()
                    start = datetime.datetime.now()
                    for emp in qry:
                        dat = calculate_working_days(emp['emp_id'], fdate, tdate, emp['name'], emp['dept__value'])
                        global_array.append(dat)
                    data1 = {'data': global_array, 'dept': dept}
                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data1, safe=False)


def leavedata(emp_id, fromdate, todate, leavetype, sta):
    filter_data = {}
    filter_data['emp_id'] = emp_id
    filter_data['fromdate__gte'] = fromdate
    filter_data['todate__lte'] = todate

    if sta:
        filter_data['finalstatus__in'] = sta

    leave_query = Leaves.objects.filter(**filter_data).extra(select={'fromdate': "DATE(fromdate)", 'todate': "DATE(todate)"}).values('leaveid', 'todate', 'fromdate', 'leavecode__leave_name', 'subtype__value', 'leavecode__leave_name', 'category__value', 'days', 'reason', 'extrahours', 'extraworkdate', 'finalstatus', 'finalapprovaldate')
    leaves_data = {}
    if 'normal' in leavetype:
        exclude_data = [leavetype['od'], leavetype['compoff']]
        leaves_data['normal'] = list(leave_query.exclude(leavecode__in=exclude_data))
    if 'compoff' in leavetype:
        data = leavetype['compoff']
        leaves_data['compoff'] = list(leave_query.filter(leavecode=data))
    if 'od' in leavetype:
        data = leavetype['od']
        leaves_data['od'] = list(leave_query.filter(leavecode=data))

    return leaves_data


def allstatus(request):
    data = ''
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if(check == 200):
                if(request.method == 'POST'):

                    data = json.loads(request.body)

                    id = data['id']
                    try:
                        data = list(Leaveapproval.objects.filter(leaveid=id).extra(select={'approvaldate': "DATE_FORMAT(approvaldate,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('dept__value', 'desg__value', 'approvaldate', 'status', 'remark'))
                        status = 200
                    except:
                        status = 500

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data, safe=False)


def singleleaveviewreport(request):
    data = ''
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    data_search = {}
                    emp_id = data['emp']
                    fromdate = data['f_date']
                    todate = data['t_date']
                    sta = data['status']
                    if data['leavetype'] == 'ALL':
                        leavetype = {'normal': 0}
                        qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')
                        leavetype['od'] = qry_od_id[0]['id']
                        qry_compoff_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
                        leavetype['compoff'] = qry_compoff_id[0]['id']

                    try:
                        leaves_data = leavedata(emp_id, fromdate, todate, leavetype, sta)
                        data = leaves_data
                        status = 200
                    except:
                        status = 500
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data, safe=False)


def mannualLeaveremaning(request):
    data = ''
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211])
            if(check == 200):
                data = []
                if(request.method == 'GET'):
                    qry_emp = EmployeePrimdetail.objects.filter(emp_status='ACTIVE', emp_id=request.GET['employee']).values('desg', 'emp_category', 'emp_type')
                    qry0 = LeaveQuota.objects.filter(category_emp=qry_emp[0]['emp_category'], type_of_emp=qry_emp[0]['emp_type'], designation=qry_emp[0]['desg'], status='INSERT').values('leave_id', 'leave_id__leave_name', 'leave_id__leave_abbr')
                    for leave in qry0:
                        qry = Leaveremaning.objects.filter(empid=request.GET['employee'], leaveid=leave['leave_id']).values('id', 'remaining')
                        if(qry.count() > 0):
                            a = {'id': qry[0]['id'],
                                 'leaveid': leave['leave_id'],
                                 'remaining': qry[0]['remaining'],
                                 'leaveid__leave_name': leave['leave_id__leave_name'],
                                 'leaveid__leave_abbr': leave['leave_id__leave_abbr']
                                 }
                        else:
                            a = {'id': -1,
                                 'leaveid': leave['leave_id'],
                                 'remaining': 0,
                                 'leaveid__leave_name': leave['leave_id__leave_name'],
                                 'leaveid__leave_abbr': leave['leave_id__leave_abbr']
                                 }
                        data.append(a)
                    status = 200

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(status=status, data=data, safe=False)


def mannualLeaveremaningupdate(request):

    data = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211])
            if(check == 200):
                if(request.method == 'PUT'):
                    data = data = json.loads(request.body)
                    inp = data['updatedata']
                    emp = data['emp_id']
                    for inp1 in inp:
                        if(inp1['id'] == -1):
                            qry = Leaveremaning.objects.create(empid=EmployeePrimdetail.objects.get(emp_id=emp), leaveid=LeaveType.objects.get(id=inp1['leaveid']), remaining=inp1['remaining'])
                        else:
                            qry = Leaveremaning.objects.filter(empid=emp, leaveid=inp1['leaveid']).update(remaining=inp1['remaining'])
                    msg = "credit leave Successfully Updated"
                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    data = {'msg': msg}
    return JsonResponse(status=status, data=data)


# def leaveCreditscript(request):
#   qry_emp=EmployeePrimdetail.objects.filter(emp_status='ACTIVE').values('emp_id','desg','dept','emp_category','emp_type')
#   for emp in qry_emp:
#       gender=EmployeePerdetail.objects.filter(emp_id=emp['emp_id']).values('gender__value')
#       leave_quota=LeaveQuota.objects.filter(designation=emp['desg'],category_emp=emp['emp_category'],type_of_emp=emp['emp_type']).exclude(status="DELETE").values()

################################################### ADD LEAVE VIEWS ######################################


def employee_remaining_leaves(empid, arrear_leave):
    gender_qry = EmployeePerdetail.objects.filter(emp_id=empid).values('gender')
    q_det = EmployeePrimdetail.objects.filter(emp_id=empid).values('emp_type', 'emp_category', 'desg')
    gender_value = EmployeeDropdown.objects.filter(sno=gender_qry[0]['gender']).values('value')

    if len(gender_value) > 0:
        if(gender_value[0]['value'] == 'MALE'):
            gender = 'M'
        elif(gender_value[0]['value'] == 'FEMALE'):
            gender = 'F'
        else:
            gender = 'B'
    else:
        gender = 'B'

    leave_qry = LeaveType.objects.filter(Q(leaveforgender=gender) | Q(leaveforgender='B')).filter(status='INSERT').exclude(leave_abbr='CO').exclude(leave_abbr='OD').values('id', 'leave_name', 'leave_abbr', 'apply_days', 'hours_leave', 'lapse_start', 'lapse_month')
    data_send = []

    date1 = date.today()

    for qr in leave_qry:
        if arrear_leave == True and qr['lapse_start'] is not None and qr['lapse_month'] is not None:
            date2 = qr['lapse_start'] - relativedelta(months=(qr['lapse_month']))
            if date2 > date1:
                continue
        qry_upload_check = OdCategoryUpload.objects.filter(LeaveId=qr['id']).values('num_of_days')
        q_quota = LeaveQuota.objects.filter(category_emp=q_det[0]['emp_category'], designation=q_det[0]['desg'], type_of_emp=q_det[0]['emp_type']).values('id')
        if len(q_quota) == 0:
            continue
        leave_rem = Leaveremaning.objects.filter(empid=empid, leaveid=qr['id']).values('remaining', 'id').order_by('-id')

        if len(leave_rem) > 0:
            lv_rm = leave_rem[0]['remaining']
            if len(qry_upload_check) > 0:
                data_send.append({'id': qr['id'], 'leave_name': qr['leave_name'], 'leave_abbr': qr['leave_abbr'], 'apply_days': qr['apply_days'], 'hours_leave': qr['hours_leave'], 'upload': 'YES', 'num_of_days': qry_upload_check[0]['num_of_days'], 'leaves_remaining': lv_rm
                                  })
            else:
                data_send.append({'id': qr['id'], 'leave_name': qr['leave_name'], 'leave_abbr': qr['leave_abbr'], 'apply_days': qr['apply_days'], 'hours_leave': qr['hours_leave'], 'upload': 'NO', 'num_of_days': 0, 'leaves_remaining': lv_rm})

    return data_send


def Extract_Leaves_Genderwise(request):
    data = {}
    arrear_leave = False
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.method == 'GET':
                if(request.GET['request_type'] == 'admin'):
                    check = checkpermission(request, [337, 211])
                    a = 1
                if(request.GET['request_type'] == 'arrear_leave'):
                    check = checkpermission(request, [337, 211])
                    a = 1
                    arrear_leave = True
                if(request.GET['request_type'] == 'employee'):
                    check = checkpermission(request, [337])
                    a = 0
                if check == 200:
                    if(a == 1):
                        empid = request.GET['emp_code']
                    else:
                        empid = request.session['hash1']

                    data_send = employee_remaining_leaves(empid, arrear_leave)

                    status = 200
                    data = {'LeaveType': data_send}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data, status=status)


######################################################## FUNCTIONS ###################################################


def employee_leave_count_date_range(emp_id, fdate, tdate):
    employee_all_leaves = employee_remaining_leaves(emp_id, False)

    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')
    qry_co_id = LeaveType.objects.filter(leave_abbr='CO').values('id')

    employee_all_leaves.append({"id": qry_od_id[0]['id'], "leave_abbr": "OD"})
    employee_all_leaves.append({"id": qry_co_id[0]['id'], "leave_abbr": "COMP-OFF"})

    leaveid_arr = []
    for leave in employee_all_leaves:
        leaveid_arr.append(leave['id'])

    qry_count = list(Leaves.objects.filter(requestdate__range=[fdate, tdate], emp_id=emp_id, leavecode__in=leaveid_arr, finalstatus__contains='APPROVED').annotate(label=F('leavecode__leave_abbr')).values('label', 'leavecode').annotate(data=Count('leavecode')))

    qry_count_lid = [c['leavecode'] for c in qry_count]

    for leave in employee_all_leaves:
        if leave['id'] not in qry_count_lid:
            qry_count.append({'label': leave['leave_abbr'], 'leavecode': leave['id'], "data": 0})

    return qry_count


# def Leave_DayLimit(date,dept,lid,empid):    #### date = from_date

#   given_date=date
#   today=datetime.datetime.now().date()
#   day_limit_qry=LeaveType.objects.filter(status='INSERT',id=lid).values('apply_days')[0:1]
#   day_limit=day_limit_qry[0]['apply_days']

#   day = datetime.timedelta(days=1)
#   while(day_limit>0):
#       today=today-day

#       qry_check_att=Attendance2.objects.filter(Emp_Id=empid).filter(date=today).exclude(status='A').exclude(status='H').values('status')
#       if(len(qry_check_att)>0):
#           day_limit=day_limit-1
#       else:
#           return True


#   if(given_date<today):
#       return False
#   else:
#       return True

def Leave_DayLimit(date, dept, lid, empid):  # date = from_date

    given_date = date
    today = datetime.datetime.now().date()
    day_limit_qry = LeaveType.objects.filter(status='INSERT', id=lid).values('apply_days')[0:1]
    day_limit = day_limit_qry[0]['apply_days']

    day = datetime.timedelta(days=1)
    while(day_limit > 0):
        today = today - day

        qry_check_att = Attendance2.objects.filter(Emp_Id=empid).filter(date=today).values('status')
        if(len(qry_check_att) == 0):
            return True
        else:
            if(qry_check_att[0]['status'] in ['A', 'H']):
                continue
            else:
                day_limit = day_limit - 1

    if(given_date < today):
        return False
    else:
        return True


def Leave_HalfCheck(fdate, tdate, half1, half2):  # check whether halves are valid or not############
    if(fdate > tdate):
        return False

    elif((half1 == '1' and half2 == '1') or (half1 == '2' and half2 == '2')):  # 0: Full day, 1: First Half, 2: Second Half
        if(fdate != tdate):
            return False
        else:
            return True

    elif((half1 == '0' and (half2 == '0' or half2 == '1')) or (half1 == '1' and half2 == '1') or (half1 == '2' and (half2 == '0' or half2 == '1'))):
        return True
    else:
        return False


def Leave_ClubCheck(leaveid, empid, fdate, tdate, fhalf, thalf):
    data = []

    qry_check_samedate_leave = Leaves.objects.filter(emp_id=empid).filter(Q(todate=tdate) | Q(fromdate=fdate)).filter(Q(finalstatus='PENDING') | Q(finalstatus__contains='APPROVED')).values('leavecode', 'thalf', 'leavecode__leave_name', 'fhalf', 'fromdate', 'todate')
    for q in qry_check_samedate_leave:
        qry_club1 = LeaveClub.objects.filter(leave_id1=q['leavecode'], leave_id2=leaveid)
        qry_club2 = LeaveClub.objects.filter(leave_id2=q['leavecode'], leave_id1=leaveid)

        if len(qry_club1) == 0 and len(qry_club2) == 0:
            data.append(False)
            data.append(q['leavecode__leave_name'])
            return data

    data.append(True)
    return data


def Leave_ClubCheck2(leaveid, empid, fdate, tdate, fhalf, thalf):
    data = []

    if(fhalf == '2'):  # if leave is applied for second half
        fhalf = 'H'
        qry_check_samedate_leave = Leaves.objects.filter(emp_id=empid, todate=fdate).filter(Q(finalstatus='PENDING') | Q(finalstatus__contains='APPROVED')).values('leavecode', 'thalf', 'leavecode__leave_name', 'fhalf')
        nextdate = tdate + timedelta(days=1)
        qry_check_nextdate_leave = Leaves.objects.filter(emp_id=empid, fromdate=nextdate).filter(Q(finalstatus='PENDING') | Q(finalstatus__contains='APPROVED')).values('leavecode', 'fhalf', 'leavecode__leave_name', 'thalf')

        if(qry_check_samedate_leave.count() > 0 or qry_check_nextdate_leave.count() > 0):  # if leave exists for either samedate or next day

            if(qry_check_samedate_leave.count() > 0):  # if due to same date

                if(qry_check_samedate_leave[0]['thalf'] == '1'):
                    samehalf = 'H'
                    qry_check_clubbing_exists = LeaveClub.objects.filter(leave_id1=qry_check_samedate_leave[0]['leavecode'], leave_id2=leaveid, day_count1=samehalf, day_count2=fhalf)
                    if(qry_check_clubbing_exists.count() == 0):
                        data.append(False)
                        data.append(qry_check_samedate_leave[0]['leavecode__leave_name'])
                        return data

            if(qry_check_nextdate_leave.count() > 0):  # if due to next day

                if(qry_check_nextdate_leave[0]['thalf'] != '2'):  # II half is not in continuation with today's II half
                    if(qry_check_nextdate_leave[0]['thalf'] == '1'):
                        thalf = 'H'
                    else:
                        thalf = 'F'
                    qry_check_clubbing_exists = LeaveClub.objects.filter(leave_id1=leaveid, leave_id2=qry_check_nextdate_leave[0]['leavecode'], day_count1=fhalf, day_count2=thalf)
                    if(qry_check_clubbing_exists.count() == 0):
                        data.append(False)
                        data.append(qry_check_nextdate_leave[0]['leavecode__leave_name'])
                        return data
                    else:
                        data.append(True)
                        return data
                else:
                    data.append(True)
                    return data
        else:
            data.append(True)
            return data

    if(fhalf == thalf and fhalf == '1'):  # if leave is applied for 1 day and for I half

        checkdate = (fdate - timedelta(days=1))
        qry_check_previousdate_leave = Leaves.objects.filter(emp_id=empid, todate=checkdate).filter(Q(finalstatus='PENDING') | Q(finalstatus__contains='APPROVED')).values('leavecode', 'thalf', 'leavecode__leave_name')
        fhalf = 'H'
        if(qry_check_previousdate_leave.count() > 0):

            if(qry_check_previousdate_leave[0]['thalf'] == '2'):
                prehalf = 'H'
            else:
                prehalf = 'F'
            qry_check_clubbing_exists = LeaveClub.objects.filter(leave_id1=qry_check_previousdate_leave[0]['leavecode'], leave_id2=leaveid).filter(day_count1=prehalf, day_count2=fhalf)
            if(qry_check_clubbing_exists.count() == 0):
                data.append(False)
                data.append(qry_check_previousdate_leave[0]['leavecode__leave_name'])
                return data
            else:
                data.append(True)
                return data
        else:
            data.append(True)
            return data

    if(fhalf == '0'):  # if leave is applied for 1 full day
        fhalf = 'F'
        predate = (fdate - timedelta(days=1))
        postdate = (tdate + timedelta(days=1))

        qry_check_predate_leave = Leaves.objects.filter(emp_id=empid, todate=predate).filter(Q(finalstatus__contains='PENDING') | Q(finalstatus__contains='APPROVED')).values('leavecode', 'thalf', 'leavecode__leave_name')

        qry_check_postdate_leave = Leaves.objects.filter(emp_id=empid, fromdate=postdate).filter(Q(finalstatus__contains='PENDING') | Q(finalstatus__contains='APPROVED')).values('leavecode', 'fhalf', 'leavecode__leave_name')
        if(qry_check_predate_leave.count() > 0 and qry_check_postdate_leave.count() == 0):
            if(qry_check_predate_leave[0]['thalf'] != '1'):
                if(qry_check_predate_leave[0]['thalf'] == 0):
                    prehalf = 'F'
                else:
                    prehalf = 'H'
                qry_check_clubbing_exists = LeaveClub.objects.filter(leave_id1=qry_check_predate_leave[0]['leavecode'], leave_id2=leaveid).filter(Q(day_count1=prehalf, day_count2=fhalf) | Q(day_count1='F', day_count2='F'))

                if(qry_check_clubbing_exists.count() == 0):
                    data.append(False)
                    data.append(qry_check_predate_leave[0]['leavecode__leave_name'])

                    return data
                else:
                    data.append(True)
                    return data

            else:
                data.append(True)
                return data
        elif(qry_check_predate_leave.count() == 0 and qry_check_postdate_leave.count() > 0):
            if(qry_check_postdate_leave[0]['fhalf'] != '2'):

                if(qry_check_postdate_leave[0]['fhalf'] == 1):
                    posthalf = 'H'
                else:
                    posthalf = 'F'
                if(thalf == '0'):
                    thalf = 'F'
                else:
                    thalf = 'H'
                qry_check_clubbing_exists = LeaveClub.objects.filter(leave_id1=leaveid, leave_id2=qry_check_postdate_leave[0]['leavecode']).filter(day_count1=thalf, day_count2=posthalf)
                if(qry_check_clubbing_exists.count() == 0):
                    data.append(False)
                    data.append(qry_check_postdate_leave[0]['leavecode__leave_name'])
                    return data
                else:
                    data.append(True)
                    return data
            else:
                data.append(True)
                return data

        elif(qry_check_predate_leave.count() > 0 and qry_check_postdate_leave.count() > 0):
            if(qry_check_predate_leave[0]['thalf'] != 1 or qry_check_postdate_leave[0]['fhalf'] != 2):
                if(qry_check_predate_leave[0]['thalf'] == 0):
                    prehalf = 'F'
                else:
                    prehalf = 'H'
                if(qry_check_postdate_leave[0]['fhalf'] == 0):
                    posthalf = 'F'
                else:
                    posthalf = 'H'
                if(qry_check_predate_leave.count() > 0):
                    qry_check_clubbing_exists = LeaveClub.objects.filter(leave_id1=qry_check_predate_leave[0]['leavecode'], leave_id2=leaveid).filter(day_count1=prehalf, day_count2=fhalf)
                    if(qry_check_clubbing_exists.count() == 0):
                        data.append(False)
                        data.append(qry_check_predate_leave[0]['leavecode__leave_name'])
                        return data

                if(qry_check_postdate_leave.count() > 0):
                    if(thalf == '0'):
                        thalf = 'F'
                    else:
                        thalf = 'H'
                    qry_check_clubbing_exists = LeaveClub.objects.filter(leave_id1=leaveid, leave_id2=qry_check_postdate_leave[0]['leavecode']).filter(day_count1=thalf, day_count2=posthalf)
                    if(qry_check_clubbing_exists.count() == 0):
                        data.append(False)
                        data.append(qry_check_predate_leave[0]['leavecode__leave_name'])
                        return data
            else:
                data.append(True)
                return data
        else:
            data.append(True)
            return data


def func_leave_quota_check(empid, num_leaves_applied, leave_id):  # check whether leaves are remaining or not ########
    qry_leave_check = Leaveremaning.objects.filter(leaveid=leave_id).filter(empid=empid).values('remaining', 'id').order_by('-id')
    if qry_leave_check[0]['remaining'] >= num_leaves_applied:
        return True
    else:
        return False


def fun_leave_same_dateRange_check(empid, from_date, to_date, from_half, to_half, leaveid):  # check whether leave is already applied in given date range                                                                                                       or not

    day = datetime.timedelta(days=1)
    check = []
    date = from_date
    while date <= to_date:
        qry_leave_check_duplicate = Leaves.objects.filter(emp_id=empid).filter(Q(fromdate__lte=date) & Q(todate__gte=date)).exclude(Q(finalstatus__contains="CANCELLED") | Q(finalstatus__contains="REJECTED")).values('fhalf', 'thalf', 'leavecode', 'leavecode__leave_name', 'fromdate', 'todate')
        if len(qry_leave_check_duplicate) > 0:

            if (fun_leave_hourly(qry_leave_check_duplicate[0]['leavecode'], qry_leave_check_duplicate[0]['fromdate'], qry_leave_check_duplicate[0]['todate'], qry_leave_check_duplicate[0]['fhalf'], qry_leave_check_duplicate[0]['thalf']) or (fun_leave_hourly(leaveid, from_date, to_date, from_half, to_half))):
                check.append(qry_leave_check_duplicate[0]['leavecode__leave_name'])
                check.append(False)
                return check

            if qry_leave_check_duplicate[0]['fhalf'] == '0':
                check.append(qry_leave_check_duplicate[0]['leavecode__leave_name'])
                check.append(False)
                return check
            elif (datetime.datetime.strptime(str(date), '%Y-%m-%d').date() == datetime.datetime.strptime(str(from_date), '%Y-%m-%d').date() or datetime.datetime.strptime(str(date), '%Y-%m-%d').date() == datetime.datetime.strptime(str(to_date), '%Y-%m-%d').date()):
                if (qry_leave_check_duplicate[0]['fhalf'] == from_half or from_half == '0'):
                    check.append(qry_leave_check_duplicate[0]['leavecode__leave_name'])
                    check.append(False)
                    return check
            else:
                check.append(qry_leave_check_duplicate[0]['leavecode__leave_name'])
                check.append(False)
                return check
        date += day
        check.append("No Leave")
        check.append(True)
    return check


def fun_leave_check_validity(empid, from_date, to_date, from_half, to_half):  # check whether attendance is marked in given date range or not ##

    day = datetime.timedelta(days=1)
    day_status = []
    fd = from_date
    while fd <= to_date:
        if fd == from_date:
            if from_half == '0':
                day_status.append(1)  # day_status[]=1 means full day leave        ## day_status[]=0.5 means half day                                                                                leave (FH or SH)
            else:
                day_status.append(0.5)
        elif fd == to_date:
            if to_half == '0':
                day_status.append(1)
            else:
                day_status.append(0.5)
        else:
            day_status.append(1)
        fd += day

    fd = from_date
    i = 0

    while fd <= to_date:
        qry_leave_check = Attendance2.objects.filter(Emp_Id=empid).filter(date=fd).values('status')
        if len(qry_leave_check) > 0:
            status = qry_leave_check[0]['status']
            if status == 'P':
                return False
            else:
                if day_status[i] == 1 and status != 'A' and status != 'H' and status != 'P/A':  # change by nikhil of P/A
                    return False
                else:
                    if fd == from_date:
                        if (status == 'P/1' or status == 'P/I') and from_half != '2':
                            return False
                        elif (status == 'P/2' or status == 'P/II') and from_half != '1':
                            return False
                    elif fd == to_date:
                        if (status == 'P/1' or status == 'P/I') and to_half != '2':
                            return False
                        elif (status == 'P/2' or status == 'P/II') and to_half != '1':
                            return False

        fd += day
        i += 1

    return True


def fun_num_of_leaves(from_date, to_date, from_half, to_half):  # return number  of leaves in given range #############

    day = datetime.timedelta(days=1)

    num_of_leaves = 0
    fd = from_date
    while fd <= to_date:
        if fd == from_date:
            if from_half == '0':
                num_of_leaves += 1  # day_status[]=1 means full day leave        ## day_status[]=0.5 means half day leave (FH or SH)
            else:
                num_of_leaves += 0.5
        elif fd == to_date:
            if to_half == '0':
                num_of_leaves += 1
            else:
                num_of_leaves += 0.5
        else:
            num_of_leaves += 1
        fd += day

    return num_of_leaves


def fun_leave_hourly(leaveid, from_date, to_date, from_half, to_half):  # check whether leave is hourly or not ######3

    leave_details = LeaveType.objects.filter(id=leaveid).values('hours_leave')
    if leave_details[0]['hours_leave'] == 'Y':
        if (from_date != to_date) or (from_half == '0' or to_half == '0') or (from_half != to_half):
            return False
        else:
            return True
    elif leave_details[0]['hours_leave'] == 'N':
        return False
    return False


def check_leave_after_lapse(from_date, to_date, leaveid):

    check = []
    leave_details = LeaveType.objects.filter(id=leaveid, leave_status='L').values('lapse_start', 'lapse_month', 'credit_day')
    if len(leave_details) > 0:
        if from_date >= leave_details[0]['lapse_start'] or to_date >= leave_details[0]['lapse_start']:
            return False

        lapse_date2 = leave_details[0]['credit_day'] - relativedelta(months=+leave_details[0]['lapse_month'])
        if from_date < lapse_date2:
            return False
    return True


def check_el(fhalf, thalf, leaveid):
    qry_od_id = LeaveType.objects.filter(leave_abbr='EL').values('id')
    lid = qry_od_id[0]['id']

    if lid == leaveid and (fhalf == '1' or (fhalf == '2' and thalf == '2')):
        return False

    return True


def check_cl_co_comb(fhalf, thalf, from_date, to_date, leaveid, num_of_leaves, empid):
    data = []
    days = datetime.timedelta(days=3)
    day = datetime.timedelta(days=1)

    from_date2 = from_date - days
    to_date2 = to_date + days

    qry_cl_id = LeaveType.objects.filter(leave_abbr='CL').values('id')
    clid = qry_cl_id[0]['id']

    qry_co_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
    coid = qry_co_id[0]['id']

    filter_lid = [clid, coid]

    if leaveid in filter_lid and num_of_leaves > 3:
        data.append(False)
        data.append("Casual and Compensatory leave cannot be applied for more than 3 days!")
        return data

    if leaveid not in filter_lid:
        data.append(True)
        return data

    num_of_days = num_of_leaves
    if fhalf == '2':
        qry_lv = Leaves.objects.filter(emp_id=empid).filter(Q(fromdate__lte=from_date) & Q(todate__gte=from_date)).filter(leavecode__in=filter_lid).exclude(Q(finalstatus__contains="CANCELLED") | Q(finalstatus__contains="REJECTED")).values('fhalf', 'thalf', 'leavecode', 'leavecode__leave_name', 'fromdate', 'todate', 'days')
        for q in qry_lv:
            num_of_days += q['days']

        if len(qry_lv) == 0:
            data.append(True)
            return data

    date = from_date - day
    while date >= from_date2:
        qry_lv = Leaves.objects.filter(emp_id=empid).filter(Q(fromdate__lte=date) & Q(todate__gte=date)).filter(leavecode__in=filter_lid).exclude(Q(finalstatus__contains="CANCELLED") | Q(finalstatus__contains="REJECTED")).values('fhalf', 'thalf', 'leavecode', 'leavecode__leave_name', 'fromdate', 'todate', 'days')
        if len(qry_lv) > 0:
            for q in qry_lv.reverse():
                num_of_days += q['days']
                date = datetime.datetime.strptime((str(q['fromdate']).split(" "))[0], '%Y-%m-%d').date()
        else:
            break
        date -= day

    if num_of_days > 3:
        data.append(False)
        data.append("Casual and Compensatory leave cannot be applied for more than 3 days!")
        return data

    if from_date != to_date or thalf == '1':
        qry_lv = Leaves.objects.filter(emp_id=empid).filter(Q(fromdate__lte=to_date) & Q(todate__gte=to_date)).filter(leavecode__in=filter_lid).exclude(Q(finalstatus__contains="CANCELLED") | Q(finalstatus__contains="REJECTED")).values('fhalf', 'thalf', 'leavecode', 'leavecode__leave_name', 'fromdate', 'todate', 'days')
        for q in qry_lv:
            num_of_days += q['days']

        if len(qry_lv) == 0:
            data.append(True)
            return data

    date = to_date + day
    while date <= to_date2:
        qry_lv = Leaves.objects.filter(emp_id=empid).filter(Q(fromdate__lte=date) & Q(todate__gte=date)).filter(leavecode__in=filter_lid).exclude(Q(finalstatus__contains="CANCELLED") | Q(finalstatus__contains="REJECTED")).values('fhalf', 'thalf', 'leavecode', 'leavecode__leave_name', 'fromdate', 'todate', 'days')
        if len(qry_lv) > 0:
            for q in qry_lv:
                num_of_days += q['days']
                date = datetime.datetime.strptime((str(q['todate']).split(" "))[0], '%Y-%m-%d').date()
        else:
            break

        date += day

    if num_of_days > 3:
        data.append(False)
        data.append("Casual and Compensatory leave cannot be applied for more than 3 days!")
        return data

    data.append(True)
    return data


def mark_normal_leave_admin(request):
    status = None
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337, 211, 404])
            if check == 200:
                if request.method == 'POST':
                    data = json.loads(request.body)
                    # accounts days arrear ############3
                    arrear_leave = False
                    if 'request_type' in data:
                        if data['request_type'] == "arrear_leave":
                            arrear_leave = True

                    from_date = datetime.datetime.strptime(data['f_date'], '%Y-%m-%d').date()
                    to_date = datetime.datetime.strptime(data['t_date'], '%Y-%m-%d').date()

                    num_of_leaves = fun_num_of_leaves(from_date, to_date, data['fromHalf'], data['toHalf'])

                    check2 = Leave_HalfCheck(from_date, to_date, data['fromHalf'], data['toHalf'])
                    check3 = fun_leave_same_dateRange_check(data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'], data['leaveid'])
                    check4 = fun_leave_check_validity(data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    # check5=fun_leave_hourly(data['leaveid'],from_date,to_date,data['fromHalf'],data['toHalf'])
                    check6 = Leave_ClubCheck(data['leaveid'], data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    check7 = check_leave_after_lapse(from_date, to_date, data['leaveid'])
                    check8 = check_el(data['fromHalf'], data['toHalf'], data['leaveid'])
                    check9 = check_cl_co_comb(data['fromHalf'], data['toHalf'], from_date, to_date, data['leaveid'], num_of_leaves, data['emp_code'])

                    check10 = True
                    if fun_leave_hourly(data['leaveid'], from_date, to_date, data['fromHalf'], data['toHalf']):
                        today = date.today()
                        if from_date != today:
                            qry_att = Attendance2.objects.filter(date=from_date).filter(Emp_Id=data['emp_code']).values('status')
                            if len(qry_att) > 0:
                                resp = checkhourlyvalid(data['emp_code'], data['leaveid'], from_date, qry_att[0]['status'])
                                if resp == 3:
                                    check10 = False

                    if arrear_leave == False:
                        check11 = check_month_locked(from_date, to_date)
                    else:
                        check11 = False

                    if(check2 == False):
                        msg = "Half Combination Not Allowed!"
                    elif(check3[1] == False):
                        msg = check3[0] + " Already Applied in selected Date Range!"
                    elif(check4 == False):
                        msg = "Attendance Already Marked for applied Days!"
                    elif(check6[0] == False):
                        msg = check6[1] + " and Applied cannot be Clubbed!"
                    elif check7 == False:
                        msg = "Leave Quota is not defined for the applied date range"
                    elif check8 == False:
                        msg = "Earned Leave cannot be applied for 0.5 days"
                    elif check9[0] == False:
                        msg = check9[1]
                    elif check10 == False:
                        msg = "Working hours are less than total hours after applying SHL"
                    elif check11 == True:
                        msg = "Payable days has been locked for this month."

                    elif(check2 and check3[1] and check4 and check6[0] and check7 and check8 and check9[0] and check10 and not check11):
                        if func_leave_quota_check(data['emp_code'], num_of_leaves, data['leaveid']):
                            status = 200
                            msg = "Leave Successfully Applied"

                            if arrear_leave == False:
                                ############ insert into leaves table ############

                                qry_ins = Leaves.objects.create(requestdate=(date.today()), fromdate=(data['f_date']), todate=(data['t_date']), days=num_of_leaves, reason=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), finalstatus='APPROVED BY ADMIN', finalapprovaldate=date.today(), leavecode=LeaveType.objects.get(id=data['leaveid']))

                                ############ update leaves remaining ##############

                                leaves_rem = Leaveremaning.objects.filter(empid=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), leaveid=LeaveType.objects.get(id=data['leaveid'])).extra(select={'remaining': 'Remaining'}).values('remaining')
                                final_leaves_rem = leaves_rem[0]['remaining'] - num_of_leaves

                                qry_quota_update = Leaveremaning.objects.filter(empid=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), leaveid=LeaveType.objects.get(id=data['leaveid'])).update(remaining=final_leaves_rem)

                                leave_id = Leaves.objects.values('leaveid').order_by('-leaveid')[:1]

                                qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept', 'desg')

                                ########## insert first reporting in leave approval with status APPROVED BY ADMIN ###########

                                flag = 0
                                while flag != 1:
                                    qry_leave_approval = Leaveapproval.objects.create(status="APPROVED BY ADMIN", approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), reportinglevel=-1, leaveid=Leaves.objects.get(leaveid=leave_id), remark=data['reason'], approved_by=request.session['hash1'], dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

                                    qry_c = Leaveapproval.objects.filter(reportinglevel=-1, dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']), leaveid=Leaves.objects.get(leaveid=leave_id))

                                    if len(qry_c) > 0:
                                        flag = 1
                                        break

                                q_lv = Leaves.objects.filter(leaveid=leave_id).values('fromdate', 'todate', 'days', 'emp_id', 'emp_id__name', 'emp_id__email')

                                message2 = 'Dear ' + q_lv[0]['emp_id__name'] + ' (' + q_lv[0]['emp_id'] + ') ' + ',<br><br>Your leave request has been APPLIED BY ADMIN.<br><br>From Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['fromdate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '<br><br>To Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['todate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(q_lv[0]['days']) + ' Day(s).<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                                subject2 = "Leave APPLIED BY ADMIN | " + q_lv[0]['emp_id__name'] + " (" + q_lv[0]['emp_id'] + ")" + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                                mail2 = q_lv[0]['emp_id__email']

                                Thread(target=store_email, args=[mail2, subject2, message2]).start()

                            else:

                                actual_days = calendar.monthrange(from_date.year, to_date.month)[1]
                                emp_id = data['emp_code']

                                qry_check_sign = Sign_In_Out_Arrear.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), date__range=[data['f_date'], data['t_date']]).values('status', 'date')
                                for qc in qry_check_sign:
                                    if (qc['date'] == from_date) and (qc['status'] == 0 or qc['status'] == data['fromHalf'] or data['fromHalf'] == 0):
                                        status = 409
                                        msg = "Sign In/Out Arrear has already been applied for the date selected"
                                    elif (qc['date'] == to_date) and (qc['status'] == 0 or qc['status'] == data['toHalf'] or data['toHalf'] == 0):
                                        status = 409
                                        msg = "Sign In/Out Arrear has already been applied for the date selected"
                                    elif qc['date'] != from_date and qc['date'] != to_date:
                                        status = 409
                                        msg = "Sign In/Out Arrear has already been applied for the date selected"

                                if status == 200:
                                    session = acc.views.getCurrentSession(None)
                                    salary_month = acc.views.getSalaryMonth(session)
                                    ########## insert into Accounts_Days_Arrear_Leaves table #############
                                    qry_ins = Days_Arrear_Leaves.objects.create(requestdate=(date.today()), fromdate=(data['f_date']), todate=(data['t_date']), days=actual_days, hr_remark=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), hr_status='APPROVED BY ADMIN', leavecode=LeaveType.objects.get(id=data['leaveid']), working_days=num_of_leaves, session=AccountsSession.objects.get(id=session), month=salary_month, finalapprovaldate=date.today())

                                    ############ update leaves remaining ##############

                                    leaves_rem = Leaveremaning.objects.filter(empid=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), leaveid=LeaveType.objects.get(id=data['leaveid'])).extra(select={'remaining': 'Remaining'}).values('remaining')
                                    final_leaves_rem = leaves_rem[0]['remaining'] - num_of_leaves

                                    qry_quota_update = Leaveremaning.objects.filter(empid=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), leaveid=LeaveType.objects.get(id=data['leaveid'])).update(remaining=final_leaves_rem)

                        else:
                            status = 409
                    else:
                        status = 409
                else:
                    status = 502
                    msg = ""
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"

    data = {'msg': msg, 'status': status}
    return JsonResponse(data=data)


def mark_od_leave_admin(request):
    status = None
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337, 211, 404])
            if check == 200:
                if request.method == 'POST':

                    data = json.loads(request.body)
                    status = 200
                    msg = "Leave Successfully Applied"

                    # accounts days arrear ############3
                    arrear_leave = False
                    if 'request_type' in data:
                        if data['request_type'] == "arrear_leave":
                            arrear_leave = True

                    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')
                    leaveid = qry_od_id[0]['id']

                    from_date = datetime.datetime.strptime(data['f_date'], '%Y-%m-%d').date()
                    to_date = datetime.datetime.strptime(data['t_date'], '%Y-%m-%d').date()

                    check2 = Leave_HalfCheck(from_date, to_date, data['fromHalf'], data['toHalf'])
                    check3 = fun_leave_same_dateRange_check(data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'], leaveid)
                    check4 = fun_leave_check_validity(data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    # check5=fun_leave_hourly(leaveid,from_date,to_date,data['fromHalf'],data['toHalf'])
                    check6 = Leave_ClubCheck(leaveid, data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'])

                    if arrear_leave == False:
                        check11 = check_month_locked(from_date, to_date)
                    else:
                        check11 = False
                    if(check2 == False):
                        msg = "Half Combination Not Allowed!"
                    elif(check3[1] == False):
                        msg = check3[0] + " Already Applied in selected Date Range!"
                    elif(check4 == False):
                        msg = "Attendance Already Marked for applied Days!"
                    elif(check6[0] == False):
                        msg = check6[1] + " and Applied leave cannot be Clubbed!"
                    elif check11 == True:
                        msg = "Payable days has been locked for this month."
                    # elif(check5==False):
                    #   msg="Leave Applied is not Hourly!"

                    elif(check2 and check3[1] and check4 and check6[0] and not check11):
                        num_of_leaves = fun_num_of_leaves(from_date, to_date, data['fromHalf'], data['toHalf'])

                        if arrear_leave == False:
                            ############ insert into leaves table ############

                            qry_ins = Leaves.objects.create(requestdate=(date.today()), fromdate=(data['f_date']), todate=(data['t_date']), days=num_of_leaves, reason=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), finalstatus='APPROVED BY ADMIN', finalapprovaldate=date.today(), leavecode=LeaveType.objects.get(id=leaveid), category=EmployeeDropdown.objects.get(sno=data['Cat']), subtype=EmployeeDropdown.objects.get(sno=data['SubCat']), filename=data['file_name'])

                            leave_id = Leaves.objects.values('leaveid').order_by('-leaveid')[:1]

                            qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept', 'desg')

                            ########## insert first reporting in leave approval with status APPROVED BY ADMIN ###########
                            flag = 0
                            while flag != 1:
                                qry_leave_approval = Leaveapproval.objects.create(status="APPROVED BY ADMIN", approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), reportinglevel=-1, leaveid=Leaves.objects.get(leaveid=leave_id), remark=data['reason'], approved_by=request.session['hash1'], dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

                                qry_c = Leaveapproval.objects.filter(reportinglevel=-1, dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']), leaveid=Leaves.objects.get(leaveid=leave_id))

                                if len(qry_c) > 0:
                                    flag = 1
                                    break

                            q_lv = Leaves.objects.filter(leaveid=leave_id).values('fromdate', 'todate', 'days', 'emp_id', 'emp_id__name', 'emp_id__email')

                            message2 = 'Dear ' + q_lv[0]['emp_id__name'] + ' (' + q_lv[0]['emp_id'] + ') ' + ',<br><br>Your leave request has been APPLIED BY ADMIN.<br><br>From Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['fromdate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '<br><br>To Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['todate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(q_lv[0]['days']) + ' Day(s).<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                            subject2 = "Leave APPLIED BY ADMIN | " + q_lv[0]['emp_id__name'] + " (" + q_lv[0]['emp_id'] + ")" + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                            mail2 = q_lv[0]['emp_id__email']

                            Thread(target=store_email, args=[mail2, subject2, message2]).start()

                        else:
                            actual_days = calendar.monthrange(from_date.year, to_date.month)[1]
                            emp_id = data['emp_code']

                            qry_check_sign = Sign_In_Out_Arrear.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), date__range=[data['f_date'], data['t_date']]).values('status', 'date')
                            for qc in qry_check_sign:
                                if (qc['date'] == from_date) and (qc['status'] == 0 or qc['status'] == data['fromHalf'] or data['fromHalf'] == 0):
                                    status = 409
                                    msg = "Sign In/Out Arrear has already been applied for the date selected"
                                elif (qc['date'] == to_date) and (qc['status'] == 0 or qc['status'] == data['toHalf'] or data['toHalf'] == 0):
                                    status = 409
                                    msg = "Sign In/Out Arrear has already been applied for the date selected"
                                elif qc['date'] != from_date and qc['date'] != to_date:
                                    status = 409
                                    msg = "Sign In/Out Arrear has already been applied for the date selected"

                            if status == 200:
                                session = acc.views.getCurrentSession(None)
                                salary_month = acc.views.getSalaryMonth(session)
                                qry_ins = Days_Arrear_Leaves.objects.create(requestdate=(date.today()), fromdate=(data['f_date']), todate=(data['t_date']), days=actual_days, hr_remark=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), hr_status='APPROVED BY ADMIN', leavecode=LeaveType.objects.get(id=leaveid), category=EmployeeDropdown.objects.get(sno=data['Cat']), subtype=EmployeeDropdown.objects.get(sno=data['SubCat']), filename=data['file_name'], working_days=num_of_leaves, session=AccountsSession.objects.get(id=session), month=salary_month, finalapprovaldate=date.today())

                    else:
                        status = 409
                        msg = "Wrongly selected leave"
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data = {'msg': msg, 'status': status}
    return JsonResponse(data=data)


def mark_normal_leave_employee(request):
    status = None
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'POST':
                    data = json.loads(request.body)

                    reporting_levels = []
                    print(data['f_date'])
                    from_date = datetime.datetime.strptime(data['f_date'].split('T')[0], '%Y-%m-%d').date()
                    to_date = datetime.datetime.strptime(data['t_date'].split('T')[0], '%Y-%m-%d').date()
                    print(from_date,to_date)
                    # utc_tz = pytz.timezone('UTC')
                    # from_date_utc = utc_tz.localize(datetime.datetime.strptime(data['f_date'], "%Y-%m-%d"))
                    # to_date_utc = utc_tz.localize(datetime.datetime.strptime(data['t_date'], "%Y-%m-%d"))
                    num_of_leaves = fun_num_of_leaves(from_date, to_date, data['fromHalf'], data['toHalf'])

                    qry_dept = EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('dept', 'desg', 'email', 'name')
                    check1 = Leave_DayLimit(from_date, qry_dept[0]['dept'], data['leaveid'], request.session['hash1'])
                    check2 = Leave_HalfCheck(from_date, to_date, data['fromHalf'], data['toHalf'])
                    check3 = fun_leave_same_dateRange_check(request.session['hash1'], from_date, to_date, data['fromHalf'], data['toHalf'], data['leaveid'])
                    check4 = fun_leave_check_validity(request.session['hash1'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    # check5=fun_leave_hourly(data['leaveid'],from_date,to_date,data['fromHalf'],data['toHalf'])
                    check6 = Leave_ClubCheck(data['leaveid'], request.session['hash1'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    check7 = check_leave_after_lapse(from_date, to_date, data['leaveid'])
                    check8 = check_el(data['fromHalf'], data['toHalf'], data['leaveid'])
                    check9 = check_cl_co_comb(data['fromHalf'], data['toHalf'], from_date, to_date, data['leaveid'], num_of_leaves, request.session['hash1'])

                    check10 = True
                    if fun_leave_hourly(data['leaveid'], from_date, to_date, data['fromHalf'], data['toHalf']):
                        today = date.today()
                        if from_date != today:
                            qry_att = Attendance2.objects.filter(date=from_date).filter(Emp_Id=request.session['hash1']).values('status')
                            if len(qry_att) > 0:
                                resp = checkhourlyvalid(request.session['hash1'], data['leaveid'], from_date, qry_att[0]['status'])
                                if resp == 3:
                                    check10 = False
                    check11 = check_month_locked(from_date, to_date)
                    if(check1 == False):
                        msg = "Apply Daylimit exceeded!"
                    elif(check2 == False):
                        msg = "Half Combination Not Allowed!"
                    elif(check3[1] == False):
                        msg = check3[0] + " Already Applied in selected Date Range!"
                    elif(check4 == False):
                        msg = "Attendance Already Marked for applied Days!"
                    elif(check6[0] == False):
                        msg = check6[1] + " and Applied leave cannot be Clubbed!"
                    elif check7 == False:
                        msg = "Leave Quota is not defined for the applied date range"
                    elif check8 == False:
                        msg = "Earned Leave cannot be applied for 0.5 days"
                    elif check9[0] == False:
                        msg = check9[1]
                    elif check10 == False:
                        msg = "Working hours are less than total hours after applying SHL"
                    elif check11 == True:
                        msg = "Payable days has been locked for this month."
                    elif(check1 and check2 and check3[1] and check4 and check6[0] and check7 and check8 and check9[0] and check10 and not check11):
                        if func_leave_quota_check(request.session['hash1'], num_of_leaves, data['leaveid']):

                            ######### insert in leaves table ###########
                            # print(parse(data['f_date']))
                            # utc_tz = pytz.timezone('UTC')
                            # from_date_utc = utc_tz.localize(datetime.datetime.strptime(data['f_date'], "%Y-%m-%d"))
                            # to_date_utc = utc_tz.localize(datetime.datetime.strptime(data['t_date'], "%Y-%m-%d"))
                            qry_ins = Leaves.objects.create(requestdate=(date.today()), fromdate=from_date, todate=to_date, days=num_of_leaves, reason=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), finalstatus='PENDING', finalapprovaldate=None, leavecode=LeaveType.objects.get(id=data['leaveid']), filename=data['file_name'])

                            ################ update leaves remaining ##########################

                            leaves_rem = Leaveremaning.objects.filter(empid=EmployeePrimdetail.objects.get(emp_id=str(request.session['hash1'])), leaveid=LeaveType.objects.get(id=data['leaveid'])).extra(select={'remaining': 'Remaining'}).values('remaining')
                            final_leaves_rem = leaves_rem[0]['remaining'] - num_of_leaves
                            qry_quota_update = Leaveremaning.objects.filter(empid=EmployeePrimdetail.objects.get(emp_id=str(request.session['hash1'])), leaveid=LeaveType.objects.get(id=data['leaveid'])).update(remaining=final_leaves_rem)

                            leave_id = Leaves.objects.values('leaveid').order_by('-leaveid')[:1]

                            report = find_reporting_levels(request.session['hash1'])
                            reporting_levels = report['rep_level']

                            if(len(reporting_levels) != 0):
                                reporting = reporting_levels[0]
                            else:
                                reporting = 0

                            ########## insert first reporting in leave approval with status PENDING ###########
                            flag = 0
                            while flag != 1:
                                qry_leave_approval = Leaveapproval.objects.create(status="PENDING", approvaldate=None, reportinglevel=reporting, dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), leaveid=Leaves.objects.get(leaveid=leave_id))

                                qry_c = Leaveapproval.objects.filter(reportinglevel=reporting, dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), leaveid=Leaves.objects.get(leaveid=leave_id))
                                if len(qry_c) > 0:
                                    flag = 1
                                    break

                            ############# send email ##################
                            qry_leave_details = LeaveType.objects.filter(id=data['leaveid']).values('leave_name', 'leave_abbr')
                            qry_rep_email = EmployeePrimdetail.objects.filter(dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), emp_status="ACTIVE").values('email', 'name', 'desg__value')

                            if data['fromHalf'] == '0':
                                fhalf = 'Full Day'
                            elif data['fromHalf'] == '1':
                                fhalf = 'First Half'
                            elif data['fromHalf'] == '2':
                                fhalf = 'Second Half'

                            if data['toHalf'] == '0':
                                thalf = 'Full Day'
                            elif data['toHalf'] == '1':
                                thalf = 'First Half'
                            elif data['toHalf'] == '2':
                                thalf = 'Second Half'

                            message1 = 'Dear ' + qry_dept[0]['name'] + ',<br><br>You have applied ' + qry_leave_details[0]['leave_name'] + ' (' + qry_leave_details[0]['leave_abbr'] + ')' + ' from ' + str(datetime.datetime.strptime(str(data['f_date'].split('T')[0]), "%Y-%m-%d").strftime("%d-%b-%Y")) + ' till ' + str(datetime.datetime.strptime(str(data['t_date'].split('T')[0]), "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(num_of_leaves) + ' Day(s).<br><br>Purpose - ' + data['reason'] + '<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                            subject1 = "Leave Request | " + qry_leave_details[0]['leave_name'] + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                            mail1 = qry_dept[0]['email']

                            Thread(target=store_email, args=[mail1, subject1, message1]).start()

                            status = 200
                            msg = "Leave Successfully Applied"
                        else:
                            status = 409
                            msg = "Wrongly selected leave"
                    else:
                        status = 409
                        msg = "Wrongly selected leave"
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data = {'msg': msg, 'status': status}
    return JsonResponse(data=data)


def mark_od_leave_employee(request):
    status = None
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'POST':

                    data = json.loads(request.body)
                    reporting_levels = []
                    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')
                    leaveid = qry_od_id[0]['id']

                    from_date = datetime.datetime.strptime(data['f_date'], '%Y-%m-%d').date()
                    to_date = datetime.datetime.strptime(data['t_date'], '%Y-%m-%d').date()

                    qry_dept = EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('dept', 'desg', 'name', 'email')
                    check1 = Leave_DayLimit(from_date, qry_dept[0]['dept'], leaveid, request.session['hash1'])
                    check2 = Leave_HalfCheck(from_date, to_date, data['fromHalf'], data['toHalf'])
                    check3 = fun_leave_same_dateRange_check(request.session['hash1'], from_date, to_date, data['fromHalf'], data['toHalf'], leaveid)
                    check4 = fun_leave_check_validity(request.session['hash1'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    check6 = Leave_ClubCheck(leaveid, request.session['hash1'], from_date, to_date, data['fromHalf'], data['toHalf'])

                    check11 = check_month_locked(from_date, to_date)
                    if(check1 == False):
                        msg = "Apply Daylimit ecxeeded!"
                    elif(check2 == False):
                        msg = "Half Combination Not Allowed!"
                    elif(check3[1] == False):
                        msg = check3[0] + " Already Applied in selected Date Range!"
                    elif(check4 == False):
                        msg = "Attendance Already Marked for applied Days!"
                    elif(check6[0] == False):
                        msg = check6[1] + " and Applied leave cannot be Clubbed!"
                    elif check11 == True:
                        msg = "Payable days has been locked for this month."
                    elif(check1 and check2 and check3[1] and check4 and check6[0] and not check11):
                        num_of_leaves = fun_num_of_leaves(from_date, to_date, data['fromHalf'], data['toHalf'])

                        ######### insert in leaves table ###########

                        qry_ins = Leaves.objects.create(requestdate=(date.today()), fromdate=(data['f_date']), todate=(data['t_date']), days=num_of_leaves, reason=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), finalstatus='PENDING', finalapprovaldate=None, leavecode=LeaveType.objects.get(id=leaveid), category=EmployeeDropdown.objects.get(sno=data['Cat']), subtype=EmployeeDropdown.objects.get(sno=data['SubCat']), filename=data['file_name'])

                        leave_id = Leaves.objects.values('leaveid').order_by('-leaveid')[:1]

                        qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept', 'desg')
                        report = find_reporting_levels(request.session['hash1'])
                        reporting_levels = report['rep_level']
                        if(len(reporting_levels) != 0):
                            reporting = reporting_levels[0]
                        else:
                            reporting = 0

                        ########## insert first reporting in leave approval with status PENDING ###########

                        flag = 0
                        while flag != 1:
                            qry_leave_approval = Leaveapproval.objects.create(status="PENDING", approvaldate=None, reportinglevel=reporting, dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), leaveid=Leaves.objects.get(leaveid=leave_id))

                            qry_c = Leaveapproval.objects.filter(reportinglevel=reporting, dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), leaveid=Leaves.objects.get(leaveid=leave_id))
                            if len(qry_c) > 0:
                                flag = 1
                                break

                        ############# send email ##################
                        qry_leave_details = LeaveType.objects.filter(id=leaveid).values('leave_name', 'leave_abbr')
                        qry_rep_email = EmployeePrimdetail.objects.filter(dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), emp_status="ACTIVE").values('email', 'name', 'desg__value')

                        if data['fromHalf'] == '0':
                            fhalf = 'Full Day'
                        elif data['fromHalf'] == '1':
                            fhalf = 'First Half'
                        elif data['fromHalf'] == '2':
                            fhalf = 'Second Half'

                        if data['toHalf'] == '0':
                            thalf = 'Full Day'
                        elif data['toHalf'] == '1':
                            thalf = 'First Half'
                        elif data['toHalf'] == '2':
                            thalf = 'Second Half'

                        message1 = 'Dear ' + qry_dept[0]['name'] + ',<br><br>You have applied ' + qry_leave_details[0]['leave_name'] + ' (' + qry_leave_details[0]['leave_abbr'] + ')' + ' from ' + str(datetime.datetime.strptime(str(data['f_date']), "%Y-%m-%d").strftime("%d-%b-%Y")) + ' till ' + str(datetime.datetime.strptime(str(data['t_date']), "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(num_of_leaves) + ' Day(s).<br><br>Purpose - ' + data['reason'] + '<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                        subject1 = "Leave Request | " + qry_leave_details[0]['leave_name'] + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                        mail1 = qry_dept[0]['email']

                        Thread(target=store_email, args=[mail1, subject1, message1]).start()

                        status = 200
                        msg = "Leave Successfully Applied"

                    else:
                        status = 409
                        msg = "Wrongly selected leave"
                else:
                    status = 403
                    msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data = {'msg': msg, 'status': status}
    return JsonResponse(data=data)


def comp_off_data_admin(request):
    msg = ""
    data = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.method == 'GET':
                if(request.GET['request_type'] == 'admin'):
                    check = checkpermission(request, [337, 211])
                    a = 1
                if(request.GET['request_type'] == 'employee'):
                    check = checkpermission(request, [337])
                    a = 0
                if check == 200:
                    if(a == 1):
                        empid = request.GET['emp_code']
                    else:
                        empid = request.session['hash1']
                    qry_dept = EmployeePrimdetail.objects.filter(emp_id=str(empid)).values('dept')
                    to_date = date.today()

                    # check extra work hours on holiday in last 3 months ##########3

                    from_date = date.today() - relativedelta(months=+3)

                    qry_co_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
                    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')

                    half_hours_limit = EmployeeDropdown.objects.filter(field="HALF DAY").exclude(value__isnull=True).values('value')
                    full_hours_limit = EmployeeDropdown.objects.filter(field="FULL DAY").exclude(value__isnull=True).values('value')

                    extra = datetime.datetime.strptime(half_hours_limit[0]['value'], '%H:%M:%S').time()
                    qry_attendance = Attendance2.objects.filter(Q(date__gte=from_date) & Q(date__lte=to_date)).filter(extra__gte=extra).filter(Emp_Id=empid, is_compoff=1).values('extra', 'date')
                    for att in qry_attendance:
                        qry_check = Leaves.objects.filter(extraworkdate__contains=str(att['date'])).filter(leavecode=qry_co_id[0]['id']).filter(emp_id=empid).exclude(Q(finalstatus__contains='CANCELLED') | Q(finalstatus__contains='REJECTED')).values('leaveid')  # change of rejection is done by nikhil
                        # arrear leave #########333
                        qry_check2 = Days_Arrear_Leaves.objects.filter(extraworkdate__contains=str(att['date'])).filter(leavecode=qry_co_id[0]['id']).filter(emp_id=empid).exclude(Q(hr_status__contains='CANCELLED') | Q(hr_status__contains='REJECTED')).values('leaveid')

                        qry_check_holiday = Holiday.objects.filter(Q(f_date__lte=att['date']) & Q(t_date__gte=att['date'])).filter(dept=EmployeeDropdown.objects.get(sno=qry_dept[0]['dept']), status='INSERT').filter(restricted='Y').values('id')

                        ##################### if selected extra work date is not already used and there is not restricted holiday on that day #######

                        if len(qry_check) == 0 and len(qry_check2) == 0 and len(qry_check_holiday) == 0:
                            data.append({'date': str(att['date']), 'extra': str(att['extra'])})

                    ##################### check for od leaves applied in last 3 months ############################
                    qry_check_od = Leaves.objects.filter(leavecode=qry_od_id[0]['id']).filter(emp_id=empid, finalstatus__contains='APPROVED').filter(Q(fromdate__gte=from_date) & Q(fromdate__lte=to_date) & Q(todate__gte=from_date) & Q(todate__lte=to_date)).values('fromdate', 'todate', 'fhalf', 'thalf', 'subtype', 'category')
                    for ch in qry_check_od:

                        q_od = OdCategoryUpload.objects.filter(sub_category=EmployeeDropdown.objects.get(sno=ch['subtype']), category=EmployeeDropdown.objects.get(sno=ch['category']), is_compoff=1)
                        if len(q_od) > 0:
                            fd = (str(ch['fromdate']).split(' '))[0]
                            td = (str(ch['todate']).split(' '))[0]

                            fd = datetime.datetime.strptime(fd, '%Y-%m-%d').date()
                            td = datetime.datetime.strptime(td, '%Y-%m-%d').date()

                            day_inc = datetime.timedelta(days=1)

                            dat = fd
                            while dat <= td:

                                qry_check = Leaves.objects.filter(extraworkdate__contains=str(dat)).filter(leavecode=qry_co_id[0]['id']).filter(emp_id=empid).exclude(Q(finalstatus__contains='CANCELLED') | Q(finalstatus__contains='REJECTED')).values('leaveid')
                                # if od is already used, then skip it

                                if len(qry_check) > 0:
                                    dat += day_inc
                                    continue

                                ######################## arrear leave ###################################

                                qry_check2 = Days_Arrear_Leaves.objects.filter(extraworkdate__contains=str(dat)).filter(leavecode=qry_co_id[0]['id']).filter(emp_id=empid).exclude(Q(hr_status__contains='CANCELLED') | Q(hr_status__contains='REJECTED')).values('leaveid')
                                # if od is already used, then skip it

                                if len(qry_check2) > 0:
                                    dat += day_inc
                                    continue

                                # check for restricted holiday #########################333

                                qry_check_holiday = Holiday.objects.filter(Q(f_date__lte=dat) & Q(t_date__gte=dat)).filter(dept=EmployeeDropdown.objects.get(sno=qry_dept[0]['dept']), status='INSERT').values('id', 'restricted')

                                qry_attendance = Attendance2.objects.filter(date=fd).filter(extra__gte=extra).filter(Emp_Id=empid).values('extra')
                                att_extra_hrs = datetime.datetime.strptime('00:00:00', '%H:%M:%S').time()

                                # get extra work hours of that od leave day range > 00:00:00 ###########33

                                if len(qry_attendance) > 0:
                                    att_extra_hrs = datetime.datetime.strptime(str(qry_attendance[0]['extra']), '%H:%M:%S').time()

                                leave_extra_hrs = datetime.datetime.strptime('00:00:00', '%H:%M:%S').time()
                                if len(qry_check_holiday) > 0 and qry_check_holiday[0]['restricted'] == 'N':

                                    if dat == fd:
                                        if ch['fhalf'] != '0':
                                            leave_extra_hrs = datetime.datetime.strptime(half_hours_limit[0]['value'], '%H:%M:%S').time()
                                        else:
                                            leave_extra_hrs = datetime.datetime.strptime(full_hours_limit[0]['value'], '%H:%M:%S').time()
                                    elif dat == td:
                                        if ch['fhalf'] != '0':
                                            leave_extra_hrs = datetime.datetime.strptime(half_hours_limit[0]['value'], '%H:%M:%S').time()
                                        else:
                                            leave_extra_hrs = datetime.datetime.strptime(full_hours_limit[0]['value'], '%H:%M:%S').time()
                                    else:
                                        leave_extra_hrs = datetime.datetime.strptime(full_hours_limit[0]['value'], '%H:%M:%S').time()

                                    ############# if attendance extra work hours is more than od work hours then use attendance extra work hours ######

                                    ##### example:- if  attendance extra work hours generated full day compoff whereas od generates half day compoff then give preference to more one #######################

                                    data.append({'date': str(datetime.datetime.strptime(((str(dat)).split(' '))[0], '%Y-%m-%d').date()), 'extra': str(max(leave_extra_hrs, att_extra_hrs))})

                                dat += day_inc

                    ##################### check for arrear od leaves applied in last 3 months ############################
                    qry_check_od = Days_Arrear_Leaves.objects.filter(leavecode=qry_od_id[0]['id']).filter(emp_id=empid, hr_status__contains='APPROVED').filter(Q(fromdate__gte=from_date) & Q(fromdate__lte=to_date) & Q(todate__gte=from_date) & Q(todate__lte=to_date)).values('fromdate', 'todate', 'fhalf', 'thalf', 'subtype', 'category')
                    for ch in qry_check_od:

                        q_od = OdCategoryUpload.objects.filter(sub_category=EmployeeDropdown.objects.get(sno=ch['subtype']), category=EmployeeDropdown.objects.get(sno=ch['category']), is_compoff=1)
                        if len(q_od) > 0:
                            fd = (str(ch['fromdate']).split(' '))[0]
                            td = (str(ch['todate']).split(' '))[0]

                            fd = datetime.datetime.strptime(fd, '%Y-%m-%d').date()
                            td = datetime.datetime.strptime(td, '%Y-%m-%d').date()

                            day_inc = datetime.timedelta(days=1)

                            dat = fd
                            while dat <= td:

                                qry_check = Leaves.objects.filter(extraworkdate__contains=str(dat)).filter(leavecode=qry_co_id[0]['id']).filter(emp_id=empid).exclude(Q(finalstatus__contains='CANCELLED') | Q(finalstatus__contains='REJECTED')).values('leaveid')
                                # if od is already used, then skip it

                                if len(qry_check) > 0:
                                    dat += day_inc
                                    continue

                                ######################## arrear leave ###################################

                                qry_check2 = Days_Arrear_Leaves.objects.filter(extraworkdate__contains=str(dat)).filter(leavecode=qry_co_id[0]['id']).filter(emp_id=empid).exclude(Q(hr_status__contains='CANCELLED') | Q(hr_status__contains='REJECTED')).values('leaveid')
                                # if od is already used, then skip it

                                if len(qry_check2) > 0:
                                    dat += day_inc
                                    continue

                                # check for restricted holiday #########################333

                                qry_check_holiday = Holiday.objects.filter(Q(f_date__lte=dat) & Q(t_date__gte=dat)).filter(dept=EmployeeDropdown.objects.get(sno=qry_dept[0]['dept']), status='INSERT').values('id', 'restricted')

                                qry_attendance = Attendance2.objects.filter(date=fd).filter(extra__gte=extra).filter(Emp_Id=empid).values('extra')
                                att_extra_hrs = datetime.datetime.strptime('00:00:00', '%H:%M:%S').time()

                                ################# get extra work hours of that od leave day range > 00:00:00 ###########

                                if len(qry_attendance) > 0:
                                    att_extra_hrs = datetime.datetime.strptime(str(qry_attendance[0]['extra']), '%H:%M:%S').time()

                                leave_extra_hrs = datetime.datetime.strptime('00:00:00', '%H:%M:%S').time()
                                if len(qry_check_holiday) > 0 and qry_check_holiday[0]['restricted'] == 'N':

                                    if dat == fd:
                                        if ch['fhalf'] != '0':
                                            leave_extra_hrs = datetime.datetime.strptime(half_hours_limit[0]['value'], '%H:%M:%S').time()
                                        else:
                                            leave_extra_hrs = datetime.datetime.strptime(full_hours_limit[0]['value'], '%H:%M:%S').time()
                                    elif dat == td:
                                        if ch['fhalf'] != '0':
                                            leave_extra_hrs = datetime.datetime.strptime(half_hours_limit[0]['value'], '%H:%M:%S').time()
                                        else:
                                            leave_extra_hrs = datetime.datetime.strptime(full_hours_limit[0]['value'], '%H:%M:%S').time()
                                    else:
                                        leave_extra_hrs = datetime.datetime.strptime(full_hours_limit[0]['value'], '%H:%M:%S').time()

                                    ############# if attendance extra work hours is more than od work hours then use attendance extra work hours ######

                                    ##### example:- if  attendance extra work hours generated full day compoff whereas od generates half day compoff then give preference to more one #######################

                                    data.append({'date': str(datetime.datetime.strptime(((str(dat)).split(' '))[0], '%Y-%m-%d').date()), 'extra': str(max(leave_extra_hrs, att_extra_hrs))})

                                dat += day_inc

                    status = 200
                    limit = datetime.datetime.strptime(full_hours_limit[0]['value'], '%H:%M:%S').time()
                    limit = (datetime.datetime.combine(datetime.date(1, 1, 1), limit) - datetime.timedelta(seconds=1)).time()
                    data_send = {'data': data, 'half_hours_limit': str(limit)}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_send, status=status)


def mark_compoff_admin(request):
    status = None
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337, 211, 404])
            if check == 200:
                if request.method == 'POST':
                    status = 200
                    msg = "Leave Successfully Applied"

                    data = json.loads(request.body)

                    # accounts days arrear ############3
                    arrear_leave = False

                    if 'request_type' in data:
                        if data['request_type'] == "arrear_leave":
                            arrear_leave = True

                    qry_od_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
                    leaveid = qry_od_id[0]['id']

                    from_date = datetime.datetime.strptime(data['f_date'], '%Y-%m-%d').date()
                    to_date = datetime.datetime.strptime(data['t_date'], '%Y-%m-%d').date()

                    num_of_leaves = fun_num_of_leaves(from_date, to_date, data['fromHalf'], data['toHalf'])

                    check2 = Leave_HalfCheck(from_date, to_date, data['fromHalf'], data['toHalf'])
                    check3 = fun_leave_same_dateRange_check(data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'], leaveid)
                    check4 = fun_leave_check_validity(data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    check6 = Leave_ClubCheck(leaveid, data['emp_code'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    # check5=fun_leave_hourly(leaveid,from_date,to_date,data['fromHalf'],data['toHalf'])
                    check9 = check_cl_co_comb(data['fromHalf'], data['toHalf'], from_date, to_date, leaveid, num_of_leaves, data['emp_code'])

                    if arrear_leave == False:
                        check11 = check_month_locked(from_date, to_date)
                    else:
                        check11 = False

                    if(check2 == False):
                        msg = "Half Combination Not Allowed!"
                    elif(check3[1] == False):
                        msg = check3[0] + " Leave Already Applied in selected Date Range!"
                    elif(check4 == False):
                        msg = "Attendance Already Marked for applied Days!"
                    elif(check6[0] == False):
                        msg = check6[1] + " and Applied leave cannot be Clubbed!"
                    elif check9[0] == False:
                        msg = check9[1]
                    elif check11 == True:
                        msg = "Payable days has been locked for this month."
                    elif(check2 and check3[1] and check4 and check6[0] and check9[0] and not check11):

                        if arrear_leave == False:
                            qry_ins = Leaves.objects.create(requestdate=(date.today()), fromdate=(data['f_date']), todate=(data['t_date']), days=num_of_leaves, reason=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), finalstatus='APPROVED BY ADMIN', finalapprovaldate=date.today(), leavecode=LeaveType.objects.get(id=leaveid), extrahours=data['extra_work_hours'], extraworkdate=data['extra_work_date'], filename=data['file_name'])

                            leave_id = Leaves.objects.values('leaveid').order_by('-leaveid')[:1]

                            qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept', 'desg')

                            flag = 0
                            while flag != 1:
                                qry_leave_approval = Leaveapproval.objects.create(status="APPROVED BY ADMIN", approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), reportinglevel=-1, leaveid=Leaves.objects.get(leaveid=leave_id), remark=data['reason'], approved_by=request.session['hash1'], dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

                                qry_c = Leaveapproval.objects.filter(reportinglevel=-1, dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']), leaveid=Leaves.objects.get(leaveid=leave_id))

                                if len(qry_c) > 0:
                                    flag = 1
                                    break

                            q_lv = Leaves.objects.filter(leaveid=leave_id).values('fromdate', 'todate', 'days', 'emp_id', 'emp_id__name', 'emp_id__email')

                            message2 = 'Dear ' + q_lv[0]['emp_id__name'] + ' (' + q_lv[0]['emp_id'] + ') ' + ',<br><br>Your leave request has been APPLIED BY ADMIN.<br><br>From Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['fromdate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '<br><br>To Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['todate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(q_lv[0]['days']) + ' Day(s).<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                            subject2 = "Leave APPLIED BY ADMIN | " + q_lv[0]['emp_id__name'] + " (" + q_lv[0]['emp_id'] + ")" + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                            mail2 = q_lv[0]['emp_id__email']

                            Thread(target=store_email, args=[mail2, subject2, message2]).start()

                        else:
                            actual_days = calendar.monthrange(from_date.year, to_date.month)[1]
                            emp_id = data['emp_code']

                            qry_check_sign = Sign_In_Out_Arrear.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), date__range=[data['f_date'], data['t_date']]).values('status', 'date')
                            for qc in qry_check_sign:
                                if (qc['date'] == from_date) and (qc['status'] == 0 or qc['status'] == data['fromHalf'] or data['fromHalf'] == 0):
                                    status = 409
                                    msg = "Sign In/Out Arrear has already been applied for the date selected"
                                elif (qc['date'] == to_date) and (qc['status'] == 0 or qc['status'] == data['toHalf'] or data['toHalf'] == 0):
                                    status = 409
                                    msg = "Sign In/Out Arrear has already been applied for the date selected"
                                elif qc['date'] != from_date and qc['date'] != to_date:
                                    status = 409
                                    msg = "Sign In/Out Arrear has already been applied for the date selected"

                            if status == 200:
                                session = acc.views.getCurrentSession(None)
                                salary_month = acc.views.getSalaryMonth(session)

                                qry_ins = Days_Arrear_Leaves.objects.create(requestdate=(date.today()), fromdate=(data['f_date']), todate=(data['t_date']), days=actual_days, hr_remark=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=str(data['emp_code'])), hr_status='APPROVED BY ADMIN', finalapprovaldate=date.today(), leavecode=LeaveType.objects.get(id=leaveid), extrahours=data['extra_work_hours'], extraworkdate=data['extra_work_date'], filename=data['file_name'], working_days=num_of_leaves, session=AccountsSession.objects.get(id=session), month=salary_month)

                    else:
                        status = 409

                else:
                    status = 502
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data = {'msg': msg, 'status': status}
    return JsonResponse(data=data)


def mark_compoff_employee(request):
    status = None
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'POST':

                    data = json.loads(request.body)
                    qry_od_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
                    leaveid = qry_od_id[0]['id']
                    emp_code = request.session['hash1']
                    from_date = datetime.datetime.strptime(data['f_date'], '%Y-%m-%d').date()
                    to_date = datetime.datetime.strptime(data['t_date'], '%Y-%m-%d').date()
                    reporting_levels = []

                    num_of_leaves = fun_num_of_leaves(from_date, to_date, data['fromHalf'], data['toHalf'])
                    qry_dept = EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('dept', 'desg', 'name', 'email')
                    check1 = Leave_DayLimit(from_date, qry_dept[0]['dept'], leaveid, request.session['hash1'])
                    check2 = Leave_HalfCheck(from_date, to_date, data['fromHalf'], data['toHalf'])
                    check3 = fun_leave_same_dateRange_check(emp_code, from_date, to_date, data['fromHalf'], data['toHalf'], leaveid)
                    check4 = fun_leave_check_validity(emp_code, from_date, to_date, data['fromHalf'], data['toHalf'])
                    check6 = Leave_ClubCheck(leaveid, request.session['hash1'], from_date, to_date, data['fromHalf'], data['toHalf'])
                    check9 = check_cl_co_comb(data['fromHalf'], data['toHalf'], from_date, to_date, leaveid, num_of_leaves, request.session['hash1'])
                    check11 = check_month_locked(from_date, to_date)
                    if(check1 == False):
                        msg = "Apply Daylimit ecxeeded!"
                    elif(check2 == False):
                        msg = "Half Combination Not Allowed!"
                    elif(check3[1] == False):
                        msg = check3[0] + " Leave Already Applied in selected Date Range!"
                    elif(check4 == False):
                        msg = "Attendance Already Marked for applied Days!"
                    elif(check6[0] == False):
                        msg = check6[1] + " and Applied cannot be Clubbed!"
                    elif check9[0] == False:
                        msg = check9[1]
                    elif check11 == True:
                        msg = "Payable days has been locked for this month."
                    elif(check1 and check2 and check3[1] and check4 and check6[0] and check9[0] and not check11):
                        qry_ins = Leaves.objects.create(requestdate=(date.today()), fromdate=(data['f_date']), todate=(data['t_date']), days=num_of_leaves, reason=data['reason'], fhalf=data['fromHalf'], thalf=data['toHalf'], emp_id=EmployeePrimdetail.objects.get(emp_id=emp_code), finalstatus='PENDING', finalapprovaldate=None, leavecode=LeaveType.objects.get(id=leaveid), extrahours=data['extra_work_hours'], extraworkdate=data['extra_work_date'], filename=data['file_name'])

                        leave_id = Leaves.objects.values('leaveid').order_by('-leaveid')[:1]

                        qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=emp_code).values('dept', 'desg')
                        report = find_reporting_levels(request.session['hash1'])
                        reporting_levels = report['rep_level']
                        if(len(reporting_levels) != 0):
                            reporting = reporting_levels[0]
                        else:
                            reporting = 0

                        flag = 0
                        while flag != 1:
                            qry_leave_approval = Leaveapproval.objects.create(status="PENDING", approvaldate=None, reportinglevel=reporting, dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), leaveid=Leaves.objects.get(leaveid=leave_id))

                            qry_c = Leaveapproval.objects.filter(reportinglevel=reporting, dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), leaveid=Leaves.objects.get(leaveid=leave_id))
                            if len(qry_c) > 0:
                                flag = 1
                                break

                        ############# send email ##################
                        qry_leave_details = LeaveType.objects.filter(id=leaveid).values('leave_name', 'leave_abbr')
                        qry_rep_email = EmployeePrimdetail.objects.filter(dept=EmployeeDropdown.objects.get(sno=report['dept'][0]), desg=EmployeeDropdown.objects.get(sno=report['rep_to'][0]), emp_status="ACTIVE").values('email', 'name', 'desg__value')

                        if data['fromHalf'] == '0':
                            fhalf = 'Full Day'
                        elif data['fromHalf'] == '1':
                            fhalf = 'First Half'
                        elif data['fromHalf'] == '2':
                            fhalf = 'Second Half'

                        if data['toHalf'] == '0':
                            thalf = 'Full Day'
                        elif data['toHalf'] == '1':
                            thalf = 'First Half'
                        elif data['toHalf'] == '2':
                            thalf = 'Second Half'

                        if data['reason'] is None:
                            data['reason'] = '-----'
                        message1 = 'Dear ' + qry_dept[0]['name'] + ',<br><br>You have applied ' + qry_leave_details[0]['leave_name'] + ' (' + qry_leave_details[0]['leave_abbr'] + ')' + ' from ' + str(datetime.datetime.strptime(str(data['f_date']), "%Y-%m-%d").strftime("%d-%b-%Y")) + ' till ' + str(datetime.datetime.strptime(str(data['t_date']), "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(num_of_leaves) + ' Day(s).<br><br>Purpose - ' + data['reason'] + '<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                        subject1 = "Leave Request | " + qry_leave_details[0]['leave_name'] + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                        mail1 = qry_dept[0]['email']
                        Thread(target=store_email, args=[mail1, subject1, message1]).start()

                        status = 200
                        msg = "Leave Successfully Applied"

                    else:
                        status = 409
                        msg = "Wrongly selected leave"
                else:
                    status = 502
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data = {'msg': msg, 'status': status}
    return JsonResponse(data=data)


def od_upload_or_not(request):
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337, 211])
            if check == 200:
                if request.method == 'POST':

                    data = json.loads(request.body)
                    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')
                    leaveid = qry_od_id[0]['id']

                    cat_id = data['Cat']
                    compoff_id = data['SubCat_compoff']
                    upload_id = data['SubCat_upload']

                    qry_sub = EmployeeDropdown.objects.filter(pid=cat_id).exclude(value__isnull=True).values('value', 'sno')
                    for qr in qry_sub:
                        qry2 = OdCategoryUpload.objects.filter(category=EmployeeDropdown.objects.get(sno=cat_id), sub_category=EmployeeDropdown.objects.get(sno=qr['sno'])).values('sno')

                        co = 0
                        up = 0
                        if qr['sno'] in compoff_id:
                            co = 1
                        if qr['sno'] in upload_id:
                            up = 1

                        if len(qry2) > 0:
                            qry3 = OdCategoryUpload.objects.filter(category=EmployeeDropdown.objects.get(sno=cat_id), sub_category=EmployeeDropdown.objects.get(sno=qr['sno'])).update(is_compoff=co, is_upload=up)
                        else:
                            qry3 = OdCategoryUpload.objects.create(category=EmployeeDropdown.objects.get(sno=cat_id), sub_category=EmployeeDropdown.objects.get(sno=qr['sno']), is_compoff=co, is_upload=up, LeaveId=LeaveType.objects.get(id=leaveid))

                    # qry_del=EmployeeDropdown.objects.filter(pid=)
                    # for sub in sub_cat:
                    #   qry_od_ins=OdCategoryUpload.objects.create(category=EmployeeDropdown.objects.get(sno=data['Cat']),sub_category=EmployeeDropdown.objects.get(sno=sub),LeaveId=LeaveType.objects.get(id=leaveid),num_of_days=0)

                    status = 200
                    msg = "Successfully inserted"

                else:
                    status = 502
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data = {'msg': msg}
    return JsonResponse(data=data, status=status)


def previous_od_upload(request):
    msg = ""
    data = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337, 211])
            if check == 200:
                if request.method == 'GET':

                    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')
                    leaveid = qry_od_id[0]['id']
                    qry_od = OdCategoryUpload.objects.filter(LeaveId=LeaveType.objects.get(id=leaveid)).values('category', 'sub_category', 'sno', 'category__value', 'sub_category__value', 'is_compoff', 'is_upload')
                    data = []
                    for j in qry_od:
                        co = "NO"
                        up = "NO"
                        if j['is_compoff'] == 1:
                            co = "YES"
                        if j['is_upload'] == 1:
                            up = "YES"
                        data.append({'category': j['category__value'], 'sub_cat': j['sub_category__value'], 'sno': j['sno'], 'is_upload': up, 'is_compoff': co})

                    status = 200
                    msg = "Successfully inserted"

                else:
                    status = 502
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data_send = {'data_send': data}
    return JsonResponse(data=data_send, status=status)

# this function returns role to ehich the given empid reports to in ascending order of reporting no


def find_reporting_levels(empid):
    reporting_levels = []
    reporting_to = []
    department = []
    reporting = Reporting.objects.filter(emp_id=empid).values('reporting_no', 'reporting_to', 'department').order_by('reporting_no')
    if(reporting.count() == 0):
        reporting_levels.append(0)
    else:
        for i in reporting:
            reporting_levels.append(i['reporting_no'])
            reporting_to.append(i['reporting_to'])
            department.append(i['department'])
    data = {'rep_level': reporting_levels, 'rep_to': reporting_to, 'dept': department}
    return data


def view_previous_leave(request):
    msg = ""
    data = {}
    data_send = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if(request.GET['request_by'] == 'admin'):
                check = checkpermission(request, [337, 211])
                emp_id = request.GET['emp_code']
            elif(request.GET['request_by'] == 'employee'):
                check = checkpermission(request, [337])
                emp_id = request.session['hash1']
            if check == 200:
                if request.method == 'GET':
                    resolve_leave_error()
                    qry_co_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
                    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')

                    if 'fdate' in request.GET:
                        fdate = datetime.datetime.strptime(str(request.GET['fdate']).split("T")[0], '%Y-%m-%d').date()
                    else:
                        fdate = datetime.datetime.strptime("2010-01-01", '%Y-%m-%d').date()

                    if 'tdate' in request.GET:
                        tdate = datetime.datetime.strptime(str(request.GET['tdate']).split("T")[0], '%Y-%m-%d').date()
                    else:
                        tdate = date.today()

                    #################################  NORMAL VIEW PREVIOUS LEAVE ###################################

                    get_remaining_leaves = employee_remaining_leaves(emp_id, False)
                    remaining_leaves = []
                    for rem in get_remaining_leaves:
                        remaining_leaves.append({'label': rem['leave_abbr'], 'data': rem['leaves_remaining']})

                    if request.GET['request_type'] == "normal":

                        qry_prv_lv = Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), requestdate__range=[fdate, tdate]).exclude(leavecode=qry_co_id[0]['id']).exclude(leavecode=qry_od_id[0]['id']).values('requestdate', 'fromdate', 'todate', 'days', 'reason', 'fhalf', 'thalf', 'finalstatus', 'finalapprovaldate', 'leavecode', 'leaveid').order_by('-leaveid')
                        data = []
                        for pr in qry_prv_lv:
                            da = []

                            qry_lv_tp = LeaveType.objects.filter(id=pr['leavecode']).values('leave_name')
                            qry_lv_app = Leaveapproval.objects.filter(leaveid=pr['leaveid']).extra(select={'approvaldate': "DATE_FORMAT(approvaldate,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('status', 'remark', 'approvaldate', 'reportinglevel')
                            if qry_lv_app[0]['status'] == "PENDING":
                                can_cancel = True
                            else:
                                can_cancel = False

                            for i in qry_lv_app:

                                qry_r = Reporting.objects.filter(emp_id=emp_id, reporting_no=i['reportinglevel']).values('reporting_to')
                                if len(qry_r) > 0:
                                    qry_rep = EmployeeDropdown.objects.filter(sno=qry_r[0]['reporting_to']).values('value')
                                    rep = qry_rep[0]['value']
                                else:
                                    if i['reportinglevel'] == -1:
                                        rep = "ADMIN"
                                    else:
                                        rep = "---"
                                da.append({'status': i['status'], 'remark': i['remark'], 'approval_date': i['approvaldate'], 'by': rep})

                            if str(pr['fhalf']) == '0':
                                fhalf = "FULL DAY"
                            elif str(pr['fhalf']) == '1':
                                fhalf = "FIRST HALF"
                            else:
                                fhalf = "SECOND HALF"

                            if str(pr['thalf']) == '0':
                                thalf = "FULL DAY"
                            elif str(pr['thalf']) == '1':
                                thalf = "FIRST HALF"
                            else:
                                thalf = "SECOND HALF"

                            data.append({'requestdate': pr['requestdate'], 'fdate': pr['fromdate'], 'tdate': pr['todate'], 'days': pr['days'], 'reason': pr['reason'], 'fhalf': fhalf, 'thalf': thalf, 'final_status': pr['finalstatus'], 'finalapprovaldate': pr['finalapprovaldate'], 'reportinglevel_status': da, 'leave_type': qry_lv_tp[0]['leave_name'], 'can_cancel': can_cancel, 'sno': pr['leaveid']})

                    ################################## OD VIEW PREVIOUS LEAVE ##########################################

                    elif request.GET['request_type'] == "od":
                        qry_prv_lv = Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), requestdate__range=[fdate, tdate]).filter(leavecode=qry_od_id[0]['id']).values('requestdate', 'fromdate', 'todate', 'days', 'reason', 'fhalf', 'thalf', 'finalstatus', 'finalapprovaldate', 'leavecode', 'subtype', 'category', 'leaveid').order_by('-leaveid')

                        data = []
                        for pr in qry_prv_lv:
                            da = []

                            qry_lv_app = Leaveapproval.objects.filter(leaveid=pr['leaveid']).extra(select={'approvaldate': "DATE_FORMAT(approvaldate,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('status', 'remark', 'approvaldate', 'reportinglevel')
                            if qry_lv_app[0]['status'] == "PENDING":
                                can_cancel = True
                            else:
                                can_cancel = False

                            for i in qry_lv_app:
                                qry_r = Reporting.objects.filter(emp_id=emp_id, reporting_no=i['reportinglevel']).values('reporting_to')
                                if len(qry_r) > 0:
                                    qry_rep = EmployeeDropdown.objects.filter(sno=qry_r[0]['reporting_to']).values('value')
                                    rep = qry_rep[0]['value']
                                else:
                                    if i['reportinglevel'] == -1:
                                        rep = "ADMIN"
                                    else:
                                        rep = "---"
                                da.append({'status': i['status'], 'remark': i['remark'], 'approval_date': i['approvaldate'], 'by': rep})

                            qry_cat = EmployeeDropdown.objects.filter(sno=pr['category']).values('value')
                            qry_sub_cat = EmployeeDropdown.objects.filter(sno=pr['subtype']).values('value')

                            if str(pr['fhalf']) == '0':
                                fhalf = "FULL DAY"
                            elif str(pr['fhalf']) == '1':
                                fhalf = "FIRST HALF"
                            else:
                                fhalf = "SECOND HALF"

                            if str(pr['thalf']) == '0':
                                thalf = "FULL DAY"
                            elif str(pr['thalf']) == '1':
                                thalf = "FIRST HALF"
                            else:
                                thalf = "SECOND HALF"

                            data.append({'requestdate': pr['requestdate'], 'fdate': pr['fromdate'], 'tdate': pr['todate'], 'days': pr['days'], 'reason': pr['reason'], 'fhalf': fhalf, 'thalf': thalf, 'final_status': pr['finalstatus'], 'finalapprovaldate': pr['finalapprovaldate'], 'reportinglevel_status': da, 'cat': qry_cat[0]['value'], 'sub_cat': qry_sub_cat[0]['value'], 'can_cancel': can_cancel, 'sno': pr['leaveid']})

                    ################################### COMP-OFF VIEW PREVIOUS LEAVE ######################################

                    elif request.GET['request_type'] == "compoff":
                        qry_prv_lv = Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), requestdate__range=[fdate, tdate]).filter(leavecode=qry_co_id[0]['id']).values('requestdate', 'fromdate', 'todate', 'days', 'reason', 'fhalf', 'thalf', 'finalstatus', 'finalapprovaldate', 'leavecode', 'leaveid', 'extrahours', 'extraworkdate').order_by('-leaveid')

                        data = []
                        for pr in qry_prv_lv:
                            da = []

                            qry_lv_app = Leaveapproval.objects.filter(leaveid=pr['leaveid']).extra(select={'approvaldate': "DATE_FORMAT(approvaldate,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('status', 'remark', 'approvaldate', 'reportinglevel').order_by('-id')
                            if qry_lv_app[0]['status'] == "PENDING":
                                can_cancel = True
                            else:
                                can_cancel = False

                            for i in qry_lv_app:
                                qry_r = Reporting.objects.filter(emp_id=emp_id, reporting_no=i['reportinglevel']).values('reporting_to')
                                if len(qry_r) > 0:
                                    qry_rep = EmployeeDropdown.objects.filter(sno=qry_r[0]['reporting_to']).values('value')
                                    rep = qry_rep[0]['value']
                                else:
                                    if i['reportinglevel'] == -1:
                                        rep = "ADMIN"
                                    else:
                                        rep = "---"
                                da.append({'status': i['status'], 'remark': i['remark'], 'approval_date': i['approvaldate'], 'by': rep})

                            if str(pr['fhalf']) == '0':
                                fhalf = "FULL DAY"
                            elif str(pr['fhalf']) == '1':
                                fhalf = "FIRST HALF"
                            else:
                                fhalf = "SECOND HALF"

                            if str(pr['thalf']) == '0':
                                thalf = "FULL DAY"
                            elif str(pr['thalf']) == '1':
                                thalf = "FIRST HALF"
                            else:
                                thalf = "SECOND HALF"

                            data.append({'requestdate': pr['requestdate'], 'fdate': pr['fromdate'], 'tdate': pr['todate'], 'days': pr['days'], 'reason': pr['reason'], 'fhalf': fhalf, 'thalf': thalf, 'final_status': pr['finalstatus'], 'finalapprovaldate': pr['finalapprovaldate'], 'reportinglevel_status': da, 'extra_hrs': pr['extrahours'], 'extra_work_date': pr['extraworkdate'], 'can_cancel': can_cancel, 'sno': pr['leaveid']})
                    data_send = {'data': data, 'remaining_leaves': remaining_leaves}

                    status = 200

                else:
                    status = 502
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"

    return JsonResponse(data=data_send, status=status)


def view_previous_arrear_leave(request):
    msg = ""
    data = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if(request.GET['request_by'] == 'admin'):
                check = checkpermission(request, [337, 211])
                emp_id = request.GET['emp_code']
            elif(request.GET['request_by'] == 'employee'):
                check = checkpermission(request, [337])
                emp_id = request.session['hash1']
            if check == 200:
                if request.method == 'GET':
                    qry_co_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
                    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')

                    #################################  NORMAL VIEW PREVIOUS LEAVE ###################################

                    if request.GET['request_type'] == "normal":

                        qry_prv_lv = Days_Arrear_Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)).exclude(leavecode=qry_co_id[0]['id']).exclude(leavecode=qry_od_id[0]['id']).values('requestdate', 'fromdate', 'todate', 'working_days', 'hr_remark', 'fhalf', 'thalf', 'hr_status', 'finalapprovaldate', 'leavecode', 'leaveid', 'arrearCredited', 'leavecode__leave_name').order_by('-leaveid')
                        data = []

                        for pr in qry_prv_lv:

                            if str(pr['fhalf']) == '0':
                                fhalf = "FULL DAY"
                            elif str(pr['fhalf']) == '1':
                                fhalf = "FIRST HALF"
                            else:
                                fhalf = "SECOND HALF"

                            if str(pr['thalf']) == '0':
                                thalf = "FULL DAY"
                            elif str(pr['thalf']) == '1':
                                thalf = "FIRST HALF"
                            else:
                                thalf = "SECOND HALF"

                            data.append({'requestdate': pr['requestdate'], 'fdate': pr['fromdate'], 'tdate': pr['todate'], 'days': pr['working_days'], 'reason': pr['hr_remark'], 'fhalf': fhalf, 'thalf': thalf, 'final_status': pr['hr_status'], 'finalapprovaldate': pr['finalapprovaldate'], 'leave_type': pr['leavecode__leave_name'], 'sno': pr['leaveid'], 'arrear_credited': pr['arrearCredited']})

                    ################################## OD VIEW PREVIOUS LEAVE ##########################################

                    elif request.GET['request_type'] == "od":
                        qry_prv_lv = Days_Arrear_Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)).filter(leavecode=qry_od_id[0]['id']).values('requestdate', 'fromdate', 'todate', 'working_days', 'hr_remark', 'fhalf', 'thalf', 'hr_status', 'finalapprovaldate', 'leavecode', 'subtype__value', 'category__value', 'leaveid', 'arrearCredited').order_by('-leaveid')

                        data = []
                        for pr in qry_prv_lv:
                            da = []

                            if str(pr['fhalf']) == '0':
                                fhalf = "FULL DAY"
                            elif str(pr['fhalf']) == '1':
                                fhalf = "FIRST HALF"
                            else:
                                fhalf = "SECOND HALF"

                            if str(pr['thalf']) == '0':
                                thalf = "FULL DAY"
                            elif str(pr['thalf']) == '1':
                                thalf = "FIRST HALF"
                            else:
                                thalf = "SECOND HALF"

                            data.append({'requestdate': pr['requestdate'], 'fdate': pr['fromdate'], 'tdate': pr['todate'], 'days': pr['working_days'], 'reason': pr['hr_remark'], 'fhalf': fhalf, 'thalf': thalf, 'final_status': pr['hr_status'], 'finalapprovaldate': pr['finalapprovaldate'], 'cat': pr['category__value'], 'sub_cat': pr['subtype__value'], 'sno': pr['leaveid'], 'arrear_credited': pr['arrearCredited']})

                    ################################### COMP-OFF VIEW PREVIOUS LEAVE ######################################

                    elif request.GET['request_type'] == "compoff":
                        qry_prv_lv = Days_Arrear_Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)).filter(leavecode=qry_co_id[0]['id']).values('requestdate', 'fromdate', 'todate', 'working_days', 'hr_remark', 'fhalf', 'thalf', 'hr_status', 'finalapprovaldate', 'leavecode', 'leaveid', 'extrahours', 'extraworkdate', 'arrearCredited').order_by('-leaveid')

                        data = []
                        for pr in qry_prv_lv:

                            if str(pr['fhalf']) == '0':
                                fhalf = "FULL DAY"
                            elif str(pr['fhalf']) == '1':
                                fhalf = "FIRST HALF"
                            else:
                                fhalf = "SECOND HALF"

                            if str(pr['thalf']) == '0':
                                thalf = "FULL DAY"
                            elif str(pr['thalf']) == '1':
                                thalf = "FIRST HALF"
                            else:
                                thalf = "SECOND HALF"

                            data.append({'requestdate': pr['requestdate'], 'fdate': pr['fromdate'], 'tdate': pr['todate'], 'days': pr['working_days'], 'reason': pr['hr_remark'], 'fhalf': fhalf, 'thalf': thalf, 'final_status': pr['hr_status'], 'finalapprovaldate': pr['finalapprovaldate'], 'extra_hrs': pr['extrahours'], 'extra_work_date': pr['extraworkdate'], 'can_cancel': can_cancel, 'sno': pr['leaveid'], 'arrear_credited': pr['arrearCredited']})

                    status = 200

                else:
                    status = 502
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data_send = {'data': data}
    return JsonResponse(data=data_send, status=status)


def func_cancel_normal_leave(LeaveId, msg, empid):

    qry_co_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')

    q_up = Leaves.objects.filter(leaveid=LeaveId).update(finalstatus=msg, finalapprovaldate=date.today())

    if msg == "CANCELLED" or msg == "REJECTED":
        qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=empid).values('dept', 'desg')
        q_up = Leaveapproval.objects.filter(leaveid=LeaveId).values('id', 'reportinglevel').order_by('-id')
        if q_up[0]['reportinglevel'] == 1 and len(q_up) > 1:
            q_del = Leaveapproval.objects.filter(id=q_up[1]['id']).delete()

        q_up2 = Leaveapproval.objects.filter(id=q_up[0]['id']).update(status=msg, approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), approved_by=empid, dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

    else:
        qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=empid).values('dept', 'desg')
        q_up2 = Leaveapproval.objects.create(leaveid=Leaves.objects.get(leaveid=LeaveId), status=msg, reportinglevel=-1, approved_by=empid, approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

    qry_lv_cd = Leaves.objects.filter(leaveid=LeaveId).values('leavecode', 'requestdate', 'days', 'emp_id')
    qry_lv_tp = LeaveType.objects.filter(id=qry_lv_cd[0]['leavecode']).exclude(lapse_start__isnull=True).exclude(lapse_month__isnull=True).values('lapse_start', 'lapse_month')

    flag = 0
    if len(qry_lv_tp) > 0:
        date1 = datetime.datetime.strptime(str(qry_lv_tp[0]['lapse_start']), '%Y-%m-%d').date()
        date2 = date1 - relativedelta(months=+int(qry_lv_tp[0]['lapse_month']))

        date_comp = datetime.datetime.strptime(str(qry_lv_cd[0]['requestdate']), '%Y-%m-%d').date()
        if date_comp < date1 and date_comp > date2:
            flag = 1

    else:
        flag = 1

    if flag == 1 and qry_lv_cd[0]['leavecode'] != qry_co_id[0]['id'] and qry_lv_cd[0]['leavecode'] != qry_od_id[0]['id']:
        qry_lv_rm = Leaveremaning.objects.filter(empid=qry_lv_cd[0]['emp_id'], leaveid=qry_lv_cd[0]['leavecode']).values('remaining', 'leaveid__accumulate_max', 'leaveid__leave_status')

        if qry_lv_rm[0]['leaveid__leave_status'] == 'A':
            rem_lv = min(float(qry_lv_rm[0]['remaining']) + float(qry_lv_cd[0]['days']), int(qry_lv_rm[0]['leaveid__accumulate_max']))
        else:
            rem_lv = float(qry_lv_rm[0]['remaining']) + float(qry_lv_cd[0]['days'])
        qry_up3 = Leaveremaning.objects.filter(empid=qry_lv_cd[0]['emp_id'], leaveid=qry_lv_cd[0]['leavecode']).update(remaining=rem_lv)


def cancel_leave(request):
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            data = json.loads(request.body)

            if data['cancelled_by'] == "admin":
                check = checkpermission(request, [211, 337])
            else:
                check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'PUT':

                    if data['cancelled_by'] == "admin":
                        message = "CANCELLED BY ADMIN"
                    else:
                        message = "CANCELLED"
                    LeaveId = data['LeaveId']

                    qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept', 'desg')

                    qry_check_cancel = Leaves.objects.filter(leaveid=LeaveId).values('finalstatus', 'fromdate', 'todate')
                    check_locked = check_month_locked(str(qry_check_cancel[0]['fromdate']).split(" ")[0], str(qry_check_cancel[0]['todate']).split(" ")[0])
                    if qry_check_cancel[0]['finalstatus'] == "CANCELLED" or qry_check_cancel[0]['finalstatus'] == "CANCELLED BY ADMIN" or qry_check_cancel[0]['finalstatus'] == "REJECTED":
                        status = 409
                        msg = "Leave already " + qry_check_cancel[0]['finalstatus']
                    elif check_locked == True and "APPROVED" in qry_check_cancel[0]['finalstatus']:
                        status = 409
                        msg = "Payable days has been locked for this month."

                    else:
                        if data['type'] == "normal":
                            func_cancel_normal_leave(LeaveId, message, request.session['hash1'])
                        elif data['type'] == "od":
                            q_up = Leaves.objects.filter(leaveid=LeaveId).update(finalstatus=message, finalapprovaldate=date.today())

                            if message == "CANCELLED" or message == "REJECTED":
                                q_up2 = Leaveapproval.objects.filter(leaveid=LeaveId).update(status=message, approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), approved_by=request.session['hash1'], dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

                            else:
                                q_up2 = Leaveapproval.objects.create(leaveid=Leaves.objects.get(leaveid=LeaveId), status=message, reportinglevel=-1, approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), approved_by=request.session['hash1'], dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

                        elif data['type'] == "compoff":
                            q_up = Leaves.objects.filter(leaveid=LeaveId).update(finalstatus=message, finalapprovaldate=date.today())
                            if message == "CANCELLED" or message == "REJECTED":
                                q_up2 = Leaveapproval.objects.filter(leaveid=LeaveId).update(status=message, approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), approved_by=request.session['hash1'], dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

                            else:
                                q_up2 = Leaveapproval.objects.create(leaveid=Leaves.objects.get(leaveid=LeaveId), status=message, reportinglevel=-1, approvaldate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), approved_by=request.session['hash1'], dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']), desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']))

                        q_lv = Leaves.objects.filter(leaveid=LeaveId).values('fromdate', 'todate', 'days', 'emp_id', 'emp_id__name', 'emp_id__email')

                        message2 = 'Dear ' + q_lv[0]['emp_id__name'] + ' (' + q_lv[0]['emp_id'] + ') ' + ',<br><br>Your leave request has been ' + message + '.<br><br>From Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['fromdate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '<br><br>To Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['todate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(q_lv[0]['days']) + ' Day(s).<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                        subject2 = "Leave " + message + "| " + q_lv[0]['emp_id__name'] + " (" + q_lv[0]['emp_id'] + ")" + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                        mail2 = q_lv[0]['emp_id__email']

                        Thread(target=store_email, args=[mail2, subject2, message2]).start()

                        status = 200
                        msg = "Leave Successfully cancelled"

                else:
                    status = 502
                    msg = "Invalid request"
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data_send = {'msg': msg}
    return JsonResponse(data=data_send, status=status)


def delete_od_upload(request):
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'DELETE':

                    data = json.loads(request.body)
                    sno = data['sno']
                    q_del = OdCategoryUpload.objects.filter(sno=sno).delete()

                    status = 200
                    msg = "Successfully cancelled"

                else:
                    status = 502
                    msg = "Invalid request"
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data_send = {'msg': msg}
    return JsonResponse(data=data_send, status=status)


def resolve_leave_error():
    # qry_leave_id = list(Leaveapproval.objects.filter(status__contains='APPROVED',leaveid__in=Leaves.objects.filter(finalstatus='PENDING').values_list('leaveid',flat=True)).values_list('leaveid',flat=True))
    # print(qry_leave_id)
    # qry_update = Leaves.objects.filter(leaveid__in=qry_leave_id).update(finalstatus='APPROVED')

    # qry_leave_id = list(Leaveapproval.objects.filter(status__contains='REJECTED',leaveid__in=Leaves.objects.filter(finalstatus='PENDING').values_list('leaveid',flat=True)).values_list('leaveid',flat=True))
    # print(qry_leave_id)
    # qry_update = Leaves.objects.filter(leaveid__in=qry_leave_id).update(finalstatus='REJECTED')

    qry_leave_id = Leaves.objects.exclude(leaveid__in=list(Leaveapproval.objects.values_list('leaveid', flat=True))).values('leaveid', 'emp_id')
    for leaveid in qry_leave_id:
        qry_first_reporting = Reporting.objects.filter(emp_id=leaveid['emp_id'], reporting_no=1).values('reporting_to', 'department')
        if len(qry_first_reporting) > 0:
            qry_leave_approval = Leaveapproval.objects.create(status="PENDING", approvaldate=None, reportinglevel=1, dept=EmployeeDropdown.objects.get(sno=qry_first_reporting[0]['department']), desg=EmployeeDropdown.objects.get(sno=qry_first_reporting[0]['reporting_to']), leaveid=Leaves.objects.get(leaveid=leaveid['leaveid']))


####################################################LEAVE APPROVAL#####################################################
def Leave_Approval(request):
    error = True
    msg = ''
    data = ''
    leaves_to_be_approved = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:

            if request.method == 'GET':

                if request.GET['request_type'] == "action":
                    resolve_leave_error()
                    getdesg = EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('desg', 'dept')
                    dept = request.session['dept']
                    qry = Leaveapproval.objects.filter(dept=getdesg[0]['dept'], desg=getdesg[0]['desg'], status='PENDING', leaveid__finalstatus='PENDING').values('leaveid', 'leaveid__requestdate', 'leaveid__subtype__value', 'leaveid__category__value', 'leaveid__emp_id', 'leaveid__emp_id__name', 'dept', 'desg', 'reportinglevel', 'leaveid__days', 'leaveid__reason', 'leaveid__leavecode__leave_abbr', 'leaveid__fromdate', 'leaveid__todate', 'leaveid__filename', 'leaveid__leavecode', 'leaveid__emp_id__dept__value', 'leaveid__extraworkdate')
                    for i in qry:
                        i['requestdate'] = i.pop('leaveid__requestdate')
                        i['sub_type'] = i.pop('leaveid__subtype__value')
                        i['category'] = i.pop('leaveid__category__value')
                        i['employeeid'] = i.pop('leaveid__emp_id')
                        i['name'] = i.pop('leaveid__emp_id__name')
                        i['days'] = i.pop('leaveid__days')
                        i['reasons'] = i.pop('leaveid__reason')
                        if i['leaveid__extraworkdate'] != '' and i['leaveid__extraworkdate'] is not None:
                            i['LeaveType'] = i.pop('leaveid__leavecode__leave_abbr') + " (" + str(datetime.datetime.strptime(str(i.pop('leaveid__extraworkdate')), '%Y-%m-%d').date()) + ")"
                        else:
                            i['LeaveType'] = i.pop('leaveid__leavecode__leave_abbr')

                        i['department'] = i.pop('dept')
                        i['dept'] = i.pop('leaveid__emp_id__dept__value')

                        # employee_reporting_check=Reporting.objects.filter(department=i['department'],reporting_no=i['reportinglevel'],reporting_to=i['desg'],emp_id=i['employeeid']).count()
                        # if employee_reporting_check > 0:
                        leaves_to_be_approved.append(i)
                    error = False
                    msg = "success"
                    status = 200
                    data = {'error': error, 'msg': msg, 'data': leaves_to_be_approved}

                elif request.GET['request_type'] == "view_previous":
                    resolve_leave_error()

                    if 'fdate' in request.GET:
                        fdate = datetime.datetime.strptime(str(request.GET['fdate']).split("T")[0], '%Y-%m-%d').date()
                    else:
                        fdate = datetime.datetime.strptime("2010-01-01", '%Y-%m-%d').date()

                    if 'tdate' in request.GET:
                        tdate = datetime.datetime.strptime(str(request.GET['tdate']).split("T")[0], '%Y-%m-%d').date()
                    else:
                        tdate = date.today()

                    qry = Leaveapproval.objects.filter(approved_by=request.session['hash1'], leaveid__requestdate__range=[fdate, tdate]).values('leaveid__requestdate', 'leaveid__subtype', 'leaveid__category', 'leaveid__emp_id', 'leaveid__emp_id__name', 'dept', 'desg', 'reportinglevel', 'leaveid__days', 'leaveid__reason', 'leaveid__leavecode__leave_abbr', 'leaveid__fromdate', 'leaveid__todate', 'leaveid__filename', 'leaveid__leavecode', 'dept__value', 'desg__value', 'leaveid__finalstatus', 'leaveid__finalapprovaldate', 'leaveid__subtype__value', 'leaveid__category__value').order_by('-id')
                    for i in qry:

                        i['requestdate'] = i.pop('leaveid__requestdate')
                        i['sub_type'] = i.pop('leaveid__subtype')
                        i['category'] = i.pop('leaveid__category')
                        i['category__value'] = i.pop('leaveid__category__value')
                        i['sub_type__value'] = i.pop('leaveid__subtype__value')
                        i['employeeid'] = i.pop('leaveid__emp_id')
                        i['name'] = i.pop('leaveid__emp_id__name')
                        i['days'] = i.pop('leaveid__days')
                        i['reason'] = i.pop('leaveid__reason')
                        i['LeaveType'] = i.pop('leaveid__leavecode__leave_abbr')
                        employee_reporting_check = Reporting.objects.filter(department=i.pop('dept'), reporting_no=i['reportinglevel'], reporting_to=i['desg'], emp_id=i['employeeid'])

                        i['dept'] = i.pop('dept__value')
                        i['desg'] = i.pop('desg__value')
                        i['reportinglevel'] = i.pop('reportinglevel')
                        i['final_status'] = i.pop('leaveid__finalstatus')
                        i['finalapprovaldate'] = i.pop('leaveid__finalapprovaldate')

                        if len(employee_reporting_check) > 0:
                            leaves_to_be_approved.append(i)

                    ########################### NUMBER OF LEAVES APPROVED (SUMMARY) ################
                    qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept', 'desg')
                    employee_reporting = Reporting.objects.filter(department=qry_dept_desg[0]['dept'], reporting_to=qry_dept_desg[0]['desg']).filter(emp_id__in=EmployeePrimdetail.objects.filter(emp_status='ACTIVE').values_list('emp_id', flat=True)).values('emp_id', 'emp_id__name')

                    leave_summary = []
                    for emp in employee_reporting:
                        leave_summary.append({'emp_id': emp['emp_id'], 'name': emp['emp_id__name'], 'data': employee_leave_count_date_range(emp['emp_id'], fdate, tdate)})
                    error = False
                    msg = "success"
                    status = 200
                    data = {'error': error, 'msg': msg, 'data': leaves_to_be_approved, 'leave_summary': leave_summary}

            if request.method == 'POST':
                inp = json.loads(request.body.decode('utf-8'))
                inp1 = inp['data1']
                id = inp1['lid']

                qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('dept', 'desg')
                dept = qry_dept_desg[0]['dept']
                desg = qry_dept_desg[0]['desg']

                appdate = date.today()
                appdatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                type = inp1['type']
                remark = inp['remark']

                getdesg = EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('desg', 'dept')
                if str(getdesg[0]['desg']) != str(desg) or str(getdesg[0]['dept']) != str(dept):
                    status = 403
                else:

                    n = len(id)
                    for l in range(n):
                        qry_check_dupli = Leaveapproval.objects.filter(leaveid=id[l], desg=desg, dept=dept).values('status')
                        q_lv_date = Leaves.objects.filter(leaveid=id[l]).values('fromdate', 'todate')
                        from_date = datetime.datetime.strptime(str(q_lv_date[0]['fromdate']).split(' ')[0], '%Y-%m-%d').date()
                        to_date = datetime.datetime.strptime(str(q_lv_date[0]['todate']).split(' ')[0], '%Y-%m-%d').date()
                        if qry_check_dupli[0]['status'] != "PENDING":
                            status = 409
                            msg = "Already " + qry_check_dupli[0]['status']
                        else:
                            if type == 1:
                                check11 = check_month_locked(from_date, to_date)
                                if check11 == True:
                                    status = 201
                                    msg = "Payable days has been locked for this month."
                                else:
                                    q_up = Leaveapproval.objects.filter(leaveid=id[l]).values('id', 'reportinglevel').order_by('-id')
                                    if q_up[0]['reportinglevel'] == 1 and len(q_up) > 1:
                                        q_del = Leaveapproval.objects.filter(id=q_up[1]['id']).delete()

                                    q_up2 = Leaveapproval.objects.filter(id=q_up[0]['id']).update(status='APPROVED', approvaldate=appdatetime, remark=remark[l], approved_by=request.session['hash1'], dept=getdesg[0]['dept'], desg=getdesg[0]['desg'])

                                    q_up3 = Leaves.objects.filter(leaveid=id[l]).update(finalstatus='APPROVED', finalapprovaldate=appdate)

                                    ############################ send email ############################
                                    q_lv = Leaves.objects.filter(leaveid=id[l]).values('fromdate', 'todate', 'days', 'emp_id', 'emp_id__name', 'emp_id__email')
                                    q_app = Leaveapproval.objects.filter(id=q_up[0]['id']).values('approved_by')
                                    q_app = EmployeePrimdetail.objects.filter(emp_id=q_app[0]['approved_by']).values('desg__value')

                                    message2 = 'Dear ' + q_lv[0]['emp_id__name'] + ' (' + q_lv[0]['emp_id'] + ') ' + ',<br><br>Your leave request has been approved by ' + q_app[0]['desg__value'] + '.<br><br>From Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['fromdate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '<br><br>To Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['todate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(q_lv[0]['days']) + ' Day(s).<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                                    subject2 = "Leave Approved | " + q_lv[0]['emp_id__name'] + " (" + q_lv[0]['emp_id'] + ")" + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                                    mail2 = q_lv[0]['emp_id__email']

                                    Thread(target=store_email, args=[mail2, subject2, message2]).start()

                                    msg = "Approved"
                                    error = False
                                    status = 200
                            elif type == 2:
                                func_cancel_normal_leave(id[l], "REJECTED", request.session['hash1'])

                                q_lv = Leaves.objects.filter(leaveid=id[l]).values('fromdate', 'todate', 'days', 'emp_id', 'emp_id__name', 'emp_id__email')
                                q_app = Leaveapproval.objects.filter(leaveid=id[l]).order_by('-id')[:1].values('approved_by')
                                q_app = EmployeePrimdetail.objects.filter(emp_id=q_app[0]['approved_by']).values('desg__value')

                                message2 = 'Dear ' + q_lv[0]['emp_id__name'] + ' (' + q_lv[0]['emp_id'] + ') ' + ',<br><br>Your leave request has been rejected by ' + q_app[0]['desg__value'] + '.<br><br>From Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['fromdate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '<br><br>To Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['todate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(q_lv[0]['days']) + ' Day(s).<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                                subject2 = "Leave Rejected | " + q_lv[0]['emp_id__name'] + " (" + q_lv[0]['emp_id'] + ")" + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                                mail2 = q_lv[0]['emp_id__email']

                                Thread(target=store_email, args=[mail2, subject2, message2]).start()

                                msg = "Rejected"
                                error = False
                                status = 200
                            elif type == 3:
                                check11 = check_month_locked(from_date, to_date)
                                if check11 == True:
                                    status = 201
                                    msg = "Payable days has been locked for this month."
                                else:
                                    q_up = Leaveapproval.objects.filter(leaveid=id[l]).values('id', 'reportinglevel').order_by('-id')
                                    if q_up[0]['reportinglevel'] == 1 and len(q_up) > 1:
                                        q_del = Leaveapproval.objects.filter(id=q_up[1]['id']).delete()

                                    q_up2 = Leaveapproval.objects.filter(id=q_up[0]['id']).update(status='APPROVED', approvaldate=appdatetime, remark=remark[l], approved_by=request.session['hash1'], dept=getdesg[0]['dept'], desg=getdesg[0]['desg'])

                                    qry2 = Leaveapproval.objects.filter(leaveid=id[l], desg=desg, dept=dept).values('reportinglevel', 'leaveid', 'leaveid__emp_id')
                                    if qry2:
                                        pmail = qry2[0]['leaveid__emp_id']
                                        level = qry2[0]['reportinglevel']
                                        level += level
                                        qry3 = Reporting.objects.filter(reporting_no=level, emp_id=pmail).values('department', 'reporting_to')
                                        if qry3.count() > 0:
                                            list_add = {'leaveid': Leaves.objects.get(leaveid=qry2[0]['leaveid']), 'reportinglevel': level, 'dept': EmployeeDropdown.objects.get(sno=qry3[0]['department']), 'desg': EmployeeDropdown.objects.get(sno=qry3[0]['reporting_to']), 'approvaldate': appdatetime}
                                            qry4 = Leaveapproval.objects.create(**list_add)
                                            if qry4:
                                                msg = "Successfully Approved!"
                                                error = False
                                            else:
                                                msg = "something went wrong"

                                            q_lv = Leaves.objects.filter(leaveid=id[l]).values('fromdate', 'todate', 'days', 'emp_id', 'emp_id__name', 'emp_id__email')

                                            message2 = 'Dear ' + q_lv[0]['emp_id__name'] + ' (' + q_lv[0]['emp_id'] + ') ' + ',<br><br>Your leave request has been sent to next level.<br><br>From Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['fromdate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '<br><br>To Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['todate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(q_lv[0]['days']) + ' Day(s).<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                                            subject2 = "Next Level | " + q_lv[0]['emp_id__name'] + " (" + q_lv[0]['emp_id'] + ")" + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                                            mail2 = q_lv[0]['emp_id__email']

                                            Thread(target=store_email, args=[mail2, subject2, message2]).start()

                                        else:
                                            qry3 = Leaves.objects.filter(leaveid=qry2[0]['leaveid']).update(finalstatus='APPROVED', finalapprovaldate=appdate)
                                            if qry3:
                                                msg = "Successfully Approved"
                                                error = False
                                            else:
                                                msg = "something went wrong"

                                            ############################ send email ############################
                                            q_lv = Leaves.objects.filter(leaveid=id[l]).values('fromdate', 'todate', 'days', 'emp_id', 'emp_id__name', 'emp_id__email')
                                            q_app = Leaveapproval.objects.filter(id=q_up[0]['id']).values('approved_by')
                                            q_app = EmployeePrimdetail.objects.filter(emp_id=q_app[0]['approved_by']).values('desg__value')

                                            message2 = 'Dear ' + q_lv[0]['emp_id__name'] + ' (' + q_lv[0]['emp_id'] + ') ' + ',<br><br>Your leave request has been approved by ' + q_app[0]['desg__value'] + '.<br><br>From Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['fromdate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '<br><br>To Date - ' + str(datetime.datetime.strptime(str(q_lv[0]['todate']).split(' ')[0], "%Y-%m-%d").strftime("%d-%b-%Y")) + '.<br><br>Duration - ' + str(q_lv[0]['days']) + ' Day(s).<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this mail.'

                                            subject2 = "Leave Approved | " + q_lv[0]['emp_id__name'] + " (" + q_lv[0]['emp_id'] + ")" + " | " + str(datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%b-%Y"))

                                            mail2 = q_lv[0]['emp_id__email']

                                            Thread(target=store_email, args=[mail2, subject2, message2]).start()
                                    else:
                                        msg = "no such entry"
                                    msg = "Approved"
                                    error = False
                                    status = 200
                            else:
                                msg = "sorry.. something went wrong"

        else:
            status = 401
    else:
        status = 400
    data = {'msg': msg, 'data': data}
    return JsonResponse(status=status, data=data)


def view_all_leave_status(request):

    msg = ""
    data = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337, 211])
            emp_id = request.GET['emp_code']
            if check == 200:
                if request.method == 'GET':

                    fdate = datetime.datetime.strptime(request.GET['fdate'], '%Y-%m-%d').date()
                    tdate = datetime.datetime.strptime(request.GET['tdate'], '%Y-%m-%d').date()
                    qry_co_id = LeaveType.objects.filter(leave_abbr='CO').values('id')
                    qry_od_id = LeaveType.objects.filter(leave_abbr='OD').values('id')

                    qry_prv_lv = Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)).filter(Q(fromdate__gte=fdate) & Q(fromdate__lte=tdate)).extra(select={'fromdate': "DATE_FORMAT(fromdate,'%%d-%%m-%%Y')", 'todate': "DATE_FORMAT(todate,'%%d-%%m-%%Y')"}).values('requestdate', 'fromdate', 'todate', 'days', 'reason', 'fhalf', 'thalf', 'finalstatus', 'finalapprovaldate', 'leavecode', 'leaveid', 'leavecode__leave_name').order_by('-leaveid')

                    data = []
                    for pr in qry_prv_lv:
                        da = []

                        qry_lv_app = Leaveapproval.objects.filter(leaveid=pr['leaveid']).extra(select={'approvaldate': "DATE_FORMAT(approvaldate,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('status', 'remark', 'approvaldate', 'reportinglevel')

                        for i in qry_lv_app:

                            qry_r = Reporting.objects.filter(emp_id=emp_id, reporting_no=i['reportinglevel']).values('reporting_to')
                            if len(qry_r) > 0:
                                qry_rep = EmployeeDropdown.objects.filter(sno=qry_r[0]['reporting_to']).values('value')
                                rep = qry_rep[0]['value']
                            else:
                                if i['reportinglevel'] == -1:
                                    rep = "ADMIN"
                                else:
                                    rep = "---"
                            da.append({'status': i['status'], 'remark': i['remark'], 'approval_date': i['approvaldate'], 'by': rep})

                        if str(pr['fhalf']) == '0':
                            fhalf = "FULL DAY"
                        elif str(pr['fhalf']) == '1':
                            fhalf = "FIRST HALF"
                        else:
                            fhalf = "SECOND HALF"

                        if str(pr['thalf']) == '0':
                            thalf = "FULL DAY"
                        elif str(pr['thalf']) == '1':
                            thalf = "FIRST HALF"
                        else:
                            thalf = "SECOND HALF"

                        data.append({'requestdate': pr['requestdate'], 'fdate': pr['fromdate'], 'tdate': pr['todate'], 'days': pr['days'], 'reason': pr['reason'], 'fhalf': fhalf, 'thalf': thalf, 'final_status': pr['finalstatus'], 'finalapprovaldate': pr['finalapprovaldate'], 'reportinglevel_status': da, 'leave_type': pr['leavecode__leave_name'], 'sno': pr['leaveid']})

                    status = 200

                else:
                    status = 502
            else:
                status = 403
                msg = "Not Authorized"
        else:
            status = 401
            msg = "Authentication failed"

    else:
        status = 500
        msg = "Technical error : wrong parameters"
    data_send = {'data': data}
    return JsonResponse(data=data_send, status=status)


def view_leave(request):
    error = True
    msg = ''
    data_details = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337, 1345])
            if check == 200:
                if request.method == 'GET':
                    qry_od = LeaveType.objects.filter(leave_abbr="OD").values('id', 'leave_name')
                    qry_co = LeaveType.objects.filter(leave_abbr="CO").values('id', 'leave_name')
                    data = []
                    data.append({'name': qry_od[0]['leave_name'], 'id': qry_od[0]['id']})
                    data.append({'name': qry_co[0]['leave_name'], 'id': qry_co[0]['id']})
                    data.append({'name': "Normal Leave", 'id': -1})
                    qry1 = EmployeeDropdown.objects.filter(field='CATEGORY OF EMPLOYEE').exclude(value__isnull=True).values('sno', 'value')
                    msg = 'Success'
                    error = False
                    status = 200
                    data = {'msg': msg, 'data': list(qry1), 'data1': data, 'error': error}

                if request.method == 'POST':
                    inp = json.loads(request.body)
                    if inp['id'] == '1':

                        fdate = inp['FromDate']
                        tdate = inp['ToDate']

                        qry_od = LeaveType.objects.filter(leave_abbr="OD").values('id', 'leave_name')
                        qry_co = LeaveType.objects.filter(leave_abbr="CO").values('id', 'leave_name')

                        leave_id = inp['Leave']
                        try:
                            status = inp['status']
                        except:
                            status = "ALL"

                        FromDate = datetime.datetime.strptime(fdate, '%Y-%m-%d').date()
                        ToDate = datetime.datetime.strptime(tdate, '%Y-%m-%d').date()
                        Dept = inp['Dept']
                        Category = inp['Category']

                        filter_data = {}
                        if status != "ALL":
                            filter_data['leaveid__finalstatus__contains'] = status
                        if Dept != "ALL":
                            filter_data['leaveid__emp_id__dept'] = Dept
                        if Category != "ALL":
                            filter_data['leaveid__emp_id__emp_category'] = Category
                        if leave_id != "ALL" and (leave_id != "-1" or leave_id != "-1"):
                            filter_data['leaveid__leavecode'] = leave_id

                        if leave_id == -1 or leave_id == "-1":
                            qry = Leaveapproval.objects.filter(**filter_data).filter(leaveid__fromdate__gte=FromDate, leaveid__todate__lte=ToDate).exclude(leaveid__leavecode=qry_od[0]['id']).exclude(leaveid__leavecode=qry_co[0]['id']).values('approved_by', 'leaveid__emp_id__name', 'dept__value', 'leaveid__requestdate', 'leaveid__leavecode__leave_abbr', 'leaveid__fromdate', 'leaveid__todate', 'leaveid__days', 'leaveid__reason', 'leaveid__filename', 'leaveid__finalstatus', 'leaveid', 'leaveid__emp_id', 'leaveid__leavecode__leave_name','leaveid__category__value', 'leaveid__subtype__value')
                        else:
                            qry = Leaveapproval.objects.filter(**filter_data).filter(leaveid__fromdate__gte=FromDate, leaveid__todate__lte=ToDate).values('approved_by', 'leaveid__emp_id__name', 'dept__value', 'leaveid__requestdate', 'leaveid__leavecode__leave_abbr', 'leaveid__fromdate', 'leaveid__todate', 'leaveid__days', 'leaveid__reason', 'leaveid__filename', 'leaveid__finalstatus', 'leaveid', 'leaveid__emp_id', 'leaveid__leavecode__leave_name', 'leaveid__category__value', 'leaveid__subtype__value')
                        qry1=list(qry)
                        status = 200
                        data = {'error': error, 'msg': msg, 'data': list(qry)}
                    if inp['id'] == '2':
                        emp_id = inp['leave_id']
                        qry = Leaveapproval.objects.filter(leaveid=emp_id).values('leaveid')
                        i = 0
                        Arr = []
                        for a in qry:
                            qry3 = Leaveapproval.objects.filter(leaveid=qry[i]['leaveid']).values('status', 'remark', 'approvaldate').order_by('reportinglevel')
                            if qry3.count() > 0:
                                Lis = []
                                for b in qry3:
                                    msg = "Success"
                                    error = False

                                    Lis.append(b)
                                if 'Lis' in locals():
                                    a['RemarkStatusApprovalDate'] = Lis
                            else:
                                Lis.append({'status': '', 'remark': '', 'approvaldate': ''})
                            Arr.append(a)
                        data_details['PreviousLeaves'] = list(Arr)
                        status = 200
                        data = {'error': error, 'msg': msg, 'data': data_details}
            else:
                status = 403
        else:
            status = 401
    else:
        status = 400
    data = {'msg': msg, 'data': data}
    return JsonResponse(status=status, data=data)


def leaveLapsescript(request):
    todaydate = (datetime.datetime.now() + datetime.timedelta(minutes=330)).date()
    leavetype = LeaveType.objects.filter(lapse_start=todaydate, status='INSERT', leave_status='L').values('id', 'leaveforgender', 'leave_status', 'lapse_month', 'accumulate_max', 'credit_day')

    for leave in leavetype:
        qry_check = LeaveLapseLog.objects.filter(leave_id=leave['id'], lapsedate=todaydate).values()

        if(qry_check.count() == 0):
            qry_leave = Leaveremaning.objects.filter(leaveid=leave['id']).update(remaining=0)
            qry_log = LeaveLapseLog.objects.create(leave_id=LeaveType.objects.get(id=leave['id']), lapsedate=todaydate)
            nextdate = add_months(todaydate, leave['lapse_month'])
            leavetypeupdate = LeaveType.objects.filter(id=leave['id']).update(lapse_start=nextdate)
    leaveCreditscript()
    return HttpResponse("okay")


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def leaveCreditscript():
    todaydate = (datetime.datetime.now() + datetime.timedelta(minutes=330)).date()
    leave_typ = LeaveType.objects.filter(credit_day=todaydate, status='INSERT').values('id', 'leaveforgender', 'leave_status', 'accumulate_max', 'credit_day', 'credittype')

    for leave in leave_typ:
        leaveqota = LeaveQuota.objects.filter(leave_id=leave['id'], status='INSERT').values('no_of_leaves', 'category_emp', 'designation', 'type_of_emp')
        for qota in leaveqota:
            qry_duplicate = LeaveCreditLog.objects.filter(creditdate=leave['credit_day'], category_emp=qota['category_emp'], designation=qota['designation'], type_of_emp=qota['type_of_emp'], leave_id=leave['id'])
            if(qry_duplicate.count() == 0):

                qry_emp = EmployeePrimdetail.objects.filter(desg=qota['designation'], emp_category=qota['category_emp'], emp_type=qota['type_of_emp'], emp_status='ACTIVE').values('emp_id')

                for emp in qry_emp:
                    gender = EmployeePerdetail.objects.filter(emp_id=emp['emp_id']).values('gender__value')
                    if(gender[0]['gender__value'] == 'MALE'):
                        gen = 'M'
                    else:
                        gen = 'F'
                    if(leave['leaveforgender'] == 'B' or leave['leaveforgender'] == gen):
                        qry_rem = Leaveremaning.objects.filter(empid=emp['emp_id'], leaveid=leave['id']).values('remaining')

                        if(qry_rem.count() > 0):
                            if(leave['leave_status'] == 'A'):
                                new_leavecount = qry_rem[0]['remaining'] + qota['no_of_leaves']
                                if(new_leavecount <= leave['accumulate_max']):
                                    leaveno = qry_rem[0]['remaining'] + qota['no_of_leaves']
                                else:
                                    leaveno = leave['accumulate_max']
                            elif(leave['leave_status'] == 'L'):

                                leaveno = qry_rem[0]['remaining'] + qota['no_of_leaves']
                            qry_update = Leaveremaning.objects.filter(empid=emp['emp_id'], leaveid=leave['id']).update(remaining=leaveno)
                        else:
                            qry_insert = Leaveremaning.objects.create(empid=EmployeePrimdetail.objects.get(emp_id=emp['emp_id']), leaveid=LeaveType.objects.get(id=leave['id']), remaining=qota['no_of_leaves'])
            qry_log = LeaveCreditLog.objects.create(no_of_leaves=qota['no_of_leaves'], creditdate=date.today(), category_emp=EmployeeDropdown.objects.get(sno=qota['category_emp']), designation=EmployeeDropdown.objects.get(sno=qota['designation']), type_of_emp=EmployeeDropdown.objects.get(sno=qota['type_of_emp']), leave_id=LeaveType.objects.get(id=leave['id']))
        nextdate = add_months(leave['credit_day'], int(leave['credittype']))
        leavetypeupdate = LeaveType.objects.filter(id=leave['id']).update(credit_day=nextdate)

    return 1


def get_leaves_remaining(request):
    msg = ""
    data = {}
    qry_lv = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'GET':
                    qry_lv = Leaveremaning.objects.filter(empid=request.session['hash1']).values('remaining', 'leaveid__leave_abbr')

                    status = 200

            else:
                status = 502
        else:
            status = 403
    else:
        status = 401

    data_send = {'data': list(qry_lv)}
    return JsonResponse(data=data_send, status=status)


def LeaveCountReport(request):
    msg = ""
    data = {}
    leave_count_arr = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211])
            if check == 200:
                if request.method == 'GET':
                    qry_get_normal_leaves = LeaveType.objects.exclude(leave_abbr='OD').exclude(leave_abbr='CO').filter(status="INSERT").values('leave_name', 'leave_abbr', 'id')
                    qry_get_emps = EmployeePrimdetail.objects.exclude(emp_id="00007").values('emp_id', 'name', 'dept__value', 'desg__value', 'emp_category__value').order_by('name')
                    i = 1
                    for q in qry_get_emps:
                        emp_data = {}
                        emp_data = {'id': i, 'emp_code': q['emp_id'], 'emp_name': q['name'], 'dept': q['dept__value'], 'desg': q['desg__value'], 'category': q['emp_category__value']}
                        for n in qry_get_normal_leaves:

                            qry_lv = Leaveremaning.objects.filter(empid=q['emp_id'], leaveid=n['id']).values('remaining')

                            if len(qry_lv) > 0:
                                emp_data[n['id']] = qry_lv[0]['remaining']
                            else:
                                emp_data[n['id']] = "----"
                        leave_count_arr.append(emp_data)
                        i += 1

                    data_send = {'data': leave_count_arr, 'normal_leaves': list(qry_get_normal_leaves)}
                    status = 200

            else:
                status = 502
        else:
            status = 403
    else:
        status = 401

    return JsonResponse(data=data_send, status=status)


def lock_monthly_report(request):
    msg = ""
    data = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211])
            if check == 200:
                if request.method == 'POST':
                    inp = json.loads(request.body)

                    session = acc.views.getCurrentSession(None)
                    qry_month = AccountsSession.objects.filter(id=session).values('current_sal_month')
                    month = qry_month[0]['current_sal_month']
                    year = int(inp['year'])
                    qry_duplicate = DaysGenerateLog.objects.filter(sessionid=session, month=inp['month']).values()

                    if(qry_duplicate.count() > 0):
                        check = 1
                        msg = "Days of this month has been already generated"
                        status = 200
                    elif(month != inp['month']):
                        check = 1
                        msg = "Salary of previous month has not been locked. Kindly contact Accounts department."
                        status = 200
                    else:

                        date = datetime.date(year, month, 1)
                        fdate = datetime.date(year, month, 1).strftime('%Y-%m-%d')
                        range1 = calendar.monthrange(year, month)
                        tdate = datetime.date(year, month, range1[1]).strftime('%Y-%m-%d')
                        global_array = []
                        qry_arr = []

                        dept = []
                        coe = []

                        qry_dept = EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value__isnull=True).values('sno')
                        dept = [d['sno'] for d in qry_dept]

                        qry_coe = EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).values('sno')
                        coe = [c['sno'] for c in qry_coe]

                        qry = EmployeePrimdetail.objects.filter(dept__in=dept, emp_category__in=coe, emp_status='ACTIVE').exclude(emp_type=219).values('emp_id', 'name', 'dept__value', 'desg__value', 'doj', 'dept', 'desg', 'emp_category', 'title')

                        dept = "All"

                        for emp in qry:
                            dat = calculate_working_days(emp['emp_id'], fdate, tdate, emp['name'], emp['dept__value'])

                            qry_lock = EmployeePayableDays.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp['emp_id']), session=AccountsSession.objects.get(id=session), month=month, defaults={'total_days': range1[1], 'working_days': dat['present'], 'leave': dat['leave'], 'holidays': dat['holiday'], 'added_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), 'dept': EmployeeDropdown.objects.get(sno=emp['dept']), 'desg': EmployeeDropdown.objects.get(sno=emp['desg']), 'emp_category': EmployeeDropdown.objects.get(sno=emp['emp_category']), 'title': EmployeeDropdown.objects.get(sno=emp['title'])})

                        lockdate = date.today()
                        qry_lock_log = DaysGenerateLog.objects.update_or_create(sessionid=AccountsSession.objects.get(id=session), month=month, defaults={'date': lockdate}, year=year)
                        # qry_cancel_leave=Leaveapproval.objects.filter(leaveid__fromdate__lt = lockdate,leaveid__finalstatus='PENDING').update(leaveid__finalstatus='AUTO CANCELLED',status='AUTO CANCELLED')
                        status = 200
                        check = 0
                        msg = "Days Successfully Locked"

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    data_send = {'check': check, 'msg': msg}
    return JsonResponse(data=data_send, status=status)


def check_month_locked(fromdate, todate):
    fromdate = datetime.datetime.strptime(str(fromdate), "%Y-%m-%d").date()
    todate = datetime.datetime.strptime(str(todate), "%Y-%m-%d").date()
    month1 = fromdate.month
    month2 = todate.month
    year1 = fromdate.year
    year2 = todate.year
    session1 = acc.views.getCurrentSession(fromdate)
    session2 = acc.views.getCurrentSession(todate)

    qry_check = DaysGenerateLog.objects.filter(sessionid=AccountsSession.objects.get(id=session1), month=month1, year=year1).values('id')
    if len(qry_check) > 0:
        return True

    qry_check = DaysGenerateLog.objects.filter(sessionid=AccountsSession.objects.get(id=session2), month=month2, year=year2).values('id')
    if len(qry_check) > 0:
        return True

    return False


def store_email(send_to, subject, message):
    print()
    # send_to="satyamg025@gmail.com"
    # yag = yagmail.SMTP({'erp@kiet.edu':'Team ERP'}, 'sc6500@@').send(send_to,subject,message)
    # q_store = MailService.objects.create(subject=subject,send_to=send_to,message=message,status='Y')


def faculty_working_days_report(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS:
        session = request.session['Session']
        session_name = request.session['Session_name']
        sem_type = request.session['sem_type']
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                category = request.GET['category'].split(',')
                from_date = datetime.datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
                to_date = datetime.datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
                department = request.GET['dept'].split(',')
                org = request.GET['org']

                emps = EmployeePrimdetail.objects.filter(emp_category__in=category, dept__in=department, organization=org).exclude(emp_id="00007").exclude(emp_status="SEPARATE").values('emp_id', 'name', 'dept__value', 'dept', 'desg', 'desg__value', 'current_pos', 'current_pos__value', 'emp_type', 'emp_type__value')

                for emp in emps:
                    emp_data = {}
                    attendance_per = 0
                    for k, v in emp.items():
                        emp_data[k] = v
                    total_present = Attendance2.objects.filter(Emp_Id=emp['emp_id'], date__range=[from_date, to_date], status='P').values().count()
                    total_working = Attendance2.objects.filter(Emp_Id=emp['emp_id'], date__range=[from_date, to_date]).exclude(status="H").values().count()

                    leave_count = employee_leave_count_date_range(emp['emp_id'], from_date, to_date)
                    total_od = 0
                    for leave in leave_count:
                        if leave['label'] == "OD":
                            total_od = leave['data']
                    emp_data['present'] = total_present
                    emp_data['od_count'] = total_od
                    emp_data['total_working'] = total_working

                    working_days = total_present + total_od
                    emp_data['p_od'] = working_days

                    if total_working != 0 and total_working != None:
                        attendance_per = float(working_days / total_working) * 100
                    emp_data['attendance_per'] = round(attendance_per, 2)
                    data.append(emp_data)
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def update_reporting():
    data = []
    get_data = SeparationReporting.objects.values('reporting_no', 'emp_id', 'sno').order_by('emp_id', 'reporting_no')
    emp_id = set()
    i = 1
    for d in get_data:
        if d['emp_id'] not in emp_id:

            i = 1
            emp_id.add(d['emp_id'])
        SeparationReporting.objects.filter(sno=d['sno']).update(reporting_no=i)
        i += 1
    print("DONE")
# update_reporting()

