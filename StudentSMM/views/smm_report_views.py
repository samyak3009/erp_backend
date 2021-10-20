from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F, Count
from login.views import checkpermission, generate_session_table_name
import json
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType
from StudentAcademics.models import *

from Registrar.models import *
from musterroll.models import EmployeePrimdetail
from itertools import groupby
from StudentAcademics.views import *

from StudentSMM.models import *

from StudentSMM.views.smm_function_views import *
import time
import math


def menteePerformanceCard(request):
    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        data['personal_data'] = get_profile(uniq_id, session_name)
        session = list(Semtiming.objects.filter(session_name=session_name).values('sem_end', 'session', 'session_name', 'uid', 'sem_start'))
        data['performance_detail'] = SemesterWisePerformance(uniq_id, session_name, session[0]['uid'])
        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def facultyCountReport(request):
    emp_id = request.session['hash1']
    data = []
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        CouncellingDetail = generate_session_table_name('CouncellingDetail_', session_name)
        CouncellingApproval = generate_session_table_name('CouncellingApproval_', session_name)
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                get_hod_department = EmployeePrimdetail.objects.filter(emp_id=emp_id).exclude(emp_id="00007").exclude(emp_status="SEPARATE").values('dept', 'dept__value')
                if len(get_hod_department) > 0:
                    emps = EmployeePrimdetail.objects.filter(dept=get_hod_department[0]['dept']).exclude(emp_id="00007").exclude(emp_status="SEPARATE").values('emp_id', 'name', 'dept', 'dept__value', 'desg', 'desg__value')
                    counselling_data = []
                    emp_count_data = []
                    for emp in emps:
                        approve_count = 0
                        pending_count = 0
                        counselling_count = 0
                        coun_id = CouncellingDetail.objects.filter(added_by=emp['emp_id']).exclude(status="DELETE").values_list('id', flat=True)

                        for c in coun_id:
                            qry = list(CouncellingApproval.objects.filter(councelling_detail=c).exclude(status="DELETE").exclude(councelling_detail__status="DELETE").values('councelling_detail__date_of_councelling', 'councelling_detail__type_of_councelling', 'councelling_detail__type_of_councelling__value', 'councelling_detail__uniq_id', 'councelling_detail__student_document', 'councelling_detail__remark', 'councelling_detail__status', 'councelling_detail__added_by', 'councelling_detail__added_by__name', 'councelling_detail__uniq_id__uniq_id__name', 'councelling_detail__uniq_id__year', 'councelling_detail__uniq_id__uniq_id__dept_detail', 'councelling_detail__uniq_id__uniq_id__dept_detail__dept__value', 'councelling_detail__uniq_id__uniq_id__dept_detail__course__value', 'level', 'remark', 'appoval_status', 'approved_by', 'approved_by__name', 'councelling_detail__added_by__dept', 'councelling_detail__added_by__dept__value', 'councelling_detail__added_by__desg', 'councelling_detail__added_by__desg__value').order_by('-id'))
                            if len(qry) > 0:
                                counselling_data.append(qry[0])
                                if qry[0]['appoval_status'] == "APPROVED":
                                    approve_count = approve_count + 1
                                    counselling_count = counselling_count + 1
                                elif qry[0]['appoval_status'] == "PENDING":
                                    pending_count = pending_count + 1
                                    counselling_count = counselling_count + 1
                        emp['total_approved'] = approve_count
                        emp['total_pending'] = pending_count
                        emp['total_counselling'] = counselling_count
                        emp_count_data.append(emp)
                    data = {'Consolidate_data': emp_count_data, 'Table_data': counselling_data}
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def facultyCounsellingReport(request):
    emp_id = request.session['hash1']
    data = []
    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        CouncellingDetail = generate_session_table_name('CouncellingDetail_', session_name)
        CouncellingApproval = generate_session_table_name('CouncellingApproval_', session_name)
        studentSession = generate_session_table_name('studentSession_', session_name)
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                uniq_ids = []
                course = request.GET['course'].split(',')
                branch = request.GET['branch'].split(',')
                sem = request.GET['sem'].split(',')
                section = request.GET['section'].split(',')
                group_id = request.GET['group_id']
                grpstudents = GroupStudents(group_id, session_name)
                for gr in grpstudents:
                    uniq_ids.append(gr['profile']['uniq_id'])
                coun_id = CouncellingDetail.objects.filter(added_by=emp_id, uniq_id__in=uniq_ids).exclude(status="DELETE").values_list('id', flat=True)

                for c in coun_id:
                    qry = list(CouncellingApproval.objects.filter(councelling_detail=c).exclude(status="DELETE").values('councelling_detail__date_of_councelling', 'councelling_detail__type_of_councelling', 'councelling_detail__type_of_councelling__value', 'councelling_detail__uniq_id', 'councelling_detail__uniq_id__uniq_id__uni_roll_no', 'councelling_detail__student_document', 'councelling_detail__remark', 'councelling_detail__status', 'councelling_detail__added_by', 'councelling_detail__added_by__name', 'councelling_detail__uniq_id__uniq_id__name', 'councelling_detail__uniq_id__sem', 'councelling_detail__uniq_id__sem__sem', 'councelling_detail__uniq_id__section', 'councelling_detail__uniq_id__section__section', 'councelling_detail__uniq_id__year', 'councelling_detail__uniq_id__uniq_id__dept_detail', 'councelling_detail__uniq_id__uniq_id__dept_detail__dept__value', 'councelling_detail__uniq_id__uniq_id__dept_detail__course__value', 'level', 'remark', 'appoval_status', 'approved_by', 'approved_by__name', 'councelling_detail__added_by__dept', 'councelling_detail__added_by__dept__value', 'councelling_detail__added_by__desg', 'councelling_detail__added_by__desg__value', 'councelling_detail').order_by('-id'))
                    if len(qry) > 0:
                        data.append(qry[0])
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            if 'councelling_detail' in data:
                id = data['councelling_detail']
            else:
                id = None
            date = data['date'].split('T')[0]
            uniq_id = data['uniq_id']
            type_of_councelling = data['type_of_councelling']
            remark = data['remark']
            stu_doc = data['student_document']
            if id != None:
                CouncellingDetail.objects.filter(added_by=emp_id, id=id).exclude(status="DELETE").update(status="DELETE")
                CouncellingApproval.objects.filter(councelling_detail__added_by=emp_id, councelling_detail=id, appoval_status="PENDING").exclude(status="DELETE").update(status="DELETE")

            if check_if_mentor_of_student(uniq_id, emp_id, session_name) == True:
                q_counselling_create = CouncellingDetail.objects.create(date_of_councelling=date, type_of_councelling=StudentAcademicsDropdown.objects.get(sno=type_of_councelling), uniq_id=studentSession.objects.get(uniq_id=uniq_id), remark=remark, student_document=stu_doc, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
                q_counselling_approval_create = CouncellingApproval.objects.create(councelling_detail=CouncellingDetail.objects.get(id=q_counselling_create.id))
            else:
                return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE("YOU ARE NOT ELIGIBLE TO FILL THE COUNSELLING DETAILS."), statusCodes.STATUS_SERVER_ERROR)
            if(q_counselling_approval_create and q_counselling_create):
                return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_SUCCESS)

            else:
                return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE("COULD NOT INSERT"), statusCodes.STATUS_SERVER_ERROR)
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            del_id = data['councelling_detail']
            CouncellingDetail.objects.filter(added_by=emp_id, id=del_id).exclude(status="DELETE").update(status="DELETE")
            CouncellingApproval.objects.filter(councelling_detail__added_by=emp_id, councelling_detail=del_id, appoval_status="PENDING").exclude(status="DELETE").update(status="DELETE")
            data = {'msg': 'Successfully Deleted.'}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
