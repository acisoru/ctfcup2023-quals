#!/usr/bin/env bash

echo $FLAG > /flag.txt
unset FLAG

socat "TCP-LISTEN:13000,reuseaddr,fork" "EXEC:/task"
