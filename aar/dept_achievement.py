# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
from django.shortcuts import render
import json
from django.http import JsonResponse
import datetime
from dateutil.relativedelta import relativedelta
import calendar
from django.db.models import Q
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from random import randint

from Accounts.models import AccountsDropdown, EmployeeGross_detail,AccountsSession,MonthlyPayable_detail
from aar.models import *
from login.models import AarDropdown,EmployeeDropdown
from musterroll.models import EmployeePrimdetail, EmployeeResearch, EmployeeAcademic, Reporting, AarReporting

from login.views import checkpermission
from Accounts.views import gross_payable_salary_components,getCurrentSession,stored_gross_payable_salary_components
#request.session['hash1']

def get_highest_qualification(emp_id):
    qr = EmployeeAcademic.objects.filter(emp_id=emp_id).values('pass_year_10','board_10','cgpa_per_10','pass_year_12','board_12','cgpa_per_12','pass_year_dip','univ_dip','cgpa_per_dip','pass_year_ug','univ_ug','degree_ug','cgpa_per_ug','pass_year_pg','univ_pg','degree_pg','cgpa_per_pg','area_spl_pg','doctrate','univ_doctrate','date_doctrate','stage_doctrate','research_topic_doctrate','degree_other','pass_year_other','univ_other','cgpa_per_other','area_spl_other','emp_id','area_spl_ug','dip_area','board_10__value','board_12__value','univ_dip__value','univ_ug__value','degree_ug__value','univ_pg__value','degree_pg__value','univ_doctrate__value','stage_doctrate__value','degree_other__value','univ_other__value',)
    highest_qualification="---"
    # print(qr)
    if qr is not None:
        r = qr[0]
        if r['doctrate']=='PD':
            try:
                highest_qualification = "PHD "
            except:
                highest_qualification = "PHD "

        else:
            if r['cgpa_per_pg']!=None:
                try:
                    if r['area_spl_pg'] != None:
                        highest_qualification = r['degree_pg__value']
                    else:
                        highest_qualification = r['degree_pg__value']
                except:
                    highest_qualification="Post Graduation"
            elif r['cgpa_per_pg']==None:
                if r['cgpa_per_ug']!=None:
                    if r['area_spl_ug'] != None:
                        if r['degree_ug__value'] != None:
                            highest_qualification = r['degree_ug__value']
                        else:
                            highest_qualification = "Graduation"
                    else:
                        highest_qualification = r['degree_ug__value']

                elif r['cgpa_per_ug']==None:
                    if r['cgpa_per_dip']!=None:
                        if r['dip_area'] != None:
                            highest_qualification = "Diploma"
                        else:
                            highest_qualification = "Diploma"
                    elif r['cgpa_per_dip']==None:
                        if(r['degree_other']!=None):
                            highest_qualification = r['degree_other__value']
                        else:
                            if r['cgpa_per_12']!=None:
                                highest_qualification = "12th"
                            elif r['cgpa_per_12']==None:
                                if r['cgpa_per_10']!=None:
                                    highest_qualification = "10th"
                                elif r['cgpa_per_10']==None:
                                    highest_qualification='----'
    return highest_qualification

def increament_status_pagal(emp_id):
    data={}
    proposed_increment=0
    proposed_increment_dir=0
    emp_data = EmployeePrimdetail.objects.filter(cadre__in = [667,668,669,645,643,644],emp_status='ACTIVE').values('emp_id','name','desg__value','dept__value','doj','ladder','desg','emp_category')
    session=getCurrentSession()
    qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=emp_id).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
    gross_salary=stored_gross_payable_salary_components(emp_id,getCurrentSession(),date.today().month-3)
    # #print(gross_salary.query)
    gross_salary_total = float()
    basic_agp=0
    for x in gross_salary:
        #print(emp_id,x['value'],x['gross_value'])
        gross_salary_total += x['gross_value']
        if(x['value']=='BASIC' or x['value']=='AGP'):
           basic_agp =basic_agp+x['gross_value']

    if len(qry_gross_value) == 0:
        data['scale_consolidates'] = '--'
        scale_consolidates=data['scale_consolidates']
    else:
        data['scale_consolidates']=qry_gross_value[0]['salary_type__value']
        scale_consolidates=data['scale_consolidates']
    proposed_inc = hodrecommendatedamount.objects.filter(emp_id=emp_id).values('amount','increment_type','increment_type__value','status','promoted_to','promotion_amount','increment')
    inc =  list(proposed_inc)
    if scale_consolidates == 'CONSOLIDATE':
        for j in inc:
            # #print('sjhbsb')
            data['increment_type__value']= j['increment_type__value']
            if j['status'] == 'INCREMENT':
                if j['increment_type'] == 276:
                    proposed_salary = AarIncrementSettings.objects.filter(ladder = emp_data[0]['ladder'],desg = emp_data[0]['desg'],emp_category = emp_data[0]['emp_category']).values('value')
                    value = list(proposed_salary)
                    for a in value:
                        propose_increment = a['value']
                        proposed_increment = (gross_salary_total * 8)/100
                if j['increment_type'] == 277:
                    proposed_increment = j['amount']
                    # #print "hiiiiiiiiii"
            elif j['status'] == 'PROMOTION':
                if j['increment'] == 'Y':
                    proposed_increment = j['promotion_amount']
                elif j['increment'] == 'N':
                    proposed_increment = 0
            elif j['status'] == 'NO INCREMENT':
                proposed_increment = 0
            status1 = j['status']
    elif scale_consolidates == 'GRADE':
        #print inc
        for j in inc:
            data['increment_type__value']= j['increment_type__value']
            if j['status'] == 'INCREMENT':
                if j['increment_type'] == 276:
                    proposed_salary = AarIncrementSettings.objects.filter(ladder = emp_data[0]['ladder'],desg = emp_data[0]['desg'],emp_category = emp_data[0]['emp_category']).values('value')
                    value = list(proposed_salary)
                    for a in value:
                        propose_increment = a['value']
                        #proposed_increment = (basic_agp * 3)/100
                        proposed_increment = (gross_salary_total * 3)/100
                if j['increment_type'] == 277:
                    proposed_increment = j['amount']
                    # #print "hiiiiiiiiii"
            elif j['status'] == 'PROMOTION':
                if j['increment'] == 'Y':
                    proposed_increment = j['promotion_amount']
                elif j['increment'] == 'N':
                    proposed_increment = 0
            elif j['status'] == 'NO INCREMENT':
                proposed_increment = 0
            status1 = j['status']
    # #print('kjhdkd')
    proposed_inc_dir = AarPart2MarksDir.objects.filter(emp_id=emp_id).values('amount','increment_type','increment_type__value','increment_type','status','promoted_to','promotion_amount','increment','remarks')
    inc_dir =  list(proposed_inc_dir)
    if scale_consolidates == 'CONSOLIDATE':
        proposed_increment_dir = '--'
        status2 = '--'
        remarks_dir = '--'
        for j in inc_dir:
            data['increment_type_dir']= j['increment_type__value']
            if j['status'] == 'INCREMENT':
                if j['increment_type'] == 276:
                    proposed_salary_dir = AarIncrementSettings.objects.filter(ladder = emp_data[0]['ladder'],desg = emp_data[0]['desg'],emp_category = emp_data[0]['emp_category']).values('value')
                    value = list(proposed_salary_dir)
                    for a in value:
                        propose_increment_dir = a['value']
                        proposed_increment_dir = (gross_salary_total * 8)/100
                if j['increment_type'] == 277:
                    # #print "tanya"
                    proposed_increment_dir = j['amount']
                    # #print proposed_increment_dir
            elif j['status'] == 'PROMOTION':
                if j['increment'] == 'Y':
                    proposed_increment_dir = j['promotion_amount']
                elif j['increment'] == 'N':
                    proposed_increment_dir = 0
            elif j['status'] == 'NO INCREMENT':
                proposed_increment_dir = 0
            status2 = j['status']
            remarks_dir = j['remarks']
    elif scale_consolidates == 'GRADE':
        proposed_increment_dir = '--'
        status2 = '--'
        remarks_dir = '--'
        for j in inc_dir:
            data['increment_type_dir']= j['increment_type__value']
            if j['status'] == 'INCREMENT':
                if j['increment_type'] == 276:
                    proposed_salary_dir = AarIncrementSettings.objects.filter(ladder = emp_data[0]['ladder'],desg = emp_data[0]['desg'],emp_category = emp_data[0]['emp_category']).values('value')
                    value = list(proposed_salary_dir)
                    for a in value:
                        propose_increment_dir = a['value']
                        proposed_increment_dir = (basic_agp * 3)/100
                if j['increment_type'] == 277:
                    proposed_increment_dir = j['amount']
                    # #print "hiiiiiiiiii"
            elif j['status'] == 'PROMOTION':
                if j['increment'] == 'Y':
                    proposed_increment_dir = j['promotion_amount']
                elif j['increment'] == 'N':
                    proposed_increment_dir = 0
            elif j['status'] == 'NO INCREMENT':
                proposed_increment_dir = 0
            else:
                proposed_increment_dir = '--'
            status2 = j['status']
            remarks_dir = j['remarks']
    else:
        proposed_increment_dir = '--'
        status2 = '--'
    #print('hgjbdkbbk')
    data=[proposed_increment_dir,proposed_increment]
    #print(data)

    return  data

def get_total_experience(emp_id):
    query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
    exp = relativedelta(date.today(), query2[0]['doj'])
    years = exp.years
    months = exp.months
    days = exp.days
    query_research = EmployeeResearch.objects.filter(emp_id=emp_id).values('research_years', 'research_months', 'industry_years', 'industry_months', 'teaching_years', 'teaching_months')
    total_exp2 = int()
    total_year = query_research[0]['research_years'] + query_research[0]['industry_years'] + query_research[0]['teaching_years']
    total_month = query_research[0]['research_months'] + query_research[0]['industry_months'] + query_research[0]['teaching_months']
    total_year1 = int(years) + int(total_year)
    ##print str(total_year1)
    total_month1 = int(months) + int(total_month)
    ##print str(total_month1)
    if(total_month1 % 12 == 0):
        c = total_month1 / 12
        total_year1 = total_year1 + c
        total_month1 = 0
    else:
        p = total_month1 % 12
        y = total_month1 / 12
        total_year1 = total_year1 + y
        total_month1 = p
    total_exp = str(total_year1) + " Years " + str(total_month1) + " Months "
    return total_exp

def GuestLecture(request):
    data_values=""
    data=""
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values=list(q)
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))

                    if 'date' in data:
                        date=data['date']
                    else:
                        date=None
                    if 'topic' in data:
                        topic=data['topic']
                    else:
                        topic=None
                    if 'speaker' in data:
                        speaker=data['speaker']
                    else:
                        speaker=None
                    if 'designation' in data:
                        designation=data['designation']
                    else:
                        designation=None
                    if 'organization' in data:
                        organization=data['organization']
                    else:
                        organization=None
                    if 'speaker_profile' in data:
                        speaker_profile=data['speaker_profile']
                    else:
                        speaker_profile=None
                    if 'contact_number' in data:
                        contact_number=data['contact_number']
                    else:
                        contact_number=None
                    if 'e_mail' in data:
                        e_mail=data['e_mail']
                    else:
                        e_mail=None
                    if 'participants_no' in data:
                        participants_no=data['participants_no']
                    else:
                        participants_no=None
                    if 'remark' in data:
                        remark=data['remark']
                    else:
                        remark=None
                    if 'dept' in data:
                        dept=data['dept']
                    else:
                        dept=None
                    if 'year' in data:
                        year=data['year']
                    else:
                        year=None
                    d= date.split('T')
                    date =datetime.datetime.strptime(d[0],'%Y-%m-%d').date()
                    dup=guestLectures.objects.filter(emp_id=emp_id,topic=topic)
                    if dup.count()==0:
                        Q=guestLectures.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),remark=remark,participants_no=participants_no,e_mail=e_mail,contact_number=contact_number,speaker_profile=speaker_profile,organization=organization,date=date,topic=topic,speaker=speaker,designation=designation)
                        sno=Q.pk
                        for i in dept:
                            AarMultiselect.objects.create(type="GUEST LECTURE",field="DEPARTMENT",value=i,emp_id=emp_id,sno=sno)
                        for i in year:
                            AarMultiselect.objects.create(type="GUEST LECTURE",field="YEAR",value=i,emp_id=emp_id,sno=sno)
                        data_values={"OK":"DATA Inserted Successfully"}
                        status=200
                    else:
                        data_values={"OK":"Duplicate Data"}
                        status=409
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

# def IndustrialVisit(request):
#     data_values=""
#     data=""
#     data_values={}
#     if 'HTTP_COOKIE' in request.META:
#         if request.user.is_authenticated:
#             check = checkpermission(request,[337])
#             if(check == 200):
#                 emp_id=request.session['hash1']
#                 if(request.method=='GET'):
#                     dept=request.GET['dept']

#                        # emp_list=EmployeePrimdetail.objects.
#                 else:
#                     status=502
#             else:
#                 status=403
#         else:
#             status=401
#     else:
#         status=500
#     return JsonResponse(data_values,safe=False,status=status)

def IndustrialVisit(request):
    data_values=""
    data=""
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                    emp=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('name','emp_id')

                    data_values=list(emp)
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))

                    if 'date' in data:
                        date=data['date']
                    else:
                        date=None
                    if 'industry' in data:
                        industry=data['industry']
                    else:
                        industry=None
                    if 'address' in data:
                        address=data['address']
                    else:
                        address=None
                    if 'contact_person' in data:
                        contact_person=data['contact_person']
                    else:
                        contact_person=None
                    if 'faculty_coordinator' in data:
                        faculty_coordinator=data['faculty_coordinator']
                    else:
                        faculty_coordinator=None
                    if 'contact_number' in data:
                        contact_number=data['contact_number']
                    else:
                        contact_number=None
                    if 'e_mail' in data:
                        e_mail=data['e_mail']
                    else:
                        e_mail=None
                    if 'participants_no' in data:
                        participants_no=data['participants_no']
                    else:
                        participants_no=None
                    if 'remark' in data:
                        remark=data['remark']
                    else:
                        remark=None

                    if 'year' in data:
                        year=data['year']
                    else:
                        year=None
                    d=date.split('T')
                    date=datetime.datetime.strptime(d[0],'%Y-%m-%d').date()
                    dup=industrialVisit.objects.filter(industry=industry,emp_id=emp_id)
                    ##print date
                    if dup.count()==0:
                        Q=industrialVisit.objects.create(t_date=str(datetime.datetime.now()),date=date,address=address,contact_person=contact_person,contact_number=contact_number,e_mail=e_mail,participants_no=participants_no,remark=remark,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),industry=industry)
                        sno=Q.pk
                        for i in faculty_coordinator:
                                AarMultiselect.objects.create(type="INDUSTRIAL VISIT",field="FACULTY COORDINATOR",value=i,emp_id=emp_id,sno=sno)
                        for i in year:
                            AarMultiselect.objects.create(type="INDUSTRIAL VISIT",field="YEAR",value=i,emp_id=emp_id,sno=sno)
                        data_values={"OK":"DATA Inserted Successfully"}
                        status=200
                    else:
                        data_values={"OK":"Duplicate Data"}
                        status=409
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def EventsOrganized(request):
    data_values=""
    data=""
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q1=AarDropdown.objects.filter(field="EVENTS_ORGANIZED").exclude(value=None).values('sno','value')
                    a=[]
                    for i in q1:
                        q2=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('value','sno')
                        a.append({i['value']:list(q2)})
                    q2=EmployeeDropdown.objects.filter(field='DEPARTMENT').exclude(value=None).values('sno','value')
                    data_values={'data':a,'data1':list(q2)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    ##print data
                    if data is not None:
                        
                        if 'category' in data:
                            category=data['category']
                        else:
                            category=None
                        if 'type' in data:
                            type_=data['type']
                        else:
                            type_=None
                        if 'from_date' in data:
                            from_date=data['from_date']
                        else:
                            from_date=None
                        if 'to_date' in data:
                            to_date=data['to_date']
                        else:
                            to_date=None
                        if 'organization' in data:
                            organization_sector=data['organization']
                        else:
                            organization_sector=None
                        if 'incorporation' in data:
                            incorporate_status=data['incorporation']
                        else:
                            incorporate_status=None
                        if 'title' in data:
                            title=data['title']
                        else:
                            title=None
                        if 'Venue' in data:
                            venue=data['Venue']
                        else:
                            venue=None
                        if 'participants' in data:
                            participants=data['participants']
                        else:
                            participants=None
                        if 'organizers' in data:
                            organizers=data['organizers']
                        else:
                            organizers=None
                        if 'attended' in data:
                            attended=data['attended']
                        else:
                            attended=None
                        if 'collaboration' in data:
                            collaboration=data['collaboration']
                        else:
                            collaboration=None
                        if 'collaborations' in data:
                            collaborations=data['collaborations']
                        else:
                            collaborations=None
                        if 'sponsered' in data:
                            sponsered=data['sponsered']
                        else:
                            sponsered=None
                        if 'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers=None
                        if 'description' in data:
                            description=data['description']
                        else:
                            description=None
                        if 'discipline' in data:
                            discipline=data['discipline']
                        else:
                            discipline=None
                        d1=from_date.split('T')
                        from_date=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        d2=to_date.split('T')
                        to_date=datetime.datetime.strptime(d2[0],'%Y-%m-%d').date()
                        c=eventsorganized.objects.filter(title=title,emp_id=emp_id).count()
                        if c==0:
                            Q=eventsorganized.objects.create(title=title,venue=venue,sponsership=sponsered,collaboration=collaboration,description=description,attended=attended,organizers=organizers,participants=participants,t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type_),from_date=from_date,to_date=to_date,organization_sector=AarDropdown.objects.get(sno=organization_sector),incorporation_status=AarDropdown.objects.get(sno=incorporate_status))
                            sno=Q.pk
                            for i in discipline:
                                AarMultiselect.objects.create(type="EVENTS_ORGANIZED",field="DISCIPLINE",value=i,emp_id=emp_id,sno=sno)
                            if(sponsered=="Yes"):
                                ponsers
                                for i in sponsers:
                                    Sponsers.objects.create(spons_id=sno,emp_id=emp_id,sponser_name=i["organisation"],type="EVENTS",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='SPONSOR')
                            if(collaboration=="Yes"):
                                for i in collaborations:
                                    Sponsers.objects.create(spons_id=sno,emp_id=emp_id,sponser_name=i["organisation"],type="EVENTS",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='COLLABORATION')
                            data_values={"OK":"DATA Inserted Successfully"}
                            status=200
                        else:
                            data_values={"OK":"duplicate data"}
                            status=409
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def mou(request):
    data_values=""
    data=""
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    ##print request.body
                    if data is not None:
                        if 'date' in data:
                            date=data['date']
                        else:
                            date=None
                        if 'organization' in data:
                            organization=data['organization']
                        else:
                            organization=None
                        if 'objective' in data:
                            objective=data['objective']
                        else:
                            objective=None
                        if 'valid_upto' in data:
                            valid_upto=data['valid_upto']
                        else:
                            valid_upto=None
                        if 'contact_number' in data:
                            contact_number=data['contact_number']
                        else:
                            contact_number=None
                        if 'e_mail' in data:
                            e_mail=data['e_mail']
                        else:
                            e_mail=None
                        if 'document' in data:
                            document=data['document']
                        else:
                            document=None
                        d1=valid_upto.split('T')
                        valid_upto=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        d2=date.split('T')
                        date=datetime.datetime.strptime(d2[0],'%Y-%m-%d').date()
                        MouSigned.objects.create(date=date,t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),document=document,e_mail=e_mail,organization=organization,objective=objective,valid_upto=valid_upto,contact_number=contact_number)
                        data_values={'ok':'Successfully added'}
                        status=200

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def Achievements(request):
    data_values={}
    data=""
    ###print "hiii"
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                ###print emp_id
                if(request.method=='POST'):
                    ##print "hii"
                    data=json.loads(request.body.decode("utf-8"))
                    ##print data
                    if data!=None:
                        if 'category' in data:
                            category=data['category']
                        else:
                            category=None
                        if 'description' in data:
                            description=data['description']
                        else:
                            description=None
                        if 'date' in data:
                            date = data['date']

                        else:
                            date=None
                        if data['type']=='STUDENT':
                            Q=Achievement.objects.filter(category=AarDropdown.objects.get(sno=category),description=description,emp_id=emp_id,type='STUDENT').count()
                            if Q==0:
                                Achievement.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),type='STUDENT',category=AarDropdown.objects.get(sno=category),description=description,date=date)
                                data_values={'ok':'data inserted'}
                                status=200
                            else:
                                data_values={'ok':'duplicate data'}
                                status=409
                        elif data['type']=='DEPARTMENT':
                            Q=Achievement.objects.filter(category=AarDropdown.objects.get(sno=category),description=description,emp_id=emp_id,type='DEPARTMENT').count()
                            if Q==0:
                                Achievement.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),type='DEPARTMENT',category=AarDropdown.objects.get(sno=category),description=description,date=date)
                                data_values={'ok':'data inserted'}
                                status=200
                            else:
                                data_values={'ok':'duplicate data'}
                                status=409
                elif(request.method=='GET'):
                    # ##print request.GET
                    if(request.GET['type']=='STUDENT'):
                        d=AarDropdown.objects.filter(field='STUDENTS ACHIEVEMENT').exclude(value=None).values('sno','value')
                        a=[]
                        for i in d:
                            query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                            a.append({i['value']:list(query1)})
                    if(request.GET['type']=='DEPARTMENT'):
                        d=AarDropdown.objects.filter(field='DEPARTMENTAL ACHIEVEMENT').exclude(value=None).values('sno','value')
                        a=[]
                        for i in d:
                            query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                            a.append({i['value']:list(query1)})
                    data_values={'data':a}
                    status=200

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def Schools(request):
    data_values={}
    data=""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                    emp=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('name','emp_id')
                    ##print emp
                    data_values=list(emp)
                    status=200
                elif(request.method=='POST'):
                    ###print emp_id
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        if 'start_date' in data:
                            start_date=data['start_date']
                        else:
                            start_date=None
                        if 'end_date' in data:
                            end_date=data['end_date']
                        else:
                            end_date=None
                        if 'resource_person' in data:
                            resource_person=data['resource_person']
                        else:
                            resource_person=None
                        if 'resource_person_name' in data:
                            resource_person_name=data['resource_person_name']
                        else:
                            resource_person_name=None
                        if 'topic' in data:
                            topic=data['topic']
                        else:
                            topic=None
                        if 'participant_number' in data:
                            participant_number=data['participant_number']
                        else:
                            participant_number=None
                        if 'participant_fee' in data:
                            participant_fee=data['participant_fee']
                        else:
                            participant_fee=None
                        d_s=start_date.split('T')
                        start_date=datetime.datetime.strptime(d_s[0],'%Y-%m-%d').date()
                        d_e=end_date.split('T')
                        end_date=datetime.datetime.strptime(d_e[0],'%Y-%m-%d').date()
                        q=SummerWinterSchool.objects.filter(topic=topic,emp_id=emp_id).count()
                        ###print emp_id
                        if q==0:
                            SummerWinterSchool.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),start_date=start_date,end_date=end_date,resource_person=resource_person,topic=topic,participant_number=participant_number,participant_fee=participant_fee)
                            data_values={'ok':'data inserted'}
                            status=200
                        else:
                            data_values={"ok":"duplicate"}
                            status=409
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def hobbyclub(request):
    data_values={}
    data=""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        if 'start_date' in data:
                            start_date=data['start_date']
                        else:
                            start_date=None
                        if 'end_date' in data:
                            end_date=data['end_date']
                        else:
                            end_date=None
                        if 'club_name' in data:
                            club_name=data['club_name']
                        else:
                            club_name=None
                        if 'project_title' in data:
                            project_title=data['project_title']
                        else:
                            project_title=None
                        if 'project_incharge' in data:
                            project_incharge=data['project_incharge']
                        else:
                            project_incharge=None
                        if 'team_size' in data:
                            team_size=data['team_size']
                        else:
                            team_size=None
                        if 'project_description' in data:
                            project_description=data['project_description']
                        else:
                            project_description=None
                        if 'project_cost' in data:
                            project_cost=data['project_cost']
                        else:
                            project_cost=None
                        if 'project_outcome' in data:
                            project_outcome=data['project_outcome']
                        else:
                            project_outcome=None
                        if 'coord' in data:
                            coord=data['coord']
                        else:
                            coord=None
                        ##print data
                        d1=start_date.split('T')
                        start_date=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        d2=end_date.split('T')
                        end_date=datetime.datetime.strptime(d2[0],'%Y-%m-%d').date()
                        c=Hobbyclub.objects.filter(emp_id=emp_id,start_date=start_date,end_date=end_date).count()
                        if c==0:
                            Q=Hobbyclub.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),project_outcome=project_outcome,project_cost=project_cost,project_description=project_description,team_size=team_size,project_incharge=EmployeePrimdetail.objects.get(emp_id=project_incharge),start_date=start_date,end_date=end_date,club_name=AarDropdown.objects.get(sno=club_name),project_title=project_title)
                            sno=Q.pk
                            for i in coord:
                                AarMultiselect.objects.create(type='HOBBY_CLUB',field="PROJECT FACULTY COORDINATOR",value=i,emp_id=emp_id,sno=sno)
                            data_values={"ok":"data inserted"}
                            status=200
                        else:
                            data_values={"ok":"duplicate data"}
                            status=409
                elif(request.method=='GET'):
                    d=AarDropdown.objects.filter(field="HOBBY_CLUB").exclude(value=None).values('sno','value')
                    dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                    emp=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('name','emp_id')
                    ##print d
                    data_values={'data1':list(d),'data2':list(emp)}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def update_departmental_aar(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='GET'):
                    if request.GET['check']=='GUEST':
                        if request.GET['check2']=='1':
                            emp_id=request.session['hash1']
                            s=guestLectures.objects.filter(emp_id=emp_id).values('id','topic','speaker')
                            status=200
                            data_values={'data':list(s)}
                        if request.GET['check2']=='2':
                            ##print request.GET
                            id=request.GET['id']
                            q=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                            query_data=guestLectures.objects.filter(id=id).values('emp_id','date','topic','speaker','designation','organization','speaker_profile','contact_number','e_mail','participants_no','remark')
                            query=AarMultiselect.objects.filter(sno=id,type='GUEST LECTURE',field='YEAR').values('value')
                            ##print query_data
                            status=200
                            data_values={'dept':list(q),'data':list(query_data),'data1':list(query)}
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    ##print data
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=200)
# check=conferance check2=2 id=id paper_title
def index_update(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='GET'):

                    if request.GET['check']=='JOURNAL':
                        if request.GET['check2']=='1':
                            emp_id=request.session['hash1']
                            s=Researchjournal.objects.filter(emp_id=emp_id).exclude(approve_status='REJECTED').exclude(approve_status='DELETE').exclude(approve_status='APPROVED').values('id','journal_name','isbn','approve_status','paper_title')
                            status=200
                            data_values={'data':list(s)}
                        if request.GET['check2']=='2': #data of user and other data
                            emp_id=request.session['hash1']
                            id=request.GET['id']
                            # paper_title=request.GET['paper_title']
                            d=AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            s=Researchjournal.objects.filter(emp_id=emp_id,id=id).values('id','category__value','type_of_journal__value','sub_category__value','published_date','paper_title','impact_factor','journal_name','volume_no','issue_no','isbn','page_no','author','author__value','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website')
                            status=200
                            data_values={'data1':list(s),'data2':list(a)}


                    if request.GET['check']=='CONFERANCE':
                        if request.GET['check2']=='1':#sending books
                            emp_id=request.session['hash1']
                            s=Researchconference.objects.filter(emp_id=emp_id).exclude(approve_status='DELETE').exclude(approve_status='REJECTED').exclude(approve_status='APPROVED').values('journal_name','isbn','approve_status','paper_title','conference_title','id')
                            status=200
                            data_values={'data':list(s)}
                        if request.GET['check2']=='2':#data of user and other data
                            emp_id=request.session['hash1']
                            id=request.GET['id']
                            d=AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE').exclude(value=None).values('sno','value')
                            a=[]
                            authing=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                if(i['value']=="AUTHOR"):
                                    authin=list(query1)
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            s=Researchconference.objects.filter(emp_id=emp_id,id=id).values('id','emp_id','category__value','type_of_conference__value','sub_category__value','conference_title','paper_title','published_date','organized_by','journal_name','volume_no','issue_no','isbn','page_no','author__value','author','conference_from','conference_to','other_description','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','sponsered','others')
                            sno=s[0]['id']
                            sp=Sponsers.objects.filter(spons_id=sno,type='CONFERENCE').values('sponser_name')
                            status=200
                            data_values={'data1':list(s),'data2':a,'data3':list(sp),'data':authin}

                    if request.GET['check']=='GUIDANCE':
                        if request.GET['check2']=='1':
                            emp_id=request.session['hash1']
                            d=AarDropdown.objects.filter(field='GUIDANCE').exclude(value=None).values('sno','value')
                            s=Researchguidence.objects.filter(emp_id=emp_id).exclude(approve_status='DELETE').exclude(approve_status='REJECTED').exclude(approve_status='APPROVED').values('emp_id','guidence','guidence__value','project_title','area_of_spec','uni_name','uni_type__value','id','uni_type','approve_status')
                            data_values={'data':list(d),'data1':list(s)}
                            status=200
                        if request.GET['check2']=='2':
                            if request.GET['data']=='70' or request.GET['data']=='71' or request.GET['data']=='72':
                                emp_id=request.session['hash1']
                                s=Researchguidence.objects.filter(emp_id=emp_id,guidence=request.GET['data']).values('emp_id','guidence__value','project_title','area_of_spec','uni_name','uni_type__value','id','uni_type')
                                data_values={'data':list(s)}
                                status=200
                        if request.GET['check2']=='3':
                            if request.GET['data']=='70':
                                emp_id=request.session['hash1']
                                a=[]
                                sno=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='COURSES').exclude(value=None).values('sno')
                                s1=AarDropdown.objects.filter(pid=sno).exclude(value=None).values('value','sno')
                                s2=Researchguidence.objects.filter(emp_id=emp_id,guidence=request.GET['data']).values('date','emp_id','guidence__value','course__value','degree__value','no_of_students','degree_awarded','status__value','project_title','area_of_spec','uni_name','uni_type__value','id','uni_type')
                                data_values={'data1':list(s1),'data2':list(s2)}
                                status=200
                            if request.GET['data']=='71':
                                emp_id=request.session['hash1']
                                a=[]
                                sno=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='DEGREE').exclude(value=None).values('sno')
                                s1=AarDropdown.objects.filter(pid=sno).exclude(value=None).values('value','sno')
                                sno1=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='UNIVERSITY TYPE').exclude(value=None).values('sno')
                                s3=AarDropdown.objects.filter(pid=sno1).exclude(value=None).values('value','sno')
                                s2=Researchguidence.objects.filter(emp_id=emp_id,guidence=request.GET['data']).values('date','emp_id','guidence__value','course__value','degree__value','no_of_students','degree_awarded','status__value','project_title','area_of_spec','uni_name','uni_type__value','id','uni_type')
                                data_values={'data1':list(s1),'data2':list(s2),'data3':list(s3)}
                                status=200
                            if request.GET['data']=='72':
                                emp_id=request.session['hash1']
                                s1=AarDropdown.objects.filter(pid=request.GET['data']).exclude(value=None).values('value','sno')
                                sno1=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='UNIVERSITY TYPE').exclude(value=None).values('sno')
                                s3=AarDropdown.objects.filter(pid=sno1).exclude(value=None).values('value','sno')
                                s2=Researchguidence.objects.filter(emp_id=emp_id,guidence=request.GET['data']).values('date','emp_id','guidence__value','course__value','degree__value','no_of_students','degree_awarded','status__value','project_title','area_of_spec','uni_name','uni_type__value','id','uni_type')
                                data_values={'data1':list(s1),'data2':list(s2),'data3':list(s3)}
                                status=200


                    if request.GET['check']=='BOOK':
                        if request.GET['check2']=='1':
                            emp_id=request.session['hash1']
                            s=Books.objects.filter(emp_id=emp_id).exclude(approve_status='DELETE').exclude(approve_status='REJECTED').exclude(approve_status='APPROVED').values('id','title','isbn','chapter','approve_status')
                            status=200
                            data_values={'data':list(s)}
                        if request.GET['check2']=='2':
                            emp_id=request.session['hash1']
                            isbn=request.GET['isbn']
                            s=Books.objects.filter(emp_id=emp_id,isbn=isbn).values('id','emp_id','role__value','role_for__value','publisher_type__value','title','edition','published_date','chapter','isbn','copyright_status','copyright_no','author__sno','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website')
                            d=AarDropdown.objects.filter(field='BOOKS').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            data_values={'data':list(s),'data2':list(a)}


                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    print(data_values)

    return JsonResponse(data_values,safe=False,status=status)

def Update_Guidence(request):
    data_values=""
    data=""
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data is not None:
                        course=data['Course']
                        degree=data['Degree']
                        degree_awarded=data['Degree_awarded']
                        guid=data['Guidance']
                        no_stud=data['No_of_Students']
                        a_o_s=data['area_of_specialization']
                        title=data['project_title']
                        status=data['status']
                        emp_id=request.session["hash1"]
                        date=data['date']
                        if guid:
                            if(course!=None):
                                Researchguidence.objects.filter(id=data['id'],guidence=guid,emp_id=emp_id,project_title=title).update(guidence=AarDropdown.objects.get(sno=guid),course=AarDropdown.objects.get(sno=course),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date)
                                data_values={"OK":"COURSE Inserted Successfully"}

                            elif(degree!=None):
                                ##print guid
                                Researchguidence.objects.filter(id=data['id'],guidence=guid,emp_id=emp_id,project_title=title).update(guidence=AarDropdown.objects.get(sno=guid),degree=AarDropdown.objects.get(sno=degree),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date)
                                data_values={"OK":"DEGREE Inserted Successfully"}

                            elif(status!=None):
                                Researchguidence.objects.filter(id=data['id'],guidence=guid,emp_id=emp_id,project_title=title).update(guidence=AarDropdown.objects.get(sno=guid),status=AarDropdown.objects.get(sno=status),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date)
                                data_values={"OK":"STATUS Inserted Successfully"}
                        status=200
                    else:
                        status=202
                        data_values={"msg":"Data not filled completed"}
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=200)

def Update_Book(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body)
                    id=data['id']
                    role=data['role']
                    for_type=data['for_type']
                    publisher=data['publisher']
                    copyright_no=data['copyright_no']
                    copyright_status=data['copyright_status']
                    if 'title' in data:
                        title=data['title']
                    else:
                        title=None
                    if 'chapter' in data:
                        chapter=data['chapter']
                    else:
                        chapter=None
                    publisher_name=data['publisher_name']
                    publisher_add=data['publisher_add']
                    edition=data['edition']
                    date=data['date']
                    publisher_email=data['publisher_email']
                    author=data['author']
                    publisher_website=data['publisher_website']
                    isbn=data['isbn']
                    publisher_code=data['publisher_code']
                    publisher_contact=data['publisher_contact']
                    emp_id=request.session['hash1']
                    role_type_new=AarDropdown.objects.get(sno=role)
                    for_type_new=AarDropdown.objects.get(sno=for_type)
                    publisher_new=AarDropdown.objects.get(sno=publisher)
                    author_new=AarDropdown.objects.get(sno=author)
                    date=date.split('T')
                    date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                    Books.objects.filter(id=id).update(role=role_type_new,role_for=for_type_new,publisher_type=publisher_new,title=title,edition=edition,published_date=date,chapter=chapter,isbn=isbn,copyright_status=copyright_status,copyright_no=copyright_no,author=author_new,publisher_name=publisher_name,publisher_address=publisher_add,publisher_zip_code=publisher_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website)
                    data_values={'data_values':"Data Successfully updated"}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def Update_Journal(request):
    data_values={}
    data=""
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        id=data["id"]
                        category=data["category"]
                        emp_id=request.session['hash1']
                        type_of_journal=data["typeofjournal"]
                        sub_category=data["subcategory"]
                        paper_title=data["papertitle"]
                        impact_factor=data["impacttext"]
                        published_date=data["dateofpub"]
                        journal_name=data["journalname"]
                        volume_no=data["volumeno"]
                        issue_no=data["issueno"]
                        isbn=data["isbn"]
                        page_no=data["pageno"]
                        author=data["typeofAuthor"]
                        #author=23
                        publisher_name=data["publishername"]
                        publisher_address1=data["publisheraddL1"]
                        publisher_address2=data["publisheraddL2"]
                        publisher_zip_code=data["zipc"]
                        publisher_contact=data["phone"]
                        publisher_email=data["eml"]
                        publisher_website=data["website"]
                        if 'subcatText' in data:
                            others=data["subcatText"]
                        else:
                            others = None
                        c=0
                        auth=Researchjournal.objects.filter(isbn=isbn).exclude(emp_id=emp_id).values('author')
                        if(auth.count()>0):
                            check_auth=AarDropdown.objects.filter(sno=author).values('value')
                            ##print check_auth
                            if check_auth[0]["value"]=="FIRST AUTHOR":
                                for i in auth:
                                    is_author1=AarDropdown.objects.filter(sno=i["author"]).values('value')
                                    if(is_author1[0]["value"]=="FIRST AUTHOR"):
                                        c=1
                                        break
                        if(c==0):
                            Researchjournal.objects.filter(id=id).update(category=AarDropdown.objects.get(sno=category),author=AarDropdown.objects.get(sno=author),type_of_journal=AarDropdown.objects.get(sno=type_of_journal),sub_category=AarDropdown.objects.get(sno=sub_category),others=others,paper_title=paper_title,published_date=published_date,impact_factor=impact_factor,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,publisher_name=publisher_name,publisher_address1=publisher_address1,publisher_address2=publisher_address2,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,emp_id=emp_id)
                            data_values={"OK":"DATA updated Successfully"}
                        else:
                            status=409
                            data_values={"OK":"failed"}
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=200)

def Update_Conferance(request):
    data_values=""
    data=""
    data_values={}
    # ##print request.body
    ##print data
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body)
                    print(data)
                    if data!=None:
                        id=data["id"]
                        category=data["category"]
                        emp_id=request.session['hash1']
                        type_of_conference=data["type"]
                        sub_category=data["subCategory"]
                        sponsered=data["sponsered"]
                        sponsers=data['sponsers']
                        conference_title=data["titleConference"]
                        paper_title=data["titlePaper"]
                        published_date=data["dateOfPublish"]
                        organized_by=data["organised"]

                        if  'volume' in data:
                            volume_no=data["volume"]
                        else:
                            volume_no=None

                        if  'page' in data:
                            page_no=data["page"]
                        else:
                            page_no=None

                        if  'journalName' in data:
                            journal_name=data["journalName"]
                        else:
                            journal_name=None

                        if  'issue' in data:
                            issue_no=data["issue"]
                        else:
                            issue_no=None

                        if  'issn' in data:
                            isbn=data["issn"]
                        else:
                            isbn=None
                        author=data["author"]
                        conference_from=data["fromDate"]
                        conference_to=data["toDate"]
                        other_description=data["description"]
                        publisher_name=data["publisherName"]
                        publisher_address=data["publisherAddress"]
                        publisher_zip_code=data["publisherPincode"]
                        publisher_contact=data["publisherContact"]
                        publisher_email=data["publisherEmail"]
                        publisher_website=data["publisherWebsite"]
                        published_date=data["dateOfPublish"]
                        others=data["others"]
                        c=0
                        auth=Researchconference.objects.filter(id=id).exclude(emp_id=emp_id).values('author')
                        if(auth.count()>0):
                            check_auth=AarDropdown.objects.filter(sno=author).values('value')
                            if check_auth[0]["value"]=="FIRST AUTHOR":
                                for i in auth:
                                    is_author1=AarDropdown.objects.filter(sno=i["author"]).values('value')
                                    if(is_author1[0]["value"]=="FIRST AUTHOR"):
                                        c=1
                                        break
                        if c==0:
                            Q=Researchconference.objects.filter(id=id).update(category=AarDropdown.objects.get(sno=category),type_of_conference=AarDropdown.objects.get(sno=type_of_conference),sub_category=AarDropdown.objects.get(sno=sub_category),emp_id=emp_id,sponsered=sponsered,conference_title=conference_title,paper_title=paper_title,published_date=published_date,organized_by=organized_by,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,author=AarDropdown.objects.get(sno=author),conference_from=conference_from,conference_to=conference_to,other_description=other_description,publisher_name=publisher_name,publisher_address=publisher_address,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,others=others)
                            Sponsers.objects.filter(spons_id=id,type='CONFERENCE').delete()
                            if(sponsered=="Yes"):
                                Sponsers.objects.create(spons_id=id,emp_id=emp_id,sponser_name=sponsers,type='CONFERENCE')
                            status=200
                            data_values={"OK":200}
                        else:
                            data_values={"sorry":"Failed"}
                            status=409
                    else:
                        data_values={"data not found":"404"}
                        status=404
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def index(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='GET'):
                    if request.GET['check']=='JOURNAL':
                        s=AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL').exclude(value=None).values('sno','value')
                        a=[]
                        for i in s:
                            query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                            i['value']=i['value'].replace('-','_')
                            a.append({i['value'].replace(' ', '_'):list(query1)})
                        data_values={'data':list(a)}
                        status=200

                    if request.GET['check']=='CONFERANCE':
                        s=AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE').exclude(value=None).values('sno','value')
                        a=[]
                        for i in s:
                            query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                            i['value']=i['value'].replace('-','_')
                            a.append({i['value'].replace(' ', '_'):list(query1)})
                        data_values={'data':list(a)}
                        status=200

                    if request.GET['check']=='GUIDANCE':
                        if request.GET['check2']=='false':

                            s=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE').exclude(value=None).values('sno','value')
                            a=[]
                            for i in s:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            data_values={'data':list(a)}
                            status=200

                        if request.GET['check2']=='true':
                            if request.GET['data']=='70':
                                a=[]
                                sno=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT Guidance',value='COURSES').exclude(value=None).values('sno')
                                s=AarDropdown.objects.filter(pid=sno).exclude(value=None).values('value','sno')
                                data_values=list(s)
                                status=200
                            if request.GET['data']=='71':
                                a=[]
                                sno=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='DEGREE').exclude(value=None).values('sno')
                                sno1=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='UNIVERSITY TYPE').exclude(value=None).values('sno')
                                s=AarDropdown.objects.filter(pid=sno).exclude(value=None).values('value','sno')
                                s1=AarDropdown.objects.filter(pid=sno1).exclude(value=None).values('value','sno')
                                data_values={'data':list(s),'data1':list(s1)}
                                status=200
                            if request.GET['data']=='72':
                                a=[]
                                sno=AarDropdown.objects.filter(field='GUIDANCE',value='RESEARCH (PH. D.)').exclude(value=None).values('sno')
                                sno1=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='UNIVERSITY TYPE').exclude(value=None).values('sno')
                                s=AarDropdown.objects.filter(pid=sno).exclude(value=None).values('value','sno')
                                s1=AarDropdown.objects.filter(pid=sno1).exclude(value=None).values('value','sno')
                                data_values={'data':list(s),'data1':list(s1)}
                                status=200

                    if request.GET['check']=='BOOK':
                        s=AarDropdown.objects.filter(field='BOOKS').exclude(value=None).values('sno','value')
                        a=[]
                        for i in s:
                            query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                            i['value']=i['value'].replace('-','_')
                            a.append({i['value'].replace(' ', '_'):list(query1)})
                        data_values={'data':list(a)}
                        status=200

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def Book(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body)
                    emp_id=request.session["hash1"]
                    role=data['role']
                    for_type=data['for_type']
                    publisher=data['publisher']

                    if 'copyright_no' in data:
                        copyright_no=data['copyright_no']
                    else:
                        copyright_no=None

                    copyright_status=data['copyright_status']

                    if 'title' in data:
                        title=data['title']
                    else:
                        title=None

                    if 'chapter' in data:
                        chapter=data['chapter']
                    else:
                        chapter=None

                    publisher_name=data['publisher_name']
                    publisher_add=data['publisher_add']
                    edition=data['edition']
                    date=data['date']
                    publisher_email=data['publisher_email']
                    author=data['author']
                    publisher_website=data['publisher_website']
                    isbn=data['isbn']
                    publisher_code=data['publisher_code']
                    publisher_contact=data['publisher_contact']
                    role_type_new=AarDropdown.objects.get(sno=role)
                    for_type_new=AarDropdown.objects.get(sno=for_type)
                    publisher_new=AarDropdown.objects.get(sno=publisher)
                    author_new=AarDropdown.objects.get(sno=author)

                    doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                    d=str(doj[0]['doj'])
                    Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                    published_date=datetime.datetime.strptime(date,'%Y-%m-%d').date()

                    if Doj!=None:
                        if published_date>Doj:
                            dup=Books.objects.filter(isbn=isbn,emp_id=emp_id).exclude(approve_status__in=['DELETE','REJECTED']).values('isbn')
                            if(dup.count()>0):
                                data_values={"sorry":"Failed"}
                                status=409
                            else:
                                query=Books.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),role=role_type_new,role_for=for_type_new,publisher_type=publisher_new,title=title,edition=edition,published_date=date,chapter=chapter,isbn=isbn,copyright_status=copyright_status,copyright_no=copyright_no,author=author_new,publisher_name=publisher_name,publisher_address=publisher_add,publisher_zip_code=publisher_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                data_values="Data Successfully Added."
                                data_values={'msg':data_values}
                                status=200
                        else:
                            data_values={"msg":"Failed"}
                            status=409
                    else:
                        data_values={"msg":"Failed DOJ is not found"}
                        status=409
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def R_Conference(request):
    data=""
    data_values={}
    status=500
    data=json.loads(request.body.decode("utf-8"))

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    if data!=None:
                        category=AarDropdown.objects.get(sno=data['category'])
                        emp_id=request.session["hash1"]
                        type_of_conference=AarDropdown.objects.get(sno=data["type"])
                        sub_category=AarDropdown.objects.get(sno=data["subCategory"])
                        if 'sponsered' in data:
                            sponsered=data["sponsered"]
                        else:
                            sponsered=None
                        if  'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers=None
                        if 'titleConference' in data:
                            conference_title=data["titleConference"]
                        else:
                            conference_title=None
                        if 'titlePaper' in data:
                            paper_title=data["titlePaper"]
                        else:
                            paper_title=None

                        if 'organised' in data:
                            organized_by=data["organised"]
                        else:
                            organized_by=None
                        if 'journalName' in data:
                            journal_name=data["journalName"]
                        else:
                            journal_name=None
                        if 'volume' in data:
                            volume_no=data["volume"]
                        else:
                            volume_no=None
                        if 'issue' in data:
                            issue_no=data["issue"]
                        else:
                            issue_no=None
                        if 'issn' in data:
                            isbn=data["issn"]
                        else:
                            isbn=None
                        if 'page' in data:
                            page_no=data["page"]
                        else:
                            page_no=None
                        if 'description' in data:
                            other_description=data["description"]
                        else:
                            other_description=None
                        if 'conference_author' in data and data['conference_author'] is not None: 
                            author=AarDropdown.objects.get(sno=data["conference_author"])
                        else:
                            author=None
                        conference_from=data["fromDate"].split('T')[0]
                        conference_to=data["toDate"].split('T')[0]
                        publisher_name=data["publisherName"]
                        publisher_address=data["publisherAddress"]
                        publisher_zip_code=data["publisherPincode"]
                        publisher_contact=data["publisherContact"]
                        publisher_email=data["publisherEmail"]
                        publisher_website=data["publisherWebsite"]
                        published_date=data["dateOfPublish"].split('T')[0]
                        if 'others' in data:
                            others=data["others"]
                        else:
                            others=None
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        published_date=datetime.datetime.strptime(published_date,'%Y-%m-%d').date()

                        if Doj!=None:
                            if published_date>Doj:
                                qry=Researchconference.objects.filter(emp_id=emp_id,category=category,conference_title=conference_title).exclude(approve_status__in=['DELETE','REJECTED']).values('conference_title','paper_title','category__value')

                                if (qry.count()>0):
                                    if "ROLE AS ORGANIZER" not in qry[0]['category__value']:
                                        query=Researchconference.objects.create(category=category,type_of_conference=type_of_conference,sub_category=sub_category,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),sponsered=sponsered,conference_title=conference_title,paper_title=paper_title,published_date=published_date,organized_by=organized_by,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,author=author,conference_from=conference_from,conference_to=conference_to,other_description=other_description,publisher_name=publisher_name,publisher_address=publisher_address,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,others=others,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                        data_values={"OK":"Success"}
                                        status=200

                                    else:
                                        data_values={"OK":"Success"}
                                        status=409

                                else:
                                    query=Researchconference.objects.create(category=category,type_of_conference=type_of_conference,sub_category=sub_category,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),sponsered=sponsered,conference_title=conference_title,paper_title=paper_title,published_date=published_date,organized_by=organized_by,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,author=author,conference_from=conference_from,conference_to=conference_to,other_description=other_description,publisher_name=publisher_name,publisher_address=publisher_address,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,others=others,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                    data_values={"OK":"Success"}
                                    status=200
                            else:
                                data_values={"msg":"published date is before doj"}
                                status=202
                        else:
                            data_values={"msg":"Failed DOJ is not available"}
                            status=402
                    else:
                        data_values={"data not found":"404"}
                        status=404
                else:
                    status=502
            else:
                status=403
        else:
            print(status)
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def R_Guidence(request):
    data=""
    data_values={}
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data is not None:
                        if 'Course' in data:
                            course=data['Course']
                        else:
                            course=None
                        if 'Degree' in data:
                            degree=data['Degree']
                        else:
                            degree=None
                        if 'Degree_awarded' in data:
                            degree_awarded=data['Degree_awarded']
                        else:
                            degree_awarded=None
                        if 'Guidance' in data:
                            guid=data['Guidance']
                        else:
                            guid=None
                        if 'No_of_Students' in data:
                            no_stud=data['No_of_Students']
                        else:
                            no_stud=None
                        if 'area_of_specialization' in data:

                            a_o_s=data['area_of_specialization']
                        else:
                            a_o_s=None
                        if 'project_title' in data:
                            title=data['project_title']
                        else:
                            title=None
                        if 'status' in data:
                            status_guid=data['status']
                        else:
                            status_guid=None
                        if 'university_type' in data:
                            uni_type=data['university_type']
                        else:
                            uni_type=None
                        if 'university_name' in data:
                            uni_name=data['university_name']
                        else:
                            uni_name=None
                        if 'date' in data:
                            date=datetime.datetime.strptime(str(data['date']).split('T')[0],'%Y-%m-%d').date()
                        else:
                            date=None
                        
                        emp_id=request.session["hash1"]

                        if(course!=None):
                            dup=Researchguidence.objects.filter(project_title=title,emp_id=emp_id,guidence=guid).exclude(approve_status__in=['DELETE','REJECTED']).values('project_title')
                            if(dup.count()>0):
                                data_values={"msg":"Failed"}
                                status=409
                            else:
                                Researchguidence.objects.create(guidence=AarDropdown.objects.get(sno=guid),course=AarDropdown.objects.get(sno=course),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                data_values={"msg":"COURSE Inserted Successfully"}
                                status=200


                        elif(degree!=None):
                            dup=Researchguidence.objects.filter(project_title=title,emp_id=emp_id,guidence=guid).exclude(approve_status__in=['DELETE','REJECTED']).values('project_title')
                            if(dup.count()>0):
                                data_values={"msg":"Failed"}
                                status=409
                            else:
                                Researchguidence.objects.create(guidence=AarDropdown.objects.get(sno=guid),degree=AarDropdown.objects.get(sno=degree),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),uni_type=AarDropdown.objects.get(sno=uni_type),uni_name=uni_name,date=date,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                data_values={"msg":"DEGREE Inserted Successfully"}
                                status=200
                        elif(status_guid!=None):
                            dup=Researchguidence.objects.filter(project_title=title,emp_id=emp_id,guidence=guid).exclude(approve_status__in=['DELETE','REJECTED']).values('project_title')
                            if (dup!= None and dup.count()>0):
                                data_values={"sorry":"Failed"}
                                status=409
                            else:
                                Researchguidence.objects.create(guidence=AarDropdown.objects.get(sno=guid),status=AarDropdown.objects.get(sno=status_guid),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,uni_type=AarDropdown.objects.get(sno=uni_type),uni_name=uni_name,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=date,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                data_values={"OK":"STATUS Inserted Successfully"}
                                status=200

                    else:
                        data_values={"msg":"Data not completely filled!"}
                        status=202
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def R_journal(request):
    data_values={}
    data=""
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    if data!=None:
                        data=json.loads(request.body.decode("utf-8"))
                        category=data["category"]
                        emp_id=request.session["hash1"]
                        type_of_journal=data["typeofjournal"]
                        sub_category=data["subcategory"]
                        paper_title=data["papertitle"]
                        impact_factor=data["impacttext"]
                        date=data["dateofpub"]
                        date=date.split('T')
                        Published_date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        journal_name=data["journalname"]
                        volume_no=data["volumeno"]
                        issue_no=data["issueno"]
                        isbn=data["isbn"]
                        page_no=data["pageno"]
                        author=data["typeofAuthor"]
                        publisher_name=data["publishername"]
                        publisher_address1=data["publisheraddL1"]
                        publisher_address2=data["publisheraddL2"]
                        if publisher_address2 is None:
                            publisher_address2=""
                        publisher_zip_code=data["zipc"]
                        publisher_contact=data["phone"]
                        publisher_email=data["eml"]
                        publisher_website=data["website"]
                        if 'subcatText' in data:
                            others=data["subcatText"]
                        else:
                            others=None
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:
                            if Published_date>Doj:
                                if(category!=None):
                                    dup=Researchjournal.objects.filter(isbn=isbn,paper_title=paper_title,emp_id=emp_id).exclude(approve_status__in=['DELETE','REJECTED']).values('isbn')
                                    if (dup.count()>0):
                                        data_values={"OK":"Cannot be inserted"}
                                        status=409
                                    else:
                                        c=0
                                        auth=Researchjournal.objects.filter(isbn=isbn).values('author')
                                        check_auth=AarDropdown.objects.filter(sno=author).values('value')
                                        if check_auth[0]["value"]=="FIRST AUTHOR":
                                            for i in auth:
                                                is_author1=AarDropdown.objects.filter(sno=i["author"]).values('value')
                                                if(is_author1[0]["value"]=="FIRST AUTHOR"):
                                                    c=1
                                                    break

                                        if(c==0):
                                            Researchjournal.objects.create(category=AarDropdown.objects.get(sno=category),author=AarDropdown.objects.get(sno=author),type_of_journal=AarDropdown.objects.get(sno=type_of_journal),sub_category=AarDropdown.objects.get(sno=sub_category),others=others,paper_title=paper_title,published_date=Published_date,impact_factor=impact_factor,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,publisher_name=publisher_name,publisher_address1=publisher_address1,publisher_address2=publisher_address2,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                            data_values={"OK":"DATA Inserted Successfully"}
                                            status=200
                                        else:
                                            qry=Researchjournal.objects.filter(emp_id=emp_id).values('journal_name','paper_title')
                                            ##print (qry[0]['journal_name'])
                                            query=Researchjournal.objects.create(category=AarDropdown.objects.get(sno=category),author=AarDropdown.objects.get(sno=author),type_of_journal=AarDropdown.objects.get(sno=type_of_journal),sub_category=AarDropdown.objects.get(sno=sub_category),others=others,paper_title=paper_title,published_date=Published_date,impact_factor=impact_factor,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,publisher_name=publisher_name,publisher_address1=publisher_address1,publisher_address2=publisher_address2,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                                    
                                            if qry.count()>0:
                                                if(qry[0]['journal_name']==data['journalname'] and qry[0]['paper_title']!=data['papertitle']):
                                                    query=Researchjournal.objects.create(category=AarDropdown.objects.get(sno=category),author=AarDropdown.objects.get(sno=author),type_of_journal=AarDropdown.objects.get(sno=type_of_journal),sub_category=AarDropdown.objects.get(sno=sub_category),others=others,paper_title=paper_title,published_date=Published_date,impact_factor=impact_factor,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,publisher_name=publisher_name,publisher_address1=publisher_address1,publisher_address2=publisher_address2,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                                    data_values={"OK":"Success"}
                                                    status=200
                                                else:

                                                    data_values={"error":"failed"}
                                                    status=409
                                            else:

                                                data_values={"error":"failed"}
                                                status=409
                                else:
                                    print(4)
                                    data_values={"sorry":"Failed"}
                                    status=409
                            else:
                                print(5)
                                data_values={"sorry":"Failed Published_date!>Doj"}
                                status=409
                        else:
                            print(6)
                            data_values={"sorry":"Failed DOJ is not available"}
                            status=409

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def Lectures(request):
    data_values={}
    data=""
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        ###print(data['organization'])
                        category=data["category"]
                        type=data["type"]
                        organization=data["organization"]
                        incorporation=data["incorporation"]
                        role=data["role"]
                        date=data["date"]
                        topic=data["topic"]
                        participants=data["participants"]
                        venue=data["venue"]
                        address=data['address']
                        e_mail=data["e_mail"]
                        pin_code=data["pin_code"]
                        contact_number=data["contact_number"]
                        website=data["website"]
                        approve_status='PENDING'
                        date=date.split('T')
                        date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        ###print (organization)
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        ##print(doj)
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:
                            if date>Doj:
                                dup=LecturesTalks.objects.filter(emp_id=emp_id,topic=topic).exclude(approve_status__in=['DELETE','APPROVED']).values('topic')
                                if(dup.count()>0):
                                    data_values={"sorry":"Duplicate entry"}
                                    status=409
                                else:
                                    LecturesTalks.objects.create(category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type),role=AarDropdown.objects.get(sno=role),incorporation_status=AarDropdown.objects.get(sno=incorporation),organization_sector=AarDropdown.objects.get(sno=organization),date=date,topic=topic,participants=participants,venue=venue,address=address,pin_code=pin_code,contact_number=contact_number,e_mail=e_mail,website=website,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                    data_values={"OK":"DATA Inserted Successfully"}
                                    status=200
                        else:
                            data_values={"sorry":"Doj is null"}
                            status=409
                elif (request.method=='GET'):
                    s=AarDropdown.objects.filter(field='LECTURES AND TALKS').exclude(value=None).values('sno','value')
                    a=[]
                    for i in s:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a.append({i['value'].replace(' ', '_'):list(query1)})
                    data_values={'data':a}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def Projects(request):
    data_values={}
    data=""
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        emp_id=request.session['hash1']
                        type=data["type"]
                        if 'p_status' in data:
                            status=data["p_status"]
                        else:
                            status=None
                        sector=data["sector"]
                        start_date=data["start_date"]
                        end_date=data["end_date"]
                        if 'principal' in data:
                            principal=data["principal"]
                            if principal=='self':
                                principal_id=emp_id
                            elif principal=='other':
                                principal_id=data['principal_id']
                        else:
                            principal_id=None
                        if 'co_principal' in data:
                            co_principal=data["co_principal"]
                            if co_principal=='self':
                                co_principal_id=emp_id
                            elif co_principal=='other':
                                co_principal_id=data['co_principal_id']
                        else:
                            co_principal=None
                        team_size=data["team_size"]
                        sponsored=data["sponsored"]
                        association=data["association"]
                        if 'organisation' in data:
                            organisation=data["organisation"]
                        else:
                            organisation=None
                        if 'contact_person' in data:
                            contact_person=data["contact_person"]
                        else:
                            contact_person=None
                        if 'address' in data:
                            address=data['address']
                        else:
                            address=None
                        if 'e_mail' in data:
                            e_mail=data["e_mail"]
                        else:
                            e_mail=None
                        if 'pin_code' in data:
                            pin_code=data["pin_code"]
                        else:
                            pin_code=None
                        if 'contact_number' in data:
                            contact_number=data["contact_number"]
                        else:
                            contact_number=None
                        if 'website' in data:
                            website=data["website"]
                        else:
                            website=None
                        if 'amount' in data:
                            amount=data['amount']
                        else:
                            amount=None
                        if 'organisation1' in data:
                            organisation1=data["organisation1"]
                        else:
                            organisation1=None
                        if 'contact_person1' in data:
                            contact_person1=data["contact_person1"]
                        else:
                            contact_person1=None
                        if 'address1' in data:
                            address1=data['address1']
                        else:
                            address1=None
                        if 'e_mail1' in data:
                            e_mail1=data["e_mail1"]
                        else:
                            e_mail1=None
                        if 'pin_code1' in data:
                            pin_code1=data["pin_code1"]
                        else:
                            pin_code1=None
                        if 'contact_number1' in data:
                            contact_number1=data["contact_number1"]
                        else:
                            contact_number1=None
                        if 'website1' in data:
                            website1=data["website1"]
                        else:
                            website1=None
                        if 'amount1' in data:
                            amount1=data['amount1']
                        else:
                            amount1=None
                        if 'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers=None
                        if 'sponsers2' in data:
                            sponsers2=data['sponsers2']
                        else:
                            sponsers2=None
                        title=data["title"]
                        descreption=data["descreption"]
                        approve_status='PENDING'
                        discipline=data["discipline"]
                        from_d= start_date.split('T')
                        to_d= end_date.split('T')
                        start_date=datetime.datetime.strptime(from_d[0],'%Y-%m-%d').date()
                        end_date=datetime.datetime.strptime(to_d[0],'%Y-%m-%d').date()
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:
                            if start_date>Doj:
                                dup=ProjectConsultancy.objects.filter(emp_id=emp_id,title=title).exclude(approve_status__in=['DELETE','REJECTED']).values('title')
                                if(dup.count()>0):
                                    data_values={"sorry":"Duplicate entry"}
                                    status=409
                                else:
                                    query=ProjectConsultancy.objects.create(type=AarDropdown.objects.get(sno=type),sector=AarDropdown.objects.get(sno=sector),status=AarDropdown.objects.get(sno=status),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),title=title,descreption=descreption,start_date=start_date,end_date=end_date,principal_investigator=principal,co_principal_investigator=co_principal,principal_investigator_id=principal_id,co_principal_investigator_id=co_principal_id,team_size=team_size,sponsored=sponsored,association=association,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                    sno=query.id
                                    if(sponsored=="yes"):
                                        for i in sponsers:
                                            Sponsers.objects.create(spons_id=sno,emp_id=emp_id,sponser_name=i["organisation"],type="PROJECT",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='SPONSOR')
                                    if(association=="yes"):
                                        for i in sponsers2:
                                            Sponsers.objects.create(spons_id=sno,emp_id=emp_id,sponser_name=i["organisation1"],type="PROJECT",contact_person=i['contact_person1'],contact_number=i['contact_number1'],e_mail=i['e_mail1'],website=i['website1'],amount=i['amount1'],address=i['address1'],pin_code=i['pin_code1'],field_type='ASSOCIATION')
                                    if  discipline!=None:
                                        for i in discipline:
                                            Discipline.objects.create(id=sno,emp_id=emp_id,value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="PROJECT/CONSULTANCY")
                                    data_values={"OK":"DATA Inserted Successfully"}
                                    status=200
                elif (request.method=='GET'):
                    s=AarDropdown.objects.filter(field='PROJECT / CONSULTANCY').exclude(value=None).values('sno','value')
                    a=[]
                    for i in s:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a.append({i['value'].replace(' ', '_'):list(query1)})
                    s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                    a2=[]
                    for i in s2:
                        query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a2.append({i['value'].replace(' ', '_'):list(query1)})
                    data_values={'data':a,'data2':a2}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def Patent_data(request):
    data_values={}
    data=""
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        if 'discipline' in data:
                            discipline=data["discipline"]
                        else:
                            discipline=None
                        if 'collaboration' in data:
                            collaboration=data["collaboration"]
                        else:
                            collaboration=None
                        if 'company' in data:
                            company_name=data["company"]
                        else:
                            company_name=None
                        if 'incorporate' in data:
                            if data['incorporate'] is not None:
                                incorporate_status=AarDropdown.objects.get(sno=data['incorporate'])
                            else:
                                incorporate_status=None
                        else:
                            incorporate_status=None
                        if 'status' in data:
                            status=data["status"]
                        else:
                            status=None
                        if 'number' in data:
                            number=data["number"]
                        else:
                            number=None
                        if 'date' in data:
                            date=data["date"]
                        else:
                            date=None
                        date=date.split('T')
                        date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        if 'owner' in data:
                            owner=AarDropdown.objects.get(sno=data['owner'])
                        else:
                            owner=None
                        if 'title' in data:
                            title=data["title"]
                        else:
                            title=None
                        if 'desc' in data:
                            descreption=data["desc"]
                        else:
                            descreption=None
                        approve_status='PENDING'
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:
                            if date>Doj:
                                dup=Patent.objects.filter(title=title).exclude(approve_status__in=['DELETE','REJECTED']).values('title')
                                if (dup.count()>0):
                                    data_values={"sorry":"Data Already Exists"}
                                    status=409
                                else:
                                    query=Patent.objects.create(incorporate_status=incorporate_status,owner=owner,title=title,descreption=descreption,collaboration=collaboration,company_name=company_name,status=status,number=number,date=date,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),approve_status='PENDING',t_date=str(datetime.datetime.now()))
                                    sno=query.id
                                    if  discipline!=None:
                                        for i in discipline:
                                            Discipline.objects.create(id=sno,emp_id=emp_id,value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="PATENT")
                                    data_values={"OK":"DATA Inserted Successfully"}
                                    status=200

                elif (request.method=='GET'):
                    s1=AarDropdown.objects.filter(field='PATENT').exclude(value=None).values('sno','value')
                    a1=[]
                    for i in s1:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a1.append({i['value'].replace(' ', '_'):list(query1)})
                    a3=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('name','emp_id')
                    s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                    a2=[]
                    for i in s2:
                        query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a2.append({i['value'].replace(' ', '_'):list(query1)})
                    data_values={'data1':a1,'data2':a2,'data3':list(a3)}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def Training(request):
    data_values={}
    data=""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        emp_id=request.session['hash1']
                        category=data["category"]
                        type=data["type"]
                        organization=data["organization"]
                        incorporation=data["status"]
                        role=data["role"]
                        attended=data["attend"]
                        organizers=data["organizer"]
                        participants=data["participants"]
                        venue=data["venue"]

                        if 'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers= None
                        if 'collaboration' in data:
                            collaborations=data["collaboration"]
                        else:
                            collaboration= None
                        if 'organisation' in data:
                            organisation=data["organisation"]
                        else:
                            organisation=None
                        if 'contact_person' in data:
                            contact_person=data["contact_person"]
                        else:
                            contact_person=None
                        if 'address' in data:
                            address=data['address']
                        else:
                            address=None
                        if 'e_mail' in data:
                            e_mail=data["e_mail"]
                        else:
                            e_mail=None
                        if 'pin_code' in data:
                            pin_code=data["pin_code"]
                        else:
                            pin_code=None
                        if 'contact_number' in data:
                            contact_number=data["contact_number"]
                        else:
                            contact_number=None
                        if 'website' in data:
                            website=data["website"]
                        else:
                            website=None
                        if 'amount' in data:
                            amount=data['amount']
                        else:
                            amount=None
                        if 'organisation1' in data:
                            organisation1=data["organisation1"]
                        else:
                            organisation1=None
                        if 'contact_person1' in data:
                            contact_person1=data["contact_person1"]
                        else:
                            contact_person1=None
                        if 'address1' in data:
                            address1=data['address1']
                        else:
                            address1=None
                        if 'e_mail1' in data:
                            e_mail1=data["e_mail1"]
                        else:
                            e_mail1=None
                        if 'pin_code1' in data:
                            pin_code1=data["pin_code1"]
                        else:
                            pin_code1=None
                        if 'contact_number1' in data:
                            contact_number1=data["contact_number1"]
                        else:
                            contact_number1=None
                        if 'website1' in data:
                            website1=data["website1"]
                        else:
                            website1=None
                        if 'amount1' in data:
                            amount1=data['amount1']
                        else:
                            amount1=None
                        if 'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers=None
                        if 'sponsers2' in data:
                            sponsers2=data['sponsers2']
                        else:
                            sponsers2=None
                        if 'sponsership' in data:
                            sponsership=data['sponsership']
                        else:
                            sponsership=None
                        if 'discipline' in data:
                            discipline=data["discipline"]
                        else:
                            discipline=None
                        from_date=data["from_date"]
                        to_date=data["to_date"]
                        title=data["title"]

                        from_d= from_date.split('T')
                        to_d= to_date.split('T')
                        from_date=datetime.datetime.strptime(from_d[0],'%Y-%m-%d').date()
                        to_date=datetime.datetime.strptime(to_d[0],'%Y-%m-%d').date()

                        approve_status='PENDING'
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')

                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:
                            if from_date>Doj:
                                dup=TrainingDevelopment.objects.filter(title=title,type=type,emp_id=emp_id).exclude(approve_status__in=['DELETE','REJECTED']).values('type')
                                if(dup.count()>0):
                                    data_values={"sorry":"Data Already Exists"}
                                    status=409
                                else:
                                    sno=[{}]
                                    query=TrainingDevelopment.objects.create(category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type),role=AarDropdown.objects.get(sno=role),incorporation_status=AarDropdown.objects.get(sno=incorporation),organization_sector=AarDropdown.objects.get(sno=organization),from_date=from_date,to_date=to_date,participants=participants,venue=venue,title=title,organizers=organizers,attended=attended,collaborations=collaborations,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),approve_status='PENDING',t_date=str(datetime.datetime.now()),sponsership=sponsership)
                                    sno[0]['id']=query.id
                                    if(collaborations=="yes"):
                                        for i in sponsers:
                                            Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=emp_id,sponser_name=i["organisation"],type="TRAINING",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='COLLABORATION')
                                    if(sponsership=="yes"):
                                        for i in sponsers2:
                                            Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=emp_id,sponser_name=i["organisation1"],type="TRAINING",contact_person=i['contact_person1'],contact_number=i['contact_number1'],e_mail=i['e_mail1'],website=i['website1'],amount=i['amount1'],address=i['address1'],pin_code=i['pin_code1'],field_type='SPONSOR')

                                    if  discipline!=None:
                                        for i in discipline:
                                            Discipline.objects.create(id=sno[0]['id'],emp_id=emp_id,value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="TRAINING")
                                    status=200
                                    data_values={"OK":"DATA Insertion Successful"}
                            else:
                                status=202
                                data_values={"msg":"Achievement of before your joining"}
                        else:
                            data_values={"msg":"Data not filled completely"}
                            status=202
                    else:
                        status=202
                        data_values={"msg":"Data not filled completely"}
                elif (request.method=='GET'):
                    s1=AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM').exclude(value=None).values('sno','value')
                    a1=[]
                    for i in s1:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a1.append({i['value'].replace(' ', '_'):list(query1)})
                    s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                    a2=[]
                    for i in s2:
                        query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a2.append({i['value'].replace(' ', '_'):list(query1)})
                    data_values={'data1':a1,'data2':a2}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def Update_Patent(request):
    data_values={}
    data=""

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data['data1']=='1':
                        id=data['id']
                        d=Discipline.objects.filter(emp_id=emp_id,type="PATENT",id=id).values('value2')
                        s1=AarDropdown.objects.filter(field='PATENT').exclude(value=None).values('sno','value')
                        a1=[]
                        for i in s1:
                            query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                            i['value']=i['value'].replace('-','_')
                            a1.append({i['value'].replace(' ', '_'):list(query1)})
                        s2=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE').exclude(value=None).values('sno','value')
                        a2=[]
                        for i in s2:
                            query1=AarDropdown.objects.filter(pid=i['sno'],field="COURSES").exclude(value=None).values('sno','value')
                            i['value']=i['value'].replace('-','_')
                            a2.append({i['value'].replace(' ', '_'):list(query1)})
                        a3=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('name','emp_id')
                        a4=Patent.objects.filter(id=id).values('title','descreption','collaboration','company_name','incorporate_status__value','status','number','date','owner__value','approve_status','emp_id')
                        data_values={'data1':a1,'data2':a2,'data3':list(a3),'data4':list(a4),'data5':list(d)}
                        status=200
                    elif data['data1']=='2':
                        if 'discipline' in data:
                            discipline=data["discipline"]
                        else:
                            discipline=None
                        collaboration=data["collaboration"]
                        if 'company' in data:
                            company_name=data["company"]
                        else:
                            company_name=None
                        if 'incorporate' in data:
                            if data['incorporate']!=None:
                                incorporate_status=AarDropdown.objects.get(sno=data['incorporate'])
                            else:
                                incorporate_status=None
                        else:
                            incorporate_status=None
                        if 'status' in data:
                            status=data["status"]
                        else:
                            status=None
                        if 'number' in data:
                            number=data["number"]
                        else:
                            number=None
                        date=data["date"]
                        id=data["id"]
                        date=date.split('T')
                        date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        owner=AarDropdown.objects.get(sno=data['owner'])
                        title=data["title"]
                        descreption=data["desc"]
                        approve_status='PENDING'
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:
                            if date>Doj:
                                query=Patent.objects.filter(id=id).update(title=title,incorporate_status=incorporate_status,owner=owner,collaboration=collaboration,company_name=company_name,status=status,number=number,date=date)
                                sno=id
                                Discipline.objects.filter(emp_id=emp_id,type="PATENT").delete()
                                if  discipline!=None:
                                    for i in discipline:
                                        Discipline.objects.create(id=sno,emp_id=emp_id,value1=None,value2=AarDropdown.objects.get(sno=i),type="PATENT")
                                data_values={"OK":"DATA Updated Successfully"}
                                status=200
                            else:
                                status=202
                                data_values={"msg":"Achievement of before your joining"}
                        else:
                            data_values={"msg":"Data not filled completely"}
                            status=202
                elif (request.method=='GET'):
                    s=Patent.objects.filter(emp_id=emp_id,approve_status="PENDING").exclude(approve_status='DELETE').values('title','approve_status','id')
                    data_values={'data':list(s)}
                    status=200

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def Update_Lectures(request):
    data_values={}
    data=""
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data['data1']=='2':
                        id=data['id']
                        category=data["category"]
                        type=data["type"]
                        organization=data["organization"]
                        incorporation=data["incorporation"]
                        role=data["role"]
                        date=data["date"]
                        date=date.split('T')
                        date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        topic=data["topic"]
                        prev_topic=data["prev_topic"]
                        participants=data["participants"]
                        venue=data["venue"]
                        address=data['address']
                        e_mail=data["e_mail"]
                        pin_code=data["pin_code"]
                        contact_number=data["contact_number"]
                        website=data["website"]

                        LecturesTalks.objects.filter(id=id).update(category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type),role=AarDropdown.objects.get(sno=role),incorporation_status=AarDropdown.objects.get(sno=incorporation),organization_sector=AarDropdown.objects.get(sno=organization),date=date,topic=topic,participants=participants,venue=venue,address=address,pin_code=pin_code,contact_number=contact_number,e_mail=e_mail,website=website,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id))
                        data_values={"OK":"DATA updated Successfully"}
                        status=200
                    elif data['data1']=='1':
                        id=data['id']
                        s1=AarDropdown.objects.filter(field='LECTURES AND TALKS').exclude(value=None).values('sno','value')
                        a=[]
                        for i in s1:
                            query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                            i['value']=i['value'].replace('-','_')
                            a.append({i['value'].replace(' ', '_'):list(query1)})
                        s2=LecturesTalks.objects.filter(emp_id=emp_id,id=id).values('emp_id','category__value','type__value','organization_sector__value','incorporation_status','role','date','topic','participants','venue','address','pin_code','contact_number','e_mail','website')
                        data_values={'data1':list(a),'data2':list(s2)}
                        #
                        status=200
                elif (request.method=='GET'):
                    s=LecturesTalks.objects.filter(emp_id=emp_id,approve_status='PENDING').exclude(approve_status='DELETE').values('topic','approve_status','id')
                    data_values={'data':list(s)}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)
# ///////////
def Update_Training(request):
    data_values={}
    data=""
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        if data['data1']=='1':
                            id=data['id']
                            d=Discipline.objects.filter(emp_id=emp_id,type="TRAINING",id=id).values('value1')
                            s1=AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM').exclude(value=None).values('sno','value')
                            a1=[]
                            for i in s1:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a1.append({i['value'].replace(' ', '_'):list(query1)})
                            s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            
                            a2=[]
                            for i in s2:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            s2=TrainingDevelopment.objects.filter(emp_id=emp_id,id=id).values('emp_id','category__value','type__value','from_date','to_date','role','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaborations','sponsership','approve_status')
                            s3=Sponsers.objects.filter(spons_id=id,field_type='COLLABORATION').values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s4=Sponsers.objects.filter(spons_id=id,field_type='SPONSOR').values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            reporting_info={'reporting_levels':s3.count(),'reporting_levels1':s4.count(),'data_a':list(s3),'data_b':list(s4)}
                            s5=Discipline.objects.filter(id=id,emp_id=emp_id,type="TRAINING").values('value1__value')
                            data_values={'data1':a1,'data2':a2,'data3':list(s2),'data4':reporting_info,'data5':list(s5),'data6':list(d)}
                            #
                            status=200
                        elif data['data1']=='2':
                            category=data["category"]
                            type=data["type"]
                            organization=data["organization"]
                            incorporation=data["status"]
                            role=data["role"]
                            attended=data["attend"]
                            organizers=data["organizer"]
                            participants=data["participants"]
                            venue=data["venue"]

                            if 'sponsers' in data:
                                sponsers=data['sponsers']
                            else:
                                sponsers= None
                            if 'collaboration' in data:
                                collaborations=data["collaboration"]
                            else:
                                collaboration= None
                            if 'organisation' in data:
                                organisation=data["organisation"]
                            else:
                                organisation=None
                            if 'contact_person' in data:
                                contact_person=data["contact_person"]
                            else:
                                contact_person=None
                            if 'address' in data:
                                address=data['address']
                            else:
                                address=None
                            if 'e_mail' in data:
                                e_mail=data["e_mail"]
                            else:
                                e_mail=None
                            if 'pin_code' in data:
                                pin_code=data["pin_code"]
                            else:
                                pin_code=None
                            if 'contact_number' in data:
                                contact_number=data["contact_number"]
                            else:
                                contact_number=None
                            if 'website' in data:
                                website=data["website"]
                            else:
                                website=None
                            if 'amount' in data:
                                amount=data['amount']
                            else:
                                amount=None
                            if 'organisation1' in data:
                                organisation1=data["organisation1"]
                            else:
                                organisation1=None
                            if 'contact_person1' in data:
                                contact_person1=data["contact_person1"]
                            else:
                                contact_person1=None
                            if 'address1' in data:
                                address1=data['address1']
                            else:
                                address1=None
                            if 'e_mail1' in data:
                                e_mail1=data["e_mail1"]
                            else:
                                e_mail1=None
                            if 'pin_code1' in data:
                                pin_code1=data["pin_code1"]
                            else:
                                pin_code1=None
                            if 'contact_number1' in data:
                                contact_number1=data["contact_number1"]
                            else:
                                contact_number1=None
                            if 'website1' in data:
                                website1=data["website1"]
                            else:
                                website1=None
                            if 'amount1' in data:
                                amount1=data['amount1']
                            else:
                                amount1=None
                            if 'sponsers' in data:
                                sponsers=data['sponsers']
                            else:
                                sponsers=None
                            if 'sponsers2' in data:
                                sponsers2=data['sponsers2']
                            else:
                                sponsers2=None
                            if 'sponsership' in data:
                                sponsership=data['sponsership']
                            else:
                                sponsership=None
                            if 'discipline' in data:
                                discipline=data["discipline"]
                            else:
                                discipline=None
                            from_date=data["from_date"]
                            to_date=data["to_date"]
                            title=data["title"]
                            prev_title=data['prev_title']
                            #sponsership="No"
                            from_d= from_date.split('T')
                            to_d= to_date.split('T')
                            from_date=datetime.datetime.strptime(from_d[0],'%Y-%m-%d').date()
                            to_date=datetime.datetime.strptime(to_d[0],'%Y-%m-%d').date()
                            approve_status='PENDING'
                            Q=TrainingDevelopment.objects.filter(emp_id=emp_id,title=prev_title).update(category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type),role=AarDropdown.objects.get(sno=role),incorporation_status=AarDropdown.objects.get(sno=incorporation),organization_sector=AarDropdown.objects.get(sno=organization),from_date=from_date,to_date=to_date,participants=participants,venue=venue,title=title,organizers=organizers,attended=attended,collaborations=collaborations,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),approve_status=approve_status,sponsership=sponsership)
                            sno=TrainingDevelopment.objects.filter(emp_id=emp_id,title=title).values('id')
                            if sno.count()>0:
                                Sponsers.objects.filter(spons_id=sno[0]['id'],emp_id=emp_id,type="TRAINING").delete()
                                Discipline.objects.filter(emp_id=emp_id,type="TRAINING",id=sno[0]['id']).delete()

                            if(collaborations=="yes"):
                                for i in sponsers:
                                    Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=emp_id,sponser_name=i["organisation"],type="TRAINING",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='COLLABORATION')
                            if(sponsership=="yes"):
                                for i in sponsers2:
                                    Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=emp_id,sponser_name=i["organisation1"],type="TRAINING",contact_person=i['contact_person1'],contact_number=i['contact_number1'],e_mail=i['e_mail1'],website=i['website1'],amount=i['amount1'],address=i['address1'],pin_code=i['pin_code1'],field_type='SPONSOR')
                            if  discipline!=None:
                                for i in discipline:
                                    Discipline.objects.create(id=sno[0]['id'],emp_id=emp_id,value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="TRAINING")
                            status=200
                            data_values={"OK":"DATA updated UnSuccessful"}
                elif (request.method=='GET'):
                    s=TrainingDevelopment.objects.filter(emp_id=emp_id,approve_status='PENDING').exclude(approve_status='APPROVED').exclude(approve_status='REJECTED').exclude(approve_status='DELETE').values('title','approve_status','id')
                    data_values={'data':list(s)}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def Update_Projects(request):
    data_values={}
    data=""
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    
                    if data!=None:
                        if (data['data1'] == '1'):
                            id=data['id']
                            s=AarDropdown.objects.filter(field='PROJECT / CONSULTANCY').exclude(value=None).values('sno','value')
                            a=[]
                            for i in s:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            a2=[]
                            for i in s2:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            s3=ProjectConsultancy.objects.filter(emp_id=emp_id,id=id).values('emp_id','status__value','type__value','sector__value','title','descreption','start_date','end_date','principal_investigator','co_principal_investigator','team_size','sponsored','association','approve_status','principal_investigator_id','co_principal_investigator_id')
                            s4=Sponsers.objects.filter(spons_id=id,field_type="SPONSORED").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s5=Sponsers.objects.filter(spons_id=id,field_type="ASSOCIATION").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s6=Discipline.objects.filter(id=id,emp_id=emp_id,type="PROJECT/CONSULTANCY").values('value1')
                            reporting_info={'reporting_levels':s4.count(),'reporting_levels1':s5.count(),'data_a':list(s4),'data_b':list(s5)}
                            data_values={'data':a,'data2':a2,'data3':list(s3),'data4':reporting_info,'data5':list(s6)}
                            status=200
                        elif (data['data1'] == '2'):
                            type=data["type"]
                            if 'p_status' in data:
                                status=data["p_status"]
                            else:
                                status=None
                            sector=data["sector"]
                            start_date=data["start_date"]
                            end_date=data["end_date"]
                            if 'principal' in data:
                                principal=data["principal"]
                                if principal=='self':
                                    principal_id=emp_id
                                elif principal=='other':
                                    principal_id=data['principal_id']
                            else:
                                principal=None
                            if 'co_principal' in data:
                                co_principal=data["co_principal"]
                                if co_principal=='self':
                                    co_principal_id=emp_id
                                elif co_principal=='other':
                                    co_principal_id=data['co_principal_id']
                            else:
                                co_principal=None
                            team_size=data["team_size"]
                            sponsored=data["sponsored"]
                            association=data["association"]
                            if 'organisation' in data:
                                organisation=data["organisation"]
                            else:
                                organisation=None
                            if 'contact_person' in data:
                                contact_person=data["contact_person"]
                            else:
                                contact_person=None
                            if 'address' in data:
                                address=data['address']
                            else:
                                address=None
                            if 'e_mail' in data:
                                e_mail=data["e_mail"]
                            else:
                                e_mail=None
                            if 'pin_code' in data:
                                pin_code=data["pin_code"]
                            else:
                                pin_code=None
                            if 'contact_number' in data:
                                contact_number=data["contact_number"]
                            else:
                                contact_number=None
                            if 'website' in data:
                                website=data["website"]
                            else:
                                website=None
                            if 'amount' in data:
                                amount=data['amount']
                            else:
                                amount=None
                            if 'organisation1' in data:
                                organisation1=data["organisation1"]
                            else:
                                organisation1=None
                            if 'contact_person1' in data:
                                contact_person1=data["contact_person1"]
                            else:
                                contact_person1=None
                            if 'address1' in data:
                                address1=data['address1']
                            else:
                                address1=None
                            if 'e_mail1' in data:
                                e_mail1=data["e_mail1"]
                            else:
                                e_mail1=None
                            if 'pin_code1' in data:
                                pin_code1=data["pin_code1"]
                            else:
                                pin_code1=None
                            if 'contact_number1' in data:
                                contact_number1=data["contact_number1"]
                            else:
                                contact_number1=None
                            if 'website1' in data:
                                website1=data["website1"]
                            else:
                                website1=None
                            if 'amount1' in data:
                                amount1=data['amount1']
                            else:
                                amount1=None
                            if 'sponsers' in data:
                                sponsers=data['sponsers']
                            else:
                                sponsers=None
                            if 'sponsers2' in data:
                                sponsers2=data['sponsers2']
                            else:
                                sponsers2=None
                            title=data["title"]
                            prev_title=data["prev_title"]
                            descreption=data["descreption"]
                            approve_status='PENDING'
                            discipline=data["discipline"]
                            id=data["id"]
                            from_d= start_date.split('T')
                            to_d= end_date.split('T')
                            start_date =datetime.datetime.strptime(from_d[0],'%Y-%m-%d').date()
                            end_date=datetime.datetime.strptime(to_d[0],'%Y-%m-%d').date()
                            query=ProjectConsultancy.objects.filter(emp_id=emp_id,id=id).update(type=AarDropdown.objects.get(sno=type),sector=AarDropdown.objects.get(sno=sector),status=AarDropdown.objects.get(sno=status),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),title=title,descreption=descreption,start_date=start_date,end_date=end_date,principal_investigator=principal,co_principal_investigator=co_principal,principal_investigator_id=principal_id,co_principal_investigator_id=co_principal_id,team_size=team_size,sponsored=sponsored,association=association,approve_status=approve_status)
                            sno=id
                            Discipline.objects.filter(emp_id=emp_id,type='PROJECT/CONSULTANCY').delete()
                            Sponsers.objects.filter(spons_id=sno,emp_id=emp_id).delete()
                            if(sponsored=="yes"):
                                for i in sponsers:
                                    Sponsers.objects.create(spons_id=sno,emp_id=emp_id,sponser_name=i["organisation"],type="PROJECT",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='SPONSORED')
                            if(association=="yes"):
                                for i in sponsers2:
                                    Sponsers.objects.create(spons_id=sno,emp_id=emp_id,sponser_name=i["organisation1"],type="PROJECT",contact_person=i['contact_person1'],contact_number=i['contact_number1'],e_mail=i['e_mail1'],website=i['website1'],amount=i['amount1'],address=i['address1'],pin_code=i['pin_code1'],field_type='ASSOCIATION')
                            if  discipline!=None:
                                ##print discipline
                                for i in discipline:
                                    Discipline.objects.create(id=sno,emp_id=emp_id,value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="PROJECT/CONSULTANCY")
                            data_values={"OK":"DATA updated Successfully"}
                            status=200
                elif (request.method=='GET'):
                    s=ProjectConsultancy.objects.filter(emp_id=emp_id).exclude(approve_status='DELETE').values('approve_status','title','id')
                    data_values={'data':list(s)}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status)

def approval(request):
    msg={}
    data_values={}
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[319,337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    data_values={'data':list(q)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))

                    if(data['test']=='1'):
                        sno=data['data']
                        dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept','desg')
                        emps=Reporting.objects.filter(department=dept[0]['dept'],reporting_to=dept[0]['desg'],reporting_no=1).values('emp_id','emp_id__name')

                        for e in emps:
                            e['name']=e['emp_id__name']
                        a=[]
                        data1=[]
                        if(sno=='1'):
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchjournal.objects.filter(emp_id=Eid,approve_status='PENDING').values('paper_title','id','emp_id')
                                b=[]
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id']}
                                        b.append(d)
                                    data={'emp_id':Eid,'name':name,'title':b}
                                    a.append(data)
                            status=200
                            data_values={'data':a}

                        elif(sno=='2'):
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchconference.objects.filter(emp_id=Eid,approve_status='PENDING').values('paper_title','id')
                                b=[]
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id']}
                                        b.append(d)
                                    data={'emp_id':Eid,'name':name,'title':b}
                                    a.append(data)
                            status=200
                            data_values={'data':a}
                            
                        elif(sno=='3'):
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Books.objects.filter(emp_id=Eid,approve_status='PENDING').values('title','id')
                                if(q.count()>0):
                                    data={'emp_id':Eid,'name':name,'title':list(q)}
                                    a.append(data)
                            status=200
                            data_values={'data':a}

                        elif(sno=='4'):
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchguidence.objects.filter(emp_id=Eid,approve_status='PENDING').values('project_title','id')
                                b=[]
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['project_title'],'id':i['id']}
                                        b.append(d)
                                    data={'emp_id':Eid,'name':name,'title':b}
                                    a.append(data)
                            status=200
                            data_values={'data':a}

                        elif(sno=='5'):
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Patent.objects.filter(emp_id=Eid,approve_status='PENDING').values('title','id')
                                if(q.count()>0):
                                    data={'emp_id':Eid,'name':name,'title':list(q)}
                                    a.append(data)
                            s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            a2=[]
                            for i in s2:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            data_values={'data':a,'data1':a2}

                        elif(sno=='6'):
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                c=0
                                q=ProjectConsultancy.objects.filter(emp_id=Eid,approve_status='PENDING').values('title','id')
                                c=ProjectConsultancy.objects.filter(emp_id=Eid,approve_status='PENDING').values('title').count()
                                if(c>0):
                                    data={'emp_id':Eid,'name':name,'title':list(q)}
                                    a.append(data)
                            status=200
                            data_values={'data':a}

                        elif(sno=='7'):
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=TrainingDevelopment.objects.filter(emp_id=Eid,approve_status='PENDING').values('title','id')
                                if(q.count()>0):
                                    data={'emp_id':Eid,'name':name,'title':list(q)}
                                    a.append(data)
                            status=200
                            data_values={'data':a}

                        elif(sno=='8'):
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=LecturesTalks.objects.filter(emp_id=Eid,approve_status='PENDING').values('topic','id')
                                b=[]
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['topic'],'id':i['id']}
                                        b.append(d)
                                    data={'emp_id':Eid,'name':name,'title':b}
                                    a.append(data)
                            status=200
                            data_values={'data':a}

                    elif(data['test']=='2'):
                        if(data['sno']=='1'):
                            q=Researchjournal.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='APPROVED')
                        if(data['sno']=='2'):
                            q=Researchconference.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='APPROVED')
                        if(data['sno']=='3'):
                            q=Books.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='APPROVED')
                        if(data['sno']=='4'):                            
                            q=Researchguidence.objects.filter(id=data['id'],emp_id=data['emp_id']).update(approve_status='APPROVED')
                        if(data['sno']=='5'):                            
                            q=Patent.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='APPROVED')
                        if(data['sno']=='6'):                            
                            q=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='APPROVED')
                        if(data['sno']=='7'):                            
                            q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='APPROVED')
                        if(data['sno']=='8'):
                            q=LecturesTalks.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='APPROVED')
                        status=200
                        data_values={"OK":"DATA updated Successfully"}

                    elif(data['test']=='3'):
                        if(data['sno']=='1'):
                            q=Researchjournal.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='REJECTED')
                        if(data['sno']=='2'):
                            q=Researchconference.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='REJECTED')
                        if(data['sno']=='3'):                            
                            q=Books.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='REJECTED')
                        if(data['sno']=='4'):                            
                            q=Researchguidence.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='REJECTED')
                        if(data['sno']=='5'):                            
                            q=Patent.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='REJECTED')
                        if(data['sno']=='6'):                            
                            q=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='REJECTED')
                        if(data['sno']=='7'):                            
                            q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='REJECTED')
                        if(data['sno']=='8'):                            
                            q=LecturesTalks.objects.filter(emp_id=data['emp_id'],id=data['id']).update(approve_status='REJECTED')
                        status=200
                        data_values={"OK":"DATA updated Successfully"}

                    elif(data['test']=='4'):
                        if(data['sno']=='8'):
                            q=LecturesTalks.objects.filter(emp_id=data['emp_id'],id=data['id']).exclude(approve_status="REJECTED").exclude(approve_status="DELETE").values('emp_id','category__value','type__value','organization_sector__value','incorporation_status__value','role__value','date','topic','participants','venue','address','pin_code','contact_number','e_mail','website','approve_status')
                            status=200
                            data_values={'data':list(q)}

                        elif(data['sno']=='7'):
                            q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],id=data['id']).exclude(approve_status="REJECTED").values('emp_id','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaborations','sponsership','approve_status')
                            s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s2=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s3=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            
                            a2=[]
                            for i in s3:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            s=Discipline.objects.filter(id=data['id'],type="TRAINING").values_list('value1__value',flat=True)
                            print(s)
                            status=200
                            data_values={'reporting_levels':s1.count(),'reporting_levels1':s2.count(),'data':list(q),'discipline_select':list(s),'sponsers':list(s1),'association':list(s2),'discipline':a2}
                        elif(data['sno']=='6'):
                            
                            q=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],id=data['id']).exclude(approve_status="REJECTED").values('emp_id','status__value','type__value','sector__value','title','descreption','start_date','end_date','principal_investigator','co_principal_investigator','team_size','sponsored','association','approve_status')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PROJECT/CONSULTANCY").values('value1__value')
                            
                            s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="PROJECT").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s3=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION',type="PROJECT").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            
                            s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            
                            a2=[]
                            for i in s2:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            data_values={'reporting_levels':s1.count(),'reporting_levels1':s3.count(),'data':list(q),'discipline':list(s),'sponsers':list(s1),'association':list(s3),'data1':a2}
                        elif(data['sno']=='5'):
                            q=Patent.objects.filter(emp_id=data['emp_id'],id=data['id']).exclude(approve_status="REJECTED").values('title','descreption','collaboration','company_name','incorporate_status__value','status','number','date','owner__value','approve_status','emp_id')

                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PATENT").values('value1__value')
                            
                            s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            
                            a2=[]
                            for i in s2:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            
                            status=200
                            data_values={'data':list(q),'discipline':list(s),'data1':a2}
                            
                        elif(data['sno']=='4'):
                            q=Researchguidence.objects.filter(emp_id=data['emp_id'],id=data['id']).exclude(approve_status="REJECTED").values('emp_id','guidence__value','course__value','degree','degree__value','no_of_students','degree_awarded','status__value','project_title','area_of_spec','approve_status')
                            
                            status=200
                            data_values={'data':list(q)}
                        elif(data['sno']=='3'):
                            q=Books.objects.filter(emp_id=data['emp_id'],id=data['id']).exclude(approve_status="REJECTED").values('emp_id','edition','role__value','role_for__value','publisher_type__value','title','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','approve_status')
                            
                            status=200
                            data_values={'data':list(q)}
                            
                        elif(data['sno']=='2'):
                            
                            q=Researchconference.objects.filter(emp_id=data['emp_id'],id=data['id']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_conference__value','sub_category__value','sponsered','conference_title','paper_title','published_date','organized_by','journal_name','volume_no','issue_no','isbn','page_no','author__value','conference_from','conference_to','other_description','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                            s=Sponsers.objects.filter(type="CONFERENCE",spons_id=data['id'],field_type='SPONSOR',emp_id=data['emp_id']).values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            ##print 'aks',s
                            status=200
                            data_values={'data':list(q),'sponsers':list(s)}
                        elif(data['sno']=='1'):
                            q=Researchjournal.objects.filter(emp_id=data['emp_id'],id=data['id']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_journal__value','sub_category__value','published_date','paper_title','impact_factor','journal_name','volume_no','issue_no','isbn','page_no','author','author__value','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                            
                            status=200
                            data_values={'data':list(q)}

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def rnd_view(request):
    data={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[1357,337])
            if(check == 200):
                data=json.loads(request.body)
                print(data)
                if(data['sno']=='8'):
                    s1=AarDropdown.objects.filter(field='LECTURES AND TALKS').exclude(value=None).values('sno','value')
                    a=[]
                    for i in s1:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a.append({i['value'].replace(' ', '_'):list(query1)})
                    q=LecturesTalks.objects.filter(id=data['id']).exclude(approve_status="REJECTED").values('emp_id','category__value','type__value','organization_sector__value','incorporation_status__value','role__value','date','topic','participants','venue','address','pin_code','contact_number','e_mail','website','approve_status')
                    status=200
                    data_values={'data':list(q),'data1':list(a)}

                elif(data['sno']=='7'):
                    s1=AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM').exclude(value=None).values('sno','value')
                    a1=[]
                    for i in s1:
                       query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                       i['value']=i['value'].replace('-','_')
                       a1.append({i['value'].replace(' ', '_'):list(query1)})
                    q=TrainingDevelopment.objects.filter(id=data['id']).exclude(approve_status="REJECTED").values('emp_id','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaborations','sponsership','approve_status')

                    s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="TRAINING").values('value1__value')

                    s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                    s2=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                    s3=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                    
                    a2=[]
                    for i in s3:
                        query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                        
                        i['value']=i['value'].replace('-','_')
                        a2.append({i['value'].replace(' ', '_'):list(query1)})
                    status=200
                    data_values={'reporting_levels':s1.count(),'reporting_levels1':s2.count(),'data':list(q),'discipline':list(s),'sponsers':list(s1),'association':list(s2),'discipline1':a2,'data1':list(a1)}

                elif(data['sno']=='6'):
                    
                    s=AarDropdown.objects.filter(field='PROJECT / CONSULTANCY').exclude(value=None).values('sno','value')
                    a=[]
                    for i in s:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a.append({i['value'].replace(' ', '_'):list(query1)})
                    q=ProjectConsultancy.objects.filter(id=data['id']).exclude(approve_status="REJECTED").values('emp_id','status__value','type__value','sector__value','title','descreption','start_date','end_date','principal_investigator','principal_investigator_id','co_principal_investigator','co_principal_investigator_id','team_size','sponsored','association','approve_status')
                    
                    s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PROJECT/CONSULTANCY").values('value1__value')
                    
                    s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="PROJECT").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')

                    s3=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION',type="PROJECT").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                    
                    s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                    
                    a2=[]
                    for i in s2:
                        query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                        
                        i['value']=i['value'].replace('-','_')
                        a2.append({i['value'].replace(' ', '_'):list(query1)})
                    status=200
                    data_values={'reporting_levels':s1.count(),'reporting_levels1':s3.count(),'data':list(q),'discipline':list(s),'sponsers':list(s1),'association':list(s3),'data1':a2,'data2':a}

                elif(data['sno']=='5'):
                    q=Patent.objects.filter(id=data['id']).exclude(approve_status="REJECTED").values('title','descreption','collaboration','company_name','incorporate_status__value','status','number','date','owner__value','approve_status','emp_id')

                    s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PATENT").values('value1__value')
                    
                    s1=AarDropdown.objects.filter(field='PATENT').exclude(value=None).values('sno','value')
                    a1=[]
                    for i in s1:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a1.append({i['value'].replace(' ', '_'):list(query1)})
                    # s2=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE').exclude(value=None).values('sno','value')
                    # a2=[]
                    # for i in s2:
                    #     query1=AarDropdown.objects.filter(pid=i['sno'],field="COURSES").exclude(value=None).values('sno','value')
                    #     i['value']=i['value'].replace('-','_')
                    #     a2.append({i['value'].replace(' ', '_'):list(query1)})
                    s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                    
                    a2=[]
                    for i in s2:
                        query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                        
                        i['value']=i['value'].replace('-','_')
                        a2.append({i['value'].replace(' ', '_'):list(query1)})
                    
                    status=200
                    data_values={'data':list(q),'discipline':list(s),'data1':a2,'data2':list(a1)}

                elif(data['sno']=='4'):
                    a=[]
                    s=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE').exclude(value=None).values('sno','value')
                    s2=AarDropdown.objects.filter(field='GUIDANCE',value='RESEARCH (PH. D.)').exclude(value=None).values('sno')
                    s3=AarDropdown.objects.filter(pid=s2).exclude(value=None).values('value','sno')
                    for i in s:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a.append({i['value'].replace(' ', '_'):list(query1)})
                    q=Researchguidence.objects.filter(id=data['id']).exclude(approve_status="REJECTED").values('emp_id','uni_type','uni_name','uni_type__value','guidence__value','course__value','degree','degree__value','no_of_students','degree_awarded','status__value','project_title','area_of_spec','approve_status','date')
                    
                    status=200
                    data_values={'data':list(q),'data1':list(a),'data2':list(s3)}

                elif(data['sno']=='3'):
                    d=AarDropdown.objects.filter(field='BOOKS').exclude(value=None).values('sno','value')
                    a=[]
                    for i in d:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a.append({i['value'].replace(' ', '_'):list(query1)})
                    q=Books.objects.filter(id=data['id']).exclude(approve_status="REJECTED").values('emp_id','edition','role__value','role_for__value','publisher_type__value','title','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','approve_status')
                    
                    status=200
                    data_values={'data':list(q),'data1':list(a)}
                    
                elif(data['sno']=='2'):
                    
                    d=AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE').exclude(value=None).values('sno','value')
                    a=[]
                    for i in d:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a.append({i['value'].replace(' ', '_'):list(query1)})
                    q=Researchconference.objects.filter(id=data['id']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_conference__value','sub_category__value','sponsered','conference_title','paper_title','published_date','organized_by','journal_name','volume_no','issue_no','isbn','page_no','author__value','conference_from','conference_to','other_description','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                    s=Sponsers.objects.filter(type="CONFERENCE",spons_id=data['id'],field_type='SPONSOR',emp_id=data['emp_id']).values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                    ##print 'aks',s
                    status=200
                    data_values={'data':list(q),'sponsers':list(s),'data1':list(a)}

                elif(data['sno']=='1'):
                    d=AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL').exclude(value=None).values('sno','value')
                    a=[]
                    for i in d:
                        query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                        i['value']=i['value'].replace('-','_')
                        a.append({i['value'].replace(' ', '_'):list(query1)})
                    q=Researchjournal.objects.filter(id=data['id']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_journal__value','sub_category__value','published_date','paper_title','impact_factor','journal_name','volume_no','issue_no','isbn','page_no','author','author__value','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                    status=200
                    data_values={'data':list(q),'data1':list(a)}
            else:
                status=403
        else:
            status=401
    else:
        status=500
    #
    return JsonResponse(data_values,safe=False,status=status)

def rnd_approval(request):
    msg={}
    data_values=[]
    data={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[1357,337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    q1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q), 'data1':list(q1)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if(data['test']=='1'):
                        sno=data['data']
                        dept=data['dept']
                        employee=EmployeeDropdown.objects.filter(value='HOD',field="DESIGNATION").values('sno','value')
                        for i in employee:
                            id=i['sno']
                            emps=EmployeePrimdetail.objects.filter(dept=dept).values('emp_id','name','dept__value')
                            ##print emps
                            a=[]
                            data1=[]
                            if(sno=='1'):
                                for emp in emps:
                                    Eid=emp['emp_id']
                                    name=emp['name']
                                    dept=emp['dept__value']

                                    q=Researchjournal.objects.filter(emp_id=Eid,approve_status='APPROVED').values('paper_title','id','emp_id')

                                    b=[]
                                    if(q.count()>0):
                                        for i in q:
                                            d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id']}
                                            b.append(d)
                                        data={'emp_id':Eid,'name':name,'title':b,'dept':dept}
                                        a.append(data)
                                status=200
                                data_values.append({'data':a})

                            elif(sno=='2'):
                                for emp in emps:
                                    Eid=emp['emp_id']
                                    name=emp['name']
                                    dept=emp['dept__value']
                                    q=Researchconference.objects.filter(emp_id=Eid,approve_status='APPROVED').values('paper_title','id')
                                    b=[]
                                    if(q.count()>0):
                                        for i in q:
                                            d={'title':i['paper_title'],'id':i['id']}
                                            b.append(d)
                                        data={'emp_id':Eid,'name':name,'title':b,'dept':dept}
                                        a.append(data)
                                status=200
                                data_values.append({'data':a})

                            elif(sno=='3'):
                                for emp in emps:
                                    Eid=emp['emp_id']
                                    name=emp['name']
                                    dept=emp['dept__value']
                                    q=Books.objects.filter(emp_id=Eid,approve_status='APPROVED').values('title','id')
                                    if(q.count()>0):
                                        data={'emp_id':Eid,'name':name,'title':list(q),'dept':dept}
                                        a.append(data)
                                status=200
                                data_values.append({'data':a})

                            elif(sno=='4'):
                                for emp in emps:
                                    Eid=emp['emp_id']
                                    name=emp['name']
                                    dept=emp['dept__value']
                                    ##print dept
                                    q=Researchguidence.objects.filter(emp_id=Eid,approve_status='APPROVED').values('project_title','id')
                                    b=[]
                                    if(q.count()>0):
                                        for i in q:
                                            d={'title':i['project_title'],'id':i['id']}
                                            b.append(d)
                                        data={'emp_id':Eid,'name':name,'title':b,'dept':dept}
                                        a.append(data)
                                status=200
                                data_values.append({'data':a})


                            elif(sno=='5'):
                                for emp in emps:
                                    Eid=emp['emp_id']
                                    name=emp['name']
                                    dept=emp['dept__value']
                                    q=Patent.objects.filter(emp_id=Eid,approve_status='APPROVED').values('title','id')
                                    if(q.count()>0):
                                        data={'emp_id':Eid,'name':name,'title':list(q),'dept':dept}
                                        a.append(data)
                                s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                                ##print(s2)
                                a2=[]
                                for i in s2:
                                    query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                    ##print(query1)
                                    i['value']=i['value'].replace('-','_')
                                    a2.append({i['value'].replace(' ', '_'):list(query1)})
                                status=200
                                data_values.append({'data':a,'data1':a2})
                                #data_values={'data':a,'data1':a2}

                            elif(sno=='6'):
                                for emp in emps:
                                    Eid=emp['emp_id']
                                    name=emp['name']
                                    dept=emp['dept__value']
                                    c=0
                                    q=ProjectConsultancy.objects.filter(emp_id=Eid,approve_status='APPROVED').values('title','id')
                                    c=ProjectConsultancy.objects.filter(emp_id=Eid,approve_status='APPROVED').values('title').count()
                                    if(c>0):
                                        data={'emp_id':Eid,'name':name,'title':list(q),'dept':dept}
                                        a.append(data)
                                status=200
                                data_values.append({'data':a})

                            elif(sno=='7'):
                                for emp in emps:
                                    Eid=emp['emp_id']
                                    name=emp['name']
                                    dept=emp['dept__value']
                                    q=TrainingDevelopment.objects.filter(emp_id=Eid,approve_status='APPROVED').values('title','id')
                                    if(q.count()>0):
                                        data={'emp_id':Eid,'name':name,'title':list(q),'dept':dept}
                                        a.append(data)
                                status=200
                                data_values.append({'data':a})

                            elif(sno=='8'):
                                for emp in emps:
                                    Eid=emp['emp_id']
                                    name=emp['name']
                                    dept=emp['dept__value']
                                    q=LecturesTalks.objects.filter(emp_id=Eid,approve_status='APPROVED').values('topic','id')
                                    b=[]
                                    if(q.count()>0):
                                        for i in q:
                                            d={'title':i['topic'],'id':i['id']}
                                            b.append(d)
                                        data={'emp_id':Eid,'name':name,'title':b,'dept':dept}
                                        a.append(data)
                                status=200
                                data_values.append({'data':a})
                    elif(data['test']=='2'):
                        if(data['sno']=='1'):
                            
                            q=Researchjournal.objects.filter(emp_id=data['emp_id'],paper_title=data['title']).update(final_status='APPROVED')
                        if(data['sno']=='2'):
                            
                            q=Researchconference.objects.filter(emp_id=data['emp_id'],paper_title=data['title']).update(final_status='APPROVED')
                        if(data['sno']=='3'):
                            
                            q=Books.objects.filter(emp_id=data['emp_id'],title=data['title']).update(final_status='APPROVED')
                        if(data['sno']=='4'):
                            
                            q=Researchguidence.objects.filter(emp_id=data['emp_id'],project_title=data['title']).update(final_status='APPROVED')
                        if(data['sno']=='5'):
                            
                            q=Patent.objects.filter(emp_id=data['emp_id'],title=data['title']).update(final_status='APPROVED')
                        if(data['sno']=='6'):
                            
                            q=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],title=data['title']).update(final_status='APPROVED')
                        if(data['sno']=='7'):
                            
                            q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],title=data['title']).update(final_status='APPROVED')
                        if(data['sno']=='8'):
                            
                            q=LecturesTalks.objects.filter(emp_id=data['emp_id'],topic=data['title']).update(final_status='APPROVED')
                        status=200
                        data_values={"OK":"DATA updated Successfully"}
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    #
    return JsonResponse(data_values,safe=False,status=status)

def rnd_tabledata(request):
    data_values=[]
    data=[]

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337,1357])
            if(check==200):
                if(request.method=='POST'):
                    data=json.loads(request.body)
                    print(data)
                    q=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                  
                    for j in data:
                        if j=='1':
                            total_count=0
                            a=[]
                            for i in q:
                                dept=i['sno']
                                q1=Researchjournal.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('paper_title').count()
                                total_count=total_count+q1
                                a.append({'type':'1','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                            data_values.append(a)
                            status=200
        
                        elif j=='2':
                            total_count=0
                            a=[]
                            for i in q:
                                dept=i['sno']
                                q1=Researchconference.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('paper_title').count()
                                total_count=total_count+q1
                                a.append({'type':'2','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                            data_values.append(a)

                            status=200

                        elif j=='3':
                            total_count=0
                            a=[]
                            for i in q:
                                dept=i['sno']
                                q1=Books.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                                total_count=total_count+q1
                                a.append({'type':'3','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                            data_values.append(a)
                            status=200

                        elif j=='4':
                            total_count=0
                            a=[]
                            for i in q:
                                dept=i['sno']
                                q1=Researchguidence.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                                total_count=total_count+q1
                                a.append({'type':'4','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                                data_values.append(a)
                            status=200

                        elif j=='5':
                            total_count=0
                            a=[]
                            for i in q:
                                dept=i['sno']
                                q1=Patent.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                                total_count=total_count+q1
                                a.append({'type':'5','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                                data_values.append(a)
                            status=200

                        elif j=='6':
                            total_count=0
                            a=[]
                            for i in q:
                                dept=i['sno']
                                q1=ProjectConsultancy.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                                a.append({'type':'6','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                                data_values.append(a)
                            status=200

                        elif j=='7':
                            total_count=0
                            a=[]
                            for i in q:
                                dept=i['sno']
                                q1=TrainingDevelopment.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                                total_count=total_count+q1
                                a.append({'type':'7','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                                data_values.append(a)
                            status=200

                        elif j=='8':
                            total_count=0
                            a=[]
                            for i in q:
                                dept=i['sno']
                                q1=LecturesTalks.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                                total_count=total_count+q1
                                data_values.append({'type':'8','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                            status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def web_rnd_tabledata(request):
    data_values=[]
    data=[]


    if(request.method=='GET'):
        #data=json.loads(request.body)
        q=EmployeeDropdown.objects.filter(field="DEPARTMENT",sno__lte=576).exclude(value=None).values('sno','value')
        #data=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
        status=200

        data=['1','2','3','4','5','6','7','8']
        for j in data:
            if j=='1':
                total_count=0
                a=[]
                for i in q:
                    dept=i['sno']
                    q1=Researchjournal.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('paper_title').count()
                    total_count=total_count+q1
                    a.append({'type':'1','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                data_values.append(a)
                status=200

            elif j=='2':
                total_count=0
                a=[]
                for i in q:
                    dept=i['sno']
                    q1=Researchconference.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('paper_title').count()
                    total_count=total_count+q1
                    a.append({'type':'2','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                data_values.append(a)

                status=200

            elif j=='3':
                total_count=0
                a=[]
                for i in q:
                    dept=i['sno']
                    q1=Books.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                    total_count=total_count+q1
                    a.append({'type':'3','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                data_values.append(a)
                status=200

            elif j=='4':
                total_count=0
                a=[]
                for i in q:
                    dept=i['sno']
                    q1=Researchguidence.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                    total_count=total_count+q1
                    a.append({'type':'4','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                data_values.append(a)
                status=200

            elif j=='5':
                total_count=0
                a=[]
                for i in q:
                    dept=i['sno']
                    q1=Patent.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                    total_count=total_count+q1
                    a.append({'type':'5','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                data_values.append(a)
                status=200

            elif j=='6':
                total_count=0
                a=[]
                for i in q:
                    dept=i['sno']
                    q1=ProjectConsultancy.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                    a.append({'type':'6','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                data_values.append(a)
                status=200

            elif j=='7':
                total_count=0
                a=[]
                for i in q:
                    dept=i['sno']
                    q1=TrainingDevelopment.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                    total_count=total_count+q1
                    a.append({'type':'7','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                data_values.append(a)
                status=200

            elif j=='8':
                total_count=0

                a=[]
                for i in q:
                    dept=i['sno']
                    q1=LecturesTalks.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
                    total_count=total_count+q1
                    a.append({'type':'8','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
                data_values.append(a)
                status=200
            print(data_values)
    else:
        status=502

    # if 'HTTP_COOKIE' in request.META:
    #     if request.user.is_authenticated:
    #         check = checkpermission(request,[337,1357])
    #         if(check==200):

    #             if(request.method=='POST'):
    #                 data=json.loads(request.body)
    #                 q=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
    #                 data=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                  
    #                 for j in data:
    #                     if j=='1':
    #                         total_count=0
    #                         a=[]
    #                         for i in q:
    #                             dept=i['sno']
    #                             q1=Researchjournal.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('paper_title').count()
    #                             total_count=total_count+q1
    #                             a.append({'type':'1','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
    #                         data_values.append(a)
    #                         status=200

    #                     elif j=='2':
    #                         total_count=0
    #                         a=[]
    #                         for i in q:
    #                             dept=i['sno']
    #                             q1=Researchconference.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('paper_title').count()
    #                             total_count=total_count+q1
    #                             a.append({'type':'2','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
    #                         data_values.append(a)

    #                         status=200

    #                     elif j=='3':
    #                         total_count=0
    #                         a=[]
    #                         for i in q:
    #                             dept=i['sno']
    #                             q1=Books.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
    #                             total_count=total_count+q1
    #                             a.append({'type':'3','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
    #                         data_values.append(a)
    #                         status=200

    #                     elif j=='4':
    #                         total_count=0
    #                         for i in q:
    #                             dept=i['sno']
    #                             q1=Researchguidence.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
    #                             total_count=total_count+q1
    #                             data_values.append({'type':'4','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
    #                         status=200

    #                     elif j=='5':
    #                         total_count=0
    #                         for i in q:
    #                             dept=i['sno']
    #                             q1=Patent.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
    #                             total_count=total_count+q1
    #                             data_values.append({'type':'5','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
    #                         status=200

    #                     elif j=='6':
    #                         total_count=0
    #                         for i in q:
    #                             dept=i['sno']
    #                             q1=ProjectConsultancy.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
    #                             data_values.append({'type':'6','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
    #                         status=200

    #                     elif j=='7':
    #                         total_count=0
    #                         for i in q:
    #                             dept=i['sno']
    #                             q1=TrainingDevelopment.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
    #                             total_count=total_count+q1
    #                             data_values.append({'type':'7','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
    #                         status=200

    #                     elif j=='8':
    #                         total_count=0
    #                         for i in q:
    #                             dept=i['sno']
    #                             q1=LecturesTalks.objects.filter(emp_id__dept=dept,approve_status='APPROVED').values('id').count()
    #                             total_count=total_count+q1
    #                             data_values.append({'type':'8','dept_id':i['sno'],'dept_value':i['value'],'no.':q1})
    #                         status=200
    #             else:
    #                 status=502
    #         else:
    #             status=403
    #     else:
    #         status=401
    # else:
    #     status=500
    return JsonResponse(data_values,safe=False,status=status)


def rnd_update(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337,1357])
            if(check==200):
                if(request.method=='POST'):
                    
                    data=json.loads(request.body.decode("utf-8"))
                    if(data['sno']=='1'):
                        pid=data["id"]
                        category=data["category"]
                        emp_id=request.session["hash1"]
                        type_of_journal=data["typeofjournal"]
                        sub_category=data["subcategory"]
                        paper_title=data["papertitle"]
                        impact_factor=data["impacttext"]
                        date=data["dateofpub"]
                        ###print(published_date)
                        date=date.split('T')
                        ###print(date)
                        Published_date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        ###print(Published_date)
                        journal_name=data["journalname"]
                        volume_no=data["volumeno"]
                        issue_no=data["issueno"]
                        ###print issue_no
                        isbn=data["isbn"]
                        page_no=data["pageno"]
                        author=data["typeofAuthor"]
                        publisher_name=data["publishername"]
                        publisher_address1=data["publisheraddL1"]
                        publisher_address2=data["publisheraddL2"]
                        if publisher_address2 is None:
                            publisher_address2=""
                        publisher_zip_code=data["zipc"]
                        publisher_contact=data["phone"]
                        publisher_email=data["eml"]
                        publisher_website=data["website"]
                        if 'subcatText' in data:
                            others=data["subcatText"]
                        else:
                            others=None
                        emp_id=data["emp_id"]
                        q=Researchjournal.objects.filter(id=pid).update(category=category,type_of_journal=type_of_journal,sub_category=sub_category,published_date=Published_date,paper_title=paper_title,impact_factor=impact_factor,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,author=author,publisher_name=publisher_name,publisher_address1=publisher_address1,publisher_address2=publisher_address2,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,others=others,t_date=datetime.datetime.now())
                            # q=Researchjournal.objects.filter(id=pid).update(category=AarDropdown.objects.get(sno=category),author=AarDropdown.objects.get(sno=author),type_of_journal=AarDropdown.objects.get(sno=type_of_journal),sub_category=AarDropdown.objects.get(sno=sub_category),others=others,paper_title=paper_title,published_date=Published_date,impact_factor=impact_factor,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,publisher_name=publisher_name,publisher_address1=publisher_address1,publisher_address2=publisher_address2,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),approve_status='PENDING',t_date=str(datetime.datetime.now()))
                        data_values={"OK":"DATA Updated Successfully"}
                        status=200
                    elif(data['sno']=='2'):
                        
                        print(data)
                        pid=data["id"]
                        category=data["category"]

                        type_of_conference=data["type"]
                        #sub_category=data["subCategory"]
                        if 'sponsered' in data:
                            sponsered=data["sponsered"]
                        else:
                            sponsered=None
                        if  'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers=None
                        conference_title=data["titleConference"]
                        paper_title=data["titlePaper"]
                        published_date=data["dateOfPublish"]
                        organized_by=data["organised"]
                        if 'journalName' in data:
                            ###print("hii")
                            journal_name=data["journalName"]
                        else:
                            journal_name=None

                        if 'volume' in data:
                            volume_no=data["volume"]
                        else:
                            volume_no=None

                        if 'issue' in data:
                            issue_no=data["issue"]
                        else:
                            issue_no=None

                        if 'issn' in data:
                            isbn=data["issn"]
                        else:
                            isbn=None
                        if 'page' in data:
                            page_no=data["page"]
                        else:
                            page_no=None

                        author=data["author"]
                        conference_from=data["fromDate"].split('T')[0]
                        conference_to=data["toDate"].split('T')[0]
                        other_description=data["description"]
                        publisher_name=data["publisherName"]
                        publisher_address=data["publisherAddress"]
                        publisher_zip_code=data["publisherPincode"]
                        publisher_contact=data["publisherContact"]
                        publisher_email=data["publisherEmail"]
                        publisher_website=data["publisherWebsite"]
                        published_date=data["dateOfPublish"]
                        approve_status='APPROVED'
                        ###print(conference_from)
                        ###print(conference_to)
                        if 'others' in data:
                            others=data["others"]
                        else:
                            others=None
                            ###print "hii"
                        emp_id=data["emp_id"]
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        published_date=datetime.datetime.strptime(published_date,'%Y-%m-%d').date()
                        q=Researchconference.objects.filter(id=pid).update(category=category,type_of_conference=type_of_conference,sponsered=sponsered,conference_title=conference_title,paper_title=paper_title,published_date=published_date,organized_by=organized_by,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,author=author,conference_from=conference_from,conference_to=conference_to,other_description=other_description,publisher_name=publisher_name,publisher_address=publisher_address,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,others=others,t_date=datetime.datetime.now())
                        
                        data_values={"OK":"DATA Updated Successfully"}
                        status=200

                    elif(data['sno']=='3'):
                        pid=data["id"]
                        role=data['role']
                        for_type=data['for_type']
                        publisher=data['publisher']
                        copyright_no=data['copyright_no']
                        copyright_status=data['copyright_status']
                        if 'title' in data:
                            title=data['title']
                        else:
                            title=None
                        if 'chapter' in data:
                            chapter=data['chapter']
                        else:
                            chapter=None
                        publisher_name=data['publisher_name']
                        publisher_add=data['publisher_add']
                        edition=data['edition']
                        date=data['date']
                        publisher_email=data['publisher_email']
                        ['author']
                        author=data['author']
                        ###print(author)
                        publisher_website=data['publisher_website']
                        isbn=data['isbn']
                        publisher_code=data['publisher_code']
                        publisher_contact=data['publisher_contact']
                        approve_status='APPROVED'
                        emp_id=data['emp_id']
                        role_type_new=AarDropdown.objects.get(sno=role)
                        for_type_new=AarDropdown.objects.get(sno=for_type)
                        publisher_new=AarDropdown.objects.get(sno=publisher)
                        date=date.split('T')
                        date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        Books.objects.filter(id=pid).update(role=role_type_new,role_for=for_type_new,publisher_type=publisher_new,title=title,edition=edition,published_date=date,chapter=chapter,isbn=isbn,copyright_status=copyright_status,copyright_no=copyright_no,author=author,publisher_name=publisher_name,publisher_address=publisher_add,publisher_zip_code=publisher_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,approve_status=approve_status)
                        data_values={"OK":"DATA Updated Successfully"}
                        status=200

                    elif(data['sno']=='4'):
                        ##print data
                        pid=data["id"]
                        course=data['Course']
                        degree=data['Degree']
                        degree_awarded=data['Degree_awarded']
                        guid=data['Guidance']
                        no_stud=data['No_of_Students']
                        a_o_s=data['area_of_specialization']
                        title=data['project_title']
                        status=data['status']
                        uni_type=data['uni_type']
                        uni_name=data['uni_name']
                        emp_id=data['emp_id']
                        date=datetime.datetime.strptime(data['date'],'%Y-%m-%d').date()
                        print(data)
                        approve_status='APPROVED'
                        if guid:
                            if(course!=None):
                                Researchguidence.objects.filter(id=pid).update(guidence=guid,course=course,degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,approve_status=approve_status,uni_type=uni_type,uni_name=uni_name,date=date)
                                data_values={"OK":"COURSE Inserted Successfully"}
                                status=200

                            elif(degree!=None):
                                Researchguidence.objects.filter(id=pid).update(guidence=guid,degree=degree,degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,approve_status=approve_status,uni_type=uni_type,uni_name=uni_name,date=date)
                                data_values={"OK":"DEGREE Inserted Successfully"}
                                status=200

                            elif(status!=None):
                                Researchguidence.objects.filter(id=pid).update(guidence=guid,status=status,degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,approve_status=approve_status,uni_type=uni_type,uni_name=uni_name,date=date)
                                data_values={"OK":"DATA Updated Successfully"}
                                status=200

                    elif(data['sno']=='5'):
                        
                        pid=data["id"]
                        emp_id=data["emp_id"]
                        if 'discipline' in data:
                            discipline=data["discipline"]
                        else:
                            discipline=None
                        collaboration=data["collaboration"]
                        if 'company' in data:
                            company_name=data["company"]
                        else:
                            company_name=None
                        if 'incorporate' in data:
                            if data['incorporate']!=None:
                                incorporate_status=AarDropdown.objects.get(sno=data['incorporate'])
                            else:
                                incorporate_status=None
                        else:
                            incorporate_status=None
                        if 'status' in data:
                            status=data["status"]
                        else:
                            status=None
                        if 'number' in data:
                            number=data["number"]

                        else:
                            number=None
                        date=data["date"]
                        date=date.split('T')
                        date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        owner=AarDropdown.objects.get(sno=data['owner'])
                        title=data["title"]
                        descreption=data["desc"]
                        approve_status='APPROVED'
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:

                            if date>Doj:
                                Patent.objects.filter(id=pid).update(title=title,incorporate_status=incorporate_status,owner=owner,collaboration=collaboration,company_name=company_name,status=status,number=number,date=date,approve_status=approve_status)
                                sno=Patent.objects.filter(id=pid,title=title).values('id')
                                if sno.count()>0:
                                    Discipline.objects.filter(id=pid,type="PATENT").delete()
                                if  discipline!=None:
                                    for i in discipline:
                                        Discipline.objects.create(id=sno[0]['id'],emp_id=emp_id,value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="PATENT")
                                data_values={"OK":"DATA Updated Successfully"}
                                status=200

                    if(data['sno']=='6'):
                        #emp_id=request.session['hash1']
                        # ##print emp_id
                        pid=data["id"]
                        if 'p_status' in data:
                            status=data["p_status"]
                        else:
                            status=None
                        sector=data["sector"]
                        start_date=data["start_date"]
                        type=data["type"]
                        end_date=data["end_date"]
                        if 'principal' in data:
                            principal=data["principal"]
                            if principal=='self':
                                principal_id=data['emp_id']
                            elif principal=='other':
                                principal_id=data['principal_id']
                        else:
                            principal=None
                        if 'co_principal' in data:
                            co_principal=data["co_principal"]
                            if co_principal=='self':
                                co_principal_id=data['emp_id']
                            elif co_principal=='other':
                                co_principal_id=data['co_principal_id']
                        else:
                            co_principal=None
                        team_size=data["team_size"]
                        sponsored=data["sponsored"]
                        association=data["association"]
                        if 'organisation' in data:
                            organisation=data["organisation"]
                        else:
                            organisation=None
                        if 'contact_person' in data:
                            contact_person=data["contact_person"]
                        else:
                            contact_person=None
                        if 'address' in data:
                            address=data['address']
                        else:
                            address=None
                        if 'e_mail' in data:
                            e_mail=data["e_mail"]
                        else:
                            e_mail=None
                        if 'pin_code' in data:
                            pin_code=data["pin_code"]
                        else:
                            pin_code=None
                        if 'contact_number' in data:
                            contact_number=data["contact_number"]
                        else:
                            contact_number=None
                        if 'website' in data:
                            website=data["website"]
                        else:
                            website=None
                        if 'amount' in data:
                            amount=data['amount']
                        else:
                            amount=None
                        if 'organisation1' in data:
                            organisation1=data["organisation1"]
                        else:
                            organisation1=None
                        if 'contact_person1' in data:
                            contact_person1=data["contact_person1"]
                        else:
                            contact_person1=None
                        if 'address1' in data:
                            address1=data['address1']
                        else:
                            address1=None
                        if 'e_mail1' in data:
                            e_mail1=data["e_mail1"]
                        else:
                            e_mail1=None
                        if 'pin_code1' in data:
                            pin_code1=data["pin_code1"]
                        else:
                            pin_code1=None
                        if 'contact_number1' in data:
                            contact_number1=data["contact_number1"]
                        else:
                            contact_number1=None
                        if 'website1' in data:
                            website1=data["website1"]
                        else:
                            website1=None
                        if 'amount1' in data:
                            amount1=data['amount1']
                        else:
                            amount1=None
                        if 'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers=None
                        if 'sponsers2' in data:
                            sponsers2=data['sponsers2']
                        else:
                            sponsers2=None
                        title=data["title"]
   
                        descreption=data["descreption"]
                        approve_status='APPROVED'
                        emp_id=data["emp_id"]
                        discipline=data["discipline"]
                        from_d= start_date.split('T')
                        to_d= end_date.split('T')
                        start_date =datetime.datetime.strptime(from_d[0],'%Y-%m-%d').date()
                        end_date=datetime.datetime.strptime(to_d[0],'%Y-%m-%d').date()
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:
                            if start_date>Doj:
                                ProjectConsultancy.objects.filter(id=pid).update(type=type,sector=sector,status=status,title=title,descreption=descreption,start_date=start_date,end_date=end_date,principal_investigator=principal,co_principal_investigator=co_principal,principal_investigator_id=principal_id,co_principal_investigator_id=co_principal_id,team_size=team_size,sponsored=sponsored,association=association,approve_status=approve_status)
                                sno=ProjectConsultancy.objects.filter(id=pid,title=title).values('id')
                                ##print(sno)
                                if sno.count()>0:
                                    Discipline.objects.filter(id=pid,type='PROJECT/CONSULTANCY').delete()
                                    Sponsers.objects.filter(spons_id=sno[0]['id']).delete()
                                if(sponsored=="yes"):
                                    for i in sponsers:
                                        print(i)
                                        Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=data['emp_id'],sponser_name=i["organisation"],type="PROJECT",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='SPONSOR')
                                if(association=="yes"):
                                    for i in sponsers2:
                                        Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=data['emp_id'],sponser_name=i["organisation1"],type="PROJECT",contact_person=i['contact_person1'],contact_number=i['contact_number1'],e_mail=i['e_mail1'],website=i['website1'],amount=i['amount1'],address=i['address1'],pin_code=i['pin_code1'],field_type='ASSOCIATION')
                                if  discipline!=None:
                                    for i in discipline:
                                        Discipline.objects.create(id=sno[0]['id'],emp_id=data['emp_id'],value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="PROJECT/CONSULTANCY")
                                data_values={"OK":"DATA Updated Successfully"}
                                status=200
                    elif(data['sno']=='7'):
                        ##print data
                        pid=data["id"]
                        category=data["category"]
                        type=data["type"]
                        organization=data["organization"]
                        incorporation=data["status"]
                        role=data["role"]
                        attended=data["attend"]
                        organizers=data["organizer"]
                        participants=data["participants"]
                        venue=data["venue"]

                        if 'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers= None
                        if 'collaboration' in data:
                            collaborations=data["collaboration"]
                        else:
                            collaboration= None
                        if 'organisation' in data:
                            organisation=data["organisation"]
                        else:
                            organisation=None
                        if 'contact_person' in data:
                            contact_person=data["contact_person"]
                        else:
                            contact_person=None
                        if 'address' in data:
                            address=data['address']
                        else:
                            address=None
                        if 'e_mail' in data:
                            e_mail=data["e_mail"]
                        else:
                            e_mail=None
                        if 'pin_code' in data:
                            pin_code=data["pin_code"]
                        else:
                            pin_code=None
                        if 'contact_number' in data:
                            contact_number=data["contact_number"]
                        else:
                            contact_number=None
                        if 'website' in data:
                            website=data["website"]
                        else:
                            website=None
                        if 'amount' in data:
                            amount=data['amount']
                        else:
                            amount=None
                        if 'organisation1' in data:
                            organisation1=data["organisation1"]
                        else:
                            organisation1=None
                        if 'contact_person1' in data:
                            contact_person1=data["contact_person1"]
                        else:
                            contact_person1=None
                        if 'address1' in data:
                            address1=data['address1']
                        else:
                            address1=None
                        if 'e_mail1' in data:
                            e_mail1=data["e_mail1"]
                        else:
                            e_mail1=None
                        if 'pin_code1' in data:
                            pin_code1=data["pin_code1"]
                        else:
                            pin_code1=None
                        if 'contact_number1' in data:
                            contact_number1=data["contact_number1"]
                        else:
                            contact_number1=None
                        if 'website1' in data:
                            website1=data["website1"]
                        else:
                            website1=None
                        if 'amount1' in data:
                            amount1=data['amount1']
                        else:
                            amount1=None
                        if 'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers=None
                        if 'sponsers2' in data:
                            sponsers2=data['sponsers2']
                        else:
                            sponsers2=None
                        if 'sponsership' in data:
                            sponsership=data['sponsership']
                        else:
                            sponsership=None
                        if 'discipline' in data:
                            discipline=data["discipline"]
                        else:
                            discipline=None
                        from_date=data["from_date"]
                        to_date=data["to_date"]
                        title=data["title"]
                        prev_title=data['prev_title']
                        emp_id=data['emp_id']
                        #sponsership="No"
                        from_d= from_date.split('T')
                        to_d= to_date.split('T')
                        from_date=datetime.datetime.strptime(from_d[0],'%Y-%m-%d').date()
                        to_date=datetime.datetime.strptime(to_d[0],'%Y-%m-%d').date()
                        approve_status='APPROVED'
                        doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        d=str(doj[0]['doj'])
                        Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                        if Doj!=None:
                            if from_date>Doj:
                                q=TrainingDevelopment.objects.filter(id=pid).update(category=category,type=type,role=role,incorporation_status=incorporation,organization_sector=organization,from_date=from_date,to_date=to_date,participants=participants,venue=venue,title=title,organizers=organizers,attended=attended,collaborations=collaborations,approve_status=approve_status,sponsership=sponsership)
                                sno=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],title=title).values('id')

                                if sno.count()>0:
                                    Sponsers.objects.filter(spons_id=sno[0]['id'],emp_id=data['emp_id'],type="TRAINING").delete()
                                    Discipline.objects.filter(emp_id=data['emp_id'],type="TRAINING",id=sno[0]['id']).delete()

                                if(collaborations=="yes"):
                                    for i in sponsers:
                                        Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=data['emp_id'],sponser_name=i["organisation"],type="TRAINING",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='COLLABORATION')
                                if(sponsership=="yes"):
                                    for i in sponsers2:
                                        Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=data['emp_id'],sponser_name=i["organisation1"],type="TRAINING",contact_person=i['contact_person1'],contact_number=i['contact_number1'],e_mail=i['e_mail1'],website=i['website1'],amount=i['amount1'],address=i['address1'],pin_code=i['pin_code1'],field_type='SPONSOR')
                                if  discipline!=None:
                                    for i in discipline:
                                        Discipline.objects.create(id=sno[0]['id'],emp_id=data['emp_id'],value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="TRAINING")
                                data_values={"OK":"DATA Updated Successfully"}
                                status=200

                    elif(data['sno']=='8'):

                        pid=data["id"]
                        if 'category' in data:
                            category=AarDropdown.objects.get(sno=data['category'])
                        else:
                            category=None
                        
                        if 'type' in data:
                            type=AarDropdown.objects.get(sno=data["type"])
                        else:
                            type=None
                        if 'organization' in data:
                            organization=AarDropdown.objects.get(sno=data["organization"])
                        else:
                            organization=None
                        if 'incorporation' in data:
                            incorporation=AarDropdown.objects.get(sno=data["incorporation"])
                        else:
                            incorporation=None
                        if 'role' in data:
                            role=AarDropdown.objects.get(sno=data["role"])
                        else:
                            role=None
                        if 'date' in data:
                            date=data["date"]
                            date=date.split('T')
                            date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                        else:
                            date=None
                        if 'topic' in data:
                            topic=data["topic"].upper()
                        else:
                            topic=None
                        if 'prev_topic' in data:
                            prev_topic=data["prev_topic"]
                        else:
                            prev_topic=None
                        if 'participants' in data:
                           participants=data["participants"]
                        else:
                             participants=None
                        if 'venue' in data:
                            venue=data["venue"]
                        else:
                            venue=None
                        if 'address' in data:
                            address=data['address']
                        else:
                            address=None
                        if 'e_mail' in data:
                           e_mail=data["e_mail"]  
                        else:
                            e_mail=None
                        if 'pin_code' in data:
                            pin_code=data["pin_code"]
                        else:
                            pin_code=None
                        if 'contact_number' in data:
                           contact_number=data["contact_number"]
                        else:
                            contact_number=None
                        if 'website' in data:
                            website=data["website"]
                        else:
                            website=None

                        emp_id=data["emp_id"]
                        approve_status='APPROVED'

                        LecturesTalks.objects.filter(id=pid).update(category=category,type=type,role=role,incorporation_status=incorporation,organization_sector=organization,date=date,topic=topic,participants=participants,venue=venue,address=address,pin_code=pin_code,contact_number=contact_number,e_mail=e_mail,website=website)
                        data_values={"OK":"DATA Updated Successfully"}
                        status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    #
    return JsonResponse(data_values,safe=False,status=status)


def rnd_reject(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337,425])
            if(check == 200):
                data = json.loads(request.body.decode('utf-8'))
                id=data['id']
                if(data['sno']=='1'):
                            
                    q=Researchjournal.objects.filter(emp_id=data['emp_id'],id=id).update(approve_status='REJECTED')
                if(data['sno']=='2'):
                    
                    q=Researchconference.objects.filter(emp_id=data['emp_id'],id=id).update(approve_status='REJECTED')
                if(data['sno']=='3'):
                    
                    q=Books.objects.filter(emp_id=data['emp_id'],id=id).update(approve_status='REJECTED')
                if(data['sno']=='4'):
                    
                    q=Researchguidence.objects.filter(emp_id=data['emp_id'],id=id).update(approve_status='REJECTED')
                if(data['sno']=='5'):
                    
                    q=Patent.objects.filter(emp_id=data['emp_id'],id=id).update(approve_status='REJECTED')
                if(data['sno']=='6'):
                    
                    q=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],id=id).update(approve_status='REJECTED')
                if(data['sno']=='7'):
                    
                    q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],id=id).update(approve_status='REJECTED')
                if(data['sno']=='8'):
                    
                    q=LecturesTalks.objects.filter(emp_id=data['emp_id'],id=id).update(approve_status='REJECTED')
                status=200
                data_values={"OK":"DATA updated Successfully"}
            else:
                status=403
        else:
            status=401
    else:
        status=500
    #
    return JsonResponse(data_values,safe=False,status=status)

def deanaar_report(request):

    msg={}
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337,425])
            if(check == 200):
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    
                    if(data['test']=='3'):
                        if 'dept' in data:
                            dept=data['dept']
                        else:
                            dept=None
                        if 'data1' in data:
                            date=data['data1']
                        else:
                            date=None
                        if 'data' in data:
                            sno=data['data']
                        else:
                            sno=None
                        date=date.split('-')
                        ###print date
                        ###print "hiiiiii"
                        m=str(date[1])
                        y=str(date[0])
                        m=int(m)
                        y=int(y)
                        if(m==12):
                            m=1
                            y+=1
                        else:
                            m+=1
                        from_date=str(y)+'-'+str(m)+'-'+'1'
                        date_from=datetime.datetime.strptime(from_date,'%Y-%m-%d').date()
                        first=[1,3,5,7,8,10,12]
                        second=[4,6,9,11]
                        if m in first:
                            to_date=str(y)+'-'+str(m)+'-'+'31'
                            date_to=datetime.datetime.strptime(to_date,'%Y-%m-%d').date()
                        if m in second:
                            to_date=str(y)+'-'+str(m)+'-'+'30'
                            date_to=datetime.datetime.strptime(to_date,'%Y-%m-%d').date()
                        if m==2:
                            if (y%400==0 or y%4==0):
                                to_date=str(y)+'-'+str(m)+'-'+'29'
                                date_to=datetime.datetime.strptime(to_date,'%Y-%m-%d').date()
                            else:
                                to_date=str(y)+'-'+str(m)+'-'+'28'
                                date_to=datetime.datetime.strptime(to_date,'%Y-%m-%d').date()
                        emps=EmployeePrimdetail.objects.filter(dept=dept).values('emp_id','name')
                        a=[]
                        if(sno=='1'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED'),Q(t_date__gte=date_from) & Q(t_date__lte=date_to),emp_id=Eid).values('paper_title','id','emp_id')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id']}
                                        b.append(d)
                            data={'data':b}
                            a.append(data)

                        elif(sno=='2'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchconference.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED'),Q(t_date__gte=date_from) & Q(t_date__lte=date_to),emp_id=Eid).values('paper_title','id','emp_id')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id']}
                                        b.append(d)
                            data={'data':b}
                            a.append(data)

                        elif(sno=='3'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Books.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED'),Q(t_date__gte=date_from) & Q(t_date__lte=date_to),emp_id=Eid).values('title','id','emp_id','chapter')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'chapter':i['chapter']}
                                        b.append(d)
                            data={'data':b}
                            a.append(data)

                        elif(sno=='4'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchguidence.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED'),Q(t_date__gte=date_from) & Q(t_date__lte=date_to),emp_id=Eid).values('project_title','id','emp_id','guidence')
                                if(q.count()>0):
                                    for i in q:
                                        try:
                                            d={'title':i['project_title'],'id':i['id'],'emp_id':i['emp_id'],'guidence':i['guidence']}
                                            b.append(d)
                                        except:
                                            a=10
                                            ##print ("hi")
                            data={'data':b}
                            a.append(data)

                        elif(sno=='5'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Patent.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED'),Q(t_date__gte=date_from) & Q(t_date__lte=date_to),emp_id=Eid).values('title','id','emp_id')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id']}
                                        b.append(d)
                            data={'data':b}
                            a.append(data)

                        elif(sno=='6'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                c=0
                                q=ProjectConsultancy.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED'),Q(t_date__gte=date_from) & Q(t_date__lte=date_to),emp_id=Eid).values('title','id','emp_id')
                                c=q.count()
                                if(c>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id']}
                                        b.append(d)
                            data={'data':b}
                            a.append(data)

                        elif(sno=='7'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                qi=TrainingDevelopment.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED')).filter(Q(t_date__gte=date_from) & Q(t_date__lte=date_to),emp_id=Eid).values('title','id','emp_id')
                                ##print(qi.query)
                                if(len(qi)>0):
                                    for i in qi:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id']}
                                        b.append(d)
                            data={'data':b}
                            a.append(data)

                        elif(sno=='8'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=LecturesTalks.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),Q(t_date__gte=date_from) & Q(t_date__lte=date_to),emp_id=Eid).values('topic','id','emp_id')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['topic'],'id':i['id'],'emp_id':i['emp_id']}
                                        b.append(d)
                            data={'data':b}
                            a.append(data)
                        status=200
                        data_values={'data':a}
                    elif(data['test']=='4'):
                        if(data['sno']=='8'):
                            #
                            q=LecturesTalks.objects.filter(emp_id=data['emp_id'],topic=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type__value','organization_sector__value','incorporation_status__value','role__value','date','topic','participants','venue','address','pin_code','contact_number','e_mail','website','approve_status')
                            s1=AarDropdown.objects.filter(field='LECTURES AND TALKS').exclude(value=None).values('sno','value')
                            a=[]
                            for i in s1:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            data_values={'data':list(q),'data1':a}
                        elif(data['sno']=='7'):
                            q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaborations','sponsership','approve_status')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="TRAINING").values('value1__value')
                            s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s2=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s3=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            ###print(s3)
                            a2=[]
                            for i in s3:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            d=AarDropdown.objects.filter(field='TRAINING AND DEVELOPMENT PROGRAM').exclude(value=None).values('sno','value')
                            a1=[]
                            for j in d:
                                query2=AarDropdown.objects.filter(pid=j['sno']).exclude(value=None).values('sno','value')
                                j['value']=j['value'].replace('-','_')
                                a1.append({j['value'].replace(' ', '_'):list(query2)})
                            status=200
                            reporting_info={'reporting_levels':s1.count(),'reporting_levels1':s2.count(),'data_a':list(s1),'data_b':list(s2)}
                            data_values={'data':list(q),'discipline':list(s),'data1':reporting_info,'data2':a2,'data3':a1}
                            #
                        elif(data['sno']=='6'):
                            q=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('emp_id','status__value','type__value','sector__value','title','descreption','start_date','end_date','principal_investigator','co_principal_investigator','team_size','sponsored','association','approve_status','principal_investigator_id','co_principal_investigator_id')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PROJECT/CONSULTANCY").values('value1__value')
                            s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="PROJECT").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s2=Sponsers.objects.filter(type="PROJECT",emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION').values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s3=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            ###print(s3)
                            a2=[]
                            for i in s3:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            d=AarDropdown.objects.filter(field='PROJECT / CONSULTANCY').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            reporting_info={'reporting_levels':s1.count(),'reporting_levels1':s2.count(),'data_a':list(s1),'data_b':list(s2)}
                            data_values={'data':list(q),'discipline':list(s),'data1':reporting_info,'data2':a2,'data3':a}
                            ###print(data_values)
                        elif(data['sno']=='5'):
                            q=Patent.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('title','descreption','collaboration','company_name','incorporate_status__value','status','number','date','owner__value','approve_status','emp_id')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PATENT").values('value1__value')
                            d=AarDropdown.objects.filter(field='PATENT').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            
                            a2=[]
                            for i in s2:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            data_values={'data':list(q),'discipline':list(s),'data1':a2,'data2':a}
                        elif(data['sno']=='4'):
                            ###print 'tanii'
                            #data_listed={}
                            q=Researchguidence.objects.filter(emp_id=data['emp_id'],project_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','guidence__value','guidence','course__value','degree','degree__value','no_of_students','degree_awarded','status__value','project_title','area_of_spec','approve_status')
                            d=AarDropdown.objects.filter(field='GUIDANCE').exclude(value=None).values('sno','value')
                            ###print q[0]['guidence']
                            if (q[0]['guidence'] == 70):
                                ###print "hiii"
                                sno=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT Guidance',value='COURSES').exclude(value=None).values('sno')
                                s=AarDropdown.objects.filter(pid=sno).exclude(value=None).values('value','sno')
                                data_values={'data2':list(s),'data':list(q),'data1':list(d)}
                                status=200
                                _listed
                            elif(q[0]['guidence'] == 71):
                                sno=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='DEGREE').exclude(value=None).values('sno')
                                sno1=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='UNIVERSITY TYPE').exclude(value=None).values('sno')
                                s=AarDropdown.objects.filter(pid=sno).exclude(value=None).values('value','sno')
                                s1=AarDropdown.objects.filter(pid=sno1).exclude(value=None).values('value','sno')
                                data_values={'data2':list(s),'data3':list(s1),'data':list(q),'data1':list(d)}
                                status=200
                            elif(q[0]['guidence'] == 72):
                                ###print "hiiiii"
                                sno=AarDropdown.objects.filter(field='GUIDANCE',value='RESEARCH (PH. D.)').exclude(value=None).values('sno')
                                sno1=AarDropdown.objects.filter(field='RESEARCH GUIDANCE / PROJECT GUIDANCE',value='UNIVERSITY TYPE').exclude(value=None).values('sno')
                                ###print(sno)
                                s=AarDropdown.objects.filter(pid=sno).exclude(value=None).values('value','sno')
                                s1=AarDropdown.objects.filter(pid=sno1).exclude(value=None).values('value','sno')
                                ###print(s)
                                data_values={'data2':list(s),'data3':list(s1),'data':list(q),'data1':list(d)}
                                status=200


                            # status=200
                            # data_values={'data':list(q),'data1':list(d)}
                        elif(data['sno']=='3'):
                            q=Books.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('emp_id','edition','role__value','role_for__value','publisher_type__value','title','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','approve_status')
                            d=AarDropdown.objects.filter(field='BOOKS').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            ###print("hiii-aks")
                            status=200
                            data_values={'data':list(q),'data1':list(a)}
                            #
                        elif(data['sno']=='2'):
                            q=Researchconference.objects.filter(emp_id=data['emp_id'],paper_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_conference__value','sub_category__value','sponsered','conference_title','paper_title','published_date','organized_by','journal_name','volume_no','issue_no','isbn','page_no','author__value','author','conference_from','conference_to','other_description','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                            ['id']
                            s=Sponsers.objects.filter(spons_id=data['id'],field_type='SPONSOR',type='CONFERENCE').values('sponser_name','type','field_type')
                            #
                            d=AarDropdown.objects.filter(field='RESEARCH PAPER IN CONFERENCE').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            #
                            status=200
                            data_values={'data':list(q),'sponsers':list(s),'data1':list(a)}
                            #
                        elif(data['sno']=='1'):
                            q=Researchjournal.objects.filter(emp_id=data['emp_id'],paper_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_journal__value','sub_category__value','published_date','paper_title','impact_factor','journal_name','volume_no','issue_no','isbn','page_no','author__value','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                            d=AarDropdown.objects.filter(field='RESEARCH PAPER IN JOURNAL').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a.append({i['value'].replace(' ', '_'):list(query1)})
                            #
                            status=200
                            data_values={'data':list(q),'data1':list(a)}
                    elif(data['test']=='5'):
                        if(data['sno']=='1'):
                            
                            category=data["category"]
                            emp_id=request.session["hash1"]
                            type_of_journal=data["typeofjournal"]
                            sub_category=data["subcategory"]
                            paper_title=data["papertitle"]
                            impact_factor=data["impacttext"]
                            date=data["dateofpub"]
                            ###print(published_date)
                            date=date.split('T')
                            ###print(date)
                            Published_date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                            ###print(Published_date)
                            journal_name=data["journalname"]
                            volume_no=data["volumeno"]
                            issue_no=data["issueno"]
                            ###print issue_no
                            isbn=data["isbn"]
                            page_no=data["pageno"]
                            author=data["typeofAuthor"]
                            publisher_name=data["publishername"]
                            publisher_address1=data["publisheraddL1"]
                            publisher_address2=data["publisheraddL2"]
                            if publisher_address2 is None:
                                publisher_address2=""
                            publisher_zip_code=data["zipc"]
                            publisher_contact=data["phone"]
                            publisher_email=data["eml"]
                            publisher_website=data["website"]
                            if 'subcatText' in data:
                                others=data["subcatText"]
                            else:
                                others=None
                            doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                            d=str(doj[0]['doj'])
                            Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                            q=Researchjournal.objects.filter(emp_id=emp_id,paper_title=paper_title).exclude(approve_status="REJECTED").update(category=AarDropdown.objects.get(sno=category),author=author,type_of_journal=AarDropdown.objects.get(sno=type_of_journal),sub_category=AarDropdown.objects.get(sno=sub_category),others=others,paper_title=paper_title,published_date=Published_date,impact_factor=impact_factor,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,publisher_name=publisher_name,publisher_address1=publisher_address1,publisher_address2=publisher_address2,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,emp_id=emp_id,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                            data_values={"OK":"DATA Updated Successfully"}
                            status=200
                        elif(data['sno']=='2'):
                            
                            category=data["category"]
                            emp_id=request.session["hash1"]
                            type_of_conference=data["type"]
                            #sub_category=data["subCategory"]
                            if 'sponsered' in data:
                                sponsered=data["sponsered"]
                            else:
                                sponsered=None
                            if  'sponsers' in data:
                                sponsers=data['sponsers']
                            else:
                                sponsers=None
                            conference_title=data["titleConference"]
                            paper_title=data["titlePaper"]
                            published_date=data["dateOfPublish"]
                            organized_by=data["organised"]
                            if 'journalName' in data:
                                ###print("hii")
                                journal_name=data["journalName"]
                            else:
                                journal_name=None
                            if 'volume' in data:
                                volume_no=data["volume"]
                            else:
                                volume_no=None
                            if 'issue' in data:
                                issue_no=data["issue"]
                            else:
                                issue_no=None
                            if 'issn' in data:
                                isbn=data["issn"]
                            else:
                                isbn=None
                            if 'page' in data:
                                page_no=data["page"]
                            else:
                                page_no=None
                            author=data["author"]
                            conference_from=data["fromDate"].split('T')[0]
                            conference_to=data["toDate"].split('T')[0]
                            other_description=data["description"]
                            publisher_name=data["publisherName"]
                            publisher_address=data["publisherAddress"]
                            publisher_zip_code=data["publisherPincode"]
                            publisher_contact=data["publisherContact"]
                            publisher_email=data["publisherEmail"]
                            publisher_website=data["publisherWebsite"]
                            published_date=data["dateOfPublish"]
                            ###print(conference_from)
                            ###print(conference_to)
                            if 'others' in data:
                                others=data["others"]
                            else:
                                others=None
                                ###print "hii"
                            doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                            d=str(doj[0]['doj'])
                            Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                            published_date=datetime.datetime.strptime(published_date,'%Y-%m-%d').date()
                            q=Researchconference.objects.filter(emp_id=emp_id,paper_title=paper_title).exclude(approve_status="REJECTED").update(category=AarDropdown.objects.get(sno=category),type_of_conference=AarDropdown.objects.get(sno=type_of_conference),emp_id=emp_id,sponsered=sponsered,conference_title=conference_title,paper_title=paper_title,published_date=published_date,organized_by=organized_by,journal_name=journal_name,volume_no=volume_no,issue_no=issue_no,isbn=isbn,page_no=page_no,author=AarDropdown.objects.get(sno=author),conference_from=conference_from,conference_to=conference_to,other_description=other_description,publisher_name=publisher_name,publisher_address=publisher_address,publisher_zip_code=publisher_zip_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website,others=others,approve_status='PENDING',t_date=str(datetime.datetime.now()))
                            data_values={"OK":"DATA Updated Successfully"}
                            status=200
                        elif(data['sno']=='3'):
                            
                            role=data['role']
                            for_type=data['for_type']
                            publisher=data['publisher']
                            copyright_no=data['copyright_no']
                            copyright_status=data['copyright_status']
                            if 'title' in data:
                                title=data['title']
                            else:
                                title=None
                            if 'chapter' in data:
                                chapter=data['chapter']
                            else:
                                chapter=None
                            publisher_name=data['publisher_name']
                            publisher_add=data['publisher_add']
                            edition=data['edition']
                            date=data['date']
                            publisher_email=data['publisher_email']
                            ['author']
                            author=data['author']
                            ###print(author)
                            publisher_website=data['publisher_website']
                            isbn=data['isbn']
                            publisher_code=data['publisher_code']
                            publisher_contact=data['publisher_contact']
                            emp_id=request.session['hash1']
                            role_type_new=AarDropdown.objects.get(sno=role)
                            for_type_new=AarDropdown.objects.get(sno=for_type)
                            publisher_new=AarDropdown.objects.get(sno=publisher)
                            ###print publisher_new
                            #author_new=AarDropdown.objects.get(sno=author)
                            ###print author_new
                            date=date.split('T')
                            date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                            Books.objects.filter(emp_id=emp_id,isbn=isbn).update(role=role_type_new,role_for=for_type_new,publisher_type=publisher_new,title=title,edition=edition,published_date=date,chapter=chapter,isbn=isbn,copyright_status=copyright_status,copyright_no=copyright_no,author=AarDropdown.objects.get(sno=author),publisher_name=publisher_name,publisher_address=publisher_add,publisher_zip_code=publisher_code,publisher_contact=publisher_contact,publisher_email=publisher_email,publisher_website=publisher_website)
                            data_values={"OK":"DATA Updated Successfully"}
                            status=200
                        elif(data['sno']=='4'):
                            ##print data
                            course=data['Course']
                            degree=data['Degree']
                            degree_awarded=data['Degree_awarded']
                            guid=data['Guidance']
                            ##print (AarDropdown.objects.get(sno=guid))
                            no_stud=data['No_of_Students']
                            a_o_s=data['area_of_specialization']
                            title=data['project_title']
                            status=data['status']
                            emp_id=request.session["hash1"]
                            if guid:
                                if(course!=None):
                                    Researchguidence.objects.filter(guidence=AarDropdown.objects.get(sno=guid),emp_id=emp_id).update(guidence=AarDropdown.objects.get(sno=guid),course=AarDropdown.objects.get(sno=course),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,emp_id=emp_id)
                                    data_values={"OK":"COURSE Inserted Successfully"}

                                elif(degree!=None):
                                    ##print guid
                                    Researchguidence.objects.filter(guidence=AarDropdown.objects.get(sno=guid),emp_id=emp_id).update(guidence=AarDropdown.objects.get(sno=guid),degree=AarDropdown.objects.get(sno=degree),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,emp_id=emp_id)
                                    data_values={"OK":"DEGREE Inserted Successfully"}

                                elif(status!=None):
                                    Researchguidence.objects.filter(guidence=AarDropdown.objects.get(sno=guid),emp_id=emp_id).update(guidence=AarDropdown.objects.get(sno=guid),status=AarDropdown.objects.get(sno=status),degree_awarded=degree_awarded,no_of_students=no_stud,area_of_spec=a_o_s,project_title=title,emp_id=emp_id)
                            data_values={"OK":"DATA Updated Successfully"}
                            status=200
                        elif(data['sno']=='5'):
                            
                            if 'discipline' in data:
                                discipline=data["discipline"]
                            else:
                                discipline=None
                            collaboration=data["collaboration"]
                            if 'company' in data:
                                company_name=data["company"]
                            else:
                                company_name=None
                            if 'incorporate' in data:
                                if data['incorporate']!=None:
                                    incorporate_status=AarDropdown.objects.get(sno=data['incorporate'])
                                else:
                                    incorporate_status=None
                            else:
                                incorporate_status=None
                            if 'status' in data:
                                status=data["status"]
                            else:
                                status=None
                            if 'number' in data:
                                number=data["number"]
                            else:
                                number=None
                                date=data["date"]
                                date=date.split('T')
                                date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                                owner=AarDropdown.objects.get(sno=data['owner'])
                                title=data["title"]
                                descreption=data["desc"]
                                approve_status='PENDING'
                                doj=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                                d=str(doj[0]['doj'])
                                Doj=datetime.datetime.strptime(d,'%Y-%m-%d').date()
                                if Doj!=None:
                                    if date>Doj:
                                        Patent.objects.filter(emp_id=emp_id,title=title).update(title=title,incorporate_status=incorporate_status,owner=owner,collaboration=collaboration,company_name=company_name,status=status,number=number,date=date)
                                        sno=Patent.objects.filter(emp_id=emp_id,title=title).values('id')
                                        if sno.count()>0:
                                            Discipline.objects.filter(emp_id=emp_id,type="PATENT").delete()
                                        if  discipline!=None:
                                            ###print discipline
                                            for i in discipline:
                                                Discipline.objects.create(id=sno[0]['id'],emp_id=emp_id,value1=None,value2=AarDropdown.objects.get(sno=i),type="PATENT")
                            data_values={"OK":"DATA Updated Successfully"}
                            status=200
                        if(data['sno']=='6'):
                            #emp_id=request.session['hash1']
                            # ##print emp_id
                            if 'p_status' in data:
                                status=data["p_status"]
                            else:
                                status=None
                            sector=data["sector"]
                            start_date=data["start_date"]
                            type=data["type"]
                            end_date=data["end_date"]
                            if 'principal' in data:
                                principal=data["principal"]
                                if principal=='self':
                                    principal_id=data['emp_id']
                                elif principal=='other':
                                    principal_id=data['principal_id']
                            else:
                                principal=None
                            if 'co_principal' in data:
                                co_principal=data["co_principal"]
                                if co_principal=='self':
                                    co_principal_id=data['emp_id']
                                elif co_principal=='other':
                                    co_principal_id=data['co_principal_id']
                            else:
                                co_principal=None
                            team_size=data["team_size"]
                            sponsored=data["sponsored"]
                            association=data["association"]
                            if 'organisation' in data:
                                organisation=data["organisation"]
                            else:
                                organisation=None
                            if 'contact_person' in data:
                                contact_person=data["contact_person"]
                            else:
                                contact_person=None
                            if 'address' in data:
                                address=data['address']
                            else:
                                address=None
                            if 'e_mail' in data:
                                e_mail=data["e_mail"]
                            else:
                                e_mail=None
                            if 'pin_code' in data:
                                pin_code=data["pin_code"]
                            else:
                                pin_code=None
                            if 'contact_number' in data:
                                contact_number=data["contact_number"]
                            else:
                                contact_number=None
                            if 'website' in data:
                                website=data["website"]
                            else:
                                website=None
                            if 'amount' in data:
                                amount=data['amount']
                            else:
                                amount=None
                            if 'organisation1' in data:
                                organisation1=data["organisation1"]
                            else:
                                organisation1=None
                            if 'contact_person1' in data:
                                contact_person1=data["contact_person1"]
                            else:
                                contact_person1=None
                            if 'address1' in data:
                                address1=data['address1']
                            else:
                                address1=None
                            if 'e_mail1' in data:
                                e_mail1=data["e_mail1"]
                            else:
                                e_mail1=None
                            if 'pin_code1' in data:
                                pin_code1=data["pin_code1"]
                            else:
                                pin_code1=None
                            if 'contact_number1' in data:
                                contact_number1=data["contact_number1"]
                            else:
                                contact_number1=None
                            if 'website1' in data:
                                website1=data["website1"]
                            else:
                                website1=None
                            if 'amount1' in data:
                                amount1=data['amount1']
                            else:
                                amount1=None
                            if 'sponsers' in data:
                                sponsers=data['sponsers']
                            else:
                                sponsers=None
                            if 'sponsers2' in data:
                                sponsers2=data['sponsers2']
                            else:
                                sponsers2=None
                            title=data["title"]
                            # prev_title=data["prev_title"]
                            descreption=data["descreption"]
                            approve_status='PENDING'
                            discipline=data["discipline"]

                            from_d= start_date.split('T')
                            to_d= end_date.split('T')
                            start_date =datetime.datetime.strptime(from_d[0],'%Y-%m-%d').date()
                            end_date=datetime.datetime.strptime(to_d[0],'%Y-%m-%d').date()
                            ProjectConsultancy.objects.filter(emp_id=data['emp_id'],title=title).update(type=AarDropdown.objects.get(sno=type),sector=AarDropdown.objects.get(sno=sector),status=AarDropdown.objects.get(sno=status),emp_id=data['emp_id'],title=title,descreption=descreption,start_date=start_date,end_date=end_date,principal_investigator=principal,co_principal_investigator=co_principal,principal_investigator_id=principal_id,co_principal_investigator_id=co_principal_id,team_size=team_size,sponsored=sponsored,association=association,approve_status=approve_status)
                            sno=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],title=title).values('id')
                            ##print(sno)
                            if sno.count()>0:
                                Discipline.objects.filter(emp_id=data['emp_id'],type='PROJECT/CONSULTANCY').delete()
                                Sponsers.objects.filter(spons_id=sno[0]['id']).delete()
                            if(sponsored=="yes"):
                                for i in sponsers:
                                    Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=data['emp_id'],sponser_name=i["organisation"],type="PROJECT",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='SPONSORED')
                            if(association=="yes"):
                                for i in sponsers2:
                                    Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=data['emp_id'],sponser_name=i["organisation1"],type="PROJECT",contact_person=i['contact_person1'],contact_number=i['contact_number1'],e_mail=i['e_mail1'],website=i['website1'],amount=i['amount1'],address=i['address1'],pin_code=i['pin_code1'],field_type='ASSOCIATION')
                            if  discipline!=None:
                                ##print discipline
                                for i in discipline:
                                    Discipline.objects.create(id=sno[0]['id'],emp_id=data['emp_id'],value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="PROJECT/CONSULTANCY")
                            data_values={"OK":"DATA Updated Successfully"}
                            status=200
                        elif(data['sno']=='7'):
                            ##print data
                            category=data["category"]
                            type=data["type"]
                            organization=data["organization"]
                            incorporation=data["status"]
                            role=data["role"]
                            attended=data["attend"]
                            organizers=data["organizer"]
                            participants=data["participants"]
                            venue=data["venue"]

                            if 'sponsers' in data:
                                sponsers=data['sponsers']
                            else:
                                sponsers= None
                            if 'collaboration' in data:
                                collaborations=data["collaboration"]
                            else:
                                collaboration= None
                            if 'organisation' in data:
                                organisation=data["organisation"]
                            else:
                                organisation=None
                            if 'contact_person' in data:
                                contact_person=data["contact_person"]
                            else:
                                contact_person=None
                            if 'address' in data:
                                address=data['address']
                            else:
                                address=None
                            if 'e_mail' in data:
                                e_mail=data["e_mail"]
                            else:
                                e_mail=None
                            if 'pin_code' in data:
                                pin_code=data["pin_code"]
                            else:
                                pin_code=None
                            if 'contact_number' in data:
                                contact_number=data["contact_number"]
                            else:
                                contact_number=None
                            if 'website' in data:
                                website=data["website"]
                            else:
                                website=None
                            if 'amount' in data:
                                amount=data['amount']
                            else:
                                amount=None
                            if 'organisation1' in data:
                                organisation1=data["organisation1"]
                            else:
                                organisation1=None
                            if 'contact_person1' in data:
                                contact_person1=data["contact_person1"]
                            else:
                                contact_person1=None
                            if 'address1' in data:
                                address1=data['address1']
                            else:
                                address1=None
                            if 'e_mail1' in data:
                                e_mail1=data["e_mail1"]
                            else:
                                e_mail1=None
                            if 'pin_code1' in data:
                                pin_code1=data["pin_code1"]
                            else:
                                pin_code1=None
                            if 'contact_number1' in data:
                                contact_number1=data["contact_number1"]
                            else:
                                contact_number1=None
                            if 'website1' in data:
                                website1=data["website1"]
                            else:
                                website1=None
                            if 'amount1' in data:
                                amount1=data['amount1']
                            else:
                                amount1=None
                            if 'sponsers' in data:
                                sponsers=data['sponsers']
                            else:
                                sponsers=None
                            if 'sponsers2' in data:
                                sponsers2=data['sponsers2']
                            else:
                                sponsers2=None
                            if 'sponsership' in data:
                                sponsership=data['sponsership']
                            else:
                                sponsership=None
                            if 'discipline' in data:
                                discipline=data["discipline"]
                            else:
                                discipline=None
                            from_date=data["from_date"]
                            to_date=data["to_date"]
                            title=data["title"]
                            prev_title=data['prev_title']
                            #sponsership="No"
                            from_d= from_date.split('T')
                            to_d= to_date.split('T')
                            from_date=datetime.datetime.strptime(from_d[0],'%Y-%m-%d').date()
                            to_date=datetime.datetime.strptime(to_d[0],'%Y-%m-%d').date()
                            approve_status='PENDING'
                            q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],title=prev_title).update(category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type),role=AarDropdown.objects.get(sno=role),incorporation_status=AarDropdown.objects.get(sno=incorporation),organization_sector=AarDropdown.objects.get(sno=organization),from_date=from_date,to_date=to_date,participants=participants,venue=venue,title=title,organizers=organizers,attended=attended,collaborations=collaborations,emp_id=data['emp_id'],approve_status=approve_status,sponsership=sponsership)
                            sno=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],title=title).values('id')
                            if sno.count()>0:
                                Sponsers.objects.filter(spons_id=sno[0]['id'],emp_id=data['emp_id'],type="TRAINING").delete()
                                Discipline.objects.filter(emp_id=data['emp_id'],type="TRAINING",id=sno[0]['id']).delete()

                            if(collaborations=="yes"):
                                for i in sponsers:
                                    Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=data['emp_id'],sponser_name=i["organisation"],type="TRAINING",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='COLLABORATION')
                            if(sponsership=="yes"):
                                for i in sponsers2:
                                    Sponsers.objects.create(spons_id=sno[0]['id'],emp_id=data['emp_id'],sponser_name=i["organisation1"],type="TRAINING",contact_person=i['contact_person1'],contact_number=i['contact_number1'],e_mail=i['e_mail1'],website=i['website1'],amount=i['amount1'],address=i['address1'],pin_code=i['pin_code1'],field_type='SPONSOR')
                            if  discipline!=None:
                                for i in discipline:
                                    Discipline.objects.create(id=sno[0]['id'],emp_id=data['emp_id'],value2=None,value1=EmployeeDropdown.objects.get(sno=i),type="TRAINING")
                            data_values={"OK":"DATA Updated Successfully"}
                            status=200
                        elif(data['sno']=='8'):
                            ##print data
                            category=data["category"]
                            type=data["type"]
                            organization=data["organization"]
                            incorporation=data["incorporation"]
                            role=data["role"]
                            date=data["date"]
                            date=date.split('T')
                            date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                            topic=data["title"]
                            prev_topic=data["prev_topic"]
                            participants=data["participants"]
                            venue=data["venue"]
                            address=data['address']
                            e_mail=data["e_mail"]
                            pin_code=data["pin_code"]
                            contact_number=data["contact_number"]
                            website=data["website"]

                            LecturesTalks.objects.filter(emp_id=data['emp_id'],topic=prev_topic).update(category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type),role=AarDropdown.objects.get(sno=role),incorporation_status=AarDropdown.objects.get(sno=incorporation),organization_sector=AarDropdown.objects.get(sno=organization),date=date,topic=topic,participants=participants,venue=venue,address=address,pin_code=pin_code,contact_number=contact_number,e_mail=e_mail,website=website,emp_id=data['emp_id'])
                            data_values={"OK":"DATA Updated Successfully"}
                            status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def aar_approved_report(request):
    msg={}
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337,319])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    ##print data
                    fromyear=int(data['fromyear'])
                    frommonth=int(data['frommonth'])
                    fromdate=datetime.date(fromyear,frommonth,1)
                    fdate=datetime.date(fromyear, frommonth ,1).strftime('%Y-%m-%d')
                    toyear=int(data['toyear'])
                    tomonth=int(data['tomonth'])
                    todate=datetime.date(toyear,tomonth,30)
                    tdate=datetime.date(toyear, tomonth ,30).strftime('%Y-%m-%d')
                    ##print tdate
                    ##print fdate
                    if(data['test']=='1'):
                        if 'data' in data:
                            sno=data['data']
                        else:
                            sno=None
                        if(sno=='1'):
                            q=Researchjournal.objects.filter(approve_status='APPROVED',emp_id=emp_id,published_date__lte=tdate,published_date__gte=fdate).values('paper_title','id','emp_id','approve_status','category__value','type_of_journal__value','published_date','journal_name','volume_no','issue_no','isbn','author__value')
                            b=list(q)
                        elif(sno=='2'):
                            q=Researchconference.objects.filter(approve_status='APPROVED',emp_id=emp_id,published_date__lte=tdate,published_date__gte=fdate).values('paper_title','id','emp_id','approve_status','category__value','type_of_conference__value','conference_title','published_date','organized_by','author__value','conference_from','conference_to','publisher_name')
                            b=list(q)
                        elif(sno=='3'):
                            q=Books.objects.filter(approve_status='APPROVED',emp_id=emp_id,published_date__lte=tdate,published_date__gte=fdate).values('title','id','emp_id','approve_status','role__value','role_for__value','publisher_type','edition','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name')
                            b=list(q)
                        elif(sno=='4'):
                            q=Researchguidence.objects.filter(approve_status='APPROVED',emp_id=emp_id,date__lte=tdate,date__gte=fdate).values('project_title','id','emp_id','approve_status','guidence__value','course__value','degree__value','no_of_students','degree_awarded','uni_type__value','uni_name','status__value','area_of_spec')
                            b=list(q)
                        elif(sno=='5'):
                            q=Patent.objects.filter(approve_status='APPROVED',emp_id=emp_id,date__lte=tdate,date__gte=fdate).values('title','id','emp_id','approve_status','descreption','collaboration','company_name','incorporate_status__value','status','date','owner__value')
                            b=list(q)
                        elif(sno=='6'):
                            q=ProjectConsultancy.objects.filter(approve_status='APPROVED',emp_id=emp_id,end_date__lte=tdate,start_date__gte=fdate).values('title','id','emp_id','approve_status','type__value','status__value','sector__value','start_date','end_date','principal_investigator','co_principal_investigator','sponsored','team_size','association')
                            b=list(q)
                        elif(sno=='7'):
                            q=TrainingDevelopment.objects.filter(approve_status='APPROVED',emp_id=emp_id,to_date__lte=tdate,from_date__gte=fdate).values('title','id','emp_id','approve_status','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','venue','participants','organizers','attended','collaborations','sponsership')
                            b=list(q)
                        elif(sno=='8'):
                            q=LecturesTalks.objects.filter(approve_status='APPROVED',emp_id=emp_id,date__lte=tdate,date__gte=fdate).values('topic','id','emp_id','approve_status','category__value','type__value','role__value','organization_sector__value','incorporation_status__value','venue','participants')
                            b=list(q)
                        data_values={'data':b}
                        status=200

            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=200)

def aar_report(request):
    msg={}
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337,319])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    print(data)
                    fromyear=int(data['fromyear'])
                    frommonth=int(data['frommonth'])
                    fromdate=datetime.date(fromyear,frommonth,1)
                    fdate=datetime.date(fromyear, frommonth ,1).strftime('%Y-%m-%d')
                    toyear=int(data['toyear'])
                    tomonth=int(data['tomonth'])
                    todate=datetime.date(toyear,tomonth,30)
                    tdate=datetime.date(toyear, tomonth ,30).strftime('%Y-%m-%d')
                    ##print tdate
                    ##print fdate
                    # range1=calendar.monthrange(year,month)
                    # tdate=datetime.date(year,month ,range1[1]).strftime('%Y-%m-%d')
                    if(data['test']=='1'):
                        if 'data' in data:
                            sno=data['data']
                        else:
                            sno=None
                        dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        if(sno=='1'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                # query=AarSession.objects.filter(Fdate__gte=fdate,Tdate__lte=tdate).values('session','Fdate','Tdate')

                                q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,published_date__lte=tdate,published_date__gte=fdate).values('paper_title','id','emp_id','approve_status','category__value','type_of_journal__value','published_date','journal_name','volume_no','issue_no','isbn','author__value','sub_category__value','impact_factor','page_no','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','emp_id__dept__value')
                                ###print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'journal_type':i['type_of_journal__value'],'publish_date':i['published_date'],'journal_name':i['journal_name'],'volume_no':i['volume_no'],'issue_no':i['issue_no'],'isbn':i['isbn'],'author':i['author__value'],'sub_category__value':i['sub_category__value'],'impact_factor':i['impact_factor'],'page_no':i['page_no'],'publisher_name':i['publisher_name'],'publisher_address1':i['publisher_address1'],'publisher_address2':i['publisher_address2'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website'],'others':i['others'],'dept':i['emp_id__dept__value']}
                                        b.append(d)

                        elif(sno=='2'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']

                                q=Researchconference.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,published_date__lte=tdate,published_date__gte=fdate).values('paper_title','id','emp_id','approve_status','category__value','type_of_conference__value','conference_title','published_date','organized_by','author__value','conference_from','conference_to','publisher_name','journal_name','volume_no','issue_no','isbn','page_no','other_description','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','sub_category__value','sponsered','emp_id__dept__value')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'conference_type':i['type_of_conference__value'],'conference_title':i['conference_title'],'publish_date':i['published_date'],'organized_by':i['organized_by'],'author':i['author__value'],'conference_from':i['conference_from'],'conference_to':i['conference_to'],'publisher_name':i['publisher_name'],'journal_name':i['journal_name'],'volume_no':i['volume_no'],'issue_no':i['issue_no'],'isbn':i['isbn'],'page_no':i['page_no'],'other_description':i['other_description'],'publisher_address':i['publisher_address'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website'],'others':i['others'],'sub_category__value':i['sub_category__value'],'sponsored':i['sponsered'],'dept':i['emp_id__dept__value']}
                                # q=Researchconference.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,published_date__lte=tdate,published_date__gte=fdate).values('paper_title','id','emp_id','approve_status')

                                # if(q.count()>0):
                                #   for i in q:
                                #       d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                        b.append(d)


                                

                        elif(sno=='3'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']


                                q=Books.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,published_date__lte=tdate,published_date__gte=fdate).values('title','id','emp_id','approve_status','role__value','role_for__value','publisher_type','edition','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','emp_id__dept__value')


                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'role':i['role__value'],'role_for':i['role_for__value'],'publisher_type':i['publisher_type'],'edition':i['edition'],'publish_date':i['published_date'],'chapter':i['chapter'],'isbn':i['isbn'],'copyright_status':i['copyright_status'],'copyright_no':i['copyright_no'],'author':i['author__value'],'publisher_name':i['publisher_name'],'publisher_address':i['publisher_address'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website '],'dept':i['emp_id__dept__value']}
                                        b.append(d)

                        elif(sno=='4'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchguidence.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,date__lte=tdate,date__gte=fdate).values('id','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','guidence','guidence__value','course','course__value','degree','degree__value','no_of_students','degree_awarded','uni_type','uni_type__value','uni_name','status__value','project_title','area_of_spec','date','approve_status')
                                for i in q:
                                    b.append(i)

                        elif(sno=='5'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']


                                q=Patent.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,date__lte=tdate,date__gte=fdate).values('title','id','emp_id','approve_status','descreption','collaboration','company_name','incorporate_status__value','status','date','owner__value','level','number','emp_id__dept__value')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'descreption':i['descreption'],'collaboration':i['collaboration'],'company_name':i['company_name'],'incorporate_status':i['incorporate_status__value'],'status':i['status'],'date':i['date'],'owner':i['owner__value'],'level':i['level'],'number':i['number'],'dept':i['emp_id__dept__value']}
                                        b.append(d)


                        elif(sno=='6'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                c=0


                                q=ProjectConsultancy.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,end_date__lte=tdate,start_date__gte=fdate).values('title','id','emp_id','approve_status','type__value','status__value','sector__value','start_date','end_date','principal_investigator','co_principal_investigator','sponsored','team_size','association','descreption','principal_investigator_id','co_principal_investigator_id','emp_id__dept__value')

                                c=q.count()
                                if(c>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'type__value':i['type__value'],'status__value':i['status__value'],'sector__value':i['sector__value'],'start_date':i['start_date'],'end_date':i['end_date'],'principal_investigator':i['principal_investigator'],'co_principal_investigator':i['co_principal_investigator'],'sponsored':i['sponsored'],'team_size':i['team_size'],'association':i['association'],'patent_descreption':i['descreption'],'principal_investigator_id':i['principal_investigator_id'],'co_principal_investigator_id':i['co_principal_investigator_id'],'dept':i['emp_id__dept__value']}
                                        b.append(d)

                        elif(sno=='7'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=TrainingDevelopment.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,to_date__lte=tdate,from_date__gte=fdate).values('id','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','category__value','type__value','from_date','to_date','role','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaborations','sponsership','approve_status'
                                    )
                                for i in q:
                                    b.append(i)


                        elif(sno=='8'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']


                                q=LecturesTalks.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,date__lte=tdate,date__gte=fdate).values('topic','id','emp_id','approve_status','category__value','type__value','role__value','organization_sector__value','incorporation_status__value','venue','participants','address','pin_code','contact_number','e_mail','website','approve_status','date','emp_id__dept__value')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['topic'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'role':i['role__value'],'address':i['address'],'pin_code':i['pin_code'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'website':i['website'],'approve_status':i['approve_status'],'date':i['date'],'dept':i['emp_id__dept__value']}
                                        b.append(d)

                        data_values={'data':b}
                        status=200
                    elif(data['test']=='2'):
                        if(data['sno']=='8'):
                            q=LecturesTalks.objects.filter(emp_id=data['emp_id'],topic=data['title']).values('emp_id','category__value','type__value','organization_sector__value','incorporation_status__value','role__value','date','topic','participants','venue','address','pin_code','contact_number','e_mail','website','approve_status')
                            status=200
                            data_values={'data':list(q)}
                        elif(data['sno']=='7'):
                            q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaborations','sponsership','approve_status')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="TRAINING").values('value1__value')
                            s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s2=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s3=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            ##print(s3)
                            a2=[]
                            for i in s3:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                ##print(query1)
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200

                            reporting_info={'reporting_levels':s1.count(),'reporting_levels1':s2.count(),'data_a':list(s1),'data_b':list(s2)}
                            data_values={'data':list(q),'discipline':list(s),'data1':reporting_info,'data2':a2}
                        elif(data['sno']=='6'):
                            q=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],title=data['title']).values('emp_id','status__value','type__value','sector__value','title','descreption','start_date','end_date','principal_investigator','co_principal_investigator','team_size','sponsored','association','approve_status')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PROJECT/CONSULTANCY").values('value1__value')
                            s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="PROJECT").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s2=Sponsers.objects.filter(type="PROJECT",emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION').values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s3=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            a2=[]
                            for i in s3:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            reporting_info={'reporting_levels':s1.count(),'reporting_levels1':s2.count(),'data_a':list(s1),'data_b':list(s2)}
                            data_values={'data':list(q),'discipline':list(s),'data1':reporting_info,'data2':a2}
                        elif(data['sno']=='5'):
                            q=Patent.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('title','descreption','collaboration','company_name','incorporate_status__value','status','number','date','owner__value','approve_status','emp_id')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PATENT").values('value1__value')
                            s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            ##print(s2)
                            a2=[]
                            for i in s2:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                ##print(query1)
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            data_values={'data':list(q),'discipline':list(s),'data1':a2}
                        elif(data['sno']=='4'):
                            q=Researchguidence.objects.filter(emp_id=data['emp_id'],project_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','guidence__value','course__value','degree','degree__value','no_of_students','degree_awarded','status__value','project_title','area_of_spec','approve_status')
                            ##print("hiii-aks"),q,data['emp_id'],data['title']
                            status=200
                            data_values={'data':list(q)}
                        elif(data['sno']=='3'):
                            q=Books.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('emp_id','edition','role__value','role_for__value','publisher_type__value','title','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','approve_status')
                            ##print("hiii-aks")
                            status=200
                            data_values={'data':list(q)}
                            
                        elif(data['sno']=='2'):
                            q=Researchconference.objects.filter(emp_id=data['emp_id'],paper_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_conference__value','sub_category__value','sponsered','conference_title','paper_title','published_date','organized_by','journal_name','volume_no','issue_no','isbn','page_no','author__value','author__value','conference_from','conference_to','other_description','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                            s=Sponsers.objects.filter(spons_id=data['id'],field_type='SPONSOR',type='CONFERENCE').values('sponser_name','type','field_type')
                            
                            status=200
                            data_values={'data':list(q),'sponsers':list(s)}
                        elif(data['sno']=='1'):
                            q=Researchjournal.objects.filter(emp_id=data['emp_id'],paper_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_journal__value','sub_category__value','published_date','paper_title','impact_factor','journal_name','volume_no','issue_no','isbn','page_no','author__value','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                            
                            status=200
                            data_values={'data':list(q)}
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=200)

def aar_report_test(request):
    msg={}
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    ##print data
                    if(data['test']=='1'):
                        ##print("hii")
                        if (data['data'] == '1'):
                            ##print "tanya"
                            q=Researchjournal.objects.filter(Q(approve_status='APPROVED'),emp_id=emp_id).values('paper_title','id','emp_id','approve_status')
                            data_values=list(q)
                            status=200
                        if (data['data'] == '2'):
                            ##print "tanya"
                            q=Researchconference.objects.filter(Q(approve_status='APPROVED'),emp_id=emp_id).values('paper_title','id','emp_id','approve_status')
                            data_values=list(q)
                            status=200
                        if (data['data'] == '3'):
                            ##print "tanya"
                            q=Books.objects.filter(Q(approve_status='APPROVED'),emp_id=emp_id).values('title','id','emp_id','approve_status')
                            data_values=list(q)
                            status=200
                    else:
                        status=403
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=200)

def report(request):
    msg={}
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337,219])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    ##print data
                    if(data['test']=='1'):
                        if 'data' in data:
                            sno=data['data']
                        else:
                            sno=None
                        dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('name','dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        if(sno=='1'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchjournal.objects.filter(Q(approve_status='APPROVED'),emp_id=emp_id).values('paper_title','id','emp_id','approve_status')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'name':name,'id':i['id'],'emp_id':i['emp_id'],'approve_status':i['approve_status']}  
                                        b.append(d)


                        elif(sno=='2'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchconference.objects.filter(Q(approve_status='APPROVED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                        b.append(d)


                        elif(sno=='3'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Books.objects.filter(Q(approve_status='APPROVED'),emp_id=Eid).values('title','id','emp_id','approve_status')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                        b.append(d)


                        elif(sno=='4'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchguidence.objects.filter(Q(approve_status='APPROVED'),emp_id=Eid).values('project_title','id','emp_id','approve_status')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['project_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                        b.append(d)


                        elif(sno=='5'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Patent.objects.filter(Q(approve_status='APPROVED'),emp_id=Eid).values('title','id','emp_id','approve_status')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                        b.append(d)



                        elif(sno=='6'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                c=0
                                q=ProjectConsultancy.objects.filter(Q(approve_status='APPROVED'),emp_id=Eid).values('title','id','emp_id','approve_status')
                                c=q.count()
                                if(c>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                        b.append(d)


                        elif(sno=='7'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=TrainingDevelopment.objects.filter(Q(approve_status='APPROVED'),emp_id=Eid).values('title','id','emp_id','approve_status')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                        b.append(d)


                        elif(sno=='8'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=LecturesTalks.objects.filter(Q(approve_status='APPROVED'),emp_id=Eid).values('topic','id','emp_id','approve_status')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['topic'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                        b.append(d)

                        data_values={'data':b}
                        status=200
                    elif(data['test']=='2'):
                        if(data['sno']=='8'):
                            q=LecturesTalks.objects.filter(emp_id=data['emp_id'],topic=data['title']).values('emp_id','category__value','type__value','organization_sector__value','incorporation_status__value','role__value','date','topic','participants','venue','address','pin_code','contact_number','e_mail','website','approve_status')
                            status=200
                            data_values={'data':list(q)}
                        elif(data['sno']=='7'):
                            q=TrainingDevelopment.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaborations','sponsership','approve_status')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="TRAINING").values('value1__value')
                            s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s2=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION',type="TRAINING").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s3=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            ##print(s3)
                            a2=[]
                            for i in s3:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                ##print(query1)
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200

                            reporting_info={'reporting_levels':s1.count(),'reporting_levels1':s2.count(),'data_a':list(s1),'data_b':list(s2)}
                            data_values={'data':list(q),'discipline':list(s),'data1':reporting_info,'data2':a2}
                        elif(data['sno']=='6'):
                            q=ProjectConsultancy.objects.filter(emp_id=data['emp_id'],title=data['title']).values('emp_id','status__value','type__value','sector__value','title','descreption','start_date','end_date','principal_investigator','co_principal_investigator','team_size','sponsored','association','approve_status')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PROJECT/CONSULTANCY").values('value1__value')
                            s1=Sponsers.objects.filter(emp_id=data['emp_id'],spons_id=data['id'],field_type='SPONSOR',type="PROJECT").values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s2=Sponsers.objects.filter(type="PROJECT",emp_id=data['emp_id'],spons_id=data['id'],field_type='ASSOCIATION').values('sponser_name','type','pin_code','address','contact_person','contact_number','e_mail','website','amount','field_type')
                            s3=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            a2=[]
                            for i in s3:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            reporting_info={'reporting_levels':s1.count(),'reporting_levels1':s2.count(),'data_a':list(s1),'data_b':list(s2)}
                            data_values={'data':list(q),'discipline':list(s),'data1':reporting_info,'data2':a2}
                        elif(data['sno']=='5'):
                            q=Patent.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('title','descreption','collaboration','company_name','incorporate_status__value','status','number','date','owner__value','approve_status','emp_id')
                            s=Discipline.objects.filter(id=data['id'],emp_id=data['emp_id'],type="PATENT").values('value1__value')
                            s2=EmployeeDropdown.objects.filter(field='KIET GROUP OF INSTITUTIONS').exclude(value=None).values('sno','value')
                            ##print(s2)
                            a2=[]
                            for i in s2:
                                query1=EmployeeDropdown.objects.filter(pid=i['sno'],field="DEPARTMENT").exclude(value=None).values('sno','value')
                                ##print(query1)
                                i['value']=i['value'].replace('-','_')
                                a2.append({i['value'].replace(' ', '_'):list(query1)})
                            status=200
                            data_values={'data':list(q),'discipline':list(s),'data1':a2}
                        elif(data['sno']=='4'):
                            q=Researchguidence.objects.filter(emp_id=data['emp_id'],project_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','guidence__value','course__value','degree','degree__value','no_of_students','degree_awarded','status__value','project_title','area_of_spec','approve_status')
                            ##print("hiii-aks"),q,data['emp_id'],data['title']
                            status=200
                            data_values={'data':list(q)}
                        elif(data['sno']=='3'):
                            q=Books.objects.filter(emp_id=data['emp_id'],title=data['title']).exclude(approve_status="REJECTED").values('emp_id','edition','role__value','role_for__value','publisher_type__value','title','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','approve_status')
                            ##print("hiii-aks")
                            status=200
                            data_values={'data':list(q)}
                            
                        elif(data['sno']=='2'):
                            q=Researchconference.objects.filter(emp_id=data['emp_id'],paper_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_conference__value','sub_category__value','sponsered','conference_title','paper_title','published_date','organized_by','journal_name','volume_no','issue_no','isbn','page_no','author__value','author__value','conference_from','conference_to','other_description','publisher_name','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                            s=Sponsers.objects.filter(spons_id=data['id'],field_type='SPONSOR',type='CONFERENCE').values('sponser_name','type','field_type')
                            
                            status=200
                            data_values={'data':list(q),'sponsers':list(s)}
                        elif(data['sno']=='1'):
                            q=Researchjournal.objects.filter(emp_id=data['emp_id'],paper_title=data['title']).exclude(approve_status="REJECTED").values('emp_id','category__value','type_of_journal__value','sub_category__value','published_date','paper_title','impact_factor','journal_name','volume_no','issue_no','isbn','page_no','author__value','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','approve_status')
                            
                            status=200
                            data_values={'data':list(q)}
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=200)

def website_aar(request):
    data_values = ''
    if(request.method=='POST'):
            data=json.loads(request.body.decode("utf-8"))

            if(data['dept']):
                emp_arr=[]
                emps=EmployeePrimdetail.objects.filter(dept=int(data['dept'])).values('emp_id','name')



                if(data['sno']=='8'):
                    b=[]
                    for emp in emps:
                        # ##print(emp)
                        Eid=emp['emp_id']
                        name=emp['name']
                        # q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status')
                        q=LecturesTalks.objects.filter(emp_id=Eid,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','category__value','date','topic','contact_number','e_mail')

                        if(q.count()>0):
                            for i in q:
                                i['name'] = name
                                # d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                b.append(i)

                    status=200
                    data_values={'data':list(b)}
                elif(data['sno']=='7'):
                    # emps=EmployeePrimdetail.objects.filter(dept=int(data['dept'])).values('emp_id')
                    b=[]
                    for emp in emps:
                        # ##print(emp)
                        Eid=emp['emp_id']
                        name=emp['name']
                        # q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status')
                        q=TrainingDevelopment.objects.filter(emp_id=Eid,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','from_date','to_date','title','attended')

                        if(q.count()>0):
                            for i in q:
                                i['name'] = name
                                # d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                b.append(i)
                    q=b
                    for i in q:
                        s=Discipline.objects.filter(id=i['emp_id'],type="TRAINING").values('value1__value')
                        s1=Sponsers.objects.filter(spons_id=i['emp_id'],field_type='SPONSOR',type="TRAINING").values('sponser_name','contact_number','amount')
                        s2=Sponsers.objects.filter(spons_id=i['emp_id'],field_type='ASSOCIATION',type="TRAINING").values('sponser_name','field_type')
                        try:
                            s= dict(s[0])
                            for key, value in s.items():
                                  i[key]=value
                        except:
                            pass
                        try:
                            s1= dict(s1[0])
                            for key, value in s1.items():
                                  i[key]=value
                        except:
                            pass
                        try:
                            s2= dict(s2[0])
                            for key, value in s2.items():
                                  i[key]=value
                        except:
                            pass


                    status=200

                    data_values={'data':list(q)}
                elif(data['sno']=='6'):
                    b=[]
                    for emp in emps:
                        # ##print(emp)
                        Eid=emp['emp_id']
                        name=emp['name']
                        q=ProjectConsultancy.objects.filter(emp_id=Eid,approve_status="APPROVED").exclude(approve_status="REJECTED").values('id','emp_id','title','descreption','start_date','end_date','team_size')
                        if(q.count()>0):
                            for i in q:
                                i['name'] = name
                                # d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                b.append(i)
                    q=b
                    for i in q:
                        s=Discipline.objects.filter(id=i['id'],type="PROJECT/CONSULTANCY").values('value1__value')
                        s1=Sponsers.objects.filter(spons_id=i['id'],field_type='SPONSOR',type="PROJECT").values('sponser_name','type')
                        s2=Sponsers.objects.filter(spons_id=i['id'],field_type='ASSOCIATION',type="PROJECT").values('sponser_name','type')
                        try:
                            s= dict(s[0])
                            for key, value in s.items():
                                  i[key]=value
                        except:
                            pass
                        try:
                            s1= dict(s1[0])
                            for key, value in s1.items():
                                  i[key]=value
                        except:
                            pass
                        try:
                            s2= dict(s2[0])
                            for key, value in s2.items():
                                  i[key]=value
                        except:
                            pass

                    status=200

                    data_values={'data':list(q)}
                elif(data['sno']=='5'):
                    b=[]
                    for emp in emps:
                        # print(emp)
                        Eid=emp['emp_id']
                        name=emp['name']
                        q=Patent.objects.filter(emp_id=Eid,approve_status="APPROVED").exclude(approve_status="REJECTED").values('id','title','descreption','date','company_name','emp_id')
                        if(q.count()>0):
                            for i in q:
                                i['name'] = name
                                # d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                b.append(i)
                    q=b
                    print(q)
                    for i in q:
                        print(i)
                        s2=Discipline.objects.filter(id=i['id'],type="PATENT").values('value1__value')
                        try:
                            s2= dict(s2[0])
                            for key, value in s2.items():
                                i[key]=value
                        except:
                            pass

                    status=200
                    data_values={'data':list(q)}
                elif(data['sno']=='4'):
                    b=[]
                    for emp in emps:
                        # ##print(emp)
                        Eid=emp['emp_id']
                        name=emp['name']
                        # q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status')
                        q=Researchguidence.objects.filter(emp_id=Eid,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','guidence__value','no_of_students','project_title','area_of_spec')
                        if(q.count()>0):
                            for i in q:
                                i['name'] = name
                                # d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                b.append(i)
                    q=b
                    status=200
                    data_values={'data':list(q)}
                elif(data['sno']=='3'):
                    b=[]
                    for emp in emps:
                        # ##print(emp)
                        Eid=emp['emp_id']
                        name=emp['name']
                        # q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status')
                        q=Books.objects.filter(emp_id=Eid,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','role__value','role_for__value','title','published_date','isbn','publisher_website')
                        if(q.count()>0):
                            for i in q:
                                i['name'] = name
                                # d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                b.append(i)
                    q=b
                    status=200
                    data_values={'data':list(q)}
                    
                elif(data['sno']=='2'):
                    # ##print(q.query)
                    b=[]
                    for emp in emps:
                        # ##print(emp)
                        Eid=emp['emp_id']
                        name=emp['name']
                        # q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status')
                        q=Researchconference.objects.filter(emp_id=Eid,approve_status="APPROVED").exclude(approve_status="REJECTED").values('id','emp_id','conference_title','paper_title','published_date','journal_name','isbn','author__value','author')
                        if(q.count()>0):
                            for i in q:
                                i['name'] = name
                                # d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                b.append(i)
                    q=b
                    for i in q:
                        s=Sponsers.objects.filter(spons_id=i['id'],field_type='SPONSOR',type='CONFERENCE').values('sponser_name','type','field_type')
                        try:
                            s= dict(s[0])
                            for key, value in s.items():
                                i[key]=value
                        except:
                            pass
                    status=200
                    data_values={'data':list(q)}
                elif(data['sno']=='1'):
                    # ##print(q.query)
                    b=[]
                    for emp in emps:
                        # ##print(emp)
                        Eid=emp['emp_id']
                        name=emp['name']
                        # q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status')
                        q=Researchjournal.objects.filter(emp_id=Eid,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','published_date','paper_title','journal_name','isbn')
                        if(q.count()>0):
                            for i in q:
                                i['name'] = name
                                # d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status']}
                                b.append(i)
                    q=b
                    status=200
                    data_values={'data':list(q)}
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=200)

def website_single(request):
    data_values = ''
    if(request.method=='POST'):
            ##print(request.body)
            data=json.loads(request.body)

            if(data['emp_id']):
                emps = data['emp_id']

                Lectures=LecturesTalks.objects.filter(emp_id__in=emps,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','category__value','date','topic','contact_number','e_mail')


                Training=TrainingDevelopment.objects.filter(emp_id__in=emps,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','from_date','to_date','title','attended')
                for i in range(Training.count()):
                    s=Discipline.objects.filter(id=Training[i]['id'],type="TRAINING").values('value1__value')
                    s1=Sponsers.objects.filter(spons_id=Training[i]['id'],field_type='SPONSOR',type="TRAINING").values('sponser_name','type')
                    s2=Sponsers.objects.filter(spons_id=Training[i]['id'],field_type='ASSOCIATION',type="TRAINING").values('sponser_name','type')
                    try:
                        s= dict(s[0])
                        for key, value in s.items():
                              q[i][key]=value
                    except:
                        pass
                    try:
                        s1= dict(s1[0])
                        for key, value in s1.items():
                              q[i][key]=value
                    except:
                        pass
                    try:
                        s2= dict(s2[0])
                        for key, value in s2.items():
                              q[i][key]=value
                    except:
                        pass


                Project=ProjectConsultancy.objects.filter(emp_id__in=emps,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','title','descreption','start_date','end_date','team_size')
                for i in range(Project.count()):
                    s=Discipline.objects.filter(id=Project[i]['id'],type="PROJECT/CONSULTANCY").values('value1__value')
                    s1=Sponsers.objects.filter(spons_id=Project[i]['id'],field_type='SPONSOR',type="PROJECT").values('sponser_name','type')
                    s2=Sponsers.objects.filter(spons_id=Project[i]['id'],field_type='ASSOCIATION',type="PROJECT").values('sponser_name','type')
                    try:
                        s= dict(s[0])
                        for key, value in s.items():
                              Project[i][key]=value
                    except:
                        pass
                    try:
                        s1= dict(s1[0])
                        for key, value in s1.items():
                              Project[i][key]=value
                    except:
                        pass
                    try:
                        s2= dict(s2[0])
                        for key, value in s2.items():
                              Project[i][key]=value
                    except:
                        pass


                Pat=Patent.objects.filter(emp_id__in=emps).exclude(approve_status="REJECTED").values('title','descreption','date','company_name','emp_id')
                for i in range(Pat.count()):
                    s2=Discipline.objects.filter(id=Pat[i]['id'],type="PATENT").values('value1__value')
                    try:
                        s2= dict(s2[0])
                        for key, value in s2.items():
                            Pat[i][key]=value
                    except:
                        pass



                Researchguide=Researchguidence.objects.filter(emp_id__in=emps,approve_status="APPROVED").exclude(approve_status="REJECTED").values('emp_id','guidence__value','no_of_students','project_title','area_of_spec')


                Book=Books.objects.filter(emp_id__in=emps).exclude(approve_status="REJECTED").values('emp_id','role__value','role_for__value','title','published_date','isbn','publisher_website')



                Researchconf=Researchconference.objects.filter(emp_id__in=emps).exclude(approve_status="REJECTED").values('id','emp_id','conference_title','paper_title','published_date','journal_name','isbn','author__value','author')

                for i in range(Researchconf.count()):
                    s=Sponsers.objects.filter(spons_id=Researchconf[i]['id'],field_type='SPONSOR',type='CONFERENCE').values('sponser_name','type','field_type')
                    try:
                        s= dict(s[0])
                        for key, value in s.items():
                              Researchconf[i][key]=value
                    except:
                        pass


                Researchjou=Researchjournal.objects.filter(emp_id__in=emps).exclude(approve_status="REJECTED").values('emp_id','published_date','paper_title','journal_name','isbn')

                status=200
                data_values={'Researchjou':list(Researchjou),'Researchconf':list(Researchconf),'Book':list(Book),'Researchguide':list(Researchguide),'Patent':list(Pat),'LecturesTalks':list(Lectures),'Project':list(Project),'Training':list(Training)}
            else:
                status=500

    else:
        status=500
    return JsonResponse(data_values,safe=False,status=200)

def director_report(request):
    msg={}
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337,425])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if(data['test']=='1'):
                        ##print data

                        # dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                        # ##print dept
                        emps=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                        ##print emps
                        if(data['type']=='1'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                ###print Eid
                                name=emp['name']
                                q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status','category__value','type_of_journal__value','published_date','journal_name','volume_no','issue_no','isbn','author__value')
                                ###print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'journal_type':i['type_of_journal__value'],'publish_date':i['published_date'],'journal_name':i['journal_name'],'volume_no':i['volume_no'],'issue_no':i['issue_no'],'isbn':i['isbn'],'author':i['author__value']}
                                        b.append(d)
                        elif(data['type']=='2'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchconference.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('paper_title','id','emp_id','approve_status','category__value','type_of_conference__value','conference_title','published_date','organized_by','author__value','conference_from','conference_to','publisher_name')

                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'conference_type':i['type_of_conference__value'],'conference_title':i['conference_title'],'publish_date':i['published_date'],'organized_by':i['organized_by'],'author':i['author__value'],'conference_from':i['conference_from'],'conference_to':i['conference_to'],'publisher_name':i['publisher_name']}
                                        b.append(d)
                        elif(data['type']=='3'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Books.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('title','id','emp_id','approve_status','role__value','role_for__value','publisher_type','edition','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'role':i['role__value'],'role_for':i['role_for__value'],'publisher_type':i['publisher_type'],'edition':i['edition'],'publish_date':i['published_date'],'chapter':i['chapter'],'isbn':i['isbn'],'copyright_status':i['copyright_status'],'copyright_no':i['copyright_no'],'author':i['author__value'],'publisher_name':i['publisher_name']}
                                        b.append(d)
                        elif(data['type']=='4'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Researchguidence.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('project_title','id','emp_id','approve_status','guidence__value','course__value','degree__value','no_of_students','degree_awarded','uni_type__value','uni_name','status__value','area_of_spec')
                                ###print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['project_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'guidence':i['guidence__value'],'course':i['course__value'],'degree_awarded':i['degree_awarded'],'degree':i['degree__value'],'no_of_students':i['no_of_students'],'uni_type':i['uni_type__value'],'uni_name':i['uni_name'],'status':i['status__value'],'area_of_spec':i['area_of_spec']}
                                        b.append(d)
                        elif(data['type']=='5'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Patent.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('title','id','emp_id','approve_status','descreption','collaboration','company_name','incorporate_status__value','status','date','owner__value')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'descreption':i['descreption'],'collaboration':i['collaboration'],'company_name':i['company_name'],'incorporate_status':i['incorporate_status__value'],'status':i['status'],'date':i['date'],'owner':i['owner__value']}
                                        b.append(d)



                        elif(data['type']=='6'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                c=0
                                q=ProjectConsultancy.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('title','id','emp_id','approve_status','type__value','status__value','sector__value','start_date','end_date','principal_investigator','co_principal_investigator','sponsored','team_size','association')
                                c=q.count()
                                if(c>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'type__value':i['type__value'],'status__value':i['status__value'],'sector__value':i['sector__value'],'start_date':i['start_date'],'end_date':i['end_date'],'principal_investigator':i['principal_investigator'],'co_principal_investigator':i['co_principal_investigator'],'sponsored':i['sponsored'],'team_size':i['team_size'],'association':i['association']}
                                        b.append(d)


                        elif(data['type']=='7'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=TrainingDevelopment.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('title','id','emp_id','approve_status','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','venue','participants','organizers','attended','collaborations','sponsership')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'role':i['role__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaborations':i['collaborations'],'sponsership':i['sponsership']}
                                        b.append(d)


                        elif(data['type']=='8'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=LecturesTalks.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('topic','id','emp_id','approve_status','category__value','type__value','role__value','organization_sector__value','incorporation_status__value','venue','participants')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['topic'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'role':i['role__value']}
                                        b.append(d)

                        data_values={'data':b}
                        status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def director_department_report(request):
    msg={}
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337,425])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='D').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}
                    status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if(data['test']=='1'):
                        
                        emps=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                        ###print emps
                        if(data['type']=='267'):
                            month=data['month']
                            date=month.split('T')
                            date=datetime.datetime.strptime(date[0],'%Y-%m-%d').date()
                            ##print date
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                ###print Eid
                                name=emp['name']
                                q=guestLectures.objects.filter(emp_id=Eid).values('topic','date','speaker','designation','organization','speaker_profile','contact_number','participants_no','remark')
                                ##print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'topic':i['topic'],'date':i['date'],'speaker':i['speaker'],'designation':i['designation'],'organization':i['organization'],'speaker_profile':i['speaker_profile'],'contact_number':i['contact_number'],'participants_no':i['participants_no'],'remark':i['remark'],'emp_id':Eid,'name':name}
                                        b.append(d)
                        elif(data['type']=='268'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=industrialVisit.objects.filter(emp_id=Eid).values('industry','date','address','contact_person','contact_number','e_mail','participants_no','remark')
                                ##print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'industry':i['industry'],'date':i['date'],'address':i['address'],'contact_person':i['contact_person'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'participants_no':i['participants_no'],'remark':i['remark'],'emp_id':Eid,'name':name}
                                        b.append(d)
                        elif(data['type']=='269'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=MouSigned.objects.filter(emp_id=Eid).values('date','organization','objective','valid_upto','contact_number','e_mail')
                                ##print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'organization':i['organization'],'date':i['date'],'objective':i['objective'],'valid_upto':i['valid_upto'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'emp_id':Eid,'name':name}
                                        b.append(d)
                        elif(data['type']=='270'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=eventsorganized.objects.filter(emp_id=Eid).values('category__value','type__value','from_date','to_date','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaboration','sponsership','description')
                                ##print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'category__value':i['category__value'],'type__value':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'organization_sector__value':i['organization_sector__value'],'incorporation_status__value':i['incorporation_status__value'],'title':i['title'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaboration':i['collaboration'],'sponsership':i['sponsership'],'description':i['description'],'emp_id':Eid,'name':name}
                                        b.append(d)
                        elif(data['type']=='271'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=Hobbyclub.objects.filter(emp_id=Eid).values('club_name__value','project_title','start_date','end_date','project_incharge__value','team_size','project_description','project_cost','project_outcome')
                                ##print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'club_name__value':i['club_name__value'],'project_title':i['project_title'],'start_date':i['start_date'],'end_date':i['end_date'],'project_incharge__value':i['project_incharge__value'],'team_size':i['team_size'],'project_description':i['project_description'],'project_cost':i['project_cost'],'project_outcome':i['project_outcome'],'emp_id':Eid,'name':name}
                                        b.append(d)



                        elif(data['type']=='272'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                c=0
                                q=SummerWinterSchool.objects.filter(emp_id=Eid).values('start_date','end_date','resource_person','topic','participant_number','participant_fee')
                                ##print q
                                if(q.count()>0):
                                    for i in q:
                                        d={'start_date':i['start_date'],'end_date':i['end_date'],'resource_person':i['resource_person'],'topic':i['topic'],'participant_number':i['participant_number'],'participant_fee':i['participant_fee'],'emp_id':Eid,'name':name}
                                        b.append(d)

                        elif(data['type']=='7'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=TrainingDevelopment.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('title','id','emp_id','approve_status','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','venue','participants','organizers','attended','collaborations','sponsership')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'role':i['role__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaborations':i['collaborations'],'sponsership':i['sponsership']}
                                        b.append(d)


                        elif(data['type']=='8'):
                            b=[]
                            for emp in emps:
                                Eid=emp['emp_id']
                                name=emp['name']
                                q=LecturesTalks.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid).values('topic','id','emp_id','approve_status','category__value','type__value','role__value','organization_sector__value','incorporation_status__value','venue','participants')
                                if(q.count()>0):
                                    for i in q:
                                        d={'title':i['topic'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'role':i['role__value']}
                                        b.append(d)

                        data_values={'data':b}
                        status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)


def delete_aar_employee(request):
    msg={}
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if(check == 200):
                if(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
                    if (data['test']==1):
                        id=data['id']
                        query_delete=Researchguidence.objects.filter(id=id).update(approve_status='DELETE')
                        data_values={"OK":"Data Deleted Successfully"}
                        status=200
                    elif(data['test']==2):
                        id=data['id']
                        query_delete=Books.objects.filter(id=id).update(approve_status='DELETE')
                        data_values={"OK":"Data Deleted Successfully"}
                        status=200
                    elif(data['test']==3):
                        id=data['id']
                        query_delete=Researchjournal.objects.filter(id=id).update(approve_status='DELETE')
                        data_values={"OK":"Data Deleted Successfully"}
                        status=200
                    elif(data['test']==4):
                        id=data['id']
                        query_delete=Researchconference.objects.filter(id=id).update(approve_status='DELETE')
                        data_values={"OK":"Data Deleted Successfully"}
                        status=200
                    elif(data['test']==5):
                        id=data['id']
                        query_delete=Patent.objects.filter(id=id).update(approve_status='DELETE')
                        data_values={"OK":"Data Deleted Successfully"}
                        status=200
                    elif(data['test']==6):
                        id=data['id']
                        title=data['title']
                        query_delete=ProjectConsultancy.objects.filter(id=id).update(approve_status='DELETE')
                        data_values={"OK":"Data Deleted Successfully"}
                        status=200
                    elif(data['test']==7):
                        id=data['id']
                        query_delete=TrainingDevelopment.objects.filter(id=id).update(approve_status='DELETE')
                        data_values={"OK":"Data Deleted Successfully"}
                        status=200
                    elif(data['test']==8):
                        id=data['id']
                        query_delete=LecturesTalks.objects.filter(id=id).update(approve_status='DELETE')
                        data_values={"OK":"Data Deleted Successfully"}
                        status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def aar_dept_report(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337,1348])

            if(check == 200):
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='D').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}
                    status=200
                if(request.method=='POST'):
                    data=json.loads(request.body)
                    ##print data
                    fromyear=int(data['fromyear'])
                    frommonth=int(data['frommonth'])
                    fromdate=datetime.date(fromyear,frommonth,1)
                    fdate=datetime.date(fromyear, frommonth ,1).strftime('%Y-%m-%d')
                    toyear=int(data['toyear'])
                    tomonth=int(data['tomonth'])
                    todate=datetime.date(toyear,tomonth,30)
                    tdate=datetime.date(toyear, tomonth ,30).strftime('%Y-%m-%d')
                    if(data['type']=='267'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=guestLectures.objects.filter(date__gte=fdate,date__lte=tdate).extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','topic','speaker','designation','organization','speaker_profile','contact_number','e_mail','participants_no','emp_id__dept__value')
                            ##print(query_data)
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'topic':i['topic'],'date':i['date'],'speaker':i['speaker'],'designation':i['designation'],'organization':i['organization'],'speaker_profile':i['speaker_profile'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'participants_no':i['participants_no'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                query_data=guestLectures.objects.filter(emp_id=emp_id,date__gte=fdate,date__lte=tdate).extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','topic','speaker','designation','organization','speaker_profile','contact_number','e_mail','participants_no','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'topic':i['topic'],'date':i['date'],'speaker':i['speaker'],'designation':i['designation'],'organization':i['organization'],'speaker_profile':i['speaker_profile'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'participants_no':i['participants_no'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='268'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=industrialVisit.objects.filter(date__gte=fdate,date__lte=tdate).extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','industry','address','contact_person','contact_number','e_mail','participants_no','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'industry':i['industry'],'date':i['date'],'address':i['address'],'contact_person':i['contact_person'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'participants_no':i['participants_no'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                query_data=industrialVisit.objects.filter(emp_id=emp_id,date__gte=fdate,date__lte=tdate).extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','industry','address','contact_person','contact_number','e_mail','participants_no','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'industry':i['industry'],'date':i['date'],'address':i['address'],'contact_person':i['contact_person'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'participants_no':i['participants_no'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='269'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=MouSigned.objects.filter(date__gte=fdate,date__lte=tdate).extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','organization','objective','valid_upto','contact_number','e_mail','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'organization':i['organization'],'date':i['date'],'objective':i['objective'],'valid_upto':i['valid_upto'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                query_data=MouSigned.objects.filter(emp_id=emp_id,date__gte=fdate,date__lte=tdate).extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','organization','objective','valid_upto','contact_number','e_mail','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'organization':i['organization'],'date':i['date'],'objective':i['objective'],'valid_upto':i['valid_upto'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='270'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=eventsorganized.objects.filter(from_date__gte=fdate,to_date__lte=tdate).extra(select={'from_date':"DATE_FORMAT(from_date,'%%d-%%m-%%Y')",'to_date':"DATE_FORMAT(to_date,'%%d-%%m-%%Y')"}).values('category__value','type__value','from_date','to_date','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaboration','sponsership','description','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'category__value':i['category__value'],'type__value':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'organization_sector__value':i['organization_sector__value'],'incorporation_status__value':i['incorporation_status__value'],'title':i['title'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaboration':i['collaboration'],'sponsership':i['sponsership'],'description':i['description'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                query_data=eventsorganized.objects.filter(emp_id=emp_id,from_date__gte=fdate,to_date__lte=tdate).extra(select={'from_date':"DATE_FORMAT(from_date,'%%d-%%m-%%Y')",'to_date':"DATE_FORMAT(to_date,'%%d-%%m-%%Y')"}).values('category__value','type__value','from_date','to_date','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaboration','sponsership','description','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'category__value':i['category__value'],'type__value':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'organization_sector__value':i['organization_sector__value'],'incorporation_status__value':i['incorporation_status__value'],'title':i['title'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaboration':i['collaboration'],'sponsership':i['sponsership'],'description':i['description'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='271'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Hobbyclub.objects.filter(start_date__gte=fdate,end_date__lte=tdate).extra(select={'start_date':"DATE_FORMAT(start_date,'%%d-%%m-%%Y')",'end_date':"DATE_FORMAT(end_date,'%%d-%%m-%%Y')"}).values('club_name','project_title','start_date','end_date','project_incharge','team_size','project_description','project_cost','project_outcome','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'club_name':i['club_name'],'project_title':i['project_title'],'start_date':i['start_date'],'end_date':i['end_date'],'project_incharge':i['project_incharge'],'team_size':i['team_size'],'project_description':i['project_description'],'project_cost':i['project_cost'],'project_outcome':i['project_outcome'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                query_data=Hobbyclub.objects.filter(emp_id=emp_id,start_date__gte=fdate,end_date__lte=tdate).extra(select={'start_date':"DATE_FORMAT(start_date,'%%d-%%m-%%Y')",'end_date':"DATE_FORMAT(end_date,'%%d-%%m-%%Y')"}).values('club_name','project_title','start_date','end_date','project_incharge','team_size','project_description','project_cost','project_outcome','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'club_name':i['club_name'],'project_title':i['project_title'],'start_date':i['start_date'],'end_date':i['end_date'],'project_incharge':i['project_incharge'],'team_size':i['team_size'],'project_description':i['project_description'],'project_cost':i['project_cost'],'project_outcome':i['project_outcome'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='272'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=SummerWinterSchool.objects.filter(start_date__gte=fdate,end_date__lte=tdate).extra(select={'start_date':"DATE_FORMAT(start_date,'%%d-%%m-%%Y')",'end_date':"DATE_FORMAT(end_date,'%%d-%%m-%%Y')"}).values('start_date','end_date','resource_person','topic','participant_number','participant_fee','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'start_date':i['start_date'],'end_date':i['end_date'],'resource_person':i['resource_person'],'topic':i['topic'],'participant_number':i['participant_number'],'participant_fee':i['participant_fee'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                query_data=SummerWinterSchool.objects.filter(emp_id=emp_id,start_date__gte=fdate,end_date__lte=tdate).extra(select={'start_date':"DATE_FORMAT(start_date,'%%d-%%m-%%Y')",'end_date':"DATE_FORMAT(end_date,'%%d-%%m-%%Y')"}).values('start_date','end_date','resource_person','topic','participant_number','participant_fee','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'start_date':i['start_date'],'end_date':i['end_date'],'resource_person':i['resource_person'],'topic':i['topic'],'participant_number':i['participant_number'],'participant_fee':i['participant_fee'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='273'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Achievement.objects.filter(type='STUDENT',t_date__gte=fdate,t_date__lte=tdate).values('category__value','description','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'category__value':i['category__value'],'description':i['description'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                query_data=Achievement.objects.filter(emp_id=emp_id,type='STUDENT',t_date__gte=fdate,t_date__lte=tdate).values('category__value','description','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'category__value':i['category__value'],'description':i['description'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)

                    elif(data['type']=='274'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Achievement.objects.filter(type='DEPARTMENT',t_date__gte=fdate,t_date__lte=tdate).values('category__value','description','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'category__value':i['category__value'],'description':i['description'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                query_data=Achievement.objects.filter(emp_id=emp_id,type='DEPARTMENT',t_date__gte=fdate,t_date__lte=tdate).values('category__value','description','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'category__value':i['category__value'],'description':i['description'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    data_values={'data':retrieve_data}
                    status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def aar_hod_dept_report(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337,319])
            if(check == 200):
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='D').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}           
                    status=200
                if(request.method=='POST'):
                    data=json.loads(request.body)
                    fromyear=int(data['fromyear'])
                    frommonth=int(data['frommonth'])
                    fromdate=datetime.date(fromyear,frommonth,1)
                    fdate=datetime.date(fromyear, frommonth ,1).strftime('%Y-%m-%d')
                    toyear=int(data['toyear'])
                    tomonth=int(data['tomonth'])
                    todate=datetime.date(toyear,tomonth,30)
                    tdate=datetime.date(toyear, tomonth ,30).strftime('%Y-%m-%d')
                    if(data['type']=='267'):
                        dept=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        retrieve_data=[]
                        for emp in emps:
                            Eid=emp['emp_id']
                            name=emp['name']
                            query_data=guestLectures.objects.filter(emp_id=Eid,date__lte=tdate,date__gte=fdate).values('date','topic','speaker','designation','organization','speaker_profile','contact_number','e_mail','participants_no','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'Topic':i['topic'],'Date':i['date'],'Speaker':i['speaker'],'Designation':i['designation'],'Organization':i['organization'],'Speaker Profile':i['speaker_profile'],'Contact Number':i['contact_number'],'Email':i['e_mail'],'Participants Number':i['participants_no'],'Department':i['emp_id__dept__value']}
                                    retrieve_data.append(d)

                    elif(data['type']=='268'):
                        dept=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        retrieve_data=[]
                        for emp in emps:
                            Eid=emp['emp_id']
                            name=emp['name']
                            query_data=industrialVisit.objects.filter(emp_id=Eid,date__lte=tdate,date__gte=fdate).values('date','industry','address','contact_person','contact_number','e_mail','participants_no','emp_id__dept__value','remark')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'Industry':i['industry'],'Date':i['date'],'Address':i['address'],'Contact Person':i['contact_person'],'Contact Number':i['contact_number'],'Email':i['e_mail'],'Participants Number':i['participants_no'],'Department':i['emp_id__dept__value']}
                                    retrieve_data.append(d)

                    elif(data['type']=='269'):
                        dept=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        retrieve_data=[]
                        for emp in emps:
                            Eid=emp['emp_id']
                            name=emp['name']
                            query_data=MouSigned.objects.filter(emp_id=Eid,date__lte=tdate,date__gte=fdate).values('date','organization','objective','valid_upto','contact_number','e_mail','emp_id__dept__value','document')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'Organization':i['organization'],'Date':i['date'],'Objective':i['objective'],'Valid upto':i['valid_upto'],'Contact Number':i['contact_number'],'Email':i['e_mail'],'Department':i['emp_id__dept__value'],'document':i['document']}
                                    retrieve_data.append(d)

                    elif(data['type']=='270'):
                        dept=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        retrieve_data=[]
                        for emp in emps:
                            Eid=emp['emp_id']   
                            name=emp['name']
                            query_data=eventsorganized.objects.filter(emp_id=Eid,from_date__gte=fdate,to_date__lte=tdate).values('category__value','type__value','from_date','to_date','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaboration','sponsership','description','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'Category':i['category__value'],'Typevalue':i['type__value'],'From Date':i['from_date'],'To Date':i['to_date'],'Organization Sector':i['organization_sector__value'],'Incorporation Status__value':i['incorporation_status__value'],'Title':i['title'],'Venue':i['venue'],'Participants':i['participants'],'Organizers':i['organizers'],'Attended':i['attended'],'Collaboration':i['collaboration'],'Sponsorship':i['sponsership'],'Description':i['description'],'Department':i['emp_id__dept__value']}
                                    retrieve_data.append(d)

                    elif(data['type']=='271'):
                        dept=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        retrieve_data=[]
                        for emp in emps:
                            Eid=emp['emp_id']
                            name=emp['name']
                            query_data=Hobbyclub.objects.filter(emp_id=Eid,start_date__gte=fdate,end_date__lte=tdate).values('club_name','project_title','start_date','end_date','project_incharge','team_size','project_description','project_cost','project_outcome','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'Club Name':i['club_name'],'Project Title':i['project_title'],'Start Date':i['start_date'],'End Date':i['end_date'],'Project Incharge':i['project_incharge'],'Team Size':i['team_size'],'Project Description':i['project_description'],'Project Cost':i['project_cost'],'Project Outcome':i['project_outcome'],'Department':i['emp_id__dept__value']}
                                    retrieve_data.append(d)

                    elif(data['type']=='272'):
                        dept=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        retrieve_data=[]
                        for emp in emps:
                            Eid=emp['emp_id']
                            name=emp['name']
                            query_data=SummerWinterSchool.objects.filter(emp_id=Eid,start_date__gte=fdate,end_date__lte=tdate).values('start_date','end_date','resource_person','topic','participant_number','participant_fee','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'Start Date':i['start_date'],'End Date':i['end_date'],'Resource Person':i['resource_person'],'Topic':i['topic'],'Participant Number':i['participant_number'],'Participant Fee':i['participant_fee'],'Department':i['emp_id__dept__value']}
                                    retrieve_data.append(d)

                    elif(data['type']=='273'):
                        dept=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        retrieve_data=[]
                        for emp in emps:
                            Eid=emp['emp_id']
                            name=emp['name']
                            query_data=Achievement.objects.filter(emp_id=Eid,type='STUDENT').values('category__value','description','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'Category':i['category__value'],'Description':i['description'],'Department':i['emp_id__dept__value']}
                                    retrieve_data.append(d)

                    elif(data['type']=='274'):
                        dept=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('dept')
                        emps=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('emp_id','name')
                        retrieve_data=[]
                        for emp in emps:
                            Eid=emp['emp_id']
                            name=emp['name']
                            query_data=Achievement.objects.filter(emp_id=Eid,type='DEPARTMENT').values('category__value','description','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'Category':i['category__value'],'Description':i['description'],'Department':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                    data_values={'data':retrieve_data}
                    status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

def aar_emp_report(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337,1348])

            if(check == 200):
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    query1=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value')
                    data_values={'data':list(q),'data1':list(query1)}
                    status=200
                if(request.method=='POST'):
                    data=json.loads(request.body)
                    ##print data
                    fromyear=int(data['fromyear'])
                    frommonth=int(data['frommonth'])
                    fromdate=datetime.date(fromyear,frommonth,1)
                    fdate=datetime.date(fromyear, frommonth ,1).strftime('%Y-%m-%d')
                    toyear=int(data['toyear'])
                    tomonth=int(data['tomonth'])
                    todate=datetime.date(toyear,tomonth,30)
                    tdate=datetime.date(toyear, tomonth ,30).strftime('%Y-%m-%d')
                    ##print fdate
                    ##print tdate
                    if(data['type']=='1'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),published_date__gte=fdate,published_date__lte=tdate).values('paper_title','id','emp_id__name','approve_status','category__value','type_of_journal__value','published_date','journal_name','volume_no','issue_no','isbn','author__value','emp_id__dept__value','sub_category__value','impact_factor','page_no','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others')
                            ##print query_data
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'title':i['paper_title'],'id':i['id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'category':i['category__value'],'journal_type':i['type_of_journal__value'],'publish_date':i['published_date'],'journal_name':i['journal_name'],'volume_no':i['volume_no'],'issue_no':i['issue_no'],'isbn':i['isbn'],'author':i['author__value'],'dept':i['emp_id__dept__value'],'sub_category':i['sub_category__value'],'impact_factor':i['impact_factor'],'page_no':i['page_no'],'publisher_name':i['publisher_name'],'publisher_address1':i['publisher_address1'],'publisher_address2':i['publisher_address2'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website'],'other_journal':i['others']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                name=i['name']
                                query_data=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=emp_id,published_date__gte=fdate,published_date__lte=tdate).values('paper_title','id','emp_id','emp_id__name','approve_status','category__value','type_of_journal__value','published_date','journal_name','volume_no','issue_no','isbn','author__value','emp_id__dept__value','sub_category__value','impact_factor','page_no','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_email','publisher_website','others','publisher_contact')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'journal_type':i['type_of_journal__value'],'publish_date':i['published_date'],'journal_name':i['journal_name'],'volume_no':i['volume_no'],'issue_no':i['issue_no'],'isbn':i['isbn'],'author':i['author__value'],'dept':i['emp_id__dept__value'],'sub_category':i['sub_category__value'],'impact_factor':i['impact_factor'],'page_no':i['page_no'],'publisher_name':i['publisher_name'],'publisher_address1':i['publisher_address1'],'publisher_address2':i['publisher_address2'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website'],'other_journal':i['others']}
                                        retrieve_data.append(d)
                    elif(data['type']=='2'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Researchconference.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),published_date__gte=fdate,published_date__lte=tdate).values('paper_title','id','emp_id__name','approve_status','category__value','type_of_conference__value','conference_title','published_date','organized_by','author__value','conference_from','conference_to','publisher_name','emp_id__dept__value','sub_category__value','sponsered','journal_name','issue_no','volume_no','isbn','page_no','other_description','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'title':i['paper_title'],'id':i['id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'category':i['category__value'],'conference_type':i['type_of_conference__value'],'conference_title':i['conference_title'],'publish_date':i['published_date'],'organized_by':i['organized_by'],'author':i['author__value'],'conference_from':i['conference_from'],'conference_to':i['conference_to'],'publisher_name':i['publisher_name'],'dept':i['emp_id__dept__value'],'sub_category__value':i['sub_category__value'],'sponsered':i['sponsered'],'journal_name':i['journal_name'],'issue_no':i['issue_no'],'volume_no':i['volume_no'],'isbn':i['isbn'],'page_no':i['page_no'],'other_description':i['other_description'],'publisher_address':i['publisher_address'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website'],'other_conference':i['others']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                name=i['name']
                                query_data=Researchconference.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=emp_id,published_date__gte=fdate,published_date__lte=tdate).values('paper_title','id','emp_id','approve_status','category__value','type_of_conference__value','conference_title','published_date','organized_by','author__value','conference_from','conference_to','publisher_name','emp_id__dept__value','sub_category__value','sponsered','journal_name','issue_no','volume_no','isbn','page_no','other_description','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'conference_type':i['type_of_conference__value'],'conference_title':i['conference_title'],'publish_date':i['published_date'],'organized_by':i['organized_by'],'author':i['author__value'],'conference_from':i['conference_from'],'conference_to':i['conference_to'],'publisher_name':i['publisher_name'],'dept':i['emp_id__dept__value'],'sub_category__value':i['sub_category__value'],'sponsered':i['sponsered'],'journal_name':i['journal_name'],'issue_no':i['issue_no'],'volume_no':i['volume_no'],'isbn':i['isbn'],'page_no':i['page_no'],'other_description':i['other_description'],'publisher_address':i['publisher_address'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website'],'other_conference':i['others']}
                                        retrieve_data.append(d)
                    elif(data['type']=='3'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Books.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),published_date__gte=fdate,published_date__lte=tdate).values('title','id','emp_id__name','approve_status','role__value','role_for__value','publisher_type__value','edition','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','emp_id__dept__value','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website')
                                ###print query_data
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'title':i['title'],'id':i['id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'role':i['role__value'],'role_for':i['role_for__value'],'publisher_type':i['publisher_type__value'],'edition':i['edition'],'publish_date':i['published_date'],'chapter':i['chapter'],'isbn':i['isbn'],'copyright_status':i['copyright_status'],'copyright_no':i['copyright_no'],'author':i['author__value'],'publisher_name':i['publisher_name'],'dept':i['emp_id__dept__value'],'publisher_address':i['publisher_address'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                            ###print query
                            retrieve_data=[]
                            for j in query:
                                Eid=j['emp_id']
                                name=j['name']
                                query_data=Books.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,published_date__gte=fdate,published_date__lte=tdate).values('title','id','emp_id','approve_status','role__value','role_for__value','publisher_type','edition','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','emp_id__dept__value','publisher_address','publisher_zip_code','publisher_contact','publisher_email','publisher_website')
                                ###print query_data
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'role':i['role__value'],'role_for':i['role_for__value'],'publisher_type':i['publisher_type'],'edition':i['edition'],'publish_date':i['published_date'],'chapter':i['chapter'],'isbn':i['isbn'],'copyright_status':i['copyright_status'],'copyright_no':i['copyright_no'],'author':i['author__value'],'publisher_name':i['publisher_name'],'dept':i['emp_id__dept__value'],'publisher_address':i['publisher_address'],'publisher_zip_code':i['publisher_zip_code'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website']}
                                        retrieve_data.append(d)
                    elif(data['type']=='4'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Researchguidence.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),date__lte=tdate,date__gte=fdate).values('project_title','id','emp_id__name','approve_status','guidence__value','course__value','degree__value','no_of_students','degree_awarded','uni_type__value','uni_name','status__value','area_of_spec','emp_id__dept__value','date')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'title':i['project_title'],'id':i['id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'guidence':i['guidence__value'],'course':i['course__value'],'degree_awarded':i['degree_awarded'],'degree':i['degree__value'],'no_of_students':['no_of_students'],'uni_type':i['uni_type__value'],'uni_name':i['uni_name'],'status':i['status__value'],'area_of_spec':i['area_of_spec'],'dept':i['emp_id__dept__value'],'date':i['date']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                Eid=i['emp_id']
                                name=i['name']
                                query_data=Researchguidence.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,date__lte=tdate,date__gte=fdate).values('project_title','id','emp_id','approve_status','guidence__value','course__value','degree__value','no_of_students','degree_awarded','uni_type__value','uni_name','status__value','area_of_spec','emp_id__dept__value','date')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'title':i['project_title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'guidence':i['guidence__value'],'course':i['course__value'],'degree_awarded':i['degree_awarded'],'degree':i['degree__value'],'no_of_students':['no_of_students'],'uni_type':i['uni_type__value'],'uni_name':i['uni_name'],'status':i['status__value'],'area_of_spec':i['area_of_spec'],'dept':i['emp_id__dept__value'],'date':i['date']}
                                        retrieve_data.append(d)
                    elif(data['type']=='5'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Patent.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),date__lte=tdate,date__gte=fdate).values('title','id','emp_id__name','approve_status','descreption','collaboration','company_name','incorporate_status__value','status','date','owner__value','emp_id__dept__value','level','number')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'title':i['title'],'id':i['id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'descreption':i['descreption'],'collaboration':i['collaboration'],'company_name':i['company_name'],'incorporate_status':i['incorporate_status__value'],'status':i['status'],'date':i['date'],'owner':i['owner__value'],'dept':i['emp_id__dept__value'],'level':i['level'],'number':i['number']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                name=i['name']
                                query_data=Patent.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=emp_id,date__lte=tdate,date__gte=fdate).values('title','id','emp_id','approve_status','descreption','collaboration','company_name','incorporate_status__value','status','date','owner__value','emp_id__dept__value','level','number')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'descreption':i['descreption'],'collaboration':i['collaboration'],'company_name':i['company_name'],'incorporate_status':i['incorporate_status__value'],'status':i['status'],'date':i['date'],'owner':i['owner__value'],'dept':i['emp_id__dept__value'],'level':i['level'],'number':i['number']}
                                        retrieve_data.append(d)
                    elif(data['type']=='6'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=ProjectConsultancy.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),end_date__gte=fdate,end_date__lte=tdate).values('title','id','emp_id__name','approve_status','type__value','status__value','sector__value','start_date','end_date','principal_investigator','co_principal_investigator','sponsored','team_size','association','emp_id__dept__value','principal_investigator_id','co_principal_investigator_id','descreption')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'title':i['title'],'id':i['id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'type__value':i['type__value'],'status__value':i['status__value'],'sector__value':i['sector__value'],'start_date':i['start_date'],'end_date':i['end_date'],'principal_investigator':i['principal_investigator'],'co_principal_investigator':i['co_principal_investigator'],'sponsored':i['sponsored'],'team_size':i['team_size'],'association':i['association'],'dept':i['emp_id__dept__value'],'principal_investigator_id':i['principal_investigator_id'],'co_principal_investigator_id':i['co_principal_investigator_id'],'patent_descreption':i['descreption']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                name=i['name']
                                query_data=ProjectConsultancy.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=emp_id,end_date__gte=fdate,end_date__lte=tdate).values('title','id','emp_id','approve_status','type__value','status__value','sector__value','start_date','end_date','principal_investigator','co_principal_investigator','sponsored','team_size','association','emp_id__dept__value','principal_investigator_id','co_principal_investigator_id','descreption')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'type__value':i['type__value'],'status__value':i['status__value'],'sector__value':i['sector__value'],'start_date':i['start_date'],'end_date':i['end_date'],'principal_investigator':i['principal_investigator'],'co_principal_investigator':i['co_principal_investigator'],'sponsored':i['sponsored'],'team_size':i['team_size'],'association':i['association'],'dept':i['emp_id__dept__value'],'principal_investigator_id':i['principal_investigator_id'],'co_principal_investigator_id':i['co_principal_investigator_id'],'patent_descreption':i['descreption']}
                                        retrieve_data.append(d)
                    elif(data['type']=='7'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=TrainingDevelopment.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),to_date__gte=fdate,to_date__lte=tdate).values('title','id','emp_id__name','approve_status','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','venue','participants','organizers','attended','collaborations','sponsership','emp_id__dept__value')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'title':i['title'],'id':i['id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'role':i['role__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaborations':i['collaborations'],'sponsership':i['sponsership'],'dept':i['emp_id__dept__value']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                name=i['name']
                                query_data=TrainingDevelopment.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=emp_id,to_date__gte=fdate,to_date__lte=tdate).values('title','id','emp_id','approve_status','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','venue','participants','organizers','attended','collaborations','sponsership','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'role':i['role__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaborations':i['collaborations'],'sponsership':i['sponsership'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='8'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=LecturesTalks.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),date__lte=tdate,date__gte=fdate).values('topic','id','emp_id__name','approve_status','category__value','type__value','role__value','organization_sector__value','incorporation_status__value','venue','participants','emp_id__dept__value','date','address','pin_code','contact_number','e_mail','website')
                            if(query_data.count()>0):
                                for i in query_data:
                                    d={'title':i['topic'],'id':i['id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'role':i['role__value'],'dept':i['emp_id__dept__value'],'date':i['date'],'address':i['address'],'pin_code':i['pin_code'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'website':i['website']}
                                    retrieve_data.append(d)
                        else:
                            query=EmployeePrimdetail.objects.filter(dept=data['dept']).values('emp_id','name')
                            ###print query
                            retrieve_data=[]
                            for i in query:
                                emp_id=i['emp_id']
                                name=i['name']
                                query_data=LecturesTalks.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=emp_id,date__lte=tdate,date__gte=fdate).values('topic','id','emp_id','approve_status','category__value','type__value','role__value','organization_sector__value','incorporation_status__value','venue','participants','emp_id__dept__value','date','address','pin_code','contact_number','e_mail','website')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'title':i['topic'],'id':i['id'],'emp_id':i['emp_id'],'name':name,'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'role':i['role__value'],'dept':i['emp_id__dept__value'],'date':i['date'],'address':i['address'],'pin_code':i['pin_code'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'website':i['website']}
                                        retrieve_data.append(d)
                    data_values={'data':retrieve_data}
                    status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)

############################################################### ANNUAL APRAISAL REPORT ##############################################################################
def getComponents(request):
    data_values={}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337,1362])
            if check == 200:
                if(request.method=='GET'):
                    if request.GET['request_type'] == 'organization':
                        query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="ORGANIZATION").values('sno','value')
                    elif request.GET['request_type'] == "department":
                        dept_sno=EmployeeDropdown.objects.filter(pid=request.GET['org'],value="DEPARTMENT").values('sno')
                        query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'],field="DEPARTMENT").values('sno','value')
                    elif request.GET['request_type'] == "emp_category":
                        query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="CATEGORY OF EMPLOYEE").values('sno','value')
                    elif(request.GET["request_type"]=="salary_type"):
                        query=AccountsDropdown.objects.filter(field="SALARY TYPE").exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
                    elif(request.GET["request_type"]=="constant_pay"):
                        query=AccountsDropdown.objects.filter(field="CONSTANT PAY DEDUCTIONS").exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
                    elif(request.GET["request_type"]=="ingredients_name"):
                        query=AccountsDropdown.objects.filter(field="SALARY COMPONENTS").exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
                    elif(request.GET["request_type"]=="variable_pay"):
                        query=AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS").exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
                    elif(request.GET["request_type"]=="pay_by"):
                        query=AccountsDropdown.objects.filter(field="PAYMENT OPTIONS").exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
                    elif(request.GET["request_type"]=="department"):
                        query=EmployeeDropdown.objects.filter(field="Department").exclude(value__isnull=True).values("sno","value")
                    elif(request.GET["request_type"]=="other_income"):
                        query=declaration_components(request.GET["request_type"])
                    elif(request.GET["request_type"]=="exemptions"):
                        query=declaration_components(request.GET["request_type"])

                    elif(request.GET["request_type"]=="residence_location"):
                        query=declaration_components(request.GET["request_type"])
                    elif(request.GET["request_type"]=="loss_deductions"):
                        query=declaration_components(request.GET["request_type"])

                    elif(request.GET["request_type"]=="child_elements"):
                        query=AccountsDropdown.objects.filter(staff_spid=request.GET['pid']).exclude(value__isnull=True).exclude(status="DELETE").values("sno","value")
                    else:
                        query=[]
                    status=200
                    data_values={'data':list(query)}
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500

    return JsonResponse(data=data_values,status=status)

def get_all_emp(dept,category):
    s = EmployeePrimdetail.objects.filter(emp_status='ACTIVE',dept=EmployeeDropdown.objects.get(sno=dept),emp_category=EmployeeDropdown.objects.get(sno=category)).exclude(emp_id="00007").extra(select={'emp_name':'name','emp_code':'emp_id'}).exclude(emp_status="SEPARATE").values('emp_name','emp_code','dept__value','desg__value').order_by('name').all()
    return s

def emp_detail(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[211,1362])
            if check==200:
                if request.method == 'GET':
                    org=request.GET['org']
                    dept=request.GET['dept']
                    ##print request.GET['emp_category']
                    category=request.GET['emp_category']
                    if (dept == 'ALL'):
                        if (category == 'ALL'):
                            s = EmployeePrimdetail.objects.filter(emp_status='ACTIVE').exclude(emp_id="00007").extra(select={'emp_name':'name','emp_code':'emp_id'}).exclude(emp_status="SEPARATE").values('emp_name','emp_code','dept__value','desg__value')
                        else:
                            s = EmployeePrimdetail.objects.filter(emp_status='ACTIVE',emp_category=EmployeeDropdown.objects.get(sno=category)).exclude(emp_id="00007").extra(select={'emp_name':'name','emp_code':'emp_id'}).exclude(emp_status="SEPARATE").values('emp_name','emp_code','dept__value','desg__value')
                    else:
                        s = get_all_emp(dept,category)
                    msg="Success"
                    status=200
                    data_values={'msg':msg,'data':list(s)}
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data=data_values,status=status)

def locking_unlocking(request):
    data_values={}

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[1362])
            if check==200:
                if request.method=='GET':
                    qry=LockingUnlocking.objects.extra(select={'fromDate':"DATE_FORMAT(fromDate,'%%d-%%m-%%Y %%H:%%i:%%s')", 'toDate':"DATE_FORMAT(toDate,'%%d-%%m-%%Y %%H:%%i:%%s')"}).values('Emp_Id','Emp_Id__name','fromDate','toDate').order_by('-id')
                    data_values = {'data':list(qry)}
                    status=200

                elif request.method == 'POST':
                    data=json.loads(request.body)
                    ##print data
                    emp_id=data['emp_id']
                    dept=data['dept']
                    category=data['emp_category']
                    fromDate=datetime.datetime.strptime(str(data['fromDate']),"%Y-%m-%d %H:%M:%S")
                    toDate=datetime.datetime.strptime(str(data['toDate']),"%Y-%m-%d %H:%M:%S")

                    if dept == 'ALL':
                        if category == 'ALL':
                            dept_sno=EmployeeDropdown.objects.filter(pid=data['org'],value="DEPARTMENT").values('sno')
                            query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'],field="DEPARTMENT").values('sno','value')
                            emp_cat = EmployeeDropdown.objects.filter(field = "CATEGORY OF EMPLOYEE").exclude(value__isnull=True).values('sno','value')
                            for d in query:
                                for q in emp_cat:
                                    s=get_all_emp(d['sno'],q['sno'])
                                    objs = (LockingUnlocking(Emp_Id=EmployeePrimdetail.objects.get(emp_id=e['emp_code']),fromDate=fromDate,toDate=toDate,unlocked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])) for e in s)
                                    q=LockingUnlocking.objects.bulk_create(objs)
                                    msg="Data Succesfully Inserted"
                        else:
                            dept_sno=EmployeeDropdown.objects.filter(pid=data['org'],value="DEPARTMENT").values('sno')
                            query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'],field="DEPARTMENT").values('sno','value')
                            emp_cat = EmployeeDropdown.objects.filter(value = "CATEGORY OF EMPLOYEE").exclude(value__isnull=True).values()
                            for d in query:
                                s=get_all_emp(d['sno'],category)
                                objs = (LockingUnlocking(Emp_Id=EmployeePrimdetail.objects.get(emp_id=e['emp_code']),fromDate=fromDate,toDate=toDate,unlocked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])) for e in s)
                                q=LockingUnlocking.objects.bulk_create(objs)
                                msg="Data Succesfully Inserted"

                    elif emp_id == 'ALL':
                        s=get_all_emp(dept,category)
                        objs = (LockingUnlocking(Emp_Id=EmployeePrimdetail.objects.get(emp_id=e['emp_code']),fromDate=fromDate,toDate=toDate,unlocked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])) for e in s)
                        q=LockingUnlocking.objects.bulk_create(objs)
                        msg="Data Succesfully Inserted"
                    else:
                        qry_ins = LockingUnlocking.objects.create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),fromDate=fromDate,toDate=toDate,unlocked_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
                        msg="Data Succesfully Inserted"

                    data_values = {'msg':msg}
                    status=200
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data=data_values,status=status)

def aar_increment_settings(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337,1362])
            if (check == 200):
                emp_id = request.session['hash1']
                if (request.method == 'POST'):

                    data = json.loads(request.body.decode("utf-8"))
                    amount = data['normal']
                    valueType = 'PERCENTAGE'
                    incrementType = data['selected_increment_type']
                    if incrementType == 'normal':
                        incrementType = 0
                    else:
                        incrementType = 1
                    data_values ={"data_value": "Success"}
                    objs = (AarIncrementSettings(t_date=str(datetime.datetime.now()), edit_by=EmployeePrimdetail.objects.get(emp_id = emp_id),increment_type=incrementType, salary_type=AccountsDropdown.objects.get(sno = sal_type),status='INSERT',value=amount, value_type=valueType, emp_category=EmployeeDropdown.objects.get(sno = data['Category_Employee']), desg=EmployeeDropdown.objects.get(sno = desg), cadre=EmployeeDropdown.objects.get(sno = cadre), ladder=EmployeeDropdown.objects.get(sno = ladder)) for sal_type in data['salary_type']  for desg in data['designation'] for cadre in data['cadre'] for ladder in data['ladder'])

                    q_ins = AarIncrementSettings.objects.bulk_create(objs)

                    # q = AarIncrementSettings.objects.create()
                    status = 200
                elif (request.method == 'GET'):
                    query1 = AccountsDropdown.objects.filter(field='SALARY TYPE').exclude(value=None).values('sno','value')
                    qry2=EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).extra(select={'ev':'value','es':'sno'}).values('ev','es')
                    data_values = {'data':list(query1),'data1':list(qry2)}
                    status = 200
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def get_isFormFilled(emp_id):
    formFilledQuery = AarPart2QuesAns.objects.filter(emp_id = emp_id).values()
    if len(list(formFilledQuery)) > 0:
        isFormFilled = True
    else:
        isFormFilled = False
    return isFormFilled

def isHODFormFilled(emp_id):
    formFilledQuery = hodrecommendatedamount.objects.filter(emp_id = emp_id).values()
    if len(list(formFilledQuery)) > 0:
        isFormFilled = True
    else:
        isFormFilled = False
    return isFormFilled

def isDirFormFilled(emp_id):
    formFilledQuery = AarPart2MarksDir.objects.filter(emp_id = emp_id).values()
    if len(list(formFilledQuery)) > 0:
        isFormFilled = True
    else:
        isFormFilled = False
    return isFormFilled

def gross_inc_per(emp_id1,dept_hod):
    ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg','ladder','dept','doj','name','cadre','emp_category')
    emp_category=ladder_sno[0]['emp_category']
    desg=ladder_sno[0]['desg']
    ladder=ladder_sno[0]['ladder']
    dept=ladder_sno[0]['dept']
    emp_category=ladder_sno[0]['emp_category']
    doj=ladder_sno[0]['doj']
    name=ladder_sno[0]['name']
    cadre=ladder_sno[0]['cadre']
    month=date.today().month-2
    if month==0:
        month=12
    gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
    session=getCurrentSession()
    q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value','salary_type')
    scale_consolidated=q7[0]['salary_type__value']

    q_increment_per = AarIncrementSettings.objects.filter(desg=desg,ladder=ladder,emp_category=emp_category,cadre=cadre,salary_type=q7[0]['salary_type']).exclude(status='DELETE').values('value')

    incr_per=0
    if len(q_increment_per)>0:
        incr_per=q_increment_per[0]['value']
    if  scale_consolidated == 'GRADE':
        total_gross=0
        for gd in gross_data:
            if gd['value'] == 'BASIC' or gd['value'] =='AGP':
                total_gross=total_gross+gd['gross_value']
    else:
        total_gross=0
        for gd in gross_data:
            total_gross=total_gross+gd['gross_value']
    ##print(scale_consolidated,total_gross,incr_per)
    # part 2
    result={'scale_consolidated':scale_consolidated,'total_gross':total_gross,'incr_per':incr_per}
    return result

def staff_shod(request):
    data_values = list()
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                status = 200
                msg={}
                emp_id = request.session['hash1']

                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg','ladder','dept','doj','name','cadre','emp_category')
                desgn_sno = list(desg_sno)
                desg = desgn_sno[0]['desg']
                dept_hod = desgn_sno[0]['dept']
                desg=desg_sno[0]['desg']
                ladder=desg_sno[0]['ladder']
                dept=desg_sno[0]['dept']
                emp_category=desg_sno[0]['emp_category']
                doj=desg_sno[0]['doj']
                name=desg_sno[0]['name']
                cadre=desg_sno[0]['cadre']
                
                month=date.today().month-2
                if month==0:
                    month=12
                gross_data=stored_gross_payable_salary_components(emp_id,getCurrentSession(),date.today().month-3)
                session=getCurrentSession()
                q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value','salary_type')
                scale_consolidated=q7[0]['salary_type__value']

                q_increment_per = AarIncrementSettings.objects.filter(desg=desg,ladder=ladder,emp_category=emp_category,cadre=cadre,salary_type=q7[0]['salary_type']).exclude(status='DELETE').values('value')

                incr_per=0
                if len(q_increment_per)>0:
                    incr_per=q_increment_per[0]['value']
                if  scale_consolidated == 'GRADE':
                    total_gross=0
                    for gd in gross_data:
                        if gd['value'] == 'BASIC' or gd['value'] =='AGP':
                            total_gross=total_gross+gd['gross_value']
                else:
                    total_gross=0
                    for gd in gross_data:
                        total_gross=total_gross+gd['gross_value']


                if(request.method == 'POST'):
                    data_values = list()
                    data = json.loads(request.body.decode("utf-8"))
                    emp_id1 = data[0]['emp_id']
                    fetch_data = AarPart2Marks.objects.filter(emp_id=emp_id1).values()

                    desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg','ladder','dept','doj','name','cadre','emp_category')
                    desgn_sno = list(desg_sno)
                    desg = desgn_sno[0]['desg']
                    dept_hod = desgn_sno[0]['dept']
                    desg=desg_sno[0]['desg']
                    ladder=desg_sno[0]['ladder']
                    dept=desg_sno[0]['dept']
                    emp_category=desg_sno[0]['emp_category']
                    doj=desg_sno[0]['doj']
                    name=desg_sno[0]['name']
                    cadre=desg_sno[0]['cadre']
                    
                    month=date.today().month-2
                    if month==0:
                        month=12
                    gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
                    session=getCurrentSession()
                    q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value','salary_type')
                    scale_consolidated=q7[0]['salary_type__value']

                    q_increment_per = AarIncrementSettings.objects.filter(desg=desg,ladder=ladder,emp_category=emp_category,cadre=cadre,salary_type=q7[0]['salary_type']).exclude(status='DELETE').values('value')

                    incr_per=0
                    if len(q_increment_per)>0:
                        incr_per=q_increment_per[0]['value']
                    if  scale_consolidated == 'GRADE':
                        total_gross=0
                        for gd in gross_data:
                            if gd['value'] == 'BASIC' or gd['value'] =='AGP':
                                total_gross=total_gross+gd['gross_value']
                    else:
                        total_gross=0
                        for gd in gross_data:
                            total_gross=total_gross+gd['gross_value']


                    ##print(fetch_data)
                    ##print fetch_data.count()
                    already_filled=False
                    if(fetch_data.count() > 0):
                        msg="Your Form Already Filled"
                        already_filled=True
                    if(data!=None):
                        ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                        lad_sno = list(ladder_sno)
                        ladd = lad_sno[0]['ladder']
                        if(ladd==661 or ladd==662 or ladd==663):
                            # part 1
                            desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg')
                            desgn_sno = list(desg_sno)
                            desg = desgn_sno[0]['desg']
                            ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                            lad_sno = list(ladder_sno)
                            ladd = lad_sno[0]['ladder']
                            dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('dept')
                            dep_sno = list(dept_no)
                            dep = dep_sno[0]['dept']
                            query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('name', 'doj')
                            query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('doj')
                            query3 = EmployeeAcademic.objects.filter(emp_id=emp_id1).values('pass_year_10','pass_year_12','pass_year_dip','pass_year_ug','pass_year_pg','date_doctrate','pass_year_other')
                            total_exp = get_total_experience(emp_id1)
                            highest_qual = get_highest_qualification(emp_id1)
                            query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                            query0_desg = list(query0)
                            desgn = query0_desg[0]['value']
                            qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                            qry1_ladd = list(qry1)
                            ladder = qry1_ladd[0]['value']
                            qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                            qry2_dept = list(qry2)
                            dept = qry2_dept[0]['value']
                            gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id1).exclude(Status="DELETE").values('Value')
                            gross_salary_total = float()
                            for x in gross_salary:
                                gross_salary_total += x['Value']
                            gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
                            session=getCurrentSession()
                            data_values.append(gross_inc_per(emp_id1,dep))
                            qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                            scale_consolidates=qry_gross_value[0]['salary_type__value']
                            # part 2
                            query_increment_type = AarDropdown.objects.filter(field = 'INCREMENT TYPE').exclude(value = None).values('value','sno')
                            increment_type = list()
                            increment = list(query_increment_type)
                            query_desg_drop = EmployeeDropdown.objects.filter(field = 'DESIGNATION').exclude(value = None).values('value','sno')
                            desg_drop = list()
                            desg_dropdown = list(query_desg_drop)
                            query4 = AarDropdown.objects.filter(field='EVALUATION CRITERIA').exclude(value=None).values('value', 'sno')
                            eva_crit_sno_list = list()
                            eval_cri = list(query4)
                            crit = list()
                            res_data = []
                            j=0
                            for x in eval_cri:
                                eva_arr = []
                                marks_arr=[]
                                eva_cri_query = AarDropdown.objects.filter(pid=x['sno']).exclude(value=None).values('value','sno')
                                eva_cris_list=list(eva_cri_query)
                                for i in eva_cris_list:
                                    eva_arr.append(i['value'])
                                max_marks_query = AarEvalutionCriteriaMaxMarks.objects.filter(type='A').values('max_marks', 'evalution_criteria')
                                max_marks_list=list(max_marks_query)
                                for i in max_marks_list:
                                    marks_arr.append(i['max_marks'])
                                res_data.append({"_id":x['sno'],"field":x['value'],"values":eva_arr,"max_marks":marks_arr[j]})
                                j = j+1

                            q = list(query1)
                            q.append({"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual,"scale":scale_consolidates,"increment_type":increment,"desg_dropdown":desg_dropdown})
                            data_values.append({'total_gross':total_gross,'incr_per':incr_per,"data_value": "Success"})   
                            data_values.append("test")         
                            data_values.append(q)
                            data_values.append(res_data)
                            isFormFilled = get_isFormFilled(emp_id1)
                            data_values.append({"isFormFilled": already_filled})
                            status = 200
                            if(len(data)>1):
                                emp_marks = data[1];
                                if data[2]['remarks']!='':
                                    remarks = data[2]['remarks']
                                else:
                                    remarks = None

                                if data[2]['result']!='':
                                    if data[2]['result']=='promotion':
                                        status_q = 'PROMOTION'
                                        type = None
                                        amount = None
                                        increment_type = None
                                        promoted_to = EmployeeDropdown.objects.get(sno = data[2]['promoted_to'])
                                        if data[2]['with_increment'] == 'Y':
                                            increment = data[2]['with_increment']
                                            promotion_amount = data[2]['with_amount']
                                        elif data[2]['with_increment'] == 'N':
                                            increment = data[2]['with_increment']
                                            promotion_amount = None
                                    elif data[2]['result']=='increment':
                                        status_q = 'INCREMENT'
                                        promoted_to = None
                                        promotion_amount = None
                                        increment = None
                                        type = data[2]['type']
                                        increment_type = AarDropdown.objects.get(sno = data[2]['increment_type'])
                                        if data[2]['amount'] != '':
                                            amount = data[2]['amount']
                                        else:
                                            amount = None
                                    elif data[2]['result'] == 'None':
                                        status_q = 'NO INCRREMENT'
                                        type = None
                                        amount = None
                                        increment_type = None
                                        promoted_to = None
                                        promotion_amount = None
                                        increment = None
                                if AarPart2Marks.objects.filter(emp_id = emp_id1).values('emp_id').count() > 0:
                                    status = 409
                                    msg = "duplicate emtry"
                                else:
                                    hodrecommendatedamount.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id = emp_id1),type=type,amount=amount,increment_type=increment_type,increment=increment,promotion_amount=promotion_amount,promoted_to=promoted_to,status=status).order_by('-id')[:1]
                                    id = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('id')
                                    h = list(id)
                                    for x in emp_marks:
                                        AarPart2Marks.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id = emp_id1),evalution_criteria=AarDropdown.objects.get(sno=x['id']),marks=x['marks'],remarks1=data[2]['remarks'],time_stamp=str(datetime.datetime.now()),employee_band='S',H_Id = h[0]['id'])
                                        msg = "success"
                                        status = 200
                        else:
                            data_values = {"msg": "no permission"}
                    #else:
                    #    data_values = {"msg": "Your Form Already Filled"}
                    status = 200
                    
                elif (request.method == 'GET'):
                    data_values = list()
                    if request.GET['request_type'] == "employee_info":
                        time=datetime.datetime.now()
                        qry_check=LockingUnlocking.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),toDate__gte=time,status="INSERT").order_by('-id')[:1].values('fromDate','toDate')
                        if len(qry_check)==0:
                            locked=True
                        else:
                            locked=False
                        q1=AarReporting.objects.filter(department=dept_hod,reporting_to=desg,reporting_no = '1').values('emp_id','emp_id__ladder')
                        data=[]
                        for q in q1:
                            ladd = q['emp_id__ladder']
                            if(ladd==661 or ladd==662 or ladd==663):
                                employees_list_query = EmployeePrimdetail.objects.filter(emp_id=q['emp_id']).values('name','emp_status')
                                if employees_list_query[0]['emp_status']=='ACTIVE':
                                    data.append({'name':employees_list_query[0]['name'],'EmpId':q['emp_id']})
                        data_values={'data':data,'locked':locked}
                        status = 200
                else:
                    data_values = {"msg":"no permission."}
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def staff_sdir(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                emp_id = request.session['hash1']
                # ques_ans = []
                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg')
                desgn_sno = list(desg_sno)
                desg = desgn_sno[0]['desg']
                if(desg==812):
                    employees_list_query = AarPart2Marks.objects.filter(employee_band='S').values('emp_id','emp_id__name','emp_id__ladder__value').distinct()
                    output = []
                    for x in employees_list_query:
                        if x not in output:
                            output.append(x)
                    employees_list = list(output)
                    data_values = list(output)

                    if request.method=="GET":
                        if 'request_type' in request.GET:
                            if request.GET['request_type']=='dept_emp':
                                employees_list_query = AarPart2Marks.objects.filter(employee_band='S',emp_id__dept=request.GET['dept']).values('emp_id','emp_id__name','emp_id__ladder__value').distinct()
                        emp_list = []
                        for x in employees_list_query:
                             emp_list.append(x['emp_id'])
                        query_emp_entries_st = (hodrecommendatedamount.objects.filter(emp_id__in = emp_list).values_list('emp_id', flat=True))
                        query_emp_entries_st2 = AarPart2MarksDir.objects.filter(emp_id__in = emp_list).values_list('emp_id', flat=True)
                        output = []
                        for x in employees_list_query:
                            if x not in output:
                                if x['emp_id'] in list(query_emp_entries_st):
                                    x['hod_status'] = "Completed"
                                else:
                                    x['hod_status'] = "Pending"

                                if x['emp_id'] in list(query_emp_entries_st2):
                                    x['admin_status'] = "Completed"
                                else:
                                    x['admin_status'] = "Pending"
                                #print(x)
                                output.append(x)
                            employees_list = list(output)
                            data_values = list(output)

                    if (request.method == 'POST'):
                        data_values = list()
                        status = 200
                        data = json.loads(request.body.decode("utf-8"))
                        if(data!=None):
                            emp_id1 = data[0]['emp_id']
                            ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder','ladder__value')
                            lad_sno = list(ladder_sno)
                            ladd = lad_sno[0]['ladder']
                            ladder_value = lad_sno[0]['ladder__value']
                            ##print ladder_value
                            if(ladd==661 or ladd==662 or ladd==663):
                                # part 1
                                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg')
                                desgn_sno = list(desg_sno)
                                desg = desgn_sno[0]['desg']
                                ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                                lad_sno = list(ladder_sno)
                                ladd = lad_sno[0]['ladder']
                                dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('dept')
                                dep_sno = list(dept_no)
                                dep = dep_sno[0]['dept']
                                query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('name', 'doj','emp_category')
                                query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('doj')
                                total_exp = get_total_experience(emp_id1)
                                highest_qual = get_highest_qualification(emp_id1)
                                query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                                query0_desg = list(query0)
                                desgn = query0_desg[0]['value']
                                qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                                qry1_ladd = list(qry1)
                                ladder = qry1_ladd[0]['value']
                                qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                                qry2_dept = list(qry2)
                                dept = qry2_dept[0]['value']
                                gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id1).exclude(Status='DELETE').values('Value')
                                gross_salary_total = float()
                                for x in gross_salary:
                                    gross_salary_total += x['Value']
                                gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
                                session=getCurrentSession()
                                qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                                scale_consolidates=qry_gross_value[0]['salary_type__value']
                                test = AarIncrementSettings.objects.filter(desg=desg,ladder=ladd).values('value','value_type')
                                a= list(test)[0]['value']
                                if scale_consolidates == 'CONSOLIDATE':
                                    salary = ((gross_salary_total * a) /100)
                                    alary
                                elif scale_consolidates == 'GRADE':
                                    salary = ((gross_salary_total * a) /100)
                                proposed_salary = gross_salary_total + salary
                                # part 2
                                query_increment_type = AarDropdown.objects.filter(field = 'INCREMENT TYPE').exclude(value = None).values('value','sno')
                                increment_type1 = list()
                                increment = list(query_increment_type)
                                qry4 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('amount')
                                qry4_amount = list(qry4)
                                amount = qry4_amount[0]['amount']
                                qry5 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('type')
                                qry5_type = list(qry5)
                                type = qry5_type[0]['type']
                                qry6 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('increment_type')
                                qry6_increment_type = list(qry6)
                                increment_type = qry6_increment_type[0]['increment_type']
                                qry7 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('status')
                                qry7_status = list(qry7)
                                qry_status = qry7_status[0]['status']
                                qry8 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('promoted_to')
                                qry8_type = list(qry8)
                                promoted_to = qry8_type[0]['promoted_to']
                                qry9 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('increment')
                                qry9_type = list(qry9)
                                increment_a = qry9_type[0]['increment']
                                qry10 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('promotion_amount')
                                qry10_type = list(qry10)
                                promotion_amount = qry10_type[0]['promotion_amount']
                                query4 = AarDropdown.objects.filter(field='EVALUATION CRITERIA').exclude(value=None).values('value', 'sno')
                                eva_crit_sno_list = list()
                                eval_cri = list(query4)
                                crit = list()
                                res_data = []
                                j=0
                                for x in eval_cri:
                                    eva_arr = []
                                    eva_sno = []
                                    marks=[]
                                    marks_arr=[]
                                    eva_cri_query = AarDropdown.objects.filter(pid=x['sno']).exclude(value=None).values('value','sno')
                                    eva_cris_list=list(eva_cri_query)
                                    for i in eva_cris_list:
                                        eva_arr.append(i['value'])
                                    max_marks_query = AarEvalutionCriteriaMaxMarks.objects.filter(type='A').values('max_marks', 'evalution_criteria')
                                    max_marks_list=list(max_marks_query)
                                    query5 = AarPart2Marks.objects.filter(emp_id=emp_id1).values('marks','evalution_criteria')
                                    marks_list = list(query5)
                                    for i in max_marks_list:
                                        for y in marks_list:
                                            if(i['evalution_criteria']==y['evalution_criteria']):
                                                marks_arr.append(i['max_marks'])
                                                marks.append(y['marks'])
                                    res_data.append({"_id":x['sno'],"field":x['value'],"values":eva_arr,"max_marks":marks_arr[j],"marks":marks[j]})
                                    j = j+1
                                q = list(query1)
                                #Part 3
                                query_desg_drop = EmployeeDropdown.objects.filter(field = 'DESIGNATION').exclude(value = None).values('value','sno')
                                desg_drop = list()
                                desg_dropdown = list(query_desg_drop)

                                q.append({"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual, "amount":amount, "type":type, "increment_type": increment_type, "status":qry_status, "increment":increment,"desg_dropdown":desg_dropdown, "promoted_to":promoted_to, "increment_a":increment_a, "promotion_amount":promotion_amount,"proposed_salary":proposed_salary, "salary":salary})
                                data_values.append({"data_value": "Success"})
                                data_values.append(q)
                                data_values.append(res_data)
                                isFormFilled = isDirFormFilled(emp_id1)
                                data_values.append({"isFormFilled":isFormFilled})
                                if isFormFilled:
                                    q_dir_data = AarPart2MarksDir.objects.filter(emp_id=emp_id1).values('type','increment_type','status','remarks','increment','promoted_to','promotion_amount','amount')
                                    data_values.append(q_dir_data[0])
                                #print(data)

                                status_q=None
                                type=None
                                increment_type=None
                                remarks=None
                                amount=None
                                promotion_amount=None
                                promoted_to=None
                                increment=None

                                if(len(data)>1):
                                    emp_marks = data[1];
                                    if data[2]['remarks']!='':
                                        remarks = data[2]['remarks']
                                    else:
                                        remarks = None
                                    if data[2]['result']!='':
                                        ##print data
                                        if data[2]['result']=='PROMOTION':
                                            status_q = 'PROMOTION'
                                            type = None
                                            amount = None
                                            increment_type = None
                                            promoted_to = EmployeeDropdown.objects.get(sno = data[2]['promoted_to'])
                                            if data[2]['with_increment'] == 'Y':
                                                increment = data[2]['with_increment']
                                                promotion_amount = data[2]['with_amount']
                                            elif data[2]['with_increment'] == 'N':
                                                increment = data[2]['with_increment']
                                                promotion_amount = None
                                        elif data[2]['result']=='INCREMENT':
                                            status_q = 'INCREMENT'
                                            promoted_to = None
                                            promotion_amount = None
                                            increment = None
                                            type = data[2]['type']
                                            increment_type = AarDropdown.objects.get(sno = data[2]['increment_type'])
                                            if data[2]['amount'] != '':
                                                amount = data[2]['amount']
                                            else:
                                                amount = None
                                        elif data[2]['result']=='None':
                                            status_q = 'NO INCREMENT'
                                            promoted_to = None
                                            promotion_amount = None
                                            increment = None
                                            type = None
                                            increment_type = None
                                            amount = None
                                        else:
                                            status_q = 'NO INCREMENT'
                                            promoted_to = None
                                            promotion_amount = None
                                            increment = None
                                            type = None
                                            increment_type = None
                                            amount = None
                                    AarPart2MarksDir.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id = emp_id1),defaults={'type':type,'increment':increment,'status':status_q,'amount':amount,'remarks':remarks,'increment_type':increment_type,'promoted_to':promoted_to,'promotion_amount':promotion_amount})

                            else:
                                data_values = {"msg": "no permission"}
                        else:
                            data_values = {"data_value": "Failure"}

                    elif (request.method == 'GET'):
                        status = 200
                else:
                    data_values = {"msg":"no permission."}
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def staff_a(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                emp_id = request.session['hash1']
                ##print emp_id
                ques_query = AarDropdown.objects.filter(field='STAFF ASSISTANT PART-2 QUESTION').exclude(value=None).values('value','sno')
                question = []
                ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('ladder')
                lad_sno = list(ladder_sno)
                ladd = lad_sno[0]['ladder']
                data_values = list()
                if(ladd==591 or ladd==592 or ladd==593 or ladd==659 or ladd==658 or ladd==660):
                    if (request.method == 'POST'):
                        status = 200
                        answerdb = AarPart2QuesAns.objects.filter(emp_id=emp_id).exclude(answer=None).values('answer')
                        data = json.loads(request.body.decode("utf-8"))
                        
                        if(data!=""):
                            if AarPart2QuesAns.objects.filter(emp_id = emp_id).values('emp_id').count() > 0:
                                status = 409
                                msg = "duplicate emtry"
                            else:
                                for x in data:
                                    q = AarPart2QuesAns.objects.update_or_create(time_stamp=str(datetime.datetime.now()),emp_id = EmployeePrimdetail.objects.get(emp_id = emp_id),
                                        ques=AarDropdown.objects.get(sno=x['ques_id']),answer=x['answer'],employee_band="A")
                                    status = 200
                                data_values = {"data_value": "Success"}
                        else:
                            data_values = {"data_value": "Failure"}

                    elif (request.method == 'GET'):
                        time=datetime.datetime.now()
                        qry_check=LockingUnlocking.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),toDate__gte=time,status="INSERT").order_by('-id')[:1].values('fromDate','toDate')
                        if len(qry_check)==0:
                            locked=True
                        else:
                            locked=False

                        # part 2
                        for x in ques_query:
                            question.append({"question":x['value'], "ques_id":x['sno']})

                        # part 1
                        desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg')
                        desgn_sno = list(desg_sno)
                        desg = desgn_sno[0]['desg']
                        ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('ladder')
                        lad_sno = list(ladder_sno)
                        ladd = lad_sno[0]['ladder']
                        dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                        dep_sno = list(dept_no)
                        dep = dep_sno[0]['dept']
                        query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('name', 'doj')
                        query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')
                        total_exp = get_total_experience(emp_id)
                        highest_qual = get_highest_qualification(emp_id)
                        query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                        query0_desg = list(query0)
                        desgn = query0_desg[0]['value']
                        qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                        qry1_ladd = list(qry1)
                        ladder = qry1_ladd[0]['value']
                        qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                        qry2_dept = list(qry2)
                        dept = qry2_dept[0]['value']
                        gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id).exclude(Status='DELETE').values('Value')
                        gross_salary_total = float()
                        for x in gross_salary:
                            gross_salary_total += x['Value']

                        q = list(query1)
                        q.append({"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual,'locked':locked})
                        data_values.append(q)
                        data_values.append(question)
                        isFormFilled = get_isFormFilled(emp_id)
                        data_values.append({"isFormFilled": isFormFilled})
                        status = 200
                else:
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def staff_ahod(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                emp_id = request.session['hash1']
                ques_ans = []
                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg','dept')
                desgn_sno = list(desg_sno)
                desg = desgn_sno[0]['desg']
                dept_hod = desgn_sno[0]['dept']
                if (request.method == 'GET'):

                    time=datetime.datetime.now()
                    qry_check=LockingUnlocking.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),toDate__gte=time,status="INSERT").order_by('-id')[:1].values('fromDate','toDate')
                    if len(qry_check)==0:
                        locked=True
                    else:
                        locked=False
                    q1=AarReporting.objects.filter(department=dept_hod,reporting_to=desg,reporting_no = '1').values('emp_id','emp_id__ladder')
                    ##print q1
                    data =[]
                    for q in q1:
                        ladd = q['emp_id__ladder']
                        if(ladd==591 or ladd==592 or ladd==593 or ladd==659 or ladd==658 or ladd==660):
                            emp_filled=AarPart2QuesAns.objects.filter(emp_id=q['emp_id']).values()
                            if emp_filled.count()>0:
                                emp_info=EmployeePrimdetail.objects.filter(emp_id=q['emp_id']).values('name','emp_status')
                                if emp_info[0]['emp_status']=='ACTIVE':
                                    data.append({'name':emp_info[0]['name'],'EmpId':q['emp_id']})
                    data_values={'data':data,'locked':locked}
                    status = 200


                elif (request.method == 'POST'):
                    data_values = list()
                    status = 200
                    data = json.loads(request.body.decode("utf-8"))
                    if(data!=None):
                        emp_id1 = data[0]['emp_id']
                        
                        ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg','ladder','dept','doj','name','cadre','emp_category')
                        lad_sno = list(ladder_sno)
                        ladd = lad_sno[0]['ladder']
                        desg=lad_sno[0]['desg']
                        ladder=lad_sno[0]['ladder']
                        dept=lad_sno[0]['dept']
                        emp_category=lad_sno[0]['emp_category']
                        doj=lad_sno[0]['doj']
                        name=lad_sno[0]['name']
                        cadre=lad_sno[0]['cadre']
                        
                        if(ladd==591 or ladd==592 or ladd==593 or ladd==659 or ladd==658 or ladd==660):
                            month=date.today().month-2
                            if month==0:
                                month=12
                            gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
                            session=getCurrentSession()
                            q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value','salary_type')
                            scale_consolidated=q7[0]['salary_type__value']

                            q_increment_per = AarIncrementSettings.objects.filter(desg=desg,ladder=ladder,emp_category=emp_category,cadre=cadre,salary_type=q7[0]['salary_type']).exclude(status='DELETE').values('value')

                            incr_per=0
                            if len(q_increment_per)>0:
                                incr_per=q_increment_per[0]['value']
                            if  scale_consolidated == 'GRADE':
                                total_gross=0
                                for gd in gross_data:
                                    if gd['value'] == 'BASIC' or gd['value'] =='AGP':
                                        total_gross=total_gross+gd['gross_value']
                            else:
                                total_gross=0
                                for gd in gross_data:
                                    total_gross=total_gross+gd['gross_value']
                            result={'scale_consolidated':scale_consolidated,'total_gross':total_gross,'incr_per':incr_per,"data_value": "Success"}
                            data_values.append(result)
                            data_values.append("test")
                            query_increment_type = AarDropdown.objects.filter(field = 'INCREMENT TYPE').exclude(value = None).values('value','sno')
                            increment_type1 = list()
                            increment = list(query_increment_type)
                            ques_query = AarDropdown.objects.filter(field='STAFF ASSISTANT PART-2 QUESTION').exclude(value=None).values('value','sno')
                            ans_query = AarPart2QuesAns.objects.filter(emp_id=emp_id1).exclude(answer=None).values('answer','ques')
                            for x in ques_query:
                                for y in ans_query:
                                    if(x['sno']==y['ques']):
                                        ques_ans.append({"question":x['value'], "ques_id":x['sno'], "answer":y['answer']})
                            # part 1
                            desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg')
                            desgn_sno = list(desg_sno)
                            desg = desgn_sno[0]['desg']
                            ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                            lad_sno = list(ladder_sno)
                            ladd = lad_sno[0]['ladder']
                            dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('dept')
                            dep_sno = list(dept_no)
                            dep = dep_sno[0]['dept']
                            query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('name', 'doj')
                            query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('doj')
                            total_exp = get_total_experience(emp_id1)
                            highest_qual = get_highest_qualification(emp_id1)
                            query_desg_drop = EmployeeDropdown.objects.filter(field = 'DESIGNATION').exclude(value = None).values('value','sno')
                            desg_drop = list()
                            desg_dropdown = list(query_desg_drop)
                            query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                            query0_desg = list(query0)
                            desgn = query0_desg[0]['value']
                            qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                            qry1_ladd = list(qry1)
                            ladder = qry1_ladd[0]['value']
                            qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                            qry2_dept = list(qry2)
                            dept = qry2_dept[0]['value']
                            gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id1).exclude(Status='DELETE').values('Value')
                            gross_salary_total = float()
                            for x in gross_salary:
                                gross_salary_total += x['Value']

                            # part 3
                            query4 = AarDropdown.objects.filter(field='EVALUATION CRITERIA').exclude(value=None).values('value', 'sno')
                            eva_crit_sno_list = list()
                            eval_cri = list(query4)
                            crit = list()
                            res_data = []
                            j=0
                            for x in eval_cri:
                                eva_arr = []
                                marks_arr=[]
                                eva_cri_query = AarDropdown.objects.filter(pid=x['sno']).exclude(value=None).values('value','sno')
                                eva_cris_list=list(eva_cri_query)
                                for i in eva_cris_list:
                                    eva_arr.append(i['value'])
                                max_marks_query = AarEvalutionCriteriaMaxMarks.objects.filter(type='A').values('max_marks', 'evalution_criteria')
                                max_marks_list=list(max_marks_query)
                                for i in max_marks_list:
                                    marks_arr.append(i['max_marks'])
                                res_data.append({"_id":x['sno'],"field":x['value'],"values":eva_arr,"max_marks":marks_arr[j]})
                                j = j+1

                            q = list(query1)
                            q.append({"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual, "increment":increment,"desg_dropdown":desg_dropdown})
                            #data_values.append({"data_value": "Success"})
                            data_values.append(q)
                            data_values.append(ques_ans)
                            data_values.append(res_data)
                            isFormFilled = isHODFormFilled(emp_id1)
                            data_values.append({"isFormFilled": isFormFilled})
                            
                            if(len(data)>1):
                                emp_marks = data[1];
                                if data[2]['remarks']!='':
                                    remarks = data[2]['remarks']
                                else:
                                    remarks = None

                                if data[2]['result']!='':
                                    if data[2]['result']=='promotion':
                                        status_q = 'PROMOTION'
                                        type = None
                                        amount = None
                                        increment_type = None
                                        promoted_to = EmployeeDropdown.objects.get(sno = data[2]['promoted_to'])
                                        if data[2]['with_increment'] == 'Y':
                                            increment = data[2]['with_increment']
                                            promotion_amount = data[2]['with_amount']
                                        elif data[2]['with_increment'] == 'N':
                                            increment = data[2]['with_increment']
                                            promotion_amount = None
                                    elif data[2]['result']=='increment':
                                        status_q = 'INCREMENT'
                                        promoted_to = None
                                        promotion_amount = None
                                        increment = None
                                        type = data[2]['type']
                                        increment_type = AarDropdown.objects.get(sno = data[2]['increment_type'])
                                        if data[2]['amount'] != '':
                                            amount = data[2]['amount']
                                        else:
                                            amount = None
                                    elif data[2]['result'] == 'None':
                                        status_q = 'NO INCRREMENT'
                                        type = None
                                        amount = None
                                        increment_type = None
                                        promoted_to = None
                                        promotion_amount = None
                                        increment = None
                                m = {'type':type,'amount':amount,'increment_type':increment_type,'increment':increment,'promotion_amount':promotion_amount,'promoted_to':promoted_to,'status':status_q}
                                hodrecommendatedamount.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id = emp_id1),defaults=m)
                                # hodrecommendatedamount.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id = emp_id1),type=type,amount=amount,increment_type=increment_type,increment=increment,promotion_amount=promotion_amount,promoted_to=promoted_to,status=status_q)
                                id = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('id')
                                h = list(id)
                                emp_marks = data[1];
                                for x in emp_marks:
                                    
                                    d = {'marks':x['marks'],'remarks1':data[2]['remarks'],'employee_band':'A','H_Id': h[0]['id']}
                                    AarPart2Marks.objects.update_or_create(evalution_criteria=AarDropdown.objects.get(sno=x['id']),emp_id=EmployeePrimdetail.objects.get(emp_id = emp_id1),defaults=d)
                        else:
                            data_values = {"msg": "no permission"}
                    else:
                        data_values = {"data_value": "Failure"}


                else:
                    data_values = {"msg":"no permission."}
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)


def staff_adir(request):
    data_values = list()
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                emp_id = request.session['hash1']
                ques_ans = []
                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg')
                desgn_sno = list(desg_sno)
                desg = desgn_sno[0]['desg']
                if(desg==812):
                    
                    employees_list_query = AarPart2Marks.objects.filter(employee_band='A').values('emp_id','emp_id__name','emp_id__ladder__value').distinct()
                    output = []
                    for x in employees_list_query:
                        if x not in output:
                            output.append(x)
                    employees_list = list(output)
                    data_values = list(output)

                    if request.method=="GET":
                        if 'request_type' in request.GET:
                            if request.GET['request_type']=='dept_emp':
                                employees_list_query = AarPart2Marks.objects.filter(employee_band='A',emp_id__dept=request.GET['dept']).values('emp_id','emp_id__name','emp_id__ladder__value').distinct()
                        emp_list = []
                        for x in employees_list_query:
                             emp_list.append(x['emp_id'])
                        #print(emp_list)
                        query_emp_entries_st = (hodrecommendatedamount.objects.filter(emp_id__in = emp_list).values_list('emp_id', flat=True))
                        query_emp_entries_st2 = AarPart2MarksDir.objects.filter(emp_id__in = emp_list).values_list('emp_id', flat=True)
                        output = []
                        for x in employees_list_query:
                            if x not in output:
                                if x['emp_id'] in list(query_emp_entries_st):
                                    x['hod_status'] = "Completed"
                                else:
                                    x['hod_status'] = "Pending"

                                if x['emp_id'] in list(query_emp_entries_st2):
                                    x['admin_status'] = "Completed"
                                else:
                                    x['admin_status'] = "Pending"
                                #print(x)
                                output.append(x)
                            employees_list = list(output)
                            data_values = list(output)

                    if (request.method == 'POST'):
                        data_values = list()
                        status = 200
                        data = json.loads(request.body.decode("utf-8"))
                        print(data)
                        if(data!=None):
                            
                            emp_id1 = data[0]['emp_id']
                            ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                            ##print(list(ladder_sno))
                            ladd = ladder_sno[0]['ladder']
                            if(ladd==591 or ladd==592 or ladd==593 or ladd==658 or ladd==659 or ladd==660):
                                # part 2
                                ques_query = AarDropdown.objects.filter(field='STAFF ASSISTANT PART-2 QUESTION').exclude(value=None).values('value','sno')
                                ans_query = AarPart2QuesAns.objects.filter(emp_id=emp_id1).exclude(answer=None).values('answer','ques')
                                for x in ques_query:
                                    for y in ans_query:
                                        if(x['sno']==y['ques']):
                                            ques_ans.append({"question":x['value'], "ques_id":x['sno'], "answer":y['answer']})
                                # part 1
                                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg')
                                desgn_sno = list(desg_sno)
                                desg = desgn_sno[0]['desg']
                                ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                                lad_sno = list(ladder_sno)
                                ladd = lad_sno[0]['ladder']
                                dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('dept')
                                dep_sno = list(dept_no)
                                dep = dep_sno[0]['dept']
                                query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('name', 'doj')
                                query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('doj')
                                total_exp = get_total_experience(emp_id1)
                                highest_qual = get_highest_qualification(emp_id1)
                                query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                                query0_desg = list(query0)
                                desgn = query0_desg[0]['value']
                                qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                                qry1_ladd = list(qry1)
                                ladder = qry1_ladd[0]['value']
                                qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                                qry2_dept = list(qry2)
                                dept = qry2_dept[0]['value']
                                gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id1).exclude(Status='DELETE').values('Value')
                                gross_salary_total = float()
                                for x in gross_salary:
                                    gross_salary_total += x['Value']
                                gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
                                session=getCurrentSession()
                                qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                                scale_consolidates=qry_gross_value[0]['salary_type__value']
                                cale_consolidates
                                test = AarIncrementSettings.objects.filter(desg=desg,ladder=ladd).values('value','value_type')
                                a= list(test)[0]['value']
                                if scale_consolidates == 'CONSOLIDATE':
                                    salary = ((gross_salary_total * a) /100)
                                    alary
                                elif scale_consolidates == 'GRADE':
                                    salary = ((gross_salary_total * a) /100)
                                proposed_salary = gross_salary_total + salary
                                ##print proposed_salary
                                # part 3
                                query_increment_type = AarDropdown.objects.filter(field = 'INCREMENT TYPE').exclude(value = None).values('value','sno')
                                increment_type1 = list()
                                increment = list(query_increment_type)
                                qry4 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('amount','promoted_to')
                                qry4_amount = list(qry4)
                                promoted_to=qry4_amount[0]['promoted_to']
                                amount = qry4_amount[0]['amount']
                                qry5 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('type')
                                qry5_type = list(qry5)
                                type = qry5_type[0]['type']
                                qry6 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('increment_type')
                                qry6_increment_type = list(qry6)
                                increment_type = qry6_increment_type[0]['increment_type']
                                qry7 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('status')
                                qry7_status = list(qry7)
                                qry_status = qry7_status[0]['status']
                                query4 = AarDropdown.objects.filter(field='EVALUATION CRITERIA').exclude(value=None).values('value', 'sno')
                                eva_crit_sno_list = list()
                                eval_cri = list(query4)
                                crit = list()
                                res_data = []
                                j=0
                                for x in eval_cri:
                                    eva_arr = []
                                    eva_sno = []
                                    marks=[]
                                    marks_arr=[]
                                    eva_cri_query = AarDropdown.objects.filter(pid=x['sno']).exclude(value=None).values('value','sno')
                                    eva_cris_list=list(eva_cri_query)
                                    for i in eva_cris_list:
                                        eva_arr.append(i['value'])
                                    max_marks_query = AarEvalutionCriteriaMaxMarks.objects.filter(type='A').values('max_marks', 'evalution_criteria')
                                    max_marks_list=list(max_marks_query)
                                    query5 = AarPart2Marks.objects.filter(emp_id=emp_id1).values('marks','evalution_criteria')
                                    marks_list = list(query5)
                                    for i in max_marks_list:
                                        for y in marks_list:
                                            if(i['evalution_criteria']==y['evalution_criteria']):
                                                marks_arr.append(i['max_marks'])
                                                marks.append(y['marks'])
                                    res_data.append({"_id":x['sno'],"field":x['value'],"values":eva_arr,"max_marks":marks_arr[j],"marks":marks[j]})
                                    j = j+1
                                q = list(query1)
                                query_desg_drop = EmployeeDropdown.objects.filter(field = 'DESIGNATION').exclude(value = None).values('value','sno')
                                desg_drop = list()
                                desg_dropdown = list(query_desg_drop)
                                q.append({"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual, "amount":amount, "type":type, "increment_type": increment_type, "status":qry_status, "increment":increment,"proposed_salary":proposed_salary, "salary":salary,"desg_dropdown":desg_dropdown,'promoted_to':promoted_to})
                                data_values.append({"data_value": "Success"})
                                data_values.append(q)
                                data_values.append(ques_ans)
                                data_values.append(res_data)
                                isFormFilled = isDirFormFilled(emp_id1)
                                data_values.append({"isFormFilled":isFormFilled})
                                if isFormFilled:
                                    q_dir_data = AarPart2MarksDir.objects.filter(emp_id=emp_id1).values('type','increment_type','status','remarks','increment','promoted_to','promotion_amount','amount')
                                    data_values.append(q_dir_data[0])
                                
                                promotion_amount=None
                                increment_type=None
                                amount=None
                                status_q=None
                                remarks=None
                                promoted_to=None

                                if(len(data)>1):
                                    if data[2]['remarks']!='':
                                        remarks = data[2]['remarks']
                                    else:
                                        remarks = None
                                    if data[1]['result']!='':
                                        if data[1]['result']=='PROMOTION':
                                            status_q = 'PROMOTION'
                                            promoted_to = EmployeeDropdown.objects.get(sno = data[2]['promotion_to'])
                                            type = None
                                            amount = None
                                            if data[2]['promotion_amount'] != '':
                                                promotion_amount = data[2]['promotion_amount']
                                            else:
                                                promotion_amount = None

                                        elif data[1]['result']=='INCREMENT':
                                            status_q = 'INCREMENT'
                                            amount = data[2]['amount']
                                            promotion_amount = None
                                            promoted_to = None
                                        elif data[1]['result']=='NO INCREMENT':
                                            status_q = 'NO INCREMENT'
                                            amount = None

                                            promotion_amount = None
                                            promoted_to = None
                                    if data[2]['increment_type']!='':
                                        increment_type=AarDropdown.objects.get(sno = data[2]['increment_type'])
                                        status_q = 'INCREMENT'
                                    else:
                                        increment_type=None

                                    if data[2]['type'] !='':
                                        type= data[2]['type']
                                    else:
                                        type=None
                                    AarPart2MarksDir.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id = emp_id1),defaults={'type':type,'amount':amount,'increment_type':increment_type,'status':status_q,'remarks':remarks,'promoted_to':promoted_to,'promotion_amount':promotion_amount})
                            else:
                                data_values = {"msg": "no permission"}
                        else:
                            data_values = {"data_value": "Failure"}

                    elif (request.method == 'GET'):
                        ##print("hello")
                        status = 200
                else:
                    data_values = {"msg":"no permission."}
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def staff_emg(request):
    data=[]
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:
                if request.method=='GET':

                    time=datetime.datetime.now()
                    qry_check=LockingUnlocking.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),toDate__gte=time,status="INSERT").order_by('-id')[:1].values('fromDate','toDate')
                    if len(qry_check)==0:
                        locked=True
                    else:
                        locked=False
                    status=200
                    emp_id=request.session['hash1']
                    isFormFilled = get_isFormFilled(emp_id)
                    q1=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg','ladder','dept','doj','name','cadre')
                    desg=q1[0]['desg']
                    ladder=q1[0]['ladder']
                    dept=q1[0]['dept']
                    doj=q1[0]['doj']
                    name=q1[0]['name']
                    cadre=q1[0]['cadre']
                    if cadre==667 or cadre==668 or cadre==669 or cadre==645 or cadre==644 or cadre==643:
                        total_exp = get_total_experience(emp_id)
                        highest_qual = get_highest_qualification(emp_id)
                        q4=EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                        desg_value=q4[0]['value']
                        q5=EmployeeDropdown.objects.filter(sno=ladder).exclude(value=None).values('value')
                        ladder_value=q5[0]['value']
                        q6=EmployeeDropdown.objects.filter(sno=dept).exclude(value=None).values('value')
                        dept_value=q6[0]['value']
                        q7=EmployeeDropdown.objects.filter(sno=cadre).exclude(value=None).values('value')
                        cadre_value=q7[0]['value']

                        month=date.today().month-2
                        if month==0:
                            month=12
                        gross_data=stored_gross_payable_salary_components(emp_id,getCurrentSession(),date.today().month-3)
                        total_gross=0
                        for gd in gross_data:
                            total_gross=total_gross+gd['gross_value']

                        session=getCurrentSession()
                        q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                        scale_consolidated=q7[0]['salary_type__value']

                        questions=[313,320,322,355]
                        ques_list=[]
                        d3=[]
                        for q in questions:
                            q8=AarDropdown.objects.filter(sno=q).values('sno','pid','field','value')
                            category=q8[0]['field']
                            q9=AarDropdown.objects.filter(field=category).exclude(value=None).values('sno','pid','field','value')
                            d2=[]
                            for q in q9:
                                q10=AarDropdown.objects.filter(field=q['value']).exclude(value=None).values('sno','pid','field','value')
                                d1=[]
                                max_list_id=[358,359,360,363,366,367,368,369,370]
                                for qr in q10:
                                    if qr['sno'] in max_list_id:
                                        q11=AarEvalutionCriteriaMaxMarks.objects.filter(evalution_criteria=qr['sno']).filter(type='E').values('max_marks')
                                        d1.append({'sub':qr['value'],'id':qr['sno'],'max':q11[0]['max_marks']})
                                    else:
                                        d1.append({'sub':qr['value'],'id':qr['sno']})

                                d2.append({'sub':q['value'],'id':q['sno'],'data':d1})
                            d3.append({'cat':category,'id':q8[0]['sno'],'data':d2})

                        data={"name":name,"dept":dept_value,"desg":desg_value,"doj":doj,"scale":scale_consolidated,"gross_salary":total_gross,"highest_qual":highest_qual,"total_exp":total_exp,"cadre":cadre_value,"questions":d3,"locked":locked,"ladder":ladder_value}
                    else:
                        status=401
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500

    return JsonResponse(data={'data':data,'isFormFilled': isFormFilled},status=status)

def staff_emg_submit(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:
                if request.method=='POST':
                    status=200
                    data=json.loads(request.body.decode("utf-8"))
                    ##print data
                    i=0
                    for d in data:
                        if i==1:
                            q_id=d['id']
                            if d['ans'] is not None:
                                for ans in d['ans']:
                                    if ans is not None:
                                        q1=AarPart2QuesAns.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),ques=AarDropdown.objects.get(sno=q_id),answer=d['ans'][ans],employee_band='M')
                            else:
                                q1=AarPart2QuesAns.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),ques=AarDropdown.objects.get(sno=q_id),defaults={'answer':"",'employee_band':'M'})

                        elif i==3:
                            for k in d:
                                q3=AarPart2Marks.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),evalution_criteria=AarDropdown.objects.get(sno=k['id']),defaults={'marks':k['ans'],'category':'E','employee_band':'M'})
                        else:
                            for k in d:
                                q2=AarPart2QuesAns.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),ques=AarDropdown.objects.get(sno=k['id']),defaults={'answer':k['ans'],'employee_band':'M'})
                        i+=1
                    msg="Success"

                else:
                    status=502
                    msg="An error occurred"
            else:
                status=403
                msg="An error occurred"
        else:
            status=401
            msg="An error occurred"
    else:
        status=500
        msg="An error occurred"
    result=[]
    result={'msg':msg}

    return JsonResponse(status=status,data=result)

def staff_emg_hod_dropdown(request):
    data=[]
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:
                if request.method=='GET':
                    ##print "aakash"
                    status=200
                    emp=request.session['hash1']
                    dept_desg=EmployeePrimdetail.objects.filter(emp_id=emp).values('dept','desg')
                    q1=AarReporting.objects.filter(department=dept_desg[0]['dept'],reporting_to=dept_desg[0]['desg'],reporting_no = '1').values('emp_id','emp_id__cadre')

                    data=[]
                    for q in q1:
                        cadre = q['emp_id__cadre']
                        if(cadre==667 or cadre==668 or cadre==669 or cadre==645 or cadre==644 or cadre==643):
                            emp_filled=AarPart2QuesAns.objects.filter(emp_id=q['emp_id']).values()
                            if emp_filled.count()>0:
                                emp_info=EmployeePrimdetail.objects.filter(emp_id=q['emp_id']).values('name','emp_status')
                                ##print emp_info
                                if emp_info[0]['emp_status']=='ACTIVE':
                                    data.append({'name':emp_info[0]['name'],'EmpId':q['emp_id']})

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500

    return JsonResponse(data=data,status=status,safe=False)

def staff_emg_details(request):
    d3=[]
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[425])
            if check==200:
                if request.method=='POST':
                    status=200
                    data=json.loads(request.body.decode("utf-8"))
                    empId=data['EmpId']

                    q1=EmployeePrimdetail.objects.filter(emp_id=empId).values('desg','ladder','dept','doj','name','cadre','emp_category')
                    desg=q1[0]['desg']
                    ladder=q1[0]['ladder']
                    dept=q1[0]['dept']
                    emp_category=q1[0]['emp_category']
                    doj=q1[0]['doj']
                    name=q1[0]['name']
                    cadre=q1[0]['cadre']

                    month=date.today().month-2
                    if month==0:
                        month=12
                    gross_data=stored_gross_payable_salary_components(empId,getCurrentSession(),date.today().month-3)
                    session=getCurrentSession()
                    q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=empId)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value','salary_type')
                    scale_consolidated=q7[0]['salary_type__value']

                    q_increment_per = AarIncrementSettings.objects.filter(desg=desg,ladder=ladder,emp_category=emp_category,cadre=cadre,salary_type=q7[0]['salary_type']).exclude(status='DELETE').values('value')

                    incr_per=0
                    if len(q_increment_per)>0:
                        incr_per=q_increment_per[0]['value']
                    if  scale_consolidated == 'GRADE':
                        total_gross=0
                        for gd in gross_data:
                            if gd['value'] == 'BASIC' or gd['value'] =='AGP':
                                total_gross=total_gross+gd['gross_value']
                    else:
                        total_gross=0
                        for gd in gross_data:
                            total_gross=total_gross+gd['gross_value']
                    ##print(scale_consolidated,total_gross,incr_per)

                    if cadre==667 or cadre==668 or cadre==669 or cadre==645 or cadre==644 or cadre==643:
                        total_exp = get_total_experience(empId)
                        highest_qual = get_highest_qualification(empId)
                        q4=EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                        desg_value=q4[0]['value']
                        q5=EmployeeDropdown.objects.filter(sno=ladder).exclude(value=None).values('value')
                        ladder_value=q5[0]['value']
                        q6=EmployeeDropdown.objects.filter(sno=dept).exclude(value=None).values('value')
                        dept_value=q6[0]['value']
                        q7=EmployeeDropdown.objects.filter(sno=cadre).exclude(value=None).values('value')
                        cadre_value=q7[0]['value']

                        month=date.today().month-2
                        if month==0:
                            month=12
                        gross_data=stored_gross_payable_salary_components(empId,getCurrentSession(),date.today().month-3)
                        total_gross=0
                        for gd in gross_data:
                            total_gross=total_gross+gd['gross_value']

                        session=getCurrentSession()
                        q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=empId)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                        scale_consolidated=q7[0]['salary_type__value']


                    questions=[313,320,322,355]
                    ques_list=[]

                    for qt in questions:
                        q8=AarDropdown.objects.filter(sno=qt).values('sno','pid','field','value')
                        category=q8[0]['field']
                        q9=AarDropdown.objects.filter(field=category).exclude(value=None).values('sno','pid','field','value')
                        d2=[]
                        for q in q9:
                            q10=AarDropdown.objects.filter(field=q['value']).exclude(value=None).values('sno','pid','field','value')
                            d1=[]
                            max_list_id=[358,359,360,363,366,367,368,369,370]
                            for qr in q10:
                                i_d=qr['sno']

                                if qr['sno'] in max_list_id:
                                    q11=AarEvalutionCriteriaMaxMarks.objects.filter(evalution_criteria=qr['sno']).filter(type='E').values('max_marks')
                                    answer=AarPart2Marks.objects.filter(emp_id=empId,evalution_criteria=i_d,category='E').values('marks')
                                    d1.append({'sub':qr['value'],'id':qr['sno'],'max':q11[0]['max_marks'],'answer':answer[0]['marks']})
                                else:
                                    answer=AarPart2QuesAns.objects.filter(ques=i_d,emp_id=empId).values('answer')
                                    d1.append({'sub':qr['value'],'id':qr['sno'],'answer':answer[0]['answer']})

                            answer2=AarPart2QuesAns.objects.filter(ques=q['sno'],emp_id=empId).values('answer')
                            if len(answer2)>0:
                                if q['sno']==321:
                                    act=[]
                                    for an2 in answer2:
                                        act.append({'v':an2['answer']})

                                    d2.append({'sub':q['value'],'id':q['sno'],'data':d1,'answer':act})
                                else:
                                    d2.append({'sub':q['value'],'id':q['sno'],'data':d1,'answer':answer2[0]['answer']})
                            else:
                                d2.append({'sub':q['value'],'id':q['sno'],'data':d1})

                        d3.append({'cat':category,'id':q8[0]['sno'],'data':d2})

                        q20=AarDropdown.objects.filter(field="INCREMENT TYPE").exclude(value=None).values('sno','field','value')
                        increment_types=[]
                        for x in q20:
                            increment_types.append({'sno':x['sno'],'value':x['value']})

                        query_desg_drop = EmployeeDropdown.objects.filter(field = 'DESIGNATION').exclude(value = None).values('value','sno')
                        desg_drop = list()
                        desg_dropdown = list(query_desg_drop)

                    data={"name":name,"dept":dept_value,"desg":desg_value,"doj":doj,"scale":scale_consolidated,"gross_salary":total_gross,"highest_qual":highest_qual,"total_exp":total_exp,"cadre":cadre_value,"data":d3,"increment":increment_types,"desg_dropdown":desg_dropdown,"ladder":ladder_value,'total_gross':total_gross,'incr_per':incr_per}
                    isFormFilled = isHODFormFilled(empId)
                else:
                    status=502
            else:
                    status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data={'result':data,"isFormFilled": isFormFilled},status=status,safe=False)

def staff_emg_hod_submit(request):
    if request.method=='POST':
        status=200
        amount=None
        data=json.loads(request.body.decode("utf-8"))
        ##print data[3]
        i=0
        if data[4] == None :
            status_q = 'NO INCREMENT'
            amount = None
            increment = None
            promotion_amount = None
            promoted_to = None
            type=None
            increment_type=None
        else:
            if data[3] == 'promotion':
                status_q = 'PROMOTION'
                type = None
                amount = None
                increment_type = None
                promoted_to = EmployeeDropdown.objects.get(sno = data[4]['promoted_to'])
                if data[4]['with_increment'] == 'Y':
                    increment = data[4]['with_increment']
                    promotion_amount = data[4]['with_amount']
                elif data[4]['with_increment'] == 'N':
                    increment = data[4]['with_increment']
                    promotion_amount = None
            elif data[3] == 'increment':
                status_q = 'INCREMENT'
                promoted_to = None
                promotion_amount = None
                increment = None

                
                type = data[4]['type']
                if data[4]['amount'] == 0:
                    amount = None
                elif data[4]['amount']!='':
                    amount = data[4]['amount']
                increment_type=AarDropdown.objects.get(sno = data[4]['increment_type'])

        q2=hodrecommendatedamount.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id=data[5]['EmpId']),type=type,amount=amount,increment_type=increment_type,increment=increment,promotion_amount=promotion_amount,promoted_to=promoted_to,status=status_q)
        id = hodrecommendatedamount.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=data[5]['EmpId'])).values('id')
        h = list(id)

        for d in data:
            if i==0:
                ##print (d[0],'hello')
                for p in d:
                    ##print()

                    q=AarPart2Marks.objects.create(employee_band='M',emp_id=EmployeePrimdetail.objects.get(emp_id=data[5]['EmpId']),evalution_criteria=AarDropdown.objects.get(sno=p['id']),marks=int(p['ans']),category='H',remarks1=data[1],remarks2=data[2],H_Id = h[0]['id'])
            i+=1
            msg="Success"
    else:
        status=502
        msg="Error"
    result={'msg':msg}
    return JsonResponse(data=result,status=status,safe=False)

def staff_emg_dir_dropdown(request):
    data=[]
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[425])
            if check==200:
                if request.method=='GET':
                    status=200
                    emp=request.session['hash1']
                    if 'request_type' in request.GET:
                        q1 = EmployeePrimdetail.objects.filter(cadre__in = [667,668,669,645,643,644],dept=request.GET['dept']).values('emp_id')
                    else:
                        q1 = EmployeePrimdetail.objects.filter(cadre__in = [667,668,669,645,643,644]).values('emp_id')
                    emp_list = []
                    for x in q1:
                        emp_list.append(x['emp_id'])   
                    query_emp_entries_st = hodrecommendatedamount.objects.filter(emp_id__in = emp_list).values_list('emp_id', flat=True).distinct()
                    query_emp_entries_st2 = AarPart2MarksDir.objects.filter(emp_id__in = emp_list).values_list('emp_id', flat=True).distinct()
                    data=[]
                    for q in q1:
                        emp_filled=AarPart2QuesAns.objects.filter(emp_id=q['emp_id']).values()
                        if emp_filled.count()>0:
                            emp_info=EmployeePrimdetail.objects.filter(emp_id=q['emp_id']).values('name','emp_status','cadre')
                            if emp_info[0]['emp_status']=='ACTIVE':
                                cad=emp_info[0]['cadre']
                                if cad==667 or cad==668 or cad==669 or cad==645 or cad==644 or cad==643:
                                    if q['emp_id'] in query_emp_entries_st:
                                        q['hod_status'] = "Completed"
                                    else:
                                        q['hod_status'] = "Pending"

                                    if q['emp_id'] in query_emp_entries_st2:
                                        q['admin_status'] = "Completed"
                                    else:
                                        q['admin_status'] = "Pending"
                                    data.append({'name':emp_info[0]['name'],'EmpId':q['emp_id'],'hod_status':q['hod_status'],'admin_status':q['admin_status']})

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500

    return JsonResponse(data=data,status=status,safe=False)

def staff_emg_dir_details(request):
    d3=[]
    data={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[425])
            if check==200:
                if request.method=='POST':
                    status=200
                    data=json.loads(request.body.decode("utf-8"))
                    empId=data['EmpId']

                    q1=EmployeePrimdetail.objects.filter(emp_id=empId).values('desg','ladder','dept','doj','name','cadre')
                    desg=q1[0]['desg']
                    ladder=q1[0]['ladder']
                    dept=q1[0]['dept']
                    doj=q1[0]['doj']
                    name=q1[0]['name']
                    cadre=q1[0]['cadre']
                    if cadre==667 or cadre==668 or cadre==669 or cadre==645 or cadre==644 or cadre==643:
                        total_exp = get_total_experience(empId)
                        highest_qual = get_highest_qualification(empId)
                        q4=EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                        desg_value=q4[0]['value']
                        q5=EmployeeDropdown.objects.filter(sno=ladder).exclude(value=None).values('value')
                        ladder_value=q5[0]['value']
                        q6=EmployeeDropdown.objects.filter(sno=dept).exclude(value=None).values('value')
                        dept_value=q6[0]['value']
                        q7=EmployeeDropdown.objects.filter(sno=cadre).exclude(value=None).values('value')
                        cadre_value=q7[0]['value']

                        month=date.today().month-2
                        if month==0:
                            month=12
                        gross_data=stored_gross_payable_salary_components(empId,getCurrentSession(),date.today().month-3)
                        total_gross=0
                        for gd in gross_data:
                            total_gross=total_gross+gd['gross_value']

                        session=getCurrentSession()
                        qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=empId)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                        scale_consolidates=qry_gross_value[0]['salary_type__value']

                        test = AarIncrementSettings.objects.filter(desg=desg,ladder=ladder,salary_type__value=scale_consolidates).values('value','value_type')
                        print(test.query)
                        a= list(test)[0]['value']
                        if scale_consolidates == 'CONSOLIDATE':
                            salary = ((total_gross * a) /100)
                        elif scale_consolidates == 'GRADE':
                            salary = ((total_gross * a) /100)
                        proposed_salary = total_gross + salary
                        ##print proposed_salary
                        q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=empId)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                        scale_consolidated=q7[0]['salary_type__value']

                    questions=[313,320,322,355]
                    ques_list=[]

                    for qt in questions:
                        q8=AarDropdown.objects.filter(sno=qt).values('sno','pid','field','value')
                        category=q8[0]['field']
                        q9=AarDropdown.objects.filter(field=category).exclude(value=None).values('sno','pid','field','value')
                        d2=[]
                        for q in q9:
                            q10=AarDropdown.objects.filter(field=q['value']).exclude(value=None).values('sno','pid','field','value')
                            d1=[]
                            max_list_id=[358,359,360,363,366,367,368,369,370]
                            for qr in q10:
                                i_d=qr['sno']

                                if qr['sno'] in max_list_id:
                                    q11=AarEvalutionCriteriaMaxMarks.objects.filter(evalution_criteria=qr['sno']).filter(type='E').values('max_marks')
                                    answer=AarPart2Marks.objects.filter(emp_id=empId,evalution_criteria=i_d,category='E').values('marks')
                                    m = AarPart2Marks.objects.filter(emp_id=empId,evalution_criteria=i_d,category='H').values('marks')
                                    #print(qr,answer,q11,m)
                                    d1.append({'sub':qr['value'],'id':qr['sno'],'max':q11[0]['max_marks'],'answer':answer[0]['marks'],'hod':m[0]['marks']})
                                else:
                                    answer=AarPart2QuesAns.objects.filter(ques=i_d,emp_id=empId).values('answer')
                                    ###print answer.query
                                    d1.append({'sub':qr['value'],'id':qr['sno'],'answer':answer[0]['answer']})

                            answer2=AarPart2QuesAns.objects.filter(ques=q['sno'],emp_id=empId).values('answer')
                            if len(answer2)>0:
                                if q['sno']==321:
                                    act=[]
                                    for an2 in answer2:
                                        act.append({'v':an2['answer']})

                                    d2.append({'sub':q['value'],'id':q['sno'],'data':d1,'answer':act})
                                else:
                                    d2.append({'sub':q['value'],'id':q['sno'],'data':d1,'answer':answer2[0]['answer']})
                            else:
                                d2.append({'sub':q['value'],'id':q['sno'],'data':d1})

                        d3.append({'cat':category,'id':q8[0]['sno'],'data':d2})

                        q20=AarDropdown.objects.filter(field="INCREMENT TYPE").exclude(value=None).values('sno','field','value')
                        increment_types=[]
                        for x in q20:
                            increment_types.append({'sno':x['sno'],'value':x['value']})

                        query_hod_marks = AarPart2Marks.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=empId),category = 'H').values("remarks1", "remarks2")
                        x = query_hod_marks
                        ##print x
                        try:
                            remark1 = x[0]['remarks1']
                            remark2 = x[0]['remarks2']
                        except:
                            remark2="----"
                            remark1="----"
                        query_hod_rec = hodrecommendatedamount.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=empId)).values('status','type','increment_type','amount','promoted_to').order_by('-id')[:1]
                        rec = query_hod_rec
                        try:
                            _status = rec[0]['status']
                            _increment_type = rec[0]['increment_type']
                            _amount = rec[0]['amount']
                            _type = rec[0]['type']
                            _promoted_to = rec[0]['promoted_to']
                        except:
                            _status = "----"
                            _increment_type ="----"
                            _amount = "----"
                            _type = "----"
                            _promoted_to = "---"

                    isFormFilled = isDirFormFilled(empId)
                    qdesg = EmployeeDropdown.objects.filter(field="DESIGNATION").exclude(value__isnull=True).values('sno','value')

                    data={"name":name,"dept":dept_value,"desg":desg_value,"doj":doj,"scale":scale_consolidated,"gross_salary":total_gross,"highest_qual":highest_qual,"total_exp":total_exp,"cadre":cadre_value,"ladder":ladder_value,"data":d3,"increment":increment_types, "remark1":remark1, "remark2":remark2, "status1":_status,"increment_type":_increment_type,"type":_type,"amount":_amount,"proposed_salary":proposed_salary, "salary":salary,"isFormFilled":isFormFilled,'promoted_to':_promoted_to,'desg_arr':list(qdesg)}
                    if isFormFilled:
                        q_dir_data = AarPart2MarksDir.objects.filter(emp_id=empId).values('type','increment_type','status','remarks','increment','promoted_to','promotion_amount','amount')
                        data['director_data']=q_dir_data[0]

                else:
                    status=502
            else:
                    status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data={'result':data},status=status,safe=False)

def staff_emg_dir_submit(request):
    msg=""
    if request.method=='POST':
        status=200
        data=json.loads(request.body.decode("utf-8"))
        

       #[u'INCREMENT', {u'promoted_amount': None, u'promoted_with': None, u'type': u'amount', u'promoted_to': None, u'amount': None, u'remarks': u'TEST ENTRY', u'increment_type': None}, u'TEST ENTRY', {u'EmpId': u'16824'}]
        type=None
        increment=None
        amount=0
        increment_type=None
        promoted_to=None
        promotion_amount=0
        status_q="NO INCREMENT"
        print(data)
        if(len(data)>1):
            emp_id1=data[3]['EmpId']
        
            emp_marks = data[1];
            try:
                if data[1]['remarks']!='':
                    remarks = data[1]['remarks']
                else:
                    remarks = None
            except:
                remarks=None
            if data[0]!='':
                if data[0]=='PROMOTION':
                    status_q = 'PROMOTION'
                    type = None
                    amount = None
                    increment_type = None
                    promoted_to = EmployeeDropdown.objects.get(sno = data[1]['promoted_to'])
                    if data[1]['with_increment'] == 'Y':
                        increment = data[1]['with_increment']
                        promotion_amount = data[1]['promoted_amount']
                    elif data[1]['with_increment'] == 'N':
                        increment = data[1]['with_increment']
                        promotion_amount = None
                elif data[0]=='INCREMENT':
                    status_q = 'INCREMENT'
                    promoted_to = None
                    promotion_amount = None
                    increment = None
                    type = data[1]['type']
                    increment_type = AarDropdown.objects.get(sno = data[1]['increment_type'])
                    if data[1]['amount'] != '':
                        amount = data[1]['amount']
                    else:
                        amount = None

            AarPart2MarksDir.objects.update_or_create(emp_id=EmployeePrimdetail.objects.get(emp_id = emp_id1),defaults={'type':type,'increment':increment,'status':status_q,'amount':amount,'remarks':remarks,'increment_type':increment_type,'promoted_to':promoted_to,'promotion_amount':promotion_amount})
        

    else:
        status=502
        msg="Error"

    result={'msg':msg}
    return JsonResponse(data=result,status=status,safe=False)

def staff_annual_increment_summary(request):
    data = list()
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                # emp_id = request.session['hash1']
                query0 = AarPart2MarksDir.objects.values('emp_id','increment_value')
                for i in list(query0):
                    emp_id = i['emp_id']
                    increment_value = i['increment_value']
                    if(increment_value == None):
                        increment_value = 0

                    query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('name','desg','doj','dept','title')
                    _desg = query1[0]['desg']
                    _dept = query1[0]['dept']
                    _title = query1[0]['title']
                    name = query1[0]['name']

                    doj = query1[0]['doj']
                    desgQ = EmployeeDropdown.objects.filter(sno=_desg).values('value')
                    desg = desgQ[0]['value']
                    deptQ = EmployeeDropdown.objects.filter(sno=_dept).values('value')
                    dept = deptQ[0]['value']

                    total_exp = get_total_experience(emp_id)
                    query2 = AarPart2Marks.objects.filter(emp_id=emp_id).values('marks')
                    marks = 0
                    for x in list(query2):
                        marks = marks + x['marks']
                    aar_marks = marks

                    highest_qual = get_highest_qualification(emp_id)

                    titleQ = EmployeeDropdown.objects.filter(sno=_title).values('value')
                    title = titleQ[0]['value']

                    session=getCurrentSession()
                    taxli = [0,1]
                    today = str(datetime.date.today());
                    premonth = int(today[5:7]) - 1;
                    current_salary = stored_gross_payable_salary_components(emp_id,getCurrentSession(),date.today().month-3)
                    salary = 0
                    proposed_salary = 0
                    for x in current_salary:
                        salary = salary + x['payable_value']

                    proposed_salary = increment_value + salary

                    data.append({"title": title,"name": name, "emp_id": emp_id, "desg": desg, "dept": dept, "doj": doj, "aar_marks": aar_marks, "qualification": highest_qual, "total_exp": total_exp, "increment_value": increment_value,"current_salary":salary,"proposed_salary":proposed_salary})

                status = 200
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data, safe=False, status=status)

def staff_a_report(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                emp_id = request.session['hash1']
                ques_ans = []
                question = []
                ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('ladder')
                lad_sno = list(ladder_sno)
                ladd = lad_sno[0]['ladder']
                data_values = list()
                if(ladd==591 or ladd==592 or ladd==593 or ladd==659 or ladd==658 or ladd==660):
                    if (request.method == 'GET'):
                        ques_query = AarDropdown.objects.filter(field='STAFF ASSISTANT PART-2 QUESTION').exclude(value=None).values('value','sno')
                        ans_query = AarPart2QuesAns.objects.filter(emp_id=emp_id).exclude(answer=None).values('answer','ques')
                        for x in ques_query:
                            for y in ans_query:
                                if(x['sno']==y['ques']):
                                    ques_ans.append({"question":x['value'], "ques_id":x['sno'], "answer":y['answer']})
                        # part 1
                        desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg')
                        desgn_sno = list(desg_sno)
                        desg = desgn_sno[0]['desg']
                        ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('ladder')
                        lad_sno = list(ladder_sno)
                        ladd = lad_sno[0]['ladder']
                        dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                        dep_sno = list(dept_no)
                        dep = dep_sno[0]['dept']
                        query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('name', 'doj', 'emp_id')
                        query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('doj')

                        query3 = EmployeeAcademic.objects.filter(emp_id=emp_id).values('pass_year_10','pass_year_12','pass_year_dip','pass_year_ug','pass_year_pg','date_doctrate','pass_year_other')
                        total_exp = get_total_experience(emp_id)
                        query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                        query0_desg = list(query0)
                        desgn = query0_desg[0]['value']
                        qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                        qry1_ladd = list(qry1)
                        ladder = qry1_ladd[0]['value']
                        qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                        qry2_dept = list(qry2)
                        dept = qry2_dept[0]['value']
                        gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id).exclude(Status='DELETE').values('Value')
                        gross_salary_total = float()
                        for x in gross_salary:
                            gross_salary_total += x['Value']

                        highest_qual = get_highest_qualification(emp_id)
                        total_exp = get_total_experience(emp_id)
                        q = list(query1)
                        q.append({"emp_id":emp_id, "desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual})
                        data_values.append(q)
                        data_values.append(ques_ans)
                        status = 200
                else:
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def staff_emg_report(request):
    data_values = list()
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:
                if request.method=='GET':
                    status=200
                    emp_id=request.session['hash1']
                    q1=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg','ladder','dept','doj','name','cadre','emp_id')
                    desg=q1[0]['desg']
                    ladder=q1[0]['ladder']
                    dept=q1[0]['dept']
                    doj=q1[0]['doj']
                    name=q1[0]['name']
                    cadre=q1[0]['cadre']
                    if cadre==667 or cadre==668 or cadre==669 or cadre==645 or cadre==644 or cadre==643:
                        total_exp = get_total_experience(emp_id)
                        highest_qual = get_highest_qualification(emp_id)
                        d5=[]
                        query_marks = AarPart2Marks.objects.filter(emp_id = emp_id).values('marks','evalution_criteria__value','evalution_criteria')
                        for x in list(query_marks):
                            query_mmarks = AarEvalutionCriteriaMaxMarks.objects.filter(evalution_criteria=x['evalution_criteria']).filter(type='E').values('max_marks')
                            a = {"marks":x['marks'],"cri":x['evalution_criteria__value'],"mmarks":query_mmarks[0]['max_marks']}
                            d5.append(a)
                        c1=['Category 1: Professional Performance',d5[0],d5[1],d5[2]]
                        c2=['Category 2: Professional development related activities',d5[3]]
                        c3=['Category 3: Individual Competencies' ,d5[4],d5[5],d5[6],d5[7],d5[8]]
                        evm = {"c1":c3,"c2":c2,"c3":c1}
                        q4=EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                        desg_value=q4[0]['value']
                        q5=EmployeeDropdown.objects.filter(sno=ladder).exclude(value=None).values('value')
                        ladder_value=q5[0]['value']
                        q6=EmployeeDropdown.objects.filter(sno=dept).exclude(value=None).values('value')
                        dept_value=q6[0]['value']
                        q7=EmployeeDropdown.objects.filter(sno=cadre).exclude(value=None).values('value')
                        cadre_value=q7[0]['value']
                        month=date.today().month-2
                        if month==0:
                            month=12
                        gross_data=stored_gross_payable_salary_components(emp_id,getCurrentSession(),date.today().month-3)
                        total_gross=0
                        for gd in gross_data:
                            total_gross=total_gross+gd['gross_value']
                        session=getCurrentSession()
                        q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                        scale_consolidated=q7[0]['salary_type__value']
                        d4=[]
                        query_db = AarPart2QuesAns.objects.filter(emp_id = emp_id).values('answer','ques__value', 'ques')
                        cat1 = [{"A1":query_db[0],"A2":query_db[1],"A3": query_db[2],"A4": query_db[3]}]
                        for x in list(query_db):
                            d4.append(x)
                        qmdb = []
                        arr = [342, 343, 344, 345, 348, 349, 350, 351, 352, 353, 354]
                        for x in arr:
                            qdb = AarPart2QuesAns.objects.filter(emp_id = emp_id, ques = x).values('answer','ques__value')
                            qmdb.append(qdb[0])
                        act_ques = []
                        dyq = AarPart2QuesAns.objects.filter(emp_id = emp_id, ques = 321).values('answer','ques__value')
                        for x in list(dyq):
                            act_ques.append(x)
                        data={"emp_id":emp_id,"name":name,"dept":dept_value,"desg":desg_value,"doj":doj,"scale":scale_consolidated,"gross_salary":total_gross,"highest_qual":highest_qual,"total_exp":total_exp,"cadre":cadre_value,"ladder":ladder_value,"ques_ans1":cat1,"cri_marks":evm,"rel_info":qmdb,"act_ques":act_ques}
                        data_values.append(data)
                    else:
                        status=401
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status, safe=False)

def staff_ahod_report(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                emp_id = request.session['hash1']
                ques_ans = []
                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg','dept')
                desgn_sno = list(desg_sno)
                desg = desgn_sno[0]['desg']
                dept_hod = desgn_sno[0]['dept']
                if (request.method == 'GET'):
                    data_values = list()
                    q1=Reporting.objects.filter(department=dept_hod,reporting_to=desg).values('emp_id','emp_id__ladder')
                    ##print q1
                    data =[]
                    for q in q1:
                        ladd = q['emp_id__ladder']
                        if(ladd==591 or ladd==592 or ladd==593 or ladd==659 or ladd==658 or ladd==660):
                            emp_filled=AarPart2QuesAns.objects.filter(emp_id=q['emp_id']).values()
                            if emp_filled.count()>0:
                                emp_info=EmployeePrimdetail.objects.filter(emp_id=q['emp_id']).values('name','emp_status')
                                if emp_info[0]['emp_status']=='ACTIVE':
                                    data_values.append({'name':emp_info[0]['name'],'EmpId':q['emp_id']})
                    status = 200

                elif (request.method == 'POST'):
                    data_values = list()
                    status = 200
                    data = json.loads(request.body.decode("utf-8"))
                    #print(data,'ji')
                    if(data!=None):
                        emp_id1 = data[0]['emp_id']
                        ##print data
                        ques_query = AarDropdown.objects.filter(field='STAFF ASSISTANT PART-2 QUESTION').exclude(value=None).values('value','sno')
                        ans_query = AarPart2QuesAns.objects.filter(emp_id=emp_id1).exclude(answer=None).values('answer','ques')
                        for x in ques_query:
                            for y in ans_query:
                                if(x['sno']==y['ques']):
                                    ques_ans.append({"question":x['value'], "ques_id":x['sno'], "answer":y['answer']})
                        ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                        lad_sno = list(ladder_sno)
                        ladd = lad_sno[0]['ladder']
                        if(ladd==591 or ladd==592 or ladd==593 or ladd==659 or ladd==658 or ladd==660):
                            # part 2
                            #print('HI')
                            query_increment_type = AarDropdown.objects.filter(field = 'INCREMENT TYPE').exclude(value = None).values('value','sno')
                            increment_type1 = list()
                            increment = list(query_increment_type)
                            # part 1
                            desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg')
                            desgn_sno = list(desg_sno)
                            desg = desgn_sno[0]['desg']
                            ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                            lad_sno = list(ladder_sno)
                            ladd = lad_sno[0]['ladder']
                            dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('dept')
                            dep_sno = list(dept_no)
                            dep = dep_sno[0]['dept']
                            query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('name', 'doj','emp_id')
                            query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('doj')
                            total_exp = get_total_experience(emp_id1)
                            highest_qual = get_highest_qualification(emp_id1)
                            query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                            query0_desg = list(query0)
                            desgn = query0_desg[0]['value']
                            qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                            qry1_ladd = list(qry1)
                            ladder = qry1_ladd[0]['value']
                            qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                            qry2_dept = list(qry2)
                            dept = qry2_dept[0]['value']
                            gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id1).exclude(Status='DELETE').values('Value')
                            ##print gross_salary
                            gross_salary_total = float()
                            for x in gross_salary:
                                gross_salary_total += x['Value']

                            #try:
                                                            # part 3
                            query4 = AarDropdown.objects.filter(field='EVALUATION CRITERIA').exclude(value=None).values('value', 'sno')
                            query_hod_marks = AarPart2Marks.objects.filter(emp_id=emp_id1).values('marks','evalution_criteria')
                            query_hod_remarks = AarPart2Marks.objects.filter(emp_id=emp_id1,category="H").values('remarks1')
                            hod_remarks = query_hod_remarks[0]
                            eva_crit_sno_list = list()
                            eval_cri = list(query4)
                            crit = list()
                            query_hod = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('status','promotion_amount','amount','increment','promoted_to__value','type','increment_type__value')
                            qh = query_hod[0]
                            if qh['status'] == 'INCREMENT':
                                # increment
                                if qh['increment_type__value'] == 'NORMAL':
                                    # normal incremnet type
                                    try:
                                        incremtus=increament_status_pagal(emp_id1)
                                        amount=incremtus[1]
                                    except:
                                        amount=0
                                    hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type'],'Gross salary total':gross_salary_total,'Increment Amount':amount,'After Increment':gross_salary_total+amount}
                                elif qh['increment_type__value'] == 'SPECIAL':
                                    # special increment type
                                    try:
                                        increament_status=increament_status_pagal(emp_id1)
                                        amount=increament_status[1]
                                    except:
                                        amount=0
                                    hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],'Gross salary total':gross_salary_total,"Increment Amount":qh['amount'],'After Increment':gross_salary_total+qh['amount'],"Type":qh['type']}
                            elif qh['status'] == 'PROMOTION':
                                if qh['increment'] == 'Y':
                                    try:
                                        increament_status=increament_status_pagal(emp_id1)
                                        amount=increament_status[1]
                                    except:
                                        amount=0
                                    # promotion with increment
                                    hod_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value'],'Gross salary total':gross_salary_total,'Increment Amount':0,'After Increment':gross_salary_total+qh['promotion_amount']}
                                elif qh['increment'] == 'N':
                                    try:
                                        increament_status=increament_status_pagal(emp_id1)
                                        amount=increament_status[1]
                                    except:
                                        amount=0
                                    # promotion with no increment
                                    hod_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value'],'Increment':amount,'Gross salary total':gross_salary_total,'Increment Amount':amount,'After Increment':gross_salary_total+qh['promotion_amount']}
                            elif qh['status'] == 'NO INCREMENT':
                                hod_data = {"Result":qh['status']}
                            res_data = []
                            j=0
                            # except:
                            #     status=202
                            #     msg="Please Complete the respective pearson to completely filled the details"
                            #     return JsonResponse(data={'result':data,'msg':msg},status=status,safe=False)

                            for x in eval_cri:
                                eva_arr = []
                                marks_arr = []
                                hod_marks = []
                                eva_cri_query = AarDropdown.objects.filter(pid=x['sno']).exclude(value=None).values('value','sno')
                                eva_cris_list=list(eva_cri_query)
                                for i in eva_cris_list:
                                    eva_arr.append(i['value'])

                                max_marks_query = AarEvalutionCriteriaMaxMarks.objects.filter(type='A').values('max_marks', 'evalution_criteria')
                                max_marks_list=list(max_marks_query)
                                for i in max_marks_list:
                                    marks_arr.append(i['max_marks'])

                                for z in list(query_hod_marks):
                                    hod_marks.append(z['marks'])
                                res_data.append({"_id":x['sno'],"field":x['value'],"values":eva_arr,"max_marks":marks_arr[j],"hod_marks":hod_marks[j]})
                                j = j+1
                            q = list(query1)

                            q.append({"emp_id":emp_id,"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual})
                            data_values.append({"data_value": "Success"})
                            data_values.append(q)
                            data_values.append(ques_ans)
                            data_values.append(res_data)
                            data_values.append(hod_data)
                            data_values.append(hod_remarks)

# //////////////////////////////////////////
                            query_dir = AarPart2MarksDir.objects.filter(emp_id=emp_id1).values('type','remarks','increment','promoted_to','promoted_to__value','status','increment_type','increment_type__value','promotion_amount','amount',)
                            dir_data={}
                            print(query_dir.query)
                            for qh in query_dir:
                                if qh['status'] == 'INCREMENT':
                                    # increment
                                    if qh['increment_type__value'] == 'NORMAL':
                                        # normal incremnet type
                                        try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]
                                        except:
                                            amount=0
                                        dir_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type'],'Gross salary total':gross_salary_total,'Increment Amount':amount,'After Increment':gross_salary_total+amount}
                                    elif qh['increment_type__value'] == 'SPECIAL':
                                        try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]
                                        except:
                                            amount=0
                                        # special increment type
                                        dir_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Increment Amount":qh['amount'],"Type":qh['type'],'Gross salary total':gross_salary_total,'Increment Amount':amount,'After Increment':gross_salary_total+amount}
                                elif qh['status'] == 'PROMOTION':
                                    if qh['increment'] == 'Y':
                                        try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]
                                        except:
                                            amount=0
                                        # promotion with increment
                                        dir_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value'],'Gross salary total':gross_salary_total,'Increment Amount':0,'After Increment':gross_salary_total+amount}
                                    elif qh['increment'] == 'N' or qh['increment'] is None:
                                        try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]
                                        except:
                                            amount=0
                                        print(amount,gross_salary_total)
                                        if amount is None or amount=="--":
                                            amount=0
                                        if gross_salary_total is None:
                                            gross_salary_total=0
                                        # promotion with no increment
                                        dir_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value'],'Gross salary total':gross_salary_total,'Increment Amount':amount,'After Increment':gross_salary_total+amount}
                                elif qh['status'] == 'NO INCREMENT':
                                    dir_data = {"Result":qh['status']}
                                dir_remarks=qh['remarks']
# //////////////////////////////////////////
                                data_values.append(dir_data)
                                data_values.append(dir_remarks)

                        else:
                            data_values = {"msg": "no permission"}
                    else:
                        data_values = {"data_value": "Failure"}

                else:
                    data_values = {"msg":"no permission."}
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def staff_adir_report(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                emp_id = request.session['hash1']
                ques_ans = []
                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg')
                desgn_sno = list(desg_sno)
                desg = desgn_sno[0]['desg']
                if(desg==812):
                    employees_list_query = AarPart2Marks.objects.filter(employee_band='A').values('emp_id','emp_id__name','emp_id__ladder__value')
                    output = []
                    for x in employees_list_query:
                        if x not in output:
                            output.append(x)
                    ##print output
                    employees_list = list(output)
                    data_values = list(output)
                    if (request.method == 'POST'):
                        data_values = list()
                        status = 200
                        data = json.loads(request.body.decode("utf-8"))
                        
                        if(data!=None):
                            emp_id1 = data[0]['emp_id']
                            ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                            lad_sno = list(ladder_sno)
                            ladd = lad_sno[0]['ladder']
                            if(ladd==591 or ladd==592 or ladd==593 or ladd==658 or ladd==659 or ladd==660):
                                # part 2
                                ques_query = AarDropdown.objects.filter(field='STAFF ASSISTANT PART-2 QUESTION').exclude(value=None).values('value','sno')
                                ans_query = AarPart2QuesAns.objects.filter(emp_id=emp_id1).exclude(answer=None).values('answer','ques')
                                for x in ques_query:
                                    for y in ans_query:
                                        if(x['sno']==y['ques']):
                                            ques_ans.append({"question":x['value'], "ques_id":x['sno'], "answer":y['answer']})
                                # part 1
                                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg')
                                desgn_sno = list(desg_sno)
                                desg = desgn_sno[0]['desg']
                                ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                                lad_sno = list(ladder_sno)
                                ladd = lad_sno[0]['ladder']
                                dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('dept')
                                dep_sno = list(dept_no)
                                dep = dep_sno[0]['dept']
                                query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('name', 'doj', 'emp_id')
                                query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('doj')
                                total_exp = get_total_experience(emp_id1)
                                highest_qual = get_highest_qualification(emp_id1)
                                query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                                query0_desg = list(query0)
                                desgn = query0_desg[0]['value']
                                qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                                qry1_ladd = list(qry1)
                                ladder = qry1_ladd[0]['value']
                                qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                                qry2_dept = list(qry2)
                                dept = qry2_dept[0]['value']
                                gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id1).exclude(Status='DELETE').values('Value')
                                gross_salary_total = float()
                                for x in gross_salary:
                                    gross_salary_total = gross_salary_total + x['Value']
                                gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
                                session=getCurrentSession()
                                qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                                scale_consolidates=qry_gross_value[0]['salary_type__value']
                                test = AarIncrementSettings.objects.filter(desg=desg,ladder=ladd).values('value','value_type')
                                a= list(test)[0]['value']
                                if scale_consolidates == 'CONSOLIDATE':
                                    salary = ((gross_salary_total * a) /100)
                                elif scale_consolidates == 'GRADE':
                                    salary = ((gross_salary_total * a) /100)
                                proposed_salary = gross_salary_total + salary
                                # part 3
                                query_increment_type = AarDropdown.objects.filter(field = 'INCREMENT TYPE').exclude(value = None).values('value','sno')
                                increment_type1 = list()
                                increment = list(query_increment_type)
                                qry4 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('amount')
                                qry4_amount = list(qry4)
                                amount = qry4_amount[0]['amount']
                                qry5 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('type')
                                qry5_type = list(qry5)
                                type = qry5_type[0]['type']
                                qry6 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('increment_type')
                                qry6_increment_type = list(qry6)
                                increment_type = qry6_increment_type[0]['increment_type']
                                qry7 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('status')
                                qry7_status = list(qry7)
                                qry_status = qry7_status[0]['status']
                                query4 = AarDropdown.objects.filter(field='EVALUATION CRITERIA').exclude(value=None).values('value', 'sno')
                                eva_crit_sno_list = list()
                                eval_cri = list(query4)
                                crit = list()
                                res_data = []
                                j = 0
                                for x in eval_cri:
                                    eva_arr = []
                                    eva_sno = []
                                    marks = []
                                    marks_arr = []
                                    eva_cri_query = AarDropdown.objects.filter(pid=x['sno']).exclude(value=None).values('value','sno')
                                    eva_cris_list=list(eva_cri_query)
                                    for i in eva_cris_list:
                                        eva_arr.append(i['value'])
                                    max_marks_query = AarEvalutionCriteriaMaxMarks.objects.filter(type='A').values('max_marks', 'evalution_criteria')
                                    max_marks_list=list(max_marks_query)
                                    query5 = AarPart2Marks.objects.filter(emp_id=emp_id1).values('marks','evalution_criteria')
                                    marks_list = list(query5)
                                    for i in max_marks_list:
                                        for y in marks_list:
                                            if(i['evalution_criteria']==y['evalution_criteria']):
                                                marks_arr.append(i['max_marks'])
                                                marks.append(y['marks'])
                                    res_data.append({"_id":x['sno'],"field":x['value'],"values":eva_arr,"max_marks":marks_arr[j],"marks":marks[j]})
                                    j = j+1
                                q = list(query1)
                                q.append({"emp_id": emp_id,"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual, "amount":amount, "type":type, "increment_type": increment_type, "status":qry_status,"proposed_salary":proposed_salary, "salary":salary})
                                data_values.append({"data_value": "Success"})
                                data_values.append(q)
                                data_values.append(ques_ans)
                                data_values.append(res_data)
                                qdir = AarPart2MarksDir.objects.filter(emp_id=emp_id1).values('type','remarks','increment','promoted_to__value','status','increment_type__value','promotion_amount','amount')
                                qh = qdir[0]
                                if qh['status'] == 'INCREMENT':
                                    # increment
                                    if qh['increment_type__value'] == 'NORMAL':
                                        # normal incremnet type
                                        hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type']}
                                    elif qh['increment_type__value'] == 'SPECIAL':
                                        # special increment type
                                        hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Increment Amount":qh['amount'],"Type":qh['type']}
                                elif qh['status'] == 'PROMOTION':
                                    if qh['increment'] == 'Y':
                                        # promotion with increment
                                        hod_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value']}
                                    elif qh['increment'] == 'N':
                                        # promotion with no increment
                                        hod_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value']}
                                elif qh['status'] == 'NO INCREMENT':
                                    hod_data = {"Result":qh['status']}
                                data_values.append(hod_data)
                                data_values.append({"Remarks":qh['remarks']})
                            else:
                                data_values = {"msg": "no permission"}
                        else:
                            data_values = {"data_value": "Failure"}

                    elif (request.method == 'GET'):
                        status = 200
                else:
                    data_values = {"msg":"no permission."}
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)


def staff_shod_report(request):
    data_values = list()
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                status = 200
                msg={}
                emp_id = request.session['hash1']
                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg','dept')
                desgn_sno = list(desg_sno)
                desg = desgn_sno[0]['desg']
                dept_hod = desgn_sno[0]['dept']
                if(request.method == 'POST'):
                    ##print(desg,"")
                    if (True):
                        data_values = list()
                        status = 200
                        data = json.loads(request.body.decode("utf-8"))
                        if(data!=None):
                            
                            emp_id1 = data[0]
                            ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                            lad_sno = list(ladder_sno)
                            ladd = lad_sno[0]['ladder']

                            #print(ladd)
                            if(ladd==661 or ladd==662 or ladd==663):
                                # part 1
                                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg')
                                desgn_sno = list(desg_sno)
                                desg = desgn_sno[0]['desg']
                                ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                                lad_sno = list(ladder_sno)
                                ladd = lad_sno[0]['ladder']
                                dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('dept')
                                dep_sno = list(dept_no)
                                dep = dep_sno[0]['dept']
                                query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('name', 'doj', 'emp_id')
                                query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('doj')
                                total_exp = get_total_experience(emp_id1)
                                highest_qual = get_highest_qualification(emp_id1)
                                query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                                query0_desg = list(query0)
                                desgn = query0_desg[0]['value']
                                qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                                qry1_ladd = list(qry1)
                                ladder = qry1_ladd[0]['value']
                                qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                                qry2_dept = list(qry2)
                                dept = qry2_dept[0]['value']
                                gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id1).exclude(Status="DELETE").values('Value')
                                gross_salary_total = float()
                                for x in gross_salary:
                                    gross_salary_total += x['Value']
                                gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
                                session=getCurrentSession()
                                qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                                scale_consolidates=qry_gross_value[0]['salary_type__value']
                                # part 2
                                #try:
                                query_increment_type = AarDropdown.objects.filter(field = 'INCREMENT TYPE').exclude(value = None).values('value','sno')
                                increment_type = list()
                                increment = list(query_increment_type)
                                query4 = AarDropdown.objects.filter(field='EVALUATION CRITERIA').exclude(value=None).values('value', 'sno')
                                query_hod = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('status','promotion_amount','amount','increment','promoted_to__value','type','increment_type__value').order_by('-id')[:1]

                                query_hod_marks = AarPart2Marks.objects.filter(emp_id=emp_id1,category='H').values('marks','evalution_criteria').distinct().order_by('-id')
                                query_hod_remarks = AarPart2Marks.objects.filter(emp_id=emp_id1,category="H").values('remarks1')
                                eva_crit_sno_list = list()
                                eval_cri = list(query4)
                                crit = list()
                                res_data = []
                                j=0
                                for x in eval_cri:
                                    eva_arr = []
                                    marks_arr=[]
                                    hod_marks = []
                                    eva_cri_query = AarDropdown.objects.filter(pid=x['sno']).exclude(value=None).values('value','sno')
                                    eva_cris_list=list(eva_cri_query)
                                    for i in eva_cris_list:
                                        eva_arr.append(i['value'])
                                    max_marks_query = AarEvalutionCriteriaMaxMarks.objects.filter(type='A').values('max_marks', 'evalution_criteria')
                                    max_marks_list=list(max_marks_query)
                                    for i in max_marks_list:
                                        marks_arr.append(i['max_marks'])
                                    for z in list(query_hod_marks):
                                        hod_marks.append(z['marks'])
                                    res_data.append({"_id":x['sno'],"field":x['value'],"values":eva_arr,"max_marks":marks_arr[j],"hod_marks":hod_marks[j]})
                                    j = j+1

                                q = list(query1)
                                hod_remarks = query_hod_remarks[0]
                                query_hod = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('status','promotion_amount','amount','increment','promoted_to__value','type','increment_type__value').order_by('-id')[:1]
                                ##print(query_hod)
                                qh = query_hod[0]
                                #print(qh)
                                if qh['status'] == 'INCREMENT':
                                    # increment
                                    if qh['increment_type__value'] == 'NORMAL':
                                        # normal incremnet type
                                        #try:
                                        #print(emp_id1,"hello")
                                        increament_status=increament_status_pagal(emp_id1)
                                        #print(increament_status,"he")
                                        amount=increament_status[1]
                                        # except:
                                        #     amount=0
                                        qh['amount'] = amount
                                        if gross_salary_total is None:
                                            gross_salary_total=0
                                        if qh['amount'] is None:
                                            qh['amount']=0
                                        
                                        hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type'],'Gross salary total':gross_salary_total,"Increment Amount":qh['amount'],'After Increment':gross_salary_total+qh['amount']}
                                    elif qh['increment_type__value'] == 'SPECIAL':
                                        # special increment type
                                        
                                        increament_status=increament_status_pagal(emp_id1)
                                        amount=increament_status[1]
                                        # except:
                                        #     amount=0
                                        hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Increment Amount":qh['amount'],"Type":qh['type'],'Gross salary total':gross_salary_total,"Increment Amount":qh['amount'],'After Increment':gross_salary_total+qh['amount']}
                                elif qh['status'] == 'PROMOTION':
                                    if qh['increment'] == 'Y':
                                        # promotion with increment
                                        #try:
                                        increament_status=increament_status_pagal(emp_id1)
                                        amount=increament_status[1]

                                        qh['amount']=amount
                                        # except:
                                        #     amount=0
                                        hod_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value'],'Gross salary total':gross_salary_total,"Increment Amount":0,'After Increment':gross_salary_total+qh['amount']}
                                    elif qh['increment'] == 'N':
                                        #try:
                                        increament_status=increament_status_pagal(emp_id1)
                                        amount=increament_status[1]
                                        # except:
                                        #     amount=0
                                        qh['amount'] =amount
                                        hod_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value'],'Gross salary total':gross_salary_total,"Increment Amount":qh['amount'],'After Increment':gross_salary_total+qh['amount']}
                                        # promotion with no increment
                                elif qh['status'] == 'NO INCREMENT':
                                    hod_data = {"Result":qh['status']}
                                else:
                                    hod_data = {"Result":""}
                                # except:
                                #     status=202
                                #     msg="Please Complete the respective pearson to completely filled the details"
                                #     return JsonResponse(data={'result':data,'msg':msg},status=status,safe=False)

                                q.append({"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual,"scale":scale_consolidates})
                                data_values.append({"data_value": "Success"})
                                data_values.append(q)
                                data_values.append(res_data)
                                data_values.append(hod_data)
                                data_values.append(hod_remarks)
                                query_dir = AarPart2MarksDir.objects.filter(emp_id=emp_id1).values('type','remarks','increment','promoted_to','promoted_to__value','status','increment_type','increment_type__value','promotion_amount','amount',)
                                
                                dir_data={}
                                
                                for qh in query_dir:
                                    dir_remarks=qh['remarks']
                                    if qh['status'] == 'INCREMENT':
                                        # increment
                                        if qh['increment_type__value'] == 'NORMAL':
                                            # normal incremnet type
                                            #try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]
                                            # except:
                                            #     amount=0
                                            qh['amount'] =amount
                                            if gross_salary_total is None:
                                                gross_salary_total=0
                                            if qh['amount'] is None:
                                                qh['amount']=0
                                            
                                            dir_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type'],'Gross salary total':gross_salary_total,"Increment Amount":qh['amount'],'After Increment':gross_salary_total+qh['amount']}
                                        elif qh['increment_type__value'] == 'SPECIAL':
                                            # special increment type
                                            #try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]

                                            qh['amount'] =amount
                                            # except:
                                            #     amount=0
                                            if gross_salary_total is None:
                                                gross_salary_total=0
                                            if qh['amount'] is None:
                                                qh['amount']=0
                                        
                                            dir_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Increment Amount":qh['amount'],"Type":qh['type'],'Gross salary total':gross_salary_total,"Increment Amount":qh['amount'],'After Increment':gross_salary_total+qh['amount']}
                                    elif qh['status'] == 'PROMOTION':
                                        if qh['increment'] == 'Y':
                                            # promotion with increment
                                            #try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]
                                            
                                            qh['amount'] =amount
                                            # except:
                                            #     amount=0
                                            if gross_salary_total is None:
                                                gross_salary_total=0
                                            if qh['amount'] is None:
                                                qh['amount']=0
                                        
                                            dir_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value'],'Gross salary total':gross_salary_total,"Increment Amount":0,'After Increment':gross_salary_total+qh['amount']}
                                        elif qh['increment'] == 'N':
                                            # try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]
                                            # except:
                                            #     amount=0
                                            qh['amount'] =amount
                                            if gross_salary_total is None:
                                                gross_salary_total=0
                                            if qh['amount'] is None:
                                                qh['amount']=0
                                        
                                            dir_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value'],'Gross salary total':gross_salary_total,"Increment Amount":qh['amount'],'After Increment':gross_salary_total+qh['amount']}
                                            # promotion with no increment
                                    elif qh['status'] == 'NO INCREMENT':
                                            # try:
                                            increament_status=increament_status_pagal(emp_id1)
                                            amount=increament_status[0]
                                            # except:
                                            #     amount=0
                                            qh['amount'] =amount
                                            if gross_salary_total is None:
                                                gross_salary_total=0
                                            if qh['amount'] is None:
                                                qh['amount']=0
                                        
                                            dir_data = {"Result":qh['status'],'Gross salary total':gross_salary_total,"Increment Amount":qh['amount'],'After Increment':gross_salary_total+amount}
                                    else:
                                        dir_data = {"Result":""}
                                    data_values.append(dir_data)
                                    data_values.append(dir_remarks) 
# //////////////////////////////////////////////////////////////


                                status = 200
                                msg = "success"
                            else:
                                data_values = {"msg": "no permission"}
                        else:
                            data_values = {"data_value": "Failure"}

                elif (request.method == 'GET'):
                    data_values = list()
                    if request.GET['request_type'] == "employee_info":
                        q1=Reporting.objects.filter(department=dept_hod,reporting_to=desg).values('emp_id','emp_id__ladder')
                        ##print q1
                        data=[]
                        for q in q1:
                            ladd = q['emp_id__ladder']
                            if(ladd==661 or ladd==662 or ladd==663):
                                employees_list_query = EmployeePrimdetail.objects.filter(emp_id=q['emp_id']).values('name','emp_status')
                                if employees_list_query[0]['emp_status']=='ACTIVE':
                                    data_values.append({'name':employees_list_query[0]['name'],'emp_id':q['emp_id']})
                        status = 200
                else:
                    data_values = {"msg":"no permission."}
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def staff_sdir_report(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if (check == 200):
                emp_id = request.session['hash1']
                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg')
                desgn_sno = list(desg_sno)
                desg = desgn_sno[0]['desg']
                if(desg==812):
                    employees_list_query = AarPart2Marks.objects.filter(employee_band='S').values('emp_id','emp_id__name','emp_id__ladder__value')
                    output = []
                    for x in employees_list_query:
                        if x not in output:
                            output.append(x)
                    employees_list = list(output)
                    data_values = list(output)

                  
                    if (request.method == 'POST'):
                        data_values = list()
                        status = 200
                        data = json.loads(request.body.decode("utf-8"))
                        if(data!=None):
                            emp_id1 = data[0]['emp_id']
                            ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder','ladder__value')
                            lad_sno = list(ladder_sno)
                            ladd = lad_sno[0]['ladder']
                            ladder_value = lad_sno[0]['ladder__value']
                            ##print ladder_value
                            if(ladd==661 or ladd==662 or ladd==663):
                                # part 1
                                desg_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('desg')
                                desgn_sno = list(desg_sno)
                                desg = desgn_sno[0]['desg']
                                ladder_sno = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('ladder')
                                lad_sno = list(ladder_sno)
                                ladd = lad_sno[0]['ladder']
                                dept_no = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('dept')
                                dep_sno = list(dept_no)
                                dep = dep_sno[0]['dept']
                                query1 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('emp_id','name', 'doj','emp_category')
                                query2 = EmployeePrimdetail.objects.filter(emp_id=emp_id1).values('doj')
                                total_exp = get_total_experience(emp_id1)
                                highest_qual = get_highest_qualification(emp_id1)
                                query0 = EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                                query0_desg = list(query0)
                                desgn = query0_desg[0]['value']
                                qry1 = EmployeeDropdown.objects.filter(sno=ladd).exclude(value=None).values('value')
                                qry1_ladd = list(qry1)
                                ladder = qry1_ladd[0]['value']
                                qry2 = EmployeeDropdown.objects.filter(sno=dep).exclude(value=None).values('value')
                                qry2_dept = list(qry2)
                                dept = qry2_dept[0]['value']
                                gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=emp_id1).exclude(Status='DELETE').values('Value')
                                gross_salary_total = float()
                                for x in gross_salary:
                                    gross_salary_total += x['Value']
                                gross_data=stored_gross_payable_salary_components(emp_id1,getCurrentSession(),date.today().month-3)
                                session=getCurrentSession()
                                qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id1)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                                scale_consolidates=qry_gross_value[0]['salary_type__value']
                                test = AarIncrementSettings.objects.filter(desg=desg,ladder=ladd).values('value','value_type')
                                a= list(test)[0]['value']
                                if scale_consolidates == 'CONSOLIDATE':
                                    salary = ((gross_salary_total * a) /100)
                                    alary
                                elif scale_consolidates == 'GRADE':
                                    salary = ((gross_salary_total * a) /100)
                                proposed_salary = gross_salary_total + salary
                                # part 2
                                query_increment_type = AarDropdown.objects.filter(field = 'INCREMENT TYPE').exclude(value = None).values('value','sno')
                                increment_type1 = list()
                                increment = list(query_increment_type)
                                qry4 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('amount')
                                qry4_amount = list(qry4)
                                amount = qry4_amount[0]['amount']
                                qry5 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('type')
                                qry5_type = list(qry5)
                                type = qry5_type[0]['type']
                                qry6 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('increment_type')
                                qry6_increment_type = list(qry6)
                                increment_type = qry6_increment_type[0]['increment_type']
                                qry7 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('status')
                                qry7_status = list(qry7)
                                qry_status = qry7_status[0]['status']
                                qry8 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('promoted_to')
                                qry8_type = list(qry8)
                                promoted_to = qry8_type[0]['promoted_to']
                                qry9 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('increment')
                                qry9_type = list(qry9)
                                increment_a = qry9_type[0]['increment']
                                qry10 = hodrecommendatedamount.objects.filter(emp_id=emp_id1).values('promotion_amount')
                                qry10_type = list(qry10)
                                promotion_amount = qry10_type[0]['promotion_amount']
                                query4 = AarDropdown.objects.filter(field='EVALUATION CRITERIA').exclude(value=None).values('value', 'sno')
                                eva_crit_sno_list = list()
                                eval_cri = list(query4)
                                crit = list()
                                res_data = []
                                j=0
                                for x in eval_cri:
                                    eva_arr = []
                                    eva_sno = []
                                    marks=[]
                                    marks_arr=[]
                                    eva_cri_query = AarDropdown.objects.filter(pid=x['sno']).exclude(value=None).values('value','sno')
                                    eva_cris_list=list(eva_cri_query)
                                    for i in eva_cris_list:
                                        eva_arr.append(i['value'])
                                    max_marks_query = AarEvalutionCriteriaMaxMarks.objects.filter(type='A').values('max_marks', 'evalution_criteria')
                                    max_marks_list=list(max_marks_query)
                                    query5 = AarPart2Marks.objects.filter(emp_id=emp_id1).values('marks','evalution_criteria')
                                    marks_list = list(query5)
                                    for i in max_marks_list:
                                        for y in marks_list:
                                            if(i['evalution_criteria']==y['evalution_criteria']):
                                                marks_arr.append(i['max_marks'])
                                                marks.append(y['marks'])
                                    res_data.append({"_id":x['sno'],"field":x['value'],"values":eva_arr,"max_marks":marks_arr[j],"marks":marks[j]})
                                    j = j+1
                                q = list(query1)

                                q.append({"desg":desgn,"ladder":ladder,"dept":dept,"total_exp": total_exp, "gross_salary":gross_salary_total, "highest_qual":highest_qual, "amount":amount, "type":type, "increment_type": increment_type, "status":qry_status,"promoted_to":promoted_to, "increment_a":increment_a, "promotion_amount":promotion_amount,"proposed_salary":proposed_salary, "salary":salary})
                                data_values.append({"data_value": "Success"})
                                data_values.append(q)
                                data_values.append(res_data)
                                qdir = AarPart2MarksDir.objects.filter(emp_id=emp_id1).values('type','remarks','increment','promoted_to__value','status','increment_type__value','promotion_amount','amount')
                                qh = qdir[0]
                                if qh['status'] == 'INCREMENT':
                                    # increment
                                    if qh['increment_type__value'] == 'NORMAL':
                                        # normal incremnet type
                                        hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type']}
                                    elif qh['increment_type__value'] == 'SPECIAL':
                                        # special increment type
                                        hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Increment Amount":qh['amount'],"Type":qh['type']}
                                elif qh['status'] == 'PROMOTION':
                                    if qh['increment'] == 'Y':
                                        # promotion with increment
                                        hod_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value']}
                                    elif qh['increment'] == 'N':
                                        # promotion with no increment
                                        hod_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value']}
                                elif qh['status'] == 'NO INCREMENT':
                                    hod_data = {"Result":qh['status']}
                                data_values.append(hod_data)
                                data_values.append({"Remarks":qh['remarks']})
                            else:
                                data_values = {"msg": "no permission"}
                        else:
                            data_values = {"data_value": "Failure"}

                    elif (request.method == 'GET'):
                        status = 200
                else:
                    data_values = {"msg":"no permission."}
                    status = 403
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data_values, safe=False, status=status)

def staff_emghod_report(request):
    d3=[]
    data={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:
                if request.method=='POST':
                    status=200
                    data=json.loads(request.body.decode("utf-8"))
                    ##print data
                    empId=data['EmpId']
                    q1=EmployeePrimdetail.objects.filter(emp_id=empId).values('desg','ladder','dept','doj','name','cadre')
                    desg=q1[0]['desg']
                    ladder=q1[0]['ladder']
                    dept=q1[0]['dept']
                    doj=q1[0]['doj']
                    name=q1[0]['name']
                    cadre=q1[0]['cadre']
                    if cadre==667 or cadre==668 or cadre==669 or cadre==645 or cadre==644 or cadre==643:
                        total_exp = get_total_experience(empId)
                        highest_qual = get_highest_qualification(empId)
                        q4=EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                        desg_value=q4[0]['value']
                        q5=EmployeeDropdown.objects.filter(sno=ladder).exclude(value=None).values('value')
                        ladder_value=q5[0]['value']
                        q6=EmployeeDropdown.objects.filter(sno=dept).exclude(value=None).values('value')
                        dept_value=q6[0]['value']
                        q7=EmployeeDropdown.objects.filter(sno=cadre).exclude(value=None).values('value')
                        cadre_value=q7[0]['value']

                        month=date.today().month-2
                        if month==0:
                            month=12
                        gross_data=stored_gross_payable_salary_components(empId,getCurrentSession(),date.today().month-3)
                        print()
                        total_gross=0
                        for gd in gross_data:
                            total_gross=total_gross+gd['gross_value']

                        session=getCurrentSession()
                        try:
                            q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=empId)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                            scale_consolidated=q7[0]['salary_type__value']
                        except:
                            scale_consolidated='---'
                    questions=[313,320,322,355]
                    ques_list=[]


                    #try:
                    for qt in questions:
                        q8=AarDropdown.objects.filter(sno=qt).values('sno','pid','field','value')
                        category=q8[0]['field']
                        q9=AarDropdown.objects.filter(field=category).exclude(value=None).values('sno','pid','field','value')
                        d2=[]
                        for q in q9:
                            q10=AarDropdown.objects.filter(field=q['value']).exclude(value=None).values('sno','pid','field','value')
                            d1=[]
                            max_list_id=[358,359,360,363,366,367,368,369,370]
                            for qr in q10:
                                i_d=qr['sno']

                                if qr['sno'] in max_list_id:
                                    q11=AarEvalutionCriteriaMaxMarks.objects.filter(evalution_criteria=qr['sno']).filter(type='E').values('max_marks')
                                    answer=AarPart2Marks.objects.filter(emp_id=empId,evalution_criteria=i_d,category='E').values('marks')
                                    m = AarPart2Marks.objects.filter(emp_id=empId,category="H",evalution_criteria=i_d).values('marks')

                                    d1.append({'sub':qr['value'],'id':qr['sno'],'max':q11[0]['max_marks'],'answer':answer[0]['marks'],'hod':m[0]['marks']})
                                else:
                                    answer=AarPart2QuesAns.objects.filter(ques=i_d,emp_id=empId).values('answer')
                                    d1.append({'sub':qr['value'],'id':qr['sno'],'answer':answer[0]['answer']})

                            answer2=AarPart2QuesAns.objects.filter(ques=q['sno'],emp_id=empId).values('answer')

                            if len(answer2)>0:
                                if q['sno']==321:
                                    act=[]
                                    for an2 in answer2:
                                        act.append({'v':an2['answer']})

                                    d2.append({'sub':q['value'],'id':q['sno'],'data':d1,'answer':act})
                                else:
                                    d2.append({'sub':q['value'],'id':q['sno'],'data':d1,'answer':answer2[0]['answer']})
                            else:
                                d2.append({'sub':q['value'],'id':q['sno'],'data':d1})

                        d3.append({'cat':category,'id':q8[0]['sno'],'data':d2})
                    query_hod = hodrecommendatedamount.objects.filter(emp_id=empId).values('status','promotion_amount','amount','increment','promoted_to__value','type','increment_type__value').order_by('-id')
                    qh = query_hod[0]
                    if qh['status'] == 'INCREMENT':
                                # increment
                        if qh['increment_type__value'] == 'NORMAL':
                            # normal incremnet type
                            try:
                                incremtus=increament_status_pagal(empId)
                                amount=incremtus[1]
                            except:
                                amount=0

                            hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type'],'Gross salary total':total_gross,'Increment Amount':amount,'After Increment':total_gross+amount}
                        elif qh['increment_type__value'] == 'SPECIAL':
                            # special increment type
                            try:
                                increament_status=increament_status_pagal(empId)
                                amount=increament_status[1]
                            except:
                                amount=0
                            hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],'Gross salary total':total_gross,"Increment Amount":qh['amount'],'After Increment':total_gross+qh['amount'],"Type":qh['type']}
                    elif qh['status'] == 'PROMOTION':
                        if qh['increment'] == 'Y':
                            try:
                                increament_status=increament_status_pagal(empId)
                                amount=increament_status[1]
                            except:
                                amount=0
                            # promotion with increment
                            hod_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value'],'Gross salary total':total_gross,'Increment Amount':0,'After Increment':total_gross+qh['promotion_amount']}
                        elif qh['increment'] == 'N':
                            try:
                                increament_status=increament_status_pagal(empId)
                                amount=increament_status[1]
                            except:
                                amount=0
                            hod_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value'],'Increment':amount,'Gross salary total':total_gross,'Increment Amount':amount,'After Increment':total_gross+amount}
                    elif qh['status'] == 'NO INCREMENT':
                                hod_data = {"Result":qh['status']}
                    query_hod_remarks = AarPart2Marks.objects.filter(emp_id=empId,category="H").values('remarks1','remarks2').order_by('-id')
                    # except Exception as e:
                    #     #print(e)
                    #     status=202
                    #     msg="Please Complete the respective pearson to completely filled the details"
                    #     return JsonResponse(data={'result':data,'msg':msg},status=status,safe=False)


                    qdir = AarPart2MarksDir.objects.filter(emp_id=empId).values('type','remarks','increment','promoted_to__value','status','increment_type__value','promotion_amount','amount')
                    if len(qdir)>0:
                        qh=qdir[0]
                        if qh['status'] == 'INCREMENT':
                            # increment
                            if qh['increment_type__value'] == 'NORMAL':
                                # normal incremnet type
                                try:
                                    increament_status=increament_status_pagal(empId)
                                    amount=increament_status[0]
                                except:
                                    amount=0
                                dir_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type'],'Gross salary total':total_gross,'Increment Amount':amount,'After Increment':total_gross+amount}
                            elif qh['increment_type__value'] == 'SPECIAL':
                                try:
                                    increament_status=increament_status_pagal(empId)
                                    amount=increament_status[0]
                                except:
                                    amount=0
                                # special increment type
                                dir_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Increment Amount":qh['amount'],"Type":qh['type'],'Gross salary total':total_gross,'Increment Amount':amount,'After Increment':total_gross+amount}
                        elif qh['status'] == 'PROMOTION':
                            if qh['increment'] == 'Y':
                                try:
                                    increament_status=increament_status_pagal(empId)
                                    amount=increament_status[0]
                                except:
                                    amount=0
                                # promotion with increment
                                dir_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value'],'Gross salary total':total_gross,'Increment Amount':0,'After Increment':total_gross+qh['promotion_amount']}
                            elif qh['increment'] == 'N':
                                try:
                                    increament_status=increament_status_pagal(empId)
                                    amount=increament_status[0]
                                except:
                                    amount=0
                                # promotion with no increment
                                dir_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value'],'Gross salary total':total_gross,'Increment Amount':amount,'After Increment':total_gross+amount}
                        elif qh['status'] == 'NO INCREMENT':
                            dir_data = {"Result":qh['status']}
                        #print(qdir)
                        query_dir_remarks=qh['remarks']
                        data={'dir_data':dir_data,'query_dir_remarks':query_dir_remarks,"name":name,"dept":dept_value,"desg":desg_value,"doj":doj,"scale":scale_consolidated,"gross_salary":total_gross,"highest_qual":highest_qual,"total_exp":total_exp,"cadre":cadre_value,"data":d3,"ladder":ladder_value,"remarks":query_hod_remarks[0],"hod_data":hod_data}
                    else:
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                        data={"name":name,"dept":dept_value,"desg":desg_value,"doj":doj,"scale":scale_consolidated,"gross_salary":total_gross,"highest_qual":highest_qual,"total_exp":total_exp,"cadre":cadre_value,"data":d3,"ladder":ladder_value,"remarks":query_hod_remarks[0],"hod_data":hod_data}
                    # #print(data['dir_data'])
                else:
                    status=502
            else:
                    status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data={'result':data},status=status,safe=False)

def staff_emgdir_report(request):
    data_values = list()
    d3=[]
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[425])
            if check==200:
                if request.method=='POST':
                    status=200
                    data=json.loads(request.body.decode("utf-8"))
                    empId=data['emp_id']
                    q1=EmployeePrimdetail.objects.filter(emp_id=empId).values('emp_id','desg','ladder','dept','doj','name','cadre')
                    desg=q1[0]['desg']
                    ladder=q1[0]['ladder']
                    dept=q1[0]['dept']
                    doj=q1[0]['doj']
                    name=q1[0]['name']
                    cadre=q1[0]['cadre']
                    emp_id = q1[0]['emp_id']
                    if cadre==667 or cadre==668 or cadre==669 or cadre==645 or cadre==644 or cadre==643:
                        total_exp = get_total_experience(empId)
                        highest_qual = get_highest_qualification(empId)
                        q4=EmployeeDropdown.objects.filter(sno=desg).exclude(value=None).values('value')
                        desg_value=q4[0]['value']
                        q5=EmployeeDropdown.objects.filter(sno=ladder).exclude(value=None).values('value')
                        ladder_value=q5[0]['value']
                        q6=EmployeeDropdown.objects.filter(sno=dept).exclude(value=None).values('value')
                        dept_value=q6[0]['value']
                        q7=EmployeeDropdown.objects.filter(sno=cadre).exclude(value=None).values('value')
                        cadre_value=q7[0]['value']

                        month=date.today().month-2
                        if month==0:
                            month=12
                        gross_data=stored_gross_payable_salary_components(empId,getCurrentSession(),date.today().month-3)
                        total_gross=0
                        for gd in gross_data:
                            total_gross=total_gross+gd['gross_value']

                        session=getCurrentSession()
                        qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=empId)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                        scale_consolidates=qry_gross_value[0]['salary_type__value']
                        test = AarIncrementSettings.objects.filter(desg=desg,ladder=ladder).values('value','value_type')
                        a= list(test)[0]['value']
                        if scale_consolidates == 'CONSOLIDATE':
                            salary = ((total_gross * a) /100)
                            alary
                        elif scale_consolidates == 'GRADE':
                            salary = ((total_gross * a) /100)
                        proposed_salary = total_gross + salary
                        q7=EmployeeGross_detail.objects.filter(Emp_Id=EmployeePrimdetail.objects.get(emp_id=empId)).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                        scale_consolidated=q7[0]['salary_type__value']


                    questions=[313,320,322,355]
                    ques_list=[]

                    for qt in questions:
                        q8=AarDropdown.objects.filter(sno=qt).values('sno','pid','field','value')
                        category=q8[0]['field']
                        q9=AarDropdown.objects.filter(field=category).exclude(value=None).values('sno','pid','field','value')
                        d2=[]
                        for q in q9:
                            q10=AarDropdown.objects.filter(field=q['value']).exclude(value=None).values('sno','pid','field','value')
                            d1=[]
                            max_list_id=[358,359,360,363,366,367,368,369,370]
                            for qr in q10:
                                i_d=qr['sno']

                                if qr['sno'] in max_list_id:
                                    q11=AarEvalutionCriteriaMaxMarks.objects.filter(evalution_criteria=qr['sno']).filter(type='E').values('max_marks')
                                    answer=AarPart2Marks.objects.filter(emp_id=empId,evalution_criteria=i_d,category='E').values('marks')
                                    m = AarPart2Marks.objects.filter(emp_id=empId,category="H",evalution_criteria=i_d).values('marks')
                                    d1.append({'sub':qr['value'],'id':qr['sno'],'max':q11[0]['max_marks'],'answer':answer[0]['marks'],'hod':m[0]['marks']})
                                else:
                                    answer=AarPart2QuesAns.objects.filter(ques=i_d,emp_id=empId).values('answer')
                                    d1.append({'sub':qr['value'],'id':qr['sno'],'answer':answer[0]['answer']})

                            answer2=AarPart2QuesAns.objects.filter(ques=q['sno'],emp_id=empId).values('answer')
                            if len(answer2)>0:
                                if q['sno']==321:
                                    act=[]
                                    for an2 in answer2:
                                        act.append({'v':an2['answer']})

                                    d2.append({'sub':q['value'],'id':q['sno'],'data':d1,'answer':act})
                                else:
                                    d2.append({'sub':q['value'],'id':q['sno'],'data':d1,'answer':answer2[0]['answer']})
                            else:
                                d2.append({'sub':q['value'],'id':q['sno'],'data':d1})

                        d3.append({'cat':category,'id':q8[0]['sno'],'data':d2})

                        q20=AarDropdown.objects.filter(field="INCREMENT TYPE").exclude(value=None).values('sno','field','value')
                        increment_types=[]
                        for x in q20:
                            increment_types.append({'sno':x['sno'],'value':x['value']})

                        query_hod_marks = AarPart2Marks.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=empId),category = 'H').values("remarks1", "remarks2")
                        x = query_hod_marks
                        remark1 = x[0]['remarks1']
                        remark2 = x[0]['remarks2']

                        query_hod_rec = hodrecommendatedamount.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=empId)).values('status','type','increment_type','amount')
                        rec = query_hod_rec
                        _status = rec[0]['status']
                        _increment_type = rec[0]['increment_type']
                        _amount = rec[0]['amount']
                        _type = rec[0]['type']

                    qdir = AarPart2MarksDir.objects.filter(emp_id=empId).values('type','remarks','increment','promoted_to__value','status','increment_type__value','promotion_amount','amount')
                    qh = qdir[0]
                    if qh['status'] == 'INCREMENT':
                        # increment
                        if qh['increment_type__value'] == 'NORMAL':
                            # normal incremnet type
                            hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Type":qh['type']}
                        elif qh['increment_type__value'] == 'SPECIAL':
                            # special increment type
                            hod_data = {"Result":qh['status'],"Increment Type":qh['increment_type__value'],"Increment Amount":qh['amount'],"Type":qh['type']}
                    elif qh['status'] == 'PROMOTION':
                        if qh['increment'] == 'Y':
                            # promotion with increment
                            hod_data = {"Result":qh['status'],"Promotion Amount":qh['promotion_amount'],"Promoted To":qh['promoted_to__value']}
                        elif qh['increment'] == 'N':
                            # promotion with no increment
                            hod_data = {"Result":qh['status'],"Promoted To":qh['promoted_to__value']}
                    elif qh['status'] == 'NO INCREMENT':
                        hod_data = {"Result":qh['status']}

                    data={"emp_id":emp_id,"name":name,"dept":dept_value,"desg":desg_value,"doj":doj,"scale":scale_consolidated,"gross_salary":total_gross,"highest_qual":highest_qual,"total_exp":total_exp,"cadre":cadre_value,"ladder":ladder_value,"data":d3,"remark1":remark1, "remark2":remark2, "status1":_status,"increment_type":_increment_type,"type":_type,"amount":_amount,"proposed_salary":proposed_salary, "salary":salary,"Remarks":qh['remarks'],"hod_data":hod_data}

                else:
                    status=502
            else:
                    status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data={'result':data},status=status,safe=False)

def aar_dir_advance_report(request):
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'organization':
                        query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="ORGANIZATION").values('sno','value')
                    elif request.GET['request_type'] == "department":
                        dept_sno=EmployeeDropdown.objects.filter(pid=548,value="DEPARTMENT").values('sno')
                        query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'],field="DEPARTMENT").values('sno','value')
                    elif request.GET['request_type'] == "emp_category":
                        query=EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="CATEGORY OF EMPLOYEE").values('sno','value')
                    data_values=list(query)
                status = 200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,status=status, safe=False)

def aar_dir_advance_report_data(request):
    data_values = list()
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:
                if request.method == 'POST':
                    status = 200
                    data=json.loads(request.body.decode("utf-8"))
                    # ##print data
                    dept = data['department']
                    org = data['organisation']
                    cat_emp = data['category_of_employee']

                    emp_a = list()
                    if dept == 'ALL':
                        query_emp_total_a = EmployeePrimdetail.objects.filter(ladder__in=[591,592,593],emp_status='ACTIVE',emp_category__in=cat_emp).values('emp_id', 'name', 'dept__value', 'desg__value', 'emp_category__value', 'ladder__value')    # A Band
                    else:
                        query_emp_total_a = EmployeePrimdetail.objects.filter(ladder__in=[591,592,593],emp_status='ACTIVE',emp_category__in=cat_emp, dept = dept).values('emp_id', 'name', 'dept__value', 'desg__value', 'emp_category__value', 'ladder__value')    # A Band
                    emps_a = list(query_emp_total_a)
                    for x in query_emp_total_a:
                        emp_a.append(x['emp_id'])
                    emp_total_a_total = len(query_emp_total_a)

                    emp_s = list()
                    if dept == 'ALL':
                        query_emp_total_s = EmployeePrimdetail.objects.filter(ladder__in=[661,662,663],emp_status='ACTIVE',emp_category__in=cat_emp).values('emp_id', 'name', 'dept__value', 'desg__value', 'emp_category__value', 'ladder__value')    # S Band
                    else:
                        query_emp_total_s = EmployeePrimdetail.objects.filter(ladder__in=[661,662,663],emp_status='ACTIVE',emp_category__in=cat_emp, dept = dept).values('emp_id', 'name', 'dept__value', 'desg__value', 'emp_category__value', 'ladder__value')    # S Band
                    emps_s = list(query_emp_total_s)
                    for x in query_emp_total_s:
                        emp_s.append(x['emp_id'])
                    emp_total_s_total = len(query_emp_total_s)

                    emp_emg = list()
                    if dept == 'ALL':
                        query_emp_total_emg = EmployeePrimdetail.objects.filter(ladder__in=[588,589,590,585,586,587,632,633,634,635,636,637,638,639,651,652,653,654,655,656,657],emp_status='ACTIVE',emp_category__in=cat_emp).values('emp_id', 'name', 'dept__value', 'desg__value', 'emp_category__value', 'ladder__value')  # EMG Band
                    else:
                        query_emp_total_emg = EmployeePrimdetail.objects.filter(ladder__in=[588,589,590,585,586,587,632,633,634,635,636,637,638,639,651,652,653,654,655,656,657],emp_status='ACTIVE',emp_category__in=cat_emp, dept = dept).values('emp_id', 'name', 'dept__value', 'desg__value', 'emp_category__value', 'ladder__value')  # EMG Band
                    emps_emg = list(query_emp_total_emg)
                    for x in query_emp_total_emg:
                        emp_emg.append(x['emp_id'])
                    emp_total_emg_total = len(query_emp_total_emg)

                    total = {"a_band_total":emp_total_a_total,"s_band_total":emp_total_s_total,"emg_band_total":emp_total_emg_total}
                    # ##print total

                    query_emp_entries_emg = AarPart2QuesAns.objects.filter(employee_band = "M", emp_id__in = emp_emg).values_list('emp_id', flat=True).distinct()
                    for x in emps_emg:
                        if x['emp_id'] in query_emp_entries_emg:
                            x['status'] = "Completed"
                        else:
                            x['status'] = "Pending"
                    emp_count_emg_filled =  len(query_emp_entries_emg)

                    ############## APPROVAL STATUS ##################

                    query_emp_entries_st = (hodrecommendatedamount.objects.filter(emp_id__in = emp_emg).values_list('emp_id', flat=True))
                    query_emp_entries_st2 = AarPart2MarksDir.objects.filter(emp_id__in = emp_emg).values_list('emp_id', flat=True)
                    #print(len(query_emp_entries_st))
                    for x in emps_emg:
                        if x['emp_id'] in (query_emp_entries_st):
                            x['hod_status'] = "Completed"
                        else:
                            x['hod_status'] = "Pending"

                        if x['emp_id'] in list(query_emp_entries_st2):
                            x['admin_status'] = "Completed"
                        else:
                            x['admin_status'] = "Pending"

                    ##################################################


                    query_emp_entries_a = AarPart2QuesAns.objects.filter(employee_band = "A", emp_id__in = emp_a).values_list('emp_id', flat=True).distinct()
                    for x in emps_a:
                        if x['emp_id'] in query_emp_entries_a:
                            x['status'] = "Completed"
                        else:
                            x['status'] = "Pending"
                    emp_count_a_filled =  len(query_emp_entries_a)

                    ############## APPROVAL STATUS ##################

                    query_emp_entries_st = hodrecommendatedamount.objects.filter(emp_id__in = emp_a).values_list('emp_id', flat=True).distinct()
                    query_emp_entries_st2 = AarPart2MarksDir.objects.filter(emp_id__in = emp_a).values_list('emp_id', flat=True).distinct()
                    for x in emps_a:
                        if x['emp_id'] in query_emp_entries_st:
                            x['hod_status'] = "Completed"
                        else:
                            x['hod_status'] = "Pending"

                        if x['emp_id'] in query_emp_entries_st2:
                            x['admin_status'] = "Completed"
                        else:
                            x['admin_status'] = "Pending"
                    ##################################################

                    query_emp_entries_s = AarPart2Marks.objects.filter(employee_band = "S", emp_id__in = emp_s).values_list('emp_id', flat=True).distinct()
                    for x in emps_s:
                        if x['emp_id'] in query_emp_entries_s:
                            x['status'] = "Completed"
                        else:
                            x['status'] = "Pending"
                    emp_count_s_filled =  len(query_emp_entries_s)

                    ############## APPROVAL STATUS ##################

                    query_emp_entries_st = hodrecommendatedamount.objects.filter(emp_id__in = emp_s).values_list('emp_id', flat=True).distinct()
                    query_emp_entries_st2 = AarPart2MarksDir.objects.filter(emp_id__in = emp_s).values_list('emp_id', flat=True).distinct()
                    for x in emps_s:
                        if x['emp_id'] in query_emp_entries_st:
                            x['hod_status'] = "Completed"
                        else:
                            x['hod_status'] = "Pending"

                        if x['emp_id'] in query_emp_entries_st2:
                            x['admin_status'] = "Completed"
                        else:
                            x['admin_status'] = "Pending"
                    ##################################################
                   

                    filled = {"a_band_filled":emp_count_a_filled,"s_band_filled":emp_count_s_filled,"emg_band_submit":emp_count_emg_filled}
                    # ##print filled

                    data_values={"message":"Success","total":total, "filled":filled, "employees_a_band":emps_a, "employees_s_band":emps_s,"employees_emg_band":emps_emg}
                    # 
                else:
                    data_values = {"message":"Error"}
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values, status=status, safe=False)


def DirReport(request):
    data5=[]
    data={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:

                if request.method=='GET':
                    data = "Hii"
                    status = 200
                elif request.method == 'POST':
                    data = json.loads(request.body.decode("utf-8"))
                    
                    emg=False
                    if data['ladder'] == 'S':
                        a=[]
                        q_dir_empid = AarPart2MarksDir.objects.values_list('emp_id',flat=True).distinct()
                        emp_data = EmployeePrimdetail.objects.filter(emp_id__in=q_dir_empid).filter(Q(ladder='661')| Q(ladder='662') | Q(ladder='663')).values('emp_id','name','desg__value','dept__value','doj','ladder','desg','emp_category')
                        v=0
                        for i in emp_data:
                            data5.append(i)
                            exp = relativedelta(date.today(), i['doj'])
                            years = exp.years
                            months = exp.months
                            days = exp.days
                            query_research = EmployeeResearch.objects.filter(emp_id=i['emp_id']).values('research_years', 'research_months', 'industry_years', 'industry_months', 'teaching_years', 'teaching_months')

                            total_exp2 = int()
                            total_year = query_research[0]['research_years'] + query_research[0]['industry_years'] + query_research[0]['teaching_years']
                            total_month = query_research[0]['research_months'] + query_research[0]['industry_months'] + query_research[0]['teaching_months']
                            total_year1 = int(years) + int(total_year)
                            total_month1 = int(months) + int(total_month)

                            hod_promoted_to=None
                            dir_promoted_to=None

                            if(total_month1 % 12 == 0):
                                c = total_month1 / 12
                                total_year1 = total_year1 + c
                                total_month1 = 0
                            else:
                                p = total_month1 % 12
                                y = total_month1 / 12
                                total_year1 = total_year1 + y
                                total_month1 = p
                            total_exp = str(total_year1) + " Years " + str(total_month1) + " Months "
                            data5[v]['total_exp']=total_exp
                           

                            query3 = EmployeeAcademic.objects.filter(emp_id=i['emp_id']).values('pass_year_10','pass_year_12','pass_year_dip','pass_year_ug','pass_year_pg','date_doctrate','pass_year_other')
                            high_qual = list(query3)
                            high_qual_list = []
                            for x in high_qual:
                                high_qual_list.append(x['pass_year_10'])
                                high_qual_list.append(x['pass_year_12'])
                                high_qual_list.append(x['pass_year_dip'])
                                high_qual_list.append(x['pass_year_ug'])
                                high_qual_list.append(x['pass_year_pg'])
                                if(x['date_doctrate'] != None):
                                    high_qual_list.append(x['date_doctrate'].year)
                                high_qual_list.append(x['pass_year_other'])
                            qual_arr = ['10th','12th','Diploma','Under Graduate','Post Graduate','Doctrate','Other']
                            highest_qual_year = max(high_qual_list)
                            index1 = high_qual_list.index(highest_qual_year)
                            highest_qual = qual_arr[index1]
                            data5[v]['high_qual']=get_highest_qualification(i['emp_id'])

                            marks = []
                            query5 = AarPart2Marks.objects.filter(emp_id=i['emp_id'],category='H').values('marks','evalution_criteria','remarks1')
                            marks_list = list(query5)
                            for y in marks_list:
                                marks.append(y['marks'])
                                marks.append(y['remarks1'])
                                # marks_obt = marks[y]
                            data5[v]['marks_obt']=marks
                            # data5[v]['remark']=remarks1

                            gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=i['emp_id']).exclude(Status='DELETE').values('Ing_Id_id__Ingredients__value','Value')
                            gross_salary=stored_gross_payable_salary_components(i['emp_id'],getCurrentSession(),date.today().month-3)
                            # #print(gross_salary.query)
                            gross_salary_total = float()
                            basic_agp=0
                            for x in gross_salary:
                                #print(i['emp_id'],x['value'],x['gross_value'])
                                gross_salary_total += x['gross_value']
                                if(x['value']=='BASIC' or x['value']=='AGP'):
                                   basic_agp =basic_agp+x['gross_value']

                            data5[v]['sumBasicAgp']=basic_agp
                            session=getCurrentSession()
                            qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=i['emp_id']).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                            scale_consolidates=qry_gross_value[0]['salary_type__value']
                            proposed_inc = hodrecommendatedamount.objects.filter(emp_id=i['emp_id']).values('amount','increment_type','increment_type__value','status','promoted_to__value','promotion_amount','increment')
                            inc =  list(proposed_inc)
                            #print inc
                            if scale_consolidates == 'CONSOLIDATE':
                                for j in inc:
                                    data5[v]['increment_type__value']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary)
                                            for a in value:
                                                propose_increment = a['value']
                                                proposed_increment = (gross_salary_total * 8)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment = 0

                                        hod_promoted_to = j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment = 0
                                    status1 = j['status']
                            elif scale_consolidates == 'GRADE':
                                for j in inc:
                                    data5[v]['increment_type__value']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary)
                                            for a in value:
                                                propose_increment = a['value']
                                                #proposed_increment = (basic_agp * 3)/100
                                                proposed_increment = (gross_salary_total * 3)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment = 0
                                        hod_promoted_to = j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment = 0
                                    status1 = j['status']
                            proposed_inc_dir = AarPart2MarksDir.objects.filter(emp_id=i['emp_id']).values('amount','increment_type','increment_type__value','increment_type','status','promoted_to__value','promotion_amount','increment','remarks')
                            inc_dir =  list(proposed_inc_dir)
                            if scale_consolidates == 'CONSOLIDATE':
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remarks_dir = '--'
                                for j in inc_dir:
                                    data5[v]['increment_type_dir']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary_dir = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary_dir)
                                            for a in value:
                                                propose_increment_dir = a['value']
                                                proposed_increment_dir = (gross_salary_total * 8)/100
                                        if j['increment_type'] == 277:
                                            # #print "tanya"
                                            proposed_increment_dir = j['amount']
                                            # #print proposed_increment_dir
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment_dir = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment_dir = 0
                                        dir_promoted_to = j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment_dir = 0
                                    status2 = j['status']
                                    remarks_dir = j['remarks']
                            elif scale_consolidates == 'GRADE':
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remarks_dir = '--'
                                for j in inc_dir:
                                    data5[v]['increment_type_dir']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary_dir = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary_dir)
                                            for a in value:
                                                propose_increment_dir = a['value']
                                                #proposed_increment_dir = (basic_agp * 3)/100
                                                proposed_increment_dir = (gross_salary_total * 3)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment_dir = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment_dir = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment_dir = 0
                                        dir_promoted_to = j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment_dir = 0
                                    else:
                                        proposed_increment_dir = '--'
                                    status2 = j['status']
                                    remarks_dir = j['remarks']
                            else:
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remark_dir = '--'
                            data5[v]['gross_salary']= gross_salary_total
                            data5[v]['scale']=scale_consolidates
                            data5[v]['proposed_increment'] = proposed_increment
                            data5[v]['status1'] = status1
                            data5[v]['hod_promoted_to']=hod_promoted_to
                            data5[v]['dir_promoted_to'] = dir_promoted_to
                            data5[v]['proposed_increment_dir'] = proposed_increment_dir
                            data5[v]['status2'] = status2
                            data5[v]['remarks_dir'] = remarks_dir

                            query_previous_increment = AarPrevious_increment.objects.filter(Emp_Id=i['emp_id']).values()
                            if len(query_previous_increment)>0:
                                for ke,va in query_previous_increment[0].iteritems():
                                    data5[v][ke] = va
                            v+=1
                        status = 200
                        data1 = list(emp_data)
                    if data['ladder'] == 'A':
                        a=[]
                        q_dir_empid = AarPart2MarksDir.objects.values_list('emp_id',flat=True).distinct()
                        
                        emp_data = EmployeePrimdetail.objects.filter(emp_id__in=q_dir_empid).filter(Q(ladder='591')| Q(ladder='592') | Q(ladder='593') | Q(ladder='658')| Q(ladder='659') | Q(ladder='660')).values('emp_id','name','desg__value','dept__value','doj','ladder','desg','emp_category')
                        # emp_data = EmployeePrimdetail.objects.filter(emp_id__in=q_dir_empid).filter(ladder__value__contains='A').values('emp_id','name','desg__value','dept__value','doj','ladder','desg','emp_category')
                        
                        print(emp_data)
                        v=0
                        for i in emp_data:
                            data5.append(i)
                            exp = relativedelta(date.today(), i['doj'])
                            years = exp.years
                            months = exp.months
                            days = exp.days
                            query_research = EmployeeResearch.objects.filter(emp_id=i['emp_id']).values('research_years', 'research_months', 'industry_years', 'industry_months', 'teaching_years', 'teaching_months')

                            hod_promoted_to=None
                            dir_promoted_to=None

                            total_exp2 = int()
                            total_year = query_research[0]['research_years'] + query_research[0]['industry_years'] + query_research[0]['teaching_years']
                            total_month = query_research[0]['research_months'] + query_research[0]['industry_months'] + query_research[0]['teaching_months']
                            total_year1 = int(years) + int(total_year)
                            total_month1 = int(months) + int(total_month)
                            if(total_month1 % 12 == 0):
                                c = total_month1 / 12
                                total_year1 = total_year1 + c
                                total_month1 = 0
                            else:
                                p = total_month1 % 12
                                y = total_month1 / 12
                                total_year1 = total_year1 + y
                                total_month1 = p
                            total_exp = str(total_year1) + " Years " + str(total_month1) + " Months "
                            data5[v]['total_exp']=total_exp
                           

                            query3 = EmployeeAcademic.objects.filter(emp_id=i['emp_id']).values('pass_year_10','pass_year_12','pass_year_dip','pass_year_ug','pass_year_pg','date_doctrate','pass_year_other')
                            high_qual = list(query3)
                            high_qual_list = []
                            for x in high_qual:
                                high_qual_list.append(x['pass_year_10'])
                                high_qual_list.append(x['pass_year_12'])
                                high_qual_list.append(x['pass_year_dip'])
                                high_qual_list.append(x['pass_year_ug'])
                                high_qual_list.append(x['pass_year_pg'])
                                if(x['date_doctrate'] != None):
                                    high_qual_list.append(x['date_doctrate'].year)
                                high_qual_list.append(x['pass_year_other'])
                            qual_arr = ['10th','12th','Diploma','Under Graduate','Post Graduate','Doctrate','Other']
                            highest_qual_year = max(high_qual_list)
                            index1 = high_qual_list.index(highest_qual_year)
                            highest_qual = qual_arr[index1]
                            data5[v]['high_qual']=get_highest_qualification(i['emp_id'])

                            marks = []
                            query5 = AarPart2Marks.objects.filter(emp_id=i['emp_id'],category='H').values('marks','evalution_criteria','remarks1')
                            marks_list = list(query5)
                            for y in marks_list:
                                marks.append(y['marks'])
                                marks.append(y['remarks1'])
                                # marks_obt = marks[y]
                            data5[v]['marks_obt']=marks
                            # data5[v]['remark']=remarks1

                            gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=i['emp_id']).exclude(Status='DELETE').values('Ing_Id_id__Ingredients__value','Value')

                            gross_salary=stored_gross_payable_salary_components(i['emp_id'],getCurrentSession(),date.today().month-3)
                            # #print(gross_salary.query)
                            gross_salary_total = float()
                            basic_agp=0
                            for x in gross_salary:
                                #print(i['emp_id'],x['value'],x['gross_value'])
                                gross_salary_total += x['gross_value']
                                if(x['value']=='BASIC' or x['value']=='AGP'):
                                   basic_agp =basic_agp+x['gross_value']

                            data5[v]['sumBasicAgp']=basic_agp
                            session=getCurrentSession()
                            qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=i['emp_id']).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                            scale_consolidates=qry_gross_value[0]['salary_type__value']
                            proposed_inc = hodrecommendatedamount.objects.filter(emp_id=i['emp_id']).values('amount','increment_type','increment_type__value','increment_type','status','promoted_to__value','promotion_amount','increment')
                            inc =  list(proposed_inc)
                            if scale_consolidates == 'CONSOLIDATE':
                                for j in inc:
                                    data5[v]['increment_type__value']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary)
                                            for a in value:
                                                propose_increment = a['value']
                                                proposed_increment = (gross_salary_total * 8)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment = 0
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment = 0
                                    hod_promoted_to=j['promoted_to__value']
                                    status1 = j['status']
                            elif scale_consolidates == 'GRADE':
                                for j in inc:
                                    data5[v]['increment_type__value']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary)
                                            for a in value:
                                                propose_increment = a['value']
                                                #proposed_increment = (basic_agp * 3)/100
                                                proposed_increment = (gross_salary_total * 3)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment = 0
                                        hod_promoted_to=j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment = 0
                                    status1 = j['status']
                            proposed_inc_dir = AarPart2MarksDir.objects.filter(emp_id=i['emp_id']).values('amount','increment_type','increment_type__value','status','promoted_to__value','promotion_amount','increment','remarks')
                            inc_dir =  list(proposed_inc_dir)
                            if scale_consolidates == 'CONSOLIDATE':
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remarks_dir = '--'
                                for j in inc_dir:
                                    data5[v]['increment_type_dir']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary_dir = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary_dir)
                                            for a in value:
                                                propose_increment_dir = a['value']
                                                proposed_increment_dir = (gross_salary_total * 8)/100
                                        if j['increment_type'] == 277:
                                            # #print "tanya"
                                            proposed_increment_dir = j['amount']
                                            # #print proposed_increment_dir
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment_dir = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment_dir = 0
                                        dir_promoted_to=j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment_dir = 0
                                    status2 = j['status']
                                    remarks_dir = j['remarks']
                            elif scale_consolidates == 'GRADE':
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remarks_dir = '--'
                                for j in inc_dir:
                                    data5[v]['increment_type_dir']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary_dir = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary_dir)
                                            for a in value:
                                                propose_increment_dir = a['value']
                                                #proposed_increment_dir = (basic_agp * 3)/100
                                                proposed_increment_dir = (gross_salary_total * 3)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment_dir = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment_dir = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment_dir = 0
                                        dir_promoted_to=j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment_dir = 0
                                    else:
                                        proposed_increment_dir = '--'
                                    status2 = j['status']
                                    remarks_dir = j['remarks']
                            else:
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remark_dir = '--'
                            data5[v]['gross_salary']= gross_salary_total
                            data5[v]['scale']=scale_consolidates
                            data5[v]['proposed_increment'] = proposed_increment
                            data5[v]['status1'] = status1
                            data5[v]['hod_promoted_to']=hod_promoted_to
                            data5[v]['dir_promoted_to'] = dir_promoted_to
                            data5[v]['proposed_increment_dir'] = proposed_increment_dir
                            data5[v]['status2'] = status2
                            data5[v]['remarks_dir'] = remarks_dir

                            query_previous_increment = AarPrevious_increment.objects.filter(Emp_Id=i['emp_id']).values()
                            if len(query_previous_increment)>0:
                                for ke,va in query_previous_increment[0].iteritems():
                                    data5[v][ke] = va
                            v+=1


                        status = 200
                        data1 = list(emp_data)
                    if data['ladder'] == 'E':
                        emg=True
                        a=[]

                        q_dir_empid = AarPart2MarksDir.objects.values_list('emp_id',flat=True).distinct()
                        print(q_dir_empid.query)
                        emp_data = EmployeePrimdetail.objects.filter(emp_id__in=q_dir_empid).filter(cadre__in = [667,668,669,645,643,644],emp_status='ACTIVE').values('emp_id','name','desg__value','dept__value','doj','ladder','desg','emp_category')
                        v=0
                        for i in emp_data:
                            data5.append(i)
                            exp = relativedelta(date.today(), i['doj'])
                            years = exp.years
                            months = exp.months
                            days = exp.days
                            query_research = EmployeeResearch.objects.filter(emp_id=i['emp_id']).values('research_years', 'research_months', 'industry_years', 'industry_months', 'teaching_years', 'teaching_months')
                            
                            hod_promoted_to=None
                            dir_promoted_to=None

                            total_exp2 = int()
                            v1=0
                            v2=0
                            v3=0
                            v4=0
                            v5=0
                            v6=0
                            if query_research[0]['research_years'] is not None:
                                v1=query_research[0]['research_years']
                            
                            if query_research[0]['industry_years'] is not None:
                                v2=query_research[0]['industry_years']
                            
                            if query_research[0]['teaching_years'] is not None:
                                v3=query_research[0]['teaching_years']
                            
                            if query_research[0]['research_months'] is not None:
                                v4=query_research[0]['research_months']
                            
                            if query_research[0]['industry_months'] is not None:
                                v5=query_research[0]['industry_months']
                            
                            if query_research[0]['teaching_months'] is not None:
                                v6=query_research[0]['teaching_months']
                            total_year = v1 + v2 + v3
                            total_month = v4 + v5 + v6
                            total_year1 = int(years) + int(total_year)
                            total_month1 = int(months) + int(total_month)
                            if(total_month1 % 12 == 0):
                                c = total_month1 / 12
                                total_year1 = total_year1 + c
                                total_month1 = 0
                            else:
                                p = total_month1 % 12
                                y = total_month1 / 12
                                total_year1 = total_year1 + y
                                total_month1 = p
                            total_exp = str(total_year1) + " Years " + str(total_month1) + " Months "
                            data5[v]['total_exp']=total_exp
                           

                            query3 = EmployeeAcademic.objects.filter(emp_id=i['emp_id']).values('pass_year_10','pass_year_12','pass_year_dip','pass_year_ug','pass_year_pg','date_doctrate','pass_year_other')
                            high_qual = list(query3)
                            high_qual_list = []
                            for x in high_qual:
                                high_qual_list.append(x['pass_year_10'])
                                high_qual_list.append(x['pass_year_12'])
                                high_qual_list.append(x['pass_year_dip'])
                                high_qual_list.append(x['pass_year_ug'])
                                high_qual_list.append(x['pass_year_pg'])
                                if(x['date_doctrate'] != None):
                                    high_qual_list.append(x['date_doctrate'].year)
                                high_qual_list.append(x['pass_year_other'])
                            qual_arr = ['10th','12th','Diploma','Under Graduate','Post Graduate','Doctrate','Other']
                            highest_qual_year = max(high_qual_list)
                            index1 = high_qual_list.index(highest_qual_year)
                            highest_qual = qual_arr[index1]
                            data5[v]['high_qual']=get_highest_qualification(i['emp_id'])

                            marks = []
                            query5 = AarPart2Marks.objects.filter(emp_id=i['emp_id'],category='H').values('marks','evalution_criteria','remarks1')
                            marks_list = list(query5)
                            for y in marks_list:
                                marks.append(y['marks'])
                                marks.append(y['remarks1'])
                                # marks_obt = marks[y]

                            if i['emp_id'] == '13320':
                                #print(marks)
                                print(marks)
                            data5[v]['marks_obt']=marks
                            # data5[v]['remark']=remarks1

                            
                            # gross_salary = EmployeeGross_detail.objects.filter(Emp_Id=i['emp_id']).exclude(Status='DELETE').values('Ing_Id_id__Ingredients__value','Value')
                            gross_salary=stored_gross_payable_salary_components(i['emp_id'],getCurrentSession(),date.today().month-3)
                            #if i['emp_id'] == '20857':
                            print(gross_salary)
                            # #print(gross_salary.query)
                            gross_salary_total = float()
                            basic_agp=0
                            for x in gross_salary:
                                #print(i['emp_id'],x['value'],x['gross_value'])
                                gross_salary_total += x['gross_value']
                                if(x['value']=='BASIC' or x['value']=='AGP'):
                                   basic_agp =basic_agp+x['gross_value']

                            data5[v]['sumBasicAgp']=basic_agp
                            # #print(gross_data)
                            session=getCurrentSession()
                            qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=i['emp_id']).filter(session=AccountsSession.objects.get(id=session)).exclude(Status="DELETE").values('salary_type__value')
                            if len(qry_gross_value) == 0:
                                scale_consolidates = '--'
                            else:
                                scale_consolidates=qry_gross_value[0]['salary_type__value']
                            proposed_inc = hodrecommendatedamount.objects.filter(emp_id=i['emp_id']).values('amount','increment_type','increment_type__value','status','promoted_to__value','promotion_amount','increment')
                            inc =  list(proposed_inc)
                            if scale_consolidates == 'CONSOLIDATE':
                                proposed_increment='--'
                                status1='--'
                                for j in inc:
                                    data5[v]['increment_type__value']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary)
                                            for a in value:
                                                propose_increment = a['value']
                                                proposed_increment = (gross_salary_total * 8)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':

                                        if j['increment'] == 'Y':
                                            proposed_increment = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment = 0
                                        hod_promoted_to=j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment = 0
                                    status1 = j['status']
                            elif scale_consolidates == 'GRADE':
                                proposed_increment='--'
                                status1='--'
                                for j in inc:
                                    data5[v]['increment_type__value']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary)
                                            for a in value:
                                                propose_increment = a['value']
                                                #proposed_increment = (basic_agp * 3)/100
                                                proposed_increment = (gross_salary_total * 3)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment = 0
                                        hod_promoted_to=j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment = 0
                                    status1 = j['status']
                            proposed_inc_dir = AarPart2MarksDir.objects.filter(emp_id=i['emp_id']).values('amount','increment_type','increment_type__value','status','promoted_to__value','promotion_amount','increment','remarks')
                            inc_dir =  list(proposed_inc_dir)
                            if scale_consolidates == 'CONSOLIDATE':
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remarks_dir = '--'
                                for j in inc_dir:
                                    data5[v]['increment_type_dir']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary_dir = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary_dir)
                                            for a in value:
                                                propose_increment_dir = a['value']
                                                proposed_increment_dir = (gross_salary_total * 8)/100
                                        if j['increment_type'] == 277:
                                            # #print "tanya"
                                            proposed_increment_dir = j['amount']
                                            # #print proposed_increment_dir
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment_dir = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment_dir = 0
                                        dir_promoted_to=j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment_dir = 0
                                    status2 = j['status']
                                    remarks_dir = j['remarks']
                            elif scale_consolidates == 'GRADE':
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remarks_dir = '--'
                                for j in inc_dir:
                                    data5[v]['increment_type_dir']= j['increment_type__value']
                                    if j['status'] == 'INCREMENT':
                                        if j['increment_type'] == 276:
                                            proposed_salary_dir = AarIncrementSettings.objects.filter(ladder = i['ladder'],desg = i['desg'],emp_category = i['emp_category']).values('value')
                                            value = list(proposed_salary_dir)
                                            for a in value:
                                                propose_increment_dir = a['value']
                                                #proposed_increment_dir = (basic_agp * 3)/100
                                                proposed_increment_dir = (gross_salary_total * 3)/100
                                        if j['increment_type'] == 277:
                                            proposed_increment_dir = j['amount']
                                            # #print "hiiiiiiiiii"
                                    elif j['status'] == 'PROMOTION':
                                        if j['increment'] == 'Y':
                                            proposed_increment_dir = j['promotion_amount']
                                        elif j['increment'] == 'N':
                                            proposed_increment_dir = 0
                                        dir_promoted_to=j['promoted_to__value']
                                    elif j['status'] == 'NO INCREMENT':
                                        proposed_increment_dir = 0
                                    else:
                                        proposed_increment_dir = '--'
                                    status2 = j['status']
                                    remarks_dir = j['remarks']
                            else:
                                proposed_increment_dir = '--'
                                status2 = '--'
                                remark_dir = '--'
                            data5[v]['gross_salary']= gross_salary_total
                            data5[v]['scale']=scale_consolidates
                            data5[v]['hod_promoted_to']=hod_promoted_to
                            data5[v]['dir_promoted_to'] = dir_promoted_to
                            data5[v]['proposed_increment'] = proposed_increment
                            data5[v]['status1'] = status1
                            data5[v]['proposed_increment_dir'] = proposed_increment_dir
                            data5[v]['status2'] = status2
                            data5[v]['remarks_dir'] = remarks_dir

                            query_previous_increment = AarPrevious_increment.objects.filter(Emp_Id=i['emp_id']).values()
                            if len(query_previous_increment)>0:
                                for ke,va in query_previous_increment[0].iteritems():
                                    data5[v][ke] = va
                            v+=1

                            
                    data = {'data':list(data5),'isemg':emg}
                    status = 200
                    data1 = list(emp_data)
                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500

    return JsonResponse(data=data,status=status,safe=False)


def aar_emp_end_report(request):
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])

            if(check == 200):
                if(request.method=='GET'):
                    q=AarDropdown.objects.filter(pid=0,value=None,type='I').values('field','sno')
                    data_values={'data':list(q)}
                    status=200
                if(request.method=='POST'):
                    data=json.loads(request.body)
                    emp_id = request.session['hash1']
                    if(data['type']=='1'):
                        retrieve_data=[] 
                        query_data=Researchjournal.objects.filter(emp_id=emp_id).exclude(approve_status='PENDING').exclude(approve_status='DELETE').values('emp_id__name','paper_title','id','emp_id','emp_id__name','approve_status','category__value','type_of_journal__value','published_date','journal_name','volume_no','issue_no','isbn','author__value','emp_id__dept__value','page_no','publisher_name','publisher_contact','publisher_email','publisher_website')
                        if(query_data.count()>0):
                            j=0
                            for i in query_data:
                                d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'category':i['category__value'],'journal_type':i['type_of_journal__value'],'publish_date':i['published_date'],'journal_name':i['journal_name'],'volume_no':i['volume_no'],'issue_no':i['issue_no'],'isbn':i['isbn'],'author':i['author__value'],'dept':i['emp_id__dept__value'],'page_no':i['page_no'],'publisher_name':i['publisher_name'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website']}
                                retrieve_data.append(d)
                                retrieve_data[j]['sno']=j+1
                                j=j+1
                    elif(data['type']=='2'):
                        retrieve_data=[]
                        query_data=Researchconference.objects.filter(emp_id=emp_id).exclude(approve_status='PENDING').exclude(approve_status='DELETE').values('emp_id__name','paper_title','id','emp_id','approve_status','category__value','type_of_conference__value','conference_title','published_date','organized_by','author__value','conference_from','conference_to','publisher_name','emp_id__dept__value','journal_name','sub_category__value','isbn','issue_no','page_no','publisher_website','publisher_contact','publisher_email')
                        if(query_data.count()>0):
                            j=0
                            for i in query_data:
                                d={'title':i['paper_title'],'id':i['id'],'emp_id':i['emp_id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'category':i['category__value'],'conference_type':i['type_of_conference__value'],'conference_title':i['conference_title'],'publish_date':i['published_date'],'organized_by':i['organized_by'],'author':i['author__value'],'conference_from':i['conference_from'],'conference_to':i['conference_to'],'publisher_name':i['publisher_name'],'dept':i['emp_id__dept__value'],'sub_category':i['sub_category__value'],'isbn':i['isbn'],'issue_no':i['issue_no'],'page_no':i['page_no'],'publisher_email':i['publisher_email'],'publisher_contact':i['publisher_contact'],'publisher_website':i['publisher_website']}
                                retrieve_data.append(d)
                                retrieve_data[j]['sno']=j+1
                                j=j+1
                    elif(data['type']=='3'):
                        retrieve_data=[]  
                        query_data=Books.objects.filter(emp_id=emp_id).exclude(approve_status='PENDING').exclude(approve_status='DELETE').values('emp_id__name','title','id','emp_id','approve_status','role__value','role_for__value','publisher_type','edition','published_date','chapter','isbn','copyright_status','copyright_no','author__value','publisher_name','emp_id__dept__value','publisher_website','publisher_contact','publisher_email')
                        if(query_data.count()>0):
                            j=0
                            for i in query_data:
                                d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'role':i['role__value'],'role_for':i['role_for__value'],'publisher_type':i['publisher_type'],'edition':i['edition'],'publish_date':i['published_date'],'chapter':i['chapter'],'isbn':i['isbn'],'copyright_status':i['copyright_status'],'copyright_no':i['copyright_no'],'author':i['author__value'],'publisher_name':i['publisher_name'],'dept':i['emp_id__dept__value'],'publisher_contact':i['publisher_contact'],'publisher_email':i['publisher_email'],'publisher_website':i['publisher_website']}
                                retrieve_data.append(d)
                                retrieve_data[j]['sno']=j+1
                                j=j+1
                    elif(data['type']=='4'):
                        retrieve_data=[] 
                        query_data=Researchguidence.objects.filter(emp_id=emp_id).exclude(approve_status='PENDING').exclude(approve_status='DELETE').values('emp_id__name','project_title','id','emp_id','approve_status','guidence__value','course__value','degree__value','no_of_students','degree_awarded','uni_type__value','uni_name','status__value','area_of_spec','emp_id__dept__value')
                        if(query_data.count()>0):
                            j=0
                            for i in query_data:
                                d={'title':i['project_title'],'id':i['id'],'emp_id':i['emp_id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'guidence':i['guidence__value'],'course':i['course__value'],'degree_awarded':i['degree_awarded'],'degree':i['degree__value'],'no_of_students':i['no_of_students'],'uni_type':i['uni_type__value'],'uni_name':i['uni_name'],'status':i['status__value'],'area_of_spec':i['area_of_spec'],'dept':i['emp_id__dept__value']}
                                retrieve_data.append(d)
                                retrieve_data[j]['sno']=j+1
                                j=j+1
                    elif(data['type']=='5'):
                        retrieve_data=[]
                        query_data=Patent.objects.filter(emp_id=emp_id).exclude(approve_status='PENDING').exclude(approve_status='DELETE').values('emp_id__name','title','id','emp_id','approve_status','descreption','collaboration','company_name','incorporate_status__value','status','date','owner__value','emp_id__dept__value','number')
                        if(query_data.count()>0):
                            j=0
                            for i in query_data:
                                d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'descreption':i['descreption'],'collaboration':i['collaboration'],'company_name':i['company_name'],'incorporate_status':i['incorporate_status__value'],'status':i['status'],'date':i['date'],'owner':i['owner__value'],'dept':i['emp_id__dept__value'],'number':i['number']}
                                retrieve_data.append(d)
                                retrieve_data[j]['sno']=j+1
                                j=j+1
                    elif(data['type']=='6'):
                        retrieve_data=[]
                        query_data=ProjectConsultancy.objects.filter(emp_id=emp_id).exclude(approve_status='PENDING').exclude(approve_status='DELETE').values('emp_id__name','title','id','emp_id','emp_id__name','approve_status','type__value','status__value','sector__value','start_date','end_date','principal_investigator','co_principal_investigator','sponsored','team_size','association','emp_id__dept__value','team_size')
                        if(query_data.count()>0):
                            j=0
                            for i in query_data:
                                d={'title':i['title'],'id':i['id'],'emp_id':i['emp_id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'type__value':i['type__value'],'status__value':i['status__value'],'sector__value':i['sector__value'],'start_date':i['start_date'],'end_date':i['end_date'],'principal_investigator':i['principal_investigator'],'co_principal_investigator':i['co_principal_investigator'],'sponsored':i['sponsored'],'team_size':i['team_size'],'association':i['association'],'dept':i['emp_id__dept__value']}
                                retrieve_data.append(d)
                                retrieve_data[j]['sno']=j+1
                                j=j+1
                    elif(data['type']=='7'):
                        retrieve_data=[]
                        query_data=TrainingDevelopment.objects.filter(emp_id=emp_id).exclude(approve_status='PENDING').exclude(approve_status='DELETE').values('emp_id__name','title','id','emp_id','approve_status','category__value','type__value','from_date','to_date','role__value','organization_sector__value','incorporation_status__value','venue','participants','organizers','attended','collaborations','sponsership','emp_id__dept__value')
                        if(query_data.count()>0):
                            j=0
                            for i in query_data:
                                d={'title':i['title'],'id':i['id'],'name':i['emp_id__name'],'emp_id':i['emp_id'],'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'role':i['role__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaborations':i['collaborations'],'sponsership':i['sponsership'],'dept':i['emp_id__dept__value']}
                                retrieve_data.append(d)
                                retrieve_data[j]['sno']=j+1
                                j=j+1

                    elif(data['type']=='8'):
                        retrieve_data=[]
                        query_data=LecturesTalks.objects.filter(emp_id=emp_id).exclude(approve_status='PENDING').exclude(approve_status='DELETE').values('emp_id__name','topic','id','emp_id','approve_status','category__value','type__value','role__value','organization_sector__value','incorporation_status__value','venue','participants','emp_id__dept__value','e_mail','website','contact_number')
                        if(query_data.count()>0):
                            j=0
                            for i in query_data:
                                d={'title':i['topic'],'id':i['id'],'emp_id':i['emp_id'],'name':i['emp_id__name'],'approve_status':i['approve_status'],'category':i['category__value'],'type':i['type__value'],'organization_sector':i['organization_sector__value'],'incorporation_status':i['incorporation_status__value'],'venue':i['venue'],'participants':i['participants'],'role':i['role__value'],'dept':i['emp_id__dept__value'],'e_mail':i['e_mail'],'website':i['website'],'contact_number':i['contact_number']}
                                retrieve_data.append(d)
                                retrieve_data[j]['sno']=j+1
                                j=j+1
                    data_values={'data':retrieve_data}
                    status=200
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values,safe=False,status=status)
