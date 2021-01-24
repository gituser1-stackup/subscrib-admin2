from django.db import models
from clients.models import Client, HCI
from django.utils import timezone
from django_mysql.models import Model, JSONField
# Create your models here.

class ArchieveManager(models.Manager):
	def all(self, *args, **kwargs):
		qs = super(ArchieveManager, self).all(*args, **kwargs).exclude(isArchived=True)
		return qs

class Application(Model):
	ApplicationName = models.CharField(max_length=50,unique=True)
	repoLink = models.CharField(null=True, blank=True, max_length=80)
	alternateRepoLink = models.CharField(null=True, blank=True, max_length=80)
	gitRepoLink = models.CharField(null=True, blank=True, max_length=80)
	alternateGitRepoLink = models.CharField(null=True, blank=True, max_length=80)
	gitRepoLinkBasic = models.CharField(null=True, blank=True, max_length=80)
	alternateGitRepoLinkBasic = models.CharField(null=True, blank=True, max_length=80)
	gitRepoLinkPro = models.CharField(null=True, blank=True, max_length=80)
	alternateGitRepoLinkPro = models.CharField(null=True, blank=True, max_length=80)
	attrs = JSONField()
	isArchived = models.BooleanField(default=False)

	objs = models.Manager()
	objects = ArchieveManager()

	def __str__(self):
		return self.ApplicationName

class AppUpdate(Model):
	app = models.ForeignKey(Application, on_delete = models.CASCADE)
	downloadZipName = models.CharField(max_length=30)
	version = models.CharField(max_length=15)
	type = models.CharField(max_length=25)
	details = models.TextField()
	isArchived = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	objs = models.Manager()
	objects = ArchieveManager()

	def __str__(self):
		return self.app.ApplicationName + '_' + self.version

class GitUpdate(Model):
	app = models.ForeignKey(Application, on_delete = models.CASCADE)
	version = models.CharField(max_length=15)
	type = models.CharField(default='git', max_length=25)
	details = models.TextField()
	isArchived = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	objs = models.Manager()
	objects = ArchieveManager()

	def __str__(self):
		return self.app.ApplicationName + '_' + self.version

class LicenceManager(models.Manager):
	def all(self, *args, **kwargs):
		qs = super(LicenceManager, self).all(*args, **kwargs).exclude(isArchived=True).exclude(App__isArchived=True).exclude(MachineID__isArchived=True).exclude(MachineID__Customer__isArchived=True)
		return qs

class Licence(Model):
	App = models.ForeignKey(Application,on_delete=models.CASCADE)
	MachineID = models.ForeignKey(HCI,on_delete=models.CASCADE)
	licence_attrs = JSONField()
	trial = models.BooleanField(default=False)
	OrderID = models.ForeignKey("orders.Order",on_delete=models.CASCADE)
	issueDate = models.DateField()
	Category = models.CharField(default='0', max_length=2)
	expiryDate = models.DateField(null=True, blank=True)
	graceIssueDate = models.DateField(null=True, blank=True)
	graceExpiryDate = models.DateField(null=True, blank=True)
	isArchived = models.BooleanField(default=False)
	updated = models.DateTimeField(auto_now=True)

	objs = models.Manager()
	objects = LicenceManager()
	
	class Meta:
		unique_together = ('App','MachineID')
		
	def __str__(self):
		return str(self.id)
