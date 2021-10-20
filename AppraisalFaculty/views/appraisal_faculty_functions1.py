
# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals

# # '''essentials'''

# from django.http import HttpResponse, JsonResponse
# from django.shortcuts import render
# from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
# import json
# # from datetime import datetime
# # import datetime
# from datetime import datetime
# # import datetime
# import operator


# # '''import constants'''
# from StudentMMS.constants_functions import requestType
# from erp.constants_variables import statusCodes, statusMessages, rolesCheck
# from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
# from AppraisalStaff.views.appraisal_staff_function import *
# from AppraisalStaff.views.appraisal_staff_checks_function import *

# # '''import models'''
# from musterroll.models import EmployeePerdetail, Roles,EmployeeCertification
# from login.models import EmployeePrimdetail
# from login.models import AarDropdown, EmployeeDropdown
# from AppraisalStaff.models import *
# from AppraisalFaculty.models import *
# from AppraisalStaff.constants_functions.functions import *
# from StudentAcademics.models import *
# from Achievement.models import *
# from LessonPlan.models import *

# # '''import views'''
# from AppraisalStaff.views import *
# from Achievement.views.achievement_function import GetAllAchievementEmployee
# from StudentFeedback.views.feedback_function_views import individual_faculty_consolidate, faculty_feedback_details
# from Accounts.views import getCurrentSession
# from StudentAcademics.views import *
# from login.views import checkpermission, generate_session_table_name

# #'''import functions'''
# from aar.dept_achievement import get_all_emp
# from .appraisal_faculty_checks import *

# # Create your views here.


# def create_incial_pending_request(emp_id, session, session_name):
# 	## form_filled_status='N' and form_approved="PENDING" ###
# 	today_date = date.today()
# 	check = FacultyAppraisal.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", session=session, form_filled_status='N', form_approved="PENDING", status="PENDING").exclude(emp_id="00007").exclude(status="DELETE").exclude(emp_id__emp_status="SEPARATE").values('id')
# 	#### CREATE FOR EVERY NEW FORM OPENING AND ANY UPDATION IN DETAILS ####
# 	details = get_emp_part_data(emp_id, session, {})
# 	if len(check) == 0 or check_if_emp_details_same_or_not(emp_id, details, session, session_name) == False:
# 		if len(details) > 0:
# 			FacultyAppraisal.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=details['emp_id']), dept=EmployeeDropdown.objects.get(sno=details['dept']), desg=EmployeeDropdown.objects.get(sno=details['desg']), highest_qualification=details['h_qual'], salary_type=AccountsDropdown.objects.get(sno=details['salary_type_id']), current_gross_salary=details['current_gross_salary'], agp=details['agp'], total_experience=details['total_experience'], emp_date=today_date, session=AccountsSession.objects.get(id=session))
# 			return True
# 		else:
# 			return False
# 	else:
# 		return True


# def get_sno_name_cat1A4(sno):
# 	sno = int(sno)
# 	field = ''
# 	if sno == 0:
# 		field = 'Invigilation at University/Flying Squad/Exam Related duties (2-points/duty)'
# 	if sno == 1:
# 		field = 'Question paper setting at University (3-points/subject)'
# 	if sno == 2:
# 		field = 'Evaluation of answer scripts/practical exam as external expert (5-points/subject)'
# 	return field


# def get_data_in_faculty_form_format(data):
# 	### data-format== course/branch/sem/subject/(session) where {eg:session=2018-2019} #######
# 	format_data = ''
# 	flag = 0
# 	for d in data:
# 		if flag == 0:
# 			format_data = str(d)
# 			flag = 1
# 		else:
# 			format_data = format_data + ' / ' + str(d)
# 	return format_data


# def get_employee_subject_wise_total_lecture(emp_id, session, session_name):
#   ### data-format== course/branch/sem/subject/(session) where {eg:session=2018-2019} #######
#   data = []
#   Sessions = []
#   Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
#   Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
#   for ses in Sessions:
# 	  Attendance = generate_session_table_name('Attendance_', ses)
# 	  qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'subject_id').distinct()
# 	  if len(qry) > 0:
# 		  for q in qry:
# 			  lectures = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", section__sem_id=q['section__sem_id'], subject_id=q['subject_id']).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'section__sem_id__sem', 'section__sem_id__dept__course', 'section__sem_id__dept__course__value', 'section__sem_id__dept__dept', 'section__sem_id__dept__dept__value', 'subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'subject_id__subject_type', 'subject_id__subject_type__value').annotate(total=Count('id')).distinct()
# 			  if len(lectures) > 0:
# 				  lectures[0]['subject'] = '(' + str(lectures[0]['subject_id__sub_alpha_code']) + ' - ' + str(lectures[0]['subject_id__sub_num_code']) + ')'
# 				  format_data_array = [lectures[0]['section__sem_id__dept__course__value'], lectures[0]['section__sem_id__dept__dept__value'], lectures[0]['section__sem_id__sem'], lectures[0]['subject']]
# 				  format_data = str(get_data_in_faculty_form_format(format_data_array))
# 				  lectures[0]['data-format'] = format_data
# 				  lectures[0]['session_name'] = ses
# 				  data.append(lectures[0])
#   return data

# #/////////////////////////////////////////////////YASH///////////////////////////////////////////////////////////////////////////////
# def get_employee_subject_section_wise_lecture_plan(emp_id, session, session_name):
# 	### data-format== course/branch/sem/subject/(session) where {eg:session=2018-2019} #######
# 	data = []
# 	Sessions = []
# 	Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
# 	Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
# 	for ses in Sessions:
# 		Attendance = generate_session_table_name('Attendance_', ses)
# 		LessonProposeApproval = generate_session_table_name('LessonProposeApproval_', ses)
# 		qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'subject_id','section').distinct()
# 		if len(qry) > 0:
# 			for q in qry:
# 				qry_approved_lp = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=q['subject_id'], propose_detail__lesson_propose__added_by=emp_id,propose_detail__lesson_propose__section=q['section']).exclude(status="DELETE").values('propose_detail__id', 'approval_status'))
# 				approved_propose_detail=[]
# 				for qry_app in qry_approved_lp:
# 					if qry_app['propose_detail__id'] not in approved_propose_detail:
# 						approved_propose_detail.append(qry_app['propose_detail__id'])
# 				lectures = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", section__sem_id=q['section__sem_id'], subject_id=q['subject_id'],section=q['section'],normal_remedial='N').exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'section__sem_id__sem', 'section__sem_id__dept__course', 'section__sem_id__dept__course__value', 'section__sem_id__dept__dept', 'section__sem_id__dept__dept__value', 'subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'subject_id__subject_type', 'subject_id__subject_type__value','section__section').annotate(total=Count('id')).distinct()
# 				if len(lectures) > 0:
# 					lectures[0]['subject'] = str(lectures[0]['subject_id__sub_name'])+' (' + str(lectures[0]['subject_id__sub_alpha_code']) + ' - ' + str(lectures[0]['subject_id__sub_num_code']) + ')'
# 					semester =  lectures[0]['section__sem_id__sem']
# 					format_data_array = [lectures[0]['section__sem_id__dept__course__value'], lectures[0]['section__sem_id__dept__dept__value'],semester,lectures[0]['section__section'], lectures[0]['subject']]
# 					format_data = str(get_data_in_faculty_form_format(format_data_array))
# 					lectures[0]['data-format'] = format_data
# 					lectures[0]['session_name'] = ses
# 					lectures[0]['proposed']=len(approved_propose_detail)
# 					data.append(lectures[0])
# 	return data
# #///////////////////////////////////////////////////////////////YASH/////////////////////////////////////////////////////////////////

# def get_overall_att_subject_section_wise_lecture(emp_id, session, session_name):
# 	data = []
# 	Sessions = []
# 	Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
# 	Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
# 	#NORMAL AND TUTORIAL
# 	att_type = list(StudentAcademicsDropdown.objects.filter(value__in=['NORMAL','TUTORIAL'],session__in=[8,9]).values_list('sno',flat=True))
# 	for ses in Sessions:
# 		Attendance = generate_session_table_name('Attendance_', ses)
# 		StudentAttStatus = generate_session_table_name('StudentAttStatus_', ses)
# 		studentSession = generate_session_table_name('studentSession_', ses)
# 		qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id','section__sem_id__dept__course__value','section__sem_id__dept__dept__value','section__sem_id__sem', 'subject_id','section','section__section','subject_id__sub_alpha_code','subject_id__sub_num_code','subject_id__sub_name').distinct()
# 		for q in qry:
# 			lectures = list(Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", section__sem_id=q['section__sem_id'], subject_id=q['subject_id'],section=q['section'],normal_remedial='N').exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values_list("id",flat=True))
# 			total_present_in_lec = StudentAttStatus.objects.filter(marked_by=emp_id,marked_by__emp_category__value="FACULTY",present_status="P",approval_status="APPROVED",att_id__in=lectures,att_type__in=att_type).exclude(status="DELETE").exclude(marked_by__emp_status="SEPARATE").exclude(marked_by="00007").count()
# 			total_strength = StudentAttStatus.objects.filter(marked_by=emp_id,marked_by__emp_category__value="FACULTY",present_status__in=["P","A"],approval_status="APPROVED",att_id__in=lectures,att_type__in=att_type).exclude(status="DELETE").exclude(marked_by__emp_status="SEPARATE").exclude(marked_by="00007").count()
# 			if len(lectures) > 0:
# 				q['subject'] = '(' + str(q['subject_id__sub_alpha_code']) + ' - ' + str(q['subject_id__sub_num_code']) + ')'
# 				q['total_present_in_lec'] = total_present_in_lec
# 				q['total_strength'] = total_strength
# 				semester = int_to_Roman(int(q['section__sem_id__sem']))
# 				format_data_array = [q['section__sem_id__dept__course__value'], q['section__sem_id__dept__dept__value'],semester,q['section__section'], q['subject']]
# 				format_data = str(get_data_in_faculty_form_format(format_data_array))
# 				q['data-format'] = format_data
# 				q['session_name'] = ses
				
# 				data.append(q)
# 	return data


# def get_employee_subject_setion_wise_total_lecture(emp_id, session, session_name):
# 	### data-format== course/branch/sem/subject/section(session) where {eg:session=2018-2019} #######
# 	data = []
# 	Sessions = []
# 	Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
# 	Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
# 	subject_type = set()
# 	for ses in Sessions:
# 		Attendance = generate_session_table_name('Attendance_', ses)
# 		qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").exclude(subject_id__max_university_marks=0).values('section__sem_id', 'subject_id', 'section','subject_id__sub_name','subject_id__sub_alpha_code','subject_id__sub_num_code').distinct()
# 		if len(qry) > 0:
# 			for q in qry:
# 				lectures = list(Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY", subject_id=q['subject_id'], section=q['section']).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values('section__sem_id', 'section__sem_id__sem', 'section__sem_id__dept__course', 'section__sem_id__dept__course__value', 'section__sem_id__dept__dept', 'section__sem_id__dept__dept__value', 'subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'section', 'section__section', 'subject_id__subject_type', 'subject_id__subject_type__value').distinct())
# 				for x in lectures:
# 					x['subject'] = '(' + str(x['subject_id__sub_alpha_code']) + ' - ' + str(x['subject_id__sub_num_code']) + ')'
# 					format_data_array = [x['section__sem_id__dept__course__value'], x['section__sem_id__dept__dept__value'], x['section__sem_id__sem'], x['subject']]
# 					format_data = str(get_data_in_faculty_form_format(format_data_array))
# 					x['data-format'] = format_data
# 					x['session_name'] = ses
# 					data.append(x)

# 					subject_type.add(x['subject_id__subject_type'])
# 	return [data, subject_type]
# #/////////////////////////////////////////////////////////////////YASH////////////////////////////////////////////////////////////////

# def get_average_cat1(data, part):
# 	total = 0
# 	no_of_rows = len(data)
# 	if len(data) > 0:
# 		if part == "A1":
# 			for d in data:
# 				total = total + d['score_claimed']
# 			total = total / no_of_rows
# 			if total > 50:
# 				total = 50
# 		if part == "A2":
# 			for d in data:
# 				total = total + d['score_claimed']
# 			if total > 15:
# 				total = 15
# 		if part == "A3":
# 			for d in data:
# 				total = total + d['score_claimed']
# 			if total > 15:
# 				total = 15
# 		if part == "A4":
# 			for d in data:
# 				total = total + d['score_claimed']
# 			if total > 20:
# 				total = 20
# 	return total




# # def get_cat1_form_data(emp_id, level, session, session_name):
# #   if int(level) > 1:
# #       level = 1

# #   final_data = {}
# #   extra_filter = {}
# #   extra_filter1 = {}
# #   statuses = []
# #   #### NO. OF SUBPARTS IN CAT1 = 4 ####
# #   for i in range(1, 8):
# #       data = {}
# #       data['data'] = []
# #       data['heading'] = []
# #       if str('A' + str(i)) not in final_data:
# #           final_data[str('A' + str(i))] = {}
# #       # for l in range(0, len(level)):
# #       #### GET STATUSES ####
# #       statuses = []
# #       status = []
# #       if int(level) <= 1:
# #           status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level)).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
# #           if len(status) == 0:
# #               statuses.append({'status': "PENDING"})
# #           else:
# #               for s in status:
# #                   statuses.append({'status': s['approval_status']})
# #       if len(status) == 0:
# #           statuses.append({'status': "PENDING"})
# #       ######################
# #       # for status in statuses:
# #       row_data = {}
# #       if statuses[0]['status'] != "PENDING":
# #           extra_filter = {'status': statuses[0]['status']}
# #       else:
# #           extra_filter = {}
# #       if i == 1 or i == 2:  # FOR A1&A2 ####
# #           lectures_wise_data = get_employee_subject_wise_total_lecture(emp_id, session, session_name)
# #       if i == 1:
# #           qry = FacAppCat1A1.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('course_paper', 'lectues_calendar', 'lectues_portal', 'score_claimed', 'score_awarded', 'fac_app_id').order_by('-fac_app_id')
# #           data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# #           data['total'] = 0
# #           if len(qry) > 0:
# #               for q in qry:
# #                   row_data = {}
# #                   if len(statuses) > 1:
# #                       if 'REVIEWED' in statuses[-1]['status']:
# #                           extra_filter1 = ({'status': 'REVIEWED'})
# #                       else:
# #                           extra_filter1 = ({'status': 'APPROVED'})
# #                       query = FacAppCat1A1.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session, course_paper=q['course_paper']).filter(**extra_filter1).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('score_awarded', 'fac_app_id').order_by('-fac_app_id')
# #                       if len(query) > 0:
# #                           row_data['score_reviewed'] = query[0]['score_awarded']

# #                   if q['lectues_calendar'] != None and q['lectues_portal'] != None:
# #                       difference = int(q['lectues_calendar']) - int(q['lectues_portal'])
# #                       percentange = (int(q['lectues_portal']) / int(q['lectues_calendar'])) * 100
# #                   else:
# #                       difference = 0
# #                       percentange = 0

# #                   if q['score_claimed'] != None:
# #                       score_claimed = float(q['score_claimed'])
# #                   else:
# #                       score_claimed = 0

# #                   row_data.update({'course_paper': q['course_paper'], 'lec_per_academic': q['lectues_calendar'], 'lec_per_taken': q['lectues_portal'], 'diff': abs(difference), '%_as_per_doc': percentange, 'score_claimed': score_claimed})
# #                   ####### for level==1 ##########
# #                   if int(level) >= 1:
# #                       if statuses[0]['status'] == "PENDING":
# #                           row_data['score_awarded'] = q['score_claimed']
# #                       else:
# #                           row_data['score_awarded'] = q['score_awarded']
# #                   ###############################
# #                   data['data'].append(row_data)
# #               data['total'] = get_average_cat1(qry, 'A' + str(i))

# #           else:
# #               for lec in range(0, len(lectures_wise_data)):
# #                   row_data = {'course_paper': lectures_wise_data[lec]['data-format'], 'lec_per_academic': lectures_wise_data[lec]['total'], 'lec_per_taken': lectures_wise_data[lec]['total'], 'diff': None, '%_as_per_doc': None, 'score_claimed': None}
# #                   ###### for level==1 ###########
# #                   if int(level) >= 1:
# #                       row_data['score_awarded'] = None
# #                   ###############################
# #                   data['data'].append(row_data)
# #           final_data['A' + str(i)] = data
# #       if i == 2:
# #           qry = FacAppCat1A2.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('course_paper', 'consulted', 'prescribed', 'additional_resource', 'score_claimed', 'score_awarded', 'fac_app_id').order_by('-fac_app_id')
# #           data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# #           data['total'] = 0
# #           if len(qry) > 0:
# #               for q in qry:
# #                   row_data = {}
# #                   if len(statuses) > 1:
# #                       if 'REVIEWED' in statuses[-1]['status']:
# #                           extra_filter1 = ({'status': 'REVIEWED'})
# #                       else:
# #                           extra_filter1 = ({'status': 'APPROVED'})
# #                       query = FacAppCat1A2.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session, course_paper=q['course_paper']).filter(**extra_filter1).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('score_awarded', 'fac_app_id').order_by('-fac_app_id')
# #                       if len(query) > 0:
# #                           row_data['score_reviewed'] = query[0]['score_awarded']
# #                   if q['score_claimed'] == None:
# #                       q['score_claimed'] = 0
# #                   row_data.update({'course_paper': q['course_paper'], 'consulted': q['consulted'], 'prescribed': q['prescribed'], 'additional_resource': q['additional_resource'], 'score_claimed': q['score_claimed']})
# #                   ####### for level==1 ##########
# #                   if int(level) >= 1:
# #                       if statuses[0]['status'] == "PENDING":
# #                           row_data['score_awarded'] = q['score_claimed']
# #                       else:
# #                           row_data['score_awarded'] = q['score_awarded']
# #                   ###############################
# #                   data['data'].append(row_data)
# #               data['total'] = get_average_cat1(qry, 'A' + str(i))

# #           else:
# #               for lec in range(0, len(lectures_wise_data)):
# #                   row_data = {'course_paper': lectures_wise_data[lec]['data-format'], 'consulted': None, 'prescribed': None, 'additional_resource': None, 'score_claimed': None}
# #                   ###### for level==1 ###########
# #                   if int(level) >= 1:
# #                       row_data['score_awarded'] = None
# #                   ###############################
# #                   data['data'].append(row_data)
# #           final_data['A' + str(i)] = data

# #       if i == 3:
# #           qry = FacAppCat1A3.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('fac_app_id', 'description', 'score_claimed', 'score_awarded', 'short_descriptn').order_by('-fac_app_id')
# #           data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# #           data['total'] = 0
# #           if len(qry) > 0:
# #               for q in qry:
# #                   row_data = {}
# #                   if len(statuses) > 1:
# #                       if 'REVIEWED' in statuses[-1]['status']:
# #                           extra_filter1 = ({'status': 'REVIEWED'})
# #                       else:
# #                           extra_filter1 = ({'status': 'APPROVED'})
# #                       query = FacAppCat1A3.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session, short_descriptn=q['short_descriptn']).filter(**extra_filter1).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('score_awarded', 'fac_app_id').order_by('-fac_app_id')
# #                       if len(query) > 0:
# #                           row_data['score_reviewed'] = query[0]['score_awarded']
# #                   if q['score_claimed'] == None:
# #                       q['score_claimed'] = 0
# #                   row_data.update({'short_descriptn': q['short_descriptn'], 'score_claimed': q['score_claimed']})
# #                   ####### for level==1 ##########
# #                   if int(level) >= 1:
# #                       if statuses[0]['status'] == "PENDING":
# #                           row_data['score_awarded'] = q['score_claimed']
# #                       else:
# #                           row_data['score_awarded'] = q['score_awarded']
# #                   ###############################
# #                   data['data'].append(row_data)
# #               data['total'] = get_average_cat1(qry, 'A' + str(i))

# #           else:
# #               row_data = {'short_descriptn': None, 'score_claimed': None}
# #               ###### for level==1 ###########
# #               if int(level) >= 1:
# #                   row_data['score_awarded'] = None
# #               ###############################
# #               data['data'].append(row_data)
# #           final_data['A' + str(i)] = data

