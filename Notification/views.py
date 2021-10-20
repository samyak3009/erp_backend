from django.shortcuts import render

# Create your views here.


from .serializers import DataStructureSerializer ,DataSetSerializer , CreateGroupSerializer,CreateSubGroupSerializer, CreateTemplateSerializer,SendNotificationSerializer
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib import messages
from django.http import Http404
from django.db.models import Count
from django.db.models import F
from django_celery_beat.models import PeriodicTask, IntervalSchedule,CrontabSchedule
from django.utils.dateparse import parse_datetime
from .models import DataStructure ,DataSet,Group,SubGroup,Template,SendNotification, Job
from .functions import check_duplicate_name,validate_ids,check_duplicate_subgroup_name,check_duplicate_group_name,check_duplicate_Template_name,get_primkey
from .constant_variables.constant_variables import PRIORITY,SCHEDULING,SUBJECT_LENGTH
from .tasks import read_insert_file ,add_rows,update_uniq_field,add_groups,add_sub_groups,send_notification
from .constant_functions.constant_functions import getUniqFieldData,checkpermission,getUser
from erp.constants_variables import rolesCheck
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser,MultiPartParser,JSONParser
# from rest_framework.parsers import JSONParser,
from rest_framework.exceptions import ParseError
from rest_framework import generics
from rest_framework import mixins
from rest_framework import filters
from datetime import datetime
from dateutil.parser import parse
import datetime
import csv,io
import json
import itertools
from nested_lookup import nested_lookup
from email_validator import validate_email, EmailNotValidError

from erp.constants_variables import statusCodes, statusMessages
from erp.constants_functions import requestMethod, functions
from StudentSMM.constants_functions import requestType



# class LoginView(APIView):

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data["user"]
#         django_login(request, user)
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({"token": token.key,
#                   "user_id":user.pk}, status=200)


# class LogoutView(APIView):
#     authentication_classes = (TokenAuthentication, )

#     def post(self, request):
#         django_logout(request)
#         return Response(status=204) 

class UploadDataView(APIView):
    parser_class = (MultiPartParser,)

    def get_object(self, file_name):
        try:
            return DataStructure.objects.exclude(status=0).get(name=file_name)
        except DataStructure.DoesNotExist:
            raise Http404

    def post(self,request):
        msg = ""
        if(200):
            if 'file' not in request.data:
                raise ParseError("Empty content")
            # print(json.loads(request.body))
            data = request.data
            file = data['file']
            file_name = data['file_name'].strip()
            file_type = ['csv']
            if file.name.split('.')[-1] not in file_type:
                DataStructure.objects.filter(name=file_name).update(status=0)
                status = 415
                return Response({"message":'THIS TYPE OF FILE IS NOT ACCEPTED'},status=status)
            file_name_id = self.get_object(file_name)    #Get object of file with name for DataSettings
            qry = list(DataStructure.objects.filter(data_id=file_name_id.data_id).values('data_fields'))
            reader = csv.DictReader(io.StringIO(file.read().decode('utf-8'))) #Read csv as Dict of csv class
            prim_key=""
            email_li = []
            phone_li = []
            for fields in qry[0]['data_fields']:
                if fields['is_unique']== 1:
                    prim_key=fields['field_name']
                elif fields['is_email']==1:
                    email_li.append(fields['field_name'])
                elif fields['is_phone']==1:
                    phone_li.append(fields['field_name'])
            dataset_list=[]
            primkey_list = []
            for row in reader:
                data={}
                row['group'] = []
                row['sub_group'] = []
                # for email in email_li:    
                #     try:  # Validate.
                #         valid = validate_email(row[email])  # Update with the normalized form.
                #         email = valid.email
                #     except EmailNotValidError as e:    # email is not valid, exception message is human-readable
                #         DataStructure.objects.filter(name=file_name).update(status=0)
                #         status = 202
                #         return Response({'msg':str(e)+row[email]},status=status)
                # for phone in phone_li:
                #     if not len(row[phone])==10:
                #         msg = "Phonenumber is invalid "+str(row[phone])#10 digit
                #         status = 202
                #         DataStructure.objects.filter(name=file_name).update(status=0)
                #         return Response({'msg':msg},status=status)
                data['data_id']=file_name_id.data_id #Settintg id of data
                data['data_json']=row
                if row[prim_key] != "":
                    if str(row[prim_key]).strip() not in primkey_list:
                        primkey_list.append(str(row[prim_key]).strip())
                    if file_name_id.data_id == 1:
                        data['prim_key']= data['data_json']['NAME']+"("+str(row[prim_key]).strip()+")" #unique cloumn from csv
                    else:
                        data['prim_key']=str(row[prim_key]).strip()
                else:
                    msg = "Uniq field cannot be empty"
                    status = 202
                    DataStructure.objects.filter(name=file_name).update(status=0)
                    return Response({'msg':msg},status=status)
                dataset_list.append(data)
            if len(primkey_list)!= len(set(primkey_list)):
                msg = "Duplicate unique field present"
                status = 202
                DataStructure.objects.filter(name=file_name).update(status=0)
                return Response({'msg':msg},status=status)

            l =read_insert_file.delay(dataset_list) #Celery task call for inserting dataset 
            msg = "Data successfully uploaded"
            status = 200
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response ({'msg':msg},status=status)
        
class UploadDataSettingView(APIView):

    def get_object(self,ids):
        return  DataStructure.objects.get(data_id=ids)

    def post(self,request):
        msg = ""
        if( 200):
            data=request.data
            status = 200
            accessible_by = data['accessible_by']
            if check_duplicate_name(data['name'].strip()): #check whether file with same name present before
                msg="File with this name already uploaded.Kindly change the file name."
                status = 202
            else:
                data_fields_list=[]
                for column in data['column']:
                    fields={}
                    fields['field_name']=column['column']
                    fields['type']="STRING" if column['type'] == 'str' else "NUMERIC"
                    fields['is_email'] = column['email'] 
                    fields['is_phone'] = column['phone_no'] 
                    fields['is_unique'] =  column['unique'] 
                    fields['is_filter'] = column['filter']
                    data_fields_list.append(fields)
                user = getUser(request)
                accessible_by.append(str(user))
                serializer = DataStructureSerializer(data={'data_fields':data_fields_list,'accessible_by':accessible_by,'name':data['name'].strip()})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    msg = "Settings successfully uploaded"
                    status = 200
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response ({'msg':msg},status=status)

    def put(self,request):#Update DataSettings (Uniq field,email,filterable..)
        msg = ""
        if(checkpermission(request, [rolesCheck.ROLE_NOTIFICATION]) == 200):
            data = request.data
            if request.data['method']=="update":
                old_uniq_column =request.data['old']#(Old Uniq field)
                new_uniq_column = request.data['new']#(new Uniq Field)
                if old_uniq_column != new_uniq_column:
                    update_uniq_field.delay(new_uniq_column,data['data']['data_id'])#Celry task to update (if uniq fields then threading)
                instances = self.get_object(ids=data['data']['data_id'])
                accessible_by = data['data']['accessible_by']
                data['data']['status']=2
                user = getUser(request)
                accessible_by.append(str(user))
                serializer = DataStructureSerializer(
                    instances, data=data['data']
                    )
                if serializer.is_valid():
                    serializer.save()
                    msg = "Successfully updated"
                    status =200
            if request.data['method']=="delete":
                data_id = request.data['data_id']
                instances = self.get_object(ids=request.data['data_id'])
                serializer = DataStructureSerializer(
                    instances, data={"status":0},partial=True
                    )
                if serializer.is_valid():
                    serializer.save()
                    DataSet.objects.filter(data_id=data_id).update(status=0)
                    msg = "Successfully deleted"
                    status =200
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response ({'msg':msg},status=status)





class DynamicSearchFilter(filters.SearchFilter):
    
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])


