echo
echo "Creating database and setting privileges"
echo
echo 'drop database nova;' | mysql -u root --password=stack
echo 'create database nova;' | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack

echo
echo "Now updating tables in the database"
su -s /bin/sh -c "nova-manage db sync" nova

#nova-manage db sync

echo
echo "Now restarting nova services"

./control_nova.sh restart
