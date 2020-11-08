FROM php:rc-fpm-alpine AS base
RUN apk update; \
    apk upgrade;
RUN apk add findutils python2 python2-dev musl-dev
RUN docker-php-ext-install mysqli

FROM base AS base_python
COPY . /code/docker
RUN python /code/docker/get-pip.py
RUN pip install pymysql

FROM src_local AS src_local

RUN updatedb

FROM src_local AS cfg
RUN echo 'chdir = /code/tstp/webui' >> /usr/local/etc/php-fpm.d/www.conf
RUN echo 'chdir = /code' >> /usr/local/etc/php-fpm.d/www.conf
RUN echo 'bollocks /code' >> /code/index.php
RUN echo 'bollocks /var/www/html' >> /var/www/html/index.php


CMD /code/docker/php/start.sh

