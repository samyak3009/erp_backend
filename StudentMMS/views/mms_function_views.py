from django.shortcuts import render
from django.db.models import Q, Sum, Count, Max, F, OuterRef, Subquery, Avg
from django.http import HttpResponse, JsonResponse
from itertools import groupby
import math
import datetime
import operator
import json
import threading
# from datetime import datetime
import datetime
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from login.views import checkpermission, generate_session_table_name

from Registrar.models import Semtiming, StudentPrimDetail
from StudentMMS.models import *
from StudentMMS.models.models_2021o import *

from StudentAcademics.models import *

from StudentAcademics.views import *
from Store_data.views.functions import get_student_attendance_subjectwise, get_overall_attendance
# Create your views here.



def test(request):
	if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
		# check=checkpermission(request,[211])
		############### if check==200: ####################
		if requestMethod.POST_REQUEST(request):
			############### if request.method=='GET': #########

			############### write your view ###################
			###################################################

			data = []
			return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def test2(request):
	if academicCoordCheck.isSubjectCoord(request):
		# check = checkpermission(request,[1369])
		# if check == 200 and 'S' in request.session['Coordinator_type']:

		############### write your view ###################
		###################################################
		data = {'data': []}
		return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def test3(request):
	if requestByCheck.requestByHOD(request.GET):
		############### if request.GET['request_type']=='hod': ###############

		############### write your view ###################
		###################################################
		data = {'data': []}
		return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def get_btlevel(session):
	qry = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='BLOOM TAXONOMY LEVEL', session=session).values('sno', 'value')
	x = len(qry)
	for i in range(x):
		qry[i]['bt_level_abbr'] = "BL-" + str(i + 1)
	return list(qry)


def get_btleveldata(session_name):
	BTLevelSettings = generate_session_table_name("BTLevelSettings_", session_name)
	qry = BTLevelSettings.objects.exclude(status='DELETE').values('bt_level', 'bt_level__value').distinct()
	x = len(qry)
	for i in range(x):
		qry[i]['bt_level_abbr'] = "BL-" + str(i + 1)
	return list(qry)


def get_skillsetlevel(session):
	qry = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='SKILL SET LEVEL', session=session).values('sno', 'value')
	return list(qry)


def get_skillsetlevel_filtered(bt_level, session_name):
	BTLevelSettings = generate_session_table_name("BTLevelSettings_", session_name)
	qry = BTLevelSettings.objects.filter(bt_level=bt_level).exclude(status='DELETE').exclude(skill_set_level__value__isnull=True).values('skill_set_level', 'skill_set_level__value')
	return list(qry)


def get_verb(bt_level, session_name):
	BTLevelSettings = generate_session_table_name("BTLevelSettings_", session_name)

	qry = BTLevelSettings.objects.filter(bt_level=bt_level).exclude(status='DELETE').exclude(verb__isnull=True).values('verb')
	return list(qry)


def get_vis_mis():
	vis_mis = []
	vis_mis.append({'sno': 'V', 'value': 'VISION'})
	vis_mis.append({'sno': 'M', 'value': 'MISSION'})
	vis_mis.append({'sno': 'QP', 'value': 'QUALITY POLICY'})
	vis_mis.append({'sno': 'PO', 'value': 'PROGRAMME OUTCOMES (POs)'})
	vis_mis.append({'sno': 'PEO', 'value': 'PROGRAM EDUCATION OBJECTIVES (PEOs)'})
	return vis_mis


def get_CO_subject(emp_id, sem, dept, session_name):
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)
	qry = AcadCoordinator.objects.filter(emp_id=emp_id, section__sem_id__sem=sem, section__dept=dept).exclude(status='DELETE').exclude(subject_id__status='DELETE').exclude(subject_id__isnull=True).values('subject_id', 'subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code').distinct()
	return list(qry)

# def get_co(subject_id,session_name):
#   print("im in")
#   SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_",session_name)
#   # SubjectCODetails = generate_session_table_name("SubjectCODetails_",session_name)
#   qry=SubjectCODetailsAttainment.objects.filter(co_id__subject_id=subject_id).exclude(co_id__status='DELETE').exclude(status='DELETE').exclude(co_id__co_num=-1).values('co_id__id','co_id__description','attainment_per')
#   x=len(qry)
#   for i in range(x):
#       qry[i]['co_level_num']="CO-"+ str(i+1)
#       qry[i]['id']=qry[i]['co_id__id']
#       qry[i]['description']=qry[i]['co_id__description']
#   print(list(qry))
#   return list(qry)


def get_co(subject_id, session_name):
	# SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_",session_name)
	SubjectCODetails = generate_session_table_name("SubjectCODetails_", session_name)
	qry = SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').exclude(co_num=-1).values('id', 'description', 'co_num')
	x = len(qry)
	for i in range(x):
		qry[i]['co_level_num'] = "CO-" + str(qry[i]['co_num'])
		# qry[i]['id']=qry['id']
		# qry[i]['description']=qry['description']

	return list(qry)


def get_co_list(subject_id, session_name):
	SubjectCODetails = generate_session_table_name("SubjectCODetails_", session_name)
	print(session_name)
	print(SubjectCODetails)
	qry = SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').exclude(co_num=-1).values_list('id', flat=True)
	print(qry)
	return list(qry)


def get_po(dept, session_name):
	Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)

	qry = Dept_VisMis.objects.filter(dept=dept, type='PO').exclude(status='DELETE').values('id', 'type', 'description')
	x = len(qry)
	for i in range(x):
		qry[i]['po_level_abbr'] = "PO-" + str(i + 1)
	return list(qry)


def get_po_list(dept, session_name):
	Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)

	qry = Dept_VisMis.objects.filter(dept=dept, type='PO').exclude(status='DELETE').values_list('id', flat=True)
	return list(qry)


def get_peo(dept, session_name):
	Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)

	qry = Dept_VisMis.objects.filter(dept=dept, type='PEO').exclude(status='DELETE').values('id', 'type', 'description')
	x = len(qry)
	for i in range(x):
		qry[i]['peo_level_abbr'] = "PEO-" + str(i + 1)
	return list(qry)


def get_peo_list(dept, session_name):
	Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)

	qry = Dept_VisMis.objects.filter(dept=dept, type='PEO').exclude(status='DELETE').values_list('id', flat=True)
	return list(qry)


def get_mission(dept, session_name):
	Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)

	qry = Dept_VisMis.objects.filter(dept=dept, type='M').exclude(status='DELETE').values('id', 'type', 'description')
	x = len(qry)
	for i in range(x):
		qry[i]['m_level_abbr'] = "M-" + str(i + 1)
	return list(qry)


def get_max_marks(session):
	print(session)
	print("samyak")
	qry = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='LEVEL', session=session).values('value')
	return list(qry)


def new_exam_dropdown(session):
	qry = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='DIRECT ATTAINMENT METHOD', session=session).values_list('sno', flat=True)
	qry1 = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(pid__in=qry).values('sno', 'field', 'value'))
	data = {}
	data1 = {}
	# modified############333
	for x in qry1:
		if x['field'] not in data1:
			data1[x['field']] = []
	for y in qry1:
		data1[y['field']].append(y)
	return(data1)
	#################################
	# for k, v in groupby(qry1, key=lambda x: x['field']):
	#
	#     v = list(v)
	#     # print(k,v)
	#     data[k] = v
	#
	# # print(data)
	# return(data)


def get_exam_co_dropdown(session):
	qry = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='DIRECT ATTAINMENT METHOD', session=session).values('sno', 'value', 'pid'))
	return qry


def internal_exam_dropdown(session):
	qry = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).exclude(value='EXAM NAME').filter(field='DIRECT ATTAINMENT METHOD', session=session).values_list('sno', flat=True)
	qry1 = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(pid__in=qry).values('sno', 'value', 'field'))
	data = {}
	for k, v in groupby(qry1, key=lambda x: x['field']):
		v = list(v)
		data[k] = v
	return(data)


def get_survey_dropdown(session):
	qry = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='INDIRECT ATTAINMENT METHOD (INTERNAL)', session=session).values_list('sno', flat=True)

	qry1 = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno__in=qry).values('sno', 'value', 'field'))
	data = {}
	for k, v in groupby(qry1, key=lambda x: x['field']):
		v = list(v)
		if(k == 'INDIRECT ATTAINMENT METHOD (INTERNAL)'):
			data['INDIRECT ATTAINMENT METHOD'] = v
		else:
			data[k] = v
	return(data)

def get_survey_dropdown_external(session):
	qry = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='INDIRECT ATTAINMENT METHOD (EXTERNAL)', session=session).values_list('sno', flat=True)

	qry1 = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno__in=qry).values('sno', 'value', 'field'))
	data = {}
	for k, v in groupby(qry1, key=lambda x: x['field']):
		v = list(v)
		data[k] = v
	return(data)


def get_survey_dropdown_by_sem(sem, session, session_name):
	SurveyAddQuestions = generate_session_table_name("SurveyAddQuestions_", session_name)
	qry = SurveyAddQuestions.objects.filter(sem_id=sem).exclude(survey_id__status='DELETE').exclude(survey_id__value__isnull=True).values('survey_id__sno', 'survey_id__value', 'survey_id__field').distinct()
	# qry=StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='INDIRECT ATTAINMENT METHOD',session=session).values_list('sno',flat=True)

	# qry1=list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno__in=qry).values('sno','value','field'))
	# data={}
	# for k,v in groupby(qry,key=lambda x:x['field']):
	#   v=list(v)
	#   data[k]=v
	return(list(qry))


def get_attempt_type():
	attempt_type = []
	attempt_type.append({'attempt_type': 'M', 'value': 'Mandatory'})
	attempt_type.append({'attempt_type': 'I', 'value': 'Internal Choice'})
	attempt_type.append({'attempt_type': 'O', 'value': 'Overall Choice'})
	return attempt_type


def get_exam_name(session):
	qry = StudentAcademicsDropdown.objects.filter(field='EXAM NAME', session=session).exclude(value__isnull=True).values('value', 'sno', 'pid')

	return list(qry)


def get_coordinator_sem(emp_id, dept, session_name):
	AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)
	qry = AcadCoordinator.objects.filter(emp_id=emp_id, section__dept=dept).exclude(status='DELETE').values('section__sem_id__sem', 'section__sem_id').distinct()
	return list(qry)


def get_exam_shift(session):
	qry = StudentAcademicsDropdown.objects.filter(field='EXAM SHIFT', session=session).exclude(value__isnull=True).values('value', 'sno')
	return list(qry)


def get_sem_mms_subjects(sem, session_name):
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	query = SubjectInfo.objects.filter(sem__in=sem).exclude(status="DELETE").values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_type__value', 'subject_unit', 'subject_unit__value', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'id').distinct()
	return list(query)


def get_ct_group(session):
	qry = StudentAcademicsDropdown.objects.filter(field='CT GROUP', session=session).exclude(value__isnull=True).values('value', 'sno')
	return list(qry)


def create_order_chooser(pet_name):
	function = "create_order_by_" + pet_name
	return eval(function)


def create_order_by_exam(list_data, sort_by_again):
	data = []
	for exam_sno, (exam_name, exam_group) in enumerate(groupby(list_data, key=lambda group_exam: group_exam['marks_id__exam_id__value'])):
		data.append({})
		data[-1]['exam_name'] = exam_name
		temp_exam = list(exam_group)
		if(sort_by_again != []):
			temp_key = sort_by_again[0]
			data[-1]['exam_set'] = create_order_chooser(temp_key)(temp_exam, sort_by_again[1:])
		else:
			data[-1]['exam_set'] = temp_exam

	return data


def create_order_by_subject(list_data, sort_by_again):
	data = []
	for sub_sno, (sub_name, sub_group) in enumerate(groupby(list_data, key=lambda group_sub: group_sub['marks_id__subject_id'])):
		data.append({})
		data[-1]['sub_id'] = sub_name
		# data[-1]['sub_name']=sub_group[0]['marks_id__subject_id__sub_name']
		# data[-1]['sub_name']=sub_group[0]['marks_id__subject_id__alpha_code']+"-"+str(sub_group[0]['marks_id__subject_id__num_code'])
		temp_sub = list(sub_group)
		if(sort_by_again != []):
			temp_key = sort_by_again[0]
			data[-1]['sub_set'] = create_order_chooser(temp_key)(temp_sub, sort_by_again[1:])
		else:
			data[-1]['sub_set'] = temp_sub
	return data


def create_order_by_student(list_data, sort_by_again):
	data = []
	for stu_sno, (stu_name, stu_group) in enumerate(groupby(list_data, key=lambda group_stu: group_stu['uniq_id'])):
		data.append({})
		data[-1]['uniq_id'] = stu_name
		# data[-1]['sub_name']=sub_group[0]['marks_id__subject_id__sub_name']
		# data[-1]['sub_name']=sub_group[0]['marks_id__subject_id__alpha_code']+"-"+str(sub_group[0]['marks_id__subject_id__num_code'])
		temp_stu = list(stu_group)
		if(sort_by_again != []):
			temp_key = sort_by_again[0]
			data[-1]['stu_set'] = create_order_chooser(temp_key)(temp_stu, sort_by_again[1:])
		else:
			data[-1]['stu_set'] = temp_stu
	return data


def create_order_by_total_marks(list_data, sort_by_again):
	data = {}
	data['total_marks'] = sum(filter(None, list(x['marks'] for x in list_data)))
	if(sort_by_again != []):
		temp_key = sort_by_again[0]
		data[temp_key] = create_order_chooser(temp_key)(list_data, sort_by_again[1:])
	else:
		data['detail'] = list_data
	return data


def get_per_exam_per_subject(uniq_id_list, subject_list, exam_name__list):
	StudentMarks = generate_session_table_name("StudentMarks_", session_name)

	query = list(StudentMarks.objects.filter(uniq_id__in=uniq_id_list, marks_id__subject_id__in=subject_list, marks_id__exam_id__in=exam_name__list).exclude(status="DELETE").exclude(marks_id__status="DELETE").values('uniq_id', 'marks_id__subject_id', 'marks_id__subject_id__sub_name', 'marks_id__exam_id', 'marks_id__exam_id__value', 'marks', 'ques_id').order_by('marks_id__exam_id', 'marks_id__subject_id', 'uniq_id').distinct())

	primary_list = create_order_by_exam(query, ['subject', 'student', 'total_marks'])
	# print(primary_list)
	# for course_sno,(course_name,course_group) in enumerate(groupby(data_set,key=lambda group_course:group_course['feedback_id__feedback_id__uniq_id__section__dept__course__value'])):

# print(get_per_exam_per_subject([3801],[1042,142],[93]))
# def get_subject_info(sem_id,subject_type):
#   data=SubjectInfo_1819o.filter(subject_type__value=subject_type,sem_id=sem_id)


def get_subjects_faculty(emp_id, section, session_name, exclude_list):
	FacultyTime = generate_session_table_name("FacultyTime_", session_name)
	qry = FacultyTime.objects.exclude(subject_id__subject_type__value__in=exclude_list).exclude(status='DELETE').filter(emp_id=emp_id, section__in=section).values('section__sem_id__sem', 'section__sem_id__dept__dept__value').distinct().annotate(sub_name=F('subject_id__sub_name'), sub_alpha_code=F('subject_id__sub_alpha_code'), sub_num_code=F('subject_id__sub_num_code'), id=F('subject_id'))
	return (list(qry))


def get_subjects_hod_dean(sem, session_name, exclude_list):
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	query = SubjectInfo.objects.filter(sem__in=sem).exclude(status="DELETE").exclude(subject_type__value__in=exclude_list).values('sub_num_code', 'sub_alpha_code', 'sub_name', 'subject_type', 'subject_type__value', 'subject_unit', 'subject_unit__value', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'added_by', 'time_stamp', 'status', 'session', 'sem', 'id').distinct()
	return list(query)


def get_student_marks(uniq_id, session_name, subject_id, exam_name, max_ct_marks, ct_group, sem_id):
	StudentMarks = generate_session_table_name("StudentMarks_", session_name)
	QuesPaperApplicableOn = generate_session_table_name('QuesPaperApplicableOn_', session_name)
	QuesPaperSectionDetails = generate_session_table_name('QuesPaperSectionDetails_', session_name)

	format_id = list(QuesPaperApplicableOn.objects.filter(ques_paper_id__exam_id=exam_name, sem=sem_id).values('ques_paper_id').order_by('-id')[:1])

	if len(format_id) > 0:
		max_marks = QuesPaperSectionDetails.objects.filter(ques_paper_id=format_id[0]['ques_paper_id']).aggregate(total_marks=Sum('max_marks'))
		total_exam_marks = max_marks.get('total_marks', 0)
	else:
		total_exam_marks = 0

	query = StudentMarks.objects.exclude(status='DELETE').exclude(marks_id__status='DELETE').filter(uniq_id=uniq_id, marks_id__subject_id=subject_id, marks_id__exam_id=exam_name).aggregate(marks_obtained=Sum('marks'))

	marks_obtained = query.get('marks_obtained', 0)

	if marks_obtained is None:

		query2 = list(StudentMarks.objects.exclude(status='DELETE').exclude(marks_id__status='DELETE').filter(uniq_id=uniq_id, marks_id__subject_id=subject_id, marks_id__exam_id=exam_name).values('present_status'))

		if query2:
			marks_obtained = query2[0]['present_status']
			if marks_obtained == 'P':
				marks_obtained = 0

		else:
			marks_obtained = 'NA'

	converted_student_marks = marks_obtained

	if not isinstance(marks_obtained, str):

		max_marks = max_ct_marks / int(ct_group)

		if total_exam_marks > 0:
			converted_student_marks = math.ceil((max_marks / (total_exam_marks)) * (marks_obtained))

		else:
			converted_student_marks = 0

	return {'marks_obtained': marks_obtained, 'converted_marks': converted_student_marks, 'total_marks': total_exam_marks}


