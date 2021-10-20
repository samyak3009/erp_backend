# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime,timedelta
from django.utils import timezone
import json
import datetime
from django.conf import settings
from django.http import HttpResponse,JsonResponse
import time
from dateutil.relativedelta import relativedelta
from django.db.models import Q,Sum,Count,Max
from login.models import EmployeeDropdown,EmployeePrimdetail,AuthUser
from attendance.models import Attendance2
from Registrar.models import *
from StudentAccounts.views import trim
from StudentHostel.models import *
from datetime import date
from datetime import datetime
import math
import calendar
from operator import itemgetter
from login.views import checkpermission,generate_session_table_name
from .models import *
from dashboard.views import academic_calendar
from StudentAcademics.models.models import *
from StudentAcademics.models.models_1819e import *
from StudentAcademics.models.models_1819o import *
from StudentAcademics.models.models_1920o import *
from StudentAcademics.models.models_1920e import *


from StudentMMS.views.mms_function_views import *

from StudentAcademics.views import *
from StudentAccounts.models import SubmitFee,ModeOfPaymentDetails,SubmitFeeComponentDetails
from login.models import EmployeePrimdetail,Daksmsstatus

from StudentMMS.models.models_1819o import *
from StudentSMM.models.models_1819o import *

from StudentSMM.models.models_1819e import *

from StudentSMM.models.models_1920o import *
from StudentMMS.models.models_1920o import *

from Registrar.models import *
from StudentHostel.models import *
import StudentHostel as studenthostel
import io
from threading import Thread
from StudentAccounts.models import SubmitFee,RefundFee
import requests
from PIL import Image,ImageChops,ImageOps
from PIL import ImageFont
from PyPDF2 import PdfFileMerger,PdfFileReader
from PIL import ImageDraw
import qrcode
import urllib
import StudentSMM  as smm
# Create your views here.


def getFeeReceipts(uniq_id,session_id):
	session_details = Semtiming.objects.filter(uid=session_id).values('session')
	new_session_id = (Semtiming.objects.filter(session=session_details[0]['session'],sem_type='odd').values('uid'))[0]['uid']
	q_fee_receipts = SubmitFee.objects.filter(session=new_session_id,uniq_id=uniq_id).exclude(cancelled_status='Y').exclude(status='DELETE').extra(select={'receipt_date':"DATE_FORMAT(time_stamp,'%%d-%%m-%%Y')"}).values('fee_rec_no','id','receipt_type','receipt_date','session__session')
	for q in q_fee_receipts:
		if q['receipt_type'] == 'N':
			q['receipt_type'] = 'Normal'
		elif q['receipt_type'] == 'D':
			q['receipt_type'] = 'Due'

		if q['fee_rec_no'][0]=='A':
			q['fee_type'] = 'Academic Fee'
		elif q['fee_rec_no'][0]=='H':
			q['fee_type'] = 'Hostel Fee'
		elif q['fee_rec_no'][0]=='P':
			q['fee_type'] = 'Penalty Fee'

	return list(q_fee_receipts)

def get_header_profile(uniq_id):
	data=[]
	q_profile = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('image_path','uniq_id__name','uniq_id__uni_roll_no')
	data=list(q_profile)
	if data[0]['uniq_id__uni_roll_no'] is None or data[0]['uniq_id__uni_roll_no'] == '':
		data[0]['uniq_id__uni_roll_no'] = "-----"

	if data[0]['image_path'] is not None:
		imagepath=settings.BASE_URL2 + "StudentMusterroll/Student_images/"+data[0]['image_path']
	else:
		imagepath=settings.BASE_URL2 + "StudentMusterroll/Student_images/default.jpg"
	data[0]['imagepath'] = imagepath
	del data[0]['image_path']
	return data

def get_profile(uniq_id,session_name):
	data={}
	print(session_name)
	studentSession = generate_session_table_name("studentSession_",session_name)
	q_prim_per_det = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('image_path','uniq_id','uniq_id__name','uniq_id__uni_roll_no','uniq_id__batch_from','uniq_id__batch_to','uniq_id__date_of_add','uniq_id__lib','uniq_id__gender__value','uniq_id__caste__value','fname','dob','aadhar_num','bg__value','mname','uniq_id__email_id','uniq_id__dept_detail__dept__value','uniq_id__admission_status__value','uniq_id__dept_detail__course__value','religion__value','physically_disabled','nationality__value')
	q_sess_det = studentSession.objects.filter(uniq_id=uniq_id).values('mob','session__session','year','section__section','sem__sem','section','sem','reg_form_status','registration_status','class_roll_no')
	print(q_sess_det)
	q_father_mob = StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values('father_mob','mother_mob')
	q_address_details = StudentAddress.objects.filter(uniq_id=uniq_id).values('c_add1','c_add2','p_add1','p_add2','c_city','p_city','c_district','p_district','p_pincode','c_pincode','c_state__value','c_state','p_state__value')
	q_primdetail = StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('admission_type__value')


	for k,v in q_prim_per_det[0].items():
		data[k]=v
		if data[k] is None or data[k] == "":
			data[k]="----"

	for k,v in q_sess_det[0].items():
		data[k]=v
		if data[k] is None or data[k] == "":
			data[k]="----"

	for k,v in q_father_mob[0].items():
		data[k]=v
		if data[k] is None or data[k] == "":
			data[k]="----"

	for k,v in q_address_details[0].items():
		data[k]=v
		if data[k] is None or data[k] == "":
			data[k]="----"
	for k,v in q_primdetail[0].items():
		data[k]=v
		if data[k] is None or data[k] == "":
			data[k]="----"

	if data['uniq_id__gender__value'] == 'BOY':
		data['uniq_id__gender__value'] = 'MALE'
	elif data['uniq_id__gender__value'] == 'GIRL':
		data['uniq_id__gender__value'] = 'FEMALE'

	if data['mother_mob'] == 0:
		data['mother_mob'] = "----"

	if data['father_mob'] == 0:
		data['father_mob'] = "----"

	if data['mob'] == 0:
		data['mob'] = "----"

	if data['section'] != '----':
		AcadCoordinator = generate_session_table_name("AcadCoordinator_",session_name)
		q_coord = AcadCoordinator.objects.filter(section=data['section'],coord_type='C').exclude(status="DELETE").values('emp_id__name')
		if len(q_coord)>0:
			data['coord_name'] = q_coord[0]['emp_id__name']
		else:
			data['coord_name']="----"
	else:
		data['coord_name']="----"

	imagepath=settings.BASE_URL2 + "StudentMusterroll/Student_images/"+data['image_path'].split(".")[0]+".JPG"
	data['imagepath'] = imagepath
	del data['image_path']
	return data

def get_bank_details(uniq_id):
	data = StudentBankDetails.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').extra(select={'ac_name':'acc_name','ac_num':'acc_num','ifsc':'ifsc_code'}).values('ac_name','ac_num','ifsc','branch','address','bank_name')
	if len(data)>0:
		return data[0]
	else:
		data={}
		data['ac_name']="----"
		data['ac_num']="----"
		data['ifsc']="----"
		data['branch']="----"
		data['address']="----"
		data['bank_name']="----"

		return data

def get_subjects(sem_id,session_name,sub_type):
	SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
	query_sub = SubjectInfo.objects.filter(sem=sem_id,subject_type=sub_type).exclude(status='DELETE').values('subject_type__value','subject_unit__value','sub_alpha_code','sub_num_code','sub_name','max_ct_marks','max_ta_marks','max_att_marks','max_university_marks','no_of_units','id')
	return list(query_sub)

def get_activity_type(session):
	qry=list(StudentAcademicsDropdown.objects.filter(field='ACTIVITY TYPE',session=session).exclude(value__isnull=True).values('sno','value'))
	return qry

