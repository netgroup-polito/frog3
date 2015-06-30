# Global Orchestrator

The Global Orchestrator is part of the  orchestration layer  (piece of a bigger architercture defined in the European project Unify - https://www.fp7-unify.eu/). It sits below the service layer and it is responsible of two important phases in the deployment of a service on the physical infrastructure. First, it further manipulates the NF-FG in order to allow its deployment;  these transformations include the enriching of the initial definition with extra details such as new VNFs, as well as the consolidation of several VNFs into a single one. Second, the orchestration layer implements the scheduler that is in charge of deciding where to instantiate the requested service (although this feature is not yet available in the current implementation of FROG).

The Unify architecture splits this layer in three logical sub-layers. In FROG, the global orchestrator module implements the first two sub-layers, and consists of a technology dependent and a technology independent part. The technology independent part receives the NF-FG from the service layer through its northbound interface, and executes the following manipulations on the graph:
- VNFs expansion: for each VNF specified in the NF-FG, it retrieves the corresponding VNF template. In fact, each VNF is associated with a template (described later on in the document),  which describes the VNF itself. It contains some information related to the hardware required by the VNF, describes the ports of the VNF, etc. Moreover, the template could say that a VNF is actually a sub-graph composed of other VNFs; for example, a Firewall could be implemented as a sub-graph composed of an URL filter only operating on the web traffic, while the non-web traffic is delivered to a stateless firewall. Even, these new VNFs are in turn associated with a template, and can be recursively expanded in further sub-graphs. The global orchestrator replaces, in the NF-FG, the original VNF with the sub-graph described in the template;
- VNFs consolidation: those VNFs implementing the L2 forwarding and that are connected together in the NF-FG, are replaced with a single VNF, in order to limit the resources required to implement the LANs on the physical infrastructure;

The technology dependent part receives the NF-FG from the thechnology indipendendent part and it transform the NF-FG in an other formalism (even the same, like in case of the Universal node is used as infrastucture layer), according to the type of infrastructure layer on which the graph is going to be deployed.  In fact, the global orchestrator supports many implementation of the infrastructure layer.

#Installation

- Required command to launch to install required python library (Tested on 
	ubuntu 14.04.1)

```sh	
$ git clone https://github.com/netgroup-polito/frog3
$ cd frog3/Orchestrator
$ sudo apt-get install python-dev python-setuptools python-sqlalchemy libmysqlclient-dev
$ sudo easy_install pip
$ sudo pip install --upgrade cython falcon requests gunicorn jsonschema mysql-python json_hyper_schema
$ ./create_db.sh
```

### Configuration
The configuration file is stored in Configuration/orchestrator.conf

### How to run
```sh
$ ./start_service_layer.sh
```
