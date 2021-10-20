# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
#from musterroll.models Reporting
from datetime import datetime
from itertools import chain
from operator import attrgetter
from pprint import pprint
from django.utils import dateparse

from .models import GrievanceData
from musterroll.models import EmployeePrimdetail,EmployeeDropdown,Reporting
from leave.models import LeaveType
from login.models import AuthUser

from login.views import checkpermission
# Create your views here.

def grievance_type_rept(request):
	msg=''
	data=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check == 200):
				if request.method == 'GET':
					qry1=EmployeeDropdown.objects.filter(field='GRIEVANCE TYPE').exclude(value__isnull=True).extra(select={'val':'value','sno':'sno'}).values('val','sno')
					#qry2=Reporting.objects.filter(emp_id='4497',reporting_no=1).values('reporting_to__sno','reporting_to__value','department__sno','department__value','reporting_no')
					status=200
					data={'grievance_type':list(qry1)}
					msg="success"
					send={'msg':msg,'data':data}
				elif request.method == 'POST':
					input_data = json.loads(request.body)
					if 'g_type' in input_data and 'g_text' in input_data and 'g_level' in input_data:
							g_info={}
							g_sta={}
							user=request.session['hash1']
							g_info['type'] = EmployeeDropdown.objects.get(sno=input_data['g_type'])
							g_info['gri_message'] = input_data['g_text']
							g_info['gri_date']= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
							user=EmployeePrimdetail.objects.get(emp_id=user)
							g_info['empid'] = user
							if 'document' in input_data:
								g_info['document'] = input_data['document']
							else:
								g_info['document']=None
							status=200
							qry=Reporting.objects.filter(emp_id=user,reporting_no=1).values()
							if qry:
								g_info['department']=EmployeeDropdown.objects.get(sno=qry[0]['department_id'])
								g_info['designation']=EmployeeDropdown.objects.get(sno=qry[0]['reporting_to_id'])
							insert_gri=GrievanceData.objects.create(**g_info)
							if insert_gri:
								msg="success"

							else:
								msg="could not insert"

					else:
						msg = "Wrong Params"
						status = 500
					send={'msg':msg,'data':data}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=400

	return JsonResponse(status=status,data=send)

def grievance_approval_hod(request):
	send = ""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check==200):
				if request.method == 'GET':
					check2 = checkpermission(request,[425])

					if (check2 == 200) :

						role="level1"
						qr=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values()[0]

						status=200
						try:
							data=GrievanceData.objects.filter(department=qr['dept_id'],designation=qr['desg_id'],remark_hod='PENDING',status_hod = 'PENDING').values('gri_id','gri_date','gri_message','type__value','empid__emp_id','empid__name','document','empid__desg__value').exclude(department__isnull=True,designation__isnull=True,empid__isnull=True)#.exclude(empid__desg__value='HOD')
							send={'data':list(data),'role':role}
							status=200

						except:
							status=500
					else:
						status=403

					# if 319 in request.session['roles'] or request.session['dept'] == 'ADMIN':
					#   if 319 in request.session['roles']:
					#       role="HOD"
					#       user=request.session['hash1']
					#       qr=EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=user)).values('dept')

					#       if qr:
					#           data=GrievanceData.objects.filter(empid__dept=qr[0]['dept'],remark_hod='PENDING',status_hod = 'PENDING').values('gri_id','gri_date','gri_message','type__value','empid__emp_id','empid__name','document','empid__desg__value').exclude(empid__desg__value='HOD')#extra(select={'gdate': 'gri_date','gid':'gri_id','gmsg':'message','sta':'status','sol_date':'solve_date','rmrk_hod':'remark_hod','rmrk_hr':'remark_hr','hodappdate':'hodapprovedate','gtype':'type','emp':'empid__emp_id','fdback':'feedback','doc':'document'}).values('gid','gdate','gmsg','gtype','emp','sta','sol_date','rmrk_hod','rmrk_hr','hodappdate','doc')
					#           msg = "Success"
					#           status = 200
					#       else:
					#           msg="Department not  known"
					#           status =500

					#   elif(request.session['dept'] == 'ADMIN') :
					#       role = 'ADMIN'
					#       data_values=GrievanceData.objects.filter(status_hod='PENDING',remark_hod='PENDING',empid__desg__value='HOD').values('gri_id','gri_date','hod_responsedate','hr_responsedate','gri_message','type__value','status_hod','status_hr','remark_hod','remark_hr','empid','empid__name','document','feedback','empid__desg__value','empid__dept__value')
					#       for i in data_values:

					#           reporting_level_filtering=Reporting.objects.filter(emp_id=i['empid'],reporting_to__value__in=request.session['roles']).order_by("-reporting_no")[:1]

					#           if reporting_level_filtering.count() > 0:
					#               data.append(i)
					#       msg="success"
					#       status = 200
					#   else:
					#       status= 403
					#       msg = "Not Autherized"
					#   send={'data':list(data),'role':role,'msg':msg}

					# else:
					#   status = 403


				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 400

	return JsonResponse(status=status,data=send,safe=False)

