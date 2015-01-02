#!/bin/sh

workdir=/data/local/tmp/monkey
packout=${workdir}/out/${1}
infotmp=${workdir}/gfxinfo.tmp

while [ true ]
do
    sleep 5
    dumpsys gfxinfo ${1} > ${infotmp}
    cat ${infotmp} >> ${packout}/gfxinfo.txt
    rm -rf ${infotmp}
done
