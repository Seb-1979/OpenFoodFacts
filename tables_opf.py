TABLES = {}

TABLES['category'] = (
    "CREATE TABLE IF NOT EXISTS `category` ("
    "  `cat_id` int(5) UNSIGNED AUTO_INCREMENT,"
    "  `cname` text NOT NULL,"
    "  FULLTEXT INDEX idx_cname (`cname`),"
    "  PRIMARY KEY (`cat_id`)"
    ") ENGINE=InnoDB"
)

TABLES["product"] = (
    "CREATE TABLE IF NOT EXISTS `product` ("
    "  `prod_id` int(6) UNSIGNED AUTO_INCREMENT,"
    "  `code` bigint(13),"
    "  `cat_id` int(5) UNSIGNED NOT NULL,"
    "  `pname` varchar(150) NOT NULL,"
    "  `brand` varchar(100),"
    "  `quantity` varchar(100),"
    "  `stores` varchar(100),"
    "  `url` varchar(170),"
    "  `score` char(1),"
    "  `energy` varchar(10),"
    "  PRIMARY KEY (`prod_id`),"
    "  CONSTRAINT `fk_cat_id` FOREIGN KEY (`cat_id`)"
    "    REFERENCES `category` (`cat_id`)"
    ") ENGINE=InnoDB"
)

TABLES["consumer"] = (
    'CREATE TABLE IF NOT EXISTS `consumer` ('
    '  `cons_id` int(6) UNSIGNED AUTO_INCREMENT,'
    '  `prod_id` int(6) UNSIGNED,'
    '  PRIMARY KEY (`cons_id`),'
    '  CONSTRAINT `fk_product` FOREIGN KEY (`prod_id`)'
    '    REFERENCES `product` (`prod_id`)'
    ') ENGINE=InnoDB'
)
