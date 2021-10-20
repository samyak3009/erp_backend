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
import copy
import random
import math
from itertools import groupby
from datetime import date
from datetime import datetime
import calendar
import collections
from PIL import Image, ImageChops, ImageOps
from PIL import ImageFont
from PyPDF2 import PdfFileMerger, PdfFileReader
from PIL import ImageDraw
from operator import itemgetter

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType

from leave.models import Holiday
from musterroll.models import EmployeePerdetail
from login.models import EmployeeDropdown, EmployeePrimdetail, AuthUser
from Registrar.models import *
from StudentAccounts.models import SubmitFee
from StudentPortal.models import *
from .models import *

from login.views import checkpermission, generate_session_table_name
from dashboard.views import academic_calendar
from LessonPlan import views as lp
from LessonPlan.models import *

def Student_Academics_dropdown(request):
	data = {}
	qry1 = ""

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371])
			if check == 200:
				session_name = request.session['Session_name']
				if request.method == 'GET':
					session = request.session['Session_id']

					if request.GET['request_type'] == 'general':
						qry1 = StudentAcademicsDropdown.objects.filter(value=None, session=session).extra(select={'fd': 'field', 'id': 'sno', 'parent': 'pid'}).values('fd', 'id', 'parent','value').exclude(status="DELETE").distinct()
						for field1 in qry1:
							if field1['parent'] != 0:
								pid = field1['parent']
								qry2 = list(StudentAcademicsDropdown.objects.filter(sno=pid, session=session).exclude(status="DELETE").values('field'))
								if len(qry2) > 0:
									field1['fd'] = field1['fd'] + '(' + qry2[0]['field'] + ')'
						msg = "Success"
						error = False
						if not qry1:
							msg = "No Data Found!!"
						status = 200
						data = {'msg': msg, 'data': list(qry1)}

					elif request.GET['request_type'] == 'subcategory':
						sno = request.GET['Sno']
						names = StudentAcademicsDropdown.objects.filter(sno=sno, session=session).exclude(status="DELETE").values('field', 'pid')
						name = names[0]['field']
						p_id = names[0]['pid']

						qry1 = StudentAcademicsDropdown.objects.filter(field=name, pid=p_id, session=session).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'valueid': 'sno', 'parentId': 'pid', 'cat': 'field', 'text1': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('valueid', 'parentId', 'cat', 'text1', 'edit', 'delete')
						for x in range(0, len(qry1)):
							test = StudentAcademicsDropdown.objects.filter(pid=qry1[x]['valueid'], session=session).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'subid': 'sno', 'subvalue': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('subid', 'subvalue', 'edit', 'delete')
							qry1[x]['subcategory'] = list(test)
						msg = "Success"
						data = {'msg': msg, 'data': list(qry1)}
						status = 200

				elif request.method == 'DELETE':
					session = request.session['Session_id']
					data = json.loads(request.body)

					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_name):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					qry = StudentAcademicsDropdown.objects.filter(sno=data['del_id'], session=session).exclude(status="DELETE").values('field')
					if(qry.exists()):

						sno = data['del_id']
						fd = qry[0]['field']
						deletec(sno, session)
						q2 = StudentAcademicsDropdown.objects.filter(field=fd, session=session).exclude(status="DELETE").exclude(value__isnull=True).values().count()
						if q2 == 0:
							q3 = StudentAcademicsDropdown.objects.filter(field=fd, session=session).exclude(status="DELETE").update(status="DELETE")
						msg = "Data Successfully Deleted..."
						status = 200
					else:
						msg = "Data Not Found!"
						status = 404
					data = {'msg': msg}
					status = 200
				elif request.method == 'POST':
					body1 = json.loads(request.body)
					session = request.session['Session_id']
					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_name):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					for body in body1:
						pid = body['parentid']
						value = body['val'].upper()
						field_id = body['cat']
						field_qry = StudentAcademicsDropdown.objects.filter(sno=field_id, session=session).exclude(status="DELETE").values('field')
						field = field_qry[0]['field']
						if pid != 0:
							field_qry = StudentAcademicsDropdown.objects.filter(sno=pid, session=session).exclude(status="DELETE").exclude(value__isnull=True).values('value')
							field = field_qry[0]['value']
							cnt = StudentAcademicsDropdown.objects.filter(field=field, session=session).exclude(status="DELETE").values('sno')
							if len(cnt) == 0:
								add = StudentAcademicsDropdown.objects.create(pid=pid, field=field, session=Semtiming.objects.get(uid=session))

						qry_ch = StudentAcademicsDropdown.objects.filter(Q(field=field) & Q(value=value)).filter(pid=pid, session=session).exclude(status="DELETE")
						if(len(qry_ch) > 0):
							status = 409

						else:
							created = StudentAcademicsDropdown.objects.create(pid=pid, field=field, value=value, session=Semtiming.objects.get(uid=session))
							msg = "Successfully Inserted"
							data = {'msg': msg}
							status = 200

				elif request.method == 'PUT':
					session = request.session['Session_id']
					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_name):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					body = json.loads(request.body)
					sno = body['sno1']
					val = body['val'].upper()
					field_qry = StudentAcademicsDropdown.objects.filter(sno=sno, session=session).exclude(status="DELETE").values('pid', 'value')
					pid = field_qry[0]['pid']
					value = field_qry[0]['value']
					add = StudentAcademicsDropdown.objects.filter(pid=pid, field=value, session=session).exclude(status="DELETE").update(field=val)
					add = StudentAcademicsDropdown.objects.filter(sno=sno, session=session).exclude(status="DELETE").update(value=val, status="UPDATE")
					add = StudentAcademicsDropdown.objects.filter(pid=sno, session=session).exclude(status="DELETE").update(field=val, status="UPDATE")
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


