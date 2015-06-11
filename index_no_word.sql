-- phpMyAdmin SQL Dump
-- version 4.4.9
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jun 11, 2015 at 11:43 AM
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
-- Table structure for table `index_no_word`
--

CREATE TABLE IF NOT EXISTS `index_no_word` (
  `id` int(11) NOT NULL,
  `word` varchar(32) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `index_no_word`
--

INSERT INTO `index_no_word` (`id`, `word`) VALUES
(1, 'on no account'),
(2, 'not at all'),
(3, 'certainly not'),
(4, 'definitely not'),
(5, 'by no means'),
(6, 'no way'),
(7, 'nope'),
(9, 'negative'),
(10, 'nix'),
(11, 'absolutely not'),
(12, 'never'),
(13, 'not by any means'),
(14, 'not at all'),
(15, 'nagative'),
(16, 'nay'),
(17, 'never'),
(19, 'void'),
(20, 'no'),
(21, 'What the fuck did you just fucki'),
(22, 'not yet'),
(23, 'not yet');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `index_no_word`
--
ALTER TABLE `index_no_word`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `index_no_word`
--
ALTER TABLE `index_no_word`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=24;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
