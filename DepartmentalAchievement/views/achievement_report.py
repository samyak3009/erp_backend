# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

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
                    fdate=datetime.datetime.strptime(data['fdate'].split('T')[0], '%Y-%m-%d').date()
                    tdate=datetime.datetime.strptime(data['tdate'].split('T')[0], '%Y-%m-%d').date()
                    if(data['type']=='267'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=guestLectures.objects.filter(date__gte=fdate,date__lte=tdate).exclude(status="DELETE").extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','topic','speaker','designation','organization','speaker_profile','contact_number','e_mail','participants_no','emp_id__dept__value')
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
                                query_data=guestLectures.objects.filter(emp_id=emp_id,date__gte=fdate,date__lte=tdate).exclude(status="DELETE").extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','topic','speaker','designation','organization','speaker_profile','contact_number','e_mail','participants_no','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'topic':i['topic'],'date':i['date'],'speaker':i['speaker'],'designation':i['designation'],'organization':i['organization'],'speaker_profile':i['speaker_profile'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'participants_no':i['participants_no'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='268'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=industrialVisit.objects.filter(date__gte=fdate,date__lte=tdate).exclude(status="DELETE").extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','industry','address','contact_person','contact_number','e_mail','participants_no','emp_id__dept__value')
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
                                query_data=industrialVisit.objects.filter(emp_id=emp_id,date__gte=fdate,date__lte=tdate).exclude(status="DELETE").extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','industry','address','contact_person','contact_number','e_mail','participants_no','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'industry':i['industry'],'date':i['date'],'address':i['address'],'contact_person':i['contact_person'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'participants_no':i['participants_no'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='269'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=MouSigned.objects.filter(date__gte=fdate,date__lte=tdate).exclude(status="DELETE").extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','organization','objective','valid_upto','contact_number','e_mail','emp_id__dept__value')
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
                                query_data=MouSigned.objects.filter(emp_id=emp_id,date__gte=fdate,date__lte=tdate).exclude(status="DELETE").extra(select={'date':"DATE_FORMAT(date,'%%d-%%m-%%Y')"}).values('date','organization','objective','valid_upto','contact_number','e_mail','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'organization':i['organization'],'date':i['date'],'objective':i['objective'],'valid_upto':i['valid_upto'],'contact_number':i['contact_number'],'e_mail':i['e_mail'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='270'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=eventsorganized.objects.filter(from_date__gte=fdate,to_date__lte=tdate).exclude(status="DELETE").extra(select={'from_date':"DATE_FORMAT(from_date,'%%d-%%m-%%Y')",'to_date':"DATE_FORMAT(to_date,'%%d-%%m-%%Y')"}).values('category__value','type__value','from_date','to_date','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaboration','sponsership','description','emp_id__dept__value')
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
                                query_data=eventsorganized.objects.filter(emp_id=emp_id,from_date__gte=fdate,to_date__lte=tdate).exclude(status="DELETE").extra(select={'from_date':"DATE_FORMAT(from_date,'%%d-%%m-%%Y')",'to_date':"DATE_FORMAT(to_date,'%%d-%%m-%%Y')"}).values('category__value','type__value','from_date','to_date','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaboration','sponsership','description','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'category__value':i['category__value'],'type__value':i['type__value'],'from_date':i['from_date'],'to_date':i['to_date'],'organization_sector__value':i['organization_sector__value'],'incorporation_status__value':i['incorporation_status__value'],'title':i['title'],'venue':i['venue'],'participants':i['participants'],'organizers':i['organizers'],'attended':i['attended'],'collaboration':i['collaboration'],'sponsership':i['sponsership'],'description':i['description'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='271'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Hobbyclub.objects.filter(start_date__gte=fdate,end_date__lte=tdate).exclude(status="DELETE").extra(select={'start_date':"DATE_FORMAT(start_date,'%%d-%%m-%%Y')",'end_date':"DATE_FORMAT(end_date,'%%d-%%m-%%Y')"}).values('club_name','project_title','start_date','end_date','project_incharge','team_size','project_description','project_cost','project_outcome','emp_id__dept__value')
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
                                query_data=Hobbyclub.objects.filter(emp_id=emp_id,start_date__gte=fdate,end_date__lte=tdate).exclude(status="DELETE").extra(select={'start_date':"DATE_FORMAT(start_date,'%%d-%%m-%%Y')",'end_date':"DATE_FORMAT(end_date,'%%d-%%m-%%Y')"}).values('club_name','project_title','start_date','end_date','project_incharge','team_size','project_description','project_cost','project_outcome','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'club_name':i['club_name'],'project_title':i['project_title'],'start_date':i['start_date'],'end_date':i['end_date'],'project_incharge':i['project_incharge'],'team_size':i['team_size'],'project_description':i['project_description'],'project_cost':i['project_cost'],'project_outcome':i['project_outcome'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='272'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=SummerWinterSchool.objects.filter(start_date__gte=fdate,end_date__lte=tdate).exclude(status="DELETE").extra(select={'start_date':"DATE_FORMAT(start_date,'%%d-%%m-%%Y')",'end_date':"DATE_FORMAT(end_date,'%%d-%%m-%%Y')"}).values('start_date','end_date','resource_person','topic','participant_number','participant_fee','emp_id__dept__value')
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
                                query_data=SummerWinterSchool.objects.filter(emp_id=emp_id,start_date__gte=fdate,end_date__lte=tdate).exclude(status="DELETE").extra(select={'start_date':"DATE_FORMAT(start_date,'%%d-%%m-%%Y')",'end_date':"DATE_FORMAT(end_date,'%%d-%%m-%%Y')"}).values('start_date','end_date','resource_person','topic','participant_number','participant_fee','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'start_date':i['start_date'],'end_date':i['end_date'],'resource_person':i['resource_person'],'topic':i['topic'],'participant_number':i['participant_number'],'participant_fee':i['participant_fee'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)
                    elif(data['type']=='273'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Achievement.objects.filter(type='STUDENT',t_date__gte=fdate,t_date__lte=tdate).exclude(status="DELETE").values('category__value','description','emp_id__dept__value')
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
                                query_data=Achievement.objects.filter(emp_id=emp_id,type='STUDENT',t_date__gte=fdate,t_date__lte=tdate).exclude(status="DELETE").values('category__value','description','emp_id__dept__value')
                                if(query_data.count()>0):
                                    for i in query_data:
                                        d={'category__value':i['category__value'],'description':i['description'],'dept':i['emp_id__dept__value']}
                                        retrieve_data.append(d)

                    elif(data['type']=='274'):
                        if(data['dept']=="all"):
                            retrieve_data=[]
                            query_data=Achievement.objects.filter(type='DEPARTMENT',t_date__gte=fdate,t_date__lte=tdate).exclude(status="DELETE").values('category__value','description','emp_id__dept__value')
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
                                query_data=Achievement.objects.filter(emp_id=emp_id,type='DEPARTMENT',t_date__gte=fdate,t_date__lte=tdate).exclude(status="DELETE").values('category__value','description','emp_id__dept__value')
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
                    fdate=datetime.datetime.strptime(data['fdate'].split('T')[0], '%Y-%m-%d').date()
                    tdate=datetime.datetime.strptime(data['tdate'].split('T')[0], '%Y-%m-%d').date()
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
                    fdate=datetime.datetime.strptime(data['fdate'].split('T')[0], '%Y-%m-%d').date()
                    tdate=datetime.datetime.strptime(data['tdate'].split('T')[0], '%Y-%m-%d').date()
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
                                q=guestLectures.objects.filter(emp_id=Eid).exclude(status="DELETE").values('topic','date','speaker','designation','organization','speaker_profile','contact_number','participants_no','remark')
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
                                q=industrialVisit.objects.filter(emp_id=Eid).exclude(status="DELETE").values('industry','date','address','contact_person','contact_number','e_mail','participants_no','remark')
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
                                q=MouSigned.objects.filter(emp_id=Eid).exclude(status="DELETE").values('date','organization','objective','valid_upto','contact_number','e_mail')
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
                                q=eventsorganized.objects.filter(emp_id=Eid).exclude(status="DELETE").values('category__value','type__value','from_date','to_date','organization_sector__value','incorporation_status__value','title','venue','participants','organizers','attended','collaboration','sponsership','description')
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
                                q=Hobbyclub.objects.filter(emp_id=Eid).exclude(status="DELETE").values('club_name__value','project_title','start_date','end_date','project_incharge__value','team_size','project_description','project_cost','project_outcome')
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
                                q=SummerWinterSchool.objects.filter(emp_id=Eid).exclude(status="DELETE").values('start_date','end_date','resource_person','topic','participant_number','participant_fee')
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
                    fdate=datetime.datetime.strptime(data['fdate'].split('T')[0], '%Y-%m-%d').date()
                    tdate=datetime.datetime.strptime(data['tdate'].split('T')[0], '%Y-%m-%d').date()
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

                    fdate=datetime.datetime.strptime(data['fdate'].split('T')[0], '%Y-%m-%d').date()
                    tdate=datetime.datetime.strptime(data['tdate'].split('T')[0], '%Y-%m-%d').date()

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

                                q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,published_date__range=[fdate,tdate]).values('paper_title','id','emp_id','approve_status','category__value','type_of_journal__value','published_date','journal_name','volume_no','issue_no','isbn','author__value','sub_category__value','impact_factor','page_no','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','emp_id__dept__value')
                                print(q)
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
                    fdate=datetime.datetime.strptime(data['fdate'].split('T')[0], '%Y-%m-%d').date()
                    tdate=datetime.datetime.strptime(data['tdate'].split('T')[0], '%Y-%m-%d').date()
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

                    fdate=datetime.datetime.strptime(data['fdate'].split('T')[0], '%Y-%m-%d').date()
                    tdate=datetime.datetime.strptime(data['tdate'].split('T')[0], '%Y-%m-%d').date()

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

                                q=Researchjournal.objects.filter(Q(approve_status='PENDING') | Q(approve_status='APPROVED') | Q(approve_status='REJECTED'),emp_id=Eid,published_date__range=[fdate,tdate]).values('paper_title','id','emp_id','approve_status','category__value','type_of_journal__value','published_date','journal_name','volume_no','issue_no','isbn','author__value','sub_category__value','impact_factor','page_no','publisher_name','publisher_address1','publisher_address2','publisher_zip_code','publisher_contact','publisher_email','publisher_website','others','emp_id__dept__value')
                                print(q)
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