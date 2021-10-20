
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse,JsonResponse

from django.shortcuts import render
from django.db.models import Q,Sum,F,Value,CharField
from datetime import date,datetime,time
import json

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod

from musterroll.models import EmployeePerdetail,Roles
from Registrar.models import *
from login.models import EmployeePrimdetail,EmployeeDropdown
from Achievement.models import *

from Achievement.views.achievement_function import *
from login.views import checkpermission,generate_session_table_name

def BookFormAuthorCheck(chapter,book_title,author):
	author_value=""
	all_authors = GetLocalAuthor()
	for a in all_authors:
		if a['sno']==author:
			author_value = a['value']
	if author_value == 'FIRST AUTHOR':
		qry = list(AchFacBooks.objects.filter(author__value='FIRST AUTHOR',book_title=book_title,chapter=chapter).exclude(status="DELETE").values_list('id',flat=True))
	else:
		qry = list(AchFacBooks.objects.filter(author__value='SINGLE AUTHOR',book_title=book_title,chapter=chapter).exclude(status="DELETE").values_list('id',flat=True))
	if len(qry)>0:
		return False
	else:
		return True

def ConferenceCategoryCheck(data):
	category = data['category']
	category1 = GetConferenceCategory()
	for c in category1:
		if c['sno']==category and c['value']=="PUBLISHED":
			cat_check = True
		elif c['sno']==category and c['value']=="PRESENTED":
			cat_check = True
		else:
			cat_check = False
	return cat_check

def ConferenceAuthorCheck(data):
	conference_title = data['conference_title']
	conference_from = data['conference_from']
	type_of_conference = data['type_of_conference']
	conference_to = data['conference_to']
	organized_by = data['organized_by']
	paper_title = data['paper_title']
	author = data['author']
	conf = list(AchFacConferenceDetail.objects.filter(conference_title=conference_title,conference_from=conference_from,type_of_conference=type_of_conference,conference_to=conference_to,organized_by=organized_by).exclude(status="DELETE").values_list('id',flat=True))
	if len(conf)>0:
		conference_detail = conf[0]
	else:
		conference_detail = None
	author = GetConferenceAuthor()
	for a in author:
		if a['value']=='FIRST AUTHOR':
			first_auth = a['sno']
		elif a['value']=='SINGLE AUTHOR':
			single_auth = a['sno']
	qry = list(AchFacConferences.objects.filter(conference_detail=conference_detail,paper_title=paper_title).exclude(status="DELETE").values_list('author',flat=True))
	if len(qry)>0:
		for q in qry:
			if(q==single_auth or q==first_auth):
				return False
			else:
				return True
		if(author==single_auth):
			return False
	else:
		return True

def ConferencePublishedCategoryCheck(data,mandatory_fields,author):
	category = data['category']
	category1 = GetConferenceCategory()
	for c in category1:
		if c['value']=='PUBLISHED' and c['sno']==category:
			mandatory_fields.extend(['journal_name','volume_no','issue_no','isbn','page_no','author'])
	return mandatory_fields

def GuidanceGuidanceCheck(data,mandatory_fields):
	guidance_for = data['guidance_for']
	guidance = GetGuidance()
	for g in guidance:
		if g['sno']==guidance_for and g['value']=='PROJECT':
			mandatory_fields.extend(['course','no_of_students'])
		elif g['sno']==guidance_for and g['value']=='DEGREE':
			mandatory_fields.extend(['guidance_awarded_status','university_type','university_name','degree'])
		elif g['sno']==guidance_for and g['value']=='RESEARCH (PH. D.)':
			mandatory_fields.extend(['guidance_status','university_type','university_name'])
	return mandatory_fields

def JournalAuthorCheck(data):
	author = data['author']
	journal_name = data['journal_name']
	type_of_journal = data['type_of_journal']
	sub_category = data['sub_category']
	volume_no = data['volume_no']
	issue_no = data['issue_no']
	isbn = data['isbn']
	paper_title = data['paper_title']
	# journal = list(AchFacJournalDetail.objects.filter(journal_name=journal_name,type_of_journal=type_of_journal,sub_category=sub_category,volume_no=volume_no,issue_no=issue_no,isbn=isbn).exclude(status="DELETE").values_list('id',flat=True))
	journal = list(AchFacJournals.objects.filter(paper_title=paper_title).exclude(status="DELETE").values_list('id',flat=True))
	if len(journal)>0:
		journal_details = journal[0]
	else:
		journal_details = None
	author = GetJournalAuthor()
	for a in author:
		if a['value']=='FIRST AUTHOR':
			first_auth = a['sno']
		elif a['value']=='SINGLE AUTHOR':
			single_auth = a['sno']
	qry = list(AchFacJournals.objects.filter(id=journal_details).exclude(status="DELETE").values_list('author',flat=True))
	if len(qry)>0:
		for q in qry:
			# if(q==single_auth or q==first_auth):
			# 	return False
			if q==single_auth:
				return False
			elif q==first_auth and author==first_auth:
				return False
			else:
				True
		if(author==single_auth):
			return False
	else:
		return True

def PatentCollaboratorCheck(data,mandatory_fields):
	if 'company_name' and 'incorporate_status' in data:
		mandatory_fields.extend(['company_name','incorporate_status'])
	return mandatory_fields

def PatentStatusCheck(data,mandatory_fields):
	patent_status = data['patent_status']
	status = GetPatentStatus()
	for s in status:
		if s['sno']==patent_status and s['value']=='FILLED':
			mandatory_fields.append('application_no')
		else:
			mandatory_fields.append('patent_number')
	return mandatory_fields

def SponsorsCollabAssoIdCheck(data,mandatory_fields):
	if 'sponsership' in data:
		sponsership = data['sponsership']
	else:
		sponsership = None
	if 'collaborations' in data:
		collaborations = data['collaborations']
	else:
		collaborations = None
	if 'association' in data:
		association = data['association']
	else:
		association = None
	if sponsership=='Yes' or collaborations=='Yes' or association=='Yes':
		mandatory_fields.extend(['organisation','pin_code','address','contact_person','contact_number','e_mail','website','amount'])
	return mandatory_fields