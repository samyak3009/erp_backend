# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django_mysql.models import JSONField
from django.db import models
from login.models import AarDropdown,EmployeeDropdown,EmployeePrimdetail
from Accounts.models import AccountsDropdown
from Registrar.models import StudentDropdown

class AchFacPublishers(models.Model):
    publisher_name = models.TextField(db_column='publisher_name', null=True, blank=True)
    publisher_address_1 = models.TextField(db_column='publisher_address_1', null=True, blank=True)
    publisher_address_2 = models.TextField(db_column='publisher_address_2', null=True, blank=True)
    publisher_zip_code = models.CharField(db_column='publisher_zip_code',max_length=20, null=True, blank=True)
    publisher_contact = models.CharField(db_column='publisher_contact',max_length=50)
    publisher_email = models.CharField(db_column='publisher_email', max_length=200)
    publisher_website = models.CharField(db_column='publisher_website', max_length=200)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True,default="INSERT")
    time_stamp=models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        managed = True
        db_table = 'AchFac_Publishers'  

class AchFacBooks(models.Model): #CATEGORY = BOOK
    emp_id = models.ForeignKey(EmployeePrimdetail, null=True, on_delete=models.SET_NULL, db_column='emp_id', related_name='AchFacBooks_emp_id')
    role = models.ForeignKey(AarDropdown, null=True, on_delete=models.SET_NULL, db_column='role', related_name='AchFacBooks_role',default=None)
    role_for = models.ForeignKey(AarDropdown, null=True,on_delete=models.SET_NULL,related_name='AchFacBooks_role_for', db_column='role_for',default=None)
    book_title = models.TextField(db_column='book_title', null=True)
    book_edition = models.CharField(db_column='book_edition', null=True, blank=True, max_length=100)
    published_date = models.DateField(db_column='published_date', blank=True)
    isbn = models.CharField(db_column='isbn', max_length=100, null=True, blank=True)
    chapter = models.TextField(db_column='chapter', null=True, blank=True)
    author = models.ForeignKey(AarDropdown, null=True, on_delete= models.SET_NULL, db_column='author', related_name='AchFacBooks_author', default=None)
    copyright_status = models.ForeignKey(AarDropdown, null=True,on_delete=models.SET_NULL,related_name='AchFacBooks_copyright_status', db_column='copyright_status',default=None)
    copyright_no = models.CharField(db_column='copyright_no', max_length=100, null=True, blank=True)
    publisher_type = models.ForeignKey(AarDropdown, null=True, on_delete=models.SET_NULL, related_name='AchFacBooks_publisher_type', limit_choices_to={'field':'PUBLISHER TYPE'}, db_column='publisher_type', default=None)
    publisher_details = models.ForeignKey(AchFacPublishers,related_name='AchFacBooks_publisher_details', on_delete=models.SET_NULL, db_column='publisher_details',null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True,default="INSERT")
    time_stamp=models.DateTimeField(db_column='time_stamp', auto_now=True)
    class Meta:
        managed = True
        db_table = 'AchFac_Books'

class AchFacConferenceDetail(models.Model):
    conference_title = models.TextField(db_column='conference_title', null=True)
    type_of_conference = models.ForeignKey(AarDropdown,related_name='AchConferenceDetail_type_of_conference', on_delete=models.SET_NULL,null=True, db_column='type_of_conference')
    conference_from = models.DateField(db_column='conference_from')
    conference_to = models.DateField(db_column='conference_to')
    organized_by = models.TextField(db_column='organized_by', null=True)
    # organized_by = models.ForeignKey(AarDropdown,related_name='AchConferenceDetail_organized_by', on_delete=models.SET_NULL,null=True, db_column='organized_by')
    other = models.CharField(db_column='organized_by_other', max_length=100, null=True, blank=True)
    type_of_activity = models.ForeignKey(AarDropdown,related_name='AchConferenceDetail_type_of_activity', on_delete=models.SET_NULL,null=True, db_column='type_of_activity')
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True,default="INSERT")
    time_stamp=models.DateTimeField(db_column='time_stamp', auto_now=True)
    class Meta:
        managed = True
        db_table = 'AchFac_ConferenceDetail'

