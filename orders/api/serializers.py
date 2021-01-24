from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField, SerializerMethodField
from orders.models import Order
from rest_framework import serializers
from clients.models import Client, HCI
from licence.models import Licence, Application

class OrderSerializer(ModelSerializer):
	applicationName = SerializerMethodField()
	customerName = SerializerMethodField()
	hciId = SerializerMethodField()
	orderStartDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	expiryDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	issueDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	graceExpiryDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	graceIssueDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	isArchived = SerializerMethodField()
	class Meta:
		model = Order
		fields = [
					'id',
					'applicationName',
					'customerName',
					'hciId',
					'MachineID',
					'App',
					'trial',
					'licence_attrs',
					'issueDate',
					'orderStartDate',
					'expiryDate',
					'period',
					'graceIssueDate',
					'graceExpiryDate',
					'graceCount',
					'isArchived',
					'Category'
				]

	def get_applicationName(self, obj):
		appObj = Application.objects.get(ApplicationName=obj.App)
		return appObj.ApplicationName

	def get_customerName(self, obj):
		macObj = HCI.objects.get(MachineID=obj.MachineID)
		cusObj = Client.objects.get(CusId=macObj.Customer)
		return cusObj.Name

	def get_hciId(self, obj):
		macObj = HCI.objects.get(MachineID = obj.MachineID)
		return macObj.MachineID

	def get_isArchived(self, obj):
		isArchived = "Active Record"
		licObjs = Licence.objects.filter(MachineID = obj.MachineID, App = obj.App)
		if licObjs.exists() and licObjs.count()==1:
			licObj = licObjs.first()
			if licObj.isArchived:
				isArchived = "Archived Record"
		if obj.App.isArchived or obj.MachineID.isArchived or obj.MachineID.Customer.isArchived:
			isArchived = "Archived Record"
		return isArchived

class OrderCreateUpdateSerializer(ModelSerializer):
	class Meta:
		model = Order
		fields = [
					'MachineID',
					'App',
					'trial',
					'licence_attrs',
					'orderStartDate',
					'period',
					'expiryDate',
					'graceIssueDate',
					'graceExpiryDate',
					'graceCount',
					'Category'
				]

class OrderGraceUpdateSerializer(ModelSerializer):
	class Meta:
		model = Order
		fields = [
			'graceExpiryDate',
			'graceIssueDate',
		]