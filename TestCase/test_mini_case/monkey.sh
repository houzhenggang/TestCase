#!/bin/sh

# blacklist file
blacklist=/data/local/tmp/blacklist.txt

# monkey log file
monkey=/data/local/tmp/monkey.txt

if [ $# -eq 1 ] && [ -n $1 ] ;then
    monkey -p $1 -s 10 --ignore-timeouts --ignore-crashes -v 50000 > $monkey 2>&1
else
    rm -f $blacklist
    for line in `pm list package -3`
    do
        echo ${line:8} >> $blacklist
    done
    monkey -s 10 --pkg-blacklist-file $blacklist --ignore-timeouts --ignore-crashes -v 500000 > $monkey 2>&1
fi
