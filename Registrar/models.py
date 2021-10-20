from __future__ import unicode_literals
from django.db import models
from login.models import AuthUser,EmployeeDropdown, EmployeePrimdetail


class StudentDropdown(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='Pid', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=500, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=500, blank=True, null=True)  # Field name made lowercase.
    is_edit = models.IntegerField(db_column='Is_Edit', default='1')  # Field name made lowercase.
    is_delete = models.IntegerField(db_column='Is_Delete', default='1')  # Field name made lowercase.
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Student_Dropdown'


class Semtiming(models.Model):
    uid = models.IntegerField(db_column='Uid', primary_key=True)  # Field name made lowercase.
    session = models.CharField(max_length=15, blank=True, null=True)
    sem_type = models.CharField(max_length=20, blank=True, null=True)
    sem_end = models.DateField(blank=True, null=True)
    sem_start = models.DateField(blank=True, null=True)
    session_name = models.CharField(max_length=25)

    class Meta:
        managed = True
        db_table = 'sem_timing'


class CourseDetail(models.Model):
    uid = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    course_duration = models.IntegerField(db_column='Course_duration')  # Field name made lowercase.
    course = models.ForeignKey(StudentDropdown, related_name='StudentDropdown_Course_id', db_column='Course_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    course_type = models.ForeignKey(StudentDropdown, related_name='StudentDropdown_Course_type', db_column='Course_type', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    dept = models.ForeignKey(EmployeeDropdown, related_name='EmployeeDropdown_Dept_id', db_column='Dept_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    capacity = models.IntegerField(db_column='capacity', default=0)  # Field name made lowercase.
    lateral_capacity = models.IntegerField(db_column='lateral_capacity', default=0)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Student_course_detail'


class AdmissionEligibility(models.Model):
    min_marks = models.IntegerField(db_column='Min_marks')  # Field name made lowercase.
    admission_through = models.ForeignKey(StudentDropdown, related_name='AdmissionEligibility_Admission_through', db_column='Admission_through', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    admission_type = models.ForeignKey(StudentDropdown, related_name='AdmissionEligibility_Admission_type', db_column='Admission_type', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    caste = models.ForeignKey(StudentDropdown, related_name='AdmissionEligibility_Caste', db_column='Caste', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    course = models.ForeignKey(StudentDropdown, related_name='AdmissionEligibility_Course_id', db_column='Course_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    eligible_entry = models.ForeignKey(StudentDropdown, related_name='AdmissionEligibility_Eligible_entry', db_column='Eligible_entry', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Student_admision_eligibility'


class StudentSemester(models.Model):
    sem_id = models.AutoField(db_column='Sem_Id', primary_key=True)  # Field name made lowercase.
    sem = models.IntegerField(db_column='Sem')  # Field name made lowercase.
    dept = models.ForeignKey(CourseDetail, related_name='CourseDetail_Dept', db_column='Dept', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'student_semester'


class Sections(models.Model):
    section_id = models.AutoField(db_column='Section_id', primary_key=True)  # Field name made lowercase.
    section = models.CharField(db_column='Section', max_length=45)  # Field name made lowercase.
    # groups = models.IntegerField(db_column='Groups', blank=True,null=True)  # Field name made lowercase.
    sem_id = models.ForeignKey(StudentSemester, related_name='Sections_StudentSemester_Sections_sem_id', db_column='Sem_id', null=True, on_delete=models.SET_NULL)
    dept = models.ForeignKey(CourseDetail, related_name='Sections_CourseDetail_Sections_dept', db_column='Dept_detail', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sections'


class StudentPrimDetail(models.Model):
    name = models.CharField(db_column='Name', max_length=500)  # Field name made lowercase.
    batch_from = models.IntegerField(db_column='Batch_from')  # Field name made lowercase.
    batch_to = models.IntegerField(db_column='Batch_to')  # Field name made lowercase.
    exam_roll_no = models.CharField(db_column='Exam_Roll_No', max_length=100)  # Field name made lowercase.
    general_rank = models.IntegerField(db_column='General_Rank', blank=True, null=True)  # Field name made lowercase.
    category_rank = models.IntegerField(db_column='Category_Rank', blank=True, null=True)  # Field name made lowercase.
    gen_rank = models.IntegerField(db_column='Gen_Rank', blank=True, null=True)  # Field name made lowercase.
    uni_roll_no = models.CharField(db_column='Uni_Roll_No', max_length=15, blank=True, null=True)  # Field name made lowercase.
    join_year = models.IntegerField(db_column='Join_Year')  # Field name made lowercase.
    email_id = models.CharField(db_column='Email_id', max_length=500, blank=True, null=True)  # Field name made lowercase.
    date_of_add = models.DateField(db_column='Date_Of_Add')  # Field name made lowercase.
    uniq_id = models.AutoField(db_column='Uniq_Id', primary_key=True)  # Field name made lowercase.
    old_uniq_id = models.CharField(db_column='old_uniq_id', max_length=500, blank=True, null=True, default=None)  # Field name made lowercase.
    form_fill_status = models.CharField(db_column='Form_Fill_Status', max_length=2, default='N')  # Field name made lowercase.
    fee_waiver = models.CharField(db_column='Fee_Waiver', max_length=41, default='N')  # Field name made lowercase.
    remark = models.CharField(max_length=500, blank=True, null=True)
    remark_detail = models.CharField(max_length=500, db_column='remark_detail', blank=True, null=True, default=None)
    admission_category = models.ForeignKey(StudentDropdown, related_name='StudentPrimDetail_StudentDropdown_Admission_category', db_column='Admission_category', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    admission_through = models.ForeignKey(StudentDropdown, related_name='StudentPrimDetail_StudentDropdown_Admission_through', db_column='Admission_through', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    admission_type = models.ForeignKey(StudentDropdown, related_name='StudentPrimDetail_StudentDropdown_Admission_type', db_column='Admission_type', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    dept_detail = models.ForeignKey(CourseDetail, related_name='StudentPrimDetail_CourseDetail_Dept_detail', db_column='Dept_detail', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    exam_type = models.ForeignKey(StudentDropdown, related_name='StudentPrimDetail_StudentDropdown_Exam_type', db_column='Exam_type', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    lib = models.ForeignKey(AuthUser, to_field='username', related_name='StudentPrimDetail_AuthUser_Lib_id', db_column='Lib_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    stu_type = models.ForeignKey(StudentDropdown, related_name='StudentPrimDetail_StudentDropdown_Stu_Type', db_column='Stu_Type', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    admission_status = models.ForeignKey(StudentDropdown, related_name='StudentPrimDetail_StudentDropdown_admission_status', db_column='admission_status', blank=True, null=True, default=52, on_delete=models.SET_NULL)
    caste = models.ForeignKey(StudentDropdown, related_name='StudentPerDetail_StudentDropdown_Caste', db_column='Caste', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    gender = models.ForeignKey(StudentDropdown, related_name='StudentPerDetail_StudentDropdown_Gender', db_column='Gender', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    old_uniq_id = models.CharField(max_length=50)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        managed = True
        db_table = 'Student_primdetail'


# class studentSession_1718e(models.Model):
#     uniq_id = models.OneToOneField(StudentPrimDetail, related_name='studentSession_1718e_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
#     mob = models.BigIntegerField(db_column='Mob', blank=True, null=True)  # Field name made lowercase.
#     fee_status = models.CharField(db_column='Fee_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     # session = models.CharField(db_column='Session', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     session = models.ForeignKey(Semtiming, related_name='S1718Session', db_column='session', null=True, on_delete=models.SET_NULL)
#     year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
#     class_roll_no = models.IntegerField(db_column='Class_Roll_No', blank=True, null=True)  # Field name made lowercase.
#     registration_status = models.IntegerField(db_column='Registration_Status', blank=True, null=True)  # Field name made lowercase.
#     acc_reg = models.IntegerField(db_column='Acc_Reg', blank=True, null=True)  # Field name made lowercase.
#     section = models.ForeignKey(Sections, related_name='studentSession_1718e_Sections_Section_id', db_column='Section_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
#     sem = models.ForeignKey(Sections, related_name='studentSession_1718e_Semtiming_Sem_id', db_column='Sem_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.

#     class Meta:
#         managed = True
#         db_table = 'studentSesion_1718e'


class studentSession_1819o(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='studentSession_1819o_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    mob = models.BigIntegerField(db_column='Mob', blank=True, null=True)  # Field name made lowercase.
    fee_status = models.CharField(db_column='Fee_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    session = models.ForeignKey(Semtiming, related_name='S1819Session', db_column='session', null=True, on_delete=models.SET_NULL)
    # session = models.CharField(db_column='Session', max_length=20, blank=True, null=True)  # Field name made lowercase.
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    class_roll_no = models.IntegerField(db_column='Class_Roll_No', blank=True, null=True)  # Field name made lowercase.
    registration_status = models.IntegerField(db_column='Registration_Status', blank=True, null=True, default=1)  # Field name made lowercase.
    acc_reg = models.IntegerField(db_column='Acc_Reg', blank=True, null=True)  # Field name made lowercase.
    section = models.ForeignKey(Sections, related_name='studentSession_1819o_Sections_Section_id', db_column='Section_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    sem = models.ForeignKey(StudentSemester, related_name='studentSession_1819o_Semtiming_Sem_id', db_column='Sem_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    att_start_date = models.DateField(default=None, null=True)
    ############## by default it will be equal to semester commencement date as defined by DEAN ACADEMICS for that semester ###########
    reg_form_status = models.CharField(max_length=10, default='LOCK')
    ############### LOCK OR UNLOCK #######################################
    reg_date_time = models.DateTimeField(default=None, null=True)

    class Meta:
        managed = True
        db_table = 'studentSession_1819o'


class studentSession_1920o(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='studentSession_1920o_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    mob = models.BigIntegerField(db_column='Mob', blank=True, null=True)  # Field name made lowercase.
    fee_status = models.CharField(db_column='Fee_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    session = models.ForeignKey(Semtiming, related_name='S1920Session', db_column='session', null=True, on_delete=models.SET_NULL)
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    class_roll_no = models.IntegerField(db_column='Class_Roll_No', blank=True, null=True)  # Field name made lowercase.
    registration_status = models.IntegerField(db_column='Registration_Status', blank=True, null=True, default=1)  # Field name made lowercase.
    acc_reg = models.IntegerField(db_column='Acc_Reg', blank=True, null=True)  # Field name made lowercase.
    section = models.ForeignKey(Sections, related_name='studentSession_1920o_Sections_Section_id', db_column='Section_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    sem = models.ForeignKey(StudentSemester, related_name='studentSession_1920o_Semtiming_Sem_id', db_column='Sem_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    att_start_date = models.DateField(default=None, null=True)
    ############## by default it will be equal to semester commencement date as defined by DEAN ACADEMICS for that semester ###########
    reg_form_status = models.CharField(max_length=10, default='LOCK')
    ############### LOCK OR UNLOCK #######################################
    reg_date_time = models.DateTimeField(default=None, null=True)

    class Meta:
        managed = True
        db_table = 'studentSession_1920o'


class StudentPerDetail(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='StudentPerDetail_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    fname = models.CharField(db_column='FName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mob_sec = models.BigIntegerField(db_column='Mob_Sec',   blank=True, null=True)  # Field name made lowercase.
    dob = models.DateField(db_column='DOB', blank=True, null=True)  # Field name made lowercase.
    image_path = models.CharField(max_length=500, blank=True, null=True)
    aadhar_num = models.BigIntegerField(blank=True, null=True)
    bank_acc_no = models.CharField(db_column='bank_Acc_no', max_length=40, blank=True, null=True)  # Field name made lowercase.
    pan_no = models.CharField(max_length=40, blank=True, null=True)
    uan_no = models.IntegerField(blank=True, null=True)
    physically_disabled = models.CharField(max_length=41, blank=True, null=True)
    bg = models.ForeignKey(EmployeeDropdown, related_name='StudentPerDetail_StudentDropdown_Bg', db_column='Bg', blank=True, null=True, default=1013, on_delete=models.SET_NULL)  # Field name made lowercase.
    marital_status = models.ForeignKey(EmployeeDropdown, related_name='StudentPerDetail_StudentDropdown_Marital_status', db_column='Marital_status', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    nationality = models.ForeignKey(EmployeeDropdown, related_name='StudentPerDetail_StudentDropdown_Nationality', db_column='Nationality', blank=True, null=True, default=261, on_delete=models.SET_NULL)  # Field name made lowercase.
    religion = models.ForeignKey(EmployeeDropdown, related_name='StudentPerDetail_StudentDropdown_Religion', db_column='Religion', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    mname = models.CharField(db_column='MName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    caste_name = models.CharField(max_length=40, blank=True, null=True)
    nation_other = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = 'Student_perdetail'
        managed = True


class RegistrarSessionCapacity(models.Model):
    session = models.CharField(db_column='session', max_length=50, null=True, blank=True)
    capacity = models.IntegerField(db_column='capacity', default=0)
    lateral_capacity = models.IntegerField(db_column='lateral_capacity', default=0)
    course = models.ForeignKey(CourseDetail, related_name='RegistrarSessionCapacity_course', db_column='course', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'Registrar_session_capacity'


class StudentAcademic(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='StudentAcademic_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    app_no = models.BigIntegerField(db_column='Application_No', blank=True, null=True)  # Field name made lowercase.
    year_10 = models.IntegerField(db_column='Year_10', blank=True, null=True)  # Field name made lowercase.
    per_10 = models.FloatField(db_column='Per_10', blank=True, null=True)  # Field name made lowercase.
    max_10 = models.FloatField(db_column='Max_10', blank=True, null=True)  # Field name made lowercase.
    total_10 = models.FloatField(db_column='Total_10', blank=True, null=True)  # Field name made lowercase.
    year_12 = models.IntegerField(db_column='Year_12', blank=True, null=True)  # Field name made lowercase.
    per_12 = models.FloatField(db_column='Per_12', blank=True, null=True)  # Field name made lowercase.
    max_12 = models.FloatField(db_column='Max_12', blank=True, null=True)  # Field name made lowercase.
    total_12 = models.FloatField(db_column='Total_12', blank=True, null=True)  # Field name made lowercase.
    phy_12 = models.FloatField(db_column='Phy_12', blank=True, null=True)  # Field name made lowercase.
    phy_max = models.FloatField(db_column='Phy_Max', blank=True, null=True)  # Field name made lowercase.
    chem_12 = models.FloatField(db_column='Chem_12', blank=True, null=True)  # Field name made lowercase.
    chem_max = models.FloatField(db_column='Chem_Max', blank=True, null=True)  # Field name made lowercase.
    math_12 = models.FloatField(db_column='Math_12', blank=True, null=True)  # Field name made lowercase.
    math_max = models.FloatField(db_column='Math_Max', blank=True, null=True)  # Field name made lowercase.
    eng_12 = models.FloatField(db_column='Eng_12', blank=True, null=True)  # Field name made lowercase.
    eng_max = models.FloatField(db_column='Eng_Max', blank=True, null=True)  # Field name made lowercase.
    bio_12 = models.FloatField(db_column='Bio_12', blank=True, null=True)  # Field name made lowercase.
    bio_max = models.FloatField(db_column='Bio_Max', blank=True, null=True)  # Field name made lowercase.
    cs_12 = models.FloatField(db_column='Cs_12',blank=True,null=True)
    cs_max = models.FloatField(db_column ='Cs_Max',blank=True,null=True)
    pcm_total = models.FloatField(db_column='PCM_Total', blank=True, null=True)  # Field name made lowercase.
    is_dip = models.CharField(db_column='Is_Dip', max_length=9, default='0', null=True)  # Field name made lowercase.
    year_dip = models.IntegerField(db_column='Year_Dip', blank=True, null=True)  # Field name made lowercase.
    per_dip = models.FloatField(db_column='Per_Dip', blank=True, null=True)  # Field name made lowercase.
    max_dip = models.FloatField(db_column='Max_Dip', blank=True, null=True)  # Field name made lowercase.
    total_dip = models.FloatField(db_column='Total_Dip', blank=True, null=True)  # Field name made lowercase.
    ug_year1 = models.FloatField(db_column='UG_Year1', blank=True, null=True)  # Field name made lowercase.
    ug_year1_max = models.FloatField(db_column='UG_Year1_Max', blank=True, null=True)  # Field name made lowercase.
    ug_year1_back = models.FloatField(db_column='UG_Year1_Back', blank=True, null=True)  # Field name made lowercase.
    ug_year2 = models.FloatField(db_column='UG_Year2', blank=True, null=True)  # Field name made lowercase.
    ug_year2_max = models.FloatField(db_column='UG_Year2_Max', blank=True, null=True)  # Field name made lowercase.
    ug_year2_back = models.FloatField(db_column='UG_Year2_Back', blank=True, null=True)  # Field name made lowercase.
    ug_year3 = models.FloatField(db_column='UG_Year3', blank=True, null=True)  # Field name made lowercase.
    ug_year3_max = models.FloatField(db_column='UG_Year3_Max', blank=True, null=True)  # Field name made lowercase.
    ug_year3_back = models.FloatField(db_column='UG_Year3_Back', blank=True, null=True)  # Field name made lowercase.
    ug_year4 = models.FloatField(db_column='UG_Year4', blank=True, null=True)  # Field name made lowercase.
    ug_year4_max = models.FloatField(db_column='UG_Year4_Max', blank=True, null=True)  # Field name made lowercase.
    ug_year4_back = models.FloatField(db_column='UG_Year4_Back', blank=True, null=True)  # Field name made lowercase.
    year_ug = models.IntegerField(db_column='Year_UG', blank=True, null=True)  # Field name made lowercase.
    per_ug = models.FloatField(db_column='Per_UG', blank=True, null=True)  # Field name made lowercase.
    max_ug = models.FloatField(db_column='Max_UG', blank=True, null=True)  # Field name made lowercase.
    total_ug = models.FloatField(db_column='Total_UG', blank=True, null=True)  # Field name made lowercase.
    sem1_ug = models.FloatField(db_column='Sem1_UG', blank=True, null=True)  # Field name made lowercase.
    sem1_ug_max = models.FloatField(db_column='Sem1_UG_Max', blank=True, null=True)  # Field name made lowercase.
    sem1_ug_back = models.FloatField(db_column='Sem1_UG_Back', blank=True, null=True)  # Field name made lowercase.
    sem2_ug = models.FloatField(db_column='Sem2_UG', blank=True, null=True)  # Field name made lowercase.
    sem2_ug_max = models.FloatField(db_column='Sem2_UG_Max', blank=True, null=True)  # Field name made lowercase.
    sem2_ug_back = models.FloatField(db_column='Sem2_UG_Back', blank=True, null=True)  # Field name made lowercase.
    sem3_ug = models.FloatField(db_column='Sem3_UG', blank=True, null=True)  # Field name made lowercase.
    sem3_ug_max = models.FloatField(db_column='Sem3_UG_Max', blank=True, null=True)  # Field name made lowercase.
    sem3_ug_back = models.FloatField(db_column='Sem3_UG_Back', blank=True, null=True)  # Field name made lowercase.
    sem4_ug = models.FloatField(db_column='Sem4_UG', blank=True, null=True)  # Field name made lowercase.
    sem4_ug_max = models.FloatField(db_column='Sem4_UG_Max', blank=True, null=True)  # Field name made lowercase.
    sem4_ug_back = models.FloatField(db_column='Sem4_UG_Back', blank=True, null=True)  # Field name made lowercase.
    sem5_ug = models.FloatField(db_column='Sem5_UG', blank=True, null=True)  # Field name made lowercase.
    sem5_ug_max = models.FloatField(db_column='Sem5_UG_Max', blank=True, null=True)  # Field name made lowercase.
    sem5_ug_back = models.FloatField(db_column='Sem5_UG_Back', blank=True, null=True)  # Field name made lowercase.
    sem6_ug = models.FloatField(db_column='Sem6_UG', blank=True, null=True)  # Field name made lowercase.
    sem6_ug_max = models.FloatField(db_column='Sem6_UG_Max', blank=True, null=True)  # Field name made lowercase.
    sem6_ug_back = models.FloatField(db_column='Sem6_UG_Back', blank=True, null=True)  # Field name made lowercase.
    sem7_ug = models.FloatField(db_column='Sem7_UG', blank=True, null=True)  # Field name made lowercase.
    sem7_ug_max = models.FloatField(db_column='Sem7_UG_Max', blank=True, null=True)  # Field name made lowercase.
    sem7_ug_back = models.FloatField(db_column='Sem7_UG_Back', blank=True, null=True)  # Field name made lowercase.
    sem8_ug = models.FloatField(db_column='Sem8_UG', blank=True, null=True)  # Field name made lowercase.
    sem8_ug_max = models.FloatField(db_column='Sem8_UG_Max', blank=True, null=True)  # Field name made lowercase.
    sem8_ug_back = models.FloatField(db_column='Sem8_UG_Back', blank=True, null=True)  # Field name made lowercase.
    pg_year1 = models.FloatField(db_column='PG_Year1', blank=True, null=True)  # Field name made lowercase.
    pg_year1_max = models.FloatField(db_column='PG_Year1_MAX', blank=True, null=True)  # Field name made lowercase.
    pg_year1_back = models.FloatField(db_column='PG_Year1_Back', blank=True, null=True)  # Field name made lowercase.
    pg_year2 = models.FloatField(db_column='PG_Year2', blank=True, null=True)  # Field name made lowercase.
    pg_year2_max = models.FloatField(db_column='PG_Year2_MAX', blank=True, null=True)  # Field name made lowercase.
    pg_year2_back = models.FloatField(db_column='PG_Year2_Back', blank=True, null=True)  # Field name made lowercase.
    pg_year3 = models.FloatField(db_column='PG_Year3', blank=True, null=True)  # Field name made lowercase.
    pg_year3_max = models.FloatField(db_column='PG_Year3_MAX', blank=True, null=True)  # Field name made lowercase.
    pg_year3_back = models.FloatField(db_column='PG_Year3_Back', blank=True, null=True)  # Field name made lowercase.
    year_pg = models.FloatField(db_column='Year_PG', blank=True, null=True)  # Field name made lowercase.
    per_pg = models.FloatField(db_column='Per_PG', blank=True, null=True)  # Field name made lowercase.
    sem1_pg = models.FloatField(db_column='Sem1_PG', blank=True, null=True)  # Field name made lowercase.
    sem1_pg_max = models.FloatField(db_column='Sem1_PG_MAX', blank=True, null=True)  # Field name made lowercase.
    sem1_pg_back = models.FloatField(db_column='Sem1_PG_Back', blank=True, null=True)  # Field name made lowercase.
    sem2_pg = models.FloatField(db_column='Sem2_PG', blank=True, null=True)  # Field name made lowercase.
    sem2_pg_max = models.FloatField(db_column='Sem2_PG_MAX', blank=True, null=True)  # Field name made lowercase.
    sem2_pg_back = models.FloatField(db_column='Sem2_PG_Back', blank=True, null=True)  # Field name made lowercase.
    sem3_pg = models.FloatField(db_column='Sem3_PG', blank=True, null=True)  # Field name made lowercase.
    sem3_pg_max = models.FloatField(db_column='Sem3_PG_MAX', blank=True, null=True)  # Field name made lowercase.
    sem3_pg_back = models.FloatField(db_column='Sem3_PG_Back', blank=True, null=True)  # Field name made lowercase.
    sem4_pg = models.FloatField(db_column='Sem4_PG', blank=True, null=True)  # Field name made lowercase.
    sem4_pg_max = models.FloatField(db_column='Sem4_PG_MAX', blank=True, null=True)  # Field name made lowercase.
    sem4_pg_back = models.FloatField(db_column='Sem4_PG_Back', blank=True, null=True)  # Field name made lowercase.
    sem5_pg = models.FloatField(db_column='Sem5_PG', blank=True, null=True)  # Field name made lowercase.
    sem5_pg_max = models.FloatField(db_column='Sem5_PG_MAX', blank=True, null=True)  # Field name made lowercase.
    sem5_pg_back = models.FloatField(db_column='Sem5_PG_Back', blank=True, null=True)  # Field name made lowercase.
    sem6_pg = models.FloatField(db_column='Sem6_PG', blank=True, null=True)  # Field name made lowercase.
    sem6_pg_max = models.FloatField(db_column='Sem6_PG_MAX', blank=True, null=True)  # Field name made lowercase.
    sem6_pg_back = models.FloatField(db_column='Sem6_PG_Back', blank=True, null=True)  # Field name made lowercase.
    area_dip = models.CharField(db_column='Area_Dip', max_length=100, blank=True, null=True)  # Field name made lowercase.
    ug_degree = models.CharField(db_column='UG_Degree', max_length=100, blank=True, null=True)  # Field name made lowercase.
    ug_area = models.CharField(db_column='UG_Area', max_length=100, blank=True, null=True)  # Field name made lowercase.
    pg_degree = models.CharField(db_column='PG_Degree', max_length=100, blank=True, null=True)  # Field name made lowercase.
    pg_area = models.CharField(db_column='PG_Area', max_length=100, blank=True, null=True)  # Field name made lowercase.
    board_10 = models.ForeignKey(EmployeeDropdown, related_name='StudentAcademic_EmployeeDropdown_Board_10', db_column='Board_10', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    board_12 = models.ForeignKey(EmployeeDropdown, related_name='StudentAcademic_EmployeeDropdown_Board_12', db_column='Board_12', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    uni_dip = models.ForeignKey(EmployeeDropdown, related_name='StudentAcademic_EmployeeDropdown_Uni_Dip', db_column='Uni_Dip', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    uni_pg = models.ForeignKey(EmployeeDropdown, related_name='StudentAcademic_EmployeeDropdown_Uni_PG', db_column='Uni_PG', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    uni_ug = models.ForeignKey(EmployeeDropdown, related_name='StudentAcademic_EmployeeDropdown_Uni_UG', db_column='Uni_UG', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    is_gate_or_gpat = models.CharField(db_column='is_gate_or_gpat', max_length=9, default=None, null=True)
    gate_or_gpat_qualified = models.CharField(db_column='gate_or_gpat_qualified', max_length=40, default=None, null=True)
    gate_or_gpat_discipline = models.CharField(db_column='gate_or_gpat_discipline', max_length=40, default=None, null=True)
    gate_or_gpat_rank = models.IntegerField(db_column='gate_or_gpat_rank', blank=True, null=True)
    gate_or_gpat_year = models.IntegerField(db_column='gate_or_gpat_year', blank=True, null=True)
    gate_or_gpat_score = models.IntegerField(db_column='gate_or_gpat_score', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Student_Academic'


class StudentDocument(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='StudentDocument_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    allot_letter = models.CharField(db_column='Allot_Letter', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_10 = models.CharField(db_column='Marksheet_10', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_12 = models.CharField(db_column='Marksheet_12', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_dip = models.CharField(db_column='Marksheet_Dip', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_ug = models.CharField(db_column='Marksheet_Ug', max_length=50, blank=True, null=True)  # Field name made lowercase.
    caste_certificate = models.CharField(db_column='Caste_Certificate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    domicile_certificate = models.CharField(db_column='Domicile_Certificate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    addressid = models.CharField(db_column='AddressId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    father_pic = models.CharField(db_column='Father_Pic', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mother_pic = models.CharField(db_column='Mother_Pic', max_length=50, blank=True, null=True)  # Field name made lowercase.
    guardian_pic = models.CharField(db_column='Guardian_Pic', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Student_Document'


class StudentFamilyDetails(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='StudentFamilyDetails_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    father_mob = models.BigIntegerField(db_column='Father_Mob', blank=True, null=True)  # Field name made lowercase.
    father_email = models.CharField(db_column='Father_Email', max_length=500, blank=True, null=True)  # Field name made lowercase.
    father_income = models.FloatField(db_column='Father_Income', blank=True, null=True)  # Field name made lowercase.
    father_occupation = models.ForeignKey(StudentDropdown, db_column='Father_Occupation', related_name='Father_Occupation', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    father_dept = models.CharField(db_column='Father_Dept', max_length=500, blank=True, null=True)  # Field name made lowercase.
    father_add = models.CharField(db_column='Father_Add', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    father_city = models.CharField(db_column='Father_City', max_length=100, blank=True, null=True)  # Field name made lowercase.
    father_pan_no = models.CharField(db_column="Father_pan_no", null=True, max_length=40, blank=True, default=None)
    father_uan_no = models.CharField(db_column="Father_uan_no", null=True, max_length=40, blank=True, default=None)
    mother_mob = models.BigIntegerField(db_column='Mother_Mob', blank=True, null=True)  # Field name made lowercase.
    mother_email = models.CharField(db_column='Mother_Email', max_length=500, blank=True, null=True)  # Field name made lowercase.
    mother_income = models.FloatField(db_column='Mother_Income', blank=True, null=True)  # Field name made lowercase.
    mother_occupation = models.ForeignKey(StudentDropdown, db_column='Mother_Occupation', related_name='Mother_Occupation', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    mother_dept = models.CharField(db_column='Mother_Dept', max_length=500, blank=True, null=True)  # Field name made lowercase.
    mother_add = models.CharField(db_column='Mother_Add', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    mother_city = models.CharField(db_column='Mother_City', max_length=100, blank=True, null=True)  # Field name made lowercase.
    mother_pan_no = models.CharField(db_column="Mother_pan_no", null=True, max_length=40, blank=True, default=None)
    mother_uan_no = models.CharField(db_column="Mother_uan_no", null=True, max_length=40, blank=True, default=None)
    gname = models.CharField(db_column='Gname', max_length=500, blank=True, null=True)  # Field name made lowercase.
    g_relation = models.CharField(db_column='G_Relation', max_length=500, blank=True, null=True)  # Field name made lowercase.
    g_mob = models.BigIntegerField(db_column='G_Mob', blank=True, null=True)  # Field name made lowercase.
    g_email = models.CharField(db_column='G_Email', max_length=500, blank=True, null=True)  # Field name made lowercase.
    g_add = models.CharField(db_column='G_Add', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    g_city = models.CharField(db_column='G_City', max_length=100, blank=True, null=True)  # Field name made lowercase.
    g_pincode = models.CharField(db_column='G_Pincode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    g_state = models.ForeignKey(EmployeeDropdown, related_name='StudentAddress_G_State', db_column='G_State', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'Student_Family_Details'
        managed = True


class StudentAddress(models.Model):
    uniq_id = models.OneToOneField('StudentPrimdetail', related_name='StudentAddress_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    p_add1 = models.CharField(db_column='P_Add1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    p_add2 = models.CharField(db_column='P_Add2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    p_city = models.CharField(db_column='P_City', max_length=30, blank=True, null=True)  # Field name made lowercase.
    p_district = models.CharField(db_column='P_District', max_length=30, blank=True, null=True)  # Field name made lowercase.
    p_pincode = models.CharField(db_column='P_Pincode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    c_add1 = models.CharField(db_column='C_Add1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    c_add2 = models.CharField(db_column='C_Add2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    c_city = models.CharField(db_column='C_City', max_length=30, blank=True, null=True)  # Field name made lowercase.
    c_district = models.CharField(db_column='C_District', max_length=30, blank=True, null=True)  # Field name made lowercase.
    c_pincode = models.CharField(db_column='C_Pincode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    c_state = models.ForeignKey(EmployeeDropdown, related_name='StudentAddress_C_State', db_column='C_State', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    p_state = models.ForeignKey(EmployeeDropdown, related_name='StudentAddress_P_State', db_column='P_State', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'Student_Address'


class StudentBankDetails(models.Model):
    uniq_id = models.ForeignKey(StudentPrimDetail, related_name='StudentBank_Uniq_Id', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    acc_name = models.CharField(max_length=1000, null=True, default=None)
    acc_num = models.CharField(max_length=1000, null=True, default=None)
    bank_name = models.CharField(max_length=1000, null=True, default=None)
    ifsc_code = models.CharField(max_length=1000, null=True, default=None)
    branch = models.CharField(max_length=1000, null=True, default=None)
    address = models.CharField(max_length=1000, null=True, default=None)
    status = models.CharField(db_column="status", max_length=20, default="INSERT")  # change in case of fee update
    edit_by = models.ForeignKey(AuthUser, db_column='Edit_by', default=None, related_name='StudentBankdetails_AuthUser_username', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'Student_BankDetails'


class StudentBranchChange_1819o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819o, related_name='stu_br_ch_uniq', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    old_section = models.ForeignKey(Sections, related_name='OldChSec_1819o', db_column='old_section_id', on_delete=models.SET_NULL, null=True)
    new_section = models.ForeignKey(Sections, related_name='NewChSec_1819o', db_column='new_section_id', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="BrChEmp_1819o", null=True, on_delete=models.SET_NULL)
    change_type = models.CharField(db_column="change_type", max_length=20, null=True, default=None)  # 'S' for section/branch,'G' for group

    class Meta:
        managed = True
        db_table = 'Student_BranchChange_1819o'


#################################################################################################################
############################## 1819e models #####################################################################
#################################################################################################################


class studentSession_1819e(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='studentSession_1819e_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    mob = models.BigIntegerField(db_column='Mob', blank=True, null=True)  # Field name made lowercase.
    fee_status = models.CharField(db_column='Fee_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    session = models.ForeignKey(Semtiming, related_name='S1819eSession', db_column='session', null=True, on_delete=models.SET_NULL)
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    class_roll_no = models.IntegerField(db_column='Class_Roll_No', blank=True, null=True)  # Field name made lowercase.
    registration_status = models.IntegerField(db_column='Registration_Status', blank=True, null=True, default=1)  # Field name made lowercase.
    acc_reg = models.IntegerField(db_column='Acc_Reg', blank=True, null=True)  # Field name made lowercase.
    section = models.ForeignKey(Sections, related_name='studentSession_1819e_Sections_Section_id', db_column='Section_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    sem = models.ForeignKey(StudentSemester, related_name='studentSession_1819e_Semtiming_Sem_id', db_column='Sem_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    att_start_date = models.DateField(default=None, null=True)
    ############## by default it will be equal to semester commencement date as defined by DEAN ACADEMICS for that semester ###########
    reg_form_status = models.CharField(max_length=10, default='LOCK')
    ############### LOCK OR UNLOCK #######################################
    reg_date_time = models.DateTimeField(default=None, null=True)

    class Meta:
        managed = True
        db_table = 'studentSession_1819e'


class StudentBranchChange_1819e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='stu_br_ch_uniq', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    old_section = models.ForeignKey(Sections, related_name='OldChSec_1819e', db_column='old_section_id', on_delete=models.SET_NULL, null=True)
    new_section = models.ForeignKey(Sections, related_name='NewChSec_1819e', db_column='new_section_id', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="BrChEmp_1819e", null=True, on_delete=models.SET_NULL)
    change_type = models.CharField(db_column="change_type", max_length=20, null=True, default=None)  # 'S' for section/branch,'G' for group

    class Meta:
        managed = True
        db_table = 'Student_BranchChange_1819e'


#################################################################################################################
############################## 1920o models #####################################################################
#################################################################################################################


class StudentBranchChange_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='stu_br_ch_uniq', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    old_section = models.ForeignKey(Sections, related_name='OldChSec_1920o', db_column='old_section_id', on_delete=models.SET_NULL, null=True)
    new_section = models.ForeignKey(Sections, related_name='NewChSec_1920o', db_column='new_section_id', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="BrChEmp_1920o", null=True, on_delete=models.SET_NULL)
    change_type = models.CharField(db_column="change_type", max_length=20, null=True, default=None)  # 'S' for section/branch,'G' for group

    class Meta:
        managed = True
        db_table = 'Student_BranchChange_1920o'


##################################################################################################################
################################################## 1920e #########################################################


class studentSession_1920e(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='studentSession_1920e_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    mob = models.BigIntegerField(db_column='Mob', blank=True, null=True)  # Field name made lowercase.
    fee_status = models.CharField(db_column='Fee_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    session = models.ForeignKey(Semtiming, related_name='ES1920Session', db_column='session', null=True, on_delete=models.SET_NULL)
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    class_roll_no = models.IntegerField(db_column='Class_Roll_No', blank=True, null=True)  # Field name made lowercase.
    registration_status = models.IntegerField(db_column='Registration_Status', blank=True, null=True, default=1)  # Field name made lowercase.
    acc_reg = models.IntegerField(db_column='Acc_Reg', blank=True, null=True)  # Field name made lowercase.
    section = models.ForeignKey(Sections, related_name='studentSession_1920e_Sections_Section_id', db_column='Section_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    sem = models.ForeignKey(StudentSemester, related_name='studentSession_1920e_Semtiming_Sem_id', db_column='Sem_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    att_start_date = models.DateField(default=None, null=True)
    ############## by default it will be equal to semester commencement date as defined by DEAN ACADEMICS for that semester ###########
    reg_form_status = models.CharField(max_length=10, default='LOCK')
    ############### LOCK OR UNLOCK #######################################
    reg_date_time = models.DateTimeField(default=None, null=True)

    class Meta:
        managed = True
        db_table = 'studentSession_1920e'


class StudentBranchChange_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name='stu_br_ch_e_uniq', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    old_section = models.ForeignKey(Sections, related_name='OldChSec_1920e', db_column='old_section_id', on_delete=models.SET_NULL, null=True)
    new_section = models.ForeignKey(Sections, related_name='NewChSec_1920e', db_column='new_section_id', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="BrChEmp_1920e", null=True, on_delete=models.SET_NULL)
    change_type = models.CharField(db_column="change_type", max_length=20, null=True, default=None)  # 'S' for section/branch,'G' for group
    status = models.CharField(db_column="status", max_length=20, default="INSERT")

    class Meta:
        managed = True
        db_table = 'Student_BranchChange_1920e'


################################################ 2021o ##########################################################
class studentSession_2021o(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='studentSession_2021o_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    mob = models.BigIntegerField(db_column='Mob', blank=True, null=True)  # Field name made lowercase.
    fee_status = models.CharField(db_column='Fee_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    session = models.ForeignKey(Semtiming, related_name='S2021Session', db_column='session', null=True, on_delete=models.SET_NULL)
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    class_roll_no = models.IntegerField(db_column='Class_Roll_No', blank=True, null=True)  # Field name made lowercase.
    registration_status = models.IntegerField(db_column='Registration_Status', blank=True, null=True, default=1)  # Field name made lowercase.
    acc_reg = models.IntegerField(db_column='Acc_Reg', blank=True, null=True)  # Field name made lowercase.
    section = models.ForeignKey(Sections, related_name='studentSession_2021o_Sections_Section_id', db_column='Section_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    sem = models.ForeignKey(StudentSemester, related_name='studentSession_2021o_Semtiming_Sem_id', db_column='Sem_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    att_start_date = models.DateField(default=None, null=True)
    ############## by default it will be equal to semester commencement date as defined by DEAN ACADEMICS for that semester ###########
    reg_form_status = models.CharField(max_length=10, default='LOCK')
    ############### LOCK OR UNLOCK #######################################
    reg_date_time = models.DateTimeField(default=None, null=True)

    class Meta:
        managed = True
        db_table = 'studentSession_2021o'


class StudentBranchChange_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name='stu_br_ch_uniq_2021o', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    old_section = models.ForeignKey(Sections, related_name='OldChSec_2021o', db_column='old_section_id', on_delete=models.SET_NULL, null=True)
    new_section = models.ForeignKey(Sections, related_name='NewChSec_2021o', db_column='new_section_id', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="BrChEmp_2021o", null=True, on_delete=models.SET_NULL)
    change_type = models.CharField(db_column="change_type", max_length=20, null=True, default=None)  # 'S' for section/branch,'G' for group

    class Meta:
        managed = True
        db_table = 'Student_BranchChange_2021o'
#################################################################################################################

#  ####################################################2021e###################################################################
class studentSession_2021e(models.Model):
    uniq_id = models.OneToOneField(StudentPrimDetail, related_name='studentSession_2021e_StudentPrimDetail_Uniq_Id', db_column='Uniq_Id', primary_key=True, on_delete=models.CASCADE)  # Field name made lowercase.
    mob = models.BigIntegerField(db_column='Mob', blank=True, null=True)  # Field name made lowercase.
    fee_status = models.CharField(db_column='Fee_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    session = models.ForeignKey(Semtiming, related_name='S2021eSession', db_column='session', null=True, on_delete=models.SET_NULL)
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    class_roll_no = models.IntegerField(db_column='Class_Roll_No', blank=True, null=True)  # Field name made lowercase.
    registration_status = models.IntegerField(db_column='Registration_Status', blank=True, null=True, default=1)  # Field name made lowercase.
    acc_reg = models.IntegerField(db_column='Acc_Reg', blank=True, null=True)  # Field name made lowercase.
    section = models.ForeignKey(Sections, related_name='studentSession_2021e_Sections_Section_id', db_column='Section_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    sem = models.ForeignKey(StudentSemester, related_name='studentSession_2021e_Semtiming_Sem_id', db_column='Sem_id', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    att_start_date = models.DateField(default=None, null=True)
    ############## by default it will be equal to semester commencement date as defined by DEAN ACADEMICS for that semester ###########
    reg_form_status = models.CharField(max_length=10, default='LOCK')
    ############### LOCK OR UNLOCK #######################################
    reg_date_time = models.DateTimeField(default=None, null=True)

    class Meta:
        managed = True
        db_table = 'studentSession_2021e'


class StudentBranchChange_2021e(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='stu_br_ch_uniq_2021e', db_column='Uniq_Id', null=True, on_delete=models.SET_NULL)
    old_section = models.ForeignKey(Sections, related_name='OldChSec_2021e', db_column='old_section_id', on_delete=models.SET_NULL, null=True)
    new_section = models.ForeignKey(Sections, related_name='NewChSec_2021e', db_column='new_section_id', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="BrChEmp_2021e", null=True, on_delete=models.SET_NULL)
    change_type = models.CharField(db_column="change_type", max_length=20, null=True, default=None)  # 'S' for section/branch,'G' for group

    class Meta:
        managed = True
        db_table = 'Student_BranchChange_2021e'
# #################################################################################################################