def getComponents(request):
	data_values={}
	status=403
	if 'HTTP_COOKIE' in request.META:
		# print(request.session['uniq_id'])

		if request.user.is_authenticated:
			if request.session['hash3'] == 'Student':
				session=request.session['Session_id']
				session_name=request.session['Session_name']
				if(request.method=='GET'):
					if request.GET['request_type'] == 'fee_receipts':
						query=getFeeReceipts(request.session['uniq_id'],session)
						data_values={'data':query}
					elif request.GET['request_type'] == 'header_profile':
						query=get_header_profile(request.session['uniq_id'])
						query[0]['session']=list(Semtiming.objects.filter(sem_start__gte="2018-06-01").values('uid','session','session_name'))
						query[0]['current_session']=request.session['Session_id']
						data_values={'data':query}
					elif request.GET['request_type'] == 'exam_name':
						query=get_exam_name()
						data_values={'data':query}
					elif request.GET['request_type'] == 'attendance_type':
						data_values=get_sub_attendance_type(session)

					elif request.GET['request_type'] == 'sem_commencement':
						studentSession = generate_session_table_name("studentSession_",session_name)
						data=list(studentSession.objects.filter(uniq_id=request.session['uniq_id'],session=session).values('year','uniq_id__dept_detail__course','session__sem_end'))
						if data:
							d=data[0]['uniq_id__dept_detail__course']
							dt=data[0]['session__sem_end']
							year=data[0]['year']
						else:
							d=None
							dt=None
							year=None
						data1=list(SemesterCommencement.objects.filter(session=session,course=d,year=year).exclude(status='DELETE').values('commencement_date','session__sem_end'))
						if not data1:
							data_values=({'commencement_date':date.today(),'session__sem_end':dt})
						else:
							com=data1[0]['commencement_date']
							end=data1[0]['session__sem_end']
							data_values=({'commencement_date':com,'session__sem_end':end})

					elif request.GET['request_type'] == 'att_category_from_type':
						data_values=get_att_category_from_type(request.GET['att_type'].split(','),session)

					elif request.GET['request_type'] == 'stu_att':
						from_date=datetime.strptime(str(request.GET['from_date']).split('T')[0],"%Y-%m-%d").date()
						to_date=datetime.strptime(str(request.GET['to_date']).split('T')[0],"%Y-%m-%d").date()
						if request.GET['att_category']==' ':
							att_category=[]
						else:
							att_category=request.GET['att_category'].split(',')
						att_type=request.GET['att_type'].split(',')
						uniq_id=request.session['uniq_id']

						# att_type = get_sub_attendance_type()
						# att_type_li = [t['sno'] for t in att_type]
						studentSession =generate_session_table_name("studentSession_",session_name)
						q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date','section__sem_id')
						subjects = get_student_subjects(q_att_date[0]['section__sem_id'],session_name)
						query=get_student_attendance(uniq_id,max(datetime.strptime(str(from_date),"%Y-%m-%d").date(),datetime.strptime(str(q_att_date[0]['att_start_date']),"%Y-%m-%d").date()),to_date,session,att_type,subjects,1,att_category,session_name)
						data_values={'data':query}

					elif request.GET['request_type'] == 'mobikiet_sem_data':
						uniq_id=request.session['uniq_id']
						sem_data = Semtiming.objects.filter(uid=request.session['Session_id']).values('sem_start','sem_end','session')
						studentSession =generate_session_table_name("studentSession_",session_name)

						q_section = studentSession.objects.filter(uniq_id=uniq_id).values('section__section','section__sem_id__sem')

						data_values={'data':{"Current_session":sem_data[0]['session'],'Exam_Des':[],'Till_Schedule':[],'sem_start':sem_data[0]['sem_start'],'sem_end':sem_data[0]['sem_end'],'section':q_section[0]['section__section'],'sem':q_section[0]['section__sem_id__sem']},'error':False,'message':""}

					elif request.GET['request_type'] == 'mobikiet_att':
						final_data={}
						from_date=datetime.strptime(str(request.GET['date_from']).split('T')[0],"%Y-%m-%d").date()
						to_date=datetime.strptime(str(request.GET['date_to']).split('T')[0],"%Y-%m-%d").date()
						uniq_id=request.session['uniq_id']
						if 'att_category' not in request.GET and 'att_type' not in request.GET :
							att_type_li = get_sub_attendance_type(session)
							att_type = [t['sno'] for t in att_type_li]
							att_category_query=get_att_category_from_type(att_type,session)
							att_category=[t['attendance_category'] for t in att_category_query]
						else:
							att_category=request.GET['att_category'].split(',')
							if att_category[0]=='':
								att_category=[]
							att_type=request.GET['att_type'].split(',')

						studentSession =generate_session_table_name("studentSession_",session_name)

						q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date','section__sem_id')
						subjects = get_student_subjects(q_att_date[0]['section__sem_id'],session_name)
						att_data = get_student_attendance(uniq_id,max(datetime.strptime(str(from_date),"%Y-%m-%d").date(),datetime.strptime(str(q_att_date[0]['att_start_date']),"%Y-%m-%d").date()),to_date,session,att_type,subjects,1,att_category,session_name)

						final_data['total_present'] = att_data['present_count']
						final_data['total_total'] = att_data['total']
						final_data['error'] = False
						final_data['message']= ""
						final_data['update'] = False
						final_data['data'] = []

						for att in att_data['sub_data']:
							if '-' in str(att['id']):
								stu_sub_data=[]
							else:
								stu_sub_data = get_student_subject_att_status(uniq_id,att['id'],max(datetime.strptime(str(from_date),"%Y-%m-%d").date(),datetime.strptime(str(q_att_date[0]['att_start_date']),"%Y-%m-%d").date()),to_date,att_type,session_name)
							date_li=[]
							lec_li=[]
							attendance_type_li=[]
							status_li=[]

							for sub in stu_sub_data:
								date_li.append(sub['att_id__date'])
								lec_li.append(sub['att_id__lecture'])
								status_li.append(sub['present_status'])
								if sub['att_type__value'] not in ['SUBSTITUTE']:
									attendance_type_li.append('S')
								elif sub['att_type__value'] not in ['REMEDIAL','NORMAL','TUTORIAL']:
									attendance_type_li.append('E')
								elif sub['att_id__group_id'] is not None:
									if 'REMEDIAL' in sub['att_type__value']:
										attendance_type_li.append('R')
									else:
										attendance_type_li.append('G')
								else:
									if 'REMEDIAL' in sub['att_type__value']:
										attendance_type_li.append('R')
									else:
										attendance_type_li.append('N')
							final_data['data'].append({'date':date_li,'lecture':lec_li,'status':status_li,'attedance_type':attendance_type_li,'subject_name':att['sub_name'],'sub_code':att['sub_alpha_code']+"-"+str(att['sub_num_code']),'lecture_present':att['present_count'],'lecture_total':att['total'],'att_type_color':get_color_app()})

						data_values=final_data

					elif request.GET['request_type'] == 'sub_att_data':
						from_date=datetime.strptime(str(request.GET['from_date']).split('T')[0],"%Y-%m-%d").date()
						to_date=datetime.strptime(str(request.GET['to_date']).split('T')[0],"%Y-%m-%d").date()
						uniq_id=request.session['uniq_id']
						sub_id=request.GET['subject_id']
						att_type = get_sub_attendance_type(session)
						att_type_li = [t['sno'] for t in att_type]
						studentSession =generate_session_table_name("studentSession_",session_name)

						q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date')
						if '-' in sub_id:
							data_values={'data':[]}
						else:
							query=get_student_subject_att_status(uniq_id,sub_id,max(datetime.strptime(str(from_date),"%Y-%m-%d").date(),datetime.strptime(str(q_att_date[0]['att_start_date']),"%Y-%m-%d").date()),to_date,att_type_li,session_name)
							data_values={'data':query,'att_type_color':get_color()}
					elif request.GET['request_type'] == 'profile':
						query=get_profile(request.session['uniq_id'],session_name)
						data_values={'data':query}
					elif request.GET['request_type'] == 'app_profile':
						query=get_profile(request.session['uniq_id'],session_name)
						data={}
						data['name']=query['uniq_id__name']
						data['FName']=query['fname']
						data['MOB']=query['mob']
						data['email']=query['uniq_id__email_id']
						data['M_Name']=query['mname']
						data['Religion']=query['religion__value']
						data['Category']=query['uniq_id__name']
						data['Nationality']=query['nationality__value']
						data['DOB']=query['dob']
						data['P_Add1']=query['p_add1']
						data['P_Add2']=query['p_add2']
						data['P_City']=query['p_city']
						data['P_Dist']=query['p_district']
						data['P_State']=query['p_state__value']
						data['P_Pincode']=query['p_pincode']
						data['C_Add1']=query['c_add1']
						data['C_Add2']=query['c_add2']
						data['C_City']=query['c_city']
						data['C_Dist']=query['c_district']
						data['C_State']=query['c_state__value']
						data['C_Pincode']=query['c_pincode']
						data['gender']=query['uniq_id__gender__value']
						data['image']=query['imagepath']
						data['bank']={}
						data['bank'] = get_bank_details(request.session['uniq_id'])
						data['bank']['update'] = False
						data['bank']['mobileNo'] = query['mob']
						data['bank']['emailid'] = query['uniq_id__email_id']
						data['error']=False
						data_values=data


					elif request.GET['request_type'] == 'time_table':
						studentSession = generate_session_table_name("studentSession_",session_name)
						q_sec = studentSession.objects.filter(uniq_id=request.session['uniq_id']).values('section')
						if q_sec[0]['section'] is not None:
							data=get_section_time_table(q_sec[0]['section'],session_name)
						else:
							data=[]
						query={'error':False,'message':"",'data':data}
						data_values=query
					elif request.GET['request_type'] == 'time_table_dash':
						studentSession = generate_session_table_name("studentSession_",session_name)
						session=Semtiming.objects.get(uid=request.session['Session_id'])
						q_sec = studentSession.objects.filter(uniq_id=request.session['uniq_id']).values('section__section','sem__sem','sem','sem__dept__dept__value','section')
						if q_sec[0]['section'] is not None and q_sec[0]['section'] is not None:
							data=create_matrix_tt(session,q_sec[0]['sem'],q_sec[0]['section'],session_name)
							data.append(q_sec[0]['section__section'])
							data.append(q_sec[0]['sem__sem'])
							data.append(q_sec[0]['sem__dept__dept__value'])
						else:
							data=[]
						data_values=data

					elif request.GET['request_type'] == 'academic_calendar':
						data_values=academic_calendar(session_name)

					elif request.GET['request_type'] == 'get_activity_type':
						data_values=get_activity_type(session)

					status=200

				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=401

	return JsonResponse(data=data_values,status=status,safe=False)

