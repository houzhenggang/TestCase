#!/bin/sh

workdir=/data/local/tmp/monkey
outfile=${workdir}/out/${1}/gfxinfo.txt
tmpfile=${workdir}/gfxinfo.tmp

touch ${outfile}

while [ true ]
do
    sleep 5
    dumpsys gfxinfo ${1} > ${tmpfile}
    cat ${tmpfile} >> ${outfile}
done
