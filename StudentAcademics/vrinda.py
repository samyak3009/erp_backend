from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime,timedelta
from django.utils import timezone
import json
from django.conf import settings
from django.http import HttpResponse,JsonResponse
import time
import copy
import random
from datetime import date
from datetime import datetime
from dateutil import tz
import math
from decimal import Decimal
import calendar
from dateutil.relativedelta import relativedelta
import collections
from operator import itemgetter
from django.db.models import Q,Sum,Count,Max,F

from login.models import EmployeeDropdown,EmployeePrimdetail,AuthUser
from musterroll.models import EmployeePerdetail
from Registrar.models import *
from .models import *

from login.views import checkpermission,generate_session_table_name
from dashboard.views import academic_calendar
from .views import *
# from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime,timedelta
from django.utils import timezone
import json
from django.conf import settings
from django.http import HttpResponse,JsonResponse
import time
import copy
import random
from datetime import date
from datetime import datetime
from dateutil import tz
import math
from decimal import Decimal
import calendar
from dateutil.relativedelta import relativedelta
import collections
from operator import itemgetter
from django.db.models import Q,Sum,Count,Max,F

from login.models import EmployeeDropdown,EmployeePrimdetail,AuthUser
from musterroll.models import EmployeePerdetail
from Registrar.models import *
from .models import *

from login.views import checkpermission,generate_session_table_name
from dashboard.views import academic_calendar
from .views import *

def StudentAttendanceRegister(request):
	data_values={}
	status=403
	print(request)
	# subject=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[1369,1371,425,337,319])
			if check == 200 and ('A' in request.session['Coordinator_type'] or 'H' in request.session['Coordinator_type']):
				session=request.session['Session_id']
				session_name=request.session['Session_name']
				sem_type=request.session['sem_type']
				Attendance = generate_session_table_name("Attendance_",session_name)
				SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
				studentSession = generate_session_table_name("studentSession_",session_name)
				studentAttStatus = generate_session_table_name("StudentAttStatus_",session_name)
				print(session_name)
				if(request.method=='GET'):
					if request.GET['request_type'] == 'stu_att_report':
						uniq_id = request.GET['uniq_id']
						section = studentSession.objects.filter(uniq_id=uniq_id).values('section')[0]['section']
						subject = request.GET['subject'].split(',')
						from_date= datetime.strptime(str(request.GET['from_date']).split('T')[0],"%Y-%m-%d").date()
						to_date= datetime.strptime(str(request.GET['to_date']).split('T')[0],"%Y-%m-%d").date()
						att_type = request.GET['att_type'].split(',')
						uniq_id_subject=list(studentAttStatus.objects.filter(uniq_id=uniq_id).exclude(status__contains="DELETE").exclude(att_id__status="DELETE").values_list('att_id__subject_id',flat=True).distinct())
						print(uniq_id_subject)
						q_sub1 = studentAttStatus.objects.filter(att_id__subject_id__in=subject,uniq_id=uniq_id).exclude(status="DELETE").values_list('att_id__subject_id',flat=True).distinct()
						print(q_sub1)
						q_sub =  SubjectInfo.objects.filter(id__in=q_sub1).exclude(status="DELETE").values('sub_num_code','sub_alpha_code','sub_name','subject_type','subject_unit','max_ct_marks','max_ta_marks','max_att_marks','max_university_marks','added_by','time_stamp','status','session','sem','id','no_of_units','subject_unit__value','subject_type__value','added_by__name').order_by('id')
						print(q_sub)
						query_student = studentSession.objects.filter(uniq_id=uniq_id).values('uniq_id','uniq_id__name','section__sem_id__sem','section__sem_id','section__section','year','section__sem_id__dept__dept__value','class_roll_no','uniq_id__uni_roll_no','mob','registration_status','reg_form_status','reg_date_time','fee_status','att_start_date','uniq_id__dept_detail__dept__value','uniq_id__dept_detail__dept__value','uniq_id__lib_id','uniq_id__gender','uniq_id__gender__value').order_by('class_roll_no')
						start_date=query_student[0]['att_start_date']

						stu_att_data=[]
						subject2=[]
						subject1 = []
						graph_att_subjectwise=[['Subjects', 'Percentage', { 'role': 'style' },{'role': 'annotation'}]]  #to store attendance percentage for graphical subjectwise attendance
						for sub in q_sub:
							status = get_student_subject_att_status(uniq_id,sub['id'],max(datetime.strptime(str(from_date),"%Y-%m-%d").date(),datetime.strptime(str(start_date),"%Y-%m-%d").date()),to_date,att_type,session_name)
							stu_att_data=[]
							for s in status:
								s['att_type']='N'
								if s['att_id__isgroup']=='Y':
									s['att_type']='G'
								elif 'NORMAL' not in s['att_type__value']  and 'REMEDIAL' not in s['att_type__value'] and 'TUTORIAL' not in s['att_type__value']:
									s['att_type']='E'
								if 'SUBSTITUTE' in s['att_type__value']:
									s['att_type']='S'
								stu_att_data.append({'date':s['att_id__date'],'lecture':s['att_id__lecture'],'att_status':s['present_status'],'attendance_type':s['att_type'],'subject_name':sub['sub_name'],'marked_by':s['marked_by'],'marked_by_name':s['marked_by__name']})


							subject2.append({'subject':sub,'data':list(stu_att_data)})
						subject1.append(subject2)
						sub_total_att = get_student_attendance(uniq_id,max(datetime.strptime(str(from_date),"%Y-%m-%d").date(),datetime.strptime(str(start_date),"%Y-%m-%d").date()),to_date,session,att_type,list(q_sub),1,[],session_name)
						query_student[0]['net_data']=sub_total_att
