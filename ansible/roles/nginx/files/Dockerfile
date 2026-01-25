FROM nginx:1.29.4

WORKDIR /app

COPY nginx.conf /etc/nginx/nginx.conf
COPY ./rendered/nginx_ssl.conf /etc/nginx/nginx_ssl.conf
COPY ./rendered/include /etc/nginx/include
RUN rm -f /etc/nginx/conf.d/default.conf


EXPOSE 80
EXPOSE 443
