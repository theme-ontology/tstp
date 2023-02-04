# syntax=docker/dockerfile:1.4

## follow M-4 base
###################################################################################################

FROM python:3.7-alpine AS builder
COPY ./m4/deps_run.txt /build/
COPY ./m4/deps_python.txt /build/
RUN xargs -a /build/deps_run.txt apk add --no-cache
RUN pip3 install --upgrade pip
RUN pip3 install -r /build/deps_python.txt --no-cache-dir


## install postgresql 
###################################################################################################

RUN apk add postgresql
RUN groupadd -r postgres --gid=999; \
    useradd -r -g postgres --uid=999 --home-dir=/var/lib/postgresql --shell=/bin/bash postgres; \
    mkdir -p /var/lib/postgresql; \
    chown -R postgres:postgres /var/lib/postgresql
ENV LANG en_US.utf8
ENV PG_MAJOR 15
ENV PATH $PATH:/usr/lib/postgresql/$PG_MAJOR/bin
ENV PG_VERSION 15.1-1.pgdg110+1
RUN mkdir /docker-entrypoint-initdb.d
RUN mkdir -p /var/run/postgresql && chown -R postgres:postgres /var/run/postgresql && chmod 2777 /var/run/postgresql
ENV PGDATA /var/lib/postgresql/data
RUN mkdir -p "$PGDATA" && chown -R postgres:postgres "$PGDATA" && chmod 777 "$PGDATA"
VOLUME /var/lib/postgresql/data

## install Sphinx, cf. https://github.com/macbre/docker-sphinxsearch/blob/master/Dockerfile
ENV SPHINX_VERSION 3.4.1-efbcc65
RUN apk add --no-cache mariadb-connector-c-dev postgresql-dev wget
RUN mkdir -pv /opt/sphinx/log /opt/sphinx/index
VOLUME /opt/sphinx/index
RUN wget http://sphinxsearch.com/files/sphinx-${SPHINX_VERSION}-linux-amd64-musl.tar.gz -O /tmp/sphinxsearch.tar.gz \
    && cd /opt/sphinx && tar -xf /tmp/sphinxsearch.tar.gz && rm /tmp/sphinxsearch.tar.gz
ENV PATH "${PATH}:/opt/sphinx/sphinx-3.4.1/bin"
RUN indexer -v
RUN ln -sv /dev/stdout /opt/sphinx/log/query.log && ln -sv /dev/stdout /opt/sphinx/log/searchd.log
EXPOSE 36307
VOLUME /opt/sphinx/conf
ARG SPHINX_CONFIG_FILE=/opt/sphinx/conf/sphinx.conf
ENV SPHINX_CONFIG_FILE ${SPHINX_CONFIG_FILE}
RUN echo "exec searchd --nodetach --config \${SPHINX_CONFIG_FILE}" > /opt/sphinx/start.sh
COPY ./sphinx/sphinx.conf /opt/sphinx/conf/
COPY ./sphinx /sphinx
RUN mkdir -pv /var/data /var/log


## install nginx, lifted from official package
###################################################################################################

ENV NGINX_VERSION 1.23.3
ENV PKG_RELEASE   1
RUN set -x \
# create nginx user/group first, to be consistent throughout docker variants
    && addgroup -g 101 -S nginx \
    && adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx \
    && apkArch="$(cat /etc/apk/arch)" \
    && nginxPackages=" \
        nginx=${NGINX_VERSION}-r${PKG_RELEASE} \
    " \
# install prerequisites for public key and pkg-oss checks
    && apk add --no-cache --virtual .checksum-deps \
        openssl \
    && case "$apkArch" in \
        x86_64|aarch64) \
# arches officially built by upstream
            set -x \
            && KEY_SHA512="e09fa32f0a0eab2b879ccbbc4d0e4fb9751486eedda75e35fac65802cc9faa266425edf83e261137a2f4d16281ce2c1a5f4502930fe75154723da014214f0655" \
            && wget -O /tmp/nginx_signing.rsa.pub https://nginx.org/keys/nginx_signing.rsa.pub \
            && if echo "$KEY_SHA512 */tmp/nginx_signing.rsa.pub" | sha512sum -c -; then \
                echo "key verification succeeded!"; \
                mv /tmp/nginx_signing.rsa.pub /etc/apk/keys/; \
            else \
                echo "key verification failed!"; \
                exit 1; \
            fi \
            && apk add -X "https://nginx.org/packages/mainline/alpine/v$(egrep -o '^[0-9]+\.[0-9]+' /etc/alpine-release)/main" --no-cache $nginxPackages \
            ;; \
        *) \
