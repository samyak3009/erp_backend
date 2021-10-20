from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from StudentMMS.constants_functions import requestType

from musterroll.models import EmployeePrimdetail
from login.models import EmployeeDropdown
from Registrar.models import StudentSemester,CourseDetail,StudentDropdown
from StudentMMS.models import *
from StudentAcademics.models import *

from .mms_function_views import get_btlevel,get_skillsetlevel,get_verb,get_skillsetlevel_filtered,get_btleveldata,get_co,get_exam_name,get_exam_shift,get_ct_group
from login.views import checkpermission,generate_session_table_name
from StudentAcademics.views import  get_student_subjects,check_islocked
from itertools import groupby

#####get_all_co_details#######
def get_co_details(subject_id,session_name):
	SubjectCODetails = generate_session_table_name("SubjectCODetails_",session_name)
	query=list(SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').values('description','added_by','id'))
	return query

#####get_faculty_subjects_corresponding_to_faculty#######
def get_faculty_subjects(emp_id,sem,session_name):
	# emp_id=request.session['hash1']
	FacultyTime = generate_session_table_name("FacultyTime_",session_name)
	query=list(FacultyTime.objects.filter(emp_id=emp_id,subject_id__sem=sem).exclude(status='DELETE').values('subject_id__sub_alpha_code','subject_id__sub_num_code','subject_id__sub_name','subject_id').distinct())
	return query

def get_coordinator_subject(emp_id,coord_type,dept,session_name):
	dept_li=dept.split(",")
	AcadCoordinator = generate_session_table_name("AcadCoordinator_",session_name)
	q_get_subjects  = AcadCoordinator.objects.filter(coord_type=coord_type,emp_id=emp_id,section__sem_id__dept__in=dept_li).exclude(status='DELETE').values('subject_id','subject_id__sub_name','subject_id__sub_num_code','subject_id__sub_alpha_code').distinct().order_by('section__sem_id__sem')
	return list(q_get_subjects)

def add_question(emp_id,data,session_name):

	SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_",session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
	SubjectCODetails = generate_session_table_name("SubjectCODetails_",session_name)
	SubjectQuesOptions = generate_session_table_name("SubjectQuesOptions_",session_name)

	if(data['question_type']=='S'):
		##########add subjective question#############
		add_ques=SubjectAddQuestions.objects.create(subject_id=SubjectInfo.objects.get(id=data['subject_id']),description=data['description'],question_img=data['question_img'],max_marks=data['max_marks'],co_id=SubjectCODetails.objects.get(id=data['co_id']),bt_level=StudentAcademicsDropdown.objects.get(sno=data['bt_level']),answer_key=data['answer_key'],answer_img=data['answer_img'],added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
		if(add_ques):
			return 1

	elif(data['question_type']=='O'):
		##########add objective question#############
		add_ques=SubjectAddQuestions.objects.create(subject_id=SubjectInfo.objects.get(id=data['subject_id']),description=data['description'],type='O',question_img=data['question_img'],max_marks=data['max_marks'],co_id=SubjectCODetails.objects.get(id=data['co_id']),bt_level=StudentAcademicsDropdown.objects.get(sno=data['bt_level']),answer_key=data['answer_key'],answer_img=data['answer_img'],added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
		##########add choices for objective question#############
		objs=(SubjectQuesOptions(ques_id=SubjectAddQuestions.objects.get(id=add_ques.id),option_description=options['option_description'],option_img=options['option_img'],is_answer=options['is_answer']) for options in data['option'])
		add_options=SubjectQuesOptions.objects.bulk_create(objs)
		if(add_ques):
			return 1
		else:
			return 0

def update_question(emp_id,data,session_name):
	SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_",session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
	SubjectCODetails = generate_session_table_name("SubjectCODetails_",session_name)
	SubjectQuesOptions = generate_session_table_name("SubjectQuesOptions_",session_name)

	if(data['type']=='S'):
		#########add subjective question#############
		add_ques=SubjectAddQuestions.objects.filter(id=data['id']).update(subject_id=SubjectInfo.objects.get(id=data['subject_id']),description=data['description'],question_img=data['question_img'],max_marks=data['max_marks'],co_id=SubjectCODetails.objects.get(id=data['co_id']),bt_level=StudentAcademicsDropdown.objects.get(sno=data['bt_level']),answer_key=data['answer_key'],answer_img=data['answer_img'],added_by=EmployeePrimdetail.objects.get(emp_id=emp_id),approval_status=data['approval_status'])
		if(add_ques):
			return 1

	elif(data['type']=='O'):
		##########add objective question#############
		add_ques=SubjectAddQuestions.objects.filter(id=data['id']).update(subject_id=SubjectInfo.objects.get(id=data['subject_id']),description=data['description'],type='O',question_img=data['question_img'],max_marks=data['max_marks'],co_id=SubjectCODetails.objects.get(id=data['co_id']),bt_level=StudentAcademicsDropdown.objects.get(sno=data['bt_level']),answer_key=data['answer_key'],answer_img=data['answer_img'],added_by=EmployeePrimdetail.objects.get(emp_id=emp_id),approval_status=data['approval_status'])
		##########add choices for objective question#############
		query=SubjectQuesOptions.objects.filter(ques_id=data['id']).delete()
		objs=(SubjectQuesOptions(ques_id=SubjectAddQuestions.objects.get(id=data['id']),option_description=options['option_description'],option_img=options['option_img'],is_answer=options['is_answer']) for options in data['option'])
		add_options=SubjectQuesOptions.objects.bulk_create(objs)
		if(add_ques):
			return 1
		else:
			return 0



def AddQues(request):
	data1=[]
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		session_name=request.session['Session_name']
		BTLevelSettings=generate_session_table_name("BTLevelSettings_",session_name)
		SubjectAddQuestions=generate_session_table_name("SubjectAddQuestions_",session_name)
		SubjectQuesOptions=generate_session_table_name("SubjectQuesOptions_",session_name)
		SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
		QuestionpaperQuestion = generate_session_table_name("QuestionPaperQuestions_",session_name)
		

		if (requestMethod.GET_REQUEST(request)):
			emp_id=request.session['hash1']
			if(requestType.custom_request_type(request.GET,'get_subjects')):
				##########get subjects corresponding to a facuty in particular sem#############
				# emp_id=request.session['hash1']
				data=get_faculty_subjects(emp_id,request.GET['sem'],session_name)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'get_co')):
				##########get co details corresponding to a subject id#############
					co_detail=get_co(request.GET['subject_id'],session_name)
					##########get all bt_levels#############

					bt_level_verbs=BTLevelSettings.objects.exclude(status='DELETE').values('verb','bt_level','bt_level__value','bt_num').order_by('bt_level')
					data1=[]
					for k,v in groupby(bt_level_verbs,key=lambda x:x['bt_level']):
						verb_li=[]
						v=list(v)
						for t in list(v):
							verb_li.append(t['verb'])
						data1.append({'bt_level':v[0]['bt_level__value'],'bt_level_id':v[0]['bt_level'],'verbs':verb_li,'bt_level_num':"BT-"+str(v[0]['bt_num'])})

					data={'CO_DETAILS':co_detail,'BT_LEVELS':data1}
					return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'view_previous')):
				get_previous=list(SubjectAddQuestions.objects.filter(subject_id=request.GET['subject_id'],added_by=emp_id).exclude(status='DELETE').values('type','description','question_img','max_marks','co_id__description','co_id','bt_level','answer_key','answer_img','id','co_id__co_num','bt_level__value','approval_status'))
				i=0
				for prev in get_previous:
					status_qry = list(QuestionpaperQuestion.objects.filter(ques_id=prev['id']).exclude(status="DELETE").values_list('id',flat=True))
					if len(status_qry)>0:
						get_previous[i]['add_status'] = True
					else:
						get_previous[i]['add_status'] = False	
					get_previous[i]['option']=list(SubjectQuesOptions.objects.filter(ques_id=prev['id']).values('option_description','option_img','is_answer'))
					i+=1
				data=list(get_previous)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
			else:
				return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST,statusCodes.STATUS_BAD_REQUEST)

		elif (requestMethod.POST_REQUEST(request)):
			data = json.loads(request.body)
			emp_id=request.session['hash1']

			qry_sem = SubjectInfo.objects.filter(id=data['subject_id']).values('sem')
			qry_sections = list(Sections.objects.filter(sem_id=qry_sem[0]['sem']).values_list('section_id',flat=True))

			if check_islocked('QUES',qry_sections,session_name):
				return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

			add=add_question(emp_id,data,session_name)
			if(add==1):
				return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)

		elif(requestMethod.PUT_REQUEST(request)):
			data = json.loads(request.body)
			emp_id=request.session['hash1']

			qry_sem = SubjectInfo.objects.filter(id=data['subject_id']).values('sem')
			qry_sections = list(Sections.objects.filter(sem_id=qry_sem[0]['sem']).values_list('section_id',flat=True))

			if check_islocked('QUES',qry_sections,session_name):
				return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
			# delete_prev_question=SubjectAddQuestions.objects.filter(id=data['question_id']).update(status='DELETE')
			update=update_question(emp_id,data,session_name)
			if(update==1):
				return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)

		elif(requestMethod.DELETE_REQUEST(request)):
			data = json.loads(request.body)

			qry_sem = SubjectAddQuestions.objects.filter(id=data['question_id']).values('subject_id__sem')

			qry_sections = list(Sections.objects.filter(sem_id=qry_sem[0]['subject_id__sem']).values_list('section_id',flat=True))

			if check_islocked('QUES',qry_sections,session_name):
				return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
			# emp_id=request.session['hash1']
			delete_prev_question=SubjectAddQuestions.objects.filter(id=data['question_id']).update(status='DELETE')
			if(delete_prev_question):
				return functions.RESPONSE(statusMessages.MESSAGE_DELETE,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def QuestionModerator(request):
	data1=[]
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		session_name=request.session['Session_name']
		session = request.session['Session_id']
		SubjectAddQuestions=generate_session_table_name("SubjectAddQuestions_",session_name)
		SubjectQuesOptions=generate_session_table_name("SubjectQuesOptions_",session_name)

		if (requestMethod.GET_REQUEST(request)):
			if(requestType.custom_request_type(request.GET,'get_subjects')):
				##########get subjects corresponding to a facuty in particular sem#############
				emp_id=request.session['hash1']
				data=get_coordinator_subject(emp_id,request.GET['coord_type'],request.GET['dept'],session_name)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
			if(requestType.custom_request_type(request.GET,'view_previous')):
				get_previous=list(SubjectAddQuestions.objects.filter(subject_id=request.GET['subject_id']).exclude(status='DELETE').values('type','description','question_img','max_marks','co_id__description','co_id','bt_level','bt_level__value','answer_key','answer_img','id','co_id__co_num','approval_status','added_by'))
				i=0
				for prev in get_previous:
					get_previous[i]['option']=list(SubjectQuesOptions.objects.filter(ques_id=prev['id']).values('option_description','option_img','is_answer'))
					i+=1
				data=list(get_previous)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			if(requestType.custom_request_type(request.GET,'get_btlevel')):
				data=get_btlevel(session)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
			else:
				return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST,statusCodes.STATUS_BAD_REQUEST)

		elif(requestMethod.PUT_REQUEST(request)):
			data = json.loads(request.body)
			emp_id=data['added_by']

			add_ques=SubjectAddQuestions.objects.filter(id=data['id']).values('subject_id__sem')

			qry_sections = list(Sections.objects.filter(sem_id=add_ques[0]['subject_id__sem']).values_list('section_id',flat=True))

			if check_islocked('QM',qry_sections,session_name):
				return JsonResponse(data={'msg':'Portal is Locked, please contact Dean Academics office to unlock the portal.'},status=202)

			update=update_question(emp_id,data,session_name)
			if(update==1):
				return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def CoeCoordinator(request):
	data_values={}
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		emp_id=request.session['hash1']
		session=request.session['Session_id']
		session_name=request.session['Session_name']
		DeptExamSchedule=generate_session_table_name("DeptExamSchedule_",session_name)
		SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)

		if (requestMethod.GET_REQUEST(request)):
			if(requestType.custom_request_type(request.GET,'get_subjects')):
				##########get subjects corresponding to a facuty in particular sem ############
				data=get_student_subjects(request.GET['sem'],session_name)
				data1=get_exam_name(session)
				data2=get_exam_shift(session)
				data_values={'data':data,'data1':data1,'data2':data2}
				return functions.RESPONSE(data_values,statusCodes.STATUS_SUCCESS)

			if(requestType.custom_request_type(request.GET,'view_previous')):
				data=list(DeptExamSchedule.objects.filter(added_by=emp_id).exclude(status='DELETE').values('exam_date','id','subject_id','subject_id__sub_alpha_code','subject_id__sub_num_code','subject_id__sub_name','exam_shift__value','exam_id__value','added_by','start_time','end_time','sem__sem','sem__dept__dept__value','sem__dept','sem__sem_id'))

				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
			else:
				return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST,statusCodes.STATUS_BAD_REQUEST)

		elif(requestMethod.POST_REQUEST(request)):
			data = json.loads(request.body)
			sem=data['sem']
			for s in sem:
				query1=DeptExamSchedule.objects.filter(sem=s,subject_id__in=data['subjects'],exam_id=data['exam_id']).exclude(status='DELETE')
			if (query1):
				return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE("Selected Subject already added"),statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
			for s in sem:
				objs=(DeptExamSchedule(exam_id=StudentAcademicsDropdown.objects.get(sno=data['exam_id']),sem=StudentSemester.objects.get(sem_id=s),subject_id=SubjectInfo.objects.get(id=sub),exam_date=data['exam_date'],start_time=data['start_time'],end_time=data['end_time'],exam_shift=StudentAcademicsDropdown.objects.get(sno=data['exam_shift']),added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])) for sub in data['subjects'])
				add=DeptExamSchedule.objects.bulk_create(objs)
			return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)

		elif(requestMethod.PUT_REQUEST(request)):
			data = json.loads(request.body)
			sem=data['sem']
			delete_prev=DeptExamSchedule.objects.filter(id=data['id']).update(status='DELETE')
			query=DeptExamSchedule.objects.create(exam_id=StudentAcademicsDropdown.objects.get(sno=data['exam_id']),sem=StudentSemester.objects.get(sem_id=data['sem']),subject_id=SubjectInfo.objects.get(id=data['subjects']),exam_date=data['exam_date'],start_time=data['start_time'],end_time=data['end_time'],exam_shift=StudentAcademicsDropdown.objects.get(sno=data['exam_shift']),added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
			if query:
				return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)
			else:
				return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE("Could not update"),statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

		elif(requestMethod.DELETE_REQUEST(request)):
			data = json.loads(request.body)
			delete_prev=DeptExamSchedule.objects.filter(id=data['id']).update(status='DELETE')
			if(delete_prev):
				return functions.RESPONSE(statusMessages.MESSAGE_DELETE,statusCodes.STATUS_SUCCESS)
			else:
				return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE("Could not delete"),statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def CtMarksRule(request):
	data_values={}
	sem_id=[]
	sub_type=[]
	if checkpermission(request,[rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
		session_name=request.session['Session_name']
		session=request.session['Session_id']
		CTMarksRule=generate_session_table_name("CTMarksRule_",session_name)

		if (requestMethod.GET_REQUEST(request)):

			if(requestType.custom_request_type(request.GET,'checkbox')):
				data2=get_ct_group(session)
				data1=get_exam_name(session)
				data_values={'data1':data1,'data2':data2}
				return functions.RESPONSE(data_values,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'view_previous')):
				data=[]
				sem_id=CTMarksRule.objects.exclude(status="DELETE").values_list('sem',flat=True).distinct()
				for s in sem_id:
					qry2=CTMarksRule.objects.filter(sem=s).exclude(status="DELETE").values_list('subject_type',flat=True).distinct()
					for sub in qry2:
						qry=CTMarksRule.objects.filter(sem=s,subject_type=sub).exclude(status="DELETE").values('ct_to_select','sem','sem__sem','sem__dept','sem__dept__course','sem__dept__dept__value','sem__dept__course__value').distinct()
						qry1=list(CTMarksRule.objects.filter(sem=s,subject_type=sub).exclude(status="DELETE").values('ct_group','id','subject_type','subject_type__value').distinct())


						data.append({"data":list(qry1),"data2":list(qry)})
				data_values={"data":data}
			elif(requestType.custom_request_type(request.GET,'delete')):
				qry_sections = list(Sections.objects.values_list('section_id',flat=True))

				if check_islocked('DMS',qry_sections,session_name):
					return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

				id=request.GET['id'].split(',')
				qry=CTMarksRule.objects.filter(id__in=id).update(status="DELETE")
				data_values=statusMessages.MESSAGE_DELETE
			return functions.RESPONSE(data_values,statusCodes.STATUS_SUCCESS)

		elif (requestMethod.PUT_REQUEST(request)):
			data=json.loads(request.body)

			qry_sections = list(Sections.objects.values_list('section_id',flat=True))

			if check_islocked('DMS',qry_sections,session_name):
				return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

			rule_id=data['rule_id']
			data2=get_ct_group(session)
			value=int(data2[0]['value'])

			ct_to_select=data['ct_select_to']
			if (ct_to_select==value):
				sem_id=CTMarksRule.objects.filter(id__in=rule_id).exclude(status="DELETE").values_list('sem_id',flat=True).distinct()
				sub_type=CTMarksRule.objects.filter(id__in=rule_id).exclude(status="DELETE").values_list('subject_type',flat=True).distinct()
				objs=(CTMarksRule(sem=StudentSemester.objects.get(sem_id=s),ct_group=data['ct_group'],ct_to_select=data['ct_select_to'],subject_type=StudentDropdown.objects.get(sno=sub)) for s in list(sem_id) for sub in list(sub_type))
				add=CTMarksRule.objects.bulk_create(objs)
			else:
				sem_id=CTMarksRule.objects.filter(id__in=rule_id).exclude(status="DELETE").values_list('sem_id',flat=True).distinct()
				sub_type=CTMarksRule.objects.filter(id__in=rule_id).exclude(status="DELETE").values_list('subject_type',flat=True).distinct()
				for group in data['ct_group']:
					objs=(CTMarksRule(sem=StudentSemester.objects.get(sem_id=s),ct_group=group,ct_to_select=data['ct_select_to'],subject_type=StudentDropdown.objects.get(sno=sub)) for s in list(sem_id) for sub in list(sub_type))
					add=CTMarksRule.objects.bulk_create(objs)
			qry2=CTMarksRule.objects.filter(id__in=rule_id).exclude(status="DELETE").update(status="DELETE")

			if add:
				data=statusMessages.MESSAGE_UPDATE

			else:
				data=statusMessages.MESSAGE_BAD_REQUEST
			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)



		elif (requestMethod.POST_REQUEST(request)):
			data=json.loads(request.body)

			qry_sections = list(Sections.objects.values_list('section_id',flat=True))

			if check_islocked('DMS',qry_sections,session_name):
				return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

			ct_select_to=data['ct_select_to']
			data2=get_ct_group(session)
			sem_id=StudentSemester.objects.filter(dept__in=data['dept'],sem__in=data['sem']).values_list('sem_id',flat=True)
			id=CTMarksRule.objects.filter(sem__in=list(sem_id),subject_type__in=data['sub_type']).exclude(status="DELETE").values_list('id',flat=True)
			if(id):
				qry=CTMarksRule.objects.filter(id__in=list(id)).update(status="DELETE")


			value=int(data2[0]['value'])

			if(ct_select_to == value):
				sem_id=StudentSemester.objects.filter(dept__in=data['dept'],sem__in=data['sem']).values_list('sem_id',flat=True)
				objs=(CTMarksRule(sem=StudentSemester.objects.get(sem_id=s),ct_group=data['ct_group'],ct_to_select=data['ct_select_to'],subject_type=StudentDropdown.objects.get(sno=d1)) for s in sem_id for d1 in data['sub_type'])
				add=CTMarksRule.objects.bulk_create(objs)

			else:
				for group in data['ct_group']:
					sem_id=StudentSemester.objects.filter(dept__in=data['dept'],sem__in=data['sem']).values_list('sem_id',flat=True)
					objs=(CTMarksRule(sem=StudentSemester.objects.get(sem_id=s),ct_group=group,ct_to_select=data['ct_select_to'],subject_type=StudentDropdown.objects.get(sno=d1)) for s in sem_id for d1 in data['sub_type'])
					add=CTMarksRule.objects.bulk_create(objs)
			return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
