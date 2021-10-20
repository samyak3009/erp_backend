from django.db import models
# Create your models here.
from StudentAcademics.models.models import *
from StudentAcademics.models.models_1819e import *
from Registrar.models import *
from login.models import EmployeePrimdetail


class ExamSchedule_1819e(models.Model):
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='ExamSchedule_1819e_id', null=True, on_delete=models.SET_NULL)
    sem = models.ForeignKey(StudentSemester, related_name='ExamSchedule_1819e_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    detained_attendance = models.FloatField(default=None, null=True)
    subject_type = models.ForeignKey(StudentDropdown, related_name='exam_Subject_type_1819e', db_column='Subject_type', null=True, on_delete=models.SET_NULL)
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_exam_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSExamSchedule_1819e'
        managed = True


class BTLevelSettings_1819e(models.Model):
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='bt_level_1819e', null=True, on_delete=models.SET_NULL)
    skill_set_level = models.ForeignKey(StudentAcademicsDropdown, related_name='skill_set_level_level_1819e', null=True, on_delete=models.SET_NULL)
    verb = models.CharField(max_length=1000, default='')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_bt_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)
    bt_num = models.IntegerField(default=1)

    class Meta:
        db_table = 'StuMMSBTLevelSettings_1819e'
        managed = True


class QuesPaperFormat_1819e(models.Model):
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_id_qp_1819e', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_qp_1819e', null=True, on_delete=models.SET_NULL)
    time = models.TimeField(default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSQuesPaperFormat_1819e'
        managed = True


class QuesPaperSectionDetails_1819e(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_1819e, related_name='ques_paper_id_1819e', null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=1000, default=None, null=True)
    attempt_type = models.CharField(max_length=5, default=None)  # 'M' for mandatory, 'I' for internal choice, 'O' for overall choice
    max_marks = models.FloatField()

    class Meta:
        db_table = 'StuMMSQuesPaperSectionDetails_1819e'
        managed = True


class QuesPaperApplicableOn_1819e(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_1819e, related_name='ques_paper_id_app_1819e', null=True, on_delete=models.SET_NULL)
    sem = models.ForeignKey(StudentSemester, related_name='ques_paper_id_sem_1819e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'StuMMSQuesPaperApplicableOn_1819e'
        managed = True


class QuesPaperBTAttainment_1819e(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_1819e, related_name='ques_paper_id_bt_att_1819e', null=True, on_delete=models.SET_NULL)
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='ques_paper_id_bt_level_1819e', null=True, on_delete=models.SET_NULL)
    minimum = models.FloatField()
    maximum = models.FloatField()

    class Meta:
        db_table = 'StuMMSQuesPaperBTAttainment_1819e'
        managed = True


class Dept_VisMis_1819e(models.Model):
    dept = models.ForeignKey(CourseDetail, related_name='Dept_VisMis_1819e', db_column='dept', blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=10, default='V')  # 'V' for Vision, 'M' for mission, 'QP' for quality policy,'PEO' for PEO's, 'PO' for PO's
    description = models.TextField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_vis_mis_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSDept_VisMis_1819e'
        managed = True


class SubjectCODetails_1819e(models.Model):
    co_num = models.IntegerField(default=1)
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="SubjectCODetails_1819e", null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_co_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCODetails_1819e'
        managed = True


class SubjectCODetailsAttainment_1819e(models.Model):
    co_id = models.ForeignKey(SubjectCODetails_1819e, related_name="SubjectCOAttain_1819e", on_delete=models.SET_NULL, null=True)
    attainment_per = models.FloatField(null=True, default=None)
    attainment_method = models.ForeignKey(StudentAcademicsDropdown, related_name='DirectAttainmentMethod_1819e', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCOAttainment_1819e'
        managed = True


class SubjectCOPOMapping_1819e(models.Model):
    co_id = models.ForeignKey(SubjectCODetails_1819e, related_name="SubjectCOMap_1819e", on_delete=models.SET_NULL, null=True)
    po_id = models.ForeignKey(Dept_VisMis_1819e, related_name="SubjectPOMap_1819e", on_delete=models.SET_NULL, null=True)
    max_marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_co_po_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCOPOMapping_1819e'
        managed = True


class SubjectPEOMIMapping_1819e(models.Model):
    m_id = models.ForeignKey(Dept_VisMis_1819e, related_name="SubjectPEOMIMap_1819e_mission", on_delete=models.SET_NULL, null=True)
    peo_id = models.ForeignKey(Dept_VisMis_1819e, related_name="SubjectPEOMIMap_1819e_peo", on_delete=models.SET_NULL, null=True)
    marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_peo_mi_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectPEOMIMapping_1819e'
        managed = True


class SubjectPOPEOMapping_1819e(models.Model):
    peo_id = models.ForeignKey(Dept_VisMis_1819e, related_name="SubjectPOPEOMap_1819e_peo", on_delete=models.SET_NULL, null=True)
    po_id = models.ForeignKey(Dept_VisMis_1819e, related_name="SubjectPOPEOMap_1819e_po", on_delete=models.SET_NULL, null=True)
    marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_po_peo_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectPOPEOMapping_1819e'
        managed = True


class SubjectAddQuestions_1819e(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="SubjectAddQuestions_1819e", on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, default='S')  # 'S' for Subjective, 'O' for Objective
    description = models.TextField()
    question_img = models.CharField(max_length=1000, default=None, null=True)
    max_marks = models.FloatField()
    co_id = models.ForeignKey(SubjectCODetails_1819e, related_name="SubjectQuesCO_1819e", on_delete=models.SET_NULL, null=True)
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='subject_ques_bt_1819e', null=True, on_delete=models.SET_NULL)
    answer_key = models.TextField(null=True)
    answer_img = models.CharField(max_length=1000, default=None, null=True)
    approval_status = models.CharField(max_length=20, default='PENDING')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_ques_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectAddQuestions_1819e'
        managed = True


class SubjectQuesOptions_1819e(models.Model):  # if question type is 'O' i.e. objective
    ques_id = models.ForeignKey(SubjectAddQuestions_1819e, related_name="SubjectAddQuestions_1819e", on_delete=models.SET_NULL, null=True)
    option_description = models.TextField()
    option_img = models.CharField(max_length=1000, default=None, null=True)
    is_answer = models.CharField(max_length=2, default='N')  # 'Y' if that option is answer

    class Meta:
        db_table = 'StuMMSSubjectQuesOptions_1819e'
        managed = True


class SubjectQuestionPaper_1819e(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="SubjectQuestionPaper_1819e_sub", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='SubjectQuestionPaper_1819e_exam', null=True, on_delete=models.SET_NULL)
    approval_status = models.CharField(max_length=20, default='PENDING')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_ques_paper_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectQuestionPaper_1819e'
        managed = True


class QuestionPaperQuestions_1819e(models.Model):
    ques_paper_id = models.ForeignKey(SubjectQuestionPaper_1819e, related_name="QuestionPaperQuestions_1819e_qpaper", on_delete=models.SET_NULL, null=True)
    section_id = models.ForeignKey(QuesPaperSectionDetails_1819e, related_name="QuestionPaperQuestions_1819e_section", on_delete=models.SET_NULL, null=True)
    ques_id = models.ForeignKey(SubjectAddQuestions_1819e, related_name="QuestionPaperQuestions_1819e_section", on_delete=models.SET_NULL, null=True)
    ques_num = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='SAVED')

    class Meta:
        db_table = 'StuMMSQuestionPaperQuestions_1819e'
        managed = True


