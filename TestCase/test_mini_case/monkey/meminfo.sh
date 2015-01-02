#!/bin/sh

workdir=/data/local/tmp/monkey
outfile=${workdir}/out/${1}/meminfo.txt
tmpfile=${workdir}/meminfo.tmp

touch ${outfile}

while [ true ]
do
    sleep 20
    dumpsys meminfo ${1} > ${tmpfile}
    cat ${tmpfile} >> ${outfile}
done
