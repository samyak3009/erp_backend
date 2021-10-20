# -*- coding: utf-8 -*-
import copy
import json
import datetime
import calendar
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from datetime import date
from random import randint
# Imports for the Models
from django.contrib.auth.models import User
from Accounts.models import AccountsDropdown, EmployeeGross_detail,AccountsSession,MonthlyPayable_detail
from DepartmentalAchievement.models import *
from login.models import AarDropdown,EmployeeDropdown
from musterroll.models import EmployeePrimdetail, EmployeeResearch, EmployeeAcademic, Reporting, AarReporting
# Imports for the Views
from login.views import checkpermission

def GuestLecture(request):
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
                elif(request.method=='GET'):
                    if 'id' in request.GET:
                        Q=guestLectures.objects.filter(id=request.GET['id'],status="INSERT").values('id','t_date','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','date','topic','speaker','designation','organization','speaker_profile','contact_number','e_mail','participants_no','remark')
                        if len(Q) > 0:
                            Q[0]['department']=list(AarMultiselect.objects.filter(type="GUEST LECTURE",field="DEPARTMENT",sno=request.GET['id']).values_list('value',flat=True))
                            Q[0]['year']=list(AarMultiselect.objects.filter(type="GUEST LECTURE",field="YEAR",sno=request.GET['id']).values_list('value',flat=True))
                        data_values={'data':list(Q)}
                    elif 'by' in request.GET:
                        Q=guestLectures.objects.exclude(status="DELETE").values('id','t_date','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','date','topic','speaker','designation','organization','speaker_profile','contact_number','e_mail','participants_no','remark')
                        data_values={'data':list(Q)}
                    else:
                        d=AarDropdown.objects.filter(field="GUEST LECTURE").exclude(value=None).values('sno','value')
                        data_values=list(EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value=None).values('sno','value'))
                        status=200
                elif(request.method=='PUT'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
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
                        ##print data
                        d1=date.split('T')
                        date=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        c=guestLectures.objects.filter(emp_id=emp_id,topic=topic).exclude(status="DELETE").exclude(id=data['id']).count()
                        if c==0:
                            guestLectures.objects.filter(id=data['id']).update(status="DELETE")
                            Q=guestLectures.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),remark=remark,participants_no=participants_no,e_mail=e_mail,contact_number=contact_number,speaker_profile=speaker_profile,organization=organization,date=date,topic=topic,speaker=speaker,designation=designation)
                            sno=Q.pk
                            for i in dept:
                                AarMultiselect.objects.create(type="GUEST LECTURE",field="DEPARTMENT",value=i,emp_id=emp_id,sno=sno)
                            for i in year:
                                AarMultiselect.objects.create(type="GUEST LECTURE",field="YEAR",value=i,emp_id=emp_id,sno=sno)
                                data_values={"ok":"data updated"}
                                status=200
                            else:
                                data_values={"ok":"duplicate data"}
                elif(request.method == 'DELETE'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
                        guestLectures.objects.filter(id=data['id']).update(status="DELETE")
                        data_values={"ok":"data deleted"}
                        status=200
                        # else:
                        #     data_values={"ok":"duplicate data"}

                else:
                    status=502
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data=data_values,safe=False)

