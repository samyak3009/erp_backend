from django.shortcuts import render
from dashboard.models import LeftPanel
from django.http import JsonResponse
from django.db.models import F
import json
from django.contrib.auth.models import User
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta,date
from django.db.models import Count

from .models1 import NoDuesHead,EmployeeSeparation,NoDuesEmp,SeparationLog,SeparationApproval
from musterroll.models import Reporting,Roles
from login.models import EmployeePrimdetail,EmployeeDropdown,AuthUser
from leave.models import Leaveapproval,Leaves,LeaveType

from leave.views import find_reporting_levels
from login.views import check,checkpermission

##########################################   NO DUES   ######################################################
def employee_view(request):
	error=True
	msg=''
	data=""
	qry2=""
	if 'HTTP_COOKIE' in request.META:		
		if request.user.is_authenticated:
			check=checkpermission(request,[211,337])
			if check==200:
				if request.method == 'GET':
					qry=NoDuesHead.objects.filter(status='ACTIVE').values('emp_id','due_head','due_head__value','emp_id__name')
					qry2=EmployeeDropdown.objects.filter(field='No Dues Category').exclude(value__isnull=True).extra(select={'id':'sno','nm':'value'}).values('id','nm')
					qry1=EmployeePrimdetail.objects.filter(emp_status='Active').extra(select={'id':'emp_id','nm':'name'}).values('id','nm')
					error=False
					msg="Success"
					
					data={'msg':msg,'data':list(qry2),'data1':list(qry1),'data2':list(qry),'error':error}
					return JsonResponse(status=200,data=data)
				if request.method == 'POST':
					data = json.loads(request.body.decode('utf-8'))
					no_dues = {}
					role_sno=EmployeeDropdown.objects.filter(pid=0,field='ROLES',value='NO DUE HEADS').values('sno')
					#print(role_sno)
					role_sno=role_sno[0]['sno']
					if 'emp_id' in data:
						no_dues['emp_id'] = EmployeePrimdetail.objects.get(emp_id=data['emp_id'])
					if 'due_head' in data:
						no_dues['due_head'] = EmployeeDropdown.objects.get(sno=data['due_head'])
					#print(no_dues)
					if no_dues:
						QryCheck = NoDuesHead.objects.filter(emp_id = no_dues['emp_id'], due_head = no_dues['due_head']).values()
						if QryCheck.count() ==0 :
							qry = NoDuesHead.objects.create(**no_dues)
							qry_roles,created=Roles.objects.get_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=data['emp_id']),roles=EmployeeDropdown.objects.get(sno=role_sno))
							
							msg = "Data Successfully Added..."
							status=200
						else:
							msg = "Head already assigned."	
							status=409
					res={'msg':msg}
					return JsonResponse(data=res,status=status)
				if request.method == 'DELETE':
					if request.body:
						inp = json.loads(request.body.decode('utf-8'))
						emp_id=inp['Emp']
						due_head=inp['NoDues']
						qry=NoDuesHead.objects.filter(emp_id=emp_id,due_head=due_head).update(status='DELETE')
						msg="Leave Deleted Successfully..!!"
						error=False
					data={'error':error,'msg':msg}
					return JsonResponse(data,safe=False)
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':data}
	return JsonResponse(status=504,data=data)

#########################  HR Separation  ##################################################
def separation_approval_admin(request):
	error=True
	msg=''
	data=""
	qry=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[211,337]) 
			if check==200:
				if request.method == 'GET':
					user=request.session['hash1']
					dept_qry=EmployeePrimdetail.objects.filter(emp_id=user).values('dept','desg')
					dept=dept_qry[0]['dept']
					desg=dept_qry[0]['desg']
					
					qry=SeparationApproval.objects.filter(status="PENDING",dept=EmployeeDropdown.objects.get(sno=dept_qry[0]['dept']),desg=EmployeeDropdown.objects.get(sno=dept_qry[0]['desg'])).values('separation_id__emp_id','separation_id__emp_id__name','separation_id__request_date','separation_id__type__value','separation_id__status','separation_id__rejoin_date','separation_id__emp_remark','separation_id','separation_id__attachment')
					error=False
					msg="Success"
					status=200
					if not qry:
						msg="No Data Found!!"
					data={'data_value':list(qry),'error':error,'msg':msg}
					
				if request.method == 'POST':
					inp=json.loads(request.body)
					Emp_id=inp['Emp_Id']
					Status=inp['hr_status']
					ID=inp['separation_id']
					Remark=inp['hr_remark']
					relieving_date=inp['relieving_date']

					user=request.session['hash1']
					dept_qry=EmployeePrimdetail.objects.filter(emp_id=user).values('dept','desg')
					dept=dept_qry[0]['dept']
					desg=dept_qry[0]['desg']
					
					qry_app=SeparationApproval.objects.filter(reportinglevel=-1,desg=desg,dept=dept,separation_id=ID).update(status=Status,remark=Remark,approved_by=request.session['hash1'],approvaldate=date.today())
					qry=EmployeeSeparation.objects.filter(id=ID,emp_id=Emp_id).exclude(emp_id='00007').update(final_status=Status,final_remark=Remark,finalAppDate=date.today(),relieving_date=relieving_date)

					if "APPROVED" in Status:

						qry3=EmployeePrimdetail.objects.filter(emp_id=Emp_id).update(emp_status='SEPARATE')
						qry4=AuthUser.objects.filter(username=Emp_id).update(is_active=0)
						qry_sep_id=EmployeeSeparation.objects.filter(emp_id=Emp_id,final_status__contains='APPROVED').values('id').order_by('-id')
						sep_id=qry_sep_id[0]['id']
						qry_sepeation_log=SeparationLog.objects.create(relieving_date=date.today(),separation_id=sep_id)
					
					
					msg="Success"
					error=False
					status=200
					data={'error':error,'msg':msg}
						
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':data}
	return JsonResponse(status=status,data=data)

