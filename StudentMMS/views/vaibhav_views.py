from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from login.views import checkpermission,generate_session_table_name
import json
from django.db.models import Sum,F
from itertools import groupby
from collections import Counter

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from erp.constants_functions.functions import *
from StudentMMS.constants_functions import requestType

from StudentMMS.models import *
from StudentAcademics.models import *
from StudentAcademics.views import *
from musterroll.models import EmployeePrimdetail
from Registrar.models import StudentSemester,CourseDetail,Sections
from login.models import EmployeeDropdown
from StudentAcademics.models import *

from .mms_function_views import *
from StudentAcademics.views import  get_student_subjects

def ct_wise_subjects_marks(request):
	session_name=request.session['Session_name']
	session=request.session['Session_id']
	StudentMarks = generate_session_table_name("StudentMarks_",session_name)
	Marks = generate_session_table_name("Marks_",session_name)
	# QuesPaperSectionDetails =generate_session_table_name("QuesPaperSectionDetails_",session_name)
	if requestMethod.POST_REQUEST(request):
		data = json.loads(request.body)
		dept = data['branch']
		sem = data['sem']
		section = data['section']
		exam_name = data['exam_name']

		
		sem_id=StudentSemester.objects.filter(dept=dept,sem=sem).values_list('sem_id',flat=True)
		section_id=Sections.objects.filter(dept=dept,sem_id=sem_id,section__in=section).values_list('section_id',flat=True)
		qry1 = StudentMarks.objects.filter(marks_id__section__in=list(section_id)).values('uniq_id','uniq_id__uniq_id__name').distinct()
		data2=[]
		data3=[]
		for f1 in qry1:
			data4=[]
			for exam in exam_name:
				qry2 = StudentMarks.objects.filter(uniq_id=f1['uniq_id'],marks_id__exam_id=exam).exclude(status="DELETE").values('marks_id__subject_id','marks_id__subject_id__sub_name').distinct()
				data1=[]
				for f2 in qry2:
					qry3 = StudentMarks.objects.filter(uniq_id=f1['uniq_id'],marks_id__subject_id=f2['marks_id__subject_id']).exclude(status="DELETE").values("marks","present_status",'uniq_id','uniq_id__uniq_id__name','marks_id__subject_id','marks_id__subject_id__sub_name','marks_id__subject_id__sub_num_code','marks_id__subject_id__sub_alpha_code','marks_id__subject_id__subject_type__value','marks_id__subject_id__subject_type','marks_id__exam_id','marks_id__exam_id__value')
					
					qry4=StudentMarks.objects.filter(uniq_id=f1['uniq_id'],marks_id__subject_id=f2['marks_id__subject_id'],marks_id__exam_id=exam).exclude(status="DELETE").aggregate(total_marks=Sum('marks'))
					for f3 in qry3:
						if f3['present_status']=='P' and f3['marks_id__exam_id']==exam:
							print(f3['marks'])
							f3['marks']=qry4
					data1.append({"marks":qry3[0]['marks'],"present_status":qry3[0]['present_status'],"marks_id__subject_id__sub_name":qry3[0]['marks_id__subject_id__sub_name'],"marks_id__exam_id":exam,"uniq_id":qry3[0]['uniq_id'],"uniq_id__uniq_id__name":qry3[0]['uniq_id__uniq_id__name'],"marks_id__subject_id":qry3[0]['marks_id__subject_id'],"marks_id__subject_id__sub_num_code":qry3[0]['marks_id__subject_id__sub_num_code'],"marks_id__subject_id__sub_alpha_code":qry3[0]['marks_id__subject_id__sub_alpha_code'],"marks_id__subject_id__subject_type__value":qry3[0]['marks_id__subject_id__subject_type__value'],"marks_id__subject_id__subject_type":qry3[0]['marks_id__subject_id__subject_type'],"marks_id__exam_id__value":qry3[0]['marks_id__exam_id__value']})
				data4.append({"sub":data1})
			data2.append({"ct_wise":data4,"stu_name":f1['uniq_id__uniq_id__name']})
		data3.append({"student_wise":data2})
		data={"data":data3}
	
	elif requestMethod.GET_REQUEST(request):
		if (requestType.firstrequest(request.GET)):
			data={"exam_name":get_exam_name(session)}
	return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

