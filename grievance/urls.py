from django.conf.urls import url
from .views import grievance_type_rept,grievance_approval_hod,grievance_approval_hr,grievance_view,feedbck,insert_approval_hod,insert_approval_hr,consolidated_report_data_hod,consolidated_report_data_hr,consolidated_rept_field_data_hod,consolidated_rept_field_data_hr,CheckForHourly#,grievance_type_rept,field_data,grievance_higher_authority_view,grievance_status_change_view,grievance_status_change
urlpatterns=[
	
	url(r'^g_view/$',grievance_view),
	url(r'^g_formdata/$',grievance_type_rept),
	url(r'^g_app1/$',grievance_approval_hod),
	url(r'^g_app2/$',grievance_approval_hr),
	url(r'^g_feedback/$',feedbck),
	url(r'^g_insert_app1/$',insert_approval_hod),
	url(r'^g_insert_app2/$',insert_approval_hr),
	url(r'^g_cons_reptdata1/$',consolidated_report_data_hod),
	url(r'^g_cons_reptdata2/$',consolidated_report_data_hr),
	url(r'^reptdata1/$',consolidated_rept_field_data_hod),
	url(r'^reptdata2/$',consolidated_rept_field_data_hr),
	url(r'^CheckForHourly/$',CheckForHourly),
	
]