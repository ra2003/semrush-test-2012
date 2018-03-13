--
-- Table structure for table `ads`
--

CREATE TABLE IF NOT EXISTS `ads` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(250) NOT NULL,
  `desc` text NOT NULL,
  `href` varchar(250) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`,`href`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=9669158 ;

-- --------------------------------------------------------

--
-- Table structure for table `ads_search`
--

CREATE TABLE IF NOT EXISTS `ads_search` (
  `id` bigint(20) unsigned NOT NULL,
  `title` varchar(250) NOT NULL,
  `desc` text NOT NULL,
  `href` varchar(250) NOT NULL,
  PRIMARY KEY (`id`),
  FULLTEXT KEY `title` (`title`,`desc`,`href`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `adsense_links`
--

CREATE TABLE IF NOT EXISTS `adsense_links` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `domain_id` int(11) unsigned NOT NULL,
  `link` text NOT NULL,
  `date_load` datetime DEFAULT NULL,
  `last_cookie` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `domain_id` (`domain_id`),
  KEY `date_load` (`date_load`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=13004 ;

-- --------------------------------------------------------

--
-- Table structure for table `domains`
--

CREATE TABLE IF NOT EXISTS `domains` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1001 ;

-- --------------------------------------------------------

--
-- Table structure for table `loader_counters`
--

CREATE TABLE IF NOT EXISTS `loader_counters` (
  `date_add` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `count_urls` int(10) unsigned NOT NULL,
  `seconds` decimal(10,4) unsigned NOT NULL,
  `connections` int(10) unsigned NOT NULL,
  `success` int(10) unsigned NOT NULL,
  `fail` int(10) unsigned NOT NULL,
  `not_parsed` int(10) unsigned NOT NULL,
  `empty_response` int(10) unsigned NOT NULL,
  PRIMARY KEY (`date_add`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `adsense_links`
--
ALTER TABLE `adsense_links`
  ADD CONSTRAINT `adsense_links_ibfk_1` FOREIGN KEY (`domain_id`) REFERENCES `domains` (`id`);