# we're on an architecture upstream doesn't officially build for
# let's build binaries from the published packaging sources
            set -x \
            && tempDir="$(mktemp -d)" \
            && chown nobody:nobody $tempDir \
            && apk add --no-cache --virtual .build-deps \
                gcc \
                libc-dev \
                make \
                openssl-dev \
                pcre2-dev \
                zlib-dev \
                linux-headers \
                bash \
                alpine-sdk \
                findutils \
            && su nobody -s /bin/sh -c " \
                export HOME=${tempDir} \
                && cd ${tempDir} \
                && curl -f -O https://hg.nginx.org/pkg-oss/archive/${NGINX_VERSION}-${PKG_RELEASE}.tar.gz \
                && PKGOSSCHECKSUM=\"52a80f6c3b3914462f8a0b2fbadea950bcd79c1bd528386aff4c28d5a80c6920d783575a061a47b60fea800eef66bf5a0178a137ea51c37277fe9c2779715990 *${NGINX_VERSION}-${PKG_RELEASE}.tar.gz\" \
                && if [ \"\$(openssl sha512 -r ${NGINX_VERSION}-${PKG_RELEASE}.tar.gz)\" = \"\$PKGOSSCHECKSUM\" ]; then \
                    echo \"pkg-oss tarball checksum verification succeeded!\"; \
                else \
                    echo \"pkg-oss tarball checksum verification failed!\"; \
                    exit 1; \
                fi \
                && tar xzvf ${NGINX_VERSION}-${PKG_RELEASE}.tar.gz \
                && cd pkg-oss-${NGINX_VERSION}-${PKG_RELEASE} \
                && cd alpine \
                && make base \
                && apk index -o ${tempDir}/packages/alpine/${apkArch}/APKINDEX.tar.gz ${tempDir}/packages/alpine/${apkArch}/*.apk \
                && abuild-sign -k ${tempDir}/.abuild/abuild-key.rsa ${tempDir}/packages/alpine/${apkArch}/APKINDEX.tar.gz \
                " \
            && cp ${tempDir}/.abuild/abuild-key.rsa.pub /etc/apk/keys/ \
            && apk del .build-deps \
            && apk add -X ${tempDir}/packages/alpine/ --no-cache $nginxPackages \
            ;; \
    esac \
# remove checksum deps
    && apk del .checksum-deps \
# if we have leftovers from building, let's purge them (including extra, unnecessary build deps)
    && if [ -n "$tempDir" ]; then rm -rf "$tempDir"; fi \
    && if [ -n "/etc/apk/keys/abuild-key.rsa.pub" ]; then rm -f /etc/apk/keys/abuild-key.rsa.pub; fi \
    && if [ -n "/etc/apk/keys/nginx_signing.rsa.pub" ]; then rm -f /etc/apk/keys/nginx_signing.rsa.pub; fi \
# Bring in gettext so we can get `envsubst`, then throw
# the rest away. To do this, we need to install `gettext`
# then move `envsubst` out of the way so `gettext` can
# be deleted completely, then move `envsubst` back.
    && apk add --no-cache --virtual .gettext gettext \
    && mv /usr/bin/envsubst /tmp/ \
    \
    && runDeps="$( \
        scanelf --needed --nobanner /tmp/envsubst \
            | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
            | sort -u \
            | xargs -r apk info --installed \
            | sort -u \
    )" \
    && apk add --no-cache $runDeps \
    && apk del .gettext \
    && mv /tmp/envsubst /usr/local/bin/ \
# Bring in tzdata so users could set the timezones through the environment
# variables
    && apk add --no-cache tzdata \
# forward request and error logs to docker log collector
    && ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
# create a docker-entrypoint.d directory
    && mkdir /docker-entrypoint.d

RUN rm -f /etc/nginx/conf.d/default.conf
COPY ./tan-ru/nginx.conf /etc/nginx/conf.d/nginx.conf


## again follow M-4 base
###################################################################################################

COPY ./m4/crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab
RUN touch /var/log/cron.log

# make debugging a little easier
RUN echo 'alias ldbg="/local/tstp/totolo/run bash"' >> ~/.bashrc
RUN echo 'alias pm="cd /local/tstp/totolo/web && python manage.py "' >> ~/.bashrc
RUN echo '. /local/tstp/totolo/run echo "apply env"' >> ~/.bashrc

# sphinx, sql, django
EXPOSE 9306
EXPOSE 5432
EXPOSE 8000

COPY ./tan-ru /tan-ru
WORKDIR /tan-ru
CMD ["/bin/bash", "startup.sh"]
