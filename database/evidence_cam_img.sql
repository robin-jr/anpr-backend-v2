/*
-- Query: SELECT * FROM rlvd_db.evidence_cam_img
LIMIT 0, 1000

-- Date: 2021-08-23 22:58
*/
CREATE TABLE `evidence_cam_img` (
  `id` bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `evidence_image` varchar(100) NOT NULL,
  `vehicle_id` bigint(11) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage1.jpg',1);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage2.jpg',1);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage1.jpg',3);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage2.jpg',3);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage1.jpg',4);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage2.jpg',4);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage3.jpg',4);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage1.jpg',2);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage2.jpg',2);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage3.jpg',2);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage4.jpg',2);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage1.jpg',5);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage2.jpg',5);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage3.jpg',5);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage4.jpg',5);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage1.jpg',6);
INSERT INTO `evidence_cam_img` (`evidence_image`,`vehicle_id`) VALUES ('/home/user/images/results/EvidenceImage2.jpg',6);