def grievance_approval_hr(request):
	msg=""
	send = ""
	data = ""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check == 200):
				data=[]
				check2 = checkpermission(request,[211])
				if(check2 == 200):
					if request.method == 'GET':
						role="HR"
						data=GrievanceData.objects.filter(status_hod='APPROVED',remark_hr='PENDING',status_hr='PENDING').values('gri_id','gri_date','gri_message','type__value','empid__name','status_hod','hod_responsedate','remark_hod','document','empid__emp_id','empid__dept__value','empid__current_pos__value')
						msg ="Success"

						status = 200
						data={'data':list(data),'role':role}

					else:
						status = 500

				else:
					status = 403
			else:
				status = 403
		else:
			status = 401
	else:
		status=400

	return JsonResponse(status=status,data=data,safe=False)


def grievance_view(request):
	send =""
	data_values=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check == 200):
				user=request.session['hash1']
				if request.method == 'GET':
					try:
						qry=GrievanceData.objects.filter(empid=user).values('gri_id','gri_message','type__value','document','gri_date','status_hod','status_hr','remark_hod','remark_hr','feedback','remark_hr','hod_responsedate','hr_responsedate','empid__dept__value').order_by("-gri_id")

						values=[]
						for i in qry:
							data={}
							data['g_id']=i['gri_id']
							data['message']=i['gri_message']
							data['type']=i['type__value']
							data['doc']=i['document']
							data['g_date']=i['gri_date']
							data['hodsta']=i['status_hod']
							data['hrsta']=i['status_hr']
							data['rmrkhod']=i['remark_hod']
							data['rmrkhr']=i['remark_hr']
							data['hodrespdate']=i['hod_responsedate']
							data['hrrespdate']=i['hr_responsedate']
							data['fdbck']=i['feedback']
							data['dept']=i['empid__dept__value']
							values.append(data)
							data_values=values
						msg="success"
						status = 200
					except:
						msg="Error"
						status = 500
					send={'msg':msg,'data':data_values}
				else:
					status = 500
			else:
				status = 403
		else:
			status = 401

	else:
		status = 400

	return JsonResponse(status=status,data=send,safe=False)



def insert_approval_hod(request):
	msg = ""
	send =""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check == 200):
				check2 = checkpermission(request,[425])

				if(check2==200):
					if request.method == 'PUT':
						data=json.loads(request.body)
						
						if not 'request_from' in data:
							data2=[]
							data2.append(data)
						else:
							data2=data['data']

						for info in data2:
							if ('g_id' in info or 'gri_id' in info) and ('rmrk' in info or 'remark' in info):
								date=datetime.now()
								try:
									gri_id=info['g_id']
								except:
									gri_id=info['gri_id']

								try:
									remark=info['rmrk']
								except:
									remark=info['remark']
									
								status=info['status']

								qry=GrievanceData.objects.filter(gri_id=gri_id).update(remark_hod=remark,status_hod=status,hod_responsedate=date)

								if qry:
									msg="Success"
									status = 200

								else:
									msg="Something Went Wrong"
									status = 500

							else:
								msg="Some Parameters Missing"
								status = 500

							send={'msg':msg}
					else:
						status = 500
				else:
						status = 403
						msg="Invalid Login!!"
			else:
				status = 403
		else:
			status = 401

	else:
		status = 400

	return JsonResponse(status=status,data=send,safe=False)

def insert_approval_hr(request):
	msg = ""
	send = ""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check == 200):
				info = json.loads(request.body)
				check2 = checkpermission(request,[211])#hr Roles
				if(check2 == 200):
					if request.method == 'PUT':
						info=json.loads(request.body)
						if 'g_id' in info and 'rmrk' in info:
						
							date=datetime.now()
							#info=json.loads(request.body)
							g_id=info['g_id']
							remark=info['rmrk']
							status=info['status']
							qry=GrievanceData.objects.filter(gri_id=g_id).update(remark_hr=remark,status_hr=status,hr_responsedate=date)
							if qry:
								status = 200
								msg="Success"
								send={'msg':msg}
							else:
								status = 500
								msg="Something Went Wrong"
								send={'msg':msg}
						else:
							msg="Could Not Insert"
							status = 500
							send={'msg':msg}
					else:
						status = 500
				else:
					status = 403
					msg="Invalid Login!"
					send={'msg':msg}

			else:
				status = 403
		else:
			status = 401
	else:
		status = 400

	return JsonResponse(status=status,data=send,safe=False)



