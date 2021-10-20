from aar.dept_achievemrnt import web_rnd_tabledata,DirReport,approval,Schools,website_aar,website_single,hobbyclub,IndustrialVisit,GuestLecture,EventsOrganized,Achievements,index,R_Conference,R_Guidence,R_journal,Book,Update_Conferance,Update_Journal,Update_Book,Update_Guidence,Lectures,Training,Projects,Patent_data,Update_Patent,Update_Lectures,Update_Training,Update_Projects,index_update,mou,aar_report,deanaar_report,report,director_report,director_department_report,delete_aar_employee,aar_dept_report,aar_emp_report,getComponents,emp_detail,locking_unlocking,aar_report_test,aar_hod_dept_report,update_departmental_aar,aar_approved_report,rnd_approval,aar_increment_settings,staff_shod,staff_sdir,staff_a,staff_ahod,staff_adir,staff_emg,staff_emg_submit,staff_emg_hod_dropdown,staff_emg_details,staff_emg_hod_submit,staff_emg_dir_dropdown,staff_emg_dir_details,staff_emg_dir_submit,staff_annual_increment_summary,staff_a_report,staff_ahod_report,staff_adir_report,staff_shod_report,staff_sdir_report,staff_emg_report,staff_emghod_report,staff_emgdir_report,aar_dir_advance_report,aar_dir_advance_report_data,aar_emp_end_report,rnd_update,rnd_reject,rnd_view,rnd_tabledata
# from aar.views import web_rnd_tabledata,DirReport,approval,Schools,website_aar,website_single,hobbyclub,IndustrialVisit,GuestLecture,EventsOrganized,Achievements,index,R_Conference,R_Guidence,R_journal,Book,Update_Conferance,Update_Journal,Update_Book,Update_Guidence,Lectures,Training,Projects,Patent_data,Update_Patent,Update_Lectures,Update_Training,Update_Projects,index_update,mou,aar_report,deanaar_report,report,director_report,director_department_report,delete_aar_employee,aar_dept_report,aar_emp_report,getComponents,emp_detail,locking_unlocking,aar_report_test,aar_hod_dept_report,update_departmental_aar,aar_approved_report,rnd_approval,aar_increment_settings,staff_shod,staff_sdir,staff_a,staff_ahod,staff_adir,staff_emg,staff_emg_submit,staff_emg_hod_dropdown,staff_emg_details,staff_emg_hod_submit,staff_emg_dir_dropdown,staff_emg_dir_details,staff_emg_dir_submit,staff_annual_increment_summary,staff_a_report,staff_ahod_report,staff_adir_report,staff_shod_report,staff_sdir_report,staff_emg_report,staff_emghod_report,staff_emgdir_report,aar_dir_advance_report,aar_dir_advance_report_data,aar_emp_end_report,rnd_update,rnd_reject,rnd_view,rnd_tabledata
from aar.views_faculty import form_data,insert_data,fc_app_advance_report,recommend
from .views.dept_ach_views import GuestLecture
from django.conf.urls import url
# from .views.dept_ach_views import IndustrialVisit
from .views.dept_ach_views import MouSignedFunction, IndustrialVisit, StudentAchievement

from .views.dept_ach_views import MouSignedFunction, IndustrialVisit,DepartmentAchievement,SummerWinter,HobbyClub,Events_organised
from .views.dept_ach_reports import Department_Achievement_Report
from .views.reports import Dept_consolidated_report


urlpatterns = [
    url(r'^MouSigned/$', MouSignedFunction),
    url(r'^industrial_visit/$', IndustrialVisit),
    url(r'^student_achievement/$', StudentAchievement),
    url(r'^GuestLecture/$',GuestLecture),
    url(r'^DepartmentAchievement/$', DepartmentAchievement),
    url(r'^HobbyClub/$', HobbyClub),
	url(r'^summerwinterschool/$',SummerWinter),
	url(r'^eventsorganized/$',Events_organised),
	url(r'^report_data/$',Department_Achievement_Report), 
	url(r'^Graphical_report/$',Dept_consolidated_report),    

]