def ct_wise_subjects_marks_faculty(request):
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		session_name=request.session['Session_name']
		emp_id=request.session['hash1']
		StudentMarks = generate_session_table_name("StudentMarks_",session_name)
		FacultyTime = generate_session_table_name("FacultyTime_",session_name)
		Marks = generate_session_table_name("Marks_",session_name)
		if requestMethod.POST_REQUEST(request):
			data = json.loads(request.body)
			dept = data['branch']
			sem_id = data['sem']
			section_id = data['section']
			exam_name = data['exam_name']
			query = FacultyTime.objects.exclude(status='DELETE').filter(emp_id=emp_id,section__in=section_id).values('subject_id','subject_id__sub_name','subject_id__sub_alpha_code','subject_id__sub_num_code','section__sem_id__sem','section__sem_id__dept__dept__value').distinct()
			qry1 = StudentMarks.objects.filter(marks_id__section__in=list(section_id)).values('uniq_id','uniq_id__uniq_id__name').distinct()
			print(qry1)
			data2=[]
			data3=[]
			for f1 in qry1:
				data4=[]
				for exam in exam_name:
					data1=[]
					for f2 in query:
						qry3 = StudentMarks.objects.filter(uniq_id=f1['uniq_id'],marks_id__subject_id=1103,marks_id__exam_id=exam).exclude(status="DELETE").values("marks","present_status",'uniq_id','uniq_id__uniq_id__name','marks_id__subject_id','marks_id__subject_id__sub_name','marks_id__subject_id__sub_num_code','marks_id__subject_id__sub_alpha_code','marks_id__subject_id__subject_type__value','marks_id__subject_id__subject_type','marks_id__exam_id','marks_id__exam_id__value')
						# print(len(qry3))
						
						qry4=StudentMarks.objects.filter(uniq_id=f1['uniq_id'],marks_id__subject_id=f2['subject_id'],marks_id__exam_id=exam).exclude(status="DELETE").aggregate(total_marks=Sum('marks'))

						for f3 in qry3:
							
							if f3['present_status']=='P' and f3['marks_id__exam_id']==exam:
								f3['marks']=qry4
						data1.append({"marks":qry3[0]['marks'],"present_status":qry3[0]['present_status'],"marks_id__subject_id__sub_name":qry3[0]['marks_id__subject_id__sub_name'],"marks_id__exam_id":exam,"uniq_id":qry3[0]['uniq_id'],"uniq_id__uniq_id__name":qry3[0]['uniq_id__uniq_id__name'],"marks_id__subject_id":qry3[0]['marks_id__subject_id'],"marks_id__subject_id__sub_num_code":qry3[0]['marks_id__subject_id__sub_num_code'],"marks_id__subject_id__sub_alpha_code":qry3[0]['marks_id__subject_id__sub_alpha_code'],"marks_id__subject_id__subject_type__value":qry3[0]['marks_id__subject_id__subject_type__value'],"marks_id__subject_id__subject_type":qry3[0]['marks_id__subject_id__subject_type'],"marks_id__exam_id__value":qry3[0]['marks_id__exam_id__value']})
					data4.append({"sub":data1})
				data2.append({"ct_wise":data4,"stu_name":f1['uniq_id__uniq_id__name']})
			data3.append({"student_wise":data2})
			data={"data":data3}
		return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def paper_data(ques_paper_id,session_name,session,uniq_id):
	
	data=[]
	QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_",session_name)
	QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_",session_name)
	QuesPaperBTAttainment = generate_session_table_name("QuesPaperBTAttainment_",session_name)
	QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_",session_name)
	SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_",session_name)
	SubjectQuesOptions = generate_session_table_name("SubjectQuesOptions_",session_name)
	StudentMarks = generate_session_table_name("StudentMarks_",session_name)
	QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_",session_name)

	question_format=list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id=ques_paper_id).values('section_id','section_id__ques_paper_id','section_id__ques_paper_id__time'))
	if(len(question_format)==0):
		return data
	total_max_marks=QuesPaperSectionDetails.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).aggregate(total_max_marks=Sum('max_marks'))
	data.append({'time_duration':question_format[0]['section_id__ques_paper_id__time'],'Max_marks':total_max_marks.get('total_max_marks',0)})

	data[0]['bt_level_attain']=[]
	data[0]['bt_level_attain']=list(QuesPaperBTAttainment.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).values('minimum','maximum').annotate(bt_level=F('bt_level__value')))

	data[0]['section']=[]
	data[0]['session']=session

	section_data=list(QuesPaperSectionDetails.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).values('id','name','attempt_type','max_marks'))
	data[0]['section']=section_data
	# data[0]['question']=[]
	
	i=0
	for section in section_data:
		ques_list=QuestionPaperQuestions.objects.filter(ques_paper_id=ques_paper_id,section_id=section['id']).exclude(status='DELETE').values('ques_id','ques_num','section_id')
	
		section['question']=[]
		# data[0]['question']=[]

		i=0
		for k,v in groupby(ques_list,key=lambda x:x['ques_num']):
			v=list(v)[::-1]
			id_list=[]
			for t in v:
				id_list.append(t['ques_id'])

			# print(id_list)
			qry=list(SubjectAddQuestions.objects.filter(id__in=id_list).extra(select={'id_ins': 'FIELD(id,%s)' % ','.join(map(str, id_list))}, order_by=['id_ins']).values('id','description','question_img','max_marks','bt_level__value','type','co_id').distinct())
			# print(qry)

			#############################
			marks = -1
			sec_query = {}
			for q in qry:
			  sec_query = q
			  qry1 = list(StudentMarks.objects.filter(uniq_id=uniq_id, ques_id__ques_id=q['id']).exclude(status='DELETE').values('marks').distinct().order_by('marks'))
			  if len(qry1) > 0:
				  if qry1[0]['marks']!=None and qry1[0]['marks']!='':
					  if float(qry1[0]['marks'])>float(marks):
						  sec_query = q
						  marks = float(qry1[0]['marks'])
			if marks == -1:
			  section['question'].append({"question": sec_query, "marks": {'marks':None}})
			else:
			  section['question'].append({"question": sec_query, "marks": {'marks':marks}})
					# qry2=list(StudentMarks.objects.filter(marks_id=qry1[0]['marks_id']).values('marks').distinct())
					# if len(qry) > 1:
					#     if qry1[0]['marks'] != None and qry1[0]['marks'] != '':
					#         section['question'].append({"question": q, "marks": qry1[0]})
					#         break
					#     else:
					#         section['question'].append({"question": q, "marks": qry1[0]})
					#       break
					# else:
					#     section['question'].append({"question": q, "marks": qry1[0]})
			# qry1=list(StudentMarks.objects.filter(uniq_id=uniq_id,ques_id__ques_id__id=qry[0]['id']).exclude(status='DELETE').values('marks').distinct())
			# # print(qry1)
			# # qry2=list(StudentMarks.objects.filter(marks_id=qry1[0]['marks_id']).values('marks').distinct())

			# section['question'].append({"question":qry,"marks":qry1[0]})
			#####................................................................


			# data[0]['question'].append({"question":qry,"marks":qry1[0]})
			# section['marks'].append(qry1)
			for q in qry:
				qj=list(SubjectAddQuestions.objects.filter(id=q['id']).values('co_id__description','co_id__co_num'))
				q['co_id__description']=qj[0]['co_id__description']
				q['co_id__co_num']=qj[0]['co_id__co_num']
				if q['type']=='O':
					q['option']=list(SubjectQuesOptions.objects.filter(ques_id=q['id']).values('option_description','option_img','is_answer'))
	
	return data

