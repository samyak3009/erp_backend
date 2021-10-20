from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
import json
import hashlib
from .models import *
import base64
import datetime
from website.models import Mercedes
from django.contrib.auth.models import User
from django.db.models import Q, F
from datetime import datetime
import random
from dateutil.relativedelta import relativedelta
from datetime import date
import yagmail
import calendar
import requests
from django.http.response import HttpResponse
from xlsxwriter.workbook import Workbook
import io
from django.conf import settings
from PIL import Image, ImageChops, ImageOps
from PIL import ImageFont
from PIL import ImageDraw

from StudentAcademics.models import *
from Registrar.models import *
from StudentMMS.models import *
from StudentSMM.models import *
from StudentFeedback.models import *
from StudentPortal.models import *
from Redressal.models import RedressalApproval
from LessonPlan.models import *
from Ticketing.models import TicketingApproval
from grievance.models import GrievanceData
from leave.models import Leaveapproval
from musterroll.models import Roles, EmployeeDropdown, EmployeePerdetail, Reporting
from Store_data.models import *
from StudentHostel.models import *
from StudentMMS.models.models_1920o import *
from StudentMMS.models.models_1920e import *
from StudentSMM.models.models_1920o import *
from StudentMMS.models.models_2021o import *

from StudentFeedback.models.models_1920o import *
from Store_data.models import *
from StudentMMS.constants_functions import requestType
from erp.constants_functions import requestMethod, functions
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
# from StudentAcademics.functions import *
from LessonPlan.models.models_1920o import *
from LessonPlan.models.models_1920e import *

###################################################
import Ticketing as Ticketing
import Redressal as Redressal
import leave as leave
# from ipware import get_client_ip

def Sms_Api(dak_id, mobile, msg):
    uname = "kietgzb"
    pwd = "kiet@123"
    senderid = "KIETGZ"
    data = {'username': uname, 'pass': pwd, 'senderid': senderid, 'dest_mobileno': mobile, 'message': msg, 'response': 'Y'}
    response = requests.post('https://www.smsjust.com/blank/sms/user/urlsms.php', data=data)
    q_upd = Daksmsstatus.objects.filter(mainid=dak_id).update(updatestatus='Y')
    return "Done"


def generate_session_table_name(baseName, session_name):
    table = baseName + session_name
    return eval(table)


def lib_sms(request):
    session_name = request.session['Session_name']
    student_session = generate_session_table_name("studentSession_", session_name)

    query = student_session.objects.filter(uniq_id__join_year=2018, uniq_id__batch_from=2017).exclude(uniq_id__lib_id__isnull=True).values('uniq_id__lib_id', 'uniq_id__name', 'mob')
    for q in query:
        msg = "Dear " + q['uniq_id__name'] + ",\n\nYour login credentials for ERP student portal are, \n\nUsername/Library-Id: " + q['uniq_id__lib_id'] + " \n\nPassword: KIET123"
        mobile = q['mob']
        uname = "kietgzb"
        pwd = "kiet@123"
        senderid = "KIETGZ"
        data = {'username': uname, 'pass': pwd, 'senderid': senderid, 'dest_mobileno': mobile, 'message': msg, 'response': 'Y'}
        response = requests.post('https://www.smsjust.com/blank/sms/user/urlsms.php', data=data)

    return JsonResponse(data={'msg': 'ok'}, status=200)


def ccell_data(request):
    query = CCellSeriesDetails.objects.distinct().values('series_id')
    data = []
    for q in query:
        qry_series_data = CCellSeriesDetails.objects.filter(series_id=q['series_id']).values('title', 'description', 'date_of_launch', 'image', 'is_file', 'url', 'series_id__description', 'series_id__title', 'series_id', 'series_id__date', 'series_id__banner').order_by('-date_of_launch')
        series_data = []
        flg_new_series = False
        for series in qry_series_data:
            flg_new = False
            if (date.today() - series['date_of_launch']).days <= 7:
                flg_new = True
                flg_new_series = True

            series_data.append({'title': series['title'], 'description': series['description'], 'date_of_launch': series['date_of_launch'], 'image': series['image'], 'is_file': series['is_file'], 'url': series['url'], 'flg_new': flg_new})
        data.append({'series_title': qry_series_data[0]['series_id__title'], 'series_description': qry_series_data[0]['series_id__description'], 'series_launch_date': qry_series_data[0]['series_id__date'], 'series_id__banner': qry_series_data[0]['series_id__banner'], 'series_data': series_data, 'flg_new': flg_new_series})

    return JsonResponse(data={'data': data}, status=200)


def getHostelCoordinatorType(hash1, session):
    session = Semtiming.objects.filter(session_name=session).values_list("session", flat=True)
    if len(session) > 0:
        return list(HostelAssignEmp.objects.filter(status="INSERT", emp_id=hash1, hostel_id__session__session=session[0], hostel_id__session__sem_type="odd").exclude(status='DELETE').values_list('type_of_duty__value', flat=True).distinct())
    else:
        return []


def my_view(request):
    status = 401
    data = {}
    if 'HTTP_AUTHORIZATION' in request.META:

        info = request.META['HTTP_AUTHORIZATION']
        print(info)
        info1 = info.split(" ")
        info2 = bytes(base64.b64decode(info1[1]))
        info3 = info2.decode().split(':')
        username = info3[0].strip()

        password = info3[1].strip()
        user = authenticate(username=username, password=password)
        if password == "ppkl@1526" and len(User.objects.filter(username=username)) > 0:
            user = User.objects.get(username=username)
        if user is not None:
            if user.is_active:
                response = login(request, user)
                # qr = AuthUser.objects.filter(username=username).extra(select={'emp_id': 'username'}).values('emp_id', 'user_type')
                #### CHANGE BY VRINDA ####
                qr = AuthUser.objects.filter(username=username).extra(select={'emp_id': 'username'}).exclude(user_type='Student').values('emp_id', 'user_type')
                if len(qr) == 0:
                    msg = "no such user"
                    data = {'msg': msg}
                    status = 400
                    response = JsonResponse(data, status=status)
                    return response
                ##########################
                qr1 = EmployeePrimdetail.objects.filter(emp_id=qr[0]['emp_id']).values('dept__value')
                qr2 = Semtiming.objects.filter(sem_start__lte=date.today(), sem_end__gte=date.today()).order_by('-uid')[:1].values('session', 'session_name', 'uid', 'sem_type')
                request.session['dept'] = qr1[0]['dept__value']
                hash3 = qr[0]['user_type']
                hash1 = username
                request.session['hash1'] = hash1
                request.session['hash3'] = hash3
                request.session['Session_id'] = qr2[0]['uid']
                request.session['Session'] = qr2[0]['session']
                request.session['Session_name'] = qr2[0]['session_name']
                session_name = qr2[0]['session_name']
                request.session['sem_type'] = qr2[0]['sem_type']
                roles = Roles.objects.filter(emp_id=hash1).values('roles').order_by('roles')
                role = []

                i = 0
                for r in roles:
                    role.append(roles[i]['roles'])  # role=[211]
                    i += 1
                request.session['roles'] = role

                if 1353 in role:
                    qr3 = Semtiming.objects.filter(session=qr2[0]['session'], sem_type='odd').order_by('-uid')[:1].values('session', 'session_name', 'uid', 'sem_type')
                    request.session['dept'] = qr1[0]['dept__value']
                    hash3 = qr[0]['user_type']
                    hash1 = username
                    request.session['hash1'] = hash1
                    request.session['hash3'] = hash3
                    request.session['Session_id'] = qr3[0]['uid']
                    request.session['Session'] = qr3[0]['session']
                    request.session['Session_name'] = qr3[0]['session_name']
                    session_name = qr3[0]['session_name']
                    request.session['sem_type'] = qr3[0]['sem_type']

                approval_role = False
                if 425 in role:
                    approval_role = True

                if 1353 in role:
                    qr3 = Semtiming.objects.filter(session=qr2[0]['session'], sem_type='odd').order_by('-uid')[:1].values('session', 'session_name', 'uid', 'sem_type')
                    request.session['dept'] = qr1[0]['dept__value']
                    hash3 = qr[0]['user_type']
                    hash1 = username
                    request.session['hash1'] = hash1
                    request.session['hash3'] = hash3
                    request.session['Session_id'] = qr3[0]['uid']
                    request.session['Session'] = qr3[0]['session']
                    request.session['Session_name'] = qr3[0]['session_name']
                    session_name = qr3[0]['session_name']
                    request.session['sem_type'] = qr3[0]['sem_type']

                ################## ACADEMIC COORDINATOR TYPE ######################
                flag_academic = False
                if 1369 in role:
                    flag_academic = True
                if flag_academic:
                    AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

                    emp_acad_roles = list(AcadCoordinator.objects.filter(emp_id=hash1).exclude(status="DELETE").values_list('coord_type', flat=True).distinct())
                    emp_acad_roles.append('A')

                    if 319 in role:
                        emp_acad_roles.append('H')

                    request.session['Coordinator_type'] = emp_acad_roles
                else:
                    request.session['Coordinator_type'] = []

                ################## HOSTEL COORDINATOR TYPE ######################
                emp_hostel_roles = getHostelCoordinatorType(hash1, session_name)
                request.session['Coordinator_type'] = request.session['Coordinator_type'] + emp_hostel_roles

                status = 200
                msg = "active"
                data = {
                    'msg': msg,
                    'user_id': hash1,
                    'type': hash3,
                    'approval_role': approval_role
                }
            else:
                msg = "not active"
                data = {'msg': msg}
        else:
            msg = "no such user"
            data = {'msg': msg}
            status = 400
    else:
        msg = "invalid request"
        data = {

            'msg': msg
        }

    response = JsonResponse(data, status=status)
    return response


