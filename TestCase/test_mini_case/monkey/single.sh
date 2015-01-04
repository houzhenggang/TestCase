#!/bin/sh

workdir=/data/local/tmp/monkey
workout=${workdir}/out

while read line
do
    package=${line}
    packout=${workout}/${package}
    if [ ! -d ${packout} ] ;then
        mkdir -p ${packout}
        sh ${workdir}/meminfo.sh ${package} &
        mid=$!
        sh ${workdir}/gfxinfo.sh ${package} &
        gid=$!
        sh ${workdir}/skpinfo.sh ${package} &
        sid=$!
        sh ${workdir}/monitor.sh &
        nid=$!
        monkey -p ${package} -s $1 --throttle $2 --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v $3 > ${packout}/monkey.txt 2>&1
        kill ${mid}
        kill ${gid}
        kill ${sid}
        kill ${nid}
        am force-stop ${package}
    fi
done < ${workdir}/packages.txt
