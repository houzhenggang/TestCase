#!/bin/sh

# blacklist file
blacklist=/data/local/tmp/blacklist.txt

# monkey log file
monkey=/data/local/tmp/monkey.txt

if [ $# -eq 4 ] ;then
    monkey -p $4 -s $1 --throttle $2 --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v $3 > $monkey 2>&1
else
    rm -f $blacklist
    for line in `pm list package -3`
    do
        echo ${line:8} >> $blacklist
    done
    monkey -s $1 --throttle $2 --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v $3 --pkg-blacklist-file $blacklist > $monkey 2>&1
fi
