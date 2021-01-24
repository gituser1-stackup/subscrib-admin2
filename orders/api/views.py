from rest_framework.generics import ( CreateAPIView, RetrieveAPIView,
									UpdateAPIView, ListAPIView,
									RetrieveUpdateAPIView, DestroyAPIView)
from rest_framework.views import APIView
from rest_framework.response import Response
from orders.models import Order
from clients.models import HCI
from .serializers import OrderSerializer
import datetime
from users.utils import logging

class OrderCreateView(CreateAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer

class OrderListView(ListAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer

class OrderDetailView(RetrieveAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	lookup_field = 	'id'

class OrderUpdateView(RetrieveUpdateAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	lookup_field = 'id'

class OrderDeleteView(DestroyAPIView):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	lookup_field = 'id'

class ReportOnOrder(APIView):

	def post(self, request):
		"""
		Method: POST
		Param request: CustomerId, MachineID, AppID, IssueStart-End, ExpiryStart-End, GracePerido
		return: List of Orders that matches the query passed
		Doing checkout process
		"""
		try:
			queryset_list = Order.objects.all()
			if "cid" in request.data and request.data["cid"]:
				machines = HCI.objects.filter(Customer__in =  request.data["cid"])
				queryset_list = queryset_list.filter(MachineID__in = machines)

			if "mid" in request.data and request.data["mid"]:
				queryset_list = queryset_list.filter(MachineID__in = request.data["mid"])

			if "appid" in request.data and request.data["appid"]:
				queryset_list = queryset_list.filter(App__in = request.data["appid"])

			if "statusAlive" in request.data and request.data["statusAlive"] is not None:
				date = datetime.datetime.today()
				if request.data["statusAlive"]:
					queryset_list = queryset_list.filter(expiryDate__gte = date)
				else:
					queryset_list = queryset_list.filter(expiryDate__lte = date)

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

			if "gracePeriod" in request.data and request.data['gracePeriod'] is not None:
				date = datetime.datetime.today()
				if request.data['gracePeriod']:
					queryset_list = queryset_list.filter(graceExpiryDate__gte = date)
				else:
					queryset_list = queryset_list.filter(graceExpiryDate__lte = date)

			serData = OrderSerializer(queryset_list,many=True)
			return Response(serData.data,status=200)
		except ValueError:
			return Response({"Error":"Wrong Input"}, status=400)
		except Exception as error:
			print(error)
			logging("ERROR : OrderApp->Report : {0}.\n".format(error))
			return Response({"Error": "Wrong Request"}, status=500)