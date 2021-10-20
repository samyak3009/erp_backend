
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.db.models import Sum,F
from login.views import checkpermission,generate_session_table_name
import json
import time
import math
from itertools import groupby

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod


from StudentAcademics.models import *
from Registrar.models import *
from StudentSMM.models import *
from StudentMMS.models import *
from login.models import EmployeePrimdetail

from .smm_function_views import *
from StudentMMS.constants_functions import requestType
from StudentAcademics.views import *


def pending_approval_function(request):

    if(academicCoordCheck.isAcademicHOD(request)):

        emp_id=request.session['hash1']
        session=request.session['Session_id']
        session_name=request.session['Session_name']
        print(session_name)
        CouncellingDetail = generate_session_table_name("CouncellingDetail_",session_name)
        CouncellingApproval = generate_session_table_name("CouncellingApproval_",session_name)

        if(requestMethod.GET_REQUEST(request)):
            if(requestType.custom_request_type(request.GET,'pending_counselling_list')):
                print(request)
                dept_id=request.GET['dept']
                sem=request.GET['sem'].split(",")
                sec=request.GET['section'].split(",")
                from_date=request.GET['from_date']
                to_date=request.GET['to_date']
                student_list=list(CouncellingApproval.objects.filter(councelling_detail__uniq_id__sem__sem__in=sem,councelling_detail__uniq_id__section__section__in=sec,councelling_detail__uniq_id__sem__dept=dept_id,appoval_status='PENDING',councelling_detail__date_of_councelling__gte=from_date,councelling_detail__date_of_councelling__lte=to_date).exclude(status='DELETE').exclude(councelling_detail__status='DELETE').values().annotate(uniq_id=F('councelling_detail__uniq_id'),name=F('councelling_detail__uniq_id__uniq_id__name'),section=F('councelling_detail__uniq_id__section__section'),semester=F('councelling_detail__uniq_id__sem__sem'),university_roll_no=F('councelling_detail__uniq_id__uniq_id__uni_roll_no'),library_id=F('councelling_detail__uniq_id__uniq_id__lib'),mentor_name=F('councelling_detail__added_by__name'),type_of_counselling=F('councelling_detail__type_of_councelling__value'),mentor_remark=F('councelling_detail__remark'),date=F('councelling_detail__date_of_councelling')))


                for stu in student_list:
                        prev_count=CouncellingApproval.objects.filter(councelling_detail__uniq_id=stu['uniq_id'],councelling_detail__type_of_councelling__value=stu['type_of_counselling'],appoval_status='APPROVED').exclude(status='DELETE').exclude(councelling_detail__status='DELETE').count()
                        stu['previous_counselling_count']=prev_count

                data={'data':student_list}

            elif(requestType.custom_request_type(request.GET,'view_previous')):

                dept_id=list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept'))
                dept=list(CourseDetail.objects.filter(dept=dept_id[0]['dept']).values('uid'))

                student_list=list(CouncellingApproval.objects.exclude(appoval_status='PENDING').exclude(councelling_detail__status='DELETE').filter(councelling_detail__uniq_id__sem__dept=dept[0]['uid']).exclude(status='DELETE').values().annotate(uniq_id=F('councelling_detail__uniq_id'),name=F('councelling_detail__uniq_id__uniq_id__name'),section=F('councelling_detail__uniq_id__section__section'),semester=F('councelling_detail__uniq_id__sem__sem'),university_roll_no=F('councelling_detail__uniq_id__uniq_id__uni_roll_no'),library_id=F('councelling_detail__uniq_id__uniq_id__lib'),mentor_name=F('councelling_detail__added_by__name'),type_of_counselling=F('councelling_detail__type_of_councelling__value'),mentor_remark=F('councelling_detail__remark'),date=F('councelling_detail__date_of_councelling'),approval_status=F('appoval_status'),approved_by=F('approved_by__name')))

                for stu in student_list:
                    prev_count=CouncellingApproval.objects.filter(councelling_detail__uniq_id=stu['uniq_id'],councelling_detail__type_of_councelling__value=stu['type_of_counselling'],appoval_status='APPROVED').exclude(status='DELETE').exclude(councelling_detail__status='DELETE').count()
                    stu['previous_counselling_count']=prev_count

                data={'data':student_list}

            elif(requestType.custom_request_type(request.GET,'sem_start_date')):
                date=get_sem_start_date(session)
                data={'data':date}
                print(data)

            return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)


        elif requestMethod.POST_REQUEST(request):
            data=json.loads(request.body)
            for q in data:
                councelling_detail=q['councelling_detail']
                remark=q['hod_remark']
                action_taken=q['action_taken']
                print(action_taken)
                qry=CouncellingApproval.objects.filter(councelling_detail=councelling_detail).update(appoval_status=action_taken,approved_by=emp_id,remark=remark)
                print(qry)
            data=statusMessages.CUSTOM_MESSAGE('COUNSELLING ' + data[0]['action_taken'])

            return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)


