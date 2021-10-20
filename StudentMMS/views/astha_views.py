from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
from login.views import checkpermission, generate_session_table_name
import json
from .mms_function_views import get_btlevel, get_skillsetlevel, get_verb, get_skillsetlevel_filtered, get_btleveldata, get_CO_subject, get_co, get_po, get_co_list, get_max_marks, get_coordinator_sem, get_exam_name, get_sem_mms_subjects, get_subjects_hod_dean, get_subjects_faculty, get_student_marks, get_student_subject_ct_marks, get_student_subject_ta_marks, get_student_subject_att_marks, get_student_subject_bonus_marks, get_student_subject_extra_bonus_marks, get_batch_dropdown, get_batch_session_dropdown, get_subject_ct_co_attainment, get_subject_university_co_attainment, get_subject_assignment_co_attainment, subject_overall_attainment, get_subject_po_target_level, get_po_list, get_subject_po_attainment, get_subject_po_target_level, get_overall_direct_po_attainment, get_po_avg_target_level, overall_po_attainment, get_po_peo_achieved_level, get_student_feedback_avg_po_wise, get_peo, peo_mi_avg, get_mission

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod

from StudentMMS.models.models_1819o import *
from StudentMMS.models.models_1819e import *
from StudentMMS.models.models_1920o import *

from StudentMMS.constants_functions import requestType
from StudentAcademics.views import *
from StudentAcademics.models.models import *
from StudentAcademics.models.models_1819e import *
from StudentAcademics.models.models_1819o import *
from StudentAcademics.models.models_1920o import *
from StudentAcademics.models.models_1920e import *
from Registrar.models import *
from login.models import EmployeePrimdetail
from itertools import groupby


