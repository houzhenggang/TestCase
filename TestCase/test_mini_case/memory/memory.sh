#!/bin/sh

workdir=/data/local/tmp/memory
workout=${workdir}/out

while read line
do
    package=${line}
    packout=${workout}/${package}
    if [ ! -d ${packout} ] ;then
        mkdir -p ${packout}
        sh ${workdir}/meminfo.sh ${package} &
        mid=$!
        if [ ${package} == 'com.android.systemui' ] ;then
            cp -f ${workdir}/SystemUiTest.jar /data/local/tmp
            uiautomator runtest SystemUiTest.jar -c cn.nubia.systemui.test.StatusBar -e Cycle 50
            uiautomator runtest SystemUiTest.jar -c cn.nubia.systemui.test.MultiTaskTest -e Cycle 50
            rm -f /data/local/tmp/SystemUiTest.jar
        else
            sh ${workdir}/monitor.sh &
            nid=$!
            monkey -p ${package} -s 13 --throttle 200 --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 200000 > ${packout}/monkey.txt 2>&1
            kill ${nid}
        fi
        kill ${mid}
    fi
done < ${workdir}/mempkgs.txt
