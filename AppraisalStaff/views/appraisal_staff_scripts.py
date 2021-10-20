
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# '''essentials'''
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
from datetime import date
import json
import datetime
import operator


# '''import constants'''
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

# '''import models'''
from musterroll.models import EmployeePerdetail, Roles, AarReporting
from login.models import EmployeePrimdetail, EmployeeDropdown

# '''import views'''
from login.views import checkpermission, generate_session_table_name

# Create your views here.


def add_dir_role_in_reporting_staff():
    emp_data = list(EmployeePrimdetail.objects.exclude(
        emp_category__value="FACULTY").values_list('emp_id', flat=True).order_by('emp_id'))

    for x in emp_data:
        reporting_check = list(AarReporting.objects.filter(emp_id=x, reporting_to=1339).values(
            'emp_id', 'reporting_no').order_by('reporting_no'))
        reporting_data = []
        if len(reporting_check) == 0:
            reporting_data = list(AarReporting.objects.filter(emp_id=x).values(
                'emp_id', 'reporting_no').order_by('reporting_no'))
            if len(reporting_data) > 0:
                AarReporting.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=reporting_data[-1]['emp_id']), reporting_to=EmployeeDropdown.objects.get(
                    sno=1339), department=EmployeeDropdown.objects.get(sno=806), reporting_no=int(reporting_data[-1]['reporting_no']) + 1)
# add_dir_role_in_reporting_staff()
