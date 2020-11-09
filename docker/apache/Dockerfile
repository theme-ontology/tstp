FROM httpd:2.4.33-alpine AS base
RUN apk update; \
    apk upgrade;

FROM base AS src_local
COPY apache/demo.apache.conf /usr/local/apache2/conf/demo.apache.conf
COPY . /code/docker

FROM src_local AS cfg
RUN echo "Include /usr/local/apache2/conf/demo.apache.conf" \
    >> /usr/local/apache2/conf/httpd.conf
CMD /code/docker/apache/start.sh

