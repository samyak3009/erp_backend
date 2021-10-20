from django.shortcuts import render

from StudentMMS.models import *
from StudentAcademics.models import StudentAcademicsDropdown
from login.models import EmployeePrimdetail
from Registrar.models import CourseDetail, StudentSemester

from login.views import generate_session_table_name

import Scripts

# old_session = 8
# odd_old_session = 9
# new_session = 10
# old_session_name = '1920o'
# odd_old_session_name = '1920e'
# new_session_name = '2021o'
# static_sesison_for_2021o = 9



old_session = 9
odd_old_session = 10
new_session = 11
old_session_name = '1920e'
odd_old_session_name = '2021o'
new_session_name = '2021e'
static_sesison_for_2021o = 10
# print("heww")
# FOR EVEN SEM
# TABLES:---
# ['BTLevelSettings_1920e','QuesPaperFormat_1920e','QuesPaperSectionDetails_1920e','QuesPaperApplicableOn_1920e','QuesPaperBTAttainment_1920e','Dept_VisMis_1920e','SubjectCODetails_1920e','SubjectCODetailsAttainment_1920e','AttMarksRule_1920e','COAttainment1920e','MarksAttainmentSettings_1920e','AssignmentQuizMarks_1920e']


# from different sem_type
def shift_btlevel():
    # print("hello")
    old_table = generate_session_table_name('BTLevelSettings_', odd_old_session_name)
    new_table = generate_session_table_name('BTLevelSettings_', new_session_name)
    get_old_data = old_table.objects.filter(bt_level__session=static_sesison_for_2021o, skill_set_level__session=static_sesison_for_2021o).exclude(status="DELETE").values('bt_level', 'bt_level__field', 'bt_level__value', 'bt_level__pid', 'skill_set_level', 'skill_set_level__field', 'skill_set_level__value', 'skill_set_level__pid', 'verb', 'status', 'added_by', 'bt_num')
    print(len(get_old_data))
    for d in get_old_data:
        d['new_bt_level'] = None
        d['new_skill_set_level'] = None
        new_bt_level = StudentAcademicsDropdown.objects.filter(session=new_session, field=d['bt_level__field'], value=d['bt_level__value']).exclude(status="DELETE").values_list('sno', flat=True)
        if len(new_bt_level) > 0:
            d['new_bt_level'] = StudentAcademicsDropdown.objects.get(sno=new_bt_level[0])

        new_skill_set_level = StudentAcademicsDropdown.objects.filter(session=new_session, field=d['skill_set_level__field'], value=d['skill_set_level__value']).exclude(status="DELETE").values_list('sno', flat=True)
        if len(new_skill_set_level) > 0:
            d['new_skill_set_level'] = StudentAcademicsDropdown.objects.get(sno=new_skill_set_level[0])

        new_table.objects.create(bt_level=d['new_bt_level'], skill_set_level=d['new_skill_set_level'], verb=d['verb'], status=d['status'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']), bt_num=d['bt_num'])
    print("script completed")
# shift_btlevel()


# from same sem_type
def shift_dept_vis_mis():
    # print("sam")
    old_table = generate_session_table_name('Dept_VisMis_', old_session_name)
    new_table = generate_session_table_name('Dept_VisMis_', new_session_name)
    get_old_data = old_table.objects.exclude(status="DELETE").values('dept', 'type', 'description', 'status', 'added_by')
    print(len(get_old_data))
    qry = (new_table(dept=CourseDetail.objects.get(uid=d['dept']), type=d['type'], description=d['description'], status=d['status'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']))for d in get_old_data)
    new_table.objects.bulk_create(qry)
    print("script completed vismis")

# shift_dept_vis_mis()


# from different sem_type
def shift_quespaper_format_all_data():
    # print("sssss")
    old_table = generate_session_table_name('QuesPaperFormat_', odd_old_session_name)
    new_table = generate_session_table_name('QuesPaperFormat_', new_session_name)

    quespaper_section_old = generate_session_table_name('QuesPaperSectionDetails_', odd_old_session_name)
    quespaper_section_new = generate_session_table_name('QuesPaperSectionDetails_', new_session_name)

    quespaper_applicable_old = generate_session_table_name('QuesPaperApplicableOn_', odd_old_session_name)
    quespaper_applicable_new = generate_session_table_name('QuesPaperApplicableOn_', new_session_name)

    quespaper_btatt_old = generate_session_table_name('QuesPaperBTAttainment_', odd_old_session_name)
    quespaper_btatt_new = generate_session_table_name('QuesPaperBTAttainment_', new_session_name)

    get_old_data = old_table.objects.filter(exam_id__session=odd_old_session).exclude(status="DELETE").values('id', 'exam_id', 'exam_id__field', 'exam_id__value', 'exam_id__pid', 'added_by', 'time', 'status')
    for d in get_old_data:
        d['new_exam_id'] = None
        new_exam_id = StudentAcademicsDropdown.objects.filter(session=new_session, field=d['exam_id__field'], value=d['exam_id__value']).exclude(status="DELETE").values_list('sno', flat=True)
        if len(new_exam_id) > 0:
            d['new_exam_id'] = StudentAcademicsDropdown.objects.get(sno=new_exam_id[0])

        new_qry = new_table.objects.create(exam_id=d['new_exam_id'], status=d['status'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']), time=d['time'])
        d['new_id'] = new_qry.id

        quespaper_section_old_data = quespaper_section_old.objects.filter(ques_paper_id=d['id']).values('name', 'attempt_type', 'max_marks')
        d['quespaper_section_old_data'] = quespaper_section_old_data

        quespaper_applicable_old_data = quespaper_applicable_old.objects.filter(ques_paper_id=d['id']).values('sem', 'sem__sem', 'sem__dept')
        for s in quespaper_applicable_old_data:
            s['new_sem'] = None
            if int(s['sem__sem']) % 2 != 0:
                new_sem = int(s['sem__sem']) + 1
            else:
                new_sem = int(s['sem__sem']) - 1
            new_sem_id = StudentSemester.objects.filter(dept=s['sem__dept'], sem=new_sem).values('sem_id')
            if len(new_sem_id) > 0:
                s['new_sem'] = StudentSemester.objects.get(sem_id=new_sem_id[0]['sem_id'])
        d['quespaper_applicable_old_data'] = quespaper_applicable_old_data

        quespaper_btatt_old_data = quespaper_btatt_old.objects.filter(ques_paper_id=d['id']).values('bt_level', 'bt_level__field', 'bt_level__value', 'minimum', 'maximum')
        for bt in quespaper_btatt_old_data:
            bt['new_bt_level'] = None
            new_bt = StudentAcademicsDropdown.objects.filter(field=bt['bt_level__field'], value=bt['bt_level__value'], session=new_session).exclude(status="DELETE").values('sno')
            if len(new_bt) > 0:
                bt['new_bt_level'] = StudentAcademicsDropdown.objects.get(sno=new_bt[0]['sno'])
        d['quespaper_btatt_old_data'] = quespaper_btatt_old_data

    section_data_qry = (quespaper_section_new(ques_paper_id=new_table.objects.get(id=d['new_id']), name=section_data['name'], attempt_type=section_data['attempt_type'], max_marks=section_data['max_marks'])for d in get_old_data for section_data in d['quespaper_section_old_data'])
    quespaper_section_new.objects.bulk_create(section_data_qry)

    applicable_data_qry = (quespaper_applicable_new(ques_paper_id=new_table.objects.get(id=d['new_id']), sem=applicable_data['new_sem'])for d in get_old_data for applicable_data in d['quespaper_applicable_old_data'])
    quespaper_applicable_new.objects.bulk_create(applicable_data_qry)

    btatt_data_qry = (quespaper_btatt_new(ques_paper_id=new_table.objects.get(id=d['new_id']), bt_level=btatt_data['new_bt_level'], minimum=btatt_data['minimum'], maximum=btatt_data['maximum'])for d in get_old_data for btatt_data in d['quespaper_btatt_old_data'])
    quespaper_btatt_new.objects.bulk_create(btatt_data_qry)
    print("script completed")
# shift_quespaper_format_all_data()


# from different sem_type
def shift_attmarks_rule():
    old_table = generate_session_table_name('AttMarksRule_', odd_old_session_name)
    new_table = generate_session_table_name('AttMarksRule_', new_session_name)

    get_old_data = old_table.objects.exclude(status="DELETE").values('sem', 'sem__sem', 'sem__dept', 'subject_type', 'from_att_per', 'to_att_per', 'marks', 'max_att_marks', 'status')
    # print(len(get_old_data))
    for d in get_old_data:
        d['new_sem'] = None
        if d['sem__sem'] % 2 != 0:
            new_sem = int(d['sem__sem']) + 1
            new_sem_id = StudentSemester.objects.filter(dept=d['sem__dept'], sem=new_sem).values('sem_id')
            if len(new_sem_id) > 0:
                d['new_sem'] = StudentSemester.objects.get(sem_id=new_sem_id[0]['sem_id'])
    objs = ((new_table(sem=d['new_sem'], subject_type=StudentDropdown.objects.get(sno=d['subject_type']), from_att_per=d['from_att_per'], to_att_per=d['to_att_per'], marks=d['marks'], max_att_marks=d['max_att_marks'], status=d['status'])) for d in get_old_data)
    qry = new_table.objects.bulk_create(objs)
    print("qry completed")
# shift_attmarks_rule()


# from different sem_type
def shift_bonus_marks_rule():
    BonusMarks_External_old = generate_session_table_name('BonusMarks_External_', odd_old_session_name)
    BonusMarks_External_new = generate_session_table_name('BonusMarks_External_', new_session_name)

    BonusMarks_Internal_old = generate_session_table_name('BonusMarks_Internal_', odd_old_session_name)
    BonusMarks_Internal_new = generate_session_table_name('BonusMarks_Internal_', new_session_name)

    BonusMarks_InternalExam_old = generate_session_table_name('BonusMarks_InternalExam_', odd_old_session_name)
    BonusMarks_InternalExam_new = generate_session_table_name('BonusMarks_InternalExam_', new_session_name)

    BonusMarks_Attendance_old = generate_session_table_name('BonusMarks_Attendance_', odd_old_session_name)
    BonusMarks_Attendance_new = generate_session_table_name('BonusMarks_Attendance_', new_session_name)

    BonusMarks_AttendanceAtt_type_old = generate_session_table_name('BonusMarks_AttendanceAtt_type_', odd_old_session_name)
    BonusMarks_AttendanceAtt_type_new = generate_session_table_name('BonusMarks_AttendanceAtt_type_', new_session_name)

    BonusMarks_Subrule_old = generate_session_table_name('BonusMarks_Subrule_', odd_old_session_name)
    BonusMarks_Subrule_new = generate_session_table_name('BonusMarks_Subrule_', new_session_name)

    BonusMarks_Applicable_On_old = generate_session_table_name('BonusMarks_Applicable_On_', odd_old_session_name)
    BonusMarks_Applicable_On_new = generate_session_table_name('BonusMarks_Applicable_On_', new_session_name)

    BonusMarks_Rule_old = generate_session_table_name('BonusMarks_Rule_', odd_old_session_name)
    BonusMarks_Rule_new = generate_session_table_name('BonusMarks_Rule_', new_session_name)


# from different sem_type
def shift_ct_marks_rule():

    CTMarksRules_old = generate_session_table_name('CTMarksRules_', odd_old_session_name)
    CTMarks_Group_ExamInfo_old = generate_session_table_name('CTMarks_Group_ExamInfo_', odd_old_session_name)
    CTMarks_Group_ExamInfo_new = generate_session_table_name('CTMarks_Group_ExamInfo_', new_session_name)
    CTMarksRules_new = generate_session_table_name('CTMarksRules_', new_session_name)
    CTMarks_GroupInfo_old = generate_session_table_name('CTMarks_GroupInfo_', odd_old_session_name)
    CTMarks_GroupInfo_new = generate_session_table_name('CTMarks_GroupInfo_', new_session_name)

    get_old_data = CTMarksRules_old.objects.exclude(status='DELETE').values('sem', 'subject_type', 'rule_no', 'added_by', 'rule_criteria', 'status', 'sem__sem', 'sem__dept', 'id')

    CTMarks_GroupInfo_old = generate_session_table_name('CTMarks_GroupInfo_', odd_old_session_name)
    CTMarks_GroupInfo_new = generate_session_table_name('CTMarks_GroupInfo_', new_session_name)

    get_old_data = CTMarksRules_old.objects.exclude(status='DELETE').values('sem', 'subject_type', 'rule_no', 'added_by', 'rule_criteria', 'timestamp', 'status', 'sem__sem', 'sem__dept', 'id')

    for each in get_old_data:
        each['new_sem'] = None
        if each['sem__sem'] % 2 != 0:
            new_sem = int(each['sem__sem']) + 1
            new_sem_id = StudentSemester.objects.filter(dept=each['sem__dept'], sem=new_sem).values('sem_id')
            if len(new_sem_id) > 0:
                each['new_sem'] = StudentSemester.objects.get(sem_id=new_sem_id[0]['sem_id'])
        if each['new_sem'] is not None:
            create = CTMarksRules_new.objects.create(sem=each['new_sem'], subject_type=StudentDropdown.objects.get(sno=each['subject_type']), rule_no=each['rule_no'], added_by=EmployeePrimdetail.objects.get(emp_id=each['added_by']), rule_criteria=each['rule_criteria'], status=each['status'])

            get_old_group_data = CTMarks_GroupInfo_old.objects.exclude(status='DELETE').exclude(rule_id__status='DELETE').filter(rule_id__id=each['id']).values('group', 'weightage', 'ct_to_select', 'status', 'id')

            for e in get_old_group_data:

                insert_new_group = CTMarks_GroupInfo_new.objects.create(rule_id=CTMarksRules_new.objects.get(id=create.id), group=e['group'], weightage=e['weightage'], ct_to_select=e['ct_to_select'], status=e['status'])

                get_old_exam_data = CTMarks_Group_ExamInfo_old.objects.exclude(status='DELETE').exclude(group_id__rule_id__status='DELETE').exclude(group_id__status='DELETE').filter(group_id__id=e['id']).values('exam_id', 'status', 'id')
                for g in get_old_exam_data:
                    g['new_exam_id'] = None
                    exam_val = StudentAcademicsDropdown.objects.filter(sno=g['exam_id']).values('value')
                    if exam_val:
                        new_exam_id = StudentAcademicsDropdown.objects.filter(value=exam_val[0]['value'], session=new_session).values('sno')
                        if new_exam_id:
                            g['new_exam_id'] = StudentAcademicsDropdown.objects.get(sno=new_exam_id[0]['sno'])

                    inset_new = CTMarks_Group_ExamInfo_new.objects.create(group_id=CTMarks_GroupInfo_new.objects.get(id=insert_new_group.id), exam_id=g['new_exam_id'], status=g['status'])
    print("qry completed")

# shift_ct_marks_rule()


# from different sem_type
def shift_co_att_settings():
    old_table = generate_session_table_name('MarksAttainmentSettings_', odd_old_session_name)
    new_table = generate_session_table_name('MarksAttainmentSettings_', new_session_name)

    get_old_data = old_table.objects.exclude(status="DELETE").values('subject_type', 'sem', 'sem__sem', 'sem__dept', 'from_direct_per', 'to_indirect_per', 'external_marks', 'internal_marks', 'attainment_level', 'attainment_type', 'added_by', 'status')
    print(len(get_old_data))
    for d in get_old_data:
        d['new_sem'] = None
        if int(d['sem__sem']) % 2 != 0:
            new_sem = int(d['sem__sem']) + 1
        else:
            new_sem = int(d['sem__sem']) - 1
        new_sem_id = StudentSemester.objects.filter(dept=d['sem__dept'], sem=new_sem).values('sem_id')
        if len(new_sem_id) > 0:
            d['new_sem'] = StudentSemester.objects.get(sem_id=new_sem_id[0]['sem_id'])

    objs = (new_table(subject_type=StudentDropdown.objects.get(sno=d['subject_type']), sem=d['new_sem'], from_direct_per=d['from_direct_per'], to_indirect_per=d['to_indirect_per'], external_marks=d['external_marks'], internal_marks=d['internal_marks'], attainment_level=d['attainment_level'], attainment_type=d['attainment_type'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']), status=d['status']) for d in get_old_data)
    qry = new_table.objects.bulk_create(objs)
    print("qry completed")
# shift_co_att_settings()


# from same sem_type
def shift_co_details():
    # print("sam")
    SubjectCODetails_old = generate_session_table_name('SubjectCODetails_', old_session_name)
    SubjectCODetails_new = generate_session_table_name('SubjectCODetails_', new_session_name)

    SubjectInfo_new = generate_session_table_name('SubjectInfo_', new_session_name)

    SubjectCODetailsAttainment_old = generate_session_table_name('SubjectCODetailsAttainment_', old_session_name)
    SubjectCODetailsAttainment_new = generate_session_table_name('SubjectCODetailsAttainment_', new_session_name)

    get_old_co_data = SubjectCODetails_old.objects.exclude(status="DELETE").values('id', 'co_num', 'subject_id', 'subject_id__sem', 'subject_id__subject_type', 'subject_id__subject_unit', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', 'description', 'status', 'added_by')
    for d in get_old_co_data:
        d['subject_co_data'] = []
        d['new_subject'] = None
        d['new_co_id'] = None
        new_subject = SubjectInfo_new.objects.filter(subject_type=d['subject_id__subject_type'], subject_unit=d['subject_id__subject_unit'], sub_alpha_code=d['subject_id__sub_alpha_code'],sem=d['subject_id__sem'], sub_num_code=d['subject_id__sub_num_code'], sub_name=d['subject_id__sub_name'],).exclude(status="DELETE").values('id')
        if len(new_subject) > 0:
            d['new_subject'] = SubjectInfo_new.objects.get(id=new_subject[0]['id'])

        new_co_id = SubjectCODetails_new.objects.create(co_num=d['co_num'], subject_id=d['new_subject'], description=d['description'], status=d['status'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']))
        d['new_co_id'] = new_co_id.id
        subject_co_data = SubjectCODetailsAttainment_old.objects.filter(co_id=d['id']).exclude(status="DELETE").values('co_id', 'attainment_per', 'attainment_method', 'attainment_method__field', 'attainment_method__value', 'status')

        d['subject_co_data'] = subject_co_data
        for sub in subject_co_data:
            sub['new_attainment_method'] = None
            new_attainment_method = StudentAcademicsDropdown.objects.filter(field=sub['attainment_method__field'], value=sub['attainment_method__value'], session=new_session).exclude(status="DELETE").values('sno')
            if len(new_attainment_method) > 0:
                sub['new_attainment_method'] = StudentAcademicsDropdown.objects.get(sno=new_attainment_method[0]['sno'])
    objs = (SubjectCODetailsAttainment_new(co_id=SubjectCODetails_new.objects.get(id=d['new_co_id']), attainment_per=sub['attainment_per'], attainment_method=sub['new_attainment_method'], status=sub['status'])for d in get_old_co_data for sub in d['subject_co_data'])
    SubjectCODetailsAttainment_new.objects.bulk_create(objs)
    print("qry completed")
# shift_co_details()  


# from same sem_type
def shift_survey_question():
    # print("r")
    old_table = generate_session_table_name('SurveyAddQuestions_', old_session_name)
    new_table = generate_session_table_name('SurveyAddQuestions_', new_session_name)

    Dept_VisMis_new = generate_session_table_name('Dept_VisMis_', new_session_name)

    get_old_data = old_table.objects.exclude(status="DELETE").values('survey_id', 'survey_id__field', 'survey_id__value', 'description', 'sem_id', 'sem_id__sem', 'sem_id__dept', 'question_img', 'po_id', 'po_id__dept', 'po_id__type', 'po_id__description', 'status', 'added_by')
    for d in get_old_data:
        d['new_survey_id'] = None
        new_survey_id = StudentAcademicsDropdown.objects.filter(field=d['survey_id__field'], value=d['survey_id__value'], session=new_session).exclude(status="DELETE").values('sno')
        if len(new_survey_id) > 0:
            d['new_survey_id'] = StudentAcademicsDropdown.objects.get(sno=new_survey_id[0]['sno'])

        d['new_sem_id'] = None
        if int(d['sem_id__sem']) % 2 != 0:
            new_sem = int(d['sem_id__sem']) + 1
        else:
            new_sem = int(d['sem_id__sem']) - 1
        new_sem_id = StudentSemester.objects.filter(sem=new_sem, dept=d['sem_id__dept']).values('sem_id')
        if len(new_sem_id) > 0:
            d['new_sem_id'] = StudentSemester.objects.get(sem_id=new_sem_id[0]['sem_id'])

        d['new_po_id'] = None
        new_po_id = Dept_VisMis_new.objects.filter(type=d['po_id__type'], description=d['po_id__description'], dept=d['po_id__dept']).exclude(status="DELETE").values('id')
        if len(new_po_id) > 0:
            d['new_po_id'] = Dept_VisMis_new.objects.get(id=new_po_id[0]['id'])

    objs = (new_table(survey_id=d['new_survey_id'], description=d['description'], sem_id=d['new_sem_id'], question_img=d['question_img'], po_id=d['new_po_id'], status=d['status'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']))for d in get_old_data)
    qry = new_table.objects.bulk_create(objs)
    print("qry completed")
# shift_survey_question()



# from same sem_type
# def shift_questions():
#     SubjectAddQuestions_old = generate_session_table_name('SubjectAddQuestions_',old_session_name)
#     SubjectAddQuestions_new = generate_session_table_name('SubjectAddQuestions_',new_session_name)

#     SubjectQuesOptions_old = generate_session_table_name('SubjectQuesOptions_',old_session_name)
#     SubjectQuesOptions_new = generate_session_table_name('SubjectQuesOptions_',new_session_name)

#     get_old_data = SubjectAddQuestions_old.objects.exclude(status="DELETE").values('subject_id','subject_id__sub_num_code','subject_id__subject_unit','subject_id__subject_type','subject_id__sub_name','subject_id__sub_alpha_code','type','description','question_img','max_marks','co_id__co_num','co_id__subject_id','co_id__description','bt_level','bt_level__value','bt_level__field')
# shift_questions()


def shift_copo_mapping():
    old_table = generate_session_table_name('SubjectCOPOMapping_', old_session_name)
    new_table = generate_session_table_name('SubjectCOPOMapping_', new_session_name)

    Subject_new = generate_session_table_name('SubjectInfo_', new_session_name)
    # SubjectCODetails_old=generate_session_table_name('SubjectCODetails_', old_session_name)
    SubjectCODetails_new=generate_session_table_name('SubjectCODetails_', new_session_name)
    Dept_VisMis_new = generate_session_table_name('Dept_VisMis_', new_session_name)
    get_old_data=old_table.objects.exclude(status='DELETE').exclude(co_id__status='DELETE').exclude(co_id__subject_id__status='DELETE').exclude(po_id__status='DELETE').values('co_id__subject_id__sub_alpha_code','co_id__subject_id__sub_num_code','co_id__subject_id__sub_name','co_id__subject_id__id','po_id__dept','po_id__description','po_id__type','co_id__subject_id__sem','co_id__description','co_id__status','co_id__co_num','co_id__subject_id__session','max_marks','added_by','status','id')
    bulk_data=[]
    count =0
    print(len(get_old_data))
    for data in get_old_data:
        obj={}
        # print(data)
        sub_new_data=list(Subject_new.objects.filter(sub_alpha_code=data['co_id__subject_id__sub_alpha_code'],sub_num_code=data['co_id__subject_id__sub_num_code'],sub_name=data['co_id__subject_id__sub_name'],sem=data['co_id__subject_id__sem'],session=new_session).exclude(status='DELETE').values('id'))
        # print(sub_new_data)
        new_co_details=SubjectCODetails_new.objects.filter(subject_id=sub_new_data[0]['id'],description=data['co_id__description'],co_num=data['co_id__co_num']).exclude(status="DELETE").values('id')

        new_po_id=Dept_VisMis_new.objects.filter(dept=data['po_id__dept'],type=data['po_id__type'],description=data['po_id__description']).exclude(status="DELETE").values('id')

        if(len(new_co_details)>0 and len(new_po_id)>0 ):
            obj['co_id']=new_co_details[0]['id']
            obj['po_id']=new_po_id[0]['id']
            obj['max_marks']=data['max_marks']
            obj['added_by']=data['added_by']
            obj['status']=data['status']
        if(len(obj)>0):
            bulk_data.append(obj)
    
        
    # print(bulk_data)
    qry=(new_table(co_id=SubjectCODetails_new.objects.get(id=d['co_id']),po_id=Dept_VisMis_new.objects.get(id=d['po_id']),max_marks=d['max_marks'],added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']),status=d['status'])for d in bulk_data)
    # print(qry)
    bulk_create=new_table.objects.bulk_create(qry)
    print("qry completed")
# shift_copo_mapping()   


#same semester
def shift_peomi_mapping():
    old_table = generate_session_table_name('SubjectPEOMIMapping_', old_session_name)
    new_table = generate_session_table_name('SubjectPEOMIMapping_', new_session_name)
    Dept_VisMis_new = generate_session_table_name('Dept_VisMis_', new_session_name)

    get_old_data = old_table.objects.exclude(status='DELETE').values('id','marks','status','added_by','m_id__id','m_id__dept','m_id__type','m_id__description','peo_id__id','peo_id__dept','peo_id__type','peo_id__description')
    bulk_data= []
    print(len(get_old_data))
    for data in get_old_data:
        obj ={}
        new_peo_id = Dept_VisMis_new.objects.filter(dept=data['peo_id__dept'],type=data['peo_id__type'],description=data['peo_id__description']).exclude(status="DELETE").values('id')
        print(new_peo_id)
        new_m_id = Dept_VisMis_new.objects.filter(dept=data['m_id__dept'],type=data['m_id__type'],description=data['m_id__description']).exclude(status="DELETE").values('id')
        print(new_m_id)
        if(len(new_m_id)>0 and len(new_peo_id)>0):
            obj['m_id']  = new_m_id[0]['id']
            obj['peo_id'] = new_peo_id[0]['id']
            obj['marks'] = data['marks']
            obj['status'] = data['status']
            obj['added_by'] = data['added_by']
        if(len(obj)>0):
            bulk_data.append(obj)
    print(bulk_data)
    qry = (new_table(peo_id = Dept_VisMis_new.objects.get(id=d['peo_id']),m_id = Dept_VisMis_new.objects.get(id=d['m_id']),marks=d['marks'],added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']),status=d['status']) for d in bulk_data)
    bulk_create = new_table.objects.bulk_create(qry)
    print("qry completed") 
# shift_peomi_mapping()



  #same semester
def shift_popeo_mapping():
    old_table = generate_session_table_name('SubjectPOPEOMapping_', old_session_name)
    new_table = generate_session_table_name('SubjectPOPEOMapping_', new_session_name)
    Dept_VisMis_new = generate_session_table_name('Dept_VisMis_', new_session_name)

    get_old_data = old_table.objects.exclude(status='DELETE').values('id','marks','status','added_by','po_id__id','po_id__dept','po_id__type','po_id__description','peo_id__id','peo_id__dept','peo_id__type','peo_id__description')
    print(len(get_old_data))
    bulk_data= []
    for data in get_old_data:
        obj ={}
        new_peo_id = Dept_VisMis_new.objects.filter(dept=data['peo_id__dept'],type=data['peo_id__type'],description=data['peo_id__description']).exclude(status="DELETE").values('id')
        new_po_id = Dept_VisMis_new.objects.filter(dept=data['po_id__dept'],type=data['po_id__type'],description=data['po_id__description']).exclude(status="DELETE").values('id')
        if(len(new_po_id)>0 and len(new_peo_id)>0):
            obj['po_id']  = new_po_id[0]['id']
            obj['peo_id'] = new_peo_id[0]['id']
            obj['marks'] = data['marks']
            obj['status'] = data['status']
            obj['added_by'] = data['added_by']
        if(len(obj)>0):
            bulk_data.append(obj)
    qry = (new_table(peo_id = Dept_VisMis_new.objects.get(id=d['peo_id']),po_id = Dept_VisMis_new.objects.get(id=d['po_id']),marks=d['marks'],added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']),status=data['status']) for d in bulk_data)
    bulk_create = new_table.objects.bulk_create(qry)
    print("qry completed")
# shift_popeo_mapping()



#########################################_Questions_Table_Shift_#############################################################

#same sem 
def subject_add_question():
    old_table = generate_session_table_name('SubjectAddQuestions_',old_session_name)
    new_table = generate_session_table_name('SubjectAddQuestions_',new_session_name)
    Subject_new = generate_session_table_name('SubjectInfo_', new_session_name)
    SubjectCODetails_new=generate_session_table_name('SubjectCODetails_', new_session_name)
    get_old_data = old_table.objects.exclude(status='DELETE').values('id','subject_id','subject_id__sub_alpha_code','subject_id__sub_num_code','type','subject_id__sub_name','subject_id__sem','description','question_img','max_marks','co_id__id','co_id__description','co_id__co_num','bt_level','bt_level__value','bt_level__field','answer_key','answer_img','approval_status','status','added_by','time_stamp')
    bulk_data = []
    print('started')
    for data in get_old_data:
        obj = {}
        sub_new_data=Subject_new.objects.filter(sub_alpha_code=data['subject_id__sub_alpha_code'],sub_num_code=data['subject_id__sub_num_code'],sub_name=data['subject_id__sub_name'],sem=data['subject_id__sem'],session=new_session).exclude(status='DELETE').values('id')
        print(sub_new_data)
        print('pppp')
        new_co_details=SubjectCODetails_new.objects.filter(subject_id=sub_new_data[0]['id'],description=data['co_id__description'],co_num=data['co_id__co_num']).exclude(status="DELETE").values('id')
        if(data['bt_level__field'] == 'BLOOM TAXONOMY LEVEL'):
            if(data['bt_level__value'] == 'BL-1: KNOWLEDGE'):
                data['bt_level__value'] = 'REMEMBER'
            elif(data['bt_level__value'] == 'BL-2:  COMPREHENSION'):
                data['bt_level__value'] = 'UNDERSTAND'
            elif(data['bt_level__value'] == 'BL-3 :  APPLICATION'):
                data['bt_level__value'] = 'APPLY'
            elif(data['bt_level__value'] == 'BL-4:  ANALYSIS'):
                data['bt_level__value'] = 'ANALYZE'
            elif(data['bt_level__value']== 'BL-5: SYNTHESIS'):
                data['bt_level__value'] = 'CREATE'
            elif(data['bt_level__value'] == 'BL-6: EVALUATION'):
                data['bt_level__value'] = 'EVALUATE'    
        new_bt_level = StudentAcademicsDropdown.objects.filter(session=new_session, field=data['bt_level__field'], value=data['bt_level__value']).exclude(status="DELETE").values_list('sno', flat=True)
        if(len(new_co_details)>0 and len(sub_new_data)>0 and len(new_bt_level)>0):
            obj['subject_id'] = sub_new_data[0]['id']
            obj['type'] = data['type']
            obj['description'] = data['description']
            obj['question_img'] = data['question_img']
            obj['max_marks'] = data['max_marks']
            obj['co_id'] = new_co_details[0]['id']
            obj['bt_level'] = new_bt_level[0]
            obj['answer_key'] = data['answer_key']
            obj['answer_img'] = data['answer_img']
            obj['approval_status'] = data['approval_status']
            obj['status'] = data['status']
            obj['added_by'] = data['added_by']
            obj['time_stamp'] = data['time_stamp']
        if(len(obj)>0):
            bulk_data.append(obj)
    qry = (new_table(subject_id = Subject_new.objects.get(id=d['subject_id']), type=d['type'], description=d['description'], question_img=d['question_img'], max_marks=d['max_marks'], co_id = SubjectCODetails_new.objects.get(id=d['co_id']), bt_level=StudentAcademicsDropdown.objects.get(sno=d['bt_level']), answer_key=d['answer_key'], answer_img=d['answer_img'], approval_status=d['approval_status'], status=d['status'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']), time_stamp=d['time_stamp']) for d in bulk_data)
    bulk_create = new_table.objects.bulk_create(qry)
    print('completed')
# subject_add_question()


# def subject_ques_options():
#     old_table = generate_session_table_name('SubjectQuesOptions_',old_session)
#     new_table = generate_session_table_name('SubjectQuesOptions_',new_session)
#     SubjectAdd_new = generate_session_table_name('SubjectAddQuestions_',new_session)

#     get_old_data = old_table.objects.exclude(status='DELETE').values('ques_id','option_description','option_img','is_answer')

#     bulk_data = []
#     for data in bulk_data:

#         new_ques_id = SubjectAdd_new.objects.filter()







    
    




