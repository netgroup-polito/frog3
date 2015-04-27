if [ `whoami` != "root" ]; then
    echo Please execute this script as superuser or with sudo previleges.
    exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: frog_restart.sh <controller-ip>" >&2
  exit 1
fi


./set_manager.sh $1

sleep 2
./set_controller_out_of_band.sh
ovs-vsctl del-controller br-ex

./control_neutron.sh restart