def get_fac_time_subject_new(emp_id, section, session_name, sub_type):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)
	query = FacultyTime.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__in=section, subject_id__subject_type__in=sub_type).values('subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'section__sem_id__sem', 'section__sem_id__dept__dept__value', 'subject_id__subject_type__value', 'subject_id__subject_type').distinct()
	return list(query)


def deletec(pid, session):
	qry = StudentAcademicsDropdown.objects.filter(pid=pid, session=session).exclude(status="DELETE").values('sno')
	if len(qry) > 0:
		for x in qry:
			deletec(x['sno'], session)
	qry = StudentAcademicsDropdown.objects.filter(sno=pid, session=session).exclude(status="DELETE").update(status="DELETE")


def get_course():
	qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_gender():
	qry = StudentDropdown.objects.filter(field="GENDER").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_admission_type():
	qry = StudentDropdown.objects.filter(field="ADMISSION TYPE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_admission_status():
	qry = StudentDropdown.objects.filter(field="ADMISSION STATUS").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_attendance_category(session):
	qry = StudentAcademicsDropdown.objects.filter(field="ATTENDANCE CATEGORY", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_day_count_attendance(year, course, session):
	qry = AttendanceSettings.objects.filter(year=year, session=session, course=course).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_filtered_course(dept):
	qry = CourseDetail.objects.filter(dept=dept).values('course', 'course__value')
	return list(qry)


def get_section(sem_id):
	qry = Sections.objects.filter(sem_id=sem_id).exclude(status="DELETE").values('section_id', 'section', 'sem_id__dept__course__value', 'sem_id__dept__dept__value').order_by('section')
	return list(qry)


def get_subject_type():
	qry = StudentDropdown.objects.filter(field="SUBJECT TYPE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_subject_unit():
	qry = StudentDropdown.objects.filter(field="SUBJECT UNIT").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_academic_faculty(session_name):
	Attendance = generate_session_table_name("Attendance_", session_name)
	q_check = Attendance.objects.filter().exclude(status='DELETE').values('emp_id', 'emp_id__name', 'emp_id__dept__value').distinct()
	return list(q_check)


def get_lecture_break(session):
	data = []
	qry = StudentAcademicsDropdown.objects.filter(field="LECTURE BREAK", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	for q in qry:
		qr = StudentAcademicsDropdown.objects.filter(pid=q['sno'], session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
		data.append({'name': q['value'], 'lecture': qr[0]['value']})
	return data


def get_filtered_sem(course, dept, sem_type):
	if sem_type == "odd":
		get_sem = StudentSemester.objects.filter(dept__dept=dept, dept__course=course).annotate(odd=F('sem') % 2).filter(odd=True).order_by('sem').values('sem', 'sem_id').order_by('sem')
	elif sem_type == "even":
		get_sem = StudentSemester.objects.filter(dept__dept=dept, dept__course=course).annotate(odd=F('sem') % 2).filter(odd=False).order_by('sem').values('sem', 'sem_id').order_by('sem')

	return list(get_sem)


def get_all_sem(sem_type):
	if sem_type == "odd":
		get_sem = StudentSemester.objects.annotate(odd=F('sem') % 2).exclude(dept__dept__value__isnull=True).filter(odd=True).values('sem', 'sem_id', 'dept__course__value', 'dept__dept__value').order_by('dept__course__value', 'dept__dept__value', 'sem')
	elif sem_type == "even":
		get_sem = StudentSemester.objects.annotate(odd=F('sem') % 2).exclude(dept__dept__value__isnull=True).filter(odd=False).values('sem', 'sem_id', 'dept__course__value', 'dept__dept__value').order_by('dept__course__value', 'dept__dept__value', 'sem')

	return list(get_sem)


def get_coord_type():
	coord_type = []
	coord_type.append({'sno': 'T', 'value': 'TIME TABLE COORDINATOR'})
	coord_type.append({'sno': 'C', 'value': 'CLASS COORDINATOR'})
	coord_type.append({'sno': 'G', 'value': 'ASSIGN GROUP COORDINATOR'})
	coord_type.append({'sno': 'S', 'value': 'SUBJECT COORDINATOR'})
	coord_type.append({'sno': 'R', 'value': 'SEMESTER REGISTRATION COORDINATOR'})
	coord_type.append({'sno': 'E', 'value': 'EXTRA ATTENDANCE COORDINATOR'})
	coord_type.append({'sno': 'QM', 'value': 'QUESTION MODERATOR'})
	coord_type.append({'sno': 'CO', 'value': 'CO COORDINATOR'})
	coord_type.append({'sno': 'COE', 'value': 'EXAM COORDINATOR'})
	coord_type.append({'sno': 'UVE', 'value': 'UNIVERSITY MARKS COORDINATOR'})
	coord_type.append({'sno': 'NC', 'value': 'NBA COORDINATOR'})

	return coord_type


def get_filtered_dept(course, dept):
	qry = CourseDetail.objects.filter(course_id__in=course.split(','), dept=dept).values("uid", "dept_id__value", "course_duration", "course__value")
	return list(qry)


def get_attendance_type(session):
	data = []
	qry = StudentAcademicsDropdown.objects.filter(field="ATTENDANCE TYPE", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	for q in qry:
		qr = StudentAcademicsDropdown.objects.filter(pid=q['sno'], session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
		data.append({'id': q['sno'], 'value': q['value'], 'data': list(qr)})
	return data


def get_sub_attendance_type(session):
	data = []
	qry = StudentAcademicsDropdown.objects.filter(field="ATTENDANCE TYPE", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	for q in qry:
		qr = StudentAcademicsDropdown.objects.filter(pid=q['sno'], session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
		for q2 in qr:
			data.append({'sno': q2['sno'], 'value': q2['value']})
	print(data,"data attendance")
	return data


def get_class_attendance_type(session):
	data = []
	qry = StudentAcademicsDropdown.objects.filter(field="ATTENDANCE TYPE", value__in=["NORMAL ATTENDANCE", 'REMEDIAL ATTENDANCE', 'TUTORIAL ATTENDANCE', 'IMPROVEMENT ATTENDANCE'], session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	for q in qry:
		qr = StudentAcademicsDropdown.objects.filter(pid=q['sno'], session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
		for q2 in qr:
			data.append({'sno': q2['sno'], 'value': q2['value']})
	return data


def get_course_years(course):
	qry = CourseDetail.objects.filter(course=course).all().aggregate(Max('course_duration'))
	year_li = list(range(1, qry['course_duration__max'] + 1))
	return year_li


def get_dept():
	qry1 = EmployeeDropdown.objects.filter(field='DEPARTMENT').exclude(pid__isnull=True).exclude(value__isnull=True).values('sno', 'value')
	return list(qry1)


def get_semester(dept, sem_type):
	if sem_type == "odd":
		get_sem = StudentSemester.objects.filter(dept=dept).annotate(odd=F('sem') % 2).filter(odd=True).order_by('sem').values('sem', 'sem_id').order_by('sem')
	elif sem_type == "even":
		get_sem = StudentSemester.objects.filter(dept=dept).annotate(odd=F('sem') % 2).filter(odd=False).order_by('sem').values('sem', 'sem_id').order_by('sem')

	return list(get_sem)


def get_filtered_emps(dept):
	if dept == "ALL":
		q_emp = EmployeePrimdetail.objects.filter(emp_status="ACTIVE").exclude(emp_id="00007").values('emp_id', 'name', 'dept__value', 'desg__value')
	else:
		q_emp = EmployeePrimdetail.objects.filter(emp_status="ACTIVE", dept__in=str(dept).split(",")).exclude(emp_id="00007").values('emp_id', 'name', 'dept__value', 'desg__value')

	return list(q_emp)


def get_filtered_emps_with_inactive(dept):
	if dept == "ALL":
		q_emp = EmployeePrimdetail.objects.filter().exclude(emp_id="00007").values('emp_id', 'name', 'dept__value', 'desg__value')
	else:
		q_emp = EmployeePrimdetail.objects.filter(dept__in=str(dept).split(",")).exclude(emp_id="00007").values('emp_id', 'name', 'dept__value', 'desg__value')

	return list(q_emp)


def get_AcadAttendanceRegister_ClassCord(emp_id, session_name):
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	sec_id = AcadCoordinator.objects.filter(status="INSERT", coord_type='C', emp_id=emp_id).values_list('section', flat=True).distinct()
	emp_id_id = FacultyTime.objects.filter(status="INSERT", section__in=sec_id).values_list('emp_id', flat=True).distinct()
	qry = EmployeePrimdetail.objects.filter(emp_status='ACTIVE', emp_id__in=emp_id_id).exclude(emp_id=emp_id).values('name', 'emp_id')
	return list(qry)


def get_AcadAttendanceRegister_ExtraCord(emp_id, session_name):
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	coord_type = AcadCoordinator.objects.filter(status="INSERT", emp_id=emp_id).values_list('coord_type', flat=True).distinct()
	if ('E' in coord_type):
		sec_id = AcadCoordinator.objects.filter(status="INSERT", coord_type='E', emp_id=emp_id).values_list('section', flat=True).distinct()

	emp_id_id = FacultyTime.objects.filter(status="INSERT", section__in=sec_id).values_list('emp_id', flat=True).distinct()
	qry = EmployeePrimdetail.objects.filter(emp_status='ACTIVE', emp_id__in=emp_id_id).exclude(emp_id=emp_id).values('name', 'emp_id')
	return list(qry)


def get_sem_filter_subjects(sem, session_name):
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	query = SubjectInfo.objects.filter(sem=sem).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_type__value', 'subject_unit', 'subject_unit__value', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'id')
	return list(query)


def get_branch(course):
	qry = CourseDetail.objects.filter(course_id=StudentDropdown.objects.get(sno=course)).values("uid", "dept_id__value", "course_duration")
	return list(qry)


def get_academic_dept():
	qry = CourseDetail.objects.filter().values("dept_id__value", "dept_id__sno").distinct()
	return list(qry)


def get_hod_filtered_dept(dept):
	qry = CourseDetail.objects.filter(dept=dept).values("dept_id__value", "dept_id__sno").distinct()
	return list(qry)


def get_week_days():
	days = []
	for i in range(0, 7):
		days.append({'id': i, 'day_name': calendar.day_name[i]})
	return days


def get_fac_time_section_multi(emp_id, sem, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id__in=sem).values('section', 'section__section').distinct().order_by('section__section')
	return list(query)


def get_fac_time_course(emp_id, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').exclude(subject_id__status='DELETE').filter(emp_id=emp_id).values('section__sem_id__dept__course_id', 'section__sem_id__dept__course_id__value', 'session__sem_start').distinct()
	return list(query)


def get_fac_all_course(emp_id, session_name):
	Attendance = generate_session_table_name("Attendance_", session_name)

	query = Attendance.objects.exclude(status='DELETE').filter(emp_id=emp_id).values('section__sem_id__dept__course_id', 'section__sem_id__dept__course_id__value').distinct()
	return list(query)


def get_fac_time_dept(emp_id, course, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id__dept__course_id=course).values('section__sem_id__dept', 'section__sem_id__dept__dept__value').distinct()
	return list(query)


def get_fac_all_dept(emp_id, course, session_name):
	Attendance = generate_session_table_name("Attendance_", session_name)

	query = Attendance.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id__dept__course_id=course).values('section__sem_id__dept', 'section__sem_id__dept__dept__value').distinct()
	return list(query)


def get_fac_time_sem(emp_id, dept, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id__dept=dept).values('section__sem_id', 'section__sem_id__sem', 'session__sem_start', 'session__sem_end').distinct().order_by('section__sem_id__sem')
	return list(query)


def get_fac_all_sem(emp_id, dept, session_name):
	Attendance = generate_session_table_name("Attendance_", session_name)

	query = Attendance.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id__dept=dept).values('section__sem_id', 'section__sem_id__sem').distinct().order_by('section__sem_id__sem')
	return list(query)


def get_fac_time_section(emp_id, sem, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id=sem).values('section', 'section__section').distinct().order_by('section__section')
	return list(query)


def get_fac_all_section(emp_id, sem, session_name):
	Attendance = generate_session_table_name("Attendance_", session_name)

	query = Attendance.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id=sem).values('section', 'section__section').distinct().order_by('section__section')
	return list(query)


def get_fac_time_subject(emp_id, section, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)
	# #print(section)
	# #print(emp_id)
	query = FacultyTime.objects.exclude(status='DELETE').exclude(subject_id__status='DELETE').filter(emp_id=emp_id, section__in=section).values('subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'section__sem_id__sem', 'section__sem_id__dept__dept__value', 'subject_id__subject_type__value', 'subject_id__subject_type').distinct()
	return list(query)


def get_fac_time_subject_type_subject(emp_id, section, session_name, sub_type):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').exclude(subject_id__status='DELETE').filter(emp_id=emp_id, section__in=section, subject_id__subject_type=sub_type).values('subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'section__sem_id__sem', 'section__sem_id__dept__dept__value').distinct()
	return list(query)


def get_fac_time_group_subject_type_subject(emp_id, section, session_name, sub_type):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').exclude(subject_id__status='DELETE').filter(emp_id=emp_id, section__in=section, subject_id__subject_type=sub_type).values('subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'section__sem_id__sem', 'section__sem_id__dept__dept__value').distinct()
	return list(query)


def get_fac_all_subject(emp_id, section, session_name):
	Attendance = generate_session_table_name("Attendance_", session_name)

	query = Attendance.objects.exclude(status='DELETE').exclude(subject_id__status='DELETE').filter(emp_id=emp_id, section__in=section).values('subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'section', 'section__sem_id__sem', 'section__sem_id__dept__dept__value').distinct()
	return list(query)


def get_fac_all_subject(emp_id, section, session_name):
	Attendance = generate_session_table_name("Attendance_", session_name)

	query = Attendance.objects.exclude(status='DELETE').exclude(subject_id__status='DELETE').filter(emp_id=emp_id, section__in=section).values('subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'section', 'section__sem_id__sem', 'section__sem_id__dept__dept__value').distinct()
	return list(query)


def get_fac_time_subject_type_filter(emp_id, section, sub_type, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').exclude(subject_id__status='DELETE').filter(emp_id=emp_id, section__in=section, subject_id__subject_type__in=sub_type).values('subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'section__sem_id__sem', 'section__sem_id__dept__dept__value').distinct()
	return list(query)


def get_fac_time_sem_multi(emp_id, dept, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id__dept__in=dept).values('section__sem_id', 'section__sem_id__sem').distinct().order_by('section__sem_id__sem')
	return list(query)


def get_sem_dates(emp_id, dept, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').filter(emp_id=emp_id, section__sem_id__dept=dept).values('session__sem_start', 'session__sem_end').distinct()
	return query


def get_fac_time_faculty(section, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.exclude(status='DELETE').filter(section=section).values('emp_id', 'emp_id__name').distinct()
	return list(query)


def get_lectures(sem_id, day, session_name):
	TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_name)

	query2 = TimeTableSlots.objects.filter(sem_id=sem_id, day=day).filter(dean_approval_status="APPROVED").exclude(status="DELETE").values('num_lecture_slots').order_by('-id')[:1]
	if len(query2) == 0:
		query = {'lectures': 0}
	else:
		query = {'lectures': query2[0]['num_lecture_slots']}
	return query


def get_lockable_attendance_type(session):
	query = AttendanceSettings.objects.exclude(status='DELETE').filter(session=session).values('att_sub_cat', 'att_sub_cat__value').distinct()
	return list(query)


def get_coordinator_course(emp_id, coord_type, session_name):
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

	q_get_course = AcadCoordinator.objects.filter(coord_type=coord_type, emp_id=emp_id).exclude(status='DELETE').values('section__sem_id__dept__course', 'section__sem_id__dept__course__value','section__sem_id__dept__course_duration').distinct()

	return list(q_get_course)


def get_intrasection_group(section, session_name, type_of_group):
	GroupSection = generate_session_table_name("GroupSection_", session_name)

	q_group = GroupSection.objects.filter(section_id__in=section.split(','), group_id__group_type="INTRA", group_id__type_of_group=type_of_group).exclude(group_id__status="DELETE").values('group_id', 'group_id__group_name', 'group_id__type_of_group').distinct()
	return list(q_group)


def get_intersection_group(sem, session_name, type_of_group):
	GroupSection = generate_session_table_name("GroupSection_", session_name)

	q_group = GroupSection.objects.filter(section_id__sem_id=sem, group_id__group_type="INTER", group_id__type_of_group=type_of_group).exclude(group_id__status="DELETE").values('group_id', 'group_id__group_name', 'group_id__type_of_group').distinct()
	return list(q_group)


def get_att_group_students_nominal(group_id, session_name):
	data = []
	group_section = get_group_sections(group_id, session_name)
	for sec in group_section:
		data.extend(get_att_group_section_students(group_id, sec, session_name))

	return list(data)

def get_att_group_students_nominal_dept_wise(group_id, session_name,dept):
	data = []
	group_section = get_group_sections(group_id, session_name)
	print(group_section,"group section")
	for sec in group_section:
		data.extend(get_att_group_section_students_dept_wise(group_id, sec, session_name,dept))
	print(data,"dataatatataataatat")

	return list(data)

def get_emp_intrasection_group(emp_id, section, session_name):
	GroupSection = generate_session_table_name("GroupSection_", session_name)
	EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)

	q_group_id = GroupSection.objects.filter(section_id__in=str(section).split(','), group_id__group_type="INTRA").exclude(group_id__status="DELETE").values_list('group_id', flat=True).distinct()

	q_group = EmpGroupAssign.objects.filter(emp_id=emp_id, group_id__in=q_group_id).exclude(status="DELETE").values('group_id', 'group_id__group_name').distinct()
	return list(q_group)


def get_emp_intersection_group(emp_id, sem, session_name):
	GroupSection = generate_session_table_name("GroupSection_", session_name)
	EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)

	q_group_id = GroupSection.objects.filter(section_id__sem_id=sem, group_id__group_type="INTER").exclude(group_id__status="DELETE").values('group_id').distinct()

	q_group = EmpGroupAssign.objects.filter(emp_id=emp_id, group_id__in=q_group_id).exclude(status="DELETE").values('group_id', 'group_id__group_name').distinct()
	return list(q_group)


def get_coordinator_dept(emp_id, coord_type, course, session_name):
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)
	q_get_dept = AcadCoordinator.objects.filter(coord_type=coord_type, emp_id=emp_id, section__sem_id__dept__course=course).exclude(status='DELETE').values('section__sem_id__dept', 'section__sem_id__dept__dept__value').annotate(uid=F('section__sem_id__dept'), dept_id__value=F('section__sem_id__dept__dept__value')).distinct()
	return list(q_get_dept)


def get_coordinator_sem(emp_id, coord_type, dept, session_name):
	dept_li = dept.split(",")
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

	q_get_sem = AcadCoordinator.objects.filter(coord_type=coord_type, emp_id=emp_id, section__sem_id__dept__in=dept_li).exclude(status='DELETE').values('section__sem_id', 'section__sem_id__sem').distinct().order_by('section__sem_id__sem')
	return list(q_get_sem)


def get_coordinator_section(emp_id, coord_type, sem, session_name):
	sem_li = sem.split(",")
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

	q_get_section = AcadCoordinator.objects.filter(coord_type=coord_type, emp_id=emp_id, section__sem_id__in=sem_li).exclude(status='DELETE').values('section', 'section__section').distinct().order_by('section__section')
	return list(q_get_section)


def get_coordinator_subject(emp_id, coord_type, section, session_name):
	section_li = section.split(",")
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)
	# #print(section_li)
	q_get_subject = AcadCoordinator.objects.filter(coord_type=coord_type, emp_id=emp_id, section__in=section_li).exclude(status='DELETE').values('subject_id', 'subject_id__sub_name').distinct().order_by('section__section')
	return list(q_get_subject)


def get_coordinator_section_multi(emp_id, coord_type, sem_li, session_name):
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

	q_get_section = AcadCoordinator.objects.filter(coord_type=coord_type, emp_id=emp_id, section__sem_id__in=sem_li).exclude(status='DELETE').values('section__section').distinct().order_by('section__section')
	return list(q_get_section)


def get_organization():
	data = EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="ORGANIZATION").values('sno', 'value')
	return list(data)


def get_department(org):
	dept_sno = EmployeeDropdown.objects.filter(pid=org, value="DEPARTMENT").values('sno')
	data = EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'], field="DEPARTMENT").values('sno', 'value')
	return list(data)


def get_emp_category():
	data = EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="CATEGORY OF EMPLOYEE").values('sno', 'value')
	return list(data)


def get_hr_filter_emp(emp_category, dept):
	data = EmployeePrimdetail.objects.filter(emp_category__in=emp_category, dept__in=dept, emp_status='ACTIVE').values('emp_id', 'name')
	return list(data)


# def get_section_students(section, extra_filter, session_name):
#   stu_data = []
#   studentSession = generate_session_table_name("studentSession_", session_name)

#   for sec in section:
#       qry = studentSession.objects.filter(section=sec).filter(**extra_filter).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'section__sem_id__sem', 'section__sem_id', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'registration_status', 'reg_form_status', 'reg_date_time', 'fee_status', 'att_start_date', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__lib_id', 'uniq_id__gender', 'uniq_id__gender__value', 'session__sem_start', 'section').order_by('class_roll_no')
#       for q in qry:
#           q_fname = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname')
#           q_fmob = StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id']).values('father_mob')
#           if len(q_fname) > 0:
#               q['fname'] = q_fname[0]['fname']
#           else:
#               q['fname'] = "---"
#           if len(q_fmob) > 0:
#               q['father_mob'] = q_fmob[0]['father_mob']
#           else:
#               q['fname'] = "---"
#       stu_data.append(list(qry))
#   return list(stu_data)


def Declarationpdf(uniq_id, session_name):
	studentSession = generate_session_table_name("studentSession_", session_name)
	StudentFillSubjects = generate_session_table_name("StudentFillSubjects_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

	receipt_name = "DECLARATION FORM"
	filename = "declaration.pdf"

	bool_white = False

	if not bool_white:
		img = Image.open(settings.FILE_PATH + "img_dec_18_19.jpg")
	else:
		img = Image.new(mode='RGB', size=(1478, 2100), color=(255, 255, 255, 0))

	size = 2480, 3508
	img.thumbnail(size, Image.ANTIALIAS)
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype(settings.FILE_PATH + "arial.ttf", 22)

	stu_det = studentSession.objects.filter(uniq_id=uniq_id).values('reg_date_time', 'year', 'uniq_id__name', 'sem__dept__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__email_id', 'sem__sem', 'section', 'mob', 'uniq_id__admission_category__value', 'uniq_id__caste__value', 'section__section')

	final_img_width = min(img.size[0], 1478)
	final_img_height = min(img.size[1], 2100)
	tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")
	PerDetail = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('religion__value', 'fname', 'mob_sec', 'dob', 'image_path', 'aadhar_num', 'bank_acc_no', 'pan_no', 'uan_no', 'physically_disabled', 'bg', 'marital_status', 'nationality', 'religion', 'mname', 'caste_name', 'nation_other')
	for x in PerDetail:
		for keys in x:
			if x[keys] is None:
				x[keys] = "--"
	Address = StudentAddress.objects.filter(uniq_id=uniq_id).values('p_add1', 'p_add2', 'p_city', 'p_district', 'p_pincode', 'c_add1', 'c_add2', 'c_city', 'c_district', 'c_pincode', 'c_state__value', 'p_state', 'c_state__value', 'p_state__value')
	for x in Address:
		for keys in x:
			if x[keys] is None:
				x[keys] = "--"
	FamilyDetails = StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values()
	index = 0
	margin_left = 0
	margin_top = 0
	if stu_det[0]['reg_date_time'] is None:
		reg_date = date.today()
	else:
		reg_date = stu_det[0]['reg_date_time'].date()
	draw.text((287, 265), str(reg_date), (0, 0, 0), font=font)
	draw.text((287, 300), str(stu_det[0]['uniq_id__uni_roll_no']), (0, 0, 0), font=font)
	draw.text((287, 335), str(stu_det[0]['uniq_id__name']), (0, 0, 0), font=font)
	draw.text((300, 400), str(PerDetail[0]['fname']), (0, 0, 0), font=font)
	draw.text((287, 455), str(FamilyDetails[0]['father_mob']), (0, 0, 0), font=font)
	draw.text((287, 500), str(stu_det[0]['uniq_id__email_id']), (0, 0, 0), font=font)

	draw.text((187 + 600, 300), str(stu_det[0]['sem__dept__course__value']), (0, 0, 0), font=font)
	draw.text((187 + 600 + 250, 300), str(stu_det[0]['sem__sem']), (0, 0, 0), font=font)
	if(stu_det[0]['section'] is None):
		draw.text((187 + 600 + 390, 300), 'NA', (0, 0, 0), font=font)
	else:
		draw.text((187 + 600 + 390, 300), str(stu_det[0]['section__section']), (0, 0, 0), font=font)
	draw.text((287 + 600, 335), str(stu_det[0]['mob']), (0, 0, 0), font=font)
	draw.text((200 + 600, 390), str(stu_det[0]['uniq_id__caste__value']), (0, 0, 0), font=font)
	draw.text((187 + 600, 445), str(PerDetail[0]['religion__value']), (0, 0, 0), font=font)
	phyDis = PerDetail[0]['physically_disabled']
	if phyDis == 'Y':
		st = "YES"
	else:
		st = 'NO'
	draw.text((287 + 600, 500), st, (0, 0, 0), font=font)

	draw.text((60, 565), str(Address[0]['c_add1']), (0, 0, 0), font=font)
	draw.text((60, 600), str(Address[0]['c_add2']), (0, 0, 0), font=font)
	draw.text((60, 640), str(Address[0]['c_district']), (0, 0, 0), font=font)
	draw.text((120, 680), str(Address[0]['c_city']), (0, 0, 0), font=font)
	draw.text((480, 680), str(Address[0]['c_pincode']), (0, 0, 0), font=font)
	draw.text((140, 715), str(Address[0]['c_state__value']), (0, 0, 0), font=font)
	draw.text((287, 755), '------', (0, 0, 0), font=font)

	draw.text((60 + 600, 565), str(Address[0]['p_add1']), (0, 0, 0), font=font)
	draw.text((60 + 600, 600), str(Address[0]['p_add2']), (0, 0, 0), font=font)
	draw.text((60 + 600, 640), str(Address[0]['p_district']), (0, 0, 0), font=font)
	draw.text((120 + 600, 680), str(Address[0]['p_city']), (0, 0, 0), font=font)
	draw.text((480 + 600, 680), str(Address[0]['p_pincode']), (0, 0, 0), font=font)
	draw.text((140 + 600, 715), str(Address[0]['p_state__value']), (0, 0, 0), font=font)
	draw.text((287 + 600, 755), '------', (0, 0, 0), font=font)

	q_sec = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id')

	sub_selected = []
	filled_subject = StudentFillSubjects.objects.filter(uniq_id=uniq_id).distinct().values_list('subject_id', flat=True)
	sub = SubjectInfo.objects.filter(sem=q_sec[0]['section__sem_id'], id__in=filled_subject).exclude(status='DELETE').values('subject_type__value', 'subject_unit__value', 'sub_alpha_code', 'sub_num_code', 'sub_name', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'no_of_units', 'id')

	for s in sub:
		sub_selected.append({'subject_id__sub_alpha_code': s['sub_alpha_code'], 'subject_id__sub_num_code': s['sub_num_code'], 'subject_id__sub_name': s['sub_name']})
	k = 0
	for x in sub_selected:
		height = k * 38
		k = k + 1
		try:
			draw.text((220, 860 + height), str(x["subject_id__sub_alpha_code"]) + str(x["subject_id__sub_num_code"]), (0, 0, 0), font=font)
		except:
			draw.text((220, 860 + height), '----' + str(x["subject_id__sub_num_code"]), (0, 0, 0), font=font)
		try:
			draw.text((400, 860 + height), str(x['subject_id__sub_name']), (0, 0, 0), font=font)
		except:
			draw.text((400, 860 + height), '----', (0, 0, 0), font=font)

	x = index // 2 * (tmp_image.size[0] // 2)
	y = index % 2 * (tmp_image.size[1] // 2)
	w, h = img.size
	tmp_image.paste(img, (x, y, x + w, y + h))

	tmp_image.save(settings.FILE_PATH + filename, "PDF", resolution=250.0)
	with open(settings.FILE_PATH + filename, 'rb') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'inline;filename=some_file.pdf'

		return response
		pdf.closed


def printDeclaration(request):
	data_values = {}
	msg = ""
	status = 403
	# if 'HTTP_COOKIE' in request.META:
	#     if request.user.is_authenticated:
	session = Semtiming.objects.get(uid=request.session['Session_id'])
	session_name = request.session['Session_name']
	studentSession = generate_session_table_name("studentSession_", session_name)
	StudentFillInsurance = generate_session_table_name("StudentFillInsurance_", session_name)
	StudentHobbyClubs = generate_session_table_name("StudentHobbyClubs_", session_name)
	if(request.method == 'GET'):
		if(request.GET['request_type'] == 'printDeclarationpdf'):
			uniq_id = request.GET['uniq_id']
			stu_det = list(studentSession.objects.filter(uniq_id=uniq_id).values('reg_date_time', 'year', 'uniq_id__name', 'uniq_id__stu_type__value', 'sem__dept__dept__value', 'sem__dept__course__value', 'uniq_id__lib', 'uniq_id__uni_roll_no', 'uniq_id__batch_from', 'uniq_id__batch_to', 'uniq_id__email_id', 'sem__sem', 'section', 'mob', 'uniq_id__admission_category__value', 'uniq_id__caste__value', 'section__section'))
			if(stu_det[0]['uniq_id__uni_roll_no'] is None):
				stu_det[0]['uniq_id__uni_roll_no'] = stu_det[0]['uniq_id__lib']
			personal_details = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('religion__value', 'fname', 'mob_sec', 'dob', 'image_path', 'aadhar_num', 'bank_acc_no', 'pan_no', 'uan_no', 'physically_disabled', 'bg', 'marital_status', 'nationality', 'religion', 'mname', 'caste_name', 'nation_other')
			insurance_details = StudentFillInsurance.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('nominee_name', 'nominee_relation', 'insurer_name', 'insurer_dob', 'insurer_aadhar_num', 'insurer_occupation', 'insurer_nominee_name', 'insurer_relation')
			bank_details = StudentBankDetails.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('acc_name', 'acc_num', 'bank_name', 'ifsc_code', 'branch', 'address')
			family_details = StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values('father_mob', 'mother_mob', 'father_occupation', 'mother_occupation', 'mother_uan_no', 'mother_uan_no', 'father_uan_no')
			hobby_club = list(StudentHobbyClubs.objects.filter(uniq_id=uniq_id).values('hobby_club__value', 'hobby_club__field'))
			data_values = {'stu_det': stu_det, 'personal_details': list(personal_details), 'insurance_details': list(insurance_details), 'bank_details': list(bank_details), 'family_details': list(family_details), 'hobby_club': hobby_club}
			status = 200
	else:
		status = 502
		msg = "Bad Request"
	#     else:
	#         status = 401
	#         msg = "Not Authorized"
	# else:
	#     status = 500
	#     msg = "Error"

	# data_values = {'msg': msg}
	return JsonResponse(data=data_values, status=status)


def get_section_registration_students(section, extra_filter, session_name):
	stu_data = []
	studentSession = generate_session_table_name("studentSession_", session_name)

	for sec in section:
		qry = studentSession.objects.filter(section=sec).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'section__sem_id__sem', 'section__sem_id', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'registration_status', 'reg_form_status', 'reg_date_time', 'fee_status', 'att_start_date', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__lib_id', 'uniq_id__gender', 'uniq_id__gender__value', 'session__sem_start', 'section').order_by('class_roll_no')
		for q in qry:
			q_fname = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname')
			q_fmob = StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id']).values('father_mob')
			due_checking_acad = SubmitFee.objects.filter(uniq_id=q['uniq_id'], fee_rec_no__contains="A", cancelled_status='N').exclude(status="DELETE").values('due_value', 'due_date').order_by('-id')
			due_checking_host = SubmitFee.objects.filter(uniq_id=q['uniq_id'], fee_rec_no__contains="H", cancelled_status='N', session__session_name=session_name).exclude(status="DELETE").values('due_value', 'due_date').order_by('-id')
			# q['fee_status'] = 'PAID'

			if len(due_checking_acad) > 0:
				if due_checking_acad[0]['due_value']is not None and due_checking_acad[0]['due_date']is not None:
					if due_checking_acad[0]['due_value'] > 0 and due_checking_acad[0]['due_date'] <= datetime.date(datetime.now()):
						q['fee_status'] = "UNPAID"

			if len(due_checking_host) > 0:
				if due_checking_host[0]['due_value']is not None and due_checking_host[0]['due_date']is not None:
					if due_checking_host[0]['due_value'] > 0 and due_checking_host[0]['due_date'] <= datetime.date(datetime.now()):
						q['fee_status'] = "UNPAID"

			if len(q_fname) > 0:
				q['fname'] = q_fname[0]['fname']
			else:
				q['fname'] = "---"
			if len(q_fmob) > 0:
				q['father_mob'] = q_fmob[0]['father_mob']
			else:
				q['fname'] = "---"
		stu_data.append(list(qry))
	return list(stu_data)


def get_att_group_section_students(group_id, section, session_name):
	stu_data = []
	StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	filters = {}
	if section == []:
		filters = {}
	else:
		if type(section) == 'list':
			filters['uniq_id__section__in'] = section
		else:
			filters['uniq_id__section__in'] = str(section).split(',')
	# #print(group_id,section,session_name)
	group_students = StuGroupAssign.objects.filter(group_id=group_id).filter(**filters).exclude(status='DELETE').exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__section__sem_id__sem', 'uniq_id__section__section', 'uniq_id__year', 'uniq_id__section__sem_id__dept__dept__value', 'uniq_id__class_roll_no', 'uniq_id__mob', 'uniq_id__registration_status', 'uniq_id__reg_form_status', 'uniq_id__reg_date_time', 'uniq_id__fee_status', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__uniq_id__lib_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'uniq_id__section', 'uniq_id__att_start_date').order_by('uniq_id__class_roll_no', 'uniq_id__section__section')

	for gr in group_students:

		q_fname = StudentPerDetail.objects.filter(uniq_id=gr['uniq_id']).values('fname')
		q_fmob = StudentFamilyDetails.objects.filter(uniq_id=gr['uniq_id']).values('father_mob')
		if len(q_fname) > 0:
			gr['fname'] = q_fname[0]['fname']
		else:
			gr['fname'] = "---"
		if len(q_fmob) > 0:
			gr['father_mob'] = q_fmob[0]['father_mob']
		else:
			gr['fname'] = "---"

		stu_data.append({'uniq_id': gr['uniq_id'], 'uniq_id__name': gr['uniq_id__uniq_id__name'], 'section__sem_id__sem': gr['uniq_id__section__sem_id__sem'], 'section__section': gr['uniq_id__section__section'], 'year': gr['uniq_id__year'], 'section__sem_id__dept__dept__value': gr['uniq_id__section__sem_id__dept__dept__value'], 'class_roll_no': gr['uniq_id__class_roll_no'], 'mob': gr['uniq_id__mob'], 'registration_status': gr['uniq_id__registration_status'], 'reg_form_status': gr['uniq_id__reg_form_status'], 'reg_date_time': gr['uniq_id__reg_date_time'], 'fee_status': gr['uniq_id__fee_status'], 'uniq_id__uni_roll_no': gr['uniq_id__uniq_id__uni_roll_no'], 'fname': gr['fname'], 'father_mob': gr['father_mob'], 'uniq_id__lib_id': gr['uniq_id__uniq_id__lib_id'], 'uniq_id__dept_detail__dept__value': gr['uniq_id__uniq_id__dept_detail__dept__value'], 'section': gr['uniq_id__section'], 'att_start_date': gr['uniq_id__att_start_date']})
	return stu_data

def get_att_group_section_students_dept_wise(group_id, section, session_name,primary_branch):
	stu_data = []
	StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	filters = {}
	filters['uniq_id__uniq_id__dept_detail__dept_id__in']=primary_branch
	if section == []:
		filters = {}
	else:
		if type(section) == 'list':
			filters['uniq_id__section__in'] = section
		else:
			filters['uniq_id__section__in'] = str(section).split(',')
	# #print(group_id,section,session_name)
	group_students = StuGroupAssign.objects.filter(group_id=group_id).filter(**filters).exclude(status='DELETE').exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__section__sem_id__sem', 'uniq_id__section__section', 'uniq_id__year', 'uniq_id__section__sem_id__dept__dept__value', 'uniq_id__class_roll_no', 'uniq_id__mob', 'uniq_id__registration_status', 'uniq_id__reg_form_status', 'uniq_id__reg_date_time', 'uniq_id__fee_status', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__uniq_id__lib_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'uniq_id__section', 'uniq_id__att_start_date').order_by('uniq_id__class_roll_no', 'uniq_id__section__section')
	print(group_students,"group_students")

	for gr in group_students:

		q_fname = StudentPerDetail.objects.filter(uniq_id=gr['uniq_id']).values('fname')
		q_fmob = StudentFamilyDetails.objects.filter(uniq_id=gr['uniq_id']).values('father_mob')
		if len(q_fname) > 0:
			gr['fname'] = q_fname[0]['fname']
		else:
			gr['fname'] = "---"
		if len(q_fmob) > 0:
			gr['father_mob'] = q_fmob[0]['father_mob']
		else:
			gr['fname'] = "---"

		stu_data.append({'uniq_id': gr['uniq_id'], 'uniq_id__name': gr['uniq_id__uniq_id__name'], 'section__sem_id__sem': gr['uniq_id__section__sem_id__sem'], 'section__section': gr['uniq_id__section__section'], 'year': gr['uniq_id__year'], 'section__sem_id__dept__dept__value': gr['uniq_id__section__sem_id__dept__dept__value'], 'class_roll_no': gr['uniq_id__class_roll_no'], 'mob': gr['uniq_id__mob'], 'registration_status': gr['uniq_id__registration_status'], 'reg_form_status': gr['uniq_id__reg_form_status'], 'reg_date_time': gr['uniq_id__reg_date_time'], 'fee_status': gr['uniq_id__fee_status'], 'uniq_id__uni_roll_no': gr['uniq_id__uniq_id__uni_roll_no'], 'fname': gr['fname'], 'father_mob': gr['father_mob'], 'uniq_id__lib_id': gr['uniq_id__uniq_id__lib_id'], 'uniq_id__dept_detail__dept__value': gr['uniq_id__uniq_id__dept_detail__dept__value'], 'section': gr['uniq_id__section'], 'att_start_date': gr['uniq_id__att_start_date']})
	return stu_data



# def get_section_students(section, extra_filter, session_name):
#   stu_data = []
#   studentSession = generate_session_table_name("studentSession_", session_name)

#   for sec in section:
#       qry = studentSession.objects.filter(section=sec).filter(**extra_filter).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'section__sem_id__sem', 'section__sem_id', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'registration_status', 'reg_form_status', 'reg_date_time', 'fee_status', 'att_start_date', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__lib_id', 'uniq_id__gender', 'uniq_id__gender__value', 'session__sem_start', 'section').order_by('class_roll_no')
#       for q in qry:
#           q['att_start_date'] = q['att_start_date'].strftime('%Y-%m-%d')
#           q['session__sem_start'] = q['session__sem_start'].strftime('%Y-%m-%d')

#           q_fname = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname')
#           q_fmob = StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id']).values('father_mob')
#           if len(q_fname) > 0:
#               q['fname'] = q_fname[0]['fname']
#           else:
#               q['fname'] = "---"
#           if len(q_fmob) > 0:
#               q['father_mob'] = q_fmob[0]['father_mob']
#           else:
#               q['fname'] = "---"
#       stu_data.append(list(qry))
#   return list(stu_data)

def get_section_students(section, extra_filter, session_name):
	stu_data = []
	studentSession = generate_session_table_name("studentSession_", session_name)
	StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
	SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
	GroupSection = generate_session_table_name("GroupSection_", session_name)
	EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
	for sec in section:
		qry = studentSession.objects.filter(section=sec).filter(**extra_filter).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'uniq_id__email_id', 'section__sem_id__sem', 'section__sem_id', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'registration_status', 'reg_form_status', 'reg_date_time', 'fee_status', 'att_start_date', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__lib_id', 'uniq_id__gender', 'uniq_id__gender__value', 'session__sem_start', 'sem__sem', 'section').order_by('class_roll_no')
		for q in qry:
			q['att_start_date'] = q['att_start_date'].strftime('%Y-%m-%d')
			q['session__sem_start'] = q['session__sem_start'].strftime('%Y-%m-%d')
			q['mentor_name'] = '---'
			q['mentor_emp_id'] = '---'
			q_fname = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname', 'mname', 'nationality__value', 'aadhar_num', 'bank_acc_no', 'religion__value', 'caste_name', 'dob', 'physically_disabled')
			q_fmob = StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id']).values('father_mob', 'mother_mob', 'g_email', 'father_city', 'father_email', 'mother_email')
			if len(q_fname) > 0:
				q['fname'] = q_fname[0]['fname']
				q['mname'] = q_fname[0]['mname']
				q['nationality'] = q_fname[0]['nationality__value']
				q['aadhar_num'] = q_fname[0]['aadhar_num']
				q['religion'] = q_fname[0]['religion__value']
				q['caste_name'] = q_fname[0]['caste_name']
				q['dob'] = q_fname[0]['dob']
				q['physically_disabled'] = q_fname[0]['physically_disabled']
			if len(q_fmob) > 0:
				q['father_mob'] = q_fmob[0]['father_mob']
				q['mother_mob'] = q_fmob[0]['mother_mob']
				q['g_email'] = q_fmob[0]['g_email']
				q['father_city'] = q_fmob[0]['father_city']
				q['father_email'] = q_fmob[0]['father_email']
				q['mother_email'] = q_fmob[0]['mother_email']

			sem = q['sem__sem']
			group_id = list(StuGroupAssign.objects.filter(uniq_id=q['uniq_id'], group_id__type_of_group='MENTOR').exclude(status='DELETE').values_list('group_id'))
			sem_group = list(GroupSection.objects.filter(section_id__sem_id__sem=sem, group_id__in=group_id).values_list('group_id'))
			mentor_name = EmpGroupAssign.objects.filter(group_id__in=sem_group).exclude(status='DELETE').values('emp_id__name', 'emp_id')
			# print(mentor_name)
			if mentor_name:
				q['mentor_name'] = mentor_name[0]['emp_id__name']
				q['mentor_emp_id'] = mentor_name[0]['emp_id']
			else:
				Mentor_Name = {}

		stu_data.append(list(qry))
	return list(stu_data)


def get_students_data_from_uniq_id(uniq_id_list, session_name):
	stu_data = []
	studentSession = generate_session_table_name("studentSession_", session_name)

	qry = studentSession.objects.filter(uniq_id__in=uniq_id_list).values('uniq_id', 'uniq_id__name', 'section__sem_id__sem', 'section__sem_id', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'registration_status', 'reg_form_status', 'reg_date_time', 'fee_status', 'att_start_date', 'uniq_id__dept_detail__dept__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__lib_id', 'uniq_id__gender', 'uniq_id__gender__value', 'session__sem_start', 'section').order_by('class_roll_no')
	for q in qry:
		q['att_start_date'] = q['att_start_date'].strftime('%Y-%m-%d')
		q['session__sem_start'] = q['session__sem_start'].strftime('%Y-%m-%d')

		q_fname = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname')
		q_fmob = StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id']).values('father_mob')
		if len(q_fname) > 0:
			q['fname'] = q_fname[0]['fname']
		else:
			q['fname'] = "---"
		if len(q_fmob) > 0:
			q['father_mob'] = q_fmob[0]['father_mob']
		else:
			q['fname'] = "---"

	return list(qry)


def get_att_group_students(group_id, session_name):
	data = []
	group_section = get_group_sections(group_id, session_name)
	for sec in group_section:
		data.append(get_att_group_section_students(group_id, sec, session_name))

	return list(data)


def get_att_group_students_att_register(group_id, session_name):
	data = []
	data1 = [[]]
	group_section = get_group_sections(group_id, session_name)
	# #print(group_section,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	for sec in group_section:
		data.append(get_att_group_section_students(group_id, sec, session_name))

	for x in data:
		data1[0].extend(x)
	# #print(data1[0], 'data1')
	return list(data1)


def get_group_sections(group_id, session_name):
	GroupSection = generate_session_table_name("GroupSection_", session_name)

	q_group_sec = GroupSection.objects.filter(group_id=group_id).values_list('section_id', flat=True).distinct()

	return list(q_group_sec)


def get_fac_app_profile(emp_id):
	q_details = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('emp_id', 'name', 'dept__value', 'desg__value', 'mob', 'email')
	q_img = EmployeePerdetail.objects.filter(emp_id=emp_id).values('image_path')

	data = q_details[0]
	data['image_path'] = settings.BASE_URL2 + "Musterroll/Employee_images/" + q_img[0]['image_path']
	return data


def get_employee_time_table(emp_id, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)
	# ADDED  IDs for Fields
	q_time_table = FacultyTime.objects.filter(emp_id=emp_id).exclude(status='DELETE').exclude(subject_id__status="DELETE").values('subject_id', 'subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code', 'section', 'section__section', 'section', 'section__sem_id__sem', 'section__sem_id__dept__course_id__value', 'section__sem_id__dept__dept__value', 'end_time', 'start_time', 'day', 'lec_num').order_by('day', 'lec_num')
	# #print(q_time_table)
	result = (collections.defaultdict(list))

	for d in list(q_time_table):
		result[d['day']].append(d)

	result_list = list(result.values())
	return result_list


def get_section_time_table(section, session_name):
	data = []
	i = 0
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	q_time_table = FacultyTime.objects.filter(section=section).exclude(status='DELETE').values('day').order_by('day').distinct()
	for d in q_time_table:
		q_time_table2 = FacultyTime.objects.filter(section=section, day=d['day']).exclude(status='DELETE').values('lec_num').order_by('lec_num').distinct()

		day_lec = []
		day_sub_code = []
		day_sub_name = []
		day_sub_type = []
		day_sub_unit = []
		day_emp_id = []
		day_emp_name = []
		day_emp_dept = []
		day_start_time = []
		day_end_time = []

		for l in q_time_table2:
			q_time_table3 = FacultyTime.objects.filter(section=section, day=d['day'], lec_num=l['lec_num']).exclude(status='DELETE').values('subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code', 'end_time', 'start_time', 'emp_id__name', 'emp_id', 'emp_id__dept__value', 'subject_id__subject_type__value', 'subject_id__subject_unit__value')
			sub_code = []
			sub_name = []
			sub_type = []
			sub_unit = []
			emp_id = []
			emp_name = []
			emp_dept = []
			start_time = ""
			end_time = ""
			for t in q_time_table3:
				sub_code.append(t['subject_id__sub_alpha_code'] + "-" + str(t['subject_id__sub_num_code']))
				sub_name.append(t['subject_id__sub_name'])
				sub_type.append(t['subject_id__subject_type__value'])
				sub_unit.append(t['subject_id__subject_unit__value'])
				emp_id.append(t['emp_id'])
				emp_name.append(t['emp_id__name'])
				emp_dept.append(t['emp_id__dept__value'])
				start_time = t['start_time']
				end_time = t['end_time']

			day_lec.append(str(l['lec_num']))
			day_sub_code.append(','.join(list(set(sub_code))))
			day_sub_name.append(','.join(list(set(sub_name))))
			day_sub_type.append(','.join(list(set(sub_type))))
			day_sub_unit.append(','.join(list(set(sub_unit))))
			day_emp_id.append(','.join(list(set(emp_id))))
			day_emp_name.append(','.join(list(set(emp_name))))
			day_emp_dept.append(','.join(list(set(emp_dept))))
			day_start_time.append(start_time)
			day_end_time.append(end_time)

		data.append({'Name': calendar.day_name[d['day']], 'lecture_no': day_lec, 'sub_code': day_sub_code, 'subject_name': day_sub_name, 'faculty_name': day_emp_name, 'faculty_id': day_emp_id, 'faculty_dept': day_emp_dept, 'sub_type': day_sub_type, 'sub_unit': day_sub_unit, 'start_time': day_start_time, 'end_time': day_end_time})

	return data


def checkIsAttendanceAlreadyMarked(lecture, section, group_id, date, session_name):
	Attendance = generate_session_table_name("Attendance_", session_name)

	if group_id is None:
		q_check = Attendance.objects.filter(date=date, lecture=lecture, section=section).exclude(status='DELETE').values('emp_id', 'emp_id__name', 'section__section', 'section__sem_id__sem', 'subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code', 'lecture')
		if len(q_check) > 0:
			return {'already_marked': True, 'msg': 'Attendance already marked for ' + str(q_check[0]['section__sem_id__sem']) + "-" + q_check[0]['section__section'] + " for lecture " + str(q_check[0]['lecture']) + " by " + q_check[0]['emp_id__name'] + " for " + q_check[0]['subject_id__sub_name']}
		else:
			return {'already_marked': False, 'msg': ''}
	else:
		q_check = Attendance.objects.filter(date=date, lecture=lecture, section=section).filter(Q(group_id=group_id) | Q(group_id__isnull=True)).exclude(status='DELETE').values('emp_id', 'emp_id__name', 'section__section', 'section__sem_id__sem', 'subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code', 'lecture')
		if len(q_check) > 0:
			return {'already_marked': True, 'msg': 'Attendance already marked for ' + str(q_check[0]['section__sem_id__sem']) + "-" + q_check[0]['section__section'] + " for lecture " + str(q_check[0]['lecture']) + " by " + q_check[0]['emp_id__name'] + " for " + q_check[0]['subject_id__sub_name']}
		else:
			return {'already_marked': False, 'msg': ''}


def checkIsAttendanceLocked(course, emp_id, date, att_cat, session, year, section, session_name, extra_filter):

	if ('updated_date' in extra_filter):
		today_date = extra_filter['updated_date']
		today_date_time = datetime.combine(today_date, datetime.min.time())
	else:
		today_date_time = datetime.today()
		today_date = today_date_time.date()

	LockingUnlocking = generate_session_table_name("LockingUnlocking_", session_name)
	emp_id_dept = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
	dept = emp_id_dept[0]['dept']
	q_att_details = AttendanceSettings.objects.filter(session=session, year=year, att_sub_cat=att_cat, course=course, lock_type='Y').exclude(status="DELETE").values('days_lock')

	if len(q_att_details) > 0:
		days_lock = q_att_details[0]['days_lock']
		date_to_be_checked = today_date
		while days_lock > 0:
			check_holiday = Holiday.objects.filter(f_date__lte=date_to_be_checked, t_date__gte=date_to_be_checked, dept=dept).exclude(status='DELETE').values()
			if len(check_holiday) > 0:
				pass
			else:
				days_lock -= 1

			date_to_be_checked = date_to_be_checked - relativedelta(days=+1)

		if date <= date_to_be_checked:
			q_find = LockingUnlocking.objects.filter(lock_type='ATT', emp_id=emp_id, section=section, att_type=att_cat, att_date_from__lte=date, att_date_to__gte=date, unlock_from__lte=today_date_time, unlock_to__gte=today_date_time).order_by('-id').values('id')[:1]

			if len(q_find) == 0:
				return True

	return False


def check_islocked(lock_type, section_li, session_name):
	if lock_type not in ['F', 'SUR', 'MMS']:
		return False
	today = datetime.now()- timedelta(seconds=20)
	LockingUnlocking = generate_session_table_name("LockingUnlocking_", session_name)

	qry_check = LockingUnlocking.objects.filter(lock_type=lock_type, section__in=section_li).values('unlock_to', 'unlock_from').order_by('-id')
	# #print(qry_check, "astha")
	if len(qry_check) > 0:
		if qry_check[0]['unlock_to'].replace(tzinfo=None) > today and qry_check[0]['unlock_from'].replace(tzinfo=None)	 <= today:
			return False
		else:
			return True
	else:
		return True


def get_student_subjects(sem, session_name):
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	query = SubjectInfo.objects.filter(sem=sem).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name').order_by('id')
	return list(query)


def get_student_lab_theory_subjects(sem, code, session_name):
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	if code == 'l' or code == 'L':
		query = SubjectInfo.objects.filter(sem=sem, subject_type__field='LAB').exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'session', 'sem', 'id', 'subject_type__value').order_by('id')
	if code == 't' or code == 'T':
		query = SubjectInfo.objects.filter(sem=sem, subject_type__field='THEORY').exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'session', 'sem', 'id', 'subject_type__value').order_by('id')
	return list(query)


def get_color():
	att_type_color = []

	att_type_color.append({'NORMAL': '#f9f9f6', 'REMEDIAL': '#499DF5', 'DAY-WISE': '#CD8500', 'TUTORIAL': '#FFFF00', 'EXTRA': '#754C78', 'MEDICAL': '#007181', 'ORIENTATION ATTENDANCE': '#ed6160', 'APTITUDE ATTENDANCE': '#662f63', 'INDUSTRIAL VISIT': '#ff4040', 'NO CAPPING': '#654321', '10% CAPPING': '3b5dab', '20% CAPPING': '#890001', 'IMPROVEMENT': '#4CAF54'})

	return att_type_color


def get_color_app():
	att_type_color = []

	att_type_color.append({'N': '#f9f9f6', 'R': '#499DF5', 'D': '#CD8500', 'T': '#FFFF00', 'E': '#754C78'})

	return att_type_color


def get_color_attendance_type(att_type):
	att_type_color = None

	color = {'NORMAL': '#4CAF50', 'REMEDIAL': '#9C27B0', 'MEDICAL': '#F44336', 'SAE PROJECT': '#CDDC39', 'EVENTS': '#29B6F6', 'PLACEMENT': '#3F51B5', 'SUBSTITUTE': '#000000', 'TUTORIAL': '#FF9800', 'SUBSTITUTE LECTURE WISE': '#cda85c','DOUBT CLEARING ATTENDANCE':'#084666','ATTENDANCE IMPROVEMENT':'#003953'}
	if str(att_type) in color:
		att_type_color = color[str(att_type)]

	return att_type_color

# def get_student_attendance(uniq_id, from_date, to_date, session, att_type_li, q_sub, flg_branch_change, att_category_li, session_name):
#     att_data = []
#     stu_extra_att = []
#     class_attendance_type = []

#     studentSession = generate_session_table_name("studentSession_", session_name)
#     StudentBranchChange = generate_session_table_name("StudentBranchChange_", session_name)
#     SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
#     StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
#     StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

#     q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')

#     if len(att_category_li) == 0:
#         att_category_li = list(AttendanceSettings.objects.filter(course=q_stu_details[0]['uniq_id__dept_detail__course'], session=session, year=q_stu_details[0]['year'], admission_type=q_stu_details[0]['uniq_id__admission_type'], att_sub_cat__in=att_type_li).exclude(status='DELETE').values_list('attendance_category', flat=True).order_by().distinct())

#     ################### BRANCH CHANGE ATTENDANCE ##########################

#     branch_change = {'present': 0, 'absent': 0, 'total': 0}

#     if flg_branch_change == 1:
#         q_check = StudentBranchChange.objects.filter(uniq_id=uniq_id, change_type='S').exclude(old_section__isnull=True).values('old_section__sem_id', 'date')
#         for qc in q_check:
#             q_sub2 = SubjectInfo.objects.filter(sem=qc['old_section__sem_id']).exclude(status="DELETE").values('id').order_by('id')

#             branch_change_data = get_student_attendance(uniq_id, from_date, qc['date'], session, att_type_li, list(q_sub2), 0, att_category_li, session_name)
#             from_date = qc['date']

#             branch_change['present'] += branch_change_data['present_count']
#             branch_change['absent'] += branch_change_data['absent_count']
#             branch_change['total'] += branch_change_data['total']

#     ################### BRANCH CHANGE ATTENDANCE END ##########################

#     sub_id = [d['id'] for d in q_sub]
#     att_data = q_sub

#     q_stu_group = StuGroupAssign.objects.filter(uniq_id=uniq_id).values_list('group_id', flat=True)
#     qry = StudentAcademicsDropdown.objects.filter(field="ATTENDANCE TYPE", value__in=["NORMAL ATTENDANCE", 'REMEDIAL ATTENDANCE', 'TUTORIAL ATTENDANCE'], session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
#     # qry=StudentAcademicsDropdown.objects.filter(field="ATTENDANCE TYPE",value__in=["NORMAL ATTENDANCE",'REMEDIAL ATTENDANCE','TUTORIAL ATTENDANCE','DAY-WISE ATTENDANCE'],session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
#     for q in qry:
#         qr = StudentAcademicsDropdown.objects.filter(pid=q['sno'], sno__in=att_type_li, session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
#         for q2 in qr:
#             class_attendance_type.append(q2['sno'])

#     q_sub_normal_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, present_status='P', att_type__in=class_attendance_type, att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=att_category_li) | Q(att_category__isnull=True)).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(present_count=Count('uniq_id')).order_by()

#     present_sub_li = [d['att_id__subject_id'] for d in q_sub_normal_att_present]

#     q_sub_normal_att_total = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(total=Count('uniq_id')).order_by()

#     total_sub_li = [d['att_id__subject_id'] for d in q_sub_normal_att_total]

#     att_total = {}
#     att_total['present_count'] = 0
#     att_total['total'] = 0
#     att_total['absent_count'] = 0
#     att_total['extra'] = []

#     for att in att_data:
#         stu_extra_att.append({'sub_id': att['id'], 'extra_capping': [], 'extra_no_capping': []})

#         if att['id'] in present_sub_li:
#             index = present_sub_li.index(att['id'])
#             att['present_count'] = q_sub_normal_att_present[index]['present_count']
#         else:
#             att['present_count'] = 0

#         if att['id'] in total_sub_li:
#             index = total_sub_li.index(att['id'])
#             att['total'] = q_sub_normal_att_total[index]['total']
#         else:
#             att['total'] = 0

#         att['absent_count'] = att['total'] - att['present_count']

#         att_total['present_count'] += att['present_count']
#         att_total['total'] += att['total']

#     ######################### NORMAL ATTENDANCE CALCULATION END ############################################

#     ######################### EXTRA ATTENDANCE CALCULATION ############################################

#     extra_attendance_type = []

#     q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')
#     year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
#     course = q_year[0]['dept__course']

#     query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=att_type_li).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
#     for q in query_att:
#         extra_attendance_type.append({'sno': q['att_sub_cat'], 'value': q['att_sub_cat__value'], 'att_per': q['att_per'], 'criteria_per': q['criteria_per'], 'data': list()})

#     q_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="EXTRA ATTENDANCE", att_sub_cat__in=att_type_li).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
#     for q in q_att:
#         q_att2 = AttendanceSettings.objects.filter(course=course, year=year, session=session, att_sub_cat=q['att_sub_cat']).exclude(status='DELETE').values('attendance_category__value', 'attendance_category', 'att_per', 'criteria_per').distinct()

#         extra_attendance_type.append({'sno': q['att_sub_cat'], 'value': q['att_sub_cat__value'], 'att_per': q['att_per'], 'criteria_per': q['criteria_per'], 'data': list(q_att2)})

#     for extra in extra_attendance_type:
#         sub_cat = []
#         att_per = extra['att_per']
#         criteria_per = extra['criteria_per']
#         sub_cat.append(None)
#         if len(extra['data']) > 0:
#             for d in extra['data']:
#                 att_per = d['att_per']
#                 criteria_per = d['criteria_per']
#                 sub_cat.append(d['attendance_category'])

#         q_sub_extra_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, present_status='P', att_type=extra['sno'], att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=att_category_li) | Q(att_category__isnull=True)).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(present_count=Count('uniq_id')).order_by()
#         present_sub_li_extra = [d['att_id__subject_id'] for d in q_sub_extra_att_present]

#         q_sub_extra_att_total = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type=extra['sno'], att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=att_category_li) | Q(att_category__isnull=True)).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(total=Count('uniq_id')).order_by()
#         total_sub_li_extra = [d['att_id__subject_id'] for d in q_sub_extra_att_total]

#         if att_per < 100:
#             att_total['extra'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': 0, 'id': extra['sno']})
#         i = 0
#         for att in att_data:

#             if att_per == 100:
#                 if att['id'] in present_sub_li_extra:
#                     index = present_sub_li_extra.index(att['id'])
#                     stu_extra_att[i]['extra_no_capping'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': q_sub_extra_att_present[index]['present_count'], 'id': extra['sno']})

#                 else:
#                     stu_extra_att[i]['extra_no_capping'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': 0, 'id': extra['sno']})
#             else:
#                 if att['id'] in present_sub_li_extra:
#                     index = present_sub_li_extra.index(att['id'])
#                     stu_extra_att[i]['extra_capping'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': q_sub_extra_att_present[index]['present_count'], 'id': extra['sno']})

#                 else:
#                     stu_extra_att[i]['extra_capping'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': 0, 'id': extra['sno']})

#             # if att['id'] in total_sub_li_extra:
#             #   index = total_sub_li_extra.index(att['id'])
#             #   att['total'] += q_sub_extra_att_total[index]['total']
#             #   att_total['total'] += q_sub_extra_att_total[index]['total']

#             i += 1

#     ####### CALCULATING EXTRA ATTENDANCE #################
#     query_max_extra_capping = StudentAcademicsDropdown.objects.filter(field='MAXIMUM EXTRA ATTENDANCE CAPPING', session=session).exclude(value__isnull=True).exclude(status='DELETE').values('value')
#     max_extra_capping = float(query_max_extra_capping[0]['value'])

#     i = 0
#     sub_extra_no_capping_total = 0

#     for att in att_data:

#         sub_extra_no_capping = 0
#         for extra in stu_extra_att[i]['extra_no_capping']:
#             if att['total'] > 0:
#                 if (round((att_total['present_count'] * 100.0) / (att_total['total'] * 1.0)) >= extra['criteria_per']):
#                     sub_extra_no_capping += extra['count']

#         sub_extra_no_capping_total += sub_extra_no_capping
#         sub_extra_capping = 0
#         j = 0
#         for extra in stu_extra_att[i]['extra_capping']:
#             if att['total'] > 0:
#                 if (round((att_total['present_count'] * 100.0) / (att_total['total'] * 1.0)) >= extra['criteria_per']):
#                     sub_extra_capping += min(extra['count'], round((att['total'] * extra['att_per']) / 100.0))
#                     att_total['extra'][j]['count'] += extra['count']
#             j += 1

#         att['present_count'] += sub_extra_no_capping
#         att['present_count'] += min(sub_extra_capping, round((att['total'] * max_extra_capping) / 100.0))

#         att['present_count'] = min(att['present_count'], att['total'])
#         att['absent_count'] = att['total'] - att['present_count']
#         i += 1

#     if len(q_sub) == 1:
#         branch_change = {'present': 0, 'absent': 0, 'total': 0}
#     att_data.append({'present_count': branch_change['present'], 'absent_count': branch_change['absent'], 'total': branch_change['total'], 'sub_num_code': '----', 'sub_alpha_code': '----', 'sub_name': 'EXTRA ATTENDANCE CORRESPONDING TO BRANCH CHANGE', 'subject_type': '----', 'subject_unit': '----', 'max_ct_marks': '----', 'max_ta_marks': '----', 'max_att_marks': '----', 'max_university_marks': '----', 'added_by': '----', 'time_stamp': '----', 'status': '----', 'session': '----', 'sem': '----', 'id': '----', 'no_of_units': '----', 'subject_unit__value': '----', 'subject_type__value': '----', 'added_by__name': '----'})
#     att_total['total'] += branch_change['total']
#     att_total['present_count'] += branch_change['present']

#     sub_extra_capping = 0
#     for extra in att_total['extra']:
#         if att_total['total'] > 0:
#             if (round((att_total['present_count'] * 100.0) / (att_total['total'] * 1.0)) >= extra['criteria_per']):
#                 sub_extra_capping += min(extra['count'], round((att_total['total'] * extra['att_per']) / 100.0))

#     att_total['present_count'] += min(sub_extra_capping, round((att_total['total'] * max_extra_capping) / 100.0))
#     att_total['present_count'] += sub_extra_no_capping_total
#     att_total['absent_count'] = att_total['total'] - att_total['present_count']

#     data = {}
#     data['present_count'] = int(att_total['present_count'])
#     data['absent_count'] = int(att_total['absent_count'])
#     data['total'] = int(att_total['total'])
#     data['extra_data'] = att_total['extra']
#     data['extra_count'] = branch_change['present'] + min(sub_extra_capping, round((att_total['total'] * max_extra_capping) / 100.0)) + sub_extra_no_capping_total
#     data['sub_data'] = att_data
#     data['att_type_color'] = get_color()

#     return data


def get_student_attendance(uniq_id, from_date, to_date, session, att_type_li, q_sub, flg_branch_change, att_category_li, session_name):
	att_data = []
	stu_extra_att = []
	class_attendance_type = []

	studentSession = generate_session_table_name("studentSession_", session_name)
	StudentBranchChange = generate_session_table_name("StudentBranchChange_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

	q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
	####CHANGE BY VRINDA (TO AVOID SEM ID NONE)####
	# q_stu_details = studentSession.objects.filter(uniq_id=uniq_id,registration_status=1).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
	###############################################

	if len(att_category_li) == 0:
		att_category_li = list(AttendanceSettings.objects.filter(course=q_stu_details[0]['uniq_id__dept_detail__course'], session=session, year=q_stu_details[0]['year'], admission_type=q_stu_details[0]['uniq_id__admission_type'], att_sub_cat__in=att_type_li).exclude(status='DELETE').values_list('attendance_category', flat=True).order_by().distinct())

	################### BRANCH CHANGE ATTENDANCE ##########################

	branch_change = {'present': 0, 'absent': 0, 'total': 0}

	if flg_branch_change == 1:
		q_check = StudentBranchChange.objects.filter(uniq_id=uniq_id, change_type='S').exclude(old_section__isnull=True).values('old_section__sem_id', 'date')
		for qc in q_check:
			q_sub2 = SubjectInfo.objects.filter(sem=qc['old_section__sem_id']).exclude(status="DELETE").values('id').order_by('id')

			branch_change_data = get_student_attendance(uniq_id, from_date, qc['date'], session, att_type_li, list(q_sub2), 0, att_category_li, session_name)
			from_date = qc['date']

			branch_change['present'] += branch_change_data['present_count']
			branch_change['absent'] += branch_change_data['absent_count']
			branch_change['total'] += branch_change_data['total']

	################### BRANCH CHANGE ATTENDANCE END ##########################
	sub_id = []
	for d in q_sub:
		if d['id'] != '----':
			sub_id.append(d['id'])
	att_data = q_sub

	q_stu_group = StuGroupAssign.objects.filter(uniq_id=uniq_id).values_list('group_id', flat=True)
	qry = StudentAcademicsDropdown.objects.filter(field="ATTENDANCE TYPE", value__in=["NORMAL ATTENDANCE", 'REMEDIAL ATTENDANCE', 'TUTORIAL ATTENDANCE'], session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	# qry=StudentAcademicsDropdown.objects.filter(field="ATTENDANCE TYPE",value__in=["NORMAL ATTENDANCE",'REMEDIAL ATTENDANCE','TUTORIAL ATTENDANCE','DAY-WISE ATTENDANCE'],session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
	for q in qry:
		qr = StudentAcademicsDropdown.objects.filter(pid=q['sno'], sno__in=att_type_li, session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
		for q2 in qr:
			class_attendance_type.append(q2['sno'])
	q_sub_normal_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, present_status='P', att_type__in=class_attendance_type, att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=att_category_li) | Q(att_category__isnull=True)).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(present_count=Count('uniq_id')).order_by()

	present_sub_li = [d['att_id__subject_id'] for d in q_sub_normal_att_present]
	q_sub_improvement_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, present_status='P', att_type__field__contains="IMPROVEMENT", att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_type__in=att_type_li) | Q(att_type__isnull=True)).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(present_count=Count('uniq_id')).order_by()

	improvement_sub_li = [d['att_id__subject_id'] for d in q_sub_improvement_att_present]

	q_sub_normal_att_total = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(att_type__field__contains="IMPROVEMENT").exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(total=Count('uniq_id')).order_by()

	total_sub_li = [d['att_id__subject_id'] for d in q_sub_normal_att_total]

	att_total = {}
	att_total['present_count'] = 0
	att_total['total'] = 0
	att_total['absent_count'] = 0
	att_total['extra'] = []

	for att in att_data:
		stu_extra_att.append({'sub_id': att['id'], 'extra_capping': [], 'extra_no_capping': []})

		if att['id'] in present_sub_li:
			index = present_sub_li.index(att['id'])
			att['present_count'] = q_sub_normal_att_present[index]['present_count']
		else:
			att['present_count'] = 0

		if att['id'] in improvement_sub_li:
			index = improvement_sub_li.index(att['id'])
			att['present_count'] += q_sub_improvement_att_present[index]['present_count']

		if att['id'] in total_sub_li:
			index = total_sub_li.index(att['id'])
			att['total'] = q_sub_normal_att_total[index]['total']
		else:
			att['total'] = 0

		att['absent_count'] = max(0, att['total'] - att['present_count'])
		att_total['present_count'] += att['present_count']
		att_total['total'] += att['total']
	######################### NORMAL ATTENDANCE CALCULATION END ############################################

	######################### EXTRA ATTENDANCE CALCULATION ############################################

	extra_attendance_type = []

	q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')

	### CHENGE BY VRINDA ###
	# year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
	year = (q_stu_details[0]['year'])
	course = None
	if len(q_year) > 0:
		course = q_year[0]['dept__course']
	# CHENGE END...

	query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=att_type_li).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
	for q in query_att:
		extra_attendance_type.append({'sno': q['att_sub_cat'], 'value': q['att_sub_cat__value'], 'att_per': q['att_per'], 'criteria_per': q['criteria_per'], 'data': list()})

	q_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="EXTRA ATTENDANCE", att_sub_cat__in=att_type_li).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
	for q in q_att:
		q_att2 = AttendanceSettings.objects.filter(course=course, year=year, session=session, att_sub_cat=q['att_sub_cat']).exclude(status='DELETE').values('attendance_category__value', 'attendance_category', 'att_per', 'criteria_per').distinct()

		extra_attendance_type.append({'sno': q['att_sub_cat'], 'value': q['att_sub_cat__value'], 'att_per': q['att_per'], 'criteria_per': q['criteria_per'], 'data': list(q_att2)})

	for extra in extra_attendance_type:
		sub_cat = []
		att_per = extra['att_per']
		criteria_per = extra['criteria_per']
		sub_cat.append(None)
		if len(extra['data']) > 0:
			for d in extra['data']:
				att_per = d['att_per']
				criteria_per = d['criteria_per']
				sub_cat.append(d['attendance_category'])

		q_sub_extra_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, present_status='P', att_type=extra['sno'], att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=att_category_li) | Q(att_category__isnull=True)).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(present_count=Count('uniq_id')).order_by()
		present_sub_li_extra = [d['att_id__subject_id'] for d in q_sub_extra_att_present]

		q_sub_extra_att_total = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type=extra['sno'], att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=att_category_li) | Q(att_category__isnull=True)).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(total=Count('uniq_id')).order_by()
		total_sub_li_extra = [d['att_id__subject_id'] for d in q_sub_extra_att_total]

		if att_per < 100:
			att_total['extra'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': 0, 'id': extra['sno']})
		i = 0
		for att in att_data:

			if att_per == 100:
				if att['id'] in present_sub_li_extra:
					index = present_sub_li_extra.index(att['id'])
					stu_extra_att[i]['extra_no_capping'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': q_sub_extra_att_present[index]['present_count'], 'id': extra['sno']})

				else:
					stu_extra_att[i]['extra_no_capping'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': 0, 'id': extra['sno']})
			else:
				if att['id'] in present_sub_li_extra:
					index = present_sub_li_extra.index(att['id'])
					stu_extra_att[i]['extra_capping'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': q_sub_extra_att_present[index]['present_count'], 'id': extra['sno']})

				else:
					stu_extra_att[i]['extra_capping'].append({'att_per': att_per, 'criteria_per': criteria_per, 'count': 0, 'id': extra['sno']})

			# if att['id'] in total_sub_li_extra:
			#   index = total_sub_li_extra.index(att['id'])
			#   att['total'] += q_sub_extra_att_total[index]['total']
			#   att_total['total'] += q_sub_extra_att_total[index]['total']

			i += 1

	####### CALCULATING EXTRA ATTENDANCE #################
	query_max_extra_capping = StudentAcademicsDropdown.objects.filter(field='MAXIMUM EXTRA ATTENDANCE CAPPING', session=session).exclude(value__isnull=True).exclude(status='DELETE').values('value')
	max_extra_capping = 0.0
	if len(query_max_extra_capping)>0:
		max_extra_capping = float(query_max_extra_capping[0]['value'])

	i = 0
	sub_extra_no_capping_total = 0

	for att in att_data:

		sub_extra_no_capping = 0
		for extra in stu_extra_att[i]['extra_no_capping']:
			if att['total'] > 0:
				if (round((att_total['present_count'] * 100.0) / (att_total['total'] * 1.0)) >= extra['criteria_per']):
					sub_extra_no_capping += extra['count']

		sub_extra_no_capping_total += sub_extra_no_capping
		sub_extra_capping = 0
		j = 0
		for extra in stu_extra_att[i]['extra_capping']:
			if att['total'] > 0:
				if (round((att_total['present_count'] * 100.0) / (att_total['total'] * 1.0)) >= extra['criteria_per']):
					sub_extra_capping += min(extra['count'], round((att['total'] * extra['att_per']) / 100.0))
					att_total['extra'][j]['count'] += extra['count']
			j += 1

		att['present_count'] += sub_extra_no_capping
		att['present_count'] += min(sub_extra_capping, round((att['total'] * max_extra_capping) / 100.0))
		att['present_count'] = att['present_count']
		att['absent_count'] = max(0,att['total'] - att['present_count'])
		i += 1

	if len(q_sub) == 1:
		branch_change = {'present': 0, 'absent': 0, 'total': 0}
	att_data.append({'present_count': branch_change['present'], 'absent_count': branch_change['absent'], 'total': branch_change['total'], 'sub_num_code': '----', 'sub_alpha_code': '----', 'sub_name': 'EXTRA ATTENDANCE CORRESPONDING TO BRANCH CHANGE', 'subject_type': '----', 'subject_unit': '----', 'max_ct_marks': '----', 'max_ta_marks': '----', 'max_att_marks': '----', 'max_university_marks': '----', 'added_by': '----', 'time_stamp': '----', 'status': '----', 'session': '----', 'sem': '----', 'id': '----', 'no_of_units': '----', 'subject_unit__value': '----', 'subject_type__value': '----', 'added_by__name': '----'})
	att_total['total'] += branch_change['total']
	att_total['present_count'] += branch_change['present']

	sub_extra_capping = 0
	for extra in att_total['extra']:
		if att_total['total'] > 0:
			if (round((att_total['present_count'] * 100.0) / (att_total['total'] * 1.0)) >= extra['criteria_per']):
				sub_extra_capping += min(extra['count'], round((att_total['total'] * extra['att_per']) / 100.0))

	att_total['present_count'] += min(sub_extra_capping, round((att_total['total'] * max_extra_capping) / 100.0))
	att_total['present_count'] += sub_extra_no_capping_total
	att_total['absent_count'] = att_total['total'] - att_total['present_count']

	data = {}
	data['present_count'] = int(att_total['present_count'])
	data['absent_count'] = max(0, int(att_total['absent_count']))
	data['total'] = int(att_total['total'])
	data['extra_data'] = att_total['extra']
	data['extra_count'] = branch_change['present'] + min(sub_extra_capping, round((att_total['total'] * max_extra_capping) / 100.0)) + sub_extra_no_capping_total
	data['sub_data'] = att_data
	data['att_type_color'] = get_color()
	return data


def get_student_subject_att_status(uniq_id, subject_id, from_date, to_date, att_type_li, session_name):
	StudentBranchChange = generate_session_table_name("StudentBranchChange_", session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
	StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)

	q_check = StudentBranchChange.objects.filter(uniq_id=uniq_id, change_type='S').exclude(old_section__isnull=True).values('old_section__sem_id', 'date').order_by('-id')[:1]
	if len(q_check) > 0:
		from_date = max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_check[0]['date']), "%Y-%m-%d").date())
	q_stu_group = StuGroupAssign.objects.filter(uniq_id=uniq_id).values_list('group_id', flat=True)

	q_sub_normal_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_id__subject_id=subject_id, att_id__date__range=[from_date, to_date], approval_status__contains='APPROVED').filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('present_status', 'att_id__date', 'att_id__lecture', 'att_type__value', 'att_id__group_id', 'att_id__subject_id__sub_name', 'att_id__subject_id', 'att_type', 'marked_by', 'marked_by__name', 'att_id__isgroup').order_by('att_id__date', 'att_id__lecture')

	att_type_li = list(map(int, att_type_li))
	for normal in q_sub_normal_att_present:
		if (normal['att_type']) not in att_type_li:
			normal['present_status'] = 'A'

	return list(q_sub_normal_att_present)


