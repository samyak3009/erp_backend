# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from login.models import EmployeePrimdetail,EmployeeDropdown,AuthUser
from musterroll.models import EmployeePerdetail


class WebDeptData(models.Model):
    Id = models.AutoField(db_column='webdataID', primary_key=True)
    Type = models.ForeignKey(EmployeeDropdown,db_column='Type', null =True,related_name='webdatatype',on_delete=models.SET_NULL)
    Dept =models.ForeignKey(EmployeeDropdown,db_column='dept', null =True, related_name='webdatadept', max_length=20,  blank=True,on_delete=models.SET_NULL)
    text=models.CharField(db_column='Text',null =True, max_length=10000)
    links=models.CharField(db_column='links',null =True, max_length=10000)
    Fdate = models.DateField(null =True)
    Tdate = models.DateField(null =True)
    pmail = models.ForeignKey(AuthUser,db_column='username',null=True,related_name='webcordinator',on_delete=models.SET_NULL)
    status = models.CharField(db_column='Status', max_length=45,null =True,)

    class Meta:
        managed= False
        db_table = 'WebDeptData'

class WebDeptData2(models.Model):
    Id=models.AutoField(db_column='webdataID', primary_key=True)
    Type=models.ForeignKey(EmployeeDropdown,db_column='Type', null =True,related_name='webdatatype2',on_delete=models.SET_NULL)
    Dept=models.ForeignKey(EmployeeDropdown,db_column='dept', null =True, related_name='webdatadept2', max_length=20,  blank=True,on_delete=models.SET_NULL)
    title=models.CharField(db_column='Title',null =True, max_length=500,blank=True)
    text=models.CharField(db_column='Text',null =True, max_length=10000,blank=True)
    pmail=models.ForeignKey(AuthUser,db_column='username',null=True,related_name='webcordinator2',blank=True,on_delete=models.SET_NULL)
    status=models.CharField(db_column='Status', max_length=45,null =True,blank=True)
    priority=models.CharField(db_column='Priority', max_length=45,null =True,blank=True)
    related_pmail=models.CharField(db_column='related_pmail', max_length=1000,blank=True)
    lab_place=models.CharField(db_column='lab_place',null =True,blank=True, max_length=50)
    image=models.CharField(max_length=500, blank=True, null=True)
    links=models.CharField(db_column='links',null =True, max_length=500,blank=True)

    class Meta:
        managed=False
        db_table = 'WebDeptData2'

