from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout

from dashboard.models import LeftPanel,Modules, Roles, MemberBlogs, Notice, Thought, ToDoList,DashboardIndividualSetting, DashboardTemplates
from django.core import serializers
from django.db.models import F
import json
import calendar
from django.conf import settings
import datetime
from datetime import datetime, timedelta
import base64
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from random import randint
import os

from musterroll.models import EmployeePerdetail
from StudentHostel.models import HostelAssignEmp
from StudentAcademics.models import *
from attendance.models import Attendance2
from erp.constants_variables import statusMessages,statusCodes
from leave.models import LeaveType, LeaveQuota, Leaves
from login.models import EmployeePrimdetail, EmployeeDropdown, AuthUser
from erp.constants_functions import  requestMethod ,functions
from erp.constants_variables import statusCodes,rolesCheck

from login.views import check, checkpermission, generate_session_table_name
from itertools import groupby

# Create your views here.


def getHostelCoordinatorType(hash1, session):
	session = Semtiming.objects.filter(session_name=session).values_list("session", flat=True)
	print(session)
	if len(session) > 0:
		return list(HostelAssignEmp.objects.filter(status="INSERT", emp_id=hash1, hostel_id__session__session=session[0], hostel_id__session__sem_type="odd").exclude(status='DELETE').values_list('type_of_duty__value', flat=True).distinct())
	else:
		return []


def start(request):
	# print(request.META)
	error = "true"
	data = ''

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3'] == 'Employee':
				value = []
				data = []

				num = 0
				role_id = request.session['roles']
				for role in role_id:

					value.append(main_tabs(role))
				left = value
				data = {'left': left}
				msg = 'success'
				error = "false"
			else:
				msg = 'not permitted'
		else:
			msg = 'not logged in'''
	else:
		msg = "wrong parameters"
	result = {'error': error, 'msg': msg, 'data': data}

	return JsonResponse(result, safe=False)


def academic_calendar(session_name):
	AcademicsCalendar = generate_session_table_name("AcademicsCalendar_", session_name)
	data = AcademicsCalendar.objects.exclude(status="DELETE").values('title', 'start', 'end', 'type__value', 'color', 'description').order_by('start')
	final_data = []
	for f in data:
		hex_code = "#"
		if 'primary' in f['color']:
			hex_code = hex_code + "009688"
		elif 'danger' in f['color']:
			hex_code = hex_code + "E05D6F"
		elif 'lightred' in f['color']:
			hex_code = hex_code + "E05D6F"
		elif 'danger' in f['color']:
			hex_code = hex_code + "D9534F"
		elif 'dutch' in f['color']:
			hex_code = hex_code + "1693A5"
		elif 'lightgreen' in f['color']:
			hex_code = hex_code + "5CB85C"
		elif 'darkgreen' in f['color']:
			hex_code = hex_code + "16A085"
		elif 'green' in f['color']:
			hex_code = hex_code + "48B14C"
		elif 'lightblue' in f['color']:
			hex_code = hex_code + "5BC0DE"
		elif 'yellow' in f['color']:
			hex_code = hex_code + "F0AD4E"
		elif 'blue' in f['color']:
			hex_code = hex_code + "428BCA"
		elif 'grey' in f['color']:
			hex_code = hex_code + "3F4E62"

		final_data.append({'Title': f['title'], 'Start': f['start'], 'End': f['end'], 'Color_Code': f['color'], 'description': f['description'], 'hex_code': hex_code})
	return final_data


def AcademicCalendar(request):

	value = {}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if(check == 200):
				session_name = request.session['Session_name']
				if(request.method == 'GET'):  # change the method of the request to this api to get as I couldn't find it

					value = academic_calendar(session_name)
					status = 200
				else:
					status = 502

			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(status=status, data=value, safe=False)


def header(request):

	value = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if(check == 200):
				if(request.method == 'GET'):  # change the method of the request to this api to get as I couldn't find it
					data = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).extra(select={'user_name': 'name', 'dprtmnt': 'dept', 'dsgntn': 'desg'}).values('user_name', 'dprtmnt', 'dsgntn')
					if data:
						status = 200
						msg = "success"
						value = {'msg': msg, 'data': list(data)}
					else:
						status = 502

			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(status=status, data=value)


def interact(request):
	error = "true"
	data = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.session['hash3'] == 'Employee':
				blogs = MemberBlogs.objects.extra(select={'title': 'blog_title', 'body': 'blog_body', 'date': 'blog_date', 'by': 'member_id'}).values('title', 'body', 'date', 'by').order_by("-blog_date")[:10]
				thought = Thought.objects.extra(select={'thought_text': 'text'}).values('thought_text').order_by("-id")[:5]
				blogs = json.dumps(list(blogs), default=str)
				thought = json.dumps(list(thought), default=str)
				data = {'blogs': blogs, 'thoughts': thought}
				error = "false"
				msg = "success"
			else:
				msg = "not permitted"
		else:
			msg = "not logged in"
	else:
		msg = "wrong parameters"
	value = {'error': error, 'msg': msg, 'data': data}
	return JsonResponse(value, safe=False)


