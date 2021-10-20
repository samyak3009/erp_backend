# -*- coding: utf-8 -*-
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
from django.db.models import Count
import math
import copy
import math
from datetime import date
from datetime import datetime
import calendar
import collections
from operator import itemgetter

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType

from musterroll.models import EmployeePerdetail
from login.models import EmployeeDropdown, EmployeePrimdetail, AuthUser
from .models import *
from Registrar.models import *

from .views import *
from login.views import checkpermission, generate_session_table_name


def get_academic_dept():
	qry = CourseDetail.objects.filter().values("dept_id__value", "dept_id__sno").distinct()
	return list(qry)


def get_hod_filtered_dept(dept):
	qry = CourseDetail.objects.filter(dept=dept).values("dept_id__value", "dept_id__sno").distinct()
	return list(qry)


def get_acad_filtered_emps(dept, emp_category):
	if dept == "ALL":
		qry = CourseDetail.objects.values_list("dept_id__sno", flat=True).distinct()

		q_emp = EmployeePrimdetail.objects.filter(emp_status="ACTIVE", dept__in=qry, emp_category__in=emp_category).exclude(emp_id="00007").values('emp_id', 'name', 'dept__value', 'desg__value', 'dept__sno')
	else:
		q_emp = EmployeePrimdetail.objects.filter(emp_status="ACTIVE", dept=dept, emp_category__in=emp_category).exclude(emp_id="00007").values('emp_id', 'name', 'dept__value', 'desg__value', 'dept__sno')

	return list(q_emp)


def get_time_difference(t1, t2):
	time1 = t1.hour * 60 + t1.minute
	time2 = t2.hour * 60 + t2.minute
	if ((time2 - time1) > 0):
		total = (int)(time2 - time1)
	else:
		total = (int)(time2 + 1440 - time1)
	return total


