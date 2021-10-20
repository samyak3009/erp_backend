from __future__ import print_function
from django.shortcuts import render

from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import time
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum, F, Value, CharField
from login.models import EmployeeDropdown, EmployeePrimdetail, AuthUser
from musterroll.models import Reporting, EmployeePerdetail
from attendance.models import Attendance2
from datetime import date
import copy
from datetime import datetime
import calendar
from operator import itemgetter
from login.views import checkpermission
from .models import *
from leave.models import Leaves
from leave.views import calculate_working_days, fun_num_of_leaves
from login.models import EmployeePrimdetail
import io
from threading import Thread
import requests
from django.http.response import HttpResponse
from xlsxwriter.workbook import Workbook
import datetime
import calendar


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def mappedVarDeductions():
    const_values_old = AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS", session=1).exclude(status="DELETE").values().order_by('session', 'sno')
    const_values_new = AccountsDropdown.objects.filter(field="VARIABLE PAY DEDUCTIONS", session=2).exclude(status="DELETE").values().order_by('session', 'sno')
    swap_constants_deduction_values = {}
    for x in const_values_old:
        for y in const_values_new:
            if(x['value'] == y['value']):
                swap_constants_deduction_values[x['sno']] = y['sno']
                break
    return swap_constants_deduction_values


def mappedPayDeductions():
    const_values_old = AccountsDropdown.objects.filter(field="CONSTANT PAY DEDUCTIONS", session=1).exclude(status="DELETE").values().order_by('session', 'sno')
    const_values_new = AccountsDropdown.objects.filter(field="CONSTANT PAY DEDUCTIONS", session=2).exclude(status="DELETE").values().order_by('session', 'sno')
    swap_constants_deduction_values = {}
    for x in const_values_old:
        for y in const_values_new:
            if(x['value'] == y['value']):
                swap_constants_deduction_values[x['sno']] = y['sno']
                break
    return swap_constants_deduction_values


def mappedPaymentOptions():
    const_values_old = AccountsDropdown.objects.filter(field="PAYMENT OPTIONS", session=1).exclude(status="DELETE").values().order_by('session', 'sno')
    const_values_new = AccountsDropdown.objects.filter(field="PAYMENT OPTIONS", session=2).exclude(status="DELETE").values().order_by('session', 'sno')
    swap_component_values = {}
    for x in const_values_old:
        for y in const_values_new:
            if(x['value'] == y['value']):
                swap_component_values[x['sno']] = y['sno']
                break
    return swap_component_values


def mappedSalaryType():
    const_values_old = AccountsDropdown.objects.filter(field="SALARY TYPE", session=1).exclude(status="DELETE").values().order_by('session', 'sno')
    const_values_new = AccountsDropdown.objects.filter(field="SALARY TYPE", session=2).exclude(status="DELETE").values().order_by('session', 'sno')
    swap_component_values = {}
    for x in const_values_old:
        for y in const_values_new:
            if(x['value'] == y['value']):
                swap_component_values[x['sno']] = y['sno']
                break
    return swap_component_values


def mappedSalaryComponent():
    const_values_old = AccountsDropdown.objects.filter(field="SALARY COMPONENTS", session=1).exclude(status="DELETE").values().order_by('session', 'sno')
    const_values_new = AccountsDropdown.objects.filter(field="SALARY COMPONENTS", session=2).exclude(status="DELETE").values().order_by('session', 'sno')
    swap_component_values = {}
    for x in const_values_old:
        for y in const_values_new:
            if(x['value'] == y['value']):
                swap_component_values[x['sno']] = y['sno']
                break
    return swap_component_values


