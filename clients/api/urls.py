from django.conf.urls import url, include
from clients.api.views import ( ClientCreateView, ClientListView, ClientDetailView,
								ClientDeleteView, ClientUpdateView, HCICreateView,
								HCIListView, HCIDetailView, HCIDeleteView, 
								HCIUpdateView, ClientUserCreateView, ClientUserListView,
								ClientUserUpdateView, ClientUserActivateView, ClientUserInActivateView,
								ClientUserDeleteView, ClientUserListView2)
from django.urls import path

urlpatterns = [
	url(r'^create/$', ClientCreateView.as_view(), name="create"),
	url(r'^$', ClientListView.as_view(), name="list"),
	url(r'^user/create/$', ClientUserCreateView.as_view(), name="usercreate"),
	url(r'^user/(?P<id>\d+)/activate/$', ClientUserActivateView.as_view(), name="useractivate"),
	url(r'^user/(?P<id>\d+)/inactivate/$', ClientUserInActivateView.as_view(), name="userinactivate"),
	url(r'^user/(?P<id>\d+)/edit/$', ClientUserUpdateView.as_view(), name="useredit"),
	url(r'^user/(?P<id>\d+)/delete/$', ClientUserDeleteView.as_view(), name="userdelete"),
	url(r'^user/$', ClientUserListView.as_view(), name="userlist"),
	url(r'^users/$', ClientUserListView2.as_view(), name="userlist2"),
	url(r'^hci/create/$', HCICreateView.as_view(), name="hcicreate"),
	url(r'^hci/$', HCIListView.as_view(), name="hcilist"),
	url(r'^hci/(?P<id>\d+)/$', HCIDetailView.as_view(), name="hcidetail"),
	url(r'^hci/(?P<id>\d+)/edit/$', HCIUpdateView.as_view(), name="hciupdate"),
	url(r'^hci/(?P<id>\d+)/delete/$', HCIDeleteView.as_view(), name="hcidelete"),
	url(r'^(?P<id>\d+)/edit/$', ClientUpdateView.as_view(), name="update"),
	url(r'^(?P<id>\d+)/delete/$', ClientDeleteView.as_view(), name="delete"),
	url(r'^(?P<id>\d+)/$', ClientDetailView.as_view(), name="detail"),
]