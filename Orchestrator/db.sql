-- phpMyAdmin SQL Dump
-- version 4.4.14
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Creato il: Set 27, 2015 alle 16:50
-- Versione del server: 5.6.26
-- Versione PHP: 5.6.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `orchestrator`
--
CREATE DATABASE IF NOT EXISTS `orchestrator` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `orchestrator`;

-- --------------------------------------------------------

--
-- Struttura della tabella `endpoint`
--

DROP TABLE IF EXISTS `endpoint`;
CREATE TABLE IF NOT EXISTS `endpoint` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(64) DEFAULT NULL,
  `graph_endpoint_id` varchar(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `graph_id` varchar(64) NOT NULL,
  `name` varchar(64) DEFAULT NULL,
  `type` varchar(64) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `endpoint_resource`
--

DROP TABLE IF EXISTS `endpoint_resource`;
CREATE TABLE IF NOT EXISTS `endpoint_resource` (
  `endpoint_id` int(64) NOT NULL,
  `resource_type` varchar(64) NOT NULL,
  `resource_id` int(64) NOT NULL,
  `session_id` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `flowspec`
--

DROP TABLE IF EXISTS `flowspec`;
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
  `protocol` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `graph`
--

DROP TABLE IF EXISTS `graph`;
CREATE TABLE IF NOT EXISTS `graph` (
  `id` int(64) NOT NULL,
  `session_id` varchar(64) NOT NULL,
  `node_id` varchar(64) DEFAULT NULL,
  `partial` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `graph_connection`
--

DROP TABLE IF EXISTS `graph_connection`;
CREATE TABLE IF NOT EXISTS `graph_connection` (
  `endpoint_id_1` varchar(64) NOT NULL,
  `endpoint_id_2` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `node`
--

DROP TABLE IF EXISTS `node`;
CREATE TABLE IF NOT EXISTS `node` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` varchar(64) NOT NULL,
  `domain_id` varchar(64) NOT NULL,
  `availability_zone` varchar(64) NOT NULL,
  `openstack_controller` varchar(64) NOT NULL,
  `openflow_controller` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `openflow_controller`
--

DROP TABLE IF EXISTS `openflow_controller`;
CREATE TABLE IF NOT EXISTS `openflow_controller` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `endpoint` varchar(64) CHARACTER SET utf8 NOT NULL,
  `version` varchar(64) CHARACTER SET utf8 NOT NULL,
  `username` varchar(64) CHARACTER SET utf8 NOT NULL,
  `password` varchar(64) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `openstack_network`
--

DROP TABLE IF EXISTS `openstack_network`;
CREATE TABLE IF NOT EXISTS `openstack_network` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `status` varchar(64) NOT NULL,
  `vlan_id` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `openstack_subnet`
--

DROP TABLE IF EXISTS `openstack_subnet`;
CREATE TABLE IF NOT EXISTS `openstack_subnet` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `os_network_id` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `o_arch`
--

DROP TABLE IF EXISTS `o_arch`;
CREATE TABLE IF NOT EXISTS `o_arch` (
  `id` int(64) NOT NULL,
  `internal_id` varchar(255) DEFAULT NULL,
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
  `last_update` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `port`
--

DROP TABLE IF EXISTS `port`;
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
  `gre_key` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `session`
--

DROP TABLE IF EXISTS `session`;
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
  `ended` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `tenant`
--

DROP TABLE IF EXISTS `tenant`;
CREATE TABLE IF NOT EXISTS `tenant` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `name` varchar(64) CHARACTER SET utf8 NOT NULL,
  `description` varchar(128) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id` varchar(64) CHARACTER SET utf8 NOT NULL,
  `name` varchar(64) CHARACTER SET utf8 NOT NULL,
  `password` varchar(64) CHARACTER SET utf8 NOT NULL,
  `tenant` varchar(64) CHARACTER SET utf8 NOT NULL,
  `mail` varchar(64) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `user_device`
--

DROP TABLE IF EXISTS `user_device`;
CREATE TABLE IF NOT EXISTS `user_device` (
  `session_id` varchar(64) NOT NULL,
  `mac_address` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Struttura della tabella `user_location`
--

DROP TABLE IF EXISTS `user_location`;
CREATE TABLE IF NOT EXISTS `user_location` (
  `user_id` varchar(64) NOT NULL,
  `node_id` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `vnf_image`
--

DROP TABLE IF EXISTS `vnf_image`;
CREATE TABLE IF NOT EXISTS `vnf_image` (
  `id` varchar(255) NOT NULL,
  `internal_id` varchar(255) NOT NULL,
  `template` text NOT NULL,
  `configuration_model` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `vnf_instance`
--

DROP TABLE IF EXISTS `vnf_instance`;
CREATE TABLE IF NOT EXISTS `vnf_instance` (
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
  `availability_zone` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `endpoint`
--
ALTER TABLE `endpoint`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `endpoint_resource`
--
ALTER TABLE `endpoint_resource`
  ADD PRIMARY KEY (`endpoint_id`,`resource_type`,`resource_id`,`session_id`);

--
-- Indici per le tabelle `flowspec`
--
ALTER TABLE `flowspec`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `graph`
--
ALTER TABLE `graph`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `service_graph_id` (`session_id`,`node_id`);

--
-- Indici per le tabelle `graph_connection`
--
ALTER TABLE `graph_connection`
  ADD PRIMARY KEY (`endpoint_id_1`,`endpoint_id_2`);

--
-- Indici per le tabelle `node`
--
ALTER TABLE `node`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `openflow_controller`
--
ALTER TABLE `openflow_controller`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `openstack_network`
--
ALTER TABLE `openstack_network`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `openstack_subnet`
--
ALTER TABLE `openstack_subnet`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `o_arch`
--
ALTER TABLE `o_arch`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `port`
--
ALTER TABLE `port`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `graph_port_id` (`graph_port_id`,`session_id`,`vnf_id`);

--
-- Indici per le tabelle `session`
--
ALTER TABLE `session`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `user_device`
--
ALTER TABLE `user_device`
  ADD PRIMARY KEY (`session_id`,`mac_address`);

--
-- Indici per le tabelle `user_location`
--
ALTER TABLE `user_location`
  ADD PRIMARY KEY (`user_id`,`node_id`);

--
-- Indici per le tabelle `vnf_image`
--
ALTER TABLE `vnf_image`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `vnf_instance`
--
ALTER TABLE `vnf_instance`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `graph_vnf_id` (`graph_vnf_id`,`session_id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
