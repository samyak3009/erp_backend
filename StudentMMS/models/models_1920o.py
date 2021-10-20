from django.db import models
# Create your models here.
from StudentAcademics.models.models import *
from StudentAcademics.models.models_1920o import *
from Registrar.models import *
from login.models import EmployeePrimdetail


class ExamSchedule_1920o(models.Model):
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='ExamSchedule_1920o_id', null=True, on_delete=models.SET_NULL)
    sem = models.ForeignKey(StudentSemester, related_name='ExamSchedule_1920o_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)  # Field name made lowercase.
    detained_attendance = models.FloatField(default=None, null=True)
    subject_type = models.ForeignKey(StudentDropdown, related_name='exam_Subject_type_1920o', db_column='Subject_type', null=True, on_delete=models.SET_NULL)
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_exam_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSExamSchedule_1920o'
        managed = True


class BTLevelSettings_1920o(models.Model):
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='bt_level_1920o', null=True, on_delete=models.SET_NULL)
    skill_set_level = models.ForeignKey(StudentAcademicsDropdown, related_name='skill_set_level_level_1920o', null=True, on_delete=models.SET_NULL)
    verb = models.CharField(max_length=1000, default='')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_bt_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)
    bt_num = models.IntegerField(default=1)

    class Meta:
        db_table = 'StuMMSBTLevelSettings_1920o'
        managed = True


