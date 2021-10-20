# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.http import HttpResponse, JsonResponse
import time
from dateutil.relativedelta import relativedelta
from django.db.models import Q, F
from django.conf import settings
import math
from datetime import date
from datetime import datetime
from operator import itemgetter
import re

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType

from login.models import EmployeeDropdown, AuthUser
from .models import *
from StudentAccounts.models import *
from StudentPortal.models import *
from musterroll.models import EmployeePerdetail,EmployeeAddress

from StudentAccounts.views import generate_lib_id
from AppraisalStaff.views.appraisal_staff_function import get_total_experience
from AppraisalFaculty.views.appraisal_faculty_functions import get_university_marks_subject_wise
from StudentSMM.views.smm_function_views import check_residential_status
from login.views import checkpermission, generate_session_table_name
from leave.views import calculate_working_days
from Accounts.views import Accounts_dropdown
from StudentHostel.views.hostel_function import get_odd_sem

import requests
from PIL import Image, ImageChops, ImageOps,ImageDraw
from PIL import ImageFont
from PyPDF2 import PdfFileMerger, PdfFileReader
# from PyPDF2 import PdfFileMerger
import textwrap
import qrcode
import urllib
from threading import Thread
# Create your views here.


def get_filtered_course(dept):
	qry = CourseDetail.objects.filter(dept=dept).values('course', 'course__value')
	return list(qry)


def get_bg():
	qry = EmployeeDropdown.objects.filter(field="BLOOD GROUP").exclude(value__isnull=True).values("sno", "value")
	return list(qry)


def get_marital_status():
	qry = EmployeeDropdown.objects.filter(field="MARITAL STATUS").exclude(value__isnull=True).values("sno", "value")
	return list(qry)


def get_state():
	qry = EmployeeDropdown.objects.filter(field="STATE").exclude(value__isnull=True).values("sno", "value")
	return list(qry)


def get_occupation():
	qry = StudentDropdown.objects.filter(field="OCCUPATION").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_course():
	qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_subject_type():
	qry = StudentDropdown.objects.filter(field="SUBJECT TYPE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_through():
	qry = StudentDropdown.objects.filter(field="ADMISSION THROUGH").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_admission_type():
	qry = StudentDropdown.objects.filter(field="ADMISSION TYPE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_exam_type():
	qry = StudentDropdown.objects.filter(field="ENTRANCE EXAM TYPE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_admission_category():
	qry = StudentDropdown.objects.filter(field="ADMISSION CATEGORY").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_gender():
	qry = StudentDropdown.objects.filter(field="GENDER").exclude(status="DELETE").exclude(value__isnull=True).values("sno", "value")
	return list(qry)


def get_branch(course):
	try:
		qry = CourseDetail.objects.filter(course_id=StudentDropdown.objects.get(sno=course)).exclude(dept_id__value='AS').values("uid", "dept_id__value", "course_duration")
	except:
		qry = []
	return list(qry)


def get_category():
	qry = StudentDropdown.objects.filter(field="ADMISSION CATEGORY").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_status():
	qry = StudentDropdown.objects.filter(field="ADMISSION STATUS").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_caste():
	qry = StudentDropdown.objects.filter(field="CASTE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
	return list(qry)


def get_nation():
	qry = EmployeeDropdown.objects.filter(field="NATIONALITY").exclude(value__isnull=True).values("sno", "value")
	return list(qry)


def get_semester(branch):
	try:
		qry = StudentSemester.objects.filter(dept=CourseDetail.objects.get(uid=branch)).exclude(sem__isnull=True).values("sem", "sem_id", 'dept__course__value')
	except:
		qry = []
	return list(qry)


def get_section(semester):
	print(semester)
	qry = Sections.objects.filter(sem_id=StudentSemester.objects.get(sem_id=semester)).exclude(status="DELETE").values("section_id", "section")
	return list(qry)


def get_religion():
	qry = EmployeeDropdown.objects.filter(field="RELIGION").exclude(value__isnull=True).values("sno", "value")
	return list(qry)


def get_board():
	qry = EmployeeDropdown.objects.filter(field="BOARD").exclude(value__isnull=True).values("sno", "value")
	return list(qry)


def get_universities():
	qry = EmployeeDropdown.objects.filter(field="UNIVERSITY").exclude(value__isnull=True).values("sno", "value")
	return list(qry)


def get_degree():
	qry = EmployeeDropdown.objects.filter(field="DEGREE").exclude(value__isnull=True).values("sno", "value")
	return list(qry)
# /////////////////////// complete detail of student USING unique ID////////////////////////////


def Student_PrimDetail(uniq_identify):
	qry1 = StudentPrimDetail.objects.filter(uniq_id=uniq_identify).values()
	return list(qry1)


def Student_Session_1718e(uniq_identify):
	studentSession_1718e.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = studentSession_1718e.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values()
	return list(qry1)


def Student_Session(uniq_identify, session_name):
	student_session = generate_session_table_name("studentSession_", session_name)

	student_session.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = student_session.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values('acc_reg', 'class_roll_no', 'fee_status', 'mob', 'registration_status', 'section_id', 'sem_id', 'session_id__session', 'uniq_id_id', 'year')
	return list(qry1)


def StudentPerDetail_fun(uniq_identify):
	StudentPerDetail.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = StudentPerDetail.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values()
	return list(qry1)


def Student_Academics(uniq_identify):
	StudentAcademic.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = StudentAcademic.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values()
	return list(qry1)


def Student_Address(uniq_identify):
	StudentAddress.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = list(StudentAddress.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values('uniq_id', 'p_add1', 'p_add2', 'p_city', 'p_district', 'p_pincode', 'c_add1', 'c_add2', 'c_city', 'c_district', 'c_city', 'c_pincode', 'c_state__value', 'p_state__value', 'c_state_id', 'p_state_id'))
	for key, value in qry1[0].items():
		if (qry1[0][key] == None or qry1[0][key] == "0" or qry1[0][key] == ''):
			qry1[0][key] = "----"
	return list(qry1)


def Student_Document(uniq_identify):
	StudentDocument.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = list(StudentDocument.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values())
	# for key,value in qry1[0].items():
	#   if (qry1[0][key]==None or qry1[0][key]=="0"):
	#       qry1[0][key]="N/A"
	return list(qry1)


def Student_FamilyDetails(uniq_identify):
	StudentFamilyDetails.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = StudentFamilyDetails.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values()

	f_oc = qry1[0]['father_occupation_id']
	m_oc = qry1[0]['mother_occupation_id']
	for q in qry1:
		q['father_occupation'] = f_oc
		q['mother_occupation'] = m_oc

	return list(qry1)


def Student_OtherDetails(uniq_identify):
	# StudentPrimDetail.objects.get_or_create(uniq_id = StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = StudentPrimDetail.objects.filter(uniq_id=uniq_identify).values('dept_detail__course__value', 'dept_detail__dept', 'dept_detail__course')
	return list(qry1)
#########################################################################


def Registration_From_Header(uniq_id, session_name, session_id):
	data = {}
	# sftp://10.0.0.12:8000/home/kiet/httpdocs/images
	studentSession = generate_session_table_name("studentSession_", session_name)
	qry = list(studentSession.objects.filter(uniq_id=uniq_id).values('uniq_id__batch_from', 'uniq_id__batch_to').distinct())
	if len(qry) > 0:
		data['year_from_to'] = str(qry[0]['uniq_id__batch_from']) + "-" + str(qry[0]['uniq_id__batch_from'] + 1)
		data['batch'] = str(qry[0]['uniq_id__batch_from']) + "-" + str(qry[0]['uniq_id__batch_to'])
		data['uniq_id'] = uniq_id
		qry1 = list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('dept_detail__course__value', 'dept_detail__dept__value', 'gen_rank', 'exam_roll_no', 'general_rank', 'category_rank', 'admission_type__value','admission_through__value'))
		if (qry1[0]['admission_type__value'] == 'FIRST YEAR'):
			data['semester'] = 'FIRST'
		else:
			data['semester'] = 'THIRD'
		data['admission_type'] = qry1[0]['admission_through__value']
		data['course'] = qry1[0]['dept_detail__course__value']
		data['branch'] = qry1[0]['dept_detail__dept__value']
		data['upsee_roll_no'] = qry1[0]['exam_roll_no']
		data['general_rank'] = qry1[0]['general_rank']
		data['category_rank'] = qry1[0]['category_rank']
		data['header_image'] = settings.BASE_URL2 + "/KIET_Header.png"
		qry3 = list(Semtiming.objects.filter(uid=session_id).values_list('session', flat=True))
		sem_odd = list(Semtiming.objects.filter(session=qry3[0], sem_type='odd').values('uid'))
		qry4 = list(StudentAcademic.objects.filter(uniq_id=uniq_id).values('app_no'))
		session_id = sem_odd[0]['uid']
		residential_status = SubmitFee.objects.filter(cancelled_status='N', uniq_id=uniq_id, status='INSERT', fee_rec_no__contains='H', session=session_id).exclude(id__in=RefundFee.objects.values_list('fee_id', flat=True)).exclude(status__contains='DELETE').values()
		data['application_number'] = qry4[0]['app_no']
		if(len(residential_status) > 0):
			data['HOSTEL_ACCOMODATION'] = 'YES'
		else:
			data['HOSTEL_ACCOMODATION'] = 'NO'
		for key, value in data.items():
			if (data[key] == None or data[key] == "0"):
				data[key] = "N/A"

		return data
	else:
		data = statusMessages.CUSTOM_MESSAGE('Please check the session selected')
		return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT)


def Student_Registration_Form_Document(uniq_identify):
	data = {}
	StudentDocument.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = list(StudentDocument.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values('father_pic', 'mother_pic'))
	StudentPerDetail.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry2 = list(StudentPerDetail.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values('image_path'))
	try:
		data['father_pic'] = settings.BASE_URL2 + "StudentMusterroll/Family_images/" + qry1[0]['father_pic']
	except:
		data['father_pic'] = qry1[0]['father_pic']
	try:
		data['mother_pic'] = settings.BASE_URL2 + "StudentMusterroll/Family_images/" + qry1[0]['mother_pic']
	except:
		data['mother_pic'] = qry1[0]['mother_pic']

	try:
		data['student_pic'] = settings.BASE_URL2 + "StudentMusterroll/Student_images/" + qry2[0]['image_path']
	except:
		data['student_pic'] = qry2[0]['image_path']
	for key, value in data.items():
		if (data[key] == None or data[key] == "0"):
			data[key] = "N/A"
	return data
	# src= settings.BASE_URL2 + "/StudentMusterroll/Student_images/Student_images_92905735.jpeg"


# def Student_Registration_Form_Sub_Header_Details(uniq_id, session_name):
#     data = {}
#     student_session = generate_session_table_name("studentSession_", session_name)
#     qry1 = StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values('uniq_id__name', 'father_occupation__value', 'father_income', 'father_dept', 'father_dept', 'mother_occupation__value', 'mother_dept', 'mother_income', 'father_mob', 'mother_mob')
#     qry2 = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname', 'dob', 'mname', 'caste_name', 'religion__value', 'aadhar_num', 'physically_disabled')
#     qry3 = StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('email_id', 'gender__value')
#     qry4 = student_session.objects.filter(uniq_id=uniq_id).values('mob')
#     data.update(qry1[0])
#     data.update(qry2[0])
#     data.update(qry3[0])
#     data.update(qry4[0])
#     for key, value in data.items():
#         if (data[key] == None or data[key] == "0"):
#             data[key] = "N/A"
#     return data

def Student_Registration_Form_Sub_Header_Details(uniq_id, session_name):
	data = {}
	student_session = generate_session_table_name("studentSession_", session_name)
	qry1 = StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values('uniq_id__name', 'father_occupation__value', 'father_income', 'father_dept', 'father_dept', 'mother_occupation__value', 'mother_dept', 'mother_income', 'father_mob', 'mother_mob')
	qry2 = StudentPerDetail.objects.filter(uniq_id=uniq_id).values('fname', 'dob', 'mname', 'caste_name', 'religion__value', 'aadhar_num', 'physically_disabled')
	qry3 = StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('email_id', 'gender__value', 'caste__value').annotate(caste_name=F('caste__value'))
	qry4 = student_session.objects.filter(uniq_id=uniq_id).values('mob')
	if len(qry1) > 0:
		data.update(qry1[0])
	if len(qry2) > 0:
		data.update(qry2[0])
	if len(qry3) > 0:
		data.update(qry3[0])
	if len(qry4) > 0:
		data.update(qry4[0])
	for key, value in data.items():
		if (data[key] == None or data[key] == "0"):
			data[key] = "N/A"
	return data


def Student_Registration_Form_FamilyDetails(uniq_identify):
	StudentFamilyDetails.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = list(StudentFamilyDetails.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values('father_dept', 'father_city', 'father_pan_no', 'mother_dept', 'mother_city', 'mother_pan_no', 'father_add', 'mother_add'))
	for key, value in qry1[0].items():
		if (qry1[0][key] == None or qry1[0][key] == "0"):
			qry1[0][key] = "N/A"
	return list(qry1)


def Student_Registration_Form_Guardian_Details(uniq_identify):
	StudentFamilyDetails.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = list(StudentFamilyDetails.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values('gname', 'g_relation', 'g_mob', 'g_email', 'g_add', 'g_city', 'g_pincode', 'g_state', 'g_state__value'))
	for key, value in qry1[0].items():
		if (qry1[0][key] == None or qry1[0][key] == "0" or qry1[0][key] == ''):
			qry1[0][key] = "N/A"
	return list(qry1)


def Student_Registration_Form_Academic_Details(uniq_identify):
	data = []
	data.append({})
	i = 0
	StudentAcademic.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = list(StudentAcademic.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values('year_10', 'per_10', 'max_10', 'total_10', 'board_10__value', 'year_12', 'per_12', 'max_12', 'total_12', 'board_12__value', 'uni_dip', 'is_dip', 'year_dip', 'per_dip', 'max_dip', 'total_dip', 'year_ug', 'per_ug', 'total_ug', 'max_ug', 'ug_area', 'ug_degree', 'uni_ug', 'uni_ug__value'))

	for key, value in qry1[0].items():
		if (qry1[0][key] == None or qry1[0][key] == "0" or qry1[0][key] == 0):
			qry1[0][key] = "N/A"
	data[i]['High_School'] = []
	try:
		data[i]['High_School'].append({'year': qry1[0]['year_10'], 'per': 100 * (qry1[0]['total_10'] / qry1[0]['max_10']), 'obtained': qry1[0]['total_10'], 'total': qry1[0]['max_10'], 'board': qry1[0]['board_10__value']})
	except:
		data[i]['High_School'].append({'year': qry1[0]['year_10'], 'per': qry1[0]['per_10'], 'obtained': qry1[0]['total_10'], 'total': qry1[0]['max_10'], 'board': qry1[0]['board_10__value']})
	print(qry1[0]['year_dip'], qry1, "print")
	if qry1[0]['year_dip'] is None or qry1[0]['year_dip'] is "N/A":
		print("1")
		data[i]['Intermediate'] = []
		try:
			data[i]['Intermediate'].append({'year': qry1[0]['year_12'], 'per': qry1[0]['per_12'], 'obtained': qry1[0]['total_12'], 'total': qry1[0]['max_12'], 'board': qry1[0]['board_12__value']})

		except:
			data[i]['Intermediate'].append({'year': qry1[0]['year_12'], 'per': qry1[0]['per_12'], 'obtained': qry1[0]['total_12'], 'total': qry1[0]['max_12'], 'board': qry1[0]['board_12__value']})

	else:
		print("2")
		data[i]['B.Sc/Diploma'] = []
		data[i]['B.Sc/Diploma'].append({'year': qry1[0]['year_dip'], 'per': qry1[0]['per_dip'], 'obtained': qry1[0]['total_dip'], 'total': qry1[0]['max_dip'], 'board': qry1[0]['uni_dip']})

	if qry1[0]['year_ug'] != None and qry1[0]['year_ug'] != "N/A" and qry1[0]['year_ug'] != 0:
		data[i]['Graduation'] = []
		data[i]['Graduation'].append({'year': qry1[0]['year_ug'], 'per': qry1[0]['per_ug'], 'obtained': qry1[0]['total_ug'], 'total': qry1[0]['max_ug'], 'board': qry1[0]['uni_ug__value'], 'area': qry1[0]['ug_area'], 'degree': qry1[0]['ug_degree']})

	for key, value in data[0].items():
		if (data[0][key] == None):
			data[0][key] = "N/A"
	return data


def Student_Registration_Form_GATE_Details(uniq_id):
	data = {}
	qry1 = list(StudentAcademic.objects.filter(uniq_id=uniq_id).values('is_gate_or_gpat', 'gate_or_gpat_rank', 'gate_or_gpat_year', 'gate_or_gpat_discipline', 'gate_or_gpat_score', 'gate_or_gpat_qualified'))

	for key, value in qry1[0].items():
		if (qry1[0][key] == None):
			qry1[0][key] = "N/A"

	return qry1


def Student_Registration_Form_Marks_12(uniq_identify):
	qry1 = []
	qry1.append({})
	StudentAcademic.objects.get_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify))
	qry1 = list(StudentAcademic.objects.filter(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_identify)).values('phy_12', 'phy_max', 'chem_12', 'chem_max', 'math_12', 'math_max', 'bio_12', 'bio_max','cs_12','cs_max', 'year_dip'))
	if qry1[0]['year_dip'] == None:
		if qry1[0]['math_12'] != None and qry1[0]['phy_12'] != None and qry1[0]['chem_12'] != None:
			qry1[0]['obtained'] = qry1[0]['math_12'] + qry1[0]['phy_12'] + qry1[0]['chem_12']
			qry1[0]['total'] = qry1[0]['math_max'] + qry1[0]['phy_max'] + qry1[0]['chem_max']
			qry1[0]['per'] = round(qry1[0]['obtained'] / qry1[0]['total'], 2) * 100
		else:
			try:
				qry1[0]['obtained'] = qry1[0]['bio_12'] + qry1[0]['phy_12'] + qry1[0]['chem_12']
				qry1[0]['total'] = qry1[0]['bio_max'] + qry1[0]['phy_max'] + qry1[0]['chem_max']
				qry1[0]['per'] = round(qry1[0]['obtained'] / qry1[0]['total'], 2) * 100
			except:
				qry1[0]['math_12'] = 'N/A'
				qry1[0]['bio_12'] = 'N/A'
				qry1[0]['chem_12'] = 'N/A'
				qry1[0]['phy_12'] = 'N/A'
				qry1[0]['cs_12'] = 'N/A'
				qry1[0]['per'] = 'N/A'
				qry1[0]['obtained'] = 'N/A'
				qry1[0]['total'] = 'N/A'
		for key, value in qry1[0].items():
			if (qry1[0][key] == None or qry1[0][key] == "0"):
				qry1[0][key] = "N/A"

	else:
		qry1[0]['math_12'] = 'N/A'
		qry1[0]['bio_12'] = 'N/A'
		qry1[0]['chem_12'] = 'N/A'
		qry1[0]['phy_12'] = 'N/A'
		qry1[0]['cs_12'] = 'N/A'
		qry1[0]['per'] = 'N/A'
		qry1[0]['obtained'] = 'N/A'
		qry1[0]['total'] = 'N/A'

	return qry1


# def Student_Registration_Form_FeeDetails(uniq_identify,session):
#   data={}
#   ids = SubmitFee.objects.filter(uniq_id=uniq_identify,session=session).exclude(cancelled_status='Y').exclude(status='DELETE').exclude(fee_rec_no__contains='H').values_list('id',flat=True)
#   if ids:
#       query = list(SubmitFeeComponentDetails.objects.filter(fee_id__in=ids).values('fee_component__value','fee_id').distinct())
#   if query:
#       for q in query:

#           qry = list(SubmitFee.objects.filter(uniq_id=uniq_identify,session=session,id=q['fee_id']).exclude(cancelled_status='Y').exclude(status='DELETE').values('id','actual_fee','paid_fee','refund_value','due_value','fee_rec_no','time_stamp'))
#           if qry:
#               qry1 = list(ModeOfPaymentDetails.objects.filter(fee_id=qry[0]['id'],MOPcomponent__value='DEMAND DRAFT').values('MOPcomponent__field','value','MOPcomponent__field'))
#               data[q['fee_component__value']]=qry
#           else:
#               data[q['fee_component__value']]={'id':None,'actual_fee':None,'paid_fee':None,'refund_value':None,'due_value':None,'fee_rec_no':None,'time_stamp':None}
#           if qry1:
#               data['DD']=qry1
#           else:
#               data['DD']=[]
#               data['DD'].append({'MOPcomponent__value':None,'value':None,'MOPcomponent__field':None})

#       qry2=SubmitFee.objects.filter(uniq_id=uniq_identify,session=session).exclude(cancelled_status='Y').exclude(status='DELETE').exclude(fee_rec_no__contains='A').values('id','actual_fee','paid_fee','refund_value','due_value','fee_rec_no','time_stamp')
#       if qry2:
#           qry3 = list(ModeOfPaymentDetails.objects.filter(fee_id=qry2[0]['id'],MOPcomponent__value='DEMAND DRAFT').values('MOPcomponent__value','value','MOPcomponent__field'))
#           data['hostel1']=qry2
#       else:

#       if qry3:
#           data['hostel2']=qry3
#   return data
####################################################################################
# /////////////////////// complete detail of student USING unique ID  ///////////// END ///////////////
def get_students_added(branch, batch):
	qry1 = StudentPrimDetail.objects.filter(dept_detail__uid__in=branch, batch_from=batch).values('uniq_id', 'name', 'uni_roll_no')
	for q in qry1:
		if q['uni_roll_no'] is not None and q['uni_roll_no'] != '':
			q['bracket_val'] = q['uni_roll_no']
		else:
			q_per = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('aadhar_num')
			if(q_per is not None and q_per != '' and len(q_per) > 0):
				q['bracket_val'] = q_per[0]['aadhar_num']
			else:
				q['bracket_val'] = "NOT MENTIONED"

	return list(qry1)


