from constants import *
import urllib2
import json
import hashlib, six, requests

def keystone_auth(username, password, tenant='admin'):
	tenant = username
	# Compile auth json
	datajs = '{\"auth\": {\"tenantName\": \"'+tenant+'\",\"passwordCredentials\": {\"username\": \"'+username+'\",\"password\": \"'+password+'\"}}}'
	
	# Perform request to keystone
	request = urllib2.Request(URL_AUTH_V2, datajs)
	request.add_header("Content-Type",'application/json')
	response = urllib2.urlopen(request, None, 5)
	
	# Save token in session
	js_response = json.load(response)
	
	# Manage response (on error urllib2 raise exception)
	return js_response["access"]["token"]["id"], js_response["access"]["user"]["id"]

