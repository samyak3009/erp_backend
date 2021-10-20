from __future__ import unicode_literals
import copy
from django.shortcuts import render
import json
from django.http import JsonResponse
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import calendar
from django.db.models import Q
from datetime import date
from django.contrib.auth.models import User

from erp.constants_variables import *
from erp.constants_functions import functions, requestMethod
from StudentMMS.constants_functions import *

from login.models import AarDropdown, EmployeeDropdown
from musterroll.models import EmployeePrimdetail, EmployeeResearch, EmployeeAcademic, Reporting, AarReporting
from DeptAchievement.models import *

from login.views import checkpermission
from DeptAchievement.views.dept_ach_functions import *
from DeptAchievement.views.dept_ach_check_function import *
from Achievement.models import *

def GuestLecture(request):
    session_id = request.session['Session_id']
    session_name = request.session['Session_name']
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'onload')):
                q1 = get_department()
                q2 = Year()
                data = {"Branch": list(q1), "YEAR": list(q2)}

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            if(requestType.custom_request_type(request.GET, 'view_prev')):
                all_data = list(guestLectures.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('id', 'date', 'topic', 'speaker', 'speaker_profile', 'organization', 'designation', 'contact_number', 'e_mail', 'participants_no', 'remark').order_by('time_stamp'))

                for i in all_data:
                    year = list(AarMultiselect.objects.filter(sno=i['id'], type='GUEST LECTURE', field='YEAR').values_list('value', flat=True))
                    Year1 = [(int(y)) for y in year]
                    i['year'] = Year1
                    dept_id = list(AarMultiselect.objects.filter(sno=i['id'], type='GUEST LECTURE', field='DEPARTMENT').values_list('value', flat=True))
                    Dept = [(int(y)) for y in dept_id]
                    i['dept_id'] = Dept
                    department = list(EmployeeDropdown.objects.filter(sno__in=dept_id).values_list('value', flat=True))
                    i['department'] = department
                    status = list(DeptAchApproval.objects.filter(approval_id=i['id'], approval_category='GUEST LECTURE', level=1).exclude(status="DELETE").values_list('approval_status', flat=True))
                    if len(status) > 0:
                        i['approval_status'] = status[0]

                return functions.RESPONSE(all_data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body.decode("utf-8"))
            check = Nonecheck(data)
            if(check == True):
                date = data['date']
                topic = data['topic']
                speaker = data['speaker']
                designation = data['designation']
                organization = data['organization']
                speaker_profile = data['speaker_profile']
                contact_number = data['contact_number']
                e_mail = data['e_mail']
                participants_no = data['participants_no']
                remark = data['remark']
                dept = data['dept']
                year = data['year']
            if(check == False):
                data = statusMessages.CUSTOM_MESSAGE("Mandatory Fields can't be empty")
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            date = datetime.datetime.strptime(str(data['date']).split('T')[0], "%Y-%m-%d").date()

            if 'id' in data:
                id = data['id']
                guestLectures.objects.filter(id=id).update(status="DELETE")
                DeptAchApproval.objects.filter(approval_id=id, approval_category='GUEST LECTURE').update(status="DELETE")

            q1 = guestLectures.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), remark=remark, participants_no=participants_no, e_mail=e_mail, contact_number=contact_number, speaker_profile=speaker_profile, organization=organization, date=date, topic=topic, speaker=speaker, designation=designation)
            q2 = DeptAchApproval.objects.create(level=1, approval_category="GUEST LECTURE", approval_id=q1.id)

            for i in year:
                q3 = AarMultiselect.objects.create(emp_id=emp_id, sno=q1.id, type="GUEST LECTURE", field="YEAR", value=i)
            for j in dept:
                q4 = AarMultiselect.objects.create(emp_id=emp_id, sno=q1.id, type="GUEST LECTURE", field="DEPARTMENT", value=j)

            if 'id' in data:
                data = statusMessages.MESSAGE_UPDATE
            else:
                data = statusMessages.MESSAGE_INSERT

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            guestLectures.objects.filter(id=id).update(status="DELETE")
            DeptAchApproval.objects.filter(approval_id=id, approval_category='GUEST LECTURE').update(status="DELETE")
            data1 = statusMessages.MESSAGE_DELETE

            return functions.RESPONSE(data1, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def MouSignedFunction(request):

    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_EMPLOYEE]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'view_previous')):
                data = list(MouSigned.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('sno', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'date', 'organization', 'objective', 'valid_upto', 'contact_number', 'e_mail', 'intro', 'document', 'time_stamp', 'status').order_by('-time_stamp'))
                for d in data:
                    qry = list(DeptAchApproval.objects.filter(approval_id=d['sno'], approval_category='MOU SIGNED', level=1).exclude(status="DELETE").values('approval_status'))
                    if len(qry) > 0:
                        d['approval_status'] = qry[0]['approval_status']
                    else:
                        d['approval_status'] = '---'
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            print(data, 'data')
            if 'sno' in data:
                sno = data['sno']
            else:
                sno = None
            date = str(data['date']).split('T')[0]
            organization = data['organization']
            objective = data['objective']
            valid_upto = str(data['valid_upto']).split('T')[0]
            contact_number = data['contact_number']
            e_mail = data['e_mail']
            intro = data['intro']
            document = data['document']
            ################################################

            ############## FOR UPDATE ######################
            if sno != None:
                MouSigned.objects.filter(sno=sno).update(status="DELETE")
                DeptAchApproval.objects.filter(approval_id=sno, approval_category='MOU SIGNED').update(status="DELETE")

                data_values = statusMessages.MESSAGE_UPDATE
            else:
                data_values = statusMessages.MESSAGE_INSERT

            ################################################
            mandatory_fields = ['date', 'organization', 'objective', 'valid_upto', 'contact_number', 'e_mail', 'intro', 'document']
            ############## FOR MANDATORY FIELDS AND CHECKS ############
            for m in mandatory_fields:
                for k, v in data.items():
                    if k == m and (v == None or v == ""):
                        data_values1 = statusMessages.CUSTOM_MESSAGE('Enter the value of ' + k)
                        data_values2 = k
                        data_values = [data_values1, data_values2]
                        return {'data': data_values, 'status': statusCodes.STATUS_CONFLICT_WITH_MESSAGE}
            ###########################################################
            MouSigned.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), date=date, organization=organization, objective=objective, valid_upto=valid_upto, contact_number=contact_number, e_mail=e_mail, intro=intro, document=document)
            mou_signed_id = list(MouSigned.objects.filter(emp_id=emp_id, date=date, organization=organization, objective=objective, valid_upto=valid_upto, contact_number=contact_number, e_mail=e_mail, intro=intro, document=document).exclude(status="DELETE").values_list('sno', flat=True))
            if len(mou_signed_id) > 0:
                approval = RequestForApproval('MOU SIGNED', mou_signed_id[0])
            return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            sno = data['sno']
            MouSigned.objects.filter(sno=sno).exclude(status="DELETE").update(status="DELETE")
            DeptAchApproval.objects.filter(approval_id=sno, approval_category='MOU SIGNED').exclude(status="DELETE").update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def IndustrialVisit(request):
    emp_id_hod = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.POST_REQUEST(request):
            received_data = json.loads(request.body)
            check = Nonecheck(received_data)
            if(check == True):
                print("dkdkwjfhtgeritherjghhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
                date = received_data['date']
                industry = received_data['industry']
                address = received_data['address']
                contact_person = received_data['contact_person']
                contact_number = received_data['contact_number']
                email = received_data['email']
                participants_no = received_data['no_of_participants']
                remark = received_data['remark']
                emp_id_faculty = received_data['emp_id']
                year = received_data['year']

                if 'id' in received_data:
                    old_id = received_data['id']
                    delete_old_visit = industrialVisit.objects.filter(id=old_id).update(status="DELETE")
                    delete_approve = DeptAchApproval.objects.filter(approval_id=old_id, approval_category="INDUSTRIAL VISIT").update(status="DELETE")
                date_string = date.split('T')
                date1 = datetime.datetime.strptime(date_string[0], "%Y-%m-%d")
                date = date1.date()
                insert_new = industrialVisit.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id_hod), date=date, industry=industry, address=address, contact_person=contact_person, contact_number=contact_number, e_mail=email, participants_no=participants_no, remark=remark)

                if insert_new:
                    for x in year:
                        multi_insert_year = AarMultiselect.objects.create(sno=insert_new.id, emp_id=emp_id_hod, type="INDUSTRIAL VISIT", field="YEAR", value=x)
                    for y in emp_id_faculty:
                        multi_insert_faculty = AarMultiselect.objects.create(sno=insert_new.id, emp_id=emp_id_hod, type="INDUSTRIAL VISIT", field="FACULTY COORDINATOR", value=y)
                    approve = DeptAchApproval.objects.create(approval_category="INDUSTRIAL VISIT", approval_id=insert_new.id, level=1)

                if 'id' in received_data:
                    return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_SUCCESS)
                else:
                    return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)
            elif(check == False):
                data = statusMessages.CUSTOM_MESSAGE("Mandatory Fields can't be empty")
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        elif requestMethod.DELETE_REQUEST(request):
            received_data = json.loads(request.body)
            delete_visit = industrialVisit.objects.filter(id=received_data['id']).update(status="DELETE")
            delete_approve = DeptAchApproval.objects.filter(approval_id=received_data['id'], approval_category="INDUSTRIAL VISIT").update(status="DELETE")
            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'refresh')):
                coordinators = []
                dept_id = EmployeePrimdetail.objects.filter(emp_id=emp_id_hod).exclude(emp_status='SEPERATE').values('dept')
                if len(dept_id) > 0:
                    coordinators = list(EmployeePrimdetail.objects.filter(dept=dept_id[0]['dept']).exclude(emp_status='SEPERATE').exclude(emp_id=emp_id_hod).values('emp_id', 'name'))
                year = Year()
                data = []
                res = {
                    "faculty_details": list(coordinators),
                    "year_list": list(year)
                }
                data.append(res)
                return functions.RESPONSE(res, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'previous')):
                dept_id = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id_hod)).exclude(emp_status='SEPERATE').values('dept')
                all_data = list(industrialVisit.objects.filter(emp_id__dept=dept_id[0]['dept']).exclude(status="DELETE").values('date', 'industry', 'address', 'contact_person', 'contact_number', 'e_mail', 'participants_no', 'remark', 'id').order_by('time_stamp'))
                length = len(all_data)
                for x in range(length):
                    all_data[x].update({"faculty_details": []})
                    all_data[x].update({"year": []})
                    all_data[x].update({"status": {}})
                    multi_faculty = list(AarMultiselect.objects.filter(sno=all_data[x]['id'], emp_id=emp_id_hod, type="INDUSTRIAL VISIT", field="FACULTY COORDINATOR").values_list('value', flat=True))
                    name_of_faculty = list(EmployeePrimdetail.objects.filter(emp_id__in=multi_faculty).values('emp_id', 'name'))
                    multi_year = list(AarMultiselect.objects.filter(sno=all_data[x]['id'], emp_id=emp_id_hod, type="INDUSTRIAL VISIT", field="YEAR").values_list('value', flat=True))
                    year = [(int(y)) for y in multi_year]
                    status = list(DeptAchApproval.objects.filter(approval_id=all_data[x]['id'], approval_category="INDUSTRIAL VISIT").exclude(status="DELETE").values('approval_status'))
                    if (len(status) > 0):
                        all_data[x]['status'] = status[0]['approval_status']

                    all_data[x]['faculty_details'].extend(name_of_faculty)
                    all_data[x]['year'].extend(year)

                return functions.RESPONSE(all_data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def StudentAchievement(request):
    emp_id_hod = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.POST_REQUEST(request):
            received_data = json.loads(request.body)
            check = Nonecheck(received_data)
            if(check == True):
                date = received_data['date']
                description = received_data['description']
                category = received_data['category']
                if 'id' in received_data:
                    old_id = received_data['id']
                    delete_old_visit = Achievement.objects.filter(sno=old_id).update(status="DELETE")
                    delete_approve = DeptAchApproval.objects.filter(approval_id=old_id, approval_category="STUDENT ACHIEVEMENT").update(status="DELETE")
                date_string = date.split('T')
                date1 = datetime.datetime.strptime(date_string[0], "%Y-%m-%d")
                date = date1.date()
                insert_new = Achievement.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id_hod), category=AarDropdown.objects.get(sno=category), description=description, type="STUDENT", date=date)
                approve = DeptAchApproval.objects.create(approval_category="STUDENT ACHIEVEMENT", approval_id=insert_new.sno, level=1)
                if 'id' in received_data:
                    return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_SUCCESS)
                else:
                    return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)
            elif(check == False):
                data = statusMessages.CUSTOM_MESSAGE("Mandatory Fields can't be empty")
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'refresh')):
                response = Dropdown("STUDENTS ACHIEVEMENT")
                return functions.RESPONSE(list(response), statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'previous')):
                all_data = list(Achievement.objects.filter(emp_id=emp_id_hod, type="STUDENT").exclude(status="DELETE").values('sno', 'category__value', 'description', 'date', 'category').order_by('time_stamp'))
                length = len(all_data)
                for x in range(length):
                    all_data[x].update({"status": {}})
                    status = list(DeptAchApproval.objects.filter(approval_id=all_data[x]['sno'], approval_category="STUDENT ACHIEVEMENT").exclude(status="DELETE").values('approval_status'))
                    if (len(status) > 0):
                        all_data[x]['status'] = status[0]['approval_status']
                return functions.RESPONSE(all_data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            received_data = json.loads(request.body)
            delete_visit = Achievement.objects.filter(sno=received_data['id']).update(status="DELETE")
            delete_approve = DeptAchApproval.objects.filter(approval_id=received_data['id'], approval_category="STUDENT ACHIEVEMENT").update(status="DELETE")

            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def DepartmentAchievement(request):
    session_id = request.session['Session_id']
    session_name = request.session['Session_name']
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'onload')):
                q1 = Dropdown('DEPARTMENTAL ACHIEVEMENT')
                all_data = {"Dropdown": list(q1)}

            elif(requestType.custom_request_type(request.GET, 'view_prev')):
                all_data = list(Achievement.objects.filter(emp_id=emp_id, type='DEPARTMENT').exclude(status="DELETE").values('sno', 'date', 'type', 'category', 'category__value', 'description', 'status', 'emp_id').order_by('time_stamp'))
                for i in all_data:
                    status = list(DeptAchApproval.objects.filter(approval_id=i['sno'], approval_category='DEPARTMENT ACHIEVEMENT', level=1).exclude(status="DELETE").values_list('approval_status', flat=True))
                    if len(status) > 0:
                        i['approval_status'] = status[0]

                    else:
                        i['approval_status']='---'

            return functions.RESPONSE(all_data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body.decode("utf-8"))
            check = Nonecheck(data)
            if(check == True):
                date = data['date']
                category = data['category']
                description = data['description']
            else:
                data = statusMessages.CUSTOM_MESSAGE("Mandatory Fields can't be empty")
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            date = datetime.datetime.strptime(str(data['date']).split('T')[0], "%Y-%m-%d").date()

            if 'id' in data:
                id = data['id']
                Achievement.objects.filter(sno=id).update(status="DELETE")
                DeptAchApproval.objects.filter(approval_id=id, approval_category='DEPARTMENT ACHIEVEMENT').update(status="DELETE")

            q1 = Achievement.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), date=date, category=AarDropdown.objects.get(sno=category), description=description, type='DEPARTMENT')
            q2 = DeptAchApproval.objects.create(level=1, approval_category="DEPARTMENT ACHIEVEMENT", approval_id=q1.sno)

            if 'id' in data:
                data = statusMessages.MESSAGE_UPDATE
            else:
                data = statusMessages.MESSAGE_INSERT

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            Achievement.objects.filter(sno=id).update(status="DELETE")
            DeptAchApproval.objects.filter(approval_id=id, approval_category='DEPARTMENT ACHIEVEMENT').update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def HobbyClub(request):
    session_id = request.session['Session_id']
    session_name = request.session['Session_name']
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'onload')):
                q1 = Hobby('HOBBY_CLUB')
                emp_id_hod = request.session['hash1']
                q2 = FactDrop(emp_id_hod)
                data = {"CLUBS": list(q1), "FACULTY": list(q2)}
                status = 200

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            if(requestType.custom_request_type(request.GET, 'view_prev')):
                all_data = list(Hobbyclub.objects.filter(emp_id=emp_id).exclude(status="DELETE").values('sno', 'emp_id', 'club_name__value', 'project_title', 'start_date', 'end_date', 'project_incharge__name', 'team_size', 'project_description', 'project_cost', 'project_outcome', 'status').order_by('time_stamp'))
                length = len(all_data)

                for i in range(length):
                    all_data[i].update({"project_coordinator": []})
                    coordinator = list(AarMultiselect.objects.filter(sno=all_data[i]['sno'], type='HOBBY_CLUB', field='PROJECT FACULTY COORDINATOR').values_list('value', flat=True))
                    name = list(EmployeePrimdetail.objects.filter(emp_id__in=coordinator).values('name', 'emp_id'))
                    all_data[i]['project_coordinator'].extend(name)
                    status = list(DeptAchApproval.objects.filter(approval_id=all_data[i]['sno'], approval_category='HOBBY_CLUB', level=1).exclude(status="DELETE").values_list('approval_status', flat=True))
                    if len(status) > 0:
                        all_data[i]['approval_status'] = status[0]

                return functions.RESPONSE(all_data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body.decode("utf-8"))
            print(data)
            check = Nonecheck(data)
            if(check == True):
                name = data['name']
                title = data['title']
                s_date = data['s_date']
                e_date = data['e_date']
                incharge = data['incharge']
                coordinator = data['coordinator']
                team = data['team']
                cost = data['cost']
                description = data['description']
                outcome = data['outcome']
            if(check == False):
                data = statusMessages.CUSTOM_MESSAGE("Mandatory Fields can't be empty")
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            s_date = datetime.datetime.strptime(str(data['s_date']).split('T')[0], "%Y-%m-%d").date()
            e_date = datetime.datetime.strptime(str(data['e_date']).split('T')[0], "%Y-%m-%d").date()

            if 'id' in data:
                id = data['id']
                Hobbyclub.objects.filter(sno=id).update(status="DELETE")
                DeptAchApproval.objects.filter(approval_id=id, approval_category='HOBBY_CLUB').update(status="DELETE")

            q1 = Hobbyclub.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), start_date=s_date, end_date=e_date, project_incharge=EmployeePrimdetail.objects.get(emp_id=incharge), team_size=team, project_description=description, project_cost=cost, project_outcome=outcome, project_title=title, club_name=AarDropdown.objects.get(sno=name))
            q2 = DeptAchApproval.objects.create(level=1, approval_category="HOBBY_CLUB", approval_id=q1.sno)

            for i in coordinator:
                q3 = AarMultiselect.objects.create(emp_id=emp_id, sno=q1.sno, type="HOBBY_CLUB", field="PROJECT FACULTY COORDINATOR", value=i)

            if 'id' in data:
                data = statusMessages.MESSAGE_UPDATE
            else:
                data = statusMessages.MESSAGE_INSERT
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']
            Hobbyclub.objects.filter(sno=id).update(status="DELETE")
            DeptAchApproval.objects.filter(approval_id=id, approval_category='HOBBY_CLUB').update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

