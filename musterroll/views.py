from django.shortcuts import render
from dashboard.models import LeftPanel
from django.http import JsonResponse
from django.db.models import F, Q, Sum,Count
import json
import requests
import time
from django.contrib.auth.models import User
import datetime
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, requestMethod, functions
from StudentMMS.constants_functions import requestType

from .models import EmployeeAcademic, EmployeeDocuments, EmployeeSeparation, EmployeeAddress, EmployeeResearch, Roles, Reporting, EmployeePerdetail, NoDuesEmp, NoDuesHead, Shifts, AarDropdown, Employee_Designations, AarReporting, EmployeeCertification, Extension, EmployeeExperience
from login.models import EmployeePrimdetail, EmployeeDropdown, AuthUser
from Registrar.models import Semtiming
from leave.models import Leaveapproval, Leaves
from grievance.models import GrievanceData

from aar.views import get_highest_qualification
from login.views import check, checkpermission

from Accounts.views import stored_gross_payable_salary_components, stored_arrear, calculate_constant_deduction_stored, calculate_variable_deduction_stored, calculate_income_tax_sum, hra_exemption_formula3, hra_exemption_formula2, calculate_loss_deductions, calculate_income_tax, calculate_tax_after_rebate, declaration_components, calculate_epf, calculate_other_income ,getCurrentSession
from Accounts.models import DaysGenerateLog, EmployeePayableDays, AccountsDropdown, Income_Tax_Paid, Employee_Declaration, SalaryIngredient, MonthlyPayable_detail, MonthlyArrear_detail, AccountsSession, Income_Tax_Paid, MonthlyArrear_detail, MonthlyDeductionValue

####################################### EMPLOYEE DETAILS ###############################################


def get_employee_details(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        user_name = data['username']
        password = data['password']
        data_values = []
        data = {}
        data2 = []

        if ((user_name == "00001") and (password == "admin")):
            status = 200
            qry = EmployeeDropdown.objects.filter(field="DEPARTMENT").values('sno', 'value').exclude(value__isnull=True)
            for q in qry:
                data = EmployeePerdetail.objects.filter(emp_id__dept=q['sno']).values('emp_id', 'emp_id__name', 'emp_id__mob', 'emp_id__email', 'image_path')
                data2.append({'data': list(data), 'dept': q['value']})
            data_values = {'Data': list(data2)}
        else:
            msg = "NOT LOGGED IN"
            status = 401
    return JsonResponse(data=data_values, status=status)


def get_reporting_employees(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if(check == 200):
                if(request.method == 'GET'):
                    qry_dept_desg = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1'], emp_status="ACTIVE").values('dept', 'desg')

                    qry_emp = Reporting.objects.filter(department=qry_dept_desg[0]['dept'], reporting_to=qry_dept_desg[0]['desg'], reporting_no='1', emp_id__emp_status='ACTIVE').values('emp_id', 'emp_id__name')
                    status = 200
                    msg = "Success"
                    data_values = {'data': list(qry_emp)}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)

############################################ get organization, dept, employee ############################


def ExtractDepartment_all_organizations(request):
    data_values = ''
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'GET'):
                    qry1 = EmployeeDropdown.objects.filter(field='Department').exclude(pid__isnull=True).exclude(value__isnull=True).extra(select={'sno': 'sno', 'value': 'value'}).values('sno', 'value')
                    data_values = {'dept': list(qry1)}
                    status = 200
                    msg = "Success"
                    data_values = {'data': data_values, 'msg': msg}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def get_details(request):

    data1 = []
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337, 1345, 1371])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'organization':
                        data = EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="ORGANIZATION").values('sno', 'value')
                        for d in data:
                            data1.append({'sno': d['sno'], 'value': d['value']})
                    
                    elif request.GET['request_type'] == "department":
                        dept_sno = EmployeeDropdown.objects.filter(pid=request.GET['org'], value="DEPARTMENT").values('sno')
                        data = EmployeeDropdown.objects.exclude(value__isnull=True).filter(pid=dept_sno[0]['sno'], field="DEPARTMENT").values('sno', 'value')
                        for d in data:
                            data1.append({'sno': d['sno'], 'value': d['value']})
                    
                    elif request.GET['request_type'] == "employee":
                        data = EmployeePrimdetail.objects.filter(dept=request.GET['dept']).values('emp_id', 'name')
                        for d in data:
                            data1.append({'emp_code': d['emp_id'], 'name': d['name']})
                    
                    elif request.GET['request_type'] == 'emp_category':
                        qry2 = EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).extra(select={'ev': 'value', 'es': 'sno'}).values('ev', 'es')
                        data1 = list(qry2)

                    # elif request.GET['request_type'] == 'type_of_exp':
                    #     qry2 = EmployeeDropdown.objects.filter(field="TYPE OF EXPERIENCE").exclude(value__isnull=True).values('sno', 'value')
                    #     data1 = list(qry2)
                    #     temp_list = {'sno':None,'value':"EXPERIENCE BEFORE KIET"}
                    #     data1.insert(-1,temp_list)

                    status = 200
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data1, safe=False)

############################################################ADD EMPLOYEE##############################################


