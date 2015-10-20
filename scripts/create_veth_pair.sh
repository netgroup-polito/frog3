ip link add $3 type veth peer name $4
ovs-vsctl add-port $1 $3
ovs-vsctl add-port $2 $4
ifconfig $3 up
ifconfig $4 up


