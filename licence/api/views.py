from rest_framework.generics import ( ListAPIView, RetrieveAPIView,
									UpdateAPIView, DestroyAPIView,
									CreateAPIView, RetrieveUpdateAPIView,
									RetrieveUpdateDestroyAPIView, ListCreateAPIView)
from rest_framework.views import APIView
from licence.models import Licence, Application, AppUpdate, GitUpdate
from users.models import AuditTrail
from clients.models import Client, HCI
from rest_framework.permissions import ( AllowAny, IsAuthenticated,
										IsAdminUser, IsAuthenticatedOrReadOnly )
from .serializers import ( LicenceCreateSerializer,
						LicenceSerializer, ApplicationSerializer, LicenceDetailSerializer,
						LicenceGraceTrailUpdateSerializer, LicenceUpdateSerializer,
						LicenceCreateArchiveSerializer, AppUpdateSerializer,
						GitUpdateSerializer, ApplicationArchiveSerializer)
from .mixin import MultipleFieldLookupMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from orders.api.serializers import OrderSerializer, OrderCreateUpdateSerializer, OrderGraceUpdateSerializer
from orders.models import Order
from django.contrib.auth import get_user_model
import datetime, time
from rest_framework.response import Response
from users.mail_utility import mail
from users.utils import logging

User = get_user_model()

class ApplicationCreateView(CreateAPIView):
	queryset = Application.objects.all()
	serializer_class = ApplicationSerializer

	def create(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			objs = Application.objs.filter(ApplicationName=request.data['ApplicationName'])
			existApp = None
			if objs.exists():
				existApp = objs.first()
				print(existApp)
				if not existApp.isArchived:
					return Response({"message": "Already a Application is present with the given Application Name"}, status=400)
			if existApp and existApp.isArchived:
				request.data['isArchived'] = False
				data = ApplicationArchiveSerializer(existApp, data=request.data)
				if data.is_valid():
					app = data.save()
					audit = AuditTrail.objects.create(user=request.user.username, rowId=app.id, action="Create",
													  table_name="App", new_data=new_data)
					audit.save()
					return Response({"output":"Application created successfully"},status=201)
				else:
					return Response({"output": data.errors}, status=400)
			response = super(ApplicationCreateView, self).create(request, *args, **kwargs)
			audit = AuditTrail.objects.create(user=request.user.username,rowId=response.data['id'], action="Create",
											  table_name="App", new_data=new_data)
			if response.status_code == 201:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->ApplicationCreation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ApplicationListView(ListAPIView):
	queryset = Application.objects.all()
	serializer_class = ApplicationSerializer

# class ApplicationDetailView(RetrieveAPIView):
# 	queryset = Application.objects.all()
# 	serializer_class = ApplicationSerializer
# 	lookup_field = 'id'

class ApplicationUpdateView(RetrieveUpdateDestroyAPIView):
	queryset = Application.objects.all()
	serializer_class = ApplicationSerializer
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			application = Application.objects.get(pk=kwargs['id'])
			serzApp = ApplicationSerializer(application)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzApp.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=application.id,action="Update",table_name="App",new_data=new_data,old_data=old_data)
			response = super(ApplicationUpdateView, self).update(request, *args, **kwargs)
			if response.status_code == 200:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->ApplicationUpdate : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

	def delete(self, request, *args, **kwargs):
		try:
			appObj = Application.objects.get(pk=kwargs["id"])
			serzApp = ApplicationSerializer(appObj)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzApp.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=appObj.id,action="Delete",table_name="App",old_data=old_data)
			audit.save()

			appObj.isArchived = True
			appObj.save()
			return Response(status=204)
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->ApplicationDeletion : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

# class ApplicationDeleteView(DestroyAPIView):
# 	queryset = Application.objects.all()
# 	serializer_class = ApplicationSerializer
# 	lookup_field = 'id'

