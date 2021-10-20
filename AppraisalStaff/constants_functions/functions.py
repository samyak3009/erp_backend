import datetime
from musterroll.models import EmployeeSeparation, EmployeePrimdetail
# from AppraisalStaff.views.appraisal_staff_function import *
import AppraisalStaff as appraisalstaff


def check_eligibility_of_employee(emp_id, session):
    # time = datetime.datetime.now()
    qry = EmployeeSeparation.objects.filter(emp_id=emp_id, final_status='APPROVED BY ADMIN').order_by('-id').values('rejoin_date', 'status')
    # total_exp = appraisalstaff.views.appraisal_staff_function.get_total_experience(emp_id, {})
    # print(total_exp, 'total_exp')
    # if appraisalstaff.views.appraisal_staff_checks_function.check_is_exp_less_than_6_month(emp_id, session, total_exp, {}) == False:
    #     status = "NOT ELIGIBLE"
    date_of_join = EmployeePrimdetail.objects.filter(emp_id=emp_id).values("doj")
    status = "ELIGIBLE"
    if len(qry) > 0:
        print(qry[0]['status'])
        if qry[0]['status'] == "LEAVE":
            d1 = datetime.date(2020, 6, 30)
            d2 = qry[0]['rejoin_date']
            if ((d1.year - d2.year) * 12 + d1.month - d2.month + (d1.day - d2.day) / 30) > 6:
                status = "ELIGIBLE"
            else:
                status = "NOT ELIGIBLE"
        elif qry[0]['status'] == "RESIGN":
            status = "NOT ELIGIBLE"
        elif date_of_join:
            d1 = datetime.date(2020, 6, 30)
            d2 = date_of_join[0]['doj']
            print("sasaqq")
            if ((d1.year - d2.year) * 12 + d1.month - d2.month + (d1.day - d2.day) / 30) > 6:
                status = "ELIGIBLE"
            else:
                status = "NOT ELIGIBLE"
    else:
        d1 = datetime.date(2020, 6, 30)
        d2 = date_of_join[0]['doj']
        if ((d1.year - d2.year) * 12 + d1.month - d2.month + (d1.day - d2.day) / 30) > 6:
            status = "ELIGIBLE"
        else:
            status = "NOT ELIGIBLE"
    return status


def check_eligibility_of_employee_faculty(emp_id, session):
    # time = datetime.datetime.now()
    qry = EmployeeSeparation.objects.filter(emp_id=emp_id, final_status='APPROVED BY ADMIN').order_by('-id').values('rejoin_date', 'status')
    # total_exp = appraisalstaff.views.appraisal_staff_function.get_total_experience(emp_id, {})
    # print(total_exp, 'total_exp')
    # if appraisalstaff.views.appraisal_staff_checks_function.check_is_exp_less_than_6_month(emp_id, session, total_exp, {}) == False:
    #     status = "NOT ELIGIBLE"
    date_of_join = EmployeePrimdetail.objects.filter(emp_id=emp_id).values("doj")
    status = "ELIGIBLE"
    if len(qry) > 0:
        if qry[0]['status'] == "LEAVE":
            d1 = datetime.date(2020, 8, 28)
            d2 = qry[0]['rejoin_date']
            if ((d1.year - d2.year) * 12 + d1.month - d2.month + (d1.day - d2.day) / 30) > 6:
                status = "ELIGIBLE"
            else:
                status = "NOT ELIGIBLE"
        elif qry[0]['status'] == "RESIGN":
            status = "NOT ELIGIBLE"
        elif date_of_join:
            d1 = datetime.date(2020, 8, 28)
            d2 = date_of_join[0]['doj']
            if ((d1.year - d2.year) * 12 + d1.month - d2.month + (d1.day - d2.day) / 30) > 6:
                status = "ELIGIBLE"
            else:
                status = "NOT ELIGIBLE"
    else:
        d1 = datetime.date(2020, 8, 28)
        d2 = date_of_join[0]['doj']
        if ((d1.year - d2.year) * 12 + d1.month - d2.month + (d1.day - d2.day) / 30) > 6:
            status = "ELIGIBLE"
        else:
            status = "NOT ELIGIBLE"
    return status
