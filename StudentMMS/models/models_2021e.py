from django.db import models
# Create your models here.
from StudentAcademics.models.models import *
from StudentAcademics.models.models_2021e import *
from Registrar.models import *
from login.models import EmployeePrimdetail
from django_mysql.models import JSONField



class ExamSchedule_2021e(models.Model):
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='ExamSchedule_2021e_id', null=True, on_delete=models.SET_NULL)
    sem = models.ForeignKey(StudentSemester, related_name='ExamSchedule_2021e_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    detained_attendance = models.FloatField(default=None, null=True)
    subject_type = models.ForeignKey(StudentDropdown, related_name='exam_Subject_type_2021e', db_column='Subject_type', null=True, on_delete=models.SET_NULL)
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_exam_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSExamSchedule_2021e'
        managed = True


class BTLevelSettings_2021e(models.Model):
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='bt_level_2021e', null=True, on_delete=models.SET_NULL)
    skill_set_level = models.ForeignKey(StudentAcademicsDropdown, related_name='skill_set_level_level_2021e', null=True, on_delete=models.SET_NULL)
    verb = models.CharField(max_length=1000, default='')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_bt_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)
    bt_num = models.IntegerField(default=1)

    class Meta:
        db_table = 'StuMMSBTLevelSettings_2021e'
        managed = True


