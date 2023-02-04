#!/bin/bash

URLGIT_TSTP_MASTER="https://github.com/theme-ontology/tstp/archive/refs/heads/master.tar.gz"
URLGIT_THEMES_MASTER="https://github.com/theme-ontology/theming/archive/refs/heads/master.tar.gz"

mkdir -p /code/tmp
mkdir -p /code/tstp
mkdir -p /code/theming
mkdir -p /www/pub/staticfiles

curl -L $URLGIT_TSTP_MASTER > /code/tmp/tstp.tar.gz
curl -L $URLGIT_THEMES_MASTER > /code/tmp/theming.tar.gz

tar -zxf /code/tmp/tstp.tar.gz tstp-master --strip-components 1 -C /code/tstp
tar -zxf /code/tmp/theming.tar.gz theming-master --strip-components 1 -C /code/theming

bash -c "/tan-ru/postgres-docker-entrypoint.sh"
if [ -n "$IS_PROD" ]; then :; else
    cp /tan-ru/nginx.dev.conf /etc/nginx/conf.d/nginx.conf
fi

if [ -d "/local/tstp" ]; then
    PATH_CODE="/local/tstp"
    cd /local/tstp/totolo/web
else
    PATH_CODE="/code/tstp"
    cd /code/tstp/totolo/web
fi

echo ":: STARTING UP AT PATH ::::::::::::::::::::::::::::::::::"
pwd
echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo ":: TOTOLO ENV :::::::::::::::::::::::::::::::::::::::::::"
/code/tstp/totolo/run env
echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::"

echo "starting cron daemon..."
nohup /usr/sbin/crond -f -l 8 &

echo "starting postgreSQL DB service... "
nohup su - postgres -c "pg_ctl start -D /var/lib/postgresql/data" &

echo "starting sphinx search service..."
nohup sh /opt/sphinx/start.sh &

echo "starting nginx web server..."
nohup nginx -g 'daemon off;' &

echo "adjusting database schemas..."
/code/tstp/totolo/run python3 manage.py makemigrations
/code/tstp/totolo/run python3 manage.py migrate
nohup /code/tstp/totolo/run python3 manage.py indexgit >> /var/log/indexgit.log &

echo "starting web server..."
if [ -n "$IS_PROD" ]; then
    /code/tstp/totolo/run python3 manage.py collectstatic -c --noinput
    ls -l /www/pub/staticfiles
    chmod -R u=rwx,go=rx /www/pub
    ls -l /www/pub/staticfiles/ontologyexplorer/img
    /code/tstp/totolo/run gunicorn website.wsgi:application --bind 0.0.0.0:8000
else
    /code/tstp/totolo/run python3 manage.py runserver 0.0.0.0:8000
fi

echo "...web server died!"