######## FOR ATTENDANCE REGISTER ################################################################################

def get_student_subject_att_status_emp_wise(uniq_id, subject_id, from_date, to_date, att_type_li, session_name, emp_id):
	StudentBranchChange = generate_session_table_name("StudentBranchChange_", session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
	StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)

	q_check = StudentBranchChange.objects.filter(uniq_id=uniq_id, change_type='S').exclude(old_section__isnull=True).values('old_section__sem_id', 'date').order_by('-id')[:1]
	if len(q_check) > 0:
		from_date = max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_check[0]['date']), "%Y-%m-%d").date())
	q_stu_group = StuGroupAssign.objects.filter(uniq_id=uniq_id).values_list('group_id', flat=True)

	q_sub_normal_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_id__subject_id=subject_id, att_id__date__range=[from_date, to_date], att_type__in=att_type_li, approval_status__contains='APPROVED', att_id__emp_id=emp_id).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('present_status', 'att_id__date', 'att_id__lecture', 'att_type__value', 'att_type', 'att_id__group_id', 'att_id').order_by('att_id__date', 'att_id__lecture', 'att_id')
	return list(q_sub_normal_att_present)


def get_student_subject_att_status_wise(uniq_id, subject_id, from_date, to_date, att_type_li, session_name, emp_id):
	StudentBranchChange = generate_session_table_name("StudentBranchChange_", session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
	StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	sub_type = list(SubjectInfo.objects.filter(id=subject_id).values('subject_type__value'))
	q_check = StudentBranchChange.objects.filter(uniq_id=uniq_id, change_type='S').exclude(old_section__isnull=True).values('old_section__sem_id', 'date').order_by('-id')[:1]
	if len(q_check) > 0:
		from_date = max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_check[0]['date']), "%Y-%m-%d").date())
	q_stu_group = StuGroupAssign.objects.filter(uniq_id=uniq_id).values_list('group_id', flat=True)
	if sub_type[0]['subject_type__value'] == 'LAB':
		q_sub_normal_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_id__subject_id=subject_id, att_id__date__range=[from_date, to_date], att_type__in=att_type_li, approval_status__contains='APPROVED', att_id__emp_id=emp_id).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('present_status', 'att_id__date', 'att_id__lecture', 'att_type__value', 'att_type', 'att_id__group_id', 'att_id').order_by('att_id__date', 'att_id__lecture', 'att_id')
	else:
		q_sub_normal_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_id__subject_id=subject_id, att_id__date__range=[from_date, to_date], att_type__in=att_type_li, approval_status__contains='APPROVED').filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('present_status', 'att_id__date', 'att_id__lecture', 'att_type__value', 'att_type', 'att_id__group_id', 'att_id').order_by('att_id__date', 'att_id__lecture', 'att_id')

	return list(q_sub_normal_att_present)


def get_attendance(sub_id, section, emp_id, session_name, isgroup, group_id):

	data = []
	i = 0
	EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
	Attendance = generate_session_table_name("Attendance_", session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

	if isgroup == 'N':
		section_li = [section]
	else:
		section_li = get_group_sections(group_id, session_name)

	q_att = Attendance.objects.filter(section__in=section_li, subject_id=sub_id, isgroup=isgroup, group_id=group_id).filter(~Q(status__contains="DELETE")).values('date', 'lecture', 'section', 'section__section', 'section__sem_id', 'section__sem_id__sem', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'emp_id', 'emp_id__name', 'isgroup', 'group_id', 'group_id__group_name', 'group_id__group_type', 'id', 'normal_remedial').order_by('-date', 'lecture')

	for att in q_att:
		att['date'] = att['date'].strftime('%Y-%m-%d')
		if isgroup == 'N':

			total_students = (StudentAttStatus.objects.filter(att_id=att['id'], approval_status__in=['APPROVED', 'PENDING']).exclude(status__contains="DELETE").values_list('uniq_id', flat=True))

			student_data = get_students_data_from_uniq_id(total_students, session_name)

			present = StudentAttStatus.objects.filter(att_id=att['id'], present_status="P", approval_status__in=['APPROVED', 'PENDING']).exclude(status__contains="DELETE").values_list('uniq_id', flat=True)

			absent = StudentAttStatus.objects.filter(att_id=att['id'], present_status="A", approval_status__in=['APPROVED', 'PENDING']).exclude(status__contains="DELETE").values_list('uniq_id', flat=True)

			pre_cnt = 0
			total = len(student_data)
			pre_cnt = len(present)
			for s in student_data:
				s['section'] = att['section']
				s['section__section'] = att['section__section']
				s['section__sem_id'] = att['section__sem_id']
				s['section__sem_id__sem'] = att['section__sem_id__sem']

				if s['uniq_id'] in present:
					s['checked'] = True
				elif s['uniq_id'] in absent:
					s['checked'] = False

			student_list = []
			student_list.append(student_data)

		else:
			student_list = []

			total_students = (StudentAttStatus.objects.filter(att_id=att['id'], approval_status__in=['APPROVED', 'PENDING']).exclude(status__contains="DELETE").values_list('uniq_id', flat=True))

			student_data = get_students_data_from_uniq_id(total_students, session_name)

			present = StudentAttStatus.objects.filter(att_id=att['id'], present_status="P", approval_status__in=['APPROVED', 'PENDING']).exclude(status__contains="DELETE").values_list('uniq_id', flat=True)

			absent = StudentAttStatus.objects.filter(att_id=att['id'], present_status="A", approval_status__in=['APPROVED', 'PENDING']).exclude(status__contains="DELETE").values_list('uniq_id', flat=True)
			pre_cnt = 0

			total = len(student_data)
			pre_cnt = len(present)

			for s in student_data:
				if s['uniq_id'] in present:
					s['checked'] = True
				elif s['uniq_id'] in absent:
					s['checked'] = False
			student_list.append(student_data)

		data.append(att)
		data[i]['student_status'] = list(student_list)
		data[i]['present_count'] = pre_cnt

		if att['normal_remedial'] == 'N':  # not remedial
			## START ::static changes for IMPROVEMENT ATTENDANCE  by Ritika
			att_type_val=list(StudentAttStatus.objects.filter(att_id=att['id']).values_list('att_type__value',flat=True).distinct())
			att['normal_remedial'] = att_type_val[0]
			## END
			data[i]['absent_count'] = total - pre_cnt
			data[i]['total'] = total
		elif att['normal_remedial'] == 'T':
			att['normal_remedial'] = 'TUTORIAL'
			data[i]['absent_count'] = total - pre_cnt
			data[i]['total'] = total
		elif att['normal_remedial'] == 'R':
			att['normal_remedial'] = 'REMEDIAL'
			data[i]['absent_count'] = 0
			data[i]['total'] = pre_cnt
		elif att['normal_remedial'] == 'D':
			att['normal_remedial'] = 'DOUBT CLEARING'
			data[i]['absent_count'] = 0
			data[i]['total'] = pre_cnt

		i += 1
	return data


def get_att_category_from_type(att_type_li, session):
	query = AttendanceSettings.objects.filter(session=session, att_sub_cat__in=att_type_li).exclude(status='DELETE').exclude(attendance_category__isnull=True).values('attendance_category', 'attendance_category__value').distinct()
	return list(query)


def get_dept_hod(course, emp_id, session_name):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	query = FacultyTime.objects.filter(emp_id=emp_id, status="INSERT", section__dept__course=course).values('section__dept', 'section__dept__dept__value').order_by('section__dept__dept__value').distinct()
	return list(query)


def get_att_status_students(att_id, status_li, session_name):
	StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

	q_status = StudentAttStatus.objects.filter(att_id=att_id, present_status__in=status_li).exclude(status__contains='DELETE').values('present_status', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__uniq_id__name', 'uniq_id__class_roll_no', 'uniq_id__section__section', 'uniq_id__section__sem_id__sem').order_by('uniq_id__class_roll_no')
	return list(q_status)


def get_state():
	qry = list(StudentAcademicsDropdown.objects.filter(field='STATE').exclude(value='NULL').values('value'))
	return qry


def getComponents(request):
	data_values = {}
	status = 403
	print(request.META)
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369, 1371, 1368, 337, 1372])
			if check == 200:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				if(request.method == 'GET'):
					status = 200
					if request.GET['request_type'] == 'course':
						query = get_course()

					elif request.GET['request_type'] == 'organization':
						query = get_organization()

					elif request.GET['request_type'] == 'emp_category':
						query = get_emp_category()

					elif request.GET['request_type'] == 'hr_filter_emp':
						query = get_hr_filter_emp(request.GET['category'].split(','), request.GET['dept'].split(','))

					elif request.GET['request_type'] == 'dept':
						query = get_department(request.GET['org'])

					elif request.GET['request_type'] == 'branch':
						query = get_branch(request.GET['course'])

					elif request.GET['request_type'] == 'sem_commencement':
						course = request.GET['course'].split(',')
						data1 = list(SemesterCommencement.objects.filter(session=session, course__in=course).exclude(status='DELETE').values('commencement_date', 'session__sem_end').distinct().order_by('commencement_date'))
						sem_end = list(Semtiming.objects.filter(uid=session).values_list('sem_end', flat=True))[0]
						if not data1:
							query = {'commencement_date': datetime.today(), 'session__sem_end': sem_end}
						else:
							com = data1[0]['commencement_date']
							end = data1[0]['session__sem_end']
							query = {'commencement_date': com, 'session__sem_end': end}

					elif request.GET['request_type'] == 'StudentWiseAttReport':
						query = get_section_students(request.GET['section'].split(','), {}, session_name)

					elif request.GET['request_type'] == 'extra_att_students':
						stu_list = get_section_students(request.GET['section'].split(','), {}, session_name)
						from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
						to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
						lectures = request.GET['lecture'].split(',')

					elif request.GET['request_type'] == 'get_academic_dept':
						query = get_academic_dept()

					elif request.GET['request_type'] == 'get_academic_faculty':
						query = get_academic_faculty(session_name)

					elif request.GET['request_type'] == 'att_section_students':
						query = get_section_students(request.GET['section'].split(','), {}, session_name)

					elif request.GET['request_type'] == 'att_section_students_multi':
						section_ids = list(Sections.objects.filter(dept__in=request.GET['branch'].split(','), section__in=request.GET['section'].split(','), sem_id__sem__in=request.GET['sem'].split(',')).values_list('section_id', flat=True))
						query = get_section_students(section_ids, {}, session_name)

					elif request.GET['request_type'] == 'att_group_students':
						query = get_att_group_students(request.GET['group_id'], session_name)

					elif request.GET['request_type'] == 'section_students':
						query = get_section_students(request.GET['section'].split(','), {}, session_name)

					elif request.GET['request_type'] == 'group_nominal_list':
						query = get_att_group_students_nominal(request.GET['group_id'], session_name)

					elif request.GET['request_type'] == 'get_all_sem':
						query = {'sems': get_all_sem(sem_type)}

					elif request.GET['request_type'] == 'StudentRegistration':
						query = get_section_registration_students(request.GET['section'].split(','), {}, session_name)
					elif request.GET['request_type'] == '#printDeclarationpdf':
						query = Declarationpdf(request.GET['uniq_id'], request.session['Session_name'])
					elif request.GET['request_type'] == 'group_eligible_students':
						query = get_section_students(get_group_sections(request.GET['group_id'], session_name), {}, session_name)

					elif request.GET['request_type'] == 'intrasection_group':
						data = request.GET
						if 'type_of_group' in data:
							type_of_group = request.GET['type_of_group']
						else:
							type_of_group = 'ACADEMICS'
						query = get_intrasection_group(request.GET['section'], session_name, type_of_group)

					elif request.GET['request_type'] == 'intersection_group':
						data = request.GET
						if 'type_of_group' in data:
							type_of_group = request.GET['type_of_group']
						else:
							type_of_group = 'ACADEMICS'
						query = get_intersection_group(request.GET['sem'], session_name, type_of_group)

					elif request.GET['request_type'] == 'emp_intrasection_group':
						if 'emp_id' in request.GET:
							emp_id = request.GET['emp_id']
						else:
							emp_id = request.session['hash1']
						query = get_emp_intrasection_group(emp_id, request.GET['section'], session_name)

					elif request.GET['request_type'] == 'emp_intersection_group':
						if 'emp_id' in request.GET:
							emp_id = request.GET['emp_id']
						else:
							emp_id = request.session['hash1']
						query = get_emp_intersection_group(emp_id, request.GET['sem'], session_name)

					elif request.GET['request_type'] == 'class_coordinator_course':
						query = get_coordinator_course(request.session['hash1'], 'C', session_name)

					elif request.GET['request_type'] == 'extra_coordinator_course':
						query = get_coordinator_course(request.session['hash1'], 'E', session_name)

					elif request.GET['request_type'] == 'coordinator_branch':
						query = get_coordinator_dept(request.session['hash1'], request.GET['coord_type'], request.GET['course'], session_name)

					elif request.GET['request_type'] == 'coordinator_sem':
						query = get_coordinator_sem(request.session['hash1'], request.GET['coord_type'], request.GET['dept'], session_name)

					elif request.GET['request_type'] == 'coordinator_section':
						query = get_coordinator_section(request.session['hash1'], request.GET['coord_type'], request.GET['sem'], session_name)

					elif request.GET['request_type'] == 'coordinator_subject':
						query = get_coordinator_subject(request.session['hash1'], request.GET['coord_type'], request.GET['section'], session_name)
						# #print(query)
					elif request.GET['request_type'] == 'coordinator_section_multi':
						seming = list(map(int, request.GET['sem'].split(',')))
						sem_li = list(StudentSemester.objects.filter(dept=request.GET['dept'], sem__in=seming).distinct().values_list('sem_id', flat=True))
						query = get_coordinator_section_multi(request.session['hash1'], request.GET['coord_type'], sem_li, session_name)

					elif request.GET['request_type'] == 'course_year':
						query = get_course_years(request.GET['course'])

					elif request.GET['request_type'] == 'attendance_type':
						query = get_attendance_type(session)

					elif request.GET['request_type'] == 'subject_type':
						query = get_subject_type()

					elif request.GET['request_type'] == 'att_category_from_type':
						query = get_att_category_from_type(request.GET['att_type'].split(','), session)

					elif request.GET['request_type'] == 'lockable_attendance_type':
						query = get_lockable_attendance_type(session)

					elif request.GET['request_type'] == 'sub_attendance_type':
						query = get_sub_attendance_type(session)

					elif request.GET['request_type'] == 'admission_type':
						query = get_admission_type()

					elif request.GET['request_type'] == 'admission_status':
						query = get_admission_status()

					elif request.GET['request_type'] == 'extra_attendance_type':
						count_type = request.GET['count_type']
						sem = request.GET['sem']

						q_year = StudentSemester.objects.filter(sem_id=sem).values('sem', 'dept__course')
						year = math.ceil(q_year[0]['sem'] / 2.0)
						course = q_year[0]['dept__course']

						if count_type == 'D':
							query = []
							query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE").exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat').distinct()
							for q in query_att:
								query.append({'sno': q['att_sub_cat'], 'value': q['att_sub_cat__value'], 'data': list()})

						elif count_type == 'L':
							query = []
							q_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="EXTRA ATTENDANCE").exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat').distinct()
							for q in q_att:
								q_att2 = AttendanceSettings.objects.filter(course=course, year=year, session=session, att_sub_cat=q['att_sub_cat']).exclude(status='DELETE').values('attendance_category__value', 'attendance_category').distinct()

								query.append({'sno': q['att_sub_cat'], 'value': q['att_sub_cat__value'], 'data': list(q_att2)})

					# elif request.GET['request_type'] == 'lectures_on_date':
					#     date = datetime.strptime(str(request.GET['date']).split('T')[0], "%Y-%m-%d").date()
					#     section = request.GET['section']
					#     query = []
					#     Attendance = generate_session_table_name("Attendance_", session_name)
					#     TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_name)

					#     lec_data = list(Attendance.objects.filter(section=section, date=date).exclude(status='DELETE').values('lecture').distinct().order_by('lecture'))
					#     for lec in lec_data:
					#         q_sub = Attendance.objects.filter(section=section, date=date, lecture=lec['lecture']).exclude(status='DELETE').values('subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code', 'group_id__group_type', 'group_id__group_name', 'emp_id__name')
					#         query.append({'lecture': lec['lecture'], 'lec_data': list(q_sub)})

					elif request.GET['request_type'] == 'lectures_on_date':
						from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
						to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()

						section = request.GET['section']
						query = []
						Attendance = generate_session_table_name("Attendance_", session_name)
						TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_name)

						lec_data = list(Attendance.objects.filter(section=section, date__range=[from_date, to_date]).exclude(status='DELETE').values('lecture').distinct().order_by('lecture'))
						for lec in lec_data:
							q_sub = Attendance.objects.filter(section=section, date__range=[from_date, to_date], lecture=lec['lecture']).exclude(status='DELETE').exclude(subject_id__status="DELETE").values('subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code', 'group_id__group_type', 'group_id__group_name', 'emp_id__name')
							query.append({'lecture': lec['lecture'], 'lec_data': list(q_sub)})

					elif request.GET['request_type'] == 'sem_lecture':
						sem = request.GET['sem']

						query_lec = TimeTableSlots.objects.filter(session=session, sem_id=sem_id).filter(dean_approval_status="APPROVED").exclude(status="DELETE").values('num_lecture_slots').order_by('-num_lecture_slots')[:1]
						if len(query_lec) > 0:
							query = {'lectures': query_lec[0]['num_lecture_slots']}
						else:
							query = {'lectures': 0}

					elif request.GET['request_type'] == 'attendance_category':
						query = get_attendance_category(session)

					elif request.GET['request_type'] == "semester":
						query = get_semester(request.GET['dept'], sem_type)

					elif request.GET['request_type'] == "section":
						query = get_section(request.GET['sem'])

					elif request.GET['request_type'] == "department":
						query = get_dept()

					elif request.GET['request_type'] == "filtered_emp":
						query = get_filtered_emps(request.GET['dept'])

					elif request.GET['request_type'] == "dept_hod":
						query = get_dept_hod(request.GET['course'], request.session['hash1'], session_name)
						# #print(query)

					elif request.GET['request_type'] == "AcadAttendanceRegister_Hod":
						q_dept = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
						query = get_filtered_emps_with_inactive(q_dept[0]['dept'])

					elif request.GET['request_type'] == "AcadAttendanceRegister_Dean":
						query = get_filtered_emps_with_inactive('ALL')

					elif request.GET['request_type'] == "AcadAttendanceRegister_ClassCord":
						query = get_AcadAttendanceRegister_ClassCord(request.session['hash1'], session_name)

					elif request.GET['request_type'] == "AcadAttendanceRegister_ExtraCord":
						query = get_AcadAttendanceRegister_ExtraCord(request.session['hash1'], session_name)

					elif request.GET['request_type'] == "student_subjects":
						query = get_student_subjects(request.GET['sem'], session_name)

					elif request.GET['request_type'] == "student_lab_theory_subjects":
						query = get_student_lab_theory_subjects(request.GET['sem'], request.GET['code'], session_name)

					elif request.GET['request_type'] == 'stu_att':
						from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
						to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
						uniq_id = request.GET['uniq_id']

						att_type = get_sub_attendance_type(session)
						att_type_li = [t['sno'] for t in att_type]
						studentSession = generate_session_table_name("studentSession_", session_name)

						q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
						subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
						query = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type_li, subjects, 1, [], session_name)

					elif request.GET['request_type'] == "filtered_dept":
						q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
						dept = q_dept[0]['dept']
						query = get_filtered_dept(request.GET['course'], dept)
						# #print(query)
					elif request.GET['request_type'] == "filtered_primary_dept":
						q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
						dept = q_dept[0]['dept']
						if dept != 576:
							query=list(CourseDetail.objects.filter(course_id=request.GET['course'],dept=dept).values("dept_id","dept_id__value").distinct())
						else:
							query=list(CourseDetail.objects.filter(course_id=request.GET['course']).exclude(dept=576).values("dept_id","dept_id__value").distinct())
					elif request.GET['request_type'] == "hod_filtered_dept":
						q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
						dept = q_dept[0]['dept']
						query = get_hod_filtered_dept(dept)

					elif request.GET['request_type'] == "sem_filter_subjects":
						query = get_sem_filter_subjects(request.GET['sem'], session_name)

					elif request.GET['request_type'] == "employee_time_table":
						query = get_employee_time_table(request.session['hash1'], session_name)

					elif request.GET['request_type'] == "section_time_table":
						query = get_section_time_table(request.GET['section'], session_name)

					elif request.GET['request_type'] == 'filtered_sem':
						q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
						dept = q_dept[0]['dept']
						query = get_filtered_sem(request.GET['course'], dept, sem_type)

					elif request.GET['request_type'] == 'fac_time_course_perid1':
						query = get_fac_time_course(request.GET['emp_id'], session_name)

					elif request.GET['request_type'] == 'fac_time_course':
						if 'emp_id' not in request.GET:
							query = get_fac_time_course(request.session['hash1'], session_name)
						else:
							query = get_fac_time_course(request.GET['emp_id'], session_name)

					########## all course for which faculty has marked attendance irrespective of time table ############
					elif request.GET['request_type'] == 'fac_all_course':
						if 'emp_id' not in request.GET:
							query = get_fac_all_course(request.session['hash1'], session_name)
						else:
							query = get_fac_all_course(request.GET['emp_id'], session_name)

					elif request.GET['request_type'] == 'fac_time_dept_perid2':
						query = get_fac_time_dept(request.GET['emp_id'], request.GET['course'], session_name)

					elif request.GET['request_type'] == 'fac_time_dept':
						query = get_fac_time_dept(request.session['hash1'], request.GET['course'], session_name)

					########## all branch for which faculty has marked attendance irrespective of time table ############
					elif request.GET['request_type'] == 'fac_all_dept':
						if 'emp_id' not in request.GET:
							query = get_fac_all_dept(request.session['hash1'], request.GET['course'], session_name)
						else:
							query = get_fac_all_dept(request.GET['emp_id'], request.GET['course'], session_name)

					elif request.GET['request_type'] == 'fac_time_sem_perid3':
						query = get_fac_time_sem(request.GET['emp_id'], request.GET['dept'], session_name)

					elif request.GET['request_type'] == 'fac_time_sem':
						# #print(request.GET['dept'])
						query = get_fac_time_sem(request.session['hash1'], request.GET['dept'], session_name)

					########## all branch for which faculty has marked attendance irrespective of time table ############
					elif request.GET['request_type'] == 'fac_all_sem':
						if 'emp_id' not in request.GET:
							query = get_fac_all_sem(request.session['hash1'], request.GET['dept'], session_name)
						else:
							query = get_fac_all_sem(request.GET['emp_id'], request.GET['dept'], session_name)

					elif request.GET['request_type'] == 'fac_time_sem_multi':
						query = get_fac_time_sem_multi(request.session['hash1'], request.GET['dept'].split(','), session_name)

					elif request.GET['request_type'] == 'dept_multi':
						course = request.GET['course'].split(',')
						# #print(course)
						data = []
						qry = CourseDetail.objects.filter(course_id__in=course).values("uid", "dept__value", "course_id", "course_id__value")
						query = list(qry)

					elif request.GET['request_type'] == 'semester_multi':
						if sem_type == "odd":
							sem = StudentSemester.objects.filter(dept__in=request.GET["branch"].split(',')).annotate(odd=F('sem') % 2).filter(odd=True).values_list('sem', flat=True)
						elif sem_type == "even":
							sem = StudentSemester.objects.filter(dept__in=request.GET["branch"].split(',')).annotate(odd=F('sem') % 2).filter(odd=False).values_list('sem', flat=True)
						query = sorted(list(set(sem)))

					elif request.GET['request_type'] == 'fac_time_section_perid4':
						query = get_fac_time_section(request.GET['emp_id'], request.GET['sem'], session_name)

					elif request.GET['request_type'] == 'fac_time_section':
						query = get_fac_time_section(request.session['hash1'], request.GET['sem'], session_name)

					########## all section for which faculty has marked attendance irrespective of time table ############
					elif request.GET['request_type'] == 'fac_all_section':
						if 'emp_id' not in request.GET:
							query = get_fac_all_section(request.session['hash1'], request.GET['sem'], session_name)
						else:
							query = get_fac_all_section(request.GET['emp_id'], request.GET['sem'], session_name)

					elif request.GET['request_type'] == 'get_sem_by_course':
						query = set(StudentSemester.objects.filter(dept__course=request.GET['course']).values_list('sem', flat=True))
						query = list(query)

					# elif request.GET['request_type'] == 'get_section_multi':
					#   #print(request.GET)
					#   temp=Sections.objects.filter(sem_id__sem__in=map(int,request.GET['sem'].split(',')[:-1]),dept__in=map(int,request.GET['branch'].split(',')[:-1])).values_list('section',flat=True)
					#   #print(temp,temp.query)
					#   query=list(set(temp))

					elif request.GET['request_type'] == 'fac_get_section_multi':
						sems = StudentSemester.objects.filter(sem__in=request.GET['sem'].split(','), dept__in=request.GET['branch'].split(',')).values_list('sem_id', flat=True)
						temp = get_fac_time_section_multi(request.session['hash1'], sems, session_name)
						array = []
						for x in temp:
							array.append(x['section__section'])
						query = list(set(array))
						query.sort()

					elif request.GET['request_type'] == 'fac_time_subject_perid5':
						query = get_fac_time_subject(request.GET['emp_id'], request.GET['section'].split(','), session_name)

					elif request.GET['request_type'] == 'fac_time_subject':
						query = get_fac_time_subject(request.session['hash1'], request.GET['section'].split(','), session_name)

					elif request.GET['request_type'] == 'fac_time_subject_type_subject':
						query = get_fac_time_subject_type_subject(request.session['hash1'], request.GET['section'].split(','), session_name, request.GET['sub_type'])

					########## all subject for which faculty has marked rattendance irrespective of time table ############
					elif request.GET['request_type'] == 'fac_all_subject':
						if 'emp_id' not in request.GET:
							query = get_fac_all_subject(request.session['hash1'], request.GET['section'].split(','), session_name)
						else:
							query = get_fac_all_subject(request.GET['emp_id'], request.GET['section'].split(','), session_name)

					elif request.GET['request_type'] == 'fac_time_subject_new':
						query = get_fac_time_subject_new(request.session['hash1'], request.GET['section'].split(','), session_name, request.GET['sub_type'].split(','))

					elif request.GET['request_type'] == 'fac_time_group_subject_new':
						query = get_fac_time_subject_new(request.session['hash1'], get_group_sections(request.GET['group_id'], session_name), session_name, request.GET['sub_type'].split(','))

					elif request.GET['request_type'] == 'fac_time_subject_multi':

						sections = Sections.objects.filter(sem_id__sem__in=request.GET['sem'].split(','), sem_id__dept__in=request.GET['branch'].split(',')).values_list('section_id', flat=True)
						query = get_fac_time_subject_type_filter(request.session['hash1'], sections, request.GET['sub_type'].split(','), session_name)

					elif request.GET['request_type'] == 'fac_time_group_subject':
						if 'emp_id' in request.GET:
							emp_id = request.GET['emp_id']
						else:
							emp_id = request.session['hash1']
						query = get_fac_time_subject(emp_id, get_group_sections(request.GET['group_id'], session_name), session_name)

					elif request.GET['request_type'] == 'fac_time_group_subject_type_subject':
						query = get_fac_time_group_subject_type_subject(request.session['hash1'], get_group_sections(request.GET['group_id'], session_name), session_name, request.GET['sub_type'])

					elif request.GET['request_type'] == 'fac_time_faculty':
						query = get_fac_time_faculty(request.GET['section'], session_name)

					elif request.GET['request_type'] == 'fac_app_profile':
						query = get_fac_app_profile(request.session['hash1'])

					elif request.GET['request_type'] == 'fac_app_profile':
						query = get_fac_app_profile(request.session['hash1'])

					elif request.GET['request_type'] == 'get_attendance':
						if 'isgroup' in request.GET:

							if request.GET['isgroup'] == 'N':
								group_id = None
								section = request.GET['section']
							else:
								section = None
								group_id = request.GET['group_id']
							query = get_attendance(request.GET['sub_id'], section, session, session_name, request.GET['isgroup'], group_id)
						else:
							group_id = None
							group = 'N'
							query = get_attendance(request.GET['sub_id'], request.GET['section'], request.session['hash1'], session_name, group, group_id)

					elif request.GET['request_type'] == 'att_status_students':
						query = get_att_status_students(request.GET['att_id'], request.GET['status'].split(','), session_name)

					elif request.GET['request_type'] == 'get_sem_by_course':
						query = set(StudentSemester.objects.filter(dept__course=request.GET['course']).values_list('sem', flat=True))
						query = list(query)
					elif request.GET['request_type'] == 'get_section_multi':
						temp = Sections.objects.filter(sem_id__sem__in=map(int, request.GET['sem'].split(',')), dept__in=map(int, request.GET['branch'].split(','))).values_list('section', flat=True)
						query = sorted(list(set(temp)))

					elif request.GET['request_type'] == 'get_emp_filtered_dept':
						Attendance = generate_session_table_name("Attendance_", session_name)

						temp = Attendance.objects.filter(emp_id=request.session['hash1']).values_list('section', flat=True)
						query = list(set(temp))

					elif request.GET['request_type'] == 'get_sec_fac':
						section = Sections.objects.filter(sem_id__sem__in=request.GET['sem'].split(','), section__in=request.GET['section'].split(','), dept__in=request.GET['branch'].split(',')).values_list('section_id', flat=True)

						FacultyTime = generate_session_table_name("FacultyTime_", session_name)

						qry_fac_emp = FacultyTime.objects.filter(session=session, section__in=section).exclude(status='DELETE').values('subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value').distinct()

						for f in qry_fac_emp:
							f['info'] = f['emp_id__name'] + ' -' + str(f['emp_id']) + ' (' + f['subject_id__sub_name'] + ')'
						query = list(qry_fac_emp)

					elif request.GET['request_type'] == 'get_section_faculty':
						section = Sections.objects.filter(sem_id__sem__in=request.GET['sem'].split(','), section__in=request.GET['section'].split(','), dept__in=request.GET['branch'].split(',')).values_list('section_id', flat=True)

						FacultyTime = generate_session_table_name("FacultyTime_", session_name)

						qry_fac_emp = FacultyTime.objects.filter(session=session, section__in=section).exclude(status='DELETE').values('emp_id', 'emp_id__name').distinct()

						for f in qry_fac_emp:
							f['info'] = f['emp_id__name'] + ' (' + str(f['emp_id']) + ') '
						query = list(qry_fac_emp)

					elif request.GET['request_type'] == 'get_subjects_multi':
						SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

						temp = list(SubjectInfo.objects.filter(sem__sem__in=map(int, request.GET['sem'].split(',')[:-1]), sem__dept__in=map(int, request.GET['branch'].split(',')[:-1]), subject_type__in=map(int, request.GET['subject_type'].split(',')[:-1])).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'id', 'sem__sem', 'sem__dept__dept__value'))
						for x in temp:

							try:
								x['info'] = '(' + str(x['sem__dept__dept__value']) + "-" + str(x['sem__sem']) + ') ' + str(x['sub_name']) + ' ( ' + str(x['sub_alpha_code']) + str(x['sub_num_code']) + ' )'
							except:
								x['info'] = x['sub_name']
						query = list(temp)

					elif request.GET['request_type'] == 'get_subjects_multi_all_type':
						SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

						temp = list(SubjectInfo.objects.filter(sem__sem__in=map(int, request.GET['sem'].split(',')[:-1]), sem__dept__in=map(int, request.GET['branch'].split(',')[:-1])).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'id', 'sem__sem', 'sem__dept__dept__value'))
						for x in temp:
							try:
								x['info'] = '(' + str(x['sem__dept__dept__value']) + "-" + str(x['sem__sem']) + ') ' + str(x['sub_name']) + ' ( ' + str(x['sub_alpha_code']) + str(x['sub_num_code']) + ' ) '
							except:
								x['info'] = x['sub_name']
						query = list(temp)

					elif request.GET['request_type'] == 'get_subjects_multi_all':
						SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
						# #print(request.GET['sem'])
						# #print(request.GET['branch'])

						temp = list(SubjectInfo.objects.filter(sem__sem_id=request.GET['sem'], sem__dept=request.GET['branch']).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'id', 'sem__sem', 'sem__dept__dept__value'))
						for x in temp:
							try:
								x['info'] = '(' + str(x['sem__dept__dept__value']) + "-" + str(x['sem__sem']) + ') ' + str(x['sub_name']) + ' ( ' + str(x['sub_alpha_code']) + str(x['sub_num_code']) + ' ) '
							except:
								x['info'] = x['sub_name']
						query = list(temp)

					elif request.GET['request_type'] == 'get_subjects_multi':
						SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

						temp = list(SubjectInfo.objects.filter(sem__sem__in=map(int, request.GET['sem'].split(',')[:-1]), sem__dept__in=map(int, request.GET['branch'].split(',')[:-1]), subject_type__in=map(int, request.GET['subject_type'].split(',')[:-1])).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'id', 'sem__sem', 'sem__dept__dept__value'))
						for x in temp:

							try:
								x['info'] = '(' + str(x['sem__dept__dept__value']) + "-" + str(x['sem__sem']) + ') ' + str(x['sub_name']) + ' ( ' + str(x['sub_alpha_code']) + str(x['sub_num_code']) + ' )'
							except:
								x['info'] = x['sub_name']
						query = list(temp)

					elif request.GET['request_type'] == 'check_attendance':
						# #print(request)
						lecture = request.GET['lecture'].split(',')
						isgroup = request.GET['isgroup']
						att_cat = request.GET['att_type']
						date = datetime.strptime(str(request.GET['date']).split('T')[0], "%Y-%m-%d").date()
						flag_marked = False
						flag_locked = False
						msg = ""
						if isgroup == 'N':
							section = request.GET['section']
							for lec in lecture:
								check = checkIsAttendanceAlreadyMarked(lec, section, None, date, session_name)
								if check['already_marked']:
									flag_marked = True
									msg = check['msg']
									break

							if not flag_marked:
								q_sec_det = Sections.objects.filter(section_id=section).exclude(status='DELETE').values('sem_id__sem', 'sem_id__dept__course')
								year = math.ceil(q_sec_det[0]['sem_id__sem'] / 2.0)
								if('updated_date' in request.GET):
									if request.GET['updated_date'] is not None:
										# #print(request.GET['updated_date'])
										updated_date = datetime.strptime(str(request.GET['updated_date']).split('T')[0], "%Y-%m-%d").date()
										# #print(q_sec_det[0]['sem_id__dept__course'], request.session['hash1'], date, att_cat, session, year, section, session_name, {'updated_date': updated_date})
										flag_locked = checkIsAttendanceLocked(q_sec_det[0]['sem_id__dept__course'], request.session['hash1'], date, att_cat, session, year, section, session_name, {'updated_date': updated_date})
										# #print(flag_locked)
								else:
									flag_locked = checkIsAttendanceLocked(q_sec_det[0]['sem_id__dept__course'], request.session['hash1'], date, att_cat, session, year, section, session_name, {})

								if flag_locked:
									msg = "Attendance Portal is locked for the date selected"

						else:
							group_id = request.GET['group_id']
							group_section = get_group_sections(group_id, session_name)
							for gs in group_section:
								for lec in lecture:
									check = checkIsAttendanceAlreadyMarked(lec, gs, group_id, date, session_name)
									if check['already_marked']:
										flag_marked = True
										msg = check['msg']
										break

							if not flag_marked:
								for gs in group_section:
									q_sec_det = Sections.objects.filter(section_id=gs).exclude(status='DELETE').values('sem_id__sem', 'sem_id__dept__course')
									year = math.ceil(q_sec_det[0]['sem_id__sem'] / 2.0)
									if('updated_date' in request.GET):
										if request.GET['updated_date'] is not None:
											# #print(request.GET['updated_date'])
											updated_date = datetime.strptime(str(request.GET['updated_date']).split('T')[0], "%Y-%m-%d").date()
											flag_locked = checkIsAttendanceLocked(q_sec_det[0]['sem_id__dept__course'], request.session['hash1'], date, att_cat, session, year, gs, session_name, {'updated_date': updated_date})
									else:
										flag_locked = checkIsAttendanceLocked(q_sec_det[0]['sem_id__dept__course'], request.session['hash1'], date, att_cat, session, year, gs, session_name, {})

									if flag_locked:
										msg = "Attendance Portal is locked for the date selected"
										break

						error = flag_marked or flag_locked
						query = {'error': error, 'msg': msg.upper()}

					elif request.GET['request_type'] == 'filtered_lectures':
						date = datetime.strptime(str(request.GET['date']).split('T')[0], "%Y-%m-%d").date()
						flag_locked = False
						att_cat = request.GET['att_type']
						if request.GET['isgroup'] == 'Y':
							group_id = request.GET['group_id']
							sections = get_group_sections(group_id, session_name)

							for sec in sections:
								q_sec_det = Sections.objects.filter(section_id=sec).exclude(status='DELETE').values('sem_id__sem', 'sem_id__dept__course')
								year = math.ceil(q_sec_det[0]['sem_id__sem'] / 2.0)

								flag_locked = checkIsAttendanceLocked(q_sec_det[0]['sem_id__dept__course'], request.session['hash1'], date, att_cat, session, year, sec, session_name, {})
								if flag_locked:
									break

						else:
							section = request.GET['section']
							q_sec_det = Sections.objects.filter(section_id=section).exclude(status='DELETE').values('sem_id__sem', 'sem_id__dept__course')
							year = math.ceil(q_sec_det[0]['sem_id__sem'] / 2.0)

							flag_locked = checkIsAttendanceLocked(q_sec_det[0]['sem_id__dept__course'], request.session['hash1'], date, att_cat, session, year, section, session_name, {})

							# flag_locked=False
						day = date.weekday()
						sem_id = request.GET['sem_id']
						lectures = get_lectures(sem_id, day, session_name)
						if flag_locked:
							query = {'lectures': 0, 'locked': flag_locked, 'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}
							status = 202
						else:
							query = {'lectures': lectures, 'locked': flag_locked}

					elif request.GET['request_type'] == 'sub_att_data_fac':
						from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
						to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
						uniq_id = request.GET['uniq_id']
						sub_id = request.GET['subject_id']
						att_type_li = request.GET['att_type'].split(',')[:-1]
						studentSession = generate_session_table_name("studentSession_", session_name)

						q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date')
						if '-' in sub_id:
							data_values = {'data': []}
						else:
							query = get_student_subject_att_status(uniq_id, sub_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, att_type_li, session_name)
							data_values = {'data': query}

					elif request.GET['request_type'] == 'sub_att_data':
						from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
						to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
						uniq_id = request.session['uniq_id']
						sub_id = request.GET['subject_id']
						att_type = get_sub_attendance_type(session)
						att_type_li = [t['sno'] for t in att_type]

						q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date')
						if '-' in sub_id:
							data_values = {'data': []}
						else:
							query = get_student_subject_att_status(uniq_id, sub_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, att_type_li, session_name)
							data_values = {'data': query}

					elif request.GET['request_type'] == 'get_state':
						query = get_state()
						data_values = {'data': query}

					elif request.GET['request_type'] == 'get_session':
						query = Semtiming.objects.filter(session_name=session_name).values('uid', 'session', 'sem_type', 'sem_end', 'sem_start', 'session_name')
						query = list(query)

					data_values = {'data': (query)}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=(data_values), status=status, safe=False)


