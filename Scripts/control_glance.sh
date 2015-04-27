#!/bin/bash

echo
echo "Controlling Glance service"

echo "" > /var/log/glance/api.log
echo "" > /var/log/glance/registry.log

service glance-registry $1
service glance-api $1

