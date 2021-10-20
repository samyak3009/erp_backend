# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from login.models import AarDropdown,EmployeeDropdown,EmployeePrimdetail
from Accounts.models import AccountsDropdown

class Books(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id_books',null=True,on_delete=models.SET_NULL)
    role = models.ForeignKey(AarDropdown,null=True,on_delete= models.SET_NULL, db_column='Role',related_name='n1role',default=None)  # Field name made lowercase.
    role_for = models.ForeignKey(AarDropdown, null=True,on_delete= models.SET_NULL,related_name='n1Role_for', db_column='Role_For',default=None)  # Field name made lowercase.
    publisher_type = models.ForeignKey(AarDropdown, null=True,on_delete= models.SET_NULL, db_column='Publisher_Type',related_name='n1publisher_type',default=None)  # Field name made lowercase.
    title = models.TextField(db_column='Title', null=True)  # Field name made lowercase.
    edition = models.CharField(db_column='Edition',max_length=100)  # Field name made lowercase.
    published_date = models.DateField(db_column='Published_Date')  # Field name made lowercase.
    chapter = models.TextField(db_column='Chapter', null=True)  # Field name made lowercase.
    isbn = models.CharField(db_column='ISBN', max_length=100)  # Field name made lowercase.
    # copyright_status = models.ForeignKey(AarDropdown, models.DO_NOTHING, db_column='Copyright_Status',related_name='n1copyright_status',default=None)  # Field name made lowercase.
    copyright_status = models.CharField(db_column='Copyright_Status', max_length=100)  # Field name made lowercase.
    copyright_no = models.CharField(db_column='Copyright_No', max_length=100,null=True)  # Field name made lowercase.
    author = models.ForeignKey(AarDropdown, null=True,on_delete= models.SET_NULL, db_column='Author',related_name='n1author',default=None)  # Field name made lowercase.
    publisher_name = models.TextField(db_column='Publisher_Name')  # Field name made lowercase.
    publisher_address = models.TextField(db_column='Publisher_Address')  # Field name made lowercase.
    publisher_zip_code = models.CharField(db_column='Publisher_Zip_Code',max_length=20,null=True)  # Field name made lowercase.
    publisher_contact = models.CharField(db_column='Publisher_Contact',max_length=50)  # Field name made lowercase.
    publisher_email = models.CharField(db_column='Publisher_Email', max_length=50)  # Field name made lowercase.
    publisher_website = models.CharField(db_column='Publisher_Website', max_length=100)  # Field name made lowercase.
    approve_status=models.CharField(db_column='approve_status', max_length=100,default='PENDING')
    t_date=models.DateTimeField(db_column='T_date')

    class Meta:
        managed = True
        db_table = 'books'


class Researchconference(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    #emp_id=models.CharField(db_column='emp_id_conference', max_length=150)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id_conference',null=True,on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown,related_name='n1Category_Research',limit_choices_to={'field':'CATEGORY'}, on_delete=models.SET_NULL, db_column='Category',null=True)  # Field name made lowercase.
    type_of_conference = models.ForeignKey(AarDropdown,related_name='n1Conference_Type',limit_choices_to={'field':'TYPE_OF_CONFERENCE'}, on_delete=models.SET_NULL,null=True, db_column='Type_Of_Conference')  # Field name made lowercase.
    sub_category = models.ForeignKey(AarDropdown,related_name='n1Sub_Category_Conference', on_delete=models.SET_NULL,null=True,limit_choices_to={'field':'SUB_CATEGORY'}, db_column='Sub_Category')  # Field name made lowercase.
    sponsered = models.CharField(db_column='Sponsored', max_length=1000)  # Field name made lowercase.
    conference_title = models.TextField(db_column='Conference_Title')  # Field name made lowercase.
    paper_title = models.TextField(db_column='Paper_Title', null=True)  # Field name made lowercase.
    published_date = models.DateField(db_column='Published_Date')  # Field name made lowercase.
    organized_by = models.TextField(db_column='Organized_By', null=True)  # Field name made lowercase.
    journal_name = models.TextField(db_column='Journal_Name',null=True)  # Field name made lowercase.
    volume_no = models.TextField(db_column='Volume_No',null=True)  # Field name made lowercase.
    issue_no = models.CharField(db_column='Issue_No', max_length=100,null=True)  # Field name made lowercase.
    isbn = models.CharField(db_column='ISBN', max_length=100,null=True)  # Field name made lowercase.
    page_no = models.CharField(db_column='Page_No', max_length=100,null=True)  # Field name made lowercase.
    author = models.ForeignKey(AarDropdown,related_name='n1Author_Conference',limit_choices_to={'field':'AUTHOR'}, on_delete=models.SET_NULL, db_column='Author',null=True)  # Field name made lowercase.
    conference_from = models.DateField(db_column='Conference_From')
    conference_to = models.DateField(db_column='Conference_To')  # Field name made lowercase.
    other_description = models.CharField(db_column='Other_Description', max_length=500)  # Field name made lowercase.
    publisher_name = models.TextField(db_column='Publisher_Name')  # Field name made lowercase.
    publisher_address = models.TextField(db_column='Publisher_Address')  # Field name made lowercase.
    publisher_zip_code = models.CharField(db_column='Publisher_Zip_Code' ,max_length=20,null=True)  # Field name made lowercase.
    publisher_contact = models.CharField(db_column='Publisher_Contact',max_length=50)  # Field name made lowercase.
    publisher_email = models.CharField(db_column='Publisher_Email', max_length=50)  # Field name made lowercase.
    publisher_website = models.CharField(db_column='Publisher_Website', max_length=100)  # Field name made lowercase.
    others=models.CharField(db_column='other_conference',max_length=100,blank=True,null=True)
    approve_status=models.CharField(db_column='approve_status', max_length=100,default='PENDING')
    t_date=models.DateTimeField(db_column='T_date')
    class Meta:
        managed = True
        db_table = 'researchconference'


class Researchguidence(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
   # emp_id=models.CharField(db_column='emp_id_guid', max_length=150,null=True)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id_guid',null=True,on_delete=models.SET_NULL)
    guidence = models.ForeignKey(AarDropdown,related_name='n1Guidence',limit_choices_to={'field':'GUIDENCE'},on_delete= models.SET_NULL,null=True, db_column='Guidence')  # Field name made lowercase.
    course = models.ForeignKey(AarDropdown,related_name='n1Course_Guidence',limit_choices_to={'field':'COURSE'}, on_delete=models.SET_NULL, db_column='Course', blank=True, null=True)  # Field name made lowercase.
    degree=models.ForeignKey(AarDropdown,related_name='n1Degree',limit_choices_to={'field':'DEGREE'}, on_delete=models.SET_NULL, db_column='Degree', blank=True, null=True)
    no_of_students = models.IntegerField(db_column='No_Of_Students', blank=True, null=True)  # Field name made lowercase.
    degree_awarded = models.CharField(db_column='degree_awarded', max_length=100, blank=True, null=True)  #YES OR NO Field name made lowercase.
    uni_type = models.ForeignKey(AarDropdown,related_name='universityType',on_delete= models.CASCADE, db_column='University_type', blank=True, null=True)  # Field name made lowercase.
    uni_name = models.CharField(db_column='University_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    status = models.ForeignKey(AarDropdown,related_name='n1Status', on_delete=models.CASCADE,limit_choices_to={'field':'STATUS'}, db_column='Status', blank=True, null=True)  # Field name made lowercase.

    project_title = models.TextField(db_column='Project_Title', blank=True, null=True)  # Field name made lowercase.
    area_of_spec = models.TextField(db_column='Area_Of_Spec',  blank=True, null=True)  # Field name made lowercase.
    approve_status=models.CharField(db_column='approve_status', max_length=100,default='PENDING')
    t_date=models.DateTimeField(db_column='T_date')
    date=models.DateTimeField(db_column='date',null=True)

    class Meta:
        managed = True
        db_table = 'researchguidence'

class Researchjournal(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    #emp_id=models.CharField(db_column='emp_id_journal', max_length=150)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id_journal',null=True,on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown,related_name='n1Category_Journal',limit_choices_to={'field':'CATEGORY'}, on_delete=models.SET_NULL,null=True, db_column='Category')  # Field name made lowercase.
    type_of_journal = models.ForeignKey(AarDropdown,related_name='n1Type_Of_Journal',limit_choices_to={'field':'TYPE_JOURNAL'}, on_delete=models.SET_NULL,null=True, db_column='Type_Of_Journal')  # Field name made lowercase.
    sub_category = models.ForeignKey(AarDropdown,related_name='n1Sub_Category_Journal',limit_choices_to={'field':'SUB_CATEGORY'}, on_delete=models.SET_NULL,null=True, db_column='Sub_Category')  # Field name made lowercase.
    published_date = models.DateField(db_column='Published_Date')  # Field name made lowercase.
    paper_title = models.TextField(db_column='Paper_Title')  # Field name made lowercase.
    impact_factor = models.FloatField(db_column='Impact_Factor',blank=True,null=True)  # Field name made lowercase.
    journal_name = models.TextField(db_column='Journal_Name', null=True)  # Field name made lowercase.
    volume_no = models.TextField(db_column='Volume_No',null=True)  # Field name made lowercase.
    issue_no = models.CharField(db_column='Issue_No', max_length=100,null=True)  # Field name made lowercase.
    isbn = models.CharField(db_column='ISBN', max_length=100,null=True)  # Field name made lowercase.
    page_no = models.CharField(db_column='Page_No', max_length=100,null=True)  # Field name made lowercase.
    author = models.ForeignKey(AarDropdown,related_name='n1Author_Journal',limit_choices_to={'field':'AUTHOR'}, on_delete=models.SET_NULL,null=True, db_column='Author')  # Field name made lowercase.
    publisher_name = models.TextField(db_column='Publisher_Name')  # Field name made lowercase.
    publisher_address1 = models.TextField(db_column='Publisher_Address1')  # Field name made lowercase.
    publisher_address2 = models.TextField(db_column='Publisher_Address2', null=True,blank=True)  # Field name made lowercase.
    publisher_zip_code = models.CharField(db_column='Publisher_Zip_Code' ,max_length=20,null=True)  # Field name made lowercase.
    publisher_contact = models.CharField(db_column='Publisher_Contact',max_length=15)  # Field name made lowercase.
    publisher_email = models.CharField(db_column='Publisher_Email', max_length=50)  # Field name made lowercase.
    publisher_website = models.CharField(db_column='Publisher_Website', max_length=100)  # Field name made lowercase.
    others=models.CharField(db_column='other_journal',max_length=100,blank=True,null=True)
    approve_status=models.CharField(db_column='approve_status', max_length=100,default='PENDING')
    t_date=models.DateTimeField(db_column='T_date')
    final_status=models.CharField(db_column='final_status', max_length=100,default='PENDING')
    class Meta:
        managed = True
        db_table = 'researchjournal'



class LecturesTalks(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,null=True,related_name='n1Category_Lectures', db_column='Category')  # Field name made lowercase.
    type = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,null=True,related_name='n1Type', db_column='Type')  # Field name made lowercase.
    organization_sector = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True,related_name='n1Organization_Sector_Lectures', db_column='Organization_sector')  # Field name made lowercase.
    incorporation_status = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True,related_name='n1Incorporation_sector_Lectures', db_column='Incorporation_sector')  # Field name made lowercase.
    role = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True,related_name='n1Role_Lectures', db_column='Role')  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    topic = models.TextField(db_column='Topic')  # Field name made lowercase.
    participants = models.IntegerField(db_column='Participants')  # Field name made lowercase.
    venue = models.TextField(db_column='Venue')  # Field name made lowercase.
    address = models.TextField(db_column='Address')  # Field name made lowercase.
    pin_code = models.CharField(db_column='Pin_Code',max_length=50)  # Field name made lowercase.
    contact_number = models.CharField(db_column='Contact_Number',max_length=50)  # Field name made lowercase.
    e_mail = models.CharField(db_column='E_mail', max_length=50)  # Field name made lowercase.
    website = models.CharField(db_column='Website',max_length=50 ,blank=True, null=True)  # Field name made lowercase.
    approve_status=models.CharField(db_column='approve_status', max_length=100,default='PENDING')
    t_date=models.DateTimeField(db_column='T_date')

    class Meta:
        managed=True
        db_table='lectures_talks'

class Sponsers(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    spons_id=models.IntegerField(db_column='spons_id')
    emp_id=models.CharField(db_column='emp_id', max_length=150)
    sponser_name=models.CharField(db_column='sponsor_name',max_length=100)
    type=models.CharField(db_column='sponsor_type',max_length=100)
    pin_code=models.CharField(db_column='pin_code',max_length=100,blank=True,null=True)
    address=models.TextField(db_column='address',blank=True,null=True)
    contact_person=models.CharField(db_column='contact_person',max_length=100,blank=True,null=True)
    contact_number=models.CharField(db_column='contact_number',max_length=100,blank=True,null=True)
    e_mail=models.CharField(db_column='e_mail',max_length=100,blank=True,null=True)
    website=models.CharField(db_column='website',max_length=100,blank=True,null=True)
    amount=models.CharField(db_column='amount',max_length=100,blank=True,null=True)
    field_type=models.CharField(db_column='field_type',max_length=100,blank=True,null=True)

    class Meta:
        managed = True
        db_table = 'Sponsers'

class TrainingDevelopment(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True,related_name='n1Category_Training', db_column='Category')  # Field name made lowercase.
    type = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True, related_name='n1Type_Training',db_column='Type')  # Field name made lowercase.
    from_date = models.DateField(db_column='From_Date')  # Field name made lowercase.
    to_date = models.DateField(db_column='To_Date')  # Field name made lowercase.
    role = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True,related_name='n1Role_Training', db_column='Role')  # Field name made lowercase.
    organization_sector = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True,related_name='n1OrganizationSector_Training', db_column='Organization_Sector')  # Field name made lowercase.
    incorporation_status = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,null=True,related_name='n1IncorporationStatus_Training', db_column='Incorporation_Status')  # Field name made lowercase.
    title = models.TextField(db_column='Title')  # Field name made lowercase.
    venue = models.CharField(db_column='Venue', max_length=100)  # Field name made lowercase.
    participants = models.IntegerField(db_column='Participants')  # Field name made lowercase.
    organizers = models.TextField(db_column='Organizers')  # Field name made lowercase.
    attended = models.CharField(db_column='Attended', max_length=50)  # Field name made lowercase.
    collaborations = models.CharField(db_column='Collaborations', max_length=50)  # Field name made lowercase.
    sponsership = models.CharField(db_column='Sponsership', max_length=50)  # Field name made lowercase.
    #amount = models.CharField(db_column='Amount', max_length=100)
    approve_status=models.CharField(db_column='approve_status', max_length=100,default='PENDING')
    t_date=models.DateTimeField(db_column='T_date')
    class Meta:
        managed = True
        db_table = 'training_development'


