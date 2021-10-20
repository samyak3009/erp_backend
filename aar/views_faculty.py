# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
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
from aar.views import *
from django.db.models import F

from Accounts.models import AccountsDropdown, EmployeeGross_detail,AccountsSession,MonthlyPayable_detail
from musterroll.models import EmployeePrimdetail, EmployeeResearch, EmployeeAcademic, Reporting, AarReporting, EmployeeSeparation
from aar.models import *
from login.models import AarDropdown,EmployeeDropdown
from leave.models import *

from Accounts.views import gross_payable_salary_components,getCurrentSession,get_salary_ingredient_details
from login.views import checkpermission
#request.session['hash1']


def isForfmFilled(emp_id_for,emp_id_by):
    formFilledQuery = EmployeePrimdetail.objectEmployeePrimdetails.filter(emp_id = emp_id).values()
    if len(list(int(formFilledQuery))) > 0:
        isFormFilled = True
    else:
        isFormFilled = False
    return isFormFilled

def FacultyAppraisal_creater(emp_identify,data,typee):
    qry1,create=FacultyAppraisal.objects.update_or_create(emp_id = EmployeePrimdetail.objects.get(emp_id=emp_identify),defaults=data)
    if typee=='CREATE':
        qry1=qry1.id
    else:
        qry1=FacultyAppraisal.objects.filter(id = qry1.id).values()
    return list(qry1)

def FacAppCat1A1_creater(emp_identify,data,typee):
    qry1=FacAppCat1A1.objects.filter(fac_app_id=emp_identify,status='INSERT').values()
    return list(qry1)

def FacAppCat1A2_creater(emp_identify,data,typee):
    qry1=FacAppCat1A2.objects.filter(fac_app_id=emp_identify,status='INSERT').values()
    return list(qry1)

def FacAppCat1A3_creater(emp_identify,data,typee):
    qry1=FacAppCat1A3.objects.filter(fac_app_id=emp_identify,status='INSERT').values()
    return list(qry1)

def FacAppCat1A4_creater(emp_identify,data,typee):
    qry1=FacAppCat1A4.objects.filter(fac_app_id=emp_identify,status='INSERT').values()
    return list(qry1)

def FacAppCat2A1_creater(emp_identify,data,typee):
    qry1=FacAppCat2A1.objects.filter(fac_app_id=emp_identify,status='INSERT').values()
    return list(qry1)

def FacAppCat3_creater(emp_identify,data,typee):
    qry1=FacAppCat3.objects.filter(fac_app_id=emp_identify,status='INSERT').values()
    return list(qry1)

def FacAppCat4A1_creater(emp_identify,data,typee):
    qry1=FacAppCat4A1.objects.filter(fac_app_id=emp_identify,status='INSERT').values()
    return list(qry1) 

def FacAppCat4A1_other_creater(emp_identify,data,typee):
    qry1=FacAppCat4A1.objects.filter(fac_app_id=emp_identify,status='OTHER').extra(select={'best_institute': 'branch_details','best_inst_avg': 'result_clear_pass','sec_best_avg': 'result_external','sec_best_institute': 'subject'}).values('best_institute','best_inst_avg','sec_best_avg','sec_best_institute')
    
    return list(qry1)   

def FacAppCat4A2_creater(emp_identify,data,typee):
    qry1=FacAppCat4A2.objects.filter(fac_app_id=emp_identify,status='INSERT').values()
    return list(qry1)

def Increament_types():
    qry=AarDropdown.objects.filter(field='INCREMENT TYPE').exclude(value = None).values('value','sno')
    return list(qry)
   
def Desgination_all():
    qry=EmployeeDropdown.objects.filter(field = 'DESIGNATION').exclude(value = None).values('value','sno')
    return list(qry)

def HOD_recommend_creater(emp_identify,data,typee):
    qry1=FacAppRecommend.objects.update_or_create(fac_app_id=FacultyAppraisal.objects.get(id=emp_identify),status='INSERT',whom='HOD',defaults={})
    qry1=FacAppRecommend.objects.filter(fac_app_id=emp_identify,status='INSERT',whom='HOD').values('fac_app_id','increment_type','increment_type__value','promoted_to','promoted_to__value','amount','recommend','status','remark')
    return list(qry1)

def DIR_recommend_creater(emp_identify,data,typee):
    qry1=FacAppRecommend.objects.update_or_create(fac_app_id=FacultyAppraisal.objects.get(id=emp_identify),status='INSERT',whom='DEAN',defaults={})
    qry1=FacAppRecommend.objects.filter(fac_app_id=emp_identify,status='INSERT',whom='DEAN').values('fac_app_id','increment_type','increment_type__value','promoted_to','promoted_to__value','amount','recommend','status','remark')
    return list(qry1)

def gross_generator(emp_id,working_days,actual_days,session,taxstatus_li,salary_month):
    data=[]
    salary_type=0
    AGP=0
    gross_salary=0
    basic_agp=0
    salary_type__value=''
    without_others=0

    ################ GET SALARY TYPE OF EMPLOYEE i.e. GRADE OR CONSOLIDATE #################
    qry=EmployeeGross_detail.objects.filter(Emp_Id=emp_id).filter(session=session).exclude(Status="DELETE").values('salary_type','salary_type__value')
    if len(qry)>0:
        salary_type=qry[0]['salary_type']
        salary_type__value=qry[0]['salary_type__value']
        ############################ GET SALARY INGREDIENTS OF EMPLOYEE BASED ON SALARY TYPE AND ALSO THEIR GROSS VALUE ###########
        sal_ing=get_salary_ingredient_details(emp_id,salary_type,taxstatus_li,session)
        gross_salary=0
        basic_agp=0
        for sal in sal_ing:
            ################### if month of salary ingredient to be credited is not equal to the month for which salary is to generated, show gross value=0#######################
            
            #################### e.g. if some component is to be credited in the month of july then it's value will be zero for the rest of the months i.e. for april,may,june,august,sept etc. #############

            if sal['salary_ingredient__next_count_month'].month != salary_month:
                data.append({'gross_value':0,'payable_value':0,'Ing_Id':sal['salary_ingredient'],'value':sal['salary_ingredient__Ingredients__value'],'sal_dropdown_id':sal['salary_ingredient__Ingredients'],'tax_status':sal['salary_ingredient__taxstatus']})
            else:
                ############### INGREDIENTS OF VALUE TYPE ######################
                if sal['salary_ingredient__calcType'] == 'V':
                    try:
                        payable_value = round((sal['prev_value']*working_days)/actual_days)
                    except:
                        payable_value=0
                    data.append({'gross_value':sal['prev_value'],'payable_value':payable_value,'Ing_Id':sal['salary_ingredient'],'value':sal['salary_ingredient__Ingredients__value'],'sal_dropdown_id':sal['salary_ingredient__Ingredients'],'tax_status':sal['salary_ingredient__taxstatus']})

                ############### INGREDIENTS OF FORMULA TYPE #####################
            
                elif sal['salary_ingredient__calcType'] == 'F':
                    formula_list=sal['salary_ingredient__Formula']

                    value=0
                    for f in formula_list:
                        qry_gross_value=EmployeeGross_detail.objects.filter(Emp_Id=emp_id,Ing_Id__Ingredients=f).filter(session=session).exclude(Status="DELETE").values('Value')
                        value+=qry_gross_value[0]['Value']
                    
                    value=round((sal['salary_ingredient__percent']*value)/100)
                    
                    try:
                        payable_value = round((value*working_days)/actual_days)
                    except:
                        payable_value=0
                    data.append({'gross_value':value,'payable_value':payable_value,'Ing_Id':sal['salary_ingredient'],'value':sal['salary_ingredient__Ingredients__value'],'sal_dropdown_id':sal['salary_ingredient__Ingredients'],'tax_status':sal['salary_ingredient__taxstatus']})
            ############# GROSS SALARY TOTAL ##################
            if(data[-1]['value']=='AGP'):
                AGP=data[-1]['gross_value']
            if(data[-1]['value']=='BASIC' or data[-1]['value']=='AGP'):
                basic_agp=basic_agp+data[-1]['gross_value']
            if(data[-1]['value']!='OTHER'):
                without_others=without_others+data[-1]['gross_value']
                
            gross_salary=gross_salary+data[-1]['gross_value']

    return [gross_salary,basic_agp,salary_type,salary_type__value,AGP,without_others]

