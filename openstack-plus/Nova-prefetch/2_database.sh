#!/bin/bash
# Author: Alberto Geniola

DEFAULT_DB_HOST="controller"
DEFAULT_DB_ROOT="root"
DEFAULT_DB_USER="cachemanager"
DEFAULT_DB_PASS="cacheT00R"
DEFAULT_DB_NAME="precache"

# Print info to the user
echo "**************************************************"
echo "This script will prepare the database in order to install the prefetching module."
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
echo "DB configuration."
echo "We will now collect info about the new db to be created. If you are unsure, just use defaults."
echo "Whatever you chose, please save this information. You'll need it to configure your compute-cache services."
echo ""

echo "Please specify the name of the new db to be created[$DEFAULT_DB_NAME]:"
read DB_NAME
if [[ $DB_NAME == "" ]]
then
    DB_NAME=$DEFAULT_DB_NAME
fi

echo "Please specify the user name to be created[$DEFAULT_DB_USER]:"
read DB_USER
if [[ $DB_USER == "" ]]
then
    DB_USER=$DEFAULT_DB_USER
fi

PASSMATCHING=0
while [[ $PASSMATCHING -ne 1 ]]
do
    echo "Please specify the user's password to be created[$DEFAULT_DB_PASS]:"
    read -s DB_PASS
    echo ""
    if [[ $DB_PASS == "" ]]
    then
        echo "Detected balnk password, using default one $DEFAULT_DB_PASS"
        DB_PASS=$DEFAULT_DB_PASS
    fi

    echo "Please confirm the password:"
    read -s DB_PASS_CONFIRM
    echo ""
    if [[ $DB_PASS != $DB_PASS_CONFIRM ]]
    then
        echo "Password doesn't match."
        PASSMATCHING=0
    else
        PASSMATCHING=1
    fi
done

echo "We'll now connect to your database and create the schema, user and tables needed to this software."
echo "To do so, you need administration rights to your database, such as the root account."
echo "In this way we will create the db($DB_NAME) and the user($DB_USER), who will be granted all privileges on that db."

echo "Please specify the DB hostname[$DEFAULT_DB_HOST]:"
read DB_HOSTNAME
if [[ $DB_HOSTNAME == "" ]]
then
    DB_HOSTNAME=$DEFAULT_DB_HOST
fi

echo "Please specify the DB admin user[$DEFAULT_DB_ROOT]:"
read DB_ROOT
if [[ $DB_ROOT == "" ]]
then
    DB_ROOT=$DEFAULT_DB_ROOT
fi

echo "Please specify the DB admin password:"
read -s DB_ROOT_PASS

echo "Trying db connection..."
RESULT=$(mysql --password="$DB_ROOT_PASS" --user="$DB_ROOT" --host="$DB_HOSTNAME" --execute="quit")
if [[ $RESULT -ne 0 ]]
then
    echo "Cannot access DB. Please run again this script and check your credentials."
    exit 1
else
    echo "DB Connection successful."
fi

mysql --password="$DB_ROOT_PASS" --user="$DB_ROOT" --host="$DB_HOSTNAME" --execute="CREATE DATABASE $DB_NAME;"
mysql --password="$DB_ROOT_PASS" --user="$DB_ROOT" --host="$DB_HOSTNAME" --execute="CREATE USER '$DB_USER'@'%' IDENTIFIED BY '$DB_PASS';"
mysql --password="$DB_ROOT_PASS" --user="$DB_ROOT" --host="$DB_HOSTNAME" --execute="GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%'; FLUSH PRIVILEGES;"
mysql --password="$DB_ROOT_PASS" --user="$DB_ROOT" --host="$DB_HOSTNAME" $DB_NAME < schema.sql

if [[ $? -eq 0 ]]
then
    echo "" > dbconf.txt
    echo "DB_HOST=$DB_HOSTNAME" >> dbconf.txt
    echo "DB_USER=$DB_USER" >> dbconf.txt
    echo "DB_PASS=$DB_PASS" >> dbconf.txt
    echo "DB_NAME=$DB_NAME" >> dbconf.txt
    echo -e -n "\033[01;32m"
    echo "Database creation successful. Login data has been saved on local file dbconf.txt. Please move this file in a safe location!"
    echo -e -n '\033[0m'
else
    echo "Error when executing query."
    exit 1
fi

#DROP USER $DB_USER
#DROP DATABASE $DB_NAME