class ProjectConsultancy(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
    type = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True, related_name='n1Type_Project',db_column='Type')
    status = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True, related_name='n1Project_Status',db_column='Status')
    sector = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True, related_name='n1Sector',db_column='Sector')
    title=models.TextField(db_column='patent_title')
    descreption=models.TextField(db_column='patent_descreption')
    start_date = models.DateField(db_column='Start_Date')  # Field name made lowercase.
    end_date = models.DateField(db_column='End_Date', blank=True, null=True)  # Field name made lowercase.
    principal_investigator = models.CharField(db_column='Principal_Investigator', max_length=100)  # Field name made lowercase.
    co_principal_investigator = models.CharField(db_column='Co_Principal_Investigator', max_length=100)  # Field name made lowercase.
    principal_investigator_id = models.CharField(db_column='Principal_Investigator_Id', max_length=100)  # Field name made lowercase.
    co_principal_investigator_id = models.CharField(db_column='Co_Principal_Investigator_Id', max_length=100)
    team_size = models.IntegerField(db_column='Team_Size')  # Field name made lowercase.
    sponsored = models.CharField(db_column='Sponsored', max_length=50)  # Field name made lowercase.
    association = models.CharField(db_column='Association', max_length=50)  # Field name made lowercase.
    approve_status=models.CharField(db_column='approve_status', max_length=100,default='PENDING')
    t_date=models.DateTimeField(db_column='T_date')

    class Meta:
        managed = True
        db_table = 'project_consultancy'

