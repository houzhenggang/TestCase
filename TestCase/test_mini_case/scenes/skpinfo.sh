#!/bin/sh

workdir=/data/local/tmp/scenes
outfile=${1}/skpinfo.txt

touch ${outfile}

logcat -c
logcat -v time -s Choreographer:I I:s | while read line
do
    if [ -n "$(echo ${line} | grep -E 'Skipped [0-9]+ frames!')" ] ;then
        #screencap -p ${1}/$(date '+%y-%m-%d-%H-%M-%S')".png"
        echo ${line} >> ${outfile}
    fi
done