def feedbck(request):
	send =""
	msg =""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check == 200):
				if request.method == 'PUT':
					info=json.loads(request.body)
					if 'g_id' in info and 'feedbck' in info:
						g_id=info['g_id']
						feedback=info['feedbck']
						user=request.session['hash1']
						qry=GrievanceData.objects.filter(empid=user,gri_id=g_id).update(feedback=feedback)
						if qry:
							msg="success"
							status = 200
						else:
							status = 500
							msg="Could not Insert"
					else :
						msg ="Wrong Parameters"
						status = 500
					send={'msg':msg}
				else:
					status = 500
			else:
				status = 403
		else:
			status = 401

	else:
		status = 400

	return JsonResponse(status = status,data=send,safe=False)




def consolidated_rept_field_data_hod(request):
	send=''
	msg = ""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check == 200):
				if request.method == 'GET':
					check2 = checkpermission(request,[319])#hod roles
					if(check2 == 200):

						dept=EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('dept__sno','dept__value')
						role='level1'
						gri_type=EmployeeDropdown.objects.filter(field='GRIEVANCE TYPE').extra(select={'val':'value','no':'sno'}).values('no','val')
						data={'dept':list(dept),'g_type':list(gri_type),'role':role}
						msg="Success"
						status=200
						send={'msg':msg,'data':data}


					else:
						status = 403


				else:
					status = 500
			else:
				status = 403
		else:
			status = 401
	else:
		status = 400

	return JsonResponse(status = status,data = send,safe=False)

def consolidated_rept_field_data_hr(request):
	send=''
	msg = ""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337])
			if(check == 200):
				if request.method == 'GET':
					check2 = checkpermission(request,[211,1345])

					if (check2 == 200) :
						dept=EmployeeDropdown.objects.filter(field='DEPARTMENT').extra(select={'dept__val':'value','dept__sno':'sno'}).values('dept__sno','dept__val')
						role='HR'

						gri_type=EmployeeDropdown.objects.filter(field='GRIEVANCE TYPE').extra(select={'val':'value','no':'sno'}).values('no','val')
						data={'dept':list(dept),'g_type':list(gri_type),'role':role}
						msg="success"
						status =200
						send={'msg':msg,'data':data}

					else:
						status = 403

				else:
					status =500
			else:
				status = 403
		else:
			status=401
	else:
		status=400

	return JsonResponse(status=status,data=send,safe=False)


