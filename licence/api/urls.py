from django.conf.urls import url, include
from licence.api.views import ( LicenceCreateView, LicenceListView, LicenceDetailView,
								LicenceDeleteView, ApplicationCreateView, ApplicationListView, 
								# ApplicationDetailView, ApplicationDeleteView,
								ApplicationUpdateView, AppUpdateView, AppUpdateRDEView, GitUpdateView, GitUpdateRDEView,
								LicenceUpdateView, LicenceRenewView, LicenceGraceRenewView, ReportOnLicence)

urlpatterns = [
	url(r'^create/$', LicenceCreateView.as_view(), name="create"),
	url(r'^$', LicenceListView.as_view(), name="list"),
	url(r'^report/$', ReportOnLicence.as_view(), name="report"),
	url(r'^app/create/$', ApplicationCreateView.as_view(), name="appcreate"),
	url(r'^app/$', ApplicationListView.as_view(), name="applist"),
	url(r'app/(?P<id>\d+)/$', ApplicationUpdateView.as_view(), name="appdetail"),
	url(r'app/(?P<id>\d+)/edit/$', ApplicationUpdateView.as_view(), name="appedit"),
	url(r'app/(?P<id>\d+)/delete/$', ApplicationUpdateView.as_view(), name="appdelete"),
	url(r'app/(?P<app>\d+)/update/$', AppUpdateView.as_view(), name="appUpdate"),
	url(r'app/(?P<app>\d+)/update/(?P<id>\d+)/$', AppUpdateRDEView.as_view(), name="appUpdateRDE"),
	url(r'app/(?P<app>\d+)/git/$', GitUpdateView.as_view(), name="gitUpdate"),
	url(r'app/(?P<app>\d+)/git/(?P<id>\d+)/$', GitUpdateRDEView.as_view(), name="gitUpdateRDE"),
	url(r'(?P<id>\d+)/edit/$', LicenceUpdateView.as_view(), name="edit"),
	url(r'(?P<id>\d+)/renew/$', LicenceRenewView.as_view(), name="renew"),
	url(r'(?P<id>\d+)/grace/$', LicenceGraceRenewView.as_view(), name="grace"),
	url(r'(?P<id>\d+)/delete/$', LicenceDeleteView.as_view(), name="delete"),
	url(r'(?P<id>\d+)/$', LicenceDetailView.as_view(), name="detail")
]