def left_panel(request):
	data=[{}]
	msg=""
	i=0
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if(request.method == 'GET'):
				uniq_id = request.session['uniq_id']
				# print(uniq_id)

				links=list(StudentLeftPanel.objects.filter(parent_id='0').values().order_by('priority'))
				for link in links:
					sub_tabs=list(sublinks(link['menu_id']))
					link['sub_tabs']=sub_tabs
					data[i]["role"]='Student'

				data[i]["tabs"]=list(links)
				i+=1
				msg="success"
				status=200
			else:
				status=502
		else:
			status=401
	else:
		status=500
	result={'msg':msg,'data':data}

	return JsonResponse(data=result,status=status)

def sublinks(parent_id):
	if StudentLeftPanel.objects.filter(parent_id=parent_id).all().count()==0:
		return []
	else:
		links=StudentLeftPanel.objects.filter(parent_id=parent_id).values().order_by('priority')
		for link in links:
			sub_tabs=list(sublinks(link['menu_id']))
			link['sub_tabs']=sub_tabs
		return links

def printFeeReceipts(request):
	data_values={}
	msg=""
	status=403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3'] == 'Student':
				session=Semtiming.objects.get(uid=request.session['Session_id'])
				session_name=request.session['Session_name']
				if(request.method=='GET'):
					#data=json.loads(request.body)
					fee_rec_no=request.GET['fee_rec_no']
					# print(data)
					#fee_id=data['fee_id']

					studentSession = generate_session_table_name("studentSession_",session_name)

					q_check = SubmitFee.objects.filter(fee_rec_no=fee_rec_no).values('fee_rec_no','uniq_id__name','cancelled_status','actual_fee','paid_fee','refund_value','due_value','session__session','receipt_type','id','time_stamp','uniq_id','receipt_type','prev_fee_rec_no')
					if len(q_check)==0:
						status=403
						msg="Fee Receipt not Found"
					else:
						if q_check[0]['uniq_id'] == request.session['uniq_id']:
							fee_rec_no=q_check[0]['fee_rec_no']
							uniq_id=q_check[0]['uniq_id']
							fee_id=q_check[0]['id']
							receipt_name="Student's Copy"
							filename="stu_port.pdf"
							bool_white=False

							date=datetime.strptime(str(q_check[0]['time_stamp']).split(' ')[0],"%Y-%m-%d").strftime("%d-%m-%Y")

							stu_per = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname')
							if len(stu_per)>0:
								fname=stu_per[0]['fname']
							else:
								fname="----"
							stu_det = studentSession.objects.filter(uniq_id=uniq_id).values('year','sem__dept__dept__value','sem__dept__course__value','uniq_id__lib','uniq_id__uni_roll_no','uniq_id__batch_from','uniq_id__batch_to')

							q_mop_details = ModeOfPaymentDetails.objects.filter(fee_id=fee_id).values('MOPcomponent__value','value')

							fee_comp_details = SubmitFeeComponentDetails.objects.filter(fee_id=fee_id).values('fee_component__value','fee_sub_component__value','sub_component_value').order_by('fee_sub_component')

							if not bool_white:
								img = Image.open(settings.FILE_PATH+"KIET_Fee_Receipt.jpg")
							else:
								img =  Image.new(mode='RGB',size=(1478,2100),color=(255,255,255,0))

							size = 1480, 2100
							img.thumbnail(size, Image.ANTIALIAS)


							qr = qrcode.make(fee_rec_no)
							qr=trim(qr)
							qr = qr.resize((136, 136), Image.NEAREST)

							draw = ImageDraw.Draw(img)
							font = ImageFont.truetype(settings.FILE_PATH+"OpenSans-Bold.ttf", 36)
							font2 = ImageFont.truetype(settings.FILE_PATH+"arial.ttf", 36)

							font7 = ImageFont.truetype(settings.FILE_PATH+"arial.ttf", 170)

							font3 = ImageFont.truetype(settings.FILE_PATH+"arial.ttf", 36)
							font4 = ImageFont.truetype(settings.FILE_PATH+"OpenSans-Bold.ttf", 36)

							font5 = ImageFont.truetype(settings.FILE_PATH+"arial.ttf", 32)
							font6 = ImageFont.truetype(settings.FILE_PATH+"OpenSans-Bold.ttf", 32)

							if q_check[0]['cancelled_status'] == 'Y':
								txt=Image.new('L', (1050,170))
								d = ImageDraw.Draw(txt)
								d.text( (0, 0), "CANCELLED",  font=font7, fill=255)
								w=txt.rotate(36,  expand=1)

								img.paste( ImageOps.colorize(w, (0,0,0), (196,196,196)), (270,640),  w)

							draw.text((1130,410),receipt_name,(0,0,0),font=font)
							draw.text((115,510),"Receipt No.:",(0,0,0),font=font)
							draw.text((115,560),"Name:",(0,0,0),font=font)
							draw.text((115,610),"Father's Name:",(0,0,0),font=font)
							draw.text((115,660),"Roll No.:",(0,0,0),font=font)
							draw.text((115,710),"Course:",(0,0,0),font=font)


							draw.text((400,515),fee_rec_no,(0,0,0),font=font2)
							draw.text((400,565),q_check[0]['uniq_id__name'],(0,0,0),font=font2)
							draw.text((400,615),fname,(0,0,0),font=font2)
							if stu_det[0]['uniq_id__uni_roll_no'] is not None:
								draw.text((400,665),str(stu_det[0]['uniq_id__uni_roll_no']),(0,0,0),font=font2)
							else:
								draw.text((400,665),"----",(0,0,0),font=font2)

							draw.text((400,715),stu_det[0]['sem__dept__course__value'],(0,0,0),font=font2)


							draw.text((650,510),"Session:",(0,0,0),font=font)
							draw.text((800,515),q_check[0]['session__session'],(0,0,0),font=font2)

							draw.text((1050,510),"Date:",(0,0,0),font=font)
							draw.text((1150,515),str(date),(0,0,0),font=font2)

							img.paste(qr,(1175,565))
							draw.text((650,660),"Batch:",(0,0,0),font=font)
							draw.text((800,665),str(stu_det[0]['uniq_id__batch_from'])+"-"+str(stu_det[0]['uniq_id__batch_to']),(0,0,0),font=font2)

							draw.text((650,710),"Branch:",(0,0,0),font=font)
							draw.text((800,715),stu_det[0]['sem__dept__dept__value'],(0,0,0),font=font2)

							draw.text((1050,710),"Year:",(0,0,0),font=font)
							draw.text((1150,715),str(stu_det[0]['year']),(0,0,0),font=font2)

							draw.text((115,860),"Particulars",(0,0,0),font=font)
							draw.text((1130,860),"Amount (Rs.)",(0,0,0),font=font)

							y=950
							if q_check[0]['receipt_type'] == 'N':
								for comp in fee_comp_details:
									if comp['sub_component_value'] > 0:
										draw.text((115,y),comp['fee_sub_component__value'].replace("(ONE TIME)","").title(),(0,0,0),font=font3)
										draw.text((1170,y),str(float(comp['sub_component_value']))+"0",(0,0,0),font=font3)
										y+=50
							elif q_check[0]['receipt_type'] == 'D':
								draw.text((115,y),q_check[0]['prev_fee_rec_no'],(0,0,0),font=font3)
								draw.text((1170,y),str(q_check[0]['actual_fee'])+"0",(0,0,0),font=font3)
								y+=50

							y+=20
							draw.line((110,y,1350,y),fill=(0,0,0),width=5)

							y+=20
							draw.text((115,y),"Total Fee",(0,0,0),font=font4)
							draw.text((1170,y),str(q_check[0]['actual_fee'])+"0",(0,0,0),font=font3)

							y+=50
							draw.text((115,y),"Amount Paid",(0,0,0),font=font4)
							draw.text((1170,y),str(q_check[0]['paid_fee'])+"0",(0,0,0),font=font3)

							y+=50
							if q_check[0]['due_value'] is not None and q_check[0]['due_value']>0:
								draw.text((115,y),"Due Amount",(0,0,0),font=font4)
								draw.text((1170,y),str(q_check[0]['due_value'])+"0",(0,0,0),font=font3)
								y+=50

							elif q_check[0]['refund_value'] is not None and q_check[0]['refund_value']>0:
								draw.text((115,y),"Refund Amount",(0,0,0),font=font4)
								draw.text((1170,y),str(q_check[0]['refund_value'])+"0",(0,0,0),font=font3)
								y+=50

							y+=10
							draw.line((110,y,1350,y),fill=(0,0,0),width=5)

							y+=20
							y-=50
							i=0
							x1=115
							x2=400
							for mop in q_mop_details:
								if i%2==0:
									x1=115
									x2=400
									y+=50
								else:
									x1=885
									x2=1170
								i+=1

								if 'DATE' in mop['MOPcomponent__value']:
									try:
										# mop['value']=(datetime.strptime(str(mop['value']).split('T')[0],"%Y-%m-%d"))+relativedelta(days=+1)
										mop['value']=(datetime.strptime(str(mop['value']).split(' ')[0],"%Y-%m-%d")+relativedelta(days=+1)).strftime("%d-%m-%Y")
										# mop['value']=(datetime.strptime(str(mop['value']).split(' ')[0],"%Y-%m-%d")).strftime("%d-%m-%Y")
									except:
										mop['value']=mop['value']
								draw.text((x1,y),str(mop['MOPcomponent__value']).title(),(0,0,0),font=font6)
								if 'AMOUNT' in mop['MOPcomponent__value']:
									draw.text((x2,y+5),str(mop['value'])+".00",(0,0,0),font=font5)
								else:
									draw.text((x2,y+5),str(mop['value']),(0,0,0),font=font5)


							final_img_width = min(img.size[0],1478)
							final_img_height = min(img.size[1],2100)
							tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")

							index=0
							margin_left = 0
							margin_top = 0

							x=index//2*(tmp_image.size[0]//2)
							y=index%2*(tmp_image.size[1]//2)
							w,h=img.size
							tmp_image.paste(img, (x ,y,x+w,y+h))

							tmp_image.save(settings.FILE_PATH+filename, "PDF", resolution=250.0)

							with open(settings.FILE_PATH+filename, 'rb') as pdf:
								response = HttpResponse(pdf, content_type='application/pdf')
								response['Content-Disposition'] = 'inline;filename=some_file.pdf'

								return response
								pdf.closed

							status=200
							return response

						else:
							status=403
							msg="Fee Receipt Not Found"
				else:
					status=502
					msg="Bad Request"
			else:
				status=403
				msg="Not Authorized"
		else:
			status=401
			msg="Not Authorized"
	else:
		status=500
		msg="Error"

	data_values={'msg':msg}
	return JsonResponse(data=data_values,status=status)

def student_registration(request):
	data_values={}
	msg=""
	status=403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3'] == 'Student':
				session=Semtiming.objects.get(uid=request.session['Session_id'])
				session_name=request.session['Session_name']
				uniq_id=request.session['uniq_id']
				if(request.method=='GET'):
					if(request.GET['request_type']=='initial_data'):
						studentSession = generate_session_table_name("studentSession_",session_name)
						q_check_lock_status = studentSession.objects.filter(uniq_id=uniq_id).values('reg_form_status')
						if q_check_lock_status[0]['reg_form_status'] == 'LOCK':
							status=202
							msg='Please contact your class coordinator to be able to fill your Registeration Form.'
							data_values={'msg':msg}
						else:

							query_sub_types = StudentDropdown.objects.filter(field="SUBJECT TYPE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno',flat=True)
							sub_data=[]
							for sub in query_sub_types:
								sub_data.extend(get_subjects(stu_data['sem'],session_name,sub))

							q_state =EmployeeDropdown.objects.filter(field="STATE").exclude(value__isnull=True).values("sno","value")
							data_values={'subjects':sub_data,'states':list(q_state)}
							status=200
							msg='success'
					elif(request.GET['request_type']=='form_data'):
						studentSession = generate_session_table_name("studentSession_",session_name)
						q_check_lock_status = studentSession.objects.filter(uniq_id=uniq_id).values('reg_form_status')
						if q_check_lock_status[0]['reg_form_status'] == 'LOCK':
							status=202
							msg='Please contact your class coordinator to be able to fill your Registeration Form.'
							data_values={'msg':msg}
						else:
							stu_data = get_profile(uniq_id,session_name)

							query_sub_types = StudentDropdown.objects.filter(field="SUBJECT TYPE").exclude(value__isnull=True).exclude(status="DELETE").values_list('sno',flat=True)
							sub_data=[]
							for sub in query_sub_types:
								sub_data.extend(get_subjects(stu_data['sem'],session_name,sub))

							q_state =EmployeeDropdown.objects.filter(field="STATE").exclude(value__isnull=True).values("sno","value")

							data_values={'profile_data':stu_data,'subjects':sub_data,'states':list(q_state)}
							status=200
							msg='success'
					elif(request.GET['request_type']=='after_submit_form'):
						studentSession = generate_session_table_name("studentSession_",session_name)
						SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)

						q_check_lock_status = studentSession.objects.filter(uniq_id=uniq_id).values('registration_status')
						if q_check_lock_status[0]['registration_status'] == 0:
							status=202
							msg='Please fill sem registration form'
							data_values={'msg':msg}
						else:
							q_sec = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id')

							sub_selected=[]
							sub=  SubjectInfo.objects.filter(sem=q_sec[0]['section__sem_id'],subject_type__value='THEORY').exclude(status='DELETE').values('subject_type__value','subject_unit__value','sub_alpha_code','sub_num_code','sub_name','max_ct_marks','max_ta_marks','max_att_marks','max_university_marks','no_of_units','id')

							for s in sub:
								sub_selected.append({'subject_id__sub_alpha_code':s['sub_alpha_code'],'subject_id__sub_num_code':s['sub_num_code'],'subject_id__sub_name':s['sub_name']})
							data_values={'subjects':list(sub_selected)}
							status=200
							msg='success'
				elif(request.method=='POST'):
					studentSession = generate_session_table_name("studentSession_",session_name)
					StudentFillSubjects = generate_session_table_name("StudentFillSubjects_",session_name)
					SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)

					#######################LOCKING STARTS######################
					section_li=list(studentSession.objects.filter(uniq_id=uniq_id).values_list('section',flat=True))
					if check_islocked("REG",section_li,session_name):
						return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
						####################LOCKING ENDS##############################
					q_check_lock_status = studentSession.objects.filter(uniq_id=uniq_id).values('reg_form_status')
					if q_check_lock_status[0]['reg_form_status'] == 'LOCK':
						status=202
						msg='Registration form is Locked. Please contact your class coordinator.'
						data_values={'msg':msg}
					else:
						data = json.loads(request.body)
						subjects = data['subjects']
						c_city=data['c_city']
						c_district=data['c_district']
						if data["c_state_id"] is None:
							c_state_id=None
						else:
							c_state_id=EmployeeDropdown.objects.get(sno=data['c_state_id'])
						c_pincode=data['c_pincode']
						c_add2=data['c_add2']
						c_add1=data['c_add1']

						mob = data['mob']
						email = data['email']
						objs = (StudentFillSubjects(uniq_id=studentSession.objects.get(uniq_id=uniq_id),subject_id=SubjectInfo.objects.get(id=sub)) for sub in subjects)
						q_ins = StudentFillSubjects.objects.bulk_create(objs)
						q_upd_em = StudentPrimDetail.objects.filter(uniq_id=uniq_id).update(email_id=email)
						q_address_update = StudentAddress.objects.filter(uniq_id=uniq_id).update(c_city=c_city,c_district=c_district,c_state=c_state_id,c_pincode=c_pincode,c_add2=c_add2,c_add1=c_add1)
						q_update_mob = studentSession.objects.filter(uniq_id=uniq_id).update(mob=mob,registration_status=1,reg_form_status='LOCK',reg_date_time=datetime.now())

						status=200
						data_values={'msg':'Registeration Form Successfully Submitted'}


				else:
					status=502
					msg="Bad Request"
			else:
				status=403
				msg="Not Authorized"
		else:
			status=401
			msg="Not Authorized"
	else:
		status=500
		msg="Error"
	return JsonResponse(data=data_values,status=status)


