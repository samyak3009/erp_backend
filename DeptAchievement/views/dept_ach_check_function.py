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


def Nonecheck(data):

    data_keys=data.keys()

    for x in data_keys:

        if x=='remark' or x=='description':
            continue

        if data[x] is None or data[x]=="" or data[x]==[]:
            return False

    else:
        return True


