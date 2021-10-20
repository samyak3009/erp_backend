
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
from aar.models import *
from login.models import EmployeePrimdetail

from Achievement.views.achievement_function import *
from login.views import checkpermission, generate_session_table_name


def ScriptsBooks(request):
    qry = list(Books.objects.values('emp_id', 'role', 'role_for', 'publisher_type', 'title', 'edition', 'published_date', 'chapter', 'isbn', 'copyright_status', 'copyright_no', 'author', 'publisher_name', 'publisher_address', 'publisher_zip_code', 'publisher_contact', 'publisher_email', 'publisher_website', 't_date', 'approve_status'))
    # publisher_data = list(Books.objects.values('publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website').distinct())
    pub_data_to_insert = []
    for p in qry:
        pub_check = GetPublisherIdCheck(p)
        if len(pub_check) == 0:
            pub_data_to_insert.append(p)
    objs1 = (AchFacPublishers(publisher_name=p['publisher_name'], publisher_address_1=p['publisher_address'], publisher_zip_code=p['publisher_zip_code'], publisher_contact=p['publisher_contact'], publisher_email=p['publisher_email'], publisher_website=p['publisher_website'])for p in pub_data_to_insert)
    q2 = AchFacPublishers.objects.bulk_create(objs1)
    # qry = list(Books.objects.values('emp_id','role','role_for','publisher_type','title','edition','published_date','chapter','isbn','copyright_status','copyright_no','author','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','t_date','approve_status'))
    cp_id = []
    for q in qry:
        copyright_status = q['copyright_status']
        copyright_status_id = list(AarDropdown.objects.filter(field='COPYRIGHT STATUS', value=copyright_status).exclude(value__isnull=True).values_list('sno', flat=True))
        # print(copyright_status_id,'copyright_status_id')
        publisher_det_id = GetPublisherIdCheck(q)
        # print(publisher_det_id,'publisher_det_id')
        if len(copyright_status_id) > 0:
            q['c_id'] = copyright_status_id[0]
        else:
            q['c_id'] = None
        q['p_id'] = publisher_det_id[0]

    for q in qry:
        # print(q['c_id'],'vrinda singhal')
        role = AarDropdown.objects.get(sno=q['role'])
        # print(role,'role')
        role_for = AarDropdown.objects.get(sno=q['role_for'])
        # print(role_for,'role_for')
        author = AarDropdown.objects.get(sno=q['author'])
        # print(author,'author')
        publisher_type = AarDropdown.objects.get(sno=q['publisher_type'])
        # print(publisher_type,'publisher_type')
        AchFacBooks.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=q['emp_id']), role=role, role_for=role_for, book_title=q['title'], book_edition=q['edition'], published_date=q['published_date'], isbn=q['isbn'], chapter=q['chapter'], author=author, copyright_status=AarDropdown.objects.get(sno=q['c_id']), copyright_no=q['copyright_no'], publisher_type=publisher_type, publisher_details=AchFacPublishers.objects.get(id=q['p_id']), time_stamp=q['t_date'])
        query = list(AchFacBooks.objects.filter(emp_id=q['emp_id'], role=q['role'], role_for=q['role_for'], book_title=q['title'], book_edition=q['edition'], published_date=q['published_date'], isbn=q['isbn'], chapter=q['chapter'], author=q['author'], copyright_status=q['c_id'], copyright_no=q['copyright_no'], publisher_type=q['publisher_type'], publisher_details=q['p_id']).exclude(status="DELETE").values_list('id', flat=True))
        AchFacApproval.objects.create(level=1, approval_category='BOOKS', approval_id=query[0], approval_status=q['approve_status'], time_stamp=q['t_date'])
        # print("inserted")
    msg = 'Data sucessfully inserted'
    data = {'msg': msg}
    status = 200
    return JsonResponse(data, status=status, safe=False)


