#! /bin/bash

#Add the ip address used by the IP forger
ifconfig eth1 192.168.4.4/24

#eth0 is used for ssh.
ifconfig eth0 192.168.1.25/24

#start the ssh server
service ssh start
echo "ssh service started"

cd /controller
./client_mac.sh

#start the IP forger
cd /controller
./pox.py IP_forger &

#Keep the container alive
while true
do
        sleep 100
done