def const_increament_generator(for_whom,emp_id,increment_type,amount,promoted_to,recommend):
    data={}
    proposed_increment=float()
    session=getCurrentSession()
    month=date.today().month-1
    if month==0:
        month=12
    accounts=gross_generator(emp_id,31,31,session,[0,1],month)
    gross=accounts[5]
    basic_agp=accounts[1]
    salary_type=accounts[3]

    def small(salary_type,increment_type,amount):
        proposed_increment=0
        if(salary_type=='GRADE'):
            if(increment_type is None):
                proposed_increment=0
            elif(increment_type=='NORMAL'):
                proposed_increment=(gross*3)/100
            elif(increment_type=='SPECIAL'):
                proposed_increment=amount
        elif(salary_type=='CONSOLIDATE'):
            if(increment_type is None):
                proposed_increment=0
            elif(increment_type=='NORMAL'):
                proposed_increment=(gross*8)/100
            elif(increment_type=='SPECIAL'):
                proposed_increment=amount
        else:
            proposed_increment='--'
        return  proposed_increment

    data['Gross salary']=accounts[0]
    data['Basic + AGP']=basic_agp
    data['Recommended']=recommend
    # print(increment_type,"hi")
    if(increment_type is not None):
        data['Increment Type']=increment_type
        if(recommend=='PROMOTION'):
            data['Incremented Amount']=small(salary_type,increment_type,amount)
            if '-' in str(data['Incremented Amount']):
                data['Incremented Gross Salary']=accounts[0]
            else:
                data['Incremented Gross Salary']=accounts[0]+data['Incremented Amount']
            #data['Incremented Gross Salary']=accounts[0]+data['Incremented Amount']
            data['Promotion To']=promoted_to

        if(recommend=='INCREMENT'):
            # print(small(salary_type,increment_type,amount),"hi")
            data['Incremented Amount']=small(salary_type,increment_type,amount)
            if '-' in str(data['Incremented Amount']):
                data['Incremented Gross Salary']=accounts[0]
            else:
                data['Incremented Gross Salary']=accounts[0]+data['Incremented Amount']
            data['Promotion To']='--'
    else:
        data['Increment Type']='--'
        if(recommend=='PROMOTION'):
            data['Incremented Amount']=0
            data['Promotion To']=promoted_to
        if(recommend=='NO INCREMENT'):
            data['Incremented Amount']=0
            data['Promotion To']='--'
    return data

def increament_generator(for_whom,emp_id,increment_type,amount,promoted_to,recommend):
    data={}
    proposed_increment=float()
    session=getCurrentSession()
    month=date.today().month-1
    if month==0:
        month=12
    accounts=gross_generator(emp_id,31,31,session,[0,1],month)
    gross=accounts[5]
    basic_agp=accounts[1]
    salary_type=accounts[3]

    def small(salary_type,increment_type,amount):
        proposed_increment=0
        if(salary_type=='GRADE'):
            if(increment_type is None):
                proposed_increment=0
            elif(increment_type=='NORMAL'):
                proposed_increment=(gross*3)/100
            elif(increment_type=='SPECIAL'):
                proposed_increment=amount
        elif(salary_type=='CONSOLIDATE'):
            if(increment_type is None):
                proposed_increment=0
            elif(increment_type=='NORMAL'):
                proposed_increment=(gross*8)/100
            elif(increment_type=='SPECIAL'):
                proposed_increment=amount
        else:
            proposed_increment='--'
        return  proposed_increment

    data['Gross salary']=accounts[0]
    data['Basic + AGP']=basic_agp

    select=for_whom+' Recommended'
    data[select]=recommend
    if(increment_type is not None):
        data['Increment Type']=increment_type
        if(recommend=='PROMOTION'):
            data['Incremented Amount']=small(salary_type,increment_type,amount)
            data['Incremented Gross Salary']=accounts[0]+data['Incremented Amount']
            data['Promotion To']=promoted_to

        if(recommend=='INCREMENT'):
            data['Incremented Amount']=small(salary_type,increment_type,amount)
            if '--' == data['Incremented Amount']:
                data['Incremented Amount']=0
            data['Incremented Gross Salary']=accounts[0]+data['Incremented Amount']
            # data['Promotion To']='--'
    else:
        # data['Increment Type']='--'
        if(recommend=='PROMOTION'):
            data['Incremented Amount']=0
            data['Promotion To']=promoted_to
        if(recommend=='NO INCREMENT'):
            data['Incremented Amount']=0
            # data['Promotion To']='--'
    return data

def check_eligibility(emp_id):
    time=datetime.datetime.now()
    qry_check=LockingUnlocking.objects.filter(Emp_Id=emp_id,toDate__gte=time,status="INSERT",Emp_Id__emp_status='ACTIVE',Emp_Id__emp_category__value='FACULTY').order_by('-id')[:1].values('fromDate','toDate')
    if qry_check is not None:
        result="UNLOCKED"
        separation=EmployeeSeparation.objects.filter(emp_id=emp_id,status="LEAVE",final_status='APPROVED BY ADMIN').order_by('-id')[:1].values('rejoin_date')
        joiner=EmployeePrimdetail.objects.filter(emp_id=emp_id).values("doj")
        resign=EmployeeSeparation.objects.filter(emp_id=emp_id,status="RESIGN",final_status='APPROVED BY ADMIN').values('rejoin_date')

        if separation:
            d1=datetime.date(2018,9,1)
            d2=separation[0]['rejoin_date']
            if ((d1.year - d2.year) * 12 + d1.month - d2.month +(d1.day - d2.day)/30)>6:
                result="ELIGIBLE"
            else:
                result="NOT ELIGIBLE"
        elif resign:
            result="NOT ELIGIBLE"
        elif joiner:
            d1=datetime.date(2018,9,1)
            d2=joiner[0]['doj']
            if ((d1.year - d2.year) * 12 + d1.month - d2.month +(d1.day - d2.day)/30)>6:
                result="ELIGIBLE"
            else:
                result="NOT ELIGIBLE"
        else:
            result="NOT EXIST"
    else:
        result="LOCKED"
    return result

def scorer(type,var_1,var_2,var_3):
    score=0
    if type=="J":#FOR JOURNAL
        # var_1:impact,var_2:author?.,var_3:null
        if var_2=="SINGLE AUTHOR":
            score=15
            if float(var_1)>=1 and float(var_1)<=2 :
                score=25
            elif float(var_1)>2 and float(var_1)<=5 :
                score=30
            elif float(var_1)>5 :
                score=35
        elif var_2=="FIRST AUTHOR" or var_2=="SUPERVISOR":
            score=9
            if float(var_1)>=1 and float(var_1)<=2 :
                score=19
            elif float(var_1)>2 and float(var_1)<=5 :
                score=24
            elif float(var_1)>5 :
                score=29
        elif var_2=="CO-AUTHOR":
            score=6
            if float(var_1)>=1 and float(var_1)<=2 :
                score=16
            elif float(var_1)>2 and float(var_1)<=5 :
                score=21
            elif float(var_1)>5 :
                score=26
    elif type=="C":#FOR CONFERENCE
        # var_1:author,var_2:type?.,var_3:null
        if var_2=="INTERNATIONAL":
            if var_1=="SINGLE AUTHOR" :
                score=10
            elif var_1=="FIRST AUTHOR" or var_1=="SUPERVISOR" :
                score=6
            elif var_1=="CO-AUTHOR" :
                score=4
        elif var_2=="NATIONAL":
            if var_1=="SINGLE AUTHOR" :
                score=7.5
            elif var_1=="FIRST AUTHOR" or var_1=="SUPERVISOR" :
                score=4.5
            elif var_1=="CO-AUTHOR" :
                score=3
    elif type=="B":#FOR BOOKS
        # var_1:type,var_2:what is it?.,var_3:null
        if var_2=="INTERNATIONAL":
            if var_1=="BOOK" :
                score=50
            elif var_1=="CHAPTER" or var_1=="ARTICLE" :
                score=10
        elif var_2=="NATIONAL":
            if var_1=="BOOK" :
                score=25
            elif var_1=="CHAPTER" or var_1=="ARTICLE" :
                score=5
        elif var_2=="REGIONAL":
            if var_1=="BOOK" :
                score=15
            elif var_1=="CHAPTER" or var_1=="ARTICLE" :
                score=3
    elif type=="PC":#FOR PROJECT & CONSULTANCY
        # var_1:prin. inve,var_2:Co-prin.,var_3:amount
        var_3=var_3.upper()
        var_2=var_2.upper()
        if var_3=="SELF" and var_2=="OTHER":
            if float(var_1)>=3000000 :
                score=8
            elif float(var_1)>=500000 and float(var_1)<3000000 :
                score=6
            elif float(var_1)>=50000 and float(var_1)<500000 :
                score=4
        elif var_3=="OTHER" and var_2=="SELF":
            if float(var_1)>=3000000 :
                score=12
            elif float(var_1)>=500000 and float(var_1)<3000000 :
                score=9
            elif float(var_1)>=50000 and float(var_1)<500000 :
                score=6
        elif var_3=="SELF" and var_2=="SELF":
            if float(var_1)>=3000000 :
                score=20
            elif float(var_1)>=500000 and float(var_1)<3000000 :
                score=15
            elif float(var_1)>=50000 and float(var_1)<500000 :
                score=10
    elif type=="PA":#FOR PATENT
        # var_1:null,var_2:type.,var_3:approve
        if var_3=="grant" and var_2=="INTERNATIONAL":
            score=40
        elif var_3=="grant" and var_2=="NATIONAL":
            score=25
    elif type=="G":#FOR GUIDANCE
        # var_1:sattus,var_2:type.,var_3:quantity
        if var_1=="DEGREE" and var_2=="AWARDED":
            score=3
        elif (var_1=="RESEARCH" or var_1=="RESEARCH (PH. D.)" ) and var_2=="AWARDED":
            score=10
        elif (var_1=="RESEARCH" or var_1=="RESEARCH (PH. D.)" ) and var_2=="SUBMITTED":
            score=7
    elif type=="FacAppCat1A1":
        # var_1:calender,var_2:portal
        x = float(var_2)/float(var_1)
        if x>=1:
            score=50
        elif x >= .80:
            score=(x)*50
        else:
            score=0
    elif type=="FacAppCat1A3":
        # var_1:discr
        # print(var_1 is not None and var_1 != '')
        if var_1 is not None and var_1 != '':
            score=5
        else:
            score=0
    elif type=="FacAppCat1A4":
        # var_1:sno,var_2:extend
        if var_1 is not None and var_2 is not None :
            if int(var_1) == 0 :
                score=2*float(var_2)
            elif int(var_1) == 1 :
                score=3*float(var_2)
            elif int(var_1) == 2 :
                score=5*float(var_2)
            else:
                score=0
        else:
            score=0
    elif type=="FacAppCat4A1":
        # var_1:sub_marks,var_1:first_mark,var_1:second_mark
        sumup=float(var_2)+float(var_3)
        avg=sumup/2
        if avg is not None :
            if float(var_1) >= avg :
                score=30
            elif float(var_1)-10 >= avg :
                score=30-(avg-float(var_1))*2
            else:
                score=0
        else:
            score=0
    elif type=="FacAppCat4A2":
        # var_1:feedback
        # print(float(var_1))
        if var_1 is not None :
            if float(var_1) >= 8.4 :
                score=20
            elif float(var_1) >= 6.5 :
                # print(float(var_1))
                score=20-(8.4-float(var_1))*10
            else:
                score=0
        else:
            score=0
    score=round(score,2)
    return score

