from django.shortcuts import render
from django.db.models import F
from django.db.models import Min,Count
from django.http import HttpResponse, JsonResponse
from datetime import date, datetime
from login.views import checkpermission, generate_session_table_name
import json
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, requestMethod, functions
from StudentMMS.constants_functions import requestType

from login.models import EmployeeDropdown
from StudentAcademics.views import *
from StudentAcademics.models import  * 
from Registrar.models import StudentDropdown


from StudentMMS.models import *

def StoredAttendance(request):	
	session_name = request.session['Session_name']
	print(session_name)
	session=list(Semtiming.objects.filter(session_name=session_name).values('uid'))
	studentSession = generate_session_table_name("studentSession_", session_name)
	Store_Attendance_Total = generate_session_table_name("Store_Attendance_Total_",session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_",session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	course=list(CourseDetail.objects.values('course').distinct())
	dept_list=[]
	departments=[]
	semester=[]
	semester_id=[]
	sections_list=[]
	uniq_id_stude=[]
	for dept in course:
		dept_list.append(list(CourseDetail.objects.filter(course=dept['course']).values('uid')))
	for all_department in dept_list:
		for depart in all_department:
			departments.append(depart['uid'])
	for all_sem in departments:
		semlist=[]
		semester_dept=list(StudentSemester.objects.filter(dept=all_sem).values('sem'))
		semester.append(semester_dept)
		semlist.append(semester_dept)
		for sem_li in semlist:
			for sem in sem_li:
				qry=list(StudentSemester.objects.filter(dept=all_sem,sem=sem['sem']).values('sem_id'))
				semester_id.append(qry)
	semester_list=[]

	for semester_li_li in semester_id:
		for sections in semester_li_li:
			semester_list.append(sections['sem_id'])
			sections_list.append(list(Sections.objects.filter(sem_id=sections['sem_id']).values('section_id')))

	
	semester_id=[123]
	sections_list=[[{'section_id':12},{'section_id':13}]]
	for semno in semester_list:
		for sectli in sections_list:
			for li in sectli:
				uniq_id=list(studentSession.objects.filter(section__section_id=li['section_id'],sem__sem_id=semno).values('uniq_id'))
				for t in uniq_id:
					uniq_id_stude.append(t['uniq_id'])
				att_type_li = get_sub_attendance_type(session[0]['uid'])
				att_type=[t['sno'] for t in att_type_li]
				att_category_query=get_att_category_from_type(att_type,session[0]['uid'])
				att_category=[t['att_category'] for t in att_category_query]
	uniq_id_stude=[1039]			
	for uniq in uniq_id_stude:
		bulk_data=[]
		# print(uniq)
		q_att_date=studentSession.objects.filter(uniq_id=uniq).values('att_start_date','section__sem_id')
		subjects=get_student_subjects(q_att_date[0]['section__sem_id'],session_name)
		present_normal=[]
		sub_id=[]
		for att in att_type_li:
			if 'NORMAL' in att['value']:
				normal_id=att['sno']
			type_att=[]
			normal_and_extra_att=[]
			type_att.append(att['sno'])
			get_cat = get_att_category_from_type(type_att, session[0]['uid'])
			category = [t['attendance_category'] for t in get_cat]

			qry =StudentAttStatus.objects.filter(uniq_id=uniq, att_type__in=type_att, approval_status__contains="APPROVED", att_id__date__range=[q_att_date[0]['att_start_date'], date.today()]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
			if len(qry) > 0:
				total = len(qry)
			else:
				total = 0	

			q_stu_details=studentSession.objects.filter(uniq_id=uniq).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
			q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')
			year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
			course = q_year[0]['dept__course']

			query_att=AttendanceSettings.objects.filter(course=course, session=session[0]['uid'], year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
			if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
				type_att.append(normal_id)
				student_sub_att=get_student_attendance(uniq,q_att_date[0]['att_start_date'],date.today(),session[0]['uid'],type_att,subjects,1,att_category,session_name)
				# print(student_sub_att,att['value'])
				for present in student_sub_att['sub_data']:
					if present['id']!='----':
						if present['total']>0  and present['present_count']!=0:
							normal_and_extra_att.append(present['present_count'])
				mapped=zip(sub_id,normal_and_extra_att,present_normal)	
				mapped=set(mapped)
				for map1 in mapped:
					if map1[1]>map1[2] and map1[1]-map1[2]!=0:
						qry={
						"subject_id":map1[0],
						"att_total":map1[1]-map1[2],
						"att_present":map1[1]-map1[2],
						"att_type":att['sno']
						}
						bulk_data.append(qry)
			else:
				student_sub_att=get_student_attendance(uniq,q_att_date[0]['att_start_date'],date.today(),session[0]['uid'],type_att,subjects,1,att_category,session_name)
				# print(student_sub_att,att['value'])
				for sub in student_sub_att['sub_data']:
					if sub['id']!='----':
						if sub['total']>0 and sub['present_count']!=0:
							present_normal.append(sub['present_count'])
							sub_id.append(sub['id'])
							qry={
							"subject_id":sub['id'],
							"att_total":sub['total'],
							"att_present":sub['present_count'],
							"att_type":att['sno']
							}
							bulk_data.append(qry)
		objs=(Store_Attendance_Total(uniq_id=studentSession.objects.get(uniq_id=uniq),subject=SubjectInfo.objects.get(id=data['subject_id']) ,att_type=StudentAcademicsDropdown.objects.get(sno=data['att_type']),attendance_total=data['att_total'],attendance_present=data['att_present'])for data in bulk_data)
		querry=Store_Attendance_Total.objects.bulk_create(objs)	
									
	return JsonResponse({"attendance":"Stored"})

def get_total_attendance(request):
	session_name = request.session['Session_name']
	session=list(Semtiming.objects.filter(session_name=session_name).values('uid'))
	studentSession = generate_session_table_name("studentSession_", session_name)
	Store_Attendance_Total = generate_session_table_name("Store_Attendance_Total_",session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_",session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
	att_type_li = get_sub_attendance_type(session[0]['uid'])
	att_type=[t['sno'] for t in att_type_li]
	att_category_query=get_att_category_from_type(att_type,session[0]['uid'])
	att_category=[t['att_category'] for t in att_category_query]
	uniq_id_li=request.GET['uniq_id_li'].split(',')
	att_percent_li=[]
	data_li=[]
	for uniq_id in uniq_id_li:
		data={}
		uniq_id_total_att=get_attendance_type_total(request,uniq_id,att_type_li)
		total_att=list(Store_Attendance_Total.objects.filter(uniq_id=uniq_id).values('uniq_id').annotate(total=Sum('attendance_total')-uniq_id_total_att['total_att_type'],present=Sum('attendance_present')))
		att_percent=round((total_att[0]['present']/total_att[0]['total'])*100)
		data['uniq_id']=uniq_id
		data['att_per']=att_percent
		data_li.append(data)
	print(data_li)	

	return JsonResponse(data_li,safe=False)

def get_attendance_type_total(request,uniq_id,type_att_li):
	session_name = request.session['Session_name']
	studentSession = generate_session_table_name("studentSession_", session_name)
	Store_Attendance_Total = generate_session_table_name("Store_Attendance_Total_",session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_",session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
	session=list(Semtiming.objects.filter(session_name=session_name).values('uid'))
	total_type_attendance=0
	for att in type_att_li:
		if 'NORMAL' in att['value']:
			normal_id=att['sno']
		type_att=[]
		type_att.append(att['sno'])
		get_cat = get_att_category_from_type(type_att, session[0]['uid'])
		category = [t['attendance_category'] for t in get_cat]
		q_att_date=studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date','section__sem_id')
		qry = StudentAttStatus.objects.filter(uniq_id=uniq_id, att_type__in=type_att, approval_status__contains="APPROVED", att_id__date__range=[q_att_date[0]['att_start_date'], date.today()]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
		if len(qry) > 0:
			total = len(qry)
		else:
			total=0	
		q_stu_details=studentSession.objects.filter(uniq_id=uniq_id).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
		q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')
		year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
		course = q_year[0]['dept__course']
		query_att=AttendanceSettings.objects.filter(course=course, session=session[0]['uid'], year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
		q_att_date=studentSession.objects.filter(uniq_id=uniq_id).values('att_start_date','section__sem_id')
		subjects=get_student_subjects(q_att_date[0]['section__sem_id'],session_name)
		if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
			# print(total,att['value'])
				total_type_attendance+=total
	data={}
	data['uniq_id']=uniq_id
	data['total_att_type']=total_type_attendance
	data['att_type']=att['sno']
	return data					
			

def StoreCtWiseAttendance(request):	
	session_name = request.session['Session_name']
	session=list(Semtiming.objects.filter(session_name=session_name).values('uid'))
	studentSession = generate_session_table_name("studentSession_", session_name)
	Store_Attendance_Ct_wise = generate_session_table_name("Store_Attendance_Ctwise_",session_name)
	StudentAttStatus = generate_session_table_name("StudentAttStatus_",session_name)
	SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
	course=list(CourseDetail.objects.values('course').distinct())
	dept_list=[]
	departments=[]
	semester=[]
	semester_id=[]
	sections_list=[]
	uniq_id_stude=[]
	for dept in course:
		dept_list.append(list(CourseDetail.objects.filter(course=dept['course']).values('uid')))
	for all_department in dept_list:
		for depart in all_department:
			departments.append(depart['uid'])
	for all_sem in departments:
		semlist=[]
		semester_dept=list(StudentSemester.objects.filter(dept=all_sem).values('sem'))
		semester.append(semester_dept)
		semlist.append(semester_dept)
		for sem_li in semlist:
			for sem in sem_li:
				qry=list(StudentSemester.objects.filter(dept=all_sem,sem=sem['sem']).values('sem_id'))
				semester_id.append(qry)
	semester_list=[]

	for semester_li_li in semester_id:
		for sections in semester_li_li:
			semester_list.append(sections['sem_id'])
			sections_list.append(list(Sections.objects.filter(sem_id=sections['sem_id']).values('section_id')))

	
	semester_id=[123]
	sections_list=[[{'section_id':12},{'section_id':13}]]
	for semno in semester_list:
		for sectli in sections_list:
			for li in sectli:
				uniq_id=list(studentSession.objects.filter(section__section_id=li['section_id'],sem__sem_id=semno).values('uniq_id'))
				for t in uniq_id:
					uniq_id_stude.append(t['uniq_id'])
				att_type_li = get_sub_attendance_type(session[0]['uid'])
				att_type=[t['sno'] for t in att_type_li]
				att_category_query=get_att_category_from_type(att_type,session[0]['uid'])
				att_category=[t['att_category'] for t in att_category_query]
				exam_type = get_exam_id(session[0]['uid'])
	uniq_id_stude=[1039]		
	to_date= date.today()	
	for uniq in uniq_id_stude:
		bulk_data=[]
		q_att_date=studentSession.objects.filter(uniq_id=uniq).values('att_start_date','section__sem_id')
		subjects=get_student_subjects(q_att_date[0]['section__sem_id'],session_name)
		present_normal=[]
		sub_id=[]
		flag=0
		for exam in exam_type:
			flag = flag+1;
			# print(exam)
			for att in att_type_li:
				if 'NORMAL' in att['value']:
					normal_id=att['sno']
				type_att=[]
				normal_and_extra_att=[]
				type_att.append(att['sno'])
				get_cat = get_att_category_from_type(type_att, session[0]['uid'])
				category = [t['attendance_category'] for t in get_cat]

				qry =StudentAttStatus.objects.filter(uniq_id=uniq, att_type__in=type_att, approval_status__contains="APPROVED", att_id__date__range=[q_att_date[0]['att_start_date'], date.today()]).filter(Q(att_category__in=category) | Q(att_category__isnull=True)).exclude(status__contains='DELETE').exclude(att_id__status='DELETE').values('att_id').distinct()
				if len(qry) > 0:
					total = len(qry)
				else:
					total = 0	

				q_stu_details=studentSession.objects.filter(uniq_id=uniq).values('section__sem_id', 'uniq_id__dept_detail__course', 'section__sem_id__sem', 'year', 'uniq_id__admission_type')
				q_year = StudentSemester.objects.filter(sem_id=q_stu_details[0]['section__sem_id']).values('sem', 'dept__course')
				year = math.ceil(q_stu_details[0]['section__sem_id__sem'] / 2.0)
				course = q_year[0]['dept__course']
				ct_dates = get_ct_dates(session_name,exam['sno'],q_stu_details[0]['section__sem_id'])
				print(flag)
				if len(ct_dates)>0:
					
					if flag==1:
						# from_date=q_att_date[0]['att_start_date']
						new_from_date = q_att_date[0]['att_start_date']
						to_date = ct_dates[0]['from_date']
					else:
						to_date = ct_dates[0]['from_date']


					print(new_from_date)
					print(to_date)
					query_att=AttendanceSettings.objects.filter(course=course, session=session[0]['uid'], year=year, att_sub_cat__field="DAY-WISE ATTENDANCE", att_sub_cat__in=type_att).exclude(status='DELETE').values('att_sub_cat__value', 'att_sub_cat', 'att_per', 'criteria_per').order_by().distinct()
					if len(query_att) > 0 and float(query_att[0]['criteria_per']) > 0.0:
						type_att.append(normal_id)
						student_sub_att=get_student_attendance(uniq,new_from_date,to_date,session[0]['uid'],type_att,subjects,1,att_category,session_name)
						print(student_sub_att,att['value'])
						for present in student_sub_att['sub_data']:
							if present['id']!='----':
								if present['total']>0  and present['present_count']!=0:
									normal_and_extra_att.append(present['present_count'])
						mapped=zip(sub_id,normal_and_extra_att,present_normal)	
						mapped=set(mapped)
						for map1 in mapped:
							if map1[1]>map1[2] and map1[1]-map1[2]!=0:
								qry={
								"subject_id":map1[0],
								"att_total":map1[1]-map1[2],
								"att_present":map1[1]-map1[2],
								"att_type":att['sno'],
								"exam_id":exam['sno']
								}
								bulk_data.append(qry)
					else:
						student_sub_att=get_student_attendance(uniq,new_from_date,to_date,session[0]['uid'],type_att,subjects,1,att_category,session_name)
						print(student_sub_att,att['value'])
						for sub in student_sub_att['sub_data']:
							if sub['id']!='----':
								if sub['total']>0 and sub['present_count']!=0:
									present_normal.append(sub['present_count'])
									sub_id.append(sub['id'])
									qry={
									"subject_id":sub['id'],
									"att_total":sub['total'],
									"att_present":sub['present_count'],
									"att_type":att['sno'],
									"exam_id":exam['sno']
									}
									bulk_data.append(qry)
			new_from_date = to_date
		objs=(Store_Attendance_Ct_wise(uniq_id=studentSession.objects.get(uniq_id=uniq),exam_id=StudentAcademicsDropdown.objects.get(sno=data['exam_id']),subject=SubjectInfo.objects.get(id=data['subject_id']) ,att_type=StudentAcademicsDropdown.objects.get(sno=data['att_type']),attendance_total=data['att_total'],attendance_present=data['att_present'])for data in bulk_data)
		querry=Store_Attendance_Ct_wise.objects.bulk_create(objs)	
									
	return JsonResponse({"attendance":"Stored"})




def get_exam_id(session):
    data = []
    qry = StudentAcademicsDropdown.objects.filter(field="EXAM NAME", session=session).exclude(value__isnull=True).exclude(status="DELETE").values("sno", "value")
    for q in qry:
    	data.append({'sno': q['sno'], 'value': q['value']})
    
    # print(data)
    return data


def get_ct_dates(session_name,exam_id,sem_id):
	data=[]
	print(exam_id)
	print(sem_id)
	ExamSchedule = generate_session_table_name('ExamSchedule_',session_name)
	qry = list(ExamSchedule.objects.filter(exam_id=exam_id,sem=sem_id).exclude(status="DELETE").values("from_date", "to_date"))
	for q in qry:
		data.append(q)
	# print(data)
	return data