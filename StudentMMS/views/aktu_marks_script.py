from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.db.models import Q
import json
import requests
import time
import unicodedata

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod

from StudentMMS.models import *
from Registrar.models import *
from musterroll.models import EmployeePrimdetail

from login.views import checkpermission,generate_session_table_name


def kiet_script(request):
	print("1")
	try:
		session_name = '1819e'
		cookie = '_ga=GA1.3.1610272396.1535472722; _gid=GA1.3.1906532346.1561990857; _gat=1; ASP.NET_SessionId=olbm0veg0d0fiidn5ety01nw; User=User=3SheT0SbF/+sfaV6EjIPPQ==; Pass=Pass=4WXUWZnZZ54/RT5XX1NN7A==; AuthToken=884a4196-79a5-4797-85e8-134eb1fc2f0d'
		StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_",session_name)
		SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)
		studentSession=generate_session_table_name("studentSession_",session_name)
		StudentFinalMarksStatus=generate_session_table_name("StudentFinalMarksStatus_",session_name)
		# session = 8
		# student_entered_marks=StudentUniversityMarks.objects.values_list('uniq_id',flat=True)

		qry_students = studentSession.objects.filter(year=4,uniq_id__dept_detail__course=13).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") |  Q(uniq_id__admission_status__value__contains="EX") | Q(uniq_id__uni_roll_no__isnull=True)).values_list('uniq_id',flat=True)).values('uniq_id','uniq_id__uni_roll_no','section__sem_id__sem','section__sem_id','sem__dept__course').order_by('uniq_id__uni_roll_no')

		for students in qry_students:

			# print(students['section__sem_id'])
			qry_sem_subjects = SubjectInfo.objects.filter(sem_id=students['section__sem_id']).exclude(status='DELETE').values('id','sub_alpha_code','sub_num_code','subject_type__value')
			# print(qry_sem_subjects)
			for sub in qry_sem_subjects:
				sub['sub_alpha_code'].replace(" ","")
				sub['sub_num_code'].replace(" ","")
				if 'GP' in sub['sub_alpha_code']:
					sub['sub_type']='GP'
				else:
					if sub['subject_type__value'] =='LAB':
						sub['sub_type']='Practical'
					else:
						sub['sub_type'] = 'Theory'

			time.sleep(2)
			re = requests.post("https://erp.aktu.ac.in/WebPages/OneView/OneView.aspx", data={'__VIEWSTATE': '/wEPDwUKLTY3NDIyMzIxOGRkzzJFpByKgv5wI2dl2lWIbUGF4Tw=', '__VIEWSTATEGENERATOR': '309C3D50', 'btnSearch': 'Search','txtRollNo':str(students['uniq_id__uni_roll_no'])},headers={'Content-Type':'application/x-www-form-urlencoded','Upgrade-Insecure-Requests':'1','Accept-Encoding':'gzip, deflate, br','Accept-Language':'en-GB,en-US;q=0.9,en;q=0.8','Cookie':cookie,'User-Agent':'test','Origin':'https://erp.aktu.ac.in','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer':'https://erp.aktu.ac.in/WebPages/OneView/OneView.aspx'})

			r=re.content
			response = r
			f= open("guru99.html","wb")
			f.write(response)
			f.close()
			soup = BeautifulSoup(r, "html.parser")

			div=soup.find("div",{"id": "pnlContent"})
			################### NECESSARY FOR FINDING ONLY LEVEL ONE TABLES ################################################
			tables_level_1=[]
			# print(soup, "duv", div)
			for table in div.find_all('table'):
				if table.parent.get('id') == 'pnlContent':
					tables_level_1.append(table)
			# print(tables_level_1)
			###########################################################################################################################

			COLLEGE_CODE = unicodedata.normalize('NFKD',soup.find(id="lblInstitute").text[1:4].strip()).encode('ascii','ignore')
			rollno = unicodedata.normalize('NFKD',soup.find(id="lblRollNo").text.strip()).encode('ascii','ignore')
			COLLEGE_NAME = unicodedata.normalize('NFKD',soup.find(id="lblInstitute").text[6:].strip()).encode('ascii','ignore')
			COURSE_CODE = unicodedata.normalize('NFKD',soup.find(id="lblCourse").text[1:3].strip()).encode('ascii','ignore')
			COURSE_NAME = unicodedata.normalize('NFKD',soup.find(id="lblCourse").text[5:].strip()).encode('ascii','ignore')
			BRANCH_CODE = unicodedata.normalize('NFKD',soup.find(id="lblBranch").text[1:3].strip()).encode('ascii','ignore')
			BRANCH_NAME = unicodedata.normalize('NFKD',soup.find(id="lblBranch").text[5:].strip()).encode('ascii','ignore')
			ENROLLMENT_NO = unicodedata.normalize('NFKD',soup.find(id="lblEnrollmentNo").text.strip()).encode('ascii','ignore')
			NAME = unicodedata.normalize('NFKD',soup.find(id="lblFullName").text.strip()).encode('ascii','ignore')
			FATHERS_NAME = unicodedata.normalize('NFKD',soup.find(id="lblFatherName").text.strip()).encode('ascii','ignore')
			try:
				TOTAL_MARKS_OBTAINED = unicodedata.normalize('NFKD',soup.find(id="lblFinalMO").text.strip()).encode('ascii','ignore').decode("utf-8")
				TOTAL_MAX_MARKS = unicodedata.normalize('NFKD',soup.find(id="lblFinalMM").text.strip()).encode('ascii','ignore').decode("utf-8")
				DIVISION = unicodedata.normalize('NFKD',soup.find(id="lblDivisionAwarded").text.strip()).encode('ascii','ignore').decode("utf-8")
			except Exception as e:
					TOTAL_MARKS_OBTAINED=None
					TOTAL_MAX_MARKS=None
					DIVISION=None
			# print(COLLEGE_CODE,rollno,COLLEGE_NAME,COURSE_CODE,COURSE_NAME,BRANCH_CODE,BRANCH_NAME,ENROLLMENT_NO,NAME,FATHERS_NAME)

			marksDivArr = tables_level_1[1].findChildren('tr')[1].findChildren('td')[0].findChildren('div')
			# print(marksDivArr[0])
			marksDiv = marksDivArr[0]

			global flag
			global FINAL_RESULT_STATUS
			flag=0
			while marksDiv:
				# print(marksDiv.findChildren('div')[0].findChildren('table'))
				# break
				if type(marksDiv) is bs4.element.Tag:
					pass
					# print(marksDiv, str(type(marksDiv)))
					# return
				else:
					# print("marksDiv")
					marksDiv=marksDiv.next_sibling
					continue
				if marksDiv.name == 'div':
					# print(flag)
					if flag == 0:
						SESSION = marksDiv.findChildren('div')[0].findChildren('span')[0].text[10:17]
						CURRENT_SEM = marksDiv.findChildren('div')[0].findChildren('span')[1].text
						SESSION_TEXT = marksDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]

						YEAR_STATUS = (marksDiv.findChildren('div')[0].findChildren('span')[2].text)
						YEAR_MARKS = (marksDiv.findChildren('div')[0].findChildren('span')[3].text)
						AUC_STATUS = (marksDiv.findChildren('div')[0].findChildren('span')[5].text)
						# print(SESSION,CURRENT_SEM,SESSION_TEXT,YEAR_STATUS,YEAR_MARKS,AUC_STATUS)
						RESULT = marksDiv.findChildren('div')[0].text.rfind('Result : ')
						RESULT_STATUS = marksDiv.findChildren('div')[0].text[RESULT+9:]
						FINAL_RESULT_STATUS = RESULT_STATUS[0:RESULT_STATUS.find('Marks')].strip().split("\n")[0]
						# print(RESULT_STATUS[0:RESULT_STATUS.find('Marks')].strip().split("\n")[0])
						# print(RESULT_STATUS.split("\n",1))
						# print(CURRENT_SEM)
						YEAR_TOTAL=YEAR_MARKS.split("/")[1]
						YEAR_OBTAINED=YEAR_MARKS.split("/")[0]
						cop=""
						if 'COP' in marksDiv.findChildren('div')[0].text:
							ind2 = marksDiv.findChildren('div')[0].text.find('COP : ')
							cop = marksDiv.findChildren('div')[0].text[ind2+6:]
							# print(cop,"cop")




						ind1 = AUC_STATUS.find('AUC Status : ')
						ind2 = AUC_STATUS.find(' AUC2 Status : ')
						auc_status = AUC_STATUS[ind1+13:ind2]
						auc2_status = AUC_STATUS[ind2+15:]

						sem_li=CURRENT_SEM.split(',')
						if str(students['section__sem_id__sem']) not in sem_li:
							marksDiv=marksDiv.next_sibling
							continue
					flag = 0
					marksNextDiv = marksDiv.next_sibling
					NEXT_SESSION=''
					while marksNextDiv and flag == 0:
						if type(marksNextDiv) is bs4.element.Tag:
							pass
						else:
							marksNextDiv=marksNextDiv.next_sibling
							continue
						if marksNextDiv.name == 'div':
							NEXT_SESSION = marksNextDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]
							NEXT_SEM = marksNextDiv.findChildren('div')[0].findChildren('span')[1].text
							if NEXT_SESSION == 'BACK' and CURRENT_SEM==NEXT_SEM:

								flag = 1
						marksNextDiv = marksNextDiv.next_sibling
					if flag == 1:
						marksDiv=marksDiv.next_sibling
						continue
					marksPrevDiv = marksDiv.previous_sibling
					if SESSION_TEXT == 'BACK':
						while marksPrevDiv:
							if marksPrevDiv.name == 'div':
								PREV_SESSION = marksPrevDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]
								PREV_SEM = marksPrevDiv.findChildren('div')[0].findChildren('span')[1].text

								if PREV_SESSION == 'REGULAR' and CURRENT_SEM==PREV_SEM:
									SESSION = marksPrevDiv.findChildren('div')[0].findChildren('span')[0].text[10:17]
							marksPrevDiv = marksPrevDiv.previous_sibling
					semtd = marksDiv.findChildren('div')[1].find_all('div',{'class': 'col-md-6'})
					m=0

					for ss in semtd :
						sem1td=ss.findChildren("table")[0]
						if sem1td.name == 'table':
							SEMESTER = sem1td.findChildren('span')[1].text
							if SEMESTER=='':
								continue

							if str(students['section__sem_id__sem']) != SEMESTER:
								continue

							STATUS = unicodedata.normalize('NFKD',sem1td.findChildren('tr')[3].findChildren('td')[2].text.strip()).encode('ascii','ignore')

							student_sub=qry_sem_subjects[:]
							student_sub_marks = []

							for subtr in  sem1td.findChildren('tr')[5].findChildren('table')[1].findChildren('tr')[1:]:
								SUB_CODE = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[0].text.strip()).encode('ascii','ignore')[:10]).replace("b","").replace("'","")
								SUB_NAME = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[1].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_TYPE = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[2].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								# if (SUB_TYPE=='Practical'):
								# 	print("inn")
								# 	SUB_TYPE='LAB'
								SUB_INTERNAL = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[3].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_EXTERNAL = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[4].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_BACK = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[5].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								CREDIT = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[6].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")

								student_sub_marks.append({'sub_code':SUB_CODE,'sub_type':SUB_TYPE,'internal':SUB_INTERNAL,'external':SUB_EXTERNAL,'back':SUB_BACK,'sub_name':SUB_NAME,'credit':CREDIT})

							########################## stored alpha code=BOP, stored num code=471 & sub code from aktu = BOP471 ######
							############# CHECK if 'BOP' present in 'BOP471' and '471' present in 'BOP471' #####################

							n2 = len(student_sub_marks)

							index_to_delete = []
							# print(student_sub)
							# print(student_sub_marks)
							for i in range(n2):
								for j in range(len(student_sub)):
									if (student_sub[j]['sub_alpha_code'] in student_sub_marks[i]['sub_code']) and (student_sub[j]['sub_num_code'] in student_sub_marks[i]['sub_code']) and (student_sub[j]['sub_type'].upper() == student_sub_marks[i]['sub_type'].upper()):

										external=(student_sub_marks[i]['external'])
										internal=(student_sub_marks[i]['internal'])
										# print("1")
										l=StudentUniversityMarks.objects.update_or_create(uniq_id=studentSession.objects.get(uniq_id=students['uniq_id']),subject_id=SubjectInfo.objects.get(id=student_sub[j]['id']),defaults={'external_marks':external,'internal_marks':internal,'added_by':EmployeePrimdetail.objects.get(emp_id='00007')})
										# print(l)
										del student_sub[j]
										index_to_delete.append(i)
										break


							for ind in sorted(index_to_delete, reverse=True):
								del student_sub_marks[ind]

							########################## stored alpha code=BOPP, stored num code=471 & sub code from aktu = BOP471P ######
							############# CHECK if 'BOP' (remove last character from stored alpha code i.e 'P') present in 'BOP471' and '471' present in 'BOP471' #####################

							n2 = len(student_sub_marks)

							index_to_delete = []

							for i in range(n2):
								for j in range(len(student_sub)):

									if (student_sub[j]['sub_alpha_code'][:-1] in student_sub_marks[i]['sub_code']) and (student_sub[j]['sub_num_code'] in student_sub_marks[i]['sub_code']) and (student_sub[j]['sub_type'].upper() == student_sub_marks[i]['sub_type'].upper()):

										external=(student_sub_marks[i]['external'])

										internal=(student_sub_marks[i]['internal'])
										StudentUniversityMarks.objects.update_or_create(uniq_id=studentSession.objects.get(uniq_id=students['uniq_id']),subject_id=SubjectInfo.objects.get(id=student_sub[j]['id']),defaults={'external_marks':external,'internal_marks':internal,'added_by':EmployeePrimdetail.objects.get(emp_id='00007')})
										del student_sub[j]
										index_to_delete.append(i)
										break

							for ind in sorted(index_to_delete, reverse=True):
								del student_sub_marks[ind]
				marksDiv=marksDiv.next_sibling
			# print(FINAL_RESULT_STATUS,TOTAL_MARKS_OBTAINED,TOTAL_MAX_MARKS)
			if TOTAL_MARKS_OBTAINED is not None:
				print(students['uniq_id__uni_roll_no'])
				StudentFinalMarksStatus.objects.update_or_create(uniq_id=studentSession.objects.get(uniq_id=students['uniq_id']),defaults={'Total_marks_obtained':TOTAL_MARKS_OBTAINED,'Total_max_marks':TOTAL_MAX_MARKS,'Division_awarded':DIVISION,'Result_status':FINAL_RESULT_STATUS,'Year_obtained':YEAR_OBTAINED,'Year_total':YEAR_TOTAL})

				

	except Exception as e:
		print(e)
	return functions.RESPONSE(statusMessages.MESSAGE_SUCCESS,statusCodes.STATUS_SUCCESS)