def Department_list(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			query = []
			session = request.session['Session_id']
			session_name = request.session['Session_name']
			sem_type = request.session['sem_type']
			if(request.method == 'GET'):
				if request.GET['request_by'] in ('HOD', 'hod'):
					check = checkpermission(request, [319])
					if check == 200:
						if request.GET['request_type'] == 'hod_filtered_dept':
							q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
							dept = q_dept[0]['dept']
							query = get_hod_filtered_dept(dept)
						status = 200
						data_values = {'data': (query), 'emp_category': get_emp_category()}
				elif request.GET['request_by'] in ('DEAN', 'dean'):
					check = checkpermission(request, [1371, 1368])
					if check == 200:
						if request.GET['request_type'] == 'get_academic_department':
							query = get_academic_dept()
						status = 200
						print("hello")
						data_values = {'data': (query), 'emp_category': get_emp_category()}
						print(data_values)
				else:
					status = 403
			else:
				status = 502
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def resolve_remark(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'A' in request.session['Coordinator_type']:
				emp = request.session['hash1']
				session_name = request.session['Session_name']
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
				if(request.method == 'POST'):
					data = json.loads(request.body)
					uniq_id = data['uniq_id']
					att_id = data['att_id']
					if att_id == -1:
						query = StudentRemarks.objects.filter(added_by=emp, uniq_id=uniq_id, id=data['id']).exclude(status__contains="DELETE").update(status='DELETE')
						if query:
							data_values = {'msg': 'Remark Successfully Deleted', 'error': False}
						else:
							data_values = {'msg': 'Error', 'error': True}
					else:
						query = StudentAttStatus.objects.filter(marked_by=emp, uniq_id=uniq_id, att_id=att_id).exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").update(remark=None)
						if query:
							data_values = {'msg': 'Remark Successfully Deleted', 'error': False}
						else:
							data_values = {'msg': 'Error', 'error': True}
					status = 200
				else:
					data_values = {'msg': 'request_error', 'error': True}
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status, safe=False)


def Student_lec_wise(request):
	data_values = []
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369, 1372, 319, 1371])
			session_name = request.session['Session_name']
			if check == 200:
				data = json.loads(request.body)
				course = data['course']
				dept = data['branch']
				sem = data['sem']
				section = data['sec']
				date = datetime.strptime(str(data['date']).split('T')[0], "%Y-%m-%d").date()
				i = 0
				data1 = []
				data1.append({})

				Attendance = generate_session_table_name("Attendance_", session_name)
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

				if(request.method == 'POST'):
					section = list(Sections.objects.filter(sem_id=sem, section=section, dept=dept).values_list('section_id', flat=True))
					lec = Attendance.objects.filter(date=date, section__in=section).exclude(status__contains='DELETE').values_list('lecture', flat=True).order_by('lecture').distinct().order_by('lecture')
					data1[0]['total_present'] = []
					for l in lec:
						print("date,section,l", date, section, l)
						q = StudentAttStatus.objects.filter(att_id__date=date, att_id__section__in=section, att_id__lecture=l, present_status='P').exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").count()
						if q:
							data1[0]['total_present'].append({'lecture': l, 'present': q})
						else:
							data1[0]['total_present'].append({'lecture': l, 'present': 0})
					students = get_section_students(section, {}, session_name)
					for stu in students[0]:
						if lec:
							data_values.append({})
							data_values[i]['data'] = []
							data_values[i]['total_lecture'] = []
							data_values[i]['name'] = stu['uniq_id__name']
							uniq_id = stu['uniq_id']
							qry = StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('uni_roll_no')
							data_values[i]['university_roll_no'] = qry[0]['uni_roll_no']
							data_values[i]['branch'] = stu['uniq_id__dept_detail__dept__value']
							data_values[i]['sem'] = stu['section__sem_id__sem']
							data_values[i]['sec'] = stu['section__section']
							data_values[i]['date'] = date
							present = 0
							absent = 0
							for l in lec:
								query = StudentAttStatus.objects.filter(uniq_id=stu['uniq_id'], att_id__date=date, att_id__lecture=l).exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").values('att_id__lecture', 'present_status')
								if query:
									if(query[0]['present_status'] == 'P'):
										present += 1
									elif(query[0]['present_status'] == 'A'):
										absent += 1
									data_values[i]['data'].append({'att_id__lecture': l, 'present_status': query[0]['present_status']})
								else:
									data_values[i]['data'].append({'att_id__lecture': l, 'present_status': "N/A"})
							data_values[i]['total_lecture'].append({'present': present, 'absent': absent})
							i += 1

					status = 200

				else:
					data_values = {'msg': 'request_error'}
			else:

				status = 403

		else:
			status = 401
	else:
		status = 500
	data_values = {'data': data_values, 'data1': data1}
	print(data_values)
	return JsonResponse(data=data_values, status=status, safe=False)


# def Student_day_and_lec_wise(request):
#     data_values = []
#     status = 403
#     if 'HTTP_COOKIE' in request.META:
#         if request.user.is_authenticated:
#             check = checkpermission(request, [1369, 1372, 319, 1371])
#             session_name = request.session['Session_name']
#             if check == 200:
#                 data = json.loads(request.body)
#                 course = data['course']
#                 dept = data['branch']
#                 sem = data['sem']
#                 section = data['sec']
#                 from_date = datetime.strptime(str(data['from_date']).split('T')[0], "%Y-%m-%d").date()
#                 to_date = datetime.strptime(str(data['to_date']).split('T')[0], "%Y-%m-%d").date()
#                 date_array = (from_date + datetime.timedelta(days=x) for x in range(0, (to_date - from_date).days))
#                 print(date_array)
#                 i = 0
#                 data1 = []
#                 data1.append({})

#                 Attendance = generate_session_table_name("Attendance_", session_name)
#                 StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

