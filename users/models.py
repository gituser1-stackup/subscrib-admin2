from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django_mysql.models import Model, JSONField

from users.utils import code_generator
from clients.models import Client

class UserProfile(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,related_name='profile')
	cid = models.ForeignKey(Client,on_delete=models.CASCADE,null=True,related_name='user', blank=True)
	firstLogin = models.BooleanField(default=True)
	key = models.CharField(max_length=120)
	reset = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		self.key = code_generator()
		super(UserProfile, self).save(*args, **kwargs)

	def __str__(self):
		return self.user.username

@receiver(post_save, sender=User)
def create_userprofile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)
		print('post save done')

@receiver(post_save, sender=UserProfile)
def post_save_activation_model_receiver(sender, instance, created, *args, **kwargs):
	if created:
		try:
			print("Activation Created")
			url = "https://10.0.0.96/activate/"+instance.key
		except:
			pass

# post_save.connect(post_save_activation_model_receiver,sender=UserProfile)

class SecurityQuestion(models.Model):
	question = models.TextField(max_length=300)
	optionA = models.CharField(max_length=80)
	optionB = models.CharField(max_length=80)
	optionC = models.CharField(max_length=80)
	optionD = models.CharField(max_length=80)
	optionE = models.CharField(max_length=80)

	def __str__(self):
		return self.question

class UserSecurityDetail(models.Model):
	userid = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	questionId = models.ForeignKey(SecurityQuestion,on_delete=models.CASCADE)
	value = models.CharField(max_length=120)

	class Meta:
		unique_together = ('userid','questionId')

class AuditTrail(Model):
	user = models.CharField(max_length=120)
	timestamp = models.DateTimeField(auto_now_add = True)
	action = models.CharField(max_length=120)
	table_name = models.CharField(max_length=120, null=True, blank=True)
	rowId = models.IntegerField()
	new_data = models.TextField(null=True, blank=True)
	old_data = models.TextField(null=True, blank=True)
	extra_info = JSONField()
	# ipaddress = models.CharField(max_length=30, null=True, blank=True)
	# mac_id = models.CharField(max_length=30, null=True, blank=True)


	def __str__(self):
		display = str(self.user)+ " " + str(self.action) + " " + str(self.table_name) + " " + str(self.timestamp)
		return display

class MacDuplication(models.Model):
	timestamp = models.DateTimeField(auto_now_add = True)
	rowId = models.IntegerField()
	ipaddress = models.CharField(max_length=30, null=True, blank=True)
	org_mac = models.CharField(max_length=30, null=True, blank=True)
	dup_mac = models.CharField(max_length=30, null=True, blank=True)
