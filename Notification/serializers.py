from rest_framework import serializers

from django.contrib.auth.models import User
from .models import DataStructure , DataSet ,Group ,SubGroup,Template,SendNotification,NotificationLog

from django.contrib.auth import authenticate
from rest_framework import exceptions
from django_mysql.models import JSONField

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()

#     def validate(self, data):
#         username = data.get("username", "")
#         password = data.get("password", "")

#         if username and password:
#             user = authenticate(username=username, password=password)
#             if user:
#                 if user.is_active:
#                     data["user"] = user
#                 else:
#                     msg = "User is deactivated."
#                     raise exceptions.ValidationError(msg)
#             else:
#                 msg = "Unable to login with given credentials."
#                 raise exceptions.ValidationError(msg)
#         else:
#             msg = "Must provide username and password both."
#             raise exceptions.ValidationError(msg)
#         return data





class DataSetListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        dataSet = [DataSet(**item) for item in validated_data]
        return DataSet.objects.bulk_create(dataSet)

    def update(self, instances, validated_data):
      
        instance_hash = {index: instance for index, instance in enumerate(instances)}

        result = [
            self.child.update(instance_hash[index], attrs)
            for index, attrs in enumerate(validated_data)
        ]

        return result


class DataSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = '__all__'
        list_serializer_class = DataSetListSerializer



class DataStructureSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataStructure
        fields = '__all__'

class CreateGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'

    def create(self, validated_data):
        qry = Group.objects.create(group_name=validated_data['group_name'],data_id=validated_data['data_id'],accessible_by=validated_data['accessible_by'])
        return qry




class CreateSubGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubGroup
        fields = '__all__'

    def create(self, validated_data):
        qry = SubGroup.objects.create(subgroup_name=validated_data['subgroup_name'],group_id=validated_data['group_id'],accessible_by=validated_data['accessible_by'])
        return qry



class CreateTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Template
        fields = "__all__"

class SendNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SendNotification
        fields = "__all__"

    def create(self,validated_data):
        qry = SendNotification.objects.create(**validated_data)
        return qry



class NotificationLogListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        dataSet = [NotificationLog(**item) for item in validated_data]
        return NotificationLog.objects.bulk_create(dataSet)

class NotificationLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationLog
        fields = "__all__"
        list_serializer_class = NotificationLogListSerializer