def check_status(status):
    x=['','','']
    if status=='DA':
        x[0]='FILLED'
        x[1]='FILLED'
        x[2]='FILLED'
    elif status=='HA':
        x[0]='NOT FILLED'
        x[1]='FILLED'
        x[2]='FILLED'
    elif status=='HSA':
        x[0]='NOT FILLED'
        x[1]='NOT FILLED'
        x[2]='FILLED'
    elif status=='Y':
        x[0]='NOT FILLED'
        x[1]='NOT FILLED'
        x[2]='FILLED'
    else:
        x[0]='NOT FILLED'
        x[1]='NOT FILLED'
        x[2]='NOT FILLED'
    return x

def form(emp_id):
    data_values = {}
    eligible=check_eligibility(emp_id)
    if eligible=="LOCKED":
        FacultyAppraisal.objects.filter(Emp_Id=emp_id).filter(form_filled_status__in=["S4"]).update(form_filled_status="Y")
    elif eligible=="ELIGIBLE":

        session=getCurrentSession()

        month=date.today().month-1
        if month==0:
            month=12
        accounts=gross_generator(emp_id,31,31,session,[0,1],month)
        total_gross=accounts[0]
        salary=EmployeeGross_detail.objects.filter(Emp_Id=emp_id).filter(session=session).exclude(Status="DELETE").values('salary_type__value','salary_type')

        primary=list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg','dept','desg__value','dept__value','doj','name','current_pos__value'))

        experience=str(get_total_experience(emp_id))
        exper_list=experience.split(' ')
        total_experience=int(exper_list[0])+float(exper_list[2])/12
        if len(primary)>0:
            data_store={'desg':EmployeeDropdown.objects.get(sno=primary[0]['desg']),'dept':EmployeeDropdown.objects.get(sno=primary[0]['dept']),'highest_qualification':get_highest_qualification(emp_id),'salary_type':AccountsDropdown.objects.get(sno=accounts[2]),'current_gross_salary':total_gross,'total_experience':total_experience,'agp':accounts[4]}
            data_values['FacultyAppraisal']=FacultyAppraisal_creater(emp_id,data_store,"GET DATA")
        else:
            data_values['FacultyAppraisal']=FacultyAppraisal_creater(emp_id,{},"GET DATA")

        appraisal=data_values['FacultyAppraisal'][0]['id']
        # /*S stand for Saved*/
        # /*S1 stand for Saved category_1*/
        # /*S2 stand for Saved category_2*/
        # /*S3 stand for Saved category_3*/
        # /*S4 stand for Saved category_4*/
        for x in primary:
            x['salary_type__value']=accounts[3]
            x['experience']=experience
            x['emp_id']=emp_id
        data_values['premilinary']=list(primary)
        data_values['DIR_filled']=DIR_recommend_creater(appraisal,{},"CREATE")
        data_values['HOD_filled']=HOD_recommend_creater(appraisal,{},"CREATE")
        data_values['FacAppCat1A1']=FacAppCat1A1_creater(appraisal,{},"CREATE")
        data_values['FacAppCat1A2']=FacAppCat1A2_creater(appraisal,{},"CREATE")
        data_values['FacAppCat1A3']=FacAppCat1A3_creater(appraisal,{},"CREATE")
        data_values['FacAppCat1A4']=FacAppCat1A4_creater(appraisal,{},"CREATE")
        data_values['FacAppCat2A1']=FacAppCat2A1_creater(appraisal,{},"CREATE")
        data_values['FacAppCat4A1']=FacAppCat4A1_creater(appraisal,{},"CREATE")
        data_values['FacAppCat4A1_OTHER']=FacAppCat4A1_other_creater(appraisal,{},"CREATE")
        data_values['FacAppCat4A2']=FacAppCat4A2_creater(appraisal,{},"CREATE")

        rec_amt=increament_generator('HOD',emp_id,'NORMAL',0,'','INCREMENT')
        data_values['recommend_amount']=rec_amt['Incremented Amount']
        if data_values['DIR_filled'] is not None and data_values['DIR_filled']!=[]:
            data_values['DIR_recommend']=increament_generator('Director',emp_id,data_values['DIR_filled'][0]['increment_type__value'],data_values['DIR_filled'][0]['amount'],data_values['DIR_filled'][0]['promoted_to__value'],data_values['DIR_filled'][0]['recommend'])
        else:
            data_values['DIR_recommend']={}
        
        if data_values['HOD_filled'] is not None and data_values['HOD_filled']!=[]:
            data_values['HOD_recommend']=increament_generator('HOD',emp_id,data_values['HOD_filled'][0]['increment_type__value'],data_values['HOD_filled'][0]['amount'],data_values['HOD_filled'][0]['promoted_to__value'],data_values['HOD_filled'][0]['recommend'])
        else:
            data_values['HOD_recommend']={}

        # temp=list(FacAppCat3.objects.filter(fac_app_id=appraisal,status="INSERT").values('type','score_awarded'))
        # data_values['FacAppCat3']=({x['type']:x['score_awarded']}for x in temp)
        data_values['cat3']={}
        range_date=["2017-08-01", "2018-07-31"]
        starting_date=["2000-08-01", "2017-08-01"]
        ending_date=["2018-07-31", "3000-07-31"]

        data_values['cat3']['J']={}
        data_values['cat3']['G']={}
        data_values['cat3']['C']={}
        data_values['cat3']['PC']={}
        data_values['cat3']['PA']={}
        data_values['cat3']['B']={}
        data_values['cat3']['L']={}
        data_values['cat3']['T']={}
        data_values['cat3']['J']['is_empty']=True
        data_values['cat3']['G']['is_empty']=True
        data_values['cat3']['C']['is_empty']=True
        data_values['cat3']['PC']['is_empty']=True
        data_values['cat3']['PA']['is_empty']=True
        data_values['cat3']['B']['is_empty']=True
        data_values['cat3']['L']['is_empty']=True
        data_values['cat3']['T']['is_empty']=True
        data_values['cat3']['J']['claimed']=0
        data_values['cat3']['J']['awarded']=0
        data_values['cat3']['G']['claimed']=0
        data_values['cat3']['G']['awarded']=0
        data_values['cat3']['C']['claimed']=0
        data_values['cat3']['C']['awarded']=0
        data_values['cat3']['PC']['claimed']=0
        data_values['cat3']['PC']['awarded']=0
        data_values['cat3']['PA']['claimed']=0
        data_values['cat3']['PA']['awarded']=0
        data_values['cat3']['B']['claimed']=0
        data_values['cat3']['B']['awarded']=0
        data_values['cat3']['L']['claimed']=0
        data_values['cat3']['L']['awarded']=0
        data_values['cat3']['T']['claimed']=0
        data_values['cat3']['T']['awarded']=0
        data_values['J']=list(Researchjournal.objects.filter(emp_id=emp_id,approve_status='APPROVED',published_date__range=range_date).exclude(author__isnull=True).values('id','journal_name','isbn','approve_status','sub_category','sub_category__value','paper_title','impact_factor','author','author__value','type_of_journal','type_of_journal__value','publisher_address1','publisher_address2','published_date'))

        for x in data_values['J']:
            x['date']=x['published_date']
            if(x['impact_factor'] is None or x['impact_factor'] == "" ):
                x['impact_factor']=0
            if x['sub_category__value'] != "SCI" and x['sub_category__value'] != "SCOPOUS":
                x['score_claimed']=scorer('J',0,x['author__value'],"")
            else:
                x['score_claimed']=scorer('J',x['impact_factor'],x['author__value'],"")
            x['type']='J'
            query=FacAppCat3.objects.update_or_create(type=x['type'],fac_app_id=FacultyAppraisal.objects.get(id=appraisal),research_journal=Researchjournal.objects.get(id=x['id']),status='INSERT',defaults={'type':x['type'],'fac_app_id':FacultyAppraisal.objects.get(id=appraisal),'research_journal':Researchjournal.objects.get(id=x['id']),'status':"INSERT",'score_claimed':x['score_claimed']})
            x['score_awarded']=query[0].score_awarded
            x['FacAppCat3_id']=query[0].id
            if x['score_claimed'] is not None:
                data_values['cat3']['J']['claimed']=data_values['cat3']['J']['claimed']+x['score_claimed']
            data_values['cat3']['J']['awarded']=query[0].score_awarded
            data_values['cat3']['J']['is_empty']=False



        data_values['C']=list(Researchconference.objects.filter(emp_id=emp_id,approve_status='APPROVED',published_date__range=range_date).exclude(author__value__isnull=True).exclude(type_of_conference__value__isnull=True).values('id','journal_name','isbn','approve_status','paper_title','sub_category__sno','sub_category__value','conference_title','type_of_conference__sno','type_of_conference__value','author__sno','author__value','published_date'))

        for x in data_values['C']:
            x['date']=x['published_date']
            x['score_claimed']=scorer('C',x['author__value'],x['type_of_conference__value'],"")
            x['type']='C'
            query=FacAppCat3.objects.update_or_create(type=x['type'],fac_app_id=FacultyAppraisal.objects.get(id=appraisal),research_conference=Researchconference.objects.get(id=x['id']),status='INSERT',defaults={'type':x['type'],'fac_app_id':FacultyAppraisal.objects.get(id=appraisal),'research_conference':Researchconference.objects.get(id=x['id']),'status':"INSERT",'score_claimed':x['score_claimed']})
            x['score_awarded']=query[0].score_awarded
            x['FacAppCat3_id']=query[0].id
            if x['score_claimed'] is not None:
                data_values['cat3']['C']['claimed']=data_values['cat3']['C']['claimed']+x['score_claimed']
            data_values['cat3']['C']['awarded']=query[0].score_awarded
            data_values['cat3']['C']['is_empty']=False



        data_values['G']=list(Researchguidence.objects.filter(emp_id=emp_id,approve_status='APPROVED',date__range=range_date).values('id','emp_id','guidence','guidence__value','project_title','area_of_spec','degree__sno','degree__value','degree_awarded','t_date','status__value','date'))
        y=len(data_values['G'])
        x=0
        while x<y:
            # print(x,y)
            if data_values['G'][x]['degree_awarded'] is None:
                if data_values['G'][x]['status__value'] is None:
                    data_values['G'].remove(data_values['G'][x])
                    y=y-1
                    continue
            if data_values['G'][x]['degree_awarded'] is None:
                data_values['G'][x]['score_claimed']=scorer('G','RESEARCH',data_values['G'][x]['status__value'],"")
                data_values['G'][x]['degree__value']=data_values['G'][x]['status__value']
            else:
                data_values['G'][x]['score_claimed']=scorer('G','DEGREE','AWARDED',"")
            data_values['G'][x]['type']='G'
            query=FacAppCat3.objects.update_or_create(type=data_values['G'][x]['type'],fac_app_id=FacultyAppraisal.objects.get(id=appraisal),research_guidance=Researchguidence.objects.get(id=data_values['G'][x]['id']),status='INSERT',defaults={'status':"INSERT",'score_claimed':data_values['G'][x]['score_claimed']})
            data_values['G'][x]['score_awarded']=query[0].score_awarded
            data_values['G'][x]['FacAppCat3_id']=query[0].id
            if data_values['G'][x]['score_claimed'] is not None:
                data_values['cat3']['G']['claimed']=data_values['cat3']['G']['claimed']+data_values['G'][x]['score_claimed']
            data_values['cat3']['G']['awarded']=query[0].score_awarded
            data_values['cat3']['G']['is_empty']=False
            x=x+1


        data_values['B']=list(Books.objects.filter(emp_id=emp_id,approve_status='APPROVED',published_date__range=range_date).exclude(publisher_type__value__isnull=True).values('id','title','isbn','chapter','role','role__value','role_for','role_for__value','publisher_type','publisher_type__value','author','author__value','approve_status','t_date','published_date'))

        for x in data_values['B']:
            x['date']=x['published_date']
            if(x['title']==None or x['title']==''):
                x['title']=x['chapter']
                x['score_claimed']=scorer('B','CHAPTER',x['publisher_type__value'],"")
            else:
                x['score_claimed']=scorer('B','BOOK',x['publisher_type__value'],"")
            x['type']='B'
            query=FacAppCat3.objects.update_or_create(type=x['type'],fac_app_id=FacultyAppraisal.objects.get(id=appraisal),books=Books.objects.get(id=x['id']),status='INSERT',defaults={'status':"INSERT",'score_claimed':x['score_claimed']})
            x['score_awarded']=query[0].score_awarded
            x['FacAppCat3_id']=query[0].id
            if x['score_claimed'] is not None:
                data_values['cat3']['B']['awarded']=query[0].score_awarded
            data_values['cat3']['B']['claimed']=data_values['cat3']['B']['claimed']+x['score_claimed']
            data_values['cat3']['B']['is_empty']=False


        data_values['PC']=list(ProjectConsultancy.objects.filter(emp_id=emp_id,approve_status='APPROVED').filter(Q(end_date__gte=range_date[0]) & Q(start_date__lte=range_date[1])).exclude(principal_investigator__isnull=True).exclude(co_principal_investigator__isnull=True).values('id','status','title','start_date','end_date','principal_investigator','co_principal_investigator','association','sponsored'))

        #data_values['PC']=list(ProjectConsultancy.objects.filter(emp_id=emp_id,approve_status='APPROVED').filter(Q(end_date__range=range_date)|Q(start_date__range=range_date)|(Q(end_date__range=ending_date) & Q(start_date__range=starting_date))).exclude(principal_investigator__isnull=True).exclude(co_principal_investigator__isnull=True).values('id','status','title','start_date','end_date','principal_investigator','co_principal_investigator','association','sponsored'))

        y=len(data_values['PC'])
        x=0
        while x<y:
            # print(x,y)
            data_values['PC'][x]['date']=data_values['PC'][x]['end_date']
            amount=Sponsers.objects.filter(type='PROJECT',spons_id=data_values['PC'][x]['id'],emp_id=emp_id).values('amount')
            if amount is not None and len(amount)>0:            
                data_values['PC'][x]['score_claimed']=scorer('PC',amount[0]['amount'],data_values['PC'][x]['principal_investigator'],data_values['PC'][x]['co_principal_investigator'])
                data_values['PC'][x]['type']='PC'
                data_values['PC'][x]['amount']=amount[0]['amount']
                query=FacAppCat3.objects.update_or_create(type=data_values['PC'][x]['type'],fac_app_id=FacultyAppraisal.objects.get(emp_id=emp_id),project_consultancy=ProjectConsultancy.objects.get(id=data_values['PC'][x]['id']),status='INSERT',defaults={'status':"INSERT",'score_claimed':data_values['PC'][x]['score_claimed']})
                data_values['PC'][x]['score_awarded']=query[0].score_awarded
                data_values['PC'][x]['id']=query[0].id
                
                if data_values['PC'][x]['score_claimed'] is not None:
                    data_values['cat3']['PC']['awarded']=query[0].score_awarded
                data_values['cat3']['PC']['claimed']=data_values['cat3']['PC']['claimed']+data_values['PC'][x]['score_claimed']
                data_values['cat3']['PC']['is_empty']=False
            else:
                data_values['PC'].remove(data_values['PC'][x])
                y=y-1
                continue
            x=x+1

        # for x in data_values['PC']:

        #     x['date']=x['end_date']
        #     amount=Sponsers.objects.filter(type='PROJECT',spons_id=x['id'],emp_id=emp_id).values('amount')
        #     if amount is not None and len(amount)>0:            
        #         x['score_claimed']=scorer('PC',x['principal_investigator'],x['co_principal_investigator'],amount[0]['amount'])
        #         x['type']='PC'
        #         x['amount']=amount[0]['amount']
        #         query=FacAppCat3.objects.update_or_create(type=x['type'],fac_app_id=FacultyAppraisal.objects.get(emp_id=emp_id),project_consultancy=ProjectConsultancy.objects.get(id=x['id']),status='INSERT',defaults={'status':"INSERT",'score_claimed':x['score_claimed']})
        #         x['score_awarded']=query[0].score_awarded
        #         x['id']=query[0].id
                
        #         if x['score_claimed'] is not None:
        #             data_values['cat3']['PC']['awarded']=query[0].score_awarded
        #         data_values['cat3']['PC']['claimed']=data_values['cat3']['PC']['claimed']+x['score_claimed']
        #         data_values['cat3']['PC']['is_empty']=False

        #     else:
        #         data_values['PC'].remove(x)
        # # //////////////////SPONSERED THROUGH (Sponsers)///////////////////
        

        data_values['PA']=list(Patent.objects.filter(emp_id=emp_id,approve_status='APPROVED',date__range=range_date).exclude(level__isnull=True).exclude(status__isnull=True).values('id','title','company_name','status','date','owner','owner__value','t_date','level'))

        for x in data_values['PA']:
            x['score_claimed']=scorer('PA','',x['level'],x['status'])
            x['type']='PA'
            query=FacAppCat3.objects.update_or_create(type=x['type'],fac_app_id=FacultyAppraisal.objects.get(emp_id=emp_id),patent=Patent.objects.get(id=x['id']),status='INSERT',defaults={'type':x['type'],'fac_app_id':FacultyAppraisal.objects.get(emp_id=emp_id),'patent':Patent.objects.get(id=x['id']),'status':"INSERT",'score_claimed':x['score_claimed']})
            x['score_awarded']=query[0].score_awarded
            x['FacAppCat3_id']=query[0].id
            if x['score_claimed'] is not None:
                data_values['cat3']['PA']['claimed']=data_values['cat3']['PA']['claimed']+x['score_claimed']
            data_values['cat3']['PA']['awarded']=query[0].score_awarded
            data_values['cat3']['PA']['is_empty']=False


        data_values['T']=list(TrainingDevelopment.objects.filter(emp_id=emp_id,approve_status='APPROVED',to_date__range=range_date).values('id','emp_id','category','category__value','type','type__value','from_date','to_date','role','role__value','organization_sector','organization_sector__value','incorporation_status','incorporation_status__value','title'))

        for x in data_values['T']:
            x['date']=x['to_date']
            x['type']='T'
            query=FacAppCat3.objects.update_or_create(type=x['type'],fac_app_id=FacultyAppraisal.objects.get(id=appraisal),training_development=TrainingDevelopment.objects.get(id=x['id']),status='INSERT',defaults={'status':"INSERT"})
            x['score_claimed']=query[0].score_claimed
            x['score_awarded']=query[0].score_awarded
            x['FacAppCat3_id']=query[0].id
            if x['score_claimed'] is not None:
                data_values['cat3']['T']['claimed']=data_values['cat3']['T']['claimed']+x['score_claimed']
            data_values['cat3']['T']['awarded']=query[0].score_awarded
            data_values['cat3']['T']['is_empty']=False

        data_values['L']=list(LecturesTalks.objects.filter(emp_id=emp_id,approve_status='APPROVED',date__range=range_date).values('id','emp_id','category','category__value','type','type__value','role','role__value','topic','date'))

        for x in data_values['L']:
            x['type']='L'
            query=FacAppCat3.objects.update_or_create(type=x['type'],fac_app_id=FacultyAppraisal.objects.get(id=appraisal),lectures_talks=LecturesTalks.objects.get(id=x['id']),status='INSERT',defaults={'status':"INSERT"})
            x['score_claimed']=query[0].score_claimed
            x['score_awarded']=query[0].score_awarded
            x['FacAppCat3_id']=query[0].id
            if x['score_claimed'] is not None:
                data_values['cat3']['L']['claimed']=data_values['cat3']['L']['claimed']+x['score_claimed']
            data_values['cat3']['L']['awarded']=query[0].score_awarded
            data_values['cat3']['L']['is_empty']=False

        data_values['inc_type']=Increament_types()
        data_values['degn_all']=Desgination_all()

        status=200
    data_values['result']=eligible

    return data_values


