#! /bin/bash

ifconfig  eth0 192.168.4.10/24
route add default gw 192.168.4.1

service ssh start

echo "ssh service started"

while true
do
	sleep 1
done

