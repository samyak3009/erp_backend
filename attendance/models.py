from django.db import models
from login.models import EmployeeDropdown,EmployeePrimdetail
from musterroll.models import Shifts
# Create your models here.

class Attendance2(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='Emp_Id', related_name='employee_id_attendance2' , max_length=20, on_delete=models.SET_NULL,null=True)
    status = models.CharField(db_column='Status', max_length=45)  # Field name made lowercase.
    date = models.DateField()
    intime = models.TimeField()
    outtime = models.TimeField()
    late = models.TimeField()
    etime = models.TimeField()
    extra = models.TimeField()
    colstatus = models.CharField(max_length=50)
    work = models.TimeField()
    is_compoff=models.IntegerField(default=0)
    remark=models.TextField(blank=True,null=True)
    shift_id = models.ForeignKey(Shifts,db_column='shift', related_name='shift_id_attendance2' , max_length=20, on_delete=models.SET_NULL,null=True)

    class Meta:
        db_table = 'attendance2'
        unique_together = (('Emp_Id', 'date'))


class machinerecords(models.Model):
    Emp_Id = models.ForeignKey(EmployeePrimdetail,db_column='EmpCode', related_name='employee_id_machinerecord' , max_length=20, on_delete=models.SET_NULL,null=True)
    date = models.DateField(db_column='date', blank=True, null=True )
    time=models.TimeField(db_column='time', blank=True, null=True)
    timestamp=models.DateTimeField(db_column='timestamp', blank=True, null=True)
    # Field name made lowercase.

    class Meta:
        db_table = 'machinerecords'
        unique_together = (('Emp_Id', 'date','time'))
