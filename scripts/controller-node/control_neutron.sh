#!/bin/bash

echo
echo "Controlling Neutron service"

rm -f /var/log/neutron/server.log.*

echo ''> /var/log/neutron/server.log

service neutron-server $1

sleep 3

echo "errors"
cat /var/log/neutron/server.log | grep ERROR | wc -l
echo "criticals"
cat /var/log/neutron/server.log | grep CRITICAL | wc -l