def ct_marks_report(request):
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:

		session_name=request.session['Session_name']
		emp_id=request.session['hash1']
		session=request.session['Session_id']

		StudentMarks = generate_session_table_name("StudentMarks_",session_name)
		SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)
		FacultyTime=generate_session_table_name("FacultyTime_",session_name)
		QuesPaperSectionDetails=generate_session_table_name("QuesPaperSectionDetails_",session_name)
		QuesPaperApplicableOn=generate_session_table_name("QuesPaperApplicableOn_",session_name)
		data=[]


		if requestMethod.GET_REQUEST(request):
			if (requestType.custom_request_type(request.GET,'subjects')):
				dept=request.GET['dept']
				sem=request.GET['sem']
				section=request.GET['section'].split(',')
				section_id=Sections.objects.filter(section__in=section,dept=dept,sem_id__sem=sem).values_list('section_id',flat=True)
				sem_id=list(Sections.objects.filter(section_id__in=section_id).values_list('sem_id',flat=True).distinct())
				data=get_subjects_hod_dean(sem_id,session_name,['LAB','VALUE ADDED COURSE'])
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif (requestType.custom_request_type(request.GET,'faculty_subjects')):
				sem=request.GET['sem']
				dept=request.GET['dept']
				section=request.GET['section'].split(',')
				section_id=list(Sections.objects.filter(section__in=section,dept=dept,sem_id__sem=sem).values_list('section_id',flat=True))
				data=get_subjects_faculty(emp_id,section_id,session_name,['LAB','VALUE ADDED COURSE'])
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif (requestType.custom_request_type(request.GET,'exam_id')):
				
				data=get_exam_name(session)
				return functions.RESPONSE(get_exam_name(session),statusCodes.STATUS_SUCCESS)


			elif(requestType.custom_request_type(request.GET,'on_submit')):
				# print(1)

				dept=request.GET['dept']
				sem=request.GET['sem']

				exam_id=request.GET['exam_id'].split(",")
				subject=request.GET['subject_id'].split(',')
				group_id=""
				
				if 'group_id' in request.GET:
					group_id=request.GET['group_id']

				students=[]
				section_ids=[]
				if group_id is not None and group_id != "" and 'section' in request.GET:
					section_ids=request.GET['section'].split(",")
					for section_id in section_ids:
						students.extend(get_att_group_section_students(group_id,section_id,session_name))
				elif  group_id is not None and group_id != "":
					section_ids=get_group_sections(group_id,session_name)
					for section_id in section_ids:
						students.extend(get_att_group_section_students(group_id,str(section_id),session_name))
				elif 'section' in request.GET:
					section_ids=request.GET['section'].split(',')
					student=get_section_students(section_ids,{},session_name)
					for x in student:
						students.extend(x)
				
				ct_group=int(list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP',session=session).values('value','sno'))[0]['value'])
				if students:
					# print(1)
					data=[]
					data.append({})
					data[-1]['student_list']=[]
					data[-1]['overall_students'] = []
					sem_id=Sections.objects.filter(section_id__in=section_ids).values_list('sem_id',flat=True)
					temp_len=len(students)
					# data[-1]['overall_students'].append({'total_students':temp_len})
					for k in range(0,temp_len):
						data[-1]['student_list'].append(students[k])
					subject_id = FacultyTime.objects.exclude(subject_id__subject_type__value='LAB').exclude(subject_id__subject_type__value='VALUE ADDED COURSE').exclude(status='DELETE').filter(subject_id__in=subject).values('section__sem_id__sem','section__sem_id__dept__dept__value','subject_id__max_ct_marks','section__sem_id').distinct().annotate(sub_name=F('subject_id__sub_name'),sub_alpha_code=F('subject_id__sub_alpha_code'),sub_num_code=F('subject_id__sub_num_code'),id=F('subject_id'))
							
					data[-1]['subjects']=[]
					
					i=0

					for s in subject_id:
						data[-1]['subjects'].append({})
						subject_name=s['sub_name']+'('+s['sub_alpha_code']+'-'+s['sub_num_code']+')'
						data[-1]['subjects'][i]['subject_details']=[]
						data[-1]['subjects'][i]['subject_details'].append({'Subject_name':subject_name,'subject_id':s['id']})
						data[-1]['subjects'][i]['CT']=[]
						k=0
						# data[-1]['subjects'][i]['CT'].append({})
						for exam in exam_id:
							data[-1]['subjects'][i]['CT'].append({})
							data[-1]['subjects'][i]['CT'][k]['exam_id']=exam
							data[-1]['subjects'][i]['CT'][k]['exam_name']=list(StudentAcademicsDropdown.objects.filter(sno=exam,session=session).values('value'))[0]['value']
							format_id=list(QuesPaperApplicableOn.objects.filter(ques_paper_id__exam_id=exam,sem=sem_id[0]).values('ques_paper_id').order_by('-id'))
							if len(format_id)>0:
								max_marks=QuesPaperSectionDetails.objects.filter(ques_paper_id=format_id[0]['ques_paper_id']).aggregate(total_marks=Sum('max_marks'))
								data[-1]['subjects'][i]['CT'][k]['max_marks']=max_marks.get('total_marks',0)
							studenting=[]

							for stud in students:
								marks_obtained =  get_student_marks(stud['uniq_id'],session_name,s['id'],exam,s['subject_id__max_ct_marks'],ct_group,s['section__sem_id'])['marks_obtained']

								paper=[]

								marks = StudentMarks.objects.filter(uniq_id=stud['uniq_id'],marks_id__exam_id=exam,marks_id__subject_id=s['id']).exclude(status="DELETE").values('ques_id__ques_paper_id','ques_id__ques_id','ques_id__section_id__id').distinct()
								if marks:
									paper = paper_data(marks[0]['ques_id__ques_paper_id'],session_name,session,stud['uniq_id'])
								
								question = []
								ques_no=0
								marks=[]
								if len(paper)>0:
									for section in paper[0]['section']:
										if section['attempt_type'] == "M":
											ques_no+=1
											question.append({"ques":ques_no,"parts":len(section['question'])})
											for no,part in enumerate(section['question']):
												marks.append({'name':chr(no+65)})
												for detail in part:
													marks[-1][detail]=part[detail]
										else:
											for no,part in enumerate(section['question']):
												ques_no+=1
												question.append({"ques":ques_no,"parts":1})
												marks.append({'name':" "})
												for detail in part:
													marks[-1][detail]=part[detail]
								studenting.append({'uniq_id':stud['uniq_id'],'uniq_id__name':stud['uniq_id__name'],'section':stud['section__section'],'marks_obtained':marks_obtained,'class_roll_no':stud['class_roll_no'],'university_roll_no':stud['uniq_id__uni_roll_no'],'father_name':stud['fname'],'paper':paper,'marks_details':marks,'question':question})
								absent=0
								detained=0
								total_marks_obtained=0
								students_sections=[]
								custom_data = {}
								for stu_present in studenting:
									print(stu_present['section'])
									students_sections.append(stu_present['section'])
									if stu_present['marks_obtained']=='A':
										absent+=1
									elif stu_present['marks_obtained']=='D':
										detained=detained+1
									else:
										if(stu_present['marks_obtained'] != 'NA'):
											total_marks_obtained = total_marks_obtained+stu_present['marks_obtained']

							data[-1]['subjects'][i]['CT'][k]['students']=studenting
							present_students = temp_len-absent-detained
							average_marks = total_marks_obtained/present_students
							print(Counter(students_sections).keys())
							print(Counter(students_sections).values())
							section = list(Counter(students_sections).keys())
							print(section)
							section_student=list(Counter(students_sections).values())
							data[-1]['overall_students'].append({'absent_students':absent,'detained_students':detained,'total_students':temp_len,'average_marks':average_marks,'present_students':present_students,'section':section,'section_students':section_student})

							k+=1
						i+=1
		else:
			data=statusMessages.MESSAGE_BAD_REQUEST

		return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,status)