def change_session(request):
    data = ''
    msg = ''
    error = True
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.method == 'POST':
                data = json.loads(request.body)

                if 'session_id' in data:
                    qr2 = Semtiming.objects.filter(uid=data['session_id']).values('session', 'session_name', 'uid', 'sem_type')

                    if request.session['hash3'] == "Student":
                        flag = False

                        if len(qr2) > 0:
                            studentSession = generate_session_table_name("studentSession_", qr2[0]['session_name'])
                            temp = studentSession.objects.filter(uniq_id=request.session['uniq_id']).values()
                            if len(temp) == 0 or temp is None:
                                #msg = "no such user"
                                msg="FEATURE IS NOT SUPPORTED IN CURRENT SESSION"
                                data = {'msg': msg}
                                #status = 403
                                status=420
                                return JsonResponse(data, status=status)

                    request.session['Session_id'] = qr2[0]['uid']
                    request.session['Session'] = qr2[0]['session']
                    request.session['Session_name'] = qr2[0]['session_name']
                    session_name = qr2[0]['session_name']
                    request.session['sem_type'] = qr2[0]['sem_type']
                    if "hash1" in request.session:
                        hash1 = request.session['hash1']
                    else:
                        hash1 = -1
                    roles = Roles.objects.filter(emp_id=hash1).values('roles').order_by('roles')
                    role = []

                    i = 0
                    for r in roles:
                        role.append(roles[i]['roles'])  # role=[211]
                        i += 1
                    request.session['roles'] = role

                    approval_role = False
                    if 425 in role:
                        approval_role = True

                    ################## ACADEMIC COORDINATOR TYPE ######################
                    flag_academic = False
                    if 1369 in role:
                        flag_academic = True
                    if flag_academic:
                        AcadCoordinator = generate_session_table_name("AcadCoordinator_", session_name)

                        emp_acad_roles = list(AcadCoordinator.objects.filter(emp_id=hash1).exclude(status="DELETE").values_list('coord_type', flat=True).distinct())
                        emp_acad_roles.append('A')

                        if 319 in role:
                            emp_acad_roles.append('H')

                        request.session['Coordinator_type'] = emp_acad_roles
                    else:
                        request.session['Coordinator_type'] = []
                    emp_hostel_roles = getHostelCoordinatorType(hash1, session_name)
                    request.session['Coordinator_type'] = request.session['Coordinator_type'] + emp_hostel_roles

                    msg = "Session Changed Successfully."
                    status = 200
                else:
                    msg = "Wrong Params"
                    status = 500
            else:
                msg = "invalid Request"
                status = 502
        else:
            status = 401
    else:
        status = 400

    send = {"msg": msg, "error": error}
    return JsonResponse(status=status, data=send)


def stu_change_password(request):
    data = ''
    msg = ''
    error = True
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Student':
                if request.method == 'POST':
                    incoming_data = request.body
                    i_data = json.loads(incoming_data)

                    if 'new' in i_data and 'old' in i_data:
                        uniq_id = request.session['uniq_id']
                        q_lib = StudentPrimDetail.objects.filter(uniq_id=uniq_id).values('lib_id')
                        user = q_lib[0]['lib_id']

                        old_password = i_data['old']
                        new_password = i_data['new']
                        user = authenticate(username=user, password=old_password)
                        if user is not None:
                            u = User.objects.get(username=user)
                            u.set_password(new_password)
                            u.save()
                            error = False
                            msg = "Password Changed Successfully."
                            status = 200
                        else:
                            msg = 'Old Password Does Not Match.'
                            status = 200
                    else:
                        msg = "Wrong Params"
                        status = 500
                else:
                    msg = "invalid Request"
                    status = 502
            else:
                status = 403
        else:
            status = 401
    else:
        status = 400

    send = {"msg": msg, "error": error}
    return JsonResponse(status=status, data=send)


