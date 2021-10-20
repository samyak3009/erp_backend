# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from musterroll.models import EmployeePrimdetail,EmployeeDropdown,Reporting
from leave.models import LeaveType
from login.models import AuthUser
from Registrar.models import *
#from musterroll.models Reporting
from datetime import datetime
from itertools import chain
from operator import attrgetter
from pprint import pprint
from django.utils import dateparse
import os
# Create your views here.

def testclear(request):
	print("helooo")
	path = '/home/ds/Desktop/BackupOfPhotos'
	data = []
	files=[]
	newData=[]
	newpath = ''
	changedName = []
	for r, d, f in os.walk(path):
		for file in f:
			if '.JPG' or '.jpeg'or '.jpg' in file:
				files.append(os.path.join(r, file))

	for f in files:
		changedName.append(f[47:])
		newpath = f[0:47]
	
	print(newpath)
	qry = list(StudentPerDetail.objects.filter().values('image_path'))
	for q in qry:	
		data.append(q['image_path'])

	print(len(changedName))
	print(len(data))
	# data = Diff(changedName,data)
	# for j in data:
	# 	newData.append(newpath+j)

	# for remove in newData:
	# 	os.remove(remove)
	# print(len(data))
	return JsonResponse({'msg':"hello",'error':"fssd",'data':data},safe=False)



def Diff(li1, li2): 
    return (list(set(li1) - set(li2))) 