class AchFacConferences(models.Model): #CATEGORY = CONFERENCE
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', related_name="AchFacConferences_emp_id", null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown, related_name='AchFacConferences_category', on_delete=models.SET_NULL, db_column='category',null=True)
    conference_detail = models.ForeignKey(AchFacConferenceDetail,related_name='AchFacConferences_conference_detail', on_delete=models.SET_NULL,null=True, db_column='conference_detail')
    sub_category = models.ForeignKey(AarDropdown, related_name='AchFacConferences_sub_category', on_delete=models.SET_NULL, null=True, db_column='sub_category')
    paper_title = models.TextField(db_column='paper_title', null=True)
    published_date = models.CharField(db_column='published_date', max_length=100,null=True, blank=True)
    journal_name = models.TextField(db_column='journal_name',null=True)
    volume_no = models.TextField(db_column='volume_no',null=True)
    issue_no = models.CharField(db_column='issue_no', max_length=100, null=True, blank=True)
    isbn = models.CharField(db_column='isbn', max_length=100,null=True, blank=True)
    page_no = models.CharField(db_column='page_no', max_length=100, null=True, blank=True)
    author = models.ForeignKey(AarDropdown,related_name='AchFacConferences_author', on_delete=models.SET_NULL, db_column='Author',null=True)
    other_description = models.TextField(db_column='other_description', null=True)
    publisher_details = models.ForeignKey(AchFacPublishers,related_name='AchFacConferences_publisher_details', on_delete=models.SET_NULL, db_column='publisher_details',null=True)
    others=models.CharField(db_column='other_conference', max_length=100, null=True, blank=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True,default="INSERT")
    time_stamp=models.DateTimeField(db_column='time_stamp', auto_now=True)
    # Take sponsers in AchFachmultiDetails
    class Meta:
        managed = True
        db_table = 'AchFac_Conferences'

