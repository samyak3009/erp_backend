from django.conf.urls import url
from .views import *
urlpatterns=[
	url(r'^validate/$',my_view),
	url(r'^login/$',std_login),
	url(r'^logout/$',logout_view),
	url(r'^changepassword/$',change_password),
	url(r'^resetdata/$',resetdata),
	url(r'^resetpassword/$',resetpassword),

	#STUDENT RESET#
	url(r'^student_resetdata/$',student_resetdata),
	url(r'^student_resetpassword/$',student_resetpassword),
	#STUDENT RESET END#

	url(r'^send_email/$',send_email),
	url(r'^mercedes_report/$',mercedes_report),
	url(r'^mer_send_email/$',mer_send_email),
	url(r'^acc_send_sms/$',acc_send_sms),
	url(r'^student_login/$',stu_login),

	############ FORGOT PASSWORD ###############
	url(r'^forgot_new/$',forgot_password_new),
	url(r'^checking_new/$',checking_otp_new),
	url(r'^change_pass_otp_new/$',change_pass_otp_new),
	url(r'^student_change_password/$',stu_change_password),
	url(r'^lib_sms/$',lib_sms),
	url(r'^send_innotech/$',send_innotech),
	################################## FCM ######################################
	url(r'^fcm_insert/$',fcm_insert),
	url(r'^fcm_remove/$',fcm_remove),
	###############################################################################
	url(r'^ccell_data/$',ccell_data),

	################################## SESSION CHANGE ######################################
	url(r'^change_session/$',change_session),
	url(r'^registration_api/$',registration_api),

	url(r'^send_bday_email/$',send_bday_email),
	url(r'^send_summary_mail/$',send_summary_mail),

]
