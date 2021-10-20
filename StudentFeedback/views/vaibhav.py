from __future__ import unicode_literals
from django.shortcuts import render
import datetime
from datetime import datetime,timedelta
from django.utils import timezone
from django.http import HttpResponse,JsonResponse
from django.db.models import Q ,Avg, Count, Subquery, OuterRef
from django.db.models import Count ,Avg, Count, Subquery, OuterRef, F, Value, Func, Case, When, IntegerField, CharField
from django.db.models import Sum
from collections import Counter
from itertools import groupby
import copy

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from erp.constants_functions.functions import *

from Registrar.models import *
from login.models import *
from musterroll.models import EmployeePrimdetail
from StudentFeedback.models import *
from StudentAccounts.models import SubmitFee,RefundFee
from StudentAcademics.models import *

from StudentAcademics.views import get_sub_attendance_type,get_student_subjects,get_student_attendance
from login.views import checkpermission,generate_session_table_name
from StudentAcademics.views import get_course,get_subject_type,get_gender

def AvgFeedback(request):
	session_name=request.session['Session_name']

	FacultyTime = generate_session_table_name("FacultyTime_",session_name)
	StuFeedbackMarks = generate_session_table_name("StuFeedbackMarks_",session_name)

	data_values={}
	if requestMethod.POST_REQUEST(request):
		data = json.loads(request.body)
		# if requestByCheck.requestByDean(data):
		course= data["course"]
		branch = data["dept"]
		semester = data["sem"]
		section = data["section"]
		qry1 = list(FacultyTime.objects.filter(section__dept__course__value__in=course,section__dept__in=branch,section__sem_id__sem__in=semester,section__section__in=section).exclude(emp_id__emp_id__is_active=0).values('emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','emp_id__mob','emp_id__email','emp_id__current_pos__value').distinct())
		for f1 in qry1:
			qry2 = StuFeedbackMarks.objects.filter(feedback_id__emp_id=f1['emp_id']).exclude(feedback_id__feedback_id__status='DELETE').values('attribute__name').distinct()
			f1['data'] = 0
			f1['total'] = 0
			f1['no_stu'] = 0
			if qry2:
				qry4 = StuFeedbackMarks.objects.filter(feedback_id__emp_id=f1['emp_id']).exclude(feedback_id__feedback_id__status='DELETE').values('feedback_id__feedback_id__status')
				no_stu=len(qry4)
				row=[]
				avg=0.0
				i=0.0
				round_avg=0.0
				for f2 in qry2:
					qry7 = StuFeedbackMarks.objects.filter(feedback_id__emp_id=f1['emp_id'],attribute__name=f2['attribute__name']).aggregate(Avg('marks'))
					qry3 = StuFeedbackMarks.objects.filter(feedback_id__emp_id=f1['emp_id'],attribute__name=f2['attribute__name']).values('attribute__min_marks','attribute__max_marks').distinct()

					round_avg=round(qry7['marks__avg'],2)
					avg=avg+qry7['marks__avg']
					i=i+1.0
					row.append({'att': f2['attribute__name'],'avg':round_avg,'min_marks':qry3[0]['attribute__min_marks'],'max_marks':qry3[0]['attribute__max_marks']})
				avg=avg/i
				round_avg=round(avg,2)
				f1['data']=row
				f1['total']=round_avg
				f1['no_stu']=no_stu
		data_values=list(qry1)
		status=statusCodes.STATUS_SUCCESS
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return functions.RESPONSE(data_values,status)