def semester_commencement(request):
	data_values = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371, 1369])
			if check == 200:
				session_id = Semtiming.objects.get(uid=request.session['Session_id'])
				session = request.session['Session']
				session_name = request.session['Session_name']

				added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
				if(request.method == 'GET'):
					if 'request_type' not in request.GET:
						course = get_course()

						status = 200
						data_values = {'course': course, 'session_name': session}
					elif request.GET['request_type'] == 'view_previous':
						query = SemesterCommencement.objects.filter(session=session_id, year__gt=0).exclude(status="DELETE").values('course', 'course__value', 'year', 'added_by', 'added_by__name', 'commencement_date').order_by('year')
						status = 200
						data_values = {'data': list(query)}
				elif request.method == "POST":
					data = json.loads(request.body)

					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_name):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					course = data['course']
					year = list(data['year'])
					# CHANGE BY VRINDA
					# commencement_date = datetime.strptime(str(data['commencement_date']).split('T')[0], "%Y-%m-%d").date() + timedelta(days=1)
					commencement_date = datetime.strptime(str(data['commencement_date']).split('T')[0], "%Y-%m-%d").date()
					###################

					upd_li = []
					for y in year:
						q_check = SemesterCommencement.objects.filter(course=course, session=session_id, year=y).exclude(status="DELETE").values('id')
						if len(q_check) > 0:
							upd_li.append(q_check[0]['id'])

					q_update = SemesterCommencement.objects.filter(id__in=upd_li).update(status='DELETE')

					objs = (SemesterCommencement(course=StudentDropdown.objects.get(sno=course), added_by=added_by, year=y, session=session_id, commencement_date=commencement_date) for y in year)
					q_ins = SemesterCommencement.objects.bulk_create(objs)

					studentSession = generate_session_table_name("studentSession_", session_name)

					for y in year:
						q_update = studentSession.objects.filter(year=y, sem__dept__course=course).update(att_start_date=commencement_date)

					status = 200
					data_values = {'msg': "Date Successfully Inserted"}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def attendance_settings(request):
	data_values = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371])
			if check == 200:
				session = Semtiming.objects.get(uid=request.session['Session_id'])
				session_name = request.session['Session']
				session_db = request.session['Session_name']
				added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						attendance_type = get_sub_attendance_type(session)
						# #print(session)
						course = get_course()
						admission_type = get_admission_type()
						attendance_category = get_attendance_category(session)

						session_name = session_name

						status = 200
						data_values = {'course': course, 'session_name': session_name, 'admission_type': admission_type, 'attendance_type': attendance_type, 'attendance_category': attendance_category}
					elif request.GET['request_type'] == 'view_previous':
						query = AttendanceSettings.objects.filter(session=session).exclude(status="DELETE").values('course', 'course__value', 'year', 'added_by', 'added_by__name', 'att_sub_cat', 'att_sub_cat__value', 'attendance_category', 'attendance_category__value', 'admission_type', 'admission_type__value', 'att_per', 'criteria_per', 'lock_type', 'days_lock', 'att_to_be_approved')
						status = 200
						data_values = {'data': list(query)}
				elif request.method == "POST":
					data = json.loads(request.body)

					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_db):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					course = data['course']
					year = list(data['year'])
					attendance_category = list(data['attendance_category'])
					att_sub_cat = (data['att_sub_cat'])
					admission_type = list(data['admission_type'])
					# attendance_type=data['attendance_type']
					att_per = data['att_per']
					criteria_per = data['criteria_per']
					lock_type = data['lock_type']
					days = data['days']
					if days is None:
						days = 0
					att_approved = data['att_approved']

					upd_li = []

					for y in year:
						for adm_type in admission_type:
							q_check = AttendanceSettings.objects.filter(session=session, year=y).filter(Q(attendance_category__in=attendance_category) | Q(attendance_category__isnull=True)).filter(admission_type=adm_type, att_sub_cat=att_sub_cat, course=course).exclude(status="DELETE").values_list('id', flat=True)
							if len(q_check) > 0:
								upd_li.extend(q_check)
					q_update = AttendanceSettings.objects.filter(id__in=upd_li).update(status="DELETE")

					if None in attendance_category:
						attendance_category = []
					if len(attendance_category) > 0:
						objs = (AttendanceSettings(course=StudentDropdown.objects.get(sno=course), added_by=added_by, year=y, session=session, admission_type=StudentDropdown.objects.get(sno=adm_type), att_sub_cat=StudentAcademicsDropdown.objects.get(sno=att_sub_cat), attendance_category=StudentAcademicsDropdown.objects.get(sno=att_cat), att_per=att_per, criteria_per=criteria_per, lock_type=lock_type, days_lock=days, att_to_be_approved=att_approved) for y in year for att_cat in attendance_category for adm_type in admission_type)
					else:
						objs = (AttendanceSettings(course=StudentDropdown.objects.get(sno=course), added_by=added_by, year=y, session=session, admission_type=StudentDropdown.objects.get(sno=adm_type), att_sub_cat=StudentAcademicsDropdown.objects.get(sno=att_sub_cat), att_per=att_per, criteria_per=criteria_per, lock_type=lock_type, days_lock=days, att_to_be_approved=att_approved) for y in year for adm_type in admission_type)
					q_ins = AttendanceSettings.objects.bulk_create(objs)

					status = 200
					data_values = {'msg': "Data Successfully Inserted"}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def assign_coordinator(request):
	data_values = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369, 1384, 337])
			if check == 200:
				session = Semtiming.objects.get(uid=request.session['Session_id'])
				session_name = request.session['Session']
				session_db = request.session['Session_name']
				sem_type = request.session['sem_type']
				added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						q_dept = EmployeePrimdetail.objects.filter(emp_id=added_by).values('dept')
						dept = q_dept[0]['dept']
						course = get_filtered_course(dept)

						organization = get_organization()
						emp_category = get_emp_category()
						get_emps = EmployeePrimdetail.objects.filter(dept=dept).values('emp_id', 'name', 'desg__value', 'dept__value')

						session_name = session_name

						status = 200
						data_values = {'session_name': session_name, 'course': course, 'coord_type': get_coord_type(), 'organization': organization, 'emp_category': emp_category}
					elif request.GET['request_type'] == 'view_previous':
						q_dept = EmployeePrimdetail.objects.filter(emp_id=added_by).values('dept')
						dept = q_dept[0]['dept']
						AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_db)

						query = AcadCoordinator.objects.filter(session=session, section__sem_id__dept__dept=dept).exclude(status="DELETE").values('id', 'emp_id__emp_status', 'section', 'section__sem_id__sem', 'section__section', 'section__sem_id__dept__dept__value', 'emp_id', 'emp_id__name', 'section__sem_id__dept__course__value', 'coord_type', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id')
						for q in query:
							if q['coord_type'] == 'T':
								q['coord_type'] = 'TIME TABLE COORDINATOR'
							elif q['coord_type'] == 'C':
								q['coord_type'] = 'CLASS COORDINATOR'
							elif q['coord_type'] == 'G':
								q['coord_type'] = 'ASSIGN GROUP COORDINATOR'
							elif q['coord_type'] == 'S':
								q['coord_type'] = 'SUBJECT COORDINATOR'
							elif q['coord_type'] == 'R':
								q['coord_type'] = 'SEMESTER REGISTRATION COORDINATOR'
							elif q['coord_type'] == 'E':
								q['coord_type'] = 'EXTRA ATTENDANCE COORDINATOR'
							elif q['coord_type'] == 'QM':
								q['coord_type'] = 'QUESTION MODERATOR'
							elif q['coord_type'] == 'CO':
								q['coord_type'] = 'CO COORDINATOR'
							elif q['coord_type'] == 'COE':
								q['coord_type'] = 'EXAM COORDINATOR'
							elif q['coord_type'] == 'UVE':
								q['coord_type'] = 'UNIVERSITY MARKS COORDINATOR'
							elif q['coord_type'] == 'NC':
								q['coord_type'] = 'NBA COORDINATOR'
							if q['subject_id'] is None:
								q['subject_id__sub_name'] = "----"

						status = 200
						data_values = {'data': list(query)}

				elif request.method == "POST":
					data = json.loads(request.body)
					AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_db)
					SubjectInfo = generate_session_table_name("SubjectInfo_", session_db)

					sem = list(data['sem'])

					qry_sections = list(Sections.objects.filter(sem_id__in=sem).values_list('section_id', flat=True))

					if check_islocked('HOD', qry_sections, session_db):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					coord_type = list(data['coord_type'])
					section = list(data['section'])
					emp_ids = data['emp_id']
					# #print(emp_ids)
					sub = data['sub']

					query_sec = Sections.objects.filter(sem_id__in=sem, section__in=section).exclude(status='DELETE').values_list('section_id', flat=True)
					section = list(query_sec)

					if len(sub) == 0:

						for coord in coord_type:
							# for sec in section:
							#     q_check_duplicate = AcadCoordinator.objects.filter(coord_type=coord, section=sec).exclude(status='DELETE').values('id')
							#     if len(q_check_duplicate) > 0:
							#         q_delt = AcadCoordinator.objects.filter(id=q_check_duplicate[0]['id']).update(status='DELETE')
							for sec in section:
								q_check_duplicate = list(AcadCoordinator.objects.filter(coord_type=coord, section=sec).exclude(status='DELETE').values('id'))
								id_list = []
								for i in q_check_duplicate:
									id_list.append(i['id'])
								if len(q_check_duplicate) > 0:
									q_delt = AcadCoordinator.objects.filter(id__in=id_list).update(status='DELETE')

						for coord in coord_type:
							for sec in section:
								for emp_id in emp_ids:
									q_ins = AcadCoordinator.objects.create(coord_type=coord, section=Sections.objects.get(section_id=sec), session=session, emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), added_by=added_by)
					else:
						for coord in coord_type:
							for sec in section:
								for s in sub:
									q_check_duplicate = AcadCoordinator.objects.filter(coord_type=coord, section=sec, subject_id=s).exclude(status='DELETE').values('id')
									if len(q_check_duplicate) > 0:
										q_delt = AcadCoordinator.objects.filter(id=q_check_duplicate[0]['id']).update(status='DELETE')

						for coord in coord_type:
							for sec in section:
								for s in sub:
									for emp_id in emp_ids:
										q_ins = AcadCoordinator.objects.create(coord_type=coord, section=Sections.objects.get(section_id=sec), subject_id=SubjectInfo.objects.get(id=s), session=session, emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), added_by=added_by)

					status = 200
					data_values = {'msg': "Coordinator Assigned Successfully"}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def new_tt_slots(request):
	data_values = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'T' in request.session['Coordinator_type']:
				session = Semtiming.objects.get(uid=request.session['Session_id'])
				session_name = request.session['Session']
				session_db = request.session['Session_name']
				sem_type = request.session['sem_type']
				added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
				TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_db)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						q_dept = EmployeePrimdetail.objects.filter(emp_id=added_by).values('dept')
						dept = q_dept[0]['dept']
						course = get_filtered_course(dept)
						days = get_week_days()
						session_name = session_name

						status = 200
						data_values = {'session_name': session_name, 'course': course, 'week_days': days}
					elif request.GET['request_type'] == 'view_previous':
						q_dept = EmployeePrimdetail.objects.filter(emp_id=added_by).values('dept')
						dept = q_dept[0]['dept']

						query = TimeTableSlots.objects.filter(session=session, sem_id__dept__dept=dept).exclude(status="DELETE").values('id', 'sem_id', 'sem_id__sem', 'sem_id__dept__dept__value', 'sem_id__dept__course__value', 'day', 'dean_approval_status', 'remark', 'num_lecture_slots', 'sem_id__dept__course').order_by('-id')
						for q in query:
							q['day_name'] = calendar.day_name[q['day']]

						status = 200
						data_values = {'data': list(query)}

				elif request.method == "POST":
					data = json.loads(request.body)
					sem = data['sem']
					days = list(data['days'])
					lec_slots = data['lec_slots']
					#######################LOCKING STARTS######################
					section_li = list(Sections.objects.filter(sem_id=sem).values_list('section_id', flat=True))
					if check_islocked("TT", section_li, session_db):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################

					###############################################################################################
					upd_li = []
					for d in days:
						q_check = TimeTableSlots.objects.filter(session=session, sem=StudentSemester.objects.get(sem_id=sem), day=d).exclude(status="DELETE").values('id')
						if len(q_check) > 0:
							upd_li.append(q_check[0]['id'])
					q_update = TimeTableSlots.objects.filter(id__in=upd_li).update(status="DELETE")
					data = []
					objs = (TimeTableSlots(sem=StudentSemester.objects.get(sem_id=sem), added_by=added_by, day=d, session=session, num_lecture_slots=lec_slots) for d in days)

					q_ins = TimeTableSlots.objects.bulk_create(objs)

					status = 200
					data_values = {'msg': "Data Successfully Inserted"}
				elif request.method == "DELETE":
					data = json.loads(request.body)
					id = data['id']
					#######################LOCKING STARTS######################
					section_li = list(Sections.objects.filter(sem_id__in=list(TimeTableSlots.objects.filter(id=id).values_list('sem', flat=True))).values_list('section_id', flat=True))
					if check_islocked("TT", section_li, session_db):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################

					q_update = TimeTableSlots.objects.filter(id=id).update(status="DELETE")
					status = 200
					data_values = {'msg': "Lecture Slots Successfully Deleted"}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def tt_slots_approval(request):
	data_values = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371])
			if check == 200:
				session = Semtiming.objects.get(uid=request.session['Session_id'])
				session_name = request.session['Session']
				session_db = request.session['Session_name']
				sem_type = request.session['sem_type']
				added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_db)

						query = TimeTableSlots.objects.filter(session=session, dean_approval_status="PENDING").exclude(status="DELETE").values('sem_id').distinct()
						data = []
						for q in query:
							query2 = TimeTableSlots.objects.filter(session=session, sem_id=q['sem_id'], dean_approval_status="PENDING").exclude(status="DELETE").values('id', 'sem_id', 'sem_id__sem', 'sem_id__dept__dept__value', 'sem_id__dept__course__value', 'day', 'dean_approval_status', 'remark', 'num_lecture_slots', 'added_by', 'added_by__name').order_by('day')
							day_det = []
							for q2 in query2:
								day_det.append({'day_name': calendar.day_name[q2['day']], 'num_slots': q2['num_lecture_slots'], 'id': q2['id']})
							data.append({'sem': query2[0]['sem_id__sem'], 'dept': query2[0]['sem_id__dept__dept__value'], 'course': query2[0]['sem_id__dept__course__value'], 'data': day_det})

						session_name = session_name

						status = 200
						data_values = {'data': list(data), "session_name": session_name}
					elif request.GET['request_type'] == 'view_previous':
						TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_db)

						query = TimeTableSlots.objects.filter(session=session).values('sem_id').distinct()
						data = []
						for q in query:
							query2 = TimeTableSlots.objects.filter(session=session, sem_id=q['sem_id']).exclude(dean_approval_status="PENDING").exclude(status="DELETE").values('id', 'sem_id', 'sem_id__sem', 'sem_id__dept__dept__value', 'sem_id__dept__course__value', 'day', 'dean_approval_status', 'remark', 'num_lecture_slots', 'added_by', 'added_by__name').order_by('day')
							day_det = []
							for q2 in query2:
								day_det.append({'day_name': calendar.day_name[q2['day']], 'num_slots': q2['num_lecture_slots'], 'id': q2['id'], 'dean_status': q2['dean_approval_status'], 'remark': q2['remark']})
							if len(day_det) > 0:
								data.append({'sem': query2[0]['sem_id__sem'], 'dept': query2[0]['sem_id__dept__dept__value'], 'course': query2[0]['sem_id__dept__course__value'], 'data': day_det})

						status = 200
						data_values = {'data': list(data)}

				elif request.method == "POST":
					data = json.loads(request.body)

					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_db):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					ids = list(data['ids'])
					app_status = data['status'].upper()
					remark = list(data['remark'])
					TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_db)

					for (i, rem) in zip(ids, remark):
						q_update = TimeTableSlots.objects.filter(id=i).update(dean_approval_status=app_status, remark=rem)

					status = 200
					data_values = {'msg': "Time Table Slot Successfully " + app_status}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def section_group(request):
	data_values = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'G' in request.session['Coordinator_type']:

				session = Semtiming.objects.get(uid=request.session['Session_id'])
				session_name = request.session['Session']
				session_db = request.session['Session_name']
				sem_type = request.session['sem_type']
				added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						course = get_coordinator_course(request.session['hash1'], 'G', session_db)

						session_name = session_name

						status = 200
						data_values = {'session_name': session_name, 'course': course, 'coord_type': 'G'}
					elif request.GET['request_type'] == 'view_previous':
						AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_db)
						GroupSection = generate_session_table_name("GroupSection_", session_db)
						SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_db)

						q_get_dept = AcadCoordinator.objects.filter(coord_type='G', emp_id=request.session['hash1']).exclude(status='DELETE').values_list('section__sem_id__dept', flat=True).distinct()

						data = []
						query = GroupSection.objects.filter(section_id__sem_id__dept__in=q_get_dept).exclude(group_id__status="DELETE").values('group_id').distinct()
						for q in query:
							q_get_details = SectionGroupDetails.objects.filter(id=q['group_id']).values('group_type', 'group_name', 'type_of_group')
							sem_id = ""
							course_id = ""
							sec_id = []
							secs = []
							semes = ""
							course_name = ""
							dept_name = ""
							dept_id = 0
							for g in q_get_details:
								q_sec_det = GroupSection.objects.filter(group_id=q['group_id']).values('section_id', 'section_id__section', 'section_id__sem_id__dept__dept__value', 'section_id__sem_id__dept__course_id__value', 'section_id__sem_id__dept__course_id', 'section_id__sem_id', 'section_id__sem_id__sem', 'section_id__sem_id__dept')
								for se in q_sec_det:
									sem_id = se['section_id__sem_id']
									semes = se['section_id__sem_id__sem']
									course_id = se['section_id__sem_id__dept__course_id']
									sec_id.append(se['section_id'])
									course_name = se['section_id__sem_id__dept__course_id__value']
									dept_name = se['section_id__sem_id__dept__dept__value']
									dept_id = se['section_id__sem_id__dept']
									secs.append(se['section_id__section'])
								data.append({'group_id': q['group_id'], 'course_id': course_id, 'section_ids': sec_id, 'sections': ",".join(secs), 'sem_id': sem_id, 'semester': semes, 'group_type_id': g['group_type'], 'group_name': g['group_name'], "group_type": g['group_type'], 'course_name': course_name, 'dept': dept_name, 'dept_id': dept_id, 'type_of_group': g['type_of_group']})
						status = 200
						data_values = {'data': list(data)}

				elif request.method == "POST":
					data = json.loads(request.body)
					section = (list(data['section']))
					group_type = data['group_type'].upper()
					group_name = list(data['group_name'])
					type_of_group = data['type_of_group']

					GroupSection = generate_session_table_name("GroupSection_", session_db)
					SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_db)
					#######################LOCKING STARTS######################
					if check_islocked("GRP", section, session_db):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################
					flag_duplicate = 0
					for gn in group_name:
						for sec in section:
							q_check = GroupSection.objects.filter(group_id__group_name=gn, section_id=sec).exclude(group_id__status='DELETE').values()
							if len(q_check) > 0:
								status = 202
								data_values = {'msg': "Group " + gn + " already exists"}
								flag_duplicate = 1
								break

					if flag_duplicate == 0:
						for gn in group_name:
							q_ins = SectionGroupDetails.objects.create(group_type=group_type, group_name=gn, added_by=added_by, session=session, type_of_group=type_of_group)
							q_get = SectionGroupDetails.objects.filter(group_type=group_type, group_name=gn, session=session, type_of_group=type_of_group).values('id').order_by('-id')[:1]

							objs = (GroupSection(group_id=SectionGroupDetails.objects.get(id=q_get[0]['id']), section_id=Sections.objects.get(section_id=sec)) for sec in section)

							q_ins2 = GroupSection.objects.bulk_create(objs)

						status = 200
						data_values = {'msg': "Data Successfully Inserted"}

				elif request.method == "DELETE":
					data = json.loads(request.body)
					id = data['group_id']
					SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_db)
					GroupSection = generate_session_table_name("GroupSection_", session_db)
					#######################LOCKING STARTS######################
					section = GroupSection.objects.filter(group_id=id).values_list('section_id')
					if check_islocked("GRP", section, session_db):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################

					q_del = SectionGroupDetails.objects.filter(id=id).update(status="DELETE")
					status = 200
					data_values = {'msg': "Group Successfully Deleted"}

				elif request.method == "PUT":
					data = json.loads(request.body)
					GroupSection = generate_session_table_name("GroupSection_", session_db)
					SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_db)
					id = data['group_id']
					#######################LOCKING STARTS######################
					section = GroupSection.objects.filter(group_id=id).values_list('section_id')
					if check_islocked("GRP", section, session_db):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################

					name = data['group_name']
					group_type = data['group_type']
					type_of_group = data['type_of_group']
					q_upd = SectionGroupDetails.objects.filter(id=id).update(group_name=name, group_type=group_type, type_of_group=type_of_group)
					q_del = GroupSection.objects.filter(group_id=id).delete()

					objs = (GroupSection(group_id=SectionGroupDetails.objects.get(id=id), section_id=Sections.objects.get(section_id=sec)) for sec in data['section'])

					q_ins2 = GroupSection.objects.bulk_create(objs)

					status = 200
					data_values = {'msg': "Group Successfully Updated"}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def GroupAssign(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'G' in request.session['Coordinator_type']:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
				StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
				SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
				StudentSession = generate_session_table_name("studentSession_", session_name)
				GroupSection = generate_session_table_name("GroupSection_", session_name)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						course = get_coordinator_course(request.session['hash1'], 'G', session_name)

						session_name = session_name

						status = 200
						data_values = {'session_name': session_name, 'course': course, 'coord_type': 'G'}

					elif request.GET['request_type'] == 'selected_group_employees':
						group_id = request.GET['group_id']

						q_get_group_emp = EmpGroupAssign.objects.filter(group_id=group_id).exclude(status='DELETE').values_list('emp_id', flat=True)

						status = 200
						data_values = {'emp_list': list(q_get_group_emp)}
					elif request.GET['request_type'] == 'selected_group_students':
						group_id = request.GET['group_id']
						section_ids = get_group_sections(group_id, session_name)
						stu_list = get_section_students(section_ids, {}, session_name)
						q_get_group_stu = StuGroupAssign.objects.filter(group_id=group_id).exclude(status='DELETE').values_list('uniq_id', flat=True)

						for data in stu_list:
							for uniq in data:
								if uniq['uniq_id'] in q_get_group_stu:
									uniq['checked'] = True
								else:
									uniq['checked'] = False

						status = 200
						data_values = {'stu_list': list(stu_list)}
				elif request.method == 'POST':
					data = json.loads(request.body)
					group_id = data['group_id']
					#######################LOCKING STARTS######################
					section_li = list(GroupSection.objects.filter(group_id=group_id).values_list('section_id', flat=True))
					if check_islocked("GRP", section_li, session_name):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################
					if data['request_type'] == 'student':
						stu_list = data['stu_list']
						################## ASSIGN STUDENT #################################
						q_get_group_stu = StuGroupAssign.objects.filter(group_id=group_id).exclude(status='DELETE').values_list('uniq_id', flat=True)
						stu_to_be_del = list(set(q_get_group_stu) - set(stu_list))
						stu_to_be_ins = list(set(stu_list) - set(q_get_group_stu))

						q_del_stu = StuGroupAssign.objects.filter(uniq_id__in=stu_to_be_del, group_id=group_id).update(status='DELETE')

						objs = (StuGroupAssign(uniq_id=StudentSession.objects.get(uniq_id=uniq), group_id=SectionGroupDetails.objects.get(id=group_id)) for uniq in stu_to_be_ins)
						q_ins = StuGroupAssign.objects.bulk_create(objs)

						status = 200

						data_values = {'msg': 'Students Successfully Assigned'}

					elif data['request_type'] == 'employee':
						emp_id_list = data['emp_id']
						################## ASSIGN FACULTY #################################
						q_get_group_emp = EmpGroupAssign.objects.filter(group_id=group_id).exclude(status='DELETE').values_list('emp_id', flat=True)
						emp_to_be_del = list(set(q_get_group_emp) - set(emp_id_list))
						emp_to_be_ins = list(set(emp_id_list) - set(q_get_group_emp))

						q_del_stu = EmpGroupAssign.objects.filter(emp_id__in=emp_to_be_del, group_id=group_id).update(status='DELETE')

						objs = (EmpGroupAssign(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), group_id=SectionGroupDetails.objects.get(id=group_id)) for emp_id in emp_id_list)
						q_ins = EmpGroupAssign.objects.bulk_create(objs)

						status = 200
						data_values = {'msg': 'Faculty Successfully Assigned'}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status, safe=False)


def subject_detail(request):
	data_values = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'S' in request.session['Coordinator_type']:

				session = Semtiming.objects.get(uid=request.session['Session_id'])
				session_name = request.session['Session']
				session_db = request.session['Session_name']
				sem_type = request.session['sem_type']
				added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
				SubjectInfo = generate_session_table_name("SubjectInfo_", session_db)
				SubjectQuesPaper=generate_session_table_name("SubjectQuestionPaper_",session_db)
				Marks = generate_session_table_name('Marks_',session_db)
				attendance=generate_session_table_name('Attendance_',session_db)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						q_dept = EmployeePrimdetail.objects.filter(emp_id=added_by).values('dept')
						dept = q_dept[0]['dept']
						course = get_coordinator_course(request.session['hash1'], 'S', session_db)
						subject_type = get_subject_type()
						subject_unit = get_subject_unit()
						session_name = session_name

						status = 200
						data_values = {'session_name': session_name, 'course': course, 'subject_unit': subject_unit, 'subject_type': subject_type, 'coord_type': 'S'}
					elif request.GET['request_type'] == 'view_previous':
						sem = request.GET['sem']

						query = SubjectInfo.objects.filter(sem=sem).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name')
						status = 200
						data_values = {'data': list(query)}

				elif request.method == "POST":

					data = json.loads(request.body)
					sem = data['sem']
					subject_data = list(data['subject'])

					qry_sections = list(Sections.objects.filter(sem_id=sem).values_list('section_id', flat=True))

					if check_islocked('SUB', qry_sections, session_db):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					flg = 0
					for sd in subject_data:
						q_check = SubjectInfo.objects.filter(session=session, sem=StudentSemester.objects.get(sem_id=sem), sub_num_code=sd['sub_num_code'], sub_alpha_code=sd['sub_alpha_code']).exclude(status="DELETE")
						if len(q_check) > 0:
							data_values = {'msg': sd['sub_alpha_code'] + "-" + str(sd['sub_num_code']) + " already exists"}
							status = 202
							flg = 1
							break

					if flg == 0:
						objs = (SubjectInfo(session=session, sem=StudentSemester.objects.get(sem_id=sem), sub_num_code=sd['sub_num_code'], sub_alpha_code=sd['sub_alpha_code'].upper(), subject_type=StudentDropdown.objects.get(sno=sd['subject_type']), subject_unit=StudentDropdown.objects.get(sno=sd['subject_unit']), sub_name=sd['sub_name'].upper(), max_ct_marks=sd['max_ct_marks'], max_ta_marks=sd['max_ta_marks'], max_att_marks=sd['max_att_marks'], no_of_units=sd['no_of_units'], max_university_marks=sd['max_university_marks'], added_by=added_by) for sd in subject_data)

						q_ins2 = SubjectInfo.objects.bulk_create(objs)

						status = 200
						data_values = {'msg': "Subjects Successfully Inserted"}

				elif request.method == "DELETE":
					data = json.loads(request.body)
					id = data['sub_id']
					qry_Sem = SubjectInfo.objects.filter(id=id).values('sem')
					sem = qry_Sem[0]['sem']

					qry_sections = list(Sections.objects.filter(sem_id=sem).values_list('section_id', flat=True))

					if check_islocked('SUB', qry_sections, session_db):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)
					ques_paper_check=SubjectQuesPaper.objects.filter(subject_id=id).filter(Q(approval_status="APPROVED") | Q(approval_status="PENDING")).exclude(status="DELETE").exists()
					# print("check",ques_paper_check,id)
					if ques_paper_check:
						return JsonResponse(data={'msg': 'subject question paper exists'}, status=202)
					
					marks_check=Marks.objects.filter(subject_id=id).exclude(status="DELETE").exists()
					attendence_check= attendance.objects.filter(subject_id=id).exclude(status="DELETE").exists()
					if marks_check or attendence_check:
						return JsonResponse(data={'msg': "Marks or Attendence corresponding to subject exists You can't delete subject"}, status=202)

					q_del = SubjectInfo.objects.filter(id=id).update(status="DELETE", added_by=added_by)
					status = 200
					data_values = {'msg': "Subject Successfully Deleted"}

				elif request.method == "PUT":
					data = json.loads(request.body)
					id = data['sub_id']
					sem = data['sem']

					qry_sections = list(Sections.objects.filter(sem_id=sem).values_list('section_id', flat=True))

					if check_islocked('SUB', qry_sections, session_db):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					update = data['subject']

					update['sub_alpha_code'] = update['sub_alpha_code'].upper()
					update['sub_name'] = update['sub_name'].upper()
					del update['added_by__name']
					del update['subject_type__value']
					del update['subject_unit__value']

					old = {}
					q_old_values = SubjectInfo.objects.filter(id=id).values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'no_of_units')
					old = q_old_values[0]
					if q_old_values[0]['sub_num_code'] != update['sub_num_code'] or q_old_values[0]['sub_alpha_code'] != update['sub_alpha_code']:
						q_check = SubjectInfo.objects.filter(sem=StudentSemester.objects.get(sem_id=sem), sub_num_code=update['sub_num_code'], sub_alpha_code=update['sub_alpha_code']).exclude(status="DELETE").values()
						if len(q_check) > 0:
							data_values = {'msg': update['sub_alpha_code'] + "-" + str(update['sub_num_code']) + " already exists"}
							status = 202

						else:
							old['status'] = "DELETE"
							old['sem'] = StudentSemester.objects.get(sem_id=old['sem'])
							old['session'] = Semtiming.objects.get(uid=old['session'])
							old['subject_unit'] = StudentDropdown.objects.get(sno=old['subject_unit'])
							old['subject_type'] = StudentDropdown.objects.get(sno=old['subject_type'])
							old['added_by'] = EmployeePrimdetail.objects.get(emp_id=old['added_by'])
							q_ins_old_value = SubjectInfo.objects.create(**old)

							q_upd = SubjectInfo.objects.filter(id=id).update(**update)
							status = 200
							data_values = {'msg': "Subject Successfully Updated"}
					else:
						old['status'] = "DELETE"
						old['sem'] = StudentSemester.objects.get(sem_id=old['sem'])
						old['session'] = Semtiming.objects.get(uid=old['session'])
						old['subject_unit'] = StudentDropdown.objects.get(sno=old['subject_unit'])
						old['subject_type'] = StudentDropdown.objects.get(sno=old['subject_type'])
						old['added_by'] = EmployeePrimdetail.objects.get(emp_id=old['added_by'])

						q_ins_old_value = SubjectInfo.objects.create(**old)

						q_upd = SubjectInfo.objects.filter(id=id).update(session=session, sem=StudentSemester.objects.get(sem_id=sem), sub_num_code=update['sub_num_code'], sub_alpha_code=update['sub_alpha_code'].upper(), subject_type=StudentDropdown.objects.get(sno=update['subject_type']), subject_unit=StudentDropdown.objects.get(sno=update['subject_unit']), sub_name=update['sub_name'].upper(), max_ct_marks=update['max_ct_marks'], max_ta_marks=update['max_ta_marks'], max_att_marks=update['max_att_marks'], max_university_marks=update['max_university_marks'], added_by=added_by, no_of_units=update['no_of_units'])
						status = 200
						data_values = {'msg': "Subject Successfully Updated"}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def create_matrix_tt(session, sem_id, section_id, session_name):
	TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_name)
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)

	lecture_break = get_lecture_break(session)
	query2 = TimeTableSlots.objects.filter(session=session, sem_id=sem_id).filter(dean_approval_status="APPROVED").exclude(status="DELETE").values('id', 'sem_id', 'sem_id__sem', 'sem_id__dept__dept__value', 'sem_id__dept__course__value', 'day', 'dean_approval_status', 'remark', 'num_lecture_slots', 'added_by', 'added_by__name').order_by('day')
	day_det = []
	max_lec = 0
	for q2 in query2:
		day_det.append({'day_name': calendar.day_name[q2['day']], 'num_slots': q2['num_lecture_slots'], 'day_id': q2['day']})
		if q2['num_lecture_slots'] > max_lec:
			max_lec = q2['num_lecture_slots']
	faculty_arr = {}
	subjects_arr = {}
	final_data = {}
	for day in day_det:
		lec_data = {}

		for lec in range(1, max_lec + 1):
			if lec > day['num_slots']:
				lec_data[str(lec)] = {'subjects': [], 'faculty': [], 'active': False}
			else:
				q_fac_time = FacultyTime.objects.filter(session=session, section=section_id, day=day['day_id'], lec_num=lec).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('subject_id').distinct()
				sub_arr = []
				final_fac_arr = []

				for f in q_fac_time:
					q_sub_det = FacultyTime.objects.filter(session=session, section=section_id, day=day['day_id'], lec_num=lec, subject_id=f['subject_id']).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('subject_id', 'subject_id__subject_type__value', 'subject_id__subject_unit__value', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'emp_id', 'emp_id__name', 'emp_id__dept__value', 'start_time', 'end_time')
					fac_arr = []
					sub_arr.append({'id': q_sub_det[0]['subject_id'], 'code': q_sub_det[0]['subject_id__sub_alpha_code'] + "-" + str(q_sub_det[0]['subject_id__sub_num_code']), 'sub_type': q_sub_det[0]['subject_id__subject_type__value'], 'sub_unit': q_sub_det[0]['subject_id__subject_unit__value'], 'sub_name': q_sub_det[0]['subject_id__sub_name'], 'mytime_from': q_sub_det[0]['start_time'], 'mytime_to': q_sub_det[0]['end_time']})
					if(q_sub_det[0]['subject_id__sub_alpha_code'] + "-" + str(q_sub_det[0]['subject_id__sub_num_code']) not in subjects_arr):
						subjects_arr[q_sub_det[0]['subject_id__sub_alpha_code'] + "-" + str(q_sub_det[0]['subject_id__sub_num_code'])] = q_sub_det[0]['subject_id__sub_name']
					for sub in q_sub_det:
						fac_arr.append({'emp_code': sub['emp_id'], 'emp_name': sub['emp_id__name'], 'dept': sub['emp_id__dept__value']})
						if(sub['emp_id'] not in faculty_arr):
							faculty_arr[sub['emp_id']] = sub['emp_id__name']
					final_fac_arr.append(fac_arr)
					# final_sub_arr.append(sub_arr)
				lec_data[str(lec)] = {'subjects': sub_arr, 'faculty': final_fac_arr, 'active': True}
		final_data[day['day_id']] = lec_data
	return [final_data, lecture_break, faculty_arr, subjects_arr]