class QuesPaperFormat_1920o(models.Model):
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_id_qp_1920o', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_qp_1920o', null=True, on_delete=models.SET_NULL)
    time = models.TimeField(default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSQuesPaperFormat_1920o'
        managed = True


class QuesPaperSectionDetails_1920o(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_1920o, related_name='ques_paper_id_1920o', null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=1000, default=None, null=True)
    attempt_type = models.CharField(max_length=5, default=None)  # 'M' for mandatory, 'I' for internal choice, 'O' for overall choice
    max_marks = models.FloatField()
    min_marks_per = models.FloatField()

    class Meta:
        db_table = 'StuMMSQuesPaperSectionDetails_1920o'
        managed = True


class QuesPaperApplicableOn_1920o(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_1920o, related_name='ques_paper_id_app_1920o', null=True, on_delete=models.SET_NULL)
    sem = models.ForeignKey(StudentSemester, related_name='ques_paper_id_sem_1920o', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'StuMMSQuesPaperApplicableOn_1920o'
        managed = True


class QuesPaperBTAttainment_1920o(models.Model):
    ques_paper_id = models.ForeignKey(QuesPaperFormat_1920o, related_name='ques_paper_id_bt_att_1920o', null=True, on_delete=models.SET_NULL)
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='ques_paper_id_bt_level_1920o', null=True, on_delete=models.SET_NULL)
    minimum = models.FloatField()
    maximum = models.FloatField()

    class Meta:
        db_table = 'StuMMSQuesPaperBTAttainment_1920o'
        managed = True


class Dept_VisMis_1920o(models.Model):
    dept = models.ForeignKey(CourseDetail, related_name='Dept_VisMis_1920o', db_column='dept', blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=10, default='V')  # 'V' for Vision, 'M' for mission, 'QP' for quality policy,'PEO' for PEO's, 'PO' for PO's
    description = models.TextField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_vis_mis_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSDept_VisMis_1920o'
        managed = True


class SubjectCODetails_1920o(models.Model):
    co_num = models.IntegerField(default=1)
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="SubjectCODetails_1920o", null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_co_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCODetails_1920o'
        managed = True


class SubjectCODetailsAttainment_1920o(models.Model):
    co_id = models.ForeignKey(SubjectCODetails_1920o, related_name="SubjectCOAttain_1920o", on_delete=models.SET_NULL, null=True)
    attainment_per = models.FloatField(null=True, default=None)
    attainment_method = models.ForeignKey(StudentAcademicsDropdown, related_name='DirectAttainmentMethod_1920o', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCOAttainment_1920o'
        managed = True


class SubjectCOPOMapping_1920o(models.Model):
    co_id = models.ForeignKey(SubjectCODetails_1920o, related_name="SubjectCOMap_1920o", on_delete=models.SET_NULL, null=True)
    po_id = models.ForeignKey(Dept_VisMis_1920o, related_name="SubjectPOMap_1920o", on_delete=models.SET_NULL, null=True)
    max_marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_co_po_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectCOPOMapping_1920o'
        managed = True


class SubjectPEOMIMapping_1920o(models.Model):
    m_id = models.ForeignKey(Dept_VisMis_1920o, related_name="SubjectPEOMIMap_1920o_mission", on_delete=models.SET_NULL, null=True)
    peo_id = models.ForeignKey(Dept_VisMis_1920o, related_name="SubjectPEOMIMap_1920o_peo", on_delete=models.SET_NULL, null=True)
    marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_peo_mi_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectPEOMIMapping_1920o'
        managed = True


class SubjectPOPEOMapping_1920o(models.Model):
    peo_id = models.ForeignKey(Dept_VisMis_1920o, related_name="SubjectPOPEOMap_1920o_peo", on_delete=models.SET_NULL, null=True)
    po_id = models.ForeignKey(Dept_VisMis_1920o, related_name="SubjectPOPEOMap_1920o_po", on_delete=models.SET_NULL, null=True)
    marks = models.FloatField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_po_peo_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectPOPEOMapping_1920o'
        managed = True


class SubjectAddQuestions_1920o(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="SubjectAddQuestions_1920o", on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, default='S')  # 'S' for Subjective, 'O' for Objective
    description = models.TextField()
    question_img = models.CharField(max_length=1000, default=None, null=True)
    max_marks = models.FloatField()
    co_id = models.ForeignKey(SubjectCODetails_1920o, related_name="SubjectQuesCO_1920o", on_delete=models.SET_NULL, null=True)
    bt_level = models.ForeignKey(StudentAcademicsDropdown, related_name='subject_ques_bt_1920o', null=True, on_delete=models.SET_NULL)
    answer_key = models.TextField(null=True)
    answer_img = models.CharField(max_length=1000, default=None, null=True)
    approval_status = models.CharField(max_length=20, default='PENDING')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_ques_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectAddQuestions_1920o'
        managed = True


class SubjectQuesOptions_1920o(models.Model):  # if question type is 'O' i.e. objective
    ques_id = models.ForeignKey(SubjectAddQuestions_1920o, related_name="SubjectAddQuestions_1920o", on_delete=models.SET_NULL, null=True)
    option_description = models.TextField()
    option_img = models.CharField(max_length=1000, default=None, null=True)
    is_answer = models.CharField(max_length=2, default='N')  # 'Y' if that option is answer

    class Meta:
        db_table = 'StuMMSSubjectQuesOptions_1920o'
        managed = True


class SubjectQuestionPaper_1920o(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="SubjectQuestionPaper_1920o_sub", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='SubjectQuestionPaper_1920o_exam', null=True, on_delete=models.SET_NULL)
    approval_status = models.CharField(max_length=20, default='PENDING')
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_sub_ques_paper_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSubjectQuestionPaper_1920o'
        managed = True


class QuestionPaperQuestions_1920o(models.Model):
    ques_paper_id = models.ForeignKey(SubjectQuestionPaper_1920o, related_name="QuestionPaperQuestions_1920o_qpaper", on_delete=models.SET_NULL, null=True)
    section_id = models.ForeignKey(QuesPaperSectionDetails_1920o, related_name="QuestionPaperQuestions_1920o_section", on_delete=models.SET_NULL, null=True)
    ques_id = models.ForeignKey(SubjectAddQuestions_1920o, related_name="QuestionPaperQuestions_1920o_section", on_delete=models.SET_NULL, null=True)
    ques_num = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='SAVED')

    class Meta:
        db_table = 'StuMMSQuestionPaperQuestions_1920o'
        managed = True


class DeptExamSchedule_1920o(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='DeptExamSchedule_1920o_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="DeptExamSchedule_1920o_sub", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='DeptExamSchedule_1920o_exam', null=True, on_delete=models.SET_NULL)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exam_shift = models.ForeignKey(StudentAcademicsDropdown, related_name="DeptExamSchedule_1920o_shift", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='DeptExamSchedule_1920o_emp', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSDeptExamSchedule_1920o'
        managed = True


class Marks_1920o(models.Model):
    section = models.ForeignKey(Sections, related_name='Marks_section_1920o', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="MarkSub_id_1920o", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='MarksExamId_1920o', null=True, on_delete=models.SET_NULL)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="MarkEmp_1920o", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_1920o, related_name="MarkGid_1920o", null=True, on_delete=models.SET_NULL)
    normal_remedial = models.CharField(max_length=5, default='N')  # 'N' for normal, 'R' for remedial
    isgroup = models.CharField(max_length=5, default='N')
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSMarks_1920o'


class StudentMarks_1920o(models.Model):
    marks_id = models.ForeignKey(Marks_1920o, related_name='StuMarks_markid_1920o', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='StuMarks_uniqid_1920o', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    present_status = models.CharField(max_length=2, default='P')
    ############# 'P' for present, 'A' for absent, 'D' for detained ###################################
    marks = models.FloatField(default=None, null=True)
    ############# if present_status='A' or 'D', then marks will be NULL ##############################
    ques_id = models.ForeignKey(QuestionPaperQuestions_1920o, related_name='StuMarksQuesId_1920o', db_column='ques_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSStudentMarks_1920o'


class StudentUniversityMarks_1920o(models.Model):
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="StuUniMarksSub_id_1920o", on_delete=models.SET_NULL, null=True)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="StuUniMarksAddedBy_1920o", null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='StuUniMarks_uniqid_1920o', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    external_marks = models.CharField(max_length=10, default=None, null=True)
    internal_marks = models.CharField(max_length=10, default=None, null=True)
    back_marks = models.CharField(max_length=10, default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSStudentUnivMarks_1920o'


class AttMarksRule_1920o(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='attmarks_sem_1920o', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    subject_type = models.ForeignKey(StudentDropdown, related_name='att_rule_subtype_1920o', db_column='Subject_type', on_delete=models.SET_NULL, null=True)
    from_att_per = models.FloatField()
    to_att_per = models.FloatField()
    marks = models.FloatField()
    max_att_marks = models.FloatField(default=None, null=True)
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSAttMarksRule_1920o'
        managed = True


class CTMarksRule_1920o(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='ctmarks_sem_1920o', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    ct_group = models.CharField(max_length=500, default=None, null=True)  # comma separated ct ids
    subject_type = models.ForeignKey(StudentDropdown, related_name='ct_rule_subtype_1920o', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    ct_to_select = models.IntegerField()
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSCTMarksRule_1920o'
        managed = True


class BonusMarksRule_1920o(models.Model):
    rule_name = models.CharField(max_length=100, default=None, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='bonusmarks_sem_1920o', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    given_ct = models.CharField(max_length=500, default=None, null=True)  # comma separated ct ids
    min_marks_per = models.FloatField()
    min_att_per = models.FloatField(null=True, default=None)
    bonus_marks = models.FloatField(null=True, default=None)
    max_marks_limit_per = models.FloatField()
    subject_type = models.ForeignKey(StudentDropdown, related_name='bonusmarks_subtype_1920o', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSBonusMarksRule_1920o'
        managed = True


class TAMarks_1920o(models.Model):
    section = models.ForeignKey(Sections, related_name='TAMarks_section_1920o', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="TAMarkSub_id_1920o", on_delete=models.SET_NULL, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="TAMarkEmp_1920o", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_1920o, related_name="TAMarkGid_1920o", null=True, on_delete=models.SET_NULL)
    isgroup = models.CharField(max_length=5, default='N')
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSTAMarks_1920o'


class StudentTAMarks_1920o(models.Model):
    ta_marks_id = models.ForeignKey(TAMarks_1920o, related_name='StuTAMarks_markid_1920o', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='StuTAMarks_uniqid_1920o', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    ct_viva_marks = models.FloatField(default=None, null=True)
    ta_lab_marks = models.FloatField(default=None, null=True)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSTAStudentMarks_1920o'


class ExtraBonus_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='ExtraBonus_Uniqid_1920o', null=True, on_delete=models.SET_NULL)
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="ExtraBonusSub_id_1920o", on_delete=models.SET_NULL, null=True)
    bonus_marks = models.FloatField()
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="ExtraBonusEmp_1920o", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSExtraBonus_1920o'


class COAttainment_1920o(models.Model):
    attainment_num = models.IntegerField()
    subject_type = models.ForeignKey(StudentDropdown, related_name='COAttainmentSubjectType_1920o', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='COAttainmentsem_1920o', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    min_att_per = models.FloatField(null=True, default=None)
    max_att_per = models.FloatField(null=True, default=None)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="COAttainmentLevel_1920o", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSCOAttainmentLevel_1920o'


class MarksAttainmentSettings_1920o(models.Model):
    subject_type = models.ForeignKey(StudentDropdown, related_name='MarksAttainmentSubjectType_1920o', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    sem = models.ForeignKey(StudentSemester, related_name='MarksAttainmentsem_1920o', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    from_direct_per = models.FloatField(null=True, default=None)  # from percentage for direct attainment settings and direct per for attainment proportion
    to_indirect_per = models.FloatField(null=True, default=None)  # to percentage for direct attainment settings and indirect per for attainment proportion
    external_marks = models.FloatField(null=True, default=None)
    internal_marks = models.FloatField(null=True, default=None)
    attainment_level = models.FloatField(null=True, default=None)
    attainment_type = models.CharField(null=True, default=None, max_length=5)  # D for direct attainment , A for attainment proportion
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="MarksAttainment_1920o", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSMarksAttainmentSettings_1920o'


class AssignmentQuizMarks_1920o(models.Model):
    section = models.ForeignKey(Sections, related_name='AssignmentMarks_section_1920o', db_column='section_id', on_delete=models.SET_NULL, null=True)  # Field
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="AssignmentMarkSub_id_1920o", on_delete=models.SET_NULL, null=True)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='AssignmentMarksExamId_1920o', null=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="AssignmentMarkEmp_1920o", null=True, on_delete=models.SET_NULL)
    group_id = models.ForeignKey(SectionGroupDetails_1920o, related_name="AssignmentMarkGid_1920o", null=True, on_delete=models.SET_NULL)
    isgroup = models.CharField(max_length=5, default='N')
    isco_wise = models.CharField(max_length=5, default='N')
    max_marks = models.FloatField(null=True, default=None)  # if marks entered is co_wise then it will be NULL ############
    ########### 'Y' if marks entered is group wise, 'N' if non-group wise ##################
    status = models.CharField(max_length=20, default="INSERT")
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSAssignmentMarks_1920o'


class AssignmentStudentMarks_1920o(models.Model):
    marks_id = models.ForeignKey(AssignmentQuizMarks_1920o, related_name='StuAssignmentMarks_markid_1920o', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='StuAssignmentMarks_uniqid_1920o', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    present_status = models.CharField(max_length=2, default='P')
    ############# 'P' for present, 'A' for absent ###################################
    marks = models.FloatField(default=None, null=True)
    ############# if present_status='A', then marks will be NULL ##############################
    ques_id = models.ForeignKey(QuestionPaperQuestions_1920o, related_name='StuAssignmentMarksQuesId_1920o', db_column='ques_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="INSERT")  # 'INSERT', 'UPDATE' OR 'DELETE' #####################
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSAssignmentStudentMarks_1920o'


class SurveyAddQuestions_1920o(models.Model):
    survey_id = models.ForeignKey(StudentAcademicsDropdown, related_name='SurveyAddQuestions_1920o_id', null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    sem_id = models.ForeignKey(StudentSemester, related_name='SurveyAddQuestions_1920o_sem', db_column='sem_id', on_delete=models.SET_NULL, null=True)
    question_img = models.CharField(max_length=1000, default=None, null=True)
    po_id = models.ForeignKey(Dept_VisMis_1920o, related_name="SurveyAddQuestions_1920o_po", on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_survey_ques_1920o', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSurveyAddQuestions_1920o'
        managed = True


class SurveyFillFeedback_1920o(models.Model):
    ques_id = models.ForeignKey(SurveyAddQuestions_1920o, related_name='SurveyFillFeedback_1920o_survey_id', null=True, on_delete=models.SET_NULL)
    feedback = models.IntegerField(default=1)  # 1 for not satisfied , 2 for satisfied , 3 for very satisfied####
    status = models.CharField(max_length=20, default='INSERT')
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='SurveyFillFeedback_uniqid_1920o', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StuMMSSurveyFillFeedback_1920o'
        managed = True


class StudentFinalMarksStatus_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='StuFinalMarks_uniqid_1920o', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    Total_marks_obtained = models.CharField(max_length=30, default=None, null=True)
    Total_max_marks = models.CharField(max_length=30, default=None, null=True)
    Division_awarded = models.CharField(max_length=40, default=None, null=True)
    Result_status = models.CharField(max_length=40, default=None, null=True)
    Year_obtained = models.CharField(max_length=40, default=None, null=True)
    Year_total = models.CharField(max_length=40, default=None, null=True)

    class Meta:
        managed = True
        db_table = 'StuMMSFinalMarksStatus_1920o'


### CT-MARKS RULE ###


class CTMarksRules_1920o(models.Model):
    sem = models.ForeignKey(StudentSemester, related_name='ctmarks_rule_sem_1920o', db_column='sem_id', blank=True, null=True, on_delete=models.SET_NULL)
    subject_type = models.ForeignKey(StudentDropdown, related_name='ctmarks_rule_subtype_1920o', db_column='Subject_Type', on_delete=models.SET_NULL, null=True)
    rule_no = models.IntegerField()
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_ctrule_1920o', null=True, on_delete=models.SET_NULL)
    rule_criteria = models.CharField(max_length=30, db_column='Rule_Criteria', null=True, blank=True, default="MAXIMUM")
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'CTMarksRules_1920o'


class CTMarks_GroupInfo_1920o(models.Model):
    rule_id = models.ForeignKey(CTMarksRules_1920o, related_name="ctmarks_rule_group_1920o", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    group = models.CharField(max_length=50, default=None)
    weightage = models.IntegerField()
    ct_to_select = models.IntegerField()
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'CTMarks_GroupInfo_1920o'


class CTMarks_Group_ExamInfo_1920o(models.Model):
    group_id = models.ForeignKey(CTMarks_GroupInfo_1920o, related_name="group_ctmarks_rule_1920o", db_column="group_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='ctmarks_rule_1920o', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'CTMarks_Group_ExamInfo_1920o'

###########################
#### BONUS MARKS RULE #####


class BonusMarks_Subrule_1920o(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    type_id = models.IntegerField(blank=True, null=True)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_bonusmarks_subrule_1920o', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'BonusMarks_Subrule_1920o'


class BonusMarks_External_1920o(models.Model):
    applicable_type = models.CharField(max_length=50, blank=True, null=True)  # OVERALL,PREVIOUS SEM,PREVIOS YEAR
    criteria = models.CharField(max_length=50, blank=True, null=True)  # PRECENTAGE, NUMBER OF STUDENTS
    range_type = models.CharField(max_length=50, blank=True, null=True)  # HIGHER,LOWER
    value = models.FloatField()
    # subrule_id = models.ForeignKey(BonusMarks_Subrule_1920o, related_name="subrule_bonusmarks_ext_1920o", db_column="subrule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'BonusMarks_External_1920o'


class BonusMarks_Internal_1920o(models.Model):
    min_range = models.IntegerField()
    max_range = models.IntegerField()
    # subrule_id = models.ForeignKey(BonusMarks_Subrule_1920o, related_name="subrule_bonusmarks_int_1920o", db_column="subrule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'BonusMarks_Internal_1920o'


class BonusMarks_InternalExam_1920o(models.Model):
    internal_id = models.ForeignKey(BonusMarks_Internal_1920o, related_name="int_bonusmarks_int_1920o", db_column="internal_id", blank=True, null=True, on_delete=models.SET_NULL)
    exam_id = models.ForeignKey(StudentAcademicsDropdown, related_name='exam_bonusmarks_int_1920o', null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'BonusMarks_InternalExam_1920o'


class BonusMarks_Attendance_1920o(models.Model):
    min_range = models.IntegerField()
    max_range = models.IntegerField()
    # subrule_id = models.ForeignKey(BonusMarks_Subrule_1920o, related_name="subrule_bonusmarks_att_1920o", db_column="subrule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'BonusMarks_Attendance_1920o'


class BonusMarks_AttendanceAtt_type_1920o(models.Model):
    att_id = models.ForeignKey(BonusMarks_Attendance_1920o, related_name="att_bonusmarks_att_1920o", db_column="att_id", blank=True, null=True, on_delete=models.SET_NULL)
    att_type = models.ForeignKey(StudentAcademicsDropdown, related_name='att_type_bonusmarks_att_1920o', null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'BonusMarks_AttendanceAtt_type_1920o'


class BonusMarks_Applicable_On_1920o(models.Model):
    sem_id = models.ForeignKey(StudentSemester, related_name="sem_bonusmarks_app_1920o", db_column="sem_id", blank=True, null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey(Sections, related_name="section_bonusmarks_app_1920o", db_column="section", blank=True, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(SubjectInfo_1920o, related_name="subject_bonusmarks_app_1920o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'BonusMarks_Applicable_On_1920o'


class BonusMarks_Rule_1920o(models.Model):
    rule_no = models.IntegerField()
    app_id = models.ForeignKey(BonusMarks_Applicable_On_1920o, related_name="rule_bonusmarks_rule_1920o", db_column="app_id", blank=True, null=True, on_delete=models.SET_NULL)
    subrule_no = models.IntegerField()
    subrule_id = models.ForeignKey(BonusMarks_Subrule_1920o, related_name="subrule_bonusmarks_rule_1920o", db_column="subrule_id", blank=True, null=True, on_delete=models.SET_NULL)
    bonus_marks = models.FloatField()
    max_marks_limit = models.FloatField()  # bonus marks
    min_range = models.IntegerField()  # bonus marks
    max_range = models.IntegerField()  # bonus marks
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_bonusmarks_rule_1920o', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'BonusMarks_Rule_1920o'


class BonusMarks_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="uniq_id_bonus_marks_1920o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    # subject = models.ForeignKey(SubjectInfo_1920o, related_name="subject_bonus_marks_1920o", db_column="subject", blank=True, null=True, on_delete=models.SET_NULL)
    rule_id = models.ForeignKey(BonusMarks_Rule_1920o, related_name="rule_bonus_marks_1920o", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    total_bonus_marks = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuMMSBonusMarks_1920o'


class BonusMarks_Students_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="uniq_id_bonusmarks_students_1920o", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    # app_id = models.ForeignKey(BonusMarks_Applicable_On_1920o, related_name="rule_bonusmarks_students_1920o", db_column="app_id", blank=True, null=True, on_delete=models.SET_NULL)
    rule_id = models.ForeignKey(BonusMarks_Rule_1920o, related_name="rule_bonusmarks_students_1920o", db_column="rule_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'BonusMarks_Students_1920o'

###########################