def get_student_subject_ta_marks(uniq_id, session_name, subject_id):
	StudentTAMarks = generate_session_table_name("StudentTAMarks_", session_name)

	query = StudentTAMarks.objects.exclude(status='DELETE').exclude(ta_marks_id__status='DELETE').filter(uniq_id=uniq_id, ta_marks_id__subject_id=subject_id).values('ct_viva_marks', 'ta_lab_marks').order_by('-id')[:1]

	total_marks = 'N/A'
	if len(query) > 0:
		total_marks = 0
		if query[0]['ct_viva_marks'] is not None:
			total_marks += query[0]['ct_viva_marks']

		if query[0]['ta_lab_marks'] is not None:
			total_marks += query[0]['ta_lab_marks']

	return total_marks


def get_groups_section(group_id, extra_filter, session_name):
	GroupSection = generate_session_table_name("GroupSection_", session_name)
	q_group_sec = GroupSection.objects.filter(group_id=group_id).filter(**extra_filter).values_list('section_id', flat=True)
	return list(q_group_sec)


def get_groups_students(group_id, session_name):
	data = []
	group_section = get_groups_section(group_id, {}, session_name)
	for sec in group_section:
		data.append(get_att_group_section_students(group_id, sec, session_name))

	return list(data)


def get_student_subject_att_marks_new(uniq_id, session_name, subject_type, sem_id, max_att_marks):
	studentSession = generate_session_table_name("studentSession_", session_name)
	AttMarksRule = generate_session_table_name("AttMarksRule_", session_name)
	session_num = int(session_name[:2])
	data = {}
	qry_from_to_date = Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end', 'uid')

	session = qry_from_to_date[0]['uid']

	from_date = datetime.strptime(str(qry_from_to_date[0]['sem_start']).split('T')[0], "%Y-%m-%d").date()
	to_date = datetime.strptime(str(qry_from_to_date[0]['sem_end']).split('T')[0], "%Y-%m-%d").date()
	if session_num >= 19:
		query = get_overall_attendance(uniq_id, session_name, session)

		for q in query:
			data[q['uniq_id']] = {}
			for sub, sub_data in q['sub_wise_att'].items():
				data[q['uniq_id']][sub] = {}
				sub_att_per = 0
				marks = 'N/A'
				if sub_data['total_att'] > 0:
					sub_att_per = round((sub_data['present_count'] * 100.0) / sub_data['total_att'])
				else:
					sub_att_per = 0

				qry_rule = AttMarksRule.objects.filter(subject_type=subject_type, sem=sem_id, from_att_per__lte=sub_att_per, to_att_per__gte=sub_att_per, max_att_marks=max_att_marks).exclude(status='DELETE').values('marks').order_by('-id')[:1]

				if len(qry_rule) == 0:
					marks = "Rule Not Defined for this attendance percentage"
				else:
					marks = min(max_att_marks, qry_rule[0]['marks'])
				data[q['uniq_id']][sub] = {'att_per': sub_att_per, 'att_marks': marks}

	return data


def get_student_subject_att_marks(uniq_id, session_name, subject_id, subject_type, sem_id, max_att_marks):
	studentSession = generate_session_table_name("studentSession_", session_name)
	AttMarksRule = generate_session_table_name("AttMarksRule_", session_name)

	qry_from_to_date = Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end', 'uid')

	session = qry_from_to_date[0]['uid']

	from_date = datetime.strptime(str(qry_from_to_date[0]['sem_start']).split('T')[0], "%Y-%m-%d").date()
	to_date = datetime.strptime(str(qry_from_to_date[0]['sem_end']).split('T')[0], "%Y-%m-%d").date()

	att_type = get_sub_attendance_type(session)
	att_type_li = [t['sno'] for t in att_type]
	q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
	query = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type_li, [{"id": subject_id}], 1, [], session_name)

	if query['total'] > 0:
		sub_att_per = round((query['present_count'] * 100.0) / query['total'])
	else:
		sub_att_per = 0

	qry_rule = AttMarksRule.objects.filter(subject_type=subject_type, sem=sem_id, from_att_per__lte=sub_att_per, to_att_per__gte=sub_att_per, max_att_marks=max_att_marks).exclude(status='DELETE').values('marks').order_by('-id')[:1]

	if len(qry_rule) == 0:
		marks = "Rule Not Defined for this attendance percentage"
	else:
		marks = min(max_att_marks, qry_rule[0]['marks'])

	return {'att_per': sub_att_per, 'att_marks': marks}


def get_student_subject_ct_marks(uniq_id, session_name, subject_id, subject_type, max_ct_marks, sem_id):

	studentSession = generate_session_table_name("studentSession_", session_name)
	CTMarksRule = generate_session_table_name("CTMarksRule_", session_name)

	ct_group = int(list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP', session__session_name=session_name).values('value', 'sno'))[0]['value'])

	qry_ct_group = CTMarksRule.objects.filter(subject_type=subject_type, sem=sem_id).exclude(status='DELETE').values('ct_group', 'ct_to_select')

	final_ct_marks = 0

	for group in qry_ct_group:
		exam_ids = group['ct_group'].split(",")
		exam_marks = []
		for exam in exam_ids:
			converted_marks = get_student_marks(uniq_id, session_name, subject_id, exam, max_ct_marks, ct_group, sem_id)['converted_marks']
			if not isinstance(converted_marks, str) and not isinstance(converted_marks, str):
				exam_marks.append(converted_marks)
			else:
				exam_marks.append(0)
		exam_marks.sort(reverse=True)

		for marks in exam_marks[:group['ct_to_select']]:
			if not isinstance(marks, str):
				final_ct_marks += marks

	return min(final_ct_marks, max_ct_marks)


def get_student_subject_bonus_marks(uniq_id, given_marks_dict, given_max_marks_dict, session_name, subject_type, sem_id, att_per, marks_obtained, max_marks):

	BonusMarksRule = generate_session_table_name("BonusMarksRule_", session_name)

	qry_bonus_rules = BonusMarksRule.objects.filter(subject_type=subject_type, sem=sem_id).exclude(status='DELETE').values('given_ct', 'min_marks_per', 'min_att_per', 'bonus_marks', 'max_marks_limit_per')
	rule_data = []
	for rule in qry_bonus_rules:
		if rule['given_ct'] is not None and rule['given_ct'] != '':
			given_ct_list = rule['given_ct'].split(',')

			keys = given_marks_dict.keys()

			if not set(given_ct_list).issubset(set(keys)):
				rule_data.append(0)
				continue

		flg_min_marks = False
		for (key, value) in given_marks_dict.items():
			per = (given_marks_dict[key] * 100) // given_max_marks_dict[key]

			if per < rule['min_marks_per']:
				flg_min_marks = True
				break

		if flg_min_marks:
			rule_data.append(0)
			continue

		if rule['min_att_per'] is not None:
			if att_per < rule['min_att_per']:
				rule_data.append(0)
				continue

		max_per_marks = math.ceil((rule['max_marks_limit_per'] * max_marks) / 100.0)

		flg_add_bonus = False
		if rule['max_marks_limit_per'] != 100:
			if round(((marks_obtained * 100) / max_marks), 2) < rule['max_marks_limit_per']:
				flg_add_bonus = True
		else:
			flg_add_bonus = True

		if flg_add_bonus:
			new_marks_obtained = marks_obtained
			new_marks_obtained += rule['bonus_marks']
			new_marks_obtained = min(new_marks_obtained, max_per_marks)

		rule_data.append(new_marks_obtained - marks_obtained)
		marks_obtained = new_marks_obtained

	return {'marks_obtained': marks_obtained, 'rule_data': rule_data}


def get_student_subject_extra_bonus_marks(uniq_id, subject_id, session_name):

	ExtraBonus = generate_session_table_name("ExtraBonus_", session_name)

	qry_bonus_rules = ExtraBonus.objects.filter(uniq_id=uniq_id, subject_id=subject_id).exclude(status='DELETE').values_list('bonus_marks', flat=True)
	if len(qry_bonus_rules) > 0:
		return qry_bonus_rules[0]
	else:
		return 0


def single_student_ct_marks(session_name, student, subject_details, extra):
	SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
	SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	sem = studentSession.objects.filter(uniq_id=student).values('sem')[0]['sem']
	if 'ct_group' in extra:
		ct_group = extra['ct_group']
	else:
		ct_group = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP', session__session_name=session_name).values('value', 'sno'))[0]['value']
	exams_conducted = (SubjectQuestionPaper.objects.exclude(status='DELETE').filter(subject_id__sem=sem).values('exam_id', 'exam_id__value').distinct().order_by('exam_id'))
	student_marks = []
	student_max = []
	student_obtain = []
	for subject in subject_details:
		subject_column_data = {}
		given_marks_dict = {}
		given_max_marks_dict = {}
		for exam in exams_conducted:
			marks = get_student_marks(student, session_name, subject['id'], exam['exam_id'], subject['max_ct_marks'], ct_group, subject['sem'])
			converted_marks = marks['converted_marks']
			subject_column_data['converted_marks'] = converted_marks

			if not isinstance(converted_marks, str) and not isinstance(converted_marks, str):
				given_marks_dict[str(exam['exam_id'])] = marks['marks_obtained']
				given_max_marks_dict[str(exam['exam_id'])] = marks['total_marks']
		student_sub_ct_marks = get_student_subject_ct_marks(student, session_name, subject['id'], subject['subject_type'], subject['max_ct_marks'], subject['sem'])
		######## CT MARKS ##################
		subject_column_data['converted_marks'] = student_sub_ct_marks

		ta_marks = get_student_subject_ta_marks(student, session_name, subject['id'])

		subject_att_marks = get_student_subject_att_marks(student, session_name, subject['id'], subject['subject_type'], subject['sem'], subject['max_att_marks'])
		####### TA MARKS ####################
		subject_column_data['ta_marks'] = ta_marks
		####### ATTENDANCE % ################
		subject_column_data['att_per'] = subject_att_marks['att_per']
		####### ATTENDANCE MARKS ############
		subject_column_data['attendance_marks'] = subject_att_marks['att_marks']

		total_marks = 0
		if not isinstance(student_sub_ct_marks, str) and not isinstance(student_sub_ct_marks, str):
			total_marks += student_sub_ct_marks

		if not isinstance(subject_att_marks['att_marks'], str) and not isinstance(subject_att_marks['att_marks'], str):
			total_marks += subject_att_marks['att_marks']

		if not isinstance(ta_marks, str) and not isinstance(ta_marks, str):
			total_marks += ta_marks

		######## TOTAL MARKS ##############
		subject_column_data['obtained_marks'] = total_marks

		############# BONUS RULE ####################

		max_marks = float(subject['max_att_marks']) + float(subject['max_ct_marks']) + float(subject['max_ta_marks'])

		bonus_marks_data = get_student_subject_bonus_marks(student, given_marks_dict, given_max_marks_dict, session_name, subject['subject_type'], sem, subject_att_marks['att_per'], total_marks, max_marks)
		total_marks = bonus_marks_data['marks_obtained']

		subject_column_data['rule_data'] = bonus_marks_data['rule_data']
		subject_column_data['marks_obtained'] = total_marks
		subject_column_data['total_marks'] = max_marks
		student_max.append(max_marks)
		student_obtain.append(total_marks)
		subject_column_data['subject_name'] = subject['sub_name'] + ' (' + subject['sub_alpha_code'] + '-' + subject['sub_num_code'] + ')'

		############ STUDENT SUBJECT MARKS DATA ######

		student_marks.append(subject_column_data)

	return {'data': student_marks, 'avg_marks_obt': sum(student_obtain), 'avg_total_marks': sum(student_max)}


def get_batch_dropdown(dept, session_name):
	studentSession = generate_session_table_name("studentSession_", session_name)
	qry = studentSession.objects.filter(sem__dept=dept).values('uniq_id__batch_from', 'uniq_id__batch_to').distinct().order_by('uniq_id__batch_from')
	for q in qry:
		q['value'] = str(q['uniq_id__batch_from']) + "-" + str(q['uniq_id__batch_to'])
	return list(qry)


def get_batch_session_dropdown(batch, session_name):
	studentSession = generate_session_table_name("studentSession_", session_name)
	batch_array = batch.split("-")
	q = []
	batch_from = int(batch_array[0][2:])
	batch_to = int(batch_array[1][2:])
	session = int(session_name[:2])
	initial_batch = batch_from
	while(batch_from <= batch_to and batch_from <= session):
		if(int(batch_from) >= 18):
			term = str(batch_from) + str(batch_from + 1)
			q.append(term + 'o')
			if batch_from == session and session_name[4:] == 'o':
				pass
			else:
				q.append(term + 'e')
		batch_from += 1
	return q


def get_attainment_level_list(subject_type, sem, session_name):
	MarksAttainmentSettings = generate_session_table_name("MarksAttainmentSettings_", session_name)

	attainment_level = list(MarksAttainmentSettings.objects.exclude(status='DELETE').filter(attainment_type='D', subject_type=subject_type, sem=sem).values('from_direct_per', 'to_indirect_per', 'attainment_level'))

	return attainment_level


def get_subject_ct_co_attainment(subject_id, sub_type, sem, session, session_name):

	Marks = generate_session_table_name("Marks_", session_name)
	StudentMarks = generate_session_table_name("StudentMarks_", session_name)
	QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
	SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	exam_list = get_exam_name(session)
	exam_data = []
	attainment_level = None
	attainment_level_list = get_attainment_level_list(sub_type, sem, session_name)
	attainment_level_list = attainment_level_list[::-1]
	co_list = []
	ye_arr = []
	no_arr = []

	for e in exam_list:
		qry_co = QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_paper_id__exam_id=e['sno'], ques_paper_id__subject_id=subject_id, ques_paper_id__approval_status='APPROVED').values('ques_id__co_id', 'ques_id__co_id__description').distinct().order_by('ques_id__co_id__co_num')
		percentage = []
		for co in qry_co:
			co_attainment = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').filter(co_id=co['ques_id__co_id'], attainment_method=e['pid']).values('attainment_per'))

			qry_marks = StudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).filter(ques_id__ques_id__co_id=co['ques_id__co_id'], present_status='P', marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id).values('marks', 'uniq_id', 'ques_id__ques_paper_id', 'ques_id').order_by('uniq_id')
			if qry_marks:
				yes = 0
				no = 0
				final_result = 0
				for k, v in groupby(qry_marks, key=lambda x: x['uniq_id']):
					v = list(v)
					total_marks = 0
					ques_paper_id = 0

					for t in v:
						if t['marks'] != None:
							total_marks = total_marks + t['marks']
					qid = []

					max_marks = QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_id__co_id=co['ques_id__co_id'], ques_paper_id=v[0]['ques_id__ques_paper_id']).values('ques_num', 'section_id', 'section_id__name', 'ques_id').order_by('section_id', 'ques_num')

					for a, b in groupby(max_marks, key=lambda x: x['ques_num']):
						for m, n in groupby(b, key=lambda s: s['section_id']):
							n = list(n)
							qid.append(n[0]['ques_id'])

					co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
					max_marks_co = co_max_marks.get('co_max_marks', 0)
					if max_marks_co != None:
						attainment_per_obtained = (total_marks / max_marks_co) * 100.0

						if co_attainment:
							if co_attainment[0]['attainment_per'] != None:

								if attainment_per_obtained >= co_attainment[0]['attainment_per']:
									yes += 1
								else:
									no += 1
						else:
							final_result = None

				if final_result != None:

					if(yes > 0):

						final_result = (yes / (yes + no)) * 100.0

				co_list.append({'co_id': co['ques_id__co_id'], 'co_name': co['ques_id__co_id__description'], 'percentage': final_result})

	co_total_per = 0
	l = 0

	for c in co_list:

		if c['percentage'] != None:
			co_total_per = co_total_per + c['percentage']

			l += 1

	if l > 0:
		avg_per = round(co_total_per / l)
		attainment_level = None

		for attainment in attainment_level_list:

			if(attainment['from_direct_per'] <= round(avg_per) and attainment['to_indirect_per'] >= round(avg_per)):
				attainment_level = attainment['attainment_level']
				break
	else:
		attainment_level = None

	return attainment_level

