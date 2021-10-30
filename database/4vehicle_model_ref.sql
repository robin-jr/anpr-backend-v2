CREATE TABLE `vehicle_model_ref` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `type_id` int NOT NULL,
  `make_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `model_type_foreign_key_idx` (`type_id`),
  KEY `model_made_foreign_key_idx` (`make_id`),
  CONSTRAINT `model_made_foreign_key` FOREIGN KEY (`make_id`) REFERENCES `vehicle_make_ref` (`id`),
  CONSTRAINT `model_type_foreign_key` FOREIGN KEY (`type_id`) REFERENCES `vehicle_type_ref` (`id`)
) ENGINE=InnoDB;



INSERT INTO `vehicle_model_ref` (`name`, `type_id`, `make_id`) VALUES ('Dio', '1', '1');
INSERT INTO `vehicle_model_ref` (`name`, `type_id`, `make_id`) VALUES ('V2', '1', '2');
INSERT INTO `vehicle_model_ref` (`name`, `type_id`, `make_id`) VALUES ('Civic', '2', '3');
INSERT INTO `vehicle_model_ref` (`name`, `type_id`, `make_id`) VALUES ('XL lorry', '3', '4');
