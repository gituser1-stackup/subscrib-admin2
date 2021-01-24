from django.conf.urls import url
from .views import (OrderCreateView, OrderDetailView,
					OrderUpdateView, OrderListView, 
					OrderDeleteView, ReportOnOrder)

urlpatterns = [
	url(r'^$',OrderListView.as_view(),name='list'),
	url(r'^create/$',OrderCreateView.as_view(),name='create'),
	url(r'^report/$',ReportOnOrder.as_view(),name='report'),
	url(r'^(?P<id>\w+)/$',OrderDetailView.as_view(),name='detail'),
	url(r'^(?P<id>\w+)/edit/$',OrderUpdateView.as_view(),name='edit'),
	url(r'^(?P<id>\w+)/delete/$',OrderDeleteView.as_view(),name='delete')
]