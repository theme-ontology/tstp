#!/bin/sh

while ! nc -z m4 31985; do echo "waiting on m4:31985..."; sleep 3; done
socat TCP-LISTEN:31985,fork TCP:m4:31985 &
cd /code/tstp/webui
php-fpm -R