class getDropdownSetting(APIView):

    filter_backends = (DynamicSearchFilter,)
    search_fields =[]
    serializer_class = DataSetSerializer

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset


    def get_queryset(self,data_id,type_of):
        if type_of is  None:
            return DataSet.objects.filter(data_id=data_id).exclude(status=0).values()
        else:
            return DataStructure.objects.filter(data_id=data_id).values()

    def get(self, request):
        if (200):
            type_of = None
            data_id = 1
            ######################GET TYPE AND DATA ID IN PARAMS###################
            if 'type' in self.request.query_params: 
                type_of =self.request.query_params['type']
            if 'data_id'  in self.request.query_params:
                data_id =self.request.query_params['data_id']
            ######################################################################## 
            if 'get_uniq_field' in self.request.query_params['request_type']:#get Prim Key of data_id
                if data_id ==1:
                    user = getUser(request)
                    data1 = getUniqFieldData(data_id)
                    data = list(filter(lambda i: i['prim_key'] != user, data1))
                else:
                    the_filtered_qs = list(self.filter_queryset(self.get_queryset(data_id,type_of)))
                    data = [t['prim_key'] for t in the_filtered_qs]
            elif 'get_filterable_fields' in self.request.query_params['request_type']:#get filterable fields by csv
                the_filtered_qs = list(self.filter_queryset(self.get_queryset(data_id,type_of)))
                filtered_list = []
                for qs in the_filtered_qs[0]['data_fields']:
                    if qs['is_filter'] == 1:
                        filtered_list.append(qs['field_name'])
                data =filtered_list

            elif 'get_filterable_data' in self.request.query_params['request_type']:# get_filterable_data of csv("Course":"B.tech","B.pharm")
                the_filtered_qs = self.filter_queryset(self.get_queryset(data_id,type_of)).values_list('data_json',flat=True)
                field = self.request.query_params['field_name']
                if 'group_id' in self.request.query_params:
                    group_id = self.request.query_params['group_id']
                    group_qs = the_filtered_qs.filter(data_json__group__contains=int(group_id))
                    data = set(nested_lookup(field,list(group_qs)))
                else:
                    data = set(nested_lookup(field,list(the_filtered_qs)))

            elif 'get_data_by_filter' in self.request.query_params['request_type']:#get_data_by_filter of csv ("filters":{"Course":"B.tech","Dept":"IT"}) 
                filters = json.loads(request.query_params['filters'])
                li = []
                product = (dict(zip(filters, x)) for x in itertools.product(*filters.values()))#cartesian products of filters
                all_fil = list(product)
                the_filtered_qs = self.filter_queryset(self.get_queryset(data_id,type_of)).values('data_json')
                for f in all_fil:
                    fil_data = list(the_filtered_qs.filter(data_json__contains = f))
                    li.extend(fil_data)
                data = li
            elif 'get_group_data_by_filter' in self.request.query_params['request_type']:# get_group_data_by_filter from dataset by groupid
                group_id = request.query_params['group_id']
                filters = json.loads(request.query_params['filters'])
                li = []
                product = (dict(zip(filters, x)) for x in itertools.product(*filters.values()))#cartesian products of filters
                all_fil = list(product)
                the_filtered_qs = self.filter_queryset(self.get_queryset(data_id,type_of)).values('data_json')
                group_qs = the_filtered_qs.filter(data_json__group__contains=int(group_id))
                for f in all_fil:
                    fil_data = list(group_qs.filter(data_json__contains = f))
                    li.extend(fil_data)
                data = li
            elif 'get_group_data' in self.request.query_params['request_type']:# get_group_data from dataset by groupid
                group_id = request.query_params['group_id']
                the_filtered_qs = self.filter_queryset(self.get_queryset(data_id,type_of)).values('data_json')
                group_qs = the_filtered_qs.filter(data_json__group__contains=int(group_id))
                data = list(group_qs)
            elif 'get_subgroup_data' in self.request.query_params['request_type']:# get_subgroup_data from group by subgrupid
                subgroup_id = request.query_params['subgroup_id']
                the_filtered_qs = self.filter_queryset(self.get_queryset(data_id,type_of)).values('data_json')
                data = list(the_filtered_qs.filter(data_json__sub_group__contains=int(subgroup_id)))
            elif 'get_field_name_by_type' in self.request.query_params['request_type']:#get fieldsname(email,phone,unique) by csv
                the_filtered_qs = list(self.filter_queryset(self.get_queryset(data_id,type_of)))
                email_li = []
                phone_li = []
                uniq_field = ""
                field_name = []
                for field in the_filtered_qs[0]['data_fields']:
                    field_name.append(field['field_name'])
                    if field['is_email'] == 1:
                        email_li.append(field['field_name'])
                    elif field['is_phone'] == 1:
                        phone_li.append(field['field_name'])
                    elif field['is_unique']== 1:
                        uniq_field = field['field_name']
                data = {"email":email_li,"phone":phone_li,"uniq":uniq_field,"fields":field_name
                }

            return Response(data)
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response ({'msg':msg},status=status)

    def post(self,request):
        if (200):
            body = request.data
            type_of = None
            data_id = 1
            if 'type' in body: 
                type_of = body['type']
            if 'data_id'  in body:
                data_id = body['data_id']

            if 'get_filterable_data' in body['request_type']:# get_filterable_data of csv("Course":"B.tech","B.pharm") #for first dropdown in group
                the_filtered_qs = self.filter_queryset(self.get_queryset(data_id,type_of)).values_list('data_json',flat=True)
                field = body['field_name']
                if 'group_id' in body:
                    group_id = body['group_id']
                    group_qs = the_filtered_qs.filter(data_json__group__contains=int(group_id))
                    data = set(nested_lookup(field,list(group_qs)))
                else:
                    data = set(nested_lookup(field,list(the_filtered_qs)))

            
            elif 'subgroup_dropdown' in body['request_type']:
                group_id = body['group_id']
                filters = body['filters']
                li = []
                product = (dict(zip(filters, x)) for x in itertools.product(*filters.values()))#cartesian products of filters
                all_fil = list(product)
                the_filtered_qs = self.filter_queryset(self.get_queryset(data_id,type_of)).values('data_json')
                group_qs = the_filtered_qs.filter(data_json__group__contains=int(group_id))
                for f in all_fil:
                    fil_data = list(group_qs.filter(data_json__contains = f))
                    li.extend(fil_data)
                data = li
                data = list(set(nested_lookup(body['field_name'],list(li))))
                
            elif 'group_dropdown' in body['request_type']:
                filters = body['filters']
                li = []
                product = (dict(zip(filters, x)) for x in itertools.product(*filters.values()))#cartesian products of filters
                all_fil = list(product)
                the_filtered_qs = self.filter_queryset(self.get_queryset(data_id,type_of)).values('data_json')
                for f in all_fil:
                    fil_data = list(the_filtered_qs.filter(data_json__contains = f))
                    li.extend(fil_data)
                data = li
                data = list(set(nested_lookup(body['field_name'],list(li))))
            return Response(data)
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response ({'msg':msg},status=status)