def mappedSalaryIngrident():
    swap_constants_deduction_values = mappedPayDeductions()
    swap_component_values = mappedSalaryComponent()
    main_details_values_old = SalaryIngredient.objects.filter(session=1, calcType="V").exclude(status="DELETE").values()
    main_details_values_new = SalaryIngredient.objects.filter(session=2, calcType="V").exclude(status="DELETE").values()
    swap_salary_ingrident = {}
    for x in main_details_values_old:
        for y in main_details_values_new:
            print(x['calcType'] == y['calcType'] and swap_component_values[x['Ingredients_id']] == y['Ingredients_id'] and x['added_by_id'] == y['added_by_id'] and x['taxstatus'] == y['taxstatus'])
            print(x['id'], y['id'], x['calcType'] == y['calcType'], swap_component_values[x['Ingredients_id']] == y['Ingredients_id'], x['added_by_id'] == y['added_by_id'], x['taxstatus'] == y['taxstatus'])
            if(x['calcType'] == y['calcType'] and swap_component_values[x['Ingredients_id']] == y['Ingredients_id'] and x['added_by_id'] == y['added_by_id'] and x['taxstatus'] == y['taxstatus']):
                swap_salary_ingrident[x['id']] = y['id']
                break
    main_details_values_old = SalaryIngredient.objects.filter(session=1, calcType="F").exclude(status="DELETE").values()
    main_details_values_new = SalaryIngredient.objects.filter(session=2, calcType="F").exclude(status="DELETE").values()
    for x in main_details_values_old:
        x['Formula'] = ",".join(list(str(swap_component_values[int(x)]) for x in list(x['Formula'].split(','))))
    for x in main_details_values_old:
        for y in main_details_values_new:
            if(x['calcType'] == y['calcType'] and x['Formula'] == y['Formula'] and swap_component_values[x['Ingredients_id']] == y['Ingredients_id'] and x['added_by_id'] == y['added_by_id'] and x['taxstatus'] == y['taxstatus']):
                swap_salary_ingrident[x['id']] = y['id']
                break
    return swap_salary_ingrident


def mappedConstantDeduction():
    swap_constants_deduction_values = mappedPayDeductions()
    swap_component_values = mappedSalaryComponent()

    main_details_values_old = ConstantDeduction.objects.filter(session=1, deductionType="V").exclude(status="DELETE").values()
    main_details_values_new = ConstantDeduction.objects.filter(session=2, deductionType="V").exclude(status="DELETE").values()
    swap_salary_ingrident = {}
    for x in main_details_values_old:
        for y in main_details_values_new:
            if(x['deductionType'] == y['deductionType'] and swap_constants_deduction_values[x['DeductionName_id']] == y['DeductionName_id'] and x['added_by_id'] == y['added_by_id'] and x['taxstatus'] == y['taxstatus'] and y['maxvalue'] == x['maxvalue']):
                swap_salary_ingrident[x['id']] = y['id']
                break
    main_details_values_old = ConstantDeduction.objects.filter(session=1, deductionType="F").exclude(status="DELETE").values()
    main_details_values_new = ConstantDeduction.objects.filter(session=2, deductionType="F").exclude(status="DELETE").values()
    for x in main_details_values_old:
        x['Formula'] = ",".join(list(str(swap_component_values[int(x)]) for x in list(x['Formula'].split(','))))
    for x in main_details_values_old:
        for y in main_details_values_new:
            if(x['deductionType'] == y['deductionType'] and x['Formula'] == y['Formula'] and swap_constants_deduction_values[x['DeductionName_id']] == y['DeductionName_id'] and x['added_by_id'] == y['added_by_id'] and x['taxstatus'] == y['taxstatus'] and y['maxvalue'] == x['maxvalue']):
                swap_salary_ingrident[x['id']] = y['id']
                break
    return swap_salary_ingrident
# print(mappedConstantDeduction())


