#The JOLNet control adapter

This is the technology-dependent controller in charge of implementing NF-FGs on the JOL Network (JOLNet) infrastructure. The JOLNet is a geographic ISP network based on the SDN paradigm (it is made of OpenFlow-capable switches) and has the capability to host virtual network functions (VNFs) directly into network devices, thanks to special servers managed by the cloud orchestrator OpenStack.

#Configuration

In order to user the global orchestrator with this infrastructure, you need to configure it in this way:

- Select the "JolnetCA" driver in the divers tab

- Set the URL of the OpenStack controller authentication endpoint and set the access credential for the orchestration user and the admin user (usually it is the same user):

```sh
[authentication]
server = http://jolnet-openstack-controller:35357

# An OpenStack (keystone) admin user is needed to create new users
orch_username = user1
orch_password = pass1
orch_tenant = tenant1

admin_user = user1
admin_password = pass1
admin_tenant_name = tenant1
```

- Set the URL of the OpenDaylight (OpenFlow controller) access endpoint:

```sh
[odl]
# OpenDayLight endpoint
endpoint = http://jolnet-odl-controller:8181
```

After that, you need also to manually insert every JOLNet node into the orchestrator database "node" table (if not already there):

```sh
| ID |  NAME   |    TYPE    |       DOMAIN_ID       |   AVAILABILITY_ZONE   |  CONTROLLER_NODE   |
   1    node1	  JolnetCA    openflow:xxxxxxxxxxx           Turin                 1.1.1.1
```

where the ID can be arbitrary assigned, the DOMAIN_ID is the OpenFlow id of the switch, AVAILABILITY_ZONE is the availability zone of the correspondent OpenStack compute node and CONTROLLER_NODE is the public IP address of the OpenStack controller.