def ScriptsConference(request):
    qry = list(Researchconference.objects.values('id', 'emp_id', 'category', 'type_of_conference', 'sub_category', 'sponsered', 'conference_title', 'paper_title', 'published_date', 'organized_by', 'journal_name', 'volume_no', 'issue_no', 'isbn', 'page_no', 'author', 'conference_from', 'conference_to', 'other_description', 'publisher_name', 'publisher_address', 'publisher_zip_code', 'publisher_contact', 'publisher_email', 'publisher_website', 'approve_status', 'others'))
    # conference_data = list(Researchconference.objects.values('type_of_conference','conference_title','conference_from','conference_to','organized_by').distinct())
    conference_data_to_insert = []
    for c in qry:
        conf_check = GetConferenceIdCheck(c)
        if len(conf_check) == 0:
            conference_data_to_insert.append(c)
    objs1 = (AchFacConferenceDetail(conference_title=c['conference_title'], type_of_conference=AarDropdown.objects.get(sno=c['type_of_conference']), conference_from=c['conference_from'], conference_to=c['conference_to'], organized_by=c['organized_by'])for c in conference_data_to_insert)
    q1 = AchFacConferenceDetail.objects.bulk_create(objs1)

    # publisher_data = list(Researchconference.objects.values('publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website').distinct())
    pub_data_to_insert = []
    for p in qry:
        pub_check = GetPublisherIdCheck(p)
        if len(pub_check) == 0:
            pub_data_to_insert.append(p)
    objs2 = (AchFacPublishers(publisher_name=p['publisher_name'], publisher_address_1=p['publisher_address'], publisher_zip_code=p['publisher_zip_code'], publisher_contact=p['publisher_contact'], publisher_email=p['publisher_email'], publisher_website=p['publisher_website'])for p in pub_data_to_insert)
    q2 = AchFacPublishers.objects.bulk_create(objs2)

    # qry = list(Researchconference.objects.values('id','emp_id','category','type_of_conference','sub_category','sponsered','conference_title','paper_title','published_date','organized_by','journal_name','volume_no','issue_no','isbn','page_no','author','conference_from','conference_to','other_description','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','approve_status','others'))
    for q in qry:
        if q['author'] == None:
            author = list(AarDropdown.objects.filter(field='AUTHOR', value=None).values_list('sno', flat=True))
            q['author'] = author[0]
        conference_det_id = GetConferenceIdCheck(q)
        # print(conference_det_id,'conference_det_id')
        q['c_id'] = conference_det_id[0]
        publisher_det_id = GetPublisherIdCheck(q)
        q['p_id'] = publisher_det_id[0]
        if q['sponsered'] == 'Yes':
            query3 = list(Sponsers.objects.filter(spons_id=q['id'], emp_id=q['emp_id'], type='CONFERENCE').values_list('sponser_name', flat=True))
            objs3 = (AchFacMultiDetails(details_for='RESEARCH PAPER IN CONFERENCE', key_id=query2[0], detail_text=s)for s in query3)
            q3 = AchFacMultiDetails.objects.bulk_create(objs3)

        query1 = AchFacConferences.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=q['emp_id']), category=AarDropdown.objects.get(sno=q['category']), conference_detail=AchFacConferenceDetail.objects.get(id=q['c_id']), sub_category=AarDropdown.objects.get(sno=q['sub_category']), paper_title=q['paper_title'], published_date=q['published_date'], journal_name=q['journal_name'], volume_no=q['volume_no'], issue_no=q['issue_no'], isbn=q['isbn'], page_no=q['page_no'], author=AarDropdown.objects.get(sno=q['author']), other_description=q['other_description'], publisher_details=AchFacPublishers.objects.get(id=q['p_id']), others=q['others'])
        query2 = list(AchFacConferences.objects.filter(emp_id=q['emp_id'], category=q['category'], conference_detail=q['c_id'], sub_category=q['sub_category'], paper_title=q['paper_title'], published_date=q['published_date'], journal_name=q['journal_name'], volume_no=q['volume_no'], issue_no=q['issue_no'], isbn=q['isbn'], page_no=q['page_no'], author=q['author'], other_description=q['other_description'], publisher_details=q['p_id'], others=q['others']).exclude(status="DELETE").values_list('id', flat=True))

        AchFacApproval.objects.create(level=1, approval_category='RESEARCH PAPER IN CONFERENCE', approval_id=query2[0], approval_status=q['approve_status'])
        # print('inserted')

    msg = 'Data sucessfully inserted'
    data = {'msg': msg}
    status = 200
    return JsonResponse(data, status=status, safe=False)


