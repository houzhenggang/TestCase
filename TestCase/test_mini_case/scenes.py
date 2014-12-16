# -*- coding:UTF-8 -*-

import codecs
import csv
import glob
import os
import re
import shutil
import subprocess
import sys
import threading

import adbkit as adb
import stress

class LogcatSkpinfoThread(threading.Thread):

    def __init__(self, outdir):
        threading.Thread.__init__(self)
        self.outdir = outdir

    def run(self):
        stat = {}
        os.system('adb -s {0} logcat -c'.format(adb.sno))
        output = open(os.path.join(self.outdir, 'skpinfo.txt'), 'w')
        self.p = subprocess.Popen('adb -s {0} logcat -v time -s Choreographer:I I:s'.format(adb.sno),
                shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = self.p.stdout.readline()
            if not line:
                break
            m = re.search('(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*Skipped (\d+) frames!', line)
            if m:
                file = os.path.join(self.outdir, '{0}.png'.format('-'.join(m.groups()[0].split(':'))))
                os.system('adb -s {0} shell screencap -p /data/local/tmp/screenshot.png'.format(adb.sno))
                os.popen('adb -s {0} pull /data/local/tmp/screenshot.png \"{1}\"'.format(adb.sno, file)).readline()
                c = int(m.groups()[1])
                stat.setdefault(c, 0)
                stat[c] += 1
                output.write(line)
                output.flush()
        output.close()

        report = open(os.path.join(self.outdir, 'skpinfo.csv'), 'wb')
        report.write(codecs.BOM_UTF8)
        writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        writer.writerow(['丢帧数量', '丢帧次数'])
        if len(stat) > 0:
            for key in sorted(stat.keys(), reverse=True):
                writer.writerow([key, stat[key]])
        report.close()

        if os.path.basename(self.outdir) == 'monkey':
            file = os.path.join(self.outdir, 'skpinfo.csv')
            os.remove(file)
        else:
            file = os.path.join(os.path.dirname(self.outdir), 'skpinfo.csv')

        if os.path.exists(file):
            report = open(file, 'ab+')
            writer = csv.writer(report, quoting=csv.QUOTE_ALL)
        else:
            report = open(file, 'wb')
            report.write(codecs.BOM_UTF8)
            writer = csv.writer(report, quoting=csv.QUOTE_ALL)
            writer.writerow(['项目', '丢帧数量', '丢帧次数'])
        writer.writerow([os.path.basename(self.outdir), sum([x * stat[x] for x in stat]), sum(stat.values())])
        report.close()

    def stop(self):
        self.p.terminate()

def scene(outdir, name, package, clsname):
    outdir = os.path.join(outdir, name)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    t1 = stress.DumpsysGfxinfoThread(outdir, package, 1)
    t2 = LogcatSkpinfoThread(outdir)
    t1.start()
    t2.start()
    subprocess.Popen('adb -s {0} shell uiautomator runtest scenes.jar -c {1}'.format(adb.sno, clsname),
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
    t1.stop()
    t2.stop()
    t1.join()
    t2.join()

def execute(workout):
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))

    # copy picture files
    os.popen('adb -s {0} shell mkdir -p /sdcard/Pictures'.format(adb.sno)).readline()
    picturesdir = open(os.path.join(workdir, 'config.txt'), 'r').readlines()[5].strip()
    os.popen('adb -s {0} push \"{1}\" /sdcard/Pictures'.format(adb.sno, unicode(picturesdir, 'utf-8').encode('GB2312'))).readlines()

    # copy pim files
    os.popen('adb -s {0} shell rm -rf /sdcard/nubia/PIM/*'.format(adb.sno)).readline()
    os.popen('adb -s {0} shell mkdir -p /sdcard/nubia/PIM'.format(adb.sno)).readline()
    pimdir = open(os.path.join(workdir, 'config.txt'), 'r').readlines()[3].strip()
    for filename in glob.glob(os.path.join(unicode(pimdir, 'utf-8'), '*')):
        realname = filename.encode('GB2312')
        if os.path.isdir(filename):
            os.popen('adb -s {0} shell mkdir /sdcard/nubia/PIM/{1}'.format(adb.sno, os.path.basename(filename))).readline()
            os.popen('adb -s {0} push \"{1}\" /sdcard/nubia/PIM/{2}'.format(adb.sno, realname, os.path.basename(filename))).readlines()
        elif os.path.isfile(filename):
            os.popen('adb -s {0} push \"{1}\" /sdcard/nubia/PIM'.format(adb.sno, realname)).readlines()

    # restore the backup
    os.popen('adb -s {0} shell am force-stop cn.nubia.databackup'.format(adb.sno)).readline()
    os.popen('adb -s {0} shell uiautomator runtest automator.jar -c cn.nubia.databackup.RestoreTestCase#testRestore'.format(adb.sno)).readlines()

    workout = os.path.join(workout, 'scenes')
    shutil.rmtree(workout, ignore_errors=True)
    if not os.path.exists(workout):
        os.mkdir(workout)

    # install ApiDemos
    os.popen('adb -s {0} push \"{1}\" /data/local/tmp/tmp.apk'.format(adb.sno, os.path.join(workdir, 'ApiDemos.apk'))).readlines()
    os.popen('adb -s {0} shell pm install -r /data/local/tmp/tmp.apk'.format(adb.sno)).readlines()

    # eanble dumpsys gfxinfo
    os.popen('adb -s {0} shell uiautomator runtest automator.jar -c com.android.settings.DevelopmentSettingsTestCase#testTrackFrameTimeDumpsysGfxinfo'.format(adb.sno)).readlines()

    # get scene info
    os.popen('adb -s {0} push \"{1}\" /data/local/tmp'.format(adb.sno, os.path.join(workdir, 'scenes.jar'))).readlines()
    model = os.popen('adb -s {0} shell getprop ro.product.model'.format(adb.sno)).readline().strip()
    if model == 'L50w':
        scene(workout, 'NativeListViewTest', 'com.example.android.apis', 'cn.sony.test.NativeListViewTest')
        scene(workout, 'ContactTest', 'com.sonyericsson.android.socialphonebook', 'cn.sony.test.ContactTest')
        scene(workout, 'DeveloperTest', 'com.android.settings', 'cn.sony.test.DeveloperTest')
        scene(workout, 'MultiTaskTest', 'com.android.systemui', 'cn.sony.test.MultiTaskTest')
        scene(workout, 'BrowserTest', 'com.android.browser', 'cn.sony.test.BrowserTest')
        scene(workout, 'LauncherTest', 'com.sonyericsson.home', 'cn.sony.test.LauncherTest')
    elif model == '':
        scene(workout, 'NativeListViewTest', 'com.example.android.apis', 'cn.sung.test.NativeListViewTest')
        scene(workout, 'ContactTest', 'com.android.contacts', 'cn.sung.test.ContactTest')
        scene(workout, 'DeveloperTest', '', 'cn.sung.test.DeveloperTest')
        scene(workout, 'MultiTaskTest', '', 'cn.sung.test.MultiTaskTest')
        scene(workout, 'BrowserTest', 'com.sec.android.app.sbrowser', 'cn.sung.test.BrowserTest')
        scene(workout, 'NoteScaleTest', 'com.android.mms', 'cn.sung.test.NoteScaleTest')
        scene(workout, 'LauncherTest', '', 'cn.sung.test.LauncherTest')
    else:
        scene(workout, 'NativeListViewTest', 'com.example.android.apis', 'cn.nubia.test.NativeListViewTest')
        scene(workout, 'ContactTest', 'com.android.contacts', 'cn.nubia.test.ContactTest')
        scene(workout, 'DeveloperTest', 'com.android.settings', 'cn.nubia.test.DeveloperTest')
        scene(workout, 'GalleryTest', 'com.android.gallery3d', 'cn.nubia.test.GalleryTest')
        scene(workout, 'MultiTaskTest', 'com.android.systemui', 'cn.nubia.test.MultiTaskTest')
        scene(workout, 'BrowserTest', 'com.android.browser', 'cn.nubia.test.BrowserTest')
        scene(workout, 'NoteScaleTest', 'com.android.contacts', 'cn.nubia.test.NoteScaleTest')
        scene(workout, 'LauncherTest', 'cn.nubia.launcher', 'cn.nubia.test.LauncherTest')
        scene(workout, 'PressMenuTest', 'cn.nubia.launcher', 'cn.nubia.test.PressMenuTest')
