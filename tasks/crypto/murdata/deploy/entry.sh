#!/bin/bash


redis-server &

/wait-for-it.sh -t 60 localhost:6379 -- echo "Redis is up"


mkdir /userdata && chown -R www-data:www-data /userdata
php /var/www/html/register_admin.php && apache2-foreground &

unset FLAG
export DATA_DIR="/userdata/"
export ADMIN_PASSWORD=Oo591a3a9d409e6c52575dPwd

wait -n

exit $?