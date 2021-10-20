from  __future__ import print_function
from django.shortcuts import render

from django.shortcuts import render
from datetime import datetime,timedelta
from django.utils import timezone
import json
from django.conf import settings
from django.http import HttpResponse,JsonResponse
import time
from dateutil.relativedelta import relativedelta
from django.db.models import Q,Sum,F,Value,CharField
from login.models import EmployeeDropdown,EmployeePrimdetail,AuthUser
from musterroll.models import Reporting,EmployeePerdetail
from attendance.models import Attendance2
from datetime import date
import copy
from datetime import datetime
import calendar
from operator import itemgetter
from login.views import checkpermission
from .models import *
from leave.models import Leaves
from leave.views import calculate_working_days,fun_num_of_leaves
from login.models import EmployeePrimdetail
import io
from threading import Thread
import requests
from django.http.response import HttpResponse
from xlsxwriter.workbook import Workbook


def Accounts_dropdown(request):
	data={}
	qry1=""
	session=getCurrentSession(None)
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				if request.method == 'GET':
					if request.GET['request_type'] == 'general':
						qry1=AccountsDropdown.objects.filter(value=None,session=session).extra(select={'fd':'field','id':'sno','parent':'pid'}).values('fd','id','parent').exclude(status="DELETE").distinct()
						for field1 in qry1:
							if field1['parent']!=0:
								pid=field1['parent']
								qry2=AccountsDropdown.objects.filter(sno=pid,session=session).exclude(status="DELETE").values('field')
								field1['fd']=field1['fd']+'('+qry2[0]['field']+')'
						msg="Success"
						error=False
						if not qry1:
							msg="No Data Found!!"
						status=200
						data={'msg':msg,'data':list(qry1)}
						
					elif request.GET['request_type'] == 'subcategory':
						sno=request.GET['Sno']
						names=AccountsDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('field','pid')
						name=names[0]['field']
						p_id=names[0]['pid']

						qry1=AccountsDropdown.objects.filter(field=name,pid=p_id,session=session).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'valueid': 'sno','parentId':'pid','cat':'field','text1':'value','edit':'is_edit','delete':'is_delete'}).values('valueid', 'parentId', 'cat', 'text1','edit','delete')
						for x in range(0,len(qry1)):
							test=AccountsDropdown.objects.filter(pid=qry1[x]['valueid'],session=session).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'subid': 'sno','subvalue':'value','edit':'is_edit','delete':'is_delete'}).values('subid','subvalue','edit','delete')
							qry1[x]['subcategory']=list(test)
						msg="Success"
						data={'msg':msg,'data':list(qry1)}
						status=200

				elif request.method == 'DELETE':
					data=json.loads(request.body)
					qry=AccountsDropdown.objects.filter(sno=data['del_id']).exclude(status="DELETE").values('field')
					if(qry.exists()):

						sno = data['del_id']
						fd=qry[0]['field']
						deletec(sno)
						q2=AccountsDropdown.objects.filter(field=fd,session=session).exclude(status="DELETE").exclude(value__isnull=True).values().count()
						if q2==0:
							q3=AccountsDropdown.objects.filter(field=fd,session=session).exclude(status="DELETE").update(status="DELETE")
						msg="Data Successfully Deleted..."
						status=200
					else:
						msg="Data Not Found!"
						status=404
					data={'msg':msg}
					status=200
				elif request.method == 'POST':
					body1 = json.loads(request.body)

					for body in body1:
						pid = body['parentid']
						value=body['val'].upper()
						field_id=body['cat']
						field_qry=AccountsDropdown.objects.filter(sno=field_id).exclude(status="DELETE").values('field')
						field=field_qry[0]['field']
						if pid != 0:
							field_qry=AccountsDropdown.objects.filter(sno=pid).exclude(status="DELETE").exclude(value__isnull=True).values('value')
							field=field_qry[0]['value']
							cnt=AccountsDropdown.objects.filter(field=field,session=session).exclude(status="DELETE").values('sno')
							if len(cnt)==0:
								add=AccountsDropdown.objects.create(pid=pid,field=field,session=AccountsSession.objects.get(id=session))

						qry_ch=AccountsDropdown.objects.filter(Q(field=field) & Q(value=value)).filter(pid=pid,session=session).exclude(status="DELETE")
						if(len(qry_ch) >0):
							status=409

						else:
							created=AccountsDropdown.objects.create(pid=pid,field=field,value=value,session=AccountsSession.objects.get(id=session))
							msg="Successfully Inserted"
							data={'msg':msg}
							status=200

				elif request.method == 'PUT':
					body = json.loads(request.body)
					sno = body['sno1']
					val=body['val'].upper()
					field_qry=AccountsDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('pid','value')
					pid=field_qry[0]['pid']
					value=field_qry[0]['value']
					add=AccountsDropdown.objects.filter(pid=pid,field=value,session=session).exclude(status="DELETE").update(field=val)
					add=AccountsDropdown.objects.filter(sno=sno).exclude(status="DELETE").update(value=val,status="UPDATE")
					add=AccountsDropdown.objects.filter(pid=sno,session=session).exclude(status="DELETE").update(field=val,status="UPDATE")
					msg="Successfully Updated"
					data={'msg':msg}
					status=200

			else:
				status=403
		else:
			status=401
	else:
		status=400
	return JsonResponse(status=status,data=data)



def deletec(pid):
	qry=AccountsDropdown.objects.filter(pid=pid,session=session).exclude(status="DELETE").values('sno')
	if len(qry)>0:
		for x in qry:
			deletec(x['sno'])
	qry=AccountsDropdown.objects.filter(sno=pid,session=session).exclude(status="DELETE").update(status="DELETE")



def get_all_emp(dept):
	s = EmployeePrimdetail.objects.filter(emp_status='ACTIVE',dept=dept).exclude(emp_type=219).exclude(emp_id="00007").extra(select={'emp_name':'name','emp_code':'emp_id'}).exclude(emp_status="SEPARATE").values('emp_name','emp_code','dept__value','desg__value').order_by('name').all()
	return s

def emp_detail(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404,211])
			if check==200:
				if request.method == 'GET':
					org=request.GET['org']
					dept=request.GET['dept']

					s = get_all_emp(dept)
					msg="Success"
					status=200
					data_values={'msg':msg,'data':list(s)}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status)      



def declaration_components(request_type, session_id):
	session=session_id
	if(request_type=="other_income"):
		query=AccountsDropdown.objects.filter(field="OTHER INCOME", session=session_id).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
	elif(request_type=="exemptions"):
		query=[]
		quer=AccountsDropdown.objects.filter(field="EXEMPTIONS", session=session_id).exclude(value__isnull=True).exclude(status="DELETE").extra(select={"Value per month":"value"}).values("sno","value")
		for q in quer:
			q_data = AccountsDropdown.objects.filter(pid=q['sno'],session=session_id).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
			query.append({'data':list(q_data),"sno":q['sno'],'value':q['value']})

	elif(request_type=="residence_location"):
		query=AccountsDropdown.objects.filter(field="RESIDENCE LOCATION", session=session_id).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
	elif(request_type=="loss_deductions"):
		query=[]
		quer=AccountsDropdown.objects.filter(field="LOSS/ DEDUCTIONS", session=session_id).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")

		for q in quer:
			if q['value'] != "80D" :
				q_data = AccountsDropdown.objects.filter(pid=q['sno'],value="SUBCATEGORY NAME", session=session_id).exclude(value__isnull=True).exclude(value__contains="UPPER LIMIT").exclude(status="DELETE").values("sno")
				q_data2=AccountsDropdown.objects.filter(pid=q_data[0]['sno'],session=session_id).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
				query.append({'data':list(q_data2),"sno":q['sno'],'value':q['value']})
			else:
				da=[]
				
				q0=AccountsDropdown.objects.filter(value="SELF MEDICLAIM", session=session_id).exclude(status="DELETE").values('sno','value')
				da.append({'sno':q0[0]['sno'],'value':q0[0]['value']})
				
				q2=AccountsDropdown.objects.filter(value="PARENT MEDICLAIM", session=session_id).exclude(status="DELETE").values('sno','value')
				da.append({'sno':q2[0]['sno'],'value':q2[0]['value']})
				
				q3=AccountsDropdown.objects.filter(value="PARENT AGE", session=session_id).exclude(status="DELETE").values('sno','value')
				da.append({'sno':q3[0]['sno'],'value':q3[0]['value']})

				query.append({'data':list(da),"sno":q['sno'],'value':q['value']})

	return query

def getComponents(request):
	data_values={}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337,404,211])
			if check == 200:
				session=getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if(request.method=='GET'):
					if request.GET['request_type'] == 'organization':
						query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="ORGANIZATION").values('sno','value')
					elif request.GET['request_type'] == "department":
						dept_sno=EmployeeDropdown.objects.filter(pid=request.GET['org'],value="DEPARTMENT").values('sno')
						query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'],field="DEPARTMENT").values('sno','value')
					
					elif request.GET['request_type'] == "designation":
						dept_sno=EmployeeDropdown.objects.filter(pid=request.GET['org'],value="DESIGNATION").values('sno')
						query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'],field="DESIGNATION").values('sno','value')
					
					elif request.GET['request_type'] == "multiple_designation":
						emp_cat_sno=EmployeeDropdown.objects.filter(pid__in=request.GET['emp_category'].split(','),value="DESIGNATION").values('sno','field')
						query=[]
						for emp in emp_cat_sno:
							desg=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=emp['sno'],field="DESIGNATION").annotate(emp_category=Value(emp['field'], output_field=CharField())).values('sno','value','emp_category')
							query.extend(desg)
					
					elif request.GET['request_type'] == "emp_category":
						query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="CATEGORY OF EMPLOYEE").values('sno','value')
						
					elif(request.GET["request_type"]=="salary_type"):
						query=AccountsDropdown.objects.filter(field="SALARY TYPE", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
					elif(request.GET["request_type"]=="constant_pay"):
						query=AccountsDropdown.objects.filter(field="CONSTANT PAY DEDUCTIONS", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
					elif(request.GET["request_type"]=="ingredients_name"):
						query=AccountsDropdown.objects.filter(field="SALARY COMPONENTS", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
					
					elif(request.GET["request_type"]=="variable_pay"):
						query=AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
					elif(request.GET["request_type"]=="pay_by"):
						query=AccountsDropdown.objects.filter(field="PAYMENT OPTIONS", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
					elif(request.GET["request_type"]=="department"):
						query=EmployeeDropdown.objects.filter(field="Department").exclude(value__isnull=True).values("sno","value")
					elif(request.GET["request_type"]=="other_income"):
						query=declaration_components(request.GET["request_type"], session)
					elif(request.GET["request_type"]=="exemptions"):
						query=declaration_components(request.GET["request_type"], session)

					elif(request.GET["request_type"]=="residence_location"):
						query=declaration_components(request.GET["request_type"], session)
					elif(request.GET["request_type"]=="loss_deductions"):
						query=declaration_components(request.GET["request_type"], session)

					elif(request.GET["request_type"]=="child_elements"):
						query=AccountsDropdown.objects.filter(pid=request.GET['pid'], session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
					else:
						query=[]
					status=200
					data_values={'data':list(query)}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=data_values,status=status)


def insert_salary_ingredients(request):
	status=401
	response_data={}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[404])
			if check == 200:
				session=getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if(request.method == 'GET'):
					qry_sal=SalaryIngredient.objects.filter(Ingredients=request.GET['id'],session=session).exclude(status="DELETE").values('calcType','Formula','percent','ingredient_nature','next_count_month','taxstatus','id')

					if len(qry_sal)>0:
						qry_app=AccountsElementApplicableOn.objects.filter(salary_ingredient=qry_sal[0]['id']).values('salary_type')
						li=[]
						for i in range(len(qry_app)):
							li.append(qry_app[i]['salary_type'])


						qry_sal[0]['applicable_on'] = li

						if qry_sal[0]['calcType'] == 'F':
							qry_sal[0]['Formula'] = list(map(int,qry_sal[0]['Formula'].split(',')))
					response_data={'data':list(qry_sal)}
					status = 200

				elif(request.method == 'POST'):
					data=json.loads(request.body)
					
					qry_sel_in=(SalaryIngredient.objects.filter(Ingredients=data['id'],session=session).exclude(status="DELETE").values('Ingredients','calcType','Formula','percent','ingredient_nature','next_count_month','taxstatus','added_by','id').order_by('-id')[:1])
					
					if len(qry_sel_in)>0:
						
						################### insert previous value of salary ingredient in case of update##############

						qry_cr=SalaryIngredient.objects.create(session=AccountsSession.objects.get(id=session),Ingredients=AccountsDropdown.objects.get(sno=qry_sel_in[0]['Ingredients']),calcType=qry_sel_in[0]['calcType'],Formula=qry_sel_in[0]['Formula'],percent=qry_sel_in[0]['percent'],ingredient_nature=qry_sel_in[0]['ingredient_nature'],next_count_month=qry_sel_in[0]['next_count_month'],taxstatus=qry_sel_in[0]['taxstatus'],added_by=EmployeePrimdetail.objects.get(emp_id=qry_sel_in[0]['added_by']),status="DELETE")
						
						qry_app=AccountsElementApplicableOn.objects.filter(salary_ingredient=qry_sel_in[0]['id']).values('salary_type')

						qry_sel2=SalaryIngredient.objects.filter(Ingredients=data['id']).values('id').order_by('-id')[:1]

						for a in qry_app:
							qry_element=AccountsElementApplicableOn.objects.create(salary_ingredient=SalaryIngredient.objects.get(id=qry_sel2[0]['id']),salary_type=AccountsDropdown.objects.get(sno=a['salary_type']))

						######################## update salary ingredient ################################################

						
						qry_sal=SalaryIngredient.objects.filter(id=qry_sel_in[0]['id']).update(Ingredients=AccountsDropdown.objects.get(sno=data["id"]),calcType=data['type'],ingredient_nature=data['nature'],next_count_month=datetime.strptime(data['month_year'].split('T')[0], '%Y-%m-%d').date(),taxstatus=data['tax_status'],percent=data['percent'],Formula=','.join(map(str,data['formula'])),added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),status="UPDATE")

						qry_app=AccountsElementApplicableOn.objects.filter(salary_ingredient=SalaryIngredient.objects.get(id=qry_sel_in[0]['id'])).delete()
						
						for a in data['applicable_on']:
							qry_element=AccountsElementApplicableOn.objects.create(salary_ingredient=SalaryIngredient.objects.get(id=qry_sel_in[0]['id']),salary_type=AccountsDropdown.objects.get(sno=a))


						response_data={'msg':"Data Succesfully Updated"}

					else:
						if len(data['formula']) == 0:
							data['formula'] = None
						else:
							data['formula']=','.join(map(str,data['formula']))

						qry_sal=SalaryIngredient.objects.create(session=session,Ingredients=data["id"],calcType=data['type'],ingredient_nature=data['nature'],next_count_month=datetime.strptime(data['month_year'].split('T')[0], '%Y-%m-%d').date(),taxstatus=data['tax_status'],percent=data['percent'],Formula=data['formula'],added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))

						qry_sel=SalaryIngredient.objects.filter(session=session,Ingredients='id').values('id').order_by('-id')[:1]
						
						for a in data['applicable_on']:
							qry_element=AccountsElementApplicableOn.objects.create(salary_ingredient=SalaryIngredient.objects.get(id=qry_sel[0]['id']),salary_type=AccountsDropdown.objects.get(sno=a))


						response_data={'msg':"Data Succesfully Added"}
					status = 200
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=response_data,status=status)


def pay_slip(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[337])
			if check==200:
				if request.method == 'GET':

					emp_id=request.session['hash1']
					taxstatus_li=[0,1]
					
					sdate=(request.GET['month'].split("T"))[0].split('-')
					date=datetime(year=int(sdate[0]),month=int(sdate[1]),day=1)
					
					month=date.month

					months_list=[]
					month_add=4
					while True:
						months_list.append(month_add)
						if month_add==month:
							break
						month_add=max((month_add+1)%13,1)

					session=getCurrentSession(date)
					if session == -1:
						return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

					loss_deductions=[]
					total_loss=[]
					
					########### check whether salary has been locked for the selected month ####
					qry_check1=DaysGenerateLog.objects.filter(sessionid=session,acc_sal_lock='Y',month=month).values()
					if len(qry_check1)>0:
						emp_details = EmployeePayableDays.objects.filter(emp_id=emp_id,month=month,session=session).annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','emp_id__doj','bank_Acc_no','uan_no','total_days','working_days','leave','holidays','emp_id__title__value')

						total_days=emp_details[0]['total_days']
						working_days=emp_details[0]['working_days']+emp_details[0]['leave']+emp_details[0]['holidays']

						###################### get stored values of salary components for the selected month ################
						gross_payable=stored_gross_payable_salary_components(emp_id,session,month)

						###################### get stored values of arrear for the selected month ################
						
						arrear = stored_arrear(emp_id,month,session)

						###################### get stored values of constant deductions for the selected month ################
						
						const_ded = calculate_constant_deduction_stored(emp_id,session,gross_payable,taxstatus_li,month)
						###################### get stored values of variable deductions for the selected month ################
						
						var_ded = calculate_variable_deduction_stored(emp_id,session,month)
						
						arrear_value=0
						arrear_list=[]

						arrear_list=arrear['data']

						#################### calculate net amount on which income tax is to be calculated #######################
						################# arrear_list[0]['value']  = additional arrear value ##############3
						################# arrear_list[1]['value']  = sign in/out arrear  ##############3
						################# arrear_list[2]['value']  = DA arrear  ##############3
						################# arrear_list[3]['value']  = Leave/Days arrear  ##############3
						################# arrear_list[4]['value']  = increment arrear  ##############3
						
						##########################   calculate_income_tax_sum(emp_id,session,working_days,actual_days,gross_payable_data,salary_month,payable_da_arrear,payable_inc_arrear,payable_days_arrear,additional_arrear,payable_sign_arrear) ###############

						income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,total_days,gross_payable,month,arrear_list[2],arrear_list[4],arrear_list[3]['value'],arrear_list[0]['value'],arrear_list[1]['value'])
						
						income_tax_sum=0
						income_tax_sum_comp_data=[]

						############ iterate for  all income tax components value i.e BASIC,AGP,HRA etc. ##############
						for d in income_tax_sum_comp:
							income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value']})
							income_tax_sum+=d['value']
							
						income_tax_sum_comp_data.append({'value':income_tax_sum,'Ing_value':'TOTAL'})
						
						########### calculate epf (constant deduction) to be deducted from employee's salary for that month #########3
						total_epf=calculate_epf(emp_id,session,[0,1],gross_payable)
						income_tax_sum_comp_data.append({'value':total_epf['value'],'Ing_value':'EPF'})

						############ calculate other income declared by employee ##########
						other_income=calculate_other_income(emp_id,session)

						##################################################

						hra_for1=0
						for comp in income_tax_sum_comp:
							if 'HRA' in comp['Ing_value']:
								hra_for1+=comp['value']

						#hra_for1=hra_exemption_formula1(emp_id,session,working_days,total_days,month)
						hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
						hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

						##################### get minimum of hra1,hra2,hra3 values. If value is <0, make it 0 using max(-ve value,0) ######
						hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

						################### calculate loss deductions declared by employee in 12B form. It include 80C,80D,80CCD etc. ####
						loss=calculate_loss_deductions(emp_id,session,gross_payable,const_ded)


						################## get standard deduction value ##########################
						qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
						std_ded_amt = int(qry_std_ded[0]['value'])

						############# calculate value on which income tax is to be calculated ################

						############# add income tax components value(i.e. BASIC+AGP+HRA etc.)+ other income total value - minimum of hra exemption value - loss and deductions final value (80C value +80D Value+....) - standard deduction amount ######

						########### if value is <0, make it 0 #####################
						final_value = max(other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt,0)
						
						########## calculate income tax on final value ###################
						income_tax=calculate_income_tax(emp_id,session,final_value)
						
						########## calculate rebate offered on income tax, tax after rebate and cess amount to be paid ###############
						tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
							
						#final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)

						
						############ get income tax to be paid in that selected month #######################3
						q_IT = Income_Tax_Paid.objects.filter(emp_id=emp_id,session=session,month=month).values('monthly_tax_paid')
						if len(q_IT)>0:
							income_tax=q_IT[0]['monthly_tax_paid']
						else:
							income_tax=0
						
						################### loss and deductions ################################################

						time=datetime.now()
						
						################ get other income components ###############
						other_income=declaration_components("other_income", session)
						n=len(other_income)
						total=0

						############## get their value as declared by employee #############
						for i in range(n):
							q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id,Dec_Id=other_income[i]['sno'],Session_Id=AccountsSession.objects.get(id=session),Value__gt=0).values('Value').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_dec)>0:
								total+=q_dec[0]['Value']
								loss_deductions.append({"country":"OTHER INCOME","name":other_income[i]['value'],"money":q_dec[0]['Value']})
						total_loss.append({"field":"OTHER INCOME",'value':total})
						
						################ get house rent allowance components i.e. rent per month and number of months ###############
						
						exemptions=declaration_components("exemptions", session)
						total=1
						n=len(exemptions[0]['data'])
						for i in range(n):
							q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id,Dec_Id=exemptions[0]['data'][i]['sno'],Session_Id=session).values('Value').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_dec)>0:
								loss_deductions.append({"country":"EXEMPTIONS","name":exemptions[0]['data'][i]['value'],"money":q_dec[0]['Value']})
								total*=q_dec[0]['Value']
	
							else:
								loss_deductions.append({"country":"EXEMPTIONS","name":exemptions[0]['data'][i]['value'],"money":0})
						
						if total==1:
							total=0
						total_loss.append({"field":"EXEMPTIONS",'value':total})
						
						################ get 80C, 80D, 80CCD components, it include LIC,LIP ,ULIP etc. ############
						loss=declaration_components("loss_deductions", session)
						m=len(loss)

						######### get value as declared by employee ###############################################
						for j in range(m):
							total=0
							n=len(loss[j]['data'])
							for i in range(n):
								q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id,Dec_Id=loss[j]['data'][i]['sno'],Session_Id=session,Value__gt=0).values('Value').exclude(status="DELETE").order_by('-id')[:1]
								if len(q_dec)>0:
									total+=q_dec[0]['Value']
									loss_deductions.append({"country":loss[j]['value'],"name":loss[j]['data'][i]['value'],"money":q_dec[0]['Value']})
							total_loss.append({"field":loss[j]['value'],'value':total})
						
						upto_values=[]
						total_v=0

						qry_sal_ing = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values('id','Ingredients__value')

						######################## get sum of salary components value already paid to employee #########

						######### e.g for month of july , for basic, its value will be april basic+may basic + june basic+ july basic #####
						for gp in qry_sal_ing:
							dj_val= MonthlyPayable_detail.objects.filter(Emp_Id=emp_id,session=session,Ing_Id=gp['id'],Month__in=months_list).extra(select={'su':'SUM(payable_value)'}).values('su')
							if len(dj_val)>0:
								if(dj_val[0]['su'] is None):
									dj_val[0]['su']=0
								upto_values.append({'field':gp['Ingredients__value'],'value':dj_val[0]['su']})
								total_v+=dj_val[0]['su']
							else:
								upto_values.append({'field':gp['Ingredients__value'],'value':0})

						########## get arrear value received to employee upto that month #############################
						q_arrear = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,session=session,Month__in=months_list).extra(select={'su':'SUM(value)'}).values('su')
						if len(q_arrear)>0:
							upto_values.append({'field':'ARREAR','value':q_arrear[0]['su']})
							total_v+=q_arrear[0]['su']
						else:
							upto_values.append({'field':'ARREAR','value':0})

						upto_values.append({'field':'TOTAL','value':total_v})

						############# get EPF deducted from employee salary upto that month  ############
						epf_paid= MonthlyDeductionValue.objects.filter(deduction_id__constantDeduction__DeductionName__value="EPF",Emp_Id=emp_id,deduction_id__variableDeduction__isnull=True,session=session,month__in=months_list).values('value')
						total_e=0
						for ep in epf_paid:
							total_e+=ep['value']
						upto_values.append({'field':'EPF','value':total_e})

						############# get mediclaim deducted from employee salary upto that month ############3
						
						med_paid= MonthlyDeductionValue.objects.filter(deduction_id__constantDeduction__DeductionName__value="MEDICLAIM",Emp_Id=emp_id,session=session,month__in=months_list).values('value')
						total_m=0
						for me in med_paid:
							total_m+=me['value']
						upto_values.append({'field':'MEDICLAIM','value':total_m})

						###################  get income tax paid by employee upto that month ######################
						q_it = Income_Tax_Paid.objects.filter(emp_id=emp_id,session=session,month__in=months_list).extra(select={'su':'SUM(monthly_tax_paid)'}).values('su')
						if len(q_it)>0:
							tax_paid=q_it[0]['su']
						else:
							tax_paid=0

						q_Sess = AccountsSession.objects.filter(id=session).values('session')
						msg="Success"
						status=200
						data_values={'msg':msg,'data':{'emp_details':list(emp_details),'gross_payable':gross_payable,'arrear':arrear,'const_ded':const_ded,'var_ded':var_ded,'income_tax':income_tax,'total_days':total_days,'working_days':working_days,'loss_deductions':loss_deductions,'total_loss':total_loss,'upto_values':upto_values,'net_income':final_value,'net_income_tax':tax_after_rebate['final_tax'],'tax_paid':tax_paid,'tax_left':tax_after_rebate['final_tax']-tax_paid,'proposed_year':income_tax_sum_comp_data,'monthly_arrear':arrear['final_value'],'session':q_Sess[0]['session']}}
					else:
						msg="Salary slip not available"
						status=202
						data_values={'msg':msg}

					
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status)         
	

def get_salary_ingredient_details(emp_id,salary_type,taxstatus_li,session):
	if salary_type  is not None:
		qry_sal_ing=AccountsElementApplicableOn.objects.filter(salary_type=salary_type,salary_ingredient__taxstatus__in=taxstatus_li,constantDeduction=None).exclude(salary_ingredient__status="DELETE").filter(salary_ingredient__session=session).values('salary_ingredient__Ingredients','salary_ingredient__calcType','salary_ingredient__percent','salary_ingredient__ingredient_nature','salary_ingredient__taxstatus','salary_ingredient__Ingredients__value','salary_ingredient__Formula','salary_ingredient','salary_ingredient__next_count_month',"salary_type__value").order_by('salary_ingredient')
		n=len(qry_sal_ing)
		for i in range(n):
			
			if qry_sal_ing[i]['salary_ingredient__Ingredients__value'] == 'AGP':
				qry_vl=AccountsDropdown.objects.filter(pid=qry_sal_ing[i]['salary_ingredient__Ingredients'], session=session).exclude(value__isnull=True).values_list('value',flat=True)
				qry_sal_ing[i]['values_list'] = list(qry_vl)
			else:
				qry_sal_ing[i]['values_list']=[]

			if qry_sal_ing[i]['salary_ingredient__ingredient_nature'] == 1:
				qry_sal_ing[i]['salary_ingredient__ingredient_nature'] = "MONTHLY"
			elif qry_sal_ing[i]['salary_ingredient__ingredient_nature'] == 3:
				qry_sal_ing[i]['salary_ingredient__ingredient_nature'] = "QUATERLY"
			elif qry_sal_ing[i]['salary_ingredient__ingredient_nature'] == 6:
				qry_sal_ing[i]['salary_ingredient__ingredient_nature'] == "HALF YEARLY"
			elif qry_sal_ing[i]['salary_ingredient__ingredient_nature'] == 12:
				qry_sal_ing[i]['salary_ingredient__ingredient_nature'] == 'YEARLY'
			elif qry_sal_ing[i]['salary_ingredient__ingredient_nature'] == -1:
				qry_sal_ing[i]['salary_ingredient__ingredient_nature'] = "LIFETIME"


			if qry_sal_ing[i]['salary_ingredient__taxstatus'] == 1:
				qry_sal_ing[i]['salary_ingredient__taxstatus'] = "TAXABLE"
			else:
				qry_sal_ing[i]['salary_ingredient__taxstatus'] = "EXEMPTED"


			if qry_sal_ing[i]['salary_ingredient__calcType'] == 'F':
				qry_sal_ing[i]['salary_ingredient__Formula'] =  list(map(int,str(qry_sal_ing[i]['salary_ingredient__Formula']).split(',')))

			############ get gross of inserted value of salary component ####################
			qry_ch=EmployeeGross_detail.objects.filter(Ing_Id=qry_sal_ing[i]['salary_ingredient'],Emp_Id=emp_id).filter(session=session).exclude(Status="DELETE").values('Value')
			if len(qry_ch) == 0:
				qry_sal_ing[i]['prev_value'] = 0
			else:
				qry_sal_ing[i]['prev_value'] = qry_ch[0]['Value']

			key = (qry_sal_ing[i]['salary_ingredient__Ingredients__value']+"_"+qry_sal_ing[i]['salary_type__value']).replace(" ","_")
			qry_sal_ing[i][key] = qry_sal_ing[i]['prev_value']
	else:
		qry_sal_ing=[]

	return list(qry_sal_ing)