def view_profile(request):
	msg = ''
	data = {}
	print('dd')
	print(dict(request.session))
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:

			check = checkpermission(request, [337])
			if check == 200:
				if request.method == 'GET':
					info_user = request.session['hash1']
					# view-profile: to send employee basic profile like name, dept, designation
					try:

						profile_data = EmployeePerdetail.objects.filter(emp_id=info_user).values('linked_in_url', 'gender__value', 'gender__value', 'nationality__value', 'fname', 'mname', 'marital_status__value', 'religion__value', 'bg__value', 'caste__value', 'emp_id__name', 'nationality__value', 'emp_id__email', 'emp_id__desg__value', 'emp_id__dept__value', 'emp_id__current_pos__value', 'emp_id__mob', 'image_path')
						status = 200
						msg = 'success'
						data = {'msg': msg, 'data': list(profile_data)}
					except:
						status = 404

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	return JsonResponse(status=status, data=data)


def edit_profile(request):
	msg = ""
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if(check == 200):
				if(request.method == 'POST'):
					fields_to_be_edited = json.loads(request.body)
					e_values1 = {}
					e_values2 = {}
					if 'linked_in_url' in fields_to_be_edited:
						e_values1['linked_in_url'] = fields_to_be_edited['linked_in_url']
					if 'email' in fields_to_be_edited:
						e_values2['email'] = fields_to_be_edited['email']
					if 'mobile_number' in fields_to_be_edited:
						e_values2['mob'] = fields_to_be_edited['mobile_number']
					if 'upload' in fields_to_be_edited:
						if fields_to_be_edited['upload']:
							e_values1['image_path'] = fields_to_be_edited['upload']
					profile_edit_values_update1 = EmployeePerdetail.objects.filter(emp_id=request.session['hash1']).update(**e_values1)
					profile_edit_values_update2 = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).update(**e_values2)
					if profile_edit_values_update1 and profile_edit_values_update2:
						msg = "updated successfully"
						status = 200
					else:
						status = 500
				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500
	result = {'msg': msg}
	return JsonResponse(status=status, data=result)


def image_path(request):
	result = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if(check == 200):
				info_user = None
				if request.method == 'POST' or request.method == 'GET':
					info_user = request.session['hash1']
				if 'emp_id' in request.GET:
					info_user = request.GET['emp_id']
				try:
					profile_data = EmployeePerdetail.objects.filter(emp_id=info_user).values('image_path')
					status = 200
					msg = 'success'
					result = {'msg': msg, 'data': list(profile_data)}
				except:
					status = 401
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(status=status, data=result, safe=False)


def upload_image(request):
	# print(request)
	error = True
	msg = ""
	data = ''
	folder = request.POST['param']
	status= 200
	if request.FILES:
		print(request.FILES['file'],'file')
		file_type = ['csv','png','jpeg','jpg','pdf','gif','xls','xlsx','odf']
		if request.FILES['file'].name.split('.')[-1] not in file_type:
			print(request.FILES['file'].name.split('.')[-1])
			msg = "This Type Of File Is Not Accepted"
			status= 202
		else:
			result = handle_uploaded_file(request.FILES['file'], folder)
			msg = "uploaded"
			error = False
			data = result

	else:
		return JsonResponse({}, safe=False)
	send = {'error': error, 'msg': msg, 'data': data}
	return JsonResponse(send,status=status, safe=False)


