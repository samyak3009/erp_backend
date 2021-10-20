from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from .views import *
from .views_reports import emp_deductions_report,emp_salary_report

urlpatterns = [

    url(r'^get_components/$',getComponents),
    url(r'^generate_monthly_salary/$',generate_monthly_salary),
    url(r'^emp_detail/$',emp_detail),
    url(r'^ingredients_add/$',insert_salary_ingredients),
    url(r'^employee_pay_detail/$',employee_pay_detail),
    url(r'^all_employee_pay_detail/$',all_employee_pay_detail),
    
    url(r'^fields/$',Accounts_dropdown),
	url(r'^fields_category/$',Accounts_dropdown),
	url(r'^add_category/$',Accounts_dropdown),
	url(r'^update_category/$',Accounts_dropdown),
	url(r'^delete_category/$',Accounts_dropdown),
	url(r'^locking_unlocking/$',locking_unlocking),
	url(r'^constant_pay_deduction/$',Constant_pay_deduction),
	url(r'^emp_declaration_approval/$',emp_declaration_approval),

	url(r'^emp_declaration_form/$',emp_declaration_form),
	url(r'^generate_monthly_excel_sheet/$',generate_monthly_excel_sheet),
	url(r'^generate_tds_sheet/$',generate_tds_sheet),

	url(r'^view_previous_sign_in_arrear/$',view_previous_sign_in_arrear),
	url(r'^view_previous_arrear/$',view_previous_arrear),
	
	url(r'^insert_increment_arrear/$',insert_increment_arrear),
	url(r'^insert_da_arrear/$',insert_da_arrear),
	url(r'^insert_sign_in_out_arrear/$',insert_sign_in_out_arrear),
	url(r'^insert_additional_arrear/$',insert_additional_arrear),
	url(r'^emp_deductions/$',Employee_deduction),
	url(r'^generate_excel/$',generate_excel),
	url(r'^emp_pay_slip/$',pay_slip),
	url(r'^modified_generate_monthly_excel_sheet/$',modified_generate_monthly_excel_sheet),

	################# REPORTS #########################33
	url(r'^emp_deductions_report/$',emp_deductions_report),
	url(r'^emp_salary_report/$',emp_salary_report),
	url(r'^form_16/$',form_16),


	
]


