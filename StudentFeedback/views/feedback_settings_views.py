from django.shortcuts import render

import datetime
from datetime import datetime,timedelta
from django.utils import timezone
from django.http import HttpResponse,JsonResponse
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Avg, Count, Subquery, OuterRef, F, Value, Func, Case, When, IntegerField, CharField
from collections import Counter

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from StudentMMS.constants_functions import requestType

from Registrar.models import *
from StudentFeedback.models import *
from StudentAccounts.models import SubmitFee,RefundFee
from StudentAcademics.models import *
from musterroll.models import EmployeePrimdetail
from Registrar.models import StudentSemester,StudentDropdown,Sections,CourseDetail

from login.views import generate_session_table_name
from StudentAcademics.views import check_islocked,get_sub_attendance_type,get_student_subjects,get_attendance_type,get_student_attendance,get_semester,get_section,get_section_students,get_filtered_emps
from erp.constants_functions.functions import *
from login.views import checkpermission
from StudentFeedback.views.feedback_function_views import check_is_portal_locked,get_attribute,studentDetailNstatus,student_residency,getSection,check_islocked_faculty
from StudentAcademics.views import get_course,get_subject_type,get_gender, get_organization, get_emp_category, get_department




def feedback_settings_data(request):
	data={};
	data['subject_type']=get_subject_type()
	data['gender']=get_gender()
	return RESPONSE(data,200)

def submit_settings(request):
	data=json.loads(request.body)
	session_name=request.session['Session_name']
	StuFeedbackEligibility=generate_session_table_name("StuFeedbackEligibility_",session_name)
	StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)
	eligible_percent=data['eligible_percent']
	dept=data['dept']
	# sub_type=data['type']
	sem=data['sem']
	attrs=data['attrs']
	sem_ids=list()
	qry=StudentSemester.objects.filter(sem__in=sem,dept__in=dept).values_list('sem_id',flat=True)
	sem_ids=qry
	#######################LOCKING STARTS######################
	section_li=list(Sections.objects.filter(sem_id__in=sem_ids).values_list('section_id',flat=True))
	print(section_li)
	if check_islocked("FEED",section_li,session_name):
		return RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
		####################LOCKING ENDS##############################

	flag_institute=False
	# if  None in sub_type:
	#   flag_institute=True
	#   sub_type.remove(None)

	############ OTHER SUBJECT TYPE #####################
	#setting_update=StuFeedbackEligibility.objects.filter(sem__in=sem_ids).update(status="DELETE")
	# exclude_sem = StuFeedbackEligibility.objects.filter(sem__in=sem_ids).exclude(status__contains='DELETE').values_list('sem',flat=True)
	# new_sem_id = list(set(sem_ids)-set(exclude_sem))

	# setting_objs=(StuFeedbackEligibility(sem=StudentSemester.objects.get(sem_id=sem),eligible_att_per=eligible_percent,added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))for sem in new_sem_id)
	# setting_insert=StuFeedbackEligibility.objects.bulk_create(setting_objs)

	for sem in sem_ids:
		q_check = StuFeedbackEligibility.objects.filter(sem=sem).exclude(status__contains='DELETE').values('id')
		if len(q_check)>0:
			StuFeedbackEligibility.objects.filter(sem=sem).exclude(status__contains='DELETE').update(eligible_att_per=eligible_percent)
		else:
			StuFeedbackEligibility.objects.exclude(status__contains='DELETE').create(sem=StudentSemester.objects.get(sem_id=sem),eligible_att_per=eligible_percent,added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))

	setting_ids=StuFeedbackEligibility.objects.filter(sem__in=sem_ids,status="INSERT").exclude(status__contains="DELETE").values_list('id',flat=True)
	attr_objs=[]
	for sett_id in setting_ids:
		for att in attrs:
			for g_id in att['gender']:
				for res in att['resident']:
					for sub in att['type']:
						if sub is None:
							attr_objs.append(StuFeedbackAttributes(name=att['name'],eligible_settings_id=StuFeedbackEligibility.objects.get(id=sett_id),residential_status=res,gender=StudentDropdown.objects.get(sno=g_id),min_marks=att['min'],max_marks=att['max']))
						else:
							attr_objs.append(StuFeedbackAttributes(name=att['name'],eligible_settings_id=StuFeedbackEligibility.objects.get(id=sett_id),residential_status=res,gender=StudentDropdown.objects.get(sno=g_id),min_marks=att['min'],max_marks=att['max'],subject_type=StudentDropdown.objects.get(sno=sub)))
	attrs_insert=StuFeedbackAttributes.objects.bulk_create(attr_objs)

	# ############### INSTITUTE TYPE ######################
	# if flag_institute:

	#   setting_ids_ins=StuFeedbackEligibility.objects.filter(sem__in=sem_ids,status="INSERT").exclude(status__contains="DELETE").values_list('id',flat=True)

	#   attr_objs_ins=(StuFeedbackAttributes(name=att['name'],eligible_settings_id=StuFeedbackEligibility.objects.get(id=sett_id_ins),residential_status=res,gender=StudentDropdown.objects.get(sno=g_id),min_marks=att['min'],max_marks=att['max'])for sett_id_ins in setting_ids_ins for att in attrs  for g_id in att['gender'] for res in att['resident'])
	#   attrs_insert_ins=StuFeedbackAttributes.objects.bulk_create(attr_objs_ins)

	msg="Successfully Updated Settings"
	response={"msg":msg}
	return RESPONSE(response,200)

