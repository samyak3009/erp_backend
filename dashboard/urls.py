from django.conf.urls import url
from .views import AcademicCalendar,left_panel,left_panel1,getModules,view_profile,TODO_List,attendancesummary,lasttenattendance,birthday_name,notice_all,image_path,upload_image,edit_profile,cctv,dashboard
urlpatterns=[
	url(r'^left_panel/$',left_panel),
	url(r'^left_panel1/$',left_panel1),
	url(r'^getModules/$',getModules),
	url(r'^view_profile/$',view_profile),
	url(r'^attsummary/$',attendancesummary),
	url(r'^lasttenattendance/$',lasttenattendance),
	url(r'^birthday_value/$',birthday_name),
	url(r'^todo_view/$',TODO_List),
	url(r'^todos/$',TODO_List),
	url(r'^todo_edit/$',TODO_List),
	url(r'^todo_delete/$',TODO_List),
	url(r'^notice/$',notice_all),
	url(r'^imagepath/$',image_path),
	url(r'^upload/$',upload_image),
	url(r'^edit_profile/$',edit_profile),
	url(r'^AcademicCalendar/$',AcademicCalendar),
	url(r'^cctv/$',cctv),
	url(r'^dashboard/$',dashboard),
	

]