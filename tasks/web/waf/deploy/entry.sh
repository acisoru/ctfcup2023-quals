#!/bin/sh

echo "$FLAG" > /flag.txt
unset FLAG


php-fpm7 -R

nginx -g "daemon off;"