def time_table(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'T' in request.session['Coordinator_type']:
				session = Semtiming.objects.get(uid=request.session['Session_id'])
				session_name = request.session['Session']
				session_db = request.session['Session_name']
				sem_type = request.session['sem_type']
				added_by = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
				TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_db)
				FacultyTime = generate_session_table_name("FacultyTime_", session_db)
				SubjectInfo = generate_session_table_name("SubjectInfo_", session_db)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						course = get_coordinator_course(request.session['hash1'], 'T', session_db)
						depts = get_dept()
						session_name = session_name

						status = 200
						data_values = {'session_name': session_name, 'course': course, 'department': depts, 'coord_type': 'T'}
					elif request.GET['request_type'] == "matrix":

						day_det = []

						faculty_arr = {}
						subjects_arr = {}
						final_data = {}

						max_lec = 0

						sem_id = request.GET['sem_id']
						section_id = request.GET['section_id']
						lecture_break = get_lecture_break(session)

						query2 = TimeTableSlots.objects.filter(session=session, sem_id=sem_id).filter(dean_approval_status="APPROVED").exclude(status="DELETE").values('id', 'sem_id', 'sem_id__sem', 'sem_id__dept__dept__value', 'sem_id__dept__course__value', 'day', 'dean_approval_status', 'remark', 'num_lecture_slots', 'added_by', 'added_by__name').order_by('day')

						for q2 in query2:
							day_det.append({'day_name': calendar.day_name[q2['day']], 'num_slots': q2['num_lecture_slots'], 'day_id': q2['day']})
							if q2['num_lecture_slots'] > max_lec:
								max_lec = q2['num_lecture_slots']

						lecture_time = StudentAcademicsDropdown.objects.filter(field='LECTURES').exclude(value=None).values_list('value', flat=True)

						lec_time = list(StudentAcademicsDropdown.objects.filter(field=x).exclude(value=None).values('field', 'value') for x in lecture_time)

						for day in day_det:
							lec_data = {}

							for lec in range(1, max_lec + 1):
								l_time = {}
								l_time['mytime_from'] = ''
								l_time['mytime_to'] = ''
								for l in lec_time:
									# #print(l[0]['field'])
									if int(l[0]['field'][-1:]) == lec:
										split = l[0]['value'].replace('-', ' ').split(' ')
										l_time['mytime_from'] = split[0]
										l_time['mytime_to'] = split[1]
								# #print(l_time)
								if lec > day['num_slots']:
									lec_data[str(lec)] = {'subjects': [], 'faculty': [], 'active': False}
								else:
									q_fac_time = FacultyTime.objects.filter(session=session, section=section_id, day=day['day_id'], lec_num=lec).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('subject_id').distinct()
									sub_arr = []
									final_fac_arr = []

									for f in q_fac_time:
										q_sub_det = FacultyTime.objects.filter(session=session, section=section_id, day=day['day_id'], lec_num=lec, subject_id=f['subject_id']).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('subject_id', 'subject_id__subject_type__value', 'subject_id__subject_unit__value', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'emp_id', 'emp_id__name', 'emp_id__dept__value', 'start_time', 'end_time')

										fac_arr = []

										l_time = {}
										l_time['mytime_from'] = ''
										l_time['mytime_to'] = ''
										# #print(q_sub_det)
										l_time['mytime_from'] = q_sub_det[0]['start_time']
										l_time['mytime_to'] = q_sub_det[0]['end_time']

										sub_arr.append({'id': q_sub_det[0]['subject_id'], 'code': q_sub_det[0]['subject_id__sub_alpha_code'] + "-" + str(q_sub_det[0]['subject_id__sub_num_code']), 'sub_type': q_sub_det[0]['subject_id__subject_type__value'], 'sub_unit': q_sub_det[0]['subject_id__subject_unit__value'], 'sub_name': q_sub_det[0]['subject_id__sub_name'], 'mytime_from': l_time['mytime_from'], 'mytime_to': l_time['mytime_to']})

										if(q_sub_det[0]['subject_id__sub_alpha_code'] + "-" + str(q_sub_det[0]['subject_id__sub_num_code']) not in subjects_arr):
											subjects_arr[q_sub_det[0]['subject_id__sub_alpha_code'] + "-" + str(q_sub_det[0]['subject_id__sub_num_code'])] = q_sub_det[0]['subject_id__sub_name']
										for sub in q_sub_det:
											fac_arr.append({'emp_code': sub['emp_id'], 'emp_name': sub['emp_id__name'], 'dept': sub['emp_id__dept__value']})
											if(sub['emp_id'] not in faculty_arr):
												faculty_arr[sub['emp_id']] = sub['emp_id__name']
										final_fac_arr.append(fac_arr)

									lec_data[str(lec)] = {'subjects': sub_arr, 'faculty': final_fac_arr, 'active': True}
							final_data[day['day_id']] = lec_data

						status = 200
						data_values = {'data': final_data, 'lecture_break': lecture_break, 'faculty_arr': faculty_arr, 'subjects_arr': subjects_arr}
				elif request.method == "POST":
					data = json.loads(request.body)
					section_id = data['section_id']
					sub_id = data['sub_id']
					day = data['day']
					lec = data['lec_num']
					#######################LOCKING STARTS######################
					if check_islocked("TT", [section_id], session_db):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################
					from_zone = tz.tzutc()
					to_zone = tz.tzlocal()
					utc = datetime.strptime((((str(data['mytime_from']).split('T'))[1]).split('Z'))[0].split('.')[0], '%H:%M:%S')

					utc = utc.replace(tzinfo=from_zone)

					start_time = utc.astimezone(to_zone)

					utc = datetime.strptime((((str(data['mytime_to']).split('T'))[1]).split('Z'))[0].split('.')[0], '%H:%M:%S')

					utc = utc.replace(tzinfo=from_zone)

					end_time = utc.astimezone(to_zone)

					start_time = (((str(start_time).split(' '))[1]).split('+'))[0]
					end_time = (((str(end_time).split(' '))[1]).split('+'))[0]
					emp_id = list(data['emp_code'])

					q_check_sub = FacultyTime.objects.filter(session=session, section=Sections.objects.get(section_id=section_id), day=day, lec_num=lec, subject_id=SubjectInfo.objects.get(id=sub_id)).exclude(status="DELETE").values()
					if len(q_check_sub) > 0:
						status = 200
						data_values = {'msg': 'Subject already Assigned for this lecture'}
					else:
						flag = 0
						objs = (FacultyTime(session=session, section=Sections.objects.get(section_id=section_id), day=day, lec_num=lec, subject_id=SubjectInfo.objects.get(id=sub_id), status="INSERT", emp_id=EmployeePrimdetail.objects.get(emp_id=emp), added_by=added_by, start_time=start_time, end_time=end_time) for emp in emp_id)
						q_ins = FacultyTime.objects.bulk_create(objs)

						status = 200
						data_values = {'msg': "Subject Successfully Added"}
				elif request.method == "DELETE":
					data = json.loads(request.body)
					section_id = data['section_id']
					sub_id = data['sub_id']
					day = data['day']
					lec = data['lec_num']
					#######################LOCKING STARTS######################
					if check_islocked("TT", [section_id], session_db):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################
					q_update_status = FacultyTime.objects.filter(session=session, section=section_id, day=day, lec_num=lec, subject_id=sub_id).exclude(status="DELETE").update(status="DELETE")

					status = 200
					data_values = {'msg': "Subject Successfully Deleted"}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status, safe=False)


def Academics_Calendar(request):
	data_values = {}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371])
			if(check == 200):
				session_name = request.session['Session_name']
				AcademicsCalendar = generate_session_table_name("AcademicsCalendar_", session_name)
				session = request.session['Session_id']

				if(request.method == 'POST'):
					data = json.loads(request.body)

					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_name):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					title = data['title']
					start = datetime.strptime(str(data['start']).split('T')[0], "%Y-%m-%d").date()
					end = datetime.strptime(str(data['end']).split('T')[0], "%Y-%m-%d").date()
					type = data['type']
					color = data['color']
					description = data['description']
					AcademicsCalendar.objects.create(title=title, start=start, end=end, type=StudentAcademicsDropdown.objects.get(sno=type), color=color, description=description, status="INSERT")
					status = 200
					data_values = {"msg": "Data Added"}
				elif(request.method == 'GET'):
					if(request.GET['request_type'] == 'view'):
						query = AcademicsCalendar.objects.exclude(status="DELETE").values('sno', 'title', 'start', 'end', 'type',
																						  'type__value', 'color', 'description').order_by('start')
						query2 = StudentAcademicsDropdown.objects.filter(field="EVENT TYPE", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
						status = 200
						data_values = {'data': list(query), 'types': list(query2)}
					else:
						status = 500
						data_values = {'msg': 'Data cannot be Viewed'}
				elif(request.method == 'DELETE'):
					data = json.loads(request.body)
					event_id = data["id"]
					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_name):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					AcademicsCalendar.objects.filter(sno=event_id).update(status="DELETE")
					status = 200
					data_values = {"msg": "Data Deleted"}
				elif(request.method == 'PUT'):
					data = json.loads(request.body)
					id = data["id"]
					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_name):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					title = data['title']
					start = datetime.strptime(str(data['start']).split('T')[0], "%Y-%m-%d").date()
					end = datetime.strptime(str(data['end']).split('T')[0], "%Y-%m-%d").date()
					type = data['type']
					color = data['color']
					description = data['description']
					AcademicsCalendar.objects.filter(sno=id).update(title=title, start=start, end=end, type=StudentAcademicsDropdown.objects.get(sno=type), color=color, description=description)
					status = 200
					data_values = {"msg": "Data Updated"}
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status)


# def LockingUnlocking(request):
# 	data_values = {}
# 	status = 403
# 	if 'HTTP_COOKIE' in request.META:
# 		if request.user.is_authenticated:
# 			check = checkpermission(request, [1371])
# 			if check == 200:
# 				query = []
# 				session = request.session['Session_id']
# 				session_name = request.session['Session_name']
# 				sem_type = request.session['sem_type']
# 				LockingUnlocking = generate_session_table_name("LockingUnlocking_", session_name)

# 				if(request.method == 'GET'):
# 					if request.GET['request_type'] == 'form_data':
# 						course = get_course()
# 						unlock_type = []

# 						unlock_type.append({'sno': 'ATT', 'value': 'ATTENDANCE'})
# 						unlock_type.append({'sno': 'F', 'value': 'FEEDBACK'})
# 						unlock_type.append({'sno': 'MMS', 'value': 'INSERT MARKS'})
# 						unlock_type.append({'sno': 'UNM', 'value': 'INSERT UNIVERSITY MARKS'})
# 						unlock_type.append({'sno': 'SUB', 'value': 'SUBJECT SETTINGS'})
# 						unlock_type.append({'sno': 'GRP', 'value': 'GROUP SETTIGS'})
# 						unlock_type.append({'sno': 'TT', 'value': 'TIME TABLE SETTINGS'})
# 						unlock_type.append({'sno': 'CO', 'value': "ADD COs"})
# 						unlock_type.append({'sno': 'DEAN', 'value': 'DEAN ACADEMIC SETTINGS'})
# 						unlock_type.append({'sno': 'REG', 'value': 'SEMESTER REGISTRATION'})
# 						unlock_type.append({'sno': 'ROLL', 'value': 'CHANGE CLASS ROLL NO'})
# 						unlock_type.append({'sno': 'QM', 'value': 'QUESTION MODERATOR'})
# 						unlock_type.append({'sno': 'HOD', 'value': 'HOD SETTINGS'})
# 						unlock_type.append({'sno': 'FEED', 'value': 'DEAN FEEDBACK SETTINGS'})
# 						unlock_type.append({'sno': 'DMS', 'value': 'DEAN MARKS SETTINGS'})
# 						unlock_type.append({'sno': 'QUES', 'value': 'EMPLOYEE QUESTION PAPER SETTINGS'})
# 						unlock_type.append({'sno': 'SUR', 'value': 'SURVEY FORM'})

# 						status = 200
# 						data_values = {'course': course, 'unlock_type': unlock_type}

# 					elif request.GET['request_type'] == 'view_previous':
# 						q_view_previous = LockingUnlocking.objects.values('emp_id', 'emp_id__name', 'section__section', 'section__sem_id__sem', 'section__sem_id__dept__dept__value', 'section__sem_id__dept__course__value', 'unlock_from', 'unlock_to', 'lock_type', 'att_date_from', 'att_date_to', 'att_type__value', 'time_stamp').order_by('-time_stamp')

# 						for q in q_view_previous:
# 							if q['lock_type'] == 'ATT':
# 								q['lock_type'] = 'ATTENDANCE'
# 							elif q['lock_type'] == 'F':
# 								q['lock_type'] = 'FEEDBACK'
# 							elif q['lock_type'] == 'G':
# 								q['lock_type'] = 'GROUP ASSIGN'
# 							elif q['lock_type'] == 'M':
# 								q['lock_type'] = 'MARKS'
# 							elif q['lock_type'] == 'T':
# 								q['lock_type'] = 'TIME TABLE'

# 						status = 200
# 						data_values = {'data': list(q_view_previous)}
# 				elif(request.method == 'POST'):
# 					data = json.loads(request.body)
# 					course = data['course']
# 					dept = data['branch']
# 					semester = data['sem']
# 					section = data['section']
# 					unlock = data['unlock']
# 					from_date = data['from_date']
# 					to_date = data['to_date']
# 					# #print(data)

# 					sec_id = []
# 					if course == 'ALL':
# 						course = get_course()
# 						for c in course:
# 							branch = get_branch(c['sno'])
# 							for b in branch:
# 								semes = get_semester(b['uid'], sem_type)
# 								for s in semes:
# 									secs = get_section(s['sem_id'])
# 									for sec in secs:
# 										sec_id.append(sec['section_id'])

# 					elif dept == 'ALL':
# 						branch = get_branch(course)
# 						for b in branch:
# 							semes = get_semester(b['uid'], sem_type)
# 							for s in semes:
# 								secs = get_section(s['sem_id'])
# 								for sec in secs:
# 									sec_id.append(sec['section_id'])

# 					elif semester == 'ALL':
# 						semes = get_semester(dept, sem_type)
# 						for s in semes:
# 							secs = get_section(s['sem_id'])
# 							for sec in secs:
# 								sec_id.append(sec['section_id'])

# 					elif section == 'ALL':
# 						secs = get_section(semester)
# 						print(secs)
# 						for sec in secs:
# 							sec_id.append(sec['section_id'])
# 					else:
# 						sec_id.append(section)
# 					print(section,'section')
# 					if unlock == 'ATT' or unlock == 'M':
# 						print("ATT")
# 						att_type = data['att_type']

# 						emp_arr = data['emp_arr']
# 						att_date_from = data['att_fdate']
# 						att_date_to = data['att_tdate']

# 						if emp_arr[0] == 'ALL':
# 							print("ALL")
# 							for sec in sec_id:
# 								print(sec)
# 								q_emp = get_fac_time_faculty(sec, session_name)
# 								print(len(q_emp))
# 								for e in q_emp:
# 									print(e)
# 								if unlock == 'ATT':
# 									for atp in att_type:
# 										print(atp)
# 										objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session), lock_type=unlock, section=Sections.objects.get(section_id=sec), unlock_from=from_date, unlock_to=to_date, emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id['emp_id']), att_type=StudentAcademicsDropdown.objects.get(sno=atp), att_date_from=att_date_from, att_date_to=att_date_to) for emp_id in q_emp)
# 										q_ins = LockingUnlocking.objects.bulk_create(objs)
# 								else:
# 									objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session), lock_type=unlock, section=Sections.objects.get(section_id=sec), unlock_from=from_date, unlock_to=to_date, emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id['emp_id']), att_date_from=att_date_from, att_date_to=att_date_to) for emp_id in q_emp)
# 									q_ins = LockingUnlocking.objects.bulk_create(objs)

# 						else:
# 							print("NOT ALL")
# 							for sec in sec_id:
# 								if unlock == 'ATT':
# 									for atp in att_type:
# 										objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session), lock_type=unlock, section=Sections.objects.get(section_id=sec), unlock_from=from_date, unlock_to=to_date, emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), att_type=StudentAcademicsDropdown.objects.get(sno=atp), att_date_from=att_date_from, att_date_to=att_date_to) for emp_id in emp_arr)
# 										q_ins = LockingUnlocking.objects.bulk_create(objs)
# 								else:
# 									objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session), lock_type=unlock, section=Sections.objects.get(section_id=sec), unlock_from=from_date, unlock_to=to_date, emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)) for emp_id in emp_arr)
# 									q_ins = LockingUnlocking.objects.bulk_create(objs)

# 					else:
# 						print("TTT")
# 						objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session), lock_type=unlock, section=Sections.objects.get(section_id=sec), unlock_from=from_date, unlock_to=to_date) for sec in sec_id)
# 						q_ins = LockingUnlocking.objects.bulk_create(objs)

# 					# if unlock=='A' or unlock=='M':
# 					#   objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session),lock_type=unlock,section=Sections.objects.get(section_id=section),unlock_from=from_date,unlock_to=to_date,emp_id=EmployeePrimdetail
# 					#       .objects.get(emp_id=emp_id)) for emp_id in emp_arr)
# 					#   q_ins = LockingUnlocking.objects.bulk_create(objs)
# 					# else:
# 					#   q_ins = LockingUnlocking.objects.create(session=Semtiming.objects.get(uid=session),lock_type=unlock,section=Sections.objects.get(section_id=section),unlock_from=from_date,unlock_to=to_date,emp_id=EmployeePrimdetail
# 					#       .objects.get(emp_id=emp_id))

# 					status = 200
# 					data_values = {'msg': 'Data Successfully Inserted'}
# 				else:
# 					status = 502
# 			else:
# 				status = 403
# 		else:
# 			status = 401
# 	else:
# 		status = 500

# 	return JsonResponse(data=data_values, status=status)


#################################################### - Divyanshu - (Re-created this function for the multiple dropdowns) ###########################################################
def LockingUnlocking(request):
	data_values = {}
	status = statusCodes.STATUS_FORBIDDEN
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371])
			if check == statusCodes.STATUS_SUCCESS:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				LockingUnlocking = generate_session_table_name("LockingUnlocking_", session_name)

				if (requestMethod.GET_REQUEST(request)):
					if(requestType.custom_request_type(request.GET, 'form_data')):
						course = get_course()
						unlock_type = []

						unlock_type.append({'sno': 'ATT', 'value': 'ATTENDANCE'})
						unlock_type.append({'sno': 'F', 'value': 'FEEDBACK'})
						unlock_type.append({'sno': 'MMS', 'value': 'INSERT MARKS'})
						unlock_type.append({'sno': 'UNM', 'value': 'INSERT UNIVERSITY MARKS'})
						unlock_type.append({'sno': 'SUB', 'value': 'SUBJECT SETTINGS'})
						unlock_type.append({'sno': 'GRP', 'value': 'GROUP SETTIGS'})
						unlock_type.append({'sno': 'TT', 'value': 'TIME TABLE SETTINGS'})
						unlock_type.append({'sno': 'CO', 'value': "ADD COs"})
						unlock_type.append({'sno': 'DEAN', 'value': 'DEAN ACADEMIC SETTINGS'})
						unlock_type.append({'sno': 'REG', 'value': 'SEMESTER REGISTRATION'})
						unlock_type.append({'sno': 'ROLL', 'value': 'CHANGE CLASS ROLL NO'})
						unlock_type.append({'sno': 'QM', 'value': 'QUESTION MODERATOR'})
						unlock_type.append({'sno': 'HOD', 'value': 'HOD SETTINGS'})
						unlock_type.append({'sno': 'FEED', 'value': 'DEAN FEEDBACK SETTINGS'})
						unlock_type.append({'sno': 'DMS', 'value': 'DEAN MARKS SETTINGS'})
						unlock_type.append({'sno': 'QUES', 'value': 'EMPLOYEE QUESTION PAPER SETTINGS'})
						unlock_type.append({'sno': 'SUR', 'value': 'SURVEY FORM'})

						status = statusCodes.STATUS_SUCCESS
						data_values = {'course': course, 'unlock_type': unlock_type}

					elif(requestType.custom_request_type(request.GET, 'view_previous')):
						q_view_previous = LockingUnlocking.objects.values('emp_id', 'emp_id__name', 'section__section', 'section__sem_id__sem', 'section__sem_id__dept__dept__value', 'section__sem_id__dept__course__value', 'unlock_from', 'unlock_to', 'lock_type', 'att_date_from', 'att_date_to', 'att_type__value', 'time_stamp').order_by('-time_stamp')

						for q in q_view_previous:
							if q['lock_type'] == 'ATT':
								q['lock_type'] = 'ATTENDANCE'
							elif q['lock_type'] == 'F':
								q['lock_type'] = 'FEEDBACK'
							elif q['lock_type'] == 'G':
								q['lock_type'] = 'GROUP ASSIGN'
							elif q['lock_type'] == 'M':
								q['lock_type'] = 'MARKS'
							elif q['lock_type'] == 'T':
								q['lock_type'] = 'TIME TABLE'

						status = statusCodes.STATUS_SUCCESS
						data_values = {'data': list(q_view_previous)}

				elif (requestMethod.POST_REQUEST(request)):
					data = json.loads(request.body)
					course = data['course']
					dept = data['branch']
					semester = data['sem']
					section = data['section']
					unlock = data['unlock']
					from_date = data['from_date']
					to_date = data['to_date']
					sec_id = list(Sections.objects.filter(dept__in=dept,sem_id__sem__in =semester, section__in=section,).values_list('section_id', flat=True))
					if unlock == 'ATT' or unlock == 'M':
						att_type = data['att_type']
						emp_arr = data['emp_arr']
						att_date_from = data['att_fdate']
						att_date_to = data['att_tdate']
						for sec in sec_id:
							#q_emp is storing the faculties of the particular section - to make the intersection with the emp_arr send by the user	
							q_emp = get_fac_time_faculty(sec, session_name)
							emp =[]
							for e in q_emp:
								emp.append(e['emp_id'])
							#intersectioin of employee array list(sent by user) and employees of the section 
							emp_arr1=list(set(emp_arr).intersection(set(emp)))
							if unlock == 'ATT':
								for atp in att_type:
									objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session), lock_type=unlock, section=Sections.objects.get(section_id=sec), unlock_from=from_date, unlock_to=to_date, emp_id=EmployeePrimdetail.objects.get(emp_id=int(emp_id)), att_type=StudentAcademicsDropdown.objects.get(sno=atp), att_date_from=att_date_from, att_date_to=att_date_to) for emp_id in emp_arr1)
									q_ins = LockingUnlocking.objects.bulk_create(objs)
							else:
								objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session), lock_type=unlock, section=Sections.objects.get(section_id=sec), unlock_from=from_date, unlock_to=to_date, emp_id=EmployeePrimdetail.objects.get(emp_id=int(emp_id))) for emp_id in emp_arr1)
								q_ins = LockingUnlocking.objects.bulk_create(objs)
					else:
						objs = (LockingUnlocking(session=Semtiming.objects.get(uid=session), lock_type=unlock, section=Sections.objects.get(section_id=sec), unlock_from=from_date, unlock_to=to_date) for sec in sec_id)
						q_ins = LockingUnlocking.objects.bulk_create(objs)
					status = statusCodes.STATUS_SUCCESS
					data_values = {'msg': statusMessages.MESSAGE_INSERT}
				else:
					status = statusCodes.STATUS_METHOD_NOT_ALLOWED
			else:
				status = statusCodes.STATUS_FORBIDDEN
		else:
			status = statusCodes.STATUS_UNAUTHORIZED
	else:
		status = statusCodes.STATUS_SERVER_ERROR

	return functions.RESPONSE(data_values, status)
##################################################################################################################################################################################


