echo
echo "Creating database and setting privileges"
echo
echo 'drop database glance;' | mysql -u root --password=stack
echo 'create database glance;' | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack

echo
echo "Now updating tables in the database"
su -s /bin/sh -c "glance-manage db_sync" glance


echo
echo "Now restarting glance services"

./control_glance.sh restart