class AdApplications(models.Model):
    autoid = models.AutoField(db_column='AutoId', primary_key=True)  # Field name made lowercase.
    aadhaarno = models.CharField(max_length=20)
    name = models.CharField(db_column='Name', max_length=200)  # Field name made lowercase.
    father = models.CharField(db_column='Father', max_length=200)  # Field name made lowercase.
    mother = models.CharField(db_column='Mother', max_length=200)  # Field name made lowercase.
    fatheroccu = models.CharField(db_column='fatherOccu', max_length=500)  # Field name made lowercase.
    dob = models.CharField(db_column='DOB', max_length=50)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=50)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=10)  # Field name made lowercase.
    upseestatus = models.CharField(db_column='UPSEEStatus', max_length=5)  # Field name made lowercase.
    upseequalified = models.CharField(db_column='UPSEEQualified', max_length=2, blank=True, null=True)  # Field name made lowercase.
    upseerollno = models.CharField(db_column='UPSEERollNo', max_length=50)  # Field name made lowercase.
    upseerank = models.CharField(db_column='UPSEERank', max_length=50)  # Field name made lowercase.
    jeestatus = models.CharField(db_column='JEEStatus', max_length=5)  # Field name made lowercase.
    jeerollno = models.CharField(db_column='JEERollNo', max_length=50)  # Field name made lowercase.
    jeerank = models.CharField(db_column='JEERank', max_length=50)  # Field name made lowercase.
    courseapplied = models.CharField(db_column='CourseApplied', max_length=50)  # Field name made lowercase.
    choice1 = models.CharField(db_column='Choice1', max_length=50)  # Field name made lowercase.
    choice2 = models.CharField(db_column='Choice2', max_length=50)  # Field name made lowercase.
    choice3 = models.CharField(db_column='Choice3', max_length=50)  # Field name made lowercase.
    board10 = models.CharField(db_column='Board10', max_length=1000)  # Field name made lowercase.
    rollno10 = models.CharField(db_column='RollNo10', max_length=50)  # Field name made lowercase.
    school10 = models.CharField(db_column='School10', max_length=1000)  # Field name made lowercase.
    year10 = models.IntegerField(db_column='Year10')  # Field name made lowercase.
    marksstatus10 = models.CharField(db_column='MarksStatus10', max_length=5)  # Field name made lowercase.
    cgpa10 = models.DecimalField(db_column='CGPA10', max_digits=8, decimal_places=2)  # Field name made lowercase.
    marks10 = models.IntegerField(db_column='Marks10')  # Field name made lowercase.
    outof10 = models.IntegerField(db_column='Outof10')  # Field name made lowercase.
    subjects10 = models.CharField(db_column='Subjects10', max_length=1000)  # Field name made lowercase.
    board12 = models.CharField(db_column='Board12', max_length=1000)  # Field name made lowercase.
    school12 = models.CharField(db_column='School12', max_length=1000)  # Field name made lowercase.
    year12 = models.IntegerField(db_column='Year12')  # Field name made lowercase.
    marksstatus12 = models.CharField(db_column='MarksStatus12', max_length=5)  # Field name made lowercase.
    cgpa12 = models.DecimalField(db_column='CGPA12', max_digits=8, decimal_places=2)  # Field name made lowercase.
    marks12 = models.IntegerField(db_column='Marks12')  # Field name made lowercase.
    outof12 = models.IntegerField(db_column='Outof12')  # Field name made lowercase.
    subjects12 = models.CharField(db_column='Subjects12', max_length=1000)  # Field name made lowercase.
    status12 = models.CharField(db_column='Status12', max_length=1)  # Field name made lowercase.
    statusdip = models.CharField(db_column='StatusDip', max_length=5)  # Field name made lowercase.
    boarddip = models.CharField(db_column='BoardDip', max_length=1000)  # Field name made lowercase.
    schooldip = models.CharField(db_column='SchoolDip', max_length=1000)  # Field name made lowercase.
    yeardip = models.IntegerField(db_column='YearDip')  # Field name made lowercase.
    marksstatusdip = models.CharField(db_column='MarksStatusDip', max_length=5)  # Field name made lowercase.
    cgpadip = models.DecimalField(db_column='CGPADip', max_digits=8, decimal_places=2)  # Field name made lowercase.
    marksdip = models.IntegerField(db_column='MarksDIp')  # Field name made lowercase.
    outofdip = models.IntegerField(db_column='OutOfDip')  # Field name made lowercase.
    subjectsdip = models.CharField(db_column='SubjectsDip', max_length=1000)  # Field name made lowercase.
    statusgrad = models.CharField(db_column='StatusGrad', max_length=5)  # Field name made lowercase.
    coursegrad = models.CharField(db_column='CourseGrad', max_length=50, blank=True, null=True)  # Field name made lowercase.
    boardgrad = models.CharField(db_column='BoardGrad', max_length=1000)  # Field name made lowercase.
    schoolgrad = models.CharField(db_column='SchoolGrad', max_length=1000)  # Field name made lowercase.
    yeargrad = models.IntegerField(db_column='YearGrad')  # Field name made lowercase.
    marksstatusgrad = models.CharField(db_column='MarksStatusGrad', max_length=5)  # Field name made lowercase.
    cgpagrad = models.DecimalField(db_column='CGPAGrad', max_digits=8, decimal_places=2)  # Field name made lowercase.
    marksgrad = models.IntegerField(db_column='MarksGrad')  # Field name made lowercase.
    outofgrad = models.IntegerField(db_column='OutOfGrad')  # Field name made lowercase.
    subjectsgrad = models.CharField(db_column='SubjectsGrad', max_length=1000)  # Field name made lowercase.
    physicsmarks = models.IntegerField(db_column='PhysicsMarks')  # Field name made lowercase.
    physicsoutof = models.IntegerField(db_column='PhysicsOutof')  # Field name made lowercase.
    chemistrymarks = models.IntegerField(db_column='ChemistryMarks')  # Field name made lowercase.
    chemistryoutof = models.IntegerField(db_column='ChemistryOutof')  # Field name made lowercase.
    mathsmarks = models.IntegerField(db_column='MathsMarks')  # Field name made lowercase.
    mathsoutof = models.IntegerField(db_column='MathsOutof')  # Field name made lowercase.
    biologymarks = models.IntegerField(db_column='BiologyMarks')  # Field name made lowercase.
    biologyoutof = models.IntegerField(db_column='BiologyOutof')  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=2000)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=500)  # Field name made lowercase.
    district = models.CharField(db_column='District', max_length=500)  # Field name made lowercase.
    pin = models.CharField(db_column='Pin', max_length=11)  # Field name made lowercase.
    emailid = models.CharField(db_column='EmailId', max_length=1000)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=50)  # Field name made lowercase.
    fathermobile = models.CharField(db_column='FatherMobile', max_length=50)  # Field name made lowercase.
    candidatemobile = models.CharField(db_column='CandidateMobile', max_length=50)  # Field name made lowercase.
    applicationid = models.CharField(db_column='ApplicationId', max_length=500)  # Field name made lowercase.
    enteredby = models.CharField(db_column='EnteredBy', max_length=50)  # Field name made lowercase.
    applyingdate = models.DateTimeField(db_column='ApplyingDate')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=500)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ad_applications'