# #       if i == 4:
# #           qry = FacAppCat1A4.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('fac_app_id', 'sno', 'executed', 'extent_to_carried', 'duties_assign', 'score_claimed', 'score_awarded').order_by('-fac_app_id', 'sno')
# #           data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# #           data['total'] = 0
# #           if len(qry) > 0:
# #               for q in qry:
# #                   row_data = {}
# #                   if len(statuses) > 1:
# #                       if 'REVIEWED' in statuses[-1]['status']:
# #                           extra_filter1 = ({'status': 'REVIEWED'})
# #                       else:
# #                           extra_filter1 = ({'status': 'APPROVED'})
# #                       query = FacAppCat1A4.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session, executed=q['executed']).filter(**extra_filter1).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('score_awarded', 'fac_app_id').order_by('-fac_app_id')
# #                       if len(query) > 0:
# #                           row_data['score_reviewed'] = query[0]['score_awarded']
# #                   if q['score_claimed'] == None:
# #                       q['score_claimed'] = 0
# #                   row_data.update({'type_of_duty': get_sno_name_cat1A4(q['sno']), 'duties_assign': q['duties_assign'], 'executed': q['executed'], 'extent_to_carried': q['extent_to_carried'], 'score_claimed': q['score_claimed']})
# #                   ####### for level==1 ##########
# #                   if int(level) >= 1:
# #                       if statuses[0]['status'] == "PENDING":
# #                           row_data['score_awarded'] = q['score_claimed']
# #                       else:
# #                           row_data['score_awarded'] = q['score_awarded']
# #                   ###############################
# #                   data['data'].append(row_data)
# #               data['total'] = get_average_cat1(qry, 'A' + str(i))
# #           else:
# #               #### SINCE SNO IN A4 IS 0,1,2 #############
# #               for sno in range(0, 3):
# #                   row_data = {'type_of_duty': get_sno_name_cat1A4(sno), 'duties_assign': None, 'executed': None, 'extent_to_carried': None, 'score_claimed': None}
# #                   ###### for level==1 ###########
# #                   if int(level) >= 1:
# #                       row_data['score_awarded'] = None
# #                   ###############################
# #                   data['data'].append(row_data)
# #           final_data['A' + str(i)] = data
# #   return final_data

# #///////////////////////////////////////////////////////////YASH//////////////////////////////////////////////////////////////////////
# def get_score_cat1_A1(per):
# 	per_point_marks =10/((100-80)+1)
# 	if per<80:
# 		score_claimed=0
# 	else:
# 		score_claimed = round((per-79)*per_point_marks,2)
# 	return score_claimed

# def get_heading_of_cat1(part, level, status):
# 	part = str(part)
# 	heading = []
# 	if part == "A1":
# 		main_heading = "<b>Lectures(including additional skills subjects), Seminars, Tutorials, Practical’s, Project Guidance (B.Tech, B.Pharm, M.Tech, M.Pharm, MBA, MCA)  Contact Hour (Give semester wise details, where necessary)</b>"
# 		heading = ['Course/Paper & Year', 'Total lectures as per academic calendar (a)', 'Total no of lecture takne as per portal (b)', '% of classes taken as per documented record', 'Score claimed by the Faculty']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A2":
# 		main_heading  = "<b> Percentage of average attendance (Max. 5 Marks)</b>"
# 		heading = ['Subject Taught', '% of Average Attendance', 'Score obtained as per % of attendance']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A3":
# 		main_heading = ""
# 		heading = ['Details of MOOC’s Developed (1 MOOCs/05 Marks)','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A4":
# 		main_heading = ""
# 		heading = ['<b>MOOC’s (NPTEL/Coursera/edx) Certification Gold-10 Marks,Elite-8 Marks, Pass-5 Marks</b>','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A5":
# 		main_heading = "<b>Academic Result (Entire Academic Year)</b>"
# 		heading = ['Branch/Semester/Section','Subject','Result (Clear Pass %','Result (Ext.Theory Exam Average','No of Students with marks in external exam']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A6":
# 		main_heading = "<b>Invited Lectures/ presentation in conferences/ talks in refresher courses at National or International Conference/Seminars</b> (International (out of India) -5 Marks, National (within India) -2.5 Marks each) <b>(Max:5 Marks)</b>"
# 		heading = ['Details of event','Class/ Talk or session Chair','International/National','Score claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A7":
# 		main_heading = "<b>1 week Industrial training/Professional Training,1 week refresher program, 1 week FDP attended or organized </b>[Attended other than ICT mode- 2 Marks each, Attended ICT mode-1 marks each, Organized other than ICT mode- 3 Marks each, Organized ICT mode- 2 marks each].(If more than one coordinator then 3 or 2 marks equally divided between them)    <b>(Max:5 Marks)</b>"
# 		heading = ['Programme','Duration','Organized by','score claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A8":
# 		main_heading = "<b>Feedback Survey</b>"
# 		heading = ['Branch','Semester','Section','Subject','Student feedback','Overall Average']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	return {'main_heading':main_heading,'heading':heading}




# def get_cat1_form_data(emp_id, level, session, session_name):
# 	if int(level) > 1:
# 		level = 1

# 	final_data = {}
# 	extra_filter = {}
# 	extra_filter1 = {}
# 	statuses = []
# 	category = 'Category1'
# 	final_data['main_heading'] = "CATEGORY -I (Maximum Marks: 100) (TEACHING, LEARNING & ACADEMIC RELATED ACTIVITIES)"
# 	#### NO. OF SUBPARTS IN CAT1 = 8 ####
# 	for i in range(1, 9):
# 		data = {}		
# 		data['heading'] = []
# 		if str('A' + str(i)) not in final_data:
# 			final_data[str('A' + str(i))] = {}

# 		statuses = []
# 		status = []
# 		if int(level) <= 1:
# 			status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level)).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
# 			if len(status) == 0:
# 				statuses.append({'status': "PENDING"})
# 			else:
# 				for s in status:
# 					statuses.append({'status': s['approval_status']})
# 		if len(status) == 0:
# 			statuses.append({'status': "PENDING"})
# 		if i==1:
# 			data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# 			sub_category = str('A' + str(i))
# 			lectures = get_employee_subject_section_wise_lecture_plan(emp_id, session, session_name)
# 			qry = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 			if len(qry)>0:
# 				data['data'] = qry
# 				final_data['A' + str(i)] = data
# 			else:
# 				add_per_rows = 0
# 				for lec in lectures:
# 					if lec['proposed']!=0:
# 						lec['difference'] = lec['proposed']-lec['total']
# 						if lec['total']<lec['proposed']:
# 							lec['% of classes taken'] = round((lec['total']/lec['proposed'])*100,2)
# 						else :
# 							lec['% of classes taken'] = 100
# 					else:
# 						lec['proposed'] = "----"
# 						lec['% of classes taken'] = 100
# 					lec['score_claimed']=get_score_cat1_A1(lec['% of classes taken'])
# 					if lec['score_claimed']==0:
# 						percent_per_rows =0
# 					percent_per_rows = round((lec['score_claimed']/10)*100,2)
# 					add_per_rows = add_per_rows+percent_per_rows

# 				avg = round(add_per_rows/len(lectures),2)
# 				data['lec']=lectures
# 				data['avg']=avg
# 				if avg < 80:
# 					data['score_claimed'] = 0
# 				else:
# 					data['overall_score_claimed'] = get_score_cat1_A1(avg)
# 				final_data['A' + str(i)] = data
# 		if i ==2 :
# 			data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# 			sub_category = str('A' + str(i))
# 			attendance = get_overall_att_subject_section_wise_lecture(emp_id, session, session_name)
# 			qry = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 			if len(qry)>0:
# 				data['data'] = qry
# 				# final_data['A' + str(i)] = data
# 			else:
# 				add_per_rows = 0
# 				for att in attendance:
# 					att['avg'] = 0
# 					if(att['total_strength'])>0:
# 						avg = round(att['total_present_in_lec']/att['total_strength']*100,2)
# 						att['avg'] = avg
# 					if avg >=90:
# 						att['score'] = 5
# 					elif avg<90 and avg>=85:
# 						att['score']=4
# 					elif avg<85 and avg>=80:
# 						att['score']=3
# 					elif avg<80 and avg>=75:
# 						att['score']=2
# 					elif avg<75 and avg>=70:
# 						att['score']=1
# 					else:
# 						att['score']=0
# 					add_per_rows = add_per_rows+att['score']

# 				avg_row_per = round(add_per_rows/len(attendance),2)
# 				data['lec']=attendance
# 				data['avg']=avg_row_per
# 				data['avg_per'] = round((data['avg']/5)*100,2)
# 			final_data['A' + str(i)] = data
# 		if i==3:
# 			data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# 			sub_category = str('A' + str(i))
# 			qry = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 			if len(qry)>0:
# 				data['data'] = qry
# 			final_data['A' + str(i)] = data
# 		if i==4:
# 			data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# 			sub_category = str('A' + str(i))
# 			qry = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 			if len(qry)>0:
# 				data['data'] = qry
# 			else:
# 				certificate = EmployeeCertification.objects.filter(emp_id=emp_id).exclude(status="DELETE").values("course_name","certified_by","mooc_type__value","link")
# 				# if "Elite + Gold" in certificate:
# 				#   data['score_claimed']=10
# 				# elif "Elite + Silver" in certificate:
# 				#   data['score_claimed'] = 8
# 				# elif "Elite" in certificate:
# 				#   data['score_claimed'] = 7
# 				# else:
# 				#   data['score_claimed'] = 5
# 			final_data['A' + str(i)] = data
# 		if i==5 or i==8:
# 			lectures_data = get_employee_subject_setion_wise_total_lecture(emp_id, session, session_name)
# 			lectures = lectures_data[0]
# 			subject_type = lectures_data[1]

# 		if i==5:
# 			data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# 			sub_category = str('A' + str(i))
# 			lectures_data = get_employee_subject_setion_wise_total_lecture(emp_id, session, session_name)
# 			lectures = lectures_data[0]
# 			data['data']=[]
# 			for lec in lectures:
# 				semester = int_to_Roman(int(lec['section__sem_id__sem']))
# 				format_data = [lec['section__sem_id__dept__course__value'],lec['section__sem_id__dept__dept__value'], semester, lec['section__section']]
# 				lec['data-format'] = get_data_in_faculty_form_format(format_data)
# 				lec['university_marks'] = get_university_marks_subject_wise(lec)
# 				data['data'].append(lec)
# 			data['last_xyrs_data']=get_past_marks_details(emp_id, session, session_name)

# 			final_data['A' + str(i)] = data
# 		if i==6:
# 			data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# 			sub_category = str('A' + str(i))
# 			qry = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 			if len(qry)>0:
# 				data['data'] = qry
# 			else:
# 				lec_achievement = GetAllAchievementEmployee(emp_id,"LECTURES AND TALKS",session)
# 				score_claimed = 0
# 				if len(lec_achievement)>0:
# 					for ach in lec_achievement:
# 						if 'NATIONAL' in ach['type_of_event__value']:
# 							score_claimed = score_claimed+2.5
# 							ach['score_claimed'] = 2.5
# 						elif 'INTERNATIONAL' in ach['type_of_event__value']:
# 							score_claimed = score_claimed+5
# 							ach['score_claimed'] = 5
# 					data['score_claimed'] = round((score_claimed/len(lec_achievement)),2)
# 				else:
# 					data['score_claimed'] = score_claimed
# 				data['lec_ach'] = lec_achievement

# 			final_data['A' + str(i)] = data
# 		if i==7:
# 			data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# 			sub_category = str('A' + str(i))
# 			qry = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 			if len(qry)>0:
# 				data['data'] = qry
# 			else:
# 				score_claimed =0
# 				train_achievement = GetAllAchievementEmployee(emp_id,"TRAINING AND DEVELOPMENT PROGRAM",session)
# 				if len(train_achievement)>0:
# 					for tr_ach in train_achievement:
# 						# if 'FDP' in tr_ach['category__value']:
# 						week_check_days =(tr_ach['to_date']-tr_ach['from_date'])
# 						if int(week_check_days.days)>=5:
# 							if 'ATTENDED' in tr_ach['role__value'] and tr_ach['training_sub_type__value'] is not None:
# 								if 'OTHER THAN ICT MODE' in tr_ach['training_sub_type__value']:
# 									score_claimed = score_claimed+1
# 									tr_ach['score_claimed'] = 1
# 								elif 'ICT MODE' in tr_ach['training_sub_type__value']:
# 									score_claimed = score_claimed+2
# 									tr_ach['score_claimed'] = 2
# 							elif 'ORGANIZED' in tr_ach['role__value'] and tr_ach['training_sub_type__value'] is not None:
# 								if 'ICT MODE' in tr_ach['training_sub_type__value']:
# 									score_claimed = score_claimed+3
# 									tr_ach['score_claimed'] = 3
# 								elif 'OTHER THAN ICT MODE' in tr_ach['training_sub_type__value']:
# 									score_claimed = score_claimed+2
# 									tr_ach['score_claimed'] = 2
# 						else:
# 							tr_ach['score_claimed'] = 0
# 					data['score_claimed'] = round((score_claimed/len(train_achievement)),2)
# 				else:
# 					data['score_claimed'] = score_claimed
# 				data['tr_ach'] = train_achievement
# 			final_data['A' + str(i)] = data

# 		if i == 8:
# 			data['heading'] = get_heading_of_cat1('A' + str(i), level, statuses)
# 			sub_category = str('A' + str(i))
# 			qry = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 			if len(qry)>0:
# 				data['data'] = qry
# 			else:
# 				data['data']=[]
# 				Sessions = []
# 				Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
# 				Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
# 				for ses in Sessions:
# 					temp_data = []
# 					feedback = faculty_feedback_details([emp_id], ses, subject_type)
# 					if len(feedback) > 0:
# 						for f_back in feedback:
# 							row_data = {'branch': f_back['branch'], 'semester': f_back['sem'], 'section': f_back['section'], 'subject': f_back['subject'], 'overall_avg': f_back['TOTAL'], 'student_feedback': f_back['TOTAL'], 'score_claimed': None}
# 							data['data'].append(row_data)
# 							temp_data.append(row_data)
# 						data['f' + str(ses[-1])] = get_total_of_cat1(temp_data, 'A' + str(i), level, statuses)['overall_feedback']
# 				if 'fo' not in data and 'fe' in data:
# 					data['final_feedback'] = round(data['fe'], 2)

# 				elif 'fe' not in data and 'fo' in data:
# 					data['final_feedback'] = round(data['fo'], 2)
# 				elif 'fe' not in data and 'fe' not in data:
# 					data['final_feedback'] = round(0, 2)
# 				else:
# 					data['final_feedback'] = round(((data['fo'] + data['fe']) / 2), 2)

# 				data['final_total'] = 0

# 				if data['final_feedback'] != None and data['final_feedback'] > 0:
# 					if data['final_feedback'] >= 8.4:
# 						data['final_total'] = 30
# 					elif data['final_feedback'] >= 6.5 and data['final_feedback'] < 8.4:
# 						difference = data['final_feedback'] - 6.4
# 						data['final_total'] = round((difference/0.1) *1.5, 2)
# 				#### FOR LEVEL=1 ####
# 				if int(level) >= 1:
# 					data['score_awarded'] = data['final_total']

# 				#####################
# 				total = get_total_of_cat1(data['data'], 'A' + str(i), level, statuses)

# 				for k, v in total.items():
# 					data[k] = round(v, 2)
# 			final_data['A' + str(i)] = data

# 	return final_data



# def get_total_of_cat1(data, part, level, status):
# 	total_data = 0
# 	length = len(data)
# 	part = str(part)
# 	# if 'A1' in part:
# 	#   total_data = {'total': 0, 'result_per': 0, 'ext_theory': 0, 'below_40': 0, 'in_40_49': 0, 'in_50_59': 0, 'above_60': 0}
# 	#   for d in data:
# 	#       if '-INST(1)' not in str(d['branch']) and '-INST(2)' not in str(d['branch']):
# 	#           total_data['result_per'] = total_data['result_per'] + d['pass_per']
# 	#           total_data['ext_theory'] = total_data['ext_theory'] + d['average_external']
# 	#           total_data['below_40'] = total_data['below_40'] + d['below_40']
# 	#           total_data['in_40_49'] = total_data['in_40_49'] + d['in_40_49']
# 	#           total_data['in_50_59'] = total_data['in_50_59'] + d['in_50_59']
# 	#           total_data['above_60'] = total_data['above_60'] + d['above_60']
# 	#       if d['score_claimed'] != None:
# 	#           total_data['total'] = total_data['total'] + d['score_claimed']
# 	#   if int(length) != 0:
# 	#       total_data['result_per'] = total_data['result_per'] / length
# 	#       total_data['ext_theory'] = total_data['ext_theory'] / length
# 	if 'A8' in part:
# 		total_data = {'overall_feedback': 0, 'total': 0}
# 		# print("data A2", data)
# 		for d in data:
# 			total_data['overall_feedback'] = total_data['overall_feedback'] + d['student_feedback']

# 		if int(length) > 0:
# 			total_data['overall_feedback'] = round(total_data['overall_feedback'] / length, 2)
# 			if float(total_data['overall_feedback']) >= 8.4:
# 				total_data['total'] = 30
# 			elif float(total_data['overall_feedback']) >= 6.5 and float(total_data['overall_feedback']) < 8.4:
# 				difference = total_data['overall_feedback'] - 6.4
# 				total_data['total'] = round(float(difference/0.1) *1.5, 2)
# 			if int(level) >= 1:
# 				if len(status) == 1:
# 					total_data['score_awarded'] = total_data['total']
# 				else:
# 					total_data['score_awarded'] = total_data['total']
# 					total_data['score_reviewed'] = total_data['total']
# 	return total_data




# def get_last_x_year_ses(session_name,x):
# 	year = []
# 	for i in range(1,x+1):
# 		Sessions=[]
# 		Sessions.append(str(int(session_name[:2]) - i) + str(int(session_name[:2]) - (i-1)) + 'o')
# 		Sessions.append(str(int(session_name[:2]) - i) + str(int(session_name[:2]) - (i-1)) + 'e')
# 		year.append(Sessions)
# 	return year


# def get_past_marks_details(emp_id, session, session_name):
# 	year = get_last_x_year_ses(session_name,5)
# 	Sessions=[]
# 	Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
# 	Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
# 	data_list =[]
# 	for ses in Sessions:
# 		Attendance = generate_session_table_name('Attendance_', ses)
# 		qry = Attendance.objects.filter(emp_id=emp_id, emp_id__emp_category__value="FACULTY").exclude(subject_id__max_university_marks=0).exclude(emp_id__emp_status="SEPARATE").exclude(emp_id="00007").exclude(status="DELETE").values( 'subject_id','subject_id__sub_name','subject_id__sub_alpha_code','subject_id__sub_num_code','section__sem_id','section__sem_id__dept').distinct()
# 		for q in qry:
# 			data={}
# 			year_li =[]
# 			for y,s in enumerate(year,1):
# 				data_li ={}
# 				data_dict={"mo":None,"me":None}
# 				for i in range(2):
# 					try:
# 						SubjectInfo = generate_session_table_name('SubjectInfo_',s[i])
# 						StudentUniversityMarks = generate_session_table_name('StudentUniversityMarks_', s[i])
# 						ses_sub_id = list(SubjectInfo.objects.filter(sub_name=q['subject_id__sub_name'],sub_alpha_code=q['subject_id__sub_alpha_code'],sub_num_code=q['subject_id__sub_num_code'],sem_id__dept=q['section__sem_id__dept']).exclude(max_university_marks=0).exclude(status="DELETE").values('id'))
# 						univ_marks = list(StudentUniversityMarks.objects.filter( subject_id=ses_sub_id[0]['id']).values_list('uniq_id', flat=True).exclude(subject_id__status="DELETE").values('subject_id', 'subject_id__max_ct_marks', 'subject_id__max_ta_marks', 'subject_id__max_att_marks', 'subject_id__max_university_marks', 'external_marks', 'internal_marks', 'back_marks', 'uniq_id').order_by('uniq_id'))
# 						if(len(univ_marks)>0) and 'e' in s[i]:
# 							data_dict['me'] = get_external_exam_average(univ_marks)
# 						elif len(univ_marks)>0 and 'o' in s[i]:
# 							data_dict['mo'] = get_external_exam_average(univ_marks)
# 					except:
# 						pass
# 				if  data_dict['mo'] is not None and data_dict['me'] is None:
# 					data_li['year']=s[i][:-1]
# 					data_li['marks']  = data_dict['mo']
# 				elif  data_dict['me'] is not None and data_dict['mo'] is None:
# 					data_li['year']=s[i][:-1]
# 					data_li['marks']  = data_dict['me']
# 				elif  data_dict['mo'] is  None and data_dict['me'] is None:
# 					data_li['year']=s[i][:-1]
# 					data_li['marks']  = 0
# 				else:
# 					data_li['year']=s[i][:-1]
# 					data_li['marks'] = round((data_dict['mo']+data_dict['me'])/2,2)
# 				year_li.append(data_li)
# 			data['sub']= q['subject_id__sub_name']
# 			data['old']=year_li
# 			data['new']=[{"name":"fghj","marks":34}]

