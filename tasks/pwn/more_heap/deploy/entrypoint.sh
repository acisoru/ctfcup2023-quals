#!/usr/bin/env bash

echo $FLAG > /flag.txt
unset FLAG

socat "TCP-LISTEN:13001,reuseaddr,fork" "EXEC:/more_heap"