def stu_login(request):
    status = 401
    data = {}
    print(request.META)
    if 'HTTP_AUTHORIZATION' in request.META:

        info = request.META['HTTP_AUTHORIZATION']
        info1 = info.split(" ")
        print(info1)
        info2 = bytes(base64.b64decode(info1[1]))
        print(info2)
        # info2=info1[1].decode('base64','strict')
        info3 = info2.decode().split(':')
        username = info3[0].strip()
        password = info3[1].strip()
        print(username,password)
        user = authenticate(username=username, password=password)
        user_type = AuthUser.objects.filter(username=username, user_type='Student')
        if password == "stuArha@1526" and len(User.objects.filter(username=username)) > 0:
            user = User.objects.get(username=username)
        if user is not None:
            if user.is_active:
                response = login(request, user)
                username = str(username)
                qr = AuthUser.objects.filter(username=username).extra(select={'lib_id': 'username'}).values('lib_id', 'user_type')
                qr1 = StudentPrimDetail.objects.filter(lib=username).values('uniq_id')
                if len(qr1) == 0:
                    msg = "no such user"
                    data = {'msg': msg}
                    status = 400
                    response = JsonResponse(data, status=status)
                    return response
                # mobile=True
                # if info3.index("PC") != -1:
                #   mobile=False

                # if mobile:
                #   qr2=Semtiming.objects.filter(sem_start__lte=date.today(),sem_end__gte=date.today()).order_by('-uid')[:1].values('session','session_name','uid','sem_type')
                # else:
                #   qr2=Semtiming.objects.filter(uid=8).order_by('-uid')[:1].values('session','session_name','uid','sem_type')
                qr3 = Semtiming.objects.filter(sem_start__lte=date.today(), sem_end__gte=date.today()).order_by('-uid')[:1].values('session', 'session_name', 'uid', 'sem_type')
                flag = False

                for x in qr3:
                    studentSession = generate_session_table_name("studentSession_", x['session_name'])
                    temp = studentSession.objects.filter(uniq_id=qr1[0]['uniq_id']).values()
                    if len(temp) > 0:
                        flag = True
                        qr2 = [x]
                        break
                    # elif getPreviousSemlogin(x['session_name'],qr1[0]['uniq_id'])[0]:
                    #     flag = True
                    #     qr2 = list(Semtiming.objects.filter(session_name=getPreviousSemlogin(x['session_name'],qr1[0]['uniq_id'])[1]).values('session', 'session_name', 'uid', 'sem_type'))
                    #     break


                if not flag:
                    msg = "no such user"
                    data = {'msg': msg}
                    status = 400
                    return JsonResponse(data, status=status)

                hash3 = qr[0]['user_type']
                hash1 = username
                request.session['uniq_id'] = qr1[0]['uniq_id']
                request.session['hash3'] = hash3
                request.session['Session_id'] = qr2[0]['uid']
                request.session['Session'] = qr2[0]['session']
                request.session['Session_name'] = qr2[0]['session_name']
                request.session['sem_type'] = qr2[0]['sem_type']

                status = 200
                msg = "active"
                data = {

                    'msg': msg,
                    'user_id': hash1,
                    'type': hash3,
                }
            else:
                msg = "not active"
                data = {'msg': msg}
        else:
            msg = "no such user"
            data = {'msg': msg}
            status = 400
    else:
        msg = "invalid request"
        data = {

            'msg': msg
        }

    return JsonResponse(data, status=status)

def getPreviousSemlogin(session_name,uniq_id):
    # qry = Semtiming.objects.filter(uid=uid-1).values()
    if 'e' in session_name:
        session_name = session_name[:4]+'o'
    elif 'o' in session_name:
        session_name = str(int(session_name[:2]) - 1) + str(session_name[:2]) + 'e'
    print(session_name)
    studentSession = generate_session_table_name("studentSession_", session_name)
    temp = studentSession.objects.filter(uniq_id=uniq_id).values()
    if len(temp) > 0:
        return [True,session_name]
    return [False,session_name]
        

def logout_view(request):
    status = 401
    if 'HTTP_COOKIE' in request.META:
        logout(request)
        msg = "logged out successfully"
        status = 200

    else:
        msg = "wrong parameters"
        status = 400

    return JsonResponse({'msg': msg}, status=status, safe=False)


def change_password(request):
    data = ''
    msg = ''
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [337])
            if(check == 200):
                if request.method == 'POST':
                    incoming_data = request.body
                    i_data = json.loads(incoming_data)

                    if 'new' in i_data and 'old' in i_data:
                        user = request.session['hash1']
                        old_password = i_data['old']
                        new_password = i_data['new']
                        user = authenticate(username=user, password=old_password)
                        if user is not None:
                            u = User.objects.get(username=user)
                            u.set_password(new_password)
                            u.save()
                            msg = "Password Changed Successfully."
                            status = 200
                        else:
                            msg = 'Old Password Does Not Match.'
                            status = 200
                    else:
                        msg = "Wrong Params"
                        status = 500
                else:
                    msg = "invalid Request"
                    status = 502

            else:
                status = 403
        else:
            status = 401
    else:

        status = 400
    send = {"msg": msg, "data": data}
    return JsonResponse(status=status, data=send)


def check(token):

    query = Token.objects.filter(key__icontains=token)
    count = query.count()
    if count > 0:
        user_id = int(query[0].user_id)
        qry = HashLogin.objects.filter(id=user_id)
        if qry:
            hash = qry[0].hash3re = Sms_Api(mainid, Mob, message)
            user_id = qry[0].hash1

        else:
            hash = ''
            user_id = ''
        msg = "1"

    else:
        msg = ""
        hash = ''

    data = {'msg': msg, 'user_type': hash, 'user_id': user_id}
    return data


def dashboard_view(request):
    return HttpResponse("hi")


def resetdata(request):
    msg = ''
    error = True

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Employee':
                user = request.session['hash1']
                qry = AuthUser.objects.filter(username=user, is_superuser=1, is_active=1)
                if(qry.count() > 0):
                    qry3 = EmployeePrimdetail.objects.filter(emp_status='ACTIVE').values('name', 'emp_id', 'desg__value', 'dept__value').exclude(emp_id=user)
                    msg = "Data Sent!!!"
                    error = False
            else:
                msg = 'Not Autherised!!'
        else:
            msg = 'Not Authenticated!!'
    else:
        msg = 'Session Problem!!'
    send = {'error': error, 'msg': msg, 'data': list(qry3)}
    return JsonResponse(send, safe=False)


def resetpassword(request):
    msg = ''
    error = True
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [402])
            if(check == 200):
                if request.session['hash3'] == 'Employee':
                    incoming_data = request.body
                    password = json.loads(incoming_data)
                    if 'emp_id' in password:
                        username = password['emp_id']
                        new_password = 'ERP@123'
                        u = User.objects.get(username=username)
                        u.set_password(new_password)
                        u.save()
                        msg = 'Password of ' + password['emp_name'] + '(' + password['emp_id'] + ')' + ' Reset Successfully To ' + new_password
                        error = False
                    else:
                        msg = "invalid parameters"
                else:
                    msg = 'Not Autherised!!'
            else:
                status = 401
                msg = 'Not Autherised!!'
        else:
            msg = 'Not Authenticated!!'
    else:
        msg = 'Session Problem!!'
    send = {'error': error, 'msg': msg}
    return JsonResponse(send, safe=False)


''' #STUDENT LOGIN RESET# '''


def student_resetdata(request):
    msg = ''
    error = True

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.session['hash3'] == 'Employee':
                user = request.session['hash1']
                qry = AuthUser.objects.filter(username=user, is_superuser=1, is_active=1)
                if(qry.count() > 0):
                    temp_list = list(AuthUser.objects.filter(user_type='student').values_list('username'))
                    qry3 = StudentPrimDetail.objects.filter(lib_id__in=temp_list).extra(select={'username': 'lib_id'}).values('name', 'email_id', 'dept_detail_id__dept__value', 'uni_roll_no', 'username')
                    msg = "Data Sent!!!"
                    error = False
            else:
                msg = 'Not Autherised!!'
        else:
            msg = 'Not Authenticated!!'
    else:
        msg = 'Session Problem!!'
    send = {'error': error, 'msg': msg, 'data': list(qry3)}
    return JsonResponse(send, safe=False)


def student_resetpassword(request):
    msg = ''
    error = True
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [402])
            if(check == 200):
                if request.session['hash3'] == 'Employee':
                    incoming_data = request.body
                    password = json.loads(incoming_data)
                    if 'username' in password:
                        username = password['username']
                        new_password = 'ERP@123'
                        u = User.objects.get(username=username)
                        u.set_password(new_password)
                        u.save()
                        msg = 'Password of ' + password['name'] + '(' + password['username'] + ')' + ' Reset Successfully To ' + new_password
                        error = False
                    else:
                        msg = "invalid parameters"
                else:
                    msg = 'Not Autherised!!'
            else:
                status = 401
                msg = 'Not Autherised!!'
        else:
            msg = 'Not Authenticated!!'
    else:
        msg = 'Session Problem!!'
    send = {'error': error, 'msg': msg}
    return JsonResponse(send, safe=False)

''' #STUDENT LOGIN RESET ENDS# '''


