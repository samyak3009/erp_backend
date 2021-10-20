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

urlpatterns = [
	url(r'^fields/$',Student_Accounts_dropdown),
	url(r'^fields_category/$',Student_Accounts_dropdown),
	url(r'^add_category/$',Student_Accounts_dropdown),
	url(r'^update_category/$',Student_Accounts_dropdown),
	url(r'^delete_category/$',Student_Accounts_dropdown),

	url(r'^getComponents/$',getComponents),
	
	url(r'^penalty_settings/$',penalty_settings),
	#url(r'^write_pdf_view/$',write_pdf_view),
	#url(r'^fee_initial_settings/$',fee_initial_settings),
	url(r'^fee_settings/$',fee_settings),
	url(r'^submit_fee/$',submit_fee),
	url(r'^due_fee_pay/$',due_fee_pay),
	url(r'^refund_pay/$',refund_pay),
	url(r'^update_fee/$',submit_fee),
	url(r'^cancel_fee_receipt/$',cancel_fee_receipt),
	url(r'^fee_receipts_report/$',get_stu_fee_receipts_report),
	
	
	url(r'^due_report/$',due_paid_report),
	url(r'^refund_report/$',refund_report),
	url(r'^transport_report/$',transport_report),
	
	url(r'^paid_report/$',due_paid_report),
	
	url(r'^unpaid_report/$',unpaid_report),
	
	url(r'^get_stu_fee_receipts/$',get_stu_fee_receipts),
	url(r'^get_fee_rec_details/$',get_stu_fee_receipts),
	
	#url(r'^img/$',img),
	url(r'^print_fee_receipt/$',print_fee_receipt),
	url(r'^print_fee_receipt_coloured/$',print_fee_receipt_coloured),
	url(r'^StudentBankDetails_account/$',StudentBankDetails_account),
	url(r'^format_report/$',format_report),
	url(r'^AccAcademicFeeLetter/$',AccAcademicFeeLetter),
	url(r'^student_insurance_report/$',student_insurance_report),
	url(r'^remider_due_date/$',remider_due_date),
	#url(r'^qr_img/$',qr_img),
	# asasasas
	
	
]