def consolidated_report_data_hod(request):
	send=''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			var=checkpermission(request,[337])
			if var==200:
				if request.method == 'POST':
					check2= checkpermission(request,[425])
					if (check2 == 200) :
						input_data=json.loads(request.body)
						#print(request.session['roles'])
						if ("f_date" and "dept" and "status" and "t_date" and "g_type") in input_data:
							from_date=input_data['f_date']
							to_date=input_data['t_date']
							#dept=EmployeePrimdetail.objects.filter(emp_id=AuthUser.objects.get(username=request.session['hash1'])).values('dept__sno')
							#print(dept.query)
							#dept = [dept[0]['dept__sno']]
							#print(dept)
							gri_type=input_data['g_type']
							sta=input_data['status']
							qry_string={'gri_date__range':[from_date, to_date]}
							qry1=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values()[0]
							qry_string.update({'department_id':qry1['dept_id'] })
							qry_string.update({'designation_id':qry1['desg_id'] })
							if 'ALL' in gri_type:
								pass
							else:
								qry_string.update({'type__in': gri_type})

							if sta == '0':
								pass
							elif sta == '1':
								qry_string.update({'status_hod': 'APPROVED'})
							elif sta == '2':
								qry_string.update({'status_hod': 'REJECTED'})
							elif sta == '3':
								qry_string.update({'status_hr': 'APPROVED'})
							elif sta == '4':
								qry_string.update({'status_hr': 'REJECTED'})


							try:
								qr=GrievanceData.objects.filter(**qry_string).values('gri_id','gri_date','hod_responsedate','hr_responsedate','gri_message','type__value','status_hod','status_hr','remark_hod','remark_hr','empid__emp_id','empid__name','document','feedback','empid__desg__value','empid__dept__value').order_by('gri_date')
								lenn=len(qr)
								for x in range(0,lenn):
									date1=qr[x]['gri_date'].strftime("%d/%m/%Y")
									qr[x]['gri_date']=date1

								role='level1'
								status=200
								msg="success"
								send={'data':list(qr),'role':role,'msg':msg}
								# if 319 in request.session['roles']:
								#   qr=GrievanceData.objects.filter(**qry_string).values('gri_id','gri_date','hod_responsedate','hr_responsedate','gri_message','type__value','status_hod','status_hr','remark_hod','remark_hr','empid__emp_id','empid__name','document','feedback','empid__desg__value','empid__dept__value')
								#   print(qr.query)
								#   role='HOD'
								# elif request.session['dept'] == 'ADMIN':
								#   qry_string.update({'empid__desg__value':'HOD'})

								#   data_values=GrievanceData.objects.filter(**qry_string).values('gri_id','gri_date','hod_responsedate','hr_responsedate','gri_message','type__value','status_hod','status_hr','remark_hod','remark_hr','empid','empid__name','document','feedback','empid__desg__value','empid__dept__value')
								#   for i in data_values:
								#       reporting_level_filtering=Reporting.objects.filter(emp_id=i['empid'],reporting_to__value__in=request.session['roles']).order_by("-reporting_no")[:1]

								#       if reporting_level_filtering.count() > 0:
								#           qr.append(i)

								#   role='ADMIN'
								# status=200
								# msg="success"

								# send={'data':list(qr),'role':role,'msg':msg}
							except:
								status=500
						else:
							status=500
					else:
						status=403
				else:
					status=500
			else:
				status=403
		else:
			status=401
	else:
		status=400
	#send={'error':error,'msg':status,'data':data}
	return JsonResponse(status=status,data=send,safe=False)


def consolidated_report_data_hr(request):

	send=''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			var=checkpermission(request,[337,211,1345])
			if var==200:
				if request.method == 'POST':
					input_data=json.loads(request.body)
					if ("f_date" and "dept" and "status" and "t_date" and "g_type") in input_data:
						from_date=input_data['f_date']
						to_date=input_data['t_date']
						dept=input_data['dept']
						gri_type=input_data['g_type']
						sta=input_data['status']
						qry_string={'gri_date__range':[from_date, to_date]}
						if  'ALL' in dept:
							pass
						else:
							qry_string.update({'empid__dept__in': dept})
						if 'ALL' in gri_type:
							pass
						else:
							qry_string.update({'type__in': gri_type})
						if sta == '0':
							pass
						elif sta == '1':
							qry_string.update({'status_hod': 'APPROVED'})
						elif sta == '2':
							qry_string.update({'status_hod': 'REJECTED'})
						elif sta == '3':
							qry_string.update({'status_hr': 'APPROVED'})
						elif sta == '4':
							qry_string.update({'status_hr': 'REJECTED'})
						qr=[]
						try:
							qr=GrievanceData.objects.filter(**qry_string).values('gri_id','gri_date','hod_responsedate','hr_responsedate','gri_message','type__value','status_hod','status_hr','remark_hod','empid__emp_id','empid__name','remark_hr','hod_responsedate','hr_responsedate','document','feedback','empid__dept__value','empid__desg__value').exclude(empid__desg__value='HR')
							role='HR'
							status=200
							msg="success"
							send={'data':list(qr),'role':role}
						except:
							status=500
					else:
						status=500
				else:
					status=500
			else:
				status=403
		else:
			status=401
	else:
		status=400
	#send={'error':error,'msg':msg,'data':data}
	return JsonResponse(status=status,data=send,safe=False)

def CheckForHourly(request):
	error=True
	msg=""
	if 'HTTP_COOKIE' in request.META :
		if request.user.is_authenticated:
			if request.session['hash3'] == 'Employee':
				if request.body:
					error=False
					msg="Success"
					data=json.loads(request.body)
					Leavetype=data['LeaveType']
					#print(LeaveType)
					Qry=LeaveType.objects.filter(id=Leavetype).values('hours_leave')
					#print(Qry)
				else:
					msg="No Request Found"
			else:
				msg="Not Authorised"
		else:
			msg="Not Logged In"
	else:
		msg="Wrong parameters"
	return JsonResponse({'msg':msg,'error':error,'data':Qry[0]},safe=False)
