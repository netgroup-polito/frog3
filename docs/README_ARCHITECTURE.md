# FROG3 Architecture
An overall view of the architecture of FROG is provided in the image below. As evident from the picture, FROG consists of three main components. Briefly, the Service Layer Application allows different actors to define the service they require from the network, as well as it starts the deployment of a service as soon as an end user is connected; this part is use case-specific, and must be changed in order to implement other use cases. The global orchestrator, instead, receives a Network Function – Forwarding Graph (NF-FG) from the service layer, executes some manipulations on it, and transforms it into the proper syntax, according to the infrastructure layer on which the service is going to be instantiated. In fact, the global orchestrator can work with different implementations of the infrastructure layer.

![architecture](https://raw.githubusercontent.com/netgroup-polito/frog3/master/images/architecture.jpg)

## Service layer
The service layer defined in the Unify architecture represents the external interface of the system, and allows the definition of a service through a formalism called Service Graph (SG).

In FROG, the service layer includes the Service Layer Application (the SLApp in the image above), which implements the logic of our specific use case; other use cases can be implemented by changing the SLApp logic. Our implementation of the SLApp delegates specific services to different OpenStack modules, some of which have been properly extended. In particular, Horizon, the OpenStack dashboard, is now able to provide to the users a graphical interface allowing them to express (out of band), the service they expect from the network, using the building blocks depicted in the image below.  Keystone, the token-based authentication mechanism for users and permissions management, is now able to store the user profile, which contains user’s specific information such as the description of his own SG.

![service-graph](https://raw.githubusercontent.com/netgroup-polito/frog3/master/images/service-graph.jpg)

The infrastructure layer does not implement any logic by itself, and hence each operation must be defined with the deployment of the proper VNFs. This makes the FROG architecture extremely flexible, since it is able to implement any type of service and use case defined in the service layer.

In each compute nodes should be instantiated an authentication graph, that contains a set of VNFs that allows a new user connected to the network to authenticate himself, in order to trigger the instantiation of his own service. A successful user authentication triggers the instantiation of the SG associated with that end user. In particular, the SLApp retrieves the proper SG description from the user profile repository (keystone), and starts the process aiming at converting the resulting SG into a NF-FG. More in detail, the SLApp executes the following transformations on the SG:

- control and management network expansion: the service is enriched with the “control and management network”, which may be used to properly configure the VNFs of the graph (e.g., to set up the proper policies in a firewall);
- LAN expansion: the LANs expressed in the SG are replaced with VNFs implementing the MAC learning switch. This step is needed to translate the abstract LAN element into a VNF actually realizing the broadcast communication medium;
- service enrichment: the SG is analysed and enriched with those VNFs that have not been inserted in the SG, but that are required for the correct implementation and delivery of the service (e.g., a DHCP server to provide to the user’s client the proper network configuration). 
The result of these steps is a NF-FG that can be sent to the next level of the architecture, namely the orchestration layer.

## Orchestration layer – The global orchestrator
The orchestration layer sits below the service layer and it is responsible of two important phases in the deployment of a service on the physical infrastructure. First, it further manipulates the NF-FG in order to allow its deployment; as detailed in the following, these transformations include the enriching of the initial definition with extra details such as new VNFs, as well as the consolidation of several VNFs into a single one . Second, the orchestration layer implements the scheduler that is in charge of deciding where to instantiate the requested service (although this feature is not yet available in the current implementation of FROG).

The Unify architecture splits this layer in three logical sub-layers. In FROG, the global orchestrator module implements the first two sub-layers, and consists of a technology-dependent and a technology independent part. The technology independent part receives the NF-FG from the service layer through its northbound interface, and executes the following manipulations on the graph:

- VNFs expansion: for each VNF specified in the NF-FG, it retrieves the corresponding VNF template. In fact, each VNF is associated with a template (described later on in the document),  which describes the VNF itself. It contains some information related to the hardware required by the VNF, describes the ports of the VNF, etc. Moreover, the template could say that a VNF is actually a sub-graph composed of other VNFs; for example, a Firewall could be implemented as a sub-graph composed of an URL filter only operating on the web traffic, while the non-web traffic is delivered to a stateless firewall. Even, these new VNFs are in turn associated with a template, and can be recursively expanded in further sub-graphs. The global orchestrator replaces, in the NF-FG, the original VNF with the sub-graph described in the template;
- VNFs consolidation: those VNFs implementing the L2 forwarding and that are connected together in the NF-FG, are replaced with a single VNF, in order to limit the resources required to implement the LANs on the physical infrastructure;

At this point, the resulting NF-FG is provided to the proper control adapter, according to the type of infrastructure layer on which the graph is going to be deployed.  In fact, the global orchestrator supports many implementation of the infrastructure layer, although in this document we focus on the OpenStack-based implementation detailed in the next section.

The control adapter is the module of the global orchestrator that takes care of translating the NF-FG into the formalism accepted by the proper infrastructure controller, which is then in charge of sending the commands to the infrastructure layer. 

As a final remark, the global orchestrator supports the update of existing services (i.e., add/remove VNFs, add/remove connections). In fact, when it receives a NF-FG from the SLApp, it checks if that graph has already been deployed; in this case, both the deployed NF-FG and the new one are provided to the proper infrastructure controller, which will calculate the difference and will trigger the proper commands in order to implement the update.

## Infrastructure layer – The OpenStack-based node
The infrastructure layer sits below the orchestration layer and includes the physical resources where the required service is actually deployed. From the point of view of the global orchestrator, it is organized in nodes, each one with its own infrastructure controller. 

In our implementation, each node of the infrastructure layer is an OpenStack domain called OpenStack-based node; in other words, each node actually consists of a cluster of servers managed through the same OpenStack instance. As shown in the image below, all the physical machines of the cluster are managed by a single Infrastructure controller, which is composed of a number of OpenStack modules and a SDN controller.

![infrastructure-layer](https://raw.githubusercontent.com/netgroup-polito/frog3/master/images/openstack-plus)

OpenStack is a widespread cloud toolkit used for managing cloud resources (network, storage, compute) in data-centers; hence, its support in our architecture represents an interesting choice because of the possibility to deploy our services in an existing (and widely deployed) environment. However, since OpenStack was designed to support the deployment of cloud services, several modifications have been made to support the NF-FG (hence network services) as well.

As depicted in the image abobe, our OpenStack-based node exploits the following OpenStack components: (i) Nova, the compute service; (ii) Neutron, the network service; (iii) Heat, the orchestration layer, and (iv) Glance, the Virtual Machines (VMs) repository. OpenStack is able to start VMs by interacting with different hypervisors (e.g., KVM, Xen, VMware); moreover, in order to properly steer the traffic among the several servers under its control, our prototype integrates also the OpenDaylight (ODL) SDN controller. As evident from the picture, Heat, Nova scheduler, Nova API, Neutron and ODL compose the infrastructure controller, while each physical machine executing the VNFs is a Nova compute node, which runs a Nova compute agent, the OpenvSwitch (OVS) softswitch and the KVM hypervisor. Note that the OpenStack-based node also supports VNFs in Docker containers although, due to a limitation of OpenStack, a compute node  just supports a virtualization environment at a time; therefore, a VNF implemented as a KVM VM and a VNF implemented as a Docker container cannot be executed on the same server. 

 

When the NF-FG must be implemented in an OpenStack-based node, the proper control adapter in the global orchestrator translates the NF-FG description into a format supported by Heat. To be used in our prototype, Heat has been extended to support the flow-rule primitive, which describes how to steer the traffic between the ports of the VNFs composing the graph. This primitive provides an interface similar to the OpenFlow flowmod message; however, it allows traffic steering between virtual ports without knowing in advance the physical server on which the VNFs will be scheduled. 

When Heat receives the NF-FG, the graph description is decomposed into a set of calls to Nova and Neutron. Particular, Nova receives a sequence of commands for each VNF of the graph in order to deploy and start the proper VM/Docker, while Neutron receives commands to implement the paths among VNFs. To this purpose, Neutron exploits the ODL controller, which inserts the flowmods in the proper switches; note that switches could be either inside a Nova compute node, or physical switches used to connect several servers, in case the VNFs of the graph have been instantiated by the Nova scheduler on many compute nodes. It is worth pointing out that several modifications have been done both in the Nova scheduler and in Neutron, in order to implement a network aware scheduling able to deploy VNFs on the servers of the cluster by considering the paths among them in the NF-FG. In fact, the original scheduling algorithm available in OpenStack schedules VMs/Docker in isolation, without considering possible interactions among them; this does not fit with NFV requirements, as NF-FGs are by definition sequences of possibly dependent VNFs.

# Available infrastructure
The infrastructure that POLITO makes available, as shown in the image below, is composed by a single OpenStack instance which is formed by an OpenStack controller, an OpenStack network node, an SDN controller (OpenDaylight) and a set of servers (compute nodes) controlled by our OpenStack controller. A compute node is is a server that runs an OpenStack compute node with kvm as hypervisor and openvswitch as vbridge.

![modules](https://raw.githubusercontent.com/netgroup-polito/frog3/master/images/modules-view.jpeg)

Each service graph will be instantiated in the node where a client is connected and all traffic directed to the Internet exit directly from the node, without going through the OpenStack network node (as happens in a legacy installation of OpenStack).

In each node, in addition to the bridge created by OpenStack (br-int, where all VMs are connected), is created two more switches to manage the ingress traffic from the users' devices and the traffic directed through the Internet, as shown in the image below.

![prototype](https://raw.githubusercontent.com/netgroup-polito/frog3/master/images/prototype.jpeg)

In particular, br-ex and br-usr work as classic L2 switches, so they can forward the traffic to the right NF-FG or to right user port.

Managing a geographical OpenStack instance, the more relevant problem is the Image transfer time. From the OpenStack controller, where resides Glance (the OpenStack image repository), placed in Turin and the compute node placed somewhere in the WAN, can it be a poor available bandwidth, in this case the request of instantiation of a service graph may take a lot of time to be successfully terminated, depending on the available bandwidth. 

Initially for every partners will be provided two service graphs (associated with two keystone users). One is an authentication graph, that handle the traffic of all unauthenticated user and force all HTTP traffic to a captive portal. A successful authentication triggers a request to the service layer, that instantiate a service graph of the logged user. The second graph is a simple graph that contain an iptables firewall that block same web addresses in addition to a DHCP and a NAT function. 

Is not possible to instantiate in the same time more than one service graph per user. So, only changing the existent service graph you can have a different graph of network function on the node for a specific user.