def form_data(request):
    data_values = {}
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337,])
            if check==200:
                if request.method == 'GET':
                    if request.GET['request_type']=="DEAN":
                        check=checkpermission(request,[1373,211])
                        if(check==200):
                            emp_id=request.GET['emp_id']
                            eligible=check_eligibility(emp_id)
                            if eligible=="LOCKED":
                                FacultyAppraisal.objects.filter(Emp_Id=emp_id).filter(form_filled_status="S4").update(form_filled_status="Y")
                                status=200
                            elif eligible=="ELIGIBLE":
                                data_values['data']=form(emp_id)
                                data_values['result']=eligible
                                status=200
                            else:
                                data_values['result']=eligible
                                status=200
                        else:
                            status=202
                            data_values = {"msg":"Check permission"}
                    elif request.GET['request_type']=="HOD":
                        check=checkpermission(request,[1369])
                        if(check==200):
                            emp_id=request.GET['emp_id']
                            eligible=check_eligibility(emp_id)
                            if eligible=="LOCKED":
                                FacultyAppraisal.objects.filter(Emp_Id=emp_id).filter(form_filled_status="S4").update(form_filled_status="Y")
                                status=200
                            elif eligible=="ELIGIBLE":
                                data_values['data']=form(emp_id)
                                data_values['result']=eligible
                                status=200
                            else:
                                data_values['result']=eligible
                                status=200
                        else:
                            status=202
                            data_values = {"msg":"Check permission"}
                    elif request.GET['request_type']=="EMPLOYEE":
                        emp_id = request.session['hash1']
                        eligible=check_eligibility(emp_id)

                        if eligible=="LOCKED":
                            FacultyAppraisal.objects.filter(Emp_Id=emp_id).filter(form_filled_status="S4").update(form_filled_status="Y")
                            status=200
                        elif eligible=="ELIGIBLE":
                            data_values['data']=form(emp_id)

                            data_values['result']=eligible
                            status=200
                        else:
                            data_values['result']=eligible
                            status=200
                    elif request.GET['request_type']=="GET_LIST":
                        emp_id = request.session['hash1']
                        dept_desg=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept','desg','desg__value')
                        if(request.GET['by']=="aar_faculty_appraisal_dean" and checkpermission(request,[1373])==200):

                            listing=list(AarReporting.objects.filter(reporting_no__in=['1','2'],emp_id__emp_category__value='FACULTY',emp_id__emp_status='ACTIVE',reporting_to__value=dept_desg[0]['desg__value']).values('emp_id','emp_id__name','emp_id__desg__value','emp_id__dept__value','emp_id__current_pos__value'))
                            for x in listing:
                                temp=FacultyAppraisal.objects.filter(emp_id=x['emp_id']).values('form_filled_status','emp_id','emp_id__name','emp_id__desg__value').order_by('form_filled_status')
                                if len(temp) > 0:
                                    x['form_filled_status']=temp[0]['form_filled_status']
                                    result=check_status(temp[0]['form_filled_status'])
                                    x['dean_status']=result[0]
                                    x['hod_status']=result[1]
                                    x['emp_status']=result[2]

                                else:
                                    x['form_filled_status']='N'
                                    x['dean_status']='NOT FILLED'
                                    x['hod_status']='NOT FILLED'
                                    x['emp_status']='NOT FILLED'
                        elif(checkpermission(request,[211])==200):
                            status=200
                            listing={}
                            data_values = {"msg":"Check permission"}
                        elif(request.GET['by']=="aar_faculty_appraisal_hod" and checkpermission(request,[1369])==200):   
                            listing=list(AarReporting.objects.filter(department=dept_desg[0]['dept'],reporting_to__value=dept_desg[0]['desg__value'],reporting_no = '1',emp_id__emp_category__value='FACULTY',emp_id__emp_status='ACTIVE').values('emp_id','emp_id__name','emp_id__desg__value','emp_id__dept__value','emp_id__current_pos__value'))
                            for x in listing:
                                temp=list(FacultyAppraisal.objects.filter(emp_id=x['emp_id']).values('form_filled_status'))
                                x['hod_status']='NOT FILLED'
                                x['emp_status']='NOT FILLED'
                                x['eligible']=check_eligibility(x['emp_id'])
                                for y in temp:
                                    result=check_status(temp[0]['form_filled_status'])
                                    x['hod_status']=result[1]
                                    x['emp_status']=result[2]
                            data_values=listing
                        else:
                            status=202
                            data_values = {"msg":"Check permission"}

                        data_values=listing
                        status=200
                    else:
                        data_values = {"msg":"BAD REQUEST"}
                        status=202
                else:
                    status=202
                    data_values = {"msg":"Check permission"}
            else:
                status=403
        else:
            status=401
    else:
        status=404
    return JsonResponse(data_values, status=status, safe=False)

