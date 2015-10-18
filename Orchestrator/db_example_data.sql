-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generato il: Ott 18, 2015 alle 18:38
-- Versione del server: 5.5.44-0ubuntu0.14.04.1
-- Versione PHP: 5.5.9-1ubuntu4.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `orchestrator`
--

--
-- Dump dei dati per la tabella `graph`
--

INSERT INTO `graph` (`id`, `session_id`, `node_id`, `partial`) VALUES
(0, '0093ab09fa3e41919d1423591adc6c5e', '2', 0);

--
-- Dump dei dati per la tabella `node`
--

INSERT INTO `node` (`id`, `name`, `type`, `domain_id`, `availability_zone`, `openstack_controller`, `openflow_controller`) VALUES
('2', 'nodo-mi:sw1', 'JolnetCA', 'openflow:110953238267840', 'AZ_MI', '244', 'LITH01'),
('244', 'Jolnet_controller', 'JolnetCA', '163.162.234.44', '', '', ''),
('567', 'Heat_node', 'HeatCA', '130.192.225.193', 'nova', '6456', 'OSCA'),
('6456', 'Heat_ctrl', 'HeatCA', 'controller.ipv6.polito.it', '', '', '');

--
-- Dump dei dati per la tabella `openflow_controller`
--

INSERT INTO `openflow_controller` (`id`, `endpoint`, `version`, `username`, `password`) VALUES
('LITH01', 'http://130.192.225.92:8181', 'LITHIUM', 'admin', 'exp31032014'),
('OSCA', 'http://odl.ipv6.polito.it:8080', 'HYDROGEN', 'admin', 'SDN@Edge_Polito');

--
-- Dump dei dati per la tabella `tenant`
--

INSERT INTO `tenant` (`id`, `name`, `description`) VALUES
('1', 'PoliTO_chain1', 'Tenant to access the Jolnet'),
('3', 'demo_jolnet', 'demo Jolnet');

--
-- Dump dei dati per la tabella `user`
--

INSERT INTO `user` (`id`, `name`, `password`, `tenant`, `mail`) VALUES
('1', 'AdminPoliTO', 'AdminPoliTO', '1', NULL),
('3', 'demo_jolnet', 'stack', '3', 'aaa@hhh.it');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
