from django.shortcuts import render
from erp.constants_variables import *
from erp.constants_functions import functions, requestMethod
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
import datetime
import copy
import json

from StudentMMS.constants_functions import requestType

from LessonPlan.models import *
from StudentAcademics.models import *

from StudentAcademics.views import get_student_subjects, StudentAcademicsDropdown
from login.views import checkpermission, generate_session_table_name

###############################################lesson plan propose by faculty#####################################################
def propose_lesson_plan(request):
    session_id = request.session['Session_id']
    session_name = request.session['Session_name']
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        session_name = request.session['Session_name']
        LessonPropose = generate_session_table_name("LessonPropose_", session_name)
        LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)
        LessonProposeDetail = generate_session_table_name("LessonProposeDetail_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        LessonProposeTopics = generate_session_table_name("LessonProposeTopics_", session_name)
        LessonProposeBTLevel = generate_session_table_name("LessonProposeBTLevel_", session_name)
        LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name)
        LessonProposeApproval = generate_session_table_name("LessonProposeApproval_", session_name)
        StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
        SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)

        ##################################################create lesson plan from received data##################################
        if requestMethod.POST_REQUEST(request):
            received_data = json.loads(request.body)
            lecture_tutorial_data = received_data['data']
            lecture_tutorial = received_data['lecture_tutorial']
            isgroup = received_data['isgroup']
            queryid = []
            if isgroup == 'N':
                for x in received_data['section']:
                    query = list(LessonPropose.objects.filter(subject=received_data['subject'], section=x, lecture_tutorial=lecture_tutorial, session=request.session['Session_id'], status="INSERT", added_by=request.session['hash1']).values_list('id', flat=True))
                    if len(query) > 0:
                        queryid.append({"section": x, "id": query[0]})
                    else:
                        query_insert1 = LessonPropose.objects.create(subject=SubjectInfo.objects.get(id=received_data['subject']), section=Sections.objects.get(section_id=x), lecture_tutorial=lecture_tutorial, session=Semtiming.objects.get(uid=request.session['Session_id']), added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']))
                        queryid.append({"section": x, "id": query_insert1.id})
            else:
                query = list(LessonPropose.objects.filter(subject=received_data['subject'], group_id=received_data['group_id'], lecture_tutorial=lecture_tutorial, session=request.session['Session_id'], status="INSERT", added_by=request.session['hash1']).values_list('id', flat=True))
                if len(query) > 0:
                    queryid.append({"group_id": received_data['group_id'], "id": query[0]})
                else:
                    query_insert1 = LessonPropose.objects.create(subject=SubjectInfo.objects.get(id=received_data['subject']), group_id=SectionGroupDetails.objects.get(id=received_data['group_id']), lecture_tutorial=lecture_tutorial, session=Semtiming.objects.get(uid=request.session['Session_id']), added_by=EmployeePrimdetail.objects.get(emp_id=request.session['hash1']),isgroup="Y")
                    queryid.append({"group_id": received_data['group_id'], "id": query_insert1.id})


            dictionary = {}
            lno = []
            z = 0
            print(lecture_tutorial_data, "lecture_tutorial_data")
            for i in lecture_tutorial_data:
                key = i['unit_no']
                lno.append(i['lno'])
                if key not in dictionary:
                    dictionary[key] = set()
                for j in i['topic']:
                    if key in dictionary:
                        dictionary[key].add(j)
            for key in dictionary.keys():
                if len(dictionary[key]) > 0:
                    qry = list(LessonTopicDetail.objects.filter(unit=key, subject=received_data['subject'], topic_name__in=list(dictionary[key])).values_list('topic_name', flat=True).distinct())
                    if len(qry) > 0:
                        for pp in qry:
                            dictionary[key].discard(pp)
            for key in dictionary.keys():
                objs = (LessonTopicDetail(unit=key, subject=SubjectInfo.objects.get(id=received_data['subject']), topic_name=v)for v in dictionary[key])
                bulk_query = LessonTopicDetail.objects.bulk_create(objs)
            for qid in queryid:

                ##############################create extra filters for group or section###########################################
                if isgroup == 'N':
                    extra_filter1={'lesson_propose__section':qid['section']}
                    extra_filter2={'propose_detail__lesson_propose__section':qid['section']}
                else:
                    extra_filter1={'lesson_propose__group_id':qid['group_id']}
                    extra_filter2={'propose_detail__lesson_propose__group_id':qid['group_id']}
                ##################################################################################################################

                lesson_propose_detail = list(LessonProposeDetail.objects.filter(lesson_propose=qid['id'], added_by=request.session['hash1'], lesson_propose__lecture_tutorial=lecture_tutorial, lesson_propose__subject=received_data['subject'], ).filter(**extra_filter1).values_list('lno', flat=True))
                to_del = [item for item in lesson_propose_detail if item not in set(lno)]
                qry = LessonProposeDetail.objects.filter(lno__in=to_del, added_by=request.session['hash1'], lesson_propose__lecture_tutorial=lecture_tutorial, lesson_propose__subject=received_data['subject'], lesson_propose=qid['id']).filter(**extra_filter1).update(status="DELETE")

                for x in lecture_tutorial_data:
                    lecture_no = x['lno']
                    unit_no = x['unit_no']
                    query2 = LessonProposeDetail.objects.update_or_create(lesson_propose=qid['id'], lno=x['lno'], added_by=request.session['hash1'], status="INSERT", defaults={
                        'lesson_propose': LessonPropose.objects.get(id=qid['id']), 'lno': x['lno'], 'schedule_date': x['schedule_date'], 'added_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])})
                    print("query2", query2)
                    already_filled = set(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=qid['id'], propose_topic__subject=received_data['subject'], propose_detail__lno=x['lno'], propose_detail__lesson_propose__added_by=request.session['hash1'], propose_detail__lesson_propose__lecture_tutorial=lecture_tutorial).filter(**extra_filter2).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values_list('propose_topic__id', flat=True))

                    newly_filled = set(LessonTopicDetail.objects.filter(unit=x['unit_no'], subject=received_data['subject'], topic_name__in=x['topic']).values_list('id', flat=True))

                    to_delete = already_filled.difference(newly_filled)
                    to_create = newly_filled.difference(already_filled)

                    q_delete = LessonProposeTopics.objects.filter(propose_topic__id__in=to_delete, propose_detail__lesson_propose__added_by=request.session['hash1'], propose_detail__lno=x['lno']).filter(**extra_filter2).update(status="DELETE")
                    q_create_objs = (LessonProposeTopics(propose_detail=LessonProposeDetail.objects.get(id=query2[0].id), propose_topic=LessonTopicDetail.objects.get(id=zz)) for zz in to_create)
                    q_bulk_create = LessonProposeTopics.objects.bulk_create(q_create_objs)
                    bt_level_already_filled = LessonProposeBTLevel.objects.filter(propose_detail=query2[0].id).exclude(status="DELETE").update(status="DELETE")
                    bt_level_objs = (LessonProposeBTLevel(propose_detail=LessonProposeDetail.objects.get(id=query2[0].id), bt_level=StudentAcademicsDropdown.objects.get(sno=bt)) for bt in x['bt_level'])
                    bt_level_create = LessonProposeBTLevel.objects.bulk_create(bt_level_objs)
            return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)
            #######################################################################################################################


        #####################################view the data of lesson plan already created##########################################
        elif requestMethod.PUT_REQUEST(request):
            received_data = json.loads(request.body)
            if 'view' in received_data:
                emp_id = request.session['hash1']
                subject = received_data['subject']
                isgroup = received_data['isgroup']
                data_values = []
                session_id = request.session['Session_id']

                ##################create extra filters corresponding to section or group##########################################
                if isgroup == 'N':
                    section = received_data['section']
                    extra_filter1={'section':section}
                    extra_filter2={'propose_detail__lesson_propose__section':section}
                    extra_filter3={'lecture_details__section':section}
                else:
                    group_id = received_data['group_id']
                    extra_filter1={'group_id':group_id}
                    extra_filter2={'propose_detail__lesson_propose__group_id':group_id}
                    extra_filter3={'lecture_details__group_id':group_id}
                ##################################################################################################################

                query_lecture_tutorial = list(LessonPropose.objects.filter(subject=received_data['subject'],session=session_id, status="INSERT", added_by=request.session['hash1']).filter(**extra_filter1).values('lecture_tutorial', 'id'))
                data = []
                print(query_lecture_tutorial)
                for x in query_lecture_tutorial:
                    query = list(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=x['id'], propose_detail__lesson_propose__added_by=emp_id).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values('propose_detail__lno', 'propose_topic__unit', 'propose_detail__schedule_date', 'propose_detail__id').annotate(lno=F('propose_detail__lno'), unit_no=F('propose_topic__unit'), schedule_date=F('propose_detail__schedule_date')).distinct().order_by('propose_detail__lno'))
                    if len(query)>0:
                        print(query)
                        for q in query:
                            q['topic'] = []
                            q['bt_level'] = []
                            qry1 = LessonProposeTopics.objects.filter(propose_detail__lno=q['propose_detail__lno'], propose_topic__unit=q['propose_topic__unit'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_topic__subject=subject, propose_detail__lesson_propose__added_by=emp_id).filter(**extra_filter2).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").values_list('propose_topic__topic_name', flat=True)
                            print(qry1)
                            if qry1:
                                q['topic'].extend(qry1)

                            qry2 = LessonProposeBTLevel.objects.filter(propose_detail__id=q['propose_detail__id']).filter(**extra_filter2).exclude(status="DELETE").values_list('bt_level__value', flat=True)
                            if qry2:
                                q['bt_level'].extend(qry2)


                            qry3 = list(LessonCompletedDetail.objects.filter(lno=q['propose_detail__lno'], lecture_details__subject_id=received_data['subject'], lecture_details__emp_id=request.session['hash1'], lecture_tutorial=x['lecture_tutorial']).filter(**extra_filter3).exclude(status="DELETE").values('lecture_details'))
                            print(qry3)
                            #########if lecture has held then non editable####################################################
                            if len(qry3) > 0:
                                q['editable'] = "NO"
                            else:
                                q['editable'] = "YES"
                            ###################################################################################################

                            qry4 = LessonProposeApproval.objects.filter(propose_detail__lno=q['lno'], propose_detail__lesson_propose__subject=subject,propose_detail__lesson_propose__added_by=request.session['hash1'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial']).filter(**extra_filter2).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values('approval_status')
                            if len(qry4) > 0:
                                q['status'] = qry4[0]['approval_status']
                            else:
                                q['status'] = "PENDING"

                    if len(query)>0:
                        data.append({"data": query, "type": x['lecture_tutorial']})
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
                ##################################################################################################################

        ################################################delete lesson plan data lno wise#########################################
        elif requestMethod.DELETE_REQUEST(request):
            received_data = json.loads(request.body)
            emp_id = request.session['hash1']
            subject = received_data['subject']
            isgroup = received_data['isgroup']

            ##################create extra filters corresponding to section or group##########################################
            if isgroup == 'N':
                section = received_data['section']
                extra_filter2={'propose_detail__lesson_propose__section':section}
                extra_filter3={'lesson_propose__section':section}
            else:
                group_id = received_data['group_id']
                extra_filter1={'group_id':group_id}
                extra_filter2={'propose_detail__lesson_propose__group_id':group_id}
                extra_filter3={'lesson_propose__group_id':group_id}
            ###################################################################################################################

            lno = received_data['lno']
            qry1 = list(LessonProposeDetail.objects.filter(lno__in=lno, added_by=emp_id, lesson_propose__lecture_tutorial=received_data['lecture_tutorial'], lesson_propose__subject=subject).filter(**extra_filter3).values_list("id", flat=True))
            qry2 = LessonProposeDetail.objects.filter(id__in=qry1, added_by=emp_id, lesson_propose__lecture_tutorial=received_data['lecture_tutorial'], lesson_propose__subject=subject).filter(**extra_filter3).update(status="DELETE")
            qry3 = LessonProposeTopics.objects.filter(propose_detail__id__in=qry1, propose_detail__added_by=emp_id, propose_detail__lesson_propose__lecture_tutorial=received_data['lecture_tutorial'], propose_detail__lesson_propose__subject=subject).filter(**extra_filter2).update(status="DELETE")
            qry4 = LessonProposeBTLevel.objects.filter(propose_detail__id__in=qry1, propose_detail__added_by=emp_id, propose_detail__lesson_propose__lecture_tutorial=received_data['lecture_tutorial'], propose_detail__lesson_propose__subject=subject).filter(**extra_filter2).update(status="DELETE")
            qry5 = LessonProposeApproval.objects.filter(propose_detail__id__in=qry1, propose_detail__added_by=emp_id, propose_detail__lesson_propose__lecture_tutorial=received_data['lecture_tutorial'], propose_detail__lesson_propose__subject=subject).filter(**extra_filter2).update(status="DELETE")
            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)
            #####################################################################################################################

        ##############################################get dropdown of topics corresponding to unit###############################
        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_topic_dropdown')):
                subject_id = request.GET['subject_id']
                unit = request.GET['unit_no']
                data = []
                qry = list(LessonTopicDetail.objects.filter(unit=unit, subject=subject_id).exclude(status="DELETE").values_list('topic_name', flat=True))
                return functions.RESPONSE(qry, statusCodes.STATUS_SUCCESS)
        #######################################################################################################################
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)



###############################Lesson Plan Submitted by faculties to be approved or rejected by HOD##############################
def lesson_plan_hod_approval(request):

    if checkpermission(request, [rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        data = []
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        LessonPropose = generate_session_table_name("LessonPropose_", session_name)
        LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)
        LessonProposeDetail = generate_session_table_name("LessonProposeDetail_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        LessonProposeTopics = generate_session_table_name("LessonProposeTopics_", session_name)
        LessonProposeBTLevel = generate_session_table_name("LessonProposeBTLevel_", session_name)
        LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name
                                                            )
        LessonProposeApproval = generate_session_table_name("LessonProposeApproval_", session_name)
        if requestMethod.GET_REQUEST(request):
            ##################################Get all Pending Lesson Plans data#################################################
            if(requestType.custom_request_type(request.GET, 'get_data')):
                sem_name = request.GET['sem_name']
                isgroup = request.GET['isgroup']
                emp_id = request.session['hash1']
                subject = get_student_subjects(request.GET['sem'], session_name)

                ##############create extra filters corresponding to section or group##########################################
                if isgroup == 'N':
                    section = request.GET['section']
                    section_name = request.GET['section_name']
                    extra_filter1={'section':section}
                    extra_filter2={'propose_detail__lesson_propose__section':section}
                    extra_filter3={'lecture_details__section':section}
                else:
                    group_id = request.GET['group_id']
                    group_name = request.GET['group_name']
                    extra_filter1={'group_id':group_id}
                    extra_filter2={'propose_detail__lesson_propose__group_id':group_id}
                    extra_filter3={'lecture_details__group_id':group_id}
                ##############################################################################################################

                data_values = []
                data1 = []
                session_id = request.session['Session_id']
                for y in subject:
                    qry111 = list(LessonPropose.objects.filter(subject=y['id'], session=session_id, status="INSERT").filter(**extra_filter1).values('added_by__name', 'added_by', 'added_by__dept__value').distinct())
                    for qr in qry111:
                        query_lecture_tutorial = list(LessonPropose.objects.filter(subject=y['id'], session=session_id, status="INSERT", added_by=qr['added_by']).filter(**extra_filter1).values('lecture_tutorial', 'id', 'section__section'))
                        data = []
                        qry_approved = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=y['id'], propose_detail__lesson_propose__added_by=qr['added_by']).filter(**extra_filter2).exclude(status="DELETE").values_list('propose_detail__id', flat=True))
                        for x in query_lecture_tutorial:
                            query = list(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=x['id'], propose_detail__lesson_propose__added_by=qr['added_by'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_detail__lesson_propose__subject=y['id']).exclude(status="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_detail__in=qry_approved).values('propose_detail__lno', 'propose_topic__unit', 'propose_detail__schedule_date', 'propose_detail__id').annotate(lno=F('propose_detail__lno'), unit_no=F('propose_topic__unit'), schedule_date=F('propose_detail__schedule_date')).distinct().order_by('propose_detail__lno'))

                            print(query)
                            for q in query:
                                q['topic'] = []
                                q['bt_level'] = []

                                qry1 = LessonProposeTopics.objects.filter(propose_detail__lno=q['propose_detail__lno'], propose_topic__unit=q['propose_topic__unit'], propose_detail__lesson_propose__added_by=qr['added_by'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_detail__lesson_propose__subject=y['id']).filter(**extra_filter2).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").exclude(propose_detail__in=qry_approved).values_list('propose_topic__topic_name', flat=True)
                                if qry1:
                                    q['topic'].extend(qry1)

                                qry2 = LessonProposeBTLevel.objects.filter(propose_detail__id=q['propose_detail__id'], propose_detail__lesson_propose__added_by=qr['added_by']).filter(**extra_filter2).exclude(status="DELETE").values_list('bt_level__value', flat=True)
                                if qry2:
                                    q['bt_level'].extend(qry2)

                                q['status'] = "PENDING"

                            if len(query) > 0:
                                data.append({"data": query, "type": x['lecture_tutorial']})
                        if len(query_lecture_tutorial) > 0 and len(data) > 0:
                            if isgroup=='N':
                                data1.append({"data": data, "faculty": qr['added_by__name'], "subject": y['sub_name'], "subject_id": y['id'], "sem_name": sem_name, "section_name": section_name})
                            else:
                                data1.append({"data": data, "faculty": qr['added_by__name'], "subject": y['sub_name'], "subject_id": y['id'], "sem_name": sem_name, "group_name": group_name})
                return functions.RESPONSE(data1, statusCodes.STATUS_SUCCESS)

            #######################################get previously approved or rejected lesson plan###############################
            elif(requestType.custom_request_type(request.GET, 'get_view_previous_data')):
                sem_id=request.GET['sem']
                sem_name = request.GET['sem_name']
                emp_id = request.session['hash1']
                isgroup = request.GET['isgroup']
                subject = get_student_subjects(request.GET['sem'], session_name)
                data_values = []
                data1 = []
                session_id = request.session['Session_id']

                ##############create extra filters corresponding to section or group##########################################
                if isgroup == 'N':
                    section_name = request.GET['section_name']
                    section = request.GET['section']
                    extra_filter1={'section':section}
                    extra_filter2={'propose_detail__lesson_propose__section':section}
                    extra_filter3={'lecture_details__section':section}
                else:
                    group_id = request.GET['group_id']
                    group_name = request.GET['group_name']
                    extra_filter1={'group_id':group_id}
                    extra_filter2={'propose_detail__lesson_propose__group_id':group_id}
                    extra_filter3={'lecture_details__group_id':group_id}
                ##############################################################################################################

                for y in subject:
                    qry111 = list(LessonPropose.objects.filter(subject=y['id'], session=session_id, status="INSERT").filter(**extra_filter1).values('added_by__name', 'added_by', 'added_by__dept__value').distinct())
                    for qr in qry111:
                        query_lecture_tutorial = list(LessonPropose.objects.filter(subject=y['id'], session=session_id, status="INSERT", added_by=qr['added_by']).filter(**extra_filter1).values('lecture_tutorial', 'id'))
                        data = []
                        qry_approved = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=y['id'], propose_detail__lesson_propose__added_by=qr['added_by']).filter(**extra_filter2).exclude(status="DELETE").values('propose_detail__id', 'approval_status'))
                        approved_propose_detail=[]
                        for qry_app in qry_approved:
                            if qry_app['propose_detail__id'] not in approved_propose_detail:
                                approved_propose_detail.append(qry_app['propose_detail__id'])
                        print(query_lecture_tutorial)
                        for x in query_lecture_tutorial:
                            approved_rejected = []
                            query = list(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=x['id'], propose_detail__lesson_propose__added_by=qr['added_by'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_detail__lesson_propose__subject=y['id'], propose_detail__in=approved_propose_detail).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values('propose_detail__lno', 'propose_topic__unit', 'propose_detail__schedule_date', 'propose_detail__id').annotate(lno=F('propose_detail__lno'), unit_no=F('propose_topic__unit'), schedule_date=F('propose_detail__schedule_date')).distinct().order_by('propose_detail__lno'))
                            print(query)
                            for q in query:
                                q['topic'] = []
                                q['bt_level'] = []

                                qry1 = LessonProposeTopics.objects.filter(propose_detail__lno=q['propose_detail__lno'], propose_topic__unit=q['propose_topic__unit'], propose_detail__lesson_propose__added_by=qr['added_by'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_detail__lesson_propose__subject=y['id'],propose_detail__in=approved_propose_detail).filter(**extra_filter2).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").values_list('propose_topic__topic_name', flat=True)
                                if qry1:
                                    q['topic'].extend(qry1)

                                qry2 = LessonProposeBTLevel.objects.filter(propose_detail__id=q['propose_detail__id'], propose_detail__lesson_propose__added_by=qr['added_by']).filter(**extra_filter2).exclude(status="DELETE").values_list('bt_level__value', flat=True)
                                if qry2:
                                    q['bt_level'].extend(qry2)

                                qry4 = list(LessonProposeApproval.objects.filter(propose_detail=q['lno'],
                                                                                 propose_detail__lesson_propose__subject=y['id'],  propose_detail__lesson_propose__added_by=qr['added_by'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial']).filter(**extra_filter2).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values('approval_status'))
                                for qz in qry_approved:
                                    if qz['propose_detail__id']==q['propose_detail__id']:
                                        q['status'] = qz['approval_status']
                                        if qz['approval_status'] not in approved_rejected:
                                            approved_rejected.append(qz['approval_status'])
                            if len(query) > 0:
                                data.append({"data": query, "type": x['lecture_tutorial'],"APPROVED_REJECTED":approved_rejected})
                        if len(query_lecture_tutorial) > 0 and len(data) > 0:
                            if isgroup=='N':
                                data1.append({"data": data, "faculty": qr['added_by__name'], "subject": y['sub_name'], "subject_id": y['id'], "sem_name": sem_name, "section_name": section_name})
                            else:
                                data1.append({"data": data, "faculty": qr['added_by__name'], "subject": y['sub_name'], "subject_id": y['id'], "sem_name": sem_name, "group_name": group_name})
                return functions.RESPONSE(data1, statusCodes.STATUS_SUCCESS)
                ###################################################################################################################

        ##############################################submit approval status for lesson plan with remarks(if any)#################
        elif requestMethod.PUT_REQUEST(request):
            received_data = json.loads(request.body)
            date = datetime.date.today()
            print(date)
            print(LessonProposeApproval)
            li = []
            print(received_data)
            for x in received_data:
                sub = x['subject_id']
                lno = x['lno']

                for l in lno:
                    li.append({'propose_detail': LessonProposeDetail.objects.get(id=l['propose_detail__id']), 'approved_by': EmployeePrimdetail.objects.get(emp_id=request.session['hash1']), 'approval_date': date, 'approval_status': l['approval_status']})
                    if x['remark'] is not None:
                        li[-1]['remark'] = x['remark']
            for l in li:
                q_create = LessonProposeApproval.objects.create(**l)
            return functions.RESPONSE(statusMessages.MESSAGE_SUCCESS, statusCodes.STATUS_SUCCESS)
        ########################################################################################################################

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
################################################################################################################################


#########################################submit lesson plan details corresponding to attendance#################################
def completed_lesson_plan(att_id, session_name, session_id, emp_id, topic):
    LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name)
    LessonCompletedTopic = generate_session_table_name("LessonCompletedTopic_", session_name)
    Attendance = generate_session_table_name("Attendance_", session_name)
    LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)
    StudentAttStatus = generate_session_table_name("StudentAttStatus_", session_name)
    qry1 = list(Attendance.objects.filter(id=att_id).exclude(status="DELETE").values('section', 'subject_id', 'emp_id', 'normal_remedial','isgroup','group_id','date','lecture'))
    print(qry1)
    if qry1[0]['normal_remedial'] == "T":
        lecture_tutorial = "T"
    elif qry1[0]['normal_remedial'] == "N":
        lecture_tutorial = "L"
    if qry1[0]['isgroup'] == 'N':
        qry2 = list(LessonCompletedDetail.objects.filter(lecture_details__emp_id=qry1[0]['emp_id'], lecture_details__section=qry1[0]['section'], lecture_details__subject_id=qry1[0]['subject_id'], lecture_tutorial=lecture_tutorial).exclude(status="DELETE").exclude(lecture_details__status="DELETE").values('lno',).order_by('-lno'))
################################YASH###################################################################
        grp_dist = False
    else:
        qry2 = list(LessonCompletedDetail.objects.filter(lecture_details__emp_id=qry1[0]['emp_id'], lecture_details__group_id=qry1[0]['group_id'], lecture_details__subject_id=qry1[0]['subject_id'], lecture_tutorial=lecture_tutorial).exclude(status="DELETE").exclude(lecture_details__status="DELETE").values('lno',).order_by('-lno'))
        grp_dist = LessonCompletedDetail.objects.filter(lecture_details__emp_id=qry1[0]['emp_id'], lecture_details__group_id=qry1[0]['group_id'], lecture_details__subject_id=qry1[0]['subject_id'],lecture_details__date=qry1[0]['date'],lecture_details__lecture=qry1[0]['lecture'] ,lecture_tutorial=lecture_tutorial).exclude(status="DELETE").exclude(lecture_details__status="DELETE").exists()
        print(grp_dist)
    if len(qry2) > 0 and  grp_dist==False:
        lno = qry2[0]['lno'] + 1
    elif len(qry2)>0 and grp_dist:
        lno = qry2[0]['lno']
    else:
        lno = 1
###########################################################################################################
    query = LessonCompletedDetail.objects.update_or_create(lecture_details=att_id, status="INSERT", lecture_tutorial=lecture_tutorial, defaults={'lecture_details': Attendance.objects.get(id=att_id), 'lno': lno, 'lecture_tutorial': lecture_tutorial})

    objs = (LessonCompletedTopic(completed_topic=LessonTopicDetail.objects.get(id=x), completed_detail=LessonCompletedDetail.objects.get(id=query[0].id)) for x in topic)
    bulk_query = LessonCompletedTopic.objects.bulk_create(objs)
    if bulk_query:
        return 200
    else:
        return 202
##############################################################################################################################

################################Check if the lesson plan exists corresponding to which attendance is to be marked##############
def check_lesson_plan_exists(session_name, session_id, emp_id, topic, subject, extra_filter, att_type):
    LessonProposeApproval = generate_session_table_name("LessonProposeApproval_", session_name)
    LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)

    q = list(StudentAcademicsDropdown.objects.filter(sno=att_type).values('value'))
    if q[0]['value'] == "TUTORIAL":
        lecture_tutorial = "T"
    else:
        lecture_tutorial = "L"
    qry1 = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=subject, propose_detail__lesson_propose__added_by=emp_id, propose_detail__lesson_propose__lecture_tutorial=lecture_tutorial, approval_status="APPROVED").filter(**extra_filter).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values_list('propose_detail__id', flat=True).distinct())
    if len(qry1) > 0:
        return 1
    else:
        return 0