def consolidate_data(fac_app_id):
    data_values={}
    data={}
    appraisal=fac_app_id
    session=getCurrentSession()
    total_emp_left=0
    total_hod_left=0
    total_dir_left=0
    data_values['FacultyAppraisal']=list(FacultyAppraisal.objects.filter(id=appraisal).values())
    emp_id=data_values['FacultyAppraisal'][0]['emp_id_id']
    salary=EmployeeGross_detail.objects.filter(Emp_Id=emp_id).filter(session=session).exclude(Status="DELETE").values('salary_type__value','salary_type')

    primary=list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values('title','desg','dept','desg__value','dept__value','doj','name'))

    data['Desgination']=primary[0]['desg__value']
    data['Date_of_Joining']=primary[0]['doj']
    data['Name']=str(primary[0]['title'])+str(primary[0]['name'])
    data['Employee_id']=emp_id
    data['Department']=primary[0]['dept__value']
    data['Salary_Type']=salary[0]['salary_type__value']

    data['Highest_Qualification']=data_values['FacultyAppraisal'][0]['highest_qualification']
    data['Current_Gross_salary']=data_values['FacultyAppraisal'][0]['current_gross_salary']
    data['AGP']=data_values['FacultyAppraisal'][0]['agp']
    exp=str(data_values['FacultyAppraisal'][0]['total_experience']).split('.')
    month=int(exp[1])*12
    if(month>9):
        month=str(month)[:1]
    else:
        month=str(month)[:2]
        
    data['Total_Experience']=exp[0] +' Years '+ month +' Months'
    form_filled_status=data_values['FacultyAppraisal'][0]['form_filled_status']
    result=check_status(form_filled_status)
    data['HOD_status']=result[0]
    data['Director_status']=result[1]
    data['emp_status']=result[2]
    total_emp=1
    if(data['emp_status']=="NOT FILLED"):
        total_emp_left=1
        total_hod_left=1
        total_dir_left=1
    elif(data['HOD_status']=="NOT FILLED"):
        total_emp_left=0
        total_hod_left=1
        total_dir_left=1
    elif(data['Director_status']=="NOT FILLED"):
        total_emp_left=0
        total_hod_left=0
        total_dir_left=1
    data['Achievement_Recognition']=data_values['FacultyAppraisal'][0]['achievement_recognition']
    data['Training_Needs']=data_values['FacultyAppraisal'][0]['training_needs']
    data['Suggestions']=data_values['FacultyAppraisal'][0]['suggestions']
    data['EMPLOYEE_Filled_on']=data_values['FacultyAppraisal'][0]['emp_date']
    data['HOD_Filled_on']=data_values['FacultyAppraisal'][0]['hod_date']
    data['Director_Filled_on']=data_values['FacultyAppraisal'][0]['dean_date']    

    awarded=0
    claimed=0
    data_values['FacAppCat1A1']=FacAppCat1A1.objects.filter(fac_app_id=appraisal,status='INSERT').aggregate()

    data_values['FacAppCat1A1']=FacAppCat1A1_creater(appraisal,{},"GET DATA")
    for x in data_values['FacAppCat1A1']:
        try:
            if(x['score_awarded'] != "--" and x['score_awarded'] != 0):
                awarded=awarded+x['score_awarded']/len(data_values['FacAppCat1A1'])
        except Exception as e:
            awarded=0
        try:
            if(x['score_claimed'] != "--" and x['score_claimed'] != 0):
                claimed=claimed+x['score_claimed']/len(data_values['FacAppCat1A1'])
        except Exception as e:
            claimed=0

    data['Category_1_A1_claimed']=claimed
    data['Category_1_A1_awarded']=awarded

    awarded=0
    claimed=0
    data_values['FacAppCat1A2']=FacAppCat1A2_creater(appraisal,{},"GET DATA")
    for x in data_values['FacAppCat1A2']:
        try:
            if(x['score_awarded'] != "--" and x['score_awarded'] != 0):
                # print('jijijij',x['score_awarded'])
                awarded=awarded+x['score_awarded']
        except Exception as e:
            awarded=0
        try:
            if(x['score_claimed'] != "--" and x['score_claimed'] != 0):
                # print('jikjknjknjknknjijij',x['score_claimed'])
                claimed=claimed+x['score_claimed']
        except Exception as e:
            claimed=0
    data['Category_1_A2_claimed']=claimed
    data['Category_1_A2_awarded']=awarded

    awarded=0
    claimed=0
    data_values['FacAppCat1A3']=FacAppCat1A3_creater(appraisal,{},"GET DATA")
    for x in data_values['FacAppCat1A3']:
        try:
            if(x['score_awarded'] != "--" and x['score_awarded'] != 0):
                awarded=awarded+x['score_awarded']
        except Exception as e:
            awarded=0
        try:
            if(x['score_claimed'] != "--" and x['score_claimed'] != 0):
                claimed=claimed+x['score_claimed']
        except Exception as e:
            claimed=0
    data['Category_1_A3_claimed']=claimed
    data['Category_1_A3_awarded']=awarded
    
    awarded=0
    claimed=0
    data_values['FacAppCat1A4']=FacAppCat1A4_creater(appraisal,{},"GET DATA")
    for x in data_values['FacAppCat1A4']:
        try:
            if(x['score_awarded'] != "--" and x['score_awarded'] != 0):
                awarded=awarded+x['score_awarded']
        except Exception as e:
            awarded=0
        try:
            if(x['score_claimed'] != "--" and x['score_claimed'] != 0):
                claimed=claimed+x['score_claimed']
        except Exception as e:
            claimed=0
    data['Category_1_A4_claimed']=claimed
    data['Category_1_A4_awarded']=awarded

    awarded=0
    claimed=0
    data_values['FacAppCat2A1']=FacAppCat2A1_creater(appraisal,{},"GET DATA")
    for x in data_values['FacAppCat2A1']:
        try:
            if(x['score_awarded'] != "--" and x['score_awarded'] != 0):
                awarded=awarded+x['score_awarded']
        except Exception as e:
            awarded=0
        try:
            if(x['score_claimed'] != "--" and x['score_claimed'] != 0):
                claimed=claimed+x['score_claimed']
        except Exception as e:
            claimed=0
    data['Category_2_A1_claimed']=claimed
    data['Category_2_A1_awarded']=awarded

    data_values['FacAppCat3']=FacAppCat3.objects.filter(fac_app_id=appraisal,status='INSERT').exclude(research_journal__approve_status = 'DELETE').exclude(research_journal__approve_status = 'REJECTED').exclude(research_conference__approve_status = 'DELETE').exclude(research_conference__approve_status = 'REJECTED').exclude(books__approve_status = 'DELETE').exclude(books__approve_status = 'REJECTED').exclude(project_consultancy__approve_status = 'DELETE').exclude(project_consultancy__approve_status = 'REJECTED').exclude(patent__approve_status = 'DELETE').exclude(patent__approve_status = 'REJECTED').exclude(research_guidance__approve_status = 'DELETE').exclude(research_guidance__approve_status = 'REJECTED').exclude(training_development__approve_status = 'DELETE').exclude(training_development__approve_status = 'REJECTED').exclude(lectures_talks__approve_status = 'DELETE').exclude(lectures_talks__approve_status = 'REJECTED').order_by('type').distinct()
    abbreviation={
    'J':'JOURNALS',
    'C':'CONFERENCE',
    'G':'GUIDANCE',
    'PA':'PATENT',
    'PC':'PROJECT/CONSULTANCY',
    'B':'BOOKS',
    'T':'TRAINING_AND_DEVELOPMENT',
    'L':'LECTURES_AND_TALKS',
    }
    for x in abbreviation:
        key_should_1='Category_3_'+abbreviation[x]+'_claimed'
        data[key_should_1]=0
        key_should_2='Category_3_'+abbreviation[x]+'_awarded'
        data[key_should_2]=0
    for x in data_values['FacAppCat3']:
        # print(x.type)
        key_should_1='Category_3_'+abbreviation[x.type]+'_claimed'
        try:
            key_should_1='Category_3_'+abbreviation[x.type]+'_claimed'
            data[key_should_1]=data[key_should_1]+x.score_claimed
        except Exception as e:
            key_should_1='Category_3_'+abbreviation[x.type]+'_claimed'
            data[key_should_1]=data[key_should_1]
        try:
            key_should_2='Category_3_'+abbreviation[x.type]+'_awarded'
            #data[key_should_2]=data[key_should_2]+x.score_awarded
            data[key_should_2]=x.score_awarded
        except Exception as e:
            key_should_2='Category_3_'+abbreviation[x.type]+'_awarded'
            data[key_should_2]=data[key_should_2]

    awarded=0
    claimed=0
    data_values['FacAppCat4A1']=FacAppCat4A1_creater(appraisal,{},"GET DATA")
    for x in data_values['FacAppCat4A1']:
        try:
            if(x['score_awarded'] != "--" and x['score_awarded'] != 0):
                awarded=awarded+x['score_awarded']
        except Exception as e:
            awarded=0
        try:
            if(x['score_claimed'] != "--" and x['score_claimed'] != 0):
                claimed=claimed+x['score_claimed']
        except Exception as e:
            claimed=0
    try:
        data['Category_4_A1_claimed']=claimed/len(data_values['FacAppCat4A1'])
    except:
        data['Category_4_A1_claimed']=0

    try:
        data['Category_4_A1_awarded']=awarded/len(data_values['FacAppCat4A1'])
    except:
        data['Category_4_A1_awarded']=0

    awarded=0
    claimed=0
    data_values['FacAppCat4A2']=FacAppCat4A2_creater(appraisal,{},"GET DATA")
    for x in data_values['FacAppCat4A2']:
        try:
            if(x['score_awarded'] != "--" and x['score_awarded'] != 0):
                awarded=awarded+x['score_awarded']
        except Exception as e:
            awarded=0
        try:
            if(x['score_claimed'] != "--" and x['score_claimed'] != 0):
                claimed=claimed+x['score_claimed']
        except Exception as e:
            claimed=0
    try:
        data['Category_4_A2_claimed']=round(claimed/len(data_values['FacAppCat4A2']),2)
    except:
        data['Category_4_A2_claimed']=0

    try:
        data['Category_4_A2_awarded']=round(awarded/len(data_values['FacAppCat4A2']),2)
    except:
        data['Category_4_A2_awarded']=0
    #data['Category_4_A2_claimed']=claimed
    #data['Category_4_A2_awarded']=awarded


    hod_data=FacAppRecommend.objects.filter(fac_app_id=appraisal,status='INSERT',whom='HOD').values('increment_type','increment_type__value','promoted_to','promoted_to__value','amount','recommend','remark')
    temp=const_increament_generator('HOD',emp_id,hod_data[0]['increment_type__value'],hod_data[0]['amount'],hod_data[0]['promoted_to__value'],hod_data[0]['recommend'])
    for x in temp:
        y=x.replace(" ","_")
        data["HOD_"+y]=temp[x]

    data['HOD_Remark']=hod_data[0]['remark']

    hod_data=FacAppRecommend.objects.filter(fac_app_id=appraisal,status='INSERT',whom='DEAN').values('increment_type','increment_type__value','promoted_to','promoted_to__value','amount','recommend','remark')
    temp=const_increament_generator('Director',emp_id,hod_data[0]['increment_type__value'],hod_data[0]['amount'],hod_data[0]['promoted_to__value'],hod_data[0]['recommend'])
    for x in temp:
        y=x.replace(" ","_")
        data['Director_'+y]=temp[x]
        # print("Director_"+y,temp[x])
    data['Director_Remark']=hod_data[0]['remark']

    data_values=[data,total_emp,total_emp_left,total_hod_left,total_dir_left]
    status=200
    return data_values
