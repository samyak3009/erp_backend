from __future__ import unicode_literals
from django.db import models
from grievance.models import GrievanceData
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from login.models import EmployeePrimdetail,EmployeeDropdown
from leave.models import LeaveType

class AccountsSession(models.Model):
    session=models.CharField(db_column='session',max_length=50,null=True,blank=True)
    Fdate=models.DateField(db_column='Fdate',null=True,blank=True)
    Tdate=models.DateField(db_column='Tdate',null=True,blank=True)
    current_sal_month=models.IntegerField(db_column='current_sal_month',null=True,blank=True)
    Insertby=models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', max_length=20,null=True,on_delete=models.SET_NULL)
    class Meta:
        db_table = 'Accounts_Session'
        managed = True

class AccountsDropdown(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='Pid', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=500, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=500, blank=True, null=True)  # Field name made lowercase.
    is_edit = models.IntegerField(db_column='Is_Edit',default='1')  # Field name made lowercase.
    is_delete = models.IntegerField(db_column='Is_Delete',default='1')  # Field name made lowercase.
    status=models.CharField(db_column='status',null=True,max_length=10,default="INSERT")## Formulatype, Valuebased
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL,related_name='session_AccountsSession_session')

    class Meta:
        db_table = 'Accounts_dropdown'
        managed = True

class SalaryIngredient(models.Model):

    Ingredients=models.ForeignKey(AccountsDropdown,db_column='ingredient',null=True,on_delete=models.SET_NULL) ##salary Ingredients name BASIC,HRA
    calcType=models.CharField(db_column='calcType',null=True,max_length=10)## Formulatype, Valuebased
    Formula=models.CharField(db_column='Formula',null=True,max_length=500,blank=True)## If formula based store formula ex Basic+HRA+DA
    percent=models.FloatField(db_column='percent', null=True,blank=True)## percentage of sum of all formula Ingredients
    #value=models.IntegerField(db_column='value', null=True)## if calcType is valuewise
    ingredient_nature=models.IntegerField(db_column='ingredient_nature' ,null=True) ### monthly(1), quaterly(4),half yearly(6), yearly(12) or lifetime(-1)
    next_count_month=models.DateField(db_column='next_count_month', blank=True, null=True)### date from which ingredient starts
    #applicable_on=models.CharField(db_column='applicable_on',null=True,max_length=50) #### consolidate, grade or both
    taxstatus=models.IntegerField(db_column='taxstatus',null=True) #### taxable or exempted
    added_by=models.ForeignKey(EmployeePrimdetail, db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    status=models.CharField(db_column='status',null=True,max_length=10,default="INSERT")## Formulatype, Valuebased
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)

    class Meta:
        db_table = 'Accounts_salaryingredient'
        managed = True

class ConstantDeduction(models.Model):
    DeductionName=models.ForeignKey(AccountsDropdown,db_column='DeductionName',max_length=100,null=True,on_delete=models.SET_NULL) ######## name of deduction
    deductionType=models.CharField(db_column='deductionType',null=True,max_length=100) ###### percentagewise or value
    Formula=models.CharField(db_column='Formula',null=True,max_length=100) #### If formula based store formula ex Basic+HRA+DA
    percent=models.FloatField(db_column='percent', null=True) ######### if percentagewise deductionType
    maxvalue=models.IntegerField(db_column='maxvalue', null=True) ####### max value of that deduction
    ##use above one for deduction type =value (value=models.IntegerField(db_column='value', null=True)) ######### if valuewise deductionType
    creditnature=models.IntegerField(db_column='creditnature' ,null=True) ######## monthly(1), quaterly(4),half yearly(6), yearly(12) or lifetime(-1)
    creditdate=models.DateField(db_column='credit_Date', blank=True, null=True) ########### start date of creditdate
    # applicable_on=models.CharField(db_column='applicable_on',null=True,max_length=100) ####### consolidate, grade or both
    added_by=models.ForeignKey(EmployeePrimdetail, db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    taxstatus=models.IntegerField(db_column='taxstatus',default=0) #### taxable or exempted
    status=models.CharField(db_column='status',null=True,max_length=100,default="INSERT")
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)

    class Meta:
        db_table = 'Accounts_constant_deduction'
        managed = True

