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
        logcat -c
        logcat -v time -s Choreographer:I I:s > ${outpath}/skpinfo.txt &
        sid=$!
        cp -f ${workdir}/ScenesTest.jar /data/local/tmp
        uiautomator runtest ScenesTest.jar -c $3
        rm -f /data/local/tmp/ScenesTest.jar
        kill ${gid}
        kill ${sid}
    fi
}

cp -f ${workdir}/ScenesTest.jar /data/local/tmp
pm install -r ${workdir}/ApiDemos.apk
model=`getprop ro.product.model`

if [ ${model} == 'L50w' ] ;then
    execute 'NativeListViewTest' 'com.example.android.apis' 'cn.sony.test.NativeListViewTest'
    execute 'ContactTest' 'com.sonyericsson.android.socialphonebook' 'cn.sony.test.ContactTest'
    execute 'DeveloperTest' 'com.android.settings' 'cn.sony.test.DeveloperTest'
    execute 'MultiTaskTest' 'com.android.systemui' 'cn.sony.test.MultiTaskTest'
    execute 'BrowserTest' 'com.android.browser' 'cn.sony.test.BrowserTest'
    execute 'LauncherTest' 'com.sonyericsson.home' 'cn.sony.test.LauncherTest'
elif [ ${model} == 'SM-G9008V' ] ;then
    execute 'NativeListViewTest' 'com.example.android.apis' 'cn.sung.test.NativeListViewTest'
    execute 'ContactTest' 'com.android.contacts' 'cn.sung.test.ContactTest'
    execute 'DeveloperTest' 'com.android.settings' 'cn.sung.test.DeveloperTest'
    execute 'MultiTaskTest' 'com.android.systemui' 'cn.sung.test.MultiTaskTest'
    execute 'BrowserTest' 'com.sec.android.app.sbrowser' 'cn.sung.test.BrowserTest'
    execute 'NoteScaleTest' 'com.android.mms' 'cn.sung.test.NoteScaleTest'
    execute 'LauncherTest' 'com.android.launcher' 'cn.sung.test.LauncherTest'
else
    execute 'NativeListViewTest' 'com.example.android.apis' 'cn.nubia.test.NativeListViewTest'
    execute 'ContactTest' 'com.android.contacts' 'cn.nubia.test.ContactTest'
    execute 'DeveloperTest' 'com.android.settings' 'cn.nubia.test.DeveloperTest'
    execute 'GalleryTest' 'com.android.gallery3d' 'cn.nubia.test.GalleryTest'
    execute 'MultiTaskTest' 'com.android.systemui' 'cn.nubia.test.MultiTaskTest'
    execute 'BrowserTest' 'com.android.browser' 'cn.nubia.test.BrowserTest'
    execute 'NoteScaleTest' 'com.android.contacts' 'cn.nubia.test.NoteScaleTest'
    execute 'LauncherTest' 'cn.nubia.launcher' 'cn.nubia.test.LauncherTest'
    execute 'PressMenuTest' 'cn.nubia.launcher' 'cn.nubia.test.PressMenuTest'
fi

rm -f /data/local/tmp/ScenesTest.jar
pm uninstall com.example.android.apis

