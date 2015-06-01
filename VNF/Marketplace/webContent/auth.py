from constants import URL_AUTH_V2
import requests
import json
from exception import Unauthorized

def keystone_auth(username, password, tenant='admin'):
	tenant = username
	# Compile auth json
	datajs = {"auth": {"tenantName": tenant,"passwordCredentials": {"username": username,"password": password}}}
	headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
	resp = requests.post(URL_AUTH_V2, data=json.dumps(datajs), headers=headers)
	if resp.status_code == 401:
		raise Unauthorized('Keystone returns 401 Unauthorized')
	resp.raise_for_status()
	js_response = json.loads(resp.text)
	
	# Manage response (on error urllib2 raise exception)
	return js_response["access"]["token"]["id"], js_response["access"]["user"]["id"]