def ScriptsGuidance(request):
    emp_id = request.session['hash1']
    qry = list(Researchguidence.objects.values('id', 'emp_id', 'guidence', 'course', 'degree', 'no_of_students', 'degree_awarded', 'uni_type', 'uni_name', 'status', 'project_title', 'area_of_spec', 'approve_status', 't_date', 'date'))
    guidance_phd = list(AarDropdown.objects.filter(field="RESEARCH (PH. D.)").values("sno", 'value'))
    # print(guidance_phd,'guidance_phd')
    # guidance_status = list(AarDropdown.objects.filter(field="GUIDANCE",value="STATUS").values_list("sno",flat=True))
    # print(guidance_status,'guidance_status')
    guidance_status_pid = list(AarDropdown.objects.filter(field="GUIDANCE", value="RESEARCH (PH. D.)").values_list('sno', flat=True))
    # print(guidance_status_pid,'guidance_status_pid')
    status = list(AarDropdown.objects.filter(field="RESEARCH (PH. D.)", pid=guidance_status_pid[0], value__isnull=True).values_list("sno", flat=True))
    # print(status,'status')
    for q in qry:
        # for g_phd in guidance_phd:
        # 	if q['guidence']==g_phd['sno']:
        q['guidence'] = AarDropdown.objects.get(sno=q['guidence'])
        if q['status'] == None:
            q['status'] = None
        else:
            q['status'] = AarDropdown.objects.get(sno=q['status'])
            # 	status_value = list(AarDropdown.objects.filter(sno=q['status']).values_list("value",flat=True))
            # 	for s in status:
            # 		if s['value']==status_value[0]:
            # 			q['status'] = AarDropdown.objects.get(sno=s['sno'])
            # else:
            # 	q['guidence'] = AarDropdown.objects.get(sno=q['guidence'])
        if q['course'] != None:
            q['course'] = StudentDropdown.objects.get(sno=q['course'])
        if q['degree'] != None:
            q['degree'] = StudentDropdown.objects.get(sno=q['degree'])
        if q['uni_type'] != None:
            q['uni_type'] = AarDropdown.objects.get(sno=q['uni_type'])
        AchFacGuidances.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=q['emp_id']), guidance_for=q['guidence'], course=q['course'], degree=q['degree'], guidance_awarded_status=q['degree_awarded'], university_type=q['uni_type'], university_name=q['uni_name'], guidance_status=q['status'], no_of_students=q['no_of_students'], project_title=q['project_title'], area_of_specification=q['area_of_spec'], date_of_guidance=q['date'], time_stamp=q['t_date'])
        query = list(AchFacGuidances.objects.filter(emp_id=q['emp_id'], guidance_for=q['guidence'], course=q['course'], degree=q['degree'], guidance_awarded_status=q['degree_awarded'], university_type=q['uni_type'], university_name=q['uni_name'], guidance_status=q['status'], no_of_students=q['no_of_students'], project_title=q['project_title'], area_of_specification=q['area_of_spec'], date_of_guidance=q['date']).exclude(status="DELETE").values_list('id', flat=True))
        AchFacApproval.objects.create(level=1, approval_category='RESEARCH GUIDANCE / PROJECT GUIDANCE', approval_id=query[0], approval_status=q['approve_status'], time_stamp=q['t_date'])
        # print("inserted")
    msg = 'Data sucessfully inserted'
    data = {'msg': msg}
    status = 200
    return JsonResponse(data, status=status, safe=False)


