FROM nginx:1.23.3-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/staticfiles
RUN chown root:nginx $APP_HOME/staticfiles
WORKDIR $APP_HOME
