echo
echo "Creating database and setting privileges"
echo
echo 'drop database neutron;' | mysql -u root --password=stack
echo 'create database neutron;' | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack
echo "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%'  IDENTIFIED BY 'stack';" | mysql -u root --password=stack

echo
echo "Now restarting neutron services"
./control_neutron.sh restart

echo
echo "Remember to create initial networks (./create_initial_networks.sh)"
echo
#./create_initial_networks.sh