class Mercedes(models.Model):
    student_name=models.CharField(db_column="StudentName",default=None,null=True,max_length=200)
    father_name=models.CharField(db_column="FatherName",default=None,null=True,max_length=200)
    mother_name=models.CharField(db_column="MotherName",default=None,null=True,max_length=200)
    student_mob=models.CharField(db_column="StudentMob",default=None,null=True,max_length=20)
    father_mob=models.CharField(db_column="FatherMob",default=None,null=True,max_length=20)
    
    student_email=models.CharField(db_column="StudentEmail",default=None,null=True,max_length=200)
    dob=models.DateField(db_column="DOB",default=None,null=True)
    category=models.CharField(db_column="Category",default=None,null=True,max_length=50)
    gender=models.CharField(db_column="Gender",default=None,null=True,max_length=10)
    address=models.CharField(db_column="Address",default=None,null=True,max_length=2000)
    city=models.CharField(db_column="City",default=None,null=True,max_length=200)
    district=models.CharField(db_column="District",default=None,null=True,max_length=200)
    pin_code=models.IntegerField(db_column="PinCode",default=None,null=True)
    ten_board=models.CharField(db_column="TenBoard",default=None,null=True,max_length=100)
    ten_year=models.IntegerField(db_column="TenYear",default=None,null=True)
    ten_grading=models.CharField(db_column="TenGrading",default="N",max_length=2,null=True)
    ten_marks=models.IntegerField(db_column="TenMarks",null=True,default=None)
    ten_max_marks=models.IntegerField(db_column="TenMaxMarks",null=True,default=None)
    ten_grade=models.FloatField(db_column="TenGrade",null=True,default=None)
    twelve=models.CharField(db_column="Twelve",default="Y",max_length=2)
    twelve_board=models.CharField(db_column="TwelveBoard",default=None,null=True,max_length=100)
    twelve_year=models.IntegerField(db_column="TwelveYear",default=None,null=True)
    twelve_grading=models.CharField(db_column="TwelveGrading",default="N",max_length=2,null=True)
    twelve_marks=models.IntegerField(db_column="TwelveMarks",null=True,default=None)
    twelve_max_marks=models.IntegerField(db_column="TwelveMaxMarks",null=True,default=None)
    twelve_grade=models.FloatField(db_column="TwelveGrade",null=True,default=None)
    diploma=models.CharField(db_column="Diploma",default="Y",max_length=2)
    diploma_board=models.CharField(db_column="DiplomaBoard",default=None,null=True,max_length=100)
    diplomacourse=models.CharField(db_column="diplomacourse",default=None,null=True,max_length=100)
    diploma_year=models.IntegerField(db_column="DiplomaYear",default=None,null=True)
    diploma_grading=models.CharField(db_column="DiplomaGrading",default="N",max_length=2,null=True)
    diploma_marks=models.IntegerField(db_column="DiplomaMarks",null=True,default=None)
    diploma_max_marks=models.IntegerField(db_column="DiplomaMaxMarks",null=True,default=None)
    diploma_grade=models.FloatField(db_column="DiplomaGrade",null=True,default=None)
    graduation=models.CharField(db_column="Graduation",null=True,default=None,max_length=50)
    graduation_university=models.CharField(db_column="GraduationUniversity",default=None,null=True,max_length=100)
    graduation_course=models.CharField(db_column="graduation_course",default=None,null=True,max_length=100)
    graduationoptionyn=models.CharField(db_column="graduation_branch",default=None,null=True,max_length=100)
    graduation_college=models.CharField(db_column="GraduationCollege",default=None,null=True,max_length=100)
    graduation_year=models.IntegerField(db_column="GraduationYear",default=None,null=True)
    graduation_grading=models.CharField(db_column="GraduationGrading",default="N",max_length=2,null=True)
    graduation_marks=models.IntegerField(db_column="GraduationMarks",null=True,default=None)
    graduation_max_marks=models.IntegerField(db_column="GraduationMaxMarks",null=True,default=None)
    graduation_grade=models.FloatField(db_column="GraduationGrade",null=True,default=None)
    btech_status=models.CharField(db_column="BtechStatus",default=None,null=True,max_length=100)
    mail_send=models.CharField(db_column="MailSend",default="N",max_length=5)
    student_aadhar_num=models.CharField(db_column="AadharNum",max_length=20,default=None,null=True)
    amount=models.FloatField(db_column="amount")
    txnid=models.CharField(db_column="TxnID",default=None,null=True,max_length=200)
    paid_status=models.CharField(db_column="PaidStatus",default="UNPAID",max_length=20)
    time_stamp=models.DateTimeField(auto_now=True)
    class Meta:
        managed = True
        db_table = 'mercedes_amc_dam'