################################################################################################################################


##########################get dropdowns of units and their corresponding topics approved by HOD################################
def complete_lesson_plan_dropdown(request):
    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        session_name = request.session['Session_name']
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        # LessonCompleted = generate_session_table_name("LessonCompleted_",session_name)
        LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name)
        LessonCompletedApproval = generate_session_table_name("LessonCompletedApproval_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        LessonCompletedTopic = generate_session_table_name("LessonCompletedTopic_", session_name)
        LessonProposeTopics = generate_session_table_name("LessonProposeTopics_", session_name)
        LessonProposeApproval = generate_session_table_name("LessonProposeApproval_", session_name)
        LessonTopicDetail = generate_session_table_name("LessonTopicDetail_", session_name)
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_unit')):
                subject_id = request.GET['subject_id']
                att_type = request.GET['att_type']
                isgroup = request.GET['isgroup']
                if isgroup == 'N':
                    section = request.GET['section']
                    extra_filter={'propose_detail__lesson_propose__section':section}
                else:
                    extra_filter={'propose_detail__lesson_propose__group_id':request.GET['group_id']}
                data = []
                q = list(StudentAcademicsDropdown.objects.filter(sno=att_type).values('value'))
                if q[0]['value'] == "TUTORIAL":
                    lecture_tutorial = "T"
                else:
                    lecture_tutorial = "L"
                qry = list(LessonProposeApproval.objects.filter(propose_detail__lesson_propose__subject=subject_id, propose_detail__lesson_propose__added_by=request.session['hash1'],propose_detail__lesson_propose__lecture_tutorial=lecture_tutorial, approval_status="APPROVED").filter(**extra_filter).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values_list('propose_detail__id', flat=True).distinct())
                if len(qry) > 0:
                    qry11 = list(LessonProposeTopics.objects.filter(propose_detail__in=qry, propose_detail__lesson_propose__added_by=request.session['hash1'], propose_detail__lesson_propose__lecture_tutorial=lecture_tutorial).filter(**extra_filter).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values_list('propose_topic__unit', flat=True).distinct())
                    for unit in qry11:
                        qry1 = list(LessonProposeTopics.objects.filter(propose_detail__in=qry, propose_topic__subject=subject_id, propose_topic__unit=unit, propose_detail__lesson_propose__added_by=request.session['hash1'],  propose_detail__lesson_propose__lecture_tutorial=lecture_tutorial).filter(**extra_filter).exclude(status="DELETE").values('propose_topic__topic_name', 'propose_topic__id','propose_topic__unit').distinct())
                        data.append({"unit": unit, "topic": qry1})
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
##################################################################################################################################


###########################delete completed lesson plan entries on attendance delete##############################################
def delete_lesson_plan_completed(session_name, session_id, emp_id, att_id):
    LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name)
    LessonCompletedTopic = generate_session_table_name("LessonCompletedTopic_", session_name)

    qry1 = list(LessonCompletedDetail.objects.filter(lecture_details=att_id).exclude(status="DELETE").values('id'))
    if len(qry1) > 0:
        qry2 = LessonCompletedDetail.objects.filter(id=qry1[0]['id']).update(status="DELETE")
        qry3 = LessonCompletedTopic.objects.filter(completed_detail=qry1[0]['id']).update(status="DELETE")
    return 1
#################################################################################################################################

###########################update completed lesson plan entries on attendance update##############################################
def update_lesson_plan(att_id, session_name, updated_att_id):
    if int(session_name[:2]) < 19:
        return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
    LessonCompletedDetail = generate_session_table_name("LessonCompletedDetail_", session_name)
    LessonCompletedTopic = generate_session_table_name("LessonCompletedTopic_", session_name)
    qry = list(LessonCompletedDetail.objects.filter(lecture_details=att_id).exclude(status="DELETE").values('id'))
    # print(qry[0]['id'], "id")
    if len(qry) > 0:
        qry_update_detail = LessonCompletedDetail.objects.filter(id=qry[0]['id']).update(lecture_details=updated_att_id)
    return 1
##################################################################################################################################
