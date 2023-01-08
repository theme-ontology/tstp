# syntax=docker/dockerfile:1.4

FROM --platform=$BUILDPLATFORM python:3.7-alpine AS builder
COPY ../deps_run.txt /build/
COPY ../deps_python.txt /build/
RUN xargs -a /build/deps_run.txt apk add --no-cache
RUN pip3 install -r deps_python.txt --no-cache-dir

EXPOSE 8000
WORKDIR /app 
COPY . /app
CMD ["/bin/bash", "startup.sh"]
