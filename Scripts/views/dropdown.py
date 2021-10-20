from django.shortcuts import render
from StudentAcademics.models import StudentAcademicsDropdown
from Registrar.models import Semtiming


old_session = 7
odd_old_session = 8
new_session = 9

# FOR EVEN SEM
# TABLES:---
#['StudentAcademicsDropdown','AccountsDropdown','StuHostelDropdown']


def changeDropdownSession():
    main_details = StudentAcademicsDropdown.objects.filter(session=odd_old_session, pid=0).exclude(status="DELETE").values().order_by('sno')
    bulk_main_details = (StudentAcademicsDropdown(pid=0, field=x['field'], value=x['value'], is_edit=x['is_edit'], is_delete=x['is_edit'], status=x['status'], session=Semtiming.objects.get(uid=new_session)) for x in main_details)
    StudentAcademicsDropdown.objects.bulk_create(bulk_main_details)

    sub_details = StudentAcademicsDropdown.objects.filter(session=odd_old_session).exclude(status="DELETE").exclude(pid=0).values().order_by('pid', 'sno')
    temp_id_map = {}
    temp_add_list = []
    for x in sub_details:
        if x['pid'] in temp_id_map:
            x['pid'] = temp_id_map[x['pid']]
            temp_add_list.append(x)
        else:
            temp_add_list = []
            temp_details = StudentAcademicsDropdown.objects.filter(sno=x['pid']).exclude(status="DELETE").values()
            store_id = StudentAcademicsDropdown.objects.filter(session=new_session, field=temp_details[0]['field'], value=temp_details[0]['value']).exclude(status="DELETE").values_list('sno', flat=True)
            x['pid'] = store_id[0]
            temp_id_map[x['pid']] = store_id[0]
            temp_add_list.append(x)
            bulk_sub_details = (StudentAcademicsDropdown(pid=x['pid'], field=x['field'], value=x['value'], is_edit=x['is_edit'], is_delete=x['is_delete'], status=x['status'], session=Semtiming.objects.get(uid=new_session)) for x in temp_add_list)
            StudentAcademicsDropdown.objects.bulk_create(bulk_sub_details)

# changeDropdownSession()
