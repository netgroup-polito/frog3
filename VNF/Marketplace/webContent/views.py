import urllib2
import json
import requests
import os.path
import logging

from utils import get_filename, handle_uploaded_file
from auth import keystone_auth
from constants import URL_IMAGE, PATH_JSON, TIMEOUT
from model import UploadForm
from service_graph import saveAndInstantiateServiceGraph
from exception import Unauthorized

from django.http import HttpResponse, QueryDict, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError


def app(request):

	if "username" not in request.session:
		return redirect("/login/")
	
	if request.method == 'POST':
		
		# Get username from session
		username = request.session['username']
	
		# Get data from user
		try:
			checked_app = QueryDict(request.POST['psa_active'])
			checked_app = checked_app.getlist('psa_active')
			ordered_app = QueryDict(request.POST['psa_ordered'])
			ordered_app = ordered_app.getlist('psa_ordered')
		except MultiValueDictKeyError:
			checked_app = []
		
		# Load data
		with open(PATH_JSON + username + '.json', 'rb') as infile:
			data = json.load(infile)
		infile.close()
		
		# Update checked app
		for app in data["list"]:
			if app["psa_id"] in checked_app:
				app["checked"] = 1
			else:
				app["checked"] = 0
		
		# Update ordered app
		i = 1
		for id_oapp in ordered_app:
			for uapp in data["list"]:
				if uapp["psa_id"] == id_oapp:
					uapp["order"] = i
					i += 1
					break
					
		# Save data
		with open(PATH_JSON + username + '.json', 'wb') as outfile:
			json.dump(data, outfile)
		outfile.close()

		# Create the service graph and instantiate it
		try:
			saveAndInstantiateServiceGraph(request.session, data)
		except Unauthorized as ex:
			logout(request)
			return HttpResponse(ex.get_mess(), status=401)
			
		return HttpResponse('Success', status=200)
		
		
	elif request.method == 'GET':
		
		# Get username from session
		username = request.session['username']
		
		# Check if file exist
		if os.path.exists(PATH_JSON + username + '.json') == False:
			# create empty json struct
			data = {}
			data['list'] = []
			data['user'] = username
			data['max-order'] = 1
			
			with open(PATH_JSON + username + '.json', 'wb') as outfile:
				json.dump(data, outfile)
			outfile.close()
			
		# Load data
		with open(PATH_JSON + username + '.json', 'rb') as infile:
			data = json.load(infile)
		infile.close()
		
		app_list = data["list"]
		
		# Bubble sort
		for i in range(1,len(app_list)):
			for j in range(len(app_list)-i):
				if app_list[j+1]['order'] < app_list[j]['order']:
					app_list[j+1],app_list[j]=app_list[j],app_list[j+1]

			
		return render(request, 'app.html', { 'title': 'MyApps', 'data': data["list"] })
		

def store(request):

	if "username" not in request.session:
		return redirect("/login/")
	
	if request.method == 'POST':
		
		# Get username from session
		username = request.session['username']
		
		# Load all app from API
		try:
			response = urllib2.urlopen(URL_IMAGE, None, TIMEOUT)
			all_app = json.load(response)
		except urllib2.URLError:
			return HttpResponse('Server timeout', status=504)
		
		# Load app previously bought by user
		with open(PATH_JSON + username + '.json', 'rb') as infile:
			prev_app = json.load(infile)
		infile.close()
			
		# Load app currently bought by user
		q_psa = QueryDict(request.POST['psa_ser'])
		cur_app = q_psa.getlist('psa-id[]')
		
		# Get id of user previous app
		id_prev_app = []
		for app in prev_app['list']:
			id_prev_app.append(app['psa_id'])
			
		# Get max cod order
		cod_order = prev_app['max-order']
		
		# Update data
		saved_list = []
		for app in all_app:
			if app["psa_id"] in cur_app:
				if app["psa_id"] not in id_prev_app:
					app["checked"] = 0
					app["order"] = cod_order
					cod_order += 1
				else:
					for app_p in prev_app['list']:
						if app_p['psa_id'] == app["psa_id"]:
							app["checked"] = app_p["checked"]
							app["order"] = app_p["order"]
				saved_list.append(app)

		datajs = {}
		datajs['list'] = saved_list
		datajs['max-order'] = cod_order
		datajs['user'] = request.session['username']
				
		# Save on local file
		with open(PATH_JSON + username + '.json', 'wb') as outfile:
			json.dump(datajs, outfile)
		outfile.close()
			
		return HttpResponse('Success', status=200)
		
	elif request.method == 'GET':
		
		# Get username from session
		username = request.session['username']
		
		# Load all available app from server
		try:
			response = urllib2.urlopen(URL_IMAGE, None, TIMEOUT)
			all_app = json.load(response)
		except urllib2.URLError:
			return redirect('/login/?err_message=Connection Timeout')
			
		# Load user app from local file
		with open(PATH_JSON + username + '.json', 'rb') as infile:
			user_app = json.load(infile)["list"]
		infile.close()
		
		# Get id of user app
		id_user_app = []
		for app in user_app:
			id_user_app.append(app["psa_id"])
		
		# Delete app chosen from available list
		new_all_app = []
		for app in all_app:
			app["price"] = 0.99
			if app["psa_id"] not in id_user_app:
				new_all_app.append(app)
		
		# Prepare user message
		if 'upload_status' in request.session:
			response_message = request.session['upload_status']
			del request.session['upload_status']
		else:
			response_message = ''	
				
		return render(request, 'store.html', { 'title': 'MyStore', 'all_app': new_all_app, 'user_app': user_app, 'response_message': response_message })
	