################### get constant deductions of employee as defined by employee pay detail form ################
def get_constant_deductions_salary_filter(emp_id,salary_type,session):
	if salary_type  is not None:
					
		qry_cons=AccountsElementApplicableOn.objects.filter(salary_type=AccountsDropdown.objects.get(sno=salary_type),salary_ingredient=None).exclude(constantDeduction__status="DELETE").values('constantDeduction','constantDeduction__DeductionName__value')
		for q in range(len(qry_cons)):
			q_ch = EmployeeDeductions.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),constantDeduction=ConstantDeduction.objects.get(id=qry_cons[q]['constantDeduction'])).filter(session=AccountsSession.objects.get(id=session)).exclude(status="DELETE")

			if len(q_ch) == 0:
				qry_cons[q]["selected"]=False
			else:
				qry_cons[q]["selected"]=True
	else:
		qry_cons=[]

	return list(qry_cons)

################### get variable deductions of employee as defined by employee pay detail form ################

def get_variable_deductions_emp_filter(emp_id,session):
	
	query=AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")

	for q in range(len(query)):
		q_ch = EmployeeDeductions.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),variableDeduction=AccountsDropdown.objects.get(sno=query[q]['sno'])).filter(session=AccountsSession.objects.get(id=session)).exclude(status="DELETE")

		if len(q_ch) == 0:
			query[q]["selected"]=False
		else:
			query[q]["selected"]=True
	
	return list(query)

################### calculate employee age for that financial year (april-march) ################
################### if dob month of employee is October and his current age is 51 (in april), then  his age will be considered as 52 for the whole year i.e in april also, his age wil be treated as 52. It is used in calculating self mediclaim value #################
def calculate_emp_age(emp_id,session):

	q_age = EmployeePerdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)).values('dob')
	qry_session=AccountsSession.objects.filter(id=session).values('Tdate','Fdate')

	if q_age[0]['dob'] is None or q_age[0]['dob'] == '':
		return 0

	today = date.today()
	birth_date = datetime(year=today.year, month=q_age[0]['dob'].month, day=q_age[0]['dob'].day).date()
	age=today.year - q_age[0]['dob'].year - ((today.month, today.day) < (q_age[0]['dob'].month, q_age[0]['dob'].day))

	if birth_date > datetime.strptime((str(qry_session[0]['Fdate'])), '%Y-%m-%d').date():
		age = birth_date.year - q_age[0]['dob'].year
	else:
		age = birth_date.year - q_age[0]['dob'].year + 1
	
	return age
	
def insert_employee_pay_detail(value_ingredients,constant_deductions,variable_deductions,emp_id,session,bank_Acc_no,uan_no,pay_by,salary_type,hash1,aadhar_num,pan_no):
	n=len(value_ingredients)
	extra={}
	if pan_no is not None and pan_no != '':
		extra["pan_no"]=pan_no
	else:
		extra["pan_no"]=None

	if aadhar_num is not None and aadhar_num != '':
		extra["aadhar_num"]=aadhar_num
	else:
		extra["aadhar_num"]=None
	qry_per_detail=EmployeePerdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)).update(bank_Acc_no=bank_Acc_no,uan_no=uan_no,**extra)

	
	qry_up=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session)).update(Status="DELETE")
		
	############## VALUE WISE INGREDIENTS INSERT/ UPDATE ###################33

	for ind in range(n):
		qry_check_sal=SalaryIngredient.objects.filter(id=value_ingredients[ind]['id']).exclude(status="DELETE").values('calcType')
		if qry_check_sal[0]['calcType'] == 'V':
			qry_ins=EmployeeGross_detail.objects.exclude(Status="DELETE").update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Ing_Id=SalaryIngredient.objects.get(id=value_ingredients[ind]['id']),session=AccountsSession.objects.get(id=session),defaults={'Value':int(round(value_ingredients[ind]['value'])),'added_by':EmployeePrimdetail.objects.get(emp_id=hash1),'pay_by':AccountsDropdown.objects.get(sno=pay_by),'salary_type':AccountsDropdown.objects.get(sno=salary_type)})
	
	qry_ch1=list(EmployeeDeductions.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session)).exclude(status="DELETE").values_list('id',flat=True))
	qry_up1=EmployeeDeductions.objects.filter(id__in=qry_ch1).update(status="DELETE")

	objs = (EmployeeDeductions(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),constantDeduction=ConstantDeduction.objects.get(id=c),added_by=EmployeePrimdetail.objects.get(emp_id=hash1)) for c in constant_deductions)

	emp_deductions = EmployeeDeductions.objects.bulk_create(objs)

	objs = (EmployeeDeductions(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),variableDeduction=AccountsDropdown.objects.get(sno=v),added_by=EmployeePrimdetail.objects.get(emp_id=hash1)) for v in variable_deductions)

	emp_deductions = EmployeeDeductions.objects.bulk_create(objs)

def employee_pay_detail(request):
	response_data={}
	msg=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[404])
			if(check == 200):
				session = getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if(request.method == 'GET'):
					if 'request_type' in request.GET:
						if request.GET['request_type'] == "salary_type":
							query=AccountsDropdown.objects.filter(field="SALARY TYPE", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
							qry=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.GET['emp_id'])).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").extra(select={'sno':'salary_type'}).values('sno','salary_type__value')

							salary_type=None
							if len(qry)>0:
								qry[0]['value']=qry[0]['salary_type__value']
								del qry[0]['salary_type__value']
							
								salary_type=qry[0]

							status=200
							response_data={'salary_type_data':list(query),'selected_salary_type_id':salary_type}
					else:

						qry_detail=EmployeePerdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.GET['emp_id'])).values('bank_Acc_no','uan_no','aadhar_num','pan_no')
	
						qry=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.GET['emp_id'])).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('pay_by')

						if len(qry) == 0:
							pay_by=None
						else:
							pay_by=qry[0]['pay_by']
							
						taxstatus_li=[0,1]
						response_data={'salary_ingredient':get_salary_ingredient_details(request.GET['emp_id'],request.GET['salary_type'],taxstatus_li,session),'constant_deductions':get_constant_deductions_salary_filter(request.GET['emp_id'],request.GET['salary_type'],session),'variable_deductions':get_variable_deductions_emp_filter(request.GET['emp_id'],session),'bank_Acc_no':qry_detail[0]['bank_Acc_no'],'uan_no':qry_detail[0]['uan_no'],'pay_by':pay_by,'aadhar_num':qry_detail[0]['aadhar_num'],'pan_no':qry_detail[0]['pan_no']}
						#print(response_data)
					
					status=200

				elif request.method == 'POST':
					data=json.loads(request.body)
					value_ingredients=data['salary_ingredient']
					constant_deductions=list(map(int,data['constant_deductions']))
					variable_deductions=list(map(int,data['variable_deductions']))
					bank_Acc_no=data['bank_Acc_no']
					uan_no=data['uan_no']
					pay_by=data['pay_by']
					salary_type=data['salary_type']
					aadhar_num=data['aadhar_num']
					pan_no=data['pan_no']
					emp_id=data['emp_id']
					
					insert_employee_pay_detail(value_ingredients,constant_deductions,variable_deductions,emp_id,session,bank_Acc_no,uan_no,pay_by,salary_type,request.session['hash1'],aadhar_num,pan_no)
					msg = "Data Succesfully Added"

					month=getSalaryMonth(session)
					q_upd = DaysGenerateLog.objects.filter(sessionid=session,acc_sal_lock='N',month=month).update(tdsSheet=None,salarySheet=None)
					
					response_data={'msg':msg}

					status = 200
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=response_data,status=status)



def all_employee_pay_detail(request):
	response_data={}
	msg=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[404])
			if(check == 200):
				session = getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if(request.method == 'GET'):
					if request.GET['request_type'] == 'pay_detail':
						designation_list = request.GET['designation'].split(',')
						department_list = request.GET['department'].split(',')

						qry_agp_dropdown = list(AccountsDropdown.objects.filter(field='AGP', session=session).exclude(value__isnull=True).values_list('value',flat=True))
								
						############## ALL SALARY INGREDIENTS ########################
						qry_sal=list(SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values('calcType','Formula','percent','ingredient_nature','next_count_month','taxstatus','id','Ingredients','Ingredients__value').order_by('-calcType'))

						for sal in qry_sal:
							qry_app=AccountsElementApplicableOn.objects.filter(salary_ingredient=sal['id']).values_list('salary_type',flat=True)
							sal['applicable_on'] = list(qry_app)

							if sal['calcType'] == 'F':
								sal['Formula'] = list(map(int,sal['Formula'].split(',')))

						qry_emps = EmployeePrimdetail.objects.filter(desg__in=designation_list,dept__in=department_list,emp_status='ACTIVE').exclude(emp_type=219).values('emp_id','name','dept__value','desg__value','emp_category__value')

						data=[]
						emp_const_ded = []
						emp_var_ded = []

						for emp in qry_emps:
							qry_acc_no = EmployeePerdetail.objects.filter(emp_id=emp['emp_id']).values('bank_Acc_no','uan_no','aadhar_num','pan_no')

							qry_pay_by = EmployeeGross_detail.objects.filter(Emp_Id=emp['emp_id'],session=session).exclude(Status="DELETE").values('pay_by','salary_type')[:1]

							if len(qry_pay_by) == 0:
								pay_by=None
								salary_type=None
							else:
								pay_by=qry_pay_by[0]['pay_by']
								salary_type=qry_pay_by[0]['salary_type']
								
							taxstatus_li=[0,1]

							############## SALARY COMPONENTS #####################

							emp_salary = copy.deepcopy(qry_sal)
								
							sal_data={}
							sal_selected={}
							sal_enabled={}
							
							for sal in emp_salary:
								qry_ch=EmployeeGross_detail.objects.filter(Ing_Id=sal['id'],Emp_Id=emp['emp_id']).filter(session=session).exclude(Status="DELETE").values('Value')
								if len(qry_ch) == 0:
									################## comp_BASIC_5_value ############################

									sal_data["comp_"+sal['Ingredients__value'].replace(" ","_")+"_"+str(sal['id'])+"_value"] = 0

								else:
									sal_data["comp_"+sal['Ingredients__value'].replace(" ","_")+"_"+str(sal['id'])+"_value"] = qry_ch[0]['Value']

								if salary_type in sal['applicable_on']:
									################## comp_BASIC_5_selected ############################
									
									sal_selected["comp_"+sal['Ingredients__value'].replace(" ","_")+"_"+str(sal['id'])+"_selected"] = True
								else:
									sal_selected["comp_"+sal['Ingredients__value'].replace(" ","_")+"_"+str(sal['id'])+"_selected"] = False

								if sal['calcType'] == 'V':
									################## comp_BASIC_5_enabled ############################
									
									sal_enabled["comp_"+sal['Ingredients__value'].replace(" ","_")+"_"+str(sal['id'])+"_enabled"] = True
								else:
									sal_enabled["comp_"+sal['Ingredients__value'].replace(" ","_")+"_"+str(sal['id'])+"_enabled"] = False
							
							############## CONSTANT DEDUCTIONS ##########################

							emp_const_ded = get_constant_deductions_salary_filter(emp['emp_id'],salary_type,session)
							const_ded_data={}
							
							for const in emp_const_ded:
								################## const_EPF_5_selected ############################
									
								const_ded_data['const_'+const['constantDeduction__DeductionName__value'].replace(" ","_")+"_"+str(const['constantDeduction'])+"_selected"] = const['selected']

							############## VARIABLE DEDUCTIONS ###########################

							emp_var_ded = get_variable_deductions_emp_filter(emp['emp_id'],session)
							var_ded_data={}
							
							for var in emp_var_ded:
								################## var_ELECTRICITY_5_selected ############################
								
								var_ded_data['var_'+var['value'].replace(" ","_")+"_"+str(var['sno'])+"_selected"] = var['selected']
							
							emp_data = {'salary_total':0,'bank_Acc_no':qry_acc_no[0]['bank_Acc_no'],'uan_no':qry_acc_no[0]['uan_no'],'aadhar_num':qry_acc_no[0]['aadhar_num'],'pan_no':qry_acc_no[0]['pan_no'],'pay_by':pay_by,'emp_id':emp['emp_id'],'emp_name':emp['name'],'dept':emp['dept__value'],'desg':emp['desg__value'],'salary_type':salary_type}
							
							emp_data.update(sal_data)
							emp_data.update(sal_selected)
							emp_data.update(sal_enabled)

							emp_data.update(const_ded_data)
							emp_data.update(var_ded_data)
							
							data.append(emp_data)

						status=200
						response_data={'data':data,'agp_dropdown':qry_agp_dropdown,'salary_ingredients':qry_sal,'constant_deductions':emp_const_ded,'variable_deductions':emp_var_ded}
						#print(response_data)
				elif request.method == 'POST':
					data = json.loads(request.body)
					emp_data = data['emp_data']

					for emp in emp_data:
						value_ingredients=emp['salary_ingredient']
						constant_deductions=list(map(int,emp['constant_deductions']))
						variable_deductions=list(map(int,emp['variable_deductions']))
						bank_Acc_no=emp['bank_Acc_no']
						uan_no=emp['uan_no']
						pay_by=emp['pay_by']
						aadhar_num=emp['aadhar_num']
						pan_no=emp['pan_no']
						salary_type=emp['salary_type']
						emp_id=emp['emp_id']

						insert_employee_pay_detail(value_ingredients,constant_deductions,variable_deductions,emp_id,session,bank_Acc_no,uan_no,pay_by,salary_type,request.session['hash1'],aadhar_num,pan_no)

					status = 200
					response_data = {'msg':'Pay Details Succesfully Updated'}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=response_data,status=status)


def locking_unlocking(request):
	data_values={}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				if request.method=='GET':
					qry=LockingUnlocking.objects.extra(select={'fromDate':"DATE_FORMAT(fromDate,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('Emp_Id','Emp_Id__name','fromDate','toDate').order_by('-id')
					data_values = {'data':list(qry)}
					status=200

				elif request.method == 'POST':
					data=json.loads(request.body)
					emp_id=data['emp_id']
					dept=data['dept']
					fromDate=datetime.strptime(str(data['fromDate']),"%Y-%m-%d %H:%M:%S")
					toDate=datetime.strptime(str(data['toDate']),"%Y-%m-%d %H:%M:%S")

					if dept == 'ALL':
						dept_sno=EmployeeDropdown.objects.filter(pid=data['org'],value="DEPARTMENT").values('sno')
						query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'],field="DEPARTMENT").values('sno','value')
						for d in query:
							s=get_all_emp(d['sno'])
							objs = (LockingUnlocking(Emp_Id=EmployeePrimdetail.objects.get(emp_id=e['emp_code']),fromDate=fromDate,toDate=toDate,unlocked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])) for e in s)
							q=LockingUnlocking.objects.bulk_create(objs)

					elif emp_id == 'ALL':
						s=get_all_emp(dept)
						objs = (LockingUnlocking(Emp_Id=EmployeePrimdetail.objects.get(emp_id=e['emp_code']),fromDate=fromDate,toDate=toDate,unlocked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])) for e in s)
						q=LockingUnlocking.objects.bulk_create(objs)
					else:
						qry_ins = LockingUnlocking.objects.create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),fromDate=fromDate,toDate=toDate,unlocked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))

					msg="Data Succesfully Inserted"
					data_values = {'msg':msg}
					status=200
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status)


def emp_declaration_form(request):
	data_values=[]
	status=401

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[337])
			if check==200:
				session=getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if request.method == 'GET':
					request_type=request.GET['request_type']
					if request.GET['request_type'] == "other_income":
						time=datetime.now()
						qry_check=LockingUnlocking.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),toDate__gte=time,status="INSERT").order_by('-id')[:1].values('fromDate','toDate')

						if len(qry_check)==0:
							locked=True
						else:
							locked=False

						q_check = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),Session_Id=AccountsSession.objects.get(id=session),Verified='Y').exclude(status="DELETE").order_by('-id')[:1]
						if len(q_check) == 0:
							verified=False
						else:
							verified=True

						other_income=declaration_components(request_type, session)
						n=len(other_income)
						for i in range(n):
							q_dec = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),Dec_Id=AccountsDropdown.objects.get(sno=other_income[i]['sno']),Session_Id=AccountsSession.objects.get(id=session)).values('Value').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_dec)>0:
								other_income[i]['prev_value']=q_dec[0]['Value']
							else:
								other_income[i]['prev_value']=0
						data_values={'data':list(other_income),'locked':locked,'verified':verified}
						status=200

					elif request.GET['request_type'] == "exemptions":
						exemptions=declaration_components(request_type, session)
						n=len(exemptions[0]['data'])
						for i in range(n):
							q_dec = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),Dec_Id=AccountsDropdown.objects.get(sno=exemptions[0]['data'][i]['sno']),Session_Id=AccountsSession.objects.get(id=session)).values('Value').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_dec)>0:
								exemptions[0]['data'][i]['prev_value']=q_dec[0]['Value']
							else:
								exemptions[0]['data'][i]['prev_value']=0
						data_values=list(exemptions)
						status=200

					elif request.GET['request_type'] == "loss_deductions":
						loss=declaration_components(request_type, session)
						m=len(loss)
						for j in range(m):
							n=len(loss[j]['data'])
							for i in range(n):
								q_dec = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),Dec_Id=AccountsDropdown.objects.get(sno=loss[j]['data'][i]['sno']),Session_Id=AccountsSession.objects.get(id=session)).values('Value').exclude(status="DELETE").order_by('-id')[:1]
								if len(q_dec)>0:
									loss[j]['data'][i]['prev_value']=q_dec[0]['Value']
								else:
									loss[j]['data'][i]['prev_value']=0
						data_values=list(loss)
						status=200

					elif request.GET['request_type'] == "residence_location":
						residence=declaration_components(request_type, session)
						n=len(residence)
						for i in range(n):
							q_dec = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),Dec_Id=AccountsDropdown.objects.get(sno=residence[i]['sno']),Session_Id=AccountsSession.objects.get(id=session)).values('Value').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_dec)>0:
								residence[i]['prev_value']=True
							else:
								residence[i]['prev_value']=False
						data_values=list(residence)
						status=200
					
				elif request.method == 'POST':
					data = json.loads(request.body)
					emp_id=request.session['hash1']
					for other_income in data['income']:
						if other_income['prev_value'] is not None :
							ins,upd = Employee_Declaration.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=other_income['sno']),Session_Id=AccountsSession.objects.get(id=session),defaults={'Value':other_income['prev_value']})
						else:
							dele = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=other_income['sno']),Session_Id=AccountsSession.objects.get(id=session)).delete()

					for exemptions in data['exemption']:
						for e in exemptions['data']:
							if e['prev_value'] is not None:
								ins,upd = Employee_Declaration.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=e['sno']),Session_Id=AccountsSession.objects.get(id=session),defaults={'Value':e['prev_value']})
							else:
								dele = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=e['sno']),Session_Id=AccountsSession.objects.get(id=session)).delete()

					for loss in data['loss']:
						for l in loss['data']:
							if l['prev_value'] is not None:
								ins,upd = Employee_Declaration.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=l['sno']),Session_Id=AccountsSession.objects.get(id=session),defaults={'Value':l['prev_value']})
							else:
								dele = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=l['sno']),Session_Id=AccountsSession.objects.get(id=session)).delete()

					for residence in data['residence']:
						if residence['prev_value'] is not False:
							ins,upd = Employee_Declaration.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=residence['sno']),Session_Id=AccountsSession.objects.get(id=session),defaults={'Value':None})
						else:
							dele = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=residence['sno']),Session_Id=AccountsSession.objects.get(id=session)).delete()


					msg="Data Succesfully Inserted"
					data_values={'msg':msg}

					status=200
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data={"data":data_values},status=status)

def emp_declaration_approval(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				session=getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if request.method == 'GET':
					request_type=request.GET['request_type']
					if request.GET['request_type'] == 'employee_status':
						dept=request.GET['dept']
						emp=EmployeePrimdetail.objects.filter(dept=dept,emp_status="ACTIVE").exclude(emp_type=219).order_by('name').values('emp_id','name')
						n=len(emp)
						for i in range(n):
							q_status=Employee_Declaration.objects.filter(Emp_Id=emp[i]['emp_id'],Session_Id=session).values('Verified','Dec_Id').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_status)>0:
								if q_status[0]['Verified'] == 'N':
									emp[i]['status']="PENDING"
									emp[i]['count']=0
									
								else:
									emp[i]['status']="VERIFIED"
									q_count=Employee_Declaration.objects.filter(Emp_Id=emp[i]['emp_id'],Session_Id=session,Verified='Y',Dec_Id=q_status[0]['Dec_Id']).values('Verified').exclude(status="DELETE").count()
									emp[i]['count']=q_count
							else:
								emp[i]['count']=0
								emp[i]['status']="NOT FILLED"

						data_values={'data':list(emp)}
						status=200

					elif request.GET['request_type'] == "other_income":
						other_income=declaration_components(request_type, session)
						emp_id=request.GET['emp_id']
						n=len(other_income)
						for i in range(n):
							q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id,Dec_Id=other_income[i]['sno'],Session_Id=session).values('Value').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_dec)>0:
								other_income[i]['prev_value']=q_dec[0]['Value']
							else:
								other_income[i]['prev_value']=0
						data_values=list(other_income)
						status=200

					elif request.GET['request_type'] == "exemptions":
						emp_id=request.GET['emp_id']
						exemptions=declaration_components(request_type, session)
						n=len(exemptions[0]['data'])
						for i in range(n):
							q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id,Dec_Id=exemptions[0]['data'][i]['sno'],Session_Id=session).values('Value').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_dec)>0:
								
								exemptions[0]['data'][i]['prev_value']=q_dec[0]['Value']
								
							else:
								exemptions[0]['data'][i]['prev_value']=0
						data_values=list(exemptions)
						status=200

					elif request.GET['request_type'] == "loss_deductions":
						emp_id=request.GET['emp_id']
						loss=declaration_components(request_type, session)
						m=len(loss)
						for j in range(m):
							n=len(loss[j]['data'])
							for i in range(n):
								q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id,Dec_Id=loss[j]['data'][i]['sno'],Session_Id=session).values('Value').exclude(status="DELETE").order_by('-id')[:1]
								if len(q_dec)>0:
									
									loss[j]['data'][i]['prev_value']=q_dec[0]['Value']
									
								else:
									loss[j]['data'][i]['prev_value']=0
						data_values=list(loss)
						status=200

					elif request.GET['request_type'] == "residence_location":
						emp_id=request.GET['emp_id']
						residence=declaration_components(request_type, session)
						n=len(residence)
						for i in range(n):
							q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id,Dec_Id=residence[i]['sno'],Session_Id=session).values('Value').exclude(status="DELETE").order_by('-id')[:1]
							if len(q_dec)>0:
								residence[i]['prev_value']=True
							else:
								residence[i]['prev_value']=False
						data_values=list(residence)
						status=200

				elif request.method == 'POST':
					data=json.loads(request.body)
					emp_id=data['emp_id']
					for other_income in data['income']:
						if other_income['prev_value'] is not None :
							upd = Employee_Declaration.objects.filter(Emp_Id=emp_id,Dec_Id=other_income['sno'],Session_Id=session).update(status="DELETE")

							ins = Employee_Declaration.objects.create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=other_income['sno']),Session_Id=AccountsSession.objects.get(id=session),Value=other_income['prev_value'],Verified='Y',Verified_By=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
						else:
							dele = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=other_income['sno']),Session_Id=AccountsSession.objects.get(id=session)).delete()

					for exemptions in data['exemption']:
						for e in exemptions['data']:
							if e['prev_value'] is not None:
								upd = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=e['sno']),Session_Id=AccountsSession.objects.get(id=session)).update(status="DELETE")

								ins = Employee_Declaration.objects.create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=e['sno']),Session_Id=AccountsSession.objects.get(id=session),Value=e['prev_value'],Verified='Y',Verified_By=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
							else:
								dele = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=e['sno']),Session_Id=AccountsSession.objects.get(id=session)).delete()

					for loss in data['loss']:
						for l in loss['data']:
							if l['prev_value'] is not None:
								upd = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=l['sno']),Session_Id=AccountsSession.objects.get(id=session)).update(status="DELETE")

								ins = Employee_Declaration.objects.create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=l['sno']),Session_Id=AccountsSession.objects.get(id=session),Value=l['prev_value'],Verified='Y',Verified_By=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
							else:
								dele = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=l['sno']),Session_Id=AccountsSession.objects.get(id=session)).delete()

					for residence in data['residence']:
						if residence['prev_value'] is not False:
							upd = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=residence['sno']),Session_Id=AccountsSession.objects.get(id=session)).update(status="DELETE")

							ins = Employee_Declaration.objects.create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=residence['sno']),Session_Id=AccountsSession.objects.get(id=session),Verified='Y',Verified_By=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
						else:
							dele = Employee_Declaration.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Dec_Id=AccountsDropdown.objects.get(sno=residence['sno']),Session_Id=AccountsSession.objects.get(id=session)).delete()


					msg="Data Succesfully Verified"
					data_values={'msg':msg}

					status=200


				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data={"data":data_values},status=status) 

def Constant_pay_deduction(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[404])
			if(check == 200):
				session=getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if(request.method=='POST'):
					data=json.loads(request.body)
					deduction_name=data['deduction_name']
					deduction_type=data['deduction_type']
					if deduction_type == 'F':
						formula=",".join(map(str,data['formula']))
					else:
						formula=None
					
					percent=data['percent']
					value=data['value']
					credit_nature=data['credit_nature']
					applicable_on=data['applicable_on']
					tax_status=data['tax_status']
					all_type = data['all_type']

					credit_date=datetime.strptime((data['credit_date'].split('T'))[0], '%Y-%m-%d').date()

					deduction_name=AccountsDropdown.objects.get(sno=deduction_name)
					emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])


					qry=ConstantDeduction.objects.filter(DeductionName=deduction_name,session=AccountsSession.objects.get(id=session)).exclude(status="DELETE").values('DeductionName','session','Formula','deductionType','percent','maxvalue','creditnature','creditdate','added_by','id','taxstatus').order_by('-id')[:1]

					msg=""
					status=200

					if len(qry)>0:
						
						############# insert previous old values of constant deduction ########

						query=ConstantDeduction.objects.create(DeductionName=AccountsDropdown.objects.get(sno=qry[0]['DeductionName']),session=AccountsSession.objects.get(id=qry[0]['session']),deductionType=qry[0]['deductionType'],Formula=qry[0]['Formula'],percent=qry[0]['percent'],maxvalue=qry[0]['maxvalue'],creditnature=qry[0]['creditnature'],creditdate=qry[0]['creditdate'],added_by=EmployeePrimdetail.objects.get(emp_id=qry[0]['added_by']),taxstatus=qry[0]['taxstatus'],status="DELETE")

						qry_app_on = AccountsElementApplicableOn.objects.filter(constantDeduction=qry[0]['id']).values('salary_type')

						qry_s = ConstantDeduction.objects.filter(DeductionName=qry[0]['DeductionName']).values('id').order_by('-id')[:1]
						
						for a in qry_app_on:
							qry_element=AccountsElementApplicableOn.objects.create(constantDeduction=ConstantDeduction.objects.get(id=qry_s[0]['id']),salary_type=AccountsDropdown.objects.get(sno=a['salary_type']))

						############## update previous values #####################################

						query=ConstantDeduction.objects.filter(DeductionName=deduction_name,session=AccountsSession.objects.get(id=session)).exclude(status="DELETE").update(DeductionName=deduction_name,deductionType=deduction_type,Formula=formula,percent=percent,maxvalue=value,creditnature=credit_nature,creditdate=credit_date,added_by=emp_id,status="UPDATE",taxstatus=tax_status)
						
						qry_sel=ConstantDeduction.objects.filter(DeductionName=deduction_name,session=AccountsSession.objects.get(id=session)).order_by("-id").exclude(status="DELETE").values("id")
						
						qry_app=AccountsElementApplicableOn.objects.filter(constantDeduction=ConstantDeduction.objects.get(id=qry_sel[0]['id'])).values('salary_type','id')

						q=AccountsElementApplicableOn.objects.filter(constantDeduction=ConstantDeduction.objects.get(id=qry_sel[0]['id'])).delete()
						
						for a in applicable_on:
							qry_element=AccountsElementApplicableOn.objects.create(constantDeduction=ConstantDeduction.objects.get(id=qry_sel[0]['id']),salary_type=AccountsDropdown.objects.get(sno=a))
						
						msg="Data Added Updated"

					else:   
						query=ConstantDeduction.objects.create(DeductionName=deduction_name,session=AccountsSession.objects.get(id=session),deductionType=deduction_type,Formula=formula,percent=percent,maxvalue=value,creditnature=credit_nature,creditdate=credit_date,added_by=emp_id)

						query1=ConstantDeduction.objects.filter(DeductionName=deduction_name,session=AccountsSession.objects.get(id=session)).order_by("-id").exclude(status="DELETE").values("id") 
						for a in applicable_on:
							query3=AccountsDropdown.objects.get(sno=a)
							sno=ConstantDeduction.objects.get(id=query1[0]["id"])
							query2=AccountsElementApplicableOn.objects.create(constantDeduction=sno,salary_type=query3)
						
						msg="Data Added Succesfully"

					qry_id=ConstantDeduction.objects.filter(DeductionName=deduction_name,session=AccountsSession.objects.get(id=session)).exclude(status="DELETE").values('id').order_by('-id')[:1]

					if all_type == 'A':
						qry_del = EmployeeDeductions.objects.filter(constantDeduction__DeductionName=deduction_name,session=AccountsSession.objects.get(id=session)).update(status="DELETE")

						qry_emps = list(EmployeePrimdetail.objects.filter(emp_status='ACTIVE').exclude(emp_type=219).values_list('emp_id',flat=True))

						objs = (EmployeeDeductions(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp),session=AccountsSession.objects.get(id=session),constantDeduction=ConstantDeduction.objects.get(id=qry_id[0]['id']),added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])) for emp in qry_emps)
						qry_ins = EmployeeDeductions.objects.bulk_create(objs)
					
					elif all_type == 'R':
						qry_del = EmployeeDeductions.objects.filter(constantDeduction__DeductionName=deduction_name,session=AccountsSession.objects.get(id=session)).update(status="DELETE")

				elif(request.method=="GET"):
					deduction_name=request.GET["deduction_name"]
					deduction_name=AccountsDropdown.objects.get(sno=deduction_name)
					query=ConstantDeduction.objects.filter(DeductionName=deduction_name,session=AccountsSession.objects.get(id=session)).exclude(status='DELETE').values()
					if len(query) >0:
						if query[0]['Formula'] is not None:
							query[0]['Formula']=query[0]['Formula'].split(',')
						applicable_on=AccountsElementApplicableOn.objects.filter(constantDeduction=query[0]['id']).values_list('salary_type',flat=True)
						query[0]['salary_type']=list(applicable_on)
						query[0]['tax_status']=str(query[0]['taxstatus'])

					status=200
					data_values={"data":list(query)}

				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
		
	return JsonResponse(data=data_values,status=status)


