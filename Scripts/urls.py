from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from .views.feedback_shift import *
from .views.StudentAcademics_shift import *
from .views.dropdown import *
from .views.StudentMMS import *
from Scripts.views.front_build import function_for_build
urlpatterns = [

    url(r'^frontendbuild/',function_for_build )
]