def mms_student_co_report(request):
    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        session_name = request.session['Session_name']

        SubjectCODetails = generate_session_table_name("SubjectCODetails_", session_name)
        SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
        QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
        SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)
        StudentMarks = generate_session_table_name("StudentMarks_", session_name)
        StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_", session_name)
        AssignmentQuizMarks = generate_session_table_name("AssignmentQuizMarks_", session_name)
        AssignmentStudentMarks = generate_session_table_name("AssignmentStudentMarks_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        COAttainment = generate_session_table_name("COAttainment_", session_name)
        SubjectCODetailsAttainment = generate_session_table_name("SubjectCODetailsAttainment_", session_name)
        MarksAttainmentSettings = generate_session_table_name("MarksAttainmentSettings_", session_name)

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'subjects')):
                sem_id = request.GET['sem'].split(",")
                subject_type = request.GET['subject_type'].split(',')
                data = get_subjects_hod_dean(sem_id, session_name, subject_type)
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'fac_subjects')):
                section_id = request.GET['section'].split(",")
                subject_type = request.GET['subject_type'].split(',')
                data = get_subjects_faculty(emp_id, section_id, session_name, subject_type)
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'subjects_report')):
                sem_id = request.GET['sem'].split(",")
                subject_type = request.GET['subject_type'].split(',')
                data = get_subjects_hod_dean(sem_id, session_name, subject_type)
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'fac_subjects_report')):
                section_id = request.GET['section'].split(",")
                subject_type = request.GET['subject_type'].split(',')
                data = get_subjects_faculty(emp_id, section_id, session_name, subject_type)
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'get_report_data')):
                subject_id = request.GET['subject_id']
                sem_id = request.GET['sem']
                exam_data = []
                exam_list = get_exam_name(session)
                i = 0
                yes = []
                no = []
                na_array = []
                students = []

                student_list = get_section_students(request.GET['section'].split(","), {}, session_name)

                for stud in student_list:
                    students.extend(stud)

                university_marks_entered = False
                sub_type = list(SubjectInfo.objects.filter(id=subject_id).values('subject_type', 'subject_type__value'))

                attainment_level = list(MarksAttainmentSettings.objects.exclude(status='DELETE').filter(sem=sem_id, attainment_type='D', subject_type=sub_type[0]['subject_type']).values('from_direct_per', 'to_indirect_per', 'attainment_level'))

                exam_pid = StudentAcademicsDropdown.objects.filter(field='DIRECT ATTAINMENT METHOD', session=session).exclude(value__isnull=True).values_list('sno')
                exam_list = StudentAcademicsDropdown.objects.filter(pid__in=exam_pid, session=session).exclude(value__isnull=True).values('sno', 'pid', 'value')

                for e in exam_list:

                    paper_id = list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id__exam_id=e['sno'], ques_paper_id__subject_id=subject_id, ques_paper_id__approval_status='APPROVED').values('ques_paper_id'))

                    if paper_id:
                        co_info = list(SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'), co_description=F('description')))

                        for c in co_info:
                            qry = list(SubjectCODetailsAttainment.objects.filter(co_id=c['id'], attainment_method__value='EXAM NAME').values('id').annotate(co_req_attain=F('attainment_per')))

                            if qry:
                                c['co_req_attain'] = qry[0]['co_req_attain']
                            else:
                                c['co_req_attain'] = None

                        co_info_data = []
                        if co_info:  # if exam has been taken
                            exam_data.append({'exam_name': e['value']})
                            exam_data[i]['co_info'] = []

                            for c in co_info:
                                get = 0
                                y = 0
                                no1 = 0
                                na = 0
                                if c['co_name'] > 0:
                                    qid = []
                                    co_section_details = list(QuestionPaperQuestions.objects.exclude(status='DELETE').exclude(status='SAVED').filter(ques_paper_id=paper_id[0]['ques_paper_id'], ques_id__co_id=c['id']).values('section_id', 'section_id__name', 'section_id__attempt_type', 'ques_id', 'ques_num').order_by('section_id', 'ques_num'))

                                    if co_section_details:
                                        co_info_data.append(c)
                                        get = 1

                                        for k, v in groupby(co_section_details, key=lambda x: x['section_id']):
                                            # print(list(v))
                                            for m, n in groupby(v, key=lambda a: a['ques_num']):
                                                n = list(n)
                                                qid.append(n[0]['ques_id'])

                                        co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
                                        c['co_max_marks'] = co_max_marks.get('co_max_marks', 0)

                                        if(e['sno'] == 201):
                                            print(qid, c['co_name'], c['id'], c['co_max_marks'])

                                        for stu in students:
                                            present_status = list(StudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, uniq_id=stu['uniq_id']).values('present_status', 'marks_id__exam_id', 'marks_id__subject_id').distinct())

                                            if 'marks' not in stu:
                                                stu['marks'] = []
                                            if present_status:

                                                if present_status[0]['present_status'] == 'P':
                                                    obtained_co = StudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, ques_id__ques_id__co_id=c['id'], uniq_id=stu['uniq_id']).aggregate(co_obtained=Sum('marks'))
                                                    obtained_co_marks = obtained_co.get('co_obtained', 0)
                                                    co_att_na = 0

                                                    if obtained_co_marks == None:  # when didn't attempt any of the questions of a particular co
                                                        obtained_co_marks = 0
                                                        co_att_na = 1

                                                    stu['marks'].append(obtained_co_marks)
                                                    attainment_per_obtained = (obtained_co_marks / c['co_max_marks']) * 100.0
                                                    if c['co_req_attain'] != None:
                                                        if attainment_per_obtained >= c['co_req_attain']:
                                                            stu['marks'].append('Y')
                                                            y += 1
                                                        elif co_att_na == 1:
                                                            stu['marks'].append('NA')
                                                            na += 1

                                                        else:
                                                            stu['marks'].append('N')
                                                            no1 += 1

                                                    else:  # when co_attain_per is not provided
                                                        stu['marks'].append('NA')
                                                        na += 1

                                                else:  # if absent or detained
                                                    stu['marks'].append('A')
                                                    stu['marks'].append('NA')
                                                    na += 1
                                            else:
                                                stu['marks'].append('NA')
                                                stu['marks'].append('NA')
                                                na += 1

                                if get == 1:
                                    yes.append(y)
                                    no.append(no1)
                                    na_array.append(na)

                            exam_data[i]['co_info'].append(co_info_data)
                            i += 1
                        else:
                            data = {'msg': 'CO details have not been filled for this subject'}
                            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

                university_marks_avail = list(StudentUniversityMarks.objects.filter(subject_id=subject_id).values('id'))
                if university_marks_avail:
                    university_marks_entered = True
                    exam_data.append({'exam_name': 'University Exam'})
                    exam_data[i]['co_info'] = []

                    co_attainment = list(SubjectCODetails.objects.filter(subject_id=subject_id, co_num=-1).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'), co_description=F('description')))
                    max_marks = list(SubjectInfo.objects.filter(id=subject_id).values('id', 'max_university_marks'))
                    if co_attainment:
                        co_per = list(SubjectCODetailsAttainment.objects.filter(co_id=co_attainment[0]['id']).values('id').annotate(co_req_attain=F('attainment_per')))
                        if co_per:
                            co_attainment[0]['co_req_attain'] = co_per[0]['co_req_attain']
                        else:
                            co_attainment[0]['co_req_attain'] = None
                        co_attainment[0]['co_max_marks'] = max_marks[0]['max_university_marks']
                        exam_data[i]['co_info'].append(co_attainment)
                        y = 0
                        no1 = 0
                        na = 0
                        for stu in students:
                            present_status = list(StudentUniversityMarks.objects.filter(subject_id=subject_id, uniq_id=stu['uniq_id']).values('external_marks', 'internal_marks', 'back_marks'))

                            if 'marks' not in stu:
                                stu['marks'] = []

                            if co_per:
                                if present_status:
                                    try:
                                        marks_obtained = float(present_status[0]['external_marks'])
                                        stu['marks'].append(marks_obtained)
                                        attainment_per_obtained = (marks_obtained / max_marks[0]['max_university_marks']) * 100.0
                                        if attainment_per_obtained >= co_attainment[0]['co_req_attain']:
                                            stu['marks'].append('Y')
                                            y += 1
                                        else:
                                            stu['marks'].append('N')
                                            no1 += 1

                                    except:
                                        stu['marks'].append('NA')
                                        stu['marks'].append('NA')
                                        na += 1

                                else:
                                    stu['marks'].append('--')
                                    stu['marks'].append('NA')
                                    na += 1
                            else:
                                stu['marks'].append('NA')
                                stu['marks'].append('NA')
                                na += 1

                        yes.append(y)
                        no.append(no1)
                        na_array.append(na)

                    else:
                        data = {'msg': 'CO attainment details have not been entered for university exam'}
                        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

                data = {'data': exam_data, 'data2': students, 'yes_count': yes, 'no_count': no, 'na_count': na_array, 'university_marks_entered': university_marks_entered, 'attainment_level': attainment_level}

            elif (requestType.custom_request_type(request.GET, 'get_report_data_lab_new')):
                subject_id = request.GET['subject_id']
                sem_id = request.GET['sem']
                exam_data = []
                exam_list = get_exam_name(session)
                i = 0
                yes = []
                no = []
                na_array = []
                students = []

                # student_list=get_section_students(request.GET['section'].split(","),{},session_name)
                if request.GET['isgroup'] == 'N':
                    section = request.GET['section'].split(",")
                    student_list = get_section_students(request.GET['section'].split(","), {}, session_name)
                    extra_filter = {'marks_id__section__in': section}
                    for stud in student_list:
                        students.extend(stud)
                else:
                    group = request.GET['group_id'].split(",")
                    student_list = []
                    for g in group:
                        student = get_att_group_students_nominal(g, session_name)
                        student_list.extend(student)
                    extra_filter = {'marks_id__group_id__in': group}
                    for stud in student_list:
                        students.append(stud)

                university_marks_entered = False
                sub_type = list(SubjectInfo.objects.filter(id=subject_id).values('subject_type', 'subject_type__value'))
                attainment_level = list(MarksAttainmentSettings.objects.exclude(status='DELETE').filter(sem=sem_id, attainment_type='D', subject_type=sub_type[0]['subject_type']).values('from_direct_per', 'to_indirect_per', 'attainment_level'))

                exam_pid = StudentAcademicsDropdown.objects.filter(field='DIRECT ATTAINMENT METHOD', session=session).exclude(value__isnull=True).values_list('sno')
                exam_list = StudentAcademicsDropdown.objects.filter(pid__in=exam_pid, session=session).exclude(value__isnull=True).values('sno', 'pid', 'value')
                for e in exam_list:
                    saved_format = AssignmentStudentMarks.objects.filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id).filter(**extra_filter).exclude(status='DELETE').values_list('marks_id__isco_wise', flat=True)
                    paper_id = list(AssignmentStudentMarks.objects.filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id).filter(**extra_filter).exclude(status='DELETE').values('id', 'marks_id__isco_wise', 'marks_id__max_marks', 'ques_id__ques_paper_id'))
                    if paper_id:
                        is_overall = 0
                        if 'N' in saved_format:
                            is_overall = 1
                            co_info = list(SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'), co_description=F('description')))

                            qry = list(SubjectCODetailsAttainment.objects.exclude(status='DELETE').filter(co_id__subject_id=subject_id, attainment_method=e['pid']).values('id').annotate(co_req_attain=F('attainment_per')))

                            if qry:
                                co_info_data = []
                                exam_data.append({'exam_name': e['value']})
                                exam_data[i]['co_info'] = []
                                get = 0
                                y = 0
                                no1 = 0
                                na = 0
                                co_info_data.append([{'co_req_attain': qry[0]['co_req_attain'], 'co_description':"All CO's", 'co_name':"All CO's"}])
                                exam_data[i]['is_overall'] = is_overall
                                exam_data[i]['co_info'].extend(co_info_data)
                                for stu in students:
                                    qry_co_wise = list(AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, uniq_id=stu['uniq_id']).values('marks_id__isco_wise'))
                                    if len(qry_co_wise) > 0 and qry_co_wise[0]['marks_id__isco_wise'] == 'N':

                                        present_status = list(AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, uniq_id=stu['uniq_id']).values('present_status', 'marks_id__exam_id', 'marks_id__subject_id', 'marks_id__max_marks').distinct())

                                        if 'marks' not in stu:
                                            stu['marks'] = []
                                        get = 1
                                        if present_status:
                                            if present_status[0]['present_status'] == 'P':
                                                obtained_co = AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, uniq_id=stu['uniq_id']).aggregate(co_obtained=Sum('marks'))

                                                obtained_co_marks = obtained_co.get('co_obtained', 0)
                                                co_att_na = 0

                                                if obtained_co_marks == None:  # when didn't attempt any of the questions of a particular co
                                                    obtained_co_marks = 0
                                                    co_att_na = 1

                                                stu['marks'].append(obtained_co_marks)
                                                try:
                                                    attainment_per_obtained = (obtained_co_marks / present_status[0]['marks_id__max_marks']) * 100.0
                                                except:
                                                    attainment_per_obtained = 0.0
                                                if qry[0]['co_req_attain'] != None:
                                                    if attainment_per_obtained >= qry[0]['co_req_attain']:
                                                        stu['marks'].append('Y')
                                                        y += 1
                                                    elif co_att_na == 1:
                                                        stu['marks'].append('NA')
                                                        na += 1

                                                    else:
                                                        stu['marks'].append('N')
                                                        no1 += 1

                                                else:
                                                    stu['marks'].append('NA')
                                                    na += 1

                                            else:
                                                stu['marks'].append('A')
                                                stu['marks'].append('NA')
                                                na += 1
                                        else:
                                            stu['marks'].append('NA')
                                            stu['marks'].append('NA')
                                            na += 1

                                    elif len(qry_co_wise) > 0 and qry_co_wise[0]['marks_id__isco_wise'] == 'Y':
                                        co_info = list(SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'), co_description=F('description')))
                                        # co_ids=[]
                                        for c in co_info:
                                            qry_co = list(SubjectCODetailsAttainment.objects.filter(co_id=c['id'], attainment_method=e['pid']).values('id').annotate(co_req_attain=F('attainment_per')))

                                            if qry_co:
                                                c['co_req_attain'] = qry_co[0]['co_req_attain']
                                            else:
                                                c['co_req_attain'] = None

                                        co_info_data = []
                                        co_ids = [c['id'] for c in co_info]
                                        if co_info:  # if exam has been taken
                                            if co_info[0]['co_name'] > 0:
                                                qid = []
                                                co_section_details = list(QuestionPaperQuestions.objects.exclude(status='DELETE').exclude(status='SAVED').filter(ques_paper_id=paper_id[0]['ques_id__ques_paper_id'], ques_id__co_id__in=co_ids).values('section_id', 'section_id__name', 'section_id__attempt_type', 'ques_id', 'ques_num').order_by('section_id', 'ques_num'))

                                                if co_section_details:
                                                    get = 1

                                                    for k, v in groupby(co_section_details, key=lambda x: x['section_id']):
                                                        for m, n in groupby(v, key=lambda a: a['ques_num']):
                                                            n = list(n)
                                                            qid.append(n[0]['ques_id'])

                                                    co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
                                                    co_info[0]['co_max_marks'] = co_max_marks.get('co_max_marks', 0)

                                                    present_status = list(AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, uniq_id=stu['uniq_id']).values('present_status', 'marks_id__exam_id', 'marks_id__subject_id').distinct())

                                                    if 'marks' not in stu:
                                                        stu['marks'] = []

                                                    if present_status:

                                                        if present_status[0]['present_status'] == 'P':
                                                            obtained_co = AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, ques_id__ques_id__co_id__in=co_ids, uniq_id=stu['uniq_id']).aggregate(co_obtained=Sum('marks'))
                                                            obtained_co_marks = obtained_co.get('co_obtained', 0)
                                                            co_att_na = 0

                                                            if obtained_co_marks == None:  # when didn't attempt any of the questions of a particular co
                                                                obtained_co_marks = 0
                                                                co_att_na = 1

                                                            stu['marks'].append(obtained_co_marks)
                                                            try:
                                                                attainment_per_obtained = (obtained_co_marks / co_info[0]['co_max_marks']) * 100.0
                                                            except:
                                                                attainment_per_obtained = 0.0
                                                            if c['co_req_attain'] != None:
                                                                if attainment_per_obtained >= c['co_req_attain']:
                                                                    stu['marks'].append('Y')
                                                                    y += 1
                                                                elif co_att_na == 1:
                                                                    stu['marks'].append('NA')
                                                                    na += 1

                                                                else:
                                                                    stu['marks'].append('N')
                                                                    no1 += 1

                                                            else:  # when co_attain_per is not provided
                                                                stu['marks'].append('NA')
                                                                na += 1

                                                        else:  # if absent or detained
                                                            stu['marks'].append('A')
                                                            stu['marks'].append('NA')
                                                            na += 1
                                                    else:
                                                        stu['marks'].append('NA')
                                                        stu['marks'].append('NA')
                                                        na += 1
                                    else:
                                        if 'marks' not in stu:
                                            stu['marks'] = []
                                        stu['marks'].append('NA')
                                        stu['marks'].append('NA')
                                        na += 1
                                if get == 1:
                                    yes.append(y)
                                    no.append(no1)
                                    na_array.append(na)
                                i += 1

                            else:
                                data = {'msg': 'CO attainment details have not been filled for this subject'}
                                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

                        else:
                            co_info = list(SubjectCODetails.objects.filter(subject_id=subject_id).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'), co_description=F('description')))

                            for c in co_info:
                                qry_co = list(SubjectCODetailsAttainment.objects.filter(co_id=c['id'], attainment_method=e['pid']).values('id').annotate(co_req_attain=F('attainment_per')))
                                # c['co_name']="CO"+str(c['co_name'])
                                if qry_co:
                                    c['co_req_attain'] = qry_co[0]['co_req_attain']
                                else:
                                    c['co_req_attain'] = None

                            co_info_data = []
                            if co_info:  # if exam has been taken
                                exam_data.append({'exam_name': e['value']})
                                exam_data[i]['co_info'] = []

                                for c in co_info:
                                    get = 0
                                    y = 0
                                    no1 = 0
                                    na = 0
                                    if c['co_name'] > 0:
                                        qid = []
                                        co_section_details = list(QuestionPaperQuestions.objects.exclude(status='DELETE').exclude(status='SAVED').filter(ques_paper_id=paper_id[0]['ques_id__ques_paper_id'], ques_id__co_id=c['id']).values('section_id', 'section_id__name', 'section_id__attempt_type', 'ques_id', 'ques_num').order_by('section_id', 'ques_num'))

                                        if co_section_details:
                                            c['co_name'] = "CO" + str(c['co_name'])
                                            co_info_data.append(c)
                                            get = 1

                                            for k, v in groupby(co_section_details, key=lambda x: x['section_id']):
                                                for m, n in groupby(v, key=lambda a: a['ques_num']):
                                                    n = list(n)
                                                    qid.append(n[0]['ques_id'])

                                            co_max_marks = SubjectAddQuestions.objects.filter(id__in=qid).aggregate(co_max_marks=Sum('max_marks'))
                                            c['co_max_marks'] = co_max_marks.get('co_max_marks', 0)

                                            for stu in students:
                                                present_status = list(AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, uniq_id=stu['uniq_id']).values('present_status', 'marks_id__exam_id', 'marks_id__subject_id').distinct())

                                                if 'marks' not in stu:
                                                    stu['marks'] = []

                                                if present_status:

                                                    if present_status[0]['present_status'] == 'P':
                                                        obtained_co = AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks__isnull=True).filter(marks_id__exam_id=e['sno'], marks_id__subject_id=subject_id, ques_id__ques_id__co_id=c['id'], uniq_id=stu['uniq_id']).aggregate(co_obtained=Sum('marks'))
                                                        obtained_co_marks = obtained_co.get('co_obtained', 0)
                                                        co_att_na = 0

                                                        if obtained_co_marks == None:  # when didn't attempt any of the questions of a particular co
                                                            obtained_co_marks = 0
                                                            co_att_na = 1

                                                        stu['marks'].append(obtained_co_marks)
                                                        attainment_per_obtained = (obtained_co_marks / c['co_max_marks']) * 100.0
                                                        if c['co_req_attain'] != None:
                                                            if attainment_per_obtained >= c['co_req_attain']:
                                                                stu['marks'].append('Y')
                                                                y += 1
                                                            elif co_att_na == 1:
                                                                stu['marks'].append('NA')
                                                                na += 1

                                                            else:
                                                                stu['marks'].append('N')
                                                                no1 += 1

                                                        else:  # when co_attain_per is not provided
                                                            stu['marks'].append('NA')
                                                            na += 1

                                                    else:  # if absent or detained
                                                        stu['marks'].append('A')
                                                        stu['marks'].append('NA')
                                                        na += 1
                                                else:
                                                    stu['marks'].append('NA')
                                                    stu['marks'].append('NA')
                                                    na += 1

                                            if get == 1:
                                                yes.append(y)
                                                no.append(no1)
                                                na_array.append(na)
                                exam_data[i]['is_overall'] = is_overall
                                exam_data[i]['co_info'].append(co_info_data)
                                i += 1

                university_marks_avail = list(StudentUniversityMarks.objects.filter(subject_id=subject_id).values('id'))

                if university_marks_avail:
                    university_marks_entered = True
                    exam_data.append({'exam_name': 'University Exam'})
                    exam_data[i]['co_info'] = []

                    co_attainment = list(SubjectCODetails.objects.filter(subject_id=subject_id, co_num=-1).exclude(status='DELETE').values('id').annotate(co_name=F('co_num'), co_description=F('description')))
                    max_marks = list(SubjectInfo.objects.filter(id=subject_id).values('id', 'max_university_marks'))
                    if co_attainment:
                        co_per = list(SubjectCODetailsAttainment.objects.filter(co_id=co_attainment[0]['id']).values('id').annotate(co_req_attain=F('attainment_per')))
                        if co_per:
                            co_attainment[0]['co_req_attain'] = co_per[0]['co_req_attain']
                        else:
                            co_attainment[0]['co_req_attain'] = None
                        co_attainment[0]['co_max_marks'] = max_marks[0]['max_university_marks']
                        exam_data[i]['co_info'].append(co_attainment)
                        y = 0
                        no1 = 0
                        na = 0
                        for stu in students:
                            present_status = list(StudentUniversityMarks.objects.filter(subject_id=subject_id, uniq_id=stu['uniq_id']).values('external_marks', 'internal_marks', 'back_marks'))

                            if 'marks' not in stu:
                                stu['marks'] = []

                            if co_per:
                                if present_status:
                                    try:
                                        marks_obtained = float(present_status[0]['external_marks'])
                                        stu['marks'].append(marks_obtained)
                                        attainment_per_obtained = (marks_obtained / max_marks[0]['max_university_marks']) * 100.0
                                        if attainment_per_obtained >= co_attainment[0]['co_req_attain']:
                                            stu['marks'].append('Y')
                                            y += 1
                                        else:
                                            stu['marks'].append('N')
                                            no1 += 1

                                    except:
                                        stu['marks'].append('NA')
                                        stu['marks'].append('NA')
                                        na += 1

                                else:
                                    stu['marks'].append('--')
                                    stu['marks'].append('NA')
                                    na += 1
                            else:
                                stu['marks'].append('NA')
                                stu['marks'].append('NA')
                                na += 1

                        yes.append(y)
                        no.append(no1)
                        na_array.append(na)

                    else:
                        data = {'msg': 'CO attainment details have not been entered for university exam'}
                        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

                data = {'data': exam_data, 'data2': students, 'yes_count': yes, 'no_count': no, 'na_count': na_array, 'university_marks_entered': university_marks_entered, 'attainment_level': attainment_level}

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST
        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def mms_attainment_settings(request):

    if checkpermission(request, [rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS:
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        session_name = request.session['Session_name']
        MarksAttainmentSettings = generate_session_table_name("MarksAttainmentSettings_", session_name)

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_attainment_limit')):
                qry = StudentAcademicsDropdown.objects.exclude(status='DELETE').exclude(value__isnull=True).filter(field='LEVEL', session=session).values('value')
                data = {'data': list(qry)}

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                dept = request.GET['dept'].split(",")
                sem = request.GET['sem'].split(",")
                sub_type = request.GET['subject_type'].split(",")
                qry = MarksAttainmentSettings.objects.filter(subject_type__in=sub_type, sem__dept__in=dept, sem__sem__in=sem, attainment_type='D').values('from_direct_per', 'to_indirect_per', 'attainment_level', 'subject_type__value').annotate(dept=F('sem__dept__dept__value'), course=F('sem__dept__course__value'), sem=F('sem__sem'))

                qry2 = MarksAttainmentSettings.objects.filter(subject_type__in=sub_type, sem__dept__in=dept, sem__sem__in=sem, attainment_type='A').values('external_marks', 'internal_marks', 'from_direct_per', 'to_indirect_per', 'subject_type__value').annotate(dept=F('sem__dept__dept__value'), course=F('sem__dept__course__value'), sem=F('sem__sem'))

                data = {'data1': list(qry), 'data2': list(qry2)}

        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            sem = data['sem'].split(",")
            dept = data['dept'].split(",")
            sub_type = data['subject_type'].split(",")

            sem_id = StudentSemester.objects.filter(dept__in=dept, sem__in=sem).values_list('sem_id', flat=True)

            if data['form_type'] == 0:
                qry1 = MarksAttainmentSettings.objects.filter(subject_type__in=sub_type, sem__dept__in=dept, sem__sem__in=sem, attainment_type='D').update(status='DELETE')
                qry_object = (MarksAttainmentSettings(subject_type=StudentDropdown.objects.get(sno=sub), sem=StudentSemester.objects.get(sem_id=s), from_direct_per=d['from'], to_indirect_per=d['to'], attainment_level=d['attainment_level'], attainment_type='D', added_by=EmployeePrimdetail.objects.get(emp_id=emp_id)) for s in sem_id for sub in sub_type for d in data['input_data'])

            elif data['form_type'] == 1:
                qry1 = MarksAttainmentSettings.objects.filter(subject_type__in=sub_type, sem__dept__in=dept, sem__sem__in=sem, attainment_type='A').update(status='DELETE')
                qry_object = (MarksAttainmentSettings(subject_type=StudentDropdown.objects.get(sno=sub), sem=StudentSemester.objects.get(sem_id=s), from_direct_per=data['direct'], to_indirect_per=data['indirect'], attainment_type='A', added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), external_marks=data['external'], internal_marks=data['internal']) for s in sem_id for sub in sub_type)

            qry_create = MarksAttainmentSettings.objects.bulk_create(qry_object)
            if qry_create:
                data = statusMessages.MESSAGE_INSERT
        else:
            data = statusMessages.MESSAGE_BAD_REQUEST
        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def enter_assi_quiz_marks(request):

    if checkpermission(request, [rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        session_name = request.session['Session_name']
        AssignmentQuizMarks = generate_session_table_name("AssignmentQuizMarks_", session_name)
        AssignmentStudentMarks = generate_session_table_name("AssignmentStudentMarks_", session_name)
        QuesPaperApplicableOn = generate_session_table_name("QuesPaperApplicableOn_", session_name)
        QuesPaperSectionDetails = generate_session_table_name("QuesPaperSectionDetails_", session_name)
        QuesPaperBTAttainment = generate_session_table_name("QuesPaperBTAttainment_", session_name)
        QuestionPaperQuestions = generate_session_table_name("QuestionPaperQuestions_", session_name)
        SubjectQuestionPaper = generate_session_table_name("SubjectQuestionPaper_", session_name)
        SubjectAddQuestions = generate_session_table_name("SubjectAddQuestions_", session_name)
        SubjectQuesOptions = generate_session_table_name("SubjectQuesOptions_", session_name)
        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)
        studentSession = generate_session_table_name("studentSession_", session_name)
        SectionGroupDetails = generate_session_table_name("SectionGroupDetails_", session_name)

        if requestMethod.GET_REQUEST(request):
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

            sections = list(Sections.objects.filter(section_id__in=section_id).values('section', 'section_id'))

            final_list = []
            sem_details = list(StudentSemester.objects.filter(sem_id=sem).values('sem', 'dept__dept__value', 'dept__course__value'))
            for sec in sections:
                section_id = sec['section_id']
                qry_marks_id = AssignmentQuizMarks.objects.filter(section=section_id, subject_id=subject_id, exam_id=exam_id, isgroup=isgroup).exclude(status='DELETE').values('id', 'isco_wise', 'max_marks').order_by('-id')
                final_data = {}
                if len(qry_marks_id) > 0:
                    marks_id = qry_marks_id[0]['id']
                    final_data['isco_wise'] = qry_marks_id[0]['isco_wise']
                    final_data['max_marks'] = qry_marks_id[0]['max_marks']
                else:
                    marks_id = None
                    final_data['isco_wise'] = None

                if isgroup == 'N':
                    students = get_section_students([section_id], {}, session_name)
                    stud = students[0]

                else:
                    stud = get_att_group_section_students(group_id, section_id, session_name)

                final_data['section'] = sec['section']
                final_data['students'] = []

                k = 0
                if stud:
                    for student in stud:
                        marks_entered = list(AssignmentStudentMarks.objects.exclude(marks_id__status="DELETE").exclude(status='DELETE').filter(uniq_id=student['uniq_id'], marks_id__exam_id=exam_id, marks_id__subject_id=subject_id, marks_id=marks_id).values('ques_id__ques_paper_id', 'present_status', 'marks_id__isco_wise'))
                        if marks_entered:
                            if marks_entered[0]['present_status'] == 'A':
                                student['isAbsent'] = True

                        papers = SubjectQuestionPaper.objects.exclude(status='DELETE').filter(exam_id=exam_id, subject_id=subject_id, approval_status="APPROVED").values_list('id', flat=True)
                        qp_data = {}
                        student['paper_data'] = []
                        a = 0
                        student['set_index'] = None
                        data = {}

                        for p in papers:
                            ques_paper_id = p
                            data = {}
                            question_format = list(QuestionPaperQuestions.objects.exclude(status='DELETE').filter(ques_paper_id=p).values('section_id', 'section_id__ques_paper_id', 'section_id__ques_paper_id__time'))
                            total_max_marks = QuesPaperSectionDetails.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).aggregate(total_max_marks=Sum('max_marks'))
                            data['time_duration'] = question_format[0]['section_id__ques_paper_id__time']
                            data['Max_marks'] = total_max_marks.get('total_max_marks', 0)
                            data['bt_level_attain'] = []
                            data['bt_level_attain'] = list(QuesPaperBTAttainment.objects.exclude(ques_paper_id__status='DELETE').filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).values('minimum', 'maximum').annotate(bt_level=F('bt_level__value')))
                            data['section'] = []
                            data['paper_id'] = ques_paper_id
                            section_data = list(QuesPaperSectionDetails.objects.filter(ques_paper_id=question_format[0]['section_id__ques_paper_id']).values('id', 'name', 'attempt_type', 'max_marks'))
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
                                                marks_value = list(AssignmentStudentMarks.objects.exclude(status='DELETE').exclude(marks_id__status='DELETE').filter(uniq_id=student['uniq_id'], ques_id__ques_id=q['id'], marks_id=marks_id).values('marks', 'present_status'))

                                                if not marks_value:
                                                    marks = None
                                                else:
                                                    marks = marks_value[0]['marks']
                                            else:
                                                marks = None
                                            q['marks_obtained'] = marks
                                        else:
                                            q['marks_obtained'] = None
                                        if q['type'] == 'O':
                                            q['option'] = list(SubjectQuesOptions.objects.filter(ques_id=q['id']).values('option_description', 'option_img', 'is_answer'))
                                        if final_data['isco_wise'] == 'N':
                                            q['marks_obtained'] = None

                                    section['question'].append(qry)
                            a += 1
                        student['paper_data'].append(data)
                        if not papers:
                            student['paper_data'] = []
                            student['set_index'] = -1

                    for student in stud:
                        marks_entered = list(AssignmentStudentMarks.objects.exclude(marks_id__status="DELETE").exclude(status='DELETE').filter(uniq_id=student['uniq_id'], marks_id__exam_id=exam_id, marks_id__subject_id=subject_id, marks_id=marks_id).values('ques_id__ques_paper_id', 'present_status', 'marks'))
                        if marks_entered:
                            if marks_entered[0]['present_status'] == 'A':
                                student['isAbsent'] = True
                            else:
                                student['overall_obtained'] = marks_entered[0]['marks']
                        else:
                            student['overall_obtained'] = None
                        if final_data['isco_wise'] == 'Y':
                            student['overall_obtained'] = None
                            final_data['max_marks'] = None
                        final_data['students'].append(student)

                final_list.append(final_data)
            data = {'data': final_list}

        elif requestMethod.POST_REQUEST(request):
            body = json.loads(request.body)
            # print(body, 'body')
            data = body['on_submit']

            for group in data:
                print(group, 'group')
                if 'max_marks' not in group:
                    group['max_marks'] = None

                if group['isgroup'] != 'N':
                    delete_filter = {'exam_id': group['exam_id'], 'subject_id': group['subject_id'], 'section': group['section_id'], 'group_id': group['group_id']}
                    qry_filter = {'section': group['section_id'], 'subject_id': group['subject_id'], 'exam_id': group['exam_id'], 'group_id': group['group_id'], 'isco_wise': group['isco_wise']}
                    qry_create = {'section': Sections.objects.get(section_id=group['section_id']), 'subject_id': SubjectInfo.objects.get(id=group['subject_id']), 'exam_id': StudentAcademicsDropdown.objects.get(sno=group['exam_id']), 'added_by': EmployeePrimdetail.objects.get(emp_id=emp_id), 'isgroup': group['isgroup'], 'group_id': SectionGroupDetails.objects.get(id=group['group_id']), 'isco_wise': group['isco_wise'], 'max_marks': group['max_marks']}
                else:
                    delete_filter = {'exam_id': group['exam_id'], 'subject_id': group['subject_id'], 'section': group['section_id']}
                    qry_filter = {'section': group['section_id'], 'subject_id': group['subject_id'], 'exam_id': group['exam_id'], 'isco_wise': group['isco_wise']}
                    qry_create = {'section': Sections.objects.get(section_id=group['section_id']), 'subject_id': SubjectInfo.objects.get(id=group['subject_id']), 'exam_id': StudentAcademicsDropdown.objects.get(sno=group['exam_id']), 'added_by': EmployeePrimdetail.objects.get(emp_id=emp_id), 'isgroup': group['isgroup'], 'isco_wise': group['isco_wise'], 'max_marks': group['max_marks']}

                group_marks = list(AssignmentQuizMarks.objects.exclude(status='DELETE').filter(**qry_filter).values('id'))
                if not group_marks:
                    delete_previous = AssignmentQuizMarks.objects.filter(**delete_filter).update(status='DELETE')
                    group_marks_qry = AssignmentQuizMarks.objects.create(**qry_create)
                    group_marks = group_marks_qry.id

                else:
                    group_marks = group_marks[0]['id']
                    group_marks_qry = AssignmentQuizMarks.objects.exclude(status='DELETE').filter(id=group_marks).update(**qry_create)

                if group['isco_wise'] == 'Y':
                    for student in group['students']:
                        qry = AssignmentStudentMarks.objects.filter(marks_id__exam_id=group['exam_id'], marks_id__subject_id=group['subject_id'], uniq_id=student['uniq_id']).update(status='DELETE')
                        set_index = student['set_index']
                        present_status = 'P'

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

                            AssignmentStudentMarks.objects.exclude(status='DELETE').filter(marks_id__exam_id=group['exam_id'], marks_id__subject_id=group['subject_id'], uniq_id=student['uniq_id']).update(status='DELETE')

                            objs = (AssignmentStudentMarks(marks_id=AssignmentQuizMarks.objects.get(id=group_marks), uniq_id=studentSession.objects.get(uniq_id=student['uniq_id']), marks=(q['marks_obt']), ques_id=QuestionPaperQuestions.objects.exclude(status='DELETE').get(ques_paper_id=student['paper_data'][set_index]['paper_id'], section_id=sec['id'], ques_id=q['id']), status=status, present_status=present_status) for sec in section for ques in sec['question'] for q in ques)

                            enter_marks = AssignmentStudentMarks.objects.bulk_create(objs)
                else:
                    for student in group['students']:
                        present_status = 'P'
                        if 'isAbsent' in student:
                            if student['isAbsent'] == True:
                                present_status = 'A'
                                student['overall_obtained'] = None

                        qry = AssignmentStudentMarks.objects.filter(marks_id__exam_id=group['exam_id'], marks_id__subject_id=group['subject_id'], uniq_id=student['uniq_id']).update(status='DELETE')
                        if 'overall_obtained' in student:
                            enter_marks = AssignmentStudentMarks.objects.create(marks_id=AssignmentQuizMarks.objects.get(id=group_marks), uniq_id=studentSession.objects.get(uniq_id=student['uniq_id']), marks=student['overall_obtained'], present_status=present_status)
        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def course_overall_attainment(request):
    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        session_name = request.session['Session_name']

        SubjectInfo = generate_session_table_name("SubjectInfo_", session_name)

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_batch')):
                data = get_batch_dropdown(request.GET['dept'], session_name)

            elif(requestType.custom_request_type(request.GET, 'sem')):
                dept = request.GET['dept']
                sem = get_coordinator_sem(emp_id, "NC", dept, session_name)
                data = {'data': sem}

            elif(requestType.custom_request_type(request.GET, 'get_batch_session_dropdown')):
                data = get_batch_session_dropdown(request.GET['batch'], session_name)

            elif(requestType.custom_request_type(request.GET, 'form_data')):
                final_data = []
                batch_session = request.GET['batch_session'].split(",")
                dept = request.GET['dept']
                batch_array = request.GET['batch'].split("-")
                batch_from = int(batch_array[0][2:])
                i = 0
                subject_array = []
                for name in batch_session:
                    final_data.append({})
                    SubjectInfo = generate_session_table_name("SubjectInfo_", name)
                    session = list(Semtiming.objects.filter(session_name=name).values('uid'))
                    batch_till = int(name[:2])
                    sem_type = name[-1:]

                    if sem_type == 'o':
                        plus_factor = 1
                    else:
                        plus_factor = 2

                    sem = (2 * (batch_till - batch_from)) + plus_factor

                    subject_id = SubjectInfo.objects.filter(sem__sem=sem, sem__dept=dept, session=session[0]['uid']).exclude(status='DELETE').values('id', 'subject_type__value', 'sem', 'subject_type')

                    for subject in subject_id:
                        subject_data = subject_overall_attainment(subject['id'], subject['subject_type'], subject['sem'], name, session[0]['uid'])
                        subject_array.append(subject_data)
                    final_data[i]['session_array'] = subject_array
                    i += 1
                data = {'data': subject_array}
        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def get_course_overall_po_attainment(request):
    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        session_name = request.session['Session_name']

        if(requestType.custom_request_type(request.GET, 'form_data')):
            batch_session = request.GET['batch_session'].split(",")
            dept = request.GET['dept']
            batch_array = request.GET['batch'].split("-")
            batch_from = int(batch_array[0][2:])
            final_data = []
            array = []
            subject_array = []
            po_array = []

            for name in batch_session:
                final_data.append({})
                SubjectInfo = generate_session_table_name("SubjectInfo_", name)
                session = list(Semtiming.objects.filter(session_name=name).values('uid'))
                batch_till = int(name[:2])
                sem_type = name[-1:]
                po_list = get_po(dept, name)

                if sem_type == 'o':
                    plus_factor = 1
                else:
                    plus_factor = 2
                sem = (2 * (batch_till - batch_from)) + plus_factor
                subject_id = list(SubjectInfo.objects.filter(sem__sem=sem, sem__dept=dept, session=session[0]['uid']).exclude(status='DELETE').values('id', 'subject_type__value', 'sem', 'subject_type', 'sub_alpha_code', 'sub_num_code', 'sub_name'))

                for subject in subject_id:
                    subject['po_data'] = []
                    for po in po_list:
                        subject_overall_attain = get_subject_po_attainment(subject['id'], subject['subject_type'], po['id'], subject['sem'], name, session[0]['uid'])

                        subject['po_data'].append({'po_id': po['id'], 'po_num': po['po_level_abbr'], 'po_desc': po['description'], 'sub_po_attain': subject_overall_attain})
                    subject_array.append(subject)

                # for po in po_list:
                #   po['overall_po_attainment']=get_overall_direct_po_attainment(subject_id,po['id'],subject['sem'],name,session[0]['uid'])
                #   po_array.append(po)

            for po in po_list:
                po_sum = 0
                i = 0
                for subject in subject_array:
                    for subject_po in subject['po_data']:
                        if po['description'] == subject_po['po_desc'] and subject_po['sub_po_attain'] is not None:
                            po_sum = po_sum + subject_po['sub_po_attain']
                            i += 1

                if po_sum is not None and i is not None and i != 0:
                    po['overall_po_attainment'] = po_sum / i
                else:
                    po['overall_po_attainment'] = None
                po_array.append(po)

            data = {'subject_list': subject_array, 'po_list': po_array}

        elif(requestType.custom_request_type(request.GET, 'nba_course')):
            q_dept = EmployeePrimdetail.objects.filter(emp_id=EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])).values('dept')
            dept = q_dept[0]['dept']
            course = list(CourseDetail.objects.filter(dept=dept).values('course', 'course__value'))
            data = {'course': course}

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def co_po_matrix(request):
    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
        emp_id = request.session['hash1']
        session = request.session['Session_id']
        session_name = request.session['Session_name']

        if(requestType.custom_request_type(request.GET, 'form_data')):
            batch_session = request.GET['batch_session'].split(",")
            dept = request.GET['dept']
            batch_array = request.GET['batch'].split("-")
            batch_from = int(batch_array[0][2:])
            subject_array = []
            po_array = []
            final_data = []
            for name in batch_session:
                final_data.append({})
                SubjectInfo = generate_session_table_name("SubjectInfo_", name)
                session = list(Semtiming.objects.filter(session_name=name).values('uid'))
                batch_till = int(name[:2])
                sem_type = name[-1:]
                po_list = get_po(dept, name)
                if sem_type == 'o':
                    plus_factor = 1
                else:
                    plus_factor = 2
                sem = (2 * (batch_till - batch_from)) + plus_factor

                subject_id = list(SubjectInfo.objects.filter(sem__sem=sem, sem__dept=dept, session=session[0]['uid']).exclude(status='DELETE').values('id', 'subject_type__value', 'sem', 'subject_type', 'sub_alpha_code', 'sub_num_code', 'sub_name'))
                for subject in subject_id:
                    subject['po_data'] = []
                    for po in po_list:
                        subject_target_level = get_subject_po_target_level(subject['id'], po['id'], name, session[0]['uid'])
                        subject['po_data'].append({'po_id': po['id'], 'po_num': po['po_level_abbr'], 'po_desc': po['description'], 'sub_target_level': subject_target_level})

                    subject_array.append(subject)

            for po in po_list:
                po_sum = 0
                i = 0
                for subject in subject_array:
                    for subject_po in subject['po_data']:
                        if po['description'] == subject_po['po_desc'] and subject_po['sub_target_level'] is not None:
                            po_sum = po_sum + subject_po['sub_target_level']
                            i += 1

                if po_sum is not None and i is not None and i != 0:
                    po['po_avg_target'] = po_sum / i
                else:
                    po['po_avg_target'] = None

                po_array.append(po)

            data = {'subject_list': subject_array, 'po_list': po_array}

        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def po_attainment_gap_report(request):
    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
        if(requestType.custom_request_type(request.GET, 'form_data')):
            batch_session = request.GET['batch_session'].split(",")
            dept = request.GET['dept']
            batch = request.GET['batch']
            batch_array = batch.split("-")
            batch_from = int(batch_array[0][2:])
            final_data = []
            array = []
            subject_array = []

            for name in batch_session:
                final_data.append({})
                SubjectInfo = generate_session_table_name("SubjectInfo_", name)
                session = list(Semtiming.objects.filter(session_name=name).values('uid'))
                batch_till = int(name[:2])
                sem_type = name[-1:]
                po_list = get_po(dept, name)

                if sem_type == 'o':
                    plus_factor = 1
                else:
                    plus_factor = 2

                sem = (2 * (batch_till - batch_from)) + plus_factor

                subject_id = list(SubjectInfo.objects.filter(sem__sem=sem, sem__dept=dept, session=session[0]['uid']).exclude(status='DELETE').values('id', 'subject_type__value', 'sem', 'subject_type', 'sub_alpha_code', 'sub_num_code', 'sub_name'))

                for subject in subject_id:

                    subject['po_data'] = []
                    for po in po_list:
                        subject_overall_attain = get_subject_po_attainment(subject['id'], subject['subject_type'], po['id'], subject['sem'], name, session[0]['uid'])

                        subject['po_data'].append({'po_id': po['id'], 'po_num': po['po_level_abbr'], 'po_desc': po['description'], 'sub_po_attain': subject_overall_attain})
                    subject_array.append(subject)
                    sem_id = subject['sem']

            overall_indirect_po_attainment = get_student_feedback_avg_po_wise(dept, {}, batch_session, batch)[0]['final_average']

            for po in po_list:
                po_sum = 0
                i = 0
                for subject in subject_array:
                    for subject_po in subject['po_data']:
                        if po['description'] == subject_po['po_desc'] and subject_po['sub_po_attain'] is not None:
                            po_sum = po_sum + subject_po['sub_po_attain']
                            i += 1

                if po_sum != 0 and i != 0:
                    po['overall_direct_po_attainment'] = po_sum / i

                else:
                    po['overall_direct_po_attainment'] = None

                for target in overall_indirect_po_attainment:
                    if po['description'] == target['description']:
                        po['overall_indirect_po_attainment'] = target['average']

                po['overall_po_attainment'] = overall_po_attainment(po['overall_direct_po_attainment'], po['overall_indirect_po_attainment'], sem_id, name, session[0]['uid'])

                po['average_target_level'] = get_po_avg_target_level(subject_id, po['id'], name, session[0]['uid'])

                if po['average_target_level'] != None and po['overall_po_attainment'] != None:
                    po['gap'] = po['overall_po_attainment'] - po['average_target_level']

                else:
                    po['gap'] = None

            data = {'po_list': po_list}
        else:
            data = statusMessages.MESSAGE_BAD_REQUEST

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def po_peo_attainment_report(request):
    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
        batch_session = request.GET['batch_session'].split(",")
        dept = request.GET['dept']
        batch = request.GET['batch']
        batch_array = batch.split("-")
        batch_from = int(batch_array[0][2:])
        subject_array = []
        for name in batch_session:
            SubjectInfo = generate_session_table_name("SubjectInfo_", name)
            SubjectPOPEOMapping = generate_session_table_name("SubjectPOPEOMapping_", name)
            session = list(Semtiming.objects.filter(session_name=name).values('uid'))
            batch_till = int(name[:2])
            sem_type = name[-1:]

            if sem_type == 'o':
                plus_factor = 1
            else:
                plus_factor = 2

            sem = (2 * (batch_till - batch_from)) + plus_factor

            po_list = get_po(dept, name)
            peo_list = get_peo(dept, name)
            marks = get_max_marks(session[0]['uid'])

            subject_id = list(SubjectInfo.objects.filter(sem__sem=sem, sem__dept=dept, session=session[0]['uid']).exclude(status='DELETE').values('id', 'subject_type__value', 'sem', 'subject_type', 'sub_alpha_code', 'sub_num_code', 'sub_name'))

            for subject in subject_id:
                subject['po_data'] = []
                for po in po_list:
                    subject_overall_attain = get_subject_po_attainment(subject['id'], subject['subject_type'], po['id'], subject['sem'], name, session[0]['uid'])

                    subject['po_data'].append({'po_id': po['id'], 'po_num': po['po_level_abbr'], 'po_desc': po['description'], 'sub_po_attain': subject_overall_attain})
                subject_array.append(subject)

        data = get_po_peo_achieved_level(subject_array, dept, name, session[0]['uid'], batch)

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def co_po_target_report(request):

    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
        session = request.session['Session_id']
        session_name = request.session['Session_name']
        SubjectCOPOMapping = generate_session_table_name("SubjectCOPOMapping_", session_name)

        dept = request.GET['dept']
        subject_id = request.GET['subject_id']

        po_list = get_po(dept, session_name)
        co_list = get_co(subject_id, session_name)

        for po in po_list:
            po['co_data'] = []
            for co in co_list:
                co_map = list(SubjectCOPOMapping.objects.filter(co_id=co['id'], po_id=po['id']).exclude(status='DELETE').values('max_marks'))

                if co_map:
                    co['co_map'] = co_map[0]['max_marks']
                else:
                    co['co_map'] = None

                po['co_data'].append({'id': co['id'], 'description': co['description'], 'co_map': co['co_map']})

            po['target_level'] = get_subject_po_target_level(subject_id, po['id'], session_name, session)

        data = {'po_list': po_list, 'co_list': co_list}

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def peo_mi_attainment_report(request):
    if checkpermission(request, [rolesCheck.ROLE_HOD, rolesCheck.ROLE_DEAN]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isNBACoordinator(request) == True:
        dept = request.GET['dept']
        batch = request.GET['batch']
        batch_session = request.GET['batch_session'].split(",")
        batch_array = request.GET['batch'].split("-")
        batch_from = int(batch_array[0][2:])
        subject_array = []

        for name in batch_session:
            session = list(Semtiming.objects.filter(session_name=name).values('uid'))
            SubjectInfo = generate_session_table_name("SubjectInfo_", name)
            batch_till = int(name[:2])
            sem_type = name[-1:]
            po_list = get_po(dept, name)
            peo_list = get_peo(dept, name)

            if sem_type == 'o':
                plus_factor = 1
            else:
                plus_factor = 2

            sem = (2 * (batch_till - batch_from)) + plus_factor

            subject_id = list(SubjectInfo.objects.filter(sem__sem=sem, sem__dept=dept, session=session[0]['uid']).exclude(status='DELETE').values('id', 'subject_type__value', 'sem', 'subject_type', 'sub_alpha_code', 'sub_num_code', 'sub_name'))

            for subject in subject_id:
                subject['po_data'] = []
                for po in po_list:
                    subject_overall_attain = get_subject_po_attainment(subject['id'], subject['subject_type'], po['id'], subject['sem'], name, session[0]['uid'])

                    subject['po_data'].append({'po_id': po['id'], 'po_num': po['po_level_abbr'], 'po_desc': po['description'], 'sub_po_attain': subject_overall_attain})
                subject_array.append(subject)

        SubjectPEOMIMapping=generate_session_table_name("SubjectPEOMIMapping_",name)
        mission_list=get_mission(dept,name)
        data1=get_po_peo_achieved_level(subject_array,dept,name,session[0]['uid'],batch)
        mission_avg_data=peo_mi_avg(mission_list,dept,name)
        peo_data_list=data1['peo_list']
        marks = get_max_marks(session[0]['uid'])

        for peo in peo_data_list:
            peo['mission_data'] = []
            for mission in mission_list:
                peo_mapping = list(SubjectPEOMIMapping.objects.filter(peo_id=peo['id'], m_id=mission['id']).exclude(status='DELETE').values('marks'))
                if peo['achieved_level'] is not None and peo_mapping:
                    m =(peo['achieved_level']*peo_mapping[0]['marks'])/ float(marks[0]['value'])

                else:
                    m = None

                peo['mission_data'].append({'id': mission['id'], 'description': mission['description'], 'attained': m, 'mi_abbr': mission['m_level_abbr']})

        for mission in mission_avg_data:
            mission_sum = 0
            i = 0
            for peo in peo_data_list:
                for m in peo['mission_data']:
                    print(m, mission)
                    if m['description'] == mission['mission'] and m['attained'] is not None:
                        mission_sum += m['attained']
                        i += 1
            if mission_sum != 0 and i != 0:
                mission['avg_attained'] = mission_sum / i
            else:
                mission['avg_attained'] = None

            if mission['avg_attained'] is not None and mission['average'] is not None:
                mission['gap'] = mission['avg_attained'] - mission['average']
            else:
                mission['gap'] = None

        data = {'peo_list': peo_data_list, 'mission_list': mission_avg_data}

        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