# 			data_list.append(data)
# 	return data_list


# #/////////////////////////////////////////////////////////YASH///////////////////////////////////////////////////////////////////////////////////// 
	
# def get_heading_of_cat3(part, level, status):
# 	part = str(part)
# 	heading = []
# 	main_heading = "Extension, Co-curricular, Field based activities, Contribution to corporate life, management of the Institution and Professional Development Activities (* All activities during Academic Year)"
# 	if part == "A1":
# 		heading = ['Departmental Activities (Max:20 Marks) (Max: 3 Marks/ semester/ activity for Mentor/Class Coordinator or Lab IC, Time Table IC, Consultancy, etc), (2 Marks per event for Organizing event at departmental level), (1 Mark per event to be divided between all co-coordinators)','Score claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A2":
# 		heading = ['Monthly/on occurrence uploading of data as individual and Coordinator on KIET ERP (Max:3 Marks)','Score claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part =='A3':
# 		heading = ['Publicity of different events on social media on regular basis (Max:2 Marks)','Score claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A4":
# 		heading = ['Institute Activity (Max: 15 Marks) (Max: 10 Marks/semester/activity for Chief Proctor/Additional HoD/Associate Dean (SW) / Assistant Dean (A)/ IQAC Coordinator/Chief Rector/Digital/NAAC/NBA Coordinator, etc),(5 marks per activity-Rector/Proctor)(3 Marks per activity for coordinator at institute level),(2 mark per event to be divided between all co-coordinators)','Score claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')

# 	return {"main_heading":main_heading,"heading":heading}



# def get_cat3_form_data(emp_id, level, session, session_name):
# 	### SCORE CLAIMED IS INPUT FIELD ###

# 	if int(level) > 1:
# 		level = 1

# 	final_data = {}
# 	extra_filter = {}
# 	statuses = []
# 	for i in range(1, 5):
# 		data = {}
# 		data['data'] = []
# 		data['heading'] = []
# 		if str('A' + str(i)) not in final_data:
# 			final_data[str('A' + str(i))] = {}
# 		if i==1:
# 			data['heading'] = get_heading_of_cat3('A' + str(i), level, statuses)
# 			row_data={"score_claimed":11,"column1":45}
# 		if i==2:
# 			data['heading'] = get_heading_of_cat3('A' + str(i), level, statuses)
# 			row_data={"score_claimed":11,"column1":45}
# 		if i==3:
# 			data['heading'] = get_heading_of_cat3('A' + str(i), level, statuses)
# 			row_data={"score_claimed":11,"column1":45}
# 		if i==4:
# 			data['heading'] = get_heading_of_cat3('A' + str(i), level, statuses)
# 			row_data={"score_claimed":11,"column1":45}
# 		data['data'].append(row_data)
# 		final_data['A' + str(i)] = data

# 	return final_data

# def get_total_of_cat2(data, part):
# 	total = 0
# 	no_of_rows = len(data)
# 	for d in data:
# 		if d['score_claimed'] != None:
# 			total = total + d['score_claimed']
# 	if total > 50:
# 		total = 50
# 	return total


# def get_heading_of_cat2(part, level, status):
# 	part = str(part)
# 	heading = []
# 	if part == "A1":
# 		main_heading = ['Papers Published in Indexed journals- SCI/SCI-E/SSCI/ESCI/SCOPUS for faculty members having experience more than 3 years.Papers Published in UGC listed Journals for faculty members having experience less than 3 years.(15 Marks for single author, 9 Marks for 1st author and Supervisor and 6 Marks for others and these will be augmented as “SCI/SCI-E/SSCI/ESCI/SCOPUS Impact Factor/Cite ScoreTM” less than 0.499 – 4 Marks, IF between 0.5 & 0.749 – 6 Marks, IF above 0.75 – 8 Marks, UGS listed Journals -2 Marks / each Journal)']
# 		heading = ['S.No.','Full Journal paper(In IEEE reference format)','ISSN/ ISBNNo.','SCI/SCI- E/SSCI/ ESCI/ SCOPUS/UGC','Impact factor/ CiteScoreTM (if any)','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A3":
# 		main_heading = ['B. Books published as author or as editor or Articles/Chapters or Monographs published in Books(International publisher – 20 Marks/book & 5 Marks/chapter or Monographs in edited book, National – 10 Marks/book & 2 Marks/chapter or Monographs, local publisher-5 Marks) [60% for I Author & 40% will be divided among the co-authors].']
# 		heading = ['S.No.','Books Published/ Articles/Chapters published in Books as single author (In IEEE reference format)','ISSN/ ISBNNo.','International/National/Regional','Editor/Author','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')

# 	elif part == "A2":
# 		main_heading = ['Full Papers published in Conference Proceedings/ Papers presented in Conferences, Seminars, Workshops, Symposia (conference in association with IEEE/ Springer/  Elsevier/ ACM/ Wiley/ IPC or organized by reputed Institutions (IIT/IISc/NIT/IIIT/JNU/Central Universities) will be considered as International otherwise will be considered as National']
# 		heading = ['S.No.','Full Papers in Conference proceedings.(In IEEE reference format)','ISSN/ ISBNNo.','Details	of Conference International/ National/Regional','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A4":
# 		main_heading = ['C (i) Ongoing /Completed Research projects and consultancies (Projects>30 Lakhs – 20 Marks, between 5-30 Lakhs – 15 Marks, between 50,000 – 5 Lakhs – 10 Marks) – [60% for PI & 40% marks will be divided among the CO-PI].']
# 		heading = ['S.No.','Title','Agency','Period','Principal Investigator or Co-PI','Grant/ Amount in (Rs Lakhs)','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A5":
# 		main_heading = ['C (ii) Completed Research outcomes: Quality and Outcomes: (At National level output/Patent-                  25 Marks (if granted) & 20 Marks (if published) and at International level output/Patent-40 Marks (if granted) & 30 Marks (if published) – [60% Marks for main applicants and 40% marks will be divided among remaining Co Applicants].']
# 		heading = ['S.No.','Title','Agency','Period','Main Applicant Or Co- Applicant','Report Accepted/ Patent/ Technology transferred','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A6":
# 		main_heading = ['C (iii) Completed Research outcomes: Design/Industrial Design : (At National level Design / Industrial Design- 20 Marks(if granted) & 15 Marks (if published) and at International level Design/Industrial Design -    30 Marks(if granted) & 20 Marks(if published) – [60% Marks for main applicants and 40% marks will be divided among remaining Co Applicants].']
# 		heading = ['S.No.','Title','Agency','Period','Main Applicant Or Co- Applicant','Report Accepted/ Patent/ Technology transferred','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	elif part == "A7":
# 		main_heading = ['D. Research Guidance']
# 		heading = ['S.No.','Number Enrolled','Thesis Submitted','Degree awarded','Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	return {'main_heading':main_heading,'heading':heading}



# def get_cat2_form_data(emp_id,level,session,session_name):
# 	#SCORE CLAIMED#
# 	if int(level) > 1:
# 		level = 1

# 	final_data = {}
# 	extra_filter = {}
# 	final_data['main_heading'] = "CATEGORY – II (Maximum Marks: 50) (RESEARCH & ACADEMIC CONTRIBUTIONS)"
# 	statuses = []
# 	category = 'category2'
# 	for i in range(1, 8):
# 		data = {}
# 		data['data'] = []
# 		data['heading'] = []
# 		sub_category = str('A' + str(i))
# 		if str('A' + str(i)) not in final_data:
# 			final_data[str('A' + str(i))] = {}

# 		statuses = []
# 		status = []
# 		if int(level) <= 1:
# 			status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level)).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
# 			if len(status) == 0:
# 				statuses.append({'status': "PENDING"})
# 			else:
# 				for s in status:
# 					statuses.append({'status': s['approval_status']})
# 		if len(status) == 0:
# 			statuses.append({'status': "PENDING"})
# 		### SUBPARTS IN CAT3 ARE PARTWISE ###
# 		if i == 1:
# 			ach_type = 'RESEARCH PAPER IN JOURNAL'
# 		if i == 2:
# 			ach_type = 'RESEARCH PAPER IN CONFERENCE'
# 		if i == 3:
# 			ach_type = 'BOOKS'
# 		if i == 4:
# 			ach_type = 'PROJECTS/CONSULTANCY'
# 		if i == 5:
# 			ach_type ='PATENT'
# 		if i == 6:
# 			ach_type ='DESIGN'
# 		if i == 7:
# 			ach_type = 'RESEARCH GUIDANCE / PROJECT GUIDANCE'
# 		data['heading'] = get_heading_of_cat2('A' + str(i), level, statuses)
# 		qry = GetAllAchievementEmployee(emp_id,ach_type,session)
# 		print(qry,ach_type)
# 		if len(qry) > 0:
# 			if 'BOOKS' in ach_type:
# 				qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 				if len(qry1)>0:
# 					data['data'] = list(qry1)
# 				else:
# 					data1 = get_cat2_score_claimed(qry,str('A' + str(i)),emp_id)
# 					data['data'] = data1[0]
# 					data['score_claimed'] = round((data1[1]/len(data1[0])),2)
# 				final_data[str('A' + str(i))] = data
# 			elif 'PROJECTS/CONSULTANCY' in ach_type:
# 				qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 				if len(qry1)>0:
# 					data['data'] = qry1
# 				else:
# 					data1 = get_cat2_score_claimed(qry,str('A' + str(i)),emp_id)
# 					data['data'] = data1[0]
# 					data['score_claimed'] = round((data1[1]/len(data1[0])),2)
# 				final_data[str('A' + str(i))] = data

# 			elif 'PATENT' in ach_type:
# 				qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 				if len(qry1)>0:
# 					data['data'] = qry1
# 				else:
# 					data1 = get_cat2_score_claimed(qry,str('A' + str(i)),emp_id)
# 					data['data'] = data1[0]
# 					data['score_claimed'] = round((data1[1]/len(data1[0])),2)
# 				final_data[str('A' + str(i))] = data
# 			elif 'RESEARCH PAPER IN JOURNAL' in ach_type:
# 				sub_cat = ['SCI','SCI-E','SSCI','ESCI','SCOPOUS']
# 				qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 				if len(qry1)>0:
# 					data['data'] = qry1
# 				else:
# 					data1 = get_cat2_score_claimed(qry,str('A' + str(i)),emp_id)
# 					data['data'] = data1[0]
# 					data['score_claimed'] = round((data1[1]/len(data1[0])),2)
# 				final_data[str('A' + str(i))] = data
# 			elif 'RESEARCH PAPER IN CONFERENCE' in ach_type:
# 				qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 				if len(qry1)>0:
# 					data['data'] = qry1
# 				else:
# 					pass
# 			elif 'RESEARCH GUIDANCE / PROJECT GUIDANCE' in ach_type:
# 				qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 				if len(qry1)>0:
# 					data['data'] = qry1
# 				else:
# 					pass
# 			elif 'DESIGN' in ach_type:
# 				qry1 = FacAppCatWiseData.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session,category=category,sub_category=sub_category).exclude(status=0).values("data_sub_category","score_claimed","score_awarded","is_editable")
# 				if len(qry1)>0:
# 					data['data'] = qry1
# 				else:
# 					pass
# 		else:
# 			row_data = get_null_values_for_achievement(ach_type, level, statuses)
# 			data['data'].append(row_data)
# 			final_data['A' + str(i)] = data

# 	return final_data




# def get_cat2_score_claimed(qry,part,emp_id):
# 	data ={}
# 	score_claimed = 0
# 	if 'A1' in part:
# 		sub_cat = ['SCI','SCI-E','SSCI','ESCI','SCOPOUS']		
# 		for q in qry:
# 			if q['journal_details__sub_category__value'] in sub_cat:
# 				if 'SINGLE AUTHOR' in q['author__value']:
# 					if q['impact_factor']>=0.75:
# 						q['score_claimed'] = 23
# 						score_claimed = score_claimed + 23
# 					elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
# 						q['score_claimed'] = 21
# 						score_claimed = score_claimed + 21
# 					elif q['impact_factor']<0.5:
# 						q['score_claimed'] = 19
# 						score_claimed = score_claimed + 19
# 				elif 'FIRST AUTHOR' in q['author__value'] or 'SUPERVISOR' in q['author__value']:
# 					if q['impact_factor']>=0.75:
# 						q['score_claimed'] = 17
# 						score_claimed = score_claimed + 17
# 					elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
# 						q['score_claimed'] = 15
# 						score_claimed = score_claimed + 15
# 					elif q['impact_factor']<0.5:
# 						q['score_claimed'] = 13
# 						score_claimed = score_claimed + 13
# 				elif 'CO-AUTHOR' in q['author__value']:
# 					if q['impact_factor']>=0.75:
# 						q['score_claimed'] = 14
# 						score_claimed = score_claimed + 14
# 					elif q['impact_factor']>=0.5 and q['impact_factor']<0.75:
# 						q['score_claimed'] = 12
# 						score_claimed = score_claimed + 12
# 					elif q['impact_factor']<0.5:
# 						q['score_claimed'] = 10
# 						score_claimed = score_claimed + 10
# 			elif 'UGC RECOMMENDED' in q['journal_details__sub_category__value']:
# 				q['score_claimed'] = 2
# 				score_claimed = score_claimed + 2
# 	elif 'A3' in part:
# 		for q in qry:
# 			if 'INTERNATIONAL' in q['publisher_type__value']:
# 				if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
# 					score_claimed = score_claimed + 5
# 					q['score_claimed'] = 5
# 				elif 'BOOK' in q['role_for__value']:
# 					score_claimed = score_claimed + 20
# 					q['score_claimed'] = 20
# 			elif 'NATIONAL' in q['publisher_type__value']:
# 				if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
# 					score_claimed = score_claimed + 2
# 					q['score_claimed'] = 2
# 				elif 'BOOK' in q['role_for__value']:
# 					score_claimed = score_claimed + 10
# 					q['score_claimed'] = 10
# 			elif 'REGIONAL' in q['publisher_type__value']:
# 				if 'CHAPTER' in q['role_for__value'] or 'MONOGRAPH' in q['role_for__value'] or 'ARTICLE' in q['role_for__value']:
# 					score_claimed = score_claimed + 1
# 					q['score_claimed'] = 1
# 				elif 'BOOK' in q['role_for__value']:
# 					score_claimed = score_claimed + 5
# 					q['score_claimed'] = 5		
# 	elif 'A4' in part:
# 		for q in qry:
# 			if 'PROPOSED' not in q['project_status__value']:
# 				if q['principal_investigator'] is not None and q['co_principal_investigator'] is not None:
# 					if 'SELF' in q['principal_investigator'].upper() and 'SELF' in q['co_principal_investigator'].upper():
# 						if q['amount']>=3000000:
# 							score_claimed = score_claimed+20
# 							q['score_claimed'] = 20
# 						elif q['amount'] >= 500000 and q['amount']<3000000:
# 							score_claimed = score_claimed + 15
# 							q['score_claimed'] = 15
# 						elif q['amount'] >=50000 and q['amount']<500000:
# 							score_claimed = score_claimed+10
# 							q['score_claimed'] = 10
# 					elif 'SELF' in q['principal_investigator'].upper() and 'OTHER' in q['co_principal_investigator'].upper():
# 						if q['amount']>=3000000:
# 							score_claimed = score_claimed+12
# 							q['score_claimed'] = 12
# 						elif q['amount'] >= 500000 and q['amount']<3000000:
# 							score_claimed = score_claimed + 9
# 							q['score_claimed'] = 9
# 						elif q['amount'] >=50000 and q['amount']<500000:
# 							score_claimed = score_claimed+6
# 							q['score_claimed'] = 6
# 					elif 'OTHER' in q['principal_investigator'].upper() and 'SELF' in q['co_principal_investigator'].upper():
# 						if q['amount']>=3000000:
# 							score_claimed = score_claimed+8
# 							q['score_claimed'] = 8
# 						elif q['amount'] >= 500000 and q['amount']<3000000:
# 							score_claimed = score_claimed + 6
# 							q['score_claimed'] = 6
# 						elif q['amount'] >=50000 and q['amount']<500000:
# 							score_claimed = score_claimed+4
# 							q['score_claimed'] = 4
# 			else:
# 				q['score_claimed'] = 0
# 	elif 'A5' in part:
# 		for q in qry:
# 			if 'IF FILED' not in q['patent_details__patent_status__value']:
# 				if q['patent_details__patent_applicant_name'] is not None and q['patent_details__patent_co_applicant_name'] is not None:
# 					if 'SELF' in q['patent_details__patent_applicant_name'].upper() and 'SELF' in q['patent_details__patent_co_applicant_name'].upper():
# 						if 'INTERNATIONAL' in q['patent_details__level__value']:
# 							if 'IF GRANTED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 40
# 								score_claimed = score_claimed+40
# 							if 'PUBLISHED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 30
# 								score_claimed = score_claimed + 30
# 						elif  'NATIONAL' in q['patent_details__level__value']:
# 							if 'IF GRANTED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 25
# 								score_claimed = score_claimed+25
# 							if 'PUBLISHED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 20
# 								score_claimed = score_claimed + 20
# 					elif 'SELF' in q['patent_details__patent_applicant_name'].upper() and 'OTHER' in q['patent_details__patent_co_applicant_name'].upper():
# 						if 'INTERNATIONAL' in q['patent_details__level__value']:
# 							if 'IF GRANTED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 24
# 								score_claimed = score_claimed+24
# 							if 'PUBLISHED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 18
# 								score_claimed = score_claimed + 18
# 						elif  'NATIONAL' in q['patent_details__level__value']:
# 							if 'IF GRANTED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 15
# 								score_claimed = score_claimed+15
# 							if 'PUBLISHED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 12
# 								score_claimed = score_claimed + 12
# 					elif 'OTHER' in q['patent_details__patent_applicant_name'].upper() and 'SELF' in q['patent_details__patent_co_applicant_name'].upper():
# 						if 'INTERNATIONAL' in q['patent_details__level__value']:
# 							if 'IF GRANTED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 16
# 								score_claimed = score_claimed+16
# 							if 'PUBLISHED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 12
# 								score_claimed = score_claimed + 12
# 						elif  'NATIONAL' in q['patent_details__level__value']:
# 							if 'IF GRANTED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 10
# 								score_claimed = score_claimed+10
# 							if 'PUBLISHED' in q['patent_details__patent_status__value']:
# 								q['score_claimed'] = 8
# 								score_claimed = score_claimed + 8
# 			else:
# 				q['score_claimed'] = 0


# 	return [qry,score_claimed]

		


# # def get_cat2_form_data(emp_id, level, session, session_name):
# 	### SCORE CLAIMED IS INPUT FIELD ###

# # 	if int(level) > 1:
# # 		level = 1

