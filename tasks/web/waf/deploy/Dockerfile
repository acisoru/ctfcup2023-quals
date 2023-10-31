FROM openresty/openresty:1.21.4.2-1-alpine-apk

RUN apk add --no-cache php7 php7-fpm php7-sqlite3 php7-json php7-session


COPY conf/app.conf /etc/nginx/conf.d/default.conf

WORKDIR /var/www/html

COPY src/ /var/www/html/
COPY sql.db /sql.db

RUN sed -i 's/nobody/root/g' /etc/php7/php-fpm.d/www.conf

COPY entry.sh /entry.sh

CMD ["/entry.sh"]
