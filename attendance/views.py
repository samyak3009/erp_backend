from __future__ import division
import json

from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse
from datetime import date, timedelta,datetime
import time
import datetime
from django.db.models import Q,Avg,Max,Min,Sum
import requests
import calendar
from dateutil.relativedelta import relativedelta

from .models import machinerecords,EmployeePrimdetail,Attendance2,EmployeeDropdown
from musterroll.models import Shifts,Reporting
from login.models import LogRecord
from leave.models import Holiday,LeaveType,Leaves

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, requestMethod, functions

from leave.views import check_leave_status,check_month_locked,calculate_working_days
from login.views import check,checkpermission,my_view
from itertools import groupby

# Create your views here.
def statsreport(request):
	Emp_Id='10636'
	fdate=datetime.date(2017,12,1)
	tdate=datetime.date(2018,1,1)
	employee_avg_time(fdate,tdate,Emp_Id)

def employee_avg_time(fdate,tdate,Emp_Id):

	final=0
	qry1=Attendance2.objects.filter(Emp_Id=Emp_Id,date__range=[fdate,tdate]).exclude(status='H').values('work')
	n=qry1.count()
	for att in qry1:
		####print(att)
		final=final+int(att['work'].hour*60*60+att['work'].minute*60+att['work'].second)
	final=final/n

	hours=int(final/3600)
	####print(float(final/3600))
	minutes1=(final/3600)-int(final/3600)
	minutes=int(minutes1*60)
	sec=minutes1*60-int(minutes1*60)
	sec=int(sec*60)
	####print(datetime.time(hours,minutes,sec))
	return 1

def dailyEmpsummary(request):
	####print(request.GET['check'])
	if(request.GET['check']=='0'):
		date=datetime.date.today()
	else:
		date=request.GET['date']
	####print(date)


	qry=EmployeeDropdown.objects.filter(sno=169).values('field').values()
	qry1=EmployeeDropdown.objects.filter(field=qry[0]['field']).exclude(sno=169).values('sno','value')

	head1=[]
	dept=[]
	present=[]
	absent=[]
	totalP=[]
	totalA=[]


	for head in qry1:
		head1.append(head['value']+"(Present)")
		head1.append(head['value']+"(Absent)")
		totalP.append(0)
		totalP.append(0)



	qry_dept=EmployeeDropdown.objects.filter(pid=552,value__isnull=False).values('sno','value')
	i=0

	for dept1 in qry_dept:
		dept.append(dept1['value'])
		present.append([])
		absent.append([])
		j=0
		for head in qry1:
			####print(date)
			qry_present=Attendance2.objects.filter(Emp_Id__emp_category=head['sno'],Emp_Id__dept=dept1['sno'],date=date).exclude(Q(status='A') | Q(status='H')).count()
			####print("dsadsadsadasdsdadsasadsadsad")
			####print(qry_present)
			qry_absent=Attendance2.objects.filter(Emp_Id__emp_category=head['sno'],Emp_Id__dept=dept1['sno'],date=date,status='A').count()
			present[i].append(qry_present)
			present[i].append(qry_absent)
			####print(present)

			totalP[j]=totalP[j]+qry_present
			totalP[j+1]=totalP[j+1]+qry_absent
			j=j+2

		i=i+1


	data={'dept':dept,'present':present,'absent':absent,'head':head1,'totalP':totalP,'totalA':totalA}
	status=200
	return JsonResponse(status=status,data=data)

def all_employee_data(request):
	error=True
	data=""
	msg=''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[211,1345])
			if check==200:
				if request.method == 'GET':
					s = EmployeePrimdetail.objects.exclude(emp_id="00007").extra(select={'emp_name':'name','emp_code':'emp_id'}).values('emp_name','emp_code').all()
					####print(s.query)
					msg="Success"
					error=False
					status=200
					data={'error':error,'msg':msg,'data':list(s)}

			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':data}
	return JsonResponse(status=status,data=data)

def employee_data(request):
	error=True
	data=""
	msg=''
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[211,1345])
			if check==200:
				if request.method == 'GET':
					s = EmployeePrimdetail.objects.filter(emp_status="ACTIVE").exclude(emp_id="00007").extra(select={'emp_name':'name','emp_code':'emp_id'}).values('emp_name','emp_code').all()
					####print(s.query)
					msg="Success"
					error=False
					status=200
					data={'error':error,'msg':msg,'data':list(s)}

				if request.method == 'POST':
					inp=json.loads(request.body.decode('utf-8'))

					if inp['leave'] == '1':
						emp_id=inp['emp_code']
						fdate=inp['fdate']
						tdate=inp['tdate']
						qry1 = EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept','dept__value','desg__value','name')
						dept1= qry1[0]['dept']
						qry2=EmployeeDropdown.objects.filter(sno=dept1,field="department").extra(select={'dept':'value'}).values('dept')
						final=emp_attendance(emp_id,fdate,tdate)
						dept=list(qry2)
						error=False
						msg="Success"
						status=200
						data={'s':final,'dept':qry1[0]['dept__value'],'desg':qry1[0]['desg__value'],'error':error,'msg':msg,'emp_id':emp_id,'name':qry1[0]['name']}
					if inp['leave'] == '2':
						print(inp)
						emp_id = int(inp['emp_code'])
						date = datetime.datetime.strptime(str(inp['date']), "%d-%m-%Y").strftime("%Y-%m-%d")
						status = inp['emp_status']

						status_li=['P','A','P/I','P/II','P/A','H']
						if status not in status_li:
							status='H'

						intime = inp['emp_intime']
						outtime = inp['emp_outtime']
						extra=inp['extra']
						shift1=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('shift')
						if shift1[0]['shift'] is not None:
							shift1=list(Shifts.objects.filter(shiftid=shift1[0]['shift'],status='INSERT').values('id'))
							shift_id=shift1[0]['id']
						else:
							shift_id=None
						if 'remark' in inp:

							upd_list={'status':status,'intime':intime,'outtime':outtime,'colstatus':'green','extra':extra,'remark':inp['remark'],'shift_id':shift_id}
							print(upd_list)

						else:  
							upd_list={'status':status,'intime':intime,'outtime':outtime,'colstatus':'green','extra':extra,'shift_id':shift_id}

						check11=check_month_locked(date,date)
						if check11 == True:
							status=202
							data={'msg' : "Payable days has been locked for the date selected"}
						else:
							print('inn')
							s=Attendance2.objects.filter(Emp_Id=emp_id).filter(date=date).update(**upd_list)
							if s:
								data={'msg':'Update Successful'}
							else:
								data = {'msg': 'Update Failed'}
							error=False
							msg="Success"
							status=200
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':data}
	return JsonResponse(status=status,data=data)

