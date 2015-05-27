#! /bin/bash

#Set the address of the captive portal

echo "192.168.1.113 keystone" >> /etc/hosts
echo "192.168.1.113 orchestrator" >> /etc/hosts

#ifconfig eth1 down
#ifconfig eth1 hw ether 00:80:48:BA:d1:30
ifconfig  eth1 192.168.4.3/24 up

#eth0 is used for ssh. The ip address is associated dynamically
cp /sbin/dhclient /usr/sbin/dhclient && /usr/sbin/dhclient eth0 -v

#start the takeMac service
cd /opt/TakeMac
#screen -d -m gunicorn -b 0.0.0.0:81 main:app -t 100

gunicorn -b 0.0.0.0:81 main:app -t 100 &

#Start the captive portal
service jetty start
echo "Captive portal started"

#Start the ssh server
service ssh start
echo "ssh service started"

#Keep the container alive
while true
do
	sleep 100
done