def get_subject_ct_co_attainment_dept_wise(subject_id, sub_type, sem, session,session_name,secondary_branch):

	Marks = generate_session_table_name("Marks_", session_name)
	StudentMarks = generate_session_table_name("StudentMarks_", session_name)
	QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
	SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	exam_list = get_exam_name(session)
	exam_data = []
	attainment_level = None
	attainment_level_list = get_attainment_level_list(sub_type, sem, session_name)
	attainment_level_list = attainment_level_list[::-1]
	co_list = []
	ye_arr = []
	no_arr = []

	for e in exam_list:
		qry_co = QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_paper_id__exam_id=e['sno'], ques_paper_id__subject_id=subject_id, ques_paper_id__approval_status='APPROVED').values('ques_id__co_id', 'ques_id__co_id__description').distinct().order_by('ques_id__co_id__co_num')
		percentage = []
		for co in qry_co:
			co_attainment = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').filter(co_id=co['ques_id__co_id'], attainment_method=e['pid']).values('attainment_per'))

			qry_marks = StudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX"))).filter(uniq_id__uniq_id__dept_detail__dept_id__in=secondary_branch,ques_id__ques_id__co_id=co['ques_id__co_id'], present_status='P', marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id).values('marks', 'uniq_id', 'ques_id__ques_paper_id', 'ques_id').order_by('uniq_id')
			if qry_marks:
				yes = 0
				no = 0
				final_result = 0
				for k, v in groupby(qry_marks, key=lambda x: x['uniq_id']):
					v = list(v)
					total_marks = 0
					ques_paper_id = 0

					for t in v:
						if t['marks'] != None:
							total_marks = total_marks + t['marks']
					qid = []

					max_marks = QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_id__co_id=co['ques_id__co_id'], ques_paper_id=v[0]['ques_id__ques_paper_id']).values('ques_num', 'section_id', 'section_id__name', 'ques_id').order_by('section_id', 'ques_num')

					for a, b in groupby(max_marks, key=lambda x: x['ques_num']):
						for m, n in groupby(b, key=lambda s: s['section_id']):
							n = list(n)
							qid.append(n[0]['ques_id'])

					co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
					max_marks_co = co_max_marks.get('co_max_marks', 0)
					if max_marks_co != None:
						attainment_per_obtained = (total_marks / max_marks_co) * 100.0

						if co_attainment:
							if co_attainment[0]['attainment_per'] != None:

								if attainment_per_obtained >= co_attainment[0]['attainment_per']:
									yes += 1
								else:
									no += 1
						else:
							final_result = None

				if final_result != None:

					if(yes > 0):

						final_result = (yes / (yes + no)) * 100.0

				co_list.append({'co_id': co['ques_id__co_id'], 'co_name': co['ques_id__co_id__description'], 'percentage': final_result})

	co_total_per = 0
	l = 0

	for c in co_list:

		if c['percentage'] != None:
			co_total_per = co_total_per + c['percentage']

			l += 1

	if l > 0:
		avg_per = round(co_total_per / l)
		attainment_level = None

		for attainment in attainment_level_list:

			if(attainment['from_direct_per'] <= round(avg_per) and attainment['to_indirect_per'] >= round(avg_per)):
				attainment_level = attainment['attainment_level']
				break
	else:
		attainment_level = None

	return attainment_level

def get_subject_university_co_attainment(subject_id, sub_type, sem, session, session_name):
	# print(subject_id, sub_type, sem, session, session_name)
	SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", session_name)

	attainment_level = None
	co_per = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').exclude(co_id__status='DELETE').filter(co_id__subject_id=subject_id, co_id__co_num=-1).values('id').annotate(co_req_attain=F('attainment_per')))
	# print(co_per, 'co_per')

	if co_per:
		max_marks = list(SubjectInfo.objects.filter(id=subject_id).values('id', 'max_university_marks'))
		qry_marks = StudentUniversityMarks.objects.filter(subject_id=subject_id).exclude(Q(uniq_id__uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__uniq_id__admission_status__value="FAILED") | Q(uniq_id__uniq_id__admission_status__value="PASSED") | Q(uniq_id__uniq_id__admission_status__value__contains="EX")).values('external_marks', 'back_marks', 'uniq_id')
		# print(qry_marks, 'qry_marks')
		attainment_level_list = get_attainment_level_list(sub_type, sem, session_name)

		yes = 0
		no = 0
		if(subject_id==1674):
			print(len(qry_marks))
		for q in qry_marks:
			if q['back_marks'] == None:
				marks_obtained = q['external_marks']
			else:
				marks_obtained = q['back_marks']

			if marks_obtained is not None:
				if marks_obtained.isnumeric():

					attainment_per_obtained = (float(marks_obtained) / max_marks[0]['max_university_marks']) * 100.0
					if attainment_per_obtained >= co_per[0]['co_req_attain']:
						yes += 1
					else:
						no += 1
			else:
				no += 1
		if(yes > 0):
			final_per = (yes / (yes + no)) * 100.0
		else:
			final_per = 0
		final_per=round(final_per)
		for attainment in attainment_level_list:
			if(attainment['from_direct_per'] <= final_per and attainment['to_indirect_per'] >= final_per):
				attainment_level = attainment['attainment_level']
				break

	return attainment_level

def get_subject_university_co_attainment_dept_wise(subject_id, sub_type, sem, session, session_name,secondary_branch):
	# print(subject_id, sub_type, sem, session, session_name)
	SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", session_name)

	attainment_level = None
	co_per = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').exclude(co_id__status='DELETE').filter(co_id__subject_id=subject_id, co_id__co_num=-1).values('id').annotate(co_req_attain=F('attainment_per')))
	# print(co_per, 'co_per')

	if co_per:
		max_marks = list(SubjectInfo.objects.filter(id=subject_id).values('id', 'max_university_marks'))
		qry_marks = StudentUniversityMarks.objects.filter(uniq_id__uniq_id__dept_detail__dept_id__in=secondary_branch,subject_id=subject_id).exclude(Q(uniq_id__uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__uniq_id__admission_status__value="FAILED") | Q(uniq_id__uniq_id__admission_status__value="PASSED") | Q(uniq_id__uniq_id__admission_status__value__contains="EX")).values('external_marks', 'back_marks', 'uniq_id')
		# print(qry_marks, 'qry_marks')
		attainment_level_list = get_attainment_level_list(sub_type, sem, session_name)

		yes = 0
		no = 0
		if(subject_id==1674):
			print(len(qry_marks))
		for q in qry_marks:
			if q['back_marks'] == None:
				marks_obtained = q['external_marks']
			else:
				marks_obtained = q['back_marks']

			if marks_obtained is not None:
				if marks_obtained.isnumeric():

					attainment_per_obtained = (float(marks_obtained) / max_marks[0]['max_university_marks']) * 100.0
					if attainment_per_obtained >= co_per[0]['co_req_attain']:
						yes += 1
					else:
						no += 1
			else:
				no += 1
		if(yes > 0):
			final_per = (yes / (yes + no)) * 100.0
		else:
			final_per = 0
		final_per=round(final_per)
		for attainment in attainment_level_list:
			if(attainment['from_direct_per'] <= final_per and attainment['to_indirect_per'] >= final_per):
				attainment_level = attainment['attainment_level']
				break

	return attainment_level



def get_subject_assignment_co_attainment(subject_id, exam_pid, sub_type, sem, session, session_name):

	SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	AssignmentQuizMarks = generate_session_table_name("AssignmentQuizMarks_", session_name)
	AssignmentStudentMarks = generate_session_table_name("AssignmentStudentMarks_", session_name)
	QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
	SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)

	attainment_level = None
	attainment_level_list = get_attainment_level_list(sub_type, sem, session_name)
	attainment_level_list = attainment_level_list[::-1]
	# print("Funcition")
	exam_id = AssignmentQuizMarks.objects.exclude(status='DELETE').filter(subject_id=subject_id, exam_id__pid=exam_pid).values('exam_id').distinct()
	for e in exam_id:
		qry = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno=e['exam_id']).values('pid', 'sno'))
		co_wise = AssignmentQuizMarks.objects.exclude(status='DELETE').filter(subject_id=subject_id, exam_id=e['exam_id']).values_list('isco_wise', flat=True)
		qry_marks = AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=e['exam_id'], marks_id__subject_id=subject_id, present_status='P').values('uniq_id', 'marks', 'marks_id', 'ques_id__ques_paper_id', 'ques_id', 'marks_id__max_marks', 'marks_id__isco_wise').order_by('uniq_id')

		yes = 0
		no = 0
		if 'N' in co_wise:
			final_per = 0
			co_attainment = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').filter(co_id__subject_id=subject_id, attainment_method=qry[0]['pid']).values('attainment_per'))
			for k, v in groupby(qry_marks, key=lambda x: x['uniq_id']):
				total_marks = 0
				v = list(v)
				for t in v:
					if t['marks'] != None:
						total_marks = total_marks + t['marks']
				if v[0]['marks_id__isco_wise'] == 'N':
					max_marks = v[0]['marks_id__max_marks']

				else:
					paper_data = QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_paper_id=v[0]['ques_id__ques_paper_id']).values('ques_num', 'section_id', 'section_id__name', 'ques_id')
					qid = []
					for a, b in groupby(paper_data, key=lambda x: x['ques_num']):
						for m, n in groupby(b, key=lambda s: s['section_id']):
							n = list(n)
							qid.append(n[0]['ques_id'])

					co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
					max_marks = co_max_marks.get('co_max_marks', 0)

				attainment_per_obtained = (float(total_marks) / max_marks) * 100.0
				if co_attainment:
					if attainment_per_obtained >= co_attainment[0]['attainment_per']:
						yes += 1
					else:
						no += 1
				else:
					final_per = None

			if final_per != None:
				if(yes > 0):
					final_per = (yes / (yes + no)) * 100.0
				else:
					final_per = 0

		else:
			final_result = 0
			qry_co = list(QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_paper_id__exam_id=e['exam_id'], ques_paper_id__subject_id=subject_id, ques_paper_id__approval_status='APPROVED').values('ques_id__co_id', 'ques_id__co_id__description', 'ques_paper_id').distinct().order_by('ques_id__co_id__co_num'))
			i = 0
			percentage = 0
			c = 0
			for co in qry_co:
				co_attainment = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').filter(co_id=co['ques_id__co_id'], attainment_method=qry[0]['pid']).values('attainment_per'))
				qry_marks = AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(ques_id__ques_id__co_id=co['ques_id__co_id'], present_status='P', marks_id__exam_id=e['exam_id'], marks_id__subject_id=subject_id).values('marks', 'uniq_id', 'ques_id__ques_paper_id', 'ques_id').order_by('uniq_id')

				for k, v in groupby(qry_marks, key=lambda x: x['uniq_id']):
					v = list(v)
					total_marks = 0
					ques_paper_id = 0
					for t in v:
						if t['marks'] != None:
							total_marks = total_marks + t['marks']
					qid = []
					max_marks = QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_id__co_id=co['ques_id__co_id'], ques_paper_id=v[0]['ques_id__ques_paper_id']).values('ques_num', 'section_id', 'section_id__name', 'ques_id')
					for a, b in groupby(max_marks, key=lambda x: x['ques_num']):
						for m, n in groupby(b, key=lambda s: s['section_id']):
							n = list(n)
							qid.append(n[0]['ques_id'])
					co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
					max_marks_co = co_max_marks.get('co_max_marks', 0)

					if max_marks_co != None:
						attainment_per_obtained = (total_marks / max_marks_co) * 100.0
						if co_attainment[0]['attainment_per'] != None:
							if attainment_per_obtained >= co_attainment[0]['attainment_per']:
								yes += 1
							else:
								no += 1
						else:
							final_result = None

				if final_result != None:
					if(yes > 0):
						final_result = (yes / (yes + no)) * 100.0
					else:
						final_result = 0

					percentage = percentage + final_result
					c += 1
				i += 1
				if(i == len(qry_co)):
					final_per = percentage / c

		if final_per != None:
			for attainment in attainment_level_list:
				if(attainment['from_direct_per'] <= final_per and attainment['to_indirect_per'] >= final_per):
					attainment_level = attainment['attainment_level']
					break
		else:
			attainment_level = None

	return attainment_level

def get_subject_assignment_co_attainment_dept_wise(subject_id, exam_pid, sub_type, sem, session, session_name,secondary_branch):

	SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	AssignmentQuizMarks = generate_session_table_name("AssignmentQuizMarks_", session_name)
	AssignmentStudentMarks = generate_session_table_name("AssignmentStudentMarks_", session_name)
	QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
	SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)

	attainment_level = None
	attainment_level_list = get_attainment_level_list(sub_type, sem, session_name)
	attainment_level_list = attainment_level_list[::-1]
	# print("Funcition")
	exam_id = AssignmentQuizMarks.objects.exclude(status='DELETE').filter(subject_id=subject_id, exam_id__pid=exam_pid).values('exam_id').distinct()
	for e in exam_id:
		qry = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno=e['exam_id']).values('pid', 'sno'))
		co_wise = AssignmentQuizMarks.objects.exclude(status='DELETE').filter(subject_id=subject_id, exam_id=e['exam_id']).values_list('isco_wise', flat=True)
		qry_marks = AssignmentStudentMarks.objects.exclude(status='DELETE').filter(uniq_id__uniq_id__dept_detail__dept_id__in=secondary_branch,marks_id__exam_id=e['exam_id'], marks_id__subject_id=subject_id, present_status='P').values('uniq_id', 'marks', 'marks_id', 'ques_id__ques_paper_id', 'ques_id', 'marks_id__max_marks', 'marks_id__isco_wise').order_by('uniq_id')

		yes = 0
		no = 0
		if 'N' in co_wise:
			final_per = 0
			co_attainment = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').filter(co_id__subject_id=subject_id, attainment_method=qry[0]['pid']).values('attainment_per'))
			for k, v in groupby(qry_marks, key=lambda x: x['uniq_id']):
				total_marks = 0
				v = list(v)
				for t in v:
					if t['marks'] != None:
						total_marks = total_marks + t['marks']
				if v[0]['marks_id__isco_wise'] == 'N':
					max_marks = v[0]['marks_id__max_marks']

				else:
					paper_data = QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_paper_id=v[0]['ques_id__ques_paper_id']).values('ques_num', 'section_id', 'section_id__name', 'ques_id')
					qid = []
					for a, b in groupby(paper_data, key=lambda x: x['ques_num']):
						for m, n in groupby(b, key=lambda s: s['section_id']):
							n = list(n)
							qid.append(n[0]['ques_id'])

					co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
					max_marks = co_max_marks.get('co_max_marks', 0)

				attainment_per_obtained = (float(total_marks) / max_marks) * 100.0
				if co_attainment:
					if attainment_per_obtained >= co_attainment[0]['attainment_per']:
						yes += 1
					else:
						no += 1
				else:
					final_per = None

			if final_per != None:
				if(yes > 0):
					final_per = (yes / (yes + no)) * 100.0
				else:
					final_per = 0

		else:
			final_result = 0
			qry_co = list(QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_paper_id__exam_id=e['exam_id'], ques_paper_id__subject_id=subject_id, ques_paper_id__approval_status='APPROVED').values('ques_id__co_id', 'ques_id__co_id__description', 'ques_paper_id').distinct().order_by('ques_id__co_id__co_num'))
			i = 0
			percentage = 0
			c = 0
			for co in qry_co:
				co_attainment = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').filter(co_id=co['ques_id__co_id'], attainment_method=qry[0]['pid']).values('attainment_per'))
				qry_marks = AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(uniq_id__uniq_id__dept_detail__dept_id__in=secondary_branch,ques_id__ques_id__co_id=co['ques_id__co_id'], present_status='P', marks_id__exam_id=e['exam_id'], marks_id__subject_id=subject_id).values('marks', 'uniq_id', 'ques_id__ques_paper_id', 'ques_id').order_by('uniq_id')

				for k, v in groupby(qry_marks, key=lambda x: x['uniq_id']):
					v = list(v)
					total_marks = 0
					ques_paper_id = 0
					for t in v:
						if t['marks'] != None:
							total_marks = total_marks + t['marks']
					qid = []
					max_marks = QuestionPaperQuestions.objects.exclude(status='SAVED').exclude(status='DELETE').filter(ques_id__co_id=co['ques_id__co_id'], ques_paper_id=v[0]['ques_id__ques_paper_id']).values('ques_num', 'section_id', 'section_id__name', 'ques_id')
					for a, b in groupby(max_marks, key=lambda x: x['ques_num']):
						for m, n in groupby(b, key=lambda s: s['section_id']):
							n = list(n)
							qid.append(n[0]['ques_id'])
					co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
					max_marks_co = co_max_marks.get('co_max_marks', 0)

					if max_marks_co != None:
						attainment_per_obtained = (total_marks / max_marks_co) * 100.0
						if co_attainment[0]['attainment_per'] != None:
							if attainment_per_obtained >= co_attainment[0]['attainment_per']:
								yes += 1
							else:
								no += 1
						else:
							final_result = None

				if final_result != None:
					if(yes > 0):
						final_result = (yes / (yes + no)) * 100.0
					else:
						final_result = 0

					percentage = percentage + final_result
					c += 1
				i += 1
				if(i == len(qry_co)):
					final_per = percentage / c

		if final_per != None:
			for attainment in attainment_level_list:
				if(attainment['from_direct_per'] <= final_per and attainment['to_indirect_per'] >= final_per):
					attainment_level = attainment['attainment_level']
					break
		else:
			attainment_level = None

	return attainment_level


