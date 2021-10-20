from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from login.views import checkpermission,generate_session_table_name
from django.db.models import Sum,F
import json
from Venue.constants_functions import requestType
from .venue_functions import *
from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from Registrar.models import *
from login.models import EmployeePrimdetail
from Venue.models import *
from musterroll.models import *
from login.models import EmployeePrimdetail

def venue_approve(request):
    emp_id=request.session['hash1']
    session=request.session['Session_id']
    if checkpermission(request,[rolesCheck.ROLE_APPROVAL]) == statusCodes.STATUS_SUCCESS:

        emp_details=list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept','desg'))
        # emp_id_hod = list(Roles.objects.filter(roles__value__contains="HOD").values_list('emp_id'))
        emp_list=list(Reporting.objects.filter(reporting_to=emp_details[0]['desg'],department=emp_details[0]['dept'],reporting_no=1).values_list('emp_id',flat=True))
        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET,'get_approve_requests')):
                data=list(VenueBookingApproval.objects.filter(level=1,approval_status='PENDING',booking_detail__added_by__in=emp_list,booking_detail__session=session).exclude(booking_detail__status='DELETE').exclude(status='DELETE').values('id','venue_detail__name','booking_detail__start_date','booking_detail__end_date','booking_detail__purpose','booking_detail__added_by__name','booking_detail__added_by__dept__value','booking_detail__added_by__emp_id','booking_detail__added_by__desg__value','booking_detail__remark','booking_detail__participants'))
                return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
            elif (requestType.custom_request_type(request.GET,'view_previous')):
                data=list(VenueBookingApproval.objects.filter(level=1,booking_detail__added_by__in=emp_list).exclude(booking_detail__status='DELETE').exclude(status='DELETE').exclude(approval_status='PENDING').values('id','venue_detail__name','booking_detail__start_date','booking_detail__end_date','booking_detail__purpose','approval_status','booking_detail__added_by__name','booking_detail__participants','booking_detail__remark','booking_detail__added_by__dept__value','booking_detail__added_by__emp_id','booking_detail__added_by__desg__value','remark'))
                return functions.RESPONSE(data,statusCodes.STATUS_SUCCESS)
            else:
                return functions.RESPONSE(statusMessages.MESSAGE_BAD_REQUEST,statusCodes.STATUS_BAD_REQUEST)
        elif (requestMethod.POST_REQUEST(request)):

            data=json.loads(request.body)
            id=data['id']
            remark=data['remark']
            status=data['status']
            qry = list(VenueBookingApproval.objects.filter(id=id).values('booking_detail','venue_detail'))
            VenueBookingApproval.objects.filter(id=id).update(status='DELETE')
            for q in qry:
                VenueBookingApproval.objects.create(approval_status=status,approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id),remark=remark,booking_detail=VenueBooking.objects.get(id=q['booking_detail']),venue_detail=VenueDetails.objects.get(id=q['venue_detail']))
            return functions.RESPONSE({'msg':status},statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)