class AchFacGuidances(models.Model): #CATEGORY = GUIDANCE
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name='AchFacGuidances_emp_id', db_column='emp_id', null=True, blank=True, on_delete=models.SET_NULL)
    guidance_for = models.ForeignKey(AarDropdown, related_name='AchFacGuidances_guidance_for', on_delete= models.SET_NULL, null=True, blank=True, db_column='guidance_for')
    course = models.ForeignKey(StudentDropdown, related_name='AchFacGuidances_course', on_delete=models.SET_NULL, db_column='course', blank=True, null=True)
    degree = models.ForeignKey(StudentDropdown, related_name='AchFacGuidances_degree', on_delete=models.SET_NULL, db_column='degree', blank=True, null=True)
    guidance_awarded_status = models.CharField(db_column='guidance_awarded_status', max_length=100, blank=True, null=True)#YES OR NO
    university_type = models.ForeignKey(AarDropdown, related_name='AchFacGuidances_university_type', on_delete= models.SET_NULL, db_column='university_type', blank=True, null=True)
    university_name = models.CharField(db_column='AchFacGuidances_university_type', max_length=100, blank=True, null=True)
    guidance_status = models.ForeignKey(AarDropdown, related_name='AchFacGuidances_guidance_status', on_delete=models.SET_NULL, db_column='guidance_status', blank=True, null=True)
    no_of_students = models.IntegerField(db_column='no_of_students', blank=True, null=True)
    project_title = models.TextField(db_column='project_title', blank=True, null=True)
    area_of_specification = models.TextField(db_column='area_of_specification',  blank=True, null=True)
    date_of_guidance = models.DateField(db_column='date_of_guidance',null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True,default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        managed = True
        db_table = 'AchFac_Guidance'

class AchFacJournalDetail(models.Model):
    journal_name = models.TextField(db_column='journal_name', null=True,  blank=True)
    type_of_journal = models.ForeignKey(AarDropdown, related_name='AchFacJournalDetail_type_of_journal', on_delete=models.SET_NULL,null=True, blank=True, db_column='type_of_journal')
    sub_category = models.ForeignKey(AarDropdown, related_name='AchFacJournalDetail_sub_category', on_delete=models.SET_NULL,null=True, blank=True, db_column='sub_category')
    volume_no = models.TextField(db_column='volume_no', null=True, blank=True)
    issue_no = models.CharField(db_column='issue_no', max_length=100, null=True, blank=True)
    isbn = models.CharField(db_column='isbn', max_length=100, blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True,default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        managed = True
        db_table = 'AchFac_JournalDetail'

class AchFacJournals(models.Model): #CATEGORY = JOURNAL
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', related_name='AchFacJournals_emp_id', null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown, related_name='AchFacJournals_category', on_delete=models.SET_NULL, null=True, blank=True, db_column='category')
    author = models.ForeignKey(AarDropdown, related_name='AchFacJournals_author', on_delete=models.SET_NULL, null=True,  blank=True, db_column='author')
    published_date = models.DateField(db_column='published_date', blank=True, null=True)
    paper_title = models.TextField(db_column='paper_title', blank=True, null=True)
    impact_factor = models.FloatField(db_column='impact_factor', blank=True, null=True)
    page_no = models.CharField(db_column='page_no', max_length=100, blank=True, null=True)
    journal_details = models.ForeignKey(AchFacJournalDetail, related_name='AchFacJournals_journal_details',  on_delete=models.SET_NULL, db_column='journal_details', null=True,  blank=True)
    publisher_details = models.ForeignKey(AchFacPublishers, related_name='AchFacJournals_publisher_details',  on_delete=models.SET_NULL, db_column='publisher_details', null=True,  blank=True)
    others = models.CharField(db_column='other', max_length=100, blank=True, null=True)
    status = models.CharField(db_column='status', max_length=100, default='INSERT', blank=True, null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    class Meta:
        managed = True
        db_table = 'AchFac_Journals'

class AchFacLecturesTalksVenue(models.Model):
    venue = models.TextField(db_column='venue' ,blank=True, null=True)
    address = models.TextField(db_column='address' ,blank=True, null=True)
    pin_code = models.CharField(db_column='pin_code',max_length=50 ,blank=True, null=True)
    contact_number = models.CharField(db_column='contact_number',max_length=50 ,blank=True, null=True)
    e_mail = models.CharField(db_column='e_mail', max_length=50 ,blank=True, null=True)
    website = models.CharField(db_column='website',max_length=50 ,blank=True, null=True)
    status = models.CharField(db_column='status', max_length=100, default='INSERT', blank=True, null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        managed=True
        db_table='AchFac_LecturesTalksVenue'

class AchFacLecturesTalks(models.Model): #CATEGORY = LECTURE N TALKS
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', related_name='AchFacLecturesTalks_emp_id', on_delete=models.SET_NULL, blank=True, null=True)
    category = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, blank=True, null=True, related_name='AchFacLecturesTalks_category', db_column='category')
    type_of_event = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, blank=True, null=True, related_name='AchFacLecturesTalks_type_of_event', db_column='type_of_event')
    organization_sector = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, blank=True, null=True, related_name='AchFacLecturesTalks_organization_sector', db_column='organization_sector')
    incorporation_status = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacLecturesTalks_incorporation_status', db_column='incorporation_status')
    role = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, blank=True, null=True, related_name='AchFacLecturesTalks_role', db_column='role')
    venue_detail = models.ForeignKey(AchFacLecturesTalksVenue, on_delete=models.SET_NULL, blank=True, null=True, related_name='AchFacLecturesTalks_venue_detail', db_column='venue_detail')
    date = models.DateField(db_column='date', blank=True, null=True)
    topic = models.TextField(db_column='topic', blank=True, null=True)
    participants = models.IntegerField(db_column='participants', blank=True, null=True)
    status = models.CharField(db_column='status', max_length=100, default='INSERT', blank=True, null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        managed=True
        db_table='AchFac_LecturesTalks'

class AchFacPatentDetail(models.Model):
    patent_title = models.TextField(db_column='patent_title', null=True, blank=True)
    patent_description = models.TextField(db_column='patent_description', null=True, blank=True)
    level = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacPatentDetail_level', db_column='level')
    patent_status = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacPatentDetail_patent_status', db_column='patent_status')
    patent_number = models.CharField(db_column='patent_number', max_length=150, blank=True, null=True)
    patent_applicant_name = models.CharField(db_column='applicant_name', null=True, blank=True , max_length=150 ,default="SELF") #SELF/OTHER
    patent_co_applicant_name = models.CharField(db_column='co_applicant_name', null=True, blank=True , max_length=150 , default="SELF") #SELF/OTHER
    patent_applicant_name_other = models.CharField(db_column='applicant_name_other', null=True, blank=True , max_length=150)
    patent_co_applicant_name_other = models.CharField(db_column='co_applicant_name_other', null=True, blank=True , max_length=150)
    application_no = models.CharField(db_column='application_no', max_length=150, blank=True, null=True)
    owner = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, related_name='AchFacPatentDetail_owner', db_column='owner')
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    # Take discipline from AchFacMultiDetails
    
    class Meta:
        managed=True
        db_table='AchFac_PatentDetail'

