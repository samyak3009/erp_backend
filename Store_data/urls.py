from django.conf.urls import url
from .views.scripts import StoredAttendance, store_ctwise_marks, StoreCtWiseAttendance, store_bonus_rule_wise, store_total_subject_attendance,store_attendance_total
urlpatterns = [
    # url(r'^stored_attendance/$', StoredAttendance),
    # url(r'^store_ct_wise_attendance', StoreCtWiseAttendance),
    # url(r'^store_total_subject_attendance/', store_total_subject_attendance),
    # url(r'^store_attendance_total/', store_attendance_total),

    ################ STORE MARKS ###############
    url(r'^store_ctwise_marks/$', store_ctwise_marks),
    # url(r'^store_bonus_marks', store_bonus_rule_wise),
    ############################################
]
