from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from .views1 import reporting_previous_approval,separation_prev_status,manual_separation_HR,employee_view,separation_approval_admin,long_leave_type,separation_approval_1stReporting,noduesApproval,retrieve,hr_separation_previous
from .views.separation_views import separation_reporting , apply_separation,exit_paper,response,add_reporting,noduesApproval,finalHRrole,accountRole
urlpatterns = [

# 	url(r'^no_dues/$',employee_view),
# ################ HR Separation ##############################
# 	url(r'^separation_employee/$',separation_approval_admin),
# 	url(r'^manual_separation/$',manual_separation_HR),
# ################## HOD Separation ########################################
# 	url(r'^separation_employee_hod/$',separation_approval_1stReporting),
# ############### Separation ###################
# 	url(r'^long_leave/$',long_leave_type),
# 	url(r'^nodues_approve/$',noduesApproval),
# ############## Retrieval Employee #################
# 	url(r'^retrieve/$',retrieve),
# 	url(r'^separation_prev_status/$',separation_prev_status),
# 	url(r'^reporting_previous_approval/$',reporting_previous_approval),
# 	url(r'^hr_separation_previous/$',hr_separation_previous),
	url(r'^apply_separation/$',apply_separation),
	url(r'^separation_reporting/$',separation_reporting),
	url(r'^exit_paper/$',exit_paper),
	url(r'^response/$',response),
	url(r'^add_reporting/$',add_reporting),
	url(r'^noduesApproval/$',noduesApproval),
	url(r'^finalHRrole/$',finalHRrole),
	url(r'^accountRole/$',accountRole)

]

