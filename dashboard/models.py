from __future__ import unicode_literals

from django.db import models
from login.models import EmployeeDropdown,EmployeePrimdetail
from django_mysql.models import JSONField
from musterroll.models import Roles
# Create your models here.

class LeftPanel(models.Model):
    menu_id = models.AutoField(db_column='Menu_Id', primary_key=True)  # Field name made lowercase.
    parent_id = models.IntegerField(db_column='Parent_Id')  # Field name made lowercase.
    role = models.ForeignKey(EmployeeDropdown,db_column='Role', related_name='Role_id', max_length=20,blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    link_name = models.CharField(db_column='Link_Name', max_length=200)  # Field name made lowercase.
    link_address = models.CharField(db_column='Link_Address', max_length=300)  # Field name made lowercase.
    icons = models.CharField(db_column='Icons', max_length=100, blank=True, null=True)  # Field name made lowercase.
    priority = models.IntegerField(db_column='Priority',default=0)  # Field name made lowercase.
    coord_type=models.CharField(max_length=2,null=True,default=None)
    app_name=models.CharField(max_length=50,null=True,default=None)
    class Meta:
        db_table = 'left_panel1'



class Modules(models.Model):
    code = models.CharField(db_column='code',max_length=50)
    name = models.CharField(db_column='name',max_length=100)
    address = models.CharField(db_column='address',max_length=200)
    icon = models.CharField(db_column = 'icon',max_length=100,blank=True,null=True)
    class Meta:
        db_table = 'modules'


# class LeftPanel2(models.Model):
# 	menu_id = models.AutoField(db_column='Menu_Id', primary_key=True)  # Field name made lowercase.
# 	parent_id = models.IntegerField(db_column='Parent_Id')  # Field name made lowercase.
# 	link_name = models.CharField(db_column='Link_Name', max_length=200)  # Field name made lowercase.
# 	link_address = models.CharField(db_column='Link_Address', max_length=300)  # Field name made lowercase.
# 	icons = models.CharField(db_column='Icons', max_length=100, blank=True, null=True)  # Field name made lowercase.
# 	class Meta:
# 		db_table = 'left_panel2'

# class LeftPanel1(models.Model):
# 	sno = models.AutoField(db_column='Sno',primary_key=True)
# 	menu_id = models.ForeignKey(LeftPanel2,db_column='Menu_Id', related_name='menu_id1', max_length=20,blank=True, null=True, on_delete=models.SET_NULL)
# 	role = models.ForeignKey(EmployeeDropdown,db_column='Role', related_name='Role_id1', max_length=20,blank=True, null=True, on_delete=models.SET_NULL)
# 	class Meta:
# 		db_table= 'left_panel1'


class MemberBlogs(models.Model):
    blog_id = models.AutoField(primary_key=True)
    member_id = models.ForeignKey(EmployeePrimdetail,db_column='Member_Id', related_name='Employee_id_blog', max_length=20, on_delete=models.SET_NULL,null=True)
    blog_body = models.TextField()
    blog_title = models.TextField()
    blog_date = models.DateField()
    blog_status = models.IntegerField()
    timegap = models.CharField(max_length=50)

    class Meta:
        db_table = 'member_blogs'

class Thought(models.Model):
    text = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'thought'



class Notice(models.Model):
    publisher = models.ForeignKey(EmployeePrimdetail,db_column='Publisher', related_name='Employee_id_notice', max_length=20, on_delete=models.SET_NULL,null=True)
    publish_date = models.DateField()
    title = models.CharField(max_length=80)
    subject = models.TextField(db_column='subject')
    description = models.TextField(db_column='description')
    notice_for = models.CharField(max_length=2)# S for Student E for employee
    attachment_name = JSONField(db_column='attachment_name')
    link = models.CharField(max_length=2000,db_column='link')
    fac_type = models.ForeignKey(EmployeeDropdown,db_column='fac_type', related_name='notice_all_fac_type',blank=True, null=True, on_delete=models.SET_NULL)


    class Meta:
        db_table = 'notice2'

class ToDoList(models.Model):
    emp_id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='Employee_id_todo_list', max_length=20, on_delete=models.SET_NULL,null=True)
    date = models.DateField()
    title = models.CharField(max_length=80)
    status = models.CharField(max_length=50,default='PENDING', editable=False)

    class Meta:
        db_table = 'todolist'

class DashboardIndividualSetting(models.Model):
    username = models.CharField(db_column='username',max_length=20)
    version = models.IntegerField(db_column='version',default=1)
    status = models.CharField(db_column='status',max_length=10)

    class Meta:
        db_table = 'DashboardIndividualSetting'
class DashboardTemplates(models.Model):
    setting_id = models.ForeignKey(DashboardIndividualSetting,db_column='setting_id',related_name = 'DashboardTemplates_setting_id',max_length=20,null=True,on_delete=models.SET_NULL)
    row = models.IntegerField(db_column='row')
    col = models.IntegerField(db_column='col')
    template_name = models.CharField(max_length=50,db_column='template_name')

    class Meta:
        db_table = 'DashboardTemplates'
