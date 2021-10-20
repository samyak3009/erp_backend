from django.shortcuts import render

import datetime
from datetime import datetime,timedelta
from django.utils import timezone
from django.http import HttpResponse,JsonResponse
from django.db.models import Avg, Sum, Count, Subquery, OuterRef, F, Value, Func, Case, When, IntegerField, CharField
from collections import Counter
from itertools import groupby
import copy
import math

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from erp.constants_functions.functions import *
from StudentMMS.constants_functions import requestType

from Registrar.models import *
from StudentAcademics.models import *
from StudentFeedback.models import *
from StudentAccounts.models import SubmitFee,RefundFee
from musterroll.models import EmployeePrimdetail
from Registrar.models import StudentSemester,StudentDropdown,Sections,CourseDetail

from login.views import checkpermission,generate_session_table_name
from StudentFeedback.views.feedback_function_views import check_is_portal_locked,get_attribute,studentDetailNstatus,student_residency,getSection,for_feedback_get_student_attendance,faculty_feedback_details,individual_faculty_consolidate,check_islocked
from StudentAcademics.views import get_course,get_subject_type,get_gender, get_sub_attendance_type,get_student_subjects,get_attendance_type,get_student_attendance,get_semester,get_section,get_section_students,get_filtered_emps

# class Round(Func):
#     function = 'ROUND'
#     template='%(function)s(%(expressions)s, 2)'

def ViewAttrbuteRemark(request):
	data_values={}
	if (requestMethod.POST_REQUEST(request)):
		data=json.loads(request.body)
		session_name=request.session['Session_name']
		StuFeedbackMarks=generate_session_table_name("StuFeedbackMarks_",session_name)

		if requestByCheck.requestByDean(data) or requestByCheck.requestByHOD(data):
			subject_typing=get_subject_type()
			subject_typing.append( {'sno': None, 'value': 'INSTITUTE'})
			sections=getSection(data['branch'],data['sem'],data['section'])
			data_values=[]
			for sub_type in subject_typing:
				temp_list=list(StuFeedbackMarks.objects.filter(feedback_id__feedback_id__uniq_id__section__in=sections,feedback_id__feedback_id__status="INSERT",attribute__subject_type=sub_type['sno'],attribute__eligible_settings_id__status="INSERT").exclude(feedback_id__remark__isnull=True).exclude(feedback_id__remark="").values("feedback_id__feedback_id__uniq_id__section__section","feedback_id__feedback_id__uniq_id__section__sem_id__sem","feedback_id__feedback_id__uniq_id__section__dept__dept__value","feedback_id__feedback_id__uniq_id__section__dept__course__value","attribute__subject_type","attribute__subject_type__value","feedback_id__remark",'feedback_id__subject__sub_name','feedback_id__subject__sub_alpha_code', 'feedback_id__subject__sub_num_code','feedback_id__subject__subject_type','feedback_id__id','feedback_id__subject__subject_type__value','feedback_id__emp_id__name','feedback_id__emp_id__desg__value').distinct())
				sub_type['count']=len(temp_list)
				data_values=data_values+temp_list

			data={'detail':data_values,'consolidate':subject_typing}
			status=statusCodes.STATUS_SUCCESS
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data,status)

