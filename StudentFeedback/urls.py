from django.conf.urls import url
from StudentMMS.views.mms_function_views import test,test2,test3
from .views.feedback_settings_views import *
from .views.feedback_report_views import ViewInstituteAttributeReport,ViewStudentStatusConsolidate,ViewAttrbuteRemark,ViewAttrbuteRemark,AvgFeedback,ConsolidateReport,Feedback_Report_faculty,Feedback_Report_Faculty_Report
urlpatterns=[
	url(r'^settings_data/$',feedback_settings_data),
	url(r'^submit_settings/$',submit_settings),
	url(r'^student_feed_data/$',student_feedform_data),
	url(r'^submit_feedback/$',submit_feedback),
	url(r'^ViewPreviousAttrbute/$',ViewPreviousAttrbute),
	url(r'^ViewAttrbuteRemark/$',ViewAttrbuteRemark),
	url(r'^ViewStudentStatusConsolidate/$',ViewStudentStatusConsolidate),
	url(r'^ViewInstituteAttributeReport/$',ViewInstituteAttributeReport),
	url(r'^AttributeDelete/$',AttributeDelete),
	url(r'^AvgFeedback/$',AvgFeedback),
	url(r'^ConsolidateReport/$',ConsolidateReport),
	url(r'^GetDeptFaculty/$',GetDeptFaculty),
	url(r'^Feedback_Report_faculty/$',Feedback_Report_faculty),
	url(r'^Feedback_Report_Faculty_Report/$',Feedback_Report_Faculty_Report),
	url(r'^Feedback_Faculty/$',FeedbackFaculty),

]
