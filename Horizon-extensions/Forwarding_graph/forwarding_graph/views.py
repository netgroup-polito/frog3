from horizon import tabs
from django.http import HttpResponse, Http404
import json

from openstack_dashboard.dashboards.admin.forwarding_graph \
    import tabs as mydashboard_tabs

from openstack_dashboard import api

import ConfigParser

import sys
sys.path.append("/usr/lib/python2.7/dist-packages")
import MySQLdb

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

		config = ConfigParser.ConfigParser()
		config.read('/etc/openstack-dashboard/conf.cfg')
		ip_addr = config.get('mysqldb', 'ip_addr')
		user = config.get('mysqldb', 'user')
		passw = config.get('mysqldb', 'passw')
		db_name = config.get('mysqldb', 'db_name')

		# Open database connection
		db = MySQLdb.connect(ip_addr ,user ,passw ,db_name)

		# prepare a cursor object using cursor() method
		cursor = db.cursor()

		# execute SQL query using execute() method.
		cursor.execute("SELECT profile FROM profile WHERE id='"+profile_id+"'")

		# Fetch a single row using fetchone() method.
		data = cursor.fetchone()

		# disconnect from server
		db.close()

		return HttpResponse(data)
	else: 
		raise Http404

def GetAjaxSessions(request):
	if request.is_ajax():
		config = ConfigParser.ConfigParser()
		config.read('/etc/openstack-dashboard/conf.cfg')
		ip_addr = config.get('mysqldb', 'ip_addr')
		user = config.get('mysqldb', 'user')
		passw = config.get('mysqldb', 'passw')
		db_name = config.get('mysqldb', 'db_name')

		# Open database connection
		db = MySQLdb.connect(ip_addr, user, passw, db_name)

		# prepare a cursor object using cursor() method
		cursor = db.cursor()

		# execute SQL query using execute() method.
		cursor.execute("SELECT user_id, profile FROM session WHERE error is NULL and ended is NULL")

		sessionsList = ""

		row = cursor.fetchone()
		while row is not None:
			userId = str(row[0])
			retVal = str(api.keystone.user_get(request, userId, admin=True))
			splittedVal = retVal.split("'")
			sessionsList = sessionsList+"('"+splittedVal[3]+"','"+row[1]+"','"+splittedVal[13]+"')"
			row = cursor.fetchone()
			print retVal

		print sessionsList
		db.close()
		return HttpResponse(sessionsList)

		# Fetch a single row using fetchone() method.
		#data = cursor.fetchall()

		# disconnect from server
		#db.close()

		#return HttpResponse(data)
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

