# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from login.models import AarDropdown, EmployeeDropdown, EmployeePrimdetail
from Accounts.models import AccountsDropdown


class AarMultiselect(models.Model):
    id = models.AutoField(primary_key=True)
    sno = models.CharField(db_column='sno', max_length=100)
    emp_id = models.CharField(db_column='emp_id', max_length=150)
    type = models.CharField(db_column='type', max_length=100)
    field = models.CharField(db_column='field', max_length=100, null=True, blank=True)
    value = models.CharField(db_column='value', max_length=100, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'aar_multiselect'


class guestLectures(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', null=True, on_delete=models.SET_NULL)
    date = models.DateField(db_column='Date')
    topic = models.CharField(db_column='guest_title', max_length=200)
    speaker = models.CharField(db_column='Speaker', max_length=50, blank=True, null=True)
    designation = models.TextField(db_column='Speaker_Designation', default=None, blank=True, null=True)
    organization = models.TextField(db_column='Organization',  blank=True, null=True)
    speaker_profile = models.TextField(db_column='Speaker_Profile', blank=True, null=True)
    contact_number = models.CharField(db_column='contact_number', max_length=100, blank=True, null=True)
    e_mail = models.CharField(db_column='e_mail', max_length=100, blank=True, null=True)
    participants_no = models.IntegerField(db_column='No_Of_Participants', blank=True, null=True)
    remark = models.TextField(db_column='Remark', null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True, default='INSERT')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'GuestLectures'


class industrialVisit(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', null=True, on_delete=models.SET_NULL)
    date = models.DateField(db_column='Date')
    industry = models.TextField(db_column='Industry', blank=True, null=True)
    address = models.TextField(db_column='address', blank=True, null=True)
    contact_person = models.CharField(db_column='contact_person', max_length=100, blank=True, null=True)
    contact_number = models.CharField(db_column='contact_number', max_length=100, blank=True, null=True)
    e_mail = models.CharField(db_column='e_mail', max_length=100, blank=True, null=True)
    participants_no = models.IntegerField(db_column='No_Of_Participants', blank=True, null=True)
    remark = models.TextField(db_column='Remark', null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True, default='INSERT')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'IndustrialVisit'


class eventsorganized(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, related_name='n1Category_event', db_column='Category')  # Field name made lowercase.
    type = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, related_name='n1Type_event', db_column='Type')  # Field name made lowercase.
    from_date = models.DateField(db_column='From_Date')  # Field name made lowercase.
    to_date = models.DateField(db_column='To_Date')  # Field name made lowercase.
    organization_sector = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, related_name='n1OrganizationSector_event', db_column='Organization_Sector')  # Field name made lowercase.
    incorporation_status = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, related_name='n1IncorporationStatus_evnt', db_column='Incorporation_Type')  # Field name made lowercase.
    title = models.TextField(db_column='Title')  # Field name made lowercase.
    venue = models.CharField(db_column='Venue', max_length=100)  # Field name made lowercase.
    venue_other = models.CharField(db_column='Venue_Other', max_length=300, null=True, blank=True,default=None)
    participants = models.IntegerField(db_column='Participants')  # Field name made lowercase.
    organizers = models.CharField(db_column='Organizers', max_length=100)  # Field name made lowercase.
    attended = models.CharField(db_column='Attended', max_length=50)  # Field name made lowercase.
    collaboration = models.CharField(db_column='Collaborations', max_length=50)  # Field name made lowercase.
    sponsership = models.CharField(db_column='Sponsership', max_length=50)  # Field name made lowercase.
    description = models.TextField(db_column='description', null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True, default='INSERT')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'eventsorganized'


class MouSigned(models.Model):
    sno = models.AutoField(db_column='sno', primary_key=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', null=True, on_delete=models.SET_NULL)
    date = models.DateField(null=True, blank=True)
    organization = models.TextField(db_column='organization')
    objective = models.TextField(db_column='objective')
    valid_upto = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, db_column='contact')
    e_mail = models.EmailField()
    intro = models.TextField(db_column='intro', null=True, default='')
    document = models.FileField(null=True, blank=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True, default='INSERT')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'mousigned'


class Achievement(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, db_column='category', related_name='n1Category')
    description = models.TextField()
    type = models.CharField(max_length=100)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    date = models.DateField()
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True, default='INSERT')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'achievement'


class Hobbyclub(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', null=True, on_delete=models.SET_NULL)
    club_name = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL, null=True, db_column='club_name', related_name='n1Club_Name')
    project_title = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    project_incharge = models.ForeignKey(EmployeePrimdetail, on_delete=models.SET_NULL, null=True, db_column='project_incharge', related_name='n1Project_Incharge')
    team_size = models.IntegerField()
    project_description = models.TextField()
    project_cost = models.IntegerField()
    project_outcome = models.TextField()
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True, default='INSERT')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'hobbyclub'


class SummerWinterSchool(models.Model):
    sno = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', related_name='summer_emp_id', null=True, on_delete=models.SET_NULL)
    start_date = models.DateField()
    end_date = models.DateField()
    resource_person = models.CharField(max_length=100)
    resource_person_id = models.ForeignKey(EmployeePrimdetail, db_column='resource_person_id', on_delete=models.SET_NULL, related_name='resource_person_id', null=True)
    topic = models.TextField()
    participant_number = models.IntegerField()
    participant_fee = models.FloatField()
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True, default='INSERT')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'summer_winter_school'


class DeptAchApproval(models.Model):
    level = models.IntegerField(db_column='level', blank=True, null=True)
    approval_category = models.CharField(db_column='approval_category', max_length=40, blank=True, null=True, default=None)
    # GUEST LECTURE,INDUSTRIAL VISIT,MOU SIGNED,EVENT ORGANISED,SUMMER/WINTER,HOBBY CLUB,STUDENT ACH,DEPARTMENTAL ACH
    approval_id = models.IntegerField(db_column='approval_id', blank=True, null=True)
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name="DeptAchApproval_approved_by", db_column="approved_by", null=True, on_delete=models.SET_NULL)
    approval_status = models.CharField(db_column='approval_status', max_length=40, blank=True, null=True, default="PENDING")
    # APPROVED,REJECTED,PENDING,DELETE
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "DeptAchApproval"
        managed = True