def manual_separation_HR(request):
	msg=''
	data={}
	qry=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[211,337]) 
			if check==200:
				
				if request.method=="GET":
					qry_head=EmployeeDropdown.objects.filter(field='No Dues Category').exclude(value__isnull=True).extra(select={'due_head':'sno','due_head__value':'value'}).values('due_head','due_head__value')
					
					#qry_head=NoDuesHead.objects.filter(status='ACTIVE').values('due_head','due_head__value').distinct()
					status=200
					data=list(qry_head)

				if request.method == 'POST':
					inp=json.loads(request.body)
					Emp_id=inp['emp_id']
					Hr_Status="APPROVED BY ADMIN"
					Hr_Remark=inp['remark']
					status=inp['status']
					relieving_date=datetime.strptime((inp['relieving_date'].split('T'))[0], '%Y-%m-%d').date()
				
					f_reporting_remark=emp_remark="--"
					f_reporting_status="APPROVED"
					attachment=inp['attachment']

					if 'no_dues_app' in inp and inp['no_dues_app'] is not None:
						no_dues_app=list(inp['no_dues_app'])
					else:
						no_dues_app=[]
					q_no2=EmployeeDropdown.objects.filter(field='No Dues Category').exclude(value__isnull=True).exclude(sno__in=no_dues_app).extra(select={'due_head':'sno','due_head__value':'value'}).values('due_head','due_head__value')

					#q_no2=NoDuesHead.objects.exclude(due_head__in=no_dues_app).filter(status="ACTIVE").values('due_head')
					no_dues_rej=[]
					for q in q_no2:
						no_dues_rej.append(q['due_head'])
					

					status=status.upper()
					if(status=='RESIGN'):
						rejoin_date=None
					else:
						rejoin_date=inp['rejoin_date']
					final_status= EmployeeSeparation.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_id)).filter(final_status__contains="PENDING").order_by('-id')[:1].values('id')
					if(final_status.count() >0):
						q_del2=SeparationApproval.objects.filter(separation_id=EmployeeSeparation.objects.get(id=final_status[0]['id'])).delete()
						q_del3=NoDuesEmp.objects.filter(separation_id=EmployeeSeparation.objects.get(id=final_status[0]['id'])).delete()
						q_del1=EmployeeSeparation.objects.filter(id=final_status[0]['id']).delete()
						
					if(status=='RESIGN'):
						qry=EmployeeSeparation.objects.create(status=status,rejoin_date=rejoin_date,emp_remark=emp_remark,final_status=Hr_Status,final_remark=Hr_Remark,emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_id),attachment=attachment,finalAppDate=date.today(),request_date=date.today(),relieving_date=relieving_date)

					else:
						qry=EmployeeSeparation.objects.create(status=status,type=EmployeeDropdown.objects.get(sno=inp['type']),rejoin_date=rejoin_date,emp_remark=emp_remark,final_status=Hr_Status,final_remark=Hr_Remark,emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_id),attachment=attachment,finalAppDate=date.today(),request_date=date.today(),relieving_date=relieving_date)

					qry_sep_id=EmployeeSeparation.objects.filter(emp_id=Emp_id,final_status__contains='APPROVED').values('id').order_by('-id')[:1]
					ID=qry_sep_id[0]['id']

					qry_dept_desg=EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('desg','dept')
					qry_sep_app=SeparationApproval.objects.create(reportinglevel=-1,separation_id=EmployeeSeparation.objects.get(id=ID),dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']),desg=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['desg']),status=Hr_Status,remark=Hr_Remark,approvaldate=date.today(),approved_by=request.session['hash1'])

					for i in no_dues_app:
						qrt_e=NoDuesEmp.objects.create(status='APPROVED BY ADMIN',due_head=EmployeeDropdown.objects.get(sno=i),separation_id=EmployeeSeparation.objects.get(id=ID),approved_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),approval_date=date.today())

					#qry_head=NoDuesHead.objects.filter(status='ACTIVE',due_head__in=no_dues_rej).values('due_head').distinct()
					for i in no_dues_rej:
						qrt_e=NoDuesEmp.objects.create(status='PENDING',due_head=EmployeeDropdown.objects.get(sno=i),separation_id=EmployeeSeparation.objects.get(id=ID))

					qry3=EmployeePrimdetail.objects.filter(emp_id=Emp_id).update(emp_status='SEPARATE')
					qry4=AuthUser.objects.filter(username=Emp_id).update(is_active=0)
					qry_sep_id=EmployeeSeparation.objects.filter(emp_id=Emp_id,final_status__contains='APPROVED').values('id').order_by('-id')
					sep_id=qry_sep_id[0]['id']

					qry_sepeation_log=SeparationLog.objects.create(relieving_date=date.today(),separation_id=sep_id)

					status=200
					msg="Success"
					data={'msg':msg}
						
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data2':data}
	return JsonResponse(status=status,data=data)

