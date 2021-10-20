# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from Registrar.models import *
from StudentAcademics.models import *
# Create your models here.


class StudentLeftPanel(models.Model):
    menu_id = models.AutoField(db_column='Menu_Id', primary_key=True)  # Field name made lowercase.
    parent_id = models.IntegerField(db_column='Parent_Id')  # Field name made lowercase.
    role = models.CharField(max_length=50, null=True)
    link_name = models.CharField(db_column='Link_Name', max_length=200)  # Field name made lowercase.
    link_address = models.CharField(db_column='Link_Address', max_length=300)  # Field name made lowercase.
    icons = models.CharField(db_column='Icons', max_length=100, blank=True, null=True)  # Field name made lowercase.
    priority = models.IntegerField(db_column='Priority', default=0)  # Field name made lowercase.

    class Meta:
        db_table = 'Stuleft_panel'


class StudentFillSubjects_1819o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819o, related_name='s_Uniq_Id', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    # subject_id = models.ForeignKey(SubjectInfo_1819o, related_name="Sub_id", on_delete=models.SET_NULL, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StudentFillSubjects_1819o'

# class StudentBankdetails(models.Model):

#     acc_name = models.CharField(max_length=1000, default=None, null=True)
#     acc_num = models.CharField(max_length=1000, default=None, null=True)
#     bank_name = models.CharField(max_length=1000, http://localhost:3000/#/erp/Hostel/SeatAllotmentRuledefault=None, null=True)
#     ifsc_code = models.CharField(max_length=1000, default=None, null=True)
#     branch = models.CharField(max_length=1000, default=None, null=True)
#     address = models.CharField(max_length=1000, default=None, null=True)
#     status = models.CharField(db_column="status",max_length=20,default="INSERT")
#     uniq_id = models.ForeignKey(StudentPrimDetail,related_name='StudentBankdetails_Uniq_Id',on_delete=models.SET_NULL,null=True)  # Field name made lowercase.
#     edit_by = models.ForeignKey(AuthUser,related_name='Student_BankDetails_Edit_by',on_delete=models.SET_NULL,null=True)

#     class Meta:
#         managed = True
#         db_table = 'Student_BankDetails'


class StudentActivities_1819o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819o, related_name='uniq_id_Activity_1819o', db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    activity_type = models.ForeignKey(StudentAcademicsDropdown, related_name='StudentActivities_activity_type_1819o', blank=True, null=True, on_delete=models.SET_NULL)
    date_of_event = models.DateField(null=True, default=None)
    organised_by = models.TextField(null=True, default=None)
    venue_address = models.TextField(null=True, default=None)
    venue_city = models.TextField(null=True, default=None)
    venue_state = models.TextField(null=True, default=None)
    venue_country = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)
    student_document = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StudentActivities_1819o'
        managed = True


#################################################################################################################
############################## 1819e models #####################################################################
#################################################################################################################


class StudentFillSubjects_1819e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='s_Uniq_Id', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    subject_id = models.ForeignKey(SubjectInfo_1819e, related_name="Sub_id", on_delete=models.SET_NULL, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StudentFillSubjects_1819e'


class StudentActivities_1819e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='uniq_id_Activity_1819e', db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    activity_type = models.ForeignKey(StudentAcademicsDropdown, related_name='StudentActivities_activity_type_1819e', blank=True, null=True, on_delete=models.SET_NULL)
    date_of_event = models.DateField(null=True, default=None)
    organised_by = models.TextField(null=True, default=None)
    venue_address = models.TextField(null=True, default=None)
    venue_city = models.TextField(null=True, default=None)
    venue_state = models.TextField(null=True, default=None)
    venue_country = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)
    student_document = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StudentActivities_1819e'
        managed = True


