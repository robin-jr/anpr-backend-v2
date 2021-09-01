/*
-- Query: SELECT * FROM rlvd_db.license_plates_rlvd
LIMIT 0, 1000

-- Date: 2021-08-23 22:58
*/
CREATE TABLE `license_plates_rlvd` (
  `entry_id` bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `object_id` varchar(100) DEFAULT NULL,
  `camera_name` varchar(100) NOT NULL,
  `junction_name` varchar(100) NOT NULL,
  `evidence_camera_name` varchar(100) NOT NULL,
  `number_plate_number` varchar(50) NOT NULL,
  `date` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  `anpr_image` varchar(100) NOT NULL,
  `cropped_image` varchar(100) NOT NULL,
  `reviewed` int NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


INSERT INTO `license_plates_rlvd` (`object_id`,`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`cropped_image`) VALUES (1,'SathyaShowroom Front','Sathya Showroom','Sathya Evidence Camera 1','TN32AB1234','2021-08-18 07:08:03.000000','images/results/anpr1.png','images/results/crop1.png');
INSERT INTO `license_plates_rlvd` (`object_id`,`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`cropped_image`) VALUES (2,'SathyaShowroom Back ','Sathya Showroom','Sathya Evidence Camera 2','TN35BZ123','2021-08-18 07:18:03.000000','images/results/anpr2.png','images/results/crop2.png');
INSERT INTO `license_plates_rlvd` (`object_id`,`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`cropped_image`) VALUES (3,'NIFT Entrance','Tidal Park Junction','Tidel Park Evidence Camera 1','TN32AB1234','2021-08-16 15:28:03.000000','images/results/anpr3.png','images/results/crop3.png');
INSERT INTO `license_plates_rlvd` (`object_id`,`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`cropped_image`) VALUES (4,'SRP Tools','Tidal Park Junction','Tidel Park Evidence Camera 1','TN32AB1234','2021-08-16 15:28:03.000000','images/results/anpr4.png','images/results/crop4.png');
INSERT INTO `license_plates_rlvd` (`object_id`,`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`cropped_image`) VALUES (5,'NIFT Left','Tidal Park Junction','Tidel Park Evidence Camera 2','TN12BC7284','2021-08-16 15:49:03.000000','images/results/anpr5.png','images/results/crop5.png');
INSERT INTO `license_plates_rlvd` (`object_id`,`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`cropped_image`) VALUES (6,'SathyaShowroom Left ','Sathya Showroom','Sathya Evidence Camera 1','TS17B2347','2021-08-18 07:09:43.000000','images/results/anpr6.png','images/results/crop6.png');
