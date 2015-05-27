#! /bin/bash

#useful link:
#	http://www.cyberciti.biz/faq/howto-debian-ubutnu-set-default-gateway-ipaddress/

#Assign the ip address to the port usd by the dhcp server
cp /sbin/dhclient /usr/sbin/dhclient && /usr/sbin/dhclient eth1 -v 
ifconfig eth0 192.168.4.1/24


#start the SSH server
service ssh start
echo "ssh service started"

iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE

#Keep the container alive
while true
do
	sleep 100
done