def Add_Musterroll(request):
    msg=""
    data=""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request,[211,337])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'fetch_category':
                        field_id=request.GET['emp_category']
                        j=0
                        field = EmployeeDropdown.objects.filter(pid=field_id).exclude(value__isnull=True).extra(select={'category_id':'sno','category_name':'value'}).values('category_id','category_name')
                        for x in range(0,len(field)):
                            test=EmployeeDropdown.objects.filter(pid=field[x]['category_id']).exclude(value__isnull=True).extra(select={'subid': 'sno','subvalue':'value'}).values('subid','subvalue')
                            field[x]['subcategory']=list(test)
                        data={'data':list(field)}
                        status=200
                        # return JsonResponse(status=status,data=a)
                    else:
                        qry1=EmployeeDropdown.objects.filter(field="TYPE OF EMPLOYMENT").exclude(value__isnull=True).extra(select={'v':'value','s':'sno'}).values('v','s')

                        qry2=EmployeeDropdown.objects.filter(field="CATEGORY OF EMPLOYEE").exclude(value__isnull=True).extra(select={'ev':'value','es':'sno'}).values('ev','es')
                        qry2_a=EmployeeDropdown.objects.filter(field='STATE').exclude(value__isnull=True).extra(select={'state_id':'sno','state_name':'value'}).values('state_id','state_name')

                        qry3=EmployeeDropdown.objects.filter(value="DESIGNATION").exclude(value__isnull=True).extra(select={'id':'sno','field':'field'}).values('id','field')
                        qry_len=len(qry3)
                        for x in range(0,qry_len):
                            qry3_a=EmployeeDropdown.objects.filter(pid=qry3[x]['id']).exclude(value__isnull=True).extra(select={'desg_id':'sno','desg_name':'value'}).values('desg_id','desg_name')
                            qry3[x]['designation']=list(qry3_a)
                        qry4=EmployeeDropdown.objects.filter(field="SHIFT SETTINGS").exclude(value__isnull=True).extra(select={'sv':'value','ss':'sno'}).values('sv','ss')
                        #print(qry4)
                        #l=0
                        arr=[]
                        arr1=[]
                        #print(qry3)

            ###################################################################################################################################################################

            # THE FOLLOWING COMMENTED CODE IS FOR THE CASE IF ANY NEW CATEGORY IS ADDED IN SHIFT SETTINGS IN EMPLOYEE EmployeeDropdown OTHER THAN FIX AND FLEXIBLE

            ####################################################################################################################################################################

                        ''' if qry4.count()>0:
                            for i in qry4:
                                #print(i)
                                sub_value_id=i['ss']
                                print(sub_value_id)
                                qry4_a=EmployeeDropdown.objects.filter(pid=sub_value_id).exclude(value__isnull=True).extra(select={'subvalue_id':'sno','subvalue':'value'}).values('subvalue_id','subvalue')
                                #print(qry4_a)
                                k=0
                                for j in qry4_a:
                                    arr.append(qry4_a[k]['subvalue'])
                                    arr1.append(qry4_a[k]['subvalue_id'])
                                    #print("hi")
                                    k=k+1

                                qry4[l]['sub_field']=arr
                                arr=[]
                                qry4[l]['sub_value_id']=arr1
                                arr1=[]
                                #print("Hi")#
                                #qry4[a]['sub_value_id']=qry4[0]['subvalue_id']
                                l=l+1
                        print(qry4)'''

                        qry5=EmployeeDropdown.objects.filter(field="TITLE").exclude(value__isnull=True).extra(select={'tv':'value','ts':'sno'}).values('tv','ts')

                        qry6=EmployeeDropdown.objects.filter(field="POSITION").exclude(value__isnull=True).extra(select={'pv':'value','ps':'sno'}).values('pv','ps')
                        qry7=EmployeeDropdown.objects.filter(field="ROLES").exclude(value__isnull=True).extra(select={'av':'value','as':'sno'}).values('av','as')
                        qry8=EmployeeDropdown.objects.filter(field="BLOOD GROUP").exclude(value__isnull=True).extra(select={'bv':'value','bs':'sno'}).values('bv','bs')
                        qry9=EmployeeDropdown.objects.filter(field="GENDER").exclude(value__isnull=True).extra(select={'gv':'value','gs':'sno'}).values('gv','gs')
                        qry10=EmployeeDropdown.objects.filter(field="NATIONALITY").exclude(value__isnull=True).extra(select={'nv':'value','ns':'sno'}).values('nv','ns')
                        qry11=EmployeeDropdown.objects.filter(field="CASTE").exclude(value__isnull=True).extra(select={'cv':'value','cs':'sno'}).values('cv','cs')
                        qry12=EmployeeDropdown.objects.filter(field="MARITAL STATUS").exclude(value__isnull=True).extra(select={'mv':'value','ms':'sno'}).values('mv','ms')
                        qry13=EmployeeDropdown.objects.filter(field="RELIGION").exclude(value__isnull=True).extra(select={'rv':'value','rs':'sno'}).values('rv','rs')
                        qry14=EmployeeDropdown.objects.filter(field="DEPARTMENT").exclude(value__isnull=True).extra(select={'dev':'value','des':'sno'}).values('dev','des')
                        qry15=EmployeeDropdown.objects.filter(field="REGULAR").exclude(value__isnull=True).extra(select={'rev':'value','rs':'sno'}).values('rs','rev')
                        qry16=EmployeeDropdown.objects.filter(field="FIX").exclude(value__isnull=True).extra(select={'fiv':'value','fis':'sno'}).values('fis','fiv')
                        qry17=EmployeeDropdown.objects.filter(field="FLEXIBLE").exclude(value__isnull=True).extra(select={'flv':'value','fls':'sno'}).values('fls','flv')

                        qry19=EmployeeDropdown.objects.filter(field="UNIVERSITY").exclude(value__isnull=True).extra(select={'uv':'value','us':'sno'}).values('uv','us')
                        qry20=EmployeeDropdown.objects.filter(field="BOARD").exclude(value__isnull=True).extra(select={'bov':'value','bos':'sno'}).values('bov','bos')
                        qry21=EmployeeDropdown.objects.filter(field="DEGREE").exclude(value__isnull=True).extra(select={'dgv':'value','dgs':'sno'}).values('dgv','dgs')
                        qry22=EmployeeDropdown.objects.filter(field="P.HD. STAGE").exclude(value__isnull=True).extra(select={'stv':'value','sts':'sno'}).values('stv','sts')
                        #qry23=EmployeeDropdown.objects.filter(field="DOCTRATE").exclude(value__isnull=True).extra(select={'doc_val':'value','doc_id':'sno'}).values('doc_val','doc_id')
                        qry23=EmployeeDropdown.objects.filter(field="ORGANIZATION").exclude(value__isnull=True).extra(select={'org_id':'sno','org_name':'value'}).values('org_id','org_name')

                        #print(qry16)
                        #print(qry17)
                        msg="Success"
                        status = 200
                        data={'msg':msg,'data':{'toe':list(qry1),'coe':list(qry2),'state':list(qry2_a),'desg':list(qry3),'shift':list(qry4),'title':list(qry5),'cp':list(qry6),'ar':list(qry7),'bg':list(qry8),'gender':list(qry9),'nationality':list(qry10),'caste':list(qry11),'ms':list(qry12),'re':list(qry13),'dept':list(qry14),'regular':list(qry15),'fix':list(qry16),'flexible':list(qry17),'uni':list(qry19),'board':list(qry20),'degree':list(qry21),'stage':list(qry22),'organization':list(qry23)}}
                        #return HttpResponse(msg)
                        # return JsonResponse(status=status,data=data_values)
                elif request.method == 'POST':
                    data = json.loads(request.body)
                    print(data)
                    added_by_id = request.session['hash1']
                    emp_per={}
                    emp_prim={}
                    address={}
                    reporting={}
                    role={}
                    emp_desg={}
                    emp_acad={}
                    # emp_research={}
                    emp_doc={}
                    emp=AuthUser.objects.exclude(username__in=['20170701','20170703','20170702','20170704','74177']).exclude(username__contains='1822').filter(user_type='Employee').extra({'user':"CAST(username as UNSIGNED)"}).order_by('-user').values('user')

                    emp_id=int(emp[0]['user'])+1

                    if 'email' in data:
                        email=data['email']
                    else:
                        email='kiet.'+str(emp_id)+'@kiet.edu'
                    na=data['name']
                    name=na.split()
                    ln=''
                    fn=''
                    size=len(name)
                    if size>1:
                        fn=na.rsplit(' ', 1)[0]
                        ln=name[len(name)-1]
                    else:
                        fn=na
                        ln=''
                    user = User.objects.create_user(username=str(emp_id), email=email, password='ERP@123',first_name=fn,last_name=ln)
                    print(user)
                    # user.first_name = fn
                    # user.last_name = ln
                    # user.user_type = 'Employee'
                    # user.save()
                    #print(data['diploma_degree_path'])
                    emp_prim['emp_id']=AuthUser.objects.get(username=emp_id)
                    print(emp_prim)
                    if 'organization' in data:
                        emp_prim['organization']=EmployeeDropdown.objects.get(sno=data['organization'])
                    else:
                        emp_prim['organization']=None
                    if 'category_cadre' in data:
                        emp_prim['cadre']=EmployeeDropdown.objects.get(sno=data['category_cadre'])
                    else:
                        emp_prim['cadre']=None
                    if 'category_lader' in data:
                        emp_prim['ladder']=EmployeeDropdown.objects.get(sno=data['category_lader'])
                    else:
                        emp_prim['ladder']=None
                    if 'name' in data:
                        emp_prim['name']=data['name']
                    else:
                        emp_prim['name']=None
                    if 'fname' in data:
                        emp_per['fname']=data['fname']
                    else:
                        emp_per['fname']=None
                    if 'image' in data:
                        emp_per['image_path']=data['image']
                    else:
                        emp_per['image_path']=None
                    if 'mname' in data:
                        emp_per['mname']=data['mname']
                    else:
                        emp_per['mname']=None
                    if 'dob' in data:
                        emp_per['dob']=data['dob']
                    else:
                        emp_per['dob']=None
                    if 'title' in data:
                        emp_prim['title']=EmployeeDropdown.objects.get(sno=data['title'])
                    else:
                        emp_prim['title']=None
                    if 'shift' in data:
                        emp_prim['shift'] =EmployeeDropdown.objects.get(sno=data['shift'])
                    else:
                        emp_prim['shift']=None
                    if 'emp_category' in data:
                        emp_prim['emp_category']=EmployeeDropdown.objects.get(sno=data['emp_category'])
                    else:
                        emp_prim['emp_category']=None
                    if 'desg' in data:
                        emp_prim['desg']=EmployeeDropdown.objects.get(sno=data['desg'])
                    else:
                        emp_prim['desg']=None
                    if 'emp_type' in data:
                        emp_prim['emp_type']=EmployeeDropdown.objects.get(sno=data['emp_type'])
                    else:
                        emp_prim['emp_type']=None

                    if 'dept' in data:
                        emp_prim['dept']=EmployeeDropdown.objects.get(sno=data['dept'])
                    else:
                        emp_prim['dept']=None
                    if 'bg' in data:
                        emp_per['bg']=EmployeeDropdown.objects.get(sno=data['bg'])
                    else:
                        emp_per['bg']=None
                    if 'gender' in data:
                        emp_per['gender']=EmployeeDropdown.objects.get(sno=data['gender'])
                    else:
                        emp_per['gender']=None
                    if 'current_pos' in data:
                        emp_prim['current_pos']=EmployeeDropdown.objects.get(sno=data['current_pos'])
                    else:
                        emp_prim['current_pos']=None
                    if 'join_pos' in data:
                        emp_prim['join_pos']=EmployeeDropdown.objects.get(sno=data['join_pos'])
                    else:
                        emp_prim['join_pos']=None
                    if 'reporting_no' in data :
                        reporting['reporting_no']=data['reporting_no']
                    else:
                        reporting['reporting_no']=None
                    if 'department' in data :
                        reporting['department']=data['department']
                    else:
                        reporting['department']=None
                    if 'designation' in data :
                        reporting['reporting_to']=sno=data['designation']
                    else:
                        reporting['reporting_to']=None
                    if 'nationality' in data:
                        emp_per['nationality']=EmployeeDropdown.objects.get(sno=data['nationality'])
                    else:
                        emp_per['nationality']=None
                    if 'caste' in data:
                        emp_per['caste']=EmployeeDropdown.objects.get(sno=data['caste'])
                    else:
                        emp_per['caste']=None
                    if 'aadhar_num' in data:
                        emp_per['aadhar_num']=data['aadhar_num']
                    else:
                        emp_per['aadhar_num']=None
                    if 'pan_no' in data:
                        emp_per['pan_no']=data['pan_no']
                    else:
                        emp_per['pan_no']=None
                    if 'marital_status' in data:
                        emp_per['marital_status']=EmployeeDropdown.objects.get(sno=data['marital_status'])
                    else:
                        emp_per['marital_status']=None
                    if 'religion' in data:
                        emp_per['religion']=EmployeeDropdown.objects.get(sno=data['religion'])
                    else:
                        emp_per['religion']=None
                    if 'roles' in data:
                        role['roles']=data['roles']
                    else:
                        role['roles']=None
                    if 'add_desg' in data:
                        emp_desg['add_desg']=data['add_desg']
                    else:
                        emp_desg['add_desg']=None
                    if 'p_add1' in data:
                        address['p_add1']=data['p_add1']
                    else:
                        address['p_add1']=None
                    if 'p_add2' in data:
                        address['p_add2']=data['p_add2']
                    else:
                        address['p_add2']=None
                    if 'p_city' in data:
                        address['p_city']=data['p_city']
                    else:
                        address['p_city']=None
                    if 'p_district' in data:
                        address['p_district']=data['p_district']
                    else:
                        address['p_district']=None
                    if 'p_state' in data and data['p_state']!=None:
                        address['p_state']=EmployeeDropdown.objects.get(sno=data['p_state'])
                    else:
                        address['p_state']=None
                    if 'p_pincode' in data:
                        address['p_pincode']=data['p_pincode']
                    else:
                        address['p_pincode']=None
                    if 'c_add1' in data:
                        address['c_add1']=data['c_add1']
                    else:
                        address['c_add1']=None
                    if 'c_add2' in data:
                        address['c_add2']=data['c_add2']
                    else:
                        address['c_add2']=None
                    if 'c_city' in data:
                        address['c_city']=data['c_city']
                    else:
                        address['c_city']=None
                    if 'c_district' in data:
                        address['c_district']=data['c_district']
                    else:
                        address['c_district']=None
                    if 'c_state' in data and data['c_state']!=None:
                        address['c_state']=EmployeeDropdown.objects.get(sno=data['c_state'])
                    else:
                        address['c_state']=None
                    if 'c_pincode' in data:
                        address['c_pincode']=data['c_pincode']
                    else:
                        address['c_pincode']=None
                    if 'mob' in data:
                        emp_prim['mob']=data['mob']
                    else:
                        emp_prim['mob']=None
                    if 'join_date' in data:
                        emp_prim['doj']=data['join_date']
                    else:
                        emp_prim['doj']=None
                    if 'mob1' in data:
                        emp_prim['mob1']=data['mob1']
                    else:
                        emp_prim['mob1']=None
                    if 'email' in data:
                        emp_prim['email']=data['email']
                    else:
                        emp_prim['email']=None
                    if 'pass_year_10' in data:
                        emp_acad['pass_year_10'] =data['pass_year_10']
                    else:
                        emp_acad['pass_year_10']=None
                    if 'board_10' in data and data['board_10']!=None:
                        emp_acad['board_10'] = EmployeeDropdown.objects.get(sno=data['board_10'])
                    else:
                        emp_acad['board_10']=None
                    if 'cgpa_per_10' in data:
                        emp_acad['cgpa_per_10'] = data['cgpa_per_10']
                    else:
                        emp_acad['cgpa_per_10']=None
                    if '10th_marksheet_path' in data:
                        emp_doc['marksheet_10'] = data['10th_marksheet_path']
                    else:
                        emp_doc['marksheet_10']=None
                    if 'pass_year_12' in data:
                        emp_acad['pass_year_12'] = data['pass_year_12']
                    else:
                        emp_acad['pass_year_12']=None
                    if 'board_12' in data and data['board_12']!=None:
                        emp_acad['board_12'] = EmployeeDropdown.objects.get(sno=data['board_12'])
                    else:
                        emp_acad['board_12']=None
                    if 'cgpa_per_12' in data:
                        emp_acad['cgpa_per_12'] = data['cgpa_per_12']
                    else:
                        emp_acad['cgpa_per_12']=None
                    if '12th_marksheet_path' in data:
                        emp_doc['marksheet_12'] = data['12th_marksheet_path']
                    else:
                        emp_doc['marksheet_12']=None
                    if 'pass_year_dip' in data:
                        emp_acad['pass_year_dip'] = data['pass_year_dip']
                    else:
                        emp_acad['pass_year_dip']=None
                    if 'univ_dip' in data and data['univ_dip']!=None:
                        emp_acad['univ_dip'] = EmployeeDropdown.objects.get(sno=data['univ_dip'])
                    else:
                        emp_acad['univ_dip']=None
                    if 'cgpa_per_dip' in data:
                        emp_acad['cgpa_per_dip'] = data['cgpa_per_dip']
                    else:
                        emp_acad['cgpa_per_dip']=None
                    if 'diploma_degree_path' in data:
                        emp_doc['marksheet_dip'] = data['diploma_degree_path']
                    else:
                        emp_doc['marksheet_dip']=None
                    if 'pass_year_ug' in data:
                        emp_acad['pass_year_ug'] = data['pass_year_ug']
                    else:
                        emp_acad['pass_year_ug']=None
                    if 'univ_ug' in data and data['univ_ug']!=None:
                        emp_acad['univ_ug'] = EmployeeDropdown.objects.get(sno=data['univ_ug'])
                    else:
                        emp_acad['univ_ug']=None
                    if 'degree_ug' in data and data['degree_ug']!=None:
                        emp_acad['degree_ug'] = EmployeeDropdown.objects.get(sno=data['degree_ug'])
                    else:
                        emp_acad['degree_ug']=None
                    if 'cgpa_per_ug' in data:
                        emp_acad['cgpa_per_ug'] = data['cgpa_per_ug']
                    else:
                        emp_acad['cgpa_per_ug']=None
                    if 'ug_degree_path' in data:
                        emp_doc['marksheet_ug'] = data['ug_degree_path']
                    else:
                        emp_doc['marksheet_ug']=None
                    if 'pass_year_pg' in data:
                        emp_acad['pass_year_pg'] = data['pass_year_pg']
                    else:
                        emp_acad['pass_year_pg']=None
                    if 'univ_pg' in data and data['univ_pg']!=None:
                        emp_acad['univ_pg'] = EmployeeDropdown.objects.get(sno=data['univ_pg'])
                    else:
                        emp_acad['univ_pg']=None
                    if 'degree_pg' in data and data['degree_pg']!=None:
                        emp_acad['degree_pg'] = EmployeeDropdown.objects.get(sno=data['degree_pg'])
                    else:
                        emp_acad['degree_pg']=None
                    if 'cgpa_per_pg' in data:
                        emp_acad['cgpa_per_pg'] = data['cgpa_per_pg']
                    else:
                        emp_acad['cgpa_per_pg']=None
                    if 'pg_degree_path' in data:
                        emp_doc['marksheet_pg'] = data['pg_degree_path']
                    else:
                        emp_doc['marksheet_pg']=None
                    if 'doctrate' in data:
                        emp_acad['doctrate'] = data['doctrate']
                    else:
                        emp_acad['doctrate']=None
                    if 'univ_doctrate' in data and data['univ_doctrate']!=None:
                        emp_acad['univ_doctrate'] = EmployeeDropdown.objects.get(sno=data['univ_doctrate'])
                    else:
                        emp_acad['univ_doctrate']=None
                    if 'stage_doctrate' in data and data['stage_doctrate']!=None:
                        emp_acad['stage_doctrate'] = EmployeeDropdown.objects.get(sno=data['stage_doctrate'])
                    else:
                        emp_acad['stage_doctrate']=None
                    if 'date_doctrate' in data:
                        try:
                            valid_date = time.strptime(data['date_doctrate'], '%Y-%m-%d')
                            emp_acad['date_doctrate'] = data['date_doctrate']
                        except ValueError:
                            emp_acad['date_doctrate']=None
                    else:
                        emp_acad['date_doctrate'] = None
                    if 'research_topic_doctrate' in data:
                        emp_acad['research_topic_doctrate'] = data['research_topic_doctrate']
                    else:
                        emp_acad['research_topic_doctrate']=None
                    if 'doctrate_degree_path' in data:
                        emp_doc['marksheet_doctrate'] = data['doctrate_degree_path']
                    else:
                        emp_doc['marksheet_doctrate']=None
                    if 'pass_year_other' in data:
                        emp_acad['pass_year_other'] = data['pass_year_other']
                    else:
                        emp_acad['pass_year_other']=None
                    if 'degree_other' in data and data['degree_other']!=None:
                        emp_acad['degree_other'] = EmployeeDropdown.objects.get(sno=data['degree_other'])
                    else:
                        emp_acad['degree_other']=None
                    if 'univ_other' in data and data['univ_other']!=None:
                        emp_acad['univ_other'] = EmployeeDropdown.objects.get(sno=data['univ_other'])
                    else:
                        emp_acad['univ_other']=None
                    if 'cgpa_per_other' in data:
                        emp_acad['cgpa_per_other'] = data['cgpa_per_other']
                    else:
                        emp_acad['cgpa_per_other']=None
                    if 'area_spl_other' in data:
                        emp_acad['area_spl_other'] = data['area_spl_other']
                    else:
                        emp_acad['area_spl_other']=None
                    if 'other_doc_path' in data:
                        emp_doc['marksheet_other'] = data['other_doc_path']
                    else:
                        emp_doc['marksheet_other']=None
                    if 'cc' in data:
                        emp_doc['character_certificate'] = data['cc']
                    else:
                        emp_doc['character_certificate']=None
                    if 'medical' in data:
                        emp_doc['medical_fitness'] = data['medical']
                    else:
                        emp_doc['medical_fitness']=None
                    if 'emp_experience' in data:
                        emp_doc['experience_certificate'] = data['emp_experience']
                    else:
                        emp_doc['experience_certificate']=None
                    # if 'research_years' in data:
                    #     emp_research['research_years'] = data['research_years']
                    # else:
                    #     emp_research['research_years']=None
                    # if 'research_months' in data:
                    #     emp_research['research_months'] = data['research_months']
                    # else:
                    #     emp_research['research_months']=None
                    # if 'industry_years' in data:
                    #     emp_research['industry_years'] = data['industry_years']
                    # else:
                    #     emp_research['industry_years']=None
                    # if 'industry_months' in data:
                    #     emp_research['industry_months'] = data['industry_months']
                    # else:
                    #     emp_research['industry_months']=None
                    # if 'teaching_years' in data:
                    #     emp_research['teaching_years'] = data['teaching_years']
                    # else:
                    #     emp_research['teaching_years']=None
                    # if 'teaching_months' in data:
                    #     emp_research['teaching_months'] = data['teaching_months']
                    # else:
                    #     emp_research['teaching_months']=None
                    # if 'remark' in data:
                    #     emp_research['remark'] = data['remark']
                    # else:
                    #     emp_research['remark']=None
                    if 'pg_degree' in data:
                        emp_doc['pg_degree']=data['pg_degree']
                    else:
                        emp_doc['pg_degree']=''
                    if 'ug_degree' in data:
                        emp_doc['ug_degree']=data['ug_degree']
                    else:
                        emp_doc['ug_degree']=''
                    print("fgfvgfvyash")
                    print(emp_prim)
                    if emp_prim:
                        qry_b = EmployeePrimdetail.objects.create(**emp_prim)
                        print(qry_b)
                    print("jhg")
                    #qry=EmployeePrimdetail.objects.extra(select={'id':'emp_id'}).values('id').order_by('-emp_id')
                    last_id=emp_prim['emp_id']
                    print(last_id)
                    # l_id=emp_doc['emp_id']=reporting_emp_id=address['emp_id']=emp_acad['emp_id']=emp_research['emp_id']=emp_per['emp_id']=EmployeePrimdetail.objects.get(emp_id=last_id)
                    l_id=emp_doc['emp_id']=reporting_emp_id=address['emp_id']=emp_acad['emp_id']=emp_per['emp_id']=EmployeePrimdetail.objects.get(emp_id=last_id.username)
                    if emp_per:
                        print("Hi")
                        qry_a = EmployeePerdetail.objects.create(**emp_per)
                    print(address)
                    if address:

                        qry_c = EmployeeAddress.objects.create(**address)

                    print(role)
                    if role:
                        for i in role['roles']:
                            if i!='':
                                qry_e = Roles.objects.create(roles=EmployeeDropdown.objects.get(sno=i),emp_id=l_id)

                    if emp_desg['add_desg']:
                        for i in emp_desg['add_desg']:
                            if i!='':
                                ins_by=request.session["hash1"]
                                status='INSERT'
                                time_stamp=str(datetime.now())
                                qry_e = Employee_Designations.objects.create(emp_designations=EmployeeDropdown.objects.get(sno=i),emp_id=l_id,status=status,time_stamp=time_stamp,inserted_by=EmployeePrimdetail.objects.get(emp_id=ins_by))
                    if reporting:
                        print("Hijh")
                        a=1
                        if(reporting['department'] and reporting['reporting_to']):
                            for i,y in enumerate(reporting['department']) and enumerate(reporting['reporting_to']):
                                print(reporting['department'][i])
                                print("Hi")
                                qry1=Reporting.objects.create(emp_id=reporting_emp_id,reporting_to=EmployeeDropdown.objects.get(sno=y),department=EmployeeDropdown.objects.get(sno=reporting['department'][i]),reporting_no=a)
                                a=a+1

                        else:
                            qry1=""

                    print(emp_acad)
                    if emp_acad:
                        qry_f = EmployeeAcademic.objects.create(**emp_acad)
                    # if emp_research:
                    #     qry_g = EmployeeResearch.objects.create(**emp_research)
                    print('hgfd')
                    if 'experience' in data:
                        objs = (EmployeeExperience(from_date=i['from_date'],to_date=i['to_date'],effective_exp_years=i['effective_exp_years'],effective_exp_months=i['effective_exp_months'],actual_exp_year=i['actual_exp_year'],actual_exp_month=i['actual_exp_month'],organisation=i['organisation'],designation=i['designation'],agp=i['agp'],gross_salary=i['gross_salary'],exp_type=i['exp_type'],remark=i['remark'],emp_id=EmployeePrimdetail.objects.get(emp_id=l_id), added_by=EmployeePrimdetail.objects.get(emp_id=added_by_id)) for i in data['experience'])
                        print(objs)
                        qry_g = EmployeeExperience.objects.bulk_create(objs)
                    print("kjhgvcx")
                    if emp_doc:
                        qryh=EmployeeDocuments.objects.create(**emp_doc)
                        
                    if qry_a and qry_b and qry_c and qry_e and qry_f and qryh:
                        msg="Data Successfully Added..."
                        status=200
                    else:
                        status = 500
                    data={'msg':msg,'id':emp_id}
                    # return JsonResponse(status=status,data=res)
            else:
                status=403
        else:
            status=401
    else:
        status=400
    return JsonResponse(status=status,data=data)


