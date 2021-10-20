from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
import json
import os
import time
import math
from itertools import groupby
from datetime import date, datetime
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType

from StudentMMS.models import *
from StudentAcademics.models import *
from Registrar.models import *
from musterroll.models import EmployeePrimdetail

from login.views import checkpermission, generate_session_table_name
from .mms_function_views import get_btlevel, get_skillsetlevel, get_verb, get_skillsetlevel_filtered, get_btleveldata, get_CO_subject, get_co, get_po, get_co_list, get_max_marks, get_coordinator_sem, get_exam_name, get_sem_mms_subjects, get_subjects_hod_dean, get_subjects_faculty, get_student_marks, get_student_subject_ct_marks, get_student_subject_ta_marks, get_student_subject_att_marks, get_student_subject_bonus_marks, get_student_subject_extra_bonus_marks, new_exam_dropdown, get_exam_co_dropdown, get_po_list, get_student_marks_new, get_student_subject_att_marks_new
from StudentAcademics.views import *
from .harsh_views import fetch_bonus_marks
from StudentMMS.tasks import call_store_ctwise_marks

# Create your views here.


def paper_data(data_form, session_name):
    ques_paper_id = data_form.GET['ques_paper_id']
    exam_id = data_form.GET['exam_id']
    sem = data_form.GET['sem']
    session = data_form.session['Session']

    data = []
    QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
    QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)
    QuesPaperBTAttainment = generate_session_table_name("QuesPaperBTAttainment_", session_name)
    QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
    SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)
    SubjectQuesOptions = generate_session_table_name("SubjectQuesOptions_", session_name)

    question_format = list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id=ques_paper_id).values('section_id', 'section_id__ques_paper_id', 'section_id__ques_paper_id__time'))

    total_max_marks = QuesPaperSectionDetails.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).aggregate(total_max_marks=Sum('max_marks'))
    data.append({'time_duration': question_format[0]['section_id__ques_paper_id__time'], 'Max_marks': total_max_marks.get('total_max_marks', 0)})

    data[0]['bt_level_attain'] = []
    data[0]['bt_level_attain'] = list(QuesPaperBTAttainment.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).values('minimum', 'maximum').annotate(bt_level=F('bt_level__value')))

    data[0]['section'] = []
    data[0]['session'] = session

    section_data = list(QuesPaperSectionDetails.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).values('id', 'name', 'attempt_type', 'max_marks'))
    data[0]['section'] = section_data

    i = 0
    for section in data[0]['section']:
        ques_list = QuestionPaperQuestions.objects.filter(ques_paper_id=ques_paper_id, section_id=section['id']).exclude(status='DELETE').values('ques_id', 'ques_num', 'section_id')

        section['question'] = []
        i = 0
        for k, v in groupby(ques_list, key=lambda x: x['ques_num']):
            v = list(v)
            id_list = []
            for t in v:
                id_list.append(t['ques_id'])

            qry = list(SubjectAddQuestions.objects.filter(id__in=id_list).extra(select={'id_ins': 'FIELD(id,%s)' % ','.join(map(str, id_list))}, order_by=['id_ins']).values('id', 'description', 'question_img', 'max_marks', 'bt_level__value', 'type', 'co_id'))
            section['question'].append(qry)

            for q in qry:
                qj = list(SubjectAddQuestions.objects.filter(id=q['id']).values('co_id__description', 'co_id__co_num'))
                q['co_id__description'] = qj[0]['co_id__description']
                q['co_id__co_num'] = qj[0]['co_id__co_num']
                if q['type'] == 'O':
                    q['option'] = list(SubjectQuesOptions.objects.filter(ques_id=q['id']).values('option_description', 'option_img', 'is_answer'))

    return data