# # 	final_data = {}
# # 	extra_filter = {}
# # 	statuses = []
# # # 	for i in range(1, 2):
# # 		data = {}
# # 		data['data'] = []
# # 		data['heading'] = []
# # 		if str('A' + str(i)) not in final_data:
# # 			final_data[str('A' + str(i))] = {}
# # 		#### GET STATUSES ####
# # 		statuses = []
# # 		status = []
# # 		if int(level) <= 1:
# # 			status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level)).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
# # 			if len(status) == 0:
# # 				statuses.append({'status': "PENDING"})
# # 			else:
# # 				for s in status:
# # 					statuses.append({'status': s['approval_status']})
# # 		if len(status) == 0:
# # 			statuses.append({'status': "PENDING"})
# # 		######################
# # 		row_data = {}
# # 		if statuses[0]['status'] != "PENDING":
# # 			extra_filter = {'status': statuses[0]['status']}
# # 		else:
# # 			extra_filter = {}
# # 		qry = FacAppCat2A1.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('fac_app_id', 'type_of_activity', 'average_hours', 'score_claimed', 'score_awarded').order_by('-fac_app_id')
# # 		data['heading'] = get_heading_of_cat2('A' + str(i), level, statuses)
# # 		data['total'] = 0
# # 		if len(qry) > 0:
# # 			for q in qry:
# # 				row_data = {}
# # 				if len(statuses) > 1:
# # 					if 'REVIEWED' in statuses[-1]['status']:
# # 						extra_filter = ({'status': 'REVIEWED'})
# # 					else:
# # 						extra_filter = ({'status': 'APPROVED'})
# # 					query = FacAppCat2A1.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session, type_of_activity=q['type_of_activity']).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('score_awarded', 'fac_app_id').order_by('-fac_app_id')
# # 					if len(query) > 0:
# # 						row_data['score_reviewed'] = query[0]['score_awarded']
# # 				row_data.update({'type_of_activity': q['type_of_activity'], 'average_hours': q['average_hours'], 'score_claimed': q['score_claimed']})
# # 				####### for level==1 ##########
# # 				if int(level) == 1:
# # 					if statuses[0]['status'] == "PENDING":
# # 						row_data['score_awarded'] = q['score_claimed']
# # 					else:
# # 						row_data['score_awarded'] = q['score_awarded']
# # 				###############################
# # 				data['data'].append(row_data)
# # 			data['total'] = get_total_of_cat2(qry, 'A' + str(i))

# # 		else:
# # 			row_data = {}
# # 			row_data = {'type_of_activity': None, 'average_hours': None, 'score_claimed': None}
# # 			###### for level==1 ###########
# # 			if int(level) == 1:
# # 				row_data['score_awarded'] = None
# # 			###############################
# # 			data['data'].append(row_data)
# # 		final_data['A' + str(i)] = data
# # 	return final_data


# def get_total_of_cat3(data):
# 	total = 0.0
# 	for d in data:
# 		if 'score_claimed' in d:
# 			try:
# 				d['score_claimed'] = float(d['score_claimed'])
# 			except:
# 				d['score_claimed'] = 0.0
# 			total = total + d['score_claimed']
# 	return total


# def get_null_values_for_achievement(ach_type, level, status):
# 	### ID == None ###
# 	ach_type = str(ach_type)
# 	row_data = {}
# 	if ach_type == "RESEARCH PAPER IN JOURNAL":
# 		row_data = {'paper_title': '---', 'journal_details__isbn': '---', 'published_date': '---', 'journal_details__type_of_journal__value': '---', 'journal_details__sub_category__value': '---', 'author__value': '---', 'impact_factor': '---', 'score_claimed': None, 'id': None}
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				row_data['score_awarded'] = None
# 			else:
# 				row_data['score_awarded'] = None
# 				row_data['score_reviewed'] = None

# 	elif ach_type == "RESEARCH PAPER IN CONFERENCE":
# 		row_data = {'paper_title': '---', 'conference_detail__conference_from': '---', 'isbn': '---', 'conference_detail__type_of_conference__value': '---', 'author__value': '---', 'score_claimed': None, 'id': None}
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				row_data['score_awarded'] = None
# 			else:
# 				row_data['score_awarded'] = None
# 				row_data['score_reviewed'] = None

# 	elif ach_type == "BOOKS":
# 		row_data = {'book_title': '---', 'published_date': '---', 'isbn': '---', 'publisher_type__value': '---', 'author__value': '---', 'publisher_details__publisher_name': '---', 'score_claimed': None, 'id': None}
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				row_data['score_awarded'] = None
# 			else:
# 				row_data['score_awarded'] = None
# 				row_data['score_reviewed'] = None

# 	elif ach_type == "PROJECTS/CONSULTANCY":
# 		row_data = {'start_date': '---', 'project_title': '---', 'project_type__value': '---', 'period': '---', 'principal_investigator': '---', 'amount': '---', 'score_claimed': None, 'id': None}
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				row_data['score_awarded'] = None
# 			else:
# 				row_data['score_awarded'] = None
# 				row_data['score_reviewed'] = None

# 	elif ach_type == "PATENT":
# 		row_data = {'patent_details__patent_title': '---', 'company_name': '---', 'patent_date': '---', 'patent_details__level__value': '---', 'patent_details__patent_status__value': '---',  'score_claimed': None, 'id': None}
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				row_data['score_awarded'] = None
# 			else:
# 				row_data['score_awarded'] = None
# 				row_data['score_reviewed'] = None

# 	elif ach_type == "RESEARCH GUIDANCE / PROJECT GUIDANCE":
# 		row_data = {'guidance_for__value': '---', 'deg_status': '---', 'date_of_guidance': '---', 'score_claimed': None, 'id': None}
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				row_data['score_awarded'] = None
# 			else:
# 				row_data['score_awarded'] = None
# 				row_data['score_reviewed'] = None

# 	elif ach_type == "TRAINING AND DEVELOPMENT PROGRAM":
# 		row_data = {'category__value': '---', 'from_date': '---', 'training_type__value': '---', 'durtion': '---', 'role__value': '---', 'organization_sector__value': '---', 'score_claimed': None, 'id': None}
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				row_data['score_awarded'] = None
# 			else:
# 				row_data['score_awarded'] = None
# 				row_data['score_reviewed'] = None

# 	elif ach_type == "LECTURES AND TALKS":
# 		row_data = {'category__value': '---', 'date': '---', 'topic': '---', 'role__value': '---', 'type_of_event__value': '---', 'score_claimed': None, 'id': None}
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				row_data['score_awarded'] = None
# 			else:
# 				row_data['score_awarded'] = None
# 				row_data['score_reviewed'] = None
# 	return row_data


# # def get_cat3_form_data(emp_id, level, session, session_name):
# # 	if int(level) > 1:
# # 		level = 1

# # 	final_data = {}
# # 	extra_filter = {}
# # 	statuses = []
# # 	######### PARTS IN CAT3 = 5 ##########
# # 	for i in range(1, 6):
# # 		data = {}
# # 		### SUBPARTS IN CAT3 ARE PARTWISE ###
# # 		if i == 1:
# # 			ach_type = ['RESEARCH PAPER IN JOURNAL', 'RESEARCH PAPER IN CONFERENCE']
# # 		if i == 2:
# # 			ach_type = ['BOOKS']
# # 		if i == 3:
# # 			ach_type = ['PROJECTS/CONSULTANCY', 'PATENT']
# # 		if i == 4:
# # 			ach_type = ['RESEARCH GUIDANCE / PROJECT GUIDANCE']
# # 		if i == 5:
# # 			ach_type = ['TRAINING AND DEVELOPMENT PROGRAM', 'LECTURES AND TALKS']
# # 		if str('A' + str(i)) not in final_data:
# # 			final_data[str('A' + str(i))] = {}
# # 		for j, a_type in enumerate(ach_type):
# # 			j = int_to_Roman(int(j) + 1)
# # 			data[j] = {}
# # 			data[j]['data'] = []
# # 			data[j]['total'] = 0
# # 			# for l in range(0, len(level)):
# # 			#### GET STATUSES ####
# # 			statuses = []
# # 			status = []
# # 			if int(level) <= 1:
# # 				status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level)).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
# # 				if len(status) == 0:
# # 					statuses.append({'status': "PENDING"})
# # 				else:
# # 					for s in status:
# # 						statuses.append({'status': s['approval_status']})
# # 			if len(status) == 0:
# # 				statuses.append({'status': "PENDING"})
# # 			######################
# # 			qry = GetAllAchievementEmployee(emp_id, a_type, session)
# # 			if len(qry) > 0:
# # 				for q in qry:
# # 					row_data = {}
# # 					if statuses[0]['status'] != "PENDING":
# # 						extra_filter = {'status': statuses[0]['status']}
# # 					else:
# # 						extra_filter = {}
# # 					query1 = FacAppCat3Achievement.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session, achievement_id=q['id'], type=a_type).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('fac_app_id', 'score_awarded', 'score_claimed').order_by('-fac_app_id')
# # 					if len(statuses) > 1:
# # 						if 'REVIEWED' in statuses[-1]['status']:
# # 							extra_filter = ({'status': 'REVIEWED'})
# # 						else:
# # 							extra_filter = ({'status': 'APPROVED'})

# # 						query2 = FacAppCat3Achievement.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session, achievement_id=q['id'], type=a_type).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('score_awarded', 'fac_app_id').order_by('-fac_app_id')
# # 						if len(query2) > 0:
# # 							q['score_reviewed'] = query2[0]['score_awarded']
# # 					####### for level==1 ##########
# # 					if int(level) == 1:
# # 						if len(query1) > 0:
# # 							if statuses[0]['status'] == "PENDING":
# # 								q['score_awarded'] = query1[0]['score_claimed']
# # 							else:
# # 								q['score_awarded'] = query1[0]['score_awarded']
# # 						else:
# # 							q['score_awarded'] = 0
# # 					###############################

# # 					if a_type == "RESEARCH PAPER IN JOURNAL":
# # 						if q['impact_factor'] == None:
# # 							q['impact_factor'] = 0

# # 					elif a_type == "RESEARCH GUIDANCE / PROJECT GUIDANCE":
# # 						if q['guidance_for__value'] == None:
# # 							q['deg_status'] = 'NOT AWARDED'
# # 						elif 'PROJECT' in q['guidance_for__value']:
# # 							q['deg_status'] = 'NOT AWARDED'
# # 						elif 'DEGREE' in q['guidance_for__value']:
# # 							if 'Yes' in q['guidance_awarded_status']:
# # 								q['deg_status'] = 'AWARDED'
# # 							else:
# # 								q['deg_status'] = 'NOT AWARDED'
# # 						elif 'RESEARCH' in q['guidance_for__value']:
# # 							if q['guidance_status__value'] == None:
# # 								q['deg_status'] = 'NOT AWARDED'
# # 							else:
# # 								q['deg_status'] = str(q['guidance_status__value'])
# # 						else:
# # 							q['deg_status'] = '---'

# # 					elif a_type == "TRAINING AND DEVELOPMENT PROGRAM":
# # 						q['durtion'] = str(str(q['from_date']) + ' To ' + str(q['to_date']))
# # 					elif a_type == "PROJECTS/CONSULTANCY":
# # 						q['amount'] = 0
# # 						q['period'] = str(str(q['start_date']) + ' To ' + str(q['end_date']))
# # 						if q['sponsored'] == "yes" or q['sponsored'] == 'Yes' or q['sponsored'] == 'YES':
# # 							for sponser in q['sponsers']:
# # 								try:
# # 									amount = float(sponser['amount'])
# # 								except:
# # 									amount = 0
# # 								q['amount'] = q['amount'] + amount
# # 						if q['association'] == "yes" or q['association'] == 'Yes' or q['association'] == 'YES':
# # 							for asso in q['associators']:
# # 								try:
# # 									amount = float(asso['amount'])
# # 								except:
# # 									amount = 0
# # 								q['amount'] = q['amount'] + amount
# # 				data1 = score_calculation_of_cat3('A' + str(i), str(j), qry, level, statuses)
# # 				for d in data1:
# # 					data[j]['data'].append(d)
# # 				data[j]['total'] = get_total_of_cat3(data1)
# # 			else:
# # 				row_data = get_null_values_for_achievement(a_type, level, statuses)
# # 				data[j]['data'].append(row_data)
# # 			final_data['A' + str(i)] = data

# # 	return final_data





# def get_heading_of_cat4(part, level, status):
# 	part = str(part)
# 	heading = []
# 	if part == "A1":
# 		heading = ['Branch/Semester/Section', 'Subject', 'Result (Clear Pass %)', 'Result (Ext. Theory Exam Average)', 'Below 40%', '40% to 49%', '50% to 59%', '60% and Above']
# 	if part == "A2":
# 		heading = ['Branch', 'Semeter', 'Section', 'Subject', 'Student Feedback']
# 	return heading


# def get_heading2_of_cat4(part, level, status):
# 	part = str(part)
# 	heading = []
# 	if part == "A1":
# 		heading = ['Subject', 'Best Institute', 'Best Institute External Exam Average', 'Second Best Institute', 'Second Best External Exam Average', 'Score Claimed']
# 		if int(level) >= 1:
# 			if len(status) == 1:
# 				heading.append('Score Awarded')
# 			else:
# 				heading.append('Score Awarded')
# 				heading.append('score Reviewed')
# 	return heading


# def get_cat4_form_data(emp_id, level, session, session_name):
# 	if int(level) > 1:
# 		level = 1

# 	final_data = {}
# 	extra_filter = {}
# 	statuses = []
# 	######### PARTS IN CAT3 = 5 ##########
# 	for i in range(1, 6):
# 		data = {}
# 		data['data'] = []
# 		data['heading'] = []
# 		if str('A' + str(i)) not in final_data:
# 			final_data[str('A' + str(i))] = {}
# 		# for l in range(0, int(level) + 1):
# 		#### GET STATUSES ####
# 		statuses = []
# 		status = []
# 		if int(level) <= 1:
# 			status = list(FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level)).exclude(status="DELETE").values('approval_status').order_by('approval_status'))
# 			if len(status) == 0:
# 				statuses.append({'status': "PENDING"})
# 			else:
# 				for s in status:
# 					statuses.append({'status': s['approval_status']})
# 		if len(status) == 0:
# 			statuses.append({'status': "PENDING"})
# 		######################
# 		row_data = {}
# 		if statuses[0]['status'] != "PENDING":
# 			extra_filter = {'status': statuses[0]['status']}
# 		else:
# 			extra_filter = {}
# 		if i == 1 or i == 2:  # FOR A1&A2 ####
# 			lectures_data = get_employee_subject_setion_wise_total_lecture(emp_id, session, session_name)
# 			lectures = lectures_data[0]
# 			subject_type = lectures_data[1]
# 		if i == 1:
# 			data['heading'] = get_heading_of_cat4('A' + str(i), level, statuses)
# 			data['heading2'] = get_heading2_of_cat4('A' + str(i), level, statuses)
# 			data['data2'] = []
# 			qry = FacAppCat4A1.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('branch_details', 'subject', 'result_clear_pass', 'result_external', 'stu_below_40', 'stu_40_49', 'stu_50_59', 'stu_above_60', 'score_claimed', 'score_awarded', 'fac_app_id').order_by('-fac_app_id')
# 			if len(qry) > 0:
# 				row_data2 = {}
# 				for q in qry:
# 					row_data = {}
# 					if 'INST(1)' not in str(q['branch_details']) and 'INST(2)' not in str(q['branch_details']):
# 						row_data = {'branch': q['branch_details'], 'subject': q['subject'], 'pass_per': q['result_clear_pass'], 'average_external': q['result_external'], 'below_40': q['stu_below_40'], 'in_40_49': q['stu_40_49'], 'in_50_59': q['stu_50_59'], 'above_60': q['stu_above_60'], 'score_claimed': q['score_claimed']}
# 						####### for level==1 ##########
# 						if int(level) >= 1:
# 							if statuses[0]['status'] == "PENDING":
# 								row_data['score_awarded'] = q['score_claimed']
# 							else:
# 								row_data['score_awarded'] = q['score_awarded']
# 						###############################
# 						data['data'].append(row_data)
# 						row_data2.update({q['subject']: {'score_claimed': q['score_claimed']}})
# 						#### FOR LEVEL=1 ####
# 						if int(level) >= 1:
# 							row_data2[q['subject']]['score_awarded'] = q['score_awarded']
# 						#####################
# 					else:
# 						if 'INST(1)' in q['branch_details']:
# 							if q['subject'] in row_data2:
# 								row_data2[q['subject']]['institute1'] = q['branch_details'].split('-')[0]
# 								row_data2[q['subject']]['ext_exam_average1'] = q['result_external']
# 								row_data2[q['subject']]['score_claimed'] = q['score_claimed']
# 								#### FOR LEVEL=1 ####
# 								if int(level) >= 1:
# 									row_data2[q['subject']]['score_awarded'] = q['score_awarded']
# 								#####################
# 								#### FOR REVIEW ####
# 								if len(statuses) > 1:
# 									if 'REVIEWED' in statuses[-1]['status']:
# 										extra_filter = ({'status': 'REVIEWED'})
# 									else:
# 										extra_filter = ({'status': 'APPROVED'})
# 									query = FacAppCat4A1.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session, subject=q['subject'], result_clear_pass__isnull=True).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('score_awarded', 'fac_app_id').order_by('-fac_app_id')
# 									if len(query) > 0:
# 										row_data2[q['subject']]['score_reviewed'] = query[0]['score_awarded']
# 								####################
# 						elif 'INST(2)' in q['branch_details']:
# 							if q['subject'] in row_data2:
# 								row_data2[q['subject']]['institute2'] = q['branch_details'].split('-')[0]
# 								row_data2[q['subject']]['ext_exam_average2'] = q['result_external']
# 				for k, v in row_data2.items():
# 					if 'institute1' in v:
# 						institute1 = v['institute1']
# 					else:
# 						institute1 = None
# 					if 'institute2' in v:
# 						institute2 = v['institute2']
# 					else:
# 						institute2 = None
# 					if 'ext_exam_average1' in v:
# 						ext_exam_average1 = v['ext_exam_average1']
# 					else:
# 						ext_exam_average1 = None
# 					if 'ext_exam_average2' in v:
# 						ext_exam_average2 = v['ext_exam_average2']
# 					else:
# 						ext_exam_average2 = None
# 					if 'score_reviewed' in v:
# 						score_reviewed = v['score_reviewed']
# 					else:
# 						score_reviewed = None

# 					# data['data2'].append({'subject': k, 'institute1': institute1, 'ext_exam_average1': ext_exam_average1, 'institute2': institute2, 'ext_exam_average2': ext_exam_average2, 'score_claimed': v['score_claimed']})
# 					if int(level) < 1:
# 						data['data2'].append({'subject': k, 'institute1': institute1, 'ext_exam_average1': ext_exam_average1, 'institute2': institute2, 'ext_exam_average2': ext_exam_average2, 'score_claimed': v['score_claimed']})
# 					else:
# 						if len(statuses) == 1:
# 							data['data2'].append({'subject': k, 'institute1': institute1, 'ext_exam_average1': ext_exam_average1, 'institute2': institute2, 'ext_exam_average2': ext_exam_average2, 'score_claimed': v['score_claimed'], 'score_awarded': v['score_awarded']})
# 						else:
# 							data['data2'].append({'subject': k, 'institute1': institute1, 'ext_exam_average1': ext_exam_average1, 'institute2': institute2, 'ext_exam_average2': ext_exam_average2, 'score_claimed': v['score_claimed'], 'score_awarded': v['score_awarded'], 'score_reviewed': score_reviewed})

# 			else:
# 				for lec in lectures:
# 					row_data = {}
# 					row_data2 = {}
# 					subject_id = set()
# 					semester = int_to_Roman(int(lec['section__sem_id__sem']))
# 					format_data = [lec['section__sem_id__dept__dept__value'], semester, lec['section__section']]
# 					lec['data-format'] = get_data_in_faculty_form_format(format_data)
# 					university_marks = get_university_marks_subject_wise(lec)
# 					if int(university_marks['per_passed_students']) != 0:
# 						subject_id.add(lec['subject_id'])
# 						row_data = {'branch': lec['data-format'], 'subject': lec['subject_id__sub_name'], 'pass_per': university_marks['per_passed_students'], 'average_external': university_marks['average_external'], 'below_40': university_marks['below_40'], 'in_40_49': university_marks['in_40_49'], 'in_50_59': university_marks['in_50_59'], 'above_60': university_marks['above_60'], 'score_claimed': None}
# 						###### for level==1 ###########
# 						if int(level) >= 1:
# 							row_data['score_awarded'] = None
# 						###############################
# 						data['data'].append(row_data)
# 						row_data2 = {'subject': lec['subject_id__sub_name'], 'institute1': None, 'ext_exam_average1': None, 'institute2': None, 'ext_exam_average2': None, 'score_claimed': None}
# 						##### FOR LEVEL==1 #####
# 						if int(level) >= 1:
# 							row_data2['score_awarded'] = None
# 						########################
# 						data['data2'].append(row_data2)
# 			total = get_total_of_cat4(data['data'], 'A' + str(i), level, statuses)
# 			for k, v in total.items():
# 				data[k] = round(v, 2)
# 			final_data['A' + str(i)] = data