#                 if(request.method == 'POST'):
#                     section = list(Sections.objects.filter(sem_id=sem, section=section, dept=dept).values_list('section_id', flat=True))
#                     date_array = [from_date + timedelta(days=x) for x in range(0, (to_date - from_date).days)]
#                     students = get_section_students(section, {}, session_name)
#                     data_values = []
#                     i = 0
#                     for stu in students[0]:
#                         dayWiseLectures = []
#                         j = 0
#                         for dates in date_array:
#                             lec = list(Attendance.objects.filter(date=dates, section__in=section).exclude(status__contains='DELETE').values_list('lecture', flat=True).order_by('lecture').distinct().order_by('lecture'))
#                             lectures = []
#                             for l in lec:
#                                 query = StudentAttStatus.objects.filter(uniq_id=stu['uniq_id'], att_id__date=dates, att_id__lecture=l).exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").values('att_id__lecture', 'present_status')
#                                 if query:
#                                     lectures.append(query[0])
#                             dayWiseLectures.append({'date': dates, 'lectures': lectures})
#                             j += 1
#                         if dayWiseLectures:
#                             data_values.append({})
#                             data_values[i]['name'] = stu['uniq_id__name']
#                             uniq_id = stu['uniq_id']
#                             qry = StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('uni_roll_no')
#                             data_values[i]['university_roll_no'] = qry[0]['uni_roll_no']
#                             data_values[i]['branch'] = stu['uniq_id__dept_detail__dept__value']
#                             data_values[i]['sem'] = stu['section__sem_id__sem']
#                             data_values[i]['sec'] = stu['section__section']
#                             data_values[i]['dates'] = dayWiseLectures
#                             i += 1
#                     status = 200

#                 else:
#                     data_values = {'msg': 'request_error'}
#             else:

#                 status = 403