def indiscipline_act_approval_function(request):
    data=[]
    if(academicCoordCheck.isAcademicHOD(request)):
        session_name=request.session['Session_name']
        print(session_name)
        emp_id=request.session['hash1']
        Incident = generate_session_table_name("Incident_",session_name)
        IncidentReporting = generate_session_table_name("IncidentReporting_",session_name)
        IncidentApproval = generate_session_table_name("IncidentApproval_",session_name)

        if(requestMethod.GET_REQUEST(request)):
            if(requestType.custom_request_type(request.GET,'indiscipline_act_list')):
                dept_id=request.GET['dept']
                sem=request.GET['sem'].split(",")
                sec=request.GET['section'].split(",")
                from_date=request.GET['from_date']
                to_date=request.GET['to_date']
                student_list=list(IncidentApproval.objects.exclude(incident_detail__status='DELETE').filter(incident_detail__uniq_id__sem__sem__in=sem,incident_detail__uniq_id__section__section__in=sec,incident_detail__uniq_id__sem__dept=dept_id,appoval_status='PENDING',incident_detail__incident__date_of_incident__gte=from_date,incident_detail__incident__date_of_incident__lte=to_date).values('incident_detail__added_by__name','incident_detail__incident__description','incident_detail__action','incident_detail__comm_to_parent','incident_detail__time_stamp','incident_detail','incident_detail__incident__incident_document','incident_detail__incident__date_of_incident','incident_detail__student_document').annotate(uniq_id=F('incident_detail__uniq_id'),uniq_id__name=F('incident_detail__uniq_id__uniq_id__name'),section__section=F('incident_detail__uniq_id__section__section'),sem__sem=F('incident_detail__uniq_id__sem__sem'),uniq_id__uni_roll_no=F('incident_detail__uniq_id__uniq_id__uni_roll_no'),uniq_id__lib=F('incident_detail__uniq_id__uniq_id__lib')))

                data={'data':student_list}

            elif(requestType.custom_request_type(request.GET,'view_previous')):
                dept_id=list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept'))
                dept=list(CourseDetail.objects.filter(dept=dept_id[0]['dept']).values('uid'))

                previous=list(IncidentApproval.objects.exclude(incident_detail__status='DELETE').exclude(appoval_status='PENDING').filter(incident_detail__uniq_id__sem__dept=dept[0]['uid']).values('incident_detail__added_by__name','incident_detail__incident__description','incident_detail__action','incident_detail__comm_to_parent','incident_detail__time_stamp','incident_detail','incident_detail__incident__incident_document','incident_detail__incident__date_of_incident','appoval_status','remark').annotate(uniq_id=F('incident_detail__uniq_id'),uniq_id__name=F('incident_detail__uniq_id__uniq_id__name'),section__section=F('incident_detail__uniq_id__section__section'),sem__sem=F('incident_detail__uniq_id__sem__sem'),uniq_id__uni_roll_no=F('incident_detail__uniq_id__uniq_id__uni_roll_no'),uniq_id__lib=F('incident_detail__uniq_id__uniq_id__lib'),approved_by=F('approved_by__name')))

                data={'data':previous}

            return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)




        elif(requestMethod.POST_REQUEST(request)):
            data=json.loads(request.body)
            print(data)
            for d in data:
                incident_detail=d['incident_detail']
                action_taken=d['action_taken']
                remark=d['hod_remark']
                qry=IncidentApproval.objects.filter(incident_detail=incident_detail).update(appoval_status=action_taken,approved_by=emp_id,remark=remark)
                data=statusMessages.CUSTOM_MESSAGE('INDISCIPLINE ACT ' + data[0]['action_taken'])
            return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
