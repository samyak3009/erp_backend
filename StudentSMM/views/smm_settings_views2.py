from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.db.models import Sum,F
from login.views import checkpermission,generate_session_table_name
import json
from itertools import groupby
import datetime
from datetime import date
import time
import math

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod

from StudentMMS.models import *
from StudentAcademics.models import *
from Registrar.models import *
from musterroll.models import EmployeePrimdetail
from StudentSMM.models import *
from StudentAccounts.models import SubmitFee,RefundFee



from StudentMMS.constants_functions import requestType
from StudentAcademics.views import *
from StudentMMS.views.mms_function_views import get_student_marks,single_student_ct_marks
from .smm_function_views import *
from StudentPortal.views import *


# def student_academic_details(uniq_id,session_name):
# 		academic={}
# 		q_academic_details = StudentAcademic.objects.filter(uniq_id=uniq_id).values('year_10','per_10','max_10','total_12','year_12','per_12','max_12','total_12','phy_12','phy_max','chem_12','chem_max','math_12','math_max','eng_12','eng_max','bio_12','bio_max','pcm_total','is_dip','per_dip','max_dip','total_dip','ug_year1','ug_year1_max','ug_year1_back','ug_year2','ug_year2_max','ug_year2_back','ug_year3','ug_year3_max','ug_year3_back','ug_year4','ug_year4_max','ug_year4_back','year_ug','per_ug','max_ug','total_ug','sem1_ug','sem1_ug_max','sem1_ug_back','sem2_ug','sem2_ug_max','sem2_ug_back','sem3_ug','sem3_ug_max','sem3_ug_back','sem4_ug','sem4_ug_max','sem4_ug_back','sem5_ug','sem5_ug_max','sem5_ug_back','sem6_ug','sem6_ug_max','sem6_ug_back','sem7_ug','sem7_ug_max','sem7_ug_back','sem8_ug','sem8_ug_max','sem8_ug_back','pg_year1','pg_year1_max','pg_year1_back','pg_year2','pg_year2_max','pg_year2_back','pg_year3','pg_year3_max','pg_year3_back','year_pg','per_ug','sem1_pg','sem1_pg_max','sem1_pg_back','sem2_pg','sem2_pg_max','sem2_pg_back','sem3_pg','sem3_pg_max','sem3_pg_back','sem4_pg','sem4_pg_max','sem4_pg_back','sem5_pg','sem5_pg_max','sem5_pg_back','sem6_pg','sem6_pg_max','sem6_pg_back','area_dip','ug_degree','ug_area','pg_degree','pg_area','board_10','board_12','uni_dip','uni_pg','uni_ug','year_dip')
# 		for k,v in q_academic_details[0].items():
# 			academic[k]=v
# 			if academic[k] is None or academic[k] == "":
# 				academic[k]="----"
# 		#########Academic Information###################
# 		academic['Academic']={}
# 		academic['Academic']['tenth']={}
# 		academic['Academic']['tenth']['course']='10th'
# 		academic['Academic']['tenth']['year']=academic['year_10']
# 		academic['Academic']['tenth']['percentage']=academic['per_10']
# 		academic['Academic']['tenth']['board/univ']=academic['board_10']
# 		academic['Academic']['twelfth']={}
# 		academic['Academic']['twelfth']['course']='12th'
# 		academic['Academic']['twelfth']['year']=academic['year_12']
# 		academic['Academic']['twelfth']['percentage']=academic['per_12']
# 		academic['Academic']['twelfth']['board/univ']=academic['board_12']
# 		academic['Academic']['diploma']={}
# 		academic['Academic']['diploma']['course']='Diploma'
# 		academic['Academic']['diploma']['year']=academic['year_dip']
# 		academic['Academic']['diploma']['percentage']=academic['per_dip']
# 		academic['Academic']['diploma']['board/univ']=academic['uni_dip']
# 		##############Academic information ends here###########
# 		return academic

