/*
-- Query: SELECT * FROM rlvd_db.violations
LIMIT 0, 1000

-- Date: 2021-08-23 22:57
*/

CREATE TABLE `violations` (
  `id` bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `violation_id` int NOT NULL,
  `object_id` varchar(100) DEFAULT NULL 
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (1,1);
INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (2,1);
INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (2,2);
INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (1,3);
INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (2,4);
INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (3,4);
INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (1,5);
INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (3,5);
INSERT INTO `violations` (`violation_id`,`object_id`) VALUES (2,6);


CREATE TABLE `violation_ref` (
  `id` bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `violation_name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
INSERT INTO `violation_ref` (`id`,`violation_name`) VALUES (1,'Red Light');
INSERT INTO `violation_ref` (`id`,`violation_name`) VALUES (2,'Helmet');
INSERT INTO `violation_ref` (`id`,`violation_name`) VALUES (3,'Triples');
