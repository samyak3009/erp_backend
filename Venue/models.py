from django.db import models
# Create your models here.
from StudentAcademics.models import *
from Registrar.models import *
from login.models import EmployeePrimdetail
from StudentPortal.models import StudentActivities_1819e
import datetime
from datetime import date, timedelta

class VenueDetails(models.Model):
    name = models.TextField(null=True,default=None)
    description = models.TextField(null=True,default=None)
    eligible_occupancy = models.IntegerField(default=0)
    booking_limit = models.IntegerField(default=0)
    venue_image = models.TextField(default='NULL')
    status = models.CharField(max_length=20,default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail,related_name='VBM_VenueDetails_added_by',null=True,on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'VBM_VenueDetails'
        managed = True

class VenueBooking(models.Model):
    start_date = models.DateTimeField(default=datetime.datetime.now())#Store date with time
    end_date = models.DateTimeField(default=datetime.datetime.now())#Store date with time
    participants = models.IntegerField(default=0)
    purpose = models.TextField(default='NULL')
    remark=models.TextField(blank=True,null=True)
    session = models.ForeignKey(Semtiming,related_name='EventDetail_session',null=True,on_delete=models.SET_NULL)
    status = models.CharField(max_length=20,default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail,related_name='VBM_EventDetail_added_by',null=True,on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'VBM_VenueBooking'
        managed = True

class VenueBookingApproval(models.Model):
    venue_detail=models.ForeignKey(VenueDetails,related_name='VBM_VenueBooking_venue_detail',null=True,on_delete=models.SET_NULL)
    booking_detail=models.ForeignKey(VenueBooking,related_name='VBM_VenueBooking_booking_detail',null=True,on_delete=models.SET_NULL)
    level=models.IntegerField(default=1)
    remark=models.TextField(blank=True,null=True)
    status=models.CharField(max_length=20,default='INSERT')
    approval_status=models.CharField(max_length=20,default='PENDING')
    approved_by=models.ForeignKey(EmployeePrimdetail,related_name='VBM_VenueBooking_approved_by',null=True,on_delete=models.SET_NULL)
    time_stamp=models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'VBM_VenueBookingApproval'
        managed = True
