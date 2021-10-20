# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
import json
import urllib
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import time
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum, Count, Max
from login.models import EmployeePrimdetail
from musterroll.models import EmployeePerdetail, Reporting
from datetime import date
from datetime import datetime
import calendar
from operator import itemgetter
from login.views import checkpermission
from .models import *
import io
from leave.models import Holiday
from threading import Thread
import requests
from random import randint
import time


def Ticketing_Dropdown(request):
    data = {}
    qry1 = ""

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'general':
                        qry1 = TicketingDropdown.objects.filter(value=None).extra(select={'fd': 'field', 'id': 'sno', 'parent': 'pid'}).values('fd', 'id', 'parent').exclude(status="DELETE").distinct()
                        for field1 in qry1:
                            if field1['parent'] != 0:
                                pid = field1['parent']
                                qry2 = TicketingDropdown.objects.filter(sno=pid).exclude(status="DELETE").values('field')
                                field1['fd'] = field1['fd'] + '(' + qry2[0]['field'] + ')'
                        msg = "Success"
                        error = False
                        if not qry1:
                            msg = "No Data Found!!"
                        status = 200
                        data = {'msg': msg, 'data': list(qry1)}

                    elif request.GET['request_type'] == 'subcategory':
                        sno = request.GET['Sno']
                        names = TicketingDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('field', 'pid')
                        name = names[0]['field']
                        p_id = names[0]['pid']

                        qry1 = TicketingDropdown.objects.filter(field=name, pid=p_id).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'valueid': 'sno', 'parentId': 'pid', 'cat': 'field', 'text1': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('valueid', 'parentId', 'cat', 'text1', 'edit', 'delete')
                        for x in range(0, len(qry1)):
                            test = TicketingDropdown.objects.filter(pid=qry1[x]['valueid']).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'subid': 'sno', 'subvalue': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('subid', 'subvalue', 'edit', 'delete')
                            qry1[x]['subcategory'] = list(test)
                        msg = "Success"
                        data = {'msg': msg, 'data': list(qry1)}
                        status = 200

                elif request.method == 'DELETE':
                    data = json.loads(request.body)
                    qry = TicketingDropdown.objects.filter(sno=data['del_id']).exclude(status="DELETE").values('field')
                    if(qry.exists()):
                        sno = data['del_id']
                        fd = qry[0]['field']
                        deletec(sno)
                        q2 = TicketingDropdown.objects.filter(field=fd).exclude(status="DELETE").exclude(value__isnull=True).values().count()
                        if q2 == 0:
                            q3 = TicketingDropdown.objects.filter(field=fd).exclude(status="DELETE").update(status="DELETE")
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
                        field_qry = TicketingDropdown.objects.filter(sno=field_id).exclude(status="DELETE").values('field')
                        field = field_qry[0]['field']
                        if pid != 0:
                            field_qry = TicketingDropdown.objects.filter(sno=pid).exclude(status="DELETE").exclude(value__isnull=True).values('value')
                            field = field_qry[0]['value']
                            cnt = TicketingDropdown.objects.filter(field=field).exclude(status="DELETE").values('sno')
                            if len(cnt) == 0:
                                add = TicketingDropdown.objects.create(pid=pid, field=field)

                        qry_ch = TicketingDropdown.objects.filter(Q(field=field) & Q(value=value)).filter(pid=pid).exclude(status="DELETE")
                        if(len(qry_ch) > 0):
                            status = 409

                        else:
                            created = TicketingDropdown.objects.create(pid=pid, field=field, value=value)
                            msg = "Successfully Inserted"
                            data = {'msg': msg}
                            status = 200

                elif request.method == 'PUT':
                    body = json.loads(request.body)
                    sno = body['sno1']
                    val = body['val'].upper()
                    field_qry = TicketingDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('pid', 'value')
                    pid = field_qry[0]['pid']
                    value = field_qry[0]['value']
                    add = TicketingDropdown.objects.filter(pid=pid, field=value).exclude(status="DELETE").update(field=val)
                    add = TicketingDropdown.objects.filter(sno=sno).exclude(status="DELETE").update(value=val, status="UPDATE")
                    add = TicketingDropdown.objects.filter(pid=sno).exclude(status="DELETE").update(field=val, status="UPDATE")
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
    qry = TicketingDropdown.objects.filter(pid=pid).exclude(status="DELETE").values('sno')
    if len(qry) > 0:
        for x in qry:
            deletec(x['sno'])
    qry = TicketingDropdown.objects.filter(sno=pid).exclude(status="DELETE").update(status="DELETE")


