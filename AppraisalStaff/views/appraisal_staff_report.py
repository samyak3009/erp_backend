
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
from musterroll.models import EmployeePerdetail, Roles
from login.models import EmployeePrimdetail

# '''import views'''
from login.views import checkpermission, generate_session_table_name

# Create your views here.
