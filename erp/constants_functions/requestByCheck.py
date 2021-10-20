def requestByHR(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='HR':
		return True
	else:
		return False

def requestByEmployee(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='employee':
		return True
	else:
		return False

def requestByHOD(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='hod':
		return True
	else:
		return False

def requestByDean(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='dean':
		return True
	else:
		return False

def requestByCoord(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='coordinator':
		return True
	else:
		return False

def requestBySubCoord(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='subjectCoordinator':
		return True
	else:
		return False

def requestByTTCoord(data): ###### time table coordinator
	if not 'request_by' in data:
		return False
	if data['request_by']=='TTCoordinator':
		return True
	else:
		return False

def requestByGroupCoord(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='groupCoordinator':
		return True
	else:
		return False

def requestByExtraAttCoord(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='extraAttCoordinator':
		return True
	else:
		return False

def requestBySubjectCOCoord(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='subjectCOCoordinator':
		return True
	else:
		return False

def requestByQuestionModerator(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='questionModerator':
		return True
	else:
		return False

def requestByNBACoordinator(data):
	if not 'request_by' in data:
		return False
	if data['request_by']=='nbaCoordinator':
		return True
	else:
		return False