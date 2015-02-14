#!/bin/sh

workdir=/data/local/tmp/memory
workout=${workdir}/out
mkdir -p ${workout}

blacklist=${workdir}/blacklist.txt
rm -rf ${blacklist}

for line in `pm list package -3`
do
    echo ${line:8} >> ${blacklist}
done

monkey -s 13 --throttle 200 --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes --pkg-blacklist-file ${blacklist} -v 30000 > ${workout}/monkey.txt 2>&1