def submit_feedback(request):
	# data=LOAD_DATA(request.body)
	data=json.loads(request.body)
	session_name=request.session['Session_name']
	uniq_id=request.session['uniq_id']
	StuFeedback=generate_session_table_name("StuFeedback_",session_name)
	StuFeedbackMarks=generate_session_table_name("StuFeedbackMarks_",session_name)
	StuFeedbackRemark=generate_session_table_name("StuFeedbackRemark_",session_name)
	StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)
	studentSession=generate_session_table_name("studentSession_",session_name)
	qry_section_id = studentSession.objects.filter(uniq_id=uniq_id).values('section_id')
	check_locked = check_islocked("F",[qry_section_id[0]['section_id']],session_name)
	if check_locked:
		msg=statusMessages.MESSAGE_PORTAL_LOCKED
		msg['openable']=False
		return RESPONSE(msg,statusCodes.STATUS_SUCCESS)

	''' #CHECKING ANY PREVIOUS ENTRY# '''


	check_already_filled=list(StuFeedback.objects.filter(uniq_id=uniq_id,status="INSERT",locked="Y").values())

	if len(check_already_filled)>0:
		return RESPONSE(statusMessages.MESSAGE_ALREADY_FILLED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

	else:
		checking_already_filled_Marks=StuFeedbackMarks.objects.filter(feedback_id__feedback_id__uniq_id=uniq_id).values()
		checking_already_filled_Remark=StuFeedbackRemark.objects.filter(feedback_id__uniq_id=uniq_id).values()

		if(len(checking_already_filled_Marks)>0 or len(checking_already_filled_Remark)>0):
			StuFeedbackMarks.objects.filter(feedback_id__feedback_id__uniq_id=uniq_id).delete()
			StuFeedbackRemark.objects.filter(feedback_id__uniq_id=uniq_id).update(remark=None)

		for subject_type in data:
			del data[subject_type]["name"]
			del data[subject_type]["sno"]

		bulk_marks=(StuFeedbackMarks(feedback_id=StuFeedbackRemark.objects.get(id=data[subject_type][fac_stu]['id']),attribute=StuFeedbackAttributes.objects.get(id=marks['id']),marks=marks['marks'] )for subject_type in data for fac_stu in data[subject_type] for marks in data[subject_type][fac_stu]['attributes'])
		StuFeedbackMarks.objects.bulk_create(bulk_marks)

		for subject_type in data:
			for fac_stu in data[subject_type]:
				StuFeedbackRemark.objects.filter(id=data[subject_type][fac_stu]['id']).update(remark=data[subject_type][fac_stu]['remark'])


		StuFeedback.objects.filter(uniq_id=uniq_id,status="INSERT").update(locked="Y")

		msg="Successfully Updated setting_ids"

		response={"msg":msg}

		return RESPONSE(response,statusCodes.STATUS_SUCCESS)

''' #GET COMPLETE FEEDBACK FORM OF STUDENT# '''
def student_feedform_data(request):
	if requestMethod.GET_REQUEST(request):
		session_name=request.session['Session_name']
		session_id=request.session['Session_id']

		SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)
		StuFeedback=generate_session_table_name("StuFeedback_",session_name)
		StuFeedbackRemark=generate_session_table_name("StuFeedbackRemark_",session_name)
		studentSession=generate_session_table_name("studentSession_",session_name)
		StudentAttStatus=generate_session_table_name("StudentAttStatus_",session_name)
		StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)

		status=statusCodes.STATUS_SUCCESS

		uniq_id=request.session['uniq_id']

		################## CHECK IF PORTAL IS LOCKED OR NOT ############

		qry_section_id = studentSession.objects.filter(uniq_id=uniq_id).values('section_id')

		check_locked = check_islocked("F",[qry_section_id[0]['section_id']],session_name)
		if check_locked:
			msg=statusMessages.MESSAGE_PORTAL_LOCKED
			msg['openable']=False
			return RESPONSE(msg,statusCodes.STATUS_SUCCESS)

		check_locked = check_is_portal_locked(qry_section_id[0]['section_id'],session_name)

		att_to_date = datetime.strptime(str(check_locked['time_stamp']).split(" ")[0], '%Y-%m-%d').date()

		studentDetail=studentDetailNstatus(request,uniq_id,att_to_date,session_name,session_id)
		checkStatus=studentDetail["status"]
		################## CHECK IF ALREADY GIVEN FEEDBACK ###################
		if checkStatus=="ALREADY_FILLED":
			msg=statusMessages.CUSTOM_MESSAGE("You have filled your feedback form")
			msg['openable']=False
			return RESPONSE(msg,statusCodes.STATUS_SUCCESS)

		################## CHECK IF NOT ELIGIBLE #######################

		if studentDetail['current_percent'] < studentDetail['eligible_percent'][0]['eligible_att_per']:
			log_record=StuFeedback.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),status='DELETE',attendance_per=studentDetail['current_percent'],locked="N")
			msg=statusMessages.CUSTOM_MESSAGE("You are not eliglible to give feedback since your attendance is less than "+str(studentDetail['eligible_percent'][0]['eligible_att_per']))
			msg['openable']=False
			return RESPONSE(msg,statusCodes.STATUS_SUCCESS)

		else:
			StuFeedback.objects.filter(uniq_id=uniq_id).update(status="DELETE")

			################## CHECK IF ELIGIBLE #######################
			msg={"msg":"Eligible for Feedback."}
			################ SEND STUDENT DATA #######################

			stu_details=studentSession.objects.filter(uniq_id=uniq_id).values('sem','uniq_id__gender')
			data={}
			gen=stu_details[0]['uniq_id__gender']
			res_status=student_residency(request,uniq_id)

			############################## ADD STUDENT ###########################

			student=StuFeedback.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),attendance_per=studentDetail['current_percent'],locked="N")

			############################## ADD OTHER THAN ACADEMICS ATTRIBUTE ###########################

			StuFeedbackRemark.objects.create(feedback_id=StuFeedback.objects.get(id=student.pk))

			########################## SEND FACULTY NAMES ################################
			faculty_list=list()

			i=0

			for sub in studentDetail['subjects'][:-1]:
				fac=StudentAttStatus.objects.filter(uniq_id=uniq_id,att_id__date__lte=att_to_date,att_id__subject_id=sub['id']).exclude(status__contains='DELETE').exclude(status__contains='DELETE').exclude(att_id__emp_id__emp_status='SEPARATE').values('att_id__emp_id','att_id__emp_id__name').annotate(total=Count('att_id')).order_by('-total')

				if len(fac)>0:
					faculty_list.append({'emp_id':fac[0]['att_id__emp_id'],'emp_name':fac[0]['att_id__emp_id__name'],'sub_details':sub,'total_lectures':fac[0]['total']})
			bulk_query=(StuFeedbackRemark(feedback_id=StuFeedback.objects.get(id=student.pk),emp_id=EmployeePrimdetail.objects.get(emp_id=subject['emp_id']),subject=SubjectInfo.objects.get(id=subject['sub_details']['id']),total_lectures=subject['total_lectures']) for subject in faculty_list)
			StuFeedbackRemark.objects.bulk_create(bulk_query)


			################ SEND ATTRIBUTE DATA #######################

			subject_typing=get_subject_type()
			subject_typing.append( {'sno': None, 'value': 'INSTITUTE'})

			attri_data=StuFeedbackAttributes.objects.filter(residential_status=res_status,gender=gen,eligible_settings_id__sem=stu_details[0]['sem'],eligible_settings_id__status="INSERT",eligible_settings_id__eligible_att_per__lte=studentDetail['current_percent']).exclude(eligible_settings_id__status__contains="DELETE").values('subject_type','id','name','min_marks','max_marks').order_by("subject_type").distinct()
			stu_data=StuFeedbackRemark.objects.filter(feedback_id__uniq_id=uniq_id,feedback_id__status="INSERT").values('subject__sub_name','subject__sub_alpha_code', 'subject__sub_num_code','subject__subject_type','id','subject__subject_type__value','emp_id__name','emp_id__desg__value').order_by("subject__subject_type").distinct()
			data_values={}
			for sno,x in enumerate(subject_typing):
				data_values[sno]={'name':x['value'],'sno':x['sno']}
				index=0
				for y in stu_data:
					if x['sno']==y['subject__subject_type']:
						data_values[sno][index]=y
						data_values[sno][index]['attributes']=[]
						flag=0

						for z in attri_data:
							if x['sno']==z['subject_type']:
								data_values[sno][index]['attributes'].append(z)
								flag=1
						if(flag==0):
							del data_values[sno][index]
						else:
							index=index+1
				if(index==0):
					del data_values[sno]
			if data_values == {}:
				if studentDetail['current_percent'] < studentDetail['eligible_percent'][0]['eligible_att_per']:
					log_record=StuFeedback.objects.filter(id=student.pk).update(status='DELETE',attendance_per=current_percent,locked="N")
					msg=statusMessages.CUSTOM_MESSAGE("You are not eliglible to give feedback since your attendance is less than "+str(studentDetail['eligible_percent'][0]['eligible_att_per']))
					print(msg)
					msg['openable']=False
					return RESPONSE(msg,statusCodes.STATUS_SUCCESS)
				else:
					msg=statusMessages.CUSTOM_MESSAGE("You are not eliglible to give feedback since your attendance is less than "+str(studentDetail['eligible_percent'][0]['eligible_att_per']))
					print(msg)
					msg['openable']=False
					return RESPONSE(statusMessages.MESSAGE_DATA_NOT_FOUND,statusCodes.STATUS_SUCCESS)
			data={"data":data_values}
			data['openable']=True

			return RESPONSE(data,statusCodes.STATUS_SUCCESS)
	else:
		return RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