def ViewStudentStatusConsolidate(request):
	data_values={}
	if (requestMethod.POST_REQUEST(request)):
		sem_type=request.session['sem_type']
		session_name=request.session['Session_name']
		session_id=request.session['Session_id']
		# session_name="1819o"
		# session_id=1
		data=json.loads(request.body)
		consolidate=[]
		whole_not_filled_total=0
		whole_eligible_total=0
		whole_filled_total=0
		whole_total=0
		whole_given_percentage=0.0
		whole_eligible_given_percentage=0.0
		whole_count=len(data['dept'])
		student_list=[]

		####################################### FEEDBACK FOR TOTAL FEEDBACK ###########################################

		for index,dept in enumerate(data['dept']):
			consolidate.append({})
			consolidate[index]['dept']=list(CourseDetail.objects.filter(uid=dept).values("dept_id","dept_id__value"))[0]
			consolidate[index]['sems']=list(StudentSemester.objects.filter(dept=dept,sem__in=data['semester']).values('sem_id','sem'))
			dept_not_filled_total=0
			dept_eligible_total=0
			dept_filled_total=0
			dept_total=0
			dept_given_percentage=0.0
			dept_eligible_given_percentage=0.0
			dept_count=len(consolidate[index]['sems'])

			######################################## FEEDBACK FOR A DEPARTMENT ###################################

			for sem in consolidate[index]['sems']:
				sem['sections']=list(Sections.objects.filter(sem_id=sem['sem_id'],section__in=data['section']).values('section','section_id'))
				sem_not_filled_total=0
				sem_eligible_total=0
				sem_filled_total=0
				sem_total=0
				sem_given_percentage=0.0
				sem_eligible_given_percentage=0.0
				sem_count=len(sem['sections'])

				##################### LOOP TO FIND DETAILS OF FEEDBACK OF A SECTION #########################################

				for section in sem['sections']:
					get_portal_unlocked_date=check_is_portal_locked(section['section_id'],session_name)
					att_to_date = datetime.strptime(str(get_portal_unlocked_date['time_stamp']).split(" ")[0], '%Y-%m-%d').date()
					students=get_section_students([section['section_id']],{},session_name)
					section['TOTAL']=len(students[0])
					list_array=[]

					############ LOOP TO FIND STATUS OF FEEDBACK OF STUDENT OF A SECTION AND STUDENT DETAILS ################

					for x in students[0]:
						temp_student_detail=studentDetailNstatus(request,x['uniq_id'],att_to_date,session_name,session_id)
						x['status']=temp_student_detail['status']
						temp_date = datetime.strptime(str(x['att_start_date']), '%Y-%m-%d')
						x['att_start_date']=temp_date.strftime('%d-%m-%y')
						if(x['status']=="ALREADY_FILLED"):
							student_attendance=for_feedback_get_student_attendance(request,x['uniq_id'],att_to_date,session_name,session_id)
							x['current_percent']=student_attendance['current_percent']
							x['eligible_percent']=student_attendance['eligible_percentage']
						else:
							x['current_percent']=temp_student_detail['current_percent']
							x['eligible_percent']=temp_student_detail['eligible_percentage']
						x['res_status']=student_residency(request,x['uniq_id'])
						list_array.append(x['status'])
						student_list.append(x)
					section["NOT_FILLED"]=0
					section["NOT_ELIGIBLE"]=0
					section["ALREADY_FILLED"]=0
					section["PERCENTAGE_GIVEN_FEEDBACK"]=0
					section["PERCENTAGE_ELIGIBLE_GIVEN_FEEDBACK"]=0
					list_count=dict(Counter(list_array))

					#######################################################################################################

					for x in list_count:
						section[x]=list_count[x]
					x = section["TOTAL"]-section["NOT_ELIGIBLE"]
					if x == 0 or section["TOTAL"] == 0:
						sem_not_filled_total=sem_not_filled_total+section["NOT_FILLED"]
						sem_eligible_total=sem_eligible_total+section["NOT_ELIGIBLE"]
						sem_filled_total=sem_filled_total+section["ALREADY_FILLED"]
						sem_total=sem_total+section["TOTAL"]
						section["PERCENTAGE_GIVEN_FEEDBACK"]=0
						section["PERCENTAGE_ELIGIBLE_GIVEN_FEEDBACK"]=0
					else:
						sem_not_filled_total=sem_not_filled_total+section["NOT_FILLED"]
						sem_eligible_total=sem_eligible_total+section["NOT_ELIGIBLE"]
						sem_filled_total=sem_filled_total+section["ALREADY_FILLED"]
						sem_total=sem_total+section["TOTAL"]
						section["PERCENTAGE_GIVEN_FEEDBACK"]=(section["ALREADY_FILLED"]*100.0)/section["TOTAL"]
						section["PERCENTAGE_GIVEN_FEEDBACK"]=round(section["PERCENTAGE_GIVEN_FEEDBACK"],2)
						section["PERCENTAGE_ELIGIBLE_GIVEN_FEEDBACK"]=(section["ALREADY_FILLED"]*100.0)/(section["TOTAL"]-section["NOT_ELIGIBLE"])
						section["PERCENTAGE_ELIGIBLE_GIVEN_FEEDBACK"]=round(section["PERCENTAGE_ELIGIBLE_GIVEN_FEEDBACK"],2)


				###########################################################################################################

				if sem_total==0:
					sem_given_percentage=0
					sem_eligible_given_percentage=0
				else:
					x=sem_total-sem_eligible_total
					if x == 0 or sem_total == 0:
						sem_given_percentage=0
						sem_eligible_given_percentage=0
					else:
						sem_given_percentage=(sem_filled_total*100.0)/sem_total
						sem_given_percentage=round(sem_given_percentage,2)
						sem_eligible_given_percentage=(sem_filled_total*100.0)/(sem_total-sem_eligible_total)
						sem_eligible_given_percentage=round(sem_eligible_given_percentage,2)
				sem['sections'].append({'section':"TOTAL","NOT_FILLED":sem_not_filled_total,"NOT_ELIGIBLE":sem_eligible_total,"ALREADY_FILLED":sem_filled_total,"TOTAL":sem_total,"PERCENTAGE_GIVEN_FEEDBACK":sem_given_percentage,"PERCENTAGE_ELIGIBLE_GIVEN_FEEDBACK":sem_eligible_given_percentage})
				dept_not_filled_total=dept_not_filled_total+sem_not_filled_total
				dept_eligible_total=dept_eligible_total+sem_eligible_total
				dept_filled_total=dept_filled_total+sem_filled_total
				dept_total=dept_total+sem_total

			#################################################################################################################

			if dept_total==0:
				dept_given_percentage=0
				dept_eligible_given_percentage=0
			else:
				x=dept_total-dept_eligible_total
				if x==0 or dept_total==0:
					dept_given_percentage=0
					dept_eligible_given_percentage=0
				else:
					dept_given_percentage=(dept_filled_total*100.0)/dept_total
					dept_given_percentage=round(dept_given_percentage,2)
					dept_eligible_given_percentage=(dept_filled_total*100.0)/(dept_total-dept_eligible_total)
					dept_eligible_given_percentage=round(dept_eligible_given_percentage,2)
			consolidate[index]['sems'].append({'sem':"TOTAL",'sections':[{'section':dept_count,"NOT_FILLED":dept_not_filled_total,"NOT_ELIGIBLE":dept_eligible_total,"ALREADY_FILLED":dept_filled_total,"TOTAL":dept_total,"PERCENTAGE_GIVEN_FEEDBACK":dept_given_percentage,"PERCENTAGE_ELIGIBLE_GIVEN_FEEDBACK":dept_eligible_given_percentage}]})
			whole_not_filled_total=whole_not_filled_total+dept_not_filled_total
			whole_eligible_total=whole_eligible_total+dept_eligible_total
			whole_filled_total=whole_filled_total+dept_filled_total
			whole_total=whole_total+dept_total

		######################################################################################################################

		if whole_total==0:
			whole_given_percentage=0
			whole_eligible_given_percentage=0
		else:
			x=whole_total-whole_eligible_total
			if x==0 or whole_total==0:
				whole_given_percentage=0
				whole_eligible_given_percentage=0
			else:
				whole_given_percentage=(whole_filled_total*100.0)/whole_total
				whole_given_percentage=round(whole_given_percentage,2)
				whole_eligible_given_percentage=(whole_filled_total*100.0)/(whole_total-whole_eligible_total)
				whole_eligible_given_percentage=round(whole_eligible_given_percentage,2)
		consolidate.append({'dept':"TOTAL","COUNT":whole_count,"NOT_FILLED":whole_not_filled_total,"NOT_ELIGIBLE":whole_eligible_total,"ALREADY_FILLED":whole_filled_total,"TOTAL":whole_total,"PERCENTAGE_GIVEN_FEEDBACK":whole_given_percentage,"PERCENTAGE_ELIGIBLE_GIVEN_FEEDBACK":whole_eligible_given_percentage})

		data={'consolidate':consolidate,'list_detail':student_list}
		status=statusCodes.STATUS_SUCCESS
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data,status)

