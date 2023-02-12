#!/bin/bash

SSL_PRIVKEY_V2_LOC=/etc/ssl/certs/v2.themeontology.org/privkey1.pem
SSL_PRIVKEY_WWW_LOC=/etc/ssl/certs/www.themeontology.org/privkey1.pem

mkdir -p /etc/ssl/certs/v2.themeontology.org
mkdir -p /etc/ssl/certs/www.themeontology.org

if [ -n "$SSL_PRIVKEY_V2" ]; then
    echo "$SSL_PRIVKEY_V2" >> $SSL_PRIVKEY_V2_LOC
else
    cp -r /code/tstp/totolo/cert/localhost /etc/ssl/certs/
fi

if [ -n "$SSL_PRIVKEY_WWW" ]; then
    echo "$SSL_PRIVKEY_WWW" >> $SSL_PRIVKEY_WWW_LOC
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

echo "running indexgit in background..."
$PATH_CODE/totolo/run python3 manage.py indexgit &
echo "running index_s3 in background..."
$PATH_CODE/totolo/run python3 manage.py index_s3 &
echo "adjusting database schemas..."
$PATH_CODE/totolo/run python3 manage.py makemigrations
$PATH_CODE/totolo/run python3 manage.py migrate
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