def singleperson_attendance(request):
	error=True
	final=[]
	msg=''

	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check=checkpermission(request,[337])
			if check==200:
				emp_id=request.session['hash1']
				fdate=request.GET['fdate']
				tdate=request.GET['tdate']

				final=emp_attendance(emp_id,fdate,tdate)

				summary = calculate_working_days(emp_id,fdate,tdate,"","")
				summary_data=[]
				summary_data.append( {"label": "Present", "data": summary['present']})
				summary_data.append( {"label": "Holiday", "data": summary['holiday']})
				summary_data.append( {"label": "Leave", "data": summary['leave']})
				summary_data.append( {"label": "Absent", "data": summary['absent']})
				summary_data.append( {"label": "Leave Non Countable", "data": summary['leave_nc']})
				
				final={'s':final,"summary":summary_data}
				
				status=200
			else:
				status=403
		else:
			status=401
	else:
		status=400
	data={'msg':msg,'data':final}
	return JsonResponse(status=status,data=data)

def emp_attendance(emp_id,fdate,tdate):
	s = Attendance2.objects.filter(Emp_Id=emp_id).filter(date__range=[fdate, tdate]).extra(select={'emp_status':'Status','att_date':'date','emp_intime':'intime','emp_outtime':'outtime','latein':'late','earlyexit':'etime','extra':'extra','colstatus':'colstatus'}).values('emp_status','att_date','emp_intime','emp_outtime','latein','earlyexit','extra','colstatus','work','remark')
	final=[]
	for att in s:
		color='black'
	
		leave=''
		category=''
		subtype=''
		if(att['emp_status']!='P'):
			response = check_leave_status(emp_id,att['att_date'],att['emp_status'])
			if 'category' in response[6]:
				category=response[6]['category']
				subtype=response[6]['subtype']
			leave=response[1]

			if(response[0]==2):

				if response[2] == 'Y':
					leave=leave+" (0.5)"
					color='blue'

				else:
					leave=leave+" (0)"
					color='red'

			elif(response[0]==1):
				if response[2] == 'Y':
					leave=leave+" (1)"
					if att['colstatus'] == 'green':
						color='green'
					else:
						color='black'


				elif response[2] == 'N':
					leave=leave+" (0)"
					color='red'

				else:
					leave=leave+" (0.5)"
					color='red'
			else:
				color='red'

		if att['emp_status'] == 'H':
			color='orange'

			qry_dept=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('dept')
			qry_holi=Holiday.objects.filter(f_date__lte=att['att_date'],t_date__gte=att['att_date'],dept=qry_dept[0]['dept']).values('h_des')

			if len(qry_holi)>0:
				att['emp_status']=qry_holi[0]['h_des']
			else:
				att['emp_status']="Holiday"
		if att['colstatus'] == 'green':
			color='green'
		att['att_date']=datetime.datetime.strptime(str(att['att_date']), "%Y-%m-%d").strftime("%d-%m-%Y")
		data={
			'att_date':att['att_date'],
			'emp_status':att['emp_status'],
			'emp_intime':att['emp_intime'],
			'emp_outtime':att['emp_outtime'],
			'leave':leave,
			'earlyexit':att['earlyexit'],
			'latein':att['latein'],
			'extra':att['extra'],
			'colstatus':color,
			'work_hours':att['work'],
			'remark':att['remark'],
			#'colstatus':att['colstatus']
			'category': category,
			'subtype': subtype
			}
		final.append(data)
	   
	return final
def add_hours(t1,t2):

	sec=t2.hour*3600+t2.minute*60+t2.second
	delta = datetime.timedelta(seconds = sec)
	k=(datetime.datetime.combine(datetime.date(1,1,1),t1) + delta).time()
	return k


