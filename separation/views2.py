from separation.models import NoDuesHead,EmployeeSeparation,NoDuesEmp,SeparationApplication,SeparationLevelApproval,SeparationExitQuestionPaper,SeparationQuestions,SeparationResponse,SeparationAnswers
from .separation_function_views import get_reporting_employees_applications,get_reporting_to_levels,check_for_level_increment,add_next_level_pending
from erp.constants_functions import requestMethod,functions
from musterroll.models import Reporting,Roles
from StudentMMS.constants_functions import requestType
from erp.constants_variables import statusCodes, statusMessages
from login.views import check,checkpermission
from login.models import EmployeePrimdetail,EmployeeDropdown,AuthUser
from itertools import groupby
import json
from django.db.models import F

def apply_separation(request): #[Apply Seperation Form] in Employee Seperation
	if request.user.is_authenticated:
		check=checkpermission(request,[337])
		emp_id=request.session['hash1']
		if check==200:
			resign_data=[]
			leave_data=[]
			if requestMethod.GET_REQUEST(request):
				if "request_type" in request.GET:
					if(requestType.custom_request_type(request.GET,'type')):####Dropdown 1 [Types of Separation]####
						qry=EmployeeDropdown.objects.filter(field="SEPARATION").exclude(value__isnull=True).values('sno','value')
						data={'data':list(qry)}
						status = statusCodes.STATUS_SUCCESS

					elif(requestType.custom_request_type(request.GET,'leave')):####Dropdown 2 [Types of Long Leave] ####
						qry=EmployeeDropdown.objects.filter(field='LONG LEAVE').exclude(value__isnull=True).values('sno','value')
						data={'data':list(qry)}
						status = statusCodes.STATUS_SUCCESS

					elif(requestType.custom_request_type(request.GET,'view_previous')): ####View Previous at Employee's end ####
						q1=list(SeparationApplication.objects.filter(emp_id=emp_id).exclude(status="DELETE").values_list('id',flat=True))
						qry=SeparationLevelApproval.objects.filter(form_id__in=q1).exclude(status="DELETE").values('id','approved_by__name','approval_status','level','approved_by','form_id','approved_by__dept__value')
						data={'data':list(qry)}
						status = statusCodes.STATUS_SUCCESS

					else:
						data = statusMessages.MESSAGE_NOT_FOUND
						status = statusCodes.STATUS_SUCCESS


				
				else:
					qry1=SeparationApplication.objects.filter(separation_type__value='RESIGN',emp_id=emp_id).extra(select={"relieving_date":"DATE_FORMAT(relieving_date,'%%d-%%m-%%Y')"}).values('id','separation_type','relieving_date','current_level','approval_status','status')
					qry2=SeparationApplication.objects.filter(separation_type__value='LONG LEAVE',emp_id=emp_id).extra(select={'rejoin_date':"DATE_FORMAT(rejoin_date,'%%d-%%m-%%Y')","relieving_date":"DATE_FORMAT(relieving_date,'%%d-%%m-%%Y')"}).values('id','separation_type','relieving_date','current_level','approval_status','status','rejoin_date')

					count1=qry1.count()
					count2=qry2.count()

					if(count1>0):  ####No Dues Data in case of RESIGN visible at Employee's end ####
						for i in qry1:
							sep_id=i['id']

							qry3=NoDuesEmp.objects.filter(separation_id=sep_id).values('status','due_head__value','approved_by','approved_by__name','approval_date')
							qry_check=NoDuesEmp.objects.filter(separation_id=sep_id).exclude(status__contains="APPROVED")
							if len(qry_check)==0:
								resign_data.append({'no_dues_data':list(qry3),'data':(i),'final_no_dues_status':"APPROVED"})
							else:
								resign_data.append({'no_dues_data':list(qry3),'data':(i),'final_no_dues_status':"PENDING"})

						status = statusCodes.STATUS_SUCCESS


					if(count2>0): #No Dues Data in case of LONG LEAVE at Employee's end ####
						for j in qry2:
							sep_id=j['id']
							qry3=NoDuesEmp.objects.filter(separation_id=sep_id).values('status','due_head__value','approved_by','approved_by__name','approval_date')
							qry_check=NoDuesEmp.objects.filter(separation_id=sep_id).exclude(status__contains="APPROVED")
							if len(qry_check)==0:
								leave_data.append({'no_dues_data':list(qry3),'data':(j),'final_no_dues_status':"APPROVED"})
							else:
								leave_data.append({'no_dues_data':list(qry3),'data':(j),'final_no_dues_status':"PENDING"})

						status = statusCodes.STATUS_SUCCESS


				data={'data':data,'Resign_Data':resign_data,'Leave_Data':leave_data}
				status = statusCodes.STATUS_SUCCESS




			elif requestMethod.POST_REQUEST(request):
				data = json.loads(request.body)
				emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])

				if 'rejoin_date' in data:  ### New Entry in case of LONG LEAVE ######
					qry=SeparationApplication.objects.create(emp_id=emp_id,separation_type=EmployeeDropdown.objects.get(sno=data['separation_type']),relieving_date=data['relieving_date'],rejoin_date=data['rejoin_date'],remark=data['remark'],document=data['document'],current_level=1,approval_status="PENDING")

					qry1=list(SeparationApplication.objects.filter(emp_id=emp_id).values_list('id',flat=True).order_by('-id')[:1])

					if len(qry1)>0: ###For Approval #######
						add_next_level_pending(request.session['hash1'],1,qry1[0])

				else:  ### New Entry in case of RESIGN ###
					qry=SeparationApplication.objects.create(emp_id=emp_id,separation_type=EmployeeDropdown.objects.get(sno=data['separation_type']),relieving_date=data['relieving_date'],remark=data['remark'],document=data['document'],resignation_doc=data['resignation_doc'],current_level=1,approval_status="PENDING")

					qry1=list(SeparationApplication.objects.filter(emp_id=emp_id).values_list('id',flat=True).order_by('-id')[:1])

					if len(qry1)>0: ###For Approval #######
						add_next_level_pending(request.session['hash1'],1,qry1[0])
				
				data = statusMessages.MESSAGE_INSERT
				status = statusCodes.STATUS_SUCCESS

			else:
				data = statusMessages.MESSAGE_METHOD_NOT_ALLOWED
				status = statusCodes.STATUS_METHOD_NOT_ALLOWED
		else:
			data = statusMessages.MESSAGE_METHOD_NOT_ALLOWED
			status = statusCodes.STATUS_METHOD_NOT_ALLOWED
	else:
		data = statusMessages.MESSAGE_FORBIDDEN
		status = statusCodes.STATUS_FORBIDDEN
	
	return functions.RESPONSE(data,status)



