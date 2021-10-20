from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.db.models import Q
import json
from bs4 import BeautifulSoup
import requests
import unicodedata

from StudentMMS.models.models_1819o import *
from StudentMMS.models.aktu_1819o import *
from StudentMMS.models.models_1819e import *
from StudentMMS.models.models_1920o import *

from erp.constants_variables import statusCodes,statusMessages,rolesCheck
from erp.constants_functions import academicCoordCheck,requestByCheck,functions,requestMethod
from Registrar.models import *
from musterroll.models import EmployeePrimdetail
from login.views import checkpermission,generate_session_table_name
import time 

def getComponents(request):
	pass