def bloomtaxonomy(request):

    if checkpermission(request, [rolesCheck.ROLE_DEAN, rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        session = request.session['Session_id']
        session_name = request.session['Session_name']
        BTLevelSettings = generate_session_table_name("BTLevelSettings_", session_name)
        if requestMethod.GET_REQUEST(request):
            status = statusCodes.STATUS_SUCCESS
            if(requestType.firstrequest(request.GET)):
                bt_level = get_btlevel(session)
                skill_set_level = get_skillsetlevel(session)
                data = {'data1': bt_level, 'data2': skill_set_level}

            elif(requestType.custom_request_type(request.GET, 'verbs')):
                qry = get_verb(request.GET['bt_level'], session_name)
                data = {'data': qry}

            elif(requestType.custom_request_type(request.GET, 'show_previous')):
                data = []
                bt_level = get_btleveldata(session_name)
                for b in bt_level:
                    skill_set_level = get_skillsetlevel_filtered(b['bt_level'], session_name)
                    verb = get_verb(b['bt_level'], session_name)
                    data.append({'bt_level': b['bt_level__value'], 'skill_set_level': skill_set_level[0]['skill_set_level__value'], 'verbs': verb})

            elif(requestType.custom_request_type(request.GET, 'previous_values')):
                data2 = list(BTLevelSettings.objects.filter(bt_level=request.GET['bt_level']).exclude(status='DELETE').exclude(verb__isnull=True).values('verb', 'skill_set_level__value', 'skill_set_level'))
                # print(data2)
                data = {'data': data2}

            else:
                data = statusMessages.MESSAGE_BAD_REQUEST
                status = statusCodes.STATUS_BAD_REQUEST
            return functions.RESPONSE(data, status)

        if requestMethod.POST_REQUEST(request):
            emp_id = request.session['hash1']
            data = json.loads(request.body)

            qry_sections = list(Sections.objects.values_list('section_id', flat=True))

            if check_islocked('DMS', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            bt_level = data['bt_level']
            bt_num = data['bt_num']
            skill_set_level = data['skill_set_level']
            verb = data['verb']
            qry = BTLevelSettings.objects.filter(bt_level=bt_level).update(status='DELETE')
            objs = (BTLevelSettings(bt_level=StudentAcademicsDropdown.objects.get(sno=bt_level), skill_set_level=StudentAcademicsDropdown.objects.get(sno=skill_set_level), verb=v['text'].upper(), added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), bt_num=bt_num) for v in verb)
            qry_insert = BTLevelSettings.objects.bulk_create(objs)

            data = statusMessages.MESSAGE_INSERT

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Set_CO_details(request):
    if academicCoordCheck.isSubjectCOCoord(request):
        emp_id = request.session['hash1']
        session_name = request.session['Session_name']
        session = request.session['Session_id']

        SubjectCODetails = generate_session_table_name("SubjectCODetails_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
        SubjectQuestionPaper = generate_session_table_name('SubjectQuestionPaper_', session_name)

        print(request)
        if requestMethod.GET_REQUEST(request):

            if(requestType.custom_request_type(request.GET, 'sem')):
                dept = request.GET['dept']
                sem = get_coordinator_sem(emp_id, "CO", dept, session_name)
                data = {'data': sem}

            elif(requestType.custom_request_type(request.GET, 'subjects')):
                sem = request.GET['sem']
                dept = request.GET['dept']
                subjects = get_CO_subject(emp_id, sem, dept, session_name)
                data = {'data': subjects}

            elif(requestType.custom_request_type(request.GET, 'form_data1')):
                final_list = []
                co_exam_list = get_exam_co_dropdown(session)
                # qry=list(SubjectCODetails.objects.exclude(status='DELETE').exclude(co_num=-1).filter(subject_id=request.GET['subject_id']).values('co_num','description','id'))
                qry = list(SubjectCODetails.objects.exclude(status='DELETE').exclude(co_num=-1).filter(subject_id=request.GET['subject_id']).values('id', 'description', 'co_num', 'subject_id').annotate(co_id=F('id')))
                for q in qry:
                    qry1 = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').filter(co_id=q['id']).values('attainment_per').annotate(sno=F('attainment_method'), value=F('attainment_method__value')))
                    q['exams'] = []
                    if qry1:

                        q['exams'] = qry1

                qry1 = list(SubjectCODetailsAttainment.objects.exclude(co_id__status='DELETE').filter(co_id__subject_id=request.GET['subject_id'], co_id__co_num=-1).values('attainment_per'))

                data = {'data': qry, 'data1': co_exam_list, 'data2': qry1}

            elif(requestType.custom_request_type(request.GET, 'university_attain_per')):
                qry1 = SubjectCODetails.objects.filter(subject_id=request.GET['subject_id'], co_num=-1).update(status='DELETE')
                qry = SubjectCODetails.objects.create(subject_id=SubjectInfo.objects.get(id=request.GET['subject_id']), description='UNIVERSITY CO', added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), co_num=-1)
                qry2 = SubjectCODetailsAttainment.objects.create(co_id=SubjectCODetails.objects.get(id=qry.id), attainment_per=request.GET['attainment_per'])

                if qry:
                    data = statusMessages.MESSAGE_INSERT
            else:
                data = statusMessages.MESSAGE_BAD_REQUEST
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            qry_sem_id = SubjectCODetails.objects.filter(subject_id=data['subject_id']).values('subject_id__sem')
            if len(qry_sem_id) > 0:
                qry_sections = list(Sections.objects.filter(sem_id=qry_sem_id[0]['subject_id__sem']).exclude(status="DELETE").values_list('section_id', flat=True))
            else:
                qry_sections = []

            if check_islocked('CO', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            #### CHECK IF EXAM IS HELD FOR THAT SUBJECT WITH CO'S #####
            check = SubjectQuestionPaper.objects.filter(subject_id=data['subject_id'], approval_status="APPROVED").exclude(status="DELETE").values('exam_id')
            if len(check) > 0:
                data = statusMessages.CUSTOM_MESSAGE('COs cannot be deleted since the exam is already held for this subject.')
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            ###########################################################
            else:
                qry = SubjectCODetails.objects.filter(subject_id=data['subject_id']).update(status='DELETE')
                data = statusMessages.MESSAGE_DELETE

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.PUT_REQUEST(request):
            data = json.loads(request.body)
            description = data['description']
            subject_id = data['subject_id']
            co_id = data['co_id']
            qry_sem_id = SubjectCODetails.objects.filter(subject_id=subject_id).values('subject_id__sem')
            qry_sections = list(Sections.objects.filter(sem_id=qry_sem_id[0]['subject_id__sem']).values_list('section_id', flat=True))

            if check_islocked('CO', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            qry_id = SubjectCODetails.objects.filter(id=co_id).update(description=description, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), co_num=data['co_num'])
            for e in data['exams']:
                if 'attainment_per'in e:

                    if (e['attainment_per'] == None):
                        qry_update = SubjectCODetailsAttainment.objects.filter(co_id=co_id, attainment_method=e['sno']).update(status='DELETE')
                    else:
                        qry_update = SubjectCODetailsAttainment.objects.filter(co_id=co_id, attainment_method=e['sno']).update(attainment_per=e['attainment_per'], attainment_method=StudentAcademicsDropdown.objects.get(sno=e['sno']), status='UPDATE')
                    if not qry_update:

                        qry_create = SubjectCODetailsAttainment.objects.create(co_id=SubjectCODetails.objects.get(id=co_id), attainment_method=StudentAcademicsDropdown.objects.get(sno=e['sno']), attainment_per=e['attainment_per'])
                data = statusMessages.MESSAGE_UPDATE

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            print(data)
            x = len(data['description'])
            subject_id = data['subject_id']
            qry_sem_id = SubjectInfo.objects.filter(id=subject_id).values('sem')
            qry_sections = list(Sections.objects.filter(sem_id=qry_sem_id[0]['sem']).values_list('section_id', flat=True))
            if check_islocked('CO', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            qry_count_co = SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').count()
            qry = list(SubjectCODetails.objects.exclude(status='DELETE').filter(subject_id=subject_id).values('co_num', 'description', 'id'))
            count = 0
            for k, v in groupby(qry, key=lambda x: x['co_num']):
                count = count + 1
            i = 0
            for d in data['description']:
                create_id = SubjectCODetails.objects.create(subject_id=SubjectInfo.objects.get(id=subject_id), description=d['description'], added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), status='INSERT', co_num=i + 1 + count)
                qry_obj = (SubjectCODetailsAttainment(co_id=SubjectCODetails.objects.get(id=create_id.id), attainment_per=e['attainment_per'], attainment_method=StudentAcademicsDropdown.objects.get(sno=e['sno'])) for e in d['exams'])
                qry_create = SubjectCODetailsAttainment.objects.bulk_create(qry_obj)
                i += 1

            if qry:
                data = statusMessages.MESSAGE_INSERT

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def co_po_mapping(request):

    if academicCoordCheck.isSubjectCOCoord(request):
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        session_name = request.session['Session_name']
        SubjectCOPOMapping = generate_session_table_name("SubjectCOPOMapping_", session_name)
        SubjectCODetails = generate_session_table_name("SubjectCODetails_", session_name)
        Dept_VisMis = generate_session_table_name("Dept_VisMis_", session_name)
        print(request.session['Session_name'])
        if requestMethod.GET_REQUEST(request):
            if(requestType.firstrequest(request.GET)):
                subject_id = request.GET['subject_id']
                dept = request.GET['dept']
                co_list = get_co_list(subject_id, session_name)
                po_list = get_po(dept, session_name)
                co = get_co(subject_id, session_name)
                max_marks = get_max_marks(session)
                data1 = []
                qry = list(SubjectCOPOMapping.objects.filter(co_id__in=co_list).exclude(status='DELETE').values('po_id', 'po_id__description', 'max_marks', 'co_id', 'co_id__description'))
                for q in qry:
                    data1.append({'co_id': q['co_id'], 'co': q['co_id__description'], 'po_id': q['po_id'], 'po': q['po_id__description'], 'max_marks': q['max_marks']})

                data = {'data': data1, 'co_list': co, 'po_list': po_list, 'max_marks': max_marks}

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            received_data = json.loads(request.body)
            data1 = received_data['data1']
            data = received_data['data']
            co_list = get_co_list(data1['subject_id'], session_name)
            po_list = get_po_list(data1['dept'], session_name)
            qry_sem_id = SubjectCODetails.objects.filter(id=data[0]['co_id']).values('subject_id__sem')
            qry_sections = list(Sections.objects.filter(sem_id=qry_sem_id[0]['subject_id__sem']).values_list('section_id', flat=True))
            if check_islocked('CO', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            print(data1['subject_id'])


            qry = SubjectCOPOMapping.objects.filter(co_id__in=co_list, po_id__in=po_list).update(status='DELETE')
            for q in data:
                co_id = q['co_id']
                po_id = q['po_id']
                max_marks = q['max_marks']
                # qry = SubjectCOPOMapping.objects.filter(co_id=co_id, po_id=po_id).update(status='DELETE')
                qry1 = SubjectCOPOMapping.objects.create(co_id=SubjectCODetails.objects.get(id=co_id), po_id=Dept_VisMis.objects.get(id=po_id), max_marks=max_marks, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
                if qry1:
                    data = statusMessages.MESSAGE_INSERT

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def create_question_paper(request):

    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        emp_id = request.session['hash1']
        session_name = request.session['Session_name']
        session = request.session['Session_id']
        QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
        QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)
        QuesPaperBTAttainment = generate_session_table_name("QuesPaperBTAttainment_", session_name)
        QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
        SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
        SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)
        SubjectQuesOptions = generate_session_table_name("SubjectQuesOptions_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'exam_name')):
                exam_list = new_exam_dropdown(session)
                print(exam_list)
                data = {'data': exam_list}

            elif(requestType.firstrequest(request.GET)):
                exam_id = request.GET['exam_id']
                sem = request.GET['sem']
                session = request.session['Session_name']
                data = []
                qry = QuesPaperApplicableOn.objects.exclude(ques_paper_id__status="DELETE").filter(sem=sem, ques_paper_id__exam_id=exam_id).values('ques_paper_id', 'ques_paper_id__time')

                if not qry:
                    data = data = statusMessages.CUSTOM_MESSAGE('No Question Paper Format defined for this data')
                    return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                else:
                    total_max_marks = QuesPaperSectionDetails.objects.filter(ques_paper_id=qry[0]['ques_paper_id']).aggregate(total_max_marks=Sum('max_marks'))
                    data.append({'time_duration': qry[0]['ques_paper_id__time'], 'Max_marks': total_max_marks.get('total_max_marks', 0)})

                    bt_level_attain = QuesPaperBTAttainment.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id=qry[0]['ques_paper_id']).values('bt_level', 'minimum', 'maximum', 'bt_level__value')

                    data[0]['bt_level_attain'] = []

                    for b in bt_level_attain:
                        data[0]['bt_level_attain'].append({'bt_level': b['bt_level__value'], 'minimum': b['minimum'], 'maximum': b['maximum']})
                    data[0]['section'] = []
                    section_data = list(QuesPaperSectionDetails.objects.filter(ques_paper_id=qry[0]['ques_paper_id']).values('id', 'name', 'attempt_type', 'max_marks'))
                    data[0]['section'] = section_data

                    data = {'data': data}

            elif(requestType.custom_request_type(request.GET, 'forward_to_hod')):
                ques_paper_id = request.GET['ques_paper_id']
                qry = (QuestionPaperQuestions.objects.exclude(status="DELETE").filter(ques_paper_id=ques_paper_id).update(status='SUBMITTED'))

                data = {'data': qry}

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                subject_id = request.GET['subject_id']
                exam_id = request.GET['exam_id']
                sem = request.GET['sem']
                saved_papers = []
                papers_id_list = list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id__subject_id=subject_id, ques_paper_id__exam_id=exam_id, ques_paper_id__added_by=emp_id, status__in=['SUBMITTED', 'SAVED', 'APPROVED']).values('ques_paper_id').distinct())

                for q in papers_id_list:
                    papers_list = list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id=q['ques_paper_id']).values('ques_paper_id__time_stamp', 'ques_paper_id', 'ques_paper_id__subject_id__sub_name', 'ques_paper_id__subject_id__sub_num_code', 'ques_paper_id__exam_id__value', 'ques_paper_id__approval_status', 'status', 'ques_paper_id__subject_id__sub_alpha_code', 'ques_paper_id__status').order_by('-ques_paper_id__time_stamp'))[:1]
                    saved_papers.append(papers_list)

                data = {'data': saved_papers}

            elif(requestType.custom_request_type(request.GET, 'get_questions')):
                get_questions = list(SubjectAddQuestions.objects.filter(subject_id=request.GET['subject_id']).exclude(status='DELETE').values('type', 'description', 'question_img', 'max_marks', 'co_id__description', 'co_id', 'bt_level', 'answer_key', 'answer_img', 'id', 'co_id__co_num', 'bt_level__value', 'approval_status'))
                i = 0
                for ques in get_questions:
                    get_questions[i]['option'] = list(SubjectQuesOptions.objects.filter(ques_id=ques['id']).values('option_description', 'option_img', 'is_answer'))
                    i += 1
                data = list(get_questions)

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'get_paper')):
                data = paper_data(request, session_name)
                data = {'data': list(data)}

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            ques_paper_id = data['ques_paper_id']
            qry_sem = SubjectQuestionPaper.objects.filter(id=ques_paper_id).values('subject_id__sem')
            qry_sections = list(Sections.objects.filter(sem_id=qry_sem[0]['subject_id__sem']).values_list('section_id', flat=True))
            if check_islocked('QUES', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            qry1 = SubjectQuestionPaper.objects.filter(id=ques_paper_id).update(status="DELETE")
            qry = QuestionPaperQuestions.objects.filter(ques_paper_id=ques_paper_id).update(status="DELETE")
            data = statusMessages.MESSAGE_DELETE

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            section_id = data['section_id']
            question = data['question']
            subject_id = data['subject_id']
            exam_id = data['exam_id']
            request_status = data['request_status']
            ques_paper_id = data['ques_paper_id']
            qry_sem = SubjectInfo.objects.filter(id=subject_id).values('sem')
            qry_sections = list(Sections.objects.filter(sem_id=qry_sem[0]['sem']).values_list('section_id', flat=True))

            if check_islocked('QUES', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            ###when section is already saved#####
            qry = QuestionPaperQuestions.objects.exclude(status="DELETE").filter(ques_paper_id=ques_paper_id, section_id=section_id).update(status="DELETE")
            x = len(question)

            if ques_paper_id is None:  # when new paper is created
                query_ins = SubjectQuestionPaper.objects.create(subject_id=SubjectInfo.objects.get(id=subject_id), exam_id=StudentAcademicsDropdown.objects.get(sno=exam_id), added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
                ques_paper_id = query_ins.id
            object_insert = (QuestionPaperQuestions(ques_paper_id=SubjectQuestionPaper.objects.get(id=ques_paper_id), section_id=QuesPaperSectionDetails.objects.get(id=section_id), ques_id=SubjectAddQuestions.objects.get(id=part['id']), ques_num=i + 1) for q, i in zip(question, range(x)) for part in q)
            query_insert = QuestionPaperQuestions.objects.bulk_create(object_insert)
            data = {'id': ques_paper_id}

            if (request_status == 'SUBMIT'):
                qry = QuestionPaperQuestions.objects.exclude(status="DELETE").filter(ques_paper_id=ques_paper_id).update(status='SUBMITTED')

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST
        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def approve_question_paper(request):

    if academicCoordCheck.isAcademicHOD(request):
        emp_id = request.session['hash1']
        session_name = request.session['Session_name']
        SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
        QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
        SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_approved_papers')):
                subject_id = request.GET['subject_id'].split(',')
                exam_id = request.GET['exam_id']
                sem = request.GET['sem'].split(',')

                get_papers_id = QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id__exam_id=exam_id, ques_paper_id__subject_id__in=subject_id).values_list('ques_paper_id', flat=True)

                get_papers_list = SubjectQuestionPaper.objects.filter(id__in=get_papers_id).filter(Q(approval_status='SUBMITTED') | Q(approval_status='APPROVED') | Q(approval_status='REJECTED')).values('id', 'approval_status', 'added_by__name', 'subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'added_by__email', 'time_stamp', 'added_by', 'subject_id__sem__sem')

                data = {'data': list(get_papers_list)}

            elif(requestType.custom_request_type(request.GET, 'get_pending_papers')):
                subject_id = request.GET['subject_id'].split(',')
                exam_id = request.GET['exam_id']
                sem = request.GET['sem'].split(',')

                get_papers_id = QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id__exam_id=exam_id, ques_paper_id__subject_id__in=subject_id, status='SUBMITTED').values_list('ques_paper_id', flat=True)
                print(get_papers_id)
                get_papers_list = SubjectQuestionPaper.objects.filter(id__in=get_papers_id, approval_status='PENDING').values('id', 'approval_status', 'added_by__name', 'subject_id', 'subject_id__sub_name', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'added_by__email', 'time_stamp', 'added_by', 'subject_id__sem__sem')

                data = {'data': list(get_papers_list)}

            elif(requestType.custom_request_type(request.GET, 'get_subjects')):
                subjects = get_sem_mms_subjects(request.GET['sem'].split(','), session_name)
                data = {'data': subjects}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.PUT_REQUEST(request):
            data = json.loads(request.body)
            ques_paper_id = data['ques_paper_id']

            qry = SubjectQuestionPaper.objects.filter(id=ques_paper_id).values('exam_id', 'subject_id', 'subject_id__sem').distinct()

            sem_list = [q['subject_id__sem'] for q in qry]

            qry_sections = list(Sections.objects.filter(sem_id__in=sem_list).values_list('section_id', flat=True))

            if check_islocked('HOD', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
            qry1 = SubjectQuestionPaper.objects.filter(id=ques_paper_id).update(approval_status="PENDING")
            data = statusMessages.CUSTOM_MESSAGE('Question Paper has been rolled back')
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            ques_paper_id = data['ques_paper_id'].split(',')

            qry = SubjectQuestionPaper.objects.filter(id__in=ques_paper_id).values('exam_id', 'subject_id', 'subject_id__sem').distinct()

            sem_list = [q['subject_id__sem'] for q in qry]

            qry_sections = list(Sections.objects.filter(sem_id__in=sem_list).values_list('section_id', flat=True))

            if check_islocked('HOD', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            action = data['action']
            for q in qry:
                # qry2=SubjectQuestionPaper.objects.filter(exam_id=q['exam_id'],subject_id=q['subject_id'],approval_status="APPROVED").exclude(status="DELETE").values("approval_status")
                # if qry2:
                #   data=statusMessages.CUSTOM_MESSAGE('Question Paper of this exam and subject is already approved')
                #   return functions.RESPONSE(data,statusCodes.STATUS_CONFLICT)

                # else:
                action_qry = SubjectQuestionPaper.objects.filter(id__in=ques_paper_id).update(approval_status=action)
                # action_qry=QuestionPaperQuestions.objects.filter(ques_paper_id__in=ques_paper_id).update(status='APPROVED')
                data = statusMessages.CUSTOM_MESSAGE('Question Paper ' + action)
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def student_internal_marks(request):
    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        emp_id = request.session['hash1']
        session_name = request.session['Session_name']
        StudentMarks = generate_session_table_name("StudentMarks_", session_name)
        Marks = generate_session_table_name("Marks_", session_name)
        studentSession = generate_session_table_name("studentSession_", session_name)
        SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
        QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
        QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)
        QuesPaperBTAttainment = generate_session_table_name("QuesPaperBTAttainment_", session_name)
        QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
        SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
        SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)
        SubjectQuesOptions = generate_session_table_name("SubjectQuesOptions_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)

        if requestMethod.GET_REQUEST(request):

            if(requestType.custom_request_type(request.GET, 'papers_list')):

                exam_id = request.GET['exam_id']
                subject_id = request.GET['subject_id']
                sem = request.GET['sem']
                group_id = request.GET['group_id']

                if group_id != 'null':
                    section_id = get_group_sections(group_id, session_name)
                    isgroup = 'Y'

                else:
                    section_id = request.GET['section'].split(",")
                    isgroup = 'N'
                    group_id = None
                # if check_islocked("MMS", section_id, session_name):
                    # return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                qry_init = list(SubjectQuestionPaper.objects.filter(exam_id=exam_id, subject_id=subject_id, approval_status='APPROVED').values('exam_id__value', 'subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code'))

                if not qry_init:
                    qry1 = list(SubjectQuestionPaper.objects.filter(exam_id=exam_id, subject_id=subject_id, approval_status='PENDING').values('exam_id__value', 'subject_id__sub_name', 'subject_id__sub_num_code', 'subject_id__sub_alpha_code'))

                    if qry1:
                        data = statusMessages.CUSTOM_MESSAGE('Question Paper Has Not Been Approved Yet')

                    else:
                        data = statusMessages.CUSTOM_MESSAGE('Question Paper Not Created')

                    return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                sections = list(Sections.objects.filter(section_id__in=section_id).values('section', 'section_id'))
                final_list = []
                sem_details = list(StudentSemester.objects.filter(sem_id=sem).values('sem', 'dept__dept__value', 'dept__course__value'))

                for sec in sections:

                    section_id = sec['section_id']
                    print(section_id)
                    print(subject_id)
                    print(exam_id)
                    print(isgroup)
                    print(request.session['hash1'])
                    print("ee")
                    qry_marks_id = Marks.objects.filter(section=section_id, subject_id=subject_id, exam_id=exam_id, emp_id=request.session['hash1'], isgroup=isgroup).exclude(status='DELETE').values('id').order_by('-id')
                    if len(qry_marks_id) > 0:
                        marks_id = qry_marks_id[0]['id']
                    else:
                        marks_id = None
                    print(marks_id,'markid')

                    if isgroup == 'N':
                        students = get_section_students([section_id], {}, session_name)
                        stud = students[0]

                    else:
                        stud = get_att_group_section_students(group_id, section_id, session_name)

                    final_data = {}
                    final_data['isgroup'] = isgroup
                    final_data['exam_name'] = qry_init[0]['exam_id__value']
                    final_data['subject_name'] = qry_init[0]['subject_id__sub_name'] + '(' + qry_init[0]['subject_id__sub_alpha_code'] + '-' + qry_init[0]['subject_id__sub_num_code'] + ')'
                    final_data['course'] = sem_details[0]['dept__course__value']
                    final_data['sem'] = sem_details[0]['sem']
                    final_data['dept'] = sem_details[0]['dept__dept__value']
                    final_data['subject_id'] = subject_id
                    final_data['exam_id'] = exam_id
                    final_data['group_id'] = group_id
                    final_data['section_id'] = section_id
                    final_data['section'] = sec['section']
                    final_data['students'] = []
                    k = 0
                    if stud:
                        for student in stud:
                            marks_entered = list(StudentMarks.objects.exclude(marks_id__status="DELETE").exclude(status='DELETE').filter(uniq_id=student['uniq_id'], marks_id__exam_id=exam_id, marks_id__subject_id=subject_id, marks_id=marks_id).values('ques_id__ques_paper_id', 'present_status'))
                            if marks_entered:

                                if marks_entered[0]['present_status'] == 'D':
                                    student['isDetained'] = True

                                elif marks_entered[0]['present_status'] == 'A':
                                    student['isAbsent'] = True

                            papers = SubjectQuestionPaper.objects.exclude(status='DELETE').filter(exam_id=exam_id, subject_id=subject_id, approval_status="APPROVED").values_list('id', flat=True)

                            qp_data = {}
                            student['paper_data'] = []
                            a = 0
                            student['set_index'] = None

                            for p in papers:
                                # print(p)
                                ques_paper_id = p
                                data = {}
                                question_format = list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id=p).values('section_id', 'section_id__ques_paper_id', 'section_id__ques_paper_id__time'))
                                # qry=QuesPaperApplicableOn_1819o.objects.exclude(ques_paper_id__status='DELETE').filter(sem=sem,ques_paper_id__exam_id=exam_id).values('ques_paper_id','ques_paper_id__time')
                                total_max_marks = QuesPaperSectionDetails.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).aggregate(total_max_marks=Sum('max_marks'))
                                # data.append({'time_duration':qry[0]['ques_paper_id__time'],'Max_marks':total_max_marks.get('total_max_marks',0)})
                                data['time_duration'] = question_format[0]['section_id__ques_paper_id__time']
                                data['Max_marks'] = total_max_marks.get('total_max_marks', 0)
                                data['bt_level_attain'] = []
                                data['bt_level_attain'] = list(QuesPaperBTAttainment.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).values('minimum', 'maximum').annotate(bt_level=F('bt_level__value')))
                                data['section'] = []
                                data['paper_id'] = ques_paper_id
                                section_data = list(QuesPaperSectionDetails.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).values('id', 'name', 'attempt_type', 'max_marks','min_marks_per'))
                                # print('',section_data)
                                min_percentage = section_data[0]['min_marks_per']
                                for c in section_data:
                                    c['min_value'] = (-1)*((c['max_marks'])*(c['min_marks_per']))/100
                                data['section'] = section_data

                                for section in data['section']:
                                    ques_list = QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id=ques_paper_id, section_id=section['id']).values('ques_id', 'ques_num', 'section_id', 'id')
                                    section['question'] = []

                                    i = 0
                                    for k, v in groupby(ques_list, key=lambda x: x['ques_num']):
                                        v = list(v)
                                        id_list = []
                                        for t in v:
                                            id_list.append(t['ques_id'])

                                        qry = list(SubjectAddQuestions.objects.filter(id__in=id_list).values('description', 'question_img', 'max_marks', 'co_id__description', 'bt_level__value', 'type', 'id', 'co_id__co_num'))
                                        for q in qry:
                                            if marks_entered:
                                                if(p == marks_entered[0]['ques_id__ques_paper_id']):
                                                    student['set_index'] = a
                                                    marks_value = (StudentMarks.objects.exclude(status='DELETE').filter(uniq_id=student['uniq_id'], ques_id__ques_id=q['id'], marks_id=marks_id).values('marks', 'present_status'))

                                                    if not marks_value:
                                                        marks = None

                                                    else:
                                                        marks = marks_value[0]['marks']
                                                else:
                                                    marks = None
                                                q['marks_obtained'] = marks
                                            else:
                                                q['marks_obtained'] = None
                                            q['min_marks_ques'] = ((-1)*(min_percentage)*(q['max_marks']))/100
                                            if q['type'] == 'O':
                                                q['option'] = list(SubjectQuesOptions.objects.filter(ques_id=q['id']).values('option_description', 'option_img', 'is_answer'))

                                        section['question'].append(qry)
                                a += 1
                                student['paper_data'].append(data)
                            final_data['students'].append(student)
                        final_list.append(final_data)
                data = {'data': final_list}

        elif requestMethod.POST_REQUEST(request):    
            body = json.loads(request.body)
            data = body['on_submit']
            sessionid=request.META['HTTP_COOKIE']
            subject_id=data[0]['subject_id']
            Section_id=data[0]['section_id']
            sem=data[0]['sem']
            dept_id=Sections.objects.filter(section_id=Section_id).values('dept')[0]['dept']
            for group in data:
                #######################LOCKING STARTS######################
                # section_li=list(Sections.objects.filter(sem_id=sem).values_list('section_id',flat=True))
                # if check_islocked("MMS", [group['section_id']], session_name):
                    # return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    ####################LOCKING ENDS##############################
                qry_filter = {'section': group['section_id'], 'subject_id': group['subject_id'], 'exam_id': group['exam_id']}

                if group['isgroup'] != 'N':
                    qry_filter['group_id'] = group['group_id']
                    qry_create = {'section': Sections.objects.get(section_id=group['section_id']), 'subject_id': SubjectInfo.objects.get(id=group['subject_id']), 'exam_id': StudentAcademicsDropdown.objects.get(sno=group['exam_id']), 'emp_id': EmployeePrimdetail.objects.get(emp_id=emp_id), 'isgroup': group['isgroup'], 'group_id': SectionGroupDetails.objects.get(id=group['group_id'])}
                else:

                    qry_create = {'section': Sections.objects.get(section_id=group['section_id']), 'subject_id': SubjectInfo.objects.get(id=group['subject_id']), 'exam_id': StudentAcademicsDropdown.objects.get(sno=group['exam_id']), 'emp_id': EmployeePrimdetail.objects.get(emp_id=emp_id), 'isgroup': group['isgroup']}

                group_marks = list(Marks.objects.exclude(status='DELETE').filter(**qry_filter).values('id'))

                if not group_marks:
                    group_marks_qry = Marks.objects.create(**qry_create)
                    group_marks = group_marks_qry.id

                else:
                    group_marks = group_marks[0]['id']

                for student in group['students']:
                    set_index = student['set_index']
                    present_status = 'P'

                    if 'isDetained' in student:
                        if student['isDetained'] == True:
                            set_index = 0
                            present_status = 'D'

                    if 'isAbsent' in student:
                        if student['isAbsent'] == True:
                            present_status = 'A'
                            set_index = 0

                    if 'isUpdated' in student:
                        status = 'UPDATE'

                    else:
                        status = 'INSERT'

                    if set_index is not None:

                        section = student['paper_data'][set_index]['section']
                        for sec in section:
                            for ques in sec['question']:
                                for q in ques:

                                    if q['marks_obtained'] is not None:

                                        q['marks_obt'] = str(q['marks_obtained'])
                                        if q['marks_obt'] == '':
                                            q['marks_obt'] = None

                                    else:
                                        q['marks_obt'] = None

                        StudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=group['exam_id'], marks_id__subject_id=group['subject_id'], uniq_id=student['uniq_id']).update(status='DELETE')

                        objs = (StudentMarks(marks_id=Marks.objects.get(id=group_marks), uniq_id=studentSession.objects.get(uniq_id=student['uniq_id']), marks=(q['marks_obt']), ques_id=QuestionPaperQuestions.objects.exclude(status='DELETE').get(ques_paper_id=student['paper_data'][set_index]['paper_id'], section_id=sec['id'], ques_id=q['id']), status=status, present_status=present_status) for sec in section for ques in sec['question'] for q in ques)

                        enter_marks = StudentMarks.objects.bulk_create(objs)

                        if enter_marks:

                            data = statusMessages.MESSAGE_INSERT
            call_store_ctwise_marks.delay(sessionid,subject_id,Section_id,dept_id,sem) #call celery function for entry of data in store
    
        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def bonus_marks_rule(request):
    if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:

        session_name = request.session['Session_name']
        BonusMarksRule = generate_session_table_name("BonusMarksRule_", session_name)

        if requestMethod.POST_REQUEST(request):
            body = json.loads(request.body)
            qry_sections = list(Sections.objects.values_list('section_id', flat=True))

            if check_islocked('DMS', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            data = body['on_submit']

            query_create = False
            sem_id = StudentSemester.objects.filter(sem__in=data[0]['sem'].split(","), dept__in=data[0]['dept'].split(",")).values_list('sem_id', flat=True)
            q = BonusMarksRule.objects.filter(sem__in=sem_id, subject_type__in=data[0]['sub_type']).update(status='DELETE')

            for d in data:

                if len(d['selectedExam']) == 0:
                    d['selectedExam'] = None
                    q1 = (BonusMarksRule(rule_name=d['Rule_name'], sem=StudentSemester.objects.get(sem_id=s), subject_type=StudentDropdown.objects.get(sno=stype), min_marks_per=d['min_marks_per'], max_marks_limit_per=d['max_marks_per'], bonus_marks=d['bonus_marks']) for s in sem_id for stype in d['sub_type'])

                    q2 = BonusMarksRule.objects.bulk_create(q1)
                else:
                    data1 = []
                    data1 = d['selectedExam']
                    create_object = (BonusMarksRule(rule_name=d['Rule_name'], sem=StudentSemester.objects.get(sem_id=s), given_ct=','.join(map(str, data1)), subject_type=StudentDropdown.objects.get(sno=stype), min_marks_per=d['min_marks_per'], max_marks_limit_per=d['max_marks_per'], bonus_marks=d['bonus_marks']) for s in sem_id for stype in d['sub_type'])

                    query_create = BonusMarksRule.objects.bulk_create(create_object)
            if query_create or q2:
                data = body['on_submit']
            data = statusMessages.MESSAGE_INSERT

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'view_previous')):
                # sem=request.GET['sem'].split(",")
                # subject_type=request.GET['sub_type'].split(",")
                # dept=request.GET['dept'].split(",")
                rule_id = list(BonusMarksRule.objects.exclude(status='DELETE').values('id', 'sem__dept__dept__value', 'sem__dept__course__value', 'subject_type__value', 'sem__sem', 'rule_name', 'sem__dept', 'sem__dept__course', 'subject_type', 'sem'))
                data = rule_id

            elif(requestType.custom_request_type(request.GET, 'view_rule')):
                rule_id = request.GET['rule_id']
                selectedExam = []
                rule_format = list(BonusMarksRule.objects.exclude(status='DELETE').filter(id=rule_id).values('id', 'rule_name', 'given_ct', 'min_marks_per', 'min_att_per', 'bonus_marks', 'max_marks_limit_per'))
                if rule_format[0]['given_ct'] == None:
                    rule_format[0]['given_ct'] = ""
                i = [int(e) if e.isdigit() else e for e in rule_format[0]['given_ct'].split(',')]
                rule_format[0]['given_ct'] = i
                data = rule_format

            elif(requestType.custom_request_type(request.GET, 'delete')):
                qry_sections = list(Sections.objects.values_list('section_id', flat=True))

                if check_islocked('DMS', qry_sections, session_name):
                    return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                BonusMarksRule.objects.filter(id=request.GET['rule_id']).update(status="DELETE")
                data = statusMessages.MESSAGE_DELETE

        elif requestMethod.PUT_REQUEST(request):
            qry_sections = list(Sections.objects.values_list('section_id', flat=True))

            if check_islocked('DMS', qry_sections, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

            body = json.loads(request.body)
            data = body['on_submit']
            rule_id = data['rule_id']
            if len(data['selectedExam']) == 0:
                qry = BonusMarksRule.objects.filter(id=rule_id).update(rule_name=data['Rule_name'], min_marks_per=data['min_marks_per'], max_marks_limit_per=data['max_marks_per'], bonus_marks=data['bonus_marks'], min_att_per=data['min_att_per'])
            else:
                qry = BonusMarksRule.objects.filter(id=rule_id).update(rule_name=data['Rule_name'], given_ct=','.join(map(str, data['selectedExam'])), min_marks_per=data['min_marks_per'], max_marks_limit_per=data['max_marks_per'], bonus_marks=data['bonus_marks'], min_att_per=data['min_att_per'])
            if qry:
                data = statusMessages.MESSAGE_UPDATE

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def enter_ta_marks(request):

    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:

        session_name = request.session['Session_name']
        emp_id = request.session['hash1']

        TAMarks = generate_session_table_name("TAMarks_", session_name)
        StudentTAMarks = generate_session_table_name("StudentTAMarks_", session_name)
        StudentMarks = generate_session_table_name("StudentMarks_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)
        studentSession = generate_session_table_name("studentSession_", session_name)

        if requestMethod.GET_REQUEST(request):
            data = []
            if(requestType.custom_request_type(request.GET, 'get_student_list')):
                subject_id = request.GET['subject_id']
                sem = request.GET['sem']
                group_id = request.GET['group_id']

                if group_id != 'null':
                    section_ids = get_group_sections(group_id, session_name)
                    students = []
                    for section_id in section_ids:
                        students.extend(get_att_group_section_students(group_id, section_id, session_name))
                else:
                    section_ids = [request.GET['section_id']]
                    student = get_section_students(section_ids, {}, session_name)
                    students = student[0]

                qry_filter = {'section__in': section_ids, 'subject_id': subject_id}

                if group_id != 'null':
                    qry_filter['group_id'] = group_id

                marks_id = list(TAMarks.objects.exclude(status='DELETE').filter(**qry_filter).values_list('id', flat=True))

                max_ta_marks = list(SubjectInfo.objects.filter(id=subject_id).values('max_ct_marks', 'max_ta_marks', 'sub_name', 'sub_alpha_code', 'sub_num_code'))
                subject_name = max_ta_marks[0]['sub_name'] + '(' + max_ta_marks[0]['sub_alpha_code'] + '-' + max_ta_marks[0]['sub_num_code'] + ')'
                data.append({'subject_name': subject_name, 'max_ta_lab_marks': max_ta_marks[0]['max_ta_marks'], 'max_viva_marks': max_ta_marks[0]['max_ct_marks']})
                for stud in students:
                    stud['ta_lab_marks'] = None
                    stud['ct_viva_marks'] = None
                    if marks_id:
                        marks = list(StudentTAMarks.objects.filter(uniq_id=stud['uniq_id'], ta_marks_id__in=marks_id, status="INSERT").exclude(status="DELETE").values('ct_viva_marks', 'ta_lab_marks'))
                        if marks:
                            stud['ta_lab_marks'] = marks[-1]['ta_lab_marks']
                            stud['ct_viva_marks'] = marks[-1]['ct_viva_marks']

                data[0]['students'] = students

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            group_id = data[0]['group_id']
            subject_id = data[0]['subject_id']
            emp_id = request.session['hash1']
            qry_filter = {'subject_id': subject_id, 'emp_id': emp_id}
            if group_id is not None:

                qry_filter['group_id'] = group_id
                section_ids = get_group_sections(group_id, session_name)
                isgroup = 'Y'

            else:
                section_id = data[0]['section_id']
                section_ids = []
                section_ids.append(section_id)
                group_id = None
                isgroup = 'N'

            #######################LOCKING STARTS######################
            # section_li=list(Sections.objects.filter(sem_id=sem).values_list('section_id',flat=True))
            if check_islocked("MMS", section_ids, session_name):
                return functions.RESPONSE(statusMessages.MESSAGE_PORTAL_LOCKED, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                ####################LOCKING ENDS##############################

            qry_filter['section_id__in'] = section_ids
            qry_filter['isgroup'] = isgroup

            qry = list(TAMarks.objects.exclude(status='DELETE').filter(**qry_filter).values_list('id', flat=True))

            qry_update = TAMarks.objects.filter(id__in=qry).update(status='DELETE')
            qry_update2 = StudentTAMarks.objects.filter(ta_marks_id__in=qry).update(status='DELETE')

            marks = []
            for section_id in section_ids:
                if isgroup == 'Y':
                    qry1 = TAMarks.objects.create(section=Sections.objects.get(section_id=section_id), subject_id=SubjectInfo.objects.get(id=subject_id), group_id=SectionGroupDetails.objects.get(id=group_id), emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), isgroup=isgroup)
                    marks.append({'id': qry1.id, 'section_id': section_id})
                else:
                    qry1 = TAMarks.objects.create(section=Sections.objects.get(section_id=section_id), subject_id=SubjectInfo.objects.get(id=subject_id), emp_id=EmployeePrimdetail.objects.get(emp_id=emp_id), isgroup=isgroup)
                    marks.append({'id': qry1.id, 'section_id': section_id})

            status = 'INSERT'

            for stud in data[0]['students']:
                for mark in marks:
                    if stud['section'] == mark['section_id']:
                        status = 'INSERT'

                        create_query = StudentTAMarks.objects.create(ta_marks_id=TAMarks.objects.get(id=mark['id']), uniq_id=studentSession.objects.get(uniq_id=stud['uniq_id']), ct_viva_marks=stud['ct_viva_marks'], ta_lab_marks=stud['ta_lab_marks'], status=status)
                        # if (stud['ct_viva_marks'] is None ) and stud['ta_lab_marks'] is None:
                        #   pass
                        # else:
                        #   status='INSERT'

                        #   create_query=StudentTAMarks.objects.create(ta_marks_id=TAMarks.objects.get(id=mark['id']),uniq_id=studentSession.objects.get(uniq_id=stud['uniq_id']),ct_viva_marks=stud['ct_viva_marks'],ta_lab_marks=stud['ta_lab_marks'],status=status)
                        break

            data = statusMessages.MESSAGE_INSERT

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def student_internal_marks_function(request):

    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        session = request.session['Session_id']
        session_name = request.session['Session_name']
        emp_id = request.session['hash1']

        TAMarks = generate_session_table_name("TAMarks_", session_name)
        StudentTAMarks = generate_session_table_name("StudentTAMarks_", session_name)
        StudentMarks = generate_session_table_name("StudentMarks_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        FacultyTime = generate_session_table_name("FacultyTime_", session_name)
        BonusMarksRule = generate_session_table_name("BonusMarksRule_", session_name)
        QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
        SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
        QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
        QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)

        if requestMethod.GET_REQUEST(request):
            section_id = request.GET['section_id']
            group_id = request.GET['group_id']
            subjects = request.GET['subject_id'].split(",")
            sem_id = request.GET['sem_id']

            data = []
            data.append({})

            if group_id != 'null':
                students = get_att_group_section_students(group_id, section_id, session_name)
            else:
                student = get_section_students([section_id], {}, session_name)
                students = student[0]

            subject_id = list(SubjectInfo.objects.exclude(subject_type__value='LAB').exclude(subject_type__value='VALUE ADDED COURSE').filter(id__in=subjects).values('id', 'sub_name', 'sub_alpha_code', 'sub_num_code').annotate(ids=F('id')))

            data[0]['subject_list'] = []
            i = 0
            for s in subject_id:
                data[0]['subject_list'].append({})
                subject_name = s['sub_name'] + '(' + s['sub_alpha_code'] + '-' + s['sub_num_code'] + ')'
                data[0]['subject_list'][i]['subject_details'] = []
                data[0]['subject_list'][i]['subject_details'].append({'Subject_name': subject_name, 'subject_id': s['ids']})
                data[0]['subject_list'][i]['student_list'] = []
                k = 0
                exams = list(SubjectQuestionPaper.objects.exclude(status='DELETE').filter(subject_id=s['ids']).values('exam_id', 'exam_id__value').distinct())
                student_list = []
                for stud in students:
                    e = 0
                    ct_group = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP', session=session).values('value', 'sno'))[0]['value']
                    max_exam_marks = list(SubjectInfo.objects.filter(id=s['ids']).values('max_ct_marks'))[0]['max_ct_marks']
                    pointer_per_exam = (max_exam_marks / float(ct_group))
                    ct_marks = []

                    for exam in exams:
                        marks_obtained = StudentMarks.objects.exclude(status='DELETE').exclude(marks_id__status='DELETE').filter(uniq_id=stud['uniq_id'], marks_id__subject_id=s['ids'], marks_id__exam_id=exam['exam_id']).aggregate(marks_obtained=Sum('marks'))

                        marks_obt = marks_obtained.get('marks_obtained', 0)

                        format_id = list(QuesPaperApplicableOn.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id__exam_id=exam['exam_id'], sem=sem_id).values('ques_paper_id'))

                        max_marks = QuesPaperSectionDetails.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id=format_id[0]['ques_paper_id']).aggregate(total_marks=Sum('max_marks'))
                        total_exam_marks = max_marks.get('total_marks', 0)
                        divisor = total_exam_marks / pointer_per_exam

                        if marks_obt is not None:
                            exam_pointer = math.ceil(marks_obt / divisor)
                        else:
                            exam_pointer = None

                        ct_marks.append({'exam_name': exam['exam_id__value'], 'marks_obtained': exam_pointer, 'maximum_marks': pointer_per_exam})

                    student_list.append({'uniq_id': stud['uniq_id'], 'uniq_id__name': stud['uniq_id__name'], 'section': stud['section__section'], 'class_roll_no': stud['class_roll_no'], 'university_roll_no': stud['uniq_id__uni_roll_no'], 'father_name': stud['fname'], 'ct_marks': ct_marks})

                data[0]['subject_list'][i]['student_list'] = student_list
                # best ct marks,attendance marks and bonus marks is remaining

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


