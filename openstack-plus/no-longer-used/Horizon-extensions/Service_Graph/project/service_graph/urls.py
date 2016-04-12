from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.project.service_graph import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^ajax_vnf$', views.GetVnfInformation, name='ajaxvnfdata'),
    url(r'^ajax_save$', views.saveServiceGraph, name='ajaxsaveservicegraph'),
    url(r'^ajax_load$', views.loadServiceGraph, name='ajaxloadservicegraph'),				   					  
)
