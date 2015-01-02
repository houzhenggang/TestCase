#!/bin/sh

workdir=/data/local/tmp/monkey

while [ true ]
do
    sleep 600
    if [ "$(echo `uiautomator dump 2>&1`)" == "ERROR: null root node returned by UiTestAutomationBridge." ] ;then
        pid=$(${workdir}/busybox pidof com.android.commands.monkey)
        if [ -n "${pid}" ] ;then
            kill ${pid}
        fi
    fi
done
