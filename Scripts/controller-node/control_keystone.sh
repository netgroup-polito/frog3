#!/bin/bash

echo
echo "Controlling Keystone service"

echo "" > /var/log/keystone/keystone-all.log
service keystone $1
