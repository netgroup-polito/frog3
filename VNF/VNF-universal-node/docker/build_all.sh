#!/bin/bash

#Author: Ivano Cerrato
#Date: Jul. 29th, 2014

sudo docker run -d -p 6000:5000 samalba/docker-registry

sleep 1

echo "Example..."
cd example
sudo docker build --tag="localhost:6000/example" .
sudo docker push localhost:6000/example
cd ..

sleep 1

echo "Bridge..."
cd bridge
sudo docker build --tag="localhost:6000/bridge" .
sudo docker push localhost:6000/bridge
cd ..

sleep 1

echo "iptables..."
cd iptables
sudo docker build --tag="localhost:6000/iptables" .
sudo docker push localhost:6000/iptables
cd ..

sleep 1

echo "pkt_gen..."
cd pkt_gen
sudo docker build --tag="localhost:6000/mz" .
sudo docker push localhost:6000/mz
cd ..

sleep 1

echo "xDPd..."
cd xdpd
sudo docker build --tag="localhost:6000/xdpd_switch" .
sudo docker push localhost:6000/xdpd_switch
cd ..

sleep 1

cd graph_nodoby

echo "captive portal..."
cd captive_portal
sudo docker build --tag="localhost:6000/captive_portal" .
sudo docker push localhost:6000/captive_portal
cd ..

sleep 1

echo "DHCP server..."
cd dhcp_server
sudo docker build --tag="localhost:6000/dhcp_server" .
sudo docker push localhost:6000/dhcp_server
cd ..

sleep 1

echo "IP forger..."
cd ip_forger
sudo docker build --tag="localhost:6000/ip_forger" .
sudo docker push localhost:6000/ip_forger
cd ..

sleep 1

echo "OVS..."
cd ovs
sudo docker build --tag="localhost:6000/ovs_switch" .
sudo docker push localhost:6000/ovs_switch
cd ..

echo "ovs_control..."
cd ovs_control
sudo docker build --tag="localhost:6000/ovs_control" .
sudo docker push localhost:6000/ovs_control
cd ..

echo "DNS bind9..."
cd dns
sudo docker build --tag="localhost:6000/dns" .
sudo docker push localhost:6000/dns
cd ..

echo "End of nobody graph"

cd ..

echo "demo-nat"

cd demo-nat

echo "dh_nat..."
cd dh_nat
sudo docker build --tag="localhost:6000/dh_nat" .
sudo docker push localhost:6000/dh_nat
cd ..

echo "nat"
cd nat
sudo docker build --tag="localhost:6000/nat" .
sudo docker push localhost:6000/nat
cd ..

echo "ftp"
cd ftp
sudo docker build --tag="localhost:6000/ftp" .
sudo docker push localhost:6000/ftp
cd ..

echo "dh_2..."
cd dh_2
sudo docker build --tag="localhost:6000/dh_2" .
sudo docker push localhost:6000/dh_2
cd ..

echo "nat2"
cd nat2
sudo docker build --tag="localhost:6000/nat2" .
sudo docker push localhost:6000/nat2
cd ..

echo "ftp2"
cd ftp2
sudo docker build --tag="localhost:6000/ftp2" .
sudo docker push localhost:6000/ftp2
cd ..

echo "ntop80"
cd ntop80
sudo docker build --tag="localhost:6000/ntop80" .
sudo docker push localhost:6000/ntop80
cd ..

echo "ntopNo80"
cd ntopNo80
sudo docker build --tag="localhost:6000/ntopno80" .
sudo docker push localhost:6000/ntopno80
cd ..

