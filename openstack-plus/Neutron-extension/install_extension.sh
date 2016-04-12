#!/bin/bash

# copy file from workspace to neutron
# you must run this script as su

neutron_path="/usr/lib/python2.7/dist-packages"

clear
service neutron-server stop

echo 'start to apply changes'

cp ./exceptions.py $neutron_path/neutron/common/exceptions.py
cp ./quota.py $neutron_path/neutron/quota.py

cp ./flowrule.py $neutron_path/neutron/extensions/flowrule.py

cp ./managers.py $neutron_path/neutron/plugins/ml2/managers.py
cp ./driver_context.py $neutron_path/neutron/plugins/ml2/driver_context.py
cp ./plugin.py $neutron_path/neutron/plugins/ml2/plugin.py

cp ./driver_api.py $neutron_path/neutron/plugins/ml2/driver_api.py
cp ./mechanism_odl.py $neutron_path/neutron/plugins/ml2/drivers/mechanism_odl.py

cp ./attributes.py $neutron_path/neutron/api/v2/attributes.py

cp ./models_v2.py $neutron_path/neutron/db/models_v2.py
cp ./db_base_plugin_v2.py $neutron_path/neutron/db/db_base_plugin_v2.py

cp -r ./networkx $neutron_path/

cp /var/log/neutron/server.log /var/log/neutron/server.log_bak
echo '' > /var/log/neutron/server.log

echo 'changes applied, now restarting'

service neutron-server start
#echo 'waiting for errors (5 seconds)....'
sleep 5

echo "errors"
cat /var/log/neutron/server.log | grep ERROR | wc -l
echo "criticals"
cat /var/log/neutron/server.log | grep CRITICAL |wc -l
