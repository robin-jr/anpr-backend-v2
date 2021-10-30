CREATE TABLE `vehicle_type_ref` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1;


INSERT INTO `vehicle_type_ref` (`name`) VALUES ('Bike');
INSERT INTO `vehicle_type_ref` (`name`) VALUES ('Car');
INSERT INTO `vehicle_type_ref` (`name`) VALUES ('Heavy Vehicle');
