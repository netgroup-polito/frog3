#!/bin/bash

#NETWORK_CONFIG_FILE='/etc/network/interfaces'

start(){
    ovs-vsctl add-br br-swt

#    ovs-vsctl set-controller br-swt tcp:192.168.4.4:8888
	for i in `ls /sys/class/net`
	do
		if [ $i != lo -a $i != 'ovs-system' -a $i != "eth0" ]
		then
		    ovs-vsctl add-port br-swt $i
		fi
	done

 ovs-vsctl show
}

case $1 in
    start)
        start
    ;;
    stop)
    ;;
    *)
        echo "Usage: $0 {start}"
        exit 2
    ;;
esac

