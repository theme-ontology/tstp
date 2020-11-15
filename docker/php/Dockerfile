FROM php:rc-fpm-alpine AS base
RUN apk add socat --no-cache

# Setup local copy of docker config files
FROM base AS src_local
COPY . /build/docker
COPY php/php.ini-development /usr/local/etc/php/php.ini
COPY php/www.conf-development /usr/local/etc/php-fpm.d/www.conf

# Final configuration
FROM src_local AS cfg
CMD /build/docker/php/start.sh