def ChangeClassRollNo(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'C' in request.session['Coordinator_type']:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				studentSession = generate_session_table_name("studentSession_", session_name)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						course = get_coordinator_course(request.session['hash1'], 'C', session_name)
						status = 200
						data_values = {'course': course, 'coord_type': 'C'}
				elif request.method == 'PUT':
					data = json.loads(request.body)
					stu_data = data['stu_data']
					#######################LOCKING STARTS######################
					section_li = list(studentSession.objects.filter(uniq_id__in=list(stu['uniq_id'] for stu in stu_data)).values_list('section', flat=True))
					if check_islocked("ROLL", section_li, session_name):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################
					for stu in stu_data:
						q_update = studentSession.objects.filter(uniq_id=stu['uniq_id']).update(class_roll_no=stu['class_roll_no'])
					status = 200
					data_values = {'msg': 'Class Roll No changed Successfully'}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def StudentNominalList(request):
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
					if check == 200 and 'H' in request.session['Coordinator_type']:
						if request.GET['request_type'] == 'form_data':
							q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
							dept = q_dept[0]['dept']
							course = get_filtered_course(dept)
							status = 200
							data_values = {'course': course, 'gender': get_gender(), 'attendance_type': get_attendance_type(session), 'subject_type': get_subject_type()}

				elif request.GET['request_by'] in ('DEAN', 'dean'):
					check = checkpermission(request, [1371, 1371, 1368, 1372, 1452])
					if check == 200:
						if request.GET['request_type'] == 'form_data':
							course = get_course()
							status = 200
							data_values = {'course': course, 'gender': get_gender(), 'attendance_type': get_attendance_type(session), 'subject_type': get_subject_type(), 'coord_type': get_coord_type()}

				elif request.GET['request_by'] in ['class_coord', 'extra_coord', 'tt_coord', 'question_moderator', 'exam_coordinator', 'university_exam_coordinator', 'nba_coordinator']:
					check = checkpermission(request, [1369])
					if check == 200 and ('C' in request.session['Coordinator_type'] or 'E' in request.session['Coordinator_type'] or 'T' in request.session['Coordinator_type'] or 'QM' in request.session['Coordinator_type'] or 'COE' in request.session['Coordinator_type'] or 'NC' in request.session['Coordinator_type']):
						if request.GET['request_type'] == 'form_data':
							except_coord_type = ['QM', 'COE', 'UVE', 'NC']

							if 'Coordinator_type' in request.GET and request.GET['Coordinator_type'] in except_coord_type:
								ccourse = get_coordinator_course(request.session['hash1'], request.GET['Coordinator_type'], session_name)
							else:
								ccourse = get_coordinator_course(request.session['hash1'], request.GET['request_by'][0].upper(), session_name)
							course = []
							for c in ccourse:
								course.append({'course__value': c['section__sem_id__dept__course__value'], 'course': c['section__sem_id__dept__course'],'duration':c['section__sem_id__dept__course_duration']})
							status = 200
							data_values = {'course': course, 'gender': get_gender(), 'attendance_type': get_attendance_type(session), 'subject_type': get_subject_type()}
				elif request.GET['request_by'] == 'faculty':
					check = checkpermission(request, [1369])
					if check == 200 and 'A' in request.session['Coordinator_type']:
						if request.GET['request_type'] == 'form_data':
							ccourse = get_fac_time_course(request.session['hash1'], session_name)
							course = []
							for c in ccourse:
								course.append({'course__value': c['section__sem_id__dept__course_id__value'], 'course': c['section__sem_id__dept__course_id']})
							status = 200
							data_values = {'course': course, 'gender': get_gender(), 'attendance_type': get_attendance_type(session), 'subject_type': get_subject_type()}

				else:
					status = 403
			else:
				status = 502
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def StudentAttendanceRecord(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			query = []
			session = request.session['Session_id']
			session_name = request.session['Session_name']
			sem_type = request.session['sem_type']
			SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

			if(request.method == 'GET'):
				if request.GET['request_by'] in ('hod', 'dean', 'extra_coord', 'class_coord', 'faculty'):
					check = checkpermission(request, [1369, 319, 1371, 1372])
					if check == 200:
						if request.GET['request_type'] == 'att_record':
							sec = list(request.GET['section'].split(',')[:-1])
							gender = list(map(int, request.GET['gender'].split(',')))
							att_type = list(request.GET['att_type'].split(',')[:-1])
							subjects = list(request.GET['subjects'].split(',')[:-1])
							dept = list(request.GET['branch'].split(',')[:-1])
							sem = list(request.GET['sem'].split(',')[:-1])
							att_category = list(request.GET['att_category'].split(','))
							if att_category[0] == '':
								att_category = []

							from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
							to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()

							multi_sem = StudentSemester.objects.filter(dept__in=dept, sem__in=sem).values_list('sem_id', flat=True)
							almostGone = []
							att_all_data = []
							for sem in multi_sem:
								section = Sections.objects.filter(sem_id=sem, section__in=sec).values_list('section_id', flat=True)
								students = get_section_students(section, {'uniq_id__gender__in': gender}, session_name)
								q_sub = list(SubjectInfo.objects.filter(id__in=subjects).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name').order_by('id'))
								# #print(q_sub)
								att_data = []
								main_detail = []
								for sec_student in students:
									if len(sec_student) > 0:
										q_sub = list(SubjectInfo.objects.filter(id__in=subjects, sem=sec_student[0]['section__sem_id']).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name').order_by('id'))
										main_detail = Sections.objects.filter(section_id__in=section).values('section', 'sem_id__sem', 'sem_id__dept__dept__value', 'sem_id__dept__course__value')[0]
									else:
										q_sub = []
									zz = 0
									for stu in sec_student:
										# #print(zz)
										zz = zz + 1
										listing = get_student_attendance(stu['uniq_id'], max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(stu['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type[:], copy.deepcopy(q_sub), 1, att_category, session_name)
										for i in listing['sub_data']:
											listing['sub_' +i['sub_name']+'('+ i['sub_alpha_code'] + '-' + i['sub_num_code']+')'] = {}
											listing['sub_' +i['sub_name']+'('+ i['sub_alpha_code'] + '-' + i['sub_num_code']+')']['present_count'] = i['present_count']
											try:
												listing['sub_' +i['sub_name']+'('+ i['sub_alpha_code'] + '-' + i['sub_num_code']+')']['percent'] = min(100, round(i['present_count'] * 100 / i['total']))
											except Exception as e:
												listing['sub_' +i['sub_name']+'('+ i['sub_alpha_code'] + '-' + i['sub_num_code']+')']['percent'] = 0
											listing['sub_' +i['sub_name']+'('+ i['sub_alpha_code'] + '-' + i['sub_num_code']+')']['absent_count'] = i['absent_count']
											listing['sub_' +i['sub_name']+'('+ i['sub_alpha_code'] + '-' + i['sub_num_code']+')']['total'] = i['total']
											listing['sub_' +i['sub_name']+'('+ i['sub_alpha_code'] + '-' + i['sub_num_code']+')']['id'] = i['id']
											listing.pop('sub_data', None)
											stu.update(listing)
										att_data.append(stu)
								almostGone.append({'main_detail': main_detail, 'attendance_detail': att_data})
							att_all_data.append(almostGone)
							data_values = {'att_data': almostGone}

							status = 200

				else:
					status = 403
			else:
				status = 502
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status)


def CollegeAttendanceRecord(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			query = []
			session = request.session['Session_id']
			session_name = request.session['Session_name']
			sem_type = request.session['sem_type']
			StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
			Attendance = generate_session_table_name("Attendance_", session_name)

			if(request.method == 'GET'):
				if request.GET['request_by'] in ('hod', 'dean', 'class_coord', 'faculty'):
					check = checkpermission(request, [1369, 1368, 1372])
					if check == 200:
						if request.GET['request_type'] == 'cllg_record':
							sec = request.GET['section'].split(',')
							dept = request.GET['branch'].split(',')
							sem = request.GET['sem'].split(',')
							status_li = request.GET['status'].split(',')

							if request.GET['request_by'] != 'faculty':
								emp_id = request.GET['emp_id'].split(',')
							else:
								emp_id = [request.session['hash1']]
							from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
							to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()

							class_att_type = get_class_attendance_type(session)
							att_type_li = []
							for att in class_att_type:
								att_type_li.append(att['sno'])

							section = Sections.objects.filter(sem_id__sem__in=sem, section__in=sec, dept__in=dept).values_list('section_id', flat=True)

							qry_att_ids = StudentAttStatus.objects.filter(att_id__emp_id__in=emp_id, att_id__date__range=[from_date, to_date], att_id__section__in=section, att_type__in=att_type_li).values('att_id', 'att_id__date', 'att_id__lecture', 'att_id__group_id', 'att_id__section', 'att_id__emp_id__name', 'att_id__emp_id', 'att_id__section__section', 'att_id__section__sem_id__sem', 'att_id__subject_id__sub_name', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_alpha_code', 'att_id__group_id__group_name', 'att_id__group_id__group_type', 'status', 'att_id__emp_id__dept__value', 'att_id__emp_id__desg__value', 'att_id__section__sem_id__dept__dept__value', 'att_id__section__sem_id__dept__course__value', 'att_id__time_stamp').distinct().order_by('-att_id__time_stamp')

							data = []
							for att in qry_att_ids:
								att['sub_code'] = att['att_id__subject_id__sub_alpha_code'] + '-' + str(att['att_id__subject_id__sub_num_code'])

								qry_check_status = list(Attendance.objects.filter(lecture=att['att_id__lecture'], date=att['att_id__date'], group_id=att['att_id__group_id'], section=att['att_id__section']).values('status', 'time_stamp', 'id').order_by('id'))

								status = 'UPDATE'
								if qry_check_status[0]['id'] == att['att_id']:
									status = 'INSERT'

								if qry_check_status[-1]['id'] == att['att_id'] and qry_check_status[-1]['status'] == 'DELETE':
									status = 'DELETE'

								att['status'] = status
								att['time_stamp'] = datetime.strptime(str(att['att_id__time_stamp']).split('.')[0], "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%Y %H:%M:%S")

								if not status in status_li:
									continue
								data.append(att)

							data_values = {'cllg_data': data}

							status = 200

				else:
					status = 403
			else:
				status = 502
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def AssignedCoordinator(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			query = []
			session = request.session['Session_id']
			session_name = request.session['Session_name']
			sem_type = request.session['sem_type']
			AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

			if(request.method == 'GET'):
				if request.GET['request_by'] in ('dean'):
					check = checkpermission(request, [1368, 1372])
					if check == 200:
						if request.GET['request_type'] == 'assigned_coordinator':
							sec = request.GET['section'].split(',')
							dept = request.GET['branch'].split(',')
							sem = request.GET['sem'].split(',')
							coord_type = request.GET['coord_type'].split(',')

							section = Sections.objects.filter(sem_id__sem__in=sem, section__in=sec, dept__in=dept).values_list('section_id', flat=True)

							qry_coord = AcadCoordinator.objects.filter(session=session, section__in=section, coord_type__in=coord_type).exclude(status="DELETE").values('id', 'section', 'section__sem_id__sem', 'section__section', 'section__sem_id__dept__dept__value', 'emp_id', 'emp_id__name', 'section__sem_id__dept__course__value', 'coord_type')
							for q in qry_coord:
								if q['coord_type'] == 'T':
									q['coord_type'] = 'TIME TABLE COORDINATOR'
								elif q['coord_type'] == 'C':
									q['coord_type'] = 'CLASS COORDINATOR'
								elif q['coord_type'] == 'G':
									q['coord_type'] = 'ASSIGN GROUP COORDINATOR'
								elif q['coord_type'] == 'S':
									q['coord_type'] = 'SUBJECT COORDINATOR'
								elif q['coord_type'] == 'R':
									q['coord_type'] = 'SEMESTER REGISTRATION COORDINATOR'
								elif q['coord_type'] == 'E':
									q['coord_type'] = 'EXTRA ATTENDANCE COORDINATOR'
								elif q['coord_type'] == 'QM':
									q['coord_type'] = 'QUESTION MODERATOR'
								elif q['coord_type'] == 'CO':
									q['coord_type'] = 'CO COORDINATOR'
								elif q['coord_type'] == 'COE':
									q['coord_type'] = 'EXAM COORDINATOR'
								elif q['coord_type'] == 'UVE':
									q['coord_type'] = 'UNIVERSITY MARKS COORDINATOR'

							data_values = {'data': list(qry_coord)}

							status = 200

				else:
					status = 403
			else:
				status = 502
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def SemRegistration(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'R' in request.session['Coordinator_type']:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				studentSession = generate_session_table_name("studentSession_", session_name)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						course = get_coordinator_course(request.session['hash1'], 'R', session_name)
						status = 200
						data_values = {'course': course, 'coord_type': 'R'}
				elif request.method == 'POST':
					data = json.loads(request.body)
					uniq_id = data['uniq_id']
					lock_status = data['lock_status']
					#######################LOCKING STARTS######################
					section_li = list(studentSession.objects.filter(uniq_id=uniq_id).values_list('section', flat=True))
					if check_islocked("REG", section_li, session_name):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################
					q_update = studentSession.objects.filter(uniq_id=uniq_id).update(reg_form_status=lock_status)
					status = 200
					data_values = {'msg': 'Registration form ' + lock_status + ' changed Successfully'}
				elif request.method == 'PUT':
					data = json.loads(request.body)
					uniq_id = data['uniq_id']
					att_start_date = datetime.strptime(str(data['date']).split('T')[0], "%Y-%m-%d").date()
					#######################LOCKING STARTS######################
					section_li = list(studentSession.objects.filter(uniq_id=uniq_id).values_list('section', flat=True))
					if check_islocked("REG", section_li, session_name):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################
					q_update = studentSession.objects.filter(uniq_id=uniq_id).update(att_start_date=att_start_date)
					status = 200
					data_values = {'msg': 'Registration Date Changed Successfully'}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def mark_class_attendance(request):
	# #print(request)
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'A' in request.session['Coordinator_type']:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				emp_id = request.session['hash1']
				Attendance = generate_session_table_name("Attendance_", session_name)
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
				SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
				studentSession = generate_session_table_name("studentSession_", session_name)
				SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						attendance_sub_type = get_class_attendance_type(session)
						course = get_fac_time_course(request.session['hash1'], session_name)
						today_date = str(datetime.now().today()).split(' ')[0]
						status = 200
						data_values = {'sub_attendance_type': attendance_sub_type, 'course': course, 'today_date': today_date}

					elif request.GET['request_type'] == 'form_data_new':
						attendance_sub_type = get_class_attendance_type(session)
						course = get_fac_all_course(request.session['hash1'], session_name)
						today_date = str(datetime.now().today()).split(' ')[0]
						status = 200
						data_values = {'sub_attendance_type': attendance_sub_type, 'course': course, 'today_date': today_date}

				elif(request.method == 'POST'):
					data = json.loads(request.body)
					remark = {}
					try:
						remark = data['remark']
					except:
						remark = None
					lecture = set(data['lecture'])
					date = datetime.strptime(str(data['date']).split('T')[0], "%Y-%m-%d").date()
					att_type = data['att_type']
					section = data['section']
					subject_id = data['subject_id']
					group_id = data['group_id']
					isgroup = data['isgroup']
					present = data['present_students']
					all_uniq = {}
					app = data['app']
					approval_status = 'APPROVED'
					lesson_plan_flag = 0
					flag_marked = False

					q_att_type = list(StudentAcademicsDropdown.objects.filter(sno=att_type).values('value'))
					###to check if lesson plan exists######
					if q_att_type[0]['value'] == "NORMAL" or q_att_type[0]['value'] == "TUTORIAL":
						q_sub_type = list(SubjectInfo.objects.filter(id=subject_id).values('subject_type__value'))
						if q_sub_type[0]['subject_type__value'] == "THEORY" or q_sub_type[0]['subject_type__value'] == "ELECTIVE/SPECIALIZATION":
							topic = data['topic']
							if isgroup == 'N':
								extra_filter = {'propose_detail__lesson_propose__section': section}
							else:
								extra_filter = {'propose_detail__lesson_propose__group_id': group_id}
							temp_variable = lp.lesson_plan_views.check_lesson_plan_exists(session_name, session, emp_id, topic, subject_id, extra_filter, att_type)
							if temp_variable == 0:
								status = 202
								data_values = {'msg': "Could not mark attendance, No Lesson Plan defined for given topics"}
								return JsonResponse(data=data_values, status=status)
							else:
								lesson_plan_flag = 1

					#########################################

					if isgroup == 'N':
						for lec in lecture:
							check = checkIsAttendanceAlreadyMarked(lec, section, None, date, session_name)
							if check['already_marked']:
								flag_marked = True
								status = 202
								data_values = {'msg': check['msg']}
								break

						if not flag_marked:
							q_sec_det = Sections.objects.filter(section_id=section).exclude(status='DELETE').values('sem_id__sem', 'sem_id__dept__course')
							year = math.ceil(q_sec_det[0]['sem_id__sem'] / 2.0)
							course = q_sec_det[0]['sem_id__dept__course']

							q_att_details = AttendanceSettings.objects.filter(session=session, year=year, att_sub_cat=att_type, course=course).exclude(status="DELETE").values('att_to_be_approved', 'att_sub_cat__value')

							if len(q_att_details) > 0:
								if q_att_details[0]['att_to_be_approved'] == 'Y':
									approval_status = 'PENDING'

							sec = []
							sec.append(section)
							section_students = get_section_students(sec, {}, session_name)

							all_uniq_id = set()

							for ss in section_students[0]:
								all_uniq_id.add(ss['uniq_id'])

							uniq_present = set(present)
							uniq_absent = set(all_uniq_id.difference(uniq_present))

							for single_uniq_id in all_uniq_id:
								all_uniq[single_uniq_id] = None

							try:
								for uniq in remark:
									all_uniq[int(uniq)] = remark[uniq]
							except:
								pass

							for lec in lecture:
								################ CHANGE ON 24.07.2019 VRINDA#####################
								is_remedial = False
								if len(q_att_details) > 0:
									normal_att_details = q_att_details[0]['att_sub_cat__value'][0].upper()
									check_data = q_att_details[0]['att_sub_cat__value'].upper()
									# print(check_data,"asdasd")
									if 'DOUBT CLEARING ATTENDANCE' in check_data or 'IMPROVEMENT' in check_data:
										# print("AYA")
										normal_att_details = "R"
										is_remedial = True

								else:
									normal_att_details = 'N'

								Attendance.objects.filter(lecture=lec, date=date, section=section, app=app, subject_id=subject_id, isgroup=isgroup, emp_id=request.session['hash1'], normal_remedial=normal_att_details, status="INSERT").update(status="DELETE", constrain_key=str(time.time()))

								q_att_insert = Attendance.objects.create(lecture=lec, date=date, section=Sections.objects.get(section_id=section), app=app, subject_id=SubjectInfo.objects.get(id=subject_id), isgroup=isgroup, emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), normal_remedial=normal_att_details)

								#################################################################
								#print(q_att_insert.id, att_type, approval_status, 'ttttt')
								present_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='P', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), approval_status=approval_status, marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), remark=all_uniq[uniq]) for uniq in uniq_present)
								q_pres_ins = StudentAttStatus.objects.bulk_create(present_objs)

								if not is_remedial:
									absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='A', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), approval_status='APPROVED', marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), remark=all_uniq[uniq]) for uniq in uniq_absent)
									q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)

								#############lesson plan insert###################
								if lesson_plan_flag == 1:
									q_lesson_plan_insert = lp.lesson_plan_views.completed_lesson_plan(q_att_insert.id, session_name, session, emp_id, topic)
									if q_lesson_plan_insert == 202:
										data_values = {'msg': "Oh Snap lesson plan could not be synced! Please delete the attendance and mark again"}
										return JsonResponse(data=data_values, status=status)
								#########################################################
							status = 200
							data_values = {'msg': 'Attendance Successfully marked'}
					else:
						group_section = get_group_sections(group_id, session_name)
						for gs in group_section:
							for lec in lecture:
								check = checkIsAttendanceAlreadyMarked(lec, gs, group_id, date, session_name)
								if check['already_marked']:
									flag_marked = True
									status = 202
									data_values = {'msg': check['msg']}
									break

							if flag_marked:
								break

						if not flag_marked:
							group_students = get_att_group_students(group_id, session_name)

							for group_section_id, group_student_section in zip(group_section, group_students):
								q_sec_det = Sections.objects.filter(section_id=group_section_id).exclude(status='DELETE').values('sem_id__sem', 'sem_id__dept__course')
								year = math.ceil(q_sec_det[0]['sem_id__sem'] / 2.0)
								course = q_sec_det[0]['sem_id__dept__course']

								q_att_details = AttendanceSettings.objects.filter(session=session, year=year, att_sub_cat=att_type, course=course).exclude(status="DELETE").values('att_to_be_approved', 'att_sub_cat__value')
								if len(q_att_details) > 0:
									if q_att_details[0]['att_to_be_approved'] == 'Y':
										approval_status = 'PENDING'

								all_uniq_id = set()
								for ss in group_student_section:
									all_uniq_id.add(ss['uniq_id'])

								uniq_present = set(studentSession.objects.filter(section=group_section_id, uniq_id__in=present).values_list('uniq_id', flat=True))

								uniq_absent = set(all_uniq_id.difference(uniq_present))

								for uniq in all_uniq_id:
									all_uniq[uniq] = None

								try:
									for uniq in remark:
										all_uniq[int(uniq)] = remark[uniq]
								except:
									pass

								remedial = False
								if len(q_att_details) > 0:
									normal_att_details = q_att_details[0]['att_sub_cat__value'][0].upper()
									check_data = q_att_details[0]['att_sub_cat__value'].upper()
									if 'DOUBT CLEARING ATTENDANCE' in check_data or 'IMPROVEMENT' in check_data:
										normal_att_details = "R"
										remedial = True
								else:
									normal_att_details = 'N'

								for lec in lecture:

									########## CHANGE ON 08.09.2019 DHRUV #######################
									# Added query to change status of already marked attendance
									Attendance.objects.filter(lecture=lec, date=date, section=group_section_id, app=app, subject_id=subject_id, isgroup=isgroup, emp_id=request.session['hash1'], group_id=group_id, normal_remedial=normal_att_details, status="INSERT").update(status="DELETE", constrain_key=str(time.time()))
									### END ####### CHANGE ON 08.09.2019 DHRUV ##################

									q_att_insert = Attendance.objects.create(lecture=lec, date=date, section=Sections.objects.get(section_id=group_section_id), app=app, subject_id=SubjectInfo.objects.get(id=subject_id), isgroup=isgroup, emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), group_id=SectionGroupDetails.objects.get(id=group_id), normal_remedial=normal_att_details)

									##############################################################
									present_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='P', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), approval_status=approval_status, marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), remark=all_uniq[uniq]) for uniq in uniq_present)

									q_pres_ins = StudentAttStatus.objects.bulk_create(present_objs)

									if not remedial:
										absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='A', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), approval_status='APPROVED', marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), remark=all_uniq[uniq]) for uniq in uniq_absent)
										q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)

									#############lesson plan insert###################
									if lesson_plan_flag == 1:
										q_lesson_plan_insert = lp.lesson_plan_views.completed_lesson_plan(q_att_insert.id, session_name, session, emp_id, topic)
										if q_lesson_plan_insert == 202:
											data_values = {'msg': "Oh Snap lesson plan could not be synced! Please delete the attendance and mark again"}
											status = 202
											return JsonResponse(data=data_values, status=status)
									#########################################################
								status = 200
								data_values = {'msg': 'Attendance Successfully marked'}
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def mark_extra_attendance(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			check2 = checkpermission(request, [1371])
			if (check == 200 and 'E' in request.session['Coordinator_type']) or check2 == 200:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				Attendance = generate_session_table_name("Attendance_", session_name)
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
				StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
				studentSession = generate_session_table_name("studentSession_", session_name)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						course = get_coordinator_course(request.session['hash1'], 'E', session_name)
						today_date = str(datetime.now().today()).split(' ')[0]
						emps = get_filtered_emps('ALL')
						status = 200
						data_values = {'course': course, 'today_date': today_date, 'coord_type': 'E', 'emps': emps}

					elif request.GET['request_type'] == 'view_previous':
						section = request.GET['section']

						class_att_type = get_class_attendance_type(session)
						att_type_li = []
						for att in class_att_type:
							att_type_li.append(att['sno'])

						query_view_select = AttendanceSettings.objects.exclude(att_sub_cat__sno__in=att_type_li).exclude(status='DELETE').values_list('att_sub_cat__sno', flat=True).distinct()

						query_extra_att_approve = list(StudentAttStatus.objects.filter(att_type__in=query_view_select, att_id__section=section).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id', 'att_type', 'att_category', 'approval_status').order_by('-att_id').distinct())

						data_values = []
						i = 0

						for q in query_extra_att_approve:

							q_details = StudentAttStatus.objects.filter(att_id=q['att_id'], att_type=q['att_type'], att_category=q['att_category'], att_id__section=section, approval_status=q['approval_status']).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('uniq_id__section__dept__course__value', 'uniq_id__sem__sem', 'uniq_id__section__dept__dept__value', 'uniq_id__section__section', 'att_id', 'att_id__date', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_alpha_code', 'id', 'att_id__subject_id__sub_name', 'att_id__lecture', 'marked_by__name', 'att_type__field', 'att_type__value', 'approval_status', 'att_category__value', 'recommended_by__name', 'approved_by__name', 'remark', 'att_type', 'att_category')
							data_values.append(q_details[0])

							q_students = StudentAttStatus.objects.filter(att_id=q['att_id'], att_type=q['att_type'], att_category=q['att_category'], att_id__section=section, approval_status=q['approval_status']).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__section__dept__course__value', 'uniq_id__sem__sem', 'uniq_id__section__dept__dept__value', 'uniq_id__section__section', 'att_id', 'att_id__date', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_alpha_code', 'id', 'att_id__subject_id__sub_name', 'att_id__lecture', 'uniq_id__class_roll_no', 'marked_by__name', 'att_type__field', 'att_type__value', 'approval_status', 'remark', 'uniq_id__uniq_id__lib_id', 'uniq_id__section__section')

							data_values[i]['student'] = []
							att_data = q_students[0]
							for q2 in q_students:
								data_values[i]['student'].append({'uniq_id__name': q2['uniq_id__uniq_id__name'], 'class_roll_no': q2['uniq_id__class_roll_no'], 'id': q2['id'], 'status': q2['approval_status'], 'uniq_id__uni_roll_no': q2['uniq_id__uniq_id__uni_roll_no'], 'uniq_id__dept_detail__dept__value': q2['uniq_id__section__dept__dept__value'], 'uniq_id__lib_id': q2['uniq_id__uniq_id__lib_id'], 'section__section': q2['uniq_id__section__section'], 'uniq_id': q2['uniq_id'], 'checked': True})
							i += 1

						data_values = {'data': data_values}
						status = 200

					elif request.GET['request_type'] == 'get_students':
						section = request.GET['section']
						att_cnt = request.GET['att_cnt']
						att_type = request.GET['att_type']
						lecture = request.GET['lecture'].split(',')
						fdate = datetime.strptime(str(request.GET['date']), "%Y-%m-%d").date()

						qry_course_year = Sections.objects.filter(section_id=section).values('sem_id__dept__course', 'sem_id__sem')
						course = qry_course_year[0]['sem_id__dept__course']
						if sem_type == 'even':
							year = int(math.ceil(qry_course_year[0]['sem_id__sem']) // 2)
						else:
							year = int(math.ceil(qry_course_year[0]['sem_id__sem']) // 2) + 1
						if checkIsAttendanceLocked(course, request.session['hash1'], fdate, att_type, session, year, section, session_name, {}):

							return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

						if att_cnt == 'L':
							lecture = request.GET['lecture'].split(',')
							date = datetime.strptime(str(request.GET['date']).split('T')[0], "%Y-%m-%d").date()
							section_students = get_section_students(section.split(','), {}, session_name)
							sec_stu_uni_li = []
							for stu in section_students[0]:
								stu['checked'] = False
								stu['present_status'] = 'A'

								sec_stu_uni_li.append(stu['uniq_id'])

							query_stu_present = StudentAttStatus.objects.filter(uniq_id__in=sec_stu_uni_li, att_id__date=date, att_id__section=section, att_id__lecture__in=lecture, present_status='P').exclude(approval_status='REJECTED').exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values_list('uniq_id', flat=True)

							for stu in section_students[0]:
								if stu['uniq_id'] in query_stu_present:
									#stu['checked'] = True
									stu['present_status'] = 'P'

						elif att_cnt == 'D':
							date = datetime.strptime(str(request.GET['date']).split('T')[0], "%Y-%m-%d").date()
							tdate = datetime.strptime(str(request.GET['tdate']).split('T')[0], "%Y-%m-%d").date()

							section_students = get_section_students(section.split(','), {}, session_name)
							sec_stu_uni_li = []
							for stu in section_students[0]:
								stu['checked'] = False
								stu['present_status'] = 'A'

								sec_stu_uni_li.append(stu['uniq_id'])

							query_stu_present = StudentAttStatus.objects.filter(uniq_id__in=sec_stu_uni_li, att_id__date__range=[date, tdate], att_id__section=section, present_status='P', att_id__lecture__in=lecture).exclude(approval_status='REJECTED').exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values_list('uniq_id', flat=True)

							for stu in section_students[0]:
								if stu['uniq_id'] in query_stu_present:
									#stu['checked'] = True
									stu['present_status'] = 'P'

						status = 200
						data_values = {'students': section_students}

				elif(request.method == 'POST'):
					data = json.loads(request.body)
					lecture = list(data['lecture'])
					date = datetime.strptime(str(data['date']).split('T')[0], "%Y-%m-%d").date()

					att_type = data['att_type']
					att_cnt = data['att_cnt']
					if 'att_category' in data:
						if data['att_category'] is not None:
							att_category = StudentAcademicsDropdown.objects.get(sno=data['att_category'])
						else:
							att_category = None
					else:
						att_category = None
					section = data['section']
					present = data['present_students']
					app = data['app']

					qry_course_year = Sections.objects.filter(section_id=section).values('sem_id__dept__course', 'sem_id__sem')
					course = qry_course_year[0]['sem_id__dept__course']
					if sem_type == 'even':
						year = int(math.ceil(qry_course_year[0]['sem_id__sem']) // 2)
					else:
						year = int(math.ceil(qry_course_year[0]['sem_id__sem']) // 2) + 1
					if checkIsAttendanceLocked(course, request.session['hash1'], date, att_type, session, year, section, session_name, {}):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					approval_status = 'APPROVED'
					q_sec_det = Sections.objects.filter(section_id=section).exclude(status='DELETE').values('sem_id__sem', 'sem_id__dept__course')
					year = math.ceil(q_sec_det[0]['sem_id__sem'] / 2.0)
					course = q_sec_det[0]['sem_id__dept__course']

					q_att_details = AttendanceSettings.objects.filter(session=session, year=year, att_sub_cat=att_type, attendance_category=att_category, course=course).exclude(status="DELETE").values('att_to_be_approved')
					if len(q_att_details) > 0:
						if q_att_details[0]['att_to_be_approved'] == 'Y':
							approval_status = 'PENDING'

					if att_cnt == 'L':
						query_att_id = StudentAttStatus.objects.filter(att_id__date=date, att_id__section=section, att_id__lecture__in=lecture).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values_list('att_id', flat=True).distinct()
						for att_id in query_att_id:
							query_att_id_stu_uniq = list(StudentAttStatus.objects.filter(uniq_id__in=present, att_id__date=date, att_id__section=section, att_id__lecture__in=lecture, present_status='A', att_id=att_id).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values_list('uniq_id', flat=True).distinct())

							if approval_status == 'APPROVED':
								q_update_status = StudentAttStatus.objects.filter(att_id=att_id, uniq_id__in=query_att_id_stu_uniq).exclude(status__contains='DELETE').update(status='DELETE')

							present_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=att_id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='P', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), att_category=att_category, approval_status=approval_status, marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), recommended_by=EmployeePrimdetail.objects.get(emp_id=data['recommended_by']), approved_by=EmployeePrimdetail.objects.get(emp_id=data['approved_by']), remark=data['remark']) for uniq in query_att_id_stu_uniq)

							q_pres_ins = StudentAttStatus.objects.bulk_create(present_objs)

					elif att_cnt == 'D':
						tdate = datetime.strptime(str(data['tdate']).split('T')[0], "%Y-%m-%d").date()

						query_stu = StudentAttStatus.objects.filter(uniq_id__in=present, att_id__date__range=[date, tdate], att_id__section=section, present_status='A', att_id__lecture__in=lecture).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values_list('uniq_id', flat=True).distinct()
						for uniq in list(query_stu):
							q_stu_group = (StuGroupAssign.objects.filter(uniq_id=uniq).exclude(status='DELETE').values_list('group_id', flat=True))

							query_att_id = StudentAttStatus.objects.filter(uniq_id=uniq, att_id__date__range=[date, tdate], att_id__section=section, present_status='A', att_id__lecture__in=lecture).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values_list('att_id', flat=True).distinct()

							for att_id in query_att_id:
								if approval_status == 'APPROVED':
									q_update_status = StudentAttStatus.objects.filter(att_id=att_id, uniq_id=uniq).exclude(status__contains='DELETE').update(status='DELETE')

								q_present = StudentAttStatus.objects.create(att_id=Attendance.objects.get(id=att_id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='P', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), approval_status=approval_status, marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), recommended_by=EmployeePrimdetail.objects.get(emp_id=data['recommended_by']), approved_by=EmployeePrimdetail.objects.get(emp_id=data['approved_by']), remark=data['remark'])

					status = 200
					data_values = {'msg': 'Attendance Successfully marked'}
				elif request.method == 'PUT':
					data = json.loads(request.body)
					att_id = data['att_id']

					if len(data['absent_students']) > 0:
						qry_course_year = StudentAttStatus.objects.filter(att_id=att_id, uniq_id=data['absent_students'][0]['uniq_id']).exclude(status__contains='DELETE').values('att_id__section', 'att_id__section__sem_id__sem', 'att_id__section__sem_id__dept__course', 'att_id__date', 'att_type').order_by('-id')[:1]

						course = qry_course_year[0]['att_id__section__sem_id__dept__course']
						section = qry_course_year[0]['att_id__section']
						att_type = qry_course_year[0]['att_type']

						if sem_type == 'even':
							year = int(math.ceil(qry_course_year[0]['att_id__section__sem_id__sem']) // 2)
						else:
							year = int(math.ceil(qry_course_year[0]['att_id__section__sem_id__sem']) // 2) + 1

						if checkIsAttendanceLocked(course, request.session['hash1'], qry_course_year[0]['att_id__date'], att_type, session, year, section, session_name, {}):
							return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					students = data['absent_students']

					class_att_type = get_class_attendance_type(session)
					att_type_li = []
					for att in class_att_type:
						att_type_li.append(att['sno'])

					for stu in students:
						q_update = StudentAttStatus.objects.filter(att_id=att_id, uniq_id=stu['uniq_id']).exclude(status__contains='DELETE').update(status='DELETE')

						q_get_last_normal = StudentAttStatus.objects.filter(att_id=att_id, uniq_id=stu['uniq_id']).filter(att_type__in=att_type_li).values('present_status', 'att_type', 'approval_status', 'marked_by', 'time_stamp', 'remark').order_by('-id')[:1]

						q_ins = StudentAttStatus.objects.create(att_id=Attendance.objects.get(id=att_id), uniq_id=studentSession.objects.get(uniq_id=stu['uniq_id']), present_status=q_get_last_normal[0]['present_status'], att_type=StudentAcademicsDropdown.objects.get(sno=q_get_last_normal[0]['att_type']), approval_status=q_get_last_normal[0]['approval_status'], marked_by=EmployeePrimdetail.objects.get(emp_id=q_get_last_normal[0]['marked_by']), remark=q_get_last_normal[0]['remark'])

					status = 200
					data_values = {'msg': 'Attendance Successfully Updated'}
				elif request.method == 'DELETE':
					data = json.loads(request.body)
					att_type = data['att_type']
					att_category = data['att_category']
					att_id = data['att_id']

					qry_course_year = StudentAttStatus.objects.filter(att_id=att_id).values('att_id__section', 'att_id__section__sem_id__sem', 'att_id__section__sem_id__dept__course', 'att_id__date')

					course = qry_course_year[0]['att_id__section__sem_id__dept__course']
					section = qry_course_year[0]['att_id__section']

					if sem_type == 'even':
						year = int(math.ceil(qry_course_year[0]['att_id__section__sem_id__sem']) // 2)
					else:
						year = int(math.ceil(qry_course_year[0]['att_id__section__sem_id__sem']) // 2) + 1

					if checkIsAttendanceLocked(course, request.session['hash1'], qry_course_year[0]['att_id__date'], att_type, session, year, section, session_name, {}):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					q_del_extra = StudentAttStatus.objects.filter(att_id=att_id, att_type=att_type, att_category=att_category, approval_status='PENDING').exclude(status__contains='DELETE').update(status='DELETE')

					status = 200
					data_values = {'msg': 'Attendance Successfully Deleted'}
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def approve_extra_attendance(request):
	data_values = {}
	present = []
	absent = []
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371])
			if check == 200:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				today_date = str(datetime.now().today()).split(' ')[0]
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

				if (request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						query_extra_att_approve = list(StudentAttStatus.objects.filter(approval_status='PENDING').exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').order_by('-att_id').distinct())

						data_values = []
						i = 0
						for q in query_extra_att_approve:
							q_details = StudentAttStatus.objects.filter(approval_status='PENDING', att_id=q['att_id']).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('uniq_id__section__dept__course__value', 'uniq_id__sem__sem', 'uniq_id__section__dept__dept__value', 'uniq_id__section__section', 'att_id', 'att_id__date', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_alpha_code', 'id', 'att_id__subject_id__sub_name', 'att_id__lecture', 'marked_by__name', 'att_type__field', 'att_type__value', 'att_category__value', 'approved_by__name', 'recommended_by__name', 'remark')
							data_values.append(q_details[0])

							q_students = StudentAttStatus.objects.filter(approval_status='PENDING', att_id=q['att_id']).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('uniq_id__uniq_id__name', 'uniq_id__section__dept__course__value', 'uniq_id__sem__sem', 'uniq_id__section__dept__dept__value', 'uniq_id__section__section', 'att_id', 'att_id__date', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_alpha_code', 'id', 'att_id__subject_id__sub_name', 'att_id__lecture', 'uniq_id__class_roll_no', 'marked_by__name', 'att_type__field', 'att_type__value', 'att_category__value', 'approved_by__name', 'recommended_by__name', 'remark')

							data_values[i]['student'] = []
							att_data = q_students[0]
							for q2 in q_students:
								data_values[i]['student'].append({'name': q2['uniq_id__uniq_id__name'], 'class_roll_no': q2['uniq_id__class_roll_no'], 'id': q2['id']})
							i += 1

						data_values = {'data': data_values}
						status = 200
					elif request.GET['request_type'] == 'view_previous':
						class_att_type = get_class_attendance_type(session)
						att_type_li = []
						for att in class_att_type:
							att_type_li.append(att['sno'])
						query_view_select = AttendanceSettings.objects.filter(att_to_be_approved='Y',session=session).exclude(status__contains='DELETE').values_list('att_sub_cat__sno', flat=True).distinct()
						query_extra_att_approve = StudentAttStatus.objects.filter(att_type__in=query_view_select).exclude(approval_status='PENDING').exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').order_by('-att_id').distinct()

						data_values = []
						i = 0

						for q in query_extra_att_approve:

							q_details = StudentAttStatus.objects.filter(att_id=q['att_id'], att_type__in=query_view_select).exclude(approval_status='PENDING').exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('uniq_id__section__dept__course__value', 'uniq_id__sem__sem', 'uniq_id__section__dept__dept__value', 'uniq_id__section__section', 'att_id', 'att_id__date', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_alpha_code', 'id', 'att_id__subject_id__sub_name', 'att_id__lecture', 'marked_by__name', 'att_type__field', 'att_type__value', 'approval_status', 'approved_by__name', 'recommended_by__name', 'att_category__value', 'remark')
							data_values.append(q_details[0])

							q_students = StudentAttStatus.objects.filter(att_id=q['att_id'], att_type__in=query_view_select).exclude(approval_status='PENDING').exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('uniq_id__uniq_id__name', 'uniq_id__section__dept__course__value', 'uniq_id__sem__sem', 'uniq_id__section__dept__dept__value', 'uniq_id__section__section', 'att_id', 'att_id__date', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_alpha_code', 'id', 'att_id__subject_id__sub_name', 'att_id__lecture', 'uniq_id__class_roll_no', 'marked_by__name', 'att_type__field', 'att_type__value', 'approved_by__name', 'recommended_by__name', 'att_category__value', 'remark')

							data_values[i]['student'] = []
							att_data = q_students[0]
							for q2 in q_students:
								data_values[i]['student'].append({'name': q2['uniq_id__uniq_id__name'], 'class_roll_no': q2['uniq_id__class_roll_no'], 'id': q2['id']})
							i += 1

						data_values = {'data': data_values}
						status = 200

				elif (request.method == 'POST'):
					data = json.loads(request.body)

					qry_sections = list(Sections.objects.values_list('section_id', flat=True))

					if check_islocked('DEAN', qry_sections, session_name):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					marked = data['id']
					query = StudentAttStatus.objects.filter(id__in=marked).values('att_id', 'uniq_id', 'id')
					if data['approval_status'] != 'REJECTED':
						for id in query:
							query_update_previous = StudentAttStatus.objects.filter(att_id=id['att_id'], uniq_id=id['uniq_id']).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').exclude(approval_status='PENDING ').update(status="DELETE")
					if len(data['id']) > 0:
						query_update = StudentAttStatus.objects.filter(id__in=marked).update(approval_status=data['approval_status'])

						data_values = {'msg': 'Attendance Successfully Updated'}
					else:
						data_values = {'msg': 'Error'}
					status = 200
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status)


def update_class_attendance(request):
	# #print(request)
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369])
			if check == 200 and 'A' in request.session['Coordinator_type']:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']

				Attendance = generate_session_table_name("Attendance_", session_name)
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
				studentSession = generate_session_table_name("studentSession_", session_name)
				SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
				SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)

				if request.method == "DELETE":
					data = json.loads(request.body)
					emp_id = request.session['hash1']
					att_id = data['att_id']
					qry_att = Attendance.objects.filter(id=att_id).values('section__sem_id__dept__course', 'date', 'section')
					class_att_type = get_class_attendance_type(session)

					att_type_li = []
					for att in class_att_type:
						att_type_li.append(att['sno'])

					qry_att_type = StudentAttStatus.objects.filter(att_id=att_id, att_type__in=att_type_li).exclude(status='DELETE').values('att_type', 'uniq_id__year')

					if len(qry_att_type) == 0:
						att_tp = -1
						year = -1
					else:
						att_tp = qry_att_type[0]['att_type']
						year = qry_att_type[0]['uniq_id__year']

					flag_locked = checkIsAttendanceLocked(qry_att[0]['section__sem_id__dept__course'], request.session['hash1'], qry_att[0]['date'], att_tp, session, year, qry_att[0]['section'], session_name, {})
					flag_locked = False

					if flag_locked:
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.', 'error': True}, status=202)

					q_del = Attendance.objects.filter(id=att_id).update(status='DELETE', constrain_key=str(time.time()))
					qry_del = StudentAttStatus.objects.filter(att_id=att_id).update(status="DELETE")

					############delete completed lesson plan###########
					q_del_lesson_plan = lp.lesson_plan_views.delete_lesson_plan_completed(session_name, session, emp_id, att_id)
					###################################################

					# att_det = {}
					# q_att_details = Attendance.objects.filter(id=att_id).values('date', 'lecture', 'section', 'subject_id', 'emp_id', 'group_id', 'normal_remedial', 'isgroup', 'app')

					# att_det['date'] = q_att_details[0]['date']

					# att_det['lecture'] = q_att_details[0]['lecture']

					# att_det['normal_remedial'] = q_att_details[0]['normal_remedial']

					# att_det['normal_remedial'] = q_att_details[0]['normal_remedial']

					# att_det['isgroup'] = q_att_details[0]['isgroup']

					# att_det['app'] = q_att_details[0]['app']

					# att_det['section'] = Sections.objects.get(section_id=q_att_details[0]['section'])

					# att_det['subject_id'] = SubjectInfo.objects.get(id=q_att_details[0]['subject_id'])

					# att_det['emp_id'] = EmployeePrimdetail.objects.get(emp_id=q_att_details[0]['emp_id'])

					# if q_att_details[0]['group_id'] is not None:
					#     att_det['group_id'] = SectionGroupDetails.objects.get(id=q_att_details[0]['group_id'])

					# att_det['status'] = 'DELETE'

					# q_status_details = StudentAttStatus.objects.filter(att_id=att_id).values('att_id', 'uniq_id', 'present_status', 'att_type', 'att_category', 'approval_status', 'marked_by', 'recommended_by', 'approved_by', 'remark')

					# q_att_insert = Attendance.objects.create(**att_det)

					# att_id = q_att_insert.id

					# for status in q_status_details:
					#     if status['att_type'] is not None:
					#         status['att_type'] = StudentAcademicsDropdown.objects.get(sno=status['att_type'])
					#     if status['att_category'] is not None:
					#         status['att_category'] = StudentAcademicsDropdown.objects.get(sno=status['att_category'])
					#     if status['recommended_by'] is not None:
					#         status['recommended_by'] = EmployeePrimdetail.objects.get(emp_id=status['recommended_by'])
					#     if status['approved_by'] is not None:
					#         status['approved_by'] = EmployeePrimdetail.objects.get(emp_id=status['approved_by'])

					#     status['att_id'] = Attendance.objects.get(id=att_id)
					#     status['uniq_id'] = studentSession.objects.get(uniq_id=status['uniq_id'])
					#     status['marked_by'] = EmployeePrimdetail.objects.get(emp_id=status['marked_by'])
					#     status['status'] = 'DELETE'

					# objs = (StudentAttStatus(**status) for status in q_status_details)

					# StudentAttStatus.objects.bulk_create(objs)

					status = 200
					data_values = {'msg': 'Attendance Successfully Deleted', 'error': False}

				elif(request.method == 'PUT'):
					data = json.loads(request.body)

					if 'request_by' in data:
						if data['request_by'] == 'dean':
							att_id = data['att_id']
							present = data['present_students']
							absent_ids = list(StudentAttStatus.objects.filter(present_status='A', att_id=att_id, uniq_id__in=present).exclude(status__contains='DELETE').values_list('id', flat=True))
							update_present = StudentAttStatus.objects.filter(id__in=absent_ids).update(present_status='P', approval_status='APPROVED', marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
							status = 200
							data_values = {'msg': 'Attendance Successfully Updated'}
							return JsonResponse(data=data_values, status=status)

					approval_status = 'APPROVED'
					att_id = data['att_id']
					present = data['present_students']

					status_update = 'DELETE'

					qry_att = Attendance.objects.filter(id=att_id).values('date', 'lecture', 'section', 'subject_id', 'group_id', 'normal_remedial', 'isgroup', 'section__sem_id__dept__course')

					class_att_type = get_class_attendance_type(session)

					att_type_li = []
					for att in class_att_type:
						att_type_li.append(att['sno'])

					qry_att_type = StudentAttStatus.objects.filter(att_id=att_id, att_type__in=att_type_li).exclude(status='DELETE').values('att_type', 'uniq_id__year')

					if len(qry_att_type) == 0:
						att_tp = -1
						year = -1
					else:
						att_tp = qry_att_type[0]['att_type']
						year = qry_att_type[0]['uniq_id__year']

					flag_locked = checkIsAttendanceLocked(qry_att[0]['section__sem_id__dept__course'], request.session['hash1'], qry_att[0]['date'], att_tp, session, year, qry_att[0]['section'], session_name, {})
					if flag_locked and not (checkpermission(request, [1371]) == 200):
						return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)

					isgroup = qry_att[0]['isgroup']
					section = qry_att[0]['section']

					qry_type = StudentAttStatus.objects.filter(att_id=att_id, att_type__in=att_type_li).values('att_type')
					# print(att_type_li)
					att_type = qry_type[0]['att_type']

					group_id = qry_att[0]['group_id']

					if group_id is not None:
						group_id = SectionGroupDetails.objects.get(id=qry_att[0]['group_id'])

					extra_att_uniq_id = StudentAttStatus.objects.filter(att_id=att_id).exclude(att_type__in=att_type_li).exclude(status__contains='DELETE').filter(approval_status__in=['APPROVED', 'PENDING']).values_list('uniq_id', flat=True)

					q_extra_att = list(extra_att_uniq_id)[:]

					extra_att_details = (StudentAttStatus.objects.filter(att_id=att_id).exclude(att_type__in=att_type_li).exclude(status__contains='DELETE').filter(approval_status__in=['APPROVED', 'PENDING']).values('uniq_id', 'present_status', 'att_type', 'att_category', 'approval_status', 'recommended_by', 'approved_by', 'remark'))

					extra_att_details = list(extra_att_details)

					q_sec_det = Sections.objects.filter(section_id=section).exclude(status='DELETE').values('sem_id__sem', 'sem_id__dept__course')
					year = math.ceil(q_sec_det[0]['sem_id__sem'] / 2.0)
					course = q_sec_det[0]['sem_id__dept__course']

					q_att_details = AttendanceSettings.objects.filter(session=session, year=year, att_sub_cat=att_type, course=course).exclude(status="DELETE").values('att_to_be_approved', 'att_sub_cat__value')
					if len(q_att_details) > 0:
						if q_att_details[0]['att_to_be_approved'] == 'Y':
							approval_status = 'PENDING'

					total_students = (StudentAttStatus.objects.filter(att_id=att_id).exclude(status__contains="DELETE").values_list('uniq_id', flat=True))

					student_data = get_students_data_from_uniq_id(total_students, session_name)

					all_uniq_id = []
					for ss in student_data:
						all_uniq_id.append(ss['uniq_id'])

					qry_del = StudentAttStatus.objects.filter(att_id=att_id).update(status=status_update)

					## CHANGE ADDED constrain_key IN UPDATE QUERY: DATE - 08/09/2019 ######################
					qry_del2 = Attendance.objects.filter(id=att_id).update(status=status_update, constrain_key=str(time.time()))
					# END # CHANGE ADDED constrain_key IN UPDATE QUERY: DATE - 08/09/2019 #################

					q_ins_att = Attendance.objects.create(lecture=qry_att[0]['lecture'], date=qry_att[0]['date'], section=Sections.objects.get(section_id=qry_att[0]['section']), subject_id=SubjectInfo.objects.get(id=qry_att[0]['subject_id']), isgroup=isgroup, emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), normal_remedial=qry_att[0]['normal_remedial'], app=data['app'], group_id=group_id)
					##########update lesson plan att id#############
					q_update_lesson_plan_detail = lp.lesson_plan_views.update_lesson_plan(att_id, session_name, q_ins_att.id)
					################################################
					att_id = q_ins_att.id

					uniq_present = list(set(present) - set(q_extra_att))
					uniq_absent = list(set(all_uniq_id) - set(uniq_present) - set(q_extra_att))

					present_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=att_id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='P', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), approval_status=approval_status, marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), status='UPDATE') for uniq in uniq_present)

					q_pres_ins = StudentAttStatus.objects.bulk_create(present_objs)

					if len(q_att_details) > 0:
						if q_att_details[0]['att_sub_cat__value'] != 'DOUBT CLEARING ATTENDANCE':
							absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=att_id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='A', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), approval_status=approval_status, marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), status='UPDATE') for uniq in uniq_absent)
							q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)
					else:
						absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=att_id), uniq_id=studentSession.objects.get(uniq_id=uniq), present_status='A', att_type=StudentAcademicsDropdown.objects.get(sno=att_type), approval_status=approval_status, marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), status='UPDATE') for uniq in uniq_absent)
						q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)

					i_data = []
					for att in extra_att_details:
						insert_data = {}
						insert_data['att_id'] = Attendance.objects.get(id=att_id)
						insert_data['uniq_id'] = studentSession.objects.get(uniq_id=att['uniq_id'])
						insert_data['present_status'] = att['present_status']
						insert_data['approval_status'] = att['approval_status']
						if att['att_type'] is not None:
							insert_data['att_type'] = StudentAcademicsDropdown.objects.get(sno=att['att_type'])
						if att['att_category'] is not None:
							insert_data['att_category'] = StudentAcademicsDropdown.objects.get(sno=att['att_category'])
						else:
							insert_data['att_category'] = None

						if att['recommended_by'] is not None:
							insert_data['recommended_by'] = EmployeePrimdetail.objects.get(emp_id=att['recommended_by'])
						else:
							insert_data['recommended_by'] = None

						if att['approved_by'] is not None:
							insert_data['approved_by'] = EmployeePrimdetail.objects.get(emp_id=att['approved_by'])
						else:
							insert_data['approved_by'] = None

						insert_data['marked_by'] = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
						insert_data['status'] = 'UPDATE'

						i_data.append(insert_data)

					extra_objs = (StudentAttStatus(att_id=att['att_id'], uniq_id=att['uniq_id'], present_status=att['present_status'], att_type=att['att_type'], att_category=att['att_category'], approval_status=att['approval_status'], recommended_by=att['recommended_by'], approved_by=att['approved_by'], marked_by=att['marked_by'], status=att['status']) for att in i_data)
					q_extra_ins = StudentAttStatus.objects.bulk_create(extra_objs)

					status = 200
					data_values = {'msg': 'Attendance Successfully Updated'}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


# def AttendanceRegister(request):
#     data_values = {}
#     status = 403
#     if 'HTTP_COOKIE' in request.META:
#         if request.user.is_authenticated:
#             check = checkpermission(request, [1369, 1371, 425, 337, 319, 1372])
#             if check == 200 and ('A' in request.session['Coordinator_type'] or 'H' in request.session['Coordinator_type']):
#                 query = []
#                 session = request.session['Session_id']
#                 session_name = request.session['Session_name']
#                 sem_type = request.session['sem_type']
#                 Attendance = generate_session_table_name("Attendance_", session_name)
#                 StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
#                 SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

#                 if(request.method == 'GET'):
#                     if request.GET['request_type'] == 'att_register_data':
#                         section = request.GET['section']
#                         subject = request.GET['subject']

#                         if 'emp_id' in request.GET:
#                             emp_id = request.GET['emp_id']
#                         else:
#                             emp_id = request.session['hash1']

#                         if 'group_id' in request.GET:
#                             group_id = request.GET['group_id']
#                             query_students = get_att_group_students(group_id, session_name)
#                             #print(query_students)
#                         else:
#                             query_students = get_section_students(section.split(','), {}, session_name)