def Employee_deduction(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				session=getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if (request.method == 'GET'):
					if(request.GET["request_type"]=='deductions'):
						month_date=request.GET['month']
						if '010' in month_date:
							month_date=month_date.replace('010','10')
						date=datetime.strptime(str(month_date).split('T')[0], '%Y-%m-%d').date()
						query1=EmployeeDeductions.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.GET["emp_id"]),constantDeduction=None,session=AccountsSession.objects.get(id=session)).exclude(status='DELETE').values("id","variableDeduction__value")
						n=len(query1)
						for a in range(n):
							id=query1[a]["id"]
							query=EmployeeVariableDeduction.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.GET["emp_id"]),deduction_id=id,month=date.month,session=AccountsSession.objects.get(id=session)).values("value").order_by('-id')[:1]
							if len(query) > 0:
								query1[a]["previous_value"]=query[0]["value"]
						status=200
						data_values={"data":list(query1)}
						
				elif(request.method=="POST"):
					data=json.loads(request.body)
					month_date=data['month']
					if '010' in month_date:
						month_date=month_date.replace('010','10')
					month=datetime.strptime((month_date.split('T'))[0], '%Y-%m-%d').date().month
					value=data["value"]
					Emp_id=data["emp_id"]

					added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
					emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_id)
					for a in value:
						deduction_id=EmployeeDeductions.objects.get(id=a["id"])
						value1=a["value"]
						query=EmployeeVariableDeduction.objects.update_or_create(month=month,deduction_id=deduction_id,Emp_Id=emp_id,session=AccountsSession.objects.get(id=session),defaults={"value":value1,"added_by":added_by})
					status=200
					data_values={"msg":"Data Successfully Added"}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values)


def insert_da_arrear(request):
	data_values={}
	msg=""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				if request.method == 'GET':
					if request.GET['request_type'] == 'form_data':
						session=getCurrentSession(None)
						if session == -1:
							return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

						
						qry_sal_ing_new=SalaryIngredient.objects.filter(Ingredients__value='DA',session=AccountsSession.objects.get(id=session)).exclude(status="DELETE").values('Formula','percent').order_by('-id')[:1]

						qry_sal_ing_prev=SalaryIngredient.objects.filter(Ingredients__value='DA',session=AccountsSession.objects.get(id=session)).values('Formula','percent').order_by('-id')[:1]
						data_values={'prev_percent':qry_sal_ing_prev[0]['percent'],'new_percent':qry_sal_ing_new[0]['percent']}
						status=200
					elif request.GET['request_type'] == 'show_previous':
						month_date = request.GET['month_date']
						month = datetime.strptime(month_date, '%Y-%m-%d').date().month

						q_da = DAArrear.objects.filter(credit_month=month).exclude(status='DELETE').extra(select={'time_stamp':"DATE_FORMAT(time_stamp,'%%d-%%m-%%Y %%H:%%i:%%s')",'credit_date':"DATE_FORMAT(credit_date,'%%d-%%m-%%Y %%H:%%i:%%s')",'Tdate':"DATE_FORMAT(Tdate,'%%d-%%m-%%Y')",'Fdate':"DATE_FORMAT(Fdate,'%%d-%%m-%%Y')"}).exclude(status='DELETE').values('emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','arrearCredited','time_stamp','credit_date','id','Fdate','Tdate','emp_id__dept','emp_id__organization')

						data_values={'data':list(q_da)}
						status=200
					else:
						status=502

				elif request.method == 'POST':
					data=json.loads(request.body)

					q_del = DAArrear.objects.filter(id=data['update_id']).update(status='DELETE')

					fdate=datetime.strptime(str(data['fdate']),"%Y-%m-%d").date()
					tdate=datetime.strptime(str(data['tdate']),"%Y-%m-%d").date()

					fromDate=fdate
					toDate=tdate
					actual_days=calendar.monthrange(fromDate.year, fromDate.month)[1]
					
					emps=list(data['emp_id'])
					
					if emps[0] == 'ALL':
						emps = EmployeePrimdetail.objects.filter(emp_status="ACTIVE").exclude(emp_type=219).values_list('emp_id',flat=True)

					session=getCurrentSession(None)
					if session == -1:
						return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

					month=getSalaryMonth(session)
					
					qry_check = DAArrear.objects.filter(emp_id__in=emps).filter((Q(Fdate__range=[fromDate,toDate]) | Q(Tdate__range=[fromDate,toDate])) | (Q(Fdate__lte=fromDate) & Q(Tdate__gte=toDate))).exclude(status='DELETE').values('id')
					if len(qry_check)>0:
						q_ins = DAArrear.objects.filter(id=data['update_id']).update(status='INSERT')
						status=202
						msg="DA Arrear has already been applied for the date range selected"
					else:
						emp_data=[]
						for emp_id in emps:
							working_days=0
							try:
								da=calculate_working_days(emp_id,fromDate,toDate,"N/A","N/A")
								working_days=da['payable_days']
							except:
								working_days=0
							q_sign_arrear = Sign_In_Out_Arrear.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date__range=[fromDate,toDate]).values('count')
							for q in q_sign_arrear:
								working_days+=q['count']
							
							q_leave_arrear = Days_Arrear_Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),fromdate__range=[fromDate,toDate]).values('working_days','fromdate','todate','fhalf','thalf')
							for q in q_leave_arrear:
								if q['fromdate'] > fromDate and q['todate'] < toDate:
									working_days+=q['working_days']
								elif q['fromdate'] < fromDate and q['todate'] < toDate:
									working_days+=fun_num_of_leaves(fromDate,q['todate'],0,q['thalf'])
								elif q['todate'] > toDate and q['fromdate'] > fromdate:
									working_days+=fun_num_of_leaves(q['fromdate'],toDate,q['thalf'],0)
								elif q['todate'] > toDate and q['fromdate'] < fromDate:
									working_days+=fun_num_of_leaves(fromDate,toDate,0,0)
								elif (q['fromdate'] == fromDate and q['todate'] < toDate) or (q['todate'] == toDate and q['fromdate'] > fromDate):
									working_days+=fun_num_of_leaves(fromDate,q['todate'],q['fhalf'],q['thalf'])
								elif (q['fromdate'] == fromDate and q['todate'] > toDate):
									working_days+=fun_num_of_leaves(fromDate,toDate,q['fhalf'],0)
								elif (q['todate'] == toDate and q['fromdate'] < fromDate):
									working_days+=fun_num_of_leaves(fromDate,toDate,0,q['thalf'])
								elif (q['fromdate']==fromDate and q['todate'] == toDate): 
									working_days+=fun_num_of_leaves(q['fromdate'],q['todate'],q['fhalf'],q['thalf'])

							emp_data.append({'emp_id':emp_id,'working_days':working_days})



						objs = (DAArrear(emp_id=EmployeePrimdetail.objects.get(emp_id=e['emp_id']),Fdate=fdate,Tdate=tdate,added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),session=AccountsSession.objects.get(id=session),credit_month=month,working_days=e['working_days'],actual_days=actual_days) for e in emp_data)
						q_ins = DAArrear.objects.bulk_create(objs)
					
						msg="Success"
						status=200
					data_values={'msg':msg}
				elif request.method=='DELETE':
					data=json.loads(request.body)
					q_del = DAArrear.objects.filter(id=data['id']).update(status='DELETE')

					status=200
					data_values={'msg':"DA Arrear Succesfully Deleted"}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status)      


def insert_sign_in_out_arrear(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[211])
			if check==200:
				if request.method == 'GET':
					emp_id=request.GET['emp_id']
					date=datetime.strptime(str(request.GET['date']),"%Y-%m-%d").date()

					qry_check = Attendance2.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date).values('status')
					if len(qry_check)>0:
						emp_status=qry_check[0]['status']
					else:
						emp_status=""
					msg="Success"
					status=200
					data_values={'msg':msg,'status':emp_status}
				elif request.method == 'POST':

					status = 200
					msg = "Success"
					data=json.loads(request.body)
					emp_id=data['emp_id']
					selected = int(data['status'])
					remark=data['remark']
					date=datetime.strptime(str(data['date']),"%Y-%m-%d").date()

					qry_check = Attendance2.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date).values('status')
					if len(qry_check)>0:
						emp_status=qry_check[0]['status']
					else:
						emp_status=""
					
					qry_check_leave = Leaves.objects.filter(fromdate__lte=date,todate__gte=date,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)).filter(finalstatus__contains="APPROVED").values('fhalf','thalf','fromdate','todate')
					if len(qry_check_leave) > 0 :
						for c in qry_check_leave:
							fhalf=c['fhalf']
							thalf=c['thalf']

							if c['fromdate'] == date or c['todate'] == date:
								if status  == 'P/A' or status == 'A':
									if (selected == 1 and fhalf == 1) or (selected == 2 and fhalf == 2) or fhalf == 0 :
										status=202
										msg="Leave already applied on the date selected"
								elif status == 'P/I':
									if (selected == 2 and fhalf == 2) or fhalf == 0:
										status=202
										msg="Leave already applied on the date selected"
								elif status == 'P/II':
									if (selected == 1 and fhalf == 1) or fhalf == 0:
										status=202
										msg="Leave already applied on the date selected"

							else:
								status=202
								msg="Leave already applied on the date selected"
					elif (selected==0 and (emp_status != 'P/A' and emp_status != 'A')) or (selected==1 and (emp_status=='P/I' or emp_status=='P')) or (selected==2 and (emp_status == 'P/II' or emp_status == 'P')):
						status=202
						msg="Attendance already applied for the date selected"

					
					qry_check_leave_arrear = Days_Arrear_Leaves.objects.filter(fromdate__lte=date,todate__gte=date,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id)).filter(hr_status__contains="APPROVED").values('fhalf','thalf','fromdate','todate')
					for ch in qry_check_leave_arrear:
						fhalf=ch['fhalf']
						thalf=ch['thalf']

						if (c['fromdate'] == date or c['todate'] == date):
							if (selected == fhalf or selected==thalf or fhalf==0 or thalf==0 or selected==0):
								status=202
								msg="Leave arrear already applied for the date selected"
						else:
							status=202
							msg="Leave arrear already applied for the date selected"

					qry_check_sign = Sign_In_Out_Arrear.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date).values('status')
					if len(qry_check_sign) >0:
						for q in qry_check_sign:
							if int(q['status']) == 0 or (selected==int(q['status']) or selected==0):
								status=202
								msg="Sign In/Out Arrear has already been applied for the date selected"

					if status == 200:
						if int(selected) == 0:
							count=1
						else:
							count=0.5
						actual_days=calendar.monthrange(date.year, date.month)[1]
						session=getCurrentSession(None)
						if session == -1:
							return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

						credit_month=getSalaryMonth(session)
						
						qry_ins = Sign_In_Out_Arrear.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date,count=count,session=AccountsSession.objects.get(id=session),status=selected,added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),actual_days=actual_days,credit_month=credit_month,hr_remark=remark)
					data_values={'msg':msg}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status)


def view_previous_arrear(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404,211,337])
			if check==200:
				if request.method == 'GET':
					data=[]
					filter_data={}
					filter_data2={}
					if request.GET['request_type'] == "employee":
						filter_data['emp_id']=request.session['hash1']
						filter_data2['Emp_Id']=request.session['hash1']
						
					first_date=datetime.strptime(str(request.GET['month']),"%Y-%m-%d").date()
					range1=calendar.monthrange(first_date.year,first_date.month)
					last_date=date(first_date.year,first_date.month ,range1[1])
					
					q_sess = AccountsSession.objects.filter(Fdate__lte=first_date,Tdate__gte=last_date).values('id')
					qry_data=Sign_In_Out_Arrear.objects.filter(**filter_data).filter(credit_month=first_date.month).extra(select={'time_stamp':"DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')","count":"count"}).values('emp_id','emp_id__name','emp_id__dept__value','count','credited','time_stamp','hr_remark','credit_date')
					n=len(qry_data)
					for i in range(n):
						qry_data[i]['type']="Sign In/Out Arrear"

					data.extend(list(qry_data))
					
					qry_data=Days_Arrear_Leaves.objects.filter(month=first_date.month).filter(**filter_data).extra(select={'time_stamp':"DATE_FORMAT(finalapprovaldate,'%%d-%%m-%%Y')","credited":"arrearCredited","count":"working_days"}).values('emp_id','emp_id__name','emp_id__dept__value','count','credited','time_stamp','hr_remark','credit_date')
					
					n=len(qry_data)
					for i in range(n):
						qry_data[i]['type']="Leave Arrear"
					data.extend(list(qry_data))
					
					if request.GET['request_type'] == 'accounts' or request.GET['request_type'] == "employee":
						q_inc = AccountsIncrementArrear.objects.filter(credit_month=first_date.month).exclude(status='DELETE').filter(**filter_data).extra(select={'count':'working_days','credited':'arrearCredited','hr_remark':'remark'}).values('emp_id','emp_id__name','emp_id__dept__value','count','credited','time_stamp','hr_remark','credit_date')

						n=len(q_inc)
						for i in range(n):
							q_inc[i]['type']="Increment Arrear"
						data.extend(q_inc)

						q_da = DAArrear.objects.filter(credit_month=first_date.month).filter(**filter_data).extra(select={'count':'working_days','credited':'arrearCredited','hr_remark':'remark'}).exclude(status='DELETE').values('emp_id','emp_id__name','emp_id__dept__value','count','credited','time_stamp','credit_date')

						n=len(q_da)
						for i in range(n):
							q_da[i]['type']="DA Arrear"
							q_da[i]['hr_remark']=""
						data.extend(q_da)

						q_add = AdditionalArrear.objects.filter(month=first_date.month,session=q_sess[0]['id']).filter(**filter_data).exclude(status='DELETE').extra(select={'count':'working_days','credited':'arrearCredited','hr_remark':'remark','count':'arrear_value'}).values('emp_id','emp_id__name','emp_id__dept__value','credited','time_stamp','hr_remark','credit_date','count')
						n=len(q_add)
						for i in range(n):
							q_add[i]['type']="Additional Arrear"
						data.extend(q_add)

					msg="Success"
					status=200
					data_values={'msg':msg,'data':list(data)}
					
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status)    

def view_previous_sign_in_arrear(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404,211])
			if check==200:
				if request.method == 'GET':
					qry_data=Sign_In_Out_Arrear.objects.extra(select={'time_stamp':"DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('emp_id','emp_id__name','date','count','emp_id__desg__value','emp_id__dept__value','credited','status','time_stamp')
					n=len(qry_data)
					for i in range(n):
						if qry_data[i]['status'] == 0 :
							qry_data[i]['status'] = "FULL DAY"
						elif qry_data[i]['status'] == 1 :
							qry_data[i]['status'] = "FIRST HALF"
						elif qry_data[i]['status'] == 2 :
							qry_data[i]['status'] = "SECOND HALF"
						date_2 = qry_data[i]['date']
						emp_id=qry_data[i]['emp_id']
						old_status = ""
						q_att = Attendance2.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date_2).values('status')
						if len(q_att)>0:
							old_status=q_att[0]['status']
						q_leave = Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),fromdate__lte=date_2,todate__gte=date_2,finalstatus__contains="APPROVED").values('leavecode__leave_name')
						for l in q_leave:
							old_status=old_status+" ("+l['leavecode__leave_name']+")"
						qry_data[i]['old_status'] = old_status
					msg="Success"
					status=200
					data_values={'msg':msg,'data':list(qry_data)}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status)      


def insert_increment_arrear(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				session=getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				month=getSalaryMonth(session)

				if request.method == 'GET':
					if request.GET['request_type'] == 'show_previous':  
						month_date = request.GET['month_date']
						month = datetime.strptime(month_date, '%Y-%m-%d').date().month

						q_inc = AccountsIncrementArrear.objects.filter(credit_month=month).extra(select={'time_stamp':"DATE_FORMAT(time_stamp,'%%d-%%m-%%Y %%H:%%i:%%s')",'credit_date':"DATE_FORMAT(credit_date,'%%d-%%m-%%Y %%H:%%i:%%s')",'Tdate':"DATE_FORMAT(Tdate,'%%d-%%m-%%Y')",'Fdate':"DATE_FORMAT(Fdate,'%%d-%%m-%%Y')"}).exclude(status='DELETE').values('emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','working_days','arrearCredited','time_stamp','remark','credit_date','id','Fdate','Tdate','emp_id__dept','emp_id__organization')

						for inc in q_inc:
							payable_inc_arrear=calculate_increment_days_arrear(inc['emp_id'],session,month,calculate_increment_days(inc['emp_id'],session,month))

							old_salary=0
							new_salary=0
							increment=0

							for (n,o,d) in zip(payable_inc_arrear['new_payable'],payable_inc_arrear['old_payable'],payable_inc_arrear['diff_payable']):
								old_salary+=o['gross_value']
								new_salary+=n['gross_value']
								increment+=d['diff_value']
							inc['old_salary']=old_salary
							inc['new_salary']=new_salary
							inc['increment']=increment
						data_values={'data':list(q_inc)}
						status=200

					elif request.GET['request_type'] == 'form_data':
						fromDate=datetime.strptime(str(request.GET['fromDate']),"%Y-%m-%d").date()
						toDate=datetime.strptime(str(request.GET['toDate']),"%Y-%m-%d").date()
						emp_id=request.GET['emp_id']
						actual_days=calendar.monthrange(fromDate.year, fromDate.month)[1]

						da=calculate_working_days(emp_id,fromDate,toDate,"N/A","N/A")
						working_days=da['payable_days']

						q_sign_arrear = Sign_In_Out_Arrear.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date__range=[fromDate,toDate]).values('count')
						for q in q_sign_arrear:
							working_days+=q['count']
						
						q_leave_arrear = Days_Arrear_Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),fromdate__range=[fromDate,toDate]).values('working_days','fromdate','todate','fhalf','thalf')
						for q in q_leave_arrear:
							if q['fromdate'] > fromDate and q['todate'] < toDate:
								working_days+=q['working_days']
							elif q['fromdate'] < fromDate and q['todate'] < toDate:
								working_days+=fun_num_of_leaves(fromDate,q['todate'],0,q['thalf'])
							elif q['todate'] > toDate and q['fromdate'] > fromdate:
								working_days+=fun_num_of_leaves(q['fromdate'],toDate,q['thalf'],0)
							elif q['todate'] > toDate and q['fromdate'] < fromDate:
								working_days+=fun_num_of_leaves(fromDate,toDate,0,0)
							elif (q['fromdate'] == fromDate and q['todate'] < toDate) or (q['todate'] == toDate and q['fromdate'] > fromDate):
								working_days+=fun_num_of_leaves(fromDate,q['todate'],q['fhalf'],q['thalf'])
							elif (q['fromdate'] == fromDate and q['todate'] > toDate):
								working_days+=fun_num_of_leaves(fromDate,toDate,q['fhalf'],0)
							elif (q['todate'] == toDate and q['fromdate'] < fromDate):
								working_days+=fun_num_of_leaves(fromDate,toDate,0,q['thalf'])
							elif (q['fromdate']==fromDate and q['todate'] == toDate): 
								working_days+=fun_num_of_leaves(q['fromdate'],q['todate'],q['fhalf'],q['thalf'])

						working_days_li=[{'working_days':working_days,'days':actual_days,'credit_month':fromDate.month,'month':fromDate.month,'session':getCurrentSession(fromDate)}]
									
						dat=calculate_increment_days_arrear(emp_id,session,month,working_days_li)
						data_values={'data':dat,'working_days':working_days}
						status=200
					else:
						status=502
				elif request.method == 'POST':
					data=json.loads(request.body)

					q_update = AccountsIncrementArrear.objects.filter(id=data['update_id']).update(status='DELETE')

					fromDate=datetime.strptime(str(data['fromDate']),"%Y-%m-%d").date()
					toDate=datetime.strptime(str(data['toDate']),"%Y-%m-%d").date()
					emp_id=data['emp_id']
					remark=data['remark']
					session=getCurrentSession(None)
					if session == -1:
						return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

					month=getSalaryMonth(session)

					credit_month=month
					
					days=calendar.monthrange(fromDate.year, fromDate.month)[1]
					da=calculate_working_days(emp_id,fromDate,toDate,"N/A","N/A")
					working_days=da['payable_days']

					q_sign_arrear = Sign_In_Out_Arrear.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date__range=[fromDate,toDate]).values('count')
					for q in q_sign_arrear:
						working_days+=q['count']
					
					q_leave_arrear = Days_Arrear_Leaves.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),fromdate__range=[fromDate,toDate]).values('working_days','fromdate','todate','fhalf','thalf')
					for q in q_leave_arrear:
						if q['fromdate'] > fromDate and q['todate'] < toDate:
							working_days+=q['working_days']
						elif q['fromdate'] < fromDate and q['todate'] < toDate:
							working_days+=fun_num_of_leaves(fromDate,q['todate'],0,q['thalf'])
						elif q['todate'] > toDate and q['fromdate'] > fromdate:
							working_days+=fun_num_of_leaves(q['fromdate'],toDate,q['thalf'],0)
						elif q['todate'] > toDate and q['fromdate'] < fromDate:
							working_days+=fun_num_of_leaves(fromDate,toDate,0,0)
						elif (q['fromdate'] == fromDate and q['todate'] < toDate) or (q['todate'] == toDate and q['fromdate'] > fromDate):
							working_days+=fun_num_of_leaves(fromDate,q['todate'],q['fhalf'],q['thalf'])
						elif (q['fromdate'] == fromDate and q['todate'] > toDate):
							working_days+=fun_num_of_leaves(fromDate,toDate,q['fhalf'],0)
						elif (q['todate'] == toDate and q['fromdate'] < fromDate):
							working_days+=fun_num_of_leaves(fromDate,toDate,0,q['thalf'])
						elif (q['fromdate']==fromDate and q['todate'] == toDate): 
							working_days+=fun_num_of_leaves(q['fromdate'],q['todate'],q['fhalf'],q['thalf'])
						
					qry_check = AccountsIncrementArrear.objects.filter((Q(Fdate__range=[fromDate,toDate]) | Q(Tdate__range=[fromDate,toDate])) | (Q(Fdate__lte=fromDate) & Q(Tdate__gte=toDate))).exclude(status='DELETE').filter(emp_id=emp_id).values()
					if len(qry_check)>0:
						q_update = AccountsIncrementArrear.objects.filter(id=data['update_id']).update(status='INSERT')
						status=202
						msg="Increment Arrear has already been applied for the selected date"
						data_values={'msg':msg}
					else:
						qry_ins=AccountsIncrementArrear.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),Fdate=fromDate,Tdate=toDate,credit_month=credit_month,session=AccountsSession.objects.get(id=session),added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),days=days,working_days=working_days,remark=remark)

						data_values={'msg':'Success'}
						status=200
				elif request.method == 'DELETE':
					data=json.loads(request.body)
					id=data['id']

					q_del = AccountsIncrementArrear.objects.filter(id=id).update(status='DELETE')
					data_values={'msg':'Increment Arrear Succesfully Deleted'}
					status=200

				else:
					status = 502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=status)


def insert_additional_arrear(request):
	data_values={}
	status=401
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				session=getCurrentSession(None)
				if session == -1:
					return JsonResponse(data={'msg':'Accounts Session not found'},status=202)

				if request.method == 'GET':
					if request.GET['request_type'] == 'show_previous':
						month_date = request.GET['month_date']
						month = datetime.strptime(month_date, '%Y-%m-%d').date().month

						q_prev_arrear = AdditionalArrear.objects.filter(month=month,session=AccountsSession.objects.get(id=session)).exclude(status='DELETE').extra(select={'time_stamp':"DATE_FORMAT(time_stamp,'%%d-%%m-%%Y %%H:%%i:%%s')",'credit_date':"DATE_FORMAT(credit_date,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','arrear_value','remark','arrearCredited','credit_date','time_stamp','id')

						data_values = {'data':list(q_prev_arrear)}
						status=200
					else:
						status=502

				elif request.method == 'POST':  
					data=json.loads(request.body)
					
					value=data['amount']
					emp_id=data['emp_id']
					remark=data['reason']
					month=getSalaryMonth(session)

					qry_ins = AdditionalArrear.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),arrear_value=value,remark=remark,month=month,session=AccountsSession.objects.get(id=session),added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
					data_values={'msg':'Arrear Succesfully Inserted'}
					status=200

				elif request.method == 'PUT':
					data=json.loads(request.body)
					
					value=data['amount']
					emp_id=data['emp_id']
					remark=data['reason']
					month=getSalaryMonth(session)
					id=data['id']

					q_delete = AdditionalArrear.objects.filter(id=id).update(status='DELETE')

					qry_ins = AdditionalArrear.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),arrear_value=value,remark=remark,month=month,session=AccountsSession.objects.get(id=session),added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))

					data_values={'msg':'Arrear Succesfully Updated'}
					status=200
					
				elif request.method=='DELETE':
					
					data=json.loads(request.body)
					
					id=data['id']

					q_delete = AdditionalArrear.objects.filter(id=id).update(status='DELETE')

					data_values={'msg':'Arrear Succesfully Deleted'}
					status=200


				else:
					status = 502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values)




def getCurrentSession(sdate):
	if sdate is None:
		today=date.today()
	else:
		today=sdate
	qry_session=AccountsSession.objects.filter(Fdate__lte=today,Tdate__gte=today).values('id').order_by('-id')[:1]
	if len(qry_session)==0:
		return -1
	return qry_session[0]['id']


def getSalaryMonth(session):
	qry_acc = AccountsSession.objects.filter(id=session).values('current_sal_month')
	
	return qry_acc[0]['current_sal_month']


############################################## SALARY CALCULATION ############################################################


def gross_payable_salary_components(emp_id,working_days,actual_days,session,taxstatus_li,salary_month):
	data=[]
	
	################ GET SALARY TYPE OF EMPLOYEE i.e. GRADE OF CONSOLIDATE #################
	qry=EmployeeGross_detail.objects.filter(Emp_Id=emp_id).filter(session=session).exclude(Status="DELETE").values('salary_type')
	if len(qry)>0:
		salary_type=qry[0]['salary_type']

		############################ GET SALARY INGREDIENTS OF EMPLOYEE BASED ON SALARY TYPE AND ALSO THEIR GROSS VALUE ###########
		sal_ing=get_salary_ingredient_details(emp_id,salary_type,taxstatus_li,session)
		
		for sal in sal_ing:
			################### if month of salary ingredient to be credited is not equal to the month for which salary is to generated, show gross value=0#######################
			
			#################### e.g. if some component is to be credited in the month of july then it's value will be zero for the rest of the months i.e. for april,may,june,august,sept etc. #############

			if sal['salary_ingredient__next_count_month'].month != salary_month:
				data.append({'gross_value':0,'payable_value':0,'Ing_Id':sal['salary_ingredient'],'value':sal['salary_ingredient__Ingredients__value'],'sal_dropdown_id':sal['salary_ingredient__Ingredients'],'tax_status':sal['salary_ingredient__taxstatus']})
			else:
				############### INGREDIENTS OF VALUE TYPE ######################

				if sal['salary_ingredient__calcType'] == 'V':
					try:
						payable_value = round((sal['prev_value']*working_days)/actual_days)
					except:
						payable_value=0
					data.append({'gross_value':sal['prev_value'],'payable_value':payable_value,'Ing_Id':sal['salary_ingredient'],'value':sal['salary_ingredient__Ingredients__value'],'sal_dropdown_id':sal['salary_ingredient__Ingredients'],'tax_status':sal['salary_ingredient__taxstatus']})

				############### INGREDIENTS OF FORMULA TYPE #####################
			
				elif sal['salary_ingredient__calcType'] == 'F':
					formula_list=sal['salary_ingredient__Formula']

					value=0
					for f in formula_list:
						qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=emp_id,Ing_Id__Ingredients=f).filter(session=session).exclude(Status="DELETE").values('Value')
						if len(qry_gross_value)>0:
							value+=qry_gross_value[0]['Value']
					
					value=round((sal['salary_ingredient__percent']*value)/100)
					
					try:
						payable_value = round((value*working_days)/actual_days)
					except:
						payable_value=0
					data.append({'gross_value':value,'payable_value':payable_value,'Ing_Id':sal['salary_ingredient'],'value':sal['salary_ingredient__Ingredients__value'],'sal_dropdown_id':sal['salary_ingredient__Ingredients'],'tax_status':sal['salary_ingredient__taxstatus']})

	return data


