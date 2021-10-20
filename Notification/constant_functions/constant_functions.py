import Notification as nf


def getUniqFieldData(data_id):
	qry = nf.models.DataSet.objects.filter(data_id=data_id).exclude(status=0).values()
	data = list(qry.values("prim_key"))
	for k,v in zip(data,list(qry)):
		k['name'] = v['data_json']['NAME']

	return data


def checkpermission(request, myList=[]):
    myList = set(myList)  # myList includes the role ids of authorized persons
    roles = []
    print("hjk")
    if len(myList) == 0:
        try:
            var = request.session['hash1']
            if var:
                return 200
        except:
            return 401

    else:
        # roles=[]
        if 'roles' in request.session:
            roles = list(request.session['roles'])
        for r in myList:
            if r in roles:
                return 200
        return 401

def getUser(request):
    user = request.session['hash1']
    name = list(nf.models.DataSet.objects.filter(data_id=1,data_json__emp_id=user).exclude(status=0).values("data_json"))
    if len(name) >0:
        user = name[0]['data_json']['Name']+"("+user+")" 
    else:
        user = "SUPERUSER("+user+")" 
    return user