def handle_uploaded_file(f, folder):
	# print(f,folder)
	file_name = f.name
	ext = file_name.split('.')[-1]
	random = randint(10000000, 99999999)
	file_init = folder
	file_init = file_init.split('/')
	file_init = file_init[::-1]
	file_init = file_init[0]
	filename = "%s_%s.%s" % (file_init, random, ext)

	# filepath= os.path.join('/usr/local/apache2/htdocs',folder,filename)
	# directoty = os.path.join('/usr/local/apache2/htdocs',folder)
	filepath = os.path.join(settings.FILE_PATH, folder, filename)
	directoty = os.path.join(settings.FILE_PATH, folder)
	# print(directoty)

	if not os.path.exists(directoty):
		os.makedirs(directoty)
	with open(filepath, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	return filename


def count(request):
	result = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if(check == 200):
				if(request.method == 'GET'):
					dir = EmployeeDropdown.objects.filter(value='DIRECTOR', field='ROLES').values('sno')
					hod = EmployeeDropdown.objects.filter(value='HOD', field='ROLES').values('sno')
					no_of_directors = Roles.objects.filter(roles=dir).count()
					no_of_hod = Roles.objects.filter(roles=hod).count()
					no_of_employees = AuthUser.objects.count()
					data = {'directors': no_of_directors, 'hod': no_of_hod, 'employees': no_of_employees}
					msg = "success"
					status = 200
					result = {'msg': msg, 'data': data}
				else:
					status = 502

			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	return JsonResponse(status=status, data=result, safe=False)


def CountLeave(request):
	error = True
	data = ""
	msg = ""
	leaves = {}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			# print(request.session['hash1'])
			qry0 = EmployeePrimdetail.objects.filter(emp_id=request.session['hash1']).values('desg', 'emp_category', 'emp_type')

			qry1 = LeaveType.objects.values('id', 'leave_name', 'leave_abbr')
			if qry1.count() > 0:
				for a in qry1:
					qry2 = LeaveQuota.objects.filter(type_of_emp=qry0[0]['emp_type'], category_emp=qry0[0]['emp_category'], designation=qry0[0]['desg'], leave_id=a['id']).values('no_of_leaves')
					# print(qry2)
					if(qry2.count() > 0):
						msg = "Success"
						error = False
						leaves[a['leave_abbr']] = qry2[0]['no_of_leaves']
					else:
						leaves[a['leave_abbr']] = ""

			else:
				msg = "No Leaves Found"
	else:
		msg = "Login First"

	result = {'error': error, 'msg': msg, 'data': leaves}

	return JsonResponse(result, safe=False)

############################  SHIVAM LEFT PANEL  ###################################
def getModules(request):
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			data=[]
			roles = request.session['roles']
			# emp_id = request.session['hash1']
			module=list(LeftPanel.objects.filter(role__in=roles).exclude(app_name=None).values_list('app_name',flat=True).distinct())
			data = {'Modules':list(Modules.objects.filter(code__in=module).values())}
			return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def left_panel1(request):
	data = [{}]
	msg = ""
	emp_link="http://127.0.0.1:4000"
	i = 0
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if(request.method == 'GET'):
				if 'Session_name' not in request.session:
					return JsonResponse(data={'msg': 'Session name not defined'}, status=202)
				session_name = request.session['Session_name']
				if 'roles' in request.session:
					roles = request.session['roles']
				emp_id = request.session['hash1']
				app_name = request.GET['app_name']
				role_count = 0
				data = []
				flag_academic = False

				if 1369 in roles:
					flag_academic = True
					roles.remove(1369)

				for role in roles:
					role_name = EmployeeDropdown.objects.filter(sno=role, field='ROLES').values('value')
					role_id = role
					links = list(LeftPanel.objects.filter(role=role_id, parent_id='0', coord_type__isnull=True,app_name=app_name).exclude(link_name="Staff Appraisal Form").exclude(role=1369).values().order_by('priority'))
					if len(links) == 0 or links is None:
						continue

					data.append({})
					data[i]["role"] = role_name[0]['value']

					for link in links:
						sub_tabs = list(sublinks(link['menu_id'],app_name))
						link['sub_tabs'] = sub_tabs
					query = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('cadre__value', 'ladder__value')
					print(query)
					if "A" in query[0]['ladder__value'] and role == 337:
						links.append({'link_name': 'Staff Appraisal Form', 'link_address': 'AppraisalStaff/AppraisalAbandEmp','icons': 'fa fa-line-chart', 'priority': 0, 'menu_id': -1})
					elif (query[0]['cadre__value'] == 'E' or query[0]['cadre__value'] == 'M' or query[0]['cadre__value'] == 'G') and role == 337:
						links.append({'link_name': 'Staff Appraisal Form','icons': 'fa fa-line-chart', 'link_address': 'AppraisalStaff/AppraisalEMG_employee', 'priority': 0, 'menu_id': -1})

					data[i]["tabs"] = list(links)
					i += 1
					role_count += 1
					msg = "success"
				############# EMPLOYEE ROLE ##################################

				emp_hostel_roles = getHostelCoordinatorType(emp_id, session_name)
				if(len(emp_hostel_roles) > 0):
					for x in emp_hostel_roles:
						if x not in request.session['Coordinator_type']:
							request.session['Coordinator_type'].append(x)
					links_hostel = list(LeftPanel.objects.filter(coord_type__in=emp_hostel_roles).exclude(coord_type__isnull=True,app_name=app_name).values('coord_type').order_by('coord_type').distinct())
					# links_hostel=list(LeftPanel.objects.filter(coord_type__in=emp_hostel_roles).exclude(coord_type__isnull=True).values('coord_type').order_by('coord_type').distinct())
					for link in links_hostel:
						# print(link)
						data.append({})
						if link['coord_type'] == 'REC':
							data[i]["role"] = 'RECTOR'
						elif link['coord_type'] == 'WAR':
							data[i]["role"] = 'WARDEN'
						print(app_name)
						lin = (LeftPanel.objects.filter(coord_type=link['coord_type'], parent_id='0',app_name=app_name).values().order_by('priority'))
						for l in lin:
							sub_tabs = list(sublinks(l['menu_id'],app_name))
							l['sub_tabs'] = sub_tabs

						data[i]["tabs"] = list(lin)
						i += 1
						role_count += 1
						msg = "success"

				############# ACADEMIC ROLE ##################################
				AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

				if flag_academic:
					emp_acad_roles = list(AcadCoordinator.objects.filter(emp_id=emp_id).exclude(status="DELETE").values_list('coord_type', flat=True).distinct())
					emp_acad_roles.append('A')
					if 319 in roles:
						emp_acad_roles.append('H')
					for x in emp_acad_roles:
						if x not in request.session['Coordinator_type']:
							request.session['Coordinator_type'].append(x)

					links_acad = (LeftPanel.objects.filter(role=1369, coord_type__in=emp_acad_roles,app_name=app_name).exclude(coord_type__isnull=True).values('coord_type').order_by('coord_type').distinct())
					print(links_acad,"link")
					if 'ACAD' in app_name or 'MMS' in app_name or 'REPORTS' in app_name:
						for link in list(links_acad):
							role=None
							if link['coord_type'] == 'T':
								role = 'TIME TABLE COORDINATOR'
							elif link['coord_type'] == 'C':
								role = 'CLASS COORDINATOR'
							elif link['coord_type'] == 'G':
								role = 'GROUP COORDINATOR'
							elif link['coord_type'] == 'S':
								role = 'SUBJECT COORDINATOR'
							elif link['coord_type'] == 'R':
								role = 'SEMESTER REGISTRATION COORDINATOR'
							elif link['coord_type'] == 'E':
								role = 'EXTRA ATTENDANCE COORDINATOR'
							elif link['coord_type'] == 'A':
								role = 'ACADEMIC'
							elif link['coord_type'] == 'H':
								role = 'ACADEMIC HOD'

							if role !=None:
								data.append({})
								data[i]["role"]=role
								lin = (LeftPanel.objects.filter(role=1369, coord_type=link['coord_type'], parent_id='0',app_name=app_name).values().order_by('priority'))
								for l in lin:
									sub_tabs = list(sublinks(l['menu_id'],app_name))
									l['sub_tabs'] = sub_tabs
								data[i]["tabs"] = list(lin)
								i += 1
								role_count += 1
								msg = "success"
					if 'MMS' in app_name or 'REPORTS' in app_name:
						for link in list(links_acad):
							role=None
							if link['coord_type'] == 'QM':
								role = 'QUESTION MODERATOR'
							elif link['coord_type'] == 'CO':
								role = 'CO COORDINATOR'
							elif link['coord_type'] == 'COE':
								role = 'EXAM COORDINATOR'
							elif link['coord_type'] == 'NC':
								role = 'NBA COORDINATOR'
							if role !=None:
								data.append({})
								data[i]["role"]=role
								lin = (LeftPanel.objects.filter(role=1369, coord_type=link['coord_type'], parent_id='0',app_name=app_name).values().order_by('priority'))
								for l in lin:
									sub_tabs = list(sublinks(l['menu_id'],app_name))
									l['sub_tabs'] = sub_tabs

								data[i]["tabs"] = list(lin)
								i += 1
								role_count += 1
								msg = "success"

					emp_link = list(Modules.objects.filter(code='EMP').values())[0]

				status = 200
			else:
				status = 502
		else:
			status = 401
	else:
		status = 500
	result = {'msg': msg, 'data': data,"emp_link":emp_link}

	return JsonResponse(data=result, status=status)



def sublinks(parent_id, app_name):
	if LeftPanel.objects.filter(parent_id=parent_id).filter(app_name=app_name).all().count() == 0:
		return []
	else:
		links = LeftPanel.objects.filter(parent_id=parent_id).filter(app_name=app_name).values().order_by('priority')
		for link in links:
			sub_tabs = list(sublinks(link['menu_id'],app_name))
			link['sub_tabs'] = sub_tabs
		return links

def left_panel(request):
	data = [{}]
	msg = ""
	i = 0
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if(request.method == 'GET'):
				if 'Session_name' not in request.session:
					return JsonResponse(data={'msg': 'Session name not defined'}, status=202)
				session_name = request.session['Session_name']
				roles = []
				if 'roles' in request.session:
					roles = request.session['roles']
				if 'hash1' not in request.session:
					logout(request)
					msg = "logged out successfully"
					status = 200
					return JsonResponse({'msg': msg}, status=status, safe=False)
				emp_id = request.session['hash1']
				role_count = 0
				#data=[{} for _ in roles]
				data = []
				flag_academic = False

				if 1369 in roles:
					flag_academic = True
					roles.remove(1369)

				for role in roles:

					role_name = EmployeeDropdown.objects.filter(sno=role, field='ROLES').values('value')
					role_id = role
					links = list(LeftPanel.objects.filter(role=role_id, parent_id='0', coord_type__isnull=True).exclude(link_name="Staff Appraisal Form").exclude(role=1369).values().order_by('priority'))

					if len(links) == 0 or links is None:
						continue

					data.append({})
					data[i]["role"] = role_name[0]['value']

					for link in links:
						sub_tabs = list(sublinks1(link['menu_id']))
						link['sub_tabs'] = sub_tabs

					query = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('cadre__value', 'ladder__value')
					if "A" in query[0]['ladder__value'] and role == 337:
						links.append({'link_name': 'Staff Appraisal Form', 'link_address': 'AppraisalStaff/AppraisalAbandEmp', 'priority': 0, 'menu_id': -1, 'icons': 'fa fa-line-chart'})
					elif (query[0]['cadre__value'] == 'E' or query[0]['cadre__value'] == 'M' or query[0]['cadre__value'] == 'G') and role == 337:
						links.append({'link_name': 'Staff Appraisal Form', 'link_address': 'AppraisalStaff/AppraisalEMG_employee', 'priority': 12, 'menu_id': -1, 'icons': 'fa fa-line-chart'})

					data[i]["tabs"] = list(links)
					i += 1
					role_count += 1
					msg = "success"
				############# EMPLOYEE ROLE ##################################

				emp_hostel_roles = getHostelCoordinatorType(emp_id, session_name)
				if(len(emp_hostel_roles) > 0):
					for x in emp_hostel_roles:
						if x not in request.session['Coordinator_type']:
							request.session['Coordinator_type'].append(x)
					links_hostel = list(LeftPanel.objects.filter(coord_type__in=emp_hostel_roles).exclude(coord_type__isnull=True).values('coord_type').order_by('coord_type').distinct())
					# links_hostel=list(LeftPanel.objects.filter(coord_type__in=emp_hostel_roles).exclude(coord_type__isnull=True).values('coord_type').order_by('coord_type').distinct())
					for link in links_hostel:
						# print(link)
						data.append({})
						if link['coord_type'] == 'REC':
							data[i]["role"] = 'RECTOR'
						elif link['coord_type'] == 'WAR':
							data[i]["role"] = 'WARDEN'

						lin = (LeftPanel.objects.filter(coord_type=link['coord_type'], parent_id='0').values().order_by('priority'))
						for l in lin:
							sub_tabs = list(sublinks1(l['menu_id']))
							l['sub_tabs'] = sub_tabs

						data[i]["tabs"] = list(lin)
						i += 1
						role_count += 1
						msg = "success"

				############# ACADEMIC ROLE ##################################
				AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

				if flag_academic:
					emp_acad_roles = list(AcadCoordinator.objects.filter(emp_id=emp_id).exclude(status="DELETE").values_list('coord_type', flat=True).distinct())
					emp_acad_roles.append('A')

					if 319 in roles:
						emp_acad_roles.append('H')
					for x in emp_acad_roles:
						if x not in request.session['Coordinator_type']:
							request.session['Coordinator_type'].append(x)
					links_acad = (LeftPanel.objects.filter(role=1369, coord_type__in=emp_acad_roles).exclude(coord_type__isnull=True).values('coord_type').order_by('coord_type').distinct())
					for link in list(links_acad):
						data.append({})
						if link['coord_type'] == 'T':
							data[i]["role"] = 'TIME TABLE COORDINATOR'
						elif link['coord_type'] == 'C':
							data[i]["role"] = 'CLASS COORDINATOR'
						elif link['coord_type'] == 'G':
							data[i]["role"] = 'GROUP COORDINATOR'
						elif link['coord_type'] == 'S':
							data[i]["role"] = 'SUBJECT COORDINATOR'
						elif link['coord_type'] == 'R':
							data[i]["role"] = 'SEMESTER REGISTRATION COORDINATOR'
						elif link['coord_type'] == 'E':
							data[i]["role"] = 'EXTRA ATTENDANCE COORDINATOR'
						elif link['coord_type'] == 'A':
							data[i]["role"] = 'ACADEMIC'
						elif link['coord_type'] == 'H':
							data[i]["role"] = 'ACADEMIC HOD'
						elif link['coord_type'] == 'QM':
							data[i]["role"] = 'QUESTION MODERATOR'
						elif link['coord_type'] == 'CO':
							data[i]["role"] = 'CO COORDINATOR'
						elif link['coord_type'] == 'COE':
							data[i]["role"] = 'EXAM COORDINATOR'
						elif link['coord_type'] == 'NC':
							data[i]["role"] = 'NBA COORDINATOR'

						lin = (LeftPanel.objects.filter(role=1369, coord_type=link['coord_type'], parent_id='0').values().order_by('priority'))
						for l in lin:
							sub_tabs = list(sublinks1(l['menu_id']))
							l['sub_tabs'] = sub_tabs

						data[i]["tabs"] = list(lin)
						i += 1
						role_count += 1
						msg = "success"
				status = 200
			else:
				status = 502
		else:
			status = 401
	else:
		status = 500
	result = {'msg': msg, 'data': data}

	return JsonResponse(data=result, status=status)


def sublinks1(parent_id):
	if LeftPanel.objects.filter(parent_id=parent_id).all().count() == 0:
		return []
	else:
		links = LeftPanel.objects.filter(parent_id=parent_id).values().order_by('priority')
		for link in links:
			sub_tabs = list(sublinks1(link['menu_id']))
			link['sub_tabs'] = sub_tabs
		return links
################################################################ Birthday ########################################################################


def birthday_name(request):
	msg = ""
	data = ''
	birthday_data = ''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if(check == 200):
				if(request.method == 'GET'):

					today_month = datetime.now().date().month
					today_day = datetime.now().date().day
					birthday_date = EmployeePerdetail.objects.extra(select={'date_all': 'dob', 'emp_id': 'emp_id'}).exclude(dob__isnull=True).values('date_all', 'emp_id')
					birthday_value = []
					birthday_emp = []
					q = 0
					c = 0
					for i in birthday_date:
						birthday_value.append(i['date_all'])
						birthday_emp.append(i['emp_id'])
						date_month = str(birthday_value[q]).split('-')
						if int(date_month[1]) == today_month and int(date_month[2]) == today_day:
							c = c + 1
							birthday_data = EmployeePerdetail.objects.filter(dob=birthday_value[q]).values('emp_id__name', 'image_path')
						q = q + 1
					status = 200
					msg = "Success"
					data = list(birthday_data)

				else:
					status = 502
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	result = {'msg': msg, 'data': data}
	# b=birthday_value[0].date()

	return JsonResponse(status=status, data=result)
################################################################ Notice ########################################################################


def notice_all(request):
	data = {}
	status = 402
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if(request.method == 'GET'):
				if(request.GET['request_type']=='view_previous'):
					if 'fac_type' in request.GET:
						emp_id = request.session['hash1']
						if request.GET['fac_type']=='all':
							if(checkpermission(request, [rolesCheck.ROLE_NOTICE_HEAD])==200):
								qr = list(Notice.objects.filter(publisher=emp_id).values('id','publisher','publisher__name','publisher__desg__value','publisher__title__value','publish_date','title','subject','description','attachment_name','link','fac_type','fac_type__value','notice_for').order_by('-publish_date'))
								for x in range(0,len(qr)):
									if qr[x]['notice_for']=='S':
										qr[x]['notice_for']='STUDENT'
									elif qr[x]['notice_for']=='E':
										qr[x]['notice_for']=qr[x]['fac_type__value']
								data = qr
								status = statusCodes.STATUS_SUCCESS
							else:
								data = statusMessages.MESSAGE_FORBIDDEN
								status = statusCodes.STATUS_FORBIDDEN
						else:
							data = statusMessages.MESSAGE_BAD_REQUEST
							status = statusCodes.STATUS_BAD_REQUEST
					elif 'notice_for' in request.GET:
						if request.GET['notice_for']=='S':
							qr = list(Notice.objects.filter(notice_for='S').values('id','publisher','publisher__name','publisher__desg__value','publisher__title__value','publish_date','title','subject','description','attachment_name','link','fac_type','notice_for').order_by('-publish_date'))
						elif request.GET['notice_for']=='E':
							emp_id = request.session['hash1']
							emp_detail = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('desg__value','emp_category__value','emp_category')
							qr = list(Notice.objects.filter(fac_type=emp_detail[0]['emp_category'],notice_for='E').values('id','publisher','publisher__name','publisher__desg__value','publisher__title__value','publish_date','title','subject','description','attachment_name','link','fac_type','notice_for'))
						notice_list=[]
						for k,v in groupby(qr, key=lambda x: x['publisher']):
							v=list(v)
							if(len(notice_list)!=0):
								if(v[0]['publisher__desg__value']=='DIRECTOR'):
									notice_list.insert(0,v)
								elif(v[0]['publisher__desg__value']=='JOINT DIRECTOR'):
									if(notice_list[0][0]['publisher__desg__value']=='DIRECTOR'):
										notice_list.insert(1,v)
									else:
										notice_list.insert(0,v)
								else:
									notice_list.append(v)
							else:
								notice_list.append(v)
						data = notice_list
						status = statusCodes.STATUS_SUCCESS
			elif(request.method=='POST'):
				emp_id = request.session['hash1']
				check1 = checkpermission(request, [rolesCheck.ROLE_NOTICE_HEAD])
				if check1==200:
					input_data = json.loads(request.body)
					att_name=None
					if 'doc' in input_data:
						att_name=input_data['doc']
					link=None
					if 'link' in input_data:
						link=input_data['link']
					fac_type=None
					if 'S' in input_data['notice_for']:
						qr=Notice.objects.create(publisher=EmployeePrimdetail.objects.get(emp_id=emp_id),publish_date=datetime.now(),title=input_data['title'],subject=input_data['subject'],description=input_data['description'],attachment_name=att_name,link=link,fac_type=None,notice_for='S')
					if 'E' in input_data['notice_for']:
						for x in input_data['fac_type']:
							qr=Notice.objects.create(publisher=EmployeePrimdetail.objects.get(emp_id=emp_id),publish_date=datetime.now(),title=input_data['title'],subject=input_data['subject'],description=input_data['description'],attachment_name=att_name,link=link,fac_type=EmployeeDropdown.objects.get(sno=x),notice_for='E')
					data=statusMessages.MESSAGE_SUCCESS
					status=statusCodes.STATUS_SUCCESS
				else:
					data = statusMessages.MESSAGE_FORBIDDEN
					status = statusCodes.STATUS_FORBIDDEN
			elif(request.method=='DELETE'):
				check1 = checkpermission(request, [rolesCheck.ROLE_NOTICE_HEAD])
				print(check1,"AYYAAAAAAA")
				if check1==200:
					input_data = json.loads(request.body)
					id = input_data['id']
					qr = Notice.objects.filter(id=id).delete()
					data=statusMessages.MESSAGE_DELETE
					status=statusCodes.STATUS_SUCCESS
				else:
					data = statusMessages.MESSAGE_FORBIDDEN
					status = statusCodes.STATUS_FORBIDDEN
			else:
				status = 403
		else:
			status = 401
	else:
		status = 500

	result_notice = {'data': data}
	return JsonResponse(status=status, data=result_notice)


############################################################### ToDo List API ##########################################################################
def TODO_List(request):
	result_todo = {}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if(check == 200):

				if(request.method == 'GET'):  # to view to do list

					emp = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
					todo_view = ToDoList.objects.filter(emp_id=emp).values('title', 'status', 'id')
					msg = "Success"
					result_todo = {'msg': msg, 'data': list(todo_view)}
					status = 200

				elif(request.method == 'POST'):  # To add elements to to do list
					todo_data = json.loads(request.body)
					todo = {}
					today_date = datetime.now().date()
					todo['date'] = today_date
					todo['title'] = todo_data['description']
					todo['status'] = 'PENDING'
					todo['emp_id'] = EmployeePrimdetail.objects.get(emp_id=request.session['hash1'])
					todo_insert = ToDoList.objects.create(**todo)
					if todo_insert:
						status = 200
						msg = "success"
						result_todo = {'msg': msg, 'data': list(todo_data)}
					else:
						status = 400
						result_todo = {'data': list(todo_data)}

				elif(request.method == 'PUT'):  # To edit elements of todo list
					todo_e = json.loads(request.body)
					todo = todo_e['status']
					todo_insert = ToDoList.objects.filter(id=todo_e['id']).update(status=todo)
					if todo_insert:
						status = 200
						msg = "success"

					else:
						msg = "could not update"
						status = 500
					result_todo = {'msg': msg}

				elif(request.method == 'DELETE'):  # To delete elements od todo list
					todo_e = json.loads(request.body)
					todo = todo_e['id']
					todo_insert = ToDoList.objects.filter(id=todo_e['id']).delete()
					if todo_insert:
						status = 200
						msg = "success"
					else:
						msg = "could not delete"
						status = 500
					result_todo = {'msg': msg}
				else:
					status = 400
			else:
				status = 403
		else:
			status = 401
	else:
		status = 400

	return JsonResponse(status=status, data=result_todo)

#######################################################################  ATTENDANCE SUMMARY            ############################################################################


def attendancesummary(request):
	attdata = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])
			if(check == 200):
					 # attendance summary for the month
				if(request.method == 'GET'):
					pmail = request.session['hash1']
					year = datetime.now().date().year
					month = datetime.now().date().month
					calarr = calendar.monthrange(year, month)
					start_date = str(year) + "-" + str(month) + "-" + str(calarr[0])
					end_date = str(year) + "-" + str(month) + "-" + str(calarr[1])
					totaldays = calarr[1]
					month = calendar.month_name[month]
					p = Attendance2.objects.filter(date__gte=start_date, date__lte=end_date, Emp_Id=pmail, status='P').count()
					pby2 = Attendance2.objects.filter(date__gte=start_date, date__lte=end_date, Emp_Id=pmail, status='P/2').count()
					abs = Attendance2.objects.filter(date__gte=start_date, date__lte=end_date, Emp_Id=pmail, status='A').count()
					status = 200
					data = {'month': month, 'p': p, 'pby2': pby2, 'abs': abs, 'totaldays': totaldays}

				else:
					status = 400
			else:
				status = 403
		else:
			status = 401
	else:
		status = 400

	return JsonResponse(status=status, data=data)


