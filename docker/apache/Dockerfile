FROM httpd:2.4.33-alpine AS base
RUN apk update; \
    apk upgrade;

FROM base AS src_local
COPY apache/demo.apache.conf /usr/local/apache2/conf/demo.apache.conf
COPY ./apache/start.sh /docker/start.sh

FROM src_local AS cfg
RUN echo "Include /usr/local/apache2/conf/demo.apache.conf" \
    >> /usr/local/apache2/conf/httpd.conf
CMD /docker/start.sh

