#!/bin/bash

# copy file from workspace to neutron
# you must run this script as su

neutron_path="/usr/lib/python2.7/dist-packages"
#neutron_path="/usr/local/lib/python2.7/dist-packages"
clear
service neutron-server stop

echo 'start to apply changes'

cp ./client.py $neutron_path/neutronclient/v2_0/client.py

echo 'changes applied, now restarting'
echo ''> /var/log/neutron/server.log
service neutron-server start
service neutron-l3-agent restart
service neutron-dhcp-agent restart
sleep 5
echo "errors"
cat /var/log/neutron/server.log | grep ERROR | wc -l
echo "criticals"
cat /var/log/neutron/server.log | grep CRITICAL | wc -l