class AppUpdateView(MultipleFieldLookupMixin, ListCreateAPIView):
	queryset = AppUpdate.objects.all().order_by('-created')
	serializer_class = AppUpdateSerializer
	lookup_fields = ['app']
	ordering = ['-created']

	def create(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			objs = AppUpdate.objs.filter(version=request.data['version'])
			existApp = None
			if objs.exists():
				existApp = objs.first()
				print(existApp)
				if not existApp.isArchived:
					return Response({"message": "Already this App Version is present"}, status=400)
			if existApp and existApp.isArchived:
				request.data['isArchived'] = False
				data = AppUpdateSerializer(existApp, data=request.data)
				if data.is_valid():
					app = data.save()
				# existApp.isArchived = False
				# existApp = AppUpdate(id=existApp.id, **data)
				# existApp.save()
				audit = AuditTrail.objects.create(user=request.user.username, rowId=existApp.id, action="Create",
												  table_name="AppUpdate", new_data=new_data)
				audit.save()
				return Response({"output":"Application Update details created successfully"},status=201)
			response = super(AppUpdateView, self).create(request, *args, **kwargs)
			audit = AuditTrail.objects.create(user=request.user.username,rowId=response.data['id'], action="Create",
											  table_name="AppUpdate", new_data=new_data)
			if response.status_code == 201:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->AppUpdateCreation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class AppUpdateRDEView(MultipleFieldLookupMixin, RetrieveUpdateDestroyAPIView):
	queryset = AppUpdate.objects.all()
	serializer_class = AppUpdateSerializer
	lookup_fields = ['app', 'id']
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			app_update = AppUpdate.objects.get(pk=kwargs['id'])
			serzApp = AppUpdateSerializer(app_update)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzApp.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=app_update.id,action="Update",table_name="AppUpdate",new_data=new_data,old_data=old_data)
			response = super(AppUpdateRDEView, self).update(request, *args, **kwargs)
			if response.status_code == 200:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->AppUpdateUpdate : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

	def delete(self, request, *args, **kwargs):
		try:
			appObj = AppUpdate.objects.get(pk=kwargs["id"])
			serzApp = AppUpdateSerializer(appObj)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzApp.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=appObj.id,action="Delete",table_name="AppUpdate",old_data=old_data)
			audit.save()

			appObj.isArchived = True
			appObj.save()
			return Response(status=204)
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->AppUpdateDeletion : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class GitUpdateView(MultipleFieldLookupMixin, ListCreateAPIView):
	queryset = GitUpdate.objects.all().order_by('-created')
	serializer_class = GitUpdateSerializer
	lookup_fields = ['app']
	ordering = ['-created']

	def create(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			objs = GitUpdate.objs.filter(version=request.data['version'])
			existApp = None
			if objs.exists():
				existApp = objs.first()
				print(existApp)
				if not existApp.isArchived:
					return Response({"message": "Already this App Version is present"}, status=400)
			if existApp and existApp.isArchived:
				request.data['isArchived'] = False
				data = GitUpdateSerializer(existApp, data=request.data)
				if data.is_valid():
					app = data.save()
				# existApp.isArchived = False
				# existApp = GitUpdate(id=existApp.id, **data)
				# existApp.save()
				audit = AuditTrail.objects.create(user=request.user.username, rowId=existApp.id, action="Create",
												  table_name="GitUpdate", new_data=new_data)
				audit.save()
				return Response({"output":"Git Update details created successfully"},status=201)
			response = super(GitUpdateView, self).create(request, *args, **kwargs)
			audit = AuditTrail.objects.create(user=request.user.username,rowId=response.data['id'], action="Create",
											  table_name="GitUpdate", new_data=new_data)
			if response.status_code == 201:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->GitUpdateCreation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class GitUpdateRDEView(MultipleFieldLookupMixin, RetrieveUpdateDestroyAPIView):
	queryset = GitUpdate.objects.all()
	serializer_class = GitUpdateSerializer
	lookup_fields = ['app', 'id']
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			git_update = GitUpdate.objects.get(pk=kwargs['id'])
			serzData = GitUpdateSerializer(git_update)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzData.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=git_update.id,action="Update",table_name="GitUpdate",new_data=new_data,old_data=old_data)
			response = super(GitUpdateRDEView, self).update(request, *args, **kwargs)
			if response.status_code == 200:
				audit.save()
			return response
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->GitUpdateUpdate : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

	def delete(self, request, *args, **kwargs):
		try:
			git_update = GitUpdate.objects.get(pk=kwargs["id"])
			serzData = GitUpdateSerializer(git_update)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzData.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=git_update.id,action="Delete",table_name="GitUpdate",old_data=old_data)
			audit.save()

			git_update.isArchived = True
			git_update.save()
			return Response(status=204)
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->GitUpdateDeletion : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class LicenceCreateView(CreateAPIView):
	queryset = Licence.objects.all()
	serializer_class = LicenceSerializer

	def create(self,request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			macid = request.data['MachineID']
			appid = request.data['App']
			objs = Licence.objs.filter(MachineID=macid,App=appid)
			existLic = None
			if objs.exists():
				existLic = objs.first()
				print(existLic)
				if not existLic.isArchived:
					return Response({"message":"Already a Licence is present for the given HCI and Application"}, status=400)
			order = OrderCreateUpdateSerializer(data = request.data)
			if order.is_valid():
				obj1 = order.save()
				# mod_data = request.data.copy()
				request.data['OrderID'] = obj1.id
				if existLic and existLic.isArchived:
					request.data['isArchived'] = False
					data = LicenceCreateArchiveSerializer(existLic, data= request.data)
				else:
					data = LicenceCreateSerializer(data= request.data)
				if data.is_valid():
					obj2 = data.save()
					audit = AuditTrail.objects.create(user=request.user.username,rowId=obj2.id,action="Create", table_name="Licence",
													  new_data=new_data)
					audit.save()
					purpose = ""
					users = User.objects.filter(profile__cid=obj2.MachineID.Customer)
					if users.exists():
						print("yes users are presentr")
						for user in users:
							if user.is_active == True:
								print(user)
								if request.data['period'] == 77:
									purpose = "licenceNotify"
									mail(to_address=user.email, username=user.username, purpose=purpose, link=None,
										 hciId=obj2.MachineID.MachineID, app=obj2.App.ApplicationName,
										 grace="-",
										 start="-"
										 , end="-", companyName=user.profile.cid.Name)
								elif 'trial' in request.data and request.data['trial']:
									purpose = "trialNotify"
									mail(to_address=user.email, username=user.username, purpose=purpose,link=None, hciId=obj2.MachineID.MachineID, app=obj2.App.ApplicationName, grace=(obj2.graceExpiryDate-obj2.graceIssueDate).days+1, start=obj2.graceIssueDate.strftime('%d-%m-%Y')
										 , end=obj2.graceExpiryDate.strftime('%d-%m-%Y'), companyName=user.profile.cid.Name)
								elif 'trial' not in request.data or ('trial' in request.data and not request.data['trial']):
									purpose = "licenceNotify"
									mail(to_address=user.email, username=user.username, purpose=purpose,link=None, hciId=obj2.MachineID.MachineID, app=obj2.App.ApplicationName, grace=(obj2.graceExpiryDate-obj2.graceIssueDate).days+1, start=obj2.OrderID.orderStartDate.strftime('%d-%m-%Y')
										 , end=obj2.expiryDate.strftime('%d-%m-%Y'), companyName=user.profile.cid.Name)
					return Response({"order":OrderSerializer(obj1).data,"licence":LicenceDetailSerializer(obj2).data})
				print(data.errors)
			print(order.errors)
			return Response({"error":"Failed to create"},status=400)
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->LicenceCreation : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class LicenceDeleteView(DestroyAPIView):
	queryset = Licence.objects.all()
	serializer_class = LicenceDetailSerializer
	lookup_field = 'id'

	def destroy(self, request, *args, **kwargs):
		try:
			licObj = Licence.objects.get(pk=kwargs["id"])
			serzLicence = LicenceSerializer(licObj)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzLicence.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=licObj.id,action="Delete",table_name="Licence",old_data=old_data)
			audit.save()

			licObj.isArchived = True
			licObj.save()
			return Response(status=204)
			# obj = self.get_object()
			# order = obj.OrderID
			# order.delete()
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->LicenceDeletion : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class LicenceDetailView(RetrieveAPIView):
	queryset = Licence.objects.all()
	serializer_class = LicenceDetailSerializer
	lookup_field = 'id'

