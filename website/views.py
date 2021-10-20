from __future__ import unicode_literals
from django.shortcuts import render
import json
from login.models import EmployeePrimdetail, EmployeeDropdown, AuthUser
from musterroll.models import EmployeePerdetail, EmployeeSeparation
from .models import WebDeptData, WebDeptData2, Mercedes
from django.http import JsonResponse
import datetime
from login.views import checkpermission
from aar.views import get_highest_qualification

from datetime import datetime
from datetime import date
from django.contrib.auth.models import User
import requests
from . import CheckSum
from . import constants
from django.db.models import Q
import requests
import json
import cgi
# from django.shortcuts import redirect, render_to_response
import yagmail
from threading import Thread


# def insert(request): ##INSERTING
# 	if(request.method=='POST'):
# 		data=json.loads(request.body.decode("utf-8"))
# 		dept_select=data['Dept_id']
# 		# url=data['url']
# 		a=['ei_kiet_best_electronics_instrumentation_engineering_course_ghaziabad.jpg','ei_kiet_best_electronics_instrumentation_engineering_course_india.jpg','ei_kiet_best_electronics_instrumentation_engineering_course_ncr.jpg','ei_kiet_best_electronics_instrumentation_engineering_course_north_india.jpg','ei_kiet_best_electronics_instrumentation_engineering_course_up.jpg']
# 		dept_name=EmployeeDropdown.objects.filter(sno=dept_select).values('value')
# 		dept_new=EmployeeDropdown.objects.get(sno=dept_select)
# 		# type_new=EmployeeDropdown.objects.get(sno=1018)
# 		name=dept_name[0]['value']
# 		name1=name.lower()
# 		print name1
# 		# for i in range(len(a)):
# 		# 	url1='images/department/'+name+'/'+a[i]
# 		# 	print url1
# 		# 	query1=WebDeptData2.objects.create(image=url1,Dept=dept_new,Type=type_new)
# 		type_new=EmployeeDropdown.objects.get(sno=992)
# 		for i in range(1,4):
# 			url1='images/department/'+name+'/'+name1+str(i)+'.jpg'
# 			print url1
# 			query1=WebDeptData2.objects.create(image=url1,Dept=dept_new,Type=type_new)

# 		msg="Data Successfully Added..."
# 		data_values={'msg':msg}
# 		return JsonResponse(data_values)


def Homepage(request):  # HOMEPAGE OF WEBSITE ( ANNOUNCEMENTS and UPCOMING EVENTS) Change Type Values
    data_values = {}
    if (request.method == 'GET'):
        today = str(date.today())
        query1 = WebDeptData.objects.filter(Tdate__gte=today, Type=1021).values('text', 'Type__value', 'links')
        query2 = WebDeptData.objects.filter(Tdate__gte=today, Type=1020).values('text', 'Type__value', 'Tdate', 'Fdate', 'links').order_by('Fdate')
        data_values = {'data1': list(query1), 'data2': list(query2)}
    return JsonResponse(data_values, safe=False)


def dept_name(request):  # Deptartment Name to Frontend
    data_values = {}
    if(request.method == 'GET'):
        query1 = EmployeeDropdown.objects.filter(field="Department").values('sno', 'value')
        data_values = {'data': list(query1)}
    return JsonResponse(data_values, safe=False)


def dept_first_click(request):  # On the First Click on The Department Page
    data_values = {}
    if(request.method == 'POST'):
        data = json.loads(request.body.decode("utf-8"))
        dept_select = data['Dept_id']
        today = str(date.today())
        query1 = WebDeptData.objects.filter(Dept=dept_select).filter(Type=979).values('Type__value', 'text')
        query2 = WebDeptData.objects.filter(Dept=dept_select).filter(Type=980).values('Type__value', 'text')
        query3 = WebDeptData.objects.filter(Dept=dept_select).filter(Type=981).values('Type__value', 'text')
        query4 = WebDeptData.objects.filter(Dept=dept_select).filter(Type=982).values('Type__value', 'text')
        query5 = WebDeptData.objects.filter(Dept=dept_select).filter(Type=983).values('Type__value', 'text')
        # Upcoming Events
        query6 = WebDeptData.objects.filter(Dept=dept_select, Tdate__gte=today, Type=979).values('text', 'Type__value', 'Tdate', 'Fdate', 'links').order_by('Fdate')
        # Announcements
        query7 = WebDeptData.objects.filter(Dept=dept_select, Tdate__gte=today, Type=980).values('text', 'Type__value', 'links').order_by('Fdate')

        emp_sep_cnt = EmployeeSeparation.objects.filter(emp_id__dept=dept_select, status="RESIGN").values_list('emp_id', flat=True)
        pro = EmployeePrimdetail.objects.filter(dept=dept_select, current_pos=836).exclude(emp_id__in=emp_sep_cnt).count()
        asstPro = EmployeePrimdetail.objects.filter(dept=dept_select, current_pos=868).exclude(emp_id__in=emp_sep_cnt).count()
        assocPro = EmployeePrimdetail.objects.filter(dept=dept_select, current_pos=887).exclude(emp_id__in=emp_sep_cnt).count()

        data_count = {'pro': pro, 'asstPro': asstPro, 'assocPro': assocPro}

        data_values = {'data1': list(query1), 'data2': list(query2), 'data3': list(query3), 'data4': list(query4), 'data5': list(query5), 'data7': data_count, 'data8': list(query6), 'data9': list(query7)}
    return JsonResponse(data_values, safe=False)


