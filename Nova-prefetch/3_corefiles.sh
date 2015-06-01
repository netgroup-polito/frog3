#!/bin/bash
# Author: Alberto Geniola

service_install_path="/var/lib/nova_precache"
service_conf_path="/etc/nova_precache/compute_service"

# Print info to the user
echo "**************************************************"
echo "This script takes care of file copy for the services we want to install."
echo "This software is provided as is, without any warranty."
echo "Alberto Geniola - April 2015"
echo "**************************************************"
echo ""
read -p "Do you want to continue? (y/n)" -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
	exit 0
fi

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo ""
echo "We will now install script files."

# Create a directory if doesn't exist
if [[ ! -d "$service_install_path" ]]
then
	mkdir "$service_install_path"
	if [[ $? -ne 0 ]]
	then
		echo "Cannot create the destination directory."
		exit 1
	fi
fi

# Perform the copy
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cp -vR $DIR/server_files/* "$service_install_path"
if [[ $? -ne 0 ]]
then
	echo "Cannot copy script files into $service_install_path. Check your input and permissions, then try again."
	exit 1
fi

# It's now time to setup the conf file
echo ""
echo "We will now install configuration file."

# Create directory if doesn't exist
if [[ ! -d "$service_conf_path" ]]
then
	mkdir -p "$service_conf_path"
	if [[ $? -ne 0 ]]
	then
		echo "Cannot create the destination directory."
		exit 1
	fi
fi

# Perform the copy
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cp -vR $DIR/server_conf_files/* "$service_conf_path"
if [[ $? -ne 0 ]]
then
	echo "Cannot copy configuration files into $service_conf_path. Check your input and permissions, then try again."
	exit 1
fi
echo -e -n "\033[01;32m"
echo "File installation completed."
echo -e -n "\033[1;36m"
echo "IMPORTANT! Please update the conf file in $service_conf_path/caching.conf"
echo ""
echo -e -n "\033[1;36m"
echo "IMPORTANT! Remember to set \"remove_unused_base_images = False\" in nova.conf. This is a MUST to before starting the precaching service."
echo -e -n '\033[0m'
echo ""