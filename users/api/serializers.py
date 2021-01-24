from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from users.models import ( SecurityQuestion, UserSecurityDetail, AuditTrail)
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class AuditSerializer(ModelSerializer):
	user = SerializerMethodField()
	timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
	new_data = SerializerMethodField()
	old_data = SerializerMethodField()
	class Meta:
		model = AuditTrail
		fields = [
					'user',
					'action',
					'timestamp',
					'new_data',
					'old_data'
				 ]

	def get_user(self, obj):
		try:
			print(obj.user)
			user = User.objects.get(username=obj.user)
			username = user.username
			return username
		except User.DoesNotExist:
			return None

	def get_new_data(self, obj):
		try:
			new_data = {}
			for eq in obj.new_data.split(';'):
				key, value = eq.split('=')
				if key.strip() == 'licence_attrs':
					value = json.loads(value.replace("\'", "\""))
					new_data[key.strip()] = value
				else:
					new_data[key.strip()] = value.strip()
			return new_data
		except Exception as err:
			# print(err)
			return None

	def get_old_data(self, obj):
		try:
			old_data = {}
			for eq in obj.old_data.split(';'):
				key, value = eq.split('=')
				if key.strip() == 'licence_attrs':
					value = json.loads(value.replace("\'", "\""))
					old_data[key.strip()] = value
				else:
					old_data[key.strip()] = value.strip()
			return old_data
		except Exception as err:
			# print(err)
			return None

class SecurityQuestionSerializer(ModelSerializer):
	class Meta:
		model = SecurityQuestion
		fields = [
					'id',
					'question',
					'optionA',
					'optionB',
					'optionC',
					'optionD',
					'optionE'
				]

class UserSecurityDetailSerializer(ModelSerializer):
	class Meta:
		model = UserSecurityDetail
		fields = [
					'id',
					'userid',
					'questionId',
					'value'
				]