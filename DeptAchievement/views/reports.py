
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
# from items import QuotesItem

# Create your views here.
from django.db.models import Case, When, Value, IntegerField
from login.views import checkpermission, generate_session_table_name
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from StudentMMS.constants_functions import requestType
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from login.models import EmployeePrimdetail,AarDropdown
from DeptAchievement.models import *
from Achievement.models import *
from .dept_ach_functions import *
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
from datetime import date
import itertools
import json
import datetime
import operator
# import validators

def Dept_consolidated_report(request):
	emp_id = request.session['hash1']
	if checkpermission(request,[rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET, 'duration_count')):
				f_date = datetime.datetime.strptime(request.GET['from_date'].split('T')[0], '%Y-%m-%d').date()
				t_date = datetime.datetime.strptime(request.GET['to_date'].split('T')[0], '%Y-%m-%d').date()
				sno = int(request.GET['sno'])
				y=int(request.GET['dur'])
				date_arry = []
				data = []
				while(f_date<t_date):
					date_arry.append(f_date)
					f_date += datetime.timedelta(days=y)
				if date_arry[-1]<t_date:
					date_arry.append(t_date)
				if sno == 1:
					for x in range(0,len(date_arry)-1):
						f = date_arry[x]
						t = date_arry[x+1]
						data1 = guestLectures.objects.filter(date__range=[f,t]).exclude(status="DELETE").values_list().distinct().count()
						data.append([t,data1])
				elif sno == 2:
					for x in range(0,len(date_arry)-1):
						f = date_arry[x]
						t = date_arry[x+1]
						data1 = industrialVisit.objects.filter(date__range=[f,t]).exclude(status="DELETE").values_list().distinct().count()
						data.append([t,data1])
				elif sno == 3:
					for x in range(0,len(date_arry)-1):
						f = date_arry[x]
						t = date_arry[x+1]
						data1 = MouSigned.objects.filter(date__range=[f,t]).exclude(status="DELETE").values_list().distinct().count()
						data.append([t,data1])
				elif sno == 4:
					for x in range(0,len(date_arry)-1):
						f = date_arry[x]
						t = date_arry[x+1]
						data1 = eventsorganized.objects.filter(from_date__range=[f,t]).exclude(status="DELETE").values_list().distinct().count()
						data.append([t,data1])
				elif sno == 5:
					for x in range(0,len(date_arry)-1):
						f = date_arry[x]
						t = date_arry[x+1]
						data1 = Hobbyclub.objects.filter(start_date__range=[f,t]).exclude(status="DELETE").values_list().distinct().count()
						data.append([t,data1])
				elif sno == 6:
					for x in range(0,len(date_arry)-1):
						f = date_arry[x]
						t = date_arry[x+1]
						data1 = SummerWinterSchool.objects.filter(start_date__range=[f,t]).exclude(status="DELETE").values_list().distinct().count()
						data.append([t,data1])
				elif sno == 7:
					for x in range(0,len(date_arry)-1):
						f = date_arry[x]
						t = date_arry[x+1]
						data1 = Achievement.objects.filter(date__range=[f,t],type="STUDENT").exclude(status="DELETE").values_list().distinct().count()
						data.append([t,data1])
				elif sno == 8:
					for x in range(0,len(date_arry)-1):
						f = date_arry[x]
						t = date_arry[x+1]
						data1 = Achievement.objects.filter(date__range=[f,t],type='DEPARTMENT').exclude(status="DELETE").values_list().distinct().count()
						data.append([t,data1])
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
			elif(requestType.custom_request_type(request.GET, 'get_count')):
				data=[]
				form_id=int(request.GET['form_id'])
				key=request.GET['key']
				if form_id==1:
					data = list(guestLectures.objects.filter().exclude(status="DELETE").values_list(key,flat=True).distinct())
				elif form_id==2:
					data = list(industrialVisit.objects.filter().exclude(status="DELETE").values_list(key,flat=True).distinct())
				elif form_id==3:
					data = list(MouSigned.objects.filter().exclude(status="DELETE").values_list(key,flat=True).distinct())
				elif form_id==4:
					data = list(eventsorganized.objects.filter().exclude(status="DELETE").values_list(key,flat=True).distinct())
				elif form_id==5:
					data = list(Hobbyclub.objects.filter().exclude(status="DELETE").values_list(key,flat=True).distinct())
				elif form_id==6:
					data = list(SummerWinterSchool.objects.filter().exclude(status="DELETE").values_list(key,flat=True).distinct())
				elif form_id==7:
					data = list(Achievement.objects.filter(type="STUDENT").exclude(status="DELETE").values_list(key,flat=True).distinct())
				elif form_id==8:
					data = list(Achievement.objects.filter(type="DEPARTMENT").exclude(status="DELETE").values_list(key,flat=True).distinct())
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
		elif(requestMethod.POST_REQUEST(request)):
			data2 = json.loads(request.body.decode("utf-8"))       
			extra_filter=data2['data']
			form_id = int(data2['form_id'])
			key_list = []
			arry = {}
			if form_id == 1:
				for x in extra_filter.keys():
					key = x[:-4]
					if key == "emp_id":
						key = key+"_id"
					key_list.append(key)
					arry[key] = extra_filter[x]
				data=list(guestLectures.objects.filter(**extra_filter).exclude(status="DELETE").values().order_by(*key_list).distinct())
			elif form_id == 2:
				for x in extra_filter.keys():
					key = x[:-4]
					if key == "emp_id":
						key = key + "_id"
					key_list.append(key)
					arry[key] = extra_filter[x]
				data=list(industrialVisit.objects.filter(**extra_filter).exclude(status="DELETE").values().order_by(*key_list).distinct())
			elif form_id == 3: 	
				for x in extra_filter.keys():
					key = x[:-4]
					if key == "emp_id":
						key = key + "_id"
					key_list.append(key)
					arry[key] = extra_filter[x]
				data=list(MouSigned.objects.filter(**extra_filter).exclude(status="DELETE").values().order_by(*key_list).distinct())
			elif form_id == 4: 	
				for x in extra_filter.keys():
					key = x[:-4]
					if key == "emp_id":
						print(key)
						key = key + "_id"
					key_list.append(key)
					arry[key] = extra_filter[x]
				data=list(eventsorganized.objects.filter(**extra_filter).exclude(status="DELETE").values( "emp_id_id","id","category_id","type_id","from_date","to_date","organization_sector_id","incorporation_status_id","title","venue","venue_other","participants","organizers","attended","collaboration","sponsership","description","time_stamp","status","incorporation_status__value","type__value","category__value","organization_sector__value").order_by(*key_list).distinct())
			elif form_id == 5: 	
				for x in extra_filter.keys():
					key = x[:-4]
					if key == "emp_id":
						key = key+"_id"
					key_list.append(key)
					arry[key] = extra_filter[x]
				data=list(Hobbyclub.objects.filter(**extra_filter).exclude(status="DELETE").values("project_title","club_name__value","start_date","end_date","project_incharge__name","project_description","team_size","project_cost","project_outcome").order_by(*key_list).distinct())
				print(data)
			elif form_id == 6: 	
				for x in extra_filter.keys():
					key = x[:-4]
					if key == "emp_id" or key == "resource_person_id":
						key = key+"_id"
					key_list.append(key)
					arry[key] = extra_filter[x]
				data=list(SummerWinterSchool.objects.filter(**extra_filter).exclude(status="DELETE").values().order_by(*key_list).distinct())
			elif form_id == 7:
				for x in extra_filter.keys():
					key = x[:-4]
					if key == "emp_id" or key == "category":
						key = key+"_id"
					key_list.append(key)
					arry[key] = extra_filter[x]

				extra_filter['type'] = "STUDENT"
				data=list(Achievement.objects.filter(**extra_filter).exclude(status="DELETE").values().order_by(*key_list).distinct())
			elif form_id == 8:
				for x in extra_filter.keys():
					key = x[:-4]
					if key == "emp_id" or key == "category":
						key = key+"_id"
					key_list.append(key)
					arry[key] = extra_filter[x]
				extra_filter['type'] = "DEPARTMENT"
				data=list(Achievement.objects.filter(**extra_filter).exclude(status="DELETE").values().order_by(*key_list).distinct())
			data1 = orderbyfun(data,key_list,arry)
			data4 = set_data_begin(data1,arry,key_list)
			return functions.RESPONSE(data4, statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

def orderbyfun(list_data,sortby,arry):
	x = sortby[0]
	data1 = []
	nam = []
	for sno,(name,group) in enumerate(itertools.groupby(list_data,key=lambda order:order[x])):
		data1.append({})
		if isinstance(name, datetime.date):
			nam.append(name.strftime('%Y-%m-%d'))
		else:
			nam.append(name)
		data1[-1][x]=name
		temp=list(group)	
		if(len(sortby)>1):
			data1[-1]['set']=orderbyfun(temp,sortby[1:],arry)
		else:
			data1[-1]["count"]= len(temp)
	for y in arry[x]:
		q=nam.count(y)
		if q == 0:
			data1.append({})
			data1[-1][x]=y		
			if(len(sortby)>1):
				data1[-1]['set']=check_for_zero(sortby[1:],arry)
			else:
				data1[-1]["count"]= 0
	return data1

def check_for_zero(sortby,arry):
	x = sortby[0]
	data1 = []
	for y in arry[x]:
		data1.append({})
		data1[-1][x] = y
		if(len(sortby)>1):
			data1[-1]['set']=check_for_zero(sortby[1:],arry)
		else:
			data1[-1]["count"]= 0
	return data1

def set_data_begin(data1,arry,sortby):
	data2 =[]
	x = sortby[0]
	for dic in data1:
		data2.append({})
		data2[-1][x] = dic[x]
		data2[-1]['count'] = []
		if len(sortby)>1:
			data3 = dic['set']
			for y in range(1,len(sortby)):
				e = sortby[y]
				data2[-1][e] = arry[e].copy()
			data2 = set_data(data3,data2,sortby[1:],arry)
		else:
			data2[-1]['count'].append(dic['count'])
	return data2

def set_data(data3,data2,sortby,arry):
	x = sortby[0]
	for y in arry[x]:
		for dic in data3:
			if isinstance(dic[x], datetime.date):
				dic[x] = str(dic[x])
			if dic[x] == y:
				if len(sortby)>1:
					data4 = dic['set']
					data2 = set_data(data4,data2,sortby[1:],arry)
				else:
					data2[-1]['count'].append(dic['count'])
				break
	return data2
