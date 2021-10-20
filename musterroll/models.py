from __future__ import unicode_literals

from django.db import models
from login.models import EmployeeDropdown,EmployeePrimdetail,AarDropdown
# Create your models here.

class EmployeePerdetail(models.Model):
    fname = models.CharField(db_column='FName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mname = models.CharField(db_column='MName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dob = models.DateField(db_column='DOB', blank=True, null=True)  # Field name made lowercase.
    bg = models.ForeignKey(EmployeeDropdown,db_column='Bg', related_name='BloodGroup', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    gender = models.ForeignKey(EmployeeDropdown,db_column='Gender', related_name='Gender', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    nationality = models.ForeignKey(EmployeeDropdown,db_column='Nationality', related_name='nationality', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    caste = models.ForeignKey(EmployeeDropdown, related_name='caste',db_column='Caste', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    marital_status = models.ForeignKey(EmployeeDropdown, related_name='marital_status',db_column='Marital_status', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    religion = models.ForeignKey(EmployeeDropdown, related_name='religion',db_column='Religion', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    image_path = models.CharField(max_length=500, blank=True, null=True)
    emp_id = models.OneToOneField(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_per', primary_key=True, unique=True, max_length=20, on_delete=models.CASCADE)  # Field name made lowercase.
    aadhar_num=models.CharField(db_column="aadhar_num",null=True,max_length=40,blank=True,default=None)
    bank_Acc_no=models.CharField(db_column="bank_Acc_no",null=True,max_length=40,blank=True,default=None)
    pan_no=models.CharField(db_column="pan_no",null=True,max_length=40,blank=True,default=None)
    uan_no=models.CharField(db_column="uan_no",null=True,max_length=40,blank=True,default=None)
    linked_in_url=models.CharField(db_column="linked_in_url",null=True,max_length=500,blank=True,default=None)

    class Meta:
        db_table = 'employee_perdetail'
        managed = True


class EmployeeAcademic(models.Model):
    pass_year_10 = models.IntegerField(db_column='Pass_Year_10', blank=True, null=True)  # Field name made lowercase.
    board_10 = models.ForeignKey(EmployeeDropdown,db_column='Board_10', related_name='board10', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    cgpa_per_10 = models.DecimalField(db_column='Cgpa_Per_10', max_digits=5, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    pass_year_12 = models.IntegerField(db_column='Pass_Year_12', blank=True, null=True)  # Field name made lowercase.
    board_12 = models.ForeignKey(EmployeeDropdown,db_column='Board_12', related_name='board12', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    cgpa_per_12 = models.DecimalField(db_column='Cgpa_Per_12', max_digits=5, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    pass_year_dip = models.IntegerField(db_column='Pass_Year_Dip', blank=True, null=True)  # Field name made lowercase.
    univ_dip = models.ForeignKey(EmployeeDropdown, related_name='DiplomaUniversity',db_column='Univ_Dip', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    cgpa_per_dip = models.DecimalField(db_column='Cgpa_Per_Dip', max_digits=5, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    pass_year_ug = models.IntegerField(db_column='Pass_Year_Ug', blank=True, null=True)  # Field name made lowercase.
    univ_ug = models.ForeignKey(EmployeeDropdown,db_column='Univ_UG', related_name='UG_University', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    degree_ug = models.ForeignKey(EmployeeDropdown,db_column='Degree_UG', related_name='UG_Degree', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    cgpa_per_ug = models.DecimalField(db_column='Cgpa_Per_Ug', max_digits=5, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    pass_year_pg = models.IntegerField(db_column='Pass_Year_Pg', blank=True, null=True)  # Field name made lowercase.
    univ_pg = models.ForeignKey(EmployeeDropdown,db_column='Univ_PG', related_name='PG_University', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    degree_pg = models.ForeignKey(EmployeeDropdown,db_column='Degree_PG', related_name='PG_Degree', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    cgpa_per_pg = models.DecimalField(db_column='Cgpa_Per_Pg', max_digits=5, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    area_spl_pg = models.CharField(db_column='Area_Spl_Pg', max_length=200, blank=True, null=True)  # Field name made lowercase.
    doctrate = models.CharField(db_column='doctrate', max_length=200, blank=True, null=True)  # Field name made lowercase.
    univ_doctrate = models.ForeignKey(EmployeeDropdown,db_column='Univ_Doctrate', related_name='DoctrateUniversity', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    date_doctrate = models.DateField(db_column='Date_Doctrate', blank=True, null=True)  # Field name made lowercase.
    stage_doctrate = models.ForeignKey(EmployeeDropdown,db_column='Stage_Doctrate', related_name='stage_doctrate', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    research_topic_doctrate = models.CharField(db_column='Research_topic_doctrate', max_length=200, blank=True, null=True)  # Field name made lowercase.
    degree_other = models.ForeignKey(EmployeeDropdown,db_column='Degree_Other', related_name='DegreeOther', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    pass_year_other = models.IntegerField(db_column='Pass_Year_Other', blank=True, null=True)  # Field name made lowercase.
    univ_other = models.ForeignKey(EmployeeDropdown,db_column='Univ_Other', related_name='OtherUniversity', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    cgpa_per_other = models.DecimalField(db_column='Cgpa_Per_Other', max_digits=5, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    area_spl_other = models.CharField(db_column='Area_Spl_Other', max_length=50, blank=True, null=True)  # Field name made lowercase.
    emp_id = models.OneToOneField(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_academic', primary_key=True, unique=True, max_length=20, on_delete=models.CASCADE)  # Field name made lowercase.
    area_spl_ug = models.CharField(db_column='Area_Spl_Ug', max_length=200, blank=True, null=True)  # Field name made lowercase.
    dip_area = models.CharField(db_column='Dip_Area', max_length=200, blank=True, null=True)  # Field name made lowercase.
    class Meta:
        db_table = 'employee_academic'
        managed = True

class EmployeeDocuments(models.Model):
    emp_id = models.OneToOneField(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_doc', primary_key=True, unique=True, max_length=20, on_delete=models.CASCADE)  # Field name made lowercase.
    marksheet_10 = models.CharField(db_column='Marksheet_10', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_12 = models.CharField(db_column='Marksheet_12', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_dip = models.CharField(db_column='Marksheet_Dip', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_ug = models.CharField(db_column='Marksheet_Ug', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_pg = models.CharField(db_column='Marksheet_Pg', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_doctrate = models.CharField(db_column='Marksheet_Doctrate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    marksheet_other = models.CharField(db_column='Marksheet_Other', max_length=50, blank=True, null=True)  # Field name made lowercase.
    medical_fitness = models.CharField(db_column='Medical_Fitness', max_length=50, blank=True, null=True)  # Field name made lowercase.
    character_certificate = models.CharField(db_column='Character_Certificate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    experience_certificate = models.CharField(db_column='Experience_Certificate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pg_degree = models.CharField(db_column='Pg_Degree', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ug_degree = models.CharField(db_column='Ug_Degree', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'employee_documents'
        managed = True


class EmployeeAddress(models.Model):
    p_add1 = models.CharField(db_column='P_Add1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    p_add2 = models.CharField(db_column='P_Add2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    p_city = models.CharField(db_column='P_City', max_length=30, blank=True, null=True)  # Field name made lowercase.
    p_district = models.CharField(db_column='P_District', max_length=30, blank=True, null=True)  # Field name made lowercase.
    p_state = models.ForeignKey(EmployeeDropdown,db_column='P_State', related_name='PermanentState', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    p_pincode = models.CharField(db_column='P_Pincode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    c_add1 = models.CharField(db_column='C_Add1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    c_add2 = models.CharField(db_column='C_Add2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    c_city = models.CharField(db_column='C_City', max_length=30, blank=True, null=True)  # Field name made lowercase.
    c_district = models.CharField(db_column='C_District', max_length=30, blank=True, null=True)  # Field name made lowercase.
    c_state = models.ForeignKey(EmployeeDropdown,db_column='C_State', related_name='CorrespondenceState', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    c_pincode = models.CharField(db_column='C_Pincode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    emp_id = models.OneToOneField(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_addr', primary_key=True, unique=True, max_length=20, on_delete=models.CASCADE)  # Field name made lowercase.

    class Meta:
        db_table = 'employee_address'

class EmployeeResearch(models.Model):
    research_years = models.IntegerField(db_column='Research_Years', blank=True, null=True)  # Field name made lowercase.
    research_months = models.IntegerField(db_column='Research_Months', blank=True, null=True)  # Field name made lowercase.
    industry_years = models.IntegerField(db_column='Industry_Years', blank=True, null=True)  # Field name made lowercase.
    industry_months = models.IntegerField(db_column='Industry_Months', blank=True, null=True)  # Field name made lowercase.
    teaching_years = models.IntegerField(db_column='Teaching_Years', blank=True, null=True)  # Field name made lowercase.
    teaching_months = models.IntegerField(db_column='Teaching_Months', blank=True, null=True)  # Field name made lowercase.
    emp_id = models.OneToOneField(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_research', primary_key=True, unique=True, max_length=20, on_delete=models.CASCADE)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=5000, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        db_table = 'employee_research'

class Reporting(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_rep', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    reporting_to = models.ForeignKey(EmployeeDropdown,db_column='Reporting_To', related_name='Designation', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    department = models.ForeignKey(EmployeeDropdown,db_column='Department', related_name='Department', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    reporting_no = models.IntegerField(db_column='Reporting_No', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'reporting'

class AarReporting(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='aaremployee_id_rep', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    reporting_to = models.ForeignKey(EmployeeDropdown,db_column='Reporting_To', related_name='aarDesignation', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    department = models.ForeignKey(EmployeeDropdown,db_column='Department', related_name='aarDepartment', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    reporting_no = models.IntegerField(db_column='Reporting_No', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Aar_reporting'

class Roles(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_role', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    roles = models.ForeignKey(EmployeeDropdown,db_column='roles', related_name='role', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.

    class Meta:
        db_table = 'roles'

class NoDuesHead(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase                                                                                       owercase.
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='nodue_emp', blank=True, null=True,on_delete=models.SET_NULL) # Field name made lowercase                                                                                        l=True)  # Field name made lowercase.
    due_head = models.ForeignKey(EmployeeDropdown,db_column='Due_Head', related_name='nodue_head', blank=True, null=True,on_delete=models.SET_NULL) # Field name made lowercase
    status = models.CharField(db_column='Status', max_length=15, blank=True, default='ACTIVE')  # Field name made lowercase


    class Meta:
        db_table = 'no_dues_head'

class EmployeeSeparation(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='emp_id_sepration', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    type = models.ForeignKey(EmployeeDropdown,db_column='Type', max_length=20, blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    rejoin_date = models.DateField(db_column='Rejoin_Date', blank=True, null=True)  # Field name made lowercase.
    emp_remark = models.CharField(db_column='Emp_Remark', max_length=5000, blank=True, null=True)  # Field name made lowercase.
    final_status = models.CharField(db_column='Final_Status', max_length=51, blank=True, null=True,default="PENDING")  # Field name made lowercase.
    final_remark = models.CharField(db_column='Final_Remark', max_length=5000, blank=True, null=True)  # Field name made lowercase.
    attachment = models.CharField(db_column='Attachment', max_length=50, blank=True, null=True)  # Field name made lowercase.
    #separation_type=models.IntegerField(db_column='Separation_type',default=0)
    finalAppDate=models.DateField(db_column="FinalAppDate",default=None,blank=True, null=True)
    request_date=models.DateField(db_column="RequestDate",blank=True, null=True,auto_now_add=True)
    relieving_date=models.DateField(db_column="relieving_date",blank=True, null=True,default=None)
    current_level = models.IntegerField(db_column='current_level',default=0,null=True)#form at reporting level
    resignation_doc = models.CharField(db_column='resignation_doc',null=True,max_length=1000)
    application_status = models.CharField(db_column='application_status',default="INSERT",null=True,blank=True,max_length=25)
    cheque_no = models.CharField(db_column='cheque_no',null=True,blank=True,max_length=25)
    bank = models.CharField(db_column='bank_name',null=True,blank=True,max_length=25)
    amount = models.IntegerField(db_column='amount', blank=True, null=True)
    EL_days= models.IntegerField(db_column='EL_days', blank=True, null=True)
    Total_days=models.IntegerField(db_column='payable_days', blank=True, null=True)


    class Meta:
        db_table = 'employee_separation'
        managed=True
    
class NoDuesEmp(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase                                                                                        owercase.
    approved_by = models.ForeignKey(EmployeePrimdetail,db_column='approved_by', related_name='approved_by_e_id', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase                                                                              l=True)  # Field name made lowercase.
    due_head = models.ForeignKey(EmployeeDropdown,db_column='Due_Head', blank=True, null=True,on_delete=models.SET_NULL) # Field name made lowercase
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase                                                                                      l=True)  # Field name made lowercase.
    separation_id = models.ForeignKey(EmployeeSeparation,db_column='Separation_id', related_name='separation_due_id', blank=True, null=True,on_delete=models.SET_NULL) # Field name made lowercase                                                                                       ull=True)  # Field name made lowercase.
    approval_date=models.DateField(db_column="approval_date",default=None,blank=True, null=True)
    approval_status = models.CharField(db_column='approval_status',default='PENDING',max_length=20)#APPROVED HOLD CANCELED PENDING
    

    class Meta:
        db_table = 'no_dues_employee'
        managed=True


class Shifts(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    shiftid = models.ForeignKey(EmployeeDropdown,db_column='shiftId', related_name='emp_shift', blank=True, null=True,on_delete=models.SET_NULL)
    intime = models.TimeField(db_column='intime',max_length=10, blank=True, null=True)
    outtime = models.TimeField(db_column='outtime',max_length=10, blank=True, null=True)
    latein = models.TimeField(db_column='lateIn', max_length=10, blank=True, null=True)  # Field name made lowercase.
    earlyexit = models.TimeField(db_column='earlyExit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    fulldaytime = models.TimeField(db_column='fullDayTime', max_length=10, blank=True, null=True)  # Field name made lowercase.
    halfdaytime = models.TimeField(db_column='halfDayTime', max_length=10, blank=True, null=True)  # Field name made lowercase.
    breakstart = models.TimeField(db_column='breakStart', max_length=10, blank=True, null=True)  # Field name made lowercase.
    breakend = models.TimeField(db_column='breakEnd', max_length=10, blank=True, null=True)  # Field name made lowercase.
    status=models.CharField(db_column='status', max_length=50, blank=False, default='INSERT')
    class Meta:
        db_table = 'shifts'

class Employee_Designations(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_desg', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    emp_designations = models.ForeignKey(EmployeeDropdown,db_column='emp_designations', related_name='emp_designations', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='Time_Stamp')  # Field name made lowercase.
    inserted_by= models.ForeignKey(EmployeePrimdetail,db_column='Inserted_By',related_name='employee_id_desig', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    status=models.CharField(db_column='Status', max_length=50, blank=False, default='INSERT')

    class Meta:
        db_table = 'Employee_Designations'
        

class EmployeeCertification(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(EmployeePrimdetail,to_field="emp_id",db_column="emp_id",on_delete=models.SET_NULL,null=True,max_length=20,related_name="cert_emp")
    course_name = models.TextField()
    certified_by = models.TextField()
    mooc_type=models.ForeignKey(AarDropdown,db_column='mooc_type', related_name='mooc_type', blank=True, null=True,on_delete=models.SET_NULL)
    nptel_type=models.ForeignKey(AarDropdown,db_column='nptel_type', related_name='nptel_type', blank=True, null=True,on_delete=models.SET_NULL)  
    issue_date = models.DateField()
    link = models.TextField()
    status = models.CharField(max_length=20)
    time_stamp = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'employee_certification' 




######################################### KIET - EXTENSION ###########################################

class Extension(models.Model):
   Names=models.CharField(max_length=100)
   Designation=models.CharField(max_length=100)
   Extension=models.CharField(max_length=100)
   Mobile_No=models.CharField(max_length=100)
   Email=models.CharField(max_length=100)
   Dept=models.CharField(max_length=100)

   class Meta:
        managed = True
        db_table = 'KIET_Extensions'

##########################################################################################################

class EmployeeExperience(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_experience',max_length=20, on_delete=models.CASCADE)
    from_date = models.DateField(db_column="From_Date",default=None,blank=True, null=True)
    to_date = models.DateField(db_column="To_Date",default=None,blank=True, null=True)
    
    effective_exp_years = models.IntegerField(db_column='Experience_Years', blank=True, null=True)
    effective_exp_months = models.IntegerField(db_column='Experience_Months', blank=True, null=True)
    actual_exp_year = models.IntegerField(db_column='Actual_Exp_Years', blank=True, null=True)
    actual_exp_month = models.IntegerField(db_column='Actual_Exp_Months', blank=True, null=True)
    
    organisation = models.CharField(db_column='Organisation', max_length=50, blank=True, null=True)
    designation = models.CharField(db_column='Designation', max_length=50, blank=True, null=True)
    agp = models.IntegerField(db_column='AGP', blank=True, null=True)
    gross_salary = models.IntegerField(db_column='Gross_Salary', blank=True, null=True)
    exp_type = models.CharField(db_column='Experience_Type', max_length=50, blank=True, null=True) # RESEARCH:R / INDUSTRY:I / TEACHING:T / EXPERIENCE IN KIET:KIET
    # exp_type = models.ForeignKey(EmployeeDropdown,db_column='Experience_Type', related_name='EmployeeExperience_exp_type', blank=False, null=True,on_delete=models.SET_NULL) # RESEARCH / INDUSTRY / TEACHING / 
    
    remark = models.TextField(db_column='Remark',blank=True, null=True)
    status=models.CharField(db_column='Status', max_length=50, blank=False, default='INSERT')
    time_stamp=models.DateTimeField(db_column='time_stamp', auto_now=True)
    added_by=models.ForeignKey(EmployeePrimdetail, db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)

    class Meta:
        db_table = 'employee_experience'