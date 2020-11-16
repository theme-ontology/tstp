#!/bin/bash

export TSTPDOCKER=1
LOCALTSTP=/local/tstp

if [ -d "$LOCALTSTP" ]; then
    echo "configuring for: DEV"
    ln -sfn $LOCALTSTP /code/tstp
else
    echo "configuring for: PROD"
    rm -rf /code/tstp-latest
    rm -rf /code/tstp
    git clone --depth 1 https://github.com/theme-ontology/tstp /code/tstp-latest
    ln -sfn /code/tstp-latest /code/tstp
    cp /run/secrets/pycredentials /code/tstp/pylib/credentials.py
fi

# this will ensure theming repos are set up and updated
if [ ! -d "/code/theming" ]; then
    git clone --depth 1 https://github.com/theme-ontology/theming /code/theming
fi
if [ ! -d "/code/theming-hist" ]; then
    git clone https://github.com/theme-ontology/theming /code/theming-hist
fi
git -C /code/theming reset --hard origin/master
chown -R root:www-data /code/theming
chmod -R ug+rw /code/theming
git -C /code/theming-hist reset --hard origin/master
chown -R root:www-data /code/theming-hist
chmod -R ug+rw /code/theming-hist
git -C "/code/theming" pull --depth=1
git -C "/code/theming-hist" pull
cp -rf /code/theming /code/theming-m4

# directories that must exist
mkdir -p /www/pub/m4/logs
mkdir -p /www/pub/data
mkdir -p /www/pub/tstpviz
chown -R root:www-data /www/pub
chmod -R ug+rw /www/pub

