def course(data):
	if data['request_type']=='course':
		return True
	else:
		return False

def branch(data):
	if data['request_type']=='branch':
		return True
	else:
		return False

def firstrequest(data):
	if data['request_type']=='form_data':
		return True
	else:
		return False

def reportData(data):
	if data['request_type']=='report_data':
		return True
	else:
		return False

def custom_request_type(data,req_type):
	if data['request_type']== req_type :
		return True
	else:
		return False