# 		if i == 2:
# 			data['heading'] = get_heading_of_cat4('A' + str(i), level, statuses)
# 			qry = FacAppCat4A2.objects.filter(fac_app_id__emp_id=emp_id, fac_app_id__session=session).filter(**extra_filter).exclude(status="DELETE").exclude(fac_app_id__status="DELETE").values('branch', 'semester', 'section', 'subject', 'overall_avg', 'student_feedback', 'score_claimed', 'fac_app_id').order_by('-fac_app_id')
# 			Sessions = []
# 			Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
# 			Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
# 			for ses in Sessions:
# 				temp_data = []
# 				feedback = faculty_feedback_details([emp_id], ses, subject_type)
# 				if len(feedback) > 0:
# 					for f_back in feedback:
# 						row_data = {'branch': f_back['branch'], 'semester': f_back['sem'], 'section': f_back['section'], 'subject': f_back['subject'], 'overall_avg': f_back['TOTAL'], 'student_feedback': f_back['TOTAL'], 'score_claimed': None}
# 						data['data'].append(row_data)
# 						temp_data.append(row_data)
# 					data['f' + str(ses[-1])] = get_total_of_cat4(temp_data, 'A' + str(i), level, statuses)['overall_feedback']
# 			if 'fo' not in data and 'fe' in data:
# 				data['final_feedback'] = round(data['fe'], 2)

# 			elif 'fe' not in data and 'fo' in data:
# 				data['final_feedback'] = round(data['fo'], 2)
# 			elif 'fe' not in data and 'fe' not in data:
# 				data['final_feedback'] = round(0, 2)
# 			else:
# 				data['final_feedback'] = round(((data['fo'] + data['fe']) / 2), 2)

# 			data['final_total'] = 0

# 			if data['final_feedback'] != None and data['final_feedback'] > 0:
# 				if data['final_feedback'] >= 8.4:
# 					data['final_total'] = 20
# 				elif data['final_feedback'] >= 6.5 and data['final_feedback'] < 8.4:
# 					difference = data['final_feedback'] - 6.4
# 					data['final_total'] = round(difference / 0.1, 2)
# 			#### FOR LEVEL=1 ####
# 			if int(level) >= 1:
# 				data['score_awarded'] = data['final_total']

# 			#####################
# 			total = get_total_of_cat4(data['data'], 'A' + str(i), level, statuses)

# 			for k, v in total.items():
# 				data[k] = round(v, 2)
# 			final_data['A' + str(i)] = data
# 		if i == 3 or i == 4 or i == 5:
# 			qry = FacultyAppraisal.objects.filter(emp_id=emp_id).exclude(status="DELETE").exclude(status="PENDING").values('achievement_recognition', 'training_needs', 'suggestions').order_by('-id')
# 			if len(qry) > 0:
# 				row_data = {}
# 				if i == 3:
# 					row_data = {'achievement': qry[0]['achievement_recognition']}
# 				if i == 4:
# 					row_data = {'training_needs': qry[0]['training_needs']}
# 				if i == 5:
# 					row_data = {'suggestions': qry[0]['suggestions']}
# 			else:
# 				row_data = {}
# 				if i == 3:
# 					row_data = {'achievement': None}
# 				if i == 4:
# 					row_data = {'training_needs': None}
# 				if i == 5:
# 					row_data = {'suggestions': None}
# 			data['data'].append(row_data)
# 			final_data['A' + str(i)] = data
# 	return final_data


# def get_next_level_status(emp_id, level, session):
# 	status = "PENDING"
# 	qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level) + 1, session=session).exclude(status="DELETE").values('id', 'approval_status').order_by('-id')
# 	if len(qry) > 0:
# 		status = qry[0]['approval_status']
# 	return status


# def get_submission_status_of_emp(emp_id, session):
# 	qry = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, level=0, form_filled_status='Y', status="SUBMITTED").exclude(status="DELETE").values('form_filled_status', 'id').order_by('-id')
# 	emp_status = "NOT FILLED"
# 	if len(qry) > 0:
# 		if qry[0]['form_filled_status'] == 'Y':
# 			emp_status = "FILLED"
# 		else:
# 			emp_status = "NOT FILLED"
# 	return emp_status


# def int_to_Roman(num):
# 	val = [
# 		1000, 900, 500, 400,
# 		100, 90, 50, 40,
# 		10, 9, 5, 4,
# 		1
# 	]
# 	syb = [
# 		"M", "CM", "D", "CD",
# 		"C", "XC", "L", "XL",
# 		"X", "IX", "V", "IV",
# 		"I"
# 	]
# 	roman_num = ''
# 	i = 0
# 	while num > 0:
# 		for _ in range(num // val[i]):
# 			roman_num += syb[i]
# 			num -= val[i]
# 		i += 1
# 	return roman_num


# def get_subject_wise_total_pass_stu_percentage(univ_marks):
# 	total_students = len(univ_marks)
# 	passed_students = 0
# 	per_passed_students = 0
# 	for univ in univ_marks:
# 		if check_is_pass_or_fail(univ)[0] == True:
# 			passed_students = passed_students + 1
# 		if total_students > 0:
# 			per_passed_students = (passed_students / total_students) * 100
# 	return round(per_passed_students, 2)

# def get_subject_wise_total_pass_students(univ_marks):
# 	total_students = len(univ_marks)
# 	passed_students = 0
# 	per_passed_students = 0
# 	for univ in univ_marks:
# 		if check_is_pass_or_fail(univ)[0] == True:
# 			passed_students = passed_students + 1
# 		if total_students > 0:
# 			per_passed_students = (passed_students / total_students) * 100
# 	failed_students = total_students - passed_students
# 	return [total_students,passed_students,failed_students]

# def get_external_exam_average(univ_marks):
# 	total_students = len(univ_marks)
# 	total_external = 0.0
# 	average = 0
# 	for univ in univ_marks:
# 		try:
# 			univ['external_marks'] = float(univ['external_marks'])
# 		except:
# 			univ['external_marks'] = 0

# 		try:
# 			univ['back_marks'] = float(univ['back_marks'])
# 		except:
# 			univ['back_marks'] = 0
# 		if univ['back_marks'] == None or univ['back_marks'] == 0:
# 			total_external = total_external + univ['external_marks']
# 		else:

# 			total_external = total_external + univ['back_marks']
# 	if total_students > 0:
# 		average = total_external / total_students
# 	return round(average, 2)


# def get_external_exam_average_per(univ_marks):
# 	total_students = len(univ_marks)
# 	total_external = 0.0
# 	average_per = 0
# 	external_total_total = 0
# 	if len(univ_marks) > 0:
# 		external_total_total = univ_marks[0]['subject_id__max_university_marks']
# 	average = 0
# 	for univ in univ_marks:
# 		try:
# 			univ['external_marks'] = float(univ['external_marks'])
# 		except:
# 			univ['external_marks'] = 0

# 		try:
# 			univ['back_marks'] = float(univ['back_marks'])
# 		except:
# 			univ['back_marks'] = 0
# 		if univ['back_marks'] == None or univ['back_marks'] == 0:
# 			total_external = total_external + univ['external_marks']
# 		else:

# 			total_external = total_external + univ['back_marks']
# 	if total_students > 0:
# 		average = total_external / total_students
# 	if external_total_total != None and external_total_total != 0:
# 		average_per = float(average / external_total_total) * 100
# 	return round(average_per, 2)


# def get_percentage_of_student(univ_marks):
# 	total_students = len(univ_marks)
# 	percentage = 0
# 	if check_is_pass_or_fail(univ_marks)[0] == True:
# 		max_marks = int(check_is_pass_or_fail(univ_marks)[1])
# 		marks_obt = int(check_is_pass_or_fail(univ_marks)[2])
# 		if int(max_marks) != 0:
# 			percentage = float((marks_obt / max_marks) * 100)
# 	return percentage


# def get_university_marks_subject_wise(lectures):
# 	# lectures = {'session_name':---,'section__sem_id':---,'section':---,'subject_id':---}
# 	data = {}
# 	if 'section__sem_id' in lectures and 'section' in lectures:
# 		extra_filter = {'uniq_id__sem': lectures['section__sem_id'], 'uniq_id__section': lectures['section']}
# 	elif 'sem' in lectures and 'section' in lectures:
# 		extra_filter = {'uniq_id__sem': lectures['sem'], 'uniq_id__section__in': lectures['section']}
# 	else:
# 		extra_filter = {}
# 	data['below_40'] = 0
# 	data['in_40_49'] = 0
# 	data['in_50_59'] = 0
# 	data['above_60'] = 0
# 	session = Semtiming.objects.filter(session_name=lectures['session_name']).values('uid')
# 	if len(session) > 0:
# 		StudentUniversityMarks = generate_session_table_name('StudentUniversityMarks_', lectures['session_name'])
# 		studentSession = generate_session_table_name('studentSession_', lectures['session_name'])
# 		print(extra_filter)
# 		univ_marks = list(StudentUniversityMarks.objects.filter(uniq_id__session=session[0]['uid'], subject_id=lectures['subject_id']).filter(**extra_filter).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).exclude(subject_id__status="DELETE").values('subject_id', 'subject_id__max_ct_marks', 'subject_id__max_ta_marks', 'subject_id__max_att_marks', 'subject_id__max_university_marks', 'external_marks', 'internal_marks', 'back_marks', 'uniq_id').order_by('uniq_id'))
# 		data['per_passed_students'] = get_subject_wise_total_pass_stu_percentage(univ_marks)
# 		students_data = get_subject_wise_total_pass_students(univ_marks)
# 		data['total_students'] = students_data[0]
# 		data['passed_students'] = students_data[1]
# 		data['failed_students'] = students_data[2]
# 		data['average_external'] = get_external_exam_average(univ_marks)
# 		data['average_external_per'] = get_external_exam_average_per(univ_marks)
# 		for student in univ_marks:
# 			percentage = get_percentage_of_student(student)
# 			percentage = float(percentage)
# 			if percentage < 40:
# 				data['below_40'] = data['below_40'] + 1
# 			elif percentage < 50.0 and percentage >= 40.0:
# 				data['in_40_49'] = data['in_40_49'] + 1
# 			elif percentage < 60.0 and percentage >= 50.0:
# 				data['in_50_59'] = data['in_50_59'] + 1
# 			else:
# 				data['above_60'] = data['above_60'] + 1
# 	else:
# 		data['per_passed_students'] = 0
# 		data['average_external'] = 0
# 		data['below_40'] = 0
# 		data['in_40_49'] = 0
# 		data['in_50_59'] = 0
# 		data['above_60'] = 0
# 	return data


# def score_calculation_of_cat1(part, data):
# 	### AT TIME OF SUBMISSION ###
# 	no_of_rows = len(data)
# 	if part == "A1":
# 		for d in data:
# 			if d['lec_per_academic'] != None and d['lec_per_taken'] != None:
# 				difference = d['lec_per_taken'] - d['lec_per_academic']
# 				percentage = (d['lec_per_taken'] / d['lec_per_academic']) * 100
# 				if percentage < 80:
# 					d['diff'] = difference
# 					d['%_as_per_doc'] = percentage
# 					d['score_claimed'] = 0
# 				elif percentage >= 100:
# 					d['score_claimed'] = 50
# 				else:
# 					d['score_claimed'] = (float(d['lec_per_taken'] / d['lec_per_academic']) * 100) * 0.5
# 			else:
# 				d['diff'] = 0
# 				d['%_as_per_doc'] = 0
# 				d['score_claimed'] = 0
# 	if part == "A2":
# 		for d in data:
# 			d['score_claimed'] = 0
# 			# changes by Dhruv
# 			if 'prescribed' not in d or 'additional_resource' not in d:
# 				continue
# 			if d['prescribed'] != None:
# 				d['score_claimed'] = 2
# 			if d['additional_resource'] != None:
# 				d['score_claimed'] = 3
# 			if d['prescribed'] != None and d['additional_resource'] != None:
# 				d['score_claimed'] = 5
# 			else:
# 				d['score_claimed'] = 0
# 	if part == "A3":
# 		for d in data:
# 			d['score_claimed'] = 0
# 			if 'short_descriptn' not in d:
# 				continue
# 			if d['short_descriptn'] != None:
# 				d['score_claimed'] = 5
# 	if part == "A4":
# 		for d in data:
# 			if d['executed'] != None:
# 				d['score_claimed'] = 0
# 				if 'Invigilation' in d['type_of_duty']:
# 					d['score_claimed'] = int(d['executed']) * 2
# 				if 'Question' in d['type_of_duty']:
# 					d['score_claimed'] = int(d['executed']) * 3
# 				if 'Evaluation' in d['type_of_duty']:
# 					d['score_claimed'] = int(d['executed']) * 5
# 			else:
# 				d['score_claimed'] = 0
# 	return data


# def get_impact_factor_score_of_journal(part, subpart, q, score_claimed):
# 	score_claimed = int(score_claimed)
# 	if part == "A1" and subpart == 'I' and q['impact_factor'] != None:
# 		if ('SCI' in q['journal_details__sub_category__value'] or 'SCOPOUS' in q['journal_details__sub_category__value'] or 'UGC RECOMMENDED' in q['journal_details__sub_category__value']) and q['impact_factor'] != None:
# 			try:
# 				q['impact_factor'] = float(q['impact_factor'])
# 			except:
# 				q['impact_factor'] = 0
# 			if (q['impact_factor']) > 1.0 and (q['impact_factor']) < 2.0:
# 				score_claimed = score_claimed + 10
# 			elif (q['impact_factor']) > 2.0 and (q['impact_factor']) < 5.0:
# 				score_claimed = score_claimed + 15
# 			elif (q['impact_factor']) > 5.0:
# 				score_claimed = score_claimed + 20
# 	return score_claimed


# def score_calculation_of_cat3(part, subpart, data, level, status):
# 	### FOR INICIAL DATA ###
# 	if part == "A1":
# 		if subpart == 'I':
# 			for q in data:
# 				q['score_claimed'] = 0
# 				if q['author__value'] != None:
# 					if 'SINGLE AUTHOR' in q['author__value']:
# 						q['score_claimed'] = 15
# 						q['score_claimed'] = get_impact_factor_score_of_journal(part, subpart, q, q['score_claimed'])
# 					elif 'FIRST AUTHOR' in q['author__value'] or 'SUPERVISOR' in q['author__value']:
# 						q['score_claimed'] = 9
# 						q['score_claimed'] = get_impact_factor_score_of_journal(part, subpart, q, q['score_claimed'])
# 					else:
# 						q['score_claimed'] = 9
# 						q['score_claimed'] = get_impact_factor_score_of_journal(part, subpart, q, q['score_claimed'])

# 		elif subpart == 'II':
# 			for q in data:
# 				q['score_claimed'] = 0
# 				if q['conference_detail__type_of_conference__value'] != None and q['author__value'] != None:
# 					if 'INTERNATIONAL' in q['conference_detail__type_of_conference__value']:
# 						if 'SINGLE AUTHOR' in q['author__value']:
# 							q['score_claimed'] = 10
# 						elif 'FIRST AUTHOR' or 'SUPERVISOR' in q['author__value']:
# 							q['score_claimed'] = 6
# 						else:
# 							q['score_claimed'] = 4
# 					elif 'NATIONAL' in q['conference_detail__type_of_conference__value']:
# 						if 'SINGLE AUTHOR' in q['author__value']:
# 							q['score_claimed'] = 7.5
# 						elif 'FIRST AUTHOR' or 'SUPERVISOR' in q['author__value']:
# 							q['score_claimed'] = 4.5
# 						else:
# 							q['score_claimed'] = 3

# 	elif part == "A2":
# 		if subpart == 'I':
# 			for q in data:
# 				q['score_claimed'] = 0
# 				if q['publisher_type__value'] != None and q['role_for__value'] != None:
# 					if 'INTERNATIONAL' in q['publisher_type__value']:
# 						if 'BOOK' in q['role_for__value']:
# 							q['score_claimed'] = 50
# 						elif 'ARTICLE' or 'CHAPTER' in q['role_for__value']:
# 							q['score_claimed'] = 10
# 					elif 'NATIONAL' in q['publisher_type__value']:
# 						if 'BOOK' in q['role_for__value']:
# 							q['score_claimed'] = 25
# 						elif 'ARTICLE' or 'CHAPTER' in q['role_for__value']:
# 							q['score_claimed'] = 5
# 					elif 'REGIONAL' in q['publisher_type__value']:
# 						if 'BOOK' in q['role_for__value']:
# 							q['score_claimed'] = 15
# 						elif 'ARTICLE' or 'CHAPTER' in q['role_for__value']:
# 							q['score_claimed'] = 3

# 	elif part == "A3":
# 		if subpart == 'I':

# 			for q in data:
# 				q['score_claimed'] = 0
# 				if q['principal_investigator'] != None and q['co_principal_investigator'] != None:
# 					if ('self' in q['principal_investigator'] or 'SELF' in q['principal_investigator']) and ('other' in q['co_principal_investigator'] or 'OTHER' in q['co_principal_investigator']):
# 						if q['amount'] != None:
# 							if q['amount'] >= 3000000:
# 								q['score_claimed'] = 12
# 							elif q['amount'] >= 500000 and q['amount'] < 3000000:
# 								q['score_claimed'] = 9
# 							elif q['amount'] >= 50000 and q['amount'] < 500000:
# 								q['score_claimed'] = 6
# 					elif ('other' in q['principal_investigator'] or 'OTHER' in q['principal_investigator']) and ('self' in q['co_principal_investigator'] or 'SELF' in q['co_principal_investigator']):
# 						if q['amount'] != None:
# 							if q['amount'] >= 3000000:
# 								q['score_claimed'] = 8
# 							elif q['amount'] >= 500000 and q['amount'] < 3000000:
# 								q['score_claimed'] = 6
# 							elif q['amount'] >= 50000 and q['amount'] < 500000:
# 								q['score_claimed'] = 4
# 					elif ('self' in q['principal_investigator'] or 'SELF' in q['principal_investigator']) and ('self' in q['co_principal_investigator'] or 'SELF' in q['co_principal_investigator']):
# 						if q['amount'] != None:
# 							if q['amount'] >= 3000000:
# 								q['score_claimed'] = 20
# 							elif q['amount'] >= 500000 and q['amount'] < 3000000:
# 								q['score_claimed'] = 15
# 							elif q['amount'] >= 50000 and q['amount'] < 500000:
# 								q['score_claimed'] = 10
# 		elif subpart == 'II':
# 			for q in data:
# 				q['score_claimed'] = 0
# 				if q['patent_details__patent_status__value'] != None and q['patent_details__level__value'] != None:
# 					if 'GRANTED' in q['patent_details__patent_status__value'] and 'INTERNATIONAL' in q['patent_details__level__value']:
# 						q['score_claimed'] = 40
# 					elif 'GRANTED' in q['patent_details__patent_status__value'] and 'NATIONAL' in q['patent_details__level__value']:
# 						q['score_claimed'] = 25
# 	elif part == "A4":
# 		if subpart == "I":
# 			for q in data:
# 				q['score_claimed'] = 0
# 				if q['guidance_for__value'] != None and (q['guidance_awarded_status'] != None or q['guidance_status__value'] != None):
# 					if q['guidance_status__value'] == None:
# 						if 'DEGREE' in q['guidance_for__value'] and (q['guidance_awarded_status'] == 'Yes' or q['guidance_awarded_status'] == 'YES' or ['guidance_awarded_status'] == 'yes'):
# 							q['score_claimed'] = 3
# 					else:
# 						if 'DEGREE' in q['guidance_for__value'] and ('AWARDED' in q['guidance_status__value']):
# 							q['score_claimed'] = 3
# 					if 'RESEARCH' in q['guidance_for__value'] and 'SUBMITTED' in q['guidance_status__value']:
# 						q['score_claimed'] = 7
# 					if q['guidance_status__value'] == None:
# 						if 'RESEARCH' in q['guidance_for__value'] and (q['guidance_awarded_status'] == 'Yes' or q['guidance_awarded_status'] == 'YES' or ['guidance_awarded_status'] == 'yes'):
# 							q['score_claimed'] = 10
# 					else:
# 						if 'RESEARCH' in q['guidance_for__value'] and ('AWARDED' in q['guidance_status__value']):
# 							q['score_claimed'] = 10
# 	elif part == "A5":
# 		if subpart == 'I':
# 			for q in data:
# 				q['score_claimed'] = 0
# 				if q['to_date'] != None and q['from_date'] != None:
# 					duration = q['to_date'] - q['from_date']
# 					# changed for date range
# 					if duration.days >= 9:
# 						q['score_claimed'] = 20
# 					elif duration.days >= 4 and duration.days < 13:
# 						q['score_claimed'] = 10
# 		elif subpart == "II":
# 			for q in data:
# 				q['score_claimed'] = 0
# 				if q['type_of_event__value'] != None:
# 					if 'INTERNATIONAL' in q['type_of_event__value']:
# 						q['score_claimed'] = 10
# 					elif 'NATIONAL' in q['type_of_event__value']:
# 						q['score_claimed'] = 5
# 	return data


