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
from Venue.models import *
from itertools import groupby
from datetime import datetime

def book_venue(request):
    if checkpermission(request,[rolesCheck.ROLE_EMPLOYEE])== statusCodes.STATUS_SUCCESS:
        session=request.session['Session_id']
        emp_id=request.session['hash1']
        data={}
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET,'get_vacant_places')):
                places=get_vacant_places(request.GET['date_from'],request.GET['date_to'],request.GET['participants'],session)
                data={'data':places}

                return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET,'venue_list')):
                venue_list=get_venue_list()
                data={'data':venue_list}

                return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET,'view_previous')):
                final_list=[]
                previous_list=function_list({'booking_detail__added_by':emp_id,'booking_detail__session':session})

                for k,v in groupby(previous_list,key=lambda x:x['booking_detail']):

                    v=list(v)
                    for s in v:
                        s['booking_detail__start_date']=s['booking_detail__start_date'].strftime("%Y-%m-%d %H:%M:%S")
                        s['booking_detail__end_date']=s['booking_detail__end_date'].strftime("%Y-%m-%d %H:%M:%S")
                    final_list.append(v)
                data={'data':final_list,'data2':get_venue_list()}

                return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
            else:
                return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST,statusCodes.STATUS_BAD_REQUEST)

        elif requestMethod.DELETE_REQUEST(request):
            data=json.loads(request.body)
            delete_qry=VenueBookingApproval.objects.filter(booking_detail=data['id']).update(status='DELETE')
            delete_qry1=VenueBookingApproval.objects.filter(id=data['id']).update(status='DELETE')
            
            data=statusMessages.CUSTOM_MESSAGE('Booking Application Deleted.')

            return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

        elif (requestMethod.POST_REQUEST(request)):
            data=json.loads(request.body)
            venue_id=data['venue']
            if 'booking_id' in data:
                # when booking is updated
                qry=VenueBooking.objects.filter(id=data['booking_id']).exclude(status='DELETE').update(start_date=data['date_from'],end_date=data['date_to'],participants=data['participants'],purpose=data['purpose'],remark=data['remark'],session=Semtiming.objects.get(uid=session),added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
                qry2=VenueBookingApproval.objects.filter(booking_detail=data['booking_id']).exclude(status='DELETE').update(venue_detail=VenueDetails.objects.get(id=venue_id),booking_detail=VenueBooking.objects.get(id=data['booking_id']))

            else:
                start_date_check = "2000-2-26 03:00:00"
                qry_check_already_booked_venue = list(VenueBooking.objects.filter(start_date__lte=data['date_to'],end_date__gte=data['date_from']).exclude(status='DELETE').values('id'))
                for var in qry_check_already_booked_venue:
                    check_for_venue = list(VenueBookingApproval.objects.filter(booking_detail=var['id']).exclude(status='DELETE').values('venue_detail'))
                    if len(check_for_venue)>0:
                        if check_for_venue[0]['venue_detail']==venue_id:
                            return_message = statusMessages.CUSTOM_MESSAGE('Booking Already Done')
                            return functions.RESPONSE(return_message,statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    
                qry=VenueBooking.objects.create(start_date=data['date_from'],end_date=data['date_to'],participants=data['participants'],purpose=data['purpose'],remark=data['remark'],session=Semtiming.objects.get(uid=session),added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))

                qry2=VenueBookingApproval.objects.create(venue_detail=VenueDetails.objects.get(id=venue_id),booking_detail=VenueBooking.objects.get(id=qry.id))

                data=statusMessages.CUSTOM_MESSAGE('SENT TO HOD.')

            return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def venue_booked_details(request):
    if checkpermission(request,[rolesCheck.ROLE_EMPLOYEE])== statusCodes.STATUS_SUCCESS:
        data=[]
        if requestMethod.GET_REQUEST(request):

            qry = list(VenueBookingApproval.objects.filter(approval_status='APPROVED',level=1).exclude(status='DELETE').exclude(booking_detail__status='DELETE').exclude(venue_detail__status='DELETE').exclude(booking_detail__in=VenueBookingApproval.objects.filter(level=2,approval_status='APPROVED').exclude(status='DELETE').exclude(booking_detail__status='DELETE').exclude(venue_detail__status='DELETE').values_list('booking_detail',flat=True)).values('booking_detail__participants','booking_detail__purpose','booking_detail__remark','booking_detail__added_by','booking_detail__added_by__name','booking_detail__added_by__desg__value','booking_detail__start_date','booking_detail__end_date','venue_detail__name','venue_detail__description','remark','approval_status','level','booking_detail__id','venue_detail__id','booking_detail__added_by__dept__value').order_by('-booking_detail__start_date'))
            qry2=list(VenueBookingApproval.objects.filter(approval_status='APPROVED',level=2).exclude(status='DELETE').exclude(booking_detail__status='DELETE').exclude(venue_detail__status='DELETE').values('booking_detail__participants','booking_detail__purpose','booking_detail__remark','booking_detail__added_by','booking_detail__added_by__name','booking_detail__added_by__desg__value','booking_detail__start_date','booking_detail__end_date','venue_detail__name','venue_detail__description','remark','approval_status','level','booking_detail__id','venue_detail__id','booking_detail__added_by__dept__value').order_by('-booking_detail__start_date'))
            data.extend(qry)
            data.extend(qry2)
            return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)









