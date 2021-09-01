/*
-- Query: SELECT * FROM rlvd_db.evidence_cam_img
LIMIT 0, 1000

-- Date: 2021-08-23 22:58
*/
CREATE TABLE `evidence_cam_img` (
  `id` bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `evidence_image` varchar(100) NOT NULL,
  `object_id` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev11.png',1);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev12.png',1);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev13.png',1);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev14.png',1);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev15.png',1);

INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev21.png',2);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev22.png',2);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev23.png',2);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev24.png',2);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev25.png',2);

INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev31.png',3);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev32.png',3);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev33.png',3);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev34.png',3);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev35.png',3);

INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev41.png',4);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev42.png',4);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev43.png',4);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev44.png',4);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev45.png',4);

INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev51.png',5);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev52.png',5);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev53.png',5);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev54.png',5);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev55.png',5);

INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev61.png',6);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev62.png',6);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev63.png',6);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev64.png',6);
INSERT INTO `evidence_cam_img` (`evidence_image`,`object_id`) VALUES ('images/results/ev65.png',6);