# def score_calculation_of_cat4(part, data):
# 	if part == "A1":
# 		### AFTER SUBMISSION OF DATA ###
# 		data1 = {}
# 		average_other = 0

# 		for d in data:
# 			if d['subject'] in data1:
# 				try:
# 					d['result_external'] = float(d['result_external'])
# 				except:
# 					d['result_external'] = 0
# 				if 'INST(1)' in d['branch_details']:
# 					data1[d['subject']]['ext_total1'] = data1[d['subject']]['ext_total1'] + float(d['result_external'])
# 				elif 'INST(2)' in d['branch_details']:
# 					data1[d['subject']]['ext_total2'] = data1[d['subject']]['ext_total2'] + float(d['result_external'])
# 				else:
# 					data1[d['subject']]['kiet_total'] = data1[d['subject']]['kiet_total'] + float(d['result_external'])
# 			else:
# 				data1[d['subject']] = {}
# 				data1[d['subject']] = {'ext_total1': 0, 'ext_total2': 0, 'kiet_total': 0}

# 		for sub in data1:
# 			average_other = float((data1[sub]['ext_total1'] + data1[sub]['ext_total2']) / 2)
# 			try:
# 				if data1[sub]['kiet_total'] > average_other:
# 					data[sub]['score_claimed'] = 30
# 				elif data1[sub]['kiet_total'] < (average_other - 10):
# 					data1[sub]['score_claimed'] = 0
# 				else:
# 					difference = float(average_other) - float(data1[sub]['kiet_total'])
# 					data1[sub]['score_claimed'] = 30.0 - (difference * 2)
# 			except:
# 				data1[sub]['score_claimed'] = 0
# 				pass
# 		for d in data:
# 			d['score_claimed'] = 0
# 			if 'INST(1)' not in d['branch_details'] and 'INST(2)' not in d['branch_details']:
# 				if d['subject'] in data1:
# 					d['score_claimed'] = data1[d['subject']]['score_claimed']

# 	elif part == "A2":
# 		difference = 0
# 		for d in data:
# 			d['score_claimed'] = 0
# 			if float(d['student_feedback']) >= 8.4:
# 				d['score_claimed'] = 20
# 			elif float(d['student_feedback']) >= 6.5 and float(d['student_feedback']) < 8.4:
# 				difference = d['student_feedback'] - 6.4

# 				d['score_claimed'] = round(float(difference) / 0.1, 2)
# 	return data


# def delete_row_from_tables(last_id, session, level, approval_status):
# 	if last_id != None:
# 		FacAppCatWiseData.objects.filter(fac_app_id=last_id).exclude(status="DELETE").update(status="DELETE")
# 		# FacAppCat1A1.objects.filter(fac_app_id__in=last_id).filter(**extra_filter).exclude(status="DELETE").update(status="DELETE")
# 		# FacAppCat1A2.objects.filter(fac_app_id__in=last_id).filter(**extra_filter).exclude(status="DELETE").update(status="DELETE")
# 		# FacAppCat1A3.objects.filter(fac_app_id__in=last_id).filter(**extra_filter).exclude(status="DELETE").update(status="DELETE")
# 		# FacAppCat1A4.objects.filter(fac_app_id__in=last_id).filter(**extra_filter).exclude(status="DELETE").update(status="DELETE")
# 		# FacAppCat2A1.objects.filter(fac_app_id__in=last_id).filter(**extra_filter).exclude(status="DELETE").update(status="DELETE")
# 		# if int(level) > 0:
# 		#   FacAppCat3Achievement.objects.filter(fac_app_id__in=last_id).filter(**extra_filter).exclude(status="DELETE").update(status="DELETE")
# 		# #### FacAppCat3Achievement = ENTRY ONLY ONCE WHEN 1ST SAVED OR SUBMITTED ####
# 		# FacAppCat4A1.objects.filter(fac_app_id__in=last_id).filter(**extra_filter).exclude(status="DELETE").update(status="DELETE")
# 		# FacAppCat4A2.objects.filter(fac_app_id__in=last_id).filter(**extra_filter).exclude(status="DELETE").update(status="DELETE")
# 		return True
# 	else:
# 		return False


# def get_statuses_at_reporting_level_of_faculty(emp_id, session):
# 	data = []
# 	qry = AarReporting.objects.filter(emp_id=emp_id).values('reporting_to', 'reporting_to__value', 'department', 'reporting_no').order_by('reporting_no')
# 	if len(qry) > 0:
# 		for q in qry:
# 			get_reporting_id = EmployeePrimdetail.objects.filter(dept=q['department'], desg=q['reporting_to']).exclude(emp_status="SEPARATE").exclude(emp_id="00007").values('emp_id')
# 			if len(get_reporting_id) > 0:
# 				get_status = list(FacAppRecommendationApproval.objects.filter(added_by=get_reporting_id[0]['emp_id'], level=q['reporting_no'], session=session, emp_id=emp_id).exclude(status="DELETE").values('approval_status', 'id').order_by('-id'))
# 				if len(get_status) > 0:
# 					data.append({'status': get_status[0]['approval_status'], 'desgination': q['reporting_to__value']})
# 				else:
# 					data.append({'status': 'PENDING', 'desgination': q['reporting_to__value']})
# 	return data


# def get_faculty_under_reporting(emp_id, session):
# 	list_emp = []
# 	consolidate_data = {}
# 	qry = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status="SEPARATE").exclude(emp_id='00007').values('emp_category__value', 'cadre__value', 'ladder__value', 'desg', 'desg__value', 'dept', 'dept__value'))
# 	if len(qry) > 0:
# 		list_emp = list(AarReporting.objects.filter(reporting_to=qry[0]['desg'], department=qry[0]['dept']).exclude(emp_id__emp_category__value="TECHNICAL STAFF").exclude(emp_id__emp_category__value="STAFF").exclude(emp_id__emp_status="SEPARATE").exclude(emp_id='00007').values('emp_id', 'emp_id__name', 'emp_id__cadre__value', 'emp_id__ladder__value', 'emp_id__dept__value').order_by('emp_id__dept__value', 'emp_id__name'))
# 		for emp in list_emp:
# 			other_details = get_emp_part_data(emp['emp_id'], session, {})
# 			for k, v in other_details.items():
# 				emp[k] = v
# 			query = FacultyAppraisal.objects.filter(emp_id=emp['emp_id'], session=session).exclude(status="DELETE").exclude(status="PENDING").values()

# 			############ REPORTING DETAILS ##################################
# 			reporting = get_reporting_of_emp_of_corresponding_band(qry[0]['dept'], qry[0]['desg'], emp['emp_id'], {})
# 			emp['reporting_level'] = reporting

# 			emp['status'] = get_statuses_at_reporting_level_of_faculty(emp['emp_id'], session)
# 			status_len = len(emp['status'])
# 			# AWARDED MARKS EDITABLE CHECK .............
# 			if int(reporting) > 1:
# 				emp['is_awarded_editable'] = False
# 			else:
# 				if status_len >= int(reporting):
# 					if emp['status'][int(reporting) - 1]['status'] != 'REVIEW' and emp['status'][int(reporting) - 1]['status'] != "REVIEWED":
# 						if status_len > int(reporting):
# 							if emp['status'][int(reporting)]['status'] != 'APPROVED' and emp['status'][int(reporting)]['status'] != 'REVIEWED':
# 								emp['is_awarded_editable'] = True
# 							else:
# 								emp['is_awarded_editable'] = False
# 						else:
# 							emp['is_awarded_editable'] = True
# 					else:
# 						emp['is_awarded_editable'] = False
# 				else:
# 					emp['is_awarded_editable'] = False
# 			############################################
# 			# REVIEWED MARKS EDITABLE CHECK .............
# 			if int(reporting) >= 1 and status_len > int(reporting):
# 				if emp['status'][int(reporting)]['status'] == "APPROVED" or emp['status'][int(reporting)]['status'] == "REVIEWED":
# 					emp['is_reviewed_editable'] = False
# 				else:
# 					emp['is_reviewed_editable'] = True
# 			else:
# 				emp['is_reviewed_editable'] = False
# 			############################################
# 			# REVIEW CHECK .................
# 			emp['is_review'] = check_if_review_is_eligible(reporting)
# 			####################################

# 			is_eligible_check = check_eligibility_of_employee_faculty(emp['emp_id'], session)
# 			if is_eligible_check == "NOT ELIGIBLE":
# 				emp['emp_status'] = "NOT ELIGIBLE"
# 			else:
# 				emp['emp_status'] = get_submission_status_of_emp(emp['emp_id'],  session)
# 			emp['desgination'] = qry[0]['desg__value']
# 			if len(query) > 0:
# 				emp['reporting'] = []
# 				if reporting != None:
# 					for i in range(1, int(reporting + 1)):
# 						status = FacAppRecommendationApproval.objects.filter(emp_id=emp['emp_id'], level=i).exclude(status="DELETE").values('approval_status', 'added_by', 'added_by__name', 'id').order_by('-id')
# 						if len(status) > 0:
# 							emp['reporting'].append({'status': status[0]['approval_status'], 'added_by': status[0]['added_by'], 'added_by__name': status[0]['added_by__name']})
# 						else:
# 							emp['reporting'].append({'status': 'PENDING', 'added_by': None, 'added_by__name': None})
# 			else:
# 				emp['reporting'] = []
# 				if reporting != None:
# 					for i in range(1, int(reporting + 1)):
# 						emp['reporting'].append({'status': 'PENDING', 'added_by': None, 'added_by__name': None})

# 			if len(emp['reporting']) > 0:
# 				if emp['reporting'][-1]['status'] == "REVIEW" or emp['reporting'][-1]['status'] == "REVIEWED":
# 					emp['is_reviewed_marks'] = True
# 				elif int(reporting) > 1 and emp['reporting'][-2]['status'] == "REVIEWED":
# 					emp['is_reviewed_marks'] = True
# 				else:
# 					emp['is_reviewed_marks'] = False
# 			#################### END.......###########################################
# 		############# FOR CONSOLIDATE DATA ####################
# 		# flag = 0
# 		# not_filled = 0
# 		# filled = 0
# 		# max_reporting = get_maximum_reporting(list_emp)
# 		# if form_type != "S-BAND":
# 		#     consolidate_data['emp'] = {}
# 		#     consolidate_data['emp']['not_filled'] = 0
# 		#     consolidate_data['emp']['filled'] = 0
# 		#     consolidate_data['emp']['total'] = 0
# 		# for emp in list_emp:
# 		#     level_reporting = 0
# 		#     if form_type != "S-BAND":
# 		#         consolidate_data['emp']['total'] = consolidate_data['emp']['total'] + 1
# 		#         if emp['emp_status'] == "NOT FILLED":
# 		#             consolidate_data['emp']['not_filled'] = consolidate_data['emp']['not_filled'] + 1
# 		#     if emp['emp_status'] == "FILLED":
# 		#         flag = 1
# 		#         if form_type != "S-BAND":
# 		#             consolidate_data['emp']['filled'] = consolidate_data['emp']['filled'] + 1
# 		#         for level, status in enumerate(emp['status']):
# 		#             if status['desgination'] == qry[0]['desg__value'] and int(level) + 1 <= int(max_reporting) and level_reporting == 0:
# 		#                 level = int(max_reporting) - 1
# 		#             if level_reporting == 0:
# 		#                 if "level_" + str(int(level) + 1) in consolidate_data:
# 		#                     if status['status'] == "PENDING" or status['status'] == "REVIEW":
# 		#                         consolidate_data["level_" + str(int(level) + 1)]['not_filled'] = consolidate_data["level_" + str(int(level) + 1)]['not_filled'] + 1
# 		#                     if status['status'] == "APPROVED" or status['status'] == "REVIEWED":
# 		#                         consolidate_data["level_" + str(int(level) + 1)]['filled'] = consolidate_data["level_" + str(int(level) + 1)]['filled'] + 1
# 		#                     consolidate_data["level_" + str(int(level) + 1)]['total'] = consolidate_data["level_" + str(int(level) + 1)]['total'] + 1

# 		#                 else:
# 		#                     consolidate_data["level_" + str(int(level) + 1)] = {}
# 		#                     consolidate_data["level_" + str(int(level) + 1)].update({'not_filled': 0, 'filled': 0, 'total': 1})
# 		#                     if status['status'] == "PENDING" or status['status'] == "REVIEW":
# 		#                         consolidate_data["level_" + str(int(level) + 1)]['not_filled'] = 1
# 		#                     if status['status'] == "APPROVED" or status['status'] == "REVIEWED":
# 		#                         consolidate_data["level_" + str(int(level) + 1)]['filled'] = 1
# 		#             if status['desgination'] == qry[0]['desg__value'] and int(level) + 1 <= int(max_reporting) and level_reporting == 0:
# 		#                 level_reporting = 1
# 		# if flag == 0:
# 		#     for i in range(1, int(max_reporting) + 1):
# 		#         consolidate_data["level_" + str(i)] = {}
# 		#         consolidate_data["level_" + str(i)]['not_filled'] = 0
# 		#         consolidate_data["level_" + str(i)]['filled'] = 0
# 		#         consolidate_data["level_" + str(i)]['total'] = 0
# 		# ################### END #################################
# 	return list_emp, consolidate_data


# def score_sheet_data(emp_id, level):
# 	data = {}
# 	data['heading'] = ['S.No', 'Nature of Activity', 'Max Score allowed', 'Score Claimed', 'Score Awarded']
# 	score_claimed = get_total_of_each_category_part(emp_id, level)
# 	data['Category_I'] = [{'s_no': 'A.1', 'name': 'Alloted Lectures taken %', 'max_score': 50, 'score_claimed': score_claimed['cat1']['A1'], 'score_awarded': None}, {'s_no': 'A.2', 'name': 'Prep. and Imparting knowledge', 'max_score': 15, 'score_claimed': score_claimed['cat1']['A2'], 'score_awarded': None}, {'s_no': 'A.3', 'name': 'Innovative practices in teaching', 'max_score': 15, 'score_claimed': score_claimed['cat1']['A3'], 'score_awarded': None}, {'s_no': 'A.4', 'name': 'Examination duties', 'max_score': 20, 'score_claimed': score_claimed['cat1']['A4'], 'score_awarded': None}]

# 	data['Category_II'] = [{'s_no': 'A.1', 'name': 'Co-curricular, Extension, Professional development related activities', 'max_score': 50, 'score_claimed': score_claimed['cat2']['A1'], 'score_awarded': None}]

# 	data['Category_III'] = [{'s_no': 'A (i)', 'name': 'Publications in Journals', 'max_score': 50, 'score_claimed': 0, 'score_awarded': None}, {'s_no': 'A (iI)', 'name': 'Publications in Conference Proc', 'max_score': 50, 'score_claimed': 0, 'score_awarded': None}, {'s_no': 'B', 'name': 'Publications in Books', 'max_score': 50, 'score_claimed': 0, 'score_awarded': None}, {'s_no': 'C (i)', 'name': 'Research & Consultancy-Ongoing', 'max_score': 50, 'score_claimed': 0, 'score_awarded': None}, {'s_no': 'C (ii)', 'name': 'Research & Consultancy-Completed', 'max_score': 50, 'score_claimed': 0, 'score_awarded': None}, {'s_no': 'D', 'name': 'Research Guidance', 'max_score': 50, 'score_claimed': 0, 'score_awarded': None}, {'s_no': 'E (i)', 'name': 'Training courses, FDP -attended', 'max_score': 50, 'score_claimed': 0}, {'s_no': 'E (ii)', 'name': 'Invited Talks', 'max_score': 50, 'score_claimed': 0, 'score_awarded': 0}]

# 	data['Category_IV'] = [{'s_no': 'A.1', 'name': 'Academic Result', 'max_score': 30, 'score_claimed': 0,
# 							'score_awarded': None}, {'s_no': 'A.2', 'name': 'Course Opinion Survey', 'max_score': 20, 'score_claimed': 0,
# 													 'score_awarded': None}]
# 	return data


# def get_recomended_data_faculty(e_id, level,  session):
# 	data = {}
# 	data['data'] = []
# 	data['key'] = []
# 	data['heading'] = []
# 	heading = {1: ['Approved by 1st Reporting', 'Review request by 2nd Reporting', 'Reviewed by 1st Reporting'], 2: ['Approved by 2nd Reporting', 'Send a review request at 1st reporting', 'Approve the reviewed request by 1st Reporting'], 2: ['Approved by 3rd Reporting', 'Send a review request at 2nd Reporting', 'Approve the reviewed request by 2nd Reporting']}
# 	if level != 0:
# 		for l in range(1, int(level) + 1):
# 			i = 0
# 			qry = FacAppRecommendationApproval.objects.filter(emp_id=e_id, level=l).exclude(status="DELETE").exclude(approval_status="REVIEW").values('id', 'emp_id', 'increment_type', 'increment_amount', 'promoted_to', 'level', 'approval_status', 'added_by', 'added_by__name', 'added_by__desg__value', 'session', 'session__session', 'status', 'promoted_to__value').order_by('id')
# 			if len(qry) > 0:

# 				for q in qry:
# 					amount = 0.0
# 					if q['increment_amount']!=None:
# 						try:
# 							amount = float(q['increment_amount'])
# 						except:
# 							amount = 0.0
# 					q['editable'] = check_if_form_editable_or_not_faculty(e_id, l, session, level, None)
# 					q['table_data'] = get_increment_in_salary(q['increment_type'], e_id, q['session'], get_salary_type(e_id, q['session'], {})['salary_type__value'], amount)
# 					# print(q['table_data'], 'vrinda')
# 					data['data'].append(q)
# 					data['key'].append(q['approval_status'])
# 					data['heading'].append(str(q['approval_status']) + ' by ' + str(q['added_by__desg__value']))
# 					i = i + 1

# 		return data
# 	return data


# def get_remark_function_faculty(pre_level, level, emp_id, session):
# 	remark = {}
# 	remark['data'] = []
# 	remark['heading'] = []
# 	remark['is_editable'] = []
# 	for l in range(int(pre_level), int(level) + 1):
# 		qry = FacAppRecommendationApproval.objects.filter(level=l, emp_id=emp_id, session=session).exclude(status="DELETE").exclude(approval_status="REVIEW").values('remark', 'id', 'approval_status', 'added_by__desg__value').order_by('-id')
# 		if len(qry) > 0:
# 			remark['data'].append(qry[0]['remark'])
# 			remark['heading'].append(str(qry[0]['added_by__desg__value']))
# 			remark['is_editable'].append(check_if_form_editable_or_not_faculty(emp_id, l, session, level, qry[0]['approval_status']))
# 		else:
# 			get_reporting_desg = AarReporting.objects.filter(emp_id=emp_id, reporting_no=l).values('reporting_to', 'reporting_to__value')
# 			if len(get_reporting_desg) > 0:
# 				remark['heading'].append(str(get_reporting_desg[0]['reporting_to__value']))
# 			else:
# 				remark['heading'].append(None)
# 			remark['data'].append(None)
# 			remark['is_editable'].append(check_if_form_editable_or_not_faculty(emp_id, l,  session, level, 'PENDING'))
# 	return remark


# def get_remark_faculty(level, emp_id, session):
# 	remark = {}
# 	if int(level) != 0:
# 		pre_level = 1
# 		remark = get_remark_function_faculty(pre_level, level, emp_id, session)
# 	return remark


