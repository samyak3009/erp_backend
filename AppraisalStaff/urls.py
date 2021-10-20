"""erp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views.appraisal_staff_setting import appraisal_staff_question_setting
from .views.appraisal_staff_views import locking_unlocking_appraisal, get_components, emg_employee_end, reporting_form_all_band, a_employee_end, appraisal_consolidate_report
from .views.appraisal_staff_report import *
from .views import *

urlpatterns = [

    url(r'^LockingUnlockingAAR/$', locking_unlocking_appraisal),
    url(r'^get_components/$', get_components),
    url(r'^AppraisalQuestionSetting/$', appraisal_staff_question_setting),
    url(r'^SubmitAppraisalFormEMG/$', emg_employee_end),
    url(r'^SubmitAppraisalFormA/$', a_employee_end),
    ####### FOR ALL BAND REPORTING AND S-BAND ##############
    url(r'^AppraisalFormALLBAND/$', reporting_form_all_band),
    url(r'^AppraisalConsolidateReport/$', appraisal_consolidate_report),

]