class ViewPreviousView(APIView):

    def get_queryset(self,user):#name of csv ,id and no. of rows
        return DataStructure.objects.filter(accessible_by__contains=[user]).exclude(status=0).values('name','data_id','data_fields','accessible_by').order_by('data_id')

    def get(self, request, format=None):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            if request.GET['request_type']=='get_data':
                user=getUser(request)
                # if 'user' in request.query_params:
                #     user = self.request.query_params['user']
                datasets = list(self.get_queryset(user))
                for data in datasets:
                    data['row_count']= DataSet.objects.filter(data_id=data['data_id']).exclude(status=0).count()
                
            return Response(datasets)
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response ({'msg':msg},status=status)






class RowDataSetDetails(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    serializer_class = DataSetSerializer

    def get_queryset(self,data_id):
        return DataSet.objects.filter(data_id=data_id).exclude(status=0).values()

    def list(self,data_id , request, *args, **kwargs):
        return self.get_queryset(data_id)

    def get(self, request, *args, **kwargs):#get all rows of a dataset
        data = self.list(self.request.query_params['data_id'] ,request, *args, **kwargs)
        return Response(data)

    def create(self,request, *args, **kwargs):
        data = json.loads(request.body)
        qry = get_primkey(data["data"][0]['data_id'])
        for row in data["data"]:
            if str(row['prim_key']) in qry:
                return False
            else:
                row['prim_key'] = str(row['prim_key']).strip()
            row["data_json"]['group'] = []
            row["data_json"]['sub_group'] = []
        add_rows.delay(data['data']) #Add rows in dataset by celery
        return True

    def post(self, request, *args, **kwargs):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            data = self.create(request, *args, **kwargs)
            if data!=True:
                return Response({'msg':'Uniq field value already exists'},status=202)
            return Response({'msg':'Data Successfully uploaded'})
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response ({'msg':msg},status=status)




class TaskUpdateView(generics.UpdateAPIView):#Update data set rows
    """
    # Update Task
    """
    
    serializer_class = DataSetSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True #List Serialzer multiple objects to update

        return super(TaskUpdateView, self).get_serializer(*args, **kwargs)

    def get_queryset(self,ids=None):
        if ids:
            return  DataSet.objects.filter(id__in=ids)

    def update(self, request, *args, **kwargs):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            if request.data['method']=="update":#Update row from csv
                ids = validate_ids(request.data['data'],"id")
                instances = self.get_queryset(ids=ids)
                # qry = get_primkey(request.data["data"][0]['data_id_id'])
                for data in request.data['data']:
                    data['prim_key'] = str(data['prim_key']).strip()
                    data['status']=2 #status UPDATE=2
                serializer = self.get_serializer(
                    instances, data=request.data['data'], partial=False, many=True
                )
                if serializer.is_valid():
                    self.perform_update(serializer)
                    msg = "Row updated successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status = 400
            elif request.data['method']=='delete':#Delete row from csv
                ids = validate_ids(request.data['data'],"id")
                instances = self.get_queryset(ids=ids)
                for data in request.data['data']:
                    data['status']=0 #Status DELETE=0
                serializer = self.get_serializer(
                    instances, data=request.data['data'], partial=False, many=True
                )
                if serializer.is_valid():
                    self.perform_update(serializer)
                    msg = "Row deleted successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status = 400
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)


        