# def ct_marks_report(request):
#   if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:

#       session_name=request.session['Session_name']
#       emp_id=request.session['hash1']
#       session=request.session['Session_id']
#       # data_values=[]
#       # session_name="1819o"
#       # session=1
#       StudentMarks = generate_session_table_name("StudentMarks_",session_name)
#       SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)
#       FacultyTime=generate_session_table_name("FacultyTime_",session_name)
#       QuesPaperSectionDetails=generate_session_table_name("QuesPaperSectionDetails_",session_name)
#       QuesPaperApplicableOn=generate_session_table_name("QuesPaperApplicableOn_",session_name)
#       data=[]


#       if requestMethod.GET_REQUEST(request):
#           if (requestType.custom_request_type(request.GET,'subjects')):
#               dept=request.GET['dept']
#               sem=request.GET['sem']
#               section=request.GET['section'].split(',')
#               section_id=Sections.objects.filter(section__in=section,dept=dept,sem_id__sem=sem).values_list('section_id',flat=True)
#               sem_id=list(Sections.objects.filter(section_id__in=section_id).values_list('sem_id',flat=True).distinct())
#               data=get_subjects_hod_dean(sem_id,session_name,['LAB','VALUE ADDED COURSE'])
#               return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

#           elif (requestType.custom_request_type(request.GET,'faculty_subjects')):
#               sem=request.GET['sem']
#               dept=request.GET['dept']
#               section=request.GET['section'].split(',')
#               section_id=list(Sections.objects.filter(section__in=section,dept=dept,sem_id__sem=sem).values_list('section_id',flat=True))
#               data=get_subjects_faculty(emp_id,section_id,session_name,['LAB','VALUE ADDED COURSE'])
#               return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

