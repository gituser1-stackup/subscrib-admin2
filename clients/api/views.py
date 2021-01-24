from rest_framework.generics import ( ListAPIView, RetrieveAPIView,
									UpdateAPIView, DestroyAPIView,
									CreateAPIView, RetrieveUpdateAPIView )
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from clients.models import Client, HCI
from users.models import AuditTrail, UserProfile
from rest_framework.permissions import ( AllowAny, IsAuthenticated,
										IsAdminUser, IsAuthenticatedOrReadOnly )
from .serializers import ( HCISerializer, ClientSerializer, HCIDetailSerializer,
						   UserSerializer, ClientUserSerializer, ClientUserSerializer2 )
from django.db.models import Q
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from users.mail_utility import mail
from users.utils import logging

import json

User = get_user_model()

class ClientUserCreateView(CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

	def create(self, request, *args, **kwargs):
		try:
			data = request.data
			qusers1 = User.objects.filter(profile__cid=request.data['profile']['cid'])
			qusers2 = User.objects.filter(email=request.data['email'])
			print(qusers2)
			if ( not qusers1.exists() or ( qusers1.exists() and qusers1.count() < 2)) and not qusers2.exists():
				new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
				response = super(ClientUserCreateView, self).create(request, *args, **kwargs)
				audit = AuditTrail.objects.create(user=request.user.username,rowId=response.data['id'], action="Create", table_name="User",
												  new_data=new_data)
				if response.status_code == 201:
					audit.save()
				return response
			if qusers2.exists():
				return Response({"info": "User with the given email id is already present"}, status=400)
			return Response({"info": "Only two users could be created Users"}, status=400)
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->UserCreation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ClientUserUpdateView(UpdateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			qusers1 = User.objects.filter(email=request.data['email']).exclude(pk=kwargs['id'])
			print(qusers1)
			if not qusers1.exists():
				user = User.objects.get(pk=kwargs["id"])
				serzUser = UserSerializer(user)
				old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzUser.data.items() if key != "id")
				audit = AuditTrail.objects.create(user=request.user.username, rowId=user.id, action="Update", table_name="User",
												  new_data=new_data, old_data=old_data)
				response = super(ClientUserUpdateView, self).update(request, *args, **kwargs)
				if response.status_code == 200:
					audit.save()
				return response
			return Response({"info": "User with the given email id is already present"}, status=400)
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->UserUpdation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ClientUserDeleteView(DestroyAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'id'

	def delete(self, request, *args, **kwargs):
		try:
			user = User.objects.get(pk=kwargs["id"])
			serzUser = UserSerializer(user)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzUser.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username, rowId=user.id, action="delete", table_name="User", old_data=old_data)
			response = super(ClientUserDeleteView, self).delete(request, *args, **kwargs)
			if response.status_code == 200:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->UserDeletion : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ClientUserListView(ListAPIView):
	queryset = User.objects.all().exclude(profile__cid=None)
	serializer_class = ClientUserSerializer

class ClientUserListView2(ListAPIView):
	queryset = Client.objects.all()
	serializer_class = ClientUserSerializer2

class ClientUserActivateView(APIView):
	def post(self, request, *args, **kwargs):
		try:
			user = User.objects.get(pk=kwargs['id'])
			print(user.is_active)
			user.is_active = True
			user.save()
			audit = AuditTrail.objects.create(user=request.user.username, rowId=user.id, action="Activate", table_name="User")
			audit.save()
			if 'mail' in request.data and request.data['mail'] == True:
				mail(to_address=user.email, username=user.username, purpose="activate",link="https://35.237.170.221/#/auth/activate?uid={id}&token={token}"
					 .format(id=urlsafe_base64_encode(force_bytes(user.id)),token=user.profile.key), companyName=user.profile.cid.Name)
			return Response({"info":"User Activated Succesfully"},status=200)
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->UserActivation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ClientUserInActivateView(APIView):
	def post(self, request, *args, **kwargs):
		try:
			user = User.objects.get(pk=kwargs['id'])
			print(user.is_active)
			user.is_active = False
			user.save()
			audit = AuditTrail.objects.create(user=request.user.username, rowId=user.id, action="InActivate", table_name="User")
			audit.save()
			return Response({"info":"User InActivated Succesfully"},status=200)
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->UserDeactivation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ClientCreateView(CreateAPIView):
	queryset = Client.objects.all()
	serializer_class = ClientSerializer

	def create(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			objs = Client.objs.filter(Q(Name=request.data['Name']) | Q(CusId=request.data['CusId']))
			existClient = None
			if objs.exists():
				existClient = objs.first()
				print(existClient)
				if not existClient.isArchived:
					return Response({"message": "Already a Client is present with the given Name or CusID"}, status=400)
			if existClient and existClient.isArchived:
				existClient.isArchived = False
				existClient.save()
				data = ClientSerializer(existClient, data=request.data)
				if data.is_valid():
					obj1 = data.save()
					audit = AuditTrail.objects.create(user=request.user.username, rowId=existClient.id, action="Create",
													  table_name="Client", new_data=new_data)
					audit.save()
					return Response({"output": "Client created successfully","client":ClientSerializer(obj1).data}, status=201)
				return Response({"output": "Error in data"},
								status=400)
			response = super(ClientCreateView, self).create(request, *args, **kwargs)
			audit = AuditTrail.objects.create(user=request.user.username,rowId=response.data['id'], action="Create", table_name="Client",
											  new_data=new_data)
			if response.status_code == 201:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->ClientCreation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ClientListView(ListAPIView):
	def get(self, *args, **kwargs):
		try:
			queryset = Client.objects.all()
			objs = ClientSerializer(queryset,many=True)
			context = {}
			context['clients'] = objs.data
			return Response(context)
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->ClientListRetrieval : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ClientDetailView(RetrieveAPIView):
	queryset = Client.objects.all()
	serializer_class = ClientSerializer
	lookup_field = 'id'

class ClientUpdateView(RetrieveUpdateAPIView):
	queryset = Client.objects.all()
	serializer_class = ClientSerializer
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			client = Client.objects.get(pk=kwargs["id"])
			serzClient = ClientSerializer(client)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzClient.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=client.id,action="Update",table_name="Client",new_data=new_data,old_data=old_data)
			response = super(ClientUpdateView, self).update(request, *args, **kwargs)
			if response.status_code == 200:
				audit.save()
				print("saved")
			return response
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->ClientUpdation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ClientDeleteView(DestroyAPIView):
	queryset = Client.objects.all()
	serializer_class = ClientSerializer
	lookup_field = 'id'

	def delete(self, request, *args, **kwargs):
		try:
			client = Client.objects.get(pk=kwargs["id"])
			serzClient = ClientSerializer(client)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzClient.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=client.id,action="Delete",table_name="Client",old_data=old_data)
			audit.save()
			client.isArchived = True
			client.save()
			return Response(status=204)
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->ClientDeletion : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class HCICreateView(CreateAPIView):
	queryset = HCI.objects.all()
	serializer_class = HCISerializer

	def create(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			print(new_data)
			objs = HCI.objs.filter(MachineID=request.data['MachineID'])
			existHCI = None
			if objs.exists():
				existHCI = objs.first()
				print(existHCI)
				if not existHCI.isArchived:
					return Response({"message": "Already a HCI is present with the given HCI ID"}, status=400)
			if existHCI and existHCI.isArchived:
				existHCI.isArchived = False
				existHCI.save()
				data = HCISerializer(existHCI, data=request.data)
				if data.is_valid():
					obj1 = data.save()
					audit = AuditTrail.objects.create(user=request.user.username, rowId=existHCI.id, action="Create",
													  table_name="HCI", new_data=new_data)
					audit.save()
					return Response({"output": "HCI created successfully", "HCI": HCISerializer(obj1).data},
									status=201)
				return Response({"output": "Error in data"},
								status=400)
			response = super(HCICreateView, self).create(request, *args, **kwargs)
			audit = AuditTrail.objects.create(user=request.user.username,rowId=response.data['id'],action="Create",table_name="HCI",new_data=new_data)
			if response.status_code == 201:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->HCICreate : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class HCIListView(ListAPIView):
	queryset = HCI.objects.all()
	serializer_class = HCIDetailSerializer

	def get_queryset(self):
		try:
			queryset_list = HCI.objects.all()
			query = self.request.GET.get("cid")
			if query:
				queryset_list = queryset_list.filter(Customer=query)
			return queryset_list
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->HCIListRetrieval : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class HCIDetailView(RetrieveAPIView):
	queryset = HCI.objects.all()
	serializer_class = HCIDetailSerializer
	lookup_field = 'id'

class HCIUpdateView(RetrieveUpdateAPIView):
	queryset = HCI.objects.all()
	serializer_class = HCIDetailSerializer
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			hci = HCI.objects.get(pk=kwargs["id"])
			serzHCI = HCISerializer(hci)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzHCI.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=hci.id,action="Update",table_name="HCI",new_data=new_data,old_data=old_data)
			response = super(HCIUpdateView, self).update(request, *args, **kwargs)
			if response.status_code == 200:
				audit.save()
				print("saved")
			return response
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->HCIUpdation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class HCIDeleteView(DestroyAPIView):
	queryset = HCI.objects.all()
	serializer_class = HCISerializer
	lookup_field = 'id'

	def delete(self, request, *args, **kwargs):
		try:
			hci = HCI.objects.get(pk=kwargs["id"])
			serzHCI = HCISerializer(hci)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzHCI.data.items() if key != "id")
			print (old_data)
			audit = AuditTrail.objects.create(user=request.user.username,rowId=hci.id,action="Delete",table_name="HCI",old_data=old_data)
			audit.save()

			hciObj = HCI.objects.get(pk=kwargs["id"])
			hciObj.isArchived = True
			hciObj.save()
			return Response(status=204)
		except Exception as error:
			print(error)
			logging("ERROR : ClientApp->HCIDeletion : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)