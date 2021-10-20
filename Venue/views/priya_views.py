from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.db.models import Sum,F
from login.views import checkpermission,generate_session_table_name
import json
from Venue.constants_functions import requestType
from Venue.views.venue_functions import *
from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from Registrar.models import *
from login.models import EmployeePrimdetail
from musterroll.models import Roles
from Venue.models import *
from itertools import groupby
import datetime
from datetime import date
import time

def admin_approval(request):
    session=request.session['Session_id']
    emp_id=request.session['hash1']
    if checkpermission(request,[rolesCheck.ROLE_ADMIN_OFFICER])== statusCodes.STATUS_SUCCESS:
        data={}
        if requestMethod.GET_REQUEST(request):
            today=datetime.date.today()
            if(requestType.custom_request_type(request.GET,'form_data')):
                if 'id' in request.GET:
                    id = request.GET['id']
                    approval_status = request.GET['approval_status']
                    remark = request.GET['remark']
                    venue_new = request.GET['venue']
                    # VenueBookingApproval.objects.filter(id = id).update(status='DELETE')
                    new = list(VenueBookingApproval.objects.filter(id = id).values_list('booking_detail',flat = True))
                    # VenueBookingApproval.objects.filter(id = id).update(level=-1)
                    VenueBookingApproval.objects.create(approval_status = approval_status,level = 2,remark = remark,venue_detail = VenueDetails.objects.get(id = venue_new),booking_detail = VenueBooking.objects.get(id = new[0]),approved_by = EmployeePrimdetail.objects.get(emp_id = emp_id))
                approval_req = get_venue_approval_data({'level':1,'approval_status':"APPROVED",'booking_detail__start_date__gte':today})
                emp_id_hod = list(Roles.objects.filter(roles__value__contains="HOD").values_list('emp_id'))
                approval_hod_req = get_venue_approval_data({'level':1,'approval_status':"PENDING",'booking_detail__start_date__gte':today,'booking_detail__added_by__in':emp_id_hod})
                
                approval_req.extend(approval_hod_req)
                send_data_values = []
                for x in approval_req:
                    if len(get_venue_approval_data({'booking_detail' :x['booking_detail'], 'level':2, 'approval_status':"APPROVED"}))>0:
                       continue 
                    send_data_values.append(x)
                    argument = list(VenueBookingApproval.objects.filter(id=x['id']).values('booking_detail__start_date','booking_detail__end_date','booking_detail__participants'))
                    venue = get_vacant_places(str(argument[0]['booking_detail__start_date']),str(argument[0]['booking_detail__end_date']),9999999999,session)
                    send_data_values[-1]['venue'] = venue
                data = { 'data':send_data_values }
                
            elif(requestType.custom_request_type(request.GET,'view_previous')):
                if 'id' in request.GET:
                    id = request.GET['id']
                    data = list(VenueBookingApproval.objects.filter(id = id).values('booking_detail'))
                    old = list(VenueBookingApproval.objects.filter(booking_detail=data[0]['booking_detail'],level=1).values('id','venue_detail','approval_status','booking_detail','approved_by','level','remark').order_by('-id'))
                    VenueBookingApproval.objects.filter(booking_detail=data[0]['booking_detail'],level=1).update(status = "DELETE")
                    VenueBookingApproval.objects.filter(id= id).update(status = "DELETE")
                    VenueBookingApproval.objects.create(approval_status = 'APPROVED',level = 1,remark = old[0]['remark'],venue_detail = VenueDetails.objects.get(id = old[0]['venue_detail']),booking_detail = VenueBooking.objects.get(id = old[0]['booking_detail']),approved_by = EmployeePrimdetail.objects.get(emp_id = old[0]['approved_by']))
                    data = {}
                else:
                    status = ['APPROVED','REJECTED']
                    data = get_venue_approval_data({'level':2,'approval_status__in':status})
        return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def Venue_Details(request):
    session=request.session['Session_id']
    emp_id=request.session['hash1']
    if checkpermission(request,[rolesCheck.ROLE_ADMIN_OFFICER])== statusCodes.STATUS_SUCCESS:
        data=[]
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET,'form_data')):
                if 'name' in request.GET and 'id' in request.GET:
                    id=request.GET['id']
                    if id:
                        qry=VenueDetails.objects.filter(id=id).exclude(status='DELETE').values('name')
                        if qry:
                            VenueDetails.objects.filter(id=id).update(status='DELETE')
                        data=statusMessages.MESSAGE_UPDATE
                    else:
                        data=statusMessages.MESSAGE_INSERT
                    VenueDetails.objects.create(name=request.GET['name'],description=request.GET['description'],eligible_occupancy=request.GET['eligible_occupancy'],booking_limit=request.GET['booking_limit'],venue_image=request.GET['venue_image'],added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
                elif 'key' in request.GET:
                    id=request.GET['id']
                    qry=VenueDetails.objects.filter(id=id).exclude(status='DELETE').values('name')
                    if qry:
                        VenueDetails.objects.filter(id=id).update(status='DELETE')
                        data=data=statusMessages.MESSAGE_DELETE
                else:
                    data=get_venue_list()
                return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
