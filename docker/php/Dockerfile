FROM php:rc-fpm-alpine AS base
RUN apk update; \
    apk upgrade;
RUN apk add bash findutils python2 python2-dev musl-dev git
RUN docker-php-ext-install mysqli

FROM base AS base_python
COPY . /code/docker
RUN python /code/docker/get-pip.py
RUN pip install pymysql natsort python-dateutil networkx

FROM base_python AS src_local
RUN git clone --depth 1 https://github.com/theme-ontology/theming /code/theming
RUN chown -R root:www-data /code/theming
RUN chmod -R ug+rw /code/theming
RUN cp -r /code/theming /code/theming-hist
RUN chown -R root:www-data /code/theming-hist
RUN chmod -R ug+rw /code/theming-hist
RUN updatedb

FROM src_local AS cfg
CMD /code/docker/php/start.sh

