# OpenStack+ 

OpenStack+ is an enhanced version of OpenStack icehouse, that introduce the support for NFV. In particular, the main feature added by this project are. 
- The primiteve of traffic steering in neutron, that allows to connect an OpenStack port to another OpenStack port or to an external port and viceversa.
- A prefetch mechanism that allows a selective prefetch on the glance images per node. This is very usefull for compute nodes connected to a controller with low bandwidth.

### Installation

Run install_extension.sh in each OpenStack submodule that you find in the repository.

```sh
$ ./install_extension.sh
```
