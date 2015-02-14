#!/bin/sh

workdir=/data/local/tmp/memory
workout=${workdir}/out

while read line
do
    package=${line}
    if [ ${package} == 'com.android.systemui' ] ;then
        cp -f ${workdir}/SystemUiTest.jar /data/local/tmp
        uiautomator runtest SystemUiTest.jar -c cn.nubia.systemui.test.StatusBar -e Cycle 10
        uiautomator runtest SystemUiTest.jar -c cn.nubia.systemui.test.MultiTaskTest -e Cycle 10
        rm -f /data/local/tmp/SystemUiTest.jar
    else
        sh ${workdir}/monitor.sh &
        nid=$!
        monkey -p ${package} -s 13 --throttle 200 --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 5000
        kill ${nid}
    fi
done < ${workdir}/packages.txt

uiautomator runtest automator.jar -c com.android.systemui.SleepWakeupTestCase\#testWakeup
am startservice -a com.ztemt.test.action.TEST_KIT --es command disableKeyguard
uiautomator runtest automator.jar -c com.android.systemui.MultiTaskTestCase\#testRecycle

dumpsys meminfo > ${workout}/meminfo-3.txt