def subject_overall_attainment(subject_id, sub_type, sem, session_name, session):
	# print(subject_id, sub_type, sem, session_name, session)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	Marks = generate_session_table_name("Marks_", session_name)
	AssignmentQuizMarks = generate_session_table_name("AssignmentQuizMarks_", session_name)
	StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", session_name)
	MarksAttainmentSettings = generate_session_table_name("MarksAttainmentSettings_", session_name)

	proportion_detail = list(MarksAttainmentSettings.objects.exclude(status='DELETE').exclude(external_marks__isnull=True).exclude(internal_marks__isnull=True).filter(subject_type=sub_type, sem=sem, attainment_type='A').values('external_marks', 'internal_marks'))
	# print(proportion_detail, 'proportion_detail')
	subject_detail = list(SubjectInfo.objects.filter(id=subject_id).exclude(status='DELETE').values('id', 'subject_type__value', 'sem', 'subject_type', 'sub_alpha_code', 'sub_num_code', 'sub_name'))
	subject_detail[0]['attainment_data'] = []
	subject_ct_entry = Marks.objects.filter(subject_id=subject_detail[0]['id']).exclude(status='DELETE').values('id')
	# print(subject_ct_entry, 'subject_ct_entry')
	subject_data = []
	internal = 0
	internal_attainment = 0
	external_attainment = 0
	univ = 0
	if subject_ct_entry:
		ct_attainment_level = get_subject_ct_co_attainment(subject_detail[0]['id'], subject_detail[0]['subject_type'], subject_detail[0]['sem'], session, session_name)
		# print(ct_attainment_level, 'ct_attainment_level')
		if ct_attainment_level != None and ct_attainment_level != '-':
			internal_attainment = internal_attainment + ct_attainment_level

		subject_detail[0]['attainment_data'].append({'CT': ct_attainment_level})
		internal += 1

	subject_university_entry = StudentUniversityMarks.objects.filter(subject_id=subject_id).values('id')
	# print(subject_university_entry, 'subject_university_entry')
	if subject_university_entry:
		univ_attainment_level = get_subject_university_co_attainment(subject_detail[0]['id'], subject_detail[0]['subject_type'], subject_detail[0]['sem'], session, session_name)
		# print(univ_attainment_level, 'univ_attainment_level')
		subject_detail[0]['attainment_data'].append({'University_Result': univ_attainment_level})
		if univ_attainment_level != None:
			external_attainment = univ_attainment_level
			univ = 1

	assignment_quiz_id = list(AssignmentQuizMarks.objects.filter(subject_id=subject_detail[0]['id']).exclude(status='DELETE').values('exam_id__pid').distinct())
	# print(assignment_quiz_id, 'assignment_quiz_id')
	for assignment_id in assignment_quiz_id:
		assignment_detail = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno=assignment_id['exam_id__pid']).values('value')
		assignment_attainment_level = get_subject_assignment_co_attainment(subject_detail[0]['id'], assignment_id['exam_id__pid'], subject_detail[0]['subject_type'], subject_detail[0]['sem'], session, session_name)
		subject_detail[0]['attainment_data'].append({assignment_detail[0]['value']: assignment_attainment_level})
		if assignment_attainment_level != None:
			internal += 1
			internal_attainment = internal_attainment + assignment_attainment_level

	if proportion_detail:
		if internal > 0:
			internal_attainment = internal_attainment / internal
		external_attain = (external_attainment * proportion_detail[0]['external_marks']) / 100.0
		internal_attain = (internal_attainment * proportion_detail[0]['internal_marks']) / 100.0
		if external_attain > 0 or internal_attain > 0:
			overall_attain = external_attain + internal_attain
		else:
			overall_attain = None
	elif(external_attainment > 0 or internal_attainment > 0):
		overall_attain = (external_attainment + internal_attainment) / (internal + univ)
	else:
		overall_attain = None
	subject_detail[0]['attainment_data'].append({'Overall_Attainment': overall_attain})

	return subject_detail

def subject_overall_attainment_dept_wise(subject_id, sub_type, sem, session_name, session,secondary_branch):
	# print(subject_id, sub_type, sem, session_name, session)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	Marks = generate_session_table_name("Marks_", session_name)
	AssignmentQuizMarks = generate_session_table_name("AssignmentQuizMarks_", session_name)
	StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", session_name)
	MarksAttainmentSettings = generate_session_table_name("MarksAttainmentSettings_", session_name)

	proportion_detail = list(MarksAttainmentSettings.objects.exclude(status='DELETE').exclude(external_marks__isnull=True).exclude(internal_marks__isnull=True).filter(subject_type=sub_type, sem=sem, attainment_type='A').values('external_marks', 'internal_marks'))
	# print(proportion_detail, 'proportion_detail')
	subject_detail = list(SubjectInfo.objects.filter(id=subject_id).exclude(status='DELETE').values('id', 'subject_type__value', 'sem', 'subject_type', 'sub_alpha_code', 'sub_num_code', 'sub_name'))
	subject_detail[0]['attainment_data'] = []
	subject_ct_entry = Marks.objects.filter(subject_id=subject_detail[0]['id']).exclude(status='DELETE').values('id')
	# print(subject_ct_entry, 'subject_ct_entry')
	subject_data = []
	internal = 0
	internal_attainment = 0
	external_attainment = 0
	univ = 0
	if subject_ct_entry:
		ct_attainment_level = get_subject_ct_co_attainment_dept_wise(subject_detail[0]['id'], subject_detail[0]['subject_type'], subject_detail[0]['sem'], session, session_name,secondary_branch)
		# print(ct_attainment_level, 'ct_attainment_level')
		if ct_attainment_level != None and ct_attainment_level != '-':
			internal_attainment = internal_attainment + ct_attainment_level

		subject_detail[0]['attainment_data'].append({'CT': ct_attainment_level})
		internal += 1

	subject_university_entry = StudentUniversityMarks.objects.filter(subject_id=subject_id).values('id')
	# print(subject_university_entry, 'subject_university_entry')
	if subject_university_entry:
		univ_attainment_level = get_subject_university_co_attainment_dept_wise(subject_detail[0]['id'], subject_detail[0]['subject_type'], subject_detail[0]['sem'], session, session_name,secondary_branch)
		# print(univ_attainment_level, 'univ_attainment_level')
		subject_detail[0]['attainment_data'].append({'University_Result': univ_attainment_level})
		if univ_attainment_level != None:
			external_attainment = univ_attainment_level
			univ = 1

	assignment_quiz_id = list(AssignmentQuizMarks.objects.filter(subject_id=subject_detail[0]['id']).exclude(status='DELETE').values('exam_id__pid').distinct())
	# print(assignment_quiz_id, 'assignment_quiz_id')
	for assignment_id in assignment_quiz_id:
		assignment_detail = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno=assignment_id['exam_id__pid']).values('value')
		assignment_attainment_level = get_subject_assignment_co_attainment_dept_wise(subject_detail[0]['id'], assignment_id['exam_id__pid'], subject_detail[0]['subject_type'], subject_detail[0]['sem'], session, session_name,secondary_branch)
		subject_detail[0]['attainment_data'].append({assignment_detail[0]['value']: assignment_attainment_level})
		if assignment_attainment_level != None:
			internal += 1
			internal_attainment = internal_attainment + assignment_attainment_level

	if proportion_detail:
		if internal > 0:
			internal_attainment = internal_attainment / internal
		external_attain = (external_attainment * proportion_detail[0]['external_marks']) / 100.0
		internal_attain = (internal_attainment * proportion_detail[0]['internal_marks']) / 100.0
		if external_attain > 0 or internal_attain > 0:
			overall_attain = external_attain + internal_attain
		else:
			overall_attain = None
	elif(external_attainment > 0 or internal_attainment > 0):
		overall_attain = (external_attainment + internal_attainment) / (internal + univ)
	else:
		overall_attain = None
	subject_detail[0]['attainment_data'].append({'Overall_Attainment': overall_attain})

	return subject_detail


def get_subject_po_target_level(subject_id, po_id, session_name, session):

	SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	SubjectCOPOMapping = generate_session_table_name("SubjectCOPOMapping_", session_name)

	qry = SubjectCOPOMapping.objects.filter(co_id__subject_id=subject_id, po_id=po_id).exclude(co_id__status="DELETE").exclude(status='DELETE').aggregate(total_po_attain=Sum('max_marks')).get('total_po_attain', 0)

	qry_count = SubjectCOPOMapping.objects.filter(co_id__subject_id=subject_id, po_id=po_id).exclude(co_id__status="DELETE").exclude(status='DELETE').count()

	if qry_count:
		target_level = qry / qry_count
	else:
		target_level = None

	return target_level


def get_po_avg_target_level(subject_array, po_id, session_name, session):
	sum_ = 0
	i = 0
	for subject in subject_array:
		po_target = get_subject_po_target_level(subject['id'], po_id, session_name, session)

		if po_target != None:
			sum_ = sum_ + po_target
			i += 1
	if i != 0:
		avg = sum_ / i
	else:
		avg = None

	return avg


def get_subject_po_attainment(subject_id, sub_type, po_id, sem, session_name, session):

	subject_overall = subject_overall_attainment(subject_id, sub_type, sem, session_name, session)
	# print(subject_overall, 'subject_overall')
	subject_po_attain = get_subject_po_target_level(subject_id, po_id, session_name, session)
	# print(subject_po_attain, 'subject_po_attain')
	subject_overall_attain = subject_overall[0]['attainment_data']
	subject_attainment = None

	for att in subject_overall_attain:
		field = list(att)[0]

		if field == 'Overall_Attainment':
			subject_attainment = att[field]

	if subject_attainment != None and subject_po_attain != None:
		po_attainment_value = (subject_attainment * subject_po_attain) / 3.0

	else:
		po_attainment_value = None

	return po_attainment_value

def get_subject_po_attainment_dept_wise(subject_id, sub_type, po_id, sem, session_name, session,secondary_branch):

	subject_overall = subject_overall_attainment_dept_wise(subject_id, sub_type, sem, session_name, session,secondary_branch)
	# print(subject_overall, 'subject_overall')
	subject_po_attain = get_subject_po_target_level(subject_id, po_id, session_name, session)
	# print(subject_po_attain, 'subject_po_attain')
	subject_overall_attain = subject_overall[0]['attainment_data']
	subject_attainment = None

	for att in subject_overall_attain:
		field = list(att)[0]

		if field == 'Overall_Attainment':
			subject_attainment = att[field]

	if subject_attainment != None and subject_po_attain != None:
		po_attainment_value = (subject_attainment * subject_po_attain) / 3.0

	else:
		po_attainment_value = None

	return po_attainment_value

def get_overall_direct_po_attainment(subject_list, po_id, sem, session_name, session):

	i = 0
	po_attainment = None
	for sub in subject_list:
		po_attainment_value = get_subject_po_attainment(sub['id'], sub['subject_type'], po_id, sem, session_name, session)

		if po_attainment_value != None:
			if po_attainment == None:
				po_attainment = 0
			po_attainment = po_attainment_value + po_attainment
			i += 1

	if po_attainment != None:
		overall_po_attainment = po_attainment / i

	else:
		overall_po_attainment = None

	return overall_po_attainment

def get_student_feedback_po_wise(survey_id, sem_id, extra_filter, session_name, session):

	data_values = []
	SurveyAddQuestions = generate_session_table_name("SurveyAddQuestions_", session_name)
	SurveyFillFeedback = generate_session_table_name("SurveyFillFeedback_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)
	for survey in survey_id:
		i = 0
		data = []
		question = []
		students = SurveyFillFeedback.objects.filter(**extra_filter).filter(ques_id__survey_id=survey).exclude(status='DELETE').exclude(ques_id__status='DELETE').values('uniq_id__uniq_id__name', 'uniq_id', 'uniq_id__uniq_id__uni_roll_no', 'ques_id__survey_id__value').order_by('uniq_id__uniq_id__name').distinct()
		question=SurveyFillFeedback.objects.filter(**extra_filter).filter(ques_id__survey_id=survey).exclude(status='DELETE').exclude(ques_id__status='DELETE').values('ques_id__description').distinct()
		# pd=SurveyFillFeedback.objects.filter(ques_id__sem_id=sem_id,ques_id__survey_id=survey).values('ques_id__po_id','ques_id__survey_id__value','ques_id__po_id__type','ques_id__po_id__description').distinct().order_by('ques_id__po_id')
		dept = StudentSemester.objects.filter(sem_id=sem_id).values('dept')
		pd = Dept_VisMis.objects.filter(dept=dept[0]['dept'], type='PO').exclude(status='DELETE').values('id', 'description').distinct().order_by('id')

		if students and pd:
			x = len(pd)
			for i in range(x):
				pd[i]['po_level_abbr'] = "PO-" + str(i + 1)

			po = list(pd)
			data.append({})
			data[0]['survey_id'] = students[0]['ques_id__survey_id__value']
			data[0]['po'] = []
			data[0]['po'].extend(po)
			data[0]['feedback'] = []
			data[0]['average'] = []
			data[0]['average_question_wise'] = []
			data[0]['question'] = []
			data[0]['question'].extend(question)
			j = 0
			for stu in students:
				data[0]['feedback'].append({})
				data[0]['feedback'][j]['student'] = stu['uniq_id__uniq_id__name']
				data[0]['feedback'][j]['uni_roll_no'] = stu['uniq_id__uniq_id__uni_roll_no']
				data[0]['feedback'][j]['data'] = []
				data[0]['feedback'][j]['data_question_wise'] = []
				for q in question:
					qry_ques = SurveyFillFeedback.objects.exclude(status='DELETE').exclude(ques_id__status='DELETE').filter(uniq_id=stu['uniq_id'], ques_id__sem_id=sem_id, ques_id__survey_id=survey, ques_id__description=q['ques_id__description']).values('feedback')
					feedback = qry_ques[0]['feedback']
					data[0]['feedback'][j]['data_question_wise'].append(feedback)  
				for p in po:
					qry = SurveyFillFeedback.objects.exclude(status='DELETE').exclude(ques_id__status='DELETE').filter(uniq_id=stu['uniq_id'], ques_id__sem_id=sem_id, ques_id__survey_id=survey, ques_id__po_id=p['id']).annotate(Feedback=Sum(F("feedback"))).aggregate(Avg('Feedback'))
					if qry['Feedback__avg'] is not None:
						feed = qry['Feedback__avg']
						data[0]['feedback'][j]['data'].append(feed)
					else:
						data[0]['feedback'][j]['data'].append(None)
				j += 1
			data_values.append(data)

			for p in po:
				count = 0
				s = 0
				for stu in students:
					qry = SurveyFillFeedback.objects.exclude(status='DELETE').exclude(ques_id__status='DELETE').filter(ques_id__sem_id=sem_id, ques_id__survey_id=survey, ques_id__po_id=p['id'], uniq_id=stu['uniq_id']).annotate(Feedback=Sum(F("feedback"))).aggregate(Avg('Feedback'))
					if qry['Feedback__avg'] is not None:
						count += 1
						s += qry['Feedback__avg']
					else:
						pass
				if count == 0:
					data[0]['average'].append(None)
				else:
					average = s / count
					data[0]['average'].append(average)
	return data_values


def get_student_feedback_avg_po_wise(dept_id, extra_filter, session_name, batch):
	data_values = []
	final_data = []
	batch_array = batch.split("-")
	from_yr = batch_array[0]
	to_yr = batch_array[1]
	batch_from = int(batch_array[0][2:])
	for s in session_name:
		qry_key = Semtiming.objects.filter(session_name=s).values('uid').distinct()
		print(qry_key)
		survey_id_internal = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='INDIRECT ATTAINMENT METHOD (INTERNAL)', session=qry_key[0]['uid']).values_list('sno', flat=True)
		print(survey_id_internal)
		survey_id_external = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='INDIRECT ATTAINMENT METHOD (EXTERNAL)',session=qry_key[0]['uid']).values_list('sno',flat=True)
		print(survey_id_external)
		Dept_VisMis = generate_session_table_name("Dept_VisMis_", s)		
		session = list(Semtiming.objects.filter(session_name=s).values('uid'))
		batch_till = int(s[:2])
		sem_type = s[-1:]
		if sem_type == 'o':
			plus_factor = 1
		else:
			plus_factor = 2
		sem = (2 * (batch_till - batch_from)) + plus_factor
		t1 = threading.Thread(target=po_internal_data,args=(survey_id_internal,sem,s,data_values,session[0]['uid'],extra_filter,dept_id,))
		t2 = threading.Thread(target=po_external_data,args=(survey_id_external,from_yr,to_yr,dept_id,session[0]['uid'],s,data_values))
		t1.start()
		t2.start()
		t1.join()
		t2.join()
	po1 = list(Dept_VisMis.objects.filter(dept=dept_id, type='PO').exclude(status='DELETE').values('id', 'description').distinct().order_by('id'))
	for p in po1:
		q = 0
		count = 0
		for x in data_values:
			for y in x[0]['po']:
				if y['description'] == p['description']:

					if y['average'] is not None:

						q += y['average']
						count += 1
		if count != 0:
			p['average'] = q / count
		else:
			p['average'] = None
	final_data.append({'data_values': data_values, 'final_average': po1})
	return final_data
