# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import Achievement as achievement
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
from datetime import datetime, date
import datetime
import json

from StudentMMS.constants_functions import requestType

from musterroll.models import EmployeePerdetail, Roles
from Registrar.models import *
from login.models import EmployeeDropdown, EmployeePrimdetail
from Achievement.models import *

# from Achievement.views.achievement_checks_function import *
from login.views import checkpermission, generate_session_table_name
# Create your views here.

#############################  AAR DROPDOWN FUNCTIONS ################################################################


def GetDiscipline():
	qry = []
	qry = list(EmployeeDropdown.objects.filter(field='DEPARTMENT').exclude(value__isnull=True).values('sno', 'pid', 'field', 'value').distinct())
	return qry

def GetOrganization():
	qry = []
	qry= list(EmployeeDropdown.objects.filter(field='ORGANIZATION').exclude(value__isnull=True).extra(select={'org_id': 'sno', 'org_name': 'value'}).values('org_id', 'org_name'))
	return qry

def GetEmpCategory():
	qry = []
	qry = list(EmployeeDropdown.objects.filter(field='CATEGORY OF EMPLOYEE').exclude(value__isnull=True).extra(select={'coe_id': 'sno', 'coe': 'value'}).values('coe', 'coe_id'))
	return qry

def GetEmployee(department,emp_category):
	qry = []
	qry = list(EmployeePrimdetail.objects.filter(emp_status='Active',dept__in=department,emp_category__in=emp_category).extra(select={'id': 'emp_id', 'nm': 'name'}).values('id', 'nm'))
	return qry

############ BOOKS ###########################################


