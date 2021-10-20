from django.conf.urls import url
from .views import *
from .astha import *
from .salil_views import *
from .dhruv import *
from .vrinda import *
from .vaibhav import *
from .script_views import SendPendingAttendance
from .AttendanceAnalyser import attendance_analyser
# 1 0 0 0 0 wget http://127.0.0.1/StudentAcademics/SendPendingAttendance

urlpatterns = [
	url(r'^fields/$',Student_Academics_dropdown),
	url(r'^fields_category/$',Student_Academics_dropdown),
	url(r'^add_category/$',Student_Academics_dropdown),
	url(r'^update_category/$',Student_Academics_dropdown),
	url(r'^delete_category/$',Student_Academics_dropdown),
	url(r'^getComponents/$',getComponents),
	url(r'^semester_commencement/$',semester_commencement),
	url(r'^att_settings/$',attendance_settings),
	url(r'^coordinator/$',assign_coordinator),
	url(r'^new_tt_slots/$',new_tt_slots),
	url(r'^tt_slots_approval/$',tt_slots_approval),
	url(r'^section_group/$',section_group),
	url(r'^subject_detail/$',subject_detail),
	url(r'^LockingUnlocking/$',LockingUnlocking),
	url(r'^time_table/$',time_table),
	url(r'^AcademicsCalendar/$',Academics_Calendar),
	url(r'^mark_class_attendance/$',mark_class_attendance),
	url(r'^mark_extra_attendance/$',mark_extra_attendance),
	url(r'^update_class_attendance/$',update_class_attendance),
	url(r'^AttendanceRegister/$',AttendanceRegister),
	url(r'^GroupAssign/$',GroupAssign),
	url(r'^ChangeClassRollNo/$',ChangeClassRollNo),
	url(r'^StudentNominalList/$',StudentNominalList),
	url(r'^DailyAttCountReport/$',DailyAttCountReport),
	url(r'^SemRegistration/$',SemRegistration),
	url(r'^StudentAttendanceRecord/$',StudentAttendanceRecord),
    ############ CHANGED ON 17/10/19 #######################
    url(r'^StudentAttendanceRecordUpdated/$', StudentAttendanceRecordUpdated),
    ### END #### CHANGED ON 17/10/19 #######################
	url(r'^CollegeAttendanceRecord/$',CollegeAttendanceRecord),
	url(r'^AssignedCoordinator/$',AssignedCoordinator),
	url(r'^RegistrationCountReport/$',RegistrationCountReport),
	url(r'^kaksha_data/$',kaksha_data),
	url(r'^EmployeeAdvanceReport/$',EmployeeAdvanceReport),
	url(r'^approve_extra_attendance/$',approve_extra_attendance),
	#url(r'^show_matrix_tt_officials/$',show_matrix_tt_officials),
	url(r'^show_matrix_tt_officials/$',show_matrix_tt_officials),
	url(r'^view_emp_details/$',view_emp_details),
	url(r'^check_student_remark/$',check_student_remark),
	url(r'^student_prev_status/$',student_prev_status),
	url(r'^total_lecture/$',total_lecture),
	url(r'^resolve_remark/$',resolve_remark),
	url(r'^SemSubjectRepot/$',SemSubjectRepot),
	url(r'^Student_lec_wise/$',Student_lec_wise),
	url(r'^Student_day_and_lec_wise/$',Student_day_and_lec_wise),
	url(r'^SecGroupReport/$',SecGroupReport),
	url(r'^StudentAttendanceRegister/$',StudentAttendanceRegister),
	url(r'^view_faculty_tt_matrix/$',view_faculty_tt_matrix),
	url(r'^Department_load/$',Department_load),
	url(r'^Department_list/$',Department_list),
	url(r'^Department_load_without_time/$',Department_load_without_time),
	url(r'^printDeclaration/$',printDeclaration),
	url(r'^student_acad_remarks/$',student_acad_remarks),
	url(r'^ModifiedAttendanceRegister/$',ModifiedAttendanceRegister),
	url(r'^get_students_hobby_club_details/$',get_students_hobby_club_details),
	url(r'^get_students_internship_details/$', get_students_internship_details),
	url(r'^att_analyser/$', attendance_analyser),
	# SCRIPTS
	url(r'^SendPendingAttendance/$',SendPendingAttendance),
	url(r'^emp_details/$',emp_details),
	url(r'^set_hobby_clubs/$',set_hobby_clubs),
	url(r'^get_hobby_club_student_details/$',get_hobby_club_student_details),
]

