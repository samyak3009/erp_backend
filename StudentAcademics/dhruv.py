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
import math
from datetime import date
from datetime import datetime
import calendar
import copy
import collections
from operator import itemgetter

from login.models import EmployeeDropdown,EmployeePrimdetail,AuthUser
from musterroll.models import EmployeePerdetail
from Registrar.models import *
from .models import *
from StudentPortal.models import StudentInternshipsTaken

from dashboard.views import academic_calendar
from login.views import checkpermission,generate_session_table_name
from .views import *

def SecGroupReport(request):
	data_values={}
	details=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.method == 'POST':
				check=checkpermission(request,[1369])
				session_name = request.session['Session_name']
				EmpGroupAssign = generate_session_table_name("EmpGroupAssign_",session_name)
				StuGroupAssign = generate_session_table_name("StuGroupAssign_",session_name)
				GroupSection = generate_session_table_name("GroupSection_",session_name)

				if check==200:
					data=json.loads(request.body.decode("utf-8'"))
					semester=data['sem']
					section=data['section']
					department=data['dept']
					sections = list(Sections.objects.filter(sem_id__sem__in=semester,section__in=section,dept__in=department).exclude(status="DELETE").values('section_id','section','sem_id','sem_id__sem','dept__dept__value','dept__course__value'))
					z = len(sections)
					for x in range(z):
						details.append({})
						if 'by'  in data:
							details[x]['details']=list(EmpGroupAssign.objects.filter(emp_id=request.session['hash1'],status="INSERT").exclude(status="DELETE").values('group_id','group_id__group_name','group_id__group_type').distinct())
						else:
							details[x]['details']=list(GroupSection.objects.filter(section_id=sections[x]['section_id']).exclude(group_id__status="DELETE").values('group_id','group_id__group_name','group_id__group_type').distinct())
							for group in details[x]['details']:
								group['stu_list']=list(StuGroupAssign.objects.filter(group_id=group['group_id'],uniq_id__section__section__in=sections[x]['section'],status="INSERT").exclude(status="DELETE").values('uniq_id','uniq_id__uniq_id__name','uniq_id__section__sem_id__sem','uniq_id__section__section','uniq_id__year','uniq_id__section__sem_id__dept__dept__value','uniq_id__class_roll_no','uniq_id__uniq_id__uni_roll_no','uniq_id__mob','uniq_id__registration_status','uniq_id__reg_form_status','uniq_id__reg_date_time','uniq_id__fee_status','uniq_id__att_start_date','uniq_id__uniq_id__dept_detail__dept__value','uniq_id__uniq_id__dept_detail__dept__value','uniq_id__uniq_id__lib_id','uniq_id__uniq_id__gender','uniq_id__uniq_id__gender__value','uniq_id__section__sem_id'))
								group['emp_list']=list(EmpGroupAssign.objects.filter(group_id=group['group_id'],status="INSERT").exclude(status="DELETE").values('emp_id','emp_id__name','emp_id__dept__value').distinct())
							details[x]['branch']=sections[x]['dept__dept__value']
							details[x]['semester']=sections[x]['sem_id__sem']
							details[x]['section']=sections[x]['section']
							details[x]['course']=sections[x]['dept__course__value']
						status=200
						data_values={'data':list(details)}

				else:
					status=403
			else:
				status=502
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=data_values,status=status,safe=False)

def SemSubjectRepot(request):
	data_values={}
	details=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[337])
			if check==200:
				session_name =request.session['Session_name']
				if request.method == 'POST':
					data=json.loads(request.body.decode("utf-8'"))
					sem = (StudentSemester.objects.filter(dept__in=data['dept'],sem__in=data['sem']).values('sem','sem_id','dept__dept__value','dept__course__value'))
					z = len(sem)
					for x in range(z):
						details.append({})
						details[x]['details']=get_sem_filter_subjects(sem[x]['sem_id'],session_name)
						details[x]['branch']=sem[x]['dept__dept__value']
						details[x]['semester']=sem[x]['sem']
						details[x]['course']=sem[x]['dept__course__value']
					status=200
					data_values={'data':details}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=data_values,status=status)

def get_student_attendance_updated(uniq_id, from_date, to_date, session, att_type_li, q_sub, flg_branch_change, att_category_li, session_name):
	att_data = []
	stu_extra_att = []
	class_attendance_type = []

	studentSession = generate_session_table_name("studentSession_", session_name)
	StudentBranchChange = generate_session_table_name("StudentBranchChange_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)

	q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')

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

	q_sub_improvement_att_present = StudentAttStatus.objects.filter(uniq_id=uniq_id, present_status='P', att_type__field__contains="IMPROVEMENT", att_id__subject_id__in=sub_id, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=att_category_li) | Q(att_category__isnull=True)).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(present_count=Count('uniq_id')).order_by()

	improvement_sub_li = [d['att_id__subject_id'] for d in q_sub_improvement_att_present]

	q_sub_normal_att_total = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_id__subject_id__in=sub_id, att_type__in=att_type_li, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_id__group_id__isnull=True) | Q(att_id__group_id__in=q_stu_group)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id__subject_id').annotate(total=Count('uniq_id')).order_by()

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
	year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
	course = q_year[0]['dept__course']

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
			i += 1

	####### CALCULATING EXTRA ATTENDANCE #################
	query_max_extra_capping = StudentAcademicsDropdown.objects.filter(field='MAXIMUM EXTRA ATTENDANCE CAPPING', session=session).exclude(value__isnull=True).exclude(status='DELETE').values('value')
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
		att['absent_count'] = att['total'] - att['present_count']
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
	data['absent_count'] = int(att_total['absent_count'])
	data['total'] = int(att_total['total'])
	data['extra_data'] = att_total['extra']
	data['extra_count'] = branch_change['present'] + min(sub_extra_capping, round((att_total['total'] * max_extra_capping) / 100.0)) + sub_extra_no_capping_total
	data['sub_data'] = att_data
	data['att_type_color'] = get_color()

	return data

def StudentAttendanceRecordUpdated(request):
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
					check = checkpermission(request, [1369, 319, 1371])
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
										# print(zz)
										zz = zz + 1
										listing = get_student_attendance_updated(stu['uniq_id'], max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(stu['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type[:], copy.deepcopy(q_sub), 1, att_category, session_name)
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

def get_students_internship_details(request):
	if 'HTTP_COOKIE' in request.META:
		if request.method == 'GET':
			session_name = request.session['Session_name']
			studentSession = generate_session_table_name("studentSession_", session_name)
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
				q_inter_list = list(StudentInternshipsTaken.objects.filter(uniq_id=q['uniq_id'], status="INSERT").exclude(internship=None).values('internship', 'taken'))
				if (len(q_inter_list) > 0):
					q['internship'] = [internship['internship'] for internship in q_inter_list]
					if(q_inter_list[0]['taken'] == '0'):
						q['taken'] = 'NO'
					else:
						q['taken'] = 'YES'
				else:
					q['internship'] = []
					q['taken'] = None

			data.append({"student_wise": qry})
			return JsonResponse(data=data, safe=False)
		else:
			msg = "invalid Request"
			status = 502

	else:
		status = 403