####################### SATYAM INTERNAL MARKSHEET REQUEST ########################

# def student_marksheet(request):

#   if checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
#       session=request.session['Session_id']
#       session_name=request.session['Session_name']
#       emp_id=request.session['hash1']

#       TAMarks = generate_session_table_name("TAMarks_",session_name)
#       StudentTAMarks = generate_session_table_name("StudentTAMarks_",session_name)
#       StudentMarks = generate_session_table_name("StudentMarks_",session_name)
#       SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)
#       FacultyTime=generate_session_table_name("FacultyTime_",session_name)
#       BonusMarksRule = generate_session_table_name("BonusMarksRule_",session_name)
#       QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_",session_name)
#       SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_",session_name)
#       QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_",session_name)
#       QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_",session_name)

#       if requestMethod.GET_REQUEST(request):
#           if (requestType.custom_request_type(request.GET,'subjects')):
#               dept=request.GET['dept']
#               sem=request.GET['sem']
#               section=request.GET['section'].split(',')
#               section_id=Sections.objects.filter(section__in=section,dept=dept,sem_id__sem=sem).values_list('section_id',flat=True)
#               sem_id=list(Sections.objects.filter(section_id__in=section_id).values_list('sem_id',flat=True).distinct())
#               data=get_subjects_hod_dean(sem_id,session_name,[])
#               return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

