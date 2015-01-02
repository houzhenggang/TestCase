#!/bin/sh

workdir=/data/local/tmp/monkey
packout=${workdir}/out/${1}
infotmp=${workdir}/meminfo.tmp

while [ true ]
do
    sleep 20
    dumpsys meminfo ${1} > ${infotmp}
    cat ${infotmp} >> ${packout}/meminfo.txt
    rm -rf ${infotmp}
done
