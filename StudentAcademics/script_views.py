	# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
# from django.db.models import ArrayAgg
from datetime import datetime,timedelta
from django.utils import timezone
import json
from django.conf import settings
from django.http import HttpResponse,JsonResponse
import time
from dateutil import tz
from dateutil.relativedelta import relativedelta
from PIL import Image,ImageChops,ImageOps
from PIL import ImageFont
from PyPDF2 import PdfFileMerger,PdfFileReader
from PIL import ImageDraw
import yagmail
from django.db.models import Q,Sum,Count,Max,F
from datetime import datetime
import collections

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod

from login.models import EmployeeDropdown,EmployeePrimdetail,AuthUser
from musterroll.models import EmployeePerdetail
from Registrar.models import *
from attendance.models import Attendance2
from .models import *

from login.views import checkpermission,generate_session_table_name,send_mail
from .views import get_organization,get_department,get_hr_filter_emp,get_emp_category,get_employee_time_table



def changeDropdownSession():
	main_details = StudentAcademicsDropdown.objects.filter(session=7,pid=0).exclude(status="DELETE").values().order_by('sno')
	bulk_main_details = (StudentAcademicsDropdown(pid=0,field=x['field'],value=x['value'],is_edit=x['is_edit'],is_delete=x['is_edit'],status=x['status'],session=Semtiming.objects.get(uid=8)) for x in main_details)
	StudentAcademicsDropdown.objects.bulk_create(bulk_main_details)
	sub_details = StudentAcademicsDropdown.objects.filter(session=7).exclude(status="DELETE").exclude(pid=0).values().order_by('pid','sno')
	temp_id_map={}
	temp_add_list=[]
	for x in sub_details:
		if x['pid'] in temp_id_map:
			x['pid']=temp_id_map[x['pid']]
			temp_add_list.append(x)
		else:

			bulk_sub_details = (StudentAcademicsDropdown(pid=x['pid'],field=x['field'],value=x['value'],is_edit=x['is_edit'],is_delete=x['is_edit'],status=x['status'],session=Semtiming.objects.get(uid=8)) for x in temp_add_list)
			StudentAcademicsDropdown.objects.bulk_create(bulk_sub_details)
			temp_add_list=[]
			temp_details=StudentAcademicsDropdown.objects.filter(sno=x['pid']).exclude(status="DELETE").values()
			store_id=StudentAcademicsDropdown.objects.filter(session=8,field=temp_details[0]['field'],value=temp_details[0]['value']).exclude(status="DELETE").values_list('sno',flat=True)
			x['pid']=store_id[0]
			temp_id_map[x['pid']]=store_id[0]
			temp_add_list.append(x)



def getAllEmployee():
	org_details=get_organization()
	dept_details=list([get_department(x['sno']) for x in org_details])
	emp_category=get_emp_category()
	emp_details=[]
	dept_details_all=[]
	for z in dept_details:
		dept_details_all=dept_details_all+[k['sno'] for k in z]
	return get_hr_filter_emp(list([x["sno"] for x in emp_category]),dept_details_all)

def DateDict():
	dateData={}
	current_date = datetime.now()
	weekDay = current_date.weekday()
	for i in range(0, 7):
		dateData[(weekDay-i)%7]=(current_date - timedelta(days=i)).date()
	return dateData

