#!/bin/bash
# Author: Alberto Geniola

# Print info to the user
echo "**************************************************"
echo "Nova Cache Manager Prototype - Dependencies checker-installer"
echo "This software is provided as is, without any warranty."
echo "Alberto Geniola - April 2015"
echo "**************************************************"

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo ""
echo "This software will check if the current system fulfil all dependencies needed by this softwate."
echo "Please make sure you've an active internet connection and APT-GET package installed and configured."
read -p "Do you want to continue? (y/n)" -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
	exit 0
fi

if [[ $(apt-get -h > /dev/null; echo $?) -ne 0 ]]
then
    echo "apt-get command was unsuccessful. Please be sure you've apitude installed."
    exit 1
fi

# Dependencies
echo "Installing dependencies linux dependencies. This may take a bit..."
apt-get -qq update
apt-get -qq -y install python2.7 python-mysqldb python-pip mysql-client sysv-rc-conf
if [[ $? -ne 0 ]]
then
    echo "Cannot install all dependencies. Exiting."
     exit 1
fi

echo "Installing python dependencies..."
pip install python-keystoneclient
pip install python-novaclient
pip install python-glanceclient

echo ""
echo -e -n "\033[01;32m"
echo "Dependencies installation is complete! "
echo -e -n '\033[0m'
echo "Goodbye!"