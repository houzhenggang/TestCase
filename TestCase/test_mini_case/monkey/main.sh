#!/bin/sh

workdir=/data/local/tmp/monkey
record=${workdir}/record.txt
workout=${workdir}/out
mkdir -p ${workout}

if [ $# -eq 4 ] ;then
    echo $* > ${record}
    if [ $4 == '1' ] ;then
        sh ${workdir}/single.sh $1 $2 $3
    else
        sh ${workdir}/monkey.sh $1 $2 $3
    fi
elif [ $# -eq 0 ] && [ -f ${record} ] ;then
    params=`cat ${record}`
    params=(${params// / })
    if [ ${params[3]} == '1' ] ;then
        sh ${workdir}/single.sh ${params[0]} ${params[1]} ${params[2]}
    else
        sh ${workdir}/monkey.sh ${params[0]} ${params[1]} ${params[2]}
    fi
fi
