
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# '''essentials'''
from django.http import JsonResponse
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
from datetime import date
import json
import datetime
import operator


# '''import constants'''
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

# '''import models'''
from musterroll.models import EmployeePerdetail, Roles
from login.models import EmployeePrimdetail

# '''import views'''
from login.views import checkpermission, generate_session_table_name
from Accounts.views import getCurrentSession
from AppraisalStaff.models import *


# Create your views here.

# STEPS :-
'''
	1. Create function for fetching data for specific part of question
	2. Create function for "FORMATTING" data for fetched data according to exact need of frontend
'''

# QUESTION SETTING


def appraisal_staff_question_setting(request):
    data = {}
    qry1 = ""
    session = getCurrentSession(None)

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'general':
                        form_type = request.GET['form_type']
                        form_part = request.GET['form_part']

                        qry1 = AppraisalStaffQuestion.objects.filter(statement=None, session=session, form_type=form_type, form_part=form_part).values(
                            'field', 'ques_id', 'parent_ques').exclude(status="DELETE").distinct()
                        for field1 in qry1:
                            if field1['parent_ques'] != 0:
                                parent_ques = field1['parent_ques']
                                qry2 = list(AppraisalStaffQuestion.objects.filter(ques_id=parent_ques, session=session,
                                                                                  form_type=form_type, form_part=form_part).exclude(status="DELETE").values('field'))

                                if qry2:
                                    field1['field'] = field1['field'] + \
                                        '(' + qry2[0]['field'] + ')'
                        msg = "Success"
                        error = False
                        if not qry1:
                            msg = "No Data Found!!"
                        status = 200
                        data = {'msg': msg, 'data': list(qry1)}

                    elif request.GET['request_type'] == 'subcategory':
                        form_type = request.GET['form_type']
                        form_part = request.GET['form_part']

                        ques_id = request.GET['ques_id']

                        names = AppraisalStaffQuestion.objects.filter(ques_id=ques_id,session=session).exclude(
                            status="DELETE").values('field', 'parent_ques')
                        print(names, ques_id)
                        if len(names) > 0:
                            name = names[0]['field']
                            p_id = names[0]['parent_ques']

                            qry1 = AppraisalStaffQuestion.objects.filter(field=name, parent_ques=p_id, session=session, form_type=form_type, form_part=form_part).exclude(
                                status="DELETE").exclude(statement__isnull=True).values('ques_id', 'parent_ques', 'field', 'statement', 'max_marks')

                            for x in range(0, len(qry1)):
                                test = AppraisalStaffQuestion.objects.filter(parent_ques=qry1[x]['ques_id'], session=session, form_type=form_type, form_part=form_part).exclude(
                                    status="DELETE").exclude(statement__isnull=True).values('ques_id', 'statement', 'max_marks')
                                qry1[x]['subcategory'] = list(test)

                            msg = "Success"
                            status = 200
                        else:
                            msg = "No Data Found!!"
                            status = 202
                        data = {'msg': msg, 'data': list(qry1)}
                elif request.method == 'DELETE':
                    data = json.loads(request.body)
                    print(data)
                    form_type = data['form_type']
                    form_part = data['form_part']

                    qry = AppraisalStaffQuestion.objects.filter(
                        ques_id=data['del_id'],session=session).exclude(status="DELETE").values('field')
                    if(qry.exists()):

                        ques_id = data['del_id']
                        fd = qry[0]['field']
                        appraisal_staff_question_delete(
                            ques_id, form_type, form_part, session)
                        q2 = AppraisalStaffQuestion.objects.filter(field=fd, session=session, form_type=form_type, form_part=form_part).exclude(
                            status="DELETE").exclude(statement__isnull=True).values().count()
                        if q2 == 0:
                            q3 = AppraisalStaffQuestion.objects.filter(
                                field=fd, session=session, form_type=form_type, form_part=form_part).exclude(status="DELETE").update(status="DELETE")
                        msg = "Data Successfully Deleted..."
                        status = 200
                    else:
                        msg = "Data Not Found!"
                        status = 404
                    data = {'msg': msg}
                    status = 200
                elif request.method == 'POST':
                    data = json.loads(request.body)
                    print(data)
                    form_type = data[0]['form_type']
                    form_part = data[0]['form_part']

                    for body in data:
                        parent_ques = body['parent_ques']
                        statement = body['statement'].upper()
                        field_id = body['cat']
                        print(field_id)
                        field_qry = AppraisalStaffQuestion.objects.filter(ques_id=field_id,session=session).exclude(
                            status="DELETE").values('field', 'parent_ques')

                        # field_id = field_qry[0]['parent_ques']

                        field = field_qry[0]['field']

                        if 'max_marks' in body:
                            max_marks = int(body['max_marks'])
                        else:
                            max_marks = None

                        if parent_ques != 0:
                            field_qry = AppraisalStaffQuestion.objects.filter(ques_id=parent_ques,session=session).exclude(
                                status="DELETE").exclude(statement__isnull=True).values('statement', 'parent_ques', 'max_marks')

                            if field_qry:
                                field = field_qry[0]['statement']
                                field_id = field_qry[0]['parent_ques']

                            cnt = AppraisalStaffQuestion.objects.filter(
                                field=field, session=session, form_type=form_type, form_part=form_part).exclude(status="DELETE").values('ques_id')

                            if len(cnt) == 0:
                                print("hello")
                                add = AppraisalStaffQuestion.objects.create(
                                    parent_ques=parent_ques, field=field, form_type=form_type, form_part=form_part, session=AccountsSession.objects.get(id=session))

                        qry_ch = AppraisalStaffQuestion.objects.filter(Q(field=field) & Q(statement=statement)).filter(
                            parent_ques=parent_ques, session=session, form_type=form_type, form_part=form_part).exclude(status="DELETE")

                        if(len(qry_ch) > 0):
                            status = 409
                            msg = "error"
                            data = {'msg': msg}

                        else:
                            created = AppraisalStaffQuestion.objects.create(
                                parent_ques=parent_ques, field=field, statement=statement, form_type=form_type, form_part=form_part, session=AccountsSession.objects.get(id=session), max_marks=max_marks)

                            msg = "Successfully Inserted"
                            data = {'msg': msg}
                            status = 200

                    msg = "Successfully Inserted"
                    data = {'msg': msg}
                    status = 200

                elif request.method == 'PUT':
                    body = json.loads(request.body)
                    print(body)
                    form_type = body['form_type']
                    form_part = body['form_part']

                    ques_id = body['ques_id']
                    statement = body['statement'].upper()
                    if 'max_marks' not in body:
                        max_marks = None
                    elif body['max_marks'] is None:
                        max_marks = body['max_marks']
                    else:
                        max_marks = int(body['max_marks'])

                    add = AppraisalStaffQuestion.objects.filter(ques_id=ques_id,session=session).update(
                        statement=statement, max_marks=max_marks)

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


def appraisal_staff_question_delete(parent_ques, form_type, form_part, session):
    qry = AppraisalStaffQuestion.objects.filter(
        parent_ques=parent_ques, session=session, form_type=form_type, form_part=form_part).exclude(status="DELETE").values('ques_id')
    if len(qry) > 0:
        for x in qry:
            appraisal_staff_question_delete(
                x['ques_id'], form_type, form_part, session)
    qry = AppraisalStaffQuestion.objects.filter(
        ques_id=parent_ques, session=session, form_type=form_type, form_part=form_part).exclude(status="DELETE").update(status="DELETE")
