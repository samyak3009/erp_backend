from django.conf.urls import url
#from views.mms_function_views import test,test2,test3

# from .views.mms_settings_views import student_marksheet,enter_ta_marks,bloomtaxonomy,Set_CO_details,co_po_mapping,create_question_paper,approve_question_paper,student_internal_marks,bonus_marks_rule,ct_marks_report
# from .views.salil_views import AddQues,QuestionModerator,CoeCoordinator,CtMarksRule
# from .views.vaibhav_views import ct_wise_subjects_marks,ct_wise_subjects_marks_faculty
from .views.vaibhav import *
from .views.astha_views import *
# from .views.smm_function_views import *
from .views.smm_settings_views import getComponents,StudentMentoring
# from .views.salil_views import *
from .views.smm_report_views import menteePerformanceCard, facultyCountReport, facultyCounsellingReport
# from .views.vrinda_settings_views import mms_vision,Questionpaper_format,InternalExamSchedule,Attendance_Marks,ExtraBonus_Marks

urlpatterns=[
	url(r'^StudentMentoring/$',StudentMentoring),
	url(r'^pending_approval_function/$',pending_approval_function),
	url(r'^indiscipline_act_approval_function/$',indiscipline_act_approval_function),
	url(r'^Disciplinary_Action/$',Disciplinary_Action),
	url(r'^getComponents/$',getComponents),
	url(r'^menteePerformanceCard/$',menteePerformanceCard),
	url(r'^facultyCountReport/$', facultyCountReport),
    url(r'^facultyCounsellingReport/$', facultyCounsellingReport),
]