def ViewInstituteAttributeReport(request):
	data_values={}
	if (requestMethod.POST_REQUEST(request)):
		sem_type=request.session['sem_type']
		data=json.loads(request.body)

		session_name=request.session['Session_name']
		StuFeedbackMarks=generate_session_table_name("StuFeedbackMarks_",session_name)
		StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)

		consolidate=[]
		student_list=[]
		temp_all_dept_list=[]
		temp_all_sem_list=[]
		temp_all_section_list=[]

		'''SECTION GATHERING'''
		section_list=list(Sections.objects.filter(sem_id__sem__in=data['semester'],section__in=data['section'],dept__in=data['dept']).values_list('section_id',flat=True))

		'''DATA GATHERING'''
		data_set=list(StuFeedbackMarks.objects.filter(feedback_id__feedback_id__uniq_id__section__in=section_list,feedback_id__feedback_id__status="INSERT",attribute__subject_type__isnull=True,attribute__eligible_settings_id__status="INSERT")
			.values(
				"feedback_id__feedback_id__uniq_id",
				"feedback_id__feedback_id__uniq_id__section__dept__course__value",
				"feedback_id__feedback_id__uniq_id__section__dept__dept__value",
				"feedback_id__feedback_id__uniq_id__section__dept__course",
				"feedback_id__feedback_id__uniq_id__section__sem_id__sem",
				"feedback_id__feedback_id__uniq_id__section__section",
				"feedback_id__feedback_id__attendance_per",
				"attribute",
				"attribute__name",
				"attribute__eligible_settings_id__sem",
				"attribute__eligible_settings_id__sem__sem",
				"attribute__min_marks",
				"attribute__max_marks",
				"attribute__gender__value",
				"attribute__residential_status",
				"marks"
				)
			.annotate(cal_marks=Round((F("marks"))*10/(F("attribute__max_marks"))))
			.order_by(
				"feedback_id__feedback_id__uniq_id__section__dept__course__value",
				"feedback_id__feedback_id__uniq_id__section__dept__dept__value",
				"feedback_id__feedback_id__uniq_id__section__sem_id__sem",
				"feedback_id__feedback_id__uniq_id__section__section",
				"attribute__name"
				)
		)
		student_counter=-1
		# '''COURSE LOOP'''
		if not len(data_set)>0:
			status=statusCodes.STATUS_CONFLICT_WITH_MESSAGE
			return RESPONSE(statusMessages.CUSTOM_MESSAGE("No Data Found"),status)
		overall_institute={}

		'''DEPARTMENT ATTRIBUTE GATHERING'''
		per_institute_attributes=list(StuFeedbackAttributes.objects.filter(subject_type__isnull=True).exclude(eligible_settings_id__status="DELETE").values('name').distinct())
		per_institute_attribute_ids=dict()
		for attribute in  per_institute_attributes:
			per_institute_attribute_ids[attribute['name']]=attribute
		'''DEPARTMENT ATTRIBUTE GATHERING END'''

		for course_sno,(course_name,course_group) in enumerate(groupby(data_set,key=lambda group_course:group_course['feedback_id__feedback_id__uniq_id__section__dept__course__value'])):
			temp_course=list(course_group)
			overall_course={}
			consolidate.append({"course":course_name,'depts':[]})

			'''DEPARTMENT ATTRIBUTE GATHERING'''
			per_course_attributes=list(StuFeedbackAttributes.objects.filter(eligible_settings_id__sem__dept__course__value=course_name,subject_type__isnull=True).exclude(eligible_settings_id__status="DELETE").values('name').distinct())
			per_course_attribute_ids={}
			for attribute in  per_course_attributes:
				per_course_attribute_ids[attribute['name']]=attribute
			'''DEPARTMENT ATTRIBUTE GATHERING END'''


			''' DEFAULT VALUE START '''
			course_selected=temp_course[0]['feedback_id__feedback_id__uniq_id__section__dept__course']
			'''FOR  DEPT'''
			temp_all_dept_list=list(CourseDetail.objects.filter(uid__in=data['dept'],course=course_selected).values_list("dept_id__value",flat=True).order_by("dept_id__value"))
			for dept_sno,dept_name in enumerate(temp_all_dept_list):
				consolidate[course_sno]['depts'].append({'dept_name':dept_name,'sems':[]})

				'''FOR DEFAULT SEM'''####################################################
				temp_all_sem_list=list(StudentSemester.objects.filter(dept_id__course=course_selected,dept_id__dept__value=dept_name,sem__in=data['semester'],dept_id__in=data['dept']).values('sem_id','sem').distinct().order_by('sem'))
				temp_all_sem_list_keys=[]

				for sem_sno,sem in  enumerate(temp_all_sem_list):
					consolidate[course_sno]['depts'][dept_sno]['sems'].append({'sem_id':sem['sem_id'],'sem_name':sem['sem'],'sections':[]})
					temp_all_sem_list_keys.append(sem['sem_id'])
					'''FOR DEFAULT SECTION'''##########################################################
					temp_all_section_list=list(Sections.objects.filter(sem_id=sem['sem_id'],section__in=data['section']).values_list('section',flat=True).order_by('section').distinct())
					per_sem_attributes=list(StuFeedbackAttributes.objects.filter(eligible_settings_id__sem=sem['sem_id'],subject_type__isnull=True).values('name').distinct())
					per_sem_attribute_ids={}
					# '''SECTION LOOP for TEMP "--" '''
					for attribute in  per_sem_attributes:
						per_sem_attribute_ids[attribute['name']]=attribute
					for section_no,section_name in enumerate(temp_all_section_list):
						consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"].append({})
						consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][section_no]['section_name']=section_name
						for atttibute_id in per_sem_attribute_ids:
							consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][section_no][atttibute_id]={"avg":"--","name":per_sem_attribute_ids[atttibute_id]['name']}

			''' DEFAULT VALUE END '''

			# '''DEPARTMENT LOOP'''
			for dept_name,dept_group in groupby(temp_course,key=lambda group_dept:group_dept['feedback_id__feedback_id__uniq_id__section__dept__dept__value']):
				overall_dept={}

				temp_dept=list(dept_group)
				dept_sno=temp_all_dept_list.index(dept_name)


				'''DEPARTMENT ATTRIBUTE GATHERING'''

				per_dept_attributes=list(StuFeedbackAttributes.objects.filter(eligible_settings_id__sem__dept__dept__value=dept_name,subject_type__isnull=True).exclude(eligible_settings_id__status="DELETE").values('name').distinct())
				per_dept_attribute_ids={}
				for attribute in  per_dept_attributes:
					per_dept_attribute_ids[attribute['name']]=attribute
				'''DEPARTMENT ATTRIBUTE GATHERING END'''


				consolidate[course_sno]['depts'][dept_sno]['dept_name']=dept_name

				temp_all_sem_list=list(StudentSemester.objects.filter(dept_id__dept__value=dept_name,dept_id__course=course_selected,sem__in=data['semester'],dept_id__in=data['dept']).values('sem_id','sem').distinct().order_by('sem'))

				temp_all_sem_list_keys=[]

				for sem in temp_all_sem_list:
					temp_all_sem_list_keys.append(sem['sem_id'])

				# '''SEMESTER LOOP'''
				for sem_name,sem_group in groupby(temp_dept,key=lambda group_sem:group_sem['attribute__eligible_settings_id__sem']):
					overall_sem={}
					temp_sem=list(sem_group)
					sem_sno=temp_all_sem_list_keys.index(sem_name)

					# '''ATTRIBUTE DATA GATHERING'''
					per_sem_attributes=list(StuFeedbackAttributes.objects.filter(eligible_settings_id__sem=sem_name,subject_type__isnull=True).exclude(eligible_settings_id__status="DELETE").values('name').distinct())
					per_sem_attribute_ids={}

					for attribute in  per_sem_attributes:
						per_sem_attribute_ids[attribute['name']]=attribute

					consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]['sem_name']=temp_sem[0]["feedback_id__feedback_id__uniq_id__section__sem_id__sem"]
					consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]['sem_id']=sem_name
					consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["attributes"]=per_sem_attribute_ids

					temp_all_section_list=list(Sections.objects.filter(sem_id=sem_name,section__in=data['section']).values_list('section',flat=True).order_by('section').distinct())

					# '''SECTION LOOP'''

					for section_name,section_group in groupby(temp_sem,key=lambda group_section:group_section['feedback_id__feedback_id__uniq_id__section__section']):

						section_sno=temp_all_section_list.index(section_name)
						temp_section=list(section_group)
						attri_keys=set(per_sem_attribute_ids.keys())

						# '''SECTION ATTRIBUTE LOOP'''
						temp_addition=0
						temp_attri_used=0
						for atttibute_id,atttibute_group in groupby(temp_section,key=lambda group_attribute:group_attribute['attribute__name']):
							temp_attri=list(atttibute_group)

							# '''ATTRIBUTE CHEKING'''
							if atttibute_id in attri_keys:
								temp_key=atttibute_id
								attri_keys.discard(atttibute_id)

								# '''ATTRIBUTE ADDITION'''
								temp_attri_total=(sum(list(x['cal_marks'] for x in list(temp_attri))))
								temp_attri_count=len(temp_attri)
								temp_avg=temp_attri_total/temp_attri_count
								if temp_key not in overall_sem:
									overall_sem[temp_key]={}
									overall_sem[temp_key]['cal_marks']=0
									overall_sem[temp_key]['counter']=0
								overall_sem[temp_key]['cal_marks']=overall_sem[temp_key]['cal_marks']+temp_attri_total
								overall_sem[temp_key]['counter']=overall_sem[temp_key]['counter']+temp_attri_count

								consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][section_sno][temp_key]={"avg":temp_avg,"name":per_sem_attribute_ids[atttibute_id]['name']}

								# '''OVERALL SECTION ADDITION'''
								temp_addition=temp_addition+temp_attri_total
								temp_attri_used=temp_attri_used+temp_attri_count
						# overall_sem[temp_key]['cal_marks']=overall_sem[temp_key]['cal_marks']+temp_addition
						# overall_sem[temp_key]['counter']=overall_sem[temp_key]['counter']+temp_attri_used
						consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][section_sno]['overall']={}
						consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][section_sno]['overall']['avg']=temp_addition/temp_attri_used

					temp_addition=0
					temp_attri_used=0
					consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"].append({'section_name':"OVERALL"})
					for attri_name in per_dept_attribute_ids:
						if attri_name in overall_sem:
							if(attri_name not in overall_dept):
								overall_dept[attri_name]={}
								overall_dept[attri_name]['cal_marks']=0
								overall_dept[attri_name]['counter']=0

							if(attri_name in overall_sem):
								overall_dept[attri_name]['cal_marks']=overall_dept[attri_name]['cal_marks']+overall_sem[attri_name]['cal_marks']
								overall_dept[attri_name]['counter']=overall_dept[attri_name]['counter']+overall_sem[attri_name]['counter']
								consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][-1][attri_name]={}
								temp_addition=temp_addition+overall_sem[attri_name]['cal_marks']
								temp_attri_used=temp_attri_used+overall_sem[attri_name]['counter']
								consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][-1][attri_name]['avg']=overall_sem[attri_name]['cal_marks']/overall_sem[attri_name]['counter']
					consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][-1]['overall']={}
					consolidate[course_sno]['depts'][dept_sno]['sems'][sem_sno]["sections"][-1]['overall']['avg']=temp_addition/temp_attri_used


				temp_addition=0
				temp_attri_used=0
				consolidate[course_sno]['depts'][dept_sno]['sems'].append({'sem_name':"OVERALL","sections":[{'section_name':"OVERALL"}]})
				consolidate[course_sno]['depts'][dept_sno]['sems'][-1]['attributes']=per_course_attribute_ids
				for attri_name in per_course_attribute_ids:
					if attri_name in overall_dept:
						if(attri_name not in overall_course):
							overall_course[attri_name]={}
							overall_course[attri_name]['cal_marks']=0
							overall_course[attri_name]['counter']=0

						if(attri_name in overall_dept):
							overall_course[attri_name]['cal_marks']=overall_course[attri_name]['cal_marks']+overall_dept[attri_name]['cal_marks']
							overall_course[attri_name]['counter']=overall_course[attri_name]['counter']+overall_dept[attri_name]['counter']
							temp_addition=temp_addition+overall_dept[attri_name]['cal_marks']
							temp_attri_used=temp_attri_used+overall_dept[attri_name]['counter']
							consolidate[course_sno]['depts'][dept_sno]['sems'][-1]["sections"][-1][attri_name]={}
							consolidate[course_sno]['depts'][dept_sno]['sems'][-1]["sections"][-1][attri_name]['avg']=overall_dept[attri_name]['cal_marks']/overall_dept[attri_name]['counter']
				consolidate[course_sno]['depts'][dept_sno]['sems'][-1]["sections"][-1]['overall']={}
				consolidate[course_sno]['depts'][dept_sno]['sems'][-1]["sections"][-1]['overall']['avg']=temp_addition/temp_attri_used


			consolidate[course_sno]['depts'].append({'dept_name':"OVERALL",'sems':[{'sem_name':"OVERALL","sections":[{'section_name':"OVERALL"}]}]})
			consolidate[course_sno]['depts'][-1]['sems'][-1]['attributes']=per_institute_attribute_ids
			temp_addition=0
			temp_attri_used=0
			for attri_name in per_institute_attribute_ids:
				if attri_name in overall_course:
					if(attri_name not in overall_institute):
						overall_institute[attri_name]={}
						overall_institute[attri_name]['cal_marks']=0
						overall_institute[attri_name]['counter']=0
					if(attri_name in overall_dept):
						overall_institute[attri_name]['cal_marks']=overall_institute[attri_name]['cal_marks']+overall_course[attri_name]['cal_marks']
						overall_institute[attri_name]['counter']=overall_institute[attri_name]['counter']+overall_course[attri_name]['counter']
						temp_addition=temp_addition+overall_course[attri_name]['cal_marks']
						temp_attri_used=temp_attri_used+overall_course[attri_name]['counter']
						consolidate[course_sno]['depts'][-1]['sems'][-1]["sections"][-1][attri_name]={}
						consolidate[course_sno]['depts'][-1]['sems'][-1]["sections"][-1][attri_name]['avg']=overall_course[attri_name]['cal_marks']/overall_course[attri_name]['counter']
			consolidate[course_sno]['depts'][-1]['sems'][-1]["sections"][-1]['overall']={}
			consolidate[course_sno]['depts'][-1]['sems'][-1]["sections"][-1]['overall']['avg']=temp_addition/temp_attri_used

		consolidate.append({'course':"OVERALL",'depts':[{'dept_name':"OVERALL",'sems':[{'sem_name':"OVERALL","sections":[{'section_name':"OVERALL"}]}]}]})
		consolidate[-1]['depts'][-1]['sems'][-1]['attributes']=per_institute_attribute_ids
		temp_addition=0
		temp_attri_used=0
		for attri_name in per_institute_attribute_ids:
			if(attri_name in overall_institute):
				consolidate[-1]['depts'][-1]['sems'][-1]["sections"][-1][attri_name]={}
				consolidate[-1]['depts'][-1]['sems'][-1]["sections"][-1][attri_name]['avg']=overall_institute[attri_name]['cal_marks']/overall_institute[attri_name]['counter']
				temp_addition=temp_addition+overall_institute[attri_name]['cal_marks']
				temp_attri_used=temp_attri_used+overall_institute[attri_name]['counter']
		consolidate[-1]['depts'][-1]['sems'][-1]["sections"][-1]['overall']={}
		consolidate[-1]['depts'][-1]['sems'][-1]["sections"][-1]['overall']['avg']=temp_addition/temp_attri_used

		data_values={"consolidate":consolidate,"student_list":data_set}
		status=statusCodes.STATUS_SUCCESS
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data_values,status)

