from login.views import checkpermission, generate_session_table_name
from StudentAcademics.models import *
from StudentMMS.models import *
from django.db.models import Sum, F


def get_ct_date(sem_id, session_name, session_id, subject_type):
    ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
    qry_exam_schedule = list(ExamSchedule.objects.filter(sem=sem_id, subject_type=subject_type, exam_id__session=session_id).exclude(status="DELETE").values('exam_id', 'exam_id__value', 'from_date', 'to_date').order_by('from_date').distinct())

    if len(qry_exam_schedule) > 0:
        for x in range(0, len(qry_exam_schedule)):
            if x == 0:
                f_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
                qry_exam_schedule[x]['to_date'] = qry_exam_schedule[x]['from_date']
                qry_exam_schedule[x]['from_date'] = f_date[0]['sem_start']
            # elif x == (len(qry_exam_schedule) - 1):
            #     t_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
            #     qry_exam_schedule[x]['from_date'] = qry_exam_schedule[x]['to_date']
            #     qry_exam_schedule[x]['to_date'] = f_date[0]['sem_end']

            else:
                qry_exam_schedule[x]['to_date'] = qry_exam_schedule[x]['from_date']
                qry_exam_schedule[x]['from_date'] = qry_exam_schedule[x - 1]['to_date']
    # qry_exam_schedule.append({'to_date': to_date, 'from_date': from_date, 'exam_id__value': "Overall"})
    # qry_exam_schedule[x]['to_date'] = to_date
    # qry_exam_schedule[x]['from_date'] = from_date
    # qry_exam_schedule[x]['exam_id__value'] = "Overall"
    # else:
    #   qry_exam_schedule=[]
    #   qry_exam_schedule.append({})
    #   f_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
    #   qry_exam_schedule[0]['from_date']=f_date[0]['sem_start']
    #   qry_exam_schedule[0]['to_date']=f_date[0]['sem_end']
    return qry_exam_schedule


def get_ct_date_update(sem_id, session_name, session_id, subject_type, from_date, to_date):
    ExamSchedule = generate_session_table_name("ExamSchedule_", session_name)
    qry_exam_schedule = list(ExamSchedule.objects.filter(sem=sem_id, subject_type=subject_type, exam_id__session=session_id).exclude(status="DELETE").values('exam_id', 'exam_id__value', 'from_date', 'to_date').order_by('from_date').distinct())

    if len(qry_exam_schedule) > 0:
        for x in range(0, len(qry_exam_schedule)):
            if x == 0:
                f_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
                qry_exam_schedule[x]['to_date'] = qry_exam_schedule[x]['from_date']
                qry_exam_schedule[x]['from_date'] = f_date[0]['sem_start']
            # elif x == (len(qry_exam_schedule) - 1):
            #     t_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
            #     qry_exam_schedule[x]['from_date'] = qry_exam_schedule[x]['to_date']
            #     qry_exam_schedule[x]['to_date'] = f_date[0]['sem_end']

            else:
                qry_exam_schedule[x]['to_date'] = qry_exam_schedule[x]['from_date']
                qry_exam_schedule[x]['from_date'] = qry_exam_schedule[x - 1]['to_date']
    qry_exam_schedule.append({'to_date': to_date, 'from_date': from_date, 'exam_id__value': "Overall"})
    # qry_exam_schedule[x]['to_date'] = to_date
    # qry_exam_schedule[x]['from_date'] = from_date
    # qry_exam_schedule[x]['exam_id__value'] = "Overall"
    # else:
    #   qry_exam_schedule=[]
    #   qry_exam_schedule.append({})
    #   f_date = list(Semtiming.objects.filter(session_name=session_name).values('sem_start', 'sem_end'))
    #   qry_exam_schedule[0]['from_date']=f_date[0]['sem_start']
    #   qry_exam_schedule[0]['to_date']=f_date[0]['sem_end']
    return qry_exam_schedule