def ScriptsJournal(request):
    emp_id = request.session['hash1']
    qry = list(Researchjournal.objects.values('emp_id', 'category', 'published_date', 'paper_title', 'impact_factor', 'page_no', 'author', 'others', 'approve_status', 't_date', 'publisher_name', 'publisher_address1', 'publisher_address2', 'publisher_zip_code', 'publisher_contact', 'publisher_email', 'publisher_website', 'type_of_journal', 'journal_name', 'volume_no', 'issue_no', 'isbn', 'sub_category'))
    # journal_data = list(Researchjournal.objects.values('type_of_journal','journal_name','volume_no','issue_no','isbn','sub_category').distinct())
    jou_data_to_insert = []
    for j in qry:
        jou_check = GetJournalDetailsCheck(j)
        if len(jou_check) == 0:
            jou_data_to_insert.append(j)

    # publisher_data = list(Researchjournal.objects.values('publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website').distinct())
    pub_data_to_insert = []
    for p in qry:
        pub_check = GetPublisherIdCheck(p)
        if len(pub_check) == 0:
            pub_data_to_insert.append(p)

    objs1 = (AchFacJournalDetail(journal_name=j['journal_name'], type_of_journal=AarDropdown.objects.get(sno=j['type_of_journal']), sub_category=AarDropdown.objects.get(sno=j['sub_category']), volume_no=j['volume_no'], issue_no=j['issue_no'], isbn=j['isbn'])for j in jou_data_to_insert)
    q1 = AchFacJournalDetail.objects.bulk_create(objs1)

    objs2 = (AchFacPublishers(publisher_name=p['publisher_name'], publisher_address_1=p['publisher_address1'], publisher_address_2=p['publisher_address2'], publisher_zip_code=p['publisher_zip_code'], publisher_contact=p['publisher_contact'], publisher_email=p['publisher_email'], publisher_website=p['publisher_website'])for p in pub_data_to_insert)
    q2 = AchFacPublishers.objects.bulk_create(objs2)

    # qry = list(Researchjournal.objects.values('emp_id','category','published_date','paper_title','impact_factor','page_no','author','others','approve_status','t_date','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','type_of_journal','journal_name','volume_no','issue_no','isbn','sub_category'))

    co_author_pid = AarDropdown.objects.filter(field="RESEARCH PAPER IN JOURNAL", value="AUTHOR").values_list('sno', flat=True)
    co_author_sno = AarDropdown.objects.filter(pid=co_author_pid[0], value="CO-AUTHOR").values_list("sno", flat=True)
    for q in qry:
        journal_id = GetJournalDetailsCheck(q)
        q['j_id'] = journal_id[0]
        pub_id = GetPublisherIdCheck(q)
        q['p_id'] = pub_id[0]

        author_check = AarDropdown.objects.filter(sno=q['author'], field="AUTHOR").values_list("sno", flat=True)
        if len(author_check) == 0:
            q['author'] = co_author_sno[0]
        AchFacJournals.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=q['emp_id']), category=AarDropdown.objects.get(sno=q['category']), author=AarDropdown.objects.get(sno=q['author']), published_date=q['published_date'], paper_title=q['paper_title'], impact_factor=q['impact_factor'], page_no=q['page_no'], journal_details=AchFacJournalDetail.objects.get(id=q['j_id']), publisher_details=AchFacPublishers.objects.get(id=q['p_id']), time_stamp=q['t_date'])
        query = list(AchFacJournals.objects.filter(emp_id=q['emp_id'], category=q['category'], author=q['author'], published_date=q['published_date'], paper_title=q['paper_title'], impact_factor=q['impact_factor'], page_no=q['page_no'], journal_details=q['j_id'], publisher_details=q['p_id']).exclude(status="DELETE").values_list('id', flat=True))
        AchFacApproval.objects.create(level=1, approval_category='RESEARCH PAPER IN JOURNAL', approval_id=query[0], approval_status=q['approve_status'], time_stamp=q['t_date'])
        # print("inserted")
    msg = 'Data sucessfully inserted'
    data = {'msg': msg}
    status = 200
    return JsonResponse(data, status=status, safe=False)


