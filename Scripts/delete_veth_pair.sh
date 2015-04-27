ip link del $3 type veth peer name $4
ovs-vsctl del-port $1 $3
ovs-vsctl del-port $2 $4