class Creategroup(APIView):

    serializer_class = CreateGroupSerializer

    def get_object(self, data_id):
        try:
            return DataStructure.objects.get(data_id=data_id)
        except DataStructure.DoesNotExist:
            raise Http404


    def get_queryset(self,user):
        return Group.objects.filter(accessible_by__contains=[user]).exclude(status=0).values()


    def get(self, request, format=None):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            if request.GET['request_type']=='get_groups':#get all groups under one access
                user = getUser(request)
                # user = self.request.query_params['user']
                datasets = self.get_queryset(user)
            return Response(datasets)
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)



    def post(self,request):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            data = request.data
            if check_duplicate_group_name(data['group_name'].strip()): #check whether file with same name present before
                msg="Group with this name already created.Kindly change the Group name."
                status =202
            else:
                ids = data.pop("ids") #primkeys to add in group
                data_id = self.get_object(data['data_id'])
                accessible_by = data['accessible_by']
                user = getUser(request)
                accessible_by.append(str(user))
                serializer = CreateGroupSerializer(data={'group_name':data['group_name'].strip(),'accessible_by':accessible_by,'data_id':data_id.data_id})
                if serializer.is_valid():
                    serializer.save()
                    add_groups.delay(data['data_id'],ids,serializer.data['id'])
                    msg="Group created Successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)


    def put(self,request):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            if request.data['method']=='update':    
                group_id = request.data['data']['group_id']
                instances = Group.objects.get(id=group_id)
                request.data['data']['status']=2    
                accessible_by = request.data['data']['accessible_by']
                user = getUser(request)
                accessible_by.append(str(user))
                serializer = CreateGroupSerializer(instances,data=request.data['data'],partial=False)
                if serializer.is_valid():
                    serializer.save()
                    msg="Group updated successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400
            if request.data['method']=='delete':
                group_id = request.data['data']['group_id']
                instances = Group.objects.get(id=group_id)
                request.data['data']['status']=0
                serializer = CreateGroupSerializer(instances,data=request.data['data'],partial=False)
                if serializer.is_valid():
                    serializer.save()
                    msg="Group deleted successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)






