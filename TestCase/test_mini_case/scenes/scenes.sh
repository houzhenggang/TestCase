#!/bin/sh

workdir=/data/local/tmp/scenes
workout=${workdir}/out

function execute()
{
    outpath=${workout}/$1
    if [ ! -d ${outpath} ] ;then
        mkdir -p ${outpath}
        sh ${workdir}/gfxinfo.sh $2 ${outpath} &
        gid=$!
        sh ${workdir}/skpinfo.sh ${outpath} &
        sid=$!
        cp -f ${workdir}/ScenesTest.jar /data/local/tmp
        uiautomator runtest ScenesTest.jar -c $3
        rm -f /data/local/tmp/ScenesTest.jar
        kill ${gid}
        kill ${sid}
        kill `${workdir}/busybox pidof logcat`
    fi
}

cp -f ${workdir}/ScenesTest.jar /data/local/tmp
pm install -r ${workdir}/ApiDemos.apk
model=`getprop ro.product.model`

if [ "${model}" == "L50w" ] ;then
    execute 'NativeListViewTest' 'com.example.android.apis' 'cn.sony.test.NativeListViewTest'
    execute 'ContactTest' 'com.sonyericsson.android.socialphonebook' 'cn.sony.test.ContactTest'
    execute 'DeveloperTest' 'com.android.settings' 'cn.sony.test.DeveloperTest'
    execute 'MultiTaskTest' 'com.android.systemui' 'cn.sony.test.MultiTaskTest'
    execute 'LauncherTest' 'com.sonyericsson.home' 'cn.sony.test.LauncherTest'
elif [ "${model}" == "SM-G9008V" ] ;then
    execute 'NativeListViewTest' 'com.example.android.apis' 'cn.sung.test.NativeListViewTest'
    execute 'ContactTest' 'com.android.contacts' 'cn.sung.test.ContactTest'
    execute 'DeveloperTest' 'com.android.settings' 'cn.sung.test.DeveloperTest'
    execute 'MultiTaskTest' 'com.android.systemui' 'cn.sung.test.MultiTaskTest'
    execute 'NoteScaleTest' 'com.android.mms' 'cn.sung.test.NoteScaleTest'
    execute 'LauncherTest' 'com.android.launcher' 'cn.sung.test.LauncherTest'
elif [ "${model}" == "Nexus 5" ] ;then
    execute 'NativeListViewTest' 'com.example.android.apis' 'cn.nexus.test.NativeListViewTest'
    execute 'ContactTest' 'com.google.android.contacts' 'cn.nexus.test.ContactTest'
    execute 'DeveloperTest' 'com.android.settings' 'cn.nexus.test.DeveloperTest'
    execute 'MultiTaskTest' 'com.android.systemui' 'cn.nexus.test.MultiTaskTest'
    execute 'NoteScaleTest' 'com.google.android.talk' 'cn.nexus.test.NoteScaleTest'
    execute 'LauncherTest' 'com.google.android.googlequicksearchbox' 'cn.nexus.test.LauncherTest'
    execute 'PressMenuTest' 'com.google.android.googlequicksearchbox' 'cn.nexus.test.PressMenuTest'
else
    execute 'NativeListViewTest' 'com.example.android.apis' 'cn.nubia.test.NativeListViewTest'
    execute 'ContactTest' 'com.android.contacts' 'cn.nubia.test.ContactTest'
    execute 'DeveloperTest' 'com.android.settings' 'cn.nubia.test.DeveloperTest'
    execute 'MultiTaskTest' 'com.android.systemui' 'cn.nubia.test.MultiTaskTest'
    execute 'NoteScaleTest' 'com.android.contacts' 'cn.nubia.test.NoteScaleTest'
    execute 'LauncherTest' 'cn.nubia.launcher' 'cn.nubia.test.LauncherTest'
    execute 'PressMenuTest' 'cn.nubia.launcher' 'cn.nubia.test.PressMenuTest'
fi

rm -f /data/local/tmp/ScenesTest.jar
pm uninstall com.example.android.apis