##################### VIEWS FOR EMPLOYEE EmployeeDropdown ########################
def HR_dropdown(request):
    data = {}
    qry1 = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'general':
                        qry1 = EmployeeDropdown.objects.filter(value=None).extra(select={'fd': 'field', 'id': 'sno', 'parent': 'pid'}).values('fd', 'id', 'parent').exclude(status="DELETE").distinct()
                        for field1 in qry1:
                            if field1['parent'] != 0:
                                pid = field1['parent']
                                qry2 = EmployeeDropdown.objects.filter(sno=pid).exclude(status="DELETE").values('field')
                                field1['fd'] = field1['fd'] + '(' + qry2[0]['field'] + ')'
                        msg = "Success"
                        error = False
                        if not qry1:
                            msg = "No Data Found!!"
                        status = 200
                        data = {'msg': msg, 'data': list(qry1)}

                    elif request.GET['request_type'] == 'subcategory':
                        sno = request.GET['Sno']
                        names = EmployeeDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('field', 'pid')
                        name = names[0]['field']

                        #p_id = names[0]['pid']

                        p_id = names[0]['pid']

                        qry1 = EmployeeDropdown.objects.filter(field=name, pid=p_id).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'valueid': 'sno', 'parentId': 'pid', 'cat': 'field', 'text1': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('valueid', 'parentId', 'cat', 'text1', 'edit', 'delete')
                        for x in range(0, len(qry1)):
                            test = EmployeeDropdown.objects.filter(pid=qry1[x]['valueid']).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'subid': 'sno', 'subvalue': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('subid', 'subvalue', 'edit', 'delete')
                            qry1[x]['subcategory'] = list(test)
                        msg = "Success"
                        data = {'msg': msg, 'data': list(qry1)}
                        status = 200

                elif request.method == 'DELETE':
                    data = json.loads(request.body)
                    qry = EmployeeDropdown.objects.filter(sno=data['del_id']).exclude(status="DELETE").values('field')
                    fd = qry[0]['field']
                    if(qry.exists()):

                        sno = data['del_id']
                        deletec(sno)
                        q2 = EmployeeDropdown.objects.filter(field=fd).exclude(status="DELETE").exclude(value__isnull=True).values().count()
                        if q2 == 0:
                            q3 = EmployeeDropdown.objects.filter(field=fd).exclude(status="DELETE").update(status="DELETE")
                        msg = "Data Successfully Deleted..."
                        status = 200
                    else:
                        msg = "Data Not Found!"
                        status = 404
                    data = {'msg': msg}
                    status = 200
                elif request.method == 'POST':
                    body1 = json.loads(request.body)

                    for body in body1:
                        pid = body['parentid']
                        value = body['val'].upper()
                        field_id = body['cat']
                        field_qry = EmployeeDropdown.objects.filter(sno=field_id).exclude(status="DELETE").values('field')
                        field = field_qry[0]['field']
                        if pid != 0:
                            field_qry = EmployeeDropdown.objects.filter(sno=pid).exclude(status="DELETE").exclude(value__isnull=True).values('value')
                            field = field_qry[0]['value']
                            cnt = EmployeeDropdown.objects.filter(field=field).exclude(status="DELETE").values('sno')
                            if len(cnt) == 0:
                                add = EmployeeDropdown.objects.create(pid=pid, field=field)

                        qry_ch = EmployeeDropdown.objects.filter(Q(field=field) & Q(value=value)).filter(pid=pid).exclude(status="DELETE")
                        if(len(qry_ch) > 0):
                            status = 409

                        else:
                            created = EmployeeDropdown.objects.create(pid=pid, field=field, value=value)
                            msg = "Successfully Inserted"
                            data = {'msg': msg}
                            status = 200

                elif request.method == 'PUT':
                    body = json.loads(request.body)
                    sno = body['sno1']
                    val = body['val'].upper()
                    field_qry = EmployeeDropdown.objects.filter(sno=sno).exclude(status="DELETE").values('pid', 'value')
                    pid = field_qry[0]['pid']
                    value = field_qry[0]['value']
                    add = EmployeeDropdown.objects.filter(pid=pid, field=value).exclude(status="DELETE").update(field=val)
                    add = EmployeeDropdown.objects.filter(sno=sno).exclude(status="DELETE").update(value=val, status="UPDATE")
                    add = EmployeeDropdown.objects.filter(pid=sno).exclude(status="DELETE").update(field=val, status="UPDATE")
                    msg = "Successfully Updated"
                    data = {'msg': msg}
                    status = 200

                else:
                    status = 403
            else:
                status = 401
        else:
            status = 400
    return JsonResponse(status=status, data=data)


def deletec(pid):
    qry = EmployeeDropdown.objects.filter(pid=pid).exclude(status="DELETE").values('sno')
    if len(qry) > 0:
        for x in qry:
            deletec(x['sno'])
    qry = EmployeeDropdown.objects.filter(sno=pid).exclude(status="DELETE").update(status="DELETE")


def deletec_aar(pid):
    qry = AarDropdown.objects.filter(pid=pid).values('sno')
    if len(qry) > 0:
        for x in qry:
            deletec_aar(x['sno'])
    qry = AarDropdown.objects.filter(sno=pid).delete()
################################################### VIEWS FOR UPDATE EMPLOYEE ##############################################


def transfer_previous_pending_leave_grievance(emp_id, department, reporting_to, reporting_no):
    Leaveapproval.objects.filter(leaveid__emp_id=emp_id, reportinglevel=reporting_no, status='PENDING').update(dept=EmployeeDropdown.objects.get(sno=department), desg=EmployeeDropdown.objects.get(sno=reporting_to))
    if reporting_no == 1:
        GrievanceData.objects.filter(empid=emp_id, status_hod='PENDING').update(department=EmployeeDropdown.objects.get(sno=department), designation=EmployeeDropdown.objects.get(sno=reporting_to))


