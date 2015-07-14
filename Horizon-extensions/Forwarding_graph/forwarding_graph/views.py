from horizon import tabs
from django.http import HttpResponse, Http404
import json

from openstack_dashboard.dashboards.admin.forwarding_graph \
    import tabs as mydashboard_tabs
from openstack_dashboard.dashboards.admin.forwarding_graph.SQL.session import Session
from openstack_dashboard.dashboards.admin.forwarding_graph.SQL.graph import Graph

from openstack_dashboard import api

import ConfigParser

import sys
sys.path.append("/usr/lib/python2.7/dist-packages")

class IndexView(tabs.TabbedTableView):
    tab_group_class = mydashboard_tabs.MypanelTabs
    template_name = 'admin/forwarding_graph/index.html'

    def get_data(self, request, context, *args, **kwargs):
        return context

def GetAjaxData(request):
    if request.is_ajax():
    	try:
    		profile_id = request.POST['profile_id']
    	except: 
    		return HttpResponse('Error') #incorrect post 
    
        nffg = Graph().get_nffg_by_id(profile_id, encode=True)
    
    	return HttpResponse(nffg)
    else: 
    	raise Http404

def GetAjaxSessions(request):
    if request.is_ajax():
    	config = ConfigParser.ConfigParser()
    	
        sessions = Session().get_active_user_session()
        
    	sessionsList = ""
    
        for session in sessions:
            userId = session.user_id
            retVal = str(api.keystone.user_get(request, userId, admin=True))
            splittedVal = retVal.split("'")
            sessionsList = sessionsList+"('"+splittedVal[3]+"','"+session.service_graph_id+"','"+splittedVal[13]+"')"
            print retVal
    
    	print sessionsList
    	return HttpResponse(sessionsList)
    
    else: 
    	raise Http404

def GetConfig(request):
    if request.is_ajax():
    	config = ConfigParser.ConfigParser()
    	config.read('/etc/openstack-dashboard/conf.cfg')
    	configParameters = ""
    	configParameters = configParameters+config.get('myjsconfig', 'ingressName')
    	configParameters = configParameters+","
    	configParameters = configParameters+config.get('myjsconfig', 'egressName')
    	configParameters = configParameters+","
    	configParameters = configParameters+config.get('myjsconfig', 'controlIngressName')
    	configParameters = configParameters+","
    	configParameters = configParameters+config.get('myjsconfig', 'controlEgressName')
    	configParameters = configParameters+","
    	configParameters = configParameters+config.get('myjsconfig', 'ingressImg')
    	configParameters = configParameters+","
    	configParameters = configParameters+config.get('myjsconfig', 'egressImg')
    	configParameters = configParameters+","
    	configParameters = configParameters+config.get('myjsconfig', 'controlIngressImg')
    	configParameters = configParameters+","
    	configParameters = configParameters+config.get('myjsconfig', 'controlEgressImg')
    
    	print configParameters
    
    	return HttpResponse(configParameters)
    else: 
    	raise Http404