################### get stored value of salary components ###################
def stored_gross_payable_salary_components(emp_id,session,month):
	data=[]
	
	qry_det = MonthlyPayable_detail.objects.filter(Emp_Id=emp_id,Month=month,session=session).values('Ing_Id','gross_value','payable_value','Ing_Id__Ingredients__value','Ing_Id__Ingredients','Ing_Id__taxstatus').order_by('Ing_Id')

	for q in qry_det:
		data.append({'gross_value':q['gross_value'],'payable_value':q['payable_value'],'Ing_Id':q['Ing_Id'],'value':q['Ing_Id__Ingredients__value'],'sal_dropdown_id':q['Ing_Id__Ingredients'],'tax_status':q['Ing_Id__taxstatus']})

	return data





def calculate_days_arrear(emp_id,session,month):

	qry_days=Days_Arrear_Leaves.objects.filter(session=session,emp_id=emp_id,arrearCredited='N',hr_status__contains="APPROVED").extra(select={'actual_days':'days','id':'leaveid'}).values('working_days','actual_days','fromdate','id')
	working_days=0
	actual_days=0
	ids=[]
	for qry in qry_days:
		if qry['fromdate'].month == month:
			continue
		working_days+=qry['working_days']
		actual_days=qry['actual_days']
		ids.append(qry['id'])

	data={'working_days':working_days,'actual_days':actual_days,'ids':ids}
	return data

def calculate_sign_in_out_arrear(emp_id,session,month):
	
	qry_days=Sign_In_Out_Arrear.objects.filter(session=session,emp_id=emp_id,credited='N').values('count','actual_days','date','id')
	working_days=0
	actual_days=0
	ids=[]
	for qry in qry_days:
		if qry['date'].month == month:
			continue
	
		working_days+=qry['count']
		actual_days=qry['actual_days']
		ids.append(qry['id'])
		
	data={'working_days':working_days,'actual_days':actual_days,'ids':ids}
	return data


def calculate_increment_days(emp_id,session,credit_month):
	qry_inc_days=AccountsIncrementArrear.objects.filter(emp_id=emp_id,credit_month=credit_month,session=session).exclude(status='DELETE').values('working_days','days','credit_month','id','Fdate')
	for inc in qry_inc_days:
		inc['month']=inc['Fdate'].month
		inc['session']=getCurrentSession(inc['Fdate'])
		
	return list(qry_inc_days)

def calculate_increment_days_arrear(emp_id,session,month,working_days_li):
		
	taxstatus_li=[0,1]
	current_sal_month=getSalaryMonth(session)
	############### get gross value of salary components #############################
	if current_sal_month == month:
		new_salary=gross_payable_salary_components(emp_id,31,31,session,taxstatus_li,month)
	else:
		new_salary = list(MonthlyPayable_detail.objects.filter(Month=month,Emp_Id=emp_id,session=session).annotate(value=F('Ing_Id__Ingredients__value')).values('gross_value','value','Ing_Id'))

	old_salary=[]
	difference=[]
	old_gross_li=[]
	for n in new_salary:
		old_gross=n['gross_value']

		diff_value=0
		for w in working_days_li:
			q_old_det = MonthlyPayable_detail.objects.filter(Month=w['month'],Emp_Id=emp_id,session=w['session'],Ing_Id__Ingredients__value=n['value']).values('gross_value','Ing_Id__Ingredients__value')
			if len(q_old_det)>0:
				old_gross=q_old_det[0]['gross_value']
			

			try:
				diff_value+=((round((w['working_days']*n['gross_value'])/w['days']) - round((w['working_days']*old_gross)/w['days'])))
			except:
				diff_value=0
		
		old_salary.append({'gross_value':old_gross,'Ing_Id':n['Ing_Id'],'value':n['value']})
		difference.append({'diff_value':diff_value,'Ing_Id':n['Ing_Id'],'value':n['value']})

	data={'old_payable':old_salary,'new_payable':new_salary,'diff_payable':difference}
	return data


def calculate_additional_arrear(emp_id,session):
	qry_additional_arrear=AdditionalArrear.objects.filter(emp_id=emp_id,arrearCredited='N',session=session).exclude(status='DELETE').values('arrear_value','id')
	additional_arrear=0
	ids=[]
	for q in qry_additional_arrear:
		additional_arrear+=q['arrear_value']
		ids.append(q['id'])
	return {'value':additional_arrear,'ids':ids}

def calculate_da_days(emp_id,session):
	qry_da_arrear=DAArrear.objects.filter(emp_id=emp_id,session=session,arrearCredited='N').exclude(status='DELETE').values('working_days','actual_days','id')
	return list(qry_da_arrear)

def calculate_da_arrear(emp_id,session,da_arrear_data):
	data={}

	prev_value=0
	new_value=0
	prev_percent=0
	new_percent=0
	difference=0

	qry_sal_ing_new=SalaryIngredient.objects.filter(Ingredients__value='DA',session=session).exclude(status="DELETE").values('Formula','percent').order_by('-id')[:1]

	qry_sal_ing_prev=SalaryIngredient.objects.filter(Ingredients__value='DA',session=session).values('Formula','percent').order_by('-id')[:1]

	prev_formula = list(map(int,qry_sal_ing_prev[0]['Formula'].split(',')))
	new_formula = list(map(int,qry_sal_ing_new[0]['Formula'].split(',')))

	prev_percent=qry_sal_ing_prev[0]['percent']
	new_percent=qry_sal_ing_new[0]['percent']

	for p in prev_formula:
		qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=emp_id,Ing_Id__Ingredients=p).filter(session=session).exclude(Status="DELETE").values('Value')
		if len(qry_gross_value)>0:
			prev_value+=qry_gross_value[0]['Value']

	prev_value_gross=round((prev_value*prev_percent)/100)
	for n in new_formula:
		qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=emp_id,Ing_Id__Ingredients=n).filter(session=session).exclude(Status="DELETE").values('Value')
		if len(qry_gross_value)>0:
			new_value+=qry_gross_value[0]['Value']
	new_value_gross=round((new_value*new_percent)/100)

	
	for da in da_arrear_data:
		difference+=((new_value_gross*da['working_days'])/da['actual_days'])-((prev_value_gross*da['working_days'])/da['actual_days'])  

	difference=round(difference)
	if difference<0:
			difference=0
	data={'prev_value':prev_value,'new_value':new_value,'prev_percent':prev_percent,'new_percent':new_percent,'difference':difference}

	return data


################## calculate constant deduction of employee for the salary month ######################
def calculate_constant_deduction(emp_id,session,payable,taxstatus_li,salary_month):
	data=[]
	query=EmployeeDeductions.objects.filter(Emp_Id=emp_id,session=session,variableDeduction__isnull=True,constantDeduction__taxstatus__in=taxstatus_li).exclude(Q(constantDeduction__status='DELETE') | Q(status="DELETE")).values('constantDeduction__deductionType','constantDeduction__Formula','constantDeduction__percent','constantDeduction__maxvalue','constantDeduction','constantDeduction__DeductionName__value','constantDeduction__creditdate','constantDeduction__creditnature','id','constantDeduction__DeductionName')
	
	final_value = 0
	for a in query:
		if a['constantDeduction__creditdate'].month != salary_month:
			data.append({'id':a['constantDeduction'],'value':0,'name':a['constantDeduction__DeductionName__value'],'nature':a['constantDeduction__creditnature'],'ded_id':a['id'],'ded_dropdown_id':a['constantDeduction__DeductionName']})
		else:
			if a['constantDeduction__deductionType']=='F':
				formula=a['constantDeduction__Formula']
				formula1=list(map(int,formula.split(",")))
				total=0
				n=len(payable)
				
				for i in range(n):
					if payable[i]['sal_dropdown_id'] in formula1:
						total+=payable[i]['payable_value']
				total=round((total*a['constantDeduction__percent'])/100)
				total=min(total,a['constantDeduction__maxvalue'])
				
				final_value += total
				data.append({'id':a['constantDeduction'],'value':total,'name':a['constantDeduction__DeductionName__value'],'nature':a['constantDeduction__creditnature'],'ded_id':a['id'],'ded_dropdown_id':a['constantDeduction__DeductionName']})
			else:
				data.append({'id':a['constantDeduction'],'value':a['constantDeduction__maxvalue'],'name':a['constantDeduction__DeductionName__value'],'nature':a['constantDeduction__creditnature'],'ded_id':a['id'],'ded_dropdown_id':a['constantDeduction__DeductionName']})
				final_value += a['constantDeduction__maxvalue']
			
	return {'data':data,'final_value':final_value}

################# calculate stored value of constant deduction for the selected month ####################33
def calculate_constant_deduction_stored(emp_id,session,payable,taxstatus_li,salary_month):
	data=[]
	query=MonthlyDeductionValue.objects.filter(Emp_Id=emp_id,session=session,deduction_id__variableDeduction__isnull=True,deduction_id__constantDeduction__taxstatus__in=taxstatus_li,month=salary_month).values('deduction_id__constantDeduction__deductionType','deduction_id__constantDeduction__Formula','deduction_id__constantDeduction__percent','deduction_id__constantDeduction__maxvalue','deduction_id__constantDeduction','deduction_id__constantDeduction__DeductionName__value','deduction_id__constantDeduction__creditdate','deduction_id__constantDeduction__creditnature','value','deduction_id')
	
	final_value = 0
	for a in query:
		final_value+=a['value']
		data.append({'id':a['deduction_id__constantDeduction'],'value':a['value'],'name':a['deduction_id__constantDeduction__DeductionName__value'],'nature':a['deduction_id__constantDeduction__creditnature'],'ded_id':a['deduction_id']})
			
	return {'data':data,'final_value':final_value}

################# calculate stored value of variable deduction for the selected month ####################33

def calculate_variable_deduction_stored(emp_id,session,salary_month):
	data=[]
	query=MonthlyDeductionValue.objects.filter(Emp_Id=emp_id,session=session,deduction_id__constantDeduction__isnull=True,month=salary_month).values('value','deduction_id__variableDeduction','deduction_id__variableDeduction__value').distinct()
	
	final_value = 0
	for q in query:
		final_value+=q['value']
		data.append({'v_id':q['deduction_id__variableDeduction'],'v_name':q['deduction_id__variableDeduction__value'],'value':q['value']})
			
	return {'data':data,'total_value':final_value}

################## calculate variable deduction of employee for the salary month ######################

def calculate_variable_deduction(emp_id,session,month):
	data=[]
	sum_value=0
	query=EmployeeDeductions.objects.filter(Emp_Id=emp_id,session=session,constantDeduction__isnull=True).exclude(status='DELETE').values('variableDeduction','variableDeduction__value','id')
	for q in query:
		qry=EmployeeVariableDeduction.objects.filter(Emp_Id=emp_id,session=session,month=month,deduction_id=q['id']).values('value','deduction_id','deduction_id__variableDeduction__value')
		value=0
		if len(qry)>0:
			value=qry[0]['value']
			sum_value+=qry[0]['value']
		data.append({'v_id':q['variableDeduction'],'v_name':q['variableDeduction__value'],'value':value})

	return {'data':list(data),'total_value':sum_value}
	
################# calculate salary components yearly value on which income tax is to be calculated ##################
def calculate_income_tax_sum(emp_id,session,working_days,actual_days,gross_payable_data,salary_month,payable_da_arrear,payable_inc_arrear,payable_days_arrear,additional_arrear,payable_sign_arrear):
	
	income_sum_data=[]

	all_ingredients =  SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").annotate(tax_status=F('taxstatus'),Ing_Id=F('id'),value=F('Ingredients__value')).values('Ing_Id','value','tax_status')
	
	payable_ids= []
	for gross in gross_payable_data:
		payable_ids.append(gross['Ing_Id'])

	for alll in all_ingredients:
		if alll['Ing_Id'] not in payable_ids:
			alll['gross_value']=0
			alll['payable_value']=0
		else:
			alll['gross_value']=gross_payable_data[payable_ids.index(alll['Ing_Id'])]['gross_value']
			alll['payable_value']=gross_payable_data[payable_ids.index(alll['Ing_Id'])]['payable_value']

	gross_payable_data = all_ingredients
	n=len(gross_payable_data)

	for i in range(n):

		if gross_payable_data[i]['tax_status'] ==0:
			continue

		rem_month=12
		month = 4
		comp_month_break_up=[]
		inc_arrear_break_up = []
		leave_arrear_break_up =[]
		da_arrear_break_up =[]
		sign_in_out_arrear_break_up =[]
		additional_arrear_break_up =[]
		payable_comp=0
		inc_arr_comp=0
		da_arrear_comp=0
		leave_arrear_comp=0
		add_arrear_comp=0
		sign_arrear_comp=0

		##################### gross value of salary components as applicable for the selected month ######################
		comp_name = gross_payable_data[i]['value']


		############## salary component break up ####################


		################# get values of salary components already received by employee in that session ###########################
		qry_mon = MonthlyPayable_detail.objects.filter(Emp_Id=emp_id,Ing_Id=gross_payable_data[i]['Ing_Id'],session=session).exclude(Month=salary_month).values('payable_value','gross_value','Month').order_by('id')

		for qr in qry_mon:
			############# e.g. if employee joins institution in month of july in that session, then for april, may,june append 0 gross value and 0 payable value #####################
			while month != qr['Month']:
				comp_month_break_up.append({'month':calendar.month_name[month],'gross_value':0,'payable_value':0})
				month=max((month+1)%13,1)
				rem_month-=1

			############## append gross and calculated payable value for the retrieved month from query ###########################
			comp_month_break_up.append({'month':calendar.month_name[qr['Month']],'gross_value':qr['gross_value'],'payable_value':qr['payable_value']})
			payable_comp+=qr['payable_value']
			month=max((month+1)%13,1)
			rem_month-=1

		while month != salary_month:
			comp_month_break_up.append({'month':calendar.month_name[month],'gross_value':0,'payable_value':0})
			month=max((month+1)%13,1)
			rem_month-=1

		payable_comp+=gross_payable_data[i]['payable_value']
		############## append gross and calculated payable value for the salary month ###########################
		comp_month_break_up.append({'month':calendar.month_name[salary_month],'gross_value':gross_payable_data[i]['gross_value'],'payable_value':gross_payable_data[i]['payable_value']})
		month=max((month+1)%13,1)
		rem_month-=1

		############## append gross value for the rest months ###########################
		
		while rem_month>0:
			payable_comp+=gross_payable_data[i]['gross_value']
			comp_month_break_up.append({'month':calendar.month_name[month],'gross_value':gross_payable_data[i]['gross_value'],'payable_value':gross_payable_data[i]['gross_value']})
			month=max((month+1)%13,1)
			rem_month-=1
		
		############## leave arrear break up ####################
		month=4
		rem_month=12

		qry_mon = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,Ing_Id=gross_payable_data[i]['Ing_Id'],arrear_type="L",session=session).exclude(Month=salary_month).values('value','Month').order_by('id')

		for qr in qry_mon:
			while month != qr['Month']:
				leave_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
				month=max((month+1)%13,1)
				rem_month-=1

			leave_arrear_break_up.append({'month':calendar.month_name[qr['Month']],'value':qr['value']})
			leave_arrear_comp+=qr['value']
			month=max((month+1)%13,1)
			rem_month-=1

		while month != salary_month:
			leave_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
			month=max((month+1)%13,1)
			rem_month-=1
			
		try:
			if payable_days_arrear[i]['Ing_Id'] == gross_payable_data[i]['Ing_Id']:
				leave_arrear_comp+=payable_days_arrear[i]['payable_value']
				leave_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':payable_days_arrear[i]['payable_value']})
			else:
				leave_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':0}) 
		except:
			leave_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':0})
		
		month=max((month+1)%13,1)
		rem_month-=1

		while rem_month>0:
			leave_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
			month=max((month+1)%13,1)
			rem_month-=1

		############## increment arrear break up ####################
		month=4
		rem_month=12

		qry_mon = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,Ing_Id=gross_payable_data[i]['Ing_Id'],arrear_type="I",session=session).exclude(Month=salary_month).values('value','Month').order_by('id')

		for qr in qry_mon:
			while month != qr['Month']:
				inc_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
				month=max((month+1)%13,1)
				rem_month-=1

			inc_arrear_break_up.append({'month':calendar.month_name[qr['Month']],'value':qr['value']})
			inc_arr_comp+=qr['value']
			month=max((month+1)%13,1)
			rem_month-=1

		while month != salary_month:
			inc_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
			month=max((month+1)%13,1)
			rem_month-=1

		try:
			if payable_inc_arrear['diff_payable'][i]['Ing_Id'] == gross_payable_data[i]['Ing_Id']:
				inc_arr_comp+=payable_inc_arrear['diff_payable'][i]['diff_value']
				inc_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':payable_inc_arrear['diff_payable'][i]['diff_value']})
			else:
				inc_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':0})
		except:
			inc_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':0})

		month=max((month+1)%13,1)
		rem_month-=1

		while rem_month>0:
			inc_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
			month=max((month+1)%13,1)
			rem_month-=1

		############## sign in/out arrear break up ####################3
		month=4
		rem_month=12

		qry_mon = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,Ing_Id=gross_payable_data[i]['Ing_Id'],arrear_type="S",session=session).exclude(Month=salary_month).values('value','Month').order_by('id')

		for qr in qry_mon:
			while month != qr['Month']:
				sign_in_out_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
				month=max((month+1)%13,1)
				rem_month-=1

			sign_in_out_arrear_break_up.append({'month':calendar.month_name[qr['Month']],'value':qr['value']})
			sign_arrear_comp+=qr['value']
			month=max((month+1)%13,1)
			rem_month-=1

		while month != salary_month:
			sign_in_out_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
			month=max((month+1)%13,1)
			rem_month-=1

		try:
			if payable_sign_arrear[i]['Ing_Id'] == gross_payable_data[i]['Ing_Id']:
				sign_arrear_comp+=payable_sign_arrear[i]['payable_value']
				sign_in_out_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':payable_sign_arrear[i]['payable_value']})
			else:
				sign_in_out_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':0})
		except:
			sign_in_out_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':0})

		month=max((month+1)%13,1)
		rem_month-=1

		while rem_month>0:
			sign_in_out_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
			month=max((month+1)%13,1)
			rem_month-=1
		

		############## DA arrear break up ####################3
		if comp_name == "DA":
			month=4
			rem_month=12

			qry_mon = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,Ing_Id=gross_payable_data[i]['Ing_Id'],arrear_type="DA",session=session).exclude(Month=salary_month).values('value','Month').order_by('id')

			for qr in qry_mon:
				while month != qr['Month']:
					da_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
					month=max((month+1)%13,1)
					rem_month-=1

				da_arrear_break_up.append({'month':calendar.month_name[qr['Month']],'value':qr['value']})
				da_arrear_comp+=qr['value']
				month=max((month+1)%13,1)
				rem_month-=1

			while month != salary_month:
				da_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
				month=max((month+1)%13,1)
				rem_month-=1

			try:
				da_arrear_comp+=payable_da_arrear['difference']
				da_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':payable_da_arrear['difference']})
			except:
				da_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':0})

			month=max((month+1)%13,1)
			rem_month-=1

			while rem_month>0:
				da_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
				month=max((month+1)%13,1)
				rem_month-=1

		############## additional arrear break up ####################
		if comp_name == "OTHERS":
			month=4
			rem_month=12

			qry_mon = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,Ing_Id=gross_payable_data[i]['Ing_Id'],arrear_type="A",session=session).exclude(Month=salary_month).values('value','Month').order_by('id')

			for qr in qry_mon:
				while month != qr['Month']:
					additional_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
					month=max((month+1)%13,1)
					rem_month-=1

				additional_arrear_break_up.append({'month':calendar.month_name[qr['Month']],'value':qr['value']})
				add_arrear_comp+=qr['value']
				month=max((month+1)%13,1)
				rem_month-=1

			while month != salary_month:
				additional_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
				month=max((month+1)%13,1)
				rem_month-=1

			add_arrear_comp+=additional_arrear
			additional_arrear_break_up.append({'month':calendar.month_name[salary_month],'value':additional_arrear})
			
			month=max((month+1)%13,1)
			rem_month-=1

			while rem_month>0:
				additional_arrear_break_up.append({'month':calendar.month_name[month],'value':0})
				month=max((month+1)%13,1)
				rem_month-=1
			
		################## break up end #######################################

		payable_value_final = payable_comp + inc_arr_comp + leave_arrear_comp + da_arrear_comp + sign_arrear_comp + add_arrear_comp

		income_sum_data.append({'Ing_Id':gross_payable_data[i]['Ing_Id'],'Ing_value':comp_name,'comp_value':payable_comp,'comp_month_break_up':comp_month_break_up,'increment_arrear':{'break_up':inc_arrear_break_up,'total_value':inc_arr_comp},'leave_arrear':{'break_up':leave_arrear_break_up,'total_value':leave_arrear_comp},'sign_in_out_arrear':{'break_up':sign_in_out_arrear_break_up,'total_value':sign_arrear_comp},'da_arrear':{'break_up':da_arrear_break_up,'total_value':da_arrear_comp},'additional_arrear':{'break_up':additional_arrear_break_up,'total_value':add_arrear_comp},'value':payable_value_final})
	

	return income_sum_data


def hra_exemption_formula1(emp_id,session,working_days,actual_days,month):

	############ calculate HRA salary ingredient from starting of financial year i.e if current month is june then it would be payable hra value of april + payable hra value of may +payable hra value of june + (gross hra value)*9 ######### 

	gross_value=0
	payable_value=0
	
	qry=EmployeeGross_detail.objects.filter(Emp_Id=emp_id).filter(session=session).exclude(Status="DELETE").values('salary_type')

	if len(qry)>0:
		qry_emp_sal = AccountsElementApplicableOn.objects.filter(salary_type=qry[0]['salary_type'],constantDeduction=None,salary_ingredient__Ingredients__value__contains="HRA").exclude(salary_ingredient__status="DELETE").values('salary_ingredient__calcType','salary_ingredient__Formula','salary_ingredient__percent','salary_ingredient__ingredient_nature','salary_ingredient__next_count_month','salary_ingredient__taxstatus','salary_ingredient__id','salary_ingredient')

		n=len(qry_emp_sal)

		for i in range(n):
			qry_emp_sal[i]['salary_ingredient__next_count_month']=qry_emp_sal[i]['salary_ingredient__next_count_month'].month
			if qry_emp_sal[i]['salary_ingredient__calcType'] == 'V':

				qry_emp_sal2=EmployeeGross_detail.objects.filter(Emp_Id=emp_id).filter(session=session,Ing_Id=qry_emp_sal[0]['salary_ingredient']).exclude(Status="DELETE").values('Value')
				try:
					payable_value = round((qry_emp_sal2[i]['Value']*working_days)/actual_days)
				except:
					payable_value=0
				gross_value=qry_emp_sal2[i]['Value']
				
			############### INGREDIENTS OF FORMULA TYPE #####################

			elif qry_emp_sal[i]['salary_ingredient__calcType'] == 'F':
		
				formula_list=list(map(int,qry_emp_sal[i]['salary_ingredient__Formula'].split(',')))

				value=0
				for f in formula_list:
					qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=emp_id,Ing_Id__Ingredients=f).filter(session=session).exclude(Status="DELETE").values('Value')
					if len(qry_gross_value)>0:
						value+=qry_gross_value[0]['Value']
				
				value=round((qry_emp_sal[i]['salary_ingredient__percent']*value)/100)
				gross_value=value
				try:
					payable_value = round((value*working_days)/actual_days)
				except:
					payable_value=0
	
	value1=0
	qry_hra=MonthlyPayable_detail.objects.filter(Ing_Id__Ingredients__value__contains="HRA",Emp_Id=emp_id,session=session).exclude(Month=month).values('payable_value')
	for q in qry_hra:
		value1+=q['payable_value']

	qry_hra=MonthlyArrear_detail.objects.filter(Ing_Id__Ingredients__value__contains="HRA",Emp_Id=emp_id,session=session).exclude(Month=month).values('payable_value')
	for q in qry_hra:
		value1+=q['payable_value']
	
	if month<4:
		month+=12
	month3=12-(month-3)
	
	value1=value1+payable_value+(gross_value*month3)
	return value1



def hra_exemption_formula2(emp_id,session,income_tax_sum,formula1_value):
	############ calculate rent paid (house rent)-10% of (calculate_income_tax_sum-hra_exemption_formula1) #########    

	qry_rent_per_month=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__value="RENT PER MONTH").values('Value').exclude(status="DELETE").order_by('-id')[:1]
	qry_no_of_month=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__value="NUMBER OF MONTHS").values('Value').exclude(status="DELETE").order_by('-id')[:1]

	rent_paid=0
	value2=0
	if len(qry_rent_per_month)>0:
		rent_paid=qry_rent_per_month[0]['Value']
		
	if len(qry_no_of_month)>0:
		rent_paid*=qry_no_of_month[0]['Value']
	
	if rent_paid>0:
		value2=max(round(rent_paid-0.1*(income_tax_sum-formula1_value)),0)   

	return value2


def hra_exemption_formula3(emp_id,session,income_tax_sum,formula1_value):
	############ 40 or 50 % of (calculate_income_tax_sum-hra_exemption_formula1) based on metro or non-metro city residence #########   
	qry_residence_location=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__field="RESIDENCE LOCATION").values('Value','Dec_Id','Dec_Id__value').exclude(status="DELETE").order_by('-id')[:1]

	value3=0
	id=-1
	name="N/A"
	if len(qry_residence_location)>0:
		qry_per=AccountsDropdown.objects.filter(pid=qry_residence_location[0]['Dec_Id'],session=session).exclude(value__isnull=True).values('value')
		per=(float)(qry_per[0]['value'])
		value3=round((per*(income_tax_sum-formula1_value))/100)     ######## ?????? correct or not ##############

		id=qry_residence_location[0]['Dec_Id']
		name=qry_residence_location[0]['Dec_Id__value']

	return {'id':id,'name':name,'value':value3}



def calculate_loss_deductions(emp_id,session,payable,const_ded):
	session_id = session
	final_value=0
	taxstatus_li = [0]

	final_data={}

	loss_data=[]
	############ 80C Calculation #####################
	
	loss = declaration_components("loss_deductions", session_id)
	for l in loss:

		if l['value'] == '80D':

			value_loss=0
			value_s=0
			data=[]

			############# 80D ###########################################
			######### self mediclaim #####################
			
			age=calculate_emp_age(emp_id,session)
			
			qry_self_medi=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__value="SELF MEDICLAIM").values('Value','Dec_Id').exclude(status="DELETE").order_by('-id')[:1]
			
			if len(qry_self_medi)>0:
				qry_age=AccountsDropdown.objects.filter(field="SELF AGE",value="AGE LIMIT", session=session_id).values('sno')
				qry_age2=AccountsDropdown.objects.filter(pid=qry_age[0]['sno'],session=session).exclude(value__isnull=True).values('value')

				qry_value=AccountsDropdown.objects.filter(field="SELF AGE",value="MAX VALUE", session=session_id).values('sno')
				qry_value2=AccountsDropdown.objects.filter(pid=qry_value[0]['sno'],session=session).exclude(value__isnull=True).values('value')

				qry_upp = AccountsDropdown.objects.filter(field='SELF',value='UPPER LIMIT', session=session_id).values('sno')
				qry_up_limit = AccountsDropdown.objects.filter(field='UPPER LIMIT',pid=qry_upp[0]['sno'],session=session).exclude(value__isnull=True).values('value')
				
				if age > int(qry_age2[0]['value']):
					value_s=min(int(qry_value2[0]['value']),qry_self_medi[0]['Value'])
					value_loss+=value_s
				else:
					value_s=min(int(qry_up_limit[0]['value']),qry_self_medi[0]['Value'])
					value_loss+=value_s

				data.append({'sub_name':'SELF MEDICLAIM','sub_id':-1,'value':value_s})
			else:
				data.append({'sub_name':'SELF MEDICLAIM','sub_id':-1,'value':0})

			############ parent mediclaim Calculation #####################

			qry_parent_age=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__value="PARENT AGE").values('Value','Dec_Id').exclude(status="DELETE").order_by('-id')[:1]
			
			qry_parent_medi=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__value="PARENT MEDICLAIM").values('Value','Dec_Id').exclude(status="DELETE").order_by('-id')[:1]
			
			if len(qry_parent_age)>0:
				qry_age=AccountsDropdown.objects.filter(field="PARENT AGE",value="PARENT AGE LIMIT", session=session_id).values('sno')
				qry_age2=AccountsDropdown.objects.filter(pid=qry_age[0]['sno'],session=session).exclude(value__isnull=True).values('value')

				qry_value=AccountsDropdown.objects.filter(field="PARENT AGE",value="MAX VALUE", session=session_id).values('sno')
				qry_value2=AccountsDropdown.objects.filter(pid=qry_value[0]['sno'],session=session).exclude(value__isnull=True).values('value')

				qry_upp = AccountsDropdown.objects.filter(field='PARENT',value='UPPER LIMIT', session=session_id).values('sno')
				qry_up_limit = AccountsDropdown.objects.filter(field='UPPER LIMIT',pid=qry_upp[0]['sno'],session=session).exclude(value__isnull=True).values('value')
				
				if len(qry_parent_medi) >0:
					if qry_parent_age[0]['Value'] > int(qry_age2[0]['value']):
						value_s=min(int(qry_value2[0]['value']),qry_parent_medi[0]['Value'])
						value_loss+=value_s
					else:
						value_s=min(int(qry_up_limit[0]['value']),qry_parent_medi[0]['Value'])
						value_loss+=value_s
				else:
					value_s=0

				data.append({'sub_name':'PARENT MEDICLAIM','sub_id':-1,'value':value_s})
				data.append({'sub_name':'PARENT AGE','sub_id':-1,'value':qry_parent_age[0]['Value']})
			else:
				data.append({'sub_name':'PARENT MEDICLAIM','sub_id':-1,'value':0})
				data.append({'sub_name':'PARENT AGE','sub_id':-1,'value':0})

			flag_m=0
			################ mediclaim constant deduction #######################################
			
			med_data=calculate_mediclaim(emp_id,session,taxstatus_li,payable)
			value_loss+=med_data['value']
			data.append({'sub_name':"MEDICLAIM",'sub_id':-1,'value':med_data['value']})

			final_value+=value_loss
			loss_data.append({'data':data,'loss':'80D','final_value':value_loss})

		else:
			qry2=AccountsDropdown.objects.filter(field=l['value'],value="UPPER LIMIT", session=session_id).values('sno')
			qry3=AccountsDropdown.objects.filter(pid=qry2[0]['sno'],session=session).values('value')

			value_loss = 0
			data = []

			for sub in l['data']:
				qry_loss=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id=sub['sno']).values('Value','Dec_Id').exclude(status="DELETE").order_by('-id')
				if len(qry_loss)>0:
					value_loss+=qry_loss[0]['Value']
					data.append({'sub_name':sub['value'],'sub_id':sub['sno'],'value':qry_loss[0]['Value']})
				else:
					value_loss+=0
					data.append({'sub_name':sub['value'],'sub_id':sub['sno'],'value':0})
			
			###### 2 hardcode constant deductions ############

			if l['value'] == '80C': 
				epf_data=calculate_epf(emp_id,session,taxstatus_li,payable)
				value_loss+=epf_data['value']
				data.append({'sub_name':'EPF','sub_id':-1,'value':epf_data['value']})

			
			#####################################################

			value_loss = min(int(qry3[0]['value']),value_loss)

			final_value+=value_loss
			loss_data.append({'data':data,'loss':l['value'],'final_value':value_loss})

	return {'data':loss_data,'value':final_value}

