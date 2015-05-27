#! /bin/bash

#useful link: 
#	http://www.cyberciti.biz/faq/howto-debian-ubutnu-set-default-gateway-ipaddress/

ifconfig  eth2 192.168.4.5/24
route add default gw 192.168.4.1

cd rofl-core/build/examples/ethswctld$ 
./ethswctld  &

xdpd -c xdpd.conf &

echo "The switch and the controller are started"

while true
do
	sleep 1
done