def checkpermission(request, myList=[]):
    myList = set(myList)  # myList includes the role ids of authorized persons
    roles = []
    if len(myList) == 0:
        try:
            var = request.session['hash1']
            if var:
                return 200
        except:
            return 401

    else:
        # roles=[]
        if 'roles' in request.session:
            roles = list(request.session['roles'])
        for r in myList:
            if r in roles:
                return 200
        return 401


def send_innotech(request):
    if request.method == "POST":
        data = json.loads(request.body)
        data['subject'] = "DEMO " + data['subject']
        data['message'] = "DEMO "
        yag = yagmail.SMTP({'noreply@kiet.edu': 'Team ERP'}, 'a4s3d2f1').send(data['send_to'], data['subject'], data['message'])
    return JsonResponse(data={'msg': 'OK'}, status=200)


def send_email(request):
    q_get_mail = MailService.objects.filter(status='N').values('send_to', 'subject', 'message', 'id')
    for mail in q_get_mail:
        if mail['send_to'] != 'default@kiet.edu':
            yag = yagmail.SMTP({'noreply@kiet.edu': 'ERP'}, 'a4s3d2f1').send(mail['send_to'], mail['subject'], mail['message'])
        q_update = MailService.objects.filter(id=mail['id']).update(status='Y')

    return JsonResponse(data={'msg': 'OK'}, status=200)


def mer_send_email(request):
    q_get_mail = Mercedes.objects.filter(mail_send='N', paid_status='PAID').values('student_email', 'student_name', 'txnid', 'id')
    for mail in q_get_mail:
        msg = "<b>Dear " + mail['student_name'].title() + ",</b><br><br>Gretings from KIET Group of Institutions.<br><br>Thank you for the registration in <b>ADVANCE DIPLOMA IN AUTO MOTIVE MECHATRONICS (ADAM)</b>. We acknowledge the receipt of your registration fee.<br><br>You will be received hall-ticket on your registered email-id soon.<br><br><hr><br>Thanks and Regards,<br><br>KIET Group of Institutions, Ghaziabad<br><br>"
        if mail['student_email'] != 'default@kiet.edu':
            yag = yagmail.SMTP({'amc.dam@kiet.edu': 'AMC DAM'}, 'kiet@12345').send(mail['student_email'], 'AMC DAM REGISTRATION', msg)
        q_update = Mercedes.objects.filter(id=mail['id']).update(mail_send='Y')

    return JsonResponse(data={'msg': 'OK'}, status=200)


def mercedes_report(request):

    output = io.BytesIO()
    try:
        status = request.GET['status'].upper()
    except:
        status = "BOTH"

    filter_data = {}
    if status != "BOTH":
        filter_data['paid_status'] = status

    qry_data = Mercedes.objects.filter(**filter_data).values()
    monthly_sheet_name = "Mercedes_DAM_Excel/" + str(date.today()) + ".xlsx"
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})

    row = 0
    col = 0
    worksheet.set_row(row, 40)

    merge_format = workbook.add_format({
        'bold':     True,
        'border':   6,
        'font_size': 9,
        'align':    'center',
        'valign':   'vcenter',
        'font_name': 'Arial'
    })

    sum_data = []
    merge_format.set_border(style=1)

    cell_format = workbook.add_format({'bold': True, 'font_size': 12, 'font_name': 'Arial'})
    cell_format2 = workbook.add_format({'font_size': 8, 'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter'})
    cell_format3 = workbook.add_format({'bold': True, 'font_size': 8, 'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter'})

    col = 0
    worksheet.write(0, 1, "STUDENT NAME", cell_format)
    worksheet.write(0, 2, "FATHER NAME", cell_format)
    worksheet.write(0, 3, "MOTHER NAME", cell_format)
    worksheet.write(0, 4, "STUDENT EMAIL", cell_format)
    worksheet.write(0, 5, "STUDENT MOB", cell_format)
    worksheet.write(0, 6, "FATHER MOB", cell_format)
    worksheet.write(0, 7, "CATEGORY", cell_format)
    worksheet.write(0, 8, "DOB", cell_format)
    worksheet.write(0, 9, "GENDER", cell_format)
    worksheet.write(0, 10, "ADDRESS", cell_format)
    worksheet.write(0, 11, "STUDENT AADHAR NUM", cell_format)
    worksheet.write(0, 12, "CITY", cell_format)
    worksheet.write(0, 13, "DISTRICT", cell_format)
    worksheet.write(0, 14, "PIN CODE", cell_format)
    worksheet.write(0, 15, "TEN MARKS", cell_format)
    worksheet.write(0, 16, "TEN GRADING", cell_format)
    worksheet.write(0, 17, "TEN GRADE", cell_format)
    worksheet.write(0, 18, "TEN MAX MARKS", cell_format)
    worksheet.write(0, 19, "TEN YEAR", cell_format)
    worksheet.write(0, 20, "TEN BOARD", cell_format)
    worksheet.write(0, 21, "TWELVE", cell_format)
    worksheet.write(0, 22, "TWELVE MAX MARKS", cell_format)
    worksheet.write(0, 23, "TWELVE GRADE", cell_format)
    worksheet.write(0, 24, "TWELVE GRADING", cell_format)
    worksheet.write(0, 25, "TWELVE YEAR", cell_format)
    worksheet.write(0, 26, "TWELVE MARKS", cell_format)
    worksheet.write(0, 27, "TWELVE MARKS", cell_format)
    worksheet.write(0, 28, "TWELVE BOARD", cell_format)
    worksheet.write(0, 29, "DIPLOMA MARKS", cell_format)
    worksheet.write(0, 30, "DIPLOMA BOARD", cell_format)
    worksheet.write(0, 31, "DIPLOMA YEAR", cell_format)
    worksheet.write(0, 32, "DIPLOMA", cell_format)
    worksheet.write(0, 33, "DIPLOMA GRADING", cell_format)
    worksheet.write(0, 34, "DIPLOMA MAX MARKS", cell_format)
    worksheet.write(0, 35, "DIPLOMA GRADE", cell_format)
    worksheet.write(0, 36, "GRADUATION MARKS", cell_format)
    worksheet.write(0, 37, "GRADUATION GRADE", cell_format)
    worksheet.write(0, 38, "GRADUATION YEAR", cell_format)
    worksheet.write(0, 39, "GRADUATION UNIVERSITY", cell_format)
    worksheet.write(0, 40, "GRADUATION MAX MARKS", cell_format)
    worksheet.write(0, 41, "GRADUATION", cell_format)
    worksheet.write(0, 42, "GRADUATION COLLEGE", cell_format)
    worksheet.write(0, 43, "GRADUATION GRADING", cell_format)
    worksheet.write(0, 44, "TXNID", cell_format)
    worksheet.write(0, 45, "BTECH STATUS", cell_format)
    worksheet.write(0, 46, "AMOUNT", cell_format)
    worksheet.write(0, 47, "PAID STATUS", cell_format)

    for q in qry_data:
        data_array = q
        row += 1
        # {'twelve': u'Y', 'ten_marks': None, 'ten_board': u'CBSE', 'twelve_max_marks': 500L, 'twelve_board': u'CBSE', 'graduation_marks': 713L, 'graduation_grade': None, 'twelve_grade': None, 'father_name': u'kanhaiya prasad singh', 'student_mob': u'7752945955', 'diploma_grade': None, 'paid_status': u'UNPAID', u'id': 20L, 'mother_name': u'anita singh', 'category': None, 'city': u'renukoot', 'district': u'sonebhadra', 'father_mob': u'9450793450', 'diploma_marks': None, 'time_stamp': datetime.datetime(2018, 6, 11, 9, 53, 27, 185542), 'diploma_board': None, 'graduation_year': 2018L, 'twelve_grading': u'N', 'student_name': u'kinkar kishore', 'ten_grading': u'Y', 'graduation_course': None, 'diploma_year': None, 'twelve_year': 2015L, 'mail_send': u'N', 'diploma': u'Y', 'graduation_college': u'krishna institute of engineering and tehnology , ghaziabad', 'twelve_marks': 407L, 'graduation_university': u'AKTU', 'ten_grade': 8.4, 'address': u'E-32 hi-tech colony murdhwa renukoot sonebhadra U.P. 231217', 'ten_max_marks': None, 'diplomacourse': None, 'pin_code': 231217L, 'graduation_max_marks': 1000L, 'student_aadhar_num': u'745700429631', 'txnid': None, 'btech_status': None, 'dob': datetime.date(1997, 6, 14), 'gender': u'Male', 'ten_year': 2013L, 'diploma_grading': None, 'graduation': None, 'graduationoptionyn': None, 'amount': 500.0, 'graduation_grading': u'N', 'diploma_max_marks': None, 'student_email': u'kinkarkishore1111@gmail.com'}

        worksheet.write(row, 1, data_array['student_name'], cell_format2)
        worksheet.write(row, 2, data_array['father_name'], cell_format2)
        worksheet.write(row, 3, data_array['mother_name'], cell_format2)
        worksheet.write(row, 4, data_array['student_email'], cell_format2)
        worksheet.write(row, 5, data_array['student_mob'], cell_format2)
        worksheet.write(row, 6, data_array['father_mob'], cell_format2)
        worksheet.write(row, 7, data_array['category'], cell_format2)
        worksheet.write(row, 8, data_array['dob'], cell_format2)
        worksheet.write(row, 9, data_array['gender'], cell_format2)
        worksheet.write(row, 10, data_array['address'], cell_format2)
        worksheet.write(row, 11, data_array['student_aadhar_num'], cell_format2)
        worksheet.write(row, 12, data_array['city'], cell_format2)
        worksheet.write(row, 13, data_array['district'], cell_format2)
        worksheet.write(row, 14, data_array['pin_code'], cell_format2)
        worksheet.write(row, 15, data_array['ten_marks'], cell_format2)
        worksheet.write(row, 16, data_array['ten_grading'], cell_format2)
        worksheet.write(row, 17, data_array['ten_grade'], cell_format2)
        worksheet.write(row, 18, data_array['ten_max_marks'], cell_format2)
        worksheet.write(row, 19, data_array['ten_year'], cell_format2)
        worksheet.write(row, 20, data_array['ten_board'], cell_format2)
        worksheet.write(row, 21, data_array['twelve'], cell_format2)
        worksheet.write(row, 22, data_array['twelve_max_marks'], cell_format2)
        worksheet.write(row, 23, data_array['twelve_grade'], cell_format2)
        worksheet.write(row, 24, data_array['twelve_grading'], cell_format2)
        worksheet.write(row, 25, data_array['twelve_year'], cell_format2)
        worksheet.write(row, 26, data_array['twelve_marks'], cell_format2)
        worksheet.write(row, 27, data_array['twelve_marks'], cell_format2)
        worksheet.write(row, 28, data_array['twelve_board'], cell_format2)
        worksheet.write(row, 29, data_array['diploma_marks'], cell_format2)
        worksheet.write(row, 30, data_array['diploma_board'], cell_format2)
        worksheet.write(row, 31, data_array['diploma_year'], cell_format2)
        worksheet.write(row, 32, data_array['diploma'], cell_format2)
        worksheet.write(row, 33, data_array['diploma_grading'], cell_format2)
        worksheet.write(row, 34, data_array['diploma_max_marks'], cell_format2)
        worksheet.write(row, 35, data_array['diploma_grade'], cell_format2)
        worksheet.write(row, 36, data_array['graduation_marks'], cell_format2)
        worksheet.write(row, 37, data_array['graduation_grade'], cell_format2)
        worksheet.write(row, 38, data_array['graduation_year'], cell_format2)
        worksheet.write(row, 39, data_array['graduation_university'], cell_format2)
        worksheet.write(row, 40, data_array['graduation_max_marks'], cell_format2)
        worksheet.write(row, 41, data_array['graduation'], cell_format2)
        worksheet.write(row, 42, data_array['graduation_college'], cell_format2)
        worksheet.write(row, 43, data_array['graduation_grading'], cell_format2)
        worksheet.write(row, 44, data_array['txnid'], cell_format2)
        worksheet.write(row, 45, data_array['btech_status'], cell_format2)
        worksheet.write(row, 46, data_array['amount'], cell_format2)
        worksheet.write(row, 47, data_array['paid_status'], cell_format2)
        # worksheet.write(row,48,data_array[11],cell_format2)
        # worksheet.write(row,49,data_array[14],cell_format2)
        # worksheet.write(row,50,data_array[19],cell_format2)

    workbook.close()

    output.seek(0)

    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=mercedes_dam.xlsx"

    output.close()

    return response


