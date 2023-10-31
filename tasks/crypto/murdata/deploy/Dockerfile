FROM php:8.1-apache

RUN apt-get update && \
    apt install -y redis-server wget
RUN pecl install redis \
&& docker-php-ext-enable redis

RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -O /wait-for-it.sh \
  && chmod +x /wait-for-it.sh
COPY entry.sh /entry.sh
COPY src/ /var/www/html/

WORKDIR /var/www/html

CMD ["/entry.sh"]
