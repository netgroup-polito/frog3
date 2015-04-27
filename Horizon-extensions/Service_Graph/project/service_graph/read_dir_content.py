#!/usr/bin/env python
#Script to print out the list of all the VNF names and the file names in which they're contained, given a directory as parameter --> output format = json

import glob, sys, os, json

#foldername = sys.argv[1]
def getVnfList( foldername ):
	
	#glob finds all the pathnames matching a specified pattern --> doesn't match only the #files starting with "."
	#the extension of the file must be specified in order to be matched --> it does not automatically lists all the files contained into a directory, it matches all the files with the specified pattern --> in this case *.*, all files
	#modify the script to make it opening a specific folder containing just manifest file 
	response = []

	for f in glob.glob(foldername + "*.txt"): 	#modify *.txt according to the extension 
	 	
		json_file = f
		json_data = open(json_file)
		data = json.load(json_data)
	
		json_data.close()
		response.append({ 'name' : data['name'], 'uri' : data['uri'] })
	
	#return json.dumps(response)
	response.sort()
	
	#returns the list of dictionaries
	return response		


