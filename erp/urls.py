#
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
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import global_settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('login.urls')),
    url(r'^musterroll/', include('musterroll.urls')),
    url(r'^leave/', include('leave.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^attendance/', include('attendance.urls')),
    url(r'^grievance/', include('grievance.urls')),
    url(r'^Accounts/', include('Accounts.urls')),
    url(r'^StudentAccounts/', include('StudentAccounts.urls')),
    url(r'^StudentAcademics/', include('StudentAcademics.urls')),
    url(r'^StudentPortal/', include('StudentPortal.urls')),
    url(r'^StudentMMS/', include('StudentMMS.urls')),
    url(r'^StudentFeedback/', include('StudentFeedback.urls')),
    # url(r'^login/',include('login.urls')),
    url(r'^separation/', include('separation.urls')),
    url(r'^Redressal/', include('Redressal.urls')),
    url(r'^Ticketing/', include('Ticketing.urls')),
    url(r'^Registrar/', include('Registrar.urls')),
    url(r'^aar/', include('aar.urls')),
    url(r'^registrar/', include('Registrar.urls')),
    url(r'^website/', include('website.urls')),
    url(r'^StudentSMM/', include('StudentSMM.urls')),
    url(r'^Venue/', include('Venue.urls')),
    url(r'^StudentHostel/', include('StudentHostel.urls')),
    url(r'^Achievement/', include('Achievement.urls')),
    url(r'^AppraisalStaff/', include('AppraisalStaff.urls')),
    url(r'^LessonPlan/', include('LessonPlan.urls')),
    url(r'^AppraisalFaculty/', include('AppraisalFaculty.urls')),
    url(r'^DeptAchievements/', include('DeptAchievement.urls')),
    url(r'^Store_data/', include('Store_data.urls')),
    url(r'^Scripts/', include('Scripts.urls'))


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#+ static(global_settings.STATIC_URL, document_root=settings.STATIC_URL)