def fc_app_advance_report(request):
    data={'data':[]}
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[211,1345])
            if check==200:
                if request.method == 'GET':
                    if request.GET['request_type']=="CONSOLIDATED":
                        total=0
                        total_start=0
                        total_emp=0
                        total_hod=0
                        total_dir=0
                        not_elegible=0
                        status=200
                        console_data={}
                        listing=(AarReporting.objects.filter(emp_id__emp_category__value='FACULTY',emp_id__emp_status='ACTIVE',reporting_no__in=[1]).values('emp_id','emp_id__name','emp_id__desg__value','emp_id__dept__value','emp_id__dept','emp_id__mob','emp_id__email','emp_id__current_pos__value').order_by('-emp_id__dept__value'))
                        
                        prev=listing[0]['emp_id__dept__value']
                        selected_dept=listing[0]['emp_id__dept']
                        console_data['pending']=[]
                        console_data['not_elegible_list']=[]
                        def caller(prev,selected_dept):
                            console_data[prev]={}
                            console_data[prev]['id']=selected_dept
                            console_data[prev]['total']=0
                            console_data[prev]['not_elegible']=0
                            console_data[prev]['elegible']=0
                            console_data[prev]['total_emp']=0
                            console_data[prev]['total_hod']=0
                            console_data[prev]['total_dir']=0
                            console_data[prev]['total_emp_not']=0
                            console_data[prev]['total_hod_not']=0
                            console_data[prev]['total_dir_not']=0
                            console_data[prev]['pending']=[]
                            console_data[prev]['not_elegible_list']=[]
                        caller(prev,selected_dept)

                        for x in listing:
                            if(x['emp_id__dept__value']!=prev):
                                prev=x['emp_id__dept__value']
                                selected_dept=x['emp_id__dept']
                                caller(prev,selected_dept)
                            total=total+1
                            console_data[prev]['total']=console_data[prev]['total']+1
                            x['eligible']=check_eligibility(x['emp_id'])
                        

                            if x['eligible']=='NOT ELIGIBLE':
                                console_data[prev]['not_elegible']=console_data[prev]['not_elegible']+1
                                not_elegible=not_elegible+1
                                y={}
                                y['Desgination']=x.pop('emp_id__desg__value')
                                y['Name']=x.pop('emp_id__name')
                                y['Email']=x.pop('emp_id__email')
                                y['Department']=x.pop('emp_id__dept__value')
                                y['Mobile_No']=x.pop('emp_id__mob')
                                y['Employee Id']=x.pop('emp_id')

                                console_data['not_elegible_list'].append(y)
                                console_data[prev]['not_elegible_list'].append(y)

                            else:
                                console_data[prev]['elegible']=console_data[prev]['elegible']+1
                                temp=FacultyAppraisal.objects.filter(emp_id=x['emp_id']).values('emp_id','form_filled_status','emp_id__desg__value','emp_id__name','emp_id__dept__value','emp_id__mob','emp_id__email','emp_id__current_pos__value')

                                temp=list(temp)
                                if len(temp)>0:
                                    y=temp[0]
                                    total_start=total_start+1
                                    result=check_status(y['form_filled_status'])
                                    if result[0]=='FILLED' and result[1]=='FILLED' and result[2]=='FILLED':
                                        console_data[prev]['total_emp']=console_data[prev]['total_emp']+1
                                        console_data[prev]['total_hod']=console_data[prev]['total_hod']+1
                                        console_data[prev]['total_dir']=console_data[prev]['total_dir']+1
                                        total_emp=total_emp+1
                                        total_hod=total_hod+1
                                        total_dir=total_dir+1
                                    elif result[0]=='NOT FILLED' and result[1]=='FILLED' and result[2]=='FILLED':
                                        console_data[prev]['total_emp']=console_data[prev]['total_emp']+1
                                        console_data[prev]['total_hod']=console_data[prev]['total_hod']+1
                                        console_data[prev]['total_dir_not']=console_data[prev]['total_dir_not']+1
                                        total_emp=total_emp+1
                                        total_hod=total_hod+1
                                    elif result[0]=='NOT FILLED' and result[1]=='NOT FILLED' and result[2]=='FILLED':
                                        total_emp=total_emp+1
                                        console_data[prev]['total_emp']=console_data[prev]['total_emp']+1
                                        console_data[prev]['total_hod_not']=console_data[prev]['total_hod_not']+1
                                    else:
                                        console_data[prev]['total_emp_not']=console_data[prev]['total_emp_not']+1
                                        x={}
                                        x['Current Position']=y.pop('emp_id__current_pos__value')
                                        x['Name']=y.pop('emp_id__name')
                                        x['Email']=y.pop('emp_id__email')
                                        x['Department']=y.pop('emp_id__dept__value')
                                        x['Mobile_No']=y.pop('emp_id__mob')
                                        x['Employee Id']=y.pop('emp_id')

                                        console_data[prev]['pending'].append(x)
                                        console_data['pending'].append(x)
                                elif len(temp)==0:
                                    y={}
                                    y['Current Position']=x.pop('emp_id__current_pos__value')
                                    y['Name']=x.pop('emp_id__name')
                                    y['Email']=x.pop('emp_id__email')
                                    y['Department']=x.pop('emp_id__dept__value')
                                    y['Mobile_No']=x.pop('emp_id__mob')
                                    y['Employee Id']=x.pop('emp_id')
                                    console_data[prev]['pending'].append(y)
                                    console_data['pending'].append(y)


                        data['total']=total
                        data['total_emp']=total_emp
                        data['total_hod']=total_hod
                        data['total_dir']=total_dir
                        data['not_elegible']=not_elegible
                        data['total_start']=total_start
                        data['console_data']=console_data
                    elif request.GET['request_type']=="PER_DATA":
                        dept=request.GET['dept']
                        listing=[]
                        if(dept=="ALL"):
                            listing=FacultyAppraisal.objects.values_list('id',flat=True)
                        else:
                            listing=FacultyAppraisal.objects.filter(emp_id__dept=dept).values_list('id',flat=True)
                        for x in listing:
                            data_values=consolidate_data(x)
                            data['data'].append(data_values[0])
                        data_values = {"msg":"SUCCESS"}
                        status=200
                    else:
                        data_values = {"msg":"BAD REQUEST"}
                        status=202
                else:
                    status=202
                    data_values = {"msg":"Check permission"}
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data=data, status=status, safe=False)

