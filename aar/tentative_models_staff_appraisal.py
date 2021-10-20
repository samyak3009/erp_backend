# ################################################################ INCREAMENT SETTINGS ################################################################
# #TABLE 1: BASIC DETAILS FOR THE INCREAMENT SETTINGS
# class StaffAppraisalIncrementSettings(models.Model):
#     salary_type = models.ForeignKey(AccountsDropdown, db_column='salary_type', related_name="StaffAppraisalIncrementSettings_AccountsDropdown_salary_type", null=True, on_delete=models.SET_NULL) # GRADE AND CONSOLIDATED
#     increment_type = models.CharField(db_column='increment_type', max_length=50, blank=True) 
#     # NO INCREMENT, NORMAL, SPECIAL, PROMOTION WITH NORMAL INCREAMENT, PROMOTION WITH SPECIAL INCREAMENT, PROMOTION WITHOUT INCREAMENT
#     value_type = models.CharField(db_column='value_type', max_length=50, blank=True) # PERCENTAGE OR AMOUNT
#     value = models.FloatField() # PERCENTAGE OR AMOUNT
#     edit_by = models.ForeignKey(EmployeePrimdetail, related_name='StaffAppraisalIncrementSettings_EmployeePrimdetail_edit_by', db_column='edit_by', null=True, on_delete=models.SET_NULL)
#     session=models.ForeignKey(AccountsSession,related_name='StaffAppraisalIncrementSettings_Semtiming',db_column='session',null=True,on_delete=models.SET_NULL,default=1)
#     status = models.CharField(db_column='Status', max_length=50, blank=True, default='INSERT')
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)

#     class Meta:
#         managed = True
#         db_table = 'StaffAppraisal_IncrementSettings'

# #TABLE 2: INCREAMENT SETTINGS APPLICABLE ON TYPE OF EMPLOYEES
# class StaffAppraisalIncrementApplicable(models.Model):
#     increment_setting = models.ForeignKey(StaffAppraisalIncrementSettings, db_column='increment_setting', related_name="StaffAppraisalIncrementApplicable_StaffAppraisalIncrementSettings_increment_setting", null=True, on_delete=models.SET_NULL) # GRADE AND CONSOLIDATED
#     emp_category = models.ForeignKey(EmployeeDropdown, related_name="StaffAppraisalIncrementApplicable_EmployeeDropdown_emp_category", blank=True, null=True, db_column='emp_category', on_delete=models.SET_NULL) 
#     desg = models.ForeignKey(EmployeeDropdown, related_name='StaffAppraisalIncrementApplicable_EmployeeDropdown_desg', db_column='desg', blank=True, null=True, on_delete=models.SET_NULL) 
#     cadre = models.ForeignKey(EmployeeDropdown, related_name='StaffAppraisalIncrementApplicable_EmployeeDropdown_cadre', db_column='cadre', blank=True, null=True, on_delete=models.SET_NULL) 
#     ladder = models.ForeignKey(EmployeeDropdown, related_name='StaffAppraisalIncrementApplicable_EmployeeDropdown_ladder', db_column='ladder', blank=True, null=True, on_delete=models.SET_NULL) 

#     class Meta:
#         managed = True
#         db_table = 'StaffAppraisal_IncrementApplicable'

# #TABLE 3: INCREAMENT SETTINGS APPLICABLE ON COMPONENT OF INCOME
# class StaffAppraisalIncrementComponents(models.Model):
#     increment_setting = models.ForeignKey(StaffAppraisalIncrementSettings, db_column='increment_setting', related_name="StaffAppraisalIncrementComponents_StaffAppraisalIncrementSettings_increment_setting", null=True, on_delete=models.SET_NULL) # GRADE AND CONSOLIDATED
#     increment_component = models.ForeignKey(AccountsDropdown, db_column='increment_component', related_name="StaffAppraisalIncrementComponents_AccountsDropdown_increment_component", null=True, on_delete=models.SET_NULL) # GRADE AND CONSOLIDATED

