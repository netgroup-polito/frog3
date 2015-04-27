if [ `whoami` != "root" ]; then
    echo Please execute this script as superuser or with sudo previleges.
    exit 1
fi

if [ "$#" -ne 4 ]; then
  echo "Usage: create_patch_port.sh <bridge-1> <bridge-2> <port-1> <port-2>" >&2
  echo "       <bridge-1> and <bridge-2> are the switches that will be connected"
  echo "       <port-1> and <port-2> are the ports created in the previous switches" 
  exit 1
fi

ovs-vsctl -- add-port $1 $3 -- add-port $2 $4 -- set interface $3 type=patch  options:peer=$4 -- set interface $4 type=patch options:peer=$3

echo 'The patch ports between switches were created'

