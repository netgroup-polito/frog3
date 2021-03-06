#The JOLNet control adapter

This is the technology-dependent controller in charge of implementing NF-FGs on the JOL Network (JOLNet) infrastructure. The JOLNet is a geographic ISP network based on the SDN paradigm (it is made of OpenFlow-capable switches) and has the capability to host virtual network functions (VNFs) directly into network devices, thanks to special servers managed by the cloud orchestrator OpenStack.

#Configuration

In order to user the global orchestrator with this infrastructure, you need to configure it in this way:

- Add the "JolnetCA" driver in the divers tab

# Essential database information

After that, you need also to manually insert every JOLNet node into the orchestrator database "node" table (if not already there):

```sh
| ID |  NAME   |    TYPE    |       DOMAIN_ID        |   AVAILABILITY_ZONE   |  OPENSTACK_CONTROLLER  | OPENFLOW_CONTROLLER  |
  1     node1	  JolnetCA    openflow:xxxxxxxxxxx            Turin              		ABC          			XYZ 
```

where the ID can be arbitrary assigned, the DOMAIN_ID is the OpenFlow id of the switch, AVAILABILITY_ZONE is the availability zone of the correspondent OpenStack compute node, OPENSTACK_CONTROLLER is the id of the OpenStack controller and OPENFLOW_CONTROLLER is the foreign key which points to the "openflow_controller" table. 

The OpenStack controller is also inserted into this table and its domain id is the public address where the orchestrator will send REST requests (it does not need availability_zone and controllers fields):

```sh
| ID  |  NAME   |    TYPE    |   DOMAIN_ID    |   AVAILABILITY_ZONE   |  OPENSTACK_CONTROLLER  | OPENFLOW_CONTROLLER  |
  ABC    ctrl	   JolnetCA       1.1.1.1     
```

The OpenFlow controller is instead inserted in a dedicated table:

```sh
| ID  |       ENDPOINT         |    VERSION     |   USERNAME    |   PASSWORD   |
  XYZ    http://2.2.2.2:8181        LITHIUM          XYZ             ABC
```

Last but not least, you need to "register" into the "user" table to get access to the orchestrator functionalities:

```sh
| ID |  NAME  |  PASSWORD  |  TENANT  |      MAIL     |
  1     AAAA      BBBBB        CCCC      AAA@BBB.COM
```

where the TENANT field is a foreign key to the "tenant" table:

```sh
|  ID  |   NAME   |   DESCRIPTION    |
  CCCC    Tenant1      My tenant 
```