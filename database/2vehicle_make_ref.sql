CREATE TABLE `vehicle_make_ref` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `type_id` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


INSERT INTO `vehicle_make_ref` (`name`, `type_id`) VALUES ('Honda', '1,2');
INSERT INTO `vehicle_make_ref` (`name`, `type_id`) VALUES ('Yamaha', '1');
INSERT INTO `vehicle_make_ref` (`name`, `type_id`) VALUES ('Toyato', '2');
INSERT INTO `vehicle_make_ref` (`name`, `type_id`) VALUES ('Mahendra', '3');








