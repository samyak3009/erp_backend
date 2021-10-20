from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from itertools import groupby

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from StudentMMS.constants_functions import requestType

from musterroll.models import EmployeePrimdetail
from StudentAcademics.models import *
from Registrar.models import StudentSemester,CourseDetail,StudentDropdown
from login.models import EmployeeDropdown
from StudentMMS.models import *

from login.views import checkpermission,generate_session_table_name
from StudentAcademics.views import *
from StudentMMS.views.mms_function_views import get_sem_mms_subjects,get_max_marks,get_peo,get_peo_list,get_po,get_po_list,get_co,get_co_list,get_mission,get_groups_students,get_groups_section,get_survey_dropdown
from StudentMMS.views.mms_function_views import *
from StudentMMS.views.external_views import get_faculty_feedback_po_wise

def uveCoordinator(request):
	data_values=[]
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC,rolesCheck.ROLE_REGISTRAR,rolesCheck.ROLE_HOD,rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
		emp_id=request.session['hash1']
		session=request.session['Session_id']
		session_name=request.session['Session_name']
		StudentAttStatus=generate_session_table_name("StudentAttStatus_",session_name)
		StudentUniversityMarks=generate_session_table_name("StudentUniversityMarks_",session_name)
		StudentFinalMarksStatus=generate_session_table_name("StudentFinalMarksStatus_",session_name)
		# UniversityMarks=generate_session_table_name("UniversityMarks_",session_name)
		SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)
		studentSession=generate_session_table_name("studentSession_",session_name)
		if (requestMethod.GET_REQUEST(request)):
			if(requestType.custom_request_type(request.GET,'get_student_list')):
				subjects=list(map(int,request.GET['subjects'].split(',')))
				sections=list(map(int,request.GET['sections'].split(',')))
				for sec in sections:
					students=[]
					data=[]
					func_stu = get_section_students([sec],{},session_name)
					students=[]

					for stu in func_stu:
						students.extend(stu)

					stu_data_list=[]
					#students=list(StudentAttStatus.objects.filter(att_id__section=sec).exclude(status__contains='DELETE').exclude(att_id__status__contains='DELETE').values('uniq_id','uniq_id__uniq_id__name','uniq_id__uniq_id__uni_roll_no','uniq_id__section','uniq_id__section__section').order_by('uniq_id__uniq_id__name').distinct().order_by('uniq_id__uniq_id__uni_roll_no'))
					for student in students:
						stu_data={}
						stu_data['uniq_id']=student['uniq_id']
						stu_data['uniq_id__uniq_id__name']=student['uniq_id__name']
						stu_data['uniq_id__uniq_id__uni_roll_no']=student['uniq_id__uni_roll_no']
						stu_data['uniq_id__section']=student['section']
						stu_data['uniq_id__section__section']=student['section__section']
						stu_data['uniq_id__sem__sem']=student['section__sem_id__sem']
						# student['subjects']=list(StudentAttStatus.objects.filter(att_id__subject_id__in=subjects,uniq_id=student['uniq_id']).exclude(status__contains='DELETE').exclude(att_id__status__contains='DELETE').exclude(att_id__subject_id__subject_type__value='VALUE ADDED COURSE').values('att_id__subject_id__sub_name','att_id__subject_id__sub_alpha_code','att_id__subject_id__sub_num_code','att_id__subject_id__subject_type','att_id__subject_id__subject_type__value','att_id__subject_id__max_university_marks','att_id__subject_id__max_ct_marks','att_id__subject_id__max_ta_marks','att_id__subject_id__max_att_marks','att_id__subject_id').distinct())
						stu_data['subjects']=list(SubjectInfo.objects.filter(id__in=subjects).exclude(status="DELETE").exclude(subject_type__value='VALUE ADDED COURSE').values('sub_num_code','sub_alpha_code','sub_name','subject_type','subject_type__value','subject_unit','subject_unit__value','max_ct_marks','max_ta_marks','max_att_marks','max_university_marks','added_by','time_stamp','status','session','sem','id').distinct())
						for sub in stu_data['subjects']:
							sub['max_internal_marks']=sub['max_ct_marks']+sub['max_ta_marks']+sub['max_att_marks']
							#####add exclude status = delete here################
							query=StudentUniversityMarks.objects.filter(uniq_id=stu_data['uniq_id'],subject_id=sub['id']).values('internal_marks','external_marks','back_marks')
							sub['internal_marks_obt']=None
							sub['external_marks_obt']=None
							sub['back_marks_obt']=None
							if(query):
								if  query[0]['internal_marks'] is not None:
									sub['internal_marks_obt']=query[0]['internal_marks']
								if query[0]['external_marks'] is not None:
									sub['external_marks_obt']=query[0]['external_marks']
								if 	query[0]['back_marks'] is not None:
									sub['back_marks_obt']=query[0]['back_marks']
						stu_data_list.append(stu_data)
					if len(students)>0:
						data.append({'section':students[0]['section__section'],'section_id':students[0]['section']})

					data_values.append({'section':data,'students':stu_data_list})
				return functions.RESPONSE(data_values,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'university_marks_report')):
				if request.GET['requested_by'] == 'FACULTY':
					subject =list(get_fac_time_subject(request.session['hash1'],request.GET['sections'].split(','),session_name))
					subjects = [d['subject_id'] for d in subject if 'subject_id' in d]
				elif request.GET['requested_by'] == 'COORDINATOR':
					subject= get_sem_filter_subjects(request.GET['sem'],session_name)
					subjects = [d['id'] for d in subject if 'id' in d]
				else:
					subject=get_sem_filter_subjects(request.GET['sem'],session_name)
					subjects = [d['id'] for d in subject if 'id' in d]

				sections=list(map(int,request.GET['sections'].split(',')))
				data=[]
				func_stu = get_section_students(sections,{},session_name)
				students=[]

				for stu in func_stu:
					students.extend(stu)

				#students=list(StudentAttStatus.objects.filter(att_id__section__in=sections).exclude(status__contains='DELETE').exclude(att_id__status__contains='DELETE').values('uniq_id','uniq_id__uniq_id__name','uniq_id__uniq_id__uni_roll_no','uniq_id__section','uniq_id__section__section','uniq_id__sem__sem').order_by('uniq_id__uniq_id__name').distinct().order_by('uniq_id__uniq_id__uni_roll_no'))
				for student in students:
					stu_data={}
					stu_data['uniq_id']=student['uniq_id']
					stu_data['uniq_id__uniq_id__name']=student['uniq_id__name']
					stu_data['uniq_id__uniq_id__uni_roll_no']=student['uniq_id__uni_roll_no']
					stu_data['uniq_id__section']=student['section']
					stu_data['uniq_id__section__section']=student['section__section']
					stu_data['uniq_id__sem__sem']=student['section__sem_id__sem']
					# student['subjects']=list(StudentAttStatus.objects.filter(att_id__subject_id__in=subjects,uniq_id=student['uniq_id']).exclude(status__contains='DELETE').exclude(att_id__status__contains='DELETE').exclude(att_id__subject_id__subject_type__value='VALUE ADDED COURSE').values('att_id__subject_id__sub_name','att_id__subject_id__sub_alpha_code','att_id__subject_id__sub_num_code','att_id__subject_id__subject_type','att_id__subject_id__subject_type__value','att_id__subject_id__max_university_marks','att_id__subject_id__max_ct_marks','att_id__subject_id__max_ta_marks','att_id__subject_id__max_att_marks','att_id__subject_id').distinct())
					stu_data['subjects']=list(SubjectInfo.objects.filter(id__in=subjects).exclude(status="DELETE").exclude(subject_type__value='VALUE ADDED COURSE').values('sub_num_code','sub_alpha_code','sub_name','subject_type','subject_type__value','subject_unit','subject_unit__value','max_ct_marks','max_ta_marks','max_att_marks','max_university_marks','added_by','time_stamp','status','session','sem','id').distinct())
					for sub in stu_data['subjects']:
						sub['max_internal_marks']=sub['max_ct_marks']+sub['max_ta_marks']+sub['max_att_marks']
						query=StudentUniversityMarks.objects.filter(uniq_id=stu_data['uniq_id'],subject_id=sub['id']).values('internal_marks','external_marks','back_marks')
						sub['internal_marks_obt']=None
						sub['external_marks_obt']=None
						sub['back_marks_obt']=None
						if(query):
							if  query[0]['internal_marks'] is not None:
								sub['internal_marks_obt']=query[0]['internal_marks']
							if query[0]['external_marks'] is not None:
								sub['external_marks_obt']=query[0]['external_marks']
							if 	query[0]['back_marks'] is not None:
									sub['back_marks_obt']=query[0]['back_marks']
					qry11=list(StudentFinalMarksStatus.objects.filter(uniq_id=stu_data['uniq_id']).values('Total_marks_obtained','Total_max_marks','Division_awarded','Result_status','Year_obtained','Year_total'))
					if len(qry11)>0:
						stu_data['Total_marks_obtained']=qry11[0]['Total_marks_obtained']
						stu_data['Total_max_marks']=qry11[0]['Total_max_marks']
						stu_data['Division_awarded']=qry11[0]['Division_awarded']
						stu_data['Result_status']=qry11[0]['Result_status']
						stu_data['Year_obtained']=qry11[0]['Year_obtained']
						stu_data['Year_total']=qry11[0]['Year_total']
					else:
						stu_data['Total_marks_obtained']="---"
						stu_data['Total_max_marks']="---"
						stu_data['Division_awarded']="---"
						stu_data['Result_status']="---"
						stu_data['Year_obtained']="---"
						stu_data['Year_total']="---"
					data.append(stu_data)

				data_values.append({'students':data})
				# print(data_values)
				return functions.RESPONSE(data_values,statusCodes.STATUS_SUCCESS)

		elif (requestMethod.POST_REQUEST(request)):
			data = json.loads(request.body)
			data=data['data']
			da=[]
			for stu in data:
				#######################LOCKING STARTS######################
				da=[]
				section1=stu['section'][0]['section_id']
				da.append(section1)
				print(da)
				if check_islocked("UNM",da,session_name):
					return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
				####################LOCKING ENDS##############################
				section=stu['section'][0]['section_id']
				for s in stu['students']:
					for x in s['subjects']:
						obj=StudentUniversityMarks.objects.filter(uniq_id=s['uniq_id'],subject_id=x['id']).update(added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),external_marks=x['external_marks_obt'],internal_marks=x['internal_marks_obt'],back_marks=x['back_marks_obt'])
						if(obj):
							pass
						else:
							objs=StudentUniversityMarks.objects.create(subject_id=SubjectInfo.objects.get(id=x['id']),uniq_id=studentSession.objects.get(uniq_id=s['uniq_id']),added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),external_marks=x['external_marks_obt'],internal_marks=x['internal_marks_obt'],back_marks=x['back_marks_obt'])

			return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def po_peo_mapping(request):

	if academicCoordCheck.isNBACoordinator(request):
		emp_id=request.session['hash1']
		session=request.session['Session_id']
		session_name=request.session['Session_name']
		SubjectPOPEOMapping=generate_session_table_name("SubjectPOPEOMapping_",session_name)
		Dept_VisMis=generate_session_table_name("Dept_VisMis_",session_name)

		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'get_data')):
				dept=request.GET['dept']
				po=get_po(dept,session_name)
				po_list=get_po_list(dept,session_name)
				peo_list=get_peo(dept,session_name)
				marks=get_max_marks(session)
				data1=[]
				qry=list(SubjectPOPEOMapping.objects.filter(po_id__in=po_list).exclude(status='DELETE').exclude(po_id__status='DELETE').exclude(peo_id__status='DELETE').values('po_id','po_id__description','marks','peo_id','peo_id__description'))
				for q in qry:
					data1.append({'peo_id':q['peo_id'],'peo':q['peo_id__description'],'po_id':q['po_id'],'po':q['po_id__description'],'marks':q['marks']})

				data={'data':data1,'peo_list':peo_list,'po_list':po,'marks':marks}

				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		elif requestMethod.POST_REQUEST(request):
			data=json.loads(request.body)
			k=False
			for q in data:
				peo_id=q['peo_id']
				po_id=q['po_id']
				marks=q['marks']
				qry=SubjectPOPEOMapping.objects.filter(peo_id=peo_id,po_id=po_id).update(status='DELETE')
				if marks is None:
					data=statusMessages.MESSAGE_INSERT
				else:
					qry1=SubjectPOPEOMapping.objects.create(peo_id=Dept_VisMis.objects.get(id=peo_id),po_id=Dept_VisMis.objects.get(id=po_id),marks=marks,added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
					if qry1 :
						data=statusMessages.MESSAGE_INSERT

			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def peo_mi_mapping(request):

	if academicCoordCheck.isNBACoordinator(request):
		emp_id=request.session['hash1']
		session=request.session['Session_id']
		session_name=request.session['Session_name']
		SubjectPEOMIMapping=generate_session_table_name("SubjectPEOMIMapping_",session_name)
		Dept_VisMis=generate_session_table_name("Dept_VisMis_",session_name)

		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'get_data')):
				dept=request.GET['dept']
				peo=get_peo(dept,session_name)
				peo_list=get_peo_list(dept,session_name)
				mission_list=get_mission(dept,session_name)
				marks=get_max_marks(session)
				data1=[]
				qry=list(SubjectPEOMIMapping.objects.filter(peo_id__in=peo_list).exclude(status='DELETE').values('m_id','m_id__description','marks','peo_id','peo_id__description'))
				for q in qry:
					data1.append({'peo_id':q['peo_id'],'peo':q['peo_id__description'],'m_id':q['m_id'],'m':q['m_id__description'],'marks':q['marks']})

				data={'data':data1,'peo_list':peo,'mission_list':mission_list,'marks':marks}

				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		elif requestMethod.POST_REQUEST(request):
			data=json.loads(request.body)
			for q in data:
				peo_id=q['peo_id']
				m_id=q['m_id']
				marks=q['marks']
				qry=SubjectPEOMIMapping.objects.filter(peo_id=peo_id,m_id=m_id).update(status='DELETE')
				if marks is None:
					data=statusMessages.MESSAGE_INSERT
				else:
					qry1=SubjectPEOMIMapping.objects.create(peo_id=Dept_VisMis.objects.get(id=peo_id),m_id=Dept_VisMis.objects.get(id=m_id),marks=marks,added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
					if qry1:
						data=statusMessages.MESSAGE_INSERT

			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)