def printDeclaration(request):
	data_values={}
	msg=""
	status=403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3'] == 'Student':
				session=Semtiming.objects.get(uid=request.session['Session_id'])
				session_name=request.session['Session_name']
				if(request.method=='GET'):
					uniq_id=request.session['uniq_id']
					return Declarationpdf(uniq_id,session_name)
					# pdf = open(settings.FILE_PATH+filename)
					# pdf.seek(0)
					# response = HttpResponse(pdf.read(), content_type="application/pdf")
					status=200
					return response
				else:
					status=502
					msg="Bad Request"
			else:
				status=403
				msg="Not Authorized"
		else:
			status=401
			msg="Not Authorized"
	else:
		status=500
		msg="Error"

	data_values={'msg':msg}
	return JsonResponse(data=data_values,status=status)

	# /////////////////////////// DHRUV START ////////////////////////////
def small_change(request):
	data_values={}
	msg=""
	status=403
	# print(request.GET)

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3'] == 'Student':
				if(request.method=='GET'):
					uniq_id=request.session['uniq_id']
					if request.GET['request_type'] == 'DOB':
						dob=datetime.strptime(str(request.GET['DATE']).split('T')[0],"%Y-%m-%d").date()
						qry=StudentPerDetail.objects.filter(uniq_id=uniq_id).update(dob=dob)
						qry=StudentPerDetail.objects.filter(uniq_id=uniq_id).values('dob')
						data_values['data']=qry[0]['dob']
						status=200
						msg="Success"
				else:
					status=502
					msg="Bad Request"
			else:
				status=403
				msg="Not Authorized"
		else:
			status=401
			msg="Not Authorized"
	else:
		status=500
		msg="Error"
	data_values['msg']=msg
	return JsonResponse(data=data_values,status=status)



	# /////////////////////////// DHRUV END ////////////////////////////