def get_emp_propose_vs_actual_data_report(added_by, subject_id, session_id, ct_date, extra_filter1, extra_filter2, extra_filter3, extra_filter4, session_name):
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
    LessonCompletedApproval = generate_session_table_name("LessonCompletedApproval_", session_name)
    query_lecture_tutorial = list(LessonPropose.objects.filter(subject=subject_id, session=session_id, status="INSERT", added_by=added_by).filter(**extra_filter1).values('lecture_tutorial', 'id'))
    data1 = []
    for x in query_lecture_tutorial:
        values = {}
        total_propose = []
        total_actual = []
        unit_wise = []
        query = list(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=x['id'], propose_detail__lesson_propose__added_by=added_by, propose_detail__lesson_propose__subject=subject_id).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values('propose_detail__lno', 'propose_topic__unit', 'propose_detail__schedule_date', 'propose_detail__id').annotate(lno=F('propose_detail__lno'), Proposed_Unit=F('propose_topic__unit'), Proposed_date=F('propose_detail__schedule_date')).distinct().order_by('propose_detail__lno'))
        distinct_units = []
        unit_data = []
        for unit in query:
            if unit['Proposed_Unit'] not in distinct_units:
                distinct_units.append(unit['Proposed_Unit'])
        for ct in ct_date:
            total_propose = []
            total_actual = []
            coverage = 0
            if len(query) > 0:
                for q in query:
                    q['Proposed_topic'] = []
                    q['Bt_level'] = []
                    qry1 = LessonProposeTopics.objects.filter(propose_detail__lno=q['propose_detail__lno'], propose_topic__unit=q['propose_topic__unit'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_topic__subject=subject_id, propose_detail__lesson_propose__added_by=added_by, propose_detail__schedule_date__range=[ct['from_date'], ct['to_date']]).filter(**extra_filter4).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").distinct().values_list('propose_topic__topic_name', flat=True)
                    if qry1:
                        q['Proposed_topic'].extend(qry1)
                        total_propose.extend(qry1)

                    # qry2 = list(LessonProposeBTLevel.objects.filter(propose_detail__id=q['propose_detail__id']).filter(**extra_filter4).exclude(status="DELETE").values_list('bt_level__value', flat=True))
                    # if len(qry2)>0:
                    # 	for bl in qry2:
                    # 		q['Bt_level'].append(bl.split(":")[0])

                    # qry4 = LessonProposeApproval.objects.filter(propose_detail__lno=q['lno'], propose_detail__lesson_propose__subject=subject_id,propose_detail__lesson_propose__added_by=added_by, propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial']).filter(**extra_filter4).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values('approval_status')
                    # if len(qry4) > 0:
                    # 	q['Proposed_status'] = qry4[0]['approval_status']
                    # else:
                    # 	q['Proposed_status'] = "PENDING"
            else:
                query = []

            query1 = list(LessonCompletedTopic.objects.filter(completed_detail__lecture_details__emp_id=added_by, completed_detail__lecture_tutorial=x['lecture_tutorial'], completed_detail__lecture_details__subject_id=subject_id, completed_detail__lecture_details__date__range=[ct['from_date'], ct['to_date']]).filter(**extra_filter2).exclude(status="DELETE").exclude(completed_detail__status="DELETE").distinct().values('completed_detail__lecture_details__date', 'completed_detail__id', 'completed_detail__approval_status', 'completed_detail__lecture_details__lecture').annotate(lno=F('completed_detail__lno'), Actual_date=F('completed_detail__lecture_details__date'), Actual_status=F('completed_detail__approval_status')).distinct().order_by('completed_detail__lecture_details__date', 'completed_detail__lecture_details__lecture'))
            plan_remark = None
            if len(query1) > 0:
                for q in query1:

                    q['Actual_Topic'] = []
                    query2 = list(LessonCompletedTopic.objects.filter(completed_detail__lno=q['lno'], completed_detail__lecture_details__emp_id=added_by, completed_detail__lecture_tutorial=x['lecture_tutorial'], completed_detail__lecture_details__subject_id=subject_id, completed_detail__lecture_details__date__range=[ct['from_date'], ct['to_date']], completed_detail=q['completed_detail__id']).filter(**extra_filter2).exclude(status="DELETE").exclude(completed_detail__status="DELETE").distinct().exclude(completed_topic__status="DELETE").values_list('completed_topic__topic_name', flat=True))
                    if query2:
                        q['Actual_Topic'].extend(query2)
                        total_actual.extend(query2)

                    # query3 = list(LessonCompletedTopic.objects.filter(completed_topic__topic_name__in=query2,completed_detail__lecture_details__emp_id=added_by,completed_detail__lno=q['lno'],completed_detail__lecture_tutorial=x['lecture_tutorial'], completed_detail__lecture_details__subject_id=subject_id,completed_detail__lecture_details__date__range=[ct['from_date'],ct['to_date']]).filter(**extra_filter2).exclude(status="DELETE").exclude(completed_detail__status="DELETE").exclude(completed_topic__status="DELETE").values_list('completed_topic__unit',flat=True).distinct())
                    # q['Actual_Unit'] =[]
                    # if len(query3)>0:
                    # 	q['Actual_Unit'].extend(query3)

                    # qry_remark=list(LessonCompletedApproval.objects.filter(completed_detail=q['completed_detail__id']).exclude(status="DELETE").values('remark'))

                    # if len(qry_remark)>0:
                    # 	if qry_remark[0]['remark'] is not None and qry_remark[0]['remark'] != "":
                    # 		plan_remark=qry_remark[0]['remark']
            else:
                query1 = []

            unit_dict = {}
            unit_dict['ct_name'] = ct['exam_id__value']
            for unit in distinct_units:
                unit_propose = []
                unit_actual = []
                for q in query:
                    unit_qry1 = LessonProposeTopics.objects.filter(propose_detail__lno=q['propose_detail__lno'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_topic__subject=subject_id, propose_detail__lesson_propose__added_by=added_by, propose_detail__schedule_date__range=[ct['from_date'], ct['to_date']], propose_topic__unit=unit).filter(**extra_filter4).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").distinct().values_list('propose_topic__topic_name', flat=True)
                    if len(unit_qry1) > 0:
                        unit_propose.extend(unit_qry1)

                for q in query1:
                    unit_query2 = list(LessonCompletedTopic.objects.filter(completed_detail__lno=q['lno'], completed_detail__lecture_details__emp_id=added_by, completed_detail__lecture_tutorial=x['lecture_tutorial'], completed_detail__lecture_details__subject_id=subject_id, completed_detail__lecture_details__date__range=[ct['from_date'], ct['to_date']], completed_detail=q['completed_detail__id'], completed_topic__unit=unit).filter(**extra_filter2).exclude(status="DELETE").exclude(completed_detail__status="DELETE").distinct().exclude(completed_topic__status="DELETE").values_list('completed_topic__topic_name', flat=True))
                    if len(unit_query2) > 0:
                        unit_actual.extend(unit_query2)
                unit_coverage = get_coverage(unit_propose, unit_actual)
                unit_dict['Unit_' + str(unit)] = unit_coverage
            coverage = get_coverage(total_propose, total_actual)
            unit_dict['Total'] = coverage
            unit_data.append(unit_dict)
            values[ct['exam_id__value']] = coverage
        values['unit_wise'] = unit_data
        if len(values) > 0:
            if x['lecture_tutorial'] == "L":
                typ = "THEORY"
            else:
                typ = "TUTORIAL"
        values['type'] = typ
        values['plan_remark'] = plan_remark
        data1.append(values)
    return data1


def get_coverage(total_propose, total_actual):
    distinct_proposed_topics = set(total_propose)
    total_actual_count = 0
    coverage = 0
    propose_count = 0
    # actual_count=0
    for distinct_topic in distinct_proposed_topics:
        actual_count = 0
        # for tp in total_propose:
        # 	if distinct_topic==tp:
        # 		propose_count+=1
        # for ta in total_actual:
        # 	if distinct_topic==ta:
        # 		actual_count+=1
        # if actual_count!=0:
        # 	total_actual_count += actual_count
        # 	coverage+=(((propose_count/actual_count)*100)*actual_count)
        # else:
        # 	total_actual_count+=propose_count
        for ta in total_actual:
            if distinct_topic == ta:
                actual_count += 1
        if actual_count != 0:
            for tp in total_propose:
                if distinct_topic == tp:
                    propose_count += 1
        else:
            for tp in total_propose:
                if distinct_topic == tp:
                    actual_count += 1
        total_actual_count += actual_count

        # 	total_actual_count += actual_count
        # 	coverage+=(((propose_count/actual_count)*100)*actual_count)
        # else:
        # 	total_actual_count+=propose_count

    if total_actual_count != 0:
        actual_coverage = (propose_count / total_actual_count) * 100
    else:
        actual_coverage = 0

    return '%.2f' % actual_coverage


def get_emp_propose_vs_actual_data_new(added_by, subject_id, session_id, ct_date, extra_filter1, extra_filter2, extra_filter3, extra_filter4, session_name):
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
    LessonCompletedApproval = generate_session_table_name("LessonCompletedApproval_", session_name)
    LessonCompletedRemark = generate_session_table_name("LessonCompletedRemark_", session_name)
    query_lecture_tutorial = list(LessonPropose.objects.filter(subject=subject_id, session=session_id, status="INSERT", added_by=added_by).filter(**extra_filter1).values('lecture_tutorial', 'id'))
    data1 = []
    data = []
    for x in query_lecture_tutorial:
        data = []
        ct_no = 1
        for ct in ct_date:
            query = list(LessonProposeTopics.objects.filter(propose_detail__lesson_propose=x['id'], propose_detail__lesson_propose__added_by=added_by, propose_detail__schedule_date__gte=ct['from_date'], propose_detail__schedule_date__lte=ct['to_date'], propose_detail__lesson_propose__subject=subject_id).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values('propose_detail__lno', 'propose_topic__unit', 'propose_detail__schedule_date', 'propose_detail__id').annotate(lno=F('propose_detail__lno'), Proposed_Unit=F('propose_topic__unit'), Proposed_date=F('propose_detail__schedule_date')).distinct().order_by('propose_detail__lno'))
            if len(query) > 0:
                for q in query:
                    q['Proposed_topic'] = []
                    q['Bt_level'] = []
                    qry1 = LessonProposeTopics.objects.filter(propose_detail__lno=q['propose_detail__lno'], propose_topic__unit=q['propose_topic__unit'], propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial'], propose_topic__subject=subject_id, propose_detail__lesson_propose__added_by=added_by, propose_detail__schedule_date__gte=ct['from_date'], propose_detail__schedule_date__lte=ct['to_date']).filter(**extra_filter4).exclude(status__contains="DELETE").exclude(propose_detail__status="DELETE").exclude(propose_topic__status="DELETE").distinct().values_list('propose_topic__topic_name', flat=True)
                    if qry1:
                        q['Proposed_topic'].extend(qry1)

                    qry2 = list(LessonProposeBTLevel.objects.filter(propose_detail__id=q['propose_detail__id']).filter(**extra_filter4).exclude(status="DELETE").values_list('bt_level__value', flat=True))
                    if len(qry2) > 0:
                        for bl in qry2:
                            q['Bt_level'].append(bl.split(":")[0])

                    qry4 = LessonProposeApproval.objects.filter(propose_detail__lno=q['lno'], propose_detail__lesson_propose__subject=subject_id, propose_detail__lesson_propose__added_by=added_by, propose_detail__lesson_propose__lecture_tutorial=x['lecture_tutorial']).filter(**extra_filter4).exclude(status="DELETE").exclude(propose_detail__status="DELETE").values('approval_status')
                    if len(qry4) > 0:
                        q['Proposed_status'] = qry4[0]['approval_status']
                    else:
                        q['Proposed_status'] = "PENDING"
            else:
                query = []

            query1 = list(LessonCompletedTopic.objects.filter(completed_detail__lecture_details__emp_id=added_by, completed_detail__lecture_tutorial=x['lecture_tutorial'], completed_detail__lecture_details__subject_id=subject_id, completed_detail__lecture_details__date__lte=ct['to_date'], completed_detail__lecture_details__date__gte=ct['from_date']).filter(**extra_filter2).exclude(status="DELETE").exclude(completed_detail__status="DELETE").distinct().values('completed_detail__lecture_details__date', 'completed_detail__id', 'completed_detail__approval_status', 'completed_detail__lecture_details__lecture', 'completed_detail__lecture_details__group_id', 'completed_detail__lecture_details__group_id__group_type').annotate(lno=F('completed_detail__lno'), Actual_date=F('completed_detail__lecture_details__date'), Actual_status=F('completed_detail__approval_status')).distinct().order_by('completed_detail__lecture_details__date', 'completed_detail__lecture_details__lecture'))
            query1_copy = []
            plan_remark = None
            if len(query1) > 0:
                date_data = {}
                lecture = None
                i = 0
                for q in query1:
                    # print(q, '     nnfekfnekfncle')
                    flag = 0
                    if 'INTER' in str(q['completed_detail__lecture_details__group_id__group_type']):
                        if q['Actual_date'] in date_data:
                            if q['completed_detail__lecture_details__lecture'] in date_data[q['Actual_date']]:
                                flag = 1
                            else:
                                date_data[q['Actual_date']].append(q['completed_detail__lecture_details__lecture'])
                        else:
                            date_data[q['Actual_date']] = []
                            date_data[q['Actual_date']].append(q['completed_detail__lecture_details__lecture'])

                    if flag == 1:
                        i = i + 1
                        continue

                    q['Actual_Topic'] = []
                    query2 = list(LessonCompletedTopic.objects.filter(completed_detail__lno=q['lno'], completed_detail__lecture_details__emp_id=added_by, completed_detail__lecture_tutorial=x['lecture_tutorial'], completed_detail__lecture_details__subject_id=subject_id, completed_detail__lecture_details__date__lte=ct['to_date'], completed_detail__lecture_details__date__gte=ct['from_date'], completed_detail=q['completed_detail__id']).filter(**extra_filter2).exclude(status="DELETE").exclude(completed_detail__status="DELETE").distinct().exclude(completed_topic__status="DELETE").values_list('completed_topic__topic_name', flat=True))
                    if query2:
                        q['Actual_Topic'].extend(query2)

                    query3 = list(LessonCompletedTopic.objects.filter(completed_topic__topic_name__in=query2, completed_detail__lecture_details__emp_id=added_by, completed_detail__lno=q['lno'], completed_detail__lecture_tutorial=x['lecture_tutorial'], completed_detail__lecture_details__subject_id=subject_id, completed_detail__lecture_details__date__lte=ct['to_date'], completed_detail__lecture_details__date__gte=ct['from_date']).filter(**extra_filter2).exclude(status="DELETE").exclude(completed_detail__status="DELETE").exclude(completed_topic__status="DELETE").values_list('completed_topic__unit', flat=True).distinct())
                    q['Actual_Unit'] = []
                    if len(query3) > 0:
                        q['Actual_Unit'].extend(query3)

                    qry_remark = list(LessonCompletedRemark.objects.filter(propose_detail=x['id']).exclude(status="DELETE").values('remark'))

                    if len(qry_remark) > 0:
                        if qry_remark[0]['remark'] is not None and qry_remark[0]['remark'] != "":
                            plan_remark = qry_remark[0]['remark']
                    query1_copy.append(q)
            else:
                query1 = []

            len_propose = len(query)
            len_actual = len(query1_copy)
            new_data = []
            for xx in range(0, max(len_propose, len_actual)):
                new_data.append({})
                try:
                    new_data[xx]['Proposed_topic'] = []
                    new_data[xx]['Proposed_Unit'] = query[xx]['propose_topic__unit']
                    new_data[xx]['Proposed_topic'].extend(query[xx]['Proposed_topic'])
                    new_data[xx]['Bt_level'] = query[xx]['Bt_level']
                    new_data[xx]['Proposed_status'] = query[xx]['Proposed_status']
                    new_data[xx]['Proposed_date'] = query[xx]['propose_detail__schedule_date']
                except:
                    new_data[xx]['Proposed_unit'] = None
                    new_data[xx]['Proposed_topic'] = None
                    new_data[xx]['Bt_level'] = None
                    new_data[xx]['Proposed_status'] = None
                    new_data[xx]['Proposed_date'] = None
                try:
                    new_data[xx]['Actual_Topic'] = []
                    new_data[xx]['Actual_date'] = query1_copy[xx]['Actual_date']
                    new_data[xx]['Actual_Topic'].extend(query1_copy[xx]['Actual_Topic'])
                    new_data[xx]['Actual_Unit'] = query1_copy[xx]['Actual_Unit']
                    new_data[xx]['Actual_status'] = query1_copy[xx]['Actual_status']
                    new_data[xx]['completed_detail__id'] = query1_copy[xx]['completed_detail__id']

                except:
                    new_data[xx]['Actual_date'] = None
                    new_data[xx]['Actual_Topic'] = None
                    new_data[xx]['Actual_Unit'] = None
                    new_data[xx]['Actual_status'] = None
                    new_data[xx]['completed_detail__id'] = None

                if new_data[xx]['Actual_Topic'] is not None and new_data[xx]['Proposed_topic']:
                    result = all(elem in new_data[xx]['Actual_Topic'] for elem in new_data[xx]['Proposed_topic'])
                    if result:
                        new_data[xx]['color_status'] = "green"
                    else:
                        new_data[xx]['color_status'] = "red"
                else:
                    new_data[xx]['color_status'] = "red"

            if len(query) > 0 or len(query1_copy) > 0:
                data.append({"ct_no": ct['exam_id__value'], "data": new_data})
                ct_no += 1
        if len(data) > 0:
            data1.append({"type": x['lecture_tutorial'], "ct_data": data, "plan_remark": plan_remark})

    return data1