def get_students(section, session_name):
	student_session = generate_session_table_name("studentSession_", session_name)

	qry_select_stu = student_session.objects.filter(section_id=section).exclude(section__status="DELETE").exclude(uniq_id__in=student_session.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no', 'year', 'sem__dept__dept__value', 'sem__dept__course__value', 'section__section', 'sem__sem', 'uniq_id__admission_status__value', 'uniq_id__join_year', 'uniq_id__gender__value').order_by('uniq_id__name')
	for q in qry_select_stu:
		if q['uniq_id__uni_roll_no'] is not None and q['uniq_id__uni_roll_no'] != '':
			q['bracket_val'] = q['uniq_id__uni_roll_no']
		else:
			q_per = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('aadhar_num')
			if(q_per is not None and q_per != ''):
				q['bracket_val'] = q_per[0]['aadhar_num']
			else:
				q['bracket_val'] = "NOT MENTIONED"
	return list(qry_select_stu)


def get_students2(section, session_name):
	student_session = generate_session_table_name("studentSession_", session_name)

	qry_select_stu = student_session.objects.filter(section_id__in=section).exclude(section__status="DELETE").exclude(uniq_id__in=student_session.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED")).values_list('uniq_id', flat=True)).values('uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no', 'year', 'sem__dept__dept__value', 'sem__dept__course__value', 'section__section', 'sem__sem', 'uniq_id__admission_status__value', 'uniq_id__join_year', 'uniq_id__gender__value').order_by('uniq_id__name')
	for q in qry_select_stu:
		if q['uniq_id__uni_roll_no'] is not None and q['uniq_id__uni_roll_no'] != '':
			q['bracket_val'] = q['uniq_id__uni_roll_no']
		else:
			q_per = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('aadhar_num')
			if(q_per is not None and q_per != ''):
				q['bracket_val'] = q_per[0]['aadhar_num']
			else:
				q['bracket_val'] = "NOT MENTIONED"
	return list(qry_select_stu)
# //////////////////////////// Onchange requests//////////////////////////


def onchange_fields(request):
	data = {'msg': "", 'data': ''}
	msg = ''
	status = 200
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			session_name = request.session['Session_name']
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'PUT':
					body = json.loads(request.body)
					# print(body)
					if request.GET['request_type'] == 'branch':
						data['data'] = get_branch(body['branch'])
					elif request.GET['request_type'] == 'semester':
						data['data'] = get_semester(body['semester'])
					elif request.GET['request_type'] == 'section':
						data['data'] = get_section(body['section'])
					elif request.GET['request_type'] == 'students':
						data['data'] = get_students(body['section'], session_name)
					elif request.GET['request_type'] == 'semester_year_1':
						query = StudentSemester.objects.filter(dept=body['semester_year_1']).exclude(sem__isnull=True).values("sem", "sem_id", 'dept__course__value')
						print(query)
						if(query[0]['dept__course__value'] == "B.TECH"):
							qry = StudentSemester.objects.filter(dept__dept__value='AS').exclude(sem__isnull=True).values("sem", "sem_id", 'dept__course__value')
							data['data'] = list(qry)
						else:
							data['data'] = get_semester(body['semester_year_1'])

					msg = "Successfully"
				else:
					status = 500
					msg = "request error"
			else:
				status = 500
				msg = "permission error"
	else:
		status = 500
		msg = "AuthUser Error"
	data['msg'] = msg
	return JsonResponse(data=data, status=status)


def getComponents(request):
	data = {'msg': "", 'data': ''}
	msg = ''
	status = 200
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			session_name = request.session['Session_name']
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					print(request.GET)
					if request.GET['request_type'] == 'branch':
						data['data'] = get_branch(request.GET['branch'])
					elif request.GET['request_type'] == 'semester':
						data['data'] = get_semester(request.GET['semester'])
					elif request.GET['request_type'] == 'section':
						data['data'] = get_section(request.GET['section'])
					elif request.GET['request_type'] == 'students':
						data['data'] = get_students2(str(request.GET['section']).split(','), session_name)

					msg = "Successfully"
				else:
					status = 500
					msg = "request error"
			else:
				status = 500
				msg = "permission error"
	else:
		status = 500
		msg = "AuthUser Error"
	data['msg'] = msg
	return JsonResponse(data=data, status=status)
# //////////////////////////////////////////Get DAta for update////////////////


def get_student(request):
	data = {}
	qry1 = []
	msg = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'POST':
					body = json.loads(request.body)
					print(body)
					if request.GET['for'] == "branch":
						qry = CourseDetail.objects.filter(course_id__in=body).exclude(dept_id__value='AS').values("uid", "dept_id__value", "course_duration")
						msg = "Success"
						status = 200
						data = {'data': list(qry)}
					elif request.GET['for'] == "fetch_student":
						dept_detail_select = body['dept_detail_select']
						batch_from_select = body['batch_from_select']
						print(dept_detail_select, batch_from_select)
						qry1 = get_students_added(dept_detail_select, batch_from_select)
						msg = "Success"
						if not qry1:
							msg = "No Data Found"
						status = 200
						data = {'data': list(qry1)}
				elif request.method == 'PUT':
					# body = json.loads(request.body)
					qry1 = get_gender()
					qry2 = get_caste()
					qry3 = get_status()
					qry4 = get_through()
					qry5 = get_admission_type()
					qry6 = get_exam_type()
					qry7 = get_course()
					# qry8 = get_admission_category()
					qry9 = get_nation()
					qry10 = get_religion()
					qry11 = get_category()
					qry12 = get_board()
					qry13 = get_universities()
					qry14 = get_degree()
					qry15 = get_bg()
					qry16 = get_marital_status()
					qry17 = get_state()
					qry18 = get_occupation()
					msg = "Success"
					error = False
					status = 200
					data = {
						'admission_through': list(qry4),
						'admission_type': list(qry5),
						'exam_type': list(qry6),
						'course': list(qry7),
						'student_status': list(qry3),
						'admission_category': list(qry11),
						'gender': list(qry1),
						'religion': list(qry10),
						'caste': list(qry2),
						'nationality': list(qry9),
						'bg': list(qry15),
						'marital_status': list(qry16),
						'father_occupation': list(qry18),
						'mother_occupation': list(qry18),
						'p_state': list(qry17),
						'c_state': list(qry17),
						'board_10': list(qry12),
						'University': list(qry13),
						'Degree': list(qry14)
					}
					# data = {'data1':list(qry1),'data2':list(qry2),'data3':list(qry3),'data4':list(qry4),'data5':list(qry5),'data6':list(qry6),'data7':list(qry7),'data8':list(qry8),'data9':list(qry9),'data10':list(qry10),'data11':list(qry11),'data12':list(qry12),'data13':list(qry13),'data14':list(qry14)}
					msg = "Successfully"
				else:
					status = 500
					msg = "request error"
			else:
				status = 500
				msg = "permission error"
	else:
		status = 500
		msg = "AuthUser Error"
	data['msg'] = msg
	return JsonResponse(data=data, status=status)


def pre_student(request):

	data = []
	status = 200
	msg = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'PUT' and request.GET['request_type'] == 'already_filled':
					body = json.loads(request.body)
					session_name = request.session['Session_name']
					# uniq_id = body['uniq_id']

					uniq_id = body['uniq_id']
					print(uniq_id)
					data.append({'StudentPrimDetail': Student_PrimDetail(uniq_id)})
					data.append(Student_Session(uniq_id, session_name))
					data.append({'StudentPerDetail': StudentPerDetail_fun(uniq_id)})
					data.append({'StudentAcademic': Student_Academics(uniq_id)})
					data.append({'StudentAddress': Student_Address(uniq_id)})
					data.append({'StudentDocument': Student_Document(uniq_id)})
					print(Student_Document(uniq_id))
					data.append({'StudentFamilyDetails': Student_FamilyDetails(uniq_id)})
					data.append({'StudentOtherDetails': Student_OtherDetails(uniq_id)})

					msg = "Successfully"
					status = 200
				else:
					status = 500
					msg = "request error"
			else:
				status = 500
				msg = "permission error"
	else:
		status = 500
		msg = "AuthUser Error"
	data.append({'msg': msg})
	return JsonResponse(data=list(data), status=status, safe=False)


def update_student(request):
	data = {}
	qry1 = []
	status = 200
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'PUT':
					if request.GET['request_type'] == 'update_student':
						session_name = request.session['Session_name']

						body = json.loads(request.body)
						Uniq_Id = body['uniq_id']
						# print(body["dob"])
						dob = datetime.now().date()
						StudentPerDetail.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=Uniq_Id), defaults={'dob': dob})

						# ///////////////////////////////////////////////////////TO SET SESSION TO LATEST///////////////////////////////////////////////////////////

						student_session = generate_session_table_name("studentSession_", session_name)

						# ////////////////////////////////////////////////////////TO SET SESSION TO LATEST///////////////////////////////////////////////////////////
						# //////////////////////////////////////////////////////START FOR PRIM & PER////////////////////////////////////////////////////////////
						fname = body["fname"].upper()
						if body["caste_id"] is None:
							caste_id = None
						else:
							caste_id = StudentDropdown.objects.get(sno=body["caste_id"])
						if body["gender_id"] is None:
							gender_id = None
						else:
							gender_id = StudentDropdown.objects.get(sno=body["gender_id"])
						if body["religion_id"] is None:
							religion_id = None
						else:
							religion_id = EmployeeDropdown.objects.get(sno=body["religion_id"])
						aadhar_num = body["aadhar_num"]
						# ////////////////////////////////////START OF DOB////////////////////////////////////////////
						# dober=body["dob"]
						# dob=dober.split('T')
						dob = datetime.strptime(str(body["dob"]).split('T')[0], "%Y-%m-%d").date()
						# /////////////////////////////////////END OF DOB///////////////////////////////////////////
						image_path = body['image_path']
						mname = body["mname"].upper()
						if body["nationality_id"] is None:
							nationality_id = None
						else:
							nationality_id = EmployeeDropdown.objects.get(sno=body["nationality_id"])
						nation_other = body["nation_other"]
						general_rank = body["general_rank"]
						category_rank = body["category_rank"]
						mob_sec = body["mob_sec"]
						gen_rank = body["gen_rank"]
						exam_roll_no = body["exam_roll_no"]
						uni_roll_no = body["uni_roll_no"]
						remark_detail = body['remark_detail']

						if body["bg_id"] is None:
							bg = None
						else:
							bg = EmployeeDropdown.objects.get(sno=body['bg_id'])
						if body["marital_status_id"] is None:
							marital_status = None
						else:
							marital_status = EmployeeDropdown.objects.get(sno=body['marital_status_id'])
						if body["admission_category_id"] is None:
							admission_category_id = None
						else:
							admission_category_id = StudentDropdown.objects.get(sno=body["admission_category_id"])
						if body["admission_status_id"] is None:
							admission_status_id = None
						else:
							admission_status_id = StudentDropdown.objects.get(sno=body["admission_status_id"])
						if body["admission_through_id"] is None:
							admission_through_id = None
						else:
							admission_through_id = StudentDropdown.objects.get(sno=body["admission_through_id"])

						if body["dept_detail_id"] is None:
							dept_detail_id = None
						else:
							dept_detail_id = CourseDetail.objects.get(uid=body["dept_detail_id"])

						fee_waiver = body['fee_waiver']
						batch_from = body["batch_from"]
						email_id = body["email_id"]
						date_of_add = body["date_of_add"]
						batch_to = body["batch_to"]
						name = body["name"].upper()
						remark = body["remark"]
						physically_disabled = body["physically_disabled"]
						caste_name = body["caste_name"]
						image_path = body["image_path"]
						# /////////////////////////////////////////////////END FOR PRIM & PER/////////////////////////////////////////////////////////////////////
						# /////////////////////////////////////////////////START FOR FAMILY/////////////////////////////////////////////////////////////////////
						sem_id_id = StudentSemester.objects.get(sem_id=body["sem_id"])
						year = body["year"]
						if body["section_id_id"] is not None:
							section_id_id = Sections.objects.get(section_id=body["section_id_id"])
						else:
							section_id_id = body['section_id_id']
						session = body["session"]
						if body["exam_type_id"] is None:
							exam_type_id = None
						else:
							exam_type_id = StudentDropdown.objects.get(sno=body["exam_type_id"])
						if body["admission_type_id"] is None:
							admission_type_id = None
						else:
							admission_type_id = StudentDropdown.objects.get(sno=body["admission_type_id"])
						# /////////////////////////////////////////////////END FOR ACADEMIC/////////////////////////////////////////////////////////////////////
						# /////////////////////////////////////////////////START FOR FAMILY/////////////////////////////////////////////////////////////////////
						father_income = body["father_income"]
						father_mob = body["father_mob"]
						if body["father_occupation"] is None:
							father_occupation = None
						else:
							father_occupation = StudentDropdown.objects.get(sno=body["father_occupation"])
						father_email = body["father_email"]
						father_city = body["father_city"]
						father_dept = body["father_dept"]
						father_add = body["father_add"]
						father_pan_no = body["father_pan"]
						father_uan_no = body["father_aadhar"]
						mother_income = body["mother_income"]
						mother_dept = body["mother_dept"]
						mother_add = body["mother_add"]
						if body["mother_occupation"] is None:
							mother_occupation = None
						else:
							mother_occupation = StudentDropdown.objects.get(sno=body["mother_occupation"])
						mother_city = body["mother_city"]
						mother_email = body["mother_email"]
						mother_mob = body["mother_mob"]
						mother_pan_no = body["mother_pan"]
						mother_uan_no = body["mother_aadhar"]
						g_city = body["g_city"]
						g_mob = body["g_mob"]
						g_email = body["g_email"]
						g_relation = body["g_relation"]
						gname = body["gname"]
						g_add = body["g_add"]
						g_pincode = body["g_pincode"]
						g_state = body["g_state"]
						if g_state is not None:
							g_state = EmployeeDropdown.objects.get(sno=g_state)
						# /////////////////////////////////////////////////END FOR FAMILY/////////////////////////////////////////////////////////////////////
						# /////////////////////////////////////////////////START FOR ADDRESS/////////////////////////////////////////////////////////////////////
						p_state_id = EmployeeDropdown.objects.get(sno=body['p_state_id'])
						p_city = body['p_city']
						p_district = body['p_district']
						p_add2 = body['p_add2']
						p_pincode = body['p_pincode']
						p_add1 = body['p_add1']
						c_city = body['c_city']
						c_district = body['c_district']
						if body["c_state_id"] is None:
							c_state_id = None
						else:
							c_state_id = EmployeeDropdown.objects.get(sno=body['c_state_id'])
						c_pincode = body['c_pincode']
						c_add2 = body['c_add2']
						c_add1 = body['c_add1']
						# /////////////////////////////////////////////////END FOR ADDRESS/////////////////////////////////////////////////////////////////////
						# /////////////////////////////////////////////////START FOR ACADEMIC/////////////////////////////////////////////////////////////////////

						area_dip = body["area_dip"]
						bio_12 = body["bio_12"]
						bio_max = body["bio_max"]
						cs_12 = body["cs_12"]
						cs_max = body["cs_max"]
						if body['board_10_id'] is not None:
							board_10_id = EmployeeDropdown.objects.get(sno=body["board_10_id"])
						else:
							board_10_id = None

						if body['board_12_id'] is not None:
							board_12_id = EmployeeDropdown.objects.get(sno=body["board_12_id"])
						else:
							board_12_id = None
						chem_12 = body["chem_12"]
						chem_max = body["chem_max"]
						eng_12 = body["eng_12"]
						eng_max = body["eng_max"]
						is_dip = body["is_dip"]
						math_12 = body["math_12"]
						math_max = body["math_max"]
						max_10 = body["max_10"]
						max_12 = body["max_12"]
						max_dip = body["max_dip"]
						max_ug = body["max_ug"]
						pcm_total = body["pcm_total"]
						per_10 = body["per_10"]
						per_12 = body["per_12"]
						per_dip = body["per_dip"]
						per_pg = body["per_pg"]
						per_ug = body["per_ug"]
						pg_area = body["pg_area"]
						pg_degree = body["pg_degree"]
						pg_year1 = body["pg_year1"]
						pg_year1_back = body["pg_year1_back"]
						pg_year1_max = body["pg_year1_max"]
						pg_year2 = body["pg_year2"]
						pg_year2_back = body["pg_year2_back"]
						pg_year2_max = body["pg_year2_max"]
						pg_year3 = body["pg_year3"]
						pg_year3_back = body["pg_year3_back"]
						pg_year3_max = body["pg_year3_max"]
						phy_12 = body["phy_12"]
						phy_max = body["phy_max"]
						sem1_pg = body["sem1_pg"]
						sem1_pg_back = body["sem1_pg_back"]
						sem1_pg_max = body["sem1_pg_max"]
						sem1_ug = body["sem1_ug"]
						sem1_ug_back = body["sem1_ug_back"]
						sem1_ug_max = body["sem1_ug_max"]
						sem2_pg = body["sem2_pg"]
						sem2_pg_back = body["sem2_pg_back"]
						sem2_pg_max = body["sem2_pg_max"]
						sem2_ug = body["sem2_ug"]
						sem2_ug_back = body["sem2_ug_back"]
						sem2_ug_max = body["sem2_ug_max"]
						sem3_pg = body["sem3_pg"]
						sem3_pg_back = body["sem3_pg_back"]
						sem3_pg_max = body["sem3_pg_max"]
						sem3_ug = body["sem3_ug"]
						sem3_ug_back = body["sem3_ug_back"]
						sem3_ug_max = body["sem3_ug_max"]
						sem4_pg = body["sem4_pg"]
						sem4_pg_back = body["sem4_pg_back"]
						sem4_pg_max = body["sem4_pg_max"]
						sem4_ug = body["sem4_ug"]
						sem4_ug_back = body["sem4_ug_back"]
						sem4_ug_max = body["sem4_ug_max"]
						sem5_pg = body["sem5_pg"]
						sem5_pg_back = body["sem5_pg_back"]
						sem5_pg_max = body["sem5_pg_max"]
						sem5_ug = body["sem5_ug"]
						sem5_ug_back = body["sem5_ug_back"]
						sem5_ug_max = body["sem5_ug_max"]
						sem6_pg = body["sem6_pg"]
						sem6_pg_back = body["sem6_pg_back"]
						sem6_pg_max = body["sem6_pg_max"]
						sem6_ug = body["sem6_ug"]
						sem6_ug_back = body["sem6_ug_back"]
						sem6_ug_max = body["sem6_ug_max"]
						sem7_ug = body["sem7_ug"]
						sem7_ug_back = body["sem7_ug_back"]
						sem7_ug_max = body["sem7_ug_max"]
						sem8_ug = body["sem8_ug"]
						sem8_ug_back = body["sem8_ug_back"]
						sem8_ug_max = body["sem8_ug_max"]
						total_10 = body["total_10"]
						total_12 = body["total_12"]
						total_dip = body["total_dip"]
						total_ug = body["total_ug"]
						ug_area = body["ug_area"]
						ug_degree = body["ug_degree"]
						ug_year1 = body["ug_year1"]
						ug_year1_back = body["ug_year1_back"]
						ug_year1_max = body["ug_year1_max"]
						ug_year2 = body["ug_year2"]
						ug_year2_back = body["ug_year2_back"]
						ug_year2_max = body["ug_year2_max"]
						ug_year3 = body["ug_year3"]
						ug_year3_back = body["ug_year3_back"]
						ug_year3_max = body["ug_year3_max"]
						ug_year4 = body["ug_year4"]
						ug_year4_back = body["ug_year4_back"]
						ug_year4_max = body["ug_year4_max"]
						is_gate_or_gpat = body["is_gate_or_gpat"]
						gate_or_gpat_rank = body["gate_or_gpat_rank"]
						gate_or_gpat_year = body["gate_or_gpat_year"]
						gate_or_gpat_discipline = body["gate_or_gpat_discipline"]
						gate_or_gpat_score = body["gate_or_gpat_score"]
						gate_or_gpat_qualified = body["gate_or_gpat_qualified"]
						##################################################################

						if body["uni_dip_id"] is not None:
							uni_dip_id = EmployeeDropdown.objects.get(sno=body["uni_dip_id"])
						else:
							uni_dip_id = body["uni_dip_id"]
						if body["uni_pg_id"] is not None:
							uni_pg_id = EmployeeDropdown.objects.get(sno=body["uni_pg_id"])
						else:
							uni_pg_id = body["uni_pg_id"]
						if body["uni_ug_id"] is not None:
							uni_ug_id = EmployeeDropdown.objects.get(sno=body["uni_ug_id"])
						else:
							uni_ug_id = body["uni_ug_id"]

						##################################################################

						# if body["ug_degree"] is not None:
						#   ug_degree=EmployeeDropdown.objects.get(sno= body["ug_degree"])
						# else:
						#   ug_degree=body["ug_degree"]

						# if body["pg_degree"] is not None:
						#   pg_degree=EmployeeDropdown.objects.get(sno=body["pg_degree"])
						# else:
						#   pg_degree=body["pg_degree"]

						##################################################################

						year_10 = body["year_10"]
						year_12 = body["year_12"]
						year_dip = body["year_dip"]
						year_pg = body["year_pg"]
						year_ug = body["year_ug"]
						# /////////////////////////////////////////////////END FOR ACADEMIC/////////////////////////////////////////////////////////////////////
						# /////////////////////////////////////////////////END FOR DOCUMENT/////////////////////////////////////////////////////////////////////
						marksheet_10 = body['marksheet_10']
						marksheet_12 = body['marksheet_12']
						marksheet_dip = body['marksheet_dip']
						marksheet_ug = body['marksheet_ug']
						addressid = body['addressid']
						domicile_certificate = body['domicile_certificate']
						allot_letter = body['allot_letter']
						caste_certificate = body['caste_certificate']
						guardian_pic = body['guardian_pic']
						mother_pic = body['mother_pic']
						father_pic = body['father_pic']

						uniqid = StudentPrimDetail.objects.get(uniq_id=Uniq_Id)
						# Uniq_Id = StudentPrimDetail.objects.get(uniq_id=Uniq_Id)

						# /////////////////////////////////////////////////END FOR DOCUMENT/////////////////////////////////////////////////////////////////////
						StudentAddress.objects.update_or_create(uniq_id=Uniq_Id, defaults={'p_state': p_state_id, 'p_city': p_city, 'p_district': p_district, 'p_add2': p_add2, 'p_pincode': p_pincode, 'p_add1': p_add1, 'c_city': c_city, 'c_district': c_district, 'c_state': c_state_id, 'c_pincode': c_pincode, 'c_add2': c_add2, 'c_add1': c_add1, })

						StudentPrimDetail.objects.update_or_create(uniq_id=Uniq_Id, defaults={'uni_roll_no': uni_roll_no, 'remark_detail': remark_detail, 'exam_roll_no': exam_roll_no, 'general_rank': general_rank, 'category_rank': category_rank, 'gen_rank': gen_rank, 'caste': caste_id, 'gender': gender_id, 'admission_category': admission_category_id, 'admission_status': admission_status_id, 'admission_through': admission_through_id, 'dept_detail_id': dept_detail_id, 'fee_waiver': fee_waiver, 'batch_from': batch_from, 'date_of_add': date_of_add, 'batch_to': batch_to, 'remark': remark, 'name': name, 'exam_type': exam_type_id, 'admission_type': admission_type_id, 'email_id': email_id, 'form_fill_status': 'Y'})

						student_session.objects.update_or_create(uniq_id=Uniq_Id, defaults={'sem': sem_id_id, 'year': year, 'section': section_id_id, 'mob': mob_sec})

						StudentAcademic.objects.update_or_create(uniq_id=Uniq_Id, defaults={'area_dip': area_dip, 'bio_12': bio_12, 'bio_max': bio_max,'cs_12':cs_12,'cs_max':cs_max, 'board_10_id': board_10_id, 'board_12_id': board_12_id, 'chem_12': chem_12, 'chem_max': chem_max, 'eng_12': eng_12, 'eng_max': eng_max, 'is_dip': is_dip, 'math_12': math_12, 'math_max': math_max, 'max_10': max_10, 'max_12': max_12, 'max_dip': max_dip, 'max_ug': max_ug, 'pcm_total': pcm_total, 'per_10': per_10, 'per_12': per_12, 'per_dip': per_dip, 'per_pg': per_pg, 'per_ug': per_ug, 'pg_area': pg_area, 'pg_degree': pg_degree, 'pg_year1': pg_year1, 'pg_year1_back': pg_year1_back, 'pg_year1_max': pg_year1_max, 'pg_year2': pg_year2, 'pg_year2_back': pg_year2_back, 'pg_year2_max': pg_year2_max, 'pg_year3': pg_year3, 'pg_year3_back': pg_year3_back, 'pg_year3_max': pg_year3_max, 'phy_12': phy_12, 'phy_max': phy_max, 'sem1_pg': sem1_pg, 'sem1_pg_back': sem1_pg_back, 'sem1_pg_max': sem1_pg_max, 'sem1_ug': sem1_ug, 'sem1_ug_back': sem1_ug_back, 'sem1_ug_max': sem1_ug_max, 'sem2_pg': sem2_pg, 'sem2_pg_back': sem2_pg_back, 'sem2_pg_max': sem2_pg_max, 'sem2_ug': sem2_ug, 'sem2_ug_back': sem2_ug_back, 'sem2_ug_max': sem2_ug_max, 'sem3_pg': sem3_pg, 'sem3_pg_back': sem3_pg_back, 'sem3_pg_max': sem3_pg_max, 'sem3_ug': sem3_ug, 'sem3_ug_back': sem3_ug_back, 'sem3_ug_max': sem3_ug_max, 'sem4_pg': sem4_pg, 'sem4_pg_back': sem4_pg_back, 'sem4_pg_max': sem4_pg_max, 'sem4_ug': sem4_ug, 'sem4_ug_back': sem4_ug_back, 'sem4_ug_max': sem4_ug_max, 'sem5_pg': sem5_pg, 'sem5_pg_back': sem5_pg_back, 'sem5_pg_max': sem5_pg_max, 'sem5_ug': sem5_ug, 'sem5_ug_back': sem5_ug_back, 'sem5_ug_max': sem5_ug_max, 'sem6_pg': sem6_pg, 'sem6_pg_back': sem6_pg_back, 'sem6_pg_max': sem6_pg_max, 'sem6_ug': sem6_ug, 'sem6_ug_back': sem6_ug_back, 'sem6_ug_max': sem6_ug_max, 'sem7_ug': sem7_ug, 'sem7_ug_back': sem7_ug_back, 'sem7_ug_max': sem7_ug_max, 'sem8_ug': sem8_ug, 'sem8_ug_back': sem8_ug_back, 'sem8_ug_max': sem8_ug_max, 'total_10': total_10, 'total_12': total_12, 'total_dip': total_dip, 'total_ug': total_ug, 'ug_area': ug_area, 'ug_degree': ug_degree, 'ug_year1': ug_year1, 'ug_year1_back': ug_year1_back, 'ug_year1_max': ug_year1_max, 'ug_year2': ug_year2, 'ug_year2_back': ug_year2_back, 'ug_year2_max': ug_year2_max, 'ug_year3': ug_year3, 'ug_year3_back': ug_year3_back, 'ug_year3_max': ug_year3_max, 'ug_year4': ug_year4, 'ug_year4_back': ug_year4_back, 'ug_year4_max': ug_year4_max, 'uni_dip_id': uni_dip_id, 'uni_pg_id': uni_pg_id, 'uni_ug_id': uni_ug_id, 'year_10': year_10, 'year_12': year_12, 'year_dip': year_dip, 'year_pg': year_pg, 'year_ug': year_ug, 'is_gate_or_gpat': is_gate_or_gpat, 'gate_or_gpat_rank': gate_or_gpat_rank, 'gate_or_gpat_year': gate_or_gpat_year, 'gate_or_gpat_discipline': gate_or_gpat_discipline, 'gate_or_gpat_score': gate_or_gpat_score, 'gate_or_gpat_qualified': gate_or_gpat_qualified})

						StudentPerDetail.objects.update_or_create(uniq_id=Uniq_Id, defaults={'physically_disabled': physically_disabled, 'caste_name': caste_name, 'bg': bg, 'marital_status': marital_status, 'fname': fname, 'religion': religion_id, 'aadhar_num': aadhar_num, 'dob': dob, 'mname': mname, 'nationality': nationality_id, 'nation_other': nation_other, 'image_path': image_path, })

						StudentFamilyDetails.objects.update_or_create(uniq_id=Uniq_Id, defaults={'father_income': father_income, 'father_mob': father_mob, 'father_occupation': father_occupation, 'father_email': father_email, 'father_city': father_city, 'father_dept': father_dept, 'father_add': father_add, 'father_pan_no': father_pan_no, 'father_uan_no': father_uan_no, 'mother_income': mother_income, 'mother_dept': mother_dept, 'mother_add': mother_add, 'mother_occupation': mother_occupation, 'mother_city': mother_city, 'mother_pan_no': mother_pan_no, 'mother_uan_no': mother_uan_no, 'mother_email': mother_email, 'mother_mob': mother_mob, 'g_city': g_city, 'g_mob': g_mob, 'g_email': g_email, 'g_relation': g_relation, 'gname': gname, 'g_add': g_add, 'g_pincode': g_pincode, 'g_state': g_state})

						StudentDocument.objects.update_or_create(uniq_id=Uniq_Id, defaults={'marksheet_10': marksheet_10, 'marksheet_12': marksheet_12, 'marksheet_dip': marksheet_dip, 'marksheet_ug': marksheet_ug, 'addressid': addressid, 'domicile_certificate': domicile_certificate, 'allot_letter': allot_letter, 'caste_certificate': caste_certificate, 'guardian_pic': guardian_pic, 'mother_pic': mother_pic, 'father_pic': father_pic})

					msg = "Successfully"
				else:
					status = 500
					msg = "request error"
			else:
				status = 500
				msg = "permission error"
	else:
		status = 500
		msg = "AuthUser Error"
	return JsonResponse(data=data, status=status)