def AvgFeedback(request):
	data_values={}
	if (requestMethod.POST_REQUEST(request)):
		sem_type=request.session['sem_type']

		session_name=request.session['Session_name']
		StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)

		data=json.loads(request.body)
		data_value=[]
		'''DATA GATHERING'''
		data_value=faculty_feedback_details(data['faculty'],session_name,data['type'])
		per_sem_attributes=list(StuFeedbackAttributes.objects.filter(subject_type__in=data['type']).exclude(subject_type__isnull=True).exclude(eligible_settings_id__status="DELETE").values('name').distinct())
		# '''ATTRIBUTE DATA GATHERING'''
		per_sem_attribute_ids={}
		for attribute in  per_sem_attributes:
			per_sem_attribute_ids[attribute['name']]=attribute
		status=statusCodes.STATUS_SUCCESS
		data_values={'data':data_value,'attribute_list':per_sem_attribute_ids}
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data_values,status)

def ConsolidateReport(request):
	data_values=[]
	if (requestMethod.POST_REQUEST(request)):
		sem_type=request.session['sem_type']
		session_name=request.session['Session_name']
		StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)

		data=json.loads(request.body)
		data_value=[]
		per_attributes=list(StuFeedbackAttributes.objects.filter(subject_type__in=data['type']).exclude(subject_type__isnull=True).exclude(eligible_settings_id__status="DELETE").values('name').distinct())
		per_sem_attribute_ids={}
		for attribute in  per_attributes:
			per_sem_attribute_ids[attribute['name']]=attribute
		data_value=data['faculty']
		data_value=individual_faculty_consolidate(data_value,session_name,data['type'])
		status=statusCodes.STATUS_SUCCESS
		data_values={'data':data_value,'attribute_list':per_sem_attribute_ids}
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data_values,status)

