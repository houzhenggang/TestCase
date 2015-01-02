#!/bin/sh

workdir=/data/local/tmp/scenes
outfile=${2}/gfxinfo.txt
tmpfile=${workdir}/gfxinfo.tmp

touch ${outfile}

while [ true ]
do
    sleep 1
    dumpsys gfxinfo ${1} > ${tmpfile}
    cat ${tmpfile} >> ${outfile}
done
