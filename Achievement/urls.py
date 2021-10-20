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
from .views.achievement_function import *
from .views.achievement_setting import *
from .views.achievement_views import Books,Conference,Patent,Design,Activity,LecturesTalks,Guidance,Journal,TrainingDevelopment,ProjectsConsultancy,AchApproval,consolidated_dropdown_data
from .views.achievement_scripts import ScriptsBooks,ScriptsConference,ScriptsGuidance,ScriptsJournal,ScriptsLecturesTalks,ScriptsPatent,ScriptsTraining,ScriptsProjects
from .views.achievement_report import EmployeeReport,RND_Report
from .views import *

urlpatterns = [
	url(r'^getComponents/$',getComponents),
	url(r'^Books/$',Books),
	url(r'^Conference/$',Conference),
	url(r'^Guidance/$',Guidance),
	url(r'^Journal/$',Journal),
	url(r'^Patent/$',Patent),
	url(r'^LecturesTalks/$',LecturesTalks),
	url(r'^TrainingDevelopment/$',TrainingDevelopment),
	url(r'^ProjectsConsultancy/$',ProjectsConsultancy),
	url(r'^Design/$',Design),
	url(r'^Activity/$',Activity),
	
    ############### SCRIPTS ##################
    url(r'^ScriptsBooks/$',ScriptsBooks),
	url(r'^ScriptsConference/$',ScriptsConference),
	url(r'^ScriptsGuidance/$',ScriptsGuidance),
	url(r'^ScriptsJournal/$',ScriptsJournal),
	url(r'^ScriptsLecturesTalks/$',ScriptsLecturesTalks),
	url(r'^ScriptsPatent/$',ScriptsPatent),
	url(r'^ScriptsTraining/$',ScriptsTraining),
	url(r'^ScriptsProjects/$',ScriptsProjects),
    ##########################################

    
	url(r'^AchApproval/$',AchApproval),
	url(r'^consolidated_dropdown_data/$',consolidated_dropdown_data),

	####################################
	url(r'^EmployeeReport/$',EmployeeReport),
	url(r'^RND_Report/$',RND_Report),
	url(r'^AchievementDropdowns/$',AchievementDropdowns)
    # url(r'^url/$',function_name),
]
