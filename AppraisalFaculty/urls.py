from django.conf.urls import url
from .views.appraisal_faculty_views import *
from .views.appraisal_faculty_reports import *

urlpatterns = [
    url(r'^form_emp_end/$', form_emp_end),
    url(r'^reporting_level_form/$', reporting_level_form),
    url(r'^cv_raman_report/$', cv_raman_report),
    url(r'^faculty_hr_report/$', faculty_hr_report)

]
