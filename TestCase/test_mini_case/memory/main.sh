#!/bin/sh

workdir=/data/local/tmp/memory
workout=${workdir}/out
mkdir -p ${workout}

if [ $1 == 'reset' ] ;then
    ${workdir}/busybox nohup sh ${workdir}/reset.sh
elif [ $1 == 'monkey' ] ;then
    ${workdir}/busybox nohup sh ${workdir}/monkey.sh
elif [ $1 == 'normal' ] ;then
    ${workdir}/busybox nohup sh ${workdir}/normal.sh
elif [ $1 == 'resident' ] ;then
    ${workdir}/busybox nohup sh ${workdir}/resident.sh
elif [ $1 == 'memory' ] ;then
    ${workdir}/busybox nohup sh ${workdir}/memory.sh
fi