#         else:
#             status = 401
#     else:
#         status = 500
#     data_values = {'data': data_values, 'data1': data1}
#     # print(data_values)
#     return JsonResponse(data=data_values, status=status, safe=False)
def Student_day_and_lec_wise(request):
    data_values = []
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1369, 1372, 319, 1371])
            session_name = request.session['Session_name']
            if check == 200:
                if(requestMethod.POST_REQUEST(request)):
                    data = json.loads(request.body)
                    course = data['course']
                    dept = data['branch']
                    sem = data['sem']
                    section = data['sec']
                    from_date = datetime.strptime(str(data['from_date']).split('T')[0], "%Y-%m-%d").date()
                    to_date = datetime.strptime(str(data['to_date']).split('T')[0], "%Y-%m-%d").date()
                    date_array = (from_date + datetime.timedelta(days=x) for x in range(0, (to_date - from_date).days))
                    # print(date_array)
                    i = 0
                    data1 = []
                    data1.append({})

                    Attendance = generate_session_table_name("Attendance_", session_name)
                    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
                    section = list(Sections.objects.filter(sem_id=sem, section=section, dept=dept).values_list('section_id', flat=True))
                    #print(section)
                    date_array = [from_date + timedelta(days=x) for x in range(0, (to_date - from_date).days + 1)]
                    #print(date_array, 'date_array')
                    students = get_section_students(section, {}, session_name)
                    #print(students)
                    data_values = []
                    i = 0
                    for stu in students[0]:
                        dayWiseLectures = []
                        j = 0
                        for dates in date_array:
                            lec = list(Attendance.objects.filter(date=dates, section__in=section).exclude(status__contains='DELETE').values_list('lecture', flat=True).order_by('lecture').distinct().order_by('lecture'))
                            #print(lec)
                            lectures = []
                            for l in lec:
                                #print(l)
                                query = StudentAttStatus.objects.filter(uniq_id=stu['uniq_id'], att_id__date=dates, att_id__lecture=l).exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").values('att_id__lecture', 'present_status')
                                if query:
                                    lectures.append(query[0])
                                else :
                                    lectures.append({'att_id__lecture':l,'present_status':"NA"})
                            if(len(lectures) != 0):
                                dayWiseLectures.append({'date': dates, 'lectures': lectures})
                                #print(dayWiseLectures)
                            j += 1
                        if dayWiseLectures:
                            data_values.append({})
                            data_values[i]['name'] = stu['uniq_id__name']
                            uniq_id = stu['uniq_id']
                            qry = StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('uni_roll_no', 'lib_id')
                            data_values[i]['university_roll_no'] = qry[0]['uni_roll_no']
                            data_values[i]['library_id']=qry[0]['lib_id']
                            data_values[i]['branch'] = stu['uniq_id__dept_detail__dept__value']
                            data_values[i]['sem'] = stu['section__sem_id__sem']
                            data_values[i]['sec'] = stu['section__section']
                            data_values[i]['dates'] = dayWiseLectures
                            i += 1
                    status = statusCodes.STATUS_SUCCESS

                    
                        

                elif(requestMethod.GET_REQUEST(request)):
                    if(requestType.custom_request_type(request.GET, 'get_graph_data')):
                        course = request.GET['course']
                        dept = request.GET['branch']
                        sem = request.GET['sem']
                        section = request.GET['sec']
                        from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
                        to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
                        date_array = (from_date + datetime.timedelta(days=x) for x in range(0, (to_date - from_date).days))
                        data1 = []
                        data1.append({})
                        Attendance = generate_session_table_name("Attendance_", session_name)
                        StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
                        section = list(Sections.objects.filter(sem_id=sem, section=section, dept=dept).values_list('section_id', flat=True))
                        date_array = [from_date + timedelta(days=x) for x in range(0, (to_date - from_date).days + 1)]
                        students = get_section_students(section, {}, session_name)
                        data_values = []
                        #FOR UNDEFINED VALUES ON GRAPH AXIS#
                        role='role'
                        true='true'
                        max_lec=0
                        #END#
                        ###DEFINING X AND Y AXIS ON GRAPH###
                        axis=['Dates', 'L1',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'}, 'L2',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'}, 'L3',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'} ,'L4',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'},'L5',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'}, 'L6',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'}, 'L7',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'}, 'L8',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'},'L9',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'},'L10',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'},'L11',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'},'L12',{ role: 'tooltip', 'p': {'html': true}},{'role':'annotation'}]
                        for dates in date_array:
                            lec = list(Attendance.objects.filter(date=dates, section__in=section).exclude(status__contains='DELETE').values_list('lecture',flat=True).order_by('lecture').distinct().order_by('lecture'))
                            percentage_lecwise=[]
                            
                            if (len(lec)>0):
                                if len(lec)>max_lec:
                                    max_lec=len(lec)
                        axis=axis[0:((max_lec*3)+1)]
                        print(axis)
                        data_values.append(axis)
                        for dates in date_array:
                            lec = list(Attendance.objects.filter(date=dates, section__in=section).exclude(status__contains='DELETE').values_list('lecture',flat=True).order_by('lecture').distinct().order_by('lecture'))
                            percentage_lecwise=[]
                            
                            if (len(lec)>0):
                                percentage_lecwise.append(dates)  
                                for l in lec:
                                    sub_name = list(Attendance.objects.filter(date=dates, section__in=section,lecture=l).exclude(status__contains='DELETE').values_list('subject_id__sub_alpha_code','subject_id__sub_num_code').distinct())
                                    full_name=str(sub_name[0])
                                    present=0
                                    for stu in students[0]:
                                        query = StudentAttStatus.objects.filter(uniq_id=stu['uniq_id'], att_id__date=dates, att_id__lecture=l).exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").values('att_id__lecture', 'present_status')
                                        if query:
                                            if query[0]['present_status']=='P':
                                                present+=1
                                            else:
                                                pass
                                        else:
                                            pass
            #######SETTING DATA FORMAT TO MATCH WITH GOOGLE GRAPH#######
                                    percentage_lecwise.append(present)
                                    percentage_lecwise.append('<div><strong>Subject Code : '+full_name+'<br>Lecture : '+str(l)+'<br>'+'Present : '+str(present)+'<br>'+'Absent : '+str(len(students[0])-present)+'</strong></div>')
                                    percentage_lecwise.append('L'+str(l))
                                for i in range(2,len(axis)):
                                    try :
                                        percentage_lecwise[i]
                                    except:
                                        percentage_lecwise.extend((0,"",""))
                                        i+=3
                                data_values.append(percentage_lecwise)
            #####END#######
                        status=statusCodes.STATUS_SUCCESS
                else:
                    status=statusCodes.STATUS_METHOD_NOT_ALLOWED
            else:

                status = statusCodes.STATUS_FORBIDDEN

        else:
            status = statusCodes.STATUS_UNAUTHORIZED
    else:
        status = statusCodes.STATUS_SERVER_ERROR
    data_values = {'data': data_values, 'data1': data1}
    return functions.RESPONSE(data_values,status)

