#!/bin/bash
# Author: Alberto Geniola

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
DEFAULT_HORIZON_PATH="/usr/share/openstack-dashboard/openstack_dashboard"
SOURCE_PATH="$DIR/horizon_plugin"


# Print info to the user
echo "**************************************************"
echo "This script will install the Horizon plugin for nova precache."
echo "This software is provided as is, without any warranty."
echo "Alberto Geniola - May 2015"
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

# Check horizon is installed
if [[ -d $DEFAULT_HORIZON_PATH ]]
then
    echo "I've found a valid horizon path: $DEFAULT_HORIZON_PATH."
    read -p "Is it correct (y/n)?: " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        HORIZON_PATH=$DEFAULT_HORIZON_PATH
    else
        read -p "Type the horizon installation path: " HORIZON_PATH
        if [[ ! -d $HORIZON_PATH ]]
        then
            echo "Invalid path: $HORIZON_PATH. It's not a directory. Aborting."
            exit 1
        fi
    fi
fi

# Time to perform file copy
cp -vR $SOURCE_PATH/* $HORIZON_PATH
if [[ $? -ne 0 ]]
then
    echo "Error occurred during file copy. Check the destination directory ($HORIZON_PATH) exists and you've write permission on that folder."
    exit 1
fi

if [[ -f "$HORIZON_PATH/enabled/_50_admin_add_panel.py" ]]
then
    rm "$HORIZON_PATH/enabled/_50_admin_add_panel.py"
fi

if [[ -f "$HORIZON_PATH/enabled/_50_admin_add_panel.pyc" ]]
then
    rm "$HORIZON_PATH/enabled/_50_admin_add_panel.pyc"
fi

echo ""
echo -e -n "\033[01;32m"
echo "Plugin installed successfully."
echo -e -n "\033[1;36m"
echo "IMPORTANT! Please update the configuration file in $HORIZON_PATH/prefetching_panel/caching.conf to match your configuration."
echo ""
echo "IMPORTANT! When done, remember to restart APACHE service."
echo ""
echo -e -n '\033[0m'
echo "Have fun!"
echo ""