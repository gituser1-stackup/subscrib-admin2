from django.conf.urls import url, include
from .views import ( CustomLoginView, ResetVerification, CustomLogoutView,
					UserSecurityDetailCreateView, ResetQuestion,
					PasswordReset, LicenceVerification, LicenceUpdate,
					 GetLicence, AuditView, update_repo_url)

urlpatterns = [
	url(r'^login/$',CustomLoginView.as_view()),
	url(r'^logout/$',CustomLogoutView.as_view()),
	url(r'^audit/$',AuditView.as_view()),
	url(r'^reset_values', UserSecurityDetailCreateView.as_view()),
	url(r'^reset_questions', ResetQuestion.as_view()),
	url(r'^reset_verify', ResetVerification.as_view()),
	url(r'^licence_verify/$', LicenceVerification.as_view()),
	url(r'^repo_link/$', update_repo_url),
	url(r'^get_licence/$', GetLicence.as_view()),
	url(r'^licence_update/$', LicenceUpdate.as_view()),
	url(r'^reset', PasswordReset.as_view()),
	url(r'^',include('rest_auth.urls')),
	url(r'^',include('django.contrib.auth.urls'))
]