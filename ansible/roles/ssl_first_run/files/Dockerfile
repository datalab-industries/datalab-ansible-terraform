FROM nginx:1.31.10

WORKDIR /app

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/conf.d/default.conf


EXPOSE 80
EXPOSE 443
