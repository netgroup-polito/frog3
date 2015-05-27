#! /bin/bash


service ssh start

echo "ssh service started"

ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
        --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile --detach \


ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach

./configure_ovs.sh start

echo "OVS started"

while true
do
	sleep 1
done

