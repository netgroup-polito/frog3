Welcome to the nova precache prototype!

..................................
Quick installation tips:
..................................
In order to install the software, simply run all the .sh script within this directory, following the right right sequence:
- 1_dependencies     (on each Compute node and Controller)
- 2_database*        (on Controller, once)
- 3_corefiles        (on each Compute node)
- 4_service          (on each Compute node)
- 5_horizon plugin** (on Controller, once)

* Please be aware that the database step has to be performed once. It will allocate the db, create an user and grant to that use all needed privileges for the new db.
We strongly encourage to install the DB on the controller node to simply your infrastructure complexity, but this is not mandatory (for instance, you may want to install
the db on a particular compute node).

** The Horizon plugin installation has to be performed only on the controller node (where horizon is installed).

..................................
Installation notes
..................................
This software is based on a very simple distributed architecture. There are N compute nodes, each one has an hypervisor running on a single openstack infrastructure.
You will need to install this service on each compute-node in order to enable that node to the prefetching operations. Every service is independent from the others and
the main synchronization is provided by the central database, which is often installed on the controller node.

 ____________
|  [HOST 1]  |
|Nova compute|
|____________|
             \
              \   ______________
 ____________  \ | [Controller] |
|  [HOST 2]  |   |    Horizon   |
|Nova compute|-- |    Database  |
|____________|   |______________|
                 /
 ____________   /
|  [HOST 3]  | /
|Nova compute|
|____________|  
              

It's also common to have an hypervisor directly installed on the controller node. In that case you'll need to install the service also on the controller. If you don't have any
compute node installed on the controller, you only need to install the database and the horizon plugin.


..................................
Default paths
..................................
DEFAULT_INSTALL_PATH="/var/lib/nova_precache"
service_conf_path="/etc/nova_precache/compute_service"
DEFAULT_SERVICE_PATH="/etc/init.d/nova_precache"
DEFAULT_HORIZON_PATH="/usr/share/openstack-dashboard/openstack_dashboard"

..................................
Default DB confs
..................................
DEFAULT_DB_HOST="controller"
DEFAULT_DB_USER="cachemanager"
DEFAULT_DB_PASS="cacheT00R"
DEFAULT_DB_NAME="precache"

..................................
Uninstallation steps
..................................
1) From controller, remove the DB and the user
mysql -u root -p
drop database precache;
drop user cachemanager;

2) From controller, delete the horizon plugin
rm -R /usr/share/openstack-dashboard/openstack_dashboard/prefetching_panel
rm /usr/share/openstack-dashboard/openstack_dashboard/enabled/50_admin_prefetching.py

3) From every compute node, disable the service and remove the files
update-rc.d nova_precache remove
rm -R /var/lib/nova_precache
rm /etc/init.d/nova_precache

Done!

..................................
Info & contacts
..................................
Alberto Geniola, albertogeniola@gmail.com