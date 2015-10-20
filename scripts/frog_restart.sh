if [ `whoami` != "root" ]; then
    echo Please execute this script as superuser or with sudo previleges.
    exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: frog_restart.sh <controller-ip>" >&2
  exit 1
fi


./del_manager.sh
./del_br.sh
./recreate_neutron_database.sh
./recreate_nova_database.sh
./control_neutron.sh stop
./set_manager.sh $1
sleep 2
./set_controller_out_of_band.sh
./create_bridge_usr.sh
ovs-vsctl del-controller br-usr
ovs-vsctl add-port br-usr eth1
./control_rabbit.sh restart
./control_neutron.sh restart 
./control_nova.sh restart
