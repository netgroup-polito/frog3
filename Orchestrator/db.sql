-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generato il: Lug 03, 2015 alle 15:52
-- Versione del server: 5.5.41-0ubuntu0.14.04.1
-- Versione PHP: 5.5.9-1ubuntu4.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `orchestrator`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `endpoint`
--

CREATE TABLE IF NOT EXISTS `endpoint` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(64) DEFAULT NULL,
  `graph_endpoint_id` varchar(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `graph_id` varchar(64) NOT NULL,
  `type` varchar(64) NOT NULL,
  `location` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `endpoint_resource`
--

CREATE TABLE IF NOT EXISTS `endpoint_resource` (
  `endpoint_id` int(64) NOT NULL,
  `resource_type` varchar(64) NOT NULL,
  `resource_id` int(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  PRIMARY KEY (`endpoint_id`,`resource_type`,`resource_id`,`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `flowspec`
--

CREATE TABLE IF NOT EXISTS `flowspec` (
  `id` int(64) NOT NULL,
  `match_id` varchar(64) NOT NULL,
  `o_arch_id` varchar(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `graph_id` varchar(64) NOT NULL,
  `priority` varchar(64) DEFAULT NULL,
  `etherType` varchar(64) DEFAULT NULL,
  `vlanId` varchar(64) DEFAULT NULL,
  `vlanPriority` varchar(64) DEFAULT NULL,
  `dlSrc` varchar(64) DEFAULT NULL,
  `dlDst` varchar(64) DEFAULT NULL,
  `nwSrc` varchar(64) DEFAULT NULL,
  `nwDst` varchar(64) DEFAULT NULL,
  `tosBits` varchar(64) DEFAULT NULL,
  `tpSrc` varchar(64) DEFAULT NULL,
  `tpDst` varchar(64) DEFAULT NULL,
  `protocol` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `graph`
--

CREATE TABLE IF NOT EXISTS `graph` (
  `id` int(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `node_id` varchar(64) DEFAULT NULL,
  `partial` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `service_graph_id` (`session_id`,`node_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `graph_connection`
--

CREATE TABLE IF NOT EXISTS `graph_connection` (
  `endpoint_id_1` varchar(64) NOT NULL,
  `endpoint_id_2` varchar(64) NOT NULL,
  PRIMARY KEY (`endpoint_id_1`,`endpoint_id_2`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `node`
--

CREATE TABLE IF NOT EXISTS `node` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` varchar(64) NOT NULL,
  `domain_id` varchar(64) DEFAULT NULL,
  `availability_zone` varchar(64) DEFAULT NULL,
  `controller_node` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `openstack_network`
--

CREATE TABLE IF NOT EXISTS `openstack_network` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `status` varchar(64) NOT NULL,
  `vlan_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `openstack_subnet`
--

CREATE TABLE IF NOT EXISTS `openstack_subnet` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `os_network_id` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `o_arch`
--

CREATE TABLE IF NOT EXISTS `o_arch` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(64) DEFAULT NULL,
  `graph_o_arch_id` varchar(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `graph_id` varchar(64) NOT NULL,
  `type` varchar(64) DEFAULT NULL,
  `start_node_type` varchar(64) NOT NULL,
  `start_node_id` varchar(64) NOT NULL,
  `end_node_type` varchar(64) NOT NULL,
  `end_node_id` varchar(64) NOT NULL,
  `status` varchar(64) DEFAULT NULL,
  `creation_date` datetime NOT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `port`
--

CREATE TABLE IF NOT EXISTS `port` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(64) DEFAULT NULL,
  `graph_port_id` varchar(64) DEFAULT NULL,
  `session_id` varchar(64) NOT NULL,
  `graph_id` varchar(64) NOT NULL,
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
  `gre_key` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `graph_port_id` (`graph_port_id`,`session_id`,`vnf_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `session`
--

CREATE TABLE IF NOT EXISTS `session` (
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
  `ended` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `user_device`
--

CREATE TABLE IF NOT EXISTS `user_device` (
  `session_id` varchar(64) NOT NULL,
  `mac_address` varchar(64) NOT NULL,
  PRIMARY KEY (`session_id`,`mac_address`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `user_location`
--

CREATE TABLE IF NOT EXISTS `user_location` (
  `user_id` varchar(64) NOT NULL,
  `node_id` varchar(64) NOT NULL,
  PRIMARY KEY (`user_id`,`node_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `vnf`
--

CREATE TABLE IF NOT EXISTS `vnf` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(64) DEFAULT NULL,
  `graph_vnf_id` varchar(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `graph_id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `template_location` varchar(64) NOT NULL,
  `image_location` varchar(64) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `type` varchar(64) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `creation_date` datetime NOT NULL,
  `last_update` datetime DEFAULT NULL,
  `availability_zone` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `graph_vnf_id` (`graph_vnf_id`,`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

