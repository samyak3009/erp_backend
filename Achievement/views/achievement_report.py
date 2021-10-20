
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse

from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField
from datetime import date, datetime, time
import json

# Create your views here.
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

from musterroll.models import EmployeePerdetail, Roles
from login.models import EmployeePrimdetail
from Achievement.models import *

from Achievement.views.achievement_views import *
from Achievement.views.achievement_function import *
from Achievement.views.achievement_checks_function import *
from login.views import checkpermission, generate_session_table_name


def ReportFunction(form_id, extra_filter, from_date, to_date):
	data = []
	if int(form_id) == 1:  # BOOKS #####################################
		if from_date != None:
			# extra_filter.update({'published_date__gte': from_date, 'published_date__lte': to_date})
			extra_filter.update({'published_date__range': [from_date, to_date]})
		data = list(AchFacBooks.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'role', 'role__value', 'role_for', 'role_for__value', 'book_title', 'book_edition', 'published_date', 'isbn', 'chapter', 'author', 'author__value', 'copyright_status', 'copyright_status__value', 'publisher_type', 'publisher_type__value', 'copyright_no', 'publisher_details', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website'))
		for d in data:
			qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='BOOKS', level=1).exclude(status="DELETE").exclude(approval_status="DELETE").values('approval_status'))
			if len(qry) > 0:
				d['approval_status'] = qry[0]['approval_status']
			else:
				d['approval_status'] = None

	elif int(form_id) == 2:  # RESEARCH PAPER IN CONFERENCE ##################
		if from_date != None:
			# extra_filter.update({'conference_detail__conference_to__lte': to_date, 'conference_detail__conference_from__gte': from_date})
			extra_filter.update({'conference_detail__conference_from__range': [from_date, to_date]})
		data = list(AchFacConferences.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category', 'category__value', 'conference_detail', 'conference_detail__conference_title', 'conference_detail__type_of_conference', 'conference_detail__type_of_conference__value', 'conference_detail__conference_from', 'conference_detail__type_of_activity__value','conference_detail__type_of_activity','conference_detail__conference_to', 'conference_detail__organized_by', 'sub_category', 'sub_category__value', 'paper_title', 'published_date', 'journal_name', 'volume_no', 'issue_no', 'isbn', 'page_no', 'author', 'author__value', 'other_description', 'publisher_details', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website', 'others', 'time_stamp').order_by('time_stamp'))
		for d in data:
			data2 = list(AchFacMultiDetails.objects.filter(details_for='RESEARCH PAPER IN CONFERENCE', key_id=d['id']).values_list('detail_text', flat=True))
			d['sponsered'] = data2
			if len(data2) > 0:
				d['is_sponser'] = 1
			else:
				d['is_sponser'] = 2
			qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='RESEARCH PAPER IN CONFERENCE', level=1).exclude(status="DELETE").exclude(approval_status="DELETE").values('approval_status'))
			if len(qry) > 0:
				d['approval_status'] = qry[0]['approval_status']
			else:
				d['approval_status'] = None

	elif int(form_id) == 3:  # RESEARCH GUIDANCE / PROJECT GUIDANCE ##################
		if from_date != None:
			extra_filter.update({'date_of_guidance__range': [from_date, to_date]})
		data = list(AchFacGuidances.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'guidance_for', 'guidance_for__value', 'course', 'course__value', 'degree', 'degree__value', 'guidance_awarded_status', 'university_type', 'university_type__value', 'university_name', 'guidance_status', 'guidance_status__value', 'no_of_students', 'project_title', 'area_of_specification', 'date_of_guidance', 'time_stamp').order_by('time_stamp'))
		for d in data:
			qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='RESEARCH GUIDANCE / PROJECT GUIDANCE', level=1).exclude(status="DELETE").exclude(approval_status="DELETE").values('approval_status'))
			if len(qry) > 0:
				d['approval_status'] = qry[0]['approval_status']
			else:
				d['approval_status'] = None

	elif int(form_id) == 4:  # RESEARCH PAPER IN JOURNAL ##################
		if from_date != None:
			extra_filter.update({'published_date__range': [from_date, to_date]})
		data = list(AchFacJournals.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category', 'category__value', 'author', 'author__value', 'published_date', 'paper_title', 'impact_factor', 'page_no', 'journal_details', 'journal_details__journal_name', 'journal_details__type_of_journal', 'journal_details__type_of_journal__value', 'journal_details__sub_category', 'journal_details__sub_category__value', 'journal_details__volume_no', 'journal_details__issue_no', 'journal_details__isbn', 'publisher_details', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website', 'others', 'time_stamp').order_by('time_stamp'))
		for d in data:
			qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='RESEARCH PAPER IN JOURNAL', level=1).exclude(status="DELETE").exclude(approval_status="DELETE").values('approval_status'))
			if len(qry) > 0:
				d['approval_status'] = qry[0]['approval_status']
			else:
				d['approval_status'] = None

	elif int(form_id) == 5:  # PATENT ##################
		if from_date != None:
			extra_filter.update({'patent_date__range': [from_date, to_date]})
		data = list(AchFacPatents.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'patent_details', 'patent_details__patent_title', 'patent_details__patent_description', 'patent_details__level', 'patent_details__level__value', 'patent_details__patent_status', 'patent_details__patent_status__value', 'patent_details__patent_number', 'patent_details__application_no', 'patent_details__owner', 'patent_details__owner__value','patent_details__patent_applicant_name','patent_details__patent_co_applicant_name', 'patent_date', 'time_stamp').order_by('time_stamp'))
		for d in data:
			qry = list(AchFacPatentCollaborator.objects.filter(patent_in=d['id']).exclude(status="DELETE").values('company_name', 'incorporate_status', 'incorporate_status__value'))
			if len(qry) > 0:
				d['is_collaborator'] = 1
				d['company_name'] = qry[0]['company_name']
				d['incorporate_status'] = qry[0]['incorporate_status']
				d['incorporate_status__value'] = qry[0]['incorporate_status__value']
			else:
				d['is_collaborator'] = 2
				d['company_name'] = None
				d['incorporate_status'] = None
				d['incorporate_status__value'] = None
			qry2 = list(AchFacMultiDetails.objects.filter(details_for="PATENT", key_id=d['id']).values('details_for', 'key_id', 'detail_emp', 'detail_emp__value'))
			if len(qry2) > 0:
				discipline_id = []
				discipline_value = []
				for q in qry2:
					discipline_id.append(q['detail_emp'])
					discipline_value.append(q['detail_emp__value'])
				d['detail_emp'] = discipline_id
				d['detail_emp__value'] = discipline_value
			else:
				d['detail_emp'] = None
				d['detail_emp__value'] = None
			qry3 = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='PATENT', level=1).exclude(approval_status="DELETE").exclude(status="DELETE").values('approval_status'))
			if len(qry3) > 0:
				d['approval_status'] = qry3[0]['approval_status']
			else:
				d['approval_status'] = None
		print(data)

	elif int(form_id) == 6:  # LECTURES AND TALKS ##################
		if from_date != None:
			extra_filter.update({'date__range': [from_date, to_date]})
		data = list(AchFacLecturesTalks.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category', 'category__value', 'type_of_event', 'type_of_event__value', 'organization_sector', 'organization_sector__value', 'incorporation_status', 'incorporation_status__value', 'role', 'role__value', 'venue_detail', 'venue_detail__venue', 'venue_detail__address', 'venue_detail__pin_code', 'venue_detail__contact_number', 'venue_detail__e_mail', 'venue_detail__website', 'date', 'topic', 'participants', 'time_stamp').order_by('time_stamp'))
		for d in data:
			qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='LECTURES AND TALKS', level=1).exclude(approval_status="DELETE").exclude(status="DELETE").values('approval_status'))
			if len(qry) > 0:
				d['approval_status'] = qry[0]['approval_status']
			else:
				d['approval_status'] = None

	elif int(form_id) == 7:  # TRAINING AND DEVELOPMENT PROGRAM ##################
		if from_date != None:
			extra_filter.update({'from_date__range': [from_date, to_date]})
			# extra_filter.update({'from_date__gte': from_date, 'to_date__lte': to_date})
		data = list(AchFacTrainings.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category', 'category__value', 'training_type', 'training_type__value', 'training_sub_type','training_sub_type__value', 'role', 'role__value', 'organization_sector', 'organization_sector__value', 'incorporation_type', 'incorporation_type__value', 'from_date', 'to_date', 'title', 'venue', 'venue__value', 'venue_other', 'other', 'participants', 'organizers', 'attended', 'collaborations', 'sponsership', 'time_stamp').order_by('time_stamp'))
		for d in data:
			qry1 = list(AchFacMapIds.objects.filter(form_id=d['id'], form_type='TRAINING AND DEVELOPMENT PROGRAM').exclude(status="DELETE").values('key_id', 'key_type'))
			sponser_id = []
			collab_id = []
			for q in qry1:
				if q['key_type'] == 'SPONSORS':
					sponser_id.append(q['key_id'])
				elif q['key_type'] == 'COLLABORATORS':
					collab_id.append(q['key_id'])
			query1 = list(AchFacSponser.objects.filter(id__in=sponser_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
			d['sponsers'] = query1
			query2 = list(AchFacCollaborators.objects.filter(id__in=collab_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
			d['collaborators'] = query2
			qry2 = list(AchFacMultiDetails.objects.filter(details_for='TRAINING AND DEVELOPMENT PROGRAM', key_id=d['id']).values('detail_emp', 'detail_emp__value'))
			if len(qry2) > 0:
				discipline_id = []
				discipline_value = []
				for q in qry2:
					discipline_id.append(q['detail_emp'])
					discipline_value.append(q['detail_emp__value'])
				d['detail_emp'] = discipline_id
				d['detail_emp__value'] = discipline_value
			else:
				d['detail_emp'] = None
				d['detail_emp__value'] = None
			qry3 = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='TRAINING AND DEVELOPMENT PROGRAM', level=1).exclude(status="DELETE").exclude(approval_status="DELETE").values('approval_status'))
			if len(qry3) > 0:
				d['approval_status'] = qry3[0]['approval_status']
			else:
				d['approval_status'] = None

	elif int(form_id) == 8:  # PROJECTS/CONSULTANCY ##################
		# print("vrindas")
		if from_date != None:
			# extra_filter.update({'start_date__range': [from_date, to_date]})
			extra_filter.update({'start_date__lte': to_date, 'end_date__gte': from_date})
		data = list(AchFacProjects.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'project_type', 'project_type__value', 'project_status', 'project_status__value', 'sector', 'sector__value', 'project_title', 'project_description', 'start_date', 'end_date', 'principal_investigator', 'co_principal_investigator', 'principal_investigator_other', 'co_principal_investigator_other', 'team_size', 'sponsored', 'association', 'time_stamp').order_by('time_stamp'))
		for d in data:
			d['amount'] = 0
			qry1 = list(AchFacMapIds.objects.filter(form_id=d['id'], form_type='PROJECTS/CONSULTANCY').exclude(status="DELETE").values('key_id', 'key_type'))
			# print(qry1,'qry1')
			sponser_id = []
			asso_id = []
			for q in qry1:
				if q['key_type'] == 'SPONSORS':
					sponser_id.append(q['key_id'])
				elif q['key_type'] == 'ASSOCIATIONS':
					asso_id.append(q['key_id'])
				# print(sponser_id,'sponser_id',asso_id,'asso_id')
			query1 = list(AchFacSponser.objects.filter(id__in=sponser_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
			for q in query1:
				try:
					q['amount'] = float(q['amount'])
				except:
					q['amount'] = 0
				if q['amount'] != None and q['amount'] > 0:
					d['amount'] = d['amount'] + q['amount']
			d['sponsers'] = query1
			# print(query1,'query1')
			query2 = list(AchFacAssociations.objects.filter(id__in=asso_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
			for q in query2:
				try:
					q['amount'] = float(q['amount'])
				except:
					q['amount'] = 0
				if q['amount'] != None and q['amount'] > 0:
					d['amount'] = d['amount'] + q['amount']
			d['associators'] = query2
			# print(query2,'query2')
			qry2 = list(AchFacMultiDetails.objects.filter(details_for='PROJECTS/CONSULTANCY', key_id=d['id']).values('detail_emp', 'detail_emp__value'))
			if len(qry2) > 0:
				discipline_id = []
				discipline_value = []
				for q in qry2:
					discipline_id.append(q['detail_emp'])
					discipline_value.append(q['detail_emp__value'])
				d['detail_emp'] = discipline_id
				d['detail_emp__value'] = discipline_value
			else:
				d['detail_emp'] = None
				d['detail_emp__value'] = None
			qry3 = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='PROJECTS/CONSULTANCY', level=1).exclude(approval_status="DELETE").exclude(status="DELETE").values('approval_status'))
			if len(qry3) > 0:
				d['approval_status'] = qry3[0]['approval_status']
			else:
				d['approval_status'] = None
	elif int(form_id) == 9: #DESIGN
		if from_date != None:
			extra_filter.update({'design_date__range': [from_date, to_date]})
		data = list(AchFacDesign.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'design_title','design_description','design_applicant_name','design_co_applicant_name','design_applicant_name_other','design_co_applicant_name_other','design_company_name','design_incorporate_status','design_incorporate_status__value','design_level','design_level__value','design_status','design_status__value','design_application_no','design_date','design_level','design_level__value','design_status','design_status__value','design_application_no','design_owner','design_date','design_owner__value').order_by('time_stamp'))
		
		for d in data:
			qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='DESIGN', level=1).exclude(approval_status="DELETE").exclude(status="DELETE").values('approval_status'))
			if len(qry) > 0:
				d['approval_status'] = qry[0]['approval_status']
			else:
				d['approval_status'] = None

			qry2 = list(AchFacMultiDetails.objects.filter(details_for='DESIGN', key_id=d['id']).values('detail_emp', 'detail_emp__value'))
			if len(qry2) > 0:
				discipline_id = []
				discipline_value = []
				for q in qry2:
					discipline_id.append(q['detail_emp'])
					discipline_value.append(q['detail_emp__value'])
				d['detail_emp'] = discipline_id
				d['detail_emp__value'] = discipline_value
			else:
				d['detail_emp'] = None
				d['detail_emp__value'] = None

		# print(data,"here")
	return data


def EmployeeReport(request):
	data = []
	emp_id = request.session['hash1']
	if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
		if requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET, 'form_data')):
				Forms = GetForms()
				dept = EmployeeDropdown.objects.filter(field="DEPARTMENT").values('sno', 'value')
				data = {'Forms': Forms, 'Branch': list(dept)}

			elif(requestType.custom_request_type(request.GET, 'get_employee_report')):
				form_id = request.GET['form_id']
				from_date = request.GET['from_date'].split('T')[0]
				to_date = request.GET['to_date'].split('T')[0]
				data = ReportFunction(form_id, {'emp_id': emp_id}, from_date, to_date)

			elif(requestType.custom_request_type(request.GET, 'get_hod_report')):
				form_id = request.GET['form_id']
				from_date = request.GET['from_date'].split('T')[0]
				to_date = request.GET['to_date'].split('T')[0]
				hod_dept = EmployeePrimdetail.objects.filter(emp_id=emp_id).values_list('dept', flat=True)
				data = ReportFunction(form_id, {'emp_id__dept': hod_dept[0]}, from_date, to_date)

			elif(requestType.custom_request_type(request.GET, 'get_dean_report')):
				form_id = request.GET['form_id']
				from_date = request.GET['from_date'].split('T')[0]
				to_date = request.GET['to_date'].split('T')[0]
				dept = request.GET['dept'].split(',')
				data = ReportFunction(form_id, {'emp_id__dept__in': dept}, from_date, to_date)

			return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return funownerctions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def RND_Report(request):
	data = []
	emp_id = request.session['hash1']
	if checkpermission(request, [rolesCheck.ROLE_RND]) == statusCodes.STATUS_SUCCESS:
		if requestMethod.GET_REQUEST(request):
			if (requestType.custom_request_type(request.GET, 'form_data')):
				dept = EmployeeDropdown.objects.filter(field="DEPARTMENT").values('sno', 'value')
				data = list(dept)

			elif(requestType.custom_request_type(request.GET, 'form_data_new')):
				if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
					hod_dept = EmployeePrimdetail.objects.filter(emp_id = emp_id).values('dept')
					if len(hod_dept)>0:
						dept = EmployeeDropdown.objects.filter(sno=hod_dept[0]['dept'],field="DEPARTMENT").values('sno', 'value')
				if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
					dept = EmployeeDropdown.objects.filter(field="DEPARTMENT").values('sno', 'value')
				data = list(dept)

			elif(requestType.custom_request_type(request.GET, 'view_previous')):
				dept = request.GET['dept'].split(',')
				# from_date = request.GET['from_date'].split('T')[0]
				# to_date = request.GET['to_date'].split('T')[0]
				type = request.GET['type']
				if type == "BOOKS":
					form_id = 1
				elif type == "RESEARCH PAPER IN CONFERENCE":
					form_id = 2
				elif type == "RESEARCH GUIDANCE / PROJECT GUIDANCE":
					form_id = 3
				elif type == "RESEARCH PAPER IN JOURNAL":
					form_id = 4
				elif type == "PATENT":
					form_id = 5
				elif type == "LECTURES AND TALKS":
					form_id = 6
				elif type == "TRAINING AND DEVELOPMENT PROGRAM":
					form_id = 7
				elif type == "PROJECTS/CONSULTANCY":
					form_id = 8
				elif type== "DESIGN":
					form_id = 9
				data = ReportFunction(form_id, {'emp_id__dept__in': dept}, None, None)
			return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

		elif requestMethod.POST_REQUEST(request):
			data = json.loads(request.body)
			type = data['type']
			employee_id = data['employee_id']
			# print(employee_id,'employee_id')
			if type == "BOOKS":
				data_values = BooksFunction(data, employee_id)
			elif type == "RESEARCH PAPER IN CONFERENCE":
				data_values = ConferenceFunction(data, employee_id)
			elif type == "RESEARCH GUIDANCE / PROJECT GUIDANCE":
				data_values = GuidanceFunction(data, employee_id)
			elif type == "RESEARCH PAPER IN JOURNAL":
				data_values = JournalFunction(data, employee_id)
			elif type == "PATENT":
				data_values = PatentFunction(data, employee_id)
			elif type == "LECTURES AND TALKS":
				data_values = LecturesTalksFunction(data, employee_id)
			elif type == "TRAINING AND DEVELOPMENT PROGRAM":
				data_values = TrainingDevelopmentFunction(data, employee_id)
			elif type == "PROJECTS/CONSULTANCY":
				data_values = ProjectsConsultancyFunction(data, employee_id)
			elif type == "DESIGN":
				data_values= DesignFunction(data,employee_id)
			return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

		elif requestMethod.DELETE_REQUEST(request):
			data = json.loads(request.body)
			type = data['type']
			id = data['id']
			if type == "BOOKS":
				AchFacBooks.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='BOOKS').exclude(status="DELETE").update(status="DELETE")
			elif type == "RESEARCH PAPER IN CONFERENCE":
				AchFacConferences.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH PAPER IN CONFERENCE').exclude(status="DELETE").update(status="DELETE")
			elif type == "RESEARCH GUIDANCE / PROJECT GUIDANCE":
				AchFacGuidances.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH GUIDANCE / PROJECT GUIDANCE').update(status="DELETE")
			elif type == "RESEARCH PAPER IN JOURNAL":
				AchFacJournals.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH PAPER IN JOURNAL').exclude(status="DELETE").update(status="DELETE")
			elif type == "PATENT":
				AchFacPatents.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='PATENT').exclude(status="DELETE").update(status="DELETE")
			elif type == "LECTURES AND TALKS":
				AchFacLecturesTalks.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='LECTURES AND TALKS').exclude(status="DELETE").update(status="DELETE")
			elif type == "TRAINING AND DEVELOPMENT PROGRAM":
				AchFacTrainings.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='TRAINING AND DEVELOPMENT PROGRAM').exclude(status="DELETE").update(status="DELETE")
			elif type == "PROJECTS/CONSULTANCY":
				AchFacProjects.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='PROJECTS/CONSULTANCY').exclude(status="DELETE").update(status="DELETE")
			elif type == "DESIGN":
				AchFacDesign.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
				AchFacApproval.objects.filter(approval_id=id, approval_category='DESIGN').exclude(status="DELETE").update(status="DELETE")
			data = statusMessages.MESSAGE_DELETE
			return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return funownerctions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