def deletec(pid):
	qry = StudentDropdown.objects.filter(pid=pid).exclude(status="DELETE").values('sno')
	if len(qry) > 0:
		for x in qry:
			deletec(x['sno'])
	qry = StudentDropdown.objects.filter(sno=pid).exclude(status="DELETE").update(status="DELETE")


def Student_dropdown(request):
	data = {}
	qry1 = ""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					if request.GET['request_type'] == 'general':
						qry1 = StudentDropdown.objects.filter(value=None).extra(select={'fd': 'field', 'id': 'sno', 'parent': 'pid'}).values('fd', 'id', 'parent').exclude(status="DELETE").distinct()
						for field1 in qry1:
							if field1['parent'] != 0:
								pid = field1['parent']
								qry2 = StudentDropdown.objects.filter(sno=pid).exclude(status="DELETE").values('field')
								field1['fd'] = field1['fd'] + '(' + qry2[0]['field'] + ')'
						msg = "Success"
						error = False
						if not qry1:
							msg = "No Data Found!!"
						status = 200
						data = {'msg': msg, 'data': list(qry1)}

					elif request.GET['request_type'] == 'subcategory':
						sno = request.GET['Sno']
						names = StudentDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('field', 'pid')
						name = names[0]['field']

						#p_id = names[0]['pid']

						p_id = names[0]['pid']

						qry1 = StudentDropdown.objects.filter(field=name, pid=p_id).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'valueid': 'sno', 'parentId': 'pid', 'cat': 'field', 'text1': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('valueid', 'parentId', 'cat', 'text1', 'edit', 'delete')
						for x in range(0, len(qry1)):
							test = StudentDropdown.objects.filter(pid=qry1[x]['valueid']).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'subid': 'sno', 'subvalue': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('subid', 'subvalue', 'edit', 'delete')
							qry1[x]['subcategory'] = list(test)
						msg = "Success"
						data = {'msg': msg, 'data': list(qry1)}
						status = 200

				elif request.method == 'DELETE':
					data = json.loads(request.body)
					qry = StudentDropdown.objects.filter(sno=data['del_id']).exclude(status="DELETE").values('field')
					fd = qry[0]['field']
					if(qry.exists()):

						sno = data['del_id']
						deletec(sno)
						q2 = StudentDropdown.objects.filter(field=fd).exclude(status="DELETE").exclude(value__isnull=True).values().count()
						if q2 == 0:
							q3 = StudentDropdown.objects.filter(field=fd).exclude(status="DELETE").update(status="DELETE")
						msg = "Data Successfully Deleted..."
						status = 200
					else:
						msg = "Data Not Found!"
						status = 404
					data = {'msg': msg}
					status = 200
				elif request.method == 'POST':
					body1 = json.loads(request.body)

					for body in body1:
						pid = body['parentid']
						value = body['val'].upper()
						field_id = body['cat']
						field_qry = StudentDropdown.objects.filter(sno=field_id).exclude(status="DELETE").values('field')
						field = field_qry[0]['field']
						if pid != 0:
							field_qry = StudentDropdown.objects.filter(sno=pid).exclude(status="DELETE").exclude(value__isnull=True).values('value')
							field = field_qry[0]['value']
							cnt = StudentDropdown.objects.filter(field=field).exclude(status="DELETE").values('sno')
							if len(cnt) == 0:
								add = StudentDropdown.objects.create(pid=pid, field=field)

						qry_ch = StudentDropdown.objects.filter(Q(field=field) & Q(value=value)).filter(pid=pid).exclude(status="DELETE")
						if(len(qry_ch) > 0):
							status = 409

						else:
							created = StudentDropdown.objects.create(pid=pid, field=field, value=value)
							msg = "Successfully Inserted"
							data = {'msg': msg}
							status = 200

				elif request.method == 'PUT':
					body = json.loads(request.body)
					sno = body['sno1']
					val = body['val'].upper()
					field_qry = StudentDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('pid', 'value')
					pid = field_qry[0]['pid']
					value = field_qry[0]['value']
					add = StudentDropdown.objects.filter(pid=pid, field=value).exclude(status="DELETE").update(field=val)
					add = StudentDropdown.objects.filter(sno=sno).exclude(status="DELETE").update(value=val, status="UPDATE")
					add = StudentDropdown.objects.filter(pid=sno).exclude(status="DELETE").update(field=val, status="UPDATE")
					msg = "Successfully Updated"
					data = {'msg': msg}
					status = 200

				else:
					status = 403
			else:
				status = 401
		else:
			status = 400
	return JsonResponse(status=status, data=data)

############# Course Setting Values On Load ##########################################################


