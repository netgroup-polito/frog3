#!/bin/bash

# copy file from workspace to heat
# you must run this script as su

clear

mkdir /usr/lib/heat-extensions
cp FlowRoute.py /usr/lib/heat-extensions

echo '' > /var/log/heat/heat-api.log
echo '' > /var/log/heat/heat-api-cfn.log
echo '' > /var/log/heat/heat-engine.log  

echo 'changes applied, now restarting'

service heat-api restart
service heat-api-cfn restart
service heat-engine restart

#echo 'waiting for errors (5 seconds)....'
sleep 5

echo "errors"
cat /var/log/heat/heat-api.log | grep ERROR | wc -l
echo "criticals"
cat /var/log/heat/heat-api.log | grep CRITICAL |wc -l

echo "errors"
cat /var/log/heat/heat-api-cfn.log | grep ERROR | wc -l
echo "criticals"
cat /var/log/heat/heat-api-cfn.log | grep CRITICAL |wc -l

echo "errors"
cat /var/log/heat/heat-engine.log | grep ERROR | wc -l
echo "criticals"
cat /var/log/heat/heat-engine.log | grep CRITICAL |wc -l