def calculate_mediclaim(emp_id,session,taxstatus_li,payble):
	################ mediclaim constant deduction #######################################
	query=EmployeeDeductions.objects.filter(Emp_Id=emp_id,session=session,variableDeduction__isnull=True,constantDeduction__taxstatus__in=taxstatus_li,constantDeduction__DeductionName__value="MEDICLAIM").exclude(Q(constantDeduction__status='DELETE') | Q(status="DELETE")).values('constantDeduction__deductionType','constantDeduction__Formula','constantDeduction__percent','constantDeduction__maxvalue','constantDeduction__creditnature','id','constantDeduction__creditdate')
	
	final_value_m = 0
	data={}
	med_val_t=0
	mediclaim_break_up=[]
	mon3=-1
	
	month=getSalaryMonth(session)
		
	for a in query:
		if a['constantDeduction__creditdate'].month == month:
			if a['constantDeduction__deductionType']=='F':
				formula=a['constantDeduction__Formula']
				formula1=list(map(int,formula.split(",")))
				total=0
				total1=0
				n=len(payable)
				
				for i in range(n):
					if payable[i]['sal_dropdown_id'] in formula1:
						total+=payable[i]['payable_value']
						total1+=payable[i]['gross_value']
				total=round((total*a['constantDeduction__percent'])/100)
				total=min(total,a['constantDeduction__maxvalue'])
				
				total1=round((total1*a['constantDeduction__percent'])/100)
				total1=min(total1,a['constantDeduction__maxvalue'])
				
				med_val_t += total
				
				
			else:
				med_val_t += a['constantDeduction__maxvalue']
			
		mon2=4
		cnt=12

		q_find = MonthlyDeductionValue.objects.filter(deduction_id=a['id'],Emp_Id=emp_id,session=session).exclude(month=month).values('value','month')
		
		for qf in q_find:
			while mon2 != qf['month']:
				mediclaim_break_up.append({'month':calendar.month_name[mon2],'value':0})
				mon2=max((mon2+1)%13,1)
				cnt-=1
			mediclaim_break_up.append({'month':calendar.month_name[mon2],'value':qf['value']})
			final_value_m+=qf['value']
			mon2=max((mon2+1)%13,1)
			cnt-=1

		if med_val_t>0:
			mediclaim_break_up.append({'month':calendar.month_name[mon2],'value':med_val_t})
			final_value_m+=med_val_t
			mon2=max((mon2+1)%13,1)
			cnt-=1

		while cnt>0:
			mediclaim_break_up.append({'month':calendar.month_name[mon2],'value':0})
			mon2=max((mon2+1)%13,1)
			cnt-=1


	flag_m=1
	

	data={'sub_name':"MEDICLAIM",'sub_id':-1,'value':final_value_m,'break_up':mediclaim_break_up}

		
	if flag_m == 0:
		data={'sub_name':"MEDICLAIM",'sub_id':-1,'value':0,'break_up':mediclaim_break_up}

	return data


def calculate_epf(emp_id,session,taxstatus_li,payable):
	flag_e=0
	query=EmployeeDeductions.objects.filter(Emp_Id=emp_id,session=session,variableDeduction__isnull=True,constantDeduction__taxstatus__in=taxstatus_li,constantDeduction__DeductionName__value="EPF").exclude(Q(constantDeduction__status='DELETE') | Q(status="DELETE")).values('constantDeduction__deductionType','constantDeduction__Formula','constantDeduction__percent','constantDeduction__maxvalue','constantDeduction__creditnature','id')

	final_value_e = 0
	final_value_e1 = 0
	total=0
	payed_epf_break_up=[]
	total1=0
	for a in query:
		if a['constantDeduction__deductionType']=='F':
			formula=a['constantDeduction__Formula']
			formula1=list(map(int,formula.split(",")))
			total=0
			total1=0
			n=len(payable)
			
			for i in range(n):
				if payable[i]['sal_dropdown_id'] in formula1:
					total+=payable[i]['payable_value']
					total1+=payable[i]['gross_value']
			total=round((total*a['constantDeduction__percent'])/100)
			total=min(total,a['constantDeduction__maxvalue'])
			
			total1=round((total1*a['constantDeduction__percent'])/100)
			total1=min(total1,a['constantDeduction__maxvalue'])
			
			final_value_e += total
			final_value_e1 += total1
			
		else:
			final_value_e += a['constantDeduction__maxvalue']
			final_value_e1 += a['constantDeduction__maxvalue']

		nature = a['constantDeduction__creditnature']
		doj = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
		sess_date = AccountsSession.objects.filter(id=session).values('Fdate')

		epf_val = 0
		mon2=4
		cnt2=12
		#if doj[0]['doj'] < sess_date[0]['Fdate']:
		month=getSalaryMonth(session)
		q_find = MonthlyDeductionValue.objects.filter(deduction_id__constantDeduction__DeductionName__value='EPF',Emp_Id=emp_id,session=session).exclude(month=month).values('value','month')
		if len(q_find)>0:
			while mon2 != q_find[0]['month']:

				epf_val+=0
				payed_epf_break_up.append({'month':calendar.month_name[mon2],'value':0})
				mon2=max((mon2+1)%13,1)
				cnt2-=1

		for qf in q_find:
			epf_val+=qf['value']
			payed_epf_break_up.append({'month':calendar.month_name[mon2],'value':qf['value']})
			mon2=max((mon2+1)%13,1)
			cnt2-=1

		epf_val += final_value_e
		payed_epf_break_up.append({'month':calendar.month_name[mon2],'value':final_value_e})
		cnt2-=1
		mon2=max((mon2+1)%13,1)
				
		while cnt2>0:
			epf_val+=final_value_e1
			payed_epf_break_up.append({'month':calendar.month_name[mon2],'value':final_value_e1})
			mon2=max((mon2+1)%13,1)
			cnt2-=1
		
		flag_e=1
		data={'sub_name':"EPF",'sub_id':-1,'value':epf_val,'break_up':payed_epf_break_up}
	if flag_e==0:
		data={'sub_name':"EPF",'sub_id':-1,'value':0,'break_up':payed_epf_break_up}

	return data

def calculate_other_income(emp_id,session):

	value=0
	data=[]
	qry_other_loss=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__field="OTHER INCOME").values('Value','Dec_Id','Dec_Id__value').exclude(status="DELETE").order_by('-id')
	for q in qry_other_loss:
		value+=q['Value']
		data.append({'id':q['Dec_Id'],'name':q['Dec_Id__value'],'value':q['Value']})

	return {'data':data,'value':value}


def calculate_income_tax(emp_id,session,final_value):
	
	########## final_value=income_tax_sum-hra exemption-loss deduction (80c, 80ccd, 80d) #############
	age = calculate_emp_age(emp_id,session)
	income_tax=0
	qry_range=Income_Tax_Range.objects.filter(from_age__lte=age,to_age__gte=age,session=session).values('from_value','to_value','percent')
	for q in qry_range:
		if final_value>=q['to_value']:
			income_tax+=(q['percent']*(q['to_value']-q['from_value']))/100
		else:
			income_tax+=(q['percent']*(final_value-q['from_value']))/100
			break

	return round(income_tax)

def calculate_tax_after_rebate(final_value,income_tax, session):

	qry1 = AccountsDropdown.objects.filter(field__contains="REBATE 87A",value="REBATE AMOUNT", session=session).values('sno')
	qry2 = AccountsDropdown.objects.filter(pid=qry1[0]['sno'],session=session).exclude(value__isnull=True).values('value')
	
	qry3 = AccountsDropdown.objects.filter(field__contains="CESS",value="PERCENT", session=session).values('sno')
	qry4 = AccountsDropdown.objects.filter(pid=qry3[0]['sno'],session=session).exclude(value__isnull=True).values('value')
	
	qry5 = AccountsDropdown.objects.filter(field__contains="REBATE 87A",value="REBATE UPPER LIMIT", session=session).values('sno')
	qry6 = AccountsDropdown.objects.filter(pid=qry5[0]['sno'],session=session).exclude(value__isnull=True).values('value')
	
	rebate_amount=0
	cess_amount=0
	income_tax2=income_tax
	if final_value<int(qry6[0]['value']):
		income_tax2=income_tax-int(qry2[0]['value'])
		if income_tax2<0:
			income_tax2=0
		rebate_amount=income_tax-income_tax2
		income_tax=income_tax2
	if income_tax >0:
		cess_amount=round((float(qry4[0]['value'])*(income_tax))/100)
		income_tax=round(income_tax+cess_amount)

	data={'rebate_amount':rebate_amount,'cess_amount':cess_amount,'final_tax':income_tax}
	return data


def calculate_monthly_income_tax(final_income_tax,session,emp_id,month):
	count=12
	count2=12
	mon=4
	payed_tax=[]
	payed_tax2=[]
	tax_p=0

	monthly_tax=final_income_tax
	f_tax=monthly_tax

	if monthly_tax is None:
		monthly_tax=0
	if f_tax is None:
		f_tax=0

	qry_tax=Income_Tax_Paid.objects.filter(emp_id=emp_id,session=session).exclude(month=month).values('monthly_tax_paid','month').order_by('id')
	for q in qry_tax:
		while mon != q['month']:
			payed_tax.append({'month':calendar.month_name[mon],'value':0})
			payed_tax2.append({'month':calendar.month_name[mon],'value':0})
			mon=max((mon+1)%13,1)
			count-=1
			count2-=1

		payed_tax.append({'month':calendar.month_name[q['month']],'value':q['monthly_tax_paid']})
		payed_tax2.append({'month':calendar.month_name[q['month']],'value':q['monthly_tax_paid']})
		
		tax_p+=q['monthly_tax_paid']
		monthly_tax-=q['monthly_tax_paid']
		mon=max((mon+1)%13,1)
		count-=1
		count2-=1

	qry_check = Income_Tax_Paid.objects.filter(emp_id=emp_id,session=session,month=month).values('monthly_tax_paid')
	if len(qry_check)>0:
		f_tax = qry_check[0]['monthly_tax_paid']
		if f_tax is None:
			f_tax=0
		count-=1
		payed_tax.append({'month':calendar.month_name[month],'value':f_tax})
	
		if count>0:
			monthly_tax=max(round((monthly_tax-f_tax)/count),0)
			while count>0:
				payed_tax.append({'month':calendar.month_name[mon],'value':monthly_tax})
				mon=max((mon+1)%13,1)
				count-=1
		else:
			monthly_tax=0
	else:
		if count>0:
			monthly_tax=max(round(monthly_tax/count),0)
			while count>0:
				payed_tax.append({'month':calendar.month_name[mon],'value':monthly_tax})
				mon=max((mon+1)%13,1)
				count-=1
		else:
			monthly_tax=0
		f_tax=monthly_tax

	return {'payed_tax_break_up':payed_tax,'payed_tax_break_up2':payed_tax2,'payed_tax_amt':tax_p,'monthly_tax':(f_tax),'rem_month':count2}

################### credit date check and verified check ##################

def generate_monthly_salary(request):
	data_values={}
	final_data=[]
	msg=""
	status=401
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				if request.method == 'GET': 
					sdate=request.GET['month'].split('/')
					date=datetime(year=int(sdate[1]),month=int(sdate[0]),day=1)
					
					session_id=getCurrentSession(date)
					session=session_id
					if session == -1:
						return JsonResponse(data={'msg':'Accounts Session not found'},status=202)
					month = getSalaryMonth(session_id)
					
					fr_month=date.month
					
					dept=request.GET['dept']
					org=request.GET['org']

					emps=[]
					if dept == 'ALL':
						dept_sno=EmployeeDropdown.objects.filter(pid=org,value="DEPARTMENT").values('sno')
						query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'],field="DEPARTMENT").values_list('sno',flat=True)

						############################# GET ALL EMPLOYEES WHOSE PAYABLE DAYS HAS BEEN GENERATED FOR THE SELECTED MONTH #######
						emps =  EmployeePayableDays.objects.filter(emp_id__dept__in=list(query),session=session,month=fr_month).values('working_days','leave','holidays','total_days','emp_id__name','emp_id','emp_id__dept__value','emp_id__desg__value')
							
					else:
						############################# GET ALL EMPLOYEES WHOSE PAYABLE DAYS HAS BEEN GENERATED FOR THE SELECTED MONTH AND DEPARTMENT #######
						
						emps =  EmployeePayableDays.objects.filter(emp_id__dept=dept,session=session,month=fr_month).values('working_days','leave','holidays','total_days','emp_id__name','emp_id','emp_id__dept__value','emp_id__desg__value')
						
					final_data=[]
					total_time=0

					# if fr_month > month:
					# 	####################### IF SELECTED MONTH IS GREATER THAN THE MONTH FOR WHICH SALARY HAS NOT BEEN LOCKED, SHOW CONFLICT MESSAGE ######################
					# 	######################## e.g. if user select june  month and salary of may has not been locked, it shows conflict message ###############################
					# 	status = 202
					# 	final_data={}
					# 	final_data = {'msg':"Salary of previous month has not been generated yet"}
					if len(emps) == 0:
						###################### show conflict message if payable days has not been generated for the selected month
						status = 202
						final_data={}
						final_data = {'msg':"Payable Days has not been generated for this month"}
					elif fr_month == month:
						
						for e in emps:
							start=time.time()

							emp_id=e['emp_id']
							
							######################## GET PAYABLE DAYS OF EMPLOYEE ################
							working=e['working_days']
							leave=e['leave']
							holiday=e['holidays']
							actual_days=e['total_days']

							########################## CALCULATE NET WORKING DAYS ###############
							working_days=working+leave+holiday
								
							gross_value=0
							payable_value=0
							taxstatus_li=[0,1]
							
							########################## GET SALARY COMPONENTS, GROSS VALUE and payable value OF EMPLOYEE ##########
							payable=gross_payable_salary_components(emp_id,working_days,actual_days,session,taxstatus_li,month)
							for p in payable:
								gross_value+=p['gross_value']
								payable_value+=p['payable_value']

							############### arrear calculation #####################

							arrear_value=0
							inc_arrear=0
							day_arrear=0
							da_arrear=0
							s_arrear=0
							arrear_list=[]

							payable_inc_arrear=calculate_increment_days_arrear(emp_id,session,month,calculate_increment_days(emp_id,session,month))

							n=len(payable_inc_arrear['diff_payable'])
							
							for i in range(n):
								inc_arrear+=(int)(payable_inc_arrear['diff_payable'][i]['diff_value'])

							days_arrear=calculate_days_arrear(emp_id,session,month)
							sign=calculate_sign_in_out_arrear(emp_id,session,month)
							additional_arrear=calculate_additional_arrear(emp_id,session)
							
							payable_days_arrear=gross_payable_salary_components(emp_id,days_arrear['working_days'],days_arrear['actual_days'],session,taxstatus_li,month)
							payable_sign_arrear=gross_payable_salary_components(emp_id,sign['working_days'],sign['actual_days'],session,taxstatus_li,month)
							
							for d in payable_days_arrear:
								day_arrear+=d['payable_value']

							for s in payable_sign_arrear:
								s_arrear+=s['payable_value']

							payable_da_arrear= calculate_da_arrear(emp_id,session,calculate_da_days(emp_id,session))
							da_arrear=payable_da_arrear['difference']

							########## arrear calculation end ##############################

							income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,payable,month,payable_da_arrear,payable_inc_arrear,payable_days_arrear,additional_arrear['value'],payable_sign_arrear)
							

							############ sub or add other income ##########
							other_income=calculate_other_income(emp_id,session)

							##################################################

							constant_deductions = calculate_constant_deduction(emp_id,session,payable,taxstatus_li,month)
							variable_deductions = calculate_variable_deduction(emp_id,session,month)

							hra_for1=0
							for comp in income_tax_sum_comp:
								if 'HRA' in comp['Ing_value']:
									hra_for1+=comp['value']

							#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)

							income_tax_sum=0
							income_tax_sum_comp_data=[]
							for d in income_tax_sum_comp:
								income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value']})
								income_tax_sum+=d['value']

							hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
							hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

							hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

							loss=calculate_loss_deductions(emp_id,session,payable,constant_deductions)

							qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
							std_ded_amt = int(qry_std_ded[0]['value'])

							final_value = max(other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt,0)
							income_tax=calculate_income_tax(emp_id,session,final_value)
							
							tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
							
							final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)

							arrear_value = inc_arrear + day_arrear + da_arrear + additional_arrear['value'] + s_arrear

							payable_value = max(payable_value + arrear_value- (constant_deductions['final_value']+variable_deductions['total_value']+final_monthly_tax['monthly_tax']),0)
							
							arrear_list.append({'arrear_name':'Increment Arrear','value':inc_arrear})
							arrear_list.append({'arrear_name':'Days Arrear','value':day_arrear})
							arrear_list.append({'arrear_name':'DA Arrear','value':da_arrear})
							arrear_list.append({'arrear_name':'Additional Arrear','value':additional_arrear['value']})
							arrear_list.append({'arrear_name':'SIGN IN/OUT Arrear','value':s_arrear})

							variation = calculate_variation(emp_id,month,gross_value)


							##################### check generated salary month ###############################

							q_gen = DaysGenerateLog.objects.filter(sessionid=session,acc_sal_lock='Y').values_list('month',flat=True) 

							final_data.append({'working_days':working,'leave':leave,'holiday':holiday,'actual_days':actual_days,'gross_payable_salary_components':payable,'gross_value':gross_value,'payable_value':payable_value,'income_tax_sum_comp':income_tax_sum_comp_data,'hra_exemption':{'data':{'HRA ACTUAL RECEIVED':hra_for1,'ACTUAL RENT PAID LESS 10 % OF SALARY':hra_for2,'50 % OR 40 % OF SALARY':hra_for3['value']},'final_value':hra_exemption},'loss_deductions':loss,'income_tax':income_tax,'cess_amount':tax_after_rebate['cess_amount'],'rebate_amount':tax_after_rebate['rebate_amount'],'final_yearly_tax':tax_after_rebate['final_tax'],'final_monthly_tax':final_monthly_tax['monthly_tax'],'emp_code':emp_id,'emp_name':e['emp_id__name'],'dept':e['emp_id__dept__value'],'desg':e['emp_id__desg__value'],'arrear':{'data':arrear_list,'final_arrear_value':arrear_value},'constant_deductions':constant_deductions,'variable_deductions':variable_deductions,'other_income':other_income,'income_tax_sum':income_tax_sum,'residence_location':hra_for3['name'],'payed_tax_amt':final_monthly_tax['payed_tax_amt'],'remaining_month':final_monthly_tax['rem_month'],'variation':variation,'STANDARD DEDUCTION':std_ded_amt,'payed_tax_break_up':final_monthly_tax['payed_tax_break_up2'],'sal_generated_month':list(q_gen)})
							status=200
					
							##print(time.time()-start,emp_id)
							total_time+=time.time()-start
							#break
						##print(total_time)
					else:
						month=fr_month
						final_data=[]
						for e in emps:

							start=time.time()
							emp_id=e['emp_id']
							
							working=e['working_days']
							leave=e['leave']
							holiday=e['holidays']
							actual_days=e['total_days']

							working_days=working+leave+holiday
							
							gross_value=0
							payable_value=0
							taxstatus_li=[0,1]
							
							payable=stored_gross_payable_salary_components(emp_id,session,month)
							for p in payable:
								gross_value+=p['gross_value']
								payable_value+=p['payable_value']

							############### arrear calculation #####################

							arrear_value=0
							arrear_list=[]

							arrear_data=stored_arrear(emp_id,month,session)
							arrear_value=arrear_data['final_value']
							arrear_list=arrear_data['data']

							########## arrear calculation end ##############################

							income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,payable,month,arrear_list[2],arrear_list[4],arrear_list[3]['value'],arrear_list[0]['value'],arrear_list[1]['value'])
							

							############ sub or add other income ##########
							other_income=calculate_other_income(emp_id,session)

							##################################################

							constant_deductions = calculate_constant_deduction_stored(emp_id,session,payable,taxstatus_li,month)
							variable_deductions = calculate_variable_deduction_stored(emp_id,session,month)

							
							income_tax_sum=0
							income_tax_sum_comp_data=[]
							for d in income_tax_sum_comp:
								income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value']})
								income_tax_sum+=d['value']

							hra_for1=0
							for comp in income_tax_sum_comp:
								if 'HRA' in comp['Ing_value']:
									hra_for1+=comp['value']
							
							#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)
							hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
							hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

							hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

							loss=calculate_loss_deductions(emp_id,session,payable,constant_deductions)

							qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
							std_ded_amt = int(qry_std_ded[0]['value'])

							final_value = max(0,other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt)
							income_tax=calculate_income_tax(emp_id,session,final_value)
							
							tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
							
							final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)

							payable_value = max(payable_value +arrear_value - (constant_deductions['final_value']+variable_deductions['total_value']+final_monthly_tax['monthly_tax']),0)
							
							variation = calculate_variation(emp_id,month,gross_value)

							arrear_data=[]
							for a in arrear_list:
								arrear_data.append({'arrear_name':a['arrear_name'],'value':a['final_value']})

							q_gen = DaysGenerateLog.objects.filter(sessionid=session,acc_sal_lock='Y').values_list('month',flat=True) 

							final_data.append({'working_days':working,'leave':leave,'holiday':holiday,'actual_days':actual_days,'gross_payable_salary_components':payable,'gross_value':gross_value,'payable_value':payable_value,'income_tax_sum_comp':income_tax_sum_comp_data,'hra_exemption':{'data':{'HRA ACTUAL RECEIVED':hra_for1,'ACTUAL RENT PAID LESS 10 % OF SALARY':hra_for2,'50 % OR 40 % OF SALARY':hra_for3['value']},'final_value':hra_exemption},'loss_deductions':loss,'income_tax':income_tax,'cess_amount':tax_after_rebate['cess_amount'],'rebate_amount':tax_after_rebate['rebate_amount'],'final_yearly_tax':tax_after_rebate['final_tax'],'final_monthly_tax':final_monthly_tax['monthly_tax'],'emp_code':emp_id,'emp_name':e['emp_id__name'],'dept':e['emp_id__dept__value'],'desg':e['emp_id__desg__value'],'arrear':{'data':arrear_data,'final_arrear_value':arrear_value},'constant_deductions':constant_deductions,'variable_deductions':variable_deductions,'other_income':other_income,'income_tax_sum':income_tax_sum,'residence_location':hra_for3['name'],'payed_tax_amt':final_monthly_tax['payed_tax_amt'],'remaining_month':final_monthly_tax['rem_month'],'variation':variation,'STANDARD DEDUCTION':std_ded_amt,'payed_tax_break_up':final_monthly_tax['payed_tax_break_up2'],'sal_generated_month':list(q_gen)})
							status=200
							##print(time.time()-start,emp_id)

					
				elif request.method == 'POST':
					final_data={}
					data=json.loads(request.body)

					today_date = datetime.today()
					
					org_sno=EmployeeDropdown.objects.filter(field="ORGANIZATION").values_list('sno',flat=True)
					dept_sno=EmployeeDropdown.objects.filter(pid__in=org_sno,value="DEPARTMENT").exclude(value__isnull=True).values_list('sno',flat=True)
					
					query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid__in=dept_sno,field="DEPARTMENT").values_list('sno',flat=True)

					fr_month=int(str(data['month']).split('/')[0])
					session=getCurrentSession(None)
					month=getSalaryMonth(session)
					############################# GET ALL EMPLOYEES WHOSE PAYABLE DAYS HAS BEEN GENERATED FOR THE SELECTED MONTH #######
					emps =  EmployeePayableDays.objects.filter(emp_id__dept__in=list(query),session=session,month=fr_month).values('working_days','leave','holidays','total_days','emp_id__name','emp_id','emp_id__dept__value','emp_id__desg__value')
					
					final_data={'emps':list(emps)}

					
					if fr_month >month:
						status = 202
						msg="Salary cannot be generated"
					elif fr_month < month:
						status = 202
						msg="Salary has been already generated"
					else:
						for e in emps:
							start=time.time()
							emp_id=e['emp_id']
							
							q_days = EmployeePayableDays.objects.filter(emp_id=emp_id,session=session,month=month).values('working_days','leave','holidays','total_days')
							
							q_bank_acc_no = EmployeePerdetail.objects.filter(emp_id=emp_id).values('bank_Acc_no','uan_no')

							q_update = EmployeePayableDays.objects.filter(emp_id=emp_id,session=session,month=month).update(bank_acc_no=q_bank_acc_no[0]['bank_Acc_no'],uan_no=q_bank_acc_no[0]['uan_no'])

							working=e['working_days']
							leave=e['leave']
							holiday=e['holidays']
							actual_days=e['total_days']

							working_days=working+leave+holiday
							
							gross_value=0
							payable_value=0
							taxstatus_li=[0,1]
							
							payable=gross_payable_salary_components(emp_id,working_days,actual_days,session,taxstatus_li,month)
							for p in payable:
								gross_value+=p['gross_value']
								payable_value+=p['payable_value']

							############### arrear calculation #####################

							arrear_value=0
							inc_arrear=0
							day_arrear=0
							da_arrear=0
							s_arrear=0
							arrear_list=[]

							inc_days_f=calculate_increment_days(emp_id,session,month)
							payable_inc_arrear=calculate_increment_days_arrear(emp_id,session,month,inc_days_f)

							n=len(payable_inc_arrear['diff_payable'])
							
							for i in range(n):
								inc_arrear+=(int)(payable_inc_arrear['diff_payable'][i]['diff_value'])

							days_arrear=calculate_days_arrear(emp_id,session,month)
							sign=calculate_sign_in_out_arrear(emp_id,session,month)
							additional_arrear=calculate_additional_arrear(emp_id,session)
							
							payable_days_arrear=gross_payable_salary_components(emp_id,days_arrear['working_days'],days_arrear['actual_days'],session,taxstatus_li,month)
							payable_sign_arrear=gross_payable_salary_components(emp_id,sign['working_days'],sign['actual_days'],session,taxstatus_li,month)
							for d in payable_days_arrear:
								day_arrear+=d['payable_value']

							for s in payable_sign_arrear:
								s_arrear+=s['payable_value']

							da_days=calculate_da_days(emp_id,session)
							payable_da_arrear= calculate_da_arrear(emp_id,session,da_days)
							da_arrear=payable_da_arrear['difference']

							########## arrear calculation end ##############################

							income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,payable,month,payable_da_arrear,payable_inc_arrear,payable_days_arrear,additional_arrear['value'],payable_sign_arrear)
							

							############ sub or add other income ##########
							other_income=calculate_other_income(emp_id,session)

							##################################################

							constant_deductions = calculate_constant_deduction(emp_id,session,payable,taxstatus_li,month)
							variable_deductions = calculate_variable_deduction(emp_id,session,month)

							hra_for1=0
							for comp in income_tax_sum_comp:
								if 'HRA' in comp['Ing_value']:
									hra_for1+=comp['value']

							#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)

							income_tax_sum=0
							income_tax_sum_comp_data=[]
							for d in income_tax_sum_comp:
								income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value']})
								income_tax_sum+=d['value']

							hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
							hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

							hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

							loss=calculate_loss_deductions(emp_id,session,payable,constant_deductions)

							qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
							std_ded_amt = int(qry_std_ded[0]['value'])

							final_value = max(0,other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt)
							income_tax=calculate_income_tax(emp_id,session,final_value)
							
							tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
							
							final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)


							####### store arrear ################

							qry_sal_ing=SalaryIngredient.objects.filter(Ingredients__value='DA',session=session).exclude(status="DELETE").values('Formula','percent','id').order_by('-id')[:1]

							q_in_ar1 = MonthlyArrear_detail.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),Month=month,arrear_type='A',defaults={'value':additional_arrear['value']})

							q_in_ar2= MonthlyArrear_detail.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),Ing_Id=SalaryIngredient.objects.get(id=qry_sal_ing[0]['id']),Month=month,arrear_type='DA',defaults={'value':da_arrear})

							for inc in payable_inc_arrear['diff_payable']:
								q_in_ar3= MonthlyArrear_detail.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),Ing_Id=SalaryIngredient.objects.get(id=inc['Ing_Id']),Month=month,arrear_type='I',defaults={'value':inc['diff_value']})

							for si in payable_sign_arrear:
								q_in_ar4= MonthlyArrear_detail.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),Ing_Id=SalaryIngredient.objects.get(id=si['Ing_Id']),Month=month,arrear_type='S',defaults={'value':si['payable_value']})

							for l in payable_days_arrear:
								q_in_ar5 = MonthlyArrear_detail.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),Ing_Id=SalaryIngredient.objects.get(id=l['Ing_Id']),Month=month,arrear_type='L',defaults={'value':l['payable_value']})

							##############################  update credit status of arrear ##################
							for inc in inc_days_f:
								q_up=AccountsIncrementArrear.objects.filter(id=inc['id']).update(arrearCredited='Y',credit_date=today_date)

							for d in days_arrear['ids']:
								q_up=Days_Arrear_Leaves.objects.filter(leaveid=d).update(arrearCredited='Y',credit_date=today_date)

							for s in sign['ids']:
								q_up=Sign_In_Out_Arrear.objects.filter(id=s).update(credited='Y',credit_date=today_date)

							for add in additional_arrear['ids']:
								q_up=AdditionalArrear.objects.filter(id=add).update(arrearCredited='Y',credit_date=today_date)

							for da in da_days:
								q_up=DAArrear.objects.filter(id=da['id']).update(arrearCredited='Y',credit_date=today_date)
							#################### store payable component values ###############################################

							for p in payable:
								qry_payable_details = MonthlyPayable_detail.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),Ing_Id=SalaryIngredient.objects.get(id=p['Ing_Id']),session=AccountsSession.objects.get(id=session),Month=month,defaults={'gross_value':p['gross_value'],'payable_value':p['payable_value']})                         
							######## store income tax ###########################
							q_tax = Income_Tax_Paid.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),month=month,defaults={'income_tax_sum':income_tax_sum,'cess':tax_after_rebate['cess_amount'],'rebate':tax_after_rebate['rebate_amount'],'hra_exemption':hra_exemption,'monthly_tax_paid':final_monthly_tax['monthly_tax']})

							############# store constant deductions #######################
							for q in constant_deductions['data']:
								q_v = MonthlyDeductionValue.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),month=month,deduction_id=EmployeeDeductions.objects.get(id=q['ded_id']),defaults={'value':q['value']})
							#################### store variable deductions #################

							query=EmployeeDeductions.objects.filter(Emp_Id=emp_id,session=AccountsSession.objects.get(id=session),constantDeduction__isnull=True).values('id')
							for q in query:
								qry=EmployeeVariableDeduction.objects.filter(Emp_Id=emp_id,session=session,month=month,deduction_id=q['id']).values('id','value')
								value=0
								if len(qry)>0:
									value=qry[0]['value']
									q_v = MonthlyDeductionValue.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),month=month,deduction_id=EmployeeDeductions.objects.get(id=q['id']),defaults={'value':value})
								else:
									q_v = MonthlyDeductionValue.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),session=AccountsSession.objects.get(id=session),month=month,deduction_id=EmployeeDeductions.objects.get(id=q['id']),defaults={'value':0})

							#print(time.time()-start,emp_id)
							status = 200
							msg="Success"
						
						tdate = AccountsSession.objects.filter(id=session).values_list('Tdate',flat=True)[0] # TO CHECK NEED OF INCREASING CREDIT DATE
						
						q_sal = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values('Formula','percent','id','next_count_month','ingredient_nature').order_by('-id')
						for s in q_sal:
							if s['next_count_month'].month == month:
								add = s['ingredient_nature']
								mon3 = s['next_count_month'] + relativedelta(months=add)
								if mon3 >= tdate: # IF NEXT DATE IS GREATER THAN SESSION END DATE THEN DON'T UPDATE
									continue
								q_up = SalaryIngredient.objects.filter(id=s['id']).update(next_count_month=mon3)

						q_cons = ConstantDeduction.objects.filter(session=session).exclude(status="DELETE").values('creditdate','creditnature','id')
						
						
						for c in q_cons:
							if c['creditdate'].month == month:
								mon3 = c['creditdate'] + relativedelta(months=1)
								if mon3 >= tdate: # IF NEXT DATE IS GREATER THAN SESSION END DATE THEN DON'T UPDATE  
									continue
								q_up = ConstantDeduction.objects.filter(id=c['id']).update(creditdate=mon3)

						q_ses = AccountsSession.objects.filter(id=session).values('current_sal_month') # TO CHECK NEED OF INCREASING SALARY MONTH
						
						check_date = q_ses[0]['current_sal_month']==tdate.split("-")[1] 
						##NEW LINE TO CHECK IS CURRENT SET MONTH EQUALS TO SESSION END DATE##
						if not check_date: 
							##NEW LINE : IF CURRENT SET MONTH EQUALS TO SESSION END DATE THEN DONT INCREASE MONTH##
							mon = max((q_ses[0]['current_sal_month']+1)%13,1)
							q_ses_up = AccountsSession.objects.filter(id=session).update(current_sal_month=mon)

						q_upd = DaysGenerateLog.objects.filter(sessionid=session,month=month).update(tdsSheet=None,salarySheet=None,acc_sal_lock='Y')
					
					final_data = {'msg':msg}
				elif request.method == 'PUT':
					final_data={}
					data=json.loads(request.body)
					session=getCurrentSession(None)
					month=getSalaryMonth(session)
					emp_id = data['emp_id']

					if 'variable_deductions' in data:
						var_ded = data['variable_deductions']['data']
						for var in var_ded:
							q_id = EmployeeDeductions.objects.filter(Emp_Id=emp_id,session=session,variableDeduction=var['v_id']).exclude(status='DELETE').values('id')
							qry_var = EmployeeVariableDeduction.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),deduction_id=EmployeeDeductions.objects.get(id=q_id[0]['id']),month=month,session=AccountsSession.objects.get(id=session),defaults={'value':var['value']})

					elif 'income_tax' in data:
						income_tax = data['income_tax']
						q_income_tax = Income_Tax_Paid.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),month=month,session=AccountsSession.objects.get(id=session),defaults={'monthly_tax_paid':income_tax})
					q_upd = DaysGenerateLog.objects.filter(sessionid=session,month=month).update(tdsSheet=None,salarySheet=None)
					status=200
				else:
					status = 502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	
	return JsonResponse(data={'data':final_data},status=status)


