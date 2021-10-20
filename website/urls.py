from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from .views import Infra_add,payment_complete,insert_mercedes,Links,Link_add,Industry_add,Achieve_add,Labs_add,Hobby_add,dept_first_click,dept_name,faculty_name,vision_mission,peos,infrastructure,hodspeak,Labs,HobbyClubs,Industrial,Accordance,Topper,Achievements,Homepage,Topper_dept,Anouncement_add,Events_add,employee_image

urlpatterns = [
    url(r'^dept_click/$', dept_first_click, name='dept_first_click'),
    url(r'^dept/$', dept_name, name='dept_name'),
    url(r'^faculty/$', faculty_name, name='faculty_name'),
    url(r'^vision_detail/$', vision_mission, name='vision_mission'),
    url(r'^peo_detail/$', peos, name='peos'),
    url(r'^infrastructure_detail/$', infrastructure, name='infrastructure'),
    url(r'^hodspeak_detail/$', hodspeak, name='hodspeak'),
    url(r'^labs_detail/$', Labs, name='Labs'),
    url(r'^hobby_clubs_detail/$', HobbyClubs, name='HobbyClubs'),
    url(r'^industrial_detail/$', Industrial, name='Industrial'),
    url(r'^accordance_detail/$', Accordance, name='Accordance'),
    url(r'^achievments_detail/$', Achievements, name='Achievements'),
    url(r'^homepage_detail/$', Homepage, name='Homepage'),
    url(r'^topper/$',Topper, name='Topper'),
    url(r'^topper_dept/$', Topper_dept, name='Topper_dept'),
    url(r'^anouncements_add/$', Anouncement_add, name='Anouncement_add'),
    url(r'^events_add/$', Events_add, name='Events_add'),
    url(r'^industry_add/$', Industry_add, name='Industry_add'),
    url(r'^achieve_add/$', Achieve_add, name='Achieve_add'),
    url(r'^labs_add/$', Labs_add, name='Labs_add'),
    url(r'^hobby_add/$', Hobby_add, name='Hobby_add'),
    url(r'^image/$', employee_image, name='employee_image'),
    url(r'^link_add/$', Link_add, name='Link_add'),
    url(r'^Links/$', Links, name='Links'),
    url(r'^insert_mercedes/$', insert_mercedes),
    url(r'^payment_complete/$',payment_complete),
    url(r'^Infra_add/$',Infra_add, name='Infra_add'),
    # url(r'^chaneDate/$',chaneDate),
]