def Topper(request):
    result = {}
    if(request.method == 'GET'):
        query1 = WebDeptData2.objects.filter(Type=1330).values('text', 'priority', 'status', 'title', 'Dept__value', 'lab_place')
        print(query1)
        url = 'https://tech.kiet.edu/api/student1/index.php/Login_controller/web_toppers'
        data_values = {'data': list(query1)}
        data_values = json.dumps(data_values)
        headers = {'content-type': 'application/json'}
        api = requests.post(url, data=data_values, headers=headers)
        msg = "Data Successfully Added..."
        result = api.json()

        data_values1 = {'msg': msg}

        return JsonResponse(result, safe=False)


def Topper_dept(request):
    if(request.method == 'POST'):
        data = json.loads(request.body.decode("utf-8"))
        dept_select = data['Dept_id']
        query1 = WebDeptData2.objects.filter(Dept=dept_select, Type=1330).values('text', 'priority', 'status', 'title', 'Dept__value', 'lab_place')
        url = 'https://tech.kiet.edu/api/student1/index.php/Login_controller/web_toppers'
        data_values = {'data': list(query1)}
        data_values = json.dumps(data_values)
        headers = {'content-type': 'application/json'}
        api = requests.post(url, data=data_values, headers=headers)
        msg = "Data Successfully Added..."
        result = api.json()

        data_values1 = {'msg': msg}

        return JsonResponse(result, safe=False)


def faculty_name(request):  # Deptartment_id From FrontEnd (Faculty Name)
    list1 = []
    data_values = {}
    if(request.method == 'POST'):
        data = json.loads(request.body.decode("utf-8"))
        dept_select = data['Dept_id']
        # dept_select=request.GET['Dept_id']
        emp_sep_cnt = EmployeeSeparation.objects.filter(emp_id__dept=dept_select).filter(status="RESIGN").values_list('emp_id', flat=True)
        # pro=EmployeePrimdetail.objects.filter(dept=dept_select,current_pos=836).exclude(emp_id__in=emp_sep_cnt).count()

        qu = EmployeePrimdetail.objects.filter(dept=dept_select).exclude(emp_id__in=emp_sep_cnt).exclude(emp_id__isnull=True).values('name', 'desg__value', 'emp_id', 'email', 'title__value', 'doj', 'emp_status', 'emp_type__value').order_by('desg', 'doj')

        query2 = EmployeePrimdetail.objects.filter(dept=dept_select, emp_status='ACTIVE').exclude(emp_id__isnull=True).values('name', 'desg__value', 'emp_id', 'email', 'title__value', 'doj', 'emp_status', 'emp_type__value').order_by('desg', 'doj')

        query1 = (qu | query2).distinct()
        print(qu)
        for i in range(len(query1)):
            query2 = EmployeePerdetail.objects.filter(emp_id=query1[i]['emp_id']).exclude(image_path__isnull=True).values('image_path', 'linked_in_url')
            try:
                image_path = settings.BASE_URL2 + "Musterroll/Employee_images/" + query2[0]['image_path']
                name = query1[i]['title__value'] + '. ' + query1[i]['name']
                url = query2[0]['linked_in_url']

            except:
                image_path = settings.BASE_URL2 + "Musterroll/Employee_images/default.png"
                name = query1[i]['name']
                url = "#"
            query1[i]['image_path'] = image_path
            query1[i]['name'] = name
            query1[i]['linked_in_url'] = url
            query1[i]['qualification'] = get_highest_qualification(query1[i]['emp_id'])
        data_values = {'data': list(query1)}
    return JsonResponse(data_values, safe=False)


def hodspeak(request):  # HodSpeak to Frontend
    data_values = {}
    if(request.method == 'POST'):
        data = json.loads(request.body.decode("utf-8"))
        dept_select = data['Dept_id']
        query = EmployeePrimdetail.objects.filter(dept=dept_select, desg=676).values('emp_id', 'name', 'title__value')
        query1 = WebDeptData2.objects.filter(Dept=dept_select).filter(Type=984).values('title', 'text', 'Type__value')
        if(len(query1) > 0):
            for i in range(len(query)):
                query2 = EmployeePerdetail.objects.filter(emp_id=query[i]['emp_id']).values('image_path')
                image_path = settings.BASE_URL2 + "Musterroll/Employee_images/" + query2[0]['image_path']
                query1[i]['image_path'] = image_path
                try:
                    query1[i]['name'] = query[i]['title__value'] + '. ' + query[i]['name']
                except:
                    query1[i]['name'] = query[i]['name']
        data_values = {'data': list(query1)}
    return JsonResponse(data_values, safe=False)