class Patent(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
    title=models.TextField(db_column='patent_title')
    descreption=models.TextField(db_column='patent_descreption')
    collaboration = models.CharField(db_column='Collaboration', max_length=50)  # Field name made lowercase.
    company_name = models.CharField(db_column='Company_Name', max_length=50,blank=True, null=True)  # Field name made lowercase.
    incorporate_status = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True,related_name='n1Incorporate_Status', db_column='Incorporate_Status',blank=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50,blank=True, null=True)  # Field name made lowercase.
    number = models.CharField(db_column='Number',max_length=150,blank=True, null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    owner = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True,related_name='n1Owner', db_column='Owner')  # Field name made lowercase.
    approve_status=models.CharField(db_column='approve_status', max_length=100,default='PENDING')
    t_date=models.DateTimeField(db_column='T_date')
    level = models.CharField(db_column='level', max_length=50,blank=True, null=True,default='NATIONAL')
    class Meta:
        managed = True
        db_table = 'patent'


class Discipline(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    id = models.IntegerField()
    type = models.CharField(db_column='Type', max_length=50)  # Field name made lowercase.
    emp_id = models.IntegerField(db_column='Emp_id')  # Field name made lowercase.
    value1 = models.ForeignKey(EmployeeDropdown,  on_delete=models.SET_NULL,null=True, related_name='n1DesciplineValue1', db_column='Value1',blank=True)  # Field name made lowercase.
    value2 = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,null=True, related_name='n1DesciplineValue2', db_column='Value2',blank=True)
    class Meta:
        managed = True
        db_table = 'discipline'



