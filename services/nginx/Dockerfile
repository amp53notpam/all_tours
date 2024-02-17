FROM nginx:1.18-alpine

RUN rm /etc/nginx/conf.d/default.conf && mkdir -p /var/log/nginx/flaskr
COPY nginx.conf /etc/nginx
COPY flaskr.conf /etc/nginx/conf.d