def getComponents(request):
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		session_name=request.session['Session_name']
		session=Semtiming.objects.filter(uid=request.session['Session_id']).values('uid','sem_start','sem_end')

		if (requestMethod.GET_REQUEST(request)):
			if(requestType.custom_request_type(request.GET,'get_mentor_course')):
				data=get_mentor_course(request.session['hash1'],session_name)

			elif(requestType.custom_request_type(request.GET,'get_mentor_branch')):
				data=get_mentor_branch(request.session['hash1'],request.GET['course'],session_name)

			elif(requestType.custom_request_type(request.GET,'get_mentor_semester')):
				data=get_mentor_semester(request.session['hash1'],request.GET['branch'],session_name)

			elif(requestType.custom_request_type(request.GET,'get_mentor_section')):
				data=get_mentor_section(request.session['hash1'],request.GET['semester'],session_name)

			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)


########################################### STUDENT MENTORING BEGINS HERE ################################################

def StudentMentoring(request):
	data=[]
	data_values=[]
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		session_name=request.session['Session_name']
		sem_type=request.session['sem_type']
		session=Semtiming.objects.filter(uid=request.session['Session_id']).values('uid','sem_start','sem_end')
		SectionGroupDetails = generate_session_table_name("SectionGroupDetails_",session_name)
		GroupSection = generate_session_table_name("GroupSection_",session_name)
		stuGroupAssign = generate_session_table_name("StuGroupAssign_",session_name)
		ActivitiesApproval = generate_session_table_name("ActivitiesApproval_",session_name)
		StudentActivities = generate_session_table_name("StudentActivities_",session_name)
		studentSession = generate_session_table_name("studentSession_",session_name)
		IncidentApproval = generate_session_table_name('IncidentApproval_',session_name)

		############################GET REQUEST BEGINS HERE##################################
		if (requestMethod.GET_REQUEST(request)):
			###########FETCH GROUP NAMES############################
			if(requestType.custom_request_type(request.GET,'UnivMarksInfo')):
				uniq_id = request.GET['uniq_id']
				data = UnivMarksInfo(uniq_id,session_name,session)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'get_group_name')):
				if ('section' in request.GET):
					groupname=GroupName(request.GET['grouptype'],{'section_id':request.GET['section']},session_name,request.GET['sem'],request.session['hash1'],request.GET['type'])
				else:
					groupname=GroupName(request.GET['grouptype'],{},session_name,request.GET['sem'],request.session['hash1'],request.GET['type'])
				data={'Group_Name':groupname}
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			############# FETCH GROUP STUDENTS LIST ####################

			elif(requestType.custom_request_type(request.GET,'get_group_students')):
				group_id = request.GET['group_id']
				grpstudents=GroupStudents(group_id,session_name)
				data={'Group_Students':grpstudents}
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			############ FECTH GROUP STUDENT MARKS LIST #####################

			elif(requestType.custom_request_type(request.GET,'get_group_students_marks')):
				subject_id=request.GET['subject_id']
				group_id = request.GET['group_id']
				session = request.session['Session_id']
				grpstudents=GroupStudents(group_id,session_name)
				grpstudents_marks=GetMenteeData(group_id,subject_id,session,session_name)
				data={'Group_Students':grpstudents,'marks':grpstudents_marks}
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			############ FETCH ALL TYPE OF DATA OF A STUDENT ###########################################

			elif(requestType.custom_request_type(request.GET,'get_student_data')):
				uniq_id=request.GET['uniq_id']
				if  not checkMenteeDetails(uniq_id,request.session['hash1'],session_name):
					return functions.RESPONSE(statusMessages.MESSAGE_UNAUTHORIZED,statusCodes.STATUS_UNAUTHORIZED)
				uniq_id=request.GET['uniq_id']
				Sessions=[]
				personal_data=get_profile(uniq_id,session_name)
				academic_data=student_academic_details(uniq_id,session_name)
				stu_reg_date = list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('date_of_add'))
				all_ses = list(Semtiming.objects.values('sem_end','session','session_name','uid','sem_start'))
				i=0
				date=list(Semtiming.objects.filter(session_name=session_name).values('sem_start'))
				for s in all_ses:

					if s['sem_end']>stu_reg_date[0]['date_of_add'] and s['sem_start']>=date[0]['sem_start']:
						Sessions.append({})
						Sessions[i]['uid']=s['uid']
						Sessions[i]['session_name']=s['session_name']
						i=i+1
				data={}
				data1 = {}
				for ses in Sessions:
					UniversityWise = UnivMarksInfo(uniq_id,ses['session_name'])
					semester_wise = SemesterWisePerformance(uniq_id,ses['session_name'],ses['uid'])
					data[ses['session_name']]=semester_wise
					data1[ses['session_name']]=UniversityWise

				q_activity= get_student_activities(uniq_id,session_name)

				personal_data['res_status']=check_residential_status(uniq_id,request.session['Session_id'],sem_type)

				indisciplinary = list(get_student_indisciplinary(uniq_id,session_name))

				data_values.append({'Personal':personal_data,'Academic':academic_data,'UniversityWise':data1,'SemesterWise':data,'Activities':list(q_activity),'Indisciplinary':indisciplinary})

				return functions.RESPONSE(data_values,statusCodes.STATUS_SUCCESS)

			############FETCH STUDENT ACTIVITIES#########################
			elif(requestType.custom_request_type(request.GET,'get_student_activities')):
				uniq_id = request.GET['uniq_id']
				q_activity= get_student_activities(uniq_id,session_name)
				return functions.RESPONSE(list(q_activity),statusCodes.STATUS_SUCCESS)

			###############FETCH STUDENT COUNSELLING######################
			elif(requestType.custom_request_type(request.GET,'get_student_counselling')):
				uniq_id=request.GET['uniq_id']
				q_counselling=get_student_counselling(uniq_id,session_name)
				return functions.RESPONSE(list(q_counselling),statusCodes.STATUS_SUCCESS)
			##############FETCH COUNSELLING TYPE###########################
			elif(requestType.custom_request_type(request.GET,'get_counselling_type')):
				session=request.session['Session_id']
				counselling_type=get_counselling_type(session)
				return functions.RESPONSE(list(counselling_type),statusCodes.STATUS_SUCCESS)

		########################GET REQUEST ENDS HERE########################################

		##########################PUT REQUEST BEGINS HERE####################################
		elif (requestMethod.PUT_REQUEST(request)):
			data = json.loads(request.body)
			emp_id=request.session['hash1']
			if(data['update_type']=='update_details'):
				##############UPDATE STUDENT'S MOBILE#################################
				if(data['update']=='mobile'):
					q_update_student_sesssion_detail=studentSession.objects.filter(uniq_id=data['uniq_id']).update(mob=data['mob'])
					return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)
				##############UPDATE STUDENT'S ADDRESS###############################
				elif(data['update']=='address'):
					q_update_student_address_detail=StudentAddress.objects.filter(uniq_id=data['uniq_id']).update(c_add1=data['c_add1'],c_add2=data['c_add2'],c_city=data['c_city'],c_district=data['c_district'],c_pincode=data['c_pincode'])
					return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)
				else:
					return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST,statusCodes.STATUS_BAD_REQUEST)

			##################APPROVE STUDENT ACTIVITY###############################
			elif(data['update_type']=='update_activity_status'):
				q_approve_activity=ActivitiesApproval.objects.filter(Activities_detail__id__in=data['id']).update(appoval_status=data['approval_status'])
				return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)

		###############################PUT REQUEST ENDS HERE#####################################

		###############################POST REQUEST BEGINS HERE##################################
		elif (requestMethod.POST_REQUEST(request)):
			CouncellingApproval = generate_session_table_name("CouncellingApproval_",session_name)
			CouncellingDetail = generate_session_table_name("CouncellingDetail_",session_name)
			data = json.loads(request.body)
			date=datetime.date.today()
			q_counselling_create=CouncellingDetail.objects.create(date_of_councelling=date,type_of_councelling=StudentAcademicsDropdown.objects.get(sno=data['type_of_councelling']),uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']),remark=data['remark'],student_document=data['student_document'],added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
			q_counselling_approval_create=CouncellingApproval.objects.create(councelling_detail=CouncellingDetail.objects.get(id=q_counselling_create.id))
			if(q_counselling_approval_create and q_counselling_create):
				return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)

			else:
				return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE("COULD NOT INSERT"),statusCodes.STATUS_SERVER_ERROR)
		###############################POST REQUEST ENDS HERE#####################################

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

##########################################STUDENT MENTORING ENDS HERE#####################################################