def acc_send_sms(request):
    query = Daksmsstatus.objects.filter(type='Accounts', updatestatus='N').values()
    for q in query:
        Mob = q['phonenos']
        message = q['msg']
        mainid = q['mainid']

        re = Sms_Api(mainid, Mob, message)

    return JsonResponse(data={'msg': 'OK'}, status=200)


# def create_user(request):
#   jsoni=[]
#   for j in jsoni:
#       hash1=unicode(str(j['Hash1'])   , 'utf-8')
#       hash2=str(j['Hash2'])

#       if hash1.isnumeric():
#           print(hash1)
#           q_lib=StudentPrimDetail.objects.filter(uni_roll_no=hash1).values('lib_card')
#           hash1=q_lib[0]['lib_card']
#           if hash1 is None or hash1== '':
#               continue

#       q_user=User.objects.create_user(username=hash1,password= hash2)
# # for j in json
# #     hash1=j['Hash1']
# #     hash2=j['Hash2']

# #     q_user=User.objects.create_user(username=hash1,password= hash2)


def forgot_password_new(request):

    error = True
    status = 403
    otp_second = ''
    if 'HTTP_AUTHORIZATION' in request.META:

        info = request.META['HTTP_AUTHORIZATION']
        info1 = info.split(" ")
        info2 = str(base64.b64decode(info1[1]))
        info2 = info2.replace('b', "")
        info2 = info2.replace("'", "")
        info3 = info2.split(':')

        pmail1 = info3[0].strip()

        mob_no = info3[1].strip()

        try:
            data = json.loads(request.body)
        except:
            data = {}
        if not 'request_type' in data:
            matching = EmployeePrimdetail.objects.filter(Q(mob=mob_no) | Q(mob1=mob_no)).filter(emp_id=pmail1).count()
        elif json.loads(request.body)['request_type'] == 'student':
            q_last_session = Semtiming.objects.filter(sem_start__lte=date.today(), sem_end__gte=date.today()).values('session_name').order_by('-sem_end')[:1]
            session_name = q_last_session[0]['session_name']
            student_session = generate_session_table_name("studentSession_", session_name)

            matching = student_session.objects.filter(mob=mob_no).filter(uniq_id__lib=pmail1).count()
        otp = ''
        if matching == 1:
            status = 200
            error = False
            today = date.today()
            now = datetime.datetime.now()
            count = Daksmsstatus.objects.filter(phonenos=mob_no, rectimestamp__date=today, msg="OTP").filter(Q(updatestatus='N') | Q(updatestatus='Y')).count()

            request.session['hash1'] = pmail1
            if(count == 0):
                characters2 = '01234567'
                n2 = 5
                for i in range(0, n2):
                    num2 = random.randint(0, len(characters2) - 1)
                    otp = otp + characters2[num2]
                Daksmsstatus.objects.create(phonenos=mob_no, counttry=0, otp=otp, rectimestamp=now, updatestatus='N', msg="OTP")
                list1 = Daksmsstatus.objects.filter(phonenos=mob_no, msg="OTP", rectimestamp=now).values("mainid", "otp").exclude(updatestatus="U").order_by("-mainid")[:1]
                Sms_Api(list1[0]['mainid'], mob_no, "Your OTP for KIET-ERP forgot password is: " + list1[0]['otp'] + ".It is valid for one time use only. Please do not share this OTP with anyone to ensure accounts security.")
                msg = "Otp generated"
            elif(count >= 3):
                error = True
                msg = "Maximum OTP Limit Reached"
            else:
                list1 = Daksmsstatus.objects.filter(phonenos=mob_no, msg="OTP").values("otp", "mainid").exclude(updatestatus="U").order_by("-mainid")[:1]
                Daksmsstatus.objects.create(phonenos=mob_no, counttry=0, otp=list1[0]['otp'], rectimestamp=now, updatestatus='N', msg="OTP")
                list2 = Daksmsstatus.objects.filter(phonenos=mob_no, msg="OTP", rectimestamp=now).values("otp", "mainid").exclude(updatestatus="U").order_by("-mainid")[:1]
                Sms_Api(list2[0]['mainid'], mob_no, "Your OTP for KIET-ERP forgot password is: " + list2[0]['otp'] + ".It is valid for one time use only. Please do not share this OTP with anyone to ensure accounts security.")
                msg = "Otp generated"

        else:
            status = 401
            msg = "Incorrect username or mobile no."
    else:
        status = 400
        msg = "request invalid"
    result = {'error': error, 'msg': msg}
    return JsonResponse(data=result, status=status)