def StudentBankDetailsChange(request):
	qry=[]
	data={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3']=='Student':
				if request.method=='GET':
					if (request.GET['request_type']== 'get_data'):
						uniq_id=request.session['uniq_id']
						data=list(StudentBankDetails.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('acc_name','acc_num','bank_name','ifsc_code','branch','address'))
						status=200

					if(request.GET['request_type']== 'send_ifsc'):
						ifsc=request.GET['ifsc']
						url = "https://ifsc.razorpay.com/" + ifsc
						try:
							response = urllib.request.urlopen(url)
							data = json.loads(response.read())
							if(data != 'Not Found'):
								address=data['ADDRESS'] +',' + data['STATE']
								data['ADDRESS']=address
							else:
								data=None
						except Exception as e:
							data=None
						status=200
					return JsonResponse(data=data,status=status,safe=False)

				if request.method=='POST':
					data=json.loads(request.body)
					uniq_id=request.session['uniq_id']
					acc_num=data['acc_num']
					acc_name=data['acc_name']
					bank_name=data['bank_name']
					ifsc_code=data['ifsc_code']
					branch=data['branch']
					address=data['address']
					qry=StudentBankDetails.objects.filter(uniq_id=uniq_id).update(status='DELETE')
					qry1=StudentBankDetails.objects.create(acc_name=acc_name,acc_num=acc_num,bank_name=bank_name,ifsc_code=ifsc_code,branch=branch,address=address,uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id),status='INSERT')
					status=200
					data_values={'msg':"Data Added Succesfully"}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(status=status,data=data_values)


def student_marks(request):
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			data=[]
			data_values={}
			session_name=request.session['Session_name']
			QuesPaperApplicableOn=generate_session_table_name("QuesPaperApplicableOn_",session_name)
			QuesPaperSectionDetails=generate_session_table_name("QuesPaperSectionDetails_",session_name)
			StudentMarks=generate_session_table_name("StudentMarks_",session_name)
			Marks=generate_session_table_name("Marks_",session_name)
			SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)
			studentSession=generate_session_table_name("studentSession_",session_name)
			if request.session['hash3']=='Student':
				if request.method=='GET':
					if (request.GET['request_type']== 'get_marks'):
						uniq_id=request.session['uniq_id']
						sem_type=request.session['sem_type']
						exam_id=request.GET['exam_id']
						# print(exam_id)
						if(exam_id!="-1"):
							qry=list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('dept_detail','join_year'))
							query=list(studentSession.objects.filter(uniq_id=uniq_id).values('sem'))
							format_id=list(QuesPaperApplicableOn.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id__exam_id=exam_id,sem=query[0]['sem']).values_list('ques_paper_id',flat=True))
							max_marks={}
							if len(format_id)==0:
								maximum=60
								max_marks['total_marks']=60
							else:
								max_marks=QuesPaperSectionDetails.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id=format_id[0]).aggregate(total_marks=Sum('max_marks'))

							subject=list(SubjectInfo.objects.exclude(subject_type__value='LAB').exclude(subject_type__value='VALUE ADDED COURSE').exclude(status="DELETE").filter(sem=query[0]['sem']).values('id','sub_name','sub_alpha_code','sub_num_code').annotate(ids=F('id')))
							avg_marks_obt=0.0
							avg_total_marks=0.0
							for s in subject:
								subject_name=s['sub_name']+' ('+s['sub_alpha_code']+'-'+s['sub_num_code']+')'
								qry=StudentMarks.objects.exclude(status='DELETE').filter(uniq_id=uniq_id,marks_id__exam_id=exam_id,marks_id__subject_id=s['id']).aggregate(marks_obtained=Sum('marks'))
								qry1=StudentMarks.objects.exclude(status="DELETE").filter(uniq_id=uniq_id,marks_id__exam_id=exam_id,marks_id__subject_id=s['id']).values('present_status')

								if qry['marks_obtained']==None:
									if len(qry1)!=0:
										qry['marks_obtained']='P'
								if len(qry1)==0:
									print("vrinda")
								else:
									if qry1[0]['present_status']=='A':
										qry['marks_obtained']=qry1[0]['present_status']
										avg_total_marks=avg_total_marks+max_marks['total_marks']
									elif qry1[0]['present_status']=='D':
										qry['marks_obtained']=qry1[0]['present_status']
										avg_total_marks=avg_total_marks+max_marks['total_marks']
									elif qry1[0]['present_status']=='P':
										print(subject_name)
										if type(qry['marks_obtained'])==type(avg_marks_obt) and max_marks is not None:
											avg_marks_obt=avg_marks_obt+qry['marks_obtained']
											avg_total_marks=avg_total_marks+max_marks['total_marks']
										elif max_marks is not None:
											avg_marks_obt=avg_marks_obt
											avg_total_marks=avg_total_marks+max_marks['total_marks']

								if len(format_id)==0:
									data.append({'subject_name':subject_name,'marks_obtained':qry.get('marks_obtained',0),'total_marks':maximum})
								else:
									query=list(studentSession.objects.filter(uniq_id=uniq_id).values('sem'))
									data.append({'subject_name':subject_name,'marks_obtained':qry.get('marks_obtained',0),'total_marks':max_marks['total_marks']})
							data_values={'data':data,'avg_marks_obt':avg_marks_obt,'avg_total_marks':avg_total_marks}
							status=200
						else:
							query=studentSession.objects.filter(uniq_id=uniq_id).values('sem')
							subject_details=list(SubjectInfo.objects.exclude(status="DELETE").filter(sem=query[0]['sem']).values('max_ct_marks','max_ta_marks','sub_name','sub_alpha_code','sub_num_code','id','max_att_marks','subject_type','sem').annotate(ids=F('id')))
							temp_data=single_student_ct_marks(session_name,uniq_id,subject_details,{})
							print(temp_data)
							data_values=temp_data
							status=200
					elif (request.GET['request_type']== 'get_exams'):
						uniq_id=request.session['uniq_id']
						qry_section_id = studentSession.objects.filter(uniq_id=uniq_id).values('section')
						print(qry_section_id)
						qry_exam_name =list(Marks.objects.filter(section=qry_section_id[0]['section']).exclude(status='DELETE').annotate(sno=F('exam_id'),value=F('exam_id__value')).values('sno','value').distinct().order_by('sno'))
						# qry_exam_name.append({'sno':int(-1),'value':'INTERNAL MARKS'})
						data_values=list(qry_exam_name)

						status=200
					return JsonResponse(data=data_values,status=status,safe=False)

				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(status=status,data=data_values)

