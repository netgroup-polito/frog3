echo
echo "Now creating base networks (please check that the IP addresses are the ones you want)"

#source admin-openrc.sh
#neutron subnet-delete ext-subnet
#neutron net-delete ext-net


#neutron net-create ext-net --shared --router:external=True
neutron net-create ext-net --shared --router:external

#neutron subnet-create ext-net --name ext-subnet  --allocation-pool start=130.192.225.200,end=130.192.225.253 --disable-dhcp --gateway 130.192.225.254 130.192.225.128/25
neutron subnet-create ext-net --name ext-subnet  --allocation-pool start=192.168.1.100,end=192.168.1.200 --disable-dhcp --gateway 192.168.1.1 192.168.1.0/24 

