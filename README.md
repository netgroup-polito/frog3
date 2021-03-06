#  FROG3 Repository Summary
This repository contains the current implementation of the FROG3 prototype.
Please check individual README's in each sub-package, all other documentation is located in the docs folder.

## FROG Service Layer
The FROG Service Layer running on top of the FROGv3 orchestrator. It allows each user to define his own service graph (a.k.a. NFV service chain). The network is initially configured with a default service graph that redirect all the unknown traffic (e.g., generated by users connecting to the network with their laptop) to a captive portal, for user identification. A successful user authentication triggers the instantiation of the service graph associated to that user. From that point on, all the traffic of that user will pass through the functions defined in the user' selected service graph before being transmitted to the Internet. All the traffic of the unauthenticated users are instead redirected to the captive portal, until a successfull autentication occurs.

## FROG Orchestrator
The Global Orchestrator is part of the orchestration layer (piece of a bigger architercture defined in the European project Unify - https://www.fp7-unify.eu/). It sits below the service layer and it is responsible of two important phases in the deployment of a service on the physical infrastructure. First, it further manipulates the NF-FG in order to allow its deployment; these transformations include the enriching of the initial definition with extra details such as new VNFs, as well as the consolidation of several VNFs into a single one. Second, the orchestration layer implements the scheduler that is in charge of deciding where to instantiate the requested service (although this feature is not yet available in the current implementation of FROG).

## OpenStack Plus
OpenStack+ is an enhanced version of OpenStack icehouse, that introduce the support for NFV. In particular, the main feature added by this project are.
- The primiteve of traffic steering in neutron, that allows to connect an OpenStack port to another OpenStack port or to an external port and viceversa.
- A prefetch mechanism that allows a selective prefetch on the glance images per node. This is very usefull for compute nodes connected to a controller with low bandwidth.

## VNFs
This folder contains some examples of virtual network functions.