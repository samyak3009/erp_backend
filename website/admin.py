# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.forms import ModelChoiceField
from django.forms import ModelForm
from login.models import EmployeePrimdetail,EmployeeDropdown,AuthUser
from musterroll.models import EmployeePerdetail
from .models import WebDeptData,WebDeptData2

class UserModelChoiceField(ModelChoiceField):
	def label_from_instance(self, obj):

		return str(obj.value)

class UserModelChoiceField2(ModelChoiceField):
	def label_from_instance(self, obj):

		return (str(obj.first_name)+' '+str(obj.last_name)+' ('+str(obj.username) +' )')

class BookAdminForm(ModelForm):
	Type = UserModelChoiceField(EmployeeDropdown.objects.filter(field='WEBSITE FIELDS').exclude(value__isnull=True))
	# Type = UserModelChoiceField(EmployeeDropdown.objects.filter(field='WEBSITE FIELDS').exclude(value__isnull=True))
	Dept = UserModelChoiceField(EmployeeDropdown.objects.filter(field='DEPARTMENT'))

	pmail = UserModelChoiceField2(AuthUser.objects.all())
	# related_pmail = UserModelChoiceField2(AuthUser.objects.all())

	class Meta:
		model = WebDeptData2
		fields = '__all__'

class BookAdminForm2(ModelForm):
	Type = UserModelChoiceField(EmployeeDropdown.objects.filter(field='WEBSITE FIELDS').exclude(value__isnull=True))
	Dept = UserModelChoiceField(EmployeeDropdown.objects.filter(field='DEPARTMENT'))

	pmail = UserModelChoiceField2(AuthUser.objects.all())
	# related_pmail = UserModelChoiceField2(AuthUser.objects.all())

	class Meta:
		model = WebDeptData
		fields = '__all__'
	
class FormAdmin(admin.ModelAdmin):
	def get_type(self,obj):
		return obj.Type.value
	def get_dept(self,obj):
		return obj.Dept.value
	
	list_display = ['get_type','get_dept','title','text','pmail','status','priority','related_pmail','lab_place','image']
	form = BookAdminForm

class FormAdmin2(admin.ModelAdmin):
	def get_type(self,obj):
		return obj.Type.value
	def get_dept(self,obj):
		return obj.Dept.value
	
	list_display = ['get_type','Dept','text','links','Fdate','Tdate','pmail','status']
	form = BookAdminForm2

admin.site.register(WebDeptData2, FormAdmin)
admin.site.register(WebDeptData,FormAdmin2)


# class FormAdmin(admin.ModelAdmin):
#   def get_type(self,obj):
#       return obj.Type.value
#   def get_dept(self,obj):
#       return obj.Dept.value
#   fields = ['Type','Dept','title','text','pmail','status','priority','related_pmail','lab_place','image']
#   list_display = ['get_type','get_dept','title','text','pmail','status','priority','related_pmail','lab_place','image']
	

# class FormAdmin1(admin.ModelAdmin):
#   def get_type(self,obj):
#       return obj.Type.value
#   fields = ['Type','Dept','text','Fdate','Tdate','pmail','status']
#   list_display = ['get_type','Dept','text','Fdate','Tdate','pmail','status']


	
# admin.site.register(WebDeptData2,FormAdmin)
# admin.site.register(WebDeptData,FormAdmin1)
