from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.db.models import Sum,F
from login.views import checkpermission,generate_session_table_name
import json
from itertools import groupby
import time
import math
from datetime import date

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod

from StudentMMS.models import *
from StudentAcademics.models import *
from Registrar.models import *
from login.models import *
from StudentPortal.models import StudentActivities_1819o,StudentActivities_1819e
from StudentSMM.models import *

from StudentMMS.constants_functions import requestType
from StudentAcademics.views import *

def Disciplinary_Action(request):
	data_values=[]
	if requestMethod.POST_REQUEST(request):

		session_name=request.session['Session_name']
		Incident = generate_session_table_name('Incident_',session_name)
		IncidentReporting = generate_session_table_name('IncidentReporting_',session_name)
		IncidentApproval = generate_session_table_name('IncidentApproval_',session_name)
		studentSession = generate_session_table_name("studentSession_",session_name)

		data = json.loads(request.body)
		date_of_incident = datetime.strptime(str(data['date_of_incident']).split('T')[0],"%Y-%m-%d").date()
		description = data['description']
		incident_document = data['incident_document']
		added_by = request.session['hash1']
		uniq_id = data['uniq_id']
		action = data['action']
		comm_to_parent = data['comm_to_parent']
		student_document = data['student_document']


		qry1=Incident.objects.create(date_of_incident=date_of_incident,description=description,incident_document=incident_document,added_by=EmployeePrimdetail.objects.get(emp_id=added_by))
		qry2=IncidentReporting.objects.create(incident=Incident.objects.get(id=qry1.id),uniq_id=studentSession.objects.get(uniq_id=uniq_id),action=action,comm_to_parent=comm_to_parent,student_document=student_document,added_by=EmployeePrimdetail.objects.get(emp_id=added_by))
		qry3=IncidentApproval.objects.create(incident_detail=IncidentReporting.objects.get(id=qry2.id))

		return functions.RESPONSE(statusMessages.MESSAGE_SUCCESS,statusCodes.STATUS_SUCCESS)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)
