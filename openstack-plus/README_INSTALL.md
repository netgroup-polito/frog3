# OpenStack Plus installation guide
The installation guide has been tested with Ubuntu 14.04, OpenStack icehouse and Opendaylight hydrogen

## Vanilla OpenStack (stable/icehouse version) controller and network node installation:

During the development phase we leveraged the official guide 
(http://docs.openstack.org/icehouse/install-guide/install/apt/content/)
for the installation and the configuration of components of interest.
Design your OpenStack network and configure it according to your needs

The component that have to be installed are the following: 
-- Identity service (keystone)
-- Command line clients (keystone, glance, nova, neutron)
-- Image service (glance)
-- Compute service (nova, both controller)
-- Networking service (neutron OpenStack networking, both controller and network node)
-- Dashboard GUI (horizon)
		
Note: if you run into some problems when installing nova-api service and the log shows you a problem like "No module named rootwrap.cmd" or something similar, you can try to copy /usr/lib/python2.7/dist-packages/oslo/rootwrap/ in /usr/local/lib/python2.7/dist-packages/oslo and then restart the service

Note: when following the guide pay attention to use file hosts shortcuts only when the guide does it. Some addresses must be written explicitly in the configuration files.

Extras: we suggest also to install phpmyadmin on controller node, to get database operations easier

## Install netgroup extensions
All these modifications must be done on the controller node
	
### NEUTRON
 Install our extension for manage user NF graphs:
```sh
cd Neutron-extension/
sudo ./install_extension.sh
```

## Configure OpenDaylight
We recommend to install OpenDayLight on a separate VM with at least 2 core and 2GB of memory and to place it on the controller node. Of course you can also install it as a separate server, in case you don't care about saving space.
	
Follow the installation guide of Opendaylight (https://wiki.opendaylight.org/view/OVSDB:OVSDB_OpenStack_Guide) and install the ODL controller (we tested it on Ubuntu, not in Fedora). The only fundamental thing is that the vesion of ODL that you choose to install MUST USE OpenFlow 1.0 (NOT OpenFlow 1.3!) with a "MaxPermSize" value of 2048m.
	  
In addiction you should stop the service SimpleForwarding using Opendaylight OSGI interface or, even better, remove the "simple_forwarding.jar" from "plugins" directory (that will prevent it from automatically run at startup)
	  
Give it a public internet address, bridging it on the "br-ex" virtual switch that brings to the outside. This step is important to give a full reachability both to Openstack and ODL virtual machine. To achieve this you must have an OVS external virtual bridge (br-ex) and an external network (ext-net) with its subnet; if you have installed the network node somewhere else, you should install its services also on the controller and stop them and delete the ext-net after finishing the installation of all virtual machines (ODL and custom orchestrator). It can be done through virt-manager (requires GUI), setting br-ex as the default NIC from View->Details->NIC:
- Specify shared device name -> Bridge name: br-ex -> Device model: virtio

But you should also modify it from the xml description file of the virtual machine (virsh edit "vm name"):
- In the <interface type ='bridge'> tag add these lines (immediately after <suorce ..> tag): 
        
        <virtualport type = 'openvswitch'/>


On controller and compute nodes insert the public address in hosts file

- IMPORTANT: before giving ODL the control of your infrastructure you must prevent it from controlling the exit point towards
	  the outside world of your compute node; otherwise you won't even be able to reach it if it's remote!! 
	  On the controller node, create a cron script like the one below (for the ROOT USER!):
		
		sudo ovs-vsctl del-controller br-ex

Now we can set Opendaylight as the preferred ml2 plugin for Openstack:

- go to the file /etc/neutron/plugins/ml2/ml2_conf.ini and change the field "mechanism_drivers" to "opendaylight"
		
- then add a couple of sections at the end of the file

			[odl]
			network_vlan_ranges = 1:4095
			tunnel_id_ranges = 1:1000
			tun_peer_patch_port = patch-int
			int_peer_patch_port = patch-tun

			tenant_network_type = gre
			#tenant_network_type = vlan
			tunnel_bridge = br-tun
			integration_bridge = br-int


			[ml2_odl]
			# (StrOpt) OpenDaylight REST URL
			# If this is not set then no HTTP requests will be made.
			#
			url = http://opendaylight:8080/controller/nb/v2/neutron

			# (StrOpt) Username for HTTP basic authentication to ODL.
			#
			username = admin
			# Example: username = admin

			# (StrOpt) Password for HTTP basic authentication to ODL.
			#
			password = admin
			# Example: password = admin

			# (IntOpt) Timeout in seconds to wait for ODL HTTP request completion.
			# This is an optional parameter, default value is 10 seconds.
			#
			timeout = 15
			# Example: timeout = 15

			# (IntOpt) Timeout in minutes to wait for a Tomcat session timeout.
			# This is an optional parameter, default value is 30 minutes.
			#
			session_timeout = 30
			# Example: session_timeout = 60

- Restart the neutron server (on controller node):

        service neutron-server restart
		
- Set Opendaylight as the manager for the Openswitch infrastructure:

		ovs-vsctl set-manager tcp:xxx.xxx.xxx.xxx:6640
	  
	 (where xxx.xxx.xxx.xxx indicates the public ip address of Opendaylight VM)

- On compute node stop (and remove from startup list) the service "neutron-plugin-openvswitch-agent"
	
## OpenStack compute node installation and configuration
	
### Required hardware and software
Standard Intel server with at least two network interfaces. Due to the necessity to host many virtual machines, we suggest to have at least 8 GB of memory.
 Ubuntu 14.04 LTS (64 bit).
 

### OpenStack compute node installation
Here there are the steps required to install a standard OpenStack icehouse compute node, that will be connected to the OpenStack controller running at POLITO premises. For your convenience, we report here all the required steps (taken from http://docs.openstack.org/icehouse/install-guide/install/apt/content/), which take into account only the components that are needed in our use case (e.g., neutron opendaylight plugin instead of neutron openvswitch plugin).

- Configure name resolution:

    - Set the hostname for the node in /etc/hostname
    
            COMPUTE_HOSTNAME


    - Edit the /etc/hosts file to contain the following:

            127.0.0.1    localhost
            127.0.1.1    COMPUTE_HOSTNAME

- Install the Compute packages:

        sudo apt-get install nova-compute-kvm

- Edit the /etc/nova/nova.conf configuration file and add these lines to the appropriate sections:
    - Replace NOVA_PASS and NOVA_DBPASS with the passwords used in the controller installation.

            [DEFAULT]
            ...
            auth_strategy = keystone
            ...
            [database]
            # The SQLAlchemy connection string used to connect to the database
            connection = mysql://nova:NOVA_DBPASS@controller.ipv6.polito.it/nova
            [keystone_authtoken]
            auth_uri = http://controller.ipv6.polito.it:5000
            auth_host = controller.ipv6.polito.it
            auth_port = 35357
            auth_protocol = http
            admin_tenant_name = service
            admin_user = nova
            admin_password = NOVA_PASS

- Configure the Compute service to use the RabbitMQ message broker by setting these configuration keys in the [DEFAULT] configuration group of the /etc/nova/nova.conf file:
    - Replace RABBIT_PASS with the passwords used in the controller installation.

            [DEFAULT]
            ...
            rpc_backend = rabbit
            rabbit_host = controller.ipv6.polito.it
            rabbit_password = RABBIT_PASS

- Configure Compute to provide remote console access to instances.
    - Edit /etc/nova/nova.conf and add the following keys under the [DEFAULT] section:
        - Replace YOUR_IP_ADDRESS with your public IP address.

                [DEFAULT]
                ...
                my_ip = YOUR_IP_ADDRESS
                vnc_enabled = True
                vncserver_listen = 0.0.0.0
                vncserver_proxyclient_address = YOUR_IP_ADDRESS
                novncproxy_base_url = http://controller.ipv6.polito.it:6080/vnc_auto.html

- Specify the host that runs the Image Service. Edit /etc/nova/nova.conf file and add these lines to the [DEFAULT] section:
        
        [DEFAULT]
        ...
        glance_host = controller.ipv6.polito.it

- You must determine whether your system's processor and/or hypervisor support hardware acceleration for virtual machines.
Run the following command:

        sudo egrep -c '(vmx|svm)' /proc/cpuinfo

    - If this command returns a value of one or greater, your system supports hardware acceleration which typically requires no additional configuration.

    - If this command returns a value of zero, your system does not support hardware acceleration and you must configure libvirt to use QEMU instead of KVM.

        - Edit the [libvirt] section in the /etc/nova/nova-compute.conf file to modify this key:

                [libvirt]
                ...
                virt_type = qemu

- Remove the SQLite database created by the packages:
        
        sudo rm /var/lib/nova/nova.sqlite

- Restart the Compute service:
        
        sudo service nova-compute restart

- Edit /etc/sysctl.conf to contain the following:
        
        net.ipv4.conf.all.rp_filter=0
        net.ipv4.conf.default.rp_filter=0
        net.bridge.bridge-nf-call-arptables=1 
        net.bridge.bridge-nf-call-iptables=1 
        net.bridge.bridge-nf-call-ip6tables=1

- Implement the changes:

        sudo sysctl -p

- To install the Networking components:

        sudo apt-get install neutron-common neutron-plugin-ml2  \
        openvswitch-datapath-dkms openvswitch-switch

- To configure the Networking common components (the Networking common component configuration includes the authentication mechanism, message broker, and plug-in):
    
    - Configure Networking to use the Identity service for authentication:
        - Edit the /etc/neutron/neutron.conf file and add the following key to the [DEFAULT] section:

                [DEFAULT]
                ...
                auth_strategy = keystone
    
    - Add the following keys to the [keystone_authtoken] section:
        - Replace NEUTRON_PASS with the passwords used in the controller installation.

                [keystone_authtoken]
                ...
                auth_uri = http://controller.ipv6.polito.it:5000
                auth_host = controller.ipv6.polito.it
                auth_protocol = http
                auth_port = 35357
                admin_tenant_name = service
                admin_user = neutron
                admin_password = NEUTRON_PASS
    - Configure Networking to use the message broker:
        - Edit the /etc/neutron/neutron.conf file and add the following keys to the [DEFAULT] section:
            - Replace RABBIT_PASS with the passwords used in the controller installation.

                    [DEFAULT]
                    ...
                    rpc_backend = neutron.openstack.common.rpc.impl_kombu
                    rabbit_host = controller.ipv6.polito.it
                    rabbit_password = RABBIT_PASS
                    
    - Configure Networking to use the Modular Layer 2 (ML2) plug-in and associated services:
        - Edit the /etc/neutron/neutron.conf file and add the following keys to the [DEFAULT] section:

                [DEFAULT]
                ...
                core_plugin = ml2
                service_plugins = router
                allow_overlapping_ips = True
 

- To configure the Modular Layer 2 (ML2) plug-in (the ML2 plug-in uses the Open vSwitch (OVS) mechanism (agent) to build the virtual networking framework for instances):

    - Edit the /etc/neutron/plugins/ml2/ml2_conf.ini file, adding the following keys:

            [ml2]
            ...
            type_drivers = gre
            tenant_network_types = gre
            mechanism_drivers = opendaylight

            [ml2_type_gre]
            ...
            tunnel_id_ranges = 1:1000
 

            [securitygroup]
            ...
            firewall_driver = neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver
            enable_security_group = True
 

            # Replace ODL_PASS with the password used in the controller installation.

            [ml2_odl]
            url = http://odl.ipv6.polito.it:8080/controller/nb/v2/neutron
            username = admin
            password = ODL_PASS
            timeout = 10
            session_timeout = 30
            [odl]
            network_vlan_ranges = 1:4095
            tunnel_id_ranges = 1:1000
            tun_peer_patch_port = patch-int
            int_peer_patch_port = patch-tun
            tunnel_bridge = br-tun
            integration_bridge = br-int
 

    - To configure Compute to use Networking. By default, most distributions configure Compute to use legacy networking. You must reconfigure Compute to manage networks through Networking. Edit the /etc/nova/nova.conf and add the following keys to the [DEFAULT] section:
    
            # Replace NEUTRON_PASS with the password used in the controller installation.

            [DEFAULT]
            ...
            network_api_class = nova.network.neutronv2.api.API
            neutron_url = http://controller.ipv6.polito.it:9696
            neutron_auth_strategy = keystone
            neutron_admin_tenant_name = service
            neutron_admin_username = neutron
            neutron_admin_password = NEUTRON_PASS
            neutron_admin_auth_url = http://controller.ipv6.polito.it:35357/v2.0
            linuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver
            firewall_driver = nova.virt.firewall.NoopFirewallDriver
            security_group_api = neutron
 

- Configure the avaibility zone
        
    The availability zone is the temporary mechanism used to place the virtual machines of the user where his is connected.

    - Set the availability zone in /etc/nova/nova.conf:

            [default]
             …
            default_availability_zone = AVAILABILITY_ZONE_NAME
 

- Set the the IP address of the instance tunnels network interface on your network node.
    - Create a script 'odl_os_ovs.sh':
#!/usr/bin/env bash

            # odl_os_ovs.sh : Stands for OpenDaylight_OpenStack_Openvswith.sh (cant be more Open than this ;) )

            if [ `whoami` != "root" ]; then
                echo Please execute this script as superuser or with sudo previleges.
                exit 1
            fi
            
            if [ "$#" -ne 1 ]; then
              echo "Usage: odl_ovs_os.sh " >&2
              echo "        is same as the local-ip configuration done for ovs-neutron-agent in ovs_quantum_plugin.ini"
              exit 1
            fi
            
            read ovstbl <<< $(ovs-vsctl get Open_vSwitch . _uuid)
            ovs-vsctl set Open_vSwitch $ovstbl other_config={"local_ip"="$1"}
            ovs-vsctl list Open_vSwitch .
        
    - Run the script:
            Replace YOUR_IP_ADDRESS with your public IP address.
            
            sudo chmod +x odl_os_ovs.sh
            sudo ./odl_os_ovs.sh YOUR_IP_ADDRESS
 

- Set the manager for OVSDB:

    Note that in this case we need the IP address of the SDN controller, because the hostname is not resolved here.

        sudo ovs-vsctl set-manager tcp:OPENDAYLIGHT_ADDRESS:6640

    - Control that, after this step, in the output of 'ovs-vsctl show' there are the bridges br-int and br-tun. Otherwise execute the following commands.

            sudo ovs-vsctl del-manager
            sudo ovs-vsctl set-manager tcp:OPENDAYLIGHT_ADDRESS:6640
            sudo ovs-vsctl add-br br-int
            sudo ovs-vsctl add-br br-tun
            sudo ovs-vsctl set-fail-mode br-int secure
            sudo ovs-vsctl set-fail-mode br-tun secure
            sudo ovs-vsctl set-controller br-int tcp:OPENDAYLIGHT_ADDRESS:6633
            sudo ovs-vsctl set-controller br-tun tcp:OPENDAYLIGHT_ADDRESS:6633
            sudo ovs-vsctl add-port br-int patch-tun
            sudo ovs-vsctl add-port br-tun patch-int
            sudo ovs-vsctl set interface patch-tun type=patch
            sudo ovs-vsctl set interface patch-int type=patch
            sudo ovs-vsctl set interface patch-tun options:peer=patch-int
            sudo ovs-vsctl set interface patch-int options:peer=patch-tun
            
    - Now you should see the needed bridge, executing 'ovs-vsctl show'.

- Set the controller of the integration bridge in "out of band" mode:

        sudo ovs-vsctl set controller br-int connection-mode=out-of-band
        sudo ovs-vsctl set bridge br-int other-config:disable-in-band=true
    - WARNING: if you delete the controller from the br-int and then you reset it, you must remember to set it in out-of-band mode.

- Set your preferred RAM allocation ratio (i.e., the oversubscription rate for the memory) in /etc/nova/nova.conf:

        [default]
        …
        ram_allocation_ratio = 5

- To finalize the installation, restart the Compute service:

        sudo service nova-compute restart
 

- Finalize the availability zone installation:

        nova aggregate-create aggregate-<AZ> <AZ>
        nova aggregate-add-host <id-host-aggregate> <compute-name>
 

- Verify the OpenStack standard installation.
    - After you have contacted the FROG administrator, export the following global variables:

        Replace USERNAME, TENANT and PASSWORD with those used on the 'Define users, tenants, and roles' section of keystone instantiation
    
            export OS_USERNAME=USERNAME
            export OS_PASSWORD=PASSWORD
            export OS_TENANT_NAME=TENANT
            export OS_AUTH_URL=http://controller.ipv6.polito.it:35357/v2.0
        
    - Create a network, and associates to it a neutron subnet:
    
        Replace TENANT_NETWORK_CIDR with the IP address and mask (e.g. 10.0.0.0/24) associate to that neutron network.

            neutron net-create demo-net
            neutron subnet-create demo-net --name demo-subnet TENANT_NETWORK_CIDR

    - Take the network ID of the net you have created:

            neutron net-list

    - Boot virtual machine: 

        Replace DEMO_NET_ID with the network id of the previous step and replace AVAILABILITY_ZONE_NAME with the availability zone provided by the FROG administrator at the POLITO domain.

            nova boot --flavor m1.tiny --image cirros-0.3.2-x86_64 --nic net-id=DEMO_NET_ID --availability-zone AVAILABILITY_ZONE_NAME demo-instance1

    - Check the status of the instance newly created: 
        
            nova list

        If the status of the instance converges to 'ACTIVE', the installation of the OpenStack standard compute node is correct and you can continue to follow the guide.

 

 

### Prototype configuration
- Configure the external bridge
    - Add an L2 bridge that manage the exit traffic (it is necessary to deliver the traffic coming from the internet to the NF-FG graph of the correct user, which happens when multiple users are connected to your compute node):

            sudo ovs-vsctl add-br br-ex

    - Add a physical network interface, connected to the Internet, to the external bridge, so the traffic of all NF-FGs will exit through that interface:

        Replace INTERFACE_NAME with the actual interface name. For example, eth0 or em0
            
            sudo ovs-vsctl add-port br-ex INTERFACE_NAME
            
        WARNING: at this point, if you were connected to the node through the interface you had bridged to br-ex, you are no longer able to reach the node. If it is possible, you should use two different interfaces: one for management and the other for the outgoing traffic of NF-FGs. 
        
        If no additional interface are available, to restore the connection you should perform the following steps in order to assign the IP address to the bridge:
        - Remove the IP address from the interface

                sudo ifconfig INTERFACE_NAME 0 

        - Configure the interface and the bridge in /etc/network/interfaces
    
                auto INTERFACE_NAME
                iface INTERFACE_NAME inet manual
                auto br-ex
                iface br-ex inet dhcp
 
        - Restart the configuration of br-ex:

                sudo ifdown br-ex
                sudo ifup br-ex
 

        - Remove the controller from br-ex (this is a bridge that does not need to be controlled by opendaylight):

                sudo ovs-vsctl del-controller br-ex
 

            WARNING: if the interface that you connected to the virtual switch is a physical interface, the bridge take the same MAC address of the interface (hence it obtains the same IP address).
Otherwise you should edit the /etc/nova/nova.conf  file according to the new IP address and restart nova-compute.

 

- Add the ingress bridge:

    - Add an L2 bridge that manage the user traffic:

            sudo ovs-vsctl add-br br-usr

    - Add a port, where you will connect the devices that use the prototype, to the ingress bridge (all the ports bridged to this bridge will be called "LAN" port):
    
        Replace INTERFACE_NAME with the actual interface name. For example, eth0 or wlan0. More then one interface can be connected to this bridge. Connecting a device to those ports you are able to reach your service.

            sudo ovs-vsctl add-port br-usr INTERFACE_NAME

    - Configure the ingress interfaces in /etc/network/interfaces 

            auto INTERFACE_NAME
            iface INTERFACE_NAME inet manual