class CreateSubgroup(APIView):

    serializer_class = CreateSubGroupSerializer

    def get_object(self, group_id):
        try:
            return Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise Http404

    def get_queryset(self,user):
        return SubGroup.objects.filter(accessible_by__contains=[user]).exclude(status=0).values("id","subgroup_name","group_id","accessible_by","status","time_stamp","group_id__data_id")


    def get(self, request, format=None):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            if request.GET['request_type']=='get_subgroups':#get all sub groups under one access
                user = getUser(request)
                # user = self.request.query_params['user']
                datasets = self.get_queryset(user)
            return Response(datasets)
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)


    def post(self,request):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            data = request.data
            if check_duplicate_subgroup_name(data['subgroup_name'].strip()): #check whether file with same name present before
                msg="SubGroup with this name already created.Kindly change the SubGroup name."
                status =202
            else:
                ids = data.pop("ids") #primkeys to add in subgroup
                group_id = self.get_object(data['group_id'])
                accessible_by = data['accessible_by']
                user = getUser(request)
                accessible_by.append(str(user))
                serializer = CreateSubGroupSerializer(data={'subgroup_name':data['subgroup_name'].strip(),'accessible_by':accessible_by,'group_id':group_id.id})
                if serializer.is_valid():
                    serializer.save()
                    add_sub_groups.delay(data['data_id'],ids,serializer.data['id'])
                    msg="SubGroup created successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)

    def put(self,request):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            if request.data['method']=='update':
                subgroup_id = request.data['data']['subgroup_id']
                instances = SubGroup.objects.get(id=subgroup_id)
                request.data['data']['status']=2
                accessible_by = request.data['data']['accessible_by']
                user = getUser(request)
                accessible_by.append(str(user))
                serializer = CreateSubGroupSerializer(instances,data=request.data['data'],partial=False)
                if serializer.is_valid():
                    serializer.save()
                    msg="SubGroup Updated successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400
            if request.data['method']=='delete':
                subgroup_id = request.data['data']['subgroup_id']
                instances = SubGroup.objects.get(id=subgroup_id)
                request.data['data']['status']=0
                serializer = CreateSubGroupSerializer(instances,data=request.data['data'],partial=False)
                if serializer.is_valid():
                    serializer.save()
                    msg="SubGroup deleted successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)






class CreateTemplate(APIView):

    serializer_class = CreateTemplateSerializer

    def get_queryset(self,user):
        return Template.objects.filter(accessible_by__contains=[user]).exclude(status=0).values()


    def get_object(self,temp_id):
        try:
            return Template.objects.get(id=temp_id)
        except Template.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            if request.GET['request_type']=='get_templates':#get all templates under one access
                user = getUser(request)
                datasets = self.get_queryset(user)
            return Response(datasets)
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)



    def post(self,request):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            data = json.loads(request.body)
            if check_duplicate_Template_name(data['template_name'].strip()): #check whether file with same name present before
                msg="Template with this name already created.Kindly change the Template name."
                status =202
            else:
                user = getUser(request)
                data['accessible_by'].append(str(user))
                serializer = CreateTemplateSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    msg="Template created successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)

    def put(self,request):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            if request.data['method']=='update':
                temp_id = request.data['data']['temp_id']
                instances = self.get_object(temp_id)
                request.data['data']['status']=2 #status UPDATE=2
                serializer = CreateTemplateSerializer(instances,data=request.data['data'],partial=False)
                if serializer.is_valid():
                    serializer.save()
                    msg="Template updated successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400 
            if request.data['method']=='delete':
                temp_id = request.data['data']['temp_id']
                instances = self.get_object(temp_id)
                request.data['data']['status']=0 #status DELETE=0
                serializer = CreateTemplateSerializer(instances,data=request.data['data'],partial=False)
                if serializer.is_valid():
                    serializer.save()
                    msg="Template deleted successfully"
                    status = 200
                else:
                    msg = serializer.errors
                    status =400
        else:
            msg = "You are unauthorized for this request"
            status = 403
        return Response({"msg":msg},status=status)


