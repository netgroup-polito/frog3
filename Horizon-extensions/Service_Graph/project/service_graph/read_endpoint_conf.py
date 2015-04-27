#!/usr/bin/env python

import glob, sys, os, json


def getEndpointList(endpoint_folder,is_admin):
	if (is_admin == True):
		role = "admin"
	else:
		role = "member"
	
	response = []
	
	for f in glob.glob(endpoint_folder + "*" + role + "*.txt"): #modify *.txt according to the extension 
		
		fp = open(f)
		for line in fp:
			response.append(line.strip())
	
	return sorted(response)
	


