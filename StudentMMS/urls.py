from django.conf.urls import url
from .views.mms_settings_views import student_marksheet,enter_ta_marks,bloomtaxonomy,Set_CO_details,co_po_mapping,create_question_paper,approve_question_paper,student_internal_marks,bonus_marks_rule
from .views.salil_views import AddQues,QuestionModerator,CoeCoordinator,CtMarksRule
from .views.vaibhav_views import ct_wise_subjects_marks,ct_wise_subjects_marks_faculty,ct_marks_report
from .views.salil_views1 import uveCoordinator,peo_mi_mapping,po_peo_mapping,mms_student_internal_co_report,survey_add_Question,survey_po_wise_Report,all_survey_po_wise_Report
from .views.vrinda_settings_views import mms_vision,Questionpaper_format,InternalExamSchedule,Attendance_Marks,ExtraBonus_Marks,Bonus_Marks_AddSubRule_Updated, Bonus_Marks_AddRule_Updated
from .views.astha_views1 import mms_student_co_report,mms_attainment_settings,enter_assi_quiz_marks,course_overall_attainment,get_course_overall_po_attainment,po_attainment_gap_report,co_po_target_report,po_peo_attainment_report,peo_mi_attainment_report,co_po_matrix
from .views.aktu_marks_script import aktu_script,kiet_script
from .views.harsh_views import *
from .views.external_views import create_form,submit_answer,get_form_filled_data,Add_session_hashcode
from .views.marks_analyser_views import external_marks_analyser,overall_marks_analyser,faculty_analyser
from .views.external_views import create_form,submit_answer,get_form_filled_data,Add_session_hashcode,create_internal_fac_survey,submit_internal_fac_survey
urlpatterns = [

	url(r'^bloomtaxonomy/$', bloomtaxonomy),
	url(r'^mms_vision/$', mms_vision),
	url(r'^Set_CO_details/$', Set_CO_details),
	url(r'^AddQues/$', AddQues),
	url(r'^co_po_mapping/$', co_po_mapping),
	url(r'^quespaper_format/$', Questionpaper_format),
	url(r'^create_question_paper/$', create_question_paper),
	url(r'^QuestionModerator/$', QuestionModerator),
	url(r'^approve_question_paper/$', approve_question_paper),
	url(r'^CoeCoordinator/$', CoeCoordinator),
	url(r'^student_internal_marks/$', student_internal_marks),
	url(r'^mms_exam_schedule_form/$', InternalExamSchedule),
	url(r'^mms_attendance_marks/$', Attendance_Marks),
	url(r'^CtMarksRule/$', CtMarksRule),
	url(r'^enter_ta_marks/$', enter_ta_marks),
	url(r'^ct_wise_subjects_marks/$', ct_wise_subjects_marks),
	url(r'^ct_wise_subjects_marks_faculty/$', ct_wise_subjects_marks_faculty),
	url(r'^bonus_marks_rule/$', bonus_marks_rule),
	url(r'^extrabonus/$', ExtraBonus_Marks),
	url(r'^ct_marks_report/$', ct_marks_report),
	url(r'^student_marksheet/$', student_marksheet),
	url(r'^uveCoordinator/$', uveCoordinator),
	url(r'^mms_student_co_report/$', mms_student_co_report),
	url(r'^mms_student_internal_co_report/$', mms_student_internal_co_report),
	url(r'^aktu_script/$', aktu_script),
	url(r'^po_peo_mapping/$', po_peo_mapping),
	url(r'^peo_mi_mapping/$', peo_mi_mapping),
	url(r'^kiet_script/$', kiet_script),
	url(r'^mms_attainment_settings/$', mms_attainment_settings),
	url(r'^enter_assi_quiz_marks/$', enter_assi_quiz_marks),
	url(r'^course_overall_attainment/$', course_overall_attainment),
	url(r'^survey_add_Question/$', survey_add_Question),
	url(r'^get_course_overall_po_attainment/$', get_course_overall_po_attainment),
	url(r'^survey_po_wise_Report/$', survey_po_wise_Report),
	url(r'^po_attainment_gap_report/$', po_attainment_gap_report),
	url(r'^co_po_target_report/$', co_po_target_report),
	url(r'^all_survey_po_wise_Report/$', all_survey_po_wise_Report),
	url(r'^po_peo_attainment_report/$', po_peo_attainment_report),
	url(r'^peo_mi_attainment_report/$', peo_mi_attainment_report),
	url(r'^co_po_matrix/$', co_po_matrix),
	url(r'^ct_marks_rule/$', new_CtMarksRule),
	url(r'^add_subrule/$', Bonus_Marks_AddSubRule_Updated),
	# url(r'^data_shift_script/$', data_shift_script),
	url(r'^add_bonus_rule/$', Bonus_Marks_AddRule_Updated),
	url(r'^create_external_form/$', create_form),
	url(r'^submit_answer_external_form/$', submit_answer),
	url(r'^get_form_filled_data/$',get_form_filled_data),
	url(r'^Add_session_hashcode/$',Add_session_hashcode),
	#####################analyser#########################
	url(r'^marks_analyser/$',overall_marks_analyser),
	url(r'^faculty_analyser/$',faculty_analyser),
	url(r'^external_marks_analyser',external_marks_analyser),
	##################internal-fac-survey###################
	url(r'^create_internal_fac_survey/$', create_internal_fac_survey),
	url(r'^submit_internal_fac_survey/$', submit_internal_fac_survey)



	


]