class SendNotificationView(APIView):

    parser_class = (MultiPartParser,)
    def get_object(self, data_id):
        try:
            return DataStructure.objects.get(data_id=data_id)
        except DataStructure.DoesNotExist:
            raise Http404

    def get_queryset(self,data_id):
        return DataSet.objects.filter(data_id=data_id).exclude(status=0).values("prim_key","id","data_id","data_json").annotate(data_fields=F("data_id__data_fields")).annotate(name=F("data_id__name"))

    def post(self,request):
        if (checkpermission(request, [rolesCheck.ROLE_NOTIFICATION])==200):
            data = request.data
            if len(data['subject'].strip())>SUBJECT_LENGTH:
                return Response({'msg':"Subject length limit exceeding"},status=202)
            group_id = None
            email_li = []
            subject = data['subject'].strip()
            phone_li = []
            subgroup_id = None
            data_id = None
            portal = data['portal']
            template_id = None
            uniq_field = None
            start_date = data['start_date']
            expiry_date = data['expiry_date']
            if 'file' not in data:
                base_queryset = self.get_queryset(data['data_id'])
                data_id = data['data_id']
                if "dataset" in data['operation_on']:
                    if "all" in data['send_to']:
                        qs = base_queryset
                    elif "few" in data['send_to']:
                        qs = base_queryset.filter(prim_key__in=data['prim_id'])       
                elif "group" in data['operation_on']:
                    # group_id = json.dumps(data['group_id'])
                    group_id = data['group_id']
                    qs = base_queryset.filter(data_json__group__contains=group_id)
                elif "subgrp" in data['operation_on']:
                    # subgroup_id = json.dumps(data['subgroup_id'])
                    subgroup_id = data['subgroup_id']
                    qs = base_queryset.filter(data_json__sub_group__contains=subgroup_id)
                primkey_list = qs.values_list('prim_key',flat=True)
                if "email_li" in data:
                    email_li = data['email_li']
                if "phone_li" in data:
                    phone_li = data['phone_li']
                uniq_field = data['uniq_field']
                qs_list = qs.values_list("data_json",flat=True)
                if 'template_id' in data:
                    template_obj = Template.objects.get(id=data['template_id'])
                    template_id = data['template_id']
                    template_body = template_obj.body
                    temp_data_key = data['temp_data_key']
                else:
                    template_body=data['template_body']
                    temp_data_key = data['temp_data_key']
            else:
                data = data.dict()
                file = data['file']
                file_type = ['csv']
                uniq_field = data['uniq_field']
                if file.name.split('.')[-1] not in file_type:
                    return Response({"message":'THIS TYPE OF FILE IS NOT ACCEPTED'})
                if "dataset" in data['operation_on']:
                    base_queryset = self.get_queryset(data['data_id'])
                    reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')))
                    primkey_list = nested_lookup(reader.fieldnames[0],list(reader))
                    qs = base_queryset.filter(prim_key__in=primkey_list)
                    qs_list = qs.values_list("data_json",flat=True)
                else:
                    reader = csv.DictReader(io.StringIO(file.read().decode('utf-8'))) #Read csv as Dict of csv class
                    qs = list(reader)
                    primkey_list = nested_lookup(uniq_field,qs)
                    qs_list = qs
                if "email_li" in data:
                    email_li=data["email_li"].split(",")
                if "phone_li" in data:
                    phone_li=data["phone_li"].split(",")
                template_body=data['template_body']
                temp_data_key = data['temp_data_key'].split(",")
                start_date = parse(json.loads(data['start_date']))
                expiry_date = parse(json.loads(data['start_date']))
            user=getUser(request)
            notification_data = {
                "data_id" :data_id,
                "group_id" : group_id,
                "subgroup_id":subgroup_id,
                "prim_keys" : list(primkey_list),
                "email" : email_li,
                "phone" : phone_li,
                "portal" : portal,
                "subject" : subject,
                "signature" : data['signature'],
                "template_id" : template_id,
                "template_body" : template_body,
                "temp_data_key" : temp_data_key,
                "priority":data['priority'],
                "scheduling" : data['scheduling'],
                "scheduling_other" : data['scheduling_other'],
                "start_date": start_date,
                "expiry_date" : expiry_date,
                # "send_by" : str(data["send_by"]),
                "send_by" : user,
            }
            serializer = SendNotificationSerializer(data=notification_data)
            if serializer.is_valid():
                serializer.save()

#################################################################################################################################################################################################
                # if data['scheduling'] in ["D","W","M"]:
                #     if data['scheduling'] is "D":
                #         schedule, _ = CrontabSchedule.objects.get_or_create(
                #         minute='0',
                #         hour='0',
                #         day_of_week='*',
                #         day_of_month='*',
                #         month_of_year='*',)
                #     elif data["scheduling"] is "M":
                #         if 'file' not in data:
                #             day_of_month =  datetime.datetime.strptime(str(start_date).split('T')[0], "%Y-%m-%d").date()
                #         else:
                #             day_of_month =  datetime.datetime.strptime(str(start_date).split(' ')[0], "%Y-%m-%d").date()
                #         print(day_of_month)
                #         schedule, _ = CrontabSchedule.objects.get_or_create(
                #         minute='0',
                #         hour='0',
                #         day_of_week='*',
                #         day_of_month=day_of_month.day,
                #         month_of_year='*', )
                #     elif data["scheduling"] is "W":
                #         if 'file' not in data:
                #             dayofweek = datetime.datetime.strptime(str(start_date).split('T')[0], "%Y-%m-%d").date().weekday()
                #         else:
                #             dayofweek = datetime.datetime.strptime(str(start_date).split(' ')[0], "%Y-%m-%d").date().weekday()
                #         schedule, _ = CrontabSchedule.objects.get_or_create(
                #         minute='0',
                #         hour='0',
                #         day_of_week=dayofweek,
                #         day_of_month='*',
                #         month_of_year='*', )
                #     print(schedule)
                #     try :
                #         PeriodicTask.objects.create(
                #              crontab=schedule,                  # we created this above.
                #              name='send_notification'+str(serializer.data['id']),          # simply describes this periodic task.
                #              task='Notification.tasks.send_notification',  # name of task.
                #              args=json.dumps([uniq_field,template_body,list(qs_list),temp_data_key,portal,serializer.data['id'],email_li,phone_li,subject,subject,data['signature']]),
                #              expires= expiry_date
                #           )
                #     except:
                #         pass
                # elif data['scheduling'] in ['OT']:
                #     schedule, _ = CrontabSchedule.objects.get_or_create(
                #         minute='*',
                #         hour='*',
                #         day_of_week='*',
                #         day_of_month='/'+str(data['days']),
                #         month_of_year='*', )
                #     try:
                #         PeriodicTask.objects.create(
                #             crontab=schedule,
                #             name='send_notification'+str(serializer.data['id']),
                #             task='Notification.tasks.send_notification',
                #             args=json.dumps([uniq_field,template_body,list(qs_list),temp_data_key,portal,serializer.data['id'],email_li,phone_li,subject,subject,data['signature']]),
                #             expires= expiry_date
                #             )
                #     except:
                #         pass
                # if data['priority'] == "H":
                #     res = send_notification.apply_async(args=(uniq_field,template_body,list(qs_list),temp_data_key,portal,serializer.data['id'],email_li,phone_li,subject,data['signature']),priority=0)
                #     SendNotification.objects.filter(id=serializer.data['id']).update(task_name=str(res))
                # elif data['priority'] == "L":
                #     res = send_notification.apply_async(args=(uniq_field,template_body,list(qs_list),temp_data_key,portal,serializer.data['id'],email_li,phone_li,subject,data['signature']),priority=9)
                #     SendNotification.objects.filter(id=serializer.data['id']).update(task_name=str(res))




