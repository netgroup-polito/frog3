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
./create_bridge_usr.sh
ovs-vsctl del-controller br-usr
ovs-vsctl del-controller br-ex
ovs-vsctl add-port br-usr wlan0


rm -rf /var/log/nova/nova-compute.log.*
echo ''>/var/log/nova/nova-compute.log
service nova-compute restart
sleep 1
cat /var/log/nova/nova-compute.log | grep ERROR | wc -l
