# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from Registrar.models import StudentPrimDetail,StudentDropdown,Semtiming,StudentBankDetails
from Accounts.models import AccountsDropdown
from login.models import EmployeePrimdetail
from StudentHostel.models import HostelSettings,HostelDropdown

# Create your models here.
class StudentAccountsDropdown(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='Pid', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=500, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=500, blank=True, null=True)  # Field name made lowercase.
    is_edit = models.IntegerField(db_column='Is_Edit',default='1')  # Field name made lowercase.
    is_delete = models.IntegerField(db_column='Is_Delete',default='1')  # Field name made lowercase.
    status=models.CharField(db_column='status',null=True,max_length=10,default="INSERT")## Formulatype, Valuebased

    class Meta:
        db_table = 'StuAccDropdown'
        managed = True


class StuAccFeeSettings(models.Model):
    course_id= models.ForeignKey(StudentDropdown,related_name='FeeSettingsCourse_id',db_column='Course_id',null=True,on_delete=models.SET_NULL)  
    gender= models.ForeignKey(StudentDropdown,related_name='FeeSettingsGender',db_column='Gender',null=True,on_delete=models.SET_NULL)  
    join_year=models.IntegerField(db_column='Join_Year',default=2010)
    admission_status= models.ForeignKey(StudentDropdown,related_name='FeeSettingsAdmissionStatus',db_column='admission_status',null=True,on_delete=models.SET_NULL)  
    caste= models.ForeignKey(StudentDropdown,related_name='FeeSettingsCaste',db_column='caste',null=True,on_delete=models.SET_NULL)  
    fee_waiver=models.CharField(db_column="Fee_Waiver",null=True,max_length=5,blank=True,default="N")
    fee_component_cat=models.ForeignKey(StudentAccountsDropdown,related_name='FeeSettingsComponentCat',db_column='FeeComponentCat',null=True,on_delete=models.SET_NULL) ### tution fee,registration etc.
    value=models.IntegerField(db_column="value",default=0)
    fee_component = models.ForeignKey(StudentAccountsDropdown,related_name='FeeSettingsComponent',db_column='FeeComponent',null=True,on_delete=models.SET_NULL) ### academic,hostel,security etc. 
    session=models.ForeignKey(Semtiming,related_name='FeeSettingsSession',db_column='session',null=True,on_delete=models.SET_NULL)
    status=models.CharField(db_column="status",default="INSERT",max_length=10)
    added_by=models.ForeignKey(EmployeePrimdetail,related_name="fee_sett_emp", db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    time_stamp=models.DateTimeField(auto_now=True)
    hostel_id=models.ForeignKey(HostelSettings,related_name="room_hostel1",db_column="hostel_id",null=True,on_delete=models.SET_NULL,default=None)
    seater_type=models.ForeignKey(HostelDropdown,related_name="seater_type1",db_column="seater_type",null=True,on_delete=models.SET_NULL,default=None)
    
    class Meta:
        db_table = 'StuAccFeeSettings'
        managed = True

class PenaltySettings(models.Model):
    penalty=models.ForeignKey(StudentAccountsDropdown,related_name='PenaltyFee',db_column='penalty',null=True,on_delete=models.SET_NULL)
    value=models.IntegerField(db_column="value",default=0)
    session=models.CharField(db_column='session',null=True,default=None,max_length=50)
    status=models.CharField(db_column="status",default="INSERT",max_length=10)
    added_by=models.ForeignKey(EmployeePrimdetail,related_name="penalty_emp", db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    time_stamp=models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'StuAccPenaltyFee'
        managed = True

# class FeeInitialSettings(models.Model):
#     fee_initial=models.ForeignKey(StudentAccountsDropdown,related_name='fee_initial',db_column='fee_initial',null=True)
#     fee_component = models.ForeignKey(StudentAccountsDropdown,related_name='FeeSettingComponent',db_column='FeeComponent',null=True,on_delete=models.SET_NULL)
#     status=models.CharField(db_column="status",default="INSERT",max_length=10)
#     added_by=models.ForeignKey(EmployeePrimdetail,related_name="fee_initial_emp", db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
#     time_stamp=models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'StuAccFeeInitial'
#         managed = True
    

class SubmitFee(models.Model):
    uniq_id=models.ForeignKey(StudentPrimDetail,related_name='submit_fee_uniq',db_column='Uniq_Id',null=True,on_delete=models.SET_NULL)
    session=models.ForeignKey(Semtiming,related_name='SubmitFeeSession',db_column='session',null=True,on_delete=models.SET_NULL)
    fee_rec_no=models.CharField(max_length=100,null=True,default=None)
    prev_fee_rec_no=models.CharField(max_length=100,null=True,default=None)
    cancelled_status=models.CharField(max_length=10,default="N")
    actual_fee=models.FloatField(null=True,default=None)
    paid_fee=models.FloatField(null=True,default=None)
    refund_value=models.FloatField(db_column="refund_value",null=True,default=None)
    due_value=models.FloatField(db_column="due_value",null=True,default=None)
    receipt_type=models.CharField(db_column="receipt_type",max_length=5,default="N") ####### 'N' for normal , 'D' for due
    status=models.CharField(db_column="status",max_length=20,default="INSERT") ######## change in case of fee update
    added_by=models.ForeignKey(EmployeePrimdetail,related_name="submit_emp", db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    due_date=models.DateField(null=True,default=None)
    time_stamp=models.DateTimeField(auto_now=True)
    seater_type=models.ForeignKey(HostelDropdown,related_name="seater_type2",db_column="seater_type",null=True,on_delete=models.SET_NULL,default=None)
    class Meta:
        db_table = 'StuAccSubmitFee'
        managed = True

class SubmitFeeComponentDetails(models.Model):
    fee_id=models.ForeignKey(SubmitFee,related_name="fee_id_submit",db_column="fee_id",default=None,null=True,on_delete=models.SET_NULL)
    fee_component=models.ForeignKey(StudentAccountsDropdown,related_name="submit_fee_comp",db_column="fee_component",null=True,on_delete=models.SET_NULL)
    fee_sub_component=models.ForeignKey(StudentAccountsDropdown,related_name="submit_fee_sub_comp",db_column="fee_sub_component",null=True,on_delete=models.SET_NULL) ####### normal or due
    sub_component_value=models.FloatField()

    class Meta:
        db_table = 'StuAccSubmitFeeComDetails'
        managed = True

class ModeOfPaymentDetails(models.Model):
    fee_id=models.ForeignKey(SubmitFee,db_column="fee_id",related_name="mop_fee_id",default=None,null=True,on_delete=models.SET_NULL)
    MOPcomponent=models.ForeignKey(StudentAccountsDropdown,related_name="mop_comp",db_column="MOPcomponent",default=None,null=True,on_delete=models.SET_NULL)
    value=models.CharField(max_length=1000,default=None,null=True)

    class Meta:
        db_table = 'StuAccModeOfPayment'
        managed = True

class RefundFee(models.Model):
    refund_type=models.CharField(db_column="refund_type",null=True,max_length=5,default=None) ############ 'E' for excess fee paid, 'S' for security, 'W' for withdrawal
    amount=models.FloatField()
    remark=models.CharField(db_column="remark",max_length=1000,null=True,default=None)
    fee_id=models.ForeignKey(SubmitFee,related_name="refund_fee_id",db_column="fee_id",default=None,null=True,on_delete=models.SET_NULL)
    added_by=models.ForeignKey(EmployeePrimdetail,related_name="refund_emp", db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    bank_details_id=models.ForeignKey(StudentBankDetails,null=True,default=None,on_delete=models.SET_NULL)
    time_stamp=models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'StuAccRefundFee'
        managed = True

# class RefundFeeBank(models.Model):
#     refund_id=models.ForeignKey(RefundFee,null=True,default=None,on_delete=models.SET_NULL)
#     acc_name=models.CharField(max_length=1000,null=True,default=None)
#     acc_num=models.CharField(max_length=1000,null=True,default=None)
#     bank_name=models.CharField(max_length=1000,null=True,default=None)
#     ifsc_code=models.CharField(max_length=1000,null=True,default=None)
#     branch=models.CharField(max_length=1000,null=True,default=None)
#     address=models.CharField(max_length=1000,null=True,default=None)
    
#     class Meta:
#         db_table = 'StuAccRefundFeeBank'
#         managed = True
    
class DueDateLog(models.Model):
    fee_id=models.ForeignKey(SubmitFee,related_name="due_fee_id",db_column="fee_id",default=None,null=True,on_delete=models.SET_NULL)
    due_date = models.DateField(db_column='due_date', blank=True, null=True) 
    added_by=models.ForeignKey(EmployeePrimdetail,related_name="due_emp", db_column='Added_By', null=True, blank=True,on_delete=models.SET_NULL)
    time_stamp=models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'StuAccDueDateLog'
        managed = True