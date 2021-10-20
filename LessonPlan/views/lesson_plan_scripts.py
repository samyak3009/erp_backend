from django.shortcuts import render
from erp.constants_variables import *
from erp.constants_functions import functions, requestMethod
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
from datetime import date
import datetime
import copy
import json

from StudentMMS.constants_functions import requestType

from LessonPlan.models import *
from StudentAcademics.models import *

from login.views import checkpermission, generate_session_table_name
from StudentAcademics.views import get_student_subjects, StudentAcademicsDropdown, check_islocked
from LessonPlan.views.lesson_plan_functions import *


def completed_lesson_plan_hod_approval(request):

    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        data = []
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        LessonPropose = generate_session_table_name("LessonPropose_", session_name)
        LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)
        # LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        LessonCompletedTopic = generate_session_table_name("LessonCompletedTopic_", session_name)
        LessonProposeBTLevel = generate_session_table_name("LessonProposeBTLevel_", session_name)
        LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name
                                                            )
        LessonCompletedRemark = generate_session_table_name("LessonCompletedRemark_", session_name
                                                            )
        LessonCompletedApproval = generate_session_table_name("LessonCompletedApproval_", session_name)
        LessonProposeTopics = generate_session_table_name("LessonProposeTopics_", session_name)
        SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
        if requestMethod.GET_REQUEST(request):
            ##################################get pending data for approval########################################################
            if(requestType.custom_request_type(request.GET, 'get_data')):
                sem_name = request.GET['sem_name']
                isgroup = request.GET['isgroup']
                emp_id = request.GET['added_by'].split(',')
                sem_id = request.GET['sem_id']
                data_values = []
                data1 = []
                session_id = request.session['Session_id']
                if isgroup == 'N':
                    sec_group_data = request.GET['section'].split(',')
                else:
                    sec_group_data = request.GET['group_id'].split(',')

                data_values = []
                for sec_group in sec_group_data:
                    if isgroup == 'N':
                        section = sec_group
                        extra_filter1 = {'section': section}
                        extra_filter2 = {'completed_detail__lecture_details__section': section}
                        extra_filter3 = {'lecture_details__section': section}
                        extra_filter4 = {'propose_detail__lesson_propose__section': section}
                        sec_group_name = Sections.objects.filter(section_id=sec_group).values_list('section', flat=True)

                    else:
                        group_id = sec_group
                        extra_filter1 = {'group_id': group_id}
                        extra_filter2 = {'completed_detail__lecture_details__group_id': group_id}
                        extra_filter3 = {'lecture_details__group_id': group_id}
                        extra_filter4 = {'propose_detail__lesson_propose__group_id': group_id}
                        sec_group_name = SectionGroupDetails.objects.filter(id=sec_group).values_list('group_name', flat=True)

                    sub_details = list(LessonPropose.objects.filter(status="INSERT").filter(**extra_filter1).values('subject', 'subject__sub_name').distinct())
                    for subject_id in sub_details:
                        q_sub_type = list(SubjectInfo.objects.filter(id=subject_id['subject']).values('subject_type', 'sub_alpha_code', 'sub_num_code', 'subject_type__value'))
                        subject_type = q_sub_type[0]['subject_type']
                        ct_date = get_ct_date(sem_id, session_name, session_id, subject_type)
                        print("ct_date", ct_date)
                        for added_by in emp_id:
                            data_x = get_emp_propose_vs_actual_data_new(added_by, subject_id['subject'], session_id, ct_date, extra_filter1, extra_filter2, extra_filter3, extra_filter4, session_name)
                            added_by_name = list(EmployeePrimdetail.objects.filter(emp_id=added_by).values('name'))
                            if len(data_x) > 0:
                                if isgroup == 'N':
                                    data_values.append({"faculty": added_by_name[0]['name'] + " ( " + added_by + " ) ", "data": data_x, "section": sec_group_name[0], "sem_name": sem_name, "subject": subject_id['subject__sub_name'] + " (" + q_sub_type[0]['sub_alpha_code'] + "-" + q_sub_type[0]['sub_num_code'] + ")", "subject_type": q_sub_type[0]['subject_type__value'], "section_group_id": sec_group, "subject_id": subject_id['subject'], "emp_id": added_by})
                                else:
                                    data_values.append({"faculty": added_by_name[0]['name'] + " ( " + added_by + " ) ", "data": data_x, "group": sec_group_name[0], "sem_name": sem_name, "subject": subject_id['subject__sub_name'] + " (" + q_sub_type[0]['sub_alpha_code'] + "-" + q_sub_type[0]['sub_num_code'] + ")", "subject_type": q_sub_type[0]['subject_type__value'], "section_group_id": sec_group, "subject_id": subject_id['subject'], "emp_id": added_by})
                # print(data_values)
                return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'get_data_faculty')):

                sem_name = request.GET['sem_name']
                isgroup = request.GET['isgroup']
                added_by = request.session['hash1']
                sem_id = request.GET['sem_id']
                subject_id = request.GET['subject_id']
                f_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
                from_date = f_date[0]['sem_start']
                to_date = str(datetime.datetime.now()).split(" ")[0]
                data_values = []
                data1 = []
                session_id = request.session['Session_id']
                if isgroup == 'N':
                    sec_group_data = request.GET['section'].split(',')
                else:
                    sec_group_data = request.GET['group_id'].split(',')

                final_data = []
                # print("sec_group_data",sec_group_data)
                for sec_group in sec_group_data:
                    data_values = []
                    if isgroup == 'N':
                        section = sec_group
                        extra_filter1 = {'section': section}
                        extra_filter2 = {'completed_detail__lecture_details__section': section}
                        extra_filter3 = {'lecture_details__section': section}
                        extra_filter4 = {'propose_detail__lesson_propose__section': section}
                        sec_group_name = Sections.objects.filter(section_id=sec_group).values_list('section', flat=True)

                    else:
                        group_id = sec_group
                        extra_filter1 = {'group_id': group_id}
                        extra_filter2 = {'completed_detail__lecture_details__group_id': group_id}
                        extra_filter3 = {'lecture_details__group_id': group_id}
                        extra_filter4 = {'propose_detail__lesson_propose__group_id': group_id}
                        sec_group_name = SectionGroupDetails.objects.filter(id=sec_group).values_list('group_name', flat=True)

                    q_sub_type = list(SubjectInfo.objects.filter(id=subject_id).values('subject_type', 'sub_alpha_code', 'sub_num_code', 'subject_type__value'))
                    subject_type = q_sub_type[0]['subject_type']
                    # ct_date = get_ct_date_update(sem_id,session_name,session_id,subject_type,from_date,to_date)
                    # print(ct_date)
                    date_range = [{'from_date': from_date, 'to_date': to_date, 'exam_id__value': "Overall"}]
                    added_by_name = list(EmployeePrimdetail.objects.filter(emp_id=added_by).values('name'))
                    data_x = get_emp_propose_vs_actual_data_new(added_by, subject_id, session_id, date_range, extra_filter1, extra_filter2, extra_filter3, extra_filter4, session_name)

                    # coverage_data=get_emp_propose_vs_actual_data_report(added_by,subject_id,session_id,date_range,extra_filter1,extra_filter2,extra_filter3,extra_filter4,session_name)
                    if len(data_x) > 0:
                        if isgroup == 'N':
                            data_values.append({"faculty": added_by_name[0]['name'] + " ( " + request.session['hash1'] + " ) ", "data": data_x, "section": sec_group_name[0], "sem_name": sem_name, "subject": subject_id + " (" + q_sub_type[0]['sub_alpha_code'] + "-" + q_sub_type[0]['sub_num_code'] + ")", "subject_type": q_sub_type[0]['subject_type__value'], "emp_id": request.session['hash1']})
                        else:
                            data_values.append({"faculty": added_by_name[0]['name'] + " ( " + request.session['hash1'] + " ) ", "data": data_x, "group": sec_group_name[0], "sem_name": sem_name, "subject": subject_id + " (" + q_sub_type[0]['sub_alpha_code'] + "-" + q_sub_type[0]['sub_num_code'] + ")", "subject_type": q_sub_type[0]['subject_type__value'], "emp_id": request.session['hash1']})
                    # final_data.append({'data':data_values,'coverage_data':coverage_data})
                return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

        ##############################################submit approval_status for lesson plan with remarks(if any)#################
        elif requestMethod.POST_REQUEST(request):
            received_data = json.loads(request.body)
            date = datetime.date.today()
            # if check_islocked('LP1', qry_sections, session_name):
            #     return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)
            li = []
            for x in received_data:
                subject_id = x['subject_id']
                lecture_tutorial = x['lecture_tutorial']
                if x['isgroup'] == "N":
                    extra_filter1 = {'section': x['section']}
                else:
                    extra_filter1 = {'group_id': x['group_id']}
                emp_id = x['emp_id']
                remark = x['remark']
                lno = x['lno']
                for l in lno:
                    li.append({'completed_detail': LessonCompletedDetail.objects.get(id=l['completed_detail__id']), 'approved_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), 'approval_date': date})
                    # if x['remark'] is not None:
                    # li[-1]['remark'] = x['remark']
                    qry = LessonCompletedDetail.objects.filter(id=l['completed_detail__id']).update(approval_status=l['approval_status'])
                    q_create = LessonCompletedApproval.objects.filter(completed_detail=l['completed_detail__id']).update(status="DELETE")
                q_lesson_propose = list(LessonPropose.objects.filter(subject=subject_id, lecture_tutorial=lecture_tutorial, added_by=emp_id).filter(**extra_filter1).exclude(status="DELETE").values('id'))
                q_lesson_remark = LessonCompletedRemark.objects.filter(propose_detail=q_lesson_propose[0]['id']).update(status="DELETE")
                if remark is not None:
                    q_lesson_remark = LessonCompletedRemark.objects.create(propose_detail=LessonPropose.objects.get(id=q_lesson_propose[0]['id']), remark=remark)

            for l in li:
                q_create = LessonCompletedApproval.objects.create(**l)
            return functions.RESPONSE(statusMessages.MESSAGE_SUCCESS, statusCodes.STATUS_SUCCESS)

        ########################################################################################################################

        ##############################################update topics and unit by teacher#######################################
        elif requestMethod.PUT_REQUEST(request):
            received_data = json.loads(request.body)
            # if check_islocked('LP2', qry_sections, session_name):
            #     return JsonResponse(data={'msg': 'Portal is Locked, please contact Dean Academics office to unlock the portal.'}, status=202)
            for data in received_data:
                check = LessonCompletedTopic.objects.filter(completed_detail=data['completed_detail_id']).exclude(status="DELETE").exclude(completed_detail__lecture_details__status="DELETE").values('completed_detail__lecture_details__group_id', 'completed_detail__lecture_details__group_id__group_type', 'completed_detail__lecture_details__section', 'completed_detail__lecture_details__subject_id', 'completed_detail__lecture_details__isgroup', 'completed_detail__lecture_details__group_id', 'completed_detail__lecture_details__emp_id', 'completed_detail__lecture_details__lecture', 'completed_detail__lecture_details__date')
                if check:
                    if 'INTER' in check[0]['completed_detail__lecture_details__group_id__group_type']:
                        get_data = list(LessonCompletedTopic.objects.filter(completed_detail__lecture_details__isgroup=check[0]['completed_detail__lecture_details__isgroup'], completed_detail__lecture_details__subject_id=check[0]['completed_detail__lecture_details__subject_id'], completed_detail__lecture_details__emp_id=check[0]['completed_detail__lecture_details__emp_id'], completed_detail__lecture_details__group_id=check[0]['completed_detail__lecture_details__group_id'], completed_detail__lecture_details__lecture=check[0]['completed_detail__lecture_details__lecture'], completed_detail__lecture_details__date=check[0]['completed_detail__lecture_details__date']).exclude(status="DELETE").exclude(completed_detail__lecture_details__status="DELETE").values_list('completed_detail', flat=True))
                        print(get_data, 'get_data')
                        qry = LessonCompletedTopic.objects.filter(completed_detail__in=get_data).exclude(status="DELETE").update(status="DELETE")
                        objs = (LessonCompletedTopic(completed_topic=LessonTopicDetail.objects.get(id=x), completed_detail=LessonCompletedDetail.objects.get(id=inter_id)) for x in data['topic'] for inter_id in get_data)
                        bulk_query = LessonCompletedTopic.objects.bulk_create(objs)
                    else:
                        qry = LessonCompletedTopic.objects.filter(completed_detail=data['completed_detail_id']).exclude(status="DELETE").update(status="DELETE")
                        objs = (LessonCompletedTopic(completed_topic=LessonTopicDetail.objects.get(id=x), completed_detail=LessonCompletedDetail.objects.get(id=data['completed_detail_id'])) for x in data['topic'])
                        bulk_query = LessonCompletedTopic.objects.bulk_create(objs)
            return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
        ################################################################################################################


def lesson_plan_lnowise_report(request):

    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        data = []
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        LessonPropose = generate_session_table_name("LessonPropose_", session_name)
        LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)
        # LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        LessonCompletedTopic = generate_session_table_name("LessonCompletedTopic_", session_name)
        LessonProposeBTLevel = generate_session_table_name("LessonProposeBTLevel_", session_name)
        LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name
                                                            )
        LessonProposeApproval = generate_session_table_name("LessonProposeApproval_", session_name)
        LessonProposeTopics = generate_session_table_name("LessonProposeTopics_", session_name)
        SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
        if requestMethod.GET_REQUEST(request):
            ##################################get pending data for approval########################################################
            if(requestType.custom_request_type(request.GET, 'get_data')):
                sem_name = request.GET['sem_name']
                isgroup = request.GET['isgroup']
                emp_id = request.GET['added_by'].split(',')
                sem_id = request.GET['sem_id']
                branch = request.GET['branch']
                from_date = request.GET['from_date']
                to_date = request.GET['to_date']
                data_values1 = {}
                data1 = []
                session_id = request.session['Session_id']
                if isgroup == 'N':
                    sec_group_data = request.GET['section'].split(',')
                else:
                    sec_group_data = request.GET['group_id'].split(',')
                # data_values1=[]
                data_values = []
                for sec_group in sec_group_data:
                    if isgroup == 'N':
                        section = sec_group
                        extra_filter1 = {'section': section}
                        extra_filter2 = {'completed_detail__lecture_details__section': section}
                        extra_filter3 = {'lecture_details__section': section}
                        extra_filter4 = {'propose_detail__lesson_propose__section': section}
                        sec_group_name = Sections.objects.filter(section_id=sec_group).values_list('section', flat=True)

                    else:
                        group_id = sec_group
                        extra_filter1 = {'group_id': group_id}
                        extra_filter2 = {'completed_detail__lecture_details__group_id': group_id}
                        extra_filter3 = {'lecture_details__group_id': group_id}
                        extra_filter4 = {'propose_detail__lesson_propose__group_id': group_id}
                        sec_group_name = SectionGroupDetails.objects.filter(id=sec_group).values_list('group_name', flat=True)

                    sub_details = list(LessonPropose.objects.filter(status="INSERT").filter(**extra_filter1).values('subject', 'subject__sub_name').distinct())

                    for subject_id in sub_details:
                        q_sub_type = list(SubjectInfo.objects.filter(id=subject_id['subject']).values('subject_type', 'sub_alpha_code', 'sub_num_code', 'subject_type__value'))
                        subject_type = q_sub_type[0]['subject_type']
                        ct_date = get_ct_date_update(sem_id, session_name, session_id, subject_type, from_date, to_date)
                        for added_by in emp_id:
                            data_x = get_emp_propose_vs_actual_data_report(added_by, subject_id['subject'], session_id, ct_date, extra_filter1, extra_filter2, extra_filter3, extra_filter4, session_name)
                            added_by_name = list(EmployeePrimdetail.objects.filter(emp_id=added_by).values('name', 'dept__value', 'desg__value'))
                            if len(data_x) > 0:
                                if isgroup == 'N':
                                    for d in data_x:
                                        d.update({"faculty": added_by_name[0]['name'] + " ( " + added_by + " ) ", "faculty_dept": added_by_name[0]['dept__value'], "designation": added_by_name[0]['desg__value'], "section": sec_group_name[0], "sem_name": sem_name, "subject": subject_id['subject__sub_name'] + " (" + q_sub_type[0]['sub_alpha_code'] + "-" + q_sub_type[0]['sub_num_code'] + ")", "subject_type": q_sub_type[0]['subject_type__value'], "emp_id": added_by, "branch": branch})
                                else:
                                    for d in data_x:
                                        d.update({"faculty": added_by_name[0]['name'] + " ( " + added_by + " ) ", "faculty_dept": added_by_name[0]['dept__value'], "designation": added_by_name[0]['desg__value'], "group": sec_group_name[0], "sem_name": sem_name, "subject": subject_id['subject__sub_name'] + " (" + q_sub_type[0]['sub_alpha_code'] + "-" + q_sub_type[0]['sub_num_code'] + ")", "subject_type": q_sub_type[0]['subject_type__value'], "emp_id": added_by, "branch": branch})
                            data_values.extend(data_x)
                ct_dropdown = []
                ct_no = 1
                for ct in ct_date:
                    ct_dropdown.append({'ct_name': ct['exam_id__value']})
                    ct_no += 1
                data_values1['data'] = data_values
                data_values1['keys'] = ct_dropdown
                return functions.RESPONSE([data_values1], statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            # if(requestType.custom_request_type(request.GET, 'get_data')):
            received_data = json.loads(request.body)
            print(received_data)
            sem_name = received_data['sem_name']
            isgroup = received_data['isgroup']
            # if request.GET['added_by']=='ALL':
            if 'added_by' in received_data:
                emp_id = received_data['added_by']
            else:
                emp_id = [request.session['hash1']]
            sem_id = received_data['sem_id']
            branch = received_data['branch']
            from_date = received_data['from_date']
            to_date = received_data['to_date']
            data_values1 = {}
            data1 = []
            session_id = request.session['Session_id']
            if isgroup == 'N':
                sec_group_data = received_data['section']
            else:
                sec_group_data = received_data['group_id']
            # data_values1=[]
            data_values = []
            ct_date_list = []
            for sec_group in sec_group_data:
                if isgroup == 'N':
                    section = sec_group
                    extra_filter1 = {'section': section}
                    extra_filter2 = {'completed_detail__lecture_details__section': section}
                    extra_filter3 = {'lecture_details__section': section}
                    extra_filter4 = {'propose_detail__lesson_propose__section': section}
                    sec_group_name = Sections.objects.filter(section_id=sec_group).values_list('section', flat=True)

                else:
                    group_id = sec_group
                    extra_filter1 = {'group_id': group_id}
                    extra_filter2 = {'completed_detail__lecture_details__group_id': group_id}
                    extra_filter3 = {'lecture_details__group_id': group_id}
                    extra_filter4 = {'propose_detail__lesson_propose__group_id': group_id}
                    sec_group_name = SectionGroupDetails.objects.filter(id=sec_group).values_list('group_name', flat=True)

                sub_details = list(LessonPropose.objects.filter(status="INSERT").filter(**extra_filter1).values('subject', 'subject__sub_name').distinct())

                for subject_id in sub_details:
                    q_sub_type = list(SubjectInfo.objects.filter(id=subject_id['subject']).values('subject_type', 'sub_alpha_code', 'sub_num_code', 'subject_type__value'))
                    subject_type = q_sub_type[0]['subject_type']
                    ct_date = get_ct_date_update(sem_id, session_name, session_id, subject_type, from_date, to_date)
                    ct_date_list.extend(ct_date)
                    for added_by in emp_id:
                        data_x = get_emp_propose_vs_actual_data_report(added_by, subject_id['subject'], session_id, ct_date, extra_filter1, extra_filter2, extra_filter3, extra_filter4, session_name)
                        added_by_name = list(EmployeePrimdetail.objects.filter(emp_id=added_by).values('name', 'dept__value', 'desg__value'))
                        if len(data_x) > 0:
                            if isgroup == 'N':
                                for d in data_x:
                                    d.update({"faculty": added_by_name[0]['name'] + " ( " + added_by + " ) ", "faculty_dept": added_by_name[0]['dept__value'], "designation": added_by_name[0]['desg__value'], "section": sec_group_name[0], "sem_name": sem_name, "subject": subject_id['subject__sub_name'] + " (" + q_sub_type[0]['sub_alpha_code'] + "-" + q_sub_type[0]['sub_num_code'] + ")", "subject_type": q_sub_type[0]['subject_type__value'], "emp_id": added_by, "branch": branch})
                            else:
                                for d in data_x:
                                    d.update({"faculty": added_by_name[0]['name'] + " ( " + added_by + " ) ", "faculty_dept": added_by_name[0]['dept__value'], "designation": added_by_name[0]['desg__value'], "group": sec_group_name[0], "sem_name": sem_name, "subject": subject_id['subject__sub_name'] + " (" + q_sub_type[0]['sub_alpha_code'] + "-" + q_sub_type[0]['sub_num_code'] + ")", "subject_type": q_sub_type[0]['subject_type__value'], "emp_id": added_by, "branch": branch})
                        data_values.extend(data_x)
            ct_dropdown = []
            ct_no = 1
            for ct in ct_date_list:
                ct_dropdown.append({'ct_name': ct['exam_id__value']})
                ct_no += 1
            data_values1['data'] = data_values
            data_values1['keys'] = ct_dropdown
            return functions.RESPONSE([data_values1], statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