#           elif (requestType.custom_request_type(request.GET,'faculty_subjects')):
#               sem=request.GET['sem']
#               dept=request.GET['dept']
#               section=request.GET['section'].split(',')
#               section_id=list(Sections.objects.filter(section__in=section,dept=dept,sem_id__sem=sem).values_list('section_id',flat=True))
#               data=get_subjects_faculty(emp_id,section_id,session_name,[])
#               return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

#           elif (requestType.reportData(request.GET)):
#               data=[]
#               filters={}

#               session_num = int(session_name[:2])

#               sem=request.GET['sem']
#               dept=request.GET['dept']
#               if 'section' in request.GET:
#                   section_id=request.GET['section'].split(',')
#               subjects=request.GET['subject_id'].split(',')
#               if 'group_id' in request.GET:
#                   group_id=request.GET['group_id']
#               else:
#                   group_id=None
#               if 'type' in request.GET:
#                   group_type=request.GET['type']
#               else:
#                   group_type=None

#               subject_type=request.GET['subject_type']

#               sem_detail=(StudentSemester.objects.filter(sem=sem,dept=dept).values('sem_id'))
#               sem_id=sem_detail[0]['sem_id']

#               exams_conducted = (SubjectQuestionPaper.objects.exclude(status='DELETE').filter(subject_id__sem=sem_id,subject_id__sem__dept=dept).values('exam_id','exam_id__value').distinct().order_by('exam_id'))
#               subject_columns = []
#               for exam in exams_conducted:
#                   subject_columns.append(exam['exam_id__value'])