def login_view(request):
	
	if request.method == 'GET':
	
		if "username" in request.session:
			return redirect("/app/")
			
		if request.GET.has_key('err_message'):
			err_msg = request.GET['err_message']
		else:
			err_msg = ''
		return render(request, 'login.html', {'title': 'Login', 'err_message': err_msg})
	
	elif request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		
		# Keystone authentication
		try:
			auth, user_id = keystone_auth(username=username, password=password)
		except Unauthorized:
			logging.error("Keystone returns 401 unauthorized")
			return redirect('/login/?err_message=Invalid Credentials')
		except:
			logging.error("Connection error")
			return redirect('/login/?err_message=Invalid Credentials')
		
		# Set session variables
		request.session['token'] = auth
		request.session['user_id'] = user_id
		request.session['username'] = username
		
		# Session expires when Web browser is closed
		request.session.set_expiry(0)
		
		return redirect('/app/')
		

def logout(request):
	request.session.flush()
			
def logout_view(request):
	logout(request)
	return redirect('/login/')
	

def user_image_upload(request):
	# Check authentication
	if "username" not in request.session:
		return redirect("/login/")
	
	if request.method == 'GET':
		form = UploadForm()
		return render(request, 'upload.html', { 'title': 'Upload', 'form': form })
	
	elif request.method == 'POST':
		form = UploadForm(request.POST, request.FILES)

		if not form.is_valid():
			return render(request, 'upload.html', { 'title': 'Upload', 'form': form, 'response_message': 'fail' })
		
		# Handle file
		fpath = handle_uploaded_file(request.FILES['file_image'])
		fname = get_filename(request.FILES['file_image'].name)
		
		# Send file to API
		params = {
				"id": fname,
				"name": form.cleaned_data['appname'],
				"status": form.cleaned_data['status'],
				"manifest_id": form.cleaned_data['manifest_id'],
				"storage_id": form.cleaned_data['storage_id'],
				"plugin_id": form.cleaned_data['plugin_id'],
				"disk_format": form.cleaned_data['disk_format'],
				"container_format": form.cleaned_data['container_format'],
				}
		files = {"image": open(fpath, 'rb')}
		
		try:
			putNewAppToAPI(fname, files, params)
			request.session['upload_status'] = 'success'
		except requests.exceptions.HTTPError:
			return render(request, 'upload.html', { 'title': 'Upload', 'form': form, 'response_message': 'fail' })
			
		# Delete file
		os.remove(fpath)
		
		return redirect('/store/')
	
def putNewAppToAPI(fname, files, params):
	url = URL_IMAGE + fname + '/'
	response = requests.put(url = url, params = params, files = files)
	response.raise_for_status()
	
def config(request):
	
	# Get username from session
	username = request.session['username']
	
	if request.method == 'POST':
		# Load user data
		with open(PATH_JSON + username + '.json', 'rb') as infile:
			data = json.load(infile)
		infile.close()
		
		# Update data with configuration test
		for app in data["list"]:
			if app['psa_id'] == request.POST['psa_id']:
				app['config'] = request.POST['config-data']
		
		# Save data
		with open(PATH_JSON + username + '.json', 'wb') as outfile:
			json.dump(data, outfile)
		outfile.close()
	
		return redirect('/app/')
		
	elif request.method == 'GET':
		# Load user data
		with open(PATH_JSON + username + '.json', 'rb') as infile:
			data = json.load(infile)
		infile.close()
		
		# Return configuration text to ajax GET
		for app in data["list"]:
			if app['psa_id'] == request.GET['psa_id']:
				if 'config' in app:
					return HttpResponse(app['config'], status=200)
				else:
					break
				
		return HttpResponse('', status=200)
		