###################################  HOD Separation  ##################################################
def separation_approval_1stReporting(request): # here hod is used for 1st reporting everywhere
	error=True
	msg=''
	data=""
	qry_a=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[425,337]) # Approval Role =425 Employe Role= 337
			if(check == 200):
				if request.method == 'GET':
					user=request.session['hash1']
					dept_qry=EmployeePrimdetail.objects.filter(emp_id=user).values('dept','desg')
					dept=dept_qry[0]['dept']
					desg=dept_qry[0]['desg']
					emp_reporting_to_user=[]
					
					qry_a=[]
					previous_actions=[]
					qry_a1=SeparationApproval.objects.filter(status="PENDING",dept=EmployeeDropdown.objects.get(sno=dept_qry[0]['dept']),desg=EmployeeDropdown.objects.get(sno=dept_qry[0]['desg'])).values('separation_id__emp_id','separation_id__emp_id__name','separation_id__request_date','separation_id__type__value','separation_id__status','separation_id__rejoin_date','separation_id__emp_remark','separation_id','separation_id__attachment')
					
					previous_actions=SeparationApproval.objects.exclude(status="PENDING").filter(dept=EmployeeDropdown.objects.get(sno=dept_qry[0]['dept']),desg=EmployeeDropdown.objects.get(sno=dept_qry[0]['desg'])).values('status','remark','separation_id__emp_id','separation_id__emp_id__name','separation_id__type__value','separation_id__rejoin_date')

					msg="Success"
					status=200
					error=False
					data={'data_value':list(qry_a1),'data':list(previous_actions),'error':error,'msg':msg}
				if request.method == 'POST':
					inp=json.loads(request.body)
					Emp_id=inp['Emp_Id']
					Status=inp['status']
					ID=inp['separation_id']
					Remark=inp['remark']
					
					user=request.session['hash1']
					dept_qry=EmployeePrimdetail.objects.filter(emp_id=user).values('dept','desg')
					dept=dept_qry[0]['dept']
					desg=dept_qry[0]['desg']
				

					if Status == 'REJECTED':
						qryt=SeparationApproval.objects.filter(separation_id=ID,dept=dept,desg=desg,separation_id__emp_id=Emp_id).update(status='REJECTED',remark=Remark,approved_by=user,approvaldate=date.today())
						qrys=EmployeeSeparation.objects.filter(id=ID).update(final_status="REJECTED",final_remark=Remark,finalAppDate=date.today())

						qry_up_nodues=NoDuesEmp.objects.filter(separation_id=ID,status=	"PENDING").update(status="N/A",approval_date=date.today())
					else:
						qryt=SeparationApproval.objects.filter(separation_id=ID,dept=dept,desg=desg,separation_id__emp_id=Emp_id).update(status='APPROVED',remark=Remark,approved_by=user,approvaldate=date.today())
						qry_sel=SeparationApproval.objects.filter(separation_id=ID,dept=dept,desg=desg,separation_id__emp_id=Emp_id).values('reportinglevel')
						qry3=Reporting.objects.filter(reporting_no=qry_sel[0]['reportinglevel']+1,emp_id=Emp_id).values('department','reporting_to')
						if len(qry3)>0:
							qry_sep_app=SeparationApproval.objects.create(reportinglevel=qry_sel[0]['reportinglevel']+1,separation_id=EmployeeSeparation.objects.get(id=ID),dept=EmployeeDropdown.objects.get(sno=qry3[0]['department']),desg=EmployeeDropdown.objects.get(sno=qry3[0]['reporting_to']))
						else:
							qry_check_no_dues=NoDuesEmp.objects.filter(status='PENDING',separation_id=EmployeeSeparation.objects.get(id=ID)).values('id')
							if len(qry_check_no_dues)==0:
								dept=EmployeeDropdown.objects.filter(field='DEPARTMENT',value='HR').values('sno')
								desg=EmployeeDropdown.objects.filter(field='DESIGNATION',value='MANAGER-HR').values('sno')
								qry_sep_app=SeparationApproval.objects.create(reportinglevel=-1,separation_id=EmployeeSeparation.objects.get(id=ID),dept=EmployeeDropdown.objects.get(sno=dept[0]['sno']),desg=EmployeeDropdown.objects.get(sno=desg[0]['sno']))

						msg="Success"
						error=False
						status=200
						data={'error':error,'msg':msg}
			else:
				status=403			
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':data}
	return JsonResponse(status=status,data=data)



