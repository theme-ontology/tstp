#!/bin/bash

URLGIT_TSTP_MASTER="https://github.com/theme-ontology/tstp/archive/refs/heads/master.tar.gz"
URLGIT_THEMES_MASTER="https://github.com/theme-ontology/theming/archive/refs/heads/master.tar.gz"

mkdir -p /code/tmp
mkdir -p /code/tstp
mkdir -p /code/theming

curl -L $URLGIT_TSTP_MASTER > /code/tmp/tstp.tar.gz
curl -L $URLGIT_THEMES_MASTER > /code/tmp/theming.tar.gz

tar -zxf /code/tmp/tstp.tar.gz tstp-master --strip-components 1 -C /code/tstp
tar -zxf /code/tmp/theming.tar.gz theming-master --strip-components 1 -C /code/theming

tree -L 1 /code/tstp

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
echo "adjusting database schemas..."
/code/tstp/totolo/run python3 manage.py makemigrations
/code/tstp/totolo/run python3 manage.py migrate
nohup /code/tstp/totolo/run python3 manage.py indexgit >> /var/log/indexgit.log &
echo "starting web server..."
/code/tstp/totolo/run python3 manage.py runserver 0.0.0.0:80
echo "...web server died!"
