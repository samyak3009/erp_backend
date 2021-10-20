from __future__ import unicode_literals

from django.db import models
from login.models import EmployeeDropdown,EmployeePrimdetail
from musterroll.models import EmployeeSeparation
# Create your models here.

###########HOLIDAY############

class Holiday(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    h_type = models.IntegerField(db_column='H_type', blank=True, null=True)  # Field name made lowercase.
    h_des = models.CharField(db_column='H_Des', max_length=500, blank=True, null=True)  # Field name made lowercase.
    dept = models.ForeignKey(EmployeeDropdown,db_column='Dept', related_name='Department_holiday', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    f_date = models.DateField(db_column='F_date', blank=True, null=True)  # Field name made lowercase.
    t_date = models.DateField(db_column='T_date', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=500, blank=True, null=True)  # Field name made lowercase.
    restricted = models.CharField(db_column='Restricted', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'holiday'
        managed = False


class LeaveType(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    leave_name = models.CharField(db_column='Leave_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    leave_abbr = models.CharField(db_column='Leave_Abbr', max_length=10, blank=True, null=True)  # Field name made lowercase.
    leave_status = models.CharField(db_column='Leave_Status', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lapse_start = models.DateField(db_column='Lapse_Start', blank=True, null=True)  # Field name made lowercase.
    lapse_month = models.IntegerField(db_column='Lapse_Month', blank=True, null=True)  # Field name made lowercase.
    accumulate_max = models.IntegerField(db_column='Accumulate_Max', blank=True, null=True)  # Field name made lowercase.
    hours_leave = models.CharField(db_column='Hours_Leave', max_length=10, blank=True, null=True)  # Field name made lowercase.
    hours = models.TimeField(db_column='Hours', blank=True, null=True)  # Field name made lowercase.
    credit_day = models.DateField(db_column='Credit_Day', blank=True, null=True)  # Field name made lowercase.
    credittype = models.CharField(db_column='CreditType', max_length=50,null=True)  # Field name made lowercase.
    leaveforgender = models.CharField(db_column='LeaveForGender', max_length=50,null=True)  # Field name made lowercase.
    apply_days = models.IntegerField(db_column='Apply_Days', blank=True, null=True)  # Field name made lowercase.
    inserted_by = models.CharField(db_column='Inserted_By', max_length=20, blank=True, null=True)  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='Time_Stamp')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=10, blank=True, null=True) # Field name made lowercase.
    leaveCountStatus = models.CharField(db_column='leaveCountStatus', max_length=50, null=True)
    NormalLeave = models.CharField(db_column='NormalLeave', max_length=50, null=True,default='YES')

    class Meta:
        db_table = 'leave_type'

class OdCategoryUpload(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    category = models.ForeignKey(EmployeeDropdown,db_column='Category', related_name='od_category', blank=True, null=True,on_delete=models.SET_NULL)
    num_of_days = models.IntegerField(db_column='Num_Of_Days', blank=True, null=False,default=0)  # Field name made lowercase.
    sub_category = models.ForeignKey(EmployeeDropdown,db_column='Sub_Category', related_name='sub_category', blank=True, null=True,on_delete=models.SET_NULL)
    LeaveId = models.ForeignKey(LeaveType,db_column='LeaveId', related_name='uploadleaveid', blank=True, null=True,on_delete=models.SET_NULL)
    is_compoff = models.IntegerField(db_column='Is_CompOff',default='0')
    is_upload = models.IntegerField(db_column='Is_Upload',default='0')

    class Meta:
        db_table = 'od_category_upload'


class Leaves(models.Model):
    leaveid = models.AutoField(db_column='LeaveID', primary_key=True)  # Field name made lowercase.
    requestdate = models.DateField(db_column='RequestDate', blank=True, null=True)  # Field name made lowercase.
    leavecode = models.ForeignKey(LeaveType,db_column='leavecode', related_name='leave_code', max_length=20, on_delete=models.SET_NULL,null=True, blank=True)  # Field name made lowercase.
    subtype = models.ForeignKey(EmployeeDropdown,db_column='SubType',on_delete=models.SET_NULL ,related_name='leave_subtype' ,blank=True, null=True)  # Field name made lowercase.
    category =models.ForeignKey(EmployeeDropdown,db_column='Category',on_delete=models.SET_NULL,related_name='leave_category', blank=True, null=True)  # Field name made lowercase.
    fromdate = models.DateTimeField(db_column='FromDate', blank=True, null=True)  # Field name made lowercase.
    todate = models.DateTimeField(db_column='ToDate', blank=True, null=True)  # Field name made lowercase.
    days = models.FloatField(db_column='Days', blank=True, null=True)  # Field name made lowercase.
    reason = models.CharField(db_column='Reason', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='Employee_id', max_length=20, on_delete=models.SET_NULL,null=True, blank=True)
    fhalf = models.CharField(db_column='Fhalf', max_length=45, blank=True, null=True)  # Field name made lowercase.
    thalf = models.CharField(db_column='Thalf', max_length=45, blank=True, null=True)  # Field name made lowercase.
    filename = models.CharField(db_column='FileName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    #registered = models.CharField(db_column='Registered', max_length=10)  # Field name made lowercase.
    extrahours = models.TimeField(db_column='ExtraHours', blank=True, null=True)  # Field name made lowercase.
    extraworkdate = models.CharField(db_column='ExtraWorkDate', max_length=100, blank=True, null=True)  # Field name made lowercase.
    #cancelrequest = models.CharField(db_column='CancelRequest', max_length=20, blank=True, null=True)  # Field name made lowercase.
    finalstatus = models.CharField(db_column='FinalStatus', max_length=45, blank=True, null=True)  # Field name made lowercase.
    finalapprovaldate = models.DateField(db_column='FinalApprovalDate', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        db_table = 'leaves'

################################## LEAVE SANDWICH ######################################

class LeaveSandwich(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    leave_id1 = models.ForeignKey(LeaveType,db_column='Leave_Id1', related_name='leave_id_1', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    leave_id2 = models.ForeignKey(LeaveType,db_column='Leave_Id2', related_name='leave_id_2', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    inserted_by = models.CharField(db_column='Inserted_By', max_length=50, blank=True, null=True)  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='Time_Stamp')  # Field name made lowercase.

    class Meta:
        db_table = 'leave_sandwich'



#############################LEAVES APPROVAL#########################################
class Leaveapproval(models.Model):

    approved_by = models.CharField(db_column='Approved_by', max_length=150, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=100, blank=True, null=True,default='PENDING')  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=100, blank=True, null=True,default='PENDING')  # Field name made lowercase.
    approvaldate = models.DateTimeField(db_column='ApprovalDate', blank=True, null=True)  # Field name made lowercase.
    reportinglevel = models.IntegerField(db_column='ReportingLevel', blank=True, null=True)  # Field name made lowercase.
    leaveid = models.ForeignKey(Leaves,db_column='LeaveID',on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    dept = models.ForeignKey(EmployeeDropdown, db_column='Dept', related_name='leave_dept',blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    desg = models.ForeignKey(EmployeeDropdown, db_column='Desg', related_name='leave_desg',blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.

    class Meta:

        db_table = 'LeaveApproval'


class LeaveClub(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    leave_id1 = models.ForeignKey(LeaveType, db_column='Leave_Id1',related_name='Leave_Type1', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    day_count1 = models.CharField(db_column='Day_Count1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    leave_id2 = models.ForeignKey(LeaveType,db_column='Leave_Id2', related_name='Leave_Type2', max_length=20, on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
    day_count2 = models.CharField(db_column='Day_Count2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    inserted_by = models.ForeignKey(EmployeePrimdetail,db_column='Inserted_By', related_name='Employee_id_club', max_length=20, on_delete=models.SET_NULL, blank=True, null=True)  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='Time_Stamp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'leave_club'





class LeaveQuota(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    no_of_leaves = models.FloatField(db_column='No_Of_Leaves', blank=True, null=True)  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='Time_stamp', blank=True, null=True)  # Field name made lowercase.
    category_emp = models.ForeignKey(EmployeeDropdown,db_column='Category_Emp',related_name='EmpCategory', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    designation = models.ForeignKey(EmployeeDropdown,db_column='designation',related_name='EmpDesg', blank=True, null=True,on_delete=models.SET_NULL)
    inserted_by = models.ForeignKey(EmployeePrimdetail,db_column='Inserted_By',related_name='Employee_id_quota', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    leave_id = models.ForeignKey(LeaveType,db_column='Leave_Id',related_name='Leave_Type_quota', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    type_of_emp = models.ForeignKey(EmployeeDropdown,db_column='Type_of_Emp',related_name='TypeOfEmployee', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=False, default='INSERT')
    class Meta:

        db_table = 'leave_quota'



class Leaveremaning(models.Model):
    id = models.AutoField(db_column='Id',primary_key=True)  # Field name made lowercase.
    empid = models.ForeignKey(EmployeePrimdetail,db_column='EmpId', related_name='Emp_id_rem', max_length=20, on_delete=models.SET_NULL,null=True, blank=True)  # Field name made lowercase.
    leaveid = models.ForeignKey(LeaveType,db_column='LeaveId',related_name='Leave_Remaining_quota', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    remaining = models.FloatField(db_column='Remaining')  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)

    class Meta:

        db_table = 'leaveremaining'

class LeaveCreditLog(models.Model):
    id = models.AutoField(db_column='Id',primary_key=True)
    no_of_leaves = models.FloatField(db_column='No_Of_Leaves', blank=True, null=True)  # Field name made lowercase.
    creditdate = models.DateTimeField(db_column='creditDate', blank=True, null=True)  # Field name made lowercase.
    category_emp = models.ForeignKey(EmployeeDropdown,db_column='Category_Emp',related_name='EmpCat', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    designation = models.ForeignKey(EmployeeDropdown,db_column='designation',related_name='EmpDesgnation', blank=True, null=True,on_delete=models.SET_NULL)
    leave_id = models.ForeignKey(LeaveType,db_column='Leave_Id',related_name='Leave_Type_qota', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.
    type_of_emp = models.ForeignKey(EmployeeDropdown,db_column='Type_of_Emp',related_name='TypeOfEmp', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.

    class Meta:
        db_table='LeaveCreditLog'

class LeaveLapseLog(models.Model):
	id = models.AutoField(db_column='Id',primary_key=True)
	lapsedate = models.DateTimeField(db_column='lapseDate', blank=True, null=True)  # Field name made lowercase.
	leave_id = models.ForeignKey(LeaveType,db_column='Leave_Id',related_name='Leave_Typ', blank=True, null=True,on_delete=models.SET_NULL)  # Field name made lowercase.

	class Meta:
		db_table='LeaveLapseLog'
