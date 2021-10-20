from separation.models import SeparationReporting,SeparationApplication,SeparationLevelApproval,SeparationExitPaper
from login.models import EmployeePrimdetail
from musterroll.models import EmployeeSeparation,NoDuesHead,NoDuesEmp


def get_reporting_to_levels(dept,desg):
	return SeparationReporting.objects.filter(department = dept,reporting_to=desg).exclude(reporting_no__isnull=True).values_list('reporting_no',flat=True).distinct()

def get_reporting_employees(dept,desg,level):
	return SeparationReporting.objects.filter(department = dept,reporting_to=desg,reporting_no=level).exclude(reporting_no__isnull=True).values_list('emp_id',flat=True)

def get_reporting_employees_applications(emp_id,status,extra_filter):
	data=list(SeparationLevelApproval.objects.filter(approved_by = emp_id,approval_status__in=status).exclude(status='DELETE').exclude(form_id__status='DELETE').extra(**extra_filter).values('form_id','approved_by__name','approval_status','remark','level','form_id__emp_id','form_id__type__value','form_id__relieving_date','form_id__rejoin_date','form_id__final_remark','form_id__resignation_doc','form_id__attachment','form_id__emp_id__name'))

	return data
def check_for_level_increment(emp_id,level):
	qr = SeparationReporting.objects.filter(emp_id=emp_id,reporting_no=level).values_list('reporting_no',flat=True).distinct()
	if(len(qr)>0):
		return True
	return False

def add_next_level_pending(emp_id,level,id):
	print(level,"LEVEL")
	if check_for_level_increment(emp_id,level):
		qr = list(SeparationReporting.objects.filter(emp_id=emp_id,reporting_no=level).values('department','reporting_to'))
		for r in qr:
			approved_by_id = EmployeePrimdetail.objects.filter(desg=r['reporting_to'],dept=r['department']).values_list('emp_id',flat=True)
			for e in approved_by_id:
				SeparationLevelApproval.objects.create(form_id=EmployeeSeparation.objects.get(id=id),approved_by=EmployeePrimdetail.objects.get(emp_id=e),approval_status='PENDING',level=level)


# def testing():
# 	qr = list(SeparationExitPaper.objects.values('paper_attr'))
# 	# qr2 = list(SeparationExitPaper.objects.values())
# 	qr1 = list(SeparationExitPaper.objects.filter(paper_attr__has_key='name').values())
# 	# print(qr2,"DATA")
# 	print(qr,"data")
# 	print(qr1,"LL")
# 	print(qr[0]['paper_attr'],'data2')
# 	print(qr[0]['paper_attr']['name'],'Name')
# 	print(qr[1]['paper_attr'],'data2')
# 	print(qr[1]['paper_attr']['name'],'Name')
# # testing()




def check_emp(emp_id):
	qry=list(EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept','desg'))
	reporting=get_reporting_to_levels(qry[0]['dept'],qry[0]['desg'])
	print(reporting,"reporting")
	if len(reporting)>0:
		print("TRUE")
		return True
	else:
		print("False")
		return False

# check_emp(4478)