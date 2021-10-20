from erp.constants_variables import statusCodes,rolesCheck
from login.views import checkpermission

def isSubjectCoord(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'S' in request.session['Coordinator_type'] and checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		return True
	else:
		return False

def isTTCoord(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'T' in request.session['Coordinator_type'] and checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		return True
	else:
		return False

def isExtraAttCoord(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'E' in request.session['Coordinator_type'] and checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		return True
	else:
		return False

def isGroupCoord(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'G' in request.session['Coordinator_type'] and checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		return True
	else:
		return False

def isAcademicHOD(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'H' in request.session['Coordinator_type'] and checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS and checkpermission(request,[rolesCheck.ROLE_HOD]) == statusCodes.STATUS_SUCCESS:
		return True
	else:
		return False

def isSubjectCOCoord(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'CO' in request.session['Coordinator_type'] and checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		return True
	else:
		return False

def isQuestionModerator(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'QM' in request.session['Coordinator_type'] and checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		return True
	else:
		return False

def isNBACoordinator(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'NC' in request.session['Coordinator_type'] and checkpermission(request,[rolesCheck.ROLE_ACADEMIC]) == statusCodes.STATUS_SUCCESS:
		return True
	else:
		return False

def isRector(request):
	print(request.session['Coordinator_type'])
	if not 'Coordinator_type' in request.session:
		return False
	if 'REC' in request.session['Coordinator_type']:
		return True
	else:
		return False

def isWarden(request):
	if not 'Coordinator_type' in request.session:
		return False
	if 'WAR' in request.session['Coordinator_type']:
		return True
	else:
		return False