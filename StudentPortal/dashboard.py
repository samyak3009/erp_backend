from __future__ import unicode_literals
from django.shortcuts import render
from datetime import date
from django.utils import timezone
import json
import datetime
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from Registrar.views import StudentPerDetail,studentSession_1920o,StudentPrimDetail
from erp.constants_functions import functions,requestMethod
from erp.constants_variables import statusCodes,statusMessages
from login.views import checkpermission,generate_session_table_name
from django.db.models.query_utils import Q

def get_birthday(request):
	if requestMethod.GET_REQUEST(request):
		if(request.GET['request_type']=='get_birthdays'):
			session_name=request.session['Session_name']
			studentSession = generate_session_table_name('studentSession_',session_name)
			d = date.today()
			date_str = d.strftime('%Y-%m-%d')
			birth_date = date_str[4:]
			uniq_list = StudentPerDetail.objects.filter(dob__contains=birth_date).exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL"))).values_list('uniq_id',flat=True)
			qr = list(studentSession.objects.filter(uniq_id__in = uniq_list).values('uniq_id__name','uniq_id__lib','year','sem__dept__course__value','sem__dept__dept__value'))
			data = {'data':qr}
			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST,statusCodes.STATUS_BAD_REQUEST)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)