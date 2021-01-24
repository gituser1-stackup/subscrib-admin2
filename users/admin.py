from django.contrib import admin
from .models import ( UserProfile, SecurityQuestion,
					UserSecurityDetail, AuditTrail, MacDuplication )

class UserSecurityDetailsManager(admin.ModelAdmin):
	list_display = ['id','userid','questionId','value']
	list_editable = ['value']
	class Meta:
		model = UserSecurityDetail

class SecurityQuestionsManager(admin.ModelAdmin):
	list_display = ['id','question','optionA','optionB','optionC','optionD','optionE']
	list_editable = ['question','optionA','optionB','optionC','optionD','optionE']
	class Meta:
		model = SecurityQuestion

admin.site.register(UserSecurityDetail,UserSecurityDetailsManager)
admin.site.register(SecurityQuestion, SecurityQuestionsManager)
admin.site.register(UserProfile)
admin.site.register(AuditTrail)
admin.site.register(MacDuplication)