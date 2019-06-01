TABLES = {}

TABLES['category'] = (
    "CREATE TABLE `category` ("
    "  `cat_id` int(5) UNSIGNED AUTO_INCREMENT,"
    "  `cname` varchar(100) NOT NULL,"
    "  FULLTEXT INDEX idx_cname (`cname`)"
    "  PRIMARY KEY (`cid`)"
    ") ENGINE=InnoDB"
)

TABLES["product"] = (
    "CREATE TABLE `product` ("
    "  `prod_id` int(6) UNSIGNED AUTO_INCREMENT,"
    "  `code` int(13) UNSIGNED,"
    "  `cat_id` int(5) UNSIGNED NOT NULL,"
    "  `pname` varchar(50) NOT NULL,"
    "  `brand` varchar(20),"
    "  `quantity` varchar(10),"
    "  `stores` varchar(50),"
    "  `url` varchar(100),"
    "  `score` char(1),"
    "  `energy` varchar(10),"
    "  PRIMARY KEY (`prod_id`),"
    "  CONSTRAINT `fk_cat_id` FOREIGN KEY (`cat_id`)"
    "    REFERENCES `category` (`cat_id`)"
    ") ENGINE=InnoDB"
)

TABLES["consumer"] = (
    'CREATE TABLE `consumer` ('
    '  `cons_id` int(6) UNSIGNED AUTO_INCREMENT,'
    '  `prod_id` int(6) UNSIGNED,'
    '  PRIMARY KEY (`cons_id`),'
    '  CONSTRAINT `fk_product` FOREIGN KEY (`prod_id`)'
    '    REFERENCES `product` (`prod_id`)'
    ') ENGINE=InnoDB'
)