class QuesPaperFormat_2021e(models.Model):
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_id_qp_2021e', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_qp_2021e', null=True, on_delete=models.SET_NULL)
    time = models.TimeField(default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSQuesPaperFormat_2021e'
        managed = True


class QuesPaperSectionDetails_2021e(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_2021e, related_name='ques_paper_id_2021e', null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=1000, default=None, null=True)
    attempt_type = models.CharField(max_length=5, default=None)  # 'M' for mandatory, 'I' for internal choice, 'O' for overall choice
    max_marks = models.FloatField()
    min_marks_per = models.FloatField(null=True)
    class Meta:
        db_table = 'StuMMSQuesPaperSectionDetails_2021e'
        managed = True


class QuesPaperApplicableOn_2021e(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_2021e, related_name='ques_paper_id_app_2021e', null=True, on_delete=models.SET_NULL)
    sem = models.ForeignKey(StudentSemester, related_name='ques_paper_id_sem_2021e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'StuMMSQuesPaperApplicableOn_2021e'
        managed = True


class QuesPaperBTAttainment_2021e(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_2021e, related_name='ques_paper_id_bt_att_2021e', null=True, on_delete=models.SET_NULL)
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='ques_paper_id_bt_level_2021e', null=True, on_delete=models.SET_NULL)
    minimum = models.FloatField()
    maximum = models.FloatField()

    class Meta:
        db_table = 'StuMMSQuesPaperBTAttainment_2021e'
        managed = True


class Dept_VisMis_2021e(models.Model):
    dept = models.ForeignKey(CourseDetail, related_name='Dept_VisMis_2021e', db_column='dept', blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=10, default='V')  # 'V' for Vision, 'M' for mission, 'QP' for quality policy,'PEO' for PEO's, 'PO' for PO's
    description = models.TextField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_vis_mis_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSDept_VisMis_2021e'
        managed = True


class SubjectCODetails_2021e(models.Model):
    co_num = models.IntegerField(default=1)
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="SubjectCODetails_2021e", null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_co_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCODetails_2021e'
        managed = True


class SubjectCODetailsAttainment_2021e(models.Model):
    co_id = models.ForeignKey(SubjectCODetails_2021e, related_name="SubjectCOAttain_2021e", on_delete=models.SET_NULL, null=True)
    attainment_per = models.FloatField(null=True, default=None)
    attainment_method = models.ForeignKey(StudentAcademicsDropdown, related_name='DirectAttainmentMethod_2021e', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCOAttainment_2021e'
        managed = True


class SubjectCOPOMapping_2021e(models.Model):
    co_id = models.ForeignKey(SubjectCODetails_2021e, related_name="SubjectCOMap_2021e", on_delete=models.SET_NULL, null=True)
    po_id = models.ForeignKey(Dept_VisMis_2021e, related_name="SubjectPOMap_2021e", on_delete=models.SET_NULL, null=True)
    max_marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_co_po_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCOPOMapping_2021e'
        managed = True


class SubjectPEOMIMapping_2021e(models.Model):
    m_id = models.ForeignKey(Dept_VisMis_2021e, related_name="SubjectPEOMIMap_2021e_mission", on_delete=models.SET_NULL, null=True)
    peo_id = models.ForeignKey(Dept_VisMis_2021e, related_name="SubjectPEOMIMap_2021e_peo", on_delete=models.SET_NULL, null=True)
    marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_peo_mi_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectPEOMIMapping_2021e'
        managed = True


class SubjectPOPEOMapping_2021e(models.Model):
    peo_id = models.ForeignKey(Dept_VisMis_2021e, related_name="SubjectPOPEOMap_2021e_peo", on_delete=models.SET_NULL, null=True)
    po_id = models.ForeignKey(Dept_VisMis_2021e, related_name="SubjectPOPEOMap_2021e_po", on_delete=models.SET_NULL, null=True)
    marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_po_peo_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectPOPEOMapping_2021e'
        managed = True


class SubjectAddQuestions_2021e(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="SubjectAddQuestions_2021e", on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, default='S')  # 'S' for Subjective, 'O' for Objective
    description = models.TextField()
    question_img = models.CharField(max_length=1000, default=None, null=True)
    max_marks = models.FloatField()
    co_id = models.ForeignKey(SubjectCODetails_2021e, related_name="SubjectQuesCO_2021e", on_delete=models.SET_NULL, null=True)
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='subject_ques_bt_2021e', null=True, on_delete=models.SET_NULL)
    answer_key = models.TextField(null=True)
    answer_img = models.CharField(max_length=1000, default=None, null=True)
    approval_status = models.CharField(max_length=20, default='PENDING')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_ques_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectAddQuestions_2021e'
        managed = True


class SubjectQuesOptions_2021e(models.Model):  # if question type is 'O' i.e. objective
    ques_id = models.ForeignKey(SubjectAddQuestions_2021e, related_name="SubjectAddQuestions_2021e", on_delete=models.SET_NULL, null=True)
    option_description = models.TextField()
    option_img = models.CharField(max_length=1000, default=None, null=True)
    is_answer = models.CharField(max_length=2, default='N')  # 'Y' if that option is answer

    class Meta:
        db_table = 'StuMMSSubjectQuesOptions_2021e'
        managed = True


class SubjectQuestionPaper_2021e(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="SubjectQuestionPaper_2021e_sub", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='SubjectQuestionPaper_2021e_exam', null=True, on_delete=models.SET_NULL)
    approval_status = models.CharField(max_length=20, default='PENDING')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_ques_paper_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectQuestionPaper_2021e'
        managed = True


class QuestionPaperQuestions_2021e(models.Model):
    ques_paper_id = models.ForeignKey(SubjectQuestionPaper_2021e, related_name="QuestionPaperQuestions_2021e_qpaper", on_delete=models.SET_NULL, null=True)
    section_id = models.ForeignKey(QuesPaperSectionDetails_2021e, related_name="QuestionPaperQuestions_2021e_section", on_delete=models.SET_NULL, null=True)
    ques_id = models.ForeignKey(SubjectAddQuestions_2021e, related_name="QuestionPaperQuestions_2021e_section", on_delete=models.SET_NULL, null=True)
    ques_num = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='SAVED')

    class Meta:
        db_table = 'StuMMSQuestionPaperQuestions_2021e'
        managed = True


