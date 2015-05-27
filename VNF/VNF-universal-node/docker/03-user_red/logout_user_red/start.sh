#! /bin/bash

#Set the address of the logout server

#ifconfig  eth1 192.168.100.30/24 up
ifconfig  eth1 192.168.4.40/24 up

#eth0 is used for ssh. The ip address is associated dynamically
cp /sbin/dhclient /usr/sbin/dhclient && /usr/sbin/dhclient eth0 -v

#Start the captive portal
rm /var/www/html/index.html
service apache2 restart
echo "Logout webserver started"

#Start the ssh server
service ssh start
echo "ssh service started"

#Keep the container alive
while true
do
	sleep 100
done

