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
from .views import *
from .dashboard import get_birthday

urlpatterns = [
	url(r'^print_fee_rec/$',printFeeReceipts),
	url(r'^left_panel/$',left_panel),
    url(r'^getComponents/$',getComponents),
    url(r'^student_registration/$',student_registration),
    url(r'^printDeclaration/$',printDeclaration),
    url(r'^update_insurance_detail/$',updateInsuranceDetails),
    url(r'^small_change/$',small_change),
    url(r'^StudentBankDetails/$',StudentBankDetailsChange),
    url(r'^academic_calendar/$',academic_calendar),
    url(r'^student_marks/$',student_marks),
    url(r'^Activities_Student_Portal/$',Activities_Student_Portal),
    url(r'^MentorCardOnPortal/$',MentorCardOnPortal),
    url(r'^HostelAppForm/$',HostelAppForm),
    url(r'^RoomPartnerChoice/$',RoomPartnerChoice),
    url(r'^SurveyFillFeedback/$',SurveyFillFeedback),
    url(r'^HostelFeeLetter_Portal/$',HostelFeeLetter_Portal),
    url(r'^PrintHostelFeeLetter/$',PrintHostelFeeLetter),
    url(r'^PlacementPolicy/$',PlacementPolicy_Form),   
    # (?# url(r'^AcademicFeeLetter_Portal/$',AcademicFeeLetter_Portal),)
    url(r'^print_tution_certificate/$',print_tution_certificate),
    url(r'^PrintAcademicFeeLetter/$',PrintAcademicFeeLetter),
    url(r'^AcademicFeeLetter_Portal/$',AcademicFeeLetter_Portal),
    url(r'^LessonPlanOnPortal/$',LessonPlanOnPortal),
    url(r'^message/$',Message),
    url(r'^Student_Directory/$',Student_Directory),
    url(r'^admincheck/$',isadmin),
    url(r'^is_alloted/$',is_alloted),
    url(r'^get_birthday/$',get_birthday),   
]