def night_shift(date,emp_id,qry3,qry4):
	checktime=datetime.time(12,0,0) ##time between which night shift to be check
	nextday=date + timedelta(days = 1) ## next day date
	timestamp1=str(date)+" "+str(checktime)
	timestamp1=datetime.datetime.strptime(timestamp1,"%Y-%m-%d %H:%M:%S") ##conversion into time stamp of present date
	timestamp2=str(nextday)+" "+str(checktime)
	timestamp2=datetime.datetime.strptime(timestamp2,"%Y-%m-%d %H:%M:%S") ##conversion into time stamp of nextday date
	qry0=machinerecords.objects.filter(Emp_Id=emp_id,timestamp__gte=timestamp1,timestamp__lte=timestamp2).order_by('date','time').values('id','time','date')
	##print(qry0.query)
	status=''
	data={'status':'1'}

	if(qry4.count()!=0):## shift is define or not
		qry_holiday=Holiday.objects.filter(dept=qry3[0]['dept']).filter(Q(f_date__lte=date) & Q(t_date__gte=date)).values('id') ## check holiday on date
		##print(qry_holiday.count())
		if(qry_holiday.count()==0): ##if no holiday
			if(qry3[0]['shift__field']=='NIGHT FLEXIBLE'):
				if(qry0.count()==0): ## if no punch than absent(A) status
					status='A'
					colstatus='red'
					data={'status':status,'intime':datetime.time(0,0,0),'outtime':datetime.time(0,0,0),'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				elif(qry0.count()==1):### If only one punch P/A status
					status='P/A'
					colstatus='blue'
					data={'status':status,'intime':qry0[0]['time'],'outtime':datetime.time(0,0,0),'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				elif(qry0.count() > 1):
				## if more than one punch on a day
					qry_in=machinerecords.objects.filter(Emp_Id=emp_id,timestamp__gte=timestamp1,timestamp__lte=timestamp2).values('id','date','time').order_by('date','time')[:1] ## get First punch of day
					qry_out=machinerecords.objects.filter(Emp_Id=emp_id,timestamp__gte=timestamp1,timestamp__lte=timestamp2).values('id','date','time').order_by('-date','-time')[:1] ## get last punch of day
					if(qry_in[0]['date']==qry_out[0]['date']):
						sec=((datetime.datetime.combine(datetime.date.today(), qry_out[0]['time']) - datetime.datetime.combine(datetime.date.today(), qry_in[0]['time'])).total_seconds())
						time=datetime.timedelta(seconds=sec)
						work_hour=(datetime.datetime.min + time).time()## calculate working hour

					else:
						sec=((datetime.datetime.combine(datetime.date.today(), datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), qry_in[0]['time'])).total_seconds())+1
						time=datetime.timedelta(seconds=sec)
						work_hour1=(datetime.datetime.min + time).time()## calculate working hour
						sec=((datetime.datetime.combine(datetime.date.today(), qry_out[0]['time']) - datetime.datetime.combine(datetime.date.today(), datetime.time(00,00,00))).total_seconds())
						time=datetime.timedelta(seconds=sec)
						work_hour2=(datetime.datetime.min + time).time()## calculate working hour
						work_hour=add_hours(work_hour1,work_hour2)

					if(work_hour< qry4[0]['halfdaytime']): ##if working hours less than half day working
						status='P/A'
						colstatus='blue'
					elif(qry4[0]['halfdaytime']<=work_hour and work_hour<qry4[0]['fulldaytime']): ##if working hours greater than or equal to half day working and less than full day working
						status='P/I'
						colstatus='blue'
					elif(work_hour>=qry4[0]['fulldaytime']): ## if woinp=json.loads(request.body.decode('utf-8'))rking hour greater than fullday hours
						status='P'
						colstatus='black'
				data={'status':status,'intime':qry_in[0]['time'],'outtime':qry_out[0]['time'],'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':work_hour,'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				### END OF FLEXIBLE NIGHT
			else:
				if(qry0.count()==0): ## if no punch than absent(A) status
					status='A'
					colstatus='red'
					data={'status':status,'intime':datetime.time(0,0,0),'outtime':datetime.time(0,0,0),'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				elif(qry0.count()==1):### If only one punch P/A status
					status='P/A'
					colstatus='blue'

					if(qry0[0]['time']<=qry4[0]['latein'] and date == qry0[0]['date']): ## if before late in time
						latein=datetime.time(0,0,0)
					else:## if after late in time

						if(qry0[0]['time'] < datetime.time(0,0,0)):
							latesec=((datetime.datetime.combine(datetime.date.today(), qry0[0]['time']) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())
							latetime=datetime.timedelta(seconds=latesec)
							latein=(datetime.datetime.min + latetime).time()

						else:

							latesec=((datetime.datetime.combine(datetime.date.today(), datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())+1
							latetime=datetime.timedelta(seconds=latesec)
							latein1=(datetime.datetime.min + latetime).time()
							latesec=((datetime.datetime.combine(datetime.date.today(), qry0[0]['time']) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
							latetime=datetime.timedelta(seconds=latesec)
							latein2=(datetime.datetime.min + latetime).time()
							latein=add_hours(latein1,latein2)


					data={'status':status,'intime':qry0[0]['time'],'outtime':datetime.time(0,0,0),'latein':latein,'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				elif(qry0.count() > 1):
					## if more than one punch on a day
					qry_in=machinerecords.objects.filter(Emp_Id=emp_id,timestamp__gte=timestamp1,timestamp__lte=timestamp2).values('id','date','time').order_by('date','time')[:1] ## get First punch of day
					qry_out=machinerecords.objects.filter(Emp_Id=emp_id,timestamp__gte=timestamp1,timestamp__lte=timestamp2).values('id','date','time').order_by('-date','-time')[:1] ## get last punch of day
					if(qry_in[0]['time']<qry4[0]['intime'] and qry_out[0]['time']<qry4[0]['intime'] and qry_in[0]['date']==date and qry_out[0]['date']==date): ### if punch IN AND PUNCH out time is less Than In shift in Time

						earlysect=((datetime.datetime.combine(datetime.date.today(),datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), qry4[0]['intime'])).total_seconds())+1
						earlytimet=datetime.timedelta(seconds=earlysect)
						earlyexit1=(datetime.datetime.min + earlytimet).time()

						earlysect=((datetime.datetime.combine(datetime.date.today(),qry4[0]['earlyexit']) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
						earlytimet=datetime.timedelta(seconds=earlysect)
						earlyexit2=(datetime.datetime.min + earlytimet).time()
						earlyexit=add_hours(earlyexit1,earlyexit2)
						data={'status':'P/A','intime':qry_in[0]['time'],'outtime':qry_out[0]['time'],'latein':datetime.time(0,0,0),'earlyexit':earlyexit,'colstatus':'blue','work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}

					elif(qry_in[0]['time']>qry4[0]['outtime'] and qry_out[0]['time']>qry4[0]['outtime'] and qry_in[0]['date']==nextday and qry_out[0]['date'] == nextday):##if punch IN AND PUNCH out time is greater than Than Shift out Time

						latesect=((datetime.datetime.combine(datetime.date.today(), datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())+1
						latetimet=datetime.timedelta(seconds=latesect)
						lateint1=(datetime.datetime.min + latetimet).time()

						latesect=((datetime.datetime.combine(datetime.date.today(), qry_in[0]['time']) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
						latetimet=datetime.timedelta(seconds=latesect)
						lateint2=(datetime.datetime.min + latetimet).time()
						lateint=add_hours(lateint1,lateint2)
						data={'status':'P/A','intime':qry_in[0]['time'],'outtime':qry_out[0]['time'],'latein':lateint,'earlyexit':datetime.time(0,0,0),'colstatus':'blue','work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}

					else:

						if(qry_in[0]['time']<=qry4[0]['intime'] and date == qry_in[0]['date']): ## if punch in time is less than or equal to shift in time
							employee_intime=qry4[0]['intime'] ## assign shift in time

						else:   ## if punch in time is grater than shift in inp=json.loads(request.body.decode('utf-8'))time
							employee_intime=qry_in[0]['time']## assign punch in time

						if(qry_out[0]['time']>=qry4[0]['outtime'] and nextday == qry_in[0]['date']):# if punch out time is greater than or equal to shift  out
							employee_outtime=qry4[0]['outtime']## assign shift out time
						else:   ## if punch out time is less than shift out timenow = dt.datetime.now()
							employee_outtime=qry_out[0]['time']## assign punch out time
						if(qry_in[0]['date']==qry_out[0]['date']):
							sec=((datetime.datetime.combine(datetime.date.today(), employee_outtime) - datetime.datetime.combine(datetime.date.today(), employee_intime)).total_seconds())
							time=datetime.timedelta(seconds=sec)
							work_hour=(datetime.datetime.min + time).time()## calculate working hour
						else:
							sec=((datetime.datetime.combine(datetime.date.today(), datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), employee_intime)).total_seconds())+1
							time=datetime.timedelta(seconds=sec)
							work_hour1=(datetime.datetime.min + time).time()## calculate working hour

							sec=((datetime.datetime.combine(datetime.date.today(), employee_outtime) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
							time=datetime.timedelta(seconds=sec)
							work_hour2=(datetime.datetime.min + time).time()## calculate working hour
							work_hour=add_hours(work_hour1,work_hour2)
						##print(work_hour)
						##sec2=qry4[0]['halfdaytime'].hour*3600+qry4[0]['halfdaytime'].minute*60+qry4[0]['halfdaytime'].second
						##delta=datetime.timedelta(seconds=sec2)
						##shifthaltime=(datetime.datetime.combine(datetime.dinp=json.loads(request.body.decode('utf-8'))ate(1,1,1),qry4[0]['intime']) + delta).time()  ##calculate half day time according to shifts

						if(work_hour< qry4[0]['halfdaytime']): ##if working hours less than half day working
							status='P/A'
							colstatus='blue'
						elif(qry4[0]['halfdaytime']<=work_hour and work_hour<qry4[0]['fulldaytime']): ##if working hours greater than or equal to half day working and less than full day working
							if(employee_intime<=qry4[0]['latein']): ## if punch in first half
								status='P/I'
								colstatus='blue'
							elif(employee_outtime>=qry4[0]['earlyexit']):##if punch in Second half
								status='P/II'
								colstatus='blue'
							else:

								if(employee_intime>datetime.time(0,0,0)):
									secearlydiff=((datetime.datetime.combine(datetime.date.today(), datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())+1
									timeearlydiff=datetime.timedelta(seconds=secearlydiff)
									earlydiff1=(datetime.datetime.min + timeearlydiff).time()

									secearlydiff=((datetime.datetime.combine(datetime.date.today(), employee_intime) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
									timeearlydiff=datetime.timedelta(seconds=secearlydiff)
									earlydiff2=(datetime.datetime.min + timeearlydiff).time()
									earlydiff=add_hours(earlydiff1,earlydiff2)

								else:
									secearlydiff=((datetime.datetime.combine(datetime.date.today(), employee_intime) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())
									timeearlydiff=datetime.timedelta(seconds=secearlydiff)
									earlydiff=(datetime.datetime.min + timeearlydiff).time()

								if(employee_outtime<datetime.time(0,0,0)):
									seclatediff=((datetime.datetime.combine(datetime.date.today(), datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), employee_outtime)).total_seconds())
									timelatediff=datetime.timedelta(seconds=seclatediff)
									latediff1=(datetime.datetime.min + timelatediff).time()

									seclatediff=((datetime.datetime.combine(datetime.date.today(), qry4[0]['earlyexit']) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
									timelatediff=datetime.timedelta(seconds=seclatediff)
									latediff2=(datetime.datetime.min + timelatediff).time()
									latediff=add_hours(latediff1+latediff2)

								else:
									seclatediff=((datetime.datetime.combine(datetime.date.today(), qry4[0]['earlyexit']) - datetime.datetime.combine(datetime.date.today(), employee_outtime)).total_seconds())
									timelatediff=datetime.timedelta(seconds=seclatediff)
									latediff=(datetime.datetime.min + timelatediff).time()
								if(earlydiff<=latediff):
									status='P/I'
									colstatus='blue'
								else:
									status='P/II'
									colstatus='blue'
						elif(work_hour>=qry4[0]['fulldaytime']): ## if working hour greater than fullday hours
							status='P'
							colstatus='black'
						if(employee_intime<=qry4[0]['latein'] and date == qry_in[0]['date']):
							latein=datetime.time(0,0,0)
						else:
							if(employee_intime <= datetime.time(23,59,59) and date == qry_in[0]['date']):

								latesec=((datetime.datetime.combine(datetime.date.today(), employee_intime) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())
								latetime=datetime.timedelta(seconds=latesec)
								latein=(datetime.datetime.min + latetime).time()


							else:

								latesec=((datetime.datetime.combine(datetime.date.today(), datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())+1
								latetime=datetime.timedelta(seconds=latesec)
								latein1=(datetime.datetime.min + latetime).time()
								latesec=((datetime.datetime.combine(datetime.date.today(), employee_intime) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
								latetime=datetime.timedelta(seconds=latesec)
								latein2=(datetime.datetime.min + latetime).time()
								latein=add_hours(latein1,latein2)
						if(employee_outtime>=qry4[0]['earlyexit'] and nextday == qry_out[0]['date']):
							earlyexit=datetime.time(0,0,0)
						else:
							if(employee_outtime>=datetime.time(0,0,0) and nextday == qry_out[0]['date']):

								earlysec=((datetime.datetime.combine(datetime.date.today(),qry4[0]['earlyexit']) - datetime.datetime.combine(datetime.date.today(), employee_outtime)).total_seconds())
								earlytime=datetime.timedelta(seconds=earlysec)
								earlyexit=(datetime.datetime.min + earlytime).time()
							else:

								earlysec=((datetime.datetime.combine(datetime.date.today(),datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), employee_outtime)).total_seconds())+1
								earlytime=datetime.timedelta(seconds=earlysec)
								earlyexit1=(datetime.datetime.min + earlytime).time()
								##print(earlyexit1)
								earlysec=((datetime.datetime.combine(datetime.date.today(),qry4[0]['earlyexit']) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
								earlytime=datetime.timedelta(seconds=earlysec)
								earlyexit2=(datetime.datetime.min + earlytime).time()
								earlyexit=add_hours(earlyexit1,earlyexit2)

						data={'status':status,'intime':qry_in[0]['time'],'outtime':qry_out[0]['time'],'latein':latein,'earlyexit':earlyexit,'colstatus':colstatus,'work_hour':work_hour,'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
		else:
			status='H'
			qry_in=machinerecords.objects.filter(Emp_Id=emp_id,timestamp__gte=timestamp1,timestamp__lte=timestamp2).values('id','date','time').order_by('date','time')[:1] ## get First punch of day
			qry_out=machinerecords.objects.filter(Emp_Id=emp_id,timestamp__gte=timestamp1,timestamp__lte=timestamp2).values('id','date','time').order_by('-date','-time')[:1] ## get last punch of day
			if( qry0.count()>0):
				if(qry_in[0]['date']==qry_out[0]['date']):
					sec=((datetime.datetime.combine(datetime.date.today(), qry_out[0]['time']) - datetime.datetime.combine(datetime.date.today(), qry_in[0]['time'])).total_seconds())
					time=datetime.timedelta(seconds=sec)
					work_hour=(datetime.datetime.min + time).time()## calculate working hour
				else:
					sec=((datetime.datetime.combine(datetime.date.today(), datetime.time(23,59,59)) - datetime.datetime.combine(datetime.date.today(), qry_in[0]['time'])).total_seconds())+1
					time=datetime.timedelta(seconds=sec)
					work_hour1=(datetime.datetime.min + time).time()## calculate working hour

					sec=((datetime.datetime.combine(datetime.date.today(), qry_out[0]['time']) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0))).total_seconds())
					time=datetime.timedelta(seconds=sec)
					work_hour2=(datetime.datetime.min + time).time()## calculate working hour
					work_hour=add_hours(work_hour1,work_hour2)
				intime=qry_in[0]['time']
				outime=qry_out[0]['time']

			else:
				work_hour=datetime.time(0,0,0)## calculate working hour
				intime=datetime.time(0,0,0)
				outime=datetime.time(0,0,0)
			data=data={'status':status,'intime':intime,'outtime':outime,'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':'red','work_hour':work_hour,'emp_id':emp_id,'extrahours':work_hour}
	return data

def mainscript(date,emp_id,qry3,qry4):

	qry0=machinerecords.objects.filter(Emp_Id=emp_id,date=date).values('id','time') ##check no of punch in machne records on  date
	status=''
	data={'status':'1'}

	if(qry4.count()!=0):
		qry_holiday=Holiday.objects.filter(dept=qry3[0]['dept']).filter(Q(f_date__lte=date) & Q(t_date__gte=date)).values('id','restricted') ## check holiday on date
		if(qry_holiday.count()==0): ##if no holiday

			if(qry3[0]['shift__field']=='FLEXIBLE'):


				if(qry0.count()==0): ## if no punch than absent(A) status
					status='A'
					colstatus='red'
					data={'status':status,'intime':datetime.time(0,0,0),'outtime':datetime.time(0,0,0),'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				elif(qry0.count()==1):### If only one punch P/A status
					status='P/A'
					colstatus='blue'
					data={'status':status,'intime':qry0[0]['time'],'outtime':datetime.time(0,0,0),'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				elif(qry0.count() > 1):
					## if more than one punch on a day
					qry_in=machinerecords.objects.filter(Emp_Id=emp_id,date=date).values('id','time').order_by('time')[:1] ## get First punch of day
					qry_out=machinerecords.objects.filter(Emp_Id=emp_id,date=date).values('id','time').order_by('-time')[:1] ## get last punch of day
					sec=((datetime.datetime.combine(datetime.date.today(), qry_out[0]['time']) - datetime.datetime.combine(datetime.date.today(), qry_in[0]['time'])).total_seconds())
					time=datetime.timedelta(seconds=sec)
					work_hour=(datetime.datetime.min + time).time()## calculate working hour

					if(work_hour< qry4[0]['halfdaytime']): ##if working hours less than half day working
						status='P/A'
						colstatus='blue'
					elif(qry4[0]['halfdaytime']<=work_hour and work_hour<qry4[0]['fulldaytime']): ##if working hours greater than or equal to half day working and less than full day working

							status='P/I'
							colstatus='blue'
					elif(work_hour>=qry4[0]['fulldaytime']): ## if woinp=json.loads(request.body.decode('utf-8'))rking hour greater than fullday hours
						status='P'
						colstatus='black'
					data={'status':status,'intime':qry_in[0]['time'],'outtime':qry_out[0]['time'],'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':work_hour,'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}

			else:
				if(qry0.count()==0): ## if no punch than absent(A) status
					status='A'
					colstatus='red'
					data={'status':status,'intime':datetime.time(0,0,0),'outtime':datetime.time(0,0,0),'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				elif(qry0.count()==1):### If only one punch P/A status
					status='P/A'
					colstatus='blue'
					if(qry0[0]['time']<=qry4[0]['latein']): ## if before late in time
						latein=datetime.time(0,0,0)
					else:## if after late in time
						latesec=((datetime.datetime.combine(datetime.date.today(), qry0[0]['time']) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())
						latetime=datetime.timedelta(seconds=latesec)
						latein=(datetime.datetime.min + latetime).time()

					data={'status':status,'intime':qry0[0]['time'],'outtime':datetime.time(0,0,0),'latein':latein,'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
				elif(qry0.count() > 1):
					## if more than one punch on a day
					qry_in=machinerecords.objects.filter(Emp_Id=emp_id,date=date).values('id','time').order_by('time')[:1] ## get First punch of day
					qry_out=machinerecords.objects.filter(Emp_Id=emp_id,date=date).values('id','time').order_by('-time')[:1] ## get last punch of day
					if(qry_in[0]['time']<qry4[0]['intime'] and qry_out[0]['time']<qry4[0]['intime']): ### if punch IN AND PUNCH out time is less Than In shift in Time
						earlysect=((datetime.datetime.combine(datetime.date.today(),qry4[0]['earlyexit']) - datetime.datetime.combine(datetime.date.today(), qry4[0]['intime'])).total_seconds())
						earlytimet=datetime.timedelta(seconds=earlysect)
						earlyexitt=(datetime.datetime.min + earlytimet).time()
						data={'status':'P/A','intime':qry_in[0]['time'],'outtime':qry_out[0]['time'],'latein':datetime.time(0,0,0),'earlyexit':earlyexitt,'colstatus':'blue','work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}

					elif(qry_in[0]['time']>qry4[0]['outtime'] and qry_out[0]['time']>qry4[0]['outtime']):##if punch IN AND PUNCH out time is greater than Than Shift out Time
						latesect=((datetime.datetime.combine(datetime.date.today(), qry_in[0]['time']) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())
						latetimet=datetime.timedelta(seconds=latesect)
						lateint=(datetime.datetime.min + latetimet).time()
						data={'status':'P/A','intime':qry_in[0]['time'],'outtime':qry_out[0]['time'],'latein':lateint,'earlyexit':datetime.time(0,0,0),'colstatus':'blue','work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}

					else:

						if(qry_in[0]['time']<=qry4[0]['intime']): ## if punch in time is less than or equal to shift in time
							employee_intime=qry4[0]['intime'] ## assign shift in time

						else:   ## if punch in time is grater than shift in inp=json.loads(request.body.decode('utf-8'))time
							employee_intime=qry_in[0]['time']## assign punch in time

						if(qry_out[0]['time']>=qry4[0]['outtime']):# if punch out time is greater than or equal to shift  out
							employee_outtime=qry4[0]['outtime']## assign shift out time
						else:   ## if punch out time is less than shift out time
							employee_outtime=qry_out[0]['time']## assign punch out time

						sec=((datetime.datetime.combine(datetime.date.today(), employee_outtime) - datetime.datetime.combine(datetime.date.today(), employee_intime)).total_seconds())

						print(employee_intime,qry4[0]['intime'],employee_outtime,qry4[0]['outtime'],"hello")
						time=datetime.timedelta(seconds=sec)
						if(sec<0):
							status='A'
							colstatus='red'
							data={'status':status,'intime':datetime.time(0,0,0),'outtime':datetime.time(0,0,0),'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':colstatus,'work_hour':datetime.time(0,0,0),'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
							return data
						work_hour=(datetime.datetime.min + time).time()## calculate working hour
						##print(type(work_hour))
						##sec2=qry4[0]['halfdaytime'].hour*3600+qry4[0]['halfdaytime'].minute*60+qry4[0]['halfdaytime'].second
						##delta=datetime.timedelta(seconds=sec2)
						##shifthaltime=(datetime.datetime.combine(datetime.dinp=json.loads(request.body.decode('utf-8'))ate(1,1,1),qry4[0]['intime']) + delta).time()  ##calculate half day time according to shifts

						if(work_hour< qry4[0]['halfdaytime']): ##if working hours less than half day working
							status='P/A'
							colstatus='blue'
						elif(qry4[0]['halfdaytime']<=work_hour and work_hour<qry4[0]['fulldaytime']): ##if working hours greater than or equal to half day working and less than full day working
							if(employee_intime<=qry4[0]['latein']): ## if punch in first half
								status='P/I'
								colstatus='blue'
							elif(employee_outtime>=qry4[0]['earlyexit']):##if punch in Second half
								status='P/II'
								colstatus='blue'
							else:
								secearlydiff=((datetime.datetime.combine(datetime.date.today(), employee_intime) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())
								timeearlydiff=datetime.timedelta(seconds=secearlydiff)
								earlydiff=(datetime.datetime.min + timeearlydiff).time()

								seclatediff=((datetime.datetime.combine(datetime.date.today(), qry4[0]['earlyexit']) - datetime.datetime.combine(datetime.date.today(), employee_outtime)).total_seconds())
								timelatediff=datetime.timedelta(seconds=seclatediff)
								latediff=(datetime.datetime.min + timelatediff).time()
								if(earlydiff<=latediff):
									status='P/I'
									colstatus='blue'
								else:
									status='P/II'
									colstatus='blue'
						elif(work_hour>=qry4[0]['fulldaytime']): ## if working hour greater than fullday hours
							status='P'
							colstatus='black'
						if(employee_intime<=qry4[0]['latein']):
							latein=datetime.time(0,0,0)
						else:
							latesec=((datetime.datetime.combine(datetime.date.today(), employee_intime) - datetime.datetime.combine(datetime.date.today(), qry4[0]['latein'])).total_seconds())
							latetime=datetime.timedelta(seconds=latesec)
							latein=(datetime.datetime.min + latetime).time()
							colstatus='blue'
						if(employee_outtime>=qry4[0]['earlyexit']):
							earlyexit=datetime.time(0,0,0)
						else:
							earlysec=((datetime.datetime.combine(datetime.date.today(),qry4[0]['earlyexit']) - datetime.datetime.combine(datetime.date.today(), employee_outtime)).total_seconds())
							earlytime=datetime.timedelta(seconds=earlysec)
							earlyexit=(datetime.datetime.min + earlytime).time()
							colstatus='blue'

						data={'status':status,'intime':qry_in[0]['time'],'outtime':qry_out[0]['time'],'latein':latein,'earlyexit':earlyexit,'colstatus':colstatus,'work_hour':work_hour,'emp_id':emp_id,'extrahours':datetime.time(0,0,0)}
						print(data)

		else:## if holiday
			status='H'
			qry_in=machinerecords.objects.filter(Emp_Id=emp_id,date=date).values('id','time').order_by('time')[:1] ## get First punch of day
			qry_out=machinerecords.objects.filter(Emp_Id=emp_id,date=date).values('id','time').order_by('-time')[:1] ## get last punch of day
			if( qry0.count()>0):
				sec=((datetime.datetime.combine(datetime.date.today(), qry_out[0]['time']) - datetime.datetime.combine(datetime.date.today(), qry_in[0]['time'])).total_seconds())
				time=datetime.timedelta(seconds=sec)
				if qry_holiday[0]['restricted']=='N':

					work_hour=(datetime.datetime.min + time).time()## calculate working hour
				else:
					work_hour=datetime.time(0,0,0)

				intime=qry_in[0]['time']
				outime=qry_out[0]['time']

			else:
				work_hour=datetime.time(0,0,0)## calculate working hour
				intime=datetime.time(0,0,0)
				outime=datetime.time(0,0,0)
			data=data={'status':status,'intime':intime,'outtime':outime,'latein':datetime.time(0,0,0),'earlyexit':datetime.time(0,0,0),'colstatus':'red','work_hour':work_hour,'emp_id':emp_id,'extrahours':work_hour}


	return data;

def attendance_script(request):

	status=200
	if request.method == 'GET':

		#r=requests.get('http://10.0.0.6/autoScript/Refreshattendance.php/')
		date2=date.today()
		date1=date.today()
		inp={}
		inp['check1']=1
		#qry_del_log=LogRecord.objects.filter(db_table='Attendance2 object',emp_id='00007').delete()
		emp_id='ALL'

	elif request.method == 'POST':
		inp=json.loads(request.body.decode('utf-8'))
		emp_id=inp['emp_id']
		print(inp)
		####print(inp)
		date2=datetime.datetime.strptime(inp['date2'], "%Y-%m-%d").date()##inp['date2']##datetime.date.()
		date1=datetime.datetime.strptime(inp['date1'], "%Y-%m-%d").date()##inp['date1']

	check11=check_month_locked(date1,date2)
	if check11 == True:
		status=202
		msg= "Payable days has been locked for the date range selected."
	else:
		if(inp['check1']==1 ):
			datecheck1=date1

			while(datecheck1<=date2):
				r=requests.post('http://10.0.0.6/autoScript/Refreshattendance.php/',data={'date':datecheck1,'emp_id':emp_id})
				print(r.text)
				datecheck1 = datecheck1 + timedelta(days = 1)
				
		if(emp_id=='ALL'):
			qry_emp=EmployeePrimdetail.objects.filter(emp_status='ACTIVE').exclude(emp_id='00007').values('emp_id','doj')
		else:
			qry_emp=EmployeePrimdetail.objects.filter(emp_status='ACTIVE',emp_id=emp_id).exclude(emp_id='00007').values('emp_id','doj')
		todaydate=(datetime.datetime.now()+datetime.timedelta(minutes=330)).date()

		for qry_emp1 in qry_emp:
			datecheck=date1
			print(datecheck)
			print(date2)
			doj=qry_emp1['doj']
			emp_id=qry_emp1['emp_id']
			qry3=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('shift','shift__field','dept') #get shift of employee
			
			shift1=EmployeePrimdetail.objects.filter(emp_id=emp_id).values('shift')

			qry11=Attendance2.objects.filter(Emp_Id=emp_id,date=datecheck).values('shift_id')
			
			if shift1[0]['shift'] is not None:
				shiftt=list(Shifts.objects.filter(shiftid=shift1[0]['shift'],status='INSERT').values('id'))
				shift_id=shiftt[0]['id']
			else:
				shift_id=None

			if(qry11.count()!=0):
				qry4=Shifts.objects.filter(id=qry11[0]['shift_id']).values() #get shidt details
			else:
				qry4=Shifts.objects.filter(id=shift_id).values() #get shidt details


			qry_update=Attendance2.objects.filter(Emp_Id=emp_id,date=datecheck).update(shift_id=shift_id)
			
			if(qry4.count()!=0):
				while(datecheck<=date2 and datecheck <= todaydate):
					if doj is not None:
						if doj<=datecheck:
							qry=Attendance2.objects.filter(Emp_Id=emp_id,date=datecheck).values('colstatus')

							if(qry.count()>0 and qry[0]['colstatus']!='green'):
								if(qry3[0]['shift__field']=='NIGHT FIX' or qry3[0]['shift__field']=='NIGHT FLEXIBLE'):

									responsedata=night_shift(datecheck,emp_id,qry3,qry4)
								else:
									responsedata=mainscript(datecheck,emp_id,qry3,qry4)

								if(responsedata['status']!='1'):

									########################################changed by Salil###################################
									qry_update=Attendance2.objects.filter(Emp_Id=emp_id,date=datecheck).update(status=responsedata['status'],intime=responsedata['intime'],outtime=responsedata['outtime'],late=responsedata['latein'],etime=responsedata['earlyexit'],colstatus=responsedata['colstatus'],work=responsedata['work_hour'],extra=responsedata['extrahours'],shift_id=shift_id)
									######################### END ##########changed by Salil###################################

							elif(qry.count()==0):

								if(qry3[0]['shift__field']=='NIGHT FIX' or qry3[0]['shift__field']=='NIGHT FLEXIBLE'):
									responsedata=night_shift(datecheck,emp_id,qry3,qry4)
								else:
									responsedata=mainscript(datecheck,emp_id,qry3,qry4)

								if(responsedata['status']!='1'):
									
									# qry_insert=Attendance2.objects.create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=datecheck,status=responsedata['status'],intime=responsedata['intime'],outtime=responsedata['outtime'],late=responsedata['latein'],etime=responsedata['earlyexit'],colstatus=responsedata['colstatus'],work=responsedata['work_hour'],extra=datetime.time(0,0,0))
									#changedbysalil#
									qry_insert=Attendance2.objects.create(Emp_Id=EmployeePrimdetail.objects.get(emp_id=emp_id),date=datecheck,status=responsedata['status'],intime=responsedata['intime'],outtime=responsedata['outtime'],late=responsedata['latein'],etime=responsedata['earlyexit'],colstatus=responsedata['colstatus'],work=responsedata['work_hour'],extra=datetime.time(0,0,0),shift_id= Shifts.objects.get(id=shift_id))

					datecheck = datecheck + timedelta(days = 1)
	msg="done"
	qry_del_log2=LogRecord.objects.filter(db_table='LogRecord object',emp_id='00007').delete()
	data={'msg':date1}
	return JsonResponse(data=data,status=status)
	
def last_three_month_att(request):
	msg=""
	data=[]
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.method == 'GET':
				check=checkpermission(request,[337,211])
				if check == 200:
					if 'request_type' not in request.GET:
						status=200

						qry_dept_desg=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1'],emp_status="ACTIVE").values('dept','desg')

						qry_emp=Reporting.objects.filter(department=qry_dept_desg[0]['dept'],reporting_to=qry_dept_desg[0]['desg'],reporting_no='1').values('emp_id','emp_id__name')

						to_date = date.today()

						from_date=date.today() - relativedelta(months=+3)

						qry_co_id=LeaveType.objects.filter(leave_abbr='CO').values('id')

						half_hours_limit=EmployeeDropdown.objects.filter(field="HALF DAY").exclude(value__isnull=True).values('value')
						full_hours_limit=EmployeeDropdown.objects.filter(field="FULL DAY").exclude(value__isnull=True).values('value')

						extra=datetime.datetime.strptime(half_hours_limit[0]['value'],'%H:%M:%S').time()

						data=[]
						for emp in qry_emp:
							qry_attendance=Attendance2.objects.filter(Q(date__gte=from_date) & Q(date__lte=to_date)).filter(extra__gte=extra).filter(Emp_Id=emp['emp_id'],is_compoff=0).values('extra','date','is_compoff','intime','outtime','id')

							for att in qry_attendance:
								qry_check=Leaves.objects.filter(extraworkdate__contains=str(att['date'])).filter(leavecode=qry_co_id[0]['id']).filter(emp_id=emp['emp_id']).exclude(Q(finalstatus__contains='CANCELLED') | Q(finalstatus__contains='REJECTED')).values('leaveid')

								qry_check_holiday=Holiday.objects.filter(Q(f_date__lte=att['date']) & Q(t_date__gte=att['date'])).filter(dept=EmployeeDropdown.objects.get(sno=qry_dept_desg[0]['dept']),status='INSERT').filter(restricted='Y').values('id')
								if att['is_compoff'] ==0:
									att['is_compoff']=False
								else:
									att['is_compoff']=True

								if len(qry_check) == 0 and len(qry_check_holiday)==0:
									data.append({'emp_id':emp['emp_id'],'emp_name':emp['emp_id__name'],'date':str(att['date']),'extra':str(att['extra']),'intime':str(att['intime']),'outtime':str(att['outtime']),'is_compoff':att['is_compoff'],'id':att['id']})
					elif request.GET['request_type']=='view_previous':
						status=200

						extra=datetime.datetime.strptime("00:00:00",'%H:%M:%S').time()

						qry_dept_desg=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1'],emp_status="ACTIVE").values('dept','desg')

						qry_emp=Reporting.objects.filter(department=qry_dept_desg[0]['dept'],reporting_to=qry_dept_desg[0]['desg'],reporting_no='1').values_list('emp_id',flat=True)

						qry_attendance=Attendance2.objects.exclude(is_compoff=0).filter(Emp_Id__in=qry_emp,extra__gt=extra).values('extra','date','is_compoff','intime','outtime','id','Emp_Id','Emp_Id__name','Emp_Id__dept__value','Emp_Id__desg__value').order_by('-date')
						for q in qry_attendance:
							if q['is_compoff'] ==-1:
								q['is_compoff']="REJECTED"
							else:
								q['is_compoff']="APPROVED"
						data=list(qry_attendance)
					elif request.GET['request_type']=='hr_report':
						status=200
						from_date=datetime.datetime.strptime(str(request.GET['month']), '%Y-%m-%d').date()
						range1=calendar.monthrange(from_date.year,from_date.month)
						to_date=date(from_date.year,from_date.month ,range1[1])
					
						half_hours_limit=EmployeeDropdown.objects.filter(field="HALF DAY").exclude(value__isnull=True).values('value')
						
						extra=datetime.datetime.strptime(half_hours_limit[0]['value'],'%H:%M:%S').time()

						qry_attendance=Attendance2.objects.filter(date__range=[from_date,to_date],extra__gt=extra).values('extra','date','is_compoff','intime','outtime','id','Emp_Id','Emp_Id__name','Emp_Id__dept__value','Emp_Id__desg__value').order_by('-date')
						for q in qry_attendance:
							print(q['is_compoff'])
							if q['is_compoff'] ==-1:
								q['is_compoff']="REJECTED"
							elif q['is_compoff']==1:
								q['is_compoff']="APPROVED"
							else:
								q['is_compoff'] ="PENDING"
						data=list(qry_attendance)

				else:
					status = 502
			else:
				status=403
		else:
			status = 401
	else:
		status=500

	return JsonResponse(data = {'data':data},status = status)

def check_compoff(request):
	msg=""
	data={}
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			if request.method == 'POST':
				check=checkpermission(request,[337])
				if check == 200:
					status=200

					data=json.loads(request.body)
					data_compoff=list(data['data'])

					for d in data_compoff:
						qry_update=Attendance2.objects.filter(id=d[0]).update(is_compoff=d[1])

					status=200
					msg="Submitted Successfully"


				else:
					status = 502
			else:
				status=403
		else:
			status = 401
	else:
		status=500

	return JsonResponse(data = {'msg':msg},status=status)


def hod_wise_attendance(request):
	data_values = []
	if 'HTTP_COOKIE' in request.META:
		if request.user.is_authenticated:
			check = checkpermission(request,[337,1345])
			if(check == 200):
				if(request.method == 'GET'):
					count_li = []
					date =request.GET['date']

					qry_dept_desg=EmployeePrimdetail.objects.filter(emp_id=request.session['hash1'],emp_status="ACTIVE").values('dept','desg')
					if 'dept' in request.GET:
						qry_emp=EmployeePrimdetail.objects.filter(dept__in=request.GET['dept'].split(','),emp_status='ACTIVE').extra(select={'emp_id__name':'name'}).values('emp_id','name','emp_id__name','dept__value')
						for emp in qry_emp:
							data_values.append({"att_data":emp_attendance(emp['emp_id'],date,date),'emp_id':emp['emp_id'],'dept':emp['dept__value'],'name':emp['emp_id__name']})
					else:
						qry_emp=Reporting.objects.filter(department=qry_dept_desg[0]['dept'],reporting_to=qry_dept_desg[0]['desg'],emp_id__emp_status='ACTIVE').values('emp_id','emp_id__name','emp_id__dept__value')
						for emp in qry_emp:
							data_values.append({"att_data":emp_attendance(emp['emp_id'],date,date),'emp_id':emp['emp_id'],'dept':emp['emp_id__dept__value'],'name':emp['emp_id__name']})
					
					count_li.append({"P":Attendance2.objects.filter(date=date,status='P',Emp_Id__dept=qry_dept_desg[0]['dept']).count()})
					count_li.append({"P/I":Attendance2.objects.filter(date=date,status='P/I',Emp_Id__dept=qry_dept_desg[0]['dept']).count()})
					count_li.append({"P/II":Attendance2.objects.filter(date=date,status='P/II',Emp_Id__dept=qry_dept_desg[0]['dept']).count()})
					count_li.append({"P/A":Attendance2.objects.filter(date=date,status='P/A',Emp_Id__dept=qry_dept_desg[0]['dept']).count()})
					count_li.append({"A":Attendance2.objects.filter(date=date,status='A',Emp_Id__dept=qry_dept_desg[0]['dept']).count()})
					status=200
					msg="Success"
				else:
					status=502
			else:
				status=403
		else:
			status=401
	else:
		status=500
	return JsonResponse(data={'data':data_values,"status_count":count_li},status=status)


#################################################_machine_code_upload_attendence_##########################################################    
# def upload_attendance(request):
#   if checkpermission(request,[rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS:
#       if requestMethod.POST_REQUEST(request):
#           data = json.loads(request.body)
#           info = data["data"]
#           if len(info)>0:
#               for x in info:
#                   print(x['DATE'])

#                   x['DATE'] = datetime.datetime.strptime(x['DATE'], "%d-%m-%Y").strftime('%Y-%m-%d')
#                   print(x['DATE'])
#                   timestamp1 = str(x["DATE"])+" "+str(x["INTIME"])
#                   timestamp2 = str(x["DATE"])+" "+str(x["OUTIME"])
#                   qry = machinerecords.objects.create(date=x["DATE"],time=x["INTIME"],timestamp=timestamp1,Emp_Id=EmployeePrimdetail.objects.get(emp_id=x["EMP_ID"]))
#                   qry1 = machinerecords.objects.create(date=x['DATE'],time=x["OUTIME"],timestamp=timestamp2,Emp_Id=EmployeePrimdetail.objects.get(emp_id=x["EMP_ID"]))
#               return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)
#       else:
#           return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
#   else:
#       return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

def upload_attendance(request):
	if checkpermission(request,[rolesCheck.ROLE_HR]) == statusCodes.STATUS_SUCCESS:
		if requestMethod.POST_REQUEST(request):
			data = json.loads(request.body)
			info = data["data"]
			if len(info)>0:
				obj1 = []
				obj = []
				count = 0
				a=0
				for x in info:
					try:
						x['DATE'] = datetime.datetime.strptime(x['DATE'], "%d-%m-%Y").strftime('%Y-%m-%d')
					except:
						return functions.RESPONSE({'msg':'Invalid date format in line no '+str(a+2)},statusCodes.STATUS_WARNING)
					try:
						s = machinerecords.objects.filter(time=x['INTIME']).values()
						s1 = machinerecords.objects.filter(time=x['OUTIME']).values()
					except:
						return functions.RESPONSE({'msg':'Invalid time format in line no '+str(a+2)},statusCodes.STATUS_WARNING)
					key = x.keys() 
					if x['INTIME']<x['OUTIME']:
						check = EmployeePrimdetail.objects.filter(emp_id=x["EMP_ID"]).values()
						if len(check)>0:
							g=0
							for w in obj:
								if w['emp'] == x['EMP_ID'] and w['DATE'] == x['DATE']:
									del obj[g]
									del obj1[g]
									count-=1
								else:
									g+=1
							qry_dup = machinerecords.objects.filter(date=x['DATE'],Emp_Id=EmployeePrimdetail.objects.get(emp_id=x["EMP_ID"])).delete()
							obj.append({})
							obj[count]['DATE'] = x['DATE']
							obj[count]['TIME'] = str(x['INTIME']).strip()
							obj[count]['emp'] = x["EMP_ID"]
							obj1.append({})
							obj1[count]['DATE'] = x['DATE']
							obj1[count]['TIME'] = str(x['OUTIME']).strip()
							obj1[count]['emp'] = x["EMP_ID"]
							count+=1
						else:
							return functions.RESPONSE({'msg':'Employee id '+x["EMP_ID"]+' is incorrect does not exist'},statusCodes.STATUS_WARNING)
					else:
						return functions.RESPONSE({'msg':'Time should be in 24 hr format in line no '+str(a+2)},statusCodes.STATUS_WARNING)
					a+=1
				print(obj)

				qr_object = (machinerecords(date=data['DATE'],time=data['TIME'],timestamp=datetime.datetime.now(),Emp_Id=EmployeePrimdetail.objects.get(emp_id=data['emp']))for data in obj)
				qr_object1 = (machinerecords(date=data['DATE'],time=data['TIME'],timestamp=datetime.datetime.now(),Emp_Id=EmployeePrimdetail.objects.get(emp_id=data['emp']))for data in obj1)
				qr_create = machinerecords.objects.bulk_create(qr_object)
				qr_create = machinerecords.objects.bulk_create(qr_object1)
				return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)
		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)