class PlacementPolicy(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819e, related_name='PlacementPolicy_uniq_id', db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    form_type = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PlacementPolicy'
        managed = True

#################################################################################################################
############################## 1920o models #####################################################################
#################################################################################################################


class StudentFillSubjects_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='s_Uniq_Id', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    subject_id = models.ForeignKey(SubjectInfo_1920o, related_name="Sub_id", on_delete=models.SET_NULL, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StudentFillSubjects_1920o'


class StudentActivities_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='uniq_id_Activity_1920o', db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    activity_type = models.ForeignKey(StudentAcademicsDropdown, related_name='StudentActivities_activity_type_1920o', blank=True, null=True, on_delete=models.SET_NULL)
    date_of_event = models.DateField(null=True, default=None)
    organised_by = models.TextField(null=True, default=None)
    venue_address = models.TextField(null=True, default=None)
    venue_city = models.TextField(null=True, default=None)
    venue_state = models.TextField(null=True, default=None)
    venue_country = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)
    student_document = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StudentActivities_1920o'
        managed = True


class StudentFillInsurance_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='insurance_Uniq_Id', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(auto_now=True)
    nominee_name = models.CharField(db_column='Nominee_Name', max_length=50, blank=True, null=True)
    nominee_relation = models.CharField(db_column='Nominee_Relation', max_length=50, blank=True, null=True)
    insurer_name = models.CharField(db_column='Insurer_Name', max_length=50, blank=True, null=True)
    insurer_dob = models.DateField(db_column='Insurer_dob', blank=True, null=True)
    insurer_aadhar_num = models.CharField(db_column="Insurer_aadhar_num", null=True, max_length=40, blank=True, default=None)
    insurer_occupation = models.CharField(db_column="Insurer_occupation", null=True, max_length=40, blank=True, default=None)
    insurer_nominee_name = models.CharField(db_column='Insurer_Nominee_Name', max_length=50, blank=True, null=True)
    insurer_relation = models.CharField(db_column='Insurer_Relation', max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'StudentFillInsurance_1920o'


class StudentHobbyClubs_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='hobbyclub_Uniq_Id', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(auto_now=True)
    hobby_club = models.ForeignKey(StudentAcademicsDropdown, related_name='hobby_club_Id', db_column='hobby_club', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'StudentHobbyClubs_1920o'


class MessageList_1920o(models.Model):
    message = models.TextField(db_column="message")
    user_type = models.CharField(db_column="user_type", max_length=100)
    time_stamp = models.DateTimeField(db_column="time_stamp", auto_now=True)
    status = models.CharField(db_column="status", max_length=20, default="INSERT")
    read_status = models.CharField(db_column="read_status", max_length=20, default="UNREAD")
    sent_by_to = models.ForeignKey(studentSession_1920o, related_name='messagelist_sent_by_to', on_delete=models.SET_NULL, null=True, db_column="sent_by_to")

    class Meta:
        managed = True
        db_table = 'MessageList_1920o'

#########################################################################################################################################
########################################################### 1920e #######################################################################
#########################################################################################################################################


class StudentFillSubjects_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name='s_Uniq_Id_1920e', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    subject_id = models.ForeignKey(SubjectInfo_1920e, related_name="Sub_id_1920e", on_delete=models.SET_NULL, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StudentFillSubjects_1920e'


class StudentFillInsurance_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name='insurance_Uniq_Id_2', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(auto_now=True)
    nominee_name = models.CharField(db_column='Nominee_Name', max_length=50, blank=True, null=True)
    nominee_relation = models.CharField(db_column='Nominee_Relation', max_length=50, blank=True, null=True)
    insurer_name = models.CharField(db_column='Insurer_Name', max_length=50, blank=True, null=True)
    insurer_dob = models.DateField(db_column='Insurer_dob', blank=True, null=True)
    insurer_aadhar_num = models.CharField(db_column="Insurer_aadhar_num", null=True, max_length=40, blank=True, default=None)
    insurer_occupation = models.CharField(db_column="Insurer_occupation", null=True, max_length=40, blank=True, default=None)
    insurer_nominee_name = models.CharField(db_column='Insurer_Nominee_Name', max_length=50, blank=True, null=True)
    insurer_relation = models.CharField(db_column='Insurer_Relation', max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'StudentFillInsurance_1920e'


class StudentHobbyClubs_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name='Student_hobbyclub_Uniq_Id', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(auto_now=True)
    hobby_club = models.ForeignKey(StudentAcademicsDropdown, related_name='Student_hobby_club_Id', db_column='hobby_club', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'StudentHobbyClubs_1920e'


class StudentActivities_1920e(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name='uniq_id_Activity_1920e', db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    activity_type = models.ForeignKey(StudentAcademicsDropdown, related_name='StudentActivities_activity_type_1920e', blank=True, null=True, on_delete=models.SET_NULL)
    date_of_event = models.DateField(null=True, default=None)
    organised_by = models.TextField(null=True, default=None)
    venue_address = models.TextField(null=True, default=None)
    venue_city = models.TextField(null=True, default=None)
    venue_state = models.TextField(null=True, default=None)
    venue_country = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)
    student_document = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StudentActivities_1920e'
        managed = True


class StudentInternshipPrograms(models.Model):
    course = models.ForeignKey(StudentDropdown, related_name='StudentInternshipPrograms_course_id', db_column='course_id', blank=True, null=True, on_delete=models.SET_NULL)
    year = models.IntegerField()
    field = models.CharField(max_length=300, default=None)
    to_select = models.IntegerField()
    duration = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StudentInternshipPrograms'
        managed = True


class StudentInternshipsTaken(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920e, related_name="StudentInternshipsTaken_uniq_id", db_column="uniq_id", null=True, on_delete=models.SET_NULL)
    internship = models.CharField(max_length=150, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)
    taken = models.CharField(max_length=20)
    erp_interest = models.CharField(max_length=20, default=None)
    session = models.ForeignKey(Semtiming, related_name='StudentInternshipsTaken_session', db_column='session', null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'StudentInternshipsTaken'
        managed = True

#########################################################################################################################################
########################################################## 2021o ########################################################################
#########################################################################################################################################

class StudentFillInsurance_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name='insurance_Uniq_Id_2021o', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(auto_now=True)
    nominee_name = models.CharField(db_column='Nominee_Name', max_length=50, blank=True, null=True)
    nominee_relation = models.CharField(db_column='Nominee_Relation', max_length=50, blank=True, null=True)
    insurer_name = models.CharField(db_column='Insurer_Name', max_length=50, blank=True, null=True)
    insurer_dob = models.DateField(db_column='Insurer_dob', blank=True, null=True)
    insurer_aadhar_num = models.CharField(db_column="Insurer_aadhar_num", null=True, max_length=40, blank=True, default=None)
    insurer_occupation = models.CharField(db_column="Insurer_occupation", null=True, max_length=40, blank=True, default=None)
    insurer_nominee_name = models.CharField(db_column='Insurer_Nominee_Name', max_length=50, blank=True, null=True)
    insurer_relation = models.CharField(db_column='Insurer_Relation', max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'StudentFillInsurance_2021o'


class StudentHobbyClubs_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name='Student_hobbyclub_Uniq_Id_2021o', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(auto_now=True)
    hobby_club = models.ForeignKey(StudentAcademicsDropdown, related_name='Student_hobby_club_Id_2021o', db_column='hobby_club', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'StudentHobbyClubs_2021o'

class StudentInternshipsTakenNew(models.Model):
    uniq_id = models.ForeignKey(StudentPrimDetail, related_name="StudentInternshipsTaken_uniq_id_2021o", db_column="uniq_id", null=True, on_delete=models.SET_NULL)
    internship = models.CharField(max_length=150, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)
    taken = models.CharField(max_length=20)
    erp_interest = models.CharField(max_length=20, default=None)
    session = models.ForeignKey(Semtiming, related_name='StudentInternshipsTaken_session_2021o', db_column='session', null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'StudentInternshipsTaken_New'
        managed = True

class StudentActivities_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name='uniq_id_Activity_2021o', db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    activity_type = models.ForeignKey(StudentAcademicsDropdown, related_name='StudentActivities_activity_type_2021o', blank=True, null=True, on_delete=models.SET_NULL)
    date_of_event = models.DateField(null=True, default=None)
    organised_by = models.TextField(null=True, default=None)
    venue_address = models.TextField(null=True, default=None)
    venue_city = models.TextField(null=True, default=None)
    venue_state = models.TextField(null=True, default=None)
    venue_country = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)
    student_document = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StudentActivities_2021o'
        managed = True


class PlacementPolicyNew(models.Model):
    uniq_id = models.ForeignKey(StudentPrimDetail, related_name='PlacementPolicy_uniq_id', db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    form_type = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)
    session = models.ForeignKey(Semtiming, related_name='PlacementPolicyNew_session', db_column='session', null=True, on_delete=models.SET_NULL)
    class Meta:
        db_table = 'PlacementPolicyNew'
        managed = True


########################################################## 2021e ########################################################################
#########################################################################################################################################

class StudentFillInsurance_2021e(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='insurance_Uniq_Id_2021e', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(auto_now=True)
    nominee_name = models.CharField(db_column='Nominee_Name', max_length=50, blank=True, null=True)
    nominee_relation = models.CharField(db_column='Nominee_Relation', max_length=50, blank=True, null=True)
    insurer_name = models.CharField(db_column='Insurer_Name', max_length=50, blank=True, null=True)
    insurer_dob = models.DateField(db_column='Insurer_dob', blank=True, null=True)
    insurer_aadhar_num = models.CharField(db_column="Insurer_aadhar_num", null=True, max_length=40, blank=True, default=None)
    insurer_occupation = models.CharField(db_column="Insurer_occupation", null=True, max_length=40, blank=True, default=None)
    insurer_nominee_name = models.CharField(db_column='Insurer_Nominee_Name', max_length=50, blank=True, null=True)
    insurer_relation = models.CharField(db_column='Insurer_Relation', max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'StudentFillInsurance_2021e'


class StudentHobbyClubs_2021e(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='Student_hobbyclub_Uniq_Id_2021e', db_column='uniq_id', null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    time_stamp = models.DateTimeField(auto_now=True)
    hobby_club = models.ForeignKey(StudentAcademicsDropdown, related_name='Student_hobby_club_Id_2021e', db_column='hobby_club', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='INSERT')

    class Meta:
        managed = True
        db_table = 'StudentHobbyClubs_2021e'

class StudentActivities_2021e(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='uniq_id_Activity_2021e', db_column='uniq_id', null=True, on_delete=models.SET_NULL)
    activity_type = models.ForeignKey(StudentAcademicsDropdown, related_name='StudentActivities_activity_type_2021e', blank=True, null=True, on_delete=models.SET_NULL)
    date_of_event = models.DateField(null=True, default=None)
    organised_by = models.TextField(null=True, default=None)
    venue_address = models.TextField(null=True, default=None)
    venue_city = models.TextField(null=True, default=None)
    venue_state = models.TextField(null=True, default=None)
    venue_country = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)
    student_document = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, default='INSERT')
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StudentActivities_2021e'
        managed = True
