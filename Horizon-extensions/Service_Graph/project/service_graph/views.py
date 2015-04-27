from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from read_dir_content import getVnfList
import json, fnmatch, os
from django.http import HttpResponseRedirect
from django.http import Http404
from readConfFile import readConfFile
from read_endpoint_conf import getEndpointList
#from openstack_dashboard import api

#global variable to store the configuration parameter - e.g. conf_list["PATH_NAME"]=my_pathname or conf_list["PATH_NAME"]="my_pathname"
#readConfFile reads the configuration file containing e.g. path containing 
conf_list = readConfFile("/etc/openstack-dashboard/sg_conf.cfg");



def index(request):

	
	foldername = conf_list["PATH_TEMPLATE"]
	endpoint_folder = conf_list["PATH_ENDPFOLDER"]

	
	vnf_list = getVnfList(foldername)
	
	is_admin = request.user.is_superuser
	
	endpoint_list = getEndpointList(endpoint_folder, is_admin)
	#user = api.keystone.user_get(request, request.user.id)
	
	context = {"vnf_list" : vnf_list, "endpoint_list" : endpoint_list, "user_id" : request.user.id, "username" : request.user.username}
	return render(request, 'project/service_graph/index.html', context)

def GetVnfInformation(request):
	vnf_file = None 
	foldername = conf_list["PATH_TEMPLATE"]
	foldername = foldername.replace('"', '').strip()
	
	if request.is_ajax():
		try:
			vnf_name = request.POST['vnf_name']
		except: 
			return HttpResponse('Error') #incorrect post 
		
		#Search a file matching the vnf_name
		for f in os.listdir(foldername):
			
			if(fnmatch.fnmatch(f, '*'+ vnf_name +'*')):
				
				vnf_file = f
				break
		
		#If the vnf exist, the file is opened and the json data read 
		if(vnf_file is not None ):
			
			json_data = open(foldername+vnf_file)

			data=json.load(json_data)
			json_data.close()
			
			return HttpResponse(json.dumps(data))
		else: 
			return HttpResponse('Error')
	else: 
		raise Http404

		
def saveServiceGraph(request):
	
	saveSGPath = conf_list["PATH_SERVICEGRAPH"]
	
	
	if request.is_ajax():
		try:
			s = request.POST['servicegraph']
			u = request.POST['user_id']
		except: 
			return HttpResponse('Error') #if incorrect post 
		
		f=open(saveSGPath + u + "_sg.json","w+")
		if(f is not None):
			f.write(s)
			f.close()
			return HttpResponse("Ok")
		else: 
			return HttpResponse('Error')
	else: 
		raise Http404
		

def loadServiceGraph(request):
	
	loadSGPath = conf_list["PATH_SERVICEGRAPH"]
	
	if request.is_ajax():
		u = request.POST['user_id']
		filename = loadSGPath + u + "_sg.json"
		json_data = open(filename)
		if(json_data is not None):
			data=json.load(json_data)
			json_data.close()

			return HttpResponse(json.dumps(data))
		else: 
			return HttpResponse('Error')
	else: 
		raise Http404