class AccountsIncrementArrear(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_incrementarrear' ,on_delete=models.SET_NULL, max_length=20,null=True)
    Fdate=models.DateField(db_column='Fdate',blank=True,null=True)
    Tdate=models.DateField(db_column='Tdate',blank=True,null=True)
    arrearCredited=models.CharField(db_column='arrearCredited',default='N',null=True ,max_length=10)
    credit_month=models.IntegerField(db_column='credit_month',null=True,blank=True)
    time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)
    added_by=models.ForeignKey(EmployeePrimdetail, related_name='employee_id_incrementarrear_add',db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    working_days = models.FloatField(db_column='Working_Days', blank=True, null=True)  # Field name made lowercase.
    days = models.FloatField(db_column='Days', blank=True, null=True)  # Field name made lowercase.
    status=models.CharField(db_column='status',max_length=20,default="INSERT")
    credit_date = models.DateTimeField(db_column="credit_date",null=True,default=None)
    remark=models.CharField(db_column="remark",null=True, max_length=1000)
    
    class Meta:
        db_table = 'Accounts_IncrementArrear'
        managed = True

class AdditionalArrear(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id' ,related_name='employee_id_addarrear', max_length=20, on_delete=models.SET_NULL,null=True)
    arrear_value=models.IntegerField(db_column="arrear_value",null=True)
    remark=models.CharField(db_column="remark",null=True, max_length=1000)
    month=models.IntegerField(db_column="month",null=True)
    arrearCredited=models.CharField(db_column='arrearCredited',default='N',max_length=10,null=True)
    time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)
    status=models.CharField(max_length=10,default='INSERT')
    added_by=models.ForeignKey(EmployeePrimdetail, db_column='Added_By',related_name='employee_id_addarrear_add', null=True, blank=True,on_delete=models.SET_NULL)
    credit_date = models.DateTimeField(db_column="credit_date",null=True,default=None)
    
    class Meta:
        db_table = 'Accounts_AdditionalArrear'
        managed = True

class DAArrear(models.Model):
    Fdate=models.DateField(db_column='Fdate',blank=True,null=True)
    Tdate=models.DateField(db_column='Tdate',blank=True,null=True)
    arrearCredited=models.CharField(db_column='arrearCredited',default='N',null=True ,max_length=10)
    credit_month=models.IntegerField(db_column='credit_month',null=True,blank=True)
    time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)
    added_by=models.ForeignKey(EmployeePrimdetail, db_column='Added_By',related_name='employee_id_DAarrear',null=True, blank=True,on_delete=models.SET_NULL)
    emp_id=models.ForeignKey(EmployeePrimdetail, db_column='DAArrear_empid',related_name='DAArrear_empid',null=True, blank=True,on_delete=models.SET_NULL)
    status=models.CharField(db_column='status',max_length=20,default="INSERT")
    working_days = models.FloatField(db_column='Working_Days', blank=True, null=True)  # Field name made lowercase.
    actual_days = models.FloatField(db_column='actual_days', blank=True, null=True)  # Field name made lowercase.
    credit_date = models.DateTimeField(db_column="credit_date",null=True,default=None)
    
    class Meta:
        db_table = 'Accounts_DAArrear'
        managed = True