def SendPendingAttendance(request):
	data = datetime.now()
	weekDay = data.weekday()
	showRange=[]
	i=1
	if((weekDay-1)<0):
		previous_date=6-weekDay-1
	elif((weekDay-1)==5):
		previous_date=4
	else:
		previous_date=weekDay-1


	session_name = Semtiming.objects.filter(sem_start__lte=data,sem_end__gte=data).values("session_name")
	if len(session_name)>0:
		dateDict=DateDict()
		session_name=session_name[0]['session_name']
		AcademicsCalendar = generate_session_table_name("AcademicsCalendar_",session_name)
		StuGroupAssign = generate_session_table_name("StuGroupAssign_",session_name)
		StudentAttStatus = generate_session_table_name("StudentAttStatus_",session_name)
		Attendance = generate_session_table_name("Attendance_",session_name)
		all_faculty=getAllEmployee()
		email_data={}
		name_data={}
		temp_array=[]
		for x in all_faculty:
			temp_array.append(x['emp_id'])
		emp_data=list(EmployeePrimdetail.objects.filter(emp_id__in=temp_array).values('email','name','emp_id'))
		for x in emp_data:
			email_data[x['emp_id']]=x['email']
			name_data[x['emp_id']]=x['name']
		for emp_id in temp_array:
			if emp_id != "00007":
				true_count=0
				false_count=0
				temp_time_table = get_employee_time_table(emp_id,session_name)
				if len(temp_time_table)>0:
					mail_body = "<p><b>Dear "+ str(name_data[emp_id]) +",</b><br><br>"+"Seems like following attendance is still pending to be uploaded.</b><br>"+""
					table_body="<table border=0 style='border-collapse:collapse;text-align:center' valign=middle cellpadding=2 cellspacing=1>"
					table_body=table_body+"<thead style='border-bottom:1px solid black;border-top:1px solid black;'><tr>"+"<th>COURSE</th>"+"<th>BRANCH</th>"+"<th>SEM</th>"+"<th>SECTION</th>"+"<th>SUBJECT</th>"+"<th>DATE</th>"+"<th>LECTURE</th>"+"</tr></thead>"

					for day in range(0,len(temp_time_table)):
						# print(day,previous_date)
						if previous_date==day:
							present_status = Attendance2.objects.filter(date=dateDict[day],Emp_Id=emp_id).filter(Q(status='P/A')|Q(status='P/II')|Q(status='P/I')|Q(status='P'))
							if day not in dateDict and len(present_status)<1 :
								continue
							for lecture in range(0,len(temp_time_table[day])):
								subject_name =str(temp_time_table[day][lecture]['subject_id__sub_name'])
								if  "PROJECT" in subject_name or "LAB" in subject_name or  "LAB/LIB" in subject_name or "MENTOR" in subject_name or  "mentor" in subject_name or "extra" in subject_name or "EXTRA" in subject_name or "LIBRARY" in subject_name or "library" in subject_name:
									continue
								main_query=Attendance.objects.filter(status__in=["INSERT","UPDATE"],date=dateDict[day],section_id=temp_time_table[day][lecture]['section'],lecture=temp_time_table[day][lecture]['lec_num']).values()
								# main_query=Attendance.objects.filter(status__in=["INSERT","UPDATE"],date=dateDict[day],section_id=temp_time_table[day][lecture]['section'],subject_id=temp_time_table[day][lecture]['subject_id'],lecture=temp_time_table[day][lecture]['lec_num']).values()
								if len(main_query)>0:
									true_count+=1
								else:
									false_count+=1
									table_body=table_body+"<tr style='border-bottom:1px solid black;'>"+"<td>"+str(temp_time_table[day][lecture]['section__sem_id__dept__course_id__value'])+"</td>"+"<td>"+str(temp_time_table[day][lecture]['section__sem_id__dept__dept__value'])+"</td>"+"<td>"+str(temp_time_table[day][lecture]['section__sem_id__sem'])+"</td>"+"<td>"+str(temp_time_table[day][lecture]['section__section'])+"</td>"+"<td>"+str(temp_time_table[day][lecture]['subject_id__sub_name'])+"("+str(temp_time_table[day][lecture]['subject_id__sub_alpha_code'])+"-"+str(temp_time_table[day][lecture]['subject_id__sub_num_code'])+")"+"</td>"+"<td>"+str(dateDict[day].strftime("%d-%m-%Y"))+"</td>"+"<td>"+str(lecture+1)+"</td>"+"</tr>"
					# return
				if false_count>0:
					table_body=table_body+"</table>"
					mail_body = mail_body+table_body +"<br><br>Kindly mark them before portal gets locked. Ignore if already marked."
					mail_body+="<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br><a href='https://play.google.com/store/apps/details?id=edu.kiet.faculty.faculty_app' target='_blank'><img src='https://play.google.com/intl/en_us/badges/images/badge_new.png'></img></a><br><br><a href='https://tech.kiet.edu/hrms/index.html' target='_blank' style='color:#137aa9;'>View On Web</a><br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this erp@kiet.edu."
					send_mail(email_data[emp_id],'Pending Attendance Alert',[mail_body],[])

		print(true_count,false_count)

		return JsonResponse(data="",status=200,safe=False)
	else:
		return JsonResponse(data="",status=500,safe=False)
