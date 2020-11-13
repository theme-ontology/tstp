#!/bin/sh

#cp /docker/php/php.ini-development /usr/local/etc/php/php.ini
#cp /docker/php/www.conf-development /usr/local/etc/php-fpm.d/www.conf
#chmod 664 /usr/local/etc/php/php.ini
#chmod 664 /usr/local/etc/php-fpm.d/www.conf
/wait
socat TCP-LISTEN:31985,fork TCP:m4:31985 &
cd /code/tstp/webui
php-fpm -R
