from django.conf.urls import url
from .views.lesson_plan_views import *
from .views.lesson_plan_scripts import *
from .views.lesson_plan_functions import *
urlpatterns = [

    url(r'^ProposeLessonPlan/$',propose_lesson_plan),
    url(r'^lesson_plan_hod_approval/$',lesson_plan_hod_approval),
    url(r'^complete_lesson_plan_dropdown/$',complete_lesson_plan_dropdown),   
    url(r'^completed_lesson_plan_hod_approval/$',completed_lesson_plan_hod_approval), 
    url(r'^lesson_plan_lnowise_report/$',lesson_plan_lnowise_report), 
    

    
]
