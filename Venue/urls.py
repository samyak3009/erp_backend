from django.conf.urls import url
from .views.shobhit_views import *
from .views.priya_views import *
from .views.venue_views import *
urlpatterns=[
    url(r'^book_venue/$',book_venue),
    url(r'^venue_booked_details/$', venue_booked_details),
    url(r'^admin_approval/$',admin_approval),
    url(r'^venue_approve/$',venue_approve),
    url(r'^venue_details/$',Venue_Details)
]