# def enter_awarded_marks_hod_first_time(category_data, last_id, is_hod_dean, level):
# 	if last_id != None:
# 		if 'cat1' in category_data:
# 			if 'A1' in category_data['cat1']:
# 				for catA1 in category_data['cat1']['A1']['data']:
# 					if catA1['course_paper'] != None and catA1['lec_per_academic'] != None:
# 						FacAppCat1A1.objects.filter(fac_app_id=last_id, course_paper=catA1['course_paper']).exclude(status="DELETE").update(score_awarded=catA1['score_awarded'], status="APPROVED")
# 			if 'A2' in category_data['cat1']:
# 				for catA2 in category_data['cat1']['A2']['data']:
# 					FacAppCat1A2.objects.filter(fac_app_id=last_id, course_paper=catA2['course_paper']).exclude(status="DELETE").update(score_awarded=catA2['score_awarded'], status="APPROVED")
# 			if 'A3' in category_data['cat1']:
# 				for catA3 in category_data['cat1']['A3']['data']:
# 					FacAppCat1A3.objects.filter(fac_app_id=last_id, short_descriptn=catA3['short_descriptn']).exclude(status="DELETE").update(score_awarded=catA3['score_awarded'], status="APPROVED")
# 			if is_hod_dean == False:
# 				if 'A4' in category_data['cat1']:
# 					for i, catA4 in enumerate(category_data['cat1']['A4']['data']):
# 						FacAppCat1A4.objects.filter(fac_app_id=last_id, sno=int(i)).exclude(status="DELETE").update(score_awarded=catA4['score_awarded'], status="APPROVED")

# 		if 'cat2' in category_data:
# 			if 'A1' in category_data['cat2']:
# 				for cat2A1 in category_data['cat2']['A1']['data']:
# 					FacAppCat2A1.objects.filter(fac_app_id=last_id, type_of_activity=cat2A1['type_of_activity']).exclude(status="DELETE").update(score_awarded=cat2A1['score_awarded'], status="APPROVED")

# 		if 'cat3' in category_data:
# 			achievement = check_for_achievement_data(category_data['cat3'], last_id, level)
# 			if achievement[0] == True:
# 				for ach in achievement[1]:
# 					FacAppCat3Achievement.objects.filter(fac_app_id=last_id, type=ach['type'], achievement_id=ach['id']).exclude(status="DELETE").update(score_awarded=ach['score_awarded'], status="APPROVED")

# 		if 'cat4' in category_data:
# 			if 'A1' in category_data['cat4']:
# 				for cat4A1 in category_data['cat4']['A1']['data']:
# 					FacAppCat4A1.objects.filter(fac_app_id=last_id, branch_details=cat4A1['branch'], subject=cat4A1['subject']).update(status="APPROVED")
# 				for cat4A1 in category_data['cat4']['A1']['data2']:
# 					FacAppCat4A1.objects.filter(fac_app_id=last_id, subject=cat4A1['subject']).update(score_claimed=cat4A1['score_claimed'], score_awarded=cat4A1['score_awarded'], status="APPROVED")
# 			if 'A2' in category_data['cat4']:
# 				for cat4A2 in category_data['cat4']['A2']['data']:
# 					FacAppCat4A2.objects.filter(fac_app_id=last_id, branch=cat4A2['branch'], semester=cat4A2['semester'], section=cat4A2['section'],  overall_avg=cat4A2['overall_avg'], student_feedback=cat4A2['student_feedback']).update(score_claimed=category_data['cat4']['A2']['final_total'], score_awarded=category_data['cat4']['A2']['final_total'], status="APPROVED")

# 				#  #### FacAppCat3Achievement = ENTRY ONLY ONCE WHEN 1ST SAVED OR SUBMITTED ####
# 				# FacAppCat4A1.objects.filter(fac_app_id__in=last_id).exclude(status="DELETE").update(score_awarded=d['score_awarded'])
# 				# FacAppCat4A2.objects.filter(fac_app_id__in=last_id).exclude(status="DELETE").update(score_awarded=d['score_awarded'])
# 		return True
# 	else:
# 		return False


# def create_another_rows_for_hod_marks(category_data, fac_app_id, is_hod_dean, level, approval_status):
# 	if fac_app_id != None:
# 		fac_app_id = FacultyAppraisal.objects.get(id=fac_app_id)
# 		if 'cat1' in category_data:
# 			if 'A1' in category_data['cat1']:
# 				for catA1 in category_data['cat1']['A1']['data']:
# 					if catA1['course_paper'] != None and catA1['lec_per_academic'] != None:
# 						if 'REVIEWED' in approval_status:
# 							score_awarded = catA1['score_reviewed']
# 						else:
# 							score_awarded = catA1['score_awarded']
# 						FacAppCat1A1.objects.create(fac_app_id=fac_app_id, course_paper=catA1['course_paper'], lectues_calendar=catA1['lec_per_academic'], lectues_portal=catA1['lec_per_taken'], score_claimed=catA1['score_claimed'], score_awarded=score_awarded, status=approval_status)
# 			if 'A2' in category_data['cat1']:
# 				for catA2 in category_data['cat1']['A2']['data']:
# 					if 'consulted' in catA2:
# 						consulted = catA2['consulted']
# 					else:
# 						consulted = None
# 					if 'prescribed' in catA2:
# 						prescribed = catA2['prescribed']
# 					else:
# 						prescribed = None
# 					if 'additional_resource' in catA2:
# 						additional_resource = catA2['additional_resource']
# 					else:
# 						additional_resource = None
# 					if 'REVIEWED' in approval_status:
# 						score_awarded = catA2['score_reviewed']
# 					else:
# 						score_awarded = catA2['score_awarded']
# 					FacAppCat1A2.objects.create(fac_app_id=fac_app_id, course_paper=catA2['course_paper'], consulted=consulted, prescribed=prescribed, additional_resource=additional_resource, score_claimed=catA2['score_claimed'], score_awarded=score_awarded, status=approval_status)
# 			if 'A3' in category_data['cat1']:
# 				for catA3 in category_data['cat1']['A3']['data']:
# 					if 'short_descriptn' in catA3:
# 						short_descriptn = catA3['short_descriptn']
# 					else:
# 						short_descriptn = None
# 					if short_descriptn != None:
# 						if 'REVIEWED' in approval_status:
# 							score_awarded = catA3['score_reviewed']
# 						else:
# 							score_awarded = catA3['score_awarded']
# 						FacAppCat1A3.objects.create(fac_app_id=fac_app_id, short_descriptn=short_descriptn, score_claimed=catA3['score_claimed'], score_awarded=score_awarded, status=approval_status)
# 			if is_hod_dean == False:
# 				if 'A4' in category_data['cat1']:
# 					for i, catA4 in enumerate(category_data['cat1']['A4']['data']):
# 						if 'REVIEWED' in approval_status:
# 							score_awarded = catA4['score_reviewed']
# 						else:
# 							score_awarded = catA4['score_awarded']
# 						# if catA4['duties_assign'] != None and catA4['executed'] != None and catA4['extent_to_carried'] != None:
# 						FacAppCat1A4.objects.create(fac_app_id=fac_app_id, sno=int(i), executed=catA4['executed'], extent_to_carried=catA4['extent_to_carried'], duties_assign=catA4['duties_assign'], score_claimed=catA4['score_claimed'], score_awarded=score_awarded, status=approval_status)

# 		if 'cat2' in category_data:
# 			if 'A1' in category_data['cat2']:
# 				for cat2A1 in category_data['cat2']['A1']['data']:
# 					if 'type_of_activity' in cat2A1:
# 						type_of_activity = cat2A1['type_of_activity']
# 					else:
# 						type_of_activity = None
# 					if 'average_hours' in cat2A1:
# 						average_hours = cat2A1['average_hours']
# 					else:
# 						average_hours = None
# 					if 'score_claimed' in cat2A1:
# 						score_claimed = cat2A1['score_claimed']
# 					else:
# 						score_claimed = None
# 					if 'REVIEWED' in approval_status:
# 						score_awarded = cat2A1['score_reviewed']
# 					else:
# 						score_awarded = cat2A1['score_awarded']
# 					# if cat2A1['type_of_activity'] != None and cat2A1['average_hours'] != None and cat2A1['score_claimed'] != None:
# 					FacAppCat2A1.objects.create(fac_app_id=fac_app_id, type_of_activity=type_of_activity, average_hours=average_hours, score_claimed=score_claimed, score_awarded=score_awarded, status=approval_status)

# 		if 'cat3' in category_data:
# 			is_entery_in_achievement = check_for_achievement_data(category_data['cat3'], fac_app_id, level)
# 			if is_entery_in_achievement[0] == True:
# 				for ach in is_entery_in_achievement[1]:
# 					FacAppCat3Achievement.objects.create(fac_app_id=fac_app_id, type=ach['type'], achievement_id=ach['id'], score_claimed=ach['score_claimed'], score_awarded=ach['score_awarded'], status=approval_status)

# 		if 'cat4' in category_data:
# 			if 'A1' in category_data['cat4']:
# 				for cat4A1 in category_data['cat4']['A1']['data']:
# 					FacAppCat4A1.objects.create(fac_app_id=fac_app_id, branch_details=cat4A1['branch'], subject=cat4A1['subject'], result_clear_pass=cat4A1['pass_per'], result_external=cat4A1['average_external'], stu_below_40=cat4A1['below_40'], stu_40_49=cat4A1['in_40_49'], stu_50_59=cat4A1['in_50_59'], stu_above_60=cat4A1['above_60'], score_claimed=cat4A1['score_claimed'], status=approval_status)
# 				for cat4A1 in category_data['cat4']['A1']['data2']:
# 					if cat4A1['institute1'] != None and cat4A1['institute2'] != None and cat4A1['ext_exam_average1'] != None and cat4A1['ext_exam_average2'] != None:
# 						if 'REVIEWED' in approval_status:
# 							score_awarded = cat4A1['score_reviewed']
# 						else:
# 							score_awarded = cat4A1['score_awarded']
# 						institute1 = str(cat4A1['institute1']) + '-INST(1)'
# 						FacAppCat4A1.objects.create(fac_app_id=fac_app_id, branch_details=institute1, subject=cat4A1['subject'], result_external=cat4A1['ext_exam_average1'], score_claimed=cat4A1['score_claimed'], score_awarded=score_awarded, status=approval_status)

# 						institute2 = str(cat4A1['institute2']) + '-INST(2)'
# 						FacAppCat4A1.objects.create(fac_app_id=fac_app_id, branch_details=institute2, subject=cat4A1['subject'], result_external=cat4A1['ext_exam_average2'], score_claimed=cat4A1['score_claimed'], score_awarded=score_awarded, status=approval_status)
# 			if 'A2' in category_data['cat4']:
# 				for cat4A2 in category_data['cat4']['A2']['data']:
# 					FacAppCat4A2.objects.create(fac_app_id=fac_app_id, branch=cat4A2['branch'], semester=cat4A2['semester'], section=cat4A2['section'], subject=cat4A2['branch'], overall_avg=cat4A2['overall_avg'], student_feedback=cat4A2['student_feedback'], score_claimed=category_data['cat4']['A2']['final_total'], score_awarded=category_data['cat4']['A2']['final_total'], status=approval_status)
# 		return True
# 	else:
# 		return False


# def get_total_of_each_category_part(emp_id, level):
# 	data = {}
# 	extra_filter = {}
# 	# if approval_status!=None and approval_status == "REVIEWED":
# 	#     extra_filter = {'status':approval_status}
# 	last_id = FacultyAppraisal.objects.filter(emp_id=emp_id, form_filled_status="Y", status="SUBMITTED").exclude(status="DELETE").values_list('id', flat=True).order_by('-id')
# 	data['cat1'] = {'A1': 0, 'A2': 0, 'A3': 0, 'A4': 0}
# 	data['cat2'] = {'A1': 0}
# 	if len(last_id) > 0:
# 		marks_claimed = 0
# 		marks = FacAppCat1A1.objects.filter(fac_app_id=last_id[0]).filter(**extra_filter).exclude(status="DELETE").values_list('score_claimed', flat=True)
# 		if len(marks) > 0:
# 			for m in marks:
# 				if m != None and m != 0:
# 					marks_claimed = marks_claimed + float(m)
# 		if float(marks_claimed) > 50:
# 			marks_claimed = 50
# 		data['cat1']['A1'] = marks_claimed

# 		marks_claimed = 0
# 		marks = FacAppCat1A2.objects.filter(fac_app_id=last_id[0]).filter(**extra_filter).exclude(status="DELETE").values_list('score_claimed', flat=True)
# 		if len(marks) > 0:
# 			for m in marks:
# 				if m != None and m != 0:
# 					marks_claimed = marks_claimed + float(m)
# 		if float(marks_claimed) > 15:
# 			marks_claimed = 15
# 		data['cat1']['A2'] = marks_claimed

# 		marks_claimed = 0
# 		marks = FacAppCat1A3.objects.filter(fac_app_id=last_id[0]).filter(**extra_filter).exclude(status="DELETE").values_list('score_claimed', flat=True)
# 		if len(marks) > 0:
# 			for m in marks:
# 				if m != None and m != 0:
# 					marks_claimed = marks_claimed + float(m)
# 		if float(marks_claimed) > 15:
# 			marks_claimed = 15
# 		data['cat1']['A3'] = marks_claimed

# 		marks_claimed = 0
# 		marks = FacAppCat1A4.objects.filter(fac_app_id=last_id[0]).filter(**extra_filter).exclude(status="DELETE").values('duties_assign', 'sno')
# 		if len(marks) > 0:
# 			for m in marks:
# 				if m['duties_assign'] != None and m['duties_assign'] != 0:
# 					if m['sno'] != None:
# 						if int(m['sno']) == 0:
# 							factor = 2
# 						if int(m['sno']) == 1:
# 							factor = 3
# 						if int(m['sno']) == 2:
# 							factor = 5
# 					marks_claimed = marks_claimed + float(m['duties_assign'] * factor)
# 		if float(marks_claimed) > 20:
# 			marks_claimed = 20
# 		data['cat1']['A4'] = marks_claimed

# 		marks_claimed = 0
# 		marks = FacAppCat2A1.objects.filter(fac_app_id=last_id[0]).filter(**extra_filter).exclude(status="DELETE").values_list('score_claimed', flat=True)
# 		if len(marks) > 0:
# 			for m in marks:
# 				if m != None and m != 0:
# 					marks_claimed = marks_claimed + float(m)
# 		if float(marks_claimed) > 50:
# 			marks_claimed = 50
# 		data['cat2']['A1'] = marks_claimed
# 	return data


# def get_approval_status_for_repoprting_level_faculty(level, emp_id, session):
# 	status = "APPROVED"
# 	qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level) + 1, session=session).exclude(status="DELETE").values('approval_status').order_by('-approval_status')
# 	if len(qry) > 0:
# 		if qry[0]['approval_status'] == "REVIEW":
# 			status = "REVIEWED"
# 	return status


# def get_current_status_reporting_level_of_employee(level, emp_id, added_by):
# 	status = "PENDING"
# 	qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, added_by=added_by).exclude(status="DELETE").values_list('approval_status', flat=True).order_by('-approval_status')
# 	if len(qry) > 0:
# 		status = qry[0]
# 	return status


# def get_detpwise_consolidate_data(dept, session):
# 	data = {}
# 	data = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0, 'not_eligible': 0}
# 	data['dept_data'] = []
# 	for d in dept:
# 		employee = list(EmployeePrimdetail.objects.filter(dept__value=d['dept__value'], emp_category__value="FACULTY").exclude(emp_id='00007').exclude(emp_status="SEPARATE").values('emp_id', 'dept', 'dept__value', 'desg', 'desg__value').distinct())
# 		dept_data = {'dept': 'None', 'dept_data': {}}
# 		if len(employee) == 0:
# 			if d['dept__value'] in dept_data['dept']:
# 				dept_data['dept_data'] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0, 'not_eligible': 0}
# 			else:
# 				dept_data['dept'] = d['dept__value']
# 				dept_data['dept_data'] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 0, 'not_eligible': 0}
# 		for emp in employee:
# 			is_eligible_check = check_eligibility_of_employee_faculty(emp['emp_id'], session)
# 			if is_eligible_check == "NOT ELIGIBLE":
# 				emp_status = "NOT ELIGIBLE"
# 			else:
# 				emp_status = get_submission_status_of_emp(emp['emp_id'],  session)

# 			level_status = get_statuses_at_reporting_level_of_faculty(emp['emp_id'], session)
# 			if 'NOT FILLED' in emp_status:
# 				if emp['dept__value'] in dept_data['dept']:
# 					dept_data['dept_data']['not_filled'] = dept_data['dept_data']['not_filled'] + 1
# 					dept_data['dept_data']['total_employee'] = dept_data['dept_data']['total_employee'] + 1

# 					data['not_filled'] = data['not_filled'] + 1
# 					data['total_employee'] = data['total_employee'] + 1
# 				else:
# 					dept_data['dept'] = emp['dept__value']
# 					dept_data['dept_data'] = {'not_filled': 1, 'filled': 0, 'total_approved': 0, 'total_employee': 1, 'not_eligible': 0}

# 					data['not_filled'] = data['not_filled'] + 1
# 					data['total_employee'] = data['total_employee'] + 1

# 			elif "FILLED" in emp_status:
# 				if emp['dept__value'] in dept_data['dept']:
# 					dept_data['dept_data']['filled'] = dept_data['dept_data']['filled'] + 1
# 					dept_data['dept_data']['total_employee'] = dept_data['dept_data']['total_employee'] + 1

# 					data['filled'] = data['filled'] + 1
# 					data['total_employee'] = data['total_employee'] + 1
# 					if len(level_status) > 0:
# 						if level_status[-1]['status'] == "APPROVED":
# 							dept_data['dept_data']['total_approved'] = dept_data['dept_data']['total_approved'] + 1

# 							data['total_approved'] = data['total_approved'] + 1
# 				else:
# 					dept_data['dept'] = emp['dept__value']
# 					dept_data['dept_data'] = {'not_filled': 0, 'filled': 1, 'total_approved': 0, 'total_employee': 1, 'not_eligible': 0}

# 					data['filled'] = data['filled'] + 1
# 					data['total_employee'] = data['total_employee'] + 1
# 					if len(level_status) > 0:
# 						if level_status[-1]['status'] == "APPROVED":
# 							dept_data['dept_data']['total_approved'] = dept_data['dept_data']['total_approved'] + 1

# 							data['total_approved'] = data['total_approved'] + 1

# 			elif 'NOT ELIGIBLE' in emp_status:
# 				if emp['dept__value'] in dept_data['dept']:
# 					dept_data['dept_data']['not_eligible'] = dept_data['dept_data']['not_eligible'] + 1
# 					dept_data['dept_data']['total_employee'] = dept_data['dept_data']['total_employee'] + 1

# 					data['not_eligible'] = data['not_eligible'] + 1
# 					data['total_employee'] = data['total_employee'] + 1
# 				else:
# 					dept_data['dept'] = emp['dept__value']
# 					dept_data['dept_data'] = {'not_filled': 0, 'filled': 0, 'total_approved': 0, 'total_employee': 1, 'not_eligible': 1}

# 					data['not_eligible'] = data['not_eligible'] + 1
# 					data['total_employee'] = data['total_employee'] + 1
# 		data['dept_data'].append(dept_data)
# 	return data


# def get_proposed_increment_faculty(emp_id, level, session):
# 	data = {'increment_amount': 0, 'increment_type': '---', 'promoted_to': '---', 'estimated_gross_salary': 0}
# 	qry = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=int(level)).exclude(status="DELETE").values('increment_type', 'id', 'increment_amount', 'promoted_to__value').order_by('-id')
# 	if len(qry) > 0:
# 		data['increment_type'] = qry[0]['increment_type']
# 		data['increment_amount'] = qry[0]['increment_amount']
# 		data['promoted_to'] = qry[0]['promoted_to__value']
# 		emp_salary_type = get_salary_type(emp_id, session, {})
# 		if len(emp_salary_type) > 0:
# 			salary_type = emp_salary_type['salary_type__value']
# 		else:
# 			salary_type = '---'
# 		salary = get_increment_in_salary(data['increment_type'], emp_id, session, salary_type, data['increment_amount'])
# 		data['estimated_gross_salary'] = salary['estimated_salary']
# 	return data


# def get_total_hod_awarded_marks(emp_id, session, session_name, level):
# 	total_marks = 0
# 	overall_total = 0
# 	data = {'cat1': 0, 'cat2': 0, 'cat3': 0, 'cat4': 0}
# 	level = int(level)
# 	fac_app_id = FacultyAppraisal.objects.filter(emp_id=emp_id, session=session, status="SUBMITTED", form_filled_status='Y').exclude(status="DELETE").values_list('id', flat=True).order_by('-id')