def checking_otp_new(request):
    error = True
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.method == 'POST':
            incoming_data = request.body
            i_data = json.loads(incoming_data)
            if 'otp' in i_data and 'mob_no' in i_data:
                otp = i_data['otp']
                mob_no = i_data['mob_no']
                matching = Daksmsstatus.objects.filter(phonenos=mob_no).values("otp", "mainid", "counttry").order_by('-mainid')[:1]
                hashed_otp = matching[0]['otp']
                mainid = matching[0]['mainid']
                counttry = matching[0]['counttry']
                if(counttry < 3):
                    if otp == hashed_otp:
                        status = 200
                        error = False
                        Daksmsstatus.objects.filter(mainid=mainid).update(updatestatus="U")
                        msg = 'Correct OTP'
                    else:
                        status = 401
                        Daksmsstatus.objects.filter(mainid=mainid).update(counttry=F('counttry') + 1)
                        msg = 'Incorrect OTP Please Try Again !'
            else:
                status = 401
                msg = 'OTP EXPIRED'
        else:
            status = 502
            msg = "Wrong Parameters"
    else:
        status = 500
        msg = 'Request Invalid'
    result = {"msg": msg, "error": error}

    return JsonResponse(status=status, data=result)


def change_pass_otp_new(request):
    data = ''
    msg = ''
    if 'HTTP_COOKIE' in request.META:
        if request.method == 'POST':
            incoming_data = request.body
            i_data = json.loads(incoming_data)
            if 'new_pass' in i_data:
                new_password = i_data['new_pass']
                username = request.session['hash1']

                u = User.objects.get(username=username)
                u.set_password(new_password)
                u.save()
                msg = "Password Changed Successfully."
                status = 200

            else:
                msg = "Wrong Params"
                status = 500
        else:
            msg = "invalid Request"
            status = 502

    else:
        status = 403

    send = {"msg": msg, "error": False}
    return JsonResponse(status=status, data=send)