def ScriptsLecturesTalks(request):
    emp_id = request.session['hash1']
    venue_data = list(LecturesTalks.objects.values('venue', 'address', 'pin_code', 'contact_number', 'e_mail', 'website'))
    venue_data_to_insert = []
    for v in venue_data:
        venue_check = LecTalksVenueIdCheck(v)
        if len(venue_check) == 0:
            venue_data_to_insert.append(v)

    objs1 = (AchFacLecturesTalksVenue(venue=v['venue'], address=v['address'], pin_code=v['pin_code'], contact_number=v['contact_number'], e_mail=v['e_mail'], website=v['website'])for v in venue_data_to_insert)
    q1 = AchFacLecturesTalksVenue.objects.bulk_create(objs1)
    qry = list(LecturesTalks.objects.values('emp_id', 'category', 'type', 'organization_sector', 'incorporation_status', 'role', 'date', 'topic', 'participants', 'venue', 'address', 'pin_code', 'contact_number', 'e_mail', 'website', 'approve_status', 't_date'))
    for q in qry:
        venue_id = LecTalksVenueIdCheck(q)
        q['v_id'] = venue_id[0]
        AchFacLecturesTalks.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=q['emp_id']), category=AarDropdown.objects.get(sno=q['category']), type_of_event=AarDropdown.objects.get(sno=q['type']), organization_sector=AarDropdown.objects.get(sno=q['organization_sector']), incorporation_status=AarDropdown.objects.get(sno=q['incorporation_status']), role=AarDropdown.objects.get(sno=q['role']), venue_detail=AchFacLecturesTalksVenue.objects.get(id=q['v_id']), date=q['date'], topic=q['topic'], participants=q['participants'], time_stamp=q['t_date'])
        query = list(AchFacLecturesTalks.objects.filter(emp_id=q['emp_id'], category=q['category'], type_of_event=q['type'], organization_sector=q['organization_sector'], incorporation_status=q['incorporation_status'], role=q['role'], venue_detail=q['v_id'], date=q['date'], topic=q['topic'], participants=q['participants']).exclude(status="DELETE").values_list('id', flat=True))
        AchFacApproval.objects.create(level=1, approval_category='LECTURES AND TALKS', approval_id=query[0], approval_status=q['approve_status'], time_stamp=q['t_date'])
        # print("inserted")
    msg = 'Data sucessfully inserted'
    data = {'msg': msg}
    status = 200
    return JsonResponse(data, status=status, safe=False)


