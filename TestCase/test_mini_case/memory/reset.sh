#!/bin/sh

workdir=/data/local/tmp/memory
workout=${workdir}/out

sleep 5
dumpsys meminfo > ${workout}/meminfo-1.txt

monkey -s 13 --throttle 100 --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 50000 > ${workout}/monkey.txt 2>&1