#               subject_columns.append('CT Marks')
#               subject_columns.append('Teacher Assessment')
#               subject_columns.append('Attendance %')
#               subject_columns.append('Attendance Marks')
#               subject_columns.append('Total Marks')
#               qry_bonus_rules = BonusMarksRule.objects.filter(subject_type=subject_type,sem=sem_id).exclude(status='DELETE').values('rule_name')

#               for bonus in qry_bonus_rules:
#                   subject_columns.append(bonus['rule_name'])
#               subject_columns.append("EXTRA BONUS")
#               subject_columns.append('Final Marks')

#               students=[]
#               # student=get_section_students(section_id,{},session_name)
#               if group_id is not None and group_type is not None:
#                   if group_type == 1:
#                       student=get_att_group_section_students(group_id,section_id,session_name)
#                       for stud in student:
#                           students.extend(stud)
#                   else:
#                       students=get_att_group_section_students(group_id,[],session_name)
#               else:
#                   student=get_section_students(section_id,{},session_name)
#                   for stud in student:
#                       students.extend(stud)
#               subject_details=list(SubjectInfo.objects.filter(id__in=subjects).values('max_ct_marks','max_ta_marks','sub_name','sub_alpha_code','sub_num_code','id','max_att_marks','subject_type','sem'))

#               ct_group=list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP',session=session).values('value','sno'))[0]['value']