def po_internal_data(survey_id_internal,sem,s,data_values,session,extra_filter,dept_id):
	SurveyAddQuestions = generate_session_table_name("SurveyAddQuestions_", s)
	SurveyFillFeedback = generate_session_table_name("SurveyFillFeedback_", s)
	studentSession = generate_session_table_name("studentSession_", s)
	Dept_VisMis = generate_session_table_name("Dept_VisMis_", s)
	for survey in survey_id_internal:
		i = 0
		data = []
		students = SurveyFillFeedback.objects.filter(**extra_filter).filter(ques_id__survey_id=survey, uniq_id__sem__sem=sem).exclude(ques_id__status='DELETE').values('uniq_id__uniq_id__name', 'uniq_id', 'uniq_id__uniq_id__uni_roll_no', 'ques_id__survey_id__value').order_by('uniq_id__uniq_id__name').distinct()
		qq=None
		faculty = InternalFacSurveyAnswer.objects.filter(ques_id__form_id__survey_id=survey,ques_id__form_id__session=session,ques_id__form_id__dept_id=dept_id).exclude(ques_id__po_id=json.dumps(qq)).exclude(ques_id__form_id__status=0).values('ans')
		# print(faculty,"herere")
		pd = Dept_VisMis.objects.filter(dept=dept_id, type='PO').exclude(status='DELETE').values('id', 'description').distinct().order_by('id')
		if pd:
			x = len(pd)
			for i in range(x):
				pd[i]['po_level_abbr'] = "PO-" + str(i + 1)
			po = list(pd)
			data.append({})
			# if students:
			# 	data[0]['survey_id__value'] = students[0]['ques_id__survey_id__value']
			# else:
			qry1 = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno=survey).values('value','field')
			data[0]['survey_id__value'] = qry1[0]['value']
			data[0]['survey_id'] = survey
			data[0]['survey'] = qry1[0]['field'].split('(')[1][:-1]
			data[0]['po'] = []
			# data[0]['average']=[]
			i = 0
			threads = list()
			for p in po:
				r = threading.Thread(target=thread_po_internal_wise,args=(students,dept_id,survey,p,po,s,faculty,))
				threads.append(r)
				r.start()
			for index, thread in enumerate(threads):
				thread.join()
			data[0]['po'].extend(po)
			# print(data[0]['po'])
			data_values.append(data)
def thread_po_internal_wise(students,dept_id,survey,p,po,s,faculty):
	SurveyFillFeedback = generate_session_table_name("SurveyFillFeedback_", s)
	count = 0
	w = 0
	for stu in students:
		qry = SurveyFillFeedback.objects.exclude(status='DELETE').exclude(ques_id__status='DELETE').filter(ques_id__sem_id__dept=dept_id, ques_id__survey_id=survey, ques_id__po_id=p['id'], uniq_id=stu['uniq_id']).annotate(Feedback=Sum(F("feedback"))).aggregate(Avg('Feedback'))
		if qry['Feedback__avg'] is not None:
			count += 1
			w += qry['Feedback__avg']
		else:
			pass
	####################################addon by samyak for internal faculty survey####################################
	for fac in faculty:
		if p['id'] in fac['ans']['po_id']:
			if fac['ans']['answer'] is not None:
				######### converting it into 3 pointer############
				fac_ans=(fac['ans']['answer']/fac['ans']['max'])*3
				count+=1
				w+=fac_ans
	#####################################################################################################################
	if count == 0:
		p['average'] = None
	else:
		average = w / count
		p['average'] = average


def po_external_data(survey_arry,from_yr,to_yr,dept_id,session,session_name,data_values):
	Dept_VisMis = generate_session_table_name("Dept_VisMis_",session_name)
	for survey in survey_arry:
		i=0
		data=[]
		pd = Dept_VisMis.objects.filter(dept=dept_id, type='PO').exclude(status='DELETE').values('id', 'description').distinct().order_by('id')
		print(dept_id)
		print(survey)
		print(session)
		answer = list(ExternalSurveyAnswer.objects.exclude(ques_id__form_id__status='DELETE').exclude(ques_id__po_id='null').filter(ques_id__form_id__dept=dept_id,ques_id__form_id__batch_from=from_yr,ques_id__form_id__batch_to=to_yr,ques_id__form_id__survey_id=survey,ques_id__form_id__session=session).values('ques_id__po_id','ques_id__form_id__survey_id__value','ans_attribute'))
		print(len(answer))
		if pd:
			x = len(pd)
			for i in range(x):
				pd[i]['po_level_abbr'] = "PO-" + str(i + 1)
			po = list(pd)
			data.append({})
			# if answer:
			# 	data[0]['survey_id__value'] = answer[0]['ques_id__form_id__survey_id__value']
			# else:
			qry1 = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(sno=survey).values('value','field')
			data[0]['survey_id__value'] = qry1[0]['value']
			data[0]['survey_id'] = survey
			data[0]['survey'] = qry1[0]['field'].split('(')[1][:-1]
			data[0]['po'] = []
			threads = list()
			for p in po:
				x = threading.Thread(target=thread_po_external_wise,args=(po,p,answer,))
				threads.append(x)
				x.start()
			for index, thread in enumerate(threads):
				thread.join()
			data[0]['po'].extend(po)
			data_values.append(data)
	# return data
def thread_po_external_wise(po,p,answer):
	count=0
	s=0
	for ans in answer:
		po_array = json.loads(ans['ques_id__po_id'])
		for x in po_array:
			if x==p['id']:
				feedback_ans = ans['ans_attribute']['answer']
				feedback_max = ans['ans_attribute']['max']
				feedback = feedback_ans/feedback_max
				count+=1
				s+=feedback
			else:
				pass
	if count==0:
		p['average'] = None
	else:
		average = (s/count)*3
		p['average'] = average

def overall_po_attainment(overall_direct_po_attainment, overall_indirect_po_attainment, sem, session_name, session):

	MarksAttainmentSettings = generate_session_table_name("MarksAttainmentSettings_", session_name)

	attainment_proportion = list(MarksAttainmentSettings.objects.exclude(status='DELETE').filter(sem=sem, attainment_type='A').values('from_direct_per', 'to_indirect_per'))
	# print(attainment_proportion)
	d = i = None
	if attainment_proportion:
		if overall_direct_po_attainment is not None:
			d = (overall_direct_po_attainment * attainment_proportion[0]['from_direct_per']) / 100.0

		if overall_indirect_po_attainment is not None:
			i = (overall_indirect_po_attainment * attainment_proportion[0]['to_indirect_per']) / 100.0

		if d is not None or i is not None:
			if i is None:
				i = 0
			elif d is None:
				d = 0
			overall_po_attainment = d + i

		else:
			overall_po_attainment = None
			# print("1", overall_po_attainment)

	else:
		overall_po_attainment = None
		# print("2", overall_po_attainment, sem)

	return overall_po_attainment


def peo_mi_avg(mission, dept, session_name):
	SubjectPEOMIMapping = generate_session_table_name("SubjectPEOMIMapping_", session_name)
	peo_list = get_peo_list(dept, session_name)
	data = []
	for m in mission:
		qry = SubjectPEOMIMapping.objects.filter(peo_id__in=peo_list, m_id=m['id']).exclude(status='DELETE').annotate(Marks=Sum(F("marks"))).aggregate(Avg('Marks'))
		if qry['Marks__avg'] is not None:
			data.append({'mission': m['description'], 'average': qry['Marks__avg'], 'id': m['id'], 'mi_abbr': m['m_level_abbr']})
		else:
			data.append({'mission': m['description'], 'average': None, 'id': m['id'], 'mi_abbr': m['m_level_abbr']})

	return data


def get_po_peo_achieved_level(subject_array, dept, session_name, session, batch):

	po_list = get_po(dept, session_name)
	peo_list = get_peo(dept, session_name)
	marks = get_max_marks(session)
	SubjectPOPEOMapping = generate_session_table_name("SubjectPOPEOMapping_", session_name)

	overall_indirect_po_attainment = get_student_feedback_avg_po_wise(dept, {}, [session_name], batch)[0]['final_average']
	for po in po_list:
		po_sum = 0
		subject_sem_value = 0
		# subject['sem']=4
		i = 0
		for subject in subject_array:
			subject_sem_value = subject['sem']
			for subject_po in subject['po_data']:
				if po['description'] == subject_po['po_desc'] and subject_po['sub_po_attain'] is not None:
					po_sum = po_sum + subject_po['sub_po_attain']
					i += 1

		if po_sum != 0 and i != 0:
			po['overall_direct_po_attainment'] = po_sum / i
		else:
			po['overall_direct_po_attainment'] = None

		for target in overall_indirect_po_attainment:
			if po['description'] == target['description']:
				po['overall_indirect_po_attainment'] = target['average']

		po['overall_po_attainment'] = overall_po_attainment(po['overall_direct_po_attainment'], po['overall_indirect_po_attainment'], subject_sem_value, session_name, session)

		po['peo_data'] = []

		for peo in peo_list:
			qry = list(SubjectPOPEOMapping.objects.filter(po_id=po['id'], peo_id=peo['id']).exclude(status='DELETE').values('marks'))

			if qry and po['overall_po_attainment'] != None and marks:
				peo_attain = (po['overall_po_attainment'] * qry[0]['marks']) / float(marks[0]['value'])
			else:
				peo_attain = None

			po['peo_data'].append({'peo_id': peo['id'], 'peo_description': peo['description'], 'attained': peo_attain})

	for peo in peo_list:

		peo_sum = 0
		i = 0
		for po in po_list:
			for peo_data in po['peo_data']:
				if peo_data['peo_description'] == peo['description'] and peo_data['attained'] is not None:
					peo_sum = peo_sum + peo_data['attained']
					i += 1
		if peo_sum != 0 and i != 0:
			peo['achieved_level'] = peo_sum / i
		else:
			peo['achieved_level'] = None

		peo_query = SubjectPOPEOMapping.objects.filter(peo_id=peo['id']).exclude(status='DELETE').annotate(peo_sum=Sum(F('marks'))).aggregate(Avg('peo_sum'))

		peo['target_level'] = peo_query['peo_sum__avg']

		if peo['target_level'] is not None and peo['achieved_level'] is not None:
			peo['gap'] = peo['achieved_level'] - peo['target_level']
		else:
			peo['gap'] = None

	data = {'po_list': po_list, 'peo_list': peo_list}

	return data


def get_group_exam_with_same_format(sem_id, session_name):
	data = []
	QuesPaperApplicableOn = generate_session_table_name('QuesPaperApplicableOn_', session_name)
	qry = QuesPaperApplicableOn.objects.filter(sem__in=sem_id).exclude(ques_paper_id__status="DELETE").values('ques_paper_id__exam_id', 'ques_paper_id__exam_id__value', 'ques_paper_id__common_key').order_by('ques_paper_id__common_key')
	for group, group_data in groupby(qry, key=lambda group: group['ques_paper_id__common_key']):
		temp_data = []
		for g in group_data:
			if g['ques_paper_id__common_key'] == None:
				data.append([g])
			else:
				temp_data.append(g)
		if len(temp_data) > 0:
			data.append(temp_data)
	return data


def check_if_format_is_same(exam, session_name):
	QuesPaperFormat = generate_session_table_name('QuesPaperFormat_', session_name)
	qry = QuesPaperFormat.objects.filter(emp_id__in=exam).exclude(status="DELETE").values('common_key').distinct()
	if len(qry) > 1:
		return False
	return True
########################################## FUNCTIONS AFTER CT-RULE AND BONUS-RULE CHANGE ########################################


def check_rule_weight(rules):
	rule_weightage = 0
	for rule in rules:
		for group in rule:
			group_weightage = group['ct_to_select'] * group['weightage']
			rule_weightage = rule_weightage + group_weightage
		if rule_weightage == 100:
			rule_weightage = 0
			continue
		else:
			return False

	return True


def create_order_by_subrule_no(rule_data, sort_by_again):
	temp_data = []
	for subrule_no, (subrule, subrule_data) in enumerate(groupby(rule_data, key=lambda subrule: subrule['subrule_no'])):
		temp_data.append({})
		temp_data[-1]['subrule_no'] = subrule
		temp_data[-1]['criteria'] = []
		temp_data[-1]['criteria_data'] = []
		temp_subrule_data = list(subrule_data)

		for sub in temp_subrule_data:
			if sub['subrule_id__name'] in temp_data[-1]['criteria']:
				continue
			else:
				for k, v in sub.items():
					if 'subrule_id__name' in k:
						temp_data[-1]['criteria'].append(v)
					elif 'subrule_id' not in k and 'app_id' not in k:
						temp_data[-1][k] = v
					elif k == str('subrule_id'):
						temp_data[-1]['criteria_data'].append({'type_id': sub['subrule_id__type_id'], 'type': sub['subrule_id__type'], 'name': sub['subrule_id__name'], 'id': sub['subrule_id']})
					else:
						temp_data[-1][k] = v

	return temp_data


def create_order_by_rule_no(data, sort_by_again):
	temp_data = []
	for rule_no, (rule, rule_data) in enumerate(groupby(data, key=lambda rule: rule['rule_no'])):
		temp_data.append({})
		temp_data[-1]['rule'] = rule
		temp_rule = list(rule_data)
		if(len(sort_by_again) > 1):
			temp_key = sort_by_again[1]
			temp_data[-1]['rule_data_set'] = create_order_chooser(temp_key)(temp_rule, sort_by_again[1:])
		else:
			temp_data[-1]['rule_data_set'] = temp_rule

	return temp_data


def create_order_by_group(rule_data, sort_by_again):
	temp_data = []
	for group_no, (group, group_data) in enumerate(groupby(rule_data, key=lambda rule: rule['group_no'])):
		temp_data.append({})
		temp_group_data = list(group_data)
		temp_data[-1]['group_no'] = group_no
		if len(temp_group_data) > 0:
			for k, v in temp_group_data[0].items():
				if 'exam_id' not in k and 'exam_id__value' not in k:
					temp_data[-1][k] = v
		if(len(sort_by_again) > 1):
			temp_key = sort_by_again[1]
			temp_data[-1]['group_data_set'] = create_order_chooser(temp_key)(temp_group, sort_by_again[1:])
		else:
			temp_data[-1]['group_data_set'] = []
			for g in temp_group_data:
				temp_data[-1]['group_data_set'].append(g['exam_id'])

	return temp_data


# def get_external_marks(uniq_id, subjects, session_name):
# 	data = {}
# 	subject_data = {}
# 	marks_obtained = 0
# 	total_marks = 0
# 	percentage = 0

# 	StudentUniversityMarks = generate_session_table_name('StudentUniversityMarks_', session_name)
# 	studentSession = generate_session_table_name('studentSession_', session_name)
# 	SubjectInfo = generate_session_table_name('SubjectInfo_', session_name)

# 	get_subjects = []
# 	get_sem = list(studentSession.objects.filter(uniq_id=uniq_id).values_list('sem', flat=True))
# 	if len(get_sem) > 0:

# 		#### FOR SUBJECTS ####
# 		if len(subjects) > 0:
# 			get_subjects = list(SubjectInfo.objects.filter(sem_id=get_sem[0]).exclude(status="DELETE").values_list('id', flat=True))
# 		else:
# 			get_subjects = subjects

# 		for sub in get_subjects:
# 			max_external = 0
# 			get_max_subject_marks = list(SubjectInfo.objects.filter(id=sub).exclude(status="DELETE").values('max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks'))
# 			if len(get_max_subject_marks) > 0:
# 				for k, v in get_max_subject_marks[0].items():
# 					if v != None:
# 						max_external += v
# 				subject_data[sub] = max_external
# 		#######################