def Department_load(request):
	data_values = []
	data1 = []
	final_data = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371, 319])
			session_name = request.session['Session_name']
			session = request.session['Session_id']
			FacultyTime = generate_session_table_name("FacultyTime_", session_name)

			if check == 200:
				if(request.method == 'GET'):
					if(request.GET['request_type'] == "filtered_emp"):
						query = get_acad_filtered_emps(request.GET['dept'], request.GET['emp_category'].split(','))
						i = 0
						qry = StudentDropdown.objects.filter(field='SUBJECT TYPE').exclude(value__isnull=True).values_list('value', flat=True).distinct()
						for q in query:
							data_values.append({})
							data_values[i]['dept'] = []
							data_values[i]['data'] = []
							dept_assigned = FacultyTime.objects.filter(emp_id=q['emp_id'], status='INSERT').values_list('section__dept__dept', flat=True).distinct()
							k = 0
							for dept in dept_assigned:
								data_values[i]['dept'].append({})
								data_values[i]['dept'][k]['day_wise'] = []
								data_values[i]['dept'][k]['lectures'] = []
								j = 0
								time = 0
								for day in range(0, 6):
									t = 0
									total_time = 0
									query1 = FacultyTime.objects.filter(emp_id=q['emp_id'], status='INSERT', day=day, section__dept__dept=dept).values('subject_id__subject_type__value', 'section__dept__dept__value', 'section__dept__dept__sno', 'lec_num', 'start_time', 'end_time').distinct()
									for qr in qry:
										l = 0
										for q1 in query1:
											department = q1['section__dept__dept__value']
											dep_id = q1['section__dept__dept__sno']
											if q1['subject_id__subject_type__value'] == qr:
												l += 1
												t += 1
												time += get_time_difference(q1['start_time'], q1['end_time'])
										data1.append({qr: l, 'time': time})
										total_time += time
										time = 0
									data_values[i]['dept'][k]['day_wise'].append({'data1': data1, 'total': t, 'total_time': total_time})
									total_time = 0
									data1 = []
								for qr in qry:
									t = 0
									time = 0
									for day in range(0, 6):
										query1 = FacultyTime.objects.filter(emp_id=q['emp_id'], status='INSERT', day=day, section__dept__dept=dept).values('subject_id__subject_type__value', 'section__dept__dept__value', 'lec_num', 'section__dept__dept__sno', 'start_time', 'end_time').distinct()
										l = 0
										for q1 in query1:
											department = q1['section__dept__dept__value']
											dep_id = q1['section__dept__dept__sno']
											if q1['subject_id__subject_type__value'] == qr:
												l += 1
												t += 1
												time += get_time_difference(q1['start_time'], q1['end_time'])
									data1 = qr
									data_values[i]['dept'][k]['lectures'].append({'data1': data1, 'total': t, 'dept': dep_id, 'name': department, 'time': time})
									time = 0
									data1 = []
								k += 1

							q_lec_time = StudentAcademicsDropdown.objects.filter(field='LECTURE TIME', session=session).exclude(value__isnull=True).exclude(status='DELETE').values('value')
							data_values[i]['data'].append(q)
							if q_lec_time:
								final_data = {'data': data_values, 'lecture_time': int(q_lec_time[0]['value'])}
							else:
								final_data = {'data': data_values, 'lecture_time': 'N/A'}
							i += 1
						status = 200
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=final_data, status=status, safe=False)