#     class Meta:
#         managed = True
#         db_table = 'StaffAppraisal_IncrementComponents'
# ############################# END ############################## INCREAMENT SETTINGS ################################################################


################################################################ LOCKING AND UNLOCKING ################################################################
class StaffAppraisalLockingUnlocking(models.Model):
    lock_type=models.CharField(default='INC',max_length=5) #INC: INCREAMENT
    att_date_from=models.DateField(default=None,null=True)
    att_date_to=models.DateField(default=None,null=True)
    unlock_from=models.DateTimeField(default=None,null=True)
    unlock_to=models.DateTimeField(default=None,null=True)
    status = models.CharField(db_column="status", default="INSERT", max_length=20)
    unlocked_by = models.ForeignKey(EmployeePrimdetail, db_column='unlocked_by', max_length=20, related_name= 'unlocked_by', on_delete=models.SET_NULL, null=True)
    session=models.ForeignKey(AccountsSession,related_name='StaffAppraisalLockingUnlocking_Semtiming_session',db_column='session',null=True,on_delete=models.SET_NULL,default=1)
    time_stamp = models.DateTimeField(db_column="time_stamp", auto_now=True)

    class Meta:
        db_table = 'StaffAppraisal_lockingunlocking'
        managed = True

class StaffAppraisalLockingUnlockingStatus(models.Model):
    locking_details = models.ForeignKey(StaffAppraisalLockingUnlocking, db_column='locking_details', related_name= 'StaffAppraisalLockingUnlockingStatus_StaffAppraisalLockingUnlocking_locking_details', on_delete=models.SET_NULL, null=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', max_length=20, related_name='StaffAppraisalLockingUnlockingStatus_EmployeePrimdetail_emp_id', null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True,default="INSERT")

    class Meta:
        db_table = 'StaffAppraisal_LockingUnlockingStatus'
        managed = True
############################# END ############################## LOCKING AND UNLOCKING ################################################################

############################################################### QUES MAX MARK SETTING ################################################################
    
    ################# NEED TO IMPLEMENT LIKE DROPDOWNS ########################
class StaffAppraisalQuestion(models.Model):
    form_type = models.CharField(db_column='form_type', max_length=500, blank=True, null=True)# FORM S-BAND/ A-BAND/ EMG-BAND {Make static on frontend}
    form_part = models.CharField(db_column='form_part', max_length=500, blank=True, null=True)# FORM PART1/ PART2/ PART3 {Make static on frontend} 
    ques_id = models.AutoField(db_column='ques_id', primary_key=True) #{ref: Sno} 
    parent_ques = models.IntegerField(db_column='parent_ques', blank=True, null=True) #{ref: pid}
    field = models.CharField(db_column='field', max_length=500, blank=True, null=True) #{ref: field}
    max_marks = models.IntegerField(db_column="max_marks", null=True) #Similar to statement take input along with statement
    statement = models.CharField(db_column='statement', max_length=500, blank=True, null=True) #{ref: Value}
    status=models.CharField(db_column='status',null=True,max_length=10,default="INSERT")
    session=models.ForeignKey(AccountsSession,related_name='StaffAppraisalQuestion_AccountsSession_session',db_column='session',null=True,on_delete=models.SET_NULL,default=1)

    class Meta:
        db_table = 'StaffAppraisal_Question'
        managed = True
    '''
    Field except form_type, form_part are just need to work like dropdown
    '''
############################# END ############################## QUES MAX MARK SETTING ################################################################

############################################################### ENTRY POINT TO START FILLING FORM #####################################################
class StaffAppraisalApplication(models.Model):
    form_type = models.CharField(db_column='form_type', max_length=500, blank=True, null=True)# FORM S-BAND/ A-BAND/ EMG-BAND {Make static on frontend}
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='ques_emp_id', max_length=20, related_name='StaffAppraisalApplication_EmployeePrimdetail_emp_id', on_delete=models.SET_NULL, null=True)
    status=models.CharField(db_column='status',null=True,max_length=10,default="INSERT")# SAVED/ SUBMITTED 
    session=models.ForeignKey(AccountsSession,related_name='StaffAppraisalApplication_AccountsSession_session',db_column='session',null=True,on_delete=models.SET_NULL,default=1)
    time_stamp = models.DateTimeField(db_column="time_stamp", auto_now=True)

    class Meta:
        db_table = 'StaffAppraisal_Application'
        managed = True
