if [ `whoami` != "root" ]; then
    echo Please execute this script as superuser or with sudo previleges.
    exit 1
fi

if [ "$#" -ne 4 ]; then
  echo "Usage: delete_patch_port.sh <bridge-1> <bridge-2> <port-1> <port-2>" >&2
  echo "       <bridge-1> and <bridge-2> are the switches that will be disconnected"
  echo "       <port-1> and <port-2> are the ports deleted in the previous switches" 
  exit 1
fi

ovs-vsctl del-port $1 $3
ovs-vsctl del-port $2 $4

echo 'The patch ports between switches were deleted'