def course_setting(request):
	data_values = {}
	data = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					if(request.GET['request_type'] == 'course'):
						qry = StudentDropdown.objects.filter(field="COURSE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
					elif(request.GET['request_type'] == 'dept'):
						qry = EmployeeDropdown.objects.filter(field='DEPARTMENT').exclude(value__isnull=True).values("sno", "value")
					elif(request.GET['request_type'] == 'type'):
						qry = StudentDropdown.objects.filter(field="COURSE TYPE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
					else:
						qry = []
					status = 200
					data_values = {'data': list(qry)}
				elif request.method == 'POST':
					data = json.loads(request.body)
					course = data['course']
					qry = CourseDetail.objects.filter(course_id=StudentDropdown.objects.get(sno=course)).exclude(dept_id__value='AS').values('course_duration', 'course_id', 'course_type', 'dept_id')
					status = 200
					data_values = {'data': list(qry)}
				else:
					status = 403
		else:
			status = 401
	else:
		status = 400
	return JsonResponse(status=status, data=data_values)

################################## Course Setting Data Insert api ########################################################


def course_setting_insert(request):
	data_values = {}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					print(request.session['Session'])
					q_course = CourseDetail.objects.exclude(course__status="DELETE").exclude(dept__status="DELETE").values('uid', 'course__value', 'dept__value', 'course_type__value', 'course_duration', 'course', 'dept', 'course_type').order_by('course__value','dept__value','course_duration')
					data_values = {'data': list(q_course)}
					status = 200
					msg = "Success"
				elif request.method == 'POST':
					data = json.loads(request.body)
					course = data['course']
					dept = data['dept']
					duration = data['duration']
					type_val = data['type']
					for i in dept:

						qry = CourseDetail.objects.update_or_create(course=StudentDropdown.objects.get(sno=course), dept=EmployeeDropdown.objects.get(sno=i), defaults={'course_duration': duration}, course_type=StudentDropdown.objects.get(sno=type_val))

						q_get_id = CourseDetail.objects.filter(course=StudentDropdown.objects.get(sno=course), dept=EmployeeDropdown.objects.get(sno=i), course_duration=duration, course_type=StudentDropdown.objects.get(sno=type_val)).values('uid')

						for x in range(1, (int(duration) * 2 + 1)):
							q_ch = StudentSemester.objects.filter(dept=q_get_id[0]['uid'], sem=x).values()
							if len(q_ch) == 0:
								qr3 = StudentSemester.objects.create(dept=CourseDetail.objects.get(uid=q_get_id[0]['uid']), sem=x)

						status = 200
					data_values = {"msg": "Data Added Succesfully"}
				else:
					status = 403
		else:
			status = 401
	else:
		status = 400
	return JsonResponse(status=status, data=data_values)

###################################### Admission Eligiblity Data On Load ##################################################


def admission_eligiblity(request):
	data_values = {}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					if(request.GET['request_type'] == 'through'):
						qry = StudentDropdown.objects.filter(field="ADMISSION THROUGH").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
					elif(request.GET['request_type'] == 'type'):
						qry = StudentDropdown.objects.filter(field="ADMISSION TYPE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
					elif(request.GET['request_type'] == 'caste'):
						qry = StudentDropdown.objects.filter(field="CASTE").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
					elif(request.GET['request_type'] == 'eligible'):
						qry = StudentDropdown.objects.filter(field="ELIGIBLE ENTRY").exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
					elif(request.GET['request_type'] == 'prev_data'):
						course = request.GET['course']
						caste = request.GET['caste']
						qry = AdmissionEligibility.objects.filter(course_id=course, caste=caste).values("admission_through", "admission_type", "eligible_entry", "min_marks")
						print(qry.query)
					else:
						qry = []
					status = 200
					data_values = {'data': list(qry)}
				else:
					status = 403
		else:
			status = 401
	else:
		status = 400
	return JsonResponse(status=status, data=data_values)

###################################### Admission Eligiblity Data Insert ##################################################


def admission_eligiblity_insert(request):
	data_values = {}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					q_get = AdmissionEligibility.objects.values('course', 'course__value', 'admission_through', 'admission_through__value', 'admission_type', 'admission_type__value', 'eligible_entry', 'eligible_entry__value', 'min_marks', 'caste', 'caste__value')
					status = 200
					msg = "Success"
					data_values = {'data': list(q_get)}
				elif request.method == 'POST':
					data = json.loads(request.body)
					course = data['course']
					through = data['through']
					type = data['type']
					caste = data['caste']
					eligible = data['eligible']
					marks = data['marks']
					qry = AdmissionEligibility.objects.update_or_create(course=StudentDropdown.objects.get(sno=course), caste=StudentDropdown.objects.get(sno=caste), admission_through=StudentDropdown.objects.get(sno=through), admission_type=StudentDropdown.objects.get(sno=type), eligible_entry=StudentDropdown.objects.get(sno=eligible), defaults={'min_marks': marks})
					status = 200
					data_values = {'msg': "Data Successfully Added"}
				else:
					status = 403
		else:
			status = 401
	else:
		status = 400
	return JsonResponse(status=status, data=data_values)

####################################################### Registrar Add Student ####################################################


def add_student(request):

	data_values = {}
	qry = {}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337,1372])
			if check == 200:
				if request.method == 'GET':
					if(request.GET['request_type'] == 'get_data'):
						qry['through'] = get_through()
						qry['type'] = get_admission_type()
						qry['exam'] = get_exam_type()
						qry['course'] = get_course()
						qry['session'] = request.session['Session']
						qry['year'] = date.today().year
						qry['category'] = get_admission_category()
						qry['gender'] = get_gender()
						qry['category'] = get_caste()

					if(request.GET['request_type'] == 'get_data_hod'):
						qry['through'] = get_through()
						qry['type'] = get_admission_type()
						qry['exam'] = get_exam_type()
						q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
						dept = q_dept[0]['dept']
						qry['course'] = get_filtered_course(dept)
						qry['session'] = request.session['Session']
						qry['year'] = date.today().year
						qry['category'] = get_admission_category()
						qry['gender'] = get_gender()
						qry['category'] = get_caste()

					if(request.GET['request_type'] == 'get_branch'):
						course = request.GET['course']
						qry['branch'] = get_branch(course)
					if(request.GET['request_type'] == 'get_marks'):
						course = request.GET['course']
						caste = request.GET['caste']
						admission_type = request.GET['admission_type']
						admission_through = request.GET['admission_through']
						qry_eligible = AdmissionEligibility.objects.filter(course_id=course, caste=caste, admission_through=admission_through, admission_type=admission_type).values("min_marks")
						qry['marks'] = list(qry_eligible)
					if(request.GET['request_type'] == 'get_batch'):
						type = request.GET['type']
						if(type == '21'):
							qry['batch'] = request.session['Session'].split('-')[0]
							qry['year'] = 1
							qry['sem'] = 1
						if(type == '22'):
							qry['batch'] = int(request.session['Session'].split('-')[0]) - 1
							qry['year'] = 2
							qry['sem'] = 3
					if (request.GET['request_type'] == 'advance'):
						qry['course'] = get_course()
						qry['year'] = date.today().year
						qry['admission_type'] = get_admission_type()
						pass
					status = 200
					data_values = {'data': qry}
				else:
					status = 403
		else:
			status = 401
	else:
		status = 400
	return JsonResponse(status=status, data=data_values)

############################################################ Registrar Add Student Function #################################################


def add_student_insert(request):
	data_values = {}
	qry = {}

	status = 403
	StudentSession = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'POST':
					print(request.body)
					data = json.loads(request.body)
					through = data['through']
					type = data['type']
					exam_type = data['exam_type']
					fee_waiver = data['fee_waiver']
					course = data['course']
					branch = data['branch']
					# session=data['session']
					batch_from = data['batch_from']
					batch_to = data['batch_to']
					year = data['year']
					sem = data['sem']
					sem_qry = StudentSemester.objects.filter(sem=sem, dept=branch).values()
					sem_val = sem_qry[0]['sem_id']
					roll_no = data['roll_no']
					app = data['app']
					category = data['category']
					general_rank = data['general_rank']
					cat_rank = data['cat_rank']
					gender = data['gender']
					gen_rank = data['gen_rank']
					remark_detail = data['remark_detail']
					name = data['name'].upper()
					fname = data['fname'].upper()
					mname = data['mname'].upper()
					fmob = data['fmob']
					mmob = data['mmob']
					smob = data['smob']
					email = data['email']
					aadhar = data['aadhar']
					pmarks = data['pmarks']
					cmarks = data['cmarks']
					mmarks = data['mmarks']
					bmarks = data['bmarks']
					csmarks = data['csmarks']
					pmarks_max = data['pmarks_max']
					cmarks_max = data['cmarks_max']
					mmarks_max = data['mmarks_max']
					bmarks_max = data['bmarks_max']
					csmarks_max = data['csmarks_max']
					sem1 = data['sem1']
					sem2 = data['sem2']
					sem3 = data['sem3']
					sem4 = data['sem4']
					sem5 = data['sem5']
					sem6 = data['sem6']
					sem7 = data['sem7']
					sem8 = data['sem8']
					sem1_max = data['sem1_max']
					sem2_max = data['sem2_max']
					sem3_max = data['sem3_max']
					sem4_max = data['sem4_max']
					sem5_max = data['sem5_max']
					sem6_max = data['sem6_max']
					sem7_max = data['sem7_max']
					sem8_max = data['sem8_max']
					year1 = data['year1']
					year2 = data['year2']
					year3 = data['year3']
					year4 = data['year4']
					year1_max = data['year1_max']
					year2_max = data['year2_max']
					year3_max = data['year3_max']
					year4_max = data['year4_max']
					date_to = date.today()
					join_year = date_to.year

					q_check_duplicate = StudentPerDetail.objects.filter(aadhar_num=aadhar, uniq_id__join_year=join_year).values()
					if len(q_check_duplicate) > 0:
						status = 202
						msg = "Entry already exists"
						data_values = {'msg': msg}
					else:
						qry = StudentPrimDetail.objects.create(name=name, dept_detail=CourseDetail.objects.get(uid=branch), fee_waiver=fee_waiver, batch_from=batch_from, batch_to=batch_to, admission_through=StudentDropdown.objects.get(sno=through), admission_type=StudentDropdown.objects.get(sno=type), exam_type=StudentDropdown.objects.get(sno=exam_type), exam_roll_no=roll_no, caste=StudentDropdown.objects.get(sno=category), general_rank=general_rank, category_rank=cat_rank, gen_rank=gen_rank, join_year=join_year, email_id=email, date_of_add=date_to, gender=StudentDropdown.objects.get(sno=gender), remark_detail=remark_detail)
						uniq_id = StudentPrimDetail.objects.filter(name=name, dept_detail=CourseDetail.objects.get(uid=branch), batch_from=batch_from, batch_to=batch_to, admission_through=StudentDropdown.objects.get(sno=through), admission_type=StudentDropdown.objects.get(sno=type), exam_type=StudentDropdown.objects.get(sno=exam_type), exam_roll_no=roll_no, caste=StudentDropdown.objects.get(sno=category), general_rank=general_rank, category_rank=cat_rank, gen_rank=gen_rank, join_year=join_year, email_id=email, date_of_add=date_to).values('uniq_id')
						print(uniq_id)
						session = request.session['Session_name'].split('_')
						ses = ""
						for x in session:
							ses = ses + x
						StudentSession = eval('studentSession_' + ses)


						session_id = request.session['Session_id']
						year = (date.today().year - batch_from)
						course_id = CourseDetail.objects.filter(uid=branch).values_list('course', flat=True)
						sem_start_date = SemesterCommencement.objects.filter(session=session_id,course=course_id[0],year=(year+1),status="INSERT").values_list('commencement_date',flat=True)

						#if admission is given after defined date
						if len(sem_start_date) > 0  and sem_start_date[0] < date.today() :
							qry_session = StudentSession.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']), defaults={'mob': smob, 'fee_status': 'UNPAID', 'session': Semtiming.objects.get(uid=request.session['Session_id']), 'year': year+1, 'sem': StudentSemester.objects.get(sem_id=sem_val), 'registration_status': 0, 'att_start_date':sem_start_date[0]})
						#if admission is given before the defined date
						elif len(sem_start_date) > 0  and sem_start_date[0] > date.today() :
							qry_session = StudentSession.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']), defaults={'mob': smob, 'fee_status': 'UNPAID', 'session': Semtiming.objects.get(uid=request.session['Session_id']), 'year': year+1, 'sem': StudentSemester.objects.get(sem_id=sem_val), 'registration_status': 0, 'att_start_date':sem_start_date[0]})
						#if date is not defined
						else:
							sem_start_date_semtiming=Semtiming.objects.filter(uid=session_id).values('sem_start')
							qry_session = StudentSession.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']), defaults={'mob': smob, 'fee_status': 'UNPAID', 'session': Semtiming.objects.get(uid=request.session['Session_id']), 'year': year+1, 'sem': StudentSemester.objects.get(sem_id=sem_val), 'registration_status': 0, 'att_start_date':sem_start_date_semtiming[0]['sem_start']})

						
						qry_session = StudentSession.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']), defaults={'mob': smob, 'fee_status': 'UNPAID', 'session': Semtiming.objects.get(uid=request.session['Session_id']), 'year': year+1, 'sem': StudentSemester.objects.get(sem_id=sem_val), 'registration_status': 0})
						qry_perdetail = StudentPerDetail.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']), defaults={'fname': fname, 'mname': mname, 'aadhar_num': aadhar})
						qry_academic = StudentAcademic.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']), defaults={'phy_12': pmarks, 'phy_max': pmarks_max, 'chem_12': cmarks, 'chem_max': cmarks_max, 'math_12': mmarks, 'math_max': mmarks_max, 'bio_12': bmarks, 'bio_max': bmarks_max,'cs_12':csmarks,'cs_max':csmarks_max, 'sem1_ug': sem1, 'sem1_ug_max': sem1_max, 'sem2_ug': sem2, 'sem2_ug_max': sem2_max, 'sem3_ug': sem3, 'sem3_ug_max': sem3_max, 'sem4_ug': sem4, 'sem4_ug_max': sem4_max, 'sem5_ug': sem5, 'sem5_ug_max': sem5_max, 'sem6_ug': sem6, 'sem6_ug_max': sem6_max, 'sem7_ug': sem7, 'sem7_ug_max': sem7_max, 'sem8_ug': sem8, 'sem8_ug_max': sem8_max, 'ug_year1': year1, 'ug_year1_max': year1_max, 'ug_year2': year2, 'ug_year2_max': year2_max, 'ug_year3': year3, 'ug_year3_max': year3_max, 'ug_year4': year4, 'ug_year4_max': year4_max})
						# qry=StudentPrimDetail.objects.update_or_create(name=name,dept_detail=EmployeeDropdown.objects.get(sno=branch),batch_from=batch_from,batch_to=batch_to,admission_through=StudentDropdown.objects.get(sno=through),admission_type=StudentDropdown.objects.get(sno=type),exam_type=StudentDropdown.objects.get(sno=exam_type),exam_roll_no=roll_no,admission_category=StudentDropdown.objects.get(sno=category),general_rank=general_rank,category_rank=cat_rank,gen_rank=gen_rank,join_year=batch_from,email_id=email,date_of_add=datetime.date.today(),uniq_id=roll_no)
						qry_family = StudentFamilyDetails.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']), defaults={'father_mob': fmob, 'mother_mob': mmob})
						# print(fmob)
						# print(smob)
						# print(aadhar)
						# qry_session=StudentSession.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']),defaults={'mob':smob,'fee_status':'Unpaid','session':request.session['Session'],'year':year})
						# qry_perdetail=StudentPerDetail.objects.update_or_create(uniq_id=StudentPrimDetail.objects.get(uniq_id=uniq_id[0]['uniq_id']),defaults={'fname':fname,'mname':mname,'aadhar_num':aadhar})
						status = 200
						data_values = {'msg': "Data Added Succesfully"}
				else:
					status = 403
		else:
			status = 401
	else:
		status = 400
	# return JsonResponse(status=status,data=data_values)
	return JsonResponse(status=status, data=data_values)


#                   msg = "Successfully"
#               else:
#                   status=500
#                   msg = "request error"
#           else:
#               status=500
#               msg = "permission error"
#   else:
#       status=500
#       msg = "AuthUser Error"

	##############################################insert-roll########################################################################

########################################################### promote-student#########################################################################

# def promote_student(request):
#   data_values={}
#   qry={}
#   data=[]
#   if 'HTTP_COOKIE' in request.META:
#       if request.user.is_authenticated:
#           check=checkpermission(request,[337])
#           if check==200:
#               if request.method=='GET':
#                   if (request.GET['request_type']=='course'):
#                       qry['course']=get_course()
#                       data_values={'data':qry}
#                   if(request.GET['request_type']=='branch'):
#                       course=request.GET['course']
#                       qry['branch']=get_branch(course)

#                       year1= date.today().year
#                       qry['year']=[]
#                       for i in range(int(year1),2009,-1):
#                           qry['year'].append(i)

#                       data_values={'data':qry}
#                   if(request.GET['request_type']=='fetch'):
#                       course=request.GET['Course']
#                       branch=request.GET['Branch']
#                       batch_from=request.GET['Batch_from']
#                       course_duration=request.GET['Course_duration']
#                       session=request.session['Session_name'].split('_')
#                       sess=""
#                       for x in session:
#                           sess=sess+ x
#                       StudentSession=eval('studentSession_'+sess)
#                       course_duration=int(course_duration)*2

#                       branch_array=[]
#                       if(branch=='1'):
#                           branch_list=list(CourseDetail.objects.filter(course_id=StudentDropdown.objects.get(sno = course)).values_list("uid",flat=True))
#                           branch_array=branch_list
#                       else:
#                           branch_array.append(branch)

#                       if(batch_from!='ALL'):
#                           qry['student']=list(StudentSession.objects.filter(uniq_id__batch_from=batch_from,uniq_id__dept_detail__in=branch_array).exclude(uniq_id__admission_status__value="WITHDRAWAL").exclude(uniq_id__admission_status__value="FAILED").values('uniq_id','registration_status','year','fee_status','section__section','sem__sem','uniq_id__name','uniq_id__uni_roll_no','uniq_id__admission_status__value','session__session').order_by('uniq_id__name'))
#                       else:
#                           qry['student']=list(StudentSession.objects.filter(uniq_id__dept_detail__in=branch_array).exclude(uniq_id__admission_status__value="WITHDRAWAL").exclude(uniq_id__admission_status__value="FAILED").exclude(sem__sem=course_duration).values('uniq_id','registration_status','year','fee_status','section__section','sem__sem','uniq_id__name','uniq_id__uni_roll_no','uniq_id__admission_status__value','session__session').order_by('uniq_id__name'))

#                       data_values={'data':qry}

#                   status=200
#               elif request.method=='POST':
#                       uniq_id=json.loads(request.body)
#                       session=request.session['Session_name'].split('_')
#                       sess=""
#                       for x in session:
#                           sess=sess+ x
#                       StudentSession=eval('studentSession_'+sess)

#                       qry=list(StudentSession.objects.filter(uniq_id__in=uniq_id).values('sem','sem__sem','sem__dept','year','uniq_id__dept_detail__course'))
#                       qry1=list(StudentSession.objects.filter(uniq_id__in=uniq_id).values('section__section').distinct())
#                       sem=qry[0]['sem__sem']
#                       sem=sem+1

#                       qry2=list(StudentSemester.objects.filter(sem=sem,dept=qry[0]['sem__dept']).values('sem_id'))

#                       year=qry[0]['year']
#                       if(year!=1 or qry[0]['uniq_id__dept_detail__course']!=12):
#                           qr=list(StudentSession.objects.filter(uniq_id=uniq_id[0]).values('section'))

#                           if(qr[0]['section']==None):
#                               qry7=list(StudentSession.objects.filter(uniq_id__in=uniq_id,section__isnull=True).values_list('uniq_id',flat=True).order_by('uniq_id__name'))
#                               qry8=Sections.objects.filter(sem_id=qry2[0]['sem_id']).values('section_id')
#                               x=len(qry8)
#                               y=len(qry7)
#                               z=j=int(y/x)
#                               start_id=0
#                               i=1
#                               for q in qry8:
#                                   uniq_id_shift=qry7[start_id:j+1]
#                                   print(qry2[0]['sem_id'])
#                                   qry9=StudentSession.objects.filter(uniq_id__in=uniq_id_shift).update(sem=qry2[0]['sem_id'],section=q['section_id'])
#                                   start_id=start_id+z
#                                   i+=1
#                                   if(i==x):
#                                       j=y
#                                   else:
#                                       j=j+z
#                           else:
#                               for q in qry1:
#                                   qry3=list(Sections.objects.filter(sem_id=qry2[0]['sem_id'],section=q['section__section']).values('section_id'))
#                                   if(((sem-1)%2)!=0):
#                                       qry4=StudentSession.objects.filter(uniq_id__in=uniq_id,section__section=q['section__section']).update(sem=qry2[0]['sem_id'],section=qry3[0]['section_id'])

#                                   else:
#                                       year=year+1
#                                       qry4=list(Semtiming.objects.filter(session_name=sess).values('uid'))
#                                       qry5=StudentSession.objects.filter(uniq_id__in=uniq_id,section__section=q['section__section']).update(year=year,sem=qry2[0]['sem_id'],section=qry3[0]['section_id'],fee_status="UNPAID",session=qry4[0]['uid'])
#                       else:
#                           qry7=Sections.objects.filter(sem_id=qry2[0]['sem_id']).values('section_id')
#                           qry8=StudentSession.objects.filter(uniq_id__in=uniq_id).values('section')
#                           if(qry8[0]['section']==None):
#                               qry9=StudentAcademic.objects.filter(uniq_id__in=uniq_id).annotate(pcmperc=(F('phy_12')+F('chem_12')+F('math_12'))/3).values_list('uniq_id',flat=True).order_by('-pcmperc')
#                               x=len(qry7)
#                               y=len(qry9)
#                               z=j=int(y/x)
#                               start_id=0
#                               i=1
#                               for q in qry7:
#                                   uniq_id_shift=qry9[start_id:j+1]
#                                   qry10=StudentSession.objects.filter(uniq_id__in=uniq_id_shift).update(section=q['section_id'])
#                                   start_id=start_id+z
#                                   i+=1
#                                   if(i==x):
#                                       j=y
#                                   else:
#                                       j=j+z

#                           else:
#                               for q in qry1:
#                                   qry3=list(Sections.objects.filter(sem_id=qry2[0]['sem_id'],section=q['section__section']).values('section_id'))
#                                   if(((sem-1)%2)!=0):
#                                       qry4=StudentSession.objects.filter(uniq_id__in=uniq_id,section__section=q['section__section']).update(sem=qry2[0]['sem_id'],section=qry3[0]['section_id'])
#                                   else:
#                                       sem=3
#                                       qry4=list(Semtiming.objects.filter(session_name=sess).values('uid'))
#                                       qry11=list(StudentSession.objects.filter(uniq_id__in=uniq_id).values('section__dept').distinct())
#                                       for q in qry11:
#                                           qry12=StudentSession.objects.filter(uniq_id__in=uniq_id,section__dept=q['section__dept']).values_list('uniq_id',flat=True).order_by('uniq_id__name')
#                                           qry13=Sections.objects.filter(dept=q['section__dept'],sem_id__sem=sem).values('section_id','sem_id')
#                                           x=len(qry12)
#                                           y=len(qry13)
#                                           z=j=x/y
#                                           start_id=0
#                                           i=1
#                                           for q1 in qry13:
#                                               uniq_id_shift=qry12[start_id:j+1]
#                                               qry10=StudentSession.objects.filter(uniq_id__in=uniq_id_shift).update(sem=q1['sem_id'],section=q1['section_id'],fee_status="UNPAID",year='2',session=qry4[0]['uid'])
#                                               start_id=start_id+z
#                                               i+=1
#                                               if(i==x):
#                                                   j=y
#                                               else:
#                                                   j=j+z
#                       status=200
#                       data_values={'msg':"Data Added Succesfully"}
#               else:
#                   status=403
#       else:
#           status=401
#   else:
#       status=400
#   return JsonResponse(status=status,data=data_values)


# def promote_student(request):
#   data_values = {}
#   qry = {}
#   data = []
#   if 'HTTP_COOKIE' in request.META:
#       if request.user.is_authenticated:
#           check = checkpermission(request, [337])
#           if check == 200:
#               if request.method == 'GET':
#                   if (request.GET['request_type'] == 'course'):
#                       qry['course'] = get_course()
#                       data_values = {'data': qry}
#                   if(request.GET['request_type'] == 'branch'):
#                       course = request.GET['course']
#                       qry['branch'] = get_branch(course)

#                       year1 = date.today().year
#                       qry['year'] = []
#                       for i in range(int(year1), 2009, -1):
#                           qry['year'].append(i)

#                       data_values = {'data': qry}
#                   if(request.GET['request_type'] == 'fetch'):
#                       course = request.GET['Course']
#                       branch = request.GET['Branch']
#                       batch_from = request.GET['Batch_from']
#                       course_duration = request.GET['Course_duration']
#                       session = request.session['Session_name'].split('_')
#                       print(session)
#                       sess = ""
#                       for x in session:
#                           sess = sess + x
#                       StudentSession = eval('studentSession_' + sess)
#                       course_duration = int(course_duration) * 2

#                       branch_array = []
#                       if(branch == '1'):
#                           branch_list = list(CourseDetail.objects.filter(course_id=StudentDropdown.objects.get(sno=course)).values_list("uid", flat=True))
#                           branch_array = branch_list
#                       else:
#                           branch_array.append(branch)

#                       if(batch_from != 'ALL'):
#                           qry['student'] = list(StudentSession.objects.filter(uniq_id__batch_from=batch_from, uniq_id__dept_detail__in=branch_array).exclude(section__status="DELETE").exclude(uniq_id__in=StudentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED"))).values('uniq_id', 'registration_status', 'year', 'fee_status', 'uniq_id__gender__value', 'section__section', 'sem__sem', 'sem__dept__course__value', 'sem__dept__dept__value', 'uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id__admission_status__value', 'session__session').order_by('uniq_id__name'))
#                       else:
#                           qry['student'] = list(StudentSession.objects.filter(uniq_id__dept_detail__in=branch_array).exclude(section__status="DELETE").exclude(uniq_id__in=StudentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED"))).exclude(sem__sem=course_duration).values('uniq_id', 'registration_status', 'year', 'fee_status', 'uniq_id__gender__value', 'section__section', 'sem__sem', 'sem__dept__course__value', 'sem__dept__dept__value',    'uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id__admission_status__value', 'session__session').order_by('uniq_id__name'))
#                       for q in qry['student']:
#                           q_pcm_sorted = StudentAcademic.objects.filter(uniq_id=q['uniq_id']).annotate(pcmperc=((F('phy_12') + F('chem_12') + F('math_12')) / (F('phy_max') + F('chem_max') + F('math_max'))) * 100).values('pcmperc')
#                           if q_pcm_sorted[0]['pcmperc'] is None:
#                               q['pcmperc'] = "---"
#                           else:
#                               q['pcmperc'] = round(float(q_pcm_sorted[0]['pcmperc']), 2)
#                           q_personal_details = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname')
#                           q['fname'] = q_personal_details[0]['fname']

#                       data_values = {'data': qry}

#                   status = 200
#               elif request.method == 'POST':
#                   uniq_id = json.loads(request.body)
#                   session = request.session['Session_name'].split('_')
#                   sess = ""
#                   for x in session:
#                       sess = sess + x
#                   StudentSession = eval('studentSession_' + sess)
#                   sem_type = request.session['sem_type']

#                   qry = list(StudentSession.objects.filter(uniq_id=uniq_id[0]).exclude(section__status="DELETE").values('sem', 'sem__sem', 'sem__dept', 'year', 'uniq_id__dept_detail__course'))

#                   sem = qry[0]['sem__sem']
#                   if sem_type == 'odd':
#                       if sem % 2 == 0:
#                           sem += 1

#                   elif sem_type == 'even':
#                       if sem % 2 != 0:
#                           sem += 1
#                   year = int(math.ceil(sem / 2.0))
#                   print(sem, year, qry[0])
#                   ################# B.TECH 1st YEAR - 1st sem ###########################
#                   if year == 1 and qry[0]['uniq_id__dept_detail__course'] == 12 and sem == 1:
#                       q_sem_id = StudentSemester.objects.filter(sem=sem, dept__dept__value='AS').values('sem_id')

#                       q_pcm_sorted = StudentAcademic.objects.filter(uniq_id__in=uniq_id).annotate(pcmperc=(F('phy_12') + F('chem_12') + F('math_12')) / (F('phy_max') + F('chem_max') + F('math_max'))).values_list('uniq_id', flat=True).order_by('-pcmperc', 'uniq_id__name')

#                       qry_sections = Sections.objects.filter(sem_id=q_sem_id[0]['sem_id']).exclude(status="DELETE").values('section_id').order_by('section')

#                       no_of_sec = len(qry_sections)
#                       for i in range(no_of_sec):
#                           uniq_li1 = q_pcm_sorted[i::(2 * no_of_sec)]
#                           uniq_li2 = q_pcm_sorted[(2 * no_of_sec - (i + 1))::2 * no_of_sec]
#                           uniq_li = uniq_li1 + uniq_li2

#                           q_update = StudentSession.objects.filter(uniq_id__in=uniq_li).update(sem=StudentSemester.objects.get(sem_id=q_sem_id[0]['sem_id']), section=Sections.objects.get(section_id=qry_sections[i]['section_id']), year=year)

#                   ################# EXCEPT B.TECH 1st YEAR and b.tech 1st year 3rd sem ###########################
#                   elif sem == 1 or (year == 2 and qry[0]['uniq_id__dept_detail__course'] == 12 and sem == 3):
#                       print("qry_depts")
#                       qry_depts = list(StudentSession.objects.filter(uniq_id__in=uniq_id).exclude(section__status="DELETE").values('uniq_id__dept_detail').distinct())
#                       print(qry_depts)
#                       for qd in qry_depts:
#                           q_sem_id = StudentSemester.objects.filter(sem=sem, dept=qd['uniq_id__dept_detail']).values('sem_id')

#                           q_name_sorted = StudentPrimDetail.objects.filter(uniq_id__in=uniq_id, dept_detail=qd['uniq_id__dept_detail']).values_list('uniq_id', flat=True).order_by('name')

#                           no_of_name = len(q_name_sorted)
#                           qry_sections = Sections.objects.filter(sem_id=q_sem_id[0]['sem_id']).exclude(status="DELETE").values('section_id').order_by('section')

#                           no_of_sec = len(qry_sections)

#                           start = 0
#                           end = no_of_name // no_of_sec
#                           ending = end
#                           for i in range(no_of_sec):
#                               print("HI2", i, ending)
#                               if i == no_of_sec - 1:
#                                   print("HI2", i, ending)
#                                   ending = len(q_name_sorted) + 1
#                               uniq_li = q_name_sorted[start:ending]
#                               print(uniq_li)
#                               q_update = StudentSession.objects.filter(uniq_id__in=uniq_li).exclude(section__status="DELETE").update(sem=StudentSemester.objects.get(sem_id=q_sem_id[0]['sem_id']), section_id=Sections.objects.get(section_id=qry_sections[i]['section_id']), year=year)

#                               start = start + end
#                               ending += end

#                   ################ REST CASE #########################################
#                   else:
#                       null_sec_uniq = list(StudentSession.objects.filter(uniq_id__in=uniq_id, section__isnull=True).exclude(section__status="DELETE").values_list('uniq_id', flat=True))

#                       uniq_id = list(set(uniq_id) - set(null_sec_uniq))

#                       qry_secs = list(StudentSession.objects.filter(uniq_id__in=uniq_id).exclude(section__status="DELETE").values('section', 'sem', 'section__section', 'uniq_id__dept_detail').distinct())

#                       for qs in qry_secs:

#                           uniq_li = list(StudentSession.objects.filter(uniq_id__in=uniq_id, section=qs['section'], sem=qs['sem']).values_list('uniq_id', flat=True))
#                           if (sem == 1 or sem == 2) and qry[0]['uniq_id__dept_detail__course'] == 12:
#                               qs['uniq_id__dept_detail'] = 59
#                               q_section_id = Sections.objects.filter(sem_id__sem=sem, sem_id__dept=qs['uniq_id__dept_detail'], section=qs['section__section']).values('section_id', 'sem_id')
#                           else:
#                               q_section_id = Sections.objects.filter(sem_id__sem=sem, sem_id__dept=qs['uniq_id__dept_detail'], section=qs['section__section']).exclude(status="DELETE").values('section_id', 'sem_id')

#                           q_update = StudentSession.objects.filter(uniq_id__in=uniq_li).update(sem=StudentSemester.objects.get(sem_id=q_section_id[0]['sem_id']), section_id=Sections.objects.get(section_id=q_section_id[0]['section_id']), year=year)

#                       ############# NULL SECTION-ID (LATERAL CASE) #####################
#                       uniq_id = null_sec_uniq
#                       qry_depts = list(StudentSession.objects.filter(uniq_id__in=uniq_id).values('uniq_id__dept_detail').distinct())

#                       for qd in qry_depts:
#                           q_sem_id = StudentSemester.objects.filter(sem=sem, dept=qd['uniq_id__dept_detail']).values('sem_id')

#                           q_name_sorted = StudentPrimDetail.objects.filter(uniq_id__in=uniq_id, dept_detail=qd['uniq_id__dept_detail']).values_list('uniq_id', flat=True).order_by('name')

#                           no_of_name = len(q_name_sorted)
#                           qry_sections = Sections.objects.filter(sem_id=q_sem_id[0]['sem_id']).exclude(status="DELETE").values('section_id').order_by('section')

#                           no_of_sec = len(qry_sections)

#                           start = 0
#                           end = no_of_name // no_of_sec
#                           # print(no_of_name,no_of_sec,end)
#                           for i in range(no_of_sec):
#                               uniq_li = q_name_sorted[start:end]

#                               # print(q_sem_id,sem,qry_sections[i]['section_id'])
#                               # print(uniq_li)
#                               q_update = StudentSession.objects.filter(uniq_id__in=uniq_li).exclude(section__status="DELETE").update(sem=StudentSemester.objects.get(sem_id=q_sem_id[0]['sem_id']), section_id=Sections.objects.get(section_id=qry_sections[i]['section_id']), year=year)

#                               start = start + (end - start)
#                               end += (end - start)
#                               if i == no_of_sec - 1:
#                                   end = no_of_name

#                               print(start, end)

#                   status = 200
#                   data_values = {'msg': "Data Added Succesfully"}
#               else:
#                   status = 403
#       else:
#           status = 401
#   else:
#       status = 400
#   return JsonResponse(status=status, data=data_values)


########################################################### Advance Report #######################################################################
def student_details(request):
	data = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1368, 317, 1371, 319, 1498])
			if check == 200:
				if request.method == 'POST':
					status = 200
					session_name = request.session['Session_name']
					session_id = request.session['Session_id']
					body = json.loads(request.body)
					course_val = body['course_val']
					year_val = body['year_val']
					dept_detail_select = body['dept_detail_select']
					admission_type = body['admission_type']
					print(admission_type)
					qry = StudentPrimDetail.objects.filter(batch_from__in=year_val, dept_detail__in=dept_detail_select, admission_type__in=admission_type).values('name', 'batch_from', 'batch_to', 'exam_roll_no', 'general_rank', 'category_rank', 'gen_rank', 'uni_roll_no', 'join_year', 'email_id', 'date_of_add', 'uniq_id', 'old_uniq_id', 'form_fill_status', 'fee_waiver', 'remark', 'admission_category__value', 'admission_through__value', 'admission_type__value', 'dept_detail__dept__value', 'exam_type__value', 'stu_type__value', 'admission_status__value', 'caste__value', 'gender__value', 'lib', 'dept_detail__course__value')

					i = 0
					for q in qry:
						data.append(q)
						uid = q['uniq_id']
						data[i]['residential_status'] = check_residential_status(uid, session_id, ('even','odd')[session_name[4] == 'o'])
						if q['lib'] != None:
							data[i]['kiet_email'] = q['name'].split()[0].lower()+'.'+q['lib'].lower()+'@kiet.edu'
						else:
							data[i]['kiet_email'] = ""
						student_session = generate_session_table_name("studentSession_", session_name)

						q1 = student_session.objects.filter(uniq_id=uid).exclude(section__status="DELETE").values('mob', 'fee_status', 'year', 'class_roll_no', 'registration_status', 'acc_reg', 'section__section', 'sem__sem', 'session__session')
						# print("ayuhs")
						if len(q1) > 0:
							for k, v in q1[0].items():
								data[i][k] = v
							if data[i]['registration_status'] == 1:
								data[i]['registration_status'] = 'Registered'
							else:
								data[i]['registration_status'] = 'Not Registered'

						q2 = StudentAcademic.objects.filter(uniq_id=uid).values('app_no', 'year_10', 'per_10', 'max_10', 'total_10', 'year_12', 'per_12', 'max_12', 'total_12', 'phy_12', 'phy_max', 'chem_12', 'chem_max', 'math_12', 'math_max', 'eng_12', 'eng_max', 'bio_12', 'bio_max','cs_12','cs_max', 'pcm_total', 'is_dip', 'year_dip', 'per_dip', 'max_dip', 'total_dip', 'ug_year1', 'ug_year1_max', 'ug_year1_back', 'ug_year2', 'ug_year2_max', 'ug_year2_back', 'ug_year3', 'ug_year3_max', 'ug_year3_back', 'ug_year4', 'ug_year4_max', 'ug_year4_back', 'year_ug', 'per_ug', 'max_ug', 'total_ug', 'sem1_ug', 'sem1_ug_max', 'sem1_ug_back', 'sem2_ug', 'sem2_ug_max', 'sem2_ug_back', 'sem3_ug', 'sem3_ug_max', 'sem3_ug_back', 'sem3_ug', 'sem3_ug_max', 'sem3_ug_back', 'sem4_ug', 'sem4_ug_max', 'sem4_ug_back', 'sem5_ug', 'sem5_ug_max', 'sem5_ug_back', 'sem6_ug', 'sem6_ug_max', 'sem7_ug', 'sem7_ug_max', 'sem7_ug_back', 'sem8_ug', 'sem8_ug_max', 'sem8_ug_back', 'pg_year1', 'pg_year1_max', 'pg_year1_back', 'pg_year2', 'pg_year2_max', 'pg_year2_back', 'pg_year3', 'pg_year3_max', 'pg_year3_back', 'year_pg', 'per_pg', 'sem1_pg', 'sem1_pg_max', 'sem1_pg_back', 'sem2_pg', 'sem2_pg_max', 'sem2_pg_back', 'sem3_pg', 'sem3_pg_max', 'sem3_pg_back', 'sem4_pg', 'sem4_pg_max', 'sem4_pg_back', 'sem5_pg', 'sem5_pg_max', 'sem5_pg_back', 'sem6_pg', 'sem6_pg_max', 'sem6_pg_back', 'area_dip', 'ug_degree', 'ug_area', 'pg_degree', 'pg_area', 'board_10__value', 'board_12__value', 'uni_dip__value', 'uni_pg__value', 'uni_ug__value')
						per = 0
						if len(q2) > 0:
							if q2[0]['bio_12'] is None and q2[0]['math_12'] is None:
								pass
							elif q2[0]['bio_12'] is None:
								try:
									if (q2[0]['phy_max'] is None or q2[0]['chem_max'] is None or q2[0]['math_max'] is None):
										per = 0
									elif (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['math_max']) > 0:
										per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['math_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['math_max'])
									else:
										per = 0
								except:
									per = 0
							elif q2[0]['math_12'] is None:
								try:
									if (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max']) > 0:
										per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['bio_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'])
									else:
										per = 0
								except:
									per = 0
							else:
								try:
									if q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'] + q2[0]['math_max'] > 0:
										per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['bio_12'] + q2[0]['math_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'] + q2[0]['math_max'])
									else:
										per = 0
								except:
									per = 0
							data[i]['pcmpcbpcmb'] = round(per, 2)
							for k, v in q2[0].items():
								data[i][k] = v

						q3 = StudentAddress.objects.filter(uniq_id=uid).values('p_add1', 'p_add2', 'p_city', 'p_district', 'p_pincode', 'c_add1', 'c_add2', 'c_city', 'c_district', 'c_pincode', 'c_state__value', 'p_state__value')
						if len(q3) > 0:
							for k, v in q3[0].items():
								data[i][k] = v

						q4 = StudentFamilyDetails.objects.filter(uniq_id=uid).values('father_mob', 'father_email', 'father_income', 'father_occupation__value', 'father_dept', 'father_add', 'father_city', 'mother_mob', 'mother_email', 'mother_income', 'mother_occupation__value', 'mother_dept', 'mother_add', 'mother_city', 'gname', 'g_relation', 'g_mob', 'g_email', 'g_add', 'g_city')
						if len(q4) > 0:
							for k, v in q4[0].items():
								data[i][k] = v

						q5 = StudentPerDetail.objects.filter(uniq_id=uid).values('fname', 'mob_sec', 'dob', 'image_path', 'image_path', 'aadhar_num', 'bank_acc_no', 'pan_no', 'uan_no', 'physically_disabled', 'bg__value', 'marital_status__value', 'nationality__value', 'religion__value', 'mname', 'caste_name', 'nation_other')
						if len(q5) > 0:
							for k, v in q5[0].items():
								data[i][k] = v
						data[i]['sno'] = i + 1
						i += 1
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data={'data': data}, status=status)

