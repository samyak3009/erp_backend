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
from login.views import checkpermission
from DeptAchievement.models import AarMultiselect
from erp.constants_variables import *
from erp.constants_functions import functions, requestMethod