class DeptExamSchedule_1819e(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='DeptExamSchedule_1819e_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="DeptExamSchedule_1819e_sub", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='DeptExamSchedule_1819e_exam', null=True, on_delete=models.SET_NULL)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exam_shift = models.ForeignKey(StudentAcademicsDropdown, related_name="DeptExamSchedule_1819e_shift", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='DeptExamSchedule_1819e_emp', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSDeptExamSchedule_1819e'
        managed = True


class Marks_1819e(models.Model):
    section = models.ForeignKey(Sections, related_name='Marks_section_1819e', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="MarkSub_id_1819e", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='MarksExamId_1819e', null=True, on_delete=models.SET_NULL)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="MarkEmp_1819e", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_1819e, related_name="MarkGid_1819e", null=True, on_delete=models.SET_NULL)
    normal_remedial = models.CharField(max_length=5, default='N')  # 'N' for normal, 'R' for remedial
    isgroup = models.CharField(max_length=5, default='N')
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSMarks_1819e'


class StudentMarks_1819e(models.Model):
    marks_id = models.ForeignKey(Marks_1819e, related_name='StuMarks_markid_1819e', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='StuMarks_uniqid_1819e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    present_status = models.CharField(max_length=2, default='P')
    ############# 'P' for present, 'A' for absent, 'D' for detained ###################################
    marks = models.FloatField(default=None, null=True)
    ############# if present_status='A' or 'D', then marks will be NULL ##############################
    ques_id = models.ForeignKey(QuestionPaperQuestions_1819e, related_name='StuMarksQuesId_1819e', db_column='ques_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSStudentMarks_1819e'


class StudentUniversityMarks_1819e(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="StuUniMarksSub_id_1819e", on_delete=models.SET_NULL, null=True)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="StuUniMarksAddedBy_1819e", null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='StuUniMarks_uniqid_1819e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    external_marks = models.CharField(max_length=10, default=None, null=True)
    internal_marks = models.CharField(max_length=10, default=None, null=True)
    back_marks = models.CharField(max_length=10, default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSStudentUnivMarks_1819e'


class AttMarksRule_1819e(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='attmarks_sem_1819e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    subject_type = models.ForeignKey(StudentDropdown, related_name='att_rule_subtype_1819e', db_column='Subject_type', on_delete=models.SET_NULL, null=True)
    from_att_per = models.FloatField()
    to_att_per = models.FloatField()
    marks = models.FloatField()
    max_att_marks = models.FloatField(default=None, null=True)
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSAttMarksRule_1819e'
        managed = True


class CTMarksRule_1819e(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='ctmarks_sem_1819e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    ct_group = models.CharField(max_length=500, default=None, null=True)  # comma separated ct ids
    subject_type = models.ForeignKey(StudentDropdown, related_name='ct_rule_subtype_1819e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    ct_to_select = models.IntegerField()
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSCTMarksRule_1819e'
        managed = True


class BonusMarksRule_1819e(models.Model):
    rule_name = models.CharField(max_length=100, default=None, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='bonusmarks_sem_1819e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    given_ct = models.CharField(max_length=500, default=None, null=True)  # comma separated ct ids
    min_marks_per = models.FloatField()
    min_att_per = models.FloatField(null=True, default=None)
    bonus_marks = models.FloatField(null=True, default=None)
    max_marks_limit_per = models.FloatField()
    subject_type = models.ForeignKey(StudentDropdown, related_name='bonusmarks_subtype_1819e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSBonusMarksRule_1819e'
        managed = True


class TAMarks_1819e(models.Model):
    section = models.ForeignKey(Sections, related_name='TAMarks_section_1819e', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="TAMarkSub_id_1819e", on_delete=models.SET_NULL, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="TAMarkEmp_1819e", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_1819e, related_name="TAMarkGid_1819e", null=True, on_delete=models.SET_NULL)
    isgroup = models.CharField(max_length=5, default='N')
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSTAMarks_1819e'


class StudentTAMarks_1819e(models.Model):
    ta_marks_id = models.ForeignKey(TAMarks_1819e, related_name='StuTAMarks_markid_1819e', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='StuTAMarks_uniqid_1819e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    ct_viva_marks = models.FloatField(default=None, null=True)
    ta_lab_marks = models.FloatField(default=None, null=True)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSTAStudentMarks_1819e'


class ExtraBonus_1819e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='ExtraBonus_Uniqid_1819e', null=True, on_delete=models.SET_NULL)
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="ExtraBonusSub_id_1819e", on_delete=models.SET_NULL, null=True)
    bonus_marks = models.FloatField()
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="ExtraBonusEmp_1819e", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSExtraBonus_1819e'


class COAttainment_1819e(models.Model):
    attainment_num = models.IntegerField()
    subject_type = models.ForeignKey(StudentDropdown, related_name='COAttainmentSubjectType_1819e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='COAttainmentsem_1819e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    min_att_per = models.FloatField(null=True, default=None)
    max_att_per = models.FloatField(null=True, default=None)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="COAttainmentLevel_1819e", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSCOAttainmentLevel_1819e'


class MarksAttainmentSettings_1819e(models.Model):
    subject_type = models.ForeignKey(StudentDropdown, related_name='MarksAttainmentSubjectType_1819e', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='MarksAttainmentsem_1819e', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    from_direct_per = models.FloatField(null=True, default=None)  # from percentage for direct attainment settings and direct per for attainment proportion
    to_indirect_per = models.FloatField(null=True, default=None)  # to percentage for direct attainment settings and indirect per for attainment proportion
    external_marks = models.FloatField(null=True, default=None)
    internal_marks = models.FloatField(null=True, default=None)
    attainment_level = models.FloatField(null=True, default=None)
    attainment_type = models.CharField(null=True, default=None, max_length=5)  # D for direct attainment , A for attainment proportion
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="MarksAttainment_1819e", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSMarksAttainmentSettings_1819e'


class AssignmentQuizMarks_1819e(models.Model):
    section = models.ForeignKey(Sections, related_name='AssignmentMarks_section_1819e', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="AssignmentMarkSub_id_1819e", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='AssignmentMarksExamId_1819e', null=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="AssignmentMarkEmp_1819e", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_1819e, related_name="AssignmentMarkGid_1819e", null=True, on_delete=models.SET_NULL)
    isgroup = models.CharField(max_length=5, default='N')
    isco_wise = models.CharField(max_length=5, default='N')
    max_marks = models.FloatField(null=True, default=None)  # if marks entered is co_wise then it will be NULL ############
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSAssignmentMarks_1819e'


class AssignmentStudentMarks_1819e(models.Model):
    marks_id = models.ForeignKey(AssignmentQuizMarks_1819e, related_name='StuAssignmentMarks_markid_1819e', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='StuAssignmentMarks_uniqid_1819e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    present_status = models.CharField(max_length=2, default='P')
    ############# 'P' for present, 'A' for absent ###################################
    marks = models.FloatField(default=None, null=True)
    ############# if present_status='A', then marks will be NULL ##############################
    ques_id = models.ForeignKey(QuestionPaperQuestions_1819e, related_name='StuAssignmentMarksQuesId_1819e', db_column='ques_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSAssignmentStudentMarks_1819e'


class SurveyAddQuestions_1819e(models.Model):
    survey_id = models.ForeignKey(StudentAcademicsDropdown, related_name='SurveyAddQuestions_1819e_id', null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    sem_id = models.ForeignKey(StudentSemester, related_name='SurveyAddQuestions_1819e_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)
    question_img = models.CharField(max_length=1000, default=None, null=True)
    po_id = models.ForeignKey(Dept_VisMis_1819e, related_name="SurveyAddQuestions_1819e_po", on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_survey_ques_1819e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSurveyAddQuestions_1819e'
        managed = True


class SurveyFillFeedback_1819e(models.Model):
    ques_id = models.ForeignKey(SurveyAddQuestions_1819e, related_name='SurveyFillFeedback_1819e_survey_id', null=True, on_delete=models.SET_NULL)
    feedback = models.IntegerField(default=1)  # 1 for not satisfied , 2 for satisfied , 3 for very satisfied####
    status = models.CharField(max_length=20, default='INSERT')
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='SurveyFillFeedback_uniqid_1819e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSurveyFillFeedback_1819e'
        managed = True


class StudentFinalMarksStatus_1819e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='StuFinalMarks_uniqid_1819e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    Total_marks_obtained = models.CharField(max_length=30, default=None, null=True)
    Total_max_marks = models.CharField(max_length=30, default=None, null=True)
    Division_awarded = models.CharField(max_length=40, default=None, null=True)
    Result_status = models.CharField(max_length=40, default=None, null=True)
    Year_obtained = models.CharField(max_length=40, default=None, null=True)
    Year_total = models.CharField(max_length=40, default=None, null=True)

    class Meta:
        managed = True
        db_table = 'StuMMSFinalMarksStatus_1819e'
