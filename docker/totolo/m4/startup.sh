#!/bin/bash

URLGIT_TSTP_MASTER="https://github.com/theme-ontology/tstp/archive/refs/heads/master.tar.gz"
URLGIT_THEMES_MASTER="https://github.com/theme-ontology/theming/archive/refs/heads/master.tar.gz"
PATH_LOCALAPP="/local/tstp/totolo/app"
PATH_GITAPP="/code/tstp/totolo/app"

mkdir /code/tmp
mkdir /code/tstp
mkdir /code/theming

curl -L $URLGIT_TSTP_MASTER > /code/tmp/tstp.tar.gz
curl -L $URLGIT_THEMES_MASTER > /code/tmp/theming.tar.gz

tar -zxf /code/tmp/tstp.tar.gz tstp-master --strip-components 1 -C /code/tstp
tar -zxf /code/tmp/theming.tar.gz theming-master --strip-components 1 -C /code/theming

tree -L 2 /local/tstp

if [ -d "$PATH_LOCALAPP" ]; then
    cd $PATH_LOCALAPP
else
    cd $PATH_GITAPP
fi
echo ":: STARTING UP AT PATH ::::::::::::::::::::::::::::::::::"
pwd
echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::"

/code/tstp/scripts/runpy python3 manage.py runserver 0.0.0.0:8000