#                         from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
#                         to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
#                         att_type = request.GET['att_type'].split(',')

#                         # all_att = get_attendance_type(session)
#                         # all_att_type = []

#                         # for al in all_att:
#                         #     for d in al['data']:
#                         #         all_att_type.append(d['sno'])

#                         valid_att_id = list(StudentAttStatus.objects.filter(att_id__date__range=[from_date, to_date], att_id__section=section, att_id__subject_id=subject, att_id__emp_id=emp_id, att_type__in=att_type).exclude(status='DELETE').exclude(att_id__status='DELETE').values_list('att_id', flat=True).distinct())

#                         query_section_att = Attendance.objects.filter(id__in=valid_att_id).exclude(status='DELETE').values('id', 'date', 'lecture', 'status').order_by('date', 'lecture', 'id').distinct()

#                         q_sub = SubjectInfo.objects.filter(id=subject).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'session__sem_start', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name').order_by('id')

#                         for stu in query_students[0]:

#                             status = get_student_subject_att_status_emp_wise(stu['uniq_id'], subject, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(stu['att_start_date']), "%Y-%m-%d").date()), to_date, att_type, session_name, emp_id)
#                             stu_att_data = []
#                             present_count = 0
#                             absent_count = 0
#                             total_count = 0
#                             i = 0
#                             count = 0
#                             n = len(status)  # Length of the status of lectures

#                             for date_lec in query_section_att:
#                                 at_status = 'N/A'
#                                 at_type = 'N'
#                                 show = 'N/A'
#                                 if i < n:  # checking status length is not greater than index(i)
#                                     if date_lec['id'] != status[i]['att_id']:  # checking is att_id available in lecture list
#                                         stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})
#                                         continue
#                                 if i < n and status[i]['att_id__date'] == date_lec['date'] and status[i]['att_id__lecture'] == date_lec['lecture']:
#                                     if status[i]['present_status'] == 'P':
#                                         if str(status[i]['att_type']) in att_type:

#                                             if ('NORMAL' in status[i]['att_type__value'] or 'REMEDIAL' in status[i]['att_type__value'] or 'TUTORIAL' in status[i]['att_type__value']):
#                                                 count += 1
#                                                 at_status = 'P'

#                                                 if status[i]['att_id__group_id'] is not None:
#                                                     at_type = 'G'
#                                                 elif 'REMEDIAL' in status[i]['att_type__value']:
#                                                     at_type = 'R'

#                                                 show = count
#                                                 present_count += 1
#                                                 total_count += 1
#                                             elif ('SUBSTITUTE' in status[i]['att_type__value']):
#                                                 count += 1
#                                                 at_status = 'P'
#                                                 show = 'S'
#                                                 at_type = 'S'
#                                                 show = count
#                                                 present_count += 1
#                                                 total_count += 1
#                                             else:
#                                                 at_type = 'E'
#                                                 at_status = 'P'
#                                                 show = 'E'

#                                                 present_count += 1
#                                                 total_count += 1
#                                         else:
#                                             at_status = 'A'
#                                             show = count

#                                             if status[i]['att_id__group_id'] is not None:
#                                                 at_type = 'G'
#                                                 total_count += 1

#                                             elif 'REMEDIAL' in status[i]['att_type__value']:
#                                                 at_type = 'N'

#                                                 at_status = 'N/A'
#                                                 show = 'N/A'
#                                             else:
#                                                 total_count += 1

#                                     else:

#                                         show = count
#                                         at_status = 'A'
#                                         if status[i]['att_id__group_id'] is not None:
#                                             at_type = 'G'
#                                             total_count += 1

#                                         elif 'REMEDIAL' in status[i]['att_type__value']:
#                                             at_type = 'N'
#                                             at_status = 'N/A'
#                                             show = 'N/A'
#                                         else:
#                                             total_count += 1

#                                     stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})

#                                     i += 1
#                                 else:
#                                     stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})

#                             stu['att_data'] = stu_att_data
#                             if total_count == 0:
#                                 percentage = 0
#                             else:
#                                 percentage = round((present_count * 100) / total_count)
#                             stu['net_data'] = {'present_count': present_count, 'absent_count': total_count - present_count, 'total': total_count, 'percentage': percentage}

#                         status = 200
#                         data_values = {'data': query_students[0]}

#                 else:
#                     status = 502
#             else:
#                 status = 403
#         else:
#             status = 401
#     else:
#         status = 500

#     return JsonResponse(data=data_values, status=status)

# def AttendanceRegister(request):
#   data_values = {}
#   status = 403
#   if 'HTTP_COOKIE' in request.META:
#       if request.user.is_authenticated:
#           check = checkpermission(request, [1369, 1371, 425, 337, 319])
#           if check == 200 and ('A' in request.session['Coordinator_type'] or 'H' in request.session['Coordinator_type']):
#               query = []
#               session = request.session['Session_id']
#               session_name = request.session['Session_name']
#               sem_type = request.session['sem_type']
#               Attendance = generate_session_table_name("Attendance_", session_name)
#               StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
#               SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

#               if(request.method == 'GET'):
#                   if request.GET['request_type'] == 'att_register_data':
#                       section = request.GET['section']
#                       subject = request.GET['subject']

#                       if 'emp_id' in request.GET:
#                           emp_id = request.GET['emp_id']
#                       else:
#                           emp_id = request.session['hash1']

#                       if 'group_id' in request.GET:
#                           group_id = request.GET['group_id']
#                           query_students = get_att_group_students_att_register(group_id, session_name)
#                           section = get_group_sections(request.GET['group_id'], session_name)
#                       else:
#                           query_students = get_section_students(section.split(','), {}, session_name)

#                       from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
#                       to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
#                       att_type = request.GET['att_type'].split(',')

#                       # all_att = get_attendance_type(session)
#                       # all_att_type = []

#                       # for al in all_att:
#                       #     for d in al['data']:
#                       #         all_att_type.append(d['sno'])
#                       if 'group_id' in request.GET:
#                           valid_att_id = list(StudentAttStatus.objects.filter(att_id__date__range=[from_date, to_date], att_id__section__in=section, att_id__subject_id=subject, att_id__emp_id=emp_id, att_type__in=att_type,att_id__group_id=group_id).exclude(status='DELETE').exclude(att_id__status='DELETE').values_list('att_id', flat=True).distinct())
#                       else:
#                           valid_att_id = list(StudentAttStatus.objects.filter(att_id__date__range=[from_date, to_date], att_id__section=section, att_id__subject_id=subject, att_id__emp_id=emp_id, att_type__in=att_type,att_id__isgroup='N').exclude(status='DELETE').exclude(att_id__status='DELETE').values_list('att_id', flat=True).distinct())

#                       query_section_att = Attendance.objects.filter(id__in=valid_att_id).exclude(status='DELETE').values('id', 'date', 'lecture', 'status').order_by('date', 'lecture', 'id').distinct()

#                       q_sub = SubjectInfo.objects.filter(id=subject).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'session__sem_start', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name').order_by('id')

#                       for stu in query_students[0]:
#                           status1 = get_student_subject_att_status_emp_wise(stu['uniq_id'], subject, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(stu['att_start_date']), "%Y-%m-%d").date()), to_date, att_type, session_name, emp_id)
#                           stu_att_data = []
#                           present_count = 0
#                           absent_count = 0
#                           total_count = 0
#                           i = 0
#                           count = 0
#                           status=[]
#                           if 'group_id' in request.GET:
#                               for s in status1:
#                                   if s['att_id__group_id'] is not None:
#                                       status.append(s)
#                           else:
#                               for s in status1:
#                                   if s['att_id__group_id'] is None:
#                                       status.append(s)
#                           n = len(status)  # Length of the status of lectures

#                           for date_lec in query_section_att:
#                               at_status = 'N/A'
#                               at_type = 'N'
#                               show = 'N/A'
#                               if i < n:  # checking status length is not greater than index(i)
#                                   if date_lec['id'] != status[i]['att_id']:  # checking is att_id available in lecture list
#                                       stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})
#                                       continue
#                               if i < n and status[i]['att_id__date'] == date_lec['date'] and status[i]['att_id__lecture'] == date_lec['lecture']:
#                                   if status[i]['present_status'] == 'P':
#                                       if str(status[i]['att_type']) in att_type:

#                                           if ('NORMAL' in status[i]['att_type__value'] or 'REMEDIAL' in status[i]['att_type__value'] or 'TUTORIAL' in status[i]['att_type__value']):
#                                               count += 1
#                                               at_status = 'P'

#                                               if status[i]['att_id__group_id'] is not None:
#                                                   at_type = 'G'
#                                               elif 'REMEDIAL' in status[i]['att_type__value']:
#                                                   at_type = 'R'

#                                               show = count
#                                               present_count += 1
#                                               total_count += 1
#                                           elif ('SUBSTITUTE' in status[i]['att_type__value']):
#                                               count += 1
#                                               at_status = 'P'
#                                               show = 'S'
#                                               at_type = 'S'
#                                               show = count
#                                               present_count += 1
#                                               total_count += 1
#                                           else:
#                                               at_type = 'E'
#                                               at_status = 'P'
#                                               show = 'E'

#                                               present_count += 1
#                                               total_count += 1
#                                       else:
#                                           at_status = 'A'
#                                           show = count

#                                           if status[i]['att_id__group_id'] is not None:
#                                               at_type = 'G'
#                                               total_count += 1

#                                           elif 'REMEDIAL' in status[i]['att_type__value']:
#                                               at_type = 'N'

#                                               at_status = 'N/A'
#                                               show = 'N/A'
#                                           else:
#                                               total_count += 1

#                                   else:

#                                       show = count
#                                       at_status = 'A'
#                                       if status[i]['att_id__group_id'] is not None:
#                                           at_type = 'G'
#                                           total_count += 1

#                                       elif 'REMEDIAL' in status[i]['att_type__value']:
#                                           at_type = 'N'
#                                           at_status = 'N/A'
#                                           show = 'N/A'
#                                       else:
#                                           total_count += 1

#                                   stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})

#                                   i += 1
#                               else:
#                                   stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})

#                           stu['att_data'] = stu_att_data
#                           if total_count == 0:
#                               percentage = 0
#                           else:
#                               percentage = round((present_count * 100) / total_count)
#                           stu['net_data'] = {'present_count': present_count, 'absent_count': total_count - present_count, 'total': total_count, 'percentage': percentage}

#                       status = 200
#                       data_values = {'data': query_students[0]}

#               else:
#                   status = 502
#           else:
#               status = 403
#       else:
#           status = 401
#   else:
#       status = 500

#   return JsonResponse(data=data_values, status=status)

def AttendanceRegister(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369, 1371, 425, 337, 319])
			if check == 200 and ('A' in request.session['Coordinator_type'] or 'H' in request.session['Coordinator_type']):
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				Attendance = generate_session_table_name("Attendance_", session_name)
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
				SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

				if(requestMethod.GET_REQUEST(request)):
					if(requestType.custom_request_type(request.GET, 'att_register_data')):
						# print(request.GET,'vrinda')
						section = request.GET['section'].split(',')
						subject = request.GET['subject']

						if 'emp_id' in request.GET:
							emp_id = request.GET['emp_id']
						else:
							emp_id = request.session['hash1']

						if 'group_id' in request.GET:
							group_id = request.GET['group_id']
							query_students = get_att_group_students_att_register(group_id, session_name)
							# query_students = get_att_group_students(group_id, session_name)
							section = get_group_sections(request.GET['group_id'], session_name)
						else:
							query_students = get_section_students(section, {}, session_name)
						# print(query_students,'query_students')
						uniq_id_dict = {}
						uniq_id_list = []
						count_dict = {}
						for each in query_students[0]:
							uniq_id_dict[each['uniq_id']] = {
								'net_data': {
									'present_count': 0,
									'absent_count': 0,
									'total': 0,
									'percentage': 0},
								'att_data': []
							}
							uniq_id_list.append(each['uniq_id'])
							count_dict[each['uniq_id']] = {'count': 0}

						from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
						to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
						att_type = request.GET['att_type'].split(',')

						# all_att = get_attendance_type(session)
						# all_att_type = []

						# for al in all_att:
						#     for d in al['data']:
						#         all_att_type.append(d['sno'])

						if 'group_id' in request.GET:
							query_section_att = list(Attendance.objects.filter(date__range=[from_date, to_date], section__in=section, subject_id=subject, emp_id=emp_id, group_id=group_id).exclude(status='DELETE').values_list('id', flat=True).distinct())

						else:
							# print('hi',from_date, to_date,section,subject)
							query_section_att = list(Attendance.objects.filter(date__range=[from_date, to_date], section__in=section, subject_id=subject, emp_id=emp_id).exclude(status='DELETE').values_list('id', flat=True).distinct())
						# print(query_section_att,'query_section_att')
						valid_att_id = StudentAttStatus.objects.filter(att_id__in=query_section_att, att_type__in=att_type).exclude(status='DELETE').exclude(att_id__status='DELETE').values('att_id', 'att_id__date', 'att_id__lecture', 'att_id__status').order_by('att_id__date', 'att_id__lecture', 'att_id__id').distinct()

						q_sub = SubjectInfo.objects.filter(id=subject).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'session__sem_start', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name').order_by('id')
						status = []
						# print(uniq_id_list,'uniq_id_list')
						# print(subject,from_date,to_date,att_type,emp_id,'vrinda')
						status1 = StudentAttStatus.objects.filter(uniq_id__in=uniq_id_list, att_id__subject_id=subject, att_id__date__range=[from_date, to_date], att_type__in=att_type, approval_status__contains='APPROVED', att_id__emp_id=emp_id).exclude(att_id__status='DELETE').exclude(status='DELETE').values('present_status', 'att_id__date', 'att_id__lecture', 'att_type__value', 'att_type', 'att_id__group_id', 'att_id', 'uniq_id').order_by('att_id', 'att_id__date', 'att_id__lecture').distinct()
						# print(status1,'status1')
						new_dict = {}
						p_students = {}
						for each, data in groupby(status1, key=lambda x: x['att_id']):
							# print(each,'each')
							new_dict[each] = []
							p_students[each] = []
							for d in data:
								new_dict[each].append(d)
								p_students[each].append(d['uniq_id'])

						for each_id in valid_att_id:
							if each_id['att_id'] not in p_students:
								p_students[each_id['att_id']] = []
								new_dict[each_id['att_id']] = []
							# print(each_id,'each_id	',p_students[each_id['att_id']])
							####### TO RESOLVE WHEN THE ATTENDANCE OF STUDENT IS NOT MARKED#######################
							diff = list(set(uniq_id_list) - set(p_students[each_id['att_id']]))
							for a_students in diff:
								at_status = 'N/A'
								at_type = 'N'
								show = 'N/A'
								uniq_id_dict[a_students]['att_data'].append({'date': each_id['att_id__date'], 'lecture': each_id['att_id__lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})
							#######################################################################################

							for stu in new_dict[each_id['att_id']]:
								at_status = 'N/A'
								at_type = 'N'
								show = 'N/A'
								# count=0

								if stu['present_status'] == 'P':
									if str(stu['att_type']) in att_type:

										if ('NORMAL' in stu['att_type__value'] or 'REMEDIAL' in stu['att_type__value'] or 'TUTORIAL' in stu['att_type__value']):
											# count += 1
											count_dict[stu['uniq_id']]['count'] += 1
											at_status = 'P'

											if stu['att_id__group_id'] is not None:
												at_type = 'G'
											elif 'REMEDIAL' in stu['att_type__value']:
												at_type = 'R'

											# show = count
											show = count_dict[stu['uniq_id']]['count']

											uniq_id_dict[stu['uniq_id']]['net_data']['present_count'] += 1
											uniq_id_dict[stu['uniq_id']]['net_data']['total'] += 1
										elif ('SUBSTITUTE' in stu['att_type__value']):
											# count += 1
											count_dict[stu['uniq_id']]['count'] += 1
											at_status = 'P'
											show = 'S'
											at_type = 'S'
											# show = count
											show = count_dict[stu['uniq_id']]['count']
											uniq_id_dict[stu['uniq_id']]['net_data']['present_count'] += 1
											uniq_id_dict[stu['uniq_id']]['net_data']['total'] += 1
										else:
											at_type = 'E'
											at_status = 'P'
											show = 'E'

											uniq_id_dict[stu['uniq_id']]['net_data']['present_count'] += 1
											uniq_id_dict[stu['uniq_id']]['net_data']['total'] += 1
									else:
										at_status = 'A'
										# show = count
										show = count_dict[stu['uniq_id']]['count']

										if stu['att_id__group_id'] is not None:
											at_type = 'G'
											uniq_id_dict[stu['uniq_id']]['net_data']['total'] += 1

										elif 'REMEDIAL' in stu['att_type__value']:
											at_type = 'N'

											at_status = 'N/A'
											show = 'N/A'
										else:
											uniq_id_dict[stu['uniq_id']]['net_data']['total'] += 1

								else:
									# show = count
									show = count_dict[stu['uniq_id']]['count']
									at_status = 'A'
									if stu['att_id__group_id'] is not None:
										at_type = 'G'
										uniq_id_dict[stu['uniq_id']]['net_data']['total'] += 1

									elif 'REMEDIAL' in stu['att_type__value']:
										at_type = 'N'
										at_status = 'N/A'
										show = 'N/A'
									else:
										uniq_id_dict[stu['uniq_id']]['net_data']['total'] += 1

								uniq_id_dict[stu['uniq_id']]['att_data'].append({'date': stu['att_id__date'], 'lecture': stu['att_id__lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})

						for each in uniq_id_dict:
							if uniq_id_dict[each]['net_data']['total'] == 0:
								uniq_id_dict[each]['net_data']['percentage'] = 0
							else:
								uniq_id_dict[each]['net_data']['percentage'] = round((uniq_id_dict[each]['net_data']['present_count'] * 100) / uniq_id_dict[each]['net_data']['total'])

							uniq_id_dict[each]['net_data']['absent_count'] = uniq_id_dict[each]['net_data']['total'] - uniq_id_dict[each]['net_data']['present_count']

							for student in query_students[0]:
								if student['uniq_id'] == each:
									student['att_data'] = uniq_id_dict[each]['att_data']
									student['net_data'] = uniq_id_dict[each]['net_data']
									break

						status = 200
						data_values = {'data': query_students[0]}

					elif (requestType.custom_request_type(request.GET, 'att_register_lecturewise_graph_data')):
						section = request.GET['section'].split(',')
						subject = request.GET['subject']
						att_type = request.GET['att_type'].split(',')
						if 'emp_id' in request.GET:
							emp_id = request.GET['emp_id']
						else:
							emp_id = request.session['hash1']

						if 'group_id' in request.GET:
							group_id = request.GET['group_id']
							query_students = get_att_group_students_att_register(group_id, session_name)
							section = get_group_sections(request.GET['group_id'], session_name)
						else:
							query_students = get_section_students(section, {}, session_name)
						uniq_id_list = []
						for each in query_students[0]:
							uniq_id_list.append(each['uniq_id'])
						from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
						to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
						date_array = (from_date + datetime.timedelta(days=x) for x in range(0, (to_date - from_date).days))
						date_array = [from_date + timedelta(days=x) for x in range(0, (to_date - from_date).days + 1)]
						#print(date_array)
						data1 = []
						data1.append({})
						data_values = []
						 #FOR UNDEFINED VALUES ON GRAPH AXIS#
						role='role'
						true='true'
						##END##
						 ###DEFINING X AND Y AXIS ON GRAPH###
						axis=['Dates', 'L1',{'role':'annotation'}, 'L2',{'role':'annotation'}, 'L3',{'role':'annotation'} ,'L4',{'role':'annotation'},'L5',{'role':'annotation'}, 'L6',{'role':'annotation'}, 'L7',{'role':'annotation'}, 'L8',{'role':'annotation'}]
						data_values.append(axis)
						for dates in date_array:
							if 'group_id' in request.GET:
								lec = list(Attendance.objects.filter(date=dates, section__in=section,subject_id=subject,emp_id=emp_id, group_id=group_id).exclude(status__contains='DELETE').values_list('lecture',flat=True).order_by('lecture').distinct().order_by('lecture'))
								#print(lec)
							else:
								lec = list(Attendance.objects.filter(date=dates, section__in=section,subject_id=subject,emp_id=emp_id).exclude(status__contains='DELETE').values_list('lecture',flat=True).order_by('lecture').distinct().order_by('lecture'))
								#print(lec)
							present_lecwise=[]
							if len(lec)>0:
								present_lecwise.append(dates)
								for l in lec:
									present=0
									for stu in query_students[0]:
										query = StudentAttStatus.objects.filter(uniq_id=stu['uniq_id'], att_id__date=dates, att_id__lecture=l, att_type__in=att_type).exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").values('att_id__lecture', 'present_status')
										if query:
											if query[0]['present_status']=='P':
												present+=1
											else:
												pass
										else:
											pass
            #######SETTING DATA FORMAT TO MATCH WITH GOOGLE GRAPH#######
									present_lecwise.extend((present,'L'+str(l)))
									#print(present_lecwise)
								for i in range(1,len(axis)):
									try :
										present_lecwise[i]
									except:
										present_lecwise.extend((0,""))
								count=0
								for i in range(0,len(present_lecwise)):
									if present_lecwise[i]==0:
										count+=1
								for i in range(count//2):
									present_lecwise.insert(1,"")
									present_lecwise.insert(1,0)
									present_lecwise.pop(len(present_lecwise)-1)
									present_lecwise.pop(len(present_lecwise)-1)
								data_values.append(present_lecwise)
			############END##############################
						status=statusCodes.STATUS_SUCCESS
						data_values = {'data': data_values, 'data1': data1}
				else:
					status = statusCodes.STATUS_METHOD_NOT_ALLOWED
			else:
				status = statusCodes.STATUS_FORBIDDEN
		else:
			status = statusCodes.STATUS_UNAUTHORIZED
	else:
		status = statusCodes.STATUS_SERVER_ERROR
	
	return functions.RESPONSE(data_values,status)


def RegistrationCountReport(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1372, 319])
			# #print(check)
			if check == 200:
				query = []
				session = request.session['Session_id']
				# #print(session)
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				studentSession = generate_session_table_name("studentSession_", session_name)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						if(request.GET['type'] == 'H'):
							q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
							dept = q_dept[0]['dept']
							course = get_filtered_course(dept)

						elif(request.GET['type'] == 'D'):
							course = get_course()
						data = []
						total = 0
						total_reg = 0
						total_not_reg = 0

						for c in course:
							if(request.GET['type'] == 'H'):
								c['sno'] = c['course']
								c['value'] = c['course__value']
								branch = CourseDetail.objects.filter(course=c['course'], dept_id=q_dept[0]['dept']).values('uid', 'dept_id__value')
								# branch=get_branch(c['sno'],request.session['hash1'],session_name)
							else:
								branch = get_branch(c['sno'])
							for b in branch:
								# if(request.GET['type']=='H'):
								#   b['uid']=b['section__dept']
								#   b['dept_id__value']=b['section__dept__dept__value']
								qry_count = list(studentSession.objects.filter(section__sem_id__dept=b['uid'], session=session).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values_list('registration_status', flat=True))
								registered = qry_count.count(1)
								data.append({'course': c['value'], 'branch': b['dept_id__value'], 'total': len(qry_count), 'registered': registered, 'not_registered': len(qry_count) - registered})
								total += len(qry_count)
								total_reg += registered
								total_not_reg += len(qry_count) - registered
						status = 200
						data_values = {'data': data, 'total': total, 'total_reg': total_reg, 'total_not_reg': total_not_reg}
					elif request.GET['request_type'] == 'non_registered_data':
						data = []
						if 'year' in request.GET:
							year = request.GET['year']
							branch_id = request.GET['branch_id']
							non_registered_det = studentSession.objects.filter(section__sem_id__dept=branch_id, registration_status=0, year=year, session=session).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values('uniq_id__name', 'mob', 'fee_status', 'year', 'class_roll_no', 'uniq_id', 'uniq_id__uni_roll_no', 'uniq_id__join_year', 'uniq_id__date_of_add', 'uniq_id__lib', 'uniq_id__gender__value', 'uniq_id__caste__value', 'uniq_id__admission_status__value', 'uniq_id__stu_type__value', 'uniq_id__exam_type__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__admission_type__value', 'uniq_id__admission_through__value', 'section__section_id', 'section__section', 'sem__sem', 'sem__sem_id')
							for q in non_registered_det:

								name = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname', 'mname')
								mob_no = StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id']).values('father_mob', 'mother_mob')
								data.append({'details': q, 'parents_name': list(name), 'parents_mob': list(mob_no)})
								# #print(data)
						else:
							branch_id = request.GET['branch_id']
							non_registered_det = studentSession.objects.filter(section__sem_id__dept=branch_id, registration_status=0, session=session).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values('uniq_id__name', 'mob', 'fee_status', 'year', 'class_roll_no', 'uniq_id', 'uniq_id__uni_roll_no', 'uniq_id__join_year', 'uniq_id__date_of_add', 'uniq_id__lib', 'uniq_id__gender__value', 'uniq_id__caste__value', 'uniq_id__admission_status__value', 'uniq_id__stu_type__value', 'uniq_id__exam_type__value', 'uniq_id__dept_detail__dept__value', 'uniq_id__admission_type__value', 'uniq_id__admission_through__value', 'section__section_id', 'section__section', 'sem__sem', 'sem__sem_id')
							for q in non_registered_det:

								name = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname', 'mname')
								mob_no = StudentFamilyDetails.objects.filter(uniq_id=q['uniq_id']).values('father_mob', 'mother_mob')
								data.append({'details': q, 'parents_name': list(name), 'parents_mob': list(mob_no)})
						status = 200
						data_values = {'data': data}
					elif request.GET['request_type'] == 'detailed_report':
						course = get_course()
						final_data = []

						total = 0
						total_reg = 0
						total_not_reg = 0

						for c in course:
							branch = get_branch(c['sno'])
							course_data = []

							course_total = 0
							course_total_reg = 0
							course_total_not_reg = 0

							year_total = []

							year_tot = 0
							year_reg = 0
							year_not_reg = 0

							year_list = []
							year_data_list = []
							if len(branch) > 0:

								for duration in range(branch[0]['course_duration']):
									year_list.append(duration + 1)

									year_data_list.append("Registered")
									year_data_list.append("Not Registered")
									year_data_list.append("Total")

									year_total.extend([0, 0, 0])

							for b in branch:
								branch_data = []

								branch_total = 0
								branch_total_reg = 0
								branch_total_not_reg = 0

								semester = get_semester(b['uid'], sem_type)
								i = 0
								for sem in semester:

									qry_count = list(studentSession.objects.filter(section__sem_id=sem['sem_id'], session=session).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values_list('registration_status', flat=True))

									sem_total = len(qry_count)
									sem_registered = qry_count.count(1)
									sem_not_registered = sem_total - qry_count.count(1)

									branch_data.append(sem_registered)
									branch_data.append(sem_not_registered)
									branch_data.append(sem_total)

									branch_total += sem_total
									branch_total_reg += sem_registered
									branch_total_not_reg += sem_not_registered

									course_total += sem_total
									course_total_reg += sem_registered
									course_total_not_reg += sem_not_registered

									year_total[i] += sem_registered
									year_total[i + 1] += sem_not_registered
									year_total[i + 2] += sem_total

									year_tot += sem_total
									year_reg += sem_registered
									year_not_reg += sem_not_registered

									i += 3

								if b['dept_id__value'] == 'AS':
									branch_data.extend([0, 0, 0, 0, 0, 0, 0, 0, 0])
								course_data.append({'branch': b['dept_id__value'], 'branch_id': b['uid'], 'data': branch_data, 'branch_total': branch_total, 'branch_total_reg': branch_total_reg, 'branch_total_not_reg': branch_total_not_reg})

							year_total.append(year_reg)
							year_total.append(year_not_reg)
							year_total.append(year_tot)

							final_data.append({'course': c['value'], 'data': course_data, 'year_total': year_total, 'course_total_reg': course_total_reg, 'course_total_not_reg': course_total_not_reg, 'course_total': course_total, 'year_list': year_list, 'year_data_list': year_data_list})
						data_values = {'data': final_data}

						status = 200

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def DailyAttCountReport(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			query = []
			session = request.session['Session_id']
			session_name = request.session['Session_name']
			sem_type = request.session['sem_type']
			studentSession = generate_session_table_name("studentSession_", session_name)
			StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
			if(request.method == 'GET'):
				if request.GET['request_type'] == 'course':
					if request.GET['request_by'] == 'hod':
						check = checkpermission(request, [1369, 425, 337, 319])
						if check == 200 and 'H' in request.session['Coordinator_type']:
							q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
							dept = q_dept[0]['dept']
							course = get_filtered_course(dept)
							status = 200
							data_values = {'course': course}
					elif request.GET['request_by'] == 'dean':
						check = checkpermission(request, [1372, 1368])
						if check == 200:
							course = get_course()

							course_data = []
							for c in course:
								course_data.append({"course": c['sno'], 'course__value': c['value']})
							status = 200
							data_values = {'course': course_data}

				elif request.GET['request_type'] == 'dept':
					course = request.GET['course'].split(',')
					emp_id = request.session['hash1']
					if request.GET['request_by'] == 'hod':
						check = checkpermission(request, [1369, 425, 337, 319])
						if check == 200 and 'H' in request.session['Coordinator_type']:
							q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
							dept = q_dept[0]['dept']
							course = CourseDetail.objects.filter(course_id__in=course, dept=dept).values("uid", "dept_id__value", "course_duration").distinct()
							status = 200
							data_values = {'course': list(course)}
					elif request.GET['request_by'] == 'dean':
						check = checkpermission(request, [1372, 1368])
						if check == 200:
							qry = CourseDetail.objects.filter(course_id__in=course).values("uid", "dept_id__value", "course_duration", 'course_id__value').distinct()
							status = 200
							data_values = {'course': list(qry)}

				elif request.GET['request_type'] == 'semester':

					branch = request.GET['branch'].split(',')

					qry_course_duration = CourseDetail.objects.filter(uid__in=branch).values('course_duration').order_by('-course_duration')[:1]
					duration = qry_course_duration[0]['course_duration']
					sem_li = []
					if sem_type == 'odd':
						for y in range(1, duration + 1):
							sem_li.append({'sem_id': (y * 2) - 1, 'sem': (y * 2) - 1})

					elif sem_type == 'even':
						for y in range(1, duration + 1):
							sem_li.append({'sem_id': (y * 2), 'sem': (y * 2)})
					status = 200
					data_values = {'semester': sem_li}

				elif request.GET['request_type'] == 'section':
					branch = request.GET['branch'].split(',')
					semester = request.GET['sem'].split(',')
					qry_max_sections = Sections.objects.filter(sem_id__dept__in=branch, sem_id__sem__in=semester).values('dept', 'sem_id').annotate(count=Count('section')).order_by('-count')[:1]
					qry_sections = []
					if len(qry_max_sections) > 0:
						qry_sections = Sections.objects.filter(sem_id__dept=qry_max_sections[0]['dept'], sem_id=qry_max_sections[0]['sem_id']).exclude(status='DELETE').values_list('section', flat=True).order_by('section')

					status = 200
					data_values = {'section': list(qry_sections)}

				elif request.GET['request_type'] == 'lecture':
					TimeTableSlots = generate_session_table_name("TimeTableSlots_", session_name)
					date = datetime.strptime(str(request.GET['date']).split('T')[0], "%Y-%m-%d").date()
					day = date.weekday()

					query2 = TimeTableSlots.objects.filter(day=day).filter(dean_approval_status="APPROVED").exclude(status="DELETE").values('num_lecture_slots').order_by('-num_lecture_slots')[:1]

					status = 200
					if len(query2) == 0:
						data_values = {'lecture': list(range(1, 9))}
					else:
						data_values = {'lecture': list(range(1, query2[0]['num_lecture_slots'] + 1))}

				elif request.GET['request_type'] == 'submit_data':
					#course = request.GET['course'].split(',')
					branch = request.GET['branch'].split(',')
					semester = request.GET['semester'].split(',')
					sections = request.GET['section'].split(',')
					lectures = request.GET['lecture'].split(',')

					date = datetime.strptime(str(request.GET['date']).split('T')[0], "%Y-%m-%d").date() + relativedelta(days=+1)
					studentSession = generate_session_table_name("studentSession_", session_name)
					StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

					final_data = []
					i = 0
					for sem in semester:
						final_data.append({})
						final_data[i]['year'] = math.ceil(int(sem) / 2.0)
						final_data[i]['lectures'] = []
						j = 0
						for lec in lectures:
							final_data[i]['lectures'].append({})
							final_data[i]['lectures'][j]['lec_num'] = lec
							final_data[i]['lectures'][j]['lec_data'] = []
							k = 0
							qry_branch = CourseDetail.objects.filter(uid__in=branch).values('dept_id__value', 'dept_id', 'course', 'course__value', 'uid')
							for b in qry_branch:
								final_data[i]['lectures'][j]['lec_data'].append({})
								final_data[i]['lectures'][j]['lec_data'][k]['branch'] = b['dept_id__value']
								final_data[i]['lectures'][j]['lec_data'][k]['course'] = b['course__value']

								final_data[i]['lectures'][j]['lec_data'][k]['branch_data'] = []

								l = 0
								branch_present = 0
								branch_total = 0

								qry_sections = Sections.objects.filter(sem_id__sem=sem, sem_id__dept=b['uid'], section__in=sections).values('section_id', 'section')
								flg_section = False
								for sec in qry_sections:
									flg_section = True

									qry_strength = studentSession.objects.filter(section=sec['section_id']).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).count()
									branch_total += qry_strength
									final_data[i]['lectures'][j]['lec_data'][k]['branch_data'].append({})
									q_sub_normal_att_present = StudentAttStatus.objects.filter(att_id__section=sec['section_id'], present_status='P', att_id__lecture=lec, approval_status__contains="APPROVED", att_id__date=date).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(present_count=Count('uniq_id')).order_by()

									q_sub_normal_att_total = StudentAttStatus.objects.filter(att_id__section=sec['section_id'], approval_status__contains="APPROVED", att_id__lecture=lec, att_id__date=date).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id', 'att_id__emp_id__name', 'att_id__subject_id__sub_alpha_code', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_name').annotate(total=Count('uniq_id')).order_by()

									final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['section'] = sec['section']
									if len(q_sub_normal_att_present) > 0:
										final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['present_count'] = q_sub_normal_att_present[0]['present_count']
										#final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['total'] = q_sub_normal_att_total[0]['total']
										final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['total'] = qry_strength

										final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['percent'] = math.ceil((final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['present_count'] * 100.0) / qry_strength)

										final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['faculty_data'] = {'name': q_sub_normal_att_total[0]['att_id__emp_id__name'], 'sub_code': q_sub_normal_att_total[0]['att_id__subject_id__sub_alpha_code'] + "-" + q_sub_normal_att_total[0]['att_id__subject_id__sub_num_code'], 'sub_name': q_sub_normal_att_total[0]['att_id__subject_id__sub_name']}

										branch_present += q_sub_normal_att_present[0]['present_count']
									else:
										final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['present_count'] = "----"
										final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['total'] = qry_strength
										final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['percent'] = "----"

										final_data[i]['lectures'][j]['lec_data'][k]['branch_data'][l]['faculty_data'] = {'name': '----', 'sub_code': "----", 'sub_name': "----"}
									l += 1

								final_data[i]['lectures'][j]['lec_data'][k]['branch_total'] = branch_total
								final_data[i]['lectures'][j]['lec_data'][k]['branch_present'] = branch_present
								if branch_total > 0:
									final_data[i]['lectures'][j]['lec_data'][k]['branch_percent'] = math.ceil((branch_present * 100.0) / branch_total)
								else:
									final_data[i]['lectures'][j]['lec_data'][k]['branch_percent'] = "----"
								k += 1
								if not flg_section:
									del final_data[i]['lectures'][j]['lec_data'][k - 1]
									k -= 1
							j += 1

						i += 1

					status = 200
					data_values = {'data': final_data}

				elif request.GET['request_type'] == 'submit_data_final':
					data = []
					branch = request.GET['branch'].split(',')
					semester = request.GET['semester'].split(',')
					section = request.GET['section'].split(',')
					lectures = request.GET['lecture'].split(',')
					date = datetime.strptime(str(request.GET['date']), "%Y-%m-%d").date()

					##### MAKE DATA=(COURSE,DEPT,SECTION) #####
					DATA = []
					for b in branch:
						for sec in section:
							qry = list(Sections.objects.filter(dept=b, section=sec).exclude(status="DELETE").values_list('dept__course__value', 'dept__dept__value', 'section').distinct())
							DATA.extend(qry)
					###########################################
					for sem in semester:
						year = math.ceil(int(sem) / 2)
						lecture_data = []
						for lec in lectures:

							q_sub_normal_att_total = StudentAttStatus.objects.filter(att_id__section__section__in=section, att_id__section__dept__in=branch, approval_status__contains="APPROVED", att_id__lecture=lec, att_id__date=date, att_id__section__sem_id__sem=sem).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__isgroup','att_id__subject_id', 'att_id__emp_id__name', 'att_id__subject_id__sub_alpha_code', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_name', 'uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__uni_roll_no', 'att_id__section__dept__dept__value', 'att_id__section__section', 'present_status', 'att_id__lecture', 'att_id__date', 'att_id__isgroup', 'att_id__app', 'att_id__section__dept__course__value').order_by('att_id__section__dept__course__value', 'att_id__section__dept__dept__value', 'att_id__section__section', 'present_status')
							lec_data = []

							for course_no, course_data in groupby(q_sub_normal_att_total, key=lambda x: x['att_id__section__dept__course__value']):
								c_data = list(course_data)
								for branch_no, branch_data in groupby(c_data, key=lambda x: x['att_id__section__dept__dept__value']):
									b_data = list(branch_data)
									for section_no, section_data in groupby(b_data, key=lambda x: x['att_id__section__section']):
										s_data = list(section_data)
										lec_wise_section_data = {}
										total_data = []

										###################################################################################
										lec_wise_section_data['present'] = 'N/A'
										lec_wise_section_data['present_data'] = {}
										lec_wise_section_data['present_data']['marked_by'] = {'name': s_data[0]['att_id__emp_id__name'], 'sub_code': s_data[0]['att_id__subject_id__sub_alpha_code'] + "-" + s_data[0]['att_id__subject_id__sub_num_code'], 'sub_name': s_data[0]['att_id__subject_id__sub_name']}
										lec_wise_section_data['present_data']['students'] = []
										lec_wise_section_data['absent'] = 'N/A'
										lec_wise_section_data['absent_data'] = {}
										lec_wise_section_data['absent_data']['marked_by'] = {'name': s_data[0]['att_id__emp_id__name'], 'sub_code': s_data[0]['att_id__subject_id__sub_alpha_code'] + "-" + s_data[0]['att_id__subject_id__sub_num_code'], 'sub_name': s_data[0]['att_id__subject_id__sub_name']}
										lec_wise_section_data['absent_data']['students'] = []
										lec_wise_section_data['present_percent'] = 0

										lec_wise_section_data['course'] = course_no
										lec_wise_section_data['section'] = section_no
										lec_wise_section_data['branch'] = branch_no
										##################################################################################

										for status, status_data in groupby(s_data, key=lambda x: x['present_status']):
											s_data = list(status_data)
											total_data.extend(s_data)

											if 'P' in status:
												lec_wise_section_data['present'] = len(s_data)
												lec_wise_section_data['present_data'] = {}
												lec_wise_section_data['present_data']['marked_by'] = {'name': s_data[0]['att_id__emp_id__name'], 'sub_code': s_data[0]['att_id__subject_id__sub_alpha_code'] + "-" + s_data[0]['att_id__subject_id__sub_num_code'], 'sub_name': s_data[0]['att_id__subject_id__sub_name']}
												lec_wise_section_data['present_data']['students'] = s_data
											else:
												lec_wise_section_data['absent'] = len(s_data)
												lec_wise_section_data['absent_data'] = {}
												lec_wise_section_data['absent_data']['marked_by'] = {'name': s_data[0]['att_id__emp_id__name'], 'sub_code': s_data[0]['att_id__subject_id__sub_alpha_code'] + "-" + s_data[0]['att_id__subject_id__sub_num_code'], 'sub_name': s_data[0]['att_id__subject_id__sub_name']}
												lec_wise_section_data['absent_data']['students'] = s_data

										if isinstance(lec_wise_section_data['present'], int) or isinstance(lec_wise_section_data['absent'], int):
											if not isinstance(lec_wise_section_data['present'], int):
												lec_wise_section_data['present'] = 0
											elif not isinstance(lec_wise_section_data['absent'], int):
												lec_wise_section_data['absent'] = 0
											lec_wise_section_data['present_percent'] = round((lec_wise_section_data['present'] / (lec_wise_section_data['present'] + lec_wise_section_data['absent'])) * 100, 2)

										lec_wise_section_data['total'] = len(total_data)
										lec_wise_section_data['total_data'] = {}
										if len(total_data) > 0:
											lec_wise_section_data['total_data']['marked_by'] = {'name': s_data[0]['att_id__emp_id__name'], 'sub_code': s_data[0]['att_id__subject_id__sub_alpha_code'] + "-" + s_data[0]['att_id__subject_id__sub_num_code'], 'sub_name': s_data[0]['att_id__subject_id__sub_name']}
										else:
											lec_wise_section_data['total_data']['marked_by'] = {'name': '---', 'sub_code': '---', 'sub_name': '--'}
										lec_wise_section_data['total_data']['students'] = total_data
										lec_data.append(lec_wise_section_data)

							########## FOR AVOIDIND CASE FOR ANY LECTURE WHOSE ATTENDANCE IS NOT MARKED ############
							if len(lec_data) < len(DATA):
								for d in DATA:
									flag = 0
									for l in lec_data:
										if 'course' in l.keys() and 'branch' in l.keys() and 'section' in l.keys():
											if l['course'] == d[0] and l['branch'] == d[1] and l['section'] == d[2]:
												flag = 1
												break
									if flag == 0:
										lec_wise_section_data = {}
										lec_wise_section_data['present'] = 'N/A'
										lec_wise_section_data['present_data'] = {}
										lec_wise_section_data['present_data']['marked_by'] = {'name': '---', 'sub_code': '---', 'sub_name': '--'}
										lec_wise_section_data['present_data']['students'] = []
										lec_wise_section_data['absent'] = 'N/A'
										lec_wise_section_data['absent_data'] = {}
										lec_wise_section_data['absent_data']['marked_by'] = {'name': '---', 'sub_code': '---', 'sub_name': '--'}
										lec_wise_section_data['absent_data']['students'] = []
										students = list(studentSession.objects.filter(section_id__section=d[2], section__sem_id__sem=sem, section_id__dept__dept__value=d[1]).values('uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no'))
										lec_wise_section_data['total'] = len(students)
										lec_wise_section_data['total_data'] = students
										lec_wise_section_data['present_percent'] = 0

										lec_wise_section_data['course'] = d[0]
										lec_wise_section_data['branch'] = d[1]
										lec_wise_section_data['section'] = d[2]
										lec_data.append(lec_wise_section_data)

							########################################################################################
							lecture_data.append({'lec_num': lec, 'lec_data': lec_data})
						data.append({'year': year, 'lecture_data': lecture_data})
					status = 200
					data_values = {'data': data}

				else:
					status = 403
			else:
				status = 502
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


def student_data(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				query = []
				session = request.GET['Session_id']
				session_name = request.GET['Session_name']
				sem_type = request.GET['sem_type']
				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':

						status = 200

					data_values = {'data': data}
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


####################################### KAKSHA VIEWS ##############################

####################################### KAKSHA VIEWS ##############################

def kaksha_under_alert():
	cancellable = True
	message = "Please update to use latest Kaksha features"
	title = "Update Available"
	alert = {'latest_code': 22, 'cancellable': cancellable, 'title': title, 'message': message, 'button_text': "message", 'link': "https://play.google.com/store/apps/details?id=edu.kiet.faculty.faculty_app&hl=en_US", 'status': 200}
	# status=200: For Update
	# status=202: For Alert
	return alert


def kaksha_data(request):
	alert = {}
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				emp_id = request.session['hash1']
				LessonPropose = generate_session_table_name("LessonPropose_", session_name)
				LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)
				LessonProposeDetail = generate_session_table_name("LessonProposeDetail_", session_name)
				SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
				LessonProposeTopics = generate_session_table_name("LessonProposeTopics_", session_name)
				LessonProposeBTLevel = generate_session_table_name("LessonProposeBTLevel_", session_name)
				LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name)
				LessonProposeApproval = generate_session_table_name("LessonProposeApproval_", session_name)
				session_id = request.session['Session_id']
				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						data = {}
						attendance_sub_type = get_class_attendance_type(session)
						data['attendance_type'] = attendance_sub_type
						course = get_fac_time_course(request.session['hash1'], session_name)
						data['course'] = []
						n_course = len(course)
						for i in range(n_course):
							dept = get_fac_time_dept(emp_id, course[i]['section__sem_id__dept__course_id'], session_name)
							data['course'].append({'sno': course[i]['section__sem_id__dept__course_id'], 'value': course[i]['section__sem_id__dept__course_id__value'], 'branch': []})

							n_branch = len(dept)
							for j in range(n_branch):
								sem = get_fac_time_sem(emp_id, dept[j]['section__sem_id__dept'], session_name)
								data['course'][i]['branch'].append({'sno': dept[j]['section__sem_id__dept'], 'value': dept[j]['section__sem_id__dept__dept__value'], 'semester': []})
								n_sem = len(sem)
								s = get_sem_dates(emp_id, dept[j]['section__sem_id__dept'], session_name)
								data['sem_start'] = s[0]['session__sem_start']
								data['sem_end'] = s[0]['session__sem_end']
								for k in range(n_sem):
									section = get_fac_time_section(emp_id, sem[k]['section__sem_id'], session_name)
									data['course'][i]['branch'][j]['semester'].append({'sno': sem[k]['section__sem_id'], 'value': sem[k]['section__sem_id__sem'], 'intersection_group': [], 'section': [], 'num_of_lectures': []})

									######################### DAY LECTURES #################################################
									for day in range(7):
										lectures = get_lectures(sem[k]['section__sem_id'], day, session_name)

										data['course'][i]['branch'][j]['semester'][k]['num_of_lectures'].append({'sno': day, 'value': calendar.day_name[day], 'lectures': lectures['lectures']})

									######################### INTER-SECTION GROUPS ##########################################

									intersection_group = get_emp_intersection_group(emp_id, sem[k]['section__sem_id'], session_name)

									n_intersection_group = len(intersection_group)
									for l in range(n_intersection_group):
										group_sub = get_fac_time_subject(emp_id, get_group_sections(intersection_group[l]['group_id'], session_name), session_name)
										group_students = get_att_group_students(intersection_group[l]['group_id'], session_name)
										for sub in group_sub:
											query_approval = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=sub['subject_id'], approval_status="APPROVED", propose_detail__lesson_propose__added_by=emp_id, propose_detail__lesson_propose__group_id=intersection_group[l]['group_id']).exclude(status="DELETE").values_list('propose_detail', flat=True))
											query_lecture_tutorial = list(LessonPropose.objects.filter(subject=sub['subject_id'], group_id=intersection_group[l]['group_id'], session=session_id, status="INSERT", added_by=request.session['hash1']).exclude(status="DELETE").values('lecture_tutorial', 'id'))
											data1 = []
											query_approval
											for x in query_lecture_tutorial:
												x['topic_data'] = []
												query = set(list(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=x['id'], propose_detail__lesson_propose__added_by=emp_id, propose_detail__in=query_approval, propose_detail__lesson_propose__subject=sub['subject_id'], propose_detail__lesson_propose__group_id=intersection_group[l]['group_id']).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values_list('propose_topic__unit', flat=True).distinct().order_by('propose_topic__unit')))

												for q in query:
													qry1 = list(LessonProposeTopics.objects.filter(propose_topic__unit=q, propose_detail__lesson_propose__group_id=intersection_group[l]['group_id'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_detail__in=query_approval, propose_topic__subject=sub['subject_id'], propose_detail__lesson_propose__added_by=emp_id).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").values_list('propose_topic__topic_name', flat=True).distinct())
													if len(qry1) > 0:
														# qry_unit = list(LessonTopicDetail.objects.filter(subject=sub['subject_id']).exclude(status="DELETE").values_list('unit', flat=True).distinct())
														# for q1 in qry_unit:
														#--------------

														#----------------
														qry_topic = LessonTopicDetail.objects.filter(subject=sub['subject_id'], unit=q, topic_name__in=qry1).exclude(status="DELETE").values('topic_name', 'id').distinct()
														if len(qry_topic) > 0:
															x['topic_data'].append({'unit': q, 'topic': list(qry_topic)})

												if len(query) > 0:
													data1.append({"topic_data": x['topic_data'], "type": x['lecture_tutorial']})

											sub['subject_data'] = data1
										data['course'][i]['branch'][j]['semester'][k]['intersection_group'].append({'sno': intersection_group[l]['group_id'], 'value': intersection_group[l]['group_id__group_name'], 'subjects': group_sub, 'students': group_students})

									######################### INTER-SECTION GROUPS END ##########################################

									n_section = len(section)
									for m in range(n_section):
										sec = []
										sec.append(section[m]['section'])

										subjects = get_fac_time_subject(emp_id, sec, session_name)
										students = get_section_students(sec, {}, session_name)
										data1 = []
										for sub in subjects:
											query_approval = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=sub['subject_id'], approval_status="APPROVED", propose_detail__lesson_propose__added_by=emp_id, propose_detail__lesson_propose__section=section[m]['section']).exclude(status="DELETE").values_list('propose_detail', flat=True))
											query_lecture_tutorial = list(LessonPropose.objects.filter(subject=sub['subject_id'], section=section[m]['section'], session=session_id, status="INSERT", added_by=request.session['hash1']).exclude(status="DELETE").values('lecture_tutorial', 'id', 'section__section'))
											data1 = []
											query_approval
											for x in query_lecture_tutorial:
												x['topic_data'] = []
												query = set(list(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=x['id'], propose_detail__lesson_propose__added_by=emp_id, propose_detail__in=query_approval, propose_detail__lesson_propose__subject=sub['subject_id'], propose_detail__lesson_propose__section=section[m]['section']).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values_list('propose_topic__unit', flat=True).distinct().order_by('propose_topic__unit')))

												for q in query:
													qry1 = list(LessonProposeTopics.objects.filter(propose_topic__unit=q, propose_detail__lesson_propose__section=section[m]['section'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_detail__in=query_approval, propose_topic__subject=sub['subject_id'], propose_detail__lesson_propose__added_by=emp_id).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").values_list('propose_topic__topic_name', flat=True).distinct())
													if len(qry1) > 0:
														# qry_unit = list(LessonTopicDetail.objects.filter(subject=sub['subject_id']).exclude(status="DELETE").values_list('unit', flat=True).distinct())
														# for q1 in qry_unit:
														qry_topic = LessonTopicDetail.objects.filter(subject=sub['subject_id'], unit=q, topic_name__in=qry1).exclude(status="DELETE").values('topic_name', 'id').distinct()
														if len(qry_topic) > 0:
															x['topic_data'].append({'unit': q, 'topic': list(qry_topic)})

												if len(query) > 0:
													data1.append({"topic_data": x['topic_data'], "type": x['lecture_tutorial']})

											sub['subject_data'] = data1

										data['course'][i]['branch'][j]['semester'][k]['section'].append({'sno': section[m]['section'], 'value': section[m]['section__section'], 'subjects': subjects, 'students': students, 'intrasection_group': []})

										#################### INTRA-SECTION GROUPS ##############################################

										intrasection_group = get_emp_intrasection_group(emp_id, section[m]['section'], session_name)

										n_intrasection_group = len(intrasection_group)
										for n in range(n_intrasection_group):
											group_sub = get_fac_time_subject(emp_id, get_group_sections(intrasection_group[n]['group_id'], session_name), session_name)
											group_students = get_att_group_students(intrasection_group[n]['group_id'], session_name)
											for sub in group_sub:
												query_approval = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=sub['subject_id'], approval_status="APPROVED", propose_detail__lesson_propose__added_by=emp_id, propose_detail__lesson_propose__group_id=intrasection_group[n]['group_id']).exclude(status="DELETE").values_list('propose_detail', flat=True))
												query_lecture_tutorial = list(LessonPropose.objects.filter(subject=sub['subject_id'], group_id=intrasection_group[n]['group_id'], session=session_id, status="INSERT", added_by=request.session['hash1']).exclude(status="DELETE").values('lecture_tutorial', 'id'))
												data1 = []
												query_approval
												for x in query_lecture_tutorial:
													x['topic_data'] = []
													query = set(list(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=x['id'], propose_detail__lesson_propose__added_by=emp_id, propose_detail__in=query_approval, propose_detail__lesson_propose__subject=sub['subject_id'], propose_detail__lesson_propose__group_id=intrasection_group[n]['group_id']).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values_list('propose_topic__unit', flat=True).distinct().order_by('propose_topic__unit')))

													for q in query:
														qry1 = list(LessonProposeTopics.objects.filter(propose_topic__unit=q, propose_detail__lesson_propose__group_id=intrasection_group[n]['group_id'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_detail__in=query_approval, propose_topic__subject=sub['subject_id'], propose_detail__lesson_propose__added_by=emp_id).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").values_list('propose_topic__topic_name', flat=True).distinct())
														if len(qry1) > 0:
															# qry_unit = list(LessonTopicDetail.objects.filter(subject=sub['subject_id']).exclude(status="DELETE").values_list('unit', flat=True).distinct())
															# for q1 in qry_unit:
															qry_topic = LessonTopicDetail.objects.filter(subject=sub['subject_id'], unit=q, topic_name__in=qry1).exclude(status="DELETE").values('topic_name', 'id').distinct()
															if len(qry_topic) > 0:
																x['topic_data'].append({'unit': q, 'topic': list(qry_topic)})

													if len(query) > 0:
														data1.append({"topic_data": x['topic_data'], "type": x['lecture_tutorial']})

												sub['subject_data'] = data1
											data['course'][i]['branch'][j]['semester'][k]['section'][m]['intrasection_group'].append({'sno': intrasection_group[n]['group_id'], 'value': intrasection_group[n]['group_id__group_name'], 'subjects': group_sub, 'students': group_students})

										#########################################################################################
						status = 200
						data_values = {'data': data, 'alert': kaksha_under_alert(), 'is_flexible_update': False}
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status)


def show_matrix_tt_officials(request):
	data_values = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371, 319, 1369, 1372])
			if check == 200:
				session_name = request.session['Session_name']
				if request.method == 'GET':
					if request.GET['request_by'] in ["DEAN", "HOD", "FACULTY", "COORDINATOR", "EXTRACOORDINATOR"]:
						sem = request.GET['sem']
						section = request.GET['section']
						table = generate_session_table_name("studentSession_", session_name)
						session = request.session['Session_id']
						qry = Sections.objects.filter(section_id=section, sem_id__sem_id=sem).values('section', 'sem_id__dept__dept__value', 'sem_id__sem')
						data = create_matrix_tt(session, sem, section, session_name)
						# #print(data, "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
						data.append(qry[0]['sem_id__dept__dept__value'])
						data.append(qry[0]['sem_id__sem'])
						data.append(qry[0]['section'])
						status = 200
						data_values = data
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status, safe=False)