'''def ConsolidateReport(request):
	data_values={}
	if requestMethod.POST_REQUEST(request):
		data = json.loads(request.body)
		# if requestByCheck.requestByDean(data):

		course= data["course"]
		branch = data["dept"]
		qry = list(FacultyTime_1819o.objects.filter(section__dept__course__value__in=course,section__dept__in=branch).exclude(emp_id__emp_id__is_active=0).values('emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','emp_id__mob','emp_id__email','emp_id__current_pos__value').distinct())
		#############################################TO FIND AVERAGE OF EACH SECTION##############################################
		for f in qry:
			qry1 = list(FacultyTime_1819o.objects.filter(emp_id=f['emp_id']).exclude(status='DELETE').values('section__section_id','section__section','section__dept__dept__value','subject_id__sub_alpha_code','subject_id__sub_num_code','subject_id__sub_name','section__sem_id__sem').distinct())
			data=[]
			for f1 in qry1:
				#########################   TO FIND NUMBER OF STUDENTS IN A SECTION   ######################################
				qry2 = studentSession_1819o.objects.filter(section__section_id=f1['section__section_id']).exclude(uniq_id__in=studentSession_1819o.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") |  Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id',flat=True)).values('uniq_id')
				no_of_student_in_class = len(qry2)
				############################################################################################################
				#######################   TO FIND NUMBER OF STUDENTS GIVEN FEEDBACK   ######################################
				no_of_student_given_feedback = 0
				for x in qry2:
					qry3 = StuFeedback_1819o.objects.filter(uniq_id=x['uniq_id'],status='INSERT')
					no_of_student_given_feedback = no_of_student_given_feedback + 1
				#############################################################################################################
				qry4 = StuFeedbackMarks_1819o.objects.filter(feedback_id__emp_id=f['emp_id']).exclude(feedback_id__feedback_id__status='DELETE').values('attribute__name').distinct()
				if qry4:
					row1=[]
					avg=0.0
					i=0.0
					c=0
					round_avg=0.0
					for f2 in qry4:
						qry5 = StuFeedbackMarks_1819o.objects.filter(feedback_id__emp_id=f['emp_id'],attribute__name=f2['attribute__name'],feedback_id__feedback_id__uniq_id__section__section_id=f1['section__section_id']).values('attribute__min_marks','attribute__max_marks').distinct()
						qry8 = StuFeedbackMarks_1819o.objects.filter(feedback_id__emp_id=f['emp_id'],attribute__name=f2['attribute__name'],feedback_id__feedback_id__uniq_id__section__section_id=f1['section__section_id']).aggregate(Avg('marks'))
						if qry8['marks__avg'] is not None:
							round_avg=round(qry8['marks__avg'],2)
							avg=avg+qry8['marks__avg']
							i=i+1.0
							row1.append({'att': f2['attribute__name'],'avg':round_avg,'min_marks':qry5[0]['attribute__min_marks'],'max_marks':qry5[0]['attribute__max_marks']})
						else:
							avg=avg+0.0
							i=i+1.0
							c=1
							row1.append({'att': f2['attribute__name'],'avg':"--",'min_marks':"--",'max_marks':"--"})
					avg=avg/i
					if c==0:
						round_avg=round(avg,2)
					else:
						round_avg="--"
					data.append({'avg_of_section':row1,'total_avg_of_section':round_avg,'no_of_student_in_class':no_of_student_in_class,'no_of_student_given_feedback':no_of_student_given_feedback,'dept':f1['section__dept__dept__value'],'sem':f1['section__sem_id__sem'],'section':f1['section__section'],'subject':f1['subject_id__sub_name'],'sub_num_code':f1['subject_id__sub_num_code'],'sub_alpha_code':f1['subject_id__sub_alpha_code']})
					f['section']=data
		#############################################################################################################################
		####################################################TO FIND TOTAL AVERAGE####################################################
		for f in qry:
			qry1 = list(FacultyTime_1819o.objects.filter(emp_id=f['emp_id']).exclude(status='DELETE').values('section__section_id','section__section','section__dept__dept__value','subject_id__sub_alpha_code','subject_id__sub_num_code','subject_id__sub_name','section__sem_id__sem').distinct())
			for f3 in qry1:
				qry6 = StuFeedbackMarks_1819o.objects.filter(feedback_id__emp_id=f['emp_id']).exclude(feedback_id__feedback_id__status='DELETE').values('attribute__name').distinct()
				if qry6:
					row2=[]
					avg=0.0
					i=0.0
					round_avg=0.0
					for f4 in qry6:
						qry7 = StuFeedbackMarks_1819o.objects.filter(feedback_id__emp_id=f['emp_id'],attribute__name=f4['attribute__name']).aggregate(Avg('marks'))
						avg=avg+qry7['marks__avg']
						round_avg=round(qry7['marks__avg'],2)
						i=i+1.0
						row2.append({'att': f4['attribute__name'],'avg':round_avg})
					avg=avg/i
					round_avg=round(avg,2)
					f['avg']=row2
					f['total_avg']=round_avg
		################################################################################################################################
		data_values=list(qry)
		status=statusCodes.STATUS_SUCCESS
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return functions.RESPONSE(data_values,status)'''

def ConsolidateReport(request):
	session_name=request.session['Session_name']

	StuFeedbackRemark = generate_session_table_name("StuFeedbackRemark_",session_name)

	data_values={}
	if requestMethod.POST_REQUEST(request):
		data = json.loads(request.body)
		# if requestByCheck.requestByDean(data):
		course= data["course"]
		dept = data["dept"]
		qry = StuFeedbackRemark.objects.filter(subject__sem__dept__course=course,subject__sem__dept=dept).exclude().values('subject__uniq_id__section__section_id','subject__uniq_id__section__section','subject__uniq_id__section__dept','subject__uniq_id__section__dept__course').distinct()
