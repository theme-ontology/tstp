# syntax=docker/dockerfile:1.4

FROM --platform=$BUILDPLATFORM python:3.7-alpine AS builder
COPY ./m4/deps_run.txt /build/
COPY ./m4/deps_python.txt /build/
RUN xargs -a /build/deps_run.txt apk add --no-cache
RUN pip3 install --upgrade pip
RUN pip3 install -r /build/deps_python.txt --no-cache-dir

# setup cron jobs
COPY ./m4/crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab
RUN touch /var/log/cron.log

# make debugging a little easier
RUN echo 'alias ldbg="/local/tstp/totolo/run bash"' >> ~/.bashrc
RUN echo 'alias pm="cd /local/tstp/totolo/web && python manage.py "' >> ~/.bashrc
RUN echo '. /local/tstp/totolo/run echo "apply env"' >> ~/.bashrc

EXPOSE 8000
COPY ./m4 /m4
WORKDIR /m4
CMD ["/bin/bash", "startup.sh"]