def stored_arrear(emp_id,month,session):
	data=[]
	final_value=0
	q_add = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,session=session,Month=month,arrear_type='A').values('value')
	v=0
	for q in q_add:
		v+=q['value']
	data.append({'arrear_name':'Additional Arrear','value':v,'final_value':v})
	final_value+=v

	q_s = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,session=session,Month=month,arrear_type='S').values('value','Ing_Id','Ing_Id__Ingredients__value')
	v=0
	sign_data=[]
	for s in q_s:
		sign_data.append({'Ing_Id':s['Ing_Id'],'payable_value':s['value'],'value':s['Ing_Id__Ingredients__value']})
		v+=s['value']

	data.append({'arrear_name':'Sign In/Out Arrear','value':sign_data,'final_value':v})
	final_value+=v

	q_da = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,session=session,Month=month,arrear_type='DA').values('value')
	v=0
	for s in q_da:
		v+=s['value']
	data.append({'arrear_name':'DA Arrear','difference':v,'final_value':v})
	final_value+=v

	q_l = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,session=session,Month=month,arrear_type='L').values('value','Ing_Id','Ing_Id__Ingredients__value')
	v=0
	leave_data=[]
	for s in q_l:
		leave_data.append({'Ing_Id':s['Ing_Id'],'payable_value':s['value'],'value':s['Ing_Id__Ingredients__value']})
		v+=s['value']
	data.append({'arrear_name':'Leave Arrear','value':leave_data,'final_value':v})
	final_value+=v

	q_i = MonthlyArrear_detail.objects.filter(Emp_Id=emp_id,session=session,Month=month,arrear_type='I').values('value','Ing_Id','Ing_Id__Ingredients__value')
	v=0
	inc_data=[]


	for s in q_i:
		inc_data.append({'Ing_Id':s['Ing_Id'],'diff_value':s['value'],'value':s['Ing_Id__Ingredients__value']})
		v+=s['value']
	data.append({'arrear_name':'Increment Arrear','diff_payable':inc_data,'final_value':v})
	final_value+=v

	return {'data':data,'final_value':final_value}

def calculate_variation(emp_id,salary_month,gross_value):

	month2 = salary_month-1
	if month2<0:
		month2=12
	qry_last_month = MonthlyPayable_detail.objects.filter(Emp_Id=emp_id,Month=month2).aggregate(sum=Sum('gross_value'))

	if qry_last_month['sum'] is None:
		value=gross_value
	else:
		value=qry_last_month['sum']
	return  gross_value - value

########################################## excel generator ##########################################3


#def generate_tds_sheet(request):
def generate_tds_sheet(session,month):

	#session=getCurrentSession()
	
	#month = int(request.GET['month'])
	salary_month=getSalaryMonth(session)
	output = io.BytesIO()

	qry_session = AccountsSession.objects.filter(id=session).values('session')
	monthly_tds_name = "Accounts_excel/TDS_"+calendar.month_name[month]+"_"+qry_session[0]['session']+".xlsx"

	taxstatus_li=[0,1]
	output = io.BytesIO()

	workbook = Workbook(settings.FILE_PATH+monthly_tds_name)
	worksheet = workbook.add_worksheet()

	bold = workbook.add_format({'bold': True})

	col=0
	row=0
	worksheet.set_row(col,60)
	cell_format = workbook.add_format({'bold': True,'font_size':9,'font_name':'Arial','align':'center','valign':'vcenter'})
	cell_format2 = workbook.add_format({'font_size':8,'font_name':'Arial','align':'center','valign':'vcenter'})
	cell_format3 = workbook.add_format({'bold': True,'font_size':8,'font_name':'Arial','font_color':'green'})
	cell_format4 = workbook.add_format({'bold': True,'font_size':8,'font_name':'Arial','font_color':'blue'})
	cell_format5 = workbook.add_format({'bold': True,'font_size':8,'font_name':'Arial','font_color':'brown'})
	cell_format6 = workbook.add_format({'bold': True,'font_size':8,'font_name':'Arial','font_color':'black'})
	
	worksheet.write(row,col,'Calculation of Income Tax for Salaries As Year '+qry_session[0]['session'],cell_format)

	row+=1
	col=0
	worksheet.write(row,col,'Emp. Code No-',cell_format)
	
	row+=1
	col=0
	worksheet.write(row,col,'P   A   N     NO.',cell_format)
	
	qry_salary_comp = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values('Ingredients__value')
	col=0
	row+=1
	for sal in qry_salary_comp:
		worksheet.write(row,col,sal['Ingredients__value']+" Salary",cell_format3)
		row+=1

	worksheet.write(row,col,"Sub Total",cell_format3)
	row+=1
	worksheet.write(row,col,"Less:",cell_format)
	row+=1
	exemptions=declaration_components("exemptions", session)
	for ex in exemptions:
		worksheet.write(row,col,ex['value'],cell_format3)
		row+=1

	worksheet.write(row,col,"Gross Total Salary",cell_format3)
	row+=1

	row+=1

	worksheet.write(row,col,'Other Income',cell_format3)
	row+=1
	worksheet.write(row,col,'Gross total income',cell_format3)
	row+=1

	row+=1

	worksheet.write(row,col,'Deductions',cell_format)
	row+=1

	deduc=declaration_components("loss_deductions", session)
	
	for d in deduc:
		worksheet.write(row,col,d['value'],cell_format5)
		row+=1

	worksheet.write(row,col,'Taxable Income',cell_format5)
	row+=1

	row+=1

	worksheet.write(row,col,'Standard Deduction',cell_format5)
	row+=1
	worksheet.write(row,col,'Net Taxable Income',cell_format5)
	row+=1

	row+=1

	worksheet.write(row,col,'Income Tax',cell_format5)
	row+=1  
	worksheet.write(row,col,'Rebate 87 A',cell_format5)
	row+=1
	worksheet.write(row,col,'Cess',cell_format5)
	row+=1
	
	worksheet.write(row,col,'TOTAL TAX PAYABLE',cell_format5)
	row+=1
	
	row+=1

	for sal in qry_salary_comp:
		worksheet.write(row,col,sal['Ingredients__value']+" Salary Current Year",cell_format)
		row+=1
		mon=4
		while mon<=12:
			worksheet.write(row,col,calendar.month_name[mon],cell_format4)
			row+=1
			mon+=1
		mon=1
		while mon<=3:
			worksheet.write(row,col,calendar.month_name[mon],cell_format4)
			row+=1
			mon+=1
		worksheet.write(row,col,"Total",cell_format)
		row+=1

	worksheet.write(row,col,"ACTUAL RENT PAID",cell_format)
	row+=1
	# mon=4
	# while mon<=12:
	#   worksheet.write(row,col,calendar.month_name[mon],cell_format6)
	#   row+=1
	#   mon+=1
	# mon=1
	# while mon<=3:
	#   worksheet.write(row,col,calendar.month_name[mon],cell_format6)
	#   row+=1
	#   mon+=1
	# worksheet.write(row,col,"Total",cell_format)
	# row+=1
	worksheet.write(row,col,"MALE   (M) / FEMALE    (F) ",cell_format)
	row+=1
	worksheet.write(row,col,"AGE",cell_format)
	row+=1

	row+=1

	worksheet.write(row,col,"Residence Location",cell_format)
	row+=1

	# mon=4
	# while mon<=12:
	#   worksheet.write(row,col,calendar.month_name[mon],cell_format6)
	#   row+=1
	#   mon+=1
	# mon=1
	# while mon<=3:
	#   worksheet.write(row,col,calendar.month_name[mon],cell_format6)
	#   row+=1
	#   mon+=1
	# worksheet.write(row,col,"Total",cell_format)
	# row+=1

	row+=1

	worksheet.write(row,col,"Deduction of HRA",cell_format)
	row+=1

	worksheet.write(row,col,"HRA ACTUAL RECEIVED",cell_format6)
	row+=1

	worksheet.write(row,col,"ACTUAL RENT PAID LESS 10 % OF SALARY",cell_format6)
	row+=1

	worksheet.write(row,col,"50 % OR 40 % OF SALARY",cell_format6)
	row+=1

	worksheet.write(row,col,"Total",cell_format6)
	row+=1

	row+=1

	for d in deduc:
		worksheet.write(row,col,"Deductions "+d['value'],cell_format)
		row+=1

		for da in d['data']:
			worksheet.write(row,col,da['value'],cell_format6)
			row+=1

		if d['value'] == '80C':
			worksheet.write(row,col,'EPF',cell_format6)
			row+=1

		if d['value'] == '80D':
			worksheet.write(row,col,'MEDICLAIM',cell_format6)
			row+=1
		worksheet.write(row,col,"Total",cell_format6)
		row+=1


	worksheet.write(row,col,"PF Deduction",cell_format)
	row+=1

	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	worksheet.write(row,col,"Mediclaim Deduction",cell_format)
	row+=1
	
	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	row+=1
	
	worksheet.write(row,col,"Leave Arrear",cell_format)
	row+=1

	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	worksheet.write(row,col,"Increment Arrear",cell_format)
	row+=1

	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	worksheet.write(row,col,"DA Arrear",cell_format)
	row+=1

	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	worksheet.write(row,col,"Sign In/Out Arrear",cell_format)
	row+=1

	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	worksheet.write(row,col,"Additional Arrear",cell_format)
	row+=1

	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	row+=1

	worksheet.write(row,col,"Total Salary",cell_format)
	row+=1

	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	row+=1

	for sal in qry_salary_comp:
		worksheet.write(row,col,"Total Arrear "+sal['Ingredients__value'],cell_format)
		row+=1

		mon=4
		while mon<=12:
			worksheet.write(row,col,calendar.month_name[mon],cell_format6)
			row+=1
			mon+=1
		mon=1
		while mon<=3:
			worksheet.write(row,col,calendar.month_name[mon],cell_format6)
			row+=1
			mon+=1
		worksheet.write(row,col,"Total",cell_format)
		row+=1

	row+=1

	worksheet.write(row,col,"TDS Deducted",cell_format)
	row+=1

	mon=4
	while mon<=12:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	mon=1
	while mon<=3:
		worksheet.write(row,col,calendar.month_name[mon],cell_format6)
		row+=1
		mon+=1
	worksheet.write(row,col,"Total",cell_format)
	row+=1

	############# format end ##############################
	############# fill data #################################
	total_time=0
	q_emps = EmployeePerdetail.objects.filter(emp_id__in=list(EmployeePayableDays.objects.filter(session=session).values_list('emp_id',flat=True).distinct())).exclude(emp_id='00007').order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','pan_no','gender__value')
	
	for e in q_emps:
		start=time.time()
		emp_id=e['emp_id']
		col+=1
		row=0   
		
		worksheet.write(row,col,e['emp_id__name'],cell_format)
		row+=1

		worksheet.write(row,col,e['emp_id'],cell_format)
		row+=1

		worksheet.write(row,col,e['pan_no'],cell_format)
		row+=1

		
		q_days = EmployeePayableDays.objects.filter(emp_id=emp_id,session=session,month=month).values('working_days','leave','holidays','total_days')
		if len(q_days) >0:
			working=q_days[0]['working_days']
			leave=q_days[0]['leave']
			holiday=q_days[0]['holidays']
			actual_days=q_days[0]['total_days']
		else:
			working=0
			leave=0
			holiday=0
			actual_days=0

		emp_id=e['emp_id']
		working_days=working+leave+holiday
		
		gross_value=0
		payable_value=0
		taxstatus_li=[0,1]
		
		if salary_month == month:
			payable=gross_payable_salary_components(emp_id,working_days,actual_days,session,taxstatus_li,month)
			for p in payable:
				gross_value+=p['gross_value']
				payable_value+=p['payable_value']

			############### arrear calculation #####################

			arrear_value=0
			inc_arrear=0
			day_arrear=0
			da_arrear=0
			s_arrear=0
			arrear_list=[]

			payable_inc_arrear=calculate_increment_days_arrear(emp_id,session,month,calculate_increment_days(emp_id,session,month))

			n=len(payable_inc_arrear['diff_payable'])
			
			for i in range(n):
				inc_arrear+=(int)(payable_inc_arrear['diff_payable'][i]['diff_value'])

			days_arrear=calculate_days_arrear(emp_id,session,month)
			sign=calculate_sign_in_out_arrear(emp_id,session,month)
			additional_arrear=calculate_additional_arrear(emp_id,session)
			
			payable_days_arrear=gross_payable_salary_components(emp_id,days_arrear['working_days'],days_arrear['actual_days'],session,taxstatus_li,month)
			payable_sign_arrear=gross_payable_salary_components(emp_id,sign['working_days'],sign['actual_days'],session,taxstatus_li,month)
			for d in payable_days_arrear:
				day_arrear+=d['payable_value']

			for s in payable_sign_arrear:
				s_arrear+=s['payable_value']

			payable_da_arrear= calculate_da_arrear(emp_id,session,calculate_da_days(emp_id,session))
			da_arrear=payable_da_arrear['difference']

			########## arrear calculation end ##############################
			income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,payable,month,payable_da_arrear,payable_inc_arrear,payable_days_arrear,additional_arrear['value'],payable_sign_arrear)
			
			############ sub or add other income ##########
			other_income=calculate_other_income(emp_id,session)

			##################################################

			constant_deductions = calculate_constant_deduction(emp_id,session,payable,taxstatus_li,month)
			variable_deductions = calculate_variable_deduction(emp_id,session,month)

			hra_for1=0
			for comp in income_tax_sum_comp:
				if 'HRA' in comp['Ing_value']:
					hra_for1+=comp['value']

			#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)

			income_tax_sum=0
			income_tax_sum_comp_data=[]

			for d in income_tax_sum_comp:
				income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value'],'Ing_Id':d['Ing_Id']})
				income_tax_sum+=d['value']

			hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
			hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

			hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

			loss=calculate_loss_deductions(emp_id,session,payable,constant_deductions)

			qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
			std_ded_amt = int(qry_std_ded[0]['value'])

			final_value = max(0,other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt)
			income_tax=calculate_income_tax(emp_id,session,final_value)
			
			tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
			
			final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)

			payable_value = payable_value - (constant_deductions['final_value']+variable_deductions['total_value']+final_monthly_tax['monthly_tax'])
			arrear_value = inc_arrear + day_arrear + da_arrear + additional_arrear['value']

			# arrear_list.append({'arrear_name':'Increment Arrear','value':inc_arrear})
			# arrear_list.append({'arrear_name':'Days Arrear','value':day_arrear})
			# arrear_list.append({'arrear_name':'DA Arrear','value':da_arrear})
			# arrear_list.append({'arrear_name':'Additional Arrear','value':additional_arrear['value']})
		else:
			payable=stored_gross_payable_salary_components(emp_id,session,month)
			for p in payable:
				gross_value+=p['gross_value']
				payable_value+=p['payable_value']

		
			############### arrear calculation #####################

			arrear_value=0
			inc_arrear=0
			day_arrear=0
			da_arrear=0
			s_arrear=0
			arrear_list=[]

			arrear_data=stored_arrear(emp_id,month,session)
			arrear_value=arrear_data['final_value']
			
			s_arrear=arrear_data['data'][1]['value']
			additional_arrear=arrear_data['data'][0]['value']
			day_arrear=arrear_data['data'][3]['value']
		
			inc_arrear=arrear_data['data'][4]

			da_arrear=arrear_data['data'][2]

			
			########## arrear calculation end ##############################



			income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,payable,month,da_arrear,inc_arrear,day_arrear,additional_arrear,s_arrear)
			
			############ sub or add other income ##########
			other_income=calculate_other_income(emp_id,session)

			##################################################

			constant_deductions = calculate_constant_deduction_stored(emp_id,session,payable,taxstatus_li,month)
			variable_deductions = calculate_variable_deduction_stored(emp_id,session,month)

			hra_for1=0
			for comp in income_tax_sum_comp:
				if 'HRA' in comp['Ing_value']:
					hra_for1+=comp['value']

			#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)

			income_tax_sum=0
			income_tax_sum_comp_data=[]

			for d in income_tax_sum_comp:
				income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value'],'Ing_Id':d['Ing_Id']})
				income_tax_sum+=d['value']

			hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
			hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

			hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

			loss=calculate_loss_deductions(emp_id,session,payable,constant_deductions)

			qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
			std_ded_amt = int(qry_std_ded[0]['value'])

			final_value = max(0,other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt)
			income_tax=calculate_income_tax(emp_id,session,final_value)
			
			tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
			
			final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)

			payable_value = payable_value - (constant_deductions['final_value']+variable_deductions['total_value']+final_monthly_tax['monthly_tax'])
			
			s_arrear_v=arrear_data['data'][1]['value']
			additional_arrear_v=arrear_data['data'][0]['value']
			day_arrear_v=arrear_data['data'][3]['value']
		
			inc_arrear=arrear_data['data'][4]
			da_arrear=arrear_data['data'][2]

			arrear_value = arrear_data['data'][4]['final_value'] + arrear_data['data'][3]['final_value'] + arrear_data['data'][2]['final_value'] + arrear_data['data'][0]['final_value'] + arrear_data['data'][1]['final_value']
			
		################# set data to excel ##############################################
		ind=0

		for sal in qry_salary_comp:
			try:
				if income_tax_sum_comp_data[ind]['Ing_value'] == sal['Ingredients__value']:
					worksheet.write(row,col,income_tax_sum_comp_data[ind]['value'],cell_format3)
					row+=1
					ind+=1
				else:
					worksheet.write(row,col,0,cell_format3)
					row+=1
			except:
				worksheet.write(row,col,0,cell_format3)
				row+=1
		
		worksheet.write(row,col,income_tax_sum,cell_format3)
		row+=1

		row+=1

		worksheet.write(row,col,hra_exemption,cell_format3)
		row+=1

		gross_total_salary = income_tax_sum-hra_exemption
		worksheet.write(row,col,gross_total_salary,cell_format3)
		row+=1

		row+=1

		worksheet.write(row,col,other_income['value'],cell_format3)
		row+=1

		gross_total_income =gross_total_salary+other_income['value']
		
		worksheet.write(row,col,gross_total_income,cell_format3)
		row+=1

		row+=2

		for l in loss['data']:
			worksheet.write(row,col,l['final_value'],cell_format5)
			row+=1

		taxable_income = max(0,gross_total_income - loss['value'])
		
		worksheet.write(row,col,taxable_income,cell_format5)
		row+=1

		row+=1

		qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
		std_ded_amt = int(qry_std_ded[0]['value'])

		worksheet.write(row,col,std_ded_amt,cell_format5)
		row+=1

		net_taxable_income = max(taxable_income - std_ded_amt,0)

		worksheet.write(row,col,net_taxable_income,cell_format5)
		row+=1

		row+=1

		worksheet.write(row,col,income_tax,cell_format5)
		row+=1

		worksheet.write(row,col,tax_after_rebate['rebate_amount'],cell_format5)
		row+=1

		worksheet.write(row,col,tax_after_rebate['cess_amount'],cell_format5)
		row+=1

		total_tax_payable = tax_after_rebate['final_tax']

		worksheet.write(row,col,total_tax_payable,cell_format5)
		row+=1

		row+=1

		ind=0
		total_salary_month=[0,0,0,0,0,0,0,0,0,0,0,0]
		for sal in qry_salary_comp:
			row+=1
			try:
				if income_tax_sum_comp[ind]['Ing_value'] == sal['Ingredients__value']:
					ni=len( income_tax_sum_comp[ind]['comp_month_break_up'])
					for d in range(ni):
						total_salary_month[d]+=income_tax_sum_comp[ind]['comp_month_break_up'][d]['payable_value']
						worksheet.write(row,col,income_tax_sum_comp[ind]['comp_month_break_up'][d]['payable_value'],cell_format4)
						row+=1
					worksheet.write(row,col,income_tax_sum_comp[ind]['comp_value'],cell_format)
					row+=1
					ind+=1
					
				else:
					mon=4
					while mon<=12:
						worksheet.write(row,col,0,cell_format4)
						row+=1
						mon+=1
					mon=1
					while mon<=3:
						worksheet.write(row,col,0,cell_format4)
						row+=1
						mon+=1
					worksheet.write(row,col,0,cell_format)
					row+=1
					
			except:
				mon=4
				while mon<=12:
					worksheet.write(row,col,0,cell_format4)
					row+=1
					mon+=1
				mon=1
				while mon<=3:
					worksheet.write(row,col,0,cell_format4)
					row+=1
					mon+=1
				worksheet.write(row,col,0,cell_format)
				row+=1
		
		qry_rent_per_month=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__value="RENT PER MONTH").values('Value').exclude(status="DELETE").order_by('-id')[:1]
		qry_no_of_month=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__value="NUMBER OF MONTHS").values('Value').exclude(status="DELETE").order_by('-id')[:1]

		try:
			worksheet.write(row,col,qry_rent_per_month[0]['Value']*qry_no_of_month[0]['Value'],cell_format)
			row+=1
		except:
			worksheet.write(row,col,0,cell_format)
			row+=1

		worksheet.write(row,col,e['gender__value'],cell_format)
		row+=1

		worksheet.write(row,col,calculate_emp_age(e['emp_id'],session),cell_format)
		row+=1

		row+=1

		qry_residence_location=Employee_Declaration.objects.filter(Emp_Id=emp_id,Session_Id=session,Dec_Id__field="RESIDENCE LOCATION").values('Value','Dec_Id','Dec_Id__value').exclude(status="DELETE").order_by('-id')[:1]
		try:
			worksheet.write(row,col,qry_residence_location[0]['Dec_Id__value'],cell_format)
			row+=1
		except:
			worksheet.write(row,col,"N/A",cell_format)
			row+=1

		row+=2

		worksheet.write(row,col,hra_for1,cell_format)
		row+=1

		worksheet.write(row,col,hra_for2,cell_format)
		row+=1

		worksheet.write(row,col,hra_for3['value'],cell_format)
		row+=1

		worksheet.write(row,col,hra_exemption,cell_format)
		row+=1

		row+=1

		for l in loss['data']:
			row+=1
			for d in l['data']:
				worksheet.write(row,col,d['value'],cell_format)
				row+=1
			worksheet.write(row,col,l['final_value'],cell_format)
			row+=1

		
		flag_e=0
		flag_m=0
		for c in constant_deductions['data']:
			if c['name'] == 'EPF':
				row+=1
				epf_data=calculate_epf(emp_id,session,taxstatus_li,payable)

				for ep in epf_data['break_up']:
					worksheet.write(row,col,ep['value'],cell_format4)
					row+=1
					
				flag_e=1
				worksheet.write(row,col,epf_data['value'],cell_format)
				row+=1
				break


		if flag_e==0:
			mon=4
			row+=1
			while mon<=12:
				worksheet.write(row,col,0,cell_format4)
				row+=1
				mon+=1
			mon=1
			while mon<=3:
				worksheet.write(row,col,0,cell_format4)
				row+=1
				mon+=1
			worksheet.write(row,col,0,cell_format)
			row+=1


		for c in constant_deductions['data']:
			if c['name'] == 'MEDICLAIM':

				med_data=calculate_mediclaim(emp_id,session,taxstatus_li,payable)
				row+=1
				for me in med_data['break_up']:
					worksheet.write(row,col,me['value'],cell_format4)
					row+=1

				flag_m=1
				worksheet.write(row,col,me['value'],cell_format)
				row+=1
				break
		
		if flag_m==0:
			mon=4
			row+=1
			while mon<=12:
				worksheet.write(row,col,0,cell_format4)
				row+=1
				mon+=1
			mon=1
			while mon<=3:
				worksheet.write(row,col,0,cell_format4)
				row+=1
				mon+=1
			worksheet.write(row,col,0,cell_format)
			row+=1

		row+=1

		arrear_value=0
		net_arrear_break_up=[]
		g=0
		while g<12:
			net_arrear_break_up.append(0)
			g+=1
		########### leave arrear ##################
		row+=1
		u=0
		n=len(income_tax_sum_comp)
		final_value=0
		while u<12:
			leave_arrear_value=0
			for i in range(n):
				leave_arrear_value+=income_tax_sum_comp[i]['leave_arrear']['break_up'][u]['value']

			final_value+=leave_arrear_value
			net_arrear_break_up[u]+=leave_arrear_value
			worksheet.write(row,col,leave_arrear_value,cell_format)
			row+=1
			u+=1
			
		worksheet.write(row,col,final_value,cell_format)
		row+=1
		arrear_value+=final_value
		########### increment arrear ##################
		row+=1
		u=0
		n=len(income_tax_sum_comp)
		final_value=0
		while u<12:
			leave_arrear_value=0
			for i in range(n):
				leave_arrear_value+=income_tax_sum_comp[i]['increment_arrear']['break_up'][u]['value']

			final_value+=leave_arrear_value
			net_arrear_break_up[u]+=leave_arrear_value
			worksheet.write(row,col,leave_arrear_value,cell_format)
			row+=1
			u+=1
			
		worksheet.write(row,col,final_value,cell_format)
		row+=1
		arrear_value+=final_value
		########### DA arrear ##################
		row+=1
		u=0
		n=len(income_tax_sum_comp)
		final_value=0
		while u<12:
			leave_arrear_value=0
			for i in range(n):
				try:
					leave_arrear_value+=income_tax_sum_comp[i]['da_arrear']['break_up'][u]['value']
				except:
					leave_arrear_value+=0

			final_value+=leave_arrear_value
			net_arrear_break_up[u]+=leave_arrear_value
			
			worksheet.write(row,col,leave_arrear_value,cell_format)
			row+=1
			u+=1
			
		worksheet.write(row,col,final_value,cell_format)
		row+=1
		arrear_value+=final_value
		########### sign in/out arrear ##################
		row+=1
		u=0
		n=len(income_tax_sum_comp)
		final_value=0
		while u<12:
			leave_arrear_value=0
			for i in range(n):
				leave_arrear_value+=income_tax_sum_comp[i]['sign_in_out_arrear']['break_up'][u]['value']

			final_value+=leave_arrear_value
			net_arrear_break_up[u]+=leave_arrear_value
			
			worksheet.write(row,col,leave_arrear_value,cell_format)
			row+=1
			u+=1
			
		worksheet.write(row,col,final_value,cell_format)
		row+=1
		arrear_value+=final_value
		########### additional arrear ##################
		row+=1
		u=0
		n=len(income_tax_sum_comp)
		final_value=0
		while u<12:
			leave_arrear_value=0
			for i in range(n):
				try:
					leave_arrear_value+=income_tax_sum_comp[i]['additional_arrear']['break_up'][u]['value']
				except:
					leave_arrear_value+=0

			final_value+=leave_arrear_value
			net_arrear_break_up[u]+=leave_arrear_value
			
			worksheet.write(row,col,leave_arrear_value,cell_format)
			row+=1
			u+=1
			
		worksheet.write(row,col,final_value,cell_format)
		row+=1
		arrear_value+=final_value

		row+=2

		total_val=0
		for t,a in zip(total_salary_month,net_arrear_break_up):
			worksheet.write(row,col,t+a,cell_format)
			row+=1
			total_val+=t

		worksheet.write(row,col,total_val+arrear_value,cell_format)
		row+=1

		row+=1

		ind=0
			
		for sal in qry_salary_comp:
			cnt=0
			row+=1
			fin_val=0
			try:
				if income_tax_sum_comp[ind]['Ing_value'] == sal['Ingredients__value']:
					while cnt<12:
						arr_value=0

						try:
							arr_value += income_tax_sum_comp[ind]['leave_arrear']['break_up'][cnt]['value']
						except:
							arr_value+=0

						try:
							arr_value += income_tax_sum_comp[ind]['increment_arrear']['break_up'][cnt]['value']
						except:
							arr_value+=0

						try:
							arr_value += income_tax_sum_comp[ind]['sign_in_out_arrear']['break_up'][cnt]['value']
						except:
							arr_value+=0

						try:
							arr_value += income_tax_sum_comp[ind]['da_arrear']['break_up'][cnt]['value']
						except:
							arr_value+=0

						try:
							arr_value += income_tax_sum_comp[ind]['additional_arrear']['break_up'][cnt]['value']
						except:
							arr_value+=0

						fin_val+=arr_value
						worksheet.write(row,col,arr_value,cell_format)
						row+=1
						cnt+=1

					worksheet.write(row,col,fin_val,cell_format)
					row+=1
				else:
					cnt=0
					while cnt<12:
						worksheet.write(row,col,0,cell_format)
						row+=1
						cnt+=1
					worksheet.write(row,col,0,cell_format)
					row+=1
				ind+=1
						
			except:
				cnt=0
				while cnt<12:
					worksheet.write(row,col,0,cell_format)
					row+=1
					cnt+=1
				worksheet.write(row,col,0,cell_format)
				row+=1



		row+=2

		total_tax=0
		for tax in final_monthly_tax['payed_tax_break_up']:
			total_tax+=tax['value']
			worksheet.write(row,col,tax['value'],cell_format)
			row+=1  

		worksheet.write(row,col,total_tax,cell_format)
		row+=1      

		stop=time.time()
		total_time+=(stop-start)
		#print(stop-start,emp_id)
		
		

	#print("Total time:",total_time)
	workbook.close()

	output.seek(0)

	response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
	response['Content-Disposition'] = "attachment; filename=tds_sheet.xlsx"

	q_upd = DaysGenerateLog.objects.filter(sessionid=session,month=month).update(tdsSheet=monthly_tds_name)
	
	output.close()

	return response


	
