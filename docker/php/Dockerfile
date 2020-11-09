FROM php:rc-fpm-alpine AS base
RUN apk update; \
    apk upgrade;
RUN apk add bash findutils python2 git gcc
RUN apk add libffi-dev openssl-dev python2-dev musl-dev
RUN docker-php-ext-install mysqli

# Add docker-compose-wait tool -------------------
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

FROM base AS base_python
RUN mkdir /code
RUN curl https://bootstrap.pypa.io/get-pip.py -o /code/get-pip.py
RUN python /code/get-pip.py
RUN pip install pymysql natsort python-dateutil networkx cryptography pytz numpy

FROM base_python AS src_local
RUN git clone --depth 1 https://github.com/theme-ontology/theming /code/theming
RUN chown -R root:www-data /code/theming
RUN chmod -R ug+rw /code/theming
RUN cp -r /code/theming /code/theming-hist
RUN chown -R root:www-data /code/theming-hist
RUN chmod -R ug+rw /code/theming-hist

FROM src_local AS src_local_docker
COPY . /code/docker
RUN updatedb

FROM src_local_docker AS cfg
CMD /code/docker/php/start.sh