def Activities_Student_Portal(request):
	data_values=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3']=='Student':
				session_name=request.session['Session_name']
				StudentActivities = generate_session_table_name("StudentActivities_",session_name)
				studentSession = generate_session_table_name("studentSession_",session_name)
				ActivitiesApproval = generate_session_table_name("ActivitiesApproval_",session_name)
				if request.method=='POST':
					data = json.loads(request.body)
					uniq_id = request.session['uniq_id']
					activity_type = data['activity_type']
					Date_of_event=datetime.strptime(str(data['Date_of_event']).split('T')[0],"%Y-%m-%d").date()
					Organized_by = data['Organized_by']
					venue_address = data['venue_address']
					venue_city = data['venue_city']
					venue_state = data['venue_state']
					venue_country = data['venue_country']
					Description = data['Description']
					Document = data['Document']

					if Document=="":
						qry = StudentActivities.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),activity_type=StudentAcademicsDropdown.objects.get(sno=activity_type),date_of_event=Date_of_event,organised_by=Organized_by,venue_address=venue_address,venue_city=venue_city,description=Description,venue_state=venue_state,venue_country=venue_country)
					else:
						qry = StudentActivities.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),activity_type=StudentAcademicsDropdown.objects.get(sno=activity_type),date_of_event=Date_of_event,organised_by=Organized_by,venue_address=venue_address,venue_city=venue_city,description=Description,venue_state=venue_state,venue_country=venue_country,student_document=Document)

					qry1=ActivitiesApproval.objects.create(Activities_detail=StudentActivities.objects.get(id=qry.id))
					if qry:
						data_values={'msg':'Data Succesfully Inserted'}
					else:
						data_values={'msg':'Data Could not be Inserted'}
					status=200

				elif request.method=='GET':
					uniq_id = request.session['uniq_id']
					qry = list(ActivitiesApproval.objects.filter(Activities_detail__uniq_id=uniq_id).exclude(status='DELETE').exclude(Activities_detail__status='DELETE').values('Activities_detail__id','Activities_detail__date_of_event','Activities_detail__organised_by','Activities_detail__venue_address','Activities_detail__venue_city','Activities_detail__description','Activities_detail__student_document','Activities_detail__time_stamp','Activities_detail__venue_state','Activities_detail__venue_country','Activities_detail__activity_type','Activities_detail__activity_type__value','appoval_status'))
					for q in qry:
						if(q['Activities_detail__student_document']==None):
							q['Activities_detail__student_document']=""
					data_values=qry
					status=200

				elif request.method=='PUT':
					uniq_id = request.session['uniq_id']
					data = json.loads(request.body)
					id = data['id']
					activity_type = data['activity_type']
					Date_of_event=datetime.strptime(str(data['Date_of_event']).split('T')[0],"%Y-%m-%d").date()
					Organized_by = data['Organized_by']
					venue_address = data['venue_address']
					venue_city = data['venue_city']
					venue_state = data['venue_state']
					venue_country = data['venue_country']
					Description = data['Description']
					Document = data['Document']
					qry1 = ActivitiesApproval.objects.filter(Activities_detail__id=id,appoval_status='PENDING').values('appoval_status')
					if qry1[0]['appoval_status']=='PENDING':
						qry = StudentActivities.objects.filter(id=id).update(status='DELETE')
						qry4 = ActivitiesApproval.objects.filter(Activities_detail__id=id).update(status='DELETE')
						qry2 = StudentActivities.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),activity_type=StudentAcademicsDropdown.objects.get(sno=activity_type),date_of_event=Date_of_event,organised_by=Organized_by,venue_address=venue_address,venue_city=venue_city,description=Description,student_document=Document,venue_state=venue_state,venue_country=venue_country)
						qry3=ActivitiesApproval.objects.create(Activities_detail=StudentActivities.objects.get(id=qry2.id))
						data_values={'msg':'Data Succesfully Updated'}
					else:
						data_values={'msg':'Data Could not be Updated'}
					status=200

				elif request.method=='DELETE':
					ActivitiesApproval = generate_session_table_name("ActivitiesApproval_",session_name)
					data = json.loads(request.body)
					id = data['id']
					qry = ActivitiesApproval.objects.filter(Activities_detail__id=id,appoval_status='PENDING').values('appoval_status')
					if qry[0]['appoval_status']=='PENDING':
						qry1 = StudentActivities.objects.filter(id=id).update(status='DELETE')
						qry4 = ActivitiesApproval.objects.filter(Activities_detail__id=id).update(status='DELETE')
						data_values={'msg':'Data Succesfully Deleted'}
					else:
						data_values={'msg':'Data Could not be Deleted'}
					status=200

				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(status=status,data=data_values,safe=False)

def MentorCardOnPortal(request):
	qry=[]
	data_values=[]
	Sessions=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3']=='Student':
				session_name=request.session['Session_name']
				sem_type=request.session['sem_type']
				session_id=request.session['Session_id']
				if request.method=='GET':
					if (request.GET['request_type']== 'get_data'):
						studentSession = generate_session_table_name("studentSession_",session_name)
						IncidentApproval = generate_session_table_name('IncidentApproval_',session_name)
						uniq_id=request.session['uniq_id']
						personal_data=get_profile(uniq_id,session_name)
						academic_data=smm.views.smm_settings_views.student_academic_details(uniq_id,session_name)
						stu_reg_date = list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('date_of_add'))
						all_ses = list(Semtiming.objects.values('sem_end','session','session_name','uid','sem_start'))
						i=0
						date=list(Semtiming.objects.filter(session_name="1819o").values('sem_start'))
						for s in all_ses:
							if s['sem_end']>stu_reg_date[0]['date_of_add'] and s['sem_start']>=date[0]['sem_start']:
								Sessions.append({})
								Sessions[i]['uid']=s['uid']
								Sessions[i]['session_name']=s['session_name']
								i=i+1
						data={}
						data1 = {}
						for ses in Sessions:
							UniversityWise = smm.views.smm_settings_views.UnivMarksInfo(uniq_id,ses['session_name'])
							semester_wise = smm.views.smm_settings_views.SemesterWisePerformance(uniq_id,ses['session_name'],ses['uid'])
							data[ses['session_name']]=semester_wise
							data1[ses['session_name']]=UniversityWise

						q_activity= smm.views.smm_settings_views.get_student_activities(uniq_id,session_name)

						if sem_type=='even':
							qry=list(Semtiming.objects.filter(uid=session_id).values_list('session',flat=True))
							sem_odd = list(Semtiming.objects.filter(session=qry[0],sem_type='odd').values('uid'))
							session_id = sem_odd[0]['uid']
						residential_status = SubmitFee.objects.filter(cancelled_status='N',uniq_id=uniq_id,status='INSERT',fee_rec_no__contains='H',session=session_id).exclude(id__in=RefundFee.objects.values_list('fee_id',flat=True)).exclude(status__contains='DELETE').values()
						if(len(residential_status)>0):
							res_status='HOSTELLER'
						else:
							res_status='DAY SCHOLAR'
						personal_data['res_status']=res_status
						indisciplinary = list(IncidentApproval.objects.filter(incident_detail__uniq_id=uniq_id).exclude(status='DELETE').exclude(incident_detail__incident__status='DELETE').exclude(incident_detail__status='DELETE').values('incident_detail__incident__date_of_incident','incident_detail__incident__description','incident_detail__incident__incident_document','incident_detail__incident__added_by','incident_detail__uniq_id','incident_detail__action','incident_detail__comm_to_parent','incident_detail__student_document','remark','appoval_status','approved_by','incident_detail__uniq_id__session__session','incident_detail__uniq_id__sem__sem','incident_detail__uniq_id__session__sem_type'))

						data_values.append({'Personal':personal_data,'Academic':academic_data,'UniversityWise':data1,'SemesterWise':data,'Activities':list(q_activity),'Indisciplinary':indisciplinary})

						status=200
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(status=status,data=data_values,safe=False)