# 	get_marks = StudentUniversityMarks.objects.filter(uniq_id=uniq_id, subject_id__in=get_subjects).values('external_marks', 'internal_marks', 'back_marks', 'subject_id')
# 	for subject in get_marks:
# 		subject['back_marks'] = subject.get('back_marks', 0)
# 		subject['external_marks'] = subject.get('external_marks', 0)
# 		subject['internal_marks'] = subject.get('internal_marks', 0)
# 		try:
# 			subject['back_marks'] = float(subject['back_marks'])
# 		except:
# 			subject['back_marks'] = 0

# 		try:
# 			subject['external_marks'] = float(subject['external_marks'])
# 		except:
# 			subject['external_marks'] = 0

# 		try:
# 			subject['internal_marks'] = float(subject['internal_marks'])
# 		except:
# 			subject['internal_marks'] = 0

# 		total_marks += int(subject_data[subject['subject_id']])
# 		if subject['back_marks'] != None and subject['back_marks'] != 0:
# 			marks_obtained += float(subject['back_marks']) + float(subject['internal_marks'])
# 		else:
# 			marks_obtained += float(subject['external_marks']) + float(subject['internal_marks'])
# 	if total_marks != 0:
# 		percentage = round(float(marks_obtained) / float(total_marks) * 100, 2)
# 	data = {'marks_obtained': marks_obtained, 'total_marks': total_marks, 'percentage': percentage}
# 	return data

