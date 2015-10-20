echo
echo "Creating database and setting privileges"
echo
echo 'drop database keystone;' | mysql -u root --password=stack
echo 'create database keystone;' | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack

echo
echo "Now updating tables in the database"
su -s /bin/sh -c "keystone-manage db_sync" keystone


echo
echo "Now restarting keystone services"

./control_keystone.sh restart