# 	approval_status = FacAppRecommendationApproval.objects.filter(emp_id=emp_id, level=1).exclude(status="DELETE").exclude(approval_status="REVIEW").values_list('approval_status', flat=True).order_by('-approval_status')
# 	if len(fac_app_id) > 0 and len(approval_status) > 0:
# 		cat1_marks = 0
# 		cat1A1 = FacAppCat1A1.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0]).exclude(status="DELETE").exclude(score_awarded=None).annotate(total=Sum('score_awarded')).values('total')
# 		if len(cat1A1) > 0:
# 			for cat in cat1A1:
# 				cat1_marks = cat1_marks + cat['total']
# 			# try:
# 			cat1_marks = float(cat1_marks)
# 			cat1_marks = cat1_marks / len(cat1A1)
# 			# except:
# 			#     cat1_marks = 0.0
# 			if float(cat1_marks) > 50.0:
# 				cat1_marks = 50
# 			total_marks = total_marks + cat1_marks
# 		cat1_marks = 0
# 		cat1A2 = FacAppCat1A2.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0]).exclude(status="DELETE").exclude(score_awarded=None).annotate(total=Sum('score_awarded')).values('total')
# 		if len(cat1A2) > 0:
# 			for cat in cat1A2:
# 				cat1_marks = cat1_marks + cat['total']
# 			if float(cat1_marks) > 15.0:
# 				cat1_marks = 15
# 			total_marks = total_marks + cat1_marks
# 		cat1_marks = 0
# 		cat1A3 = FacAppCat1A3.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0]).exclude(status="DELETE").exclude(score_awarded=None).annotate(total=Sum('score_awarded')).values('total')
# 		if len(cat1A3) > 0:
# 			for cat in cat1A3:
# 				cat1_marks = cat1_marks + cat['total']
# 			if float(cat1_marks) > 15.0:
# 				cat1_marks = 15
# 			total_marks = total_marks + cat1_marks
# 		cat1_marks = 0
# 		cat1A4 = FacAppCat1A4.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0]).exclude(status="DELETE").exclude(score_awarded=None).annotate(total=Sum('score_awarded')).values('total')
# 		if len(cat1A4) > 0:
# 			for cat in cat1A4:
# 				cat1_marks = cat1_marks + cat['total']
# 			if float(cat1_marks) > 20.0:
# 				cat1_marks = 20
# 			total_marks = total_marks + cat1_marks
# 		data['cat1'] = total_marks
# 		overall_total = overall_total + total_marks
# 		total_marks = 0

# 		cat2_marks = 0
# 		cat2A1 = FacAppCat2A1.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0]).exclude(status="DELETE").exclude(score_awarded=None).annotate(total=Sum('score_awarded')).values('total')
# 		if len(cat2A1) > 0:
# 			for cat in cat2A1:
# 				cat2_marks = cat2_marks + cat['total']
# 			if float(cat2_marks) > 50.0:
# 				cat2_marks = 50
# 			total_marks = total_marks + cat2_marks
# 		data['cat2'] = total_marks
# 		overall_total = overall_total + total_marks
# 		total_marks = 0

# 		cat3_marks = 0
# 		#### CHECK FOR ACHIEVEMENT ID ####
# 		ach_valid_ids = []
# 		get_ach_id = FacAppCat3Achievement.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0]).exclude(status="DELETE").exclude(score_awarded=None).values('achievement_id', 'type', 'id')
# 		if len(get_ach_id) > 0:
# 			from_date = datetime(2018, 9, 1).date()
# 			to_date = datetime(2019, 8, 31).date()
# 			for ach_id in get_ach_id:
# 				if "BOOKS" in str(ach_id['type']):
# 					check_date_range = AchFacBooks.objects.filter(id=ach_id['achievement_id'], published_date__range=[from_date, to_date]).exclude(status="DELETE").values()
# 					if len(check_date_range) > 0:
# 						ach_valid_ids.append(ach_id['id'])
# 				elif "RESEARCH PAPER IN CONFERENCE" in str(ach_id['type']):
# 					check_date_range = AchFacConferences.objects.filter(id=ach_id['achievement_id'], conference_detail__conference_from__range=[from_date, to_date]).exclude(status="DELETE").values()
# 					if len(check_date_range) > 0:
# 						ach_valid_ids.append(ach_id['id'])
# 				elif "RESEARCH GUIDANCE / PROJECT GUIDANCE" in str(ach_id['type']):
# 					check_date_range = AchFacGuidances.objects.filter(id=ach_id['achievement_id'], date_of_guidance__range=[from_date, to_date]).exclude(status="DELETE").values()
# 					if len(check_date_range) > 0:
# 						ach_valid_ids.append(ach_id['id'])
# 				elif "RESEARCH PAPER IN JOURNAL" in str(ach_id['type']):
# 					check_date_range = AchFacJournals.objects.filter(id=ach_id['achievement_id'], published_date__range=[from_date, to_date]).exclude(status="DELETE").values()
# 					if len(check_date_range) > 0:
# 						ach_valid_ids.append(ach_id['id'])
# 				elif "PATENT" in str(ach_id['type']):
# 					check_date_range = AchFacPatents.objects.filter(id=ach_id['achievement_id'], patent_date__range=[from_date, to_date]).exclude(status="DELETE").values()
# 					if len(check_date_range) > 0:
# 						ach_valid_ids.append(ach_id['id'])
# 				elif "LECTURES AND TALKS" in str(ach_id['type']):
# 					check_date_range = AchFacLecturesTalks.objects.filter(id=ach_id['achievement_id'], date__range=[from_date, to_date]).exclude(status="DELETE").values()
# 					if len(check_date_range) > 0:
# 						ach_valid_ids.append(ach_id['id'])
# 				elif "TRAINING AND DEVELOPMENT PROGRAM" in str(ach_id['type']):
# 					check_date_range = AchFacTrainings.objects.filter(id=ach_id['achievement_id'], from_date__range=[from_date, to_date]).exclude(status="DELETE").values()
# 					if len(check_date_range) > 0:
# 						ach_valid_ids.append(ach_id['id'])
# 				elif "PROJECTS/CONSULTANCY" in str(ach_id['type']):
# 					check_date_range = AchFacProjects.objects.filter(id=ach_id['achievement_id'], start_date__range=[from_date, to_date]).exclude(status="DELETE").values()
# 					if len(check_date_range) > 0:
# 						ach_valid_ids.append(ach_id['id'])
# 		##################################
# 		cat3 = FacAppCat3Achievement.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0], id__in=ach_valid_ids).exclude(status="DELETE").exclude(score_awarded=None).annotate(total=Sum('score_awarded')).values('total')
# 		if len(cat3) > 0:
# 			for cat in cat3:
# 				cat3_marks = cat3_marks + cat['total']
# 			if float(cat3_marks) > 50.0:
# 				cat3_marks = 50
# 			total_marks = total_marks + cat3_marks
# 		data['cat3'] = total_marks
# 		overall_total = overall_total + total_marks
# 		total_marks = 0

# 		cat4_marks = 0
# 		i = 0
# 		cat4A1 = FacAppCat4A1.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0]).exclude(status="DELETE").exclude(score_awarded=None).values('subject', 'branch_details', 'score_awarded')
# 		for cat4 in cat4A1:
# 			if 'INST(1)' in cat4['branch_details']:
# 				i = i + 1
# 				cat4_marks = cat4_marks + cat4['score_awarded']
# 		total_marks = total_marks + cat4_marks / i
# 		cat4A2 = FacAppCat4A2.objects.filter(fac_app_id=fac_app_id[0], status=approval_status[0]).exclude(status="DELETE").exclude(score_awarded=None).values('score_awarded')
# 		if len(cat4A2) > 0:
# 			total_marks = total_marks + cat4A2[0]['score_awarded']
# 		data['cat4'] = total_marks

# 		#### CHANGE ####
# 		# lectures_data = get_employee_subject_setion_wise_total_lecture(emp_id, session, session_name)
# 		# lectures = lectures_data[0]
# 		# print(lectures_data[1], 'subject')
# 		# subject_type = lectures_data[1]
# 		# subject_type = {84, 85, 86, 87, 100, 101}

# 		# row_data = {}
# 		# cat4A2 = {}
# 		# Sessions = []
# 		# Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'o')
# 		# Sessions.append(str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e')
# 		# for ses in Sessions:
# 		#     temp_data = []
# 		#     feedback = faculty_feedback_details([emp_id], ses, subject_type)
# 		#     print(feedback, 'feedback')
# 		#     if len(feedback) > 0:
# 		#         for f_back in feedback:
# 		#             row_data = {'branch': f_back['branch'], 'semester': f_back['sem'], 'section': f_back['section'], 'subject': f_back['subject'], 'overall_avg': f_back['TOTAL'], 'student_feedback': f_back['TOTAL'], 'score_claimed': None}
# 		#             # cat4A2['data'].append(row_data)
# 		#             temp_data.append(row_data)
# 		#         cat4A2['f' + str(ses[-1])] = get_total_of_cat4(temp_data, 'A2', level, 'APPROVED')['overall_feedback']
# 		# if 'fo' not in cat4A2 and 'fe' in cat4A2:
# 		#     cat4A2['final_feedback'] = round(cat4A2['fe'], 2)

# 		# elif 'fe' not in cat4A2 and 'fo' in cat4A2:
# 		#     cat4A2['final_feedback'] = round(cat4A2['fo'], 2)
# 		# elif 'fe' not in cat4A2 and 'fe' not in cat4A2:
# 		#     cat4A2['final_feedback'] = round(0, 2)
# 		# else:
# 		#     cat4A2['final_feedback'] = round(((cat4A2['fo'] + cat4A2['fe']) / 2), 2)

# 		# cat4A2['final_total'] = 0

# 		# if cat4A2['final_feedback'] != None and cat4A2['final_feedback'] > 0:
# 		#     if cat4A2['final_feedback'] >= 8.4:
# 		#         cat4A2['final_total'] = 20
# 		#     elif cat4A2['final_feedback'] >= 6.5 and cat4A2['final_feedback'] < 8.4:
# 		#         difference = cat4A2['final_feedback'] - 6.4
# 		#         cat4A2['final_total'] = round(difference / 0.1, 2)
# 		################
# 		# total_marks = total_marks + cat4A2['final_total']
# 		# data['cat4'] = total_marks
# 		overall_total = overall_total + total_marks

# 	overall_total = round(overall_total, 2)
# 	return [overall_total, data]


# def score_calculation_of_cat3_per_report(ach_type, achievement, session):
# 	data = {'total': 0}
# 	if 'RESEARCH PAPER IN JOURNAL' in ach_type:
# 		for ach in achievement:
# 			ach['score_claimed'] = 0
# 			try:
# 				ach['impact_factor'] = float(ach['impact_factor'])
# 			except:
# 				ach['impact_factor'] = 0
# 			if 'SCI' in ach['journal_details__sub_category__value'] and ach['impact_factor'] != None:
# 				if ach['impact_factor'] >= 2:
# 					ach['score_claimed'] = 20
# 				elif ach['impact_factor'] >= 1 and ach['impact_factor'] < 1.99:
# 					ach['score_claimed'] = 18
# 				elif ach['impact_factor'] >= 0.51 and ach['impact_factor'] < 0.99:
# 					ach['score_claimed'] = 16
# 				elif ach['impact_factor'] >= 0.1 and ach['impact_factor'] < 0.50:
# 					ach['score_claimed'] = 14

# 			elif 'SCOPOUS' in ach['journal_details__sub_category__value'] and ach['impact_factor'] != None:
# 				if ach['impact_factor'] >= 2:
# 					ach['score_claimed'] = 15
# 				elif ach['impact_factor'] >= 1 and ach['impact_factor'] < 1.99:
# 					ach['score_claimed'] = 13
# 				elif ach['impact_factor'] >= 0.51 and ach['impact_factor'] < 0.99:
# 					ach['score_claimed'] = 12
# 				elif ach['impact_factor'] >= 0.1 and ach['impact_factor'] < 0.50:
# 					ach['score_claimed'] = 10

# 			elif 'ICI' in ach['journal_details__sub_category__value']:
# 				ach['score_claimed'] = 5

# 			elif 'UGC' in ach['journal_details__sub_category__value']:
# 				ach['score_claimed'] = 4

# 			else:
# 				ach['score_claimed'] = 3

# 			data['total'] = data['total'] + ach['score_claimed']

# 	elif 'RESEARCH PAPER IN CONFERENCE' in ach_type:
# 		for ach in achievement:
# 			ach['score_claimed'] = 0
# 			if 'IEEE' in ach['sub_category__value']:
# 				ach['score_claimed'] = 5
# 			else:
# 				ach['score_claimed'] = 3
# 			data['total'] = data['total'] + ach['score_claimed']

# 	elif 'BOOKS' in ach_type:
# 		for ach in achievement:
# 			ach['score_claimed'] = 0
# 			if ach['publisher_type__value'] != None and ach['role_for__value'] != None:
# 				if 'INTERNATIONAL' in ach['publisher_type__value']:
# 					if 'BOOK' in ach['role_for__value']:
# 						ach['score_claimed'] = 50
# 					elif 'ARTICLE' in ach['role_for__value'] or 'CHAPTER' in ach['role_for__value']:
# 						ach['score_claimed'] = 10
# 				elif 'NATIONAL' in ach['publisher_type__value']:
# 					if 'BOOK' in ach['role_for__value']:
# 						ach['score_claimed'] = 25
# 					elif 'ARTICLE' or 'CHAPTER' in ach['role_for__value']:
# 						ach['score_claimed'] = 5
# 				elif 'REGIONAL' in ach['publisher_type__value']:
# 					if 'BOOK' in ach['role_for__value']:
# 						ach['score_claimed'] = 15
# 					elif 'ARTICLE' in ach['role_for__value'] or 'CHAPTER' in ach['role_for__value']:
# 						ach['score_claimed'] = 3
# 			data['total'] = data['total'] + ach['score_claimed']

# 	elif 'PROJECTS/CONSULTANCY' in ach_type:
# 		for ach in achievement:
# 			ach['score_claimed'] = 0
# 			if 'PROPOSED' not in ach['project_status__value']:
# 				#### FOR AMOUNT ####
# 				ach['amount'] = 0
# 				if ach['sponsored'] == "yes" or ach['sponsored'] == 'Yes' or ach['sponsored'] == 'YES':
# 					for sponser in ach['sponsers']:
# 						try:
# 							amount = float(sponser['amount'])
# 						except:
# 							amount = 0
# 						ach['amount'] = ach['amount'] + amount
# 				if ach['association'] == "yes" or ach['association'] == 'Yes' or ach['association'] == 'YES':
# 					for asso in ach['associators']:
# 						try:
# 							amount = float(asso['amount'])
# 						except:
# 							amount = 0
# 						ach['amount'] = ach['amount'] + amount
# 				####################

# 				if ach['principal_investigator'] != None and ach['co_principal_investigator'] != None:
# 					if ('self' in ach['principal_investigator'] or 'SELF' in ach['principal_investigator']) and ('other' in ach['co_principal_investigator'] or 'OTHER' in ach['co_principal_investigator']):
# 						if ach['amount'] != None:
# 							if ach['amount'] >= 3000000:
# 								ach['score_claimed'] = 12
# 							elif ach['amount'] >= 500000 and ach['amount'] < 3000000:
# 								ach['score_claimed'] = 9
# 							elif ach['amount'] >= 50000 and ach['amount'] < 500000:
# 								ach['score_claimed'] = 6
# 					elif ('other' in ach['principal_investigator'] or 'OTHER' in ach['principal_investigator']) and ('self' in ach['co_principal_investigator'] or 'SELF' in ach['co_principal_investigator']):
# 						if ach['amount'] != None:
# 							if ach['amount'] >= 3000000:
# 								ach['score_claimed'] = 8
# 							elif ach['amount'] >= 500000 and ach['amount'] < 3000000:
# 								ach['score_claimed'] = 6
# 							elif ach['amount'] >= 50000 and ach['amount'] < 500000:
# 								ach['score_claimed'] = 4
# 					elif ('self' in ach['principal_investigator'] or 'SELF' in ach['principal_investigator']) and ('self' in ach['co_principal_investigator'] or 'SELF' in ach['co_principal_investigator']):
# 						if ach['amount'] != None:
# 							if ach['amount'] >= 3000000:
# 								ach['score_claimed'] = 20
# 							elif ach['amount'] >= 500000 and ach['amount'] < 3000000:
# 								ach['score_claimed'] = 15
# 							elif ach['amount'] >= 50000 and ach['amount'] < 500000:
# 								ach['score_claimed'] = 10
# 			data['total'] = data['total'] + ach['score_claimed']

# 	elif 'PATENT' in ach_type:
# 		for ach in achievement:
# 			ach['score_claimed'] = 0
# 			if ach['patent_details__patent_status__value'] != None and ach['patent_details__level__value'] != None:
# 				if 'GRANTED' in ach['patent_details__patent_status__value'] and 'INTERNATIONAL' in ach['patent_details__level__value']:
# 					ach['score_claimed'] = 40
# 				elif 'GRANTED' in ach['patent_details__patent_status__value'] and 'NATIONAL' in ach['patent_details__level__value']:
# 					ach['score_claimed'] = 25
# 			data['total'] = data['total'] + ach['score_claimed']

# 	elif 'GUIDANCE' in ach_type:
# 		for ach in achievement:
# 			ach['score_claimed'] = 0
# 			if ach['guidance_for__value'] != None and (ach['guidance_awarded_status'] != None or ach['guidance_status__value'] != None):
# 				if ach['guidance_status__value'] == None:
# 					if 'DEGREE' in ach['guidance_for__value'] and (ach['guidance_awarded_status'] == 'Yes' or ach['guidance_awarded_status'] == 'YES' or ach['guidance_awarded_status'] == 'yes'):
# 						ach['score_claimed'] = 3
# 				else:
# 					if 'DEGREE' in ach['guidance_for__value'] and ('AWARDED' in ach['guidance_status__value']):
# 						ach['score_claimed'] = 3
# 				if 'RESEARCH' in ach['guidance_for__value'] and 'SUBMITTED' in ach['guidance_status__value']:
# 					ach['score_claimed'] = 7
# 				if ach['guidance_status__value'] == None:
# 					if 'RESEARCH' in ach['guidance_for__value'] and (ach['guidance_awarded_status'] == 'Yes' or ach['guidance_awarded_status'] == 'YES' or ach['guidance_awarded_status'] == 'yes'):
# 						ach['score_claimed'] = 10
# 				else:
# 					if 'RESEARCH' in ach['guidance_for__value'] and ('AWARDED' in ach['guidance_status__value']):
# 						ach['score_claimed'] = 10
# 			data['total'] = data['total'] + ach['score_claimed']

# 	elif 'TRAINING AND DEVELOPMENT PROGRAM' in ach_type:
# 		for ach in achievement:
# 			ach['score_claimed'] = 0
# 			if ach['to_date'] != None and ach['from_date'] != None:
# 				duration = ach['to_date'] - ach['from_date']
# 				# changed for date range
# 				if duration.days >= 9:
# 					ach['score_claimed'] = 20
# 				elif duration.days >= 4 and duration.days < 13:
# 					ach['score_claimed'] = 10
# 			data['total'] = data['total'] + ach['score_claimed']

# 	elif 'LECTURES AND TALKS' in ach_type:
# 		for ach in achievement:
# 			ach['score_claimed'] = 0
# 			if ach['type_of_event__value'] != None:
# 				if 'INTERNATIONAL' in ach['type_of_event__value']:
# 					ach['score_claimed'] = 10
# 				elif 'NATIONAL' in ach['type_of_event__value']:
# 					ach['score_claimed'] = 5
# 			data['total'] = data['total'] + ach['score_claimed']
# 	return [achievement, data]


# def get_training_sugg(emp_id, session):
# 	data = {}
# 	qry = list(FacultyAppraisal.objects.filter(emp_id=emp_id, form_filled_status="Y", status="SUBMITTED", session=session).exclude(status="DELETE").values('training_needs', 'suggestions').order_by('-id'))
# 	if len(qry) > 0:
# 		data['training'] = qry[0]['training_needs']
# 		data['suggestion'] = qry[0]['suggestions']
# 	return data
