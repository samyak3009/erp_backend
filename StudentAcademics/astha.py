# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
# from django.db.models import ArrayAgg
from datetime import datetime,timedelta
from django.utils import timezone
import json
from django.conf import settings
from django.http import HttpResponse,JsonResponse
import time
from dateutil import tz
from dateutil.relativedelta import relativedelta
from django.db.models import Q,Sum,Count,Max,F
import copy
import math
from datetime import date
from datetime import datetime
import calendar
import collections
from operator import itemgetter

from login.models import EmployeeDropdown,EmployeePrimdetail,AuthUser
from musterroll.models import EmployeePerdetail
from Registrar.models import *
from .models import *

from dashboard.views import academic_calendar
from login.views import checkpermission,generate_session_table_name
from .views import *

def total_lecture(request):
	data=[]
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.method=='POST':
				data=json.loads(request.body)
				session_name = request.session['Session_name']
				branchs=data['branch'].split(",")
				sems=data['sem'].split(",")
				# print(sem)
				to_date=datetime.strptime(str(data['to_date']).split('T')[0],"%Y-%m-%d").date()
				from_date=datetime.strptime(str(data['from_date']).split('T')[0],"%Y-%m-%d").date()
				sections=data['section'].split(",")
				subjects=data['subject'].split(",")

				data={}
				k=0
				SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
				Attendance = generate_session_table_name("Attendance_",session_name)

				for index,branch in enumerate(branchs):
					data[index]={'branch':''}
					data[index]['sem']={}
					for index_2,sem in enumerate(sems):
						section_list=list(Sections.objects.filter(section__in=sections,dept=branch,sem_id__sem=sem).values('section_id','section','dept__dept__value','sem_id','sem_id__sem'))
						data[index]['sem'][sem]={'section':[]}
						for index_3,q in enumerate(section_list):
							data[index]['branch']=q['dept__dept__value']
							data[index]['sem'][sem]['section'].append(q)
							a=list(SubjectInfo.objects.filter(sem=q['sem_id'],id__in=subjects).values('id','sub_name','sub_num_code','sub_alpha_code'))
							for d in a:
								total_lecture=Attendance.objects.filter(date__gte=from_date,date__lte=to_date,subject_id=d['id'],section=q['section_id']).exclude(status='DELETE').values().count()
								name = d['sub_name']+'('+d['sub_alpha_code']+'-'+d['sub_num_code']+')'
								data[index]['sem'][sem]['section'][data[index]['sem'][sem]['section'].index(q)][name]=total_lecture
				status=200
				data_values=data
			else:
				status=403
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=data_values,status=status,safe=False)
