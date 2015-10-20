cd /home/stack

rm -rf log

mkdir log

mkdir log/keystone
cp /var/log/keystone/keystone-all.log /home/stack/log/keystone/.

mkdir log/nova
cp /var/log/nova/nova-api.log /home/stack/log/nova/.
cp /var/log/nova/nova-cert.log /home/stack/log/nova/.
cp /var/log/nova/nova-compute.log /home/stack/log/nova/.
cp /var/log/nova/nova-conductor.log /home/stack/log/nova/.
cp /var/log/nova/nova-consoleauth.log /home/stack/log/nova/.
cp /var/log/nova/nova-manage.log /home/stack/log/nova/.
cp /var/log/nova/nova-scheduler.log /home/stack/log/nova/.

mkdir log/neutron
cp /var/log/neutron/server.log /home/stack/log/neutron/.

mkdir log/heat
cp /var/log/heat/heat-api-cfn.log /home/stack/log/heat/.
cp /var/log/heat/heat-api.log /home/stack/log/heat/.
cp /var/log/heat/heat-engine.log /home/stack/log/heat/.
cp /var/log/heat/heat-manage.log /home/stack/log/heat/.

zip -r logs logs/*