class AchFacPatents(models.Model): #CATEGORY = PATENT
    emp_id = models.ForeignKey(EmployeePrimdetail, db_column='emp_id', related_name='AchFacPatents_emp_id', null=True, blank=True, on_delete=models.SET_NULL)
    patent_details = models.ForeignKey(AchFacPatentDetail, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacPatents_patent_details', db_column='patent_details')
    patent_date = models.DateField(db_column='patent_date', blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    class Meta:
        managed = True
        db_table = 'AchFac_Patents'

class AchFacPatentCollaborator(models.Model):
    patent_in = models.ForeignKey(AchFacPatents, on_delete=models.SET_NULL, related_name='AchFacPatentCollaborator_patent_in', db_column='patent_in',blank=True, null=True)
    company_name = models.CharField(db_column='company_name', max_length=50, blank=True, null=True)
    incorporate_status = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,null=True,related_name='AchFacPatentCollaborator_incorporate_status', db_column='incorporate_status',blank=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True,default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    class Meta:
        managed=True
        db_table='AchFac_PatentCollaborator'

class AchFacTrainings(models.Model):     #TRAINING
    emp_id=models.ForeignKey(EmployeePrimdetail, db_column='emp_id', related_name='AchFacTrainings_emp_id', null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacTrainings_category', db_column='category')
    training_type = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacTrainings_training_type', db_column='training_type')
    training_sub_type = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacTrainings_training_sub_type', db_column='training_sub_type')
    role = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacTrainings_role', db_column='role')
    organization_sector = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacTrainings_organization_sector', db_column='organization_sector')
    incorporation_type = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacTrainings_incorporation_type', db_column='incorporation_type')
    from_date = models.DateField(db_column='from_date', null=True, blank=True)
    to_date = models.DateField(db_column='to_date', null=True, blank=True)
    title = models.TextField(db_column='title', null=True, blank=True)
    venue = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacTrainings_venue', db_column='venue')
    venue_other = models.CharField(db_column='venue_other', null=True, blank=True, max_length=100)
    other = models.CharField(db_column='other', null=True, blank=True, max_length=100)
    participants = models.IntegerField(db_column='participants', null=True, blank=True)
    organizers = models.TextField(db_column='organizers', null=True, blank=True)
    attended = models.CharField(db_column='attended', null=True, blank=True, max_length=50)
    collaborations = models.CharField(db_column='collaborations', null=True, blank=True, max_length=50, default="NO")
    sponsership = models.CharField(db_column='sponsership', null=True, blank=True, max_length=50, default="NO")
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    # Take discipline from AchFacMultiDetails

    class Meta:
        managed = True
        db_table = 'AchFac_Trainings'

class AchFacProjects(models.Model): #CATEGORY = PROJECT
    emp_id=models.ForeignKey(EmployeePrimdetail, related_name='AchFacProjects_emp_id', db_column='emp_id', blank=True, null=True, on_delete=models.SET_NULL)
    project_type = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacProjects_project_type',db_column='project_type')
    project_status = models.ForeignKey(AarDropdown,  on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacProjects_project_status', db_column='project_status')
    sector = models.ForeignKey(AarDropdown, on_delete=models.SET_NULL, null=True, blank=True, related_name='AchFacProjects_sector', db_column='sector')
    project_title = models.TextField(db_column='project_title', null=True, blank=True)
    project_description = models.TextField(db_column='project_description', null=True, blank=True)
    start_date = models.DateField(db_column='start_date', null=True, blank=True)
    end_date = models.DateField(db_column='end_date', blank=True, null=True)
    principal_investigator = models.CharField(db_column='principal_investigator', null=True, blank=True, max_length=100, default="SELF")# "SELF" / "OTHER"
    co_principal_investigator = models.CharField(db_column='co_principal_investigator', null=True, blank=True, max_length=100, default="SELF")# "SELF" / "OTHER"
    principal_investigator_other = models.CharField(db_column='principal_investigator_other', null=True, blank=True, max_length=100)
    co_principal_investigator_other = models.CharField(db_column='co_principal_investigator_other', null=True, blank=True, max_length=100)
    team_size = models.IntegerField(db_column='team_size', null=True, blank=True)
    sponsored = models.CharField(db_column='sponsored', max_length=50, null=True, blank=True, default="NO")# YES/NO
    association = models.CharField(db_column='association', max_length=50, null=True, blank=True, default="NO")# YES/NO
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    # Take discipline from AchFacMultiDetails

    class Meta:
        managed = True
        db_table = 'AchFac_Projects'

class AchFacMultiDetails(models.Model):
    details_for = models.CharField(db_column='details_for', max_length=50, null=True, blank=True) ####### form category ######
    # RESEARCH PAPER IN CONFERENCE,PATENT,TRAINING AND DEVELOPMENT PROGRAM,PROJECTS/CONSULTANCY
    key_id = models.IntegerField(db_column='key_id', null=True, blank=True) ###### row id #########
    detail_text = models.CharField(db_column='detail_text', max_length=50, null=True, blank=True) ######## sponsers text ######
    detail_emp = models.ForeignKey(EmployeeDropdown, on_delete=models.SET_NULL, null=True, related_name='Discipline_detail_emp', db_column='detail_emp', blank=True)
    
    class Meta:
        managed = True
        db_table = 'AchFac_MultiDetails'

class AchFacSponser(models.Model):
    organisation=models.CharField(db_column='organisation', max_length=100, blank=True, null=True)
    pin_code=models.CharField(db_column='pin_code', max_length=100, blank=True, null=True)
    address=models.TextField(db_column='address', blank=True, null=True)
    contact_person=models.CharField(db_column='contact_person', max_length=100, blank=True, null=True)
    contact_number=models.CharField(db_column='contact_number', max_length=100, blank=True, null=True)
    e_mail=models.CharField(db_column='e_mail', max_length=100, blank=True, null=True)
    website=models.CharField(db_column='website', max_length=100, blank=True, null=True)
    amount=models.CharField(db_column='amount', max_length=100, blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        managed = True
        db_table = 'AchFac_Sponser'

class AchFacCollaborators(models.Model):
    organisation=models.CharField(db_column='organisation', max_length=100, blank=True, null=True)
    pin_code=models.CharField(db_column='pin_code', max_length=100, blank=True, null=True)
    address=models.TextField(db_column='address', blank=True, null=True)
    contact_person=models.CharField(db_column='contact_person', max_length=100, blank=True, null=True)
    contact_number=models.CharField(db_column='contact_number', max_length=100, blank=True, null=True)
    e_mail=models.CharField(db_column='e_mail', max_length=100, blank=True, null=True)
    website=models.CharField(db_column='website', max_length=100, blank=True, null=True)
    amount=models.CharField(db_column='amount', max_length=100, blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'AchFac_Collaborators'

class AchFacAssociations(models.Model):
    organisation=models.CharField(db_column='organisation', max_length=100, blank=True, null=True)
    pin_code=models.CharField(db_column='pin_code', max_length=100, blank=True, null=True)
    address=models.TextField(db_column='address', blank=True, null=True)
    contact_person=models.CharField(db_column='contact_person', max_length=100, blank=True, null=True)
    contact_number=models.CharField(db_column='contact_number', max_length=100, blank=True, null=True)
    e_mail=models.CharField(db_column='e_mail', max_length=100, blank=True, null=True)
    website=models.CharField(db_column='website', max_length=100, blank=True, null=True)
    amount=models.CharField(db_column='amount', max_length=100, blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'AchFac_Associations'

class AchFacMapIds(models.Model):
    key_type=models.TextField(db_column="key_type" ,blank=True, null=True)# SPONSORS,ASSOCIATIONS,COLLABORATORS
    key_id=models.IntegerField(db_column="key_id" ,blank=True, null=True)
    form_id=models.IntegerField(db_column="form_id" ,blank=True, null=True)
    form_type=models.TextField(db_column='form_type', blank=True, null=True)# TRAINING AND DEVELOPMENT PROGRAM,PROJECTS/CONSULTANCY
    status=models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  
    time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)

    class Meta:
        managed = True
        db_table = 'AchFac_Map_Ids'

class AchFacApproval(models.Model):
	level=models.IntegerField(db_column='level', blank=True, null=True)
	approval_category = models.CharField(db_column='approval_category', max_length=40, blank=True, null=True, default=None)
    # BOOKS,RESEARCH PAPER IN CONFERENCE,RESEARCH GUIDANCE / PROJECT GUIDANCE,RESEARCH PAPER IN JOURNAL,PATENT,LECTURES AND TALKS,TRAINING AND DEVELOPMENT PROGRAM,PROJECTS/CONSULTANCY
	approval_id = models.IntegerField(db_column='approval_id', blank=True, null=True)
	approved_by = models.ForeignKey(EmployeePrimdetail,related_name="AchFacApproval_approved_by",db_column="approved_by",null=True,on_delete=models.SET_NULL)
	approval_status=models.CharField(db_column='approval_status', max_length=40, blank=True, null=True, default="PENDING")
    # APPROVED,REJECTED,PENDING,DELETE
	status=models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  
	time_stamp=models.DateTimeField(db_column='time_stamp',auto_now=True)
	
	class Meta:
		db_table="AchFac_Approval"
		managed=True


class AchFacDesign(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name='AchFacDesign_emp_id', db_column='emp_id', blank=True, null=True, on_delete=models.SET_NULL)
    design_title = models.TextField(db_column='title', null=True, blank=True)
    design_description = models.TextField(db_column='description', null=True, blank=True)
    design_applicant_name = models.CharField(db_column='applicant_name', null=True, blank=True , max_length=150 ,default="SELF") #SELF/OTHER
    design_co_applicant_name = models.CharField(db_column='co_applicant_name', null=True, blank=True , max_length=150 , default="SELF") #SELF/OTHER
    design_applicant_name_other = models.CharField(db_column='applicant_name_other', null=True, blank=True , max_length=150)
    design_co_applicant_name_other = models.CharField(db_column='co_applicant_name_other', null=True, blank=True , max_length=150)
    design_company_name = models.TextField(db_column='company_name', null=True, blank=True)
    design_incorporate_status = models.ForeignKey(AarDropdown,related_name="design_incorporate_status",db_column='incorporation_type', null=True, blank=True,on_delete=models.SET_NULL)
    design_level = models.ForeignKey(AarDropdown,related_name="design_level",db_column='level', null=True, blank=True,on_delete=models.SET_NULL)
    design_status= models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,related_name="design_status",db_column='design_status', null=True, blank=True)
    design_application_no = models.CharField(db_column='application_no', max_length=150, blank=True, null=True)
    design_date = models.DateField(db_column='Date', null=True, blank=True)
    design_owner= models.ForeignKey(AarDropdown, on_delete=models.SET_NULL,related_name="design_owner",db_column='owner', null=True, blank=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp',auto_now=True)
    
    class Meta:
        db_table="AchFac_Design"
        managed=True

class AchFacActivityDetails(models.Model):    
    act_main_org = models.ForeignKey(EmployeeDropdown,related_name='Coordinator_organisation',db_column='Main_Coordinator_org', null=True, blank=True , max_length=150,on_delete=models.SET_NULL)
    act_main_dept = JSONField(db_column='Main_Coordinator_dept', null=True, blank=True , max_length=150)
    act_main_category = JSONField(db_column='Main_Coordinator_category', null=True, blank=True , max_length=150,default="FACULTY")
    act_main_emp_id = JSONField(db_column='Main_Coordinator', blank=True, null=True)
    
    act_co_org = models.ForeignKey(EmployeeDropdown,related_name='CO_Coordinator_org',db_column='Co_Coordinator_org', null=True, blank=True , max_length=150,on_delete=models.SET_NULL)
    act_co_dept = JSONField(db_column='Co_Coordinator_dept', null=True, blank=True , max_length=150)
    act_co_category = JSONField(db_column='Co_Coordinator_category', null=True, blank=True , max_length=150 , default="FACULTY")
    act_co_emp_id = JSONField(db_column='Co_Coordinator', blank=True, null=True)

    class Meta:
        db_table="AchFac_ActivityDetails"
        managed=True

class AchFacActivity(models.Model):
    act_level = models.ForeignKey(AarDropdown,related_name='Activity_Level',db_column='level', null=True, blank=True , max_length=150,on_delete=models.SET_NULL)
    act_type = models.ForeignKey(AarDropdown,related_name='activity_Type',db_column='activity_type', null=True, blank=True , max_length=150,on_delete=models.SET_NULL)
    act_sub_type = models.ForeignKey(AarDropdown,related_name='Activity_SubCategory',db_column='sub_category', null=True, blank=True , max_length=150,on_delete=models.SET_NULL)
    
    act_start_date = models.DateField(db_column='start_date', null=True, blank=True)
    act_end_date = models.DateField(db_column='end_date', blank=True, null=True)
    
    act_description = models.TextField(db_column='description', null=True, blank=True)
    
    coord_detail = models.ForeignKey(AchFacActivityDetails,related_name='Activity_coord_detail', on_delete=models.SET_NULL, db_column='coord_detail',null=True)
    
    act_added_by = models.ForeignKey(EmployeePrimdetail, related_name='AchFacActivity_added_by_emp_id', db_column='added_by', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp',auto_now=True)

    class Meta:
        db_table="AchFac_Activity"
        managed=True