def category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids):

	curr_mon=getSalaryMonth(session)

	old_row=row
	old_col=col

	sum_data=[]
	sum_gross_comp=[]
	sum_gross_total=0
	sum_payable_comp=[]
	sum_payabe_total=0
	sum_arrear_total=0
	sum_grand_total=0
	sum_income_tax=0
	sum_cons_ded=[]
	sum_cons_ded_total=0
	sum_var_ded=[]
	sum_var_ded_total=0
	sum_income_tax=0
	sum_net_salary_payable=0

	jump=0

	row+=1
	worksheet.merge_range(row,col,row+2,col,'Sno',merge_format)
	col+=1
	worksheet.merge_range(row,col,row+2,col,'Title',merge_format)
	col+=1
	worksheet.merge_range(row,col,row+2,col,'Name of Employee',merge_format)
	col+=1
	worksheet.merge_range(row,col,row+2,col,'E_Code',merge_format)
	col+=1
	
	worksheet.merge_range(row,col,row+2,col,'Designation',merge_format)
	col+=1
	worksheet.merge_range(row,col,row+2,col,'Department',merge_format)
	col+=1
	worksheet.merge_range(row,col,row+2,col,'Emp. P F No UP/24848/',merge_format)
	
	col+=1
	worksheet.merge_range(row,col,row+2,col,'Bank A/C No.',merge_format)
	col+=1
	worksheet.merge_range(row,col,row,col+3,'No. of days',merge_format)
	worksheet.merge_range(row+1,col,row+2,col,'Working Days',merge_format)
	
	col+=1
	worksheet.merge_range(row+1,col,row+2,col,'Leave',merge_format)
	col+=1
	worksheet.merge_range(row+1,col,row+2,col,'Holidays',merge_format)
	col+=1
	worksheet.merge_range(row+1,col,row+2,col,'Total Days',merge_format)
	col+=1
	
	jump=col

	worksheet.merge_range(row,col,row,col+len(qry_salary_comp),'Gross Salary',merge_format)
	
	for q in qry_salary_comp:
		worksheet.merge_range(row+1,col,row+2,col,q['Ingredients__value'],merge_format)
		col+=1
		sum_gross_comp.append(0)
		sum_payable_comp.append(0)
		
	worksheet.merge_range(row+1,col,row+2,col,'Total',merge_format)
	col+=1
	worksheet.merge_range(row,col,row,col+len(qry_salary_comp)+1,'Salary payable',merge_format)

	for q in qry_salary_comp:
		worksheet.merge_range(row+1,col,row+2,col,q['Ingredients__value'],merge_format)
		col+=1
		
	worksheet.merge_range(row+1,col,row+2,col,'Total',merge_format)
	col+=1
	worksheet.merge_range(row+1,col,row+2,col,'Arrear',merge_format)
	col+=1
	worksheet.merge_range(row,col,row,col,'',merge_format)
	worksheet.merge_range(row+1,col,row+2,col,'Grand Total',merge_format)
	
	col+=1

	ded_len = len(q_const_ded)  
	worksheet.merge_range(row,col,row,col+ded_len+1,'Constant Pay Deductions',merge_format)

	worksheet.merge_range(row+1,col,row+2,col,'Income Tax',merge_format)
	col+=1

	for c in q_const_ded:
		sum_cons_ded.append(0)
		worksheet.merge_range(row+1,col,row+2,col,c['DeductionName__value'],merge_format)
		col+=1

	
	worksheet.merge_range(row+1,col,row+2,col,'Total',merge_format)
	col+=1

	col+=3

	ded_len = len(q_var_ded)
	worksheet.merge_range(row,col,row,col+ded_len,'Variable Pay Deductions',merge_format)
	for v in q_var_ded:
		sum_var_ded.append(0)
		worksheet.merge_range(row+1,col,row+2,col,v['value'],merge_format)
		col+=1

	worksheet.merge_range(row+1,col,row+2,col,'Total',merge_format)
	col+=1

	worksheet.merge_range(row,col,row+2,col,'Net Salary Payable',merge_format)
	col+=1
	
	i=1
	row+=3
	col=0

	sni=0

	for e in q_emps:
		sni+=1
		
		emp_id =e['emp_id']
		worksheet.write(row,col,sni,cell_format2)
		worksheet.write(row,col+1,e['emp_id__title__value'],cell_format3)
		worksheet.write(row,col+2,e['emp_id__name'],cell_format3)
		worksheet.write(row,col+3,e['emp_id'],cell_format2)
		worksheet.write(row,col+4,e['emp_id__desg__value'],cell_format2)
		worksheet.write(row,col+5,e['emp_id__dept__value'],cell_format2)
		worksheet.write(row,col+6,e['uan_no'],cell_format2)
		worksheet.write(row,col+7,e['bank_Acc_no'],cell_format2)

		############# days ############################

		q_days = EmployeePayableDays.objects.filter(emp_id=emp_id,session=session,month=month).values('working_days','leave','holidays','total_days')
					
		if len(q_days)>0:       
			working=q_days[0]['working_days']
			leave=q_days[0]['leave']
			holiday=q_days[0]['holidays']
			actual_days=q_days[0]['total_days']
		else:
			working=0
			leave=0
			holiday=0
			actual_days=0


		working_days=working+leave+holiday

		taxstatus_li=[0,1]
		worksheet.write(row,col+8,working,cell_format2)
		worksheet.write(row,col+9,leave,cell_format2)
		worksheet.write(row,col+10,holiday,cell_format2)
		worksheet.write(row,col+11,working_days,cell_format2)

		if month==curr_mon:
			gross_comp=gross_payable_salary_components(e['emp_id'],working_days,actual_days,session,[0,1],month)
			id_li=[d['Ing_Id'] for d in gross_comp]

			
			############ arrear and income tax #########################

			arrear_value=0
			inc_arrear=0
			day_arrear=0
			da_arrear=0
			s_arrear=0
			arrear_list=[]

			payable_inc_arrear=calculate_increment_days_arrear(emp_id,session,month,calculate_increment_days(emp_id,session,month))

			n=len(payable_inc_arrear['diff_payable'])
			
			for i in range(n):
				inc_arrear+=(int)(payable_inc_arrear['diff_payable'][i]['diff_value'])

			days_arrear=calculate_days_arrear(emp_id,session,month)
			sign=calculate_sign_in_out_arrear(emp_id,session,month)
			additional_arrear=calculate_additional_arrear(emp_id,session)
			
			payable_days_arrear=gross_payable_salary_components(emp_id,days_arrear['working_days'],days_arrear['actual_days'],session,taxstatus_li,month)
			payable_sign_arrear=gross_payable_salary_components(emp_id,sign['working_days'],sign['actual_days'],session,taxstatus_li,month)
			for d in payable_days_arrear:
				day_arrear+=d['payable_value']

			for s in payable_sign_arrear:
				s_arrear+=s['payable_value']

			payable_da_arrear= calculate_da_arrear(emp_id,session,calculate_da_days(emp_id,session))
			da_arrear=payable_da_arrear['difference']

			arrear_value = inc_arrear + day_arrear + da_arrear + additional_arrear['value'] +s_arrear

			########## arrear calculation end ##############################

			income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,gross_comp,month,payable_da_arrear,payable_inc_arrear,payable_days_arrear,additional_arrear['value'],payable_sign_arrear)
			

			############ sub or add other income ##########
			other_income=calculate_other_income(emp_id,session)

			##################################################

			constant_deductions = calculate_constant_deduction(emp_id,session,gross_comp,taxstatus_li,month)
			variable_deductions = calculate_variable_deduction(emp_id,session,month)

			hra_for1=0
			for comp in income_tax_sum_comp:
				if 'HRA' in comp['Ing_value']:
					hra_for1+=comp['value']

			#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)

			income_tax_sum=0
			income_tax_sum_comp_data=[]
			for d in income_tax_sum_comp:
				income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value']})
				income_tax_sum+=d['value']

			hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
			hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

			hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

			loss=calculate_loss_deductions(emp_id,session,gross_comp,constant_deductions)

			qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
			std_ded_amt = int(qry_std_ded[0]['value'])

			final_value = max(0,other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt)
			income_tax=calculate_income_tax(emp_id,session,final_value)
			
			tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
			
			final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)
		
		else:
			gross_comp=stored_gross_payable_salary_components(emp_id,session,month)
			id_li=[d['Ing_Id'] for d in gross_comp]

			arrear_value=0
			arrear_list=[]

			arrear_data=stored_arrear(emp_id,month,session)
			arrear_value=arrear_data['final_value']
			arrear_list=arrear_data['data']

			########## arrear calculation end ##############################

			income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,gross_comp,month,arrear_list[2],arrear_list[4],arrear_list[3],arrear_list[0]['value'],arrear_list[1])
			

			############ sub or add other income ##########
			other_income=calculate_other_income(emp_id,session)

			##################################################

			constant_deductions = calculate_constant_deduction_stored(emp_id,session,gross_comp,taxstatus_li,month)
			variable_deductions = calculate_variable_deduction_stored(emp_id,session,month)

			hra_for1=0
			for comp in income_tax_sum_comp:
				if 'HRA' in comp['Ing_value']:
					hra_for1+=comp['value']

			#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)

			income_tax_sum=0
			income_tax_sum_comp_data=[]
			for d in income_tax_sum_comp:
				income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value']})
				income_tax_sum+=d['value']

			hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
			hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

			hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

			loss=calculate_loss_deductions(emp_id,session,gross_comp,constant_deductions)

			qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
			std_ded_amt = int(qry_std_ded[0]['value'])

			final_value = max(0,other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt)
			income_tax=calculate_income_tax(emp_id,session,final_value)
			
			tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
			
			final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)

			######### end ##################################

		inc = 0
		total = 0
		ni = len(gross_comp)
		cn=0
		for comp in qry_salary_comp:
			if comp['id'] in id_li:
				index = id_li.index(comp['id'])
				total += int(gross_comp[index]['gross_value'])
				worksheet.write(row,col+12+inc,gross_comp[index]['gross_value'],cell_format2)
				sum_gross_comp[cn]+=gross_comp[index]['gross_value']
			else:
				worksheet.write(row,col+12+inc,0,cell_format2)
			inc += 1
			cn+=1
		sum_gross_total+=total
		worksheet.write(row,col+12+inc,total,cell_format2)
		inc+=1
		################# payable ######################################

		cn=0
		total_payable = 0
		for comp in qry_salary_comp:
			if comp['id'] in id_li:
				index = id_li.index(comp['id'])
				total_payable += int(gross_comp[index]['payable_value'])
				worksheet.write(row,col+12+inc,gross_comp[index]['payable_value'],cell_format2)
				sum_payable_comp[cn]+=gross_comp[index]['payable_value']
			else:
				worksheet.write(row,col+12+inc,0,cell_format2)
			inc += 1
			cn+=1
		sum_payabe_total+=total_payable
		worksheet.write(row,col+12+inc,total_payable,cell_format2)
		inc+=1

		sum_arrear_total+=arrear_value
		worksheet.write(row,col+12+inc,arrear_value,cell_format2)
		inc+=1

		grand_total = total_payable + arrear_value
		sum_grand_total+=grand_total
		
		worksheet.write(row,col+12+inc,grand_total,cell_format2)
		inc+=1

		const_ded = constant_deductions
		var_ded = variable_deductions
		cons_ded_total = 0
		var_id_li=[d['v_id'] for d in var_ded['data']]
		const_id_li=[d['id'] for d in const_ded['data']]

		worksheet.write(row,col+12+inc,final_monthly_tax['monthly_tax'],cell_format2)
		inc+=1

		sum_income_tax+=final_monthly_tax['monthly_tax']

		np=len(q_const_ded)
		cn2=0
		for c in q_const_ded:
			if c['id'] in const_id_li:
				index = const_id_li.index(c['id'])
				worksheet.write(row,col+12+inc,const_ded['data'][index]['value'],cell_format2)
				sum_cons_ded[cn2]+=const_ded['data'][index]['value']
				if const_ded['data'][index]['name'] != 'EPF' and const_ded['data'][index]['name'] != 'ESI':
					cons_ded_total+=const_ded['data'][index]['value']

			else:
				worksheet.write(row,col+12+inc,0,cell_format2)
			inc += 1
			cn2+=1

		
		worksheet.write(row,col+12+inc,cons_ded_total,cell_format2)
		inc+=1
		sum_cons_ded_total+=cons_ded_total

		salary_payable = grand_total - const_ded['final_value'] - final_monthly_tax['monthly_tax']
		
		inc+=3

		np=len(q_var_ded)
		cn2=0
		for v in q_var_ded:
			if v['sno'] in var_id_li:
				index = var_id_li.index(v['sno'])
				
				sum_var_ded[cn2]+=var_ded['data'][index]['value']
				worksheet.write(row,col+12+inc,var_ded['data'][index]['value'],cell_format2)
			else:
				worksheet.write(row,col+12+inc,0,cell_format2)
			inc += 1
			cn2+=1
		worksheet.write(row,col+12+inc,var_ded['total_value'],cell_format2)
		inc+=1

		sum_var_ded_total+=var_ded['total_value']

		net_salary_payable = salary_payable - var_ded['total_value']

		sum_net_salary_payable+=net_salary_payable
		worksheet.write(row,col+12+inc,net_salary_payable,cell_format2)
		inc+=1

		row+=1
		i+=1

	for s in sum_gross_comp:
		worksheet.write(row,jump,s,cell_format2)
		jump+=1
	sum_data.extend(sum_gross_comp)
	sum_data.append(sum_gross_total)
	worksheet.write(row,jump,sum_gross_total,cell_format2)
	jump+=1

	sum_data.extend(sum_payable_comp)
	sum_data.append(sum_payabe_total)
	
	for p in sum_payable_comp:
		worksheet.write(row,jump,p,cell_format2)
		jump+=1
	worksheet.write(row,jump,sum_payabe_total,cell_format2)
	jump+=1

	sum_data.append(sum_arrear_total)
	sum_data.append(sum_grand_total)
	sum_data.append(sum_income_tax)
	
	worksheet.write(row,jump,sum_arrear_total,cell_format2)
	jump+=1

	worksheet.write(row,jump,sum_grand_total,cell_format2)
	jump+=1

	worksheet.write(row,jump,sum_income_tax,cell_format2)
	jump+=1

	for c in sum_cons_ded:
		worksheet.write(row,jump,c,cell_format2)
		jump+=1

	sum_data.extend(sum_cons_ded)
	sum_data.append(sum_cons_ded_total)
	
	worksheet.write(row,jump,sum_cons_ded_total,cell_format2)
	jump+=1

	jump+=3

	for v in sum_var_ded:
		worksheet.write(row,jump,v,cell_format2)
		jump+=1

	sum_data.append("")
	sum_data.append("")
	sum_data.append("")
	
	sum_data.extend(sum_var_ded)
	sum_data.append(sum_var_ded_total)
	
	worksheet.write(row,jump,sum_var_ded_total,cell_format2)
	jump+=1

	sum_data.append(sum_net_salary_payable)
	
	worksheet.write(row,jump,sum_net_salary_payable,cell_format2)
	jump+=1


	row+=4

	return (row,col,worksheet,sum_data)

def open_website(url):
   requests.get(url)
   return 1

def generate_excel(request):
	data_values={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				if request.method == 'GET':

					sdate=request.GET['month'].split('/')
					date=datetime(year=int(sdate[1]),month=int(sdate[0]),day=1)
					
					session=getCurrentSession(date)
					if session == -1:
						return JsonResponse(data={'msg':'Accounts Session not found'},status=202)
					
					fr_month=date.month
					salary_month=getSalaryMonth(session)
					
					url=""
					base_url = settings.BASE_URL
					base_url2 = settings.BASE_URL2
					
					q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).values('acc_sal_lock','id')

					if request.GET['type'] == 'salary_sheet':
						q_check = DaysGenerateLog.objects.filter(id=q_check[0]['id']).update(salarySheet=None,tdsSheet=None)

						resp= generate_monthly_excel_sheet(session,fr_month)

						q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).exclude(salarySheet__isnull=True).values('salarySheet')
						
						url=base_url2+q_check[0]['salarySheet']
						# if q_check[0]['acc_sal_lock'] =='N':
						# 	q_check = DaysGenerateLog.objects.filter(id=q_check[0]['id']).update(salarySheet=None,tdsSheet=None)

						# 	resp= generate_monthly_excel_sheet(session,fr_month)

						# 	q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).exclude(salarySheet__isnull=True).values('salarySheet')
							
						# 	url=base_url2+q_check[0]['salarySheet']
						# else:
						# 	q_check = DaysGenerateLog.objects.filter(id=q_check[0]['id']).exclude(salarySheet__isnull=True).values('salarySheet')
						# 	if len(q_check)==0:
						# 		resp= generate_monthly_excel_sheet(session,fr_month)
						# 		q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).exclude(salarySheet__isnull=True).values('salarySheet')
						# 		url=base_url2+q_check[0]['salarySheet']
								
						# 	else:
						# 		url=base_url2+q_check[0]['salarySheet']
					
					elif request.GET['type'] == 'tds':
						q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).update(salarySheet=None,tdsSheet=None)
						resp= generate_tds_sheet(session,fr_month)
						q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).exclude(tdsSheet__isnull=True).values('tdsSheet')
						url=base_url2+q_check[0]['tdsSheet']
						# if q_check[0]['acc_sal_lock'] =='N':
						# 	q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).update(salarySheet=None,tdsSheet=None)
						# 	resp= generate_tds_sheet(session,fr_month)
						# 	q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).exclude(tdsSheet__isnull=True).values('tdsSheet')
						# 	url=base_url2+q_check[0]['tdsSheet']
						# else:
						# 	q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).exclude(tdsSheet__isnull=True).values('tdsSheet')
						# 	if len(q_check)==0:
						# 		resp= generate_tds_sheet(session,fr_month)
						# 		q_check = DaysGenerateLog.objects.filter(sessionid=session,month=fr_month).exclude(tdsSheet__isnull=True).values('tdsSheet')
						# 		url=base_url2+q_check[0]['tdsSheet']
								
						# 	else:
						# 		url=base_url2+q_check[0]['tdsSheet']

					msg="Success"
					status=200
					data_values={'msg':"Processing","url":url}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data=data_values,status=200)

