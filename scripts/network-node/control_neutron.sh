#!/bin/bash

echo
echo "Controlling Neutron service"

rm -f /var/log/neutron/server.log.*
rm -f /var/log/neutron/l3-agent.log.*
rm -f /var/log/neutron/dhcp-agent.log.*
rm -f /var/log/neutron/openvswitch-agent.log.*
rm -f /var/log/neutron/neutron-ns-metadata-proxy*

echo "" > /var/log/neutron/l3-agent.log
echo "" > /var/log/neutron/neutron-ns-metadata-proxy
echo "" > /var/log/neutron/dhcp-agent.log
echo "" > /var/log/neutron/openvswitch-agent.log

service neutron-l3-agent $1
service neutron-dhcp-agent $1
service neutron-metadata-agent $1