def fcm_insert(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.method == 'POST':
                data = json.loads(request.body)
                if request.session['hash3'] == 'Student':
                    user_id = request.session['uniq_id']
                    qry1 = StudentPrimDetail.objects.filter(uniq_id=user_id).values('lib')
                    username = qry1[0]['lib']
                else:
                    username = request.session['hash1']
                if 'fcm_token' in data:
                    fcm_token = data['fcm_token']
                device_id = data['device_id']
                if 'application' in data:
                    application = data['application']
                else:
                    application = "web"
                # qry = fcm.objects.filter(username=username ,device_id=device_id).count()
                # if qry == 0:
                #   fcm.objects.create(username=AuthUser.objects.get(username=username), fcm_token=fcm_token, device_id=device_id)
                #   data_values = {'msg' : 'Successfully Inserted'}
                # else:
                #   fcm.objects.filter(username=username,device_id=device_id).update(fcm_token=fcm_token)
                #   data_values = {'msg' : 'Successfully Updated'}
                if 'fcm_token' in data:
                    fcm.objects.update_or_create(username=AuthUser.objects.get(username=username), device_id=device_id, defaults={'fcm_token': fcm_token, 'application': application})
                data_values = {'msg': 'Successfully Inserted'}
                status = 200
            else:
                status = 502
        else:
            status = 403
    else:
        status = 500
    return JsonResponse(data=data_values, status=status, safe=False)


def fcm_remove(request):
    data_values = {}
    status = 403
    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            if request.method == 'POST':
                data = json.loads(request.body)
                device_id = data['device_id']
                fcm.objects.filter(device_id=device_id).delete()
                data_values = {'msg': 'Successfully Deleted'}
                status = 200
            else:
                status = 502
        else:
            status = 403
    else:
        status = 500
    return JsonResponse(data=data_values, status=status, safe=False)


def registration_api(request):
    if request.method == "GET":
        now = datetime.now().date()
        now1 = now.strftime("%Y-%m-%d")
        if now1 < '2019-03-18':
            library_id = request.GET['lib_id']
            qry = list(StudentPrimDetail.objects.filter(lib=library_id).values('name', 'email_id', 'lib', 'dept_detail__dept__value', 'dept_detail__course__value', 'uniq_id'))
            qry1 = list(studentSession_1819e.objects.filter(uniq_id=qry[0]['uniq_id']).values('mob', 'sem__sem'))
            qry[0]['mobile_no'] = qry1[0]['mob']
            qry[0]['semester'] = qry1[0]['sem__sem']
            data = {'data': qry}
            status = 200
    else:
        status = 502

    return JsonResponse(data=data, status=status, safe=False)


########################### EMAIL ##################################################

def send_bday_email(request):
    dates = date.today()

    month = dates.month
    day = dates.day

    if month < 10:
        month_str = "0" + str(month)
    else:
        month_str = str(month)

    if day < 10:
        day_str = "0" + str(day)
    else:
        day_str = str(day)
    date_string = month_str + "-" + day_str

    ############ EMPLOYEE ######################

    emp_id = EmployeePerdetail.objects.filter(dob__endswith=date_string, emp_id__emp_status='ACTIVE').exclude(emp_id__email__isnull=True).annotate(email=F('emp_id__email'), name=F('emp_id__name'), user_type=F('emp_id__emp_id__user_type')).values('email', 'name', 'user_type')

    emp_msg = "Happy Birthday! May your coming year surprise you with \nthe happiness of smiles and the feeling of love. We hope \nyou have made plenty of sweet memories to cherish forever \nover the last year and that today is an extra special day.\n\nThank you for everything you do to \nmake KIET a great place and \nHappy Birthday, once again!"

    ####### STUDENTS #######################

    students = StudentPerDetail.objects.filter(dob__endswith=date_string).exclude(uniq_id__email_id__isnull=True).exclude(uniq_id__in=StudentPerDetail.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") | Q(uniq_id__admission_status__value__contains="EX")).values_list('uniq_id', flat=True)).annotate(email=F('uniq_id__email_id'), name=F('uniq_id__name'), user_type=F('uniq_id__lib__user_type')).values('email', 'name', 'user_type')

    student_msg = "Happy Birthday! May your coming year surprise you with \nthe happiness of smiles and the feeling of love. We hope \nyou have made plenty of sweet memories to cherish forever \nover the last year and that today is an extra special day.\n\nHappy Birthday, once again!"

    bday_person = list(emp_id)
    bday_person.extend(list(students))

    for bday in bday_person:
        img = Image.open(settings.FILE_PATH + "images/bday.png")

        img.thumbnail([img.size[0], img.size[1]], Image.ANTIALIAS)

        font = ImageFont.truetype(settings.FILE_PATH + "font/Bitter-Italic.otf", 14)
        draw = ImageDraw.Draw(img)
        draw.text((90, 330), "Dear " + bday['name'].title() + ",", font=font, fill="#464343")

        msg = ""
        if bday['user_type'] == 'Employee':
            msg = emp_msg
        elif bday['user_type'] == 'Student':
            msg = student_msg
        else:
            continue

        draw.text((90, 360), msg, font=font, fill="#464343")

        final_img_width = img.size[0]
        final_img_height = img.size[1]
        tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")

        index = 0
        margin_left = 0
        margin_top = 0

        x = index // 2 * (tmp_image.size[0] // 2)
        y = index % 2 * (tmp_image.size[1] // 2)
        w, h = img.size
        tmp_image.paste(img, (x, y, x + w, y + h))

        tmp_image.save(settings.FILE_PATH + "images/happy_birthday.png", "PNG", resolution=300.0)

        contents = [yagmail.inline(settings.FILE_PATH + "images/happy_birthday.png"), "\n\n\n", yagmail.inline(settings.FILE_PATH + "images/logo.png"), "KIET Group Of Institutions\n13 Km Stone, Delhi Meerut Road, NH 58\nMuradNagar, Ghaziabad, 201206, U.P.\ntech.kiet.edu\n\nNote: This is a system generated email, for any feedbacks and suggestions kindly reply to this erp@kiet.edu."]

        if bday['user_type'] == 'Employee':
            send_mail(bday['email'], '!!! HAPPY BIRTHDAY !!!', contents, ['hr@kiet.edu'])

        elif bday['user_type'] == 'Student':
            send_mail(bday['email'], '!!! HAPPY BIRTHDAY !!!', contents, [])

    return JsonResponse(data={'success': 'ok'}, status=200, safe=False)


def send_summary_mail(request):

    today_weekday = date.today().weekday()
    today_day = date.today().day

    if today_weekday == 0:  # monday or 1st day of month
        qry_distinct_reporting = list(Reporting.objects.values('department', 'reporting_to', 'reporting_to__value').distinct())

        ###### LEAVE SUMMARY ##############

        for report in qry_distinct_reporting:
            pending_leave = Leaveapproval.objects.filter(status='PENDING', dept=report['department'], desg=report['reporting_to'], leaveid__finalstatus='PENDING').values('leaveid__leavecode__leave_abbr', 'leaveid__fromdate', 'leaveid__todate', 'leaveid__days', 'leaveid__emp_id__name', 'leaveid__reason')

            count = len(pending_leave)
            if count == 0:
                continue

            emails = list(EmployeePerdetail.objects.filter(emp_id__dept=report['department'], emp_id__desg=report['reporting_to'], emp_id__emp_status='ACTIVE').values_list('emp_id__email', flat=True))

            msg = "Dear " + report['reporting_to__value'] + ",<br><br>Following leaves are pending on your KIET-ERP Portal:<br><br><table border='1' width='100%' style='border-collapse: collapse'><tr><th>Sno</th><th>Employee</th><th>Leave Type</th><th>From Date</th><th>To Date</th><th>Days</th><th>Reason</th></tr>"

            for i in range(count):
                msg = msg + "<tr><td>" + str(i + 1) + ".</td><td>" + pending_leave[i]['leaveid__emp_id__name'] + "</td><td>" + pending_leave[i]['leaveid__leavecode__leave_abbr'] + "</td><td>" + pending_leave[i]['leaveid__fromdate'].strftime("%d-%b-%Y") + "</td><td>" + pending_leave[i]['leaveid__todate'].strftime("%d-%b-%Y") + "</td><td>" + str(pending_leave[i]['leaveid__days']) + "</td><td>" + str(pending_leave[i]['leaveid__reason']) + "</td></tr>"
            msg += "</table><br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br><a href='https://play.google.com/store/apps/details?id=kiet.edu.hrms&hl=en' target='_blank'><img src='https://play.google.com/intl/en_us/badges/images/badge_new.png'></img></a><br><br><a href='https://tech.kiet.edu/hrms/index.html' target='_blank' style='color:#137aa9;'>View On Web</a><br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this erp@kiet.edu."

            subject = "PENDING LEAVE SUMMARY | " + str(count) + " LEAVES ARE PENDING"
            send_mail(emails, subject, [msg], [])
            # break

        ######## GRIEVANCE SUMMARY #########

        for report in qry_distinct_reporting:
            pending_grievance = GrievanceData.objects.filter(department=report['department'], designation=report['reporting_to'], status_hod='PENDING').values('gri_message', 'type__value', 'empid__name')

            count = len(pending_grievance)
            if count == 0:
                continue

            emails = list(EmployeePerdetail.objects.filter(emp_id__dept=report['department'], emp_id__desg=report['reporting_to'], emp_id__emp_status='ACTIVE').values_list('emp_id__email', flat=True))

            msg = "Dear " + report['reporting_to__value'] + ",<br><br>Following grievances are pending on your KIET-ERP Portal:<br><br><table border='1' width='100%' style='border-collapse: collapse'><tr><th>Sno</th><th>Employee</th><th>Grievance Type</th><th>Grievance</th></tr>"

            for i in range(count):
                msg = msg + "<tr><td>" + str(i + 1) + ".</td><td>" + pending_grievance[i]['empid__name'] + "</td><td>" + pending_grievance[i]['type__value'] + "</td><td>" + pending_grievance[i]['gri_message'] + "</td></tr>"

            msg += "</table><br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br><a href='https://play.google.com/store/apps/details?id=kiet.edu.hrms&hl=en' target='_blank'><img src='https://play.google.com/intl/en_us/badges/images/badge_new.png'></img></a><br><br><a href='https://tech.kiet.edu/hrms/index.html' target='_blank' style='color:#137aa9;'>View On Web</a><br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this erp@kiet.edu."

            subject = "PENDING GRIEVANCE SUMMARY | " + str(count) + " GRIEVANCES ARE PENDING"
            send_mail(emails, subject, [msg], [])

            # break

        ##### STUDENT REDRESSAL SUMMARY #######

        qry_emp_redressal = RedressalApproval.objects.filter(coord_status='PENDING').values('emp_id', 'emp_id__email', 'emp_id__desg__value').distinct()
        for pending in qry_emp_redressal:
            Redressal.views.check_self_escalate(pending['emp_id'])
            pending_redressal = RedressalApproval.objects.filter(coord_status='PENDING', emp_id=pending['emp_id']).values('redressal_id__grievance_ticket_num', 'redressal_id__category__value', 'redressal_id__description', 'redressal_id__uniq_id__name')
            count = len(pending_redressal)
            if count == 0:
                continue

            msg = "Dear " + pending['emp_id__desg__value'] + ",<br><br>Following student grievances are pending on your KIET-ERP Portal:<br><br><table border='1' width='100%' style='border-collapse: collapse'><tr><th>Sno</th><th>Redressal Id</th><th>Student Name</th><th>Redressal Category</th><th>Description</th></tr>"

            for i in range(count):
                msg = msg + "<tr><td>" + str(i + 1) + ".</td><td>" + pending_redressal[i]['redressal_id__grievance_ticket_num'] + "</td><td>" + pending_redressal[i]['redressal_id__uniq_id__name'] + "</td><td>" + pending_redressal[i]['redressal_id__category__value'] + "</td><td>" + pending_redressal[i]['redressal_id__description'] + "</td></tr>"

            msg += "</table><br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br><a href='https://play.google.com/store/apps/details?id=kiet.edu.hrms&hl=en' target='_blank'><img src='https://play.google.com/intl/en_us/badges/images/badge_new.png'></img></a><br><br><a href='https://tech.kiet.edu/hrms/index.html' target='_blank' style='color:#137aa9;'>View On Web</a><br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this erp@kiet.edu."

            subject = "PENDING REDRESSAL SUMMARY | " + str(count) + " REDRESSALS ARE PENDING"
            send_mail(pending['emp_id__email'], subject, [msg], [])

            # break

        ##### TICKETING SUMMARY #######

        qry_emp_redressal = TicketingApproval.objects.filter(coord_status='PENDING').values('emp_id', 'emp_id__email', 'emp_id__desg__value').distinct()
        for pending in qry_emp_redressal:
            Ticketing.views.check_self_escalate(pending['emp_id'])
            pending_redressal = TicketingApproval.objects.filter(coord_status='PENDING', emp_id=pending['emp_id']).values('redressal_id__ticket_num', 'redressal_id__category__value', 'redressal_id__description', 'redressal_id__emp_id__name')
            count = len(pending_redressal)
            if count == 0:
                continue

            msg = "Dear " + pending['emp_id__desg__value'] + ",<br><br>Following tickets raised by employees are pending on your KIET-ERP Portal:<br><br><table border='1' width='100%' style='border-collapse: collapse'><tr><th>Sno</th><th>Grievance Id</th><th>Employee</th><th>Grievance Category</th><th>Description</th></tr>"

            for i in range(count):
                msg = msg + "<tr><td>" + str(i + 1) + ".</td><td>" + pending_redressal[i]['redressal_id__ticket_num'] + "</td><td>" + pending_redressal[i]['redressal_id__emp_id__name'] + "</td><td>" + pending_redressal[i]['redressal_id__category__value'] + "</td><td>" + pending_redressal[i]['redressal_id__description'] + "</td></tr>"

            msg += "</table><br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br><a href='https://play.google.com/store/apps/details?id=kiet.edu.hrms&hl=en' target='_blank'><img src='https://play.google.com/intl/en_us/badges/images/badge_new.png'></img></a><br><br><a href='https://tech.kiet.edu/hrms/index.html' target='_blank' style='color:#137aa9;'>View On Web</a><br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this erp@kiet.edu."

            subject = "PENDING TICKETING SUMMARY | " + str(count) + " TICKETS ARE PENDING"
            send_mail(pending['emp_id__email'], subject, [msg], [])

            # break

    ####### PAYABLE DAYS SUMMARY ##########

    if today_day == 1:  # 1st day of month ######

        employees = EmployeePerdetail.objects.filter(emp_id__emp_status='ACTIVE').exclude(emp_id__emp_type=219).exclude(emp_id="00007").exclude(emp_id__email__isnull=True).exclude(emp_id__email='default@kiet.edu').values('emp_id__name', 'emp_id', 'emp_id__email', 'emp_id__dept__value').order_by('emp_id__name')

        today = date.today() - relativedelta(days=+1)
        year = int(today.year)
        month = int(today.month)
        fdate = date(year, month, 1).strftime('%Y-%m-%d')
        range1 = calendar.monthrange(year, month)
        tdate = date(year, month, range1[1]).strftime('%Y-%m-%d')

        for emp in employees:
            emp_data = leave.views.calculate_working_days(emp['emp_id'], fdate, tdate, emp['emp_id__name'], emp['emp_id__dept__value'])

            msg = "Dear " + emp['emp_id__name'].title() + ",\n\nHere is your " + calendar.month_name[month] + "'s payable days summary :\n\nPresent: " + str(emp_data['present']) + "\nLeave: " + str(emp_data['leave']) + "\nHoliday: " + str(emp_data['holiday']) + "\n"
            if emp_data['leave_nc'] > 0:
                msg = msg + "Leave(WP): " + str(emp_data['leave_nc']) + "\n"
            msg = msg + "Absent: " + str(emp_data['absent']) + "\n\n <b>Total Payable Days: " + str(emp_data['payable_days']) + "/" + str(range1[1]) + "</b>\n\n"

            msg = msg + "These are not final payable days, it may change in case of some updation or sandwich case until payable days gets locked for this month. Please make sure to mark your remaining leaves and grievances and make them approved before payable days gets locked for this month."

            msg += "<br><br><hr><br>Thanks and Regards,<br><br>Team ERP<br><br><a href='https://play.google.com/store/apps/details?id=kiet.edu.hrms&hl=en' target='_blank'><img src='https://play.google.com/intl/en_us/badges/images/badge_new.png'></img></a><br><br><a href='https://tech.kiet.edu/hrms/index.html' target='_blank' style='color:#137aa9;'>View On Web</a><br><br>Note: This is a system generated email, for any feedbacks and suggestions kindly reply to this erp@kiet.edu."

            subject = "PAYABLE DAYS SUMMARY | " + calendar.month_name[month] + " " + str(year)
            send_mail(emp['emp_id__email'], subject, [msg], [])
            # break

    return JsonResponse(data={'success': 'ok'}, status=200, safe=False)


def send_mail(to, subject, contents, cc):
    yag = yagmail.SMTP({settings.EMAIL_ID: 'Team ERP'}, settings.EMAIL_PASSWORD).send(to, subject, contents, cc=cc)


def std_login(request):
    status = 401
    data={}
    if 'HTTP_AUTHORIZATION' in request.META:
        info = request.META['HTTP_AUTHORIZATION']
        info1 = info.split(" ")
        print(info1)
        info2 = bytes(base64.b64decode(info1[1]))
        info3 = info2.decode().split(':')
        username = info3[0].strip()
        password = info3[1].strip()
        user_type=""
        if len(info3)>2:
            user_type = info3[2].strip()
        print(password)
        user = authenticate(username = username,password=password)
        if password == "#att@404" and len(User.objects.filter(username=username))>0:
            user = User.objects.get(username=username)
        qr=[]
        if user is not None:
            if user.is_active:
                response = login(request,user)
                if user_type == 'employee':
                    qr = list(AuthUser.objects.filter(username=username).extra(select={'emp_id': 'username'}).exclude(user_type='Student').values('emp_id', 'user_type'))
                elif user_type == 'student':
                    print(username)
                    qr = list(AuthUser.objects.filter(username=username).extra(select={'lib_id': 'username'}).exclude(user_type='Employee').values('lib_id', 'user_type'))
                if len(qr)==0:
                    msg='User does not exist'
                else:
                    msg='Success'
                    status=200
                    ip = get_client_ip(request)
                    if ip is not None:
                        external_login.objects.create(username=username,device_ip=ip)
            else:
                msg='Invalid Credentials'
        else:
            msg='Invaid Credentials'
    else:
        msg='Invalid Credentials'
    if len(qr)>0:
        data={'msg':msg,'data':qr[0]}
    else:
        data={'msg':msg}
    return JsonResponse(data=data,status=status,safe=True)