def separation_reporting(request):
	if request.user.is_authenticated:
		emp_id = request.session['hash1']
		emp_detail = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_status='SEPARATE').values('desg','dept'))
		if requestMethod.GET_REQUEST(request):
			if 'request_type' in request.GET:
				if(requestType.custom_request_type(request.GET,'pending_separation')):
					if(len(emp_detail)>0):
						status_filter = ['PENDING','HOLD']
						data_temp=get_reporting_employees_applications(emp_id,status_filter,{})
						levels = get_reporting_to_levels(emp_detail[0]['dept'],emp_detail[0]['desg'])
						data={}
						for t,u in groupby(data_temp,key=lambda x:x['level']):
							data[t]={}
							for k,v in groupby(list(u),key=lambda x:x['approval_status']):
								data[t][k]=list(v)
						status = statusCodes.STATUS_SUCCESS
					else:
						data=statusMessages.MESSAGE_DATA_NOT_FOUND
						status=statusCodes.STATUS_UNAUTHORIZED
				elif(requestType.custom_request_type(request.GET,'view_previous')):
					if(len(emp_detail)>0):
						data=get_reporting_employees_applications(emp_id,['APPROVED','CANCELED'],{})
						status = statusCodes.STATUS_SUCCESS
				else:
					data = statusMessages.MESSAGE_NOT_FOUND
					status = statusCodes.STATUS_NOT_FOUND
			else:
				data = statusMessages.MESSAGE_NOT_FOUND
				status = statusCodes.STATUS_NOT_FOUND
		elif requestMethod.PUT_REQUEST(request):
			fetched_data = json.loads(request.body)
			id = fetched_data['id']
			approval_status = fetched_data['approval_status']
			remark = fetched_data['remark']
			resignee_emp_id = fetched_data['emp_id']
			level = fetched_data['level']
			previous_status = fetched_data['previous_status']
			previous_status = SeparationLevelApproval.objects.filter(form_id=id,approved_by=emp_id,level=level,approval_status=previous_status).exclude(status='DELETE').update(status='DELETE')
			qr = SeparationLevelApproval.objects.create(form_id=SeparationApplication.objects.get(id=id),approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id),approval_status=approval_status,remark=remark,level=level)
			if 'APPROVED' in approval_status:
				if check_for_level_increment(resignee_emp_id,level):
					add_next_level_pending(resignee_emp_id,level+1,id)
					# qr1 = SeparationLevelApproval.objects.create(form_id=SeparationApplication.objects.get(id=id),approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id),approval_status='PENDING',level=level+1)
					inc_val=1
				else:
					inc_val=0
				qr1 = SeparationApplication.objects.filter(id=id).update(current_level=F('current_level')+inc_val,approval_status="PENDING")
			else:
				qr1 = SeparationApplication.objects.filter(id=id).exclude(status='DELETE').update(approval_status=approval_status)

			data = statusMessages.MESSAGE_INSERT
			status = statusCodes.STATUS_SUCCESS
		else:
			data = statusMessages.MESSAGE_METHOD_NOT_ALLOWED
			status = statusCodes.STATUS_METHOD_NOT_ALLOWED
	else:
		data = statusMessages.MESSAGE_FORBIDDEN
		status = statusCodes.STATUS_FORBIDDEN
	return functions.RESPONSE(data,status)