#################################################################################### - Divyanshu - ####################################################################################################
               #This "priority" is used in "order_by" (in descending order) to execute the task with higher priority first. This priority is also given in Celery task while calling it.  
                if data['priority'] == "H":
                    task_priority=9
                elif data['priority'] == "L":
                    task_priority=0
                
                if 'file' not in data:
                    date1 =  datetime.datetime.strptime(str(start_date).split('T')[0], "%Y-%m-%d").date()
                    date2 =  datetime.datetime.strptime(str(expiry_date).split('T')[0], "%Y-%m-%d").date()
                else:
                    date1 =  datetime.datetime.strptime(str(start_date).split(' ')[0], "%Y-%m-%d").date()
                    date2 =  datetime.datetime.strptime(str(expiry_date).split(' ')[0], "%Y-%m-%d").date()
                #This "interval" is used to update the next_execution_date of the task.
                interval=1 #For Once and Daily scheduliing case
                if data['scheduling'] in ["W","M","OT"]:
                    if data["scheduling"] is "M":
                        interval=28 #Task will repeat after every 28 days (till the task meets its expiry date)     
                    elif data["scheduling"] is "W":
                        interval=7  #Task will repeat after every 7 days (till the task meets its expiry date) 
                    elif data['scheduling'] in ['OT']:
                        interval=data['days']

                args=json.dumps([uniq_field,template_body,list(qs_list),temp_data_key,portal,serializer.data['id'],email_li,phone_li,subject,data['signature']])
                Job.objects.create(notify_id=SendNotification.objects.get(id=serializer.data['id']),start_date=date1,next_execution_date=date1,interval=interval,end_date=date2,args=args,scheduling=data["scheduling"],task_priority=task_priority)

                message="Notification sent successfully"
                status = statusCodes.STATUS_SUCCESS
            else:
                print(serializer.errors)
                message = "Invalid data"
                status =statusCodes.STATUS_BAD_REQUEST
        else: 
            message = "You are unauthorized for this request"
            status = statusCodes.STATUS_UNAUTHORIZED
        message=statusMessages.CUSTOM_MESSAGE(message)    
        return Response(message,status=status)
#######################################################################################################################################################################################################


##################################################################################### - Divyanshu - ####################################################################################################
#Function to pause , resume and check status of the job task.
def pause_resume_job_task(request):
    if 'HTTP_COOKIE' in request.META:
        msg=""
        if request.user.is_authenticated:
            if checkpermission(request, [rolesCheck.ROLE_NOTIFICATION]) == statusCodes.STATUS_SUCCESS:
                if (requestMethod.POST_REQUEST(request)):
                    current_date=datetime.datetime.now().date()
                    body=json.loads(request.body)
                    #Taking Job id in list format from frontend. This pauses only one Job at a request. 
                    if (requestType.custom_request_type(body, 'pause')):
                        job=Job.objects.filter(id__in=body["id"],flag=1).values()
                        if len(job) >0:
                            if job[0]["status"] ==1:
                                Job.objects.filter(id=body["id"][0]).update(flag=0)
                                msg="Task is revoked successfully"
                            else:
                                msg="Task is already completed"
                        else:
                            msg="Task is already revoked"
                        
                        status=statusCodes.STATUS_SUCCESS
                       
                    # Taking Job id in list format from frontend. This resumes only one Job at a request. 
                    elif (requestType.custom_request_type(body, 'resume')):
                        job=Job.objects.filter(id__in=body["id"],flag=0).values()
                        if len(job) >0:
                            if job[0]["status"] ==1:
                                job=job.exclude(end_date__lt=current_date)
                                if len(job) >0:
                                    Job.objects.filter(id=body["id"][0]).update(flag=1,next_execution_date=current_date)
                                    msg="Task is restored successfully"
                                else:
                                    msg="Task is expired"
                            else:
                                msg="Task is already completed"
                        else:
                            msg="Task is already active"
                        status=statusCodes.STATUS_SUCCESS

                    # Taking Job id in list format from frontend. This gives the status of only one Job at a request
                    elif (requestType.custom_request_type(body, 'check_status')):
                        job=Job.objects.filter(id__in=body["id"]).values()
                        if(job[0]["status"]==0):
                            msg="Task is completed"
                        else:
                            if(job[0]["flag"]==1):
                                msg="Task is active"
                            else:
                                if(job[0]["end_date"]<current_date):
                                    msg="Task is paused and has been expired"
                                else:
                                    msg="Task is paused and it is restorable"
                        status=statusCodes.STATUS_SUCCESS
                    else:
                        msg="Invalid request_type"
                        status = statusCodes.STATUS_BAD_REQUEST
                    msg=statusMessages.CUSTOM_MESSAGE(msg)   
                else:
                    msg=statusMessages.MESSAGE_METHOD_NOT_ALLOWED
                    status = statusCodes.STATUS_METHOD_NOT_ALLOWED
            else:
                msg=statusMessages.MESSAGE_FORBIDDEN
                status = statusCodes.STATUS_FORBIDDEN           
        else:
            msg=statusMessages.MESSAGE_UNAUTHORIZED
            status = statusCodes.STATUS_UNAUTHORIZED
    else:
        msg=statusMessages.MESSAGE_BAD_REQUEST
        status = statusCodes.STATUS_BAD_REQUEST
    return functions.RESPONSE(msg,status)

