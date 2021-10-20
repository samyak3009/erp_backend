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