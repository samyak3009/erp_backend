from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from .views import *
urlpatterns = [

    url(r'^fields/$', Student_dropdown),
    url(r'^fields_category/$', Student_dropdown),
    url(r'^add_category/$', Student_dropdown),
    url(r'^update_category/$', Student_dropdown),
    url(r'^delete_category/$', Student_dropdown),
    url(r'^get_values/$', course_setting),
    url(r'^insert_course_detail/$', course_setting_insert),
    url(r'^get_eligible_values/$', admission_eligiblity),
    url(r'^insert_admission_eligible/$', admission_eligiblity_insert),
    url(r'^add_student/$', add_student),
    url(r'^add_student_insert/$', add_student_insert),
    url(r'^get_student/$', get_student),
    url(r'^onchange_fields/$', onchange_fields),
    url(r'^getComponents/$', getComponents),
    url(r'^pre_student/$', pre_student),
    url(r'^update_student/$', update_student),
    url(r'^insert_univ_roll/$', insert_roll),
    url(r'^promote_student/$', promote_student),
    url(r'^section/$', section),
    url(r'^student_details/$', student_details),
    url(r'^registrar_summary/$', registrar_summary),
    url(r'^shift_student/$', shift_student),
    url(r'^insert_roll/$', insert_roll),
    url(r'^print_student_form/$', print_student_form),
    url(r'^placement_policy_report/$', placement_policy_report),
    url(r'^delete_student/$', delete_student),
    url(r'^faculty_report/$', faculty_report),
    url(r'^faculty_univ_marks_report/$', faculty_univ_marks_report),
    url(r'^branch_change/$', branch_change),
    url(r'^student_details_for_lib_cards/$', student_details_for_lib_cards),
    url(r'^getPincode/$', getPincode),
    url(r'^digital_id/$',digital_id),
    url(r'^digital_id_employee/$',digital_id_employee),
	url(r'^digital_id_hostel/$',digital_id_hostel),
]