def Feedback_Report_faculty(request):
	data_values={}
	data_values2={}
	if (requestMethod.POST_REQUEST(request)):

		session_name=request.session['Session_name']
		data=json.loads(request.body)
		sem_type=request.session['sem_type']
		emp_id=[]
		emp_id.append(request.session['hash1'])

		if check_islocked('FF', emp_id, session_name)==True:
			data_values={'msg':"Report is locked from DEAN Portal"}
			status=statusCodes.STATUS_CONFLICT_WITH_MESSAGE
			return RESPONSE(data_values,status)
		StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)
		data_value1=[]
		data_value2=[]
		'''DATA GATHERING'''
		data_value1=faculty_feedback_details(emp_id,session_name,data['type'])
		data_values2=individual_faculty_consolidate(emp_id,session_name,data['type'])
		per_sem_attributes=list(StuFeedbackAttributes.objects.filter(subject_type__in=data['type']).exclude(subject_type__isnull=True).exclude(eligible_settings_id__status="DELETE").values('name').distinct())
		# '''ATTRIBUTE DATA GATHERING'''
		per_sem_attribute_ids={}
		for attribute in  per_sem_attributes:
			per_sem_attribute_ids[attribute['name']]=attribute
		status=statusCodes.STATUS_SUCCESS
		data_values={'data':data_value1,'total_data':data_values2,'attribute_list':per_sem_attribute_ids}
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data_values,status)