#           elif (requestType.custom_request_type(request.GET,'exam_id')):
				
#               data=get_exam_name(session)
#               return functions.RESPONSE(get_exam_name(session),statusCodes.STATUS_SUCCESS)


#           elif(requestType.custom_request_type(request.GET,'on_submit')):

#               dept=request.GET['dept']
#               sem=request.GET['sem']

#               exam_id=request.GET['exam_id'].split(",")
#               subject=request.GET['subject_id'].split(',')
#               group_id=""
				
#               if 'group_id' in request.GET:
#                   group_id=request.GET['group_id']

#               students=[]
#               section_ids=[]
#               if group_id is not None and group_id != "" and 'section' in request.GET:
#                   section_ids=request.GET['section'].split(",")
#                   for section_id in section_ids:
#                       students.extend(get_att_group_section_students(group_id,section_id,session_name))
#               elif  group_id is not None and group_id != "":
#                   section_ids=get_group_sections(group_id,session_name)
#                   for section_id in section_ids:
#                       students.extend(get_att_group_section_students(group_id,str(section_id),session_name))
#               elif 'section' in request.GET:
#                   section_ids=request.GET['section'].split(',')
#                   student=get_section_students(section_ids,{},session_name)
#                   for x in student:
#                       students.extend(x)
#               ct_group=int(list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP',session=session).values('value','sno'))[0]['value'])
#               if students:
#                   data=[]
#                   data.append({})
#                   data[-1]['student_list']=[]
#                   sem_id=Sections.objects.filter(section_id__in=section_ids).values_list('sem_id',flat=True)
#                   temp_len=len(students)
#                   for k in range(0,temp_len):
#                       data[-1]['student_list'].append(students[k])
#                   subject_id = FacultyTime.objects.exclude(subject_id__subject_type__value='LAB').exclude(subject_id__subject_type__value='VALUE ADDED COURSE').exclude(status='DELETE').filter(subject_id__in=subject).values('section__sem_id__sem','section__sem_id__dept__dept__value','subject_id__max_ct_marks','section__sem_id').distinct().annotate(sub_name=F('subject_id__sub_name'),sub_alpha_code=F('subject_id__sub_alpha_code'),sub_num_code=F('subject_id__sub_num_code'),id=F('subject_id'))
#                   data[-1]['students']=[]
#                   for stud in students:
#                       student=[]
#                       Subject=[]
#                       for s in subject_id:
#                           subject_name=s['sub_name']+'('+s['sub_alpha_code']+'-'+s['sub_num_code']+')'
#                           Exam=[]
#                           for exam in exam_id:
#                               format_id=list(QuesPaperApplicableOn.objects.filter(ques_paper_id__exam_id=exam,sem=sem_id[0]).values('ques_paper_id').order_by('-id'))
#                               row=[]
#                               if len(format_id)>0:
#                                   max_marks=QuesPaperSectionDetails.objects.filter(ques_paper_id=format_id[0]['ques_paper_id']).aggregate(total_marks=Sum('max_marks'))
#                                   row.append(max_marks.get('total_marks',0))
#                               studenting=[]
#                               marks_obtained =  get_student_marks(stud['uniq_id'],session_name,s['id'],exam,s['subject_id__max_ct_marks'],ct_group,s['section__sem_id'])['marks_obtained']
#                           Exam=[]
#                           for exam in exam_id:
						
#                               paper=[]
#                               marks = StudentMarks.objects.filter(uniq_id=stud['uniq_id'],marks_id__exam_id=exam,marks_id__subject_id=s['id']).exclude(status="DELETE").values('ques_id__ques_paper_id','ques_id__ques_id','ques_id__section_id__id').distinct()
#                               if marks:
#                                   paper = paper_data(marks[0]['ques_id__ques_paper_id'],session_name,session,stud['uniq_id'])
#                               Exam.append({'exam_id':exam,'exam_name':list(StudentAcademicsDropdown.objects.filter(sno=exam,session=session).values('value'))[0]['value'],'max_marks':row,'paper':paper,'marks_obtained':marks_obtained})
#                           Subject.append({'Subject_name':subject_name,'subject_id':s['id'],'exam':Exam})
#                       data[-1]['students'].append({'uniq_id':stud['uniq_id'],'uniq_id__name':stud['uniq_id__name'],'section':stud['section__section'],'class_roll_no':stud['class_roll_no'],'university_roll_no':stud['uniq_id__uni_roll_no'],'father_name':stud['fname'],'subject':Subject})
#       else:
#           data=statusMessages.MESSAGE_BAD_REQUEST

#       return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

#   else:
#       return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)