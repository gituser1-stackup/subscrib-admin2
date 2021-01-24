from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
import datetime, time, pdb, json

from rest_auth.views import LoginView, LogoutView
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from django.contrib.auth.models import User
from users.models import SecurityQuestion, UserSecurityDetail, UserProfile, AuditTrail, MacDuplication
from .serializers import ( SecurityQuestionSerializer, UserSecurityDetailSerializer, AuditSerializer)
from licence.models import Licence, Application, AppUpdate, GitUpdate
from clients.models import HCI
from users.encrypt import encrypt_message

from django.core.serializers.json import DjangoJSONEncoder
import datetime, time, pdb, json
from datetime import date 
from datetime import timedelta 
import os

from users.utils import logging

class AuditView(APIView):

	def post(self,request):
		try:
			licId = request.data['id']
			tableName = request.data['table']
			if licId and licId != 0 and tableName!="":
				audits = AuditTrail.objects.filter(rowId=licId,table_name=tableName)
				if audits.exists() and audits.count() > 0:
					serdata = AuditSerializer(audits,many=True)
					return Response(serdata.data,status=200)
			return Response({"output":"No record is available"},status=200)
		except Exception as error:
			print(error)
			logging("ERROR : UserApp->AuditRetrieve : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class CustomLoginView(LoginView):
	def get_response(self):
		original_response = super(CustomLoginView,self).get_response()
		if original_response.status_code == 200 and self.user.profile.cid == None and (self.user.is_superuser == True or self.user.is_staff == True):
			if not self.user.username == 'user':
				audit = AuditTrail.objects.create(user=self.user.username,rowId=self.user.id,action="Login")
				audit.save()
			user_first_login = self.user.profile.firstLogin
			entry = {"isFirstLogin": user_first_login, "username": self.user.username }
			original_response.data.update(entry)
			return original_response
		return Response({"error": "Wrong Credentials"}, status=400)

class CustomLogoutView(LogoutView):
	def post(self, request, *args, **kwargs):
		try:
			username = request.user.username
			user_id = request.user.id
			original_response = super(CustomLogoutView,self).post(request, *args, **kwargs)
			if original_response.status_code == 200:
				if username != 'user':
					audit = AuditTrail.objects.create(user=username, rowId=user_id, action="Logout")
					audit.save()
			return original_response
		except Exception as error:
			print(error)
			logging("ERROR : UserApp->Logout : {0}.\n".format(error))
			return Response({"Error": "Internal Server Error"}, status=500)

class PasswordReset(APIView):

	permission_classes = (permissions.AllowAny,)

	def post(self,request):
		try:
			userid = request.data['userid']
			user = User.objects.filter(pk=userid)
			if user.exists() and user.count() == 1:
				user = user.first()
				userp = UserProfile.objects.get(user=userid)
				if userp.reset == True:
					user.set_password(request.data['password'])
					user.save()
					userp.reset = False
					userp.save()
					return Response({"output":"Successfully Password Reset"})
			print(request.data)
			return Response({"output":"Invalid User"},status=400)
		except Exception as error:
			print(error)
			logging("ERROR : UserApp->PassswordReset : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class UserSecurityDetailCreateView(ListCreateAPIView):
	queryset = UserSecurityDetail.objects.all()
	serializer_class = UserSecurityDetailSerializer

	def create(self, request, *args, **kwargs):
		try:
			quescount = SecurityQuestion.objects.all().count()
			count = 0
			for data in request.data['values']:
				obj = UserSecurityDetailSerializer(data=data)
				if obj.is_valid():
					obj.save()
					count += 1
				else:
					return Response({"error":"Failure, unable to add user reset details.","errors": obj.errors})
			if count == quescount:
				user = User.objects.get(username=request.user.username)
				userp = UserProfile.objects.get(user=user.pk)
				userp.firstLogin = False
				userp.save()
				print("Success")
				return Response({"Output":"Successfully added the User Reset Details."})
			print("Failure")
			return Response({"error": "Failure, unable to add user reset details."})
		except Exception as error:
			print(error)
			logging("ERROR : UserApp->UserSecurityQuestion : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ResetQuestion(APIView):

	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		try:
			user = User.objects.filter(username=request.user.username)
			if user.exists() and user.count() == 1:
				users = user.first()
				print(users.id)
				pkid = users.id
				queryset = SecurityQuestion.objects.all()
				qs = SecurityQuestionSerializer(queryset,many=True)
				return Response({"questions":qs.data,'userid':pkid})
			return Response({"error":"Invalid Username"},status=400)
		except Exception as error:
			print(error)
			logging("ERROR : UserApp->ResetQuestion(GET) : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)


	def post(self, request):
		try:
			print(request.data['username'])
			user = User.objects.filter(username=request.data['username'])
			if user.exists() and user.count() == 1:
				users = user.first()
				print(users.id)
				pkid = users.id
				queryset = SecurityQuestion.objects.all()
				qs = SecurityQuestionSerializer(queryset,many=True)
				return Response({"questions":qs.data,"userid":pkid})
			return Response({"error":"Invalid Username"},status=400)
		except Exception as error:
			print(error)
			logging("ERROR : UserApp->ResetQuestion(POST) : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class ResetVerification(APIView):

	permission_classes = (permissions.AllowAny,)

	def post(self,request):
		try:
			quescount = SecurityQuestion.objects.all().count()
			count = 0
			userpk = int()
			for data in request.data['values']:
				obj = UserSecurityDetail.objects.filter(userid=data['userid'],questionId=data['questionId'],value__iexact=data['value'])
				if obj.exists() and obj.count()==1:
					userpk = data['userid']
					count += 1
				else:
					return Response({"error":"Invalid User"},status=400)
			if count == quescount:
				userp = UserProfile.objects.get(user=userpk)
				userp.reset = True
				userp.save()
				return Response({"output":"Successfully Validated",'Reset':True})
			return Response({"output":"Invalid User","Reset":False},status=400)
		except Exception as error:
			print(error)
			logging("ERROR : UserApp->ResetVerification : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)

class GetLicence(APIView):

	def post(self, request):
		try:
			print(request.data)
			user = User.objects.filter(username="user")
			if not user.exists():
				usr = User.objects.create(username="user")
				usr.set_password("User@12#$")
				usr.save()
			appObj = Application.objects.get(id=request.data['appid'])
			hciObj = HCI.objects.get(id=request.data['mid'])
			ts = time.time()
			date = datetime.datetime.fromtimestamp(ts).date()
			data = {
				"username": "user",
				"mid": hciObj.MachineID,
				"appid": appObj.ApplicationName,
				"password": "User@12#$",
				"dummy": True
			}
			enc = encrypt_message(json.dumps(data,cls=DjangoJSONEncoder).encode('utf-8'))
			print(enc)
			licenceObj = Licence.objects.filter(MachineID=request.data['mid'],App=request.data['appid'])
			if licenceObj.exists() and licenceObj.count() == 1 and not licenceObj.first().isArchived:
				lic = licenceObj.first()
				orderObj = lic.OrderID
				data = {
					"username": "user",
					# "customer": lic.MachineID.Customer.Name,
					# "cusid": lic.MachineID.Customer.CusId,
					"mid": lic.MachineID.MachineID,
					"appid": lic.App.ApplicationName,
					"password": "User@12#$",
					"start": orderObj.orderStartDate,
					"expire": lic.expiryDate,
					"graceStart": lic.graceIssueDate,
					"graceExpire": lic.graceExpiryDate,
					"trial": lic.trial,
					"licence_attrs": lic.licence_attrs,
					"period": orderObj.period,
					"serverTime": date,
					"updated_on": lic.updated,
					"Category": lic.Category
				}
				enc = encrypt_message(json.dumps(data,cls=DjangoJSONEncoder).encode('utf-8'))
				print(data)
				return Response([{"data":enc}],status=200)
			return Response([{"msg":"dummy","data":enc}],status=200)
		except Exception as error:
			print(error)
			logging("ERROR : UserApp->GetLicence : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)
	

class LicenceVerification(APIView):

	def post(self, request):
		# print(request.data)
		category = { '0': 'POC category','1': 'Standard','2': 'Pro'}
		try:
			appObj = Application.objects.get(ApplicationName=request.data['appid'])
		except:
			return Response({"error":"Invalid Licence"},status=400)
		try:
			hciObj = HCI.objects.get(MachineID=request.data['mid'])
		except:
			return Response({"error":"Invalid Licence"},status=400)
		try:
			licenceObj = Licence.objects.filter(MachineID = hciObj, App = appObj)
			ts = time.time()
			date = datetime.datetime.fromtimestamp(ts).date()
			if licenceObj.exists() and licenceObj.count()==1 and not licenceObj.first().isArchived:
				if "dummy" in request.data:
					return Response({"message" : "update necessary","update" : True},status=200)
				else:
					now = datetime.datetime.today()
					licence = licenceObj.first()
					try:
						if "updated_on" in request.data:
							updated_on = datetime.datetime.strptime(request.data["updated_on"],"%Y-%m-%dT%H:%M:%S.%fZ")
						else:
							updated_on = None
					except:
						updated_on = None
					if updated_on == None or licence.updated.strftime('%Y-%m-%d %H:%M:%S') != updated_on.strftime('%Y-%m-%d %H:%M:%S'):
						msg = "Need to be updated"
						update = True
					else:
						msg = "Upto Date"
						update = False
					upgrade = []
					version_update = False
					appUpdate = AppUpdate.objects.filter(app=appObj, version__gt=request.data['version']).exclude(isArchived=True)
					# appUpdateLatest = None
					if appUpdate.exists():
						# appUpdateLatest = appUpdate.filter()
						for app_update in appUpdate.all():
							# if 'version' in request.data and update and\
							# 		update.version is not None and\
							# 		update.version > request.data['version']:
							upgrade.append({
								"version": app_update.version,
								"module": app_update.type,
								"details": app_update.details,
								"downloadZipName": app_update.downloadZipName
							})
						version_update = True
						# print(upgrade)
					print(request.data['Category'], licence.Category)
					if licence.Category != request.data['Category']:
						upgrade.append({
							"version": licence.Category,
							"module": "git",
							"type": "upgrade",
							"details": "Upgrade Playbook Category from {0} to {1}".format(category[request.data['Category']],
								category[licence.Category]),
							"downloadZipName": ""
						})
						version_update = True
					else:
						gitUpdate = GitUpdate.objects.filter(app=appObj).exclude(isArchived=True)
						gitUpdateLatest = None
						if gitUpdate.exists():
							gitUpdateLatest = gitUpdate.latest('created')
						if 'git' in request.data and gitUpdateLatest and\
								gitUpdateLatest.version is not None and\
								gitUpdateLatest.version > request.data['git']:
							upgrade.append({
								"version": gitUpdateLatest.version,
								"module": "git",
								"details": gitUpdateLatest.details,
								"downloadZipName": ""
							})
							version_update = True
					print(upgrade)
					return Response({"message" : msg,"update" : update, "version_update": version_update,
									 	"new_updates": upgrade},status=200)
			elif "dummy" not in request.data:
				return Response({"message" : "Licence Does'nt Exist","update":True},status=200)
			return Response({"message" : "Licence Does'nt Exist","update":False},status=200)
		except Exception as err:
			print(err)
			return Response({"message": "Internal server error", "error": str(err)}, status=500)

def LicenceCheck(licid, mac_id, ipaddress) :
	today = date.today()
	# yesterday = today - timedelta(days = 1)
	auditObj = AuditTrail.objects.filter(rowId = licid, table_name = "Licence", action = "Licence Key Update",
		timestamp__lte=today)
	if not auditObj.exists():
		return True
	for audit in auditObj.all():
		# print(audit.extra_info['mac_id'], mac_id)
		if 'mac_id' not in audit.extra_info or audit.extra_info['mac_id'] == None or\
			 audit.extra_info['mac_id'] == mac_id:
			continue
		else:
			print("audit failed")
			duplicatemac = MacDuplication.objects.create(rowId = licid, ipaddress = ipaddress,
				dup_mac = mac_id, org_mac = audit.extra_info['mac_id'])
			duplicatemac.save()
			return False
	return True

class LicenceUpdate(APIView):

	def post(self, request):
		try:
			appObj = Application.objects.get(ApplicationName=request.data['appid'])
		except:
			return Response({"error":"Invalid Licence"},status=400)
		try:
			hciObj = HCI.objects.get(MachineID=request.data['mid'])
		except:
			return Response({"error":"Invalid Licence"},status=400)
		try:
			licenceObj = Licence.objects.filter(MachineID = hciObj, App = appObj)
			ts = time.time()
			date = datetime.datetime.fromtimestamp(ts).date()
			if licenceObj.exists() and licenceObj.count() == 1 and not licenceObj.first().isArchived:
				lic = licenceObj.first()
				# print("Licence Update", lic.MachineID.Customer.Name, lic.MachineID.MachineID, lic.App.ApplicationName)
				# print(request.data['host_details'])
				licCheck = LicenceCheck(lic.id, request.data['host_details']['mac_id'], request.data['host_details']['ipaddress'])
				print("licence check ", licCheck)
				if licCheck == False:
					return Response({"error":"Invalid Licence"},status=400)
				audit = AuditTrail.objects.create(
					user=request.user.username,
					rowId=lic.id,
					action="Licence Key Update",
					table_name="Licence",
					extra_info = request.data['host_details']
				)
				audit.save()
				orderObj = lic.OrderID
				if lic.trial:
					data = {
						"username": "user",
						# "customer": lic.MachineID.Customer.Name,
						# "cusid": lic.MachineID.Customer.CusId,
						"mid": lic.MachineID.MachineID,
						"graceStart": lic.graceIssueDate,
						"graceExpire": lic.graceExpiryDate,
						"appid": lic.App.ApplicationName,
						"password": "User@12#$",
						"trial": lic.trial,
						"licence_attrs": lic.licence_attrs,
						"serverTime": date,
						"updated_on": lic.updated,
						"Category": lic.Category
					}
					encrypted_text = encrypt_message(json.dumps(data, cls=DjangoJSONEncoder).encode('utf-8'))
					return Response({"data":encrypted_text},status=200)
				if orderObj.period == 77:
					data = {
						"username": "user",
						# "customer": lic.MachineID.Customer.Name,
						# "cusid": lic.MachineID.Customer.CusId,
						"mid": lic.MachineID.MachineID,
						"start": orderObj.orderStartDate,
						"expire": None,
						"graceStart": None,
						"graceExpire": None,
						"appid": lic.App.ApplicationName,
						"password": "User@12#$",
						"trial": lic.trial,
						"licence_attrs": lic.licence_attrs,
						"period": orderObj.period,
						"serverTime": date,
						"updated_on": lic.updated,
						"Category": lic.Category
					}
				else:
					data = {
						"username": "user",
						# "customer": lic.MachineID.Customer.Name,
						# "cusid": lic.MachineID.Customer.CusId,
						"mid": lic.MachineID.MachineID,
						"start": orderObj.orderStartDate,
						"expire": lic.expiryDate,
						"graceStart": lic.graceIssueDate,
						"graceExpire": lic.graceExpiryDate,
						"appid": lic.App.ApplicationName,
						"password": "User@12#$",
						"trial": lic.trial,
						"licence_attrs": lic.licence_attrs,
						"period": orderObj.period,
						"serverTime": date,
						"updated_on": lic.updated,
						"Category": lic.Category
						
					}
				print(data)
				encrypted_text = encrypt_message(json.dumps(data, cls=DjangoJSONEncoder).encode('utf-8'))
				return Response({"data":encrypted_text},status=200)
			data = {
				"username": "user",
				# "customer": hciObj.Customer.Name,
				# "cusid": hciObj.Customer.CusId,
				"mid": hciObj.MachineID,
				"appid": appObj.ApplicationName,
				"password": "User@12#$",
				"dummy": True
			}
			encrypted_text = encrypt_message(json.dumps(data, cls=DjangoJSONEncoder).encode('utf-8'))
			return Response({"info":"Dummy Licence","data":encrypted_text},status=200)
		except Exception as err:
			print(err)
			return Response({"message": "Internal server error", "error": str(err)}, status=500)

def check_if_repo_is_up(repo_url):
	HOST_UP = True if os.system("ping -c 1 " + repo_url) is 0 else False
	return HOST_UP

@api_view(['POST'])
def update_repo_url(request):
	try:
		appObj = Application.objects.get(ApplicationName=request.data['appid'])
	except:
		return Response({"error":"Invalid Licence"},status=400)
	try:
		hciObj = HCI.objects.get(MachineID=request.data['mid'])
	except:
		return Response({"error":"Invalid Licence"},status=400)
	try:
		licenceObj = Licence.objects.filter(MachineID = hciObj, App = appObj)
		if licenceObj.exists() and licenceObj.count() == 1 and not licenceObj.first().isArchived:
			lic = licenceObj.first()
			repo_url = None
			if request.data['module'] == 'app':
				if check_if_repo_is_up(appObj.repoLink.split('/')[2].split(':')[0]):
					repo_url = appObj.repoLink
				elif check_if_repo_is_up(appObj.alternateRepoLink.split('/')[2].split(':')[0]):
					repo_url = appObj.alternateRepoLink
			if request.data['module'] == 'git':
				if lic.Category == '0':
					if check_if_repo_is_up(appObj.gitRepoLink.split('/')[2].split(':')[0]):
						repo_url = appObj.gitRepoLink
					elif check_if_repo_is_up(appObj.alternateGitRepoLink.split('/')[2].split(':')[0]):
						repo_url = appObj.alternateGitRepoLink
				if lic.Category == '1':
					if check_if_repo_is_up(appObj.gitRepoLinkBasic.split('/')[2].split(':')[0]):
						repo_url = appObj.gitRepoLinkBasic
					elif check_if_repo_is_up(appObj.alternateGitRepoLinkBasic.split('/')[2].split(':')[0]):
						repo_url = appObj.alternateGitRepoLinkBasic
				if lic.Category == '2':
					if check_if_repo_is_up(appObj.gitRepoLinkPro.split('/')[2].split(':')[0]):
						repo_url = appObj.gitRepoLinkPro
					elif check_if_repo_is_up(appObj.alternateGitRepoLinkPro.split('/')[2].split(':')[0]):
						repo_url = appObj.alternateGitRepoLinkPro
			if not repo_url:
				return Response({"error": "No Repo is UP. Please try after sometime."}, status=400)
			data = {
				"repo_url": repo_url
			}
		return Response(data, status=200)
	except Application.DoesNotExist:
		return Response({"error": "Object does not exist."}, status=400)
	except Exception as err:
		print(err)
		return Response({"error": "Some error as occured, please contact back-end"}, status=500)