# class guestLectures(models.Model):
#     id = models.AutoField(db_column='id', primary_key=True)
#     emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
#     date = models.DateField(db_column='Date')
#     topic = models.CharField(db_column='guest_title',max_length=200)
#     speaker = models.CharField(db_column='Speaker', max_length=50, blank=True, null=True)
#     designation = models.TextField(db_column='Speaker_Designation',default=None ,blank=True, null=True)
#     organization = models.TextField(db_column='Organization',  blank=True, null=True)
#     speaker_profile = models.TextField(db_column='Speaker_Profile', blank=True, null=True)
#     contact_number = models.CharField(db_column='contact_number',max_length=100,blank=True,null=True)
#     e_mail = models.CharField(db_column='e_mail',max_length=100,blank=True,null=True)
#     # dept = models.ForeignKey(EmployeeDropdown,db_column='Dept', related_name='n1Department_for', blank=True, null=True,on_delete=models.SET_NULL)
#     participants_no = models.IntegerField(db_column='No_Of_Participants', blank=True, null=True)
#     # year = models.CharField(db_column='Year',max_length=100,blank=True,null=True)
#     remark = models.TextField(db_column='Remark', null=True)
#     t_date=models.DateTimeField(db_column='T_date')
#     # status = models.CharField(db_column='Status', max_length=50,blank=True, null=True,default='INSERT')  # Field name made lowercase.
#     status = models.CharField(db_column='Status', max_length=50,blank=True, null=True,default='INSERT')  # Field name made lowercase.

#     class Meta:
#         managed = True
#         db_table = 'GuestLectures'