def HostelAppForm(request):
	Sessions=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3']=='Student':
				uniq_id = request.session['uniq_id']
				session_name = request.session['Session_name']
				sem_type=request.session['sem_type']
				session_id=request.session['Session_id']
				session = request.session['Session']
				if int(session_name[:2])<19:
					return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
				# previous_session_odd=str(int(session_name[:2])-1)+str(int(session_name[2:4])-1)+"o"
				# previous_session_even=str(int(session_name[:2])-1)+str(int(session_name[2:4])-1)+"e"

				HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_',session_name)
				HostelSeaterPriority = generate_session_table_name('HostelSeaterPriority_',session_name)
				HostelStudentMedical = generate_session_table_name('HostelStudentMedical_',session_name)
				HostelMedicalCases = generate_session_table_name('HostelMedicalCases_',session_name)
				HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_',session_name)
				# studentSession_previous_odd = generate_session_table_name("studentSession_",previous_session_odd)
				# studentSession_previous_even = generate_session_table_name("studentSession_",previous_session_even)
				studentSession = generate_session_table_name("studentSession_",session_name)
				if request.method=='GET':
					if (request.GET['request_type']== 'form_data'):
						locking_status = studenthostel.views.hostel_function.check_isLocked('S',uniq_id,session_name)
						details = studenthostel.views.hostel_function.get_student_details(uniq_id,session_name,{},sem_type,session_id)
						course_dur = list(CourseDetail.objects.filter(course=details[0]['sem__dept__course']).values_list('course_duration',flat=True).distinct())
						if locking_status==True:
							details[0]['is_locked']=False
						else:
							details[0]['is_locked']=True
							details[0]['msg']='Portal is locked'
						# if details[0]['year'] == course_dur[0]:
						if False:
							details[0]['is_eligible'] = "N"
							data_values = {'msg':'You are not eligible for filling the hostel application form'}
						else:
							details[0]['is_eligible'] = "Y"
							app_check = list(HostelStudentAppliction.objects.filter(uniq_id=uniq_id,current_status="PENDING").exclude(status='DELETE').values_list('id',flat=True))
							if len(app_check)>0:
								details[0]['already_filled']=True
								details[0]['app_id']=app_check[0]
							else:
								details[0]['already_filled']=False
								details[0]['app_id']=None
							new_session = session.split('-')
							new_session1 = str(int(new_session[0])-1)+'-'+str(int(new_session[1])-1)
							qry = list(Semtiming.objects.filter(session=new_session1).values('uid','session_name','sem_start','sem_end','sem_type'))
							att_per = 0.0
							total_marks = 0.0
							total_marks_obt = 0.0
							count = 0
							details[0]['att']={}
							for q in qry:
								i=0
								sub_id = []
								max_marks = 0.0
								total_internal = 0.0
								total_external = 0.0
								attendance = 0.0
								att_category = []
								att_type = get_sub_attendance_type(q['uid'])
								att_type_li = [t['sno'] for t in att_type]
								studentSession = generate_session_table_name("studentSession_",q['session_name'])

								q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date','section__sem_id')
								subjects = get_student_subjects(q_att_date[0]['section__sem_id'],q['session_name'])
								query=get_student_attendance(uniq_id,max(datetime.strptime(str(q['sem_start']),"%Y-%m-%d").date(),datetime.strptime(str(q_att_date[0]['att_start_date']),"%Y-%m-%d").date()),q['sem_end'],q['uid'],att_type_li,subjects,1,att_category,q['session_name'])
								if (query['total']>0):
									attendance = round((query['present_count']/query['total'])*100,2)
									att_per = att_per+(query['present_count']/query['total'])*100
								else:
									attendance =0.0
								details[0]['att'][q['session_name']]=attendance
								if q['sem_type'] == 'odd':
									subjects = get_student_subjects(q_att_date[0]['section__sem_id'],q['session_name'])
									StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_",q['session_name'])
									for s in subjects:
										sub_id.append(s['id'])
										if(sub_id[i]=="" or sub_id[i]=="----" or sub_id[i]==None):
											sub_id.pop(i)
											i = i-1
										i = i+1
									marks = StudentUniversityMarks.objects.filter(uniq_id=uniq_id,subject_id__in=sub_id).values('external_marks','internal_marks','subject_id__max_university_marks','subject_id__max_ct_marks','subject_id__max_att_marks','subject_id__max_ta_marks','back_marks')
									print(marks.query)
									for m in marks:
										max_marks = max_marks+float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks'])+float(m['subject_id__max_att_marks'])+float(m['subject_id__max_ta_marks'])
										try:
											if (m['internal_marks']=='' or m['internal_marks']==None):
												m['internal_marks'] = 0.0
											if (m['external_marks']=='' or m['external_marks']==None):
												m['external_marks'] = 0.0
											if (m['back_marks']!= None):
												count = count+1
												m['external_marks'] = float(m['back_marks'])
											total_internal = total_internal + float(m['internal_marks'])
											total_external = total_external + float(m['external_marks'])
										except ValueError:
											total_internal = total_internal
											total_external = total_external
										total_marks = max_marks
										total_marks_obt = total_external + total_internal
									details[0]['univ_marks'] = {'Marks':{'Obtained_Marks':total_marks_obt,'Max_Marks':total_marks},'Carry_Over':count}
							if att_per!=0:
								average_att = round(att_per,2)/2
							else:
								average_att = 0.00
							details[0]['avg_att'] = average_att
							if details[0]['gender__value'] == 'MALE':
								hostel_id = studenthostel.views.hostel_function.get_hostel('BOYS',{},session_id)
							elif details[0]['gender__value'] == 'FEMALE':
								hostel_id = studenthostel.views.hostel_function.get_hostel('GIRLS',{},session_id)
							h_id=[]
							for h in hostel_id:
								h_id.append(h['sno'])
							q1 = list(HostelSetting.objects.filter(branch=details[0]['sem__dept'],year=details[0]['year'],hostel_id__hostel_id__in=h_id).exclude(status="DELETE").values('hostel_id__bed_capacity','hostel_id__bed_capacity__value').distinct().order_by("hostel_id__bed_capacity__value"))
							if len(q1)>0:
								details[0]['room_preference'] = q1
							else:
								attendance =0.0
							details[0]['att'][q['session_name']]=attendance
							if q['sem_type'] == 'odd':
								StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_",q['session_name'])
								for s in subjects:
									sub_id.append(s['id'])
									if(sub_id[i]=="" or sub_id[i]=="----" or sub_id[i]==None):
										sub_id.pop(i)
										i = i-1
									i = i+1
								marks = StudentUniversityMarks.objects.filter(uniq_id=uniq_id,subject_id__in=sub_id).values('external_marks','internal_marks','subject_id__max_university_marks','subject_id__max_ct_marks','subject_id__max_att_marks','subject_id__max_ta_marks','back_marks')
								for m in marks:
									max_marks = max_marks+float(m['subject_id__max_university_marks']) + float(m['subject_id__max_ct_marks'])+float(m['subject_id__max_att_marks'])+float(m['subject_id__max_ta_marks'])
									if (m['internal_marks']=='' or m['internal_marks']==None):
										m['internal_marks'] = 0.0
									if (m['external_marks']=='' or m['external_marks']==None):
										m['external_marks'] = 0.0
									if (m['back_marks']!= None):
										count = count+1
										m['external_marks'] = float(m['back_marks'])
									total_internal = total_internal + float(m['internal_marks'])
									total_external = total_external + float(m['external_marks'])
									total_marks = max_marks
									total_marks_obt = total_external + total_internal
								details[0]['univ_marks'] = {'Marks':{'Obtained_Marks':total_marks_obt,'Max_Marks':total_marks},'Carry_Over':count}
							if att_per!=0:
								average_att = round(att_per,2)/2
							else:
								average_att = 0.00
							details[0]['avg_att'] = average_att
							if details[0]['gender__value'] == 'MALE':
								hostel_id = studenthostel.views.hostel_function.get_hostel('BOYS',{},session_id)
							elif details[0]['gender__value'] == 'FEMALE':
								hostel_id = studenthostel.views.hostel_function.get_hostel('GIRLS',{},session_id)
							h_id=[]
							for h in hostel_id:
								h_id.append(h['sno'])
							q1 = HostelSetting.objects.filter(branch=details[0]['sem__dept'],year=details[0]['year'],hostel_id__hostel_id__in=h_id).exclude(status="DELETE").values('hostel_id__bed_capacity','hostel_id__bed_capacity__value').distinct().order_by("hostel_id__bed_capacity__value")
							if len(q1)>0:
								details[0]['room_preference'] = list(q1)
							else:
								details[0]['room_preference'] = []
							details[0]['medical_cases'] = studenthostel.views.hostel_function.get_medical_cases({},session_id)
							data_values = details[0]
						status = 200

					elif (request.GET['request_type']== 'edit_form'):
						app_id = request.GET['app_id']
						seater = list(HostelSeaterPriority.objects.filter(application_id=app_id).exclude(status="DELETE").values('seater','seater__value','priority').order_by('priority'))
						medical = list(HostelMedicalCases.objects.filter(student_medical__uniq_id=uniq_id,student_medical__session=session_id).exclude(status="DELETE").values("student_medical__medical_category","student_medical__medical_category__value","student_medical__document","cases","cases__value").distinct())
						if len(medical)==0:
							medical=None
							Category=None
						else:
							for m in medical:
								Category = m['student_medical__medical_category__value']
						if len(seater)==0:
							seater=None
						data_values = ({"Room_preference":seater,"Medical":medical,"Category":Category})
						status = 200

				elif request.method == "POST":
					data = json.loads(request.body)
					print(data)
					agree = data['agree']
					medical_data = data['medical_data']
					medical_cases = []
					medical_doc = []
					if medical_data!=None:
						for m in medical_data:
							medical_cases.append(m['cases'])
							medical_doc.append(m['document'])
					room_preference = data['room_preference']
					attendance = data['attendance']
					uni_marks = data['univ_marks']
					marks_obt = uni_marks['Marks']['Obtained_Marks']
					carry_over = uni_marks['Carry_Over']
					if marks_obt==0:
						marks_obt=None
					max_marks = uni_marks['Marks']['Max_Marks']
					if max_marks==0:
						max_marks=None

					if agree==True:
						locking_status = studenthostel.views.hostel_function.check_isLocked('S',uniq_id,session_name)
						if locking_status==True:
							qry = list(HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values_list('id',flat=True))
							if len(qry)>0:
								HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").update(status="DELETE")
								HostelSeaterPriority.objects.filter(application_id=qry[0]).update(status="DELETE")
								HostelStudentMedical.objects.filter(uniq_id=uniq_id).update(status="DELETE")
								q1 = list(HostelStudentMedical.objects.filter(uniq_id=uniq_id,status="DELETE").values_list('id',flat=True).order_by('-id'))
								if len(q1)>0:
									HostelMedicalCases.objects.filter(student_medical=q1[0]).update(status="DELETE")
									HostelMedicalApproval.objects.filter(student_medical=q1[0]).update(status="DELETE")

							HostelStudentAppliction.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),current_status="PENDING",attendance_avg=attendance,agree=1,uni_marks_obt=marks_obt,uni_max_marks=max_marks,carry=carry_over)
							app_id = list(HostelStudentAppliction.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values_list('id',flat=True))
							objs = (HostelSeaterPriority(application_id=HostelStudentAppliction.objects.get(id=app_id[0]),seater=HostelDropdown.objects.get(sno=r),priority=i+1)for i,r in enumerate(room_preference))
							create = HostelSeaterPriority.objects.bulk_create(objs)

							########## FOR CATEGORY ################
							query = studenthostel.views.hostel_function.get_medical_category({},session_id)
							########################################
							if medical_data!=None:
								HostelStudentMedical.objects.filter(uniq_id=uniq_id).update(status="DELETE")
								HostelMedicalCases.objects.filter(student_medical__uniq_id=uniq_id).update(status="DELETE")
								HostelMedicalApproval.objects.filter(student_medical__uniq_id=uniq_id).update(status="DELETE")

								if len(medical_doc)>0:
									HostelStudentMedical.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),document=medical_doc[0],session=Semtiming.objects.get(uid=session_id))
								else:
									HostelStudentMedical.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),session=Semtiming.objects.get(uid=session_id))

								# q2 = (HostelStudentMedical(uniq_id=studentSession.objects.get(uniq_id=uniq_id),document=m,session=Semtiming.objects.get(uid=session_id))for m in medical_doc)
								# HostelStudentMedical.objects.bulk_create(q2)
								medical_id = list(HostelStudentMedical.objects.filter(uniq_id=uniq_id,document__in=medical_doc).exclude(status="DELETE").values_list('id',flat=True))
								q3 = (HostelMedicalCases(student_medical=HostelStudentMedical.objects.get(id=medical_id[0]),cases=HostelDropdown.objects.get(sno=m))for m in medical_cases)
								HostelMedicalCases.objects.bulk_create(q3)
								HostelMedicalApproval.objects.create(student_medical=HostelStudentMedical.objects.get(id=medical_id[0]),level=1,approval_status="PENDING")
							data_values={'msg':'Your Hostel Application Form Is Succesfully Filled'}
							status=200
						else:
							data_values={'msg':'Portal is locked'}
							status=202
					else:
						data_values={'msg':'Please agree our terms and conditions'}
						status=202
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(status=status,data=data_values,safe=False)

