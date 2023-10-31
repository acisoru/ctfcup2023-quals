#!/bin/sh

echo "$FLAG" > /flag.txt
unset FLAG

exec "/monitoring"
