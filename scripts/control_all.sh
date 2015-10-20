echo
echo "Type './control_all.sh [start | stop |restart | status]'"
echo

./control_keystone.sh $1
./control_glance.sh $1
./control_nova.sh $1
./control_neutron.sh $1
./control_heat.sh $1
