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
from datetime import date
from datetime import datetime
import calendar
from collections import Counter
from operator import itemgetter

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod

from .models import *
from leave.models import Leaves
from login.models import EmployeePrimdetail
from login.models import EmployeeDropdown,EmployeePrimdetail,AuthUser
from musterroll.models import Reporting,EmployeePerdetail
from attendance.models import Attendance2

from .views import *
from leave.views import calculate_working_days,fun_num_of_leaves
from login.views import checkpermission

def chech_salary_locked(session,month):
	qry_check = DaysGenerateLog.objects.filter(sessionid=session,month=month,acc_sal_lock='Y').count()
	if qry_check == 0:
		return False
	else:
		return True

def emp_deductions_report(request):
	if checkpermission(request,[rolesCheck.ROLE_ACCOUNTS])== statusCodes.STATUS_SUCCESS:
		if requestMethod.GET_REQUEST(request):
			dept_list = request.GET['dept'].split(',')
			emp_category_list = request.GET['emp_category'].split(',')
			salary_type_list = request.GET['salary_type'].split(',')
			const_ded_list = request.GET['constant_deductions'].split(',')
			variable_ded_list = request.GET['variable_deductions'].split(',')
			
			date=(datetime.strptime(request.GET['month'].split('T')[0], '%Y-%m-%d').date()+relativedelta(days=+1))
					

			session=getCurrentSession(date)
			curr_session=getCurrentSession(None)

			if session == -1:
				return JsonResponse(data={'msg':'Accounts Session not found'},status=202)
			month = date.month
			salary_month = getSalaryMonth(session)
			if variable_ded_list[0]=='':
				variable_ded_list=[]

			if const_ded_list[0]=='':
				const_ded_list=[]
			
			const_ded_name_value = AccountsDropdown.objects.filter(sno__in=const_ded_list).values_list('value',flat=True)
			var_ded_name_value = AccountsDropdown.objects.filter(sno__in=variable_ded_list).values_list('value',flat=True)
				
			const_ded_name = AccountsDropdown.objects.filter(value__in=list(const_ded_name_value),session=session).exclude(status='DELETE').values('value','sno')
			var_ded_name = AccountsDropdown.objects.filter(value__in=list(var_ded_name_value),session=session).exclude(status='DELETE').values('value','sno')
				
			sal_type_value = AccountsDropdown.objects.filter(sno__in=salary_type_list).values_list('value',flat=True)
			salary_type_list = list(AccountsDropdown.objects.filter(value__in=list(sal_type_value),session=session).exclude(status='DELETE').values_list('sno',flat=True))

		
			if month != salary_month or session!=curr_session:
						
				if not chech_salary_locked(session,month):
					return functions.RESPONSE(statusMessages.MESSAGE_DATA_NOT_FOUND,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

				qry_emp_list = (EmployeeGross_detail.objects.filter(salary_type__in=salary_type_list,Emp_Id__emp_category__in=emp_category_list,Emp_Id__dept__in=dept_list).exclude(Emp_Id__emp_type=219).filter(session=session).exclude(Status="DELETE").values_list('Emp_Id',flat=True))
				const_summary_data=[]
				var_summary_data=[]
				
				const_data=[]
				var_data=[]

				for const in const_ded_name:
					qry_constant_deductions = MonthlyDeductionValue.objects.filter(Emp_Id__in=qry_emp_list,session=session,month=month).filter(deduction_id__constantDeduction__DeductionName=const['sno']).filter(value__gt=0).annotate(deduction_name=F('deduction_id__constantDeduction__DeductionName__value'),emp_name=F('Emp_Id__name'),desg=F('Emp_Id__desg__value'),dept=F('Emp_Id__dept__value'),emp_category=F('Emp_Id__emp_category__value'),deduction_type=Value('CONSTANT PAY DEDUCTIONS', output_field=CharField())).values('Emp_Id','emp_name','deduction_name','value','desg','dept','emp_category','deduction_type')

					const_summary_data.append({'deduction_name':const['value'],'count':len(qry_constant_deductions)})
					const_data.extend(list(qry_constant_deductions))
				
				for var in var_ded_name:
					qry_variable_deductions = MonthlyDeductionValue.objects.filter(Emp_Id__in=qry_emp_list,session=session,month=month).filter(deduction_id__variableDeduction=var['sno']).filter(value__gt=0).annotate(deduction_name=F('deduction_id__variableDeduction__value'),emp_name=F('Emp_Id__name'),desg=F('Emp_Id__desg__value'),dept=F('Emp_Id__dept__value'),emp_category=F('Emp_Id__emp_category__value'),deduction_type=Value('VARIABLE PAY DEDUCTIONS', output_field=CharField())).values('Emp_Id','emp_name','deduction_name','value','desg','dept','emp_category','deduction_type')

					var_summary_data.append({'deduction_name':var['value'],'count':len(qry_variable_deductions)})
					var_data.extend(list(qry_variable_deductions))
				
				data=const_data
				data.extend(var_data)

			else:
				const_summary_data=[]
				cons_ded=[]
				var_summary_data=[]
				var_ded=[]
				const_data=[]
				var_data=[]
				
				taxstatus_li = [0,1]

				qry_emp_list = list(EmployeeGross_detail.objects.filter(salary_type__in=salary_type_list,Emp_Id__emp_category__in=emp_category_list,Emp_Id__dept__in=dept_list).exclude(Emp_Id__emp_type=219).filter(session=session).exclude(Status="DELETE").values_list('Emp_Id',flat=True))

				################ CONSTANT PAY DEDUCTIONS ########################

				constant_deductions_emp = EmployeeDeductions.objects.filter(constantDeduction__DeductionName__in=const_ded_list,session=session,Emp_Id__in=qry_emp_list).exclude(status='DELETE').annotate(desg=F('Emp_Id__desg__value'),dept=F('Emp_Id__dept__value'),emp_category=F('Emp_Id__emp_category__value'),emp_name=F('Emp_Id__name')).values('Emp_Id','emp_name','dept','desg','emp_category').distinct()
				for emp in constant_deductions_emp:
					emp_days =EmployeePayableDays.objects.filter(emp_id=emp['Emp_Id'],session=session,month=month).values('working_days','leave','holidays','total_days')
					
					if len(emp_days)>0:
						working=emp_days[0]['working_days']
						leave=emp_days[0]['leave']
						holiday=emp_days[0]['holidays']
						actual_days=emp_days[0]['total_days']

						########################## CALCULATE NET WORKING DAYS ###############
						working_days=working+leave+holiday
					else:
						actual_days=0
						working_days=0
					payable=gross_payable_salary_components(emp['Emp_Id'],working_days,actual_days,session,taxstatus_li,month)

					emp_const_ded = calculate_constant_deduction(emp['Emp_Id'],session,payable,taxstatus_li,month)
					
					for const in emp_const_ded['data']:
						if const['value'] > 0 and str(const['ded_dropdown_id']) in const_ded_list:
							const_data.append({'Emp_Id':emp['Emp_Id'],'emp_name':emp['emp_name'],'dept':emp['dept'],'desg':emp['desg'],'emp_category':emp['emp_category'],'deduction_type':'CONSTANT PAY DEDUCTIONS','deduction_name':const['name'],'value':const['value']})
							cons_ded.append(const['name'])
				count_data = Counter(cons_ded)

				for key,value in count_data.items():
					const_summary_data.append({'deduction_name':key,'count':value})

				for const in const_ded_name:
					if const['value'] not in cons_ded:
						const_summary_data.append({'deduction_name':const['value'],'count':0})

				################ VARIABLE PAY DEDUCTIONS #############################

				variable_deductions_emp = EmployeeDeductions.objects.filter(variableDeduction__in=variable_ded_list,session=session,Emp_Id__in=qry_emp_list).exclude(status='DELETE').annotate(desg=F('Emp_Id__desg__value'),dept=F('Emp_Id__dept__value'),emp_category=F('Emp_Id__emp_category__value'),emp_name=F('Emp_Id__name')).values('Emp_Id','emp_name','dept','desg','emp_category').distinct()
				for emp in variable_deductions_emp:
					emp_var_ded = calculate_variable_deduction(emp['Emp_Id'],session,month)
					
					for var in emp_var_ded['data']:
						if var['value'] > 0 and str(var['v_id']) in variable_ded_list:
							var_data.append({'Emp_Id':emp['Emp_Id'],'emp_name':emp['emp_name'],'dept':emp['dept'],'desg':emp['desg'],'emp_category':emp['emp_category'],'deduction_type':'VARIABLE PAY DEDUCTIONS','deduction_name':var['v_name'],'value':var['value']})
							var_ded.append(var['v_name'])
				count_data = Counter(var_ded)

				for key,value in count_data.items():
					var_summary_data.append({'deduction_name':key,'count':value})

				for var in var_ded_name:
					if var['value'] not in var_ded:
						var_summary_data.append({'deduction_name':var['value'],'count':0})
					
				data=const_data
				data.extend(var_data)	
						
			return functions.RESPONSE({'const_summary_data':const_summary_data,'var_summary_data':var_summary_data,'data':data},statusCodes.STATUS_SUCCESS)
		
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)


