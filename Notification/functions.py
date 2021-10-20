from .models import DataStructure,Group,SubGroup,Template,DataSet,NotificationLog
from .serializers import DataSetSerializer,NotificationLogSerializer
from .tasks import send_notification_via_email,send_notification_via_phone
from django_celery_results.models import TaskResult


def check_duplicate_name(name):
	if DataStructure.objects.filter(name=name).exclude(status=0).exists():
		return True
	return False



def validate_ids(data, data_field, unique=True): #key id and unique=True
	#get ids to update or delete
	field =data_field
	if isinstance(data, list):
		id_list = [int(x[field]) for x in data]

		if unique and len(id_list) != len(set(id_list)):
			raise ValidationError("Multiple updates to a single {} found".format(field))

		return id_list

	return [data]



def check_duplicate_group_name(name):
	if Group.objects.filter(group_name=name).exclude(status=0).exists():
		return True
	return False



def get_primkey(data_id):
	qry = list(DataSet.objects.filter(data_id=data_id).exclude(status=0).values_list("prim_key",flat=True))
	print(qry)
	return qry

def check_duplicate_subgroup_name(name):
	if SubGroup.objects.filter(subgroup_name=name).exclude(status=0).exists():
		return True
	return False


def check_duplicate_Template_name(name):
	if Template.objects.filter(template_name=name).exclude(status=0).exists():
		return True
	return False



def update_by_threads(dataset,prim_key_li):
	serializer = DataSetSerializer(dataset, data=prim_key_li, partial=True, many=True)
	serializer.is_valid(raise_exception=True)
	serializer.save()

def send_by_threads(qs_list,msg,temp_data_key,portal,email_li,phone_li,uniq_field,template_body,qry_id,subject,signature):
	data_values_list =[]
	for data_json in qs_list:
		notification_log = {}
		send_email_list = []
		send_phone_list = []
		format_values = []
		for col in temp_data_key:
			if "dataset" in str(col):
				print(col)
				x = str(col)
				col = x.replace('dataset.','')
				# col = col.replace('dataset.','')
				format_values.append(data_json[col])
			else:
				format_values.append(col)
		msg_body = msg.format(*format_values)
		for email in email_li:
			send_email_list.append(data_json[email])
		for phone in phone_li:
			send_phone_list.append(data_json[phone])
		notification_log['prim_key'] = data_json[uniq_field]
		notification_log['msg'] = msg_body
		notification_log['email'] = send_email_list
		notification_log['phone'] = send_phone_list
		notification_log['portal'] = portal
		notification_log["notify_id"] = qry_id
		print(notification_log)
		# if data_json[uniq_field] == "954":
		data_values_list.append(notification_log)
	if (NotificationLog.objects.filter(notify_id=qry_id).exists()==False):
		serializer = NotificationLogSerializer(data=data_values_list,many=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
	for d in data_values_list:
		send_notification_via_email.delay(d,subject,signature)
		send_notification_via_phone.delay(d,subject,signature)