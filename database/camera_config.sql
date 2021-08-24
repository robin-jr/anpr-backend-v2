-- phpMyAdmin SQL Dump
-- version 4.6.6deb5ubuntu0.5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 05, 2021 at 08:12 PM
-- Server version: 5.7.35-0ubuntu0.18.04.1
-- PHP Version: 7.2.24-0ubuntu0.18.04.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `phpmyadmin`
--

-- --------------------------------------------------------

--
-- Table structure for table `camera_config`
--

CREATE TABLE `camera_config` (
  `id` int(11) NOT NULL,
  `camera_number` varchar(100) NOT NULL,
  `latitude` decimal(10,7) NOT NULL,
  `longitude` decimal(10,7) NOT NULL,
  `url` varchar(100) NOT NULL,
  `plate_model` varchar(100) NOT NULL,
  `char_model` varchar(100) NOT NULL,
  `char_model_width` int(11) NOT NULL,
  `char_model_height` int(11) NOT NULL,
  `vid_width` int(11) NOT NULL,
  `vid_height` int(11) NOT NULL,
  `char_det_model` varchar(100) NOT NULL,
  `char_recog_model` varchar(100) NOT NULL,
  `char_split` tinyint(1) NOT NULL,
  `plate_threshold` decimal(10,1) NOT NULL,
  `character_threshold` decimal(10,1) NOT NULL,
  `plate_interval` int(11) NOT NULL,
  `roi_y_min` int(11) NOT NULL,
  `roi_x_min` int(11) NOT NULL,
  `roi_y_max` int(11) NOT NULL,
  `roi_x_max` int(11) NOT NULL,
  `nireq` int(11) NOT NULL,
  `object_tracking` varchar(100) NOT NULL,
  `post_processing_method` int(11) NOT NULL,
  `cluster_end` int(11) NOT NULL,
  `cluster_end_vehicle` int(11) NOT NULL,
  `no_of_active_vehicles` int(11) NOT NULL,
  `extras` int(11) NOT NULL,
  `full_image_save_quality` int(11) NOT NULL,
  `cropped_image_save_quality` int(11) NOT NULL,
  `video_display` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `camera_config`
--

INSERT INTO `camera_config` (`id`, `camera_number`, `latitude`, `longitude`, `url`, `plate_model`, `char_model`, `char_model_width`, `char_model_height`, `vid_width`, `vid_height`, `char_det_model`, `char_recog_model`, `char_split`, `plate_threshold`, `character_threshold`, `plate_interval`, `roi_y_min`, `roi_x_min`, `roi_y_max`, `roi_x_max`, `nireq`, `object_tracking`, `post_processing_method`, `cluster_end`, `cluster_end_vehicle`, `no_of_active_vehicles`, `extras`, `full_image_save_quality`, `cropped_image_save_quality`, `video_display`) VALUES
(8, 'ALCO_DEMO', '13.1037360', '80.2006020', 'rtsp://192.168.1.170:554/live.sdp', 'T31-FP16', 'Default', 304, 192, 1280, 720, 'CD2-FP32', 'CR1', 1, '0.4', '0.2', 1, 0, 0, 720, 1280, 1, 'short-term', 14, 190, 7, 3, -3, 99, 99, 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `camera_config`
--
ALTER TABLE `camera_config`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `camera_config`
--
ALTER TABLE `camera_config`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