def Feedback_Report_Faculty_Report(request):
	data_values={}
	if (requestMethod.POST_REQUEST(request)):
		sem_type=request.session['sem_type']

		session_name=request.session['Session_name']
		StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)

		data_json=json.loads(request.body)
		data_value=[]
		'''DATA GATHERING'''
		temp_data_value=faculty_feedback_details(data_json['faculty'],session_name,data_json['type'])
		per_sem_attributes=list(StuFeedbackAttributes.objects.filter(subject_type__in=data_json['type']).exclude(subject_type__isnull=True).values('name').distinct())
		# '''ATTRIBUTE DATA GATHERING'''

		temp_emp_list=[]
		for data in temp_data_value:
			if data['faculty'] not in  temp_emp_list:
				temp_emp_list.append(data['faculty'])
				avg_total=individual_faculty_consolidate([data['faculty'].split('(')[1].split(')')[0]],session_name,data_json['type'])[0]['TOTAL']
				print(avg_total)
				data_value.append({'faculty':data['faculty'],'data':[], 'avg_total':avg_total})
				# data_value.append({'faculty':data['faculty'],'data':[]})
			indexer=temp_emp_list.index(data['faculty'])
			data_value[indexer]['data'].append(data)

		per_sem_attribute_ids={}
		for attribute in  per_sem_attributes:
			per_sem_attribute_ids[attribute['name']]=attribute
		status=statusCodes.STATUS_SUCCESS
		data_values={'data':data_value,'attribute_list':per_sem_attribute_ids}
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data_values,status)
