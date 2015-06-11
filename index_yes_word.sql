-- phpMyAdmin SQL Dump
-- version 4.4.9
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jun 11, 2015 at 11:41 AM
-- Server version: 10.0.19-MariaDB-log
-- PHP Version: 5.6.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `have_i_jacked_it`
--

-- --------------------------------------------------------

--
-- Table structure for table `index_yes_word`
--

CREATE TABLE IF NOT EXISTS `index_yes_word` (
  `id` int(11) NOT NULL,
  `word` varchar(32) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `index_yes_word`
--

INSERT INTO `index_yes_word` (`id`, `word`) VALUES
(1, 'affirmative'),
(6, 'true'),
(7, 'yea'),
(8, 'all right'),
(9, 'aye'),
(10, 'beyond a doubt'),
(11, 'by all means'),
(12, 'certainly'),
(13, 'definitely'),
(16, 'gladly'),
(19, 'indubitably'),
(21, 'most assuredly'),
(23, 'of course'),
(24, 'positively'),
(26, 'sure thing'),
(27, 'surely'),
(28, 'undoubtedly'),
(29, 'unquestionably'),
(31, 'willingly'),
(32, 'without fail'),
(33, 'yep'),
(34, 'tru'),
(36, 'assuredly'),
(38, 'without fail'),
(39, 'yeah');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `index_yes_word`
--
ALTER TABLE `index_yes_word`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `index_yes_word`
--
ALTER TABLE `index_yes_word`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=41;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