#               for stu in students:
#                   student_marks=[]
#                   for subject in subject_details:
#                       total_sub_marks = subject['max_ct_marks']+subject['max_ta_marks']+subject['max_att_marks']

#                       subject_column_data=[]
#                       given_marks_dict = {}
#                       given_max_marks_dict = {}
#                       for exam in exams_conducted:

#                           ### CHANGE FOR RULES ###
#                           ######################################################################
#                           if session_num < 19:
#                               marks = get_student_marks(stu['uniq_id'], session_name, subject['id'], exam['exam_id'], subject['max_ct_marks'], ct_group, sem_id)
#                           else:
#                               marks = get_student_marks_new([stu['uniq_id']], [subject['id']], [exam['exam_id']], sem_id, session_name, 0, {})
#                               print(marks, '19')
#                           #######################################################################
#                           ### END ###
#                           converted_marks =  marks['converted_marks']
#                           subject_column_data.append(converted_marks)

#                           if not isinstance(converted_marks,str) and not isinstance(converted_marks,str):
#                               given_marks_dict[str(exam['exam_id'])] = marks['marks_obtained']
#                               given_max_marks_dict[str(exam['exam_id'])] = marks['total_marks']

#                       ### CHANGE FOR RULES ###
#                       ###################################################
#                       if session_num < 19:
#                           student_sub_ct_marks = get_student_subject_ct_marks(stu['uniq_id'], session_name, subject['id'], subject['subject_type'], subject['max_ct_marks'], subject['sem'])
#                       else:
#                           student_sub_ct_marks = get_student_marks_new([stu['uniq_id']], [subject['id']], exam['exam_id'], sem_id, session_name, 1, {})['total_ct_marks']
#                           print(student_sub_ct_marks, 'student_sub_ct_marks')
#                       ###################################################
#                       ### END ###