def student_details_for_lib_cards(request):
	data = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1368, 317, 1371, 319, 1498])
			if check == 200:
				if request.method == 'POST':
					status = 200
					session_name = request.session['Session_name']
					session_id = request.session['Session_id']
					body = json.loads(request.body)
					course_val = body['course_val']
					year_val = body['year_val']
					dept_detail_select = body['dept_detail_select']
					admission_type = body['admission_type']
					print(admission_type)
					qry = StudentPrimDetail.objects.filter(batch_from__in=year_val, dept_detail__in=dept_detail_select, admission_type__in=admission_type).exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL") | Q(admission_status__value="FAILED") | Q(admission_status__value="PASSED"))).values('name', 'batch_from', 'batch_to', 'exam_roll_no', 'general_rank', 'category_rank', 'gen_rank', 'uni_roll_no', 'join_year', 'email_id', 'date_of_add', 'uniq_id', 'old_uniq_id', 'form_fill_status', 'fee_waiver', 'remark', 'admission_category__value', 'admission_through__value', 'admission_type__value', 'dept_detail__dept__value', 'exam_type__value', 'stu_type__value', 'admission_status__value', 'caste__value', 'gender__value', 'lib', 'dept_detail__course__value')

					i = 0
					for q in qry:
						data.append(q)
						uid = q['uniq_id']
						data[i]['residential_status'] = check_residential_status(uid, session_id, ('even','odd')[session_name[4] == 'o'])
						if q['lib'] != None:
							data[i]['kiet_email'] = q['name'].split()[0].lower()+'.'+q['lib'].lower()+'@kiet.edu'
						else:
							data[i]['kiet_email'] = ""
						student_session = generate_session_table_name("studentSession_", session_name)

						q1 = student_session.objects.filter(uniq_id=uid).exclude(section__status="DELETE").values('mob', 'fee_status', 'year', 'class_roll_no', 'registration_status', 'acc_reg', 'section__section', 'sem__sem', 'session__session')
						# print("ayuhs")
						if len(q1) > 0:
							for k, v in q1[0].items():
								data[i][k] = v
							if data[i]['registration_status'] == 1:
								data[i]['registration_status'] = 'Registered'
							else:
								data[i]['registration_status'] = 'Not Registered'

						q2 = StudentAcademic.objects.filter(uniq_id=uid).values('app_no', 'year_10', 'per_10', 'max_10', 'total_10', 'year_12', 'per_12', 'max_12', 'total_12', 'phy_12', 'phy_max', 'chem_12', 'chem_max', 'math_12', 'math_max', 'eng_12', 'eng_max', 'bio_12', 'bio_max', 'pcm_total', 'is_dip', 'year_dip', 'per_dip', 'max_dip', 'total_dip', 'ug_year1', 'ug_year1_max', 'ug_year1_back', 'ug_year2', 'ug_year2_max', 'ug_year2_back', 'ug_year3', 'ug_year3_max', 'ug_year3_back', 'ug_year4', 'ug_year4_max', 'ug_year4_back', 'year_ug', 'per_ug', 'max_ug', 'total_ug', 'sem1_ug', 'sem1_ug_max', 'sem1_ug_back', 'sem2_ug', 'sem2_ug_max', 'sem2_ug_back', 'sem3_ug', 'sem3_ug_max', 'sem3_ug_back', 'sem3_ug', 'sem3_ug_max', 'sem3_ug_back', 'sem4_ug', 'sem4_ug_max', 'sem4_ug_back', 'sem5_ug', 'sem5_ug_max', 'sem5_ug_back', 'sem6_ug', 'sem6_ug_max', 'sem7_ug', 'sem7_ug_max', 'sem7_ug_back', 'sem8_ug', 'sem8_ug_max', 'sem8_ug_back', 'pg_year1', 'pg_year1_max', 'pg_year1_back', 'pg_year2', 'pg_year2_max', 'pg_year2_back', 'pg_year3', 'pg_year3_max', 'pg_year3_back', 'year_pg', 'per_pg', 'sem1_pg', 'sem1_pg_max', 'sem1_pg_back', 'sem2_pg', 'sem2_pg_max', 'sem2_pg_back', 'sem3_pg', 'sem3_pg_max', 'sem3_pg_back', 'sem4_pg', 'sem4_pg_max', 'sem4_pg_back', 'sem5_pg', 'sem5_pg_max', 'sem5_pg_back', 'sem6_pg', 'sem6_pg_max', 'sem6_pg_back', 'area_dip', 'ug_degree', 'ug_area', 'pg_degree', 'pg_area', 'board_10__value', 'board_12__value', 'uni_dip__value', 'uni_pg__value', 'uni_ug__value')
						per = 0
						if len(q2) > 0:
							if q2[0]['bio_12'] is None and q2[0]['math_12'] is None:
								pass
							elif q2[0]['bio_12'] is None:
								try:
									if (q2[0]['phy_max'] is None or q2[0]['chem_max'] is None or q2[0]['math_max'] is None):
										per = 0
									elif (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['math_max']) > 0:
										per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['math_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['math_max'])
									else:
										per = 0
								except:
									per = 0
							elif q2[0]['math_12'] is None:
								try:
									if (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max']) > 0:
										per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['bio_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'])
									else:
										per = 0
								except:
									per = 0
							else:
								try:
									if q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'] + q2[0]['math_max'] > 0:
										per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['bio_12'] + q2[0]['math_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'] + q2[0]['math_max'])
									else:
										per = 0
								except:
									per = 0
							data[i]['pcmpcbpcmb'] = round(per, 2)
							for k, v in q2[0].items():
								data[i][k] = v

						q3 = StudentAddress.objects.filter(uniq_id=uid).values('p_add1', 'p_add2', 'p_city', 'p_district', 'p_pincode', 'c_add1', 'c_add2', 'c_city', 'c_district', 'c_pincode', 'c_state__value', 'p_state__value')
						if len(q3) > 0:
							for k, v in q3[0].items():
								data[i][k] = v

						q4 = StudentFamilyDetails.objects.filter(uniq_id=uid).values('father_mob', 'father_email', 'father_income', 'father_occupation__value', 'father_dept', 'father_add', 'father_city', 'mother_mob', 'mother_email', 'mother_income', 'mother_occupation__value', 'mother_dept', 'mother_add', 'mother_city', 'gname', 'g_relation', 'g_mob', 'g_email', 'g_add', 'g_city')
						if len(q4) > 0:
							for k, v in q4[0].items():
								data[i][k] = v

						q5 = StudentPerDetail.objects.filter(uniq_id=uid).values('fname', 'mob_sec', 'dob', 'image_path', 'image_path', 'aadhar_num', 'bank_acc_no', 'pan_no', 'uan_no', 'physically_disabled', 'bg__value', 'marital_status__value', 'nationality__value', 'religion__value', 'mname', 'caste_name', 'nation_other')
						if len(q5) > 0:
							for k, v in q5[0].items():
								data[i][k] = v
						data[i]['sno'] = i + 1
						i += 1
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data={'data': data}, status=status)


def registrar_summary(request):
	data_values = {}
	total = []
	c = 0
	fw = 0
	jk = 0
	km = 0
	dir = 0
	ts = 0
	fo = 0
	lc = 0
	ews = 0
	o = 0
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [1368])
			if check == 200:
				if request.method == 'GET':
					session_name = request.session['Session_name']
					course_id = request.GET['course_id']
					join_year = request.GET['join_year']
					admission_type = request.GET['admission_type']
					registrar_session = session_name[0:4]
					print(registrar_session)
					q_get_dept = CourseDetail.objects.filter(course_id=course_id).exclude(dept__value='AS').values('course_id', 'dept', 'course_id__value', 'dept__value', 'uid', 'capacity', 'lateral_capacity')
					data = []
					for d in q_get_dept:
						q_f_ups = StudentPrimDetail.objects.filter(dept_detail=d['uid'], fee_waiver='N', admission_through__value="COUNSELLING", join_year=join_year, admission_type__value=admission_type).exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL") | Q(admission_status__value="FAILED") | Q(admission_status__value="PASSED"))).count()
						q_f_fw = StudentPrimDetail.objects.filter(dept_detail=d['uid'], fee_waiver='Y', join_year=join_year, admission_type__value=admission_type, admission_through__value="COUNSELLING").exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL") | Q(admission_status__value="FAILED") | Q(admission_status__value="PASSED"))).count()
						q_f_ews = StudentPrimDetail.objects.filter(dept_detail=d['uid'], join_year=join_year, admission_type__value=admission_type, admission_through__value="EWS").exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL") | Q(admission_status__value="FAILED") | Q(admission_status__value="PASSED"))).count()
						q_f_jk = StudentPrimDetail.objects.filter(dept_detail=d['uid'], join_year=join_year, admission_type__value=admission_type, admission_through__value="J&K").exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL") | Q(admission_status__value="FAILED") | Q(admission_status__value="PASSED"))).count()
						q_f_km = StudentPrimDetail.objects.filter(dept_detail=d['uid'], join_year=join_year, admission_type__value=admission_type, admission_through__value="KM (KASHMIR MIGRANT)").exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL") | Q(admission_status__value="FAILED") | Q(admission_status__value="PASSED"))).count()
						q_f_direct = StudentPrimDetail.objects.filter(dept_detail=d['uid'], join_year=join_year, admission_type__value=admission_type, admission_through__value="DIRECT").exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL") | Q(admission_status__value="FAILED") | Q(admission_status__value="PASSED"))).count()
						q_f_ups1 = StudentPrimDetail.objects.filter(dept_detail=d['uid'], join_year=join_year, admission_type__value=admission_type).exclude(uniq_id__in=StudentPrimDetail.objects.filter(Q(admission_status__value="WITHDRAWAL") | Q(admission_status__value="FAILED") | Q(admission_status__value="PASSED"))).count()
						if admission_type == "LATERAL":
							# cap = CourseDetail.objects.filter(course_id=course_id).exclude(dept__value='AS').get()
							capacity = list(RegistrarSessionCapacity.objects.filter(course=d['uid'], session=registrar_session).values('capacity', 'lateral_capacity'))
							data.append({'branch': d['dept__value'], 'COUNSELLING': q_f_ups, 'FW': q_f_fw, 'j_k': q_f_jk, 'km': q_f_km, 'DIRECT': q_f_direct, 'EWS': q_f_ews, 'total_seats': d['capacity'], 'f_occupied': q_f_ups + q_f_direct, 'course': d['course_id__value'], 'lateral_capacity': capacity[0]['lateral_capacity'], 'occupied': q_f_ups1})
							c = c + q_f_ups
							fw = fw + q_f_fw
							jk = jk + q_f_jk
							ews = ews + q_f_ews
							km = km + q_f_km
							dir = dir + q_f_direct
							ts = ts + capacity[0]['capacity']
							fo = fo + q_f_ups + q_f_direct
							lc = lc + capacity[0]['lateral_capacity']
							o = o + q_f_ups1
						else:
							capacity = list(RegistrarSessionCapacity.objects.filter(course=d['uid'], session=registrar_session).values('capacity', 'lateral_capacity'))
							data.append({'branch': d['dept__value'], 'COUNSELLING': q_f_ups, 'FW': q_f_fw, 'j_k': q_f_jk, 'km': q_f_km, 'DIRECT': q_f_direct, 'EWS': q_f_ews, 'total_seats': d['capacity'], 'f_occupied': q_f_ups + q_f_direct, 'course': d['course_id__value']})
							c = c + q_f_ups
							fw = fw + q_f_fw
							jk = jk + q_f_jk
							ews = ews + q_f_ews
							km = km + q_f_km
							dir = dir + q_f_direct
							ts = ts + capacity[0]['capacity']
							fo = fo + q_f_ups + q_f_direct
							lc = lc + capacity[0]['lateral_capacity']
							o = o + q_f_ups1

					status = 200
					total.append({'COUNSELLING': c,
								  'FW': fw,
								  'j_k': jk,
								  'km': km,
								  'EWS': ews,
								  'DIRECT': dir,
								  'total_seats': ts,
								  'f_occupied': fo,
								  'lateral_capacity': lc,
								  'occupied': o})
					data_values = {'data': data, 'total': total}
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status)


