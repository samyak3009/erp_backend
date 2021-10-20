from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from itertools import groupby
from django.db import connection
import math

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType

from StudentMMS.models import *
from StudentAcademics.models import *
from musterroll.models import EmployeePrimdetail
from Registrar.models import StudentSemester, CourseDetail, StudentDropdown
from login.models import EmployeeDropdown

from login.views import checkpermission, generate_session_table_name
from .mms_function_views import *
from StudentAcademics.views import *


def new_CtMarksRule(request):
	if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
		session_name = request.session['Session_name']
		emp_id = request.session['hash1']
		session = request.session['Session_id']
		CTMarksRules = generate_session_table_name("CTMarksRules_", session_name)
		CTMarksGroup = generate_session_table_name("CTMarks_GroupInfo_", session_name)
		CTMarksExam = generate_session_table_name("CTMarks_Group_ExamInfo_", session_name)

		session_num = int(session_name[:2])
		if session_num < 19:
			return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
		if (requestMethod.GET_REQUEST(request)):
			if(requestType.custom_request_type(request.GET, 'exam_type')):
				data = get_exam_name(session)
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

			if(requestType.custom_request_type(request.GET, 'view_previous')):
				# if session < 8:
				#     return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
				sem = request.GET['sem'].split(',')
				sub_type = request.GET['subject_type'].split(',')
				department = request.GET['department'].split(',')

				sem_id = list(StudentSemester.objects.filter(dept__in=department, sem__in=sem).values_list('sem_id', flat=True))

				sem_id_list = CTMarksRules.objects.filter(sem__in=sem_id).distinct().exclude(status='DELETE').values_list('sem', flat=True)
				subject_type = CTMarksRules.objects.filter(subject_type__in=sub_type).distinct().exclude(status='DELETE').values_list('subject_type', flat=True)

				rules = []
				for x in sem_id:
					for y in sub_type:

						rule_list = list(CTMarksRules.objects.filter(sem=x, subject_type=y).exclude(status='DELETE').values('rule_no', 'rule_criteria', 'id'))

						if(rule_list == []):
							continue
						else:
							objects = {'data': []}
							objects['data'].append(rule_list)

						for rule in rule_list:
							rule['sem'] = list(StudentSemester.objects.filter(sem_id=x).values_list('sem', flat=True))[0]
							rule['sub_type'] = StudentDropdown.objects.filter(field="SUBJECT TYPE", sno=y).exclude(value__isnull=True).exclude(status="DELETE").values_list('value', flat=True)[0]
							dep_cou = list(StudentSemester.objects.filter(sem_id=x).values('dept__course__value', 'dept__dept__value'))[0]
							rule['course'] = dep_cou['dept__course__value']
							rule['department'] = dep_cou['dept__dept__value']

							rule.update({"group": []})
							group = list(CTMarksGroup.objects.filter(rule_id=rule['id']).exclude(status='DELETE').values('group', 'weightage', 'ct_to_select', 'id'))
							for g in group:
								g.update({"exam_type_list": []})
								exam_type = list(CTMarksExam.objects.filter(group_id=g['id']).exclude(status='DELETE').values_list('exam_id__value', flat=True))
								g['exam_type_list'].extend(exam_type)
							rule['group'] = group
						objects['course'] = rule['course']
						objects['department'] = rule['department']
						objects['sem'] = rule['sem']
						objects['sub_type'] = rule['sub_type']
						objects['rule_criteria'] = rule['rule_criteria']
						rules.append(objects)

				return functions.RESPONSE(rules, statusCodes.STATUS_SUCCESS)

		elif(requestMethod.POST_REQUEST(request)):
			received_data = json.loads(request.body)
			rules = received_data['rules']
			sem = received_data['sem']
			sub_type = received_data['sub_type']
			criteria = received_data['criteria']
			if session < 8:
				return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
			no_of_rule = len(rules)
			check = check_rule_weight(rules)
			if check == False:
				return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE("Rule Weightage must be hundred"), statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
			sem_id = list(StudentSemester.objects.filter(dept__in=received_data['dept'], sem__in=sem).values_list('sem_id', flat=True))

			delete_prev_rule = CTMarksRules.objects.filter(sem_id__in=sem_id, subject_type__in=sub_type).update(status="DELETE")
			delete_prev_group = CTMarksGroup.objects.filter(rule_id__sem_id__in=sem_id, rule_id__subject_type__in=sub_type).update(status="DELETE")
			delete_prev_exam = CTMarksExam.objects.filter(group_id__rule_id__sem_id__in=sem_id, group_id__rule_id__subject_type__in=sub_type).update(status="DELETE")

			objs = (CTMarksRules(sem=StudentSemester.objects.get(sem_id=s), subject_type=StudentDropdown.objects.get(sno=d1), rule_no=x, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), rule_criteria=criteria) for s in sem_id for d1 in sub_type for x in range(1, no_of_rule + 1))
			add = CTMarksRules.objects.bulk_create(objs)

			id_list = list(CTMarksRules.objects.filter(subject_type__in=sub_type, sem__in=sem_id, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id)).exclude(status="DELETE").values('id', 'rule_no'))
			for x in id_list:
				rule_number = x['rule_no'] - 1
				obj = (CTMarksGroup(rule_id=CTMarksRules.objects.get(id=x['id']), group=(num + 1), weightage=rules[rule_number][num]['weightage'], ct_to_select=rules[rule_number][num]['ct_to_select'])for num in range(len(rules[rule_number])))
				add = CTMarksGroup.objects.bulk_create(obj)

				group_id_list = list(CTMarksGroup.objects.filter(rule_id=x['id']).exclude(status="DELETE").values('id', 'group'))
				for y in group_id_list:
					group_number = int(y['group']) - 1
					objs = (CTMarksExam(group_id=CTMarksGroup.objects.get(id=y['id']), exam_id=StudentAcademicsDropdown.objects.get(sno=exam))for exam in rules[rule_number][group_number]['sno'])
					add1 = CTMarksExam.objects.bulk_create(objs)

			return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def fetch_bonus_marks(uniq_id, subjects, sem_id, session_name):

	BonusMarks = generate_session_table_name("BonusMarks_", session_name)
	BonusMarks_Rule = generate_session_table_name("BonusMarks_Rule_", session_name)

	final_list = {}
	max_len = 0
	for each in uniq_id:
		new_dict = {}
		each_id = each['uniq_id']
		for subject in subjects:
			sub_id = subject['id']
			data = []
			sub_dict = {'marks_info': [], 'rule_data': []}

			fetch_rules_subrules = list(BonusMarks.objects.filter(uniq_id=each_id, rule_id__app_id__subject=sub_id, rule_id__app_id__sem_id=sem_id).exclude(status="DELETE").values('rule_id__rule_no', 'rule_id__subrule_no').distinct())
			for each_rule in fetch_rules_subrules:
				b_marks = BonusMarks.objects.filter(uniq_id=each_id, rule_id__app_id__subject=sub_id, rule_id__app_id__sem_id=sem_id, rule_id__rule_no=each_rule['rule_id__rule_no'], rule_id__subrule_no=each_rule['rule_id__subrule_no']).exclude(status="DELETE").values_list('total_bonus_marks', flat=True)
				bonus_marks = 0
				if len(b_marks) > 0:
					bonus_marks = b_marks[0]
				marks_dict = {'rule_no': each_rule['rule_id__rule_no'], 'subrole_id': each_rule['rule_id__subrule_no'], 'marks': bonus_marks}
				data.append(bonus_marks)
				sub_dict['marks_info'].append(marks_dict)

			sub_dict['rule_data'] = data
			p_len = len(sub_dict['rule_data'])

			if(max_len < p_len):
				max_len = p_len
			new_dict[sub_id] = sub_dict
		final_list[each_id] = new_dict
	for stu, data in final_list.items():
		for sub, sub_data in data.items():
			diff = max_len - len(sub_data['rule_data'])
			for i in range(0, diff):
				sub_data['rule_data'].append(0)

	return final_list