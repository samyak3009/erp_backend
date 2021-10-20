from django.db import models
# Create your models here.
from StudentAcademics.models.models import *
from StudentAcademics.models.models_2021e import *
from Registrar.models import *
from login.models import EmployeePrimdetail
from StudentPortal.models import StudentActivities_2021e


class Incident_2021e(models.Model):
    date_of_incident = models.DateField()
    description = models.TextField()
    incident_document = models.TextField(default='NULL')
    status = models.CharField(max_length=20, default='INSERT')
    # type_of_incident=models.ForxeignKey(StudentAcademicsDropdown,related_name='type_of_councelling_2021e',null=True,on_delete=models.SET_NULL)#"ACADEMIC" IN CASE OF MENTOR FILLED INCIDENT /"HOSTEL" IN CASE OF RECTOR FILLED INCIDENT
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_Incident_2021e', null=True, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SMM_Incident_2021e'
        # managed = True


class IncidentReporting_2021e(models.Model):
    incident = models.ForeignKey(Incident_2021e, related_name='incidentReporting_incident_2021e', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='incidentReporting_uniqid_2021e', null=True, on_delete=models.SET_NULL)
    action = models.TextField(default='NULL')
    comm_to_parent = models.TextField(default='NULL')
    status = models.CharField(max_length=20, default='INSERT')
    student_document = models.TextField(default='NULL')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_IncidentReporting_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SMM_IncidentReporting_2021e'
        managed = True


class IncidentApproval_2021e(models.Model):
    incident_detail = models.ForeignKey(IncidentReporting_2021e, related_name='incidentApproval_incident_2021e', null=True, on_delete=models.SET_NULL)
    level = models.IntegerField(default=1)
    remark = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='INSERT')
    appoval_status = models.CharField(max_length=20, default='PENDING')
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_IncidentApproval_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SMM_IncidentApproval_2021e'
        managed = True


class CouncellingDetail_2021e(models.Model):
    date_of_councelling = models.DateField()
    type_of_councelling = models.ForeignKey(StudentAcademicsDropdown, related_name='type_of_councelling_2021e', null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021e, related_name='councellingDetail_uniqid_2021e', null=True, on_delete=models.SET_NULL)
    student_document = models.TextField()
    remark = models.TextField()
    status = models.CharField(max_length=20, default='INSERT')
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_CouncellingDetail_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SMM_CouncellingDetail_2021e'
        managed = True


class CouncellingApproval_2021e(models.Model):
    councelling_detail = models.ForeignKey(CouncellingDetail_2021e, related_name='councellingApproval_incident_2021e', null=True, on_delete=models.SET_NULL)
    level = models.IntegerField(default=1)
    remark = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='INSERT')
    appoval_status = models.CharField(max_length=20, default='PENDING')
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_CouncellingApproval_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SMM_CouncellingApproval_2021e'
        managed = True


class ActivitiesApproval_2021e(models.Model):
    Activities_detail = models.ForeignKey(StudentActivities_2021e, related_name='StudentActivities_activity_2021e', null=True, on_delete=models.SET_NULL)
    level = models.IntegerField(default=1)
    remark = models.TextField()
    status = models.CharField(max_length=20, default='INSERT')
    appoval_status = models.CharField(max_length=20, default='PENDING')
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name='added_by_StudentActivities_2021e', null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SMM_StudentActivitiesApproval_2021e'
        managed = True
