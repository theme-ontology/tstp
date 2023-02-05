#!/bin/bash


mkdir -p /etc/ssl/certs/v2.themeontology.org

if [ -n "$SSL_PRIVKEY_V2" ]; then
    echo "$SSL_PRIVKEY_V2" >> /etc/ssl/certs/v2.themeontology.org/privkey1.pem
fi