def IndustrialVisit(request):
    data_values=""
    data=""
    data_values={}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                # if(request.method=='GET'):
                #     dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                #     emp=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('name','emp_id')

                #     data_values=list(emp)
                #     status=200
                if(request.method=='POST'):
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
                

                elif(request.method=='GET'):
                    if 'id' in request.GET:
                        Q=list(industrialVisit.objects.filter(id=request.GET['id']).values('id','t_date','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','date','industry','address','contact_person','contact_number','e_mail','participants_no','remark'))
                        #Q[0]['coord']=AarMultiselect.objects.filter(sno=request.GET['id']).values('sno','type','field','value','emp_id')
                        Q[0]['coord']=list(AarMultiselect.objects.filter(type="INDUSTRIAL VISIT",field="FACULTY COORDINATOR",sno=request.GET['id']).values_list('value',flat=True))
                        Q[0]['year']=list(AarMultiselect.objects.filter(type="INDUSTRIAL VISIT",field="YEAR",sno=request.GET['id']).values_list('value',flat=True))

                        data_values={'data':list(Q)}
                    elif 'by' in request.GET:
                        Q=industrialVisit.objects.exclude(status="DELETE").values('id','t_date','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','date','industry','address','contact_person','contact_number','e_mail','participants_no','remark')
                        data_values={'data':list(Q)}
                    else:
                        d=AarDropdown.objects.filter(field="INDUSTRIAL VISIT").exclude(value=None).values('sno','value')
                        dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                        emp=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('name','emp_id')
                        data_values={'data1':list(d),'data2':list(emp)}
                    status=200
                elif(request.method=='PUT'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
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
                            faculty_coordinator=[]
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
                            year=[]
                        if 'e_mail' in data:
                            e_mail=data['e_mail']
                        else:
                            e_mail=None
                        ##print data
                        d1=date.split('T')
                        date=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        #dup=industrialVisit.objects.filter(industry=industry,emp_id=emp_id)
                        c=industrialVisit.objects.filter(industry=industry,emp_id=emp_id).exclude(status="DELETE").exclude(id=data['id']).count()
                        if c==0:
                            industrialVisit.objects.filter(id=data['id']).update(status="DELETE")
                            Q=industrialVisit.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),industry=data['industry'],address=address,contact_person=contact_person,contact_number=contact_number,e_mail=e_mail,remark=remark,date=date,participants_no=participants_no)
                            sno=Q.pk
                            for i in faculty_coordinator:
                                AarMultiselect.objects.create(type="INDUSTRIAL VISIT",field="FACULTY COORDINATOR",value=i,emp_id=emp_id,sno=sno)
                            for i in year:
                                AarMultiselect.objects.create(type="INDUSTRIAL VISIT",field="YEAR",value=i,emp_id=emp_id,sno=sno)
                            data_values={"ok":"data updated"}
                            status=200
                        else:
                            data_values={"ok":"duplicate data"}
                elif(request.method == 'DELETE'):
                    data=json.loads(request.body.decode("utf-8"))
                    if 'id' in data:
                        q=industrialVisit.objects.filter(id=data['id']).update(status="DELETE")
                        print(q)
                        data_values={"ok":"data deleted"}
                        status=200
                        # else:
                        #     data_values={"ok":"duplicate data"}

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
                    if 'id' in request.GET:
                        q2=list(eventsorganized.objects.filter(id=request.GET['id']).values('id','emp_id','category','type','from_date','to_date','organization_sector','incorporation_status','title','venue','participants','organizers','attended','collaboration','sponsership','description','t_date','status'))
                        sno=request.GET['id']
                        q2[0]['discipline']=list(AarMultiselect.objects.filter(type="EVENTS_ORGANIZED",field="DISCIPLINE",sno=sno).values_list('value',flat=True))
                        if(q2[0]['sponsership']=="Yes"):
                            q2[0]['sponsers_list']=list(Sponsers.objects.filter(spons_id=sno,emp_id=emp_id,type="EVENTS",field_type='SPONSOR').values('sponser_name','type','contact_person','contact_number','e_mail','website','amount','address','pin_code','field_type'))
                        if(q2[0]['collaboration']=="Yes"):
                            q2[0]['collab_list']=list(Sponsers.objects.filter(spons_id=sno,emp_id=emp_id,type="EVENTS",field_type='COLLABORATION').values('sponser_name','type','contact_person','contact_number','e_mail','website','amount','address','pin_code','field_type'))
                        data_values={'data':list(q2)}
                        status=200
                    elif 'by' in request.GET:
                        q2=eventsorganized.objects.exclude(status="DELETE").values('id','emp_id','category','category__value','type','type__value','from_date','to_date','organization_sector','organization_sector__value','incorporation_status','incorporation_status__value','title','venue','participants','organizers','attended','collaboration','sponsership','description','t_date','status')
                        data_values={'data':list(q2)}
                        status=200
                    else:
                        q1=AarDropdown.objects.filter(field="EVENTS_ORGANIZED").exclude(value=None).values('sno','value')
                        a=[]
                        for i in q1:
                            q2=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('value','sno')
                            a.append({i['value']:list(q2)})
                        q2=EmployeeDropdown.objects.filter(field='DEPARTMENT').exclude(value=None).values('sno','value')
                        data_values={'data':a,'data1':list(q2)}
                        status=200
                elif(request.method=='DELETE'):
                    data=json.loads(request.body.decode("utf-8"))
                    eventsorganized.objects.filter(id=data['id']).update(status='DELETE')
                    data_values={'msg':'Deleted successfully'}
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
                            type=data['type']
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
                        ##print collaboration
                        d1=from_date.split('T')
                        from_date=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        d2=to_date.split('T')
                        to_date=datetime.datetime.strptime(d2[0],'%Y-%m-%d').date()
                        c=eventsorganized.objects.filter(title=title,emp_id=emp_id).count()
                        if c==0:
                            Q=eventsorganized.objects.create(title=title,venue=venue,sponsership=sponsered,collaboration=collaboration,description=description,attended=attended,organizers=organizers,participants=participants,t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type),from_date=from_date,to_date=to_date,organization_sector=AarDropdown.objects.get(sno=organization_sector),incorporation_status=AarDropdown.objects.get(sno=incorporate_status))
                            sno=Q.pk
                            for i in discipline:
                                AarMultiselect.objects.create(type="EVENTS_ORGANIZED",field="DISCIPLINE",value=i,emp_id=emp_id,sno=sno)
                            if(sponsered=="Yes"):

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
                elif(request.method=='PUT'):
                    data=json.loads(request.body)
                    if data is not None:
                        if 'category' in data:
                            category=data['category']
                        else:
                            category=None
                        if 'type' in data:
                            type=data['type']
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
                            incorporation_status=data['incorporation']
                        else:
                            incorporation_status=None
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
                        if 'sponsered' in data:
                            sponsership=data['sponsered']
                        else:
                            sponsership=None
                        if 'description' in data:
                            description=data['description']
                        else:
                            description=None
                        if 'discipline' in data:
                            discipline=data['discipline']
                        else:
                            discipline=None
                        print(discipline)
                        if 'collaborations' in data:
                            collaborations=data['collaborations']
                        else:
                            collaborations=[]
                        if 'sponsers' in data:
                            sponsers=data['sponsers']
                        else:
                            sponsers=[]
                        d1=from_date.split('T')
                        from_date=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        d2=to_date.split('T')
                        to_date=datetime.datetime.strptime(d2[0],'%Y-%m-%d').date()
                        c=eventsorganized.objects.filter(title=title,emp_id=emp_id).exclude(id=data['id']).exclude(status='DELETE').count()
                        if c==0:
                            eventsorganized.objects.filter(id=data['id']).update(status='DELETE')
                            Q=eventsorganized.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type),organization_sector=AarDropdown.objects.get(sno=organization_sector),incorporation_status=AarDropdown.objects.get(sno=incorporation_status),from_date=from_date,to_date=to_date,title=title,venue=venue,participants=participants,organizers=organizers,attended=attended,collaboration=collaboration,sponsership=sponsership,description=description)
                            sno=Q.pk
                            for i in discipline:
                                AarMultiselect.objects.create(type="EVENTS_ORGANIZED",field="DISCIPLINE",value=i,emp_id=emp_id,sno=sno)
                            if(sponsership=="Yes"):
                                for i in sponsers:
                                    Sponsers.objects.create(spons_id=sno,emp_id=emp_id,sponser_name=i["organisation"],type="EVENTS",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='SPONSOR')
                            if(collaboration=="Yes"):
                                for i in collaborations:
                                    Sponsers.objects.create(spons_id=sno,emp_id=emp_id,sponser_name=i["organisation"],type="EVENTS",contact_person=i['contact_person'],contact_number=i['contact_number'],e_mail=i['e_mail'],website=i['website'],amount=i['amount'],address=i['address'],pin_code=i['pin_code'],field_type='COLLABORATION')
                            data_values={'ok':'data inserted'}
                            status=200
                        else:
                            data_values={'ok':'duplicate'}
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
                        if 'intro' in data:
                            intro=data['intro']
                        else:
                            intro=None
                        d1=valid_upto.split('T')
                        valid_upto=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        d2=date.split('T')
                        date=datetime.datetime.strptime(d2[0],'%Y-%m-%d').date()
                        MouSigned.objects.create(intro=intro,date=date,t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),document=document,e_mail=e_mail,organization=organization,objective=objective,valid_upto=valid_upto,contact_number=contact_number)
                        data_values={'ok':'Successfully added'}
                        status=200
                elif(request.method=='GET'):
                    if 'id' in request.GET:
                        Q=MouSigned.objects.filter(sno=request.GET['id']).values('sno','intro','t_date','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','organization','objective','valid_upto','contact_number','e_mail','document','date')
                        #Q[0]['coord']=AarMultiselect.objects.filter(sno=request.GET['id']).values('sno','type','field','value','emp_id')
                        data_values={'data':list(Q)}
                    elif 'by' in request.GET:
                        Q=MouSigned.objects.exclude(status="DELETE").values('sno','t_date','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','organization','objective','valid_upto','contact_number','e_mail','document','date')
                        data_values={'data':list(Q)}
                    else:
                        d=AarDropdown.objects.filter(field="MOU SIGNED").exclude(value=None).values('sno','value')
                        dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                        emp=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('name','emp_id')
                        data_values={'data1':list(d),'data2':list(emp)}
                    status=200
                elif(request.method=='PUT'):
                    data=json.loads(request.body.decode("utf-8"))
                    if data!=None:
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
                        if 'intro' in data:
                            intro=data['intro']
                        else:
                            intro=None
                        d1=date.split('T')
                        date=datetime.datetime.strptime(d1[0],'%Y-%m-%d').date()
                        d2=valid_upto.split('T')
                        valid_upon=datetime.datetime.strptime(d2[0],'%Y-%m-%d').date()
                        c=MouSigned.objects.filter(emp_id=emp_id,date=date,valid_upto=valid_upto).exclude(status="DELETE").exclude(sno=data['id']).count()
                        if c==0:
                            MouSigned.objects.filter(sno=data['id']).update(status="DELETE")
                            Q=MouSigned.objects.create(intro=intro,date=date,t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),organization=organization,objective=objective,valid_upto=valid_upto,contact_number=contact_number,document=document,e_mail=e_mail)
                            
                            data_values={"ok":"data updated"}
                            status=200
                        else:
                            status=200
                            data_values={"ok":"duplicate data"}
                elif(request.method == 'DELETE'):
                    data=json.loads(request.body.decode("utf-8"))
                    MouSigned.objects.filter(sno=data['id']).update(status="DELETE")
                    data_values={"ok":"data deleted"}
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
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    if(request.GET['type']=='STUDENT'):
                        if 'id' in request.GET:
                            a=list(Achievement.objects.filter(sno=request.GET['id']).values('sno','emp_id','category','description','type','t_date','date','status'))
                        elif 'by' in request.GET:
                            a=list(Achievement.objects.filter(type='STUDENT').exclude(status='DELETE').values('sno','emp_id','category','category__value','description','type','t_date','date','status'))
                        else:
                            d=AarDropdown.objects.filter(field='STUDENTS ACHIEVEMENT').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                a.append({i['value']:list(query1)})
                        data_values={'data':a}
                        status=200
                    if(request.GET['type']=='DEPARTMENT'):
                        if 'id' in request.GET:
                            a=list(Achievement.objects.filter(sno=request.GET['id']).values('sno','emp_id','category','description','type','t_date','date','status'))
                        elif 'by' in request.GET:
                            a=list(Achievement.objects.filter(type='DEPARTMENT').exclude(status='DELETE').values('sno','emp_id','category','category__value','description','type','t_date','date','status'))
                        else:
                            d=AarDropdown.objects.filter(field='DEPARTMENTAL ACHIEVEMENT').exclude(value=None).values('sno','value')
                            a=[]
                            for i in d:
                                query1=AarDropdown.objects.filter(pid=i['sno']).exclude(value=None).values('sno','value')
                                a.append({i['value']:list(query1)})
                        data_values={'data':a}
                        status=200
                elif(request.method=='POST'):
                    data=json.loads(request.body.decode("utf-8"))
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
                elif request.method == 'DELETE':
                    data=json.loads(request.body.decode("utf-8"))
                    Achievement.objects.filter(sno=data['id']).update(status='DELETE')
                    status=200

                elif request.method == 'PUT':
                    data=json.loads(request.body.decode("utf-8"))
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
                            Q=Achievement.objects.filter(category=AarDropdown.objects.get(sno=category),description=description,emp_id=emp_id,type='STUDENT').exclude(sno=data['id']).exclude(status='DELETE').count()
                            if Q==0:
                                Achievement.objects.filter(sno=data['id']).update(status='DELETE')
                                Achievement.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),category=AarDropdown.objects.get(sno=category),description=description,type='STUDENT',date=date)
                                data_values={'ok':'data inserted'}
                                status=200
                            else:
                                data_values={'ok':'duplicate data'}
                                status=409
                        elif data['type']=='DEPARTMENT':
                            Q=Achievement.objects.filter(category=AarDropdown.objects.get(sno=category),description=description,emp_id=emp_id,type='DEPARTMENT').exclude(sno=data['id']).exclude(status='DELETE').count()
                            if Q==0:
                                Achievement.objects.filter(sno=data['id']).update(status='DELETE')
                                Achievement.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),category=AarDropdown.objects.get(sno=category),description=description,type='DEPARTMENT',date=date)
                                data_values={'ok':'data inserted'}
                                status=200
                            else:
                                data_values={'ok':'duplicate data'}
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

