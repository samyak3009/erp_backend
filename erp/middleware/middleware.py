import time
import json
from django.db.models.signals import *
from django.contrib.auth import authenticate, login, logout
from django.dispatch import receiver
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django_query_signals import *
from login.models import LogRecord, AuthUser
from erp.constants_variables import statusCodes, statusMessages
from erp.constants_functions import academicCoordCheck
from datetime import datetime
import yagmail
from django.conf import settings


class LogAllMiddleware(object):

    pmail = ""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if(response.status_code not in [statusCodes.STATUS_SUCCESS, statusCodes.STATUS_CONFLICT_WITH_MESSAGE, statusCodes.STATUS_UNAUTHORIZED, statusCodes.STATUS_BAD_REQUEST]):
            pass
            # file_name="/home/kiet/httpdocs/django_back/erp/errors/"+str(datetime.now())+self.pmail+".html"
            # F = open(file_name,"wb")
            # F.write(response.content)
            # str_str=""
            # for key, value in request.session.items():
            #     if key=="_auth_user_backend":
            #         continue
            #     str_str=str_str+str(key)+":"+str(value)+" , "
            # # yagmail.SMTP({settings.EMAIL_ID:'Team ERP'}, settings.EMAIL_PASSWORD).send(settings.EMAIL_ID,"ERROR IN "+str(self.pmail)+" "+str(str_str)+" with status "+str(response.status_code),file_name)
            # msg="Some is wrong temporary. The developers has been informed about issue. \n \n Kindly try after some time!!"
            # data={'msg':msg}
            # status=202
            # response = JsonResponse(status=status,data=data)
        return response

    def process_request(self, request):
        global pmail
        try:
            pmail = request.session['hash1']
        except:
            pmail = request.session['uniq_id']
        else:
            pmail = ""
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        url = request.build_absolute_uri()
        url = request.build_absolute_uri()
        uu = (url.split("?")[0]).split('/')

        if len(uu) == 6:
            req = uu[-3] + '/' + uu[-2] + '/'
        elif len(uu) == 5:
            req = uu[-2] + '/'
        elif len(uu) == 7:
            req = uu[-4] + '/' + uu[-3] + '/' + uu[-2] + '/'

        if 'StudentPortal' not in req:

            end_points = ['validate/', 'attendance/empAttScript/', 'dashboard/upload/', 'student_login/', 'forgot_new/', 'checking_new/', 'change_pass_otp_new/', 'send_innotech/', 'leave/autoleavecredit/', 'logout/', 'send_bday_email/', 'send_summary_mail/', 'acc_send_sms/','login/','StudentAccounts/print_fee_receipt/','StudentAccounts/remider_due_date/','StudentMMS/create_external_form/','StudentMMS/submit_answer_external_form/']
            if req not in end_points and 'website' not in req:
                # if not 'roles' in request.session:
                #     logout(request)
                # sdasdasdasd
                #     return JsonResponse(status=statusCodes.STATUS_UNAUTHORIZED,data=statusMessages.MESSAGE_UNAUTHORIZED)

                if not 'HTTP_COOKIE' in request.META:

                    return JsonResponse(status=statusCodes.STATUS_BAD_REQUEST, data=statusMessages.MESSAGE_BAD_REQUEST)
                if not request.user.is_authenticated:
                    return JsonResponse(status=statusCodes.STATUS_UNAUTHORIZED, data=statusMessages.MESSAGE_UNAUTHORIZED)
        else:
            end_points = ['StudentPortal/HostelFeeLetter/', 'StudentPortal/PrintHostelFeeLetter/', 'StudentPortal/AcademicFeeLetter/', 'StudentPortal/PrintAcademicFeeLetter/', 'StudentPortal/printDeclaration/', 'StudentAcademics/get_branch_change_students/', 'build_details/', 'AppraisalFaculty/update_feedback_marks/','StudentMMS/create_external_form/']

            if req not in end_points:
                if not 'hash3' in request.session:
                    logout(request)
                    return JsonResponse(status=statusCodes.STATUS_UNAUTHORIZED, data=statusMessages.MESSAGE_UNAUTHORIZED)

                if request.session['hash3'] != 'Student':
                    logout(request)
                    return JsonResponse(status=statusCodes.STATUS_UNAUTHORIZED, data=statusMessages.MESSAGE_UNAUTHORIZED)

                if not 'HTTP_COOKIE' in request.META:
                    return JsonResponse(status=statusCodes.STATUS_BAD_REQUEST, data=statusMessages.MESSAGE_BAD_REQUEST)
                if not request.user.is_authenticated:

                    return JsonResponse(status=statusCodes.STATUS_UNAUTHORIZED, data=statusMessages.MESSAGE_UNAUTHORIZED)

        global pmail

        try:
            pmail = request.session['hash1']
        except:
            if req == 'attendance/empAttScript' and request.method == 'GET':
                pmail = "00007"
            else:
                pmail = ""

        return None

    def process_response(self, request, response):
        global pmail
        try:
            pmail = request.session['hash1']
        except:
            pmail = request.session['uniq_id']
        else:
            pmail = ""
        return response

    ############################### insert log ####################

    @receiver(post_save)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            q_au = AuthUser.objects.filter(username=pmail)
            if len(q_au) > 0:
                operation = "insert"
                new = vars(instance)
                if '_state' in new:
                    del new['_state']

                if not 'LogRecord' in str(instance):
                    try:
                        q_insert = LogRecord.objects.using('log_db').create(emp_id=AuthUser.objects.get(username=pmail), db_table=instance, operation=operation, new_or_inserted_values=new)
                    except:
                        pass
    #################### delete log ###############################

    @receiver(pre_delete)
    def post_delete_handler(sender, **kwargs):
        q = kwargs['args']['self']
        if len(q) > 0:
            db_table = kwargs['args']['self'][0]
            operation = "delete"
            n = len(kwargs['args']['self'])
            for i in range(n):
                q_au = AuthUser.objects.filter(username=pmail)
                if len(q_au) > 0:
                    prev_values = vars(kwargs['args']['self'][i])
                    if '_state' in prev_values:
                        del prev_values['_state']
                    if str(db_table) != 'LogRecord object':
                        try:
                            q_update = LogRecord.objects.using('log_db').create(emp_id=AuthUser.objects.get(username=pmail), db_table=db_table, operation=operation, previous_values=prev_values)
                        except:
                            pass

    ###################### update log ################################
    @receiver(pre_update)
    def pre_update(sender, **kwargs):
        q = kwargs['args']['self']
        if len(q) > 0:
            db_table = kwargs['args']['self'][0]
            operation = "update"
            n = len(kwargs['args']['self'])
            for i in range(n):
                q_au = AuthUser.objects.filter(username=pmail)
                if len(q_au) > 0:
                    prev_values = vars(kwargs['args']['self'][i])
                    new_values = kwargs['args']['kwargs']
                    if '_state' in prev_values:
                        del prev_values['_state']
                    if '_state' in new_values:
                        del new_values['_state']
                    try:
                        q_update = LogRecord.objects.using('log_db').create(emp_id=AuthUser.objects.get(username=pmail), db_table=db_table, operation=operation, previous_values=prev_values, new_or_inserted_values=new_values)
                    except:
                        pass