def get_category():
    qry_cat = TicketingDropdown.objects.filter(field='TICKETING CATEGORY').exclude(value__isnull=True).exclude(status='DELETE').values('sno', 'value')
    return list(qry_cat)


def get_subcategory(cat_li):
    qry_sub_cat = TicketingDropdown.objects.filter(pid__in=cat_li).exclude(value__isnull=True).exclude(status='DELETE').values('sno', 'value')
    return list(qry_sub_cat)


def get_priority():
    qry_priority = TicketingDropdown.objects.filter(field='PRIORITY').exclude(value__isnull=True).exclude(status='DELETE').values('sno', 'value')
    return list(qry_priority)


def calculate_no_of_holidays(f_date, t_date, dept):
    qry_holi = Holiday.objects.filter(f_date__lte=t_date, dept=dept, t_date__gte=f_date).exclude(status='DELETE').values('f_date', 't_date')
    number = 0
    for h in qry_holi:
        number += (min(h['t_date'], t_date) - max(h['f_date'], f_date)).days + 1

    return number


def check_self_escalate(emp_id):
    # qry_dept_desg=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept','desg')
    # qry_reporting_emp =  Reporting.objects.filter(department=qry_dept_desg[0]['dept'],reporting_to=qry_dept_desg[0]['desg']).exclude(department__isnull=True).values_list('emp_id',flat=True)

    # qry_rep_grievance = TicketingApproval.objects.filter(emp_id__in=qry_reporting_emp,coord_status='PENDING').exclude(redressal_id__category__value__contains='ERP').values('time_stamp','redressal_id__priority__hours','id','redressal_id','emp_id')

    # for grievance in qry_rep_grievance:
    # 	q_dept_desg=EmployeePrimdetail.objects.filter(emp_id=grievance['emp_id']).values('dept','desg')
    # 	f_date = datetime.strptime(str(grievance['time_stamp']).split(' ')[0], '%Y-%m-%d').date()
    # 	t_date = date.today()
    # 	no_of_holidays=calculate_no_of_holidays(f_date,t_date,q_dept_desg[0]['dept'])

    # 	time1=grievance['time_stamp']+timedelta(days=no_of_holidays)+timedelta(hours=grievance['redressal_id__priority__hours'])
    # 	now=datetime.now()

    # 	if time1<now:
    # 		qry_get_last_reporting = Reporting.objects.filter(emp_id=grievance['emp_id']).exclude(department__isnull=True).values('department','reporting_to').order_by('-reporting_no')[:1]
    # 		if qry_get_last_reporting[0]['department'] == qry_dept_desg[0]['dept'] and qry_get_last_reporting[0]['reporting_to'] == qry_dept_desg[0]['desg']:
    # 			qry_escalate_update = TicketingApproval.objects.filter(id=grievance['id']).update(remark='ESCALATED',action_time=datetime.now(),coord_status='ESCALATED')

    # 			qry_ins = TicketingApproval.objects.create(redressal_id=TicketingInsert.objects.get(id=grievance['redressal_id']),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id))
    pass


def check_should_escalate(id, emp_id):
    return False
    # qry_dept_desg=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept','desg')
    # qry_get_last_reporting = Reporting.objects.filter(emp_id=emp_id).values('department','reporting_to').exclude(department__isnull=True).order_by('-reporting_no')[:1]
    # if len(qry_get_last_reporting)==0:
    # 	return False
    # qry_get_rep_em = EmployeePrimdetail.objects.filter(dept=qry_get_last_reporting[0]['department'],desg=qry_get_last_reporting[0]['reporting_to']).values('emp_id')
    # if len(qry_get_rep_em)==0:
    # 	return False

    # qry_rep_grievance = TicketingApproval.objects.filter(id=id).exclude(redressal_id__category__value__contains='ERP').values('time_stamp','redressal_id__priority__hours','id','redressal_id')
    # if len(qry_rep_grievance)==0:
    # 	return False

    # f_date = datetime.strptime(str(qry_rep_grievance[0]['time_stamp']).split(' ')[0], '%Y-%m-%d').date()
    # t_date = date.today()
    # no_of_holidays=calculate_no_of_holidays(f_date,t_date,qry_dept_desg[0]['dept'])

    # time1=qry_rep_grievance[0]['time_stamp']+timedelta(days=no_of_holidays)+timedelta(hours=qry_rep_grievance[0]['redressal_id__priority__hours'])
    # now=datetime.now()

    # if now>time1:
    # 	qry_escalate_update = TicketingApproval.objects.filter(id=qry_rep_grievance[0]['id']).update(remark='ESCALATED',action_time=datetime.now(),coord_status='ESCALATED')

    # 	qry_ins = TicketingApproval.objects.create(redressal_id=TicketingInsert.objects.get(id=qry_rep_grievance[0]['redressal_id']),emp_id=EmployeePrimdetail.objects.get(emp_id=qry_get_rep_em[0]['emp_id']))

    # 	return True
    # return False


