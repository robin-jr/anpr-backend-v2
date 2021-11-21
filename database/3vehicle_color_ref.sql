CREATE TABLE `vehicle_color_ref` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `code` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


INSERT INTO `vehicle_color_ref` (`name`, `code`) VALUES ('Red', '#F90716');
INSERT INTO `vehicle_color_ref` (`name`, `code`) VALUES ('Green', '#2FDD92');
INSERT INTO `vehicle_color_ref` (`name`, `code`) VALUES ('Black', '#090910');
INSERT INTO `vehicle_color_ref` (`name`, `code`) VALUES ('Blue', '#2F86A6');
INSERT INTO `vehicle_color_ref` (`name`, `code`) VALUES ('Grey', '#A19882');
INSERT INTO `vehicle_color_ref` (`name`, `code`) VALUES ('White', '#FFF5B7');
