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
from .views import hod_wise_attendance,upload_attendance,dailyEmpsummary,check_compoff,last_three_month_att,attendance_script,employee_data,singleperson_attendance,all_employee_data

urlpatterns = [

    url(r'^all_employee_data/',all_employee_data),
    url(r'^employee/',employee_data),
    url(r'^att_data/$', last_three_month_att),
    url(r'^singlepersonatt/',singleperson_attendance),
    url(r'^empAttScript/',attendance_script),
    url(r'^check_compoff/',check_compoff),
    url(r'^stats/',dailyEmpsummary),
    url(r'^hod_wise_attendance/',hod_wise_attendance),
    url(r'^upload_attendance/',upload_attendance),

]
