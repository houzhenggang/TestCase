#!/bin/sh

if [ $# -eq 1 ] && [ -n $1 ] ;then
    monkey -p $1 -s 10 --throttle 100 --ignore-timeouts --ignore-crashes -v 50000 > /data/local/tmp/monkey.txt 2>&1
else
    monkey -s 10 --throttle 100 --ignore-timeouts --ignore-crashes -v 500000 > /data/local/tmp/monkey.txt 2>&1
fi
