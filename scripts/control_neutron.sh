#!/bin/bash

echo
echo "Controlling Neutron service"

rm -f /var/log/neutron/server.log.*
rm -f /var/log/neutron/l3-agent.log.*
rm -f /var/log/neutron/dhcp-agent.log.*
rm -f /var/log/neutron/openvswitch-agent.log.*
rm -f /var/log/neutron/neutron-ns-metadata-proxy*

echo ''> /var/log/neutron/server.log

service neutron-server $1

sleep 5

echo "errors"
cat /var/log/neutron/server.log | grep ERROR | wc -l
echo "criticals"
cat /var/log/neutron/server.log | grep CRITICAL | wc -l
