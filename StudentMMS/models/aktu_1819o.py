from django.db import models


class Branchdetails(models.Model):
    id = models.AutoField(primary_key=True)  # Field name made lowercase.
    branch_code = models.CharField(db_column='Branch_Code', max_length=5)  # Field name made lowercase.
    branch_name = models.CharField(db_column='Branch_Name', max_length=1000)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'BranchDetails'


class College(models.Model):
    id = models.AutoField(primary_key=True)  # Field name made lowercase.
    insitute_code = models.CharField(db_column='Insitute_Code', max_length=5, blank=True, null=True)  # Field name made lowercase.
    institude_name = models.CharField(db_column='Institude_name', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'College'


class Coursedetails(models.Model):
    id = models.AutoField(primary_key=True)  # Field name made lowercase.
    course_code = models.CharField(db_column='Course_Code', max_length=10)  # Field name made lowercase.
    course_name = models.CharField(db_column='Course_Name', max_length=200)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'CourseDetails'

class Subjectdetails(models.Model):
    id = models.AutoField(primary_key=True)  # Field name made lowercase.
    branch_id = models.ForeignKey(Branchdetails,related_name='Subjectetails_branch',on_delete=models.PROTECT,db_column='Branch_id')  # Field name made lowercase.
    course_id = models.ForeignKey(Coursedetails,related_name='Subjectetails_course',on_delete=models.PROTECT,db_column='Course_id')  # Field name made lowercase.
    sem = models.IntegerField(db_column='Sem')  # Field name made lowercase.
    sub_code = models.CharField(db_column='Sub_code', max_length=10)  # Field name made lowercase.
    sub_name = models.CharField(db_column='Sub_name', max_length=100)  # Field name made lowercase.
    max_university_marks = models.IntegerField(db_column='Max_University_Marks', blank=True, null=True)  # Field name made lowercase.
    max_internal_marks = models.IntegerField(db_column='Max_Internal_Marks', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'SubjectDetails'

class Studentprimdetail(models.Model):
    uniq_id = models.AutoField(primary_key=True)
    name = models.CharField(db_column='Name', max_length=200)  # Field name made lowercase.
    rollno = models.CharField(db_column='RollNo', max_length=20)  # Field name made lowercase.
    fathername = models.CharField(db_column='FatherName', max_length=20)  # Field name made lowercase.
    semester = models.IntegerField(db_column='Semester',default=None,null=True)  # Field name made lowercase.
    resultstatus = models.CharField(db_column='ResultStatus', max_length=100,default=None,null=True)  # Field name made lowercase.
    college_id = models.ForeignKey(College,related_name='Stu_College',on_delete=models.PROTECT,db_column='College_id')  # Field name made lowercase.
    branch_id = models.ForeignKey(Branchdetails,related_name='Stu_branch',on_delete=models.PROTECT,db_column='Branch_id')  # Field name made lowercase.
    course_id = models.ForeignKey(Coursedetails,related_name='Stu_Course',on_delete=models.PROTECT,db_column='Course_id')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'StudentPrimdetail'

class Studentmarks(models.Model):
    id = models.AutoField(primary_key=True)  # Field name made lowercase.
    uniq_id = models.ForeignKey(Studentprimdetail,related_name='StuMarks_uniq_id',on_delete=models.PROTECT,db_column='uniq_id')
    subject_id = models.ForeignKey(Subjectdetails,related_name='StuMarks_subject_id',on_delete=models.PROTECT,db_column='subject_id')
    internal_marks = models.CharField(max_length=5)
    external_marks = models.CharField(max_length=5, blank=True, null=True)
    back_marks = models.CharField(max_length=5, blank=True, null=True)
    credit = models.CharField(max_length=5)

    class Meta:
        managed = True
        db_table = 'StudentMarks'