def Department_load_without_time(request):
	data_values = []
	data1 = []
	final_data = {}
	sub_name = []
	data2 = []
	status = 403
	if checkpermission(request, [rolesCheck.ROLE_HOD or rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
		session_name = request.session['Session_name']
		session = request.session['Session_id']
		FacultyTime = generate_session_table_name("FacultyTime_", session_name)

		if (requestMethod.GET_REQUEST(request)):
			if(requestType.custom_request_type(request.GET, 'filtered_emp')):
				query = get_acad_filtered_emps(request.GET['dept'], request.GET['emp_category'].split(','))
				i = 0
				for q in query:
					data_values.append({})
					data_values[i]['dept'] = []
					data_values[i]['data'] = []
					dept_assigned = FacultyTime.objects.filter(emp_id=q['emp_id'], status='INSERT').exclude(subject_id__status="DELETE").values_list('section__dept__dept', flat=True).distinct()
					k = 0
					z = 0
					for dept in dept_assigned:
						data_values[i]['dept'].append({})
						data_values[i]['dept'][k]['lectures'] = []
						query1 = FacultyTime.objects.filter(emp_id=q['emp_id'], status='INSERT', section__dept__dept=dept).exclude(subject_id__status="DELETE").values_list('section__sem_id__sem', flat=True).distinct()

						z = 0
						for sem in query1:
							query2 = FacultyTime.objects.filter(emp_id=q['emp_id'], status='INSERT', section__dept__dept=dept, section__sem_id__sem=sem).exclude(subject_id__status="DELETE").values('subject_id__subject_type__value', 'section__dept__dept__value', 'section__dept__dept__sno', 'subject_id__sub_name').distinct()
							for q2 in query2:
								t = 0
								# p=0
								if q2['subject_id__subject_type__value'] == 'LAB':
									for day in range(0, 6):
										query3 = FacultyTime.objects.filter(emp_id=q['emp_id'], status='INSERT', day=day, section__dept__dept=dept, section__sem_id__sem=sem, subject_id__sub_name=q2['subject_id__sub_name'], subject_id__subject_type__value='LAB').exclude(subject_id__status="DELETE").values('lec_num').distinct().count()
										t += query3
								else:
									for day in range(0, 6):
										query3 = FacultyTime.objects.filter(emp_id=q['emp_id'], status='INSERT', day=day, section__dept__dept=dept, section__sem_id__sem=sem, subject_id__sub_name=q2['subject_id__sub_name']).exclude(subject_id__subject_type__value='LAB').exclude(subject_id__status="DELETE").values('lec_num').distinct().count()
										t += query3
								data1.append({'sub_name': q2['subject_id__sub_name'], 'type': q2['subject_id__subject_type__value'], 'sem': sem, 'dept': dept, 'total': t, 'department': q2['section__dept__dept__value']})
							if query2:
								data2.append({})
								data2[z]['sem'] = data1
								z += 1
							data1 = []
						data_values[i]['dept'][k]['lectures'] = data2
						data2 = []
						k += 1
					data_values[i]['data'] = q
					i += 1
					# final_data={'data':data_values}
					#  print(data_values)
				return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)
			else:
				return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE("Invalid Request Type"), statusCodes.STATUS_SERVER_ERROR)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