def shift_student(request):
	data_values = {}
	status = 403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					if request.GET['request_type'] == 'form_data':
						course = get_course()
						admission_status = get_status()
						status = 200
						data_values = {'course': course, 'admission_status': admission_status}
				elif request.method == 'POST':
					session_name = request.session['Session_name']

					data = json.loads(request.body)
					sem_id = data['sem_to']
					section = data['section_to']
					branch = data['branch_to']
					admission_status = data['admission_status']
					uniq_ids = data['uniq_ids']

					q_get_sem_no = StudentSemester.objects.filter(sem_id=sem_id).values('sem')
					year = math.ceil(q_get_sem_no[0]['sem'] / 2)

					# for uniq_id in uniq_ids:
					student_session = generate_session_table_name("studentSession_", session_name)

					q_update = student_session.objects.filter(uniq_id__in=uniq_ids).exclude(section__status="DELETE").update(section_id=section, sem=sem_id, year=year)

					if sem_id == 311 or sem_id == 312:
						q_update2 = StudentPrimDetail.objects.filter(uniq_id__in=uniq_ids).update(admission_status=admission_status)
					else:
						q_update2 = StudentPrimDetail.objects.filter(uniq_id__in=uniq_ids).update(admission_status=admission_status, dept_detail=branch)
					status = 200
					data_values = {'msg': 'Student Shifted Successfully'}

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(data=data_values, status=status)

#   #################################################### Section######################################################################


def section(request):

	data_values = {}
	qry = {}
	data = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					if(request.GET['request_type'] == 'course'):
						qry['course'] = get_course()
						data_values = {'data': qry}
						status = 200
					elif(request.GET['request_type'] == 'branch'):
						course = request.GET['course']
						qry['branch'] = get_branch(course)
						data_values = {'data': qry}
						status = 200
					elif(request.GET['request_type'] == 'semester'):
						branch = request.GET['branch']
						qry['sem'] = get_semester(branch)
						data_values = {'data': qry}
						status = 200
					elif(request.GET['request_type'] == 'previous'):
						qry3 = Sections.objects.exclude(status="DELETE").count()
						qry4 = list(Sections.objects.exclude(status="DELETE").values('section_id', 'section', 'sem_id', 'sem_id__sem', 'dept', 'dept__dept__value', 'dept', 'dept__course__value'))
						data_values = {'data': qry4}
						status = 200
					else:
						status = 300
						data_values = {'msg': "Wrong Request! Please try again"}

				elif request.method == 'POST':
					body = json.loads(request.body)
					branch = body['Branch']
					sem = body['Semester']
					no_section = int(body['No_section'])
					if no_section <= 26:
						changed = set(map(str, map(lambda x: chr(65 + x), range(0, no_section))))
					else:
						changed = set(map(str, map(lambda x: chr(65 + x), range(0, 26))))
						changed1 = set(map(str, map(lambda x: chr(64 + int(x / 26)) + chr(65 + int(x % 26)), range(26, no_section))))
						changed.update(changed1)
					qry = set(Sections.objects.filter(dept=branch, sem_id=sem).exclude(status="DELETE").values_list('section', flat=True))
					inst = changed.difference(qry)
					dele = qry.difference(changed)
					qry = Sections.objects.filter(dept=branch, sem_id=sem, section__in=dele).exclude(status="DELETE").update(status="DELETE")
					obj = (Sections(dept=CourseDetail.objects.get(uid=branch), sem_id=StudentSemester.objects.get(sem_id=sem), status="INSERT", section=sec) for sec in inst)
					qry = Sections.objects.bulk_create(obj)
					status = 200
					data_values = {'msg': "Data Added Succesfully"}
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(status=status, data=data_values)


def insert_roll(request):
	data_values = {}
	qry = {}
	qry1 = []
	data = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					if (request.GET['request_type'] == 'course'):
						qry['course'] = get_course()
						data_values = {'data': qry}
					if (request.GET['request_type'] == 'branch'):
						course = request.GET['course']
						qry['branch'] = get_branch(course)
						data = {'uid': '1', 'dept_id__value': 'ALL'}
						qry['branch'].append(data)
						year1 = date.today().year
						qry['year'] = []
						for i in range(int(year1), 2009, -1):
							qry['year'].append(i)
						data_values = {'data': qry}
					if (request.GET['request_type'] == 'fetch'):
						course = request.GET['Course']
						branch = request.GET['Branch']
						batch_from = request.GET['Batch_from']

						session = request.session['Session_name'].split('_')
						sess = ""
						for x in session:
							sess = sess + x
						StudentSession = eval('studentSession_' + sess)
						qry['student'] = []
						if(branch == '1'):
							qry1 = get_branch(course)
							for q in qry1:
								qry2 = list(StudentSession.objects.filter(uniq_id__batch_from=batch_from, uniq_id__dept_detail=q['uid']).exclude(section__status="DELETE").exclude(uniq_id__admission_status__value="WITHDRAWAL").exclude(uniq_id__admission_status__value="FAILED").values('uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id', 'uniq_id__dept_detail__dept__value', 'year', 'section__section').order_by('uniq_id__name'))
								for stu in qry2:
									qry_father_name = StudentPerDetail.objects.filter(uniq_id=stu['uniq_id']).values('fname')
									if len(qry_father_name) > 0:
										stu['fname'] = qry_father_name[0]['fname']
									else:
										stu['fname'] = "---"
								qry['student'].extend(qry2)
						else:
							qry2 = list(StudentSession.objects.filter(uniq_id__batch_from=batch_from, uniq_id__dept_detail=branch).exclude(uniq_id__admission_status__value="WITHDRAWAL").exclude(uniq_id__admission_status__value="FAILED").values('uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id', 'uniq_id__dept_detail__dept__value', 'year', 'section__section').order_by('uniq_id__name'))
							for stu in qry2:
								qry_father_name = StudentPerDetail.objects.filter(uniq_id=stu['uniq_id']).values('fname')
								if len(qry_father_name) > 0:
									stu['fname'] = qry_father_name[0]['fname']
								else:
									stu['fname'] = "---"
							qry['student'] = qry2

					data_values = {'data': qry}
					status = 200

				elif request.method == 'POST':
					data = json.loads(request.body)
					for data1 in data:
						uniq_id = data1['uniq_id']
						old_roll_no = data1['Old_Roll_No']
						new_roll_no = data1['New_Roll_No']
						qry = StudentPrimDetail.objects.filter(uniq_id=uniq_id, uni_roll_no=old_roll_no).update(uni_roll_no=new_roll_no)
					status = 200
					data_values = {'msg': "Data Added Succesfully"}

				else:
					status = 403
		else:
			status = 401
	else:
		status = 400
	return JsonResponse(status=status, data=data_values)


class RegistrarScripts():

	def section_insertion(session, sem, order, no_of_section):
		StudentSession = eval('studentSession_' + session)
		students = StudentSession.objects.filter(sem=sem, uniq_id__admission_status__value="REGULAR").values_list('uniq_id', flat=True).order_by('uniq_id__name')
		print(students)
		if(order == "ALPHABETIC"):
			per_section = len(students) / no_of_section
			initial = 0
			final = per_section
			section = 151
			for x in range(0, no_of_section):
				listing = students[initial:final]
				qry = StudentSession.objects.filter(uniq_id__in=listing).update(section=Sections.objects.get(section_id=section))
				print(qry)
				section = section + 1
				initial = initial + per_section
				final = final + per_section
	# section_insertion('1819o',249,'ALPHABETIC',2)

Scripts1 = RegistrarScripts()
# Scripts1.section_insertion('1819o',249,'ALPHABETIC',2)

#################print student form at the time of registration#####################


def print_student_form(request):
	data = []
	data_values = []
	status = 200
	msg = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET' and request.GET['request_type'] == 'already_filled':

					uniq_id = request.GET['uniq_id']
					session_name = request.session['Session_name']
					# uniq_id = body['uniq_id']
					date_place = []
					date_place.append({})
					date_of_admission = list(StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('date_of_add'))
					date_place[0]['date'] = date_of_admission[0]['date_of_add']
					date_place[0]['plcae'] = "GHAZIABAD"
					session_id = request.session['Session_id']
					data.append({'header': Registration_From_Header(uniq_id, session_name, session_id)})
					data.append({'StudentPrimDetail': Student_PrimDetail(uniq_id)})
					data.append({'Student_Registration_Form_Marks_12': Student_Registration_Form_Marks_12(uniq_id)})
					data.append({'StudentPerDetail': StudentPerDetail_fun(uniq_id)})
					data.append({'Student_Registration_Form_Guardian_Details': Student_Registration_Form_Guardian_Details(uniq_id)})
					data.append({'StudentAddress': Student_Address(uniq_id)})
					data.append({'StudentDocument': Student_Registration_Form_Document(uniq_id)})
					data.append({'Student_Registration_Form_Sub_Header_Details': Student_Registration_Form_Sub_Header_Details(uniq_id, session_name)})
					data.append({'Student_Registration_Form_FamilyDetails': Student_Registration_Form_FamilyDetails(uniq_id)})
					# data.append({'Student_Registration_Form_FeeDetails':Student_Registration_Form_FeeDetails(uniq_id,session_id)})
					data.append({'Student_Registration_Form_Academic_Details': Student_Registration_Form_Academic_Details(uniq_id)})
					data.append({'Student_Registration_Form_GATE_Details': Student_Registration_Form_GATE_Details(uniq_id)})
					data.append({'date_place': date_place})

					msg = "Successfully"
					status = 200
				else:
					status = 500
					msg = "request error"
			else:
				status = 500
				msg = "permission error"
	else:
		status = 500
		msg = "AuthUser Error"
	data.append({'msg': msg})
	return JsonResponse(data=list(data), status=status, safe=False)


###################################################### Registrar Placement Policy Report ########################################################################

def placement_policy_report(request):
	data = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					status = 200
					session_name = request.session['Session_name']
					student_session = generate_session_table_name("studentSession_", session_name)
					course_val = request.GET['course_val']
					dept_detail_select = request.GET['dept_detail_select'].split(",")
					course_duration = list(CourseDetail.objects.filter(course=course_val).values('course_duration'))
					year = course_duration[0]['course_duration']
					uniq_id_list = student_session.objects.filter(sem__dept__in=dept_detail_select, year=year).values_list('uniq_id', flat=True)
					qry = StudentPrimDetail.objects.filter(uniq_id__in=uniq_id_list).values('name', 'batch_from', 'batch_to', 'exam_roll_no', 'general_rank', 'category_rank', 'gen_rank', 'uni_roll_no', 'join_year', 'email_id', 'date_of_add', 'uniq_id', 'old_uniq_id', 'form_fill_status', 'fee_waiver', 'remark', 'admission_category__value', 'admission_through__value', 'admission_type__value', 'dept_detail__dept__value', 'exam_type__value', 'stu_type__value', 'admission_status__value', 'caste__value', 'gender__value', 'lib', 'dept_detail__course__value')
					i = 0
					for q in qry:
						data.append(q)
						uid = q['uniq_id']
						q1 = student_session.objects.filter(uniq_id=uid).values('mob', 'fee_status', 'year', 'class_roll_no', 'registration_status', 'acc_reg', 'section__section', 'sem__sem', 'session__session')
						if len(q1) > 0:
							for k, v in q1[0].items():
								data[i][k] = v
							if data[i]['registration_status'] == 1:
								data[i]['registration_status'] = 'Registered'
							else:
								data[i]['registration_status'] = 'Not Registered'

						q2 = StudentAcademic.objects.filter(uniq_id=uid).values('app_no', 'year_10', 'per_10', 'max_10', 'total_10', 'year_12', 'per_12', 'max_12', 'total_12', 'phy_12', 'phy_max', 'chem_12', 'chem_max', 'math_12', 'math_max', 'eng_12', 'eng_max', 'bio_12', 'bio_max', 'pcm_total', 'is_dip', 'year_dip', 'per_dip', 'max_dip', 'total_dip', 'ug_year1', 'ug_year1_max', 'ug_year1_back', 'ug_year2', 'ug_year2_max', 'ug_year2_back', 'ug_year3', 'ug_year3_max', 'ug_year3_back', 'ug_year4', 'ug_year4_max', 'ug_year4_back', 'year_ug', 'per_ug', 'max_ug', 'total_ug', 'sem1_ug', 'sem1_ug_max', 'sem1_ug_back', 'sem2_ug', 'sem2_ug_max', 'sem2_ug_back', 'sem3_ug', 'sem3_ug_max', 'sem3_ug_back', 'sem3_ug', 'sem3_ug_max', 'sem3_ug_back', 'sem4_ug', 'sem4_ug_max', 'sem4_ug_back', 'sem5_ug', 'sem5_ug_max', 'sem5_ug_back', 'sem6_ug', 'sem6_ug_max', 'sem7_ug', 'sem7_ug_max', 'sem7_ug_back', 'sem8_ug', 'sem8_ug_max', 'sem8_ug_back', 'pg_year1', 'pg_year1_max', 'pg_year1_back', 'pg_year2', 'pg_year2_max', 'pg_year2_back', 'pg_year3', 'pg_year3_max', 'pg_year3_back', 'year_pg', 'per_pg', 'sem1_pg', 'sem1_pg_max', 'sem1_pg_back', 'sem2_pg', 'sem2_pg_max', 'sem2_pg_back', 'sem3_pg', 'sem3_pg_max', 'sem3_pg_back', 'sem4_pg', 'sem4_pg_max', 'sem4_pg_back', 'sem5_pg', 'sem5_pg_max', 'sem5_pg_back', 'sem6_pg', 'sem6_pg_max', 'sem6_pg_back', 'area_dip', 'ug_degree', 'ug_area', 'pg_degree', 'pg_area', 'board_10__value', 'board_12__value', 'uni_dip__value', 'uni_pg__value', 'uni_ug__value')
						per = 0
						if len(q2) > 0:
							if q2[0]['bio_12'] is None and q2[0]['math_12'] is None:
								pass
							elif q2[0]['bio_12'] is None:
								if (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['math_max']) > 0:
									per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['math_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['math_max'])
								else:
									per = 0
							elif q2[0]['math_12'] is None:
								if (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max']) > 0:
									per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['bio_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'])
								else:
									per = 0
							else:
								if q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'] + q2[0]['math_max'] > 0:
									per = ((q2[0]['phy_12'] + q2[0]['chem_12'] + q2[0]['bio_12'] + q2[0]['math_12']) * 100) / (q2[0]['phy_max'] + q2[0]['chem_max'] + q2[0]['bio_max'] + q2[0]['math_max'])
								else:
									per = 0
							data[i]['pcmpcbpcmb'] = round(per, 2)
							for k, v in q2[0].items():
								data[i][k] = v

						q3 = StudentAddress.objects.filter(uniq_id=uid).values('p_add1', 'p_add2', 'p_city', 'p_district', 'p_pincode', 'c_add1', 'c_add2', 'c_city', 'c_district', 'c_pincode', 'c_state__value', 'p_state__value')
						if len(q3) > 0:
							for k, v in q3[0].items():
								data[i][k] = v

						q4 = StudentFamilyDetails.objects.filter(uniq_id=uid).values('father_mob', 'father_email', 'father_income', 'father_occupation__value', 'father_dept', 'father_add', 'father_city', 'mother_mob', 'mother_email', 'mother_income', 'mother_occupation__value', 'mother_dept', 'mother_add', 'mother_city', 'gname', 'g_relation', 'g_mob', 'g_email', 'g_add', 'g_city')
						if len(q4) > 0:
							for k, v in q4[0].items():
								data[i][k] = v

						q5 = StudentPerDetail.objects.filter(uniq_id=uid).values('fname', 'mob_sec', 'dob', 'image_path', 'image_path', 'aadhar_num', 'bank_acc_no', 'pan_no', 'uan_no', 'physically_disabled', 'bg__value', 'marital_status__value', 'nationality__value', 'religion__value', 'mname', 'caste_name', 'nation_other')
						if len(q5) > 0:
							for k, v in q5[0].items():
								data[i][k] = v
						placement_data = list(PlacementPolicyNew.objects.exclude(status="DELETE").filter(uniq_id=uid).values('form_type', 'time_stamp'))

						if len(placement_data) > 0:
							data[i]['placement_form_type'] = placement_data[0]['form_type']
							data[i]['placement_time_stamp'] = placement_data[0]['time_stamp']
							data[i]['placement_form_status'] = 'Filled'
						else:
							data[i]['placement_form_type'] = '--'
							data[i]['placement_time_stamp'] = '--'
							data[i]['placement_form_status'] = 'Not Filled'
						data[i]['sno'] = i + 1
						i += 1

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(data={'data': data}, status=status)


def delete_student(request):
	data = {}
	status = 200
	msg = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET' and request.GET['request_type'] == 'DELETE':

					uniq_id = request.GET['uniq_id']
					session_details = list(Semtiming.objects.values_list('session_name', flat=True))

					for session_name in session_details:
						try:
							student_session = generate_session_table_name("studentSession_", session_name)
							student_session.objects.filter(uniq_id=uniq_id).delete()
						except:
							pass

					StudentAddress.objects.filter(uniq_id=uniq_id).delete()
					StudentAcademic.objects.filter(uniq_id=uniq_id).delete()
					StudentPerDetail.objects.filter(uniq_id=uniq_id).delete()
					StudentFamilyDetails.objects.filter(uniq_id=uniq_id).delete()
					StudentDocument.objects.filter(uniq_id=uniq_id).delete()
					StudentPrimDetail.objects.filter(uniq_id=uniq_id).delete()

					msg = "Successfully"
					status = 200

				elif request.method == 'GET' and request.GET['request_type'] == 'GET_LIST':

					data_values = list(StudentPrimDetail.objects.values("name", "batch_from", "batch_to", "exam_roll_no", "general_rank", "category_rank", "gen_rank", "uni_roll_no", "join_year", "email_id", "date_of_add", "uniq_id", "old_uniq_id", "form_fill_status", "fee_waiver", "remark", "remark_detail", "admission_category__value", "admission_through__value", "admission_type__value", "dept_detail__dept__value", "exam_type__value", "lib", "stu_type__value", "admission_status__value", "caste", "gender", "old_uniq_id", "time_stamp"))
					data['data'] = data_values
					msg = "Successfully"
					status = 200
				else:
					status = 500
					msg = "request error"
			else:
				status = 500
				msg = "permission error"
	else:
		status = 500
		msg = "AuthUser Error"
	data['msg'] = msg
	return JsonResponse(data=data, status=status, safe=False)


def faculty_report(request):
	data = []
	if checkpermission(request, [rolesCheck.ROLE_REGISTRAR_REPORT]) == statusCodes.STATUS_SUCCESS:
		session = request.session['Session']
		session_name = request.session['Session_name']
		sem_type = request.session['sem_type']
		if int(session_name[:2]) < 19:
			return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET, 'form_data')):
				session_range = str('20' + str(int(session_name[:2]) - 1) + '-20' + str(int(session_name[:2])))
				previous_session_name = Semtiming.objects.filter(session=session_range).values_list('session_name', flat=True)

				emps = EmployeePerdetail.objects.filter(emp_id__emp_category__value="FACULTY").exclude(emp_id='00007').exclude(emp_id__emp_status='SEPARATE').values('emp_id', 'emp_id__name', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__doj', 'emp_id__mob', 'aadhar_num')
				max_total_subjects = 0
				for emp in emps:
					emp_data = {}
					subject_array = []
					emp_data['subjects'] = []
					for k, v in emp.items():
						emp_data[k] = v
					emp_data['total_experience'] = get_total_experience(emp['emp_id'], {})
					max_sub = 0
					# for ses in previous_session_name:
					#     FacultyTime = generate_session_table_name('FacultyTime_', ses)
					#     subjects = FacultyTime.objects.filter(emp_id=emp['emp_id']).exclude(status="DELETE").values('subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name').distinct()
					#     if len(subjects) > 0:
					#         max_sub = max_sub + len(subjects)
					#         for i, sub in enumerate(subjects):
					#             emp_data['subjects'].append(str(sub['subject_id__sub_alpha_code'] + '-' + sub['subject_id__sub_num_code']))

					#     break
					FacultyTime = generate_session_table_name('FacultyTime_', session_name)
					subjects = FacultyTime.objects.filter(emp_id=emp['emp_id']).exclude(status="DELETE").values('subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name').distinct()
					if len(subjects) > 0:
						max_sub = max_sub + len(subjects)
						for i, sub in enumerate(subjects):
							emp_data['subjects'].append(str(sub['subject_id__sub_alpha_code'] + '-' + sub['subject_id__sub_num_code']))
					if int(max_sub) > int(max_total_subjects):
						max_total_subjects = int(max_sub)
					data.append(emp_data)
				data = {'data': data, 'max_subjects': max_total_subjects}
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def faculty_univ_marks_report(request):
	print(1)
	emp_id = request.session['hash1']
	data = []
	if checkpermission(request, [rolesCheck.ROLE_REGISTRAR_REPORT, rolesCheck.ROLE_STUDENT_REPORT]) == statusCodes.STATUS_SUCCESS:
		session = request.session['Session']
		session_name = request.session['Session_name']
		sem_type = request.session['sem_type']
		if int(session_name[:2]) < 19:
			return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET, 'subject_type')):
				data = get_subject_type()

			elif(requestType.custom_request_type(request.GET, 'form_data')):
				subject_type = request.GET['subject_type'].split(',')
				session_range = str('20' + str(int(session_name[:2]) - 1) + '-20' + str(int(session_name[:2])))
				emps = EmployeePrimdetail.objects.filter(emp_category__value="FACULTY").exclude(emp_id="00007").exclude(emp_status="SEPARATE").values('emp_id', 'name', 'dept__value', 'desg__value', 'dept', 'desg')

				for emp in emps:
					previous_session_name = Semtiming.objects.filter(session=session_range).values_list('session_name', flat=True)
					for ses in previous_session_name:
						emp[ses] = []
						FacultyTime = generate_session_table_name('FacultyTime_', ses)
						subjects = FacultyTime.objects.filter(emp_id=emp['emp_id'], subject_id__subject_type__in=subject_type).exclude(subject_id__status="DELETE").exclude(status="DELETE").values('subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'subject_id__sem').distinct()
						for sub in subjects:
							section_id = list(FacultyTime.objects.filter(emp_id=emp['emp_id'], subject_id__subject_type__in=subject_type, subject_id=sub['subject_id'], subject_id__sem=sub['subject_id__sem']).exclude(status="DELETE").exclude(subject_id__status="DELETE").values_list('section', flat=True).distinct())
							sub_name = str(sub['subject_id__sub_name'] + ' (' + sub['subject_id__sub_alpha_code'] + '-' + sub['subject_id__sub_num_code'] + ')')
							params = {'session_name': ses, 'subject_id': sub['subject_id'], 'sem': sub['subject_id__sem'], 'section': section_id}
							details = get_university_marks_subject_wise(params)
							details['subject_id'] = sub['subject_id']
							details['subjects_name'] = sub_name
							emp[ses].append(details)
					data.append(emp)
			elif(requestType.custom_request_type(request.GET, 'form_data_section_wise')):
				subject_type = request.GET['subject_type'].split(',')
				session_name = '1920o'
				emps = EmployeePrimdetail.objects.filter(emp_category__value="FACULTY").exclude(emp_id="00007").exclude(emp_status="SEPARATE").values('emp_id', 'name', 'dept__value', 'desg__value', 'dept', 'desg')

				for emp in emps:
					FacultyTime = generate_session_table_name('FacultyTime_', session_name)
					subjects = FacultyTime.objects.filter(emp_id=emp['emp_id'], subject_id__subject_type__in=subject_type).exclude(subject_id__status="DELETE").exclude(status="DELETE").values('subject_id', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'subject_id__sem','subject_id__sem__sem','subject_id__sem__dept__dept__value','subject_id__sem__dept__dept','subject_id__sem__dept__course','subject_id__sem__dept__course__value').distinct()
					fac_data = []
					for sub in subjects:
						section_id = list(FacultyTime.objects.filter(emp_id=emp['emp_id'], subject_id__subject_type__in=subject_type, subject_id=sub['subject_id'], subject_id__sem=sub['subject_id__sem']).exclude(status="DELETE").exclude(subject_id__status="DELETE").values('section','section__section').distinct())
						sub_name = str(sub['subject_id__sub_name'] + ' (' + sub['subject_id__sub_alpha_code'] + '-' + sub['subject_id__sub_num_code'] + ')')
						for sec in section_id:
							params = {'session_name': session_name, 'subject_id': sub['subject_id'], 'sem': sub['subject_id__sem'], 'section': [sec['section']]}
							details = get_university_marks_subject_wise(params)
							details['subject_id'] = sub['subject_id']
							details['subjects_name'] = sub_name
							details['dept'] = sub['subject_id__sem__dept__dept__value']
							details['course'] = sub['subject_id__sem__dept__course__value']
							details['sem'] = sub['subject_id__sem__sem']
							details['section'] = sec['section__section']
							fac_data.append(details)
					emp['data'] = fac_data
					data.append(emp)
			return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def branch_change(request):
	session_name = request.session['Session_name']
	StudentBranchChange = generate_session_table_name("StudentBranchChange_", session_name)
	studentSession = generate_session_table_name('studentSession_', session_name)
	emp_id = request.session['hash1']
	if checkpermission(request, [rolesCheck.ROLE_REGISTRAR]) == statusCodes.STATUS_SUCCESS:
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET, 'onload')):
				course = get_course()
				data = {"course": course}
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET, 'branch')):
				branch = get_branch(request.GET['course_id'])
				data = {"branch": branch}
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET, 'semester')):
				Semester = get_semester(request.GET['branch_id'])
				data = []
				for i in Semester:
					if(i['sem'] % 2 == 1):
						sem = {}
						sem['sem'] = i['sem']
						sem['sem_id'] = i['sem_id']
						sem['dept__course__value'] = i['dept__course__value']
						data.append(sem)
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET, 'section')):
				section = get_section(request.GET['sem_id'])
				data = {"section": section}
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET, 'student')):
				section = request.GET['section_id']
				student = get_students2([section], session_name)
				data = {"student": student}
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET, 'view_previous')):
				details = list(StudentBranchChange_1920o.objects.filter(status='INSERT').values('id', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__uni_roll_no', 'old_section__section', 'new_section__section', 'uniq_id__uniq_id__lib', 'old_section__dept_id__dept__value', 'new_section__dept_id__dept__value', 'emp_id__name', 'emp_id', 'old_section__sem_id__sem', 'new_section__sem_id__sem', 'date', 'uniq_id__uniq_id__dept_detail__course__value').order_by('-id'))
				data = {"details": details}
				return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

		elif requestMethod.POST_REQUEST(request):
			data1 = json.loads(request.body)
			uniq_id = data1['uniq_id']
			new_section = data1['new_section']
			old_section = data1['old_section']
			Date = date.today()
			for i in uniq_id:
				qry = StudentBranchChange.objects.filter(uniq_id=studentSession.objects.get(uniq_id=i)).values()
				if len(qry) > 0:
					qry2 = StudentBranchChange.objects.filter(uniq_id=studentSession.objects.get(uniq_id=i)).update(status='DELETE')

				StudentBranchChange.objects.create(uniq_id=studentSession.objects.get(uniq_id=i), emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), new_section=Sections.objects.get(section_id=new_section), old_section=Sections.objects.get(section_id=old_section), change_type="S", date=Date)
				new_sem = list(Sections.objects.filter(section_id=new_section).values_list('sem_id', flat=True))
				sem = None
				if len(new_sem) > 0:
					sem = new_sem[0]
				studentSession.objects.filter(uniq_id__in=uniq_id).update(section=new_section, sem=new_sem[0])

			data = {"msg": "Data Recorded Succesfully"}
			return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST, statusCodes.STATUS_BAD_REQUEST)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Case1(year, sem, uniq_id, session):
	StudentSession = eval('studentSession_' + session)
	qry = list(StudentSession.objects.filter(uniq_id=uniq_id[0]).values('uniq_id__dept_detail__course'))
	if year == 1 and qry[0]['uniq_id__dept_detail__course'] == 12 and sem == 1:
		return True
	else:
		return False