def mms_student_internal_co_report(request):
	if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		emp_id=request.session['hash1']
		session=request.session['Session_id']
		session_name=request.session['Session_name']
		data=[]
		AssignmentStudentMarks= generate_session_table_name("AssignmentStudentMarks_",session_name)
		AssignmentQuizMarks= generate_session_table_name("AssignmentQuizMarks_",session_name)
		SubjectCODetails = generate_session_table_name("SubjectCODetails_",session_name)
		SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_",session_name)
		QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_",session_name)
		SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_",session_name)
		SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
		COAttainment = generate_session_table_name("COAttainment_",session_name)
		SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_",session_name)
		MarksAttainmentSettings = generate_session_table_name("MarksAttainmentSettings_",session_name)

		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'subjects')):
				sem_id=request.GET['sem'].split(",")
				data=get_subjects_hod_dean(sem_id,session_name,[])
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'fac_subjects')):
				section_id=request.GET['section'].split(",")
				data=get_subjects_faculty(emp_id,section_id,session_name,[])
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'get_report_data')):
				subject_id=request.GET['subject_id']
				sem_id=request.GET['sem']
				isgroup=request.GET['isgroup']
				exam_data=[]
				exam_list=internal_exam_dropdown(session)
				i=0
				yes=[]
				no=[]
				na_array=[]
				students=[]
				co_wise=[]
				flag=0
				k=0
				get=0
				y=0
				no1=0
				na=0
				if isgroup=='N':
					student_list=get_section_students(request.GET['section'].split(","),{},session_name)
					section=request.GET['section'].split(",")
				else:
					################get sections corresponding to group ids###########
					section=get_groups_section(request.GET['section'],{},session_name)
					################get students corresponding to group ids###########
					student_list=get_groups_students(request.GET['section'],session_name)
				for stud in student_list:
						students.extend(stud)
				################get subject type of given subject###########
				sub_type=list(SubjectInfo.objects.filter(id=subject_id).values('subject_type'))
				attainment_level=list(MarksAttainmentSettings.objects.exclude(status='DELETE').filter(sem=sem_id,attainment_type='D',subject_type=sub_type[0]['subject_type']).values('from_direct_per','to_indirect_per','attainment_level'))

				for key,value in exam_list.items():
					for v in value:
						if isgroup=='N':
							######if not groupwise#####
							qry=list(AssignmentQuizMarks.objects.filter(subject_id=subject_id,exam_id=v['sno'],section__in=section).exclude(status='DELETE').values('isco_wise'))
						else:
							######if groupwise#####
							print(section)
							qry=list(AssignmentQuizMarks.objects.filter(subject_id=subject_id,exam_id=v['sno'],section__in=section,isgroup='Y').exclude(status='DELETE').values('isco_wise'))
							print(qry)
						if qry:
							co_wise.append(qry[0]['isco_wise'])
							k=1
				if k==1:
					if 'N' not in co_wise:
						##############if none of the marks are enterred co_wise################
						for key,value in exam_list.items():
							for val in value:
								paper_id=list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id__exam_id=val['sno'],ques_paper_id__subject_id=subject_id,ques_paper_id__approval_status='APPROVED').values('ques_paper_id'))

								if paper_id:#######if paper is created#########
									co_info=list(SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'),co_description=F('description')))
									for c in co_info:
										qry=list(SubjectCODetailsAttainment.objects.filter(co_id=c['id'],attainment_method__value=key).values('id').annotate(co_req_attain=F('attainment_per')))
										if qry:
											c['co_req_attain']=qry[0]['co_req_attain']
										else:
											c['co_req_attain']=None

									co_info_data=[]
									if co_info:
										exam_data.append({'exam_name': val['value'],'exam':key})
										exam_data[i]['co_info']=[]
										for c in co_info:
											get=0
											y=0
											no1=0
											na=0
											flag=1
											if c['co_name']>0:
												qid=[]
												co_section_details=list(QuestionPaperQuestions.objects.exclude(status='DELETE').exclude(status='SAVED').filter(ques_paper_id=paper_id[0]['ques_paper_id'],ques_id__co_id=c['id']).values('section_id','section_id__name','section_id__attempt_type','ques_id','ques_num'))
												if co_section_details:
													co_info_data.append(c)
													get=1
													for k,v in groupby(co_section_details,key=lambda x:x['ques_num']):
														for m,n in groupby(v,key=lambda a:a['section_id']):
															n=list(n)
															qid.append(n[0]['ques_id'])
													co_max_marks=SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
													c['co_max_marks']=co_max_marks.get('co_max_marks',0)

													for stu in students:
														present_status=list(AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=val['sno'],marks_id__subject_id=subject_id,uniq_id=stu['uniq_id']).values('present_status','marks_id__exam_id','marks_id__subject_id').distinct())
														# stu['marks']=[]
														if present_status:
															if 'marks' not in stu:
																stu['marks']=[]
															if present_status[0]['present_status']=='P':
																obtained_co=AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(marks_id__exam_id=val['sno'],marks_id__subject_id=subject_id,ques_id__ques_id__co_id=c['id'],uniq_id=stu['uniq_id']).aggregate(co_obtained=Sum('marks'))
																obtained_co_marks=obtained_co.get('co_obtained',0)
																co_att_na=0
																if obtained_co_marks==None:
																	obtained_co_marks=0
																	co_att_na=1
																stu['marks'].append(obtained_co_marks)
																attainment_per_obtained = (obtained_co_marks/c['co_max_marks'])*100.0
																if c['co_req_attain'] != None:
																	if attainment_per_obtained >= c['co_req_attain']:
																		stu['marks'].append('Y')
																		y+=1
																	elif co_att_na==1:
																		stu['marks'].append('NA')
																		na+=1
																	else:
																		stu['marks'].append('N')
																		no1+=1
																else:
																	stu['marks'].append('NA')
																	na+=1

															else:     	  #if absent or detained
																stu['marks'].append('A')
																stu['marks'].append('NA')
																na+=1
														else:
															stu['marks'].append('NA')
															stu['marks'].append('NA')
															na+=1

											if get==1:
												yes.append(y)
												no.append(no1)
												na_array.append(na)
										exam_data[i]['co_info'].append(co_info_data)
										i+=1
									else:
										data={'msg': 'CO details have not been filled for this subject'}
										return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)


					else:
						for key,value in exam_list.items():

							for val in value:
								get=0
								na=0
								y=0
								no1=0
								flag=0
								for sec in section:
									if isgroup=='N':
										qry=list(AssignmentQuizMarks.objects.filter(subject_id=subject_id,exam_id=val['sno'],section=sec).exclude(status='DELETE').values('isco_wise'))
									else:
										qry=list(AssignmentQuizMarks.objects.filter(subject_id=subject_id,exam_id=val['sno'],section=sec,isgroup='Y').exclude(status='DELETE').values('isco_wise'))
									if qry:
										if qry[0]['isco_wise'] == 'Y':
											paper_id=list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id__exam_id=val['sno'],ques_paper_id__subject_id=subject_id,ques_paper_id__approval_status='APPROVED').values('ques_paper_id'))
											if paper_id:
												co_info=list(SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'),co_description=F('description')))
												# print(co_info)
												qry=list(SubjectCODetailsAttainment.objects.filter(co_id=co_info[0]['id'],attainment_method__value=key).values('id').annotate(co_req_attain=F('attainment_per')))
												if qry:
													co_info[0]['co_req_attain']=qry[0]['co_req_attain']
												else:
													co_info[0]['co_req_attain']=None
												flag=1
												co_info_data=[]
												if co_info:
													exam_data.append({'exam_name': val['value'],'exam':key})
													exam_data[i]['co_info']=[]
													qid=[]
													cid=[]
													max_m=0
													for c in co_info:
														get=0
														y=0
														no1=0
														na=0
														if c['co_name']>0:
															co_section_details=list(QuestionPaperQuestions.objects.exclude(status='DELETE').exclude(status='SAVED').filter(ques_paper_id=paper_id[0]['ques_paper_id'],ques_id__co_id=c['id']).values('section_id','section_id__name','section_id__attempt_type','ques_id','ques_num'))

															if co_section_details:
																cid.append(c['id'])
																get=1
																for k,v in groupby(co_section_details,key=lambda x:x['ques_num']):
																	for m,n in groupby(v,key=lambda a:a['section_id']):
																		n=list(n)
																		qid.append(n[0]['ques_id'])
													for z in co_info:
														one=z
														break
													print(one)
													co_info_data.append(one)
													print(co_info_data)
													co_max_marks=SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
													co_info[0]['co_max_marks']=co_max_marks.get('co_max_marks',0)
													for stu in students:
														present_status=list(AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=val['sno'],marks_id__subject_id=subject_id,uniq_id=stu['uniq_id']).values('present_status','marks_id__exam_id','marks_id__subject_id').distinct())
														if present_status:
															if 'marks' not in stu:
																stu['marks']=[]
															if present_status[0]['present_status']=='P':
																obtained_co=AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(marks_id__exam_id=val['sno'],marks_id__subject_id=subject_id,ques_id__ques_id__co_id__in=cid,uniq_id=stu['uniq_id']).aggregate(co_obtained=Sum('marks'))
																obtained_co_marks=obtained_co.get('co_obtained',0)
																co_att_na=0
																if obtained_co_marks==None:
																	obtained_co_marks=0
																	co_att_na=1
																stu['marks'].append(obtained_co_marks)
																attainment_per_obtained = (obtained_co_marks/co_info[0]['co_max_marks'])*100.0
																if co_info[0]['co_req_attain'] != None:
																	if attainment_per_obtained >= co_info[0]['co_req_attain']:
																		stu['marks'].append('Y')
																		y+=1
																	elif co_att_na==1:
																		stu['marks'].append('NA')
																		na+=1
																	else:
																		stu['marks'].append('N')
																		no1+=1
																else:
																	stu['marks'].append('NA')
																	na+=1

															else:       #if absent or detained
																stu['marks'].append('A')
																stu['marks'].append('NA')
																na+=1
														else:
															stu['marks'].append('NA')
															stu['marks'].append('NA')
															na+=1

													if get==1:
														yes.append(y)
														no.append(no1)
														na_array.append(na)

												else:
													data={'msg': 'CO details have not been filled for this subject'}
													return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

										else:

												co_info_data=[]
												co_info=list(SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'),co_description=F('description')))

												if co_info:

													qry=list(SubjectCODetailsAttainment.objects.filter(co_id=co_info[0]['id'],attainment_method__value=key).values('id').annotate(co_req_attain=F('attainment_per')))
													if qry:
														co_info[0]['co_req_attain']=qry[0]['co_req_attain']
													else:
														co_info[0]['co_req_attain']=None
													exam_data.append({'exam_name': val['value'],'exam':key})
													exam_data[i]['co_info']=[]
													print(exam_data)
													max_m=AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(marks_id__exam_id=val['sno'],marks_id__subject_id=subject_id,).values('marks_id__max_marks').distinct()
													co_info[0]['co_max_marks']=max_m[0]['marks_id__max_marks']

													co_info_data.append(co_info[0])
													# print(co_info_data)
													flag=1
													for stu in students:
														present_status=list(AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=val['sno'],marks_id__subject_id=subject_id,uniq_id=stu['uniq_id']).values('present_status','marks_id__exam_id','marks_id__subject_id').distinct())
														if 'marks' not in stu:
																stu['marks']=[]
														if present_status:

															if present_status[0]['present_status']=='P':
																obtained_co=AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(marks_id__exam_id=val['sno'],marks_id__subject_id=subject_id,uniq_id=stu['uniq_id']).values('marks')
																if obtained_co:
																	obtained_co_marks=obtained_co[0]['marks']
																else:
																	obtained_co_marks=None
																co_att_na=0
																if obtained_co_marks==None:
																	obtained_co_marks=0
																	co_att_na=1
																stu['marks'].append(obtained_co_marks)
																if co_info[0]['co_req_attain'] != None:
																	attainment_per_obtained = int(obtained_co_marks)/int(co_info[0]['co_max_marks'])*100.0

																	get=1

																	if attainment_per_obtained >= co_info[0]['co_req_attain']:
																		stu['marks'].append('Y')
																		y+=1
																	elif co_att_na==1:
																		stu['marks'].append('NA')
																		na+=1
																	else:
																		stu['marks'].append('N')
																		no1+=1
																else:
																	stu['marks'].append('NA')
																	na+=1

															else:       #if absent or detained
																stu['marks'].append('A')
																stu['marks'].append('NA')
																na+=1
														else:
															stu['marks'].append('NA')
															stu['marks'].append('NA')
															na+=1

													if get==1:
														yes.append(y)
														no.append(no1)
														na_array.append(na)
												else:
													data={'msg': 'CO details have not been filled for this subject'}
													return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
								if flag==1:
									exam_data[i]['co_info'].append(list(co_info_data))
									i+=1
					data={'data':exam_data,'data2':students,'yes_count':yes,'no_count':no,'na_count':na_array,'attainment_level':attainment_level}
				else:
					data={'msg':'No Data'}
					return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
		else:
			data=statusMessages.MESSAGE_BAD_REQUEST
		return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def survey_add_Question(request):

	if academicCoordCheck.isNBACoordinator(request):
		emp_id=request.session['hash1']
		session=request.session['Session_id']
		session_name=request.session['Session_name']
		Dept_VisMis=generate_session_table_name("Dept_VisMis_",session_name)
		data_values=[]
		data=[]
		SurveyAddQuestions=generate_session_table_name("SurveyAddQuestions_",session_name)
		SurveyFillFeedback=generate_session_table_name("SurveyFillFeedback_",session_name)

		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'get_data')):
				dept=request.GET['dept']
				po_list=get_po(dept,session_name)
				survey_list=get_survey_dropdown(session)
				data={'po_list':po_list,'survey_list':survey_list}
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'view_previous')):
				sem_id=request.GET['sem_id']
				survey_id=request.GET['survey_id']
				dept=request.GET['dept']
				po_list=get_po(dept,session_name)
				data1=SurveyAddQuestions.objects.filter(sem_id=sem_id,survey_id=survey_id).exclude(status='DELETE').values('question_img','description','survey_id__value','survey_id').distinct()
				for d in data1:
					data=list(SurveyAddQuestions.objects.filter(sem_id=sem_id,survey_id=survey_id,description=d['description']).exclude(status='DELETE').values('po_id__description','po_id','id'))
					d['po_id__description']=data
					for t in d['po_id__description']:
						d['unique_key']=t['id']
						for po in po_list:
							if po['description'] == t['po_id__description']:
								t['po'] = po['po_level_abbr']
								break
				# for d in data:
				# 	for po in po_list:
				# 		if po['description'] == d['po_id__description']:
				# 			d['po'] = po['po_level_abbr']
				# 			break
				qry=SurveyFillFeedback.objects.filter(ques_id__survey_id=survey_id,ques_id__sem_id=sem_id).values('ques_id')
				if qry:
					data_values.append({'data':list(data1),'editable':False, 'session':session_name})
				else:
					data_values.append({'data':list(data1),'editable':True, 'session':session_name})

				if data1:
					return functions.RESPONSE(data_values,statusCodes.STATUS_SUCCESS)
				else:
					data=statusMessages.CUSTOM_MESSAGE("Survey Not Added")
					data_values.append({'data':data,'editable':None})
					return functions.RESPONSE(data_values,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)


		elif requestMethod.POST_REQUEST(request):
			data=json.loads(request.body)
			sem_id=data['sem_id']
			survey_id=data['survey_id']
			qry=SurveyAddQuestions.objects.filter(survey_id=survey_id,sem_id=sem_id).exclude(status='DELETE').values('sem_id')
			if qry and 'check' in data:
				data=statusMessages.CUSTOM_MESSAGE("Survey Already Added")
				return functions.RESPONSE(data,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

			else:
				objs=(SurveyAddQuestions(added_by=EmployeePrimdetail.objects.get(emp_id=emp_id),sem_id=StudentSemester.objects.get(sem_id=sem_id),description=x['description'],question_img=x['question_img'],po_id=Dept_VisMis.objects.get(id=x['po_id']),survey_id=StudentAcademicsDropdown.objects.get(sno=x['survey_id'])) for x in data['data'])
				q_ins=SurveyAddQuestions.objects.bulk_create(objs)
				if q_ins :
					data=statusMessages.MESSAGE_INSERT

				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		elif requestMethod.PUT_REQUEST(request):
			data=json.loads(request.body)
			print(data)
			sem_id=data['sem_id']
			survey_id=data['survey_id']
			emp_id=request.session['hash1']
			for x in data['data']:
				q_id=x['ques_id'].split(",")
				qry1=SurveyAddQuestions.objects.filter(sem_id=sem_id,survey_id=survey_id,id__in=q_id).update(status='DELETE')
				po_id=x['po_id'].split(",")
				for po in po_id:
					qry=SurveyAddQuestions.objects.create(added_by=EmployeePrimdetail.objects.get(emp_id=emp_id),sem_id=StudentSemester.objects.get(sem_id=sem_id),description=x['description'],question_img=x['question_img'],po_id=Dept_VisMis.objects.get(id=po),survey_id=StudentAcademicsDropdown.objects.get(sno=survey_id))
				if qry:
					data=statusMessages.MESSAGE_UPDATE
			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		elif requestMethod.DELETE_REQUEST(request):
			data=json.loads(request.body)
			sem_id=data['sem_id']
			survey_id=data['survey_id']
			ques_id=data['ques_id'].split(",")
			qry=SurveyFillFeedback.objects.filter(ques_id__sem_id=sem_id,ques_id__survey_id=survey_id).values('ques_id')
			if qry:
				data=statusMessages.CUSTOM_MESSAGE("Cannot delete, survey already conducted! ")
			else:
				for ques in ques_id:
					qry=SurveyAddQuestions.objects.filter(sem_id=sem_id,survey_id=survey_id,id__in=ques_id).update(status='DELETE'
					)
					if qry:
						data=statusMessages.MESSAGE_DELETE
			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)


