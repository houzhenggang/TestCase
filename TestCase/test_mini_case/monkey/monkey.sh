#!/bin/sh

workdir=/data/local/tmp/monkey
workout=${workdir}/out

blacklist=${workdir}/blacklist.txt
rm -f ${blacklist}

for line in `pm list package -3`
do
    echo ${line:8} >> ${blacklist}
done

if [ ! -f ${workout}/monkey.txt ] ;then
    sh ${workdir}/meminfo.sh ${package} &
    mid=$!
    monkey -s $1 --throttle $2 --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes --pkg-blacklist-file ${blacklist} -v $3 > ${workout}/monkey.txt 2>&1
    kill ${mid}
fi
