README 

WHAT DO YOU NEED

A folder in which all the template files for each VNF element are placed.
A folder containing the endpoint configuration files (i.e. one file for the user,one for internet etc.).
A folder in which/from which the service graph is saved/loaded.  
A configuration file in which these paths are saved (more details in the following section).
The service_graph installation zip, of course :)

INSTALLATION

Unzip the installation package.

There are two “service_graph “ folders, the first one containing all the “static” files (.js, .css, images), located into the “static” directory, and the other one containing all the python files (view, url, script, etc and the templates), located into the “project directory”. 
The first one is referred as “static folder ”, the second one as “project folder” in the following instructions.  

Perform the following steps:

1.	Copy the “static folder” into "/usr/share/openstack-dashboard/static/"
2.	Copy “project folder” into "/usr/share/openstack-dashboard/openstack_dashboard/dashboards/project/"
3.	Go into "/usr/share/openstack-dashboard/openstack_dashboard/dashboards/project"
4.	Modify the “dashboard.py” file by adding ‘service_graph’ among the panes of the OrchestrationPanels as follows into the example below:

			class OrchestrationPanels(horizon.PanelGroup):
				name = _("Orchestration")
				slug = "orchestration"
				panels = ('stacks',
					'service_graph',)
					
5.	Add all the images you need into "/usr/share/openstack-dashboard/static/service_graph". The images are used to customize the endpoint icons. See the section below for details. 
6.	IMPORTANT!!! Permission settings: the interface does not work in case the permission are not correctly set. Modify the permissions by means of the "chown" command to get the ownership of the folders ( “chmod” otherwise).
7.	Configuration file: create a configuration file to store the pathnames to the folders containing all the necessary files (templates, endpoint, save/load) as follows:

		PATH_TEMPLATE=”/Your_templates_path/”
		PATH_ENDPFOLDER=”/Your_endpoint_path/”
		PATH_SERVICEGRAPH=”/Your_servicegraphjson_path_tosaveload/”
		
8.	Open the "view.py" file located into "/usr/share/openstack-dashboard/openstack_dashboard/dashboards/project/service_graph/" and edit the path passed to the "ReadConfFile" function: it is the path where your config file is located (the one containing all the paths).

	I.e.	conf_list = readConfFile("/etc/openstack-dashboard/sg_conf.cfg");
9. All the template files in the code are supposed to be "*.txt". If you use a different extension, open the "read_dir_content.py" into "/usr/share/openstack-dashboard/openstack_dashboard/dashboards/project/service_graph/". 
	This is the script which looks for the templates and matches all the files corresponding to a regex (i.e. "*.txt" matches all the txt files).
	Modify the " for f in glob.glob(foldername + "*.txt"): " according to your file names.
	The same has to be done for the endpoint configuration files. Modify the script "read_endpoint_conf.py" in the same dir.
	
IMAGES and ICONS
The endpoint icon on the bottom-right of the endpoint symbol represents the endpoint type (internet, user for the moment). Both the endpoint type and the corresponding image must have the same name (i.e. internet type --> image name is "internet.*"), in order to have a direct match.

ENDPOINT FILENAMES
The endpoint file name contains the user type (i.e. enpointadminconf.txt ) to be able to have different endpoint conf file according to the user type (member, admin).
Be careful to specify the user type into the endpoint filename.( Otherwise, modify the script "read_endpoint_conf.py").