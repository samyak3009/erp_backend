from .models import DataStructure,DataSet,NotificationLog, SendNotification, Job

from .serializers import DataSetSerializer,NotificationLogSerializer
# from .functions import update_by_threads,send_by_threads
import Notification as nf
from celery import shared_task
import json
from nested_lookup import nested_lookup
import _thread
import time
import requests
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yagmail
from .constant_variables.constant_variables import SENDER_EMAIL,PASSWORD,SMTP_SERVER,SMS_USERNAME,SMS_PASSWORD,SMS_SENDERID,PORT
import re 
import html2text
from bs4 import BeautifulSoup

from huey import crontab
from huey.contrib.djhuey import HUEY
import datetime
from django_mysql.models.functions import JSONInsert

@shared_task
def read_insert_file(dataset_list): # INSERT IN DATABASE TABLE 
    serializer = DataSetSerializer(data=dataset_list,many=True) #many=True FOR LIST OF DATA
    if serializer.is_valid(raise_exception=True):
        serializer.save()


@shared_task
def add_rows(dataset_list):
    print(dataset_list)
    serializer = DataSetSerializer(data=dataset_list,many=True) #many=True FOR LIST OF DATA
    if serializer.is_valid(raise_exception=True):
        serializer.save()


@shared_task
def update_uniq_field(new_field,data_id):
    dataset = DataSet.objects.filter(data_id=data_id).exclude(status=0).only("data_json")
    data_json  = list(dataset.values("data_json"))
    new_uniq = nested_lookup(new_field,data_json) 
    prim_key_li  =[]
    for uniq in new_uniq:
        prim_key_li.append({"prim_key":uniq})
    threads =  len(dataset)//500 
    for thread in range(threads+1): #Start thread with 500 or less than 500 instances
        _thread.start_new_thread ( nf.functions.update_by_threads, (dataset[thread*500:(thread+1)*500],prim_key_li[thread*500:(thread+1)*500]) )


@shared_task
def add_groups(data_id,ids,group_id):
    instances = DataSet.objects.filter(data_id=data_id,prim_key__in=ids).exclude(status=0).only('data_json')
    data_json = list(instances.values('data_json'))
    data_list = []
    for qr in data_json :
        data = {}
        qr['data_json']['group'].append(group_id)
        data['data_json'] = qr['data_json']
        data_list.append(data)
    serializer = DataSetSerializer(instances,data=data_list,partial=True, many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()


@shared_task
def add_sub_groups(data_id,ids,sub_group_id):
    print(ids)
    instances = DataSet.objects.filter(data_id=data_id,prim_key__in=ids).exclude(status=0).only('data_json')
    data_json = list(instances.values('data_json'))
    data_list = []
    for qr in data_json :
        data = {}
        qr['data_json']['sub_group'].append(sub_group_id)
        data['data_json'] = qr['data_json']
        data_list.append(data)
    print(data_list)
    serializer = DataSetSerializer(instances,data=data_list,partial=True, many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()


@shared_task
def send_notification(uniq_field,template_body,qs_list,temp_data_key,portal,qry_id,email_li,phone_li,subject,signature):
    msg = re.sub(r'&lt;&lt;(.*?)(?<!\\)&gt;&gt;',"{}",template_body)
    msg = re.sub("&lt;script&gt;", "" ,msg)
    msg = re.sub("&lt;/script&gt;", "" ,msg)
    # msg = msg + "<br>" + signature
    threads =  len(qs_list)//500 
    for thread in range(threads+1):
        _thread.start_new_thread ( nf.functions.send_by_threads, (qs_list[thread*500:(thread+1)*500],msg,temp_data_key,portal,email_li,phone_li,uniq_field,template_body,qry_id,subject,signature))



@shared_task
def send_notification_via_email(data,subject,signature):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    body = data['msg'] + "<br>" + signature
    part2 = MIMEText(body, "html")
    message.attach(part2)
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(SMTP_SERVER,PORT)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(SENDER_EMAIL, PASSWORD)
        for email in data['email']:
            print(email)
            message["To"] = email
            server.sendmail(
                SENDER_EMAIL, email, message.as_string()
            )
        date_of_task_execution=datetime.datetime.now().date()
        date_in_format_for_JSONInsert='$."'+str(date_of_task_execution)+'"' #The '$' is for JSONInsert format
        task_result_json={date_in_format_for_JSONInsert:1}
        NotificationLog.objects.filter(notify_id=data['notify_id'],prim_key=data['prim_key']).update( email_task_result=JSONInsert('email_task_result', task_result_json))
        
    except Exception as e:
        # Print any error messages to stdout
        print(e)
        date_of_task_execution=datetime.datetime.now().date()
        date_in_format_for_JSONInsert='$."'+str(date_of_task_execution)+'"' #The '$' is for JSONInsert format
        task_result_json={date_in_format_for_JSONInsert:0}
        NotificationLog.objects.filter(notify_id=data['notify_id'],prim_key=data['prim_key']).update( email_task_result=JSONInsert('email_task_result', task_result_json))
        

@shared_task
def send_notification_via_phone(data,subject,signature):
    body = data['msg']
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    body = h.handle(body)
    body = str(body).strip()
    print(body)
    body = body.replace('**'," ")
    body = body.replace('<',"")
    body = body.replace('/>',"")
    body = body + "\n" + signature
    print(body)
    uname = SMS_USERNAME
    pwd = SMS_PASSWORD
    senderid = SMS_SENDERID
    for phone_no in data['phone']:
        data_msg ={}
        data_msg = {'username': uname, 'pass': pwd, 'senderid': senderid, 'dest_mobileno':9792920841, 'message': body ,'response': 'Y'}
        response = requests.post('https://www.smsjust.com/blank/sms/user/urlsms.php', data=data_msg)
        print(response)
        date_of_task_execution=datetime.datetime.now().date()
        date_in_format_for_JSONInsert='$."'+str(date_of_task_execution)+'"' #The '$' is for JSONInsert format
        if response.status_code != 200:
            NotificationLog.objects.filter(notify_id=data['notify_id'],prim_key=data['prim_key']).update(phone_task_result=JSONInsert('phone_task_result', {date_in_format_for_JSONInsert:0}))
        else:
            NotificationLog.objects.filter(notify_id=data['notify_id'],prim_key=data['prim_key']).update(phone_task_result=JSONInsert('phone_task_result', {date_in_format_for_JSONInsert:1}))
              
@HUEY.periodic_task(crontab(minute='*',hour='*',day='*',month='*'))
def JOB():
    current_date=datetime.datetime.now().date()
    json_task_date='$."'+str(current_date)+'"'
    query_list=Job.objects.filter(next_execution_date=current_date,status=1,flag=1).order_by('-task_priority').values()
    print(" Query list ",len(query_list))
    for query in query_list:
        res = send_notification.apply_async(args=json.loads(query["args"]),priority=query["task_priority"])
        SendNotification.objects.filter(id=query["notify_id_id"]).update(task_name=str(res))
        next_execution_date=query["next_execution_date"]+datetime.timedelta(days=(query["interval"]))
        if next_execution_date > query["end_date"]:
            Job.objects.filter(id=query["id"]).update(status=0,next_execution_date=next_execution_date,task_name=JSONInsert('task_name',{json_task_date:str(res)}),job_result=JSONInsert('job_result',{json_task_date:1}))
        else:
            Job.objects.filter(id=query["id"]).update(next_execution_date=next_execution_date,task_name=JSONInsert('task_name',{json_task_date:str(res)}),job_result=JSONInsert('job_result',{json_task_date:1}))