############################ VIEW PREVIOUS STATUS ######################################3

def separation_prev_status(request):
	status=401
	msg=''
	data={}
	qry1=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[337])
			if check==200:
				if request.method == 'GET':
					sep_id=request.GET['sep_id']
					emp_id=request.session['hash1']

					qry_rep=SeparationApproval.objects.filter(separation_id=sep_id).extra(select={'approvaldate':"DATE_FORMAT(approvaldate,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('status','remark','approvaldate','desg__value')

					status=200

			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':list(qry_rep)}
	return JsonResponse(status=status,data=data)


######################################   EMPLOYEE SEPARATION   ################################################

def reporting_previous_approval(request):
	status=401
	msg=''
	data={}
	qry1=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:

			check=checkpermission(request,[425,337])
			if check==200:
				if request.method == 'GET':

					qry_prev=SeparationApproval.objects.filter(approved_by=request.session['hash1']).extra(select={'approvaldate':"DATE_FORMAT(approvaldate,'%%d-%%m-%%Y ')"}).values('approvaldate','remark','status','separation_id__emp_id','separation_id__emp_id__name','separation_id__emp_id__dept__value','separation_id__emp_id__desg__value','separation_id__final_status','separation_id__status','separation_id__type__value','separation_id__rejoin_date','separation_id__emp_remark')

					data=list(qry_prev)
					status=200

			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'data':data}
	return JsonResponse(status=status,data=data)


def long_leave_type(request):
	status=401
	msg=''
	data={}
	qry1=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:

			check=checkpermission(request,[337])
			if check==200:
				
				if request.method == 'GET':
					resign_data_final1=[]
					leave_data_final1=[]
					due_data=[]

					emp_id=request.session['hash1']

					qry1=EmployeeDropdown.objects.filter(field='LONG LEAVE').exclude(value__isnull=True).extra(select={'id':'sno','nm':'value'}).values('id','nm')

					qry2=EmployeeSeparation.objects.filter(status='Resign',emp_id=emp_id).values('id','status','type__value','rejoin_date','emp_remark','final_status','final_remark','finalAppDate')
					qry3=EmployeeSeparation.objects.filter(status='Leave',emp_id=emp_id).extra(select={'rejoin_date':"DATE_FORMAT(rejoin_date,'%%d-%%m-%%Y')"}).values('id','status','type__value','rejoin_date','emp_remark','final_status','final_remark','finalAppDate')	

					qry2_count=qry2.count()
					qry3_count=qry3.count()
					
					if(qry2_count>0):
						
						for i in qry2:
							sep_id=i['id']
							
							qry4=NoDuesEmp.objects.filter(separation_id=sep_id).values('status','due_head__value','approved_by','approved_by__name','approval_date')
							qry_check=NoDuesEmp.objects.filter(separation_id=sep_id).exclude(status__contains="APPROVED")
							if len(qry_check)==0:
								resign_data_final1.append({'no_dues_data':list(qry4),'data':(i),'final_no_dues_status':"APPROVED"})
							else:
								resign_data_final1.append({'no_dues_data':list(qry4),'data':(i),'final_no_dues_status':"PENDING"})


						status=200

						
					if(qry3_count>0):
						
						for k in qry3:
							sep_id=k['id']
							qry4=NoDuesEmp.objects.filter(separation_id=sep_id).values('status','due_head__value','approved_by','approved_by__name','approval_date')
							qry_check=NoDuesEmp.objects.filter(separation_id=sep_id).exclude(status__contains="APPROVED")
							if len(qry_check)==0:
								leave_data_final1.append({'no_dues_data':list(qry4),'data':(k),'final_no_dues_status':"APPROVED"})
							else:
								leave_data_final1.append({'no_dues_data':list(qry4),'data':(k),'final_no_dues_status':"PENDING"})


						status=200
					if(qry3_count !=0 or qry2_count != 0 or qry1.count() != 0):
						status=200
					else:
						status=204
						
					data={'msg':msg,'data':list(qry1),'data1':resign_data_final1,'data2':leave_data_final1}
					
					
				if request.method == 'POST':
					inp = json.loads(request.body)
					if 'attachment' in inp:
						attachment=inp['attachment']
					else:
						attachment=None
					emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
					if inp["status"]=="Leave":
						final_status= EmployeeSeparation.objects.filter(emp_id=emp_id).values('final_status').order_by('-id')
						if(final_status.count() ==0 or final_status[0]['final_status']=='REJECTED' or final_status[0]['final_status']=='APPROVED'):
							#print inp
							
							# qry1=EmployeeSeparation.objects.create(emp_id=emp_id,status=inp['status'],type=EmployeeDropdown.objects.get(sno=inp['type']),rejoin_date=inp['rejoin_date'],emp_remark=inp['reason'],final_status='PENDING',attachment=attachment,request_date=date.today())

							qry_sel=EmployeeSeparation.objects.filter(emp_id=emp_id).values('id').order_by('-id')[:1]
							qry_rep=Reporting.objects.filter(emp_id=request.session['hash1'],reporting_no=1).values('department_id','reporting_to')
							# qry_sep_app=SeparationApproval.objects.create(reportinglevel=1,separation_id=EmployeeSeparation.objects.get(id=qry_sel[0]['id']),dept=EmployeeDropdown.objects.get(sno=qry_rep[0]['department_id']),desg=EmployeeDropdown.objects.get(sno=qry_rep[0]['reporting_to']))

							qry_head=NoDuesHead.objects.filter(status='ACTIVE').values('due_head').distinct()
							# for i in qry_head:
								# qrt_e=NoDuesEmp.objects.create(status='PENDING',due_head=EmployeeDropdown.objects.get(sno=i['due_head']),separation_id=EmployeeSeparation.objects.get(id=qry_sel[0]['id']))

							# qrt_e=NoDuesEmp.objects.create(status='PENDING',due_head=EmployeeDropdown.objects.get(sno='1336'),separation_id=EmployeeSeparation.objects.get(id=qry_sel[0]['id']))

							msg="Success"
							status=200
						else:
							status=409
							msg="Duplicate Entry.."
					else:
						final_status= EmployeeSeparation.objects.filter(emp_id=emp_id).values('final_status').order_by('-id')
						print(final_status,"Final")
						if(final_status.count() ==0 or final_status[0]['final_status']=='REJECTED' or final_status[0]['final_status']=='APPROVED'):
							# qry1=EmployeeSeparation.objects.create(emp_id=emp_id,status=inp['status'],emp_remark=inp['reason'],attachment=attachment,request_date=date.today())

							# qry_sel=EmployeeSeparation.objects.filter(emp_id=emp_id).values('id').order_by('-id')[:1]
							# qry_rep=Reporting.objects.filter(emp_id=request.session['hash1'],reporting_no=1).values('department_id','reporting_to')
							# qry_sep_app=SeparationApproval.objects.create(reportinglevel=1,separation_id=EmployeeSeparation.objects.get(id=qry_sel[0]['id']),dept=EmployeeDropdown.objects.get(sno=qry_rep[0]['department_id']),desg=EmployeeDropdown.objects.get(sno=qry_rep[0]['reporting_to']))

							# qry_head=NoDuesHead.objects.filter(status='ACTIVE').values('due_head').distinct()
							# for i in qry_head:
							# 	qrt_e=NoDuesEmp.objects.create(status='PENDING',due_head=EmployeeDropdown.objects.get(sno=i['due_head']),separation_id=EmployeeSeparation.objects.get(id=qry_sel[0]['id']))
								
							# qrt_e=NoDuesEmp.objects.create(status='PENDING',due_head=EmployeeDropdown.objects.get(sno='1336'),separation_id=EmployeeSeparation.objects.get(id=qry_sel[0]['id']))

							msg="Success"
							status=200
						else:
							msg="Duplicate Entry.."
							status=409
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':data}
	return JsonResponse(status=status,data=data)

#####################################NODUES APPROVAL########################################################
def noduesApproval(request):
	msg=''
	data={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[337])
			if check==200:
				if request.method == 'GET':
					dic={}
					query=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('desg','dept')

					qry2=NoDuesEmp.objects.filter(due_head=1336,separation_id__emp_id__dept=query[0]['dept'],status="PENDING").values('id','separation_id__emp_id','separation_id__emp_id__name','due_head__value')
						
					if query[0]['desg']!=676:
						qry1=NoDuesHead.objects.filter(status="ACTIVE",emp_id=request.session['hash1']).values('due_head')

						for y in qry1:
							qry2=NoDuesEmp.objects.filter(due_head=y['due_head'],status="PENDING").values('id','separation_id__emp_id','separation_id__emp_id__name','due_head__value')
							dic=[]
							for x in qry2:
								dic1={}
								dic1['EmpId']=x['separation_id__emp_id']
								dic1['Name']=x['separation_id__emp_id__name']
								dic1['NoDuesDept']=x['due_head__value']
								dic1['NoDuesId']=x['id']
								dic.append(dic1)
					elif len(qry2)==0:
						qry2=NoDuesEmp.objects.filter(due_head=1336,separation_id__emp_id__dept=query[0]['dept'],status="PENDING").values('id','separation_id__emp_id','separation_id__emp_id__name','due_head__value')
						dic=[]
						for x in qry2:
							dic1={}
							dic1['EmpId']=x['separation_id__emp_id']
							dic1['Name']=x['separation_id__emp_id__name']
							dic1['NoDuesDept']=x['due_head__value']
							dic1['NoDuesId']=x['id']
							dic.append(dic1)

					msg='Success...'
					status=200
					
					data={'data':dic,'msg':msg}
				if request.method == 'POST':
					inp = json.loads(request.body.decode('utf-8'))
					NoDuesId=inp['NoDuesId']
					qry=NoDuesEmp.objects.filter(id=NoDuesId).update(status='APPROVED',approved_by=request.session['hash1'],approval_date=date.today())
					qry2=NoDuesEmp.objects.filter(id=NoDuesId).values('separation_id')
					qry3=SeparationApproval.objects.filter(separation_id=qry2[0]['separation_id'],status="PENDING").values('separation_id')
								
					qry4=NoDuesEmp.objects.filter(separation_id=qry2[0]['separation_id']).exclude(status__contains="APPROVED")
					if len(qry3)==0 and len(qry4)==0:
						dept=EmployeeDropdown.objects.filter(field='DEPARTMENT',value='HR').values('sno')
						desg=EmployeeDropdown.objects.filter(field='DESIGNATION',value='MANAGER-HR').values('sno')
						qry_sep_app=SeparationApproval.objects.create(reportinglevel=-1,separation_id=EmployeeSeparation.objects.get(id=qry2[0]['separation_id']),dept=EmployeeDropdown.objects.get(sno=dept[0]['sno']),desg=EmployeeDropdown.objects.get(sno=desg[0]['sno']))

					
					msg="Approved"
					status=200
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':data}
	return JsonResponse(status=status,data=data)


#########################################################LEAVE APPROVAL##################################################################
def Leave_Approval(request):
	error=True
	msg=''
	data=''
	leaves_to_be_approved=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[211,337])
			if check==200:
				if request.method == 'GET':
					getdesg=EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('desg')
					dept=request.session['dept']
					qry=Leaveapproval.objects.filter(dept__value=request.session['dept'],desg=getdesg,status='PENDING').values('leaveid','leaveid__requestdate','leaveid__subtype','leaveid__category','leaveid__emp_id','leaveid__emp_id__name','dept','desg','reportinglevel','leaveid__days','leaveid__reason','leaveid__leavecode__leave_abbr','leaveid__fromdate','leaveid__todate','leaveid__filename','leaveid__leavecode')
					for i in qry:
						i['requestdate']= i.pop('leaveid__requestdate')
						i['sub_type']=i.pop('leaveid__subtype')
						i['category']= i.pop('leaveid__category')
						i['employeeid']=i.pop('leaveid__emp_id')
						i['name']=i.pop('leaveid__emp_id__name')
						i['days']=i.pop('leaveid__days')
						i['reasons']=i.pop('leaveid__reason')
						i['LeaveType']=i.pop('leaveid__leavecode__leave_abbr')
						i['department']=i.pop('dept')

						employee_reporting_check=Reporting.objects.filter(department=i['department'],reporting_no=i['reportinglevel'],reporting_to=i['desg'],emp_id=i['employeeid']).count()
						if employee_reporting_check > 0:
							leaves_to_be_approved.append(i)
					error=False	
					msg="success"
					status=200
					data={'error':error,'msg':msg,'data':leaves_to_be_approved}	
				if request.method == 'POST':
					inp = json.loads(request.body.decode('utf-8'))
					inp1 = inp['data1']
					id=inp1['lid']
					dept=inp1['Dept']
					desg=inp1['Desg']
					appdate=datetime.now()
					type=inp1['type']
					remark=inp['remark']
					if type==1:
						qry1=Leaveapproval.objects.filter(leaveid=id,desg=desg,dept=dept).update(status ='APPROVED',approvaldate=appdate,remark=remark)
						qry2=Leaveapproval.objects.filter(leaveid=id,dept=dept,desg=desg).values('leaveid')
						qry3=Leaves.objects.filter(leaveid=qry2[0]['leaveid']).update(finalstatus='APPROVED',finalapprovaldate=appdate)
						msg="Approved"
						error=False
						status=200
					elif type==2:							
						qry1=Leaveapproval.objects.filter(leaveid=id,desg=desg,dept=dept).update(status ='REJECTED',approvaldate=appdate,remark=remark)
						qry2=Leaveapproval.objects.filter(leaveid=id,desg=desg,dept=dept).values('leaveid')
						qry3=Leaves.objects.filter(leaveid=qry2[0]['leaveid']).update(finalstatus='REJECTED',finalapprovaldate=appdate)
						msg="Rejected"
						error=False
						status=200
					elif type==3:
						qry1=Leaveapproval.objects.filter(leaveid=id,desg=desg,dept=dept).update(status ='APPROVED',approvaldate=appdate,remark=remark)
						qry2=Leaveapproval.objects.filter(leaveid=id,desg=desg,dept=dept).values('reportinglevel','leaveid','leaveid__emp_id')
						if qry2:
							pmail=qry2[0]['leaveid__emp_id']
							level=qry2[0]['reportinglevel']
							level+=level
							qry3=Reporting.objects.filter(reporting_no=level,emp_id=pmail).values('department','reporting_to')
							if qry3.count() > 0:
								list_add={'leaveid':Leaves.objects.get(leaveid=qry2[0]['leaveid']),'applicant':pmail,'reportinglevel':level,'dept':EmployeeDropdown.objects.get(sno=qry3[0]['department']),'desg':EmployeeDropdown.objects.get(sno=qry3[0]['reporting_to'])}
								qry4=Leaveapproval.objects.create(**list_add)
								if qry4:
									msg="Successfully Approved!"
									error=False
								else:
									msg="something went wrong"
							else:
								qry3=Leaves.objects.filter(leaveid=qry2[0]['leaveid']).update(finalstatus='APPROVED',finalapprovaldate=appdate);
								if qry3:										
									msg="Successfully Approvede"
									error=False
								else:
									msg="something went wrong"
						else:
							msg="no such entry"
						msg="Approved"
						error=False
						status=200
					else:
						msg="sorry.. something went wrong"		
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':data}
	return JsonResponse(status=status,data=data)


