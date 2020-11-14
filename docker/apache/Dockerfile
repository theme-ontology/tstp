FROM httpd:2.4-alpine AS base

FROM base AS src_local
COPY apache/custom.apache.conf /usr/local/apache2/conf/custom.apache.conf
RUN echo "Include /usr/local/apache2/conf/custom.apache.conf" \
    >> /usr/local/apache2/conf/httpd.conf

