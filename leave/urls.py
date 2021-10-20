"""hr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

#from .views import add_update_dropdown,field_add,field_update,field_delete,field_update_view,test_view,field_add,Add_Holiday_Type,Add_Holiday
#from leave.views import update_view_id,Add_Holiday,Add_Holiday_Type,Delete_Holiday,View_Table,add_leave,leave_data,club_leave,club_previous_leave,sandwich_leave,Leave_Quota_Table,Leave_Insert,onload_values,Seperation_Table_View,Seperation_Change_status,change_status,leaves,CompOffLeaves,InsertCompOff,AllNormalLeaveTyes,NormalLeaveInsert,od_leave_data,od_delete_data,ViewPrevious,show_leavetype,leave_days,update_type,delete_type,onload_category,upload_category,delete_club_type,sandwich_previous_leave,delete_sandwich_type,previous_leave_quota,delete_quota_type,onload_values,GetSubCatFromCat,OdLeaveInsert,short_leave_insert,CheckForHourly,Leave_Approval,primaryAppproveLeave,GetLeaveCodeFromLeaveId,OdLeaveCheckForUpload,CancelLeave,view_leave,view_leave_status,ExtractDepartment,ExtractHolidays

from leave.views import view_previous_arrear_leave, od_leave, lock_monthly_report, leaveLapsescript, get_leaves_remaining, allstatus, singleleaveviewreport, view_leave, view_all_leave_status, Leave_Approval, leaveCreditscript, mannualLeaveremaningupdate, mannualLeaveremaning, delete_od_upload, cancel_leave, previous_od_upload, view_previous_leave, mark_compoff_employee, mark_od_leave_employee, mark_normal_leave_employee, Extract_Leaves_Genderwise, od_upload_or_not, mark_compoff_admin, comp_off_data_admin, mark_od_leave_admin, mark_normal_leave_admin, delete_quota_type, Leave_Insert, Leave_Quota_Table, delete_type, update_type, leave_days, Club_Get_Leave, Club_Leave, monthholiday, quota_leave_detail, Add_Holiday, ExtractDepartment, ExtractHolidays, Add_Holiday_Type, Delete_Holiday, View_Table, monthlydeptsummary, singleleaveviewreport, show_leavetype, add_leave, LeaveCountReport, faculty_working_days_report


urlpatterns = [
    url(r'^add_holiday/$', Add_Holiday),
    url(r'^get_dept/$', ExtractDepartment),
    url(r'^get_holiday/$', ExtractHolidays),
    url(r'^add_holiday_type/$', Add_Holiday_Type),
    url(r'^delete_holiday/$', Delete_Holiday),
    url(r'^view/$', View_Table),
    url(r'^add_leave/$', add_leave),
    url(r'update_type/$', update_type),
    url(r'^mannualLeaveremaning/$', mannualLeaveremaning),
    url(r'^mannualLeaveremaningupdate/$', mannualLeaveremaningupdate),
    url(r'autoleavecredit/$', leaveLapsescript),

    url(r'delete_type/$', delete_type),
    url(r'^leave_data/$', Club_Get_Leave),
    url(r'^leave_club/$', Club_Get_Leave),
    url(r'^club_leave/$', Club_Leave),
    url(r'^delete_club/$', Club_Leave),
    url(r'^leave_quota_table/$', Leave_Quota_Table),
    url(r'^leave_insert/$', Leave_Insert),
    url(r'leave_show/$', show_leavetype),
    url(r'genderwise_leaves/$', Extract_Leaves_Genderwise),

    url(r'mark_normal_leave_admin/$', mark_normal_leave_admin),
    url(r'mark_od_leave_admin/$', mark_od_leave_admin),
    url(r'mark_compoff_leave_admin/$', mark_compoff_admin),
    url(r'compoff_data/$', comp_off_data_admin),
    url(r'normal_leave_employee_insert/$', mark_normal_leave_employee),
    url(r'od_leave_employee_insert/$', mark_od_leave_employee),
    url(r'comp_off_employee_insert/$', mark_compoff_employee),
    url(r'od_upload_or_not/$', od_upload_or_not),
    url(r'monthlyreport/$', monthlydeptsummary),
    url(r'view_previous_leave/$', view_previous_leave),
    url(r'view_previous_arrear_leave/$', view_previous_arrear_leave),

    url(r'previous_od/$', previous_od_upload),
    url(r'delete_od/$', delete_od_upload),
    url(r'^view_leave/$', view_leave),
    url(r'singleleaveview/$', singleleaveviewreport),
    url(r'^all_status/$', allstatus),
    url(r'^leaveapproval/$', Leave_Approval),
    url(r'^get_leaves_remaining/$', get_leaves_remaining),
    url(r'^LeaveCountReport/$', LeaveCountReport),

    url(r'OD/$', od_leave),
    url(r'days_leave/$', leave_days),
    url(r'view_all_leave_status/$', view_all_leave_status),
    url(r'singleleaveview/$', singleleaveviewreport),

    url(r'leave_quota/$', quota_leave_detail),
    url(r'^delete_quota/$', delete_quota_type),
    url(r'^cancel_leave/$', cancel_leave),
    url(r'^lock_monthly_report/$', lock_monthly_report),
    url(r'^faculty_working_days_report/$', faculty_working_days_report),


]
