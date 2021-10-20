from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.db.models import Sum,F,Q
from login.views import checkpermission,generate_session_table_name
import json
from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from Registrar.models import *
from login.models import EmployeePrimdetail
from Venue.models import *
from datetime import datetime

def get_vacant_places(start_date,end_date,participants,session):

    start_date_format=datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')
    end_date_format=datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')
    occupied_venue_list=list(VenueBookingApproval.objects.filter(approval_status='APPROVED',booking_detail__session=session,level=2).exclude(status='DELETE').values('venue_detail','booking_detail__start_date','booking_detail__end_date'))

    booking_days=abs((end_date_format-start_date_format).days)   
    venue_id=[]
    if occupied_venue_list:
        for venue in occupied_venue_list:
            if not ((venue['booking_detail__end_date']<start_date_format) or (venue['booking_detail__start_date']>end_date_format)):
                venue_id.append(venue['venue_detail']) 
        venue_available=list(VenueDetails.objects.filter(booking_limit__gte=booking_days,eligible_occupancy__lte=participants).exclude(id__in=venue_id).exclude(status='DELETE').values('id','name','description','venue_image','booking_limit','eligible_occupancy','added_by'))
    else:
        venue_available=list(VenueDetails.objects.filter(booking_limit__gte=booking_days,eligible_occupancy__lte=participants).exclude(status='DELETE').values('id','name','description','venue_image','booking_limit','eligible_occupancy','added_by'))

    return venue_available

def get_venue_list():
    
    venue_list=list(VenueDetails.objects.exclude(status='DELETE').values('id','name','description','venue_image','booking_limit','eligible_occupancy'))
    return venue_list

def get_venue_approval_data(extra_filter):
    data = []
    qry = list(VenueBookingApproval.objects.filter(**extra_filter).exclude(status='DELETE').values('id','level','venue_detail','venue_detail__name','venue_detail__description','venue_detail__eligible_occupancy','booking_detail__purpose','booking_detail','booking_detail__added_by__name','approval_status','booking_detail__start_date','booking_detail__end_date','booking_detail__participants','remark','time_stamp').order_by('-booking_detail__start_date'))
    for q in qry:
        if q['level']!=1:
            data.append(q)
        else:
            query = list(VenueBookingApproval.objects.filter(booking_detail=q['booking_detail'],level=2).exclude(status="DELETE").values())
            if len(query)==0:
                data.append(q)
    return data

def function_list(extra_filter):
    previous_list=list(VenueBookingApproval.objects.exclude(status='DELETE').exclude(booking_detail__status='DELETE').exclude(venue_detail__status='DELETE').filter(**extra_filter).values('booking_detail','id','approval_status','approval_status','approved_by','approved_by','booking_detail__start_date','booking_detail__end_date','booking_detail__purpose','booking_detail__participants','booking_detail__remark','level','remark','venue_detail','venue_detail__name','venue_detail__venue_image','venue_detail__description').order_by('-booking_detail__start_date'))
    return previous_list