import urllib2
import json
import requests
import os.path


from utils import get_filename, handle_uploaded_file
from auth import keystone_auth
from constants import URL_IMAGE, PATH_JSON, TIMEOUT
from service_graph import saveAndInstantiateServiceGraph

from django.http import HttpResponse, QueryDict
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
			checked_app = request.POST.getlist('psa_active')
		except MultiValueDictKeyError:
			checked_app = []
		
		# Load data
		with open(PATH_JSON + username + '.json', 'rb') as infile:
			data = json.load(infile)
		infile.close()
		
		# Update data
		for app in data["list"]:
			if app["psa_id"] in checked_app:
				app["checked"] = 1
			else:
				app["checked"] = 0
		
		# Save data
		with open(PATH_JSON + username + '.json', 'wb') as outfile:
			json.dump(data, outfile)
		outfile.close()
		
		# Crate service graph and instantiate it 
		saveAndInstantiateServiceGraph(request.session, data)
		
		request.session['save_status'] = 'success'
		return redirect('/app/')
		
	elif request.method == 'GET':
		
		# Get username from session
		username = request.session['username']
		
		# Check if file exist
		if os.path.exists(PATH_JSON + username + '.json') == False:
			# create empty json struct
			data = {}
			data['list'] = []
			data['user'] = username
			
			with open(PATH_JSON + username + '.json', 'wb') as outfile:
				json.dump(data, outfile)
			outfile.close()
			
		# Load data
		with open(PATH_JSON + username + '.json', 'rb') as infile:
			data = json.load(infile)
		infile.close()
		
		# Prepare user message
		if 'save_status' in request.session:
			response_message = request.session['save_status']
			del request.session['save_status']
		else:
			response_message = ''
			
		return render(request, 'app.html', { 'data': data["list"], 'response_message': response_message })
		

def store(request):

	if "username" not in request.session:
		return redirect("/login/")
	
	if request.method == 'POST':
		
		# Get username from session
		username = request.session['username']
		
		# Load data
		try:
			response = urllib2.urlopen(URL_IMAGE, None, TIMEOUT)
		except urllib2.URLError:
			return redirect('/login/?err_message=Connection Timeout')
			
		data = json.load(response)
		
		q_psa = QueryDict(request.POST['psa_ser'])
		psa_list = q_psa.getlist('psa-id[]')
		
		# Update data
		saved_list = []
		for app in data:
			if app["psa_id"] in psa_list:
				app["checked"] = 0
				saved_list.append(app)

		datajs = {}
		datajs['list'] = saved_list
		datajs['user'] = request.session['username']
				
		# Save on local file
		with open(PATH_JSON + username + '.json', 'wb') as outfile:
			json.dump(datajs, outfile)
			
		return HttpResponse('Success')
		
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
		
		# Eliminate app chosen from available list
		new_all_app = []
		for app in all_app:
			if app["psa_id"] not in id_user_app:
				new_all_app.append(app)
		
		# Prepare user message
		if 'upload_status' in request.session:
			response_message = request.session['upload_status']
			del request.session['upload_status']
		else:
			response_message = ''	
				
		return render(request, 'list.html', { 'all_app': new_all_app, 'user_app': user_app, 'username': username, 'response_message': response_message })
	

def login_view(request):
	
	if request.method == 'GET':
		try:
			err_msg = request.GET['err_message']
			return render(request, 'login.html', {'title': 'PSA Login', 'err_message': err_msg}, content_type="text/html")
		except KeyError:
			return render(request, 'login.html', {'title': 'PSA Login'}, content_type="text/html")
			
	
	elif request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		
		# Keystone authentication
		try:
			auth, user_id = keystone_auth(username=username, password=password)
		except urllib2.URLError:
			return redirect('/login/?err_message=Invalid Credentials')
		
		request.session['token'] = auth
		request.session['user_id'] = user_id
		request.session['username'] = username
		
		return redirect('/app/')
		
				
def logout_view(request):
	
	if "username" in request.session:
		del request.session['username']
		
	if "token" in request.session:
		del request.session['token']
		
	return redirect('/login/')
	

def user_image_upload(request):
	# Check authentication
	if "username" not in request.session:
		return redirect("/login/")

	try:
		appname = request.POST['user_img_name']
		fname = get_filename(request.FILES['user_img'].name)
	except MultiValueDictKeyError:
		request.session['upload_status'] = 'fail'
		return redirect('/store/')
		
	if appname == '':
		request.session['upload_status'] = 'fail'
		return redirect('/store/')
		
	# Handle file
	fpath = handle_uploaded_file(request.FILES['user_img'])
	
	# Send file to API
	try:
		r = requests.put(
			url = URL_IMAGE + fname + '/',
			params = {
				"id": fname,
				"name": appname,
				"status":"1",
				"manifest_id":"01",
				"storage_id":"01",
				"plugin_id":"01",
				"disk_format":"qcow2",
				"container_format":"bare",
			},
			files = {
				"image": open(fpath, 'rb')
			},
		)
		request.session['upload_status'] = 'success'
		
	except requests.exceptions.RequestException as e:
		request.session['upload_status'] = 'fail'
		redirect('/store/')
		
	return redirect('/store/')
	
		