class LicenceListView(ListAPIView):
	queryset = Licence.objects.all()
	serializer_class = LicenceDetailSerializer

	def get_queryset(self):
		try:
			queryset_list = Licence.objects.all()
			mid = self.request.GET.get("mid")
			appid = self.request.GET.get("appid")
			cid = self.request.GET.get("cid")
			if mid:
				queryset_list = queryset_list.filter(MachineID=mid)
			return queryset_list
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->LicenceListRetrieval : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class LicenceUpdateView(RetrieveUpdateAPIView):
	queryset = Licence.objects.all()
	serializer_class = LicenceDetailSerializer
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			licence = Licence.objects.get(pk=kwargs['id'])
			serzLice = LicenceSerializer(licence)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzLice.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=licence.id,action="Update",table_name="Licence",new_data=new_data,old_data=old_data)
			flag = 0
			if licence.issueDate == licence.OrderID.orderStartDate:
				flag = 1
			order = OrderCreateUpdateSerializer(licence.OrderID,data=request.data)
			if order.is_valid():
				obj1 = order.save()
				request.data['OrderID'] = obj1.id
				if flag == 1:
					licence = LicenceCreateSerializer(licence,data=request.data)
				else:
					licence = LicenceUpdateSerializer(licence,data=request.data)
				if licence.is_valid():
					obj2 = licence.save()
					audit.save()
					return Response({"order":OrderSerializer(obj1).data,"licence":LicenceDetailSerializer(obj2).data})
				else:
					print(licence.errors)
			print(order.errors)
			return Response({"error":"Failed to create"},status=400)
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->LicenceUpdate : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class LicenceRenewView(RetrieveUpdateAPIView):
	queryset = Licence.objects.all()
	serializer_class = LicenceDetailSerializer
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			licence = Licence.objects.get(pk=kwargs['id'])
			serzLice = LicenceSerializer(licence)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzLice.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=licence.id,action="Renew",table_name="Licence",new_data=new_data,old_data=old_data)
			order = OrderCreateUpdateSerializer(data=request.data)
			if order.is_valid():
				obj1 = order.save()
				mutable = request.POST._mutable
				request.POST._mutable = True
				request.data['OrderID'] = obj1.id
				request.POST._mutable = mutable
				licence = Licence.objects.get(pk=kwargs['id'])
				licence = LicenceUpdateSerializer(licence,data=request.data)
				if licence.is_valid():
					obj2 = licence.save()
					print(obj2)
					audit.save()
					purpose = ""
					users = User.objects.filter(profile__cid=obj2.MachineID.Customer)
					if users.exists():
						print("yes users are presentr")
						for user in users:
							if user.is_active == True:
								print(user)
								if request.data['period'] == 77:
									purpose = "licenceNotify"
									mail(to_address=user.email, username=user.username, purpose=purpose, link=None,
										 hciId=obj2.MachineID.MachineID, app=obj2.App.ApplicationName,
										 grace="-",
										 start="-"
										 , end="-", companyName=user.profile.cid.Name)
								elif 'trial' in request.data and request.data['trial']:
									purpose = "trialNotify"
									mail(to_address=user.email, username=user.username, purpose=purpose, link=None, hciId=obj2.MachineID.MachineID,
										 app=obj2.App.ApplicationName, grace=(obj2.graceExpiryDate-obj2.graceIssueDate).days+1,
										 start=obj2.graceIssueDate.strftime('%d-%m-%Y'), end=obj2.graceExpiryDate.strftime('%d-%m-%Y'), companyName=user.profile.cid.Name)
								elif 'trial' not in request.data or ('trial' in request.data and not request.data['trial']):
									purpose = "licenceNotify"
									mail(to_address=user.email, username=user.username, purpose=purpose, link=None, hciId=obj2.MachineID.MachineID,
										 app=obj2.App.ApplicationName, grace=(obj2.graceExpiryDate-obj2.graceIssueDate).days+1, start=obj2.OrderID.orderStartDate.strftime('%d-%m-%Y'), end=obj2.expiryDate.strftime('%d-%m-%Y'), companyName=user.profile.cid.Name)
					return Response({"order":OrderSerializer(obj1).data,"licence":LicenceDetailSerializer(obj2).data})
				print(licence.errors)
			else:
				print(order.errors)
			return Response({"Error":"Wrong Input"}, status=400)
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->LicenceRenewal : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class LicenceGraceRenewView(RetrieveUpdateAPIView):
	queryset = Licence.objects.all()
	serializer_class = LicenceGraceTrailUpdateSerializer
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		try:
			data = request.data
			new_data = "; ".join("{0} = {1}".format(key, value) for key, value in data.items())
			licence = Licence.objects.get(pk=kwargs['id'])
			serzLice = LicenceSerializer(licence)
			old_data = "; ".join("{0} = {1}".format(key, value) for key, value in serzLice.data.items() if key != "id")
			audit = AuditTrail.objects.create(user=request.user.username,rowId=licence.id,action="GraceRenew",table_name="Licence",new_data=new_data,old_data=old_data)
			order = OrderGraceUpdateSerializer(licence.OrderID,data=request.data)
			if order.is_valid():
				obj1 = order.save()
				order = licence.OrderID
				order.graceCount += 1
				# if order.is_valid():
				obj1 = order.save()
			# mutable = request.POST._mutable
			# request.POST._mutable = True
			# request.data['OrderID'] = obj1.id
			# request.POST._mutable = mutable
				licence = Licence.objects.get(pk=kwargs['id'])
				licence = LicenceGraceTrailUpdateSerializer(licence,data=request.data)
				if licence.is_valid():
					obj2 = licence.save()
					print(obj2)
					audit.save()
					purpose = "graceNotify"
					users = User.objects.filter(profile__cid=obj2.MachineID.Customer)
					if users.exists():
						print("yes users are presentr")
						for user in users:
							if user.is_active == True:
								print(user)
								mail(to_address=user.email, username=user.username, purpose=purpose, link=None, hciId=obj2.MachineID.MachineID,
									 app=obj2.App.ApplicationName, grace=(obj2.graceExpiryDate-obj2.graceIssueDate).days+1, start=obj2.graceIssueDate.strftime('%d-%m-%Y')
									 , end=obj2.graceExpiryDate.strftime('%d-%m-%Y'), companyName=user.profile.cid.Name)
					return Response({"order":OrderSerializer(order).data,"licence":LicenceDetailSerializer(obj2).data})
				print(licence.errors)
			return Response({"Error":"Wrong Input"}, status=400)
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->LicenceGraceRenew : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ReportOnLicence(APIView):

	def post(self, request):
		try:
			queryset_list = Licence.objects.all()
			if "cid" in request.data and request.data["cid"]:
				machines = HCI.objects.filter(Customer__in =  request.data["cid"])
				queryset_list = queryset_list.filter(MachineID__in = machines)

			if "mid" in request.data and request.data["mid"]:
				queryset_list = queryset_list.filter(MachineID__in = request.data["mid"])

			if "appid" in request.data and request.data["appid"]:
				queryset_list = queryset_list.filter(App__in = request.data["appid"])

			if "statusAlive" in request.data and request.data["statusAlive"] is not None:
				date = datetime.datetime.today()
				if request.data["statusAlive"] == "Active":
					queryset_list = queryset_list.filter(expiryDate__gte = date)
				elif request.data["statusAlive"] == "Ingrace":
					queryset_list = queryset_list.filter(graceExpiryDate__gte = date, expiryDate__lt = date, trial=False)
				elif request.data["statusAlive"] == "Expired":
					queryset_list = queryset_list.filter(graceExpiryDate__lt = date)
				elif request.data["statusAlive"] == "Trail":
					queryset_list = queryset_list.filter(trial = True, graceExpiryDate__gte = date)
				elif request.data["statusAlive"] == "Perpetual":
					queryset_list = queryset_list.filter(OrderID__period = 77)

			if "issueStartDate" in request.data and request.data['issueStartDate']:
				date = request.data['issueStartDate']
				date = datetime.datetime.strptime(date,"%d-%m-%Y").date()
				queryset_list = queryset_list.filter(issueDate__gte = date)

			if "issueEndDate" in request.data and request.data['issueEndDate']:
				date = request.data['issueEndDate']
				date = datetime.datetime.strptime(date,"%d-%m-%Y").date()
				queryset_list = queryset_list.filter( issueDate__lte =  date)

			if "expiryStartDate" in request.data and request.data['expiryStartDate']:
				date = request.data['expiryStartDate']
				date = datetime.datetime.strptime(date,"%d-%m-%Y").date()
				queryset_list = queryset_list.filter(expiryDate__gte = date)

			if "expiryEndDate" in request.data and request.data['expiryEndDate']:
				date = request.data['expiryEndDate']
				date = datetime.datetime.strptime(date,"%d-%m-%Y").date()
				queryset_list = queryset_list.filter( expiryDate__lte =  date)

			# if "gracePeriod" in request.data and request.data['gracePeriod'] is not None:
			# 	date = datetime.datetime.today()
			# 	if request.data['gracePeriod']:
			# 		queryset_list = queryset_list.filter(graceExpiryDate__gte = date)
			# 	else:
			# 		queryset_list = queryset_list.filter(graceExpiryDate__lte = date)

			serData = LicenceDetailSerializer(queryset_list,many=True)
			return Response(serData.data,status=200)
		except ValueError:
			return Response({"Error": "Wrong Request"}, status=400)
		except Exception as error:
			print(error)
			logging("ERROR : LicenceApp->Report : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)