def getComponents(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = 200
            if check == 200:
                if(request.method == 'GET'):
                    if request.GET['request_type'] == 'category':
                        query = get_category()
                    elif request.GET['request_type'] == 'sub_category':
                        query = get_subcategory(request.GET['category'].split(","))
                    elif request.GET['request_type'] == 'priority':
                        query = get_priority()
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


def AssignCoordinator(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if(request.method == 'GET'):
                    if request.GET['request_type'] == 'view_previous':
                        qry_data = TicketingCoordinator.objects.exclude(status='DELETE').values('category', 'subCategory', 'emp_id', 'category__value', 'subCategory__value', 'emp_id__name')

                        data_values = {'data': list(qry_data)}
                        status = 200

                elif(request.method == 'POST'):
                    data = json.loads(request.body)
                    category = TicketingDropdown.objects.get(sno=data['category'])
                    emp_id = EmployeePrimdetail.objects.get(emp_id=data['emp_id'])
                    added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])

                    qry_check = TicketingCoordinator.objects.filter(category=category, subCategory__in=data['sub_category']).update(status='DELETE')

                    objs = (TicketingCoordinator(category=category, emp_id=emp_id, added_by=added_by, subCategory=TicketingDropdown.objects.get(sno=sub_cat)) for sub_cat in data['sub_category'])
                    qry_ins = TicketingCoordinator.objects.bulk_create(objs)

                    status = 200
                    data_values = {'msg': "Coordinator Successfully Assigned"}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def AssignPriority(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if(request.method == 'GET'):
                    if request.GET['request_type'] == 'view_previous':
                        qry_data = TicketingPriority.objects.exclude(status='DELETE').values('priority', 'priority__value', 'hours')

                        data_values = {'data': list(qry_data)}
                        status = 200

                elif(request.method == 'POST'):
                    data = json.loads(request.body)
                    priority = TicketingDropdown.objects.get(sno=data['priority'])

                    qry_check = TicketingPriority.objects.filter(priority=priority).update(status='DELETE')

                    qry_ins = TicketingPriority.objects.create(priority=priority, hours=data['hours'])

                    status = 200
                    data_values = {'msg': "Priority Added Successfully"}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def Ticketing_Insert(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Employee':
                if(request.method == 'GET'):
                    if request.GET['request_type'] == 'view_previous':
                        qry_data = TicketingInsert.objects.filter(emp_id=request.session['hash1']).extra(select={'timestamp': "DATE_FORMAT(timestamp,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('category', 'category__value', 'subCategory', 'subCategory__value', 'priority', 'priority__priority__value', 'priority__hours', 'id', 'description', 'attachment', 'griev_sugg', 'ticket_num', 'final_status', 'status', 'feedback', 'timestamp', 'emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value')

                        for qd in qry_data:
                            qry_level_data = TicketingApproval.objects.filter(redressal_id=qd['id']).extra(select={'action_time': "DATE_FORMAT(action_time,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('coord_status', 'remark', 'action_time')
                            qd['level_data'] = list(qry_level_data)

                        data_values = {'data': list(qry_data)}
                        status = 200

                elif(request.method == 'POST'):
                    data = json.loads(request.body)
                    q_last_grv = TicketingInsert.objects.values('id').order_by('-id')[:1]
                    if len(q_last_grv) == 0:
                        num = 1
                    else:
                        num = q_last_grv[0]['id'] + 1

                    if data['griev_sugg'] == 'T':
                        ticket_number = "TCKT" + str(num)
                    else:
                        ticket_number = "SUGG" + str(num)
                    pri_id = TicketingPriority.objects.filter(priority=data['priority']).exclude(status='DELETE').values('id')
                    if len(pri_id) > 0:
                        priority = TicketingPriority.objects.get(id=pri_id[0]['id'])
                    else:
                        priority = None

                    if data['file_name'] != None and len(data['file_name']) > 0:
                        attachment = "Ticketing/" + data['file_name']
                    else:
                        attachment = None
                    print(request.session.keys())
                    qry_ins = TicketingInsert.objects.create(category=TicketingDropdown.objects.get(sno=data['category']), subCategory=TicketingDropdown.objects.get(sno=data['sub_category']), priority=priority, description=data['description'], attachment=attachment, griev_sugg=data['griev_sugg'], emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), ticket_num=ticket_number)

                    qry_coord = TicketingCoordinator.objects.filter(category=data['category'], subCategory=data['sub_category']).exclude(status='DELETE').values('emp_id')
                    if len(qry_coord) > 0:
                        q_app_ins = TicketingApproval.objects.create(redressal_id=TicketingInsert.objects.get(id=qry_ins.id), emp_id=EmployeePrimdetail.objects.get(emp_id=qry_coord[0]['emp_id']))
                    status = 200
                    data_values = {'msg': "Grievance Inserted Successfully"}

                elif(request.method == 'PUT'):
                    data = json.loads(request.body)

                    q_update_feedback = TicketingInsert.objects.filter(id=data['id']).update(feedback=data['feedback'])

                    q_update_feedback = TicketingInsert.objects.filter(id=data['id']).values('category', 'subCategory', 'priority', 'emp_id', 'description', 'attachment', 'griev_sugg', 'ticket_num', 'emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value')
                    if data['feedback'] == 'REOPEN':
                        q_last_grv = TicketingInsert.objects.values('id').order_by('-id')[:1]
                        if len(q_last_grv) == 0:
                            num = 1
                        else:
                            num = q_last_grv[0]['id'] + 1

                        if q_update_feedback[0]['priority'] is not None:
                            priority = TicketingPriority.objects.get(id=q_update_feedback[0]['priority'])
                        else:
                            priority = None
                        qry_ins = TicketingInsert.objects.create(category=TicketingDropdown.objects.get(sno=q_update_feedback[0]['category']), subCategory=TicketingDropdown.objects.get(sno=q_update_feedback[0]['subCategory']), priority=priority, description=data['description'], attachment=q_update_feedback[0]['attachment'], griev_sugg=q_update_feedback[0]['griev_sugg'], emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), ticket_num=q_update_feedback[0]['ticket_num'], ticket_type='R')
                        qry_coord = TicketingCoordinator.objects.filter(category=q_update_feedback[0]['category'], subCategory=q_update_feedback[0]['subCategory']).exclude(status='DELETE').values('emp_id')
                        if len(qry_coord) > 0:
                            q_app_ins = TicketingApproval.objects.create(redressal_id=TicketingInsert.objects.get(id=qry_ins.id), emp_id=EmployeePrimdetail.objects.get(emp_id=qry_coord[0]['emp_id']))
                        status = 200
                        data_values = {'msg': "Grievance Reopened Successfully"}
                    else:
                        status = 200
                        data_values = {'msg': "Feedback Sumitted Successfully"}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def CoordinatorApprove(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if(request.method == 'GET'):
                    if request.GET['request_type'] == 'view_previous':
                        qry_data = TicketingApproval.objects.filter(emp_id=request.session['hash1']).exclude(coord_status='PENDING').extra(select={'timestamp': "DATE_FORMAT(timestamp,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('remark', 'redressal_id', 'redressal_id__category__value', 'redressal_id__subCategory__value', 'redressal_id__priority__priority__value', 'redressal_id__description', 'redressal_id__attachment', 'redressal_id__griev_sugg', 'redressal_id__ticket_num', 'redressal_id__ticket_type', 'timestamp', 'redressal_id__emp_id__name', 'id', 'redressal_id__emp_id', 'redressal_id__feedback', 'redressal_id__final_status', 'redressal_id__emp_id__dept__value', 'redressal_id__emp_id__desg__value', 'coord_status')

                        for qd in qry_data:
                            if qd['redressal_id__griev_sugg'] == 'T':
                                qd['redressal_id__griev_sugge'] = 'TICKET'
                            elif qd['redressal_id__griev_sugg'] == 'S':
                                qd['redressal_id__griev_sugge'] = 'SUGGESTION'

                            if qd['redressal_id__ticket_type'] == 'N':
                                qd['redressal_id__ticket_type'] = 'NEW'
                            elif qd['redressal_id__ticket_type'] == 'R':
                                qd['redressal_id__ticket_type'] = 'REOPENED'

                            q_check = TicketingApproval.objects.filter(redressal_id=qd['redressal_id'], id__lt=qd['id']).values('emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value', 'remark').order_by('-id')[:1]

                            if len(q_check) > 0:
                                qd['forwarded_by'] = q_check[0]
                            else:
                                qd['forwarded_by'] = {}

                            q_check2 = TicketingApproval.objects.filter(redressal_id=qd['redressal_id'], id__gt=qd['id']).values('emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value', 'remark').order_by('id')[:1]

                            if len(q_check2) > 0:
                                qd['forwarded_to'] = q_check2[0]
                            else:
                                qd['forwarded_to'] = {}

                            # q_check = TicketingApproval.objects.filter(redressal_id=qd['redressal_id']).exclude(id=qd['id']).values('emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','remark','redressal_id__emp_id__name','redressal_id__emp_id','redressal_id__emp_id__dept__value','redressal_id__emp_id__desg__value').order_by('-id')[:1]
                            # if len(q_check)>0:
                            #   qd['forwarded_by'] = q_check[0]
                            # else:
                            #   qd['forwarded_by'] = {}

                            q_prev_status = TicketingApproval.objects.filter(redressal_id=qd['redressal_id']).extra(select={'action_time': "DATE_FORMAT(action_time,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value', 'remark', 'action_time', 'redressal_id__emp_id__name', 'redressal_id__emp_id', 'redressal_id__emp_id__dept__value', 'redressal_id__emp_id__desg__value').order_by('id')
                            qd['prev_status'] = list(q_prev_status)

                        data_values = {'data': list(qry_data)}
                        status = 200

                    elif request.GET['request_type'] == 'form_data':

                        check_self_escalate(request.session['hash1'])
                        qry_data = TicketingApproval.objects.filter(emp_id=request.session['hash1'], coord_status='PENDING').extra(select={'timestamp': "DATE_FORMAT(timestamp,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('redressal_id', 'redressal_id__category__value', 'redressal_id__subCategory__value', 'redressal_id__priority__priority__value', 'redressal_id__description', 'redressal_id__attachment', 'redressal_id__griev_sugg', 'redressal_id__ticket_num', 'redressal_id__ticket_type', 'timestamp', 'id', 'redressal_id__emp_id__name', 'redressal_id__emp_id', 'redressal_id__emp_id__dept__value', 'redressal_id__emp_id__desg__value')

                        final_data = []
                        for qd in qry_data:
                            if check_should_escalate(qd['id'], request.session['hash1']):
                                continue

                            if qd['redressal_id__griev_sugg'] == 'T':
                                qd['redressal_id__griev_sugge'] = 'TICKET'
                            elif qd['redressal_id__griev_sugg'] == 'S':
                                qd['redressal_id__griev_sugge'] = 'SUGGESTION'

                            if qd['redressal_id__ticket_type'] == 'N':
                                qd['redressal_id__ticket_type'] = 'NEW'
                            elif qd['redressal_id__ticket_type'] == 'R':
                                qd['redressal_id__ticket_type'] = 'REOPENED'

                            q_check = TicketingApproval.objects.filter(redressal_id=qd['redressal_id']).exclude(id=qd['id']).values('emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value', 'coord_status').order_by('-id')[:1]
                            if len(q_check) > 0:
                                qd['forwarded_by'] = q_check[0]
                            else:
                                qd['forwarded_by'] = {}

                            q_prev_status = TicketingApproval.objects.filter(redressal_id=qd['redressal_id']).extra(select={'action_time': "DATE_FORMAT(action_time,'%%d-%%m-%%Y %%H:%%i:%%s')"}).exclude(id=qd['id']).values('emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value', 'remark', 'action_time', 'coord_status', 'redressal_id__emp_id__name', 'redressal_id__emp_id', 'redressal_id__emp_id__dept__value', 'redressal_id__emp_id__desg__value').order_by('id')
                            qd['prev_status'] = list(q_prev_status)
                            final_data.append(qd)

                        data_values = {'data': list(final_data)}
                        status = 200

                elif(request.method == 'POST'):
                    data = json.loads(request.body)
                    q_det = TicketingApproval.objects.filter(id=data['id']).values('redressal_id')
                    if data['status'] == 'C':
                        q_upd = TicketingApproval.objects.filter(id=data['id']).update(remark=data['remark'], coord_status='CLOSED', action_time=datetime.now())

                        q_upd2 = TicketingInsert.objects.filter(id=q_det[0]['redressal_id']).update(final_status='CLOSED')
                    elif data['status'] == 'F':
                        q_upd = TicketingApproval.objects.filter(id=data['id']).update(remark=data['remark'], coord_status='FORWARDED', action_time=datetime.now())

                        q_app_ins = TicketingApproval.objects.create(redressal_id=TicketingInsert.objects.get(id=q_det[0]['redressal_id']), emp_id=EmployeePrimdetail.objects.get(emp_id=data['emp_id']))

                    status = 200
                    data_values = {'msg': "Grievance Solved Successfully"}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def CoordinatorMultiApprove(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                d = json.loads(request.body)
                for data in d['id']:
                    q_det = TicketingApproval.objects.filter(id=data['id']).values('redressal_id')
                    if d['status'] == 'C':
                        q_upd = TicketingApproval.objects.filter(id=data['id']).update(remark=data['remark'], coord_status='CLOSED', action_time=datetime.now())

                        q_upd2 = TicketingInsert.objects.filter(id=q_det[0]['redressal_id']).update(final_status='CLOSED')
                    elif d['status'] == 'F':
                        q_upd = TicketingApproval.objects.filter(id=data['id']).update(remark=data['remark'], coord_status='FORWARDED', action_time=datetime.now())

                        q_app_ins = TicketingApproval.objects.create(redressal_id=TicketingInsert.objects.get(id=q_det[0]['redressal_id']), emp_id=EmployeePrimdetail.objects.get(emp_id=d['emp_id']))

                status = 200
                data_values = {'msg': "Grievance Solved Successfully"}

            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def ConsolidatedReport(request):
    data_values = {}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if(request.method == 'GET'):
                    if request.GET['request_type'] == 'form_data':
                        data_values = {
                            'category': get_category(),
                            'pripority': get_priority(),
                        }
                        status = 200
                    elif request.GET['request_type'] == 'table_data':
                        category = request.GET['category'].split(',')
                        subcategory = list(map(int, request.GET['sub_category'].split(',')))
                        griev_sugg = request.GET['type'].split(',')
                        priority = request.GET['priority'].split(",")

                        fromDate = datetime.strptime((str(request.GET['from_date']).split("T")[0]) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                        toDate = datetime.strptime((str(request.GET['to_date']).split("T")[0]) + " 23:59:59", "%Y-%m-%d %H:%M:%S")

                        final_data = []
                        total_pending = 0
                        total_closed = 0
                        total_reopen = 0
                        total_not_sat = 0
                        total_sat = 0

                        for cat in category:
                            q_cat_name = TicketingDropdown.objects.filter(sno=cat).values('value')

                            sub_cat_li = TicketingDropdown.objects.filter(pid=cat).exclude(value__isnull=True).exclude(status='DELETE').values_list('sno', flat=True)
                            sub = list(set(subcategory).intersection(sub_cat_li))

                            sub_data = []
                            cat_pending = 0
                            cat_closed = 0
                            cat_reopen = 0
                            cat_not_sat = 0
                            cat_sat = 0

                            for s in sub:
                                q_sub_name = TicketingDropdown.objects.filter(sno=s).values('value')

                                qry_pending = TicketingInsert.objects.filter(category=cat, subCategory=s, final_status='PENDING', griev_sugg__in=griev_sugg, priority__priority__in=priority, timestamp__range=[fromDate, toDate]).count()
                                qry_closed = TicketingInsert.objects.filter(category=cat, subCategory=s, final_status='CLOSED', griev_sugg__in=griev_sugg, priority__priority__in=priority, timestamp__range=[fromDate, toDate]).count()
                                qry_reopen = TicketingInsert.objects.filter(category=cat, subCategory=s, ticket_type='R', griev_sugg__in=griev_sugg, priority__priority__in=priority, timestamp__range=[fromDate, toDate]).count()
                                qry_not_sat = TicketingInsert.objects.filter(category=cat, subCategory=s, feedback='NS', griev_sugg__in=griev_sugg, priority__priority__in=priority, timestamp__range=[fromDate, toDate]).count()
                                qry_sat = TicketingInsert.objects.filter(category=cat, subCategory=s, feedback='S', priority__priority__in=priority, griev_sugg__in=griev_sugg, timestamp__range=[fromDate, toDate]).count()

                                cat_pending += qry_pending
                                cat_closed += qry_closed
                                cat_reopen += qry_reopen
                                cat_not_sat += qry_not_sat
                                cat_sat += qry_sat

                                sub_data.append({'sub_cat_id': s, 'sub_cat_name': q_sub_name[0]['value'], 'total': qry_pending + qry_closed, 'pending': qry_pending, 'closed': qry_closed, 'reopen': qry_reopen, 'not_satisfied': qry_not_sat, 'satisfied': qry_sat})

                            total_pending += cat_pending
                            total_closed += cat_closed
                            total_reopen += cat_reopen
                            total_not_sat += cat_not_sat
                            total_sat += cat_sat

                            final_data.append({'cat_id': cat, 'cat_name': q_cat_name[0]['value'], 'total': cat_pending + cat_closed, 'pending': cat_pending, 'closed': cat_closed, 'reopen': cat_reopen, 'not_satisfied': cat_not_sat, 'satisfied': cat_sat, 'sub_cat_data': sub_data})

                        data_values = {'data': final_data, 'total': total_pending + total_closed, 'pending': total_pending, 'closed': total_closed, 'reopen': total_reopen, 'not_satisfied': total_not_sat, 'satisfied': total_sat}
                        status = 200

                    elif request.GET['request_type'] == 'detail_data':
                        print(request.GET['from_date'], 'fromDate')
                        print(request.GET['to_date'], 'to_date')
                        fromDate = datetime.strptime((str(request.GET['from_date']).split("T")[0]) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                        toDate = datetime.strptime((str(request.GET['to_date']).split("T")[0]) + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                        print(fromDate, 'fromDate')
                        print(toDate, 'to_date')
                        extra_filter = {'category': request.GET['category'], 'subCategory': request.GET['sub_category']}
                        if request.GET['type'] == 'TOTAL':
                            pass
                        elif request.GET['type'] == 'PENDING':
                            extra_filter['final_status'] = 'PENDING'
                        elif request.GET['type'] == 'CLOSED':
                            extra_filter['final_status'] = 'CLOSED'
                        elif request.GET['type'] == 'REOPEN':
                            extra_filter['ticket_type'] = 'R'
                        elif request.GET['type'] == 'NOT_SATISFIED':
                            extra_filter['feedback'] = 'NS'
                        elif request.GET['type'] == 'SATISFIED':
                            extra_filter['feedback'] = 'S'

                        qry_data = TicketingInsert.objects.filter(timestamp__range=[fromDate, toDate]).filter(**extra_filter).extra(select={'timestamp': "DATE_FORMAT(timestamp,'%%d-%%m-%%Y %%H:%%i:%%s')"}).exclude(status="DELETE").values('id', 'category__value', 'subCategory__value', 'priority__priority__value', 'description', 'attachment', 'griev_sugg', 'ticket_num', 'ticket_type', 'timestamp', 'id', 'feedback', 'emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value')

                        for qd in qry_data:
                            if qd['griev_sugg'] == 'T':
                                qd['griev_sugg'] = 'TICKET'

                            elif qd['griev_sugg'] == 'S':
                                qd['griev_sugg'] = 'SUGGESTION'

                            if qd['ticket_type'] == 'N':
                                qd['ticket_type'] = 'NEW'
                            elif qd['ticket_type'] == 'R':
                                qd['ticket_type'] = 'REOPENED'

                            q_prev_status = TicketingApproval.objects.filter(redressal_id=qd['id']).extra(select={'action_time': "DATE_FORMAT(action_time,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value', 'remark', 'action_time', 'coord_status', 'redressal_id__emp_id__name', 'redressal_id__emp_id', 'redressal_id__emp_id__dept__value', 'redressal_id__emp_id__desg__value').order_by('id')

                            qd['prev_status'] = list(q_prev_status)
                            for x in qd['prev_status']:
                                image_path = EmployeePerdetail.objects.filter(emp_id=x['emp_id']).values_list('image_path', flat=True)

                                x['image_path'] = image_path[0]

                        data_values = {'data': list(qry_data)}
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