def changeDropdownSession():
    main_details = AccountsDropdown.objects.filter(session=1, pid=0).exclude(status="DELETE").values().order_by('sno')

    bulk_main_details = (AccountsDropdown(pid=0, field=x['field'], value=x['value'], is_edit=x['is_edit'], is_delete=x['is_edit'], status=x['status'], session=AccountsSession.objects.get(id=2)) for x in main_details)
    AccountsDropdown.objects.bulk_create(bulk_main_details)
    sub_details = AccountsDropdown.objects.filter(session=1).exclude(status="DELETE").exclude(pid=0).values().order_by('pid', 'sno')
    temp_id_map = {}
    temp_add_list = []
    for x in sub_details:
        if x['pid'] in temp_id_map:
            x['pid'] = temp_id_map[x['pid']]
            temp_add_list.append(x)
        else:

            bulk_sub_details = (AccountsDropdown(pid=x['pid'], field=x['field'], value=x['value'], is_edit=x['is_edit'], is_delete=x['is_edit'], status=x['status'], session=AccountsSession.objects.get(id=2)) for x in temp_add_list)
            AccountsDropdown.objects.bulk_create(bulk_sub_details)
            temp_add_list = []
            temp_details = AccountsDropdown.objects.filter(sno=x['pid']).exclude(status="DELETE").values()
            store_id = AccountsDropdown.objects.filter(session=2, field=temp_details[0]['field'], value=temp_details[0]['value']).exclude(status="DELETE").values_list('sno', flat=True)
            x['pid'] = store_id[0]
            temp_id_map[x['pid']] = store_id[0]
            temp_add_list.append(x)
# changeDropdownSession()


def changeConstantDeduction():

    swap_constants_deduction_values = mappedPayDeductions()
    swap_component_values = mappedSalaryComponent()

    main_details_values = ConstantDeduction.objects.filter(session=1, deductionType="V").exclude(status="DELETE").values()
    for x in main_details_values:
        x['creditdate'] = add_months(x['creditdate'], x['creditnature'])
    bulk_main_details = (ConstantDeduction(DeductionName=AccountsDropdown.objects.get(sno=swap_constants_deduction_values[x['DeductionName_id']]), deductionType="V", maxvalue=x['maxvalue'], creditnature=x['creditnature'], creditdate=x['creditdate'], added_by=EmployeePrimdetail.objects.get(emp_id=x['added_by_id']), taxstatus=x['taxstatus'], status=x['status'], session=AccountsSession.objects.get(id=2))for x in main_details_values)
    ConstantDeduction.objects.bulk_create(bulk_main_details)

    main_details_values = ConstantDeduction.objects.filter(session=1, deductionType="F").exclude(status="DELETE").values()
    for x in main_details_values:
        x['creditdate'] = add_months(x['creditdate'], x['creditnature'])
        x['Formula'] = ",".join(list(str(swap_component_values[int(x)]) for x in list(x['Formula'].split(','))))
    bulk_main_details = (ConstantDeduction(DeductionName=AccountsDropdown.objects.get(sno=swap_constants_deduction_values[x['DeductionName_id']]), Formula=x['Formula'], percent=x['percent'], deductionType="F", maxvalue=x['maxvalue'], creditnature=x['creditnature'], creditdate=x['creditdate'], added_by=EmployeePrimdetail.objects.get(emp_id=x['added_by_id']), taxstatus=x['taxstatus'], status=x['status'], session=AccountsSession.objects.get(id=2))for x in main_details_values)
    ConstantDeduction.objects.bulk_create(bulk_main_details)
# changeConstantDeduction()


def changeSalaryIngredient():
    swap_constants_deduction_values = mappedPayDeductions()
    swap_component_values = mappedSalaryComponent()

    main_details_values = SalaryIngredient.objects.filter(session=1, calcType="V").exclude(status="DELETE").values()
    for x in main_details_values:
        x['next_count_month'] = add_months(x['next_count_month'], x['ingredient_nature'])
    bulk_main_details = (SalaryIngredient(Ingredients=AccountsDropdown.objects.get(sno=swap_component_values[x['Ingredients_id']]), calcType="V", ingredient_nature=x['ingredient_nature'], next_count_month=x['next_count_month'], added_by=EmployeePrimdetail.objects.get(emp_id=x['added_by_id']), taxstatus=x['taxstatus'], status=x['status'], session=AccountsSession.objects.get(id=2))for x in main_details_values)
    SalaryIngredient.objects.bulk_create(bulk_main_details)

    main_details_values = SalaryIngredient.objects.filter(session=1, calcType="F").exclude(status="DELETE").values()
    for x in main_details_values:
        x['next_count_month'] = add_months(x['next_count_month'], x['ingredient_nature'])
        x['Formula'] = ",".join(list(str(swap_component_values[int(x)]) for x in list(x['Formula'].split(','))))
    bulk_main_details = (SalaryIngredient(Ingredients=AccountsDropdown.objects.get(sno=swap_component_values[x['Ingredients_id']]), Formula=x['Formula'], percent=x['percent'], calcType="F", ingredient_nature=x['ingredient_nature'], next_count_month=x['next_count_month'], added_by=EmployeePrimdetail.objects.get(emp_id=x['added_by_id']), taxstatus=x['taxstatus'], status=x['status'], session=AccountsSession.objects.get(id=2))for x in main_details_values)
    SalaryIngredient.objects.bulk_create(bulk_main_details)
