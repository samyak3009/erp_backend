from django.shortcuts import render

from StudentAcademics.models import *
from login.models import EmployeePrimdetail
from Registrar.models import StudentDropdown, StudentSemester, Sections, Semtiming


def StuAcadAttSettings_session_shift():
    data = list(AttendanceSettings.objects.filter(session=10).exclude(status='DELETE').exclude(att_sub_cat__status='DELETE').exclude(attendance_category__status='DELETE').values('session', 'att_sub_cat', 'att_sub_cat__field', 'att_sub_cat__value', 'att_sub_cat__is_edit', 'att_sub_cat__is_delete', 'att_sub_cat__status', 'attendance_category', 'attendance_category__field', 'attendance_category__value', 'attendance_category__is_edit', 'attendance_category__is_delete', 'admission_type', 'course', 'year', 'att_per', 'criteria_per', 'lock_type', 'days_lock', 'att_to_be_approved', 'status', 'added_by'))
    i = 0
    for d in data:
        new_att_sub_cat = list(StudentAcademicsDropdown.objects.filter(field=d['att_sub_cat__field'], value=d['att_sub_cat__value'], is_edit=d['att_sub_cat__is_edit'], is_delete=d['att_sub_cat__is_delete'], session=11).exclude(status='DELETE').values("sno"))
        new_att_cat = None
        if(d['attendance_category'] != None):
            q = StudentAcademicsDropdown.objects.filter(field=d['attendance_category__field'], value=d['attendance_category__value'], is_edit=d['attendance_category__is_edit'], is_delete=d['attendance_category__is_delete'], session=11).exclude(status='DELETE').values("sno")
            print(q)
            new_att_cat = StudentAcademicsDropdown.objects.get(sno=q[0]['sno'])
        if(len(new_att_sub_cat) > 0):
            i += 1
            qry_object = AttendanceSettings.objects.create(session=Semtiming.objects.get(uid=11), att_sub_cat=StudentAcademicsDropdown.objects.get(sno=new_att_sub_cat[0]['sno']), attendance_category=new_att_cat, admission_type=StudentDropdown.objects.get(sno=d['admission_type']), course=StudentDropdown.objects.get(sno=d['course']), year=d['year'], att_per=d['att_per'], criteria_per=d['criteria_per'], lock_type=d['lock_type'], days_lock=d['days_lock'], att_to_be_approved=d['att_to_be_approved'], status=d['status'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']))
    print("script completed")
# StuAcadAttSettings_session_shift()


def SubjectInfo_session_shift():
    data = list(SubjectInfo_1920e.objects.filter(session=9).exclude(status='DELETE').values('session', 'sem', 'subject_type', 'subject_unit', 'sub_alpha_code', 'sub_num_code', 'sub_name', 'max_ct_marks', 'max_ta_marks', 'max_att_marks', 'max_university_marks', 'no_of_units', 'status', 'added_by'))
    print("data length ",len(data))
    qry_object = (SubjectInfo_2021e(session=Semtiming.objects.get(uid=11), sem=StudentSemester.objects.get(sem_id=d['sem']), subject_type=StudentDropdown.objects.get(sno=d['subject_type']), subject_unit=StudentDropdown.objects.get(sno=d['subject_unit']), sub_alpha_code=d['sub_alpha_code'], sub_num_code=d['sub_num_code'], sub_name=d['sub_name'], max_ct_marks=d['max_ct_marks'], max_ta_marks=d['max_ta_marks'], max_att_marks=d['max_att_marks'], max_university_marks=d['max_university_marks'], no_of_units=d['no_of_units'], status=d['status'], added_by=EmployeePrimdetail.objects.get(emp_id=d['added_by']))for d in data)
    qry_create = SubjectInfo_2021e.objects.bulk_create(qry_object)
    print("script completed")

# SubjectInfo_session_shift()


def AcadCoordinator_session_shift():
    qry = AcadCoordinator_1920e.objects.filter(session=9).exclude(status='DELETE').values("section__sem_id__sem", "section__dept", "section__section", "section", "subject_id", 'subject_id__sem_id', 'subject_id__subject_type', 'subject_id__subject_unit', 'subject_id__sub_alpha_code', 'subject_id__sub_num_code', 'subject_id__sub_name', "coord_type", "emp_id", "added_by", 'status')
    print(len(qry))
    for q in qry:
        subject_id = None
        if q['subject_id'] != None:
            # old_sub = list(SubjectInfo_1819e.objects.filter(id=1947).values())[0]
            sub_id = SubjectInfo_2021e.objects.filter(sem=q['subject_id__sem_id'], subject_type=q['subject_id__subject_type'], subject_unit=q['subject_id__subject_unit'], sub_alpha_code=q['subject_id__sub_alpha_code'], sub_num_code=q['subject_id__sub_num_code'], sub_name=q['subject_id__sub_name']).values_list('id', flat=True)
            if len(sub_id) > 0:
                subject_id = SubjectInfo_2021e.objects.get(id=sub_id[0])
        # new_sem = int(q["section__sem_id__sem"])+2
        # if new_sem%2==0:
        # 	new_sec_id = list(Sections.objects.filter(sem_id__sem=new_sem,sem_id__dept=q['section__dept'],section=q["section__section"]).exclude(status="DELETE").values("section_id"))
        # 	print(new_sec_id)
        # 	if len(new_sec_id)>0:
        qry1 = AcadCoordinator_2021e.objects.create(session=Semtiming.objects.get(uid=11), section=Sections.objects.get(section_id=q['section']), subject_id=subject_id, coord_type=q["coord_type"], emp_id=EmployeePrimdetail.objects.get(emp_id=q["emp_id"]), status=q['status'], added_by=EmployeePrimdetail.objects.get(emp_id=q["added_by"]))
    print("script completed")
# AcadCoordinator_session_shift()


def TimeTableSlots_session_shift():
    qry = TimeTableSlots_1920e.objects.filter(session=9).exclude(status='DELETE').values('sem', 'day', 'num_lecture_slots', 'dean_approval_status', 'remark', 'status', 'added_by', 'time_stamp')
    print(len(qry))
    for q in qry:
        qry = TimeTableSlots_2021e.objects.create(session=Semtiming.objects.get(uid=11), sem=StudentSemester.objects.get(sem_id=q['sem']), day=q['day'], num_lecture_slots=q['num_lecture_slots'], dean_approval_status=q['dean_approval_status'], remark=q['remark'], status=q['status'], added_by=EmployeePrimdetail.objects.get(emp_id=q['added_by']))
    print("script completed")

# TimeTableSlots_session_shift()
