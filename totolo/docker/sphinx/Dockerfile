FROM macbre/sphinxsearch:3.4.1 AS totolo-sphinx

COPY ./sphinx/sphinx.conf /opt/sphinx/conf/
COPY ./sphinx /sphinx
RUN mkdir -p /opt/sphinx/conf
RUN mkdir -p /opt/sphinx/index
RUN mkdir -p /var/data
RUN mkdir -p /var/log

CMD ["/bin/sh", "/sphinx/bootstrap.sh"]
