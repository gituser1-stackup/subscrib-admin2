from rest_framework.serializers import ModelSerializer,HyperlinkedIdentityField, SerializerMethodField
from clients.models import Client, HCI
from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import UserProfile
from licence.models import Licence

User = get_user_model()

class UserProfileSerializer(ModelSerializer):
	class Meta:
		model = UserProfile
		fields = [
			'cid'
		]

class UserSerializer(ModelSerializer):
	profile = UserProfileSerializer(required=True)
	class Meta:
		model = User
		fields = [
			'id',
			'username',
			'email',
			'profile'
		]

	def create(self, validated_data):
		profile_data = 	validated_data.pop('profile')
		user = User(**validated_data)
		user.is_active = False
		user.save()
		profile, created = UserProfile.objects.get_or_create(user=user)
		for attr, value in profile_data.items():
			setattr(profile, attr, value)
		profile.save()
		print(profile.cid)
		return user

	def update(self, instance, validated_data):
		profile_data = validated_data.pop('profile')
		profile = instance.profile

		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()
		for attr, value in profile_data.items():
			setattr(profile, attr, value)
		profile.save()
		return instance

class UserDetailSerializer(ModelSerializer):
	id = SerializerMethodField()
	email = SerializerMethodField()
	username = SerializerMethodField()
	is_active = SerializerMethodField()
	class Meta:
		model = UserProfile
		fields = [
			'id',
			'username',
			'email',
			'is_active',
			'cid'
		]

	def get_id(self, obj):
		return obj.user.id

	def get_email(self,obj):
		user = User.objects.filter(id=obj.user.id)
		if user.exists():
			return user.first().email
		else:
			return None

	def get_username(self,obj):
		user = User.objects.filter(id=obj.user.id)
		if user.exists():
			return user.first().username
		else:
			return None

	def get_is_active(self, obj):
		user = User.objects.filter(id=obj.user.id)
		if user.exists():
			return user.first().is_active
		else:
			return None

class ClientUserSerializer(ModelSerializer):
	cusId = SerializerMethodField()
	cusName = SerializerMethodField()
	# email = SerializerMethodField()
	# is_active = SerializerMethodField()
	class Meta:
		model = User
		fields = [
			'id',
			'username',
			'email',
			'is_active',
			'cusId',
			'cusName',
		]

	def get_cusId(self,obj):
		clients = Client.objects.filter(id=obj.profile.cid.id)
		if clients.exists():
			return clients.first().id
		else:
			return None

	def get_cusName(self,obj):
		clients = Client.objects.filter(id=obj.profile.cid.id)
		if clients.exists():
			return clients.first().Name
		else:
			return None

class ClientUserSerializer2(ModelSerializer):
	users = SerializerMethodField()
	isLicencePresent = SerializerMethodField()
	# cusName = SerializerMethodField()
	# email = SerializerMethodField()
	# is_active = SerializerMethodField()
	class Meta:
		model = Client
		fields = [
			'id',
			'Name',
			'CusId',
			'users',
			'isLicencePresent'
		]

	def get_users(self,obj):
		users = UserProfile.objects.filter(cid__id=obj.id)#id=obj.profile.cid.id)
		if users.exists():
			return UserDetailSerializer(users, many=True).data
		else:
			return None

	def get_isLicencePresent(self, obj):
		hcis = HCI.objects.all().filter(Customer=obj.id)
		if hcis.exists():
			licObj = Licence.objects.all().filter(MachineID__in=hcis)
			if licObj.exists():
				return True
			else:
				return False
		else:
			return False

class ClientSerializer(ModelSerializer):
	class Meta:
		model = Client
		resource_name = "clients"
		fields = [
			'id',
			'Name',
			'CusId',
			'Lat',
			'Long',
			'CustLoc',
		]


class HCISerializer(ModelSerializer):
	class Meta:
		model = HCI
		fields = [
			'id',
			'MachineID',
			'Customer'
		]

class HCIDetailSerializer(ModelSerializer):
	customerName = SerializerMethodField()
	customerId = SerializerMethodField()
	class Meta:
		model = HCI
		fields = [
			'id',
			'MachineID',
			'Customer',
			'customerName',
			'customerId'
		]

	def get_customerName(self,obj):
		name = Client.objects.filter(CusId=obj.Customer).values_list('Name',flat=True)
		return str(name[0])

	def get_customerId(self,obj):
		idval = Client.objects.filter(CusId=obj.Customer).values_list('CusId',flat=True)
		return idval[0]