def aktu_script(request):
	session_name = '1819o'

	batch_from = '15'
	semester = '7'
	college_code = '032'

	db_name = "aktu_"+session_name

	if batch_from=='15':
		max_external_marks = 100
		max_internal_marks = 50
	else:
		max_external_marks = 70
		max_internal_marks = 30

	qry_branch = Branchdetails.objects.using(db_name).filter(id__gt=16).values('id','branch_code')
	qry_college = College.objects.using(db_name).filter(insitute_code=college_code).values('id','insitute_code')

	for branch in qry_branch:
		index = 1
		break_count=0

		print(branch['id'],"branch")
		while True:
			if break_count >=10:
				break

			if index<10:
				index_str="00"+str(index)
			elif index<100:
				index_str="0"+str(index)
			else:
				index_str=str(index)

			uni_roll_no = batch_from+str(qry_college[0]['insitute_code'])+str(branch['branch_code'])+index_str

			print(uni_roll_no,"lo")
			re = requests.post("https://erp.aktu.ac.in/WebPages/OneView/OneView.aspx", data={'__VIEWSTATE': '/wEPDwUKLTY3NDIyMzIxOGRkzzJFpByKgv5wI2dl2lWIbUGF4Tw=', '__VIEWSTATEGENERATOR': '309C3D50', 'btnSearch': 'Search','txtRollNo':uni_roll_no},headers={'Content-Type':'application/x-www-form-urlencoded','Upgrade-Insecure-Requests':'1','Accept-Encoding':'gzip, deflate, br','Accept-Language':'en-GB,en-US;q=0.9,en;q=0.8','Cookie':'_ga=GA1.3.128666710.1549476160; _gid=GA1.3.957109422.1549476160; _gat=1; ASP.NET_SessionId=j3jm4dkvp3pnbbjh5c4xxpx3; User=User=3SheT0SbF/+sfaV6EjIPPQ==; Pass=Pass=0LG9J9/az/6AVA9HfNCFWg==; AuthToken=8c0eacac-7830-456d-b959-994f3486bf22','User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36','Origin':'https://erp.aktu.ac.in','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer':'https://erp.aktu.ac.in/WebPages/OneView/OneView.aspx'})

			r=re.text
			response = r
			soup = BeautifulSoup(response,"html.parser")
			div=soup.find("div",{"id": "pnlContent"})

			################### NECESSARY FOR FINDING ONLY LEVEL ONE TABLES ################################################

			tables_level_1=[]
			for table in div.find_all('table'):
				if table.parent.get('id') == 'pnlContent':
					tables_level_1.append(table)

			#################################################################################################################

			COLLEGE_CODE = str(unicodedata.normalize('NFKD',soup.find(id="lblInstitute").text[1:4].strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			rollno = str(unicodedata.normalize('NFKD',soup.find(id="lblRollNo").text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			COLLEGE_NAME = str(unicodedata.normalize('NFKD',soup.find(id="lblInstitute").text[6:].strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			COURSE_CODE = str(unicodedata.normalize('NFKD',soup.find(id="lblCourse").text[1:3].strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			COURSE_NAME = str(unicodedata.normalize('NFKD',soup.find(id="lblCourse").text[5:].strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			BRANCH_CODE = str(unicodedata.normalize('NFKD',soup.find(id="lblBranch").text[1:3].strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			BRANCH_NAME = str(unicodedata.normalize('NFKD',soup.find(id="lblBranch").text[5:].strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			ENROLLMENT_NO = str(unicodedata.normalize('NFKD',soup.find(id="lblEnrollmentNo").text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			NAME = str(unicodedata.normalize('NFKD',soup.find(id="lblFullName").text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
			FATHERS_NAME = str(unicodedata.normalize('NFKD',soup.find(id="lblFatherName").text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")

			marksDivArr = tables_level_1[1].findChildren('tr')[1].findChildren('td')[0].findChildren('div')

			if NAME=='':
				break_count+=1
				index+=1
				continue

			break_count=0

			qry_course_insert = Coursedetails.objects.using(db_name).update_or_create(course_code=COURSE_CODE,defaults={'course_name':COURSE_NAME})

			qry_branch_id = Branchdetails.objects.using(db_name).filter(branch_code=BRANCH_CODE).values('id')

			qry_primdetail_insert = Studentprimdetail.objects.using(db_name).update_or_create(rollno=uni_roll_no,defaults={'name':NAME,'fathername':FATHERS_NAME,'semester':semester,'college_id':College.objects.using(db_name).get(id=qry_college[0]['id']),'branch_id':Branchdetails.objects.using(db_name).get(id=qry_branch_id[0]['id']),'course_id':Coursedetails.objects.using(db_name).get(id=qry_course_insert[0].id)})

			if len(marksDivArr)==0:
				index+=1
				continue

			marksDiv = marksDivArr[0]
			global flag
			flag=0
			while marksDiv:
				if marksDiv.name == 'div':
					YEAR_STATUS=''
					if flag == 0:
						SESSION = marksDiv.findChildren('div')[0].findChildren('span')[0].text[10:17]
						CURRENT_SEM = marksDiv.findChildren('div')[0].findChildren('span')[1].text
						SESSION_TEXT = marksDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]

						YEAR_STATUS = (marksDiv.findChildren('div')[0].findChildren('span')[2].text)
						YEAR_MARKS = (marksDiv.findChildren('div')[0].findChildren('span')[3].text)
						AUC_STATUS = (marksDiv.findChildren('div')[0].findChildren('span')[5].text)

						cop=""
						if 'COP' in marksDiv.findChildren('div')[0].text:
							ind2 = marksDiv.findChildren('div')[0].text.find('COP : ')
							cop = marksDiv.findChildren('div')[0].text[ind2+6:]

						ind1 = AUC_STATUS.find('AUC Status : ')
						ind2 = AUC_STATUS.find(' AUC2 Status : ')
						auc_status = AUC_STATUS[ind1+13:ind2]
						auc2_status = AUC_STATUS[ind2+15:]

						sem_li=CURRENT_SEM.split(',')
						if semester not in sem_li:
							marksDiv=marksDiv.next_sibling
							continue

					flag = 0
					marksNextDiv = marksDiv.next_sibling
					NEXT_SESSION=''
					while marksNextDiv and flag == 0:
						if marksNextDiv.name == 'div':
							NEXT_SESSION = marksNextDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]
							NEXT_SEM = marksNextDiv.findChildren('div')[0].findChildren('span')[1].text
							if NEXT_SESSION == 'BACK' and CURRENT_SEM==NEXT_SEM:

								flag = 1
						marksNextDiv = marksNextDiv.next_sibling
					if flag == 1:
						marksDiv=marksDiv.next_sibling
						continue
					marksPrevDiv = marksDiv.previous_sibling
					if SESSION_TEXT == 'BACK':
						while marksPrevDiv:
							if marksPrevDiv.name == 'div':
								PREV_SESSION = marksPrevDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]
								PREV_SEM = marksPrevDiv.findChildren('div')[0].findChildren('span')[1].text

								if PREV_SESSION == 'REGULAR' and CURRENT_SEM==PREV_SEM:
									SESSION = marksPrevDiv.findChildren('div')[0].findChildren('span')[0].text[10:17]
							marksPrevDiv = marksPrevDiv.previous_sibling
					semtd = marksDiv.findChildren('div')[1].find_all('div',{'class': 'col-md-6'})
					m=0
					for ss in semtd :
						sem1td=ss.findChildren("table")[0]
						if sem1td.name == 'table':
							SEMESTER = sem1td.findChildren('span')[1].text
							if SEMESTER=='':
								return

							if semester != SEMESTER:
								continue

							STATUS = unicodedata.normalize('NFKD',sem1td.findChildren('tr')[3].findChildren('td')[2].text.strip()).encode('ascii','ignore')

							for subtr in  sem1td.findChildren('tr')[5].findChildren('table')[1].findChildren('tr')[1:]:
								SUB_CODE = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[0].text.strip()).encode('ascii','ignore')[:10]).replace("b","").replace("'","")
								SUB_NAME = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[1].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_TYPE = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[2].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_INTERNAL = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[3].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_EXTERNAL = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[4].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_BACK = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[5].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								CREDIT = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[6].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")

								qry_sub_insert = Subjectdetails.objects.using(db_name).update_or_create(branch_id=Branchdetails.objects.using(db_name).get(id=qry_branch_id[0]['id']),course_id=Coursedetails.objects.using(db_name).get(id=qry_course_insert[0].id),sem=semester,sub_code=SUB_CODE,type=SUB_TYPE,defaults={'sub_name':SUB_NAME,'max_university_marks':max_external_marks,'max_internal_marks':max_internal_marks})

								qry_marks_insert = Studentmarks.objects.using(db_name).update_or_create(uniq_id=Studentprimdetail.objects.using(db_name).get(uniq_id=qry_primdetail_insert[0].uniq_id),subject_id=Subjectdetails.objects.using(db_name).get(id=qry_sub_insert[0].id),defaults={'internal_marks':SUB_INTERNAL,'external_marks':SUB_EXTERNAL,'back_marks':SUB_BACK,'credit':CREDIT})

					qry_update_status = Studentprimdetail.objects.using(db_name).filter(uniq_id=qry_primdetail_insert[0].uniq_id).update(resultstatus=YEAR_STATUS)

				marksDiv=marksDiv.next_sibling

			time.sleep(2)
			index+=1

	return functions.RESPONSE(statusMessages.MESSAGE_SUCCESS,statusCodes.STATUS_SUCCESS)


def kiet_script_test(request):
	try:
		session_name = '1819e'
		cookie = '_ga=GA1.3.1610272396.1535472722; _gid=GA1.3.1906532346.1561990857; _gat=1; ASP.NET_SessionId=jjxwhpjdbecpaa3oxjjirdmy; User=User=3SheT0SbF/+sfaV6EjIPPQ==; Pass=Pass=4WXUWZnZZ54/RT5XX1NN7A==; AuthToken=9378e373-fabe-4782-b1ec-5b772f7ab1bc'
		StudentUniversityMarks = generate_session_table_name("StudentUniversityMarks_",session_name)
		SubjectInfo=generate_session_table_name("SubjectInfo_",session_name)
		studentSession=generate_session_table_name("studentSession_",session_name)

		# student_entered_marks=StudentUniversityMarks.objects.values_list('uniq_id',flat=True)

		qry_students = studentSession.objects.filter(year=4,uniq_id__dept_detail__course=13).exclude(uniq_id__in=studentSession.objects.filter(Q(uniq_id__admission_status__value="WITHDRAWAL") | Q(uniq_id__admission_status__value="FAILED") | Q(uniq_id__admission_status__value="PASSED") |  Q(uniq_id__admission_status__value__contains="EX") | Q(uniq_id__uni_roll_no__isnull=True)).values_list('uniq_id',flat=True)).values('uniq_id','uniq_id__uni_roll_no','section__sem_id__sem','section__sem_id','sem__dept__course')


		for students in qry_students:
			print(students['uniq_id__uni_roll_no'])
			print(students['section__sem_id'])
			qry_sem_subjects = SubjectInfo.objects.filter(sem_id=students['section__sem_id']).exclude(status='DELETE').values('id','sub_alpha_code','sub_num_code','subject_type__value')
			print(qry_sem_subjects)
			for sub in qry_sem_subjects:
				sub['sub_alpha_code'].replace(" ","")
				sub['sub_num_code'].replace(" ","")
				if 'GP' in sub['sub_alpha_code']:
					sub['sub_type']='GP'
				else:
					if sub['subject_type__value'] =='LAB':
						sub['sub_type']='Practical'
					else:
						sub['sub_type'] = 'Theory'

			time.sleep(2)
			re = requests.post("https://erp.aktu.ac.in/WebPages/OneView/OneView.aspx", data={'__VIEWSTATE': '/wEPDwUKLTY3NDIyMzIxOGRkzzJFpByKgv5wI2dl2lWIbUGF4Tw=', '__VIEWSTATEGENERATOR': '309C3D50', 'btnSearch': 'Search','txtRollNo':str(students['uniq_id__uni_roll_no'])},headers={'Content-Type':'application/x-www-form-urlencoded','Upgrade-Insecure-Requests':'1','Accept-Encoding':'gzip, deflate, br','Accept-Language':'en-GB,en-US;q=0.9,en;q=0.8','Cookie':cookie,'User-Agent':'test','Origin':'https://erp.aktu.ac.in','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer':'https://erp.aktu.ac.in/WebPages/OneView/OneView.aspx'})

			r=re.content
			response = r
			f= open("guru99.html","wb")
			f.write(response)
			f.close()
			soup = BeautifulSoup(r, "html.parser")

			div=soup.find("div",{"id": "pnlContent"})

			################### NECESSARY FOR FINDING ONLY LEVEL ONE TABLES ################################################
			tables_level_1=[]
			print(soup, "duv", div)
			for table in div.find_all('table'):
				if table.parent.get('id') == 'pnlContent':
					tables_level_1.append(table)
			print(len(tables_level_1))
			###########################################################################################################################

			COLLEGE_CODE = unicodedata.normalize('NFKD',soup.find(id="lblInstitute").text[1:4].strip()).encode('ascii','ignore')
			rollno = unicodedata.normalize('NFKD',soup.find(id="lblRollNo").text.strip()).encode('ascii','ignore')
			COLLEGE_NAME = unicodedata.normalize('NFKD',soup.find(id="lblInstitute").text[6:].strip()).encode('ascii','ignore')
			COURSE_CODE = unicodedata.normalize('NFKD',soup.find(id="lblCourse").text[1:3].strip()).encode('ascii','ignore')
			COURSE_NAME = unicodedata.normalize('NFKD',soup.find(id="lblCourse").text[5:].strip()).encode('ascii','ignore')
			BRANCH_CODE = unicodedata.normalize('NFKD',soup.find(id="lblBranch").text[1:3].strip()).encode('ascii','ignore')
			BRANCH_NAME = unicodedata.normalize('NFKD',soup.find(id="lblBranch").text[5:].strip()).encode('ascii','ignore')
			ENROLLMENT_NO = unicodedata.normalize('NFKD',soup.find(id="lblEnrollmentNo").text.strip()).encode('ascii','ignore')
			NAME = unicodedata.normalize('NFKD',soup.find(id="lblFullName").text.strip()).encode('ascii','ignore')
			FATHERS_NAME = unicodedata.normalize('NFKD',soup.find(id="lblFatherName").text.strip()).encode('ascii','ignore')

			print(COLLEGE_CODE,rollno,COLLEGE_NAME,COURSE_CODE,COURSE_NAME,BRANCH_CODE,BRANCH_NAME,ENROLLMENT_NO,NAME,FATHERS_NAME)

			marksDivArr = tables_level_1[1].findChildren('tr')[1].findChildren('td')[0].findChildren('div')

			marksDiv = marksDivArr[0]
			global flag
			flag=0
			while marksDiv:
				if type(marksDiv) is bs4.element.Tag:
					pass
					# print(marksDiv, str(type(marksDiv)))
					# return
				else:
					# print("marksDiv")
					marksDiv=marksDiv.next_sibling
					continue
				if marksDiv.name == 'div':
					print(flag)
					if flag == 0:
						SESSION = marksDiv.findChildren('div')[0].findChildren('span')[0].text[10:17]
						CURRENT_SEM = marksDiv.findChildren('div')[0].findChildren('span')[1].text
						SESSION_TEXT = marksDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]

						YEAR_STATUS = (marksDiv.findChildren('div')[0].findChildren('span')[2].text)
						YEAR_MARKS = (marksDiv.findChildren('div')[0].findChildren('span')[3].text)
						AUC_STATUS = (marksDiv.findChildren('div')[0].findChildren('span')[5].text)
						print(SESSION,CURRENT_SEM,SESSION_TEXT,YEAR_STATUS,YEAR_MARKS,AUC_STATUS)
						cop=""
						if 'COP' in marksDiv.findChildren('div')[0].text:
							ind2 = marksDiv.findChildren('div')[0].text.find('COP : ')
							cop = marksDiv.findChildren('div')[0].text[ind2+6:]

						ind1 = AUC_STATUS.find('AUC Status : ')
						ind2 = AUC_STATUS.find(' AUC2 Status : ')
						auc_status = AUC_STATUS[ind1+13:ind2]
						auc2_status = AUC_STATUS[ind2+15:]

						sem_li=CURRENT_SEM.split(',')
						if str(students['section__sem_id__sem']) not in sem_li:
							marksDiv=marksDiv.next_sibling
							# print(marksDiv, sem_li)
							continue
					flag = 0
					marksNextDiv = marksDiv.next_sibling
					NEXT_SESSION=''
					while marksNextDiv and flag == 0:
						if type(marksNextDiv) is bs4.element.Tag:
							pass
						else:
							marksNextDiv=marksNextDiv.next_sibling
							continue
						if marksNextDiv.name == 'div':
							NEXT_SESSION = marksNextDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]
							NEXT_SEM = marksNextDiv.findChildren('div')[0].findChildren('span')[1].text
							if NEXT_SESSION == 'BACK' and CURRENT_SEM==NEXT_SEM:

								flag = 1
						marksNextDiv = marksNextDiv.next_sibling
					if flag == 1:
						marksDiv=marksDiv.next_sibling
						continue
					marksPrevDiv = marksDiv.previous_sibling
					if SESSION_TEXT == 'BACK':
						while marksPrevDiv:
							if marksPrevDiv.name == 'div':
								PREV_SESSION = marksPrevDiv.findChildren('div')[0].findChildren('span')[0].text[18:-1]
								PREV_SEM = marksPrevDiv.findChildren('div')[0].findChildren('span')[1].text

								if PREV_SESSION == 'REGULAR' and CURRENT_SEM==PREV_SEM:
									SESSION = marksPrevDiv.findChildren('div')[0].findChildren('span')[0].text[10:17]
							marksPrevDiv = marksPrevDiv.previous_sibling
					semtd = marksDiv.findChildren('div')[1].find_all('div',{'class': 'col-md-6'})
					m=0

					for ss in semtd :
						sem1td=ss.findChildren("table")[0]
						if sem1td.name == 'table':
							SEMESTER = sem1td.findChildren('span')[1].text
							if SEMESTER=='':
								continue

							if str(students['section__sem_id__sem']) != SEMESTER:
								continue

							STATUS = unicodedata.normalize('NFKD',sem1td.findChildren('tr')[3].findChildren('td')[2].text.strip()).encode('ascii','ignore')

							student_sub=qry_sem_subjects[:]
							student_sub_marks = []

							for subtr in  sem1td.findChildren('tr')[5].findChildren('table')[1].findChildren('tr')[1:]:
								SUB_CODE = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[0].text.strip()).encode('ascii','ignore')[:10]).replace("b","").replace("'","")
								SUB_NAME = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[1].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_TYPE = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[2].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								# if (SUB_TYPE=='Practical'):
								# 	print("inn")
								# 	SUB_TYPE='LAB'
								SUB_INTERNAL = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[3].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_EXTERNAL = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[4].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								SUB_BACK = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[5].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")
								CREDIT = str(unicodedata.normalize('NFKD',subtr.findChildren('td')[6].text.strip()).encode('ascii','ignore')).replace("b","").replace("'","")

								student_sub_marks.append({'sub_code':SUB_CODE,'sub_type':SUB_TYPE,'internal':SUB_INTERNAL,'external':SUB_EXTERNAL,'back':SUB_BACK,'sub_name':SUB_NAME,'credit':CREDIT})

							########################## stored alpha code=BOP, stored num code=471 & sub code from aktu = BOP471 ######
							############# CHECK if 'BOP' present in 'BOP471' and '471' present in 'BOP471' #####################

							n2 = len(student_sub_marks)

							index_to_delete = []
							print(student_sub)
							print(student_sub_marks)
							for i in range(n2):
								for j in range(len(student_sub)):
									if (student_sub[j]['sub_alpha_code'] in student_sub_marks[i]['sub_code']) and (student_sub[j]['sub_num_code'] in student_sub_marks[i]['sub_code']) and (student_sub[j]['sub_type'].upper() == student_sub_marks[i]['sub_type'].upper()):

										external=(student_sub_marks[i]['external'])
										internal=(student_sub_marks[i]['internal'])
										print("1")
										l=StudentUniversityMarks.objects.update_or_create(uniq_id=studentSession.objects.get(uniq_id=students['uniq_id']),subject_id=SubjectInfo.objects.get(id=student_sub[j]['id']),defaults={'external_marks':external,'internal_marks':internal,'added_by':EmployeePrimdetail.objects.get(emp_id='00007')})
										print(l)
										del student_sub[j]
										index_to_delete.append(i)
										break


							for ind in sorted(index_to_delete, reverse=True):
								del student_sub_marks[ind]

							########################## stored alpha code=BOPP, stored num code=471 & sub code from aktu = BOP471P ######
							############# CHECK if 'BOP' (remove last character from stored alpha code i.e 'P') present in 'BOP471' and '471' present in 'BOP471' #####################

							n2 = len(student_sub_marks)

							index_to_delete = []

							for i in range(n2):
								for j in range(len(student_sub)):

									if (student_sub[j]['sub_alpha_code'][:-1] in student_sub_marks[i]['sub_code']) and (student_sub[j]['sub_num_code'] in student_sub_marks[i]['sub_code']) and (student_sub[j]['sub_type'].upper() == student_sub_marks[i]['sub_type'].upper()):

										external=(student_sub_marks[i]['external'])

										internal=(student_sub_marks[i]['internal'])
										print("2")
										StudentUniversityMarks.objects.update_or_create(uniq_id=studentSession.objects.get(uniq_id=students['uniq_id']),subject_id=SubjectInfo.objects.get(id=student_sub[j]['id']),defaults={'external_marks':external,'internal_marks':internal,'added_by':EmployeePrimdetail.objects.get(emp_id='00007')})
										print("3")
										del student_sub[j]
										index_to_delete.append(i)
										break

							for ind in sorted(index_to_delete, reverse=True):
								del student_sub_marks[ind]
				marksDiv=marksDiv.next_sibling

	except Exception as e:
		print(e)
	return functions.RESPONSE(statusMessages.MESSAGE_SUCCESS,statusCodes.STATUS_SUCCESS)