def ScriptsPatent(request):
    emp_id = request.session['hash1']
    qry = list(Patent.objects.values('id', 'emp_id', 'title', 'descreption', 'collaboration', 'company_name', 'incorporate_status', 'status', 'number', 'date', 'owner', 'approve_status', 't_date', 'level'))
    # patent_det_data1 = list(Patent.objects.values('title','descreption','number','status','level','owner'))
    patent_data_to_insert = []
    for p in qry:
        if p['status'] == 'fill':
            patent_check = GetPatentDetailsIdCheck(p, None, p['number'])
        elif p['status'] == 'grant':
            patent_check = GetPatentDetailsIdCheck(p, p['number'], None)
        level = p['level']
        level_id = list(AarDropdown.objects.filter(field='LEVEL', value=level).values_list('sno', flat=True))
        p['l_id'] = level_id[0]
        status = p['status']
        if status == 'fill':
            status_id = list(AarDropdown.objects.filter(field='STATUS', value='IF FILLED').values_list('sno', flat=True))
            p['application_no'] = p['number']
            p['patent_number'] = None
        elif status == 'grant':
            status_id = list(AarDropdown.objects.filter(field='STATUS', value='IF GRANTED').values_list('sno', flat=True))
            p['patent_number'] = p['number']
            p['application_no'] = None
        p['s_id'] = status_id[0]
        if len(patent_check) == 0:
            patent_data_to_insert.append(p)
    objs1 = (AchFacPatentDetail(patent_title=p['title'], patent_description=p['descreption'], level=AarDropdown.objects.get(sno=p['l_id']), patent_status=AarDropdown.objects.get(sno=p['s_id']), application_no=p['application_no'], patent_number=p['patent_number'], owner=AarDropdown.objects.get(sno=p['owner']))for p in patent_data_to_insert)
    q1 = AchFacPatentDetail.objects.bulk_create(objs1)

    # qry = list(Patent.objects.values('id','emp_id','title','descreption','collaboration','company_name','incorporate_status','status','number','date','owner','approve_status','t_date','level'))
    for q in qry:
        if q['status'] == 'fill':
            patent_id = GetPatentDetailsIdCheck(q, None, q['number'])
            q['p_id'] = patent_id[0]
        elif q['status'] == 'grant':
            patent_id = GetPatentDetailsIdCheck(q, q['number'], None)
            q['p_id'] = patent_id[0]
        AchFacPatents.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=q['emp_id']), patent_details=AchFacPatentDetail.objects.get(id=q['p_id']), patent_date=q['date'])
        query1 = list(AchFacPatents.objects.filter(emp_id=q['emp_id'], patent_details=q['p_id'], patent_date=q['date']).exclude(status="DELETE").values_list('id', flat=True))
        if q['collaboration'] == 'yes':
            AchFacPatentCollaborator.objects.create(patent_in=AchFacPatents.objects.get(id=query1[0]), company_name=q['company_name'], incorporate_status=AarDropdown.objects.get(sno=q['incorporate_status']))
        query2 = list(Discipline.objects.filter(id=q['id'], type='PATENT', emp_id=q['emp_id']).values('value1', 'value2'))
        detail_emp = []
        for dis in query2:
            if dis['value1'] != None:
                detail_emp.append(dis['value1'])
            elif dis['value2'] != None:
                query3 = list(EmployeePrimdetail.objects.filter(emp_id=q['emp_id']).values_list('dept', flat=True))
                detail_emp.append(query3[0])
        if len(query2) > 0:
            objs2 = (AchFacMultiDetails(details_for='PATENT', key_id=query1[0], detail_emp=EmployeeDropdown.objects.get(sno=d))for d in detail_emp)
            q2 = AchFacMultiDetails.objects.bulk_create(objs2)
        AchFacApproval.objects.create(level=1, approval_category='PATENT', approval_id=query1[0], approval_status=q['approve_status'], time_stamp=q['t_date'])
        # print("inserted")
    msg = 'Data sucessfully inserted'
    data = {'msg': msg}
    status = 200
    return JsonResponse(data, status=status, safe=False)