def get_external_marks(uniq_id, session_name):
	data = {}
	subject_data = {}
	marks_obtained = 0
	total_marks = 0
	percentage = 0

	StudentUniversityMarks = generate_session_table_name('StudentUniversityMarks_', session_name)
	studentSession = generate_session_table_name('studentSession_', session_name)
	SubjectInfo = generate_session_table_name('SubjectInfo_', session_name)

	get_subjects = []
	get_sem = list(studentSession.objects.filter(uniq_id=uniq_id).values_list('sem', flat=True))
	if len(get_sem) > 0:

		#### FOR SUBJECTS ####
		# if len(subjects) == 0:
		#     get_subjects = list(SubjectInfo.objects.filter(sem_id=get_sem[0]).exclude(status="DELETE").values_list('id', flat=True))
		# else:
		#     get_subjects = subjects

		get_subjects = list(SubjectInfo.objects.filter(sem_id=get_sem[0]).exclude(status="DELETE").values_list('id', flat=True))
		get_max_subject_marks = list(SubjectInfo.objects.filter(id__in=get_subjects).exclude(status="DELETE").values('id', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks'))
		for sub in get_max_subject_marks:
			max_external = 0
			for k, v in sub.items():
				if v != None and 'id' not in str(k):
					max_external += v
			subject_data[sub['id']] = max_external
		#######################

	get_marks = StudentUniversityMarks.objects.filter(uniq_id=uniq_id, subject_id__in=get_subjects).values('external_marks', 'internal_marks', 'back_marks', 'subject_id')
	for subject in get_marks:
		subject['back_marks'] = subject.get('back_marks', 0)
		subject['external_marks'] = subject.get('external_marks', 0)
		subject['internal_marks'] = subject.get('internal_marks', 0)
		try:
			subject['back_marks'] = float(subject['back_marks'])
		except:
			subject['back_marks'] = 0

		try:
			subject['external_marks'] = float(subject['external_marks'])
		except:
			subject['external_marks'] = 0

		try:
			subject['internal_marks'] = float(subject['internal_marks'])
		except:
			subject['internal_marks'] = 0

		total_marks += int(subject_data[subject['subject_id']])
		if subject['back_marks'] != None and subject['back_marks'] != 0:
			marks_obtained += float(subject['back_marks']) + float(subject['internal_marks'])
		else:
			marks_obtained += float(subject['external_marks']) + float(subject['internal_marks'])
	if total_marks != 0:
		percentage = round(float(marks_obtained) / float(total_marks) * 100, 2)
	data = {'marks_obtained': marks_obtained, 'total_marks': total_marks, 'percentage': percentage}
	return data


# def get_external_bonus(uniq_ids, sem_id, subjects, subrule, session_name):

#     data = {}
#     all_stu_data = []
#     return_data = []
#     type_id = subrule['type_id']

#     BonusMarks_External = generate_session_table_name('BonusMarks_External_', session_name)
#     studentSession = generate_session_table_name('studentSession_', session_name)

#     get_data = list(BonusMarks_External.objects.filter(id=type_id).exclude(status="DELETE").values('applicable_type', 'criteria', 'range_type', 'value'))

#     if len(get_data) > 0:
#         for stu in uniq_ids:
#             get_current_sem = studentSession.objects.filter(uniq_id=stu).values('sem_id', 'sem_id__sem', 'section_id', 'uniq_id__batch_from', 'uniq_id__batch_to')

#             if len(get_current_sem) > 0:
#                 session_data = get_batch_session_dropdown(str(get_current_sem[0]['uniq_id__batch_from']) + '-' + str(get_current_sem[0]['uniq_id__batch_to']), '1920o')

#                 if 'OVERALL' in str(get_data[0]['applicable_type']):
#                     current_session_data = session_data[:-1]
#                 elif 'PREVIOUS SEM' in str(get_data[0]['applicable_type']):
#                     current_session_data = session_data[-2:-1]
#                 elif 'PREVIOUS YEAR' in str(get_data[0]['applicable_type']):
#                     current_session_data = session_data[-3:-1]

#                 marks_obtained = 0
#                 total_marks = 0
#                 percentage = 0

#                 for session in current_session_data:
#                     new_session = str(session).split(' (')[0]
#                     external_marks = get_external_marks(stu, subjects, new_session)
#                     marks_obtained += external_marks['marks_obtained']
#                     total_marks += external_marks['total_marks']

#                 if total_marks != 0:
#                     percentage = round(float(marks_obtained) / float(total_marks) * 100, 2)
#                 data = {'uniq_id': stu, 'marks_obtained': marks_obtained, 'total_marks': total_marks, 'percentage': percentage, 'range_type': get_data[0]['range_type'], 'criteria': get_data[0]['criteria'], 'value': get_data[0]['value']}
#                 all_stu_data.append(data)

#                 ### FOR RETURN DATA ###
#                 # return_data.append({'uniq_id': stu, 'status': False})
#                 #######################
#         all_stu_data = sorted(all_stu_data, key=lambda i: i['percentage'])

#         value = int(get_data[0]['value'])
#         if 'STUDENT' in str(get_data[0]['criteria']):
#             if value >= len(all_stu_data):
#                 return_data = [r['uniq_id'] for r in all_stu_data]
#             else:
#                 if 'HIGH' in str(get_data[0]['range_type']):
#                     return_data = [r['uniq_id'] for r in all_stu_data[-int(value):]]
#                 else:
#                     difference = value - len(all_stu_data)
#                     return_data = [r['uniq_id'] for r in all_stu_data[:int(value)]]

#         else:
#             if 'HIGH' in str(get_data[0]['range_type']):
#                 return_data = [r['uniq_id'] for r in all_stu_data if float(r['percentage']) >= float(value)]
#             else:
#                 return_data = [r['uniq_id'] for r in all_stu_data if float(r['percentage']) <= float(value)]
#     return return_data

def get_external_bonus(uniq_ids, sem_ids, subrule, session_name):

	data = {}
	all_stu_data = []
	return_data = []
	final_return_data = []
	type_id = subrule['type_id']

	BonusMarks_External = generate_session_table_name('BonusMarks_External_', session_name)
	studentSession = generate_session_table_name('studentSession_', session_name)
	SubjectInfo = generate_session_table_name('SubjectInfo_', session_name)

	get_data = list(BonusMarks_External.objects.filter(id=type_id).exclude(status="DELETE").values('applicable_type', 'criteria', 'range_type', 'value'))

	if len(get_data) > 0:
		for sem in sem_ids:
			get_students = studentSession.objects.filter(sem_id=sem).values_list('uniq_id', flat=True)
			get_students = list(set(uniq_ids) & set(get_students))
			get_current_sem = studentSession.objects.filter(sem_id=sem).values('sem_id', 'sem_id__sem', 'section_id', 'uniq_id__batch_from', 'uniq_id__batch_to')
			if len(get_current_sem) > 0:
				session_data = get_batch_session_dropdown(str(get_current_sem[0]['uniq_id__batch_from']) + '-' + str(get_current_sem[0]['uniq_id__batch_to']), '1920o')

				if 'OVERALL' in str(get_data[0]['applicable_type']):
					current_session_data = session_data[:-1]
				elif 'PREVIOUS SEM' in str(get_data[0]['applicable_type']):
					current_session_data = session_data[-2:-1]
				elif 'PREVIOUS YEAR' in str(get_data[0]['applicable_type']):
					current_session_data = session_data[-3:-1]

			get_subjects = list(SubjectInfo.objects.filter(sem_id=sem).exclude(status="DELETE").values_list('id', flat=True))

			for stu in get_students:
				marks_obtained = 0
				total_marks = 0
				percentage = 0

				for session in current_session_data:
					new_session = str(session).split(' (')[0]
					external_marks = get_external_marks(stu, new_session)
					marks_obtained += external_marks['marks_obtained']
					total_marks += external_marks['total_marks']

				if total_marks != 0:
					percentage = round(float(marks_obtained) / float(total_marks) * 100, 2)
				data = {'uniq_id': stu, 'marks_obtained': marks_obtained, 'total_marks': total_marks, 'percentage': percentage, 'range_type': get_data[0]['range_type'], 'criteria': get_data[0]['criteria'], 'value': get_data[0]['value']}
				all_stu_data.append(data)

				### FOR RETURN DATA ###
				# return_data.append({'uniq_id': stu, 'status': False})
				#######################
			all_stu_data = sorted(all_stu_data, key=lambda i: i['percentage'])

			value = int(get_data[0]['value'])
			if 'STUDENT' in str(get_data[0]['criteria']):
				if value >= len(all_stu_data):
					return_data = [r['uniq_id'] for r in all_stu_data]
				else:
					if 'HIGH' in str(get_data[0]['range_type']):
						return_data = [r['uniq_id'] for r in all_stu_data[-int(value):]]
					else:
						difference = value - len(all_stu_data)
						return_data = [r['uniq_id'] for r in all_stu_data[:int(value)]]

			else:
				if 'HIGH' in str(get_data[0]['range_type']):
					return_data = [r['uniq_id'] for r in all_stu_data if float(r['percentage']) >= float(value)]
				else:
					return_data = [r['uniq_id'] for r in all_stu_data if float(r['percentage']) <= float(value)]

			final_return_data.extend(return_data)
	return final_return_data


# def get_bonusrule(session_name, session):

#     data = []
#     BonusMarks_Students = generate_session_table_name('BonusMarks_Students_', session_name)
#     BonusMarks_Subrule = generate_session_table_name("BonusMarks_Subrule_", session_name)
#     BonusMarks_Applicable_On = generate_session_table_name("BonusMarks_Applicable_On_", session_name)
#     BonusMarks_Rule = generate_session_table_name("BonusMarks_Rule_", session_name)
#     SubjectInfo = generate_session_table_name('SubjectInfo_', session_name)
#     studentSession = generate_session_table_name('studentSession_', session_name)

#     sort_by_again = ['rule_no', 'subrule_no']
#     temp_data = BonusMarks_Rule.objects.filter().exclude(status="DELETE").values('rule_no', 'app_id', 'app_id__sem_id', 'app_id__sem_id__sem', 'app_id__section', 'app_id__section__section', 'app_id__subject', 'subrule_no', 'subrule_id', 'subrule_id__type', 'subrule_id__type_id', 'subrule_id__name', 'bonus_marks', 'max_marks_limit', 'min_range', 'max_range').order_by('rule_no', 'subrule_no')

#     data = create_order_by_rule_no(temp_data, sort_by_again)
#     for rule in data:
#         rule['sem'] = set()
#         rule['section'] = set()
#         rule['subject'] = set()
#         rule['student'] = set()
#         get_details = BonusMarks_Rule.objects.filter(rule_no=rule['rule']).exclude(status="DELETE").values('app_id__sem_id', 'app_id__sem_id__sem', 'app_id__subject', 'app_id__section', 'app_id__subject').distinct()
#         if len(get_details) > 0:
#             for detail in get_details:
#                 rule['sem'].add(detail['app_id__sem_id'])
#                 rule['section'].add(detail['app_id__section'])
#                 rule['subject'].add(detail['app_id__subject'])

#             get_student = list(BonusMarks_Students.objects.filter(rule_id__rule_no=rule['rule']).exclude(status="DELETE").exclude(rule_id__status="DELETE").values_list('uniq_id', flat=True).distinct())
#             rule['student'] = get_student
#         rule['sem'] = list(rule['sem'])
#         rule['section'] = list(rule['section'])
#         rule['subject'] = list(rule['subject'])
#         rule['student'] = list(rule['student'])
#     return data
def get_bonusrule(sem_id, session_name, session):

	data = []
	BonusMarks_Students = generate_session_table_name('BonusMarks_Students_', session_name)
	BonusMarks_Subrule = generate_session_table_name("BonusMarks_Subrule_", session_name)
	BonusMarks_Applicable_On = generate_session_table_name("BonusMarks_Applicable_On_", session_name)
	BonusMarks_Rule = generate_session_table_name("BonusMarks_Rule_", session_name)
	SubjectInfo = generate_session_table_name('SubjectInfo_', session_name)
	studentSession = generate_session_table_name('studentSession_', session_name)

	sort_by_again = ['rule_no', 'subrule_no']
	temp_data = BonusMarks_Rule.objects.filter(app_id__sem_id__in=sem_id).exclude(status="DELETE").values('rule_no', 'app_id', 'app_id__sem_id', 'app_id__sem_id__sem', 'app_id__section', 'app_id__section__section', 'app_id__subject', 'subrule_no', 'subrule_id', 'subrule_id__type', 'subrule_id__type_id', 'subrule_id__name', 'bonus_marks', 'max_marks_limit', 'min_range', 'max_range').order_by('rule_no', 'subrule_no')
	data = create_order_by_rule_no(temp_data, sort_by_again)
	for rule in data:
		rule['sem'] = set()
		rule['section'] = set()
		rule['subject'] = set()
		rule['student'] = set()
		get_details = BonusMarks_Rule.objects.filter(rule_no=rule['rule'], app_id__sem_id__in=sem_id).exclude(status="DELETE").values('app_id__sem_id', 'app_id__sem_id__sem', 'app_id__subject', 'app_id__section', 'app_id__subject').distinct()
		if len(get_details) > 0:
			for detail in get_details:
				rule['sem'].add(detail['app_id__sem_id'])
				rule['section'].add(detail['app_id__section'])
				rule['subject'].add(detail['app_id__subject'])

			get_student = list(BonusMarks_Students.objects.filter(rule_id__rule_no=rule['rule'], rule_id__app_id__sem_id__in=sem_id, uniq_id__sem__in=sem_id).exclude(status="DELETE").exclude(rule_id__status="DELETE").values_list('uniq_id', flat=True).distinct())
			rule['student'] = get_student
		rule['sem'] = list(rule['sem'])
		rule['section'] = list(rule['section'])
		rule['subject'] = list(rule['subject'])
		rule['student'] = list(rule['student'])
	return data


def bonus_marks_rule_wise(sem_id, session_name, session):

	data = {}
	application_data = {}
	studentSession = generate_session_table_name('studentSession_', session_name)
	SubjectInfo = generate_session_table_name('SubjectInfo_', session_name)
	BonusMarks_AttendanceAtt_type = generate_session_table_name('BonusMarks_AttendanceAtt_type_', session_name)
	BonusMarks_Attendance = generate_session_table_name('BonusMarks_Attendance_', session_name)
	BonusMarks_InternalExam = generate_session_table_name('BonusMarks_InternalExam_', session_name)
	BonusMarks_Internal = generate_session_table_name('BonusMarks_Internal_', session_name)
	BonusMarks_Rule = generate_session_table_name('BonusMarks_Rule_', session_name)
	BonusMarks = generate_session_table_name('BonusMarks_', session_name)

	get_rule_data = get_bonusrule(sem_id, session_name, session)
	total_bonus_get = {}
	for rule_no, rule in enumerate(get_rule_data):
		ext_check = 1
		get_external_data = []

		for stu in rule['student']:
			get_sem_id = studentSession.objects.filter(uniq_id=stu).values('sem_id', 'section_id')

			### RULE STUDENTS BONUS ###
			if stu not in total_bonus_get:
				total_bonus_get[stu] = {}
			###########################
			if len(get_sem_id) > 0:

				for sub in rule['subject']:
					#### GET INTERNAL MARKS ####
					sub_detail = SubjectInfo.objects.filter(id=sub, sem_id=get_sem_id[0]['sem_id'], session=session).exclude(status="DELETE").values('max_ct_marks', 'max_att_marks', 'max_ta_marks', 'subject_type', 'id', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'subject_type', 'subject_type__value')
					get_internal_marks = get_single_student_internal_marks(stu, get_sem_id[0]['sem_id'], sub_detail, session_name)
					internal_marks = float(get_internal_marks['avg_marks_obt'])
					max_internal_marks = get_internal_marks['avg_total_marks']
					if internal_marks == None:
						internal_marks = 0
					############################

					### RULE STUDENT BONUS ###
					if sub not in total_bonus_get[stu]:
						total_bonus_get[stu][sub] = 0
					else:
						internal_marks += float(total_bonus_get[stu][sub])
					# get_marks = BonusMarks.objects.filter(uniq_id=stu, rule_id__app_id__subject=sub).exclude(status="DELETE").exclude(rule_id__status="DELETE").aggregate(bonus_marks=Sum('total_bonus_marks'))
					# print(get_marks, 'get_marks')
					# if len(get_marks) > 0:
					#     if sub not in total_bonus_get[stu]:
					#         total_bonus_get[stu][sub] = 0

					#     elif get_marks['bonus_marks'] != None:
					#         total_bonus_get[stu][sub] += float(get_marks['bonus_marks'])
					##########################

					##################################
					max_subrule_marks = 0
					max_bonus_ids = set()
					for subrule_no, subrule in enumerate(rule['rule_data_set']):
						subrule_ids = set()
						flag = 1  # 1 for satisfying all criteria
						for criteria in subrule['criteria_data']:

							if 'EXTERNAL' in criteria['type'] and flag == 1:
								if ext_check == 1:
									get_external_data = get_external_bonus(rule['student'], rule['sem'],  criteria, session_name)
									ext_check = 0
								if stu not in get_external_data:
									flag = 0
								else:
									get_rule_id = BonusMarks_Rule.objects.filter(app_id__sem_id=get_sem_id[0]['sem_id'], app_id__section=get_sem_id[0]['section_id'], app_id__subject=sub, rule_no=int(rule['rule']), subrule_no=int(subrule['subrule_no']), subrule_id__type=criteria['type'], subrule_id__type_id=criteria['type_id']).exclude(status="DELETE").exclude(app_id__status="DELETE").values_list('id', flat=True)
									if len(get_rule_id) > 0:
										subrule_ids.add(get_rule_id[0])
								#############################################

							elif 'INTERNAL' in criteria['type'] and flag == 1:
								exam_ids = BonusMarks_InternalExam.objects.filter(internal_id=criteria['type_id']).exclude(internal_id__status="DELETE").values_list('exam_id', flat=True)
								get_range = BonusMarks_Internal.objects.filter(id=criteria['type_id']).exclude(status="DELETE").values('min_range', 'max_range')
								percentage = 0
								# get_internal_data = get_student_per_ct_marks([stu], exam_ids, [sub], session_name)
								# total_data = get_single_student_internal_marks(stu, get_sem_id[0]['sem_id'], [sub], session_name)
								# print(total_data, 'total_data')
								# get_internal_data = get_student_total_ct_marks_v([stu], get_sem_id[0]['sem_id'], [sub], session_name, exam_ids)
								# if len(get_internal_data) > 0:
								#     if len(get_internal_data[0]['sub_details']) > 0:
								#         if len(get_internal_data[0]['sub_details'][0]['selected_internal']) > 0:

								#             # int_flag = 1 ### true if exam range is satisfying
								#             percentage = 0
								#             marks_obtained = 0
								#             out_of = 0

								#             try:
								#                 out_of = float(get_internal_data[0]['sub_details'][0]['selected_internal']['out_of'])
								#                 marks_obtained = float(get_internal_data[0]['sub_details'][0]['selected_internal']['marks_obtained'])
								#             except:
								#                 pass
								#             #### UPDATE INTERNAL MARKS FOR BONUS ####
								#             if stu in total_bonus_get:
								#                 if sub in total_bonus_get[stu]:
								#                     marks_obtained += float(total_bonus_get[stu][sub])
								#             #########################################

								#             if float(out_of) != 0:
								#                 percentage = round(float(marks_obtained / out_of) * 100, 2)

								#             if float(percentage) < float(get_range[0]['min_range']) or float(percentage) > float(get_range[0]['max_range']):
								#                 flag = 0
								if float(max_internal_marks) > 0:
									marks_obtained = float(internal_marks)

									### UPDATE INTERNAL MARKS FOR BONUS ####
									# if stu in total_bonus_get:
									# 	if sub in total_bonus_get[stu]:
									# 		marks_obtained += float(total_bonus_get[stu][sub])
									#########################################

									percentage = round(float(marks_obtained / max_internal_marks) * 100, 2)
									if float(percentage) < float(get_range[0]['min_range']) or float(percentage) > float(get_range[0]['max_range']):
										flag = 0
									if flag != 0:
										get_rule_id = BonusMarks_Rule.objects.filter(app_id__sem_id=get_sem_id[0]['sem_id'], app_id__section=get_sem_id[0]['section_id'], app_id__subject=sub, rule_no=int(rule['rule']), subrule_no=int(subrule['subrule_no']), subrule_id__type=criteria['type'], subrule_id__type_id=criteria['type_id']).exclude(status="DELETE").exclude(app_id__status="DELETE").values_list('id', flat=True)
										if len(get_rule_id) > 0:
											subrule_ids.add(get_rule_id[0])
								#############################################

							elif 'ATTENDANCE' in criteria['type'] and flag == 1:
								att_type_li = BonusMarks_AttendanceAtt_type.objects.filter(att_id=criteria['type_id']).exclude(att_id__status="DELETE").values_list('att_type', flat=True)
								get_range = BonusMarks_Attendance.objects.filter(id=criteria['type_id']).exclude(status="DELETE").values('min_range', 'max_range')
								get_attendance_data = get_student_attendance_subjectwise([stu], att_type_li, [sub], session_name, session)
								if len(get_attendance_data) > 0:
									if float(get_attendance_data[0]['percent']) >= float(get_range[0]['min_range']) and float(get_attendance_data[0]['percent']) <= get_range[0]['max_range']:
										get_rule_id = BonusMarks_Rule.objects.filter(app_id__sem_id=get_sem_id[0]['sem_id'], app_id__section=get_sem_id[0]['section_id'], app_id__subject=sub, rule_no=int(rule['rule']), subrule_no=int(subrule_no) + 1, subrule_id__type=criteria['type'], subrule_id__type_id=criteria['type_id']).exclude(status="DELETE").exclude(app_id__status="DELETE").values_list('id', flat=True)
										if len(get_rule_id) > 0:
											subrule_ids.add(get_rule_id[0])
											#############################################
									else:
										flag = 0

						if flag != 0 and len(subrule_ids) > 0:
							if float(subrule['min_range']) <= float(total_bonus_get[stu][sub]) and float(subrule['max_range']) >= float(total_bonus_get[stu][sub]):
								### CHECK FOR MAX-INTERNAL LIMIT ###
								if float(max_internal_marks) < float(subrule['max_marks_limit']):
									max_marks_limit = float(max_internal_marks)
								else:
									max_marks_limit = float(subrule['max_marks_limit'])
								internal_difference = float(max_marks_limit) - float(internal_marks)
								if float(internal_difference) > 0 and internal_difference > float(subrule['bonus_marks']):
									bonus_marks = subrule['bonus_marks']
								elif float(internal_difference) > 0:
									bonus_marks = float(internal_difference)
								else:
									bonus_marks = 0
								if float(max_subrule_marks) < float(bonus_marks):
									max_subrule_marks = float(bonus_marks)
									max_bonus_ids = max_bonus_ids.union(subrule_ids)
					####################################
					### UPDATE RULE BONUS ###
					if stu in total_bonus_get:
						if sub in total_bonus_get[stu]:
							total_bonus_get[stu][sub] = float(total_bonus_get[stu][sub]) + float(max_subrule_marks)
					#########################

					### APPEND THE DATA IN FORMAT ###
					if stu in application_data:
						if 'rule_' + str(rule['rule']) in application_data[stu]:
							if sub in application_data[stu]['rule_' + str(rule['rule'])]:
								application_data[stu]['rule_' + str(rule['rule'])][sub]['ids'] = application_data[stu]['rule_' + str(rule['rule'])][sub]['ids'].union(max_bonus_ids)
								application_data[stu]['rule_' + str(rule['rule'])][sub]['bonus_marks'] = max_subrule_marks
							else:
								application_data[stu]['rule_' + str(rule['rule'])][sub] = {'ids': set(), 'bonus_marks': max_subrule_marks}
								application_data[stu]['rule_' + str(rule['rule'])][sub]['ids'] = application_data[stu]['rule_' + str(rule['rule'])][sub]['ids'].union(max_bonus_ids)
						else:
							application_data[stu]['rule_' + str(rule['rule'])] = {}
							application_data[stu]['rule_' + str(rule['rule'])][sub] = {'ids': set(), 'bonus_marks': max_subrule_marks}
							application_data[stu]['rule_' + str(rule['rule'])][sub]['ids'] = application_data[stu]['rule_' + str(rule['rule'])][sub]['ids'].union(max_bonus_ids)
					else:
						application_data[stu] = {}
						application_data[stu]['rule_' + str(rule['rule'])] = {}
						application_data[stu]['rule_' + str(rule['rule'])][sub] = {}
						application_data[stu]['rule_' + str(rule['rule'])][sub] = {'ids': set(), 'bonus_marks': max_subrule_marks}
						application_data[stu]['rule_' + str(rule['rule'])][sub]['ids'] = application_data[stu]['rule_' + str(rule['rule'])][sub]['ids'].union(max_bonus_ids)
					#################################
	return application_data


def get_ctrule_wise_student_marks(uniq_id, sem_id, subject_type, session_name,subject_id_list=[]): #added parametr of subjecT_id_list 
	studentSession = generate_session_table_name("studentSession_", session_name)
	CTMarksRules = generate_session_table_name("CTMarksRules_", session_name)
	CTMarks_GroupInfo = generate_session_table_name('CTMarks_GroupInfo_', session_name)
	CTMarks_Group_ExamInfo = generate_session_table_name('CTMarks_Group_ExamInfo_', session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

	qry_ct_rule = CTMarks_Group_ExamInfo.objects.filter(group_id__rule_id__subject_type__in=subject_type, group_id__rule_id__sem=sem_id).exclude(status='DELETE').exclude(group_id__rule_id__status="DELETE").exclude(group_id__status="DELETE").values('group_id__id', 'group_id__rule_id', 'group_id__rule_id__rule_criteria', 'group_id__weightage', 'group_id__ct_to_select', 'exam_id', 'exam_id__value').annotate(rule_no=F('group_id__rule_id__rule_no'), group_no=F('group_id__group')).order_by('group_id__rule_id__rule_no', 'group_id__group')
	sort_by_again = ['rule_no', 'group']
	ct_rule = create_order_by_rule_no(qry_ct_rule, sort_by_again)

	total = {}

	if (len(subject_id_list)!=0):
		subject_details = list(SubjectInfo.objects.exclude(status="DELETE").filter(sem=sem_id, subject_type__in=subject_type,id__in=subject_id_list).values('max_ct_marks', 'max_ta_marks', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'id', 'max_att_marks', 'subject_type', 'sem').annotate(ids=F('id')))
	else:
		subject_details = list(SubjectInfo.objects.exclude(status="DELETE").filter(sem=sem_id, subject_type__in=subject_type).values('max_ct_marks', 'max_ta_marks', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'id', 'max_att_marks', 'subject_type', 'sem').annotate(ids=F('id')))

	data = {'subjects': [], 'subject_data': [], 'details': {}}
	subject_data = []
	for subject in subject_details:
		sub_data = {'rule_data': {}}

		total_ct_actual = {}
		internal_marks = 0
		for rule_no, rule in enumerate(ct_rule):

			sub_data['subject_id'] = subject['id']
			sub_data['rule_data']['rule_' + str(int(rule_no) + 1)] = {}
			sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['total_ct_converted'] = {}
			sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['max_ct_marks'] = {}
			total_ct_actual = {}
			internal_marks = 0
			for group_no, group in enumerate(rule['rule_data_set']):
				grp_marks = 0
				marks = get_max_ctmarks_group(uniq_id, group['group_data_set'], sem_id, subject['id'], group['group_id__ct_to_select'], session_name, group['group_id__weightage'], subject['max_ct_marks'])
				data['details']['uniq_id'] = uniq_id
				data['details']['semester'] = sem_id
				data['details']['subject_type'] = subject_type

				for mark in marks['selected_ct']:
					if not isinstance(mark['internal_marks'], str):
						internal_marks += mark['internal_marks']
						grp_marks += mark['internal_marks']

				for mark in marks['all_group_ct']:
					marks = mark['internal_marks']
					if marks == 0:
						marks = mark['status']
						if 'P' in str(mark['status']):
							marks = 'N/A'
					sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['total_ct_converted'][str(mark['exam_id'])] = marks
					sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['max_ct_marks'][str(mark['exam_id'])] = mark['converted_total_marks']
					total_ct_actual[str(mark['exam_id'])] = mark['marks_obtained']

				sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['rule_id'] = group['group_id__rule_id']
				sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['group_' + str(int(group_no) + 1)] = {}
				sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['group_' + str(int(group_no) + 1)]['marks'] = grp_marks
				sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['group_' + str(int(group_no) + 1)]['weightage'] = group['group_id__weightage']

			sub_data['rule_data']['rule_' + str(int(rule_no) + 1)]['total_rule_marks'] = internal_marks

		sub_data['internal'] = internal_marks
		sub_data['total_ct_actual'] = total_ct_actual
		data['subject_data'].append(sub_data)
		data['subjects'].append(subject['id'])

	return data


def get_student_per_ct_marks(uniq_id, exam_list, subjects, session_name):
	ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	CTMarksRules = generate_session_table_name("CTMarksRules_", session_name)
	Store_Ctmarks_RuleWise = generate_session_table_name("Store_Ctmarks_RuleWise_", session_name)

	response = []
	criteria = None
	for each in uniq_id:
		stu_dict = {'uniq_id': each, 'sub_details': []}
		for subject_id in subjects:
			sub_name = list(SubjectInfo.objects.filter(id=subject_id).values_list('sub_name', flat=True))[0]
			new_dict = {'subject_id': subject_id, 'subject_name': sub_name, 'marks_info': []}
			stu_dict['sub_details'].append(new_dict)
			rules = Store_Ctmarks_RuleWise.objects.filter(uniq_id=each, exam_id__in=exam_list, subject=subject_id).values_list('rule_id', flat=True).distinct()
			if len(rules) > 0:
				for rule in rules:
					fetch = Store_Ctmarks_RuleWise.objects.filter(rule_id=rule, uniq_id=each, exam_id__in=exam_list, subject=subject_id).aggregate(total=Sum('ct_marks_obtained'), max_marks=Sum('ct_marks_total'))
					marks = {'rule_id': rule, 'marks_obtained': fetch['total'], 'out_of': fetch['max_marks']}
					new_dict['marks_info'].append(marks)

				criteria = CTMarksRules.objects.filter(id=rules[0]).values_list('rule_criteria', flat=True)
				if len(criteria) > 0:
					criteria = criteria[0]
					data = fetch_internals(new_dict['marks_info'], criteria)
					new_dict['marks_info'] = []
					for exam in exam_list:
						fetch_marks = list(Store_Ctmarks_RuleWise.objects.filter(rule_id=data['rule_id'], uniq_id=each, exam_id=exam, subject=subject_id).values('ct_marks_obtained', 'ct_marks_total'))
						if fetch_marks:
							mark_dict = {'exam_id': exam, 'marks_obtained': fetch_marks[0]['ct_marks_obtained'], 'out_of': fetch_marks[0]['ct_marks_total']}
						else:
							mark_dict = {'exam_id': exam, 'marks_obtained': 'NA', 'out_of': 'NA'}

						new_dict['marks_info'].append(mark_dict)
		response.append(stu_dict)
	return response


# def get_student_total_ct_marks(uniq_id, sem_id, subjects, session_name):
#     # uniq_id and subject ids are in list
#     response = []
#     criteria = None
#     ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
#     SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
#     studentSession = generate_session_table_name("studentSession_", session_name)
#     CTMarksRules = generate_session_table_name("CTMarksRules_", session_name)
#     Store_Ctmarks_RuleWise = generate_session_table_name("Store_Ctmarks_RuleWise_", session_name)

#     ct_conducted = ExamSchedule.objects.filter(sem=sem_id).distinct().values_list('exam_id', flat=True)
#     for each in uniq_id:
#         stu_dict = {'uniq_id': each, 'sub_details': []}
#         for subject_id in subjects:
#             sub_name = list(SubjectInfo.objects.filter(id=subject_id).values_list('sub_name', flat=True))[0]
#             new_dict = {'subject_id': subject_id, 'subject_name': sub_name, 'marks_info': []}
#             new_dict['selected_internal'] = {'rule_id': 0, 'marks_obtained': 0.0, 'out_of': 0.0}
#             stu_dict['sub_details'].append(new_dict)
#             rules = Store_Ctmarks_RuleWise.objects.filter(uniq_id=each,  subject=subject_id).values_list('rule_id', flat=True).distinct()
#             if len(rules) > 0:
#                 for rule in rules:
#                     fetch = Store_Ctmarks_RuleWise.objects.filter(rule_id=rule, uniq_id=each, subject=subject_id).aggregate(total=Sum('ct_marks_obtained'), max_marks=Sum('ct_marks_total'))
#                     marks = {'rule_id': rule, 'marks_obtained': fetch['total'], 'out_of': fetch['max_marks']}
#                     new_dict['marks_info'].append(marks)

#                 criteria = CTMarksRules.objects.filter(id=rules[0]).values_list('rule_criteria', flat=True)
#                 if len(criteria) > 0:
#                     criteria = criteria[0]
#                     data = fetch_internals(new_dict['marks_info'], criteria)
#                     new_dict['selected_internal'] = data
#         response.append(stu_dict)

#     return response
def get_student_total_ct_marks(uniq_id, sem_id, subjects, session_name):
	# uniq_id and subject ids are in list
	response = []
	criteria = None
	ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	CTMarksRules = generate_session_table_name("CTMarksRules_", session_name)
	Store_Ctmarks_RuleWise = generate_session_table_name("Store_Ctmarks_RuleWise_", session_name)
	CTMarks_GroupInfo = generate_session_table_name('CTMarks_GroupInfo_', session_name)
	CTMarks_Group_ExamInfo = generate_session_table_name('CTMarks_Group_ExamInfo_', session_name)

	ct_conducted = ExamSchedule.objects.filter(sem=sem_id).distinct().values_list('exam_id', flat=True)
	for each in uniq_id:
		stu_dict = {'uniq_id': each, 'sub_details': []}
		for subject_id in subjects:
			sub_name = list(SubjectInfo.objects.filter(id=subject_id).values_list('sub_name', flat=True))[0]
			new_dict = {'subject_id': subject_id, 'subject_name': sub_name, 'marks_info': []}
			new_dict['selected_internal'] = {'rule_id': 0, 'marks_obtained': 0.0, 'out_of': 0.0}
			stu_dict['sub_details'].append(new_dict)
			rules = Store_Ctmarks_RuleWise.objects.filter(uniq_id=each,  subject=subject_id).values_list('rule_id', flat=True).distinct()
			if len(rules) > 0:
				for rule in rules:
					get_distinct_group_id = CTMarks_Group_ExamInfo.objects.filter(group_id__rule_id=rule).exclude(status="DELETE").values('group_id', 'exam_id', 'group_id__ct_to_select').distinct().order_by('group_id')
					exam_data_final = []
					for k, exam_data in groupby(get_distinct_group_id, key=lambda x: x['group_id']):
						exam = {'exam_id': [], 'ct_to_select': 0}
						for v in exam_data:
							exam['ct_to_select'] = int(v['group_id__ct_to_select'])
							exam['exam_id'].append(v['exam_id'])
						exam_data_final.append(exam)

					all_fetch = []
					for marks in exam_data_final:
						fetch = Store_Ctmarks_RuleWise.objects.filter(rule_id=rule, uniq_id=each, subject=subject_id, exam_id__in=marks['exam_id']).exclude(status="DELETE").values('ct_marks_obtained', 'ct_marks_total')
						for f in fetch:
							try:
								f['ct_marks_obtained'] = float(f['ct_marks_obtained'])
							except:
								f['ct_marks_obtained'] = 0
						all_fetch.extend(sorted(fetch, key=lambda i: i['ct_marks_obtained'], reverse=True)[:int(marks['ct_to_select'])])
					total = 0
					max_marks = 0
					for all_f in all_fetch:
						total += float(all_f['ct_marks_obtained'])
						max_marks += float(all_f['ct_marks_total'])
					marks = {'rule_id': rule, 'marks_obtained': total, 'out_of': total}
					new_dict['marks_info'].append(marks)

				criteria = CTMarksRules.objects.filter(id=rules[0]).values_list('rule_criteria', flat=True)
				if len(criteria) > 0:
					criteria = criteria[0]
					data = fetch_internals(new_dict['marks_info'], criteria)
					new_dict['selected_internal'] = data
		response.append(stu_dict)

	return response


def get_student_total_ct_marks_v(uniq_id, sem_id, subjects, session_name, extra_filter):
	# uniq_id and subject ids are in list
	response = []
	criteria = None
	extra_filter = {'exam_id__in': extra_filter}
	ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	studentSession = generate_session_table_name("studentSession_", session_name)
	CTMarksRules = generate_session_table_name("CTMarksRules_", session_name)
	Store_Ctmarks_RuleWise = generate_session_table_name("Store_Ctmarks_RuleWise_", session_name)
	CTMarks_Group_ExamInfo = generate_session_table_name('CTMarks_Group_ExamInfo_', session_name)

	ct_conducted = ExamSchedule.objects.filter(sem=sem_id).distinct().values_list('exam_id', flat=True)
	for each in uniq_id:
		stu_dict = {'uniq_id': each, 'sub_details': []}
		for subject_id in subjects:
			sub_name = list(SubjectInfo.objects.filter(id=subject_id).values_list('sub_name', flat=True))[0]
			new_dict = {'subject_id': subject_id, 'subject_name': sub_name, 'marks_info': []}
			new_dict['selected_internal'] = {'rule_id': 0, 'marks_obtained': 0.0, 'out_of': 0.0}
			stu_dict['sub_details'].append(new_dict)
			rules = Store_Ctmarks_RuleWise.objects.filter(uniq_id=each,  subject=subject_id).values_list('rule_id', flat=True).distinct()
			if len(rules) > 0:
				final_dict = []
				for rule in rules:
					rule_dict = []
					total = 0
					marks_obtained = 0
					get_exam_group_wise = CTMarks_Group_ExamInfo.objects.filter(group_id__rule_id=rule).filter(**extra_filter).exclude(status="DELETE").values('exam_id', 'group_id', 'group_id__ct_to_select', 'group_id__group').order_by('group_id__group')
					for group_no, (group, group_data) in enumerate(groupby(get_exam_group_wise, key=lambda rule: rule['group_id__group'])):
						temp_dict = []
						exam_ids = []
						ct_to_select = 0
						flag = 0
						for g in group_data:
							if flag == 0:
								ct_to_select = g['group_id__ct_to_select']
								flag = 1
							exam_ids.append(g['exam_id'])
						for exam in exam_ids:
							fetch = Store_Ctmarks_RuleWise.objects.filter(rule_id=rule, uniq_id=each, subject=subject_id, exam_id=exam).aggregate(total=Sum('ct_marks_obtained'), max_marks=Sum('ct_marks_total'))
							marks = {'rule_id': rule, 'marks_obtained': fetch['total'], 'out_of': fetch['max_marks']}
							new_dict['marks_info'].append(marks)
							temp_dict.append(marks)
						if len(temp_dict) > 0:
							rule_dict.extend(sorted(temp_dict, key=lambda i: i['marks_obtained'], reverse=True)[:int(ct_to_select)])
					for r in rule_dict:
						marks_obtained += float(r['marks_obtained'])
						total += float(r['out_of'])
					final_dict.append({'rule_id': rule, 'marks_obtained': marks_obtained, 'out_of': total})

				criteria = CTMarksRules.objects.filter(id=rules[0]).values_list('rule_criteria', flat=True)
				if len(criteria) > 0:
					criteria = criteria[0]
					data = fetch_internals(final_dict, criteria)
					new_dict['selected_internal'] = data
		response.append(stu_dict)

	return response


def get_single_student_internal_marks(uniq_id, sem_id, subject, session_name):

	### STUDENT INTERNAL MARKS ALL SUBJECT ###
	data = []
	final_data = {}
	overall_total = 0
	overall_obtained = 0

	for sub in subject:
		sub_name = sub['sub_name'] + ' (' + sub['sub_alpha_code'] + '-' + sub['sub_num_code'] + ')'
		total_marks = 0
		max_internal_marks = 0
		total_ct_marks = 0
		max_ct_marks = sub.get('max_ct_marks', 0)
		max_att_marks = sub.get('max_att_marks', 0)
		max_ta_marks = sub.get('max_ta_marks', 0)

		total_ct_marks = 0
		max_internal_marks = max_ct_marks + max_att_marks + max_ta_marks
		if 'THEORY' in sub['subject_type__value'] or 'ELECTIVE' in sub['subject_type__value']:
			ct_marks = get_student_total_ct_marks([uniq_id], sem_id, [sub['id']], session_name)
			if len(ct_marks) > 0:
				if len(ct_marks[0]['sub_details']) > 0:
					total_ct_marks = ct_marks[0]['sub_details'][0]['selected_internal']['marks_obtained']

		att_marks_data = get_student_subject_att_marks_new([uniq_id], session_name, sub['subject_type'], sem_id, sub['max_att_marks'])
		att_marks = {'att_marks': 'N/A', 'att_per': 0}
		if uniq_id in att_marks_data:
			if sub['id'] in att_marks_data[uniq_id]:
				att_marks = att_marks_data[uniq_id][sub['id']]

		subject_att_marks = att_marks['att_marks']
		subject_att_per = att_marks['att_per']
		ta_marks = get_student_subject_ta_marks(uniq_id, session_name, sub['id'])
		if ta_marks != 'N/A':
			ta_marks = math.ceil(float(ta_marks))

		total_marks += float(total_ct_marks)

		if not isinstance(subject_att_marks, str):
			total_marks += subject_att_marks

		if not isinstance(ta_marks, str):
			total_marks += ta_marks

		overall_total += max_internal_marks
		overall_obtained += total_marks
		data.append({'uniq_id': uniq_id, 'converted_marks': total_ct_marks, 'ta_marks': ta_marks, 'attendance_marks': subject_att_marks, 'att_per': subject_att_per, 'rule_data': [], 'subject_name': sub_name, 'subject_id': sub['id'], 'total_marks': max_internal_marks, 'marks_obtained': total_marks})
	final_data = {'data': data, 'avg_marks_obt': overall_obtained, 'avg_total_marks': overall_total}
	return final_data


def fetch_internals(mark_list, criteria):
	data = {}
	data = {'rule_id': 0, 'marks_obtained': 0.0, 'out_of': 0.0}

	if len(mark_list) >= 1:
		max_value = mark_list[0]

	if criteria == 'MAXIMUM':
		max_marks = 0
		for each in mark_list:
			total = each['marks_obtained']
			if (max_marks < total):
				max_marks = total
				max_value = each
		data = max_value

	elif criteria == 'AVERAGE':
		total = 0
		average = 0
		rule_list = []
		final_list = []
		for each in mark_list:
			rule_list.append(each['rule_id'])
			total = total + each['marks_obtained']
		if len(mark_list) > 0:
			average = total / len(mark_list)
		new_dict = {'rule_id': rule_list, 'marks_obtained': average}
		data = new_dict

	return data


def get_student_marks_updated(uniq_id, session_name, subject_id, exam_name, max_ct_marks, weightage, sem_id):
	StudentMarks = generate_session_table_name("StudentMarks_", session_name)
	QuesPaperApplicableOn = generate_session_table_name('QuesPaperApplicableOn_', session_name)
	QuesPaperSectionDetails = generate_session_table_name('QuesPaperSectionDetails_', session_name)
	marks_obtained = None
	max_marks = 0

	format_id = list(QuesPaperApplicableOn.objects.filter(ques_paper_id__exam_id=exam_name, sem=sem_id).values('ques_paper_id').order_by('-id')[:1])

	if len(format_id) > 0:
		max_marks = QuesPaperSectionDetails.objects.filter(ques_paper_id=format_id[0]['ques_paper_id']).aggregate(total_marks=Sum('max_marks'))
		total_exam_marks = max_marks.get('total_marks', 0)

	else:
		total_exam_marks = 0

	max_marks = (max_ct_marks * weightage) / 100

	query = StudentMarks.objects.exclude(status='DELETE').exclude(marks_id__status='DELETE').filter(uniq_id=uniq_id, marks_id__subject_id=subject_id, marks_id__exam_id=exam_name).aggregate(marks_obtained=Sum('marks'))
	marks_obtained = query.get('marks_obtained', 0)

	status = 'N/A'
	if marks_obtained is None:

		query2 = list(StudentMarks.objects.exclude(status='DELETE').exclude(marks_id__status='DELETE').filter(uniq_id=uniq_id, marks_id__subject_id=subject_id, marks_id__exam_id=exam_name).values('present_status'))

		if query2:
			marks_obtained = query2[0]['present_status']
			status = str(marks_obtained)
			if marks_obtained == 'P':
				marks_obtained = 0

		else:
			marks_obtained = 'NA'

	converted_student_marks = marks_obtained

	if not isinstance(marks_obtained, str):

		if total_exam_marks != 0:
			if (math.ceil((marks_obtained * max_marks) / total_exam_marks) > max_marks):
				converted_student_marks = max_marks
			else:
				converted_student_marks = math.ceil((marks_obtained * max_marks) / total_exam_marks)

		else:
			converted_student_marks = 0

	response = {'marks_obtained': marks_obtained, 'converted_marks': converted_student_marks, 'total_marks': total_exam_marks, 'converted_total_marks': max_marks, 'status': status}
	return (response)


def check_ct_status(uniq_id, ct_list, sem, subject_id, session_name):

	StudentMarks = generate_session_table_name("StudentMarks_", session_name)
	present_status = []
	for exam_name in ct_list:
		query2 = list(StudentMarks.objects.exclude(status='DELETE').exclude(marks_id__status='DELETE').filter(uniq_id=uniq_id, marks_id__subject_id=subject_id, marks_id__exam_id=exam_name).values('present_status'))

		exam_value = StudentAcademicsDropdown.objects.filter(sno=exam_name).values_list('value', flat=True)[0]

		new_dict = {'exam_name': exam_value, 'exam_id': exam_name, 'present_status': False}

		if len(query2) > 0:
			if query2[0]['present_status'] == 'P':
				new_dict['present_status'] = True

		present_status.append(new_dict)

	return(present_status)


def get_max_ctmarks_group(uniq_id, ct_list, sem, subject, to_select, session_name, weightage, max_ct_marks):

	StudentMarks = generate_session_table_name("StudentMarks_", session_name)
	ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)

	ct_conducted = ExamSchedule.objects.filter(sem=sem).distinct().values_list('exam_id', flat=True)

	subject_data = []
	individual_sub_data = {}
	exam_list = []

	for exam in ct_list:

		marks = get_student_marks_updated(uniq_id, session_name, subject, exam, max_ct_marks, weightage, sem)
		if isinstance(marks['converted_marks'], str):
			marks['converted_marks'] = 0

		if isinstance(marks['marks_obtained'], str):
			marks['marks_obtained'] = 0

		if isinstance(marks['converted_total_marks'], str):
			marks['converted_total_marks'] = 0

		exam_value = StudentAcademicsDropdown.objects.filter(sno=exam).values_list('value', flat=True)[0]
		new_dict = {'exam_name': exam_value, 'exam_id': exam, 'internal_marks': marks['converted_marks'], 'converted_total_marks': marks['converted_total_marks'], 'marks_obtained': marks['marks_obtained'], 'total_marks': marks['total_marks'], 'id': subject, 'status': marks['status']}
		exam_list.append(new_dict)
	new_list = sorted(exam_list, key=lambda i: (i['internal_marks'], i['marks_obtained']))[:int(to_select)]
	data = {'all_group_ct': exam_list, 'selected_ct': new_list}
	return data


def get_student_marks_new(uniq_id, subject, exam, sem_id, session_name, flag, extra_filter):
	# uniq_id,subject,exam all ids are in list
	data = []
	response = {'marks_obtained': 0, 'total_marks': 0, 'converted_marks': 0, 'total_ct_marks': 0}

	if flag == 0:
		data = get_student_per_ct_marks(uniq_id, exam, subject, session_name)
		if len(data) > 0:
			if len(data[0]['sub_details']) > 0:
				if len(data[0]['sub_details'][0]['marks_info']) > 0:
					response['converted_marks'] = data[0]['sub_details'][0]['marks_info'][0]['marks_obtained']
	else:
		data = get_student_total_ct_marks(uniq_id, sem_id, subject, session_name)
		if len(data) > 0:
			if len(data[0]['sub_details']) > 0:
				response['total_ct_marks'] = data[0]['sub_details'][0]['selected_internal']['marks_obtained']
	### BY NOW TOTAL-MARKS AND MARKS_OBTAINED IS NOT THERE ###
	return response


def check_if_ctrule_created(dept, sem, subject_type, session, session_name):
	CTMarksRules = generate_session_table_name('CTMarksRules_', session_name)

	for s in sem:
		for sub_type in subject_type:
			qry_check = CTMarksRules.objects.filter(sem=s, subject_type=sub_type).exclude(status="DELETE").values('id')
			if len(qry_check) == 0:
				return False

	return True