class EmployeeDeductions(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id',related_name='employee_id_deduction', max_length=20,null=True,on_delete=models.SET_NULL)
    variableDeduction=models.ForeignKey(AccountsDropdown,db_column='varD',null=True,on_delete=models.SET_NULL)
    status=models.CharField(db_column="status",default="INSERT", max_length=50)
    constantDeduction=models.ForeignKey(ConstantDeduction,db_column='constD',null=True,on_delete=models.SET_NULL)
    #approvedBy= models.ForeignKey(EmployeePrimdetail,db_column='approvedby', max_length=20,null=True)
    added_by=models.ForeignKey(EmployeePrimdetail,related_name='employee_id_deduction_add', db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)

    class Meta:
        db_table = 'Accounts_EmployeeDeductions'
        managed = True


class AccountsElementApplicableOn(models.Model):
    salary_ingredient=models.ForeignKey(SalaryIngredient,db_column='salary_ingredient',null=True,on_delete=models.SET_NULL)
    constantDeduction=models.ForeignKey(ConstantDeduction,db_column='constD',null=True,on_delete=models.SET_NULL)
    salary_type=models.ForeignKey(AccountsDropdown,db_column='salary_type',null=True,on_delete=models.SET_NULL)

    class Meta:
        db_table = 'Accounts_ElementApplicableOn'
        managed = True


class MonthlyDeductionValue(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,related_name='employee_id_deductionvalue',db_column='Emp_Id',on_delete=models.SET_NULL, max_length=20,null=True)
    deduction_id=models.ForeignKey(EmployeeDeductions,db_column='deductionID',null=True,on_delete=models.SET_NULL)
    value=models.IntegerField(db_column="value",default=0,null=True)
    month=models.IntegerField(db_column="month",null=True)
    session=models.ForeignKey(AccountsSession,db_column='session',on_delete=models.SET_NULL,null=True)
    added_by=models.ForeignKey(EmployeePrimdetail, db_column='Added_By',on_delete=models.SET_NULL,related_name='employee_id_deductionvalue_add', null=True, blank=True)

    class Meta:
        db_table = 'Accounts_MonthlyDeductionValue'
        managed = True

class EmployeeVariableDeduction(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,related_name='employee_id_v_deductionvalue',db_column='Emp_Id', max_length=20,null=True,on_delete=models.SET_NULL)
    deduction_id=models.ForeignKey(EmployeeDeductions,db_column='deductionID',null=True,on_delete=models.SET_NULL)
    value=models.IntegerField(db_column="value",default=0,null=True)
    month=models.IntegerField(db_column="month",null=True)
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)
    added_by=models.ForeignKey(EmployeePrimdetail, db_column='Added_By',related_name='employee_id_v_deductionvalue_add',on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'Accounts_EmployeeVariableDeduction'
        managed = True

class EmployeeGross_detail(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id',related_name='employee_grossdetail', max_length=20,null=True,on_delete=models.SET_NULL)
    Ing_Id = models.ForeignKey(SalaryIngredient, db_column='Ingredient_Id', max_length=20, on_delete=models.SET_NULL,null=True)
    Value = models.FloatField(db_column='Value', null=True, blank=True,default=0.0)
    Status = models.CharField(db_column='Status', max_length=30, null=True, blank=True,default="INSERT")
    added_by=models.ForeignKey(EmployeePrimdetail, db_column='Added_By',related_name='employee_grossdetail_add', null=True, blank=True,on_delete=models.SET_NULL)
    pay_by=models.ForeignKey(AccountsDropdown,db_column='pay_by',null=True,on_delete=models.SET_NULL)
    salary_type=models.ForeignKey(AccountsDropdown,db_column='salary_type',related_name="salary_type",null=True,on_delete=models.SET_NULL)
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,blank=True,on_delete=models.SET_NULL)

    class Meta:
        db_table = 'Accounts_GrossDetails'
        managed = True


class MonthlyPayable_detail(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', max_length=20, related_name='employee_monthlypayable' ,null=True,on_delete=models.SET_NULL)
    Ing_Id = models.ForeignKey(SalaryIngredient, db_column='Gross_Id', max_length=20, on_delete=models.SET_NULL,null=True)
    payable_value = models.FloatField(db_column='payable_value', max_length=20, null=True, blank=True)
    gross_value = models.FloatField(db_column='gross_value', max_length=20, null=True, blank=True)
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,blank=True,on_delete=models.SET_NULL)
    Month = models.IntegerField(db_column='Month', null=True, blank=True)

    class Meta:
        db_table = 'Accounts_PayableDetails'
        managed = True

class MonthlyArrear_detail(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', max_length=20,related_name='employee_arreardetail',null=True,on_delete=models.SET_NULL)
    arrear_type = models.CharField(db_column='arrear_type',max_length=10,null=True,default=None)
    ######### arrear_type="A" (additional arrear) , arrear_type="S" (sign in/out arrear) , arrear_Type="L" (leave arrear) , arrear_type="DA" (DA arrear) , arrear_type="I" (increment arrear)
    Ing_Id = models.ForeignKey(SalaryIngredient, db_column='Ing_Id', max_length=20, on_delete=models.SET_NULL,null=True)
    ########## ing_id=null for additional arrear ################
    value = models.FloatField(db_column='Value', null=True, blank=True)
    session =  models.ForeignKey(AccountsSession,db_column='Session', max_length=30, null=True, blank=True,on_delete=models.SET_NULL)
    Month = models.IntegerField(db_column='Month', null=True, blank=True)

    class Meta:
        db_table = 'Accounts_MonthlyArrearDetails'
        managed = True

class Employee_Declaration(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_declarations',null=True,on_delete=models.SET_NULL)
    Dec_Id = models.ForeignKey(AccountsDropdown, db_column='Dec_Id', max_length=20, on_delete=models.SET_NULL,null=True)
    Session_Id = models.ForeignKey(AccountsSession, db_column='Session_Id', max_length=20, on_delete=models.SET_NULL,null=True)
    Value = models.IntegerField(db_column='Value', null=True ,blank=True)
    status = models.CharField(db_column="status",max_length=10,default="INSERT")
    Verified = models.CharField(db_column='Verified' ,max_length=20, null=True, default='N')
    Verified_By = models.ForeignKey(EmployeePrimdetail,db_column='verifyby', max_length=20, on_delete=models.SET_NULL,null=True)
    time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)

    class Meta:
        db_table = 'Accounts_EmployeeDeclaration'
        managed = True


class LockingUnlocking(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', max_length=20,related_name='LockingUnlocking',null=True,on_delete=models.SET_NULL)
    fromDate = models.DateTimeField(db_column="fromDate")
    toDate = models.DateTimeField(db_column="toDate")
    status = models.CharField(db_column="status",default="INSERT",max_length=20)
    time_stamp = models.DateTimeField(db_column="time_stamp",auto_now=True)
    unlocked_by = models.ForeignKey(EmployeePrimdetail,db_column='unlocked_by', max_length=20, on_delete=models.SET_NULL,null=True)

    class Meta:
        db_table = 'Accounts_lockingunlocking'
        managed = True


class Sign_In_Out_Arrear(models.Model):
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', max_length=20,related_name='sign_in_out_emp_id',null=True,on_delete=models.SET_NULL)
    date=models.DateField(db_column="date")
    count=models.FloatField(db_column="count")
    actual_days=models.IntegerField(db_column="actual_days")
    credit_month=models.IntegerField(db_column='credit_month',null=True,blank=True)
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)
    status=models.IntegerField(db_column="status",default=0)
    credited=models.CharField(db_column="credited",default='N',max_length=2)
    time_stamp = models.DateTimeField(db_column="time_stamp",auto_now=True)
    added_by = models.ForeignKey(EmployeePrimdetail,db_column='added_by', max_length=20, on_delete=models.SET_NULL,null=True)
    hr_remark = models.CharField(db_column='HrRemark', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    credit_date = models.DateTimeField(db_column="credit_date",null=True,default=None)
    
    class Meta:
        db_table = 'Accounts_Sign_In_Out_Arrear'
        managed = True


class Days_Arrear_Leaves(models.Model):
    leaveid = models.AutoField(db_column='LeaveID', primary_key=True)  # Field name made lowercase.
    requestdate = models.DateField(db_column='RequestDate', blank=True, null=True)  # Field name made lowercase.
    leavecode = models.ForeignKey(LeaveType,db_column='leavecode', related_name='arrear_leave_code', max_length=20, on_delete=models.SET_NULL,null=True, blank=True)  # Field name made lowercase.
    subtype = models.ForeignKey(EmployeeDropdown,db_column='SubType',on_delete=models.SET_NULL ,related_name='arrear_leave_subtype' ,blank=True, null=True)  # Field name made lowercase.
    category =models.ForeignKey(EmployeeDropdown,db_column='Category',on_delete=models.SET_NULL,related_name='arrear_leave_category', blank=True, null=True)  # Field name made lowercase.
    fromdate = models.DateField(db_column='FromDate', blank=True, null=True)  # Field name made lowercase.
    todate = models.DateField(db_column='ToDate', blank=True, null=True)  # Field name made lowercase.
    days = models.FloatField(db_column='Days', blank=True, null=True)  # Field name made lowercase.
    working_days = models.FloatField(db_column='Working_Days', blank=True, null=True)  # Field name made lowercase.

    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='arrear_Employee_id', max_length=20, on_delete=models.SET_NULL,null=True, blank=True)
    fhalf = models.CharField(db_column='Fhalf', max_length=45, blank=True, null=True)  # Field name made lowercase.
    thalf = models.CharField(db_column='Thalf', max_length=45, blank=True, null=True)  # Field name made lowercase.
    filename = models.CharField(db_column='FileName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    extrahours = models.TimeField(db_column='ExtraHours', blank=True, null=True)  # Field name made lowercase.
    extraworkdate = models.CharField(db_column='ExtraWorkDate', max_length=100, blank=True, null=True)  # Field name made lowercase.
    hr_status = models.CharField(db_column='HrStatus', max_length=45, blank=True, null=True)  # Field name made lowercase.
    hr_remark = models.CharField(db_column='HrRemark', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    #acc_status = models.CharField(db_column='AccStatus', max_length=45, blank=True, null=True)  # Field name made lowercase.
    #acc_remark = models.CharField(db_column='AccRemark', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    session=models.ForeignKey(AccountsSession,db_column='session',null=True,on_delete=models.SET_NULL)
    month=models.IntegerField(default=4)
    arrearCredited=models.CharField(db_column='arrearCredited',default='N',null=True ,max_length=10)
    finalapprovaldate = models.DateField(db_column='FinalApprovalDate', blank=True, null=True)  # Field name made lowercase.
    credit_date = models.DateTimeField(db_column="credit_date",null=True,default=None)
    
    class Meta:
        managed = True
        db_table = 'Accounts_Days_Arrear_Leaves'

class Income_Tax_Range(models.Model):

    session=models.ForeignKey(AccountsSession,db_column='session',related_name="income_tax_session",null=True,blank=True,on_delete=models.SET_NULL)
    from_value=models.FloatField(db_column="from_value",null=True)
    to_value=models.FloatField(db_column="to_value",null=True)
    from_age=models.IntegerField(db_column="from_age",null=True)
    to_age=models.IntegerField(db_column="to_age",null=True)
    percent=models.FloatField(db_column="Percent",null=True)
    time_stamp=models.DateTimeField(db_column="time_stamp",auto_now=True)
    added_by=models.ForeignKey(EmployeePrimdetail,db_column="added_by",related_name="income_tax_added_by",null=True,on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'Accounts_Income_Tax_Range'

class Income_Tax_Paid(models.Model):

    session=models.ForeignKey(AccountsSession,db_column='session',related_name="tax_paid_session",null=True,blank=True,on_delete=models.SET_NULL)
    month=models.IntegerField(db_column="month",null=True)
    income_tax_sum=models.FloatField(db_column="income_tax_sum",null=True)
    hra_exemption=models.FloatField(db_column="hra_exemption",null=True)
    rebate=models.FloatField(db_column="rebate",null=True)
    cess=models.FloatField(db_column="cess",null=True)
    monthly_tax_paid=models.FloatField(db_column="monthly_tax_paid",null=True)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column="emp_id",related_name="tax_paid_emp",null=True,on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'Accounts_Income_Tax_Paid'


class EmployeePayableDays(models.Model):
    session=models.ForeignKey(AccountsSession,db_column='session',related_name="payable_session",null=True,blank=True,on_delete=models.SET_NULL)
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='payable_Employee_id', max_length=20, on_delete=models.SET_NULL,null=True, blank=True)
    dept = models.ForeignKey(EmployeeDropdown,db_column='dept',on_delete=models.SET_NULL ,related_name='payable_daysdept', null=True)
    desg = models.ForeignKey(EmployeeDropdown,db_column='desg',on_delete=models.SET_NULL ,related_name='payable_days_desg', null=True)
    emp_category = models.ForeignKey(EmployeeDropdown,db_column='emp_category',on_delete=models.SET_NULL ,related_name='payable_days_emp_category', null=True)
    title = models.ForeignKey(EmployeeDropdown,db_column='title',on_delete=models.SET_NULL ,related_name='payable_days_title', null=True)
    bank_acc_no = models.CharField(max_length=500,null=True,default=None)
    uan_no = models.CharField(max_length=500,null=True,default=None)
    pan_no = models.CharField(max_length=500,null=True,default=None)
    month=models.IntegerField(db_column="month",null=True)
    total_days=models.FloatField(db_column="total_days",null=True)
    working_days=models.FloatField(db_column="working_days",null=True)
    leave=models.FloatField(db_column="leave",null=True)
    holidays=models.FloatField(db_column="holidays",null=True)
    time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    added_by=models.ForeignKey(EmployeePrimdetail,db_column='added_by',related_name='payable_days_emp_by',null=True,on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'Accounts_EmployeePayableDays'

class DaysGenerateLog(models.Model):
    sessionid=models.ForeignKey(AccountsSession,db_column='session',related_name="day_lock_session",null=True,blank=True,on_delete=models.SET_NULL)
    date=models.DateField(db_column='lock_date',null=True,blank=True)
    month=models.IntegerField(db_column='month',null=True,blank=True)
    year=models.IntegerField(db_column='year',null=True,blank=True)
    salarySheet=models.CharField(db_column='salarySheet',max_length=200,null=True,blank=True)
    tdsSheet=models.CharField(db_column='TDSSheet',max_length=200,null=True,blank=True)
    acc_sal_lock=models.CharField(db_column='AccSalLock',max_length=200,null=True,blank=True,default="N")

    class Meta:
        managed = True
        db_table = 'Accounts_lockDaysLock'