def view_emp_details(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1371, 1369, 319, 1372])
			if check == 200:
				if request.method == 'GET':
					session = request.session['Session_id']
					session_name = request.session['Session_name']
					FacultyTime = generate_session_table_name("FacultyTime_", session_name)
					# #print(request.GET, request.GET['request_type'], 'Time_Table')
					if request.GET['request_type'] == 'Emp_id':
						if request.GET['request_by'] in ['DEAN', 'dean']:
							qry = FacultyTime.objects.filter(session=session).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('emp_id', 'emp_id__name', 'emp_id__dept__value').distinct()
							data_values = list(qry)
							status = 200
						if request.GET['request_by'] in ['HOD', 'hod']:
							emp = request.session['hash1']
							dept = EmployeePrimdetail.objects.filter(emp_id=emp).values('dept')
							qry = FacultyTime.objects.filter(section__sem_id__dept__dept=dept[0]['dept'], session=session).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('emp_id', 'emp_id__name', 'emp_id__dept__value').distinct()
							data_values = list(qry)
							status = 200
					elif request.GET['request_type'] == 'Time_Table':
						if request.GET['request_by'] in ['DEAN', 'HOD', 'dean', 'hod']:
							emp_id = request.GET['faculty']
							qry1 = get_employee_time_table(emp_id, session_name)
							data_values = list(qry1)
							status = 200
						if request.GET['request_by'] in ['FACULTY', 'faculty']:
							qry1 = get_employee_time_table(request.session['hash1'], session_name)
							data_values = list(qry1)
							status = 200
					else:
						status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status, safe=False)


def EmployeeAdvanceReport(request):
	data_values = {}
	qry = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337, 1372])
			if check == 200:
				sem_type = request.session['sem_type']
				session_name = request.session['Session_name']
				SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
				FacultyTime = generate_session_table_name("FacultyTime_", session_name)

				if request.method == 'GET':
					if(request.GET['request_type'] == 'subject'):
						semester = request.GET['sem'].split(',')
						branch = request.GET['branch'].split(',')
						temp = list(SubjectInfo.objects.filter(sem__sem__in=semester, sem__dept__in=branch).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'id', 'sem__sem', 'sem__dept__dept__value'))
						data_values = {'data': temp}
						status = 200
				if request.method == 'POST':
					data = json.loads(request.body)

					employee_list_final = []
					branch = data['branch'].split(',')
					subject_id = data['subject_id'].split(',')
					sections = data['section'].split(',')

					employee_list = list(FacultyTime.objects.filter(section__section__in=sections, subject_id__in=subject_id).exclude(status="DELETE").values('emp_id', 'subject_id__sub_alpha_code', 'section__section', 'section', 'emp_id__name', 'emp_id__dept__value', 'subject_id__sub_name', 'subject_id__sub_num_code', 'section__sem_id__sem', 'section__sem_id__dept__course__value', 'day', 'lec_num'))
					data_values = {'data': employee_list}
					c = 0
					employee_list = (FacultyTime.objects.filter(section__dept__in=branch, section__section__in=sections, subject_id__in=subject_id).exclude(status="DELETE").values('emp_id', 'subject_id__sub_alpha_code', 'section', 'section__section', 'section', 'emp_id__name', 'emp_id__dept__value', 'subject_id__sub_name', 'subject_id__sub_num_code', 'section__sem_id__sem', 'section__sem_id__dept__course__value', 'day', 'lec_num', 'subject_id__subject_type__value', 'subject_id__sem__dept__dept__value', 'subject_id').order_by('section', 'subject_id', 'emp_id'))
					employee_list = list(employee_list)
					employee_list_final = []
					j = 0
					if(len(employee_list)):
						employee_list_final.append(employee_list[0])
					for i in employee_list:
						if(i['section'] == employee_list_final[j]['section'] and i['subject_id'] == employee_list_final[j]['subject_id'] and i['emp_id'] == employee_list_final[j]['emp_id']):
							pass
						else:
							employee_list_final.append(i)
							j += 1
					data_values = {'data': employee_list_final}

					status = 200
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status, safe=False)


def check_student_remark(request):
	data_values = []
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369, 1372])
			if check == 200 and 'A' in request.session['Coordinator_type']:
				remarks_list = {}
				emp = request.session['hash1']
				session_name = request.session['Session_name']
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
				studentSession = generate_session_table_name("studentSession_", session_name)
				if(request.method == 'GET'):
					if request.GET['request_type'] == 'form_data':
						uniq = []
						uniq_list = StudentAttStatus.objects.filter(marked_by=emp).exclude(remark__isnull=True).exclude(status__contains="DELETE").exclude(att_id__status="DELETE").values_list('uniq_id', flat=True).distinct()
						uniq_list2 = StudentRemarks.objects.filter(added_by=emp).exclude(status='DELETE').values_list('uniq_id', flat=True).distinct()
						if uniq_list:
							uniq.extend(uniq_list)
						if uniq_list2:
							uniq.extend(uniq_list2)
						# #print(uniq)
						i = 0
						sem_list = studentSession.objects.filter(uniq_id__in=uniq).values('uniq_id', 'sem__sem', 'section_id__section')
						for uniq in uniq:
							for x in sem_list:
								if x['uniq_id'] == uniq:
									sem = x['sem__sem']
									section = x['section_id__section']
							remark = []
							data_values.append({})
							data_values[i]['uniq'] = uniq
							data_values[i]['data'] = []
							q1 = list(StudentAttStatus.objects.filter(marked_by=emp, uniq_id=uniq).exclude(remark__isnull=True).exclude(status="DELETE").exclude(att_id__status="DELETE").values('uniq_id__section__dept__course__value', 'uniq_id__sem__sem', 'uniq_id__section__dept__dept__value', 'uniq_id__section__section', 'att_id', 'att_id__date', 'att_id__subject_id__sub_num_code', 'att_id__subject_id__sub_alpha_code', 'att_id__subject_id__sub_name', 'att_id__lecture', 'uniq_id__uniq_id__name', 'remark', 'uniq_id__uniq_id__uni_roll_no').order_by('-att_id__date', '-att_id__lecture'))
							rem1 = list(StudentRemarks.objects.filter(uniq_id=uniq, added_by=emp).values('remark', 'time_stamp', 'uniq_id__dept_detail__dept__value', 'uniq_id__name', 'uniq_id__uni_roll_no').order_by('-time_stamp').annotate(uniq_id__section__dept__dept__value=F('uniq_id__dept_detail__dept__value'), uniq_id__uniq_id__name=F('uniq_id__name'), uniq_id__uniq_id__uni_roll_no=F('uniq_id__uni_roll_no')))
							remark.extend(q1)
							# name,uni roll no,dept,sem,remark,lecture,remark date,
							for re in rem1:
								date = datetime.strptime(str(re['time_stamp']).split(' ')[0], "%Y-%m-%d").date()
								re.update({"att_id__date": date})
								re.update({"att_id__lecture": -1})
								re.update({"uniq_id__sem__sem": sem})
								re.update({"uniq_id__section__section": section})
							remark.extend(rem1)

							data_values[i]['data'] = remark
							i += 1

						status = 200
					else:
						data_values = {'msg': 'request_error'}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status, safe=False)


def student_prev_status(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369, 1372])
			if check == 200 and 'A' in request.session['Coordinator_type']:
				emp = request.session['hash1']
				session_name = request.session['Session_name']
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

				if(request.method == 'POST'):
					data = json.loads(request.body)
					uniq_list = data['uniq_id']
					sub = data['subject_id']
					status_list = []
					data_values = []
					i = 0
					for uniq in uniq_list:
						remark = []
						status_list = list(StudentAttStatus.objects.filter(uniq_id=uniq, att_id__subject_id=sub).exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").values_list('present_status', flat=True).order_by('-att_id__date', '-att_id__lecture')[:5])
						rem = list(StudentAttStatus.objects.filter(uniq_id=uniq, att_id__subject_id=sub).exclude(remark__isnull=True).exclude(status__contains="DELETE").exclude(att_id__status__contains="DELETE").values('remark', 'att_id__date', 'att_id__lecture').order_by('-att_id__date', '-att_id__lecture'))
						rem1 = list(StudentRemarks.objects.filter(uniq_id=uniq, added_by=emp).values('remark', 'time_stamp', 'id').order_by('-time_stamp'))
						remark.extend(rem)

						for re in rem1:
							# #print(re)
							# #print(str(re['time_stamp']))
							date = datetime.strptime(str(re['time_stamp']).split(' ')[0], "%Y-%m-%d").date()
							re.update({"att_id__date": date})
							re.update({"att_id__lecture": -1})
						remark.extend(rem1)
						data_values.append({'uniq': uniq, 'present_status': status_list, 'remark': remark})
					status = 200
				else:
					data_values = {'msg': 'request_error'}
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	
	return JsonResponse(data=data_values, status=status, safe=False)

# ADDED FUNCTIONALITY -> Remarks for any student at any time


def student_acad_remarks(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369, 1372])
			if check == 200 and 'A' in request.session['Coordinator_type']:
				emp = request.session['hash1']
				session_name = request.session['Session_name']
				session = request.session['Session_id']
				if(request.method == 'POST'):
					data = json.loads(request.body)
					objs = (StudentRemarks(added_by=EmployeePrimdetail.objects.get(emp_id=emp), session=Semtiming.objects.get(uid=session), uniq_id=StudentPrimDetail.objects.get(uniq_id=x), remark=data['remark']) for x in data['uniq_id'])
					q_ins = StudentRemarks.objects.bulk_create(objs)
					if q_ins:
						data_values = {'msg': 'Remark added successfully.', 'error': False}
						status = 200
					else:
						data_values = {'msg': 'Remark could not be added.', 'error': True}
						status = 500
				else:
					data_values = {'msg': 'request_error', 'error': 'True'}
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status, safe=False)

# Modified attedace register###############################3
# Modified attedace register###############################3


def ModifiedAttendanceRegister(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1369, 1371, 425, 337, 319, 1372])
			if check == 200 and ('A' in request.session['Coordinator_type'] or 'H' in request.session['Coordinator_type']):
				query = []
				session = request.session['Session_id']
				session_name = request.session['Session_name']
				sem_type = request.session['sem_type']
				Attendance = generate_session_table_name("Attendance_", session_name)
				StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
				SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'att_register_data':
						section = request.GET['section']
						subject = request.GET['subject']

						if 'emp_id' in request.GET:
							emp_id = request.GET['emp_id']
						else:
							emp_id = request.session['hash1']

						from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
						to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
						att_type = request.GET['att_type'].split(',')

						sub_type = list(SubjectInfo.objects.filter(id=subject).values('subject_type__value'))

						if sub_type[0]['subject_type__value'] == 'LAB':
							valid_att_id = list(StudentAttStatus.objects.filter(att_id__date__range=[from_date, to_date], att_id__section=section, att_id__subject_id=subject, att_id__emp_id=emp_id, att_type__in=att_type).exclude(status='DELETE').exclude(att_id__status='DELETE').values_list('att_id', flat=True).distinct())
							query_section_att = Attendance.objects.filter(id__in=valid_att_id).exclude(status='DELETE').values('id', 'date', 'lecture', 'status').order_by('date', 'lecture', 'id').distinct()

						else:
							valid_att_id = list(StudentAttStatus.objects.filter(att_id__date__range=[from_date, to_date], att_id__section=section, att_id__subject_id=subject, att_type__in=att_type).exclude(status='DELETE').exclude(att_id__status='DELETE').values_list('att_id', flat=True).distinct())
							query_section_att = Attendance.objects.filter(id__in=valid_att_id).exclude(status='DELETE').values('id', 'date', 'lecture', 'status').order_by('date', 'lecture', 'id').distinct()

						q_sub = SubjectInfo.objects.filter(id=subject).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_unit', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'session__sem_start', 'sem', 'id', 'no_of_units', 'subject_unit__value', 'subject_type__value', 'added_by__name').order_by('id')
						query_students = get_section_students(section.split(','), {}, session_name)
						for stu in query_students[0]:
							status = get_student_subject_att_status_wise(stu['uniq_id'], subject, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(stu['att_start_date']), "%Y-%m-%d").date()), to_date, att_type, session_name, emp_id)
							# #print(status)
							stu_att_data = []

							present_count = 0
							absent_count = 0
							total_count = 0

							i = 0

							count = 0
							n = len(status)  # Length of the status of lectures

							for date_lec in query_section_att:
								at_status = 'N/A'
								at_type = 'N'
								show = 'N/A'
								if i < n:  # checking status length is not greater than index(i)
									if date_lec['id'] != status[i]['att_id']:  # checking is att_id available in lecture list
										stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})
										continue
								if i < n and status[i]['att_id__date'] == date_lec['date'] and status[i]['att_id__lecture'] == date_lec['lecture']:
									if status[i]['present_status'] == 'P':
										if str(status[i]['att_type']) in att_type:

											if ('NORMAL' in status[i]['att_type__value'] or 'REMEDIAL' in status[i]['att_type__value'] or 'TUTORIAL' in status[i]['att_type__value']):
												count += 1
												at_status = 'P'

												if status[i]['att_id__group_id'] is not None:
													at_type = 'G'
												elif 'REMEDIAL' in status[i]['att_type__value']:
													at_type = 'R'

												show = count
												present_count += 1
												total_count += 1
											elif ('SUBSTITUTE' in status[i]['att_type__value']):
												count += 1
												at_status = 'P'
												show = 'S'
												at_type = 'S'
												show = count
												present_count += 1
												total_count += 1
											else:
												at_type = 'E'
												at_status = 'P'
												show = 'E'

												present_count += 1
												total_count += 1
										else:
											at_status = 'A'
											show = count

											if status[i]['att_id__group_id'] is not None:
												at_type = 'G'
												total_count += 1

											elif 'REMEDIAL' in status[i]['att_type__value']:
												at_type = 'N'

												at_status = 'N/A'
												show = 'N/A'
											else:
												total_count += 1

									else:

										show = count
										at_status = 'A'
										if status[i]['att_id__group_id'] is not None:
											at_type = 'G'
											total_count += 1

										elif 'REMEDIAL' in status[i]['att_type__value']:
											at_type = 'N'
											at_status = 'N/A'
											show = 'N/A'
										else:
											total_count += 1

									stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})

									i += 1
								else:
									stu_att_data.append({'date': date_lec['date'], 'lecture': date_lec['lecture'], 'att_status': at_status, 'count': show, 'attendance_type': at_type})

							stu['att_data'] = stu_att_data
							if total_count == 0:
								percentage = 0
							else:
								percentage = round((present_count * 100) / total_count)
							stu['net_data'] = {'present_count': present_count, 'absent_count': total_count - present_count, 'total': total_count, 'percentage': percentage}

						status = 200
						data_values = {'data': query_students[0]}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data=data_values, status=status)


# def view_emp_details(request):
#     data_values=[]
#     status=403
#     if 'HTTP_COOKIE' in request.META:
#         if request.user.is_authenticated:
#             check=checkpermission(request,[1371,1369,319])
#             if check==200:
#                 if request.method=='GET':
#                     session=request.session['Session_id']
#                     session_name=request.session['Session_name']
#                     FacultyTime = generate_session_table_name("FacultyTime_",session_name)
#                     StudentAttStatus = generate_session_table_name("StudentAttStatus_",session_name)
#                     if request.GET['request_type']=='Emp_id':
#                         date=datetime.now()
#                         q_time_table = list(FacultyTime.objects.filter(emp_id=emp_id,day=request.GET['day']).exclude(status='DELETE').values('subject_id','subject_id__sub_name','subject_id__sub_num_code','subject_id__sub_alpha_code','section','section__section','section','section__sem_id__sem','section__sem_id__dept__course_id__value','section__sem_id__dept__dept__value','end_time','start_time','day','lec_num').order_by('day','lec_num'))
#                         for q in q_time_table:
#                             q=list(StudentAttStatus.objects.filter(att_id__lecture=q['lec_num'],att_id__section=q['section'],att_id__date=date).exclude(status='DELETE').exclude(att_id__status='DELETE').values('marked_by__name','att_id__lecture','att_id__subject_id__sub_name','att_id__subject_id__sub_alpha_code','att_id__subject_id__sub_num_code').distinct())
#                             if len(q)>0:
#                                 data_values.append(q[0])


#                     else:
#                         status=502
#             else:
#                 status=403
#         else:
#             status=401
#     else:
#         status=500
#     return JsonResponse(data=data_values,status=status,safe=False)

#############################################all emp details####################
def emp_details(request):
	if 'HTTP_COOKIE' in request.META:
		if request.method == 'GET':
			qry = list(EmployeePrimdetail.objects.filter(emp_status='ACTIVE').exclude(emp_id='00007').values('name', 'dept__value', 'mob', 'email', 'emp_id', 'emp_type__value', 'desg__value'))
			for q in qry:
				if 'name' not in q or q['name'] is None:
					q['name'] = '---'
				if 'dept__value' not in q or q['dept__value'] is None:
					q['dept__value'] = '---'
				if 'mob' not in q or q['mob'] is None:
					q['mob'] = '---'
				if 'email' not in q or q['email'] is None:
					q['email'] = '---'
				if 'emp_type__value' not in q or q['emp_type__value'] is None:
					q['emp_type__value'] = '---'
				if 'desg__value' not in q or q['desg__value'] is None:
					q['desg__value'] = '---'
			return JsonResponse(data=qry, status=200, safe=False)

		else:
			msg = "invalid Request"
			status = 502

	else:
		status = 403

################end#################################all emp detail##################


def get_students_hobby_club_details(request):
	if 'HTTP_COOKIE' in request.META:
		if request.method == 'GET':
			session_name = request.session['Session_name']
			studentSession = generate_session_table_name("studentSession_", session_name)
			StudentHobbyClubs = generate_session_table_name("StudentHobbyClubs_", session_name)
			semester = request.GET['semester'].split(',')
			branch = request.GET['branch'].split(',')
			section = request.GET['section'].split(',')
			qry = list(studentSession.objects.filter(section__section__in=section, sem__sem__in=semester, section__dept__in=branch).filter(fee_status="PAID").exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'section__sem_id__sem', 'section__sem_id', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'uniq_id__dept_detail__dept__value', 'uniq_id__lib_id', 'uniq_id__gender__value', 'registration_status').order_by('class_roll_no').distinct())
			data = []
			for q in qry:
				if(q['registration_status'] == 0):
					q['registration_status'] = 'NOT REGISTERED'
				else:
					q['registration_status'] = 'REGISTERED'
				q['hobby_club'] = []
				qry_hobby_club_list = list(StudentHobbyClubs.objects.filter(uniq_id=q['uniq_id'], status="INSERT").values('hobby_club__value', 'hobby_club__field'))
				qry_hobby_club = []
				for i in qry_hobby_club_list:
					qry_hobby_club.append(i['hobby_club__field'] + " (" + i['hobby_club__value'] + ")")
				if len(qry_hobby_club) > 0:
					q['hobby_club'].extend(qry_hobby_club)
			qry_hobby_clubs = list(StudentAcademicsDropdown.objects.filter(field="HOBBY CLUBS").values('sno'))
			qry_h = list(StudentAcademicsDropdown.objects.filter(pid=qry_hobby_clubs[0]['sno']).values_list('sno', flat=True))
			qry_hobby = list(StudentAcademicsDropdown.objects.filter(pid__in=qry_h).values('sno', 'value', 'field').distinct())
			uniq_list = list(StudentHobbyClubs.objects.filter(status="INSERT").values_list('uniq_id', flat=True).distinct())
			hobby_data = []
			for q in qry_hobby:
				uniq_list = list(StudentHobbyClubs.objects.filter(status="INSERT", hobby_club=q['sno']).values_list('uniq_id', flat=True).distinct())
				qry_stu_detail = list(studentSession.objects.filter(section__section__in=section, sem__sem__in=semester, section__dept__in=branch, uniq_id__in=uniq_list).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'section__sem_id__sem', 'section__section', 'year', 'section__sem_id__dept__dept__value', 'class_roll_no', 'uniq_id__uni_roll_no', 'mob', 'uniq_id__lib_id', 'uniq_id__gender', 'uniq_id__gender__value').order_by('class_roll_no'))
				hobby_data.append({"hobby_club": q['field'] + " (" + q['value'] + ")", "stu": qry_stu_detail})
			data.append({"student_wise": qry, "hobby_club": hobby_data})
			return JsonResponse(data=data, status=200, safe=False)

		else:
			msg = "invalid Request"
			status = 502

	else:
		status = 403


def set_hobby_clubs(request):
	session_name = request.session['Session_name']
	studentSession = generate_session_table_name("studentSession_", session_name)
	StudentHobbyClubs = generate_session_table_name("StudentHobbyClubs_", session_name)
	id_all = set(studentSession.objects.filter(registration_status=1, fee_status="PAID").exclude(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list("uniq_id", flat=True).order_by('uniq_id').distinct())
	id_list = set(StudentHobbyClubs.objects.filter(status="INSERT").values_list('uniq_id', flat=True).order_by('uniq_id').distinct())
	not_filled_list = id_all.difference(id_list)
	length = len(not_filled_list)
	rand_list = {}
	for i in not_filled_list:
		loop_len = random.randrange(2, 7)
		h_list = set()
		for j in range(0, loop_len):
			h_id = random.randrange(729, 744)
			h_list.add(h_id)
			j = len(h_list)
		rand_list[i] = list(h_list)
	for i in rand_list:
		for j in rand_list[i]:
			qry = StudentHobbyClubs.objects.create(uniq_id=studentSession.objects.get(uniq_id=i), hobby_club=StudentAcademicsDropdown.objects.get(sno=j))
	data = {'msg': 'Success', 'count': len(rand_list)}

	return JsonResponse(data=data, status=200, safe=False)

def get_hobby_club_student_details(request):
	if 'HTTP_COOKIE' in request.META:
		if request.method == 'GET':
			session_name = request.session['Session_name']
			studentSession = generate_session_table_name("studentSession_", session_name)
			StudentHobbyClubs = generate_session_table_name("StudentHobbyClubs_", session_name)
			semester = request.GET['semester'].split(',')
			branch = request.GET['branch'].split(',')
			section = request.GET['section'].split(',')
			data={}
			qry_hobby_clubs = list(StudentAcademicsDropdown.objects.filter(field="HOBBY CLUBS").values('sno'))
			qry_h = list(StudentAcademicsDropdown.objects.filter(pid=qry_hobby_clubs[0]['sno']).values_list('sno', flat=True))
			qry_hobby = list(StudentAcademicsDropdown.objects.filter(pid__in=qry_h).values('sno', 'value', 'field').distinct())
			for q in qry_hobby:
				uniq_list = list(StudentHobbyClubs.objects.filter(status="INSERT", hobby_club=q['sno'],uniq_id__section__section__in=section, uniq_id__sem__sem__in=semester, uniq_id__section__dept__in=branch,).filter(uniq_id__fee_status="PAID").exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).values('uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__section__sem_id__sem', 'uniq_id__section__sem_id', 'uniq_id__section__section', 'uniq_id__year', 'uniq_id__section__sem_id__dept__dept__value', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__mob', 'uniq_id__uniq_id__dept_detail__dept__value', 'uniq_id__uniq_id__lib_id', 'uniq_id__uniq_id__gender__value').distinct())
				data[q['value']]=uniq_list
			return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)