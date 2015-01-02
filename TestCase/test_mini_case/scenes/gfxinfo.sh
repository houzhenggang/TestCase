#!/bin/sh

workdir=/data/local/tmp/scenes
infotmp=${workdir}/gfxinfo.tmp

while [ true ]
do
    sleep 1
    dumpsys gfxinfo ${1} > ${infotmp}
    cat ${infotmp} >> ${2}/gfxinfo.txt
    rm -f ${infotmp}
done
