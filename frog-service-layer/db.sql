-- phpMyAdmin SQL Dump
-- version 4.4.10
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 13, 2015 at 03:39 PM
-- Server version: 5.5.42
-- PHP Version: 5.6.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `service_layer`
--

-- --------------------------------------------------------

--
-- Table structure for table `node`
--

CREATE TABLE `node` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `domain_id` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `node`
--

INSERT INTO `node` (`id`, `name`, `domain_id`) VALUES
('0', 'node0', '130.192.225.105'),
('1', 'node1', '130.192.225.193'),
('2', 'node2', '10.0.0.3'),
('3', 'node3', '10.0.0.4'),
('4', 'node4', '10.0.0.5');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `node`
--
ALTER TABLE `node`
  ADD PRIMARY KEY (`id`);