def Update_Musterroll(request):
    data = ""
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:

            if request.method == 'GET':
                check = 500
                if request.GET['request_type'] == 'fetch_id':
                    check = checkpermission(request, [211, 337])

                elif request.GET['request_type'] == 'update_fetch_data':
                    check = checkpermission(request, [337])

                elif request.GET['request_type'] == 'employee_detail':
                    check = checkpermission(request, [337, 425])

                if check == 200:
                    if request.GET['request_type'] == 'fetch_id':
                        qry1 = EmployeePrimdetail.objects.filter(emp_status='Active').extra(select={'id': 'emp_id', 'nm': 'name'}).values('id', 'nm')
                        status = 200
                        msg = "Success"
                        data = {'msg': msg, 'data': list(qry1)}

                    else:
                        data = request.GET
                        if 'emp_id' in data:
                            Emp_Id = data['emp_id']
                        else:
                            Emp_Id = request.session['hash1']

                    ####################################################### ALL DATA ##################################################################

                    qry2 = EmployeeDropdown.objects.filter(field='TYPE OF EMPLOYMENT').exclude(value__isnull=True).extra(select={'toe_id': 'sno', 'toe': 'value'}).values('toe', 'toe_id')
                    # print(qry2.query)

                    qry3 = EmployeeDropdown.objects.filter(field='CATEGORY OF EMPLOYEE').exclude(value__isnull=True).extra(select={'coe_id': 'sno', 'coe': 'value'}).values('coe', 'coe_id')

                    qry4 = EmployeeDropdown.objects.filter(value="DESIGNATION").exclude(value__isnull=True).extra(select={'id': 'sno', 'field': 'field'}).values('id', 'field')
                    qry_len = len(qry4)
                    for x in range(0, qry_len):
                        qry4_a = EmployeeDropdown.objects.filter(pid=qry4[x]['id']).exclude(value__isnull=True).extra(select={'desg_id': 'sno', 'desg_name': 'value'}).values('desg_id', 'desg_name')
                        qry4[x]['designation'] = list(qry4_a)
                    # print(qry4)

                    qry4_b = EmployeeDropdown.objects.filter(value="CADRE").exclude(value__isnull=True).extra(select={'id': 'sno', 'field': 'field'}).values('id', 'field')
                    qry_len = len(qry4_b)
                    for x in range(0, qry_len):
                        qry4_b1 = EmployeeDropdown.objects.filter(pid=qry4_b[x]['id']).exclude(value__isnull=True).extra(select={'cadre_id': 'sno', 'cadre_name': 'value'}).values('cadre_id', 'cadre_name')

                        qry4_b[x]['cadre'] = list(qry4_b1)
                        # print(qry4_b)

                    qry4_c = EmployeeDropdown.objects.filter(value="LADDER").exclude(value__isnull=True).extra(select={'id': 'sno', 'field': 'field'}).values('id', 'field')
                    qry_len = len(qry4_c)
                    for x in range(0, qry_len):
                        qry4_c1 = EmployeeDropdown.objects.filter(pid=qry4_c[x]['id']).exclude(value__isnull=True).extra(select={'ladre_id': 'sno', 'ladre_name': 'value'}).values('ladre_id', 'ladre_name')

                        qry4_c[x]['ladre'] = list(qry4_c1)

                    qry4_d = EmployeeDropdown.objects.filter(value="POSITION").exclude(value__isnull=True).extra(select={'id': 'sno', 'field': 'field'}).values('id', 'field')
                    qry_len = len(qry4_d)
                    for x in range(0, qry_len):
                        qry4_d1 = EmployeeDropdown.objects.filter(pid=qry4_d[x]['id']).exclude(value__isnull=True).extra(select={'pos_id': 'sno', 'pos_name': 'value'}).values('pos_id', 'pos_name')

                        qry4_d[x]['position'] = list(qry4_d1)

                    qry5 = EmployeeDropdown.objects.filter(field='SHIFT SETTINGS').exclude(value__isnull=True).extra(select={'sft_id': 'sno', 'sft': 'value'}).values('sft', 'sft_id')
                    # print(qry5)
                    qry_len = len(qry5)
                    for x in range(0, qry_len):
                        qry4_b1 = EmployeeDropdown.objects.filter(pid=qry5[x]['sft_id']).exclude(value__isnull=True).extra(select={'shift_id': 'sno', 'shift_name': 'value'}).values('shift_id', 'shift_name')

                        qry5[x]['shift'] = list(qry4_b1)

                    # print(qry5)
                    qry6 = EmployeeDropdown.objects.filter(field='TITLE').exclude(value__isnull=True).extra(select={'title_id': 'sno', 'title': 'value'}).values('title', 'title_id')

                    qry7 = EmployeeDropdown.objects.filter(field='DEPARTMENT').exclude(value__isnull=True).extra(select={'dept_id': 'sno', 'dept': 'value'}).values('dept', 'dept_id')

                    qry8 = EmployeeDropdown.objects.filter(field='POSITION').exclude(value__isnull=True).extra(select={'pos_id': 'sno', 'pos': 'value'}).values('pos', 'pos_id')

                    qry9 = EmployeeDropdown.objects.filter(field='ROLES').exclude(sno=402).exclude(value__isnull=True).extra(select={'role_id': 'sno', 'role': 'value'}).values('role_id', 'role').distinct()

                    qry10 = EmployeeDropdown.objects.filter(field='BLOOD GROUP').exclude(value__isnull=True).extra(select={'bg_id': 'sno', 'bg': 'value'}).values('bg', 'bg_id')

                    qry11 = EmployeeDropdown.objects.filter(field='GENDER').exclude(value__isnull=True).extra(select={'gender_id': 'sno', 'gender': 'value'}).values('gender', 'gender_id')

                    qry12 = EmployeeDropdown.objects.filter(field='NATIONALITY').exclude(value__isnull=True).extra(select={'nation_id': 'sno', 'nation': 'value'}).values('nation', 'nation_id')

                    qry13 = EmployeeDropdown.objects.filter(field='CASTE').exclude(value__isnull=True).extra(select={'caste_id': 'sno', 'caste': 'value'}).values('caste', 'caste_id')

                    qry14 = EmployeeDropdown.objects.filter(field='MARITAL STATUS').exclude(value__isnull=True).extra(select={'marriage_id': 'sno', 'marriage': 'value'}).values('marriage', 'marriage_id')

                    qry15 = EmployeeDropdown.objects.filter(field='RELIGION').exclude(value__isnull=True).extra(select={'rel_id': 'sno', 'rel': 'value'}).values('rel', 'rel_id')

                    qry16 = EmployeeDropdown.objects.filter(field='BOARD').exclude(value__isnull=True).extra(select={'board_id': 'sno', 'board': 'value'}).values('board', 'board_id')

                    qry17 = EmployeeDropdown.objects.filter(field='UNIVERSITY').exclude(value__isnull=True).extra(select={'uni_id': 'sno', 'uni': 'value'}).values('uni', 'uni_id')

                    qry18 = EmployeeDropdown.objects.filter(field='DEGREE').exclude(value__isnull=True).extra(select={'deg_id': 'sno', 'deg': 'value'}).values('deg', 'deg_id')

                    qry19 = EmployeeDropdown.objects.filter(field='P.HD. STAGE').exclude(value__isnull=True).extra(select={'stage_id': 'sno', 'stage': 'value'}).values('stage', 'stage_id')
                    qry20 = EmployeeDropdown.objects.filter(field='ORGANIZATION').exclude(value__isnull=True).extra(select={'org_id': 'sno', 'org_name': 'value'}).values('org_id', 'org_name')
                    qry21 = EmployeeDropdown.objects.filter(field='STATE').exclude(value__isnull=True).extra(select={'state_id': 'sno', 'state_name': 'value'}).values('state_id', 'state_name')
                    if(1353 in request.session['roles']):
                        qry22 = Semtiming.objects.filter(sem_start__gte="2018-06-01", sem_type__contains="odd").values('uid', 'session', 'session_name')
                    else:
                        qry22 = Semtiming.objects.filter(sem_start__gte="2018-06-01").values('uid', 'session', 'session_name')

                    qry23 = request.session['Session_id']

                    data1 = {'toe_d': list(qry2), 'coe_d': list(qry3), 'desg_d': list(qry4), 'cadre_d': list(qry4_b), 'ladre': list(qry4_c), 'position': list(qry4_d), 'sft_d': list(qry5), 'title_d': list(qry6), 'dept_d': list(qry7), 'pos_d': list(qry8), 'roles_d': list(qry9), 'bg_d': list(qry10), 'gender_d': list(qry11), 'nationality_d': list(qry12), 'caste_d': list(qry13), 'marital_status_d': list(qry14), 'rel_d': list(qry15), 'board_d': list(qry16), 'uni_d': list(qry17), 'deg_d': list(qry18), 'stage_d': list(qry19), 'organization': list(qry20), 'state': list(qry21), 'session': list(qry22), 'current_session': qry23}

                ########################################## DATA CORRESPONDENDING TO RECIEVED ID ##########################################

                    qry2_a = EmployeePrimdetail.objects.filter(emp_id=Emp_Id).extra(select={'dep': 'dept', 'title': 'title', 'toe': 'emp_type', 'coe': 'emp_category', 'dsgn': 'desg', 'sft': 'shift', 'current_pos': 'current_pos', 'cadre': 'cadre', 'ladder': 'ladder', 'organization': 'organization'}).values('dep', 'title', 'toe', 'coe', 'dsgn', 'sft', 'current_pos', 'cadre', 'ladder', 'organization')
                    # print(qry2_a[0]['coe'])
                    ########### VARIABLES HOLDING IDS ####################

                    dept_id = qry2_a[0]['dep']
                    title_id = qry2_a[0]['title']
                    coe_id = qry2_a[0]['coe']
                    toe_id = qry2_a[0]['toe']
                    dsgn_id = qry2_a[0]['dsgn']
                    sft_id = qry2_a[0]['sft']

                    ######################################################

                    qry2_b = EmployeeDropdown.objects.filter(sno=coe_id).extra(select={'coe_name': 'value'}).values('coe_name')

                    qry2_c = EmployeeDropdown.objects.filter(sno=toe_id).extra(select={'toe_name': 'value'}).values('toe_name')

                    qry2_d = EmployeeDropdown.objects.filter(sno=dsgn_id).extra(select={'dsgn_name': 'value'}).values('dsgn_name')

                    qry2_e = EmployeeDropdown.objects.filter(sno=sft_id).extra(select={'sft_name': 'value'}).values('sft_name')
                    # print(qry2_e)

                    qry2_f = EmployeeDropdown.objects.filter(sno=dept_id).extra(select={'dept_name': 'value'}).values('dept_name')

                    qry2_g = EmployeeDropdown.objects.filter(sno=title_id).extra(select={'title_name': 'value'}).values('title_name')

                    qry2_h = EmployeePrimdetail.objects.filter(emp_id=Emp_Id).extra(select={'nme': 'name', 'date_joining': 'doj', 'primary_mobile': 'mob', 'secondary_mobile': 'mob1', 'mail': 'email'}).values('nme', 'date_joining', 'primary_mobile', 'secondary_mobile', 'mail')

                    qry2_j = Roles.objects.filter(emp_id=Emp_Id).extra(select={'role': 'roles'}).values('role')
                    qry2_desg = Employee_Designations.objects.filter(emp_id=Emp_Id, status='INSERT').extra(select={'add_desg': 'emp_designations'}).values('add_desg')
                    # print(qry2_j[0]['role'])
                    # qry_b=EmployeeDropdown.objects.filter(sno__in=qry_a.values('holiday')).extra(select={'ht_val':'value'}).values('ht_val')
                    qry_b = EmployeeDropdown.objects.filter(sno__in=qry2_j.values('role')).exclude(value__isnull=True).extra(select={'role': 'sno'}).values('role')
                    qry_desg = EmployeeDropdown.objects.filter(sno__in=qry2_desg.values('add_desg')).exclude(value__isnull=True).extra(select={'add_desg': 'sno'}).values('add_desg')

                    qry2_k = EmployeePerdetail.objects.filter(emp_id=Emp_Id).extra(select={'Linked_in': 'linked_in_url', 'father': 'fname', 'mother': 'mname', 'birth_date': 'dob', 'gndr': 'gender', 'blood_group': 'bg', 'nation': 'nationality', 'caste': 'caste', 'marry': 'marital_status', 'rel': 'religion', 'image': 'image_path'}).values('Linked_in', 'father', 'mother', 'birth_date', 'gndr', 'blood_group', 'nation', 'caste', 'marry', 'rel', 'image', 'aadhar_num', 'pan_no')

                    qry2_m = EmployeeAddress.objects.filter(emp_id=Emp_Id).extra(select={'permanent_add_1': 'p_add1', 'permanent_add_2': 'p_add2', 'place': 'p_city', 'district': 'p_district', 'state': 'p_state',
                                                                                         'pin': 'p_pincode', 'corresp_add_1': 'c_add1', 'corresp_add_2': 'c_add2', 'corresp_place': 'c_city', 'corresp_district': 'c_district', 'corresp_state': 'c_state', 'corresp_pin': 'c_pincode'}).values(
                        'permanent_add_1', 'permanent_add_2', 'place', 'district', 'state', 'pin', 'corresp_add_1', 'corresp_add_2', 'corresp_place', 'corresp_district', 'corresp_state', 'corresp_pin', 'p_state__value', 'c_state__value')

                    qry2_n = Reporting.objects.filter(emp_id=Emp_Id).extra(select={'reporting_level': 'reporting_no', 'reporting_designation_id': 'reporting_to', 'reporting_official_dept_id': 'department'}).values('reporting_level', 'reporting_designation_id', 'reporting_official_dept_id')
                    reporting_designation_id = {}
                    department_id = {}
                    department_name = {}
                    reporting_designation_name = {}
                    designation_name = {}

                    # print(qry2_n[0]['reporting_level'])
                    j = 0

                    '''for i in qry2_n:
						qry2_n1=EmployeeDropdown.objects.filter(sno=qry2_n[j]['reporting_designation_id']).extra(select={'official_designation':'value'}).values('official_designation')
						#print(qry2_n1[0]['official_designation'])
						designation_name[j]=(qry2_n1[0]['official_designation'])
						qry2_n2=EmployeeDropdown.objects.filter(sno=qry2_n[j]['reporting_official_dept_id']).extra(select={'official_department':'value'}).values('official_department')
						#print(qry2_n[j]['reporting_official_dept_id'])
						department_name[j]=qry2_n2[0]['official_department']
						j=j+1

					reporting_info={'reporting_levels':qry2_n.count(),'designation':designation_name,'department':department_name,'ids':list(qry2_n)}
					#print(reporting_info)'''
                    try:
                        for i in qry2_n:
                            qry2_n1 = EmployeeDropdown.objects.filter(sno=qry2_n[j]['reporting_designation_id']).extra(select={'official_designation': 'value'}).values('official_designation')
                            ########################## DYNAMIC DICTIONARY ###############################
                            qry2_n[j]['designation'] = qry2_n1[0]['official_designation']
                            ##############################################################################
                            qry2_n2 = EmployeeDropdown.objects.filter(sno=qry2_n[j]['reporting_official_dept_id']).extra(select={'official_department': 'value', 'org_pid': 'pid'}).values('official_department', 'org_pid')
                            # print(qry2_n[j]['reporting_official_dept_id'])
                            ######################################################## Organization ###############################################################
                            qry2_n3 = EmployeeDropdown.objects.filter(sno=qry2_n2[0]['org_pid']).extra(select={'official_organization_id': 'pid', 'official_organization': 'field'}).values('official_organization_id', 'official_organization')
                            qry2_n[j]['department'] = qry2_n2[0]['official_department']
                            qry2_n[j]['organization'] = qry2_n3[0]['official_organization']
                            qry2_n[j]['organization_id'] = qry2_n3[0]['official_organization_id']
                            j = j + 1
                        # print(qry2_n)
                        reporting_info = {'reporting_levels': qry2_n.count(), 'designation': designation_name, 'department': department_name, 'ids': list(qry2_n)}
                    except:
                        reporting_info = ""

                    ############################################ Appraisal ####################################################################################
                    qry2_app = AarReporting.objects.filter(emp_id=Emp_Id).extra(select={'appraisal_level': 'reporting_no', 'appraisal_designation_id': 'reporting_to', 'appraisal_official_dept_id': 'department'}).values('appraisal_level', 'appraisal_designation_id', 'appraisal_official_dept_id')
                    appraisal_designation_id = {}
                    app_dept = {}
                    app_desg = {}
                    appraisal_designation_name = {}
                    app_desg_name = {}
                    # print(qry2_n[0]['reporting_level'])
                    j = 0

                    '''for i in qry2_n:
						qry2_n1=EmployeeDropdown.objects.filter(sno=qry2_n[j]['reporting_designation_id']).extra(select={'official_designation':'value'}).values('official_designation')
						#print(qry2_n1[0]['official_designation'])
						designation_name[j]=(qry2_n1[0]['official_designation'])
						qry2_n2=EmployeeDropdown.objects.filter(sno=qry2_n[j]['reporting_official_dept_id']).extra(select={'official_department':'value'}).values('official_department')
						#print(qry2_n[j]['reporting_official_dept_id'])
						department_name[j]=qry2_n2[0]['official_department']
						j=j+1

					reporting_info={'reporting_levels':qry2_n.count(),'designation':designation_name,'department':department_name,'ids':list(qry2_n)}
					#print(reporting_info)'''
                    try:
                        for i in qry2_app:
                            qry2_app1 = EmployeeDropdown.objects.filter(sno=qry2_app[j]['appraisal_designation_id']).extra(select={'official_designation': 'value'}).values('official_designation')
                            ########################## DYNAMIC DICTIONARY ###############################
                            qry2_app[j]['designation'] = qry2_app1[0]['official_designation']
                            ##############################################################################
                            qry2_app2 = EmployeeDropdown.objects.filter(sno=qry2_app[j]['appraisal_official_dept_id']).extra(select={'official_department': 'value', 'org_pid': 'pid'}).values('official_department', 'org_pid')
                            # print(qry2_n[j]['reporting_official_dept_id'])
                            ######################################################## Organization ###############################################################
                            qry2_app3 = EmployeeDropdown.objects.filter(sno=qry2_app2[0]['org_pid']).extra(select={'official_organization_id': 'pid', 'official_organization': 'field'}).values('official_organization_id', 'official_organization')
                            qry2_app[j]['department'] = qry2_app2[0]['official_department']
                            qry2_app[j]['organization'] = qry2_app3[0]['official_organization']
                            qry2_app[j]['organization_id'] = qry2_app3[0]['official_organization_id']
                            j = j + 1
                        # print(qry2_n)
                        appraisal_info = {'appraisal_levels': qry2_app.count(), 'designation': designation_name, 'department': department_name, 'ids': list(qry2_app)}
                    except:
                        appraisal_info = ""
                    ###########################################################################################################################################
                    qry2_o = EmployeePrimdetail.objects.filter(emp_id=Emp_Id).extra(select={'pos': 'current_pos'}).values('pos')
                    pos_id = qry2_o[0]['pos']

                    qry2_join_pos = EmployeePrimdetail.objects.filter(emp_id=Emp_Id).extra(select={'join_pos': 'join_pos'}).values('join_pos')
                    join_pos_id = qry2_join_pos[0]['join_pos']
                    qry2_join_pos_val = EmployeeDropdown.objects.filter(sno=join_pos_id).extra(select={'join_pos_value': 'value'}).values('join_pos_value')
                    join_position = {'id': list(qry2_join_pos), 'val': list(qry2_join_pos_val)}

                    qry2_p = EmployeeDropdown.objects.filter(sno=pos_id).extra(select={'pos_value': 'value'}).values('pos_value')

                    position = {'id': list(qry2_o), 'val': list(qry2_p)}

                    a = EmployeeAcademic.objects.filter(emp_id=Emp_Id).extra(select={'x_pass_yr': 'pass_year_10', 'x_board': 'board_10', 'x_cgpa': 'cgpa_per_10', 'xii_pass_yr': 'pass_year_12', 'xii_board': 'board_12', 'xii_cgpa': 'cgpa_per_12', 'diploma_pass_yr': 'pass_year_dip', 'diploma_uni': 'univ_dip', 'diploma_cgpa': 'cgpa_per_dip', 'ug_pass_yr': 'pass_year_ug', 'ug_uni': 'univ_ug', 'ug_degree': 'degree_ug', 'ug_cgpa': 'cgpa_per_ug', 'pg_pass_yr': 'pass_year_pg', 'pg_uni': 'univ_pg', 'pg_cgpa': 'cgpa_per_pg', 'pg_degree': 'degree_pg', 'pg_area_specialization': 'area_spl_pg', 'doc_research_topic': 'research_topic_doctrate', 'doc_dropdown': 'doctrate', 'doc_uni': 'univ_doctrate', 'doc_date': 'date_doctrate', 'doc_stage': 'stage_doctrate', 'other_degree': 'degree_other', 'other_pass_yr': 'pass_year_other', 'other_uni': 'univ_other', 'other_cgpa': 'cgpa_per_other', 'other_area_specialization': 'area_spl_other', 'pg_area': 'area_spl_pg', 'ug_area': 'area_spl_ug', 'dip_area': 'dip_area'}).values('x_pass_yr', 'x_board', 'x_cgpa', 'xii_pass_yr', 'xii_board', 'xii_cgpa', 'doc_date', 'diploma_pass_yr', 'diploma_uni', 'diploma_cgpa', 'ug_pass_yr', 'ug_uni', 'ug_degree', 'ug_cgpa', 'pg_pass_yr', 'pg_uni', 'pg_cgpa', 'pg_degree', 'pg_area_specialization', 'doc_dropdown', 'doc_uni', 'doc_stage', 'doc_research_topic', 'other_degree', 'other_pass_yr', 'other_uni', 'other_cgpa', 'other_area_specialization', 'ug_area', 'pg_area', 'dip_area')
                    # print(qry2_q)

                    qry2_r = EmployeeDocuments.objects.filter(emp_id=Emp_Id).extra(select={'x_marksheet': 'marksheet_10', 'xii_marksheet': 'marksheet_12', 'diploma_marksheet': 'marksheet_dip', 'ug_marksheet': 'marksheet_ug', 'pg_marksheet': 'marksheet_pg', 'doctrate_marksheet': 'marksheet_doctrate', 'other_marksheet': 'marksheet_other', 'medical': 'medical_fitness', 'cc': 'character_certificate', 'exp': 'experience_certificate', 'ug_degree1': 'ug_degree', 'pg_degree1': 'pg_degree'}).values('x_marksheet', 'xii_marksheet', 'diploma_marksheet', 'ug_marksheet', 'pg_marksheet', 'doctrate_marksheet', 'other_marksheet', 'medical', 'cc', 'exp', 'ug_degree1', 'pg_degree1')

                    if qry2_r:
                        # print("Hi")
                        qry2_q = a[0]
        ################################### DYNAMIC INDEXING IN DICTIONARY ###################################

                        qry2_q['x_marksheet'] = qry2_r[0]['x_marksheet']
                        # print(a['x_marksheet'])
                        qry2_q['xii_marksheet'] = qry2_r[0]['xii_marksheet']
                        qry2_q['diploma_marksheet'] = qry2_r[0]['diploma_marksheet']
                        qry2_q['ug_marksheet'] = qry2_r[0]['ug_marksheet']
                        qry2_q['pg_marksheet'] = qry2_r[0]['pg_marksheet']
                        qry2_q['doctrate_marksheet'] = qry2_r[0]['doctrate_marksheet']
                        qry2_q['other_marksheet'] = qry2_r[0]['other_marksheet']
                        qry2_q['medical'] = qry2_r[0]['medical']
                        qry2_q['cc'] = qry2_r[0]['cc']
                        qry2_q['exp'] = qry2_r[0]['exp']
                        qry2_q['ug_degree1'] = qry2_r[0]['ug_degree1']
                        qry2_q['pg_degree1'] = qry2_r[0]['pg_degree1']
    #########################################################################################################
                    else:
                        qry2_q = ""

                    qry_r = EmployeeAcademic.objects.filter(emp_id=Emp_Id).extra(select={'doc_id': 'doctrate'}).values('doc_id')
                    qry_s = EmployeeDropdown.objects.filter(sno__in=qry_r.values('doc_id')).extra(select={'doc_val': 'value', 'doc_id': 'sno'}).values('doc_val', 'doc_id')
                    # qry_t = EmployeeResearch.objects.filter(emp_id=Emp_Id).extra(select={'years_r': 'research_years', 'months_r': 'research_months', 'years_i': 'industry_years', 'months_i': 'industry_months', 'years_t': 'teaching_years', 'months_t': 'teaching_months', 'remark': 'remark'}).values('years_r', 'months_r', 'years_i', 'months_i', 'years_t', 'months_t', 'remark')

                    qry_research = EmployeeExperience.objects.filter(emp_id=Emp_Id,exp_type="R",status="INSERT").values('id','emp_id','emp_id__name','from_date','to_date','effective_exp_years','effective_exp_months','actual_exp_year','actual_exp_month','organisation','designation','agp','gross_salary','exp_type','remark','added_by','added_by__name')
                    qry_teaching = EmployeeExperience.objects.filter(emp_id=Emp_Id,exp_type="T",status="INSERT").values('id','emp_id','emp_id__name','from_date','to_date','effective_exp_years','effective_exp_months','actual_exp_year','actual_exp_month','organisation','designation','agp','gross_salary','exp_type','remark','added_by','added_by__name')
                    qry_industry = EmployeeExperience.objects.filter(emp_id=Emp_Id,exp_type="I",status="INSERT").values('id','emp_id','emp_id__name','from_date','to_date','effective_exp_years','effective_exp_months','actual_exp_year','actual_exp_month','organisation','designation','agp','gross_salary','exp_type','remark','added_by','added_by__name')
                    
                    last_exp = EmployeeExperience.objects.filter(emp_id=Emp_Id,exp_type="KIET",status="INSERT").values('id','effective_exp_years','effective_exp_months','to_date').order_by('-id')[:1]
                    if len(last_exp)>0:
                        difference = relativedelta(date.today(),last_exp[0]['to_date'])
                        update_exp = EmployeeExperience.objects.filter(emp_id=Emp_Id,exp_type="KIET",status="INSERT",id=last_exp[0]['id']).update(effective_exp_years=(last_exp[0]['effective_exp_years']+difference.years),effective_exp_months=(last_exp[0]['effective_exp_months']+difference.months),to_date=date.today())
                    
                    qry_kiet_exp = EmployeeExperience.objects.filter(emp_id=Emp_Id,exp_type="KIET",status="INSERT").values('id','emp_id','emp_id__name','from_date','to_date','effective_exp_years','effective_exp_months','actual_exp_year','actual_exp_month','organisation','designation','agp','gross_salary','exp_type','remark','added_by','added_by__name')
                    # print(qry_industry)
                    # doc_info={'doc_no':list(qry_r),'doc_name':list(qry_s)}
                    # qry_s=EmployeeDropdown.objects.select_related('sno')
                    # qry_s=EmployeeDropdown.join(EmployeeAcademic)

                    net_exp = get_net_experience(Emp_Id)

                    names = {'coe_value': list(qry2_b), 'toe_value': list(qry2_c), 'dsgn_value': list(qry2_d), 'sft_value': list(qry2_e), 'dept_value': list(qry2_f), 'title_value': list(qry2_g), 'name_n_join_date_contact': list(qry2_h), 'add_role': list(qry_b), 'add_desg': list(qry_desg), 'personal_details': list(qry2_k), 'residential_details': list(qry2_m), 'reporting_level': reporting_info, 'appraisal_level': appraisal_info, 'pos': position, 'join_pos': join_position, 'academic_details': qry2_q, 'doc_info': list(qry_s), 'research_info': list(qry_research),'teaching_info': list(qry_teaching),'industry_info': list(qry_industry),'kiet_exp_info':list(qry_kiet_exp), 'net_exp': list(net_exp)}
                    # names = {'coe_value': list(qry2_b), 'toe_value': list(qry2_c), 'dsgn_value': list(qry2_d), 'sft_value': list(qry2_e), 'dept_value': list(qry2_f), 'title_value': list(qry2_g), 'name_n_join_date_contact': list(qry2_h), 'add_role': list(qry_b), 'add_desg': list(qry_desg), 'personal_details': list(qry2_k), 'residential_details': list(qry2_m), 'reporting_level': reporting_info, 'appraisal_level': appraisal_info, 'pos': position, 'join_pos': join_position, 'academic_details': qry2_q, 'doc_info': list(qry_s)}
                    msg = "logged in"
                    error = False
                    status = 200
                    data = {'data_d': data1, 'id': list(qry2_a), 'names': names, 'msg': msg, 'pmail': Emp_Id}
                else:
                    status = 403
            if request.method == 'PUT':
                check = checkpermission(request, [211, 337])
                if check == 200:
                    data = json.loads(request.body)
                    added_by_id = request.session['hash1']
                    Emp_Id = data['emp_id']
                    empType_id = data['toe']
                    empCategory_id = data['coe']
                    empDesg_id = data['desg']
                    empImg = data['image']
                    empShift_id = data['shift']
                    empTitle_id = data['title']
                    empName = data['name']
                    empDept_id = data['dep']
                    empDOJ_id = data['date_join']
                    pos = data['pos']
                    role = data['role']
                    emp_desg = data['add_desg']
                    if 'reporting' in data:
                        reporting_count = int(data['reporting'])
                    else:
                        reporting_count = None
                    if 'department' in data:
                        DepartmentId = data['department']
                    else:
                        DepartmentId = None
                    if 'designation' in data:
                        reportingTo = data['designation']
                    else:
                        reportingTo = None
                    if 'appraisal' in data:
                        appraisal_count = int(data['appraisal'])
                    else:
                        appraisal_count = None
                    if 'app_dept' in data:
                        app_dept = data['app_dept']
                    else:
                        app_dept = None
                    if 'app_desg' in data:
                        app_desg = data['app_desg']
                    else:
                        app_desg = None
                    if 'father' in data:
                        fName = data['father']
                    else:
                        fName = None
                    if 'mother' in data:
                        mName = data['mother']
                    else:
                        mName = None
                    DOB = data['birthday']
                    blood_group = data['b_grp']
                    gender = data['gender']
                    nationality = data['nation']
                    aadhar_num = data['aadhar_num']
                    pan_no = data['pan_no']
                    caste = data['caste']
                    marital_status = data['marriage']
                    religion = data['rel']
                    mob = data['mob_p']
                    if 'mob_s' in data:
                        mob1 = data['mob_s']
                    else:
                        mob1 = None
                    email = data['mail']

                    p_add1 = data['add_p1']
                    p_add2 = data['add_p2']
                    p_city = data['city_p']
                    p_district = data['dis_p']
                    p_pincode = data['pin_p']
                    p_state = data['state_p']
                    c_add1 = data['add_c1']
                    c_add2 = data['add_c2']
                    c_city = data['city_c']
                    c_district = data['dis_c']
                    c_state = data['state_c']
                    c_pincode = data['pin_c']

                    pass_year_10 = data['10_yr']
                    board_10 = data['10_board']
                    cgpa_per_10 = data['10_cgpa']
                    x_marksheet = data['x_marksheet']
                    pass_year_12 = data['12_yr']
                    board_12 = data['12_board']
                    cgpa_per_12 = data['12_cgpa']
                    xii_marksheet = data['xii_marksheet']
                    pass_year_dip = data['dip_yr']
                    univ_dip = data['dip_uni']
                    cgpa_per_dip = data['dip_cgpa']
                    diploma_marksheet = data['diploma_marksheet']
                    pass_year_ug = data['ug_yr']
                    univ_ug = data['ug_uni']
                    degree_ug = data['ug_degree']
                    join_pos = data['join_pos']
                    cgpa_per_ug = data['ug_cgpa']
                    ug_marksheet = data['ug_marksheet']
                    pass_year_pg = data['pg_yr']
                    univ_pg = data['pg_uni']
                    degree_pg = data['pg_degree']
                    cgpa_per_pg = data['pg_cgpa']
                    area_spl_ug = data['ug_area']
                    area_spl_pg = data['pg_area']
                    dip_area = data['dip_area']
                    pg_marksheet = data['pg_marksheet']
                    ug_degree_path = data['ug_degree_path']
                    pg_degree_path = data['pg_degree_path']
                    doctrate = data['doc']
                    univ_doctrate = data['doc_uni']
                    stage_doctrate = data['doc_stage']
                    doctrate_marksheet = data['doctrate_marksheet']

                    # reasearchYears = data['yrs_research']
                    # reasearchMonths = data['mon_research']
                    # industryYears = data['yrs_industry']
                    # industryMonths = data['mon_industry']
                    # teachingYears = data['yrs_teach']
                    # teachingMonths = data['mon_teach']
                    date_doctrate = data['doc_date']
                    research_topic_doctrate = data['doc_research']
                    degree_other = data['other_degree']
                    pass_year_other = data['other_yr']
                    univ_other = data['other_uni']
                    cgpa_per_other = data['other_cgpa']
                    area_spl_other = data['other_area']
                    other_marksheet = data['other_marksheet']
                    organization = data['organization']
                    cadre = data['cadre']
                    ladder = data['ladder']
                    emp_exp = data['emp_experience']
                    # if 'remark' in data:
                    #     exp_remark = data['remark']
                    # else:
                    #     exp_remark = None
                    cc = data['cc']
                    medical = data['medical']
                    update = {'emp_type': empType_id, 'emp_category': empCategory_id, 'desg': empDesg_id, 'shift': empShift_id, 'title': empTitle_id,
                              'name': empName, 'dept': empDept_id, 'current_pos': pos, 'join_pos': join_pos, 'mob': mob, 'mob1': mob1, 'email': email, 'doj': empDOJ_id, 'organization': organization, 'cadre': cadre, 'ladder': ladder}
                    qry1 = EmployeePrimdetail.objects.filter(emp_id=Emp_Id).update(**update)

                    qry3 = Reporting.objects.filter(emp_id=Emp_Id).delete()
                    if reporting_count is not None:
                        if reporting_count >= 1:
                            for i in range(0, reporting_count):
                                Reporting.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id), reporting_to=EmployeeDropdown.objects.get(sno=reportingTo[i]), department=EmployeeDropdown.objects.get(sno=DepartmentId[i]), reporting_no=i + 1)
                                transfer_previous_pending_leave_grievance(Emp_Id, DepartmentId[i], reportingTo[i], i + 1)
                        else:
                            Reporting.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id), reporting_to=None, department=None, reporting_no=0)
                    else:
                        Reporting.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id), reporting_to=None, department=None, reporting_no=0)

                    ################################################### Appraisal ##############################################################

                    qry3 = AarReporting.objects.filter(emp_id=Emp_Id).delete()
                    if appraisal_count is not None:
                        if appraisal_count >= 1:
                            for i in range(0, appraisal_count):
                                qry2 = AarReporting.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id), reporting_to=EmployeeDropdown.objects.get(sno=app_desg[i]), department=EmployeeDropdown.objects.get(sno=app_dept[i]), reporting_no=i + 1)
                        else:
                            qry2 = AarReporting.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id), reporting_to=None, department=None, reporting_no=0)
                    else:
                        qry2 = AarReporting.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id), reporting_to=None, department=None, reporting_no=0)

                    ############################################################################################################################

                    qry3 = Roles.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id)).delete()

                    for i in role:
                        qrya = Roles.objects.filter(emp_id=Emp_Id).create(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id), roles=EmployeeDropdown.objects.get(sno=i))

                    qry5 = Employee_Designations.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id)).update(status='DELETE')
                    if emp_desg:
                        for i in emp_desg:
                            if i != '':
                                ins_by = request.session["hash1"]
                                status = 'INSERT'
                                time_stamp = str(datetime.now())
                                qry_e = Employee_Designations.objects.create(emp_designations=EmployeeDropdown.objects.get(sno=i), emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id), status=status, time_stamp=time_stamp, inserted_by=EmployeePrimdetail.objects.get(emp_id=ins_by))

                    update1 = {'fname': fName, 'mname': mName, 'bg': blood_group, 'gender': gender, 'nationality': nationality, 'caste': caste, 'aadhar_num': aadhar_num, 'pan_no': pan_no,
                               'marital_status': marital_status, 'religion': religion, 'dob': DOB, 'image_path': empImg}
                    qry4 = EmployeePerdetail.objects.filter(emp_id=Emp_Id).update(**update1)

                    update2 = {'p_add1': p_add1, 'p_add2': p_add2, 'p_city': p_city, 'p_district': p_district, 'p_state': p_state, 'p_pincode': p_pincode,
                               'c_add1': c_add1, 'c_add2': c_add2, 'c_city': c_city, 'c_district': c_district, 'c_state': c_state, 'c_pincode': c_pincode}
                    qry5 = EmployeeAddress.objects.filter(emp_id=Emp_Id).update(**update2)

                    update3 = {'pass_year_10': pass_year_10, 'board_10': board_10, 'cgpa_per_10': cgpa_per_10, 'pass_year_12': pass_year_12, 'board_12': board_12, 'cgpa_per_12': cgpa_per_12, 'pass_year_dip': pass_year_dip, 'univ_dip': univ_dip, 'cgpa_per_dip': cgpa_per_dip, 'pass_year_ug': pass_year_ug, 'univ_ug': univ_ug, 'degree_ug': degree_ug, 'cgpa_per_ug': cgpa_per_ug, 'pass_year_pg': pass_year_pg, 'univ_pg': univ_pg, 'degree_pg': degree_pg, 'cgpa_per_pg': cgpa_per_pg, 'area_spl_pg': area_spl_pg, 'doctrate': doctrate, 'univ_doctrate': univ_doctrate, 'stage_doctrate': stage_doctrate, 'date_doctrate': date_doctrate, 'stage_doctrate': stage_doctrate, 'research_topic_doctrate': research_topic_doctrate, 'degree_other': degree_other, 'pass_year_other': pass_year_other, 'univ_other': univ_other, 'cgpa_per_other': cgpa_per_other, 'area_spl_other': area_spl_other, 'area_spl_ug': area_spl_ug, 'dip_area': dip_area}
                    # print(cgpa_per_12)
                    qry6 = EmployeeAcademic.objects.filter(emp_id=Emp_Id).update(**update3)

                    # update4 = {'remark': exp_remark, 'research_years': reasearchYears, 'research_months': reasearchMonths, 'industry_years': industryYears, 'industry_months': industryMonths, 'teaching_years': teachingYears, 'teaching_months': teachingMonths}
                    # qry7 = EmployeeResearch.objects.filter(emp_id=Emp_Id).update(**update4)

                    if 'update_experience' in data:
                        for i in data['update_experience']:
                            print(type(i))
                            if 'id' in i:
                                qry7 = EmployeeExperience.objects.filter(id=i['id'],emp_id=Emp_Id,exp_type=i['exp_type']).update(**i)
                            else:
                                qry8 = EmployeeExperience.objects.create(from_date=i['from_date'],to_date=i['to_date'],effective_exp_years=i['effective_exp_years'],effective_exp_months=i['effective_exp_months'],actual_exp_year=i['actual_exp_year'],actual_exp_month=i['actual_exp_month'],organisation=i['organisation'],designation=i['designation'],agp=i['agp'],gross_salary=i['gross_salary'],exp_type=i['exp_type'],remark=i['remark'],emp_id=EmployeePrimdetail.objects.get(emp_id=Emp_Id),added_by=EmployeePrimdetail.objects.get(emp_id=added_by_id))

                    if 'delete_experience' in data :
                        for i in data['delete_experience']:
                            if 'id' in i:
                                qry=EmployeeExperience.objects.filter(id=i['id'],emp_id=Emp_Id).update(status="DELETE")

                    update5 = {'marksheet_10': x_marksheet, 'marksheet_12': xii_marksheet, 'marksheet_dip': diploma_marksheet, 'marksheet_ug': ug_marksheet, 'marksheet_pg': pg_marksheet, 'marksheet_doctrate': doctrate_marksheet, 'marksheet_other': other_marksheet, 'medical_fitness': medical, 'character_certificate': cc, 'experience_certificate': emp_exp, 'ug_degree': ug_degree_path, 'pg_degree': pg_degree_path}
                    qryx = EmployeeDocuments.objects.filter(emp_id=Emp_Id).update(**update5)
                    status = 200
                    msg = "Data Updated Successfully!"
                    data = {'msg': msg}

                else:
                    status = 403
        else:
            status = 401
    else:
        status = 400
    return JsonResponse(status=status, data=data, safe=False)