def ViewPreviousAttrbute(request):
	data_values={}
	if (requestMethod.GET_REQUEST(request)):
		if requestByCheck.requestByDean(request.GET):
			session_name=request.session['Session_name']

			StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)

			qry1 = list(StuFeedbackAttributes.objects.filter(eligible_settings_id__status="INSERT").exclude(eligible_settings_id__status="DELETE").values('id','name','residential_status','gender__value','min_marks','max_marks','subject_type__value','eligible_settings_id','eligible_settings_id__id','eligible_settings_id__sem__sem','eligible_settings_id__sem__dept__dept__value','eligible_settings_id__sem__dept__course__value','eligible_settings_id__eligible_att_per','eligible_settings_id__status').order_by('-id').distinct())
			# .annotate(domain=Case(When(subject_type__value__isnull=True, then=F("INSTITUTE")),output_field=CharField()))
			data_values=qry1
			status=statusCodes.STATUS_SUCCESS
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data_values,status)

def AttributeDelete(request):
	data_values={}
	if (requestMethod.DELETE_REQUEST(request)):
		data = json.loads(request.body)
		session_name=request.session['Session_name']

		StuFeedbackAttributes=generate_session_table_name("StuFeedbackAttributes_",session_name)
		StuFeedbackEligibility=generate_session_table_name("StuFeedbackEligibility_",session_name)

		#######################LOCKING STARTS######################
		section_li=Sections.objects.filter(sem_id__in=list(StuFeedbackAttributes.objects.filter(id__in=data['id']).values_list('eligible_settings_id__sem',flat=True))).values_list('section_id',flat=True)
		if check_islocked("FEED",section_li,session_name):
			return RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
			####################LOCKING ENDS##############################

		eligible_settings_id=StuFeedbackAttributes.objects.filter(id__in=data['id']).values('eligible_settings_id')
		len_list=len(eligible_settings_id)
		if(len_list>0):
			for f in eligible_settings_id:
				checker=StuFeedbackEligibility.objects.filter(id=f['eligible_settings_id'],status="INSERT").update(status="DELETE")
				if checker == 1:
					to_be_copy_eligibility=list(StuFeedbackEligibility.objects.filter(id=f['eligible_settings_id']).values())[0]
					new_row=StuFeedbackEligibility.objects.create(sem=StudentSemester.objects.get(sem_id=to_be_copy_eligibility['sem_id']),eligible_att_per=to_be_copy_eligibility['eligible_att_per'],added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),status="INSERT")
					to_be_copy=list(StuFeedbackAttributes.objects.filter(eligible_settings_id__id=f['eligible_settings_id']).exclude(id__in=data['id']).values())
					bulk_new_row=[]
					for x in to_be_copy:
						if(x['subject_type_id'] is None):
							bulk_new_row.append(StuFeedbackAttributes(name=x['name'],eligible_settings_id=StuFeedbackEligibility.objects.get(id=new_row.pk),residential_status=x['residential_status'],gender=StudentDropdown.objects.get(sno=x['gender_id']),min_marks=x['min_marks'],max_marks=x['max_marks']))
						else:
							bulk_new_row.append(StuFeedbackAttributes(subject_type=StudentDropdown.objects.get(sno=x['subject_type_id']),name=x['name'],eligible_settings_id=StuFeedbackEligibility.objects.get(id=new_row.pk),residential_status=x['residential_status'],gender=StudentDropdown.objects.get(sno=x['gender_id']),min_marks=x['min_marks'],max_marks=x['max_marks']))
					StuFeedbackAttributes.objects.bulk_create(bulk_new_row)
		data_values=statusMessages.CUSTOM_MESSAGE("DELETED SUCCESSFULLY")
		status=statusCodes.STATUS_SUCCESS
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data_values,status)