def recommend(request):
    data_values = {}
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[1369,1373])
            if check==200:
                if request.method == 'POST':
                    appraisal=request.GET['fac_app_id_id']
                    data = json.loads(request.body.decode("utf-8'"))
                    recommend={}
                    emp_id = request.session['hash1']
                    for key in data:
                        recommend=data[key][0]
                    FacAppRecommend.objects.filter(fac_app_id=appraisal,status="INSERT",whom=recommend['whom']).update(status="DELETE")
                    temp=recommend['promoted_to']
                    if temp is None or temp=='':
                        promoted_to=None
                    else:
                        promoted_to=EmployeeDropdown.objects.get(sno=temp)  
                    temp=recommend['increment_type']
                    if temp is None or temp=='':
                        increment_type=None
                    else:
                        increment_type=AarDropdown.objects.get(sno=temp)
                    
                    FacAppRecommend.objects.update_or_create(fac_app_id=FacultyAppraisal.objects.get(id=appraisal),whom=recommend['whom'],status="INSERT",defaults={'increment_type':increment_type,'promoted_to':promoted_to,'amount':recommend['amount'],'recommend':recommend['recommend'],'remark':recommend['remark'],'by_emp_id':EmployeePrimdetail.objects.get(emp_id=emp_id)})
                    if recommend['whom']=='HOD':
                        FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA',hod_date=datetime.datetime.now())
                    else:
                        FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='DA',dean_date=datetime.datetime.now())


                    data_values = {"msg":"SUCCESS"}
                    status=200
                else:
                    status=202
                    data_values = {"msg":"Check permission"}
            else:
                status=403
        else:
            status=401
    else:
        status=500
    return JsonResponse(data_values, status=status, safe=False)