def Case2(year, sem, uniq_id, session):
	StudentSession = eval('studentSession_' + session)
	qry = list(StudentSession.objects.filter(uniq_id=uniq_id[0]).values('uniq_id__dept_detail__course'))
	if sem == 1 or (year == 2 and qry[0]['uniq_id__dept_detail__course'] == 12 and sem == 3):
		return True
	else:
		return False


def Case3(sem, uniq_id, session):
	StudentSession = eval('studentSession_' + session)
	qry = StudentSession.objects.filter(uniq_id=uniq_id[0]).values('uniq_id__batch_from', 'uniq_id__batch_to')
	duration = qry[0]['uniq_id__batch_to'] - qry[0]['uniq_id__batch_from']

	if sem == duration * 2 - 1:
		return True
	else:
		return False


def promote_student(request):
	data_values = {}
	qry = {}
	data = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if check == 200:
				session = request.session['Session_name']
				# session="1920e"
				StudentSession = eval('studentSession_' + session)
				if request.method == 'GET':
					if (request.GET['request_type'] == 'course'):
						qry['course'] = get_course()
						data_values = {'data': qry}

					if(request.GET['request_type'] == 'branch'):
						course = request.GET['course']
						qry['branch'] = get_branch(course)
						year1 = date.today().year
						qry['year'] = []
						for i in range(int(year1), 2009, -1):
							qry['year'].append(i)

						data_values = {'data': qry}

					if(request.GET['request_type'] == 'fetch'):
						course = request.GET['Course']
						branch = request.GET['Branch']
						batch_from = request.GET['Batch_from']
						course_duration = request.GET['Course_duration']
						course_duration = int(course_duration) * 2

						branch_array = branch.split(",")

						if(batch_from != 'ALL'):
							qry['student'] = list(StudentSession.objects.filter(uniq_id__batch_from=batch_from, uniq_id__dept_detail__in=branch_array).exclude(uniq_id__in=StudentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED"))).values('uniq_id', 'registration_status', 'year', 'fee_status', 'uniq_id__gender__value', 'section__section', 'sem__sem', 'sem__dept__course__value', 'sem__dept__dept__value', 'uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id__admission_status__value', 'session__session', 'uniq_id__dept_detail__dept__value').order_by('uniq_id__name'))
						else:
							qry['student'] = list(StudentSession.objects.filter(uniq_id__dept_detail__in=branch_array).exclude(uniq_id__in=StudentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED"))).exclude(sem__sem=course_duration).values('uniq_id', 'registration_status', 'year', 'fee_status', 'uniq_id__gender__value', 'section__section', 'sem__sem', 'sem__dept__course__value', 'sem__dept__dept__value',    'uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id__admission_status__value', 'session__session', 'uniq_id__dept_detail__dept__value').order_by('uniq_id__name'))

						for q in qry['student']:
							q_pcm_sorted = StudentAcademic.objects.filter(uniq_id=q['uniq_id']).annotate(pcmperc=((F('phy_12') + F('chem_12') + F('math_12')) / (F('phy_max') + F('chem_max') + F('math_max'))) * 100).values('pcmperc')
							if q_pcm_sorted[0]['pcmperc'] is None:
								q['pcmperc'] = "---"
							else:
								q['pcmperc'] = round(float(q_pcm_sorted[0]['pcmperc']), 2)
							q_personal_details = StudentPerDetail.objects.filter(uniq_id=q['uniq_id']).values('fname')
							q['fname'] = q_personal_details[0]['fname']

						data_values = {'data': qry}

					status = 200

				elif request.method == 'POST':
					uniq_id = json.loads(request.body)
					sem_type = request.session['sem_type']
					# sem_type = 'even'
					qry = list(StudentSession.objects.filter(uniq_id=uniq_id[0]).values('sem', 'sem__sem', 'sem__dept', 'year', 'uniq_id__dept_detail__course'))
					sem = qry[0]['sem__sem']
					if sem_type == 'odd':
						if sem % 2 == 0:
							sem += 1
					elif sem_type == 'even':
						if sem % 2 != 0:
							sem += 1
					year = int(math.ceil(sem / 2.0))

					check1 = Case1(year, sem, uniq_id, session)  # [For 1st year BTech (new admission)
					check2 = Case2(year, sem, uniq_id, session)  # [For 1st year going to 2nd year or for 1st year of any other course]
					check3 = Case3(sem, uniq_id, session)  # [For Final year students of different courses]

					if (check3 == False):
						if(check1 == True):  # Alloting Sections [For 1st year BTech (new admission)]
							sem_id = StudentSemester.objects.filter(sem=sem, dept__dept__value='AS').values('sem_id')
							pcm_sorted_nonCS = StudentAcademic.objects.filter(uniq_id__in=uniq_id, cs_12__isnull=True).annotate(pcmperc=(F('phy_12') + F('chem_12') + F('math_12')) / (F('phy_max') + F('chem_max') + F('math_max'))).values_list('uniq_id', flat=True).order_by('-pcmperc', 'uniq_id__name')
							pcm_sorted_withCS = StudentAcademic.objects.filter(uniq_id__in=uniq_id).exclude(cs_12__isnull=True).annotate(pcmperc=(F('phy_12') + F('chem_12') + F('math_12')) / (F('phy_max') + F('chem_max') + F('math_max'))).values_list('uniq_id', flat=True).order_by('-pcmperc', 'uniq_id__name')

							sections = Sections.objects.filter(sem_id=sem_id[0]['sem_id']).exclude(status="DELETE").values('section_id' , 'section').order_by('section')
							sec = len(sections)  # Number of Sections

							sections_NONCS=[178,179,180,181,182,183,185,186,187,188,189,190,191,192,193,194,252]
							sections_CS=[195,196,197,198,199,200,201]

							for i in range(len(sections_CS)):  # For alloting sections on PCM % criteria with CS
								uniq_list1 = pcm_sorted_withCS[i::(2 * len(sections_CS))]
								uniq_list2 = pcm_sorted_withCS[(2 * len(sections_CS) - (i + 1))::2 * len(sections_CS)]
								uniq_list = uniq_list1 + uniq_list2
					
								data_update = StudentSession.objects.filter(Q(uniq_id__admission_status__value="REGULAR") | Q(uniq_id__admission_status__value="RE-ADMITTED")).filter(uniq_id__in=uniq_list).exclude(section__status="DELETE").update(sem=StudentSemester.objects.get(sem_id=sem_id[0]['sem_id']), section=Sections.objects.get(section_id=sections_CS[i]), year=year, session=Semtiming.objects.get(session_name=session))

							for i in range(len(sections_NONCS)):  # For alloting sections on PCM % criteria without CS
								uniq_list1 = pcm_sorted_nonCS[i::(2 * len(sections_NONCS))]
								uniq_list2 = pcm_sorted_nonCS[(2 * len(sections_NONCS) - (i + 1))::2 * len(sections_NONCS)]
								uniq_list = uniq_list1 + uniq_list2

								data_update = StudentSession.objects.filter(Q(uniq_id__admission_status__value="REGULAR") | Q(uniq_id__admission_status__value="RE-ADMITTED")).filter(uniq_id__in=uniq_list).exclude(section__status="DELETE").update(sem=StudentSemester.objects.get(sem_id=sem_id[0]['sem_id']), section=Sections.objects.get(section_id=sections_NONCS[i]), year=year, session=Semtiming.objects.get(session_name=session))



						elif(check2 == True):  # For 1st year Students of all Courses and 1st year BTech students going to 2nd year
							depts = list(StudentSession.objects.filter(uniq_id__in=uniq_id).values('uniq_id__dept_detail').distinct())
							for i in depts:
								sem_id = StudentSemester.objects.filter(sem=sem, dept=i['uniq_id__dept_detail']).values('sem_id')
								names = StudentPrimDetail.objects.filter(uniq_id__in=uniq_id, dept_detail=i['uniq_id__dept_detail']).values_list('uniq_id', flat=True).order_by('name')
								sections = Sections.objects.filter(sem_id=sem_id[0]['sem_id']).exclude(status="DELETE").values('section_id').order_by('section')
								total_name = len(names)  # Number of Names(Unique ID's)
								sec = len(sections)  # Number of Sections

								start = 0
								end = total_name // sec  # Strenght in one Section
								total = end

								for i in range(sec):
									if i == (sec - 1):
										total = len(names) + 1
									uniq_list = names[start:total]
									data_update = StudentSession.objects.filter(Q(uniq_id__admission_status__value="REGULAR") | Q(uniq_id__admission_status__value="RE-ADMITTED")).filter(uniq_id__in=uniq_list).exclude(section__status="DELETE").update(sem=StudentSemester.objects.get(sem_id=sem_id[0]['sem_id']), section_id=Sections.objects.get(section_id=sections[i]['section_id']), year=year, session=Semtiming.objects.get(session_name=session))

									start += end
									total += end

						else:  # For rest of the students of all courses + Lateral Entry
							null_sec_uniq_list = list(StudentSession.objects.filter(Q(uniq_id__admission_status__value="REGULAR") | Q(uniq_id__admission_status__value="RE-ADMITTED")).filter(uniq_id__in=uniq_id, section__isnull=True).exclude(section__status="DELETE").values_list('uniq_id', flat=True))  # To check Lateral Entry ( having "NULL" Section_id)
							uniq_id = list(set(uniq_id) - set(null_sec_uniq_list))
							section = list(StudentSession.objects.filter(Q(uniq_id__admission_status__value="REGULAR") | Q(uniq_id__admission_status__value="RE-ADMITTED")).filter(uniq_id__in=uniq_id).exclude(section__status="DELETE").values('section', 'sem', 'section__section', 'uniq_id__dept_detail').distinct().order_by("section"))
							for i in section:
								uniq_list = list(StudentSession.objects.filter(uniq_id__in=uniq_id, section=i['section'], sem=i['sem']).exclude(section__status="DELETE").values_list('uniq_id', flat=True))
								if (sem == 1 or sem == 2) and qry[0]['uniq_id__dept_detail__course'] == 12:
									i['uniq_id__dept_detail'] = 59
									section_id = Sections.objects.filter(sem_id__sem=sem, sem_id__dept=i['uniq_id__dept_detail'], section=i['section__section']).exclude(status="DELETE").values('section_id', 'sem_id')
								else:
									section_id = Sections.objects.filter(sem_id__sem=sem, sem_id__dept=i['uniq_id__dept_detail'], section=i['section__section']).exclude(status="DELETE").values('section_id', 'sem_id')

								data_update = StudentSession.objects.filter(Q(uniq_id__admission_status__value="REGULAR") | Q(uniq_id__admission_status__value="RE-ADMITTED")).filter(uniq_id__in=uniq_list).exclude(section__status="DELETE").update(sem=StudentSemester.objects.get(sem_id=section_id[0]['sem_id']), section_id=Sections.objects.get(section_id=section_id[0]['section_id']), year=year, session=Semtiming.objects.get(session_name=session))
							uniq_list = null_sec_uniq_list  # In the case of Lateral Entry

							depts = list(StudentSession.objects.filter(uniq_id__in=uniq_list).exclude(section__status="DELETE").values('uniq_id__dept_detail').distinct())
							for i in depts:
								sem_id = StudentSemester.objects.filter(sem=sem, dept=i['uniq_id__dept_detail']).values('sem_id')
								names = StudentPrimDetail.objects.filter(uniq_id__in=uniq_id, dept_detail=i['uniq_id__dept_detail']).values_list('uniq_id', flat=True).order_by('name')
								sections = Sections.objects.filter(sem_id=sem_id[0]['sem_id']).exclude(status="DELETE").values('section_id').order_by('section')
								total_name = len(names)  # Number of Names(Unique ID's)
								sec = len(sections)  # Number of Sections

								start = 0
								end = total_name // sec  # Strenght in one Section

								for i in range(sec):
									uniq_list = names[start:end]
									data_update = StudentSession.objects.filter(Q(uniq_id__admission_status__value="REGULAR") | Q(uniq_id__admission_status__value="RE-ADMITTED")).filter(uniq_id__in=uniq_list).exclude(section__status="DELETE").update(sem=StudentSemester.objects.get(sem_id=sem_id[0]['sem_id']), section_id=Sections.objects.get(section_id=sections[i]['section_id']), year=year, session=Semtiming.objects.get(session_name=session))

									start += (end - start)
									end += (end - start)

									if i == (sec - 1):
										end = total_name

					status = 200
					data_values = {"msg": "Data Added Successfully"}
				else:
					status = 403
		else:
			status = 401
	else:
		status = 400

	return JsonResponse(status=status, data=data_values)


def getPincode(request):
	if requestMethod.GET_REQUEST(request):
		value = request.GET['value'].strip().replace(' ', "%20")
		if (requestType.custom_request_type(request.GET, 'pincode')): #Seacrh by Pincodes
			url="https://api.postalpincode.in/pincode/"+value
			response = urllib.request.urlopen(url)
			data = json.loads(response.read())
	
		elif (requestType.custom_request_type(request.GET, 'post_office')): #Search by City / PostOffices
			url="https://api.postalpincode.in/postoffice/"+value
			response = urllib.request.urlopen(url)
			data = json.loads(response.read())

		if(data[0]["Status"]!="Error"):
			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS) #Status Code 200 with Data + Message
		else:
			return functions.RESPONSE(data,statusCodes.STATUS_CONFLICT_WITH_MESSAGE) # Status Code 202 without Data + Message
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

def trim(im):
	bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
	diff = ImageChops.difference(im, bg)
	diff = ImageChops.add(diff, diff, 2.0, -100)
	bbox = diff.getbbox()
	if bbox:
		return im.crop(bbox)

def digital_id(request):
	print(request.META)
	data= {}
	msg = "" 
	status=200
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			print(check)
			check=200
			session_data = get_odd_sem(request.session['Session'])
			session_name = session_data['session_name']
			if check==200:
				if request.method=="POST":
					body= json.loads(request.body)

					# print(body)
					# #[4205, 4206, 4208]
					user = AuthUser.objects.filter(username=request.user).extra(select={'faculty_id': 'username'}).values('faculty_id')
					faculty_id = user[0]['faculty_id']#7102
					body=json.loads(request.body)
					student_prim=StudentPrimDetail.objects.filter(uniq_id__in=body).values('lib','name',"batch_from","batch_to","dept_detail__course__value","dept_detail__dept__value","dept_detail","gender__value")
					student_session = generate_session_table_name("studentSession_", session_name)
					HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
					# session_name='1920o'
					student_hostel = HostelSeatAlloted.objects.filter(paid_status='ALREADY PAID',uniq_id__in=body).exclude(status="DELETE").values("hostel_part__value").distinct()
					mobile = student_session.objects.filter(uniq_id__in=body).values('mob')
					print(mobile)
					# print(student_hostel)
					# print(student_prim)
					student_per=StudentPerDetail.objects.filter(uniq_id__in=body).values('fname','mob_sec','dob')
					print(student_per)
					student_address=StudentAddress.objects.filter(uniq_id__in=[12,13200000,1000000]).values(
						"p_add1","p_add2", "p_city","p_district",'uniq_id',"p_pincode","c_add1","c_add2","c_city","c_district", "c_pincode", "c_state","p_state__value" )
					print(student_address)
					# return
					img1='id_front.jpeg'
					img2='id_back.jpeg'
					pdfs=[]
					page_count=0
					for i in range(0,len(student_prim),3):
						page_div=30
						a4_paper_size=2480 , 3508
						a4_paper = Image.new(mode='RGB', size=(5000, 7000), color=(255, 255, 255, 0))
						a4_paper.thumbnail(a4_paper_size, Image.ANTIALIAS)
						for count in range(i,i+3):
							if(count<len(student_prim)):
								# stu_photo = list(StudentPerDetail.objects.filter(uniq_id=uniq_id).values_list('image_path',flat=True))
								im2 =Image.open('pranjal.png')
								# print("yes")
								data_lib=student_prim[count]['lib']
								id_front = Image.open(img1)
								id_back = Image.open(img2)                        
								size = 653,1007
								W=653
								H=1007
								id_front.thumbnail(size, Image.ANTIALIAS)
								id_back.thumbnail(size, Image.ANTIALIAS)
								qr = qrcode.make(data_lib)
								qr = trim(qr)
								qr = qr.resize((170, 170), Image.NEAREST)
								gender=''
								adrr=''
								id_back.paste(qr,(250,300))
								student_addr= str(student_address[count]['p_add1'])+"#"+str(student_address[count]['p_add2'])+"#"+str(student_address[count][ 'p_city'])+"#"+str(student_address[count]['p_district'])+"#"+str(student_address[count]['p_state__value'])+"#"+str(student_address[count]['p_pincode'])
								student_addr.upper()
								print(student_addr)
								student_addr=student_addr.replace('None','----')
								student_addr=student_addr.replace('NONE','----')
								student_addr_l1=student_addr.split('#')
								font = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 26)
								font1 = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 35)
								font2 = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 25)    
								font3=  ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 30)                    
								draw = ImageDraw.Draw(id_front)
								draw_back =ImageDraw.Draw(id_back)
								draw_back.text((200, 40),str(student_per[count]['dob']),(0, 0, 0),font=font,align="left")
								draw_back.text((200, 80),str(mobile[count]['mob']),(0, 0, 0),font=font,align="left")
								w_adr,h_addr=draw.textsize(student_addr_l1)
								hg = 122
								draw_back.text((183, hg),student_addr_l1[0].upper(),(0, 0, 0),font=font2,align="left")
								hg+=30
								draw_back.text((173, hg),student_addr_l1[1].upper(),(0, 0, 0),font=font2,align="left")
								hg+=30
								district  = student_addr_l1[2].upper()+"  "+student_addr_l1[3].upper()
								draw_back.text((180, hg),district,(0, 0, 0),font=font2,align="left")
								hg+=30
								state = student_addr_l1[4]+"  - "+student_addr_l1[5]
								draw_back.text((200, hg),state.upper(),(0, 0, 0),font=font2,align="left")

								##############################################################
								w,h=draw.textsize(student_prim[count]['name'])
								student_pic = im2.resize((250, 250), Image.NEAREST)
								id_front.paste(student_pic,(((W-w)//2)-70, (H-h)//2-200))
								draw.text((((W-w)//2)-100, (H-h)//2+60),student_prim[count]['name'],(0, 0, 0),font=font1,align="left")
								draw.text(((W//2)-140, H-60),"  "+data_lib, (0, 0, 0), font=font1)
								if(student_prim[count]['gender__value']=="MALE"):
									relation="S/o"
								else:
									relation="D/o"
								draw.text((((W-w)//2)-170, (H-h)//2 +105), relation, (0, 0, 0), font=font)
								draw.text((((W-w)//2)-70, (H-h)//2 +105),student_per[count]['fname'], (0, 0, 0), font=font)
								draw.text((((W-w)//2)-100, (H-h)//2 +140),student_prim[count]['dept_detail__course__value'], (0, 0, 0), font=font)
								draw.text((((W-w)//2)+20, (H-h)//2 +140),"Student", (0, 0, 0), font=font)
								draw.text((((W-w)//2)+140, (H-h)//2 +140),student_prim[count]['dept_detail__dept__value'], (0, 0, 0), font=font)
								draw.text((((W-w)//2)-20, (H-h)//2 +180),str(student_prim[count]['batch_from'])+"-", (0, 0, 0), font=font)
								draw.text((((W-w)//2)+60, (H-h)//2 +180),str(student_prim[count]['batch_to']), (0, 0, 0), font=font)
								draw.text((((W-w)//2)+40, (H-h)//2 +284),str(student_prim[count]['batch_to']), (0, 0, 0), font=font)
								a4_paper.paste(id_front,(587,10+page_div))
								a4_paper.paste(id_back,(1250,10+page_div))
								page_div+=1100
						filename="digital_id"+str(page_count)+".pdf"
						a4_paper.save(settings.FILE_PATH+ filename, "PDF", resolution=250.0)
						pdfs.append(settings.FILE_PATH + filename)                    
						page_count+=1
					merger = PdfFileMerger()
					for pdf in pdfs:
						merger.append(open(pdf, 'rb'))
					filename="final.pdf"
					with open(settings.FILE_PATH+ filename, 'wb') as fout:
						merger.write(fout)
					with open(settings.FILE_PATH+ filename, 'rb') as pdf:
						response = HttpResponse(pdf, content_type='application/pdf')
						response['Content-Disposition'] = 'inline;filename=some_file.pdf'
					return response
					pdf.closed
					status = 200
					return response
				else:
					print("request error")
			else:
				print("not checked")
		else:
			status = 403
			msg = "Not Authorized"
	else:
		status = 500
		msg = "Error"

	data={"msg":msg}
	return JsonResponse(data,status=status)

def digital_id_employee(request):
	data= {}
	msg = "" 
	status=200
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			session_data = get_odd_sem(request.session['Session'])
			session_name = session_data['session_name']
			if check==200:
				if request.method=="POST":
					body= json.loads(request.body)
					# employe_prim = EmployeePrimdetail.objects.filter(emp_id__in=body).values('name','emp_id','dept__value','current_pos__value','mob','doj')
					employe_data = EmployeePerdetail.objects.filter(emp_id__in=body).values('emp_id','emp_id__name','emp_id__emp_category__value','emp_id__dept__value','emp_id__desg__value','emp_id__mob','emp_id__doj','dob','image_path','bg__value')
					employe_add = EmployeeAddress.objects.filter(emp_id__in=body).values('p_add1','p_add2','p_city','p_district','p_pincode','p_state__value')
					img1='id_front1.jpeg'
					img2='id_back1.jpeg'
					pdfs=[]
					page_count=0
					for i in range(0,len(employe_data),3):
						page_div=30
						a4_paper_size=2480 , 3508
						a4_paper = Image.new(mode='RGB', size=(5000, 7000), color=(255, 255, 255, 0))
						a4_paper.thumbnail(a4_paper_size, Image.ANTIALIAS)
						for count in range(i,i+3):
							if(count<len(employe_data)):
								im2 =Image.open('pranjal.png')
								yr = str(employe_data[count]['emp_id__doj']).split('-')[0]
								if employe_data[count]['emp_id__emp_category__value'] == "STAFF":
									lib_id = 'S'+str(yr)+str(employe_data[count]['emp_id'])
								elif employe_data[count]['emp_id__emp_category__value'] == "FACULTY":
									lib_id = 'F'+str(yr)+str(employe_data[count]['emp_id'])
								elif employe_data[count]['emp_id__emp_category__value'] == "TECHNICAL STAFF":
									lib_id = 'TS'+str(yr)+str(employe_data[count]['emp_id'])
								print(lib_id)
								id_front = Image.open(img1)
								id_back = Image.open(img2)                        
								size = 653,1007
								W=653
								H=1007
								id_front.thumbnail(size, Image.ANTIALIAS)
								id_back.thumbnail(size, Image.ANTIALIAS)
								emp_add= str(employe_add[count]['p_add1'])+"#"+str(employe_add[count]['p_add2'])+"#"+str(employe_add[count][ 'p_city'])+"#"+str(employe_add[count]['p_district'])+"#"+str(employe_add[count]['p_state__value'])+"#"+str(employe_add[count]['p_pincode'])
								emp_add.upper()
								print(emp_add)
								emp_add=emp_add.replace('None','----')
								emp_add=emp_add.replace('NONE','----')
								emp_add=emp_add.split('#')
								font = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 26)
								font1 = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 32)
								font2 = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 28)    
								font3=  ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 40)                    
								draw = ImageDraw.Draw(id_front)
								draw_back =ImageDraw.Draw(id_back)
								qr = qrcode.make(lib_id)
								qr = trim(qr)
								qr = qr.resize((170, 170), Image.NEAREST)
								gender=''
								adrr=''
								id_front.paste(qr,(90,730))
								w,h=draw.textsize(employe_data[count]['emp_id__name'])
								student_pic = im2.resize((210, 210), Image.NEAREST)
								id_front.paste(student_pic,(((W-w)//2)-50, (H-h)//2-230))
								ll =len(str(employe_data[count]['emp_id__name']))
								draw.text((((W-w)//2)-(ll*6), (H-h)//2),employe_data[count]['emp_id__name'],(0, 0, 0),font=font1,align="center")
								draw.text(((W//2)-140, H-60),"  "+lib_id, (0, 0, 0), font=font3)
								draw.text((((W-w)//2)+30, (H-h)//2 +50), employe_data[count]['emp_id__dept__value'], (0, 0, 0), font=font)
								ee=len(str(employe_data[count]['emp_id__desg__value']))
								draw.text((((W-w)//2)-(ee*6), (H-h)//2 +105),employe_data[count]['emp_id__desg__value'], (0, 0, 0), font=font2)
								draw.text((((W-w)//2)+130, (H-h)//2 +155),employe_data[count]['emp_id'], (0, 0, 0), font=font)
								################################back#######################################################
								doj = str(employe_data[count]['emp_id__doj'])
								doj=re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', doj)
								dob = str(employe_data[count]['dob'])
								dob=re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', dob)
								draw_back.text((210, 45),dob,(0, 0, 0),font=font,align="left")
								draw_back.text((210, 85),doj,(0, 0, 0),font=font,align="left")
								draw_back.text((210, 125),str(employe_data[count]['bg__value']),(0, 0, 0),font=font,align="left")
								draw_back.text((210, 165),str(employe_data[count]['emp_id__mob']),(0, 0, 0),font=font,align="left")
								w_adr,h_addr=draw.textsize(emp_add)
								hg = 207
								draw_back.text((183, hg),emp_add[0].upper(),(0, 0, 0),font=font2,align="left")
								hg+=30
								# add_1 = emp_add[1].upper()
								
								add_1 = emp_add[1].upper()

								q = len(add_1)//25+1
								print(q,'len') 
								for e in range(1,q+1):
									if e==1:
										s = add_1[(e-1)*25:e*25]+'-'
									elif e==q:
										s= add_1[(e-1)*25:e*25]+','
									else:
										s='-'+add_1[(e-1)*25:e*25]+'-'
									draw_back.text((173, hg),s,(0, 0, 0),font=font,align="left")
									hg+=30
								# hg+=30
								district  = emp_add[2].upper()+"  "+emp_add[3].upper()
								draw_back.text((180, hg),district,(0, 0, 0),font=font2,align="left")
								hg+=30
								state = emp_add[4]+"  - "+emp_add[5]
								draw_back.text((200, hg),state.upper(),(0, 0, 0),font=font2,align="left")
								a4_paper.paste(id_front,(587,10+page_div))
								a4_paper.paste(id_back,(1250,10+page_div))
								page_div+=1100
						filename="digital_id"+str(page_count)+".pdf"
						a4_paper.save(settings.FILE_PATH+ filename, "PDF", resolution=250.0)
						pdfs.append(settings.FILE_PATH + filename)                    
						page_count+=1
					merger = PdfFileMerger()
					for pdf in pdfs:
						merger.append(open(pdf, 'rb'))
					filename="final.pdf"
					with open(settings.FILE_PATH+ filename, 'wb') as fout:
						merger.write(fout)
					with open(settings.FILE_PATH+ filename, 'rb') as pdf:
						response = HttpResponse(pdf, content_type='application/pdf')
						response['Content-Disposition'] = 'inline;filename=some_file.pdf'
					return response
					pdf.closed
					status = 200
					return response
				else:
					print("request error")
			else:
				print("not checked")
		else:
			status = 403
			msg = "Not Authorized"
	else:
		status = 500
		msg = "Error"

	data={"msg":msg}
	return JsonResponse(data,status=status)

def digital_id_hostel(request):
	data= {}
	msg = "" 
	status=200
	if 'HTTP_COOKIE' in request.META:
		# print("yes")
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			session_data = get_odd_sem(request.session['Session'])
			session_name = session_data['session_name']
			if check==200:
				if request.method=="POST":
					body= json.loads(request.body)
					# print(body)
					# #[4205, 4206, 4208]
					user = AuthUser.objects.filter(username=request.user).extra(select={'faculty_id': 'username'}).values('faculty_id')
					faculty_id = user[0]['faculty_id']#7102
					body=json.loads(request.body)
					student_prim=StudentPrimDetail.objects.filter(uniq_id__in=body).values('uniq_id','lib','name',"batch_from","batch_to","dept_detail__course__value","dept_detail__dept__value","dept_detail","gender__value")
					HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
					student_session = generate_session_table_name("studentSession_", session_name)
					# session_name='1920o'
					student_hostel = HostelSeatAlloted.objects.filter(paid_status='PAID',uniq_id__in=body).exclude(status="DELETE").values("hostel_part__value").distinct()
					# print(student_hostel)
					# print(student_prim)
					mobile = student_session.objects.filter(uniq_id__in=body).values('mob')
					# print(mobile)
					student_per=StudentPerDetail.objects.filter(uniq_id__in=body).values('fname','mob_sec','dob')
					# print(student_per)
					student_address=StudentAddress.objects.filter(uniq_id__in=body).values(
						"p_add1","p_add2", "p_city","p_district","p_pincode","c_add1","c_add2","c_city","c_district", "c_pincode", "c_state","p_state__value" )
					img1='id_front.jpeg'
					img2='id_back.jpeg'
					pdfs=[]
					page_count=0
					for i in range(0,len(student_prim),3):
						page_div=30
						a4_paper_size=2480 , 3508
						a4_paper = Image.new(mode='RGB', size=(5000, 7000), color=(255, 255, 255, 0))
						a4_paper.thumbnail(a4_paper_size, Image.ANTIALIAS)
						for count in range(i,i+3):
							if(count<len(student_prim)):
								# print(student_prim[count])
								stu_photo = list(StudentPerDetail.objects.filter(uniq_id=student_prim[count]['uniq_id']).values_list('image_path',flat=True))
								stu_photo = 'https://tech.kiet.edu/upload_images/StudentMusterroll/Student_images/'+stu_photo[0]
								im2 =Image.open('pranjal.png')
								student_hostel = HostelSeatAlloted.objects.filter(paid_status='PAID',uniq_id=body[count]).exclude(status="DELETE").values("hostel_part__value").distinct()
								# print(student_hostel)
								# print("yes")
								data_lib=student_prim[count]['lib']
								id_front = Image.open(img1)
								id_back = Image.open(img2)                        
								size = 653,1007
								W=653
								H=1007
								id_front.thumbnail(size, Image.ANTIALIAS)
								id_back.thumbnail(size, Image.ANTIALIAS)
								student_addr= str(student_address[count]['p_add1'])+"#"+str(student_address[count]['p_add2'])+"#"+str(student_address[count][ 'p_city'])+"#"+str(student_address[count]['p_district'])+"#"+str(student_address[count]['p_state__value'])+"#"+str(student_address[count]['p_pincode'])
								student_addr.upper()
								# print(student_addr)
								student_addr=student_addr.replace('None','----')
								student_addr=student_addr.replace('NONE','----')
								student_addr_l1=student_addr.split('#')
								print(student_addr_l1)
								font = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 26)
								font1 = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 35)
								font2 = ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 25)    
								font3=  ImageFont.truetype("/home/samyakjain/.local/lib/python3.6/site-packages/django/contrib/admin/static/admin/fonts/arial.ttf", 30)                    
								draw = ImageDraw.Draw(id_front)
								draw_back =ImageDraw.Draw(id_back)
								draw_back.text((200, 40),str(student_per[count]['dob']),(0, 0, 0),font=font,align="left")
								draw_back.text((200, 80),str(mobile[count]['mob']),(0, 0, 0),font=font,align="left")
								w_adr,h_addr=draw.textsize(student_addr_l1)
								hg = 122
								print(student_addr_l1)
								add = student_addr_l1[0].upper()
								q = len(add)//25+1 
								for e in range(1,q+1):
									if e==q and e==1:
										s = add[(e-1)*25:e*25]+','
									elif e==q:
										s = '-'+add[(e-1)*25:e*25]+','
									elif e==1:
										s= add[(e-1)*25:e*25]+'-'
									else:
										s='-'+add[(e-1)*25:e*25]+'-'
									draw_back.text((173, hg),s,(0, 0, 0),font=font,align="left")
									hg+=30
								add_1 = student_addr_l1[1].upper()
								q = len(add_1)//25+1 
								for e in range(1,q+1):
									if e==q and e==1:
										s = add_1[(e-1)*25:e*25]+','
									elif e==q:
										s = '-'+add_1[(e-1)*25:e*25]+','
									elif e==1:
										s= add_1[(e-1)*25:e*25]+'-'
									else:
										s='-'+add_1[(e-1)*25:e*25]+'-'
									draw_back.text((173, hg),s,(0, 0, 0),font=font,align="left")
									hg+=30
								district  = student_addr_l1[2].upper()+"  "+student_addr_l1[3].upper()
								draw_back.text((180, hg),district,(0, 0, 0),font=font2,align="left")
								hg+=30
								state = student_addr_l1[4]+"  - "+student_addr_l1[5]
								draw_back.text((200, hg),state.upper(),(0, 0, 0),font=font2,align="left")
								w,h=draw.textsize(student_prim[count]['name'])
								# print(w,h)
								student_pic = im2.resize((250, 250), Image.NEAREST)
								id_front.paste(student_pic,(((W-w)//2)-70, (H-h)//2-200))
								# len_name=len(student_prim[count]['name'])//2
								draw.text((((W-w)//2)-100, (H-h)//2+60),student_prim[count]['name'],(0, 0, 0),font=font1,align="left")
								print((W-w)//2)
								draw.text(((W//2)-140, H-60),"  "+data_lib, (0, 0, 0), font=font1)
								stud = student_hostel[0]['hostel_part__value']+" HOSTEL"
								draw.text((((W-w)//2)-120, ((H-h)//2)+340),stud,(0, 0, 0),font=font3,align="left")
								# draw.text((((W-w)//2)-180, ((H-h)//2)+380),"HOSTEL",(0, 0, 0),font=font,align="left")
								# 'gender__value': 'MALE'
								if(student_prim[count]['gender__value']=="MALE"):
									relation="S/o"
								else:
									relation="D/o"
								draw.text((((W-w)//2)-170, (H-h)//2 +105), relation, (0, 0, 0), font=font)
								draw.text((((W-w)//2)-70, (H-h)//2 +105),student_per[count]['fname'], (0, 0, 0), font=font)
								draw.text((((W-w)//2)-100, (H-h)//2 +140),student_prim[count]['dept_detail__course__value'], (0, 0, 0), font=font)
								draw.text((((W-w)//2)+20, (H-h)//2 +140),"Student", (0, 0, 0), font=font)
								draw.text((((W-w)//2)+140, (H-h)//2 +140),student_prim[count]['dept_detail__dept__value'], (0, 0, 0), font=font)
								# 2019-2023
								draw.text((((W-w)//2)-20, (H-h)//2 +180),str(student_prim[count]['batch_from'])+"-", (0, 0, 0), font=font)
								draw.text((((W-w)//2)+60, (H-h)//2 +180),str(student_prim[count]['batch_to']), (0, 0, 0), font=font)
								draw.text((((W-w)//2)+40, (H-h)//2 +284),str(student_prim[count]['batch_to']), (0, 0, 0), font=font)
								a4_paper.paste(id_front,(587,10+page_div))
								a4_paper.paste(id_back,(1250,10+page_div))
								page_div+=1100
						filename="digital_id"+str(page_count)+".pdf"
						a4_paper.save(settings.FILE_PATH_NEW+ filename, "PDF", resolution=250.0)
						pdfs.append(settings.FILE_PATH_NEW + filename)                    
						page_count+=1
					merger = PdfFileMerger()
					for pdf in pdfs:
						merger.append(open(pdf, 'rb'))
					filename="final.pdf"
					with open(settings.FILE_PATH_NEW + filename, 'wb') as fout:
						merger.write(fout)
					with open(settings.FILE_PATH_NEW+ filename, 'rb') as pdf:
						response = HttpResponse(pdf, content_type='application/pdf')
						response['Content-Disposition'] = 'inline;filename=some_file.pdf'
					return response
					pdf.closed
					status = 200
					return response
				else:
					print("request error")
			else:
				print("not checked")
		else:
			status = 403
			msg = "Not Authorized"
	else:
		status = 500
		msg = "Error"

	data={"msg":msg}
	return JsonResponse(data,status=status)




