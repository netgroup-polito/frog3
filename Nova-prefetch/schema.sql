-- Dump della struttura di tabella precache.prefetching
CREATE TABLE IF NOT EXISTS `prefetching` (
  `compute_hostname` varchar(50) NOT NULL,
  `image_id` varchar(50) NOT NULL,
  `md5` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'PENDING',
  `message` varchar(255) DEFAULT NULL,
  `added_on` datetime DEFAULT NULL,
  `priority` int(11) unsigned NOT NULL DEFAULT '1',
  `dowload_completed_on` datetime DEFAULT NULL,
  `marked_for_deletion` tinyint(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`compute_hostname`,`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;