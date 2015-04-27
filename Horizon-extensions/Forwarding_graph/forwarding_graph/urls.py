from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.admin.forwarding_graph import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^\?tab=mypanel_tabs_tab$', views.IndexView.as_view(), name='mypanel_tabs'),
	url(r'^ajax_data_request$', views.GetAjaxData, name='ajaxdata'),
	url(r'^ajax_sessions_request$', views.GetAjaxSessions, name='ajaxsessions'),
	url(r'^ajax_config_request$', views.GetConfig, name='ajaxconfig'),
)