################################################################### 15 day Attendance Info of Employee ##########################################################
def lasttenattendance(request):

	attdata = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])

			if(check == 200):
				if(request.method == 'GET'):
					pmail = request.session['hash1']
					# lasttenattendance :gives last 15 days attendance of employee
					date = datetime.now() - timedelta(days=15)
					fdate = date.date().strftime('%Y-%m-%d')
					tdate = datetime.now().date().strftime('%Y-%m-%d')
					recent_15days_attendance = Attendance2.objects.filter(date__range=[fdate, tdate], Emp_Id=pmail).values('date', 'status', 'intime', 'outtime').order_by('-date')
					# print(recent_15days_attendance)
					status = 200
					msg = 'success'
					data = {'msg': msg, 'data': list(recent_15days_attendance)}

				else:
					status = 400
			else:
				status = 403
		else:
			status = 401
	else:
		status = 400

	return JsonResponse(status=status, data=data)

#################################################################################################################################################################


def test(request):
	error = True
	attdata = ""
	msg = ""
	pmail = '00007'
	#$qry=Leaveremaning.objects.filter(empid='pmail',)
	msg = "Success"
	result = {'error': error, 'msg': msg, 'data': send}
	return JsonResponse(result, safe=False)

##################################################################################################################


def cctv(request):

	attdata = {}

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request, [337])

			if(check == 200):
				if(request.method == 'GET'):
					field = 'CCTV SURVEILLANCE'
					names = EmployeeDropdown.objects.filter(field=field).values('field', 'pid')
					name = names[0]['field']
					p_id = names[0]['pid']

					qry1 = EmployeeDropdown.objects.filter(field=name, pid=p_id).exclude(value__isnull=True).extra(select={'valueid': 'sno', 'parentId': 'pid', 'cat': 'field', 'text1': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('valueid', 'parentId', 'cat', 'text1', 'edit', 'delete')
					for x in range(0, len(qry1)):
						test = EmployeeDropdown.objects.filter(pid=qry1[x]['valueid']).exclude(value__isnull=True).extra(select={'subid': 'sno', 'subvalue': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('subid', 'subvalue', 'edit', 'delete')
						qry1[x]['subcategory'] = list(test)
					msg = "Success"
					data = {'msg': msg, 'data': list(qry1)}
					status = 200

				else:
					status = 400
			else:
				status = 403
		else:
			status = 401
	else:
		status = 400

	return JsonResponse(status=status, data=data)

def dashboard(request):
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.method == 'GET':
				if(request.GET['request_type'] == 'temp_coords'):
					user_type = request.session['hash3']
					if 'Employee' in user_type:
						username = request.session['hash1']
					else:
						username = StudentPrimDetail.objects.filter(uniq_id=request.session['uniq_id']).values_list('lib')[0]
					if DashboardIndividualSetting.objects.filter(username = username[0],status='insert').exists():
						ver = DashboardIndividualSetting.objects.filter(username = username[0],status = 'insert').values_list('version')[0]
						qr = DashboardIndividualSetting.objects.filter(username = username[0],status = 'insert').update(username = username[0],version = ver[0],status = 'delete')
						qr2 = DashboardIndividualSetting.objects.create(username = username[0],version = ver[0]+1 ,status = 'insert')
					else:
						DashboardIndividualSetting.objects.create(username = username[0],status='insert')
					data_lists = json.loads(request.GET['data'])
					for data in data_lists:
						print(data)
						id_temp =  DashboardIndividualSetting.objects.filter(username = username[0],status='insert').values_list('id')[0]
						print(id_temp)
						DashboardTemplates.objects.create(setting_id =DashboardIndividualSetting.objects.get(id=id_temp[0]),row = int(data["row"]) ,col = int(data["col"]),template_name = data["template_name"])
					return functions.RESPONSE({'msg':'success'},statusCodes.STATUS_SUCCESS)
				elif(request.GET['request_type'] == 'get_temp_coordinate'):
					user_type = request.session['hash3']
					if 'Employee' in user_type:
						username = request.session['hash1']
					else:
						username = StudentPrimDetail.objects.filter(uniq_id=request.session['uniq_id']).values_list('lib')[0]
						if DashboardIndividualSetting.objects.filter(username = username[0],status='insert').exists():
							id_data = DashboardIndividualSetting.objects.filter(username = username[0],status='insert').values_list('id')[0]
							data = list(DashboardTemplates.objects.filter(setting_id = id_data[0]).values('col','row','template_name'))
							c={}
							for x in data:
								c[x['template_name']] = { 'row' : x['row'] , 'col' : x['col']}
							return JsonResponse(data=c, safe=False)
						else:
							data = ['no data exists']
							return JsonResponse(data= data, safe=False)
