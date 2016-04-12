-- phpMyAdmin SQL Dump
-- version 4.4.10
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 13, 2015 at 03:33 PM
-- Server version: 5.5.42
-- PHP Version: 5.6.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `orchestrator`
--

-- --------------------------------------------------------

--
-- Table structure for table `action`
--

CREATE TABLE `action` (
  `id` int(64) NOT NULL,
  `flow_rule_id` varchar(64) NOT NULL,
  `output_type` varchar(64) DEFAULT NULL,
  `output` varchar(64) DEFAULT NULL,
  `controller` tinyint(1) DEFAULT NULL,
  `_drop` tinyint(1) NOT NULL,
  `set_vlan_id` varchar(64) DEFAULT NULL,
  `set_vlan_priority` varchar(64) DEFAULT NULL,
  `pop_vlan` tinyint(1) DEFAULT NULL,
  `set_ethernet_src_address` varchar(64) DEFAULT NULL,
  `set_ethernet_dst_address` varchar(64) DEFAULT NULL,
  `set_ip_src_address` varchar(64) DEFAULT NULL,
  `set_ip_dst_address` varchar(64) DEFAULT NULL,
  `set_ip_tos` varchar(64) DEFAULT NULL,
  `set_l4_src_port` varchar(64) DEFAULT NULL,
  `set_l4_dst_port` varchar(64) DEFAULT NULL,
  `output_to_queue` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `endpoint`
--

CREATE TABLE `endpoint` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(64) DEFAULT NULL,
  `graph_endpoint_id` varchar(64) NOT NULL,
  `graph_id` varchar(64) NOT NULL,
  `name` varchar(64) DEFAULT NULL,
  `type` varchar(64) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `endpoint_resource`
--

CREATE TABLE `endpoint_resource` (
  `endpoint_id` int(64) NOT NULL,
  `resource_type` varchar(64) NOT NULL,
  `resource_id` int(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `flow_rule`
--

CREATE TABLE `flow_rule` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(255) DEFAULT NULL,
  `graph_flow_rule_id` varchar(64) NOT NULL,
  `graph_id` varchar(64) NOT NULL,
  `priority` varchar(64) DEFAULT NULL,
  `type` varchar(64) DEFAULT NULL,
  `node_id` varchar(64) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `creation_date` datetime NOT NULL,
  `last_update` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `graph`
--

CREATE TABLE `graph` (
  `id` int(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `node_id` varchar(64) DEFAULT NULL,
  `partial` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `graph_connection`
--

CREATE TABLE `graph_connection` (
  `endpoint_id_1` varchar(64) NOT NULL,
  `endpoint_id_1_type` varchar(64) NOT NULL,
  `endpoint_id_2` varchar(64) NOT NULL,
  `endpoint_id_2_type` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `match`
--

CREATE TABLE `match` (
  `id` int(64) NOT NULL,
  `flow_rule_id` varchar(64) NOT NULL,
  `port_in_type` varchar(64) DEFAULT NULL,
  `port_in` varchar(64) DEFAULT NULL,
  `ether_type` varchar(64) DEFAULT NULL,
  `vlan_id` varchar(64) DEFAULT NULL,
  `vlan_priority` varchar(64) DEFAULT NULL,
  `source_mac` varchar(64) DEFAULT NULL,
  `dest_mac` varchar(64) DEFAULT NULL,
  `source_ip` varchar(64) DEFAULT NULL,
  `dest_ip` varchar(64) DEFAULT NULL,
  `tos_bits` varchar(64) DEFAULT NULL,
  `source_port` varchar(64) DEFAULT NULL,
  `dest_port` varchar(64) DEFAULT NULL,
  `protocol` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `node`
--

CREATE TABLE `node` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` varchar(64) NOT NULL,
  `domain_id` varchar(64) NOT NULL,
  `availability_zone` varchar(64) DEFAULT NULL,
  `openstack_controller` varchar(64) DEFAULT NULL,
  `openflow_controller` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `node`
--

INSERT INTO `node` (`id`, `name`, `type`, `domain_id`, `availability_zone`, `openstack_controller`, `openflow_controller`) VALUES
('0', 'node0', 'OpenStack+CA', '130.192.225.105', 'nova', NULL, NULL),
('1', 'node1', 'OpenStack+_compute', '130.192.225.193', 'nova', '0', '0'),
('2', 'node2', 'OpenStack+_compute', '10.0.0.3', 'vecchia', '0', '0'),
('3', 'node3', 'OpenStack+_compute', '10.0.0.4', 'nova', '0', '0'),
('4', 'node4', 'UnifiedNode', '10.0.0.5', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `openflow_controller`
--

CREATE TABLE `openflow_controller` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `endpoint` varchar(64) CHARACTER SET utf8 NOT NULL,
  `version` varchar(64) CHARACTER SET utf8 NOT NULL,
  `username` varchar(64) CHARACTER SET utf8 NOT NULL,
  `password` varchar(64) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `openflow_controller`
--

INSERT INTO `openflow_controller` (`id`, `endpoint`, `version`, `username`, `password`) VALUES
('0', 'http://130.192.225.103:8080', 'Hydrogen', 'admin', 'SDN@Edge_Polito');

-- --------------------------------------------------------

--
-- Table structure for table `openstack_network`
--

CREATE TABLE `openstack_network` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `status` varchar(64) NOT NULL,
  `vlan_id` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `openstack_subnet`
--

CREATE TABLE `openstack_subnet` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `os_network_id` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `port`
--

CREATE TABLE `port` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(64) DEFAULT NULL,
  `graph_port_id` varchar(64) NOT NULL,
  `graph_id` int(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `vnf_id` varchar(64) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `type` varchar(64) DEFAULT NULL,
  `virtual_switch` varchar(64) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `creation_date` datetime NOT NULL,
  `last_update` datetime DEFAULT NULL,
  `os_network_id` varchar(64) DEFAULT NULL,
  `mac_address` varchar(64) DEFAULT NULL,
  `ipv4_address` varchar(64) DEFAULT NULL,
  `vlan_id` varchar(64) DEFAULT NULL,
  `gre_key` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `session`
--

CREATE TABLE `session` (
  `id` varchar(64) NOT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `service_graph_id` varchar(63) NOT NULL,
  `service_graph_name` varchar(64) NOT NULL,
  `ingress_node` varchar(64) DEFAULT NULL,
  `egress_node` varchar(64) DEFAULT NULL,
  `status` varchar(64) NOT NULL,
  `started_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `error` datetime DEFAULT NULL,
  `ended` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tenant`
--

CREATE TABLE `tenant` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `name` varchar(64) CHARACTER SET utf8 NOT NULL,
  `description` varchar(128) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `tenant`
--

INSERT INTO `tenant` (`id`, `name`, `description`) VALUES
('0', 'demo', 'Demo tenant'),
('1', 'isp', 'ISP Tenant'),
('2', 'demo2', 'Demo2 Tenant');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `name` varchar(64) CHARACTER SET utf8 NOT NULL,
  `password` varchar(64) CHARACTER SET utf8 NOT NULL,
  `tenant_id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `mail` varchar(64) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `password`, `tenant_id`, `mail`) VALUES
('0', 'demo', 'stack', '0', NULL),
('1', 'isp', 'stack', '1', NULL),
('2', 'demo2', 'stack', '2', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `vnf_image`
--

CREATE TABLE `vnf_image` (
  `id` varchar(255) NOT NULL,
  `internal_id` varchar(255) NOT NULL,
  `template` text NOT NULL,
  `configuration_model` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `vnf_instance`
--

CREATE TABLE `vnf_instance` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(64) DEFAULT NULL,
  `graph_vnf_id` varchar(64) NOT NULL,
  `graph_id` int(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `template_location` varchar(64) NOT NULL,
  `image_location` varchar(64) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `type` varchar(64) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `creation_date` datetime NOT NULL,
  `last_update` datetime DEFAULT NULL,
  `availability_zone` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `action`
--
ALTER TABLE `action`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `endpoint`
--
ALTER TABLE `endpoint`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `endpoint_resource`
--
ALTER TABLE `endpoint_resource`
  ADD PRIMARY KEY (`endpoint_id`,`resource_type`,`resource_id`);

--
-- Indexes for table `flow_rule`
--
ALTER TABLE `flow_rule`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `graph`
--
ALTER TABLE `graph`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `service_graph_id` (`session_id`,`node_id`);

--
-- Indexes for table `graph_connection`
--
ALTER TABLE `graph_connection`
  ADD PRIMARY KEY (`endpoint_id_1`,`endpoint_id_1_type`,`endpoint_id_2`,`endpoint_id_2_type`);

--
-- Indexes for table `match`
--
ALTER TABLE `match`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `node`
--
ALTER TABLE `node`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `openflow_controller`
--
ALTER TABLE `openflow_controller`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `openstack_network`
--
ALTER TABLE `openstack_network`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `openstack_subnet`
--
ALTER TABLE `openstack_subnet`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `port`
--
ALTER TABLE `port`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `graph_port_id` (`graph_port_id`,`vnf_id`);

--
-- Indexes for table `session`
--
ALTER TABLE `session`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tenant`
--
ALTER TABLE `tenant`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `vnf_image`
--
ALTER TABLE `vnf_image`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `vnf_instance`
--
ALTER TABLE `vnf_instance`
  ADD PRIMARY KEY (`id`);