# class industrialVisit(models.Model):
#     id = models.AutoField(db_column='id', primary_key=True)
#     emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
#     date = models.DateField(db_column='Date')
#     industry = models.TextField(db_column='Industry', blank=True, null=True)
#     address = models.TextField(db_column='address',blank=True,null=True)
#     contact_person = models.CharField(db_column='contact_person',max_length=100,blank=True,null=True)
#     contact_number=models.CharField(db_column='contact_number',max_length=100,blank=True,null=True)
#     e_mail = models.CharField(db_column='e_mail',max_length=100,blank=True,null=True)
#     participants_no = models.IntegerField(db_column='No_Of_Participants', blank=True, null=True)
#     # year = models.CharField(db_column='Year',max_length=100,blank=True,null=True)
#     # faculty_coordinator = models.ForeignKey(EmployeePrimdetail,db_column='Faculty_Coordinator', related_name='n1Faculty', blank=True, null=True,on_delete=models.SET_NULL)
#     remark = models.TextField(db_column='Remark', null=True)
#     t_date=models.DateTimeField(db_column='T_date')
#     status = models.CharField(db_column='Status', max_length=50,blank=True, null=True,default='INSERT')  # Field name made lowercase.

#     class Meta:
#         managed = True
#         db_table = 'IndustrialVisit'


# class eventsorganized(models.Model):
#     id = models.AutoField(db_column='id', primary_key=True)
#     emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
#     category = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,null=True,related_name='n1Category_event', db_column='Category')  # Field name made lowercase.
#     type = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,null=True, related_name='n1Type_event',db_column='Type')  # Field name made lowercase.
#     from_date = models.DateField(db_column='From_Date')  # Field name made lowercase.
#     to_date = models.DateField(db_column='To_Date')  # Field name made lowercase.
#     # role = models.ForeignKey(AarDropdown, models.DO_NOTHING,related_name='n1Role_event', db_column='Role')  # Field name made lowercase.
#     organization_sector = models.ForeignKey(AarDropdown,on_delete=models.SET_NULL,null=True,related_name='n1OrganizationSector_event', db_column='Organization_Sector')  # Field name made lowercase.
#     incorporation_status = models.ForeignKey(AarDropdown,on_delete=models.SET_NULL,null=True,related_name='n1IncorporationStatus_evnt', db_column='Incorporation_Type')  # Field name made lowercase.
#     title = models.TextField(db_column='Title')  # Field name made lowercase.
#     venue = models.CharField(db_column='Venue', max_length=100)  # Field name made lowercase.
#     participants = models.IntegerField(db_column='Participants')  # Field name made lowercase.
#     organizers = models.CharField(db_column='Organizers', max_length=100)  # Field name made lowercase.
#     attended = models.CharField(db_column='Attended', max_length=50)  # Field name made lowercase.
#     collaboration = models.CharField(db_column='Collaborations', max_length=50)  # Field name made lowercase.
#     sponsership = models.CharField(db_column='Sponsership', max_length=50)  # Field name made lowercase.
#     description=models.TextField(db_column='description', null=True)
#     t_date=models.DateTimeField(db_column='T_date')
#     status = models.CharField(db_column='Status', max_length=50,blank=True, null=True,default='INSERT')  # Field name made lowercase.
#     class Meta:
#         managed = True
#         db_table = 'eventsorganized'

# class MouSigned(models.Model):
#     sno=models.AutoField(db_column='sno',primary_key=True)
#     emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
#     date=models.DateField(null=True,blank=True)
#     organization=models.TextField(db_column='organization')
#     objective=models.TextField(db_column='objective')
#     valid_upto=models.DateField(null=True,blank=True)
#     contact_number=models.CharField(max_length=20,db_column='contact')
#     e_mail=models.EmailField()
#     intro=models.TextField(db_column='intro',null=True,default='')
#     document=models.FileField(null=True,blank=True)
#     t_date=models.DateTimeField(db_column='T_date')
#     status = models.CharField(db_column='Status', max_length=50,blank=True, null=True,default='INSERT')  # Field name made lowercase.
#     class Meta:
#         managed=True
#         db_table='mousigned'

class AarCoordinator(models.Model):
    id = models.AutoField(primary_key=True)
    sno = models.CharField(db_column='sno',max_length=100)
    emp_id=models.CharField(db_column='emp_id', max_length=150)
    pid=models.CharField(max_length=100)
    field=models.CharField(max_length=100,null=True,blank=True)
    value = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'aar_coordinator'