def generate_monthly_excel_sheet(session,month):
	
	output = io.BytesIO()

	current_sal_month = getSalaryMonth(session)
	flag_unlocked_month = False
	if current_sal_month == month:
		flag_unlocked_month = True

	qry_session = AccountsSession.objects.filter(id=session).values('session')
	monthly_sheet_name = "Accounts_excel/"+calendar.month_name[month]+"_"+qry_session[0]['session']+".xlsx"
	workbook = Workbook(settings.FILE_PATH+monthly_sheet_name)
	worksheet = workbook.add_worksheet()

	bold = workbook.add_format({'bold': True})

	row=0
	col=0
	worksheet.set_row(row,40)

	merge_format = workbook.add_format({
	'bold':     True,
	'border':   6,
	'font_size': 9,
	'align':    'center',
	'valign':   'vcenter',
	'font_name':'Arial'
	})

	sum_data=[]
	merge_format.set_border(style=1)
	
	q_ac_d = EmployeePayableDays.objects.filter(session=session,month=month).values('total_days').order_by('-id')[:1]

	cell_format = workbook.add_format({'bold': True,'font_size':12,'font_name':'Arial'})
	cell_format2 = workbook.add_format({'font_size':8,'font_name':'Arial','align':'center','valign':'vcenter'})
	cell_format3 = workbook.add_format({'bold': True,'font_size':8,'font_name':'Arial','align':'center','valign':'vcenter'})
	
	worksheet.write(row,col, 'Salary for the month '+calendar.month_name[month]+" "+qry_session[0]['session'],cell_format)

	worksheet.write(row,11, q_ac_d[0]['total_days'],cell_format)

	row+=2
	worksheet.write(row,col, 'KIET GROUP OF INSTITUTIONS (FACULTY)',cell_format)
	row+=1
	
	qry_salary_comp = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values('Ingredients__value','id')
	qry_salary_comp_ids = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values_list('id',flat=True)
	q_const_ded = ConstantDeduction.objects.filter(session=session).exclude(status="DELETE").values('DeductionName__value','id')
	q_var_ded = AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("value",'sno')

	############# emp_category = 223 (faculty),dept != 575(KSOP) (i.e KIET GROUP OF INSTITUTIONS) ######################
	if flag_unlocked_month:
		em_ex = list(EmployeePrimdetail.objects.filter(Q(dept=575) | Q(desg__value__contains="WARDEN")).values_list('emp_id',flat=True))
		
		q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=223).exclude(emp_id__emp_type=219).exclude(emp_id__in=em_ex).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
	else:
		em_ex = list(EmployeePayableDays.objects.filter(Q(dept=575) | Q(desg__value__contains="WARDEN")).filter(month=month,session=session).values_list('emp_id',flat=True))
		
		q_emps = EmployeePayableDays.objects.filter(emp_category=223).filter(month=month,session=session).exclude(emp_id__in=em_ex).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),emp_id__title__value=F('title__value'),bank_Acc_no=F('bank_acc_no')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','uan_no','pan_no')

	
	(row,col,worksheet,sd)=category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids)
	sum_data.append(sd)
	############# emp_category = 224 (technical staff),dept != 575(KSOP) (i.e KIET GROUP OF INSTITUTIONS) ######################
	row+=1
	worksheet.write(row,col, 'KIET GROUP OF INSTITUTIONS (TECHNICAL STAFF)',cell_format)
	row+=1
	

	if flag_unlocked_month:

		q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=224).exclude(emp_id__emp_type=219).exclude(emp_id__in=em_ex).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
	else:
		q_emps = EmployeePayableDays.objects.filter(emp_category=224).filter(month=month,session=session).exclude(emp_id__in=em_ex).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

	
	(row,col,worksheet,sd)=category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids)

	sum_data.append(sd)
	############# emp_category = 428 (staff),dept != 575(KSOP) (i.e KIET GROUP OF INSTITUTIONS) ######################
	
	row+=1
	worksheet.write(row,col, 'KIET GROUP OF INSTITUTIONS (STAFF)',cell_format)
	row+=1
	
	if flag_unlocked_month:

		q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=428).exclude(emp_id__emp_type=219).exclude(emp_id__in=em_ex).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
	else:
		q_emps = EmployeePayableDays.objects.filter(emp_category=428).filter(month=month,session=session).exclude(emp_id__in=em_ex).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

	(row,col,worksheet,sd)=category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids)
	sum_data.append(sd)
	######################## KSOP ###############################################
	row+=1
	worksheet.write(row,col, 'KIET SCHOOL OF PHARMACY (FACULTY)',cell_format)
	row+=1
	############# emp_category = 223 (faculty),dept = 575(KSOP) ######################
	
	if flag_unlocked_month:

		q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=223,emp_id__dept=575).exclude(emp_id__emp_type=219).exclude(emp_id__desg__value__contains="WARDEN").order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
	else:
		q_emps = EmployeePayableDays.objects.filter(emp_category=223,dept=575).filter(month=month,session=session).exclude(desg__value__contains="WARDEN").order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')


	(row,col,worksheet,sd)=category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids)
	sum_data.append(sd)
	############# emp_category = 224 (technical staff),dept = 575(KSOP)  ######################
	row+=1
	worksheet.write(row,col, 'KIET SCHOOL OF PHARMACY (TECHNICAL STAFF)',cell_format)
	row+=1

	if flag_unlocked_month:

		q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=224,emp_id__dept=575).exclude(emp_id__emp_type=219).exclude(emp_id__desg__value__contains="WARDEN").order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
	else:
		q_emps = EmployeePayableDays.objects.filter(emp_category=224,dept=575).filter(month=month,session=session).exclude(desg__value__contains="WARDEN").order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

	(row,col,worksheet,sd)=category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids)
	sum_data.append(sd)
	############# emp_category = 428 (staff),dept = 575(KSOP) ######################
	row+=1
	worksheet.write(row,col, 'KIET SCHOOL OF PHARMACY (STAFF)',cell_format)
	row+=1

	if flag_unlocked_month:

		q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=428,emp_id__dept=575).exclude(emp_id__emp_type=219).exclude(emp_id__desg__value__contains="WARDEN").order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
	else:
		q_emps = EmployeePayableDays.objects.filter(emp_category=428,dept=575).filter(month=month,session=session).exclude(desg__value__contains="WARDEN").order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

	(row,col,worksheet,sd)=category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids)
	sum_data.append(sd)
	############ warden ########################
	row+=1
	worksheet.write(row,col, 'KIET GROUP OF INSTITUTIONS (WARDEN)',cell_format)
	row+=1

	if flag_unlocked_month:
		
		q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=428,emp_id__desg__value__contains="WARDEN").exclude(emp_id__emp_type=219).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
	else:
		q_emps = EmployeePayableDays.objects.filter(emp_category=428,desg__value__contains="WARDEN").filter(month=month,session=session).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

	(row,col,worksheet,sd)=category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids)
	sum_data.append(sd)

	########### all faculty sum ###########################
	row+=1
	worksheet.write(row,col, 'RECONCILIATION',cell_format)
	row+=4

	q_emps = []
	(row,col,worksheet,sd)=category_sheet(row,col,qry_salary_comp,q_emps,worksheet,q_const_ded,q_var_ded,cell_format,cell_format2,cell_format3,merge_format,session,month,qry_salary_comp_ids)
	sum_data.append(sd)
	emp_type=["KIET FACULTY","KIET TECHNICAL STAFF","KIET STAFF",'KSOP FACULTY','KSOP TECHNICAL STAFF','KSOP STAFF','KIET WARDEN']
	col=0
	row-=4
	col2=col
	in3=0
	sno=1
	final_net_total=[0 for d in sum_data[0]]
	for et,sd in zip(emp_type,sum_data):
		worksheet.write(row,col,sno,cell_format2)
		col+=2
		sno+=1

		worksheet.write(row,col,et,cell_format2)
		col+=10
		in3=0
		for d in sd:
			if d != "":
				final_net_total[in3]+=d
			else:
				final_net_total[in3]=""
			worksheet.write(row,col, d,cell_format2)
			col+=1
			in3+=1
		col=col2
		row+=1
	col+=12
	for f in final_net_total:
		worksheet.write(row,col,f,cell_format3)
		col+=1

	workbook.close()

	output.seek(0)

	response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
	response['Content-Disposition'] = "attachment; filename=monthly_report.xlsx"

	output.close()
	q_upd = DaysGenerateLog.objects.filter(sessionid=session,month=month).update(salarySheet=monthly_sheet_name)
	
	return response


################################### MODIFIED SALARY SHEET ###########################################################################

def modified_category_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids):

	curr_mon=getSalaryMonth(session)

	emp_data=[]
	
	sum_data=[]
	sum_gross_comp=[]
	sum_gross_total=0
	sum_payable_comp=[]
	sum_payabe_total=0
	sum_arrear_total=0
	sum_grand_total=0
	sum_income_tax=0
	sum_cons_ded=[]
	sum_cons_ded_total=0
	sum_var_ded=[]
	sum_var_ded_total=0
	sum_income_tax=0
	sum_net_salary_payable=0

	
	
	i=1
	col=0

	sni=0

	for e in q_emps:
		sni+=1
		final_sheet_array={}
		emp_id=e['emp_id']
		final_sheet_array['E_Code'] =e['emp_id']
		final_sheet_array['Sno'] =sni
		final_sheet_array['Title']=e['emp_id__title__value']
		final_sheet_array['Name_of_Employee']=e['emp_id__name']
		final_sheet_array['Designation']=e['emp_id__desg__value']
		final_sheet_array['Department']=e['emp_id__dept__value']
		final_sheet_array['Emp_PF_No']=e['uan_no']
		final_sheet_array['Bank_AC_No']=e['bank_Acc_no']
		
		############# days ############################

		q_days = EmployeePayableDays.objects.filter(emp_id=emp_id,session=session,month=month).values('working_days','leave','holidays','total_days')
					
		if len(q_days)>0:       
			working=q_days[0]['working_days']
			leave=q_days[0]['leave']
			holiday=q_days[0]['holidays']
			actual_days=q_days[0]['total_days']
		else:
			working=0
			leave=0
			holiday=0
			actual_days=0

		working_days=working+leave+holiday
		final_sheet_array['working_days']=working
		final_sheet_array['leave']=leave
		final_sheet_array['holidays']=holiday
		final_sheet_array['total_days']=working_days
		
		taxstatus_li=[0,1]
		
		
		if month==curr_mon:
			gross_comp=gross_payable_salary_components(e['emp_id'],working_days,actual_days,session,[0,1],month)
			id_li=[d['Ing_Id'] for d in gross_comp]
			
			############ arrear and income tax #########################

			arrear_value=0
			inc_arrear=0
			day_arrear=0
			da_arrear=0
			s_arrear=0
			arrear_list=[]

			payable_inc_arrear=calculate_increment_days_arrear(emp_id,session,month,calculate_increment_days(emp_id,session,month))

			n=len(payable_inc_arrear['diff_payable'])
			
			for i in range(n):
				inc_arrear+=(int)(payable_inc_arrear['diff_payable'][i]['diff_value'])

			days_arrear=calculate_days_arrear(emp_id,session,month)
			sign=calculate_sign_in_out_arrear(emp_id,session,month)
			additional_arrear=calculate_additional_arrear(emp_id,session)
			
			payable_days_arrear=gross_payable_salary_components(emp_id,days_arrear['working_days'],days_arrear['actual_days'],session,taxstatus_li,month)
			payable_sign_arrear=gross_payable_salary_components(emp_id,sign['working_days'],sign['actual_days'],session,taxstatus_li,month)
			for d in payable_days_arrear:
				day_arrear+=d['payable_value']

			for s in payable_sign_arrear:
				s_arrear+=s['payable_value']

			payable_da_arrear= calculate_da_arrear(emp_id,session,calculate_da_days(emp_id,session))
			da_arrear=payable_da_arrear['difference']

			arrear_value = inc_arrear + day_arrear + da_arrear + additional_arrear['value'] +s_arrear

			########## arrear calculation end ##############################

			income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,gross_comp,month,payable_da_arrear,payable_inc_arrear,payable_days_arrear,additional_arrear['value'],payable_sign_arrear)
			

			############ sub or add other income ##########
			other_income=calculate_other_income(emp_id,session)

			##################################################

			constant_deductions = calculate_constant_deduction(emp_id,session,gross_comp,taxstatus_li,month)
			variable_deductions = calculate_variable_deduction(emp_id,session,month)

			hra_for1=0
			for comp in income_tax_sum_comp:
				if 'HRA' in comp['Ing_value']:
					hra_for1+=comp['value']

			#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)

			income_tax_sum=0
			income_tax_sum_comp_data=[]
			for d in income_tax_sum_comp:
				income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value']})
				income_tax_sum+=d['value']

			hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
			hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

			hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

			loss=calculate_loss_deductions(emp_id,session,gross_comp,constant_deductions)

			qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
			std_ded_amt = int(qry_std_ded[0]['value'])

			final_value = max(0,other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt)
			income_tax=calculate_income_tax(emp_id,session,final_value)
			
			tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
			
			final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)
		
		else:
			gross_comp=stored_gross_payable_salary_components(emp_id,session,month)
			id_li=[d['Ing_Id'] for d in gross_comp]

			arrear_value=0
			arrear_list=[]

			arrear_data=stored_arrear(emp_id,month,session)
			arrear_value=arrear_data['final_value']
			arrear_list=arrear_data['data']

			########## arrear calculation end ##############################

			income_tax_sum_comp=calculate_income_tax_sum(emp_id,session,working_days,actual_days,gross_comp,month,arrear_list[2],arrear_list[4],arrear_list[3],arrear_list[0]['value'],arrear_list[1])
			

			############ sub or add other income ##########
			other_income=calculate_other_income(emp_id,session)

			##################################################

			constant_deductions = calculate_constant_deduction_stored(emp_id,session,gross_comp,taxstatus_li,month)
			variable_deductions = calculate_variable_deduction_stored(emp_id,session,month)

			hra_for1=0
			for comp in income_tax_sum_comp:
				if 'HRA' in comp['Ing_value']:
					hra_for1+=comp['value']

			#hra_for1=hra_exemption_formula1(emp_id,session,working_days,actual_days,month)

			income_tax_sum=0
			income_tax_sum_comp_data=[]
			for d in income_tax_sum_comp:
				income_tax_sum_comp_data.append({'value':d['value'],'Ing_value':d['Ing_value']})
				income_tax_sum+=d['value']

			hra_for2=hra_exemption_formula2(emp_id,session,income_tax_sum,hra_for1)
			hra_for3=hra_exemption_formula3(emp_id,session,income_tax_sum,hra_for1)

			hra_exemption=max(min(hra_for1,hra_for2,hra_for3['value']),0)

			loss=calculate_loss_deductions(emp_id,session,gross_comp,constant_deductions)

			qry_std_ded = AccountsDropdown.objects.filter(field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
			std_ded_amt = int(qry_std_ded[0]['value'])

			final_value = max(0,other_income['value']+income_tax_sum- hra_exemption - loss['value'] - std_ded_amt)
			income_tax=calculate_income_tax(emp_id,session,final_value)
			
			tax_after_rebate=calculate_tax_after_rebate(final_value,income_tax,session)
			
			final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)

			######### end ##################################

		total = 0
		ni = len(gross_comp)
		cn=0
		emp_gross_arr=[]
		for comp in qry_salary_comp:
			if comp['id'] in id_li:
				index = id_li.index(comp['id'])
				total += int(gross_comp[index]['gross_value'])
				final_sheet_array['Gross_'+comp['Ingredients__value'].replace(" ","_")]=gross_comp[index]['gross_value']
				emp_gross_arr.append({'id':comp['id'],'name':'Gross_'+comp['Ingredients__value'],'value':gross_comp[index]['gross_value']})
			else:
				emp_gross_arr.append({'id':comp['id'],'name':'Gross_'+comp['Ingredients__value'],'value':0})
				final_sheet_array['Gross_'+comp['Ingredients__value'].replace(" ","_")]=0
				
			cn+=1
		sum_gross_total+=total
		final_sheet_array['emp_gross_arr']=emp_gross_arr
		final_sheet_array['gross_total']=total

		final_sheet_array['variation']=calculate_variation(emp_id,month,total)
		################# payable ######################################

		cn=0
		total_payable = 0
		emp_payable_arr=[]
		for comp in qry_salary_comp:
			if comp['id'] in id_li:
				index = id_li.index(comp['id'])
				total_payable += int(gross_comp[index]['payable_value'])
				final_sheet_array['Payable_'+comp['Ingredients__value'].replace(" ","_")]=gross_comp[index]['payable_value']
				#sum_payable_comp[cn]+=gross_comp[index]['payable_value']
				emp_payable_arr.append({'id':comp['id'],'name':'Payable_'+comp['Ingredients__value'],'value':gross_comp[index]['payable_value']})
			else:
				emp_payable_arr.append({'id':comp['id'],'name':'Payable_'+comp['Ingredients__value'],'value':0})
				final_sheet_array['Payable_'+comp['Ingredients__value'].replace(" ","_")]=0
				
			cn+=1
		sum_payabe_total+=total_payable
		final_sheet_array['emp_payable_arr']=emp_payable_arr
		final_sheet_array['payable_total']=total_payable
		
		sum_arrear_total+=arrear_value
		final_sheet_array['arrear_total']=arrear_value
		
		grand_total = total_payable + arrear_value
		final_sheet_array['grand_total']=grand_total
		sum_grand_total+=grand_total
		
		const_ded = constant_deductions
		var_ded = variable_deductions
		cons_ded_total = 0
		var_id_li=[d['v_id'] for d in var_ded['data']]
		const_id_li=[d['id'] for d in const_ded['data']]

		final_sheet_array['monthly_tax']=final_monthly_tax['monthly_tax']
		
		sum_income_tax+=final_monthly_tax['monthly_tax']

		np=len(q_const_ded)
		cn2=0
		emp_const_ded=[]
		for c in q_const_ded:
			if c['id'] in const_id_li:
				index = const_id_li.index(c['id'])
				final_sheet_array["Const_"+c['DeductionName__value'].replace(" ","_")]=const_ded['data'][index]['value']
				#sum_cons_ded[cn2]+=const_ded['data'][index]['value']
				emp_const_ded.append({'id':c['id'],'name':"Const_"+c['DeductionName__value'],'value':const_ded['data'][index]['value']})
				if const_ded['data'][index]['name'] != 'EPF' and const_ded['data'][index]['name'] != 'ESI':
					cons_ded_total+=const_ded['data'][index]['value']
			else:
				emp_const_ded.append({'id':c['id'],'name':"Const_"+c['DeductionName__value'],'value':0})
				final_sheet_array["Const_"+c['DeductionName__value'].replace(" ","_")]=0
			cn2+=1

		final_sheet_array['emp_const_ded']=emp_const_ded
		final_sheet_array['constant_deductions_total']=cons_ded_total
				
		sum_cons_ded_total+=cons_ded_total

		salary_payable = grand_total - const_ded['final_value'] - final_monthly_tax['monthly_tax']
		
		np=len(q_var_ded)
		cn2=0
		emp_var_ded=[]
		for v in q_var_ded:
			if v['sno'] in var_id_li:
				index = var_id_li.index(v['sno'])
				final_sheet_array["Var_"+v['value'].replace(" ","_")]=var_ded['data'][index]['value']
				emp_var_ded.append({'id':v['sno'],'name':"Var_"+v['value'],'value':var_ded['data'][index]['value'],'is_edit':True})
			else:
				emp_var_ded.append({'id':v['sno'],'name':"Var_"+v['value'],'value':0,'is_edit':False})
				final_sheet_array["Var_"+v['value'].replace(" ","_")]=0
			cn2+=1

		final_sheet_array['emp_var_ded']=emp_var_ded
		final_sheet_array['variable_deductions_total']=var_ded['total_value']
		
		sum_var_ded_total+=var_ded['total_value']

		net_salary_payable = salary_payable - var_ded['total_value']

		sum_net_salary_payable+=net_salary_payable
		final_sheet_array['variable_deductions_total']=var_ded['total_value']
		final_sheet_array['net_salary_payable']=net_salary_payable

		emp_data.append(final_sheet_array)
		
		i+=1

	return emp_data


################################### HR SUMMARY SALARY SHEET ###########################################################################

def modified_salary_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids,year):

	curr_mon=getSalaryMonth(session)

	emp_data=[]
	
	sum_data=[]
	sum_gross_comp=[]
	sum_gross_total=0
	
	i=1
	col=0

	sni=0
	print("q_emps",q_emps)
	for e in q_emps:
		sni+=1
		final_sheet_array={}
		emp_id=e['emp_id']
		final_sheet_array['E_Code'] =e['emp_id']
		final_sheet_array['Sno'] =sni
		final_sheet_array['Title']=e['emp_id__title__value']
		final_sheet_array['Name_of_Employee']=e['emp_id__name']
		final_sheet_array['Designation']=e['emp_id__desg__value']
		final_sheet_array['Department']=e['emp_id__dept__value']
		final_sheet_array['Emp_PF_No']=e['uan_no']
		final_sheet_array['Bank_AC_No']=e['bank_Acc_no']
		
		############# days ############################
		q_days = EmployeePayableDays.objects.filter(emp_id=emp_id,session=session,month=month).values('working_days','leave','holidays','total_days')
		
		fdate=datetime.date(datetime(year, (month)%13, 1))
		tdate=datetime.date(datetime.now())
		print(fdate,tdate,"q_days",q_days)
		if len(q_days)>0:       
			working=q_days[0]['working_days']
			leave=q_days[0]['leave']
			holiday=q_days[0]['holidays']
			actual_days=q_days[0]['total_days']
		else:
			q_days_fallback=calculate_working_days(emp_id,fdate,tdate,e['emp_id__name'],e['emp_id__dept__value'])
			# print(q_days_fallback)
			working=q_days_fallback['present']
			leave=q_days_fallback['leave']
			holiday=q_days_fallback['holiday']
			actual_days=q_days_fallback['total_days']
		# else:
		# 	working=0
		# 	leave=0
		# 	holiday=0
		# 	actual_days=0

		working_days=working+leave+holiday
		final_sheet_array['working_days']=working
		final_sheet_array['leave']=leave
		final_sheet_array['holidays']=holiday
		final_sheet_array['total_days']=working_days
		
		taxstatus_li=[0,1]
		
		
		if month==curr_mon:
			gross_comp=gross_payable_salary_components(e['emp_id'],working_days,actual_days,session,[0,1],month)
			id_li=[d['Ing_Id'] for d in gross_comp]
			
			##################################################

			constant_deductions = calculate_constant_deduction(emp_id,session,gross_comp,taxstatus_li,month)
			variable_deductions = calculate_variable_deduction(emp_id,session,month)

		else:
			gross_comp=stored_gross_payable_salary_components(emp_id,session,month)
			id_li=[d['Ing_Id'] for d in gross_comp]
			######### end ##################################

		total = 0
		ni = len(gross_comp)
		cn=0
		gross_hra=0
		emp_gross_arr=[]
		for comp in qry_salary_comp:
			if comp['id'] in id_li:
				index = id_li.index(comp['id'])
				total += int(gross_comp[index]['gross_value'])
				if(comp['Ingredients__value']=="HRA CONSOLIDATED"  or comp['Ingredients__value']=="HRA GRADE"):
					if(gross_comp[index]['gross_value']>0):
						gross_hra=gross_comp[index]['gross_value']
					continue
				final_sheet_array['Gross_'+comp['Ingredients__value'].replace(" ","_")]=gross_comp[index]['gross_value']
				emp_gross_arr.append({'id':comp['id'],'name':comp['Ingredients__value'],'value':gross_comp[index]['gross_value']})
			
			else:
				if(comp['Ingredients__value']=="HRA CONSOLIDATED"  or comp['Ingredients__value']=="HRA GRADE"):
					continue
				emp_gross_arr.append({'id':comp['id'],'name':comp['Ingredients__value'],'value':0})
				final_sheet_array['Gross_'+comp['Ingredients__value'].replace(" ","_")]=0
		final_sheet_array['Gross_HRA']=gross_hra
		emp_gross_arr.append({'id':"-1",'name':'HRA','value':gross_hra})
		cn+=1

		sum_gross_total+=total
		final_sheet_array['emp_gross_arr']=emp_gross_arr

		final_sheet_array['gross_total']=total
		print(final_sheet_array)
		final_sheet_array['variation']=calculate_variation(emp_id,month,total)

		emp_data.append(final_sheet_array)
		
		i+=1
	return emp_data
################################### END HR SUMMARY SALARY SHEET ###########################################################################

def modified_generate_monthly_excel_sheet(request):
	
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[404])
			if check==200:
				if request.method == 'GET':

					sdate=request.GET['month'].split('/')
					date=datetime(year=int(sdate[1]),month=int(sdate[0]),day=1)
					
					session=getCurrentSession(date)
					if session == -1:
						return JsonResponse(data={'msg':'Accounts Session not found'},status=202)
					
					month=date.month
					current_sal_month = getSalaryMonth(session)
					flag_unlocked_month = False
					if current_sal_month == month:
						flag_unlocked_month = True

					org=request.GET['org']
					if request.GET['dept']!='ALL':
						department=[int(request.GET['dept'])]
					else:
						q_pid = EmployeeDropdown.objects.filter(pid=org,value="DEPARTMENT").exclude(value__isnull=True).values('sno')
						department=EmployeeDropdown.objects.filter(pid=q_pid[0]['sno'],field="DEPARTMENT").exclude(value__isnull=True).values_list('sno',flat=True)

					if request.GET['emp_category']!='ALL':
						employee_category=[int(request.GET['emp_category'])]
					else:
						employee_category=EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).values_list('sno',flat=True)
						
					final_data=[]
					heads=[]

					
					q_ac_d = EmployeePayableDays.objects.filter(session=session,month=month).values('total_days').order_by('-id')[:1]

					if len(q_ac_d)==0:
						return JsonResponse(data={'msg':'Payable days has not been generated for the selected month'},status=202,safe=False)

					month_total_days=q_ac_d[0]['total_days']

					qry_salary_comp = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values('Ingredients__value','id')
					qry_salary_comp_ids = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values_list('id',flat=True)
					q_const_ded = ConstantDeduction.objects.filter(session=session).exclude(status="DELETE").values('DeductionName__value','id')
					q_var_ded = AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("value",'sno')

					
					# heads=['Sno','Title','Name of Employee','E_Code','Designation','Department','Emp. P F No UP/24848/','Bank A/C No.','No of days','Working Days','Leave','Holidays','Total Days']
					
					############# emp_category = 223 (faculty),dept != 575(KSOP) (i.e KIET GROUP OF INSTITUTIONS) ######################
					
					if flag_unlocked_month:
						emp_exc = list(EmployeePrimdetail.objects.filter(Q(dept=575) | Q(desg__value__contains="WARDEN")).values_list('emp_id',flat=True))
					else:
						emp_exc = list(EmployeePayableDays.objects.filter(Q(dept=575) | Q(desg__value__contains="WARDEN")).filter(month=month,session=session).filter(month=month,session=session).values_list('emp_id',flat=True))

					if 223 in employee_category:
						if flag_unlocked_month:
							q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__dept__in=department,emp_id__emp_category=223).exclude(emp_id__emp_type=219).exclude(emp_id__in=emp_exc).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
						else:
							q_emps = EmployeePayableDays.objects.filter(dept__in=department,emp_category=223).filter(month=month,session=session).exclude(emp_id__in=emp_exc).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

						final_data.append({'sheet_name':'KIET GROUP OF INSTITUTIONS (FACULTY)','data':modified_category_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids)})
						
					############# emp_category = 224 (technical staff),dept != 575(KSOP) (i.e KIET GROUP OF INSTITUTIONS) ######################
					if 224 in employee_category:
						if flag_unlocked_month:
							q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=224,emp_id__dept__in=department).exclude(emp_id__emp_type=219).exclude(emp_id__in=emp_exc).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
						else:
							q_emps = EmployeePayableDays.objects.filter(emp_category=224,dept__in=department).filter(month=month,session=session).exclude(emp_id__in=emp_exc).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

						final_data.append({'sheet_name':'KIET GROUP OF INSTITUTIONS (TECHNICAL STAFF)','data':modified_category_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids)})
						
					
					############# emp_category = 428 (staff),dept != 575(KSOP) (i.e KIET GROUP OF INSTITUTIONS) ######################
					if 428 in employee_category:
						if flag_unlocked_month:
							q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=428,emp_id__dept__in=department).exclude(emp_id__emp_type=219).exclude(emp_id__in=emp_exc).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
						else:
							q_emps = EmployeePayableDays.objects.filter(emp_category=428,dept__in=department).filter(month=month,session=session).exclude(emp_id__in=emp_exc).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

						final_data.append({'sheet_name':'KIET GROUP OF INSTITUTIONS (STAFF)','data':modified_category_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids)})
					
					######################## KSOP ###############################################
					
					############# emp_category = 223 (faculty),dept = 575(KSOP) ######################
					if 223 in employee_category and 575 in department:
						if flag_unlocked_month:
							q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=223,emp_id__dept=575).exclude(emp_id__emp_type=219).exclude(emp_id__desg__value__contains="WARDEN").order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
						else:
							q_emps = EmployeePayableDays.objects.filter(emp_category=223,dept=575).filter(month=month,session=session).exclude(desg__value__contains="WARDEN").order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

						final_data.append({'sheet_name':'KIET SCHOOL OF PHARMACY (FACULTY)','data':modified_category_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids)})
						
					############# emp_category = 224 (technical staff),dept = 575(KSOP)  ######################
					if 224 in employee_category and 575 in department:
						if flag_unlocked_month:
							q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=224,emp_id__dept=575).exclude(emp_id__emp_type=219).exclude(emp_id__desg__value__contains="WARDEN").order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
						else:
							q_emps = EmployeePayableDays.objects.filter(emp_category=224,dept=575).filter(month=month,session=session).exclude(desg__value__contains="WARDEN").order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

						final_data.append({'sheet_name':'KIET SCHOOL OF PHARMACY (TECHNICAL STAFF)','data':modified_category_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids)})
						
					############# emp_category = 428 (staff),dept = 575(KSOP) ######################
					if 428 in employee_category and 575 in department:
						if flag_unlocked_month:
							q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=428,emp_id__dept=575).exclude(emp_id__emp_type=219).exclude(emp_id__desg__value__contains="WARDEN").order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
						else:
							q_emps = EmployeePayableDays.objects.filter(emp_category=428,dept=575).filter(month=month,session=session).exclude(desg__value__contains="WARDEN").order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

						final_data.append({'sheet_name':'KIET SCHOOL OF PHARMACY (STAFF)','data':modified_category_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids)})
						
					############ warden ########################
					if 428 in employee_category:
						if flag_unlocked_month:
							q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__emp_category=428,emp_id__desg__value__contains="WARDEN",emp_id__dept__in=department).exclude(emp_id__emp_type=219).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
						else:
							q_emps = EmployeePayableDays.objects.filter(emp_category=428,desg__value__contains="WARDEN",dept__in=department).filter(month=month,session=session).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

						final_data.append({'sheet_name':'KIET GROUP OF INSTITUTIONS (WARDEN)','data':modified_category_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids)})
						
					qry_generate_btn_visible = DaysGenerateLog.objects.filter(sessionid=session,month=month,acc_sal_lock='N').count()
					if qry_generate_btn_visible>0:
						show_btn = True
					else:
						show_btn=False
					return JsonResponse(data={'data':final_data,'show_btn':show_btn},status=200,safe=False)

				elif request.method=='PUT':
					data=json.loads(request.body)

					session=getCurrentSession(None)
					if session == -1:
						return JsonResponse(data={'msg':'Accounts Session not found'},status=202)
					month = getSalaryMonth(session)

					for da in data:
						emp_id=da['emp_id']
						if 'variable_deductions' in da:
							var_ded = da['variable_deductions']
							for var in var_ded:
								if not var['is_edit']:
									continue
								q_id = EmployeeDeductions.objects.filter(Emp_Id=emp_id,session=session,variableDeduction=var['id']).values('id')
								qry_var = EmployeeVariableDeduction.objects.update_or_create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),deduction_id=EmployeeDeductions.objects.get(id=q_id[0]['id']),month=month,session=AccountsSession.objects.get(id=session),defaults={'value':var['value']})

						elif 'income_tax' in da:
							income_tax = da['income_tax']
							q_income_tax = Income_Tax_Paid.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),month=month,session=AccountsSession.objects.get(id=session),defaults={'monthly_tax_paid':income_tax})
					
					q_upd = DaysGenerateLog.objects.filter(sessionid=session,month=month).update(tdsSheet=None,salarySheet=None)


					return JsonResponse(data={'msg':'Succesfully Updated'},status=200,safe=False)
				else:
					return JsonResponse(data={'msg':'Invalid request method'},status=405,safe=False)
			else:
				return JsonResponse(data={'msg':'Not Authorized'},status=403,safe=False)
		else:
			return JsonResponse(data={'msg':'Not authenticated'},status=401,safe=False)
	else:
		return JsonResponse(data={'msg':'Cookie not found'},status=500,safe=False)

#################### on creating new session, shift all old ingredient, deduction settings to new session creating new rows ##########

