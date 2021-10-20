# from django.urls import url
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import UploadDataSettingView,UploadDataView,getDropdownSetting, TaskUpdateView ,RowDataSetDetails,ViewPreviousView,Creategroup,CreateSubgroup,CreateTemplate,SendNotificationView, pause_resume_job_task
# LoginView, LogoutView, 
urlpatterns = [
	# url('login', LoginView.as_view()),
	# url('logout/', LogoutView.as_view()),
	url('UploadData/', UploadDataView.as_view()),
	url('UploadSetting/', UploadDataSettingView.as_view()),
	# url('UploadSetting/', UploadDataSettingView.as_view()),
	url('getDropdownSetting/', getDropdownSetting.as_view()),
	url('ViewPrevious/', ViewPreviousView.as_view()),
	url('RowDataSetDetails/', RowDataSetDetails.as_view()),
	url('TaskUpdateView/', TaskUpdateView.as_view()),
	url('Creategroup/', Creategroup.as_view()),
	url('CreateSubgroup/', CreateSubgroup.as_view()),
	url('CreateTemplate/', CreateTemplate.as_view()),
	url('SendNotification/', SendNotificationView.as_view()),
	url(r'^pause_resume_task/$', pause_resume_job_task),
]