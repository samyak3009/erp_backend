from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.core import serializers
from login.views import checkpermission, generate_session_table_name
from StudentAcademics.models.models import StudentAcademicsDropdown
from StudentMMS.constants_functions import requestType,Checks
from StudentMMS.views.mms_function_views import get_survey_dropdown_external,get_po,get_survey_dropdown
from StudentAcademics.views import get_coordinator_course,get_course,get_filtered_course
from StudentFeedback.views.feedback_function_views import check_islocked_faculty
import json
import csv
import base64
import datetime
from json.decoder import JSONDecoder
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.models.models_1920e import *
from StudentMMS.models.models_2021o import *
from Registrar.models import *
import math

from itertools import groupby

def create_form(request):   
	data=""
	status = 402
	# print(request.GET)
	if 'hash_code' in request.GET:
		# print("hello")		
		session = request.GET['session']
		hash_code = request.GET['hash_code']
		qry_hash = list(ExternalSurveySession.objects.filter(hash_code=hash_code).values('id','expiry_date','form_status'))
		# print(qry_hash)
		if len(qry_hash)>0:
			date = datetime.datetime.now()
			if qry_hash[0]['form_status'] == 0:
				if qry_hash[0]['expiry_date'] > date:
					data=""
				else:
					data={}
					data['msg'] = "form expired kindly contact to the admin."
					return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
			else:
				data={}
				data['msg'] = "Your response has already been submitted."
				return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
	else:
		# print("rararraraar")
		# print(dict(request.session))
		emp_id = request.session['hash1']
		session = request.session['Session_id']
		session_name=request.session['Session_name']

	if(requestMethod.POST_REQUEST(request)):
		if academicCoordCheck.isNBACoordinator(request):
			data = json.loads(request.body)
			qry_survey = list(ExternalSurvey.objects.filter(survey_id = data['survey_id'],batch_from=data['batch_from'],batch_to=data['batch_to'],dept=data['dept'],session=session).exclude(status='DELETE').values('id'))
			if len(qry_survey)>0:
				qry_del = ExternalSurvey.objects.filter(survey_id=data['survey_id'],batch_from=data['batch_from'],batch_to=data['batch_to'],dept=data['dept'],session=session).update(status='DELETE')
			survey_id = ExternalSurvey.objects.create(survey_id = StudentAcademicsDropdown.objects.get(sno=data['survey_id']),batch_from = data['batch_from'],batch_to = data['batch_to'],dept=CourseDetail.objects.get(uid=data['dept']),session=Semtiming.objects.get(uid=session),created_by = EmployeePrimdetail.objects.get(emp_id=emp_id))
			qr_object = (ExternalSurveyAttr(form_id=ExternalSurvey.objects.get(id=survey_id.id),element_type=k,element_id=att['element_id'],attribute=att,po_id=json.dumps(att['po_id']))for k,v in data['elements'].items() for att in v)
			qr_create = ExternalSurveyAttr.objects.bulk_create(qr_object)
			data = statusMessages.MESSAGE_INSERT
			status = statusCodes.STATUS_SUCCESS
		else:
			data = statusMessages.MESSAGE_FORBIDDEN
			status = statusCodes.STATUS_FORBIDDEN
	elif(requestMethod.GET_REQUEST(request)):
		print("sasasasa")
		if(requestType.custom_request_type(request.GET, 'get_form_data')):
			if 'session' in request.GET:
				session = request.GET['session']
			survey_id = request.GET['survey_id']
			dept = request.GET['dept']
			batch_from = request.GET['batch_from']
			batch_to = request.GET['batch_to']
			data = get_survey_forms(dept,session,survey_id,batch_from,batch_to);
			if len(data)==0:
				data={}
				data['survey_id'] = survey_id
				data['batch_from'] = batch_from
				data['batch_to'] = batch_to
				data['dept'] = dept
				data['elements'] = {'form':[]}
			status = statusCodes.STATUS_SUCCESS
		elif(requestType.custom_request_type(request.GET,'get_po')):
			dept=request.GET['dept']
			data = get_po(dept,session_name)
			status = statusCodes.STATUS_SUCCESS
		elif(requestType.custom_request_type(request.GET,'get_survey')):
			data = get_survey_dropdown_external(session)
			status = statusCodes.STATUS_SUCCESS
		elif(requestType.custom_request_type(request.GET,'get_filled_survey')):
			dept = request.GET['dept']
			batch_from = request.GET['batch_from']
			batch_to = request.GET['batch_to']
			data = list(ExternalSurvey.objects.filter(session=session,batch_from= batch_from,batch_to=batch_to,dept=dept).exclude(status='DELETE').values('survey_id','survey_id__field','survey_id__value').distinct())
			for x in data:
				x['session']=session
			status = statusCodes.STATUS_SUCCESS
		elif(requestType.custom_request_type(request.GET,'get_all_survey')):
			dept_value = request.session['dept']
			data = list(ExternalSurvey.objects.filter(dept__dept_id__value = dept_value).exclude(status='DELETE').values('id','survey_id','survey_id__value','survey_id__field','batch_from','batch_to','dept','dept__dept_id__value','session__session_name','session','created_by','created_by__name').distinct())
			status = statusCodes.STATUS_SUCCESS
		elif(requestType.custom_request_type(request.GET,'get_status_of_survey')):
			dept = request.GET['dept']
			batch_from = request.GET['batch_from']
			batch_to = request.GET['batch_to']
			survey_id = request.GET['survey_id']
			if 'session' in request.GET:
				session = request.GET['session']
			data1 = ExternalSurvey.objects.filter(session=session,batch_from=batch_from,dept=dept,batch_to=batch_to,survey_id=survey_id).exclude(status='DELETE').values_list('id',flat=True)
			if int(session) != int(request.session['Session_id']):
				data = {'editable': False , 'status':'cannot edit this form of another session'}
			elif len(data1)>0:
				data2 = ExternalSurveyAnsDetail.objects.filter(form_id=data1[0]).exclude(status='DELETE').count()
				print(data1)
				if data2>0:
					data = {'editable':False , 'status':'cannot edit this form as form is already filled'}
				else:
					data = {'editable':True}
			else:
				data = {'editable':True}
			status = statusCodes.STATUS_SUCCESS
	elif(requestMethod.PUT_REQUEST(request)):
		data = json.loads(request.body)
		att_list = data['att_list']
		qr1=ExternalSurvey.objects.filter(created_by = emp_id, session = session).values_list('id',flat=True)
		if(len(qr1)>0):
			qr2 = ExternalSurvey.objects.filter(id = qr1[0]).update(status='DELETE')
		temp_data = {}
		for att in att_list:
			temp=[]
			for key,value in att.items():
				if key == 'options':
					for opt in value:
						temp.append({'key':key,'value':opt})
				else:
					temp.append({'key':key,'value':value})
			temp_data[att['element_id']]=temp
		survey_id = ExternalSurvey.objects.create(survey_id = StudentAcademicsDropdown.objects.get(sno=data['survey_id']),batch_from = data['batch_from'],batch_to = data['batch_to'],created_by = EmployeePrimdetail.objects.get(emp_id=emp_id),session = Semtiming.objects.get(uid=session))
		qry_object=(ExternalSurveyAttr(form_id = ExternalSurvey.objects.get(id=survey_id.id), element_id = att, attribute = k['key'], value = k['value'])for att,val in temp_data.items() for k in val)
		qry_create=ExternalSurveyAttr.objects.bulk_create(qry_object)
		data = statusMessages.MESSAGE_INSERT
		status = statusCodes.STATUS_SUCCESS
	elif(requestMethod.DELETE_REQUEST(request)):
		if academicCoordCheck.isNBACoordinator(request):
			data = json.loads(request.body)
			empy_id = request.session['hash1']
			# print(empy_id)
			# print(data[0]['id'])
			qry = ExternalSurvey.objects.filter(id=data[0]['id'],created_by=empy_id).exclude(status='DELETE').update(status='DELETE')
			# print(qry)
			if qry == 0:
				data = {'msg':"You cannot delete other's form"}
				status = 202
			else:
				data = statusMessages.MESSAGE_DELETE
				status = statusCodes.STATUS_SUCCESS
		else:
			data = statusMessages.MESSAGE_FORBIDDEN
			status = statusCodes.STATUS_FORBIDDEN

	else:
		data = statusMessages.MESSAGE_METHOD_NOT_ALLOWED
		status =  statusCodes.STATUS_METHOD_NOT_ALLOWED
	# else:
		# data = statusMessages.MESSAGE_FORBIDDEN
		# status = statusCodes.STATUS_FORBIDDEN
	return functions.RESPONSE(data,status)