################################################### RETRIVE EMPLOYEE ###############################################

def retrieve(request):
	msg=""
	data={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[211,337])
			if check==200:
				if request.method == 'GET':
					qry=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value__isnull=True).values('value','sno')
					msg = "success"
					status = 200
					data = {'msg': msg, 'data': list(qry)}
				elif request.method == 'POST':
					inp = json.loads(request.body.decode('utf-8'))
					
					if(inp['type'] == '1'):
						dept=inp['dept']
						qry=EmployeePrimdetail.objects.filter(dept=dept,emp_status='SEPARATE').values('name','emp_id')
						msg = "Approved"
						status = 200
						data = {'msg': msg, 'data': list(qry)}
					elif(inp['type'] == '2'):
						name=inp['name']
						qry=EmployeePrimdetail.objects.filter(emp_id=name,emp_status='SEPARATE').values('name','emp_id','desg__value')
						msg = "Approved"
						status = 200
						data = {'msg': msg, 'data': list(qry)}
					elif(inp['type'] == 'manual_separation'):
						dept=inp['dept']
						qry=EmployeePrimdetail.objects.filter(dept=dept,emp_status='ACTIVE').values('name','emp_id')
						if(qry):
							status=200
						else:
							status=204
						# emp=[]
						# a=0
						# if(qry):
						# 	for i in qry:
						# 		emp1={}
						# 		qry_check_sep=EmployeeSeparation.objects.filter(emp_id=i['emp_id'],hr_status="APPROVED").values('separation_type').order_by('-id')

						# 		if(qry_check_sep.count() == 0 ):
						# 			emp1['name']=i['name']
						# 			emp1['emp_id']=i['emp_id']
						# 			emp.append(emp1)
						# 			a+=1
								
						# 			msg = "Approved"
						# 			status = 200
						# 		else:
						# 			status=204
						# else:
						# 	status=204


						data = {'msg': msg, 'data': list(qry)}
					elif(inp['type'] == '3'):
						name = inp['name']
						dept = inp['dept']
						qry=EmployeePrimdetail.objects.filter(emp_id=name,dept=dept).update(emp_status='ACTIVE')
						qry=AuthUser.objects.filter(username=name).update(is_active=1)
						sep_id_qry=EmployeeSeparation.objects.filter(emp_id=name,final_status__contains='APPROVED').values('id').order_by('-id')

						qry_emp_sep=EmployeeSeparation.objects.filter(id=sep_id_qry[0]['id']).update(rejoin_date=date.today())
						sep_id=sep_id_qry[0]['id']
						qry_sep_log=SeparationLog.objects.filter(rejoin_date=None,separation_id=sep_id).exclude(relieving_date__isnull=True).update(rejoin_date=date.today())
						qry_update_doj=EmployeePrimdetail.objects.filter(emp_id=name).update(doj=date.today())
						msg = "Employee Retrieve Successfully!!!"
						status = 200
					elif(inp['type'] == 'manual_separation_emp_details'):
						name=inp['name']
						qry=EmployeePrimdetail.objects.filter(emp_id=name,emp_status='ACTIVE').values('name','emp_id','desg__value')
						msg = "Approved"
						status = 200
						data = {'msg': msg, 'data': list(qry)}
						

				else:
					msg = "sorry.. something went wrong"
			else:
				status = 403
		else:
			status = 401
	else:
		status = 400
	data = {'msg': msg, 'data': data}
	return JsonResponse(status=status, data=data)
