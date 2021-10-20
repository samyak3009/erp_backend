
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse,JsonResponse	

from django.shortcuts import render
from django.db.models import Q,Sum,F,Value,CharField
from datetime import date,datetime,time
import json

# Create your views heredvfffdfdfdffdfdf.
from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from StudentMMS.constants_functions import requestType
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod

from musterroll.models import EmployeePerdetail,Roles
from login.models import EmployeePrimdetail,AarDropdown
from Registrar.models import *
from Achievement.models import *

from Achievement.views.achievement_function import *
from login.views import checkpermission,generate_session_table_name

def getComponents(request):
	data =[]
	if checkpermission(request,[rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'get_books_role')):
				data = get_role_books()
			elif(requestType.custom_request_type(request.GET,'get_books_for')):
				data = get_book_for()
			elif(requestType.custom_request_type(request.GET,'get_publisher_type')):
				data = get_publisher_type()
			elif(requestType.custom_request_type(request.GET,'get_local_author')):
				data = get_local_author()
			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
		
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

# def see():
# 	qry = list(AarDropdown.objects.filter(pid=0,value=None).exclude(status="DELETE").values('field', 'sno', 'pid','value'))
# 	for x in qry:
# 		print(x)
# 		print('ppppp')
# 		qry1 = list(AarDropdown.objects.filter(pid=0,field=x['field']).exclude(status="DELETE").values('field', 'sno', 'pid','value'))
# 		for y in qry1:
# 			if y['value'] is not None:
# 				qry2 = AarDropdown.objects.filter(sno=y['sno']).exclude(status="DELETE").update(pid=x['sno'])
# 		print(qry1)
# 	print(len(qry))
# see()


def AchievementDropdowns(request):
	if checkpermission(request,[rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'get_dropdowns')):
				qry = list(AarDropdown.objects.filter(pid=0).exclude(status="DELETE").values('field', 'sno', 'pid','value').distinct())
				for field1 in qry:
					# if field1['value'] is not None:
						# field1['field'] = field1['value'] + '( ' + field1['field'] + ' )'
					qry1 = list(AarDropdown.objects.filter(pid=field1['sno']).exclude(status="DELETE").extra(select={'field': 'field', 'sno': 'sno', 'pid': 'pid'}).values('field', 'sno', 'pid','value').distinct())
					qry.extend(qry1)
				return functions.RESPONSE(qry,statusCodes.STATUS_SUCCESS)                                    
			elif(requestType.custom_request_type(request.GET,'get_subcategory')):
				sno = request.GET['sno']
				name = list(AarDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('field','value'))
				if len(name)>0:
					qry1 = list(AarDropdown.objects.filter(pid=sno).exclude(status="DELETE").exclude(value__isnull=True).values('sno','pid','value','is_delete','is_edit'))
					for x in qry1:
							nam = x['sno']
							qry2 = list(AarDropdown.objects.filter(pid=nam).exclude(status="DELETE").exclude(value__isnull=True).values('sno','pid','value','is_delete','is_edit'))
							x['sub_category'] = list(qry2)
					return functions.RESPONSE(qry1,statusCodes.STATUS_SUCCESS)                    
				else:
					return functions.RESPONSE(statusMessages.MESSAGE_DATA_NOT_FOUND,statusCodes.STATUS_NOT_FOUND)                   
		elif requestMethod.DELETE_REQUEST(request):
			data = json.loads(request.body)
			nam = data['sno']
			y = list(AarDropdown.objects.filter(sno=nam).exclude(status="DELETE").exclude(value__isnull=True).values('sno'))
			if len(y)>0:
				nam2 = y[0]['sno']
				qry3 = AarDropdown.objects.filter(sno=nam2).update(status='DELETE')
				return functions.RESPONSE(statusMessages.MESSAGE_DELETE,statusCodes.STATUS_SUCCESS)                    
			else:
				return functions.RESPONSE(statusMessages.MESSAGE_DATA_NOT_FOUND,statusCodes.STATUS_NOT_FOUND) 
		elif requestMethod.POST_REQUEST(request):
			data = json.loads(request.body)
			if(data['request_type']=='add_category'):
				value = data['value'].upper()
				pid = data['pid']
				field = AarDropdown.objects.filter(sno = pid).exclude(status = "DELETE").values_list('value',flat=True)
				if len(field)>0:
					add = AarDropdown.objects.create(field = field[0], value = value, pid = pid , is_edit=1, is_delete=1,status='INSERT')
					return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)
			elif(data['request_type']=='add_sub_category'):
				field = data['field']
				value = data['value'].upper()
				pid = data['pid']
				add = AarDropdown.objects.create(field = field, value = value, pid = pid , is_edit=1 , is_delete=1 ,status='INSERT')
				return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)
		elif requestMethod.PUT_REQUEST(request):
			body = json.loads(request.body)
			sno = body['sno']
			val = body['value'].upper()

			add = AarDropdown.objects.filter(sno=sno).exclude(status="DELETE").update(value=val, status="UPDATE")
			pid_update = AarDropdown.objects.filter(pid=sno).exclude(status="DELETE").update(field=val)

			return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)