#                       ######## CT MARKS ##################
#                       subject_column_data.append(student_sub_ct_marks)

#                       ta_marks = get_student_subject_ta_marks(stu['uniq_id'],session_name,subject['id'])
#                       if ta_marks!='N/A':
#                           ta_marks = math.ceil(float(ta_marks))
#                       subject_att_marks = get_student_subject_att_marks(stu['uniq_id'],session_name,subject['id'],subject['subject_type'],subject['sem'],subject['max_att_marks'])
#                       ####### TA MARKS ####################
#                       subject_column_data.append(ta_marks)
#                       ####### ATTENDANCE % ################
#                       subject_column_data.append(subject_att_marks['att_per'])
#                       ####### ATTENDANCE MARKS ############
#                       subject_column_data.append(subject_att_marks['att_marks'])

#                       total_marks=0
#                       if not isinstance(student_sub_ct_marks, str) and not isinstance(student_sub_ct_marks,str):
#                           total_marks+=student_sub_ct_marks

#                       if not isinstance(subject_att_marks['att_marks'], str) and not isinstance(subject_att_marks['att_marks'],str):
#                           total_marks+=subject_att_marks['att_marks']

#                       if not isinstance(ta_marks, str) and not isinstance(ta_marks,str):
#                           total_marks+=ta_marks

#                       ######## TOTAL MARKS ##############
#                       subject_column_data.append(total_marks)

#                       ############# BONUS RULE ####################

#                       max_marks = float(subject['max_att_marks'])+float(subject['max_ct_marks'])+float(subject['max_ta_marks'])

#                       bonus_marks_data = get_student_subject_bonus_marks(stu['uniq_id'],given_marks_dict,given_max_marks_dict,session_name,subject['subject_type'],sem_id,subject_att_marks['att_per'],total_marks,max_marks)
#                       total_marks = bonus_marks_data['marks_obtained']

#                       extra_bonus_marks = get_student_subject_extra_bonus_marks(stu['uniq_id'],subject['id'],session_name)

#                       total_marks+=extra_bonus_marks

#                       total_marks=min(total_sub_marks,total_marks)

#                       subject_column_data.extend(bonus_marks_data['rule_data'])
#                       subject_column_data.append(extra_bonus_marks)
#                       subject_column_data.append(total_marks)
#                       subject_column_data.append(subject['max_ct_marks'])
#                       subject_column_data.append(subject['max_ta_marks'])
#                       subject_column_data.append(subject['max_att_marks'])

#                       ############ STUDENT SUBJECT MARKS DATA ######

#                       student_marks.append(subject_column_data)

#                   stu['marks_data'] = student_marks


#               data = {'subject_columns':subject_columns,'subject_details':list(subject_details),'students_data':students}

#               return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

#       else:
#           data=statusMessages.MESSAGE_BAD_REQUEST

#       return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

