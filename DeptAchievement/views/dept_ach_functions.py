# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
from django.shortcuts import render
import json
from django.http import JsonResponse
import datetime
from dateutil.relativedelta import relativedelta
import calendar
from django.db.models import Q
from datetime import date
from django.contrib.auth.models import User

from login.models import AarDropdown, EmployeeDropdown
from musterroll.models import EmployeePrimdetail, EmployeeResearch, EmployeeAcademic, Reporting, AarReporting
from DeptAchievement.models import *

from login.views import checkpermission

#'''import functions'''
# Create your views here.


def get_achievements_list():

    data = [{"sno":1, "value":"GUEST LECTURE"},{"sno":2,"value":"INDUSTRIAL VISIT"},{"sno":3,"value":"MOU SIGNED"},{"sno":4,"value":"EVENTS ORGANISED"},{"sno":5,"value":"HOBBY CLUB"},{"sno":6,"value":"SUMMER WINTER SCHOOL"},{"sno":7,"value":"STUDENT ACHIEVEMENT"},{"sno":8,"value":"DEPARTMENT ACHIEVEMENT"}]
    return (data)

def RequestForApproval(form_type, form_id):
    DeptAchApproval.objects.create(level=1, approval_category=form_type, approval_id=form_id, approval_status='PENDING')
    return True


def get_department():
    q1 = list(EmployeeDropdown.objects.filter(field='DEPARTMENT').exclude(value=None).values('sno', 'value'))
    return(q1)


def Year():
    year_list = [{"sno": 1}, {"sno": 2}, {"sno": 3}, {"sno": 4}]
    return year_list


def Dropdown(field):
    q1 = list(AarDropdown.objects.filter(field=field).exclude(value=None).values_list('sno', flat=True))
    q2 = AarDropdown.objects.filter(field='CATEGORY', pid__in=q1).values('sno', 'value')
    return(q2)


def Hobby(field):
    q1 = list(AarDropdown.objects.filter(field=field, pid=0).exclude(value=None).values('sno', 'value'))
    return(q1)


def FactDrop(hod):
    dept_id = EmployeePrimdetail.objects.filter(emp_id=hod).exclude(emp_status='SEPERATE').values('dept')
    coordinators = list(EmployeePrimdetail.objects.filter(dept=dept_id[0]['dept']).values('emp_id', 'name'))
    return(coordinators)

def get_type_list():

    sno_value=list(AarDropdown.objects.filter(field="EVENTS_ORGANIZED", value="TYPE", status="INSERT").exclude(value=None).values_list('sno',flat=True))
    type_value = list(AarDropdown.objects.filter(field="TYPE", pid__in=sno_value, status="INSERT").exclude(value=None).values('value','sno'))
    return (type_value)

def get_category_list():

    sno_value=list(AarDropdown.objects.filter(field="EVENTS_ORGANIZED", value="CATEGORY", status="INSERT").exclude(value=None).values_list('sno',flat=True))
    type_value = list(AarDropdown.objects.filter(field="CATEGORY", pid__in=sno_value, status="INSERT").exclude(value=None).values('value','sno'))
    return (type_value)

def get_organisation():

    sno_value=list(AarDropdown.objects.filter(field="EVENTS_ORGANIZED", value="ORGANIZATION_SECTOR", status="INSERT").exclude(value=None).values_list('sno',flat=True))

    type_value = list(AarDropdown.objects.filter(field="ORGANIZATION_SECTOR", pid__in=sno_value, status="INSERT").exclude(value=None).values('value','sno'))
    return (type_value)  

def get_incorp():

    sno_value=list(AarDropdown.objects.filter(field="EVENTS_ORGANIZED", value="INCORPORATION_TYPE", status="INSERT").exclude(value=None).values_list('sno',flat=True))

    type_value = list(AarDropdown.objects.filter(field="INCORPORATION_TYPE", pid__in=sno_value, status="INSERT").exclude(value=None).values('value','sno'))
    return (type_value)  

def get_venue():

    data=[{"venue":"KIET Group of Institutions"},{"venue":"Other"}]
    return(data)

def get_incollab_sponsor():

    data=[{"value":"Yes"},{"value":"No"}]
    return(data)



