from rest_framework.serializers import ModelSerializer,HyperlinkedIdentityField, SerializerMethodField
from licence.models import Licence, Application, GitUpdate, AppUpdate
from clients.models import Client, HCI
from rest_framework import serializers
from datetime import timedelta
from orders.api.serializers import OrderSerializer
import datetime, time

class LicenceCreateSerializer(ModelSerializer):
	class Meta:
		model = Licence
		fields = [
			'MachineID',
			'App',
			'licence_attrs',
			'OrderID',
			'trial',
			'issueDate',
			'expiryDate',
			'graceExpiryDate',
			'graceIssueDate',
			'Category'
		]

class LicenceCreateArchiveSerializer(ModelSerializer):
	class Meta:
		model = Licence
		fields = [
			'MachineID',
			'App',
			'OrderID',
			'licence_attrs',
			'trial',
			'issueDate',
			'expiryDate',
			'graceExpiryDate',
			'graceIssueDate',
			'isArchived',
			'Category'
		]

class LicenceUpdateSerializer(ModelSerializer):
	class Meta:
		model = Licence
		fields = [
			'MachineID',
			'App',
			'licence_attrs',
			'OrderID',
			'trial',
			'expiryDate',
			'graceExpiryDate',
			'graceIssueDate',
			'Category'
		]

class LicenceSerializer(ModelSerializer):
	startDate = SerializerMethodField()
	period = SerializerMethodField()
	class Meta:
		model = Licence
		fields = [
			'id',
			'MachineID',
			'App',
			'licence_attrs',
			'trial',
			'issueDate',
			'expiryDate',
			'graceExpiryDate',
			'graceIssueDate',
			'startDate',
			'period',
			'Category'
		]

	def get_startDate(self, obj):
		orderObj = obj.OrderID
		obj = OrderSerializer(orderObj)
		return obj.data['orderStartDate']

	def get_period(self, obj):
		orderObj = obj.OrderID
		obj = OrderSerializer(orderObj)
		return obj.data['period']

class LicenceGraceTrailUpdateSerializer(ModelSerializer):
	class Meta:
		model = Licence
		fields = [
			'trial',
			'graceExpiryDate',
			'graceIssueDate',
			'licence_attrs',
			'Category',
		]

class LicenceDetailSerializer(ModelSerializer):
	applicationName = SerializerMethodField()
	customerName = SerializerMethodField()
	hciId = SerializerMethodField()
	graceIssueDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	expiryDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	issueDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	graceExpiryDate = serializers.DateField(format = "%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
	inactiveIngrace = SerializerMethodField()
	orderStartDate = SerializerMethodField()
	status = SerializerMethodField()
	period = SerializerMethodField()
	class Meta:
		model = Licence
		fields = [
			'id',
			'MachineID',
			'customerName',
			'hciId',
			'trial',
			'applicationName',
			'App',
			'issueDate',
			'licence_attrs',
			'orderStartDate',
			'expiryDate',
			'graceExpiryDate',
			'graceIssueDate',
			'OrderID',
			"inactiveIngrace",
			"status",
			"period",
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

	def get_orderStartDate(self, obj):
		orderObj = obj.OrderID
		obj = OrderSerializer(orderObj)
		return obj.data['orderStartDate']

	def get_period(self, obj):
		orderObj = obj.OrderID
		obj = OrderSerializer(orderObj)
		return obj.data['period']

	def get_inactiveIngrace(self, obj):
		try:
			diff = obj.graceIssueDate - obj.expiryDate
		except:
			return False
		if diff == timedelta(hours=24):
			return False
		return True

	def get_status(self, obj):
		try:
			date = datetime.datetime.today().date()
			diff = obj.graceIssueDate - obj.expiryDate
			if obj.trial:
				return "trial"
			elif obj.expiryDate >= date:
				return "active"
			elif diff == timedelta(hours=24) and obj.graceExpiryDate >= date:
				return "activeIngrace"
			elif diff != timedelta(hours=24) and obj.graceExpiryDate >= date:
				return "inactiveIngrace"
			return "Expired"
		except:
			return "Unknown"

class ApplicationSerializer(ModelSerializer):
	class Meta:
		model = Application
		fields = [
			'id',
			'ApplicationName',
			'repoLink',
			'alternateRepoLink',
			'gitRepoLink',
			'alternateGitRepoLink',
			'gitRepoLinkBasic',
			'alternateGitRepoLinkBasic',
			'gitRepoLinkPro',
			'alternateGitRepoLinkPro',
			'attrs',
		]

class ApplicationArchiveSerializer(ModelSerializer):
	class Meta:
		model = Application
		fields = [
			'id',
			'ApplicationName',
			'repoLink',
			'alternateRepoLink',
			'gitRepoLink',
			'alternateGitRepoLink',
			'gitRepoLinkBasic',
			'alternateGitRepoLinkBasic',
			'gitRepoLinkPro',
			'alternateGitRepoLinkPro',
			'attrs',
			'isArchived'
		]

class AppUpdateSerializer(ModelSerializer):
	class Meta:
		model = AppUpdate
		fields = [
			'id',
			'app',
			'version',
			'type',
			'downloadZipName',
			'details',
			'created',
			'updated'
		]
		read_only_fields = ['created', 'updated']

	def __init__(self, *args, **kwargs):
		if 'data' in kwargs and 'isArchived' in kwargs['data']:
			self.Meta.fields = list(self.Meta.fields)
			self.Meta.fields.append('isArchived')
		super(AppUpdateSerializer, self).__init__(*args, **kwargs)

class GitUpdateSerializer(ModelSerializer):
	class Meta:
		model = GitUpdate
		fields = [
			'id',
			'app',
			'version',
			'type',
			'details',
			'created',
			'updated'
		]
		read_only_fields = ['created', 'updated']

	def __init__(self, *args, **kwargs):
		if 'data' in kwargs and 'isArchived' in kwargs['data']:
			self.Meta.fields = list(self.Meta.fields)
			self.Meta.fields.append('isArchived')
		super(GitUpdateSerializer, self).__init__(*args, **kwargs)