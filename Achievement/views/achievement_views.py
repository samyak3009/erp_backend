
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse

from django.shortcuts import render
from django.db.models import Q, Sum, F, Value, CharField, Case, When, Value, IntegerField
from django.db.models.functions import Concat
from datetime import date
import json
import datetime
import operator
# from items import QuotesItem

# Create your views here.

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from StudentMMS.constants_functions import requestType
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

from musterroll.models import EmployeePerdetail, Roles
from login.models import EmployeePrimdetail
from Registrar.models import *
from Achievement.models import *

from Achievement.views.achievement_function import *
from Achievement.views.achievement_checks_function import *
from login.views import checkpermission, generate_session_table_name
from Registrar.models import Semtiming
# import validators


def Books(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                role = GetRoleBook()
                role_for = GetBookFor()
                publisher_type = GetPublisherType()
                author = GetLocalAuthor()
                copyright_status = GetCopyrightStatus()
                DOJ = GetDOJ(emp_id)
                Books = GetBooks()
                data = ({'Role': role, 'Role_For': role_for, 'Publisher': publisher_type, 'Author': author, 'Copyright_status': copyright_status, 'DOJ': DOJ, 'Books': Books})
            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacBooks.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'role', 'role__value', 'role_for', 'role_for__value', 'book_title', 'book_edition', 'published_date', 'isbn', 'chapter', 'author', 'author__value', 'copyright_status', 'copyright_status__value', 'copyright_no', 'publisher_details', 'publisher_type', 'publisher_type__value', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website', 'time_stamp').order_by('time_stamp'))
                numbermap = {'PENDING': 1, 'APPROVED': 2, 'REJECTED': 3}
                # order = Case(*[When(approval_status=value, then=pos) for pos, value in enumerate(approval_status)])
                # queryset = AchFacApproval.objects.filter(approval_status__in=approval_status).order_by(order).values("approval_status")
                # print(queryset,'set')
                for d in data:

                    qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='BOOKS', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry) > 0:
                        d['approval_status'] = qry[0]['approval_status']
                    else:
                        d['approval_status'] = None
                # print(sorted(data,key=numbermap.__getitem__('approval_status')))
                # order = Case(*[When(approval_status=d['approval_status'], then=pos) for pos, d in enumerate(data)])
                # queryset = AchFacApproval.objects.filter(approval_status__in=approval_status).order_by(order).values("approval_status")
                # print(queryset,'set')

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            values = BooksFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacBooks.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='BOOKS').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Conference(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                category = GetConferenceCategory()
                type_of_conference = GetConfernenceType()
                activity_type = GetConferenceActivityType()
                sub_category = GetConferenceSubCategory()
                author = GetConferenceAuthor()
                organiser = GetConferenceOrganiser()
                sponsered = [{'sno': 1, 'value': 'Yes'}, {'sno': 2, 'value': 'No'}]
                DOJ = GetDOJ(emp_id)
                if isinstance(DOJ, datetime.date):
                    doj_date = "{}".format(DOJ.year)
                data = {'Category': category, 'Type_of_journal': type_of_conference, 'Sub_category': sub_category, 'Author': author, 'Organized_By':organiser ,'Type_Of_Activity':activity_type, 'Sponsered': sponsered, 'Year': doj_date, 'DOJ': DOJ}
            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacConferences.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category', 'category__value', 'conference_detail', 'conference_detail__conference_title', 'conference_detail__type_of_conference', 'conference_detail__type_of_conference__value', 'conference_detail__conference_from', 'conference_detail__conference_to','conference_detail__other', 'sub_category', 'sub_category__value', 'paper_title', 'published_date', 'journal_name', 'volume_no', 'issue_no', 'isbn', 'page_no', 'author', 'author__value', 'other_description', 'publisher_details', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website','conference_detail__organized_by','conference_detail__type_of_activity__value', 'conference_detail__type_of_activity', 'others', 'time_stamp').order_by('time_stamp'))
                for d in data:
                    data2 = list(AchFacMultiDetails.objects.filter(details_for='RESEARCH PAPER IN CONFERENCE', key_id=d['id']).values_list('detail_text', flat=True))
                    d['sponsered'] = data2
                    if len(data2) > 0:
                        d['is_sponser'] = 1
                    else:
                        d['is_sponser'] = 2
                    qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='RESEARCH PAPER IN CONFERENCE', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry) > 0:
                        d['approval_status'] = qry[0]['approval_status']
                    else:
                        d['approval_status'] = None
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            values = ConferenceFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            print(request)
            data = json.loads(request.body)
            id = data['id']
            AchFacConferences.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH PAPER IN CONFERENCE').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Guidance(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                guidance_for = GetGuidance()
                guidance_status = GetGuidanceStatus()
                course = GetGuidanceCourse()
                degree = GetGuidanceDegree()
                univ_type = GetUnivType()
                guidance_awarded_status = [{'sno': 1, 'value': 'Yes'}, {'sno': 2, 'value': 'No'}]
                DOJ = GetDOJ(emp_id)
                data = {'Guidance_for': guidance_for, 'Guidance_status': guidance_status, 'Course': course, 'Degree': degree, 'University_type': univ_type, 'Guidance_awarded_status': guidance_awarded_status, 'DOJ': DOJ}
            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacGuidances.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'guidance_for', 'guidance_for__value', 'course', 'course__value', 'degree', 'degree__value', 'guidance_awarded_status', 'university_type', 'university_type__value', 'university_name', 'guidance_status', 'guidance_status__value', 'no_of_students', 'project_title', 'area_of_specification', 'date_of_guidance', 'time_stamp').order_by('time_stamp'))
                for d in data:
                    qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='RESEARCH GUIDANCE / PROJECT GUIDANCE', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry) > 0:
                        d['approval_status'] = qry[0]['approval_status']
                    else:
                        d['approval_status'] = None
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            values = GuidanceFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacGuidances.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH GUIDANCE / PROJECT GUIDANCE').update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Journal(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                category = GetJournalCategory()
                type = GetJournalType()
                sub_category = GetJournalSubCategory()
                author = GetJournalAuthor()
                DOJ = GetDOJ(emp_id)
                data = {'Category': category, 'Type_of_journal': type, 'Sub_category': sub_category, 'Author': author, 'DOJ': DOJ}
            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacJournals.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'emp_id__name', 'category', 'category__value', 'author', 'author__value', 'published_date', 'paper_title', 'impact_factor', 'page_no', 'journal_details', 'journal_details__journal_name', 'journal_details__type_of_journal', 'journal_details__type_of_journal__value', 'journal_details__sub_category', 'journal_details__sub_category__value', 'journal_details__volume_no', 'journal_details__issue_no', 'journal_details__isbn', 'publisher_details', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website', 'others', 'time_stamp').order_by('time_stamp'))
                for d in data:
                    qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='RESEARCH PAPER IN JOURNAL', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry) > 0:
                        d['approval_status'] = qry[0]['approval_status']
                    else:
                        d['approval_status'] = None
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            print(data)
            values = JournalFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacJournals.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH PAPER IN JOURNAL').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Patent(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                emp_name = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values_list('name', flat=True))
                emp = {'emp_id': emp_id, 'emp_name': emp_name[0]}
                incorporate_status = GetPatentIncorporateStatus()
                owner = GetPatentOwner()
                collaborations = [{'sno': 1, 'value': 'Yes'}, {'sno': 2, 'value': 'No'}]
                level = GetPatentLevel()
                status = GetPatentStatus()
                dept = GetDiscipline()
                DOJ = GetDOJ(emp_id)
                data = {'Emp': emp, 'Incorporate_status': incorporate_status, 'Owner': owner, 'Collaborations': collaborations, 'Level': level, 'Status': status, 'Department': dept, 'DOJ': DOJ}
            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacPatents.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'patent_details', 'patent_details__patent_title', 'patent_details__patent_description', 'patent_details__level', 'patent_details__level__value', 'patent_details__patent_status', 'patent_details__patent_status__value', 'patent_details__patent_number', 'patent_details__application_no', 'patent_details__owner', 'patent_details__owner__value', 'patent_date', 'time_stamp','patent_details__patent_applicant_name','patent_details__patent_applicant_name_other','patent_details__patent_co_applicant_name','patent_details__patent_co_applicant_name_other').order_by('time_stamp'))
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
                    qry3 = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='PATENT', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry3) > 0:
                        d['approval_status'] = qry3[0]['approval_status']
                    else:
                        d['approval_status'] = None
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            print(data)
            values = PatentFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacPatents.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='PATENT').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def LecturesTalks(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                category = GetLecTalksCategory()
                type = GetLecTalksType()
                org_sector = GetLecTalksOrgSec()
                incorp_sector = GetLecTalksIncorpSec()
                role = GetLecTalksRole()
                DOJ = GetDOJ(emp_id)
                data = {'Category': category, 'Type': type, 'Organisation_sector': org_sector, 'Incorporation_sector': incorp_sector, 'Role': role, 'DOJ': DOJ}
            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacLecturesTalks.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category', 'category__value', 'type_of_event', 'type_of_event__value', 'organization_sector', 'organization_sector__value', 'incorporation_status', 'incorporation_status__value', 'role', 'role__value', 'venue_detail', 'venue_detail__venue', 'venue_detail__address', 'venue_detail__pin_code', 'venue_detail__contact_number', 'venue_detail__e_mail', 'venue_detail__website', 'date', 'topic', 'participants', 'time_stamp').order_by('time_stamp'))
                for d in data:
                    qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='LECTURES AND TALKS', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry) > 0:
                        d['approval_status'] = qry[0]['approval_status']
                    else:
                        d['approval_status'] = None
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            values = LecturesTalksFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacLecturesTalks.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='LECTURES AND TALKS').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def TrainingDevelopment(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                category = GetTrainingDevopCategory()
                training_type = GetTrainingDevopType()
                training_sub_type=GetTrainingDevopSubType()
                role = GetTrainingDevopRole()
                organization_sector = GetTrainingDevopOrgSec()
                incorporation_type = GetTrainingDevopIncorpType()
                venue = GetTrainingDevopVenue()
                dept = GetDiscipline()
                sponsership = [{'sno': 1, 'value': 'Yes'}, {'sno': 2, 'value': 'No'}]
                DOJ = GetDOJ(emp_id)
                data = {'Category': category, 'Training_type': training_type,'Training_sub_type':training_sub_type,'Role': role, 'Organisation_sector': organization_sector, 'Incorporation_type': incorporation_type, 'Venue': venue, 'Department': dept, 'sponsership': sponsership, 'DOJ': DOJ}
            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacTrainings.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category', 'category__value', 'training_type', 'training_type__value', 'training_sub_type', 'training_sub_type__value','role', 'role__value', 'organization_sector', 'organization_sector__value', 'incorporation_type', 'incorporation_type__value', 'from_date', 'to_date', 'title', 'venue', 'venue__value', 'venue_other', 'other', 'participants', 'organizers', 'attended', 'collaborations', 'sponsership', 'time_stamp').order_by('time_stamp'))
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
                    qry3 = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='TRAINING AND DEVELOPMENT PROGRAM', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry3) > 0:
                        d['approval_status'] = qry3[0]['approval_status']
                    else:
                        d['approval_status'] = None
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            values = TrainingDevelopmentFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacTrainings.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='TRAINING AND DEVELOPMENT PROGRAM').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return funownerctions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def ProjectsConsultancy(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                type = GetProjectType()
                status = GetProjectStatus()
                sector = GetProjectSector()
                dept = GetDiscipline()
                sponsers = [{'sno': 1, 'value': 'Yes'}, {'sno': 2, 'value': 'No'}]
                DOJ = GetDOJ(emp_id)
                data = {'Type': type, 'Status': status, 'Sector': sector, 'Department': dept, 'Sponsers': sponsers, 'DOJ': DOJ}
            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacProjects.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'project_type', 'project_type__value', 'project_status', 'project_status__value', 'sector', 'sector__value', 'project_title', 'project_description', 'start_date', 'end_date', 'principal_investigator', 'co_principal_investigator', 'principal_investigator_other', 'co_principal_investigator_other', 'team_size', 'sponsored', 'association', 'time_stamp').order_by('time_stamp'))
                for d in data:
                    qry1 = list(AchFacMapIds.objects.filter(form_id=d['id'], form_type='PROJECTS/CONSULTANCY').exclude(status="DELETE").values('key_id', 'key_type'))
                    sponser_id = []
                    asso_id = []
                    for q in qry1:
                        if q['key_type'] == 'SPONSORS':
                            sponser_id.append(q['key_id'])
                        elif q['key_type'] == 'ASSOCIATIONS':
                            asso_id.append(q['key_id'])
                    query1 = list(AchFacSponser.objects.filter(id__in=sponser_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
                    d['sponsers'] = query1
                    query2 = list(AchFacAssociations.objects.filter(id__in=asso_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
                    d['associators'] = query2
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
                    qry3 = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='PROJECTS/CONSULTANCY', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry3) > 0:
                        d['approval_status'] = qry3[0]['approval_status']
                    else:
                        d['approval_status'] = None
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            values = ProjectsConsultancyFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacProjects.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='PROJECTS/CONSULTANCY').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

def Design(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                emp_name = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values_list('name', flat=True))
                emp = {'emp_id': emp_id, 'emp_name': emp_name[0]}
                dept=GetDiscipline()
                collaborations = [{'sno': 1, 'value': 'Yes'}, {'sno': 2, 'value': 'No'}]
                incorporate_status = GetDesignIncorporateStatus()
                level = GetDesignLevel()
                status = GetDesignStatus()
                owner = GetDesignOwner()
                DOJ = GetDOJ(emp_id)
                data = {'Emp': emp, 'Incorporate_status': incorporate_status, 'Owner': owner, 'Collaborations': collaborations, 'Level': level, 'Status': status, 'Department': dept, 'DOJ': DOJ}

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacDesign.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value','design_title','design_description','design_company_name','design_applicant_name','design_co_applicant_name','design_incorporate_status','design_level','design_status','design_application_no','design_owner','design_date','design_applicant_name_other','design_co_applicant_name_other').order_by('time_stamp'))
                for d in data:
                    qry = list(AchFacApproval.objects.filter(approval_id=d['id'], approval_category='DESIGN', level=1).exclude(status="DELETE").values('approval_status'))
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

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            values = DesignFunction(data, emp_id)
            return functions.RESPONSE(values['data'], values['status'])

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacDesign.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            AchFacApproval.objects.filter(approval_id=id, approval_category='DESIGN').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Activity(request):
    data = []
    emp_id = request.session['hash1']
    session = request.session['Session_id']
    if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                print('fff')
                level = GetActivityLevel()
                act_type = GetActivityType()
                organisation = GetOrganization()
                dept = GetDiscipline()
                emp_category = GetEmpCategory()
                # employee = GetEmployee()
                data = {'Level': level, 'Type': act_type, 'Organisation':organisation, 'Department': dept, 'Emp_category': emp_category}

            elif(requestType.custom_request_type(request.GET, 'get_dept_emp')):
                dept_id = request.GET['dept_id'].split(',')
                emp_category = request.GET['emp_category'].split(',')
                employee = GetEmployee(dept_id,emp_category)
                data = {'Employee': employee}

            elif(requestType.custom_request_type(request.GET, 'get_subcategory')):
                type_id = request.GET['type_id']
                sub_category = GetActivitySubCategory(type_id)
                data = {'Sub_Category': sub_category}

            elif(requestType.custom_request_type(request.GET, 'get_dates')):
                qry = list(Semtiming.objects.filter(uid=session).values('sem_start','sem_end'))
                data = {'data':qry}

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(AchFacActivity.objects.exclude(status="DELETE").values('id','act_level','act_level__value','act_type','act_type__value','act_sub_type','act_sub_type__value','act_start_date','act_end_date','act_description','coord_detail','coord_detail__act_main_org','coord_detail__act_main_dept','coord_detail__act_main_category','coord_detail__act_main_emp_id','coord_detail__act_co_org','coord_detail__act_co_dept','coord_detail__act_co_category','coord_detail__act_co_emp_id','status','time_stamp','act_added_by','act_added_by__name').order_by('time_stamp')[::-1])

                for i in data:
                    if i['coord_detail__act_main_dept'] is not None:
                        qry1 = list(EmployeeDropdown.objects.filter(sno__in=i['coord_detail__act_main_dept']).values_list('value',flat=True))
                        i['main_dept']=qry1

                    if i['coord_detail__act_main_category'] is not None:
                        qry2 = list(EmployeeDropdown.objects.filter(sno__in=i['coord_detail__act_main_category']).values_list('value',flat=True))
                        i['main_category']=qry2
                    
                    if i['coord_detail__act_main_emp_id'] is not None:
                        qry3 = list(EmployeePrimdetail.objects.filter(emp_id__in=i['coord_detail__act_main_emp_id']).annotate(Name=Concat('name', Value(' '), 'emp_id')).values_list('Name',flat=True))
                        i['main_employee']=qry3

                    if i['coord_detail__act_co_dept'] is not None:
                        qry4 = list(EmployeeDropdown.objects.filter(sno__in=i['coord_detail__act_co_dept']).values_list('value',flat=True))
                        i['co_dept']=qry4

                    if i['coord_detail__act_co_category'] is not None:
                        qry5 = list(EmployeeDropdown.objects.filter(sno__in=i['coord_detail__act_co_category']).values_list('value',flat=True))
                        i['co_category']=qry5

                    if i['coord_detail__act_co_emp_id'] is not None:
                        qry6 = list(EmployeePrimdetail.objects.filter(emp_id__in=i['coord_detail__act_co_emp_id']).annotate(Name=Concat('name', Value(' '), 'emp_id')).values_list('Name',flat=True))
                        i['co_employee']=qry6

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            print(data)
            level = data['level']
            Type = data['type']
            sub_type = data['sub_cat']
            start = data['s_date']
            end = data ['e_date']

            co_org_obj = None
            co_dept = None
            co_catg = None
            co_emp = None

            main_org = data['main_org']
            main_dept = data['main_dept']
            main_catg = data['main_catg']
            main_emp = data['main_emp']
            if 'co_org' in data and data['co_org'] is not None :
                co_org = data['co_org']
                co_org_obj=EmployeeDropdown.objects.get(sno=co_org)
            if 'co_org' in data and data['co_dept'] is not None:
                co_dept = data['co_dept']
            if 'co_org' in data and data['co_catg'] is not None:
                co_catg = data['co_catg']
            if 'co_org' in data and data['co_emp'] is not None:
                co_emp = data['co_emp']

            if 'desc' in data:
                desc = data['desc']
            else:
                desc = None

            if 'id' not in data:
                detail_qry=AchFacActivityDetails.objects.create(act_main_org=EmployeeDropdown.objects.get(sno=main_org),act_main_dept=main_dept,act_main_category=main_catg,act_main_emp_id=main_emp,act_co_org=co_org_obj,act_co_dept=co_dept,act_co_category=co_catg,act_co_emp_id=co_emp)
                qry=AchFacActivity.objects.create(act_level=AarDropdown.objects.get(sno=level),act_type=AarDropdown.objects.get(sno=Type),act_sub_type=AarDropdown.objects.get(sno=sub_type),act_start_date=start,act_end_date=end,act_description=desc,act_added_by=EmployeePrimdetail.objects.get(emp_id=emp_id),coord_detail=AchFacActivityDetails.objects.get(id=detail_qry.id))
                
                data = statusMessages.MESSAGE_INSERT
                
            else:
                qry1=AchFacActivity.objects.filter(id=data['id']).update(
                    act_level=AarDropdown.objects.get(sno=level),
                    act_type=AarDropdown.objects.get(sno=Type),
                    act_sub_type=AarDropdown.objects.get(sno=sub_type),
                    act_start_date=start,
                    act_end_date=end,
                    act_description=desc,
                    status="UPDATE",
                    act_added_by=EmployeePrimdetail.objects.get(emp_id=emp_id)
                    )
                qrr2= AchFacActivityDetails.objects.filter(id=data['coord_detail']).update(act_main_org=EmployeeDropdown.objects.get(sno=main_org),
                    act_main_dept=main_dept,
                    act_main_category=main_catg,
                    act_main_emp_id=main_emp,
                    act_co_org=co_org_obj,
                    act_co_dept=co_dept,
                    act_co_category=co_catg,
                    act_co_emp_id=co_emp,) 

                data = statusMessages.MESSAGE_UPDATE
            
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            AchFacActivity.objects.filter(id=id).exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

def AchApproval(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            dept = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values_list('dept', flat=True))

            if(requestType.custom_request_type(request.GET, 'form_data')):
                forms = GetForms()
                data = {'Forms': forms}
            elif(requestType.custom_request_type(request.GET, 'pending_requests')):
                sno = int(request.GET['sno'])
                category = request.GET['category']
                qry = list(AchFacApproval.objects.filter(approval_category=category, approval_status='PENDING', level=1).exclude(status="DELETE").values_list('approval_id', flat=True))
                if sno == 1:
                    # BOOKS
                    data = list(AchFacBooks.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'role__value', 'role_for__value', 'book_title', 'book_edition', 'published_date', 'isbn', 'chapter', 'author__value', 'copyright_status__value', 'copyright_no', 'publisher_type__value', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website').distinct())
                    for d in data:
                        approval_table_id = GetApprovalRequests('BOOKS', d['id'])
                        d['approval_table_id'] = approval_table_id[0]
                elif sno == 2:
                    # RESEARCH PAPER IN CONFERENCE
                    data = list(AchFacConferences.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category__value', 'conference_detail__conference_title', 'conference_detail__type_of_conference__value', 'conference_detail__conference_from', 'conference_detail__conference_to', 'conference_detail__organized_by', 'sub_category__value', 'paper_title', 'published_date', 'journal_name', 'volume_no', 'issue_no', 'isbn', 'page_no', 'author__value', 'other_description', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website').distinct())
                    for d in data:
                        data2 = list(AchFacMultiDetails.objects.filter(details_for='CONFERENCE', key_id=d['id']).values_list('detail_text', flat=True))
                        d['sponsered'] = data2
                        if len(data2) > 0:
                            d['is_sponser'] = 1
                        else:
                            d['is_sponser'] = 2
                        approval_table_id = GetApprovalRequests('RESEARCH PAPER IN CONFERENCE', d['id'])
                        d['approval_table_id'] = approval_table_id[0]
                elif sno == 3:
                    # RESEARCH GUIDANCE / PROJECT GUIDANCE
                    data = list(AchFacGuidances.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'guidance_for__value', 'course__value', 'degree__value', 'guidance_awarded_status', 'university_type__value', 'university_name', 'guidance_status__value', 'no_of_students', 'project_title', 'area_of_specification', 'date_of_guidance').distinct())
                    for d in data:
                        approval_table_id = GetApprovalRequests('RESEARCH GUIDANCE / PROJECT GUIDANCE', d['id'])
                        d['approval_table_id'] = approval_table_id[0]
                elif sno == 4:
                    # RESEARCH PAPER IN JOURNAL
                    data = list(AchFacJournals.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category__value', 'author__value', 'published_date', 'paper_title', 'impact_factor', 'page_no', 'journal_details__journal_name', 'journal_details__type_of_journal__value', 'journal_details__sub_category__value', 'journal_details__volume_no', 'journal_details__issue_no', 'journal_details__isbn', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website', 'others').distinct())
                    for d in data:
                        approval_table_id = GetApprovalRequests('RESEARCH PAPER IN JOURNAL', d['id'])
                        d['approval_table_id'] = approval_table_id[0]
                elif sno == 5:
                    # PATENT
                    data = list(AchFacPatents.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'patent_details__patent_title', 'patent_details__patent_description', 'patent_details__level__value', 'patent_details__patent_status__value', 'patent_details__patent_number', 'patent_details__application_no', 'patent_details__owner__value', 'patent_date','patent_details__patent_applicant_name','patent_details__patent_applicant_name_other','patent_details__patent_co_applicant_name','patent_details__patent_co_applicant_name_other').distinct())
                    for d in data:
                        qry = list(AchFacPatentCollaborator.objects.filter(patent_in=d['id'], patent_in__emp_id__dept=dept[0]).exclude(status="DELETE").values('company_name', 'incorporate_status__value'))
                        if len(qry) > 0:
                            d['company_name'] = qry[0]['company_name']
                            d['incorporate_status__value'] = qry[0]['incorporate_status__value']
                        else:
                            d['company_name'] = None
                            d['incorporate_status__value'] = None
                        qry2 = list(AchFacMultiDetails.objects.filter(details_for="PATENT", key_id=d['id']).values('details_for', 'key_id', 'detail_emp__value'))
                        if len(qry2) > 0:
                            discipline_value = []
                            for q in qry2:
                                discipline_value.append(q['detail_emp__value'])
                            d['detail_emp__value'] = discipline_value
                        else:
                            d['detail_emp__value'] = None
                        approval_table_id = GetApprovalRequests('PATENT', d['id'])
                        d['approval_table_id'] = approval_table_id[0]
                elif sno == 6:
                    # LECTURES AND TALKS
                    data = list(AchFacLecturesTalks.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category__value', 'type_of_event__value', 'organization_sector__value', 'incorporation_status__value', 'role__value', 'venue_detail__venue', 'venue_detail__address', 'venue_detail__pin_code', 'venue_detail__contact_number', 'venue_detail__e_mail', 'venue_detail__website', 'date', 'topic', 'participants'))
                    for d in data:
                        approval_table_id = GetApprovalRequests('LECTURES AND TALKS', d['id'])
                        d['approval_table_id'] = approval_table_id[0]
                elif sno == 7:
                    # TRAINING AND DEVELOPMENT PROGRAM
                    data = list(AchFacTrainings.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category__value', 'training_type__value', 'role__value', 'organization_sector__value', 'incorporation_type__value', 'from_date', 'to_date', 'title', 'venue__value', 'venue_other', 'other', 'participants', 'organizers', 'attended', 'collaborations', 'sponsership').distinct())
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
                        qry2 = list(AchFacMultiDetails.objects.filter(details_for='TRAINING AND DEVELOPMENT PROGRAM', key_id=d['id']).values('detail_emp__value'))
                        if len(qry2) > 0:
                            discipline_value = []
                            for q in qry2:
                                discipline_value.append(q['detail_emp__value'])
                            d['detail_emp__value'] = discipline_value
                        else:
                            d['detail_emp__value'] = None
                        approval_table_id = GetApprovalRequests('TRAINING AND DEVELOPMENT PROGRAM', d['id'])
                        d['approval_table_id'] = approval_table_id[0]
                elif sno == 8:
                    # PROJECTS/CONSULTANCY
                    data = list(AchFacProjects.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'project_type__value', 'project_status__value', 'sector__value', 'project_title', 'project_description', 'start_date', 'end_date', 'principal_investigator', 'co_principal_investigator', 'principal_investigator_other', 'co_principal_investigator_other', 'team_size', 'sponsored', 'association').distinct())
                    for d in data:
                        qry1 = list(AchFacMapIds.objects.filter(form_id=d['id'], form_type='PROJECTS/CONSULTANCY').exclude(status="DELETE").values('key_id', 'key_type'))
                        sponser_id = []
                        asso_id = []
                        for q in qry1:
                            if q['key_type'] == 'SPONSORS':
                                sponser_id.append(q['key_id'])
                            elif q['key_type'] == 'ASSOCIATIONS':
                                asso_id.append(q['key_id'])
                        query1 = list(AchFacSponser.objects.filter(id__in=sponser_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
                        d['sponsers'] = query1
                        query2 = list(AchFacAssociations.objects.filter(id__in=asso_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
                        d['associators'] = query2
                        qry2 = list(AchFacMultiDetails.objects.filter(details_for='PROJECTS/CONSULTANCY', key_id=d['id']).values('detail_emp', 'detail_emp__value'))
                        if len(qry2) > 0:
                            discipline_value = []
                            for q in qry2:
                                discipline_value.append(q['detail_emp__value'])
                            d['detail_emp__value'] = discipline_value
                        else:
                            d['detail_emp__value'] = None
                        approval_table_id = GetApprovalRequests('PROJECTS/CONSULTANCY', d['id'])
                        d['approval_table_id'] = approval_table_id[0]

                elif sno == 9:
                    # DESIGN
                    data = list(AchFacDesign.objects.filter(id__in=qry, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value','design_title','design_description','design_company_name','design_applicant_name','design_co_applicant_name','design_incorporate_status','design_level','design_status','design_application_no','design_owner','design_date').distinct())
                    for d in data:
                        qry2= list(AchFacMultiDetails.objects.filter(details_for='DESIGN', key_id=d['id']).values('detail_emp', 'detail_emp__value'))
                        if len(qry2) > 0:
                            discipline_value = []
                            for q in qry2:
                                discipline_value.append(q['detail_emp__value'])
                            d['detail_emp__value'] = discipline_value
                        else:
                            d['detail_emp__value'] = None

                        approval_table_id = GetApprovalRequests('DESIGN', d['id'])
                        d['approval_table_id'] = approval_table_id[0]

            elif(requestType.custom_request_type(request.GET, 'approve_or_reject')):
                approval_status = request.GET['approval_status']
                approval_table_id = request.GET['approval_table_id'].split(',')
                qry = list(AchFacApproval.objects.filter(id__in=approval_table_id, level=1, approval_status="PENDING").exclude(status="DELETE").values('approval_category', 'approval_id'))
                AchFacApproval.objects.filter(id__in=approval_table_id).exclude(status="DELETE").update(status="DELETE")
                for q in qry:
                    AchFacApproval.objects.create(approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id), level=1, approval_category=q['approval_category'], approval_id=q['approval_id'], approval_status=approval_status)
                data = statusMessages.CUSTOM_MESSAGE('Successfully ' + approval_status)

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                sno = int(request.GET['sno'])
                Forms = GetForms()
                for f in Forms:
                    if f['sno'] == sno:
                        category = f['value']
                data_id = list(AchFacApproval.objects.filter(level=1, approval_category=category).exclude(approval_status='PENDING').exclude(status="DELETE").values_list('approval_id', flat=True))
                if len(data_id) > 0:
                    data_id = data_id
                else:
                    data_id = []
                if sno == 1:
                    # BOOKS
                    category = 'BOOKS'
                    data = list(AchFacBooks.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'role__value', 'role_for__value', 'book_title', 'book_edition', 'published_date', 'isbn', 'chapter', 'author__value', 'copyright_status__value', 'copyright_no', 'publisher_type__value', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website').distinct())
                    for d in data:
                        d['approval_status'] = GetApprovalStatus(d, category)
                elif sno == 2:
                    # RESEARCH PAPER IN CONFERENCE
                    category = 'RESEARCH PAPER IN CONFERENCE'
                    data = list(AchFacConferences.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category__value', 'conference_detail__conference_title', 'conference_detail__type_of_conference__value', 'conference_detail__conference_from', 'conference_detail__conference_to', 'conference_detail__organized_by', 'sub_category__value', 'paper_title', 'published_date', 'journal_name', 'volume_no', 'issue_no', 'isbn', 'page_no', 'author__value', 'other_description', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website').distinct())
                    for d in data:
                        qry = list(AchFacMultiDetails.objects.filter(details_for='RESEARCH PAPER IN CONFERENCE', key_id=d['id']).values_list('detail_text', flat=True))
                        d['sponsered'] = qry
                        d['approval_status'] = GetApprovalStatus(d, category)
                elif sno == 3:
                    # RESEARCH GUIDANCE / PROJECT GUIDANCE
                    category = 'RESEARCH GUIDANCE / PROJECT GUIDANCE'
                    data = list(AchFacGuidances.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'guidance_for__value', 'course__value', 'degree__value', 'guidance_awarded_status', 'university_type__value', 'university_name', 'guidance_status__value', 'no_of_students', 'project_title', 'area_of_specification', 'date_of_guidance').distinct())
                    for d in data:
                        d['approval_status'] = GetApprovalStatus(d, category)
                elif sno == 4:
                    # RESEARCH PAPER IN JOURNAL
                    category = 'RESEARCH PAPER IN JOURNAL'
                    data = list(AchFacJournals.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category__value', 'author__value', 'published_date', 'paper_title', 'impact_factor', 'page_no', 'journal_details__journal_name', 'journal_details__type_of_journal__value', 'journal_details__sub_category__value', 'journal_details__volume_no', 'journal_details__issue_no', 'journal_details__isbn', 'publisher_details__publisher_name', 'publisher_details__publisher_address_1', 'publisher_details__publisher_address_2', 'publisher_details__publisher_zip_code', 'publisher_details__publisher_contact', 'publisher_details__publisher_email', 'publisher_details__publisher_website', 'others').distinct())
                    for d in data:
                        d['approval_status'] = GetApprovalStatus(d, category)
                elif sno == 5:
                    # PATENT
                    category = 'PATENT'
                    data = list(AchFacPatents.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'patent_details__patent_title', 'patent_details__patent_description', 'patent_details__level__value', 'patent_details__patent_status__value', 'patent_details__patent_number', 'patent_details__application_no', 'patent_details__owner__value', 'patent_date','patent_details__patent_applicant_name','patent_details__patent_applicant_name_other','patent_details__patent_co_applicant_name','patent_details__patent_co_applicant_name_other').distinct())
                    for d in data:
                        qry = list(AchFacPatentCollaborator.objects.filter(patent_in=d['id']).exclude(status="DELETE").values('company_name', 'incorporate_status__value'))
                        if len(qry) > 0:
                            d['company_name'] = qry[0]['company_name']
                            d['incorporate_status__value'] = qry[0]['incorporate_status__value']
                        else:
                            d['company_name'] = None
                            d['incorporate_status__value'] = None
                        qry2 = list(AchFacMultiDetails.objects.filter(details_for="PATENT", key_id=d['id']).values('details_for', 'key_id', 'detail_emp__value'))
                        if len(qry2) > 0:
                            discipline_value = []
                            for q in qry2:
                                discipline_value.append(q['detail_emp__value'])
                            d['detail_emp__value'] = discipline_value
                        else:
                            d['detail_emp__value'] = None
                        d['approval_status'] = GetApprovalStatus(d, category)
                elif sno == 6:
                    # LECTURES AND TALKS
                    category = 'LECTURES AND TALKS'
                    data = list(AchFacLecturesTalks.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category__value', 'type_of_event__value', 'organization_sector__value', 'incorporation_status__value', 'role__value', 'venue_detail__venue', 'venue_detail__address', 'venue_detail__pin_code', 'venue_detail__contact_number', 'venue_detail__e_mail', 'venue_detail__website', 'date', 'topic', 'participants').distinct())
                    for d in data:
                        d['approval_status'] = GetApprovalStatus(d, category)
                elif sno == 7:
                    # TRAINING AND DEVELOPMENT PROGRAM
                    category = 'TRAINING AND DEVELOPMENT PROGRAM'
                    data = list(AchFacTrainings.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'category__value', 'training_type__value', 'role__value', 'organization_sector__value', 'incorporation_type__value', 'from_date', 'to_date', 'title', 'venue__value', 'venue_other', 'participants', 'organizers', 'attended', 'collaborations', 'sponsership').distinct())
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
                        qry2 = list(AchFacMultiDetails.objects.filter(details_for='TRAINING AND DEVELOPMENT PROGRAM', key_id=d['id']).values('detail_emp__value'))
                        if len(qry2) > 0:
                            discipline_value = []
                            for q in qry2:
                                discipline_value.append(q['detail_emp__value'])
                            d['detail_emp__value'] = discipline_value
                        else:
                            d['detail_emp__value'] = None
                        d['approval_status'] = GetApprovalStatus(d, category)
                elif sno == 8:
                    # PROJECTS/CONSULTANCY
                    category = 'PROJECTS/CONSULTANCY'
                    data = list(AchFacProjects.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'project_type__value', 'project_status__value', 'sector__value', 'project_title', 'project_description', 'start_date', 'end_date', 'principal_investigator', 'co_principal_investigator', 'principal_investigator_other', 'co_principal_investigator_other', 'team_size', 'sponsored', 'association').distinct())
                    for d in data:
                        qry1 = list(AchFacMapIds.objects.filter(form_id=d['id'], form_type='PROJECTS/CONSULTANCY').exclude(status="DELETE").values('key_id', 'key_type'))
                        sponser_id = []
                        asso_id = []
                        for q in qry1:
                            if q['key_type'] == 'SPONSORS':
                                sponser_id.append(q['key_id'])
                            elif q['key_type'] == 'ASSOCIATIONS':
                                asso_id.append(q['key_id'])
                        query1 = list(AchFacSponser.objects.filter(id__in=sponser_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
                        d['sponsers'] = query1
                        query2 = list(AchFacAssociations.objects.filter(id__in=asso_id).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
                        d['associators'] = query2
                        qry2 = list(AchFacMultiDetails.objects.filter(details_for='PROJECTS/CONSULTANCY', key_id=d['id']).values('detail_emp', 'detail_emp__value'))
                        if len(qry2) > 0:
                            discipline_value = []
                            for q in qry2:
                                discipline_value.append(q['detail_emp__value'])
                            d['detail_emp__value'] = discipline_value
                        else:
                            d['detail_emp__value'] = None
                        d['approval_status'] = GetApprovalStatus(d, category)

                elif sno == 9:
                    # DESIGN
                    category = 'DESIGN'
                    data = list(AchFacDesign.objects.filter(id__in=data_id, emp_id__dept=dept[0]).exclude(status="DELETE").values('id', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value','design_title','design_description','design_company_name','design_applicant_name','design_co_applicant_name','design_incorporate_status','design_level','design_status','design_application_no','design_owner','design_date').distinct())
                    for d in data:
                        qry2 = list(AchFacMultiDetails.objects.filter(details_for='DESIGN', key_id=d['id']).values('detail_emp', 'detail_emp__value'))
                        if len(qry2) > 0:
                            discipline_value = []
                            for q in qry2:
                                discipline_value.append(q['detail_emp__value'])
                            d['detail_emp__value'] = discipline_value
                        else:
                            d['detail_emp__value'] = None

                        d['approval_status'] = GetApprovalStatus(d, category)
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            approval_status = data['approval_status']
            approval_table_id = data['approval_table_id']  # ids in array ###########
            qry = list(AchFacApproval.objects.filter(id__in=approval_table_id, level=1, approval_status="PENDING").exclude(status="DELETE").values('approval_category', 'approval_id'))
            AchFacApproval.objects.filter(id__in=approval_table_id).exclude(status="DELETE").update(status="DELETE")
            for q in qry:
                AchFacApproval.objects.create(approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id), level=1, approval_category=q['approval_category'], approval_id=q['approval_id'], approval_status=approval_status)
            data = statusMessages.CUSTOM_MESSAGE('Successfully ' + approval_status)
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def BooksFunction(data, emp_id):
    id = data['id']  # for insert id is none ##########################
    role = data['role']
    role_for = data['role_for']
    book_title = data['book_title']
    book_edition = data['book_edition']
    published_date = datetime.datetime.strptime(data['published_date'].split('T')[0], '%Y-%m-%d').date()
    isbn = data['isbn']
    author = data['author']
    copyright_status = data['copyright_status']
    copyright_no = data['copyright_no']
    publisher_type = data['publisher_type']
    ############### PUBLISHER DETAILS ##############
    publisher_name = data['publisher_name']
    publisher_address_1 = data['publisher_address_1']
    publisher_address_2 = data['publisher_address_2']
    publisher_zip_code = data['publisher_zip_code']
    publisher_contact = data['publisher_contact']
    publisher_email = data['publisher_email']
    publisher_website = data['publisher_website']
    ################################################
    ############## FOR UPDATE ######################
    if id != None:
        AchFacBooks.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='BOOKS').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT

    ################################################
    ######### FORMAT CHANGE FOR USE ################
    data1 = {}
    for k, v in data.items():
        data1[k] = v
    ################################################
    mandatory_fields = ['role', 'role_for', 'book_title', 'book_edition', 'published_date', 'isbn', 'author', 'copyright_status', 'publisher_type', 'publisher_name', 'publisher_address_1', 'publisher_zip_code', 'publisher_contact', 'publisher_email', 'publisher_website']
    if 'chapter' in data:
        chapter = data['chapter']
        mandatory_fields.append('chapter')
    else:
        chapter = None
    ############## FOR MANDATORY FIELDS AND CHECKS ############
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    author_check = BookFormAuthorCheck(chapter, book_title, author)
    if author_check == False:
        data_values = statusMessages.CUSTOM_MESSAGE('INVALID AUTHOR')
        return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ################################################
    qry = GetPublisherIdCheck(data1)
    if len(qry) == 0:
        AchFacPublishers.objects.create(publisher_name=publisher_name, publisher_address_1=publisher_address_1, publisher_address_2=publisher_address_2, publisher_zip_code=publisher_zip_code, publisher_contact=publisher_contact, publisher_email=publisher_email, publisher_website=publisher_website)
        pub_id = GetPublisherIdCheck(data1)
    else:
        pub_id = qry
    AchFacBooks.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), role=AarDropdown.objects.get(sno=role), role_for=AarDropdown.objects.get(sno=role_for), book_title=book_title, book_edition=book_edition, published_date=published_date, isbn=isbn, chapter=chapter, author=AarDropdown.objects.get(sno=author), copyright_status=AarDropdown.objects.get(sno=copyright_status), copyright_no=copyright_no, publisher_type=AarDropdown.objects.get(sno=publisher_type), publisher_details=AchFacPublishers.objects.get(id=pub_id[0]))
    books_id = list(AchFacBooks.objects.filter(emp_id=emp_id, role=role, role_for=role_for, book_title=book_title, book_edition=book_edition, published_date=published_date, isbn=isbn, chapter=chapter, author=author, copyright_status=copyright_status, copyright_no=copyright_no, publisher_type=publisher_type, publisher_details=pub_id[0]).exclude(status="DELETE").values_list('id', flat=True))
    approval = RequestForApproval('BOOKS', books_id[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}


def ConferenceFunction(data, emp_id):
    id = data['id']  # for insert id is none #######################
    category = data['category']
    sub_category = data['sub_category']
    paper_title = data['paper_title']
    published_date = data['published_date']
    other_description = data['other_description']
    #################### CONFERENCE DETAILS #####################
    conference_title = data['conference_title']
    type_of_conference = data['type_of_conference']
    conference_from = datetime.datetime.strptime(data['conference_from'].split('T')[0], '%Y-%m-%d').date()
    conference_to = datetime.datetime.strptime(data['conference_to'].split('T')[0], '%Y-%m-%d').date()
    organized_by = data['organized_by']
    activity_type = data['activity_type']
    #############################################################
    ################### PUBLISHER DETAILS #######################
    publisher_name = data['publisher_name']
    publisher_address_1 = data['publisher_address_1']
    publisher_address_2 = data['publisher_address_2']
    publisher_zip_code = data['publisher_zip_code']
    publisher_contact = data['publisher_contact']
    publisher_email = data['publisher_email']
    publisher_website = data['publisher_website']
    #############################################################
    ################### SPONSERS DETAILS ########################
    sponsered = data['sponsered']  # [] is no sponsers and [value] if sponsers ######################################
    #############################################################
    if 'journal_name' and 'volume_no' and 'issue_no' and 'isbn' and 'page_no' in data:
        journal_name = data['journal_name']
        volume_no = data['volume_no']
        issue_no = data['issue_no']
        isbn = data['isbn']
        page_no = data['page_no']
    else:
        journal_name = None
        volume_no = None
        issue_no = None
        isbn = None
        page_no = None
    if 'others' in data:  # others if author is others ######################
        others = data['others']
    else:
        others = None
    if 'other' in data:  # other if organised_by is others ######################
        other = data['other']
    else:
        other = None

    if 'author' in data:
        if data['author'] != None:
            author = AarDropdown.objects.get(sno=data['author'])
        else:
            author = None
    else:
        author = None
    ############################################################
    ###################### FOR UPDATE ##########################
    if id != None:
        AchFacConferences.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH PAPER IN CONFERENCE').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT
    ############################################################
    ############## CHANGE FORMAT FOR USE #######################
    data1 = {}
    for k, v in data.items():
        data1[k] = v
    ############################################################
    ############## FOR MANDATORY FIELDS AND CHECKS ############
    mandatory_fields = ['category','activity_type', 'sub_category', 'published_date', 'type_of_conference', 'conference_title', 'conference_from', 'conference_to', 'publisher_name', 'publisher_address_1', 'publisher_zip_code', 'publisher_contact', 'publisher_email', 'publisher_website']
    mandatory_fields = ConferencePublishedCategoryCheck(data1, mandatory_fields, author)
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    category_check = ConferenceCategoryCheck(data1)
    if category_check == True:
        author_check = ConferenceAuthorCheck(data1)
        if author_check == False:
            data_values = statusMessages.CUSTOM_MESSAGE('INVALID AUTHOR')
            return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ################################################

    qry = GetPublisherIdCheck(data1)
    if len(qry) == 0:
        AchFacPublishers.objects.create(publisher_name=publisher_name, publisher_address_1=publisher_address_1, publisher_address_2=publisher_address_2, publisher_zip_code=publisher_zip_code, publisher_contact=publisher_contact, publisher_email=publisher_email, publisher_website=publisher_website)
        pub_id = GetPublisherIdCheck(data1)
    else:
        pub_id = qry
    qry1 = GetConferenceIdCheck(data1)
    if len(qry1) == 0:
        AchFacConferenceDetail.objects.create(conference_title=conference_title,type_of_activity=AarDropdown.objects.get(sno=activity_type), type_of_conference=AarDropdown.objects.get(sno=type_of_conference), conference_from=conference_from, conference_to=conference_to, organized_by=organized_by,other=other)
        conf_id = GetConferenceIdCheck(data1)
    else:
        conf_id = qry1
    AchFacConferences.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), category=AarDropdown.objects.get(sno=category), conference_detail=AchFacConferenceDetail.objects.get(id=conf_id[0]), sub_category=AarDropdown.objects.get(sno=sub_category), paper_title=paper_title, published_date=published_date, journal_name=journal_name, volume_no=volume_no, issue_no=issue_no, isbn=isbn, page_no=page_no, author=author, other_description=other_description, publisher_details=AchFacPublishers.objects.get(id=pub_id[0]), others=others)
    ########## FOR SPONSERED #########
    conference_id = list(AchFacConferences.objects.filter(emp_id=emp_id, category=category, conference_detail=conf_id[0], sub_category=sub_category, paper_title=paper_title, published_date=published_date, journal_name=journal_name, volume_no=volume_no, issue_no=issue_no, isbn=isbn, page_no=page_no, author=author, other_description=other_description, publisher_details=pub_id[0], others=others).exclude(status="DELETE").values_list('id', flat=True))
    objs = (AchFacMultiDetails(details_for='RESEARCH PAPER IN CONFERENCE', key_id=conference_id[0], detail_text=s)for s in sponsered)
    sponser = AchFacMultiDetails.objects.bulk_create(objs)

    approval = RequestForApproval('RESEARCH PAPER IN CONFERENCE', conference_id[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}


def GuidanceFunction(data, emp_id):
    id = data['id']  # s for insert id is none ###################
    guidance_for = data['guidance_for']
    project_title = data['project_title']
    area_of_specification = data['area_of_specialization']
    date_of_guidance = datetime.datetime.strptime(data['date_of_guidance'].split('T')[0], '%Y-%m-%d').date()
    #############################################################
    if 'course' in data:
        course = StudentDropdown.objects.get(sno=data['course'])
    else:
        course = None
    if 'degree' in data:
        degree = StudentDropdown.objects.get(sno=data['degree'])
    else:
        degree = None
    if 'guidance_awarded_status' in data:
        guidance_awarded_status = data['guidance_awarded_status']
    else:
        guidance_awarded_status = None
    if 'university_type' in data:
        university_type = AarDropdown.objects.get(sno=data['university_type'])
    else:
        university_type = None
    if 'university_name' in data:
        university_name = data['university_name']
    else:
        university_name = None
    if 'guidance_status' in data:
        guidance_status = AarDropdown.objects.get(sno=data['guidance_status'])
    else:
        guidance_status = None
    if 'no_of_students' in data:
        no_of_students = data['no_of_students']
    else:
        no_of_students = None
    #############################################################
    ######################### FOR UPDATE ########################
    if id != None:
        AchFacGuidances.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH GUIDANCE / PROJECT GUIDANCE').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT
    #############################################################
    ############## CHANGE FORMAT FOR USE ########################
    data1 = {}
    for k, v in data.items():
        data1[k] = v
    ############################################################
    ############## FOR MANDATORY FIELDS AND CHECKS #############
    mandatory_fields = ['guidance_for', 'date_of_guidance', 'project_title', 'area_of_specification']
    mandatory_fields = GuidanceGuidanceCheck(data1, mandatory_fields)
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ################################################

    AchFacGuidances.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), guidance_for=AarDropdown.objects.get(sno=guidance_for), course=course, degree=degree, guidance_awarded_status=guidance_awarded_status, university_type=university_type, university_name=university_name, guidance_status=guidance_status, no_of_students=no_of_students, project_title=project_title, area_of_specification=area_of_specification, date_of_guidance=date_of_guidance)
    guidance_id = list(AchFacGuidances.objects.filter(emp_id=emp_id, guidance_for=guidance_for, course=course, degree=degree, guidance_awarded_status=guidance_awarded_status, university_type=university_type, university_name=university_name, guidance_status=guidance_status, no_of_students=no_of_students, project_title=project_title, area_of_specification=area_of_specification, date_of_guidance=date_of_guidance).exclude(status="DELETE").values_list('id', flat=True))

    approval = RequestForApproval('RESEARCH GUIDANCE / PROJECT GUIDANCE', guidance_id[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}


def JournalFunction(data, emp_id):
    print(emp_id, 'emp_id')
    id = data['id']  # id is none in case of insert ###########################
    category = data['category']
    author = data['author']
    published_date = datetime.datetime.strptime(data['published_date'].split('T')[0], '%Y-%m-%d').date()
    paper_title = data['paper_title']
    page_no = data['page_no']
    ############ JOURNAL DETAILS ######################
    journal_name = data['journal_name']
    type_of_journal = data['type_of_journal']
    volume_no = data['volume_no']
    issue_no = data['issue_no']
    isbn = data['isbn']
    sub_category = data['sub_category']
    ###################################################
    ############ PUBLISHER DETAILS ####################
    publisher_name = data['publisher_name']
    publisher_address_1 = data['publisher_address_1']
    publisher_address_2 = data['publisher_address_2']
    publisher_zip_code = data['publisher_zip_code']
    publisher_contact = data['publisher_contact']
    publisher_email = data['publisher_email']
    publisher_website = data['publisher_website']
    ###################################################
    if 'others' in data:
        others = data['others']
    else:
        others = None
    if 'impact_factor' in data:
        impact_factor = data['impact_factor']
    else:
        impact_factor = None
    ###################################################
    ############# FOR UPDATE ##########################
    if id != None:
        AchFacJournals.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='RESEARCH PAPER IN JOURNAL').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT
    ###################################################
    ############## CHANGE FORMAT FOR USE ##############
    data1 = {}
    for k, v in data.items():
        data1[k] = v
    ###################################################
    ######## FOR MANDATORY FIELD AND CHECKS ###########
    mandatory_fields = ['category', 'type_of_journal', 'sub_category', 'published_date', 'paper_title', 'journal_name', 'volume_no', 'issue_no', 'isbn', 'page_no', 'publisher_name', 'author', 'publisher_address_1', 'publisher_zip_code', 'publisher_email', 'publisher_contact', 'publisher_website']
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    author_check = JournalAuthorCheck(data1)
    if author_check == False:
        data_values = statusMessages.CUSTOM_MESSAGE('Invalid Author')
        return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ###################################################

    journal_check = GetJournalDetailsCheck(data1)
    if len(journal_check) > 0:
        journal_det_id = journal_check
    else:
        AchFacJournalDetail.objects.create(journal_name=journal_name, type_of_journal=AarDropdown.objects.get(sno=type_of_journal), sub_category=AarDropdown.objects.get(sno=sub_category), volume_no=volume_no, issue_no=issue_no, isbn=isbn)
        journal_det_id = GetJournalDetailsCheck(data1)
    publisher_check = GetPublisherIdCheck(data1)
    if len(publisher_check) > 0:
        pub_id = publisher_check
    else:
        AchFacPublishers.objects.create(publisher_name=publisher_name, publisher_address_1=publisher_address_1, publisher_address_2=publisher_address_2, publisher_zip_code=publisher_zip_code, publisher_contact=publisher_contact, publisher_email=publisher_email, publisher_website=publisher_website)
        pub_id = GetPublisherIdCheck(data1)
    AchFacJournals.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), category=AarDropdown.objects.get(sno=category), author=AarDropdown.objects.get(sno=author), published_date=published_date, paper_title=paper_title, impact_factor=impact_factor, page_no=page_no, journal_details=AchFacJournalDetail.objects.get(id=journal_det_id[0]), publisher_details=AchFacPublishers.objects.get(id=pub_id[0]), others=others)
    journal_id = list(AchFacJournals.objects.filter(emp_id=emp_id, category=category, author=author, published_date=published_date, paper_title=paper_title, impact_factor=impact_factor, page_no=page_no, journal_details=journal_det_id[0], publisher_details=pub_id[0], others=others).exclude(status="DELETE").values_list('id', flat=True))

    approval = RequestForApproval('RESEARCH PAPER IN JOURNAL', journal_id[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}


def PatentFunction(data, emp_id):
    id = data['id']  # for insert id is None ###########################
    emp = data['employee']
    collab = data['collab']
    ################ PATENT DETAILS ############################
    patent_title = data['patent_title']
    patent_description = data['patent_description']
    patent_applicant_name=data['patent_applicant_name']
    patent_co_applicant_name=data['patent_co_applicant_name']
    level = data['level']
    patent_status = data['patent_status']
    patent_date = datetime.datetime.strptime(data['patent_date'].split('T')[0], '%Y-%m-%d').date()
    owner = data['owner']
    ################ DISCIPLINE DETAILS ########################
    detail_emp = data['discipline']
    ############################################################
    ################ COLLABORATERS DETAILS #####################
    if 'company_name' and 'incorporate_status' in data:
        company_name = data['company_name']
        incorporate_status = AarDropdown.objects.get(sno=data['incorporate_status'])
    else:
        company_name = None
        incorporate_status = None
    ############################################################
    if 'patent_number' in data:
        patent_number = data['patent_number']
    else:
        patent_number = None
    if 'application_no' in data:
        application_no = data['application_no']
    else:
        application_no = None

    if 'patent_applicant_name_other' in data:
        patent_applicant_name_other = data['patent_applicant_name_other']
    else:
        patent_applicant_name_other = None

    if 'patent_co_applicant_name_other' in data:
        patent_co_applicant_name_other = data['patent_co_applicant_name_other']
    else:
        patent_co_applicant_name_other = None
    ############################################################
    ############# FOR UPDATE ###################################
    if id != None:
        AchFacPatents.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='PATENT').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT
    ############################################################
    ################ FORMAT CHANGE FOR USE #####################
    data1 = {}
    for k, v in data.items():
        data1[k] = v
    ############################################################
    ############ FOR MANDATORY FIELDS AND CHECKS  ##############
    mandatory_fields = ['level', 'patent_status', 'owner', 'patent_title', 'patent_description', 'patent_date']
    mandatory_fields = PatentCollaboratorCheck(data1, mandatory_fields)
    mandatory_fields = PatentStatusCheck(data1, mandatory_fields)
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ############################################################

    patent_check = GetPatentDetailsIdCheck(data1, patent_number, application_no)
    if len(patent_check) > 0:
        patent_id = patent_check
    else:
        AchFacPatentDetail.objects.create(patent_title=patent_title, patent_description=patent_description, level=AarDropdown.objects.get(sno=level), patent_status=AarDropdown.objects.get(sno=patent_status), patent_number=patent_number, application_no=application_no, owner=AarDropdown.objects.get(sno=owner),patent_co_applicant_name=patent_co_applicant_name,patent_applicant_name=patent_applicant_name,patent_co_applicant_name_other=patent_co_applicant_name_other,patent_applicant_name_other=patent_applicant_name_other)
        # query = AchFacPatentDetail.objects.bulk_create(objs)
        patent_id = GetPatentDetailsIdCheck(data1, patent_number, application_no)
    AchFacPatents.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), patent_details=AchFacPatentDetail.objects.get(id=patent_id[0]), patent_date=patent_date)
    p_id = list(AchFacPatents.objects.filter(emp_id=emp_id, patent_details=patent_id[0], patent_date=patent_date).exclude(status="DELETE").values_list('id', flat=True))
    if company_name and incorporate_status is not None:

        collaborators_check = GetPatentCollaboratorsIdCheck(data1)
        if len(collaborators_check) > 0:
            collab_id = collaborators_check
        else:
            AchFacPatentCollaborator.objects.create(patent_in=AchFacPatents.objects.get(id=p_id[0]), company_name=company_name, incorporate_status=incorporate_status)
            collab_id = GetPatentCollaboratorsIdCheck(data1)
    if detail_emp != None:
        objs1 = (AchFacMultiDetails(details_for='PATENT', key_id=p_id[0], detail_emp=EmployeeDropdown.objects.get(sno=d))for d in detail_emp)
        query2 = AchFacMultiDetails.objects.bulk_create(objs1)

    approval = RequestForApproval('PATENT', p_id[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}


def DesignFunction(data,employee_id):
    id = data['id']
    emp_id = data['employee']
    emp_discipline = data['emp_discipline']
    design_title = data['design_title']
    design_description = data['design_description']
    design_applicant_name=data['design_applicant_name']
    design_co_applicant_name=data['design_co_applicant_name']
    design_level=data['design_level']
    design_status=data['design_status']
    design_application_no=data['design_application_no']
    design_date=datetime.datetime.strptime(data['design_date'].split('T')[0], '%Y-%m-%d').date()
    design_owner=data['design_owner']

    ##################################################################################################################
    if 'design_company_name' and 'design_incorporate_status' in data:
        design_company_name=data['design_company_name']
        design_incorporate_status=AarDropdown.objects.get(sno=data['design_incorporate_status'])
    else:
        design_company_name= None
        design_incorporate_status = None

    if 'design_applicant_name_other' in data:
        design_applicant_name_other = data['design_applicant_name_other']
    else:
        design_applicant_name_other = None

    if 'design_co_applicant_name_other' in data:
        design_co_applicant_name_other = data['design_co_applicant_name_other']
    else:
        design_co_applicant_name_other = None

    ####################################################################################################################
    if id != None:
        AchFacDesign.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='DESIGN').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT

    mandatory_fields = ['design_title','design_description','design_applicant_name','design_co_applicant_name','design_level','design_status','design_owner',"design_application_no",'design_company_name','design_incorporate_status']
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}

    qry=AchFacDesign.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=employee_id),design_title=design_title,design_description=design_description,design_applicant_name=design_applicant_name,design_co_applicant_name=design_co_applicant_name,design_company_name=design_company_name , design_incorporate_status=design_incorporate_status,design_level=AarDropdown.objects.get(sno=design_level),design_status=AarDropdown.objects.get(sno=design_status),design_application_no=design_application_no,design_date=design_date,design_owner=AarDropdown.objects.get(sno=design_owner),design_applicant_name_other=design_applicant_name_other,design_co_applicant_name_other=design_co_applicant_name_other)

    qry1=list(AchFacDesign.objects.filter(emp_id=employee_id).values_list('id',flat=True).order_by('-id')[:1])

    if emp_discipline != None:
        objs1 = (AchFacMultiDetails(details_for='DESIGN', key_id=qry1[0], detail_emp=EmployeeDropdown.objects.get(sno=d))for d in emp_discipline)
        query2 = AchFacMultiDetails.objects.bulk_create(objs1)

    approval = RequestForApproval('DESIGN',qry1[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}


def DesignUpdateFunction(data,emp_id):
    id = data['id']
    design_title = data['design_title']
    design_company_name = data['design_company_name']
    design_description = data['design_description']
    design_applicant_name = data['design_applicant_name']
    design_co_applicant_name = data['design_co_applicant_name']
    design_incorporate_type = data['design_incorporation_type']
    design_level = data['design_level']
    design_status = data['design_status']
    design_application_no = data['design_application_no']
    design_date = datetime.datetime.strptime(data['design_date'].split('T')[0], '%Y-%m-%d').date()
    design_owner = data['design_owner']
    AchFacDesign.objects.filter(id=id,emp_id=emp_id).exclude(status="DELETE").update(design_title= design_title,design_description=design_description,design_applicant_name=design_applicant_name, design_co_applicant_name=design_co_applicant_name,design_application_no=design_application_no,design_date=design_date,design_level=design_level,design_status=design_status,design_owner=design_owner)
    AchFacApproval.objects.filter(approval_id=id, approval_category='DESIGN').exclude(status="DELETE").update(approval_status="PENDING")
    
    return {'data': "design successfully updated", 'status': statusCodes.STATUS_SUCCESS}
    
    
def LecturesTalksFunction(data, emp_id):
    id = data['id']
    category = data['category']
    type_of_event = data['type_of_event']
    organization_sector = data['organization_sector']
    incorporation_status = data['incorporation_status']
    role = data['role']
    date = datetime.datetime.strptime(data['date'].split('T')[0], '%Y-%m-%d').date()
    topic = data['topic']
    participants = data['participants']
    ######## VENUE DETAILS ####################################
    venue = data['venue']
    address = data['address']
    pin_code = data['pin_code']
    contact_number = data['contact_number']
    e_mail = data['e_mail']
    website = data['website']
    ############################################################
    ############# FOR UPDATE ###################################
    if id != None:
        AchFacLecturesTalks.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='LECTURES AND TALKS').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT
    ############################################################
    ################ FORMAT CHANGE FOR USE #####################
    data1 = {}
    for k, v in data.items():
        data1[k] = v
    ############################################################
    ############ FOR MANDATORY FIELDS AND CHECKS  ##############
    mandatory_fields = ['category', 'type_of_event', 'organization_sector', 'incorporation_status', 'role', 'date', 'topic', 'participants', 'venue', 'address', 'pin_code', 'contact_number', 'e_mail', 'website']
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ############################################################

    lectalks_venue_check = LecTalksVenueIdCheck(data1)
    if len(lectalks_venue_check) > 0:
        venue_id = LecTalksVenueIdCheck(data1)
    else:
        AchFacLecturesTalksVenue.objects.create(venue=venue, address=address, pin_code=pin_code, contact_number=contact_number, e_mail=e_mail, website=website)
        venue_id = LecTalksVenueIdCheck(data1)
    AchFacLecturesTalks.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), category=AarDropdown.objects.get(sno=category), type_of_event=AarDropdown.objects.get(sno=type_of_event), organization_sector=AarDropdown.objects.get(sno=organization_sector), incorporation_status=AarDropdown.objects.get(sno=incorporation_status), role=AarDropdown.objects.get(sno=role), venue_detail=AchFacLecturesTalksVenue.objects.get(id=venue_id[0]), date=date, topic=topic, participants=participants)
    lec_talks_id = list(AchFacLecturesTalks.objects.filter(emp_id=emp_id, category=category, type_of_event=type_of_event, organization_sector=organization_sector, incorporation_status=incorporation_status, role=role, venue_detail=venue_id[0], date=date, topic=topic, participants=participants).exclude(status="DELETE").values_list('id', flat=True))

    approval = RequestForApproval('LECTURES AND TALKS', lec_talks_id[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}


def TrainingDevelopmentFunction(data, emp_id):
    id = data['id']
    category = data['category']
    training_type = data['training_type']
    training_sub_type = data['training_sub_type']
    role = data['role']
    organization_sector = data['organization_sector']
    incorporation_type = data['incorporation_type']
    from_date = datetime.datetime.strptime(data['from_date'].split('T')[0], '%Y-%m-%d').date()
    to_date = datetime.datetime.strptime(data['to_date'].split('T')[0], '%Y-%m-%d').date()
    title = data['title']
    venue = data['venue']
    participants = data['participants']
    organizers = data['organizers']
    attended = data['attended']
    collaborations = data['collaborations']
    sponsership = data['sponsership']  # [] if No and [value] if Yes ###############
    discipline = data['discipline']
    if 'venue_others' in data:
        venue_other = data['venue_others']
    else:
        venue_other = None
    if 'other' in data:
        other = data['other']
    else:
        other = None
    ############ SPONSORS DETAILS ##############################
    sponsers = []
    collaborators = []
    if sponsership == 'Yes':
        sponsers = data['sponsers']  # array of dictionary ###################
        if len(sponsers) == 0:
            data_values = statusMessages.CUSTOM_MESSAGE('Enter the sponsers')
            return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    if collaborations == 'Yes':
        collaborators = data['collaborators']  # array of dictionanry #################
        if len(collaborators) == 0:
            data_values = statusMessages.CUSTOM_MESSAGE('Enter the collaborators')
            return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ############################################################
    ############# FOR UPDATE ###################################
    if id != None:
        AchFacTrainings.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='TRAINING AND DEVELOPMENT PROGRAM').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT
    ############################################################
    ################ FORMAT CHANGE FOR USE #####################
    data1 = {}
    for k, v in data.items():
        data1[k] = v
    ############################################################
    ############ FOR MANDATORY FIELDS AND CHECKS  ##############
    mandatory_fields = ['category', 'discipline', 'training_type', 'from_date', 'to_date', 'role', 'organization_sector', 'incorporation_type', 'title', 'venue', 'participants', 'organizers', 'attended', 'collaborations']
    if sponsership == 'Yes' or collaborations == 'Yes':
        mandatory_fields = SponsorsCollabAssoIdCheck(data1, mandatory_fields)
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    for s in sponsers:
        for k, v in s.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    for c in collaborators:
        for k, v in c.items():
            if v == None or v == "":
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    sponser_id = []
    collab_id = []
    if sponsers != None:
        for i in sponsers:
            data2 = {}
            for k, v in i.items():
                data2[k] = v
            sponsers_check = GetSponsorsIdCheck(data2)
            if len(sponsers_check) > 0:
                sponser_id.append(sponsers_check[0])
            else:
                AchFacSponser.objects.create(organisation=data2['organisation'], pin_code=data2['pin_code'], address=data2['address'], contact_number=data2['contact_number'], contact_person=data2['contact_person'], e_mail=data2['e_mail'], website=data2['website'], amount=data2['amount'])
                s_id = GetSponsorsIdCheck(data2)
                sponser_id.append(s_id[0])

    if collaborators != None:
        for i in collaborators:
            data2 = {}
            for k, v in i.items():
                data2[k] = v
            collab_check = GetCollaboratorsIdCheck(data2)
            if len(collab_check) > 0:
                collab_id.append(collab_check[0])
            else:
                AchFacCollaborators.objects.create(organisation=data2['organisation'], pin_code=data2['pin_code'], address=data2['address'], contact_number=data2['contact_number'], contact_person=data2['contact_person'], e_mail=data2['e_mail'], website=data2['website'], amount=data2['amount'])
                c_id = GetCollaboratorsIdCheck(data2)
                collab_id.append(c_id[0])
    ############################################################

    AchFacTrainings.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), category=AarDropdown.objects.get(sno=category), training_type=AarDropdown.objects.get(sno=training_type),training_sub_type=AarDropdown.objects.get(sno=training_sub_type), role=AarDropdown.objects.get(sno=role), organization_sector=AarDropdown.objects.get(sno=organization_sector), incorporation_type=AarDropdown.objects.get(sno=incorporation_type), from_date=from_date, to_date=to_date, title=title, venue=AarDropdown.objects.get(sno=venue), venue_other=venue_other, other=other, participants=participants, organizers=organizers, attended=attended, collaborations=collaborations, sponsership=sponsership)
    training_id = list(AchFacTrainings.objects.filter(emp_id=emp_id, category=category, training_type=training_type, role=role, organization_sector=organization_sector, incorporation_type=incorporation_type, from_date=from_date, to_date=to_date, title=title, venue=venue, venue_other=venue_other, participants=participants, organizers=organizers, attended=attended, collaborations=collaborations, sponsership=sponsership).exclude(status="DELETE").values_list('id', flat=True))
    objs1 = (AchFacMapIds(key_type='SPONSORS', key_id=s, form_id=training_id[0], form_type='TRAINING AND DEVELOPMENT PROGRAM')for s in sponser_id)
    query = AchFacMapIds.objects.bulk_create(objs1)
    objs2 = (AchFacMapIds(key_type='COLLABORATORS', key_id=c, form_id=training_id[0], form_type='TRAINING AND DEVELOPMENT PROGRAM')for c in collab_id)
    query = AchFacMapIds.objects.bulk_create(objs2)
    objs3 = (AchFacMultiDetails(details_for='TRAINING AND DEVELOPMENT PROGRAM', key_id=training_id[0], detail_emp=EmployeeDropdown.objects.get(sno=d))for d in discipline)
    query3 = AchFacMultiDetails.objects.bulk_create(objs3)

    approval = RequestForApproval('TRAINING AND DEVELOPMENT PROGRAM', training_id[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}


def ProjectsConsultancyFunction(data, emp_id):
    print(data, 'data')
    id = data['id']
    project_type = data['project_type']
    project_status = data['project_status']
    sector = data['sector']
    project_title = data['project_title']
    project_description = data['project_description']
    start_date = datetime.datetime.strptime(data['start_date'].split('T')[0], '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(data['end_date'].split('T')[0], '%Y-%m-%d').date()
    principal_investigator = data['principal_investigator']
    co_principal_investigator = data['co_principal_investigator']
    team_size = data['team_size']
    sponsored = data['sponsored']
    association = data['association']
    discipline = data['discipline']
    ##########################################################
    if 'principal_investigator_other' in data:
        principal_investigator_other = data['principal_investigator_other']
    else:
        principal_investigator_other = None
    if 'co_principal_investigator_other' in data:
        co_principal_investigator_other = data['co_principal_investigator_other']
    else:
        co_principal_investigator_other = None
    ############## SPONSORS DETAILS ##########################
    sponsers = []
    if sponsored == "Yes":
        sponsers = data['sponsers']  # array of dictionary ##############
        if len(sponsers) == 0:
            data_values = statusMessages.CUSTOM_MESSAGE('Enter the sponsers')
            return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ##########################################################
    ############## ASSOCIATION DETAILS #######################
    associators = []
    if association == "Yes":
        associators = data['associators']  # array of dictionary ##############
        if len(associators) == 0:
            data_values = statusMessages.CUSTOM_MESSAGE('Enter the associators')
            return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    ############################################################
    ############# FOR UPDATE ###################################
    if id != None:
        AchFacProjects.objects.filter(id=id).update(status="DELETE")
        AchFacApproval.objects.filter(approval_id=id, approval_category='PROJECTS/CONSULTANCY').update(status="DELETE")
        data_values = statusMessages.MESSAGE_UPDATE
    else:
        data_values = statusMessages.MESSAGE_INSERT
    ############################################################
    ################ FORMAT CHANGE FOR USE #####################
    # print("update")
    data1 = {}
    for k, v in data.items():
        data1[k] = v
    ############################################################
    ############ FOR MANDATORY FIELDS AND CHECKS  ##############
    mandatory_fields = ['start_date', 'end_date', 'project_type', 'project_status', 'discipline', 'sector', 'principal_investigator', 'co_principal_investigator', 'team_size', 'sponsored', 'project_title', 'project_description', 'association']
    if sponsored == 'Yes' or association == 'Yes':
        mandatory_fields = SponsorsCollabAssoIdCheck(data1, mandatory_fields)
    for m in mandatory_fields:
        for k, v in data.items():
            if k == m and (v == None or v == ""):
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    for s in sponsers:
        for k, v in s.items():
            if v == None or v == "":
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
    for a in associators:
        for k, v in a.items():
            if v == None or v == "":
                data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                data_values2 = k
                data_values = [data_values1, data_values2]
                return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}

    sponser_id = []
    asso_id = []
    if sponsers != None:
        for i in sponsers:
            data2 = {}
            for k, v in i.items():
                data2[k] = v
            sponsers_check = GetSponsorsIdCheck(data2)
            if len(sponsers_check) > 0:
                sponser_id.append(sponsers_check[0])
            else:
                AchFacSponser.objects.create(organisation=data2['organisation'], pin_code=data2['pin_code'], address=data2['address'], contact_number=data2['contact_number'], contact_person=data2['contact_person'], e_mail=data2['e_mail'], website=data2['website'], amount=data2['amount'])
                s_id = GetSponsorsIdCheck(data2)
                sponser_id.append(s_id[0])

    if associators != None:
        for i in associators:
            data2 = {}
            for k, v in i.items():
                data2[k] = v
            asso_check = GetAssociationsIdCheck(data2)
            if len(asso_check) > 0:
                asso_id.append(asso_check[0])
            else:
                AchFacAssociations.objects.create(organisation=data2['organisation'], pin_code=data2['pin_code'], address=data2['address'], contact_number=data2['contact_number'], contact_person=data2['contact_person'], e_mail=data2['e_mail'], website=data2['website'], amount=data2['amount'])
                a_id = GetAssociationsIdCheck(data2)
                asso_id.append(a_id[0])
    ############################################################
    # print("vrinda")
    AchFacProjects.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), project_type=AarDropdown.objects.get(sno=project_type), project_status=AarDropdown.objects.get(sno=project_status), sector=AarDropdown.objects.get(sno=sector), project_title=project_title, project_description=project_description, start_date=start_date, end_date=end_date, principal_investigator=principal_investigator, co_principal_investigator=co_principal_investigator, principal_investigator_other=principal_investigator_other, co_principal_investigator_other=co_principal_investigator_other, team_size=team_size, sponsored=sponsored, association=association)
    project_id = list(AchFacProjects.objects.filter(emp_id=emp_id, project_type=project_type, project_status=project_status, sector=sector, project_title=project_title, project_description=project_description, start_date=start_date, end_date=end_date, principal_investigator=principal_investigator, co_principal_investigator=co_principal_investigator, principal_investigator_other=principal_investigator_other, co_principal_investigator_other=co_principal_investigator_other, team_size=team_size, sponsored=sponsored, association=association).exclude(status="DELETE").values_list('id', flat=True))

    objs1 = (AchFacMapIds(key_type='SPONSORS', key_id=s, form_id=project_id[0], form_type='PROJECTS/CONSULTANCY')for s in sponser_id)
    query = AchFacMapIds.objects.bulk_create(objs1)
    objs2 = (AchFacMapIds(key_type='ASSOCIATIONS', key_id=a, form_id=project_id[0], form_type='PROJECTS/CONSULTANCY')for a in asso_id)
    query = AchFacMapIds.objects.bulk_create(objs2)
    objs3 = (AchFacMultiDetails(details_for='PROJECTS/CONSULTANCY', key_id=project_id[0], detail_emp=EmployeeDropdown.objects.get(sno=d))for d in discipline)
    query3 = AchFacMultiDetails.objects.bulk_create(objs3)

    approval = RequestForApproval('PROJECTS/CONSULTANCY', project_id[0])
    return {'data': data_values, 'status': statusCodes.STATUS_SUCCESS}