def SurveyFillFeedback(request):
	data_values=[]
	Sessions=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3']=='Student':

				session_name=request.session['Session_name']
				sem_type=request.session['sem_type']
				session_id=request.session['Session_id']
				uniq_id = request.session['uniq_id']
				SurveyAddQuestions=generate_session_table_name("SurveyAddQuestions_",session_name)
				SurveyFillFeedback=generate_session_table_name("SurveyFillFeedback_",session_name)
				studentSession=generate_session_table_name("studentSession_",session_name)
				# StudentSemester=generate_session_table_name("StudentSemester_",session_name)
				if request.method=='GET':
					if (request.GET['request_type']== 'get_data'):
						print(studentSession)
						sem_id=studentSession.objects.filter(uniq_id=uniq_id).values('sem')
						qry=list(SurveyAddQuestions.objects.filter(survey_id=StudentAcademicsDropdown.objects.get(sno=request.GET['survey_id']),sem_id=sem_id[0]['sem']).exclude(status__contains='DELETE').values('description','question_img','po_id','id'))
						qry1=SurveyFillFeedback.objects.filter(uniq_id=uniq_id,ques_id__survey_id=request.GET['survey_id']).exclude(status__contains='DELETE').values('feedback')
						if qry1:
							msg=True
						else:
							msg=False
						data_values = {'data':qry,'msg':msg}
						status=200

					elif(request.GET['request_type']== 'get_survey'):
						qry=studentSession.objects.filter(uniq_id=uniq_id).values('sem')
						survey_list=get_survey_dropdown_by_sem(qry[0]['sem'],session_id,session_name)
						# survey_list=get_survey_dropdown(session_id)

						data_values={'survey_list':survey_list}
						status=200


				elif request.method=='POST':
					data1 = json.loads(request.body)
					data1=data1['data']
					for x in data1:
						objs = SurveyFillFeedback.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id),ques_id=SurveyAddQuestions.objects.get(id=x['ques_id']),feedback=x['feedback'])

						if objs :
							data_values = {'msg':'Successfully Submitted'}
							status=200

				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(status=status,data=data_values,safe=False)