class AarMultiselect(models.Model):
    id = models.AutoField(primary_key=True)
    sno = models.CharField(db_column='sno',max_length=100)
    emp_id=models.CharField(db_column='emp_id', max_length=150)
    type=models.CharField(db_column='type', max_length=100)
    field=models.CharField(db_column='field', max_length=100,null=True,blank=True)
    value = models.CharField(db_column='value', max_length=100,null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'aar_multiselect'

# class Achievement(models.Model):
#     sno = models.AutoField(primary_key=True)
#     emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
#     category = models.ForeignKey(AarDropdown,on_delete=models.SET_NULL, null=True, db_column='category',related_name='n1Category')
#     description = models.TextField()
#     type=models.CharField(max_length=100)
#     t_date=models.DateTimeField(db_column='T_date')
#     date = models.DateField()
#     status = models.CharField(db_column='Status', max_length=50,blank=True, null=True,default='INSERT')  # Field name made lowercase.


#     class Meta:
#         managed = True
#         db_table = 'achievement'

# class Hobbyclub(models.Model):
#     sno = models.AutoField(primary_key=True)
#     emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id',null=True,on_delete=models.SET_NULL)
#     club_name = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL,null=True, db_column='club_name',related_name='n1Club_Name')
#     project_title = models.TextField()
#     start_date = models.DateField()
#     end_date = models.DateField()
#     project_incharge = models.ForeignKey(EmployeePrimdetail, on_delete=models.SET_NULL,null=True, db_column='project_incharge',related_name='n1Project_Incharge')
#     team_size = models.IntegerField()
#     project_description = models.TextField()
#     project_cost = models.IntegerField()
#     project_outcome = models.TextField()
#     t_date=models.DateTimeField(db_column='T_date')
#     status = models.CharField(db_column='Status', max_length=50,blank=True, null=True,default='INSERT')  # Field name made lowercase.

#     class Meta:
#         managed = True
#         db_table = 'hobbyclub'


# class SummerWinterSchool(models.Model):
#     sno = models.AutoField(primary_key=True)
#     emp_id=models.ForeignKey(EmployeePrimdetail,db_column='emp_id', related_name='summer_emp_id',null=True,on_delete=models.SET_NULL)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     resource_person = models.CharField(max_length=100)
#     resource_person_id = models.ForeignKey(EmployeePrimdetail,db_column='resource_person_id', on_delete=models.SET_NULL, related_name='resource_person_id', null=True)
#     topic = models.TextField()
#     participant_number = models.IntegerField()
#     participant_fee = models.IntegerField()
#     t_date=models.DateTimeField(db_column='T_date')
#     status = models.CharField(db_column='Status', max_length=50,blank=True, null=True,default='INSERT')  # Field name made lowercase.

#     class Meta:
#         managed = True
#         db_table = 'summer_winter_school'

class AarIncrementSettings(models.Model):
    salary_type = models.ForeignKey(AccountsDropdown, db_column='salary_type',null=True,on_delete=models.SET_NULL)
    increment_type = models.CharField(db_column='increment_type', max_length=50, blank=True)
    value_type = models.CharField(db_column='value_type', max_length=50, blank=True)
    value = models.FloatField()
    status = models.CharField(db_column='Status', max_length=50,blank=True, default='INSERT')
    t_date=models.DateTimeField(db_column='T_date')
    emp_category = models.ForeignKey(EmployeeDropdown, related_name='Aar_Emp_Category', blank=True, null=True,db_column='emp_category', limit_choices_to={'Field':'CATEGORY OF EMPLOYEE'},on_delete=models.SET_NULL)  # Field name made lowercase.
    desg = models.ForeignKey(EmployeeDropdown, related_name='Aar_designation',db_column='Desg', blank=True, null=True, limit_choices_to={'Field':'DESIGNATION'},on_delete=models.SET_NULL)  # Field name made lowercase.
    cadre = models.ForeignKey(EmployeeDropdown, related_name='Aar_cadre',db_column='Cadre', blank=True, null=True, limit_choices_to={'Field':'CADRE'},on_delete=models.SET_NULL)  # Field name made lowercase.
    ladder = models.ForeignKey(EmployeeDropdown, related_name='Aar_ladder',db_column='Ladder', blank=True, null=True, limit_choices_to={'Field':'LADDER'},on_delete=models.SET_NULL)  # Field name made lowercase.
    edit_by = models.ForeignKey(EmployeePrimdetail,db_column='edit_by',null=True,on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'Aar_IncrementSettings'

class LockingUnlocking(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', max_length=20,related_name='LockingUnlockingAAR',null=True,on_delete=models.SET_NULL)
    fromDate = models.DateTimeField(db_column="fromDate")
    toDate = models.DateTimeField(db_column="toDate")
    status = models.CharField(db_column="status",default="INSERT",max_length=20)
    time_stamp = models.DateTimeField(db_column="time_stamp",auto_now=True)
    unlocked_by = models.ForeignKey(EmployeePrimdetail,db_column='unlocked_by', max_length=20,related_name= 'unlocked_by_aar', on_delete=models.SET_NULL,null=True)

    class Meta:
        db_table = 'Aar_lockingunlocking'
        managed = True

class AarPrevious_increment(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', max_length=20,related_name='AARprevIncr',null=True,on_delete=models.SET_NULL)
    year_2015=models.FloatField(default=None,null=True)
    year_2016=models.FloatField(default=None,null=True)
    year_2017=models.FloatField(default=None,null=True)
    
    class Meta:
        db_table = 'AarPrevious_increment'
        managed = True

class AarEvalutionCriteriaMaxMarks(models.Model):
    evalution_criteria = models.ForeignKey(AarDropdown,db_column='evalution_criteria', null=True,on_delete=models.SET_NULL)
    max_marks = models.IntegerField()
    status = models.CharField(db_column="status",default="INSERT",max_length=20)
    type = models.CharField(db_column="type",max_length=5)
    #### 'A' for assisstant, 'S' for support , 'E' for executive
    time_stamp = models.DateTimeField(db_column="time_stamp",auto_now=True)

    class Meta:
        db_table = 'Aar_Evalution_Creteria_Max_Marks'
        managed = True

class AarPart2QuesAns(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='ques_emp_id', max_length=20, on_delete=models.SET_NULL,null=True)
    ques = models.ForeignKey(AarDropdown,db_column='ques', null=True,on_delete=models.SET_NULL)
    answer = models.TextField(db_column="answer")
    employee_band = models.CharField(db_column = "employe_band", max_length = 200 , null = True)
    #type = models.
    time_stamp = models.DateTimeField(db_column="time_stamp",auto_now=True)

    class Meta:
        db_table = 'Aar_Part2_Questions_marks'
        managed = True

class AarPersonalParticulars(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='ques_emp_id', max_length=20, on_delete=models.SET_NULL,null=True)
    current_gross_salary = models.FloatField()

    class Meta:
        db_table = 'Aar_Personal_Particulars'
        managed = True

class AarPart2Marks(models.Model):
    employee_band = models.CharField(db_column = "employe_band", max_length = 200 , null = True)
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='ques_emp_id', max_length=20, on_delete=models.SET_NULL,null=True)
    evalution_criteria = models.ForeignKey(AarDropdown,db_column='evalution_criteria', null=True, on_delete=models.SET_NULL)
    marks = models.IntegerField()
    H_Id = models.CharField(db_column="H_Id", max_length=200, null = True)
    category = models.CharField(db_column='category', max_length=50,default='H') # H for HOD E for Employee
    remarks1 = models.CharField(db_column="remarks1", max_length=200)
    remarks2 = models.CharField(db_column="remarks2", max_length=200)
    time_stamp = models.DateTimeField(db_column="time_stamp",auto_now=True)

    class Meta:
        db_table = 'Aar_Part2_Marks'
        managed = True


class AarReportingStatus(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='ques_emp_id', max_length=20,related_name='emp_id_aar', on_delete=models.SET_NULL,null=True)
    status = models.CharField(db_column="status",default="INSERT",max_length=20)
    remark = models.CharField(db_column="remark",max_length=20)
    reportingLevel = models.IntegerField()
    approved_by = models.ForeignKey(EmployeePrimdetail,db_column='approved_by', max_length=20,related_name='approved_by', on_delete=models.SET_NULL,null=True)

    class Meta:
        db_table = 'Aar_Reporting_Status'
        managed = True

class AarPart2MarksDir(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='ques_emp_id', max_length=20, on_delete=models.SET_NULL,null=True)
    type = models.TextField(db_column="type", null=True) #amount_type=amount/percentage/null
    remarks = models.CharField(db_column="remarks", max_length=200, null=True)
    increment = models.TextField(db_column="increment", null=True)
    promoted_to = models.ForeignKey(EmployeeDropdown, db_column="promoted_to", max_length=200, on_delete=models.SET_NULL, null= True)
    status = models.TextField(db_column="status",  default='INCREMENT')
    increment_type=models.ForeignKey(AarDropdown, db_column='increment_type', max_length=50, on_delete=models.SET_NULL, null=True)
    promotion_amount = models.IntegerField(null = True)
    amount = models.IntegerField(null = True)
    
    class Meta:
        db_table = 'Aar_Part2_Marks_DIR'
        managed = True

class hodrecommendatedamount(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', max_length=20, on_delete=models.SET_NULL,null=True)
    type = models.TextField(db_column="type", null=True)
    increment_type=models.ForeignKey(AarDropdown, db_column='increment_type', max_length=50, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField(null = True)
    status = models.TextField(db_column="status",  default='INCREMENT')
    promoted_to = models.ForeignKey(EmployeeDropdown, db_column="promoted_to", max_length=200, on_delete=models.SET_NULL, null= True)
    increment = models.TextField(db_column="increment", null=True)
    promotion_amount = models.IntegerField(null = True)

    class Meta:
        db_table = 'aar_hodrecommendatedamount'
        managed = True

#################################### FACULTY APPRAISAL ###################


# class FacultyAppraisal(models.Model):
#     emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', on_delete=models.SET_NULL,null=True,related_name="part1_emp")
#     dept=models.ForeignKey(EmployeeDropdown, db_column="dept", on_delete=models.SET_NULL, null= True,related_name="part1_dept")
#     desg=models.ForeignKey(EmployeeDropdown, db_column="desg", on_delete=models.SET_NULL, null= True,related_name="part1_desg")
#     highest_qualification=models.CharField(null=True,max_length=200)
#     salary_type=models.ForeignKey(AccountsDropdown,null=True,on_delete=models.SET_NULL,related_name="part1_sal_type")
#     current_gross_salary=models.FloatField(null=True)
#     agp=models.FloatField(null=True)
#     total_experience=models.FloatField(null=True)
#     form_filled_status = models.CharField(max_length=5,default='N')
#     form_approved = models.CharField(max_length=5,default='N')
#     achievement_recognition=models.TextField(null=True)
#     training_needs=models.TextField(null=True)
#     suggestions=models.TextField(null=True)
#     # emp_place=models.CharField(max_length=200,default=None,null=True)
#     emp_date=models.DateField(default=None,null=True)
#     hod_date=models.DateField(default=None,null=True)
#     dean_date=models.DateField(default=None,null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)

#     class Meta:
#         db_table = 'FacAppPart1'
#         managed = True

# class FacAppCat1A1(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="cat1_a1")
#     course_paper = models.TextField(null=True)
#     lectues_calendar = models.IntegerField(null=True)
#     lectues_portal = models.IntegerField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0)
#     status = models.CharField(max_length=10,default="INSERT",null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    
#     class Meta:
#         db_table = 'FacAppCat1A1'
#         managed = True

# class FacAppCat1A2(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="cat1_a2")
#     course_paper = models.TextField(null=True)
#     consulted = models.TextField(null=True)
#     prescribed = models.TextField(null=True)
#     additional_resource = models.TextField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0)
#     status = models.CharField(max_length=10,default="INSERT",null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    
#     class Meta:
#         db_table = 'FacAppCat1A2'
#         managed = True

# class FacAppCat1A3(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="cat1_a3")
#     description = models.TextField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0)
#     short_descriptn = models.TextField(null=True)
#     status = models.CharField(max_length=10,default="INSERT",null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    
#     class Meta:
#         db_table = 'FacAppCat1A3'
#         managed = True

# class FacAppCat1A4(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="cat1_a4")
#     sno=models.IntegerField(null=True)
#     executed=models.FloatField(null=True)
#     extent_to_carried=models.FloatField(null=True)
#     duties_assign=models.IntegerField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0,null=True)
#     status = models.CharField(max_length=10,default="INSERT",null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    
#     class Meta:
#         db_table = 'FacAppCat1A4'
#         managed = True

# class FacAppCat2A1(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="cat2_a1")
#     type_of_activity=models.TextField(default=None,null=True)
#     average_hours = models.FloatField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0,null=True)
#     status = models.CharField(max_length=10,default="INSERT",null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    
#     class Meta:
#         db_table = 'FacAppCat2A1'
#         managed = True

# class FacAppCat3(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="cat3")
#     type=models.CharField(default='J',max_length=5)
#     ######### 'J' for research journal, 'C' for research conference, 'B' for books, 'PC' for project consultancy, 'PA' for patent, 'G' for research guidance, 'T' for training development, 'L' for lecture talks #########################################
#     research_journal = models.ForeignKey(Researchjournal,db_column="research_journal",on_delete=models.SET_NULL,null=True,related_name="app_res")
#     research_conference = models.ForeignKey(Researchconference,db_column="research_conference",on_delete=models.SET_NULL,null=True,related_name="app_conf")
#     books = models.ForeignKey(Books,db_column="books",on_delete=models.SET_NULL,null=True,related_name="app_book")
#     project_consultancy = models.ForeignKey(ProjectConsultancy,db_column="project_consultancy",on_delete=models.SET_NULL,null=True,related_name="app_project")
#     patent = models.ForeignKey(Patent,db_column="patent",on_delete=models.SET_NULL,null=True,related_name="app_patent")
#     research_guidance = models.ForeignKey(Researchguidence,db_column="research_guidance",on_delete=models.SET_NULL,null=True,related_name="app_res_guid")
#     training_development = models.ForeignKey(TrainingDevelopment,db_column="training_development",on_delete=models.SET_NULL,null=True,related_name="app_training")
#     lectures_talks = models.ForeignKey(LecturesTalks,db_column="lectures_talks",on_delete=models.SET_NULL,null=True,related_name="app_lecture")
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0,null=True)#Same value for all the same type of journals
#     status = models.CharField(max_length=10,default="INSERT",null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    
#     class Meta:
#         db_table = 'FacAppCat3'
#         managed = True

# class FacAppCat4A1(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="cat4_a1")
#     branch_details = models.TextField(null=True)
#     subject = models.CharField(max_length=200,null=True)
#     result_clear_pass=models.FloatField(null=True)
#     result_external=models.FloatField(null=True)
#     stu_below_40=models.IntegerField(null=True)
#     stu_40_49=models.IntegerField(null=True)
#     stu_50_59=models.IntegerField(null=True)
#     stu_above_60=models.IntegerField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0)
#     status = models.CharField(max_length=10,default="INSERT",null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    
#     class Meta:
#         db_table = 'FacAppCat4A1'
#         managed = True

# class FacAppCat4A2(models.Model):
#     fac_app_id = models.ForeignKey(FacultyAppraisal, db_column='fac_app_id', on_delete=models.SET_NULL,null=True,related_name="cat4_a2")
#     branch = models.TextField(max_length=100,null=True)
#     semester = models.CharField(max_length=25,null=True)
#     section = models.CharField(max_length=10,null=True)
#     subject = models.CharField(max_length=200,null=True)
#     overall_avg=models.FloatField(null=True)
#     student_feedback=models.FloatField(null=True)
#     score_claimed = models.FloatField(null=True)
#     score_awarded = models.FloatField(default=0,null=True)
#     status = models.CharField(max_length=10,default="INSERT",null=True)
#     time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
    
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