class DeptExamSchedule_2021e(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='DeptExamSchedule_2021e_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="DeptExamSchedule_2021e_sub", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='DeptExamSchedule_2021e_exam', null=True, on_delete=models.SET_NULL)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exam_shift = models.ForeignKey(StudentAcademicsDropdown, related_name="DeptExamSchedule_2021e_shift", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='DeptExamSchedule_2021e_emp', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSDeptExamSchedule_2021e'
        managed = True


class Marks_2021e(models.Model):
    section = models.ForeignKey(Sections, related_name='Marks_section_2021e', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="MarkSub_id_2021e", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='MarksExamId_2021e', null=True, on_delete=models.SET_NULL)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="MarkEmp_2021e", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_2021e, related_name="MarkGid_2021e", null=True, on_delete=models.SET_NULL)
    normal_remedial = models.CharField(max_length=5, default='N')  # 'N' for normal, 'R' for remedial
    isgroup = models.CharField(max_length=5, default='N')
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSMarks_2021e'


class StudentMarks_2021e(models.Model):
    marks_id = models.ForeignKey(Marks_2021e, related_name='StuMarks_markid_2021e', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='StuMarks_uniqid_2021e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    present_status = models.CharField(max_length=2, default='P')
    ############# 'P' for present, 'A' for absent, 'D' for detained ###################################
    marks = models.FloatField(default=None, null=True)
    ############# if present_status='A' or 'D', then marks will be NULL ##############################
    ques_id = models.ForeignKey(QuestionPaperQuestions_2021e, related_name='StuMarksQuesId_2021e', db_column='ques_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSStudentMarks_2021e'


class StudentUniversityMarks_2021e(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="StuUniMarksSub_id_2021e", on_delete=models.SET_NULL, null=True)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="StuUniMarksAddedBy_2021e", null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='StuUniMarks_uniqid_2021e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    external_marks = models.CharField(max_length=10, default=None, null=True)
    internal_marks = models.CharField(max_length=10, default=None, null=True)
    back_marks = models.CharField(max_length=10, default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSStudentUnivMarks_2021e'


class AttMarksRule_2021e(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='attmarks_sem_2021e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    subject_type = models.ForeignKey(StudentDropdown, related_name='att_rule_subtype_2021e', db_column='Subject_type', on_delete=models.SET_NULL, null=True)
    from_att_per = models.FloatField()
    to_att_per = models.FloatField()
    marks = models.FloatField()
    max_att_marks = models.FloatField(default=None, null=True)
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSAttMarksRule_2021e'
        managed = True


class CTMarksRule_2021e(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='ctmarks_sem_2021e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    ct_group = models.CharField(max_length=500, default=None, null=True)  # comma separated ct ids
    subject_type = models.ForeignKey(StudentDropdown, related_name='ct_rule_subtype_2021e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    ct_to_select = models.IntegerField()
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSCTMarksRule_2021e'
        managed = True


class BonusMarksRule_2021e(models.Model):
    rule_name = models.CharField(max_length=100, default=None, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='bonusmarks_sem_2021e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    given_ct = models.CharField(max_length=500, default=None, null=True)  # comma separated ct ids
    min_marks_per = models.FloatField()
    min_att_per = models.FloatField(null=True, default=None)
    bonus_marks = models.FloatField(null=True, default=None)
    max_marks_limit_per = models.FloatField()
    subject_type = models.ForeignKey(StudentDropdown, related_name='bonusmarks_subtype_2021e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSBonusMarksRule_2021e'
        managed = True


class TAMarks_2021e(models.Model):
    section = models.ForeignKey(Sections, related_name='TAMarks_section_2021e', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="TAMarkSub_id_2021e", on_delete=models.SET_NULL, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="TAMarkEmp_2021e", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_2021e, related_name="TAMarkGid_2021e", null=True, on_delete=models.SET_NULL)
    isgroup = models.CharField(max_length=5, default='N')
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSTAMarks_2021e'


class StudentTAMarks_2021e(models.Model):
    ta_marks_id = models.ForeignKey(TAMarks_2021e, related_name='StuTAMarks_markid_2021e', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='StuTAMarks_uniqid_2021e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    ct_viva_marks = models.FloatField(default=None, null=True)
    ta_lab_marks = models.FloatField(default=None, null=True)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSTAStudentMarks_2021e'


class ExtraBonus_2021e(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='ExtraBonus_Uniqid_2021e', null=True, on_delete=models.SET_NULL)
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="ExtraBonusSub_id_2021e", on_delete=models.SET_NULL, null=True)
    bonus_marks = models.FloatField()
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="ExtraBonusEmp_2021e", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSExtraBonus_2021e'


class COAttainment_2021e(models.Model):
    attainment_num = models.IntegerField()
    subject_type = models.ForeignKey(StudentDropdown, related_name='COAttainmentSubjectType_2021e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='COAttainmentsem_2021e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    min_att_per = models.FloatField(null=True, default=None)
    max_att_per = models.FloatField(null=True, default=None)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="COAttainmentLevel_2021e", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSCOAttainmentLevel_2021e'


class MarksAttainmentSettings_2021e(models.Model):
    subject_type = models.ForeignKey(StudentDropdown, related_name='MarksAttainmentSubjectType_2021e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='MarksAttainmentsem_2021e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    from_direct_per = models.FloatField(null=True, default=None)  # from percentage for direct attainment settings and direct per for attainment proportion
    to_indirect_per = models.FloatField(null=True, default=None)  # to percentage for direct attainment settings and indirect per for attainment proportion
    external_marks = models.FloatField(null=True, default=None)
    internal_marks = models.FloatField(null=True, default=None)
    attainment_level = models.FloatField(null=True, default=None)
    attainment_type = models.CharField(null=True, default=None, max_length=5)  # D for direct attainment , A for attainment proportion
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="MarksAttainment_2021e", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSMarksAttainmentSettings_2021e'


class AssignmentQuizMarks_2021e(models.Model):
    section = models.ForeignKey(Sections, related_name='AssignmentMarks_section_2021e', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_2021e, related_name="AssignmentMarkSub_id_2021e", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='AssignmentMarksExamId_2021e', null=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="AssignmentMarkEmp_2021e", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_2021e, related_name="AssignmentMarkGid_2021e", null=True, on_delete=models.SET_NULL)
    isgroup = models.CharField(max_length=5, default='N')
    isco_wise = models.CharField(max_length=5, default='N')
    max_marks = models.FloatField(null=True, default=None)  # if marks entered is co_wise then it will be NULL ############
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSAssignmentMarks_2021e'


class AssignmentStudentMarks_2021e(models.Model):
    marks_id = models.ForeignKey(AssignmentQuizMarks_2021e, related_name='StuAssignmentMarks_markid_2021e', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='StuAssignmentMarks_uniqid_2021e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    present_status = models.CharField(max_length=2, default='P')
    ############# 'P' for present, 'A' for absent ###################################
    marks = models.FloatField(default=None, null=True)
    ############# if present_status='A', then marks will be NULL ##############################
    ques_id = models.ForeignKey(QuestionPaperQuestions_2021e, related_name='StuAssignmentMarksQuesId_2021e', db_column='ques_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSAssignmentStudentMarks_2021e'


class SurveyAddQuestions_2021e(models.Model):
    survey_id = models.ForeignKey(StudentAcademicsDropdown, related_name='SurveyAddQuestions_2021e_id', null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    sem_id = models.ForeignKey(StudentSemester, related_name='SurveyAddQuestions_2021e_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)
    question_img = models.CharField(max_length=1000, default=None, null=True)
    po_id = models.ForeignKey(Dept_VisMis_2021e, related_name="SurveyAddQuestions_2021e_po", on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_survey_ques_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSurveyAddQuestions_2021e'
        managed = True


class SurveyFillFeedback_2021e(models.Model):
    ques_id = models.ForeignKey(SurveyAddQuestions_2021e, related_name='SurveyFillFeedback_2021e_survey_id', null=True, on_delete=models.SET_NULL)
    feedback = models.IntegerField(default=1)  # 1 for not satisfied , 2 for satisfied , 3 for very satisfied####
    status = models.CharField(max_length=20, default='INSERT')
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='SurveyFillFeedback_uniqid_2021e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSurveyFillFeedback_2021e'
        managed = True


class StudentFinalMarksStatus_2021e(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='StuFinalMarks_uniqid_2021e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    Total_marks_obtained = models.CharField(max_length=30, default=None, null=True)
    Total_max_marks = models.CharField(max_length=30, default=None, null=True)
    Division_awarded = models.CharField(max_length=40, default=None, null=True)
    Result_status = models.CharField(max_length=40, default=None, null=True)
    Year_obtained = models.CharField(max_length=40, default=None, null=True)
    Year_total = models.CharField(max_length=40, default=None, null=True)

    class Meta:
        managed = True
        db_table = 'StuMMSFinalMarksStatus_2021e'


### CT-MARKS RULE ###


class CTMarksRules_2021e(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='ctmarks_rule_sem_2021e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    subject_type = models.ForeignKey(StudentDropdown, related_name='ctmarks_rule_subtype_2021e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    rule_no = models.IntegerField()
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_ctrule_2021e', null=True, on_delete=models.SET_NULL)
    rule_criteria = models.CharField(max_length=30, db_column='Rule_Criteria', null=True, blank=True, default="MAXIMUM")
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'CTMarksRules_2021e'


class CTMarks_GroupInfo_2021e(models.Model):
    rule_id = models.ForeignKey(CTMarksRules_2021e, related_name="ctmarks_rule_group_2021e", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    group = models.CharField(max_length=50, default=None)
    weightage = models.IntegerField()
    ct_to_select = models.IntegerField()
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'CTMarks_GroupInfo_2021e'


class CTMarks_Group_ExamInfo_2021e(models.Model):
    group_id = models.ForeignKey(CTMarks_GroupInfo_2021e, related_name="group_ctmarks_rule_2021e", db_column="group_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='ctmarks_rule_2021e', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'CTMarks_Group_ExamInfo_2021e'

###########################
#### BONUS MARKS RULE #####


class BonusMarks_Subrule_2021e(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    type_id = models.IntegerField(blank=True, null=True)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_bonusmarks_subrule_2021e', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'BonusMarks_Subrule_2021e'


class BonusMarks_External_2021e(models.Model):
    applicable_type = models.CharField(max_length=50, blank=True, null=True)  # OVERALL,PREVIOUS SEM,PREVIOS YEAR
    criteria = models.CharField(max_length=50, blank=True, null=True)  # PRECENTAGE, NUMBER OF STUDENTS
    range_type = models.CharField(max_length=50, blank=True, null=True)  # HIGHER,LOWER
    value = models.FloatField()
    # subrule_id = models.ForeignKey(BonusMarks_Subrule_2021e, related_name="subrule_bonusmarks_ext_2021e", db_column="subrule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'BonusMarks_External_2021e'


class BonusMarks_Internal_2021e(models.Model):
    min_range = models.IntegerField()
    max_range = models.IntegerField()
    # subrule_id = models.ForeignKey(BonusMarks_Subrule_2021e, related_name="subrule_bonusmarks_int_2021e", db_column="subrule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'BonusMarks_Internal_2021e'


class BonusMarks_InternalExam_2021e(models.Model):
    internal_id = models.ForeignKey(BonusMarks_Internal_2021e, related_name="int_bonusmarks_int_2021e", db_column="internal_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_bonusmarks_int_2021e', null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'BonusMarks_InternalExam_2021e'


class BonusMarks_Attendance_2021e(models.Model):
    min_range = models.IntegerField()
    max_range = models.IntegerField()
    # subrule_id = models.ForeignKey(BonusMarks_Subrule_2021e, related_name="subrule_bonusmarks_att_2021e", db_column="subrule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'BonusMarks_Attendance_2021e'


class BonusMarks_AttendanceAtt_type_2021e(models.Model):
    att_id = models.ForeignKey(BonusMarks_Attendance_2021e, related_name="att_bonusmarks_att_2021e", db_column="att_id", blank=True, null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_bonusmarks_att_2021e', null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'BonusMarks_AttendanceAtt_type_2021e'


class BonusMarks_Applicable_On_2021e(models.Model):
    sem_id = models.ForeignKey(StudentSemester, related_name="sem_bonusmarks_app_2021e", db_column="sem_id", blank=True, null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey(Sections, related_name="section_bonusmarks_app_2021e", db_column="section", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_2021e, related_name="subject_bonusmarks_app_2021e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'BonusMarks_Applicable_On_2021e'


class BonusMarks_Rule_2021e(models.Model):
    rule_no = models.IntegerField()
    app_id = models.ForeignKey(BonusMarks_Applicable_On_2021e, related_name="rule_bonusmarks_rule_2021e", db_column="app_id", blank=True, null=True, on_delete=models.SET_NULL)
    subrule_no = models.IntegerField()
    subrule_id = models.ForeignKey(BonusMarks_Subrule_2021e, related_name="subrule_bonusmarks_rule_2021e", db_column="subrule_id", blank=True, null=True, on_delete=models.SET_NULL)
    bonus_marks = models.FloatField()
    max_marks_limit = models.FloatField()  # bonus marks
    min_range = models.IntegerField()  # bonus marks
    max_range = models.IntegerField()  # bonus marks
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_bonusmarks_rule_2021e', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'BonusMarks_Rule_2021e'


class BonusMarks_2021e(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021e, related_name="uniq_id_bonus_marks_2021e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    # subject = models.ForeignKey(SubjectInfo_2021e, related_name="subject_bonus_marks_2021e", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    rule_id = models.ForeignKey(BonusMarks_Rule_2021e, related_name="rule_bonus_marks_2021e", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    total_bonus_marks = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSBonusMarks_2021e'


class BonusMarks_Students_2021e(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021e, related_name="uniq_id_bonusmarks_students_2021e", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    # app_id = models.ForeignKey(BonusMarks_Applicable_On_2021e, related_name="rule_bonusmarks_students_2021e", db_column="app_id", blank=True, null=True, on_delete=models.SET_NULL)
    rule_id = models.ForeignKey(BonusMarks_Rule_2021e, related_name="rule_bonusmarks_students_2021e", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'BonusMarks_Students_2021e'

###########################
################################## EXTERNAL SURVEY ###########################
# class ExternalSurvey(models.Model):
#     survey_id = models.ForeignKey(StudentAcademicsDropdown, related_name='ExternalSurvey_survey_id', null=True, on_delete=models.SET_NULL, db_column='Survey_Id')
#     batch_from = models.IntegerField(db_column='Batch_from')
#     batch_to = models.IntegerField(db_column='Batch_to')
#     created_by = models.ForeignKey(EmployeePrimdetail, related_name='ExternalSurvey_created_by', null=True, on_delete=models.SET_NULL, db_column='Created_By')
#     session = models.ForeignKey(Semtiming, related_name='ExternalSurvey_session', null=True, on_delete=models.SET_NULL, db_column='session')
#     status = models.CharField(max_length=20, default='INSERT')
#     dept = models.ForeignKey(CourseDetail, related_name='ExternalSurvey_dept_id',null=True,on_delete=models.SET_NULL,db_column='Dept')
#     class Meta:
#         managed = True
#         db_table = 'StuMMSExternalSurvey'


# class ExternalSurveyAttr(models.Model):
#     form_id = models.ForeignKey(ExternalSurvey, related_name='SurveyAttributes_id', null=True, on_delete=models.SET_NULL, db_column='Form_Id')
#     element_type = models.CharField(db_column='Element_type',max_length=20)
#     po_id = JSONField(null=True)
#     element_id = models.IntegerField(db_column='Element_Id')
#     attribute = JSONField()
#     class Meta:
#         managed = True
#         db_table = 'StuMMSExternalSurveyAttr'

# class ExternalSurveyAnsDetail(models.Model):
#     form_id = models.ForeignKey(ExternalSurvey,related_name='ExternalSurvey_form_id',null=True,on_delete=models.SET_NULL,db_column='form_id')
#     added_by = models.ForeignKey(EmployeePrimdetail,related_name='ExternalSurveyAnswer_created_by',null=True,on_delete=models.SET_NULL,db_column='added_by')
#     status = models.CharField(max_length=20, default='INSERT')
#     class Meta:
#         managed = True
#         db_table = 'StuMMSExternalSurveyAnsDetail'

# class ExternalSurveyAnswer(models.Model):
#     ques_id = models.ForeignKey(ExternalSurveyAttr,related_name='Element_que_Id',null=True,on_delete=models.SET_NULL,db_column='Ques_id')
#     ans_id = models.ForeignKey(ExternalSurveyAnsDetail,related_name='ExternalSurvey_nas_id',null=True,on_delete=models.SET_NULL,db_column='ans_id')
#     ans_attribute = JSONField()
#     class Meta:
#         managed = True
#         db_table = 'StuMMSExternalSurveyAnswer'

# class ExternalSurveySession(models.Model):
#     hash_code = models.CharField(db_column='hash_code', max_length=256)
#     expiry_date = models.DateField(db_column='expiry_date', blank=True, null=True)
#     form_status = models.IntegerField(db_column='form_status',default=0)
#     class Meta:
#         managed = True
#         db_table = 'StuMMSExternalSurveySession'


# class ExternalSurveyFeedback(models.Model):
#     feedback = models.IntegerField(db_column='feedback')
#     status = models.CharField(max_length=20,default='INSERT')
#     time_stamp = models.DateTimeField(auto_now=True)
#     ques_id = models.ForeignKey(ExternalSurveyAttr,related_name='feedback_que_id', null=True,on_delete=models.SET_NULL,db_column='ques_id')
#     ans_id = models.ForeignKey(ExternalSurveyAnswer,related_name='feedback_ans_id', null=True,on_delete=models.SET_NULL,db_column='ans_id')
#     class Meta:
#         managed = True
#         db_table = 'StuMMSExternalSurveyfeedback'

##################################################################################
########################################## faculty internal survey feedback######################################################

# class InternalFacSurvey(models.Model):
#     survey_id = models.ForeignKey(StudentAcademicsDropdown,related_name='InternalFacSurvey_Survey_id',null=True,on_delete=models.SET_NULL,db_column='survey_id')
#     session = models.ForeignKey(Semtiming,related_name='InternalFacSurvey_session',null=True,on_delete=models.SET_NULL,db_column='session')
#     created_by = models.ForeignKey(EmployeePrimdetail,related_name='InternalFacSurvey_createdby',null=True,on_delete=models.SET_NULL,db_column='created_by')
#     dept = models.ForeignKey(CourseDetail, related_name='InternalFacSurvey_dept_id',null=True,on_delete=models.SET_NULL,db_column='dept_id')  
#     category = models.ForeignKey(EmployeeDropdown, related_name='InternalFacSurvey_category', db_column='category', blank=True, null=True, on_delete=models.SET_NULL)
#     status = models.IntegerField(db_column='status',default=1)
#     time_stamp = models.DateTimeField(auto_now=True)
#     class Meta:
#         managed = True
#         db_table = 'StuMMSInternalFacSurvey'

# class InternalFacSurveyQuestion(models.Model):
#     form_id = models.ForeignKey(InternalFacSurvey,related_name='InternalFacSurveyQuestion_formid',null=True,on_delete=models.SET_NULL,db_column='form_id')
#     element_id = models.IntegerField(db_column='element_id')
#     po_id = JSONField(null=True)
#     ques = JSONField()
#     class Meta:
#         managed = True
#         db_table = 'StuMMSInternalFacSurveyQuestion'

# class InternalFacSurveyAnswer(models.Model):
#     ques_id = models.ForeignKey(InternalFacSurveyQuestion,related_name='InternalFacSurveyAnswer_quesid',null=True,on_delete=models.SET_NULL,db_column='ques_id')
#     added_by = models.ForeignKey(EmployeePrimdetail,related_name='InternalFacSurveyAnswer_addedby',null=True,on_delete=models.SET_NULL,db_column='added_by')
#     ans = JSONField();
#     time_stamp = models.DateTimeField(auto_now=True)
#     status = models.IntegerField(db_column='status',default=1)
#     class Meta:
#         managed = True
#         db_table = 'StuMMSInternalFacSurveyAnswer'        

###################################################################################################################################