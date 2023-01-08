# syntax=docker/dockerfile:1.4

FROM --platform=$BUILDPLATFORM python:3.7-alpine AS builder
COPY ./m4/app/deps_run.txt /build/
COPY ./m4/app/deps_python.txt /build/
RUN xargs -a /build/deps_run.txt apk add --no-cache
RUN pip3 install -r /build/deps_python.txt --no-cache-dir

EXPOSE 8000
COPY ./m4/app /app
WORKDIR /app 
CMD ["/bin/bash", "startup.sh"]