def exit_paper(request):
	if request.user.is_authenticated:
		if requestMethod.GET_REQUEST(request):
			if 'request_type' in request.GET:
				if(requestType.custom_request_type(request.GET,'emp_type')):
					qry=EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).values('sno','value')
					data={'data':list(qry)}
					status = statusCodes.STATUS_SUCCESS

				else:
					data = statusMessages.MESSAGE_NOT_FOUND
					status = statusCodes.STATUS_SUCCESS
			
			else:
				data = statusMessages.MESSAGE_NOT_FOUND
				status = statusCodes.STATUS_NOT_FOUND

		elif requestMethod.POST_REQUEST(request):
			info = json.loads(request.body)
			emp_category=info['emp_category']
			title=info['title']
			expiry_date=info['expiry_date']
			p_ques_id=info['ques_id']
			ques_no=info['ques_no']
			description=info['description']
			answer_type=info['answer_type']

			qry1=SeparationExitQuestionPaper.objects.create(emp_category=EmployeeDropdown.objects.get(sno=info['emp_category']),title=info['title'],expiry_date=info['expiry_date'])
			qry2=SeparationQuestions.objects.create(paper_id=SeparationExitQuestionPaper.objects.get(id=qry1.id),p_ques_id=info['ques_id'],ques_no=info['ques_no'],description=info['description'],answer_type=info['answer_type'])

			data = statusMessages.MESSAGE_INSERT
			status = statusCodes.STATUS_SUCCESS

		else:
			data = statusMessages.MESSAGE_METHOD_NOT_ALLOWED
			status = statusCodes.STATUS_METHOD_NOT_ALLOWED
	
	else:
		data = statusMessages.MESSAGE_FORBIDDEN
		status = statusCodes.STATUS_FORBIDDEN
	return functions.RESPONSE(data,status)


def response(request):
	if request.user.is_authenticated:
		# emp_id=request.session['hash1']
		emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])

		if requestMethod.POST_REQUEST(request):
			info=json.loads(request.body)
			paper_id=info['paper_id']
			answer=info['answer']
			ques_id=info['ques_id']

			qry1=list(SeparationApplication.objects.filter(emp_id=emp_id).values_list('id',flat=True).order_by('-id')[:1])
			qry2=SeparationResponse.objects.create(emp_id=emp_id,paper_id=SeparationExitQuestionPaper.objects.get(id=paper_id),form_id=SeparationApplication.objects.get(id=qry1[0]))
			qry3=SeparationAnswers.objects.create(resp_id=SeparationResponse.objects.get(id=qry2.id),ques_id=SeparationQuestions.objects.get(p_ques_id=ques_id),answer=info['answer'])


			data = statusMessages.MESSAGE_INSERT
			status = statusCodes.STATUS_SUCCESS


		else:
			data = statusMessages.MESSAGE_METHOD_NOT_ALLOWED
			status = statusCodes.STATUS_METHOD_NOT_ALLOWED

	else:
		data = statusMessages.MESSAGE_FORBIDDEN
		status = statusCodes.STATUS_FORBIDDEN

	return functions.RESPONSE(data,status)






	############# CHANGE BY HARSH #############
	if obtained_co['co_obtained'] == 0.0:
		stu['marks'].pop()
		stu['marks'].append(0)
	###########################################