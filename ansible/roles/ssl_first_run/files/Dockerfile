FROM nginx:1.31.0

WORKDIR /app

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/conf.d/default.conf


EXPOSE 80
EXPOSE 443
