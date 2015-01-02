#!/bin/sh

workdir=/data/local/tmp/memory
packout=${workdir}/out/${1}
infotmp=${workdir}/meminfo.tmp

while [ true ]
do
    sleep 2
    dumpsys meminfo ${1} > ${infotmp}
    cat ${infotmp} >> ${packout}/meminfo.txt
    rm -rf ${infotmp}
done
