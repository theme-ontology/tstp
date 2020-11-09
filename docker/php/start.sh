#!/bin/sh

/code/docker/tstpconfig.sh

# only the php process should do this
/wait
/code/tstp/scripts/run python /code/tstp/pylib/dbdefine.py

cp /code/docker/php/php.ini-development /usr/local/etc/php/php.ini
cp /code/docker/php/www.conf-development /usr/local/etc/php-fpm.d/www.conf
chmod 664 /usr/local/etc/php/php.ini
chmod 664 /usr/local/etc/php-fpm.d/www.conf
cd /code/tstp/webui

php-fpm -R