def Schools(request):
    data_values={}
    data=""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[337])
            if(check == 200):
                emp_id=request.session['hash1']
                if(request.method=='GET'):
                    if 'id' in request.GET:
                        Q=list(SummerWinterSchool.objects.filter(sno=request.GET['id']).values('sno','t_date','emp_id','emp_id__desg__value','emp_id__name','emp_id__dept__value','start_date','end_date','resource_person','topic','participant_number','participant_fee'))
                        Q[0]['resource_person_name']=list(AarMultiselect.objects.filter(type="SUM_WIN_SCHOOL",field="PARTICIPANT",sno=request.GET['id']).values_list('value',flat=True))
                        print(list(AarMultiselect.objects.filter(type="SUM_WIN_SCHOOL",field="PARTICIPANT",sno=request.GET['id']).values_list('value',flat=True)))
                        data_values={'data':list(Q)}
                    elif 'by' in request.GET:
                        Q=SummerWinterSchool.objects.exclude(status="DELETE").values('sno','t_date','emp_id','emp_id__desg__value','emp_id__name','emp_id__dept__value','start_date','end_date','resource_person','topic','participant_number','participant_fee')
                        data_values={'data':list(Q)}
                    else:
                        dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                        emp=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('name','emp_id')
                        ##print emp
                        data_values=list(emp)
                    status=200
                elif(request.method=='DELETE'):
                    data=json.loads(request.body.decode("utf-8"))
                    SummerWinterSchool.objects.filter(sno=data['id']).update(status="DELETE")
                    status=200

                elif(request.method=='POST'):
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
                        if resource_person=="EXTERNAL":
                            resource_person_name=resource_person_name.split(',')
                        d_s=start_date.split('T')
                        start_date=datetime.datetime.strptime(d_s[0],'%Y-%m-%d').date()
                        d_e=end_date.split('T')
                        end_date=datetime.datetime.strptime(d_e[0],'%Y-%m-%d').date()
                        q=SummerWinterSchool.objects.filter(topic=topic,emp_id=emp_id).count()
                        ###print emp_id
                        if q==0:
                            Q=SummerWinterSchool.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),start_date=start_date,end_date=end_date,resource_person=resource_person,topic=topic,participant_number=participant_number,participant_fee=participant_fee)
                            sno=Q.pk
                            for i in resource_person_name:
                                AarMultiselect.objects.create(type="SUM_WIN_SCHOOL",field="PARTICIPANT",value=i,emp_id=emp_id,sno=sno)
                            data_values={'ok':'data inserted'}
                            status=200
                        else:
                            data_values={"ok":"duplicate"}
                            status=409
                elif(request.method=='PUT'):
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
                            resource_person_name=[]
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
                        if resource_person=="EXTERNAL":
                            resource_person_name=resource_person_name.split(',')
                        d_s=start_date.split('T')
                        start_date=datetime.datetime.strptime(d_s[0],'%Y-%m-%d').date()
                        d_e=end_date.split('T')
                        end_date=datetime.datetime.strptime(d_e[0],'%Y-%m-%d').date()
                        q=SummerWinterSchool.objects.filter(topic=topic,emp_id=emp_id).exclude(sno=data['id']).exclude(status='DELETE').count()
                        if q==0:
                            SummerWinterSchool.objects.filter(sno=data['id']).update(status='DELETE')
                            Q=SummerWinterSchool.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),start_date=start_date,end_date=end_date,resource_person=resource_person,topic=topic,participant_number=participant_number,participant_fee=participant_fee)
                            sno=Q.pk
                            for i in resource_person_name:
                                AarMultiselect.objects.create(type="SUM_WIN_SCHOOL",field="PARTICIPANT",value=i,emp_id=emp_id,sno=sno)
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
                    if 'id' in request.GET:
                        Q=list(Hobbyclub.objects.filter(sno=request.GET['id']).values('sno','t_date','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','project_outcome','project_cost','project_description','team_size','project_incharge','project_incharge__name','project_incharge__dept__value','project_incharge__desg__value','start_date','end_date','club_name','club_name__value','project_title'))
                        Q[0]['coord']=list(AarMultiselect.objects.filter(sno=request.GET['id']).values_list('value',flat=True))
                        data_values={'data':list(Q)}
                    elif 'by' in request.GET:
                        Q=Hobbyclub.objects.exclude(status="DELETE").values('sno','t_date','emp_id','emp_id__name','emp_id__dept__value','emp_id__desg__value','project_outcome','project_cost','project_description','team_size','project_incharge','project_incharge__name','project_incharge__dept__value','project_incharge__desg__value','start_date','end_date','club_name__value','project_title')

                        data_values={'data':list(Q)}
                    else:
                        d=AarDropdown.objects.filter(field="HOBBY_CLUB").exclude(value=None).values('sno','value')
                        dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
                        emp=EmployeePrimdetail.objects.filter(dept=dept[0]['dept']).values('name','emp_id')
                        data_values={'data1':list(d),'data2':list(emp)}
                    status=200
                elif(request.method=='PUT'):
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
                        c=Hobbyclub.objects.filter(emp_id=emp_id,start_date=start_date,end_date=end_date).exclude(status="DELETE").exclude(sno=data['id']).count()
                        if c==0:
                            Hobbyclub.objects.filter(sno=data['id']).update(status="DELETE")
                            # data_copy=Hobbyclub.objects.filter(id=data['id']).values()
                            Q=Hobbyclub.objects.create(t_date=str(datetime.datetime.now()),emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id),project_outcome=project_outcome,project_cost=project_cost,project_description=project_description,team_size=team_size,project_incharge=EmployeePrimdetail.objects.get(emp_id=project_incharge),start_date=start_date,end_date=end_date,club_name=AarDropdown.objects.get(sno=club_name),project_title=project_title)

                            
                            sno=Q.pk
                            for i in coord:
                                AarMultiselect.objects.create(type='HOBBY_CLUB',field="PROJECT FACULTY COORDINATOR",value=i,emp_id=emp_id,sno=sno)
                            data_values={"ok":"data inserted"}
                            status=200
                        else:
                            data_values={"ok":"duplicate data"}
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
00000000000000000000000000000000000000000000000000000000000000...................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................