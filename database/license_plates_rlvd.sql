/*
-- Query: SELECT * FROM rlvd_db.license_plates_rlvd
LIMIT 0, 1000

-- Date: 2021-08-23 22:58
*/
CREATE TABLE `license_plates_rlvd` (
  `entry_id` bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `camera_name` varchar(100) NOT NULL,
  `junction_name` varchar(100) NOT NULL,
  `evidence_camera_name` varchar(100) NOT NULL,
  `number_plate_number` varchar(50) NOT NULL,
  `date` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  `anpr_image` varchar(100) NOT NULL,
  `xmin` varchar(50) NOT NULL,
  `xmax` varchar(50) NOT NULL,
  `ymin` varchar(50) NOT NULL,
  `ymax` varchar(50) NOT NULL,
  `reviewed` int NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


INSERT INTO `license_plates_rlvd` (`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`xmin`,`xmax`,`ymin`,`ymax`) VALUES ('SathyaShowroom Front','Sathya Showroom','Sathya Evidence Camera 1','TN32AB1234','2021-08-18 07:08:03.000000','/home/user/images/results/FullImage1.jpg','50','60','70','80');
INSERT INTO `license_plates_rlvd` (`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`xmin`,`xmax`,`ymin`,`ymax`) VALUES ('SathyaShowroom Back ','Sathya Showroom','Sathya Evidence Camera 2','TN35BZ123','2021-08-18 07:18:03.000000','/home/user/images/results/FullImage2.jpg','51','65','78','89');
INSERT INTO `license_plates_rlvd` (`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`xmin`,`xmax`,`ymin`,`ymax`) VALUES ('NIFT Entrance','Tidal Park Junction','Tidel Park Evidence Camera 1','TN32AB1234','2021-08-16 15:28:03.000000','/home/user/images/results/FullImage6.jpg','10','60','45','80');
INSERT INTO `license_plates_rlvd` (`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`xmin`,`xmax`,`ymin`,`ymax`) VALUES ('SRP Tools','Tidal Park Junction','Tidel Park Evidence Camera 1','TN32AB1234','2021-08-16 15:28:03.000000','/home/user/images/results/FullImage6.jpg','50','60','77','120');
INSERT INTO `license_plates_rlvd` (`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`xmin`,`xmax`,`ymin`,`ymax`) VALUES ('NIFT Left','Tidal Park Junction','Tidel Park Evidence Camera 2','TN12BC7284','2021-08-16 15:49:03.000000','/home/user/images/r esults/FullImage10.jpg','54','60','54','80');
INSERT INTO `license_plates_rlvd` (`camera_name`,`junction_name`,`evidence_camera_name`,`number_plate_number`,`date`,`anpr_image`,`xmin`,`xmax`,`ymin`,`ymax`) VALUES ('SathyaShowroom Left ','Sathya Showroom','Sathya Evidence Camera 1','TS17B2347','2021-08-18 07:09:43.000000','/home/user/images/results/FullImage9.jpg','58','60','65','80');
