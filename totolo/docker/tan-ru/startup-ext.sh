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