#   else:
#       return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def student_marksheet(request):

    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        session = request.session['Session_id']
        session_name = request.session['Session_name']
        emp_id = request.session['hash1']

        TAMarks = generate_session_table_name("TAMarks_", session_name)
        StudentTAMarks = generate_session_table_name("StudentTAMarks_", session_name)
        StudentMarks = generate_session_table_name("StudentMarks_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        FacultyTime = generate_session_table_name("FacultyTime_", session_name)
        QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
        SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
        QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
        QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)

        if session>19:
            BonusMarksRule = generate_session_table_name("BonusMarksRule_", session_name)

        if requestMethod.GET_REQUEST(request):
            if (requestType.custom_request_type(request.GET, 'subjects')):
                dept = request.GET['dept']
                sem = request.GET['sem']
                section = request.GET['section'].split(',')
                section_id = Sections.objects.filter(section__in=section, dept=dept, sem_id__sem=sem).values_list('section_id', flat=True)
                sem_id = list(Sections.objects.filter(section_id__in=section_id).values_list('sem_id', flat=True).distinct())
                data = get_subjects_hod_dean(sem_id, session_name, [])
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif (requestType.custom_request_type(request.GET, 'faculty_subjects')):
                sem = request.GET['sem']
                dept = request.GET['dept']
                section = request.GET['section'].split(',')
                section_id = list(Sections.objects.filter(section__in=section, dept=dept, sem_id__sem=sem).values_list('section_id', flat=True))
                data = get_subjects_faculty(emp_id, section_id, session_name, [])
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif (requestType.reportData(request.GET)):
                data = []
                filters = {}

                session_num = int(session_name[:2])

                sem = request.GET['sem']
                dept = request.GET['dept']
                if 'section' in request.GET:
                    section_id = request.GET['section'].split(',')
                subjects = request.GET['subject_id'].split(',')
                if 'group_id' in request.GET:
                    group_id = request.GET['group_id']
                else:
                    group_id = None
                if 'type' in request.GET:
                    group_type = request.GET['type']
                else:
                    group_type = None

                subject_type = request.GET['subject_type']

                sem_detail = (StudentSemester.objects.filter(sem=sem, dept=dept).values('sem_id'))
                sem_id = sem_detail[0]['sem_id']

                exams_conducted = (SubjectQuestionPaper.objects.exclude(status='DELETE').filter(subject_id__sem=sem_id, subject_id__sem__dept=dept).values('exam_id', 'exam_id__value').distinct().order_by('exam_id'))
                subject_columns = []
                for exam in exams_conducted:
                    subject_columns.append(exam['exam_id__value'])

                subject_columns.append('CT Marks')
                subject_columns.append('Teacher Assessment')
                subject_columns.append('Attendance %')
                subject_columns.append('Attendance Marks')
                subject_columns.append('Total Marks')

                #### GET STUDENTS ####
                students = []
                stu_uniq_ids = []

                if group_id is not None and group_type is not None:
                    if group_type == 1:
                        student = get_att_group_section_students(group_id, section_id, session_name)
                        for stud in student:
                            students.extend(stud)
                    else:
                        students = get_att_group_section_students(group_id, [], session_name)
                    for stu in students:
                        stu_uniq_ids.append(stu['uniq_id'])
                else:
                    student = get_section_students(section_id, {}, session_name)
                    for stud in student:
                        students.extend(stud)
                        for stu in stud:
                            stu_uniq_ids.append(stu['uniq_id'])
                ######################
                subject_details = list(SubjectInfo.objects.filter(id__in=subjects).values('max_ct_marks', 'max_ta_marks', 'sub_name', 'sub_alpha_code', 'sub_num_code', 'id', 'max_att_marks', 'subject_type', 'sem'))
                ct_group = list(StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='CT GROUP', session=session).values('value', 'sno'))[0]['value']

                # # #### BONUS RULES CHANGES ####
                # if session_num < 19:
                #   qry_bonus_rules = BonusMarksRule.objects.filter(subject_type=subject_type, sem=sem_id).exclude(status='DELETE').values('rule_name')
                #   for bonus in qry_bonus_rules:
                #       subject_columns.append(bonus['rule_name'])
                # if session_num >= 19:
                #   bonus_marks_data = fetch_bonus_marks(students, subject_details, sem_id, session_name)
                #   print(subject_details)
                #   att_data = get_student_subject_att_marks_new(stu_uniq_ids, session_name, subject_type, sem_id, subject_details[0]['max_att_marks'])
                #   print(att_data)
                # # #############################
                #### BONUS RULES CHANGES ####
                if session_num < 19:
                    qry_bonus_rules = BonusMarksRule.objects.filter(subject_type=subject_type, sem=sem_id).exclude(status='DELETE').values('rule_name')
                    for bonus in qry_bonus_rules:
                        subject_columns.append(bonus['rule_name'])
                if session_num >= 19:
                    bonus_marks_data = fetch_bonus_marks(students, subject_details, sem_id, session_name)
                    att_data = {}
                    for stu in stu_uniq_ids:
                        att_data[stu] = {}
                    for subject in subject_details:
                        sub_att_data = get_student_subject_att_marks_new(stu_uniq_ids, session_name, subject_type, sem_id, subject['max_att_marks'])
                        for each in stu_uniq_ids:
                            att_data[each][subject['id']] = {}
                            if subject['id'] in sub_att_data[each]:
                                att_data[each][subject['id']] = sub_att_data[each][subject['id']]
                            else:
                                att_data[each][subject['id']]['att_marks'] = 'Rule Not Defined for this attendance percentage'
                                att_data[each][subject['id']]['att_per'] = 0

                #############################

                flag = 0
                for stu in students:
                    student_marks = []
                    for subject in subject_details:

                        total_sub_marks = subject['max_ct_marks'] + subject['max_ta_marks'] + subject['max_att_marks']

                        subject_column_data = []
                        given_marks_dict = {}
                        given_max_marks_dict = {}
                        for exam in exams_conducted:

                            ### CHANGE FOR RULES ###
                            ######################################################################
                            if session_num < 19:
                                marks = get_student_marks(stu['uniq_id'], session_name, subject['id'], exam['exam_id'], subject['max_ct_marks'], ct_group, sem_id)
                            else:
                                marks = get_student_marks_new([stu['uniq_id']], [subject['id']], [exam['exam_id']], sem_id, session_name, 0, {})
                            #######################################################################
                            ### END ###

                            converted_marks = marks['converted_marks']
                            subject_column_data.append(converted_marks)

                            if not isinstance(converted_marks, str) and not isinstance(converted_marks, str):
                                given_marks_dict[str(exam['exam_id'])] = marks['marks_obtained']
                                given_max_marks_dict[str(exam['exam_id'])] = marks['total_marks']

                        ### CHANGE FOR RULES ###
                        ###################################################
                        if session_num < 19:
                            student_sub_ct_marks = get_student_subject_ct_marks(stu['uniq_id'], session_name, subject['id'], subject['subject_type'], subject['max_ct_marks'], subject['sem'])
                        else:
                            student_sub_ct_marks = get_student_marks_new([stu['uniq_id']], [subject['id']], exam['exam_id'], sem_id, session_name, 1, {})['total_ct_marks']
                        ###################################################
                        ### END ###

                        ######## CT MARKS ##################
                        subject_column_data.append(student_sub_ct_marks)

                        ta_marks = get_student_subject_ta_marks(stu['uniq_id'], session_name, subject['id'])
                        if ta_marks != 'N/A':
                            ta_marks = math.ceil(float(ta_marks))

                        ################ ATTENDANCE MARKS #################
                        if session_num < 19:
                            subject_att_marks = get_student_subject_att_marks(stu['uniq_id'], session_name, subject['id'], subject['subject_type'], subject['sem'], subject['max_att_marks'])
                        else:
                            subject_att_marks = {'att_marks': 'N/A', 'att_per': 0}
                            if stu['uniq_id'] in att_data:
                                if subject['id'] in att_data[stu['uniq_id']]:
                                    subject_att_marks = att_data[stu['uniq_id']][subject['id']]
                        ###################################################
                        ####### TA MARKS ####################
                        subject_column_data.append(ta_marks)
                        ####### ATTENDANCE % ################
                        subject_column_data.append(subject_att_marks['att_per'])
                        ####### ATTENDANCE MARKS ############
                        subject_column_data.append(subject_att_marks['att_marks'])

                        total_marks = 0
                        if not isinstance(student_sub_ct_marks, str):
                            total_marks += student_sub_ct_marks

                        if not isinstance(subject_att_marks['att_marks'], str):
                            total_marks += subject_att_marks['att_marks']

                        if not isinstance(ta_marks, str) and not isinstance(ta_marks, str):
                            total_marks += ta_marks

                        ######## TOTAL MARKS ##############
                        subject_column_data.append(total_marks)

                        ############ CHANGES ####################
                        ############# BONUS RULE ####################
                        max_marks = float(subject['max_att_marks']) + float(subject['max_ct_marks']) + float(subject['max_ta_marks'])

                        if session_num < 19:
                            bonus_marks_data = get_student_subject_bonus_marks(stu['uniq_id'], given_marks_dict, given_max_marks_dict, session_name, subject['subject_type'], sem_id, subject_att_marks['att_per'], total_marks, max_marks)
                            total_marks = bonus_marks_data['marks_obtained']
                            subject_column_data.extend(bonus_marks_data['rule_data'])

                        else:
                            if stu['uniq_id'] in bonus_marks_data:
                                if subject['id'] in bonus_marks_data[stu['uniq_id']]:
                                    subject_column_data.extend(bonus_marks_data[stu['uniq_id']][subject['id']]['rule_data'])

                                    for bonus in bonus_marks_data[stu['uniq_id']][subject['id']]['rule_data']:
                                        try:
                                            bonus = float(bonus)
                                        except:
                                            bonus = 0
                                        total_marks += float(bonus)
                                    l = len(bonus_marks_data[stu['uniq_id']][subject['id']]['rule_data'])

                                    if flag == 0:
                                        for i in range(1, int(l) + 1):
                                            subject_columns.append('Rule ' + str(i))
                                            i += 1
                                        flag = 1
                        #############################################

                        extra_bonus_marks = get_student_subject_extra_bonus_marks(stu['uniq_id'], subject['id'], session_name)
                        total_marks += extra_bonus_marks

                        total_marks = min(total_sub_marks, total_marks)

                        subject_column_data.append(extra_bonus_marks)
                        subject_column_data.append(total_marks)
                        subject_column_data.append(extra_bonus_marks)
                        subject_column_data.append(subject['max_ct_marks'])
                        subject_column_data.append(subject['max_ta_marks'])
                        subject_column_data.append(subject['max_att_marks'])

                        ############ STUDENT SUBJECT MARKS DATA ######

                        student_marks.append(subject_column_data)
                    stu['marks_data'] = student_marks

                subject_columns.append("EXTRA BONUS")
                subject_columns.append('Final Marks')
                data = {'subject_columns': subject_columns, 'subject_details': list(subject_details), 'students_data': students}

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
