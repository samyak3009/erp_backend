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
from django.contrib.auth.models import User

from StudentMMS.constants_functions import *
from erp.constants_variables import *
from erp.constants_functions import functions, requestMethod

from login.models import AarDropdown, EmployeeDropdown
from musterroll.models import EmployeePrimdetail, EmployeeResearch, EmployeeAcademic, Reporting, AarReporting
from DeptAchievement.models import *
from Achievement.models import *

from login.views import checkpermission
from DeptAchievement.views.dept_ach_functions import *
from DeptAchievement.views.dept_ach_check_function import *


#'''import functions'''
# Create your views here.

def all_detail(dept_id, sno, from_date, to_date, emp_id_hod):

    if sno == "1":
        all_data = list(guestLectures.objects.filter(emp_id__dept__in=dept_id, date__range=(from_date, to_date)).exclude(status="DELETE").values('id', 'date', 'topic', 'speaker', 'speaker_profile', 'organization', 'designation', 'contact_number', 'e_mail', 'participants_no', 'remark').order_by('time_stamp'))
        print(all_data)

        for i in all_data:
            year = list(AarMultiselect.objects.filter(sno=i['id'], type='GUEST LECTURE', field='YEAR').values_list('value', flat=True))
            print(year)
            # Year1 = [(int(y)) for y in year]
            i['year'] = year
            dept_id = list(AarMultiselect.objects.filter(sno=i['id'], type='GUEST LECTURE', field='DEPARTMENT').values_list('value', flat=True))
            Dept = [(int(y)) for y in dept_id]
            i['dept_id'] = Dept
            department = list(EmployeeDropdown.objects.filter(sno__in=dept_id).values_list('value', flat=True))
            i['department'] = department
            status = list(DeptAchApproval.objects.filter(approval_id=i['id'], approval_category='GUEST LECTURE', level=1).exclude(status="DELETE").values_list('approval_status', flat=True))
            if len(status) > 0:
                i['approval_status'] = status[0]
            else:
                i['approval_status'] = '---'

        return all_data

    elif sno == "2":

        all_data = list(industrialVisit.objects.filter(emp_id__dept__in=dept_id, date__range=(from_date, to_date)).exclude(status="DELETE").values('date', 'industry', 'address', 'contact_person', 'contact_number', 'e_mail', 'participants_no', 'remark', 'id','emp_id__dept__value').order_by('time_stamp'))

        length = len(all_data)

        for x in range(length):

            all_data[x].update({"faculty_details": []})
            all_data[x].update({"year": []})
            all_data[x].update({"approval_status": {}})

            multi_faculty = list(AarMultiselect.objects.filter(sno=all_data[x]['id'], emp_id=emp_id_hod, type="INDUSTRIAL VISIT", field="FACULTY COORDINATOR").values_list('value', flat=True))
            print(multi_faculty, 'multi_faculty')
            name_of_faculty = list(EmployeePrimdetail.objects.filter(emp_id__in=multi_faculty).values('emp_id', 'name'))

            multi_year = list(AarMultiselect.objects.filter(sno=all_data[x]['id'], emp_id=emp_id_hod, type="INDUSTRIAL VISIT", field="YEAR").values_list('value', flat=True))

            # year = [(int(y)) for y in multi_year]

            status = list(DeptAchApproval.objects.filter(approval_id=all_data[x]['id'], approval_category="INDUSTRIAL VISIT").exclude(status="DELETE").values('approval_status'))

            if (len(status) > 0):
                all_data[x]['approval_status'] = status[0]['approval_status']
            else:
                all_data[x]['approval_status'] = '---'

            all_data[x]['faculty_details'].extend(name_of_faculty)
            all_data[x]['year'].extend(multi_year)

        return all_data

    elif sno == "3":

        data = list(MouSigned.objects.filter(emp_id__dept__in=dept_id,	date__range=(from_date, to_date)).exclude(status="DELETE").values('sno', 'emp_id', 'emp_id__name', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'date', 'organization', 'objective', 'valid_upto', 'contact_number', 'e_mail', 'intro', 'document', 'time_stamp').order_by('-time_stamp'))
        for d in data:
            qry = list(DeptAchApproval.objects.filter(approval_id=d['sno'], approval_category='MOU SIGNED', level=1).exclude(status="DELETE").values('approval_status'))
            if len(qry) > 0:
                d['approval_status'] = qry[0]['approval_status']
            else:
                d['approval_status'] = '---'

        return data

    elif sno == "4":
        all_data = list(eventsorganized.objects.filter(emp_id__dept__in=dept_id, from_date__range=(from_date, to_date)).exclude(status="DELETE").values('from_date', 'to_date', 'title', 'venue', 'participants', 'organizers', 'attended', 'description', 'category', 'incorporation_status', 'organization_sector', 'type', 'collaboration', 'sponsership', 'id','emp_id','emp_id__dept__value').order_by('time_stamp'))
        length = len(all_data)
        for x in range(0, length):
            status = list(DeptAchApproval.objects.filter(approval_id=all_data[x]['id'], approval_category="EVENTS_ORGANISED").exclude(status="DELETE").values('approval_status'))
            category = list(AarDropdown.objects.filter(sno=all_data[x]['category']).values('value', 'sno'))
            incorporation_status = list(AarDropdown.objects.filter(sno=all_data[x]['incorporation_status']).values('value', 'sno'))
            organization_sector = list(AarDropdown.objects.filter(sno=all_data[x]['organization_sector']).values('value', 'sno'))
            type_list = list(AarDropdown.objects.filter(sno=all_data[x]['type']).values('value', 'sno'))
            all_data[x]['category'] = category
            all_data[x]['incorporation_status'] = incorporation_status
            all_data[x]['organization_sector'] = organization_sector
            all_data[x]['type'] = type_list

            if (len(status) > 0):
                all_data[x]['approval_status'] = status[0]['approval_status']
            else:
                all_data[x]['approval_status'] = "---"

            all_data[x].update({"collab_data": []})

            if all_data[x]['collaboration'] == "Yes":
                mapping_collab = AchFacMapIds.objects.filter(key_type="COLLABORATORS", form_id=all_data[x]['id'], form_type="EVENTS_ORGANISED").values_list('key_id', flat=True)
                extract_collab = list(AchFacCollaborators.objects.filter(id__in=mapping_collab).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
                all_data[x]['collab_data'] = extract_collab
            else:
                all_data[x]['collab_data'] = []
            all_data[x].update({"sponsor_data": []})
            if all_data[x]['sponsership'] == "Yes":
                mapping_spons = AchFacMapIds.objects.filter(key_type="SPONSORS", form_id=all_data[x]['id'], form_type="EVENTS_ORGANISED").values_list('key_id', flat=True)
                extract_spons = list(AchFacSponser.objects.filter(id__in=mapping_spons).exclude(status="DELETE").values('organisation', 'pin_code', 'address', 'contact_person', 'contact_number', 'e_mail', 'website', 'amount'))
                all_data[x]['sponsor_data'] = extract_spons
            else:
                all_data[x]['sponsor_data'] = []

        return all_data

    elif sno == "5":
        all_data = list(Hobbyclub.objects.filter(emp_id__dept__in=dept_id, start_date__range=(from_date, to_date)).exclude(status="DELETE").values('sno', 'emp_id', 'emp_id__dept__value','club_name__value', 'project_title', 'start_date', 'end_date', 'project_incharge__name', 'team_size', 'project_description', 'project_cost', 'project_outcome').order_by('time_stamp'))
        length = len(all_data)

        for i in range(length):
            all_data[i].update({"project_coordinator": []})
            coordinator = list(AarMultiselect.objects.filter(sno=all_data[i]['sno'], type='HOBBY_CLUB', field='PROJECT FACULTY COORDINATOR').values_list('value', flat=True))
            name = list(EmployeePrimdetail.objects.filter(emp_id__in=coordinator).values('name', 'emp_id'))
            all_data[i]['project_coordinator'].extend(name)
            status = list(DeptAchApproval.objects.filter(approval_id=all_data[i]['sno'], approval_category='HOBBY_CLUB', level=1).exclude(status="DELETE").values_list('approval_status', flat=True))
            if len(status) > 0:
                all_data[i]['approval_status'] = status[0]
            else:
                all_data[i]['approval_status'] = '---'

        return all_data

    elif sno == "6":
        all_data = list(SummerWinterSchool.objects.filter(emp_id__dept__in=dept_id, start_date__range=(from_date, to_date)).exclude(status="DELETE").values('start_date', 'end_date', 'resource_person', 'topic', 'participant_number', 'participant_fee','emp_id__dept__value', 'sno').order_by('time_stamp'))
        length = len(all_data)
        for x in range(length):

            all_data[x].update({"approval_status": {}})
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
                all_data[x]['approval_status'] = status[0]['approval_status']
            else:
                all_data[x]['approval_status'] = '---'

        return all_data

    elif sno == "7":
        all_data = list(Achievement.objects.filter(emp_id__dept__in=dept_id, type="STUDENT", date__range=(from_date, to_date)).exclude(status="DELETE").values('sno','emp_id__dept__value', 'category__value', 'description', 'date', 'category').order_by('time_stamp'))
        length = len(all_data)
        for x in range(length):
            all_data[x].update({"approval_status": {}})
            status = list(DeptAchApproval.objects.filter(approval_id=all_data[x]['sno'], approval_category="STUDENT ACHIEVEMENT").exclude(status="DELETE").values('approval_status'))
            if (len(status) > 0):
                all_data[x]['approval_status'] = status[0]['approval_status']
            else:
                all_data[x]['approval_status'] = '---'

        return all_data

    elif sno == "8":
        all_data = list(Achievement.objects.filter(emp_id__dept__in=dept_id, type='DEPARTMENT', date__range=(from_date, to_date)).exclude(status="DELETE").values('sno', 'date', 'type', 'category','emp_id__dept__value', 'category__value', 'description', 'emp_id').order_by('time_stamp'))
        for i in all_data:
            status = list(DeptAchApproval.objects.filter(approval_id=i['sno'], approval_category='DEPARTMENT ACHIEVEMENT', level=1).exclude(status="DELETE").values_list('approval_status', flat=True))
            if len(status) > 0:
                i['approval_status'] = status[0]
            else:
                i['approval_status'] = '---'
        return all_data


def Department_Achievement_Report(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'data')):

                sno = request.GET['sno']
                f_date = request.GET['from_date'].split('T')[0]
                t_date = request.GET['to_date'].split('T')[0]
                if 'department' in request.GET:
                    dept_id = request.GET['department'].split(",")
                    data = all_detail(dept_id, sno, f_date, t_date, emp_id)
                    return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

                dept_id = list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values_list('dept_id', flat=True))
                print(dept_id)
                data = all_detail(dept_id, sno, f_date, t_date, emp_id)

            elif(requestType.custom_request_type(request.GET, 'hod')):
                data = get_achievements_list()

            elif(requestType.custom_request_type(request.GET, 'dean')):
                data = [{"category": []}, {"department": []}]
                data[0]['category'] = get_achievements_list()
                data[1]['department'].extend(get_department())

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
