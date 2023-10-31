#!/bin/bash

echo "nameserver 1.1.1.1" > /etc/resolv.conf

echo "$FLAG" > /flag
unset FLAG

/usr/bin/supervisord -c /supervisord.conf