# changeSalaryIngredient()


def changeGrossDetails():
    swap_payment_options = mappedPaymentOptions()
    swap_salary_type = mappedSalaryType()
    swap_salary_ingrident = mappedSalaryIngrident()
    print(swap_salary_ingrident)
    main_details_values = EmployeeGross_detail.objects.filter(session=1).exclude(Status="DELETE").values().order_by('Emp_Id', 'id')

    for x in main_details_values:
        x['salary_type_id'] = swap_salary_type[x['salary_type_id']]
        x['pay_by_id'] = swap_payment_options[x['pay_by_id']]
        x['Ing_Id_id'] = swap_salary_ingrident[x['Ing_Id_id']]

    bulk_main_details = (EmployeeGross_detail(pay_by=AccountsDropdown.objects.get(sno=x['pay_by_id']), salary_type=AccountsDropdown.objects.get(sno=x['salary_type_id']), Ing_Id=SalaryIngredient.objects.get(id=x['Ing_Id_id']), Value=x['Value'], Emp_Id=EmployeePrimdetail.objects.get(emp_id=x['Emp_Id_id']), added_by=EmployeePrimdetail.objects.get(emp_id=x['added_by_id']), Status=x['Status'], session=AccountsSession.objects.get(id=2))for x in main_details_values)
    EmployeeGross_detail.objects.bulk_create(bulk_main_details)
# changeGrossDetails()


def changeEmployeeDeductions():
    swap_var_deduction = mappedVarDeductions()
    swap_constant_deduction = mappedConstantDeduction()

    main_details_values = EmployeeDeductions.objects.filter(session=1).exclude(variableDeduction__isnull=True).exclude(status="DELETE").values().order_by('id')
    for x in main_details_values:
        x['variableDeduction_id'] = swap_var_deduction[x['variableDeduction_id']]
    print(main_details_values)
    bulk_main_details = (EmployeeDeductions(variableDeduction=AccountsDropdown.objects.get(sno=x['variableDeduction_id']), Emp_Id=EmployeePrimdetail.objects.get(emp_id=x['Emp_Id_id']), added_by=EmployeePrimdetail.objects.get(emp_id=x['added_by_id']), status=x['status'], session=AccountsSession.objects.get(id=2))for x in main_details_values)
    EmployeeDeductions.objects.bulk_create(bulk_main_details)

    main_details_values = EmployeeDeductions.objects.filter(session=1).exclude(constantDeduction__isnull=True).exclude(status="DELETE").values().order_by('id')
    for x in main_details_values:
        x['constantDeduction_id'] = swap_constant_deduction[x['constantDeduction_id']]
    print(main_details_values)
    bulk_main_details = (EmployeeDeductions(constantDeduction=ConstantDeduction.objects.get(id=x['constantDeduction_id']), Emp_Id=EmployeePrimdetail.objects.get(emp_id=x['Emp_Id_id']), added_by=EmployeePrimdetail.objects.get(emp_id=x['added_by_id']), status=x['status'], session=AccountsSession.objects.get(id=2))for x in main_details_values)
    EmployeeDeductions.objects.bulk_create(bulk_main_details)
# changeEmployeeDeductions()