##################################################### SHIFT SETTINGS ##################################################

def HR_ShiftSettings(request):
    data = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'normal':
                        qry = EmployeeDropdown.objects.filter(field='SHIFT SETTINGS').exclude(value__isnull=True).extra(select={'sft_id': 'sno', 'sft': 'value'}).values('sft', 'sft_id')
                        qry_len = len(qry)
                        for x in range(0, qry_len):
                            qrya = EmployeeDropdown.objects.filter(pid=qry[x]['sft_id']).exclude(value__isnull=True).extra(select={'shift_id': 'sno', 'shift_name': 'value'}).values('shift_id', 'shift_name')
                            qry[x]['shift'] = list(qrya)
                        msg = "Success"
                        status = 200
                        data = {'msg': msg, 'values': list(qry)}

                    if request.GET['request_type'] == 'update':
                        sId = request.GET['sft']
                        qry = Shifts.objects.filter(shiftid=sId).exclude(status='DELETE').extra(select={'time_in': 'intime', 'time_out': 'outtime', 'in_late': 'latein', 'exit_early': 'earlyexit', 'fdtime': 'fulldaytime', 'hdtime': 'halfdaytime', 'brk_strt': 'breakstart', 'brk_end': 'breakend'}).values('time_in', 'time_out', 'in_late', 'exit_early', 'fdtime', 'hdtime', 'brk_strt', 'brk_end')
                        msg = "Success"
                        if qry.count() == 0:
                            qry = ""
                        status = 200
                        data = {'msg': msg, 'values': list(qry)}

                elif request.method == 'POST':
                    data = json.loads(request.body)
                    print(data)
                    sId = data['shift']
                    iTime = data['intime']
                    oTime = data['outtime']
                    lIn = data['latein']
                    eExit = data['earlyexit']
                    fdTime = data['fulldaytime']
                    hdTime = data['halfdaytime']
                    bStart = data['breakstart']
                    bEnd = data['breakend']
                    if iTime > oTime or lIn < iTime or lIn > oTime or eExit < iTime or eExit > oTime:
                        return JsonResponse(status=500, data=data)
                    qry = Shifts.objects.filter(shiftid=sId).count()
                    if qry > 0:
                        sId = EmployeeDropdown.objects.get(sno=data['shift'])
                        qry1 = Shifts.objects.filter(shiftid=sId).update(status='DELETE')
                        qry = Shifts.objects.create(shiftid=sId, intime=iTime, outtime=oTime, latein=lIn, earlyexit=eExit,
                                                    fulldaytime=fdTime, halfdaytime=hdTime, breakstart=bStart, breakend=bEnd)
                        msg = "Shifts Updated Successfully !!"
                        data = {'msg': msg}
                    else:
                        sId = EmployeeDropdown.objects.get(sno=data['shift'])
                        qry = Shifts.objects.create(shiftid=sId, intime=iTime, outtime=oTime, latein=lIn, earlyexit=eExit,
                                                    fulldaytime=fdTime, halfdaytime=hdTime, breakstart=bStart, breakend=bEnd)
                        msg = "Shifts Added Successfully !!"
                        data = {'msg': msg}
                    status = 200

            else:
                status = 403
        else:
            status = 401
    else:
        status = 400
    return JsonResponse(status=status, data=data)

