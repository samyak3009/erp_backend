from django.shortcuts import render

import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from collections import Counter
from django.db.models import Sum,Count
from Registrar.models import StudentSemester
from login.views import generate_session_table_name

from StudentFeedback.models import *

old_session_name = '1920o'
new_session_name = '2021o'

def submit_settings():
    StuFeedbackEligibility_old = generate_session_table_name('StuFeedbackEligibility_', old_session_name)
    StuFeedbackEligibility_new = generate_session_table_name('StuFeedbackEligibility_', new_session_name)


    getModels= list(StuFeedbackEligibility_old.objects.filter().exclude(status='DELETE').values('sem','eligible_att_per','added_by','status','time_stamp'))
    for data in getModels:
        queryinsert = StuFeedbackEligibility_new.objects.create(sem=StudentSemester.objects.get(sem_id=data['sem']),eligible_att_per=data['eligible_att_per'],added_by=EmployeePrimdetail.objects.get(emp_id=data['added_by']),status=data['status'],time_stamp=data['time_stamp'])


# submit_settings()
    
def change_attributes():
    StuFeedbackAttributes_old = generate_session_table_name('StuFeedbackAttributes_', old_session_name)
    StuFeedbackAttributes_new = generate_session_table_name('StuFeedbackAttributes_', new_session_name)
    StuFeedbackEligibility_old = generate_session_table_name('StuFeedbackEligibility_', old_session_name)
    StuFeedbackEligibility_new = generate_session_table_name('StuFeedbackEligibility_', new_session_name)

    getModels=list(StuFeedbackAttributes_old.objects.filter().exclude(eligible_settings_id__status='DELETE').values())
    data_list=[]
    for data in getModels:
        sem = StuFeedbackEligibility_old.objects.filter(id=data['eligible_settings_id_id']).exclude(status='DELETE').values('sem','sem__sem','sem__dept')
        sem_id = StudentSemester.objects.filter(sem=sem[0]['sem__sem']+1,dept=sem[0]['sem__dept']).values()
        print(sem_id,'sem_id')
        setting_id= StuFeedbackEligibility_new.objects.filter(sem=sem_id[0]['sem_id']).values()
        print(setting_id,'setting_id')
        if data['subject_type_id']!=None:
            data_list.append({'subject_type':StudentDropdown.objects.get(sno=data['subject_type_id']),'name':data['name'],'eligible_settings_id':StuFeedbackEligibility_new.objects.get(id=setting_id[0]['id']),'residential_status':data['residential_status'],'gender':StudentDropdown.objects.get(sno=data['gender_id']),'min_marks':data['min_marks'],'max_marks':data['max_marks']})
        else:
            data_list.append({'subject_type':None,'name':data['name'],'eligible_settings_id':StuFeedbackEligibility_new.objects.get(id=setting_id[0]['id']),'residential_status':data['residential_status'],'gender':StudentDropdown.objects.get(sno=data['gender_id']),'min_marks':data['min_marks'],'max_marks':data['max_marks']})


    print(data_list)
    qry=(StuFeedbackAttributes_new(subject_type=r['subject_type'],name=r['name'],eligible_settings_id=r['eligible_settings_id'] ,residential_status=r['residential_status'],gender=r['gender'],min_marks=r['min_marks'],max_marks=r['max_marks'])for r in data_list)

    # qry=(StuFeedbackAttributes_new(subject_type=StudentDropdown.objects.get(sno=r['subject_type']),name=r['name'],eligible_settings_id=StuFeedbackEligibility_new.objects.get(id=r['eligible_settings_id']) ,residential_status=r['residential_status'],gender=StudentDropdown.objects.get(sno=r['gender']),min_marks=r['min_marks'],max_marks=r['max_marks'])for r in data_list)
    qry1=StuFeedbackAttributes_new.objects.bulk_create(qry)

# change_attributes()