echo
echo "Creating database and setting privileges"
echo
echo 'drop database heat;' | mysql -u root --password=stack
echo 'create database heat;' | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'localhost'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'%'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack

echo
echo "Now updating tables in the database"
#su -s /bin/sh -c "heat-manage db_sync" heat
heat-manage db_sync

echo
echo "Now restarting nova services"
./control_heat.sh restart


