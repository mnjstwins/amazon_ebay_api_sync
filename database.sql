-- phpMyAdmin SQL Dump
-- version 3.5.8.2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: May 09, 2014 at 04:56 PM
-- Server version: 5.1.73
-- PHP Version: 5.3.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `sync`
--

-- --------------------------------------------------------

--
-- Table structure for table `sync`
--

CREATE TABLE IF NOT EXISTS `sync` (
  `ItemID` varchar(100) NOT NULL,
  `Type` varchar(25) NOT NULL,
  `Images` varchar(16000) NOT NULL,
  `LastUpdate` double NOT NULL,
  `SubCategory` varchar(16000) DEFAULT NULL,
  `Category` varchar(255) NOT NULL,
  `Price` double NOT NULL,
  `CurrencyID` varchar(25) NOT NULL,
  `Description` varchar(1023) NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Seller` varchar(255) NOT NULL,
  `URL` varchar(1024) NOT NULL,
  PRIMARY KEY (`ItemID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `sync_config`
--

CREATE TABLE IF NOT EXISTS `sync_config` (
  `Sync_Type` varchar(255) NOT NULL,
  `Sync_Key` varchar(255) NOT NULL,
  `Sync_Value` varchar(255) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `sync_config`
--

INSERT INTO `sync_config` (`Sync_Type`, `Sync_Key`, `Sync_Value`) VALUES
('Amazon', 'JSON_KEY', '{"keyID":"REDACTED", "secret":"REDACTED", "associate_id":"REDACTED"}'),
('EBAY', 'JSON_KEY', '{"key":"REDACTED"}');

-- --------------------------------------------------------

--
-- Table structure for table `sync_searches`
--

CREATE TABLE IF NOT EXISTS `sync_searches` (
  `search_number` int(11) NOT NULL AUTO_INCREMENT,
  `search_poller` varchar(255) NOT NULL,
  `search_text` varchar(255) NOT NULL,
  PRIMARY KEY (`search_number`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `sync_searches`
--

INSERT INTO `sync_searches` (`search_number`, `search_poller`, `search_text`) VALUES
(1, 'amazon', 'Kindle 3g'),
(2, 'ebay', 'Poweredge 1955');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