def GetDeptFaculty(request):
	data_values={}
	if (requestMethod.POST_REQUEST(request)):
		data = json.loads(request.body)
		dept_list=list(CourseDetail.objects.filter(uid__in=data['dept']).values_list('dept',flat=True))
		if "965" in data['dept']:
			dept_list=['965']
		print(dept_list)
		dept_string=",".join(str(x) for x in dept_list)
		print(dept_string)
		data_value=get_filtered_emps(dept_string)
		data_values=data_value
		status=statusCodes.STATUS_SUCCESS
	else:
		status=statusCodes.STATUS_BAD_GATEWAY
	return RESPONSE(data_values,status)

def FeedbackFaculty(request):
	print('hi,feedback')
	session_name = request.session['Session_name']
	session_id=request.session['Session_id']
	if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
		LockingUnlocking= generate_session_table_name('LockingUnlocking_',session_name)
		if requestMethod.POST_REQUEST(request):
			data = json.loads(request.body)
			print(data)
			emp_id = data['emp_id']
			unlock_type = data['unlock_type']
			from_date = data['from_date_time']
			to_date = data['to_date_time']

			for x in emp_id:
				insert_new=LockingUnlocking.objects.create(session=Semtiming.objects.get(uid=session_id),lock_type=unlock_type,emp_id=EmployeePrimdetail.objects.get(emp_id=x),unlock_from=from_date,unlock_to=to_date)

			return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)

		elif requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET, 'view_previous')):
				final_data=[]
				for lock in ["FF","FS"]:
					key_lock =[]
					key_lock.append(lock)
					emp_id_list = list(LockingUnlocking.objects.filter(lock_type__in=key_lock).distinct().values_list('emp_id',flat=True))
					all_data=[]

					for x in emp_id_list:
						current_data=list(LockingUnlocking.objects.filter(session=session_id,lock_type__in=key_lock,emp_id=x).values('emp_id','unlock_from','unlock_to','lock_type').order_by('-time_stamp'))
						current_data = current_data[0]
						all_data.append(current_data)

					length=len(all_data)
					for y in range(length):
						emp_name = list(EmployeePrimdetail.objects.filter(emp_id=all_data[y]['emp_id']).values('name','dept__value'))
						all_data[y]['emp_name']=emp_name[0]['name']
						all_data[y]['department']=emp_name[0]['dept__value']
						# status = islock(all_data[y]['unlock_from'],all_data[y]['unlock_to'])
						status=check_islocked_faculty(all_data[y]['lock_type'],[all_data[y]['emp_id']],session_name)
						final_status = "LOCKED"
						if status==False:
							final_status="UNLOCKED"
						all_data[y]['status']=final_status
					final_data.extend(all_data)
				return functions.RESPONSE(final_data, statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET, 'form_data')):
				print('hello')
				unlock_type = []
				data_values = {}
				unlock_type.append({'sno': 'FF', 'value': 'FACULTY_FEEDBACK'})
				organization = get_organization()
				employeecategory = get_emp_category()
				data_values = {'organization': organization, 'unlock_type': unlock_type, 'employeecategory': employeecategory}
				return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)