def insert_data(request):
    data_values = {}
    status=200
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check=checkpermission(request,[337])
            if check==200:
                if request.method == 'PUT':
                    data = json.loads(request.body.decode("utf-8'"))
                    emp_id=data['emp_id']
                    FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HA')

                elif request.method == 'POST':         
                    data = json.loads(request.body.decode("utf-8'"))
                    appraisal=data['fac_app_id_id']
                    by=request.GET['by']
                    emp_id = request.session['hash1']
                    query=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg','desg__value')
                    desg=query[0]['desg__value']
                    form_fill_status=FacultyAppraisal.objects.filter(id=appraisal).values('form_filled_status')
                    if request.GET['request_type']=="SUBMIT":
                        if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='Y')
                        elif by=="aar_faculty_appraisal_hod":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HA')

                    elif request.GET['request_type']=="PAGE_1":

                        # ///////////////////////////////////CATEGORY 1 STARTS//////////////////////////////////////////////////////

                        data1=data['FacAppCat1A1']
                        FacAppCat1A1.objects.filter(fac_app_id=appraisal,status= "INSERT").update(status= "DELETE")

                        obj=(FacAppCat1A1(course_paper=data['course_paper'],fac_app_id_id=appraisal,status="INSERT",lectues_calendar=data['lectues_calendar'],lectues_portal=data['lectues_portal'],score_awarded=data['score_awarded'],score_claimed=scorer('FacAppCat1A1',data['lectues_calendar'],data['lectues_portal'],'')) for data in data1)
                        qry=FacAppCat1A1.objects.bulk_create(obj)
                        if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='S1A1')
                        elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA')


                        data2=data['FacAppCat1A2']
                        FacAppCat1A2.objects.filter(fac_app_id=appraisal,status= "INSERT").update(status="DELETE")
                        obj=(FacAppCat1A2(additional_resource=data['additional_resource'],consulted=data['consulted'],status="INSERT",course_paper=data['course_paper'],prescribed=data['prescribed'],score_awarded=data['score_awarded'],score_claimed=data['score_claimed'],fac_app_id_id=appraisal) for data in data2)
                        qry=FacAppCat1A2.objects.bulk_create(obj)
                        if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='S1A2')
                        elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA')


                        data3=data['FacAppCat1A3']
                        FacAppCat1A3.objects.filter(fac_app_id=appraisal,status= "INSERT").update(status= "DELETE")
                        obj=(FacAppCat1A3(short_descriptn=data['short_descriptn'],score_awarded=data['score_awarded'],status="INSERT",score_claimed=scorer('FacAppCat1A3',data['short_descriptn'],'',''),fac_app_id_id=appraisal) for data in data3)
                        qry=FacAppCat1A3.objects.bulk_create(obj)
                        if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='S1A3')
                        elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA')
                        

                        if 'FacAppCat1A4' in data:
                            data4=data['FacAppCat1A4']
                            FacAppCat1A4.objects.filter(fac_app_id=appraisal,status= "INSERT").update(status= "DELETE")
                            obj=(FacAppCat1A4(sno=data['sno'],executed=data['executed'],extent_to_carried=data['extent_to_carried'],duties_assign=data['duties_assign'],status="INSERT",score_claimed=scorer('FacAppCat1A4',data['sno'],data['executed'],''),score_awarded=data['score_awarded'],fac_app_id_id=appraisal) for data in data4)
                            qry=FacAppCat1A4.objects.bulk_create(obj)
                            if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                                FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='S1')
                            elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                                FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA')
                        
                        FacultyAppraisal.objects.filter(id=appraisal).update(emp_date=datetime.datetime.now())
                        
                        status=200
                        data_values = {"msg":"Successfully Saved PART-I"}
                        



                        # ///////////////////////////////////CATEGORY 1 ENDS////////////////////////////////////////////////////////////////////

                    elif request.GET['request_type']=="PAGE_2":


                        # ///////////////////////////////////CATEGORY 2 STARTS//////////////////////////////////////////////////////////////////

                        data5=data['FacAppCat2A1']
                        FacAppCat2A1.objects.filter(fac_app_id=appraisal,status= "INSERT").update(status="DELETE")
                        obj=(FacAppCat2A1(average_hours=data['average_hours'],type_of_activity=data['type_of_activity'],status="INSERT",score_claimed=data['score_claimed'],score_awarded=data['score_awarded'],fac_app_id_id=appraisal) for data in data5)
                        qry=FacAppCat2A1.objects.bulk_create(obj)
                        if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='S2')
                        elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA')
                        FacultyAppraisal.objects.filter(id=appraisal).update(emp_date=datetime.datetime.now())
                        status=200
                        data_values = {"msg":"Successfully Saved PART-II"}

                        # ///////////////////////////////////CATEGORY 2 ENDS////////////////////////////////////////////////////////////////////
                    
                    elif request.GET['request_type']=="PAGE_3":

                        # ///////////////////////////////////CATEGORY 3 STARTS//////////////////////////////////////////////////////////////////
                        data8=data['T']
                        FacAppCat3.objects.filter(fac_app_id=appraisal,type='T',status= "INSERT").update(status="DELETE")
                        obj=(FacAppCat3(training_development=TrainingDevelopment.objects.get(id=data['id']),type='T',status="INSERT",score_claimed=data['score_claimed'],fac_app_id_id=appraisal)  for data in data8)
                        qry=FacAppCat3.objects.bulk_create(obj)

                        data9=data['L']
                        FacAppCat3.objects.filter(fac_app_id=appraisal,type='L',status= "INSERT").update(status="DELETE")
                        obj=(FacAppCat3(lectures_talks=LecturesTalks.objects.get(id=data['id']),type='L',status="INSERT",score_claimed=data['score_claimed'],fac_app_id_id=appraisal)  for data in data9)
                        qry=FacAppCat3.objects.bulk_create(obj)
                        FacultyAppraisal.objects.filter(id=appraisal).update(emp_date=datetime.datetime.now())
                        status=200
                        data_values = {"msg":"Successfully Saved PART-III"}

                        # ///////////////////////////////////CATEGORY 3 ENDS////////////////////////////////////////////////////////////////////

                    elif request.GET['request_type']=="PAGE_4":

                        # ///////////////////////////////////CATEGORY 4 STARTS//////////////////////////////////////////////////////////////////

                        try:
                            FacAppCat4A1.objects.filter(fac_app_id=appraisal).update(status="DELETE")
                            data10=data['other_ins_det']
                            if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                                FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='S4A1')
                            elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                                FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA')
                            obj=(FacAppCat4A1(branch_details=data['best_institute'],result_clear_pass=data['best_inst_avg'],result_external=data['sec_best_avg'],subject=data['sec_best_institute'],status="OTHER",fac_app_id_id=appraisal) for data in data10)
                            qry=FacAppCat4A1.objects.bulk_create(obj)
                            
                            data6=data['FacAppCat4A1']

                            flag=0
                            for info in data6:

                                first_mark=0
                                second_mark=0
                                try:
                                    first_mark=data10[flag]['sec_best_avg']
                                    second_mark=data10[flag]['best_inst_avg']
                                except Exception as e:
                                    print(e)
                                qry=FacAppCat4A1.objects.create(branch_details=info['branch_details'],stu_50_59=info['stu_50_59'],result_clear_pass=info['result_clear_pass'],stu_below_40=info['stu_below_40'],result_external=info['result_external'],score_claimed=scorer('FacAppCat4A1',info['score_claimed'],first_mark,second_mark),stu_40_49=info['stu_40_49'],score_awarded=info['score_awarded'],stu_above_60=info['stu_above_60'],subject=info['subject'],status="INSERT",fac_app_id_id=appraisal)
                                flag=flag+1
                        except Exception as e:
                            FacAppCat4A1.objects.filter(fac_app_id=appraisal).update(status="DELETE")
                            flag=1

                        if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='S4A1')
                        elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA')
                        data7=data['FacAppCat4A2']
                        FacAppCat4A2.objects.filter(fac_app_id=appraisal).update(status="DELETE")
                        obj=(FacAppCat4A2(section=data['section'],semester=data['semester'],branch=data['branch'],student_feedback=data['student_feedback'],subject=data['subject'],status="INSERT",score_claimed=scorer('FacAppCat4A2',data['student_feedback'],'',''),score_awarded=data['score_awarded'],fac_app_id_id=appraisal) for data in data7)
                        qry=FacAppCat4A2.objects.bulk_create(obj)
                        if by=="aar_faculty_appraisal_emp" and form_fill_status!="Y":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='S')
                        elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HSA')


                        data0=data['FacultyAppraisal']
                        FacultyAppraisal.objects.filter(id=appraisal).update(achievement_recognition=data0['achievement_recognition'],suggestions=data0['suggestions'],training_needs=data0['training_needs'])
                        FacultyAppraisal.objects.filter(id=appraisal).update(emp_date=datetime.datetime.now())
                        status=200
                        data_values = {"msg":"Successfully Saved PART-IV"}
                        if flag==1:
                            status=202  
                            data_values = {"msg":"Not Saved PART-IV"}

                    elif request.GET['request_type']=="PAGE_5":

                        data6=data['cat3']
                        for key in data6:
                            FacAppCat3.objects.filter(fac_app_id=appraisal,type=key,status="INSERT").exclude(score_claimed__isnull=True).update(score_awarded=data6[key]['awarded'])

                        if by=="aar_faculty_appraisal_hod":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HA')
                        elif by=="aar_faculty_appraisal_hod" and form_fill_status!="HA":
                            FacultyAppraisal.objects.filter(id=appraisal).update(form_filled_status='HA')
                        FacultyAppraisal.objects.filter(id=appraisal).update(emp_date=datetime.datetime.now())
                        status=200
                        data_values = {"msg":"Successfully Saved PART-V"}


                        # /////////////////////////////////////////////////////////////////////////////////////////

                    else:                   
                        status=202
                        data_values = {"msg":"Bad Request"}

                else:
                    status=202
                    data_values = {"msg":"Check permission"}
            else:
                status=403
                data_values = {"msg":"Check permission"}

        else:
            status=401
            data_values = {"msg":"Check permission"}

    else:
        status=500
        data_values = {"msg":"Check permission"}

    return JsonResponse(data_values, status=status, safe=False)