def get_survey_forms(dept,session,survey_id,batch_from,batch_to):
	qr1 = list(ExternalSurvey.objects.filter(survey_id=survey_id ,batch_from =batch_from, batch_to= batch_to, dept = dept, session = session).exclude(status='DELETE').values('id','survey_id','batch_to','batch_from','dept_id','session','survey_id__value'))
	print(qr1)
	if(len(qr1)>0):
		qr2 = list(ExternalSurveyAttr.objects.filter(form_id=qr1[0]['id']).values('element_id','attribute','element_type').order_by('element_type','element_id'))
		print(qr2)
		att_list = {}
		for k,v in groupby(qr2,key=lambda x:x['element_type']):
			att_list[k] = []
			for i,j in groupby(list(v),key=lambda y:y['element_id']):
				l=list(j)
				if len(l)>0:
					att_list[k].append(l[0]['attribute'])
		data={'dept':qr1[0]['dept_id'],'batch_from':qr1[0]['batch_from'],'batch_to':qr1[0]['batch_to'],'form_id':qr1[0]['id'],'survey_id':survey_id,'elements':att_list,'survey':qr1[0]['survey_id__value']}
	else:
		data=[]
	return data

def submit_answer(request):
	print("samyak")
	if(requestMethod.POST_REQUEST(request)):
		print("in submit")
		data = json.loads(request.body)
		for x,y in data['elements'].items():
			for z in y:
				if((z['answer']==None and z['answer'] == "") and z['mand']==True):
					data = {'msg':'Mandatory Answer Should not be Empty'}
					status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
					return functions.RESPONSE(data,status)
				if(z['answer']!=None and z['answer']!=""):					
					if(z['category']=='text' and (z['len_check']!=None and z['len_check']!="")):
						if(not(Checks.length_check(z['len_check'],len(z['answer'])))):
							data = {'msg':'Text filled length Should match to the length define'}
							status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
							return functions.RESPONSE(data,status)
					elif(z['category']=='number'):
						if(z['po_id']!=None):
							if(len(z['po_id'])>0 and (z['max']==None or z['max']=="")):
								data = {'msg':'number filled connected with PO must be define with the maximum length'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
						if(z['len_check']!=None and z['len_check']!=""):
							if(not(Checks.length_check(z['len_check'],len(str(z['answer']))))):
								data = {'msg':'length of the number filled must match with the length define'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
						if(z['min']!=None or z['max']!=None):
							maxvalue = z['max'] 
							if(z['min']==None or z['min']==""):
								z['min']=0
							if(z['max']==None or z['max']==""):
								maxvalue= math.inf
							if(not(Checks.min_max_value_check(z['min'],maxvalue,z['answer']))):
								data = {'msg':'number filled must be in range of minimum and maximum define value'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
					elif(z['category']=='slider'):
						if(z['po_id']!=None):
							if(len(z['po_id'])>0 and (z['max']==None or z['max']=="")):
								data = {'msg':'slider value connected with po must have maximum value defined'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
						if(z['min']!=None or z['max']!=None):
							maxvalue = z['max']
							if(z['min']==None or z['min']==""):
								z['min']=0
							elif(z['max']==None or z['max']==""):
								maxvalue=math.inf
							if(not(Checks.min_max_value_check(z['min'],maxvalue,z['answer']))):
								data = {'msg':'slider value filled must be in range of minimum and maximum value'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
					elif(z['category']=='textarea' and z['max_words']!=None and z['max_words']!=""):
						if(not(Checks.min_words_in_paragraph(z['max_words'],z['answer']))):
							data = {'msg':'the no of words in paragraph Should match with the the length defined'}
							status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
							return functions.RESPONSE(data,status)
					elif(z['category']=='email'):
						if(not(Checks.email_check(z['answer']))):
							data = {'msg':'invalid email'}
							status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
							return functions.RESPONSE(data,status)
					elif(z['category']=='date' and z['start']!=None and z['end']!=None):
						if(not(Checks.min_max_date(z['start'],z['end'],z['answer']))):
							data = {'msg':'the date range mismatch with the start and end date defined'}
							status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
							return functions.RESPONSE(data,status)
				qry_id = ExternalSurveyAttr.objects.filter(form_id=data['form_id'],form_id__dept=data['dept'],form_id__survey_id=data['survey_id'],element_id = z['element_id'],element_type = x).exclude(form_id__status='DELETE').values_list('id',flat=True)
				z['ques_id'] = qry_id[0]
		emp = 'hash_code'
		if(emp in data):
			key = None
		else:
			emp_id = request.session['hash1']
			key = EmployeePrimdetail.objects.get(emp_id=emp_id)
		# print("indirect")
		qry_create = ExternalSurveyAnsDetail.objects.create(form_id=ExternalSurvey.objects.get(id=data['form_id']),added_by=key)
		qry_obj = (ExternalSurveyAnswer(ans_id=ExternalSurveyAnsDetail.objects.get(id=qry_create.id),ans_attribute=z,ques_id=ExternalSurveyAttr.objects.get(id=z['ques_id']))for k,t in data['elements'].items() for z in t)
		qr_create = ExternalSurveyAnswer.objects.bulk_create(qry_obj)
		# print(key,'key')
		if key==None:
			# print("sub")
			qry_hash = ExternalSurveySession.objects.filter(hash_code=data['hash_code']).update(form_status=1)
		data = statusMessages.MESSAGE_FILLED
		status = statusCodes.STATUS_SUCCESS
	else:
		data = statusMessages.MESSAGE_FORBIDDEN
		status = statusCodes.STATUS_FORBIDDEN
	return functions.RESPONSE(data,status)

def get_form_filled_data(request):
	if academicCoordCheck.isNBACoordinator(request):
		emp_id = request.session['hash1']
		session = request.session['Session_id']
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET, 'get_answers')):
				dept = request.GET['dept']
				survey_id = request.GET['survey_id']
				batch_from = request.GET['batch_from']
				batch_to = request.GET['batch_to']
				data = get_data_session_wise(dept,survey_id,batch_from,batch_to,session)
				status = statusCodes.STATUS_SUCCESS
			else:
				data = statusMessages.MESSAGE_DATA_NOT_FOUND
				status = statusCodes.STATUS_NOT_FOUND
		elif(requestMethod.DELETE_REQUEST(request)):
			data = json.loads(request.body)
			print(data)
			qry = ExternalSurveyAnsDetail.objects.filter(id=data['ans_id']).exclude(status='DELETE').update(status='DELETE')
			data = statusMessages.MESSAGE_DELETE
			status = statusCodes.STATUS_SUCCESS
		else:
			data = statusMessages.MESSAGE_DATA_NOT_FOUND
			status =  statusCodes.STATUS_NOT_FOUND
	else:
		data = statusMessages.MESSAGE_FORBIDDEN
		status = statusCodes.STATUS_FORBIDDEN
	return functions.RESPONSE(data,status)


def get_data_session_wise(dept,survey_id,batch_from,batch_to,session):
	qry1 = list(ExternalSurvey.objects.filter(survey_id=survey_id,dept=dept,session=session,batch_from=batch_from,batch_to=batch_to).exclude(status='DELETE').values())
	if(len(qry1)>0):
		qry = list(ExternalSurveyAnswer.objects.filter(ques_id__form_id=qry1[0]['id']).exclude(ans_id__status='DELETE').values('ans_id','ans_attribute','ques_id').order_by('ans_id','ques_id'))
		att_list = {}
		for k,v in groupby(qry,key=lambda x:x['ans_id']):
			att_list[k]=[]
			for i,j in groupby(list(v),key=lambda y:y['ques_id']):
				r = list(j)
				if(len(r)>0):
					att_list[k].append(r[0]['ans_attribute'])
		data = {'dept':dept,'survey_id':survey_id,'batch_from':batch_from,'batch_to':batch_to,'form_id':qry1[0]['id'],'data':att_list}
	else:
		data = []
	return data

def Add_session_hashcode(request):
	if requestMethod.POST_REQUEST(request):
		data = json.loads(request.body)
		print(data)
		csv_data = data['csv_data']
		data_obj = data['data_obj']
		response = HttpResponse(content_type='text/csv')  
		response['Content-Disposition'] = 'attachment; filename="file.csv"'  
		writer = csv.writer(response)
		key = list(csv_data[0].keys())
		key.append('LINK')
		writer.writerow(key)
		link_url = "http://localhost/Indirect/IndirectForm/IndirectForm.html?"
		count = 0
		for x in data_obj:
			csv_data[count]['LINK'] = link_url+'hash_code='+x['hash_code']
			x['expiry_date'] = x['expiry_date'].split('T')[0]
			print(x['expiry_date'])
			# hash_qry = ExternalSurveySession.objects.filter(hash_code=x['hash_code']).values_list('form_status',flat=True)
			# if len(hash_qry)>0:
			# 	status = hash_qry[0]
			# else:
			# 	status = 0
			obj,create = ExternalSurveySession.objects.update_or_create(hash_code = x['hash_code'], defaults={'expiry_date':x['expiry_date']},)
			print(x['hash_code'])
			data1 = list(csv_data[count].values())
			writer.writerow(data1)
			count+=1
			# s1=base64.b64decode(x['hash_code']).decode('utf-8')
		return response  

def check_for_vaid_link(hash_code):
	qry = list(ExternalSurveySession.objects.filter(hash_code=hash_code).values('id','expiry_date','form_status'))
	if len(qry)>0:
		date = datetime.datetime.now()
		if qry[0]['form_status'] == 0:
			if qry[0]['expiry_date'] > date:
				data=[]
			else:
				data = {'mssg':'this link get expired please contact to the admin'}
		else:
			data = {'mssg':'your response is submitted'}



####################################################INTERNAL FACULTY SURVEY #############################################################

def create_internal_fac_survey(request):
	if academicCoordCheck.isNBACoordinator(request):
		emp_id = request.session['hash1']
		session = request.session['Session_id']
		session_name=request.session['Session_name']
		if(requestMethod.POST_REQUEST(request)):
			data = json.loads(request.body)
			# print(type(data['survey_id']))
			# print(data)
			data['survey_id']=int(data['survey_id'])
			qry = InternalFacSurvey.objects.filter(survey_id=data['survey_id'],category__in=data['category'],session=session,dept=data['dept']).exclude(status=0).values_list('id',flat=True)
			# print(qry)
			for y in range(len(qry)):
				qry_del = InternalFacSurvey.objects.filter(id=qry[y]).update(status=0)
			for x in data['category']:
				qry_survey = InternalFacSurvey.objects.create(survey_id = StudentAcademicsDropdown.objects.get(sno=data['survey_id']),category=EmployeeDropdown.objects.get(sno=x),dept=CourseDetail.objects.get(uid=data['dept']),session=Semtiming.objects.get(uid=session),created_by = EmployeePrimdetail.objects.get(emp_id=emp_id),time_stamp=str(datetime.datetime.now()))
				qr_object = (InternalFacSurveyQuestion(form_id=InternalFacSurvey.objects.get(id=qry_survey.id),element_id=att['element_id'],ques=att,po_id=json.dumps(att['po_id']))for k,v in data['elements'].items() for att in v)
				qr_create = InternalFacSurveyQuestion.objects.bulk_create(qr_object)
			return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)
		elif(requestMethod.GET_REQUEST(request)):
			# if(requestType.custom_request_type(request.GET, 'get_survey')):
				# data = get_survey_dropdown(session)
				# return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
			if(requestType.custom_request_type(request.GET,'get_po')):
				dept = request.GET['dept']
				data = get_po(dept,session_name)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
			elif(requestType.custom_request_type(request.GET,'view_previews')):
				dept = request.GET['dept']
				category = request.GET['category'].split(',')
				survey_id = request.GET['survey_id']
				qry = list(InternalFacSurvey.objects.filter(survey_id=survey_id,category__in=category,dept=dept,session=session).exclude(status=0).values('id','survey_id__value','survey_id','category','dept','category__value','dept__dept_id__value','created_by__name','created_by'))
				return functions.RESPONSE(qry,statusCodes.STATUS_SUCCESS)
			elif(requestType.custom_request_type(request.GET,'view_form')):
				form_id = request.GET['id']
				data = get_internal_fac_form_data(form_id)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		elif(requestMethod.DELETE_REQUEST(request)):
			data = json.loads(request.body)
			qry = InternalFacSurvey.objects.filter(id=data['id']).update(status=0)
			data = statusMessages.MESSAGE_DELETE
			status = statusCodes.STATUS_SUCCESS
			return functions.RESPONSE(data,status)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def submit_internal_fac_survey(request):
	emp_id = request.session['hash1']
	session = request.session['Session_id']
	session_name=request.session['Session_name']
	if(requestMethod.POST_REQUEST(request)):
		data = json.loads(request.body)
		qry_dupli = list(InternalFacSurveyAnswer.objects.filter(ques_id__form_id=data['form_id'],added_by=emp_id).exclude(ques_id__form_id__status=0).values('id'))
		if len(qry_dupli)==0:
			for x,y in data['elements'].items():
				for z in y:
					if((z['answer']==None and z['answer'] == "") and z['mand']==True):
						data = {'msg':'Mandatory Answer Should not be Empty'}
						status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
						return functions.RESPONSE(data,status)
					if(z['answer']!=None and z['answer']!=""):					
						if(z['category']=='text' and (z['len_check']!=None and z['len_check']!="")):
							if(not(Checks.length_check(z['len_check'],len(z['answer'])))):
								data = {'msg':'Text filled length Should match to the length define'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
						elif(z['category']=='number'):
							if(z['po_id']!=None):
								if(len(z['po_id'])>0 and (z['max']==None or z['max']=="")):
									data = {'msg':'number filled connected with PO must be define with the maximum length'}
									status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
									return functions.RESPONSE(data,status)
							if(z['len_check']!=None and z['len_check']!=""):
								if(not(Checks.length_check(z['len_check'],len(str(z['answer']))))):
									data = {'msg':'length of the number filled must match with the length define'}
									status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
									return functions.RESPONSE(data,status)
							if(z['min']!=None or z['max']!=None):
								maxvalue = z['max'] 
								if(z['min']==None or z['min']==""):
									z['min']=0
								if(z['max']==None or z['max']==""):
									maxvalue= math.inf
								if(not(Checks.min_max_value_check(z['min'],maxvalue,z['answer']))):
									data = {'msg':'number filled must be in range of minimum and maximum define value'}
									status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
									return functions.RESPONSE(data,status)
						elif(z['category']=='slider'):
							if(z['po_id']!=None):
								if(len(z['po_id'])>0 and (z['max']==None or z['max']=="")):
									data = {'msg':'slider value connected with po must have maximum value defined'}
									status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
									return functions.RESPONSE(data,status)
							if(z['min']!=None or z['max']!=None):
								maxvalue = z['max']
								if(z['min']==None or z['min']==""):
									z['min']=0
								elif(z['max']==None or z['max']==""):
									maxvalue=math.inf
								if(not(Checks.min_max_value_check(z['min'],maxvalue,z['answer']))):
									data = {'msg':'slider value filled must be in range of minimum and maximum value'}
									status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
									return functions.RESPONSE(data,status)
						elif(z['category']=='textarea' and z['max_words']!=None and z['max_words']!=""):
							if(not(Checks.min_words_in_paragraph(z['max_words'],z['answer']))):
								data = {'msg':'the no of words in paragraph Should match with the the length defined'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
						elif(z['category']=='email'):
							if(not(Checks.email_check(z['answer']))):
								data = {'msg':'invalid email'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
						elif(z['category']=='date' and z['start']!=None and z['end']!=None):
							if(not(Checks.min_max_date(z['start'],z['end'],z['answer']))):
								data = {'msg':'the date range mismatch with the start and end date defined'}
								status = statusCodes.STATUS_CONFLICT_WITH_MESSAGE
								return functions.RESPONSE(data,status)
					qry_id = InternalFacSurveyQuestion.objects.filter(form_id=data['form_id'],form_id__dept=data['dept'],form_id__survey_id=data['survey_id'],element_id = z['element_id'],form_id__category=data['category']).exclude(form_id__status=0).values_list('id',flat=True)
					z['ques_id'] = qry_id[0]
			qry_obj = (InternalFacSurveyAnswer(ans=z,ques_id=InternalFacSurveyQuestion.objects.get(id=z['ques_id']),added_by=EmployeePrimdetail.objects.get(emp_id=emp_id),time_stamp=str(datetime.datetime.now()))for k,t in data['elements'].items() for z in t)
			qr_create = InternalFacSurveyAnswer.objects.bulk_create(qry_obj)
			data = statusMessages.MESSAGE_FILLED
			status = statusCodes.STATUS_SUCCESS
		else:
			data['msg'] = "Your response has already been submitted."
			return functions.RESPONSE(data, statusCodes.STATUS_WARNING)
	elif(requestMethod.GET_REQUEST(request)):
		if(requestType.custom_request_type(request.GET,'get_filled_survey')):
			key = check_islocked_faculty("FS",[emp_id],session_name)
			if key==True:
				qry_survey ={'mssg':"Your Portal is Locked kindly contect to Dean Sir"}
				return functions.RESPONSE(qry_survey,statusCodes.STATUS_SUCCESS)
			qry = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values('emp_category','dept'))
			qry_dept = list(CourseDetail.objects.filter(dept_id=qry[0]['dept']).values('uid','course_type__value','dept_id__value'))
			if(len(qry_dept)>1):
				for w in qry_dept:
					if(w['course_type__value']=='UG'):
						dept = w['uid']
						break
			else:
				dept = qry_dept[0]['uid']
			qry_survey = list(InternalFacSurvey.objects.filter(category=qry[0]['emp_category'],dept=dept,session=session).exclude(status=0).values('id','survey_id__value').distinct())
			return functions.RESPONSE(qry_survey,statusCodes.STATUS_SUCCESS)
		elif(requestType.custom_request_type(request.GET,'get_data_survey')):
			form_id = request.GET['id']
			qry_ans = list(InternalFacSurveyAnswer.objects.filter(ques_id__form_id=form_id,added_by=emp_id).exclude(status=0).values('id'))
			if len(qry_ans)>0:
				data={}
				data['msg'] = "Your response has already been submitted."
				return functions.RESPONSE(data, statusCodes.STATUS_WARNING)
			data = get_internal_fac_form_data(form_id)
			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
		elif(requestType.custom_request_type(request.GET, 'get_survey')):
			data = get_survey_dropdown(session)
			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
		elif(requestType.custom_request_type(request.GET,'get_course')):
			if request.GET['request_by'] in ('HOD', 'hod'):
				check = checkpermission(request, [319])
				if check == 200:
					q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
					dept = q_dept[0]['dept']
					ccourse = get_filtered_course(dept)
					course=[]
					for c in ccourse:
						if c['course'] in [12,13,16,17]:
							course.append({'course__value': c['course__value'], 'course': c['course']})
					status = 200
					data_values = {'course': course}
					return functions.RESPONSE(data_values,status)
			elif request.GET['request_by'] in ('DEAN', 'dean'):
				check = checkpermission(request, [1371, 1371, 1368, 1372, 1452])
				if check == 200:
					ccourse = get_course()
					course =[]
					for c in ccourse:
						if c['sno'] in [12,13,16,17]:
							course.append({'value': c['value'], 'sno': c['sno']})
					status = 200
					data_values = {'course': course}
					return functions.RESPONSE(data_values,status)
			elif request.GET['request_by'] in ['nba_coordinator']:
					check = checkpermission(request, [1369])
					if check == 200 and ('NC' in request.session['Coordinator_type']):
						ccourse = get_coordinator_course(request.session['hash1'], request.GET['Coordinator_type'], session_name)
						course = []
						for c in ccourse:
							if c['section__sem_id__dept__course'] in [12,13,16,17]:
								course.append({'course__value': c['section__sem_id__dept__course__value'], 'course': c['section__sem_id__dept__course'],'duration':c['section__sem_id__dept__course_duration']})
						status = 200
						data_values = {'course': course}
						return functions.RESPONSE(data_values,status)
		else:
			data = statusMessages.MESSAGE_FORBIDDEN
			status = statusCodes.STATUS_FORBIDDEN
	else:
		data = statusMessages.MESSAGE_FORBIDDEN
		status = statusCodes.STATUS_FORBIDDEN
	return functions.RESPONSE(data,status)

def get_internal_fac_form_data(form_id):
	data = list(InternalFacSurvey.objects.filter(id=form_id).exclude(status=0).values('dept','category','survey_id'))
	if len(data)>0:
		qry = list(InternalFacSurveyQuestion.objects.filter(form_id=form_id).exclude(form_id__status=0).values('element_id','ques').order_by('element_id'))
		att_list = {}
		att_list['form'] = [] 
		for i,j in groupby(qry,key=lambda x:x['element_id']):
			l = list(j)
			if len(l)>0:
				att_list['form'].append(l[0]['ques'])
		data={'dept':data[0]['dept'],'category':data[0]['category'],'survey_id':data[0]['survey_id'],'form_id':form_id,'elements':att_list}
	else:
		data=[]
	return data

def get_faculty_feedback_po_wise(survey_id,category,dept,session,session_name):
	data_values = []
	Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)
	# print(dept)
	qry_po = Dept_VisMis.objects.filter(dept=dept, type='PO').exclude(status='DELETE').values('id', 'description').distinct().order_by('id')
	if qry_po:	
		for survey in survey_id:
			pd=list(qry_po)
			x = len(pd)
			for i in range(x):
				pd[i]['po_level_abbr'] = "PO-" + str(i + 1)
			data={}
			data['feedback']=[]
			final_count=[0]*len(pd)
			final_arry=[None]*len(pd)
			for cat in category:
				a = None
				qry = list(InternalFacSurveyAnswer.objects.filter(ques_id__form_id__survey_id=survey,ques_id__form_id__session=session,ques_id__form_id__dept=dept,ques_id__form_id__category=cat).exclude(ques_id__form_id__status=0).exclude(ques_id__po_id=json.dumps(a)).values('ans','added_by','added_by__name','ques_id__element_id','ques_id__form_id__category__value','ques_id__po_id','ques_id__form_id__survey_id__value').order_by('added_by','ques_id__element_id'))
				if len(qry)>0:
					data['survey_id']=qry[0]['ques_id__form_id__survey_id__value']
					for k,v in groupby(qry,key=lambda x:x['added_by']):
						m = list(v)
						att_list={}
						att_list['emp_id']=k
						att_list['emp_name']=m[0]['added_by__name']
						att_list['emp_category']=m[0]['ques_id__form_id__category__value']
						att_list['po_answer']=[None]*len(pd)
						po_arry=[0]*len(pd)
						for c,j in groupby(m,key=lambda y:y['ques_id__element_id']):
							r = list(j)
							if(len(r)>0):
								i=0
								for p in pd:
									if p['id'] in r[0]['ans']['po_id']:
										if r[0]['ans']['answer']!=None:
											if att_list['po_answer'][i]==None:
												att_list['po_answer'][i] = (r[0]['ans']['answer']/r[0]['ans']['max'])*3
											else:
												att_list['po_answer'][i]= (att_list['po_answer'][i] + (r[0]['ans']['answer']/r[0]['ans']['max'])*3)
											po_arry[i]+=1
											if final_arry[i]==None:
												final_arry[i]= (r[0]['ans']['answer']/r[0]['ans']['max'])*3
											else:
												final_arry[i]=(final_arry[i]+(r[0]['ans']['answer']/r[0]['ans']['max'])*3)
											final_count[i]+=1
									i+=1
						for i in range(len(pd)):
							if att_list['po_answer'][i]!=None: 
								att_list['po_answer'][i]=att_list['po_answer'][i]/po_arry[i]
						data['feedback'].append(att_list)
			if len(data['feedback'])>0:
				for i in range(len(pd)):
					if final_arry[i]!=None:
						final_arry[i]=final_arry[i]/final_count[i]
				data['po']=pd
				data['avg']=final_arry
				data_values.append(data)
	return data_values