#######################################Divyanshu - code for graph - calculating percentage of attendance subjectwise ################################################################################################						
						for graph_att in sub_total_att['sub_data']:
							if graph_att['total'] > 0:
								percentage=round((100*graph_att['present_count'])/graph_att['total'])
							else:
								percentage=0
								
							if percentage < 60:
								graph_att_subjectwise.append([graph_att['sub_name'],percentage,'#EE1D1D',percentage])
							elif percentage>74:
								graph_att_subjectwise.append([graph_att['sub_name'],percentage,'#32CA56',percentage])
							else:
								graph_att_subjectwise.append([graph_att['sub_name'],percentage,'#ff7f50',percentage])
#####################################################################################################################################################################################################################						
						status=200
						data_values={'data':query_student[0],'att_data':subject1,'net_data':sub_total_att, 'graphical':graph_att_subjectwise}
						print(data_values)
					elif request.GET['request_type'] == 'mobikiet_att':
						#session_name = '1920o'
						#session = 8
						StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
						final_data = {}
						from_date= datetime.strptime(str(request.GET['from_date']).split('T')[0],"%Y-%m-%d").date()
						to_date= datetime.strptime(str(request.GET['to_date']).split('T')[0],"%Y-%m-%d").date()
						uniq_id = request.GET['uniq_id']
						normal_id = []
						if 'att_category' not in request.GET or 'att_type' not in request.GET:
							att_type_li = get_sub_attendance_type(session)
							att_type = [t['sno'] for t in att_type_li]
							e_att = []
							for t in att_type_li:
								if 'NORMAL' in t['value'] or 'REMEDIAL' in t['value'] or 'TUTORIAL' in t['value']:
									normal_id.append(t['sno'])
								else:
									e_att.append(t['sno'])
							# normal_id.append(t['sno'] for t in att_type_li)
							att_category_query = get_att_category_from_type(att_type, session)
							att_category = [t['attendance_category'] for t in att_category_query]
						else:
							att_type_li = []
							att_category = request.GET['att_category'].split(',')
							if att_category[0] == '':
								att_category = []
							att_type = request.GET['att_type'].split(',')
						# session_name = '1819e'
						StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
						studentSession = generate_session_table_name("studentSession_", session_name)
						q_att_date = studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date', 'section__sem_id')
						subjects = get_student_subjects(q_att_date[0]['section__sem_id'], session_name)
						att_data = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, att_type, subjects, 1, att_category, session_name)
						final_data['total_present'] = att_data['present_count']
						final_data['total_total'] = att_data['total']
						final_data['error'] = False
						final_data['message'] = ""
						final_data['update'] = False
						final_data['data'] = []
						final_data['attendance_type'] = []
						############# ATTENDANCE TYPE ATTENDANCE #########################
						normal_attendance = 0
						# print(att_type_li)
						get_cat = get_att_category_from_type(normal_id, session)
						category = [t['attendance_category'] for t in get_cat]
						e_att_adta = get_student_attendance(uniq_id, min(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, normal_id, subjects, 1, category, session_name)
						for att in att_type_li:

							# if 'NORMAL' in att['value'] or 'REMIDIAL' in att['value'] or 'TUTORIAL' in att['value']:
							#   normal_id.append(att['sno'])
							final_att_data = {}
							type_att = []
							type_att.append(att['sno'])
							get_cat = get_att_category_from_type(type_att, session)
							category = [t['attendance_category'] for t in get_cat]
							##### FOR TOTAL #######
							qry = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type__in=type_att, approval_status__contains="APPROVED", att_id__date__range=[from_date, to_date]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
							if len(qry) > 0:
								total = len(qry)
							else:
								total = 0
							#######################
							q_stu_details = studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
							q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')
							year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
							course = q_year[0]['dept__course']

							query_att = AttendanceSettings.objects.filter(course=course, session=session, year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
							if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
								type_att.extend(normal_id)
								new_att_data = get_student_attendance(uniq_id, min(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, type_att, subjects, 1, category, session_name)

								# if att['sno']==652:
								# print(new_att_data,'vrinda')
								if int(total) > 0 and int(new_att_data['present_count']) != 0:
									if int(normal_attendance) > 0:
										# print( new_att_data['present_count'],new_att_data['total'],normal_attendance,att['value'])
										new_att_data['present_count'] = new_att_data['present_count'] - e_att_adta['present_count']
										final_att_data = {'total': total, 'present_count': new_att_data['present_count'], 'value': att['value'], 'color': get_color_attendance_type(att['value'])}
										# print(final_att_data,'final_att_data')

										final_data['attendance_type'].append(final_att_data)

							else:
								new_att_data = get_student_attendance(uniq_id, max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, session, type_att, subjects, 1, category, session_name)
								if int(new_att_data['present_count']) != 0:
									# if 'NORMAL' in att['value']:
									if att['sno'] in normal_id:
										normal_attendance += int(new_att_data['present_count'])
									final_att_data = {'total': total, 'present_count': new_att_data['present_count'], 'value': att['value'], 'color': get_color_attendance_type(att['value'])}
									final_data['attendance_type'].append(final_att_data)
						#################################################################
						for att in att_data['sub_data']:
							if '-' in str(att['id']):
								stu_sub_data = []
							else:
								stu_sub_data = get_student_subject_att_status(uniq_id, att['id'], max(datetime.strptime(str(from_date), "%Y-%m-%d").date(), datetime.strptime(str(q_att_date[0]['att_start_date']), "%Y-%m-%d").date()), to_date, att_type, session_name)
							date_li = []
							lec_li = []
							attendance_type_li = []
							status_li = []

							for sub in stu_sub_data:
								date_li.append(sub['att_id__date'])
								lec_li.append(sub['att_id__lecture'])
								status_li.append(sub['present_status'])
								if sub['att_type__value'] in ['SUBSTITUTE']:
									attendance_type_li.append('S')
								elif sub['att_type__value'] not in ['REMEDIAL', 'NORMAL', 'TUTORIAL']:
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
							final_data['data'].append({'date': date_li, 'lecture': lec_li, 'status': status_li, 'attedance_type': attendance_type_li, 'subject_name': att['sub_name'], 'sub_code': att['sub_alpha_code'] + "-" + str(att['sub_num_code']), 'lecture_present': att['present_count'], 'lecture_total': att['total'], 'att_type_color': get_color_app()})
						status=200
						data_values = final_data

				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=data_values,status=status)
