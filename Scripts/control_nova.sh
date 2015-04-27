#!/bin/bash

echo
echo "Controlling Nova service"

rm -rf /var/log/nova/nova-api.log.*
echo ''>/var/log/nova/nova-api.log
service nova-api $1
sleep 1
cat /var/log/nova/nova-api.log | grep ERROR | wc -l

rm -rf /var/log/nova/nova-cert.log.*
echo ''>/var/log/nova/nova-cert.log
service nova-cert $1
sleep 1
cat /var/log/nova/nova-cert.log | grep ERROR | wc -l

rm -rf /var/log/nova/nova-consoleauth.log.*
echo ''>/var/log/nova/nova-consoleauth.log
service nova-consoleauth $1
sleep 1
cat /var/log/nova/nova-consoleauth.log | grep ERROR | wc -l

rm -rf /var/log/nova/nova-scheduler.log.*
echo ''>/var/log/nova/nova-scheduler.log
service nova-scheduler $1
sleep 1
cat /var/log/nova/nova-scheduler.log | grep ERROR | wc -l

rm -rf /var/log/nova/nova-compute.log.*
echo ''>/var/log/nova/nova-compute.log
service nova-compute $1
sleep 1
cat /var/log/nova/nova-compute.log | grep ERROR | wc -l

rm -rf /var/log/nova/nova-conductor.log.*
echo ''>/var/log/nova/nova-conductor.log
service nova-conductor $1
sleep 1
cat /var/log/nova/nova-conductor.log | grep ERROR | wc -l


service nova-novncproxy $1

echo ''>/var/log/nova/nova-manage.log
rm -rf /var/log/nova/nova-manage.log.*

