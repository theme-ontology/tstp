from db import do
import log
import webobject


TABLES = {
    'web_objects' : """
        CREATE TABLE IF NOT EXISTS `web_objects` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `category` VARCHAR(15) NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `unique_index` (`category`, `name`),
            KEY object_by_category (`category`)
        ) ENGINE = MYISAM;
    """,

    'web_attributes' : """
        CREATE TABLE IF NOT EXISTS `web_attributes` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `category` VARCHAR(15) NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            `attr` VARCHAR(20) NOT NULL,
            `value` TEXT NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `unique_index` (`category`, `name`, `attr`),
            KEY attribute_by_category_name (`category`, `name`(15))
        ) ENGINE = MYISAM;
    """,

    'web_connections' : """
        CREATE TABLE IF NOT EXISTS `web_connections` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `category` VARCHAR(15) NOT NULL,
            `category1` VARCHAR(15) NOT NULL,
            `name1` VARCHAR(255) NOT NULL,
            `category2` VARCHAR(15) NOT NULL,
            `name2` VARCHAR(255) NOT NULL,
            `attr` VARCHAR(15) NOT NULL,
            `value` TEXT NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `unique_index` (`category`, `category1`, `name1`(15), `category2`, `name2`(15), `attr`),
            INDEX `category_index` (`category`),
            KEY connection_by_category1_name1 (category1, name1(15)),
            KEY connection_by_category2_name2 (category2, name2(15))
        ) ENGINE = MYISAM;
    """,

    'web_events' : """
        CREATE TABLE IF NOT EXISTS `web_events` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `eventid` VARCHAR(15) NOT NULL,
            `userid` VARCHAR(15) NOT NULL,
            `entrytime` DATETIME NOT NULL,
            `eventstate` VARCHAR(15) NOT NULL,
            `action` VARCHAR(15) NOT NULL,
            `category` VARCHAR(15) NOT NULL,
            `refcategory` VARCHAR(15) NOT NULL,
            `category1` VARCHAR(15) NOT NULL,
            `name1` VARCHAR(255) NOT NULL,
            `category2` VARCHAR(15) NOT NULL,
            `name2` VARCHAR(255) NOT NULL,
            `field` VARCHAR(15) NOT NULL,
            `oldvalue` TEXT NOT NULL,
            `newvalue` TEXT NOT NULL,
            PRIMARY KEY (`id`),
            INDEX `category_index` (`category`),
            INDEX `user_index` (`userid`),
            KEY event_by_category1_name1 (category1, name1(15)),
            KEY event_by_category2_name2 (category2, name2(15))
        ) ENGINE = MYISAM;
    """,

    'web_counters' : """
        CREATE TABLE IF NOT EXISTS `web_counters` (
            `id` VARCHAR(15) NOT NULL,
            `value` INT,
            PRIMARY KEY (`id`)
        ) ENGINE = MYISAM;
    """,
}


def create_tables():
    for key, query in TABLES.iteritems():
        do(query)


if __name__ == '__main__':
    if False:
        create_tables()