################################################################ ADD PAYROLL ###########################################################


def GetData(request):
    error = True
    msg = ""
    if request.META:
        if 'HTTP_COOKIE' in request.META:
            if request.user.is_authenticated:
                data = json.loads(request.body)
                EmpId = data['emp_id']
                QryGetEmp = EmployeePrimdetail.objects.filter(emp_id=EmpId).values()
                if QryGetEmp.count():
                    msg = "Success"
                    error = False
                else:
                    msg = "No data Found"
                    error = True
            else:
                msg = "User not authenticated"
        else:
            msg = "No cookie"
    else:
        msg = "No request"

    data_to_be_sent = {'data': list(QryGetEmp), 'msg': msg, 'error': error}

    return JsonResponse(data_to_be_sent, safe=False)

###################################### Assign Links Dashboard ###############################


def GetLinks(request):
    error = True

    if request.META:
        if 'HTTP_COOKIE' in request.META:
            if request.user.is_authenticated:
                sub_links = []
                link_qry = LeftPanel.objects.filter(parent_id=0).values('menu_id', 'link_name')
                # print(link_qry)
                x = 0
                for i in link_qry:
                    sub_link = LeftPanel.objects.filter(parent_id=i['menu_id']).values('menu_id', 'link_name')
                    # print(list(sub_link)emp_per[0]['highest_qual'])
                    a = link_qry[x]['link_name']
                    # print(a)
                    sub_links.append(list(sub_link))
                    #
                    x += 1
                role_qry = LeftPanel.objects.exclude(role__value=True).values('role__value', 'role').distinct()
                # print(role_qry)
                error = False
                msg = "Success"
                data = {'roles': list(role_qry), 'main_links': list(link_qry), 'msg': msg, 'error': error}

            else:
                msg = "User not authenticated"
        else:
            msg = "No cookie"
    else:
        msg = "No request"
    return JsonResponse(data, safe=False)

    ############################# Advance Search  ############################################


def AdvanceSearch(request):  # by dept_id
    if request.method == 'POST':
        status = 200
        data = json.loads(request.body)
        dept_id = list(data['dept'].split(","))
        detail = EmployeePrimdetail.objects.filter(dept__in=dept_id, emp_status="ACTIVE").extra(select={'doj': "DATE_FORMAT(doj,'%%d-%%m-%%Y')"}).values('name', 'dept__value', 'current_pos__value', 'emp_type__value', 'emp_category__value', 'cadre__value', 'mob', 'mob1', 'email', 'lib_card_no', 'organization__value', 'emp_status', 'ladder__value', 'shift__value', 'doj', 'emp_id', 'emp_id', 'desg__value', 'title__value')
        q = Reporting.objects.values('reporting_to', 'emp_id')
        det = list(detail)
        rep = list(q)
        for i in range(len(det)):
            c = 0
            rep_no = Reporting.objects.filter(emp_id=detail[i]['emp_id']).count()
            for j in range(len(rep)):
                if detail[i]['emp_id'] == q[j]['emp_id']:
                    c += 1
                    if c == 1:
                        rep_no1 = Reporting.objects.filter(emp_id=detail[i]['emp_id']).values('reporting_to', 'reporting_to__value', 'department__value')
                        emp_per = EmployeePerdetail.objects.filter(emp_id=detail[i]['emp_id']).extra(select={'dob': "DATE_FORMAT(dob,'%%d-%%m-%%Y')"}).values('fname', 'mname', 'bg__value', 'dob', 'gender__value', 'image_path', 'nationality__value', 'caste__value', 'marital_status__value', 'religion__value', 'aadhar_num', 'pan_no')
                        emp_aca = EmployeeAcademic.objects.filter(emp_id=detail[i]['emp_id']).values('pass_year_10', 'board_10__value', 'cgpa_per_10', 'pass_year_12', 'board_12__value', 'cgpa_per_12', 'pass_year_dip', 'univ_dip__value', 'cgpa_per_dip', 'pass_year_ug', 'univ_ug__value', 'degree_ug__value', 'cgpa_per_ug', 'pass_year_pg', 'univ_pg__value', 'degree_pg__value', 'cgpa_per_pg', 'area_spl_pg', 'doctrate', 'univ_doctrate__value', 'date_doctrate', 'stage_doctrate__value', 'research_topic_doctrate', 'degree_other__value', 'pass_year_other', 'univ_other__value', 'cgpa_per_other', 'area_spl_other', 'area_spl_ug')
                        emp_add = EmployeeAddress.objects.filter(emp_id=detail[i]['emp_id']).values('p_add1', 'p_add2', 'p_city', 'p_district', 'p_state__value', 'p_pincode', 'c_add1', 'c_add2', 'c_city', 'c_district', 'c_state__value', 'c_pincode')
                        #emp_res = EmployeeResearch.objects.filter(emp_id=detail[i]['emp_id']).values('research_years','research_months','industry_years','industry_months','teaching_years','teaching_months','remark')
                        #emp_pay = EmployeePayroll.objects.filter(emp_id=detail[i]['emp_id']).values('bank_ac_no','uan_no','pan_no','aadhar_no','pf_deduction','salary_type__value','basic','agp','da','hra','other_allowances','mediclaim')
                        # emp_aca = EmployeeAcademic.objects.filter(emp_id=emp_id=detail[i]['emp_id']).values()
                        print(detail[i]['emp_id'])
                        highest_qual = get_highest_qualification(detail[i]['emp_id'])
                        print(highest_qual)
                        detail[i]['name']=detail[i]['title__value']+" "+ detail[i]['name']
                        detail[i]['dob'] = emp_per[0]['dob']
                        detail[i]['fname'] = emp_per[0]['fname']
                        detail[i]['mname'] = emp_per[0]['mname']
                        detail[i]['bg__value'] = emp_per[0]['bg__value']
                        detail[i]['gender__value'] = emp_per[0]['gender__value']
                        detail[i]['aadhar_num'] = emp_per[0]['aadhar_num']
                        detail[i]['pan_no'] = emp_per[0]['pan_no']
                        detail[i]['nationality__value'] = emp_per[0]['nationality__value']
                        detail[i]['caste__value'] = emp_per[0]['caste__value']
                        detail[i]['marital_status__value'] = emp_per[0]['marital_status__value']
                        detail[i]['No_of_reportings'] = rep_no
                        detail[i]['religion__value'] = emp_per[0]['religion__value']
                        detail[i]['highest_qual'] = highest_qual
                        detail[i]['image_path'] = emp_per[0]['image_path']
                        #emp_pay = dict(emp_pay[0])
                        # for key, value in emp_pay.items():
                        #      detail[i][key]=value
                        if len(emp_add) > 0:
                            emp_add = dict(emp_add[0])
                            for key, value in emp_add.items():
                                detail[i][key] = value
                        if len(emp_aca) > 0:
                            emp_aca = dict(emp_aca[0])
                            for key, value in emp_aca.items():
                                detail[i][key] = value
                        rep_to2 = []
                        for k in range(rep_no):
                            rep_to1 = {}
                            rep_to1['rep_to'] = rep_no1[k]['reporting_to__value']
                            rep_to1['rep_to_dept'] = rep_no1[k]['department__value']
                            rep_to1['rep_id'] = rep_no1[k]['reporting_to']
                            rep_to2.append(rep_to1)
                        detail[i]['reporting_to'] = rep_to2
            if rep_no == 0:
                detail[i]['reporting_to'] = {}
                detail[i]['No_of_reportings'] = '0'
        data1 = list(detail)
        return JsonResponse(data1, safe=False, status=status)