def GetRoleBook():
	data = []
	qry = list(AarDropdown.objects.filter(field='BOOKS', value='ROLE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetBookFor():
	data = []
	qry = list(AarDropdown.objects.filter(field='BOOKS', value='FOR').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetPublisherType():

	data = []

	qry = list(AarDropdown.objects.filter(field='BOOKS', value='PUBLISHER TYPE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetLocalAuthor():
	data = []
	qry = list(AarDropdown.objects.filter(field='BOOKS', value='LOCAL AUTHOR').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetCopyrightStatus():
	qry = []
	qry = list(AarDropdown.objects.filter(field="COPYRIGHT STATUS").exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return qry
#############################################################
################ CONFERENCE #################################


def GetConferenceCategory():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE', value='CATEGORY').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'field', 'pid', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'field', 'pid', 'value'))
	return data


def GetConfernenceType():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE', value='TYPE OF JOURNAL').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'field', 'pid', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetConferenceSubCategory():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE', value='SUB CATEGORY').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'field', 'pid', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetConferenceAuthor():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE', value='AUTHOR').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data

def GetConferenceOrganiser():
	data = []

	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE', value='ORGANIZED BY').exclude(value__isnull=True).values('sno', 'pid', 'field', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).values('sno', 'pid', 'field', 'value').distinct())
	return data

def GetConferenceActivityType():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE', value='TYPE OF ACTIVITY').exclude(value__isnull=True).values('sno', 'pid', 'field', 'value').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data

############################################################
############### GUIDANCE ###################################


def GetGuidance():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE', value='GUIDANCE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'value', 'field').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(value="STATUS").exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	return data


def GetGuidanceStatus():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE', value='GUIDANCE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'value', 'field'))
	for q in qry:
		qry1 = list(AarDropdown.objects.filter(pid=q['sno'], value='RESEARCH (PH. D.)').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	for q1 in qry1:
		data = list(AarDropdown.objects.filter(pid=q1['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetGuidanceCourse():
	qry = []
	qry = list(StudentDropdown.objects.filter(Q(field='COURSE') | Q(field="PG DEGREE") | Q(field="UG DEGREE")).exclude(value__isnull=True).values('sno', 'pid', 'value', 'field'))
	return qry


def GetGuidanceDegree():
	qry = list(StudentDropdown.objects.filter(field='PG DEGREE').exclude(value__isnull=True).values('sno', 'pid', 'value', 'field').distinct())
	return qry


def GetUnivType():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE', value='UNIVERSITY TYPE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'value', 'field').distinct())
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'value', 'field').distinct())
	return data
###########################################################
################ JOURNAL ##################################


def GetJournalCategory():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL', value='CATEGORY').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetJournalType():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL', value='TYPE OF JOURNAL').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'value', 'field'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetJournalSubCategory():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL', value='SUB CATEGORY').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetJournalAuthor():
	data = []
	qry = list(AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL', value='AUTHOR').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data
###########################################################
################### PATENT ################################


def GetPatentIncorporateStatus():
	data = []
	qry = list(AarDropdown.objects.filter(field='PATENT', value='INCORPORATE STATUS').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetPatentOwner():
	data = []
	qry = list(AarDropdown.objects.filter(field='PATENT', value='OWNER').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetPatentLevel():
	data = []
	qry = list(AarDropdown.objects.filter(field='PATENT', value='LEVEL').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetPatentStatus():
	data = []
	qry = list(AarDropdown.objects.filter(field='PATENT', value='STATUS').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data

###########################################################
############### LECTURES AND TALKS ########################


def GetLecTalksCategory():
	data = []
	qry = list(AarDropdown.objects.filter(field='LECTURES AND TALKS', value='CATEGORY').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetLecTalksType():
	data = []
	qry = list(AarDropdown.objects.filter(field='LECTURES AND TALKS', value='TYPE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetLecTalksOrgSec():
	data = []
	qry = list(AarDropdown.objects.filter(field='LECTURES AND TALKS', value='ORGANIZATION SECTOR').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetLecTalksIncorpSec():
	data = []
	qry = list(AarDropdown.objects.filter(field='LECTURES AND TALKS', value='INCORPORATION SECTOR').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetLecTalksRole():
	data = []
	qry = list(AarDropdown.objects.filter(field='LECTURES AND TALKS', value='ROLE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data
#############################################################
############ TRAINING AND DEVELOPMENT #######################


def GetTrainingDevopCategory():
	data = []
	qry = list(AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM', value='CATEGORY').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetTrainingDevopType():
	data = []
	qry = list(AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM', value='TYPE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetTrainingDevopRole():
	data = []
	qry = list(AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM', value='ROLE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetTrainingDevopOrgSec():
	data = []
	qry = list(AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM', value='ORGANIZATION SECTOR').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetTrainingDevopIncorpType():
	data = []
	qry = list(AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM', value='INCORPORATION TYPE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetTrainingDevopVenue():
	data = []
	qry = list(AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM', value='VENUE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data

def GetTrainingDevopSubType():
	data = []
	qry = list(AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM', value='SUB-TYPE').exclude(value__isnull=True).values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).values('sno', 'pid', 'field', 'value').distinct())
	return data
##############################################################
######### PROJECT/CONSULTANCY ################################


def GetProjectType():
	data = []
	qry = list(AarDropdown.objects.filter(field='PROJECTS/CONSULTANCY', value='TYPE').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetProjectStatus():
	data = []
	qry = list(AarDropdown.objects.filter(field='PROJECTS/CONSULTANCY', value='STATUS').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetProjectSector():
	data = []
	qry = list(AarDropdown.objects.filter(field='PROJECTS/CONSULTANCY', value='SECTOR').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data

############################ AAR DROPDOWN FUNCTIONS END ###########################################


def GetForms():
	Forms = []
	Forms = [{"sno": 1, "value": "BOOKS"},
			 {"sno": 2, "value": "RESEARCH PAPER IN CONFERENCE"},
			 {"sno": 3, "value": "RESEARCH GUIDANCE / PROJECT GUIDANCE"},
			 {"sno": 4, "value": "RESEARCH PAPER IN JOURNAL"},
			 {"sno": 5, "value": "PATENT"},
			 {"sno": 6, "value": "LECTURES AND TALKS"},
			 {"sno": 7, "value": "TRAINING AND DEVELOPMENT PROGRAM"},
			 {"sno": 8, "value": "PROJECTS/CONSULTANCY"},
			 {"sno": 9, "value": "DESIGN"},
			 {"sno": 10, "value": "ACTIVITY"}]
	return Forms


def RequestForApproval(form_type, form_id):
	AchFacApproval.objects.create(level=1, approval_category=form_type, approval_id=form_id, approval_status='PENDING')
	return True


def GetApprovalRequests(form_type, form_id):
	qry = []
	qry = list(AchFacApproval.objects.filter(approval_category=form_type, approval_id=form_id, level=1, approval_status='PENDING').exclude(status="DELETE").values_list('id', flat=True))
	return qry


def GetApprovalStatus(data, category):
	qry = list(AchFacApproval.objects.filter(approval_id=data['id'], level=1, approval_category=category).exclude(status="DELETE").values_list('approval_status', flat=True))
	if len(qry) > 0:
		status = qry[0]
	else:
		status = None
	return status


def GetDOJ(emp_id):
	qry = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values_list('doj', flat=True))
	if len(qry) > 0:
		date = qry[0]
	else:
		date = None
	return date


def GetBooks():
	qry = []
	qry = list(AchFacBooks.objects.values_list('book_title', flat=True))
	return qry


#################### TABLE DATA CHECKS FUNCTIONS ##################################################


def GetPublisherIdCheck(data):
	qry = []
	publisher_name = data['publisher_name']
	if 'publisher_address' in data:
		publisher_address_1 = data['publisher_address']
		publisher_address_2 = None
	elif 'publisher_address1' in data:
		publisher_address_1 = data['publisher_address1']
		publisher_address_2 = data['publisher_address2']
	else:
		publisher_address_1 = data['publisher_address_1']
		publisher_address_2 = data['publisher_address_2']
	publisher_zip_code = data['publisher_zip_code']
	publisher_contact = data['publisher_contact']
	publisher_email = data['publisher_email']
	publisher_website = data['publisher_website']
	qry = list(AchFacPublishers.objects.filter(publisher_name=publisher_name, publisher_address_1=publisher_address_1, publisher_address_2=publisher_address_2, publisher_zip_code=publisher_zip_code, publisher_contact=publisher_contact, publisher_email=publisher_email, publisher_website=publisher_website).exclude(status="DELETE").values_list('id', flat=True))
	return qry


def GetConferenceIdCheck(data):
	qry = []
	conference_title = data['conference_title']
	type_of_conference = data['type_of_conference']
	conference_from = data['conference_from']
	conference_to = data['conference_to']
	organized_by = data['organized_by']
	qry = list(AchFacConferenceDetail.objects.filter(conference_title=conference_title, type_of_conference=type_of_conference, conference_from=conference_from, conference_to=conference_to, organized_by=organized_by).exclude(status="DELETE").values_list('id', flat=True))
	return qry


def GetJournalDetailsCheck(data):
	qry = []
	journal_name = data['journal_name']
	type_of_journal = data['type_of_journal']
	sub_category = data['sub_category']
	volume_no = data['volume_no']
	issue_no = data['issue_no']
	isbn = data['isbn']
	qry = list(AchFacJournalDetail.objects.filter(journal_name=journal_name, type_of_journal=type_of_journal, sub_category=sub_category, volume_no=volume_no, issue_no=issue_no, isbn=isbn).exclude(status="DELETE").values_list('id', flat=True))
	return qry


def GetSponsorsIdCheck(data):
	qry = []
	if 'organisation' in data:
		organisation = data['organisation']
	if 'sponser_name' in data:
		organisation = data['sponser_name']
	pin_code = data['pin_code']
	address = data['address']
	contact_person = data['contact_person']
	contact_number = data['contact_number']
	e_mail = data['e_mail']
	website = data['website']
	amount = data['amount']
	qry = list(AchFacSponser.objects.filter(organisation=organisation, pin_code=pin_code, address=address, contact_number=contact_number, contact_person=contact_person, e_mail=e_mail, website=website, amount=amount).exclude(status="DELETE").values_list('id', flat=True))
	return qry


def GetCollaboratorsIdCheck(data):
	qry = []
	if 'organisation' in data:
		organisation = data['organisation']
	if 'sponser_name' in data:
		organisation = data['sponser_name']
	pin_code = data['pin_code']
	address = data['address']
	contact_person = data['contact_person']
	contact_number = data['contact_number']
	e_mail = data['e_mail']
	website = data['website']
	amount = data['amount']
	qry = list(AchFacCollaborators.objects.filter(organisation=organisation, pin_code=pin_code, address=address, contact_number=contact_number, contact_person=contact_person, e_mail=e_mail, website=website, amount=amount).exclude(status="DELETE").values_list('id', flat=True))
	return qry


def GetAssociationsIdCheck(data):
	qry = []
	if 'organisation' in data:
		organisation = data['organisation']
	if 'sponser_name' in data:
		organisation = data['sponser_name']
	pin_code = data['pin_code']
	address = data['address']
	contact_person = data['contact_person']
	contact_number = data['contact_number']
	e_mail = data['e_mail']
	website = data['website']
	amount = data['amount']
	qry = list(AchFacAssociations.objects.filter(organisation=organisation, pin_code=pin_code, address=address, contact_number=contact_number, contact_person=contact_person, e_mail=e_mail, website=website, amount=amount).exclude(status="DELETE").values_list('id', flat=True))
	return qry


def GetPatentDetailsIdCheck(data, patent_number, application_no):
	# print(data,patent_number,application_no,'vrinda')
	qry = []
	if 'patent_title' in data:
		patent_title = data['patent_title']
	elif 'title' in data:
		patent_title = data['title']
	if 'patent_description' in data:
		patent_description = data['patent_description']
	elif 'descreption' in data:
		patent_description = data['descreption']
	if 'patent_status' in data:
		patent_status = data['patent_status']
		level = data['level']
	elif 'status' in data:
		if data['status'] == 'fill':
			query1 = list(AarDropdown.objects.filter(field='STATUS', value='IF FILLED').exclude(status="DELETE").values_list('sno', flat=True))
		elif data['status'] == 'grant':
			query1 = list(AarDropdown.objects.filter(field='STATUS', value='IF GRANTED').exclude(status="DELETE").values_list('sno', flat=True))
		patent_status = query1[0]
		level_val = data['level']
		query2 = list(AarDropdown.objects.filter(field='LEVEL', value=level_val).exclude(status="DELETE").values_list('sno', flat=True))
		level = query2[0]
	owner = data['owner']
	qry = list(AchFacPatentDetail.objects.filter(patent_title=patent_title, patent_description=patent_description, level=level, patent_status=patent_status, patent_number=patent_number, application_no=application_no, owner=owner).exclude(status="DELETE").values_list('id', flat=True))
	return qry


def GetPatentCollaboratorsIdCheck(data):
	qry = []
	company_name = data['company_name']
	incorporate_status = data['incorporate_status']
	qry = list(AchFacPatentCollaborator.objects.filter(company_name=company_name, incorporate_status=incorporate_status).exclude(status="DELETE").values_list('id', flat=True))
	return qry


def LecTalksVenueIdCheck(data):
	qry = []
	venue = data['venue']
	address = data['address']
	pin_code = data['pin_code']
	contact_number = data['contact_number']
	e_mail = data['e_mail']
	website = data['website']
	qry = list(AchFacLecturesTalksVenue.objects.filter(venue=venue, address=address, pin_code=pin_code, contact_number=contact_number, e_mail=e_mail, website=website).exclude(status="DELETE").values_list('id', flat=True))
	return qry
###################################################################################################
################### APPRAISAL LINK ##############


def GetAllAchievementEmployee(emp_id, ach_type, session):
    ach = str(ach_type)
    data = []
    extra_filter = {}
    if ach == "BOOKS":
        form_id = 1
    if ach == "RESEARCH PAPER IN CONFERENCE":
        form_id = 2
    if ach == "RESEARCH GUIDANCE / PROJECT GUIDANCE":
        form_id = 3
    if ach == "RESEARCH PAPER IN JOURNAL":
        form_id = 4
    if ach == "PATENT":
        form_id = 5
    if ach == "LECTURES AND TALKS":
        form_id = 6
    if ach == "TRAINING AND DEVELOPMENT PROGRAM":
        form_id = 7
    if ach == "PROJECTS/CONSULTANCY":
        form_id = 8
    if ach == 'DESIGN':
        form_id = 9
    if ach == 'ACTIVITY':
        form_id = 10
    extra_filter = {'emp_id': emp_id}
    from_date = datetime.date(2019, 8, 1)
    to_date = datetime.date(2020, 7, 31)
    # Change by Dhruv
    qry = achievement.views.achievement_report.ReportFunction(form_id, extra_filter, from_date, to_date)
    if len(qry) > 0:
        for q in qry:
            if q['approval_status'] == "APPROVED":
                data.append(q)
    return data


def GetAllActivitiesEmployee(emp_id,level):
	data = []
	
	## FOR FACULTY APPRAISAL ##
	# from_date = datetime.date(2019, 8, 1)
	to_date = datetime.date(2019, 8, 1)
	level_value = AarDropdown.objects.filter(field='LEVEL',value__in=level).exclude(status="DELETE").exclude(value__isnull=True).values_list('sno',flat=True)
	data = list(AchFacActivity.objects.filter(act_end_date__gte=to_date,act_level__in=level_value).filter(Q(coord_detail__act_main_emp_id__contains=[emp_id])|Q(coord_detail__act_co_emp_id__contains=[emp_id])).exclude(status="DELETE").values('id','act_level','act_level__value','act_type','act_type__value','act_sub_type','act_sub_type__value','act_start_date','act_end_date','act_description','coord_detail','coord_detail__act_main_org','coord_detail__act_main_dept','coord_detail__act_main_category','coord_detail__act_main_emp_id','coord_detail__act_co_org','coord_detail__act_co_dept','coord_detail__act_co_category','coord_detail__act_co_emp_id'))
	for d in data:
		d['marks'] = 0
		for l in level:
			if 'DEPARTMENTAL' in l:
				l= 'DEP'
			elif "INSTITUTIONAL" in l:
				l= 'INST'
			qry = AarDropdown.objects.filter(pid=d['act_sub_type'],value__contains=l).exclude(status="DELETE").exclude(value__isnull=True).values()
			if len(qry)>0:
				qry1 = list(AarDropdown.objects.filter(pid=qry[0]['sno'],field=qry[0]['value']).exclude(status="DELETE").exclude(value__isnull=True).values("value"))
				if len(qry1)>0:
					d['marks'] += int(qry1[0]['value'])
	return data

#################################################

 ######################################################################### DESIGN #################################################
def GetDesignIncorporateStatus():
	data = []
	qry = list(AarDropdown.objects.filter(field='DESIGN', value='INCORPORATE STATUS').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetDesignOwner():
	data = []
	qry = list(AarDropdown.objects.filter(field='DESIGN', value='OWNER').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetDesignLevel():
	data = []
	qry = list(AarDropdown.objects.filter(field='DESIGN', value='LEVEL').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetDesignStatus():
	data = []
	qry = list(AarDropdown.objects.filter(field='DESIGN', value='STATUS').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data
 ###############################################################################################################################
 ############################################################### ACTIVITY ###########################################################

def GetActivityLevel():
	data = []
	qry = list(AarDropdown.objects.filter(field='ACTIVITY', value='LEVEL').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data

def GetActivityType():
	data = []
	qry = list(AarDropdown.objects.filter(field='ACTIVITY', value='TYPE OF ACTIVITY').exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	for q in qry:
		data = list(AarDropdown.objects.filter(pid=q['sno']).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value').distinct())
	return data


def GetActivitySubCategory(type_id):
	data = []
	data = list(AarDropdown.objects.filter(pid = type_id).exclude(value__isnull=True).exclude(status="DELETE").values('sno', 'pid', 'field', 'value'))
	return data
##################################################################################################################################################################