from django.db import models
from clients.models import HCI
from django_mysql.models import Model, JSONField


class Order(Model):
	MachineID = models.ForeignKey(HCI,on_delete=models.CASCADE)
	App = models.ForeignKey("licence.Application",on_delete=models.CASCADE)
	licence_attrs = JSONField()
	Category = models.CharField(default='0', max_length=2)
	trial = models.BooleanField(default=False)
	issueDate = models.DateField(auto_now=True)
	orderStartDate = models.DateField(null=True)
	period = models.IntegerField(null=True)
	expiryDate = models.DateField(null=True, blank=True)
	graceIssueDate = models.DateField(null=True, blank=True)
	graceExpiryDate = models.DateField(null=True, blank=True)
	graceCount = models.IntegerField(default=1)
	
	def __str__(self):
		return str(self.id)