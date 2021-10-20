from __future__ import unicode_literals
from django.shortcuts import render
# from django.db.models import ArrayAgg
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import time
from dateutil import tz
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum, Count, Max, F
import math
from datetime import date
from datetime import datetime
import calendar
import collections
from operator import itemgetter
import copy

from login.models import EmployeePrimdetail
from Registrar.models import CourseDetail, Sections
from .models import *

from login.views import generate_session_table_name


def get_dept_faculty(dept):
    dept_id = CourseDetail.objects.filter(uid__in=dept).values_list('dept', flat=True)
    faculty = list(EmployeePrimdetail.objects.filter(dept__in=dept_id).values('emp_id', 'name'))
    return(faculty)


def get_subject_multi_type(dept, sem, sub_type, session_name):

    SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

    temp = list(SubjectInfo.objects.filter(sem__sem__in=sem, sem__dept__in=dept, subject_type__in=sub_type).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'id', 'sem__sem', 'sem__dept__dept__value').order_by('sem__sem', 'sem__dept__dept__value'))
    for x in temp:

        try:
            x['info'] = '(' + str(x['sem__dept__dept__value']) + "-" + str(x['sem__sem']) + ') ' + str(x['sub_name']) + ' ( ' + str(x['sub_alpha_code']) + str(x['sub_num_code']) + ' )'
        except:
            x['info'] = x['sub_name']
    return list(temp)