############################### END ########################## ENTRY POINT TO START FILLING FORM #####################################################

################################################################ ALL QUES ANSWERS ################################################################
class StaffAppraisalAnswer(models.Model):
    application = models.ForeignKey(StaffAppraisalApplication, db_column='ques_emp_id', max_length=20, related_name='StaffAppraisalAnswer_StaffAppraisalApplication_application', on_delete=models.SET_NULL, null=True)
    ques_id = models.ForeignKey(StaffAppraisalQuestion, db_column='ques_id', null=True, related_name='StaffAppraisalAnswer_StaffAppraisalQuestion_ques_id', on_delete=models.SET_NULL)
    marks_obtained = models.IntegerField(db_column="marks_obtained", null=True)
    answer = models.TextField(db_column="answer", null=True)
    status = models.CharField(db_column="status", default="INSERT", max_length=20)
    time_stamp = models.DateTimeField(db_column="time_stamp", auto_now=True)

    class Meta:
        db_table = 'StaffAppraisal_Answer'
        managed = True
############################# END ############################## ALL QUES ANSWERS ################################################################

############################################################### APPROVAL STATUS ################################################################
class StaffAppraisalRecommendationApproval(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', related_name='StaffAppraisalRecommendationApproval_EmployeePrimdetail_emp_id', max_length=20, on_delete=models.SET_NULL, null=True)
    increment_type = models.CharField(db_column='increment_type', max_length=50, blank=True) 
    # NO INCREMENT, NORMAL, SPECIAL, PROMOTION WITH SPECIAL INCREAMENT, PROMOTION WITHOUT INCREAMENT
    increment_amount = models.IntegerField(db_column="increment_amount", null = True)
    promoted_to = models.ForeignKey(EmployeeDropdown, db_column="promoted_to", max_length=200, related_name='StaffAppraisalRecommendationApproval_EmployeeDropdown_promoted_to', on_delete=models.SET_NULL, null= True)
    level = models.IntegerField(db_column="level", null = True)
    remark = models.TextField(db_column="remark", null=True)
    approval_status = models.CharField(db_column="approval_status", default="INSERT", max_length=20)
    added_by = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', max_length=20, related_name='StaffAppraisalRecommendationApproval_EmployeePrimdetail_added_by', null=True, on_delete=models.SET_NULL)
    session=models.ForeignKey(AccountsSession,related_name='StaffAppraisalRecommendationApproval_AccountsSession_session',db_column='session',null=True,on_delete=models.SET_NULL,default=1)
    status = models.CharField(db_column="status", default="INSERT", max_length=20)
    time_stamp = models.DateTimeField(db_column="time_stamp", auto_now=True)

    class Meta:
        db_table = 'StaffAppraisal_RecommendationApproval'
        managed = True
############################# END ############################## APPROVAL STATUS ################################################################

class AarReportingStatus(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='ques_emp_id', max_length=20, related_name='emp_id_aar', on_delete=models.SET_NULL, null=True)
    status = models.CharField(db_column="status", default="INSERT", max_length=20)
    remark = models.CharField(db_column="remark", max_length=20)
    reportingLevel = models.IntegerField()
    approved_by = models.ForeignKey(EmployeePrimdetail, db_column='approved_by', max_length=20, related_name='approved_by', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'StaffAppraisal_Reporting_Status'
        managed = True