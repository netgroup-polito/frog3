#!/bin/bash

echo
echo "Controlling Heat service"

echo ''>/var/log/heat/heat-engine.log
echo ''>/var/log/heat/heat-api.log

service heat-api $1
service heat-api-cfn $1
service heat-engine $1

