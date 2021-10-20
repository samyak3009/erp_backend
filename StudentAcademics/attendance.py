def mark_class_attendance(request):
	print(request)
	data_values={}
	status=403
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[1369])
			if check == 200 and 'A' in request.session['Coordinator_type']:
				query=[]
				session=request.session['Session_id']
				session_name=request.session['Session_name']
				sem_type=request.session['sem_type']
				Attendance = generate_session_table_name("Attendance_",session_name)
				StudentAttStatus = generate_session_table_name("StudentAttStatus_",session_name)
				SubjectInfo = generate_session_table_name("SubjectInfo_",session_name)
				studentSession = generate_session_table_name("studentSession_",session_name)
				SectionGroupDetails = generate_session_table_name("SectionGroupDetails_",session_name)

				if(request.method=='GET'):
					if request.GET['request_type'] == 'form_data':
						attendance_sub_type = get_class_attendance_type(session)
						course = get_fac_time_course(request.session['hash1'],session_name)
						today_date = str(datetime.now().today()).split(' ')[0]
						status=200
						data_values={'sub_attendance_type':attendance_sub_type,'course':course,'today_date':today_date}

				elif(request.method=='POST'):
					data = json.loads(request.body)
					remark={}
					try:
						remark=data['remark']
					except:
						remark=None
					lecture = list(data['lecture'])
					date = datetime.strptime(str(data['date']).split('T')[0],"%Y-%m-%d").date()
					att_type = data['att_type']
					section = data['section']
					subject_id = data['subject_id']
					group_id = data['group_id']
					isgroup = data['isgroup']
					present = data['present_students']
					all_uniq={}
					app = data['app']
					if 'time_stamp' not in data:
						time_stamp=""
					else:
						time_stamp = data['time_stamp']
						print(time_stamp)
					# time_stamp="2019-02-2 11:09:08"
					approval_status='APPROVED'

					flag_marked = False

					if isgroup == 'N':
						for lec in lecture:
							check = checkIsAttendanceAlreadyMarked(lec,section,None,date,session_name)
							if check['already_marked']:
								flag_marked = True
								status=202
								data_values={'msg':check['msg']}
								break

						if not flag_marked:
							q_sec_det = Sections.objects.filter(section_id=section).exclude(status='DELETE').values('sem_id__sem','sem_id__dept__course')
							year = math.ceil(q_sec_det[0]['sem_id__sem']/2.0)
							course = q_sec_det[0]['sem_id__dept__course']

							q_att_details = AttendanceSettings.objects.filter(session=session,year=year,att_sub_cat=att_type,course=course).exclude(status="DELETE").values('att_to_be_approved','att_sub_cat__value')
							if len(q_att_details)>0:
								if q_att_details[0]['att_to_be_approved'] == 'Y':
									approval_status = 'PENDING'
							sec=[]
							sec.append(section)
							section_students = get_section_students(sec,{},session_name)
							all_uniq_id = []
							for ss in section_students[0]:
								all_uniq_id.append(ss['uniq_id'])

							uniq_present = present
							uniq_absent = list(set(all_uniq_id) - set(uniq_present))
							for id in all_uniq_id:
								all_uniq[id]=None
							try:
								for uniq in remark:
									all_uniq[int(uniq)]=remark[uniq]
							except:
								pass
							for lec in lecture:
								if time_stamp == "":
									q_att_insert = Attendance.objects.create(lecture=lec,date=date,section=Sections.objects.get(section_id=section),app=app,subject_id=SubjectInfo.objects.get(id=subject_id),isgroup=isgroup,emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),normal_remedial=q_att_details[0]['att_sub_cat__value'][0].upper())

									present_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='P',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),approval_status=approval_status,marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_present)
									q_pres_ins = StudentAttStatus.objects.bulk_create(present_objs)
									
									if len(q_att_details)>0:
										print(q_att_details[0]['att_sub_cat__value'],"asadasafafafa")
										if q_att_details[0]['att_sub_cat__value']!='REMEDIAL':
											absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='A',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),approval_status='APPROVED',marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_absent)
											q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)
									else:
										absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='A',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),approval_status='APPROVED',marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_absent)
										q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)
								else:
									q_att_insert = Attendance.objects.create(lecture=lec,date=date,section=Sections.objects.get(section_id=section),app=app,time_stamp=time_stamp,subject_id=SubjectInfo.objects.get(id=subject_id),isgroup=isgroup,emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),normal_remedial=q_att_details[0]['att_sub_cat__value'][0].upper())

									present_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='P',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),time_stamp=time_stamp,approval_status=approval_status,marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_present)
									q_pres_ins = StudentAttStatus.objects.bulk_create(present_objs)
									
									if len(q_att_details)>0:
										if q_att_details[0]['att_sub_cat__value']!='REMEDIAL':
											absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='A',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),time_stamp=time_stamp,approval_status='APPROVED',marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_absent)
											q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)
									else:
										absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='A',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),time_stamp=time_stamp,approval_status='APPROVED',marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_absent)
										q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)

							status=200
							data_values={'msg':'Attendance Successfully marked'}
					else:
						group_section = get_group_sections(group_id,session_name)
						for gs in group_section:
							for lec in lecture:
								check = checkIsAttendanceAlreadyMarked(lec,gs,group_id,date,session_name)
								if check['already_marked']:
									flag_marked=True
									status=202
									data_values={'msg':check['msg']}
									break

							if flag_marked:
								break

						if not flag_marked:
							group_students = get_att_group_students(group_id,session_name)
							n=len(group_students)
							for i in range(n):
								q_sec_det = Sections.objects.filter(section_id=group_section[i]).exclude(status='DELETE').values('sem_id__sem','sem_id__dept__course')
								year = math.ceil(q_sec_det[0]['sem_id__sem']/2.0)
								course = q_sec_det[0]['sem_id__dept__course']

								q_att_details = AttendanceSettings.objects.filter(session=session,year=year,att_sub_cat=att_type,course=course).exclude(status="DELETE").values('att_to_be_approved','att_sub_cat__value')
								if len(q_att_details)>0:
									if q_att_details[0]['att_to_be_approved'] == 'Y':
										approval_status = 'PENDING'

								all_uniq_id = []
								for ss in group_students[i]:
									all_uniq_id.append(ss['uniq_id'])

								uniq_present = studentSession.objects.filter(section=group_section[i],uniq_id__in=present).values_list('uniq_id',flat=True)
								#uniq_present = present
								uniq_absent = list(set(all_uniq_id) - set(uniq_present))
								for id in all_uniq_id:
									all_uniq[id]=None
								try:
									for uniq in remark:
										all_uniq[int(uniq)]=remark[uniq]
								except:
									pass
								for lec in lecture:
									if time_stamp == "":
										q_att_insert = Attendance.objects.create(lecture=lec,date=date,section=Sections.objects.get(section_id=group_section[i]),app=app,subject_id=SubjectInfo.objects.get(id=subject_id),isgroup=isgroup,emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),group_id=SectionGroupDetails.objects.get(id=group_id),normal_remedial=q_att_details[0]['att_sub_cat__value'][0].upper())

										present_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='P',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),time_stamp=time_stamp,approval_status=approval_status,marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_present)
										q_pres_ins = StudentAttStatus.objects.bulk_create(present_objs)

										if len(q_att_details)>0:
											if q_att_details[0]['att_sub_cat__value']!='REMEDIAL':
												absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='A',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),approval_status='APPROVED',marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_absent)
												q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)
										else:
											absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='A',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),approval_status='APPROVED',marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_absent)
											q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)
									else:
										q_att_insert = Attendance.objects.create(lecture=lec,date=date,section=Sections.objects.get(section_id=group_section[i]),app=app,subject_id=SubjectInfo.objects.get(id=subject_id),isgroup=isgroup,emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),group_id=SectionGroupDetails.objects.get(id=group_id),normal_remedial=q_att_details[0]['att_sub_cat__value'][0].upper())

										present_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='P',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),time_stamp=time_stamp,approval_status=approval_status,marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_present)
										q_pres_ins = StudentAttStatus.objects.bulk_create(present_objs)

										if len(q_att_details)>0:
											if q_att_details[0]['att_sub_cat__value']!='REMEDIAL':
												absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='A',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),time_stamp=time_stamp,approval_status='APPROVED',marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_absent)
												q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)
										else:
											absent_objs = (StudentAttStatus(att_id=Attendance.objects.get(id=q_att_insert.id),uniq_id=studentSession.objects.get(uniq_id=uniq),present_status='A',att_type=StudentAcademicsDropdown.objects.get(sno=att_type),time_stamp=time_stamp,approval_status='APPROVED',marked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),remark=all_uniq[uniq]) for uniq in uniq_absent)
											q_abs_ins = StudentAttStatus.objects.bulk_create(absent_objs)

								status=200
								data_values={'msg':'Attendance Successfully marked'}
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500

	return JsonResponse(data=data_values,status=status)