# def AchievementDropdowns(request):
# 	if checkpermission(request,[rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
# 		if requestMethod.GET_REQUEST(request):
# 			if(requestType.custom_request_type(request.GET,'get_dropdowns')):
# 				qry = list(AarDropdown.objects.filter(type='I',pid=0).exclude(value__isnull=False).exclude(status="DELETE").values('sno','pid','field','is_delete','is_edit'))
# 				return functions.RESPONSE(qry,statusCodes.STATUS_SUCCESS)                                    
# 			elif(requestType.custom_request_type(request.GET,'get_subcategory')):
# 				sno = request.GET['sno']
# 				name = list(AarDropdown.objects.filter(sno=sno).exclude(status="DELETE").values_list('field',flat=True))
# 				if len(name)>0:
# 					qry1 = list(AarDropdown.objects.filter(field=name[0]).exclude(status="DELETE").exclude(value__isnull=True).values('sno','pid','value','is_delete','is_edit'))
# 					for x in qry1:
# 						nam = x['sno']
# 						qry2 = list(AarDropdown.objects.filter(pid=nam).exclude(status="DELETE").exclude(value__isnull=True).values('sno','pid','value','is_delete','is_edit'))
# 						x['sub_category'] = list(qry2)
# 					return functions.RESPONSE(qry1,statusCodes.STATUS_SUCCESS)                    
# 				else:
# 					return functions.RESPONSE(statusMessages.MESSAGE_DATA_NOT_FOUND,statusCodes.STATUS_NOT_FOUND)                   
# 		elif requestMethod.DELETE_REQUEST(request):
# 			data = json.loads(request.body)
# 			nam = data['sno']
# 			y = list(AarDropdown.objects.filter(sno=nam).exclude(status="DELETE").exclude(value__isnull=True).values('sno'))
# 			if len(y)>0:
# 				nam2 = y[0]['sno']
# 				qry3 = AarDropdown.objects.filter(sno=nam2).update(status='DELETE')
# 				return functions.RESPONSE(statusMessages.MESSAGE_DELETE,statusCodes.STATUS_SUCCESS)                    
# 			else:
# 				return functions.RESPONSE(statusMessages.MESSAGE_DATA_NOT_FOUND,statusCodes.STATUS_NOT_FOUND) 
# 		elif requestMethod.POST_REQUEST(request):
# 			data = json.loads(request.body)
# 			if(data['request_type']=='add_category'):
# 				field = data['field']
# 				value = data['value'].upper()
# 				add = AarDropdown.objects.create(field = field, value = value, pid = 0 , is_edit=1, is_delete=1,status='INSERT')
# 				return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)
# 			elif(data['request_type']=='add_sub_category'):
# 				field = data['field']
# 				value = data['value'].upper()
# 				pid = data['pid']
# 				add = AarDropdown.objects.create(field = field, value = value, pid = pid , is_edit=1 , is_delete=1 ,status='INSERT')
# 				return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)
# 		elif requestMethod.PUT_REQUEST(request):
# 			body = json.loads(request.body)
# 			sno = body['sno']
# 			val = body['value'].upper()
# 			print(val)
# 			print(sno)
# 			add = AarDropdown.objects.filter(sno=sno).exclude(status="DELETE").update(value=val, status="UPDATE")
# 			return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)
# 		else:
# 			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
# 	else:
# 		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
# 		