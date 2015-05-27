#! /bin/bash

#Set the address of the DNS server

ifconfig  eth1 192.168.200.25/24 up

#eth0 is used for ssh. The ip address is associated dynamically
cp /sbin/dhclient /usr/sbin/dhclient && /usr/sbin/dhclient eth0 -v

cp /usr/sbin/named /sbin/named && /sbin/named -u bind
echo "DNS started"

#Start the ssh server
service ssh start
echo "ssh service started"

#Keep the container alive
while true
do
	sleep 100
done

