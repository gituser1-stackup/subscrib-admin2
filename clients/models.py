from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class ClientManager(models.Manager):
	def all(self, *args, **kwargs):
		qs = super(ClientManager, self).all(*args, **kwargs).exclude(isArchived=True)
		return qs

class Client(models.Model):
	Name = models.CharField(max_length=50, unique=True)
	CusId = models.CharField(max_length=20,unique=True)
	Long = models.CharField(max_length=20,null=True, blank= True)
	Lat = models.CharField(max_length=20,null=True, blank=True)
	CustLoc = models.CharField(max_length=35,null=True, blank=True)
	isArchived = models.BooleanField(default=False)

	objs = models.Manager()
	objects = ClientManager()

	def __str__(self):
		return self.CusId

class HCIManager(models.Manager):
	def all(self, *args, **kwargs):
		qs = super(HCIManager, self).all(*args, **kwargs).exclude(isArchived=True).exclude(Customer__isArchived=True)
		return qs

class HCI(models.Model):
	MachineID = models.CharField(max_length=20,unique=True)
	Customer = models.ForeignKey(Client,on_delete=models.CASCADE)
	isArchived = models.BooleanField(default=False)

	objs = models.Manager()
	objects = HCIManager()

	def __str__(self):
		return self.MachineID