def SummerWinter(request):

    emp_id_hod = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.POST_REQUEST(request):
            received_data = json.loads(request.body)
            check = Nonecheck(received_data)
            if(check == True):
                start_date = received_data['start_date']
                end_date = received_data['end_date']
                resource_person = received_data['resource_person']
                topic = received_data['topic']
                no_of_participants = received_data['no_of_participants']
                fee = received_data['fee']
                list_name = received_data['list_name']

                if 'id' in received_data:

                    old_id = received_data['id']
                    delete_old_visit = SummerWinterSchool.objects.filter(sno=old_id).update(status="DELETE")
                    delete_approve = DeptAchApproval.objects.filter(approval_id=old_id, approval_category="SUM_WIN_SCHOOL").update(status="DELETE")
                
                date_string = start_date.split('T')
                date1 = datetime.datetime.strptime(date_string[0], "%Y-%m-%d")
                start_date = date1.date()
                date_string1 = end_date.split('T')
                date2 = datetime.datetime.strptime(date_string1[0], "%Y-%m-%d")
                end_date = date2.date()
                try:
                    fee=float(fee)
                except:
                    fee=0.00

                insert_new = SummerWinterSchool.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id_hod), start_date=start_date, end_date=end_date, resource_person=resource_person, topic=topic, participant_number=no_of_participants, participant_fee=fee)
                if insert_new:
                    for x in list_name:
                        multi_insert = AarMultiselect.objects.create(sno=insert_new.sno, emp_id=emp_id_hod, type="SUM_WIN_SCHOOL", field="PARTICIPANT", value=x)

                    approve = DeptAchApproval.objects.create(approval_category="SUM_WIN_SCHOOL", approval_id=insert_new.sno, level=1)

                    if 'id' in received_data:
                        return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_SUCCESS)
                    else:
                        return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)
                else:
                    return functions.RESPONSE(statusMessages.MESSAGE_SERVICE_UNAVAILABLE, statusCodes.STATUS_SERVER_ERROR)
            elif(check == False):
                data = statusMessages.CUSTOM_MESSAGE("Mandatory Fields can't be empty")
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'refresh')):
                response = [{"value": "INTERNAL"}, {"value": "EXTERNAL"}]
                return functions.RESPONSE(response, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'INTERNAL')):
                dept_id = EmployeePrimdetail.objects.filter(emp_id=emp_id_hod).exclude(emp_status='SEPERATE').values('dept')
                coordinators = list(EmployeePrimdetail.objects.filter(dept=dept_id[0]['dept']).exclude(emp_status='SEPERATE').values('emp_id', 'name'))
                return functions.RESPONSE(coordinators, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                all_data = list(SummerWinterSchool.objects.filter(emp_id=emp_id_hod).exclude(status="DELETE").values('start_date', 'end_date', 'resource_person', 'topic', 'participant_number', 'participant_fee', 'sno').order_by('time_stamp'))
                length = len(all_data)
                for x in range(length):
                    all_data[x].update({"status": {}})
                    all_data[x].update({"name_list": []})

                    if all_data[x]['resource_person'] == "INTERNAL":
                        multi_faculty = list(AarMultiselect.objects.filter(sno=all_data[x]['sno'], emp_id=emp_id_hod, type="SUM_WIN_SCHOOL").values_list('value', flat=True))
                        name_of_faculty = list(EmployeePrimdetail.objects.filter(emp_id__in=multi_faculty).values('emp_id', 'name'))
                        all_data[x]['name_list'] = name_of_faculty
                    elif all_data[x]['resource_person'] == "EXTERNAL":
                        multi_external = list(AarMultiselect.objects.filter(sno=all_data[x]['sno'], emp_id=emp_id_hod, type="SUM_WIN_SCHOOL").values('value'))
                        for y in multi_external:
                            y['name'] = y.pop('value')
                            y.update({'emp_id': None})
                        all_data[x]['name_list'] = multi_external
                    status = list(DeptAchApproval.objects.filter(approval_id=all_data[x]['sno'], approval_category="SUM_WIN_SCHOOL").exclude(status="DELETE").values('approval_status'))
                    if (len(status) > 0):
                        all_data[x]['status'] = status[0]['approval_status']
                return functions.RESPONSE(all_data, statusCodes.STATUS_SUCCESS)

############################################# DELETE ##############################################

        elif requestMethod.DELETE_REQUEST(request):

            received_data = json.loads(request.body)

            delete_visit = SummerWinterSchool.objects.filter(sno=received_data['id']).update(status="DELETE")

            delete_approve = DeptAchApproval.objects.filter(approval_id=received_data['id'], approval_category="SUM_WIN_SCHOOL").update(status="DELETE")

            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

def Events_organised(request):
    emp_id_hod = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            check = Nonecheck(data)
            if(check == True):
                category=data['category']
                branch=data['discipline']
                type_value=data['type']
                sector=data['organization_sector']
                from_date=data['from_date']
                to_date=data['to_date']
                incorp_sector=data['incorp_sector']
                title=data['title']
                venue=data['venue']
                participants = data['participants']
                organizers= data['organizers']
                attended= data['attended']
                in_collab=data['in_collab']
                sponsor_type=data['sponsor']
                description=data['description']
                s_date = datetime.datetime.strptime(str(from_date).split('T')[0], "%Y-%m-%d").date()
                e_date = datetime.datetime.strptime(str(to_date).split('T')[0], "%Y-%m-%d").date()

                if 'id' in data:
                    old_id = data['id']
                    delete_old_event = eventsorganized.objects.filter(id=old_id).update(status="DELETE")
                    delete_approve = DeptAchApproval.objects.filter(approval_id=old_id, approval_category="EVENTS_ORGANISED").update(status="DELETE")
                if 'other' in data:
                    other_venue=data['other']
                    insert_new = eventsorganized.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id_hod),category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type_value),from_date=s_date,to_date=e_date,organization_sector=AarDropdown.objects.get(sno=sector),incorporation_status=AarDropdown.objects.get(sno=incorp_sector),title=title,venue=venue,participants=participants,organizers=organizers,attended=attended,collaboration=in_collab,sponsership=sponsor_type,description=description, status="INSERT",venue_other=other_venue)

                else:
                    insert_new = eventsorganized.objects.create(emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id_hod),category=AarDropdown.objects.get(sno=category),type=AarDropdown.objects.get(sno=type_value),from_date=s_date,to_date=e_date,organization_sector=AarDropdown.objects.get(sno=sector),incorporation_status=AarDropdown.objects.get(sno=incorp_sector),title=title,venue=venue,participants=participants,organizers=organizers,attended=attended,collaboration=in_collab,sponsership=sponsor_type,description=description, status="INSERT")

                if insert_new:
                    approve = DeptAchApproval.objects.create(approval_category="EVENTS_ORGANISED", approval_id=insert_new.id, level=1)

                    for x in branch:
                        discipline = AarMultiselect.objects.create(sno=insert_new.id,emp_id=emp_id_hod,type="EVENTS_ORGANIZED",field="DISCIPLINE",value=x)


                    if in_collab == "Yes":
                        length = len(data['collab_data'])
                        for x in range(0,length):
                            organisation = data['collab_data'][x]['organisation']
                            address = data['collab_data'][x]['address']
                            pin = data['collab_data'][x]['pincode']
                            contact_person = data['collab_data'][x]['contact_person']
                            contact_number = data['collab_data'][x]['contact_number']
                            email = data['collab_data'][x]['email']
                            website = data['collab_data'][x]['website']
                            amount = data['collab_data'][x]['amount']                        

                            insert_new_collab = AchFacCollaborators.objects.create(organisation=organisation, pin_code=pin, address=address, contact_person=contact_person, contact_number=contact_number, e_mail=email, website=website, amount=amount)
                            insert_new_map=AchFacMapIds.objects.create(key_type="COLLABORATORS", key_id=insert_new_collab.id, form_id=insert_new.id, form_type="EVENTS_ORGANISED")     

                    if sponsor_type == "Yes":
                        length = len(data['sponsor_data'])
                        for x in range(0,length):
                            organisation = data['sponsor_data'][x]['organisation']
                            address = data['sponsor_data'][x]['address']
                            pin = data['sponsor_data'][x]['pincode']
                            contact_person = data['sponsor_data'][x]['contact_person']
                            contact_number = data['sponsor_data'][x]['contact_number']
                            email = data['sponsor_data'][x]['email']
                            website = data['sponsor_data'][x]['website']
                            amount = data['sponsor_data'][x]['amount']                        

                            insert_new_spons = AchFacSponser.objects.create(organisation=organisation, pin_code=pin, address=address, contact_person=contact_person, contact_number=contact_number, e_mail=email, website=website, amount=amount)
                            insert_new_map=AchFacMapIds.objects.create(key_type="SPONSORS", key_id=insert_new_spons.id, form_id=insert_new.id, form_type="EVENTS_ORGANISED")
                    if 'id' in data:
                        return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_SUCCESS)
                    else:
                        return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)
                else:
                    return functions.RESPONSE(statusMessages.MESSAGE_SERVICE_UNAVAILABLE, statusCodes.STATUS_SERVER_ERROR)
            elif(check == False):
                data = statusMessages.CUSTOM_MESSAGE("Mandatory Fields can't be empty")
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                category = get_category_list()
                department_list= get_department()
                type_value = get_type_list()
                organization_sector = get_organisation()
                incorp_sector = get_incorp()
                venue = get_venue()
                in_collab = get_incollab_sponsor()
                sponsor = get_incollab_sponsor()                
                data={
                    "category":category,
                    "discipline":department_list,
                    "type":type_value,
                    "organization_sector":organization_sector,
                    "incorp_sector":incorp_sector,
                    "venue":venue,
                    "in_collab":in_collab,
                    "sponsor":sponsor
                }
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                all_data=list(eventsorganized.objects.filter(emp_id=emp_id_hod).exclude(status="DELETE").values('from_date','to_date','title','venue','venue_other','participants','organizers','attended','description','category','incorporation_status','organization_sector','type','collaboration','sponsership','id').order_by('time_stamp'))
                length = len(all_data)
                for x in range(0,length):
                    status = list(DeptAchApproval.objects.filter(approval_id=all_data[x]['id'], approval_category="EVENTS_ORGANISED").exclude(status="DELETE").values('approval_status'))
                    category=list(AarDropdown.objects.filter(sno=all_data[x]['category']).values('value','sno'))
                    incorporation_status=list(AarDropdown.objects.filter(sno=all_data[x]['incorporation_status']).values('value','sno'))
                    organization_sector=list(AarDropdown.objects.filter(sno=all_data[x]['organization_sector']).values('value','sno'))
                    type_list=list(AarDropdown.objects.filter(sno=all_data[x]['type']).values('value','sno'))
                    discipline = list(AarMultiselect.objects.filter(emp_id=emp_id_hod, type="EVENTS_ORGANIZED",field="DISCIPLINE", sno=all_data[x]['id']).values_list('value',flat=True))
                    discipline_int = [(int(y)) for y in discipline]
                    all_data[x]['discipline']=discipline_int
                    all_data[x]['category']=category
                    all_data[x]['incorp_sector']=incorporation_status
                    all_data[x]['organization_sector']=organization_sector
                    all_data[x]['type']=type_list

                    if (len(status) > 0):
                        all_data[x]['approval_status'] = status[0]['approval_status']
                    else:
                        all_data[x]['approval_status']="---"

                    all_data[x].update({"collab_data": []})
                    if all_data[x]['collaboration']=="Yes":
                        mapping_collab=AchFacMapIds.objects.filter(key_type="COLLABORATORS", form_id=all_data[x]['id'], form_type="EVENTS_ORGANISED").values_list('key_id',flat=True)
                        extract_collab=list(AchFacCollaborators.objects.filter(id__in=mapping_collab).exclude(status="DELETE").values('organisation','pin_code','address','contact_person','contact_number','e_mail','website','amount'))
                        all_data[x]['collab_data']=extract_collab
                    else:
                        all_data[x]['collab_data']=[]

                    all_data[x].update({"sponsor_data": []})
                    if all_data[x]['sponsership']=="Yes":                        
                        mapping_spons=AchFacMapIds.objects.filter(key_type="SPONSORS", form_id=all_data[x]['id'], form_type="EVENTS_ORGANISED").values_list('key_id',flat=True)
                        extract_spons=list(AchFacSponser.objects.filter(id__in=mapping_spons).exclude(status="DELETE").values('organisation','pin_code','address','contact_person','contact_number','e_mail','website','amount'))
                        all_data[x]['sponsor_data']=extract_spons
                    else:
                        all_data[x]['sponsor_data']=[]
                return functions.RESPONSE(all_data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            received_data = json.loads(request.body)
            delete_event = eventsorganized.objects.filter(id=received_data['id']).update(status="DELETE")
            delete_approve = DeptAchApproval.objects.filter(approval_id=received_data['id'], approval_category="EVENTS_ORGANISED").update(status="DELETE")
            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
