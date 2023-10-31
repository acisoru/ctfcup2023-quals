#!/usr/bin/env bash

echo $FLAG > /flag.txt
unset FLAG

socat "TCP-LISTEN:13002,reuseaddr,fork" "EXEC:/some_storage"