############################################### AAR ######################################################################
def AAR_dropdown(request):
    data = {}
    qry1 = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_type'] == 'general':
                        qry1 = AarDropdown.objects.filter(value=None).extra(select={'fd': 'field', 'id': 'sno', 'parent': 'pid'}).values('fd', 'id', 'parent').distinct()
                        for field1 in qry1:
                            if field1['parent'] != 0:
                                pid = field1['parent']
                                qry2 = AarDropdown.objects.filter(sno=pid).values('field')
                                field1['fd'] = field1['fd'] + '(' + qry2[0]['field'] + ')'
                        msg = "Success"
                        error = False
                        if not qry1:
                            msg = "No Data Found!!"
                        status = 200
                        data = {'msg': msg, 'data': list(qry1)}

                    elif request.GET['request_type'] == 'subcategory':
                        sno = request.GET['Sno']
                        names = AarDropdown.objects.filter(sno=sno).values('field')
                        name = names[0]['field']
                        qry1 = AarDropdown.objects.filter(field=name).exclude(value__isnull=True).extra(select={'valueid': 'sno', 'parentId': 'pid', 'cat': 'field', 'text1': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('valueid', 'parentId', 'cat', 'text1', 'edit', 'delete')
                        for x in range(0, len(qry1)):
                            test = AarDropdown.objects.filter(pid=qry1[x]['valueid']).exclude(value__isnull=True).extra(select={'subid': 'sno', 'subvalue': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('subid', 'subvalue', 'edit', 'delete')
                            qry1[x]['subcategory'] = list(test)
                        msg = "Success"
                        data = {'msg': msg, 'data': list(qry1)}
                        status = 200

                elif request.method == 'DELETE':
                    data = json.loads(request.body)
                    qry = AarDropdown.objects.filter(sno=data['del_id']).values('field')
                    fd = qry[0]['field']
                    if(qry.exists()):
                        sno = data['del_id']
                        deletec_aar(sno)

                        q2 = AarDropdown.objects.filter(field=fd).exclude(value__isnull=True).values().count()

                        if q2 == 0:
                            q3 = AarDropdown.objects.filter(field=fd).delete()
                        msg = "Data Successfully Deleted..."
                        status = 200
                    else:
                        msg = "Data Not Found!"
                        status = 404
                    data = {'msg': msg}
                    status = 200
                elif request.method == 'POST':
                    body1 = json.loads(request.body)
                    for body in body1:
                        pid = body['parentid']
                        value = body['val'].upper()
                        field_id = body['cat']
                        field_qry = AarDropdown.objects.filter(sno=field_id).values('field')
                        field = field_qry[0]['field']
                        if pid != 0:
                            field_qry = AarDropdown.objects.filter(sno=field_id).values('value')
                            field = field_qry[0]['value']
                            cnt = AarDropdown.objects.filter(field=field).values('sno')
                            if len(cnt) == 0:
                                add = AarDropdown.objects.create(pid=pid, field=field)
                        add, created = AarDropdown.objects.get_or_create(pid=pid, field=field, value=value)
                        if(created == False):
                            status = 409

                        else:
                            msg = "Successfully Inserted"
                            data = {'msg': msg}
                            status = 200

                elif request.method == 'PUT':
                    body = json.loads(request.body)
                    sno = body['sno1']
                    val = body['val'].upper()
                    field_qry = AarDropdown.objects.filter(sno=sno).values('pid', 'value')
                    pid = field_qry[0]['pid']
                    value = field_qry[0]['value']
                    add = AarDropdown.objects.filter(pid=pid, field=value).update(field=val)
                    add = AarDropdown.objects.filter(sno=sno).update(value=val)
                    msg = "Successfully Updated"
                    data = {'msg': msg}
                    status = 200

            else:
                status = 403
        else:
            status = 401
    else:
        status = 400
    return JsonResponse(status=status, data=data)
################################################ Count Report ####################################################


def emp_count(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [211, 337])
            if(check == 200):
                if(request.method == 'GET'):
                    data2 = []
                    data3 = []
                    qry1 = EmployeeDropdown.objects.filter(field='Department').exclude(pid__isnull=True).exclude(value__isnull=True).extra(select={'sno': 'sno', 'value': 'value'}).values('sno', 'value')

                    filter_li = ['Faculty', 'Technical Staff', 'Staff']
                    filter_li2 = ['Assistant Professor', 'Associate Professor', 'Professor', 'PROTEM LECTURER']
                    id_li = []
                    id_li2 = []
                    for li in filter_li:
                        qr = EmployeeDropdown.objects.filter(value=li).values('sno')
                        id_li.append(qr[0]['sno'])

                    for li in filter_li2:
                        qr = EmployeeDropdown.objects.filter(value=li, field="POSITION").values('sno')
                        id_li2.append(qr[0]['sno'])

                    for q in qry1:
                        data2 = []
                        for k in id_li:
                            qry3 = EmployeePrimdetail.objects.filter(emp_category=EmployeeDropdown.objects.get(sno=k), dept=EmployeeDropdown.objects.get(sno=q['sno']), emp_status='ACTIVE')
                            data2.append(len(qry3))

                        for k in id_li2:
                            qry3 = EmployeePrimdetail.objects.filter(current_pos=EmployeeDropdown.objects.get(sno=k), dept=EmployeeDropdown.objects.get(sno=q['sno']), emp_status='ACTIVE')
                            data2.append(len(qry3))

                        data3.append({'dept_id': q['sno'], 'dept_value': q['value'], 'data': data2})
                    for q in qry1:
                        data4 = []
                        for k in id_li:
                            qry3 = EmployeePrimdetail.objects.filter(emp_category=EmployeeDropdown.objects.get(sno=k), emp_status='ACTIVE')
                            data4.append(len(qry3))

                        for k in id_li2:
                            qry3 = EmployeePrimdetail.objects.filter(current_pos=EmployeeDropdown.objects.get(sno=k), emp_status='ACTIVE')
                            data4.append(len(qry3))

                    data_values = {'dept': list(data3), 'total': list(data4)}
                    status = 200
                    msg = "Success"
                    data_values = {'data': data_values, 'msg': msg}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def get_dept_faculty(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if(check == 200):
                if(request.method == 'GET'):
                    qry_dept = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1'], emp_status="ACTIVE").values('dept', 'desg')
                    qry_emp = Reporting.objects.filter(department_id=qry_dept[0]['dept'], reporting_to=qry_dept[0]['desg'], emp_id__emp_status="ACTIVE").values('emp_id__name', 'emp_id').distinct()
                    qry_dept1 = Roles.objects.filter(emp_id=request.session['hash1'], roles=425).count()
                    if qry_dept1 > 0:
                        value = 1
                    else:
                        value = 0
                    status = 200
                    msg = "Success"
                    data_values = {'data': list(qry_emp), 'check': value}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def get_dept_faculty_web(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'GET'):
                    qry_dept = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1'], emp_status="ACTIVE").values('dept', 'desg')
                    qry_emp = Reporting.objects.filter(department_id=qry_dept[0]['dept'], emp_id__emp_status="ACTIVE").values('emp_id__name', 'emp_id').distinct()
                    qry_dept1 = Roles.objects.filter(emp_id=request.session['hash1'], roles=425).count()
                    if qry_dept1 > 0:
                        value = 1
                    else:
                        value = 0
                    status = 200
                    msg = "Success"
                    data_values = {'data': list(qry_emp), 'check': value}

                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500

    return JsonResponse(data=data_values, status=status)


def emp_certification(request):
    data_values = {}
    msg = ""
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if(check == 200):
                if(request.method == 'GET'):
                    if (request.GET['request_type'] == 'view_previous'):
                        details = EmployeeCertification.objects.filter(emp_id=request.session['hash1']).exclude(status='DELETE').values('sno', 'course_name', 'certified_by', 'issue_date', 'link', 'mooc_type__value', 'mooc_type__sno','nptel_type','nptel_type__value')
                        status = 200
                        data_values = list(details)
                        print(data_values)
                    elif (request.GET['request_type'] == 'mooc_types_dropdown'):
                        query = AarDropdown.objects.filter(field='MOOC TYPES').exclude(value=None).values('sno', 'field', 'value')
                        data_values = list(query)
                        status = 200
                    elif (request.GET['request_type'] == 'nptel_dropdown'):
                        query = AarDropdown.objects.filter(field='CERTIFICATE CATEGORY').exclude(value=None).values('sno', 'field', 'value')
                        data_values = list(query)
                        status = 200

                elif(request.method == 'POST'):
                    data = json.loads(request.body)
                    print(data)
                    if 'category' in data:
                        nptel_type = data['category']
                        EmployeeCertification.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),nptel_type=AarDropdown.objects.get(sno=nptel_type),mooc_type=AarDropdown.objects.get(sno=data['mooc_type__sno']), course_name=data['course_name'], certified_by=data['certified_by'], link=data['link'], issue_date=datetime.strptime(str(data['issue_date']).split('T')[0], "%Y-%m-%d").date(), status="INSERT", time_stamp=date.today())
                    else:
                        EmployeeCertification.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),mooc_type=AarDropdown.objects.get(sno=data['mooc_type__sno']), course_name=data['course_name'], certified_by=data['certified_by'], link=data['link'], issue_date=datetime.strptime(str(data['issue_date']).split('T')[0], "%Y-%m-%d").date(), status="INSERT", time_stamp=date.today())
                    status = 200
                    msg = "Certificate Details Saved"
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    print(data)
                    sno = data['sno']
                    EmployeeCertification.objects.filter(sno=sno).update(status='DELETE')
                    if data['nptel_type'] is not None:
                        EmployeeCertification.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),nptel_type=AarDropdown.objects.get(sno=data['nptel_type']),mooc_type=AarDropdown.objects.get(sno=data['mooc_type__sno']), course_name=data['course_name'], certified_by=data['certified_by'], link=data['link'], issue_date=datetime.strptime(str(data['issue_date']).split('T')[0], "%Y-%m-%d").date(), status='UPDATE', time_stamp=date.today())
                    else:
                        EmployeeCertification.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),mooc_type=AarDropdown.objects.get(sno=data['mooc_type__sno']), course_name=data['course_name'], certified_by=data['certified_by'], link=data['link'], issue_date=datetime.strptime(str(data['issue_date']).split('T')[0], "%Y-%m-%d").date(), status='UPDATE', time_stamp=date.today())
                    status = 200
                    msg = "Certificate Details Updated"

                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    sno = data['sno']
                    EmployeeCertification.objects.filter(sno=sno).update(status='DELETE')
                    status = 200
                    msg = "Certificate Details Deleted"
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data={'data': data_values, 'msg': msg}, status=status)


def emp_certi_report(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [319, 1345, 1371])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_by'] == 'HOD':
                        qry_dept = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1'], emp_status="ACTIVE").values('dept', 'desg')
                        qry_emp1 = EmployeePrimdetail.objects.filter(dept=qry_dept[0]['dept']).values('emp_id', 'dept__value', 'emp_category__value', 'name').order_by('name', 'dept__value', 'emp_category__value')
                        for y in qry_emp1:
                            qry_emp2 = EmployeeCertification.objects.filter(emp_id=y['emp_id']).exclude(status='DELETE').values('course_name', 'certified_by', 'issue_date', 'link')
                            y['certi_list'] = list(qry_emp2)
                        data_values = list(qry_emp1)
                        status = 200

                    elif request.GET['request_by'] == 'HR':
                        qry_emp1 = EmployeePrimdetail.objects.filter(dept__in=request.GET['dept'].split(","), emp_category__in=request.GET['coe'].split(","), emp_status="ACTIVE").values('emp_id', 'dept__value', 'emp_category__value', 'name').order_by('dept__value', 'emp_category__value', 'name')
                        for y in qry_emp1:
                            qry_emp2 = EmployeeCertification.objects.filter(emp_id=y['emp_id']).exclude(status='DELETE').values('course_name', 'certified_by', 'issue_date', 'link')
                            y['certi_list'] = list(qry_emp2)
                        data_values = list(qry_emp1)
                        status = 200
                    else:
                        status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        data_values = {"message": "Could not display"}
        status = 500
    return JsonResponse(data=data_values, status=status, safe=False)

def emp_certificate_report(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [319, 1345, 1371])
            if check == 200:
                if request.method == 'GET':
                    if request.GET['request_by'] == 'HOD':
                        dept=request.GET['dept'].split(',')
                        qry_emp1 = EmployeePrimdetail.objects.filter(emp_status="ACTIVE",dept__in=dept).exclude(emp_id="00007").values('emp_id', 'dept__value', 'emp_category__value', 'name').order_by('name', 'dept__value', 'emp_category__value')
                        for y in qry_emp1:
                            qry_emp2 = EmployeeCertification.objects.filter(emp_id=y['emp_id']).exclude(status='DELETE').values('course_name', 'certified_by', 'issue_date', 'link','mooc_type','mooc_type__value','nptel_type','nptel_type__value')
                            y['certi_list'] = list(qry_emp2)
                        data_values = list(qry_emp1)
                        status = 200
                    else:
                        status = 502
                        
                if request.method == 'POST':
                    data = json.loads(request.body)
                    old_course_name = data['old_course_name']
                    old_certified_by = data['old_certified_by']
                    old_issue_date = data['old_issue_date']
                    old_mooc_type = data['old_mooc_type']
                    old_nptel_type = data['old_nptel_type']
                    old_link = data['old_link']
                    course_name = data['course_name']
                    certified_by = data['certified_by']
                    issue_date = data['issue_date']
                    mooc_type = data['mooc_type']
                    nptel_type = data['nptel_type']
                    link = data['link']
                    emp_id = data['emp_id']
                    EmployeeCertification.objects.filter(course_name=old_course_name,mooc_type=old_mooc_type,nptel_type=old_nptel_type,certified_by=old_certified_by,issue_date=old_issue_date,link=old_link,emp_id=emp_id).update(course_name=course_name,certified_by=certified_by,issue_date=issue_date,mooc_type=mooc_type,nptel_type=nptel_type,link=link)
                    data_values = {"message": "mooc successfully updated"}
                    status = 200
                                        
                if request.method == 'DELETE':
                    data = json.loads(request.body)
                    course_name = data['course_name']
                    certified_by = data['certified_by']
                    issue_date = data['issue_date']
                    mooc_type = data['mooc_type']
                    nptel_type = data['nptel_type']
                    emp_id = data['emp_id']
                    EmployeeCertification.objects.filter(course_name=course_name,certified_by=certified_by,nptel_type=nptel_type,issue_date=issue_date,mooc_type=mooc_type,emp_id=emp_id).update(status='DELETE')
                    data_values = {"message": "mooc successfully deleted"}
                    status = 200
            else:
                status = 403
        else:
            status = 401
    else:
        data_values = {"message": "Could not display"}
        status = 500
    return JsonResponse(data=data_values, status=status, safe=False)


######################################### KIET - EXTENSION ###########################################


def extension_data(request):
    if checkpermission(request,[211,337]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET,'get_data')):
                print("sss")
                data = list(Extension.objects.all().values())
                print(data)
                for x in data:
                    for k in x:
                        if(x[k]==None):
                            x[k]="----"
                return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
            elif(requestType.custom_request_type(request.GET,'get_dept')):
                data2 = list(Extension.objects.all().values('Dept').distinct())
                data = []
                for x in data2:
                    print(x)
                    d = list(Extension.objects.filter(Dept=x['Dept']).values())
                    for c in d:
                        for k in c:
                            if(c[k]== None ):
                                c[k]="----"
                    obj = {'dept_name': x['Dept'], 'value': d}
                    data.append(obj)
                return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS) 
        elif checkpermission(request,[211]) == statusCodes.STATUS_SUCCESS:               
            if requestMethod.POST_REQUEST(request):
                info = json.loads(request.body)
                if 'id'in info:
                    id = info['id']
                    print(info)
                    qry = Extension.objects.filter(id=id).update(Extension=info['Extension'])
                    return functions.RESPONSE(statusMessages.MESSAGE_UPDATE,statusCodes.STATUS_SUCCESS)                               
                else:
                    qry = Extension.objects.create(Names=info['Names'], Designation=info['Designation'], Extension=info['Extension'], Mobile_No=info['Mobile_No'], Email=info['Email'], Dept=info['Dept'])
                    return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)                               
            elif requestMethod.DELETE_REQUEST(request):
                info = json.loads(request.body)
                id = info['id']
                qry = Extension.objects.filter(id=id).delete()
                return functions.RESPONSE(statusMessages.MESSAGE_DELETE,statusCodes.STATUS_SUCCESS)
            else:
                return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
        else:
            functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

####################################### REPORTING REPORT ###################################
# sasas


def reporting_report(request):
    data = []
    check = checkpermission(request, [211, 1345])
    if check == 200:
        session_name = request.session['Session_name']
        session = request.session['Session_id']
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_data')):
                category = request.GET['category'].split(',')
                dept = request.GET['dept'].split(',')
                employees = list(EmployeePrimdetail.objects.filter(dept__in=dept, emp_category__in=category).exclude(emp_id='00007').exclude(emp_status="SEPARATE").values('emp_id', 'name', 'dept__value', 'desg__value', 'mob', 'doj', 'email', 'emp_category__value'))
                for emp in employees:
                    reporting = list(Reporting.objects.filter(emp_id=emp['emp_id']).values('department', 'reporting_to', 'reporting_no').order_by('reporting_no'))
                    for l in reporting:
                        report_on = list(EmployeePrimdetail.objects.filter(dept=l['department'], desg=l['reporting_to']).exclude(emp_status="SEPARATE").values('emp_id', 'name', 'dept__value', 'desg__value').annotate(R_emp_id=F('emp_id'), R_name=F('name')))
                        if len(report_on) > 0:
                            l['R_emp_id'] = report_on[0]['R_emp_id']
                            l['R_name'] = report_on[0]['R_name']
                        else:
                            l['R_emp_id'] = '---'
                            l['R_name'] = '---'
                    emp['reporting'] = reporting
                data = employees
            return functions.RESPONSE(data, 200)

        else:
            return functions.RESPONSE({'msg': 'You are not authorized to access this page'}, 405)
    else:
        return functions.RESPONSE({'msg': 'You are not authorized to access this page'}, 403)


############################################################ 2021 SESSION ################################################################
def get_net_experience(emp_id):  # BEFORE + IN KIET (INCUDING NON - TEACHING AS WELL)
    data = []
    qry = EmployeeExperience.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('exp_type','effective_exp_years','effective_exp_months','actual_exp_year','actual_exp_month')
    year,month = 0,0
    for q in qry:
        if 'KIET' in str(q['exp_type']):
            year+=q['actual_exp_year']
            month+=q['actual_exp_month']
        else:
            year+=q['effective_exp_years']
            month+=q['effective_exp_months']
    year+=month//12
    month%=12

    month = str(month)+" months"
    year = str(year)+" years"

    return (year,month)

def get_teaching_exp(emp_id):   # ONLY TEACHING IE BEFORE KIET: T -> EFFECTIVE + AFTER KIET: KIET -> EFFECTIVE
    data = []
    qry = EmployeeExperience.objects.filter(emp_id=emp_id).filter(Q(exp_type__contains='T')| Q(exp_type__contains='KIET')).exclude(status="DELETE").values('exp_type','effective_exp_years','effective_exp_months','actual_exp_year','actual_exp_month')
    year,month = 0,0
    for q in qry:
        year+=q['effective_exp_years']
        month+=q['effective_exp_months']
    year+=month//12
    month%=12
    return (month,year)
# print(get_net_experience(12066))
# print(get_teaching_exp(12066))

#########################################################################################
######################roles to employee and employees to roles report##############
def emp_roles_list(qry_list):
    for i in range(len(qry_list)):
        qry1=list(Roles.objects.filter(emp_id=qry_list[i]['emp_id_id']).values_list('roles',flat=True))
        role=list(EmployeeDropdown.objects.filter(sno__in=qry1).extra(select={'role':'value'}).values_list('role',flat=True))
        qry_list[i]["roles"]=role
    return qry_list

