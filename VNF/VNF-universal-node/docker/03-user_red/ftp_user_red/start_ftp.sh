#! /bin/bash

#useful link:
#	http://www.cyberciti.biz/faq/howto-debian-ubutnu-set-default-gateway-ipaddress/

#Assign the ip address to the port usd by the dhcp server
#cp /sbin/dhclient /usr/sbin/dhclient && /usr/sbin/dhclient eth0 -v
#ifconfig eth0 192.168.100.3/24
ifconfig eth0 192.168.4.41/24

#start the SSH server
service ssh start
echo "ssh service started"

#Keep the container alive
while true
do
	sleep 100
done

