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
    export PATH_CODE="/local/tstp"
    cd /local/tstp/totolo/web
else
    export PATH_CODE="/code/tstp"
    cd /code/tstp/totolo/web
fi

## execute startup script from git repo
bash $PATH_CODE/totolo/docker/tan-ru/startup-ext.sh
##