def roles_report(request):
    check = checkpermission(request, [1345])
    if check == 200:
        data=[]
        session_name = request.session['Session_name']
        session = request.session['Session_id']
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'roles_to_employee')):
                qry=EmployeeDropdown.objects.filter(field="ROLES").exclude(value__isnull=True)
                all_roles=list(qry.exclude(value="SUPERUSER").extra(select={'role':'value','role_id':'sno'}).values('role','role_id'))
                data=all_roles
            if(requestType.custom_request_type(request.GET, 'get_emp')):
                all_emp=list(EmployeePrimdetail.objects.filter(emp_status="ACTIVE").exclude(emp_id="00007").values('name','emp_id'))
                for emp in all_emp:
                    data.append({"emp_name":emp['name']+" ( "+emp['emp_id']+" )","emp_id":emp['emp_id']})
            if(requestType.custom_request_type(request.GET, 'get_emp_detail')):
                emp_id = request.GET['emp_id'].split(',')
                qry=list(EmployeePrimdetail.objects.filter(emp_id__in=emp_id).values(
                    "name", "emp_id_id", "doj", "mob", "mob1","desg__value", "lib_card_no",
                    "email", "dept__value", "current_pos__value", "emp_category__value","emp_type__value",
                    "organization__value", "join_pos__value", "cadre__value", "shift__value","title__value","ladder__value"
                ).order_by("name"))
                data=emp_roles_list(qry) 
            if(requestType.custom_request_type(request.GET, 'get_rolewise_emp')):
                role = request.GET['roles'].split(',')
                emp_list=[]
                qry=list(Roles.objects.filter(roles__in=role).exclude(emp_id="00007").values_list('emp_id',flat=True))#all emp with that roles
                roles_list=list(map(int, role))
                for emp in qry:
                    roles_emp=list(Roles.objects.filter(emp_id=emp).values_list('roles',flat=True))#roles of a particular emp
                    if(set(roles_list).issubset(set(roles_emp))):
                        emp_list.append(emp)
                employees=list(EmployeePrimdetail.objects.filter(emp_id__in=emp_list,emp_status="ACTIVE").values(
                    "name", "emp_id_id", "doj", "mob", "mob1","desg__value","lib_card_no", "email",
                    "dept__value", "current_pos__value","emp_category__value", "emp_type__value", "organization__value",
                    "join_pos__value", "cadre__value", "shift__value","title__value","ladder__value").order_by("name"))
                data=emp_roles_list(employees)
            return functions.RESPONSE(data, 200)
        else:
            return functions.RESPONSE({'msg': 'You are not authorized to access this page'}, 405)
    else:
        return functions.RESPONSE({'msg': 'You are not authorized to access this page'}, 403)


def emp_salary_slip(request):
    check = checkpermission(request, [211])
    if check == 200:
        data = []
        if request.method == "POST":
            data = json.loads(request.body)
            request_type = data['request_type']
            date = data['month']
            month = int(date.split('/')[0])
            year = int(date.split('/')[1])
            # print(month, year)
            sdate = datetime(year, month, 1).date()
            # print(date)
            session = getCurrentSession(sdate)
            if request_type == "get_all_emp":
                org, dept, category = list(data.values())[:-2]
                if dept == 'ALL':
                    dept = list(EmployeeDropdown.objects.filter(
                        field="Department").exclude(value__isnull=True).values_list("sno"))
                else:
                    dept = dept.split(',')
                if category=="ALL":
                    category = list(EmployeeDropdown.objects.exclude(value__isnull=True).filter(field="CATEGORY OF EMPLOYEE").values_list('sno'))
                else:
                    category=category.split(',')
                
                qry = list(EmployeePayableDays.objects.filter(session=session, month=month, emp_id__organization=org, dept__in=dept, emp_category__in=category).annotate(name=F('emp_id__name'), designation=F('emp_id__desg__value'), status=F(
                    'emp_id__emp_status'), category=F('emp_category__value')).values('emp_id', 'name', 'desg', 'dept', 'emp_category', 'designation', 'dept__value', 'month', 'category', 'status', 'emp_id__organization').distinct())
            
            if request_type == "get_emp_slip":
                emp_id, dept, org, desig, category, status = list(data.values())[:-2]

                taxstatus_li = [0, 1]

                months_list = []
                month_add = 4
                while True:
                    months_list.append(month_add)
                    if month_add == month:
                        break
                    month_add = max((month_add + 1) % 13, 1)

                session = getCurrentSession(sdate)
                if session == -1:
                    return JsonResponse(data={'msg': 'Accounts Session not found'}, status=202)

                loss_deductions = []
                total_loss = []

                ########### check whether salary has been locked for the selected month ####
                qry_check1 = DaysGenerateLog.objects.filter(
                    sessionid=session, acc_sal_lock='Y', month=month).values()
                if len(qry_check1) > 0:
                    emp_details = EmployeePayableDays.objects.filter(emp_id=emp_id, month=month, session=session).annotate(emp_id__desg__value=F('desg__value'), emp_id__dept__value=F('dept__value'), bank_Acc_no=F('bank_acc_no'), emp_id__title__value=F(
                        'title__value')).values('emp_id', 'emp_id__name', 'emp_id__dept__value', 'emp_id__desg__value', 'emp_id__doj', 'bank_Acc_no', 'uan_no', 'total_days', 'working_days', 'leave', 'holidays', 'emp_id__title__value')

                    total_days = emp_details[0]['total_days']
                    working_days = emp_details[0]['working_days'] + \
                        emp_details[0]['leave'] + emp_details[0]['holidays']

                    ###################### get stored values of salary components for the selected month ################
                    gross_payable = stored_gross_payable_salary_components(
                        emp_id, session, month)

                    ###################### get stored values of arrear for the selected month ################

                    arrear = stored_arrear(emp_id, month, session)

                    ###################### get stored values of constant deductions for the selected month ################

                    const_ded = calculate_constant_deduction_stored(
                        emp_id, session, gross_payable, taxstatus_li, month)
                    ###################### get stored values of variable deductions for the selected month ################

                    var_ded = calculate_variable_deduction_stored(
                        emp_id, session, month)

                    arrear_value = 0
                    arrear_list = []

                    arrear_list = arrear['data']

                    income_tax_sum_comp = calculate_income_tax_sum(emp_id, session, working_days, total_days, gross_payable, month,
                                                                   arrear_list[2], arrear_list[4], arrear_list[3]['value'], arrear_list[0]['value'], arrear_list[1]['value'])

                    income_tax_sum = 0
                    income_tax_sum_comp_data = []

                    ############ iterate for  all income tax components value i.e BASIC,AGP,HRA etc. ##############
                    for d in income_tax_sum_comp:
                        income_tax_sum_comp_data.append(
                            {'value': d['value'], 'Ing_value': d['Ing_value']})
                        income_tax_sum += d['value']

                    income_tax_sum_comp_data.append(
                        {'value': income_tax_sum, 'Ing_value': 'TOTAL'})

                    # calculate epf (constant deduction) to be deducted from employee's salary for that month #########3
                    total_epf = calculate_epf(
                        emp_id, session, [0, 1], gross_payable, month)
                    income_tax_sum_comp_data.append(
                        {'value': total_epf['value'], 'Ing_value': 'EPF'})

                    ############ calculate other income declared by employee ##########
                    other_income = calculate_other_income(emp_id, session)

                    ##################################################

                    hra_for1 = 0
                    for comp in income_tax_sum_comp:
                        if 'HRA' in comp['Ing_value']:
                            hra_for1 += comp['value']

                    # hra_for1=hra_exemption_formula1(emp_id,session,working_days,total_days,month)
                    hra_for2 = hra_exemption_formula2(
                        emp_id, session, income_tax_sum, hra_for1)
                    hra_for3 = hra_exemption_formula3(
                        emp_id, session, income_tax_sum, hra_for1)

                    ##################### get minimum of hra1,hra2,hra3 values. If value is <0, make it 0 using max(-ve value,0) ######
                    hra_exemption = max(
                        min(hra_for1, hra_for2, hra_for3['value']), 0)

                    ################### calculate loss deductions declared by employee in 12B form. It include 80C,80D,80CCD etc. ####
                    loss = calculate_loss_deductions(
                        emp_id, session, gross_payable, const_ded, month)

                    ################## get standard deduction value ##########################
                    qry_std_ded = AccountsDropdown.objects.filter(
                        field='STANDARD DEDUCTION', session=session).exclude(value__isnull=True).values('value')
                    std_ded_amt = int(qry_std_ded[0]['value'])

                    ############# calculate value on which income tax is to be calculated ################

                    ############# add income tax components value(i.e. BASIC+AGP+HRA etc.)+ other income total value - minimum of hra exemption value - loss and deductions final value (80C value +80D Value+....) - standard deduction amount ######

                    ########### if value is <0, make it 0 #####################
                    final_value = max(
                        other_income['value'] + income_tax_sum - hra_exemption - loss['value'] - std_ded_amt, 0)

                    ########## calculate income tax on final value ###################
                    income_tax = calculate_income_tax(
                        emp_id, session, final_value)

                    ########## calculate rebate offered on income tax, tax after rebate and cess amount to be paid ###############
                    tax_after_rebate = calculate_tax_after_rebate(
                        final_value, income_tax, session)

                    # final_monthly_tax=calculate_monthly_income_tax(tax_after_rebate['final_tax'],session,emp_id,month)

                    # get income tax to be paid in that selected month #######################3
                    q_IT = Income_Tax_Paid.objects.filter(
                        emp_id=emp_id, session=session, month=month).values('monthly_tax_paid')
                    if len(q_IT) > 0:
                        income_tax = q_IT[0]['monthly_tax_paid']
                    else:
                        income_tax = 0

                    ################### loss and deductions ################################################

                    time = datetime.now()

                    ################ get other income components ###############
                    other_income = declaration_components(
                        "other_income", session)
                    n = len(other_income)
                    total = 0

                    ############## get their value as declared by employee #############
                    for i in range(n):
                        q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id, Dec_Id=other_income[i]['sno'], Session_Id=AccountsSession.objects.get(
                            id=session), Value__gt=0).values('Value').exclude(status="DELETE").order_by('-id')[:1]
                        if len(q_dec) > 0:
                            total += q_dec[0]['Value']
                            loss_deductions.append(
                                {"country": "OTHER INCOME", "name": other_income[i]['value'], "money": q_dec[0]['Value']})
                    total_loss.append(
                        {"field": "OTHER INCOME", 'value': total})

                    ################ get house rent allowance components i.e. rent per month and number of months ###############

                    exemptions = declaration_components("exemptions", session)
                    total = 1
                    n = len(exemptions[0]['data'])
                    for i in range(n):
                        q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id, Dec_Id=exemptions[0]['data'][i]['sno'], Session_Id=session).values(
                            'Value').exclude(status="DELETE").order_by('-id')[:1]
                        if len(q_dec) > 0:
                            loss_deductions.append(
                                {"country": "EXEMPTIONS", "name": exemptions[0]['data'][i]['value'], "money": q_dec[0]['Value']})
                            total *= q_dec[0]['Value']

                        else:
                            loss_deductions.append(
                                {"country": "EXEMPTIONS", "name": exemptions[0]['data'][i]['value'], "money": 0})

                    if total == 1:
                        total = 0
                    total_loss.append({"field": "EXEMPTIONS", 'value': total})

                    ################ get 80C, 80D, 80CCD components, it include LIC,LIP ,ULIP etc. ############
                    loss = declaration_components("loss_deductions", session)
                    m = len(loss)

                    ######### get value as declared by employee ###############################################
                    for j in range(m):
                        total = 0
                        n = len(loss[j]['data'])
                        for i in range(n):
                            q_dec = Employee_Declaration.objects.filter(Emp_Id=emp_id, Dec_Id=loss[j]['data'][i]['sno'], Session_Id=session, Value__gt=0).values(
                                'Value').exclude(status="DELETE").order_by('-id')[:1]
                            if len(q_dec) > 0:
                                total += q_dec[0]['Value']
                                loss_deductions.append(
                                    {"country": loss[j]['value'], "name": loss[j]['data'][i]['value'], "money": q_dec[0]['Value']})
                        total_loss.append(
                            {"field": loss[j]['value'], 'value': total})

                    upto_values = []
                    total_v = 0

                    qry_sal_ing = SalaryIngredient.objects.filter(session=session).exclude(
                        status="DELETE").values('id', 'Ingredients__value')

                    ######################## get sum of salary components value already paid to employee #########

                    ######### e.g for month of july , for basic, its value will be april basic+may basic + june basic+ july basic #####
                    for gp in qry_sal_ing:
                        dj_val = MonthlyPayable_detail.objects.filter(Emp_Id=emp_id, session=session, Ing_Id=gp['id'], Month__in=months_list).extra(
                            select={'su': 'SUM(payable_value)'}).values('su')
                        if len(dj_val) > 0:
                            if(dj_val[0]['su'] is None):
                                dj_val[0]['su'] = 0
                            upto_values.append(
                                {'field': gp['Ingredients__value'], 'value': dj_val[0]['su']})
                            total_v += dj_val[0]['su']
                        else:
                            upto_values.append(
                                {'field': gp['Ingredients__value'], 'value': 0})

                    ########## get arrear value received to employee upto that month #############################
                    q_arrear = MonthlyArrear_detail.objects.filter(
                        Emp_Id=emp_id, session=session, Month__in=months_list).extra(select={'su': 'SUM(value)'}).values('su')
                    if len(q_arrear) > 0:
                        upto_values.append(
                            {'field': 'ARREAR', 'value': q_arrear[0]['su']})
                        total_v += q_arrear[0]['su']
                    else:
                        upto_values.append({'field': 'ARREAR', 'value': 0})

                    upto_values.append({'field': 'TOTAL', 'value': total_v})

                    ############# get EPF deducted from employee salary upto that month  ############
                    epf_paid = MonthlyDeductionValue.objects.filter(deduction_id__constantDeduction__DeductionName__value="EPF", Emp_Id=emp_id,
                                                                    deduction_id__variableDeduction__isnull=True, session=session, month__in=months_list).values('value')
                    total_e = 0
                    for ep in epf_paid:
                        total_e += ep['value']
                    upto_values.append({'field': 'EPF', 'value': total_e})

                    # get mediclaim deducted from employee salary upto that month ############3

                    med_paid = MonthlyDeductionValue.objects.filter(
                        deduction_id__constantDeduction__DeductionName__value="MEDICLAIM", Emp_Id=emp_id, session=session, month__in=months_list).values('value')
                    total_m = 0
                    for me in med_paid:
                        total_m += me['value']
                    upto_values.append(
                        {'field': 'MEDICLAIM', 'value': total_m})

                    ###################  get income tax paid by employee upto that month ######################
                    q_it = Income_Tax_Paid.objects.filter(emp_id=emp_id, session=session, month__in=months_list).extra(
                        select={'su': 'SUM(monthly_tax_paid)'}).values('su')
                    if len(q_it) > 0:
                        tax_paid = q_it[0]['su']
                    else:
                        tax_paid = 0

                    q_Sess = AccountsSession.objects.filter(
                        id=session).values('session')
                    msg = "Success"
                    status = 200
                    data_values = {'msg': msg, 'data': {'emp_details': list(emp_details), 'gross_payable': gross_payable, 'arrear': arrear, 'const_ded': const_ded, 'var_ded': var_ded, 'income_tax': income_tax, 'total_days': total_days, 'working_days': working_days, 'loss_deductions': loss_deductions, 'total_loss': total_loss,
                                                        'upto_values': upto_values, 'net_income': final_value, 'net_income_tax': tax_after_rebate['final_tax'], 'tax_paid': tax_paid, 'tax_left': tax_after_rebate['final_tax'] - tax_paid, 'proposed_year': income_tax_sum_comp_data, 'monthly_arrear': arrear['final_value'], 'session': q_Sess[0]['session']}}
                else:
                    msg = "Salary slip not available"
                    status = 202
                    data_values = {'msg': msg}
                    return functions.RESPONSE(data_values, status)
                qry = data_values
            return functions.RESPONSE(qry, 200)
        else:
            return functions.RESPONSE({'msg': 'You are not authorized to access this page'}, 405)
    else:
        return functions.RESPONSE({'msg': 'You are not authorized to access this page'}, 403)