################################################## HR Previous ##########################################
def hr_separation_previous(request):
	error=True
	data_resign=[]
	data_leave=[]
	
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:

			check=checkpermission(request,[211,337])
			if check==200:
				if request.method == 'GET':
					qry_sep=EmployeeSeparation.objects.exclude(final_status="PENDING").filter(status="RESIGN").values('id','emp_id','emp_id__name','emp_id__desg__value','emp_id__dept__value','emp_id__emp_type__value','status','emp_remark','emp_id__doj','final_status','final_remark','type__value','relieving_date')

					for qs in qry_sep:
						qry_no=NoDuesEmp.objects.filter(separation_id=qs['id']).extra(select={'approval_date':"DATE_FORMAT(approval_date,'%%d-%%m-%%Y')"}).values('due_head__value','status','approval_date','approved_by','approved_by__name')

						qry_up_nodues=NoDuesEmp.objects.filter(separation_id=qs['id']).exclude(status__contains="APPROVED").values('id')
						if len(qry_up_nodues)==0:
							data_resign.append({'separation_data':qs,'no_dues_status':"APPROVED","no_dues_data":list(qry_no)})
						else:
							data_resign.append({'separation_data':qs,'no_dues_status':"PENDING","no_dues_data":list(qry_no)})

					qry_sep=EmployeeSeparation.objects.exclude(final_status="PENDING").filter(status="LEAVE").values('id','emp_id','emp_id__name','emp_id__desg__value','emp_id__dept__value','emp_id__emp_type__value','status','emp_remark','rejoin_date','final_status','final_remark','type__value','relieving_date')

					for qs in qry_sep:

						if qs['relieving_date'] is not None:
							qs['from_date']=qs['relieving_date']+timedelta(days=1)

						if qs['rejoin_date'] is not None:
							qs['to_date']=qs['rejoin_date']-timedelta(days=1)
						qry_no=NoDuesEmp.objects.filter(separation_id=qs['id']).extra(select={'approval_date':"DATE_FORMAT(approval_date,'%%d-%%m-%%Y')"}).values('due_head__value','status','approval_date','approved_by','approved_by__name')

						qry_up_nodues=NoDuesEmp.objects.filter(separation_id=qs['id']).exclude(status__contains="APPROVED").values('id')
						if len(qry_up_nodues)==0:
							data_leave.append({'separation_data':qs,'no_dues_status':"APPROVED","no_dues_data":list(qry_no)})
						else:
							data_leave.append({'separation_data':qs,'no_dues_status':"PENDING","no_dues_data":list(qry_no)})


					status=200
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data2={'data_leave':data_leave,'data_resign':data_resign}
	return JsonResponse(status=status,data=data2)