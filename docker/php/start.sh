#!/bin/sh

#cp /docker/php/php.ini-development /usr/local/etc/php/php.ini
#cp /docker/php/www.conf-development /usr/local/etc/php-fpm.d/www.conf
#chmod 664 /usr/local/etc/php/php.ini
#chmod 664 /usr/local/etc/php-fpm.d/www.conf
/wait
cd /code/tstp/webui
php-fpm -R