def vision_mission(request):  # Vision to Frontend
    data_values = {}
    if(request.method == 'POST'):
        arr = []
        data = json.loads(request.body.decode("utf-8"))
        dept_select = data['Dept_id']
        query1 = WebDeptData2.objects.filter(Dept=dept_select).filter(Type=985).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')

        query2 = WebDeptData2.objects.filter(Dept=dept_select).filter(Type=986).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')
        for i in range(len(query2)):
            query2[i]['text'] = (query2[i]['text'].split('<br>'))
        data_values = {'data1': list(query1), 'data2': list(query2)}
    return JsonResponse(data_values, safe=False)


def peos(request):  # PEOS to Frontend
    data_values = {}
    if(request.method == 'POST'):
        data = json.loads(request.body.decode("utf-8"))
        dept_select = data['Dept_id']
        query1 = WebDeptData2.objects.filter(Dept=dept_select).filter(Type=987).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')
        for i in range(len(query1)):
            query1[i]['text'] = (query1[i]['text'].split('<br>'))

        query2 = WebDeptData2.objects.filter(Dept=dept_select).filter(Type=988).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')
        for i in range(len(query2)):
            query2[i]['text'] = (query2[i]['text'].split('<br>'))
        data_values = {'data1': list(query1), 'data2': list(query2)}
    return JsonResponse(data_values, safe=False)


def infrastructure(request):  # Infrastructure to Frontend
    data_values = {}
    if(request.method == 'POST'):
        data = json.loads(request.body.decode("utf-8"))
        dept_select = data['Dept_id']
        query1 = WebDeptData2.objects.filter(Dept=dept_select).filter(Type=989).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')
        data_values = {'data': list(query1)}
    return JsonResponse(data_values, safe=False)


def Labs(request):  # Labs to Frontend
    data_values = {}
    status = 500
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        dept = data['Dept_id']
        s = WebDeptData2.objects.filter(Dept=dept, Type=990).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image', 'pmail__first_name', 'related_pmail')
        data_values = {'data': list(s)}
        status = 200
    return JsonResponse(data_values, safe=False, status=status)


def HobbyClubs(request):  # Hobby Clubs to Frontend(
    data_values = {}
    status = 500
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        dept = data['Dept_id']
        s = WebDeptData2.objects.filter(Dept=dept, Type=991).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image', 'related_pmail')
        data_values = {'data': list(s)}
        status = 200
    return JsonResponse(data_values, safe=False, status=status)


def Industrial(request):  # Industrial to Frontend
    data_values = {}
    status = 500
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        dept = data['Dept_id']
        s = WebDeptData2.objects.filter(Dept=dept, Type=998).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')
        data_values = {'data': list(s)}
        status = 200
    return JsonResponse(data_values, safe=False, status=status)


def Links(request):  # Important Links to Frontend
    data_values = {}
    status = 500
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        dept = data['Dept_id']
        s = WebDeptData2.objects.filter(Dept=dept, Type=1347).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')
        data_values = {'data': list(s)}
        status = 200
    return JsonResponse(data_values, status=status)


def Accordance(request):  # Accordian And Slider Images Of Deptartment
    data_values = {}
    status = 500
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        dept = data['Dept_id']
        query1 = WebDeptData2.objects.filter(Dept=dept, Type=992).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')
        query2 = WebDeptData2.objects.filter(Dept=dept, Type=1018).values('Dept__value', 'Type__value', 'image')
        data_values = {'data1': list(query1), 'data2': list(query2)}
    status = 200
    return JsonResponse(data_values, safe=False, status=status)


def Achievements(request):  # Achievments to Frontend
    data_values = {}
    status = 500
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        dept = data['Dept_id']
        s = WebDeptData2.objects.filter(Dept=dept, Type=982).values('Dept__value', 'Type__value', 'title', 'text', 'lab_place', 'image')
        data_values = {'data': list(s)}
        status = 200
    return JsonResponse(data_values, safe=False, status=status)


def add_student(request):  # register form to Frontend
    data_values = {}
    status = 500
    if request.method == 'POST':
        data = json.loads(returnequest.body.decode("utf-8"))
        status = 200
    return JsonResponse(data_values, safe=False, status=status)


