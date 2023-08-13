#!/bin/bash

if [[ "$DEBUG" -ne 1 ]]; then
    url="themeontology.org"
    email="mikael@odinlake.net"
    mkdir -p /opt/letsencrypt
    certbot certonly -d $url -d "*.$url" --dns-route53 --logs-dir /opt/letsencrypt/logs/ --config-dir /opt/letsencrypt/config/ --work-dir /home/mo/letsencrypt/work/ -m $email --agree-tos --non-interactive
fi

echo ":: STARTING UP AT PATH ::::::::::::::::::::::::::::::::::"
pwd
echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::"

echo "starting cron daemon..."
nohup /usr/sbin/crond -f -l 8 &

echo "starting postgreSQL DB service... "
nohup su - postgres -c "pg_ctl start -D /var/lib/postgresql/data" &

echo "starting sphinx search service..."
nohup sh /opt/sphinx/start.sh &

echo "starting nginx web server..."
nohup nginx -g 'daemon off;' &

for ii in {1..10}
do
    if pg_isready -h localhost -p 5432 -U $POSTGRES_USER
    then
        echo "postgres is ready on localhost:5432."
        break
    fi
    echo "Waiting for postgres..."
    sleep 2
done

echo "adjusting database schemas..."
$PATH_CODE/totolo/run python3 manage.py makemigrations
$PATH_CODE/totolo/run python3 manage.py migrate
echo "running indexgit in background..."
$PATH_CODE/totolo/run python3 manage.py indexgit &
echo "running index_s3 in background..."
$PATH_CODE/totolo/run python3 manage.py index_s3 &
echo "starting web server..."
if [ -n "$IS_PROD" ]; then
    $PATH_CODE/totolo/run python3 manage.py collectstatic -c --noinput
    ls -l /www/pub/staticfiles
    chmod -R u=rwx,go=rx /www/pub
    ls -l /www/pub/staticfiles/ontologyexplorer/img
    $PATH_CODE/totolo/run gunicorn website.wsgi:application --bind 0.0.0.0:8000
else
    $PATH_CODE/totolo/run python3 manage.py runserver 0.0.0.0:8000
fi

echo "...web server died!"