def ScriptsTraining(request):
    emp_id = request.session['hash1']
    qry = list(TrainingDevelopment.objects.values('id', 'emp_id', 'category', 'type', 'from_date', 'to_date', 'role', 'organization_sector', 'incorporation_status', 'title', 'venue', 'participants', 'organizers', 'attended', 'collaborations', 'sponsership', 'approve_status', 't_date'))
    for q in qry:
        if q['venue'] == 'KIET':
            query = list(AarDropdown.objects.filter(field='VENUE', value='KIET Group of Institutions').values_list('sno', flat=True))
            q['venue_id'] = query[0]
            q['venue_other'] = None
        else:
            query = list(AarDropdown.objects.filter(field='VENUE', value='Other').values_list('sno', flat=True))
            q['venue_id'] = query[0]
            q['venue_other'] = q['venue']
        AchFacTrainings.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=q['emp_id']), category=AarDropdown.objects.get(sno=q['category']), training_type=AarDropdown.objects.get(sno=q['type']), role=AarDropdown.objects.get(sno=q['role']), organization_sector=AarDropdown.objects.get(sno=q['organization_sector']), incorporation_type=AarDropdown.objects.get(sno=q['incorporation_status']), from_date=q['from_date'], to_date=q['to_date'], title=q['title'], venue=AarDropdown.objects.get(sno=q['venue_id']), venue_other=q['venue_other'], participants=q['participants'], organizers=q['organizers'], attended=q['attended'], collaborations=q['collaborations'], sponsership=q['sponsership'])
        query1 = list(AchFacTrainings.objects.filter(emp_id=q['emp_id'], category=q['category'], incorporation_type=q['incorporation_status'], training_type=q['type'], role=q['role'], organization_sector=q['organization_sector'], from_date=q['from_date'], to_date=q['to_date'], title=q['title'], venue=q['venue_id'], venue_other=q['venue_other'], participants=q['participants'], organizers=q['organizers'], attended=q['attended'], collaborations=q['collaborations'], sponsership=q['sponsership']).exclude(status="DELETE").values_list('id', flat=True))
        query2 = list(Discipline.objects.filter(id=q['id'], type='TRAINING', emp_id=q['emp_id']).values('value1', 'value2'))
        detail_emp = []
        for dis in query2:
            if dis['value1'] != None:
                detail_emp.append(dis['value1'])
            elif dis['value2'] != None:
                detail_emp.append(dis['value2'])
        if len(query2) > 0:
            objs1 = (AchFacMultiDetails(details_for='TRAINING AND DEVELOPMENT PROGRAM', key_id=query1[0], detail_emp=EmployeeDropdown.objects.get(sno=d))for d in detail_emp)
            q1 = AchFacMultiDetails.objects.bulk_create(objs1)
        if q['collaborations'] == 'yes':
            query3 = list(Sponsers.objects.filter(spons_id=q['id'], type='TRAINING', field_type='COLLABORATION').values('sponser_name', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
            collab_ids = []
            for collab in query3:
                collab_check = GetCollaboratorsIdCheck(collab)
                if len(collab_check) == 0:
                    AchFacCollaborators.objects.create(organisation=collab['sponser_name'], pin_code=collab['pin_code'], address=collab['address'], contact_person=collab['contact_person'], contact_number=collab['contact_number'], e_mail=collab['e_mail'], website=collab['website'], amount=collab['amount'])
                    collab_check1 = GetCollaboratorsIdCheck(collab)
                    collab_ids.append(collab_check1[0])
                else:
                    collab_ids.append(collab_check[0])
            objs2 = (AchFacMapIds(key_type='COLLABORATORS', key_id=c, form_id=query1[0], form_type='TRAINING AND DEVELOPMENT PROGRAM')for c in collab_ids)
            q2 = AchFacMapIds.objects.bulk_create(objs2)

        if q['sponsership'] == 'yes':
            query4 = list(Sponsers.objects.filter(spons_id=q['id'], type='TRAINING', field_type='SPONSOR').values('sponser_name', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
            sponser_ids = []
            for sponser in query4:
                sponser_check = GetSponsorsIdCheck(sponser)
                if len(sponser_check) == 0:
                    AchFacSponser.objects.create(organisation=sponser['sponser_name'], pin_code=sponser['pin_code'], address=sponser['address'], contact_person=sponser['contact_person'], contact_number=sponser['contact_number'], e_mail=sponser['e_mail'], website=sponser['website'], amount=sponser['amount'])
                    sponser_check1 = GetSponsorsIdCheck(sponser)
                    sponser_ids.append(sponser_check1[0])
                else:
                    sponser_ids.append(sponser_check[0])
            objs3 = (AchFacMapIds(key_type='SPONSORS', key_id=s, form_id=query1[0], form_type='TRAINING AND DEVELOPMENT PROGRAM')for s in sponser_ids)
            q3 = AchFacMapIds.objects.bulk_create(objs3)
        AchFacApproval.objects.create(level=1, approval_category='TRAINING AND DEVELOPMENT PROGRAM', approval_id=query1[0], approval_status=q['approve_status'], time_stamp=q['t_date'])
    msg = 'Data sucessfully inserted'
    data = {'msg': msg}
    status = 200
    return JsonResponse(data, status=status, safe=False)


def ScriptsProjects(request):
    emp_id = request.session['hash1']
    qry = list(ProjectConsultancy.objects.values('id', 'emp_id', 'type', 'status', 'sector', 'title', 'descreption', 'start_date', 'end_date', 'principal_investigator', 'co_principal_investigator', 'principal_investigator_id', 'co_principal_investigator_id', 'team_size', 'sponsored', 'association', 'approve_status', 't_date'))
    for q in qry:
        AchFacProjects.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=q['emp_id']), project_type=AarDropdown.objects.get(sno=q['type']), project_status=AarDropdown.objects.get(sno=q['status']), sector=AarDropdown.objects.get(sno=q['sector']), project_title=q['title'], project_description=q['descreption'], start_date=q['start_date'], end_date=q['end_date'], principal_investigator=q['principal_investigator'], co_principal_investigator=q['co_principal_investigator'], principal_investigator_other=q['principal_investigator_id'], co_principal_investigator_other=q['co_principal_investigator_id'], team_size=q['team_size'], sponsored=q['sponsored'], association=q['association'])
        query1 = list(AchFacProjects.objects.filter(emp_id=q['emp_id'], project_type=q['type'], project_status=q['status'], sector=q['sector'], project_title=q['title'], project_description=q['descreption'], start_date=q['start_date'], end_date=q['end_date'], principal_investigator=q['principal_investigator'], co_principal_investigator=q['co_principal_investigator'], principal_investigator_other=q['principal_investigator_id'], co_principal_investigator_other=q['co_principal_investigator_id'], team_size=q['team_size'], sponsored=q['sponsored'], association=q['association']).exclude(status="DELETE").values_list('id', flat=True))
        query2 = list(Discipline.objects.filter(id=q['id'], type='PROJECTS/CONSULTANCY', emp_id=q['emp_id']).values('value1', 'value2'))
        detail_emp = []
        for dis in query2:
            if dis['value1'] != None:
                detail_emp.append(dis['value1'])
            elif dis['value2'] != None:
                detail_emp.append(dis['value2'])
        if len(query2) > 0:
            objs1 = (AchFacMultiDetails(details_for='PROJECTS/CONSULTANCY', key_id=query1[0], detail_emp=EmployeeDropdown.objects.get(sno=d))for d in detail_emp)
            q1 = AchFacMultiDetails.objects.bulk_create(objs1)
        if q['association'] == 'yes':
            query3 = list(Sponsers.objects.filter(spons_id=q['id'], type='PROJECT', field_type='ASSOCIATION').values('sponser_name', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
            asso_ids = []
            for asso in query3:
                asso_check = GetAssociationsIdCheck(asso)
                if len(asso_check) == 0:
                    AchFacAssociations.objects.create(organisation=asso['sponser_name'], pin_code=asso['pin_code'], address=asso['address'], contact_person=asso['contact_person'], contact_number=asso['contact_number'], e_mail=asso['e_mail'], website=asso['website'], amount=asso['amount'])
                    asso_check1 = GetAssociationsIdCheck(asso)
                    asso_ids.append(asso_check1[0])
                else:
                    asso_ids.append(asso_check[0])
            objs2 = (AchFacMapIds(key_type='ASSOCIATIONS', key_id=a, form_id=query1[0], form_type='PROJECTS/CONSULTANCY')for a in asso_ids)
            q2 = AchFacMapIds.objects.bulk_create(objs2)

        if q['sponsored'] == 'yes':
            query4 = list(Sponsers.objects.filter(spons_id=q['id'], type='PROJECT', field_type='SPONSOR').values('sponser_name', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
            sponser_ids = []
            for sponser in query4:
                sponser_check = GetSponsorsIdCheck(sponser)
                if len(sponser_check) == 0:
                    AchFacSponser.objects.create(organisation=sponser['sponser_name'], pin_code=sponser['pin_code'], address=sponser['address'], contact_person=sponser['contact_person'], contact_number=sponser['contact_number'], e_mail=sponser['e_mail'], website=sponser['website'], amount=sponser['amount'])
                    sponser_check1 = GetSponsorsIdCheck(sponser)
                    sponser_ids.append(sponser_check1[0])
                else:
                    sponser_ids.append(sponser_check[0])
            objs2 = (AchFacMapIds(key_type='SPONSORS', key_id=s, form_id=query1[0], form_type='PROJECTS/CONSULTANCY')for s in sponser_ids)
            q2 = AchFacMapIds.objects.bulk_create(objs2)
        AchFacApproval.objects.create(level=1, approval_category='PROJECTS/CONSULTANCY', approval_id=query1[0], approval_status=q['approve_status'], time_stamp=q['t_date'])
        # print("inserted")
    msg = 'Data sucessfully inserted'
    data = {'msg': msg}
    status = 200
    return JsonResponse(data, status=status, safe=False)
