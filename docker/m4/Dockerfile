FROM php:rc-fpm-alpine AS base
ENV WAIT_VERSION 2.7.2
COPY deps_build.txt /build/deps_build.txt
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN apk update &&\
    apk upgrade  &&\
    xargs -a /build/deps_build.txt apk add --no-cache &&\
    chmod +x /wait

# Add python packages
FROM base AS base_python
COPY deps_python.txt /build/deps_python.txt
RUN curl https://bootstrap.pypa.io/get-pip.py -o /build/get-pip.py &&\
    python /build/get-pip.py  &&\
    pip install -r /build/deps_python.txt

# Cleanup build and add runtime packages
FROM base_python AS base_run
COPY deps_run.txt /build/deps_run.txt
RUN xargs -a /build/deps_run.txt apk add --no-cache &&\
    chmod +x /wait &&\
    apk del .build-deps

# Setup local copy of docker config files
FROM base_run AS src_local
COPY . /build/docker

# Final configuration
FROM src_local AS cfg
EXPOSE 31985
CMD /build/docker/m4/start.sh

