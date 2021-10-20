# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
# from django.db.models import ArrayAgg
from datetime import datetime,timedelta
from django.utils import timezone
import json
import copy
from django.conf import settings
from django.http import HttpResponse,JsonResponse
import time
from dateutil import tz
from dateutil.relativedelta import relativedelta
from django.db.models import Q,Sum,Count,Max,F
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
from StudentAcademics.views import *
from .views import *

def faculty_tt_matrix(session,emp_id,session_name):
	FacultyTime = generate_session_table_name("FacultyTime_",session_name)
	query2=FacultyTime.objects.filter(session=session,emp_id__emp_id__username=emp_id).exclude(status='DELETE').exclude(subject_id__status="DELETE").values('day','lec_num','subject_id__sub_num_code')
	day_det=[]
	max_lec=0
	max2=0
	final_data={}
	ranging= range(len(query2))
	for x in ranging:
		if max2 < query2[x]['lec_num']:
			max2=query2[x]['lec_num']
	for q2 in query2:
		day_det.append({'day_name':calendar.day_name[q2['day']],'num_slots':max2,'day_id':q2['day']})
		if max2 > max_lec:
			max_lec=max2
	for day in day_det:
		lec_data={}
		for lec in range(1,max_lec+1):
			if lec > day['num_slots']:
				sec_arr={'section':[],'active':False}
				lec_data[str(lec)]={sec_arr}
			else:
				q_fac_time =FacultyTime.objects.filter(session=session,emp_id__emp_id__username=emp_id,day=day['day_id'],lec_num=lec).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('section__section_id','subject_id__sub_num_code','lec_num').distinct()
				final_fac_arr=[]
				sec_arr=[]
				if len(q_fac_time)>0:
					for f in q_fac_time:
						q_sub_det=FacultyTime.objects.filter(session=session,emp_id__emp_id__username=emp_id,section__section_id=f['section__section_id'],day=day['day_id'],subject_id__sub_num_code=f['subject_id__sub_num_code'],lec_num=f['lec_num']).exclude(status='DELETE').exclude(subject_id__status="DELETE").values('subject_id','subject_id__subject_type__value','subject_id__subject_unit__value','subject_id__sub_alpha_code','subject_id__sub_num_code','subject_id__sub_name','emp_id','emp_id__name','emp_id__dept__value','start_time','end_time','section__section','section__section_id','section__sem_id__sem_id','section__sem_id__sem','lec_num','section__sem_id__dept__dept__value')
						if lec == q_sub_det[0]['lec_num']:
							sec_arr.append({'semester':q_sub_det[0]['section__sem_id__sem'],'section_id':q_sub_det[0]['section__section_id'],'section':q_sub_det[0]['section__section'],'subject_id':q_sub_det[0]['subject_id'],'sub_type':q_sub_det[0]['subject_id__subject_type__value'],'sub_unit':q_sub_det[0]['subject_id__subject_unit__value'],'sub_name':q_sub_det[0]['subject_id__sub_name'],'code':q_sub_det[0]['subject_id__sub_alpha_code']+"-"+str(q_sub_det[0]['subject_id__sub_num_code']),'time_from':q_sub_det[0]['start_time'],'time_to':q_sub_det[0]['end_time'],'dept':q_sub_det[0]['section__sem_id__dept__dept__value'],'active':True})
				else:
					sec_arr.append({'semester':"--",'section_id':"--",'section':"--",'id':"--",'sub_type':"--",'sub_unit':"--",'sub_name':"--",'code':"--",'time_from':"--",'time_to':"--",'dept':"--",'active':False})

				lec_data[str(lec)]=sec_arr
			final_data[day['day_id']] = lec_data
	return [final_data]

def view_faculty_tt_matrix(request):
	data_values={}
	status=403
	if 'HTTP_COOKIE' in request.META:
		session_name = request.session['Session_name']
		FacultyTime = generate_session_table_name("FacultyTime_",session_name)
		if request.user.is_authenticated:
			check=checkpermission(request,[1371,1369,319])
			if check==200:
				if request.method=='GET':
					session=request.session['Session_id']
					if request.GET['request_type'] == 'Emp_id':
						if request.GET['request_by'] in ['DEAN','dean']:
							qry=FacultyTime.objects.filter(session=session).exclude(status="DELETE",emp_id__emp_id__username='00007').exclude(subject_id__status="DELETE").values('emp_id','emp_id__name','emp_id__dept__value').distinct()
							data_values=list(qry)
							status=200
						elif request.GET['request_by'] in ['HOD','hod']:
							emp=request.session['hash1']
							dept=EmployeePrimdetail.objects.filter(emp_id=emp).values('dept')
							qry=FacultyTime.objects.filter(section__sem_id__dept__dept=dept[0]['dept']).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('emp_id','emp_id__name','emp_id__dept__value').distinct()
							data_values=list(qry)
							status=200
						elif request.GET['request_by']=='FACULTY':
							emp_id=request.session['hash1']
							data_values=list(emp_id)
						else:
							status=502
					elif request.GET['request_type']=="Time_Table":
						if request.GET['request_by'] in ['DEAN','HOD','dean','hod']:
							emp_id=request.GET['Emp_id']
							qry1=faculty_tt_matrix(session,emp_id,session_name)
							data_values=list(qry1)
							status=200
						if request.GET['request_by'] in  ['FACULTY','faculty']:
							emp_id=request.session['hash1']
							qry1=faculty_tt_matrix(session,emp_id,session_name)
							data_values=list(qry1)
							status=200
					elif request.GET['request_type']=="get_fac_subjects":
						emp_id=request.GET['emp_id']
						qry1=FacultyTime.objects.filter(session=session,emp_id__emp_id__username=emp_id).exclude(status='DELETE').exclude(subject_id__status="DELETE").values('subject_id__sub_name').distinct()
						data_values=list(qry1)
						status=200
					else:
						status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status,safe=False)

# def Attendance(request):
# 	data_values={}
# 	status=403
# 	if 'HTTP_COOKIE' in request.META:
# 		if request.user.is_authenticated:
# 			if request.method=='POST':
# 				session=request.session['Session_id']
# 				session_name=request.session['Session_name']
# 				studentSession = generate_session_table_name("studentSession_",session_name)

# 				uniq_id=request.GET['uniq_id']
# 				qry1=studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date','section__sem_id')

# 				from_date=datetime.strptime(str(qry1[0]['att_start_date']).split('T')[0],"%Y-%m-%d").date()
# 				now=datetime.datetime.now()
# 				to_date=str(now)

# 				att_type=get_attendance_type()
# 				att_type_li = [t['sno'] for t in att_type]

# 				subjects = get_student_subjects(qry1[0]['section__sem_id'],session_name)

# 				qry2=get_student_attendance(uniq_id,from_date,to_date,session,att_type_li,subjects,1,[],session_name)

# 				total_lec=qry2['total']
# 				total_present=qry2['present_count']
# 				total_absent=qry2['absent_count']
# 				total_precentage=round((total_present/total_lec))

# 				att_type=get_attendance_type()
# 				for f in att_type['data']:
