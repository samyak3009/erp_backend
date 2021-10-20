from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from .views import get_employee_details, get_dept_faculty_web, get_reporting_employees, ExtractDepartment_all_organizations, get_details, HR_ShiftSettings, Add_Musterroll, Update_Musterroll, GetData, GetLinks, HR_dropdown, AdvanceSearch, AAR_dropdown, emp_count, get_dept_faculty, emp_certification, emp_certi_report, extension_data, reporting_report,roles_report,emp_certificate_report,emp_salary_slip
from attendance.views import employee_data, all_employee_data
urlpatterns = [

    #url(r'^/$', admin.site.urls),
    ################# EMPLOYEE DETAILS ##########
    url(r'^employee_details/$', get_employee_details),

    ##################### ADD MUSTERROLL ##########################
    url(r'^add/$', Add_Musterroll),
    url(r'^get_reporting_employees/$', get_reporting_employees),
    url(r'^data/$', Add_Musterroll),
    url(r'^add/values/$', Add_Musterroll),
    url(r'^get_dept/$', ExtractDepartment_all_organizations),
    ##################### MUSTERROLL SETTINGS ######################
    url(r'^fields/$', HR_dropdown),
    url(r'^fields_category/$', HR_dropdown),
    url(r'^add_category/$', HR_dropdown),
    url(r'^update_category/$', HR_dropdown),
    url(r'^delete_category/$', HR_dropdown),
    ############## UPDATE EMPLOYEE ####################
    url(r'^update_employee/id$', employee_data),
    url(r'^all_employee_data$', all_employee_data),
    url(r'^update_employee/info$', Update_Musterroll),
    url(r'^update_employee/update$', Update_Musterroll),
    url(r'^get_details/$', get_details),
    url(r'^dept_faculty/$', get_dept_faculty),
    url(r'^dept_faculty_web/$', get_dept_faculty_web),






    ################### SHIFT SETTINGS ###################
    url(r'^view_shift/$', HR_ShiftSettings),
    url(r'^add_shift/$', HR_ShiftSettings),
    url(r'^previous_shift/$', HR_ShiftSettings),

    ############### PAYROLL#######################
    # url(r'^pay/$',pay_view),

    ################### Employee RecordReport ############
    url(r'^GetData$', GetData),
    url(r'^AdvanceSearch/$', AdvanceSearch),
    #################### Dashboard Assign Link #############
    url(r'^GetLinks/$', GetLinks),
    ######################### AAR ###
    url(r'^aar_fields/$', AAR_dropdown),
    url(r'^aar_fields_category/$', AAR_dropdown),
    url(r'^aar_add_category/$', AAR_dropdown),
    url(r'^aar_update_category/$', AAR_dropdown),
    url(r'^aar_delete_category/$', AAR_dropdown),
    ################################ count ######################
    url(r'^emp_count/$', emp_count),

    #################### MOOC #############################
    url(r'^emp_certification/$', emp_certification),
    url(r'^emp_certification_report/$', emp_certi_report),
    url(r'^emp_certificate_report/$', emp_certificate_report),

    ################## KIET - EXTENSION #########
    url(r'^extension_data/$', extension_data),

    ################ REPORTING REPORT ###########
    url(r'^reporting_report/$', reporting_report),
    #############################################
    url(r'^roles_report/$', roles_report),
    url(r'^emp_salary_slip/$', emp_salary_slip),
    
    

]
