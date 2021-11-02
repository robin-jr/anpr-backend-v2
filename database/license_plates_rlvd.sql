
CREATE TABLE `license_plates_rlvd` (
  `entry_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `camera_name` varchar(100) NOT NULL,
  `junction_name` varchar(100) NOT NULL,
  `evidence_camera_name` varchar(100) NOT NULL,
  `number_plate_number` varchar(50) NOT NULL,
  `date` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  `cropped_image` varchar(200) NOT NULL,
  `anpr_image` varchar(200) NOT NULL,
  `evidence_images` varchar(1000) NOT NULL,
  `speed` DECIMAL(5,2) NOT NULL,
  `speed_limit` DECIMAL(5,2) NOT NULL,
  `violations` varchar(100) NOT NULL DEFAULT '',
  `reviewed` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`entry_id`)
) ENGINE=InnoDB;


INSERT INTO `license_plates_rlvd` (`camera_name`, `junction_name`, `evidence_camera_name`, `number_plate_number`, `date`, `cropped_image`, `anpr_image`, `evidence_images`, `speed`, `speed_limit`, `violations`, `reviewed`) VALUES ('Sathya Showroom Front', 'Sathya Showroom', 'Sathya Showroom', 'TN76BX1234', '2021-08-18 07:08:03', 'images/results/crop1.png', 'images/results/anpr1.png', 'images/results/anpr1.png, images/results/anpr2.png', '20.02', '60.00', '1,2', '0');
INSERT INTO `license_plates_rlvd` (`camera_name`, `junction_name`, `evidence_camera_name`, `number_plate_number`, `date`, `cropped_image`, `anpr_image`, `evidence_images`, `speed`, `speed_limit`, `violations`, `reviewed`) VALUES ('Sathya Showroom Back', 'Sathya Showroom', 'Sathya Showroom', 'TN64DC1423', '2021-08-18 07:08:03', 'images/results/crop2.png', 'images/results/anpr2.png', 'images/results/anpr2.png, images/results/anpr4.png', '50', '60.76', '1,2', '0');
INSERT INTO `license_plates_rlvd` (`camera_name`, `junction_name`, `evidence_camera_name`, `number_plate_number`, `date`, `cropped_image`, `anpr_image`, `evidence_images`, `speed`, `speed_limit`, `violations`, `reviewed`) VALUES ('Sathya Showroom Front', 'Sathya Showroom', 'Sathya Showroom', 'TN12DE1245', '2021-08-18 07:08:03', 'images/results/crop3.png', 'images/results/anpr3.png', 'images/results/anpr1.png', '90', '60', '1', '0');
INSERT INTO `license_plates_rlvd` (`camera_name`, `junction_name`, `evidence_camera_name`, `number_plate_number`, `date`, `cropped_image`, `anpr_image`, `evidence_images`, `speed`, `speed_limit`, `violations`, `reviewed`) VALUES ('Sathya Showroom Front', 'Sathya Showroom', 'Sathya Showroom', 'TN12DO1234', '2021-08-18 07:08:03', 'images/results/crop4.png', 'images/results/anpr4.png', 'images/results/anpr1.png', '40', '60', '3', '0');