def Anouncement_add(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)

                    print(data)
                    fdate = datetime.strptime(str(data["fdate"]).split('T')[0], "%Y-%m-%d").date()
                    tdate = datetime.strptime(str(data["tdate"]).split('T')[0], "%Y-%m-%d").date()
                    input_data = data["data"]
                    input_link = data["link"]
                    TYPE = data['type']
                    query = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    department = EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    pmail = AuthUser.objects.get(username=request.session["hash1"])
                    # Type=EmployeeDropdown.objects.get(sno=1021)
                    if(TYPE == "1" or TYPE == "3"):
                        Type = EmployeeDropdown.objects.get(sno=980)
                        query1 = WebDeptData.objects.create(Dept=department, pmail=pmail, Type=Type, Fdate=fdate, Tdate=tdate, text=input_data, links=input_link)
                    if(TYPE == "2" or TYPE == "3"):
                        Type = EmployeeDropdown.objects.get(sno=1021)
                        query1 = WebDeptData.objects.create(Dept=department, pmail=pmail, Type=Type, Fdate=fdate, Tdate=tdate, text=input_data, links=input_link)
                    status = 200
                    data_values = {"msg": "Data Added"}
                elif(request.method == 'GET'):
                    if(request.GET['request_type'] == 'views'):
                        query3 = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                        Type = EmployeeDropdown.objects.get(sno=1021)
                        Type2 = EmployeeDropdown.objects.get(sno=980)
                        today = str(date.today())
                        pmail = AuthUser.objects.get(username=request.session["hash1"])
                        query4 = WebDeptData.objects.filter(Dept=query3[0]['dept'], Tdate__gte=today).filter(Q(Type=Type) | Q(Type=Type2)).values('links', 'text', 'Type__value', 'Tdate', 'Fdate', 'Id')
                        # print (query4.query)
                        status = 200
                        data_values = {'data': list(query4)}
                    else:
                        status = 500
                        data_values = {'msg': 'Data cannot be Viewed'}
                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    id = data["id"]
                    query = WebDeptData.objects.filter(Id=id).delete()
                    status = 200
                    data_values = {"msg": "Data Deleted"}
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    id = data["id"]
                    fdate = data["fdate"]
                    tdate = data["tdate"]
                    input_data = data["data"]
                    input_link = data["link"]
                    query = WebDeptData.objects.filter(Id=id).update(Fdate=fdate, Tdate=tdate, text=input_data, links=input_link)
                    status = 200
                    data_values = {"msg": "Data Updated"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def Events_add(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    fdate = data["fdate"]
                    tdate = data["tdate"]
                    input_data = data["data"]
                    input_link = data['link']
                    TYPE = data['type']
                    query = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    department = EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    pmail = AuthUser.objects.get(username=request.session["hash1"])
                    if(TYPE == "1" or TYPE == "3"):
                        Type = EmployeeDropdown.objects.get(sno=979)
                        query1 = WebDeptData.objects.create(Dept=department, Type=Type, pmail=pmail, Fdate=fdate, Tdate=tdate, text=input_data, links=input_link)
                    if(TYPE == "2" or TYPE == "3"):
                        Type = EmployeeDropdown.objects.get(sno=1020)
                        query1 = WebDeptData.objects.create(Dept=department, Type=Type, pmail=pmail, Fdate=fdate, Tdate=tdate, text=input_data, links=input_link)
                    status = 200
                    data_values = {"msg": "Data Added"}
                elif(request.method == 'GET'):
                    if(request.GET['request_type'] == 'view'):
                        query3 = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                        today = str(date.today())
                        Type = EmployeeDropdown.objects.get(sno=1020)
                        Type2 = EmployeeDropdown.objects.get(sno=979)
                        query4 = WebDeptData.objects.filter(Dept=query3[0]['dept'], Tdate__gte=today).filter(Q(Type=Type) | Q(Type=Type2)).values('links', 'text', 'Type__value', 'Tdate', 'Id', 'Fdate')
                        status = 200
                        data_values = {'data': list(query4)}
                    else:
                        status = 500
                        data_values = {'msg': 'Data cannot be Viewed'}
                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    id = data["id"]
                    query = WebDeptData.objects.filter(Id=id).delete()
                    status = 200
                    data_values = {"msg": "Data Deleted"}
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    id = data["id"]
                    fdate = data["fdate"]
                    tdate = data["tdate"]
                    input_data = data["data"]
                    input_link = data["link"]
                    query = WebDeptData.objects.filter(Id=id).update(Fdate=fdate, Tdate=tdate, text=input_data, links=input_link)
                    status = 200
                    data_values = {"msg": "Data Updated"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def Industry_add(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    input_data = data["data"].encode('ascii', 'ignore').decode('ascii')
                    input_link = data['title']
                    query = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    department = EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    pmail = AuthUser.objects.get(username=request.session["hash1"])
                    Type = EmployeeDropdown.objects.get(sno=998)
                    query1 = WebDeptData2.objects.create(Dept=department, Type=Type, pmail=pmail, text=input_data, title=input_link)
                    status = 200
                    data_values = {"msg": "Data Added"}
                elif(request.method == 'GET'):
                    if(request.GET['request_type'] == 'view'):
                        query3 = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                        Type = EmployeeDropdown.objects.get(sno=998)
                        query4 = WebDeptData2.objects.filter(Dept=query3[0]['dept'], Type=Type).values('Id', 'title', 'text')
                        status = 200
                        data_values = {'data': list(query4)}
                    else:
                        status = 500
                        data_values = {'msg': 'Data cannot be Viewed'}
                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    id = data["id"]
                    query = WebDeptData2.objects.filter(Id=id).delete()
                    status = 200
                    data_values = {"msg": "Data Deleted"}
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    id = data["id"]
                    input_data = data["title"]
                    input_link = data["data"].encode('ascii', 'ignore').decode('ascii')
                    query = WebDeptData2.objects.filter(Id=id).update(title=input_data, text=input_link)
                    status = 200
                    data_values = {"msg": "Data Updated"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def Achieve_add(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    input_data = data["data"].encode('ascii', 'ignore').decode('ascii')
                    input_link = data['title']
                    query = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    department = EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    pmail = AuthUser.objects.get(username=request.session["hash1"])
                    Type = EmployeeDropdown.objects.get(sno=982)
                    query1 = WebDeptData2.objects.create(Dept=department, Type=Type, pmail=pmail, text=input_data, title=input_link)
                    status = 200
                    data_values = {"msg": "Data Added"}
                elif(request.method == 'GET'):
                    if(request.GET['request_type'] == 'view'):
                        query3 = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                        Type = EmployeeDropdown.objects.get(sno=982)
                        query4 = WebDeptData2.objects.filter(Dept=query3[0]['dept'], Type=Type).values('Id', 'title', 'text')
                        status = 200
                        data_values = {'data': list(query4)}
                    else:
                        status = 500
                        data_values = {'msg': 'Data cannot be Viewed'}
                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    id = data["id"]
                    query = WebDeptData2.objects.filter(Id=id).delete()
                    status = 200
                    data_values = {"msg": "Data Deleted"}
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    id = data["id"]
                    input_data = data["title"]
                    input_link = data["data"].encode('ascii', 'ignore').decode('ascii')
                    query = WebDeptData2.objects.filter(Id=id).update(title=input_data, text=input_link)
                    status = 200
                    data_values = {"msg": "Data Updated"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def Hobby_add(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    input_data = data["data"].encode('ascii', 'ignore').decode('ascii')
                    input_link = data['title']
                    input_coor = data['coordinator']
                    query = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    department = EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    pmail = AuthUser.objects.get(username=request.session["hash1"])
                    Type = EmployeeDropdown.objects.get(sno=991)
                    query1 = WebDeptData2.objects.create(Dept=department, Type=Type, pmail=pmail, text=input_data, title=input_link, related_pmail=input_coor)
                    status = 200
                    data_values = {"msg": "Data Added"}
                elif(request.method == 'GET'):
                    if(request.GET['request_type'] == 'view'):
                        query3 = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                        Type = EmployeeDropdown.objects.get(sno=991)
                        query4 = WebDeptData2.objects.filter(Dept=query3[0]['dept'], Type=Type).values('Id', 'title', 'text', 'related_pmail')
                        status = 200
                        data_values = {'data': list(query4)}
                    else:
                        status = 500
                        data_values = {'msg': 'Data cannot be Viewed'}
                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    id = data["id"]
                    query = WebDeptData2.objects.filter(Id=id).delete()
                    status = 200
                    data_values = {"msg": "Data Deleted"}
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    id = data["id"]
                    input_data = data["title"]
                    input_coordinator = data["coordinator"]
                    input_link = data["data"].encode('ascii', 'ignore').decode('ascii')
                    query = WebDeptData2.objects.filter(Id=id).update(title=input_data, text=input_link, related_pmail=input_coordinator)
                    status = 200
                    data_values = {"msg": "Data Updated"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def Labs_add(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    input_data = data["data"].encode('ascii', 'ignore').decode('ascii')
                    input_link = data['title']
                    input_coor = data['pmail__first_name']
                    # print(input_coor)
                    input_place = data['place']
                    query = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    department = EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    input_coor = AuthUser.objects.get(username=input_coor)
                    # print(input_data)
                    Type = EmployeeDropdown.objects.get(sno=990)
                    query1 = WebDeptData2.objects.create(Dept=department, Type=Type, pmail=input_coor, text=input_data, title=input_link, lab_place=input_place)
                    status = 200
                    data_values = {"msg": "Data Added"}
                elif(request.method == 'GET'):
                    if(request.GET['request_type'] == 'view'):
                        query3 = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                        Type = EmployeeDropdown.objects.get(sno=990)
                        query4 = WebDeptData2.objects.filter(Dept=query3[0]['dept'], Type=Type).values('Id', 'title', 'text', 'related_pmail', 'lab_place', 'pmail', 'pmail__first_name', 'pmail__username')
                        # print(query4.query)
                        data = list(query4)
                        status = 200
                        data_values = {'data': data}
                    else:
                        status = 500
                        data_values = {'msg': 'Data cannot be Viewed'}
                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    id = data["id"]
                    query = WebDeptData2.objects.filter(Id=id).delete()
                    status = 200
                    data_values = {"msg": "Data Deleted"}
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    id = data["id"]
                    input_data = data["data"].encode('ascii', 'ignore').decode('ascii')
                    input_link = data['title']
                    input_coor = data['pmail__first_name']
                    input_place = data['place']
                    # query=EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    # department=EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    input_coor = AuthUser.objects.get(username=input_coor)
                    query = WebDeptData2.objects.filter(Id=id).update(text=input_data, title=input_link, pmail=input_coor, lab_place=input_place)
                    status = 200
                    data_values = {"msg": "Data Updated"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def Infra_add(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    input_data = data["data"].encode('ascii', 'ignore').decode('ascii')
                    input_link = data['title']
                    input_coor = data['pmail__first_name']
                    input_place = data['place']
                    query = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    department = EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    input_coor = AuthUser.objects.get(username=input_coor)
                    Type = EmployeeDropdown.objects.get(sno=989)
                    query1 = WebDeptData2.objects.create(Dept=department, Type=Type, pmail=input_coor, text=input_data, title=input_link, image=input_place)
                    status = 200
                    data_values = {"msg": "Data Added"}
                elif(request.method == 'GET'):
                    if(request.GET['request_type'] == 'view'):
                        query3 = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                        Type = EmployeeDropdown.objects.get(sno=989)
                        query4 = WebDeptData2.objects.filter(Dept=query3[0]['dept'], Type=Type).values('Id', 'title', 'priority', 'related_pmail', 'text', 'image')
                        data = list(query4)
                        status = 200
                        data_values = {'data': data}
                    else:
                        status = 500
                        data_values = {'msg': 'Data cannot be Viewed'}
                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    id = data["id"]
                    query = WebDeptData2.objects.filter(Id=id).delete()
                    status = 200
                    data_values = {"msg": "Data Deleted"}
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    id = data["id"]
                    input_data = data["data"].encode('ascii', 'ignore').decode('ascii')
                    input_link = data['title']
                    input_coor = data['pmail__first_name']
                    input_place = data['place']
                    input_coor = AuthUser.objects.get(username=input_coor)
                    query = WebDeptData2.objects.filter(Id=id).update(text=input_data, title=input_link, pmail=input_coor, lab_place=input_place)
                    status = 200
                    data_values = {"msg": "Data Updated"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def Link_add(request):
    data_values = {}
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [1346])
            if(check == 200):
                if(request.method == 'POST'):
                    data = json.loads(request.body)
                    input_data = data["data"].encode('ascii', 'ignore').decode('ascii')
                    input_link = data['title']
                    query = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                    department = EmployeeDropdown.objects.get(sno=query[0]["dept"])
                    pmail = AuthUser.objects.get(username=request.session["hash1"])
                    Type = EmployeeDropdown.objects.get(sno=1347)
                    query1 = WebDeptData2.objects.create(Dept=department, Type=Type, pmail=pmail, text=input_data, title=input_link)
                    status = 200
                    data_values = {"msg": "Data Added"}
                elif(request.method == 'GET'):
                    if(request.GET['request_type'] == 'view'):
                        query3 = EmployeePrimdetail.objects.filter(emp_id=request.session["hash1"]).values("dept")
                        Type = EmployeeDropdown.objects.get(sno=1347)
                        query4 = WebDeptData2.objects.filter(Dept=query3[0]['dept'], Type=Type).values('Id', 'title', 'text')
                        status = 200
                        data_values = {'data': list(query4)}
                    else:
                        status = 500
                        data_values = {'msg': 'Data cannot be Viewed'}
                elif(request.method == 'DELETE'):
                    data = json.loads(request.body)
                    id = data["id"]
                    query = WebDeptData2.objects.filter(Id=id).delete()
                    status = 200
                    data_values = {"msg": "Data Deleted"}
                elif(request.method == 'PUT'):
                    data = json.loads(request.body)
                    id = data["id"]
                    input_data = data["title"]
                    input_link = data["data"].encode('ascii', 'ignore').decode('ascii')
                    query = WebDeptData2.objects.filter(Id=id).update(title=input_data, text=input_link)
                    status = 200
                    data_values = {"msg": "Data Updated"}
                else:
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 500
    return JsonResponse(data=data_values, status=status)


def employee_image(request):
    list1 = []
    # print (request.body)
    if(request.method == 'POST'):
        data = json.loads(request.body.decode("utf-8"))
        pmail = data['pmail']

        query1 = EmployeePrimdetail.objects.filter(emp_id=pmail).exclude(emp_id__isnull=True).values('name', 'desg__value', 'emp_id', 'email', 'title__value').order_by('desg')
        for i in range(len(query1)):
            query2 = EmployeePerdetail.objects.filter(emp_id=query1[i]['emp_id']).exclude(image_path__isnull=True).values('image_path')
            try:
                image_path = settings.BASE_URL2 + "Musterroll/Employee_images/" + query2[0]['image_path']
                name = query1[i]['title__value'] + '. ' + query1[i]['name']
            except:
                image_path = settings.BASE_URL2 + "Musterroll/Employee_images/default.png"
                name = query1[i]['name']
            query1[i]['image_path'] = image_path
            query1[i]['name'] = name
        data_values = {'data': list(query1)}
        return JsonResponse(data_values, safe=False)


def insert_mercedes(request):
    data = {}
    list1 = []
    status = 502
    request.session['user_id'] = 5
    # if request.method == 'GET':
    # 	order_id="AMCDAM18_123754"

    # 	request.session['user_id']=1
    # 	data_dict = {'MID':constants.PAYTM_MERCHANT_MID,'ORDER_ID':order_id,'TXN_AMOUNT':0.01,'CUST_ID':"741234",'INDUSTRY_TYPE_ID':constants.INDUSTRY_TYPE_ID,'WEBSITE': constants.PAYTM_MERCHANT_WEBSITE,'CHANNEL_ID':constants.CHANNEL_ID,'CALLBACK_URL':constants.CALLBACK_URL}
    # 	param_dict = data_dict
    # 	#param_dict['PAYTM_TXN_URL']=constants.PAYTM_TXN_URL
    # 	param_dict['CHECKSUMHASH'] = CheckSum.generate_checksum(data_dict, constants.PAYTM_MERCHANT_KEY)
    # 	data=param_dict

    # 	print(data)
    # 	#r=requests.post(constants.PAYTM_TXN_URL, data=json.dumps(param_dict))
    # 	#print(r)
    if request.method == 'POST':
        data = json.loads(request.body)
        # print(data)
        student_name = data['stuname']
        father_name = data['fathername']
        mother_name = data['motherName']
        student_mob = data['CandidatephoneNumber']
        student_email = data['email']
        father_mob = data['FatherphoneNumber']
        dob = datetime.strptime(str(data['dob']), "%Y-%m-%d")
        # category=data['Categoey']
        gender = data['gender']
        address = data['address']
        city = data['city']
        district = data['district']
        pin_code = int(data['pincode'])
        ten_board = data['highschoolboard']
        ten_year = int(data['highschoolyear'])
        ten_grading = data['gradingoption']

        if ten_grading is None:
            ten_grading = "N"

        # photo=data['ApplicantPhoto']
        if ten_grading == "Y":
            ten_grade = data['highschoolcgpa']
            ten_marks = None
            ten_max_marks = None
        else:
            ten_grade = None
            ten_marks = int(data['highschoolMarks'])
            ten_max_marks = int(data['highschooloutofMarks'])

        twelve = data['interptionyn']
        if twelve == "Y":
            twelve_board = data['ddlInterBoard']
            twelve_year = data['interyear']
            twelve_grading = data['intergradingoption']
            if twelve_grading is None:
                twelve_grading = "N"
            if twelve_grading == "Y":
                twelve_marks = None
                twelve_max_marks = None
                twelve_grade = float(data['intercgpa'])
            else:
                twelve_marks = int(data['interMarks'])
                twelve_max_marks = int(data['interoutofMarks'])
                twelve_grade = None
        else:
            twelve_board = None
            twelve_year = None
            twelve_grading = None
            twelve_marks = None
            twelve_max_marks = None
            twelve_grade = None
            twelve_marks = None
            twelve_max_marks = None
            twelve_grade = None

        diploma = data['diplomoptionyn']
        if diploma == "Y":
            diplomacourse = data['diplomacourse']
            diploma_board = data['diplomaboard']
            diploma_year = data['diplomayear']
            diploma_grading = data['diplomagradingoption']
            if diploma_grading is None:
                diploma_grading = "N"
            if diploma_grading == "Y":
                diploma_marks = None
                diploma_max_marks = None
                diploma_grade = float(data['diplomacgpa'])
            else:
                diploma_marks = int(data['diplomaMarks'])
                diploma_max_marks = int(data['diplomaoutofMarks'])
                diploma_grade = None
        else:
            diplomacourse = None
            diploma_board = None
            diploma_year = None
            diploma_grading = None
            diploma_marks = None
            diploma_max_marks = None
            diploma_grade = None
            diploma_marks = None
            diploma_max_marks = None
            diploma_grade = None

        graduation = data['graduationcourse']
        graduation_university = data['graduationboard']
        graduation_college = data['graduationCollege']
        graduation_year = data['graduationyear']
        graduation_grading = data['graduationgradingoption']
        graduationoptionyn = data['graduationoptionyn']
        if graduation_grading is None:
            graduation_grading = "N"
        if graduation_grading == "Y":
            graduation_marks = None
            graduation_max_marks = None
            graduation_grade = float(data['graduationcgpa'])
        else:
            graduation_marks = int(data['graduationMarks'])
            graduation_max_marks = int(data['graduationoutof'])
            graduation_grade = None

        # btech_status=data['be_btech_status']
        student_aadhar_num = (data['aadharNO'])
        amount = 1
        txnid = None
        qry_insert = Mercedes.objects.create(father_mob=father_mob, student_mob=student_mob, student_name=student_name, father_name=father_name, mother_name=mother_name, student_email=student_email, dob=dob, gender=gender, address=address, city=city, district=district, pin_code=pin_code, ten_board=ten_board, ten_marks=ten_marks, ten_max_marks=ten_max_marks, ten_year=ten_year, ten_grading=ten_grading, ten_grade=ten_grade, twelve_board=twelve_board, twelve_marks=twelve_marks, twelve_max_marks=twelve_max_marks, twelve_year=twelve_year, twelve_grading=twelve_grading, twelve_grade=twelve_grade, diploma=diploma, diplomacourse=diplomacourse, diploma_board=diploma_board, diploma_marks=diploma_marks, diploma_max_marks=diploma_max_marks, diploma_year=diploma_year, diploma_grading=diploma_grading, diploma_grade=diploma_grade, graduation_university=graduation_university, graduation_college=graduation_college, graduation_marks=graduation_marks, graduation_max_marks=graduation_max_marks, graduation_year=graduation_year, graduation_grading=graduation_grading, graduation_grade=graduation_grade, graduation_course=graduation, graduationoptionyn=graduationoptionyn, student_aadhar_num=student_aadhar_num, amount=amount)

        q_id = Mercedes.objects.filter(student_name=student_name).values('id', 'student_email').order_by('-id')[:1]
        order_id = "AMCDAM19_" + str(q_id[0]['id'])

        request.session['user_id'] = q_id[0]['id']
        data_dict = {'MID': constants.PAYTM_MERCHANT_MID, 'ORDER_ID': order_id, 'TXN_AMOUNT': "500", 'CUST_ID': q_id[0]['student_email'], 'INDUSTRY_TYPE_ID': constants.INDUSTRY_TYPE_ID, 'WEBSITE': constants.PAYTM_MERCHANT_WEBSITE, 'CHANNEL_ID': constants.CHANNEL_ID, 'CALLBACK_URL': constants.CALLBACK_URL}
        param_dict = data_dict
        # param_dict['PAYTM_TXN_URL']=constants.PAYTM_TXN_URL
        param_dict['CHECKSUMHASH'] = CheckSum.generate_checksum(data_dict, constants.PAYTM_MERCHANT_KEY)
        data = param_dict
        # data_dict = {'MID':constants.MERCHANT_ID,'ORDER_ID':order_id,'TXN_AMOUNT': constants.bill_amount,'CUST_ID':student_aadhar_num,'INDUSTRY_TYPE_ID':constants.INDUSTRY_TYPE_ID,'WEBSITE': constants.PAYTM_WEBSITE,'CHANNEL_ID':constants.CHANNEL_ID,'CALLBACK_URL':CHANNEL_ID.CALLBACK_URL}
  #       param_dict = data_dict
  #       param_dict['CHECKSUMHASH'] = CheckSum.generate_checksum(data_dict, constants.MERCHANT_KEY)

    status = 200
    # print(param_dict)
    # print(data)
    # list1.append(param_dict)
    # print(list1)
    # print(json.dumps(list1))
    jsonified = json.dumps(data, cls=MyEncoder)
    # print(list(param_dict))
    return JsonResponse(data=jsonified, status=status, safe=False)
    # return redirect("http://stackoverflow.com/")
    # return render_to_response('test.html', { 'foo': 123, 'bar': 456 })


def payment_complete(request):
    msg = ""
    error = True
    data = {}
    if request.method == "POST":

        MERCHANT_KEY = constants.PAYTM_MERCHANT_KEY
        data_dict = {}
        for key in request.POST:
            data_dict[key] = request.POST[key]
        user_id = data_dict['ORDERID'].split("_")[1]
        print(user_id)
        verify = CheckSum.verify_checksum(data_dict, MERCHANT_KEY, data_dict['CHECKSUMHASH'])
        print("Hi")
        if verify:
            q_det = Mercedes.objects.filter(id=user_id).values('amount', 'student_name', 'student_email')
            if len(q_det) > 0:
                url = "https://secure.paytm.in/oltp/HANDLER_INTERNAL/TXNSTATUS?JsonData={%27MID%27:%27KriIns08204252501061%27,%27ORDERID%27:%27" + data_dict['ORDERID'] + "%27}"
                print(url)
                r = requests.get(url)
                data = json.loads(r.text)
                print(data)
                print(q_det[0])
                if q_det[0]['amount'] >= float(data['TXNAMOUNT']) and data['STATUS'] == "TXN_SUCCESS":
                    error = False
                    msg = "Thank you, your transaction was successfull. Transaction ID: " + str(data['TXNID']) + "Order ID:" + data['ORDERID']
                    q_up = Mercedes.objects.filter(id=user_id).update(paid_status="PAID", txnid=data['TXNID'])

                    message = "<b>Dear " + q_det[0]['student_name'].title() + ",</b><br><br>Gretings from KIET Group of Institutions.<br><br>Thank you for the registration in <b>ADVANCE DIPLOMA IN AUTO MOTIVE MECHATRONICS (ADAM)</b>. We acknowledge the receipt of your registration fee.<br><br>You will be received hall-ticket on your registered email-id soon.<br><br><hr><br>Thanks and Regards,<br><br>KIET Group of Institutions, Ghaziabad<br><br>"
                    Thread(target=store_email, args=[q_det[0]['student_email'], "AMC DAM REGISTRATION", message, user_id, q_det[0]['student_name']]).start()
                    #del request.session['user_id']
                else:
                    msg = "Oh Snap!. Sorry. Your transaction did not go through. If amount is already deducted, kindly contact at amc.dam@kiet.edu"

            else:
                msg = "Oh Snap!. Sorry. Your transaction did not go through. If amount is already deducted, kindly contact at amc.dam@kiet.edu"
        else:
            msg = "Session Expired"

    url2 = "https://tech.kiet.edu/index.html#/MCZBnZ_payment_status?error=" + str(error)

    return redirect(url2)


def store_email(send_to, subject, message, id, name):
    yag = yagmail.SMTP({'amc.dam@kiet.edu': 'AMC DAM'}, 'kiet@12345').send(send_to, subject, message)
    q_store = Mercedes.objects.filter(id=id).update(mail_send='Y')


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode("ASCII")  # <- or any other encoding of your choice
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
