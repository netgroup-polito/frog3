#!/bin/bash
# Author: Alberto Geniola

DEFAULT_INSTALL_PATH="/var/lib/nova_precache"
DEFAULT_SERVICE_PATH="/etc/init.d/nova_precache"
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
DEFAULT_SERVICE_SOURCE_PATH=$DIR/nova_precache.sh

# Print info to the user
echo "**************************************************"
echo "This script takes care of service installation for compute nodes."
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

# Check server files installed
if [[ ! -d $DEFAULT_INSTALL_PATH ]]
then
    echo "Error occurred: it seems core files have not been installed yet ($DEFAULT_INSTALL_PATH not a directory). Can't proceed with installation. Please run 3_corefiles.sh first."
    exit 1
fi

# Execute service installation
cp $DEFAULT_SERVICE_SOURCE_PATH $DEFAULT_SERVICE_PATH
if [[ $? -ne 0 ]]
then
    echo "Error occurred: cannot copy $DEFAULT_SERVICE_SOURCE_PATH in $DEFAULT_SERVICE_PATH"
    exit 1
fi

chmod 775 $DEFAULT_SERVICE_PATH
if [[ $? -ne 0 ]]
then
    echo "Error occurred: cannot chmod $DEFAULT_SERVICE_PATH to 755."
    exit 1
fi

update-rc.d nova_precache defaults 97 03
if [[ $? -ne 0 ]]
then
    echo "Error occurred: update-rc failed."
    exit 1
fi

sysv-rc-conf nova_precache on
if [[ $? -ne 0 ]]
then
    echo "Error occurred: sysv-rc-conf failed."
    exit 1
fi

echo ""
echo -e -n "\033[01;32m"
echo "Service installation OK!"
echo "Service won't be started. When you are ready to start it, use \"service nova_precache start\"."
echo -e -n '\033[0m'