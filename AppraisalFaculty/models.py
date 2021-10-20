from django.db import models
from login.models import EmployeeDropdown, EmployeePrimdetail, AarDropdown
from Accounts.models import AccountsDropdown, AccountsSession
from AppraisalStaff.models import AppraisalStaffLockingUnlocking
from aar.models import Researchjournal, Researchconference, Books, ProjectConsultancy, Patent, Researchguidence, TrainingDevelopment, LecturesTalks
from django_mysql.models import JSONField

class FacAppLockingUnlockingStatus(models.Model):
    locking_details = models.ForeignKey(AppraisalStaffLockingUnlocking, db_column='locking_details', related_name='AppraisalFacultyLockingUnlockingStatus_AppraisalStaffLockingUnlocking_locking_details', on_delete=models.SET_NULL, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id',
                               related_name='AppraisalFacultyLockingUnlockingStatus_EmployeePrimdetail_emp_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default='INSERT')
    # MIND 'SESSION(FROM PARENT TABLE)' CHECK DURING FETCHING

    class Meta:
        db_table = 'FacAppLockingUnlockingStatus'
        managed = True


class FacultyAppraisal(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', on_delete=models.SET_NULL, null=True, related_name="part1_emp")
    dept = models.ForeignKey(EmployeeDropdown, db_column="dept", on_delete=models.SET_NULL, null=True, related_name="part1_dept")
    desg = models.ForeignKey(EmployeeDropdown, db_column="desg", on_delete=models.SET_NULL, null=True, related_name="part1_desg")
    highest_qualification = models.CharField(null=True, max_length=200)
    salary_type = models.ForeignKey(AccountsDropdown, null=True, on_delete=models.SET_NULL, related_name="part1_sal_type")
    current_gross_salary = models.FloatField(null=True)
    agp = models.FloatField(null=True)
    total_experience = models.CharField(max_length=100, null=True, default=0)
    form_filled_status = models.CharField(max_length=10, default='N')
    form_approved = models.CharField(max_length=10, default='PENDING')
    # PENDING,APPROVED ###
    status = models.CharField(max_length=10, default='PENDING')
    # PENDING,SAVED,SUBMIT #
    achievement_recognition = models.TextField(null=True)
    training_needs = models.TextField(null=True)
    suggestions = models.TextField(null=True)
    level = models.IntegerField(db_column='level', default=0, null=True)
    emp_date = models.DateField(default=None, null=True)
    hod_date = models.DateField(default=None, null=True)
    dean_date = models.DateField(default=None, null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    session = models.ForeignKey(AccountsSession, related_name='FacultyAppraisal_AccountsSession_session', db_column='session', null=True, on_delete=models.SET_NULL, default=1)

    class Meta:
        db_table = 'FacAppPart1'
        managed = True



class FacAppRecommendationApproval(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', related_name='FacAppRecommendationApproval_EmployeePrimdetail_emp_id', on_delete=models.SET_NULL, null=True)
    increment_type = models.CharField(db_column='increment_type', max_length=50, blank=True)
    # NO INCREMENT, NORMAL, SPECIAL, PROMOTION WITH SPECIAL INCREAMENT,
    # PROMOTION WITHOUT INCREAMENT
    increment_amount = models.FloatField(
        db_column='increment_amount', null=True)
    promoted_to = models.ForeignKey(EmployeeDropdown, db_column='promoted_to', max_length=200, related_name='FacAppRecommendationApproval_EmployeeDropdown_promoted_to', on_delete=models.SET_NULL, null=True)
    level = models.IntegerField(db_column='level', null=True)
    remark = models.TextField(db_column='remark', null=True)
    approval_status = models.CharField(
        db_column='approval_status', default='INSERT', max_length=20)
    # APPROVED, REJECTED, REVIEW, PENDING
    added_by = models.ForeignKey(EmployeePrimdetail, db_column='added_by', related_name='FacAppRecommendationApproval_EmployeePrimdetail_added_by', null=True, on_delete=models.SET_NULL)
    session = models.ForeignKey(AccountsSession, related_name='FacAppRecommendationApproval_AccountsSession_session', db_column='session', null=True, on_delete=models.SET_NULL, default=1)
    status = models.CharField(db_column='status', default='INSERT', max_length=20)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = 'FacAppRecommendationApproval'
        managed = True
# Create your models here.

################################################################MODELS BY YASH ####################################################
class FacAppCatWiseData(models.Model):
    fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="appraisal_id")
    category = models.CharField(max_length=100)
    #CATEGORY-I,CATEGORY-II....
    sub_category = models.CharField(max_length=100)
    #A1,A2,A3.....
    data_sub_category = JSONField(db_column='data_sub_category')
    #[{'Course/Paper & Year':"","Total lectures as per academic calendar":50,}...{}]
    status = models.IntegerField(db_column='status', default=1)
    # 0 = DELETE, 1 = INSERT,
    is_editable = models.IntegerField(default=1)
    #0:EDITABLE,1:NOT EDITABLE
    score_claimed = models.FloatField(default=0,null=True)
    score_awarded = models.FloatField(default=0)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = 'FacAppCatWiseData'
        managed = True 

class FacAppAcadData(models.Model):
    fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="acad_data")
    external_data = JSONField(db_column='external_data')
    #{'marks':"","other":""}OTHER LAST 5 YRS DATA
    score_claimed = models.FloatField(default=0,null=True)
    score_awarded = models.FloatField(default=0)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    status = models.IntegerField(db_column='status', default=1)

    class Meta:
        db_table = 'FacAppAcadData'
        managed = True
###################################################################################################################################













# class FacAppCat1A1(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat1_a1")
#     course_paper = models.TextField(null=True)
#     lectues_calendar = models.IntegerField(null=True)
#     lectues_portal = models.IntegerField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0)  # BOTH FOR APPROVED AND REVIEWED #############
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     # PENDING ,APPROVED ,REVIEW ,REVIEWED #
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat1A1'
#         managed = True


# class FacAppCat1A2(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat1_a2")
#     course_paper = models.TextField(null=True)
#     consulted = models.TextField(null=True)
#     prescribed = models.TextField(null=True)
#     additional_resource = models.TextField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0)
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat1A2'
#         managed = True


# class FacAppCat1A3(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat1_a3")
#     description = models.TextField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0)
#     short_descriptn = models.TextField(null=True)
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat1A3'
#         managed = True


# class FacAppCat1A4(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat1_a4")
#     sno = models.IntegerField(null=True)
#     ### 0 for invigilation,1 for question paper setting,3 for evaluation of answer ###
#     executed = models.FloatField(null=True)
#     extent_to_carried = models.FloatField(null=True)
#     duties_assign = models.IntegerField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0, null=True)
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat1A4'
#         managed = True


# class FacAppCat2A1(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat2_a1")
#     type_of_activity = models.TextField(default=None, null=True)
#     average_hours = models.FloatField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0, null=True)
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat2A1'
#         managed = True


# class FacAppCat3(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat3")
#     type = models.CharField(default='J', max_length=5)
#     ######### 'J' for research journal, 'C' for research conference, 'B' for books, 'PC' for project consultancy, 'PA' for patent, 'G' for research guidance, 'T' for training development, 'L' for lecture talks #########################################
#     research_journal = models.ForeignKey(Researchjournal, db_column="research_journal", on_delete=models.SET_NULL, null=True, related_name="app_res")
#     research_conference = models.ForeignKey(Researchconference, db_column="research_conference", on_delete=models.SET_NULL, null=True, related_name="app_conf")
#     books = models.ForeignKey(Books, db_column="books", on_delete=models.SET_NULL, null=True, related_name="app_book")
#     project_consultancy = models.ForeignKey(ProjectConsultancy, db_column="project_consultancy", on_delete=models.SET_NULL, null=True, related_name="app_project")
#     patent = models.ForeignKey(Patent, db_column="patent", on_delete=models.SET_NULL, null=True, related_name="app_patent")
#     research_guidance = models.ForeignKey(Researchguidence, db_column="research_guidance", on_delete=models.SET_NULL, null=True, related_name="app_res_guid")
#     training_development = models.ForeignKey(TrainingDevelopment, db_column="training_development", on_delete=models.SET_NULL, null=True, related_name="app_training")
#     lectures_talks = models.ForeignKey(LecturesTalks, db_column="lectures_talks", on_delete=models.SET_NULL, null=True, related_name="app_lecture")
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0, null=True)  # Same value for all the same type of journals
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat3'
#         managed = True

# class FacAppCat3Achievement(models.Model):
#     ### ENTERY ONLY ONCE BECAUSE NOT EDITABLE ###
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat3Achievement")
#     type = models.CharField(default='J', max_length=50)
#     achievement_id = models.IntegerField(db_column='achievement_id')
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0, null=True)  # Same value for all the same type of journals
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat3Achievement'
#         managed = True