def survey_po_wise_Report(request):

	if checkpermission(request,[rolesCheck.ROLE_HOD,rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
		data=[]
		emp_id=request.session['hash1']
		session=request.session['Session_id']
		session_name=request.session['Session_name']
		SurveyAddQuestions=generate_session_table_name("SurveyAddQuestions_",session_name)
		SurveyFillFeedback=generate_session_table_name("SurveyFillFeedback_",session_name)
		studentSession=generate_session_table_name("studentSession_",session_name)

		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'get_data')):
				survey_id=request.GET['survey_id'].split(',')
				sem_id=request.GET['sem_id']
				sections=request.GET['section'].split(',')
				i=0
				da=get_student_feedback_po_wise(survey_id,sem_id,{'uniq_id__section__in':sections},session_name,session)
				data={'data':da}
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
			elif(requestType.custom_request_type(request.GET,'get_data_faculty')):
				survey_id=request.GET['survey_id'].split(',')
				category=request.GET['category'].split(',')
				dept =request.GET['dept']
				da=get_faculty_feedback_po_wise(survey_id,category,dept,session,session_name)
				data={'data':da}
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'get_survey_dropdown_data')):
				dept=request.GET['dept']
				po_list=get_po(dept,session_name)
				sem=request.GET['sem_id']
				survey_list=get_survey_dropdown_by_sem(sem,session,session_name)
				data={'po_list':po_list,'survey_list':survey_list}
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		elif requestMethod.POST_REQUEST(request):
			data=json.loads(request.body)
			sem_id=data['sem_id']
			objs=(SurveyAddQuestions(added_by=EmployeePrimdetail.objects.get(emp_id=emp_id),sem_id=StudentSemester.objects.get(sem_id=sem_id),description=x['description'],question_img=x['question_img'],po_id=Dept_VisMis.objects.get(id=x['po_id']),survey_id=StudentAcademicsDropdown.objects.get(sno=x['survey_id'])) for x in data['data'])
			q_ins=SurveyAddQuestions.objects.bulk_create(objs)
			if q_ins :
				data=statusMessages.MESSAGE_INSERT

			return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def all_survey_po_wise_Report(request):

	if checkpermission(request,[rolesCheck.ROLE_HOD,rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
		data=[]
		emp_id=request.session['hash1']
		session=request.session['Session_id']
		session_name=request.session['Session_name']
		SurveyAddQuestions=generate_session_table_name("SurveyAddQuestions_",session_name)
		SurveyFillFeedback=generate_session_table_name("SurveyFillFeedback_",session_name)
		studentSession=generate_session_table_name("studentSession_",session_name)
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'get_data')):
				dept=request.GET['dept']
				sess=request.GET['session'].split(',')
				batch=request.GET['batch']
				da=get_student_feedback_avg_po_wise(dept,{},sess,batch)
				data={'data':da}
				# print(data)
				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

			elif(requestType.custom_request_type(request.GET,'get_batch_dropdown')):
					data=get_batch_dropdown(request.GET['dept'],session_name)

			elif(requestType.custom_request_type(request.GET,'get_batch_session_dropdown')):
					data=get_batch_session_dropdown(request.GET['batch'],session_name)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)


# def peo_mi_gap(request):

# 	if checkpermission(request,[rolesCheck.ROLE_HOD,rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
# 		data=[]
# 		emp_id=request.session['hash1']
# 		session=request.session['Session_id']
# 		session_name=request.session['Session_name']
# 		SurveyAddQuestions=generate_session_table_name("SurveyAddQuestions_",session_name)
# 		SurveyFillFeedback=generate_session_table_name("SurveyFillFeedback_",session_name)
# 		studentSession=generate_session_table_name("studentSession_",session_name)
# 		if requestMethod.GET_REQUEST(request):
# 			if(requestType.custom_request_type(request.GET,'get_data')):
# 				mi_peo_avg=get_mission(dept,session_name)
# 				dept=request.GET['dept']
# 				sess=request.GET['session'].split(',')
# 				da=get_student_feedback_avg_po_wise(dept,{},sess)

# 				data={'data':da}
# 				return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

# 		else:
# 			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
# 	else:
# 		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
