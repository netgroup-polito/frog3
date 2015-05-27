#! /bin/bash

brctl addbr br0
brctl addif br0 eth0
brctl addif br0 eth1
ifconfig br0 up

service ssh start

echo "ssh service started"

while true
do
	sleep 1
done