# class FacAppCat4A1(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat4_a1")
#     branch_details = models.TextField(null=True)
#     subject = models.CharField(max_length=200, null=True)
#     result_clear_pass = models.FloatField(null=True)
#     result_external = models.FloatField(null=True)
#     stu_below_40 = models.IntegerField(null=True)
#     stu_40_49 = models.IntegerField(null=True)
#     stu_50_59 = models.IntegerField(null=True)
#     stu_above_60 = models.IntegerField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0)
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat4A1'
#         managed = True


# class FacAppCat4A2(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL, null=True, related_name="cat4_a2")
#     branch = models.TextField(max_length=100, null=True)
#     semester = models.CharField(max_length=25, null=True)
#     section = models.CharField(max_length=10, null=True)
#     subject = models.CharField(max_length=200, null=True)
#     overall_avg = models.FloatField(null=True)
#     student_feedback = models.FloatField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0, null=True)
#     status = models.CharField(max_length=10, default="INSERT", null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = 'FacAppCat4A2'
#         managed = True

# class FacAppRecommend(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal,db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="dir_fac")
#     increment_type=models.ForeignKey(AarDropdown, db_column='increment_type', max_length=50, on_delete=models.SET_NULL, null=True)#NORMAL/SPECIAL
#     promoted_to = models.ForeignKey(EmployeeDropdown, db_column="promoted_to", max_length=200, on_delete=models.SET_NULL, null= True)
#     amount = models.FloatField(null = True)#ONLY IN SPECIAL
#     recommend=models.CharField(db_column="recommend", max_length=50, default='NO INCREMENT')#INCREMENT/NO INCREMENT/PROMOTION
#     status=models.CharField(db_column="status", max_length=50, default='INSERT')
#     remark=models.TextField(default=None,null=True)
#     whom=models.CharField(db_column="whom", max_length=10, default='HOD')
#     by_emp_id = models.ForeignKey(EmployeePrimdetail,db_column='emp_id',on_delete=models.SET_NULL,null=True,related_name="emp_empp_id")
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)

#     class Meta:
#         db_table = 'FacAppRecommend'
#         managed = True