def emp_salary_report(request):
	if checkpermission(request,[rolesCheck.ROLE_ACCOUNTS, rolesCheck.ROLE_HR, rolesCheck.ROLE_HR_REPORTS])== statusCodes.STATUS_SUCCESS:
		if request.method == 'GET':
			sdate=request.GET['month'].split('/')
			date=datetime(year=int(sdate[1]),month=int(sdate[0]),day=1)
			
			session=getCurrentSession(date)
			if session == -1:
				return JsonResponse(data={'msg':'Accounts Session not found'},status=202)
			
			year=date.year
			next_year=date.year
			month=date.month
			if(month == 12):
				next_year=year+1
			current_sal_month = getSalaryMonth(session)
			flag_unlocked_month = False
			print(current_sal_month == month ,current_sal_month ,month)
			if current_sal_month <= month:
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
				month_total_days=(datetime(next_year, (month+1)%13, 1) - datetime(year, month%13, 1)).days
				# return JsonResponse(data={'msg':'Payable days has not been generated for the selected month'},status=202,safe=False)
			else:
				month_total_days=q_ac_d[0]['total_days']
			qry_salary_comp = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values('Ingredients__value','id')
			qry_salary_comp_ids = SalaryIngredient.objects.filter(session=session).exclude(status="DELETE").values_list('id',flat=True)
			q_const_ded = ConstantDeduction.objects.filter(session=session).exclude(status="DELETE").values('DeductionName__value','id')
			q_var_ded = AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS",session=session).exclude(value__isnull=True).exclude(status="DELETE").values("value",'sno')

			
			# heads=['Sno','Title','Name of Employee','E_Code','Designation','Department','Emp. P F No UP/24848/','Bank A/C No.','No of days','Working Days','Leave','Holidays','Total Days']
			
			############# emp_category = 223 (faculty),dept != 575(KSOP) (i.e KIET GROUP OF INSTITUTIONS) ######################
			
			# if flag_unlocked_month:
			# 	emp_exc = list(EmployeePrimdetail.objects.filter(Q(dept=575) | Q(desg__value__contains="WARDEN")).values_list('emp_id',flat=True))
			# else:
			# 	emp_exc = list(EmployeePayableDays.objects.filter(Q(dept=575) | Q(desg__value__contains="WARDEN")).filter(month=month,session=session).filter(month=month,session=session).values_list('emp_id',flat=True))

			if flag_unlocked_month:
				q_emps = EmployeePerdetail.objects.filter(emp_id__emp_status="ACTIVE",emp_id__dept__in=department,emp_id__emp_category__in=employee_category).order_by('emp_id__name').values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')
			else:
				q_emps = EmployeePayableDays.objects.filter(dept__in=department,emp_category__in=employee_category).filter(month=month,session=session).order_by('emp_id__name').annotate(emp_id__desg__value=F('desg__value'),emp_id__dept__value=F('dept__value'),bank_Acc_no=F('bank_acc_no'),emp_id__title__value=F('title__value')).values('emp_id__name','emp_id','emp_id__desg__value','emp_id__dept__value','emp_id__title__value','bank_Acc_no','pan_no','uan_no')

			final_data.append({'sheet_name':'KIET GROUP OF INSTITUTIONS','data':modified_salary_sheet(qry_salary_comp,q_emps,q_const_ded,q_var_ded,session,month,qry_salary_comp_ids,year)})
			print("snkmdkm")
			return JsonResponse(data={'data':final_data},status=statusCodes.STATUS_SUCCESS,safe=False)
		else:
			return JsonResponse(data=statusMessages.MESSAGE_BAD_REQUEST,status=statusCodes.STATUS_BAD_REQUEST,safe=False)
	else:
		return JsonResponse(data=statusMessages.MESSAGE_SERVICE_UNAVAILABLE,status=statusCodes.STATUS_BAD_GATEWAY,safe=False)