#######################################################################################################################################################################################################



#-----------------------------------------------------------------------SQL------------------------------------------------------------#
# SELECT employee_primdetail.Emp_Status,employee_primdetail.DOJ,employee_address.P_Add1,employee_address.P_Add2,employee_address.P_City,employee_address.P_District,employee_address.P_Pincode,employee_address.C_Add1,employee_address.C_Add2,employee_address.C_City,employee_address.C_District,employee_address.C_Pincode,employee_address.C_State,employee_address.P_State, employee_primdetail.Name,employee_primdetail.Emp_Id,employee_primdetail.Email,employee_primdetail.Mob,employee_primdetail.Mob1,tb1.Value AS Deptartment, tb2.Value AS Desingnation,tb3.Value AS Current_position,tb4.Value AS Ladder,tb5.Value AS Cadre FROM employee_primdetail LEFT JOIN employee_dropdown tb1 ON employee_primdetail.Dept = tb1.Sno LEFT JOIN employee_dropdown tb2 ON employee_primdetail.Desg = tb2.Sno LEFT JOIN employee_dropdown tb3 ON employee_primdetail.Current_Pos=tb3.Sno LEFT JOIN employee_dropdown tb4 ON employee_primdetail.Ladder=tb4.Sno LEFT JOIN employee_dropdown tb5 ON employee_primdetail.Cadre=tb5.Sno INNER JOIN employee_address WHERE employee_address.Emp_Id=employee_primdetail.Emp_Id;

#--------------------------------------------------------------------------SQL--------------------------------------------------------------#


# SELECT Student_primdetail.Lib_id,Student_perdetail.FName,Student_perdetail.Mob_Sec,Student_perdetail.DOB,Student_perdetail.bank_Acc_no,Student_perdetail.aadhar_num, Student_primdetail.Name,LCASE(CONCAT(Student_primdetail.Name,".",Student_primdetail.Lib_id,"@kiet.edu")) AS kiet_email,Student_primdetail.Email_id,studentSession_2021o.Mob,Student_primdetail.Uni_Roll_No,student_semester.Sem,employee_dropdown.Value,studentSession_2021o.Uniq_Id,sections.Section,studentSession_2021o.Fee_Status,studentSession_2021o.Year,studentSession_2021o.Class_Roll_No,Student_Dropdown.Value FROM studentSession_2021o LEFT JOIN sections ON studentSession_2021o.Section_id=sections.Section_id LEFT JOIN Student_primdetail ON studentSession_2021o.Uniq_Id=Student_primdetail.Uniq_Id LEFT JOIN student_semester ON studentSession_2021o.Sem_id=student_semester.Sem_Id LEFT JOIN Student_course_detail ON Student_primdetail.Dept_detail=Student_course_detail.id LEFT JOIN employee_dropdown ON Student_course_detail.Dept_id=employee_dropdown.Sno LEFT JOIN Student_Dropdown ON Student_course_detail.Course_id=Student_Dropdown.Sno LEFT JOIN Student_perdetail ON studentSession_2021o.Uniq_Id=Student_perdetail.Uniq_Id ;






# SELECT Student_primdetail.Lib_id,Student_perdetail.FName,Student_perdetail.Mob_Sec,Student_perdetail.DOB,Student_perdetail.bank_Acc_no,Student_perdetail.aadhar_num, Student_primdetail.Name,LCASE(CONCAT(SUBSTRING_INDEX(Student_primdetail.Name," ",1),".",Student_primdetail.Lib_id,"@kiet.edu")) AS kiet_email,Student_primdetail.Email_id,studentSession_2021o.Mob,Student_primdetail.Uni_Roll_No,student_semester.Sem,employee_dropdown.Value,studentSession_2021o.Uniq_Id,sections.Section,studentSession_2021o.Fee_Status,studentSession_2021o.Year,studentSession_2021o.Class_Roll_No,Student_Dropdown.Value FROM studentSession_2021o LEFT JOIN sections ON studentSession_2021o.Section_id=sections.Section_id LEFT JOIN Student_primdetail ON studentSession_2021o.Uniq_Id=Student_primdetail.Uniq_Id LEFT JOIN student_semester ON studentSession_2021o.Sem_id=student_semester.Sem_Id LEFT JOIN Student_course_detail ON Student_primdetail.Dept_detail=Student_course_detail.id LEFT JOIN employee_dropdown ON Student_course_detail.Dept_id=employee_dropdown.Sno LEFT JOIN Student_Dropdown ON Student_course_detail.Course_id=Student_Dropdown.Sno LEFT JOIN Student_perdetail ON studentSession_2021o.Uniq_Id=Student_perdetail.Uniq_Id 