######################################################consolidate report dropdowns###########################################
def consolidated_dropdown_data(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_dropdown_data')):
                form_id=int(request.GET['form_id'])
                if form_id==1:
                    qry=AarDropdown.objects.filter(field='BOOKS').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                elif form_id==2:
                    qry=AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                elif form_id==3:
                    qry=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                elif form_id==4:
                    qry=AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                elif form_id==5:
                    qry=AarDropdown.objects.filter(field='PATENT').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                elif form_id==6:
                    qry=AarDropdown.objects.filter(field='LECTURES AND TALKS').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                elif form_id==7:
                    qry=AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                elif form_id==8:
                    qry=AarDropdown.objects.filter(field='PROJECTS/CONSULTANCY').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                elif form_id==9:
                    qry=AarDropdown.objects.filter(field='DESIGN').exclude(status="DELETE").exclude(value__isnull=True).values('sno','value')

                data=list(qry)
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'get_report_data')):
                required_criteria=request.GET['dropdown'].split(',')
                from_date=request.GET['from_date']
                to_date=request.GET['to_date']
                dept = request.GET['dept'].split(',')      
                form_id=int(request.GET['form_id'])          
                if form_id==1:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        for q in filter_fields:
                            field_count=AchFacBooks.objects.filter(Q(role=q['sno']) | Q(role_for=q['sno']) | Q(publisher_type=q['sno']) | Q(author=q['sno'])).filter(emp_id__dept__in=dept,published_date__range=[from_date,to_date]).exclude(status="DELETE").count()
                            if field_count:
                                # print(q['value'],field_count)
                                data.append({"label":q['value'],"value":field_count})
                        if filter_fields:
                            data_values.append({"heading":query_field_name[0]['value'],"data":data})
                elif form_id==2:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        for q in filter_fields:
                            field_count=AchFacConferences.objects.filter(Q(category=q['sno']) | Q(sub_category=q['sno']) | Q(author=q['sno']) | Q(conference_detail__type_of_conference=q['sno']) | Q(conference_detail__type_of_activity=q['sno'])).filter(emp_id__dept__in=dept,conference_detail__conference_from__gte=from_date,conference_detail__conference_from__lte=to_date).exclude(status="DELETE").count()
                            if field_count:
                                data.append({"label":q['value'],"value":field_count})
                        if filter_fields:
                            data_values.append({"heading":query_field_name[0]['value'],"data":data})
                elif form_id==3:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        for q in filter_fields:
                            field_count=AchFacGuidances.objects.filter(Q(guidance_for__value=q['value']) | Q(university_type__value=q['value']) | Q(course__value=q['value'])).filter(emp_id__dept__in=dept,date_of_guidance__range=[from_date,to_date]).exclude(status="DELETE").count()
                            if field_count!=0:
                                data.append({"label":q['value'],"value":field_count})
                        if filter_fields:
                            data_values.append({"heading":query_field_name[0]['value'],"data":data})
                elif form_id==4:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        for q in filter_fields:
                            field_count=AchFacJournals.objects.filter(Q(category=q['sno']) | Q(journal_details__type_of_journal=q['sno']) | Q(author=q['sno']) | Q(journal_details__sub_category=q['sno']) | Q(journal_details__type_of_journal=q['sno']) | Q(journal_details__sub_category=q['sno'])).filter(emp_id__dept__in=dept,published_date__range=[from_date,to_date]).exclude(status="DELETE").count()
                            if field_count:
                                data.append({"label":q['value'],"value":field_count})
                            
                        if filter_fields:
                            data_values.append({"heading":query_field_name[0]['value'],"data":data})
                elif form_id==6:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        for q in filter_fields:
                            field_count=AchFacLecturesTalks.objects.filter(Q(category=q['sno']) | Q(type_of_event=q['sno']) | Q(organization_sector=q['sno']) | Q(incorporation_status=q['sno'])).filter(emp_id__dept__in=dept,date__range=[from_date,to_date]).exclude(status="DELETE").count()
                            if field_count:
                                data.append({"label":q['value'],"value":field_count})
                        data_values.append({"heading":query_field_name[0]['value'],"data":data})
                elif form_id==5:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        print(filter_fields)
                        for q in filter_fields:
                            field_count=AchFacPatents.objects.filter(Q(patent_details__level=q['sno']) | Q(patent_details__patent_status=q['sno']) | Q(patent_details__owner=q['sno'])).filter(emp_id__dept__in=dept,patent_date__range=[from_date,to_date]).exclude(status="DELETE").count()
                            print(field_count)
                            if field_count!=0 :
                                data.append({"label":q['value'],"value":field_count})
                            else:
                                field_count1=AchFacPatentCollaborator.objects.filter(incorporate_status=q['sno']).filter(patent_in__emp_id__dept__in=dept,patent_in__patent_date__range=[from_date,to_date]).exclude(status="DELETE").count()
                                if field_count1:
                                    data.append({"label":q['value'],"value":field_count1})
                                
                        if filter_fields:
                            data_values.append({"heading":query_field_name[0]['value'],"data":data})
                elif form_id==7:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        for q in filter_fields:
                            field_count=AchFacTrainings.objects.filter(Q(category=q['sno']) | Q(training_type=q['sno']) | Q(organization_sector=q['sno']) | Q(incorporation_type=q['sno']) | Q(venue=q['sno'])).filter(emp_id__dept__in=dept,from_date__gte=from_date,to_date__lte=to_date).exclude(status="DELETE").count()
                            if field_count:
                                data.append({"label":q['value'],"value":field_count})
                        data_values.append({"heading":query_field_name[0]['value'],"data":data})
                elif form_id==8:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        for q in filter_fields:
                            field_count=AchFacProjects.objects.filter(Q(project_type=q['sno']) | Q(project_status=q['sno']) | Q(sector=q['sno'])).filter(emp_id__dept__in=dept,start_date__gte=from_date,end_date__lte=to_date).exclude(status="DELETE").count()
                            if field_count:
                                data.append({"label":q['value'],"value":field_count})
                        if filter_fields:
                            data_values.append({"heading":query_field_name[0]['value'],"data":data})

                elif form_id==9:
                    data_values=[]
                    for req in required_criteria:
                        query_field_name=AarDropdown.objects.filter(sno=req).exclude(value__isnull=True).exclude(status="DELETE").values('value')
                        filter_fields=AarDropdown.objects.filter(pid=req).exclude(value__isnull=True).exclude(status="DELETE").values('sno','value')
                        data=[]
                        for q in filter_fields:
                            field_count=AchFacDesign.objects.filter(Q(design_status=q['sno']) | Q(design_incorporate_status=q['sno']) | Q(design_level=q['sno']) | Q(design_owner=q['sno'])).filter(emp_id__dept__in=dept,design_date__range=[from_date,to_date]).exclude(status="DELETE").count()
                            if field_count:
                                data.append({"label":q['value'],"value":field_count})
                        if filter_fields:
                            data_values.append({"heading":query_field_name[0]['value'],"data":data})

                return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)
            elif(requestType.custom_request_type(request.GET, 'get_count')):
                data=[]
                form_id=int(request.GET['form_id'])
                key=request.GET['key']
                dept=request.GET['dept'].split(',')

                if form_id==1:
                    data = list(AchFacBooks.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                elif form_id==2:
                    data = list(AchFacConferences.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                elif form_id==3:
                    data = list(AchFacGuidances.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                elif form_id==4:
                    data = list(AchFacJournals.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                elif form_id==5:
                    data = list(AchFacPatents.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                elif form_id==6:
                    data = list(AchFacLecturesTalks.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                elif form_id==7:
                    data = list(AchFacTrainings.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                elif form_id==8:
                    data = list(AchFacProjects.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                elif form_id==9:
                    data = list(AchFacDesign.objects.filter(emp_id__dept__in=dept).exclude(status="DELETE").values_list(key,flat=True).distinct())

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'duration_count')):
                data=[]
                form_id=int(request.GET['form_id'])
                z=int(request.GET['duration'])
                dept=request.GET['dept'].split(',')
                from_d = datetime.datetime.strptime(request.GET['from_date'].split('T')[0], '%Y-%m-%d').date()
                to_d = datetime.datetime.strptime(request.GET['to_date'].split('T')[0], '%Y-%m-%d').date()
                print(from_d,to_d)
                date_list=[]
                data_values=[]
                while(from_d<=to_d):
                    date_list.append(from_d)
                    from_d=from_d + datetime.timedelta(days=z)
                if date_list[-1]<to_d:
                    date_list.append(to_d)
                print(date_list)
                if form_id==1:
                    for x in range(1,len(date_list)):
                        from_date=date_list[x-1]
                        to_date=date_list[x]
                        data = AchFacBooks.objects.filter(emp_id__dept__in=dept,published_date__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])
                elif form_id==2:
                    for x in range(0,len(date_list)-1):
                        from_date=date_list[x]
                        to_date=date_list[x+1]
                        data = AchFacConferences.objects.filter(emp_id__dept__in=dept,conference_detail__conference_from__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])
                elif form_id==3:
                    for x in range(0,len(date_list)-1):
                        from_date=date_list[x]
                        to_date=date_list[x+1]
                        data = AchFacGuidances.objects.filter(emp_id__dept__in=dept,date_of_guidance__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])
                elif form_id==4:
                    for x in range(0,len(date_list)-1):
                        from_date=date_list[x]
                        to_date=date_list[x+1]
                        data = AchFacJournals.objects.filter(emp_id__dept__in=dept,published_date__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])
                elif form_id==5:
                    for x in range(0,len(date_list)-1):
                        from_date=date_list[x]
                        to_date=date_list[x+1]
                        data = AchFacPatents.objects.filter(emp_id__dept__in=dept,patent_date__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])
                elif form_id==6:
                    for x in range(0,len(date_list)-1):
                        from_date=date_list[x]
                        to_date=date_list[x+1]
                        data = AchFacLecturesTalks.objects.filter(emp_id__dept__in=dept,date__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])
                elif form_id==7:
                    for x in range(0,len(date_list)-1):
                        from_date=date_list[x]
                        to_date=date_list[x+1]
                        data = AchFacTrainings.objects.filter(emp_id__dept__in=dept,from_date__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])
                elif form_id==8:
                    for x in range(0,len(date_list)-1):
                        from_date=date_list[x]
                        to_date=date_list[x+1]
                        data = AchFacProjects.objects.filter(emp_id__dept__in=dept,start_date__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])

                elif form_id==9:
                    for x in range(0,len(date_list)-1):
                        from_date=date_list[x]
                        to_date=date_list[x+1]
                        data = AchFacDesign.objects.filter(emp_id__dept__in=dept,design_date__range=[from_date,to_date]).exclude(status="DELETE").values_list().distinct().count()
                        data_values.append([to_date,data])
                return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body.decode("utf-8"))       
            data1=data['data']
            form_id = data['form_id']
            extra_filter=data1
            print(extra_filter)
            if form_id==1:
                data=AchFacBooks.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()
            elif form_id==2:
                data=AchFacConferences.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()
            elif form_id==3:
                data=AchFacGuidances.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()
            elif form_id==4:
                data=AchFacJournals.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()
            elif form_id==5:
                data=AchFacPatents.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()
            elif form_id==6:
                data=AchFacLecturesTalks.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()
            elif form_id==7:
                data=AchFacTrainings.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()
            elif form_id==8:
                data=AchFacProjects.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()
            elif form_id==9:
                data=AchFacDesign.objects.filter(**extra_filter).exclude(status="DELETE").values().distinct().count()

            print(data)
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)                

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)